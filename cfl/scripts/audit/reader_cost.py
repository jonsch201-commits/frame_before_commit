#!/usr/bin/env python3
"""reader_cost.py -- derive a document's reader_token_cost instead of typing it.

WHY THIS EXISTS
---------------
`exchange/PR3-DESCRIPTION.md` carried `reader_token_cost: "~1,500 tokens (about four
minutes to read)"`. Jon checked it on 2026-09-04 at ~15:3x. Measured:

    bytes 10,631 | words 1,773
    chars/4     -> 2,657 tokens
    words*1.33  -> 2,358 tokens
    at 200 wpm  -> 8.9 minutes
    at 250 wpm  -> 7.1 minutes

The claim understated the cost by 57-77% and the reading time by roughly half.

HOW IT GOT WRONG, and it is the PR's own section 3 in the PR's own frontmatter:
the number was TYPED ONCE and never re-derived, while the document grew three
times the same day (a vocabulary gloss, four more gloss rows, a denominator
note). "The summary and the run have separate provenance" -- here the summary was
a frontmatter field and the run was the file it describes.

It also had a practical edge: Jon said he had FIVE MINUTES at 22:00 and this
document told him it was a four-minute read.

WHAT IT DOES
------------
Prints derived token and minute estimates for a file, as a RANGE with both
methods named, never a single confident number. Optionally rewrites the
`reader_token_cost:` frontmatter line in place (--write) so the claim is derived
rather than authored.

BOUNDS, stated because an estimate that hides its method is the defect above:
  - chars/4 and words*1.33 are HEURISTICS, not a tokenizer. They bracket the
    real count for English prose; they are wrong for code, tables, and CJK.
  - Reading speed 200-250 wpm is ordinary adult prose speed. A dense technical
    page with tables reads SLOWER, so the upper minute figure is the honest one
    to quote to someone with a fixed window.
  - No tokenizer is available offline here. If one is ever added, replace the
    heuristics and delete this paragraph.

Exit: 0 always for a readable file; 2 if the file cannot be read (UNKNOWN).
"""

import argparse
import re
import sys
from pathlib import Path

FM_RE = re.compile(r'^(reader_token_cost:)\s*.*$', re.MULTILINE)

# ---------------------------------------------------------------------------
# RESPONSE COST -- added 2026-09-04 ~16:0x, hours after this script shipped,
# because Jon corrected the thing it measures:
#
#   "the reading time might be 5 minutes its just that the thinking and
#    replying time is not."
#
# He is right and the correction lands on this file's own stated bound. The
# skill this script serves says: "deriving protects against drift, never against
# aiming at the wrong thing." Reading time is DERIVED CORRECTLY AND AIMED WRONG.
# The scarce resource is not his eyes. It is his judgement.
#
# So a document now declares how many DECISIONS it asks of its reader, because
# N decisions is what costs him -- and one hard decision in a short letter is
# more expensive than a long letter that asks for nothing.
#
# Heuristic and honest about it: counts explicit ask markers. It cannot judge how
# HARD a decision is, and difficulty is most of the cost. So it reports a COUNT
# and requires the author to list them; a count with no list is the defect this
# whole file exists to prevent.
# ---------------------------------------------------------------------------
ASK_PATTERNS = [
    (re.compile(r'^\s*(?:[-*]|\d+\.)?\s*.*(?<![A-Za-z])(?:should|would|do)\s+(?:you|we|I).*\?\s*$',
                re.MULTILINE | re.IGNORECASE), "a question put to the reader"),
    (re.compile(r'WHAT I NEED FROM YOU', re.IGNORECASE), "an explicit ask block"),
    (re.compile(r'^\s*on_silence:\s*ACTS', re.MULTILINE | re.IGNORECASE),
     "an on-silence default that FIRES if unanswered"),
    (re.compile(r'(?<![A-Za-z])(?:ruling|decide|your call|approve|authoris|authoriz)\w*', re.IGNORECASE),
     "a decision word"),
]


def response_cost(text: str) -> dict:
    hits = {}
    for rx, label in ASK_PATTERNS:
        n = len(rx.findall(text))
        if n:
            hits[label] = n
    return {"markers": hits, "total": sum(hits.values())}



def measure(text: str) -> dict:
    words = len(text.split())
    chars = len(text)
    t_chars = chars // 4
    t_words = int(words * 1.33)
    lo, hi = sorted((t_chars, t_words))
    return {
        "chars": chars, "words": words,
        "tok_chars": t_chars, "tok_words": t_words,
        "tok_lo": lo, "tok_hi": hi,
        "min_fast": words / 250.0, "min_slow": words / 200.0,
    }


