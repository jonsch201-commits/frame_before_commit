#!/usr/bin/env python3
"""check_struck_gates.py — does any site still ACT on a gate this project struck?

WHY THIS EXISTS
---------------
On 2026-08-14 the 11,901-byte carrier gate was found still enforcing at FOUR sites, a week
after it had been falsified and after the lesson had been written into SIX CFL documents.
One of those sites was an instruction that DELETED carrier content at every session close.

Striking a gate in prose did not strike the gate. The measured shape of that defect:
"this program's letters channel works; its letters->instruments channel does not exist."

This is the missing instrument, and it is deliberately the smallest one that closes the gap.

WHAT IT DOES NOT DO
-------------------
It does not block. It does not fix. It does not scrub history. Jon has corrected this
project for over-gating six or more times -- a register whose checker blocks work would be
the same defect wearing the uniform of the cure. This REPORTS; a human decides.

THE DISTINCTION IT TURNS ON
---------------------------
An occurrence of a struck gate's marker is INERT if it is:
  - struck-through prose (~~...~~), or on a line that says STRUCK/RETIRED/FALSIFIED,
  - inside the register itself, or a file whose name marks it a correction/record,
  - a historical citation -- CORRECT AS A RECORD OF WHAT WAS BELIEVED, and never to be scrubbed.
Everything else is a candidate ACTING site and is reported for a human to judge.

FAILURE DIRECTION
-----------------
Unreadable file or missing register => UNKNOWN (exit 2), never a pass. A check that could
not run must never render as "there is nothing there."
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTER = os.path.join(REPO, "wiki", "references", "struck-gates.md")
# Scanned roots: where things ACT. wiki/ prose is deliberately NOT scanned -- it is the
# record, and the record is supposed to remember what was once believed.
ROOTS = ["scripts", ".claude", "skills", "docker"]

INERT_LINE = re.compile(
    r"(~~|STRUCK|RETIRED|FALSIFIED|do not reinstate|no replacement|struck-through|"
    r"was struck|now struck|historical|record of what was believed)", re.I)
INERT_FILE = re.compile(r"(CORRECTION|struck-gates|check_struck_gates|RETIRED|INCIDENT)", re.I)

# --- ADDED after the FIRST RUN over-reported 5 of 5 ------------------------------------------
# Every instrument in this repo has over-reported on its first run, each in the direction its own
# docstring warned about. This one was no exception: all five "ACTING" sites were inert, and the
# way that was established was by READING THE LIST, never by re-reading the count.
#
# The three classes it could not see, each verified by hand 2026-08-14:
#   1. A COMMENTED-OUT line. post-compact-wake.sh:110 is the struck line quoted inside its own
#      correction note -- shell-commented, and quoting the old code is exactly how the note works.
#   2. A RETIRED JSON BLOCK. managed-settings.json holds the three PII-zip entries under
#      `_retired_2026_08_11`, whose own text says "They are INERT: this key is not a permissions
#      block." The entries are kept, not deleted, because no-deletion binds records hardest.
#   3. A DATED ONE-SHOT ARTIFACT. RESUME-PROMPT-<id>-2026-08-11.txt was fed to one resume on one
#      day. It is a record of what was sent, not a live policy.
COMMENT_LINE = re.compile(r"^\s*(#|//|/\*|\*)")
# A dated artifact: a filename carrying an ISO date is a record OF that date, not a live rule.
DATED_ARTIFACT = re.compile(r"20\d\d-\d\d-\d\d")
# A JSON/YAML key marked retired or reversed makes everything nested under it inert.
RETIRED_BLOCK_KEY = re.compile(r'"?_(retired|rule_\d+_REVERSED|superseded)', re.I)


def in_retired_block(lines, idx):
    """Walk BACKWARD to the nearest key at a shallower indent. If it is a _retired-class key,
    this line is inside a retired block. Indentation-based, because parsing every format here
    would be a bigger instrument than the defect."""
    cur = len(lines[idx]) - len(lines[idx].lstrip())
    for j in range(idx - 1, max(-1, idx - 400), -1):
        line = lines[j]
        if not line.strip():
            continue
        ind = len(line) - len(line.lstrip())
        if ind < cur:
            if RETIRED_BLOCK_KEY.search(line):
                return True
            cur = ind
            if ind == 0:
                return False
    return False


def load_markers(path):
    """Markers come from the register's own table -- derived, never a second hardcoded list."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("| **SG-"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 6:
                continue
            sg = re.sub(r"\*+", "", cells[0]).strip()
            marker = cells[-1].strip().strip("`")
            if marker:
                rows.append((sg, marker))
    return rows


