#!/usr/bin/env bash
# render-sessions.sh -- JSONL -> markdown, so the layer graph RAG embeds is not stale.
#
# JON'S ORDER, 2026-09-01, verbatim, typos his:
#   "Your PreCompact hook mirrors JSONL. It does NOT render md. raw/transcripts/claude-code/*.md
#    newest is 2026-08-21. That md layer is what graph RAG embeds. Fix is a hook, not a habit."
#   "(3) Acceptance test, committed, run by the hourly beat: newest md in raw/ must be younger
#    than the newest compact stamp, else FAIL. A capture that prints `copied 0 / failed 0` is
#    UNKNOWN, not PASS."
#
# WE DO NOT OWN A RENDERER AND WE DO NOT WRITE ONE. CFL's chat-exporter is the fleet converter
# (CFL confirmed 2026-09-01: "YES chat-exporter is the fleet converter"). We CALL it.
#   ⛔ If it is missing or fails, this script reports UNKNOWN and exits non-zero.
#      It NEVER falls back to a hand-rolled renderer -- a silent fallback would make a broken
#      dependency look like a working one, which is the exact class this whole effort is about.
#
# EMPLOYER GATE, stated BEFORE the parser runs (Professional CLAUDE.md: employer-identifying
# content is GATED, not banned):
#   Output stays in this trunk. `git remote -v` is EMPTY by standing Jon gate, so nothing
#   rendered here can reach a git host. Jon 2026-08-19: non-public repos and C:/G:/D: are one
#   trust zone. This script never pushes, never leaves the trunk, and never writes to a sibling.
#
# Usage:  bash scripts/render-sessions.sh [--check] [--all]
#   (default) render any archived session whose md is missing or older than its jsonl
#   --check   acceptance test only, render nothing: newest md must be younger than newest
#             compact stamp. Exit 0 PASS, 1 FAIL, 2 UNKNOWN.
#   --all     re-render every archived session (ignores freshness)
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2
CONV="${PRO_CONVERTER:-N:/claude-cfl/clone/skills/chat-exporter/scripts/convert-claude-code.py}"
OUT="${PRO_RENDER_OUT:-raw/transcripts/claude-code}"
STAMPS="${PRO_STAMPS:-exchange/precompact-receipts.log}"
MODE="render"
# SOURCE: the LIVE project dir by default, as of 2026-09-01.
# [m] the archive holds 6 of 37 live sessions = 16%, so an archive-sourced render can only
# ever cover 16% of this trunk's history -- and the wake hook was defaulting to exactly
# that while its own step 1 reported PASS. The two facts never collided because nobody
# printed the POPULATION next to the verdict. It is printed now, on every run.
# Widening this is safe ONLY because the freshness skip was repaired in the same edit: on
# the old glob that branch was unreachable, so 37 sessions would have been re-converted,
# in full, on every single wake.
# R4 (2026-09-04): the key is DERIVED from this tree's path by scripts/project_dirs.py, never typed.
# ALL dirs this tree has lived under are rendered: after a drive move the old sessions stay under the old key.
PROJ_DIR="${PRO_PROJECT_DIR:-$(python "$(dirname "$0")/project_dirs.py" --primary 2>/dev/null)}"
[ -n "$PROJ_DIR" ] || { echo "RENDER: UNKNOWN -- no project dir resolves for this tree (project_dirs.py); a scan that cannot run is UNKNOWN"; exit 2; }
ALL_PROJ_DIRS="${PRO_PROJECT_DIR:-$(python "$(dirname "$0")/project_dirs.py" 2>/dev/null | tr '\n' ' ')}"
SRC_GLOB="${PRO_RENDER_SRC:-$(for d in $ALL_PROJ_DIRS; do printf '%s/*.jsonl ' "$d"; done)}"
[ "${1:-}" = "--check" ] && MODE="check"
[ "${1:-}" = "--all" ] && MODE="all"

