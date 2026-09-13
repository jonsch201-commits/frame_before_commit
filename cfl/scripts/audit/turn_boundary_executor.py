#!/usr/bin/env python
"""turn_boundary_executor.py -- ONE cheap wiki-executor pass at a turn boundary (M-9 prototype).

Jon approved this CONDITIONAL ON COST (map row M-9: "Jon-approved conditional on token
efficiency") -- so the acceptance test is that the pass MEASURES ITS OWN COST and reports it
in its own output. It does. The cost pattern follows scripts/audit/turn_cost_report.py:
proxy units in input-token equivalents with the formula printed, never dollars.

What one pass does (and all it does):
  A. Find the LAST real user turn (origin.kind == 'human', not isMeta, not a tool_result
     carrier) in the session JSONL at/before --as-of, and distill its text into a retrieval
     query (content words, stopwords dropped, first-occurrence order, capped).
  B. Run that query through the GraphRAG index (hybrid; falls back to lexical with a printed
     bound if the embedder cannot load) and print the TOP-3 citations.
  C. Print the index's STALE state (Index.staleness() -- a stale index must announce itself).
  D. Print the OPEN TAKE rows from exchange/WORK-CLAIMS.md (TAKE with no later DONE/RELEASE
     on the same work item) -- the "what am I mid-way through" half of the boundary.
  E. Report its own cost: wall-time per phase + the estimated token load its own printout
     would add to the session context if injected at the boundary.

⛔ THIS SCRIPT DOES NOT WIRE ITSELF. Hook wiring (PostToolUse / turn-boundary hook) is
PROPOSAL-ONLY, same posture as exchange/memory-core-v0/hooks/WIRING-PROPOSAL.md -- hooks die
per-session (measured 08-20), so any wiring must carry the liveness self-check. Run by hand:

  python scripts/audit/turn_boundary_executor.py --session 643640a7 --as-of 2026-08-22
  python scripts/audit/turn_boundary_executor.py --selftest

ASCII-safe stdout by construction. Paths cross process boundaries as argv, never inline
in -c program text.
"""

