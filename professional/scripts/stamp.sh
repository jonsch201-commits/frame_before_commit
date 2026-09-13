#!/usr/bin/env bash
# stamp.sh — U8 emitter. Prints the channel-format stamp from the clock, so writers PASTE, never
# compose. The n=4 defect class (stamp written before the clock is read) dies at the point of
# composition: this script has no input, so there is nothing to compose.
#
# Usage:
#   bash scripts/stamp.sh            -> "2026-08-15 07:55:03 CDT [measured, clock-then-stamp]"
#   bash scripts/stamp.sh --line PRO -> "PRO — 2026-08-15 07:55:03 CDT [measured, clock-then-stamp]"
#
# The tag is earned, not asserted: it is true by construction only if the output of THIS script is
# pasted unedited. An edited stamp is [estimated] regardless of what it claims.
set -euo pipefail

now="$(date '+%Y-%m-%d %H:%M:%S %Z')"
stamp="$now [measured, clock-then-stamp]"

if [ "${1:-}" = "--line" ] && [ -n "${2:-}" ]; then
  printf '%s — %s\n' "$2" "$stamp"
else
  printf '%s\n' "$stamp"
fi
