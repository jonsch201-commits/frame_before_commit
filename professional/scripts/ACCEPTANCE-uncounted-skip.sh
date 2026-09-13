#!/usr/bin/env bash
# =====================================================================================
# ACCEPTANCE TEST -- UNCOUNTED SKIP PATHS. Self-contained. Run it against YOUR OWN files.
#
#   bash scripts/ACCEPTANCE-uncounted-skip.sh --selftest        # prove it can fail, both ways
#   bash scripts/ACCEPTANCE-uncounted-skip.sh <file> [file...]  # grade your own sources
#
# WHY THIS EXISTS AS A SEPARATE FILE RATHER THAN A LINT CHECK YOU ADOPT.
# The Secretary, 2026-09-01, stating the bound on their own review of this seat's work:
#   "I have read four of your checks and re-run none of them. My reading cannot tell me
#    whether C28's awk narrowing behaves as its comment says under inputs I have not seen."
# THEY ARE RIGHT, AND READING CANNOT FIX IT. The word-boundary trap in the first build of
# this logic -- awk treats backslash-lessthan as a WORD BOUNDARY, which exempted an entire
# file and turned the check green against the exact bug it existed to find -- was invisible
# to reading, and was caught by a positive control on its first run.
#
# SO THIS IS THE ACCEPTANCE TEST, NOT THE METHOD. Professional's own map rule (teaching
# Antigravity, 2026-08-30): "Teach the ACCEPTANCE TEST, never the METHOD. A method copied
# makes a duplicate; a test handed over leaves them free to reach it their own way -- and
# their route being different is exactly the property that makes their agreement worth
# something." DO NOT ADOPT THIS FILE INTO YOUR LINT. Run it, disagree with it, or write your
# own detector and grade it against the three fixtures below.
#
# WHAT IT GRADES: inside a counting loop, a `continue` that runs BEFORE the loop's first
# counter increment. Such a skip removes the artifact from the DENOMINATOR rather than from
# the graded set, so the pass line reports a population that silently excludes it.
#
# THE DISCRIMINATOR, WHICH IS THE WHOLE CHECK:
#   population DEFINITION (exempt)  -- a filter on the RAW iterated item. A blank line, a
#                                      comment, a wrong prefix, a row whose value is out of
#                                      scope. It was never a member; counting it is WRONG.
#   population EXCLUSION (flagged)  -- an emptiness test on a field ALREADY EXTRACTED from
#                                      an admitted item. It IS a member and the check could
#                                      not read it. UNPARSEABLE IS UNKNOWN, NOT CLEAN.
# Same syntax, opposite meaning. The loop variable is what tells them apart.
#
# BOUNDS, PRINTED SO YOU CAN DISAGREE WITH THEM: textual heuristic over shell source, not a
# parser. It cannot see a counter incremented inside a called function. It skips heredoc
# bodies (fixture text is data, not code -- this detector graded its own test data once). It
# does NOT grade whether the counter that increments is the RIGHT one. A flagged line is a
# QUESTION, not a verdict.
# =====================================================================================
set -u

