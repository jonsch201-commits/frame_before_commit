#!/usr/bin/env python3
"""wiki_reachability.py -- is this page reachable from a root, by ANY path, through ANY link form?

⛔ THIS IS NOT THE MR-88 ORPHAN CENSUS AND DOES NOT CLAIM TO BE. That census is canonical, it lives
at `N:\\claude-personal\\scripts\\orphan_census.py`, and it asks a ONE-HOP question: is this page
referenced from a named hub (`wiki/index.md` or `wiki/concepts/**`). ⭐ **Run it, do not replace it.**
This file answers a DIFFERENT question because CFL's wiki has a different shape, and the shape was
measured rather than assumed.

⭐ WHY A DIFFERENT QUESTION, AND THE MEASUREMENT IS SOUL'S, NOT MINE. `[measured 2026-09-12 20:2x by
soul d7f7f45e (Claude Personal) over 3,058 of CFL's 3,159 wiki pages, with personal/, home/ and pro/
omitted per Jon's 2026-07-25 ruling]` inbound `[[refs]]` to `sources/` pages, by the top-level
directory doing the referring:

    sources 296 · intake-triage 252 · skills-gate 199 · concepts 13 · references 3 · tracker 1

⛔ **`concepts/` and `references/` together contribute 16 of 765 inbound refs — about 2%.** The
dominant hub is **sources citing sources, at 296**, and two of the three real hubs (`intake-triage`,
`skills-gate`) are directories CFL excludes as queue tier. ⭐ **So CFL's wiki is a FLAT CITATION WEB,
not hub-and-spoke.** A one-hop-from-a-named-hub question presumes hub-and-spoke and is close to
meaningless on a web: a page can be densely cited by its peers and still have no one-hop path from
any hub. Running the one-hop definition against CFL reports ~425 of 441 `sources/` pages orphaned,
and that number is almost entirely the hub set failing to transfer.

⛔ AND THE FIX SOUL REFUSED TO SHIP, WHICH IS WHY THIS FILE EXISTS AT ALL. They declined to add a
`--hub-set` parameter to their census, in their words: *"Handing you --hub-set would let you pick a
set that makes the number look reasonable, and a definition tuned until its output is comfortable is
the test calibrated to current behaviour. I would rather ship you nothing than that."* ⭐ **They were
right. A tunable hub set is a dial for making a number acceptable.** So the question changes instead:
**TRANSITIVE REACHABILITY from a small, declared, non-negotiable root set.**

✅ THE DEFINITION THIS FILE ENCODES, stated in full because a transferred definition is what went
wrong twice tonight:

  ROOT SET -- deliberately tiny and NOT a parameter you may widen to improve the number:
      wiki/index.md            (CLAUDE.md's mandated first lookup)
      every LIVE wayfinder map (frontmatter `kind: wayfinder:map` + `status: LIVE`) in wiki/tracker/
    ⚠️ tracker/ is EXCLUDED from the eligible pool and its LIVE maps are still ROOTS. That is not a
    contradiction: a register is not curated content, and it is still a door a reader is told to open.

  ELIGIBLE PAGE -- derived from two artifacts already ratified in THIS trunk, never from my judgment:
      the PREFIX_INCLUDE rows of scripts/audit/public_include_cfl.txt (CFL's published surface):
        patterns/ concepts/ references/ entities/ sources/ skills-gate/validation/
    EXCLUDED, each with the ratified reason:
      intake-triage/, archive/  -- QUEUE tier in build_index.py's tier_of(); operational packets, and
                                  the measured cost of treating them as content was severe
      tracker/                  -- registers (roots, not content; see above)
      personal/, home/, pro/    -- ⛔ JON-EXCLUDED, 2026-07-25 ruling. Surfaced, never acted on.
      everything else           -- UNKNOWN, not eligible: test-outputs/, sensitive/, sessions/,
                                  works/, methodology/, analyses/, transcripts/, root files.
                                  ⭐ An unnamed directory is UNKNOWN, never "fine".

  EDGE -- ANY of three forms, and counting only the first is how 313 became a CEILING:
      (1) `[[slug]]`  resolved by frontmatter `slug:` else filename stem
      (2) `[text](path.md)`  markdown link normalising under wiki/
      (3) a bare `wiki/...md` path mentioned in prose
    ⚠️ Soul's figure -- 128 of 441 `sources/` pages have >=1 inbound `[[ref]]`, so 313 have none -- is
    explicitly a CEILING on isolation because only form (1) was counted. This file counts all three
    and reports each form's contribution separately, so the drop between them IS the measurement of
    how much form (1) alone overstates isolation.

  REACHABLE = in the transitive closure of the root set over those edges, restricted to eligible
  pages plus the roots. UNREACHABLE = eligible and not in the closure.

⛔ WHAT THIS TOOL CANNOT TELL YOU, printed on every run: whether an unreachable page SHOULD be
reachable. A page can be correct, valuable, and cited by nothing. This measures reachability and
never worth, and a run is not a licence to delete or to link anything.

Exit: 0 always when it could measure; 4 if the wiki root is absent (a missing tree is NOT an empty
tree, which is Soul's rule from tonight and it is right).

Usage:
  python scripts/audit/wiki_reachability.py --selftest
  python scripts/audit/wiki_reachability.py
  python scripts/audit/wiki_reachability.py --wiki-root N:/claude-cfl/clone/wiki --list 40
"""
import glob
import os
import re
import sys

