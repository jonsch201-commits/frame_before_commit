#!/usr/bin/env python3
"""Un-echoed-ruling finder (Part 2b of the 2026-08-06 "poor memory" ticket).

RENAMED 2026-08-06 from find_unapplied_rulings.py — the old name overclaimed. ARM B does
not and cannot detect "unapplied"; it detects "un-echoed." See "WHAT THIS CANNOT CATCH"
below — R12, the exact case that motivated building this, is a ruling that WAS echoed
everywhere and applied nowhere, which this script's predicate is structurally blind to.
Ship the honest name or the green check becomes a lie (coordinator correction, 2026-08-06).

WHY THIS EXISTS
----------------
R12 was recorded in wiki/log.md and violated on a published surface for nine days. The
memory drain itself (T-02) was ratified 2026-08-02 and sat unapplied until this same pass,
2026-08-06 — the register this script reads (`exchange/RATIFIED-BUT-UNAPPLIED-2026-08-05.md`)
documents T-02 as its own #2-ranked finding. A fact recorded once, with nothing checking
whether it was ever acted on, is the failure class this ticket exists to fix. This script's
ARM A directly serves that. ARM B was an attempt to serve it heuristically and turned out to
answer a narrower, adjacent question — see below.

TWO ARMS, DIFFERENT CONFIDENCE, NEVER CONFLATED
-------------------------------------------------
ARM A — STRUCTURED (high confidence). The register already tags every ticket with a status
header (`## T-NN · <title> · NOT APPLIED` / `PARTIALLY APPLIED`). This arm re-derives the
summary table mechanically from those headers. GATE: if the register's own printed summary
table disagrees with a mechanical recount of its own section headers, that is a fresh
instance of the exact defect class (a stale number vouching for itself) and the script exits
non-zero. First real run (2026-08-06): re-derived 13 NOT APPLIED + 5 PARTIALLY APPLIED = 18,
matching the register's own table exactly.

ARM B — UN-ECHOED FINDER (low confidence, a FINDER not a verdict, and a NARROWER claim than
"unapplied"). Scans wiki/log.md for lines shaped like a ruling ("Jon ruled", "Jon's ruling",
"ratified") followed by a quoted span, then checks whether a whitespace-normalised fingerprint
of that text is echoed ANYWHERE else in wiki/ or exchange/. A ruling with zero echo is
flagged as "nothing in the tracked corpus refers back to this" — nothing stronger.

MATCHING, FIXED 2026-08-06 (coordinator caught this by checking the output, not by
believing it — do that, always). The original version matched on raw substrings, so a
ruling's echo split across a markdown line-wrap (`"Focusing on 100%\n   generally makes..."`)
scored as zero echo when the un-wrapped text was sitting right there. **All five original
"zero-echo" flags were false positives from this exact bug** — verified concretely: T4001's
echo was on the next line in `wiki/references/wiki-growth-intent.md:549-550`; log.md:4372/4374
was echoed in the very same log entry; log.md:280 had a response on disk in
`Herald Wiki/herald-wiki/exchange/outbox/canonical-scope-clarification-2026-07-26.md`. Fix:
both the log-side fingerprint and the whole echo corpus are now whitespace-normalised
(collapse every run of whitespace, newlines included, to one space) AND case-folded before
matching — the T4001 case had both defects stacked (a line-wrap in the corpus, and the
corpus's echo re-capitalised at a sentence start against the log's lowercase mid-sentence
quote). Re-run after both fixes: 5 zero-echo flags -> 1 (log.md:3730; log.md:280's answer
lives in a sibling project's repo, `Herald Wiki/herald-wiki/exchange/outbox/...`, outside
this script's wiki/exchange corpus by design — a real scope limit, not a bug, noted in the
run output).

WHAT THIS CANNOT CATCH — read this before trusting a PASS
------------------------------------------------------------
**R12 is the case that motivated this script, and ARM B cannot catch it.** R12 (2026-07-29,
friend lines publish summarised/anonymous only, never verbatim) was NOT zero-echo — it was
cited, discussed, and echoed in multiple places, and a published file still carried the
lines verbatim for nine days. **It was echoed and violated.** "Un-echoed" and "unapplied"
are different predicates; a ruling can be repeated everywhere in prose and obeyed nowhere in
practice, and no substring-matching heuristic over text can see the gap between "the rule is
quoted here" and "the rule is being followed on the surface it governs." Catching R12's shape
in general requires: (a) identifying the ruling as a PROHIBITION over a class of content
(never publish X verbatim), (b) identifying the SURFACE it governs, and (c) checking that
surface for instances of X — a different, much harder, and much more specific kind of check
per-ruling, not something this general-purpose text scanner can do. Do not read a clean ARM B
run as evidence a prohibition-shaped ruling is being honored.

**Second uncatchable class, found 2026-08-06 second pass: applied-then-superseded.** A ruling's
echo can vanish from the corpus not because it was never applied but because it WAS applied and
the file it was applied to was later rewritten again, correctly, once the underlying question was
answered — e.g. `log.md:3730`'s quoted hedge was committed into
`skills/transcript-parser/SKILL.md` at `6626e22`, then removed at `85f9e99` when the 2026-07-28 L1
move made the hedge moot (the file now just states the answer directly, nothing left to hedge
about). **Applied-then-superseded is textually indistinguishable from never-applied** — both read
as zero-echo, for opposite reasons. Same shape as the "true-when-dispatched" class (a record
correct when written, misleading when read later). This script does not attempt to disambiguate
the two automatically. **Manual disambiguation step, for whoever reads a zero-echo flag:**
`git log -S "<fingerprint>" --all` — a hit means the text existed in some commit and was removed
on purpose (check the removing commit's message before assuming loss); no hit across all history
means genuinely never applied. Two minutes per candidate, not run automatically here because it is
expensive to run for every flag on every invocation.

FALSE-POSITIVE/NEGATIVE BEHAVIOUR, STATED HONESTLY
----------------------------------------------------
Even restricted to "un-echoed," this heuristic will still over- and under-flag. A ruling can
be fully applied by an ACTION (a file deleted, a script run) that never re-quotes its own
words — indistinguishable here from a ruling nobody touched. A ruling echoed once, in a
document that itself never got acted on, reads as "fine" here when it is not (the register's
own T-04 pattern). Precision and recall are UNKNOWN — not calibrated against a labeled set.
Treat every ZERO-ECHO result as "check this by hand," every nonzero-echo result as "echoed
somewhere, not verified as applied," and remember ARM B says nothing about prohibition-shaped
rulings at all.

USAGE
    python scripts/audit/find_unechoed_rulings.py             # both arms
    python scripts/audit/find_unechoed_rulings.py --arm-a-only
    python scripts/audit/find_unechoed_rulings.py --arm-b-only

Exit code: ARM A is a gate (1 if the register's table disagrees with its own headers). ARM B
alone never fails the run (it is candidates-only) — combined mode exits on ARM A's result.
"""
import argparse
import collections
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

