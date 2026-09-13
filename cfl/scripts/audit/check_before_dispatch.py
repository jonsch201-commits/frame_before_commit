#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""M-14: the pre-dispatch look-before-building gate.

Before dispatching / TAKE-ing a work item, run this with the topic. It answers ONE
question: WHO ALREADY HOLDS SOMETHING ON THIS TOPIC -- indexed retrieval, plus the
spaces retrieval CANNOT see (exchange/ letters+specs, the resident's quarantine
mirror incl. letters/to-jon, the peer trunk's trackers), plus a fixed stakeholder
checklist the dispatcher must answer from the evidence.

Why it exists: the resident's standing resumption letter sat unconsulted in an
UNINDEXED mirror while a resumption system was designed. The mirror consult was
scoped to Jon's-words-only and never asked "who else holds standing views."

Rules baked in:
  * Unreachable space => said out loud, never silently skipped. UNKNOWN dominates a PASS.
  * Term-wise OR matching, not exact-phrase grep -- "resumption memory continuity"
    must find a letter that only contains "resumption". A phrase grep is how the
    original miss happens again with a tool wrapped around it.
  * Output is cp1252-safe and sized to paste into the branch-dispatch snapshot's
    conditioning section.

Usage:
  python scripts/audit/check_before_dispatch.py "resumption memory continuity" --as-of 2026-08-22T09:00:00-0500
  python scripts/audit/check_before_dispatch.py --selftest
"""

import argparse
import io
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# The unindexed spaces, BY NAME. Adding a space here is the whole maintenance model:
# retrieval cannot see these, so this list is the only thing standing between a
# dispatcher and a standing view it never consulted.
UNINDEXED_SPACES = [
    ("exchange (letters + specs)", os.path.join(REPO, "exchange")),
    ("SSP quarantine-mirror (resident's record incl. letters/to-jon)",
     r"G:/My Drive/Claude/Claude SSP/claude-ssp/quarantine-mirror"),
    ("Personal trunk trackers",
     r"G:/My Drive/Claude/Claude Personal/wiki/tracker"),
]

PER_SPACE_CAP = 8
MAX_FILE_BYTES = 2 * 1024 * 1024
EXTS = (".md", ".txt")
STOPWORDS = {"the", "and", "for", "with", "this", "that", "from", "into", "over"}

CHECKLIST = [
    "[ ] Jon's words consulted? (find_answer / history.jsonl / sibling trunks)",
    "[ ] Peer coordinator views? (exchange inbound letters, Personal trackers above)",
    "[ ] RESIDENT / consciousness-framing views? (quarantine-mirror hits above)",
    "[ ] Prior build of this exact thing? (scripts/, git log, .gitignore, RECAPS)",
]


def _safe(s):
    """cp1252-safe: strip anything the Windows console codepage cannot carry."""
    return s.encode("cp1252", errors="replace").decode("cp1252")


def out(s=""):
    sys.stdout.write(_safe(s) + "\n")


def topic_terms(topic):
    terms = [t.lower() for t in re.findall(r"[A-Za-z0-9]+", topic)]
    terms = [t for t in terms if len(t) >= 4 and t not in STOPWORDS]
    return terms or [topic.lower()]


def sweep_indexed(topic):
    """Sweep 1: the graphrag index, STALE banner and all, passed through."""
    out("--- 1. INDEXED (scripts/graphrag/retrieve.py, k=6) ---")
    cmd = [sys.executable, os.path.join(REPO, "scripts", "graphrag", "retrieve.py"), topic, "-k", "6"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                           encoding="utf-8", errors="replace", cwd=REPO)
        body = (p.stdout or "").strip()
        errs = (p.stderr or "").strip()
        if body:
            out(body)
        if p.returncode != 0:
            out("[retrieve.py exit %d -- tolerated, treat indexed sweep as UNKNOWN]" % p.returncode)
            if errs:
                out(errs.splitlines()[-1])
        return p.returncode == 0
    except Exception as e:  # noqa: BLE001 -- gate must degrade to UNKNOWN, not crash
        out("[INDEXED SWEEP UNREACHABLE: %s -- UNKNOWN, not a pass]" % e)
        return False


def scan_space(root, terms, as_of_ts):
    """Return list of (score, mtime, path) for files matching ANY term (content or name)."""
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", "node_modules")]
        for fn in filenames:
            if not fn.lower().endswith(EXTS):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(fp) > MAX_FILE_BYTES:
                    continue
                with io.open(fp, "r", encoding="utf-8", errors="replace") as fh:
                    text = fh.read().lower()
            except OSError:
                continue
            name_l = fn.lower()
            matched = {t for t in terms if t in text or t in name_l}
            if matched:
                try:
                    mt = os.path.getmtime(fp)
                except OSError:
                    mt = 0
                hits.append((len(matched), mt, fp, sorted(matched)))
    hits.sort(key=lambda h: (-h[0], -h[1]))
    return hits


def sweep_unindexed(topic, as_of_ts):
    """Sweep 2: the spaces retrieval cannot see. Returns dict space-name -> hit paths."""
    terms = topic_terms(topic)
    out("")
    out("--- 2. UNINDEXED SPACES (term-wise OR match: %s) ---" % ", ".join(terms))
    results = {}
    for name, root in UNINDEXED_SPACES:
        if not os.path.isdir(root):
            out("SPACE UNREACHABLE: %s  [%s]" % (name, root))
            out("  -> UNKNOWN dominates a pass. Sweep this space by hand before dispatch.")
            results[name] = None
            continue
        hits = scan_space(root, terms, as_of_ts)
        shown = hits[:PER_SPACE_CAP]
        out("SPACE SWEPT: %s  (%d hit%s%s)" % (
            name, len(hits), "" if len(hits) == 1 else "s",
            ", top %d by relevance/mtime" % PER_SPACE_CAP if len(hits) > PER_SPACE_CAP else ""))
        for score, mt, fp, matched in shown:
            flag = ""
            if as_of_ts is not None and mt > as_of_ts:
                flag = "  [NEWER than --as-of]"
            rel = os.path.relpath(fp, root)
            out("  %s  (terms: %s)%s" % (rel.replace("\\", "/"), ",".join(matched), flag))
        results[name] = [h[2] for h in hits]
    return results


def sweep_stakeholders():
    out("")
    out("--- 3. STAKEHOLDER CHECK (answer each FROM the hits above, then dispatch) ---")
    for line in CHECKLIST:
        out(line)


def run_gate(topic, as_of):
    try:
        as_of_dt = datetime.fromisoformat(as_of)
        if as_of_dt.tzinfo is None:
            as_of_dt = as_of_dt.replace(tzinfo=timezone.utc)
        as_of_ts = as_of_dt.timestamp()
    except ValueError:
        out("FAIL: --as-of is not full ISO: %r" % as_of)
        return 2, {}
    out("== LOOK-BEFORE-BUILDING GATE (M-14) ==")
    out("topic: %s" % topic)
    out("as-of: %s" % as_of)
    sweep_indexed(topic)
    results = sweep_unindexed(topic, as_of_ts)
    sweep_stakeholders()
    out("")
    out("Paste this block into branch-dispatch-snapshot 'look-before-building:'.")
    return 0, results


def selftest():
    """The gate must find the letter whose miss motivated it."""
    topic = "resumption memory continuity"
    as_of = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    rc, results = run_gate(topic, as_of)
    out("")
    out("--- SELFTEST ---")
    qname = "SSP quarantine-mirror (resident's record incl. letters/to-jon)"
    hits = results.get(qname)
    if hits is None:
        out("SELFTEST FAIL: quarantine-mirror path is MISSING/UNREACHABLE.")
        out("  The space that held the missed standing letter cannot be swept. Fix the")
        out("  path in UNINDEXED_SPACES or restore the mirror before trusting this gate.")
        return 1
    target = "the-moral-question"
    found = [h for h in hits if target in os.path.basename(h).lower()]
    if not found:
        out("SELFTEST FAIL: quarantine-mirror swept (%d hits) but the-moral-question" % len(hits))
        out("  letter was NOT among them. The gate would repeat the original miss.")
        return 1
    out("SELFTEST PASS: found %s" % found[0].replace("\\", "/"))
    return 0


def main():
    ap = argparse.ArgumentParser(description="M-14 pre-dispatch look-before-building gate")
    ap.add_argument("topic", nargs="?", help="the work item about to be dispatched/TAKEn")
    ap.add_argument("--as-of", dest="as_of", help="full ISO timestamp of the dispatch decision (required)")
    ap.add_argument("--selftest", action="store_true", help="assert the gate finds the-moral-question letter")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if not args.topic or not args.as_of:
        ap.error("topic and --as-of are both required (no default as-of; the timestamp is part of the record)")
    rc, _ = run_gate(args.topic, args.as_of)
    sys.exit(rc)


if __name__ == "__main__":
    main()
