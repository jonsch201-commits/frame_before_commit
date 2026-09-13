#!/usr/bin/env python3
"""migrate_context_key.py -- R10 of the restart gate, as ONE instrument every trunk runs from its own tree.

Jon, 2026-09-05 00:2x CDT, verbatim, typos his: "ensure all co trunks do not betry themselves in the
context of this migration to N. Memory is so keyas is cdocumentation and tracability and more and many
have failed in that context. Ensure we find efficent unalzy fixes and solutions going forward."

The harness keys ~/.claude/projects/<key> on the working directory. The key holds session transcripts,
subagent transcripts and the agent MEMORY directory. A session started from a new home opens an EMPTY
key; the old files stay on disk, readable by absolute path, and the seat cannot tell from inside that
it used to know more (CFL: 75 memories -> 2 after its 09-02 move; found 09-04 by soul).

    --check   print the triple (sessions / subagents / memories) for the OLD key and the NEW key
              of --old-root and --new-root; exit 0 if memory counts are equal, 1 if not, 2 UNKNOWN
    --copy    additive copy of OLD/memory -> NEW/memory (never overwrite a newer file, never delete),
              write MIGRATED-FROM-<oldkey>-<date>.md inside NEW/memory, verify every copied file by
              md5, print counts both sides; exit 0 only if every file verifies
    --selftest fixtures in a temp dir: copy works, verification catches a corrupted byte, an existing
              newer file in NEW is not overwritten, the note is written, --check exit codes

What this does NOT do, on purpose: it does not copy session JSONLs (they must be copied after the
session is quiesced and parse-verified -- soul's torn-transcript hazard) and it does not rename or
delete anything (the old key stays the read fallback; renaming is the seat's own act after its first
session from the new home). Readers that want every session iterate BOTH keys (project_dirs.py).

Usage from any trunk (the tree does not need this repo; copy this one file):
    python migrate_context_key.py --check --old-root "G:/My Drive/Claude/Claude Personal" --new-root "N:/claude-personal"
    python migrate_context_key.py --copy  --old-root ... --new-root ...
"""
import hashlib
import os
import re
import shutil
import sys
import tempfile
import time

PROJECTS = os.path.join(os.path.expanduser("~"), ".claude", "projects")


def derive_key(root):
    p = os.path.abspath(root).replace("/", "\\")
    return re.sub(r"[^A-Za-z0-9]", "-", p)


def triple(keydir):
    if not os.path.isdir(keydir):
        return None
    sessions = sum(1 for f in os.listdir(keydir) if f.endswith(".jsonl"))
    subagents = 0
    for dp, dn, fn in os.walk(keydir):
        if "subagents" in dp.replace("/", os.sep).split(os.sep):
            subagents += sum(1 for f in fn if f.endswith(".jsonl"))
    mem = os.path.join(keydir, "memory")
    memories = sum(1 for f in os.listdir(mem) if f.endswith(".md")) if os.path.isdir(mem) else 0
    return sessions, subagents, memories


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check(old_key, new_key, projects=PROJECTS):
    o = triple(os.path.join(projects, old_key)); n = triple(os.path.join(projects, new_key))
    print("OLD %s  sessions=%s subagents=%s memories=%s" % ((old_key,) + (o if o else ("ABSENT",) * 3)))
    print("NEW %s  sessions=%s subagents=%s memories=%s" % ((new_key,) + (n if n else ("ABSENT",) * 3)))
    if o is None:
        print("UNKNOWN: old key absent -- nothing to migrate from, or the wrong root was given"); return 2
    if n is None:
        print("FAIL: new key absent -- a session from the new home would open EMPTY (memories %d -> 0)" % o[2]); return 1
    if n[2] < o[2]:
        print("FAIL: memories %d (old) vs %d (new) -- delta %d" % (o[2], n[2], o[2] - n[2])); return 1
    print("PASS: memories %d (old) <= %d (new); sessions stay under the old key until copied after quiesce" % (o[2], n[2]))
    return 0


