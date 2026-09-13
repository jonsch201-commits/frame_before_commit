#!/usr/bin/env python3
"""check_vocabulary.py — structural conformance for wiki/references/vocabulary.md (ticket S-4).

⛔ WHAT THIS IS NOT, said first because the tempting version is the wrong one. This is NOT a
term-drift detector. S-4's closure test — "a term used in a second sense is detected, not
remembered" — is a real design problem, and `/su-compact` says in as many words: do not build that
on the way out. ⭐ So this checks the ONE thing that is mechanically checkable and currently unchecked:
**does the glossary conform to its own stated contract.**

THE CONTRACT, from the page's own opening paragraph:
    "Per term below: the one referent it keeps, and the uses it must NOT have —
     the negative half is what makes it enforceable."

So an entry without its negative half is not a weak entry; it is a **restatement**, which is the
exact failure `skills/domain-modeling/SKILL.md` names as the "redundant flat scalar". And a term with
TWO entries is a glossary equivocating on the term it reserved — the defect the page exists to stop,
happening inside the page.

⚠️ NEVER wire this file into retrieval weighting. The 2026-08-07 alias poisoning is the measured
precedent: mined aliases scored 200 EXACT, ordinary English fragments became the highest-weighted
retrieval keys in the wiki, and 76 hand-authored sets had to be restored. A decoding key is not a
retrieval key.

Usage:  python scripts/audit/check_vocabulary.py [--page PATH] [--strict] [--self-test]
Exit:   0 conformant, 1 defects (--strict only), 2 the page is unreachable.
"""
import argparse
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_PAGE = os.path.join(REPO, "wiki", "references", "vocabulary.md")

# A heading is an ENTRY when its text is a term. Two generations of format coexist on the page:
#   gen 1 (2026-08-06):  ## triage
#   gen 2 (2026-08-08+): ## `trunk` — ⚠️ IN CONFLICT, and the conflict is the entry
# Both are legitimate; the term is the backticked token if present, else the whole heading.
# ⚠️ A heading that is a SENTENCE is not an entry — e.g. "## What was corrected on sight (…)".
# Guessing wrong in that direction invents defects, so the sentence test is deliberately blunt:
# more than four words AND no backticks means prose.
TERM_RE = re.compile(r"^##\s+(.*?)\s*$")
BACKTICK = re.compile(r"^`([^`]+)`")


def parse(text):
    """-> list of (term, heading_line_no, body). Non-entry headings are returned separately."""
    lines = text.splitlines()
    heads = [(i + 1, m.group(1)) for i, l in enumerate(lines) if (m := TERM_RE.match(l))]
    entries, prose = [], []
    for idx, (ln, head) in enumerate(heads):
        end = heads[idx + 1][0] - 1 if idx + 1 < len(heads) else len(lines)
        body = "\n".join(lines[ln:end])
        bt = BACKTICK.match(head)
        if bt:
            term = bt.group(1)
        elif len(head.split()) > 4:
            prose.append((ln, head))
            continue
        else:
            term = head
        entries.append((term, ln, body))
    return entries, prose


