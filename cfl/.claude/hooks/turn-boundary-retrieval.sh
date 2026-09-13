#!/usr/bin/env bash
# turn-boundary-retrieval.sh — hook wrapper for scripts/audit/turn_boundary_executor.py (M-9 / PR-3 B)
#
# ⛔ STAGED, NOT WIRED. This file is not referenced by .claude/settings.json. It is built
# so the wiring can be reviewed and applied by Jon (or a security-builder lane with his
# say-so) — see exchange/TB-1-PROPOSED-WIRING.md for the exact settings.json entry, which
# event it proposes, and why. Editing settings.json is out of scope for whoever wrote this
# file (dispatch TB-1-stage, 2026-09-05).
#
# WHAT THIS DOES
# --------------
# Gate on .claude/hooks/state/MODE, then run ONE cheap turn_boundary_executor.py pass and
# append its report to .claude/hooks/state/turn-boundary-retrieval.log. Every path below
# ends in `exit 0` — a recording hook that can fail a tool call, or (worse) block a Stop/
# UserPromptSubmit event, is worse than the gap it fills. This wrapper never emits exit 2
# and never prints a `decision` field.
#
# MODE GATE — the whole point of this file
# -----------------------------------------
# .claude/hooks/state/MODE holds exactly one word: AFK or LIVE.
#   MODE == AFK               -> proceed (safe: Jon is away from the keyboard)
#   MODE == LIVE              -> do nothing (Jon may be mid-thought; do not spend tokens
#                                 or wall-clock on his behalf without being asked)
#   MODE missing / unreadable -> UNKNOWN. Treat as LIVE. Do nothing.
#                                 (brief, verbatim: "the safe default is not to act while
#                                 Jon may be at the keyboard" — UNKNOWN dominates a PASS,
#                                 not the other way around)
#   MODE == anything else     -> also treated as "not AFK" -> do nothing. A gate that
#                                 fails open on a typo is not a gate.
#
# "Do nothing" is literal: no stdin read past what the OS already delivered, no log
# line written, no executor invoked, no side effect at all beyond this script's own
# process exiting. That is what the selftest (turn_boundary_wrapper_selftest.py) checks
# for the LIVE / absent / malformed cases — see its "writes nothing" assertions.
#
# STDIN — READ ONCE, ONLY IF WE ARE GOING TO ACT
# -----------------------------------------------
# The MODE check above needs no stdin at all, so it runs first and stdin is left
# completely untouched on every skip path. Only once MODE==AFK do we read stdin, and we
# read it exactly once (`cat` into a temp file), matching hook_fanout.sh's fix for the
# "a drained stream cannot tell you no payload was sent from someone already having read
# it" defect (measured 2026-09-04 on the PostCompact entry). Nothing downstream reads
# stdin a second time.
#
# PLATFORM CONTRACT this wrapper relies on — verified against
# https://code.claude.com/docs/en/hooks (fetched 2026-09-05), not from memory:
#   * The hook command receives one JSON payload on stdin with (at minimum) a
#     `session_id` field, across all hook events this repo wires.
#   * For most events "Claude Code writes stdout to the debug log and doesn't show it in
#     the transcript. The exceptions are UserPromptSubmit, UserPromptExpansion,
#     SessionStart, and PostModelSwitch, where Claude Code adds plain-text stdout as
#     context that Claude can see and act on." Stop does NOT add stdout as context.
#     turn_boundary_executor.py's own self-cost block explicitly reasons about "if
#     injected at the boundary" — that framing only makes literal sense if this wrapper
#     is eventually wired to one of the four context-adding events (UserPromptSubmit is
#     the one that means "a turn boundary" in the sense this script's docstring uses:
#     the point where a new human turn begins). See TB-1-PROPOSED-WIRING.md for the
#     reasoning and the exact proposed entry -- this file only stages the mechanism.
#   * Exit code contract: this wrapper always exits 0 regardless of what runs inside it,
#     so no event's blocking semantics (Stop/UserPromptSubmit exit-2 behavior) are ever
#     triggered by an internal fault.
#
# WHY IT IS SAFE TO SELF-STAGE (same posture as pre-stop-consult.sh's note): this file
# adds no capability. It cannot write outside its own log file and cannot alter
# permissions, settings, or credentials. It is inert until a human edits settings.json.
set -uo pipefail

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)}"
STATE_DIR="$REPO/.claude/hooks/state"
# Testability seam ONLY -- production wiring sets neither override, so both default to
# the real paths below. turn_boundary_wrapper_selftest.py uses these two to exercise the
# real repo (real executor, real py_closed.sh) end-to-end without ever touching the live
# MODE file a real session is depending on, or spamming the live log.
MODE_FILE="${TURN_BOUNDARY_MODE_FILE:-$STATE_DIR/MODE}"
LOG_FILE="${TURN_BOUNDARY_LOG_FILE:-$STATE_DIR/turn-boundary-retrieval.log}"
EXECUTOR="$REPO/scripts/audit/turn_boundary_executor.py"
PY_CLOSED="$REPO/.claude/hooks/py_closed.sh"

# --- MODE gate -----------------------------------------------------------------------
# Read the file directly rather than `test -r` + separate read: an OS-level unreadable
# file (locked, Drive-transient) can pass a permission-bit test and still fail to open,
# same lesson py_closed.sh already encodes. `cat` failing (missing file, ACL, whatever)
# leaves $mode empty, which the case statement below treats as "not AFK".
mode="$(cat -- "$MODE_FILE" 2>/dev/null)"
mode="$(printf '%s' "$mode" | tr -d '[:space:]')"

case "$mode" in
  AFK) : ;;                      # proceed
  *)   exit 0 ;;                 # LIVE, empty (missing/unreadable), or anything malformed
esac

# --- stdin: read exactly once, only now that we know we are acting -------------------
TMP="$(mktemp 2>/dev/null || echo "${TEMP:-${TMPDIR:-/tmp}}/turn-boundary-retrieval.$$")"
trap 'rm -f "$TMP"' EXIT
cat > "$TMP" 2>/dev/null || : # empty stdin is legitimate; the JSON parse below then fails closed

# --- extract session_id from the payload ----------------------------------------------
# A malformed payload (bad JSON, or JSON with no usable session_id) must write NOTHING —
# not the log, not a placeholder file. So the python step below is the only gate between
# "payload looked fine" and "we invoke the executor and append to the log."
sid="$(python -c '
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        d = json.load(fh)
except Exception:
    sys.exit(1)
sid = d.get("session_id") if isinstance(d, dict) else None
if not sid or not isinstance(sid, str):
    sys.exit(1)
print(sid)
' "$TMP" 2>/dev/null)"
rc=$?
if [ "$rc" -ne 0 ] || [ -z "$sid" ]; then
  exit 0   # malformed / no session_id: write nothing, exit clean
fi

# --- run the one cheap pass, append to the log, always exit 0 ------------------------
as_of="$(date +%Y-%m-%d 2>/dev/null)"
if [ -z "$as_of" ]; then
  exit 0   # clock unreadable somehow -- degrade to no-op rather than pass a bad --as-of
fi

mkdir -p "$STATE_DIR" 2>/dev/null || exit 0

{
  printf -- '----- turn-boundary-retrieval %s UTC session=%s as-of=%s -----\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ)" "$sid" "$as_of"
  bash "$PY_CLOSED" "$EXECUTOR" --session "$sid" --as-of "$as_of" 2>&1
  printf -- '----- end (exit=%s) -----\n' "$?"
} >> "$LOG_FILE" 2>/dev/null

exit 0
