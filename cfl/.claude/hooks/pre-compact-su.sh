#!/usr/bin/env bash
# PreCompact hook — the Standard Update's missing TRIGGER.
#
# WHY THIS EXISTS
# ---------------
# Jon, 2026-08-06, verbatim:
#   "It could literally be built into the compact command as I understand."
#
# He is right about the trigger and half-right about the mechanism. The Standard Update is a
# session-close ritual that currently depends on somebody REMEMBERING to run it. A compact is
# precisely the moment session state is about to be lost, so it is precisely the moment the SU
# matters. `PreCompact` is a real hook event in the current version and it fires exactly there.
#
# WHERE THE IDEA HAS TO BEND (measured, not assumed — see docs/su-in-compact-2026-08-06.md):
#
#   1. THE HOOK CANNOT RUN THE GATE. `scripts/audit/su_gate.sh` was measured at >5 minutes on
#      this checkout on 2026-08-06 (the header's "~51s" is stale). A hook that outruns its
#      `timeout` is KILLED, and a killed check reports nothing. So this hook does a CHEAP check
#      and RECORDS; it never runs the gate. Running the gate is `/su`'s job.
#
#      "Cheap" is measured, not assumed, because an unmeasured comment is how this repo gets
#      wrong numbers into its own headers. MEASURED 2026-08-06 on the live Drive-backed checkout:
#      13.4 s and 14.3 s wall clock across two runs, of which 0.5-0.8 s is CPU. `git status
#      --porcelain` alone is 3.9 s. The cost is Google Drive I/O, not work. It is well inside a
#      60 s timeout but it is NOT sub-second, and on an off-Drive checkout it would be. Anyone
#      shortening the staged `timeout` below 60 should re-measure first.
#
#   2. THE HOOK CANNOT SHOW YOU ANYTHING. Per the hooks docs, stdout on exit 0 goes to the debug
#      log and is NOT shown in the transcript; the only events whose stdout becomes context are
#      UserPromptSubmit, UserPromptExpansion and SessionStart. PreCompact is not one of them.
#      Therefore the output of this hook is a FILE — `exchange/su-close/precompact/`. A durable
#      artifact is the only channel a PreCompact hook actually has. The one thing it CAN surface
#      is a `decision: "block"` reason, which is why strict mode below exists.
#
# WHAT IT DOES
# ------------
#   - Reads the hook payload on stdin (JSON).
#   - Answers ONE question in under a second: has a Standard Update landed for today?
#     Evidence = `exchange/su-close/<YYYY-MM-DD>/` exists and is non-empty. That directory is
#     `su_close.sh`'s own artifact path, so this derives the answer from the thing that produces
#     it rather than from a marker someone has to remember to touch. (Derive, don't record.)
#   - Writes a receipt into `exchange/su-close/precompact/` either way. The receipt survives the
#     compact; the session's memory of it does not. That is the entire point.
#   - Exits 0. It does NOT block by default.
#
# WHY IT DOES NOT BLOCK BY DEFAULT, stated so nobody "fixes" it
# -------------------------------------------------------------
# An auto-compact fires when context is nearly exhausted. Blocking it there does not buy a
# Standard Update — it strands a session with no room to run one, and the SU takes minutes. A
# gate that fires when it cannot be satisfied is the RATIO_FLOOR failure this repo already has a
# scar from: an alarm calibrated to always fire stops being read.
#
# Strict mode is opt-in and MANUAL-ONLY by design: set CFL_PRECOMPACT_BLOCK=1 and it will block
# a *manual* `/compact` when no SU exists for today, emitting the reason. It never blocks an
# `auto` compact regardless of the variable, because you cannot ask a session out of context to
# go do more work.
#
# SAFETY, stated because the standing fence says security-adjacent config is propose-never-apply:
#   Reads: its own stdin, the repo's directory listing, `git` porcelain. No network, no
#   credentials, no deletes, no writes outside `exchange/su-close/precompact/`. It cannot grant
#   a capability. It is not self-registering — the settings.json stanza is STAGED FOR JON in
#   docs/su-in-compact-2026-08-06.md and this script does not install it.
#
# Exit: 0 always, except an intentional strict-mode block via JSON `decision`.

set -uo pipefail

PAYLOAD="$(cat 2>/dev/null || true)"

# CLAUDE_PROJECT_DIR is set in the hook process environment (hooks docs). Fall back to this
# script's own location so the hook still works if it is invoked by hand for testing.
REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
cd "$REPO" 2>/dev/null || exit 0

