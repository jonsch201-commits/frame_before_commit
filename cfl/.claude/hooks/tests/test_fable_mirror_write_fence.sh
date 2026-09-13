#!/bin/bash
# test_fable_mirror_write_fence.sh — self-test for the WIRED fable-mirror write fence.
#
# Run from anywhere:  bash .claude/hooks/tests/test_fable_mirror_write_fence.sh
# Exit 0 = every case behaved as specified. Exit 1 = at least one did not.
#
# Scope note (2026-08-06): this suite tests ONLY the fence that is actually wired in
# .claude/settings.json — the path fence (fable-mirror may Write only under
# wiki/intake-triage/) and the wrapper's fail-closed posture. A content/publication screen was
# prototyped the same day and is PARKED UNWIRED at
# .claude/hooks/parked/fable-mirror-publication-screen.UNWIRED.py by Jon's ruling, not by
# oversight; see the header of that file. It is deliberately not exercised here.
#
# Every case names its own EXPECTED exit code, so the suite contains real NEGATIVE CONTROLS —
# cases that must be BLOCKED (rc=2). A fence never observed blocking is a claimed check, not a
# check.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
FENCE="$REPO/.claude/hooks/fable-mirror-write-fence.sh"
export CLAUDE_PROJECT_DIR="$REPO"

PY="$(command -v python 2>/dev/null || command -v python3 2>/dev/null || command -v py 2>/dev/null)"
if [ -z "$PY" ]; then echo "FATAL: no python on PATH"; exit 1; fi

pass=0; fail=0

# mkjson <agent_type|-> <tool_name> <file_path>
mkjson() {
  "$PY" - "$@" <<'EOF'
import json, os, sys
agent, tool, path = sys.argv[1:4]
d = {"hook_event_name": "PreToolUse", "tool_name": tool,
     "cwd": os.environ["CLAUDE_PROJECT_DIR"],
     "tool_input": {"file_path": path, "content": "synthetic test payload"}}
if agent != "-":
    d["agent_type"] = agent
    d["agent_id"] = "agent_test"
print(json.dumps(d))
EOF
}

# run <label> <expected_rc> <agent> <tool> <path>
run() {
  label="$1"; want="$2"; shift 2
  out="$(mkjson "$@" | bash "$FENCE" 2>&1)"; rc=$?
  if [ "$rc" = "$want" ]; then
    pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "$label" "$rc"
  else
    fail=$((fail+1)); printf 'FAIL  %-46s rc=%s (want %s)\n     %s\n' "$label" "$rc" "$want" "$out"
  fi
}

echo "== ALLOW — must pass through (rc=0) ========================================"
run "packet inside intake-triage"        0 fable-mirror Write "wiki/intake-triage/pkt.md"
run "packet, absolute path"              0 fable-mirror Write "$REPO/wiki/intake-triage/abs.md"
run "packet, nested subdir"              0 fable-mirror Write "wiki/intake-triage/sub/deep.md"
run "NotebookEdit inside allow-root"     0 fable-mirror NotebookEdit "wiki/intake-triage/n.ipynb"
run "main thread writes anywhere"        0 - Write "wiki/index.md"
run "other agent writes anywhere"        0 wiki-master Write "wiki/index.md"
run "other agent writes outside repo"    0 wiki-master Write "/c/Users/JonSc/.ssh/config"

echo
echo "== BLOCK — NEGATIVE CONTROLS, must be denied (rc=2) ========================"
run "write to wiki/ proper"              2 fable-mirror Write "wiki/concepts/x.md"
run "traversal escape via .."            2 fable-mirror Write "wiki/intake-triage/../../x.md"
run "prefix confusion (-evil suffix)"    2 fable-mirror Write "wiki/intake-triage-evil/x.md"
run "absolute path outside the repo"     2 fable-mirror Write "/c/Users/JonSc/.ssh/id_rsa"
run "write into the Claude Personal tree" 2 fable-mirror Write "/g/My Drive/Claude/Claude Personal/notes.md"
run "Edit outside allow-root"            2 fable-mirror Edit "wiki/log.md"
run "empty target path"                  2 fable-mirror Write ""

echo
echo "== BLOCK — wrapper fail-closed posture (rc=2) =============================="
tmp="$("$PY" -c 'import tempfile;print(tempfile.mkdtemp())')"
cp "$FENCE" "$tmp/fence.sh"

# 1. Evaluator missing entirely: the wrapper must block, not let the write through.
out="$(mkjson fable-mirror Write "wiki/intake-triage/p.md" \
      | CLAUDE_PROJECT_DIR="$tmp" bash "$tmp/fence.sh" 2>&1)"; rc=$?
if [ "$rc" = 2 ]; then pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "evaluator absent -> fail closed" "$rc"
else fail=$((fail+1)); printf 'FAIL  %-46s rc=%s (want 2)\n' "evaluator absent -> fail closed" "$rc"; fi

# 2. ...and must NOT block a different agent in that same broken state (scoping holds even
#    while the fence is degraded).
out="$(mkjson wiki-master Write "wiki/index.md" \
      | CLAUDE_PROJECT_DIR="$tmp" bash "$tmp/fence.sh" 2>&1)"; rc=$?
if [ "$rc" = 0 ]; then pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "evaluator absent, other agent -> allow" "$rc"
else fail=$((fail+1)); printf 'FAIL  %-46s rc=%s (want 0)\n' "evaluator absent, other agent -> allow" "$rc"; fi

# 3. THE DEFECT FIXED 2026-08-06. Evaluator crashes with exit 1. Exit 1 on PreToolUse is a
#    NON-BLOCKING error per CC docs, so the old `exit $?` propagated a crash as an ALLOW.
#    The wrapper must now normalize any non-0/non-2 code to 2.
mkdir -p "$tmp/.claude/hooks"
printf 'import sys\nsys.stdin.read()\nraise SystemExit(1)\n' > "$tmp/.claude/hooks/fable-mirror-write-fence.py"
out="$(mkjson fable-mirror Write "wiki/intake-triage/p.md" \
      | CLAUDE_PROJECT_DIR="$tmp" bash "$tmp/fence.sh" 2>&1)"; rc=$?
if [ "$rc" = 2 ]; then pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "evaluator exits 1 -> normalized to block" "$rc"
else fail=$((fail+1)); printf 'FAIL  %-46s rc=%s (want 2)\n' "evaluator exits 1 -> normalized to block" "$rc"; fi

# 4. Same crash, different agent: must still be an allow, never a repo-wide block.
out="$(mkjson wiki-master Write "wiki/index.md" \
      | CLAUDE_PROJECT_DIR="$tmp" bash "$tmp/fence.sh" 2>&1)"; rc=$?
if [ "$rc" = 0 ]; then pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "evaluator exits 1, other agent -> allow" "$rc"
else fail=$((fail+1)); printf 'FAIL  %-46s rc=%s (want 0)\n' "evaluator exits 1, other agent -> allow" "$rc"; fi

rm -rf "$tmp"

echo
echo "-------------------------------------------------------------------"
echo "pass=$pass fail=$fail"
[ "$fail" -eq 0 ] || exit 1
