#!/usr/bin/env bash
# corpus-sync.sh -- push this trunk's graded roots into ITS OWN slice of the query corpus.
#
# WHY. C23 grades whether the corpus this trunk's retrieval reads still contains this trunk's
# work. It had been failing with a lag measured in DAYS, and the remedy was a hand-run nobody
# had written down -- so the check reported a true defect that nothing could close. That is the
# same shape as step 7 of the postcompact pipeline before `archive-backfill.sh`:
#
#     A MEASUREMENT WITH NO REMEDY WIRED TO IT IS A NUMBER, NOT A CONTROL.
#
# AND THE STAKES ARE THE ONE THIS TRUNK ALREADY PAID FOR. On 2026-09-01 a seat concluded that
# no JSONL->md parser existed and shipped that into WAKE.md. The parser was on disk. What it
# was NOT in was the corpus. A trunk whose own work is missing from the corpus its retrieval
# reads will conclude its own work does not exist -- confidently, and in writing.
#
# ⛔ COPY-ONLY. NEVER DELETES, NEVER MIRRORS DELETIONS. Jon 2026-08-09 (verbatim): "Yeah no
#    deletion." A file that left the working tree stays in the corpus; it is stale, not lost,
#    and C23 grades PRESENCE and SIZE, so an orphan there costs a false green on nothing.
#
# ⛔ SCOPE IS THIS TRUNK'S OWN SLICE AND THE GRADED ROOTS ONLY. It writes under
#    $LINT_CORPUS_MIRROR (default N:/claude-corpus/professional) and touches no sibling's
#    slice. `raw/` is deliberately NOT synced: it is machine-rendered history, it is large, and
#    it is outside C23's graded roots -- syncing it would inflate the corpus without changing
#    the verdict. That exclusion is a choice, printed below, not an oversight.
#
# PII / EGRESS POSTURE, stated before it runs. N: is local disk, inside the C:/G:/D: trust zone
# Jon named 2026-08-19. `git remote -v` is empty by standing Jon gate. Nothing copied here can
# reach a git host or leave the machine.
#
# Usage:  bash scripts/corpus-sync.sh [--dry-run]
# Exit:   0 sync ran (or dry-run); 1 at least one copy failed; 2 UNKNOWN (no mirror / absent).
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2

MIRROR="${LINT_CORPUS_MIRROR:-N:/claude-corpus/professional}"
ROOTS="${LINT_CORPUS_ROOTS:-wiki|exchange|scripts}"
# 2026-09-02: ROOTS holds DIRECTORIES, so every root-level .md sat outside this population --
# WAKE.md, CLAUDE.md, START-HERE.md, RESUME.md among them. The mirror carried a 34-HOUR-OLD
# WAKE.md while this script reported already-fresh=667 on every run: TRUE ABOUT ITS OWN
# POPULATION AND SILENT ABOUT THE FILE THE NEXT SESSION READS FIRST. Declared, never globbed,
# so adding a root doc is a visible edit and not a silent widening.
ROOT_FILES="${LINT_CORPUS_ROOT_FILES:-WAKE.md|CLAUDE.md|START-HERE.md|RESUME.md|RESUME-NEXT.md|POSTCOMPACT-STATUS.md|BRIEFING-2026-08-07.md}"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

if [ ! -d "$MIRROR" ]; then
  echo "CORPUS-SYNC: UNKNOWN -- mirror not found at $MIRROR. A missing destination is UNKNOWN, never a clean sync."
  exit 2
fi

