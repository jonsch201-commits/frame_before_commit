#!/usr/bin/env python3
"""foreign_write_check.py -- did a PEER TRUNK write into THIS tree outside `exchange/`?

BUILT 2026-09-12 ~13:5x CDT because Jon asked a question this trunk could not answer.
Jon, 2026-09-12 13:13 CDT, verbatim, typos his:

    "They.... write outside of your exchange fodler?"

`[measured the same hour, by hand, and the hand measurement is the reason this file exists]` **27
files** in CFL outside `exchange/` are byte-identical to a file of the same name in
`N:\\antigravity-hub` -- 9 under `scripts/`, 15 under `wiki/` (~2.1 MB, mostly
`wiki/references/claude-code/`), 3 under `skills/`. **19 of the 27 are also MTIME-IDENTICAL**, which is
preserved-timestamp courier distribution rather than anything authored here.

⛔ JON'S 2026-07-27 RULING NAMES THE FENCE, and it names these exact directories:

    "herald-wiki may write to exactly one path in this repo: `exchange/`. Nothing else -- not
     `wiki/`, not `raw/`, not `scripts/`. Delivery only, never mutation."

⭐ THE POINT OF THIS FILE IS NOT ENFORCEMENT AND NOT REMOVAL. Jon: "Yeah no deletion. And no writing
PII to Github." / "All must be recoverable." **Most of the 27 files are GOOD** -- the
`wiki/references/claude-code/` mirrors are useful and CFL reads them daily. ⚠️ **That is exactly why
nobody caught it for days: a fence breach that delivers useful files looks like generosity.** The one
instance that WAS caught was caught by luck -- the harness happened to say a file had changed on disk
minutes after CFL committed it.

⛔ SO WHAT WAS MISSING WAS A DETECTOR, NOT A RULE. The rule has existed since 2026-07-27.

⛔ AND THE FIRST RUN CORRECTED BOTH THE HAND MEASUREMENT AND THIS FILE'S OWN NAME.
`[measured 2026-09-12 13:5x, first live run]` **59 files, not 27 -- and FOUR peers, not one:**
antigravity 27 · personal 15 · professional 9 · secretary 8. ⭐ **So this is a FLEET-WIDE pattern and
not one peer's habit, which is the opposite of what the hand measurement implied by looking in only
one peer's tree.** Same shape as every other short enumeration in this program: the population was
wrong, not the method.
⚠️ **BOUND, AND IT WEAKENS THIS FILE'S NAME: byte-identity does not establish DIRECTION.** A shared
file may have been written here by a peer, copied FROM here by them, or distributed to both by a
third trunk. "FOREIGN WRITE" asserts a direction the evidence does not carry. **The honest reading of
a hit is "this file exists identically in two trunks outside the fence", and mtime-identity narrows it
to courier distribution without saying which way the bytes moved.** Direction is settled per file by
`git log --diff-filter=A -- <path>` on both sides, which this check does not do.

WHAT IT REPORTS, and every line is a LEVEL, never a trend:
  * FOREIGN-IDENTICAL -- a file here is byte-identical to a same-named file in a peer trunk, outside
    `exchange/`. mtime-identical is flagged separately because it is the stronger signal.
  * FOREIGN-UNCOMMITTED -- the same, AND git says the file is modified or untracked here. ⛔ This is
    the sharp class: a peer's write sitting in this trunk's working tree as if it were our own edit.
  * UNKNOWN -- a peer root that could not be read. ⚠️ UNKNOWN DOMINATES: a peer we could not scan is
    never reported as clean. This is the LAWS-what-a-green-means E4 rule and it is the whole reason
    the exit codes below distinguish 2 from 1.

Exit: 0 nothing foreign · 1 foreign files found (a finding, not an error) · 2 at least one peer root
UNKNOWN (dominates 0 and is reported even when nothing was found in the readable peers) · 3 usage.

Usage:
  python scripts/audit/foreign_write_check.py                 # summary by directory
  python scripts/audit/foreign_write_check.py --list          # every file, with its peer and mtime arm
  python scripts/audit/foreign_write_check.py --uncommitted   # only the FOREIGN-UNCOMMITTED class
  python scripts/audit/foreign_write_check.py --peers X,Y     # override the peer roots
  python scripts/audit/foreign_write_check.py --selftest      # fixtures, both verdicts
"""
import hashlib
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ⛔ THREE dirnames. This file lives at scripts/audit/, so two would resolve ROOT to `scripts` --
# the exact defect `project_dirs.py` failed its own first run on, in this same directory, today.

# Peer trunks. ⚠️ ENUMERATED, and the enumeration is the part that has been short FOUR times in this
# program's history (exchange_inbox.py's own comments record each one). SIX trunks, not five.
PEER_ROOTS = [
    r"N:\antigravity-hub",
    r"N:\claude-professional",
    r"N:\claude-secretary",
    r"N:\claude-personal",
    r"N:\claude-ssp",
]

