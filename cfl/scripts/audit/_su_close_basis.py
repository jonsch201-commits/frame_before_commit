#!/usr/bin/env python3
"""_su_close_basis.py — did the number get worse, or did the measure get truer?

WHY THIS EXISTS — Jon, 2026-08-06, verbatim
-------------------------------------------
    "Getting worse is getting better if worse is more true than the prior measure."

`su_close.sh` renders a row moving 7 -> 11 as FAIL **whether the world got worse or the
instrument got better**. On the day of the ruling the merge-order hazard count did exactly
that: the committed 2026-08-03 register was built against one comparison ref, the live re-run
was built against `origin/close/pre-compact-2026-08-02`, and the count rose from 10 to 11 with
a *different denominator* (39 branches -> 35). That is a ratchet advance being scored as a
regression, and until the scorecard can tell the two apart the ruling is doctrine the
instruments cannot apply.

WHAT THIS DOES
--------------
Given two dated su-close run directories, it answers ONE question per row:

    was this row's MEASUREMENT BASIS the same in both runs?

    SAME    -> a worse number is a REGRESSION. The thing being measured got worse.
    CHANGED -> a worse number is RE-BASED. The denominator / baseline / comparison ref moved.
    UNKNOWN -> comparability could not be determined. FAIL-CLOSED: the row keeps its failure.
               "We could not tell" is not "it is fine" — that is this program's own posture
               ("a check that could not run is UNKNOWN, never a pass") applied one level up.

THE ANTI-HATCH RULE, WHICH IS THE WHOLE DESIGN
----------------------------------------------
A row that can self-declare "my basis changed" and thereby stop failing is a WORSE defect than
the one being fixed — it is RATIO_FLOOR inverted, an alarm that can always be silenced. So:

  1. NO ROW MAY DECLARE ITS OWN BASIS. There is no flag, no frontmatter, no author-set field.
     Every basis component is a VALUE THIS SCRIPT COMPUTES from the two runs' dated artifacts.
  2. CHANGED requires a NAMED FIELD WITH BOTH VALUES PRINTED. If this script cannot name what
     changed and show the before and after, the verdict is UNKNOWN, never CHANGED. A re-basing
     that cannot be pointed at is not a re-basing.
  3. THE BASIS IS RE-DERIVED FROM THE PRIOR RUN'S RAW INSTRUMENT OUTPUT, never from a number a
     previous run wrote down about itself. `capture-list.out` and `stranded.out` are dated
     measurements; a "basis: unchanged" note would be a claim. Property 3 of su_close.sh
     survives intact.
  4. AMNESTY LASTS EXACTLY ONE RUN. The next run's prior is this run, so the moved basis becomes
     the new baseline and the ratchet re-engages at the new level. RE-BASED buys a run, not an
     exemption. This is the property that makes the mechanism safe to build at all.

WHAT IS DELIBERATELY *NOT* A BASIS COMPONENT
--------------------------------------------
**A content hash of the instrument file.** It was designed in and then cut, because it answers
"did the file change" and not "did the definition change", and it over-triggers in both a noisy
and a gameable direction. Measured, not assumed: `scripts/extract_claude_code_sessions.py` was
committed twice on 2026-08-06 for reasons unrelated to what `capture.pipeline.absent.subagents`
counts. Had the hash been a basis field, that row's 1 -> 48 (the session's own tail — a REAL
regression, and the ruling's own worked example of one) would have been excused as RE-BASED.
An excuse hatch that opens whenever anyone edits a script is exactly the defect this file exists
to avoid. It is left UNBUILT and named here so nobody re-adds it thinking it was overlooked.

THE COMPONENTS THAT SURVIVED, all computed, none declarable
-----------------------------------------------------------
  against  — the comparison ref *by name*, re-read from each run's own summary.md header.
             Ref NAME, never resolved sha: a sha moves on every push and would make every
             branch row RE-BASED forever, which is the hatch.
  pop      — the DENOMINATOR'S MEMBERSHIP, enumerated from each run's raw instrument output,
             compared by SUBSET:
                 prior members are all still present -> SAME  (pure accretion; 576 subagents
                     becoming 652 is the same population plus 76 new ones, so a rising defect
                     count is a real regression)
                 any prior member is GONE            -> CHANGED (members left; the delta now
                     mixes departures with arrivals and the counts are not comparable)
             An empty prior population is UNKNOWN, never SAME — 0/0 discipline, one level up.
  den      — fallback ONLY where members are not enumerable: a denominator that SHRANK is a
             changed basis; non-decreasing is treated as the same basis. Explicitly weaker,
             labelled `(proxy)` in the output so no reader mistakes it for the subset test.

HOW THIS COULD STILL BE GAMED — named because a guard whose hole is undocumented is worse
------------------------------------------------------------------------------------------
1. **CHANGE A ROW'S DEFINITION WITHOUT CHANGING ITS ID.** This is the real one. The comparer
   matches runs by row id; if `git.worktree.clean` silently starts counting something narrower
   under the same name, the `den` proxy reads "non-decreasing" and the verdict comes back SAME.
   The number would improve for free and nothing here would notice. MITIGATION IS A CONVENTION,
   NOT AN ENFORCEMENT: a redefined row must be RENAMED, so the new id reports NOPRIOR (which is
   fail-closed) rather than a false SAME. That is exactly why `git.worktree.clean` was retired
   into `git.worktree.stranded` + `git.worktree.inflight` on 2026-08-06 instead of being edited
   in place. **A reviewer must check this by reading the diff; no instrument here can.**
2. **SHRINK A DENOMINATOR ON A ROW WHOSE MEMBERS ARE NOT ENUMERABLE.** The `den` proxy calls any
   decrease a basis change, so deleting inputs buys a RE-BASED. Bounded by: it lasts one run,
   and the fix is to make that row's population enumerable (add it to POP_BY_ROW), at which
   point the subset test replaces the proxy and a deletion reads CHANGED for the true reason.
3. **CHANGE `--against` GRATUITOUSLY.** A different comparison ref legitimately re-bases the
   branch rows, so passing one every run would keep them permanently excused. Bounded by: the
   ref name is printed in the row's note on every run, so a reader sees it oscillating.
All three share one bound: RE-BASED lasts exactly one run, and the tally prints the field and
both values every time it fires.

Usage:
  python _su_close_basis.py --prior DIR --current DIR      # TSV verdicts on stdout
  python _su_close_basis.py --prior DIR --current DIR --explain
  python _su_close_basis.py --self-test

Output (TSV, one line per row present in the current run):
  <row_id>  <verdict>  <direction>  <detail>
      verdict   SAME | CHANGED | UNKNOWN | NOPRIOR
      direction WORSE | NOTWORSE | UNKNOWN
      detail    human-readable, always names the fields compared and their values

Exit: 0 comparison ran; 2 a run directory was unreadable (never a silent empty result).
"""

