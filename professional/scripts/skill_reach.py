#!/usr/bin/env python3
"""Report which script dependencies named by loaded SKILL.md files DO NOT EXIST here.

WHY THIS EXISTS. Herald measured 2026-08-24 that `sync-universal.sh` copies
`skills/.` to ~/.claude/skills/ and has NEVER copied `scripts/`. A skill body is a
set of paths resolved against the CURRENT trunk's root, and every trunk has a
different root. So the skill loads, lists, and reads correctly -- and the command
it names is absent. Nothing announces this until someone runs it, and Herald's own
sentence is why nobody does: A SEAT THAT TRUSTS ITS OWN SKILL LIST NEVER RUNS IT,
BECAUSE IT BELIEVES THE CAPABILITY IS PRESENT.

Measured independently in Professional the same morning: 7 skills, 17 references,
17 DEAD, 7 of 7 fully broken. Herald measured Personal at 16 dead of the same 17.
The MATCHING reference counts prove the bodies copy faithfully; the DIFFERING dead
counts prove the resolution is local. That pair is the evidence, not either number.

WHY IT REPORTS AND DOES NOT FAIL. The fix for a dead reference is NOT to copy
scripts/ into every trunk -- that manufactures the divergent-duplicate defect this
trunk documented on 2026-08-23 (two copies of one memory pack, the older sitting
where a reader would run it). The fix is that a seat LEARNS ITS CAPABILITY IS
ABSENT BEFORE TRUSTING THE SKILL LIST. That is information, not a stop, and Jon's
standing rule is that rules producing stopping are defective rules.

THE HOLE THIS FOUND, which is bigger than the count: [SECRETARY] CLAUDE-STANDARDS §15 makes the
WWJA battery binding at every barrier in EVERY trunk, and WWJA's step 1 is
`scripts/graphrag/retrieve.py` -- one of the 17 dead here. A standard is binding on
a trunk where its first mechanical step cannot execute, and nothing reports that.
"""
import os
import re
import sys

# TWO ROOTS, NOT ONE. Herald measured 2026-08-24 that its trunk carries BOTH a synced
# ~/.claude/skills/ AND a project-local <repo>/.claude/skills/ holding `dream` and `ears`.
# A gate reading one root would have PASSED that trunk on the night it published "dream does
# not exist anywhere" -- Soul's MEASURED-THE-WRONG-POPULATION. Proven-failable is not enough;
# a gate must also be proven over the right population. This trunk has no project-local
# skills dir [measured 2026-08-24] -- which is exactly why the one-root version looked correct
# here and would have shipped wrong. HERALD'S RULE, ADOPTED: A GATE IS VALIDATED AGAINST THE
# POPULATION THAT HAS THE DEFECT, NEVER THE ONE THAT HAPPENS NOT TO. This trunk cannot
# self-test the two-root case from its own tree -- S5/S6 seed it in a temp dir for that reason.
SKILL_ROOTS = [os.path.expanduser("~/.claude/skills"), ".claude/skills"]
# SELFTEST HOOK, added 2026-09-02. C10 and C11 shipped with NO selftest coverage and lint has
# been printing "C10+C11 UNPROVEN" on every clean run since. An UNPROVEN check is soul's class
# exactly -- a check whose failure has never been shown to differ from its pass. This override
# lets lint.sh point the roots at a directory that does not exist and prove the UNKNOWN branch
# fires. It changes NOTHING in a normal run: absent the variable, SKILL_ROOTS is untouched.
import os as _os
if _os.environ.get("LINT_SKILL_ROOTS"):
    SKILL_ROOTS = [p for p in _os.environ["LINT_SKILL_ROOTS"].split(os.pathsep if hasattr(os,"pathsep") else ";") if p]
PAT = re.compile(r'(scripts/[A-Za-z0-9_./-]+\.(?:py|sh))')


def scan_all(root, skill_roots=None):
    """Scan EVERY skill root. Returns (rows, totals, roots_seen, roots_missing)."""
    roots = skill_roots if skill_roots is not None else         [r if os.path.isabs(r) else os.path.join(root, r) for r in SKILL_ROOTS]
    rows, seen, missing, unread = [], [], [], []
    tot = dead_tot = broken = 0
    for sd in roots:
        r, s = scan(root, sd)
        if s.get("no_skills_dir"):
            missing.append(sd)
            continue
        seen.append(sd)
        unread += s.get("unread") or []
        rows += [(os.path.basename(os.path.dirname(sd + os.sep)) + "/" + n, d, t, p)
                 for (n, d, t, p) in r]
        tot += s["refs"]; dead_tot += s["dead"]; broken += s["broken"]
    return rows, dict(skills=len(rows), refs=tot, dead=dead_tot, broken=broken,
                      unread=unread, no_skills_dir=not seen), seen, missing


