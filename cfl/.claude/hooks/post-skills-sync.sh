#!/usr/bin/env bash
# PostToolUse hook — redeploy skills/ to ~/.claude/ the moment a skill file is edited.
#
# WHY THIS EXISTS
# ---------------
# `wiki/intake-triage/FINDING-skills-do-not-redeploy-mid-session-2026-08-06.md`: skills are
# deployed to `~/.claude/skills/` by `sync-universal.sh`, which the SessionStart stanza runs ONCE
# at session open. Every skill edit made DURING a session is therefore live in the repo and stale
# in the deployed copy until the next cold open. The already-recorded consequence of exactly this
# split is `project_skill-frontmatter-silent-autoinvoke-failure` — a defect that was fixed in the
# repo while the deployed copy kept it.
#
# WHAT IT HONESTLY DOES AND DOES NOT DO — read this before believing the gap is closed
# ------------------------------------------------------------------------------------
# It closes the FILE half. It does not close the LOAD half, and it must not be described as if it
# did. Verified against https://code.claude.com/docs/en/hooks (fetched 2026-08-06): `reloadSkills`
# is available ONLY in `SessionStart`'s `hookSpecificOutput` — doc: "SessionStart also accepts
# initialUserMessage, watchPaths, sessionTitle, and reloadSkills". `PostToolUse`'s
# `hookSpecificOutput` carries only `additionalContext` and `updatedToolOutput`. So this hook makes
# the deployed bytes current; whether the RUNNING session re-reads them is not something a
# PostToolUse hook can command. A fresh session, or a session started with the SessionStart stanza,
# gets the reload.
#
# MATCHER AND PATH FILTER — the correction to the previously-staged stanza
# ------------------------------------------------------------------------
# The stanza circulating as "a PostToolUse on `skills/**`" cannot be written that way. Doc:
# `PreToolUse`, `PostToolUse` ... matchers filter on "tool name" — `Bash`, `Edit|Write`, `mcp__.*`.
# A path in the matcher field would match no tool and the hook would never fire — the exact
# built-and-wired-to-nothing failure this whole sweep is about. Path filtering is a separate
# documented field: "you can filter more narrowly by setting the `if` field ... `if` uses
# permission rule syntax to match against the tool name and arguments together, so ...
# `"Edit(*.ts)"` runs only for TypeScript files." Hence matcher `Write|Edit|MultiEdit` plus
# `if: "Edit(skills/**)"` in the stanza, AND the belt-and-braces path check below, so the hook is
# still correct if the stanza is pasted without the `if`.
#
# SAFETY
# ------
# Reads its own stdin and the repo. Writes only to `~/.claude/{CLAUDE.md,skills/}` via the existing
# `sync-universal.sh` — the same command the SessionStart stanza already runs, with no new reach —
# plus a log line under `.claude/hooks/state/`. No network, no credentials, no deletes.
# Exit 0 on every path: a PostToolUse hook cannot block anyway (doc: exit 2 "Shows stderr to
# Claude; the tool already ran"), and a sync failure must never look like an edit failure.
#
# DEBOUNCE
# --------
# A skills edit run touches many files. `sync-universal.sh` measured at ~1-3 s on this Drive-backed
# checkout, which is cheap once and not cheap forty times. At most one sync per DEBOUNCE_SEC.

set -uo pipefail

DEBOUNCE_SEC="${CFL_SKILLS_SYNC_DEBOUNCE:-20}"

PAYLOAD="$(cat 2>/dev/null || true)"
REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)}"
cd "$REPO" 2>/dev/null || exit 0

STATE_DIR="$REPO/.claude/hooks/state"
LOG="$STATE_DIR/post-skills-sync.log"
STAMP_FILE="$STATE_DIR/skills-sync.stamp"
mkdir -p "$STATE_DIR" 2>/dev/null || exit 0

note() {
  printf '%s\t%s\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" "$*" >>"$LOG" 2>/dev/null
  printf 'post-skills-sync: %s\n' "$*" >&2
}

# Path check. grep, not jq: jq is not guaranteed present on this Windows box, and a hook that dies
# on a missing dependency is a hook that silently never fires.
FILEPATH="$(printf '%s' "$PAYLOAD" \
  | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 \
  | sed 's/.*:[[:space:]]*"//; s/"$//')"
FILEPATH="${FILEPATH//\\\\/\/}"

case "$FILEPATH" in
  *skills/*|*skills\\*) : ;;
  *) exit 0 ;;
esac

# Debounce.
NOW="$(date +%s)"
LAST="$(cat "$STAMP_FILE" 2>/dev/null || echo 0)"
case "$LAST" in ''|*[!0-9]*) LAST=0 ;; esac
if [ $((NOW - LAST)) -lt "$DEBOUNCE_SEC" ]; then
  note "SKIP debounce ($((NOW - LAST))s < ${DEBOUNCE_SEC}s) after $FILEPATH"
  exit 0
fi
printf '%s' "$NOW" >"$STAMP_FILE" 2>/dev/null || true

if [ ! -f "$REPO/sync-universal.sh" ]; then
  note "FAIL sync-universal.sh not found at $REPO — deployed skills are now STALE"
  exit 0
fi

if bash "$REPO/sync-universal.sh" >/dev/null 2>&1; then
  note "SYNCED after $FILEPATH (deployed copy current; live-session reload NOT implied — see header)"
else
  note "FAIL sync-universal.sh returned non-zero after $FILEPATH — deployed skills may be STALE"
fi

exit 0