DEFAULT_WIKI = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "wiki")
ELIGIBLE_PREFIXES = ("patterns/", "concepts/", "references/", "entities/", "sources/",
                     "skills-gate/validation/")
EXCLUDED_QUEUE = ("intake-triage/", "archive/")
EXCLUDED_REGISTER = ("tracker/",)
EXCLUDED_JON = ("personal/", "home/", "pro/")
WIKILINK = re.compile(r"\[\[([^\]\|]+?)(?:\|[^\]]*)?\]\]")
MDLINK = re.compile(r"\[[^\]]*\]\(([^)\s]+\.md)\)")
BAREPATH = re.compile(r"(?<![\w/])((?:wiki/)?(?:[A-Za-z0-9_.\-]+/)+[A-Za-z0-9_.\-]+\.md)")
FM_SLUG = re.compile(r"^slug:\s*[\"']?([^\"'\n]+)", re.M)
FM_KIND = re.compile(r"^kind:\s*[\"']?([^\"'\n]+)", re.M)
FM_STATUS = re.compile(r"^status:\s*[\"']?([^\"'\n]+)", re.M)


def _out():
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass


def strip_code(text):
    """Fenced blocks out, inline backticks KEPT. ⛔ THE SECOND HALF IS A CORRECTION MADE 2026-09-12
    20:2x, ONE RUN AFTER THIS FILE WAS WRITTEN, AND IT IS THE NIGHT'S PATTERN ONE LEVEL DOWN.

    The rule I imported says syntax documentation is not a link: a 2026-08-07 rerun reported 57 "NEW"
    dangling refs of which ~47 were prose ABOUT the wikilink syntax. True -- and it was written about
    [[slug]] EXAMPLES. ⛔ I applied it to INLINE BACKTICKS TOO, and `[measured 20:21]` **CFL's
    wiki/index.md is 145,071 B with 545 table rows, ZERO [[wikilinks]], ZERO markdown links, and
    refers to every page as a BACKTICKED PATH.** So the guard deleted the one linking convention this
    wiki actually uses, and the first run reported 118 of 697 reachable from an index that resolved
    to ELEVEN outbound edges.
    ⭐ A guard imported to kill one false-positive family destroyed the true-positive family in this
    tree -- the same shape as every other finding tonight: a rule correct where it was written and
    wrong where it was carried.
    ✅ So: fences out (a fenced block is still documentation), inline backticks KEPT for PATH forms;
    [[slug]] extraction still runs over backtick-stripped text via strip_meta(), because the original
    2026-08-07 finding about [[slug]] examples stands."""
    return re.sub(r"```.*?```", " ", text, flags=re.S)


def strip_meta(text):
    """Fences AND inline backticks out -- ONLY for [[slug]] extraction, where a backticked [[slug]]
    really is documentation about the syntax."""
    return re.sub("`[^`" + chr(10) + "]*`", " ", strip_code(text))

META_EXAMPLES = {"slug", "wikilink", "source-slug-a", "source-slug-b", "name", "their-name"}


def load(wiki):
    pages = {}
    for p in glob.glob(os.path.join(wiki, "**", "*.md"), recursive=True):
        p = p.replace("\\", "/")
        rel = p.split("/wiki/", 1)[1] if "/wiki/" in p else os.path.basename(p)
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            t = ""
        fm = t[:t.find("---", 4)] if t.startswith("---") else ""
        m = FM_SLUG.search(fm)
        pages[rel] = {"text": t, "fm": fm,
                      "slug": (m.group(1).strip() if m else os.path.basename(rel)[:-3]),
                      "kind": (FM_KIND.search(fm).group(1).strip() if FM_KIND.search(fm) else ""),
                      "status": (FM_STATUS.search(fm).group(1).strip() if FM_STATUS.search(fm) else "")}
    return pages


