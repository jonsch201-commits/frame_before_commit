#!/usr/bin/env python3
"""ACCEPTANCE: the PR4 exclusion register is real, and declared-clean files are ROUTED, not trusted.

DO NOT ADOPT THIS INTO YOUR LINT. RUN IT. It is a test handed to peers, not a method.

THE RULE IT MECHANIZES
----------------------
    A DERIVED-SURFACE SCRUB MUST CLASSIFY BODIES, NEVER DECLARATIONS.

Proposed by soul (Claude Personal, session 0f54112c) 2026-09-01 and adopted the same night.
The fixture: a CFL letter whose frontmatter says "delivered ... as a POINTER, not as content
... the names ... are NOT written into the consciousness-framing trunk" -- and whose body
carries two children's full legal names, two exact dates of birth, a baptism date, a parish,
a celebrant and two godparents. It was landed eleven days after the stated delivery and it
still carries the frontmatter that vouches for its own absence.

    A reviewer who triages by reading frontmatter CLEARS that file.

So this check inverts the reflex. A file that DECLARES it holds no PII is not cleared by the
declaration; it is PROMOTED by it, and reported as REQUIRES-BODY-REVIEW. The check never
opens a body and never judges content -- it routes.

WHAT IT GRADES, AND WHAT IT CANNOT
----------------------------------
  A  every path in the register EXISTS in its owning trunk. A register that rots into dead
     paths reads as protection and provides none.
  B  every registered path is matched by the exclusion predicate a publisher would apply.
     (Checking the register against itself is not a test; this checks the PREDICATE.)
  C  files whose frontmatter DECLARES cleanliness are listed as REQUIRES-BODY-REVIEW.

  * It grades PATHS. A file not in the register is UNGRADED, never proven clean.
  * It reads only the first 40 lines of a file, and only to find a declaration. It never
    reports what a body contains -- printing a PII string to prove PII exists is the defect
    it is checking for.
  * A trunk root it cannot read is UNKNOWN and is printed, never counted as zero.
  * ⛔ NOTHING CALLS THIS AT PUBLISH TIME YET, because no PR4 publish step exists. Until one
    does, this is a document with a test, not a control. That bound is printed on every run.

Usage:
    python scripts/ACCEPTANCE-pr4-exclusions.py             # grade the register
    python scripts/ACCEPTANCE-pr4-exclusions.py --selftest  # prove it can fail
Exit: 0 every graded row held; 1 at least one did not; 2 UNKNOWN (register unreadable/empty).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTER = os.path.join(ROOT, "wiki", "tracker", "pr4-publish-exclusions.md")

TRUNKS = {
    "CFL": "G:/My Drive/Claude/Claude Foundational Layer/claude-foundational-layer",
    "Personal": "G:/My Drive/Claude/Claude Personal",
    "Professional": ROOT,
    "Secretary": "G:/My Drive/Claude/Claude Secretary",
    "Antigravity": "G:/My Drive/Claude/Antigravity",
}

# A frontmatter phrase asserting the artifact is safe to publish / carries no detail. These are
# the CLAIMS this check refuses to trust. Matching one PROMOTES a file to body review.
DECLARATION_PATTERNS = [
    r"as a pointer,? not as content",
    r"delivered:?\s*as a pointer",
    r"no pii",
    r"pii[- ]free",
    r"carries none of it",
    r"not written into",
    r"detail stays here",
    r"safe to publish",
    r"redacted",
]
DECL_RE = re.compile("|".join(DECLARATION_PATTERNS), re.I)

ROW_RE = re.compile(r"^\|\s*\*\*(X-\d+)\*\*\s*\|\s*`([^`]+)`\s*\|\s*([A-Za-z]+)\s*\|")


def parse_register(path):
    """-> (rows, error). A row is (id, relpath, trunk)."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        return [], "register unreadable: %s" % e
    rows = []
    for line in text.splitlines():
        m = ROW_RE.match(line.strip())
        if m:
            rows.append((m.group(1), m.group(2), m.group(3)))
    return rows, None


def excluded_by_predicate(relpath, rows):
    """THE PREDICATE A PUBLISHER APPLIES: exact repo-relative path match, separator-normalised.

    Deliberately exact, not a glob. A glob broad enough to be convenient is broad enough to
    exclude a page nobody meant to exclude, and over-exclusion is the violation with no alarm
    on it (Jon 2026-08-11: "don't make key PII info harder to use it's often relevent").
    """
    norm = relpath.replace("\\", "/").strip().lstrip("./")
    return any(norm == r[1].replace("\\", "/").strip().lstrip("./") for r in rows)


def declares_clean(abspath):
    """True iff the file's first 40 lines DECLARE cleanliness. Never opens the body's meaning."""
    try:
        with open(abspath, "r", encoding="utf-8", errors="replace") as fh:
            head = "".join(fh.readline() for _ in range(40))
    except OSError:
        return None                                   # UNKNOWN, never False
    return bool(DECL_RE.search(head))


