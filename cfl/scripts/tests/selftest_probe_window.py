#!/usr/bin/env python3
"""selftest_probe_window.py -- GATE-07: the probe packet's raw slice covers EVERY anchor the sealed
question names, prints its windows, and stays selective (it is not the whole raw).

Motivating record: S-cd-02 report 2026-09-02, finding 1 -- three sealed questions aimed at anchors
outside the +/-200-line window around the MEDIAN cited anchor graded UNKNOWN on coverage alone.

Fixture: a synthetic fl-style raw of 1,200 lines with `## Human` turns at lines ~50, ~600, ~1150;
a page citing :T1 and :T3 whose sealed question names :T3 (far from the median). Checks:
  1. the slice contains the T3 header line (the sealed anchor) -- FAILS on the pre-GATE-07 code
  2. the slice contains the T1 header line (the median window is kept)
  3. the slice does NOT contain the T2 header line at ~600 (selective: not the whole raw)
  4. raw_meta names the sealed anchor and prints more than one window
  5. a sealed anchor not in the index is reported as NOT IN INDEX, never silently dropped
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audit"))
import ingest_gate  # noqa: E402

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (("  " + detail) if detail else ""))
    if not ok:
        fails.append(name)


def main():
    root = tempfile.mkdtemp(prefix="gate07_")
    rawdir = os.path.join(root, "raw", "transcripts", "claude-code", "fl")
    os.makedirs(rawdir)
    lines = ["filler line %d\n" % i for i in range(1, 1201)]
    markers = {}
    for t, at in ((1, 50), (2, 600), (3, 1150)):
        lines[at - 1] = "## Human\n"
        lines[at] = "TURN%d-UNIQUE-SENTINEL\n" % t
        markers[t] = "TURN%d-UNIQUE-SENTINEL" % t
    raw_rel = "raw/transcripts/claude-code/fl/code-2026-09-02-ffffff-gate07-fixture.md"
    raw_path = os.path.join(root, raw_rel.replace("/", os.sep))
    with open(raw_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)
    fm = {"source_file": raw_rel, "probe_sealed": "what does :T3 say => TURN3"}
    page_text = "## Key Claims\n- claim one :T1\n- claim three :T3\n"
    page_path = os.path.join(root, "gate07-page.md")
    with open(page_path, "w", encoding="utf-8") as f:
        f.write("---\nsource_file: %s\n---\n%s" % (raw_rel, page_text))
    out = os.path.join(root, "packets")
    os.makedirs(out)

    packet = ingest_gate.write_probe_packet(page_path, fm, page_text, root, out)
    body = open(packet, encoding="utf-8").read()
    slice_part = body.split("## Raw slice", 1)[1].split("## Page text", 1)[0]
    meta = slice_part.split("\n", 1)[0]

    check("1 sealed anchor T3 (line 1150) inside the slice", markers[3] in slice_part)
    check("2 median-window anchor T1 (line 50) inside the slice", markers[1] in slice_part)
    check("3 uncited T2 (line 600) NOT in the slice (selective)", markers[2] not in slice_part)
    check("4 meta names the sealed anchor and >1 window", "[3]" in meta and meta.count("-") >= 2, meta[:140])

    fm2 = dict(fm, probe_sealed="what does :T9 say => nothing")
    packet2 = ingest_gate.write_probe_packet(page_path, fm2, page_text, root, out)
    meta2 = open(packet2, encoding="utf-8").read().split("## Raw slice", 1)[1].split("\n", 1)[0]
    check("5 sealed anchor absent from index is reported", "NOT IN INDEX: [9]" in meta2, meta2[:140])

    print("SELFTEST", "PASS" if not fails else "FAIL %s" % fails)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