import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------------------------
# Row -> which population defines its denominator. Rows absent here fall back to the `den` proxy.
# This table is STRUCTURE (which artifact enumerates this row's population), not a per-run value.
# ---------------------------------------------------------------------------------------------
POP_BY_ROW = {
    "capture.pipeline.absent.unexplained.sessions": "sessions",
    "capture.pipeline.absent.empty.sessions": "sessions",
    "capture.pipeline.absent.subagents": "subagents",
    "capture.extract.stale.quiescent.sessions": "sessions",
    "capture.extract.stale.quiescent.subagents": "subagents",
    "capture.extract.stale.live.sessions": "sessions",
    "capture.extract.stale.live.subagents": "subagents",
    "capture.extract.failed.sessions": "sessions",
    "capture.extract.failed.subagents": "subagents",
    "branches.stranded": "branches",
    "branches.hazard": "hazard_branches",
}

# Rows whose value is defined RELATIVE TO A COMPARISON REF. Change the ref, change the question.
REF_ROWS = {"branches.stranded", "branches.hazard"}

# Fallback modes, used ONLY when comparing two legacy run dirs with no basis-rows.tsv.
# su_close.sh writes the authoritative mode for every row it records; when that file is present
# it wins. A row id that appears in neither is reported UNKNOWN rather than guessed.
FALLBACK_MODE = {
    "capture.pipeline.absent.unexplained.sessions": "zero",
    "capture.pipeline.absent.empty.sessions": "report",
    "capture.pipeline.absent.subagents": "zero",
    "capture.extract.stale.quiescent.sessions": "zero",
    "capture.extract.stale.quiescent.subagents": "zero",
    "capture.extract.stale.live.sessions": "report",
    "capture.extract.stale.live.subagents": "report",
    "capture.extract.failed.sessions": "zero",
    "capture.extract.failed.subagents": "zero",
    "capture.temporal.subagents": "all",
    "capture.links.bidirectional": "all",
    "capture.midturn": "all",
    "wiki.citations.marker": "ratchet",
    "wiki.citations.resolve": "all",
    "wiki.v40.conformant": "ratchet",
    "skills.frontmatter": "zero",
    "triage.outbox": "zero",
    "wiki.log.entry": "all",
    "audit.mirror.claims": "all",
    "coordinator.groundable": "all",
    "wiki.summaries": "all",
    "wiki.seeds": "all",
    "branches.stranded": "zero",
    "branches.hazard": "zero",
    "channels.mail": "zero",
    "git.worktree.clean": "zero",       # retired 2026-08-06; kept so legacy runs still compare
    "git.worktree.stranded": "zero",
    "git.worktree.inflight": "report",
    "git.unpushed": "zero",
    "wake.map": "all",
}

