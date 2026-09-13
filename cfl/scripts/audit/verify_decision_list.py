#!/usr/bin/env python3
"""Run every closure test on a decision list, and REFUSE TO LET IT SHIP IF A ROW IS ALREADY CLOSED.

⛔ PROVENANCE, STATED FIRST BECAUSE IT IS THE HONEST THING
----------------------------------------------------------
Jon ruled that the four coordinators should build this INDEPENDENTLY: "seeing an answer can make
the solution worse." **SSP returned theirs first and CFL read it before writing this. That cost the
independence he was protecting, and this file is therefore NOT an independent second design.**

The CLOSURE TEST idea is SSP's (`personal-ssp-PROTOTYPE-RETURN-…-2026-08-09.md`), including its
best insight, which is theirs and is quoted rather than paraphrased:

    "'is this row still open?' is unanswerable — you cannot search for the absence of an event.
     'What would closure look like, and can I find it?' is answerable, cheap, and mechanical."

And the partition — PROVABLE vs UNPROVABLE, where UNPROVABLE is a first-class answer rather than a
failure — is theirs too. **Do not let this file's existence obscure that.**

⭐ WHAT IS ACTUALLY CFL'S, AND IT IS THE GAP THEIR RETURN LEFT
--------------------------------------------------------------
Their §5 says the tests "can run at every heartbeat." **Nothing makes them.** A test that exists and
is not run is indistinguishable from no test — that is the capture canary (a proxy nobody re-ran),
the suppressed `docker build` (an error channel nobody watched), and the `FILELIST.sha256` check
that pointed at a file no step wrote. **This program's characteristic failure is not missing
mechanisms. It is mechanisms with no trigger.**

So the contribution here is the TRIGGER, and specifically WHERE THE COST FALLS:

    ⭐ THE LIST CANNOT BE PUBLISHED WITHOUT ITS TESTS HAVING RUN, AND A ROW THAT PROVES CLOSED
       BLOCKS THE PUBLISH.

That is the same shape as GATE 1 refusing a dirty tree, and the same shape as Herald's proposed
"publish gates on drain": **the cost of not checking falls on the thing you want to do.** A reminder
is not a mechanism; an incentive is.

FORMAT
------
A row carries its test inline:

    | **A1** | Ratify CONSENT.md | … | `[closure: grep -q "EMPTY SLOT" shelf/continuity/CONSENT.md ; test $? -ne 0]` |

* exit 0  → CLOSED  → ⛔ blocks the publish; the row is stale and must be struck
* exit !0 → OPEN    → fine
* no test → UNPROVABLE → reported, never blocking. ⭐ Per SSP: not a failure of the check, it is the
                         page telling its reader "nobody can verify this cheaply; a human must."

⚠️ AND THE LIMIT SSP NAMED, KEPT: a closure test is a PROXY. Their example — A1's test passes on a
CONSENT.md whose marker was deleted without ratification. **So a test must be named for WHAT IT
CHECKS, never for what it implies.** This script prints the test verbatim next to its verdict so a
reader can see the gap between them.
"""
import argparse, re, subprocess, sys, pathlib

# ⛔ THE CONSOLE, FIXED AT THE ROOT RATHER THAN PER-LITERAL.
# v1 printed check-marks and died with UnicodeEncodeError on the Windows cp1252 console -- AFTER
# computing the tally correctly. A verifier that crashes on the console it runs in is a verifier
# nobody runs, which is this program's characteristic failure; and "the check passed, the PRINT
# died" is the same shape as the yaml validation that looked broken when only its output was.
# v2 tried to replace the offending literals one at a time. ⭐ IT MISSED TWO, AND THE `assert`
# GUARDING IT PASSED ANYWAY because it asserted "something changed", not "everything changed" --
# an assert that accepts partial success is the silent-no-op defect wearing a seatbelt.
# v3 reconfigures the stream once. Whack-a-mole on literals is not a fix.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TEST_RE = re.compile(r"\[closure:\s*(?P<cmd>.+?)\s*\]")
ROW_RE = re.compile(r"^\|\s*(?:\*\*|~~)?(?P<id>[A-Z]-?\d+[a-z]?|C-0[a-d])(?:\*\*|~~)?\s*\|")

