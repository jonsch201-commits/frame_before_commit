#!/usr/bin/env bash
# sh_closed.sh — the fail-closed wrapper CFL's plain-bash hook entries run through.
#
# WHY THIS EXISTS
# ----------------
# H-1c's harness run (wiki/intake-triage/H1-hook-harness-2026-09-02.md, --degrade phase)
# copied every wrapped hook script into the scratch clone with its bytes truncated to zero
# and re-ran the harness. The 11 python hooks wrapped by .claude/hooks/py_closed.sh all
# failed CLOSED and VISIBLE (HOOK-FAULT + non-zero exit). But CFL's four PLAIN bash hook
# entries — pre-stop-consult.sh, pre-compact-su.sh, fable-mirror-write-fence.sh,
# post-compact-wake.sh — failed OPEN: `bash <empty-file>` exits 0. Bash only fails closed on
# an UNREADABLE file (exit 126); a zero-byte file is syntactically valid (an empty script)
# and bash runs it to completion doing nothing, exit 0. A zero-byte shell script is exactly
# what a Drive-transient fault or a failed copy produces (see reference
# "Silent EINVAL Launcher and Copy-as-Deletion"), so this is the same fault shape py_closed.sh
# closes, just for the other interpreter.
#
# WHAT THIS DOES
# --------------
# Usage:  bash "${CLAUDE_PROJECT_DIR}/.claude/hooks/sh_closed.sh" [--block] <script.sh> [args...]
#
# Before ever invoking bash on the target, this wrapper:
#   1. confirms the path exists as a regular file
#   2. actually READS it — `head -c 64` into a variable, not just `test -f` / `test -r`,
#      which can both pass against a file the OS then refuses to open (see wiki reference
#      "Read-Fence Is Tool-Layer, Not Process-Layer")
#   3. checks its on-disk size (via `wc -c`) is > 0
#   4. runs `bash -n <script>` — a syntax-only check that catches a truncated-mid-write or
#      otherwise corrupted script without executing any of it
#
# On any failure it:
#   - prints `HOOK-FAULT <script> <reason>` to stderr
#   - appends a JSON line {ts, hook, script, reason, cwd} to
#     N:\claude-gists-private\HOOK-FAULTS-cfl.jsonl, and — if that path is not writable from
#     this trunk — falls back to exchange/su-close/HOOK-FAULTS.jsonl inside the project. Both
#     writes are best-effort; neither failing to write blocks the wrapper's own exit contract.
#   - exits 1 by default, or 2 with --block (see BLOCKING SCOPE below)
#
# On success it execs `bash "$script" "$@"` with stdin passed through untouched (`exec`, not
# a subshell call, so the wrapped script inherits this process's PID).
#
# LEDGER PATH IS OVERRIDABLE (trunk-agnostic) — added so this file can be published as a
# standalone prototype (N:\claude-gists-private\PROTO-sh_closed-v1.sh) and reused by another
# trunk without editing the hardcoded N:\ path in place:
#   --ledger <path>          overrides the primary ledger path for this invocation
#   $SH_CLOSED_LEDGER         same, via environment, checked if --ledger is not given
# Neither overrides the in-repo fallback ledger, which is always $REPO/exchange/su-close/HOOK-FAULTS.jsonl.
#
# BLOCKING SCOPE — --block is for PreToolUse fences ONLY. Same rule as py_closed.sh: exit 2
# BLOCKS the triggering action (safe for a single PreToolUse call); any other non-zero exit is
# a non-blocking, visible error (the right posture for Stop/PreCompact/SessionStart — a
# hook-infra fault at those points should never trap Jon in a stop-block loop over a wrapper
# bug). In this repo's settings.json rewrap (H-3b), --block is passed ONLY to the
# fable-mirror-write-fence.sh entry, because blocking a write is that hook's actual purpose.
# pre-stop-consult.sh, pre-compact-su.sh, and post-compact-wake.sh are wrapped WITHOUT --block.
set -uo pipefail

FAULT_LOG_PRIMARY_DEFAULT="N:\\claude-gists-private\\HOOK-FAULTS-cfl.jsonl"
REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)}"
FAULT_LOG_FALLBACK="$REPO/exchange/su-close/HOOK-FAULTS.jsonl"

block=0
FAULT_LOG_PRIMARY="${SH_CLOSED_LEDGER:-$FAULT_LOG_PRIMARY_DEFAULT}"

# Parse leading flags in either order: --block and/or --ledger <path>.
while [ $# -gt 0 ]; do
  case "$1" in
    --block)
      block=1
      shift
      ;;
    --ledger)
      FAULT_LOG_PRIMARY="${2:-$FAULT_LOG_PRIMARY}"
      shift 2
      ;;
    *)
      break
      ;;
  esac
done

script="${1:-}"
shift || true

# json_escape <string> — minimal escaping (backslash, double-quote, control chars) so the
# fault line stays valid JSON without depending on any interpreter that might itself be broken.
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
  line="{\"ts\":\"$ts\",\"hook\":\"sh_closed.sh\",\"script\":\"$esc_script\",\"reason\":\"$esc_reason\",\"cwd\":\"$esc_cwd\"}"

  wrote=0
  primary_dir="$(dirname "$FAULT_LOG_PRIMARY" 2>/dev/null)"
  if [ -n "$primary_dir" ] && mkdir -p "$primary_dir" 2>/dev/null; then
    if printf '%s\n' "$line" >>"$FAULT_LOG_PRIMARY" 2>/dev/null; then
      wrote=1
    fi
  fi
  mkdir -p "$(dirname "$FAULT_LOG_FALLBACK")" 2>/dev/null
  if printf '%s\n' "$line" >>"$FAULT_LOG_FALLBACK" 2>/dev/null; then
    wrote=1
  fi
  [ "$wrote" -eq 1 ] || printf 'sh_closed.sh: WARNING could not write fault ledger to either location\n' >&2
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

# Syntax-only check. Catches a truncated-mid-write or otherwise corrupted script (still
# nonzero bytes, but not parseable bash) that the size check above would let through — bash
# itself would otherwise run the valid PREFIX of a corrupted script and silently stop partway.
if ! bash -n -- "$script" 2>/dev/null; then
  fault "syntax-check-failed"
fi

exec bash "$script" "$@"
