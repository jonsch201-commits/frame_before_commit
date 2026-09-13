#!/usr/bin/env python3
"""instrument-inventory.py -- the join between AN INSTRUMENT EXISTS and SOMETHING CALLS IT.

WHY THIS EXISTS. 2026-09-02, three instances in one afternoon, all in this trunk, none of them a
bug in the instrument:

  1. scripts/boundary-census.py is the DIRECT form of the question C29 answers from a DEAD receipt
     log. It was already in the tree, built a week earlier for the adjacent reason, and nothing
     connected it. C29 kept reporting 1 silent boundary of 22; the true figure is at least 4.
  2. scripts/lint.sh already hashes its own source at entry and exit and reports UNKNOWN if the
     file changed mid-run. An earlier session built it. This session panicked about exactly that
     failure and killed a run before discovering the guard existed.
  3. scripts/corpus-sync.sh states in its own output that it rebuilds no index. C25 grades the
     index's age. No step in the loop owned the rebuild, so the check failed every session and
     nothing changed in the world.

That is not three bugs. It is one shape, and soul named it [relayed+, 2026-09-02]:
THE FIX EXISTS AND NOTHING CALLS IT. A trunk that is good at building instruments and keeps no
inventory of which ones are wired will keep paying for the same artifact twice.

WHAT THIS REPORTS. For every executable under scripts/, whether ANY of these references it:
  hooks      .claude/settings.json                     (the harness invokes it)
  lint       scripts/lint.sh                           (a check runs it)
  script     any other file under scripts/             (a pipeline step runs it)
  doc        WAKE.md, CLAUDE.md, wiki/, exchange/      (a human or a session is told to run it)

BOUNDS, and they are the whole honesty of this tool:

  * A TEXTUAL REFERENCE IS NOT AN INVOCATION. A filename in a comment, a changelog line, or a
    "do not use this" warning all count as a reference here. This tool answers "is it MENTIONED
    anywhere", which is a LOWER BOUND on wiring: UNREFERENCED is strong evidence of unwired,
    REFERENCED is weak evidence of wired.
  * It cannot see dynamic invocation -- a name built from a variable, a glob over scripts/, or a
    dispatch table -- so a script called only that way reports UNREFERENCED and is a false alarm.
  * It says NOTHING about whether a referenced instrument actually RUNS. Every hook in this trunk
    is referenced by settings.json and NONE has fired since 2026-09-01 20:10. Referenced, wired,
    and dead are three different states and this tool distinguishes only the first.
  * The four reference classes are DECLARED, not discovered. A caller living somewhere else --
    another trunk, a cron, a skill file outside these paths -- is outside this population, and a
    population that excludes the caller reports a false orphan. Name a new class here rather than
    widening a glob silently.
"""
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SETTINGS = ".claude/settings.json"
LINT = "scripts/lint.sh"
DOC_ROOTS = ["wiki", "exchange"]
DOC_FILES = ["WAKE.md", "CLAUDE.md", "START-HERE.md", "RESUME.md", "RESUME-NEXT.md"]


# ⛔ THE POPULATION ROOT IS THE SAME HAZARD ONE LEVEL UP FROM THE REFERENCE CLASSES, and it is the
# one that caught soul [relayed+ 2026-09-02, their correction to me]: their inventory walked
# scripts/ in a trunk with TWO executable roots, found 3 hook-named scripts "not on disk", and
# nearly reported three broken hooks in a working config -- a false alarm caused entirely by the
# search root. This trunk's own CLAUDE.md already carries the class, written about SKILLS after the
# project-local root was missed: "the question is never what is in the directory -- it is what are
# ALL the directories a thing can load from in this trunk, and did I enumerate them before
# counting." Nobody had transferred it from skills to executables.
# ⛔ MEASURED HERE, and the first version of this file had the defect: walking scripts/ alone gave
# 33 and MISSED .claude/skills/oath-checks/oath_checks.sh -- which holds checks C16 through C29.
# The most load-bearing instrument in the lint suite was outside the population that counts
# instruments.
# ROOTS ARE DECLARED AND PRINTED WITH THE VERDICT. A root that does not exist is listed as absent
# rather than silently skipped: absent is a fact about this trunk, not a gap in the count.
EXEC_ROOTS = ["scripts", ".claude/hooks", ".claude/skills", ".claude/commands"]


def executables():
    out = []
    for root in EXEC_ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for fn in filenames:
                if fn.endswith((".py", ".sh")):
                    out.append(os.path.join(dirpath, fn).replace("\\", "/"))
    return sorted(out)


