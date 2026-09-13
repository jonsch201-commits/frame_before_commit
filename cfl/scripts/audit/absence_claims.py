#!/usr/bin/env python3
"""absence_claims.py -- FRAME2-POP. Grade every ABSENCE CLAIM in this repo's prose for whether it
names the POPULATION it searched.

WHY, Jon 2026-09-05 (dispatch N:\\claude-cfl\\clone\\exchange\\dispatches\\2026-09-05\\002941-FRAME2-pop.md):
CFL's failures "may be a search skill issue... may be an unformalized skill." Herald adopted
POPULATION as the third value in their review metric the night before, after five trunks spent a
night hunting a mirror job that turned out to be a running process, not a file. Every trunk asked
the RIGHT question and searched a corpus that COULD NOT CONTAIN THE ANSWER: Task Scheduler --
correct, empty. Both drives grepped for robocopy in *.bat/*.cmd/*.ps1/*.sh -- correct, prose only.

THE RULE: before writing "not found", name the population searched AND one population that was
not. This script does not enforce the second half (naming a population NOT searched) -- no static
detector can verify a claim about a search that didn't happen. It enforces the first half only:
did the writer name ANY population at all before asserting absence.

WHAT THIS CONSUMES, PER THE DISPATCH, RATHER THAN RE-DERIVING
---------------------------------------------------------------
finding_consequence.py already solved "a markdown bullet is a BLOCK: the marker line plus every
indented continuation line, and the evidence usually lives in the indent" -- and paid for that
lesson on its own second real run. `extract_blocks()` was factored out of that file's `grade()`
(additive edit, same file, same algorithm) so this script calls it instead of re-deriving block
extraction from scratch.

THE TWO GRADES
--------------
  BOUNDED     the block names what was searched: a path, a glob, a command, a file count, or a
              named store/venue (Task Scheduler, GitHub, history.jsonl, a corpus, ...).
  UNBOUNDED   an absence is asserted with NO population named anywhere in the block. THIS IS THE
              FINDING -- the exact shape of the mirror-job night: a confident negative with no
              stated scope, indistinguishable on the page from a negative that covers everything.

  absence_claims.py [--paths P [P ...]] [--repo R] [--self-test]
  exit 0 clean (all BOUNDED, at least one claim graded)
  exit 1 any UNBOUNDED claim found
  exit 2 unreadable input, or ZERO claims found (a pattern-list defect is UNKNOWN, never clean)
"""
import argparse
import io
import os
import re
import subprocess
import sys

# cp1252 guard -- this exact bug shipped twice in this repo in the last four hours per the dispatch.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import finding_consequence as fc  # noqa: E402  -- consumed for extract_blocks(), not re-derived

DEFAULT_SCAN = ["wiki", "exchange", "scripts", "GATES.md"]
SCAN_EXTS = (".md", ".txt", ".py", ".sh", ".ps1")

# Seed list from the dispatch, widened only by reading real hits (per instruction 1), not by
# guessing further phrasings past what those hits actually contained.
#
# ⛔ NARROWED 2026-09-05 (FRAME2-precision) after a 40-hit hand-graded sample of the first real run
# (310 UNBOUNDED) put precision at 7/40 = 17.5%. Bare `absent` alone accounted for 28/40 sampled
# hits at 1/28 = 3.6% precision -- it fires on adjectival/compound/definitional/table-field uses
# ("constitution-absent models", "*absent* row", "probe_sealed absent", "an absent one", "'absent'
# means absent from top-6") that are not narrative absence CLAIMS at all. The one construction that
# kept real signal was "absent FROM <referent>" (2/2 in-sample: "absent from the export", "absent
# from this raw"), so bare `absent` is dropped and only `absent\s+from` survives as a trigger.
# See the per-pattern precision table in the FRAME2-precision report for the full breakdown.
ABSENCE = re.compile(
    r"\b("
    r"not\s+found"
    r"|no\s+hits?"
    r"|0\s+hits?"
    r"|zero\s+hits?"
    r"|nothing\s+found"
    r"|does\s+not\s+exist"
    r"|no\s+such"
    r"|returns?\s+nothing"
    r"|no\s+primary"
    r"|absent\s+from"
    r"|no\s+results?"
    r"|could\s+not\s+find"
    r"|unable\s+to\s+find"
    r"|no\s+matches?"
    r"|never\s+found"
    r"|not\s+present"
    r"|no\s+evidence\s+of"
    r"|no\s+record\s+of"
    r"|no\s+occurrences?"
    r")\b",
    re.IGNORECASE,
)

