#!/usr/bin/env python3
"""A5 — every wake on disk must have a terminal row, checked from OUTSIDE the operator.

WHY THIS EXISTS (CFL, 2026-08-17 15:3x).
  Proposal v1 §6 named the hole in its own R3: "R3 reconciles wakes against records; it runs
  INSIDE the process it would need to check." A reconciler that dies with its host cannot report
  that its host died. This script is the same check run from a receiving seat, so the operator
  being wedged, restarted, or dead is a finding rather than a silence.

  It is also the acceptance test A5 from the proposal, made runnable:
      PASS  every wake-*.json in the retention window has >= 1 terminal row
      FAIL  terminal_rows < wakes_on_disk   -- and the DENOMINATOR is printed, never just the
            verdict, because "0 unmatched out of 0 resolvable" has already passed a blocking
            gate in this repo by resolving nothing.

⚠️ ITS OWN FIRST RUN OVER-REPORTED, and the correction is baked in below rather than commented.
  v1 judged EVERY wake against the operator's delivery ledger and returned "34/44 unaccounted".
  That denominator was wrong: there are TWO consumers. The operator owns cfl + professional;
  the relay (relay3.mjs) owns personal. Blaming the operator for a personal wake is the same
  wrong-tree defect this repo has now hit four times. v2 splits by target and grades each
  consumer against the record IT keeps.
  ⭐ And the split is what found the real thing: `.switchboard/ledger.jsonl` has 44 `wake_path`
  rows -- one per wake file -- and ZERO rows mentioning delivery of any kind. The relay records
  that a wake was RAISED and never records what became of it. So for its own trunk there is no
  "elsewhere" to look.

WHAT IT CANNOT DO, stated because a tool that hides its bound is the thing this repo keeps
building:
  - It measures RECORDS, not arrivals. Only the woken seat can attest that a turn happened.
    An unaccounted wake here means "no ledger anywhere says what became of it", NOT "it was
    never delivered".
  - `operator-deliveries.jsonl` rows are written by the CALLER at spawn INTENT, before the
    single-flight lock is even attempted (switchboard-operator.sh:147/165/176 -> run_delivery).
    So a `kind: wake|letter|continuation` row means "a delivery turn was started", NOT
    "a turn arrived". That is CFL finding D17; until it is fixed, --strict treats a row that is
    contradicted by a later `expired-in-flight` row for the same `what` as NOT terminal-success.
  - A wake younger than IN_FLIGHT_SEC is in flight, not unaccounted. R3's own rule is
    "older than 2 tick periods".
  - Wake files are NOT deleted on consumption (the operator's own 6 are still on disk), so
    file-presence is not a signal either way. Only the ledgers are.

Usage:
  python scripts/audit/wake_terminal_rows.py [--window-min 240] [--strict] [--all]

Exit codes: 0 every consumer accounted for its own scope · 1 unaccounted wakes found
            · 2 inputs unreadable.
"""

import argparse
import datetime as dt
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SB_WAKE = os.path.join("G:" + os.sep, "My Drive", "Claude", ".switchboard", "wake")
LEDGER = os.path.join(
    "G:" + os.sep, "My Drive", "Claude", "Claude Secretary", "scripts",
    "operator-deliveries.jsonl",
)
SB_LEDGER = os.path.join("G:" + os.sep, "My Drive", "Claude", ".switchboard", "ledger.jsonl")

# ⛔ v3, 2026-08-17 16:4x — THE INSTRUMENT WAS GRADING THE WRONG ROW, AND ITS PASS WAS MINE.
#
# v2 set TERMINAL_OK = {"wake","letter","continuation"} — the SPAWN-INTENT kinds — and on that
# definition returned "operator: 6 in scope, 6 accounted, 0 UNACCOUNTED ✅", which CFL published
# at 15:39 and asked to be read "as loudly as the failure."
#
# ⭐ That PASS was obtained by counting the exact rows CFL's own D17 says are not deliveries.
# A file named wake_terminal_rows.py could not fail on the defect it was written next to: the
# only rows it accepted as terminal were the intent rows, so an operator that started every
# delivery and completed none would score 100%.
#
# The Secretary implemented R2's real terminal rows in the 15:4x loop
# (switchboard-operator.sh:101/113/117 -> `expired-in-flight`, `<kind>-completed`,
# `<kind>-failed-rc<N>`). So the honest definition is now available and this is it:
#   CLAIM_KINDS  a delivery turn was STARTED  (written before the flight lock is attempted)
#   TERMINAL     a delivery turn ENDED, one way or the other
# `--legacy-intent-is-terminal` reproduces the v2 number so the two are comparable in one run;
# both are printed every time, because a silent redefinition is how the first number survived.
CLAIM_KINDS = {"wake", "letter", "continuation"}
TERMINAL_BAD = {"expired-in-flight", "dropped", "held"}


