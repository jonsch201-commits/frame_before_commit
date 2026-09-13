#!/usr/bin/env python3
"""lane_precondition.py -- check a queued lane's stated premise against disk BEFORE dispatching it.

WHY THIS EXISTS
---------------
2026-09-04 17:1x. The gate floor fired, found GO, and dispatched the first queued
lane from `exchange/WAKE.md`:

    S-cd-03 `a90789ef603396d52` (7 of ~12 pages already on disk, uncommitted, in
    `wiki/sources/infrastructure/` and `wiki/skills-gate/probe-packets/`,
    written 13:3x)

The lane opened, ran `git status --porcelain`, found it CLEAN, established that
all 10 sessions of the batch were already accepted or rejected and committed, and
correctly refused to invent scope. It returned "(no action)" after ~107,000
tokens.

The lane behaved perfectly. THE QUEUE WAS WRONG. Its stated premise -- "already
on disk, uncommitted" -- had been true when it was written at 13:3x and was false
by 17:1x, because another lane finished the work and committed it. Nothing
compared the two.

⭐ THAT IS THIS WEEK'S ONE DEFECT AGAIN, IN THE DISPATCHER: the queue entry and
the thing it describes have separate provenance. Every other instrument built
today checks a PUBLISHED CLAIM. This checks an INSTRUCTION, which nobody had
thought to treat as a claim at all.

⚠ AND THE COST IS ASYMMETRIC, which is why a guard is worth its own file: a lane
dispatched on a stale premise does not fail loudly. It reads the disk, finds the
work done, and returns success. The dispatcher then records a completed lane. The
only visible trace is the spend.

WHAT IT DOES
------------
Parses the paused-lane block of `exchange/WAKE.md`, and for every entry that
claims files are UNCOMMITTED under a named path, asks git whether anything is in
fact uncommitted there.

  GO            the premise holds; the lane has work waiting
  ALREADY-DONE  the premise is FALSE; dispatching would buy a confirmation
  UNKNOWN       the entry states no checkable premise, or git could not answer

⛔ UNKNOWN IS NOT GO. An entry whose premise cannot be checked is not thereby
approved -- it is a queue entry nobody can verify, which is the condition this
file exists to make visible.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
  * It does not edit the queue. A dispatcher that silently rewrites its own
    instructions is worse than a stale one; the coordinator disposes.
  * It does not judge whether the lane's WORK is worth doing -- only whether the
    premise the queue states about disk is still true.
  * An entry with no path and no "uncommitted" claim is UNKNOWN, never GO. Most
    queue entries are prose, and prose is not a precondition.

Exit: 0 at least one GO and no ALREADY-DONE | 3 at least one entry's premise is
false | 2 UNKNOWN (WAKE or git unreadable).
"""

import argparse
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# A queue entry looks like:  - S-cd-03 `a90789ef...` (7 of ~12 pages already on
# disk, uncommitted, in `wiki/sources/...` and `wiki/skills-gate/...`, written 13:3x)
# The agent id is OPTIONAL, and requiring it was a structural defect.
#
# The first version demanded a backticked hex sha, which only a lane that HAS
# ALREADY BEEN DISPATCHED has. So the queue could express RESUMPTIONS and nothing
# else -- new work had no shape it could take, and the gate floor spent three
# consecutive firings reporting an empty queue while real work sat undispatched.
# The entry naming the work did not fail to parse loudly; it simply was not seen.
ENTRY_RE = re.compile(r"^\s*-\s+\**([A-Za-z][\w-]*)\**\s+(?:`([0-9a-f]{6,})`\s*)?(.*)$")
# A premise may name a DIRECTORY (`wiki/sources/infrastructure/`) or a single
# FILE (`scripts/audit/repair_list_from_ledger.py`). The first version required a
# trailing slash, so UC-0 -- whose premise names one file -- graded UNKNOWN, and
# an unverifiable entry is exactly what this guard exists to stop being invisible.
# The path must contain a "/" so that a bare word in backticks (a lane name, a
# flag like `--selftest`) is not mistaken for a path.
PATH_RE = re.compile(r"`([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*/?)`")
UNCOMMITTED_RE = re.compile(r"\buncommitted\b", re.IGNORECASE)
# An entry may instead state a COMMAND premise:  verify: `<command>`
# GO when it exits non-zero (the check still fails, work remains); ALREADY-DONE
# when it exits 0. See grade() for why this exists.
VERIFY_RE = re.compile(r"verify:\s*`([^`]+)`")
# Struck text (~~like this~~) is SUPERSEDED and is never read as a premise.
# See parse_queue for why. Non-greedy, and DOTALL because a struck premise
# usually wraps across the joined continuation lines.
STRIKE_RE = re.compile(r"~~.*?~~", re.DOTALL)