def classify(rel):
    if rel.startswith(EXCLUDED_JON):
        return "jon-excluded"
    if rel.startswith(EXCLUDED_QUEUE):
        return "queue"
    if rel.startswith(EXCLUDED_REGISTER):
        return "register"
    if rel.startswith(ELIGIBLE_PREFIXES):
        return "eligible"
    return "unknown"


def roots_of(pages):
    r = ["index.md"] if "index.md" in pages else []
    for rel, p in pages.items():
        if rel.startswith("tracker/") and "wayfinder:map" in p["kind"] and "LIVE" in p["status"].upper():
            r.append(rel)
    return sorted(set(r))


def edges_from(rel, pages, slug_index, stem_index):
    """-> {target_rel: form}. Form is '[[slug]]', 'md-link', or 'bare-path'."""
    body = strip_code(pages[rel]["text"])      # fences out, backticked PATHS kept
    meta = strip_meta(pages[rel]["text"])      # backticks out too, for [[slug]] only
    out = {}
    for m in WIKILINK.finditer(meta):
        s = m.group(1).strip()
        if not s or s.lower() in META_EXAMPLES:
            continue
        tgt = slug_index.get(s) or stem_index.get(s)
        if tgt and tgt != rel:
            out.setdefault(tgt, "[[slug]]")
    for rx, form in ((MDLINK, "md-link"), (BAREPATH, "bare-path")):
        for m in rx.finditer(body):
            raw = m.group(1).replace("\\", "/").lstrip("./")
            cand = raw.split("wiki/", 1)[1] if raw.startswith("wiki/") else raw
            if cand in pages and cand != rel:
                out.setdefault(cand, form)
    return out


def run(wiki, listn=25):
    _out()
    if not os.path.isdir(wiki):
        print("⛔ REFUSED (exit 4): no wiki at %s. A MISSING TREE IS NOT AN EMPTY TREE." % wiki)
        return 4
    pages = load(wiki)
    slug_index, stem_index = {}, {}
    for rel, p in pages.items():
        slug_index.setdefault(p["slug"], rel)
        stem_index.setdefault(os.path.basename(rel)[:-3], rel)
    buckets = {}
    for rel in pages:
        buckets.setdefault(classify(rel), []).append(rel)
    roots = roots_of(pages)
    print("=== WIKI REACHABILITY -- transitive, three link forms, declared roots ===")
    print("  RESOLVED ROOT : %s" % wiki)
    print("                  %d *.md under it; cwd %s" % (len(pages), os.getcwd()))
    print("  ⛔ NOT the MR-88 orphan census. That one is one-hop-from-a-hub and lives in")
    print("     N:/claude-personal/scripts/orphan_census.py. Run it too; it answers a different thing.")
    print("  ROOT SET      : %d (index.md + LIVE wayfinder maps in tracker/)" % len(roots))
    for r in roots[:6]:
        print("                  %s" % r)
    if len(roots) > 6:
        print("                  ... and %d more" % (len(roots) - 6))
    print("  POOL          : eligible %d | queue %d | register %d | jon-excluded %d | UNKNOWN %d"
          % (len(buckets.get("eligible", [])), len(buckets.get("queue", [])),
             len(buckets.get("register", [])), len(buckets.get("jon-excluded", [])),
             len(buckets.get("unknown", []))))
    print("     eligible = the PREFIX_INCLUDE rows of public_include_cfl.txt; queue = tier_of()'s")
    print("     queue tier; jon-excluded = his 2026-07-25 ruling, surfaced never acted on; UNKNOWN")
    print("     is an unnamed directory and is NOT 'fine'.")
    # transitive closure
    allowed = set(buckets.get("eligible", [])) | set(roots)
    seen, form_used, frontier = set(roots), {}, list(roots)
    while frontier:
        cur = frontier.pop()
        for tgt, form in edges_from(cur, pages, slug_index, stem_index).items():
            if tgt in allowed and tgt not in seen:
                seen.add(tgt)
                form_used[tgt] = form
                frontier.append(tgt)
    elig = set(buckets.get("eligible", []))
    reach = sorted(elig & seen)
    unreach = sorted(elig - seen)
    by_form = {}
    for t in reach:
        by_form[form_used.get(t, "(root)")] = by_form.get(form_used.get(t, "(root)"), 0) + 1
    print("\n  REACHABLE     : %d of %d eligible" % (len(reach), len(elig)))
    print("  UNREACHABLE   : %d" % len(unreach))
    print("  first edge that reached each page, by form: %s" % (by_form or "{}"))
    print("  ⭐ THE FORM SPLIT IS THE POINT: counting only [[slug]] overstates isolation, which is why")
    print("     a 313-of-441 figure from wikilinks alone is a CEILING and never a count.")
    if unreach:
        print("\n  UNREACHABLE (first %d):" % min(listn, len(unreach)))
        for rel in unreach[:listn]:
            print("     %s" % rel)
        if len(unreach) > listn:
            print("     ... and %d more" % (len(unreach) - listn))
    print("\n  ⛔ THIS TOOL CANNOT TELL YOU WHETHER AN UNREACHABLE PAGE *SHOULD* BE REACHABLE.")
    print("     A page can be correct, valuable, and cited by nothing. This measures reachability,")
    print("     never worth, and a run is NOT a licence to delete or to link anything.")
    return 0


