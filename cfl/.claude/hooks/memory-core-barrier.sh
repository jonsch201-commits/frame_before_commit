#!/usr/bin/env bash
# memory-core-barrier.sh -- PreCompact shim: pass the harness's session_id to the barrier writer.
#
# WHY THIS EXISTS
# ---------------
# `write_barrier_memory.py` requires --session and does NOT read the hook's stdin JSON
# (`grep -c 'stdin|session_id'` -> 0). CFL first proposed the hook entry WITHOUT --session.
# Claude Professional ran that exact shape as the config gate holder and it exits:
#     write_barrier_memory.py: error: --session is required (or use --selftest)
#
# ⛔ WIRED AS PROPOSED IT WOULD HAVE FAILED AT EVERY COMPACT WHILE THE SETTINGS READ AS WIRED --
# a third PreCompact entry that never lands. That is WORSE than the zero it replaced, because a
# reader inspecting settings.json sees the capability and gets none. It is the green-hook-over-a-
# dead-channel class this trunk spent 2026-09-05 cataloguing, authored by the seat cataloguing it.
#
# ⭐ SO THE SHIM'S WHOLE JOB IS TO MAKE THE FAILURE LOUD RATHER THAN SILENT: a missing session_id
# exits NONZERO with a named reason. It never writes a record under a guessed or empty session --
# a barrier record whose session field is wrong is worse than no record, because it is evidence
# pointing at the wrong window.
#
# PreCompact stdin is JSON: {"session_id": "...", "transcript_path": "...", "trigger": "..."}
set -uo pipefail

PAYLOAD="$(cat)"
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
WRITER="$ROOT/skills/memory-core/scripts/write_barrier_memory.py"

sid="$(printf '%s' "$PAYLOAD" | python -c "
import json,sys
try:
    print(json.load(sys.stdin).get('session_id','') or '')
except Exception:
    print('')
" 2>/dev/null)"

if [ -z "$sid" ]; then
  echo "memory-core-barrier: UNKNOWN -- no session_id on PreCompact stdin; no record written." >&2
  echo "  payload was ${#PAYLOAD} byte(s). A record under a guessed session is worse than none." >&2
  exit 1
fi
if [ ! -f "$WRITER" ]; then
  echo "memory-core-barrier: UNKNOWN -- writer absent at $WRITER; no record written." >&2
  exit 1
fi

exec python "$WRITER" \
  --barrier compact \
  --as-of "$(date -Iseconds)" \
  --session "$sid" \
  --seat cfl \
  --root "$ROOT"
