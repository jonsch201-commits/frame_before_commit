#!/usr/bin/env bash
# assert-gate-spoke.sh -- no check clears the publish path unless it FAILS CLOSED on empty output.
#
# WHY. 2026-09-01/02, a Google Drive file-handle leak made every byte-read on G: fail while
# metadata kept succeeding. CPython's launcher, unable to read a script's TEXT, exits 0 with
# ZERO BYTES. Measured that day: all seven of this trunk's Python gates returned exit=0
# bytes=0 -- BYTE-IDENTICAL TO A CLEAN PASS. bash failed closed at 126; python did not.
# Soul (Claude Personal) named the class `an-acceptance-test-that-cannot-fail` and asked that
# nothing clear PR4's publish path unless it fails closed on empty output. Adopted here.
#
# THE RULE, and it is one line: A GATE THAT SAID NOTHING DID NOT PASS. It is UNKNOWN, and
# UNKNOWN IS NEVER A PASS.
#
# usage: assert-gate-spoke.sh SENTINEL_REGEX -- <command...>
#   exit 0  gate exited 0 AND printed a line matching SENTINEL_REGEX      -> PASS
#   exit 1  gate exited non-zero                                         -> FAIL (its own verdict)
#   exit 2  gate exited 0 but printed NOTHING, or printed no sentinel    -> UNKNOWN, NEVER A PASS
#
# The sentinel matters more than the byte count: a gate can emit a banner and still not have
# reached its verdict. Requiring the VERDICT LINE specifically is what makes truncation --
# e.g. a cp1252 UnicodeEncodeError mid-report, also measured that day -- fail rather than pass.

# CONTROLS, RUN 2026-09-02, not assumed:
#   good.py        exit 0, prints "VERDICT: PASS 3/3"      -> PASS    exit 0
#   silent.py      exit 0, ZERO BYTES                      -> UNKNOWN exit 2   <- the day's signature
#   nosentinel.py  exit 0, prints "starting", no verdict   -> UNKNOWN exit 2
#   fails.py       exit 1, prints "VERDICT: FAIL"          -> FAIL    exit 1
#   cp1252trunc.py REAL failure of this machine: dies on U+26D4 mid-report,
#                  exit 1, 10 bytes, no verdict line       -> FAIL    exit 1
#   cp1252trunc.py WITH PYTHONUTF8=1 -- same script, fixed -> PASS    exit 0
#     ^ that last one matters: without it this is a blocker, not a gate.
#
# ⚠️ WHAT COULD NOT BE CONTROLLED HERE, stated rather than glossed: the ORIGINAL fault --
# a script whose text the launcher cannot read -- could not be reproduced after the mount was
# fixed. `chmod 000` does not deny read on this filesystem (verified: the script still ran and
# printed). silent.py reproduces the SIGNATURE (exit 0 / zero bytes) but not the CAUSE. So the
# gate is proven against the signature and not against the original mechanism.
set -u
SENTINEL="${1:?usage: assert-gate-spoke.sh SENTINEL_REGEX -- <command...>}"; shift
[ "${1:-}" = "--" ] && shift
[ $# -gt 0 ] || { echo "UNKNOWN: no command given" >&2; exit 2; }

OUT_F=$(mktemp); ERR_F=$(mktemp)
# NEVER read $? after a pipe. Status is taken from the command itself.
"$@" > "$OUT_F" 2> "$ERR_F"
rc=$?
bytes=$(wc -c < "$OUT_F")
sent=0
grep -qE "$SENTINEL" "$OUT_F" && sent=1

# Print the population every time: verdict, exit code, bytes, sentinel presence.
echo "GATE: cmd=[$*] exit=$rc stdout_bytes=$bytes sentinel=$([ $sent -eq 1 ] && echo present || echo ABSENT)"
[ -s "$ERR_F" ] && { echo "GATE-STDERR:"; sed 's/^/  /' "$ERR_F"; }
cat "$OUT_F"
rm -f "$OUT_F" "$ERR_F"

if [ "$rc" -ne 0 ]; then
  echo "GATE-VERDICT: FAIL -- the gate returned exit $rc" >&2; exit 1
fi
if [ "$bytes" -eq 0 ]; then
  echo "GATE-VERDICT: UNKNOWN -- exit 0 with ZERO BYTES. This is the silent-launcher signature. NEVER A PASS." >&2; exit 2
fi
if [ "$sent" -ne 1 ]; then
  echo "GATE-VERDICT: UNKNOWN -- exit 0 and $bytes bytes, but no line matched the sentinel /$SENTINEL/. Output without a verdict is not a verdict." >&2; exit 2
fi
echo "GATE-VERDICT: PASS -- exit 0 and the sentinel line was printed"
