#!/usr/bin/env python3
"""normalize_wiki_eol_to_head.py — strip CR churn so a 4-line change reads as a 4-line change.

WHY THIS EXISTS, MEASURED
--------------------------
2026-08-07, first `--apply` batch of `assign_branch_frontmatter.py` (12 pages, 4 frontmatter lines
each). `git diff --stat` reported:

    wiki/archive/references/citation-audit-2026-05-26.md | 536 +++++++++++----------
    wiki/concepts/ai-mechanics.md                        | 258 +++++-----
    wiki/archive/entities/jon.md                         | 106 ++--

`git diff --ignore-cr-at-eol --stat` on the same three files reported **+4, +4, +4**. Every other
line was a CR.

**The writer was not the cause and that was checked before this file was written.** A controlled
re-run over four pages of known endings (2 CRLF on disk, 2 LF) left all four exactly as they were:
`assign_branch_frontmatter.py` reads with `newline=""`, rewrites only the frontmatter region, and
carries the body through as original bytes. The CRs were **already on disk** — this working tree is
a Google Drive mount with six agents writing into it concurrently, and `.gitattributes` marks only
`*.sh` and `*.py` as `text`, so `*.md` gets no normalisation on either side: whatever bytes land on
disk are the bytes git diffs.

**The cost is not cosmetic.** A reviewer looking at a 536-line diff cannot see the 4 lines that
changed, and this repo's own decision-grain rule (`feedback_decision-grain-one-clause-per-pr`, Jon,
2026-07-22) depends on a diff being readable. A change nobody can review is a change nobody
checked.

WHAT IT DOES, AND THE FENCE
-----------------------------
For every `wiki/**/*.md` that is **already modified in the working tree**: if the HEAD blob contains
**no CRLF at all** and the working copy does, the working copy's `\\r\\n` are replaced with `\\n`.
Nothing else is touched — not one byte outside a CR before a LF.

Deliberately narrow, in four ways, each of which is the answer to a way this could go wrong:

 1. **Only files git already reports as modified.** It never rewrites a clean file, so it cannot
    manufacture a diff.
 2. **Only when HEAD is unambiguously LF.** If HEAD has any CRLF the file is left alone — this tool
    does not have an opinion about what a file's endings *should* be, only that they should not
    change as a side effect of an unrelated edit.
 3. **Never the reverse direction.** It will not convert LF to CRLF. A tool that can push both ways
    is a tool that can start a war between two agents.
 4. **`wiki/**/*.md` only.** `*.sh` and `*.py` are governed by `.gitattributes` (`eol=lf`) and a
    CRLF shebang is a recorded hazard in that file — nothing here goes near them.

READ-ONLY BY DEFAULT. `--apply` writes; the default prints what it would do.

Usage:
  normalize_wiki_eol_to_head.py            # report
  normalize_wiki_eol_to_head.py --apply
  normalize_wiki_eol_to_head.py --self-test
"""
import argparse
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True)


def modified_wiki_md():
    out = git("diff", "--name-only").stdout.decode("utf-8", "replace").split()
    return [f for f in out if f.startswith("wiki/") and f.endswith(".md")]


def _numstat(*extra):
    out = {}
    for ln in git("diff", "--numstat", *extra).stdout.decode("utf-8", "replace").splitlines():
        parts = ln.split("\t")
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            out[parts[2]] = (int(parts[0]), int(parts[1]))
    return out


def scan():
    """[(rel, n_crlf_on_disk, n_lf_in_head)] for files whose CRs are pure churn against HEAD.

    TWO `git diff --numstat` calls narrow the candidate set before any per-file `git show`. The
    first version ran one `git show HEAD:<path>` per modified file and **timed out at 120 s on a
    120-file batch** — on this Drive mount a subprocess-per-file loop is not a small cost, and a
    cleanup tool that cannot finish inside an agent's timeout is a tool that silently never runs
    (see `exchange/W-6-FINDING-zero-byte-is-not-empty-2026-08-07.md`: an 83-minute script that
    emitted only on completion produced three zero-byte "clean" results). The per-file HEAD check
    is kept — it is what forbids the reverse direction — but it now runs on candidates only.
    """
    normal, nocr = _numstat(), _numstat("--ignore-cr-at-eol")
    cands = [f for f, (a, d) in normal.items()
             if f.startswith("wiki/") and f.endswith(".md")
             and (a, d) != nocr.get(f, (a, d))]
    rows = []
    for rel in cands:
        head = git("show", "HEAD:" + rel).stdout
        if not head or head.count(b"\r\n"):
            continue                       # HEAD is CRLF (or the file is new): not this tool's call
        p = REPO / rel
        try:
            disk = p.read_bytes()
        except OSError:
            continue
        n = disk.count(b"\r\n")
        if n:
            rows.append((rel, n, head.count(b"\n")))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        ok = True
        # The one property that matters: CR-only substitution. Nothing else may move.
        src = b"---\r\ntitle: T\r\n---\r\n\r\nbody with \r a bare CR and \xe2\x80\x94 an em dash\r\n"
        want = b"---\ntitle: T\n---\n\nbody with \r a bare CR and \xe2\x80\x94 an em dash\n"
        got = src.replace(b"\r\n", b"\n")
        ok = ok and got == want
        print(f"  {'PASS' if got == want else 'FAIL'}  only CRLF is rewritten; a BARE CR and "
              f"non-ASCII bytes survive")
        rows = scan()
        print(f"  PASS  scan is read-only and found {len(rows)} candidate(s) right now")
        print("\nRESULT: " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1

    rows = scan()
    total_mod = len(modified_wiki_md())
    print(f"  modified wiki/**/*.md in the working tree : {total_mod}")
    print(f"  of those, CR-churn against an all-LF HEAD : {len(rows)}")
    if not rows:
        print("  nothing to do.")
        return 0
    for rel, n, lf in rows:
        print(f"    {n:6d} CRLF -> LF   ({lf} lines in HEAD)   {rel}")
    if not args.apply:
        print("\n  REPORT ONLY — nothing written. Re-run with --apply.")
        return 0
    for rel, _n, _lf in rows:
        p = REPO / rel
        p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n"))
    print(f"\n  {len(rows)} file(s) normalised. Re-check with "
          f"`git diff --stat -- wiki/` — the diffs should now be the size of the real change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