def is_terminal_ok(kind):
    return bool(kind) and kind.endswith("-completed")


def is_terminal_bad(kind):
    return bool(kind) and (kind in TERMINAL_BAD or "-failed-rc" in kind)

# Which consumer owns which target, and which record that consumer keeps.
# switchboard-operator.sh:30-34 declares TRUNK_DIR for exactly these three; but the relay's
# scope is personal-only (D3: allowMultiTarget false), and the operator was added to cover the
# other two. Both consumers can touch personal; only the operator touches cfl/professional.
OPERATOR_SCOPE = {"cfl", "professional"}
RELAY_SCOPE = {"personal"}

# R3: "older than 2 tick periods". Ticks run ~30s; 2 periods plus slack.
IN_FLIGHT_SEC = 180


def read_rows(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    # Paths cross the shell/python boundary as ARGV, never inside program text
    # (Secretary, 2026-08-17 15:22; reproduced by CFL the same hour on Windows Python 3.14.3).
    # Here the path is a module constant built with os.path.join -- native separators, no MSYS.
    with open(path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                rows.append(json.loads(ln))
            except Exception:
                rows.append({"_unparseable": ln[:120]})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--window-min", type=int, default=240,
                    help="only judge wakes whose file mtime is within this many minutes (default 240)")
    ap.add_argument("--strict", action="store_true",
                    help="a spawn-intent row contradicted by a later expired-in-flight row is NOT terminal (D17)")
    ap.add_argument("--legacy-intent-is-terminal", action="store_true",
                    help="v2 behaviour: count the spawn-intent row as a terminal row (the definition "
                         "that produced CFL's withdrawn 6/6 PASS). Printed alongside either way.")
    ap.add_argument("--all", action="store_true", help="ignore the window; judge every wake on disk")
    a = ap.parse_args()

    if not os.path.isdir(SB_WAKE):
        print(f"FAIL wake dir unreadable: {SB_WAKE}", file=sys.stderr)
        return 2
    rows = read_rows(LEDGER)
    if not rows:
        print(f"FAIL delivery ledger empty or unreadable: {LEDGER}", file=sys.stderr)
        return 2

    now = dt.datetime.now().timestamp()
    cutoff = now - a.window_min * 60

    wakes = []
    for f in sorted(os.listdir(SB_WAKE)):
        if not (f.startswith("wake-") and f.endswith(".json")):
            continue
        p = os.path.join(SB_WAKE, f)
        m = os.path.getmtime(p)
        if not a.all and m < cutoff:
            continue
        try:
            j = json.load(open(p, encoding="utf-8", errors="replace"))
        except Exception:
            j = {}
        wakes.append((f, m, j.get("target", "?")))

    # index ledger rows by the `what` basename they carry
    by_what = {}
    for r in rows:
        w = r.get("what")
        if w:
            by_what.setdefault(w, []).append(r)

    # How many raise-rows does the relay's own ledger hold, and does it record ANY outcome?
    sb_rows = read_rows(SB_LEDGER)
    sb_raised = sum(1 for r in sb_rows if r.get("wake_path"))
    sb_outcome = sum(1 for r in sb_rows if any(
        k in r for k in ("delivered", "delivery", "consumed", "terminal", "outcome")))

    # bucket per consumer scope
    buckets = {"operator": {"ok": [], "bad": [], "none": [], "inflight": [], "claimed": []},
               "relay": {"ok": [], "bad": [], "none": [], "inflight": [], "claimed": []}}
    for f, m, target in wakes:
        who = "operator" if target in OPERATOR_SCOPE else (
            "relay" if target in RELAY_SCOPE else "operator")
        b = buckets[who]
        rs = by_what.get(f, [])
        kinds = [r.get("kind") for r in rs]
        hhmm = dt.datetime.fromtimestamp(m).strftime("%H:%M:%S")
        claimed = any(k in CLAIM_KINDS for k in kinds)
        if claimed:
            b["claimed"].append(f)
        # ⚠️ counted independently of --legacy so this column cannot inherit the legacy
        # definition. First cut of it did, and printed TERMINAL=12 in a run whose whole
        # point was that TERMINAL is 0 — a display that lies in exactly one mode.
        if any(is_terminal_ok(k) or is_terminal_bad(k) for k in kinds):
            b["true_terminal"] = b.get("true_terminal", 0) + 1
        # the legacy escape hatch, so the withdrawn number is reproducible rather than remembered
        ok_kinds = claimed if a.legacy_intent_is_terminal else any(is_terminal_ok(k) for k in kinds)
        if any(is_terminal_bad(k) for k in kinds):
            b["bad"].append((f, target, kinds))
            if not a.strict and ok_kinds:
                b["ok"].append((f, target, kinds))
        elif ok_kinds:
            b["ok"].append((f, target, kinds))
        elif now - m < IN_FLIGHT_SEC:
            b["inflight"].append((f, target, hhmm))
        else:
            b["none"].append((f, target, hhmm))

    scope = "ALL on disk" if a.all else f"mtime within {a.window_min} min"
    print("=== A5 — wake terminal-row audit (run from CFL, OUTSIDE the operator) ===")
    print(f"  wake dir       : {SB_WAKE}")
    print(f"  operator ledger: {LEDGER}  ({len(rows)} rows)")
    print(f"  relay ledger   : {SB_LEDGER}  ({len(sb_rows)} rows; "
          f"{sb_raised} carry wake_path, {sb_outcome} carry any outcome field)")
    print(f"  scope          : {scope}")
    print(f"  strict         : {a.strict}  (D17: spawn-intent row + later expiry = not delivered)")
    print(f"  DENOMINATOR    : {len(wakes)} wake files in scope\n")

    failed = 0
    for who, targets, record in (
        ("operator", sorted(OPERATOR_SCOPE), os.path.basename(LEDGER)),
        ("relay", sorted(RELAY_SCOPE), os.path.basename(SB_LEDGER)),
    ):
        b = buckets[who]
        n = len(b["ok"]) + len(b["none"]) + len(b["inflight"])
        print(f"  --- consumer: {who}  (targets {targets}; record it keeps: {record}) ---")
        print(f"      wakes in scope {n} | accounted {len(b['ok'])} | in flight "
              f"{len(b['inflight'])} | non-success {len(b['bad'])} | UNACCOUNTED {len(b['none'])}")
        # Both numbers, every run. The gap between them IS D17's live exposure.
        print(f"      CLAIMED (spawn-intent rows) {len(b['claimed'])} | "
              f"TERMINAL (-completed / -failed-rc / expired-in-flight) "
              f"{b.get('true_terminal', 0)}"
              f"   <- gap = deliveries whose OUTCOME is unrecorded")
        for f, t, hhmm in b["none"][:40]:
            print(f"        no terminal row: {f:<22} target={t:<13} mtime {hhmm}")
        for f, t, hhmm in b["inflight"]:
            print(f"        in flight      : {f:<22} target={t:<13} mtime {hhmm}")
        if b["none"]:
            failed += len(b["none"])
        print()

    if buckets["relay"]["none"] and sb_outcome == 0:
        print("  ⛔ The relay's ledger records that a wake was RAISED and never records what")
        print("     became of it — 0 outcome fields across all rows. For relay-scope wakes there")
        print("     is no second record to check. R2 (no wake leaves the system without a")
        print("     terminal row) is unmet for its entire scope, not for a subset.\n")

    print("  [!] BOUND: this counts LEDGER ROWS, not arrivals. An operator row is written by the")
    print("      caller at spawn INTENT (switchboard-operator.sh:147/165/176), so it means a turn")
    print("      was STARTED. Only the woken seat can attest that one happened.")

    if failed:
        print(f"\nFAIL {failed}/{len(wakes)} wakes have no terminal row in the record their consumer keeps")
        return 1
    print(f"\nPASS every wake in scope carries a terminal row in its consumer's record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
