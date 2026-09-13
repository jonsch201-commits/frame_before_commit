#!/usr/bin/env python3
"""WW-19 -- a verdict must carry its own provenance, or a reader cannot grade it.

WHY THIS EXISTS, in three instances from one 24-hour window, all in this trunk:

  WS-1  (2026-09-06, CFL N2 C0) -- `staleness()` returned `(False, "")` on the default path,
        which is byte-identical to a clean check. The verdict omitted WHETHER IT WAS COMPUTED.
        No freshness banner could fire for four days while the skill promised one every query.

  WW-15 (2026-09-07, CFL N1 C2) -- the TTL cache was keyed on time and never on the index it
        described, so a STALE verdict outlived the rebuild that answered it. The verdict omitted
        WHAT IT WAS COMPUTED OVER. An alarm its own prescribed remedy cannot clear gets ignored.

  the truncated-prompt consult (2026-09-07) -- a 4,937 B elder prompt passed with shell=True was
        cut at the first newline by cmd.exe; the fork answered fluently, rc=0. The verdict omitted
        WHETHER THE QUESTION ARRIVED.

⭐ THE UNIFIER, and it is the reason this lint checks four roles instead of one: EACH INSTANCE
OMITTED A DIFFERENT FIELD OF THE SAME TUPLE. A lint written by any one of those three authors,
checking only the field that burned them, would have passed the other two. So every role is
checked independently and has its own RED fixture -- a guard must be failable on its own axis
(Secretary, 2026-09-05), or a new role can sit inert forever riding another role's failure.

THE FOUR ROLES a verdict-bearing artifact must be able to speak to:

  state             the verdict itself
  subject_identity  WHAT it was computed over -- the thing that, when it changes, voids the verdict
  computed_at       WHEN
  cost              what it cost to produce, so a later reader can decide whether to re-pay it

⛔ THE RULE THAT MAKES THIS MORE THAN A REQUIRED-KEYS CHECK, and it is the whole point of WS-1:

  ABSENT  -> FAIL.        The reader cannot distinguish "not computed" from "computed and fine".
  NULL    -> PASS.        An explicit null IS the artifact saying "not computed". That is honest
                          and must never be penalised, or the lint teaches authors to invent a
                          value -- which is the exact defect (a guessed pass) it exists to stop.
  VALUE   -> PASS.

"Not computed" must be SAYABLE. A schema that cannot express it forces every producer to lie.

Exit: 0 all clean · 1 findings · 5 selftest failed.
"""

# ⛔ ONE HOME FOR THE GRAPH -- and this shim has to sit BELOW the module docstring.
# [2026-09-13 03:0x] My first version of it landed ABOVE the docstring, which did two things at once:
# it used `sys` before this module's own `import sys` seventy lines down (NameError on every run), and
# it displaced the docstring from being the file's FIRST STATEMENT, so `__doc__` became None and
# argparse died on `__doc__.splitlines()`. Two failures from one careless insertion point, and the
# second only appeared after fixing the first.
# ⭐ Both were found by scripts/audit/lint_shipped_tree.py -- a lint I wrote four hours after breaking
# this file, for a different purpose, and its first real finding was my own damage. That is the whole
# argument for an executability check over a shipped tree: nothing else runs 125 scripts.
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "lib"))
from graphrag_home import DB as _GRAPHRAG_DB  # noqa: E402


import argparse
import copy
import json
import os
import re
import sys

# --------------------------------------------------------------------------- specs
# Each spec maps the four roles onto one artifact's real field names. Add a row when a new
# verdict-bearing artifact appears; the roles never change, only their spelling does.
SPECS = {
    # The freshness cache written beside every graphrag index (retrieve.py::_write_stale_cache).
    # This is WW-19's passing fixture: it is the artifact AFTER WW-15 bound it to the index.
    "freshness-cache": {
        "state": "is_stale",
        "subject_identity": "index_built_utc",
        "computed_at": "checked_utc",
        "cost": "walk_seconds",
    },
    # ⛔ WW-34 (2026-09-07). The barrier's reader-facing verdict: ONE MUTABLE FILE that every
    # later reader and WAKE opens. Markdown, not JSON -- and the roles are what matter, not the
    # encoding, so the same four rows grade it.
    "postcompact-status": {
        "state": "VERDICT",
        "subject_identity": "boundary",
        "computed_at": "checked_utc",
        "cost": "elapsed",
    },
}

