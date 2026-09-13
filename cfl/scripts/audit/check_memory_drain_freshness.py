#!/usr/bin/env python3
r"""Agent-memory DRAIN FRESHNESS check — does the wiki still hold every memory, and hold it current?

WHY THIS EXISTS
---------------
Jon's destination, verbatim, 2026-08-05 23:09:13 CDT:

    "make it so no memory files are actually needed because everything makes it into the wiki"

On 2026-08-06 that became TRUE — all 50 CFL agent-memory files were drained into `wiki/`
(48 to `wiki/references/agent-memory/`, 2 routed to `wiki/personal/`). **And it will silently
stop being true.** The Claude Code agent keeps writing new memory files into a store outside
git, and only a manual drain moves them. Nothing detected a memory that exists on disk with no
wiki page; nothing detected a memory that was drained and then *changed afterwards*.

That is this repo's single most-repeated defect — [[derive-dont-record]]: a fact captured once,
then drifting with nothing able to notice. It has already produced `RATIO_FLOOR`, `wiki.seeds`,
a stale local `main` that nearly republished a compliance violation, an index that lost two
memory files, and a gate header wrong by 6x. A one-time drain that nothing re-measures is the
same shape wearing a fresh costume. This script is the instrument that notices.

WHAT IT MEASURES
----------------
The link between a source memory file and its wiki page is the page's own `origin:` frontmatter
field, which records the absolute source path. **Matching is origin-driven, not path- or
filename-driven.** That matters for three reasons:

  1. The two files routed to `wiki/personal/` ARE drained. A check that only looked in
     `wiki/references/agent-memory/` would report them UNDRAINED and push a future session to
     re-drain family + financial content onto a connector-published surface. Because this scans
     all of `wiki/` and keys on `origin:`, they resolve correctly wherever they landed.
     (Regression-tested explicitly: selftest group 4.)
  2. Source filenames carry a `feedback_`/`project_`/`reference_` prefix the page drops, so
     filename-stripping would be a guess. `origin:` is a declaration.
  3. Only *frontmatter* `origin:` counts. Several `wiki/intake-triage/` agent-end extracts and
     `wiki/log.md` merely MENTION a memory path in their body text; a grep-based matcher would
     count them as drain pages. (Regression-tested: selftest group 5.)

Four states, each computed differently:

  UNDRAINED — a source memory file with no wiki page claiming it as `origin:`. A defect.
              Visibly absent, and the easy half.

  STALE     — the source changed AFTER it was drained, so the page looks drained and is wrong.
              The subtler and more valuable half. Computed two ways, of different strength:

              (a) DECLARED (strong, gating). Source frontmatter `metadata.modified:` (ISO-8601,
                  maintained by the memory subsystem itself) vs the page's `as_of:` field, which
                  records the source's `modified` value AT DRAIN TIME. If source `modified` is
                  later than page `as_of`, the fact moved after it was copied. This comparison is
                  filesystem-independent — no mtime, no clock skew, no Drive sync artifacts.
                  **Day-granular when `as_of` carries only a date** (36 of 48 pages record a bare
                  `YYYY-MM-DD`); comparing a bare date against a full timestamp would fire on
                  every same-day drain. That bug would have made this check cry wolf on ~75% of
                  the corpus on day one.

              (b) MTIME (advisory, non-gating by default). Source file mtime vs the page's last
                  git commit time (falling back to page mtime when untracked). Catches sources
                  with no `modified` field at all — 24 of 50 have none, so (a) is blind to
                  roughly half the store and (b) is the only cover they get. Advisory because
                  mtime is not a content signal: a no-op rewrite, a file copy, or a restore bumps
                  it, and a page recommitted for an unrelated typo looks freshly drained. Use
                  `--strict-mtime` to make it gate.

  ORPHANED  — a page in the drain directory whose `origin:` names a file no longer in the store.
              **Reported as INFO, not scored as a defect.** Sources are never deleted by this
              program (NO DESTRUCTIVE ACTS), so an orphan most likely means a memory was renamed
              or the page was drained from the other store. It is worth seeing, not worth failing.

THE SPLIT STORE — and why the denominator is printed
-----------------------------------------------------
There are TWO CFL memory directories, keyed by launch working directory (see
`wiki/references/agent-memory/cfl-memory-store-split-by-cwd.md`): the repo-folder store (current)
and the parent Drive-folder store (stale to early June, still asserts "Phase 3c running"). Nothing
in the UI tells a session which one it loaded. So this script **names the store it measured in
every report**, and additionally discovers and lists sibling stores WITHOUT scoring them — their
files are not counted as UNDRAINED, because draining the stale store has never been ratified.
This repo's own phrasing: *a count without its denominator is a rumour with a number attached.*

USAGE
    python scripts/audit/check_memory_drain_freshness.py
    python scripts/audit/check_memory_drain_freshness.py --strict-mtime
    python scripts/audit/check_memory_drain_freshness.py --selftest

Exit codes: 0 clean · 1 defects found (UNDRAINED, or DECLARED-STALE, or MTIME-stale under
--strict-mtime) · 2 error (store or wiki not found).

READ-ONLY. This script never writes to, moves, or deletes a source memory file.

SU WIRING — WRITTEN BUT NOT APPLIED (2026-08-06)
------------------------------------------------
`scripts/audit/su_close.sh` was dirty in the working tree while this check was built (another
agent held it), so the row below was NOT inserted. An instrument nobody runs is this repo's other
most-repeated defect, so this is a debt, not a completion — apply it as soon as the file is free.

Insert after the `stranded_branches.py` block (near line 1265, before the CHANNELS section), which
this matches in shape — `record <id> <TIER> <mode> <value> <denominator> <rc> "<note>"`, values
scraped with `num` from the instrument's own stdout:

    MDF="$REPO/scripts/audit/check_memory_drain_freshness.py"
    if [ -f "$MDF" ]; then
      rc=$(run "$OUT/memdrain.out" "$PY" "$MDF")
      mtot=$(num "$OUT/memdrain.out" 'sources measured +: ([0-9]+)')
      mund=$(num "$OUT/memdrain.out" 'UNDRAINED +: ([0-9]+)')
      mstl=$(num "$OUT/memdrain.out" 'STALE \(declared\) +: ([0-9]+)')
      mmt=$(num  "$OUT/memdrain.out" 'STALE \(mtime advisory\) +: ([0-9]+)')
      mgap=$(num "$OUT/memdrain.out" 'AS_OF GAP +: ([0-9]+)')
      record memory.undrained LOSS     zero "$mund" "$mtot" "$rc" \
        "memory files with no wiki page — Jon's destination is false while nonzero"
      record memory.stale     LOSS     zero "$mstl" "$mtot" "$rc" \
        "source changed AFTER it was drained — the page looks drained and is wrong"
      record memory.mtime     ADVISORY zero "$mmt"  "$mtot" "$rc" \
        "source file newer than its page (weak signal; confirm by diff before re-draining)"
      record memory.asofgap   ADVISORY zero "$mgap" "$mtot" "$rc" \
        "page claims its source is undated when the source carries a modified timestamp"
    else
      record memory.undrained LOSS     zero "" "" 2 "check_memory_drain_freshness.py not found"
      record memory.stale     LOSS     zero "" "" 2 "check_memory_drain_freshness.py not found"
    fi

Denominator is `sources measured`, so the row can never read 0/0 — a 0/0 row is scored UNKNOWN by
`classify`, never a pass, which is the correct treatment if the store ever goes missing.
"""
import argparse
import datetime as dt
import glob
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

