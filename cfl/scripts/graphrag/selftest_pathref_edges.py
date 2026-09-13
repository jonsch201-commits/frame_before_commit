#!/usr/bin/env python3
"""selftest_pathref_edges.py -- the falsifier for F-4 (backticked-path graph edges).

WHY THIS EXISTS. F-4 was adopted 2026-08-31 from a measurement of this trunk's own index:
CFL's extract_links() reads [[wikilinks]] and [md](links), and this program writes NEITHER --
it cites by backticked path. 31,797 such references sit in indexed chunk text and the graph
extractor cannot see one of them. Adding them takes degree-zero from 1,076 (54.0%) to 391
(19.6%) and edges from 1,541 to 7,563.

IT TESTS THE REAL FUNCTION. extract_pathrefs() is imported from build_trunk_index; a
re-implementation here would test a copy, which is the class this repo's own method rules name.

POSITIVE CONTROLS ARE MANDATORY, and so are the negatives -- an extractor that matches
everything would "pass" a suite made only of things that should match. The two failure
directions of this change are opposite and both are covered:
  * MISSES a real citation  -> the defect stays live and the fix reads as shipped
  * MATCHES prose or syntax -> the graph fills with edges nobody wrote, which is WORSE than
    a sparse graph, because a wrong edge is retrievable and a missing one is merely absent

  python scripts/selftest_pathref_edges.py     # exit 0 = all controls behaved
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from build_index import extract_pathrefs  # noqa: E402  (CFL adaptation: Herald's trunk names it build_trunk_index)

BT = chr(96)


def bt(s):
    """Wrap in backticks without ever typing one through a shell."""
    return BT + s + BT


# (name, text, expected targets, what the case is for)
CASES = [
    ("plain_citation",
     "see " + bt("wiki/tracker/foo.md") + " for the ruling",
     ["wiki/tracker/foo.md"],
     "POSITIVE -- the form this entire program actually writes"),

    ("two_in_one_line",
     bt("wiki/log.md") + " and " + bt("CARRIER.md"),
     ["CARRIER.md", "wiki/log.md"],
     "POSITIVE -- multiple citations in one paragraph, sorted"),

    ("windows_separators",
     bt("wiki" + chr(92) + "tracker" + chr(92) + "bar.md"),
     ["wiki/tracker/bar.md"],
     "POSITIVE -- Jon and half this repo write Windows paths; both must normalise"),

    ("deduped",
     bt("wiki/log.md") + " ... later again " + bt("wiki/log.md"),
     ["wiki/log.md"],
     "POSITIVE -- one edge per (src,target); repetition is emphasis, not degree"),

    ("line_and_anchor_suffix_is_not_matched",
     bt("wiki/log.md:1889") + " says so",
     [],
     "BOUND, ASSERTED NOT ASSUMED -- a `path:line` cite does NOT match, because the regex "
     "anchors on .md at the closing backtick. This is the single biggest known miss and it is "
     "stated here rather than discovered later."),

    ("short_basename_still_matched",
     bt("a/b.md") + " and " + bt("c.md"),
     ["a/b.md", "c.md"],
     "POSITIVE, AND IT CAUGHT A REAL DEFECT: the first draft floored the regex at 4 characters "
     "before .md, so every citation with a short name was silently dropped. Found by this "
     "control BEFORE the rebuild, not after."),

    ("bare_path_in_prose",
     "see wiki/tracker/foo.md for the ruling",
     [],
     "NEGATIVE -- prose is not a citation; only the backticked form is"),

    ("wikilink_not_double_counted",
     "see [[loop-taxonomy]] and " + bt("wiki/log.md"),
     ["wiki/log.md"],
     "NEGATIVE-ish -- the wikilink is upstream's job; we must not re-emit it"),

    ("non_md_ignored",
     bt("scripts/build_index.py") + " and " + bt("settings.json"),
     [],
     "NEGATIVE -- CFL's stem resolver does basename[:-3], so non-.md would resolve wrong"),

    ("directory_not_a_file",
     bt("wiki/tracker/"),
     [],
     "NEGATIVE -- a directory is not a citable node"),

    ("empty_and_none",
     "",
     [],
     "NEGATIVE -- empty input yields nothing and must not raise"),

    ("code_fence_content_still_counts",
     "```\n" + bt("wiki/log.md") + "\n```",
     ["wiki/log.md"],
     "STATED DECISION, not an oversight: a path inside a fence is still a real reference in "
     "this corpus (every letter quotes commands that name files). The dream skill's exclusion "
     "rule is about [[slug]] SYNTAX EXAMPLES, which cannot occur here -- a syntax example is "
     "never a resolvable filename, so it dies at the resolver instead."),
]


def main():
    print("=" * 78)
    print("F-4 CONTROL SUITE -- backticked-path graph edges")
    print("   exercising build_index.extract_pathrefs() directly")
    print("=" * 78)
    failures = []
    for name, text, expected, why in CASES:
        got = [t for _kind, t in extract_pathrefs(text)]
        ok = (got == sorted(expected))
        print("  [%s] %-34s got=%s" % ("PASS" if ok else "FAIL", name, got))
        print("         %s" % why)
        if not ok:
            print("         WANT=%s" % sorted(expected))
            failures.append(name)

    # every emitted edge must carry the new kind, or it would silently merge with wikilinks
    kinds = {k for k, _ in extract_pathrefs(bt("a/b.md") + " " + bt("c.md"))}
    ok = (kinds == {"pathref"})
    print("  [%s] %-34s kinds=%s" % ("PASS" if ok else "FAIL", "edge_kind_is_new", sorted(kinds)))
    print("         NEGATIVE CONTROL -- a pathref must never be emitted as 'wikilink' or "
          "'mdlink'; a new kind is what keeps the old graph measurable next to the new one")
    if not ok:
        failures.append("edge_kind_is_new")

    print()
    if failures:
        print("[FAIL] %d control(s) did not behave: %s" % (len(failures), ", ".join(failures)))
        return 1
    print("[ OK  ] all controls behaved, positives AND negatives.")
    print("[BOUND] This proves the EXTRACTOR. Resolution is CFL's stem pass, and a basename")
    print("        collision there can still point an edge at the wrong twin -- a defect that")
    print("        predates this change and applies to every wikilink in the index today.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
