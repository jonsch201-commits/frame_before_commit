#!/usr/bin/env bash
# GraphRAG for the Professional trunk — one line per verb, so no session re-derives the paths.
#
#   scripts/graphrag.sh build            # idempotent; no-op when nothing changed. Runs the seal probe.
#   scripts/graphrag.sh query "..."      # EVERY tier (default since 2026-08-31; see the note below)
#   scripts/graphrag.sh query "..." --knowledge-only   # the old narrow default: wiki + constitutions
#   scripts/graphrag.sh asop "..."       # the 57 ASOPs (standards tier -- NOT in the default scope)
#   scripts/graphrag.sh query "..." --tier claude_ai   # 667 claude.ai transcripts, full-text
#                                         # chunked (37,204 chunks) -- NOT in the default scope
#   scripts/graphrag.sh selftest         # CFL's build selftest + this trunk's sealed-exclusion probe
#   scripts/graphrag.sh sealcheck        # the sealed-exclusion probe alone
#
# ⛔ EVERY PATH IS QUOTED. `My Drive` contains a space; this trunk has logged three separate
# defects from an unquoted path splitting on it. Do not remove a quote to tidy a line.
#
# ⛔ THE SEALED EXCLUSION IS THE ONE THING THIS WRAPPER EXISTS TO GUARANTEE.
# `wiki/sealed/` holds the +30-day memory audit — an exam the audited party must not be able to
# study. The exclusion is implemented in `scripts/graphrag_pro.py` (two independent mechanisms) and
# PROBE-TESTED here after every build. An exclusion you did not test is an exclusion you do not have.
#
# The builder is CFL's (`--root`-aware); we own the shim and this wrapper, not a second builder.
# Exit codes are CFL's: 0 ok · 2 bad corpus · 4 another build holds the lock · 5 selftest failed.
# The build lock is SHARED with CFL's own index by design (same GRAPHRAG_HOME): two builds cannot
# run at once, and the second one refuses with exit 4 rather than interleaving.

set -euo pipefail

# R4b (2026-09-05): the tree root is DERIVED from this script's location, never typed -- a hardcoded G: root would make a
# seat launched from N: index and write the G: tree (Secretary found 20 such lines in its tree at 13:15).
PRO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# CFL's builder lives in CFL's LIVE home; its G: copy is the daemon's mirror (R8), never the source.
CFL_GRAPHRAG="${CFL_GRAPHRAG:-N:/claude-cfl/clone/scripts/graphrag}"
DB="${LOCALAPPDATA:-$HOME/.cache}/claude/graphrag/professional.sqlite"
# A phrase that exists ONLY inside wiki/sealed/. If retrieval ever returns a wiki/sealed/ path for
# it, the exam is indexed and the seal is broken.
SEAL_PROBE="the exam is void as an exam"

if [ ! -d "$CFL_GRAPHRAG" ]; then
  echo "FAIL CFL graphrag tooling not found: $CFL_GRAPHRAG" >&2
  exit 2
fi

sealcheck() {
  # E4, 2026-09-03. This read `... 2>/dev/null | grep -c '"source": "wiki/sealed' || true`, and a
  # SEAL CHECK is the worst place in this repo for that shape. Two silent passes were reachable:
  # a CRASHING retriever writes nothing to stdout, so grep counts 0 and the seal reports INTACT
  # because the instrument died; and an ABORTED grep returns a non-zero exit indistinguishable
  # from a clean no-match, which `|| true` then coerced into a count. A seal that passes when its
  # own probe fails is the silent-healthy failure this trunk spent 2026-09-03 cataloguing.
  # Now: run the probe, CHECK ITS EXIT, and count with awk, which cannot confuse error with zero.
  local hits out rc
  out=$(python "$CFL_GRAPHRAG/retrieve.py" "$SEAL_PROBE" --db "$DB" --all-tiers -k 20 --json 2>&1); rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "SEAL UNKNOWN: the probe itself failed (exit $rc). UNKNOWN is not INTACT." >&2
    printf '%s\n' "$out" | tail -3 >&2
    return 2
  fi
  hits=$(printf '%s\n' "$out" | awk '/"source": "wiki\/sealed/{n++} END{print n+0}')
  if [ "$hits" -ne 0 ]; then
    echo "⛔ SEAL BROKEN: $hits chunk(s) under wiki/sealed/ are retrievable from the index." >&2
    echo "   The +30-day exam is studyable. Rebuild with scripts/graphrag_pro.py and re-probe." >&2
    return 5
  fi
  echo "SEAL OK: 0 retrievable chunks under wiki/sealed/ (probe: \"$SEAL_PROBE\", -k 20, --all-tiers)"
}

