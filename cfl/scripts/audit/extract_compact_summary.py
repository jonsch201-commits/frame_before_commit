#!/usr/bin/env python3
"""extract_compact_summary.py — RP-3: pull compact summaries out of a CC session
JSONL as quotable-never-as-ruling artifacts, and (with --diff) grade every
quoted span in a summary against the record window it claims to describe.

WHY: a compact summary is the harness's own paraphrase of Jon's turns, written
into the JSONL as a `type: user` record with `isCompactSummary: true` (see
wiki/references/source-schemas.md, "Compact-summary wrapper"). It is NOT a
transcript and it is NOT a ruling. The known defect this closes (2026-09-01):
four of Jon's mid-turn messages appeared 4/4 as paraphrase in a compact summary
and 0/4 in the corresponding record window — the verbatim lines existed only
as `attachment.type: queued_command` entries the compact never saw. A summary
read as if it were Jon's own words is the hedge-flattening failure class named
in CLAUDE.md. This script never asserts a summary's claims are true; it only
measures whether each quoted span is FOUND-VERBATIM, FOUND-NEAR (paraphrased),
FOUND-IN-QUEUED-ONLY (the RP-27 class), or NOT-IN-WINDOW.

Every artifact this script writes carries the frontmatter line:
    status: "MACHINE PARAPHRASE, never a ruling; grade against the window"
That line is not decoration — it is the fact the artifact exists to assert.

CLI:
    python extract_compact_summary.py --jsonl <path> [<path> ...] [--all]
        [--out-dir DIR] [--diff] [--receipts-dir DIR]

    --jsonl PATH...   one or more session JSONL files (Windows paths OK)
    --all             extract every compact summary in each file (default:
                       only the newest one per file)
    --out-dir DIR     where to write artifacts (default:
                       exchange/su-close/compact-summaries)
    --diff            also run the quote-vs-window diff for each summary and
                       append a "## DIFF" section to its artifact
    --receipts-dir DIR  PreCompact receipts directory (default:
                       exchange/su-close/precompact) — used only by --diff to
                       locate the (lo, hi] window bounding a summary

Exit 0 on a clean run (summaries found and written; diff, if requested, ran
without an internal error — a NOT-IN-WINDOW or SUSPICIOUS verdict is a
reported FINDING, not a script failure). Exit 1 on an internal error (bad
path, unparseable JSONL, no compact summary found at all when one was
expected). UNKNOWN is written into the artifact/report, never silently
rounded to a verdict.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import mint_window  # noqa: E402  (local module, scripts/audit/mint_window.py)

DEFAULT_OUT_DIR = os.path.join(ROOT, "exchange", "su-close", "compact-summaries")
DEFAULT_RECEIPTS_DIR = os.path.join(ROOT, "exchange", "su-close", "precompact")
FL_WINDOWS_DIR = os.path.join(ROOT, "raw", "transcripts", "claude-code", "fl")

SUMMARY_PREFIX = "This session is being continued from a previous conversation"
RECEIPT_HDR = re.compile(r"# PreCompact receipt — (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)([+-]\d{4})")
RECEIPT_NAME = re.compile(r"^(\d{8}T\d{6})-([0-9a-f]{6,8})\.md$")
FM_WINDOW_UTC = re.compile(r'window_utc:\s*"?\(([^→\s]+)\s*→\s*([^)\s]+)\]"?')
FM_SESSION = re.compile(r"^session:\s*(\S+)", re.M)

MIN_QUOTE_LEN = 8
MAX_QUOTE_LEN = 500
NEAR_MATCH_RATIO = 0.60


# --------------------------------------------------------------------------
# 1. Locate compact-summary records in a session JSONL
# --------------------------------------------------------------------------

def iter_jsonl(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield i, json.loads(line)
            except json.JSONDecodeError:
                continue


def summary_text_of(entry):
    """Return the summary text if this entry is a compact-summary record,
    else None. Checks the three documented shapes (isCompactSummary flag,
    type: summary, and the fallback text-prefix match) per the ticket brief
    and wiki/references/source-schemas.md."""
    if entry.get("type") == "summary":
        # documented fallback shape; not observed in this repo's corpus as of
        # 2026-09-02 but checked per the ticket's instruction
        txt = entry.get("summary") or entry.get("text") or ""
        if txt:
            return txt
    if entry.get("type") != "user":
        return None
    msg = entry.get("message") or {}
    content = msg.get("content")
    if isinstance(content, list):
        content = mint_window.text_of(content)
    if not isinstance(content, str):
        return None
    is_flagged = entry.get("isCompactSummary") is True
    is_prefixed = content.startswith(SUMMARY_PREFIX)
    if is_flagged or is_prefixed:
        return content
    return None


def find_compact_summaries(jsonl_path, all_summaries=False):
    """Returns a list of dicts: {line, ts, text, flagged, prefixed} in file
    order. If all_summaries is False, only the LAST one is returned (the
    newest compact of the session)."""
    found = []
    for lineno, entry in iter_jsonl(jsonl_path):
        txt = summary_text_of(entry)
        if txt is None:
            continue
        found.append({
            "line": lineno,
            "ts": entry.get("timestamp") or "",
            "text": txt,
            "flagged_isCompactSummary": entry.get("isCompactSummary") is True,
            "type_summary": entry.get("type") == "summary",
            "prefix_matched": txt.startswith(SUMMARY_PREFIX),
        })
    if not found:
        return []
    return found if all_summaries else [found[-1]]


# --------------------------------------------------------------------------
# 2. Quote extraction from summary text
# --------------------------------------------------------------------------

QUOTE_PATTERNS = [
    re.compile(r'"([^"\n]{%d,%d})"' % (MIN_QUOTE_LEN, MAX_QUOTE_LEN)),
    re.compile(r'\u201c([^\u201d\n]{%d,%d})\u201d' % (MIN_QUOTE_LEN, MAX_QUOTE_LEN)),
    re.compile(r"(?:Jon said|verbatim)[:,]?\s+[\"\u201c]?([^\"\u201d\n]{%d,%d})[\"\u201d]?" %
                (MIN_QUOTE_LEN, MAX_QUOTE_LEN), re.IGNORECASE),
]


def extract_quotes(summary_text):
    """Every quoted span in the summary: text inside quotation marks, or
    following 'Jon said'/'verbatim'. Deduplicated, order-preserving."""
    seen = set()
    out = []
    for pat in QUOTE_PATTERNS:
        for m in pat.finditer(summary_text):
            q = m.group(1).strip()
            if not q or q in seen:
                continue
            seen.add(q)
            out.append(q)
    return out


# --------------------------------------------------------------------------
# 3. Window location — committed .md file first, in-memory mint fallback
# --------------------------------------------------------------------------

def find_committed_window(session_id, ts):
    """Search raw/transcripts/claude-code/fl/*.md for a committed
    record-pipeline-window/v1 file whose window_utc contains ts, or the
    nearest earlier one. Returns (path, lo, hi, body) or None."""
    if not os.path.isdir(FL_WINDOWS_DIR):
        return None
    candidates = []
    for name in os.listdir(FL_WINDOWS_DIR):
        if not name.endswith(".md"):
            continue
        path = os.path.join(FL_WINDOWS_DIR, name)
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                head = f.read(2000)
        except OSError:
            continue
        if "record-pipeline-window/v1" not in head:
            continue
        sm = FM_SESSION.search(head)
        if sm and sm.group(1)[:8] != session_id[:8]:
            # session ids in windows may be truncated/full; accept only a
            # matching (or fuller-prefix) session id, never an unrelated one
            continue
        wm = FM_WINDOW_UTC.search(head)
        if not wm:
            continue
        lo, hi = wm.group(1), wm.group(2)
        candidates.append((path, lo, hi))
    contains, earlier = [], []
    for path, lo, hi in candidates:
        if lo < ts <= hi:
            contains.append((path, lo, hi))
        elif hi <= ts:
            earlier.append((path, lo, hi))
    pick = None
    if contains:
        pick = sorted(contains, key=lambda t: t[2])[-1]
    elif earlier:
        pick = sorted(earlier, key=lambda t: t[2])[-1]
    if not pick:
        return None
    path, lo, hi = pick
    with open(path, encoding="utf-8", errors="replace") as f:
        body = f.read()
    counts = {}
    for key in ("user_text_turns", "assistant_text_blocks", "tool_calls",
                "queued_human", "queued_machine", "total_messages"):
        km = re.search(r"^%s:\s*(\d+)\s*$" % key, body, re.M)
        if km:
            counts[key] = int(km.group(1))
    return {"path": path, "lo": lo, "hi": hi, "body": body, "source": "committed", "counts": counts}


def _receipt_utc(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        head = f.read(200)
    m = RECEIPT_HDR.search(head)
    if not m:
        return None
    dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
    off = m.group(2)
    delta = timedelta(hours=int(off[1:3]), minutes=int(off[3:5]))
    return dt - delta if off[0] == "+" else dt + delta


def _session6(session_id):
    return session_id.replace("-", "")[:6]


def synthesize_window(jsonl_path, session_id, summary_ts, receipts_dir, summary_line=None):
    """No committed window covers this summary. Reproduce the same bound
    logic auto_mint_windows.py uses (nearest receipt at/after the summary
    timestamp establishes hi; the receipt before that establishes lo) and
    mint an IN-MEMORY window via mint_window.mint(). Never writes to disk —
    raw/transcripts/claude-code/fl/ is not in this ticket's write-set.

    summary_line, when given, is a hard safety cap enforced by POSITION, not
    by timestamp: the JSONL is truncated to lines strictly before
    summary_line before minting, so the summary's own record can never end
    up inside the window it is graded against — no matter what a receipt
    lookup computes, and no matter how hi_iso compares to the summary's own
    timestamp. A timestamp-only cap was tried first and measured to be
    UNSAFE: session e515d858 (no PreCompact receipt on record — true for a
    still-open live session) has records positioned BEFORE the summary's
    own line whose `timestamp` field is LATER than the summary's own
    timestamp (harness writes are not strictly chronological by line), so
    'last timestamp before this line' computed a bound that did not exclude
    the summary and the diff still came back 18/18 FOUND-VERBATIM
    (SUSPICIOUS-PERFECT-MATCH) — a false positive from the tool, not a real
    finding. Position-based truncation has no such failure mode: the
    summary's own line is never read in the first place."""
    sess6 = _session6(session_id)
    receipts = []
    if os.path.isdir(receipts_dir):
        for name in sorted(os.listdir(receipts_dir)):
            m = RECEIPT_NAME.match(name)
            if not m:
                continue
            if not (sess6.startswith(m.group(2)) or m.group(2).startswith(sess6)):
                continue
            path = os.path.join(receipts_dir, name)
            utc = _receipt_utc(path)
            if utc:
                receipts.append((utc, name))
    receipts.sort()
    summary_key = summary_ts[:19] if summary_ts else ""
    this_receipt = None
    for utc, name in receipts:
        if utc.strftime("%Y-%m-%dT%H:%M:%S") <= summary_key or not summary_key:
            this_receipt = (utc, name)
        else:
            break
    # NOTE: deliberately no fallback to receipts[0] here when no receipt
    # qualifies (utc <= summary_key) — a receipt fires BEFORE the compact
    # writes its summary, so a receipt with utc > summary_ts is not the one
    # that bounds this summary's content and must not be used as if it were
    # (that bug let the summary's own record leak into its own window).
    if this_receipt is None:
        # no receipts for this session at all — UNKNOWN bound; window is the
        # whole session up to the summary instant, clearly flagged as such
        lo_iso = "1970-01-01T00:00:00Z"
        hi_iso = (summary_key + "Z") if summary_key else None
        bound_note = "UNKNOWN (no PreCompact receipt found for this session)"
    else:
        idx = receipts.index(this_receipt)
        prev = receipts[idx - 1] if idx > 0 else None
        lo_iso = last_ts_at_or_before(jsonl_path, prev[0]) if prev else "1970-01-01T00:00:00Z"
        hi_iso = last_ts_at_or_before(jsonl_path, this_receipt[0])
        bound_note = "receipt %s" % this_receipt[1]
    if not hi_iso:
        hi_iso = (summary_key + "Z") if summary_key else "9999-12-31T23:59:59Z"
    mint_source = jsonl_path
    tmp_path = None
    if summary_line is not None:
        tmp_path = _truncate_before_line(jsonl_path, summary_line)
        mint_source = tmp_path
        bound_note += " (position-truncated before line %d, excl. the summary's own record)" % summary_line
        # hi_iso may still be later than the truncated file's own content;
        # that's fine -- mint() simply finds nothing past what's on disk.
        # It must never be EARLIER than lo_iso though (degenerate range).
        if hi_iso < lo_iso:
            hi_iso = lo_iso
    try:
        body, counts = mint_window.mint(mint_source, lo_iso, hi_iso)
    finally:
        if tmp_path:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    return {"path": None, "lo": lo_iso, "hi": hi_iso, "body": body, "counts": counts,
            "source": "synthesized-in-memory", "bound_note": bound_note}


def _truncate_before_line(jsonl_path, before_line):
    """Write a temp file containing only the lines strictly before
    before_line (1-indexed) and return its path. Caller must remove it."""
    import tempfile
    fd, tmp_path = tempfile.mkstemp(prefix="ecs_window_", suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
        with open(jsonl_path, encoding="utf-8", errors="ignore") as src:
            for i, line in enumerate(src, 1):
                if i >= before_line:
                    break
                out.write(line if line.endswith("\n") else line + "\n")
    return tmp_path


def last_ts_at_or_before(jsonl_path, cutoff_dt):
    cutoff_iso = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%S")
    last = None
    with open(jsonl_path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            i = line.find('"timestamp":"')
            if i == -1:
                continue
            ts = line[i + 13:i + 13 + 24].split('"')[0]
            if ts[:19] <= cutoff_iso:
                if last is None or ts > last:
                    last = ts
    return last


QUEUED_BLOCK_RE = re.compile(
    r"## (?:Human|Machine) \(queued,[^\n]*\n\n.*?(?=\n## |\Z)", re.S)


def core_window_body(full_body):
    """mint_window.py v1.1 (RP-27) already renders queued_command entries
    INLINE into a minted window's body, under '## Human (queued, ...)' /
    '## Machine (queued, ...)' headings — the RP-27 fix landed at the
    emitter, not here. Strip those rendered blocks back out before grading
    a quote against 'the window', so this script's FOUND-IN-QUEUED-ONLY
    verdict stays meaningful: it answers 'is this text in the ORDINARY
    user/assistant dialogue a window reader sees', separately from 'is this
    text recoverable at all, via the queued-command channel'. Also lets
    this diff still do useful work against a pre-v1.1 (legacy) committed
    window file, where queued content was never rendered in the first
    place — core_window_body is then a no-op."""
    return QUEUED_BLOCK_RE.sub("", full_body)


# --------------------------------------------------------------------------
# 4. Queued-command lookup (the RP-27 class)
# --------------------------------------------------------------------------

def find_queued_commands(jsonl_path):
    """Every attachment.type == queued_command prompt in the session, with
    timestamp. This is the ONLY place Jon's real mid-turn text can live when
    a compact summary paraphrases it away — see the standing constraint in
    CLAUDE.md ('Jon Messages Subagents Mid-Turn — Main Never Sees It') and
    the 2026-09-01 four-mid-turn-messages finding this ticket closes."""
    out = []
    for lineno, entry in iter_jsonl(jsonl_path):
        if entry.get("type") != "attachment":
            continue
        att = entry.get("attachment") or {}
        if att.get("type") != "queued_command":
            continue
        prompt = att.get("prompt") or ""
        if prompt:
            out.append({"line": lineno, "ts": entry.get("timestamp") or "", "prompt": prompt})
    return out


# --------------------------------------------------------------------------
# 5. Verdict logic
# --------------------------------------------------------------------------

def _norm(s):
    return " ".join(s.split()).lower()


def best_line_match(quote, body):
    """Best-matching line in body by difflib ratio. Returns (ratio, line, diff)."""
    nq = _norm(quote)
    best = (0.0, None)
    for line in body.splitlines():
        nl = _norm(line)
        if not nl:
            continue
        r = difflib.SequenceMatcher(None, nq, nl).ratio()
        if r > best[0]:
            best = (r, line)
    if best[1] is None:
        return 0.0, None, ""
    diff = "\n".join(difflib.unified_diff(
        [quote], [best[1]], lineterm="", n=0))
    return best[0], best[1], diff


def verdict_for_quote(quote, window_body, queued_prompts, check_queued=True):
    """Returns dict {verdict, detail}. Verdicts:
    FOUND-VERBATIM / FOUND-NEAR / FOUND-IN-QUEUED-ONLY / NOT-IN-WINDOW."""
    nq = _norm(quote)
    if nq and nq in _norm(window_body):
        return {"verdict": "FOUND-VERBATIM", "detail": ""}
    ratio, line, diff = best_line_match(quote, window_body)
    if ratio >= NEAR_MATCH_RATIO:
        return {"verdict": "FOUND-NEAR", "detail": "ratio=%.2f best-line=%r diff=%s" % (ratio, line, diff)}
    if check_queued:
        for qp in queued_prompts:
            if nq in _norm(qp["prompt"]) or _norm(qp["prompt"]) in nq:
                return {"verdict": "FOUND-IN-QUEUED-ONLY",
                        "detail": "queued_command line %s ts=%s" % (qp["line"], qp["ts"])}
            r2 = difflib.SequenceMatcher(None, nq, _norm(qp["prompt"])).ratio()
            if r2 >= NEAR_MATCH_RATIO:
                return {"verdict": "FOUND-IN-QUEUED-ONLY",
                        "detail": "near-match ratio=%.2f queued_command line %s ts=%s" % (r2, qp["line"], qp["ts"])}
    return {"verdict": "NOT-IN-WINDOW", "detail": "best window-line ratio=%.2f" % ratio}


# --------------------------------------------------------------------------
# 6. Diff driver for one summary
# --------------------------------------------------------------------------

def diff_one_summary(jsonl_path, session_id, summary, receipts_dir):
    ts = summary["ts"]
    window = find_committed_window(session_id, ts)
    if window is None:
        window = synthesize_window(jsonl_path, session_id, ts, receipts_dir,
                                    summary_line=summary["line"])
    queued = find_queued_commands(jsonl_path)
    core_body = core_window_body(window["body"])
    quotes = extract_quotes(summary["text"])
    rows = []
    counts = {"FOUND-VERBATIM": 0, "FOUND-NEAR": 0, "FOUND-IN-QUEUED-ONLY": 0, "NOT-IN-WINDOW": 0}
    for q in quotes:
        v = verdict_for_quote(q, core_body, queued, check_queued=True)
        counts[v["verdict"]] += 1
        rows.append({"quote": q, **v})
    win_user_turns = window.get("counts", {}).get("user_text_turns")
    # SUSPICIOUS-ZERO-QUOTES: real dialogue happened in the window but the
    # summary quoted none of it -- either it's pure paraphrase (worth
    # knowing) or the quote-extraction regex missed something.
    suspicious_zero_quotes = bool(win_user_turns and win_user_turns > 0 and len(quotes) == 0)
    # SUSPICIOUS-PERFECT-MATCH: every quote in a non-trivial summary graded
    # FOUND-VERBATIM with zero FOUND-NEAR/NOT-IN-WINDOW -- "a diff of 0
    # differences is SUSPICIOUS by construction" per the ticket brief. A
    # real machine paraphrase rarely reproduces 100% of its quoted spans
    # byte-for-byte; a perfect score is either a genuinely well-behaved
    # summary or a sign the window computation leaked the summary into
    # itself (the exact bug this script's own selftest now guards against).
    suspicious_perfect_match = bool(
        win_user_turns and win_user_turns > 0 and len(quotes) > 0 and
        counts["FOUND-NEAR"] == 0 and counts["NOT-IN-WINDOW"] == 0 and
        counts["FOUND-IN-QUEUED-ONLY"] == 0 and counts["FOUND-VERBATIM"] == len(quotes))
    return {
        "session": session_id,
        "summary_ts": ts,
        "summary_line": summary["line"],
        "window_source": window["source"],
        "window_path": window.get("path"),
        "window_lo": window["lo"],
        "window_hi": window["hi"],
        "window_user_text_turns": win_user_turns,
        "n_quotes": len(quotes),
        "counts": counts,
        "rows": rows,
        "suspicious_zero_diff": suspicious_zero_quotes,
        "suspicious_perfect_match": suspicious_perfect_match,
    }


# --------------------------------------------------------------------------
# 7. Artifact writer
# --------------------------------------------------------------------------

def write_artifact(out_dir, session_id, summary, diff_result=None):
    os.makedirs(out_dir, exist_ok=True)
    sess6 = _session6(session_id)
    ts = summary["ts"] or "unknown-ts"
    utc_compact = re.sub(r"[^0-9TZ]", "", ts) or "unknown"
    fname = "%s-%s.md" % (sess6, utc_compact)
    path = os.path.join(out_dir, fname)
    sha = hashlib.sha256(summary["text"].encode("utf-8")).hexdigest()
    date_tag = ts[:10] if ts else "unknown-date"

    lines = [
        "---",
        "kind: compact-summary",
        "session: %s" % session_id,
        "summary_utc: %s" % ts,
        "jsonl_line: %d" % summary["line"],
        "sha256: %s" % sha,
        "bytes: %d" % len(summary["text"].encode("utf-8")),
        'status: "MACHINE PARAPHRASE, never a ruling; grade against the window"',
        "flagged_isCompactSummary: %s" % summary["flagged_isCompactSummary"],
        "type_summary: %s" % summary["type_summary"],
        "prefix_matched: %s" % summary["prefix_matched"],
        "generated_by: extract_compact_summary.py",
        "---",
        "",
        "## [COMPACT-SUMMARY:%s]" % date_tag,
        "",
        summary["text"],
        "",
    ]

    if diff_result is not None:
        d = diff_result
        lines += [
            "## DIFF",
            "",
            "window_source: %s" % d["window_source"],
            "window_path: %s" % (d["window_path"] or "(none — synthesized in-memory, not written to disk)"),
            "window_range: (%s -> %s]" % (d["window_lo"], d["window_hi"]),
            "window_user_text_turns: %s" % d["window_user_text_turns"],
            "quotes_found_in_summary: %d" % d["n_quotes"],
            "counts: FOUND-VERBATIM=%d FOUND-NEAR=%d FOUND-IN-QUEUED-ONLY=%d NOT-IN-WINDOW=%d" % (
                d["counts"]["FOUND-VERBATIM"], d["counts"]["FOUND-NEAR"],
                d["counts"]["FOUND-IN-QUEUED-ONLY"], d["counts"]["NOT-IN-WINDOW"]),
        ]
        if d["suspicious_zero_diff"]:
            lines.append("SUSPICIOUS-ZERO-QUOTES: window has %s user text turn(s) but the summary "
                          "yielded ZERO quoted spans — report, do not silently pass." % d["window_user_text_turns"])
        if d["suspicious_perfect_match"]:
            lines.append("SUSPICIOUS-PERFECT-MATCH: all %d quote(s) graded FOUND-VERBATIM, zero "
                          "FOUND-NEAR/NOT-IN-WINDOW/FOUND-IN-QUEUED-ONLY — a diff of 0 differences "
                          "is suspicious by construction; verify the window bound did not leak the "
                          "summary into itself." % d["n_quotes"])
        lines.append("")
        for i, r in enumerate(d["rows"], 1):
            lines.append("%d. [%s] %r" % (i, r["verdict"], r["quote"]))
            if r["detail"]:
                lines.append("   %s" % r["detail"])
        lines.append("")

    text = "\n".join(lines)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path, sha, len(text.encode("utf-8"))


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def session_id_of(jsonl_path):
    return os.path.splitext(os.path.basename(jsonl_path))[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--jsonl", nargs="+", required=True)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    ap.add_argument("--diff", action="store_true")
    ap.add_argument("--receipts-dir", default=DEFAULT_RECEIPTS_DIR)
    args = ap.parse_args(argv)

    rc = 0
    for jsonl_path in args.jsonl:
        if not os.path.isfile(jsonl_path):
            print("ERROR file-not-found: %s" % jsonl_path)
            rc = 1
            continue
        session_id = session_id_of(jsonl_path)
        summaries = find_compact_summaries(jsonl_path, all_summaries=args.all)
        if not summaries:
            print("INFO no-compact-summary-found: %s" % jsonl_path)
            continue
        for summary in summaries:
            diff_result = None
            if args.diff:
                diff_result = diff_one_summary(jsonl_path, session_id, summary, args.receipts_dir)
            path, sha, nbytes = write_artifact(args.out_dir, session_id, summary, diff_result)
            print("WROTE %s  sha256=%s  bytes=%d  line=%d  ts=%s" % (
                path, sha, nbytes, summary["line"], summary["ts"]))
            if diff_result:
                d = diff_result
                flags = "".join([
                    "  SUSPICIOUS-ZERO-QUOTES" if d["suspicious_zero_diff"] else "",
                    "  SUSPICIOUS-PERFECT-MATCH" if d["suspicious_perfect_match"] else "",
                ])
                print("  DIFF window=%s(%s) quotes=%d verdicts=%s%s" % (
                    d["window_source"], d["window_path"] or "in-memory", d["n_quotes"], d["counts"], flags))
    return rc


if __name__ == "__main__":
    sys.exit(main())
