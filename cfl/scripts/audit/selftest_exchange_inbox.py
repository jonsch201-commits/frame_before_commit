#!/usr/bin/env python3
"""selftest_exchange_inbox.py — external, offline exercise of the N: ROOTS / G: fault-detection
addition to exchange_inbox.py (lane B-3, 2026-09-02).

Everything here runs against a SCRATCH tree under %LOCALAPPDATA%\\Temp\\claude\\ — never against
the real N:\\ or G:\\ trees. Two things are checked:

  1. INBOUND-N correctness: a fake N: root (2 letters + 1 zero-byte file) is scanned via
     `exchange_inbox.py`'s `--roots` override; the output must list exactly 2 non-hollow letters
     and 1 HOLLOW.

  2. The `--fault-sim` invariant ("no `UNREAD n` token for any G:-rooted channel") is exercised
     TWICE against the same local fixture peer:
       (a) the correct build — the invariant holds.
       (b) a DELIBERATELY PLANTED REGRESSION — `exchange_inbox.probe_g` is monkeypatched, in
           process, to ignore the `force_fault` flag and always report OK. Under that regression,
           `--fault-sim` no longer forces the fault branch, the fixture peer scans normally, and
           its `UNREAD n` token appears. The same assertion used in (a), applied to (b)'s output,
           must register a FAILURE — proving this selftest can actually fail, not just always pass.

Exit: 0 if the correct build passes AND the regression is correctly caught. 1 otherwise.
Every check prints PASS/FAIL individually; nothing here rounds UNKNOWN to PASS.
"""
import contextlib
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "exchange_inbox.py")

# Import the module directly (not via subprocess) so the regression branch can monkeypatch
# `probe_g` in process — a subprocess cannot be monkeypatched from here.
_spec = importlib.util.spec_from_file_location("exchange_inbox_under_test", SCRIPT)
eib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eib)

failures = []


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                        (" — " + str(detail)) if detail else ""))
    if not ok:
        failures.append(name)


