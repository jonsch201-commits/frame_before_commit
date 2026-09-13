#!/usr/bin/env python3
"""finding_consequence.py — FRAME 1. Grade a finding by what CHANGED, not by what was decided.

WHY, Jon 2026-09-05 (paraphrased from his `/wayfinder` on the restart block; his own words are in
exchange/RESTART-BLOCK-2026-09-05.md): CFL found three defects that would have wrecked his restart
and filed a RUNBOOK. He had to tell it to block.

⛔ THE SENTENCE THAT INDICTS IT IS CFL'S OWN, written earlier the same day on
wiki/tracker/wayfinder-compact-barrier-2026-09-04.md: *"A finding with no consequent is a log line."*
The barrier's verifier had caught a compact summary naming 1 of 13 LIVE maps, reported it, and
NOTHING CHANGED. ⭐ Detection is solved in this trunk. CONSEQUENCE is not.

WHAT THIS ADDS THAT `finding_consequent.py` DOES NOT
---------------------------------------------------
That script grades a finding for a DISPOSITION -- a WORD (FIXED / TICKETED / DECLINED / ACCEPTED).
⚠️ A disposition is a claim about intent. **This grades for an ARTIFACT: something on disk whose
state is different because the finding existed, and which can be checked without believing anyone.**

  FIXED with no commit          -> DISPOSITIONED-ONLY. The word is not the change.
  "ticketed as P3-10"           -> that is finding_consequent's job, not this one.
  "fixed in abc1234"            -> CONSEQUENT if that object exists in this repo.
  "G28"                         -> CONSEQUENT if GATES.md carries that gate.
  "scripts/audit/runlock.py"    -> CONSEQUENT if the path exists.

⛔ THE GRADES ARE THREE, AND THE MIDDLE ONE IS THE POINT:
  CONSEQUENT             an artifact is named AND resolves. The finding moved something.
  CLAIMED-UNVERIFIABLE   an artifact is named and does NOT resolve. ⚠️ WORSE THAN NONE: it reads as
                         done. A dangling sha or a gate id that is not in the ledger is a claim
                         wearing evidence's clothes.
  NONE                   no artifact named at all. Honest, and a log line.

⚠️ WHAT THIS DOES NOT MEASURE, stated because every gate here now has to say so: it does NOT check
that the artifact ADDRESSES the finding. A commit that exists and is irrelevant grades CONSEQUENT.
This is a check for the LINK, not for the CURE -- naming what it cannot see is the whole discipline
(soul's BOUND line, adopted).

  finding_consequence.py [--file F] [--repo R] [--self-test]
  exit 0 clean · 1 any CLAIMED-UNVERIFIABLE (a false green) · 2 unreadable input (UNKNOWN)
"""
import argparse
import io
import os
import re
import subprocess
import sys

# ⛔ THE cp1252 GUARD, AND THE STORY OF HOW IT GOT HERE IS THE POINT OF THIS WHOLE FILE.
# This script was written WITH the entry-point case soul proved necessary an hour earlier
# (ask_elder.py case 11). Cases 1-9 passed. CASE 10 -- the one that actually invokes the
# program -- FAILED, and so did case 11 and 12: stdout on this machine is cp1252, the BOUND and
# ZERO-ROWS lines contain ⚠️, and the process died AFTER computing every grade correctly.
# ⭐ So the grades were right, the exit code was 1 for the wrong reason, and NINE GREEN CASES
# SAID NOTHING ABOUT IT. The same defect ask_elder.py documents in its own header, committed by
# the same author, in a new file, within the hour -- and caught only because the entry-point
# case was adopted from a peer the same night. ⚠️ A LESSON WRITTEN DOWN IS NOT A LESSON APPLIED.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(HERE))

# a finding row: a leading bullet or table row that carries a disposition word
DISPOSITION = re.compile(r"\b(FIXED|TICKETED|DECLINED|ACCEPTED|CLOSED|STRUCK|WITHDRAWN)\b")
SHA = re.compile(r"\b([0-9a-f]{7,40})\b")
GATE = re.compile(r"\bG(\d{1,3})\b")
PATH = re.compile(r"\b((?:scripts|wiki|exchange|skills|evidence)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]{1,5})\b")


