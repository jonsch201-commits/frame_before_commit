#!/usr/bin/env bash
# which_model.sh -- WHICH MODEL actually ran this seat, per session, measured from the transcript.
#
# ⛔ WHY THIS EXISTS. Jon, 2026-08-28: "you will wake as fable model, but I think by now you can see
# why main should not always be a fable". Nothing in this trunk could have told a waking seat what
# model it was, what model wrote the note it was reading, or that the answer had ever changed.
#
# ⭐ AND THE DATA WAS NEVER MISSING. Every assistant line in every session JSONL carries
# `"model":"claude-..."`. `[m 2026-08-29]` this trunk's transcripts hold 6,176 opus-5, 3,299
# opus-4-8 and 767 fable-5 lines. THREE MODELS HAVE RUN THIS SEAT AND NO INSTRUMENT READ THE FIELD.
# Derivable and not derived -- the same shape as the courier roster (wiki/concepts/
# a-roster-built-from-correspondents.md) and of measured-against-the-wrong-key.md.
#
# ⛔ THE FIXTURE IS OUR OWN WIKI. wiki/concepts/conformance-professional.md asserts
# "Model | main loop Fable 5" in prose, honestly stamped 2026-08-14. `[m 2026-08-29]` the last SIX
# sessions are 100% opus-5. A perfect [measured] stamp with no mechanism for when it stopped being
# true -- Secretary CLAUDE-STANDARDS §20 -- on the one field Jon has now made load-bearing.
# ✅ So this prints the COMMAND'S answer and never stores a value.
#
# Usage: scripts/which_model.sh              per-session model, newest first
#        scripts/which_model.sh --check      compare the wiki's stored claim to the measurement; exit 1 on drift
#        scripts/which_model.sh --selftest   prove the parser and the drift check can both fail
set -u
cd "$(dirname "$0")/.." || exit 2

# R4 (2026-09-04): key derived by scripts/project_dirs.py (the live session writes under the PRIMARY dir).
PROJ="${MODEL_PROJ_DIR:-$(python "$(dirname "$0")/project_dirs.py" --primary 2>/dev/null)}"
CLAIM_FILE="${MODEL_CLAIM_FILE:-wiki/concepts/conformance-professional.md}"
N="${MODEL_N:-8}"

# dominant model of one transcript, or empty if the file names none
dominant() {
  grep -ohE '"model":"[^"]+"' "$1" 2>/dev/null | sed 's/.*:"//; s/"$//' \
    | grep -v '^<synthetic>$' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}'
}