RE_TABLE_ROW = re.compile(
    r"^\|\s*`([^`]+)`\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*\*\*([A-Za-z-]+)\*\*"
)
RE_AGAINST = re.compile(r"against:\s*`([^`]+)`")
RE_SESSION = re.compile(r"^  ([0-9a-f]{6})  ")
RE_SUBAGENT = re.compile(r"^  sub +([0-9a-f]+/[0-9a-f]+)")
RE_BRANCH = re.compile(r"^  (?:PR #\d+|STRANDED)\s+\d+ ahead\b")
RE_HAZARD = re.compile(r"^\s+!! MERGE-ORDER HAZARD:")


def _int(tok):
    try:
        return int(tok)
    except (TypeError, ValueError):
        return None


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


class Run(object):
    """One dated su-close run directory, read for basis components only."""

    def __init__(self, path):
        self.path = path
        self.rows = {}        # id -> dict(value, denom, tier, mode, status)
        self.against = None
        self.pops = {}        # name -> set() | None  (None = not enumerable from this run)
        self.ok = os.path.isdir(path)
        if self.ok:
            self._load_rows()          # may set self.against from summary.md (fallback)
            self._load_meta()          # basis-meta.tsv wins when a run wrote one
            self._load_populations()

    # -- rows ---------------------------------------------------------------------------------
    def _load_meta(self):
        """The comparison ref, preferring basis-meta.tsv over summary.md.

        ORDER MATTERS AND THIS IS WHY. summary.md is written at the END of a run, AFTER the
        adjudication that needs it — so reading `against` only from summary.md made the CURRENT
        run's ref invisible and every branch row came back UNKNOWN instead of CHANGED. Caught on
        the first real end-to-end run, not by a fixture. su_close.sh now drops basis-meta.tsv
        before it calls this; summary.md remains the fallback, which is what lets runs recorded
        before this file existed (2026-08-03/05/06) still be compared.
        """
        meta = _read(os.path.join(self.path, "basis-meta.tsv"))
        if meta:
            for line in meta.splitlines():
                k, _, v = line.rstrip("\n").partition("\t")
                if k == "against" and v:
                    self.against = v

    def _load_rows(self):
        # basis-rows.tsv is authoritative when a run wrote one (id/tier/mode/value/denom/status).
        tsv = _read(os.path.join(self.path, "basis-rows.tsv"))
        if tsv:
            for line in tsv.splitlines():
                f = line.rstrip("\n").split("\t")
                if len(f) < 6:
                    continue
                self.rows[f[0]] = {
                    "tier": f[1], "mode": f[2],
                    "value": _int(f[3]), "denom": _int(f[4]), "status": f[5],
                }
        summ = _read(os.path.join(self.path, "summary.md"))
        if summ:
            m = RE_AGAINST.search(summ)
            if m:
                self.against = m.group(1)
            for line in summ.splitlines():
                m = RE_TABLE_ROW.match(line)
                if not m:
                    continue
                rid, tier, val, den, status = m.groups()
                if rid in self.rows:
                    continue  # basis-rows.tsv already supplied it
                self.rows[rid] = {
                    "tier": tier, "mode": FALLBACK_MODE.get(rid),
                    "value": _int(val), "denom": _int(den), "status": status,
                }

    # -- populations --------------------------------------------------------------------------
    def _load_populations(self):
        cl = _read(os.path.join(self.path, "capture-list.out"))
        if cl is None:
            self.pops["sessions"] = None
            self.pops["subagents"] = None
        else:
            ses, sub = set(), set()
            for line in cl.splitlines():
                m = RE_SESSION.match(line)
                if m:
                    ses.add(m.group(1))
                    continue
                m = RE_SUBAGENT.match(line)
                if m:
                    sub.add(m.group(1))
            self.pops["sessions"] = ses
            self.pops["subagents"] = sub

        sb = _read(os.path.join(self.path, "stranded.out"))
        if sb is None:
            self.pops["branches"] = None
            self.pops["hazard_branches"] = None
        else:
            branches, hazards, cur = set(), set(), None
            for line in sb.splitlines():
                if RE_BRANCH.match(line):
                    parts = line.split()
                    cur = parts[-1] if parts else None
                    if cur:
                        branches.add(cur)
                elif RE_HAZARD.match(line) and cur:
                    hazards.add(cur)
            self.pops["branches"] = branches
            self.pops["hazard_branches"] = hazards