def scan(root, skills_dir):
    """Return (rows, totals) for ONE skill root. rows = [(skill, dead, total, [dead paths])]."""
    rows = []
    unread = []
    tot = dead_tot = broken = 0
    if not os.path.isdir(skills_dir):
        return rows, dict(skills=0, refs=0, dead=0, broken=0, unread=[], no_skills_dir=True)
    for d in sorted(os.listdir(skills_dir)):
        f = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isfile(f):
            continue
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                refs = sorted(set(PAT.findall(fh.read())))
        except OSError:
            # UNREADABLE IS NOT ABSENT. This branch said `continue` until 2026-08-24,
            # so a SKILL.md that could not be READ was dropped from the scan and the
            # tool reported its dead-reference count as if the scan were complete.
            # Measured that day during a Google Drive content outage: every read on the
            # volume failed while directory listings stayed perfect, so this scanner
            # would have walked every skill, read none, and printed a clean 0 DEAD.
            # CFL found the identical `except OSError: continue` in two of its own
            # checks the same hour, one of which certified a boot surface CLEAN.
            # THE TEST, CFL's, adopted: does the failure path produce DIFFERENT OUTPUT
            # than the success path? And the reason this shape is worse than `|| true`:
            # `|| true` swallows an exit code and produces SILENCE, which eventually
            # gets investigated; this swallows a read failure into a category that
            # ALREADY HAS A LEGITIMATE POPULATION, producing a plausible wrong number
            # that blends into a known backlog. A number of the expected shape does not
            # get investigated.
            unread.append(os.path.join(os.path.basename(skills_dir), d))
            continue
        if not refs:
            continue
        dead = [r for r in refs if not os.path.exists(os.path.join(root, r))]
        tot += len(refs)
        dead_tot += len(dead)
        if dead and len(dead) == len(refs):
            broken += 1
        if dead:
            rows.append((d, len(dead), len(refs), dead))
    return rows, dict(skills=len(rows), refs=tot, dead=dead_tot, broken=broken,
                      unread=unread, no_skills_dir=False)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if mode == "--selftest":
        import tempfile
        import shutil
        rc = 0
        d = tempfile.mkdtemp()
        try:
            sk = os.path.join(d, "skills")
            os.makedirs(os.path.join(sk, "alpha"))
            os.makedirs(os.path.join(sk, "beta"))
            with open(os.path.join(sk, "alpha", "SKILL.md"), "w", encoding="utf-8") as fh:
                fh.write("run `scripts/present.py` to do the thing\n")
            with open(os.path.join(sk, "beta", "SKILL.md"), "w", encoding="utf-8") as fh:
                fh.write("run `scripts/absent.py` and also `scripts/present.py`\n")
            tree = os.path.join(d, "tree")
            os.makedirs(os.path.join(tree, "scripts"))
            with open(os.path.join(tree, "scripts", "present.py"), "w", encoding="utf-8") as fh:
                fh.write("#\n")
            # S1: a resolvable reference must NOT be reported
            rows, s = scan(tree, sk)
            if any(r[0] == "alpha" for r in rows):
                print("SELFTEST BROKEN: S1 a RESOLVABLE reference was reported dead"); rc = 3
            # S2: an unresolvable one must be caught, and partial != fully broken
            if not (s["dead"] == 1 and s["refs"] == 3 and s["broken"] == 0):
                print("SELFTEST BROKEN: S2 miscount", s); rc = 3
            # S3: removing the present script makes beta FULLY broken -- proves `broken` can fire
            os.remove(os.path.join(tree, "scripts", "present.py"))
            _r, s2 = scan(tree, sk)
            if not (s2["dead"] == 3 and s2["broken"] == 2):
                print("SELFTEST BROKEN: S3 fully-broken counter did not fire", s2); rc = 3
            # S4: a skills dir that does not exist must not crash and must not pass silently
            _r, s3 = scan(tree, os.path.join(d, "nope"))
            if not s3.get("no_skills_dir"):
                print("SELFTEST BROKEN: S4 missing skills dir not flagged", s3); rc = 3
            # S5: A SECOND SKILL ROOT MUST BE COUNTED. Seeded because a one-root scanner
            # passes this trunk (no project-local dir) and silently mismeasures one that
            # has two -- proven-failable over the WRONG population is still a false green.
            sk2 = os.path.join(d, "skills2")
            os.makedirs(os.path.join(sk2, "gamma"))
            with open(os.path.join(sk2, "gamma", "SKILL.md"), "w", encoding="utf-8") as fh:
                fh.write("run `scripts/only_in_second_root.py`" + chr(10))
            _r5, s5, seen5, miss5 = scan_all(tree, [sk, sk2])
            if not (s5["dead"] == 4 and len(seen5) == 2 and not miss5):
                print("SELFTEST BROKEN: S5 second skill root not counted", s5, seen5); rc = 3
            # S6: one root present, one absent -> scan proceeds and names the absent one
            _r6, s6, seen6, miss6 = scan_all(tree, [sk, os.path.join(d, "nope2")])
            if not (len(seen6) == 1 and len(miss6) == 1 and not s6.get("no_skills_dir")):
                print("SELFTEST BROKEN: S6 partial-root case wrong", s6, seen6, miss6); rc = 3
            # S7: UNREADABLE IS NOT ABSENT. Seeded by patching builtins.open, NOT by
            #     chmod -- CFL's note, adopted: file permissions do not produce a read
            #     failure for the OWNER on Windows, so a chmod-based control cannot fire
            #     on the platform it runs on, and a control that cannot fire is not a
            #     control. This branch is unreachable from a healthy filesystem, which
            #     is exactly why it shipped as `continue` and went unnoticed for a day.
            import builtins
            _real_open = builtins.open

            def _blind(path, *a, **k):
                if str(path).endswith('SKILL.md'):
                    raise OSError(22, 'Invalid request code')
                return _real_open(path, *a, **k)

            builtins.open = _blind
            try:
                _r7, s7 = scan(tree, sk)
            finally:
                builtins.open = _real_open
            if len(s7.get('unread') or []) != 2:
                print('SELFTEST BROKEN: S7 unreadable SKILL.md not counted', s7); rc = 3
            if s7['dead'] or s7['refs']:
                print('SELFTEST BROKEN: S7 counts reported over files it could not read', s7); rc = 3
            _r7b, s7b = scan(tree, sk)
            if s7b.get('unread'):
                print('SELFTEST BROKEN: S7 a READABLE tree was reported unreadable', s7b); rc = 3
        finally:
            shutil.rmtree(d, ignore_errors=True)
        if rc == 0:
            print("SELFTEST: S1 resolvable-not-reported / S2 dead-caught / "
                  "S3 fully-broken-fires / S4 missing-skills-dir / S5 second-skill-root-counted / "
                  "S6 partial-roots / S7 unreadable-is-not-absent -- each proven failable (7/7)")
        return rc

    rows, s, seen, missing = scan_all(root)
    if s.get("no_skills_dir"):
        print("UNKNOWN [skill-reach] NO skill root exists of %r -- cannot assess. "
              "UNKNOWN is not a PASS." % (SKILL_ROOTS,))
        return 0
    print("  roots scanned: %s%s" % (", ".join(seen),
          ("  |  absent (not an error, but it is the population): " + ", ".join(missing))
          if missing else ""))
    if s.get("unread"):
        print("UNKNOWN [skill-reach] %d SKILL.md file(s) COULD NOT BE READ: %s"
              % (len(s["unread"]), ", ".join(sorted(s["unread"])[:5])))
        print("UNKNOWN [skill-reach] their references are UNKNOWN, not absent. The counts below "
              "are a LOWER BOUND. UNKNOWN DOMINATES A PASS.")
    for name, dead, total, paths in rows:
        print("  %-24s %d/%d DEAD  %s" % (name, dead, total, paths[:3]))
    print("SKILL REACHABILITY: %d skill(s) name scripts | %d ref(s) | %d DEAD | %d fully broken"
          % (s["skills"], s["refs"], s["dead"], s["broken"]))
    if s["dead"]:
        print("  A skill whose script is absent still LOADS and still LISTS. The capability is not "
              "here. Do NOT copy scripts/ in -- that makes divergent duplicates; declare and fail loudly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
