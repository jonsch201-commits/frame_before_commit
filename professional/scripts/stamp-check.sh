#!/usr/bin/env bash
# stamp-check.sh — U8 checker. Audits [measured] timestamp claims in a thread/branch/wiki file.
#
#   bash scripts/stamp-check.sh <file> [...]     audit files; exit 0 clean, 1 findings
#   bash scripts/stamp-check.sh --selftest       prove every check failable; exit 0 proven, 3 broken
#
# Checks (each observed in a real defect instance, n=4 across 3 trunks, 08-14/08-15):
#   S1 FUTURE     — a stamp later than the file's mtime. A stamp cannot postdate the write that
#                   carried it; future stamps are composed, not read.
#   S2 MONOTONIC  — stamps within one file go backwards. Append-only channels move forward;
#                   a regression means at least one stamp was not read from a clock.
#   S3 PRECISION  — a "[measured" claim whose stamp has no seconds field. The observed
#                   discriminator in all defect instances: composed stamps are minute-round,
#                   read stamps carry seconds. Minute-round + measured-claim = flag.
#
# A finding is a FLAG, not a verdict — S1/S2 admit innocent causes (file copied, clock changed).
# The checker reports what it saw and how much it read; it never rewrites anything.
set -uo pipefail

STAMP_RE='[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}(:[0-9]{2})? C[DS]T'

audit_file() {
  # Single awk pass with mktime() — no per-line subprocess. One `date -r` per file is the only spawn.
  local f="$1"
  if [ ! -f "$f" ]; then echo "FLAG [S0] $f: not a file"; return 1; fi
  local mtime_epoch; mtime_epoch=$(date -r "$f" +%s)
  # STAMP_SINCE (epoch, optional): grandfather line — stamps older than it are read for monotonic
  # context but never flagged. Frozen history stays frozen; the full audit runs with SINCE unset.
  awk -v FILE="$f" -v MTIME="$mtime_epoch" -v SINCE="${STAMP_SINCE:-0}" '
    BEGIN { scanned=0; findings=0; prev=0 }
    {
      # 2026-08-24: A QUOTED STAMP IS NOT AN ASSERTED STAMP, and S2 could not tell them apart.
      # It fired on a Jon utterance stamped 20:46:26 and cited as PROVENANCE inside a 22:3x entry,
      # so the gate PENALISED CORRECT CITATION -- the one thing this trunk demands most. A line
      # carrying [verbatim quotes another actor clock; it does not stamp this session work.
      # NARROW ON PURPOSE: [verbatim only. [relayed is NOT excluded, because a relayed stamp can
      # still be this seat asserting a time, and a broad exclusion would gut S2.
      if (index($0, "[verbatim") > 0) next
      if (!match($0, /[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}(:[0-9]{2})? C[DS]T/)) next
      ts = substr($0, RSTART, RLENGTH); scanned++
      d = ts; sub(/ C[DS]T$/, "", d)
      has_sec = (d ~ /[0-9]{2}:[0-9]{2}:[0-9]{2}$/)
      spec = d; gsub(/[-:]/, " ", spec); if (!has_sec) spec = spec " 00"
      epoch = mktime(spec)
      if (epoch <= 0) next
      if (epoch >= SINCE) {
        if (epoch > MTIME + 60) { print "FLAG [S1-FUTURE] " FILE ": stamp \x27" ts "\x27 is after file mtime"; findings++ }
        if (prev > 0 && epoch < prev - 60) { print "FLAG [S2-MONOTONIC] " FILE ": stamp \x27" ts "\x27 precedes an earlier stamp in the same file"; findings++ }
        if (index($0, "[measured") > 0 && !has_sec) { print "FLAG [S3-PRECISION] " FILE ": \x27[measured\x27 claim with minute-round stamp \x27" ts "\x27 (no seconds)"; findings++ }
      }
      prev = epoch
    }
    END { print "READ: " FILE " — " scanned " stamps scanned, " findings " flags"; exit (findings > 0 ? 1 : 0) }
  ' "$f"
}

selftest() {
  local d; d=$(mktemp -d) || exit 3
  local rc=0
  # S1: stamp 1 day in the future vs mtime
  printf 'X — %s CDT [measured]\n' "$(date -d '+1 day' '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date '+%Y-%m-%d %H:%M:%S')" > "$d/s1"
  audit_file "$d/s1" >/dev/null && { echo "SELFTEST BROKEN: S1 did not fire"; rc=3; }
  # S2: second stamp earlier than first
  { echo "A — 2026-08-15 09:00:00 CDT [measured]"; echo "B — 2026-08-15 08:00:00 CDT [measured]"; } > "$d/s2"
  touch -d '2026-08-15 10:00:00' "$d/s2" 2>/dev/null
  audit_file "$d/s2" >/dev/null && { echo "SELFTEST BROKEN: S2 did not fire"; rc=3; }
  # S3: measured claim, minute-round
  echo "C — 2026-08-15 08:00 CDT [measured]" > "$d/s3"
  touch -d '2026-08-15 10:00:00' "$d/s3" 2>/dev/null
  audit_file "$d/s3" >/dev/null && { echo "SELFTEST BROKEN: S3 did not fire"; rc=3; }
  # S2-QUOTED: a backwards stamp on a [verbatim line must NOT fire -- it is provenance.
  { echo "A — 2026-08-15 09:00:00 CDT [measured]"; echo "Jon, 2026-08-15 08:00:00 CDT [verbatim, primary x]: quoted"; } > "$d/s2q"
  touch -d '2026-08-15 10:00:00' "$d/s2q" 2>/dev/null
  audit_file "$d/s2q" >/dev/null || { echo "SELFTEST BROKEN: a QUOTED backwards stamp flagged -- the gate punishes correct citation"; rc=3; }
  # ...and the exclusion must not disarm S2: same file WITHOUT [verbatim still fires.
  { echo "A — 2026-08-15 09:00:00 CDT [measured]"; echo "Jon, 2026-08-15 08:00:00 CDT [measured]: not a quote"; } > "$d/s2n"
  touch -d '2026-08-15 10:00:00' "$d/s2n" 2>/dev/null
  audit_file "$d/s2n" >/dev/null && { echo "SELFTEST BROKEN: [verbatim exclusion disarmed S2 for unquoted stamps"; rc=3; }
  # clean file passes
  echo "D — 2026-08-15 08:00:00 CDT [measured]" > "$d/ok"
  touch -d '2026-08-15 10:00:00' "$d/ok" 2>/dev/null
  audit_file "$d/ok" >/dev/null || { echo "SELFTEST BROKEN: clean file flagged"; rc=3; }
  rm -rf "$d"
  [ $rc -eq 0 ] && echo "SELFTEST: S1/S2/S3 each proven failable; [verbatim exclusion proven BOTH ways; clean file passes (6/6)"
  exit $rc
}

[ "${1:-}" = "--selftest" ] && selftest
[ $# -eq 0 ] && { echo "usage: stamp-check.sh <file>... | --selftest"; exit 2; }

overall=0
for f in "$@"; do audit_file "$f" || overall=1; done
exit $overall
