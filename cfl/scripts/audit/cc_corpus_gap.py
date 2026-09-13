#!/usr/bin/env python3
"""Claude Code corpus gap — the SESSION CLASS that never reaches the corpus.

WHY THIS EXISTS
---------------
Jon's most consequential statements are made in Claude Code **main sessions** — the
coordinator sessions where scope is set and rulings are given. Those are exactly the
sessions systematically absent from the mirror corpus. What survives instead is their
SUBAGENT extracts: 377 of them on disk, versus 54 primary extracts, and every one of
those subagent files opens with a banner saying it carries none of Jon's authority.

The measured consequence, 2026-07-26: two sentences this program quotes as Jon-verbatim
have no locatable Jon turn behind them. They exist only as a model's quotation of a main
session that was never exported. A quotation with no record behind it is indistinguishable
from an invention, and nothing in this repo could tell the difference.

Root cause is structural, not accidental: `extract_claude_code_sessions.py` runs against
sessions that have ENDED. A live session is not in the corpus, by construction. Retention
(`cleanupPeriodDays`, default 30) then destroyed many before extraction ever ran — that
half is fixed (set to 3650 on 2026-07-25), but the live-session hole is still open and
NOTHING MEASURES IT. This file is the measurement. `extract_live_session.py` is the close.

WHY MAIN AND SUBAGENT ARE COUNTED SEPARATELY, NEVER POOLED
----------------------------------------------------------
They are different record classes with different authority. A subagent transcript's
`## Dispatch` turns were authored by an orchestrating agent, not by Jon; a main session's
`## Human` turns are Jon. Pooling them produces a coverage percentage that looks healthy
precisely BECAUSE the low-authority class dominates the count 363-to-29 on disk. That
average is the defect wearing a reassuring number, so the two totals never touch here.

WHY mtime AND SIZE ARE REJECTED AS THE STALENESS SIGNAL
-------------------------------------------------------
This repo has already been burned by both, and both are still live in the codebase:

  - `extract_claude_code_sessions.needs_extract()` calls mtime "the RELIABLE 'grew/changed'
    signal". It is not one here. The corpus lives on Google Drive, whose mirroring rewrites
    mtimes independently of content; a refresh pass rewrites an .md (new mtime) while
    covering exactly the same records; and a JSONL copied out of an archive carries the
    copy's mtime, not the session's. mtime answers "was this file touched", which is a
    different question from "does this markdown cover those records".
  - `RATIO_FLOOR = 0.20`, the md/jsonl size backstop, fires on essentially every healthy
    session — its own comment records measured ratios of 0.0019 to 0.159, i.e. ALL of them
    below the floor. An alarm that always fires carries no information.

So staleness here is measured by COUNTING THE SAME THING ON BOTH SIDES, content-derived,
never by a filesystem attribute:

  jsonl side : `convert-claude-code.extract_turn_records()` — the canonical turn walk, the
               same one that produced the markdown in the first place.
  md side    : `turn_index.index()` — the ratified, fence-aware turn enumerator every wiki
               citation already resolves against.

If the JSONL now yields more turns than the markdown contains, the markdown is behind by
exactly that difference. Both numbers come from the repo's own authorities, so this check
cannot drift away from what the extractor and the citation layer actually believe.

...BUT A RAW TURN DEFICIT IS ITSELF A PROXY, AND IT LIES TOO
------------------------------------------------------------
The first run of this file reported 18 of 22 main extracts STALE. That number was wrong in
the direction that manufactures alarm, and the reason is the same class of error it was
written to avoid. On 2026-07-25 `convert-claude-code.py` gained an entire turn class:
`Tool Result` records (a `user` record whose content is a LIST) had been dropped outright
by every earlier version. So an extract written before that date is missing those turns
*because the parser changed*, not because the session grew. Measured across all 22:

  - 0 of 22 markdowns contain a single `## Tool Result` header;
  - for 16 of them, `md_turns + jsonl_tool_result_turns == jsonl_turns` EXACTLY
    (e.g. da51cc: 2415 + 1165 = 3580), i.e. the whole deficit is the new class;
  - Human-turn counts match exactly in 21 of 22 — no Jon turn was missed at all.

Only 2 sessions have a deficit that survives excluding the new class, and only 1 is
missing a Jon turn. Calling all 18 "stale" would have reported the live-session hole as
~9x its true size and sent re-extraction work after files that are not behind on content.

So the deficit is decomposed rather than totalled:

  STALE (growth)  — the markdown is behind on turns that the added class does NOT explain.
                    This is the live-session hole, and it is the number that matters.
  REPARSE-DUE     — the deficit is fully explained by turn classes the extract's parser
                    did not have. Real work (the tool payloads are absent from the corpus),
                    but NOT evidence that a session escaped capture.

and the Human-turn delta is reported on its own line regardless, because "how many of Jon's
turns exist in a JSONL but not in the corpus" is the actual question this audit answers.

A record-level watermark is preferred when present: files written by
`extract_live_session.py` carry `captured_through_record: N` in frontmatter, which is
compared directly against the JSONL's record count. That is a stronger signal than the
turn comparison because it is exact and stated by the writer rather than inferred.
Measured 2026-07-27: 0 of 54 primary extracts carry one, and 0 primary sidecars (which
would carry `total_records:`) exist on disk at all — so for every pre-existing primary
extract the turn comparison IS the only available measurement. That absence is itself
reported below, as `watermark absent`, rather than being silently scored as "current".

WHAT `history.jsonl` ADDS THAT NOTHING ELSE CAN
-----------------------------------------------
`~/.claude/history.jsonl` records every typed prompt with its `sessionId`, and it SURVIVES
the retention sweep that deletes the session JSONLs themselves. It is therefore the only
on-disk evidence that a session ever existed after its JSONL is gone. A session id present
in history with NEITHER a JSONL NOR an extract is permanently lost — unrecoverable, no
Anthropic-side restore path. Counting them is the difference between "we lost some" and a
number Jon can act on. Only ids and counts are read out of this file; the `display` field
holds prompt text and is never printed.

NOTHING IS CACHED. Every count above is recomputed from disk on every run. A cached count
is a fact written down once that then diverges with nothing able to notice — the
characteristic failure this program keeps paying for.

Usage:
    python scripts/audit/cc_corpus_gap.py
    python scripts/audit/cc_corpus_gap.py --list          # session ids per bucket
    python scripts/audit/cc_corpus_gap.py --strict        # exit 1 if any gap remains
    python scripts/audit/cc_corpus_gap.py --projects-root DIR   # audit an archive copy
"""
import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from turn_index import index as turn_index  # the ratified turn enumerator