def copy(old_key, new_key, projects=PROJECTS, now=None):
    src = os.path.join(projects, old_key, "memory")
    dst = os.path.join(projects, new_key, "memory")
    if not os.path.isdir(src):
        print("UNKNOWN: no memory dir under the old key (%s)" % src); return 2
    os.makedirs(dst, exist_ok=True)
    copied, skipped_newer, failed = [], [], []
    for f in sorted(os.listdir(src)):
        s = os.path.join(src, f); d = os.path.join(dst, f)
        if not os.path.isfile(s):
            continue
        if os.path.exists(d) and os.path.getmtime(d) > os.path.getmtime(s) and md5(d) != md5(s):
            skipped_newer.append(f); continue
        shutil.copy2(s, d)
        if md5(s) == md5(d):
            copied.append(f)
        else:
            failed.append(f)
    stamp = (now or time.strftime("%Y-%m-%d"))
    note = os.path.join(dst, "MIGRATED-FROM-%s-%s.md" % (old_key[:40], stamp))
    with open(note, "w", encoding="utf-8") as fh:
        fh.write("---\nname: migrated-from-%s\ndescription: provenance -- memory copied additively from the old project key on %s by migrate_context_key.py; the old key stays readable by absolute path\nmetadata:\n  type: reference\n---\n\nSource: %s\nCopied: %d file(s), md5-verified. Skipped (newer file already present, different content): %d. Failed verification: %d.\nOld key is the read fallback until the first session runs from the new home; then rename its memory/ to memory.MIGRATED-<date>. Never delete.\n"
                 % (old_key[:40], stamp, src, len(copied), len(skipped_newer), len(failed)))
    print("COPIED %d  SKIPPED-NEWER %d  FAILED-VERIFY %d  note=%s" % (len(copied), len(skipped_newer), len(failed), os.path.basename(note)))
    for f in skipped_newer: print("  skipped (newer in NEW, differs): %s" % f)
    for f in failed: print("  FAILED md5: %s" % f)
    print("source %d files -> dest %d files (incl. note)" % (len([x for x in os.listdir(src) if os.path.isfile(os.path.join(src, x))]), len(os.listdir(dst))))
    return 1 if failed else 0


def selftest():
    fails = 0
    with tempfile.TemporaryDirectory() as td:
        old = os.path.join(td, "OLDKEY"); new = os.path.join(td, "NEWKEY")
        os.makedirs(os.path.join(old, "memory")); os.makedirs(os.path.join(old, "subagents"))
        for i in range(3):
            open(os.path.join(old, "memory", "m%d.md" % i), "w").write("memory %d\n" % i)
        open(os.path.join(old, "s1.jsonl"), "w").write("{}\n"); open(os.path.join(old, "subagents", "agent-a.jsonl"), "w").write("{}\n")
        rc = check("OLDKEY", "NEWKEY", td); ok = rc == 1
        print("PASS" if ok else "FAIL", "check: new key absent -> exit 1 (got %d)" % rc); fails += not ok
        rc = copy("OLDKEY", "NEWKEY", td, now="2026-09-05"); ok = rc == 0 and len(os.listdir(os.path.join(new, "memory"))) == 4
        print("PASS" if ok else "FAIL", "copy: 3 files + note, all verified (rc %d)" % rc); fails += not ok
        rc = check("OLDKEY", "NEWKEY", td); ok = rc == 0
        print("PASS" if ok else "FAIL", "check after copy -> exit 0 (got %d)" % rc); fails += not ok
        # newer differing file in NEW must not be overwritten
        p = os.path.join(new, "memory", "m1.md"); open(p, "w").write("edited on the new home\n")
        t = time.time() + 100; os.utime(p, (t, t))
        copy("OLDKEY", "NEWKEY", td, now="2026-09-05")
        ok = open(p).read().startswith("edited"); print("PASS" if ok else "FAIL", "newer file in NEW preserved"); fails += not ok
        # md5 verification catches corruption: monkeypatch shutil.copy2 to corrupt
        orig = shutil.copy2
        def bad(s, d): orig(s, d); open(d, "ab").write(b"x")
        shutil.copy2 = bad
        try:
            rc = copy("OLDKEY", "NEWKEY2", td, now="2026-09-05")
        finally:
            shutil.copy2 = orig
        ok = rc == 1; print("PASS" if ok else "FAIL", "corrupted copy -> FAILED-VERIFY, exit 1 (got %d)" % rc); fails += not ok
        rc = check("NOPE", "NEWKEY", td); ok = rc == 2
        print("PASS" if ok else "FAIL", "old key absent -> UNKNOWN exit 2 (got %d)" % rc); fails += not ok
    print("SELFTEST", "PASS" if not fails else "FAIL", "%d failure(s)" % fails)
    return 1 if fails else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--old-root" not in argv or "--new-root" not in argv:
        print(__doc__); return 2
    old_key = derive_key(argv[argv.index("--old-root") + 1]); new_key = derive_key(argv[argv.index("--new-root") + 1])
    if "--copy" in argv:
        rc = copy(old_key, new_key)
        return max(rc, check(old_key, new_key))
    return check(old_key, new_key)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