PROJECTS_ROOT = r"C:\Users\JonSc\.claude\projects"
CFL_STORE = os.path.join(
    PROJECTS_ROOT,
    "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer",
    "memory",
)
# Sibling CFL-keyed stores. Discovered by glob too, but named here so a store that disappears
# is itself visible rather than silently dropping out of the report.
KNOWN_SIBLING_STORES = [
    os.path.join(PROJECTS_ROOT, "G--My-Drive-Claude-Claude-Foundational-Layer", "memory"),
]

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

DRAIN_DIR_REL = "wiki/references/agent-memory"

# Leading date or ISO timestamp of an `as_of:` value, e.g.
#   "2026-07-26 (memory `modified` timestamp)"      -> date only, day-granular
#   "2026-07-28T22:18:47.044Z (source `modified`)"  -> full timestamp
#   "undated (source has no `modified` field)"      -> no match, treated as undeclared
AS_OF_RE = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}:\d{2}(?:\.\d+)?))?")


def _mtime(path):
    """Naive-UTC mtime. (utcfromtimestamp is deprecated in 3.12+ and its warning would pollute
    the SU transcript, where noise is how a row stops being read.)"""
    return dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc).replace(tzinfo=None)


def norm(p):
    """Normalize a path for comparison: forward slashes, lowercase, no trailing slash.

    Origin fields are Windows absolute paths with backslashes; os.path.join on the store gives
    the same shape. Case-insensitive because Windows is.
    """
    return os.path.normpath(str(p)).replace("\\", "/").rstrip("/").lower()


