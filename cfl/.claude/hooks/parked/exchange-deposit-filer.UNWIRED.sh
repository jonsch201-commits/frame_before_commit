#!/bin/bash
# exchange-deposit-filer.UNWIRED.sh — PROTOTYPE, NOT WIRED into .claude/settings.json.
#
# What this would be: a PostToolUse hook (matcher: Write) that, after a new
# flat file lands directly in exchange/, exchange/inbound/, or
# exchange/outbound/, files it into its mined bucket via
# `scripts/audit/organize_exchange.py --file-single ... --apply`.
#
# WHY THIS IS SAFE TO WIRE WHEN THE TIME COMES (the feasibility finding):
#   1. It is PostToolUse, not PreToolUse. It runs AFTER the Write has already
#      succeeded. A failure in this hook cannot prevent a deposit from
#      landing — the letter is already on disk before this script starts.
#      This is the deposit-time analogue of "no blocking hook, and no gate
#      on the gates" (wiki/references/struck-gates.md): it can only refile,
#      never refuse.
#   2. It touches exactly ONE file — the one just written — via
#      --file-single, not a full-tree rescan. Cheap, bounded, no stampede.
#   3. It reuses organize_exchange.py's move-and-stub mechanism verbatim:
#      git mv + a redirect stub at the old path. No deletion, ever. Any
#      citation written against the flat path in the same turn still
#      resolves (to the stub, which names the new path).
#   4. It is idempotent by construction (same classify()/is_redirect_stub()
#      checks as bulk --apply) — firing on a file that's already filed, or
#      on a stub itself, is a documented no-op, not a second move.
#   5. If organize_exchange.py errors for any reason (git failure, disk
#      contention, whatever), that is a non-blocking PostToolUse error per
#      the harness contract — the file stays flat and gets picked up by the
#      next scheduled --report/--apply pass instead. Flat-and-unfiled is
#      always the safe failure mode here, never lost-or-blocked.
#
# WHY IT IS NOT WIRED YET:
#   - Jon asked for cross-trunk alignment on the exchange reorganization
#     (Herald opened branches/20260815-exchange-organization.md as the
#     alignment surface) before any live-tree change lands. Wiring a hook
#     that reshapes every future deposit's path is exactly the kind of
#     change that belongs on that alignment surface, not slipped in as a
#     side effect of a report-and-prototype task.
#   - It has only been tested against a scratch git repo (see the deposit
#     note this hook shipped alongside), never against a live Claude Code
#     session's actual Write-tool PostToolUse payload shape. The matcher
#     and the exact JSON field carrying the written file's path need to be
#     confirmed against a real PostToolUse invocation before this is
#     trustworthy in production — see fable-mirror-write-fence.sh for the
#     established pattern (stdin JSON -> Python evaluator) this should copy.
#
# TO ACTIVATE (once aligned + payload-shape-verified): move this out of
# parked/, drop the .UNWIRED. tag, and add a PostToolUse entry to
# .claude/settings.json matching Write, filtering to paths under
# exchange/, exchange/inbound/, exchange/outbound/ (top-level only — do not
# fire on writes into already-organized subdirectories), calling this
# script with the written file's path.

set -u
input="$(cat)"

PY="$(command -v python 2>/dev/null || command -v python3 2>/dev/null || command -v py 2>/dev/null)"
[ -z "$PY" ] && exit 0   # non-blocking: no interpreter, just skip filing this deposit

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../../.." 2>/dev/null && pwd)}"
ORG_PY="$REPO/scripts/audit/organize_exchange.py"
[ -f "$ORG_PY" ] && exit 0 || true  # placeholder; real version parses $input for tool_input.file_path

# Real implementation (once payload shape is confirmed) would extract the
# written file's path from $input (PostToolUse JSON), check it's a flat
# file directly under exchange/, exchange/inbound/, or exchange/outbound/,
# and if so:
#   "$PY" "$ORG_PY" --file-single "<path>" --apply --root "$REPO/exchange"
# then always exit 0 (PostToolUse cannot block; nothing to block here).

exit 0