# ⚠️ NEGATIVE-CONTROL GUARD: prose quoting/discussing the absence-claim RULE ITSELF, rather than
# asserting an absence found in a real search. A static detector cannot tell "I searched and found
# nothing" from "the rule says don't write 'not found'" except by these structural landmarks. This
# is a heuristic, named as one -- see the BOUND line in main().
# ⛔ WIDENED 2026-09-05 (FRAME2-precision): `means? absent` catches the definitional construction
# measured in-sample -- '"absent" means absent from top-6' -- where the trigger phrase is present
# but the block is defining the term, not asserting a finding.
META_QUOTE = re.compile(
    r"\b(before writing|e\.g\.|for example|the rule (says|states)|quoting|as an example"
    r"|means?\s+absent)\b",
    re.IGNORECASE,
)

# ⛔ ADDED 2026-09-05 (FRAME2-precision), measured against the same sample:
#
#  TABLE_ROW    a markdown table row (`| cell | cell |`). The instruction set's own FP taxonomy
#               names "a table cell" explicitly; in-sample every table-row hit (8/8) was a FALSE
#               POSITIVE (structured per-item audit output, not a narrative claim) -- and the one
#               table row that DID name a real path (`A:\Bkp2\...\CuteWriter.exe | ABSENT |`) is
#               already unambiguous from its own cell, so losing it from the count costs nothing.
#  LEDGER_TMPL  the literal `probe_sealed absent (accepted as given` template string. It is a fixed,
#               machine-generated pipeline-metadata field (verified: 475 occurrences across
#               wiki/skills-gate/**, every one byte-identical in shape) -- never a free-text claim.
#               It alone produced 156/310 = 50% of the FIRST run's raw UNBOUNDED count.
#  QUOTED       the trigger phrase's only occurrence in the block is inside a quotation (a quoted
#               error string, a "[FOUND-VERBATIM] '...'" citation, or a changelog bug description).
#               These are the AUTHOR REPORTING SOMEONE/SOMETHING ELSE'S TEXT, not asserting an
#               absence themselves. In-sample: 4/4 such hits were FALSE POSITIVES.
TABLE_ROW = None  # detected via the snippet (first line), not a compiled pattern -- see grade_file
LEDGER_TMPL = re.compile(r"probe_sealed\s+absent\s*\(accepted as given", re.IGNORECASE)
QUOTE_SPAN = re.compile(
    r'"[^"]*"'
    r'|\u201c[^\u201d]*\u201d'
    r"|'[A-Z][^']{3,100}[.!?]'"  # a single-quoted FULL SENTENCE (cap start, terminal punct) --
    # deliberately narrow so it does not eat ordinary apostrophes/contractions ("prompt's", "Jon's")
)


def is_quoted_only(joined):
    """True if every ABSENCE match in `joined` falls inside a quoted span -- i.e. the writer is
    citing/quoting text (an error string, a verbatim excerpt), not asserting an absence themselves."""
    dequoted = QUOTE_SPAN.sub(" ", joined)
    return not ABSENCE.search(dequoted)