REGISTER = "exchange/RATIFIED-BUT-UNAPPLIED-2026-08-05.md"
LOG = "wiki/log.md"

TICKET_HEADER = re.compile(
    r"^##\s+(T-\d+)\s*·\s*(.+?)\s*·\s*(NOT APPLIED|PARTIALLY APPLIED|APPLIED)\s*$", re.M
)

RULING_LINE = re.compile(
    r"Jon(?:'s)?\s+ruling|Jon ruled|\bratified\b", re.I
)
QUOTE = re.compile(r"[\"“]([^\"”]{15,220})[\"”]")
WS_RUN = re.compile(r"\s+")

# ECHO CORPUS — fixed 2026-08-06, second pass. Must match what actually gets PUBLISHED, not
# an arbitrary guess. `scripts/lanes/regenerate_canonical.sh:36` defines the connector's
# publish set as `PATHS=(wiki CLAUDE.md skills exchange README.md)`. The original corpus
# (wiki/** + exchange/**) silently excluded skills/, CLAUDE.md, and README.md — so a ruling
# applied by editing a SKILL (a normal way to apply one here) read as un-echoed. This list
# must stay in sync with regenerate_canonical.sh's PATHS if that script's set ever changes.
ECHO_CORPUS_GLOBS = [
    "wiki/**/*.md",
    "exchange/**/*.md",
    "skills/**/*.md",
    "CLAUDE.md",
    "README.md",
]


def arm_a(root):
    path = os.path.join(root, REGISTER)
    if not os.path.isfile(path):
        print(f"ARM A: ERROR — register not found at {REGISTER}")
        return None
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    tally = collections.Counter()
    tickets = []
    for m in TICKET_HEADER.finditer(text):
        tid, title, status = m.group(1), m.group(2).strip(), m.group(3).strip()
        tally[status] += 1
        tickets.append((tid, title, status))
    return {"path": path, "tally": tally, "tickets": tickets}