copied=0; fresh=0; failed=0; seen=0
rf_copied=0; rf_fresh=0; rf_failed=0; rf_seen=0
IFS='|' read -r -a root_list <<< "$ROOTS"
for r in "${root_list[@]}"; do
  [ -d "$r" ] || { echo "CORPUS-SYNC: root '$r' absent in the working tree -- skipped, and SAID so."; continue; }
  while IFS= read -r f; do
    seen=$((seen + 1))
    dst="$MIRROR/$f"
    # Fresh iff the mirror copy is at least as new AND EXACTLY as large.
    # 2026-09-02: this read -ge on SIZE, which made a LARGER stale copy permanently fresh. A
    # CRLF-translated copy is always bigger than its LF source, so once written it satisfied both
    # -ge tests forever and was never refreshed again -- C23 measured 617 files pinned that way.
    # BIGGER IS NOT FRESHER. Equality still catches the truncated copy the original comment was
    # written for: a short file fails -eq exactly as it failed -ge, so nothing is given up.
    if [ -f "$dst" ] \
       && [ "$(stat -c %Y "$dst")" -ge "$(stat -c %Y "$f")" ] \
       && [ "$(stat -c %s "$dst")" -eq "$(stat -c %s "$f")" ]; then
      fresh=$((fresh + 1))
      continue
    fi
    if [ "$DRY" -eq 1 ]; then copied=$((copied + 1)); continue; fi
    mkdir -p "$(dirname "$dst")"
    # COUNT THE EFFECT, NEVER THE CALL: a copy counts only once the destination exists.
    if cp -f "$f" "$dst" 2>/dev/null && [ -e "$dst" ]; then
      copied=$((copied + 1))
    else
      failed=$((failed + 1)); echo "CORPUS-SYNC: COPY-FAIL $f"
    fi
  done < <(find "$r" -type f ! -path '*/.git/*' 2>/dev/null)
done

if [ "$seen" -eq 0 ]; then
  echo "CORPUS-SYNC: UNKNOWN -- zero source files across roots [$ROOTS]. A zero population is UNKNOWN, never a pass."
  exit 2
fi

pfx="CORPUS-SYNC"; [ "$DRY" -eq 1 ] && pfx="CORPUS-SYNC(dry-run)"

# --- declared root-level files. Same guard, SEPARATE counters, so neither population can hide
# inside the other's total.
IFS="|" read -r -a rootfile_list <<< "$ROOT_FILES"
for f in "${rootfile_list[@]}"; do
  if [ ! -f "$f" ]; then echo "CORPUS-SYNC: declared root file $f absent in the working tree -- skipped, and SAID so."; continue; fi
  rf_seen=$((rf_seen + 1))
  dst="$MIRROR/$f"
  d_ok=0
  if [ -f "$dst" ]; then
    if [ "$(stat -c %Y "$dst")" -ge "$(stat -c %Y "$f")" ] && [ "$(stat -c %s "$dst")" -eq "$(stat -c %s "$f")" ]; then d_ok=1; fi
  fi
  if [ "$d_ok" -eq 1 ]; then rf_fresh=$((rf_fresh + 1)); continue; fi
  if [ "$DRY" -eq 1 ]; then rf_copied=$((rf_copied + 1)); continue; fi
  mkdir -p "$(dirname "$dst")"
  if cp -f "$f" "$dst" 2>/dev/null && [ -e "$dst" ]; then rf_copied=$((rf_copied + 1));
  else rf_failed=$((rf_failed + 1)); echo "CORPUS-SYNC: COPY-FAIL $f"; fi
done

echo "$pfx: roots=[$ROOTS] seen=$seen copied=$copied already-fresh=$fresh failed=$failed -> $MIRROR"
echo "$pfx: root-files=[$ROOT_FILES] seen=$rf_seen copied=$rf_copied already-fresh=$rf_fresh failed=$rf_failed -- a SEPARATE population; the roots= line says NOTHING about it."
echo "$pfx: copy-only by design -- 0 deletions, and files removed from the working tree REMAIN in the mirror. raw/ is out of scope."
echo "$pfx: this moves bytes into the corpus. It does NOT rebuild any index; nothing here may report improved retrieval until a rebuild has read it."
[ "$failed" -gt 0 ] && exit 1
exit 0