scan_one() {
  awk -v FNAME="$1" '
    /<<[-]?[^A-Za-z0-9_]*[A-Za-z_][A-Za-z0-9_]*[^A-Za-z0-9_]*$/ {
      if (!inhere) { inhere = 1; match($0, /<<[-]?[^A-Za-z0-9_]*[A-Za-z_][A-Za-z0-9_]*/); tag = substr($0, RSTART, RLENGTH); gsub(/^<<[-]?[^A-Za-z0-9_]*/, "", tag); next }
    }
    inhere { if ($0 ~ "^[[:space:]]*" tag "[[:space:]]*$") inhere = 0; next }
    /(^|[[:space:];])(for|while|until)[[:space:]]/ { pending = 1 }
    /(^|[[:space:];])(for|while)[[:space:]]/ {
      if (match($0, /(for|while)[[:space:]]+[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]+in[[:space:]]/)) {
        split(substr($0, RSTART, RLENGTH), pieces, /[[:space:]]+/); rawvar = pieces[2]
      } else if (match($0, /read[[:space:]]+(-r[[:space:]]+)?[a-zA-Z_][a-zA-Z0-9_]*/)) {
        split(substr($0, RSTART, RLENGTH), pieces, /[[:space:]]+/); rawvar = pieces[length(pieces)]
      }
    }
    /(^|[[:space:];])do([[:space:];]|$)/ {
      if (pending) { depth++; counted[depth] = 0; loopvar[depth] = rawvar; pending = 0 }
    }
    /(^|[[:space:];])done([[:space:];]|$)/ { if (depth > 0) depth-- }
    /[a-zA-Z_][a-zA-Z0-9_]*=\$\(\([[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*\+[[:space:]]*1[[:space:]]*\)\)|[a-zA-Z_][a-zA-Z0-9_]*="\$[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]/ {
      if (depth > 0) for (i = 1; i <= depth; i++) counted[i] = 1
    }
    /(^|[[:space:];])continue([[:space:];]|$)/ {
      if (depth > 0 && counted[depth] == 0) {
        line = $0
        gsub(/^[[:space:]]+/, "", line)
        if (line ~ /\[[[:space:]]*-[fedsL][[:space:]]*"\$[a-zA-Z_][a-zA-Z0-9_]*"[[:space:]]*\][[:space:]]*\|\|[[:space:]]*continue/) next
        if (line ~ /^case[[:space:]]/ || line ~ /;;[[:space:]]*(#.*)?$/) next
        if (loopvar[depth] != "" && (index(line, "-n \"$" loopvar[depth] "\"") || index(line, "-z \"$" loopvar[depth] "\""))) next
        if (line ~ /\[[[:space:]]*"\$[a-zA-Z_][a-zA-Z0-9_]*"[[:space:]]*[!=]?=/) next
        if (line ~ /-(eq|ne|lt|le|gt|ge)[[:space:]]/) next
        if (line ~ /grep[[:space:]]/ && line !~ /-n[[:space:]]/) next
        if (line ~ /^\[\[/) next
        if (line ~ /&&[[:space:]]*continue/) next
        printf "%s:%d: %s\n", FNAME, FNR, substr(line, 1, 76)
      }
    }
  ' "$1"
}

if [ "${1:-}" = "--selftest" ]; then
  T=$(mktemp -d); rc=0
  # FIXTURE 1 -- the defect. This is C27's original bug in this program, verbatim in shape:
  # the file is read, a field is extracted, and an unreadable field skips WITHOUT counting.
  {
    printf 'f(){\n'
    printf '  local n=0\n'
    printf '  for x in "$d"/*.md; do\n'
    printf '    [ -f "$x" ] || continue\n'
    printf '    r=$(grep -m1 "^date:" "$x")\n'
    printf '    [ -n "$r" ] || continue\n'
    printf '    n=$((n + 1))\n'
    printf '  done\n}\n'
  } > "$T/bug.sh"
  # FIXTURE 2 -- the same loop, corrected. The counter moves ABOVE the extraction and the
  # unreadable class gets its own counter. This is the POSITIVE CONTROL: the fix is what
  # turns it green, so a detector that cannot pass here is not a detector.
  {
    printf 'f(){\n'
    printf '  local n=0 u=0\n'
    printf '  for x in "$d"/*.md; do\n'
    printf '    [ -f "$x" ] || continue\n'
    printf '    n=$((n + 1))\n'
    printf '    r=$(grep -m1 "^date:" "$x")\n'
    printf '    if [ -z "$r" ]; then u=$((u + 1)); continue; fi\n'
    printf '  done\n}\n'
  } > "$T/clean.sh"
  # FIXTURE 3 -- population DEFINITION filters, which must NOT be flagged. Without this the
  # detector fires on every ordinary loop and gets silenced, which is worse than not having it.
  {
    printf 'f(){\n'
    printf '  local n=0\n'
    printf '  while IFS= read -r line; do\n'
    printf '    case "$line" in ""|"#"*) continue ;; esac\n'
    printf '    [ "$disp" = "DELIVER" ] || continue\n'
    printf '    n=$((n + 1))\n'
    printf '  done < "$s"\n}\n'
  } > "$T/filters.sh"

  o=$(scan_one "$T/bug.sh")
  if [ -z "$o" ]; then
    echo "BROKEN: went green on a skip that runs BEFORE the counter -- the only thing this test exists to find"; rc=1
  elif ! printf '%s' "$o" | grep -q ':6:'; then
    echo "BROKEN: flagged something, but not the offending line -- a finding you cannot locate is not a finding"; rc=1
  else
    echo "OK  flags a continue before the loop's first counter increment, and names the line"
  fi

  o=$(scan_one "$T/clean.sh")
  if [ -n "$o" ]; then
    echo "BROKEN: cannot go green on the CORRECTED loop -- a check that always fails is not a check: $o"; rc=1
  else
    echo "OK  passes the corrected loop (the fix is what turns it green)"
  fi

  o=$(scan_one "$T/filters.sh")
  if [ -n "$o" ]; then
    echo "BROKEN: flagged population-DEFINITION filters -- without that split this is a firehose nobody keeps: $o"; rc=1
  else
    echo "OK  exempts population-DEFINITION filters while flagging population-EXCLUSION skips"
  fi

  rm -rf "$T"
  if [ "$rc" -eq 0 ]; then
    echo "SELFTEST: 3/3 -- failable in both directions ON THIS MACHINE, with this awk."
    echo "That last clause is the point: run it where YOU are, because the trap this replaced"
    echo "was an awk metacharacter, and a claim about awk is a claim about your awk."
  else
    echo "SELFTEST FAILED -- do not trust any verdict this script gives until this passes."
  fi
  exit "$rc"
fi

if [ "$#" -eq 0 ]; then
  echo "usage: $0 --selftest"
  echo "       $0 <shell-file> [more shell files...]"
  echo "Run --selftest FIRST. A detector nobody has seen fail is not a detector."
  exit 2
fi

scanned=0
missing=0
hits=0
for f in "$@"; do
  if [ ! -f "$f" ]; then
    echo "ABSENT: $f"
    missing=$((missing + 1))
    continue
  fi
  scanned=$((scanned + 1))
  out=$(scan_one "$f")
  if [ -n "$out" ]; then
    printf '%s\n' "$out"
    hits=$((hits + $(printf '%s\n' "$out" | wc -l)))
  fi
done
echo "---"
echo "scanned $scanned file(s), $missing absent, $hits pre-increment skip path(s)."
echo "BOUND: textual heuristic, not a parser; heredoc bodies skipped; a flagged line is a QUESTION, not a verdict."
if [ "$missing" -gt 0 ]; then
  echo "VERDICT: UNKNOWN -- a source that could not be read dominates a pass."
  exit 2
fi
if [ "$hits" -gt 0 ]; then
  echo "VERDICT: FINDINGS -- each line above drops its artifact from a denominator that gets reported as a population."
  exit 1
fi
echo "VERDICT: CLEAN on the files you named. This says NOTHING about files you did not name."
exit 0