# The corpus is pinned absolute for the same reason extract_claude_code_sessions.py pins it:
# there is exactly ONE corpus no matter which checkout you run from. Code follows the
# checkout; data stays put. --corpus-root overrides for testing against a copy.
CORPUS_ROOT = Path(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer")
CODE_ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = Path.home() / ".claude" / "projects"
HISTORY = Path.home() / ".claude" / "history.jsonl"

HEX6 = re.compile(r"[0-9a-f]{6}")


def load_converter(code_root):
    """Import convert-claude-code.py by path (its filename has hyphens, so it is not
    importable by name). The canonical turn walk must come from the same module the
    extractor uses — a reimplementation here would be a second source of truth about
    what counts as a turn, which is precisely how the two sides drift apart.
    """
    p = code_root / "skills" / "chat-exporter" / "scripts" / "convert-claude-code.py"
    if not p.exists():
        p = CORPUS_ROOT / "skills" / "chat-exporter" / "scripts" / "convert-claude-code.py"
    if not p.exists():
        sys.exit(f"ERROR: converter not found (looked under {code_root} and {CORPUS_ROOT})")
    spec = importlib.util.spec_from_file_location("convert_claude_code", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, p


def read_frontmatter(md_path, fields):
    """Line-scan the leading `---` block for flat scalar fields.

    Deliberately not a YAML parse: the corpus has no yaml dependency, these values are
    flat scalars, and one malformed file must not take the whole audit down. Same
    approach as extract_claude_code_sessions.read_frontmatter().
    """
    out = {}
    try:
        with open(md_path, "r", encoding="utf-8", errors="replace") as f:
            if f.readline().strip() != "---":
                return out
            for line in f:
                if line.strip() == "---":
                    break
                if ":" in line:
                    k, _, v = line.partition(":")
                    if k.strip() in fields:
                        out[k.strip()] = v.strip()
    except OSError:
        pass
    return out


# --------------------------------------------------------------------------
# JSONL enumeration — main vs subagent, deduped by SESSION ID not by filename
# --------------------------------------------------------------------------

def iter_main_jsonls(projects_root):
    """{session_uuid: path} for every TOP-LEVEL session JSONL.

    Top-level only, matching extract_claude_code_sessions.iter_session_jsonls(): a
    `<uuid>/subagents/agent-*.jsonl` is a different record class with different
    authority and is enumerated separately. Deduped by uuid because worktree renames
    leave the same session visible under two project dirs.
    """
    out = {}
    if not projects_root.is_dir():
        return out
    for d in sorted(projects_root.iterdir()):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.jsonl")):
            out.setdefault(p.stem, p)
    return out


def iter_subagent_jsonls(projects_root):
    """{agent_id: path} for every subagent transcript, deduped by agentId."""
    out = {}
    if not projects_root.is_dir():
        return out
    for d in sorted(projects_root.iterdir()):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*/subagents/agent-*.jsonl")):
            out.setdefault(p.stem[len("agent-"):], p)
    return out


def count_records(jsonl_path):
    """Number of valid JSON lines — the SAME definition convert-claude-code.load_events()
    uses for its record count, so `captured_through_record: N` and this number are
    directly comparable. Blank lines are skipped; a line that does not parse is not a
    record. Counted fresh, never cached.
    """
    n = 0
    try:
        with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    json.loads(line)
                except json.JSONDecodeError:
                    continue
                n += 1
    except OSError:
        return 0
    return n


# --------------------------------------------------------------------------
# Extract enumeration — keyed by SESSION ID, never by filename
# --------------------------------------------------------------------------

FM_FIELDS = ("source_id", "agent_id", "capture_state", "captured_through_record",
             "sidechain_records", "char_count")


def is_transcript_md(p):
    return (p.suffix == ".md"
            and p.name != "index.md"
            and not p.name.endswith(".sidecar.md")
            and "payloads" not in p.parts)


def index_extracts(corpus_root):
    """Return (main_extracts, sub_extracts), each {session_id: {...}}.

    Keyed by the id the file DECLARES in frontmatter (`source_id` for a primary,
    `agent_id` for a subagent) — authoritative, and it survives the file being renamed
    or moved. The 6-hex filename prefix is kept only as a fallback index for files
    predating those fields, never as the primary key: ~400 ids in a 16^6 space is a
    small but real collision risk, and a collision would make one session's extract
    answer for another's.
    """
    out_dir = corpus_root / "raw" / "transcripts" / "claude-code"
    sub_root = out_dir / "subagents"
    main, sub = {}, {}
    if not out_dir.is_dir():
        return main, sub

    for p in sorted(out_dir.rglob("*.md")):
        if not is_transcript_md(p):
            continue
        fm = read_frontmatter(p, FM_FIELDS)
        is_sub = sub_root in p.parents
        if is_sub:
            key = (fm.get("agent_id") or fm.get("source_id", "")
                   or fm.get("uuid", "")).removeprefix("agent-")
        else:
            # TWO FIELD NAMES, ONE FACT — and reading only one of them manufactured a
            # corpus-loss crisis. 26 extracts declare `uuid:` and 107 declare `source_id:`;
            # this read `source_id` alone, got "", fell through to the filename fallback
            # below, and reported every one of them LOST. It was not finding losses. It was
            # finding a field name. A registry of 29 "permanently lost" sessions was then
            # published on that output, and a reconstruction was dispatched against a session
            # that has a real 12.67 MB transcript on disk.
            #
            # Caught by herald-wiki, reading CFL's published claim and checking it.
            key = fm.get("source_id", "") or fm.get("uuid", "")
        rec = {"path": p, "fm": fm, "key": key or None,
               # FALLBACK GUARD. `p.name[:6]` is the literal string "code-2" for every
               # `code-2026-*.md`, which matches no session id and silently routes the file
               # to LOST. A fallback that always produces the same wrong answer is worse than
               # no fallback. Take the first 6-hex run from the filename instead, and if there
               # is none, emit "" so the file is reported UNKEYED rather than lost.
               "prefix": (key[:6] if key
                          else (re.search(r"[0-9a-f]{6}", p.name).group(0)
                                if re.search(r"[0-9a-f]{6}", p.name) else ""))}
        (sub if is_sub else main)[key or str(p)] = rec

    return main, sub


def build_prefix_map(extracts):
    """{first-6-of-id: [record, ...]} fallback index for extracts with no usable id."""
    m = {}
    for rec in extracts.values():
        m.setdefault(rec["prefix"], []).append(rec)
    return m


def md_claimed_records(rec):
    """(value, basis) for how many JSONL records this markdown claims to cover.

    Preference order, strongest first:
      1. `captured_through_record: N`  — stated explicitly by extract_live_session.py.
      2. `sidechain_records: X of Y`   — subagent primaries carry the total as Y.
      3. companion `.sidecar.md` `total_records: N`.
    Returns (None, "absent") when no file states one. Absent is REPORTED, never
    silently treated as "covered" — an unmeasurable file is not a healthy file.
    """
    fm = rec["fm"]
    v = fm.get("captured_through_record")
    if v and v.strip().isdigit():
        return int(v.strip()), "captured_through_record"
    sc = fm.get("sidechain_records", "")
    m = re.search(r"(\d+)\s+of\s+(\d+)", sc)
    if m:
        return int(m.group(2)), "sidechain_records"
    side = rec["path"].with_name(rec["path"].name[:-3] + ".sidecar.md")
    if side.exists():
        sfm = read_frontmatter(side, ("total_records",))
        t = sfm.get("total_records", "")
        if t.strip().isdigit():
            return int(t.strip()), "sidecar total_records"
    return None, "absent"


def md_turn_profile(rec):
    """(total_turns, {role_letter: count}) for an extracted markdown, or None.

    Role letters are turn_index.py's own: H=Human, A=Assistant, C=Compaction,
    R=Tool Result, D=Dispatch. The per-role breakdown is what makes the
    growth-vs-reparse decomposition possible — a bare total cannot distinguish
    "the session grew" from "the parser learned a new record class".
    """
    try:
        idx = turn_index(str(rec["path"]))
    except Exception:
        return None
    counts = {}
    for t in idx["turns"]:
        counts[t["role"]] = counts.get(t["role"], 0) + 1
    return idx["turn_count"], counts


# convert-claude-code role name -> turn_index role letter. Kept explicit so the two
# vocabularies are reconciled in ONE place rather than assumed equal at each use.
ROLE_LETTER = {"Human": "H", "Assistant": "A", "Compaction": "C",
               "Tool Result": "R", "Dispatch": "D"}


# --------------------------------------------------------------------------
# Per-class audit
# --------------------------------------------------------------------------

def audit_class(label, jsonls, extracts, converter, verbose_errors):
    """Compare one record class. Returns a dict of buckets holding SESSION IDS ONLY."""
    prefix_map = build_prefix_map(extracts)
    res = {"label": label, "total_jsonl": len(jsonls), "extracted": [], "missing": [],
           "stale": [], "reparse": [], "current": [], "unmeasurable": [], "ahead": [],
           "orphan_extracts": [], "watermark_absent": 0, "watermark_present": 0,
           "human_in_jsonl": 0, "human_in_md": 0, "human_missing": []}

    matched_extract_keys = set()

    for sid, path in sorted(jsonls.items()):
        rec = extracts.get(sid)
        if rec is None:
            cands = prefix_map.get(sid[:6], [])
            rec = cands[0] if len(cands) == 1 else None
        if rec is None:
            res["missing"].append(sid)
            continue

        matched_extract_keys.add(id(rec))
        res["extracted"].append(sid)

        n_records = count_records(path)
        claimed, basis = md_claimed_records(rec)
        if claimed is None:
            res["watermark_absent"] += 1
        else:
            res["watermark_present"] += 1

        # The turn walk runs REGARDLESS of whether a watermark exists: the watermark
        # answers "how far did the writer get", the turn profile answers "how many of
        # Jon's turns are in the corpus". The second question is the one being asked,
        # and no watermark can answer it.
        try:
            events = converter.load_events(path)
            jrecords = converter.extract_turn_records(events)
        except Exception as e:
            res["unmeasurable"].append((sid, f"jsonl walk failed: {type(e).__name__}"))
            if verbose_errors:
                print(f"    ! {sid[:6]}: {e}", file=sys.stderr)
            continue

        jsonl_turns = len(jrecords)
        jcounts = {}
        for r, _t, _e in jrecords:
            L = ROLE_LETTER.get(r, "?")
            jcounts[L] = jcounts.get(L, 0) + 1

        prof = md_turn_profile(rec)
        if prof is None:
            res["unmeasurable"].append((sid, "md turn index failed"))
            continue
        md_turns, mcounts = prof

        # Jon's own turns — tracked separately and always, for both classes. ('H' in a
        # subagent transcript should be 0; a nonzero one would itself be a finding.)
        res["human_in_jsonl"] += jcounts.get("H", 0)
        res["human_in_md"] += mcounts.get("H", 0)
        h_delta = jcounts.get("H", 0) - mcounts.get("H", 0)
        if h_delta > 0:
            res["human_missing"].append((sid, f"{h_delta} Jon turn(s) not in corpus"))

        # A stated watermark that is behind the record count is unambiguous growth — no
        # decomposition needed, the writer itself says it stopped early.
        if claimed is not None and claimed < n_records:
            res["stale"].append(
                (sid, f"records {claimed}/{n_records} ({basis}), +{h_delta} Jon turn(s)"))
            continue

        # Decompose the deficit. Classes the markdown has ZERO of, but the JSONL yields,
        # are classes its parser did not have — that deficit is reparse-due, not growth.
        missing_classes = {L for L in jcounts if jcounts[L] > 0 and mcounts.get(L, 0) == 0}
        explained = sum(jcounts[L] for L in missing_classes)
        deficit = jsonl_turns - md_turns

        if deficit <= 0:
            if deficit < 0:
                # Extract covers MORE than the live JSONL yields — legitimate when it came
                # from an archive copy longer than what survives live. Reported, never
                # averaged into "current": it means the live file is not the best copy.
                res["ahead"].append((sid, f"turns {md_turns}/{jsonl_turns}"))
            else:
                res["current"].append(sid)
        elif deficit > explained:
            res["stale"].append(
                (sid, f"turns {md_turns}/{jsonl_turns}, {deficit - explained} unexplained"
                      f" by absent class(es) {sorted(missing_classes) or '-'}"
                      f", +{h_delta} Jon turn(s)"))
        else:
            res["reparse"].append(
                (sid, f"turns {md_turns}/{jsonl_turns}; deficit {deficit} fully explained"
                      f" by class(es) {sorted(missing_classes)} the parser lacked"))

    for rec in extracts.values():
        if id(rec) not in matched_extract_keys:
            res["orphan_extracts"].append(rec["key"] or rec["path"].name)

    return res


def print_class(res, show_list):
    n = res["total_jsonl"]
    pct = (100 * len(res["extracted"]) // n) if n else 0
    print(f"\n{res['label']}")
    print(f"  JSONLs on disk (deduped by session id)        : {n}")
    print(f"  ...extracted to markdown                      : {len(res['extracted'])}  ({pct}%)")
    print(f"  ...NOT EXTRACTED — no markdown at all         : {len(res['missing'])}")
    print(f"  of those extracted:")
    print(f"      current (md covers the whole jsonl)       : {len(res['current'])}")
    print(f"      STALE — jsonl grew past the md            : {len(res['stale'])}")
    print(f"      reparse-due — deficit is a parser class   : {len(res['reparse'])}")
    print(f"      md ahead of live jsonl (archive is longer): {len(res['ahead'])}")
    print(f"      unmeasurable (walk or index failed)       : {len(res['unmeasurable'])}")
    print(f"      stated record watermark present / absent  : "
          f"{res['watermark_present']} / {res['watermark_absent']}")
    print(f"  extracts with NO live jsonl (md is the only copy): {len(res['orphan_extracts'])}")
    print(f"  Jon turns: {res['human_in_md']} in corpus / {res['human_in_jsonl']} in jsonl"
          f"  -> {res['human_in_jsonl'] - res['human_in_md']} MISSING"
          f" across {len(res['human_missing'])} session(s)")

    if show_list:
        for bucket, title in (("missing", "NOT EXTRACTED"), ("stale", "STALE (growth)"),
                              ("human_missing", "MISSING JON TURNS"),
                              ("reparse", "REPARSE-DUE"),
                              ("ahead", "MD AHEAD"), ("unmeasurable", "UNMEASURABLE")):
            items = res[bucket]
            if not items:
                continue
            print(f"    --- {title} ---")
            for it in items:
                if isinstance(it, tuple):
                    print(f"      {it[0]}  [{it[1]}]")
                else:
                    print(f"      {it}")


# --------------------------------------------------------------------------
# history.jsonl — the ledger that outlives the sessions
# --------------------------------------------------------------------------

def audit_history(history_path, main_jsonls, main_extracts):
    """Session ids in history.jsonl with no JSONL and no extract = permanently lost.

    Reads `sessionId` and `project` ONLY. The `display` field is the typed prompt text
    and is never read into any structure that gets printed.
    """
    if not history_path.exists():
        return None
    ids = {}
    lines = 0
    for line in open(history_path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        lines += 1
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(o, dict):
            continue
        sid = o.get("sessionId")
        if sid:
            e = ids.setdefault(sid, {"prompts": 0, "project": o.get("project", "")})
            e["prompts"] += 1

    extract_prefixes = {r["prefix"] for r in main_extracts.values()}
    extract_keys = set(main_extracts.keys())

    has_jsonl, has_extract_only, lost = [], [], []
    for sid in sorted(ids):
        if sid in main_jsonls:
            has_jsonl.append(sid)
        elif sid in extract_keys or sid[:6] in extract_prefixes:
            has_extract_only.append(sid)
        else:
            lost.append(sid)
    return {"lines": lines, "ids": ids, "has_jsonl": has_jsonl,
            "extract_only": has_extract_only, "lost": lost}


def main():
    ap = argparse.ArgumentParser(description="Claude Code corpus gap auditor")
    ap.add_argument("--projects-root", default=str(PROJECTS_ROOT),
                    help="scan DIR instead of ~/.claude/projects (e.g. an archive copy)")
    ap.add_argument("--corpus-root", default=str(CORPUS_ROOT),
                    help="repo root holding raw/transcripts/claude-code")
    ap.add_argument("--history", default=str(HISTORY))
    ap.add_argument("--list", action="store_true", help="print session ids per bucket")
    ap.add_argument("--no-history", action="store_true")
    ap.add_argument("--verbose-errors", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any gap remains")
    a = ap.parse_args()

    projects_root = Path(a.projects_root)
    corpus_root = Path(a.corpus_root)
    converter, conv_path = load_converter(CODE_ROOT)

    main_jsonls = iter_main_jsonls(projects_root)
    sub_jsonls = iter_subagent_jsonls(projects_root)
    main_extracts, sub_extracts = index_extracts(corpus_root)

    print("=== CLAUDE CODE CORPUS GAP — is the MAIN-SESSION class in the corpus? ===\n")
    print("Main sessions are where Jon rules. Subagent transcripts carry none of his")
    print("authority and outnumber them ~12:1 on disk, so the two are never pooled here.")
    print("Staleness is measured by counting turns on BOTH sides with the repo's own")
    print("authorities (canonical walk vs ratified enumerator) — never by mtime or size.\n")
    print(f"  projects root : {projects_root}")
    print(f"  corpus root   : {corpus_root / 'raw' / 'transcripts' / 'claude-code'}")
    print(f"  converter     : {conv_path}")

    m = audit_class("MAIN SESSIONS", main_jsonls, main_extracts, converter, a.verbose_errors)
    s = audit_class("SUBAGENT TRANSCRIPTS", sub_jsonls, sub_extracts, converter, a.verbose_errors)
    print_class(m, a.list)
    print_class(s, a.list)

    h = None
    if not a.no_history:
        h = audit_history(Path(a.history), main_jsonls, main_extracts)
        print("\nHISTORY LEDGER (~/.claude/history.jsonl — survives the retention sweep)")
        if h is None:
            print("  history.jsonl not present — permanently-lost count NOT MEASURABLE.")
        else:
            print(f"  prompt records read                           : {h['lines']}")
            print(f"  distinct session ids in history               : {len(h['ids'])}")
            print(f"  ...with a live JSONL on disk                  : {len(h['has_jsonl'])}")
            print(f"  ...JSONL gone but an extract survives         : {len(h['extract_only'])}")
            print(f"  ...NEITHER — PERMANENTLY LOST                 : {len(h['lost'])}")
            if h["lost"]:
                shown = h["lost"] if a.list else h["lost"][:15]
                print(f"    --- permanently lost session ids"
                      f"{'' if a.list else ' (first 15; --list for all)'} ---")
                for sid in shown:
                    e = h["ids"][sid]
                    print(f"      {sid}  ({e['prompts']} prompt record(s), project={e['project']})")

    gaps = (len(m["missing"]) + len(m["stale"]) + len(s["missing"]) + len(s["stale"]))
    print("\n" + "=" * 72)
    print(f"MAIN     : {len(m['missing'])} unextracted, {len(m['stale'])} stale, "
          f"{len(m['reparse'])} reparse-due, "
          f"{m['human_in_jsonl'] - m['human_in_md']} Jon turn(s) on disk but not in corpus")
    print(f"SUBAGENT : {len(s['missing'])} unextracted, {len(s['stale'])} stale, "
          f"{len(s['reparse'])} reparse-due")
    if h:
        print(f"LOST     : {len(h['lost'])} session ids in history with no JSONL and no extract")
    if gaps:
        print(f"\n{gaps} session(s) are absent or behind. A live session is not in the corpus")
        print("until something snapshots it — see scripts/extract_live_session.py.")
        return 1 if a.strict else 0
    print("\nNo gap: every JSONL on disk has a markdown that covers all of its records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
