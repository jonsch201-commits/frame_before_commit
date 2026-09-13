#!/usr/bin/env bash
# check-pipe-status.sh -- P-9 AS A CONTROL, NOT A REGISTER ROW.
#
# ⛔ WHY. `$?` after a pipeline is the EXIT STATUS OF THE LAST COMMAND IN THE PIPE, not of the
# command you care about. `cmd 2>&1 | head -1; rc=$?` reports head's success while cmd failed.
#
# THIS TRUNK HAS COMMITTED IT THREE TIMES IN ONE DAY [measured 2026-09-02]:
#   1. `git status --porcelain 2>&1 | head -5`  -> printed git-exit=0 while git exited 128
#   2. six git subcommands all reporting rc=0 while printing "fatal: not a git repository";
#      the seat concluded "diagnostics through this shell are unreliable" FROM ITS OWN BUG
#   3. `bash scripts/awaiting-jon.sh ... | tail -5; echo "exit=$?"` -> printed 0 for a script
#      that does not exist (real exit 127)
#
# ⭐ It was logged as register row P-9 after instance 1 and fired twice more the same day.
# THE SEAT'S OWN PRE-COMPACT ELDER NAMED THE REASON: "a document with a test, not a control."
# A register catches a relapse only if something CONSULTS it, and nothing consulted this one.
#
# FIX: read PIPESTATUS[0], or run the command without a pipe and capture into a variable.
#
# usage: check-pipe-status.sh [--selftest] [paths...]   default: scripts/*.sh
# exit 0 = no offending line   1 = offences found   2 = UNKNOWN (empty population, never a pass)
set -u

scan_one() {  # $1 = file. prints offending "file:line:text"
  awk -v F="$1" '
    /^[[:space:]]*#/ { next }                       # comments are not code
    {
      line=$0
      # strip the shell-string cases that are not a pipeline: || && 2>&1 |& are handled by
      # requiring a bare | that is not part of || and not inside [[ ]]
      if (line !~ /\$\?/) next                       # only lines that READ $?
      probe=line
      gsub(/\|\|/,"",probe)                          # remove || so it is not seen as a pipe
      if (probe !~ /\|/) next                        # no real pipe on this line -> fine
      if (line ~ /PIPESTATUS/) next                  # the correct idiom -> fine
      printf "%s:%d:%s\n", F, NR, line
    }' "$1"
}

if [ "${1:-}" = "--selftest" ]; then
  d=$(mktemp -d) || exit 3; rc=0
  printf 'out=$(git status | head -1)\nrc=$?\n'            > "$d/bad_split.sh"   # NOT caught: $? on its own line
  printf 'out=$(git status | head -1); rc=$?\n'            > "$d/bad_same.sh"    # caught
  printf 'git status | head -1; echo "e=$?"\n'             > "$d/bad_echo.sh"    # caught
  printf 'git status > /tmp/o; rc=$?\n'                    > "$d/good_nopipe.sh" # clean
  printf 'git status | head -1; rc=${PIPESTATUS[0]}\n'     > "$d/good_ps.sh"     # clean
  printf 'a || b; rc=$?\n'                                 > "$d/good_oror.sh"   # clean: || is not a pipe
  printf '# git status | head -1; rc=$?\n'                 > "$d/good_comment.sh"# clean: comment

  for f in bad_same bad_echo; do
    [ -n "$(scan_one "$d/$f.sh")" ] || { echo "SELFTEST BROKEN: $f.sh not caught -- the detector cannot fail"; rc=3; }
  done
  for f in good_nopipe good_ps good_oror good_comment; do
    [ -z "$(scan_one "$d/$f.sh")" ] || { echo "SELFTEST BROKEN: $f.sh flagged -- false positive on a correct idiom"; rc=3; }
  done
  # ⚠️ KNOWN BOUND, asserted so it cannot silently become a claim of completeness:
  [ -z "$(scan_one "$d/bad_split.sh")" ] || { echo "SELFTEST BROKEN: bad_split.sh was caught -- update the stated bound, the detector got better"; rc=3; }
  rm -rf "$d"
  [ $rc -eq 0 ] && echo "SELFTEST: 2 offences caught / 4 correct idioms cleared / 1 KNOWN MISS asserted (\$? on a following line is NOT detected -- single-line scan only). 7/7"
  exit $rc
fi

files=("$@"); [ ${#files[@]} -eq 0 ] && files=(scripts/*.sh)
n=0; hits=0
for f in "${files[@]}"; do
  [ -f "$f" ] || continue
  n=$((n+1)); out=$(scan_one "$f")
  [ -n "$out" ] && { printf '%s\n' "$out"; hits=$((hits+$(printf '%s\n' "$out" | grep -c .))); }
done
echo "PIPE-STATUS: scanned $n file(s), $hits offending line(s). BOUND: single-line scan only -- \$? read on a LATER line is NOT detected."
[ "$n" -eq 0 ] && { echo "UNKNOWN: zero files scanned. A zero population is UNKNOWN, never a pass." >&2; exit 2; }
[ "$hits" -eq 0 ] && exit 0
exit 1
