#!/usr/bin/env bash
# no-cd-compound.sh -- PreToolUse(Bash) guard, 2026-09-03 (PP-2).
#
# WHY: a Bash command of the shape `cd <path> && <cmd> <relative-path>` (or `;`) cannot be resolved by
# Claude Code's permission layer against the Read() deny rules, so it raises a prompt only Jon can answer.
# Four lanes stalled on it on 2026-09-03 (one for two hours). Jon, 17:4x: "i mean, that requires i stay
# at the pc". Briefs and agent-definition fences did not stop it; this check does, in-turn, with the fix.
#
# WHAT: exit 2 (block, reason shown to the model) when the command contains a compound `cd`.
# Everything else exits 0 and prints nothing. It never rewrites, never allows anything new.
#
# SELF-TEST: bash .claude/hooks/no-cd-compound.sh --self-test
set -u

check() {   # $1 = command text; returns 0 = allow, 2 = block
  local cmd="$1"
  # `cd X && ...`, `cd X; ...`, `cd X || ...` anywhere in the command (start, or after ; && | || newline)
  if printf '%s' "$cmd" | grep -Eq '(^|[;&|]|\n)[[:space:]]*cd[[:space:]]+[^;&|[:space:]]+[[:space:]]*(&&|;|\|\|)'; then
    return 2
  fi
  return 0
}

reason() {
  local root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
  printf 'BLOCKED by no-cd-compound (PP-2): a compound `cd <path> && ...` cannot be permission-checked and would stall this lane on a prompt only Jon can answer. Your cwd is already %s. Re-run the same command with ABSOLUTE paths and no cd.\n' "$root"
}

if [ "${1:-}" = "--self-test" ]; then
  pass=0; fail=0
  t() { local want="$1" cmd="$2"; check "$cmd"; local got=$?; if [ "$got" = "$want" ]; then pass=$((pass+1)); echo "  PASS want=$want got=$got : $cmd"; else fail=$((fail+1)); echo "  FAIL want=$want got=$got : $cmd"; fi; }
  t 2 'cd N:/claude-cfl/clone && grep -n foo scripts/audit/x.py'
  t 2 'cd "N:/claude-cfl/clone" && grep -nE "a|b" scripts/audit/route_agent_return.py | head -40'
  t 2 'cd /n/claude-corpus/cfl/raw/transcripts/claude-ai; grep -cF "x" _routing/incoming/chat.md'
  t 2 'echo hi; cd /tmp && ls'
  t 2 $'echo hi\ncd /tmp && ls'
  t 0 'grep -n foo N:/claude-cfl/clone/scripts/audit/x.py'
  t 0 'git -C N:/claude-cfl/clone status --short'
  t 0 'python N:/claude-cfl/clone/scripts/audit/dispatch_gate.py'
  t 0 'echo "the word cd appears && here" | cat'
  t 0 'cd /tmp'            # a bare cd is not the compound shape; the harness handles it
  echo "no-cd-compound SELF-TEST: $pass PASS / $fail FAIL"
  [ "$fail" = 0 ] && exit 0 || exit 1
fi

# Hook mode: read the PreToolUse payload on stdin.
payload="$(cat)"
cmd="$(printf '%s' "$payload" | python -c 'import json,sys
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception:
    print("")' 2>/dev/null)"
[ -z "$cmd" ] && exit 0
check "$cmd" || { reason >&2; exit 2; }
exit 0