ROLES = ("state", "subject_identity", "computed_at", "cost")

# --------------------------------------------------------------------------- applicability
# ⭐ THE SECOND AXIS, AND IT IS WHY THIS FILE GREW: PRESENCE IS NOT APPLICABILITY.
# WW-19 asked whether a verdict CAN say what it was computed over. WW-34 asks the next question:
# does what it was computed over MATCH WHAT YOU ARE ABOUT TO USE IT FOR. A verdict can carry all
# four roles, be perfectly honest, and still be the wrong verdict for your subject -- which is
# exactly what a skipped run leaves behind, because the skip is correct and the file is stale.
#
# [measured 2026-09-07 20:34, the case that produced this] POSTCOMPACT-STATUS.md carried a real
# VERDICT, a real timestamp and a real elapsed for boundary 20260906T215038-46276084 while the
# boundary just crossed was 20260907T202211-a86404c0. Every role a WW-19 lint checks was present.
# Nothing was missing. The file was simply about something else, and said so nowhere a reader
# could check -- so a WW-19-clean artifact was still unreadable as a verdict about today.
#
# ⛔ A MISMATCH IS UNKNOWN, NEVER A PASS AND NEVER A FAIL OF THE PRODUCER. The producer did its
# job; the reader is asking the wrong file. Rendering it as PASS is the WS-1 defect (a skipped
# check indistinguishable from a clean one); rendering it as FAIL blames a correct artifact and
# teaches the next author to overwrite a verdict they do not own.
APPLIES, OTHER_SUBJECT, NO_SUBJECT = "APPLIES", "UNKNOWN-FOR-THIS-SUBJECT", "UNKNOWN-NO-SUBJECT"


def applicability(obj, spec, want):
    """-> (grade, found) for 'is this verdict about `want`?'"""
    field = spec["subject_identity"]
    found = obj.get(field) if isinstance(obj, dict) else None
    if found is None:
        return NO_SUBJECT, None
    return (APPLIES if str(found) == str(want) else OTHER_SUBJECT), found


def parse_status_md(text):
    """POSTCOMPACT-STATUS.md -> dict. The title line carries the timestamp and session; the
    body carries `KEY: value` lines. Deliberately tolerant: a field this cannot find is ABSENT,
    which the four-role check then reports as MISSING -- never invented, never defaulted."""
    obj = {}
    m = re.search(r"^# POSTCOMPACT-STATUS \u2014 (\S+) session (\S+)", text, re.M)
    if m:
        obj["checked_utc"], obj["session"] = m.group(1), m.group(2)
    for line in text.splitlines():
        m = re.match(r"^([A-Za-z_]+): (.+)$", line)
        if m and m.group(1) not in obj:
            obj[m.group(1)] = m.group(2).strip()
    return obj


def lint_verdict(obj, spec):
    """-> list of (role, field, grade) with grade in COMPUTED / NOT-COMPUTED / MISSING.

    Deliberately returns a row for EVERY role, present or not: a lint that only reports problems
    cannot be read as a coverage statement, and a reader of the output has no way to tell a role
    that passed from a role the lint does not check.
    """
    rows = []
    for role in ROLES:
        field = spec[role]
        if not isinstance(obj, dict) or field not in obj:
            rows.append((role, field, "MISSING"))
        elif obj[field] is None:
            rows.append((role, field, "NOT-COMPUTED"))
        else:
            rows.append((role, field, "COMPUTED"))
    return rows


def findings(rows):
    return [r for r in rows if r[2] == "MISSING"]


