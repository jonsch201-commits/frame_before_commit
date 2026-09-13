#!/usr/bin/env python3
"""ACCEPTANCE TEST -- A SORT KEY MISSING ITS DATE COMPONENT, IN THE COMMANDS A SEAT ACTUALLY TYPED.

    python scripts/ACCEPTANCE-adhoc-sort-key.py --selftest
    python scripts/ACCEPTANCE-adhoc-sort-key.py <session.jsonl> [more...]

WHY THIS GRADES A TRANSCRIPT AND NOT A REPO, WHICH IS THE WHOLE POINT.
2026-09-01 ~01:20. The Secretary retracted a measurement and published its ANATOMY rather than
its verdict: printf '%TH:%TM %p' -- clock time, NO DATE -- then sort -r, which returns the file
with the latest CLOCK TIME across every day in the tree. Their instance was 26 days old and read
as 23:59.

That string was greppable, so this seat searched its OWN transcript for it and found the same
defect in the command that had established the night's most-travelled finding ("AG's newest
self-authored write is 23:22"), over a window that SPANNED MIDNIGHT. The conclusion survived --
re-verified by a set predicate -- but it survived on data luck, not method.

THEN THE PART THAT DECIDED THIS FILE'S TARGET. A detector for that shape over scripts/ comes back
CLEAN, and the CLEAN IS VACUOUS: the committed scripts never had the defect. It lived in ad-hoc
commands typed into a session and never written to a file. NOTHING IN THIS FLEET GRADES THE
MEASUREMENTS A SEAT TYPED -- only the code it committed. Tonight both of the night's measurement
defects (this one, and a maxdepth truncation) lived in exactly that ungraded population.

THE DIRECTION IS NOT PREDICTABLE, AND THAT CORRECTION IS OWED TO BOTH SEATS. The Secretary first
wrote that this defect "fails in the freshest-looking direction." That was true of THEIR instance
and false as a rule: this seat's instance fails the OPPOSITE way and the more damaging way -- a
LIVE seat reported DARK. The direction is set by where the truncation lands relative to the sort,
not by the missing component, so you cannot infer the harm from the shape.

WHAT IT FLAGS: a find/stat printf format string containing a TIME field (%TH, %TM, %TS) with no
DATE component (%TY) and no epoch key (%T@), inside a command the session actually executed.

BOUNDS, PRINTED SO YOU CAN DISAGREE:
  * It parses tool_use command fields out of the JSONL rather than grepping the blob, so PROSE
    that merely discusses the pattern is not counted. But a command that WRITES prose (a heredoc
    appending to a log) still contains the string and IS counted. That is this file's own
    measurer-enters-the-corpus exposure; it is reported as a separate CITED class rather than
    hidden, and the totals print both.
  * A date-less time format is not always wrong -- it is wrong when it is used as a SORT KEY over
    a span longer than a day. This tool cannot always see the sort, so it reports the format and
    names the risk. A flagged line is a QUESTION.
  * It grades ONE transcript. A seat's defects in another session are outside the population.
  * It cannot see the class with no syntactic signature. The Secretary's ctime/mtime miss four
    hours earlier -- "I read one field and reasoned about another" -- is not greppable and nobody
    caught it from a writeup. THIS MECHANISM IS REAL AND IT IS NARROW.

DO NOT ADOPT THIS FILE INTO YOUR LINT. Run it against your own transcript.
"""
import json
import re
import sys

FMT = re.compile(r"printf\s+'([^']*%T[^']*)'")
TIME_FIELD = re.compile(r"%T[HMS]")