def render(m: dict, r: dict | None = None) -> str:
    """The string that goes in frontmatter. A RANGE, with the slower minute figure
    quoted second because that is the one a person with a fixed window needs."""
    return (f'"~{m["tok_lo"]:,}-{m["tok_hi"]:,} tokens; '
            f'{m["min_fast"]:.0f}-{m["min_slow"]:.0f} min to read '
            f'({m["words"]:,} words, derived by scripts/audit/reader_cost.py -- '
            f'heuristic, not a tokenizer)"'
            if not r else
            f'"~{m["tok_lo"]:,}-{m["tok_hi"]:,} tokens; {m["min_fast"]:.0f}-{m["min_slow"]:.0f} min '
            f'to READ, but {r["total"]} ask-marker(s) -- REPLY time is the real cost and this '
            f'number does not measure it ({m["words"]:,} words, derived by '
            f'scripts/audit/reader_cost.py)"')


def self_check() -> list:
    fails = []
    m = measure("word " * 1000)
    if not (m["words"] == 1000):
        fails.append("word count wrong on a 1000-word fixture")
    if not (m["tok_lo"] <= m["tok_hi"]):
        fails.append("lo/hi not ordered")
    if m["min_slow"] <= m["min_fast"]:
        fails.append("slow reading time must exceed fast -- the range is inverted")
    # A grown document must cost MORE. This is the exact drift that was missed.
    m2 = measure("word " * 2000)
    if not (m2["tok_lo"] > m["tok_lo"]):
        fails.append("doubling the text did not raise the estimate -- the measure is inert")
    # CONTROL: an empty file must not report a comfortable small number as if measured.
    m0 = measure("")
    if m0["words"] != 0 or m0["tok_hi"] != 0:
        fails.append("empty input did not measure as zero")

    # RESPONSE COST, both directions. A document that asks nothing must score 0,
    # or the metric cannot tell a briefing from a demand.
    if response_cost("Here is a fact. Here is another fact.")["total"] != 0:
        fails.append("a document that asks nothing scored above zero -- cannot distinguish "
                     "a briefing from a demand")
    if response_cost("## WHAT I NEED FROM YOU" + chr(10) +
                     "Should you approve this?")["total"] < 2:
        fails.append("an explicit ask block plus a question scored under 2 -- the ask "
                     "counter is inert")
    if response_cost("on_silence: ACTS -- this fires if unanswered")["total"] < 1:
        fails.append("an on_silence ACTS default did not register as an ask; a default that "
                     "FIRES is the most expensive kind of silence")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--write", action="store_true",
                    help="rewrite the reader_token_cost: frontmatter line in place")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()

    if a.self_check:
        f = self_check()
        if f:
            print(f"SELF-CHECK: FAIL -- {len(f)} violation(s)")
            for x in f:
                print("  " + x)
            return 1
        print("SELF-CHECK: PASS -- 9 assertions: growth fixture, empty-input control, and "
              "three response-cost controls incl. a document that asks nothing")
        return 0

    if not a.path:
        print("UNKNOWN: no path given")
        return 2
    p = Path(a.path)
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"UNKNOWN: cannot read {p} ({e.__class__.__name__})")
        return 2

    m = measure(text)
    print(f"{p.name}: {m['chars']:,} chars, {m['words']:,} words")
    print(f"  tokens : {m['tok_lo']:,}-{m['tok_hi']:,}  (chars/4={m['tok_chars']:,}, "
          f"words*1.33={m['tok_words']:,}) -- heuristic, not a tokenizer")
    print(f"  minutes: {m['min_fast']:.1f} (250 wpm) - {m['min_slow']:.1f} (200 wpm); "
          f"quote the slower one to someone with a fixed window")

    r = response_cost(text)
    print(f"  ASK MARKERS: {r['total']}  <- REPLY cost, which is the one that matters and "
          f"which this script CANNOT size")
    for label, n in sorted(r["markers"].items(), key=lambda kv: -kv[1]):
        print(f"    {n:3d}  {label}")
    if r["total"] == 0:
        print("    none -- this document informs and asks nothing. Cheapest kind to receive.")
    else:
        print("    A short document with one hard decision costs more than a long one with none.")
        print("    LIST the decisions explicitly; a count with no list is the defect this file exists for.")

    if a.write:
        new_line = f"reader_token_cost: {render(m, response_cost(text))}"
        if FM_RE.search(text):
            text = FM_RE.sub(new_line.replace("\\", "\\\\"), text, count=1)
            p.write_text(text, encoding="utf-8")
            print(f"  WROTE: {new_line}")
        else:
            print("  NOT WRITTEN: no reader_token_cost: line in this file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
