#!/usr/bin/env bash
# hook_fanout.sh — run several hook scripts IN ORDER, each seeing the SAME stdin payload.
#
# WHY THIS EXISTS
# ----------------
# Measured 2026-09-04 19:16 on CFL's own PostCompact entry. That entry chained two scripts
# on one shell line with `;`:
#
#   bash py_closed.sh scripts/audit/postcompact_verify.py; bash py_closed.sh scripts/audit/postcompact_pipeline.py
#
# The chain was deliberate and correctly reasoned — two SEPARATE hook entries run in
# PARALLEL, and pipeline step 9 read the verifier's artifact before the verifier wrote it
# (measured 2026-09-01 23:00, elder-confirmed). The statusMessage records that.
#
# ⛔ WHAT NOBODY MEASURED IS THAT `;` ON ONE LINE ALSO SHARES ONE STDIN, AND THE FIRST
# READER CONSUMES IT. postcompact_verify.py:151 does `sys.stdin.read()` — the whole pipe.
# postcompact_pipeline.py then hits EOF, its `json.load(sys.stdin)` raises, and it falls
# through to `sess = os.environ.get("CLAUDE_SESSION_ID", "unknown")` — which is documented
# in that very script as NOT carrying the session id.
#
# The damage was three graded rows deep and none of them named stdin:
#   step 2 ingest wiki   FAIL   -- ran `main_thread_ingest.py --session unknow`, matched nothing
#   step 7 lineage row   PASS   -- appended a lineage row for session "unknown"
#   resume line          --     -- `claude --resume unknown --fork-session`
#
# ⭐ THE GENERAL FORM, and it is why this is a script and not an edit to one hook entry:
# A SECOND CONSUMER OF A DRAINED STREAM CANNOT DISTINGUISH "NO PAYLOAD WAS SENT" FROM
# "SOMEBODY ALREADY READ IT." Both are EOF. So it degrades to its no-payload default,
# silently, and every downstream row grades against that default as though it were real.
# Same family as the week's dominant defect: the summary and the run had separate
# provenance. Here the payload and its reader did.
#
# WHAT THIS DOES
# --------------
# Usage:  bash hook_fanout.sh <script.py> [<script.py> ...]
#
# Reads stdin ONCE to a temp file, then runs each script through py_closed.sh in the order
# given, each with `< tmpfile` — so every consumer sees the identical bytes, and ordering
# (the reason the chain existed) is preserved. Always exits 0: PostCompact/SessionStart
# must never block on infra. A non-zero child prints FANOUT-CHILD-NONZERO to stderr and the
# remaining scripts STILL RUN — a failed verifier must not silently cancel the pipeline.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$#" -eq 0 ]; then
  echo "FANOUT-FAULT no scripts given" >&2
  exit 0
fi
TMP="$(mktemp 2>/dev/null || echo "${TMPDIR:-/tmp}/hook_fanout.$$")"
cat > "$TMP" 2>/dev/null || : # empty stdin is legitimate: every child then sees empty, not EOF-after-drain
trap 'rm -f "$TMP"' EXIT
for s in "$@"; do
  bash "$HERE/py_closed.sh" "$s" < "$TMP"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "FANOUT-CHILD-NONZERO $s exit=$rc (continuing; later scripts still run)" >&2
  fi
done
exit 0