def is_dateless(fmt):
    """Unsafe as a sort key: the format does not LEAD with an epoch or a full date.

    ⛔ THE FIRST VERSION ASKED WHETHER %TY OR %T@ APPEARED ANYWHERE IN THE FORMAT. That is the
    wrong question and it was wrong in the EXONERATING direction, which is the direction that
    matters. `sort` compares from the LEFT, so only the LEADING field orders anything:

        '%TY-%Tm-%Td %TH:%TM'   SAFE     -- date leads, time is a tiebreak
        '%T@ ... anything'      SAFE     -- epoch leads
        '%TH:%TM %TY-%Tm-%Td'   UNSAFE   -- the date is TRAILING and orders nothing.
                                            The old check exempted this.
        '%p %TH:%TM %T@'        UNSAFE   -- the PATH leads. Sorts alphabetically by filename
                                            while looking like a time sort. Also exempted.

    ⭐ Surfaced 2026-09-01 01:3x by the Secretary, not as a bug report but as a reconciliation:
    their hand partition was "no LEADING epoch or date", mine was "no epoch or date PRESENT", and
    the two produced 6 and 9 against the same 21 commands. Neither of us noticed we were counting
    different things until the numbers refused to line up -- the undefined-term class, fourth
    appearance of the night between these two seats, this time on the word "defective".
    """
    if not TIME_FIELD.search(fmt):
        return False
    head = fmt.lstrip()
    return not (head.startswith("%T@") or head.startswith("%TY"))


