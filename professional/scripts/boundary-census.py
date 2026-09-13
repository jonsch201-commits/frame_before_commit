#!/usr/bin/env python3
"""BOUNDARY CENSUS -- derive compact boundaries from a source the boundary cannot suppress.

WHY THIS EXISTS. lint C29 grades compact boundaries from `exchange/precompact-receipts.log`.
That log is written BY the PreCompact hook. So a boundary whose hook died writes no line, is
not in C29's population, and CANNOT FAIL C29 -- the check whose entire purpose is catching
boundaries with no durable record. Measured 2026-09-02: this trunk compacted twice with the
hook dead ("Invalid request code", Google Drive file-handle leak); zero receipt lines exist
for that date; C29 FAILED on the PREVIOUS day's boundary while blind to both of these.

  predicate: receipt lines      claim: compact boundaries
  separator: a boundary that emitted no receipt

GROUND TRUTH. `~/.claude/projects/<project>/*.jsonl` carries one
`{"type":"system","subtype":"compact_boundary","compactMetadata":{...}}` entry per boundary.
It is on C:, written by the harness, and stayed readable through the entire G: fault -- so it
survives exactly the failure that suppresses the receipt.

UNRECORDED MUST FAIL, NOT VANISH.
"""
import sys, json, glob, os, argparse, datetime
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

def boundaries_from_jsonl(project_dir):
    out = []
    for f in sorted(glob.glob(os.path.join(project_dir, "*.jsonl"))):
        sess = os.path.splitext(os.path.basename(f))[0]
        try:
            fh = open(f, encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"UNREADABLE {f}: {e}", file=sys.stderr); continue
        with fh:
            for n, line in enumerate(fh, 1):
                if '"compact_boundary"' not in line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if o.get("type") == "system" and o.get("subtype") == "compact_boundary":
                    out.append({"session": sess, "line": n, "ts": o.get("timestamp")})
    return out

def receipts(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path, encoding="utf-8", errors="replace"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2:
            rows.append({"ts": parts[0], "session": parts[1]})
    return rows

def main():
    ap = argparse.ArgumentParser()
    # R4 (2026-09-04): default derived by scripts/project_dirs.py, never typed.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import project_dirs
    _dirs = project_dirs.existing_dirs(project_dirs.ROOT)
    ap.add_argument("--project-dir", default=(_dirs[0] if _dirs else "UNKNOWN-no-project-dir"))
    ap.add_argument("--receipts", default="exchange/precompact-receipts.log")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        # POSITIVE CONTROL: a receipt log missing a boundary that the JSONL has must FAIL.
        b = boundaries_from_jsonl(a.project_dir)
        if not b:
            print("SELFTEST BROKEN: no boundaries found in ground truth; cannot control"); return 3
        sess = {x["session"] for x in b}
        got = sess - {r["session"] for r in receipts(a.receipts)}
        print(f"SELFTEST: ground truth has {len(b)} boundary(ies) across {len(sess)} session(s); "
              f"{len(got)} session(s) have NO receipt line at all")
        if not got:
            print("SELFTEST BROKEN: every session already has a receipt -- the check cannot "
                  "currently be shown to fail, so it is not yet a check"); return 3
        print("VERDICT: SELFTEST PASS -- the unrecorded case exists and is detected")
        return 0

    b = boundaries_from_jsonl(a.project_dir)
    r = receipts(a.receipts)
    rs = {x["session"] for x in r}
    bysess = {}
    for x in b:
        bysess.setdefault(x["session"], []).append(x)
    # EPOCH. The recorder (scripts/precompact-capture.sh) landed 2026-08-15; its first receipt
    # line is 2026-08-15 19:48:23. Boundaries BEFORE that had no recorder to miss them, and
    # counting them as failures inflates the finding fourfold -- measured: 18 raw unrecorded,
    # of which 14 are pre-recorder and 4 are real. Print BOTH; grade only the real ones.
    EPOCH = os.environ.get("BOUNDARY_EPOCH", "2026-08-15")
    unrec_all = {s: v for s, v in bysess.items() if s not in rs}
    pre = sum(1 for v in unrec_all.values() for x in v if (x["ts"] or "")[:10] < EPOCH)
    unrec = {}
    for s, v in unrec_all.items():
        post = [x for x in v if (x["ts"] or "")[:10] >= EPOCH]
        if post:
            unrec[s] = post
    print(f"POPULATION: {len(b)} compact_boundary entr(ies) in {len(bysess)} session(s) "
          f"[ground truth: session JSONL on C:]; {len(r)} receipt line(s) in {a.receipts} "
          f"covering {len(rs)} session(s). "
          f"{pre} unrecorded boundary(ies) PRE-DATE the recorder (before {EPOCH}) and are "
          f"BACKLOG, printed not graded.")
    for s, v in sorted(unrec.items()):
        ts = ", ".join(sorted({(x['ts'] or '?')[:19] for x in v}))
        print(f"  UNRECORDED session {s}: {len(v)} boundary(ies) with NO receipt line -- {ts}")
    if unrec:
        n = sum(len(v) for v in unrec.values())
        print(f"VERDICT: FAIL -- {n} boundary(ies) across {len(unrec)} session(s) left no "
              f"durable record. A boundary the recorder missed is exactly what a receipt-based "
              f"check cannot see.")
        return 1
    print("VERDICT: PASS -- every session with a compact boundary has a receipt line")
    return 0

if __name__ == "__main__":
    sys.exit(main())
