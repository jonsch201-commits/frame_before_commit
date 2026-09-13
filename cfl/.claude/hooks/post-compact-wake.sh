#!/usr/bin/env bash
# post-compact-wake.sh — the half of the compact boundary CFL never built.
#
# WIRED 2026-08-07 as a SECOND SessionStart entry, matcher `compact|clear`. settings.json PARSE
# VERIFIED the same day: 2 SessionStart entries, matchers `startup|resume` and `compact|clear`.
# The `startup|resume` entry was deliberately NOT widened -- it runs a `git pull`, which has no
# business firing on a compact. The stanza is reproduced at the bottom of this header so it stays
# recoverable from this script alone if settings.json is ever rebuilt.
#
# WHY THIS EXISTS
# ---------------
# Jon, 2026-08-07, verbatim:
#   "need to let you know I did not follow your precise words and include the required text in
#    compact command, and not all projects have been getting this for me."
#
# He is reporting a defect in the PROCEDURE. `/su-compact` Step 5 ends by handing him a block to
# paste into `/compact`. That step puts a human in the loop at the exact moment the human is out
# of context, and it failed on the very session that wrote it.
#
# He asked for the automation twice before that:
#   "How do we adjust the compact command such that it will be as though you were waking up from
#    the compact? What roles in personal should have this feature?"          — 2026-08-04
#   "It could literally be built into the compact command as I understand."  — 2026-08-06 (B-1)
#
# WHY IT IS SessionStart AND NOT PreCompact
# ------------------------------------------
# `pre-compact-su.sh` already records the measured constraint, verified 2026-08-06 against the
# live hooks docs and independently corroborated twice in the corpus: PreCompact stdout on exit 0
# goes to the DEBUG LOG, not the transcript. The only events whose stdout becomes context are
# UserPromptSubmit, UserPromptExpansion and SessionStart. **A PreCompact hook cannot say anything
# to the session that survives it.** Its only channel is a file, which is why
# `exchange/su-close/precompact/` exists.
#
# SessionStart CAN. It fires with a `source` field, and `compact` is one of its values.
#
# THE EVIDENCE, WITH ITS LIMIT STATED
# ------------------------------------
# Claude Personal's `.claude/hooks/wake-probe.sh` emits `hookSpecificOutput.additionalContext` and
# was OBSERVED FIRING on `source=compact` on 2026-08-06 — recorded in that repo at
# `wiki/sources/sessions/wake-probe-fired-2026-08-06.md` and seen independently at a session open.
#
#   ** n=1, and it came after ~25 hours of silence. The fire is real; the reliability is NOT
#   established. ** Personal's probe header says exactly this and says DO NOT DELETE on the
#   strength of one firing. This script inherits that caveat rather than laundering it: if the
#   hook never fires, the session is no worse off than today, because today it fires zero times.
#
# WHAT IT EMITS, AND WHAT IT DELIBERATELY DOES NOT
# -------------------------------------------------
# It emits an IMPERATIVE OVER THE CLOCKED FILES — never their contents. Two reasons, both paid for:
#
#   1. Contents drift. CFL's `/wake` restates the six-file open order inline, and Personal's
#      `/wake` names that as a defect in its own text: "do not paste a remembered version of that
#      list here, because it can drift out of sync with its source." So this reads the count and
#      the names from disk at fire time and tells the session to OPEN them. Naming a file is not
#      reading it — that sentence is the payload.
#   2. Context is the scarce thing at a compact boundary. Injecting `CARRIER.md` would evict the
#      very material the compact was run to make room for.
#
# It does NOT summarise the session, does NOT judge whether an SU ran, and does NOT block. Judging
# is `/su`'s job and blocking a post-compact session is blocking a session that has nowhere to go.
#
# SAFETY
#   Reads: its own stdin, `git` porcelain, `ls`, `wc -c`. No network, no credentials, no writes of
#   any kind, no deletes. It cannot grant a capability. FAILS OPEN on every path — a hook that
#   breaks a session open is worse than no hook.
#
# STAGED SETTINGS STANZA — for Jon. This script does NOT install it.
# Add as a SECOND SessionStart entry; do not widen the existing `startup|resume` matcher, which
# runs a `git pull` that has no business firing on a compact.
#
#   {
#     "matcher": "compact|clear",
#     "hooks": [
#       { "type": "command",
#         "command": "bash \"${CLAUDE_PROJECT_DIR}/.claude/hooks/post-compact-wake.sh\"",
#         "timeout": 30,
#         "statusMessage": "Post-compact: re-grounding against the record..." }
#     ]
#   }
#
# Exit: 0 always.

set -u

PAYLOAD="$(cat 2>/dev/null || true)"

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
cd "$REPO" 2>/dev/null || exit 0

# No jq — absent from this box's Git Bash. The official samples use it and would silently no-op
# here, the same shape as `grep -P`. sed only.
SRC="$(printf '%s' "$PAYLOAD" | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
[ -n "$SRC" ] || SRC="unknown"

