#!/usr/bin/env bash
# archive-backfill.sh -- mirror EVERY live session JSONL into raw/session-archive/, not just
# the one that happened to be open at a compact boundary.
#
# WHY. `scripts/precompact-capture.sh` archives the CURRENT session when PreCompact fires.
# That is the right thing to do and it is not enough: a session that never compacts is never
# archived at all. [m 2026-09-01 21:2x CDT] the archive held 6 of 39 live sessions = 15.4%,
# and step 7 of the postcompact pipeline has been reporting exactly that FAIL without anything
# in the trunk being able to act on it. A measurement with no remedy wired to it is a number,
# not a control.
#
# WHAT IS AT STAKE, and it is a standing Jon constraint, not a preference. Jon, 2026-08-09
# (verbatim, typos his): "All must be recoverable, keep json." and "4. Yeah no deletion. And
# no writing PII to Github." The live copy under ~/.claude/projects/ is the EXPOSED one --
# `cleanupPeriodDays` has already taken sessions permanently elsewhere in this fleet. The
# archive on G: is the durable one. 33 unarchived sessions were 33 sessions one retention
# sweep from gone.
#
# PII / EGRESS POSTURE, stated before it runs. raw/session-archive is gitignored and stays on
# G:. `git remote -v` is EMPTY by standing Jon gate. Nothing this script copies can reach a
# git host, and Jon 2026-08-19 places C:/G:/D: and non-public repos in one trust zone. This
# script never pushes, never writes outside this trunk, and never touches a sibling.
#
# COUNTERS COUNT THE EFFECT, NEVER THE CALL -- the rule this trunk paid for on 2026-09-01,
# when a converter that printed "SKIP" and exited 0 was counted as six renders. Here,
# `copied` increments only after cp returns 0 AND the destination exists with nonzero size.
#
# Usage:  bash scripts/archive-backfill.sh [--dry-run]
# Exit:   0 nothing failed; 1 at least one copy failed; 2 the source population is unreadable.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2

# R4 (2026-09-04): key derived by scripts/project_dirs.py; --primary = the dir this tree writes to NOW.
# BOUND: this backfill walks the PRIMARY dir only; sessions under a previous key are the previous key's backfill.
PROJ_DIR="${PRO_PROJECT_DIR:-$(python "$(dirname "$0")/project_dirs.py" --primary 2>/dev/null)}"
ARCHIVE_ROOT="${PRO_ARCHIVE_ROOT:-raw/session-archive}"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

if [ ! -d "$PROJ_DIR" ]; then
  echo "BACKFILL: UNKNOWN -- project dir not found: $PROJ_DIR"
  exit 2
fi

live=0; copied=0; fresh=0; failed=0; subdirs=0
for j in "$PROJ_DIR"/*.jsonl; do
  [ -f "$j" ] || continue
  live=$((live + 1))
  sid="$(basename "$j" .jsonl)"
  dest="$ARCHIVE_ROOT/$sid/$sid.jsonl"

  # Freshness by mtime AND size: an archived copy that is older OR shorter than the live
  # file is stale. Size alone would miss an in-place rewrite; mtime alone would miss a
  # truncated copy from a failed run.
  if [ -f "$dest" ] \
     && [ "$(stat -c %Y "$dest")" -ge "$(stat -c %Y "$j")" ] \
     && [ "$(stat -c %s "$dest")" -ge "$(stat -c %s "$j")" ]; then
    fresh=$((fresh + 1))
    main_fresh=1
  else
    main_fresh=0
  fi

  if [ "$main_fresh" -eq 0 ]; then
    if [ "$DRY" -eq 1 ]; then
      copied=$((copied + 1))
    else
      mkdir -p "$ARCHIVE_ROOT/$sid"
      if cp -f "$j" "$dest" 2>/dev/null && [ -s "$dest" ]; then
        copied=$((copied + 1))
      else
        failed=$((failed + 1))
        echo "BACKFILL: COPY-FAIL $sid"
      fi
    fi
  fi

  # subagent JSONLs are a channel that appears in NO main transcript (universal CLAUDE.md,
  # channel 2). Losing them loses Jon's mid-turn messages to subagents specifically.
  # 2026-09-04 (P4-8): this block used to sit INSIDE the main-file copy branch, so a session
  # whose main JSONL was already fresh never had NEW subagent lanes archived, and `subdirs`
  # counted copies-this-run while printing as if it were a population. Measured 91 live vs 88
  # archived with the line reading `subagent-dirs=0`. Now: per-file, every live session, and
  # the printed numbers are counted from disk after the loop.
  sdir="${j%.jsonl}/subagents"
  if [ -d "$sdir" ]; then
    for a in "$sdir"/*; do
      [ -f "$a" ] || continue
      adest="$ARCHIVE_ROOT/$sid/subagents/$(basename "$a")"
      if [ -f "$adest" ]          && [ "$(stat -c %Y "$adest")" -ge "$(stat -c %Y "$a")" ]          && [ "$(stat -c %s "$adest")" -ge "$(stat -c %s "$a")" ]; then
        continue
      fi
      if [ "$DRY" -eq 1 ]; then subdirs=$((subdirs + 1)); continue; fi
      mkdir -p "$ARCHIVE_ROOT/$sid/subagents"
      if cp -f "$a" "$adest" 2>/dev/null && [ -s "$adest" ]; then
        subdirs=$((subdirs + 1))
      else
        failed=$((failed + 1)); echo "BACKFILL: COPY-FAIL $sid/subagents/$(basename "$a")"
      fi
    done
  fi
done

if [ "$live" -eq 0 ]; then
  echo "BACKFILL: UNKNOWN -- zero live sessions found under $PROJ_DIR. A zero population is UNKNOWN, never a pass."
  exit 2
fi

held=$(find "$ARCHIVE_ROOT" -mindepth 2 -maxdepth 2 -name '*.jsonl' 2>/dev/null | wc -l | tr -d ' ')
sub_live=$(find "$PROJ_DIR" -path '*/subagents/*' -name 'agent-*.jsonl' 2>/dev/null | wc -l | tr -d ' ')
sub_held=$(find "$ARCHIVE_ROOT" -path '*/subagents/*' -name 'agent-*.jsonl' 2>/dev/null | wc -l | tr -d ' ')
pfx="BACKFILL"; [ "$DRY" -eq 1 ] && pfx="BACKFILL(dry-run)"
echo "$pfx: live=$live copied=$copied already-fresh=$fresh failed=$failed; subagent-jsonls live=$sub_live archived=$sub_held copied-this-run=$subdirs; archive now holds $held session jsonl(s)"
[ "$DRY" -eq 0 ] && [ "$sub_held" -lt "$sub_live" ] && echo "BACKFILL: SUBAGENT-GAP $((sub_live - sub_held)) live subagent jsonl(s) not in archive after this run" && failed=$((failed + 1))
[ "$failed" -gt 0 ] && exit 1
exit 0