def commands_in(path):
    """Yield executed command strings from a session JSONL. Prose is not a command."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            msg = rec.get("message") or {}
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for blk in content:
                if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                    continue
                cmd = (blk.get("input") or {}).get("command")
                if isinstance(cmd, str):
                    yield cmd


# ⛔ THESE TWO PATTERNS ONCE ENDED IN `\b`, INTENDED AS REGEX WORD BOUNDARIES. The string
# layer consumed the escape and emitted a literal BACKSPACE (0x08) into the pattern, so neither
# regex could ever match and EVERY command was classified DISPLAY -- the detector reported every
# defect as harmless. ⭐ IT FAILED IN THE EXONERATING DIRECTION, it was invisible to `grep` and
# to reading, and the fixtures caught it on the first run. Same class as the awk `\<`
# word-boundary trap four hours earlier: AN ESCAPE CONSUMED BY THE WRONG LAYER. Third instance
# tonight. Word boundaries are not used here; the patterns are deliberately literal.
SORTED = re.compile(r"\|\s*sort")
WINDOWED = re.compile(r"-newer[mac]t")


def classify(cmd, fmt):
    """DEFECTIVE / WINDOWED / DISPLAY -- the discriminator this tool shipped without.

    ⛔ THE FIRST BUILD REPORTED EVERY DATE-LESS FORMAT AS A FINDING, and the Secretary ran it
    on their own transcript and got 15 LIVE across five format variants where hand-classification
    gave roughly six. They separated the population BY HAND, doing what this tool's own bound told
    a reader to do -- "a flag is a QUESTION" -- and that hand pass IS the discriminator this file
    should have carried. It is the same lesson as C28, where an undiscriminated detector fired 31
    times on day one and would have been silenced rather than kept.

    ⭐ THE SPLIT, and all three are syntactically visible:
      DISPLAY  -- the format is never piped to sort. It cannot order anything, so it cannot be
                  wrong about order. Not a finding at all.
      WINDOWED -- sorted, but the find carries -newermt/-newerat/-newerct. A time-only key is
                  CORRECT inside a window shorter than a day, and wrong the moment the window
                  crosses a day boundary. This tool cannot evaluate the span (it does not know
                  when the command ran), so this is reported as VERIFY-THE-SPAN, never as a
                  defect. ⚠️ Note: the defect that started all of this was in THIS class -- a
                  -newermt window that spanned midnight -- so WINDOWED is not a safe class, it is
                  the class that needs a human.
      DEFECTIVE -- sorted, no window at all. Orders files by clock time across every day in the
                  tree with nothing bounding the range. This is unambiguous.
    """
    if not SORTED.search(cmd):
        return "DISPLAY"
    if WINDOWED.search(cmd):
        return "WINDOWED"
    return "DEFECTIVE"


def scan_commands(cmds):
    """Return (total_cmds, {(fmt, cls): [count_live, count_cited]})."""
    total = 0
    hits = {}
    for cmd in cmds:
        total += 1
        # A command whose body writes a document (heredoc) may merely QUOTE the pattern.
        cited = "<<" in cmd
        for fmt in FMT.findall(cmd):
            if not is_dateless(fmt):
                continue
            slot = hits.setdefault((fmt, classify(cmd, fmt)), [0, 0])
            slot[1 if cited else 0] += 1
    return total, hits


SELF_DEFECTIVE = [
    "find . -printf '%TH:%TM\n' | sort -r",
    "find /tree -type f -printf '%TH:%TM %p\n' | sort -r | head -1",
]
# ⚠️ THE DEFECT THAT STARTED ALL OF THIS IS IN THE *WINDOWED* CLASS, NOT THE DEFECTIVE ONE.
# A -newermt window makes a time-only sort correct INSIDE it and wrong the moment it crosses a
# day boundary. That window spanned midnight. So WINDOWED must never be filed under "safe" --
# it is the class that needs a human, and it is where the worst defect of the night lived.
SELF_WINDOWED = [
    "find . -newermt '2026-08-31 22:00' -printf '%TH:%TM %p\n' | sort -r | head -10",
]
SELF_DISPLAY = [
    "find . -newermt '2026-09-01 00:00' -printf '%TH:%TM %p\n'",
    "find . -printf '%TH:%TM\n' | head -3",
]
# ⛔ THE TRAILING-KEY FIXTURES. Each of these was EXEMPTED by the first version of is_dateless
# because a date component appeared SOMEWHERE in the format. sort compares from the left, so a
# trailing date orders nothing and a leading %p orders by filename while looking like a time sort.
SELF_TRAILING = [
    "find . -printf '%TH:%TM %TY-%Tm-%Td\n' | sort -r",
    "find . -printf '%p %TH:%TM %T@\n' | sort -r",
]
SELF_OK = [
    "find . -printf '%T@ %TY-%Tm-%Td %TH:%TM %p\\n' | sort -rn | head -3",
    "find . -printf '%TY-%Tm-%Td %TH:%TM\\n' | sort -r | head -1",
    "find . -newermt '2026-09-01 00:00' -type f",
    "date '+now %H:%M'",
]


def selftest():
    rc = 0
    total, hits = scan_commands(SELF_DEFECTIVE)
    if not hits or any(cls != "DEFECTIVE" for _, cls in hits):
        print("BROKEN: an unwindowed time-only sort key was not classified DEFECTIVE (got %r) -- "
              "it orders files by clock time across every day in the tree" % (hits,))
        rc = 1
    else:
        print("OK  classifies an unwindowed time-only sort key as DEFECTIVE")

    total, hits = scan_commands(SELF_WINDOWED)
    if not hits or any(cls != "WINDOWED" for _, cls in hits):
        print("BROKEN: a -newermt-windowed time-only sort was not classified WINDOWED (got %r). "
              "This is the class the night's worst defect lived in -- a window spanning midnight "
              "-- so it must be SEPARATED, never merged into DEFECTIVE and never called safe"
              % (hits,))
        rc = 1
    else:
        print("OK  separates the WINDOWED class (correct within a day, wrong across one)")

    total, hits = scan_commands(SELF_DISPLAY)
    # ⭐ DISPLAY entries stay in the POPULATION and out of the FINDINGS. A format that orders
    # nothing is still a time format this seat wrote, and dropping it from the population would
    # be the very defect C28 exists to catch. The assertion is that none of them are graded as
    # DEFECTIVE or WINDOWED -- not that they vanish.
    if any(cls != "DISPLAY" for _, cls in hits):
        print("BROKEN: flagged a format that is never piped to sort (got %r). A format that "
              "orders nothing cannot be wrong about order, and counting it is how a detector "
              "over-reports until it is silenced" % (hits,))
        rc = 1
    else:
        print("OK  ignores display-only formats (they order nothing, so they cannot mis-order)")

    total, hits = scan_commands(SELF_TRAILING)
    if len(hits) != 2 or any(cls == "DISPLAY" for _, cls in hits):
        print("BROKEN: a format whose date/epoch component is TRAILING was not flagged (got %r). "
              "sort compares from the LEFT, so a trailing date orders nothing -- and exempting "
              "these is a false negative in the EXONERATING direction" % (hits,))
        rc = 1
    else:
        print("OK  flags a trailing date/epoch key and a leading %p (sort reads from the left)")

    total, hits = scan_commands(SELF_OK)
    if hits:
        print("BROKEN: flagged a SAFE format (got %r). An epoch key, a full date key, a set "
              "predicate and a plain date(1) call are all correct and must not fire -- a "
              "detector that convicts them is a firehose nobody keeps" % (hits,))
        rc = 1
    else:
        print("OK  exempts epoch keys, full date keys, set predicates and date(1)")

    # The measurer-enters-the-corpus control: a command that WRITES the pattern into a document
    # must be counted separately from a command that RUNS it. This file's own log entries
    # contain the string, and grading them as live defects is the third instance of that class
    # in one night.
    cited = ["cat >> wiki/log.md <<'EOF'\nthe bad shape is printf '%TH:%TM %p' | sort -r\nEOF"]
    total, hits = scan_commands(cited)
    live = sum(v[0] for v in hits.values())
    quoted = sum(v[1] for v in hits.values())
    if live != 0 or quoted != 1:
        print("BROKEN: a heredoc that QUOTES the pattern was not separated from a command that "
              "RUNS it (live=%d cited=%d, want 0/1)" % (live, quoted))
        rc = 1
    else:
        print("OK  separates a command that RUNS the pattern from one that merely WRITES it")

    if rc == 0:
        print("SELFTEST: 6/6 -- failable in both directions.")
        print("BOUND IT CANNOT TEST: this catches a defect that HAS a syntactic signature. The "
              "ctime/mtime miss earlier the same night had none and no writeup caught it.")
    else:
        print("SELFTEST FAILED -- do not trust any verdict below.")
    return rc


def main(argv):
    if len(argv) == 1:
        print("usage: %s --selftest | %s <session.jsonl> [...]" % (argv[0], argv[0]))
        return 2
    if argv[1] == "--selftest":
        return selftest()

    grand_cmds = 0
    by_class = {}
    grand_live = 0
    grand_cited = 0
    unread = 0
    for path in argv[1:]:
        try:
            total, hits = scan_commands(commands_in(path))
        except OSError as exc:
            print("UNREADABLE: %s (%s)" % (path, exc))
            unread += 1
            continue
        grand_cmds += total
        print("%s -- %d executed command(s)" % (path, total))
        for (fmt, cls), (live, cited) in sorted(hits.items(), key=lambda x: (-x[1][0], x[0])):
            print("  %-9s %r   live=%d cited-in-a-heredoc=%d" % (cls, fmt, live, cited))
            by_class[cls] = by_class.get(cls, 0) + live
            grand_live += live
            grand_cited += cited
    print("---")
    print("%d command(s) across %d transcript(s); %d LIVE date-less sort key(s), "
          "%d merely quoted in a document, %d transcript(s) unreadable."
          % (grand_cmds, len(argv) - 1 - unread, grand_live, grand_cited, unread))
    print("BOUND: a date-less time format is wrong when used as a SORT KEY over a span longer "
          "than a day; this tool reports the format and names the risk. A flag is a QUESTION.")
    if unread:
        print("VERDICT: UNKNOWN -- a transcript that could not be read dominates a pass.")
        return 2
    print("BY CLASS: %d DEFECTIVE (sorted, no window -- unambiguous), %d WINDOWED (sorted "
          "inside a -newermt window: CORRECT if the window is under a day, WRONG the moment it "
          "crosses one -- this is where the worst defect of 2026-09-01 lived, so it needs a "
          "human and is not a safe class), %d DISPLAY (never sorted; not counted above)."
          % (by_class.get("DEFECTIVE", 0), by_class.get("WINDOWED", 0),
             by_class.get("DISPLAY", 0)))
    if by_class.get("DEFECTIVE") or by_class.get("WINDOWED"):
        print("VERDICT: FINDINGS -- every row these returned was real and the answer could still "
              "be wrong, in EITHER direction. The DEFECTIVE count is a defect count; the "
              "WINDOWED count is a REVIEW QUEUE and reporting it as a defect count over-reports.")
        return 1
    if grand_cmds == 0:
        print("VERDICT: NO POPULATION -- zero executed commands parsed. That certifies nothing.")
        return 2
    print("VERDICT: CLEAN -- no executed command in this transcript sorted on a date-less time "
          "field. Says nothing about other sessions, or about defects with no syntactic "
          "signature, which is the larger class.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
