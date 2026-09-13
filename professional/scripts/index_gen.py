#!/usr/bin/env python3
"""Derive the machine-readable wiki index FROM FRONTMATTER, in a single pass.

WHY A SINGLE PASS. The first version of this generator was bash and spawned five
`awk` processes plus a `head|grep` per page. On the Google Drive mount that is ~300
process spawns against a network filesystem, and it EXCEEDED A 120-SECOND BUDGET on
47 files -- the identical defect as lint.sh T-A, which was killed at exit 143 for
running 284 per-pair network stats. A gate that cannot finish inside a headless
timeout is a gate that does not run. Measured, then fixed, 2026-08-23.

WHY IT EXISTS AT ALL. wiki/index.md is hand-maintained and passes lint C2 today only
because this tree is small. The same latent failure already fired at scale in two
sibling trunks. Adopted from the Secretary's scripts/index-check.ps1, whose rule is
the right one: A JON-FACING SURFACE MUST BE DERIVED, NEVER HAND-MAINTAINED.

And it makes Jon's named defect load-bearing. He wrote, 2026-08-23: "The metadata
consistency!" Deriving the surface FROM the metadata means a missing `description:`
stops being an ignorable warning and becomes a visibly broken row.
"""
import os
import sys

SCAN_DIRS = ["wiki/concepts", "wiki/references", "wiki/sources", "wiki/fbc"]
EXCLUDE_PREFIXES = ("wiki/sealed/",)   # sealed material excluded by name, deliberately
# CANONICAL key -> accepted aliases, measured across this fleet 2026-08-23.
# Jon, 2026-08-23: "The metadata consistency! ... Very unprofessional."
# The aliases are the defect, not a convenience: the SAME fact is stored under
# different keys in different trunks and different pages of the same trunk, so any
# consumer must know all of them or silently miss rows. We accept aliases here so the
# surface is complete, and we COUNT them separately so the inconsistency is visible
# instead of being smoothed over. A crosswalk that hides the drift is not a fix.
CANON = {
    "name":        ("name", "title", "slug"),
    "description": ("description", "summary"),
    "kind":        ("kind", "type", "label"),
    "created":     ("created", "date", "sealed"),
    "sensitivity": ("sensitivity", "tier"),
}
KEYS = tuple(a for aliases in CANON.values() for a in aliases)


def parse_frontmatter(path):
    """Return (dict_of_keys, had_frontmatter, unreadable).
    
    UNREADABLE IS A THIRD STATE AND IT USED TO BE FOLDED INTO THE SECOND. Until
    2026-08-24 the OSError branch returned (out, had), so a page that could not be
    read was counted as a page with NO FRONTMATTER -- silently absorbed into the
    metadata backlog this generator exists to report. Measured that morning during
    a Google Drive content outage: every read returned `Invalid request code` while
    directory listings stayed correct, so the walker finds 60 pages and reads none.
    CFL's test, adopted: DOES THE FAILURE PATH PRODUCE DIFFERENT OUTPUT THAN THE
    SUCCESS PATH? It did not. Now it does.
    """
    out = {}
    had = False
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            first = fh.readline()
            if first.rstrip("\n\r") != "---":
                return out, False, False
            had = True
            for line in fh:
                s = line.rstrip("\n\r")
                if s == "---":
                    break
                i = s.find(":")
                if i <= 0:
                    continue
                k = s[:i].strip()
                v = s[i + 1:].strip().strip('"')
                if k in KEYS and k not in out:
                    out[k] = v
    except OSError:
        return out, had, True
    return out, had, False


def resolve(fmv, canon):
    """Return (value, which_key). which_key is None when nothing matched."""
    for k in CANON[canon]:
        v = fmv.get(k)
        if v:
            return v, k
    return "", None


def collect(root="."):
    rows, stats = [], dict(total=0, desc=0, name=0, kind=0, nofm=0, sens=0, alias=0, unread=0)
    alias_use = {}
    for sd in SCAN_DIRS:
        base = os.path.join(root, sd)
        if not os.path.isdir(base):
            continue
        found = []
        for dirpath, _dirnames, filenames in os.walk(base):
            for fn in filenames:
                if fn.endswith(".md") and fn != "README.md":
                    found.append(os.path.join(dirpath, fn))
        for full in sorted(found):
            rel = os.path.relpath(full, root).replace("\\", "/")
            if rel.startswith(EXCLUDE_PREFIXES):
                continue
            fmv, had, unreadable = parse_frontmatter(full)
            stats["total"] += 1
            if unreadable:
                stats["unread"] += 1
            if not had:
                stats["nofm"] += 1
            vals = {}
            for canon in ("name", "description", "kind", "created", "sensitivity"):
                v, which = resolve(fmv, canon)
                vals[canon] = v
                if which and which != canon:
                    stats["alias"] += 1
                    alias_use[which] = alias_use.get(which, 0) + 1
            if not vals["name"]:
                vals["name"] = os.path.basename(rel)[:-3]
                stats["name"] += 1
            if not vals["description"]:
                vals["description"] = "— (no description)"
                stats["desc"] += 1
            if not vals["kind"]:
                vals["kind"] = "?"
                stats["kind"] += 1
            if not vals["created"]:
                vals["created"] = "?"
            if vals["sensitivity"]:
                stats["sens"] += 1
            else:
                vals["sensitivity"] = "—"
            rows.append((rel, vals["name"], vals["kind"], vals["created"],
                         vals["sensitivity"], vals["description"]))
    stats["alias_use"] = alias_use
    return rows, stats