# ---------------------------------------------------------------------------------------------
# Field comparisons. Each returns (STATE, detail) where STATE is SAME | CHANGED | UNKNOWN and
# detail ALWAYS names the field and its two values — rule 2, enforced by the self-test.
# ---------------------------------------------------------------------------------------------
def cmp_against(prior, cur):
    if prior is None or cur is None:
        return "UNKNOWN", "against=? (one run's summary.md did not record a comparison ref)"
    if prior != cur:
        return "CHANGED", "against: %s -> %s" % (prior, cur)
    return "SAME", "against: %s (unchanged)" % cur


def cmp_population(name, prior, cur):
    if prior is None or cur is None:
        return "UNKNOWN", "pop[%s]=? (not enumerable from one run's artifacts)" % name
    if not prior:
        # 0/0 discipline, one level up: an empty prior population measured nothing, so a subset
        # test against it is vacuously true and would hand out a free SAME.
        return "UNKNOWN", "pop[%s]: prior population EMPTY — nothing to compare against" % name
    missing = prior - cur
    if missing:
        sample = ", ".join(sorted(missing)[:4])
        return "CHANGED", "pop[%s]: %d of %d prior members GONE (e.g. %s); prior %d -> now %d" % (
            name, len(missing), len(prior), sample, len(prior), len(cur))
    return "SAME", "pop[%s]: all %d prior members present, +%d new -> %d (accretion)" % (
        name, len(prior), len(cur) - len(prior), len(cur))


def cmp_denominator(prior, cur):
    if prior is None or cur is None:
        return "UNKNOWN", "den=? (missing in one run)"
    if cur < prior:
        return "CHANGED", "den (proxy): %d -> %d, SHRANK — population not comparable" % (prior, cur)
    return "SAME", "den (proxy): %d -> %d, non-decreasing" % (prior, cur)


def direction(mode, p, c):
    """Did this row's number move the WRONG way? Mode decides which way that is."""
    if mode == "report" or mode is None:
        return "UNKNOWN", "mode=%s — no target, direction not defined" % (mode,)
    pv, pd, cv, cd = p.get("value"), p.get("denom"), c.get("value"), c.get("denom")
    if cv is None or pv is None:
        return "UNKNOWN", "value missing in one run"
    if mode == "zero":
        # value counts DEFECTS; the target is 0 regardless of denominator.
        return ("WORSE" if cv > pv else "NOTWORSE"), "defects %d -> %d" % (pv, cv)
    if mode == "all":
        if cd is None or pd is None:
            return "UNKNOWN", "denominator missing in one run"
        return (("WORSE" if (cd - cv) > (pd - pv) else "NOTWORSE"),
                "shortfall %d -> %d" % (pd - pv, cd - cv))
    if mode == "ratchet":
        if not cd or not pd:
            return "UNKNOWN", "denominator missing or zero in one run"
        pr, cr = pv * 1000 // pd, cv * 1000 // cd
        return ("WORSE" if cr < pr else "NOTWORSE"), "rate %d -> %d per-mille" % (pr, cr)
    return "UNKNOWN", "unrecognised mode %r" % (mode,)


