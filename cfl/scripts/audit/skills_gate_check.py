#!/usr/bin/env python3
"""skills_gate_check.py -- mechanical invariants of the skills gate (RP-20 -> PR-3).

The gate's judgment half (probe grading) is human/fable work; this script checks the
MECHANICAL half so the prototype meets PR-3's own bar (prototypes made AND TESTED,
ticket closes on a running artifact + measured output):

  G1  every index line in LEDGER.md has a matching '## PROP-xxx' section, and vice versa
  G2  every non-fixture section carries the five required fields
      (From / Motivating record / Diff / Probe / Verdict)
  G3  every ACCEPTED CREATE names a target skill file that EXISTS on disk
  G4  both branches are exercised: >=1 ACCEPTED/REJECTED row and >=1 RETURNED-UNREAD row
      (a gate that has only ever said yes is an acceptance test that cannot fail)
  G5  GATE-SPEC.md exists and states the strict-improvement rule and the revert rule
  G6  NUMERIC STRICT IMPROVEMENT (GATE-SPEC rule 8, GT-1 2026-09-02): every ACCEPTED
      section dated on or after 2026-09-02 carries R_before=<x>@<sha8> and
      R_after=<y>@<sha8>, with y > x and BOTH sha8 equal to the first 8 chars of
      wiki/skills-gate/validation/<skill>/heldout.sha256 for the skill the row targets.
      Before this rule, "strict improvement" was prose in every row: the gate's own
      GATE-SPEC said so ("What this is not (yet): a benchmark suite"). A row that names
      no split, or names a split whose hash has moved, is UNKNOWN -- and UNKNOWN never
      rounds to PASS, so it fails.

Exit 0 all pass; exit 1 with each failure named. --selftest proves G1-G4 can FAIL by
running against a deliberately broken in-memory fixture (never written to the wiki), and
proves G6 fails on a planted prose-only ACCEPTED row while passing a numeric one.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "wiki" / "skills-gate" / "LEDGER.md"
SPEC = ROOT / "wiki" / "skills-gate" / "GATE-SPEC.md"

REQUIRED_FIELDS = ["**From:**", "**Motivating record", "**Diff:**", "**Probe", "**Verdict:"]

# G6 applies only to rows decided on or after the day the rule landed. Earlier rows are
# not retro-failed: the split did not exist when they were gated, and rewriting them to
# look compliant would be a fabricated measurement (no-deletion cuts both ways).
G6_EPOCH = (2026, 9, 2)
R_BEFORE = re.compile(r"R_before\s*=\s*([0-9]*\.?[0-9]+)@([0-9a-f]{8})")
R_AFTER = re.compile(r"R_after\s*=\s*([0-9]*\.?[0-9]+)@([0-9a-f]{8})")
SKILL_TARGET = re.compile(r"skills/([A-Za-z0-9_-]+)/SKILL\.md")
SEC_DATE = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")


def _g6(sid, sec, root):
    """Return a list of G6 failures for one ACCEPTED section dated >= the epoch."""
    fails = []
    b, a = R_BEFORE.search(sec), R_AFTER.search(sec)
    if not b or not a:
        return [f"G6: {sid} ACCEPTED on/after 2026-09-02 with no R_before=<x>@<sha8> / "
                f"R_after=<y>@<sha8> pair -- strict improvement asserted in prose only"]
    if not float(a.group(1)) > float(b.group(1)):
        fails.append(f"G6: {sid} R_after={a.group(1)} is not strictly greater than "
                     f"R_before={b.group(1)} -- a tie reverts (GATE-SPEC gate rule 3)")
    m = SKILL_TARGET.search(sec)
    if not m:
        fails.append(f"G6: {sid} names no skills/<name>/SKILL.md target, so the split it "
                     f"was scored on cannot be identified -- UNKNOWN, not a pass")
        return fails
    skill = m.group(1)
    held = root / "wiki" / "skills-gate" / "validation" / skill / "heldout.sha256"
    if not held.is_file():
        fails.append(f"G6: {sid} targets {skill} but no held-out split exists at "
                     f"{held.as_posix()} -- UNKNOWN, not a pass")
        return fails
    want = held.read_text(encoding="utf-8").split()[0][:8]
    for label, mm in (("R_before", b), ("R_after", a)):
        if mm.group(2) != want:
            fails.append(f"G6: {sid} {label} cites split {mm.group(2)} but "
                         f"{skill}/heldout.sha256 is {want} -- scored on a split that moved")
    return fails


def check(ledger_text: str, spec_text: str, root: Path):
    fails = []
    index_ids = set(re.findall(r"^- (PROP-\d+)", ledger_text, re.M))
    section_ids = set(re.findall(r"^## (PROP-\d+)", ledger_text, re.M))
    for missing in sorted(index_ids - section_ids):
        fails.append(f"G1: {missing} indexed but has no section")
    for missing in sorted(section_ids - index_ids):
        fails.append(f"G1: {missing} has a section but no index line")

    sections = re.split(r"^## ", ledger_text, flags=re.M)[1:]
    returned_seen = verdict_seen = False
    # G2 groups sections by proposal id + version token ("PROP-004 v3"): an append-only
    # restatement section with the same key may supply fields the original lacks (2026-09-02, GT-1-F1).
    def _g2_key(sec):
        toks = sec.split("\n", 1)[0].strip().split()
        if len(toks) > 1 and re.match(r"v\d+$", toks[1]):
            return toks[0] + " " + toks[1]
        return toks[0] if toks else ""
    _g2_groups = {}
    for sec in sections:
        _g2_groups.setdefault(_g2_key(sec), []).append(sec)
    for sec in sections:
        sid = sec.split(" ", 1)[0].split("\n")[0].strip()
        if "RETURNED-UNREAD" in sec:
            returned_seen = True
            continue  # fixtures/returns are exempt from G2/G3
        if any(v in sec for v in ("ACCEPTED", "REJECTED")):
            verdict_seen = True
        _g2_blob = "\n".join(_g2_groups.get(_g2_key(sec), [sec]))
        for f in REQUIRED_FIELDS:
            if f not in _g2_blob:
                fails.append(f"G2: {sid} missing field {f}")
        if "ACCEPTED" in sec:
            d = SEC_DATE.search(sec.split(chr(10), 1)[0])
            if d and tuple(int(x) for x in d.groups()) >= G6_EPOCH:
                fails.extend(_g6(sid, sec, root))

        if "ACCEPTED" in sec and "CREATE" in sec:
            m = re.search(r"CREATE\s+`([^`]+)`", sec)
            if not m:
                fails.append(f"G3: {sid} ACCEPTED CREATE names no target in backticks")
            elif not (root / m.group(1)).exists():
                fails.append(f"G3: {sid} target `{m.group(1)}` does not exist on disk")

    if not returned_seen:
        fails.append("G4: no RETURNED-UNREAD row -- refusal branch never exercised")
    if not verdict_seen:
        fails.append("G4: no ACCEPTED/REJECTED row -- gate branch never exercised")

    if "strict" not in spec_text.lower() or "revert" not in spec_text.lower():
        fails.append("G5: GATE-SPEC missing strict-improvement or revert rule")
    return fails


def main():
    if "--selftest" in sys.argv:
        broken = ("- PROP-900\n\n## PROP-901 (x) -- ACCEPTED\n\n- **Diff:** CREATE `no/such/file.md`\n")
        fails = check(broken, "no rules here", ROOT)
        want = ["G1", "G1", "G2", "G3", "G4", "G5"]
        got = [f[:2] for f in fails]
        for w in want:
            if w not in got:
                print(f"SELFTEST FAIL: broken fixture did not trigger {w}; got {fails}")
                return 1
        print(f"SELFTEST PASS: broken fixture triggers {sorted(set(got))} ({len(fails)} failures raised)")

        # ---- G6, both directions, against the LIVE held-out split hash -------------
        held = ROOT / "wiki" / "skills-gate" / "validation" / "exchange-letters" / "heldout.sha256"
        if not held.is_file():
            print("SELFTEST FAIL: G6 cannot be exercised -- no exchange-letters heldout.sha256")
            return 1
        sha8 = held.read_text(encoding="utf-8").split()[0][:8]
        prose = chr(10).join([
            "- PROP-800",
            "",
            "## PROP-800 (2026-09-03) -- ACCEPTED",
            "",
            "- **From:** fixture",
            "- **Motivating record:** fixture",
            "- **Diff:** AMEND `skills/exchange-letters/SKILL.md`",
            "- **Probe:** the cold reader found it clearer. Strict improvement: yes.",
            "- **Verdict:** ACCEPTED.",
            "",
        ])
        numeric = prose.replace("- **Probe:** the cold reader found it clearer. Strict improvement: yes.",
                                f"- **Probe:** R_before=0.8672@{sha8} -> R_after=0.9141@{sha8}")
        pf = [f for f in check(prose, "strict revert", ROOT) if f.startswith("G6")]
        nf = [f for f in check(numeric, "strict revert", ROOT) if f.startswith("G6")]
        if not pf:
            print("SELFTEST FAIL: planted prose-only ACCEPTED row did NOT trigger G6")
            return 1
        if nf:
            print(f"SELFTEST FAIL: numeric ACCEPTED row wrongly triggered G6: {nf}")
            return 1
        print(f"SELFTEST PASS (G6, prose branch): {pf[0]}")
        print(f"SELFTEST PASS (G6, numeric branch): row citing split {sha8} raises no G6 failure")

        tie = numeric.replace(f"R_after=0.9141@{sha8}", f"R_after=0.8672@{sha8}")
        stale = numeric.replace(f"R_after=0.9141@{sha8}", "R_after=0.9141@deadbeef")
        for label, text in (("tie", tie), ("stale-split", stale)):
            gf = [f for f in check(text, "strict revert", ROOT) if f.startswith("G6")]
            if not gf:
                print(f"SELFTEST FAIL: {label} row did NOT trigger G6")
                return 1
            print(f"SELFTEST PASS (G6, {label} branch): {gf[0]}")
        return 0

    if not LEDGER.is_file() or not SPEC.is_file():
        print("UNKNOWN: LEDGER.md or GATE-SPEC.md missing -- not a pass")
        return 2
    fails = check(LEDGER.read_text(encoding="utf-8"), SPEC.read_text(encoding="utf-8"), ROOT)
    if fails:
        for f in fails:
            print("GATE-CHECK FAIL:", f)
        return 1
    print("GATE-CHECK PASS: G1-G6 hold on the live ledger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
