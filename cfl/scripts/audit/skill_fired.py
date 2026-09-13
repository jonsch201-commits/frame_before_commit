#!/usr/bin/env python3
"""skill_fired.py -- did frame-before-commit actually FIRE where it was required?

Jon, compass message 2026-09-09 (verbatim, typos his):
    "I don't see frame bedore commit or gound before stating or the literal vector
     embeded graph rag completeness or the automatic wiki updates i've asked for"
    "you need to help me see when I should have used a skill"

Companion to query_by_default.py. That one covers the QUERY axis. This one covers
the INVOCATION axis: `frame-before-commit` Extension v2 section 1 lists four
triggers that MUST self-invoke the protocol. Nothing in the fleet reports whether
they did.

THE FOUR TRIGGERS (Extension v2 s1, ratified WAYFINDER-008 2026-09-10)
    1. committing to a major architecture or roadmap change
    2. emitting an outward dispatch to a peer trunk
    3. asserting that something "does not exist"
    4. selecting between multi-model / tool execution paths under budget constraint

EVIDENCE THAT IT FIRED
    A run is only credited when a SEAL exists -- the skill's own rule since
    2026-08-06: an unsealed run scores UNKNOWN for movement. So this looks for a
    seal write (wiki/test-outputs/seals/) or an explicit [FRAME-BEFORE-COMMIT
    marker, within --window tool calls BEFORE the trigger.

WHAT IT REFUSES TO DO
    It does not score the run's quality and it does not gate. Trigger 1 and 4 are
    not reliably detectable from a transcript, so it reports them as UNDETECTABLE
    rather than as zero -- a class it cannot see must never render as a class that
    did not occur. UNKNOWN dominates a PASS.

EXIT
    0 always.
"""
import argparse
import io
import json
import os
import re
import sys

SEAL_WRITE = re.compile(r"test-outputs[/\\]seals[/\\]SEAL-|PRE-BRANCH SEAL", re.I)
FBC_MARK = re.compile(r"\[FRAME-BEFORE-COMMIT|\[BRANCH REGISTRY\]|\[LABEL ASSIGNMENT\]", re.I)
# Trigger 2: a write or copy whose destination is a peer trunk's inbound, or our outbox.
DISPATCH = re.compile(
    r"(?:claude-(?:professional|secretary|personal|corpus)|antigravity-hub)[/\\]exchange[/\\]inbound"
    r"|exchange[/\\]outbox[/\\]",
    re.I,
)
# Trigger 3: a negative-existence assertion in the seat's own prose.
NEGATIVE = re.compile(
    r"\b(?:does not exist|do(?:es)? not exist|no such|nothing (?:exists|is there)|"
    r"never (?:existed|written)|zero version-controlled|no primary exists|"
    r"has no producer|CORPUS SILENT)\b",
    re.I,
)


def blocks(path):
    """Yield (n, kind, name, text) over assistant tool_use and text blocks, in order."""
    n = 0
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            msg = rec.get("message") or {}
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    n += 1
                    yield n, "tool", b.get("name", ""), json.dumps(b.get("input") or {},
                                                                  ensure_ascii=False)
                elif b.get("type") == "text":
                    yield n, "text", "", b.get("text", "")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jsonl", nargs="?")
    ap.add_argument("--window", type=int, default=40,
                    help="tool calls back that a seal still counts as covering a trigger")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return selftest()

    path = args.jsonl or os.environ.get("CLAUDE_SESSION_JSONL", "")
    if not path or not os.path.exists(path):
        print("UNKNOWN: no session JSONL. A check that could not run is UNKNOWN, not a PASS.")
        return 0

    last_fbc = None
    fired = 0
    covered, uncovered = [], []
    for n, kind, name, text in blocks(path):
        if SEAL_WRITE.search(text) or FBC_MARK.search(text):
            if last_fbc is None or n - last_fbc > 3:
                fired += 1
            last_fbc = n
            continue
        trig = None
        if kind == "tool" and DISPATCH.search(text):
            trig = "dispatch"
        elif kind == "text" and NEGATIVE.search(text):
            trig = "negative-assertion"
        if trig:
            rec = (n, trig, (text[:70].replace("\n", " ")))
            if last_fbc is not None and (n - last_fbc) <= args.window:
                covered.append(rec)
            else:
                uncovered.append(rec)

    print(f"session : {os.path.basename(path)}")
    print(f"window  : {args.window} tool calls")
    print(f"frame-before-commit runs with a SEAL : {fired}")
    print()
    print(f"trigger 2 + 3 events COVERED by a run : {len(covered)}")
    print(f"trigger 2 + 3 events NOT covered      : {len(uncovered)}")
    print("trigger 1 (architecture/roadmap) and 4 (model/path choice): UNDETECTABLE from a")
    print("  transcript. Reported as UNDETECTABLE, never as zero. UNKNOWN dominates a PASS.")
    print()
    if uncovered:
        print("NOT COVERED -- candidates, not verdicts:")
        for n, trig, snip in uncovered[:15]:
            print(f"  call #{n:<4} {trig:<18} {snip}")
        if len(uncovered) > 15:
            print(f"  ... and {len(uncovered) - 15} more")
    else:
        print("Every detectable trigger had a sealed run within the window.")
    return 0


def selftest():
    cases = [
        ("seal write detected", SEAL_WRITE.search("wiki/test-outputs/seals/SEAL-x-2026-09-11.md"), True),
        ("fbc marker detected", FBC_MARK.search("[FRAME-BEFORE-COMMIT — PURE — 4 branches]"), True),
        ("plain prose is not a seal", SEAL_WRITE.search("I thought about it carefully"), False),
        ("peer inbound is a dispatch", DISPATCH.search("N:/claude-secretary/exchange/inbound/x.md"), True),
        ("own outbox is a dispatch", DISPATCH.search("exchange/outbox/letter.md"), True),
        ("wiki write is not a dispatch", DISPATCH.search("wiki/concepts/thing.md"), False),
        ("negative assertion caught", NEGATIVE.search("that file does not exist anywhere"), True),
        ("hedged absence caught", NEGATIVE.search("returns CORPUS SILENT for this"), True),
        ("ordinary sentence is not one", NEGATIVE.search("the index was rebuilt today"), False),
    ]
    ok = 0
    for label, got, want in cases:
        good = bool(got) == want
        ok += good
        print(f"  {'PASS' if good else 'FAIL'}  {label}")
    print(f"selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