def _git_has(repo, sha):
    try:
        r = subprocess.run(["git", "-C", repo, "cat-file", "-e", sha + "^{object}"],
                           capture_output=True, timeout=30)
        return r.returncode == 0
    except Exception:
        return False


def artifacts(line):
    """Every artifact this line CLAIMS, as (kind, token). Order is report order, not priority."""
    out = []
    for m in GATE.finditer(line):
        out.append(("gate", "G" + m.group(1)))
    for m in PATH.finditer(line):
        out.append(("path", m.group(1)))
    for m in SHA.finditer(line):
        tok = m.group(1)
        # a bare decimal run is not a sha; require at least one letter so "1691" is not a commit
        if re.search(r"[a-f]", tok) and not re.fullmatch(r"[0-9]+", tok):
            out.append(("sha", tok))
    return out


def resolve(kind, token, repo, gates_text):
    if kind == "gate":
        return bool(re.search(r"^- \[[ xX]\] %s:" % re.escape(token), gates_text, re.MULTILINE))
    if kind == "path":
        return os.path.exists(os.path.join(repo, token))
    if kind == "sha":
        return _git_has(repo, token)
    return False


def grade_line(line, repo, gates_text):
    """-> (grade, [(kind, token, resolved)]) for one finding row."""
    claims = artifacts(line)
    if not claims:
        return "NONE", []
    checked = [(k, t, resolve(k, t, repo, gates_text)) for k, t in claims]
    if any(r for _, _, r in checked):
        # at least one artifact resolves -> the finding moved something real
        return ("CONSEQUENT" if all(r for _, _, r in checked) else "CONSEQUENT-PARTIAL"), checked
    return "CLAIMED-UNVERIFIABLE", checked


# ⛔ FOLDED IN 2026-09-05 by the coordinator, found by pointing this function at REAL files
# (exchange/RESTART-BLOCK-2026-09-05.md, exchange/FRAMES-week-between-PR3-and-PR4.md) rather than a
# fixture: both scanned as 0 rows, including the most consequence-bearing block written that night
# ("1. ✅ **MEMORY COPIED, per trunk, verified.**"). NUMBERED ROWS ARE ROWS. The extractor only
# recognized "-", "*" and "|" as a block marker, so a numbered list was invisible to it -- and worse,
# a numbered row sitting after an unrelated bullet got silently swallowed as that bullet's
# CONTINUATION line instead of being missed outright. Both the block-START test and the
# block-END (continuation-break) test need this pattern, or the second failure mode reappears.
ROWNUM = re.compile(r"^\d{1,3}[.)]\s")


def extract_blocks(text, trigger_re):
    """Generic bullet/table-BLOCK extractor, factored out of grade() below for reuse by other
    detectors (e.g. absence_claims.py) that need the same "a bullet is its marker line plus every
    indented continuation line" rule but grade on a different trigger than DISPOSITION.

    -> list of (line_no_1_based, joined_block_text, first_line_stripped_110)
    Only blocks whose joined text matches trigger_re are returned.
    """
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not (s.startswith("-") or s.startswith("|") or s.startswith("*") or ROWNUM.match(s)):
            i += 1
            continue
        start = i
        block = [s]
        j = i + 1
        while j < len(lines):
            raw = lines[j]
            nxt = raw.strip()
            if not nxt:
                break
            if not (raw.startswith("  ") or raw.startswith("\t")):
                break
            if nxt.startswith("-") or nxt.startswith("*") or nxt.startswith("|") or ROWNUM.match(nxt):
                break
            block.append(nxt)
            j += 1
        joined = " ".join(block)
        i = j if j > i + 1 else i + 1
        if not trigger_re.search(joined):
            continue
        out.append((start + 1, joined, s[:110]))
    return out