def compare(prior_run, cur_run):
    """-> list of (row_id, verdict, direction, detail)."""
    out = []
    for rid in sorted(cur_run.rows):
        c = cur_run.rows[rid]
        p = prior_run.rows.get(rid) if prior_run.ok else None
        if p is None:
            out.append((rid, "NOPRIOR", "UNKNOWN",
                        "row absent from prior run %s — no basis to compare" %
                        (os.path.basename(prior_run.path) if prior_run.ok else "(none)")))
            continue

        mode = c.get("mode") or FALLBACK_MODE.get(rid)
        dirn, dir_detail = direction(mode, p, c)

        fields = []
        if rid in REF_ROWS:
            fields.append(cmp_against(prior_run.against, cur_run.against))
        pop_name = POP_BY_ROW.get(rid)
        if pop_name:
            fields.append(cmp_population(pop_name,
                                         prior_run.pops.get(pop_name),
                                         cur_run.pops.get(pop_name)))
        else:
            fields.append(cmp_denominator(p.get("denom"), c.get("denom")))

        states = [s for s, _ in fields]
        if "CHANGED" in states:
            verdict = "CHANGED"
        elif "UNKNOWN" in states:
            verdict = "UNKNOWN"
        else:
            verdict = "SAME"

        # Rule 2: CHANGED must be able to point at something. It always can here, because the
        # only path to CHANGED is a comparison that already built a two-valued detail string —
        # but the invariant is asserted rather than assumed, and the self-test exercises it.
        detail = "; ".join(d for _, d in fields) + " | " + dir_detail
        if verdict == "CHANGED" and not any(
                st == "CHANGED" and "->" in d for st, d in fields):
            verdict = "UNKNOWN"
            detail = "basis change could not be named with both values — UNKNOWN, never CHANGED"
        out.append((rid, verdict, dirn, detail))
    return out