def git_dirty_paths(repo):
    try:
        r = subprocess.run(["git", "-C", repo, "status", "--porcelain"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "%s: %s" % (type(e).__name__, e)
    if r.returncode != 0:
        return None, (r.stderr or "").strip()[:200]
    out = []
    for ln in r.stdout.splitlines():
        if len(ln) > 3:
            out.append(ln[3:].strip().strip('"'))
    return out, None


def parse_queue(text):
    """Every `- NAME \\`sha\\` (...)` bullet, with the paths and claims it states.

    ⛔ CONTINUATION LINES ARE JOINED. A bullet in WAKE.md wraps across two or three
    lines, and the paths a lane's premise names are usually on the SECOND line:

        - S-cd-03 `a90789ef603396d52` (7 of ~12 pages already on disk, uncommitted, in
          `wiki/sources/infrastructure/` and `wiki/skills-gate/probe-packets/`, ...)

    Matching one line at a time saw a premise with no paths and graded the real
    2026-09-04 entry UNKNOWN -- the guard reporting "I cannot check this" about the
    exact entry it was written to catch. Third time today a wrapped line has
    defeated a matcher; the rule is now explicit rather than rediscovered."""
    # ⛔ SCOPED TO THE PAUSED-LANE BLOCK, which this docstring has claimed since it
    # was written and the code did not do. With a strict entry regex the lie was
    # invisible -- prose bullets did not look like `NAME \`sha\``. The moment the
    # regex was loosened to admit new work, the same function returned 115 entries
    # from one file: three real ones and 112 lines of prose.
    #
    # A doc that describes a narrower behaviour than the code has is the same
    # defect as a number typed once: it was true when written and nothing
    # re-checked it. The scope is now enforced instead of described.
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines)
                  if "Paused lanes" in ln or "paused lane" in ln.lower()), None)
    if start is not None:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            s = lines[j].strip()
            # The block ends at the next top-level numbered item.
            if re.match(r"^\d+\.\s", s):
                end = j
                break
        lines = lines[start:end]

    rows, cur = [], None
    for ln in lines:
        m = ENTRY_RE.match(ln)
        if m:
            if cur:
                rows.append(cur)
            cur = {"lane": m.group(1), "agent": (m.group(2) or "not-yet-dispatched")[:18],
                   "text": m.group(3)}
            continue
        if cur is not None:
            stripped = ln.strip()
            # A continuation is an indented, non-bullet, non-blank line. A blank
            # line or a new bullet at any level ends the entry: a premise must not
            # absorb the prose of the paragraph after the list.
            if stripped and ln.startswith((" ", "\t")) and not stripped.startswith(("-", "*", "#", "|")):
                cur["text"] += " " + stripped
            else:
                rows.append(cur)
                cur = None
    if cur:
        rows.append(cur)
    for r in rows:
        # ⛔ STRUCK TEXT IS SUPERSEDED AND IS NOT A PREMISE.
        #
        # This repo corrects by striking in place and keeping the original as
        # evidence -- "yeah no deletion" governs. So a corrected entry still
        # CONTAINS its old premise, inside ~~...~~, and a parser that reads the
        # whole line re-reads the very claim the correction retired. Both stale
        # entries came back as ALREADY-DONE the moment the entry regex was
        # loosened, which is the correction being un-made by a reader.
        #
        # Kept, not deleted, and not read. That is what striking MEANS.
        live_text = STRIKE_RE.sub(" ", r["text"])
        r["struck"] = live_text != r["text"]
        r["paths"] = [x for x in PATH_RE.findall(live_text) if "/" in x]
        r["claims_uncommitted"] = bool(UNCOMMITTED_RE.search(live_text))
        mv = VERIFY_RE.search(live_text)
        r["verify"] = mv.group(1).strip() if mv else ""
    return rows


