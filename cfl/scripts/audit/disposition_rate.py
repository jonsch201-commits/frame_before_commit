#!/usr/bin/env python3
"""Disposition rate — what fraction of this program's findings ever got ACTED ON.

WHY THIS EXISTS, AND WHY IT IS DIFFERENT FROM EVERY OTHER CHECK HERE
--------------------------------------------------------------------
⛔ WE INSTRUMENT DELIVERY EVERYWHERE AND RESPONSE NOWHERE.

Every instrument in `scripts/audit/` answers "did the thing get produced?" — was the letter
written, did the probe run, did the agent return. **Not one of them asks whether anybody then DID
anything about it.** So a checker that fires perfectly, writes a correct finding, and is ignored
forever reports as healthy, because from the producing side it IS healthy.

The frame arrived 2026-08-23 from a Hank Green transcript Jon supplied, on the Merck/Moderna
phase-3 melanoma readout. Eight of sixteen pancreatic-cancer patients **"did not mount an immune
response at all to the vaccine. So their body just kind of didn't notice it existed."** The
vaccine was delivered. It was not received. **Measuring doses administered would have called that
trial a success.**

  > DELIVERED IS NOT RECEIVED.
  > A FINDING NOBODY DISPOSITIONS IS A FINDING THAT WAS NEVER MADE.

The fixtures are this program's own, all measured in a single day (2026-08-23):
  - Five critic fires wrote correct findings and sat undispositioned for six days.
  - 14 of 65 letters written since 08-15 reached ZERO copies of at least one addressee.
  - 43 letters stranded in a retired trunk, eleven addressed to a seat BY NAME.
  - 18 Herald letters read as UNREAD that had in fact been absorbed — acting without stamping is
    indistinguishable from never reading, in BOTH directions.
  - A granted Jon approval sat unused for twelve days: read, summarised, never dispositioned.

⭐ PUBLISH THE NUMBER EVEN IF IT IS 0%. ESPECIALLY IF IT IS 0%.
A rate this tool refuses to print because it is embarrassing is the same defect one layer up. The
whole value is that the number is visible and moves.

WHAT COUNTS AS A DISPOSITION
----------------------------
Not "somebody read it." A disposition is a DURABLE MARK that says what happened: routed, resolved,
declined-with-reason, ticketed-with-an-owner. ⚠️ Deliberately generous — this tool is measuring an
order of magnitude, not grading prose. If the generous count is still terrible, the strict count
would only be worse, and nobody can argue the threshold was rigged.

⛔ WHAT THIS TOOL DOES NOT DO, stated so nobody reads a good number as good news:
it cannot tell a REAL disposition from a rubber stamp. A row marked ROUTED whose `routed_by`
names nothing is counted as dispositioned here. **The rate is an UPPER BOUND on health.**

Usage:
    python scripts/audit/disposition_rate.py
    python scripts/audit/disposition_rate.py --json
    python scripts/audit/disposition_rate.py --selftest     # both verdicts, exits 1 on failure
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return None


def surface_routing_ledger(root):
    """Agent returns. ROUTED or an explicit recorded skip counts as dispositioned.

    ⛔ CORRECTED 2026-08-23 ~15:4x, BY ME, AGAINST MY OWN HEADLINE, WITHIN AN HOUR OF PUBLISHING
    IT TO THREE TRUNKS. Read this before quoting the number.

    I published "3.1% disposition rate on agent returns" and called it the most important number in
    the program. It is LITERALLY TRUE AND IT INSTALLS A FALSE BELIEF -- which is precisely the
    defect class Jon handed us the same afternoon ("a truth sentence that puts a huge lie into
    people's heads"), committed by me, on my own flagship measurement, in the tool built to detect
    the family it belongs to.

    THE DENOMINATOR IS NOT WHAT THE LABEL SAYS. These rows are written AUTOMATICALLY by a hook, one
    per subagent return -- 2,257 of them, every kind of run, including lint checks, extractors, and
    mechanical parses whose whole value was consumed inside the session that spawned them. So this
    measures:

        NOT  "what fraction of our FINDINGS did anyone act on"
        BUT  "what fraction of AGENT RUNS produced a durably-cited artifact"

    ⭐ And "every agent run should leave a durably-cited artifact" WAS NEVER THE STANDARD. A lint
    check that returns clean and is believed has been fully received. Counting it as an ignored
    finding is the same error as counting a delivered letter as a lost one.

    ⚠ WHAT SURVIVES, because the correction is not a retraction: a real signal is still in here.
    Some of those PENDING rows ARE substantive returns nobody ever consumed, and the ledger cannot
    tell those from routine ones because IT NEVER RECORDED WHICH WERE WHICH. That is a genuine
    defect and it is now the honest finding: THE LEDGER HAS NO NOTION OF WHICH RETURNS CARRIED
    SOMETHING WORTH DISPOSITIONING. Fixing it means classifying at write time, not at read time.

    ⛔ So this row is reported as a CITATION RATE, labelled as such, and is NOT summed into the
    headline. The letters surface is a true disposition rate -- a letter is an addressed
    communication that asks for something -- and it is the number to quote.
    """
    p = os.path.join(root, "exchange", "ROUTING-LEDGER.md")
    text = _read(p)
    if text is None:
        return None
    rows = [ln for ln in text.split("\n") if re.match(r"^\|\s*20\d\d", ln)]
    done = [ln for ln in rows
            if re.search(r"\|\s*(ROUTED|NOT-CONSIDERED)", ln)]
    return {"surface": "agent runs CITED (ROUTING-LEDGER)", "total": len(rows),
            "dispositioned": len(done), "excluded_from_headline": True,
            "note": "CITATION rate, NOT a disposition rate -- auto-logged, one row per subagent "
                    "return, most of them routine. See the docstring. Do NOT quote as 3% ignored."}


def surface_inbound(root):
    """Peer letters. Dispositioned when the file carries a resolved/read/disposition marker.

    ⚠️ Generous on purpose: ANY of several markers counts, and one anywhere in the file is enough.
    """
    d = os.path.join(root, "exchange", "inbound")
    if not os.path.isdir(d):
        return None
    files = [f for f in os.listdir(d) if f.endswith(".md")]
    marker = re.compile(r"(resolved:|disposition[-: ]|disposed[-: ]|read-[a-z]+:|actioned)", re.I)
    done = 0
    for f in files:
        t = _read(os.path.join(d, f))
        if t and marker.search(t):
            done += 1
    return {"surface": "peer letters (exchange/inbound)", "total": len(files),
            "dispositioned": done,
            "note": "generous: any resolved/read/actioned marker anywhere in the file"}


def surface_findings(root):
    """FINDING-*.md deposits. Dispositioned when some OTHER tracked file names the finding.

    ⭐ This is the right test and it is the one the program keeps failing: a finding that only
    exists in its own file has not been dispositioned, it has been FILED. Naming it elsewhere --
    a ticket, a map row, a decision -- is the act.
    """
    d = os.path.join(root, "wiki", "intake-triage")
    if not os.path.isdir(d):
        return None
    findings = []
    for dirpath, _dirnames, filenames in os.walk(d):
        for f in filenames:
            if f.startswith("FINDING-") and f.endswith(".md"):
                findings.append(f)
    if not findings:
        return {"surface": "findings (wiki/intake-triage)", "total": 0, "dispositioned": 0,
                "note": "no FINDING-*.md deposits"}

    # Search the tracked surfaces where a disposition would live.
    hay = []
    for sub in (os.path.join("wiki", "tracker"), os.path.join("wiki", "DECISIONS.md"),
                os.path.join("wiki", "index.md"), os.path.join("wiki", "log.md")):
        p = os.path.join(root, sub)
        if os.path.isfile(p):
            hay.append(_read(p) or "")
        elif os.path.isdir(p):
            for f in os.listdir(p):
                if f.endswith(".md"):
                    hay.append(_read(os.path.join(p, f)) or "")
    blob = "\n".join(hay)
    done = sum(1 for f in findings if f in blob)
    return {"surface": "findings (wiki/intake-triage)", "total": len(findings),
            "dispositioned": done,
            "note": "dispositioned = named by some file under wiki/tracker, DECISIONS, index or log"}


SURFACES = [surface_routing_ledger, surface_inbound, surface_findings]


def collect(root):
    out = []
    for fn in SURFACES:
        r = fn(root)
        if r is not None:
            r["rate"] = (r["dispositioned"] / r["total"]) if r["total"] else None
            out.append(r)
    return out


def _trunk_banner(root):
    """Name the TREE that was measured, unmissably, on every single run.

    RAISED 2026-08-23 ~18:3x by CFL's own adversarial sweep, and it is the most expensive defect
    of the day. Herald ran this tool "against Personal's tree", reported 352 letters / 21.3% /
    agent-returns 3.0%, and both trunks concluded the numbers were "functionally IDENTICAL across
    two independently-built trees -- a structural property." CFL amplified that.

    THEY WERE CFL'S NUMBERS BOTH TIMES. `--root` defaults to REPO, which is derived from
    `__file__`, so invoking the script BY PATH from another trunk silently measures the trunk the
    SCRIPT lives in, never the caller's. Measured here: CFL 359 letters / 22.3%; Personal, with an
    explicit --root, 286 / 27.6% -- and NO ROUTING-LEDGER ROW AT ALL, because Personal has no such
    ledger. So Personal's "3.0% agent-return rate" does not exist and never did.

    THIS IS A REGRESSION OF PR-1 PROMISE 4, which was graded VERIFIED this morning for exactly
    this bug -- "the tool silently bound to CFL no matter where it ran, and the fix is in the
    code." The fix went into ONE file. This script was written LATER THE SAME DAY with the same
    defect. A fix applied to an instance rather than a class comes back wearing the next tool.

    The banner cannot be silenced, because silence is precisely how a copy passed for a
    corroboration. It prints the resolved path AND whether the root is the script's own trunk.
    """
    import os as _os
    same = _os.path.abspath(root) == _os.path.abspath(REPO)
    print("  MEASURING: %s" % _os.path.abspath(root))
    if same:
        print("  ^ this is the SCRIPT'S OWN TRUNK. If you meant another trunk, pass --root; "
              "this tool does NOT infer it from your working directory.")
    else:
        print("  ^ FOREIGN ROOT (script lives in %s). Surfaces absent there are reported "
              "ABSENT, never as zero." % _os.path.abspath(REPO))
    print()


def render(rows, root=None):
    if root is not None:
        _trunk_banner(root)
    print("=== DISPOSITION RATE — of the findings this program produced, how many were acted on ===\n")
    print(f"  {'surface':<38} {'total':>7} {'disposed':>9} {'rate':>7}")
    print(f"  {'-'*38} {'-'*7} {'-'*9} {'-'*7}")
    worst = None
    for r in rows:
        rate = "n/a" if r["rate"] is None else f"{r['rate']:.1%}"
        print(f"  {r['surface']:<38} {r['total']:>7} {r['dispositioned']:>9} {rate:>7}")
        if r.get("excluded_from_headline"):
            continue
        if r["rate"] is not None and (worst is None or r["rate"] < worst["rate"]):
            worst = r
    print()
    for r in rows:
        print(f"    {r['surface']}: {r['note']}")
    print()
    head = [r for r in rows if not r.get("excluded_from_headline")]
    tot = sum(r["total"] for r in head)
    dis = sum(r["dispositioned"] for r in head)
    if tot:
        print(f"  HEADLINE {dis}/{tot} = {dis/tot:.1%} of ADDRESSED findings carry a disposition.")
        print("  (rows marked excluded_from_headline are NOT summed in -- see their note)")
    if worst and worst["rate"] is not None and worst["rate"] < 0.25:
        print()
        print(f"  ⛔ WORST SURFACE: {worst['surface']} at {worst['rate']:.1%}.")
        print("     This is the delivered-is-not-received defect, measured rather than argued.")
        print("     A checker firing correctly into a surface nobody dispositions is not working —")
        print("     it only LOOKS like it is working, because production and response are")
        print("     instrumented separately and only production is instrumented at all.")
    print()
    print("  ⚠ UPPER BOUND. This tool cannot tell a real disposition from a rubber stamp: a row")
    print("    marked ROUTED whose pointer names nothing still counts here. Health is at best this.")


def selftest():
    """Exercise BOTH verdicts on synthetic trees. A rate that can only be computed on the real
    repo has never been shown to be capable of reporting a GOOD number."""
    import tempfile
    ok = True

    def build(tmp, rows):
        os.makedirs(os.path.join(tmp, "exchange"), exist_ok=True)
        with open(os.path.join(tmp, "exchange", "ROUTING-LEDGER.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("| closed_utc | id | disposition |\n|---|---|---|\n")
            for r in rows:
                fh.write(f"| 2026-08-23T00:00:00Z | abc123 | {r} |\n")

    print("--- selftest case 1: everything dispositioned (expect 100%) ---")
    with tempfile.TemporaryDirectory() as t:
        build(t, ["ROUTED"] * 5)
        r = surface_routing_ledger(t)
        got = r["dispositioned"] / r["total"]
        print(f"    {r['dispositioned']}/{r['total']} = {got:.0%}  "
              f"{'PASS' if got == 1.0 else 'FAIL'}")
        ok &= (got == 1.0)

    print("--- selftest case 2: nothing dispositioned (expect 0%, and it MUST print) ---")
    with tempfile.TemporaryDirectory() as t:
        build(t, ["PENDING"] * 7)
        r = surface_routing_ledger(t)
        got = r["dispositioned"] / r["total"]
        print(f"    {r['dispositioned']}/{r['total']} = {got:.0%}  "
              f"{'PASS' if got == 0.0 else 'FAIL'}")
        ok &= (got == 0.0)

    print("--- selftest case 3: a recorded skip COUNTS (expect 100%) ---")
    with tempfile.TemporaryDirectory() as t:
        build(t, ["NOT-CONSIDERED:out of scope"] * 3)
        r = surface_routing_ledger(t)
        got = r["dispositioned"] / r["total"]
        print(f"    {r['dispositioned']}/{r['total']} = {got:.0%}  "
              f"{'PASS' if got == 1.0 else 'FAIL'}")
        print("      (the ledger's own contract: a recorded skip is legitimate;")
        print("       the UNRECORDED skip is the defect)")
        ok &= (got == 1.0)

    print("\n" + ("SELFTEST PASS — 0% and 100% both reachable and both printed"
                  if ok else "SELFTEST FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    rows = collect(a.root)
    if a.json:
        # The root travels INSIDE the payload: a machine consumer cannot read a banner,
        # and Herald consumed this tool's output as data, not as a terminal session.
        print(json.dumps({"measured_root": os.path.abspath(a.root),
                          "script_trunk": os.path.abspath(REPO),
                          "is_own_trunk": os.path.abspath(a.root) == os.path.abspath(REPO),
                          "rows": rows}, indent=2))
    else:
        render(rows, root=a.root)
    # ⛔ Exit 0 ALWAYS. This reports; it does not gate. A rate that blocks work would be struck as
    # a gate on the day it was written -- see wiki/references/struck-gates.md, and Jon's seventh
    # over-gating correction, 2026-08-23.
    return 0


if __name__ == "__main__":
    sys.exit(main())