# Everything below is DERIVED at fire time. Nothing is recorded in this file that could go stale.
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
HEADSHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
DIRTY="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
UNPUSHED="$(git rev-list --count '@{u}..HEAD' 2>/dev/null || echo 'n/a')"
CARRIER_B="$(wc -c < exchange/CARRIER.md 2>/dev/null | tr -d ' ')"; CARRIER_B="${CARRIER_B:-0}"
WAKE_LINE="$(grep -m1 -i '^written:' exchange/WAKE.md 2>/dev/null || echo 'written: UNKNOWN')"
RECEIPTS="$(ls -1 exchange/su-close/precompact/*.md 2>/dev/null | wc -l | tr -d ' ')"

# ---------------------------------------------------------------------------
# COMPARANDS -- added 2026-08-24. These are NUMBERS, not prose, and they are
# printed here because this hook already runs at every compact boundary.
#
# WHY HERE AND NOT IN A NEW FILE: the root cause under eight of 2026-08-23/24's
# defects is that a fact needing later COMPARISON was written as a sentence in a
# document instead of as data. Prose cannot be diffed, so when the world moved,
# nothing could notice. See wiki/concepts/the-comparand-lives-in-prose.md.
#
# The two mechanisms that actually changed behaviour this week both worked for
# ONE reason -- they rode something that already runs. A tenth instrument nobody
# opens is the defect wearing a lab coat: exchange/ROUTING-LEDGER.md is 2,592
# rows of accurate, automatic, entirely unread data. So the test for anything
# proposed here is "what already runs, and can this ride it?" -- and the answer
# at a compact boundary is this hook.
LEDGER_PENDING="$(grep -c '| PENDING |' exchange/ROUTING-LEDGER.md 2>/dev/null | tr -d ' ')"
LEDGER_PENDING="${LEDGER_PENDING:-UNKNOWN}"
BASELINE_ASOF="$(grep -m1 '"as_of"' wiki/tracker/heartbeat-baseline.json 2>/dev/null                  | sed -e 's/.*: *"//' -e 's/".*//')"
BASELINE_ASOF="${BASELINE_ASOF:-ABSENT}"

esc() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\t/ /g'; }

M="POST-COMPACT RE-GROUNDING (SessionStart source=$(esc "$SRC")). "
M="${M}The working context is gone and the summary above is a SUMMARY, not the record. "
M="${M}MEASURED NOW: branch $(esc "$BRANCH") @ $(esc "$HEADSHA") | uncommitted $DIRTY | unpushed $UNPUSHED | "
M="${M}routing-ledger PENDING $(esc "$LEDGER_PENDING") | heartbeat baseline as_of $(esc "$BASELINE_ASOF") "
M="${M}(a baseline older than 14 days makes every direction UNKNOWN, never 'unchanged' -- and a "
M="${M}number recalled from prose must never be compared against an instrument that has since been "
M="${M}replaced: that shipped a false 'WORSE 9 -> 10' on 2026-08-24) | "
# CORRECTED 2026-08-14 -- the carrier byte gate is STRUCK. This line read, verbatim, until today:
#     M="${M}exchange/CARRIER.md ${CARRIER_B} B (gate 11901) | ..."
# 11,901 was falsified at n=2 on 2026-08-06 [relayed -- Personal's [measured], Claude Code 2.1.223]:
# a carrier at 11,871 B -- thirty bytes UNDER the gate -- was reduced to a bare path, while a 6,874 B
# file in the same boundary survived whole. It was never a threshold; it is the size one file happened
# to be on the one day it survived. What actually carries the carrier across a boundary is the
# preserve-verbatim classes in the compact instruction (paths, numbers, Jon's words, prohibitions,
# deferred items, open questions) -- not byte count. Report the size; never gate on it; do NOT
# substitute a replacement number (MR-13). Record: exchange/CORRECTION-2026-08-14-carrier-byte-gate-struck.md
# This hook fires post-compact, which is exactly where a session is most likely to be carrying a
# remembered copy of the struck gate -- so it says so out loud rather than going silent.
M="${M}exchange/CARRIER.md ${CARRIER_B} B (size only -- there is NO byte gate; the 11901 gate was falsified and struck 2026-08-14, do not reinstate it or any replacement number) | "
M="${M}exchange/WAKE.md $(esc "$WAKE_LINE") | "
M="${M}${RECEIPTS} PreCompact receipts on disk. "
M="${M}BEFORE PLANNING, OPEN these -- naming a file is not reading it: "
M="${M}(1) exchange/CARRIER.md  (2) exchange/WAKE.md -- if its written: stamp is older than the clock, "
M="${M}the last session stopped without checkpointing and THAT IS THE FIRST FINDING  "
M="${M}(3) peer mail both directions: python scripts/audit/exchange_inbox.py  "
M="${M}(4) the LIVE maps derived from kind: wayfinder:map + status: LIVE under wiki/tracker/ -- resume at the first unclosed ticket  "
M="${M}(5) wiki/tracker/ruling-queue-cfl.md -- a gate is a reserved class, its default executes NOTHING. "
M="${M}Follow CLAUDE.md's own 'Read at session open' section as currently written; do not trust a "
M="${M}remembered copy of that list, including this one. "
M="${M}Summarize each as a pointer, never re-derive its contents. Run /wake for the full pass."

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}' "$M"

exit 0