def selftest():
    _out()
    import tempfile
    ok = fail = 0

    def chk(name, cond):
        nonlocal ok, fail
        print(("PASS " if cond else "FAIL ") + name)
        if cond:
            ok += 1
        else:
            fail += 1

    tmp = tempfile.mkdtemp()
    w = os.path.join(tmp, "wiki")
    def mk(rel, body):
        p = os.path.join(w, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(body)
    mk("index.md", "# Index\n\n[[alpha]] and [beta](concepts/beta.md)\n")
    mk("concepts/alpha.md", "---\nslug: alpha\n---\n# A\n\nsee wiki/references/gamma.md\n")
    mk("concepts/beta.md", "# B\n")
    mk("references/gamma.md", "# G\n")
    mk("references/lonely.md", "# nobody links me\n")
    mk("references/fenced.md", "# f\n\n```\n[[lonely]]\n```\nand `[[lonely]]` inline\n")
    mk("tracker/wayfinder-x.md", "---\nkind: wayfinder:map\nstatus: \"LIVE\"\n---\n[[deep]]\n")
    mk("sources/deep.md", "---\nslug: deep\n---\n# D\n")
    mk("intake-triage/packet.md", "[[lonely]]\n")
    mk("personal/private.md", "[[lonely]]\n")
    pages = load(w)
    chk("classify: eligible / queue / register / jon-excluded / unknown all separate",
        classify("sources/deep.md") == "eligible" and classify("intake-triage/packet.md") == "queue"
        and classify("tracker/wayfinder-x.md") == "register"
        and classify("personal/private.md") == "jon-excluded" and classify("index.md") == "unknown")
    chk("a LIVE wayfinder map in tracker/ is a ROOT even though tracker/ is excluded from the pool",
        "tracker/wayfinder-x.md" in roots_of(pages) and "index.md" in roots_of(pages))
    si = {p["slug"]: r for r, p in pages.items()}
    st = {os.path.basename(r)[:-3]: r for r in pages}
    e = edges_from("index.md", pages, si, st)
    chk("both [[slug]] and md-link edges are found from one page",
        e.get("concepts/alpha.md") == "[[slug]]" and e.get("concepts/beta.md") == "md-link")
    chk("a bare wiki/ path in prose is an edge (form 3)",
        edges_from("concepts/alpha.md", pages, si, st).get("references/gamma.md") == "bare-path")
    chk("⛔ a [[ref]] inside a code fence or backticks is NOT an edge (negative arm)",
        edges_from("references/fenced.md", pages, si, st) == {})
    chk("⛔ a [[ref]] from a QUEUE page does not make a page reachable (negative arm)",
        "intake-triage/packet.md" not in roots_of(pages))
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = run(w, listn=5)
    out = buf.getvalue()
    chk("run() exits 0 and prints the resolved root and its count", rc == 0 and "RESOLVED ROOT" in out)
    chk("⛔ the reachable set excludes the page nothing links (negative arm)",
        "references/lonely.md" in out and "UNREACHABLE" in out)
    chk("a page reached only via a LIVE map root IS reachable (sources/deep.md)",
        "sources/deep.md" not in out.split("UNREACHABLE (first")[-1])
    chk("it states it is NOT the MR-88 census", "NOT the MR-88 orphan census" in out)
    chk("it states it cannot say whether a page SHOULD be reachable", "never worth" in out)
    miss = os.path.join(tmp, "nope")
    with contextlib.redirect_stdout(io.StringIO()):
        rc4 = run(miss)
    chk("⛔ a missing wiki REFUSES with exit 4, never an empty census (negative arm)", rc4 == 4)
    print("\n%d passed, %d failed" % (ok, fail))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    _w = DEFAULT_WIKI
    if "--wiki-root" in sys.argv:
        _w = sys.argv[sys.argv.index("--wiki-root") + 1].replace("\\", "/")
    _n = 25
    if "--list" in sys.argv:
        _n = int(sys.argv[sys.argv.index("--list") + 1])
    sys.exit(run(_w, _n))
