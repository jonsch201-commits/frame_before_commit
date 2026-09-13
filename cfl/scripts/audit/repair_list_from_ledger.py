#!/usr/bin/env python3
"""repair_list_from_ledger.py — UC-0 (2026-09-02): derive the sealed repair list for the ultracode run.

The list is DERIVED from wiki/skills-gate/INGEST-LEDGER.md, never typed: a page belongs on it when
the LATEST ledger row for that page path is REJECTED with probe note
"not reached (LINT stopped the pipeline)" — i.e. REJECTED-lint. A page that was rejected-lint and
LATER re-gated to anything else (ACCEPTED by GATE-06, REJECTED-probe, UNKNOWN) is excluded, because
only the newest row is the page's current verdict.

"Latest" = the row that appears LAST in the file. The ledger is append-only and every row carries
the same date (2026-09-02), so file position is the only ordering the file offers; the merged
per-gate sections (GATE-00 .. GATE-RB) are concatenated in gate order and GATE-06's rows are
appended after them, so position == time for this file. If a future ledger interleaves dates, add a
timestamp sort here — do not silently trust position.

Per page the script prints:  path | failing E-checks | sha256 of the page bytes NOW
  - failing E-checks = every `Ek=grade` token in that row's lint summary whose grade is neither
    PASS nor N/A-kind (so FAIL, N/A-blocked and unrecov all count; the last one is why a repair
    can end UNKNOWN rather than ACCEPTED).
  - sha256 is computed from the page file on disk at run time (MISSING if the file is gone). The
    seal freezes these hashes so a page edited between seal and run is detectable.

Modes
  (default)            print the rows to stdout, then the total and the sha256 of the list text
  --seal-block         print a markdown block (fenced list + total + list sha256) for a SEAL file
  --verify-seal FILE   re-derive now and compare against the block embedded in FILE; exit 1 on drift
  --selftest           fixture ledger: A rejected-lint; B rejected-lint then ACCEPTED; C accepted
                       only; D rejected-fence. Must return exactly [A]. Exit 1 otherwise.

The list text whose sha256 is published is the canonical form: one line per page,
`<path>|<check,check,...>|<sha256>`, sorted by path, LF-terminated, UTF-8. Sorting by path (not
ledger order) makes the list reproducible regardless of how the ledger was merged.

PYTHONIOENCODING=utf-8 is expected; paths inside this program are Windows-style-agnostic (forward
slashes are what the ledger stores).
"""
import argparse
import hashlib
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_LEDGER = "wiki/skills-gate/INGEST-LEDGER.md"
LINT_NOTE = "not reached (LINT stopped the pipeline)"
ROW_RX = re.compile(r"^- (\d{4}-\d{2}-\d{2}) ([0-9a-f]{8}) (\S+) (ACCEPTED|REJECTED|UNKNOWN) (.*)$")
CHECK_RX = re.compile(r"(E\w+)=(\S+)")
OK_GRADES = {"PASS", "N/A-kind"}
BLOCK_BEGIN = "<!-- repair-list:begin -->"
BLOCK_END = "<!-- repair-list:end -->"


def sha256_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return "MISSING"


def latest_rows(ledger_path):
    """path -> (verdict, rest-of-index-line) for the LAST index line per page path."""
    latest = {}
    with open(ledger_path, encoding="utf-8") as f:
        for line in f:
            m = ROW_RX.match(line.rstrip("\n"))
            if m:
                latest[m.group(3)] = (m.group(4), m.group(5))
    return latest


def failing_checks(rest):
    return [k for k, v in CHECK_RX.findall(rest) if v not in OK_GRADES]


def derive(ledger_path, root="."):
    rows = []
    for path, (verdict, rest) in latest_rows(ledger_path).items():
        if verdict == "REJECTED" and LINT_NOTE in rest:
            rows.append((path, failing_checks(rest), sha256_file(os.path.join(root, path))))
    rows.sort(key=lambda r: r[0])
    return rows


def canonical_text(rows):
    return "".join("%s|%s|%s\n" % (p, ",".join(c), h) for p, c, h in rows)


def list_sha(rows):
    return hashlib.sha256(canonical_text(rows).encode("utf-8")).hexdigest()


def seal_block(rows, ledger_path):
    out = [BLOCK_BEGIN,
           "Derived by `scripts/audit/repair_list_from_ledger.py --seal-block` from `%s` "
           "(latest row per page = REJECTED, probe note `%s`). Verify with `--verify-seal <this file>`."
           % (ledger_path, LINT_NOTE),
           "", "```", canonical_text(rows).rstrip("\n"), "```", "",
           "- total: **%d** pages" % len(rows),
           "- sha256 of the canonical list text: `%s`" % list_sha(rows),
           BLOCK_END]
    return "\n".join(out) + "\n"