def run_verify(repo, cmd):
    """Returns (exit_code, error). Runs the command in the repo, with a timeout.

    NOT shell=True, deliberately. A queue file is a text artifact that several
    parties write to; handing its contents to a shell would turn an edit to a
    markdown list into arbitrary execution. The command is split and run directly,
    so a premise can invoke an instrument and nothing else."""
    import shlex
    try:
        r = subprocess.run(shlex.split(cmd), cwd=repo, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=300)
        return r.returncode, None
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, "%s: %s" % (type(e).__name__, e)


def grade(rows, dirty, repo=None):
    """dirty is the list of paths git reports as changed, or None for UNKNOWN."""
    out = []
    for r in rows:
        # A COMMAND PREMISE takes precedence over a file-state one.
        #
        # Added after THREE consecutive gate-floor firings dispatched nothing while
        # real work existed. The first version could only read premises about FILE
        # STATE ("N files uncommitted under X"), but most remaining work here is
        # defined by A CHECK THAT FAILS -- "9 derivations do not quote their source"
        # is not a fact about uncommitted files and could never be queued. So the
        # queue could only hold work already half-done and left dirty on disk, and a
        # lane whose whole job is to turn a red gate green was inexpressible.
        #
        # The command is the SAME oracle the gate uses, so the queue entry and the
        # gate cannot drift apart -- this file's own defect, applied to its own new
        # feature.
        if r.get("verify"):
            if repo is None:
                out.append((r, "UNKNOWN", "a verify: premise was stated but no repo was "
                                          "given to run it in"))
                continue
            code, err = run_verify(repo, r["verify"])
            if code is None:
                out.append((r, "UNKNOWN", "the verify command could not run (%s); a "
                                          "premise that cannot be checked is not "
                                          "approved" % err))
            elif code == 0:
                out.append((r, "ALREADY-DONE",
                            "`%s` exits 0 -- the check it names now passes, so there is "
                            "nothing left to do" % r["verify"]))
            else:
                out.append((r, "GO", "`%s` exits %d -- the check still fails, so work "
                                     "remains" % (r["verify"], code)))
            continue
        if dirty is None:
            out.append((r, "UNKNOWN", "git could not be read; a premise that cannot be "
                                      "checked is not approved"))
            continue
        if not r["claims_uncommitted"] or not r["paths"]:
            out.append((r, "UNKNOWN", "the entry states no checkable premise about disk "
                                      "(prose is not a precondition)"))
            continue
        hits = [d for d in dirty if any(d.startswith(p) for p in r["paths"])]
        if hits:
            out.append((r, "GO", "%d uncommitted file(s) under %s"
                        % (len(hits), ", ".join(r["paths"]))))
        else:
            out.append((r, "ALREADY-DONE",
                        "the entry says files are UNCOMMITTED under %s and NOTHING is. "
                        "Dispatching buys a confirmation, not work."
                        % ", ".join(r["paths"])))
    return out


