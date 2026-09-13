#!/usr/bin/env python3
"""for_jon_routed.py -- RE-2: did every item marked "for Jon" go through Secretary first?

Jon, 2026-09-05 (WW-5): "route through secretary by default and if it believe its for me afteer co trunk
review well ok fine then." Jon, 2026-09-06 09:03/09:07/09:18: "routing error" -- four seats asked the same
question in ninety minutes. [measured 2026-09-06] CFL's own instance: five consecutive reports ended with
a WHAT I NEED FROM YOU block and none of its items had gone to Secretary; when they finally did (RE-1), the
routing seat judged THREE OF FOUR were not Jon's.

This is the check the skill `present-to-jon` now names. It reads a markdown file, finds the for-Jon block
(a heading or bold line containing WHAT I NEED FROM YOU or JON SELECTION), and for every list item under
it requires a routing receipt of the form  `via: <path>`  or  `[routed: <path>]`  where <path> is a file
that exists (Secretary's ruling or letter that carried the item). An item without one prints UNROUTED.

Exit: 0 all routed · 3 at least one UNROUTED · 2 no for-Jon block found (UNKNOWN, never a pass).
Selftest exercises BOTH verdicts and the UNKNOWN case:  python for_jon_routed.py --selftest
"""
import io
import os
import re
import sys
import tempfile

BLOCK_RE = re.compile(r"(WHAT I NEED FROM YOU|JON SELECTION)", re.I)
ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+(.*)$")
VIA_RE = re.compile(r"(?:via:\s*|\[routed:\s*)`?([^`\]\s]+)`?")
END_RE = re.compile(r"^(#{1,6}\s|---\s*$|\*\*[A-Z][^*]{3,}\*\*\s*$)")


def check(path, root=None):
    root = root or os.path.dirname(os.path.abspath(path))
    text = io.open(path, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()
    rows, in_block, found = [], False, False
    for ln in lines:
        if BLOCK_RE.search(ln) and not in_block:
            in_block, found = True, True
            continue
        if in_block:
            if END_RE.match(ln) and not ITEM_RE.match(ln):
                in_block = False
                continue
            m = ITEM_RE.match(ln)
            if not m:
                continue
            item = m.group(1).strip()
            v = VIA_RE.search(item)
            if not v:
                rows.append(("UNROUTED", "no via:/[routed:] receipt", item[:90]))
                continue
            p = v.group(1)
            cands = [p, os.path.join(root, p), os.path.expanduser(p)]
            ok = any(os.path.isfile(c) for c in cands)
            rows.append(("ROUTED" if ok else "UNROUTED", p if ok else f"receipt path does not exist: {p}", item[:90]))
    return rows, found


def main(argv):
    if "--selftest" in argv:
        return self_test()
    if len(argv) < 2:
        print("usage: for_jon_routed.py <report-or-letter.md>  |  --selftest")
        return 2
    rows, found = check(argv[1])
    if not found:
        print("UNKNOWN: no WHAT I NEED FROM YOU / JON SELECTION block found -- nothing checked, not a pass")
        return 2
    bad = 0
    for verdict, why, item in rows:
        bad += verdict == "UNROUTED"
        print(f"  {verdict:9s} {item}  [{why}]")
    print(f"for-jon items: {len(rows)}  routed: {len(rows) - bad}  UNROUTED: {bad}")
    return 3 if bad else 0


def self_test():
    d = tempfile.mkdtemp()
    receipt = os.path.join(d, "secretary-RULING-x.md")
    io.open(receipt, "w").write("ruling\n")
    fails = 0

    def ok(name, got, want):
        nonlocal fails
        good = got == want
        fails += 0 if good else 1
        print(("PASS " if good else "FAIL ") + f"{name}: got {got!r} want {want!r}")

    routed = os.path.join(d, "routed.md")
    io.open(routed, "w").write("# report\n\n**WHAT I NEED FROM YOU:**\n- send the compact  via: secretary-RULING-x.md\n- next  [routed: secretary-RULING-x.md]\n\n## after\n- not an item of the block\n")
    rows, found = check(routed)
    ok("routed: block found", found, True)
    ok("routed: two items, both ROUTED", [r[0] for r in rows], ["ROUTED", "ROUTED"])
    unrouted = os.path.join(d, "unrouted.md")
    io.open(unrouted, "w").write("**WHAT I NEED FROM YOU:**\n- send the compact\n- SSP is yours to decide via: does-not-exist.md\n")
    rows, found = check(unrouted)
    ok("unrouted: both UNROUTED (missing receipt; nonexistent path)", [r[0] for r in rows], ["UNROUTED", "UNROUTED"])
    none = os.path.join(d, "none.md")
    io.open(none, "w").write("# nothing for jon here\n- a list\n")
    rows, found = check(none)
    ok("no block: found=False (UNKNOWN, not pass)", found, False)
    print(f"selftest: {4 - fails}/4")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