def verify_seal(seal_path, ledger_path, root):
    text = open(seal_path, encoding="utf-8").read()
    b, e = text.find(BLOCK_BEGIN), text.find(BLOCK_END)
    if b == -1 or e == -1:
        print("VERIFY: UNKNOWN — no repair-list block in %s" % seal_path)
        return 2
    block = text[b:e]
    m = re.search(r"sha256 of the canonical list text: `([0-9a-f]{64})`", block)
    t = re.search(r"total: \*\*(\d+)\*\*", block)
    if not m or not t:
        print("VERIFY: UNKNOWN — block lacks sha/total lines")
        return 2
    rows = derive(ledger_path, root)
    now = list_sha(rows)
    sealed_lines = re.search(r"```\n(.*?)\n```", block, re.S)
    sealed_rows = {}
    if sealed_lines:
        for ln in sealed_lines.group(1).splitlines():
            parts = ln.split("|")
            if len(parts) == 3:
                sealed_rows[parts[0]] = (parts[1], parts[2])
    if now == m.group(1) and len(rows) == int(t.group(1)):
        print("VERIFY: PASS — %d pages, list sha256 %s matches the seal" % (len(rows), now))
        return 0
    print("VERIFY: DRIFT — sealed sha %s / total %s; derived now sha %s / total %d"
          % (m.group(1), t.group(1), now, len(rows)))
    now_map = {p: (",".join(c), h) for p, c, h in rows}
    for p in sorted(set(sealed_rows) | set(now_map)):
        a, b_ = sealed_rows.get(p), now_map.get(p)
        if a != b_:
            print("  %s: sealed=%s now=%s" % (p, a, b_))
    return 1


def selftest():
    root = tempfile.mkdtemp(prefix="repair_list_selftest_")
    pages = {}
    for name in "ABCD":
        p = "wiki/sources/fixture/page-%s.md" % name
        full = os.path.join(root, p)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write("---\ntitle: %s\n---\nbody %s\n" % (name, name))
        pages[name] = p
    lint_fail = "E1k_kind=FAIL E1_form=PASS E2_anchor=PASS E3_fidelity=FAIL E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=unrecov"
    lint_ok = "E1k_kind=PASS E1_form=PASS E2_anchor=PASS E3_fidelity=PASS E4_uncap=PASS E5_link=PASS E6_find=PASS E7_prov=PASS E7m_reads=N/A-kind E8_fixity=PASS"
    ledger = os.path.join(root, "LEDGER.md")
    rows = [
        "- 2026-09-02 aaaaaaaa %s REJECTED %s %s" % (pages["A"], LINT_NOTE, lint_fail),
        "- 2026-09-02 bbbbbbbb %s REJECTED %s %s" % (pages["B"], LINT_NOTE, lint_fail),
        "- 2026-09-02 cccccccc %s ACCEPTED probe_sealed absent (accepted as given) %s" % (pages["C"], lint_ok),
        "- 2026-09-02 dddddddd %s REJECTED not reached (FENCE stopped the pipeline) %s" % (pages["D"], lint_ok),
        "- 2026-09-02 bbbbbbb2 %s ACCEPTED probe_sealed absent (accepted as given) %s" % (pages["B"], lint_ok),
    ]
    with open(ledger, "w", encoding="utf-8") as f:
        f.write("# fixture\n\n---\n" + "\n".join(rows) + "\n")
    got = derive(ledger, root)
    paths = [p for p, _, _ in got]
    ok = True
    if paths != [pages["A"]]:
        print("SELFTEST FAIL: expected [A] got %r" % paths); ok = False
    elif got[0][1] != ["E1k_kind", "E3_fidelity", "E8_fixity"]:
        print("SELFTEST FAIL: checks %r" % (got[0][1],)); ok = False
    elif got[0][2] != sha256_file(os.path.join(root, pages["A"])):
        print("SELFTEST FAIL: sha mismatch"); ok = False
    # negative control: the detector must fire if B's later ACCEPTED row is removed
    with open(ledger, "w", encoding="utf-8") as f:
        f.write("# fixture\n\n---\n" + "\n".join(rows[:-1]) + "\n")
    got2 = [p for p, _, _ in derive(ledger, root)]
    if got2 != [pages["A"], pages["B"]]:
        print("SELFTEST FAIL: negative control expected [A,B] got %r" % got2); ok = False
    print("SELFTEST %s (fixture %s): B rejected-then-accepted excluded=%s; D fence-rejected excluded=%s; "
          "negative control (B's ACCEPTED row removed -> B returns)=%s"
          % ("PASS" if ok else "FAIL", root, pages["B"] not in paths, pages["D"] not in paths,
             got2 == [pages["A"], pages["B"]]))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--root", default=".", help="repo root the ledger's page paths are relative to")
    ap.add_argument("--seal-block", action="store_true")
    ap.add_argument("--verify-seal", metavar="FILE")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--first", type=int, default=0, help="print only the first N rows (dry-run slice)")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.verify_seal:
        sys.exit(verify_seal(a.verify_seal, a.ledger, a.root))
    rows = derive(a.ledger, a.root)
    if a.seal_block:
        print(seal_block(rows, a.ledger), end="")
        return
    for p, c, h in (rows[:a.first] if a.first else rows):
        print("%s | %s | %s" % (p, ",".join(c), h))
    print("total: %d pages; sha256(list): %s" % (len(rows), list_sha(rows)))


if __name__ == "__main__":
    main()