# ---------------------------------------------------------------------------------------------
# Payload fields. Pull with grep rather than jq: jq is not guaranteed present on this Windows box
# and a hook that dies on a missing dependency is a hook that silently never fires — the exact
# defect (T-06, pre-stop-consult.sh written-and-unwired) this file is trying not to repeat.
#
# `session_id`, `prompt_id`, `transcript_path`, `cwd`, `hook_event_name` and `permission_mode` are
# documented common input fields.
#
# `trigger` — RE-VERIFIED 2026-08-06 against https://code.claude.com/docs/en/hooks (fetched, not
# recalled). It is now documented BOTH as the PreCompact matcher dimension (values `manual`,
# `auto`) AND as PreCompact's event-specific INPUT field ("what initiated compaction"). The earlier
# "UNVERIFIED" note in this header and in the receipt was correct when written and is now stale;
# both are corrected. Still read defensively — an absent field yields "unknown", never a guess.
#
# `custom_instructions` remains UNVERIFIED: it does not appear in the current input schema for
# PreCompact. Nothing here depends on it.
#
# Output for PreCompact is top-level `decision` / `reason` only (no `hookSpecificOutput` for this
# event), which is what the strict-mode branch at the bottom emits.
# ---------------------------------------------------------------------------------------------
jget() { printf '%s' "$PAYLOAD" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed 's/.*:[[:space:]]*"//; s/"$//'; }

SID="$(jget session_id)";        SID="${SID:-unknown}"
TRIGGER="$(jget trigger)";       TRIGGER="${TRIGGER:-unknown}"
EVENT="$(jget hook_event_name)"; EVENT="${EVENT:-PreCompact}"
TRANSCRIPT="$(jget transcript_path)"

NOW="$(date +%Y-%m-%dT%H:%M:%S%z)"
TODAY="$(date +%F)"

# ---------------------------------------------------------------------------------------------
# The one question. Derived from su_close.sh's own artifact path, not from a marker file.
# ---------------------------------------------------------------------------------------------
SU_DIR="exchange/su-close/$TODAY"
if [ -d "$SU_DIR" ] && [ -n "$(ls -A "$SU_DIR" 2>/dev/null)" ]; then
  SU_TODAY="yes"
else
  SU_TODAY="no"
fi
LAST_SU="$(ls -1d exchange/su-close/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] 2>/dev/null | sed 's|.*/||' | sort | tail -1)"
LAST_SU="${LAST_SU:-none}"

# Cheap repo state. Every one of these is a fact a compact is about to make expensive to re-obtain.
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
HEADSHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
DIRTY="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
UNPUSHED="$(git rev-list --count '@{u}..HEAD' 2>/dev/null || echo 'n/a')"
WAKE_AGE="$(git log -1 --format=%cs -- exchange/WAKE.md 2>/dev/null || echo unknown)"

# ---------------------------------------------------------------------------------------------
# The receipt. This is the hook's ONLY real output channel — see note 2 in the header.
# ---------------------------------------------------------------------------------------------
OUTDIR="exchange/su-close/precompact"
mkdir -p "$OUTDIR" 2>/dev/null || exit 0
STAMP="$(date +%Y%m%dT%H%M%S)"
OUTFILE="$OUTDIR/$STAMP-${SID:0:8}.md"

{
  echo "# PreCompact receipt — $NOW"
  echo
  echo "Written by \`.claude/hooks/pre-compact-su.sh\`. A compact was about to discard this"
  echo "session's working state; these are the facts that cost something to re-obtain."
  echo
  echo "| field | value |"
  echo "|---|---|"
  echo "| event | \`$EVENT\` |"
  echo "| trigger | \`$TRIGGER\` (documented PreCompact input field, re-verified 2026-08-06) |"
  echo "| session | \`$SID\` |"
  echo "| branch | \`$BRANCH\` @ \`$HEADSHA\` |"
  echo "| uncommitted files | $DIRTY |"
  echo "| commits ahead of upstream | $UNPUSHED |"
  echo "| SU artifacts for $TODAY | **$SU_TODAY** |"
  echo "| last SU artifact dir | \`$LAST_SU\` |"
  echo "| exchange/WAKE.md last committed | $WAKE_AGE |"
  [ -n "$TRANSCRIPT" ] && echo "| transcript | \`$TRANSCRIPT\` |"
  echo
  if [ "$SU_TODAY" = "no" ]; then
    echo "## NO STANDARD UPDATE FOR $TODAY"
    echo
    echo "This compact discarded session state with no SU on record for today."
    echo "Run \`/su $TODAY --dry-run\` to see the scorecard, or"
    echo "\`bash scripts/audit/su_close.sh --as-of $TODAY\` for the real close."
  else
    echo "## SU present for $TODAY — \`$SU_DIR\`"
  fi
  echo
  echo "_Not a gate. This hook records; it does not block (see script header for why)._"
} > "$OUTFILE" 2>/dev/null

# ---------------------------------------------------------------------------------------------
# Strict mode — opt-in, MANUAL compacts only. Off unless CFL_PRECOMPACT_BLOCK=1.
# PreCompact takes a top-level `decision` per the hooks docs; `reason` is the only text this hook
# can put in front of a human or the model.
# ---------------------------------------------------------------------------------------------
if [ "${CFL_PRECOMPACT_BLOCK:-0}" = "1" ] && [ "$SU_TODAY" = "no" ] && [ "$TRIGGER" = "manual" ]; then
  printf '{"decision":"block","reason":"No Standard Update for %s. Receipt written to %s. Run /su %s (or su_close.sh --as-of %s), then compact again. Unset CFL_PRECOMPACT_BLOCK to compact anyway."}\n' \
    "$TODAY" "$OUTFILE" "$TODAY" "$TODAY"
  exit 0
fi

exit 0
