#!/usr/bin/env python3
"""alignment_map.py -- the map of the maps, DERIVED from the maps themselves.

WHY THIS EXISTS
---------------
Jon, 2026-09-04, verbatim (typos his):

    I don't feel like I have a proper map of how they branch into the branches
    and sub-branches of all your projects

and, the same day:

    I have no surface to materially reviedw your progress i feel.

He is describing a measured condition, not an impression. `[m 2026-09-04: 20
kind: wayfinder:map files under wiki/tracker/; 14 declare status LIVE; one
declares no status at all. There is no index of them anywhere in the repo.]`

CFL's cold-open rule already says: derive the LIVE set, enumerate them ALL, and
resume on the one whose scope matches the directive. It never said what the
scopes ARE or how they relate. So a session can obey that rule perfectly, print
fourteen filenames, and still leave Jon with no shape -- which is what happened.

THE THING THIS DELIBERATELY DOES NOT DO
---------------------------------------
It does NOT hold a filename -> branch lookup table. Such a table is the defect
[[derive-dont-record]] names: typed once, right on the day it is written, and
silently rotting as maps are chartered and closed. It would also put one
session's opinion of another map's scope above that map's own.

Instead every map DECLARES its own branch in frontmatter (`branch:`), and this
script reports an undeclared map as UNKNOWN and EXITS 3. The alignment is
enforced at the maps, not asserted here.

THE FOUR BRANCHES, and why there are four
-----------------------------------------
CFL's job is to make Jon's judgement cheap -- not to be right, to be CHECKABLE.
His own sentence is the acceptance test (~/.claude/history.jsonl:2611, his typed
prompt, typos his):

    Look I can always decide 'nah i don't like that interpreatation' - if i can
    actually see the shape.

Each branch is worthless without the one before it, which is why they are
ordered and not a set:

  capture -- is the input still alive at all?
  trace   -- does a claim reach a primary?
  check   -- can a second party falsify it?
  see     -- can Jon evaluate it in the time he actually has?

A fifth value, `unaligned`, is legal and load-bearing: a map whose author judges
it serves none of the four says so out loud. That is a finding about the map,
not a gap in this list, and it is NOT the same as an undeclared map (UNKNOWN).

EXIT: 0 every LIVE map declares a known branch | 3 at least one does not |
2 the tracker directory could not be read.
"""

import argparse
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ticket_rows import merged as parse_tickets  # noqa: E402
import sys

BRANCHES = ["capture", "trace", "check", "see", "unaligned"]
BRANCH_GLOSS = {
    "capture": "is the input still alive at all?",
    "trace": "does a claim reach a primary?",
    "check": "can a second party falsify it?",
    # WIDENED 2026-09-04 on Secretary's boundary question, ruled by CFL as the
    # taxonomy's owner. It read "can JON evaluate it in the time he has."
    #
    # Their case: their pre-trace map serves a reader with NO WORKING MEMORY --
    # Jon after an interruption, a peer, a subagent, a seat across a compact.
    # Three of those four are not Jon and face the IDENTICAL constraint.
    #
    # RULED: widen the gloss, do NOT add a sixth branch. The four branches split
    # on the PROPERTY being served, never on the identity of the reader; a sixth
    # branch would split on identity and break the cut. The constraint is the same
    # (no working memory) and so is the remedy (legibility), so it is one branch.
    #
    # Jon stays named FIRST because the alignment's whole anchor is making HIS
    # judgement cheap, and a gloss that forgets that drifts into "this helps
    # somebody read it", which is every artifact ever written.
    "see": "can an evaluator with no working memory -- Jon first among them, but "
           "also a peer, a subagent, or a seat across a compact -- evaluate it in "
           "the time they have?",
    # NOT A PROPERTY. An ACT. See DERIVABLE below.
    "unaligned": "author states it serves none of the four",
}