# ⛔⛔ THE PROTOTYPE FAILED ITS OWN DECISIVE TEST, AND THE FAILURE IS THE RESULT.
# v1 was run against the two KNOWN-CLOSED rows (D-4, B6) and reported BOTH as OPEN.
# Cause: Windows Python resolves bare `bash` to WSL's bash, which cannot translate this repo's
# Drive path. The test never ran, exited 1 -- and v1 read "non-zero" as OPEN.
#
# ⭐ SO A TEST THAT COULD NOT RUN WAS INDISTINGUISHABLE FROM A ROW THAT IS GENUINELY OPEN.
# That inverts this program's standing rule -- "a gate that could not run is UNKNOWN, never a
# pass" -- which is printed in the operator's own heartbeat instructions and which this file
# violated on its first run. ⛔ And it is WORSE than a false pass: reporting OPEN keeps the row on
# Jon's list, so a broken verifier REPRODUCES the D-4 defect it was built to prevent.
#
# Fix has two parts and both matter: an explicit ERROR state that BLOCKS like CLOSED, and a shell
# that is RESOLVED rather than assumed.
SHELLS = [r"C:\Program Files\Git\bin\bash.exe",
          r"C:\Program Files\Git\usr\bin\bash.exe",
          "bash"]


def _shell():
    for sh in SHELLS:
        if sh == "bash" or pathlib.Path(sh).exists():
            return sh
    return "bash"


def run_test(cmd, repo):
    """Return (rc, err). rc is None when the test COULD NOT RUN -- never conflated with non-zero."""
    try:
        r = subprocess.run([_shell(), "-c", cmd], cwd=repo,
                           capture_output=True, text=True, timeout=60)
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)
    err = (r.stderr or "").strip()
    # A shell that could not even reach the working directory has not tested anything.
    if "Failed to translate" in err or "execvpe" in err:
        return None, err[:200]
    if r.returncode == 127:
        return None, err[:200] or "command not found"
    return r.returncode, err[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--strict", action="store_true",
                    help="exit 5 if any row has NO closure test (adoption gate, off by default)")
    a = ap.parse_args()

    text = pathlib.Path(a.list).read_text(encoding="utf-8")
    closed, open_, unprovable, errored = [], [], [], []

    for line in text.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        rid = m.group("id")
        if line.lstrip().startswith("| ~~"):        # already struck; not a live row
            continue
        t = TEST_RE.search(line)
        if not t:
            unprovable.append(rid)
            continue
        cmd = t.group("cmd")
        rc, err = run_test(cmd, a.repo)
        if rc is None:
            errored.append((rid, cmd, err))
        else:
            (closed if rc == 0 else open_).append((rid, cmd))

    # ASCII-ONLY OUTPUT, deliberately. The first version printed check-marks and died with
    # UnicodeEncodeError on the Windows console -- AFTER computing the tally correctly. A verifier
    # that crashes on the console it runs in is a verifier nobody runs, which is this program's
    # characteristic failure. Same shape as the yaml validation that "failed" when only its print
    # failed. Markers belong in prose; a tool's stdout must survive cp1252.
    print("=== decision-list verification ===")
    print(f"  list: {a.list}")
    for rid, cmd in open_:
        print(f"  [OPEN      ] {rid:<5} test: {cmd[:88]}")
    for rid, cmd, err in errored:
        print(f"  [ERROR     ] {rid:<5} TEST COULD NOT RUN -- this is UNKNOWN, not OPEN: {err[:60]}")
    for rid in unprovable:
        print(f"  [UNPROVABLE] {rid:<5} no closure test — a human must verify this one")
    for rid, cmd in closed:
        print(f"  [CLOSED    ] {rid:<5} test PASSED: {cmd[:80]}")

    print(f"\n  open {len(open_)} · unprovable {len(unprovable)} · CLOSED {len(closed)} | ERROR {len(errored)}")

    # ⛔ AN UNRUNNABLE TEST BLOCKS. This guard was MISSING for three revisions while the ERROR state
    # was already being COMPUTED AND PRINTED -- so the tally said "ERROR 1" and the exit code said
    # "fine". A verdict that disagrees with its own report is worse than no report, and it is the
    # same shape as every other defect this cycle: the surface looked right, the outcome was wrong.
    if errored:
        print("\n[BLOCKED] %d closure test(s) COULD NOT RUN." % len(errored))
        print("   An unrunnable test is UNKNOWN, never OPEN. Calling it OPEN would keep a")
        print("   possibly-closed row on Jon's list -- the exact defect this exists to stop.")
        return 6
    if closed:
        print("\n⛔ PUBLISH BLOCKED — the list carries row(s) that are ALREADY CLOSED.")
        print("   This is the D-4/B6 defect: Jon reading an ask he already answered.")
        print("   Strike them, or correct the test if the test is what is wrong.")
        print("   [warn] A test is a PROXY: read the command above and ask what it actually checks.")
        return 4
    if a.strict and unprovable:
        print(f"\n⛔ STRICT: {len(unprovable)} row(s) carry no closure test.")
        return 5
    print("\n✅ No row proves closed. (This is NOT 'every row is real' — see UNPROVABLE.)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
