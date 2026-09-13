#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lint_work_claims.py -- unlazy's CHECK/EXPECT oracle shape applied to WORK-CLAIMS DONE rows.

Origin: Jon's inline PR-252 question on the WORK-CLAIMS glossary entry, verbatim:
"How should unlazy be used in this context?" (sitting docket row 13,
wiki/intake-triage/SITTING-DOCKET-jons-glossary-questions-2026-08-29.md). The docket's
partial answer: a DONE row in exchange/WORK-CLAIMS.md is a promise in past tense.
unlazy's rule (skills/unlazy/SKILL.md, "Author gates that can fail honestly") is that a
checker proves only the declared command oracle -- it cannot infer whether an English
gate title describes what the command actually measures, and a `CHECK:` that can never
fail is worthless (gate-lint.mjs exists precisely to catch that at authoring time).
This script is the WORK-CLAIMS analogue of gate-lint: for every DONE row it asks
"does the pointer column carry or resolve to something a machine can independently
re-check" -- a file that exists, a commit that exists, a URL -- or is the row PURE
ASSERTION (prose with nothing behind it a script can re-run).

This is NOT gate-lint itself and does not claim DONE rows use CHECK:/EXPECT: syntax --
they don't. It borrows the SHAPE: an oracle must be re-runnable by someone other than
the row's author, or it isn't verification, it's a promise.

Classification per DONE row's pointer field:
  VERIFIED-FILE    pointer names a repo-relative path that exists on disk right now.
  VERIFIED-COMMIT  pointer contains a 7-40 char hex token that `git cat-file -e` finds.
  UNVERIFIED-URL   pointer contains an http(s) URL -- format-checkable, not fetched by
                   default (no oracle re-run without network; flagged, not failed).
  SELF-REF-ONLY    pointer is "this commit" (or a trivial variant) with no other
                   identifiable file/hash -- ambiguous by the time this script runs;
                   which commit is not recoverable from the row alone.
  ASSERTION-ONLY   pointer is prose with nothing a script can independently re-check.
  PARSE-ERROR      the row did not split into the 5 expected table columns, or verb
                   was not one of TAKE/DONE/RELEASE/NOTE in the expected position.
                   Fail-closed: a row this script cannot parse is reported, never
                   silently skipped and never silently counted as passing.

Known false-positive/false-negative directions on THIS FIRST RUN (first-run numbers
are hypotheses, not conclusions -- see MEMORY feedback_first-run-numbers-are-hypotheses):
  - OVER-counts ASSERTION-ONLY: a pointer like "letter + script in this commit" DOES
    name "script" but not a resolvable path, so it falls to SELF-REF-ONLY/ASSERTION
    even though a human reading the row plus its neighbours could resolve it via git
    log at that timestamp. This script does not attempt timestamp-to-commit inference
    (heuristic, not an oracle) -- so some legitimately-verifiable rows undercount as
    verified.
  - UNDER-counts ASSERTION-ONLY: a pointer naming a real file path that exists is
    counted VERIFIED-FILE even if that file does NOT actually contain evidence of the
    claimed work (existence is not correctness). This script checks EXISTENCE only,
    never CONTENT match to the claim -- so VERIFIED-FILE is a weak pass, not a strong
    one, and should be read as "at least the referent exists," never "the claim is true."
  - Markdown-table parsing is brittle to hand-edited rows with shifted columns (see the
    T-10 TAKE row 2026-08-28, which puts the verb in column 1 instead of column 3) --
    those are correctly caught as PARSE-ERROR here, but a differently-shifted row this
    script has not seen could parse into the wrong columns silently. No known instance
    of that in this corpus as of this run; flagged as a residual risk.

Usage:
  python scripts/audit/lint_work_claims.py
  python scripts/audit/lint_work_claims.py --file exchange/WORK-CLAIMS.md
  python scripts/audit/lint_work_claims.py --self-test