def main():
    if not os.path.isfile(REGISTER):
        print("UNKNOWN: register absent at wiki/references/struck-gates.md", file=sys.stderr)
        print("  A missing register is not an empty one. Never a pass.", file=sys.stderr)
        return 2

    markers = load_markers(REGISTER)
    if not markers:
        print("UNKNOWN: register parsed to ZERO markers -- the table shape changed.", file=sys.stderr)
        print("  An empty denominator is never a pass.", file=sys.stderr)
        return 2

    scanned = unreadable = 0
    degraded = []
    acting, inert = [], 0

    for root in ROOTS:
        base = os.path.join(REPO, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                rel = os.path.relpath(fp, REPO).replace("\\", "/")
                try:
                    with open(fp, encoding="utf-8", errors="strict") as fh:
                        lines = fh.read().split("\n")
                except UnicodeDecodeError:
                    # NOT UNKNOWN, and the distinction is the point. Every marker in the
                    # register is ASCII, so a replacement-decode still finds it reliably --
                    # the file IS scanned, just degraded. Counting it as unreadable pinned
                    # this check at exit 2 forever on one file's encoding, and an instrument
                    # that can never return clean is a mute button, not an alarm (cf. the
                    # retired RATIO_FLOOR). Reported separately so the encoding stays visible
                    # instead of being swallowed by a pass.
                    with open(fp, encoding="utf-8", errors="replace") as fh:
                        lines = fh.read().split(chr(10))
                    degraded.append(rel)
                except OSError:
                    unreadable += 1          # counted, never silently skipped
                    continue
                scanned += 1
                if INERT_FILE.search(fn):
                    continue
                for n, line in enumerate(lines, 1):
                    for sg, marker in markers:
                        if marker.lower() in line.lower():
                            if (INERT_LINE.search(line)
                                    or COMMENT_LINE.match(line)
                                    or DATED_ARTIFACT.search(fn)
                                    or in_retired_block(lines, n - 1)):
                                inert += 1
                            else:
                                acting.append((sg, rel, n, line.strip()[:110]))

    print("=== check_struck_gates ===")
    print(f"  register      : {len(markers)} struck gate(s) -- {', '.join(s for s, _ in markers)}")
    print(f"  files scanned : {scanned}   roots: {', '.join(ROOTS)}")
    print(f"  unreadable    : {unreadable}" + ("   <-- UNKNOWN, not clean" if unreadable else ""))
    if degraded:
        print(f"  degraded read : {len(degraded)}  -- not valid UTF-8, scanned with replacement.")
        print(f"                  Markers are ASCII so detection holds, but the ENCODING is")
        print(f"                  a real finding on its own: {', '.join(degraded)}")
    print(f"  inert hits    : {inert}   (struck prose / records -- correct, never scrub these)")
    print(f"  ACTING sites  : {len(acting)}")
    if acting:
        print()
        print("  Candidate sites that may still ACT on a struck gate. Judgement is a human's:")
        for sg, rel, n, txt in acting:
            print(f"    {sg}  {rel}:{n}")
            print(f"        {txt}")
        print()
        print("  A site is only a defect if it ACTS. Historical citations are correct as records")
        print("  of what was believed and must NOT be scrubbed.")
    # --- POSITIVE CONTROL, because a checker reporting ZERO must be shown able to report more.
    # A negative result from an instrument never proven to fire is indistinguishable from an
    # instrument that cannot fire. This synthesises one acting site in memory and asserts the
    # classifier calls it ACTING -- no file is written, nothing on disk is touched.
    probe_marker = markers[0][1]
    probe_line = f'if [ "$bytes" -gt {probe_marker} ]; then cut_the_carrier; fi'
    fires = not (INERT_LINE.search(probe_line) or COMMENT_LINE.match(probe_line)
                 or in_retired_block([probe_line], 0))
    print(f"  positive ctrl : {'PASS -- classifier calls a live enforcement line ACTING' if fires else 'FAIL'}")
    if not fires:
        print("    A zero from an instrument that cannot fire is not evidence. Treat as UNKNOWN.",
              file=sys.stderr)
        return 2

    if unreadable:
        return 2
    return 1 if acting else 0


if __name__ == "__main__":
    sys.exit(main())