# ⛔ THE FIFTH VALUE IS NOT DERIVABLE BY ANYONE BUT THE AUTHOR, EVER.
#
# Secretary opened this file's own gloss table and found the boundary already
# drawn in it, 2026-09-04: four values are PROPERTIES OF THE DESTINATION and can
# be read off the artifact. The fifth is glossed "author STATES it serves none of
# the four" -- an act of will, not a property. Nothing in a map's text can
# establish that its author judged it unaligned.
#
# ⚠ And it is exactly the value a tidy sweep reaches for, because it makes every
# awkward map fit. So a map that fits none of the four is recorded
# UNKNOWN-MAY-BE-UNALIGNED. Only its author may collapse that to `unaligned`.
DERIVABLE = ["capture", "trace", "check", "see"]

FM_RE = re.compile(r"^---\s*$")
# Ticket rows look like:  | **EAR-6** | task (AFK, CFL) | ... | OPEN -- ... |
ROW_RE = re.compile(r"^\|\s*\**([A-Z][A-Z0-9]*-[0-9]+[a-z]?)\**\s*\|")
# A status cell counts as CLOSED only on an explicit closure word. Anything
# else -- INCLUDING AN EMPTY CELL -- is OPEN. An unreadable status is never a
# closure: that is "UNKNOWN dominates a PASS" applied to a ticket table.
CLOSED_RE = re.compile(
    r"\b(CLOSED|DONE|RESOLVED|LANDED|MERGED|WITHDRAWN|SUPERSEDED)\b")