# --- BOUND signals: any one of these inside the block counts as "named its population" ---
PATH_HINT = re.compile(
    r"\b[\w.\-]+/[\w.\-/]+\.[A-Za-z0-9]{1,6}\b"          # a/b/c.ext
    r"|\b[\w-]+\.(md|py|sh|ps1|jsonl?|json|txt|log|yml|yaml|csv|js|ts|bat|cmd)\b",
    re.IGNORECASE,
)
GLOB_HINT = re.compile(r"\*\.[A-Za-z0-9]{1,6}|\*\*")
BACKTICK_HINT = re.compile(r"`[^`]+`")
COUNT_HINT = re.compile(
    r"\b\d[\d,]*\s+"
    r"(files?|hits?|results?|matches?|lines?|entries|rows?|records?|jsonls?|conversations?"
    r"|sessions?|transcripts?|repos?|paths?|dirs?|directories)\b",
    re.IGNORECASE,
)
COMMAND_HINT = re.compile(
    r"\b(grep|rg|findstr|robocopy|schtasks|tasklist|Get-ChildItem|Select-String|sqlite3"
    r"|git\s+(log|grep|diff)|curl|find\s)\b",
    re.IGNORECASE,
)
VENUE_HINT = re.compile(
    r"\b(Task Scheduler|GitHub(?:\s+Actions|\s+Issues)?|Google Drive|history\.jsonl|GATES\.md"
    r"|corpus|ledger ?[.]?\w*|registry|the wiki|wiki/|exchange/|scripts/|raw/|\bJSONLs?\b"
    r"|Task Manager|Event Viewer|the repo|this repo|working tree)\b",
    re.IGNORECASE,
)
BOUND_SIGNALS = [PATH_HINT, GLOB_HINT, BACKTICK_HINT, COUNT_HINT, COMMAND_HINT, VENUE_HINT]


def is_bounded(block_text):
    return any(p.search(block_text) for p in BOUND_SIGNALS)


def iter_scan_files(repo, scan_targets):
    """Yield absolute file paths under the given repo-relative scan targets (files or dirs)."""
    for rel in scan_targets:
        full = os.path.join(repo, rel)
        if os.path.isfile(full):
            yield full
            continue
        if not os.path.isdir(full):
            continue
        for dirpath, dirnames, filenames in os.walk(full):
            # skip vcs internals and obvious noise directories
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__")]
            # ⛔ NARROWED 2026-09-05 (FRAME2-precision): wiki/references/claude-code/ is a mirrored
            # third-party product changelog/doc set (Claude Code's own release notes), never CFL/Jon
            # prose asserting a search result. Measured 3/3 hits there were FALSE POSITIVES ("Fixed
            # slash commands not found...", "Removed support ... Search returns no results...", a
            # docs link reading "not found in the marketplace") -- release-note descriptions of
            # user-facing bugs, not first-person absence claims.
            norm = dirpath.replace("\\", "/")
            if "/wiki/references/claude-code" in norm or norm.endswith("wiki/references/claude-code"):
                continue
            for fn in filenames:
                if fn.lower().endswith(SCAN_EXTS):
                    yield os.path.join(dirpath, fn)


