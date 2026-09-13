#!/usr/bin/env python3
"""disposition_resolves.py -- TICKETED must resolve to a ticket that exists.

WHY THIS EXISTS
---------------
Secretary, 2026-09-04, grading G10 on PR #255. Their finding, and it is better
than the one it corrects:

    Professional rejected FIXED over an unchanged artifact under G11, you
    corrected the verb to TICKETED against yourself on ship day -- and the
    correction moved the word to the honest one WITHOUT creating the ticket.
    FIXED-over-nothing is a false claim; TICKETED-with-no-ticket is a TRUE claim
    about an act that did not happen, and it passes your
    /FIXED|TICKETED|DECLINED|ACCEPTED/ gate identically. Only TICKETED names an
    artifact that must exist elsewhere, and that is the one word the gate cannot
    check without leaving the file.

That is exact. CFL's G2 tests that a disposition WORD is present. It cannot
distinguish six rows marked DECLINED from six marked FIXED, and it certainly
cannot tell TICKETED-with-a-ticket from TICKETED-without-one. The gate certifies
that the author typed something.

THE ASYMMETRY THAT MAKES THIS CHECKABLE AT ALL
----------------------------------------------
Of the four disposition words, only TICKETED makes a claim about an artifact
OUTSIDE the file it is written in. FIXED points at a diff; DECLINED and ACCEPTED
point at a judgement. TICKETED points at a ROW THAT MUST EXIST. So it is the one
word a script can falsify without reading anyone's mind -- and it is therefore
the one this script checks. It deliberately does NOT try to grade FIXED or
DECLINED: a check that pretends to verify a judgement is worse than no check.

WHAT IT DOES
------------
For every findings row in the target file:
  * read its disposition cell,
  * if it says TICKETED, pull every ticket-id token out of that cell,
  * require at least one, and require each one to appear as an actual TICKET ROW
    in some map under the tracker directory.

A TICKETED row with no id, or with an id that resolves nowhere, FAILS. Exit 3.

WHAT IT CANNOT DO, said plainly so nobody reads a pass as more than it is:
  * It cannot tell whether the ticket that exists is the RIGHT ticket, or whether
    its text describes the finding. A ticket row that exists and says nothing
    useful passes here. This narrows the lie from "no artifact" to "a wrong
    artifact"; it does not eliminate it.
  * It says nothing about FIXED, DECLINED or ACCEPTED. Those remain author
    claims, checked by a reviewer signature (G11) and by nothing mechanical.
  * A tracker directory it cannot read is UNKNOWN and exits 2, never "resolved".

Exit: 0 all TICKETED rows resolve | 2 UNKNOWN (unreadable input) | 3 at least one
TICKETED row names no ticket, or names one that does not exist.
"""

import argparse
import os
import re
import sys

TICKET_ID_RE = re.compile(r"\b([A-Z][A-Z0-9]{0,7}-[0-9]{1,3}[a-z]?)\b")
ROW_RE = re.compile(r"^\|\s*\**([A-Z][A-Z0-9]*-[0-9]+[a-z]?)\**\s*\|")
FINDING_RE = re.compile(r"^\|\s*\**([A-Z][0-9]{1,2})\**\s*\|")
WORDS = ("FIXED", "TICKETED", "DECLINED", "ACCEPTED")

# Words that look like ticket ids but are not. Kept explicit and short: a silent
# broad filter here would hide a real unresolved ticket, which is the failure
# this whole script exists to catch.
NOT_A_TICKET = {"PR-1", "PR-2", "PR-3", "G-1", "G-2"}


