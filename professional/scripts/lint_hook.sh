#!/usr/bin/env bash
# Non-blocking SessionStart wrapper for lint.sh that DISTINGUISHES "did not run" from "passed".
#
# WHY THIS EXISTS. Until 2026-08-24 14:2x the hook was `bash scripts/lint.sh || true`.
# Measured during the Google Drive content outage that morning, from this seat:
#     bash scripts/lint.sh                    -> 126   (the script itself was unreadable)
#     bash -c 'bash scripts/lint.sh || true'  ->   0
# `|| true` converts THE GATE COULD NOT RUN into THE GATE PASSED. It was written so a
# lint failure would not block session start -- a defensible goal -- and it produced a
# check with two outcomes, green and green.
#
# It broke two of this trunk's own rules, both written the same week:
#   1. A GATE THAT CANNOT RUN IS UNKNOWN, AND UNKNOWN DOMINATES A PASS.
#   2. A TEST THAT CAN ONLY RETURN ONE ANSWER IS A RATCHET, NOT A TEST.
# And Herald's rule names why it was invisible: A GATE IS VALIDATED AGAINST THE
# POPULATION THAT HAS THE DEFECT, NEVER THE ONE THAT HAPPENS NOT TO. `|| true` was
# validated against a working filesystem, where it is indistinguishable from correct.
#
# CFL's sharpening, adopted, because it is wider than the idiom:
#     DOES THE FAILURE PATH PRODUCE DIFFERENT OUTPUT THAN THE SUCCESS PATH?
# `|| true` followed by an explicit "did not run" line is fine. `2>/dev/null` with no
# default is just as bad. THE IDIOM IS NOT THE DEFECT; INDISTINGUISHABLE OUTPUT IS.
#
# And why a SessionStart hook is the worst place for it, also CFL's: a green stamp here
# does not merely fail to warn -- it CERTIFIES THE SESSION AS GROUNDED at the exact
# moment the session has no ground, and every later claim inherits the stamp.
#
# STAYS NON-BLOCKING (always exit 0). Jon's standing rule is that rules producing
# stopping are defective rules. This prints the distinction rather than erasing it.
set -u

run_once() {
    bash "$1"
    rc=$?
    if [ "$rc" -eq 0 ]; then
        return 0
    elif [ "$rc" -ge 124 ]; then
        # 124 timeout / 126 cannot execute / 127 not found -- the gate never graded anything.
        echo "UNKNOWN [lint-hook] lint COULD NOT RUN (rc=$rc). Unreadable, missing, or timed out."
        echo "UNKNOWN [lint-hook] UNKNOWN DOMINATES A PASS -- this session is NOT gated. Re-run before trusting any check."
    else
        echo "FAIL [lint-hook] lint RAN and FAILED (rc=$rc). Its findings are above; this hook does not block."
    fi
    return 0
}

if [ "${1:-}" = "--selftest" ]; then
    d=$(mktemp -d) || exit 3
    rc=0
    printf '#!/usr/bin/env bash\nexit 0\n'  > "$d/pass.sh"
    printf '#!/usr/bin/env bash\nexit 1\n'  > "$d/fail.sh"
    # NO chmod-based "unreadable" fixture here. File permissions do not produce a read
    # failure for the OWNER on Windows, so a chmod control cannot fire on the platform it
    # runs on -- and a control that cannot fire is not a control [CFL, 2026-08-24]. S3 uses
    # a path that does not exist, which raises everywhere. An earlier draft of this file
    # created a chmod 000 fixture and then never asserted on it: dead scaffolding that
    # LOOKS like a control is worse than none, because it answers the question "is this
    # case covered?" with a yes.

    # S1: a PASSING lint prints no verdict line -- silence means graded-and-clean
    out=$(run_once "$d/pass.sh" 2>&1)
    case "$out" in *"lint-hook"*) echo "SELFTEST BROKEN: S1 clean run emitted a verdict line"; rc=3;; esac

    # S2: a lint that RAN and FAILED says FAIL, and must NOT say UNKNOWN
    out=$(run_once "$d/fail.sh" 2>&1)
    case "$out" in *"FAIL [lint-hook]"*) ;; *) echo "SELFTEST BROKEN: S2 no FAIL line"; rc=3;; esac
    case "$out" in *"UNKNOWN"*) echo "SELFTEST BROKEN: S2 a real failure was reported as UNKNOWN"; rc=3;; esac

    # S3: THE ONE THE OUTAGE FOUND. A lint that CANNOT RUN says UNKNOWN, never silence.
    #     Seeded, because this trunk's filesystem is readable -- proven-failable over the
    #     WRONG population is still a false green.
    out=$(run_once "$d/absent.sh" 2>&1)
    case "$out" in *"UNKNOWN [lint-hook]"*) ;; *) echo "SELFTEST BROKEN: S3 unrunnable lint did not report UNKNOWN"; rc=3;; esac
    case "$out" in *"FAIL ["*) echo "SELFTEST BROKEN: S3 unrunnable lint reported as a graded FAILURE"; rc=3;; esac

    # S4: the three outcomes must be MUTUALLY DISTINGUISHABLE from output alone --
    #     CFL's test. Identical output for two different states is the whole defect.
    a=$(run_once "$d/pass.sh" 2>&1); b=$(run_once "$d/fail.sh" 2>&1); c=$(run_once "$d/absent.sh" 2>&1)
    if [ "$a" = "$b" ] || [ "$a" = "$c" ] || [ "$b" = "$c" ]; then
        echo "SELFTEST BROKEN: S4 two outcomes produce identical output"; rc=3
    fi

    # S5: the wrapper NEVER blocks, in any of the three states
    for f in pass.sh fail.sh absent.sh; do
        ( run_once "$d/$f" >/dev/null 2>&1 ); [ $? -eq 0 ] || { echo "SELFTEST BROKEN: S5 blocked on $f"; rc=3; }
    done

    rm -rf "$d"
    [ $rc -eq 0 ] && echo "SELFTEST: S1 clean-is-silent / S2 ran-and-failed-says-FAIL / S3 could-not-run-says-UNKNOWN / S4 three outcomes mutually distinguishable / S5 never blocks -- each proven failable (5/5)"
    exit $rc
fi

run_once "${1:-scripts/lint.sh}"
exit 0