def audit(text):
    entries, prose = parse(text)
    no_keeps, no_negative, dupes = [], [], {}
    for term, ln, body in entries:
        # Tolerant on purpose: real entries write "**Keeps:**", "**Keeps (authority sense):**" and
        # "**Keeps three distinguishable senses...**". A strict `**Keeps:**` match reported three
        # false defects on the first run of this script.
        if "**Keeps" not in body:
            no_keeps.append((term, ln))
        if "**Must NOT" not in body and "must NOT" not in body:
            no_negative.append((term, ln))
        dupes.setdefault(term.strip().lower(), []).append((term, ln))
    dupes = {k: v for k, v in dupes.items() if len(v) > 1}
    return entries, prose, no_keeps, no_negative, dupes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", default=DEFAULT_PAGE)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not os.path.isfile(a.page):
        print(f"⛔ UNKNOWN — page unreachable: {a.page}", file=sys.stderr)
        return 2
    text = open(a.page, encoding="utf-8", errors="ignore").read()
    entries, prose, no_keeps, no_negative, dupes = audit(text)

    print("=== check_vocabulary ===")
    print(f"  page     : {os.path.relpath(a.page, REPO)}")
    print(f"  entries  : {len(entries)}   (non-entry headings skipped: {len(prose)})")
    print()
    if dupes:
        print("  ⛔ DUPLICATE TERM — the glossary equivocates on a term it reserved. This is the")
        print("     defect the page exists to stop, happening inside the page.")
        for k, v in sorted(dupes.items()):
            where = " · ".join(f"line {ln}" for _t, ln in v)
            print(f"      {k}  —  {len(v)} entries at {where}")
        print()
    if no_negative:
        print("  ⚠️  NO NEGATIVE HALF — the page's own contract: \"the negative half is what makes")
        print("      it enforceable.\" Without it an entry is a restatement, not a reservation.")
        for t, ln in no_negative:
            print(f"      line {ln:>4}  {t}")
        print()
    if no_keeps:
        print("  ⚠️  NO 'Keeps' — the entry says what a term must not mean and never says what it does.")
        for t, ln in no_keeps:
            print(f"      line {ln:>4}  {t}")
        print()
    if not (dupes or no_negative or no_keeps):
        print("  ✅ every entry carries both halves and no term is defined twice.")
        print()
    print("  ⛔ BOUND, and it is most of the ticket: THIS DETECTS NOTHING ABOUT USAGE. A term used")
    print("     in a second sense somewhere in the repo is invisible here. S-4's closure test —")
    print("     'a term used in a second sense is DETECTED, not remembered' — is NOT met by this")
    print("     script and is a real design problem, not an oversight.")
    bad = len(dupes) + len(no_negative) + len(no_keeps)
    return 1 if (bad and a.strict) else 0


def self_test():
    fails = []
    good = ("## alpha\n\n**Keeps:** one thing.\n\n**Must NOT mean:** another.\n"
            "## `beta` — a term with a descriptive heading\n\n"
            "**Keeps (one sense):** x.\n\n**Must NOT mean:** y.\n")
    e, p, nk, nn, d = audit(good)
    if len(e) != 2:
        fails.append(f"expected 2 entries, got {len(e)}")
    if nk or nn or d:
        fails.append("a conformant page reported defects")
    # ⭐ The tolerant matcher, which the first run got wrong: "**Keeps (authority sense):**" and
    # "**Keeps three distinguishable senses**" are real forms on the live page.
    if audit("## g\n\n**Keeps three senses:** a.\n\n**Must NOT** b.\n")[2]:
        fails.append("'Keeps three senses' was not accepted as a Keeps clause")
    # Missing negative half must fire.
    if not audit("## solo\n\n**Keeps:** only this.\n")[3]:
        fails.append("an entry with no negative half was not flagged")
    # Duplicate term must fire, case-insensitively and across both heading formats.
    dup = "## Herald\n\n**Keeps:** a.\n\n**Must NOT** b.\n## `herald` — names three things\n\nx\n"
    if not audit(dup)[4]:
        fails.append("a term defined twice was not flagged")
    # A sentence heading is prose, not an entry — flagging it would invent a defect.
    if audit("## What was corrected on sight in present-tense prose only\n\nx\n")[0]:
        fails.append("a sentence heading was treated as a term entry")

    print("=== SELF-TEST — check_vocabulary.py ===")
    if fails:
        for f in fails:
            print(f"  FAIL: {f}")
        print(f"\nRESULT: FAIL — {len(fails)} failure(s)")
        return 1
    checks = [
        "both heading generations parse as entries",
        "a conformant page reports no defects",
        "'Keeps (qualified)' forms are accepted, not flagged",
        "an entry with no negative half is flagged",
        "a term defined twice is flagged, case-insensitively",
        "a sentence heading is prose, not an invented entry",
    ]
    for c in checks:
        print(f"  {c:<58}: PASS")
    print(f"\nRESULT: PASS — {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