def grade_file(path):
    """-> list of (line_no, grade, snippet) for absence-claim blocks in this file.
    grade is one of BOUNDED / UNBOUNDED. Blocks matching META_QUOTE are skipped (negative control:
    they mention absence but do not assert one)."""
    try:
        text = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None  # unreadable -- caller treats as UNKNOWN, not zero
    rows = []
    for line_no, joined, snippet in fc.extract_blocks(text, ABSENCE):
        if META_QUOTE.search(joined):
            continue
        if snippet.lstrip().startswith("|"):  # TABLE_ROW guard, see comment above
            continue
        if LEDGER_TMPL.search(joined):
            continue
        if is_quoted_only(joined):
            continue
        grade = "BOUNDED" if is_bounded(joined) else "UNBOUNDED"
        rows.append((line_no, grade, snippet))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="+", default=None,
                     help="repo-relative files/dirs to scan (default: %s)" % DEFAULT_SCAN)
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    scan_targets = a.paths if a.paths else DEFAULT_SCAN
    files = sorted(set(iter_scan_files(a.repo, scan_targets)))

    print("=== ABSENCE CLAIMS === before writing \"not found\", name the population searched")
    print("  repo  : %s" % os.path.abspath(a.repo))
    print("  scan  : %s (%d files)\n" % (", ".join(scan_targets), len(files)))

    total_bounded = 0
    total_unbounded = 0
    unbounded_hits = []
    unreadable = []

    for path in files:
        rows = grade_file(path)
        if rows is None:
            unreadable.append(path)
            continue
        for line_no, grade, snippet in rows:
            if grade == "BOUNDED":
                total_bounded += 1
            else:
                total_unbounded += 1
                unbounded_hits.append((path, line_no, snippet))

    total = total_bounded + total_unbounded

    if unreadable:
        print("  ⚠️ %d file(s) UNREADABLE (encoding/permission) -- excluded from the count below, "
              "not folded into a clean total:" % len(unreadable))
        for p in unreadable[:10]:
            print("      %s" % os.path.relpath(p, a.repo))

    if total == 0:
        print("  ⚠️ ZERO ABSENCE CLAIMS MATCHED across %d file(s). That is UNKNOWN, not clean -- "
              "either this repo currently has none, or this run's phrase list is a defect. Do not "
              "report it green without checking a known-positive by hand." % len(files))
        return 2

    print("  BOUNDED   : %d" % total_bounded)
    print("  UNBOUNDED : %d" % total_unbounded)
    print("  total     : %d\n" % total)

    if unbounded_hits:
        print("  ⛔ UNBOUNDED absence claims (no population named):")
        for p, ln, snippet in unbounded_hits:
            print("    %s:%d  %s" % (os.path.relpath(p, a.repo), ln, snippet))

    print("\n  ⚠️ BOUND: this checks only whether A population is NAMED in the block. It cannot "
          "check whether the named population was the RIGHT one -- a block that greps the wrong "
          "directory and finds nothing grades BOUNDED here, same as the mirror-job night graded "
          "'correct, empty' before anyone asked whether Task Scheduler could have held the job at "
          "all. It also does not enforce the dispatch's second half -- naming a population that was "
          "NOT searched -- because no static check can verify a search that did not happen.")

    return 1 if total_unbounded else 0