Windows-Python note: this file takes its target path as argv (--file), never builds a
POSIX path inside a -c string -- see MEMORY reference_posix-path-inline-vs-argv-python-trap.
"""

import argparse
import io
import os
import re
import subprocess
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DEFAULT_TARGET = os.path.join(REPO, "exchange", "WORK-CLAIMS.md")

VERBS = {"TAKE", "DONE", "RELEASE", "NOTE"}
HEX_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
URL_RE = re.compile(r"https?://\S+")
# Repo-relative-looking path tokens: contains a slash, ends in a plausible extension,
# or is a bare known top-level dir prefix (exchange/, wiki/, scripts/, skills/, docs/).
PATH_TOKEN_RE = re.compile(
    r"(?:[A-Za-z0-9_.\-]+/)+[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,6}"
    r"|(?:exchange|wiki|scripts|skills|docs)/[A-Za-z0-9_.\-/]+"
)
SELF_REF_RE = re.compile(r"^\s*this\s+commit\s*\)?\s*$", re.IGNORECASE)


def read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="strict") as f:
        return f.read()


def parse_rows(text):
    """Yield (line_no, raw_line, status, fields) for every table data row.

    status is one of "ok" or "parse-error". Header and separator lines are skipped.
    Fail-closed: any row that looks like a table row (starts with '|') but does not
    split into exactly 5 non-empty-position fields with a recognizable verb is a
    parse-error, reported, never silently dropped.
    """
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if stripped.startswith("|---") or stripped.startswith("| ---"):
            continue
        if stripped.startswith("| at |") or stripped.startswith("|at|"):
            continue  # header
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) != 5:
            yield (i, line, "parse-error", cells)
            continue
        at, seat, verb, work_item, pointer = cells
        if verb not in VERBS:
            # Column-shifted row (e.g. verb in position 1). Do not guess which
            # column is which -- report and move on.
            yield (i, line, "parse-error", cells)
            continue
        yield (i, line, "ok", {
            "at": at, "seat": seat, "verb": verb,
            "work_item": work_item, "pointer": pointer,
        })


def git_commit_exists(token):
    try:
        r = subprocess.run(
            ["git", "cat-file", "-e", token + "^{commit}"],
            cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return r.returncode == 0
    except OSError:
        return False


def classify_pointer(pointer, repo_root):
    """Return (classification, evidence_str)."""
    if SELF_REF_RE.match(pointer):
        return ("SELF-REF-ONLY", "pointer is bare 'this commit' with no other locatable reference")

    path_matches = PATH_TOKEN_RE.findall(pointer)
    for candidate in path_matches:
        cand_norm = candidate.strip().rstrip(").,;:")
        full = os.path.normpath(os.path.join(repo_root, cand_norm))
        if os.path.commonpath([os.path.normpath(repo_root), full]) != os.path.normpath(repo_root):
            continue  # path escapes repo root, refuse to trust it
        if os.path.isfile(full) or os.path.isdir(full):
            return ("VERIFIED-FILE", "exists: " + cand_norm)

    hex_matches = HEX_RE.findall(pointer)
    for h in hex_matches:
        if len(h) >= 7 and git_commit_exists(h):
            return ("VERIFIED-COMMIT", "git cat-file -e found commit " + h)

    url_matches = URL_RE.findall(pointer)
    if url_matches:
        return ("UNVERIFIED-URL", "format-checkable only, not fetched: " + url_matches[0])

    if path_matches or hex_matches:
        # Named something path/hash-shaped but none of it resolved.
        return ("ASSERTION-ONLY", "path/hash-shaped token present but did not resolve: " + pointer)

    return ("ASSERTION-ONLY", "no file, commit, or URL reference in pointer")


def lint(target_path):
    text = read_text(target_path)
    results = []
    for line_no, raw, status, fields in parse_rows(text):
        if status == "parse-error":
            results.append({
                "line": line_no, "verb": None, "classification": "PARSE-ERROR",
                "evidence": "row did not parse into 5 recognized columns: " + repr(fields),
                "pointer": None, "work_item": None, "raw": raw.strip(),
            })
            continue
        if fields["verb"] != "DONE":
            continue
        classification, evidence = classify_pointer(fields["pointer"], REPO)
        results.append({
            "line": line_no, "verb": "DONE", "classification": classification,
            "evidence": evidence, "pointer": fields["pointer"],
            "work_item": fields["work_item"], "raw": raw.strip(),
        })
    return results


def summarize(results):
    done_rows = [r for r in results if r["verb"] == "DONE"]
    parse_errors = [r for r in results if r["classification"] == "PARSE-ERROR"]
    by_class = {}
    for r in done_rows:
        by_class.setdefault(r["classification"], []).append(r)
    assertion_only = by_class.get("ASSERTION-ONLY", []) + by_class.get("SELF-REF-ONLY", [])
    return done_rows, parse_errors, by_class, assertion_only


def print_report(results, target_path):
    done_rows, parse_errors, by_class, assertion_only = summarize(results)
    print("lint_work_claims.py -- target: %s" % target_path)
    print("DONE rows scanned: %d" % len(done_rows))
    print("Parse errors (fail-closed, reported not skipped): %d" % len(parse_errors))
    for pe in parse_errors:
        print("  PARSE-ERROR line %d: %s" % (pe["line"], pe["evidence"]))
    print("")
    print("Classification breakdown:")
    for cls in sorted(by_class.keys()):
        print("  %-16s %d" % (cls, len(by_class[cls])))
    print("")
    print("Assertion-only (ASSERTION-ONLY + SELF-REF-ONLY) DONE rows: %d / %d" %
          (len(assertion_only), len(done_rows)))
    for r in assertion_only:
        wi = (r["work_item"] or "")[:70]
        print("  line %d [%s]: %s | pointer=%r" % (r["line"], r["classification"], wi, r["pointer"]))
    return done_rows, parse_errors, assertion_only


# ---------------------------------------------------------------------------
# Self-test: one positive control (known-verifiable DONE row) and one negative
# control (synthetic assertion-only DONE row), run against a fixture, never
# against the live ledger, so the self-test result cannot drift with the ledger.
# ---------------------------------------------------------------------------

POSITIVE_CONTROL_ROW = (
    "| 2026-08-18T20:22:45-0500 | 643640a7/fable | DONE | "
    "V2 seat-addressability + work-claims design (due 08-19) | "
    "exchange/V2-SEAT-ADDRESSABILITY-AND-WORK-CLAIMS-2026-08-18.md |"
)
# This exact row is real (exchange/WORK-CLAIMS.md line 19) and its pointer names a
# file this repo actually carries -- verified by hand before wiring the control.

NEGATIVE_CONTROL_ROW = (
    "| 2026-08-29T00:00:00-0500 | synthetic/self-test | DONE | "
    "synthetic negative control -- must be flagged | trust me it is done |"
)

MALFORMED_CONTROL_ROW = (
    "| TAKE | 2026-08-29T00:00:01-0500 | synthetic | shifted columns must fail closed |"
)


def self_test():
    fixture = "\n".join([
        "| at | seat | verb | work item | pointer |",
        "|---|---|---|---|---|",
        POSITIVE_CONTROL_ROW,
        NEGATIVE_CONTROL_ROW,
        MALFORMED_CONTROL_ROW,
    ])
    tmp_path = os.path.join(REPO, "scripts", "audit", "_lint_work_claims_selftest_fixture.md")
    with io.open(tmp_path, "w", encoding="utf-8") as f:
        f.write(fixture)
    try:
        text = read_text(tmp_path)
        results = list(parse_rows(text))
        ok_rows = [(i, r, s, f) for (i, r, s, f) in results]

        pos_result = None
        neg_result = None
        parse_error_seen = False
        for line_no, raw, status, fields in ok_rows:
            if status == "parse-error":
                parse_error_seen = True
                continue
            if fields["verb"] != "DONE":
                continue
            cls, ev = classify_pointer(fields["pointer"], REPO)
            if "V2-SEAT-ADDRESSABILITY" in fields["pointer"]:
                pos_result = cls
            elif "trust me" in fields["pointer"]:
                neg_result = cls

        pos_pass = pos_result == "VERIFIED-FILE"
        neg_pass = neg_result == "ASSERTION-ONLY"
        malformed_pass = parse_error_seen

        print("SELF-TEST")
        print("  positive control (real file pointer)  -> %-14s expected VERIFIED-FILE   %s" %
              (pos_result, "PASS" if pos_pass else "FAIL"))
        print("  negative control (prose-only pointer)  -> %-14s expected ASSERTION-ONLY %s" %
              (neg_result, "PASS" if neg_pass else "FAIL"))
        print("  malformed control (shifted columns)    -> parse-error seen=%-5s expected True     %s" %
              (parse_error_seen, "PASS" if malformed_pass else "FAIL"))

        overall = pos_pass and neg_pass and malformed_pass
        print("SELF-TEST OVERALL: %s" % ("PASS" if overall else "FAIL"))
        return overall
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT_TARGET,
                     help="path to a WORK-CLAIMS.md-shaped ledger (default: exchange/WORK-CLAIMS.md)")
    ap.add_argument("--self-test", action="store_true",
                     help="run the fixture-based positive/negative/malformed controls and exit")
    args = ap.parse_args()

    if args.self_test:
        ok = self_test()
        sys.exit(0 if ok else 1)

    if not os.path.isfile(args.file):
        print("FAIL-CLOSED: target file does not exist: %s" % args.file)
        sys.exit(2)

    try:
        results = lint(args.file)
    except UnicodeDecodeError as e:
        print("FAIL-CLOSED: could not decode %s as UTF-8: %s" % (args.file, e))
        sys.exit(2)

    done_rows, parse_errors, assertion_only = print_report(results, args.file)
    # Exit nonzero if there were unreported-parse-error rows or any assertion-only
    # DONE rows, so this can be wired into a gate later without changes.
    sys.exit(0 if (not parse_errors and not assertion_only) else 1)


if __name__ == "__main__":
    main()
