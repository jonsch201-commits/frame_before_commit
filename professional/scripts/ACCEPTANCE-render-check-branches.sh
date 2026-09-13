#!/usr/bin/env bash
# ACCEPTANCE-render-check-branches.sh
#
# GRADES: scripts/render-sessions.sh --check, all three of its verdict branches.
# HAND THIS TO A PEER AS A TEST, NOT A METHOD: "do not adopt it, run it."
#
# WHY IT EXISTS. [m 2026-09-01 21:2x CDT] --check printed
#   "RENDER-CHECK: FAIL -- raw/transcripts/claude-code holds no .md at all"
# while that directory held 76 .md files. Cause: newest_mtime() had been deleted from
# above the --check block on the belief that a second definition further down "shadowed"
# it. A bash function definition takes effect when EXECUTION reaches it, and --check
# exits before the lower definition is ever reached -- so the deletion removed --check's
# ONLY instrument. The undefined call returned EMPTY, `command not found` went to stderr
# (which the postcompact pipeline does not print), and the caller read empty as a
# measured zero.
#
# THE CLASS, stated so it is checkable elsewhere: AN INSTRUMENT THAT DID NOT EXIST WAS
# REPORTED AS AN INSTRUMENT THAT RAN AND FOUND NOTHING. Absence-of-measurement rendered
# as measurement-of-absence. A repair alone does not prevent the class returning; only a
# committed positive control does, which is what the UNKNOWN case below is.
#
# THE THREE CONTROLS
#   A  empty output dir            -> FAIL,    exit 1   (a real zero IS a failure)
#   B  1 .md, instrument stubbed   -> UNKNOWN, exit 2   (the regression case; never a pass)
#   C  live trunk output dir       -> PASS,    exit 0   (only if md is newer than the stamp)
#
# Control C is the only one whose verdict depends on trunk state. If the trunk genuinely
# has not rendered since its last compact, C is EXPECTED to fail and this script says so
# rather than calling it a defect of --check.
#
# Usage:  bash scripts/ACCEPTANCE-render-check-branches.sh
# Exit:   0 all graded branches behaved; 1 at least one did not.

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1
TARGET="scripts/render-sessions.sh"
STAMPS_ABS="$ROOT/${PRO_STAMPS:-exchange/precompact-receipts.log}"

fails=0
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

grade() {  # name expected_exit expected_substring actual_exit actual_output
  local name="$1" xe="$2" xs="$3" ae="$4" ao="$5"
  if [ "$ae" = "$xe" ] && printf '%s' "$ao" | grep -qF "$xs"; then
    echo "PASS [$name] exit=$ae and output contains: $xs"
  else
    echo "FAIL [$name] expected exit=$xe containing \"$xs\"; got exit=$ae: $ao"
    fails=$((fails + 1))
  fi
}

[ -f "$TARGET" ] || { echo "UNKNOWN -- $TARGET not found; nothing was graded."; exit 1; }
[ -f "$STAMPS_ABS" ] || { echo "UNKNOWN -- no stamps file at $STAMPS_ABS; --check cannot reach a verdict, so nothing was graded."; exit 1; }

# ---- A: a genuinely empty output directory must FAIL -----------------------
mkdir -p "$tmp/empty"
out_a="$(PRO_RENDER_OUT="$tmp/empty" bash "$TARGET" --check 2>&1)"; ea=$?
grade "A empty-dir-is-FAIL" 1 "holds no .md at all (0 files" "$ea" "$out_a"

# ---- B: THE REGRESSION. A blind instrument over a non-empty dir must be ----
#         UNKNOWN, never FAIL and never PASS. Stubbing newest_mtime to return
#         nothing reproduces exactly what an undefined function returned.
mkdir -p "$tmp/full"; : > "$tmp/full/fixture.md"
sed 's|^newest_mtime() { ls -t.*|newest_mtime() { :; }|' "$TARGET" > "$tmp/blind.sh"
if ! grep -q 'newest_mtime() { :; }' "$tmp/blind.sh"; then
  echo "FAIL [B stub-did-not-apply] the fixture could not stub newest_mtime; branch B was NOT graded, which is UNKNOWN, not a pass."
  fails=$((fails + 1))
else
  # the copy cd's to ITS OWN parent, so the stamps path must be absolute here
  out_b="$(PRO_STAMPS="$STAMPS_ABS" PRO_RENDER_OUT="$tmp/full" bash "$tmp/blind.sh" --check 2>&1)"; eb=$?
  grade "B blind-instrument-is-UNKNOWN" 2 "the INSTRUMENT failed, not the trunk" "$eb" "$out_b"
fi

# ---- C: the live output directory ------------------------------------------
out_c="$(bash "$TARGET" --check 2>&1)"; ec=$?
case "$ec" in
  0) echo "PASS [C live-dir] exit=0: $out_c" ;;
  1) if printf '%s' "$out_c" | grep -qF "holds no .md at all (0 files"; then
       echo "FAIL [C live-dir] --check says the live output dir is EMPTY. If it is not, this is the 2026-09-01 defect returning: $out_c"
       fails=$((fails + 1))
     else
       echo "NOT-A-DEFECT [C live-dir] exit=1 for STALENESS, which is a true verdict about the trunk, not about --check: $out_c"
     fi ;;
  *) echo "FAIL [C live-dir] unexpected exit=$ec: $out_c"; fails=$((fails + 1)) ;;
esac

echo "---"
if [ "$fails" -eq 0 ]; then
  echo "ACCEPTANCE-render-check-branches: PASS (3 branches graded, 0 failing)"
  exit 0
fi
echo "ACCEPTANCE-render-check-branches: FAIL ($fails failing)"
exit 1