def self_test():
    import tempfile
    print("=== SELF-TEST -- absence_claims ===")
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

    bounded_text = (
        "- Checked Task Scheduler for the mirror job: not found, empty, 0 tasks registered.\n"
        "- Both drives grepped for robocopy in *.bat/*.cmd/*.ps1/*.sh: no hits.\n"
    )
    rows = grade_file_from_text(bounded_text)
    ok("1 a claim naming a venue + glob -> BOUNDED",
       [g for _, g, _ in rows], ["BOUNDED", "BOUNDED"])

    unbounded_text = "- We looked everywhere for the daemon. Not found.\n"
    rows2 = grade_file_from_text(unbounded_text)
    ok("2 THE POINT: an absence claim with no named population -> UNBOUNDED",
       [g for _, g, _ in rows2], ["UNBOUNDED"])

    negative_text = (
        '- The rule says: before writing "not found", name the population searched.\n'
    )
    rows3 = grade_file_from_text(negative_text)
    ok("3 CONTROL: quoting the rule itself is not a claim -> 0 rows",
       len(rows3), 0)

    bounded_count_text = "- Searched the corpus, 2206 files, no matches.\n"
    rows4 = grade_file_from_text(bounded_count_text)
    ok("4 a file-count population -> BOUNDED",
       rows4[0][1], "BOUNDED")

    path_text = "- Read wiki/tracker/wayfinder-cfl.md: no such ticket.\n"
    rows5 = grade_file_from_text(path_text)
    ok("5 a path population -> BOUNDED",
       rows5[0][1], "BOUNDED")

    no_disposition_text = "- The sky is blue today and nothing about search happened here.\n"
    rows6 = grade_file_from_text(no_disposition_text)
    ok("6 CONTROL: a bullet with no absence phrase is not a row at all",
       len(rows6), 0)

    # ⛔ FOLD-IN CASE, coordinator 2026-09-05: real files with numbered lists scanned as 0 rows
    # until extract_blocks() learned ROWNUM. Prove absence_claims.py inherits the fix via fc.
    numbered_text = "1. We searched the ledger. Not found, no matches.\n"
    rows7 = grade_file_from_text(numbered_text)
    ok("6b FOLD-IN: a numbered row is a row (not invisible, not swallowed)",
       len(rows7), 1)

    # ⛔ ENTRY-POINT CASE, per the dispatch: a program that dies on invocation stays undetected by
    # function-only tests. Run it for real.
    scan_dir = os.path.join(repo, "wiki")
    os.makedirs(scan_dir)
    io.open(os.path.join(scan_dir, "unbounded.md"), "w", encoding="utf-8").write(
        "- We looked everywhere. Not found.\n"
    )
    r = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--repo", repo, "--paths", "wiki"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    ok("7 ENTRY POINT RUNS and exits 1 on an unbounded claim",
       (r.returncode, "UNBOUNDED" in r.stdout), (1, True))
    if r.returncode not in (0, 1, 2):
        print("        child stderr tail: %s" % (r.stderr.strip().splitlines() or ["(none)"])[-1][:160])

    # 8 POSITIVE CONTROL: an all-bounded scan exits 0
    scan_dir2 = os.path.join(repo, "wiki2")
    os.makedirs(scan_dir2)
    io.open(os.path.join(scan_dir2, "bounded.md"), "w", encoding="utf-8").write(
        "- Grepped `scripts/audit/*.py` for the pattern: no hits.\n"
    )
    r2 = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--repo", repo, "--paths", "wiki2"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    ok("8 CONTROL: an all-bounded scan exits 0", r2.returncode, 0)

    # 9 zero population -> exit 2 UNKNOWN, never a clean 0
    scan_dir3 = os.path.join(repo, "wiki3")
    os.makedirs(scan_dir3)
    io.open(os.path.join(scan_dir3, "irrelevant.md"), "w", encoding="utf-8").write(
        "Nothing to see here, just prose with no bullets.\n"
    )
    r3 = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--repo", repo, "--paths", "wiki3"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    ok("9 zero claims matched -> exit 2 UNKNOWN, never clean", r3.returncode, 2)

    # ⛔ FRAME2-precision cases, 2026-09-05 -- one per narrowing, so a regression can't slip back in.

    # 10 NARROWING: bare "absent" (no "from") is no longer a trigger at all -- these are the
    # exact FP shapes measured in-sample: compound adjective, prenominal, conditional, negation.
    bare_absent_text = (
        "- constitution-absent models provide an ablation baseline.\n"
        "- Windows: when absent, Claude Code uses PowerShell as the shell tool.\n"
        "- Residue, once: memory makes COI auditable, not absent.\n"
    )
    rows10 = grade_file_from_text(bare_absent_text)
    ok("10 NARROWING: bare 'absent' (no 'from') no longer matches at all",
       len(rows10), 0)

    # 11 bare "absent" still doesn't fire even inside a real bullet with other absence language
    # absent -- but "absent FROM <referent>" still does, and still grades UNBOUNDED when the
    # referent alone isn't a recognized BOUND signal (venue/path/glob/count/command).
    absent_from_text = "- Referenced workbooks are absent from the export.\n"
    rows11 = grade_file_from_text(absent_from_text)
    ok("11 'absent from <referent>' still triggers and grades UNBOUNDED",
       [g for _, g, _ in rows11], ["UNBOUNDED"])

    # 12 NARROWING: the definitional "X means absent" construction is a META_QUOTE skip, not a claim.
    definitional_text = '- Graded from top-k=6; "absent" means absent from top-6.\n'
    rows12 = grade_file_from_text(definitional_text)
    ok("12 NARROWING: definitional 'means absent' is a meta-quote skip, not a claim",
       len(rows12), 0)

    # 13 NARROWING: TABLE_ROW guard -- a markdown table cell reading ABSENT is not a prose claim,
    # even when the row also names a full path (the path is unambiguous on its own; this guard
    # trades that one recoverable case for killing every other table-cell false positive measured).
    table_row_text = "| A:\\Bkp2\\Schroeder\\Downloads\\CuteWriter.exe | ABSENT |\n"
    rows13 = grade_file_from_text(table_row_text)
    ok("13 NARROWING: a markdown table row is skipped, not graded",
       len(rows13), 0)

    # 14 NARROWING: LEDGER_TMPL guard -- the fixed INGEST-LEDGER probe_sealed boilerplate (measured
    # at 156/310 = 50% of the first real run's raw UNBOUNDED count, 475 occurrences repo-wide, every
    # one byte-identical in shape) is a machine-generated metadata field, never a free-text claim.
    ledger_text = ("- probe: probe_sealed absent (accepted as given, per lane instructions "
                   "-- frontmatter always precedes body); --probe-verdict TRUSTED\n")
    rows14 = grade_file_from_text(ledger_text)
    ok("14 NARROWING: probe_sealed ledger boilerplate is skipped, not graded",
       len(rows14), 0)

    # 15 NARROWING: QUOTED guard -- the trigger phrase's only occurrence is inside a quoted error
    # string / verbatim citation; the author is reporting someone/something else's text, not
    # asserting an absence of their own.
    quoted_text = (
        '* Fixed plugins showing "not found in marketplace" errors on fresh startup.\n'
    )
    rows15 = grade_file_from_text(quoted_text)
    ok("15 NARROWING: a quoted error string is skipped, not graded",
       len(rows15), 0)

    # 16 CONTROL: the QUOTED guard must not eat a real claim that merely CONTAINS a quote elsewhere
    # in the block -- only when the trigger phrase itself has no unquoted occurrence.
    quote_elsewhere_text = (
        '- T126 ("I 100% refuse to apply ANY gates...") -- not present anywhere in the '
        "reproduced slice text.\n"
    )
    rows16 = grade_file_from_text(quote_elsewhere_text)
    ok("16 CONTROL: a claim with an unrelated quote elsewhere still grades UNBOUNDED",
       [g for _, g, _ in rows16], ["UNBOUNDED"])

    # 17 NARROWING: wiki/references/claude-code/ (mirrored product changelog/docs) is excluded from
    # the scan entirely -- measured 3/3 FALSE POSITIVE there (release-note bug descriptions, not
    # first-person absence claims). Uses its own isolated repo so test 7's unbounded.md (also under
    # "wiki/") can't leak in and mask the result.
    repo2 = tempfile.mkdtemp()
    scan_dir4 = os.path.join(repo2, "wiki", "references", "claude-code")
    os.makedirs(scan_dir4)
    io.open(os.path.join(scan_dir4, "changelog.md"), "w", encoding="utf-8").write(
        "* Fixed slash commands not found when typing the exact name of a soft-hidden command\n"
    )
    r4 = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--repo", repo2, "--paths", "wiki"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    ok("17 NARROWING: wiki/references/claude-code/ excluded -> zero claims from it (exit 2, "
       "not falsely clean and not falsely flagged)", r4.returncode, 2)

    print("  %d passed, %d failed" % (np, nf))
    return 0 if nf == 0 else 1


def grade_file_from_text(text):
    """Test helper: run the block-extraction + grading pipeline over an in-memory string, so
    self-test cases don't each need their own temp file."""
    rows = []
    for line_no, joined, snippet in fc.extract_blocks(text, ABSENCE):
        if META_QUOTE.search(joined):
            continue
        if snippet.lstrip().startswith("|"):
            continue
        if LEDGER_TMPL.search(joined):
            continue
        if is_quoted_only(joined):
            continue
        grade = "BOUNDED" if is_bounded(joined) else "UNBOUNDED"
        rows.append((line_no, grade, snippet))
    return rows


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