def grade(text, repo, gates_text):
    """Grade BULLET BLOCKS, not single lines.

    ⛔ THE FIRST VERSION GRADED ONE LINE AT A TIME AND WAS WRONG ON ITS SECOND REAL RUN. It read
    PR3-DESCRIPTION.md, found a row saying "STRUCK", graded it NONE, and the author dutifully added
    the commit sha -- ON THE CONTINUATION LINE, where a line-at-a-time reader cannot see it. It
    still said NONE. ⭐ The instrument built to catch "a claim with no artifact" was itself unable to
    see an artifact that was right there, and it would have driven its own author to keep adding
    citations it could never credit. A markdown bullet is a BLOCK: the marker line plus every
    indented line under it, and the evidence usually lives in the indent.
    """
    lines = text.splitlines()
    rows = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not (s.startswith("-") or s.startswith("|") or s.startswith("*")):
            i += 1
            continue
        start = i
        block = [s]
        j = i + 1
        # continuation: indented, non-empty, and not itself a new bullet or table row
        while j < len(lines):
            raw = lines[j]
            nxt = raw.strip()
            if not nxt:
                break
            if not (raw.startswith("  ") or raw.startswith("	")):
                break
            if nxt.startswith("-") or nxt.startswith("*") or nxt.startswith("|"):
                break
            block.append(nxt)
            j += 1
        joined = " ".join(block)
        i = j if j > i + 1 else i + 1
        if not DISPOSITION.search(joined):
            continue
        g, checked = grade_line(joined, repo, gates_text)
        rows.append((start + 1, g, checked, s[:110]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="a file holding finding rows")
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.file:
        print("UNKNOWN: no --file given. An ungraded population is not a clean one.")
        return 2
    try:
        text = io.open(a.file, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print("UNKNOWN: cannot read %s (%s). Unreadable is never clean."
              % (os.path.abspath(a.file), e.__class__.__name__))
        return 2
    try:
        gates_text = io.open(os.path.join(a.repo, "GATES.md"), encoding="utf-8",
                             errors="replace").read()
    except OSError:
        gates_text = ""
        print("WARN: no GATES.md under %s -- gate ids cannot resolve and will grade "
              "CLAIMED-UNVERIFIABLE. That is a property of THIS RUN, not of the findings."
              % os.path.abspath(a.repo), file=sys.stderr)
    rows = grade(text, a.repo, gates_text)
    print("=== FINDING CONSEQUENCE === a finding with no consequent is a log line")
    print("  file : %s" % os.path.abspath(a.file))
    print("  repo : %s\n" % os.path.abspath(a.repo))
    counts = {}
    for ln, g, checked, snip in rows:
        counts[g] = counts.get(g, 0) + 1
        marks = " ".join("%s:%s%s" % (k, t, "" if r else "<-UNRESOLVED") for k, t, r in checked)
        print("  %-22s :%-5d %s" % (g, ln, snip))
        if marks:
            print("  %22s        %s" % ("", marks))
    print("\n  %d finding row(s): %s" % (len(rows), ", ".join(
        "%s=%d" % (k, v) for k, v in sorted(counts.items())) or "none"))
    bad = counts.get("CLAIMED-UNVERIFIABLE", 0)
    if not rows:
        print("  ⚠️ ZERO ROWS MATCHED. That is UNKNOWN, not clean -- either this file holds no "
              "findings or the row shape is different here. Name which before reporting it green.")
        return 2
    if bad:
        print("  ⛔ %d row(s) NAME AN ARTIFACT THAT DOES NOT RESOLVE. That reads as done and is not."
              % bad)
    print("  ⚠️ BOUND: this checks that the named artifact EXISTS, never that it ADDRESSES the "
          "finding. A real commit that is irrelevant grades CONSEQUENT.")
    return 1 if bad else 0


def self_test():
    import tempfile
    print("=== SELF-TEST -- finding_consequence ===")
    np = nf = 0

    def ok(n, got, want):
        nonlocal np, nf
        if got == want:
            np += 1
            print("  PASS  %s" % n)
        else:
            nf += 1
            print("  FAIL  %s\n        want: %r\n        got : %r" % (n, want, got))

    repo = tempfile.mkdtemp()
    os.makedirs(os.path.join(repo, "scripts", "audit"))
    io.open(os.path.join(repo, "scripts", "audit", "real.py"), "w").write("x\n")
    gates = "- [x] G28: a real gate\n  CHECK: x\n  EXPECT: y\n"

    ok("1 a path that exists -> CONSEQUENT",
       grade_line("- FIXED in scripts/audit/real.py", repo, gates)[0], "CONSEQUENT")
    ok("2 a gate id present in GATES.md -> CONSEQUENT",
       grade_line("- FIXED, gated as G28", repo, gates)[0], "CONSEQUENT")

    # ⛔ THE GRADE THAT MATTERS: a named artifact that does NOT resolve is WORSE than none, because
    # it reads as done. This is the case the whole script exists for.
    ok("3 THE POINT: a gate id NOT in the ledger -> CLAIMED-UNVERIFIABLE",
       grade_line("- FIXED, gated as G99", repo, gates)[0], "CLAIMED-UNVERIFIABLE")
    ok("4 a path that does not exist -> CLAIMED-UNVERIFIABLE",
       grade_line("- FIXED in scripts/audit/ghost.py", repo, gates)[0], "CLAIMED-UNVERIFIABLE")

    ok("5 a disposition word with NO artifact -> NONE (honest, and a log line)",
       grade_line("- FIXED. It is much better now.", repo, gates)[0], "NONE")

    # NEGATIVE CONTROLS
    ok("6 CONTROL: a line with no disposition word is not a finding row",
       len(grade("- just a bullet about scripts/audit/real.py\n", repo, gates)), 0)
    ok("7 CONTROL: prose mentioning a path is skipped unless it is a row",
       len(grade("FIXED something in scripts/audit/real.py\n", repo, gates)), 0)
    # ⚠️ a bare number must NOT be read as a commit sha -- "1,691 files" would grade the finding
    # CLAIMED-UNVERIFIABLE forever and the row would never go green no matter what was fixed
    ok("8 CONTROL: a decimal run is not a sha",
       grade_line("- FIXED, 1691 files staged", repo, gates)[0], "NONE")
    ok("9 mixed: one resolving and one not -> CONSEQUENT-PARTIAL, never a clean pass",
       grade_line("- FIXED in scripts/audit/real.py and G99", repo, gates)[0], "CONSEQUENT-PARTIAL")

    # ⛔ ENTRY-POINT CASE (soul's mutation finding, 2026-09-05): every case above tests FUNCTIONS.
    # `sys.exit(self_test() if ... else main())` means the test branch never crosses main(), so all
    # of them can pass on a program that dies on every real invocation. A CHECK THAT TESTS A
    # FUNCTION TESTS A FUNCTION.
    f = os.path.join(repo, "findings.md")
    io.open(f, "w", encoding="utf-8").write("- FIXED in scripts/audit/real.py\n- FIXED as G99\n")
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--file", f, "--repo", repo],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=120)
    ok("10 THE ENTRY POINT RUNS, and exits 1 on the unverifiable row",
       (r.returncode, "CLAIMED-UNVERIFIABLE" in r.stdout), (1, True))
    if r.returncode not in (0, 1):
        print("        child stderr tail: %s" % (r.stderr.strip().splitlines() or ["(none)"])[-1][:160])
    # 11 POSITIVE CONTROL for 10: an all-clean file must exit 0, or exit 1 means nothing
    f2 = os.path.join(repo, "clean.md")
    io.open(f2, "w", encoding="utf-8").write("- FIXED in scripts/audit/real.py\n")
    r2 = subprocess.run([sys.executable, os.path.abspath(__file__), "--file", f2, "--repo", repo],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        timeout=120)
    ok("11 CONTROL: an all-consequent file exits 0 (so exit 1 carries information)",
       r2.returncode, 0)
    # 12 an empty population is UNKNOWN, never clean
    f3 = os.path.join(repo, "empty.md")
    io.open(f3, "w", encoding="utf-8").write("nothing here\n")
    r3 = subprocess.run([sys.executable, os.path.abspath(__file__), "--file", f3, "--repo", repo],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        timeout=120)
    ok("12 zero rows matched -> exit 2 UNKNOWN, never a clean 0", r3.returncode, 2)

    print("  %d passed, %d failed" % (np, nf))
    return 0 if nf == 0 else 1


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