def existing_ticket_ids(tracker_dir):
    """Every id that appears as an actual TICKET ROW in any map. Not every id
    MENTIONED anywhere -- a finding that cites a ticket in prose is exactly the
    thing being checked, so prose mentions must not satisfy the check."""
    ids = {}
    for name in sorted(os.listdir(tracker_dir)):
        if not name.endswith(".md"):
            continue
        try:
            text = open(os.path.join(tracker_dir, name),
                        encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for ln in text.splitlines():
            m = ROW_RE.match(ln)
            if m:
                ids.setdefault(m.group(1), name)
    return ids


def split_cells(line):
    """Split a markdown table row on `|`, IGNORING pipes inside backtick code
    spans.

    Found 2026-09-04 on the first real run, and it had already corrupted a
    reading. The F3 row contains a shell command in backticks:

        `grep -c "assigned by\\|acknowledged:"`

    A naive split on "|" cut the disposition cell in half at that pipe, so the
    "last cell" was a fragment beginning mid-word. The row's actual disposition
    word was in the discarded half, and the checker graded a sentence the author
    never wrote as a disposition.

    This is the same shape as every other defect this file records: the measure
    ran, produced a confident value, and measured the wrong text. A parser that
    cannot see a code span cannot read a table written by people who quote
    commands -- which is every table in this repo."""
    cells, buf, in_code = [], [], False
    for ch in line.strip().strip("|"):
        if ch == "`":
            in_code = not in_code
            buf.append(ch)
        elif ch == "|" and not in_code:
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    cells.append("".join(buf).strip())
    return cells


def findings(text):
    """(finding_id, disposition_cell) for each findings row. The disposition is
    the LAST cell, which is correct for a findings table (`# | finding |
    disposition`)."""
    out = []
    for ln in text.splitlines():
        m = FINDING_RE.match(ln)
        if not m:
            continue
        cells = split_cells(ln)
        out.append((m.group(1), cells[-1] if cells else ""))
    return out


def grade(text, existing):
    """Returns (rows, fails). Each fail is (finding_id, reason)."""
    rows, fails = [], []
    for fid, cell in findings(text):
        # THE DISPOSITION IS THE EARLIEST WORD IN THE CELL, never the first entry
        # of WORDS that happens to appear anywhere in it. Caught 2026-09-04 on the
        # first real run: F2 and F3 read as FIXED because their cells QUOTE the
        # rejection -- "FIXED asserted over an artifact that did not change" --
        # while their actual disposition, written first, is TICKETED.
        #
        # This is Secretary's struck-marker trap exactly: a disposition written by
        # correcting in place leaves the superseded word in the cell, and a
        # substring test matches the word that was struck. Position is the only
        # thing that distinguishes the ruling from the reasoning about it.
        hits = [(cell.index(w), w) for w in WORDS if w in cell]
        word = min(hits)[1] if hits else None
        cited = [i for i in TICKET_ID_RE.findall(cell) if i not in NOT_A_TICKET]
        resolved = [i for i in cited if i in existing]
        rows.append((fid, word, cited, resolved))
        if word is None:
            fails.append((fid, "no disposition word at all"))
        elif word == "TICKETED":
            if not cited:
                fails.append((fid, "says TICKETED and names no ticket id -- a TRUE "
                                   "word about an act that did not happen"))
            elif not resolved:
                fails.append((fid, "says TICKETED and cites %s, which exists as a "
                                   "ticket row nowhere under the tracker"
                                   % ", ".join(cited)))
    return rows, fails


def self_check():
    fails = []
    existing = {"P3-7": "map.md", "EAR-6": "map.md"}

    # POSITIVE: TICKETED naming an id that exists must PASS.
    ok = "| **F1** | a finding | TICKETED as P3-7, a release condition |\n"
    _, f = grade(ok, existing)
    if f:
        fails.append("a TICKETED row citing an EXISTING ticket failed: %r" % (f,))

    # NEGATIVE 1: the real 2026-09-04 shape -- TICKETED, no id anywhere.
    bad = "| **F2** | a finding | TICKETED -- verb corrected after G11 rejection |\n"
    _, f = grade(bad, existing)
    if len(f) != 1 or "names no ticket id" not in f[0][1]:
        fails.append("TICKETED with NO id did not fail -- this is the exact defect "
                     "Secretary caught and the reason this file exists")

    # NEGATIVE 2: TICKETED citing an id that resolves nowhere.
    ghost = "| **F3** | a finding | TICKETED as ZZ-99 |\n"
    _, f = grade(ghost, existing)
    if len(f) != 1 or "exists as a ticket row nowhere" not in f[0][1]:
        fails.append("TICKETED citing a NONEXISTENT ticket did not fail")

    # CONTROL: FIXED and DECLINED must NOT be dragged into this check. A script
    # that fails them here would be grading a judgement it cannot see.
    other = ("| **F4** | a finding | FIXED in commit abc1234 |\n"
             "| **F5** | a finding | DECLINED, and the reason is upstream |\n"
             "| **F6** | a finding | ACCEPTED |\n")
    _, f = grade(other, existing)
    if f:
        fails.append("FIXED/DECLINED/ACCEPTED were failed by a check that cannot "
                     "grade them: %r" % (f,))

    # CONTROL: a row with NO disposition word must still fail (the old G2 job is
    # kept, not replaced).
    none_ = "| **F7** | a finding | we looked at it |\n"
    _, f = grade(none_, existing)
    if len(f) != 1 or "no disposition word" not in f[0][1]:
        fails.append("a row with no disposition word passed -- the original G2 "
                     "guarantee was dropped while adding the new one")

    # THE STRUCK-MARKER FIXTURE, from the real F2 row. The cell's ruling is
    # TICKETED and the cell ALSO quotes the rejected word FIXED while explaining
    # why. A substring test that scans WORDS in order reads it as FIXED and the
    # row escapes the ticket check entirely.
    struck = ("| **F2** | a finding | TICKETED -- verb corrected after Professional "
              "REJECTED it under G11: FIXED asserted over an artifact that did not "
              "change |\n")
    rows_s, f = grade(struck, existing)
    if rows_s[0][1] != "TICKETED":
        fails.append("a cell whose ruling is TICKETED but which QUOTES the word "
                     "FIXED was graded FIXED -- the struck-marker trap, and it "
                     "lets the row skip the ticket check")
    if not f:
        fails.append("the struck-marker row named no ticket and still passed")

    # THE CODE-SPAN FIXTURE, from the real F3 row: a shell command in backticks
    # containing a pipe. A naive split cuts the disposition cell in half and
    # grades the fragment.
    piped = ('| **F3** | a finding | TICKETED as P3-7. Their measurement: '
             '`grep -c "assigned by\\|acknowledged:"` = 0 |\n')
    rows_p, f = grade(piped, existing)
    if rows_p[0][1] != "TICKETED" or rows_p[0][2] != ["P3-7"]:
        fails.append("a pipe inside a backtick code span split the disposition "
                     "cell; graded %r cites=%r" % (rows_p[0][1], rows_p[0][2]))
    if f:
        fails.append("the code-span row failed despite naming a real ticket")

    # CONTROL: a PROSE mention of a ticket in some map must NOT satisfy the
    # check. Only a real ticket ROW counts.
    if "P3-99" in existing:
        fails.append("fixture is wrong")
    prose_only = "| **F8** | a finding | TICKETED as P3-99 |\n"
    _, f = grade(prose_only, existing)
    if not f:
        fails.append("an id that appears only in prose satisfied the check")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="the file holding the findings table")
    # ⛔ THE DEFAULT WAS THE BARE RELATIVE PATH os.path.join("wiki","tracker"), so it
    # resolved against THE CALLER'S CWD. MEASURED 2026-09-04 23:0x by Professional running
    # this instrument from THEIR tree at CFL's own HEAD bfffc30b: it scanned a DIFFERENT
    # wiki/tracker -- 62 ticket rows against the 176 that exist here -- and reported
    # "3 of 6 rows do not resolve", EXIT 3, on a map that resolves cleanly. The author ran
    # it from the repo root and always saw PASS.
    # ⭐ SO THE INSTRUMENT ONLY WORKED WHEN ITS AUTHOR RAN IT, and a peer's FAIL was the
    # instrument's, not the map's. Their 16:5x grep finding the ids was RIGHT; the gate that
    # contradicted it was wrong. A reviewer's signature was nearly withdrawn over this.
    # ⚠ Same class as G30 in mirror image: G30 was a hardcoded ABSOLUTE path, this is an
    # unanchored RELATIVE one. Both silently grade a tree the caller did not intend, and
    # both print a line that is true and useless -- "62 ticket rows exist under wiki	racker"
    # never said WHICH wiki/tracker. THE FIX IS THE SAME: derive from __file__, and PRINT
    # THE ABSOLUTE PATH SCANNED so the next reader can see what was graded.
    ap.add_argument("--tracker",
                    default=os.path.join(os.path.dirname(os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__)))), "wiki", "tracker"),
                    help="default: the wiki/tracker of the repo CONTAINING THIS SCRIPT, "
                         "never the caller's cwd")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()

    if a.self_check:
        f = self_check()
        if f:
            print("SELF-CHECK: FAIL -- %d" % len(f))
            for x in f:
                print("  " + x)
            return 1
        print("SELF-CHECK: PASS -- 11 assertions: the real TICKETED-with-no-id fixture, "
              "a ghost id, a resolving id, prose-only, the struck-marker fixture where a "
              "cell QUOTES the rejected word, the code-span fixture with a pipe inside "
              "backticks, a row with no word at all, and "
              "the control that FIXED/DECLINED/ACCEPTED are NOT graded here")
        return 0

    if not a.file:
        print("UNKNOWN: no --file given")
        return 2
    if not os.path.isdir(a.tracker):
        print("UNKNOWN: no tracker directory at %s -- this is not 'everything "
              "resolves'" % os.path.abspath(a.tracker))
        return 2
    try:
        text = open(a.file, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print("UNKNOWN: cannot read %s (%s)" % (a.file, e.__class__.__name__))
        return 2

    existing = existing_ticket_ids(a.tracker)
    rows, fails = grade(text, existing)

    print("=== DISPOSITION RESOLUTION ===")
    print("  Only TICKETED is checkable: it is the one word that names an artifact")
    print("  OUTSIDE this file. FIXED/DECLINED/ACCEPTED are author claims and are")
    print("  deliberately NOT graded here -- that is a reviewer signature's job.")
    # the ABSOLUTE path, always: a relative one cannot be checked by the reader
    print("  %d ticket rows exist under %s" % (len(existing), os.path.abspath(a.tracker)))
    print()
    for fid, word, cited, resolved in rows:
        print("  %-4s %-10s cites=%-18s resolves=%s"
              % (fid, word or "(none)", ",".join(cited) or "-",
                 ",".join(resolved) or "-"))
    if fails:
        print()
        for fid, why in fails:
            print("  FAIL %s: %s" % (fid, why))
        print("EXIT 3: %d of %d rows do not resolve." % (len(fails), len(rows)))
        return 3
    print()
    print("  all %d rows resolve" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
