#!/usr/bin/env python3
"""
coverage_census.py -- re-runnable wiki coverage census.

Codifies the method described in
wiki/intake-triage/DREAM-SWEEP-A-F-wiki-coverage-census-and-pending-actions-2026-08-24.md
section A.1, so it can be re-run on any trunk / any commit without re-deriving
the method by hand.

METHOD
------
1. Walk --raw-root for main-session transcripts:
     - only claude-ai / claude-code venues (chat-*.md / code-*.md)
     - excludes: *.sidecar.md, anything under a "subagents" directory,
       anything under "_superseded", anything under "podcasts"
     - any path containing "XC-Exchequer" is SKIPPED, COUNTED, NEVER OPENED
   Filenames are parsed as (chat|code)-YYYY-MM-DD-<6hex>-<title>.md.
   Files that don't match that shape are counted separately as "unparsed"
   and excluded from the session-id set (mirrors the 08-24 packet's 9
   non-parsing files: skip-registry.md, summary-*-cc.md, recon-*-reconstructed.md,
   AUDIT-NOTES.md, pre-nap-note*.md, etc).
2. Renders collapse to distinct SESSIONS by 6-hex id. A session's date is its
   earliest render's date; bytes are the sum of all its main-transcript renders.
3. Walk --wiki-root for every *.md file (all trunks, not just wiki/sources --
   personal/home/pro sources pages count as coverage, they are just never
   quoted per Jon's 2026-07-25 ruling; this script only tests existence, it
   never prints file content).
4. Classify each session against the wiki, in this priority order:
     A - a file under a path containing "/sources/" whose FILENAME ends in
         -<id>.md
     B - the id (bare 6-hex token, OR the first 6 hex chars of a full UUID
         appearing in the body) is cited in the BODY of a file under a path
         containing "/sources/", "/concepts/", or "/references/"
     S - the id appears (filename-suffix OR body) in any file named
         session-stubs*.md anywhere under wiki-root
     C - the id appears ONLY under wiki/intake-triage/ or wiki/tracker/
     D - the id appears ONLY somewhere else in wiki/ (log.md, index.md, ...)
     Z - the id appears NOWHERE in wiki/, by any id form
   Bare 6-hex body matching is restricted to the KNOWN session-id set (never
   an unconstrained hex regex) -- this is the exact correction the 08-24
   packet made after its first pass (424 -> 351 hard-gap) by missing this.

SELF-CITATION EXCLUSION (--exclude-self-citations, default ON)
----------------------------------------------------------------
A census/coverage packet that PUBLISHES a Z-list (or a C/D list) into
wiki/intake-triage/ becomes, on the next re-run, a wiki file that CITES every
id it just classified -- moving those ids off Z and onto C purely because the
measuring instrument's own prior output is sitting in the corpus it measures.
Found 2026-09-02 comparing this script's fixture run against the 08-24
packet's own numbers: all 8 checked top-20 Z-listed sessions from that packet
flipped to C on re-run for exactly this reason.

When this flag is on (default), any wiki file whose FILENAME matches
`census` or `dream-sweep-a-f` (case-insensitive) -- this covers
wiki/intake-triage/*CENSUS*, *coverage-census*, *DREAM-SWEEP-A-F*, and the
C1-census-*/CENSUS-*-coverage.* files this script itself writes -- is
excluded entirely from the classification evidence pool (both filename and
body matching). Pass --no-exclude-self-citations to disable and reproduce
the raw (contaminated) behavior for comparison.

SELF-CHECK (--self-check)
--------------------------
Runs two invariant checks after classification and prints PASS/FAIL for
each, exiting nonzero if either fails:
  1. Class priority order: for every session, the assigned tier is
     re-derived independently from the evidence pool and must be the FIRST
     tier (in A,B,S,C,D,Z order) for which that session's evidence qualifies.
  2. XC-Exchequer never opened: re-walks --raw-root and asserts zero "main"
     or "unparsed" yields carry an XC-Exchequer path, and asserts zero wiki
     files scanned carry one either. Prints the confirmed skip count.

OUTPUT
------
Two artifacts: a markdown report and a JSON work-queue (one row per session,
Z sessions ordered newest-first), plus the exact command line and the
XC-Exchequer skip count, printed to stdout as a run summary.

This script is READ-ONLY. It never writes into --raw-root or --wiki-root.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

# Filenames carry a DATE-ID pair somewhere in the stem, but not always in
# the same position: "chat-2026-08-03-6ef78d-title.md" (prefix-date-id-title)
# and "agent-interaction-framework-2026-07-02-5990f2.md" (title-date-id, no
# chat-/code- prefix, seen throughout claude-ai/fl/<project>/ subdirs) both
# occur in this corpus. Match the date-id pair anywhere in the stem instead
# of anchoring a fixed prefix shape.
FNAME_RE = re.compile(r"(\d{4}-\d{2}-\d{2})-([0-9a-f]{6})(?:-|$)")
FULLUUID_RE = re.compile(
    r"\b([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})\b"
)
HEX6_WORD_RE = re.compile(r"\b([0-9a-f]{6})\b")

VENUE_MAP = {"chat": "claude-ai", "code": "claude-code"}


def is_xc(path: str) -> bool:
    return "xc-exchequer" in path.lower()


def is_sidecar(name: str) -> bool:
    return name.endswith(".sidecar.md")


def under_dir(path: str, dirname: str) -> bool:
    parts = re.split(r"[\\/]+", path)
    return dirname in parts


def walk_raw(raw_root: str, as_of: str | None):
    """
    Yields (kind, info) where kind in {"main", "unparsed", "xc_skip"}.
    as_of: optional 'YYYY-MM-DD' -- if given, filter main-session files to
    those whose PARSED DATE is <= as_of (used by the fixture regression to
    neutralise raw-mirror growth since 2026-08-24).
    """
    xc_skip = 0
    for dirpath, dirnames, filenames in os.walk(raw_root):
        # never descend into or open an XC-Exchequer path
        dirnames[:] = [d for d in dirnames if "xc-exchequer" not in d.lower()]
        if is_xc(dirpath):
            xc_skip += len(filenames)
            continue
        if under_dir(dirpath, "subagents"):
            continue
        if under_dir(dirpath, "_superseded"):
            continue
        if under_dir(dirpath, "podcasts"):
            continue
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if is_xc(full):
                xc_skip += 1
                continue
            if not fn.endswith(".md") or is_sidecar(fn):
                continue
            m = FNAME_RE.search(fn)
            if not m:
                yield ("unparsed", {"path": full})
                continue
            date, sid = m.groups()
            title = (fn[:-3].replace(m.group(0), "", 1)).strip("-")
            parts_lower = [p.lower() for p in re.split(r"[\\/]+", dirpath)]
            if "claude-ai" in parts_lower:
                venue = "claude-ai"
            elif "claude-code" in parts_lower:
                venue = "claude-code"
            else:
                venue = "other"
            if as_of and date > as_of:
                continue
            try:
                size = os.path.getsize(full)
            except OSError:
                size = -1
            yield (
                "main",
                {
                    "path": full,
                    "venue": venue,
                    "date": date,
                    "id": sid,
                    "title": title,
                    "bytes": size,
                },
            )
    return xc_skip


def collect_sessions(raw_root: str, as_of: str | None):
    sessions = {}  # id -> dict
    unparsed = []
    xc_skip = 0
    gen = walk_raw(raw_root, as_of)
    for kind, info in gen:
        if kind == "unparsed":
            unparsed.append(info["path"])
            continue
        sid = info["id"]
        s = sessions.setdefault(
            sid,
            {"id": sid, "date": info["date"], "venue": info["venue"],
             "title": info["title"], "bytes": 0, "renders": []},
        )
        if info["date"] < s["date"]:
            s["date"] = info["date"]
            s["venue"] = info["venue"]
            s["title"] = info["title"]
        s["bytes"] += max(info["bytes"], 0)
        s["renders"].append(info["path"])
    # xc_skip is not returned by generator return value when using yield in
    # a normal for-loop (StopIteration.value is lost) -- recompute directly.
    xc_skip = count_xc(raw_root)
    return sessions, unparsed, xc_skip


def count_xc(raw_root: str) -> int:
    n = 0
    for dirpath, dirnames, filenames in os.walk(raw_root):
        if "xc-exchequer" in dirpath.lower():
            n += len(filenames)
            dirnames[:] = []
            continue
        for fn in filenames:
            if "xc-exchequer" in fn.lower():
                n += 1
    return n


SELF_CITATION_RE = re.compile(r"census|dream-sweep-a-f", re.I)


def is_self_citation_file(fn: str) -> bool:
    """
    True for a wiki file that IS a census/coverage-census packet -- these
    must never contribute classification evidence, because a census that
    cites the ids it classifies (its own Z-list, its own top-20 table)
    contaminates every re-run that treats "cited in wiki/intake-triage" as
    coverage. Matches wiki/intake-triage/*CENSUS*, *coverage-census*,
    *DREAM-SWEEP-A-F*, and the C1-census-*/CENSUS-*-coverage.* files this
    script itself writes.
    """
    return bool(SELF_CITATION_RE.search(fn))


def walk_wiki(wiki_root: str):
    """
    Returns (files, xc_skip). files is a list of dicts (path, is_sources,
    is_concepts, is_refs, is_stub, is_intake_or_tracker, is_self_citation)
    with body text loaded lazily by caller. xc_skip is the count of wiki
    files SKIPPED (never opened, never scanned) because their path contains
    "XC-Exchequer" (case-insensitive) -- found 2026-09-02 via --self-check:
    the original version of this function had no XC guard at all and was
    opening wiki pages named e.g. CENSUS-xc-exchequer-three-trees-*.md and
    reading their bodies, which is exactly the "never opened" rule the raw
    scan already honoured. The XC rule applies to --wiki-root too, not just
    --raw-root.
    """
    files = []
    xc_skip = 0
    for dirpath, dirnames, filenames in os.walk(wiki_root):
        dirnames[:] = [d for d in dirnames if "xc-exchequer" not in d.lower()]
        if "xc-exchequer" in dirpath.lower():
            xc_skip += sum(1 for fn in filenames if fn.endswith(".md"))
            continue
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            if "xc-exchequer" in fn.lower():
                xc_skip += 1
                continue
            full = os.path.join(dirpath, fn)
            parts = [p.lower() for p in re.split(r"[\\/]+", dirpath)]
            files.append({
                "path": full,
                "fname": fn,
                "is_sources": "sources" in parts,
                "is_concepts": "concepts" in parts,
                "is_refs": "references" in parts,
                "is_stub_file": fn.lower().startswith("session-stubs"),
                "is_intake_or_tracker": ("intake-triage" in parts or "tracker" in parts),
                "is_self_citation": is_self_citation_file(fn),
            })
    return files, xc_skip


def classify(sessions: dict, wiki_files: list, exclude_self_citations: bool = True):
    """
    Returns (id_class, evidence, fname_hits, body_hits):
      id_class  -- dict id -> class letter
      evidence  -- dict id -> list of wiki paths backing that class, for the
                   JSON output
      fname_hits, body_hits -- dict id -> list of wiki file dicts, the raw
                   evidence pool BEFORE the priority cut, exposed so
                   --self-check can independently re-derive each class and
                   assert the priority order was actually honoured.

    When exclude_self_citations is True (the default), any wiki file
    self-flagged as a census/coverage packet (see is_self_citation_file) is
    dropped from the evidence pool before either matching pass runs -- a
    census must not be able to move the class of the ids it itself
    classified by citing them in its own output.
    """
    if exclude_self_citations:
        scan_files = [w for w in wiki_files if not w["is_self_citation"]]
    else:
        scan_files = wiki_files

    ids = set(sessions.keys())
    id_class = {}
    evidence = {}

    # Pass 1: filename-suffix matches (id anywhere in the filename, since
    # renders/titles vary; safe because ids are 6-hex and drawn from the
    # known session set).
    fname_hits = defaultdict(list)  # id -> list of wiki file dicts
    for wf in scan_files:
        stem = wf["fname"][:-3]  # strip .md
        # id must appear as a trailing hex6 token preceded by '-'
        for m in re.finditer(r"-([0-9a-f]{6})(?:$|[^0-9a-f])", stem):
            sid = m.group(1)
            if sid in ids:
                fname_hits[sid].append(wf)

    # Pass 2: body matches -- read every wiki file once, extract hex6 tokens
    # and full-uuid tokens (first 6 chars), intersect with known id set.
    body_hits = defaultdict(list)  # id -> list of wiki file dicts
    for wf in scan_files:
        try:
            with open(wf["path"], "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            continue
        found = set()
        for m in HEX6_WORD_RE.finditer(text):
            tok = m.group(1)
            if tok in ids:
                found.add(tok)
        for m in FULLUUID_RE.finditer(text):
            tok = m.group(1)  # first 8 hex chars of the uuid group
            sid6 = tok[:6]
            if sid6 in ids:
                found.add(sid6)
        for sid in found:
            body_hits[sid].append(wf)

    for sid in ids:
        fhits = fname_hits.get(sid, [])
        bhits = body_hits.get(sid, [])
        all_hits = fhits + bhits

        # A: filename under a sources/ path (session-stubs.md itself lives
        # under wiki/sources/ but is a registry, not a per-session page --
        # excluded here so stub-only sessions fall through to S below).
        a_hits = [w for w in fhits if w["is_sources"] and not w["is_stub_file"]]
        if a_hits:
            id_class[sid] = "A"
            evidence[sid] = [w["path"] for w in a_hits]
            continue

        # B: body-cited under sources/concepts/references (same stub-file
        # exclusion as A).
        b_hits = [w for w in bhits
                  if (w["is_sources"] or w["is_concepts"] or w["is_refs"])
                  and not w["is_stub_file"]]
        if b_hits:
            id_class[sid] = "B"
            evidence[sid] = [w["path"] for w in b_hits]
            continue

        # S: stub registry
        s_hits = [w for w in all_hits if w["is_stub_file"]]
        if s_hits:
            id_class[sid] = "S"
            evidence[sid] = [w["path"] for w in s_hits]
            continue

        if not all_hits:
            id_class[sid] = "Z"
            evidence[sid] = []
            continue

        # C: only in intake-triage or tracker
        c_hits = [w for w in all_hits if w["is_intake_or_tracker"]]
        non_c = [w for w in all_hits if not w["is_intake_or_tracker"]]
        if c_hits and not non_c:
            id_class[sid] = "C"
            evidence[sid] = [w["path"] for w in c_hits]
            continue

        # D: only elsewhere
        id_class[sid] = "D"
        evidence[sid] = [w["path"] for w in all_hits]

    return id_class, evidence, fname_hits, body_hits


def month_of(date: str) -> str:
    return date[:7]


def build_report(sessions, id_class, unparsed, xc_skip, raw_root, wiki_root,
                  as_of, cmdline, exclude_self_citations=True):
    total = len(sessions)
    tiers = {"A": 0, "B": 0, "S": 0, "C": 0, "D": 0, "Z": 0}
    for c in id_class.values():
        tiers[c] += 1
    covered = tiers["A"] + tiers["B"]

    by_month = defaultdict(lambda: {"sessions": 0, "covered": 0, "gap": 0, "hardgap": 0})
    for sid, s in sessions.items():
        mo = month_of(s["date"])
        by_month[mo]["sessions"] += 1
        c = id_class[sid]
        if c in ("A", "B"):
            by_month[mo]["covered"] += 1
        if c in ("C", "D", "Z"):
            by_month[mo]["gap"] += 1
        if c == "Z":
            by_month[mo]["hardgap"] += 1

    z_sessions = sorted(
        (s for s in sessions.values() if id_class[s["id"]] == "Z"),
        key=lambda s: s["date"], reverse=True,
    )

    lines = []
    lines.append("---")
    lines.append("name: coverage-census-2026-09-02")
    lines.append("title: \"Coverage census re-run (instrument: coverage_census.py)\"")
    lines.append("kind: finding")
    lines.append(f"date: {datetime.now().date().isoformat()}")
    lines.append(f"as_of: {as_of or 'HEAD'}")
    lines.append("trunk: fl")
    lines.append("sensitivity: T1")
    lines.append("---\n")
    lines.append("# Coverage census re-run\n")
    lines.append(f"**Command:** `{cmdline}`\n")
    lines.append(f"**raw-root:** `{raw_root}`  \n**wiki-root:** `{wiki_root}`\n")
    lines.append(f"**Unparsed main-transcript-shaped files (excluded from session set):** {len(unparsed)}\n")
    lines.append(f"**XC-Exchequer paths skipped (counted, never opened):** {xc_skip}\n")
    lines.append(f"**Self-citation exclusion (census/coverage-packet wiki files dropped from evidence pool):** {'ON' if exclude_self_citations else 'OFF (--no-exclude-self-citations)'}\n")
    lines.append("## Totals\n")
    lines.append("| tier | meaning | count | % |")
    lines.append("|---|---|---:|---:|")
    labels = {
        "A": "source page filename carries the id",
        "B": "cited in body of source/concept/reference page",
        "S": "deliberately stubbed in session-stubs.md",
        "C": "appears only in intake-triage/ or tracker/",
        "D": "appears only elsewhere in wiki/",
        "Z": "appears nowhere in wiki/, by any id form",
    }
    for t in ["A", "B", "S", "C", "D", "Z"]:
        pct = 100 * tiers[t] / total if total else 0
        lines.append(f"| {t} | {labels[t]} | {tiers[t]} | {pct:.1f}% |")
    lines.append(f"\n**Total sessions:** {total}  \n**Covered (A+B):** {covered} ({100*covered/total:.1f}% if total else 'n/a')  \n")

    lines.append("\n## Per-month\n")
    lines.append("| month | sessions | covered (A+B) | coverage rate | gap (C+D+Z) | hard gap (Z) |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for mo in sorted(by_month.keys()):
        row = by_month[mo]
        rate = 100 * row["covered"] / row["sessions"] if row["sessions"] else 0
        lines.append(f"| {mo} | {row['sessions']} | {row['covered']} | {rate:.1f}% | {row['gap']} | {row['hardgap']} |")

    lines.append("\n## Z list (hard gap), newest first, with bytes\n")
    lines.append("| date | id | venue | bytes | title |")
    lines.append("|---|---|---|---:|---|")
    for s in z_sessions:
        lines.append(f"| {s['date']} | `{s['id']}` | {s['venue']} | {s['bytes']} | {s['title']} |")

    return "\n".join(lines) + "\n"


def build_json(sessions, id_class, evidence):
    z_first = sorted(
        sessions.values(),
        key=lambda s: (id_class[s["id"]] != "Z", s["date"]),
        reverse=True,
    )
    # Actually: Z sessions first, newest-first within Z, then the rest.
    z = sorted((s for s in sessions.values() if id_class[s["id"]] == "Z"),
               key=lambda s: s["date"], reverse=True)
    rest = sorted((s for s in sessions.values() if id_class[s["id"]] != "Z"),
                  key=lambda s: s["date"], reverse=True)
    rows = []
    for s in z + rest:
        rows.append({
            "id": s["id"],
            "date": s["date"],
            "venue": s["venue"],
            "title": s["title"],
            "class": id_class[s["id"]],
            "bytes": s["bytes"],
            "transcript_paths": s["renders"],
            "wiki_evidence": evidence.get(s["id"], []),
        })
    return rows


def tier_eligibility(sid: str, fname_hits: dict, body_hits: dict) -> dict:
    """
    Independently re-derives, from the raw evidence pool, which tiers a
    session QUALIFIES for -- used only by --self-check to verify classify()
    actually applied the documented priority order (A,B,S, then Z-if-empty,
    else C-or-D) rather than assigning some other tier.
    """
    fhits = fname_hits.get(sid, [])
    bhits = body_hits.get(sid, [])
    all_hits = fhits + bhits
    elig = {}
    elig["A"] = any(w["is_sources"] and not w["is_stub_file"] for w in fhits)
    elig["B"] = any((w["is_sources"] or w["is_concepts"] or w["is_refs"])
                     and not w["is_stub_file"] for w in bhits)
    elig["S"] = any(w["is_stub_file"] for w in all_hits)
    elig["Z"] = (len(all_hits) == 0)
    c_hits = [w for w in all_hits if w["is_intake_or_tracker"]]
    non_c = [w for w in all_hits if not w["is_intake_or_tracker"]]
    elig["C"] = bool(c_hits) and not non_c
    elig["D"] = bool(all_hits) and bool(non_c)
    return elig


def self_check_priority(sessions: dict, id_class: dict, fname_hits: dict, body_hits: dict):
    """
    Returns a list of (id, assigned_class, expected_class, eligibility)
    violations -- empty means the priority order A > B > S > (Z if no
    evidence, else C/D) was honoured for every session.
    """
    violations = []
    for sid in sessions:
        elig = tier_eligibility(sid, fname_hits, body_hits)
        assigned = id_class[sid]
        if elig["A"]:
            expected = "A"
        elif elig["B"]:
            expected = "B"
        elif elig["S"]:
            expected = "S"
        elif elig["Z"]:
            expected = "Z"
        elif elig["C"]:
            expected = "C"
        else:
            expected = "D"
        if expected != assigned:
            violations.append((sid, assigned, expected, elig))
    return violations


def self_check_xc(sessions: dict, unparsed: list, wiki_files: list):
    """
    Returns a list of (source, session_id_or_None, path) violations for any
    XC-Exchequer path that leaked into the session set, the unparsed list,
    or the wiki scan -- i.e. any XC-Exchequer file this run actually
    touched/counted as content rather than skipping. Empty means clean.
    """
    violations = []
    for sid, s in sessions.items():
        for r in s["renders"]:
            if "xc-exchequer" in r.lower():
                violations.append(("main", sid, r))
    for u in unparsed:
        if "xc-exchequer" in u.lower():
            violations.append(("unparsed", None, u))
    for wf in wiki_files:
        if "xc-exchequer" in wf["path"].lower():
            violations.append(("wiki", None, wf["path"]))
    return violations


# ---------------------------------------------------------------------------
# DR-1 -- POPULATION GUARD, added 2026-09-04 after this instrument returned a
# clean, plausible, FLATTERING number against the wrong corpus.
#
# What happened: --raw-root was pointed at the repo's own raw/transcripts
# instead of the corpus mirror. Result: sessions=67 covered=63 (94.0%), no
# error, no warning. The canonical root gives sessions=870 covered=491 (56.4%).
#
# The instrument was NOT at fault -- --raw-root is REQUIRED, so it cannot
# default wrong. A required flag prevents a DEFAULT; it does nothing about a
# wrong ARGUMENT. This guard covers the argument.
#
# TWO INDEPENDENT SIGNALS. Each must be able to fire while the other is silent,
# or this is one check wearing two names:
#
#   S1 SHRINK   -- the corpus is append-only, so a denominator SMALLER than the
#                  largest one previously recorded for this (wiki-root, as-of)
#                  is a population error until proven otherwise. This is the
#                  one that would have caught 733 -> 67.
#   S2 IN-REPO  -- --raw-root resolves inside this git repo rather than a
#                  separate corpus mirror. Fires on the FIRST run ever, when
#                  S1 has no high-water mark to compare against.
#
# S1 is silent on a first run; S2 is silent for anyone whose mirror legitimately
# lives in-repo. Neither subsumes the other.
#
# EXIT 3 on S1 unless --allow-shrink is passed with a reason. S2 warns only --
# an in-repo corpus is unusual, not wrong.
# ---------------------------------------------------------------------------

HWM_DEFAULT = os.path.join("evidence", "census-highwater.json")


def _hwm_key(wiki_root: str, as_of: str | None, raw_root: str | None = None) -> str:
    """--as-of legitimately shrinks the population, so an as-of run is compared
    only against its OWN history, never against the unfiltered one.

    RAW-ROOT ADDED 2026-09-04, and the defect that forced it happened inside one
    hour of DR-1 shipping. A deliberate SUBSET run --

        --raw-root .../raw/transcripts/claude-ai   (260 sessions)

    -- shared a key with the full-root run (882 sessions), so it OVERWROTE the
    high-water mark with the smaller number on an --allow-shrink override that was
    honest and correct for what it described. The mark then read 260, and a later
    real collapse from 882 to 400 would have registered as GROWTH and passed.

    The guard announced the shrink loudly and still ended up blind, because the
    thing it recorded (raw_root, in the VALUE) was not the thing it compared on
    (the KEY). A population guard keyed on anything less than the population's own
    definition guards a different population. Each root now keeps its own history,
    so a subset run cannot poison the full run's mark and needs no override at all
    after its first."""
    parts = [os.path.normpath(os.path.abspath(wiki_root)), f"as_of={as_of or 'none'}"]
    if raw_root:
        parts.append(f"raw={os.path.normpath(os.path.abspath(raw_root))}")
    return "|".join(parts)


def _repo_root(start: str):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def raw_root_is_in_repo(raw_root: str) -> bool:
    """S2. True when --raw-root lies inside the same git repo this script does."""
    here = _repo_root(os.path.dirname(os.path.abspath(__file__)))
    if not here:
        return False
    rr = os.path.normpath(os.path.abspath(raw_root))
    return rr == here or rr.startswith(here + os.sep)


def read_hwm(path: str, key: str):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get(key)
    except (OSError, ValueError):
        return None


def write_hwm(path: str, key: str, total: int, raw_root: str) -> None:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    data[key] = {
        "sessions": total,
        "raw_root": os.path.normpath(os.path.abspath(raw_root)),
        "recorded": datetime.now().isoformat(timespec="seconds"),
    }
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def population_guard(total, raw_root, wiki_root, as_of, hwm_file, allow_shrink):
    """Returns (lines_to_print, shrink_fired). Never writes on a shrink -- a wrong
    population must not silently become the new high-water mark."""
    out = []
    shrink = False

    if raw_root_is_in_repo(raw_root):
        out.append("  WARN S2 IN-REPO: --raw-root resolves INSIDE this git repo. The corpus "
                   "mirror is normally a separate tree; an in-repo root usually means the "
                   "wrong population. Not fatal -- verify the denominator below is the one "
                   "you meant.")

    key = _hwm_key(wiki_root, as_of, raw_root)
    prev = read_hwm(hwm_file, key)
    if prev is None:
        out.append("  note S1 SHRINK: no high-water mark yet for this (wiki-root, as-of, raw-root); "
                   f"recording sessions={total} as the first. S1 CANNOT FIRE ON THIS RUN.")
        write_hwm(hwm_file, key, total, raw_root)
    elif total < prev["sessions"]:
        shrink = True
        out.append("  FAIL S1 SHRINK: the corpus is append-only and this denominator went DOWN.")
        out.append(f"    now      sessions={total}  --raw-root="
                   f"{os.path.normpath(os.path.abspath(raw_root))}")
        out.append(f"    previous sessions={prev['sessions']}  --raw-root={prev['raw_root']}"
                   f"  recorded={prev['recorded']}")
        out.append("    A SMALLER POPULATION PRODUCES A HIGHER COVERAGE PERCENTAGE. Read the "
                   "roots above before reading the number below.")
        out.append("    High-water mark NOT updated. Re-run against the right root, or pass "
                   "--allow-shrink REASON if the shrink is real (a purge, a re-scope).")
    else:
        write_hwm(hwm_file, key, total, raw_root)

    if shrink and allow_shrink:
        out.append(f"  OVERRIDE --allow-shrink: {allow_shrink}")
        out.append("    Recorded as the new high-water mark on the operator's stated reason.")
        write_hwm(hwm_file, key, total, raw_root)
        shrink = False

    return out, shrink


def self_check_population():
    """Negative controls. A guard that cannot fire is this week's dominant defect,
    so both signals are exercised against fixtures that MUST trip them and
    fixtures that MUST NOT."""
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as td:
        hf = os.path.join(td, "hwm.json")

        # S1 must NOT fire on a first run, and must record.
        _, fired = population_guard(870, td, td, None, hf, None)
        if fired:
            fails.append("S1 fired on a first run (no high-water mark exists)")
        if read_hwm(hf, _hwm_key(td, None, td)) is None:
            fails.append("first run did not record a high-water mark")

        # S1 must NOT fire on growth, and must advance the mark.
        _, fired = population_guard(871, td, td, None, hf, None)
        if fired:
            fails.append("S1 fired on a GROWING population")
        if read_hwm(hf, _hwm_key(td, None, td))["sessions"] != 871:
            fails.append("growth did not advance the high-water mark")

        # S1 MUST fire on the real fixture: 871 -> 67.
        _, fired = population_guard(67, td, td, None, hf, None)
        if not fired:
            fails.append("S1 did NOT fire on 871 -> 67 (the defect this guard exists for)")
        if read_hwm(hf, _hwm_key(td, None, td))["sessions"] != 871:
            fails.append("a SHRINK was recorded as the new high-water mark -- the guard "
                         "would never fire again")

        # --allow-shrink must clear it AND record.
        _, fired = population_guard(67, td, td, None, hf, "purge, stated by operator")
        if fired:
            fails.append("--allow-shrink did not clear S1")
        if read_hwm(hf, _hwm_key(td, None, td))["sessions"] != 67:
            fails.append("--allow-shrink did not record the new mark")

        # --as-of is keyed separately: an as-of run must not be compared against
        # the unfiltered history.
        hf2 = os.path.join(td, "hwm2.json")
        population_guard(870, td, td, None, hf2, None)
        _, fired = population_guard(120, td, td, "2026-08-01", hf2, None)
        if fired:
            fails.append("an --as-of run was compared against the unfiltered high-water mark")

        # A SUBSET ROOT MUST KEEP ITS OWN HISTORY. This is the 2026-09-04 fixture,
        # replayed with the real numbers: a full-root run at 882, then a deliberate
        # claude-ai-only run at 260 under --allow-shrink. Before the raw_root was in
        # the key, the second run overwrote the first's mark and a later collapse
        # 882 -> 400 would have read as growth.
        hf3 = os.path.join(td, "hwm3.json")
        sub = os.path.join(td, "claude-ai")
        os.makedirs(sub, exist_ok=True)
        population_guard(882, td, td, None, hf3, None)          # full root
        _, fired = population_guard(260, sub, td, None, hf3, None)  # subset root
        if fired:
            fails.append("a DIFFERENT --raw-root was compared against another root's "
                         "high-water mark -- a subset run should need no override")
        if read_hwm(hf3, _hwm_key(td, None, td))["sessions"] != 882:
            fails.append("a subset run OVERWROTE the full root's high-water mark -- the "
                         "guard is blind in exactly the range that matters")
        _, fired = population_guard(400, td, td, None, hf3, None)
        if not fired:
            fails.append("S1 did NOT fire on 882 -> 400 after a subset run; this is the "
                         "exact blindness the raw_root key exists to prevent")

        # S2 must fire on this repo's own tree and stay silent outside it.
        here = _repo_root(os.path.dirname(os.path.abspath(__file__)))
        if here and not raw_root_is_in_repo(os.path.join(here, "raw", "transcripts")):
            fails.append("S2 did NOT fire on an in-repo --raw-root")
        if raw_root_is_in_repo(td):
            fails.append("S2 fired on a root OUTSIDE the repo (false positive)")

    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    # NOT required=True, but ONLY so --self-check-population can run standalone.
    # --self-check is a different flag with different semantics: it runs the
    # class-priority invariants AFTER a real classification, so it does need roots.
    # Conflating the two would have made a real check unrunnable; enforced below.
    ap.add_argument("--raw-root")
    ap.add_argument("--wiki-root")
    ap.add_argument("--as-of", default=None,
                     help="YYYY-MM-DD -- only include main-session files whose parsed date is <= this")
    ap.add_argument("--out-md", default=None)
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--exclude-self-citations", action=argparse.BooleanOptionalAction,
                     default=True,
                     help="Exclude census/coverage-packet wiki files from classification "
                          "evidence (default ON). Use --no-exclude-self-citations to "
                          "reproduce the raw (self-citation-contaminated) behavior.")
    ap.add_argument("--hwm-file", default=HWM_DEFAULT,
                    help="high-water-mark file for the DR-1 population guard (S1).")
    ap.add_argument("--allow-shrink", default=None, metavar="REASON",
                    help="acknowledge a genuinely smaller population (a purge, a "
                         "re-scope). Requires a stated reason; echoed in the output.")
    ap.add_argument("--self-check", action="store_true",
                     help="Run the class-priority-order and XC-Exchequer-never-opened "
                          "invariant checks after classification; print PASS/FAIL and "
                          "exit nonzero on failure (files are still written).")
    ap.add_argument("--self-check-population", action="store_true",
                     help="Run the population-guard fixtures (S1/S2) against temp-dir "
                          "controls and exit. Needs no roots -- a guard whose check is "
                          "harder to run than the thing it guards stops being run.")
    args = ap.parse_args()

    if args.self_check_population:
        fails = self_check_population()
        if fails:
            print(f"POPULATION SELF-CHECK: FAIL -- {len(fails)}")
            for x in fails:
                print("  " + x)
            return 1
        print("POPULATION SELF-CHECK: PASS -- 13 assertions: first-run, growth, the "
              "871->67 shrink fixture, --allow-shrink, --as-of separation, the "
              "2026-09-04 subset-root fixture (882 full / 260 claude-ai / 400 collapse), "
              "and S2 in-repo both directions")
        return 0

    if not args.raw_root or not args.wiki_root:
        ap.error("--raw-root and --wiki-root are required for a census run "
                 "(not needed for --self-check-population)")

    cmdline = " ".join(sys.argv)

    sessions, unparsed, xc_skip_raw = collect_sessions(args.raw_root, args.as_of)
    wiki_files, xc_skip_wiki = walk_wiki(args.wiki_root)
    xc_skip = xc_skip_raw + xc_skip_wiki
    id_class, evidence, fname_hits, body_hits = classify(
        sessions, wiki_files, exclude_self_citations=args.exclude_self_citations)

    md = build_report(sessions, id_class, unparsed, xc_skip,
                       args.raw_root, args.wiki_root, args.as_of, cmdline,
                       args.exclude_self_citations)
    rows = build_json(sessions, id_class, evidence)

    total = len(sessions)
    covered = sum(1 for c in id_class.values() if c in ("A", "B"))
    z = sum(1 for c in id_class.values() if c == "Z")
    aug = sum(1 for s in sessions.values() if month_of(s["date"]) == "2026-08")
    aug_cov = sum(1 for s in sessions.values()
                  if month_of(s["date"]) == "2026-08" and id_class[s["id"]] in ("A", "B"))

    guard_lines, shrink_fired = population_guard(
        total, args.raw_root, args.wiki_root, args.as_of, args.hwm_file,
        args.allow_shrink)
    if guard_lines:
        print("=== POPULATION GUARD (DR-1) ===")
        for gl in guard_lines:
            print(gl)

    print(f"sessions={total} covered_AB={covered} Z={z} unparsed={len(unparsed)} "
          f"xc_skip={xc_skip} (raw={xc_skip_raw} wiki={xc_skip_wiki})")
    print(f"august_sessions={aug} august_covered={aug_cov}")
    print(f"exclude_self_citations={args.exclude_self_citations}")

    self_check_failed = False
    if args.self_check:
        pv = self_check_priority(sessions, id_class, fname_hits, body_hits)
        if pv:
            print(f"SELF-CHECK [class priority order]: FAIL -- {len(pv)} violation(s)")
            for sid, assigned, expected, elig in pv[:10]:
                print(f"  id={sid} assigned={assigned} expected={expected} eligibility={elig}")
            self_check_failed = True
        else:
            print(f"SELF-CHECK [class priority order]: PASS -- {len(sessions)} sessions checked")

        pf = self_check_population()
        if pf:
            print(f"SELF-CHECK [population guard DR-1]: FAIL -- {len(pf)} violation(s)")
            for v in pf:
                print(f"  {v}")
            self_check_failed = True
        else:
            print("SELF-CHECK [population guard DR-1]: PASS -- 9 assertions incl. the "
                  "871->67 fixture that MUST fire and four that MUST NOT")

        xv = self_check_xc(sessions, unparsed, wiki_files)
        if xv:
            print(f"SELF-CHECK [XC-Exchequer never opened]: FAIL -- {len(xv)} leak(s)")
            for src, sid, p in xv[:10]:
                print(f"  source={src} id={sid} path={p}")
            self_check_failed = True
        else:
            print(f"SELF-CHECK [XC-Exchequer never opened]: PASS -- xc_skip={xc_skip} confirmed, 0 leaked into session/unparsed/wiki scans")

    if args.out_md:
        with open(args.out_md, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"wrote {args.out_md}")
    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        print(f"wrote {args.out_json}")

    if self_check_failed:
        sys.exit(1)
    if shrink_fired:
        sys.exit(3)


if __name__ == "__main__":
    main()