case "${1:-}" in
  build)
    shift
    python "$PRO_ROOT/scripts/graphrag_pro.py" "$@"
    sealcheck
    ;;
  query)
    # ⛔ THE DEFAULT IS EVERY TIER, AND THAT IS A DELIBERATE REVERSAL MADE 2026-08-31.
    # `retrieve.py` fails CLOSED to {knowledge} and that is CORRECT at the library layer -- an
    # allow-set that replaced a fail-OPEN boolean on 08-23. But this WRAPPER is what sessions and
    # humans actually call, and `[m 08-31]` the knowledge tier is 1,908 of 45,914 chunks: a default
    # query answered from 4.16% of the index this trunk paid to build.
    #
    # ⭐ MEASURED BEFORE CHANGING, NOT ASSERTED -- `scripts/PROTOTYPE-tier-scope-ab.py` on branch
    # `proto/tier-scope`, 12 probes in two families with OPPOSITE expected outcomes:
    #     recall (answer outside knowledge):  default 0/6  ->  widened 6/6
    #     noise  (answer inside  knowledge):  default 6/6  ->  widened 6/6, NONE LOST,
    #                                         2 demoted (#1->#4, #1->#5), both still inside k=8.
    # ⭐ +6 found, 0 lost. A demotion within the returned set costs a large-model consumer almost
    # nothing; a MISS costs everything. The narrow default was losing every ASOP question in the
    # actuarial trunk and both of Jon's rulings that live in the letters channel.
    #
    # ⚠️ THE COST IS REAL AND IS NOT ZERO: widening demoted 2 of 6 in-tier probes. If a future
    # measurement shows a LOSS rather than a demotion, this reversal is wrong and should be undone.
    # `--knowledge-only` restores the old behaviour for anyone who wants it.
    shift
    [ $# -ge 1 ] || { echo "usage: scripts/graphrag.sh query \"<question>\" [--knowledge-only] [retrieve.py flags]" >&2; exit 2; }
    q="$1"; shift
    SCOPE_FLAG="--all-tiers"
    for a in "$@"; do
      case "$a" in
        --knowledge-only) SCOPE_FLAG="" ;;
        --tier|--tier=*|--all-tiers) SCOPE_FLAG="" ;;   # caller named a scope; do not fight it
      esac
    done
    set -- $(printf '%s\n' "$@" | grep -vx -- '--knowledge-only' || true)
    # shellcheck disable=SC2086
    python "$CFL_GRAPHRAG/retrieve.py" "$q" --db "$DB" $SCOPE_FLAG "$@"
    ;;
  asop)
    # ⭐ THE ASOPs ARE IN THEIR OWN TIER AND THE DEFAULT SCOPE DOES NOT REACH THEM.
    # CFL's retriever holds an allow-set of {knowledge} that FAILS CLOSED, so `standards` is
    # invisible without the flag. This verb exists so nobody has to know that -- and so nobody
    # queries without it, finds nothing, and concludes the standards are not on disc. They are:
    # 57 of them, `raw/asops/`, registered in `wiki/references/asop-register.md`.
    shift
    [ $# -ge 1 ] || { echo "usage: scripts/graphrag.sh asop \"<question>\" [retrieve.py flags]" >&2; exit 2; }
    q="$1"; shift
    python "$CFL_GRAPHRAG/retrieve.py" "$q" --db "$DB" --tier standards "$@"
    ;;
  selftest)
    python "$CFL_GRAPHRAG/build_index.py" --selftest
    sealcheck
    ;;
  sealcheck)
    sealcheck
    ;;
  *)
    sed -n '2,15p' "$0"
    exit 2
    ;;
esac