def parse_frontmatter(text):
    """Return {key: value} for a leading `---` fenced YAML-ish block.

    Deliberately line-based rather than PyYAML: no dependency, and these files are hand-written
    with occasional formatting that a strict parser rejects. Handles two shapes that appear in
    the real corpus:
      - top-level `key: value`, with folded continuation lines (indented, no colon-key of their own)
      - a nested `metadata:` block whose children are indented `key: value` -> "metadata.key"
    Returns {} when there is no frontmatter at all.
    """
    if not text.startswith("---"):
        return {}
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return {}
    body = []
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        body.append(ln)
    else:
        return {}  # unterminated fence -> not frontmatter

    out = {}
    cur_key = None
    in_metadata = False
    for ln in body:
        if not ln.strip():
            continue
        m_top = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*):\s?(.*)$", ln)
        m_sub = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_\-]*):\s?(.*)$", ln)
        if m_top:
            key, val = m_top.group(1), m_top.group(2).strip()
            in_metadata = key == "metadata" and val == ""
            out[key] = val
            cur_key = key
        elif m_sub and in_metadata:
            out["metadata." + m_sub.group(1)] = m_sub.group(2).strip()
            cur_key = "metadata." + m_sub.group(1)
        elif cur_key and ln.startswith((" ", "\t")):
            # folded continuation of the previous scalar
            out[cur_key] = (out[cur_key] + " " + ln.strip()).strip()
    return out


def parse_iso(s):
    """Parse an ISO-8601 timestamp to a naive UTC datetime. Returns None on anything unparseable."""
    if not s:
        return None
    s = str(s).strip().strip("\"'")
    m = re.match(r"^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})(?:\.(\d+))?\s*(Z|[+-]\d{2}:?\d{2})?", s)
    if not m:
        m2 = re.match(r"^(\d{4}-\d{2}-\d{2})$", s)
        if m2:
            return dt.datetime.strptime(m2.group(1), "%Y-%m-%d")
        return None
    base = dt.datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S")
    tz = m.group(4)
    if tz and tz not in ("Z",):
        tz = tz.replace(":", "")
        sign = 1 if tz[0] == "+" else -1
        base -= sign * dt.timedelta(hours=int(tz[1:3]), minutes=int(tz[3:5]))
    return base


def parse_as_of(s):
    """Return (datetime, day_granular_bool) for an `as_of:` value, or (None, None)."""
    if not s:
        return None, None
    m = AS_OF_RE.match(str(s).strip().strip("\"'"))
    if not m:
        return None, None  # e.g. "undated (source has no `modified` field)"
    if m.group(2):
        return dt.datetime.strptime(m.group(1) + " " + m.group(2)[:8], "%Y-%m-%d %H:%M:%S"), False
    return dt.datetime.strptime(m.group(1), "%Y-%m-%d"), True


def git_last_commit_times(repo_root, rel_paths_root):
    """Map normalized abs path -> datetime of the most recent commit touching it.

    One `git log` walk rather than one call per file: 50+ subprocess spawns against a
    Google-Drive-backed repo is slow enough that a future session would be tempted to skip
    running this at all.
    """
    times = {}
    try:
        p = subprocess.run(
            ["git", "-C", repo_root, "log", "--pretty=format:__C__%cI", "--name-only", "--", rel_paths_root],
            capture_output=True, text=True, timeout=180,
        )
        if p.returncode != 0:
            return times
        cur = None
        for ln in p.stdout.split("\n"):
            ln = ln.rstrip()
            if ln.startswith("__C__"):
                cur = parse_iso(ln[5:])
            elif ln and cur is not None:
                key = norm(os.path.join(repo_root, ln))
                if key not in times:  # log is newest-first; first sighting wins
                    times[key] = cur
    except Exception:
        pass
    return times


def load_sources(memory_dir):
    """Enumerate source memory files. MEMORY.md is the index, not a memory — excluded."""
    out = {}
    for fn in sorted(os.listdir(memory_dir)):
        if not fn.endswith(".md") or fn == "MEMORY.md":
            continue
        full = os.path.join(memory_dir, fn)
        if not os.path.isfile(full):
            continue
        try:
            with open(full, encoding="utf-8", errors="ignore") as f:
                fm = parse_frontmatter(f.read())
        except OSError:
            fm = {}
        out[norm(full)] = {
            "name": fn,
            "path": full,
            "mtime": _mtime(full),
            "modified": parse_iso(fm.get("metadata.modified")),
        }
    return out


