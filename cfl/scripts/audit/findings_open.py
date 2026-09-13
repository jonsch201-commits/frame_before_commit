#!/usr/bin/env python3
"""findings_open.py -- one screen carrying a finding's CURRENT state, per population.

WHY THIS EXISTS (WW-4)
----------------------
2026-09-04 23:11: the EXIT-3 finding was dispositioned, fixed, and re-verified by a
non-author. 2026-09-05: Jon read it as live. Nothing between those two points was broken.
**There is no surface that carries a finding's CURRENT state.** Letters accumulate; a
finding's status lives only in the newest one, and the newest one is not where anybody looks.

⛔ AND THE TICKET'S OWN REMEDY WOULD HAVE SHIPPED A FALSE GREEN.
WW-4 said: build this over `exchange/su-close/FINDINGS-LEDGER.jsonl`, one row per finding.
`[measured 2026-09-05]` that ledger is **696 append-only rows collapsing to 4 distinct keys
-- C1, C1, C2, C3 -- and the latest row for every one says CLOSED.** The file is healthy and
honest. It holds COMPACT-VERIFIER findings ONLY. The finding Jon read as live was a
PEER-REVIEW DISPOSITION finding, a class that has never entered it. Built as specced, this
script would print `0 OPEN` while the finding that motivated it stayed invisible.

SO: THREE POPULATIONS, THREE DENOMINATORS, REPORTED SEPARATELY AND NEVER BLENDED.

    1. compact-verifier findings   FINDINGS-LEDGER.jsonl, latest row per `key`   MEASURED
    2. TICKETED dispositions       tracker rows, via disposition_resolves.py      MEASURED
    3. peer-review findings        the newest letter that mentions them           UNKNOWN

⛔ POPULATION 3 IS RENDERED `UNKNOWN -- not measured here`, NEVER FOLDED INTO A TOTAL, and
never as a zero. This is WW-3 one layer over: an empty sweep and a clean sweep print the same
bytes unless one of them says so, and here the sweep that cannot see the population is the one
that would print the reassuring number. ⭐ **A single blended count is the defect, not the
feature.** The fix for population 3 is to make letters deposit a ledger row; until that
exists, this screen says so out loud rather than implying coverage it does not have.

USAGE
    findings_open.py [--repo DIR] [--json]
    findings_open.py --selftest

EXIT CODES
    0  every MEASURED population is clean AND every population is accounted for
    1  a MEASURED population has an OPEN finding
    3  UNKNOWN -- a population could not be measured (dominates a PASS)
    2  usage / unreadable input
"""
import argparse
import collections
import json
import os
import subprocess
import sys
import tempfile

REPO_DEFAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEDGER_REL = os.path.join("exchange", "su-close", "FINDINGS-LEDGER.jsonl")


def read_ledger(path):
    """Latest row per `key` IS the current state -- the file is append-only and rows repeat.

    Returns (latest_by_key, n_rows, error_or_None). A missing or unreadable file is an
    ERROR, never an empty dict: zero findings and no measurement print the same bytes.
    """
    if not os.path.exists(path):
        return {}, 0, "ledger not found at %s" % path
    latest, n, bad = {}, 0, 0
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                n += 1
                try:
                    r = json.loads(line)
                except ValueError:
                    bad += 1
                    continue
                k = r.get("key")
                if k is None:
                    bad += 1
                    continue
                latest[k] = r
    except OSError as e:
        return {}, 0, "ledger unreadable: %s" % e
    if n == 0:
        return {}, 0, "ledger is empty -- that is no measurement, not a clean sweep"
    if bad:
        return latest, n, "%d of %d rows unparseable or keyless" % (bad, n)
    return latest, n, None