def self_check():
    fails = []
    q = ("Some prose that is not a queue entry.\n"
         "   - S-cd-03 `a90789ef603396d52` (7 of ~12 pages already on disk, uncommitted, "
         "in `wiki/sources/infrastructure/` and `wiki/skills-gate/probe-packets/`, "
         "written 13:3x)\n"
         "   - graders `a8097ddfa9546cf25`, `a1f9c2a056d94b3e2`\n")
    q_wrapped = ("   - S-cd-03 `a90789ef603396d52` (7 of ~12 pages already on disk, "
                 "uncommitted, in\n"
                 "     `wiki/sources/infrastructure/` and "
                 "`wiki/skills-gate/probe-packets/`, written 13:3x)\n")
    wr = parse_queue(q_wrapped)
    if not wr or wr[0]["paths"] != ["wiki/sources/infrastructure/",
                                    "wiki/skills-gate/probe-packets/"]:
        fails.append("a WRAPPED queue entry lost the paths on its continuation line -- "
                     "the guard then reports UNKNOWN about the very entry it exists to "
                     "catch: %r" % (wr[0]["paths"] if wr else None,))

    # A FILE premise must be checkable, not just a directory one.
    qf = ("   - UC-0 `ad566f62c03cd8b7e` (`scripts/audit/repair_list_from_ledger.py` on "
          "disk 13:37, uncommitted; it has `--selftest`)\n")
    rf = parse_queue(qf)
    if not rf or rf[0]["paths"] != ["scripts/audit/repair_list_from_ledger.py"]:
        fails.append("a premise naming a single FILE was not checkable, or a bare "
                     "backticked flag was mistaken for a path: %r"
                     % (rf[0]["paths"] if rf else None,))

    rows = parse_queue(q)
    if len(rows) != 2:
        fails.append("queue parsing wrong: %d rows" % len(rows))
    if rows and rows[0]["paths"] != ["wiki/sources/infrastructure/",
                                     "wiki/skills-gate/probe-packets/"]:
        fails.append("paths not extracted: %r" % (rows[0]["paths"],))

    # THE REAL 2026-09-04 FIXTURE: the premise says uncommitted, the tree is clean.
    g = grade([rows[0]], [])
    if g[0][1] != "ALREADY-DONE":
        fails.append("a queue entry claiming UNCOMMITTED files against a CLEAN tree did "
                     "not read ALREADY-DONE -- this is the dispatch that cost a lane")
    # And the positive: dirty files under the path must read GO, or the guard
    # blocks every real lane and gets switched off.
    g2 = grade([rows[0]], ["wiki/sources/infrastructure/x.md"])
    if g2[0][1] != "GO":
        fails.append("real uncommitted work under the stated path did not read GO; the "
                     "guard would block every genuine lane")
    # A path OUTSIDE the entry's scope must not satisfy it.
    g3 = grade([rows[0]], ["scripts/audit/unrelated.py"])
    if g3[0][1] != "ALREADY-DONE":
        fails.append("an unrelated dirty file satisfied the premise; the guard would "
                     "pass on any busy tree")
    # STRUCK text must not be read back as a live premise. This repo corrects by
    # striking in place and keeping the original as evidence, because deletion is
    # forbidden -- so a reader that reads struck text un-makes every correction.
    qs = ("   - S-cd-03 CLOSED-VERIFIED. Struck premise kept as evidence: "
          "~~S-cd-03 `aaaaaa` (pages uncommitted in `wiki/sources/`)~~\n")
    rs = parse_queue(qs)
    if rs and (rs[0]["claims_uncommitted"] or rs[0]["paths"]):
        fails.append("a STRUCK premise was read back as live; every correction made by "
                     "striking in place would be un-made by the next reader")

    # A NEW lane has no agent id yet. Requiring one meant the queue could hold
    # only resumptions, and new work was invisible rather than rejected.
    qn = "   - REDERIVE-EVIDENCE (new work; verify: `python -c exit(3)`)\n"
    rn = parse_queue(qn)
    if len(rn) != 1 or rn[0]["lane"] != "REDERIVE-EVIDENCE":
        fails.append("an entry with NO agent id did not parse; the queue could then "
                     "only express resumptions and new work would be invisible")

    # COMMAND PREMISES, both directions. A new feature with no control is the
    # defect this file exists for, so the exit-0 and exit-nonzero cases are both
    # asserted against real commands rather than mocks.
    qv = ("   - REDERIVE `aaaaaa` (work remains; verify: `python -c exit(3)`)\n"
          "   - DONEV `bbbbbb` (nothing left; verify: `python -c exit(0)`)\n"
          "   - BADV `cccccc` (verify: `definitely-not-a-real-command-here`)\n")
    rv = parse_queue(qv)
    if len(rv) != 3 or not all(r["verify"] for r in rv):
        fails.append("a verify: premise did not parse: %r" % ([r.get("verify") for r in rv],))
    gv = grade(rv, [], os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
    if gv[0][1] != "GO":
        fails.append("a verify command exiting NON-ZERO did not read GO -- a failing "
                     "check means work remains, and this is the only way a lane whose "
                     "job is to turn a red gate green can ever be queued")
    if gv[1][1] != "ALREADY-DONE":
        fails.append("a verify command exiting 0 did not read ALREADY-DONE")
    if gv[2][1] != "UNKNOWN":
        fails.append("an UNRUNNABLE verify command did not read UNKNOWN; 'could not "
                     "check' would render as 'nothing to do'")

    # An entry with no checkable premise is UNKNOWN, never GO.
    g4 = grade([rows[1]], ["wiki/sources/infrastructure/x.md"])
    if g4[0][1] != "UNKNOWN":
        fails.append("an entry with no stated premise read as GO")
    # git unreadable is UNKNOWN, never GO.
    g5 = grade([rows[0]], None)
    if g5[0][1] != "UNKNOWN":
        fails.append("an unreadable git read as something other than UNKNOWN")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wake", default=os.path.join(REPO, "exchange", "WAKE.md"))
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()

    if a.self_check:
        f = self_check()
        if f:
            print("SELF-CHECK: FAIL -- %d" % len(f))
            for x in f:
                print("  " + x)
            return 1
        print("SELF-CHECK: PASS -- 15 assertions incl. the real 2026-09-04 fixture "
              "(premise says UNCOMMITTED, tree is clean), the positive control that "
              "genuine work still reads GO, and the control that an unrelated dirty "
              "file does NOT satisfy a scoped premise, plus command premises in all "
              "three directions (fails=GO, passes=ALREADY-DONE, unrunnable=UNKNOWN)")
        return 0

    try:
        text = open(a.wake, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print("UNKNOWN: cannot read %s (%s) -- this is not 'no queued lanes'"
              % (a.wake, type(e).__name__))
        return 2

    rows = parse_queue(text)
    dirty, err = git_dirty_paths(a.repo)
    graded = grade(rows, dirty, a.repo)

    print("=== LANE PRECONDITION === a queue entry is a CLAIM about disk, and claims expire")
    if err:
        print("  git unreadable: %s" % err)
    print()
    go = stale = 0
    for r, verdict, why in graded:
        if verdict == "GO":
            go += 1
        elif verdict == "ALREADY-DONE":
            stale += 1
        print("  %-13s %-10s %s" % (verdict, r["lane"], why))
    print()
    print("  %d entries: %d GO, %d ALREADY-DONE, %d UNKNOWN"
          % (len(graded), go, stale, len(graded) - go - stale))
    if stale:
        print("  EXIT 3: dispatching an ALREADY-DONE entry does not fail loudly. The lane")
        print("  reads the disk, finds the work done, and returns success -- the only")
        print("  visible trace is the spend. The queue is the coordinator's to correct.")
        return 3
    return 0 if go else 2


if __name__ == "__main__":
    sys.exit(main())