def main():
    rows, err = parse_register(REGISTER)
    if err:
        print("UNKNOWN -- %s" % err)
        return 2
    if not rows:
        print("UNKNOWN -- the register parsed to ZERO rows. A zero population is UNKNOWN, "
              "never a pass; an empty exclusion list must never read as 'nothing to exclude'.")
        return 2

    fails = 0
    promoted = []
    unknown_roots = []

    print("register: %s" % os.path.relpath(REGISTER, ROOT).replace("\\", "/"))
    print("rows: %d" % len(rows))
    print()

    for rid, rel, trunk in rows:
        base = TRUNKS.get(trunk)
        if base is None:
            print("FAIL [%s] unknown trunk %r -- a row naming a trunk this check cannot resolve "
                  "is not excluded by anything." % (rid, trunk))
            fails += 1
            continue
        if not os.path.isdir(base):
            print("UNKNOWN [%s] trunk root unreadable: %s -- UNKNOWN, never counted as clean." % (rid, base))
            unknown_roots.append(base)
            continue

        full = os.path.join(base, rel.replace("/", os.sep))
        # A: the path is real
        if not os.path.exists(full):
            print("FAIL [%s] registered path does not exist in %s: %s\n"
                  "     A register that rots into dead paths reads as protection and provides none."
                  % (rid, trunk, rel))
            fails += 1
            continue
        # B: the publisher's predicate actually matches it
        if not excluded_by_predicate(rel, rows):
            print("FAIL [%s] the exclusion PREDICATE does not match its own registered path: %s" % (rid, rel))
            fails += 1
            continue
        # C: routing, not trust
        d = declares_clean(full)
        if d is None:
            print("UNKNOWN [%s] %s exists but its head is unreadable -- UNKNOWN." % (rid, rel))
        elif d:
            promoted.append((rid, trunk, rel))
            print("PASS [%s] excluded, and it DECLARES cleanliness in its own frontmatter -> "
                  "REQUIRES-BODY-REVIEW, never CLEAR: %s" % (rid, rel))
        else:
            print("PASS [%s] excluded by path: %s" % (rid, rel))

    print()
    print("declared-clean and therefore PROMOTED to body review: %d" % len(promoted))
    for rid, trunk, rel in promoted:
        print("  REQUIRES-BODY-REVIEW %s [%s] %s" % (rid, trunk, rel))
    if unknown_roots:
        print("UNREADABLE trunk root(s) (UNKNOWN, never zero): %d" % len(unknown_roots))

    print()
    # ASCII ONLY IN OUTPUT. The first draft printed a non-ASCII marker here and CRASHED on a
    # cp1252 console AFTER every row had passed -- exit 1 over a clean grade. One more display
    # decoupled from the thing it describes, in a check written to catch exactly that.
    print("BOUND, printed every run: this grades PATHS, never CONTENT. A file absent from the "
          "register is UNGRADED, not clean. And NOTHING CALLS THIS AT PUBLISH TIME YET -- no PR4 "
          "publish step exists, so the register is a document with a test, not a control.")
    print("---")
    if fails == 0 and not unknown_roots:
        print("ACCEPTANCE-pr4-exclusions: PASS (%d row(s) graded, 0 failing)" % len(rows))
        return 0
    if fails == 0:
        print("ACCEPTANCE-pr4-exclusions: UNKNOWN (%d row(s), 0 failing, %d unreadable root(s)) "
              "-- UNKNOWN is never a pass." % (len(rows), len(unknown_roots)))
        return 2
    print("ACCEPTANCE-pr4-exclusions: FAIL (%d failing of %d)" % (fails, len(rows)))
    return 1


def selftest():
    """Prove every branch can fire, against real temp files."""
    import tempfile
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        clean = os.path.join(d, "clean.md")
        declaring = os.path.join(d, "declaring.md")
        open(clean, "w", encoding="utf-8").write("---\ntitle: ordinary\n---\n\nbody\n")
        open(declaring, "w", encoding="utf-8").write(
            "---\ntitle: t\ndelivered: as a POINTER, not as content. Detail stays here.\n---\n\nbody\n")

        if declares_clean(clean) is not False:
            print("FAIL [decl-negative] an ordinary head must not read as a declaration"); fails += 1
        else:
            print("PASS [decl-negative] ordinary head -> not a declaration")

        if declares_clean(declaring) is not True:
            print("FAIL [decl-positive] the fixture's own wording must be detected"); fails += 1
        else:
            print("PASS [decl-positive] 'as a POINTER, not as content' detected -> body review")

        if declares_clean(os.path.join(d, "nope.md")) is not None:
            print("FAIL [decl-unknown] a missing file must be UNKNOWN, never False"); fails += 1
        else:
            print("PASS [decl-unknown] missing file -> UNKNOWN, never a silent clean")

        rows = [("X-1", "exchange/inbound/a.md", "CFL")]
        if not excluded_by_predicate("exchange/inbound/a.md", rows):
            print("FAIL [pred-hit] exact path must match"); fails += 1
        else:
            print("PASS [pred-hit] exact path matches")
        if excluded_by_predicate("exchange/inbound/a.md.bak", rows):
            print("FAIL [pred-miss] a near-miss path must NOT match -- over-exclusion is the "
                  "violation with no alarm on it"); fails += 1
        else:
            print("PASS [pred-miss] near-miss path does not match")

        empty = os.path.join(d, "empty.md")
        open(empty, "w", encoding="utf-8").write("# no rows here\n")
        r, e = parse_register(empty)
        if r or e:
            print("FAIL [parse-empty] an empty register must parse to zero rows with no error"); fails += 1
        else:
            print("PASS [parse-empty] zero rows -> caller returns UNKNOWN, never a pass")

        real, e2 = parse_register(REGISTER)
        if e2 or not real:
            print("FAIL [parse-real] the live register must parse to at least one row (got %r, %r)" % (len(real), e2))
            fails += 1
        else:
            print("PASS [parse-real] live register parses %d row(s)" % len(real))

    print("---")
    print("SELFTEST: %s (%d failing)" % ("PASS" if fails == 0 else "FAIL", fails))
    return 0 if fails == 0 else 3


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