def w(path, text=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def run_subprocess(argv):
    """Real subprocess call against the actual script — used for the N: ROOTS check, which
    needs no monkeypatching and should be verified against the real entry point (argparse and
    all), not the in-process import."""
    # encoding="utf-8" is load-bearing on this machine: the default console codepage is cp1252
    # and the script's own stdout is reconfigured to utf-8, so a subprocess capture without this
    # raises UnicodeDecodeError on the em-dashes/emoji this file and its output both use.
    proc = subprocess.run([sys.executable, SCRIPT] + argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def run_inprocess(argv):
    """Run eib.main() in process, capturing stdout — required for the probe_g monkeypatch."""
    buf = io.StringIO()
    saved_argv = sys.argv[:]
    sys.argv = ["exchange_inbox.py"] + argv
    try:
        with contextlib.redirect_stdout(buf):
            rc = eib.main()
    finally:
        sys.argv = saved_argv
    return rc, buf.getvalue()


def main():
    tmp = tempfile.mkdtemp(prefix="exchange_inbox_selftest_")

    # ============================================================================================
    # PART 1 — INBOUND-N: 2 letters + 1 hollow (zero-byte) file on a fake N: root.
    # ============================================================================================
    n_roots = os.path.join(tmp, "n-roots")
    gists = os.path.join(n_roots, "claude-gists-private")
    w(os.path.join(gists, "LETTER-2026-09-02-alpha.md"), "---\ndate: 2026-09-02\n---\nalpha body\n")
    w(os.path.join(gists, "RECEIPT-2026-09-02-beta.md"), "---\ndate: 2026-09-02\n---\nbeta body\n")
    w(os.path.join(gists, "TICKET-2026-09-02-hollow.md"), "")  # 0 bytes — must render HOLLOW

    ours_n = os.path.join(tmp, "ours-n")
    os.makedirs(os.path.join(ours_n, "inbound"), exist_ok=True)

    rc_n, out_n = run_subprocess(["--no-g", "--our-exchange", ours_n, "--roots", n_roots])

    n_only_lines = re.findall(r"^\s*N-ONLY\s+claude-gists-private/(\S+)\s", out_n, re.M)
    hollow_lines = re.findall(r"^\s*HOLLOW\s+claude-gists-private/(\S+)\s", out_n, re.M)

    check("INBOUND-N lists exactly 2 non-hollow letters",
          len(n_only_lines) == 2, f"found {n_only_lines}")
    check("INBOUND-N lists exactly 1 HOLLOW file",
          len(hollow_lines) == 1, f"found {hollow_lines}")
    check("the HOLLOW file is TICKET-2026-09-02-hollow.md (never rendered as read)",
          hollow_lines == ["TICKET-2026-09-02-hollow.md"], f"got {hollow_lines}")
    check("subprocess exit 0 on a clean --no-g run", rc_n == 0, f"rc={rc_n}")

    # ============================================================================================
    # PART 2 — the --fault-sim invariant, correct build vs. a planted regression.
    #
    # A single local fixture PEER stands in for "a G:-rooted channel" so this never touches real
    # G:\ or N:\ — the invariant under test ("--fault-sim withholds UNREAD for every declared
    # channel") does not depend on which filesystem the peer's `exchange` path happens to be on.
    # ============================================================================================
    fx_exchange = os.path.join(tmp, "fixturepeer", "exchange")
    w(os.path.join(fx_exchange, "outbox", "fixturepeer-to-cfl-a-2026-01-01.md"),
      "---\ndate: 2026-01-01\n---\nunreferenced\n")
    os.makedirs(os.path.join(fx_exchange, "inbound"), exist_ok=True)

    ours_fx = os.path.join(tmp, "ours-fx")
    os.makedirs(os.path.join(ours_fx, "inbound"), exist_ok=True)

    empty_n_roots = os.path.join(tmp, "empty-n-roots")
    # The gists dir must EXIST (even empty) so N: roots read as "present but empty," not
    # "absent/unreachable" -- scan_n_roots()/n_readable distinguishes those two states on purpose.
    os.makedirs(os.path.join(empty_n_roots, "claude-gists-private"), exist_ok=True)

    fixture_peers = [{"key": "fixturepeer", "exchange": fx_exchange,
                       "name_pat": r"zzz-never", "inbound_pat": r"^fixturepeer-"}]

    argv_fault_sim = ["--fault-sim", "--our-exchange", ours_fx, "--roots", empty_n_roots]

    def no_unread_for_fixturepeer(out):
        return not re.search(r"\[fixturepeer\]\s+UNREAD \d+", out)

    # ---- (a) correct build ----------------------------------------------------------------
    saved_peers = eib.PEERS[:]
    saved_probe_g = eib.probe_g
    rc_a, out_a = None, None
    try:
        eib.PEERS[:] = fixture_peers
        rc_a, out_a = run_inprocess(argv_fault_sim)
    finally:
        eib.PEERS[:] = saved_peers
        eib.probe_g = saved_probe_g

    check("--fault-sim: correct build withholds UNREAD for the fixture channel",
          no_unread_for_fixturepeer(out_a),
          "expected: no UNREAD token" if no_unread_for_fixturepeer(out_a)
          else "found an UNREAD token where none was expected")
    _has_unknown_fault_a = "[fixturepeer] UNKNOWN(fault)" in out_a
    check("--fault-sim: correct build still shows UNKNOWN(fault) for the fixture channel",
          _has_unknown_fault_a,
          "banner present" if _has_unknown_fault_a else "UNKNOWN(fault) banner missing")
    check("--fault-sim: correct build exits 0 (N: roots were reachable, even if empty-scratch)",
          rc_a == 0, f"rc={rc_a}")

    # ---- (b) planted regression: probe_g ignores force_fault, always reports OK -----------
    def broken_probe_g(*_a, **_k):
        return True, "REGRESSION: probe_g ignored --fault-sim and reported OK"

    rc_b, out_b = None, None
    try:
        eib.PEERS[:] = fixture_peers
        eib.probe_g = broken_probe_g
        rc_b, out_b = run_inprocess(argv_fault_sim)
    finally:
        eib.PEERS[:] = saved_peers
        eib.probe_g = saved_probe_g

    invariant_held_under_regression = no_unread_for_fixturepeer(out_b)
    # THE POINT OF THIS SELFTEST: the SAME check, applied to the regression's output, must NOT
    # hold — an UNREAD token for the fixture channel must now be present, because the broken
    # probe_g let PEERS scanning proceed as though nothing were wrong.
    check("PLANTED REGRESSION correctly breaks the invariant (selftest CAN fail, not just pass)",
          not invariant_held_under_regression,
          "the invariant broke as expected under the planted regression" if not invariant_held_under_regression
          else "the regression did not surface — either the monkeypatch did not take, or "
               "--fault-sim no longer depends on probe_g at all")
    _has_unread_b = "[fixturepeer]  UNREAD" in out_b
    check("PLANTED REGRESSION shows the fixture channel scanned normally (UNREAD token present)",
          _has_unread_b, f"out_b tail: {out_b[-400:]}" if not _has_unread_b else "token found")

    total = 9  # derived from the check() calls above -- update this if a check is added/removed
    print()
    print("=== selftest_exchange_inbox.py ===")
    if failures:
        print(f"RESULT: FAIL — {len(failures)}/{total} failure(s): {failures}")
        return 1
    print(f"RESULT: PASS — {total}/{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