# ---------------------------------------------------------------------------------------------
# SELF-TEST — negative controls first. A verdict that has never been made to come out CHANGED,
# SAME and UNKNOWN on demand is not known to discriminate anything.
# ---------------------------------------------------------------------------------------------
def self_test():
    fails = []

    def t(name, expected, actual):
        if expected == actual:
            print("  %-64s PASS" % name)
        else:
            print("  %-64s FAIL (expected %r got %r)" % (name, expected, actual))
            fails.append(name)

    print("=== _su_close_basis.py SELF-TEST ===")
    print()
    print("-- population subset: accretion is the SAME basis, departure is not")
    t("prior subset of current (576 -> 652) = SAME", "SAME",
      cmp_population("subagents", set("abcdef"), set("abcdefgh"))[0])
    t("identical populations = SAME", "SAME",
      cmp_population("subagents", set("abc"), set("abc"))[0])
    t("a prior member VANISHED = CHANGED", "CHANGED",
      cmp_population("subagents", set("abcd"), set("abce"))[0])
    t("population shrank = CHANGED", "CHANGED",
      cmp_population("branches", set("abcd"), set("abc"))[0])
    t("EMPTY prior population = UNKNOWN, never SAME", "UNKNOWN",
      cmp_population("branches", set(), set("abc"))[0])
    t("population not enumerable = UNKNOWN", "UNKNOWN",
      cmp_population("branches", None, set("abc"))[0])
    t("CHANGED names both counts", True,
      "->" in cmp_population("subagents", set("abcd"), set("abce"))[1])

    print()
    print("-- comparison ref: the 2026-08-06 hazard re-basing, in miniature")
    t("origin/main -> origin/close/... = CHANGED", "CHANGED",
      cmp_against("origin/main", "origin/close/pre-compact-2026-08-02")[0])
    t("same ref = SAME", "SAME", cmp_against("origin/main", "origin/main")[0])
    t("ref unrecorded in one run = UNKNOWN", "UNKNOWN", cmp_against(None, "origin/main")[0])
    t("CHANGED prints both refs", True,
      "origin/main -> origin/close/pre-compact-2026-08-02"
      in cmp_against("origin/main", "origin/close/pre-compact-2026-08-02")[1])

    print()
    print("-- denominator proxy: weaker, and labelled as such")
    t("den grew = SAME", "SAME", cmp_denominator(100, 120)[0])
    t("den equal = SAME", "SAME", cmp_denominator(100, 100)[0])
    t("den SHRANK = CHANGED", "CHANGED", cmp_denominator(120, 100)[0])
    t("den missing = UNKNOWN", "UNKNOWN", cmp_denominator(None, 100)[0])
    t("proxy is labelled 'proxy'", True, "proxy" in cmp_denominator(100, 120)[1])

    print()
    print("-- direction: which way is worse depends on the mode, not on the sign")
    t("zero 1 -> 48 is WORSE", "WORSE",
      direction("zero", {"value": 1, "denom": 576}, {"value": 48, "denom": 652})[0])
    t("zero 25 -> 9 is NOTWORSE", "NOTWORSE",
      direction("zero", {"value": 25, "denom": 50}, {"value": 9, "denom": 55})[0])
    t("all 138/139 -> 174/174 is NOTWORSE", "NOTWORSE",
      direction("all", {"value": 138, "denom": 139}, {"value": 174, "denom": 174})[0])
    t("all 174/174 -> 170/175 is WORSE", "WORSE",
      direction("all", {"value": 174, "denom": 174}, {"value": 170, "denom": 175})[0])
    t("ratchet rate fall is WORSE", "WORSE",
      direction("ratchet", {"value": 14, "denom": 244}, {"value": 13, "denom": 245})[0])
    t("ratchet rate hold is NOTWORSE", "NOTWORSE",
      direction("ratchet", {"value": 930, "denom": 1613}, {"value": 930, "denom": 1613})[0])
    t("report mode has no direction", "UNKNOWN",
      direction("report", {"value": 2, "denom": 50}, {"value": 32, "denom": 652})[0])
    t("unknown mode is UNKNOWN, not a guess", "UNKNOWN",
      direction(None, {"value": 1, "denom": 2}, {"value": 0, "denom": 2})[0])

    print()
    print("-- THE HATCH CONTROL: a row cannot declare its own basis")
    # There is no code path from run-directory CONTENT to a verdict except through the four
    # comparison functions above, all of which take computed values. This asserts the absence
    # of the thing rather than the presence: no basis key is read from any row's own text.
    # Scope matters, and getting it wrong is how a control passes vacuously: the slice must
    # exclude the module docstring (which DISCUSSES these words) and this self-test (which
    # NAMES them), or the check is testing its own assertion literals. First draft did exactly
    # that and reported FAIL on itself — which is the control working, one level down.
    src = _read(os.path.abspath(__file__)) or ""
    body = src.split('"""', 2)[2].split("def self_test")[0]
    t("slice is the real comparison code, not empty", True,
      "def cmp_population" in body and "def compare" in body)
    for forbidden in ("rebased:", "basis:", "basis_changed", "--declare"):
        t("no author-settable field %-28r" % forbidden, True, forbidden not in body)

    print()
    print("-- end-to-end on synthetic run dirs (the REAL data check is in su_close --self-test)")
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp()
    try:
        def mkrun(name, against, rows, subs, branches):
            d = os.path.join(tmp, name)
            os.makedirs(d)
            with open(os.path.join(d, "summary.md"), "w", encoding="utf-8") as fh:
                fh.write("# SU CLOSE\n\nrepo: `x`  ·  against: `%s`  ·  dry-run: 0\n\n" % against)
                fh.write("| check | tier | value | denominator | status | note |\n|---|---|---:|---:|---|---|\n")
                for rid, tier, v, dn, st in rows:
                    fh.write("| `%s` | %s | %s | %s | **%s** | n |\n" % (rid, tier, v, dn, st))
            with open(os.path.join(d, "capture-list.out"), "w", encoding="utf-8") as fh:
                for s in subs:
                    fh.write("  sub %s    1 B  2026-08-06 00:00  md*  fl  a  t\n" % s)
            with open(os.path.join(d, "stranded.out"), "w", encoding="utf-8") as fh:
                for b, haz in branches:
                    fh.write("  STRANDED     1 ahead    0d         %s\n" % b)
                    if haz:
                        fh.write("             !! MERGE-ORDER HAZARD: scripts/x.py\n")
            return d

        a = mkrun("a", "origin/main",
                  [("capture.pipeline.absent.subagents", "LOSS", 1, 2, "FAIL"),
                   ("branches.hazard", "ADVISORY", 1, 2, "FAIL")],
                  ["aaaaaa/111111", "aaaaaa/222222"],
                  [("b1", True), ("b2", False)])
        # b: subagents accreted (nothing gone) but defects rose -> REGRESSION.
        #    branches measured against a DIFFERENT ref, hazards rose -> RE-BASED.
        b = mkrun("b", "origin/close/pre-compact-2026-08-02",
                  [("capture.pipeline.absent.subagents", "LOSS", 2, 3, "FAIL"),
                   ("branches.hazard", "ADVISORY", 2, 2, "FAIL")],
                  ["aaaaaa/111111", "aaaaaa/222222", "aaaaaa/333333"],
                  [("b1", True), ("b2", True)])
        res = dict((r[0], (r[1], r[2])) for r in compare(Run(a), Run(b)))
        t("accretion + more defects -> SAME/WORSE (REGRESSION)", ("SAME", "WORSE"),
          res.get("capture.pipeline.absent.subagents"))
        t("ref moved + more hazards -> CHANGED/WORSE (RE-BASED)", ("CHANGED", "WORSE"),
          res.get("branches.hazard"))
        # A row the prior run never had cannot be adjudicated at all.
        c = mkrun("c", "origin/main",
                  [("capture.pipeline.absent.subagents", "LOSS", 2, 3, "FAIL"),
                   ("branches.hazard", "ADVISORY", 1, 1, "FAIL"),
                   ("brand.new.row", "LOSS", 5, 9, "FAIL")],
                  ["aaaaaa/111111", "aaaaaa/222222", "aaaaaa/333333"],
                  [("b2", True)])   # b1, which carried the prior hazard, is GONE
        res2 = dict((r[0], (r[1], r[2])) for r in compare(Run(a), Run(c)))
        t("row absent from prior -> NOPRIOR, never SAME", ("NOPRIOR", "UNKNOWN"),
          res2.get("brand.new.row"))
        t("prior hazard branch GONE -> CHANGED", "CHANGED",
          res2.get("branches.hazard", ("?",))[0])
        # No prior run directory at all: everything is unadjudicable, nothing is excused.
        res3 = dict((r[0], (r[1], r[2])) for r in compare(Run(os.path.join(tmp, "nope")), Run(c)))
        t("no prior run at all -> NOPRIOR for every row", ("NOPRIOR", "UNKNOWN"),
          res3.get("capture.pipeline.absent.subagents"))

        # THE REGRESSION TEST FOR THE BUG THE FIRST REAL RUN FOUND. An in-flight run has no
        # summary.md yet — it is written last — so `against` must come from basis-meta.tsv or
        # the current run's own comparison ref is invisible and every branch row reads UNKNOWN.
        d = os.path.join(tmp, "d")
        os.makedirs(d)
        with open(os.path.join(d, "basis-meta.tsv"), "w", encoding="utf-8") as fh:
            fh.write("against\torigin/close/pre-compact-2026-08-02\n")
        with open(os.path.join(d, "basis-rows.tsv"), "w", encoding="utf-8") as fh:
            fh.write("branches.hazard\tADVISORY\tzero\t11\t35\tFAIL\n")
        t("mid-run dir with NO summary.md still knows its ref",
          "origin/close/pre-compact-2026-08-02", Run(d).against)
        t("mid-run hazard row -> CHANGED/WORSE (RE-BASED)", ("CHANGED", "WORSE"),
          dict((r[0], (r[1], r[2])) for r in compare(Run(a), Run(d))).get("branches.hazard"))
        # And basis-meta.tsv must WIN over a stale summary.md, not merely fill a gap.
        with open(os.path.join(d, "summary.md"), "w", encoding="utf-8") as fh:
            fh.write("repo: `x`  ·  against: `origin/main`  ·  dry-run: 0\n")
        t("basis-meta.tsv beats summary.md", "origin/close/pre-compact-2026-08-02", Run(d).against)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if fails:
        print("RESULT: FAIL — %d case(s): %s" % (len(fails), "; ".join(fails)))
        return 1
    print("RESULT: PASS — the verdict comes out CHANGED, SAME, UNKNOWN and NOPRIOR on demand,")
    print("        and CHANGED can never be reached without naming both values.")
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--prior")
    ap.add_argument("--current")
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.prior or not args.current:
        sys.stderr.write("ERROR: --prior and --current are both required\n")
        return 2
    cur = Run(args.current)
    if not cur.ok or not cur.rows:
        sys.stderr.write("ERROR: current run dir unreadable or has no rows: %s\n" % args.current)
        return 2
    prior = Run(args.prior)
    rows = compare(prior, cur)
    if args.explain:
        print("prior   : %s (against=%s, rows=%d)" % (args.prior, prior.against, len(prior.rows)))
        print("current : %s (against=%s, rows=%d)" % (args.current, cur.against, len(cur.rows)))
        print()
        for rid, verdict, dirn, detail in rows:
            print("%-46s %-8s %-9s %s" % (rid, verdict, dirn, detail))
    else:
        for rid, verdict, dirn, detail in rows:
            print("%s\t%s\t%s\t%s" % (rid, verdict, dirn, detail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