def frontmatter(text):
    lines = text.splitlines()
    if not lines or not FM_RE.match(lines[0]):
        return {}
    out = {}
    for ln in lines[1:]:
        if FM_RE.match(ln):
            break
        if ":" in ln:
            k, v = ln.split(":", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            # An inline `# ...` comment is stripped from ENUM fields only.
            #
            # Caught 2026-09-04 on the first real declarations: each was written as
            #     branch: capture  # its destination is that after a compact ...
            # because the RATIONALE belongs next to the judgement, not in a commit
            # message nobody re-reads. The parser took the whole tail as the value,
            # so three correctly-declared maps still reported UNDECLARED.
            #
            # Deliberately NOT applied to free-text fields: `status:` and `owner:`
            # here routinely contain '#' inside real prose, and stripping there would
            # silently truncate a status. A rule that is right for an enum and wrong
            # for prose has to know which it is looking at.
            if k in ("branch", "kind") and "#" in v:
                v = v.split("#", 1)[0].strip()
            out[k] = v
    return out


STATUS_HDR_RE = re.compile(r"^(status|state|disposition|verdict)\b", re.IGNORECASE)


def _cells(ln):
    return [c.strip() for c in ln.strip().strip("|").split("|")]


def tickets(text):
    """Returns (open_ids, closed_count, schema). Order preserved, so open_ids[0]
    is the first unclosed ticket -- what the cold-open rule tells a session to
    resume at.

    THE STATUS COLUMN IS FOUND BY ITS HEADER, NEVER BY POSITION. The first
    version of this function read the LAST cell of every row. Secretary caught
    it within the hour of shipping (2026-09-04): wayfinder-pr3-2026-08-31.md
    uses `id | question | type | blocked-by | due`, so its last cell is a DATE.
    Every ticket in that map read OPEN, including the closed ones.

    That is this week's dominant defect wearing a third costume. The failure was
    SAFE in direction -- over-reporting open work never hides progress -- and it
    was still a number that could not be wrong in the other direction, which is
    what makes it worthless as a measure.

    A table with no status-like header returns schema="UNKNOWN" and NO counts.
    It does not fall back to the last column and it does not report zero: a
    schema this function cannot read is a thing it did not measure."""
    open_ids, closed = [], 0
    rows, unreadable = 0, 0
    idx = None          # the status column of the table CURRENTLY being read

    for ln in text.splitlines():
        c = _cells(ln)
        m = ROW_RE.match(ln)

        # EACH ROW IS READ AGAINST ITS OWN TABLE'S HEADER, not against the first
        # status-like header in the file. Second catch of the same afternoon:
        # wayfinder-pr3-2026-08-31.md opens with a FINDINGS table headed
        # `# | finding | disposition`, and a whole-file header search bound the
        # ticket rows further down to column 2 -- which in the ticket table is
        # `type`. The count was then derived from the wrong column of the wrong
        # table and still printed a confident number.
        #
        # A header row is any table row that is NOT a ticket row and carries a
        # status-like cell; it rebinds idx for everything below it until the next
        # header. A blank line or non-table line ends the table and clears the
        # binding, so rows in an unheaded table are never read against a header
        # that belongs to a different one.
        if not m and len(c) >= 2 and any(STATUS_HDR_RE.match(x) for x in c):
            idx = next(i for i, h in enumerate(c) if STATUS_HDR_RE.match(h))
            continue
        if not ln.strip().startswith("|"):
            idx = None
            continue
        if not m:
            continue

        rows += 1
        if idx is None:
            unreadable += 1
            continue
        status = c[idx] if idx < len(c) else ""
        if CLOSED_RE.search(status):
            closed += 1
        else:
            open_ids.append(m.group(1))

    # MI-13, 2026-09-06: tables are read above with their header-bound schema semantics; the
    # BULLET and HEADING conventions of the 09-05 maps are read by the shared matcher
    # (scripts/audit/ticket_rows.py) and unioned here. [measured 06:5x] this function returned
    # open=0 closed=0 [NO-TICKETS] for a map carrying 18 tickets in those two shapes.
    for r in parse_tickets(text):
        if r.form == "table":
            continue
        rows += 1
        if r.closed:
            closed += 1
        else:
            open_ids.append(r.id)
    if rows == 0:
        return [], 0, "NO-TICKETS"
    if unreadable == rows:
        return [], 0, "UNKNOWN-SCHEMA"
    if unreadable:
        # PARTIAL is reported, never silently folded into the counts. A map with
        # some readable and some unreadable tables must not print as if measured
        # whole -- that is the population defect in miniature.
        return open_ids, closed, "PARTIAL-%d-UNREAD" % unreadable
    return open_ids, closed, "OK"


def quotes_source(tracker_dir, m, span=60):
    """True when the derived-evidence contains at least `span` consecutive
    characters that appear VERBATIM in the map it describes.

    Whitespace is collapsed on both sides first, for the same reason as everywhere
    else today: a quote wrapped across lines is the same words, and three separate
    matchers have already been defeated by a line break.

    span=60 is a judgement and is stated as one: short enough that a single real
    clause clears it, long enough that an incidental phrase ("the wiki", "every
    trunk") cannot. It is not a proof that the evidence is SUFFICIENT -- nothing
    mechanical can be -- only that the deriver read the artifact rather than
    summarising their impression of it."""
    src = os.path.join(tracker_dir, m["file"])
    try:
        raw = open(src, encoding="utf-8", errors="replace").read()
    except OSError:
        return False           # unreadable source is NOT a pass
    # ⛔ THE FRONTMATTER IS EXCLUDED, and the first version forgot to: the evidence
    # field LIVES in the frontmatter, so every derivation trivially quoted itself
    # and the check passed all nine on its first run. A check whose subject is
    # inside its own corpus cannot fail -- the same shape as a freshness gate going
    # green on a file its own author deposited, which Secretary hit today, and as a
    # census counting its own output, which CFL hit this week.
    lines = raw.splitlines()
    if lines and FM_RE.match(lines[0]):
        for i, ln in enumerate(lines[1:], 1):
            if FM_RE.match(ln):
                lines = lines[i + 1:]
                break
    text = " ".join(" ".join(lines).split())
    ev = " ".join(m["evidence"].split())
    if len(ev) < span:
        return False
    for i in range(len(ev) - span + 1):
        if ev[i:i + span] in text:
            return True
    return False


def classify_status(status_raw):
    """A status field whose value STARTS WITH LIVE is LIVE however much prose
    follows it -- the real maps all carry trailing prose, and a naive equality
    test calls every one of them OTHER. A MISSING status field is UNKNOWN:
    never dead, never live."""
    if not status_raw:
        return "UNKNOWN"
    up = status_raw.upper()
    if up.startswith("LIVE"):
        return "LIVE"
    if "SUPERSEDED" in up or "MERGED-INTO" in up:
        return "SUPERSEDED"
    return "OTHER"


def scan(tracker_dir):
    maps = []
    for name in sorted(os.listdir(tracker_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(tracker_dir, name)
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        fm = frontmatter(text)
        if fm.get("kind") != "wayfinder:map":
            continue
        op, cl, schema = tickets(text)
        # ⛔ A DERIVED VALUE NEVER OCCUPIES THE DECLARED FIELD. Secretary's hard
        # constraint, 2026-09-04: "Merge them and the gate goes green on peer
        # readings while reporting owner commitments -- the wrapper-for-contents
        # family, introduced by the act of closing the gate."
        #
        # `branch:`         an act of will by the map's AUTHOR. Commits somebody.
        # `branch-derived:` a READING of the map's own text by a third party,
        #                   checkable against it, committing nobody.
        # They are different claims and they get different fields, so a reader can
        # always tell which one a green gate was built from.
        maps.append({
            "schema": schema,
            "file": name,
            "live": classify_status(fm.get("status", "")),
            "owner": fm.get("owner", "UNDECLARED"),
            "branch": fm.get("branch", ""),
            "derived": fm.get("branch-derived", ""),
            "derived_by": fm.get("derived-by", ""),
            "evidence": fm.get("derived-evidence", ""),
            "open": op, "closed": cl, "date": fm.get("date", ""),
        })
    return maps


def self_check():
    fails = []
    fm = frontmatter("---\nkind: wayfinder:map\nstatus: LIVE\nbranch: check\n---\nbody\n")
    if fm.get("branch") != "check":
        fails.append("frontmatter did not parse a branch")
    # An inline rationale comment on an ENUM field must not become the value.
    fm2 = frontmatter("---\nkind: wayfinder:map\nbranch: capture  # because X\n"
                      "status: LIVE -- see #14 for why\n---\n")
    if fm2.get("branch") != "capture":
        fails.append("an inline # rationale on branch: was swallowed into the value; "
                     "three correctly-declared maps read UNDECLARED because of this")
    if "#14" not in fm2.get("status", ""):
        fails.append("a '#' inside a free-text status was truncated -- comment "
                     "stripping must apply to ENUM fields only, or a real status is lost")
    if frontmatter("no frontmatter here"):
        fails.append("a file with no frontmatter returned fields")
    if classify_status('LIVE - chartered 2026-08-31') != "LIVE":
        fails.append("a LIVE status with trailing prose did not read as LIVE")
    if classify_status("") != "UNKNOWN":
        fails.append("a MISSING status read as something other than UNKNOWN")
    if classify_status("SUPERSEDED -- 2026-08-24") != "SUPERSEDED":
        fails.append("a superseded map did not read SUPERSEDED")
    body = ("| id | type | text | status |\n|---|---|---|---|\n"
            "| **AA-1** | task | text | CLOSED |\n"
            "| **AA-2** | task | text | OPEN -- next |\n"
            "| **AA-3** | task | text |  |\n"
            "not a row\n")
    op, cl, schema = tickets(body)
    if schema != "OK":
        fails.append("a table WITH a status header did not parse: %s" % schema)
    if cl != 1:
        fails.append("closed count wrong: %d" % cl)
    if op != ["AA-2", "AA-3"]:
        fails.append("open ids wrong: %r -- an EMPTY status cell must read OPEN, "
                     "never closed" % (op,))
    op2, _, _ = tickets("| id | type | t | status |\n|---|---|---|---|\n"
                        "| **BB-1** | task | t | CLOSED |\n")
    if op2:
        fails.append("a fully closed map reported an open ticket")

    # THE 2026-09-04 FIXTURE, taken from the real map Secretary caught. The last
    # cell is a DATE, not a status. It must report UNKNOWN-SCHEMA and NO counts:
    # never fall back to the last column, and never report zero as if measured.
    pr3 = ("| id | question | type | blocked-by | due |\n|---|---|---|---|---|\n"
           "| **P3-1** | q | grilling | - | 2026-09-04 |\n"
           "| **P3-7** | q | task | P3-1 | 2026-09-04 |\n")
    op3, cl3, schema3 = tickets(pr3)
    if schema3 != "UNKNOWN-SCHEMA":
        fails.append("a table whose last column is a DATE was parsed as if that "
                     "column were a status -- the exact defect the header lookup "
                     "exists to prevent")
    if op3 or cl3:
        fails.append("an unreadable schema produced counts; it must produce none")

    # CONTROL: a map with NO ticket rows is NO-TICKETS, which is distinct from a
    # map whose rows could not be read. Collapsing the two would make an empty
    # map and an unparseable map print identically.
    if tickets("just prose, no tables\n")[2] != "NO-TICKETS":
        fails.append("a map with no ticket rows did not read NO-TICKETS")

    # THE TWO-TABLE FIXTURE, also from the real 2026-09-04 map. A FINDINGS table
    # headed `disposition` sits ABOVE the ticket table. A whole-file header
    # search bound the ticket rows to the findings table's column and produced a
    # confident number from the wrong column of the wrong table.
    two = ("| # | finding | disposition |\n|---|---|---|\n"
           "| **F1** | a finding | TICKETED |\n"
           "\n"
           "| id | question | type | blocked-by | due |\n|---|---|---|---|---|\n"
           "| **P3-1** | q | grilling | - | 2026-09-04 |\n")
    op4, cl4, schema4 = tickets(two)
    if schema4 != "UNKNOWN-SCHEMA":
        fails.append("ticket rows under an UNHEADED table were read against a "
                     "DIFFERENT table's header -- schema=%s, open=%r" % (schema4, op4))
    if op4 or cl4:
        fails.append("the two-table fixture produced counts from the wrong table")

    # And its inverse: when the ticket table DOES carry its own status header,
    # a findings table above it must not disturb the reading.
    two_ok = ("| # | finding | disposition |\n|---|---|---|\n"
              "| **F1** | a finding | TICKETED |\n"
              "\n"
              "| id | type | text | status |\n|---|---|---|---|\n"
              "| **P3-1** | task | t | CLOSED |\n"
              "| **P3-2** | task | t | OPEN |\n")
    op5, cl5, schema5 = tickets(two_ok)
    if schema5 != "OK" or op5 != ["P3-2"] or cl5 != 1:
        fails.append("a correctly-headed ticket table below a findings table did "
                     "not parse: schema=%s open=%r closed=%d" % (schema5, op5, cl5))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracker", default=os.path.join("wiki", "tracker"))
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()

    if a.self_check:
        f = self_check()
        if f:
            print("SELF-CHECK: FAIL -- %d" % len(f))
            for x in f:
                print("  " + x)
            return 1
        print("SELF-CHECK: PASS -- 18 assertions, both directions, incl. the controls "
              "that an EMPTY ticket status reads OPEN, a MISSING status reads UNKNOWN, "
              "a fully-closed map fabricates no next ticket, and the real 2026-09-04 "
              "date-in-the-last-column and two-table fixtures report UNKNOWN-SCHEMA "
              "rather than guessing, in both directions")
        return 0

    if not os.path.isdir(a.tracker):
        print("UNKNOWN: no tracker directory at %s -- this is not 'no maps'" % a.tracker)
        return 2

    maps = scan(a.tracker)
    live = [m for m in maps if m["live"] == "LIVE"]
    unknown_status = [m for m in maps if m["live"] == "UNKNOWN"]

    print("=== ALIGNMENT: CFL's job is to make Jon's judgement CHEAP -- not to be "
          "right, to be CHECKABLE. ===")
    print("    His test: I can always decide 'nah i don't like that interpreatation'")
    print("    - if i can actually see the shape.")
    print()
    print("%d wayfinder maps | %d LIVE | %d declare NO status (UNKNOWN, not dead)"
          % (len(maps), len(live), len(unknown_status)))
    print()

    # ⛔ G14's PASS CONDITION WAS ASKING FOR THE WRONG THING, and Secretary named it
    # 2026-09-04: "every LIVE map DECLARES" is unsatisfiable by anyone but 16 absent
    # authors, so THE ONLY WAY TO CLOSE IT IS TO IMPERSONATE THEM. A gate whose only
    # reachable green requires speaking for other people is not a strict gate; it is
    # a gate that teaches you to forge.
    #
    # Replaced with: every LIVE map carries a branch value WITH ITS PROVENANCE
    # VISIBLE. `neither: 0` is the pass. Declared and derived both count -- and are
    # never merged, so a reader always knows which kind of claim closed it.
    def bucket(m):
        if m["branch"] in BRANCHES:
            return "declared"
        if m["derived"] in DERIVABLE:
            return "derived"
        if m["derived"] == "unaligned":
            # ⛔ NOT REACHABLE BY DERIVATION. Recorded as a refusal, not a value.
            return "illegal-derived-unaligned"
        if m["derived"] == "unknown-may-be-unaligned":
            # TWO CAUSES, SPLIT. Secretary, 2026-09-04 18:3x: "your
            # unknown-may-be-unaligned bucket is currently carrying two causes for
            # four maps (two fit no property, two had nothing measured)."
            #
            # They are different findings and only one of them is about the map:
            #   NO-PROPERTY  the Destination was read and states a deliverable or a
            #                date, not a property of the four. A fact about the map.
            #   NOT-MEASURED no readable Destination section exists at all. A fact
            #                about CFL's reading, and a thing CFL can fix alone.
            # Collapsing them lets an unread map hide inside a bucket of genuinely
            # unclassifiable ones -- the same shape as UNKNOWN(not asked) hiding
            # inside UNKNOWN(asked), which this file already split once today.
            ev = m["evidence"].lower()
            if "nothing was measured" in ev or "no '## destination'" in ev:
                return "unknown-not-measured"
            return "unknown-no-property"
        return "neither"

    buckets = {}
    for m in live:
        buckets.setdefault(bucket(m), []).append(m)

    for b in BRANCHES:
        rows = [m for m in live if m["branch"] == b or
                (m["derived"] == b and b in DERIVABLE)]
        if not rows:
            continue
        print("-- %s: %s" % (b.upper(), BRANCH_GLOSS[b]))
        for m in sorted(rows, key=lambda r: r["date"], reverse=True):
            first = m["open"][0] if m["open"] else "(none open)"
            # The full derived-by prose lives in the FILE, where a rejector reads it.
            # Printing it whole here buries the table it annotates -- and a table
            # nobody can scan is the `see` branch failing inside the tool that
            # measures `see`.
            if m["branch"] in BRANCHES:
                prov = "declared by %s" % ((m["owner"] or "?")[:40])
            else:
                who = (m["derived_by"] or "UNRECORDED").split(",")[0]
                prov = "DERIVED by %s -- rejections wanted" % who
            print("   %-52s open=%2d closed=%2d next=%-9s [%s]"
                  % (m["file"][:52], len(m["open"]), m["closed"], first, m["schema"]))
            print("     %s" % prov)
        print()

    # TRUNCATED EVIDENCE, added 2026-09-04 18:1x. soul (Claude Personal) ran the
    # G19 rejection pass and returned 1 of 3 rejected -- but the pattern across all
    # three was worth more than the score:
    #
    #   "in every case the deciding line was in the part of the Destination your own
    #    excerpt cut off ... what it caught was not a taxonomy error, it was a
    #    READING error, and your process generated the excerpts it then reasoned
    #    from."
    #
    # The one rejection turned on a clause that began exactly where CFL's excerpt
    # stopped -- at a colon. So the check is theirs, stated in their words: "if a
    # derivation's evidence field can't hold the sentence that justifies it, the
    # derivation isn't checkable by the next reader either."
    #
    # An ellipsis is the visible signature of a fragment. This does not prove the
    # evidence is sufficient -- nothing mechanical can -- it only refuses the one
    # shape that is provably a cut-off, and says so.
    # ⛔ THE FIRST VERSION OF THIS CHECK WAS TOO WEAK AND PASSED EVERYTHING.
    # It looked for an ellipsis or a short field. All nine derivations were long
    # and ellipsis-free -- and every one of them was still CFL's PARAPHRASE of the
    # map rather than the map's own words. A check that cannot fail on the very
    # artifacts that provoked it is the defect this whole day is about, so it was
    # replaced within minutes of being written.
    #
    # The strong form is mechanical: does the evidence QUOTE the artifact? A
    # derivation that cites the map verbatim can be checked against the map by
    # anyone. A paraphrase can only be checked against the deriver's judgement,
    # which is the thing under review.
    thin = [m for m in live if m["derived"] in DERIVABLE
            and not quotes_source(a.tracker, m)]
    if thin:
        print("-- EVIDENCE DOES NOT QUOTE THE SOURCE: paraphrase, not citation.")
        print("   soul, 2026-09-04, after rejecting one of three: the deciding line was")
        print("   inside the truncation in all three cases, and the process generated the")
        print("   excerpts it then reasoned from. These derivations PARAPHRASE the map")
        print("   rather than quoting it, so they can only be checked against CFL's")
        print("   judgement -- which is the thing under review. Quote 60+ characters of")
        print("   the map's own text, verbatim, or withdraw the derivation.")
        for m in thin:
            print("   %-52s evidence=%d chars, quotes source: NO"
                  % (m["file"][:52], len(m["evidence"])))
        print()

    unk = (buckets.get("unknown-no-property", [])
           + buckets.get("unknown-not-measured", []))
    if unk:
        print("-- UNKNOWN-MAY-BE-UNALIGNED: fits none of the four on its own text.")
        print("   ONLY THE AUTHOR MAY COLLAPSE THIS TO `unaligned`. That value is an")
        print("   ACT, not a property -- nothing in a map's text can establish that its")
        print("   author judged it aligned with nothing. It is also the value a tidy")
        print("   sweep reaches for, because it makes every awkward map fit.")
        for m in buckets.get("unknown-no-property", []):
            print("   NO-PROPERTY  %-42s owner=%s" % (m["file"][:42], m["owner"][:28]))
        for m in buckets.get("unknown-not-measured", []):
            print("   NOT-MEASURED %-42s owner=%s" % (m["file"][:42], m["owner"][:28]))
        if buckets.get("unknown-not-measured"):
            print("   NOT-MEASURED is CFL's to fix alone -- no readable Destination was")
            print("   found, so nothing about the map has been established either way.")
        if buckets.get("unknown-no-property"):
            print("   NO-PROPERTY: Secretary's open question, offered not ruled -- a PR map")
            print("   declares what it SHIPS while the four branches classify what a map")
            print("   SERVES, so the fix may be `kind: wayfinder:delivery` rather than a")
            print("   sixth branch. NOT adopted here; it is their hypothesis, not a ruling.")
        print()

    illegal = buckets.get("illegal-derived-unaligned", [])
    for m in illegal:
        print("  ILLEGAL: %s carries `branch-derived: unaligned`. The fifth value is"
              % m["file"])
        print("     not derivable by anyone but the author. Use")
        print("     `branch-derived: unknown-may-be-unaligned`.")

    neither = buckets.get("neither", [])
    if neither:
        print("-- NEITHER: no branch value at all, declared or derived.")
        n_unowned = sum(1 for m in neither if m["owner"] == "UNDECLARED")
        print("   %d of %d carry `owner: UNDECLARED`. An unowned LIVE map has no name"
              % (n_unowned, len(neither)))
        print("   attached to its expiry, so every on-silence inside it defaults against")
        print("   nobody -- Secretary's finding, and bigger than this gate.")
        for m in sorted(neither, key=lambda r: r["date"], reverse=True):
            first = m["open"][0] if m["open"] else "(none open)"
            print("   %-52s open=%2d closed=%2d next=%-9s [%s]"
                  % (m["file"][:52], len(m["open"]), m["closed"], first, m["schema"]))
        print()

    for m in unknown_status:
        print("  WARN no status: field at all -- %s (UNKNOWN, never read as dead)"
              % m["file"])

    print("PROVENANCE: declared %d | derived %d | unknown-may-be-unaligned %d | neither %d"
          % (len(buckets.get("declared", [])), len(buckets.get("derived", [])),
             len(unk), len(neither)))
    print("            of the unknowns: %d NO-PROPERTY (a fact about the map) | "
          "%d NOT-MEASURED (a fact about CFL's reading)"
          % (len(buckets.get("unknown-no-property", [])),
             len(buckets.get("unknown-not-measured", []))))
    if illegal:
        print("EXIT 3: %d map(s) carry an ILLEGALLY DERIVED `unaligned`." % len(illegal))
        return 3
    if thin:
        print("EXIT 3: %d derivation(s) cite a fragment rather than the clause that "
              "justifies them." % len(thin))
        return 3
    if neither:
        print("EXIT 3: %d of %d LIVE maps carry no branch value of either kind. "
              "`neither: 0` is the pass condition." % (len(neither), len(live)))
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
