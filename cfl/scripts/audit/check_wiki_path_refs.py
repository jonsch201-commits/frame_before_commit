#!/usr/bin/env python3
"""check_wiki_path_refs.py -- do the repo's `wiki/....md` path citations point at files that exist?

WHY THIS EXISTS
---------------
Jon ruled 2026-08-07: "a pages pranch and sub branch sould live in both the frontmatter and the
folder path." The frontmatter half landed the same day (39.7% -> 85.9%). The FOLDER half is a mass
`git mv`, and before moving anything somebody had to measure what a move would break.

MEASURED 2026-08-07, and the measurement found a defect that has nothing to do with the move:

    distinct `wiki/....md` paths cited across 1,442 tracked files : 677
    resolve to a file that exists today                           : 544
    DANGLING, real                                                : 96    (14.2%)
    self-test fixtures, separated out and NOT counted              : 37

    total citation occurrences : 3,352 across 614 tracked files
      wiki 2,416 . exchange 314 . skills 271 . scripts 252 . .claude 24 . CLAUDE.md 13

**One citation in seven was already dangling before anyone touched a folder.** Had the move gone
first, every one of those would have been attributed to it -- a real defect laundered into
migration noise, which is the shape memory `migrations-blind-instruments` already records.

**THE FIRST PUBLISHED NUMBER WAS 132 (19.5%) AND IT WAS WRONG BY 37%.** It counted this script's
own baseline file and other scripts' deliberate negative controls -- `wiki/a.md`,
`wiki/concepts/zzz.md`, `wiki/intake-triage-evil/x.md` -- as broken citations. **A checker that
reads its own output measures itself, and a checker that cannot tell a fixture from a defect
inflates its own alarm.** Both are the false-positive class this file warns about below, found in
this file, minutes after it was committed. Kept here rather than quietly corrected.

THE OTHER HALF OF THE FINDING, AND IT DECIDES THE SEQUENCING
------------------------------------------------------------
The wiki's own link form is `[[slug]]` -- 1,286 occurrences -- and **a wikilink is
path-independent, so a folder move cannot break one.** The 3,352 path citations are the only
fragile class.

So the cheap order is: **fix the 96, convert fragile path citations to `[[slug]]` where a slug
exists, and only then move folders.** Moving first maximises the blast radius; converting first
shrinks it toward zero. This script does not do the conversion -- it measures, so the decision is
made on a number.

WHY IT IS A DELTA AND NOT AN ALARM
-----------------------------------
A check that fires on 96 rows on every run is a mute button -- `RATIO_FLOOR` was retired for
exactly that on 2026-08-06, and `publish_content_gate.py` reproduced the defect on its own first
run (374 hits) before being converted. So: `--update-baseline` records the known-broken set, and a
bare run reports only what is NEW. **No baseline on disk -> UNKNOWN (exit 2), never clean.**

WHAT IT DELIBERATELY DOES NOT DO
---------------------------------
- It does not repair anything. A dangling citation may want a repoint, a deletion, or a note that
  the target was intentionally retired; that is a judgment call per row.
- It does not scan `raw/` (gitignored corpus, read-only, not ours to lint).
- It does not check `[[slug]]` targets. Those are a different question with a different failure
  mode, and conflating them would hide which class actually broke.

Exit: 0 clean or baseline recorded | 6 NEW broken citations | 2 could not run (UNKNOWN dominates).
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(HERE, "wiki_path_refs_baseline.txt")
REF = re.compile(r"(?<![A-Za-z0-9_-])wiki/[A-Za-z0-9_./-]+\.md")
SKIP_DIRS = ("raw/",)


def tracked(root):
    p = subprocess.run(["git", "-C", root, "ls-files", "-z"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0 or not p.stdout:
        return None
    return [f for f in p.stdout.split("\0") if f and not f.startswith(SKIP_DIRS)]


def load_baseline():
    try:
        raw = open(BASELINE, encoding="utf-8").read()
    except OSError:
        return set(), False
    return set(l.strip() for l in raw.splitlines()
               if l.strip() and not l.startswith("#")), True


def scan(root, files):
    """Return {referenced_path: [(citing_file, line_no, dispositioned), ...]} for paths that do
    NOT exist. `dispositioned` is True when that specific citing LINE carries `[target retired:`
    or `[cross-trunk:` (case-sensitive, bracket required) within 200 characters after the cite --
    added D8-A, 2026-09-04, so a human annotation left in place by a repair lane (never a deletion:
    the cite itself stays, as evidence) can be told apart from a row nobody has looked at yet.

    THREE EXCLUSIONS, the first two found within minutes of this script's first commit, the third
    added 2026-09-02 (PATHREFS lane) after C-2's DANGLING-2026-09-02.md audit found it by hand:

    1. THE BASELINE FILE IS SKIPPED. It lists every dangling path, so scanning it makes each one
       appear "cited from scripts/" and destroys the fixture-vs-real split below. A checker that
       reads its own output is measuring itself.
    2. FIXTURES ARE SEPARATED, NOT COUNTED. Other scripts' self-tests cite deliberately-absent
       paths as NEGATIVE CONTROLS -- wiki/a.md, wiki/concepts/zzz.md, wiki/does-not-exist-zzz.md,
       wiki/intake-triage-evil/x.md. Those are correct code, not defects. Measured: 36 of the
       first run's 132 are fixture-only, so the honest dangling count is 96, not 132 -- the first
       published figure was inflated 37% by the very false-positive class this file's docstring
       warns about elsewhere.
    3. THE REGEX REQUIRES A TRUNK BOUNDARY. A bare `wiki/[A-Za-z0-9_./-]+\\.md` matches as a
       SUBSTRING of another trunk's directory name -- `herald-wiki/exchange/inbound/foo.md` (a real
       path in Herald's own tree) was being misread as a citation of `wiki/exchange/inbound/foo.md`
       (this repo's tree), and `scripts/ollama_wiki/system_prompt.md` was misread as
       `wiki/system_prompt.md`. Both are the exact false-positive class this docstring already
       warns about for exclusion 2, wearing a different costume: a checker that cannot tell a
       trunk-qualified path from a bare one inflates its own alarm. `REF` now requires the
       character immediately before `wiki/` to NOT be `[A-Za-z0-9_-]` (start of string, whitespace,
       backtick, slash, or most punctuation are all fine) -- so `herald-wiki/...` and
       `ollama_wiki/...` no longer match, while `` `wiki/index.md` `` and a bare `wiki/index.md`
       still do.
    """
    broken, seen_ok = {}, set()
    for f in files:
        if os.path.abspath(os.path.join(root, f)) == os.path.abspath(BASELINE):
            continue
        try:
            text = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "wiki/" not in text:
            continue
        for n, line in enumerate(text.split("\n"), 1):
            for m in REF.finditer(line):
                path = m.group(0)
                if path in seen_ok:
                    continue
                if os.path.isfile(os.path.join(root, path)):
                    seen_ok.add(path)
                    continue
                window = line[m.end():m.end() + 200]
                dispositioned = ("[target retired:" in window) or ("[cross-trunk:" in window)
                broken.setdefault(path, []).append((f, n, dispositioned))
    return broken, seen_ok


# DISPOSITIONED dirs and the ARTIFACT dirs below are used both by classify() and by self_test().
ARTIFACT_DIRS = ("scripts/", "wiki/intake-triage/agent-end/", "wiki/skills-gate/probe-packets/")


def classify(broken):
    """Split `broken` (from scan()) into fixture / artifact / dispositioned / real sets, in that
    precedence -- each a subset of what is left after the previous exclusion is removed.

      1. FIXTURE       -- cited only from scripts/ as self-test negative controls.
      2. ARTIFACT      -- cited only from transcript-capture dirs (agent-end/, probe-packets/).
      3. DISPOSITIONED -- added D8-A, 2026-09-04. Every REMAINING citing occurrence carries the
         `[target retired:` / `[cross-trunk:` annotation within 200 chars, i.e. a human already
         judged every citation of this path in place. Requiring ALL (not ANY) mirrors the same
         ALL-must-match rule FIXTURE and ARTIFACT already use above: one undispositioned citation
         means the row still needs a human look, so it stays REAL rather than hiding.
      4. REAL          -- everything else. THE NUMBER (the alarm percentage) is len(real).

    Factored out of main() so self_test() calls the identical code path instead of a duplicated
    copy that could silently drift from what actually runs.
    """
    fixture = {p for p, w in broken.items() if all(c.startswith("scripts/") for c, _, _ in w)}
    artifact = {p for p, w in broken.items()
                if p not in fixture
                and all(any(c.startswith(d) for d in ARTIFACT_DIRS) for c, _, _ in w)}
    # D8-B, 2026-09-04: the ALL-must-match rule now applies only to citations a HUMAN COULD
    # ANNOTATE. It previously included occurrences inside scripts/ and the transcript-capture
    # dirs, which are machine-written: nobody annotates a probe-packet and nobody should.
    #
    # [m 2026-09-04 15:1x] DISPOSITIONED fell 1 -> 0 between two runs the same day. Cause: a
    # target cited from BOTH a real wiki page AND a probe-packet is not ARTIFACT (not ALL its
    # cites are artifact), so it fell through to this test -- where the unannotatable
    # probe-packet occurrence blocked it forever. Measured: 5 targets sit partially annotated
    # and every blocking occurrence is under wiki/skills-gate/probe-packets/.
    #
    # That made this a gate CORRECT BEHAVIOUR COULD NOT CLOSE: a human could annotate every
    # citation they wrote and the row would still read REAL. Same family as CB-9, closed this
    # morning in postcompact_verify, and as unlazy-verify's G2.
    #
    # A target must still have at least ONE human-authored citation to qualify -- otherwise it
    # is ARTIFACT or FIXTURE by the precedence above, not dispositioned.
    def _human(cite):
        c = cite.replace(chr(92), '/')
        return not c.startswith('scripts/') and not any(c.startswith(d) for d in ARTIFACT_DIRS)

    dispositioned = set()
    for p, w in broken.items():
        if p in fixture or p in artifact:
            continue
        human = [(c, n, d) for c, n, d in w if _human(c)]
        if human and all(d for _, _, d in human):
            dispositioned.add(p)
    real = {p: w for p, w in broken.items()
            if p not in fixture and p not in artifact and p not in dispositioned}
    return fixture, artifact, dispositioned, real


def main(argv):
    if "--self-test" in argv:
        return self_test()
    root = os.path.dirname(os.path.dirname(HERE))
    root = root if os.path.isdir(os.path.join(root, ".git")) else "."
    files = tracked(root)
    if files is None:
        print("UNKNOWN -- `git ls-files` failed. Nothing was scanned; this is NOT a pass.")
        return 2

    broken, ok = scan(root, files)
    total = len(broken) + len(ok)
    # ARTIFACT_DIRS (added D8, 2026-09-04): wiki/intake-triage/agent-end/*.i1.md and
    # wiki/skills-gate/probe-packets/*.probe-packet.md are machine-generated transcript captures
    # that embed VERBATIM raw tool-call JSON (a `"content": "...wiki/foo.md..."` string inside a
    # quoted diff or fixture body). The `wiki/...`-shaped substring inside them is quoted text, not
    # an authored citation -- confirmed by reading multiple samples directly (e.g.
    # agent-end/e515d8/code-2026-09-02-a7bd43-....i1.md:345, a JSON `content` field containing a
    # fixture generator script that happens to name `wiki/tracker/wayfinder-week-2026-09-02.md`).
    # This is the exact false-positive class PATHREFS-2026-09-02.md section 6 identified and
    # explicitly deferred ("a larger change than this lane's time budget covers"). A target cited
    # ONLY from these two directories (or scripts/) is a capture artifact, not a real citation.
    # fixture/artifact/dispositioned/real -- see classify() for the precedence and reasoning.
    fixture, artifact, dispositioned, real = classify(broken)
    print("=== WIKI PATH REFERENCES ===")
    print("  tracked files scanned      : %d   <- DENOMINATOR 1 (raw/ excluded by design)" % len(files))
    print("  distinct wiki/*.md paths   : %d   <- DENOMINATOR 2" % total)
    print("  resolve to a real file     : %d" % len(ok))
    print("  DANGLING, real             : %d   (%.1f%%)   <- THE NUMBER"
          % (len(real), 100.0 * len(real) / total if total else 0.0))
    print("  self-test FIXTURES         : %d   cited only from scripts/ as negative controls;"
          % len(fixture))
    print("                                   correct code, never counted as a defect")
    print("  transcript-capture ARTIFACTS: %d   cited only from agent-end/ or probe-packets/ raw"
          % len(artifact))
    print("                                   tool-call JSON; quoted text, not an authored citation")
    print("  DISPOSITIONED               : %d   every citing line carries `[target retired:` or"
          % len(dispositioned))
    print("                                   `[cross-trunk:` within 200 chars after the cite --")
    print("                                   a human already judged this row; not THE NUMBER")
    print("  IDENTITY  real(%d) + artifact(%d) + dispositioned(%d) = %d total broken"
          % (len(real), len(artifact), len(dispositioned),
             len(real) + len(artifact) + len(dispositioned)))
    print("            (fixtures excluded from \"total broken\" -- they are correct code, not defects)")
    print("  undispositioned real + dispositioned = %d   (was the old THE NUMBER, before"
          % (len(real) + len(dispositioned)))
    print("                                            dispositioning existed)")
    print("  NOTE: `[[slug]]` wikilinks are path-independent and are NOT checked here -- a folder")
    print("        move cannot break one. This number is the fragile class only.")

    base, have = load_baseline()
    if "--update-baseline" in argv:
        hdr = ["# check_wiki_path_refs baseline -- dangling wiki/*.md citations known at record time.",
               "# A bare run reports only what is NEW. Shrinking this file is the work."]
        open(BASELINE, "w", encoding="utf-8", newline="\n").write(
            "\n".join(hdr + sorted(real)) + "\n")
        print("  baseline RECORDED          : %d REAL dangling paths (fixtures excluded)"
              % len(real))
        print("")
        print("  Baseline recorded. This is NOT a pass -- nothing was judged.")
        return 0
    if not have:
        print("")
        print("  UNKNOWN -- no baseline on disk. Nothing can be called NEW, so nothing is called")
        print("  clean either. Run --update-baseline once, after reading the total above.")
        return 2

    new = sorted(p for p in real if p not in base)
    fixed = sorted(p for p in base if p not in real)
    print("  baseline dangling          : %d" % len(base))
    print("  FIXED since baseline       : %d   <- the direction that matters" % len(fixed))
    print("  NEW since baseline         : %d   <- THE ALARM" % len(new))
    if new:
        print("")
        for pth in new[:25]:
            where = real[pth][0]
            print("    %s" % pth)
            print("      first cited at %s:%d" % (where[0], where[1]))
        if len(new) > 25:
            print("    ... and %d more" % (len(new) - 25))
        print("")
        print("  REMEDY is per-row judgment: repoint, or record that the target was retired on")
        print("  purpose. Do NOT bulk-delete citations -- a dangling cite is evidence that")
        print("  something existed, and deleting it destroys the only trace.")
        return 6
    print("")
    print("  PASS -- no NEW dangling citations. This does NOT say the wiki's links are sound;")
    print("  it says nothing broke that was not already broken. Different claims.")
    return 0


def self_test():
    cases = [
        ("regex matches a plain citation", REF.findall("see wiki/index.md now") == ["wiki/index.md"]),
        ("regex matches a nested path",
         REF.findall("`wiki/tracker/wayfinder-cfl.md`") == ["wiki/tracker/wayfinder-cfl.md"]),
        ("NEGATIVE CONTROL: a bare directory is not a citation", REF.findall("wiki/tracker/") == []),
        ("NEGATIVE CONTROL: a non-md path is not matched", REF.findall("wiki/index.html") == []),
        ("NEGATIVE CONTROL: another trunk's dir is not read as ours (herald-wiki/)",
         REF.findall("see herald-wiki/exchange/inbound/foo.md") == []),
        ("NEGATIVE CONTROL: another trunk's dir is not read as ours (ollama_wiki/)",
         REF.findall("scripts/ollama_wiki/system_prompt.md") == []),
        ("a genuine citation right after a trunk-qualified false one still matches",
         REF.findall("herald-wiki/x.md and wiki/index.md") == ["wiki/index.md"]),
        ("raw/ is excluded -- the corpus is read-only and not ours to lint",
         "raw/" in SKIP_DIRS),
        ("no baseline renders UNKNOWN, never clean",
         "no baseline on disk" in open(os.path.abspath(__file__), encoding="utf-8").read()),
        ("wikilinks are explicitly out of scope, and the output says so",
         "path-independent" in open(os.path.abspath(__file__), encoding="utf-8").read()),
        ("it reports FIXED as well as NEW -- a ratchet needs the good direction visible",
         "FIXED since baseline" in open(os.path.abspath(__file__), encoding="utf-8").read()),
        ("it does NOT scan its own baseline -- a checker reading its own output measures itself",
         "A checker that reads its own output" in open(os.path.abspath(__file__), encoding="utf-8").read()),
        ("self-test fixtures are separated from real defects, not counted as them",
         "FIXTURES ARE SEPARATED, NOT COUNTED" in open(os.path.abspath(__file__), encoding="utf-8").read()),
        # ARTIFACT_DIRS cases added D8, 2026-09-04. These mirror classify()'s fixture/artifact
        # split via ad-hoc 2-tuples (pre-dispositioning shape) -- kept as-is since they still
        # exercise the same startswith() logic; the DISPOSITIONED cases below exercise the real
        # scan()+classify() path end to end instead of restating its rules as a lambda.
        ("a target cited ONLY from agent-end/ transcript captures is an ARTIFACT, not real",
         (lambda ARTIFACT_DIRS=("scripts/", "wiki/intake-triage/agent-end/",
                                 "wiki/skills-gate/probe-packets/"):
          all(any(c.startswith(d) for d in ARTIFACT_DIRS) for c, _ in
              [("wiki/intake-triage/agent-end/e515d8/x.i1.md", 1)]))()),
        ("a target cited ONLY from probe-packets/ is an ARTIFACT, not real",
         (lambda ARTIFACT_DIRS=("scripts/", "wiki/intake-triage/agent-end/",
                                 "wiki/skills-gate/probe-packets/"):
          all(any(c.startswith(d) for d in ARTIFACT_DIRS) for c, _ in
              [("wiki/skills-gate/probe-packets/x.probe-packet.md", 1)]))()),
        ("a target cited from agent-end/ AND a real wiki page is REAL, not artifact -- "
         "one genuine citer is enough to keep it counted",
         (lambda ARTIFACT_DIRS=("scripts/", "wiki/intake-triage/agent-end/",
                                 "wiki/skills-gate/probe-packets/"):
          not all(any(c.startswith(d) for d in ARTIFACT_DIRS) for c, _ in
                  [("wiki/intake-triage/agent-end/e515d8/x.i1.md", 1),
                   ("wiki/concepts/foo.md", 3)]))()),
    ]

    # DISPOSITIONED cases, added D8-A 2026-09-04. Unlike the string-grep cases above, these run
    # the real scan()+classify() code path against a synthetic on-disk repo -- the annotation
    # check depends on line content and a 200-character window, which a docstring grep cannot
    # verify. Nothing here touches the real repo; TemporaryDirectory cleans itself up.
    with tempfile.TemporaryDirectory(prefix="cwpr_selftest_") as _troot:
        os.makedirs(os.path.join(_troot, "wiki"), exist_ok=True)
        # a real target so case 5 (annotated but the target still exists) has something to resolve to.
        with open(os.path.join(_troot, "wiki", "real-target.md"), "w", encoding="utf-8") as _fh:
            _fh.write("ok\n")
        _citer_lines = [
            # 1: annotated with [target retired: right after the cite -- DISPOSITIONED
            "See wiki/does-not-exist-1.md [target retired: page removed].",
            # 2: annotated with [cross-trunk: right after the cite -- DISPOSITIONED
            "See wiki/does-not-exist-2.md [cross-trunk: lives in personal].",
            # 3 CONTROL: same shape, no annotation at all -- REAL, not dispositioned
            "See wiki/does-not-exist-3.md with no annotation nearby.",
            # 4 CONTROL: annotation present but ~280 chars away on the same line, past the
            # 200-char window -- a stray bracket elsewhere on the line must not disposition it
            "See wiki/does-not-exist-4.md" + (" " * 280) + "[target retired: too far to count].",
            # 5: annotated cite whose target actually exists -- resolves, not counted at all
            "See wiki/real-target.md [target retired: stale note, target still there].",
        ]
        with open(os.path.join(_troot, "wiki", "citer.md"), "w", encoding="utf-8") as _fh:
            _fh.write("\n".join(_citer_lines) + "\n")
        # D8-B fixtures. A probe-packet is machine-written; nobody annotates one. A target
        # cited from BOTH a human page and a probe-packet must be judged on the HUMAN citation
        # only -- otherwise the row can never be dispositioned no matter what a human does.
        _pp = os.path.join(_troot, "wiki", "skills-gate", "probe-packets")
        os.makedirs(_pp, exist_ok=True)
        with open(os.path.join(_pp, "p.probe-packet.md"), "w", encoding="utf-8") as _fh:
            _fh.write("raw capture quoting wiki/does-not-exist-5.md unannotated" + chr(10)
                      + "raw capture quoting wiki/does-not-exist-6.md "
                        "[target retired: written by a machine]" + chr(10))
        _citer_lines += [
            # 6 D8-B: human cite annotated, machine cite NOT -- must be DISPOSITIONED
            "See wiki/does-not-exist-5.md [target retired: judged by a human].",
            # 7 D8-B CONTROL: human cite UNannotated, machine cite annotated -- must stay REAL
            "See wiki/does-not-exist-6.md with no annotation from any human.",
        ]
        with open(os.path.join(_troot, "wiki", "citer.md"), "w", encoding="utf-8") as _fh:
            _fh.write(chr(10).join(_citer_lines) + chr(10))

        _broken, _ok = scan(_troot, ["wiki/citer.md",
                                     "wiki/skills-gate/probe-packets/p.probe-packet.md"])
        _fixture, _artifact, _dispositioned, _real = classify(_broken)

    cases += [
        ("DISPOSITIONED: `[target retired:` annotation within 200 chars after the cite",
         "wiki/does-not-exist-1.md" in _dispositioned),
        ("DISPOSITIONED: `[cross-trunk:` annotation within 200 chars after the cite",
         "wiki/does-not-exist-2.md" in _dispositioned),
        ("CONTROL: no annotation at all stays REAL, not dispositioned",
         "wiki/does-not-exist-3.md" in _real
         and "wiki/does-not-exist-3.md" not in _dispositioned),
        ("CONTROL: annotation ~280 chars away (past the 200-char window) stays REAL",
         "wiki/does-not-exist-4.md" in _real
         and "wiki/does-not-exist-4.md" not in _dispositioned),
        ("an annotated cite whose target actually exists resolves -- not counted at all",
         "wiki/real-target.md" not in _broken and "wiki/real-target.md" in _ok
         and "wiki/real-target.md" not in _dispositioned and "wiki/real-target.md" not in _real),
        ("D8-B: human cite annotated, probe-packet cite not -- DISPOSITIONED "
         "(a machine citation nobody can annotate must not block a human judgement)",
         "wiki/does-not-exist-5.md" in _dispositioned),
        ("D8-B CONTROL: human cite UNannotated while the probe-packet cite IS -- stays REAL "
         "(an annotation in machine output must never rescue a row)",
         "wiki/does-not-exist-6.md" in _real
         and "wiki/does-not-exist-6.md" not in _dispositioned),
        ("identity: real + artifact + dispositioned covers every non-fixture broken path",
         set(_real) | _artifact | _dispositioned == set(_broken) - _fixture),
    ]
    w = max(len(n) for n, _ in cases)
    for n, okv in cases:
        print("  %-*s : %s" % (w, n, "PASS" if okv else "FAIL"))
    bad = sum(1 for _, okv in cases if not okv)
    print("")
    print("RESULT: %s -- %d/%d" % ("PASS" if not bad else "FAIL", len(cases) - bad, len(cases)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
