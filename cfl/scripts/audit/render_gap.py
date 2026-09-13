#!/usr/bin/env python3
"""render_gap.py -- render every session this trunk has on disk but not in markdown. Step 1 of Jon's order.

Jon, 2026-09-12 manual trigger, verbatim, typos his:

    "1. RENDER FIRST. Every session under your project key whose transcript JSONL is newer than its
     render, plus every session with no render at all. Raw logs are the point: a .jsonl that was never
     rendered is invisible to every markdown index in this fleet."

⛔ WHY A BACKUP METHOD, and Jon named the principle in the same message ("using backup methods if
needed"). The obvious tool refuses the job:
  * `auto_mint_windows.py` prints `auto-mint: nothing unconsumed; 0 to do` -- it drives off UNCONSUMED
    PRECOMPACT RECEIPTS, so a session with no receipt is outside its population by construction. It is
    not broken and it cannot do this.
  * `mint_window.py` is the sole emitter and takes `jsonl lo hi --out`. It CAN do the job, per session,
    over the full line range.
⭐ So the backup method is: derive the gap with `render_horizon.py`, then drive `mint_window.py` over
each gap session's whole range. No new emitter is written -- the committed format keeps one author.

⚠️ WHAT THIS IS NOT: a replacement for the receipt-driven path. A window minted here has NO precompact
receipt behind it, so it is labelled `gapfill` in its filename and is a RENDER, never a boundary
record. Confusing the two is how a compact-summary once got quoted as a Jon ruling.

Exit: 0 all gap sessions rendered (or none pending) · 1 at least one render failed · 2 the gap could
not be derived, which is UNKNOWN and dominates · 3 usage.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts", "audit"))
MINT = os.path.join(ROOT, "scripts", "audit", "mint_window.py")
OUT_MAIN = os.path.join(ROOT, "raw", "transcripts", "claude-code", "gapfill")
OUT_SUB = os.path.join(ROOT, "raw", "transcripts", "claude-code", "subagents", "gapfill")


def gap():
    import render_horizon as rh
    dirs, derr = rh.project_dirs_list()
    if derr:
        return None, None, derr
    recs = rh.records(dirs)
    idx, _unk = rh.render_index()
    missing, stale = [], []
    for sid, p, sz, mt, kind in recs:
        stem = sid[6:] if sid.startswith("agent-") else sid
        hit = idx.get(stem[:6].lower())
        if hit is None:
            missing.append((sid, p, sz, mt, kind))
        elif mt > hit[0] + 1:
            stale.append((sid, p, sz, mt, kind))
    return missing, stale, None


def nlines(p):
    n = 0
    try:
        with open(p, "rb") as f:
            for _ in f:
                n += 1
    except OSError:
        return None
    return n


def render_one(sid, path, kind, stamp):
    n = nlines(path)
    if not n:
        return False, "0 lines or unreadable"
    stem = sid[6:] if sid.startswith("agent-") else sid
    out_dir = OUT_SUB if kind == "subagent" else OUT_MAIN
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "code-%s-%s-gapfill-%s.md" % (stamp, stem[:6], time.strftime("%H%M%S")))
    try:
        r = subprocess.run([sys.executable, MINT, path, "1", str(n), "--out", out],
                           capture_output=True, text=True, timeout=600)
    except Exception as exc:
        return False, "%s: %s" % (type(exc).__name__, exc)
    if r.returncode != 0:
        return False, "mint exit %d: %s" % (r.returncode, (r.stderr or r.stdout)[-300:])
    if not os.path.isfile(out) or os.path.getsize(out) == 0:
        return False, "mint exited 0 and wrote no bytes -- the silent-EINVAL shape, treated as FAILURE"
    return True, out


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass
    limit = None
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])
    dry = "--dry-run" in argv
    missing, stale, err = gap()
    if err:
        print("⛔ UNKNOWN: could not derive the gap -- %s" % err)
        return 2
    todo = [(r, "no-render") for r in missing] + [(r, "stale") for r in stale]
    todo.sort(key=lambda t: -t[0][2])
    print("=== RENDER GAP -- step 1 ===")
    print("  no-render: %d | stale: %d | total to do: %d%s"
          % (len(missing), len(stale), len(todo), (" (limit %d)" % limit) if limit else ""))
    if dry:
        for (sid, p, sz, mt, kind), why in todo[:limit or 20]:
            print("  WOULD render %-9s %-9s %10d B  %s" % (why, kind, sz, sid))
        return 0
    stamp = time.strftime("%Y-%m-%d")
    ok = bad = 0
    for (sid, p, sz, mt, kind), why in (todo[:limit] if limit else todo):
        good, info = render_one(sid, p, kind, stamp)
        if good:
            ok += 1
            print("  RENDERED %-9s %-9s %10d B  %s -> %s" % (why, kind, sz, sid[:20], os.path.basename(info)))
        else:
            bad += 1
            print("  ⛔ FAILED %-9s %-9s %10d B  %s -- %s" % (why, kind, sz, sid[:20], info))
    print("\n  rendered %d | failed %d" % (ok, bad))
    print("  ⚠️ Re-run render_horizon.py to see the new gap. It will NOT be zero: this session's own")
    print("     jsonl grows while this runs, which is the reason step 3 says a zero has not measured.")
    # ⭐ ALWAYS-PRINTED FINAL LINE, added 2026-09-12 ~19:2x at Professional's request, and the
    # reason is a shape this program keeps paying for: this script is now the FIRST Stop hook with a
    # 30-second timeout, and A HOOK THAT TIMED OUT LOOKS IDENTICAL TO ONE THAT RAN AND FOUND NOTHING
    # TO DO. One terminal line naming both counts is the difference between a receipt and a silence.
    print("  RENDER-GAP DONE: rendered %d | failed %d | remaining to do %d" % (ok, bad, max(0, len(todo) - ok - bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