def load_wiki_pages(wiki_root, repo_root):
    """Every wiki page declaring a frontmatter `origin:`. Body mentions do not count."""
    pages = []
    for dirpath, _dirnames, filenames in os.walk(wiki_root):
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            full = os.path.join(dirpath, fn)
            try:
                with open(full, encoding="utf-8", errors="ignore") as f:
                    head = f.read(8192)
            except OSError:
                continue
            fm = parse_frontmatter(head)
            origin = fm.get("origin")
            if not origin:
                continue
            pages.append({
                "path": full,
                "rel": os.path.relpath(full, repo_root).replace("\\", "/"),
                "origin_raw": origin,
                "origin": norm(origin),
                "as_of_raw": fm.get("as_of", ""),
                "mtime": _mtime(full),
            })
    return pages


def discover_sibling_stores(measured_dir):
    found = []
    seen = {norm(measured_dir)}
    cands = list(KNOWN_SIBLING_STORES)
    cands += glob.glob(os.path.join(PROJECTS_ROOT, "*Foundational-Layer*", "memory"))
    cands += glob.glob(os.path.join(PROJECTS_ROOT, "*Claude-Personal*", "memory"))
    for c in cands:
        if norm(c) in seen:
            continue
        seen.add(norm(c))
        if os.path.isdir(c):
            n = len([f for f in os.listdir(c) if f.endswith(".md") and f != "MEMORY.md"])
            newest = None
            for f in os.listdir(c):
                if f.endswith(".md"):
                    t = _mtime(os.path.join(c, f))
                    newest = t if newest is None or t > newest else newest
            found.append({"path": c, "count": n, "newest": newest})
        else:
            found.append({"path": c, "count": None, "newest": None})
    return found


def scan(memory_dir, wiki_root, repo_root, use_git=True):
    if not os.path.isdir(memory_dir):
        print(f"ERROR: memory dir not found: {memory_dir}", file=sys.stderr)
        return None
    if not os.path.isdir(wiki_root):
        print(f"ERROR: wiki root not found: {wiki_root}", file=sys.stderr)
        return None

    sources = load_sources(memory_dir)
    pages = load_wiki_pages(wiki_root, repo_root)
    git_times = git_last_commit_times(repo_root, os.path.relpath(wiki_root, repo_root)) if use_git else {}

    by_origin = {}
    for pg in pages:
        by_origin.setdefault(pg["origin"], []).append(pg)

    drain_dir_abs = norm(os.path.join(repo_root, DRAIN_DIR_REL))

    undrained, drained, declared_stale, mtime_stale, as_of_gap, duplicates = [], [], [], [], [], []

    for key, src in sorted(sources.items(), key=lambda kv: kv[1]["name"]):
        matches = by_origin.get(key, [])
        if not matches:
            undrained.append(src)
            continue
        drained.append(src)
        if len(matches) > 1:
            duplicates.append((src, [m["rel"] for m in matches]))

        # Best page = the one that looks freshest, so a source is only called stale when EVERY
        # page claiming it is behind. Otherwise a duplicate page would manufacture a false stale.
        best_declared = None
        for pg in matches:
            a, day = parse_as_of(pg["as_of_raw"])
            if a and (best_declared is None or a > best_declared[0]):
                best_declared = (a, day, pg)

        if src["modified"]:
            if best_declared:
                a, day, pg = best_declared
                if day:
                    if src["modified"].date() > a.date():
                        declared_stale.append((src, pg, a, True))
                elif src["modified"] > a:
                    declared_stale.append((src, pg, a, False))
            else:
                # Page says "undated" but the source DOES carry `modified`. Two causes, and they
                # are distinguishable: compare the source's `modified` against when the page was
                # last committed. If `modified` predates the page, the field was sitting there at
                # drain time and the drain misread it -> the page states a falsehood about its own
                # source, and the strong staleness check above is disabled on that page forever.
                # If `modified` postdates the page, the memory was rewritten after being drained
                # -> genuinely stale, by the same logic as the mtime signal.
                pg0 = matches[0]
                pgt = None
                for pg in matches:
                    t = git_times.get(norm(pg["path"]), pg["mtime"])
                    pgt = t if pgt is None or t > pgt else pgt
                cause = "gained-after-drain" if (pgt and src["modified"] > pgt) else "misread-at-drain"
                as_of_gap.append((src, pg0, cause, pgt))

        page_time = None
        for pg in matches:
            t = git_times.get(norm(pg["path"]), pg["mtime"])
            page_time = t if page_time is None or t > page_time else page_time
        if page_time is not None and src["mtime"] > page_time:
            mtime_stale.append((src, page_time, matches[0]))

    orphaned = []
    for pg in pages:
        if not norm(os.path.dirname(pg["path"])).startswith(drain_dir_abs):
            continue
        if pg["origin"] in sources:
            continue
        in_sibling = os.path.isfile(pg["origin_raw"])
        orphaned.append((pg, in_sibling))

    return {
        "memory_dir": memory_dir,
        "wiki_root": wiki_root,
        "sources_total": len(sources),
        "pages_with_origin": len(pages),
        "pages_matching_store": len({p["origin"] for p in pages if p["origin"] in sources}),
        "drained": drained,
        "undrained": undrained,
        "declared_stale": declared_stale,
        "mtime_stale": mtime_stale,
        "as_of_gap": as_of_gap,
        "duplicates": duplicates,
        "orphaned": orphaned,
        "siblings": discover_sibling_stores(memory_dir),
        "used_git": bool(git_times),
        "sources_with_modified": sum(1 for s in sources.values() if s["modified"]),
    }