def read_artifact(path, spec_name):
    """-> (obj, err). JSON or markdown by kind; an unreadable artifact is UNKNOWN, never clean."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as exc:
        return None, f"UNREADABLE ({type(exc).__name__}) -- UNKNOWN, not clean"
    if spec_name == "postcompact-status":
        return parse_status_md(raw), None
    try:
        return json.loads(raw), None
    except ValueError as exc:
        return None, f"UNREADABLE ({type(exc).__name__}) -- UNKNOWN, not clean"


def lint_file(path, spec_name):
    obj, err = read_artifact(path, spec_name)
    if err:
        return None, err
    return lint_verdict(obj, SPECS[spec_name]), None


def selftest() -> int:
    failures = []

    def check(label, got, want):
        ok = got == want
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}: got {got!r} want {want!r}")
        if not ok:
            failures.append(label)

    # GREEN fixture: the REAL shape retrieve.py writes today, copied from a live cache file --
    # not invented, so a change to the writer breaks this test instead of silently diverging.
    GREEN = {
        "checked_utc": 1788812409.0247195,
        "is_stale": False,
        "message": "",
        "walk_seconds": 0.17682379996404052,
        "index_built_utc": "2026-09-07T20:20:04Z",
    }

    print("selftest: WW-19 -- GREEN control (the fixed freshness cache passes all four roles)")
    rows = lint_verdict(GREEN, SPECS["freshness-cache"])
    check("green fixture yields no findings", findings(rows), [])
    check("all four roles report COMPUTED",
          sorted(g for _, _, g in rows), ["COMPUTED"] * 4)

    # One RED per role. This is the ticket's own requirement: the three real defects each dropped
    # a DIFFERENT field, so a lint proven by only one of them proves nothing about the others.
    print("selftest: WW-19 -- one RED fixture PER ROLE (no role may ride another's failure)")
    for role in ROLES:
        field = SPECS["freshness-cache"][role]
        stripped = copy.deepcopy(GREEN)
        del stripped[field]
        rows = lint_verdict(stripped, SPECS["freshness-cache"])
        found = findings(rows)
        check(f"dropping {role!r} ({field}) is caught",
              [r[0] for r in found], [role])
        check(f"dropping {role!r} leaves the other three passing", len(found), 1)

    print("selftest: WW-19 -- NULL is 'not computed' and MUST NOT fail")
    # ⛔ The most important case here. If an explicit null failed, every producer would be pushed
    # to invent a value to get green -- manufacturing exactly the confident non-answer WS-1 was.
    nulled = copy.deepcopy(GREEN)
    nulled["walk_seconds"] = None
    rows = lint_verdict(nulled, SPECS["freshness-cache"])
    check("explicit null yields no findings", findings(rows), [])
    check("explicit null is reported as NOT-COMPUTED, distinctly from COMPUTED",
          [g for r, _, g in rows if r == "cost"], ["NOT-COMPUTED"])

    print("selftest: WW-19 -- a non-dict artifact fails every role rather than crashing")
    rows = lint_verdict("not a dict", SPECS["freshness-cache"])
    check("garbage input reports all four roles MISSING", len(findings(rows)), 4)

    # ---------------------------------------------------------------- WW-34: the second axis
    def render_status(fields):
        """Render the producer's real shape so the fixture breaks when the producer changes."""
        lines = [f"# POSTCOMPACT-STATUS \u2014 {fields['checked_utc']} session {fields['session']}",
                 "", f"VERDICT: {fields['VERDICT']}  (SKIPPED/UNKNOWN is never a PASS)"]
        for k in ("boundary", "elapsed"):
            if k in fields:
                lines.append(f"{k}: {fields[k]}")
        lines += ["", "| step | verdict | note |", "|---|---|---|", "| 0 capture fired | PASS | x |"]
        return "\n".join(lines) + "\n"

    FULL = {"checked_utc": "2026-09-07T20:34:44", "session": "a86404c0",
            "VERDICT": "PASS-WITH-SKIPS", "boundary": "20260907T202211-a86404c0",
            "elapsed": "35.1s"}

    print("selftest: WW-34 -- the status file parses and passes all four roles")
    rows = lint_verdict(parse_status_md(render_status(FULL)), SPECS["postcompact-status"])
    check("patched status yields no findings", findings(rows), [])

    print("selftest: WW-34 -- the file AS IT SHIPPED (no boundary line) is caught")
    # \u26d4 The RED is not invented: this is the byte shape POSTCOMPACT-STATUS.md had for the life
    # of the trunk until this ticket, and it is what a skipped run leaves behind.
    was = {k: v for k, v in FULL.items() if k != "boundary"}
    rows = lint_verdict(parse_status_md(render_status(was)), SPECS["postcompact-status"])
    check("missing boundary line is a MISSING subject_identity",
          [r[0] for r in findings(rows)], ["subject_identity"])

    print("selftest: WW-34 -- applicability: a present, honest verdict about ANOTHER subject")
    obj = parse_status_md(render_status(FULL))
    spec = SPECS["postcompact-status"]
    check("same boundary APPLIES (control -- the check is not a constant no)",
          applicability(obj, spec, "20260907T202211-a86404c0")[0], APPLIES)
    check("a different boundary is UNKNOWN-FOR-THIS-SUBJECT, not PASS and not FAIL",
          applicability(obj, spec, "20260906T215038-46276084")[0], OTHER_SUBJECT)
    check("no subject at all is UNKNOWN-NO-SUBJECT, distinct from a mismatch",
          applicability(parse_status_md(render_status(was)), spec, "anything")[0], NO_SUBJECT)
    check("an APPLIES verdict is NOT reported stale (negative control for the negative arm)",
          applicability(obj, spec, FULL["boundary"])[0] == OTHER_SUBJECT, False)

    print("selftest: WW-34 -- the LIVE status file, graded against the LIVE boundary")
    live_status = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "exchange", "su-close", "POSTCOMPACT-STATUS.md")
    recs = os.path.join(os.path.dirname(live_status), "precompact")
    if os.path.isfile(live_status) and os.path.isdir(recs):
        newest = sorted(f for f in os.listdir(recs) if f.endswith(".md"))
        obj_live, err_live = read_artifact(live_status, "postcompact-status")
        if newest and not err_live:
            grade, found = applicability(obj_live, spec, newest[-1][:-3])
            print(f"  [INFO] live status is about {found!r}; newest boundary is "
                  f"{newest[-1][:-3]!r} -> {grade}")
            check("live status parses to a dict", isinstance(obj_live, dict), True)
    else:
        print(f"  [SKIP] live status not present -- reported, not silently omitted")

    print("selftest: WW-19 -- the live cache, if present, is linted for real (skipped, not omitted)")
    live = str(_GRAPHRAG_DB) + ".staleness_cache.json"
    if os.path.isfile(live):
        rows, err = lint_file(live, "freshness-cache")
        check("live freshness cache carries all four roles", err or findings(rows), [])
    else:
        print(f"  [SKIP] live cache not present at {live!r} -- reported, not silently omitted")

    print(f"\nselftest: {'ALL PASS' if not failures else str(len(failures)) + ' FAILED'}")
    return 0 if not failures else 5


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", help="verdict artifact (JSON) to lint")
    ap.add_argument("--kind", default="freshness-cache", choices=sorted(SPECS))
    ap.add_argument("--for", dest="subject", metavar="SUBJECT",
                    help="the subject you intend to USE this verdict for (WW-34). A verdict "
                         "about anything else renders UNKNOWN-FOR-THIS-SUBJECT, never a pass.")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.path:
        ap.error("give a path, or --selftest")

    rows, err = lint_file(args.path, args.kind)
    if err:
        print(f"{args.path}: {err}")
        return 1
    print(f"{args.path}  [{args.kind}]")
    for role, field, grade in rows:
        mark = "FAIL" if grade == "MISSING" else "ok"
        print(f"  [{mark:4s}] {role:17s} <- {field:18s} {grade}")
    if args.subject:
        obj, _ = read_artifact(args.path, args.kind)
        grade, found = applicability(obj or {}, SPECS[args.kind], args.subject)
        print(f"\n  [{'ok  ' if grade == APPLIES else 'UNKN'}] applies-to        "
              f"asked about {args.subject!r}; verdict is about {found!r} -> {grade}")
        if grade != APPLIES:
            print("\nThis verdict is not about what you asked. It is not a pass and it is not a "
                  "failure of the artifact -- it is UNKNOWN for your subject, and UNKNOWN "
                  "dominates a PASS.")
            return 1

    bad = findings(rows)
    if bad:
        print(f"\n{len(bad)} role(s) MISSING: a reader cannot tell 'not computed' from "
              f"'computed and fine'. An explicit null is the correct way to say 'not computed'.")
        return 1
    print("\nclean: every role is either computed or explicitly declared not-computed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
