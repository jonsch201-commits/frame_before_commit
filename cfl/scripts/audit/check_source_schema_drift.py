#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check_source_schema_drift.py -- probe: does the newest CC session JSONL still match
the documented record-type/field set in wiki/references/source-schemas.md?

Why it exists: wiki/references/source-schemas.md is the ONE canonical page for the two
source-data schemas this program lives on (CC session JSONL, claude.ai export JSON).
Both schemas are EMPIRICAL -- no published spec exists for either -- so the only way
to know the documented page has gone stale is to re-measure and diff. This script is
that re-measurement, wired for the heartbeat battery / probe registry (see
skills/probe-registry).

Method: parse the newest session JSONL under a given projects root, collect the
observed set of top-level `type` values and, per type, the observed field-name set.
Compare against the DOCUMENTED set baked into this file (kept in sync with
source-schemas.md by hand -- see SCHEMA_UPDATED_WITH below). Any NEW record type not
in DOCUMENTED_TYPES, or any DOCUMENTED field absent from EVERY observed record of its
type, is a WARN naming the delta. This is a drift ALARM, not a schema validator: it
must never crash on a shape it has not seen before, and an unrecognized field on a
KNOWN type is not itself a WARN (the page's field lists are a floor, not a ceiling).

Usage:
  python scripts/audit/check_source_schema_drift.py --as-of 2026-08-22T21:00:00-05:00
      [--projects-root "C:\\Users\\JonSc\\.claude\\projects\\<slug>"] [--strict]
  python scripts/audit/check_source_schema_drift.py --selftest
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SCHEMA_PAGE = os.path.join(REPO, "wiki", "references", "source-schemas.md")

PASS, WARN, UNKNOWN, INFO = "PASS", "WARN", "UNKNOWN", "INFO"

DEFAULT_PROJECTS_ROOT = os.path.join(
    os.path.expanduser("~"), ".claude", "projects",
    "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer",
)

# ---------------------------------------------------------------------------
# The documented shape, hand-synced against source-schemas.md Section 1.
# SCHEMA_UPDATED_WITH names what this was last measured against -- update both
# together whenever Section 1's record-type table changes.
# ---------------------------------------------------------------------------
SCHEMA_UPDATED_WITH = "wiki/references/source-schemas.md Section 1, measured 2026-08-22 against session 643640a7"

# Per-type: field names this page claims are ALWAYS present on that record type.
# Deliberately conservative (only fields observed on every sampled instance of the
# type) so a WARN here means a real absence, not sampling noise.
DOCUMENTED_FIELDS: dict[str, set[str]] = {
    "user": {"type", "message", "uuid", "timestamp", "sessionId", "version", "userType"},
    "assistant": {"type", "message", "uuid", "timestamp", "session_id", "userType"},
    "system": {"type", "subtype", "uuid", "timestamp", "sessionId"},
    "attachment": {"type", "attachment", "sessionId", "timestamp", "uuid"},
    "file-history-snapshot": {"type", "messageId", "snapshot"},
    "file-history-delta": {"type", "messageId", "trackingPath"},
    "last-prompt": {"type", "sessionId", "lastPrompt"},
    "mode": {"type", "sessionId", "mode"},
    "permission-mode": {"type", "sessionId", "permissionMode"},
    "ai-title": {"type", "sessionId", "aiTitle"},
    "bridge-session": {"type", "sessionId", "bridgeSessionId"},
    "queue-operation": {"type", "sessionId", "operation"},
    "pr-link": {"type", "sessionId", "prUrl"},
    "custom-title": {"type", "sessionId", "customTitle"},
    "agent-name": {"type", "sessionId", "agentName"},
    "atis-latch": {"type", "sessionId", "atis"},
}

DOCUMENTED_TYPES: set[str] = set(DOCUMENTED_FIELDS.keys())


class Row:
    def __init__(self, n, name, status, evidence):
        self.n = n
        self.name = name
        self.status = status
        self.evidence = evidence

    def line(self):
        return f"[{self.n:2d}] {self.status:7s} {self.name:28s} {self.evidence}"


def find_newest_jsonl(projects_root: str):
    files = glob.glob(os.path.join(projects_root, "*.jsonl"))
    if not files:
        return None
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[0]


def measure(path: str):
    """Return (types_seen, fields_by_type, harness_versions, n_lines, n_bad_json)."""
    types_seen: set[str] = set()
    fields_by_type: dict[str, set[str]] = {}
    harness_versions: set[str] = set()
    n_lines = 0
    n_bad = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            try:
                d = json.loads(line)
            except Exception:
                n_bad += 1
                continue
            if not isinstance(d, dict):
                n_bad += 1
                continue
            t = d.get("type", "<missing-type>")
            types_seen.add(t)
            fields_by_type.setdefault(t, set()).update(d.keys())
            v = d.get("version")
            if v:
                harness_versions.add(v)
    return types_seen, fields_by_type, harness_versions, n_lines, n_bad


def evaluate(path: str, label: str) -> list[Row]:
    rows: list[Row] = []
    n = 1

    if not path or not os.path.isfile(path):
        rows.append(Row(n, "file-found", UNKNOWN, f"no JSONL found ({label})"))
        return rows
    rows.append(Row(n, "file-found", PASS, f"{path}")); n += 1

    types_seen, fields_by_type, versions, n_lines, n_bad = measure(path)

    rows.append(Row(n, "lines-parsed", INFO if n_bad == 0 else WARN,
                     f"{n_lines} lines, {n_bad} failed JSON parse")); n += 1

    ver = ", ".join(sorted(versions)) if versions else "UNKNOWN (no `version` field observed)"
    rows.append(Row(n, "harness-version", INFO, ver)); n += 1

    new_types = types_seen - DOCUMENTED_TYPES
    if new_types:
        rows.append(Row(n, "new-record-types", WARN,
                         f"undocumented type(s) seen: {sorted(new_types)} -- "
                         f"add to source-schemas.md Section 1"))
    else:
        rows.append(Row(n, "new-record-types", PASS,
                         f"all {len(types_seen)} observed types are documented"))
    n += 1

    missing_field_warnings = []
    for t, documented in DOCUMENTED_FIELDS.items():
        if t not in fields_by_type:
            continue  # type not present in this file at all -- not a drift signal
        observed = fields_by_type[t]
        missing = documented - observed
        if missing:
            missing_field_warnings.append(f"{t}: missing {sorted(missing)}")
    if missing_field_warnings:
        rows.append(Row(n, "missing-documented-fields", WARN,
                         "; ".join(missing_field_warnings)))
    else:
        rows.append(Row(n, "missing-documented-fields", PASS,
                         "every documented field present on every type it was checked against"))
    n += 1

    return rows


def run_selftest() -> int:
    """Synthetic JSONL with a novel record type + a known type missing a documented
    field. Both MUST produce WARN rows -- this is the drift-detection contract."""
    print("=== selftest: novel type + missing field must both WARN ===")
    synthetic = [
        {"type": "user", "message": {"role": "user", "content": "hi"}, "uuid": "u1",
         "timestamp": "2026-01-01T00:00:00Z", "sessionId": "s1", "version": "9.9.999",
         "userType": "external"},
        # A known type ("system") with a documented field ("subtype") dropped:
        {"type": "system", "uuid": "u2", "timestamp": "2026-01-01T00:00:01Z", "sessionId": "s1"},
        # A record type never seen before -- this is the drift case:
        {"type": "quantum-flux-event", "sessionId": "s1", "payload": 42},
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False,
                                      encoding="utf-8") as f:
        for rec in synthetic:
            f.write(json.dumps(rec) + "\n")
        tmp_path = f.name

    try:
        rows = evaluate(tmp_path, "selftest-synthetic")
        for r in rows:
            print(r.line())

        new_type_row = next(r for r in rows if r.name == "new-record-types")
        missing_field_row = next(r for r in rows if r.name == "missing-documented-fields")

        ok = True
        if new_type_row.status != WARN or "quantum-flux-event" not in new_type_row.evidence:
            print("SELFTEST FAIL: novel record type did not produce the expected WARN")
            ok = False
        if missing_field_row.status != WARN or "subtype" not in missing_field_row.evidence:
            print("SELFTEST FAIL: missing documented field did not produce the expected WARN")
            ok = False

        if ok:
            print("SELFTEST PASS: both injected drift cases produced WARN as required.")
            return 0
        return 1
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--as-of", help="measured clock (required unless --selftest)")
    ap.add_argument("--projects-root", default=DEFAULT_PROJECTS_ROOT,
                     help="directory of *.jsonl session files to probe (newest wins)")
    ap.add_argument("--strict", action="store_true",
                     help="nonzero exit if any row is WARN")
    ap.add_argument("--selftest", action="store_true",
                     help="run the synthetic drift-injection selftest and exit")
    args = ap.parse_args()

    if args.selftest:
        return run_selftest()

    if not args.as_of:
        print("ERROR: --as-of is required (repo convention: no now() default -- a "
              "measured clock only). Use --selftest to skip this.", file=sys.stderr)
        return 2

    print(f"check_source_schema_drift.py -- as-of {args.as_of}")
    print(f"schema page: {SCHEMA_PAGE}")
    print(f"synced with: {SCHEMA_UPDATED_WITH}")
    print()

    newest = find_newest_jsonl(args.projects_root)
    rows = evaluate(newest, args.projects_root)
    for r in rows:
        print(r.line())

    warns = [r for r in rows if r.status == WARN]
    unknowns = [r for r in rows if r.status == UNKNOWN]
    print()
    print(f"summary: {len(rows)} checks, {len(warns)} WARN, {len(unknowns)} UNKNOWN")

    if args.strict and (warns or unknowns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
