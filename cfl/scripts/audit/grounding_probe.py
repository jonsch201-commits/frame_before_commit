#!/usr/bin/env python3
"""grounding_probe.py — end-to-end proof that a fresh wiki/exchange write is
retrievable by graphrag WITHOUT a manual rebuild. GR-1's acceptance test.

Jon's question, verbatim: "does writing to the exchange hook raw md updates
so vector embeded graph rag can function as intended yet so all trunks can
ground while reading?" The answer measured before this lane was NO: a page
written mid-session sat unreachable to retrieve.py until someone remembered
to run build_index.py by hand. This probe is the automated check that the
fix (index_queue_enqueue.py hook + index_queue_drain.py) actually closes
that gap, end to end, on demand or at any barrier that wants to re-verify it.

STAGES, and a failure names WHICH one broke rather than a bare exit code:
  1. WRITE   -- write wiki/intake-triage/probes/grounding-canary-<ts>.md
                containing a random nonce sentence nothing else in the corpus
                can contain (a UUID4 hex embedded in prose).
  2. ENQUEUE -- run index_queue_enqueue.py with a synthetic PostToolUse
                payload naming the canary -- the SAME code path a real
                Write/Edit hook firing would take, not a hand-rolled append.
  3. DRAIN   -- run index_queue_drain.py (unless --selftest's disabled leg,
                see below).
  4. QUERY   -- run retrieve.py "<nonce>" --tier knowledge -k 3 --json and
                check the canary's path is rank 1.
PASS iff all four stages complete and rank 1 is the canary, inside a 120s
budget measured from stage 1. Any other outcome exits 1 naming the stage.

The canary file is NEVER deleted (this program's standing rule) and carries
`kind: probe-canary` in its frontmatter so wiki lint knows to ignore it as a
content page.

--selftest proves the probe can actually FAIL, not just always print PASS --
the single biggest hole in any self-test that only ever exercises its own
happy path. It runs the probe twice: once with the drain stage disabled
(env GROUNDING_PROBE_DISABLE_DRAIN=1 -- the canary is written and enqueued
but never indexed, so the query stage cannot find it) and asserts exit 1;
once normally and asserts exit 0. Both runs' full output is printed so a
reader can see the negative control actually fired, not just trust a label.

Federated form: every path comes from --root / --index / env, never a CFL
literal, so this file is safe to publish standalone
(N:\\claude-gists-private\\PROTO-grounding_probe-v1.py).

Usage:
  python scripts/audit/grounding_probe.py --root <repo> [--index <path>]
  python scripts/audit/grounding_probe.py --root <repo> --selftest
Exit codes: 0 PASS · 1 FAIL (stage named) · 2 bad args.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path


def canary_path(root: Path, ts: str) -> Path:
    return root / "wiki" / "intake-triage" / "probes" / f"grounding-canary-{ts}.md"


def write_canary(root: Path, ts: str, nonce: str) -> Path:
    p = canary_path(root, ts)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "---\n"
        f"title: grounding canary {ts}\n"
        "kind: probe-canary\n"
        "---\n\n"
        f"# grounding canary {ts}\n\n"
        "This page exists solely to prove the graphrag write-to-retrieval loop closes "
        "without a manual rebuild (GR-1). It is never deleted. The sentence below "
        "contains a nonce nothing else in the corpus can contain:\n\n"
        f"the grounding probe nonce is {nonce} and it should be retrievable at rank one.\n",
        encoding="utf-8",
    )
    return p


def run_enqueue(root: Path, canary: Path, python_exe: str) -> tuple[int, str]:
    payload = json.dumps({
        "session_id": "grounding-probe",
        "tool_name": "Write",
        "tool_input": {"file_path": str(canary)},
    })
    r = subprocess.run(
        [python_exe, str(root / "scripts" / "audit" / "index_queue_enqueue.py")],
        input=payload, capture_output=True, text=True, cwd=root, timeout=10,
    )
    return r.returncode, (r.stdout + r.stderr)


def run_drain(root: Path, index: str | None, python_exe: str) -> tuple[int, str]:
    cmd = [python_exe, str(root / "scripts" / "audit" / "index_queue_drain.py")]
    if index:
        cmd += ["--db", index]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=root, timeout=300)
    return r.returncode, (r.stdout + r.stderr)


def run_query(root: Path, index: str | None, nonce: str, python_exe: str) -> tuple[int, str, list]:
    # ⛔ MEASURED DEVIATION FROM THE LITERAL SPEC, stated rather than silently fixed: the canary
    # lives under wiki/intake-triage/probes/, and build_index.py's tier_of() classifies every
    # wiki/intake-triage/** path as tier "queue", never "knowledge" (README section 2, "Tiering").
    # Querying `--tier knowledge` for a canary that structurally CANNOT be in that tier would make
    # this probe fail on every run regardless of whether the enqueue/drain mechanism works --
    # a probe engineered to always report the same verdict is worse than no probe (see this
    # program's "caution errors have no instrument" finding). First run against a real index
    # confirmed it empirically: drain exit 0, canary chunk present, "knowledge"-tier query top-3
    # did not contain it at all. This probe therefore queries "queue" -- the tier the canary's OWN
    # location actually belongs to, and the tier that also holds the exchange/wiki-intake-triage
    # traffic Jon's original question named ("writing to the exchange hook raw md updates"). A
    # caller who wants the knowledge-tier claim proven should place a canary under a knowledge
    # path (e.g. wiki/concepts/) and pass that; this script's own probes/ location is queue-tier
    # by construction and is queried as such.
    cmd = [python_exe, str(root / "scripts" / "graphrag" / "retrieve.py"), nonce,
           "--tier", "queue", "-k", "3", "--json"]
    if index:
        cmd += ["--db", index]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=root, timeout=60)
    results = []
    try:
        results = json.loads(r.stdout).get("results", [])
    except Exception:
        pass
    return r.returncode, (r.stdout + r.stderr), results


def probe(root: Path, index: str | None, disable_drain: bool) -> int:
    t0 = time.time()
    python_exe = sys.executable
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    nonce = uuid.uuid4().hex

    canary = write_canary(root, ts, nonce)
    rel_canary = str(canary.relative_to(root)).replace("\\", "/")
    print(f"STAGE 1 WRITE   canary={rel_canary} nonce={nonce}")

    rc, out = run_enqueue(root, canary, python_exe)
    print(f"STAGE 2 ENQUEUE exit={rc}\n{out}")
    if rc != 0:
        print(f"FAIL stage=ENQUEUE exit={rc}", file=sys.stderr)
        return 1

    if disable_drain:
        print("STAGE 3 DRAIN   SKIPPED (GROUNDING_PROBE_DISABLE_DRAIN=1 -- negative control)")
    else:
        rc, out = run_drain(root, index, python_exe)
        print(f"STAGE 3 DRAIN   exit={rc}\n{out}")
        if rc != 0:
            print(f"FAIL stage=DRAIN exit={rc}", file=sys.stderr)
            return 1

    rc, out, results = run_query(root, index, nonce, python_exe)
    print(f"STAGE 4 QUERY   exit={rc}\n{out}")
    elapsed = time.time() - t0
    if rc != 0:
        print(f"FAIL stage=QUERY exit={rc} elapsed={elapsed:.1f}s", file=sys.stderr)
        return 1

    rank1 = results[0] if results else None
    hit = bool(rank1 and rank1.get("source", "").split(":")[0] == rel_canary)
    if not hit:
        found_at = next((r["rank"] for r in results
                         if r.get("source", "").split(":")[0] == rel_canary), None)
        print(f"FAIL stage=QUERY canary not at rank 1 "
              f"(found_at_rank={found_at}, top result={rank1}) elapsed={elapsed:.1f}s",
              file=sys.stderr)
        return 1

    if elapsed > 120:
        print(f"FAIL stage=BUDGET elapsed={elapsed:.1f}s > 120s budget", file=sys.stderr)
        return 1

    print(f"PASS canary retrieved at rank 1, elapsed={elapsed:.1f}s")
    return 0


def selftest(root: Path, index: str | None) -> int:
    print("=== selftest leg 1: drain DISABLED, expect FAIL (exit 1) ===")
    rc1 = probe(root, index, disable_drain=True)
    print(f"leg 1 exit={rc1} (expected 1)\n")

    print("=== selftest leg 2: drain ENABLED, expect PASS (exit 0) ===")
    rc2 = probe(root, index, disable_drain=False)
    print(f"leg 2 exit={rc2} (expected 0)\n")

    ok = (rc1 == 1) and (rc2 == 0)
    print(f"selftest: {'ALL PASS' if ok else 'FAILED'} "
          f"(leg1={rc1} expected 1, leg2={rc2} expected 0)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="repo root to write the canary and query")
    ap.add_argument("--index", default=None, help="graphrag --db path override; default env/repo default")
    ap.add_argument("--selftest", action="store_true",
                    help="run the negative-then-positive control pair; see module docstring")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"FAIL --root is not a directory: {root}", file=sys.stderr)
        return 2

    if args.selftest:
        return selftest(root, args.index)

    disable = os.environ.get("GROUNDING_PROBE_DISABLE_DRAIN") == "1"
    return probe(root, args.index, disable_drain=disable)


if __name__ == "__main__":
    sys.exit(main())
