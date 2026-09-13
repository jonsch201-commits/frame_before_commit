#!/bin/bash
# test_py_closed.sh — self-test for the py_closed.sh fail-closed python hook wrapper.
#
# Run from anywhere:  bash .claude/hooks/tests/test_py_closed.sh
# Exit 0 = every case behaved as specified. Exit 1 = at least one did not.
#
# Scope (H-3, 2026-09-02): py_closed.sh exists because H-1's harness run found CFL's real
# hook faults share one shape — a python hook whose target script is missing/empty/unreadable,
# silently falling through to exit 0 (FAIL-OPEN-SILENT). This suite proves the wrapper closes
# that shape: a planted 0-byte script and a planted unreadable path both produce a HOOK-FAULT
# line, a ledger row (in at least one of the two destinations), and a non-zero exit — 1 by
# default, 2 with --block. A real, working script's stdout and exit code must pass through
# untouched.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
WRAPPER="$REPO/.claude/hooks/py_closed.sh"
export CLAUDE_PROJECT_DIR="$REPO"

pass=0; fail=0

FALLBACK_LEDGER="$REPO/exchange/su-close/HOOK-FAULTS.jsonl"

# ledger_grew <marker> <before_count> -- true if a NEW line containing marker now exists in
# the fallback ledger (the one write-path this test tree can always reach; the N:\ primary
# ledger may or may not be writable depending on where this clone sits, so it is checked only
# opportunistically below, never as the pass/fail criterion).
ledger_has() {
  marker="$1"
  [ -f "$FALLBACK_LEDGER" ] && grep -qF "$marker" "$FALLBACK_LEDGER"
}

tmp="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/pyclosed-test-$$")"
mkdir -p "$tmp"

zero="$tmp/zero_hook.py"
: >"$zero"   # 0-byte

good="$tmp/good_hook.py"
printf 'print("py-closed-selftest-ok")\n' >"$good"

missing="$tmp/does_not_exist.py"

echo "== plain (non-blocking) mode, exit 1 on fault =============================="

out="$("$WRAPPER" "$zero" 2>&1 >/dev/null)"; rc=$?
if [ "$rc" -eq 1 ] && printf '%s' "$out" | grep -q '^HOOK-FAULT'; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "0-byte script -> HOOK-FAULT + exit 1" "$rc"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s\n     %s\n' "0-byte script -> HOOK-FAULT + exit 1" "$rc" "$out"
fi

marker="zero_hook.py"
if ledger_has "$marker"; then
  pass=$((pass+1)); echo "PASS  0-byte script -> ledger row written"
else
  fail=$((fail+1)); echo "FAIL  0-byte script -> no ledger row found in $FALLBACK_LEDGER"
fi

out="$("$WRAPPER" "$missing" 2>&1 >/dev/null)"; rc=$?
if [ "$rc" -eq 1 ] && printf '%s' "$out" | grep -q '^HOOK-FAULT'; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "missing/unreadable path -> HOOK-FAULT + exit 1" "$rc"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s\n     %s\n' "missing/unreadable path -> HOOK-FAULT + exit 1" "$rc" "$out"
fi

marker2="does_not_exist.py"
if ledger_has "$marker2"; then
  pass=$((pass+1)); echo "PASS  missing path -> ledger row written"
else
  fail=$((fail+1)); echo "FAIL  missing path -> no ledger row found in $FALLBACK_LEDGER"
fi

echo
echo "== good script: output and exit code pass through ==========================="

out="$("$WRAPPER" "$good" 2>/dev/null)"; rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "py-closed-selftest-ok" ]; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s out=%s\n' "good script -> passthrough" "$rc" "$out"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s out=%s\n' "good script -> passthrough" "$rc" "$out"
fi

# argv passthrough
argecho="$tmp/argecho.py"
printf 'import sys\nprint(",".join(sys.argv[1:]))\n' >"$argecho"
out="$("$WRAPPER" "$argecho" foo bar 2>/dev/null)"; rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "foo,bar" ]; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s out=%s\n' "good script -> args passthrough" "$rc" "$out"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s out=%s\n' "good script -> args passthrough" "$rc" "$out"
fi

# stdin passthrough
stdinecho="$tmp/stdinecho.py"
printf 'import sys\nprint(sys.stdin.read().strip())\n' >"$stdinecho"
out="$(printf 'piped-payload' | "$WRAPPER" "$stdinecho" 2>/dev/null)"; rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "piped-payload" ]; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s out=%s\n' "good script -> stdin passthrough" "$rc" "$out"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s out=%s\n' "good script -> stdin passthrough" "$rc" "$out"
fi

# non-zero exit from the underlying script passes through too (not swallowed to 0 or 1)
badexit="$tmp/badexit.py"
printf 'import sys\nsys.exit(7)\n' >"$badexit"
"$WRAPPER" "$badexit" >/dev/null 2>&1; rc=$?
if [ "$rc" -eq 7 ]; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "good script's own non-zero exit passes through" "$rc"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s (want 7)\n' "good script's own non-zero exit passes through" "$rc"
fi

echo
echo "== --block mode: PreToolUse-fence posture (exit 2 on fault) ================="

out="$("$WRAPPER" --block "$zero" 2>&1 >/dev/null)"; rc=$?
if [ "$rc" -eq 2 ] && printf '%s' "$out" | grep -q '^HOOK-FAULT'; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "--block + 0-byte script -> exit 2" "$rc"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s\n     %s\n' "--block + 0-byte script -> exit 2" "$rc" "$out"
fi

out="$("$WRAPPER" --block "$good" 2>/dev/null)"; rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "py-closed-selftest-ok" ]; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "--block + good script -> still passthrough" "$rc"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s out=%s\n' "--block + good script -> still passthrough" "$rc" "$out"
fi

rm -rf "$tmp" 2>/dev/null

echo
echo "-------------------------------------------------------------------"
echo "pass=$pass fail=$fail"
[ "$fail" -eq 0 ] || exit 1
