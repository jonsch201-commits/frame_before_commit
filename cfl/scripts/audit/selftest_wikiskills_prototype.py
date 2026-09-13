#!/usr/bin/env python3
"""selftest_wikiskills_prototype.py -- offline regression check for wikiskills_prototype_render.py
(lane W-5, week-2026-09-02-corpus map).

Builds a SCRATCH copy of the tree the renderer needs (wiki/, skills/, scripts/audit/) under the
system temp dir (`tempfile.mkdtemp`) -- never touches G:\\, never writes back into N:\\claude-corpus
(read-only), never touches this clone's own wiki/WIKISKILLS-PROTOTYPE.md. `git init`s the scratch
copy (with -c user.name/user.email flags only -- no global git config is ever written) so
`git ls-files` inside the renderer resolves against the scratch tree, not this repo.

Branch (a): render the scratch tree as-is, record sources-count and rendered_sha256. Remove one
wiki/sources page, commit, re-render. ASSERT both the sources count decreased by exactly 1 and
rendered_sha256 changed. This is the regression detector: if a future edit to the renderer
hardcodes the sources count instead of deriving it from disk, branch (a) FAILS here, proving the
detector can actually fail rather than always reporting PASS.

Branch (b): render the scratch tree twice with NO change in between (same commit). ASSERT the two
renders are byte-identical (excl. rendered_at) -- a determinism sanity check independent of (a).

Exit 0 if both branches pass, 1 otherwise (with the failing branch named).
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

COPY_DIRS = ["wiki", "skills", "scripts"]
GIT_ENV_FLAGS = ["-c", "user.name=selftest", "-c", "user.email=selftest@localhost"]


def sh(cmd, cwd, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(cmd)}\nSTDOUT:{r.stdout}\nSTDERR:{r.stderr}")
    return r.stdout.strip()


def build_scratch():
    scratch = tempfile.mkdtemp(prefix="wikiskills-selftest-")
    for d in COPY_DIRS:
        shutil.copytree(os.path.join(REPO_ROOT, d), os.path.join(scratch, d))
    sh(["git", "init", "-q"], scratch)
    sh(["git"] + GIT_ENV_FLAGS + ["add", "-A"], scratch)
    sh(["git"] + GIT_ENV_FLAGS + ["commit", "-q", "-m", "scratch base"], scratch)
    return scratch


def render(scratch):
    r = subprocess.run([sys.executable, os.path.join(scratch, "scripts", "audit",
                        "wikiskills_prototype_render.py")], cwd=scratch, capture_output=True,
                        text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"render failed:\n{r.stdout}\n{r.stderr}")
    with open(os.path.join(scratch, "wiki", "WIKISKILLS-PROTOTYPE.md"), encoding="utf-8") as f:
        text = f.read()
    m_count = re.search(r"sources/\s+(\d+) pages", text)
    m_sha = re.search(r"rendered_sha256: ([0-9a-f]{64})", text)
    return int(m_count.group(1)), m_sha.group(1), text


def strip_rendered_at(s):
    return re.sub(r"^rendered_at: .*$", "rendered_at: X", s, flags=__import__("re").M)


def branch_a(scratch):
    n0, sha0, _ = render(scratch)
    sources_dir = os.path.join(scratch, "wiki", "sources")
    victim = None
    for dirpath, _, files in os.walk(sources_dir):
        for f in files:
            if f.endswith(".md"):
                victim = os.path.join(dirpath, f)
                break
        if victim:
            break
    if not victim:
        return False, "no wiki/sources page found to remove in scratch copy"
    os.remove(victim)
    sh(["git"] + GIT_ENV_FLAGS + ["add", "-A"], scratch)
    sh(["git"] + GIT_ENV_FLAGS + ["commit", "-q", "-m", "remove one page"], scratch)
    n1, sha1, _ = render(scratch)
    ok = (n1 == n0 - 1) and (sha1 != sha0)
    detail = f"before: {n0} pages sha={sha0[:8]}; after removing 1: {n1} pages sha={sha1[:8]}"
    return ok, detail


def branch_b(scratch):
    _, _, t0 = render(scratch)
    _, _, t1 = render(scratch)
    ok = strip_rendered_at(t0) == strip_rendered_at(t1)
    return ok, "two renders of the unchanged scratch tree, compared excl. rendered_at"


def main():
    scratch = build_scratch()
    try:
        results = []
        for name, fn in [("branch (a) planted-removal regression detector", branch_a),
                          ("branch (b) determinism sanity", branch_b)]:
            try:
                ok, detail = fn(scratch)
            except Exception as e:
                ok, detail = False, f"raised: {e}"
            results.append((name, ok, detail))
            print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
        overall = all(ok for _, ok, _ in results)
        print(f"\nOVERALL: {'PASS' if overall else 'FAIL'} (scratch tree: {scratch})")
        sys.exit(0 if overall else 1)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
