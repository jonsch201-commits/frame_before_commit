#!/usr/bin/env python3
"""review_surface.py -- partition a PR's diff into what a HUMAN reviews and what is only RECORD.

WHY THIS EXISTS
---------------
`[measured 2026-09-05 15:36 CDT, CFL, tree N:\\claude-cfl\\clone]` PR #255 (PR-3) changes
**5,263 files, +1,253,795 / -14,620 lines**. GitHub's Files tab does not render a diff
that size. So the question "is this PR human-readable?" had never actually been asked of
the thing Jon opens -- it had only been asked of the prose beside it.

CFL already carries TWO instruments that measure the readability of the DESCRIPTION
(`reader_cost.py`, `finished_means_reviewable.py`) and gate G9 settles it with a cold
reader. It carried ZERO that measure the readability of the DIFF. PR-2's own announcement
letter states the assumption in its title: "review surface is the description"
(`exchange/inbound/cfl-to-all-PR2-IS-OPEN-252-...-review-surface-is-the-description-2026-08-29.md`).

The measured partition of PR #255 says the assumption is what hid the problem:

    REVIEW            632 files     111,042 added   (12.0% of files,  8.9% of lines)
      of which NEW    526 files     102,565 added   -- read once, no "before" to compare
      of which MODIF  104 files  +8,419 / -1,819   -- the actual diff-reading
    EXCLUDED-TRUNK      3 files          29 added   -- wiki/home, wiki/pro, wiki/sensitive
    RECORD-PROSE    1,150 files     135,255 added
    RECORD-MACHINE  3,477 files   1,007,467 added   (66.1% of files, 80.4% of lines)

**88% of the files and 91% of the added lines are RECORD, not CHANGE.** They are correct,
they belong in the repo, and no person will ever read them in a review. Their only effect
on a reviewer is to bury the 632 files that carry the decisions.

⛔ THESE NUMBERS ARE A RECORDED VALUE AND THEY EXPIRE. They are here to explain the shape of
the problem, not to be quoted as current state -- rerun the script. The first draft of this
docstring already went stale inside a single session, when adding classification rules moved
REVIEW from 618 to 632. That is [[derive-dont-record]] firing on the file that cites it.

DESIGN NOTE -- FAIL-CLOSED, on CFL's own precedent
--------------------------------------------------
`regenerate_canonical.sh` aborts (exit 4) when a new `wiki/` child appears on neither the
published nor the excluded list, rather than publishing it by default. Same rule here: a
changed path matching NO class is **UNCLASSIFIED**, and any unclassified path makes the
verdict UNKNOWN with exit 3. A partition that silently absorbed new paths into whichever
side it defaults to would mis-grade the next PR the first time the tree grows, which is
this trunk's named characteristic failure ([[derive-dont-record]]).

USAGE
    review_surface.py [--base REF] [--head REF] [--markdown OUT.md] [--repo DIR]
    review_surface.py --selftest

    --base defaults to the merge-base of origin/main and --head; --head defaults to HEAD.

EXIT CODES
    0  PASS    -- every changed path classified; the REVIEW subset is reported
    3  UNKNOWN -- one or more paths are UNCLASSIFIED (dominates a PASS)
    2  usage / not a git repo / git failed
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

# --- the classification table -------------------------------------------------
# ORDER MATTERS: first match wins, most specific first.
CLASSES = [
    # ---- EXCLUDED-TRUNK: surface, do not act. --------------------------------
    # Jon's 2026-07-25 ruling keeps wiki/personal, wiki/home and wiki/pro off the
    # published `canonical` branch; wiki/sensitive is the same hazard class by name.
    # CLAUDE.md: "If a check reports under wiki/home, wiki/pro or wiki/personal,
    # SURFACE IT, DO NOT ACT." So they get their own row rather than being folded
    # into RECORD, where a reviewer would never see that they moved.
    ("EXCLUDED-TRUNK", "excluded trunks / sensitive", r"^wiki/(personal|home|pro|sensitive)/"),
    # ---- RECORD: machine-generated. Written by a script, read by a script. ----
    ("RECORD-MACHINE", "ingest / triage artifacts", r"^wiki/intake-triage/"),
    ("RECORD-MACHINE", "skills-gate ledgers",       r"^wiki/skills-gate/"),
    ("RECORD-MACHINE", "test outputs",              r"^wiki/test-outputs/"),
    ("RECORD-MACHINE", "evidence / lineage",        r"^evidence/"),
    ("RECORD-MACHINE", "su-close receipts",         r"^exchange/su-close/"),
    ("RECORD-MACHINE", "peer mail (inbound)",       r"^exchange/inbound/"),
    ("RECORD-MACHINE", "elder / compact windows",   r"^exchange/elders/"),
    ("RECORD-MACHINE", "memory-core instances",     r"^exchange/memory-core-v0/"),
    # ---- RECORD: prose. A person wrote it; it is correspondence, not change. --
    ("RECORD-PROSE", "ingested sources",          r"^wiki/sources/"),
    ("RECORD-PROSE", "external reference copies", r"^wiki/references/"),
    ("RECORD-PROSE", "transcripts / archive",     r"^wiki/(transcripts|archive)/"),
    ("RECORD-PROSE", "exchange correspondence",   r"^exchange/"),
    ("RECORD-PROSE", "shelf / parked",            r"^shelf/"),
    ("RECORD-PROSE", "gists",                     r"^gists/"),
    ("RECORD-PROSE", "scratchpad",                r"^scratchpad/"),
    # ---- REVIEW: the files that carry a decision. ----------------------------
    ("REVIEW", "constitutions",       r"^(CLAUDE\.md|CLAUDE-UNIVERSAL\.md)$"),
    ("REVIEW", "gates",               r"^GATES\.md$"),
    ("REVIEW", "harness config",      r"^(\.claude/|commands/|sync-universal\.sh$|launch-cfl\.bat$|\.gitignore$)"),
    ("REVIEW", "skills",              r"^skills/"),
    ("REVIEW", "scripts",             r"^scripts/"),
    ("REVIEW", "docker",              r"^docker/"),
    ("REVIEW", "docs",                r"^docs/"),
    ("REVIEW", "wiki concepts",       r"^wiki/concepts/"),
    ("REVIEW", "wiki tracker (maps)", r"^wiki/tracker/"),
    ("REVIEW", "wiki patterns",       r"^wiki/patterns/"),
    ("REVIEW", "wiki entities",       r"^wiki/(entities|methodology)/"),
    ("REVIEW", "wiki index",          r"^wiki/index\.md$"),
    ("REVIEW", "wiki decisions",      r"^wiki/DECISIONS\.md$"),
    ("REVIEW", "wiki meta / guides",   r"^wiki/(CLAUDE\.md|README\.md|SCHEMA\.md|agent-guide\.md|overview\.md|index\.md|meta-index\.md|retrieval-index\.md|WIKISKILLS-PROTOTYPE\.md)$"),
    ("REVIEW", "prototypes",           r"^PROTOTYPE-[\w.\-]+$"),
    # ---- RECORD: wiki operational logs and loose legacy pages. ---------------
    ("RECORD-MACHINE", "wiki operation logs", r"^wiki/(log\.md|logs\.md|log-GATE-[\w.\-]+\.md)$"),
    ("RECORD-PROSE",   "wiki analyses",       r"^wiki/analyses/"),
    ("RECORD-PROSE",   "wiki works",          r"^wiki/works/"),
    ("RECORD-PROSE",   "wiki session index",  r"^wiki/sessions/"),
    ("RECORD-PROSE",   "wiki loose legacy pages", r"^wiki/[\w.\-]+\.md$"),
    ("RECORD-PROSE",   "loose repo-root scratch", r"^[\w.\-]+\.(sh|html)$"),
]
COMPILED = [(c, label, re.compile(rx)) for c, label, rx in CLASSES]
ORDER = ["REVIEW", "EXCLUDED-TRUNK", "RECORD-PROSE", "RECORD-MACHINE", "UNCLASSIFIED"]


def classify(path):
    for cls, label, rx in COMPILED:
        if rx.search(path):
            return cls, label
    return "UNCLASSIFIED", "no rule matches this path"


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("git %s failed: %s\n" % (" ".join(args), r.stderr.strip()))
        sys.exit(2)
    return r.stdout


def collect(repo, base, head):
    """Return list of (added, deleted, path, status). Binary files report added=deleted=None.

    STATUS MATTERS, and the reason came from the elder consult of session 71ce5a0e
    (2026-09-05): "431 NEW files -- you skim a new instrument, you don't diff it -- and 152
    MODIFIED files whose entire combined churn is 8,962 lines." Reading a new file and
    reviewing a change to an existing one are different acts costing different amounts, and
    a single files-changed number hides the difference.
    """
    status = {}
    for line in git(repo, "diff", "--name-status", base, head).splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            status[parts[-1]] = parts[0][0]
    rows = []
    for line in git(repo, "diff", "--numstat", base, head).splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        a, d, p = parts[0], parts[1], parts[-1]
        rows.append((None if a == "-" else int(a), None if d == "-" else int(d), p,
                     status.get(p, "?")))
    return rows


def summarize(rows):
    buckets = {}
    for row in rows:
        a, d, p, st = row[0], row[1], row[2], (row[3] if len(row) > 3 else "?")
        cls, label = classify(p)
        b = buckets.setdefault(cls, {})
        e = b.setdefault(label, {"files": 0, "added": 0, "deleted": 0, "paths": [],
                                 "new_files": 0, "new_added": 0,
                                 "mod_files": 0, "mod_added": 0, "mod_deleted": 0,
                                 "stat": {}})
        e["files"] += 1
        e["added"] += a or 0
        e["deleted"] += d or 0
        e["paths"].append(p)
        e["stat"][p] = (a, d, st)
        if st == "A":
            e["new_files"] += 1
            e["new_added"] += a or 0
        elif st in ("M", "R", "C"):
            e["mod_files"] += 1
            e["mod_added"] += a or 0
            e["mod_deleted"] += d or 0
    return buckets


def totals(buckets, cls):
    b = buckets.get(cls, {})
    return (sum(e["files"] for e in b.values()),
            sum(e["added"] for e in b.values()),
            sum(e["deleted"] for e in b.values()))


def render(buckets, base, head, markdown=False):
    out = []
    W = out.append
    tf = sum(totals(buckets, c)[0] for c in ORDER)
    ta = sum(totals(buckets, c)[1] for c in ORDER)
    h = (lambda s: W("## " + s)) if markdown else (lambda s: W("=== %s ===" % s))

    if markdown:
        W("# Review surface: %s..%s" % (base[:12], head[:12]))
        W("")
        W("**%d changed files, %d added lines.**" % (tf, ta))
        W("")
        W("| class | files | % of files | added lines | % of lines |")
        W("|---|---:|---:|---:|---:|")
    else:
        W("REVIEW SURFACE  %s..%s" % (base[:12], head[:12]))
        W("")
        W("%d changed files, %d added lines." % (tf, ta))
        W("")
    for cls in ORDER:
        f, a, _ = totals(buckets, cls)
        if f == 0 and cls == "UNCLASSIFIED":
            continue
        pf = 100.0 * f / tf if tf else 0
        pa = 100.0 * a / ta if ta else 0
        if markdown:
            W("| **%s** | %d | %.1f%% | %d | %.1f%% |" % (cls, f, pf, a, pa))
        else:
            W("  %-16s %6d files (%5.1f%%)  %9d added (%5.1f%%)" % (cls, f, pf, a, pa))
    W("")

    rv = buckets.get("REVIEW", {})
    nf = sum(e["new_files"] for e in rv.values())
    na = sum(e["new_added"] for e in rv.values())
    mf = sum(e["mod_files"] for e in rv.values())
    ma = sum(e["mod_added"] for e in rv.values())
    md = sum(e["mod_deleted"] for e in rv.values())
    h("What to actually review (%d files)" % totals(buckets, "REVIEW")[0])
    W("")
    if markdown:
        W("**Two different acts, costing different amounts — so they are counted separately.**")
        W("")
        W("| | files | lines |")
        W("|---|---:|---:|")
        W("| **NEW** — read it once; there is no \"before\" to compare against | %d | %d added |" % (nf, na))
        W("| **MODIFIED** — the actual diff-reading, and the only part that needs the old version | **%d** | **+%d / -%d** |" % (mf, ma, md))
        W("")
        W("⭐ **The modified-file churn is the number a reviewer's time scales with: %d lines across %d files.**" % (ma + md, mf))
    else:
        W("  NEW      %5d files  %8d added   (read once; no 'before' to compare)" % (nf, na))
        W("  MODIFIED %5d files  +%d / -%d   <-- reviewer time scales with THIS" % (mf, ma, md))
    W("")
    if markdown:
        W("| group | files | added |")
        W("|---|---:|---:|")
    for label, e in sorted(buckets.get("REVIEW", {}).items(), key=lambda kv: -kv[1]["added"]):
        if markdown:
            W("| %s | %d | %d |" % (label, e["files"], e["added"]))
        else:
            W("  %-24s %5d files  %8d added" % (label, e["files"], e["added"]))
    W("")

    # THE MODIFIED LIST. Added 2026-09-05 after Professional ran the G9 cold-reader test at
    # n=2 on this very page: "What both readers were reaching for and neither page has: the
    # 104 MODIFIED files listed with one line each." Two cold readers asked for it
    # independently, so it is not a nicety -- it is the thing the page was missing.
    if mf:
        h("The %d MODIFIED files, in full -- this is the reviewer's actual worklist" % mf)
        W("")
        mods = []
        for label, e in rv.items():
            for p in e["paths"]:
                mods.append((label, p))
        by_path = {}
        for e in rv.values():
            by_path.update(e["stat"])
        mods = [(lb, p) for lb, p in mods if by_path.get(p, (0, 0, "?"))[2] in ("M", "R", "C")]
        mods.sort(key=lambda t: -(by_path[t[1]][0] or 0) - (by_path[t[1]][1] or 0))
        if markdown:
            W("| file | + | − | group |")
            W("|---|---:|---:|---|")
            for lb, p in mods:
                a, d, _ = by_path[p]
                W("| `%s` | %d | %d | %s |" % (p, a or 0, d or 0, lb))
        else:
            for lb, p in mods:
                a, d, _ = by_path[p]
                W("  +%-6d -%-6d %-22s %s" % (a or 0, d or 0, lb, p))
        W("")

    h("What is RECORD, and why it is in the diff anyway")
    W("")
    for cls in ("RECORD-PROSE", "RECORD-MACHINE"):
        for label, e in sorted(buckets.get(cls, {}).items(), key=lambda kv: -kv[1]["added"]):
            if markdown:
                W("- **%s** (%s) — %d files, %d added" % (label, cls, e["files"], e["added"]))
            else:
                W("  %-16s %-26s %5d files  %8d added" % (cls, label, e["files"], e["added"]))
    W("")

    u = buckets.get("UNCLASSIFIED", {})
    if u:
        h("UNCLASSIFIED -- the verdict is UNKNOWN until these get a rule")
        W("")
        for label, e in u.items():
            for p in e["paths"][:40]:
                W(("- `%s`" if markdown else "  %s") % p)
            if e["files"] > 40:
                W(("- ...and %d more" if markdown else "  ...and %d more") % (e["files"] - 40))
        W("")
        W("**VERDICT: UNKNOWN** -- %d path(s) match no class. UNKNOWN dominates a PASS."
          % sum(e["files"] for e in u.values()))
    else:
        rf, ra, _ = totals(buckets, "REVIEW")
        W(("**VERDICT: PASS** -- " if markdown else "VERDICT: PASS -- ")
          + "every changed path is classified. The human review surface is "
          + "**%d files / %d added lines**, %.1f%% of the files and %.1f%% of the lines in this diff."
          % (rf, ra, 100.0 * rf / tf if tf else 0, 100.0 * ra / ta if ta else 0))
    return "\n".join(out)


# --- selftest -----------------------------------------------------------------
def selftest():
    """Exercise BOTH verdicts against a real git repo built here. A check that only
    exercises PASS has not tested the FAIL path -- WW-1's negative-control lesson."""
    ok = [True]

    def assert_(cond, msg):
        print(("  PASS  " if cond else "  FAIL  ") + msg)
        ok[0] = ok[0] and bool(cond)

    cases = [
        ("wiki/intake-triage/x.json", "RECORD-MACHINE"),
        ("exchange/inbound/letter.md", "RECORD-MACHINE"),
        ("exchange/su-close/CONSUMED.md", "RECORD-MACHINE"),
        ("exchange/CARRIER.md", "RECORD-PROSE"),
        ("wiki/sources/foo.md", "RECORD-PROSE"),
        ("scripts/audit/x.py", "REVIEW"),
        ("skills/wiki-query/SKILL.md", "REVIEW"),
        ("CLAUDE.md", "REVIEW"),
        ("wiki/tracker/wayfinder-x.md", "REVIEW"),
        ("wiki/concepts/x.md", "REVIEW"),
        ("wiki/home/index.md", "EXCLUDED-TRUNK"),
        ("wiki/sensitive/sources/cfl/x.md", "EXCLUDED-TRUNK"),
        ("wiki/log-GATE-00.md", "RECORD-MACHINE"),
        ("wiki/README.md", "REVIEW"),
        ("totally/new/tree/x.md", "UNCLASSIFIED"),
    ]
    for p, want in cases:
        got = classify(p)[0]
        assert_(got == want, "classify(%-32s) -> %-15s (want %s)" % (p, got, want))

    assert_(classify("exchange/inbound/a.md")[0] == "RECORD-MACHINE",
            "exchange/inbound wins over the broad exchange/ rule (order matters)")

    with tempfile.TemporaryDirectory() as td:
        def g(*a):
            subprocess.run(["git", "-C", td, *a], capture_output=True, text=True, check=True)
        g("init", "-q")
        g("config", "user.email", "t@t")
        g("config", "user.name", "t")
        open(os.path.join(td, "README.txt"), "w").write("seed\n")
        g("add", "-A")
        g("commit", "-qm", "seed")
        base = subprocess.run(["git", "-C", td, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        os.makedirs(os.path.join(td, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(td, "wiki", "intake-triage"), exist_ok=True)
        open(os.path.join(td, "scripts", "a.py"), "w").write("x\ny\n")
        open(os.path.join(td, "wiki", "intake-triage", "b.json"), "w").write("lll\n" * 50)
        g("add", "-A")
        g("commit", "-qm", "clean")
        head = subprocess.run(["git", "-C", td, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        b = summarize(collect(td, base, head))
        assert_(totals(b, "REVIEW")[0] == 1, "clean fixture: REVIEW = 1 file")
        assert_(totals(b, "RECORD-MACHINE")[0] == 1, "clean fixture: RECORD-MACHINE = 1 file")
        assert_("UNCLASSIFIED" not in b, "clean fixture: no UNCLASSIFIED -> PASS path exercised")
        assert_("VERDICT: PASS" in render(b, base, head), "renderer prints PASS on the clean fixture")
        # NEW-vs-MODIFIED split. Planted because the first cut of this feature silently
        # reported 0/0 for both -- collect() had not been given the status map, summarize()
        # defaulted every row to "?", and NOTHING errored. A split that can read all-zero
        # must have a test that fails when it does.
        assert_(sum(e["new_files"] for e in b["REVIEW"].values()) == 1,
                "clean fixture: REVIEW NEW = 1 (a split that reads 0/0 must FAIL here)")
        assert_(sum(e["mod_files"] for e in b["REVIEW"].values()) == 0,
                "clean fixture: REVIEW MODIFIED = 0")
        open(os.path.join(td, "scripts", "a.py"), "a").write("modified\n")
        g("add", "-A")
        g("commit", "-qm", "modify the existing script")
        head3 = subprocess.run(["git", "-C", td, "rev-parse", "HEAD"],
                               capture_output=True, text=True).stdout.strip()
        b3 = summarize(collect(td, head, head3))
        assert_(sum(e["mod_files"] for e in b3["REVIEW"].values()) == 1,
                "modify-only fixture: REVIEW MODIFIED = 1 (M is distinguished from A)")
        assert_(sum(e["new_files"] for e in b3["REVIEW"].values()) == 0,
                "modify-only fixture: REVIEW NEW = 0")

        os.makedirs(os.path.join(td, "brand-new-tree"), exist_ok=True)
        open(os.path.join(td, "brand-new-tree", "c.md"), "w").write("z\n")
        g("add", "-A")
        g("commit", "-qm", "unclassified")
        head2 = subprocess.run(["git", "-C", td, "rev-parse", "HEAD"],
                               capture_output=True, text=True).stdout.strip()
        b2 = summarize(collect(td, base, head2))
        assert_("UNCLASSIFIED" in b2, "planted path is UNCLASSIFIED -> UNKNOWN path exercised")
        txt = render(b2, base, head2)
        assert_("VERDICT: UNKNOWN" in txt, "renderer prints UNKNOWN, not a quiet pass")
        assert_("brand-new-tree/c.md" in txt, "renderer NAMES the unclassified path")

    print("\nSELFTEST: %s" % ("PASS" if ok[0] else "FAIL"))
    return 0 if ok[0] else 1


def main():
    ap = argparse.ArgumentParser(description="partition a diff into REVIEW vs RECORD")
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
    ap.add_argument("--base", default=None)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--markdown", metavar="OUT.md", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    base = a.base or git(a.repo, "merge-base", "origin/main", a.head).strip()
    head = git(a.repo, "rev-parse", a.head).strip()
    rows = collect(a.repo, base, head)
    if not rows:
        print("UNKNOWN -- git reported zero changed files between %s and %s. "
              "That is not a clean diff; it is no measurement." % (base[:12], head[:12]))
        return 3
    b = summarize(rows)
    print(render(b, base, head))
    if a.markdown:
        with open(a.markdown, "w", encoding="utf-8") as f:
            f.write(render(b, base, head, markdown=True) + "\n")
        print("\nwrote %s" % a.markdown)
    return 3 if "UNCLASSIFIED" in b else 0


if __name__ == "__main__":
    sys.exit(main())