# newest_mtime() is defined ONCE, HERE, above every path that calls it.
#
# [m 2026-09-01 21:2x] IT WAS NOT ONCE, AND THEN IT WAS ZERO. Two bodies lived in this
# file -- a `find -printf` copy here and an `ls -t`/`stat` copy at the bottom. The note
# that replaced them called the first one "silently shadowed by the later definition."
# THAT DIAGNOSIS WAS WRONG. A bash function definition takes effect when EXECUTION
# reaches it, and --check mode exits above the bottom definition, so the two bodies were
# never in competition: the top one served --check, the bottom one served the render
# path. Deleting the top one deleted --check's only measurement, and --check is step 2
# of the postcompact pipeline.
#
# THE FAILURE MODE IS THE POINT: an undefined function returns EMPTY, and the caller
# read empty as a measured zero -- "raw/transcripts/claude-code holds no .md at all"
# while 76 .md files sat in it. `command not found` went to stderr, which the pipeline
# does not print. A MEASUREMENT THAT COULD NOT RUN WAS REPORTED AS A MEASUREMENT THAT
# RAN AND FOUND NOTHING. That is the register's own class, one layer down: not a step
# that did not happen reported as one that did, but an INSTRUMENT that did not exist
# reported as an instrument that found zero.
#
# So --check no longer trusts an empty return. It counts the files itself, and an empty
# mtime over a non-empty directory is UNKNOWN, which is never a pass.
newest_mtime() { ls -t "$1"/*.md 2>/dev/null | head -1 | while read -r f; do stat -c %Y "$f"; done; }
count_md()     { ls -1 "$1"/*.md 2>/dev/null | wc -l | tr -d ' '; }

newest_stamp() {  # epoch of the newest compact boundary we have a receipt for
  [ -f "$STAMPS" ] || return 1
  # receipt lines carry an ISO-ish local timestamp; take the newest parseable one
  local best=""
  while IFS= read -r line; do
    local d
    d=$(printf '%s\n' "$line" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' | head -1)
    [ -n "$d" ] || continue
    local e; e=$(date -d "$d" +%s 2>/dev/null) || continue
    [ -z "$best" ] && best="$e"
    [ "$e" -gt "$best" ] && best="$e"
  done < "$STAMPS"
  [ -n "$best" ] && printf '%s\n' "$best"
}

if [ "$MODE" = "check" ]; then
  st=$(newest_stamp) || { echo "RENDER-CHECK: UNKNOWN -- no parseable compact stamp in $STAMPS"; exit 2; }
  if [ ! -d "$OUT" ]; then
    echo "RENDER-CHECK: FAIL -- $OUT does not exist; this trunk has rendered ZERO md, ever."
    exit 1
  fi
  n_md=$(count_md "$OUT")
  md=$(newest_mtime "$OUT")
  if [ -z "$md" ] && [ "$n_md" -eq 0 ]; then
    echo "RENDER-CHECK: FAIL -- $OUT holds no .md at all (0 files; newest compact stamp $(date -d @"$st" '+%F %T'))"
    exit 1
  fi
  if [ -z "$md" ]; then
    echo "RENDER-CHECK: UNKNOWN -- $OUT holds $n_md .md file(s) but newest_mtime returned nothing; the INSTRUMENT failed, not the trunk. UNKNOWN is never a pass."
    exit 2
  fi
  if [ "$md" -ge "$st" ]; then
    echo "RENDER-CHECK: PASS -- newest md $(date -d @"$md" '+%F %T') >= newest compact stamp $(date -d @"$st" '+%F %T')"
    exit 0
  fi
  echo "RENDER-CHECK: FAIL -- newest md $(date -d @"$md" '+%F %T') is OLDER than newest compact stamp $(date -d @"$st" '+%F %T') (lag $(( (st-md)/3600 ))h)"
  exit 1
fi

if [ ! -f "$CONV" ]; then
  echo "RENDER: UNKNOWN -- converter not found at: $CONV"
  echo "  This is UNKNOWN, not zero, and NOT a reason to hand-roll one. Fix the path or the dependency."
  exit 2
fi

mkdir -p "$OUT"
rendered=0; skipped=0; failed=0; scanned=0; noop=0
# ============================================================================
# TWO STACKED DEFECTS, MEASURED AND FIXED 2026-09-01 19:3x. Both shipped by the
# seat that wrote this script to END this class, and step 2 (the acceptance
# test) is the only reason either was found -- step 1 reported rendered=6 while
# NOTHING was written.
#
#   D1  THE FRESHNESS GLOB COULD NEVER MATCH. It searched "*<full-uuid>*.md",
#       but the converter names its output with only the FIRST SIX characters
#       of the session id (code-2026-08-18-20690e-...). [m] 0 of 6 matched on
#       the full uuid; 6 of 6 match on the 6-char stem. The skip branch was
#       UNREACHABLE, so every session was handed to the converter every run.
#   D2  `rendered` COUNTED EXIT CODES, NOT FILES WRITTEN. The converter prints
#       "SKIP: <path> already exists. Use --force to overwrite." AND EXITS 0.
#       Six exit-zeros became "rendered=6" with zero bytes written.
#
# THE RULE THIS ENCODES: a counter must count the EFFECT, never the CALL.
# Below, `rendered` is incremented only when the converter's own output does
# not say it skipped -- and the run then proves it by mtime, both directions.
# ============================================================================
# THE EFFECT PROOF IS STAT ARITHMETIC, NOT `find`. The first form of this check
# was written `-newmermt` -- a TYPO -- so find errored, stderr went to /dev/null,
# `fresh` came back empty, and the check reported a FALSE RED against a directory
# that had just been written. A later edit then deleted the `run_start` the line
# still referenced, and `set -u` (line 28) aborted the script silently at that
# point: counters printed, no verdict line, exit 1.
# ⛔ TWO DIAGNOSES WERE PUBLISHED FOR THIS BEFORE THE LINE WAS READ -- unsupported
# `@epoch` syntax, then an MSYS path find could not stat. BOTH WERE WRONG. Clock
# skew was ruled out by measurement (/tmp and G: agreed to 1s) and was not it
# either. ⭐ The cause was found by reading the line, never by theorising about
# it, and a swallowed stderr is what made three runs look like three mysteries.
# Comparing two integers has no error channel to swallow.
# newest_mtime() lives at the top of this file, above --check. Do not redefine it here.
PRE_NEWEST=$(newest_mtime "$OUT"); PRE_NEWEST=${PRE_NEWEST:-0}
for j in $SRC_GLOB; do
  [ -f "$j" ] || continue
  scanned=$((scanned + 1))
  base=$(basename "$j" .jsonl)
  stem=$(printf '%s' "$base" | cut -c1-6)     # D1: the converter's own naming
  # freshness: skip when an md exists that is newer than the jsonl
  if [ "$MODE" != "all" ]; then
    existing=$(find "$OUT" -name "*-${stem}-*.md" -newer "$j" -print -quit 2>/dev/null)
    if [ -n "$existing" ]; then skipped=$((skipped + 1)); continue; fi
  fi
  # Reaching here means: no md exists, OR the md is OLDER than the jsonl. Both
  # want a write. Without --force the converter refuses the second case and
  # exits 0, which is precisely how a stale render survived a "PASS" for 1h25m.
  cout=$(python "$CONV" --run "$j" --out "$OUT" --force 2>&1)
  crc=$?
  if [ "$crc" -ne 0 ]; then
    failed=$((failed + 1))
    echo "  FAILED: $j"
  elif printf '%s' "$cout" | grep -q '^SKIP:'; then
    # D2: exit 0 and wrote nothing. This is NOT a render.
    noop=$((noop + 1))
  else
    rendered=$((rendered + 1))
    [ -n "${PRO_RENDER_VERBOSE:-}" ] && { echo "  RENDERED: $j"; printf '%s
' "$cout" | grep -E '^(WROTE|SKIP)' ; }
  fi
done

echo "RENDER: scanned=$scanned rendered=$rendered skipped=$skipped noop=$noop failed=$failed  out=$OUT"
echo "  POPULATION: $SRC_GLOB  (this is what was scanned; it is NOT necessarily every live session)"
# EFFECT PROOF: a claimed render must ADVANCE the newest output mtime.
if [ "$rendered" -gt 0 ]; then
  POST_NEWEST=$(newest_mtime "$OUT"); POST_NEWEST=${POST_NEWEST:-0}
  if [ "$POST_NEWEST" -le "$PRE_NEWEST" ]; then
    echo "RENDER: FAIL -- claimed rendered=$rendered but the newest md in $OUT did not advance"
    echo "  ($PRE_NEWEST -> $POST_NEWEST). A counter that counts CALLS instead of EFFECTS is the"
    echo "  exact defect this line exists to catch: on 2026-09-01 this script reported rendered=6"
    echo "  while writing zero bytes, and only the acceptance test noticed."
    exit 1
  fi
  echo "  EFFECT PROVEN: newest md mtime advanced $PRE_NEWEST -> $POST_NEWEST"
fi
if [ "$noop" -gt 0 ]; then
  echo "  NOTE: $noop session(s) exited 0 while writing nothing (converter SKIP, output already present)."
  echo "  Counted as noop, never as rendered. Use --all to force a re-render."
fi
# Jon's clause 3, enforced here: a run that rendered nothing is UNKNOWN, never a clean pass.
if [ "$scanned" -eq 0 ]; then
  echo "RENDER: UNKNOWN -- scanned 0 sessions. A zero population is not a pass."
  exit 2
fi
if [ "$rendered" -eq 0 ] && [ "$skipped" -eq 0 ] && [ "$noop" -eq 0 ]; then
  echo "RENDER: UNKNOWN -- rendered 0 and skipped 0 out of $scanned. The counters do not account"
  echo "  for the population, which means this run cannot certify anything."
  exit 2
fi
# 2026-09-12: subagent JSONLs (<key>/<sid>/subagents/agent-*.jsonl) were never in SRC_GLOB; same fleet converter, driven per file, isMeta turns appended verbatim.
python "$ROOT/scripts/render-subagents.py" || echo "RENDER-SUBAGENTS: nonzero exit (UNKNOWN or failed; see its lines above) -- does not alter the main-session verdict"
[ "$failed" -gt 0 ] && exit 1
exit 0