measure() {
  local f m any=0
  [ -d "$PROJ" ] || { echo "UNKNOWN could not read $PROJ -- a scan that cannot run is UNKNOWN, never clean"; return 2; }
  for f in $(ls -t "$PROJ"/*.jsonl 2>/dev/null | head -"$N"); do
    m="$(dominant "$f")"
    any=1
    printf '%s  %s  %s\n' "$(stat -c%y "$f" 2>/dev/null | cut -c1-16)" "$(basename "$f" | cut -c1-8)" "${m:-NO-MODEL-FIELD}"
  done
  [ "$any" -eq 1 ] || { echo "UNKNOWN zero transcripts under $PROJ -- an empty population is not a clean one"; return 2; }
  return 0
}

# newest session's model = what this seat most recently WAS
newest_model() {
  local f; f=$(ls -t "$PROJ"/*.jsonl 2>/dev/null | head -1); [ -n "$f" ] || return 1
  dominant "$f"
}

check() {
  local newest claim
  newest="$(newest_model)" || { echo "UNKNOWN [model] no transcript to measure -- UNKNOWN dominates a PASS"; return 2; }
  [ -n "$newest" ] || { echo "UNKNOWN [model] newest transcript names no model"; return 2; }
  if [ ! -f "$CLAIM_FILE" ]; then echo "UNKNOWN [model] claim file absent at $CLAIM_FILE"; return 2; fi
  # the stored claim: the Model row of the conformance table, lowercased and despaced for comparison
  claim=$(grep -iE '^\| *Model *\|' "$CLAIM_FILE" | head -1 | tr 'A-Z' 'a-z' | tr -d ' ')
  if [ -z "$claim" ]; then echo "UNKNOWN [model] $CLAIM_FILE states no Model row -- absence is not agreement"; return 2; fi
  # ✅ SECRETARY §20 COMPLIANT STATE: a Model row that PRINTS THE COMMAND stores no value, so it
  # cannot go stale and there is nothing to reconcile. This is the state we WANT the wiki in.
  if printf '%s' "$claim" | grep -q "which_model.sh"; then
    echo "PASS [model] $CLAIM_FILE prints the command instead of storing a value -- nothing to go stale (newest measured: $newest)"
    return 0
  fi
  # normalise: claude-fable-5 -> fable, claude-opus-5 -> opus
  local key; key=$(printf '%s' "$newest" | sed 's/^claude-//; s/-[0-9].*$//')
  if printf '%s' "$claim" | grep -q "$key"; then
    echo "PASS [model] stored claim names '$key'; newest session measured $newest"
    return 0
  fi
  echo "FAIL [model] STORED CLAIM AND MEASUREMENT DISAGREE."
  echo "  $CLAIM_FILE says: $(grep -iE '^\| *Model *\|' "$CLAIM_FILE" | head -1)"
  echo "  newest transcript measured: $newest"
  echo "  ⛔ A file may not assert another artifact's identity in prose. Print the command."
  return 1
}

case "${1:-}" in
  --check) check; exit $? ;;
  --selftest)
    rc=0
    T=$(mktemp -d)
    # control 1: a transcript naming fable is read as fable (parser positive control)
    printf '{"model":"claude-fable-5"}\n{"model":"claude-fable-5"}\n{"model":"claude-opus-5"}\n' > "$T/a.jsonl"
    got=$(MODEL_PROJ_DIR="$T" bash -c 'source /dev/null; :'; dominant "$T/a.jsonl")
    [ "$got" = "claude-fable-5" ] || { echo "SELFTEST BROKEN: parser did not return the dominant model (got '$got')"; rc=3; }
    echo "OK parser returns the dominant model of a transcript"
    # control 2: drift MUST fail
    printf '| Model | main loop Fable 5 |\n' > "$T/claim.md"
    OUT=$(MODEL_PROJ_DIR="$T" MODEL_CLAIM_FILE="$T/claim.md" bash "$0" --check); crc=$?
    printf '{"model":"claude-opus-5"}\n' > "$T/a.jsonl"
    OUT=$(MODEL_PROJ_DIR="$T" MODEL_CLAIM_FILE="$T/claim.md" bash "$0" --check); crc=$?
    [ "$crc" -eq 1 ] || { echo "SELFTEST BROKEN: drift did not fail (rc=$crc)"; rc=3; }
    echo "$OUT" | grep -q "DISAGREE" || { echo "SELFTEST BROKEN: drift failed without naming the disagreement"; rc=3; }
    echo "OK --check FAILS when the stored claim and the measurement disagree"
    # control 3: agreement must PASS -- a check that cannot pass is not a gate
    printf '| Model | main loop Opus 5 |\n' > "$T/claim.md"
    OUT=$(MODEL_PROJ_DIR="$T" MODEL_CLAIM_FILE="$T/claim.md" bash "$0" --check); crc=$?
    [ "$crc" -eq 0 ] || { echo "SELFTEST BROKEN: --check did not pass on agreement (rc=$crc)"; rc=3; }
    echo "OK --check PASSES when they agree (positive control)"
    # control 4: an unreadable project dir is UNKNOWN, never clean
    OUT=$(MODEL_PROJ_DIR="$T/nope" MODEL_CLAIM_FILE="$T/claim.md" bash "$0" --check); crc=$?
    [ "$crc" -eq 2 ] || { echo "SELFTEST BROKEN: unreadable transcript dir did not return UNKNOWN (rc=$crc)"; rc=3; }
    echo "OK an unreadable transcript directory is UNKNOWN, not clean"
    rm -rf "$T"
    [ $rc -eq 0 ] && echo "SELFTEST: 4/4 controls proven"
    exit $rc ;;
  *) measure; exit $? ;;
esac