def report(r, strict_mtime):
    W = 94
    print("=" * W)
    print("AGENT-MEMORY DRAIN FRESHNESS CHECK")
    print("=" * W)
    print("  Destination (Jon, 2026-08-05): \"make it so no memory files are actually needed")
    print("  because everything makes it into the wiki\"")
    print()
    print("  STORE MEASURED          : " + r["memory_dir"])
    print("  wiki root               : " + r["wiki_root"])
    print(f"  page timestamps from    : {'git last-commit time' if r['used_git'] else 'file mtime (git unavailable)'}")
    print()
    print("  -- DENOMINATOR ------------------------------------------------------------------")
    print(f"  sources measured        : {r['sources_total']}   (*.md in the store, excluding MEMORY.md)")
    print(f"  ...with `modified` field: {r['sources_with_modified']}   (only these can be checked for DECLARED staleness)")
    print(f"  wiki pages w/ `origin:`  : {r['pages_with_origin']}   (any origin value; most name a session, not a path)")
    print(f"  ...resolving to this store: {r['pages_matching_store']}   <- the number that matters")
    print()

    if r["siblings"]:
        print("  -- SIBLING STORES (reported, NOT measured, NOT scored) ---------------------------")
        print("     Memory is keyed by launch cwd; draining these has never been ratified.")
        for s in r["siblings"]:
            if s["count"] is None:
                print(f"     - {s['path']}  [ABSENT]")
            else:
                nw = s["newest"].strftime("%Y-%m-%d") if s["newest"] else "?"
                print(f"     - {s['path']}")
                print(f"         {s['count']} memory files, newest {nw}")
        print()

    print("  -- RESULTS -----------------------------------------------------------------------")
    print(f"  DRAINED                 : {len(r['drained'])} / {r['sources_total']}")
    print(f"  UNDRAINED               : {len(r['undrained'])}")
    print(f"  STALE (declared)        : {len(r['declared_stale'])}")
    print(f"  STALE (mtime advisory)  : {len(r['mtime_stale'])}")
    print(f"  AS_OF GAP               : {len(r['as_of_gap'])}")
    print(f"  ORPHANED pages (info)   : {len(r['orphaned'])}")
    print(f"  DUPLICATE pages         : {len(r['duplicates'])}")
    print()

    if r["undrained"]:
        print(f"  UNDRAINED — on disk, no wiki page claims it as `origin:` ({len(r['undrained'])}):")
        print("    A memory the wiki does not hold. Jon's destination is false while this is nonzero.")
        for s in r["undrained"]:
            print(f"    - {s['name']}   (mtime {s['mtime'].strftime('%Y-%m-%d')})")
        print()

    if r["declared_stale"]:
        print(f"  STALE (declared) — source changed AFTER it was drained ({len(r['declared_stale'])}):")
        print("    The page looks drained and is wrong. Re-drain these.")
        for s, pg, a, day in r["declared_stale"]:
            g = "day-granular" if day else "exact"
            print(f"    - {s['name']}")
            print(f"        source modified : {s['modified'].isoformat()}")
            print(f"        page as_of      : {a.isoformat()}  ({g})")
            print(f"        page            : {pg['rel']}")
        print()

    if r["mtime_stale"]:
        print(f"  STALE (mtime, advisory) — source file newer than its page ({len(r['mtime_stale'])}):")
        print("    Weaker signal: mtime moves on no-op rewrites, copies and restores. Confirm by")
        print("    diffing the source against the page before re-draining.")
        for s, pt, pg in r["mtime_stale"]:
            print(f"    - {s['name']}")
            print(f"        source mtime : {s['mtime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"        page updated : {pt.strftime('%Y-%m-%d %H:%M:%S')}   ({pg['rel']})")
        print()

    if r["as_of_gap"]:
        misread = [x for x in r["as_of_gap"] if x[2] == "misread-at-drain"]
        gained = [x for x in r["as_of_gap"] if x[2] == "gained-after-drain"]
        print(f"  AS_OF GAP — page says \"source has no `modified` field\"; the source has one ({len(r['as_of_gap'])}):")
        if misread:
            print(f"    [misread-at-drain] {len(misread)} — the field predates the page, so it WAS there")
            print("    at drain time. The page states a falsehood about its own source, and the strong")
            print("    DECLARED-staleness check is disabled on it. Fix: re-derive as_of from the source.")
            for s, pg, _c, _t in misread:
                print(f"      - {s['name']}  (modified {s['modified'].isoformat()})  ->  {pg['rel']}")
        if gained:
            print(f"    [gained-after-drain] {len(gained)} — `modified` POSTDATES the page: the memory was")
            print("    rewritten after it was drained. Treat as stale and re-drain.")
            for s, pg, _c, t in gained:
                ts = t.strftime("%Y-%m-%d %H:%M:%S") if t else "?"
                print(f"      - {s['name']}  (modified {s['modified'].isoformat()} > page {ts})  ->  {pg['rel']}")
        print()

    if r["duplicates"]:
        print(f"  DUPLICATE — one source claimed by several pages ({len(r['duplicates'])}):")
        for s, rels in r["duplicates"]:
            print(f"    - {s['name']}  ->  {', '.join(rels)}")
        print()

    if r["orphaned"]:
        print(f"  ORPHANED (INFO — not scored as a defect) ({len(r['orphaned'])}):")
        print("    A drain page whose source is not in the measured store. Sources are never")
        print("    deleted by this program, so this most likely means a rename, or a page drained")
        print("    from the other store. Worth seeing; not a failure.")
        for pg, in_sib in r["orphaned"]:
            where = "source exists elsewhere on disk" if in_sib else "source not found anywhere"
            print(f"    - {pg['rel']}")
            print(f"        origin: {pg['origin_raw']}  [{where}]")
        print()

    fail = bool(r["undrained"]) or bool(r["declared_stale"])
    if strict_mtime and r["mtime_stale"]:
        fail = True

    if fail:
        print("RESULT: FAIL — the wiki no longer holds the memory store completely and currently.")
        return 1
    if r["mtime_stale"] or r["as_of_gap"]:
        print("RESULT: PASS (with advisories) — every memory is drained; see advisories above.")
        return 0
    print("RESULT: PASS — every memory file is drained, and none has changed since it was drained.")
    return 0


# ---------------------------------------------------------------------------------------------
# SELFTEST — a check only ever observed reporting "all clear" has not been tested.
# Every group below builds a throwaway fixture tree in the OS temp dir and asserts the state
# actually fires. Nothing here touches the real store or the real wiki.
# ---------------------------------------------------------------------------------------------
def _w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _src(name, modified=None, body="content"):
    md = f"  modified: {modified}\n" if modified else ""
    return f"---\nname: {name}\ndescription: \"x\"\nmetadata:\n  node_type: memory\n  type: feedback\n{md}---\n\n{body}\n"


def _page(origin, as_of="undated (source has no `modified` field)"):
    return f"---\ntitle: t\nsource_kind: reference\norigin: {origin}\nas_of: {as_of}\n---\n\n# t\n\nbody\n"


def selftest():
    import shutil
    import tempfile
    import time

    fails = []
    tmp = tempfile.mkdtemp(prefix="drain-freshness-selftest-")
    try:
        mem = os.path.join(tmp, "memory")
        repo = os.path.join(tmp, "repo")
        wiki = os.path.join(repo, "wiki")
        drain = os.path.join(repo, DRAIN_DIR_REL.replace("/", os.sep))
        personal = os.path.join(wiki, "personal")
        os.makedirs(mem)
        os.makedirs(drain)
        os.makedirs(personal)

        # --- group 1: clean drained pair (must NOT be flagged anything)
        _w(os.path.join(mem, "feedback_clean.md"), _src("clean", "2026-07-01T10:00:00.000Z"))
        _w(os.path.join(drain, "clean.md"),
           _page(os.path.join(mem, "feedback_clean.md"), "2026-07-01 (memory `modified` timestamp)"))

        # --- group 2: UNDRAINED — source with no page anywhere
        _w(os.path.join(mem, "feedback_undrained.md"), _src("undrained", "2026-07-02T10:00:00.000Z"))

        # --- group 3: DECLARED STALE — source modified AFTER the page's as_of
        _w(os.path.join(mem, "feedback_stale.md"), _src("stale", "2026-08-05T09:00:00.000Z"))
        _w(os.path.join(drain, "stale.md"),
           _page(os.path.join(mem, "feedback_stale.md"), "2026-07-01 (memory `modified` timestamp)"))

        # --- group 4: THE wiki/personal ROUTING TEST. Drained, but NOT in the drain dir.
        # Must count as DRAINED, must NOT appear in undrained. This is the regression that would
        # otherwise push a session to re-drain family content onto a published surface.
        _w(os.path.join(mem, "feedback_personal_routed.md"), _src("routed", "2026-07-03T10:00:00.000Z"))
        _w(os.path.join(personal, "routed.md"),
           _page(os.path.join(mem, "feedback_personal_routed.md"), "2026-07-03 (memory `modified` timestamp)"))

        # --- group 5: BODY-MENTION DECOY. Mentions a memory path in prose, no frontmatter origin.
        # Must NOT be treated as a drain page -> its source must still read UNDRAINED.
        _w(os.path.join(mem, "feedback_decoy.md"), _src("decoy", "2026-07-04T10:00:00.000Z"))
        _w(os.path.join(wiki, "log.md"),
           "# Log\n\nWe drained " + os.path.join(mem, "feedback_decoy.md") + " today.\n")

        # --- group 6: ORPHAN — page in drain dir whose source does not exist
        _w(os.path.join(drain, "orphan.md"), _page(os.path.join(mem, "feedback_ghost.md")))

        # --- group 7: DAY-GRANULAR GUARD. Source modified 19:35 on the SAME DAY as a bare-date
        # as_of. Must NOT be stale — this is the false-positive that would have hit ~75% of pages.
        _w(os.path.join(mem, "feedback_sameday.md"), _src("sameday", "2026-07-26T19:35:27.074Z"))
        _w(os.path.join(drain, "sameday.md"),
           _page(os.path.join(mem, "feedback_sameday.md"), "2026-07-26 (memory `modified` timestamp)"))

        # --- group 8: AS_OF GAP — source dated, page says undated
        _w(os.path.join(mem, "feedback_gap.md"), _src("gap", "2026-07-05T10:00:00.000Z"))
        _w(os.path.join(drain, "gap.md"), _page(os.path.join(mem, "feedback_gap.md")))

        # --- group 9: MTIME STALE — no `modified` field at all, source touched after the page
        _w(os.path.join(drain, "mtimestale.md"), _page(os.path.join(mem, "feedback_mtimestale.md")))
        time.sleep(1.1)
        _w(os.path.join(mem, "feedback_mtimestale.md"), _src("mtimestale", None))

        # MEMORY.md must be excluded from the denominator
        _w(os.path.join(mem, "MEMORY.md"), "# Memory Index\n- [x](feedback_clean.md)\n")

        r = scan(mem, wiki, repo, use_git=False)
        if r is None:
            print("FAIL: scan returned None")
            return 1

        names = lambda lst: sorted(s["name"] for s in lst)
        und = names(r["undrained"])
        if und != ["feedback_decoy.md", "feedback_undrained.md"]:
            fails.append(f"G2/G5 FAIL undrained: got {und}")

        ds = sorted(s["name"] for s, _, _, _ in r["declared_stale"])
        if ds != ["feedback_stale.md"]:
            fails.append(f"G3/G7 FAIL declared_stale: got {ds} (want only feedback_stale.md)")

        drained_names = names(r["drained"])
        if "feedback_personal_routed.md" not in drained_names:
            fails.append("G4 FAIL: wiki/personal-routed source not counted as DRAINED")
        if "feedback_personal_routed.md" in und:
            fails.append("G4 FAIL: wiki/personal-routed source wrongly reported UNDRAINED")

        orph = sorted(os.path.basename(pg["path"]) for pg, _ in r["orphaned"])
        if orph != ["orphan.md"]:
            fails.append(f"G6 FAIL orphaned: got {orph}")

        gap = sorted(s["name"] for s, _, _, _ in r["as_of_gap"])
        if gap != ["feedback_gap.md"]:
            fails.append(f"G8 FAIL as_of_gap: got {gap}")

        ms = sorted(s["name"] for s, _, _ in r["mtime_stale"])
        if "feedback_mtimestale.md" not in ms:
            fails.append(f"G9 FAIL mtime_stale did not fire: got {ms}")

        if r["sources_total"] != 8:
            fails.append(f"G0 FAIL sources_total: got {r['sources_total']} want 8 (MEMORY.md excluded)")

        # --- group 10: exit code must be 1 when defects exist, 0 on a clean tree
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_dirty = report(r, strict_mtime=False)
        if rc_dirty != 1:
            fails.append(f"G10 FAIL: dirty tree exit code {rc_dirty}, want 1")

        mem2 = os.path.join(tmp, "memory_clean")
        repo2 = os.path.join(tmp, "repo_clean")
        wiki2 = os.path.join(repo2, "wiki")
        drain2 = os.path.join(repo2, DRAIN_DIR_REL.replace("/", os.sep))
        os.makedirs(mem2)
        os.makedirs(drain2)
        _w(os.path.join(mem2, "feedback_ok.md"), _src("ok", "2026-07-01T10:00:00.000Z"))
        time.sleep(1.1)
        _w(os.path.join(drain2, "ok.md"),
           _page(os.path.join(mem2, "feedback_ok.md"), "2026-07-01 (memory `modified` timestamp)"))
        r2 = scan(mem2, wiki2, repo2, use_git=False)
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2):
            rc_clean = report(r2, strict_mtime=False)
        if rc_clean != 0:
            fails.append(f"G10 FAIL: clean tree exit code {rc_clean}, want 0\n{buf2.getvalue()}")

        # --- group 11: frontmatter parser must ignore an unterminated fence
        if parse_frontmatter("---\norigin: x\nno closing fence\n") != {}:
            fails.append("G11 FAIL: unterminated frontmatter fence parsed as frontmatter")
        if parse_frontmatter("no frontmatter here") != {}:
            fails.append("G11 FAIL: bare text parsed as frontmatter")

        # --- group 12: as_of parser shapes seen in the real corpus
        if parse_as_of("undated (source has no `modified` field)") != (None, None):
            fails.append("G12 FAIL: 'undated' should yield no as_of")
        d, day = parse_as_of("2026-07-28T22:18:47.044Z (source `modified` field)")
        if day is not False or d is None:
            fails.append(f"G12 FAIL: full-timestamp as_of mis-parsed: {d} {day}")
        d, day = parse_as_of("2026-08-06 (memory `modified` timestamp; two instances)")
        if day is not True or d is None:
            fails.append(f"G12 FAIL: date-only as_of mis-parsed: {d} {day}")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print(f)
    if fails:
        print(f"\nSELFTEST: {len(fails)} failure(s)")
        return 1
    print("SELFTEST: 12/12 groups passed")
    print("  proved firing: UNDRAINED, DECLARED-STALE, MTIME-STALE, ORPHAN, AS_OF-GAP")
    print("  proved NOT firing: same-day drain, wiki/personal routing, body-mention decoy")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Agent-memory drain freshness check")
    ap.add_argument("--memory-dir", default=CFL_STORE, help="memory store to measure")
    ap.add_argument("--wiki-root", default=os.path.join(REPO_ROOT, "wiki"))
    ap.add_argument("--repo-root", default=REPO_ROOT)
    ap.add_argument("--strict-mtime", action="store_true",
                    help="treat advisory mtime staleness as a failure")
    ap.add_argument("--no-git", action="store_true",
                    help="use page mtime instead of git last-commit time")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    r = scan(a.memory_dir, a.wiki_root, a.repo_root, use_git=not a.no_git)
    if r is None:
        return 2
    return report(r, a.strict_mtime)


if __name__ == "__main__":
    sys.exit(main())
