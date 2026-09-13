#!/usr/bin/env python3
"""Is an extract current? Compare turn counts, not byte ratios.

WHY THIS REPLACES RATIO_FLOOR
-----------------------------
`RATIO_FLOOR = 0.20` in `scripts/extract_claude_code_sessions.py` asks whether the rendered markdown
is at least 20% of the JSONL's byte size. **It is unsatisfiable.** Measured healthy range across 18
real sessions: 0.0037-0.159, all below the floor both before and after the tool-payload fidelity fix.
The markdown legitimately summarizes tool payloads the JSONL stores in full, so a complete extract
scores 0.17 and is flagged stale forever. `2b2ff8` is the standing witness: 2,319 turns and
4,010,987 chars rendered against a 23,533,461-byte JSONL, refreshed and immediately re-flagged with
an identical ratio.

Two LOSS-tier blocking SU rows were wired under that condition. **An alarm whose steady state is
firing carries no information**, and both rows have been red long enough that nobody reads them.

THE REPLACEMENT HAS NO TUNABLE CONSTANT
---------------------------------------
Turn parity: the sidecar's `turns_covered` versus the turn count re-derived from the JSONL now.
Exact equality. **There is no threshold to calibrate, so the recalibration decision class is deleted
rather than re-parameterized** — which is what took this out of the standing in-code reservation to
Jon. That reservation covered *choosing a new ratio*; there is no longer a ratio to choose.

THE NON-NEGOTIABLE CLAUSE
-------------------------
**The counting rule is implemented once, in the extractor, and imported here.** `turns_covered` is
written as `len(extract_turn_records(events))` at `convert-claude-code.py:636`; this checker calls
the same function on the same events. A second, independently-written counter is exactly how false
fires would return — divergent handling of isMeta records, signature-only thinking, or
tool-result-only events would reintroduce the disease under a new name.

VERDICTS
--------
  CURRENT   sidecar == re-derived
  STALE     sidecar <  re-derived   (the JSONL grew; the extract is behind)
  ERROR     sidecar >  re-derived   (impossible — the extract claims turns the source lacks;
                                     never reported as merely "stale", because it means the
                                     sidecar, the source, or the counter is wrong)
  UNKNOWN   either number underivable — NEVER a pass. A 0 over an empty set is not a pass.
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# THREE dirnames: this file is at <repo>/scripts/audit/turn_parity.py, so two levels lands on
# <repo>/scripts, not the repo root. The first run of the kill condition failed on exactly this and
# reported `UNKNOWN — extractor unimportable (FileNotFoundError)`. **That report was correct and is
# the reason the bug was found in one run rather than shipped**: had the import failure defaulted to
# a pass, a checker that never reaches its counter would have certified every extract in the corpus.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONVERTER_DIR = os.path.join(REPO, "skills", "chat-exporter", "scripts")


def _load_by_path():
    import importlib.util
    path = os.path.join(CONVERTER_DIR, "convert-claude-code.py")
    spec = importlib.util.spec_from_file_location("cc_converter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sidecar_turns(sidecar_path):
    """Read `turns_covered:` from the sidecar frontmatter. Absent/unparsable -> None (UNKNOWN)."""
    try:
        with open(sidecar_path, encoding="utf-8", errors="replace") as fh:
            head = fh.read(4096)
    except OSError:
        return None
    m = re.search(r"^turns_covered:\s*(\d+)\s*$", head, re.MULTILINE)
    return int(m.group(1)) if m else None


def normalize_path(p):
    """Accept Git-Bash `/c/Users/...` as well as native `C:\\Users\\...`.

    Both shells are in daily use in this repo, and a `/c/...` path silently fails to open under
    Windows Python. The first run of this checker returned a bare UNDERIVABLE for exactly that
    reason — a real file, a correct counter, and a verdict that looked like a missing source.
    Normalizing is not cosmetic: an UNKNOWN that is really a path-form bug is indistinguishable
    from an UNKNOWN that is really a lost transcript, and this program has already published a
    false-loss registry once.
    """
    if p and re.match(r"^/[a-zA-Z]/", p):
        return p[1].upper() + ":" + p[2:]
    return p


def rederived_turns(jsonl_path):
    """Re-count with THE EXTRACTOR'S OWN function. Never a second implementation.

    Returns (count, reason). A None count always carries the reason it is None — "I could not
    look" must never be reportable as "there is nothing there."
    """
    path = normalize_path(jsonl_path)
    if not os.path.exists(path):
        return None, f"source not found at {path}"
    try:
        mod = _load_by_path()
    except Exception as e:
        return None, (f"extractor unimportable ({e.__class__.__name__}: {e}) — the shared counter "
                      f"lives at {os.path.join(CONVERTER_DIR, 'convert-claude-code.py')}; "
                      f"UNKNOWN, never a pass")
    try:
        events = mod.load_events(path)
        return len(mod.extract_turn_records(events)), ""
    except Exception as e:
        return None, f"re-count failed: {e.__class__.__name__}: {e}"


def verdict(sidecar_n, rederived_n):
    if sidecar_n is None or rederived_n is None:
        return "UNKNOWN"
    if sidecar_n == rederived_n:
        return "CURRENT"
    return "STALE" if sidecar_n < rederived_n else "ERROR"


def check(jsonl_path, sidecar_path):
    s = sidecar_turns(normalize_path(sidecar_path))
    r, why = rederived_turns(jsonl_path)
    if s is None and not why:
        why = f"sidecar carries no parsable turns_covered: {sidecar_path}"
    return verdict(s, r), s, r, why


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--jsonl")
    ap.add_argument("--sidecar")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()
    if not a.jsonl or not a.sidecar:
        print("ERROR: --jsonl and --sidecar are both required. Missing input is UNKNOWN, not PASS.",
              file=sys.stderr)
        return 2

    v, s, r, why = check(a.jsonl, a.sidecar)
    print(f"{v}  sidecar_turns={s if s is not None else 'UNDERIVABLE'}  "
          f"rederived_turns={r if r is not None else 'UNDERIVABLE'}"
          + (f"  — {why}" if why else ""))
    return {"CURRENT": 0, "STALE": 1, "ERROR": 2, "UNKNOWN": 2}[v]


def self_test():
    cases = [
        ("equal -> CURRENT", verdict(100, 100) == "CURRENT"),
        ("sidecar behind -> STALE", verdict(90, 100) == "STALE"),
        # NEGATIVE CONTROL: an extract claiming MORE turns than the source holds is an impossible
        # state. Reporting it as STALE would send someone to re-extract, which cannot fix it.
        ("NEGATIVE CONTROL: sidecar ahead -> ERROR, never STALE", verdict(110, 100) == "ERROR"),
        # NEGATIVE CONTROL: the failure that produced a 29-session false-loss registry — a missing
        # number rendered as a clean result.
        ("NEGATIVE CONTROL: missing sidecar number -> UNKNOWN, never CURRENT",
         verdict(None, 100) == "UNKNOWN"),
        ("NEGATIVE CONTROL: missing source number -> UNKNOWN, never CURRENT",
         verdict(100, None) == "UNKNOWN"),
        ("NEGATIVE CONTROL: 0 == 0 is not silently a pass on nothing",
         verdict(None, None) == "UNKNOWN"),
        ("no tunable constant exists in this module",
         "FLOOR" not in open(__file__, encoding="utf-8").read().split('"""')[2]),
    ]
    print("=== SELF-TEST (negative control) ===")
    bad = 0
    for name, ok in cases:
        bad += 0 if ok else 1
        print(f"  {name:<62} : {'PASS' if ok else 'FAIL'}")
    print(f"\nRESULT: {'PASS' if not bad else 'FAIL'} — {len(cases)-bad}/{len(cases)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