def roots_line():
    parts = []
    for root in EXEC_ROOTS:
        if os.path.isdir(root):
            n = sum(1 for dp, _dn, fns in os.walk(root) for f in fns if f.endswith((".py", ".sh")))
            parts.append("%s=%d" % (root, n))
        else:
            parts.append("%s=ABSENT" % root)
    return " | ".join(parts)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def hook_commands():
    try:
        data = json.loads(read(SETTINGS) or "{}")
    except json.JSONDecodeError:
        return "", 0
    blob, n = [], 0
    for _event, groups in (data.get("hooks") or {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                blob.append(hook.get("command", ""))
                n += 1
    return "\n".join(blob), n


def doc_blob():
    parts = []
    for f in DOC_FILES:
        parts.append(read(f))
    for root in DOC_ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            for fn in filenames:
                if fn.endswith(".md"):
                    parts.append(read(os.path.join(dirpath, fn)))
    return "\n".join(parts)


# --- LIVENESS. soul [relayed+ 2026-09-02, measured their seat]: Personal has 162 executables,
# 14 hook-wired (8.6% against this trunk's 15%), and ALL FOURTEEN ARE DEAD -- the whole continuity
# and Jon-capture apparatus correctly declared, correctly wired, and not executed once in ten hours.
# Their conclusion, adopted: "REFERENCED IS NOT RUNNING" is not a caveat on this tool, it is the
# HEADLINE. A wiring inventory whose top line is a reference count reads HEALTHY in a trunk where
# nothing runs.
#
# THE DEMAND SIDE IS THE HALF THAT COSTS RETRACTIONS. An artifact with an old mtime is not a dead
# hook unless something HAPPENED that should have written it. So each row below pairs the newest
# artifact a wired instrument writes with the count of events that should have invoked it, read
# from this session's own JSONL rather than from any log a hook maintains.
#
# BOUND: the map is DECLARED, not discovered. A hook that writes somewhere not listed here reports
# as dead and is a false alarm; add the path rather than widen a glob.
WIRED_ARTIFACTS = {
    "precompact-capture.sh": "exchange/precompact-receipts.log",
    "postcompact-brief.sh": "exchange/postcompact-brief.log",
    "postcompact-pipeline.py": "exchange/lineage.tsv",
    "render-sessions.sh": "raw/transcripts/claude-code",
}


def compact_boundaries():
    """Demand: compact boundaries in THIS session's JSONL. Read from the harness record, never
    from a receipt log -- the recorder is part of what may be dead."""
    base = os.path.expanduser("~/.claude/projects")
    newest, count = 0.0, 0
    if not os.path.isdir(base):
        return None, 0
    for dirpath, _dn, filenames in os.walk(base):
        if "Professional" not in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".jsonl"):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        if '"compact_boundary"' not in line:
                            continue
                        try:
                            o = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if o.get("type") == "system" and o.get("subtype") == "compact_boundary":
                            count += 1
                            newest = max(newest, os.path.getmtime(fp))
            except OSError:
                continue
    return newest, count


def newest_mtime(path):
    if os.path.isfile(path):
        return os.path.getmtime(path)
    if os.path.isdir(path):
        best = 0.0
        for dirpath, _dn, filenames in os.walk(path):
            for fn in filenames:
                try:
                    best = max(best, os.path.getmtime(os.path.join(dirpath, fn)))
                except OSError:
                    pass
        return best or None
    return None


def report_liveness():
    import time
    _newest_jsonl, demand = compact_boundaries()
    now = time.time()
    print("")
    print("LIVENESS -- wired is not alive. Demand read from the harness JSONL, not from any hook log.")
    print("BOUND: a FRESH artifact does not prove the HOOK ran. A person running the script by hand")
    print("   leaves the identical evidence. Measured 2026-09-02: render-sessions.sh reads fresh")
    print("   because THIS SESSION ran it by hand at 12:50 after finding the md 13.5 h stale -- the")
    print("   hook itself has not fired. So STALE here is evidence; FRESH is not the negation of it.")
    print("demand: %d compact boundary(ies) recorded for this trunk" % demand)
    dead = 0
    for script, artifact in sorted(WIRED_ARTIFACTS.items()):
        m = newest_mtime(artifact)
        if m is None:
            print("  UNKNOWN  %-26s %-38s artifact absent -- UNKNOWN, never a pass" % (script, artifact))
            dead += 1
            continue
        age_h = (now - m) / 3600.0
        verdict = "STALE" if age_h > 6 else "fresh"
        if verdict == "STALE":
            dead += 1
        print("  %-8s %-26s %-38s newest write %.1f h ago" % (verdict, script, artifact, age_h))
    if demand and dead:
        print("FINDING: %d of %d wired instrument(s) have written nothing recent while %d boundary(ies)"
              % (dead, len(WIRED_ARTIFACTS), demand))
        print("         should have invoked them. WIRED AND DEAD -- the state a reference count hides.")
    return dead


def main():
    exes = executables()
    hooks_blob, n_hooks = hook_commands()
    lint_blob = read(LINT)
    scripts_blob = {p: read(p) for p in exes}
    docs_blob = doc_blob()

    rows, orphans = [], []
    for path in exes:
        base = os.path.basename(path)
        # A script naming ITSELF is not a caller. Exclude its own text from the script class.
        others = "\n".join(v for k, v in scripts_blob.items() if k != path)
        refs = []
        if base in hooks_blob:
            refs.append("hooks")
        if base in lint_blob and path != LINT:
            refs.append("lint")
        if base in others:
            refs.append("script")
        if base in docs_blob:
            refs.append("doc")
        rows.append((path, refs))
        if not refs:
            orphans.append(path)

    print("INSTRUMENT INVENTORY -- reference is a LOWER BOUND on wiring, never proof of it.")
    print("population: %d executable(s) across the declared roots below (.py, .sh)" % len(exes))
    print("classes:    hooks(%d command(s) in %s) | lint | script | doc" % (n_hooks, SETTINGS))
    print("roots:      %s -- DECLARED, and printed with the verdict: an executable in a root not"
          % roots_line())
    print("            listed here is outside this population and reports as nothing at all.")
    print("")
    for path, refs in rows:
        if refs:
            print("  REFERENCED  %-52s %s" % (path, ",".join(refs)))
    print("")
    for path in orphans:
        print("  UNREFERENCED %-52s no hook, no lint, no sibling script, no doc names it" % path)
    print("")
    print("TOTAL referenced=%d unreferenced=%d of %d"
          % (len(exes) - len(orphans), len(orphans), len(exes)))
    print("⛔ REFERENCED IS NOT RUNNING. Every hook here is referenced by settings.json and none")
    print("   has fired since 2026-09-01 20:10. Referenced, wired and alive are three states.")
    report_liveness()
    if orphans:
        print("FINDING: %d instrument(s) that nothing in the declared classes names." % len(orphans))
        return 1
    print("FINDING: none -- every instrument is named by at least one declared class.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
