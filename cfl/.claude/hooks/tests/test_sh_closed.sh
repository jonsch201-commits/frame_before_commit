#!/bin/bash
# test_sh_closed.sh — self-test for the sh_closed.sh fail-closed bash hook wrapper.
#
# Run from anywhere:  bash .claude/hooks/tests/test_sh_closed.sh
# Exit 0 = every case behaved as specified. Exit 1 = at least one did not.
#
# Scope (H-3b, 2026-09-02): sh_closed.sh exists because H-1c's --degrade harness run found
# CFL's four plain-bash hook entries fail OPEN on a zero-byte script (bash exits 0 on an
# empty file — it only fails closed, exit 126, on an UNREADABLE file). This suite proves the
# wrapper closes that gap for bash the way py_closed.sh already closes it for python: a
# planted 0-byte script, an unreadable path, and a syntax-broken script all produce a
# HOOK-FAULT line, a ledger row, and a non-zero exit (1 default, 2 with --block); a real
# working script's stdout/exit code/args/stdin all pass through untouched.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
WRAPPER="$REPO/.claude/hooks/sh_closed.sh"
export CLAUDE_PROJECT_DIR="$REPO"

pass=0; fail=0

FALLBACK_LEDGER="$REPO/exchange/su-close/HOOK-FAULTS.jsonl"

ledger_has() {
  marker="$1"
  [ -f "$FALLBACK_LEDGER" ] && grep -qF "$marker" "$FALLBACK_LEDGER"
}

tmp="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/shclosed-test-$$")"
mkdir -p "$tmp"

zero="$tmp/zero_hook.sh"
: >"$zero"   # 0-byte

good="$tmp/good_hook.sh"
printf '#!/usr/bin/env bash\necho "sh-closed-selftest-ok"\n' >"$good"

missing="$tmp/does_not_exist.sh"

broken="$tmp/broken_hook.sh"
printf '#!/usr/bin/env bash\nif [ 1 -eq 1 ]; then\n  echo "unterminated if"\n' >"$broken"   # missing fi

echo "== plain (non-blocking) mode, exit 1 on fault =============================="

out="$("$WRAPPER" "$zero" 2>&1 >/dev/null)"; rc=$?
if [ "$rc" -eq 1 ] && printf '%s' "$out" | grep -q '^HOOK-FAULT'; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "0-byte script -> HOOK-FAULT + exit 1" "$rc"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s\n     %s\n' "0-byte script -> HOOK-FAULT + exit 1" "$rc" "$out"
fi

marker="zero_hook.sh"
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

marker2="does_not_exist.sh"
if ledger_has "$marker2"; then
  pass=$((pass+1)); echo "PASS  missing path -> ledger row written"
else
  fail=$((fail+1)); echo "FAIL  missing path -> no ledger row found in $FALLBACK_LEDGER"
fi

echo
echo "== syntax-broken script (bash -n catch) ======================================"

out="$("$WRAPPER" "$broken" 2>&1 >/dev/null)"; rc=$?
if [ "$rc" -eq 1 ] && printf '%s' "$out" | grep -q '^HOOK-FAULT'; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "syntax-broken script -> HOOK-FAULT + exit 1" "$rc"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s\n     %s\n' "syntax-broken script -> HOOK-FAULT + exit 1" "$rc" "$out"
fi

marker3="broken_hook.sh"
if ledger_has "$marker3"; then
  pass=$((pass+1)); echo "PASS  syntax-broken script -> ledger row written"
else
  fail=$((fail+1)); echo "FAIL  syntax-broken script -> no ledger row found in $FALLBACK_LEDGER"
fi

echo
echo "== good script: output and exit code pass through ==========================="

out="$("$WRAPPER" "$good" 2>/dev/null)"; rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "sh-closed-selftest-ok" ]; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s out=%s\n' "good script -> passthrough" "$rc" "$out"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s out=%s\n' "good script -> passthrough" "$rc" "$out"
fi

# argv passthrough
argecho="$tmp/argecho.sh"
printf '#!/usr/bin/env bash\necho "$1,$2"\n' >"$argecho"
out="$("$WRAPPER" "$argecho" foo bar 2>/dev/null)"; rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "foo,bar" ]; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s out=%s\n' "good script -> args passthrough" "$rc" "$out"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s out=%s\n' "good script -> args passthrough" "$rc" "$out"
fi

# stdin passthrough
stdinecho="$tmp/stdinecho.sh"
printf '#!/usr/bin/env bash\nread -r line\necho "$line"\n' >"$stdinecho"
out="$(printf 'piped-payload\n' | "$WRAPPER" "$stdinecho" 2>/dev/null)"; rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "piped-payload" ]; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s out=%s\n' "good script -> stdin passthrough" "$rc" "$out"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s out=%s\n' "good script -> stdin passthrough" "$rc" "$out"
fi

# non-zero exit from the underlying script passes through too (not swallowed to 0 or 1)
badexit="$tmp/badexit.sh"
printf '#!/usr/bin/env bash\nexit 7\n' >"$badexit"
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
if [ "$rc" -eq 0 ] && [ "$out" = "sh-closed-selftest-ok" ]; then
  pass=$((pass+1)); printf 'PASS  %-46s rc=%s\n' "--block + good script -> still passthrough" "$rc"
else
  fail=$((fail+1)); printf 'FAIL  %-46s rc=%s out=%s\n' "--block + good script -> still passthrough" "$rc" "$out"
fi

rm -rf "$tmp" 2>/dev/null

echo
echo "-------------------------------------------------------------------"
echo "pass=$pass fail=$fail"
[ "$fail" -eq 0 ] || exit 1
