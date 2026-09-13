#!/usr/bin/env bash
# py_closed.sh — the fail-closed wrapper CFL's python hook entries run through.
#
# WHY THIS EXISTS
# ----------------
# H-1's harness run (wiki/intake-triage/H1-hook-harness-2026-09-02.md) found the shape of
# every CFL hook fault to date is the same one: a `python <script>` hook entry whose target
# script file is missing, empty, or unreadable. Bash then either (a) lets python fail with a
# traceback that never reaches the platform's stdout channel, or (b) — as measured for
# `pre-stop-consult.sh` — falls through an unchecked exit code straight to an unconditional
# `exit 0`. Either way the hook is silently a no-op: FAIL-OPEN-SILENT.
#
# WHAT THIS DOES
# --------------
# Usage:  bash "${CLAUDE_PROJECT_DIR}/.claude/hooks/py_closed.sh" [--block] <script.py> [args...]
#
# Before ever invoking python, this wrapper actually READS the target script (not just
# `test -f` / `test -r`, which can both pass against a file the OS then refuses to open —
# see wiki reference "Read-Fence Is Tool-Layer, Not Process-Layer") and checks:
#   1. the path exists as a regular file
#   2. `head -c 64` off it succeeds and returns at least one byte
#   3. its on-disk size (via `wc -c`) is > 0
#
# On any failure it:
#   - prints `HOOK-FAULT <script> <reason>` to stderr (visible to a human tailing logs, and
#     to the platform's own stderr capture for non-Stop/PreToolUse events)
#   - appends a JSON line {ts, hook, script, reason, cwd} to
#     N:\claude-gists-private\HOOK-FAULTS-cfl.jsonl, and — if that path is not writable from
#     this trunk (a fresh clone off N:\, a different machine) — falls back to
#     exchange/su-close/HOOK-FAULTS.jsonl inside the project. Both writes are best-effort;
#     neither failing to write blocks the wrapper's own exit-code contract below.
#   - exits 1 by default, or 2 with --block (see BLOCKING SCOPE below)
#
# On success it execs `python "$script" "$@"` with stdin passed through untouched (`exec`,
# not a subshell call, so python inherits this process's PID and the wrapper adds no extra
# layer to signal/timeout handling).
#
# BLOCKING SCOPE — --block is for PreToolUse fences ONLY.
# -----------------------------------------------------------------------------------------
# Per official Claude Code hook semantics: exit 2 BLOCKS the triggering action; any other
# non-zero exit is a non-blocking, visible error. That distinction is safe for PreToolUse
# (blocking a single tool call is recoverable) and dangerous for Stop/SubagentStop/SessionEnd
# — a hook-infra fault at session-teardown time exiting 2 there would trap Jon's session in a
# stop-block loop over a wrapper bug, not a real policy decision. So --block is opt-in and
# this repo's settings.json rewrap (see H-3 report) passes it ONLY to the one PreToolUse
# entry that is itself a security fence (fable-mirror-write-fence). Every Stop/SubagentStop/
# SessionEnd/SessionStart/PreCompact/PostCompact entry is wrapped WITHOUT --block, so a
# faulted script there degrades to exit 1 (a visible non-blocking error) rather than a block.
# -----------------------------------------------------------------------------------------
set -uo pipefail

FAULT_LOG_PRIMARY="N:\\claude-gists-private\\HOOK-FAULTS-cfl.jsonl"
REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)}"
FAULT_LOG_FALLBACK="$REPO/exchange/su-close/HOOK-FAULTS.jsonl"

block=0
if [ "${1:-}" = "--block" ]; then
  block=1
  shift
fi

script="${1:-}"
shift || true

# json_escape <string> — minimal escaping (backslash, double-quote, control chars) so the
# fault line stays valid JSON without depending on python (which may be the very thing that
# is broken).
json_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | tr -d '\r' | awk '{printf "%s\\n", $0}' | sed -e 's/\\n$//'
}

log_fault() {
  reason="$1"
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ)"
  cwd="$(pwd 2>/dev/null || echo unknown)"
  esc_script="$(json_escape "$script")"
  esc_reason="$(json_escape "$reason")"
  esc_cwd="$(json_escape "$cwd")"
  line="{\"ts\":\"$ts\",\"hook\":\"py_closed.sh\",\"script\":\"$esc_script\",\"reason\":\"$esc_reason\",\"cwd\":\"$esc_cwd\"}"

  wrote=0
  if mkdir -p "N:\\claude-gists-private" 2>/dev/null; then
    if printf '%s\n' "$line" >>"$FAULT_LOG_PRIMARY" 2>/dev/null; then
      wrote=1
    fi
  fi
  mkdir -p "$(dirname "$FAULT_LOG_FALLBACK")" 2>/dev/null
  if printf '%s\n' "$line" >>"$FAULT_LOG_FALLBACK" 2>/dev/null; then
    wrote=1
  fi
  [ "$wrote" -eq 1 ] || printf 'py_closed.sh: WARNING could not write fault ledger to either location\n' >&2
}

fault() {
  reason="$1"
  printf 'HOOK-FAULT %s %s\n' "$script" "$reason" >&2
  log_fault "$reason"
  if [ "$block" -eq 1 ]; then
    exit 2
  else
    exit 1
  fi
}

[ -n "$script" ] || fault "no-script-argument"
[ -f "$script" ] || fault "not-a-regular-file"

# Actual read, not just a permission-bit test: an OS-level unreadable file (locked, ACL,
# Drive-transient) can pass `test -r` and still fail to open.
head_bytes="$(head -c 64 -- "$script" 2>/dev/null | wc -c | tr -d ' ')"
if [ -z "$head_bytes" ] || [ "$head_bytes" -eq 0 ] 2>/dev/null; then
  fault "unreadable-or-empty"
fi

size="$(wc -c < "$script" 2>/dev/null | tr -d ' ')"
case "$size" in
  ''|*[!0-9]*) fault "size-check-failed" ;;
esac
if [ "$size" -eq 0 ]; then
  fault "zero-byte-script"
fi

exec python "$script" "$@"
