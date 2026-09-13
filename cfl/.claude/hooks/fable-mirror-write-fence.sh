#!/bin/bash
# fable-mirror-write-fence.sh — PreToolUse wrapper for the fable-mirror Write-fence.
#
# Thin launcher: pipes the hook's stdin JSON to the Python evaluator, which does all
# parsing, path normalization, and the allow/block decision. This wrapper exists for one
# reason the evaluator cannot provide on its own: to FAIL CLOSED if no Python interpreter
# is on PATH in the hook runtime. A hook command that cannot launch its interpreter exits
# 127 (non-blocking per CC docs) and would let the write through — a silent hole. Here, if
# the input looks like a fable-mirror call and we have no interpreter, we exit 2 (block).
#
# jq is intentionally NOT used: it is absent from this machine's Git Bash (verified
# 2026-07-22), and the existing SessionStart hook likewise avoids it.
#
# Docs (code.claude.com/docs/en/hooks, verified 2026-07-22):
#   Exit 2 => blocking error, stderr fed to the model, tool call prevented.
#   Non-2 non-zero => non-blocking error (write would proceed) — hence the fail-closed guard.
#   CLAUDE_PROJECT_DIR is exported to all hook command processes.
set -u

input="$(cat)"

PY="$(command -v python 2>/dev/null || command -v python3 2>/dev/null || command -v py 2>/dev/null)"

if [ -z "$PY" ]; then
  # No interpreter. Only fail closed if this smells like a fable-mirror call; otherwise
  # do not interfere with other agents / the main thread.
  case "$input" in
    *'"agent_type"'*'"fable-mirror"'*)
      echo "fable-mirror write-fence: no Python interpreter on PATH; failing closed (blocked)." >&2
      exit 2 ;;
    *) exit 0 ;;
  esac
fi

# CLAUDE_PROJECT_DIR is set in the hook process environment by the harness, but this script runs
# under `set -u`, so a bare `${CLAUDE_PROJECT_DIR}` aborts with "unbound variable" and exit 1 the
# moment it is absent — and exit 1 on PreToolUse is a NON-blocking error (only exit 2 blocks).
# That is a silent FAIL-OPEN on the one fence that is actually wired. Observed 2026-08-06 running
# this hook by hand. Fall back to the script's own location, which is inside the repo by
# construction, so the fence works when invoked outside the harness too.
REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)}"
EVAL_PY="$REPO/.claude/hooks/fable-mirror-write-fence.py"

if [ ! -f "$EVAL_PY" ]; then
  # Same asymmetry as the missing-interpreter case above: fail closed only for fable-mirror.
  case "$input" in
    *'"agent_type"'*'"fable-mirror"'*)
      echo "fable-mirror write-fence: evaluator not found at $EVAL_PY; failing closed (blocked)." >&2
      exit 2 ;;
    *) exit 0 ;;
  esac
fi

# The evaluator independently requires CLAUDE_PROJECT_DIR and fails CLOSED without it (correct).
# Hand it the resolved root so the fence is testable outside the harness; the fallback is derived
# from this script's own location, which is inside the repo by construction — it cannot widen the
# allow-root to somewhere the hook does not already live.
export CLAUDE_PROJECT_DIR="$REPO"

printf '%s' "$input" | "$PY" "$EVAL_PY"
rc=$?

# THE REMAINING FAIL-OPEN, closed 2026-08-06. The evaluator blocks with exit 2 and allows with
# exit 0 — but any OTHER non-zero code (an unhandled exception is exit 1, a SIGKILL is 137, a
# harness timeout kills the pipeline) is a NON-BLOCKING error on PreToolUse: the write would
# proceed. `exit $?` therefore propagated a crash as an allow. That is the same shape as the
# `${CLAUDE_PROJECT_DIR}`/`set -u` defect above: the wrapper was weaker than the Python it
# wrapped. Normalize every unexpected code to 2 for fable-mirror calls, and leave every other
# caller alone.
if [ "$rc" -ne 0 ] && [ "$rc" -ne 2 ]; then
  case "$input" in
    *'"agent_type"'*'"fable-mirror"'*)
      echo "fable-mirror write-fence: evaluator exited $rc (not 0/2); failing closed (blocked)." >&2
      exit 2 ;;
    *) exit 0 ;;
  esac
fi

exit $rc
