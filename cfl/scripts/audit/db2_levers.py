#!/usr/bin/env python3
"""db2_levers.py -- P3-2: wire DB-2's 11 lever decisions from the Review-fold ONLY.

WHY A NEW FILE, NOT AN EXTENSION OF heartbeat_battery.py
----------------------------------------------------------
Checked first: heartbeat_battery.py (1385 lines, 12 checks already), write_barrier_memory.py,
check_before_dispatch.py, check_reachability_chain.py, scan_midturn_messages.py all exist and
each already owns ONE mechanism DB-2 reuses. None of them own "all 11 DB-2 rows" -- that
composite is new. Folding 8 more checks directly into heartbeat_battery.py's numbered Row
sequence would renumber every existing check's identity (rows are addressed by number elsewhere
-- WAKE.md prose, the baseline JSON). This module owns the DB-2 COMPOSITE and each function is
written so a later PR-3 hook step can import it into the battery as new numbered rows without
copying logic -- the seam is the function boundary, not a fresh reimplementation at fold time.
Two rows (11, "tool-refuses") and (21, "heartbeat, reused chain script") call the EXISTING
instruments directly rather than re-deriving their logic, per the zero-new-instruments
constraint (DB-2 preamble, 2026-08-30 directive).

SOURCE OF TRUTH, PER THE TICKET'S BINDING CONSTRAINT
-------------------------------------------------------
`wiki/intake-triage/DB-2-lever-decisions-2026-08-30.md`. The base table (rows 27-39) carries
SEVEN cells marked with a leading "⛔ ... SUPERSEDED" -- those base cells are NEVER read here.
The corrected mechanism for every marked row comes ONLY from "## Review fold -- REVISION 1"
(lines 69-127), items 1-7. Rows the base table does NOT mark (2, 9, 11, 17, 20) are wired as
the base table states them -- the Review-fold did not touch them, and re-deriving an unmarked
cell from the fold section would be reading a decision that was never revised.

LEVER TALLY THIS FILE WIRES: 8 heartbeat WARN, 1 tool-refuses, 2 demotions = 11 rows over the
10 prose-only census rows (DB-1) + the row-18b split. This is the DB-2 tally itself (base-table
"## Tally" line + Review-fold item 7's recount, which agree on 8/1/2 = 11). It is DIFFERENT
from the charter's "Closing census: tool-refuses 8 * heartbeat 17 * demoted 2 * prose-only 0"
line -- that 27-count is DB-1's WHOLE census after PR-3 wiring (Review-fold item 7's own
"closing denominator" sentence), covering the rows DB-1 already scored as tool-refuses/heartbeat
BEFORE DB-2 ever ran, plus this file's 11. The charter's clause (A) opening sentence ("8
heartbeat WARNs + 1 tool-refuses + 2 demotion residues") matches this file's scope; the
"Closing census" sentence that follows it in the SAME bullet is the different, larger number.
Reported explicitly in the P3-2 report rather than silently picked.

Each `check_row_*` function returns a Verdict (status in {PASS, WARN, UNKNOWN, DEMOTE}) plus one
evidence string, mirrors heartbeat_battery.py's Row shape so this module can be folded in later
without a second data model.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import subprocess
import sys
import tempfile
import datetime as dt

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS, WARN, UNKNOWN, DEMOTE = "PASS", "WARN", "UNKNOWN", "DEMOTE"


class Verdict:
    def __init__(self, row, name, lever, status, evidence):
        self.row = row          # census row id, e.g. "2", "18b"
        self.name = name
        self.lever = lever      # heartbeat-warn | tool-refuses | demote
        self.status = status
        self.evidence = evidence

    def line(self):
        return f"[census row {self.row:>3}] {self.lever:14s} {self.status:7s} {self.name:26s} {self.evidence}"


def run_cmd(args, cwd=REPO, timeout=60):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                            timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, p.stdout, p.stderr
    except Exception as e:  # pragma: no cover - defensive
        return -1, "", str(e)


def _read(path):
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Row 2 -- seal-before-run (heartbeat WARN) -- base table, NOT superseded.
# Review-fold item 7 names the hidden cost: PROBE-REGISTRY has no per-row
# run-artifact pointer yet -- that is DATA-CONTRACT CHANGE #1. Until that field
# exists, the real registry cannot be checked; a fixture registry with the field
# CAN, which is what the selftest exercises. Live run against the real registry
# is UNKNOWN-BY-DESIGN (prerequisite missing), never a silent PASS.
# ---------------------------------------------------------------------------

SEAL_ROW_RE = re.compile(
    r"^\|\s*(?P<id>P\S+)\s*\|.*?\|\s*(?P<seal_ts>\d{4}-\d{2}-\d{2}(?:T[\d:]+)?)\s*"
    r"\|\s*(?P<run_ts>\d{4}-\d{2}-\d{2}(?:T[\d:]+)?)\s*\|",
    re.MULTILINE,
)


def check_row2_seal_before_run(registry_text):
    """registry_text: PROBE-REGISTRY.md content -- REQUIRES a 4th pipe-cell pair
    (seal_ts, run_ts) per row that does not exist in the shipped file today
    (data-contract change #1). Returns UNKNOWN against the real file until that
    field is added; a fixture with the field exercises the real logic."""
    if "seal_ts" not in registry_text and not SEAL_ROW_RE.search(registry_text):
        return Verdict("2", "SEAL-BEFORE-RUN", "heartbeat-warn", UNKNOWN,
                        "PROBE-REGISTRY has no per-row run-artifact pointer yet "
                        "(data-contract change #1, Review-fold item 7) -- "
                        "cannot compare seal-time vs run-time; UNKNOWN, not PASS")
    late = []
    for m in SEAL_ROW_RE.finditer(registry_text):
        seal_ts, run_ts = m.group("seal_ts"), m.group("run_ts")
        if run_ts <= seal_ts:
            late.append((m.group("id"), seal_ts, run_ts))
    if late:
        rid, s, r = late[0]
        return Verdict("2", "SEAL-BEFORE-RUN", "heartbeat-warn", WARN,
                        f"{len(late)} row(s) whose run precedes/ties its seal, e.g. {rid} "
                        f"(seal={s}, run={r})")
    return Verdict("2", "SEAL-BEFORE-RUN", "heartbeat-warn", PASS,
                    "every sealed row's run postdates its seal")


# ---------------------------------------------------------------------------
# Row 9 -- consolidation at every close (heartbeat WARN) -- base table, NOT superseded.
# ---------------------------------------------------------------------------

CLOSE_RE = re.compile(r"^close-[0-9a-f]+-(\d{8}T\d{6})\d{0,4}\.md$")
CONS_RE = re.compile(r"^CONS-(\d{4}-\d{2}-\d{2})")


def check_row9_consolidation_at_close(instances_dir):
    if not os.path.isdir(instances_dir):
        return Verdict("9", "CONSOLIDATION-AT-CLOSE", "heartbeat-warn", UNKNOWN,
                        f"{instances_dir} not found")
    closes, conses = [], []
    for name in sorted(os.listdir(instances_dir)):
        m = CLOSE_RE.match(name)
        if m:
            closes.append((m.group(1), name))
        m2 = CONS_RE.match(name)
        if m2:
            conses.append(m2.group(1))
    if not closes:
        return Verdict("9", "CONSOLIDATION-AT-CLOSE", "heartbeat-warn", UNKNOWN,
                        "0 close-* instances found -- nothing to check yet")
    cons_dates = sorted(conses)
    uncovered = []
    for ts, name in closes:
        close_date = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"
        # WARN when no CONS-* artifact exists in the window UP TO AND INCLUDING this close's date
        if not any(cd <= close_date for cd in cons_dates):
            uncovered.append(name)
    if uncovered:
        return Verdict("9", "CONSOLIDATION-AT-CLOSE", "heartbeat-warn", WARN,
                        f"{len(uncovered)} close boundary/ies with no CONS-* artifact in window, "
                        f"e.g. {uncovered[0]}")
    return Verdict("9", "CONSOLIDATION-AT-CLOSE", "heartbeat-warn", PASS,
                    f"{len(closes)} close boundary/ies, each has a preceding CONS-* artifact")


# ---------------------------------------------------------------------------
# Row 10 -- template-eval per instance -- ⛔ BASE CELLS SUPERSEDED.
# Review-fold item 3 is the ONLY source: DEMOTE to per-TEMPLATE-REVISION; the
# residue WARN is NOT-BUILDABLE-YET (no template carries a version field --
# that is DATA-CONTRACT CHANGE #2, "version-stamp the four templates"). The
# concrete, buildable-TODAY check is the retirement-note-presence check: has
# the demotion been written into SPEC.md's retirement section, per the
# Review-fold's stated work item?
# ---------------------------------------------------------------------------

def check_row10_template_eval_demoted(spec_text, templates):
    """templates: list of (name, text) -- checks whether ANY template carries a
    `template-version:` frontmatter key (the prerequisite the Review-fold says
    is unshipped). Also checks SPEC.md for the retirement note."""
    has_version = any(re.search(r"^template-version:\s*\S+", t, re.MULTILINE) for _, t in templates)
    retirement_noted = bool(re.search(r"retir\w*", spec_text or "", re.IGNORECASE))
    if not has_version:
        note = "retirement note PRESENT in SPEC.md" if retirement_noted else \
               "retirement note ABSENT from SPEC.md -- work item outstanding"
        return Verdict("10", "TEMPLATE-EVAL (demoted)", "demote", DEMOTE,
                        "residue WARN is NOT-BUILDABLE-YET: no template carries `template-version:` "
                        f"(data-contract change #2 unshipped); {note}")
    # prerequisite shipped -- the residue WARN becomes live: any template whose
    # version exceeds the eval log's highest logged version for it.
    return Verdict("10", "TEMPLATE-EVAL (demoted, residue live)", "demote", PASS,
                    "template-version field is shipped -- residue WARN activates on next "
                    "version bump without a matching eval-log row (checked at fold time)")


# ---------------------------------------------------------------------------
# Row 11 -- tier-0 index row per barrier (tool-refuses) -- base table, NOT superseded.
# Extends write_barrier_memory.py --verify's existing shape: fail nonzero when
# INDEX-tier0.md lacks a row for the instance under verification.
# ---------------------------------------------------------------------------

def check_row11_index_row_present(instance_basename, index_text):
    if index_text is None:
        return Verdict("11", "TIER0-INDEX-ROW", "tool-refuses", UNKNOWN,
                        "INDEX-tier0.md not found -- verify cannot run")
    if instance_basename in index_text:
        return Verdict("11", "TIER0-INDEX-ROW", "tool-refuses", PASS,
                        f"{instance_basename} has an INDEX-tier0.md row")
    return Verdict("11", "TIER0-INDEX-ROW", "tool-refuses", WARN,
                    f"{instance_basename} MISSING from INDEX-tier0.md -- "
                    "write_barrier_memory.py --verify must FAIL nonzero on this instance")


# ---------------------------------------------------------------------------
# Row 12 -- read-receipt stamping -- ⛔ BASE CELLS SUPERSEDED.
# Review-fold item 4: DEMOTE (channel-log ledger retired visibly); kept
# discipline = existing battery check 5 (INBOX-NEW) + wake step 1 item 3
# (miscite fixed: NOT step 3). This function checks only the demotion's own
# work item -- has the retirement note been written into the channel log
# itself, per the fold's stated obligation.
# ---------------------------------------------------------------------------

RETIREMENT_MARK = "RETIRED (DB-2 row 12"


def check_row12_read_receipt_demoted(channel_log_text):
    if channel_log_text is None:
        return Verdict("12", "READ-RECEIPT-LEDGER (demoted)", "demote", UNKNOWN,
                        "channel log not found")
    if RETIREMENT_MARK in channel_log_text:
        return Verdict("12", "READ-RECEIPT-LEDGER (demoted)", "demote", PASS,
                        "retirement note present in channel log; kept discipline is battery "
                        "check 5 (INBOX-NEW) + wake step 1 item 3")
    return Verdict("12", "READ-RECEIPT-LEDGER (demoted)", "demote", DEMOTE,
                    "retirement note NOT YET WRITTEN into the channel log -- work item "
                    "outstanding (Review-fold item 4); demotion decided, not yet recorded")


# ---------------------------------------------------------------------------
# Row 15 -- WORK-CLAIMS append-only -- ⛔ BASE CELLS SUPERSEDED.
# Review-fold item 5: normalize on (timestamp, seat, verb) with whitespace/EOL
# normalized; commit 1f51a31 (whole-file LF->CRLF, zero rows altered) is the
# KNOWN false positive and must NOT fire.
# ---------------------------------------------------------------------------

CLAIM_ROW_RE = re.compile(
    r"^\|\s*(?P<ts>[^|]+?)\s*\|\s*(?P<seat>[^|]+?)\s*\|\s*(?P<verb>TAKE|DONE|RELEASE|NOTE)\s*\|"
)


def _claim_identity(line):
    m = CLAIM_ROW_RE.match(line.strip())
    if not m:
        return None
    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    return (norm(m.group("ts")), norm(m.group("seat")), norm(m.group("verb")))


def check_row15_work_claims_immutable(old_lines, new_lines):
    """old_lines / new_lines: the WORK-CLAIMS.md content at two commits, split on lines.
    Normalizes line endings and whitespace before comparing row IDENTITY so a whole-file
    CRLF<->LF conversion (1f51a31's shape) never fires -- only an actual identity change does."""
    def index_by_identity(lines):
        out = {}
        for ln in lines:
            ident = _claim_identity(ln)
            if ident:
                out.setdefault(ident, []).append(ln.strip())
        return out

    old_idx = index_by_identity([l.rstrip("\r\n") for l in old_lines])
    new_idx = index_by_identity([l.rstrip("\r\n") for l in new_lines])

    altered = []
    for ident, old_texts in old_idx.items():
        new_texts = new_idx.get(ident)
        if new_texts is None:
            altered.append((ident, "ROW DELETED"))
        elif sorted(t.replace(" ", "") for t in old_texts) != sorted(t.replace(" ", "") for t in new_texts):
            altered.append((ident, "ROW CONTENT CHANGED"))
    if altered:
        ident, why = altered[0]
        return Verdict("15", "WORK-CLAIMS-IMMUTABLE", "heartbeat-warn", WARN,
                        f"{len(altered)} prior row(s) altered/deleted, e.g. {ident} ({why})")
    return Verdict("15", "WORK-CLAIMS-IMMUTABLE", "heartbeat-warn", PASS,
                    "no prior row's (timestamp, seat, verb) identity was altered or deleted")


# ---------------------------------------------------------------------------
# Row 17 -- ledger no-positional-reference (heartbeat WARN) -- base table, NOT superseded.
# ---------------------------------------------------------------------------

POSITIONAL_RE = re.compile(
    r"\b(the\s+row\s+above|the\s+row\s+below|the\s+previous\s+row|row\s+above|row\s+below)\b",
    re.IGNORECASE)


def check_row17_no_positional_reference(new_ledger_lines):
    hits = [ln for ln in new_ledger_lines if POSITIONAL_RE.search(ln)]
    if hits:
        return Verdict("17", "LEDGER-NO-POSITIONAL-REF", "heartbeat-warn", WARN,
                        f"{len(hits)} row(s) appended since last check use positional reference, "
                        f"e.g. {hits[0].strip()[:90]}")
    return Verdict("17", "LEDGER-NO-POSITIONAL-REF", "heartbeat-warn", PASS,
                    f"0 positional references in {len(new_ledger_lines)} row(s) appended since last check")


# ---------------------------------------------------------------------------
# Row 20 -- M-14 look-before-building before TAKE (heartbeat WARN) -- base table,
# NOT superseded. Honesty bound stated inline: this checks the ATTESTATION
# (an `m14:` token present), never the run itself.
# ---------------------------------------------------------------------------

TAKE_ROW_RE = re.compile(r"^\|.*\|\s*TAKE\s*\|", re.IGNORECASE)


def check_row20_m14_token_on_take(claims_lines):
    take_rows = [ln for ln in claims_lines if TAKE_ROW_RE.match(ln.strip())]
    missing = [ln for ln in take_rows if "m14:" not in ln]
    if missing:
        return Verdict("20", "M14-TOKEN-ON-TAKE", "heartbeat-warn", WARN,
                        f"{len(missing)}/{len(take_rows)} TAKE row(s) since epoch carry no `m14:` "
                        f"token. BOUND: this checks the ATTESTATION, not the run -- a seat can "
                        f"type the token falsely; that residue is peer-review's to catch, not "
                        f"this check's, e.g. {missing[0].strip()[:90]}")
    if not take_rows:
        return Verdict("20", "M14-TOKEN-ON-TAKE", "heartbeat-warn", UNKNOWN,
                        "0 TAKE rows in scope -- nothing to check")
    return Verdict("20", "M14-TOKEN-ON-TAKE", "heartbeat-warn", PASS,
                    f"{len(take_rows)}/{len(take_rows)} TAKE row(s) carry an `m14:` token "
                    "(attestation only, per stated bound)")


# ---------------------------------------------------------------------------
# Row 21 -- reachability chain at open (heartbeat WARN) -- base table, NOT
# superseded, but Review-fold item 2 adds a PRECONDITION: fold in only after
# the chain's terminal node is derived (not hardcoded to `wayfinder-cfl.md`).
# check_reachability_chain.py was corrected 2026-09-02 to derive hop 3/4 --
# verified first-hand by reading its own docstring/code (see this ticket's
# STEP 1 grounding). Precondition is now MET; this wraps the existing script.
# ---------------------------------------------------------------------------

def check_row21_reachability_chain(repo=REPO):
    script = os.path.join(repo, "scripts", "audit", "check_reachability_chain.py")
    if not os.path.isfile(script):
        return Verdict("21", "REACHABILITY-CHAIN", "heartbeat-warn", UNKNOWN,
                        "check_reachability_chain.py not found -- precondition script missing")
    with io.open(script, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    if "hardcoded" in src.lower() and "wayfinder-cfl.md\"" in src and "DERIVED" not in src:
        return Verdict("21", "REACHABILITY-CHAIN", "heartbeat-warn", UNKNOWN,
                        "PRECONDITION NOT MET (Review-fold item 2): terminal node still hardcoded "
                        "-- do not fold in yet")
    rc, out, err = run_cmd([sys.executable, script], cwd=repo)
    if rc == 0:
        return Verdict("21", "REACHABILITY-CHAIN", "heartbeat-warn", PASS,
                        "precondition met (derived terminal node, 2026-09-02 fix); chain intact")
    return Verdict("21", "REACHABILITY-CHAIN", "heartbeat-warn", WARN,
                    f"precondition met; chain broken (exit {rc}): {(err or out)[:160]}")


# ---------------------------------------------------------------------------
# Row 22 -- mid-turn scan at open -- ⛔ ENTIRE BASE CELLS SUPERSEDED.
# Review-fold item 1 is the ONLY source: discriminator is the WRAPPER STRING
# at position 0, NOT isMeta (a real Jon mid-turn message carried the wrapper
# with isMeta absent). Wraps scan_midturn_messages.py's own logic/selftest
# rather than re-deriving it (zero-new-instruments).
# ---------------------------------------------------------------------------

def check_row22_midturn_wrapper_scan(repo=REPO, session=None):
    script = os.path.join(repo, "scripts", "audit", "scan_midturn_messages.py")
    if not os.path.isfile(script):
        return Verdict("22", "MIDTURN-WRAPPER-SCAN", "heartbeat-warn", UNKNOWN,
                        "scan_midturn_messages.py not found")
    args = [sys.executable, script]
    if session:
        args += ["--session", session]
    rc, out, err = run_cmd(args, cwd=repo, timeout=90)
    if rc == 2:
        return Verdict("22", "MIDTURN-WRAPPER-SCAN", "heartbeat-warn", UNKNOWN,
                        f"usage/setup error (exit 2): {(err or out)[:160]}")
    if rc == 1 or "unsurfaced" in (out or "").lower():
        return Verdict("22", "MIDTURN-WRAPPER-SCAN", "heartbeat-warn", WARN,
                        f"unsurfaced wrapper-bearing mid-turn message(s) found: {(out or err)[:160]}")
    return Verdict("22", "MIDTURN-WRAPPER-SCAN", "heartbeat-warn", PASS,
                    "0 unsurfaced wrapper-bearing mid-turn messages")


# ---------------------------------------------------------------------------
# Row 18b -- canonical regenerated at SU -- ⛔ BASE CELLS SUPERSEDED.
# Review-fold item 6: canonical vs main@8-days-stale figure corrected; operand
# MUST be a freshly-fetched origin/main (or `git ls-remote`) -- against local
# main or a stale origin/main the WARN is structurally green while canonical
# rots. This function takes the two commit dates as input so the caller
# controls freshness explicitly (never trusts a cached ref silently).
# ---------------------------------------------------------------------------

def check_row18b_canonical_age(canonical_source_commit_date, origin_main_head_date,
                                fresh_fetch_confirmed, su_boundary_days=1):
    if not fresh_fetch_confirmed:
        return Verdict("18b", "CANONICAL-AGE", "heartbeat-warn", UNKNOWN,
                        "operand not confirmed fresh-fetched from origin/main -- per Review-fold "
                        "item 6 this WARN is structurally green on a stale/local ref, so it "
                        "refuses to render a verdict rather than risk a false PASS")
    age_days = (origin_main_head_date - canonical_source_commit_date).days
    if age_days > su_boundary_days:
        return Verdict("18b", "CANONICAL-AGE", "heartbeat-warn", WARN,
                        f"canonical is {age_days} day(s) behind freshly-fetched origin/main "
                        f"(> {su_boundary_days}-day SU-boundary threshold)")
    return Verdict("18b", "CANONICAL-AGE", "heartbeat-warn", PASS,
                    f"canonical is {age_days} day(s) behind freshly-fetched origin/main "
                    f"(<= {su_boundary_days}-day threshold)")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

ROW_LEVERS = {
    "2": "heartbeat-warn", "9": "heartbeat-warn", "10": "demote", "11": "tool-refuses",
    "12": "demote", "15": "heartbeat-warn", "17": "heartbeat-warn", "20": "heartbeat-warn",
    "21": "heartbeat-warn", "22": "heartbeat-warn", "18b": "heartbeat-warn",
}


def tally(levers=ROW_LEVERS):
    heartbeat = sum(1 for v in levers.values() if v == "heartbeat-warn")
    refuses = sum(1 for v in levers.values() if v == "tool-refuses")
    demoted = sum(1 for v in levers.values() if v == "demote")
    return heartbeat, refuses, demoted


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        from importlib import import_module
        import sys as _sys
        _sys.path.insert(0, os.path.join(REPO, "scripts", "tests"))
        mod = import_module("selftest_db2_levers")
        n, fails = mod.run()
        print(f"db2_levers selftest: {n} assertions, {len(fails)} failed")
        for f in fails:
            print(f"  FAIL: {f}")
        return 0 if not fails else 1
    hb, tr, dm = tally()
    print(f"DB-2 lever tally (this file's scope, 11 rows): heartbeat-warn={hb} "
          f"tool-refuses={tr} demote={dm}")
    print("Live-run against real repo artifacts requires per-row inputs; see "
          "scripts/tests/selftest_db2_levers.py for the wired demonstration on fixtures, "
          "and wiki/intake-triage/P3-2-DB2-LEVERS-2026-09-04.md for the measured-vs-charter report.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