import argparse
import glob
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def _key_for(path):
    """~/.claude/projects sanitises a path by replacing every non-alphanumeric
    CHARACTER (not run) with '-'. Mirrors extract_claude_code_sessions.py's _key_for."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(path)).strip("-")


_PROJECTS_ROOT = os.path.join(os.path.expanduser("~"), ".claude", "projects")

# ⛔ THIS WAS PINNED TO THE G: KEY, AND THE 2026-09-02 G:->N: MOVE SILENTLY DEMOTED IT
# TO A TRUNK CFL LEFT THREE DAYS AGO -- a --session lookup against current work would
# fail (or resolve a same-prefix G: collision) with no error naming the real cause. No
# --project-dir override exists here, so resolve_session() below searches EVERY
# candidate dir (current-derived first, then historical) rather than one hardcoded path.
PROJECT_DIR_CANDIDATES = [
    os.path.join(_PROJECTS_ROOT, _key_for(REPO)),  # DERIVED: current checkout
    os.path.join(_PROJECTS_ROOT,
                 "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer"),  # historical
]
# kept so any external caller importing the old name still works; searched dirs are
# PROJECT_DIR_CANDIDATES, not this single value.
PROJECT_DIR = PROJECT_DIR_CANDIDATES[0]
DEFAULT_CLAIMS = os.path.join(REPO, "exchange", "WORK-CLAIMS.md")

# Cost proxy weight for injected context: printed output lands as INPUT tokens at the next
# API call (weight 1.0 in turn_cost_report.py's ratio table). Token estimate is chars/4 --
# an ESTIMATE, stated as such in the report; the harness tokenizer is not invoked here.
W_INPUT = 1.0
CHARS_PER_TOKEN = 4.0

STOPWORDS = set("""
a an and are as at be been but by can could did do does for from had has have he her his how
i if in into is it its just me my no not of on or our out she so some than that the their
them then there these they this to up us was we were what when where which who why will with
would you your yours am were done need needs let lets also very really please ok okay yeah
went going get got make made want wants like now then here going go
""".split())


def asc(s):
    return str(s).encode("ascii", "replace").decode("ascii")


def resolve_session(arg):
    """Same convention as turn_cost_report.py: a path, or a uuid prefix under one of
    PROJECT_DIR_CANDIDATES (current-derived checked before historical)."""
    if os.path.isfile(arg):
        return arg
    hits = []
    for d in PROJECT_DIR_CANDIDATES:
        for h in sorted(glob.glob(os.path.join(d, arg + "*.jsonl"))):
            if os.path.isfile(h) and h not in hits:
                hits.append(h)
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit("ERROR: no session file matches %r under any of %s"
                 % (arg, PROJECT_DIR_CANDIDATES))
    sys.exit("ERROR: %d session files match %r: %s"
             % (len(hits), arg, [os.path.basename(h) for h in hits]))


def is_turn_boundary(rec):
    m = rec.get("message") or {}
    cont = m.get("content")
    if isinstance(cont, list):
        kinds = set(b.get("type") for b in cont if isinstance(b, dict))
        return kinds != {"tool_result"}
    return True


def user_text(rec):
    m = rec.get("message") or {}
    cont = m.get("content")
    if isinstance(cont, list):
        cont = " ".join(b.get("text", "") for b in cont if isinstance(b, dict))
    return re.sub(r"\s+", " ", str(cont or "")).strip()


def last_human_turn(path, as_of):
    """Return (record, bounds). Prefers origin.kind=='human'; falls back to any non-meta
    turn boundary with a printed bound (fallback_used)."""
    bounds = {"lines": 0, "parse_errors": 0, "beyond_as_of": 0,
              "human_turns": 0, "other_turns": 0, "fallback_used": False}
    last_human, last_other = None, None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            bounds["lines"] += 1
            try:
                rec = json.loads(line)
            except ValueError:
                bounds["parse_errors"] += 1
                continue
            ts = rec.get("timestamp") or ""
            if ts and ts[:10] > as_of:
                bounds["beyond_as_of"] += 1
                continue
            if rec.get("type") != "user" or not is_turn_boundary(rec):
                continue
            if (rec.get("origin") or {}).get("kind") == "human" and not rec.get("isMeta"):
                bounds["human_turns"] += 1
                last_human = rec
            elif not rec.get("isMeta"):
                bounds["other_turns"] += 1
                last_other = rec
    rec = last_human
    if rec is None and last_other is not None:
        rec = last_other
        bounds["fallback_used"] = True
    return rec, bounds


def topic_query(text, cap=12):
    """Content words of the turn, stopwords dropped, first-occurrence order, deduped."""
    out, seen = [], set()
    for tok in re.findall(r"[A-Za-z0-9_\-\.]{2,}", text.lower()):
        tok = tok.strip(".-_")
        if len(tok) < 2 or tok in STOPWORDS or tok in seen:
            continue
        seen.add(tok)
        out.append(tok)
        if len(out) >= cap:
            break
    return " ".join(out)


def open_take_rows(claims_path):
    """OPEN = a TAKE row whose work item has no LATER row with verb DONE or RELEASE.
    Registry rows are '| at | seat | verb | work item | pointer |' in file order (append-only,
    so file order IS time order). Returns (open_rows, bounds)."""
    bounds = {"rows": 0, "takes": 0, "closed": 0, "malformed": 0, "missing": False}
    if not os.path.isfile(claims_path):
        bounds["missing"] = True
        return [], bounds
    opens = {}  # work item -> (at, seat)
    with open(claims_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 5 or cells[0] in ("at", "---"):
                if len(cells) >= 1 and cells[0] not in ("at", "---") and line.count("|") > 2:
                    bounds["malformed"] += 1
                continue
            at, seat, verb, item = cells[0], cells[1], cells[2], cells[3]
            bounds["rows"] += 1
            if verb == "TAKE":
                bounds["takes"] += 1
                opens[item] = (at, seat)
            elif verb in ("DONE", "RELEASE") and item in opens:
                bounds["closed"] += 1
                del opens[item]
    rows = [(at, seat, item) for item, (at, seat) in opens.items()]
    rows.sort()
    return rows, bounds


def run_retrieval(query, db, k=3, mode="hybrid"):
    """Top-k citations via the GraphRAG index. Returns (items, mode_used, note)."""
    sys.path.insert(0, os.path.join(REPO, "scripts", "graphrag"))
    try:
        from retrieve import Index  # noqa: E402
    except Exception as exc:
        return [], "none", "retrieve.py unimportable: %s" % asc(exc)
    try:
        idx = Index(db) if db else Index()
    except SystemExit as exc:
        return [], "none", str(exc)
    items, used, note = [], mode, ""
    try:
        if mode == "hybrid":
            order, _, _ = idx.hybrid(query, None, k)
            ranked = [(cid, info["rrf"]) for cid, info in order]
        else:
            ranked, _, _ = idx.lexical(query, None)
            ranked = ranked[:k]
    except SystemExit as exc:  # embedder mismatch/missing refuses loudly -- degrade, say so
        used = "lexical"
        note = "hybrid unavailable (%s) -- fell back to lexical" % asc(str(exc)[:120])
        ranked, _, _ = idx.lexical(query, None)
        ranked = ranked[:k]
    rows = idx.chunk_rows([cid for cid, _ in ranked])
    for cid, score in ranked:
        r = rows.get(cid)
        if r:
            flat = " ".join((r["text"] or "").split())[:160]
            items.append(("%s:%s-%s" % (r["path"], r["start_line"], r["end_line"]),
                          round(float(score), 5), r["heading"] or "", flat))
    stale, why = idx.staleness()
    return items, used, note or "", (stale, why)


def execute(args, out_lines):
    """The one pass. Appends report lines; returns phase timings."""
    P = out_lines.append
    timings = []

    t0 = time.perf_counter()
    path = resolve_session(args.session)
    rec, jb = last_human_turn(path, args.as_of)
    if rec is None:
        P("FAIL: no user turn boundary at/before %s in %s" % (args.as_of, asc(path)))
        return timings
    text = user_text(rec)
    query = topic_query(text)
    timings.append(("A topic-from-last-turn", time.perf_counter() - t0))

    P("TURN-BOUNDARY EXECUTOR (one pass, as-of %s)" % args.as_of)
    P("session      : %s" % asc(os.path.basename(path)))
    P("last turn    : %s  origin=%s%s" % (
        (rec.get("timestamp") or "")[:19],
        asc((rec.get("origin") or {}).get("kind") or "user"),
        "  [BOUND: no origin-human turn found; last non-meta boundary used]"
        if jb["fallback_used"] else ""))
    P("turn text    : %s" % asc(text[:110]))
    P("query        : %s" % asc(query))

    t0 = time.perf_counter()
    if not query:
        P("RETRIEVAL    : skipped (empty query after stopword strip)")
        stale_state = None
    else:
        items, used, note, stale_state = run_retrieval(query, args.db, k=3, mode=args.mode)
        P("RETRIEVAL    : mode=%s  top-%d" % (used, len(items)))
        if note:
            P("  BOUND      : %s" % note)
        for i, (src, score, heading, snip) in enumerate(items, 1):
            P("  %d. %s  score=%s" % (i, asc(src), score))
            if heading:
                P("     # %s" % asc(heading))
            P("     %s" % asc(snip))
        if not items:
            P("  (no results -- an empty top-3 is a finding, not a silent pass)")
    timings.append(("B retrieval", time.perf_counter() - t0))

    t0 = time.perf_counter()
    if stale_state is None:
        P("STALE        : not checked (no retrieval ran)")
    else:
        stale, why = stale_state
        P("STALE        : %s%s" % ("STALE -- " + asc(why) if stale else "fresh", ""))
    timings.append(("C staleness", time.perf_counter() - t0))

    t0 = time.perf_counter()
    takes, cb = open_take_rows(args.claims)
    if cb["missing"]:
        P("OPEN TAKEs   : registry not found at %s" % asc(args.claims))
    else:
        P("OPEN TAKEs   : %d open of %d TAKE rows (%d closed by DONE/RELEASE)"
          % (len(takes), cb["takes"], cb["closed"]))
        for at, seat, item in takes:
            P("  - [%s %s] %s" % (asc(at), asc(seat), asc(item[:90])))
    timings.append(("D open-claims", time.perf_counter() - t0))

    P("")
    P("MEASURED BOUNDS: jsonl %d lines, %d parse errors, %d beyond as-of; turns human=%d other=%d; claims rows=%d malformed-ish=%d"
      % (jb["lines"], jb["parse_errors"], jb["beyond_as_of"], jb["human_turns"],
         jb["other_turns"], cb.get("rows", 0), cb.get("malformed", 0)))
    return timings


def cost_block(out_lines, timings, t_total):
    """Phase E -- the acceptance test Jon set: the pass reports its own cost."""
    text = "\n".join(out_lines)
    est_tokens = int(len(text) / CHARS_PER_TOKEN + 0.5)
    proxy = est_tokens * W_INPUT
    lines = [
        "",
        "SELF-COST (the acceptance test: the pass measures itself)",
        "  formula     : est_tokens = output_chars / 4 (ESTIMATE, tokenizer not invoked);",
        "                proxy_units = est_tokens * 1.0 (injected output = INPUT tokens, per turn_cost_report.py ratios)",
        "  output size : %d chars -> ~%d tokens -> %.0f proxy units if injected at the boundary"
        % (len(text), est_tokens, proxy),
        "  model tokens consumed BY this pass itself: 0 (pure script; the only token cost IS the injection above)",
        "  wall time   : %.2f s total" % t_total,
    ]
    for name, dt in timings:
        lines.append("    %-24s %.2f s" % (name, dt))
    lines.append("  not measured: this cost block's own ~%d chars are excluded from the estimate; cache dynamics at the real boundary (a repeated injection becomes cache_read at 0.1x)" % sum(len(x) for x in lines))
    return lines


def selftest():
    """Synthetic JSONL + synthetic registry in a temp dir; no live index required."""
    import tempfile
    ok = True

    def check(name, passed):
        nonlocal_ok[0] = nonlocal_ok[0] and passed
        print("  %s %s" % ("PASS" if passed else "FAIL", name))

    nonlocal_ok = [True]
    tmp = tempfile.mkdtemp(prefix="tbe-selftest-")
    try:
        # -- synthetic session: meta turn, human turn, tool_result carrier, task-notification
        jl = os.path.join(tmp, "fake-session.jsonl")
        recs = [
            {"type": "user", "isMeta": True, "timestamp": "2026-08-22T01:00:00Z",
             "message": {"content": "harness injection, must not be picked"}},
            {"type": "user", "origin": {"kind": "human"}, "timestamp": "2026-08-22T02:00:00Z",
             "message": {"content": "please fix the barrier memory consolidation index"}},
            {"type": "user", "timestamp": "2026-08-22T03:00:00Z",
             "message": {"content": [{"type": "tool_result", "content": "x"}]}},
            {"type": "user", "origin": {"kind": "task-notification"},
             "timestamp": "2026-08-22T04:00:00Z",
             "message": {"content": "agent finished, must not beat the human turn"}},
            {"type": "user", "origin": {"kind": "human"}, "timestamp": "2026-08-23T05:00:00Z",
             "message": {"content": "BEYOND as-of, must be excluded"}},
        ]
        with open(jl, "w", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")
        rec, jb = last_human_turn(jl, "2026-08-22")
        check("picks the human turn (not meta/carrier/notification)",
              rec is not None and "consolidation" in user_text(rec))
        check("as-of excludes the later human turn", jb["beyond_as_of"] == 1)
        check("counts: human=1 other=1", jb["human_turns"] == 1 and jb["other_turns"] == 1)

        q = topic_query("please fix THE the barrier memory consolidation index and and")
        check("topic query drops stopwords + dedupes",
              q == "fix barrier memory consolidation index")

        # -- synthetic registry: open TAKE, closed TAKE, RELEASE-closed TAKE
        cl = os.path.join(tmp, "claims.md")
        with open(cl, "w", encoding="utf-8") as fh:
            fh.write("| at | seat | verb | work item | pointer |\n")
            fh.write("|---|---|---|---|---|\n")
            fh.write("| t1 | s/f | TAKE | closed thing | p |\n")
            fh.write("| t2 | s/f | DONE | closed thing | p |\n")
            fh.write("| t3 | s/f | TAKE | open thing | p |\n")
            fh.write("| t4 | s/f | TAKE | released thing | p |\n")
            fh.write("| t5 | s/f | RELEASE | released thing | p |\n")
        takes, cb = open_take_rows(cl)
        check("open-TAKE logic: exactly the open thing survives",
              len(takes) == 1 and takes[0][2] == "open thing")
        check("closed count = 2 (DONE + RELEASE)", cb["closed"] == 2)

        # -- full pass end-to-end against the synthetic inputs (retrieval degrades honestly
        #    if the live index is absent; the cost block must appear either way)
        ns = argparse.Namespace(session=jl, as_of="2026-08-22", db=None,
                                mode="lexical", claims=cl)
        out = []
        t0 = time.perf_counter()
        timings = execute(ns, out)
        out.extend(cost_block(out, timings, time.perf_counter() - t0))
        text = "\n".join(out)
        check("report carries query line", "query        : fix barrier memory" in text)
        check("report carries open TAKE row", "open thing" in text)
        check("report carries SELF-COST block with proxy units",
              "SELF-COST" in text and "proxy units" in text and "wall time" in text)
        check("cost formula printed (auditability)", "output_chars / 4" in text)
        live_index_note = ("retrieval exercised against LIVE index"
                           if "RETRIEVAL    : mode=" in text and "no results" not in text
                           else "retrieval ran degraded/empty -- BOUND: live-index content not asserted by selftest")
        print("  NOTE %s" % live_index_note)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    ok = nonlocal_ok[0]
    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="One cheap wiki-executor pass at a turn boundary (M-9). Proposal-only for hooks; run by hand.")
    ap.add_argument("--session", help="session uuid (or prefix) or a path to a .jsonl")
    ap.add_argument("--as-of", metavar="YYYY-MM-DD",
                    help="reporting date; records after this date are excluded (repo convention, no default)")
    ap.add_argument("--db", default=None, help="index path (default: build_index.py's off-Drive DEFAULT_DB)")
    ap.add_argument("--mode", default="hybrid", choices=["hybrid", "lexical"])
    ap.add_argument("--claims", default=DEFAULT_CLAIMS, help="WORK-CLAIMS registry path")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if not args.session or not args.as_of:
        sys.exit("ERROR: --session and --as-of are required (or --selftest)")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.as_of):
        sys.exit("ERROR: --as-of must be YYYY-MM-DD")
    out = []
    t0 = time.perf_counter()
    timings = execute(args, out)
    out.extend(cost_block(out, timings, time.perf_counter() - t0))
    print("\n".join(out))


if __name__ == "__main__":
    main()