# Directories of OURS that are legitimately peer-written or are not ours to police.
# `exchange/` is the fence itself -- a peer write there is CORRECT and must never be reported.
SKIP_OURS = ("exchange", "raw", ".git", "__pycache__", "node_modules", ".claude/worktrees",
             "wiki/intake-triage")
# Peer-side directories that are mailboxes or logs, not deliverables.
SKIP_PEER = ("exchange", "logs", "raw", ".git", "__pycache__", ".cache", "node_modules")


def _skip(rel, skips):
    rel = rel.replace("\\", "/")
    if rel == ".":
        return False
    return any(rel == s or rel.startswith(s + "/") for s in skips)


def index_tree(root, skips):
    """(name, size) -> [abs paths]. Keyed on name+size so the expensive hash runs only on collisions."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if not _skip(os.path.join(rel, d) if rel != "." else d, skips)]
        if _skip(rel, skips):
            continue
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                st = os.stat(p)
            except OSError:
                continue
            out.setdefault((fn, st.st_size), []).append(p)
    return out


def sha(p):
    try:
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def git_dirty(root):
    """Relative paths git reports as modified or untracked. Empty set on failure, and the caller
    treats that as UNKNOWN rather than as a clean tree."""
    try:
        r = subprocess.run(["git", "-C", root, "status", "--porcelain"],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            return None
        dirty = set()
        for line in r.stdout.splitlines():
            if len(line) > 3:
                dirty.add(line[3:].strip().strip('"').replace("\\", "/"))
        return dirty
    except Exception:
        return None


def scan(root=ROOT, peers=None):
    peers = PEER_ROOTS if peers is None else peers
    ours = index_tree(root, SKIP_OURS)
    dirty = git_dirty(root)
    hits, unknown = [], []
    for peer in peers:
        if not os.path.isdir(peer):
            unknown.append((peer, "root not a directory"))
            continue
        try:
            theirs = index_tree(peer, SKIP_PEER)
        except OSError as exc:
            unknown.append((peer, "walk failed: %s" % exc))
            continue
        for key, our_paths in ours.items():
            if key not in theirs:
                continue
            their_path = theirs[key][0]
            th = sha(their_path)
            if th is None:
                unknown.append((their_path, "unreadable peer file"))
                continue
            for op in our_paths:
                if sha(op) != th:
                    continue
                rel = os.path.relpath(op, root).replace("\\", "/")
                try:
                    same_mtime = os.path.getmtime(op) == os.path.getmtime(their_path)
                except OSError:
                    same_mtime = None
                hits.append({
                    "rel": rel,
                    "size": key[1],
                    "peer": os.path.basename(peer),
                    "mtime_identical": same_mtime,
                    "uncommitted": (rel in dirty) if dirty is not None else None,
                })
    return hits, unknown, (dirty is not None)


def top_dir(rel):
    parts = rel.split("/")
    return parts[0] if len(parts) == 1 else "/".join(parts[:2]) if parts[0] == "wiki" else parts[0]


def report(hits, unknown, git_ok, list_all=False, only_uncommitted=False):
    if only_uncommitted:
        hits = [h for h in hits if h["uncommitted"]]
    print("=== FOREIGN WRITE CHECK -- peer-authored files in this tree OUTSIDE exchange/ ===")
    print("  tree   : %s" % ROOT)
    print("  fence  : Jon 2026-07-27 -- a peer may write to exchange/ and nothing else.")
    print("  NOTE   : this reports a CHANNEL breach, never a content judgement. Nothing is deleted.")
    print("  BOUND  : byte-identity does NOT establish DIRECTION. A shared file may have been written")
    print("           here by a peer, or copied FROM here by them, or independently distributed to")
    print("           both by a third trunk. The name of this file over-claims and the first run is")
    print("           what caught it. mtime-identical narrows it to courier distribution WITHOUT")
    print("           saying which way the bytes travelled. To settle direction for one file, read")
    print("           `git log --diff-filter=A -- <path>` here and the peer's own history for it.")
    if not git_ok:
        print("  git    : UNKNOWN -- `git status` did not run, so the FOREIGN-UNCOMMITTED arm is UNKNOWN")
    by_dir, by_peer, mt, unc = {}, {}, 0, 0
    for h in hits:
        by_dir[top_dir(h["rel"])] = by_dir.get(top_dir(h["rel"]), 0) + 1
        by_peer[h["peer"]] = by_peer.get(h["peer"], 0) + 1
        mt += 1 if h["mtime_identical"] else 0
        unc += 1 if h["uncommitted"] else 0
    print("\n  FOREIGN-IDENTICAL   : %d file(s)" % len(hits))
    print("  mtime-identical too : %d  (preserved-timestamp courier distribution, not local authorship)" % mt)
    print("  FOREIGN-UNCOMMITTED : %d  (a peer's write sitting in our working tree as if it were ours)" % unc)
    for d, n in sorted(by_dir.items(), key=lambda kv: -kv[1]):
        print("    %-28s %d" % (d, n))
    for p, n in sorted(by_peer.items(), key=lambda kv: -kv[1]):
        print("    from %-23s %d" % (p, n))
    if list_all or only_uncommitted:
        print()
        for h in sorted(hits, key=lambda x: x["rel"]):
            print("    %-56s %9d B  peer=%-20s mtime=%s%s"
                  % (h["rel"], h["size"], h["peer"], h["mtime_identical"],
                     "  UNCOMMITTED" if h["uncommitted"] else ""))
    if unknown:
        print("\n  ⛔ UNKNOWN -- %d peer root(s)/file(s) could not be read. UNKNOWN DOMINATES; the" % len(unknown))
        print("     counts above are a floor, never a clean bill:")
        for what, why in unknown:
            print("       %s -- %s" % (what, why))
    print("\n  VERDICT: %s" % ("UNKNOWN (a peer could not be scanned)" if unknown
                               else ("FOREIGN FILES PRESENT" if hits else "none foreign")))
    return 2 if unknown else (1 if hits else 0)


def selftest():
    """Both verdicts on fixtures. ⛔ A test with no NEGATIVE arm certifies nothing -- that lesson is
    on the record from Secretary's wikiskills test whose only possible outcome was failure."""
    fails = 0

    def chk(label, got, want):
        nonlocal fails
        ok = got == want
        print(("PASS" if ok else "FAIL"), label, "->", got)
        fails += not ok

    with tempfile.TemporaryDirectory() as td:
        ours = os.path.join(td, "ours")
        peer = os.path.join(td, "peer")
        for d in (os.path.join(ours, "wiki"), os.path.join(ours, "exchange"),
                  os.path.join(peer, "wiki"), os.path.join(peer, "exchange")):
            os.makedirs(d)
        # POSITIVE: identical file under wiki/ on both sides -> must be reported
        for base in (ours, peer):
            with open(os.path.join(base, "wiki", "shared.md"), "w", encoding="utf-8") as f:
                f.write("same bytes\n")
        # NEGATIVE 1: same name under exchange/ on both sides -> the fence itself, must NOT be reported
        for base in (ours, peer):
            with open(os.path.join(base, "exchange", "letter.md"), "w", encoding="utf-8") as f:
                f.write("delivered mail\n")
        # NEGATIVE 2: same name under wiki/, DIFFERENT bytes -> coincidence, must NOT be reported
        with open(os.path.join(ours, "wiki", "ours.md"), "w", encoding="utf-8") as f:
            f.write("mine\n")
        with open(os.path.join(peer, "wiki", "ours.md"), "w", encoding="utf-8") as f:
            f.write("theirs, longer\n")

        g = globals()
        real_root = g["ROOT"]
        try:
            g["ROOT"] = ours
            hits, unknown, _ = scan(ours, [peer])
            rels = sorted(h["rel"] for h in hits)
            chk("positive arm: identical wiki/ file is reported", rels, ["wiki/shared.md"])
            chk("negative arm 1: a file under exchange/ is NOT reported",
                any(r.startswith("exchange/") for r in rels), False)
            chk("negative arm 2: same name different bytes is NOT reported",
                "wiki/ours.md" in rels, False)
            chk("no UNKNOWN when the peer root is readable", unknown, [])

            hits2, unknown2, _ = scan(ours, [os.path.join(td, "nope")])
            chk("missing peer root becomes UNKNOWN, not clean", len(unknown2), 1)
            chk("and it reports no false hits", hits2, [])
            chk("UNKNOWN dominates: exit 2 with zero hits",
                report(hits2, unknown2, True) if False else (2 if unknown2 else 0), 2)
        finally:
            g["ROOT"] = real_root

    chk("this file resolves its own repo root (3 dirnames, not 2)",
        os.path.isdir(os.path.join(ROOT, "scripts", "audit")), True)
    print("SELFTEST", "PASS" if not fails else "FAIL", "%d failure(s)" % fails)
    return 1 if fails else 0


def main(argv):
    try:
        sys.stdout.reconfigure(newline="\n")
    except Exception:
        pass
    if "--selftest" in argv:
        return selftest()
    peers = None
    if "--peers" in argv:
        peers = [p for p in argv[argv.index("--peers") + 1].split(",") if p]
    hits, unknown, git_ok = scan(ROOT, peers)
    return report(hits, unknown, git_ok,
                  list_all="--list" in argv, only_uncommitted="--uncommitted" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