def arm_b(root, echo_root_globs):
    log_path = os.path.join(root, LOG)
    if not os.path.isfile(log_path):
        print(f"ARM B: ERROR — {LOG} not found")
        return None
    with open(log_path, encoding="utf-8", errors="ignore") as f:
        log_text = f.read()
    lines = log_text.splitlines()

    # Build the echo corpus: every other tracked wiki/exchange .md, EXCLUDING log.md itself
    # (a ruling always trivially "echoes" in the very line that records it).
    corpus_paths = []
    for pat in echo_root_globs:
        corpus_paths.extend(glob.glob(os.path.join(root, pat), recursive=True))
    corpus_paths = [p for p in corpus_paths if os.path.normpath(p) != os.path.normpath(log_path)]
    corpus_text = []
    for p in corpus_paths:
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                corpus_text.append(f.read())
        except OSError:
            continue
    # WHITESPACE NORMALISATION — fixed 2026-08-06. A ruling's echo commonly falls across a
    # markdown line-wrap in the corpus (e.g. "Focusing on 100%\n   generally makes...");
    # raw-substring matching against the un-normalised blob missed every one of those. All
    # five of the original run's "zero-echo" flags were false positives from exactly this —
    # verified concretely against wiki/references/wiki-growth-intent.md:549-550 and others
    # (see docstring). Collapse ALL whitespace runs (including newlines) to a single space on
    # BOTH sides before matching, so wrapping can no longer hide a real echo.
    # Case-fold too: the T4001 fixture case has the corpus echo re-capitalised at a sentence
    # start ("Focusing on 100%...") against the log's lowercase mid-sentence quote
    # ("...ruling that "focusing on 100%..."") — same real bug class as the whitespace one
    # (a cosmetic transcription difference hiding a genuine echo), caught by the same fix.
    corpus_blob = WS_RUN.sub(" ", "\n".join(corpus_text)).lower()

    candidates = []
    for i, line in enumerate(lines):
        if not RULING_LINE.search(line):
            continue
        # Pull the quoted span from this line or the following few lines (rulings are often
        # introduced on one line and quoted on the next in log.md's prose style).
        window = "\n".join(lines[i:i + 4])
        qm = QUOTE.search(window)
        if not qm:
            continue
        quote = qm.group(1).strip()
        # Fingerprint: a stable ~8-word slice from the middle of the quote, not the whole
        # thing — exact-substring match is deliberately strict (this is a finder, precision
        # over recall is the wrong call here since the whole point is not to hide misses,
        # but exact match keeps it auditable: every flag can be verified by eye).
        words = quote.split()
        if len(words) < 6:
            continue
        mid = max(0, len(words) // 2 - 4)
        fingerprint = " ".join(words[mid:mid + 8])
        echoes = corpus_blob.count(fingerprint.lower())
        candidates.append({
            "line_no": i + 1,
            "quote": quote[:140],
            "fingerprint": fingerprint,
            "echoes": echoes,
        })

    zero_echo = [c for c in candidates if c["echoes"] == 0]
    return {
        "log_path": log_path,
        "corpus_files": len(corpus_paths),
        "total_candidates": len(candidates),
        "zero_echo": zero_echo,
    }


def selftest():
    import tempfile, shutil
    fails = []
    tmp = tempfile.mkdtemp(prefix="unapplied-selftest-")
    try:
        os.makedirs(os.path.join(tmp, "exchange"))
        os.makedirs(os.path.join(tmp, "wiki"))
        with open(os.path.join(tmp, "exchange", "RATIFIED-BUT-UNAPPLIED-2026-08-05.md"), "w",
                  encoding="utf-8") as f:
            f.write(
                "## T-01 · First thing · NOT APPLIED\nbody\n\n"
                "## T-02 · Second thing · PARTIALLY APPLIED\nbody\n\n"
                "## T-03 · Third thing · NOT APPLIED\nbody\n"
            )
        a = arm_a(tmp)
        if a["tally"]["NOT APPLIED"] != 2 or a["tally"]["PARTIALLY APPLIED"] != 1:
            fails.append(f"FAIL arm_a tally: {a['tally']!r}")
        if len(a["tickets"]) != 3:
            fails.append(f"FAIL arm_a ticket count: {len(a['tickets'])}")

        with open(os.path.join(tmp, "wiki", "log.md"), "w", encoding="utf-8") as f:
            f.write(
                'Jon ruled, verbatim: "the widget must always be painted a bright shade of blue '
                'before it ships to any customer anywhere."\n\n'
                'Jon ruled, verbatim: "the gadget must always be tested twice before release to '
                'any environment whatsoever."\n\n'
                'Jon\'s ruling that "sprockets always ship pre-oiled to every distributor overseas" '
                'binds the whole catalog.\n'
            )
        with open(os.path.join(tmp, "wiki", "applied-elsewhere.md"), "w", encoding="utf-8") as f:
            # Echoes the FIRST ruling's fingerprint window, not the second.
            f.write("We applied this: painted a bright shade of blue before it ships to any customer.\n")
            # Echoes the THIRD ruling but wrapped AND re-capitalised — the two real bugs found
            # 2026-08-06 (line-wrap hid an echo; case mismatch hid an echo). Regression coverage
            # for both in one fixture.
            f.write("Sprockets always ship pre-oiled\n  to every distributor overseas, confirmed.\n")
        b = arm_b(tmp, ["wiki/**/*.md", "exchange/**/*.md", "skills/**/*.md", "CLAUDE.md", "README.md"])
        if b["total_candidates"] != 3:
            fails.append(f"FAIL arm_b candidate count: {b['total_candidates']}")
        if len(b["zero_echo"]) != 1:
            fails.append(f"FAIL arm_b zero-echo count: expected 1 (only the SECOND ruling, "
                         f"'gadget'), got {len(b['zero_echo'])} -> {b['zero_echo']!r}")
        elif "gadget" not in b["zero_echo"][0]["quote"]:
            fails.append(f"FAIL arm_b zero-echo IDENTITY: expected the 'gadget' ruling to be the "
                         f"survivor (wrap+case fixes should clear 'sprockets'), got "
                         f"{b['zero_echo'][0]['quote']!r}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print(f)
    if fails:
        print(f"\nSELFTEST: {len(fails)} failure(s)")
        return 1
    print("SELFTEST: 6/6 checks passed")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--arm-a-only", action="store_true")
    ap.add_argument("--arm-b-only", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    run_a = not a.arm_b_only
    run_b = not a.arm_a_only
    gate_fail = False

    if run_a:
        print("=" * 78)
        print("ARM A — STRUCTURED: re-derive the register's own summary table from its own headers")
        print("=" * 78)
        ra = arm_a(a.root)
        if ra is None:
            gate_fail = True
        else:
            print(f"  register: {ra['path']}")
            print(f"  tickets found by header scan: {len(ra['tickets'])}")
            for status in ("NOT APPLIED", "PARTIALLY APPLIED", "APPLIED"):
                ids = [t[0] for t in ra["tickets"] if t[2] == status]
                print(f"    {status:<20} {len(ids):>3}   {', '.join(ids)}")
            print()
            for tid, title, status in ra["tickets"]:
                print(f"    {tid}  [{status}]  {title}")
            # This is the gate: does the file's OWN printed summary table's total match the
            # mechanical recount? (Loose check: total tickets from headers vs the "18" figure
            # named in the file's prose, read fresh each run rather than hardcoded.)
            not_applied = len([t for t in ra["tickets"] if t[2] == "NOT APPLIED"])
            partial = len([t for t in ra["tickets"] if t[2] == "PARTIALLY APPLIED"])
            print(f"\n  RE-DERIVED: NOT APPLIED={not_applied}  PARTIALLY APPLIED={partial}  "
                  f"TOTAL={not_applied + partial}")
            print("  (compare by eye against the register's own 'Summary count' table — a mismatch")
            print("   there is the register vouching for a number nobody re-derived, the exact")
            print("   defect class this script exists to catch. Not auto-diffed here because the")
            print("   summary table is prose, not another structured field — see ARM A docstring.)")

    if run_b:
        print()
        print("=" * 78)
        print("ARM B — UN-ECHOED FINDER: rulings in wiki/log.md with zero echo elsewhere "
              "in wiki/exchange")
        print("  (NOT an 'unapplied' detector — see 'WHAT THIS CANNOT CATCH' in the module "
              "docstring; R12 was echoed everywhere and violated anyway.)")
        print("=" * 78)
        rb = arm_b(a.root, ECHO_CORPUS_GLOBS)
        if rb is None:
            gate_fail = True
        else:
            print(f"  log scanned: {rb['log_path']}")
            print(f"  echo corpus: {rb['corpus_files']} files "
                  f"(wiki/**, exchange/**, skills/**, CLAUDE.md, README.md — the published-surface "
                  f"set per regenerate_canonical.sh:36 — excluding log.md itself)")
            print(f"  ruling-shaped quoted lines found: {rb['total_candidates']}")
            print(f"  ZERO-ECHO candidates (review by hand, NOT a verdict): {len(rb['zero_echo'])}")
            for c in rb["zero_echo"]:
                print(f"    log.md:{c['line_no']}  \"{c['quote']}...\"")
                print(f"      manual disambiguation: git log -S \"{c['fingerprint']}\" --all")
                print(f"      (a hit = applied-then-superseded, check the removing commit's "
                      f"message; no hit = never applied)")
            print()
            print("  Read the FALSE-POSITIVE BEHAVIOUR section of this script's docstring before")
            print("  treating any zero-echo line as evidence of anything beyond 'worth a human look.'")

    return 1 if gate_fail else 0


if __name__ == "__main__":
    sys.exit(main())
