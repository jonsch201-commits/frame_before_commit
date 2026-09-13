#!/usr/bin/env bash
# foreign-module-guard.sh -- fails when a TRACKED module in scripts/ has been rewritten
# in the working tree, and names the symbols the rewrite REMOVED.
#
# WHY THIS EXISTS, and it is a rate rather than an incident:
#   2026-09-07  a foreign 22,911 B session_identity.py overwrote this trunk's 4,814 B copy
#               and dropped line(). Four consumers call it. The Stop hook died. Jon found it,
#               pasted the traceback, and asked why his ears had stopped.
#   2026-09-12  a foreign project_dirs.py overwrote the tracked one at 12:40:57 and dropped
#               tree_root(). SEVEN consumers import it by name. Measured dead by firing
#               ledger-stub-writer.py --selftest: ImportError. Professional took the same
#               overwrite on the same filename with a DIFFERENT sha in the same hour.
#
# ⛔ THE CLASS: a courier drop is NEW FILES ONLY. An overwrite of a tracked module is not a
#    delivery, it is a silent downgrade -- and it presents as a healthy delivery, because the
#    file is present, readable, and imports fine until something calls the symbol that left.
#    Nothing in this fleet was watching the DIFFERENCE between the tracked copy and the one
#    on disk, so both times it was found by a human hitting the crash.
#
# ⭐ It reports REMOVED symbols, never "the file changed" -- a legitimate edit by this seat
#    adds and changes; a foreign overwrite of a same-named module DELETES the local API.
#    That asymmetry is what makes this failable without firing on ordinary work.
#
# Exit 0 clean · 3 findings · 4 the positive control could not demonstrate a failure.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 4
SCOPE="scripts"

removed_symbols() {   # $1 = tracked path; prints def/CONST names present in HEAD, absent on disk
  local f="$1"
  comm -23 \
    <(git show "HEAD:$f" 2>/dev/null | grep -oE '^(def [a-zA-Z_][a-zA-Z0-9_]*|[A-Z_]{3,} *=)' | sed 's/ *=//; s/^def //' | sort -u) \
    <(grep -oE '^(def [a-zA-Z_][a-zA-Z0-9_]*|[A-Z_]{3,} *=)' "$f" 2>/dev/null | sed 's/ *=//; s/^def //' | sort -u)
}

# ---- positive control FIRST: a guard that has only ever passed is not evidence -----------
# It runs ENTIRELY on two temp files and NEVER touches git. The first version of this control
# committed a fixture into the repo to simulate the overwrite, which left two junk commits and
# then reported its own fixture as a finding -- a control that contaminates the population it
# is controlling for. Rewritten; the earlier commits are left in history per no-deletion.
symbols_of() { grep -oE '^(def [a-zA-Z_][a-zA-Z0-9_]*|[A-Z_]{3,} *=)' "$1" 2>/dev/null | sed 's/ *=//; s/^def //' | sort -u; }
CTLDIR="$(mktemp -d)"
printf 'def kept():
    pass

def control_symbol_that_will_be_removed():
    pass
' > "$CTLDIR/before.py"
printf 'def kept():
    pass
' > "$CTLDIR/after.py"
CTL_OUT="$(comm -23 <(symbols_of "$CTLDIR/before.py") <(symbols_of "$CTLDIR/after.py"))"
CTL_NEG="$(comm -23 <(symbols_of "$CTLDIR/before.py") <(symbols_of "$CTLDIR/before.py"))"
rm -rf "$CTLDIR"
if ! printf '%s' "$CTL_OUT" | grep -q control_symbol_that_will_be_removed; then
  echo "CONTROL FAILED -- the guard cannot see a removed symbol. Verdict UNKNOWN, not clean."; exit 4
fi
if [ -n "${CTL_NEG// /}" ]; then
  echo "NEGATIVE CONTROL FAILED -- the guard reports a removal where nothing changed."; exit 4
fi
echo "control OK -- a removed symbol is visible, and an unchanged file reports nothing"

# ---- the real check --------------------------------------------------------------------
findings=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  case "$f" in *.py) ;; *) continue ;; esac
  if [ ! -f "$f" ]; then echo "DELETED  $f  tracked but absent on disk -- reported, never repaired here"; continue; fi
  gone="$(removed_symbols "$f" | tr '\n' ' ')"
  if [ -n "${gone// /}" ]; then
    findings=$((findings+1))
    echo "FINDING  $f  rewritten in working tree, REMOVED: $gone"
    echo "         mtime $(stat -c%y "$f" | cut -c1-19)   tracked sha $(git rev-parse "HEAD:$f" | cut -c1-12)"
  fi
done < <(git diff --name-only -- "$SCOPE")

if [ "$findings" -eq 0 ]; then
  echo "clean -- no tracked module in $SCOPE/ has lost a symbol"
  exit 0
fi
echo "findings: $findings"
echo "REMEDY, in this order: copy the on-disk file aside under a qualified name (no deletion),"
echo "git checkout -- the path, clear __pycache__, then FIRE a consumer and read its exit code."
exit 3