def run_disposition_check(repo):
    """Population 2. Shell out to the instrument that owns it rather than reimplementing.

    ⛔ NOT READ THROUGH A PIPE. This trunk has shipped two scripts that printed
    'RESULT: FAIL' and exited 0; the exit code is captured from the process directly.
    """
    script = os.path.join(repo, "scripts", "audit", "disposition_resolves.py")
    if not os.path.exists(script):
        return None, "disposition_resolves.py not found at %s" % script
    try:
        p = subprocess.run([sys.executable, script], cwd=repo,
                           capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "could not run disposition_resolves.py: %s" % e
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode == 0 and not out.strip():
        # This trunk's own law from the 2026-09-01 Drive EINVAL hour.
        return None, "exit 0 with zero bytes -- UNKNOWN, not a pass"
    return (p.returncode, out), None


def build(repo):
    report = collections.OrderedDict()

    latest, n_rows, err = read_ledger(os.path.join(repo, LEDGER_REL))
    if err and not latest:
        report["compact-verifier findings"] = {
            "state": "UNKNOWN", "denominator": LEDGER_REL, "detail": err, "rows": []}
    else:
        openrows = [v for v in latest.values() if str(v.get("state", "")).upper() != "CLOSED"]
        report["compact-verifier findings"] = {
            "state": "OPEN" if openrows else "CLEAN",
            "denominator": "%s -- %d rows collapsing to %d distinct finding(s)"
                           % (LEDGER_REL, n_rows, len(latest)),
            "detail": err or "",
            "rows": [{"key": v.get("key"), "state": v.get("state"),
                      "closed_at": v.get("closed_at"),
                      "closed_reason": v.get("closed_reason"),
                      "detail": v.get("detail")} for v in latest.values()],
        }

    res, derr = run_disposition_check(repo)
    if derr:
        report["TICKETED dispositions"] = {
            "state": "UNKNOWN", "denominator": "wiki/tracker/** via disposition_resolves.py",
            "detail": derr, "rows": []}
    else:
        rc, out = res
        # ⛔ EXIT 2 IS NOT A FINDING. Caught by this script's OWN first live run, which graded
        # `disposition_resolves.py`'s usage error ("UNKNOWN: no --file given", exit 2) as OPEN.
        # A nonzero exit was mapped straight to a verdict without asking WHICH nonzero -- the
        # exact class this file exists to stop, committed inside the file that stops it.
        # 0 -> CLEAN · 1 -> OPEN · anything else -> UNKNOWN, which dominates.
        state = {0: "CLEAN", 1: "OPEN"}.get(rc, "UNKNOWN")
        report["TICKETED dispositions"] = {
            "state": state,
            "denominator": "wiki/tracker/** via disposition_resolves.py (exit %d%s)"
                           % (rc, "" if state != "UNKNOWN" else " -- not a findings verdict"),
            "detail": out.strip().splitlines()[-1] if out.strip() else "",
            "rows": []}

    # ⛔ POPULATION 3. Declared UNKNOWN by construction, and that is the finding, not a gap
    # in this script. Do not "fix" it by counting letters -- a letter count is not a state.
    report["peer-review findings"] = {
        "state": "UNKNOWN",
        "denominator": "NONE -- a peer-review finding's state lives only in the newest letter "
                       "that mentions it",
        "detail": "This is WW-4 itself. EXIT 3 was closed and re-verified 2026-09-04 23:11 and "
                  "Jon read it as live on 2026-09-05, because no ledger row exists for this "
                  "class. The fix is to make letters deposit a row -- not to make this screen "
                  "guess. UNKNOWN dominates a PASS.",
        "rows": []}
    return report


def render(report):
    out = []
    W = out.append
    W("FINDINGS -- current state by population. NO BLENDED TOTAL, BY DESIGN.")
    W("")
    worst = 0
    for name, pop in report.items():
        st = pop["state"]
        mark = {"CLEAN": "  OK ", "OPEN": " OPEN", "UNKNOWN": " UNK "}[st]
        W("%s  %-26s %s" % (mark, name, st))
        W("        denominator: %s" % pop["denominator"])
        if pop["detail"]:
            for ln in str(pop["detail"]).splitlines():
                W("        %s" % ln)
        for r in pop["rows"]:
            if str(r.get("state", "")).upper() != "CLOSED":
                W("        OPEN  %s -- %s" % (r.get("key"), r.get("detail")))
        W("")
        if st == "OPEN":
            worst = max(worst, 1)
        elif st == "UNKNOWN":
            worst = max(worst, 3)
    W("VERDICT: %s" % ("UNKNOWN -- a population could not be measured; UNKNOWN dominates a PASS"
                       if worst == 3 else
                       "OPEN findings exist in a measured population" if worst == 1 else
                       "every population measured and clean"))
    return "\n".join(out), worst


def selftest():
    ok = [True]

    def a(cond, msg):
        print(("  PASS  " if cond else "  FAIL  ") + msg)
        ok[0] = ok[0] and bool(cond)

    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "exchange", "su-close"))
        os.makedirs(os.path.join(td, "scripts", "audit"))
        lp = os.path.join(td, LEDGER_REL)

        # (1) missing ledger -> UNKNOWN, never CLEAN
        latest, n, err = read_ledger(lp)
        a(err is not None and not latest, "missing ledger -> error, not an empty clean sweep")

        # (2) empty ledger -> UNKNOWN. Zero findings and no measurement must not look alike.
        open(lp, "w").close()
        latest, n, err = read_ledger(lp)
        a(err is not None, "EMPTY ledger -> error ('no measurement'), not CLEAN")

        # (3) append-only: the LATEST row per key is the state, and it can close an open one
        with open(lp, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"key": "K1", "state": "OPEN", "detail": "d"}) + "\n")
            fh.write(json.dumps({"key": "K1", "state": "OPEN", "detail": "d"}) + "\n")
            fh.write(json.dumps({"key": "K1", "state": "CLOSED", "detail": "d"}) + "\n")
            fh.write(json.dumps({"key": "K2", "state": "OPEN", "detail": "still open"}) + "\n")
        latest, n, err = read_ledger(lp)
        a(n == 4 and len(latest) == 2, "4 rows collapse to 2 keys")
        a(latest["K1"]["state"] == "CLOSED", "LATEST row wins: K1 reads CLOSED, not OPEN")
        a(latest["K2"]["state"] == "OPEN", "K2 stays OPEN")

        rep = build(td)
        a(rep["compact-verifier findings"]["state"] == "OPEN",
          "an open ledger key makes population 1 OPEN")
        a(rep["peer-review findings"]["state"] == "UNKNOWN",
          "population 3 is UNKNOWN BY CONSTRUCTION -- never CLEAN, never 0")
        a(rep["TICKETED dispositions"]["state"] == "UNKNOWN",
          "a missing disposition_resolves.py is UNKNOWN, not a pass")

        # EXIT-CODE MAPPING. Planted because this script's own first live run graded a
        # USAGE error (exit 2) as OPEN -- a nonzero exit mapped to a verdict without asking
        # which nonzero. All four cases exercised.
        os.makedirs(os.path.join(td, "scripts", "audit"), exist_ok=True)
        dr = os.path.join(td, "scripts", "audit", "disposition_resolves.py")
        stub = "import sys\nprint('output so it is not zero-bytes')\nsys.exit(%d)\n"
        for code, want in ((0, "CLEAN"), (1, "OPEN"), (2, "UNKNOWN"), (3, "UNKNOWN")):
            with open(dr, "w", encoding="utf-8") as fh:
                fh.write(stub % code)
            got = build(td)["TICKETED dispositions"]["state"]
            a(got == want, "disposition_resolves exit %d -> %s" % (code, want))
        # and the zero-byte case, which is UNKNOWN by this trunk's EINVAL law
        with open(dr, "w", encoding="utf-8") as fh:
            fh.write("import sys\nsys.exit(0)\n")
        a(build(td)["TICKETED dispositions"]["state"] == "UNKNOWN",
          "exit 0 with ZERO BYTES -> UNKNOWN, not a pass")
        os.remove(dr)
        txt, worst = render(rep)
        a(worst == 3, "UNKNOWN dominates OPEN in the verdict")
        a("NO BLENDED TOTAL" in txt, "the screen states that it does not blend")
        a("K2" in txt, "the open row is NAMED, not just counted")

        # (4) all ledger keys closed must STILL not produce a green screen, because
        #     population 3 is unmeasurable. This is the whole point of the ticket.
        with open(lp, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"key": "K1", "state": "CLOSED", "detail": "d"}) + "\n")
        rep2 = build(td)
        _, worst2 = render(rep2)
        a(rep2["compact-verifier findings"]["state"] == "CLEAN", "all-closed ledger reads CLEAN")
        a(worst2 == 3,
          "ALL-CLOSED LEDGER STILL VERDICTS UNKNOWN -- the false green this ticket exists to stop")

    print("\nSELFTEST: %s" % ("PASS" if ok[0] else "FAIL"))
    return 0 if ok[0] else 1


def main():
    ap = argparse.ArgumentParser(description="current state of findings, per population")
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    rep = build(args.repo)
    if args.json:
        print(json.dumps(rep, indent=2))
        return max([0] + [3 if p["state"] == "UNKNOWN" else 1 if p["state"] == "OPEN" else 0
                          for p in rep.values()])
    txt, worst = render(rep)
    print(txt)
    return worst


if __name__ == "__main__":
    sys.exit(main())