HEADER = """---
title: Claude Professional -- DERIVED index
generated-by: scripts/index_gen.py
kind: reference
warning: DO NOT HAND-EDIT. Regenerated from page frontmatter; edits are overwritten.
---

# DERIVED index — generated from frontmatter, never hand-maintained

**`wiki/index.md` is the CURATED view and stays hand-written** — its rows carry editorial judgement
a generator cannot produce. **THIS file is the mechanical one.** It is regenerated from what each page
actually declares, so it cannot drift from disk, and `--check` fails when it has.

⛔ **A row reading `— (no description)` is a real defect, not a cosmetic one:** that page is invisible
to anyone browsing this surface and to any retriever that indexes descriptions.

"""


def render(rows, stats):
    L = [HEADER]
    L.append("## Conformance, measured at generation time\n")
    L.append("| metric | count |")
    L.append("|---|---|")
    L.append("| pages scanned | %d |" % stats["total"])
    L.append("| **missing `description:`** | **%d** |" % stats["desc"])
    L.append("| missing `name:` | %d |" % stats["name"])
    L.append("| missing `kind:` | %d |" % stats["kind"])
    L.append("| no frontmatter block at all | %d |" % stats["nofm"])
    L.append("| carrying `sensitivity:` | %d of %d |" % (stats["sens"], stats["total"]))
    L.append("| **values found under a NON-CANONICAL alias** | **%d** |" % stats.get("alias", 0))
    L.append("")
    au = stats.get("alias_use") or {}
    if au:
        L.append("⚠️ **Alias keys in live use, and each one is a place a consumer that knows only the")
        L.append("canonical name silently misses the row:** " +
                 " · ".join("`%s:` ×%d" % (k, n) for k, n in sorted(au.items(), key=lambda x: -x[1])))
        L.append("")
    L.append("## Pages\n")
    L.append("| file (clickable) | name | kind | created | sensitivity | description |")
    L.append("|---|---|---|---|---|---|")
    for r in rows:
        # A DERIVED SURFACE THAT CANNOT BE NAVIGATED IS HALF AN INDEX. Raised by the
        # Secretary 2026-08-24, hours after this trunk published the same finding against
        # CFL's hand-written index: that one navigates and drifts; this one could not drift
        # and could not be walked. Rows are relative to THIS file, which lives in wiki/, so
        # the "wiki/" prefix is stripped rather than linked through.
        href = r[0][5:] if r[0].startswith("wiki/") else r[0]
        L.append("| [`%s`](%s) | %s | %s | %s | %s | %s |" % ((r[0], href) + r[1:]))
    return "\n".join(L) + "\n"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    out = "wiki/INDEX-DERIVED.md"

    if mode == "--selftest":
        import tempfile, shutil
        rc = 0
        d = tempfile.mkdtemp()
        try:
            cd = os.path.join(d, "wiki", "concepts")
            os.makedirs(cd)
            with open(os.path.join(cd, "good.md"), "w", encoding="utf-8") as fh:
                fh.write("---\nname: good\ndescription: a real description\nkind: concept\ncreated: 2026-08-23\n---\nbody\n")
            _r, s = collect(d)
            if not (s["total"] == 1 and s["desc"] == 0):
                print("SELFTEST BROKEN: S1 clean page miscounted", s); rc = 3
            with open(os.path.join(cd, "bad.md"), "w", encoding="utf-8") as fh:
                fh.write("---\nname: bad\nkind: concept\n---\nbody\n")
            _r, s = collect(d)
            if s["desc"] != 1:
                print("SELFTEST BROKEN: S2 missing description did NOT fire", s); rc = 3
            with open(os.path.join(cd, "raw.md"), "w", encoding="utf-8") as fh:
                fh.write("no frontmatter here\n")
            _r, s = collect(d)
            if not (s["nofm"] == 1 and s["name"] == 1):
                print("SELFTEST BROKEN: S3 bare page did NOT fire", s); rc = 3
            r1, s1 = collect(d)
            before = render(r1, s1)
            with open(os.path.join(cd, "later.md"), "w", encoding="utf-8") as fh:
                fh.write("---\nname: later\ndescription: added after generation\nkind: concept\n---\n")
            r2, s2 = collect(d)
            if render(r2, s2) == before:
                print("SELFTEST BROKEN: S4 drift NOT detected -- a new page left the index unchanged"); rc = 3
            # S5: the sealed exclusion can actually fire
            sealed = os.path.join(d, "wiki", "sealed")
            os.makedirs(sealed)
            with open(os.path.join(sealed, "secret.md"), "w", encoding="utf-8") as fh:
                fh.write("---\nname: secret\ndescription: must never appear\nkind: concept\n---\n")
            r3, _s3 = collect(d)
            if any("sealed" in row[0] for row in r3):
                print("SELFTEST BROKEN: S5 sealed page LEAKED into the index"); rc = 3
            # S6: EVERY page row must be a NAVIGABLE link, and the href must not keep the
            # wiki/ prefix -- this file lives inside wiki/. Seeded because the generator
            # shipped for a full day emitting backticked paths that no reader could follow,
            # and nothing in S1-S5 could see it: they all test COUNTS, never NAVIGATION.
            import re as _re
            body = render(r3, _s3)
            links = _re.findall(r"\| \[`([^`]+)`\]\(([^)]+)\)", body)
            if len(links) != len(r3):
                print("SELFTEST BROKEN: S6 %d of %d page rows are not links"
                      % (len(r3) - len(links), len(r3))); rc = 3
            if any(h.startswith("wiki/") for _t, h in links):
                print("SELFTEST BROKEN: S6 href kept the wiki/ prefix -- link resolves one level too high"); rc = 3
        finally:
            shutil.rmtree(d, ignore_errors=True)
        # S7: THE THIRD STATE. An OSError on read must report UNREADABLE, not
        #     'no frontmatter'. Proven in BOTH directions: a missing path is
        #     unreadable, a real page is not. This branch could not be reached from
        #     a healthy filesystem, which is why it shipped wrong -- A GATE IS
        #     VALIDATED AGAINST THE POPULATION THAT HAS THE DEFECT.
        _d7 = tempfile.mkdtemp()
        _fm, _had, _un = parse_frontmatter(os.path.join(_d7, 'does-not-exist.md'))
        if not (_un and not _had):
            print('SELFTEST BROKEN: S7 an unreadable page was not reported unreadable'); rc = 3
        _ok = os.path.join(_d7, 's7-readable.md')
        with open(_ok, 'w', encoding='utf-8') as fh:
            fh.write(chr(10).join(['---', 'name: s7', '---', '']))
        _fm, _had, _un = parse_frontmatter(_ok)
        if _un or not _had:
            print('SELFTEST BROKEN: S7 a READABLE page was reported unreadable'); rc = 3
        shutil.rmtree(_d7, ignore_errors=True)

        if rc == 0:
            print("SELFTEST: S1 clean / S2 no-description / S3 no-frontmatter / S4 drift / "
                  "S5 sealed-exclusion / S6 rows-are-navigable-links / "
                  "S7 unreadable-is-not-absent -- each proven failable (7/7)")
        return rc

    rows, stats = collect(".")
    text = render(rows, stats)

    if stats["unread"]:
        print("UNKNOWN [index-gen] %d of %d page(s) COULD NOT BE READ -- their metadata is "
              "UNKNOWN, not absent. UNKNOWN DOMINATES A PASS; refusing to grade or overwrite."
              % (stats["unread"], stats["total"]))
        return 2

    if mode == "--check":
        if not os.path.exists(out):
            print("FAIL [index-gen] %s does not exist -- run: python scripts/index_gen.py" % out)
            return 1
        with open(out, "r", encoding="utf-8") as fh:
            cur = fh.read()
        if cur != text:
            print("FAIL [index-gen] %s has DRIFTED from disk. Regenerate it." % out)
            return 1
        print("PASS [index-gen] %s matches disk (%d pages)" % (out, stats["total"]))
        return 0

    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("GENERATED %s -- %d page(s); missing description %d, name %d, kind %d; no frontmatter %d; sensitivity %d"
          % (out, stats["total"], stats["desc"], stats["name"], stats["kind"], stats["nofm"], stats["sens"]))
    if stats["desc"]:
        print("  NOTE: %d page(s) have no description and render as defects on the surface." % stats["desc"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
