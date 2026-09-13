#!/usr/bin/env python3
"""role_history.py -- the agent role record, generated rather than remembered.

WHY THIS EXISTS -- Jon, verbatim, 2026-08-06
--------------------------------------------
    "And I neeeed to have agent role history. Your history as a coordinator is key. My
     definitions of skills masters, wiki masters.... Their triumphs and their failures....
     All their jsons and mds. I don't like that I can't find them organized"

Two halves, and they are different problems.

HALF A -- what each role DID. Scattered, not missing.
    A role's definition is in `.claude/agents/` or `skills/<name>/SKILL.md`; its runs are 790
    subagent transcripts under `raw/transcripts/claude-code/subagents/`; its raw JSONLs are in
    `~/.claude/projects/*/`; its rules are spread across `CLAUDE.md`, the coordination charter,
    and hundreds of wiki pages. Every piece exists. None of it is assembled. Half A is an
    INDEX JOIN over data that already exists -- it is not a new scanner, and it does not
    re-walk the corpus: it reads `wiki/tracker/corpus-index.jsonl`, which corpus_index.py
    already produces.

HALF B -- how it WENT. This one is genuinely missing.
    245 wiki files mention "coordinator". Not one of them scores whether the coordinator was
    RIGHT. A record of what an agent did, with no record of how it went, cannot answer the
    only question worth asking of a role: is it getting better?

    Half B reads `wiki/tracker/role-episodes.jsonl` -- adjudicated, one row per episode, every
    row carrying a citation. The rows are hand-written; they are NOT hand-maintained, because
    this script re-resolves every anchor against the cited file on every run. An anchor that
    stops resolving is printed as CITATION-BROKEN and dropped from every statistic. That is
    the difference between this ledger and `MEMORY.md`, which diverged from its own store by
    two files on 2026-08-06 with nothing able to notice.

THE NUMBER THIS EXISTS TO PRODUCE
----------------------------------
Not the episode list. The **who-caught-it ratio**: of the defects and wins on record, what
share did the role find *itself, unprompted*, versus Jon finding it, versus another agent
finding it? The coordinator's own account of 2026-08-06, quoted in the ledger:

    "The measurable failure is that I don't retrieve at all -- I answer from context and only
     check when challenged. Every check today came from you pushing, not from me reaching."

A history that only records failures is a flagellation, not a history, so the ledger carries
`valence` and this script prints DEFECT and TRIUMPH counts side by side and refuses to hide
either. `--strict` fails the build if either count is zero.

DENOMINATORS ARE PRINTED, NOT DOCUMENTED
-----------------------------------------
Every count in the output carries its denominator in the output itself. "9 roles covered" is
worthless; "9 of 40 roles have at least one recorded run" is a finding. The 2026-07-29 lesson
(`feedback_migrations-blind-instruments.md`) was a BLOCKING gate that passed by resolving
nothing -- 0 unsupported out of 0 resolvable. Check the denominator, not the verdict.

WHAT IT WRITES
---------------
  wiki/tracker/role-history.md     -- human digest, one section per role
  wiki/tracker/role-history.jsonl  -- machine rows

Both GENERATED. Do not hand-edit either; edit `role-episodes.jsonl` (the adjudicated input)
or the underlying definitions, and regenerate.

USAGE
------
  python scripts/audit/role_history.py              # generate
  python scripts/audit/role_history.py --dry-run    # print, write nothing
  python scripts/audit/role_history.py --verify     # citations only, exit 1 on any break
  python scripts/audit/role_history.py --strict     # generate; nonzero exit on any defect
  python scripts/audit/role_history.py --self-test  # the instrument checks itself
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import corpus_index as _CI          # noqa: E402  the ONE index reader (schema state included)

REPO = Path(__file__).resolve().parents[2]
CORPUS_INDEX = REPO / "wiki" / "tracker" / "corpus-index.jsonl"
EPISODES = REPO / "wiki" / "tracker" / "role-episodes.jsonl"
OUT_MD = REPO / "wiki" / "tracker" / "role-history.md"
OUT_JSONL = REPO / "wiki" / "tracker" / "role-history.jsonl"

AGENT_DEFS = REPO / ".claude" / "agents"
SKILLS_DIR = REPO / "skills"
CHARTER_GLOB = "coordination-charter-*.md"
CLAUDE_MD = REPO / "CLAUDE.md"
WIKI = REPO / "wiki"

# The CC project stores. Jon asked for "all their jsons and mds" -- the mds are the parsed
# corpus, the jsons are these. Both are enumerated; neither is read for content here.
CC_PROJECTS = Path(os.path.expanduser("~")) / ".claude" / "projects"

# Built-in agent types that have no file in .claude/agents/ but are real dispatch targets and
# appear in transcript filenames. Named here rather than inferred, so the roster's provenance
# is auditable per role (`def_source` in the output).
BUILTIN_AGENTS = ["general-purpose", "explore", "plan", "claude", "claude-code-guide",
                  "statusline-setup"]

# Session roles: no agent file, no skill directory, but a real role with a charter. The
# coordinator is the one Jon named first.
SESSION_ROLES = ["coordinator"]

SUBAGENT_FN = re.compile(r"^code-(\d{4}-\d{2}-\d{2})-([0-9a-f]{6})-(.+)\.md$")

# Transcript speaker headers. `## Human` is NOT always Jon -- hook feedback and task
# notifications render under it too, which is why episode attribution is adjudicated in the
# ledger and never inferred from the header alone. Recorded here so the next reader knows.
SPEAKER = {"## Human": "JON-OR-HOOK", "## Assistant": "COORDINATOR", "## Tool Result": "AGENT"}


# --------------------------------------------------------------------------------------
# roster
# --------------------------------------------------------------------------------------
def build_roster() -> tuple[dict, dict]:
    """Roster from three enumerable sources. Returns (roster, source_counts)."""
    roster: dict[str, dict] = {}
    counts = {"agent_defs": 0, "skills": 0, "builtin": 0, "session": 0}

    if AGENT_DEFS.is_dir():
        for p in sorted(AGENT_DEFS.glob("*.md")):
            roster[p.stem] = {"role": p.stem, "kind": "subagent",
                              "def_source": "agent-def",
                              "definition": str(p.relative_to(REPO)).replace("\\", "/"),
                              "definition_bytes": p.stat().st_size}
            counts["agent_defs"] += 1

    if SKILLS_DIR.is_dir():
        for d in sorted(SKILLS_DIR.iterdir()):
            sk = d / "SKILL.md"
            if not sk.is_file():
                continue
            counts["skills"] += 1
            if d.name in roster:
                roster[d.name]["also_skill"] = str(sk.relative_to(REPO)).replace("\\", "/")
                continue
            roster[d.name] = {"role": d.name, "kind": "skill-role",
                              "def_source": "skill",
                              "definition": str(sk.relative_to(REPO)).replace("\\", "/"),
                              "definition_bytes": sk.stat().st_size}

    for name in BUILTIN_AGENTS:
        if name not in roster:
            roster[name] = {"role": name, "kind": "builtin-agent",
                            "def_source": "builtin (no repo file)",
                            "definition": None, "definition_bytes": 0}
            counts["builtin"] += 1

    for name in SESSION_ROLES:
        if name not in roster:
            charters = sorted((REPO / "exchange").glob(CHARTER_GLOB))
            roster[name] = {
                "role": name, "kind": "session-role",
                "def_source": "charter + CLAUDE.md (session role, not an agent file)",
                "definition": (str(charters[0].relative_to(REPO)).replace("\\", "/")
                               if charters else None),
                "definition_bytes": charters[0].stat().st_size if charters else 0}
            counts["session"] += 1

    return roster, counts


# --------------------------------------------------------------------------------------
# half A -- runs
# --------------------------------------------------------------------------------------
def load_corpus_rows():
    """(rows, read) — rows PLUS the schema state of the index they came from.

    This used to skip every `#` line, which meant it never looked at the header at all: it was
    schema-BLIND, not schema-tolerant. That is a quieter version of the 2026-08-06 defect. If a
    future schema renames `kind`, `attribute_runs`'s `r.get("kind") == "subagent"` matches nothing
    and this file reports **0 runs for every role** — a clean, confident, wrong answer with no
    error anywhere. Reusing `corpus_index.read_index` puts the version comparison back and makes
    the state a value the caller has to carry.
    """
    read = _CI.read_index(CORPUS_INDEX)
    return list(read.rows.values()), read


def attribute_runs(rows: list[dict], roster: dict) -> tuple[dict, list, int]:
    """Map subagent transcripts to roles by filename slug, longest-alias-first.

    Returns (runs_by_role, unattributed_paths, subagent_total). Unattributed is returned, not
    swallowed: a role index that silently drops runs is the blind-instrument failure again.
    """
    aliases = sorted(roster.keys(), key=len, reverse=True)
    runs: dict[str, list] = defaultdict(list)
    unattributed: list[str] = []
    subs = [r for r in rows if r.get("kind") == "subagent"]

    for r in subs:
        base = os.path.basename(r["path"])
        m = SUBAGENT_FN.match(base)
        if not m:
            unattributed.append(r["path"])
            continue
        date, sid, slug = m.groups()
        slug_l = slug.lower()
        for a in aliases:
            al = a.lower()
            if slug_l == al or slug_l.startswith(al + "-"):
                runs[a].append({"date": date, "id": sid, "path": r["path"],
                                "turns": r.get("turn_count"), "size": r.get("size"),
                                "parent_id": r.get("parent_id"),
                                "desc": slug[len(a) + 1:].replace("-", " ") or None})
                break
        else:
            unattributed.append(r["path"])

    # A session role has no subagent transcripts -- it IS the main thread. Its runs are the
    # claude-code main-thread conversations. This is VENUE-level attribution, not slug-level:
    # it claims "every CC main-thread session in this repo was run by the coordinator role,"
    # which is true of the period the charter covers and is stated here so it can be argued
    # with rather than discovered. Marked `attribution: venue` on every row it produces.
    mains = [r for r in rows
             if r.get("kind") == "conversation" and r.get("venue") == "claude-code"]
    for role in SESSION_ROLES:
        if role not in roster:
            continue
        for r in mains:
            base = os.path.basename(r["path"])
            m = re.match(r"^code-(\d{4}-\d{2}-\d{2})-([0-9a-f]{6})-(.+)\.md$", base)
            if not m:
                continue
            date, sid, slug = m.groups()
            runs[role].append({"date": date, "id": sid, "path": r["path"],
                               "turns": r.get("turn_count"), "size": r.get("size"),
                               "parent_id": None, "attribution": "venue",
                               "desc": slug.replace("-", " ")})
    return runs, unattributed, len(subs)


def sidecar_and_jsonl(runs: dict) -> tuple[dict, dict, int]:
    """Count the .sidecar.md files and the CC .jsonl files behind each role's runs.

    Jon asked for "all their jsons and mds". The mds are the parsed transcripts; the jsons are
    the raw CC session JSONLs, which live outside the repo and are subject to the retention
    sweep. Presence is counted; nothing is read.
    """
    jsonl_by_prefix: dict[str, list[str]] = defaultdict(list)
    total_jsonl = 0
    if CC_PROJECTS.is_dir():
        for proj in CC_PROJECTS.iterdir():
            if not proj.is_dir():
                continue
            for f in proj.glob("*.jsonl"):
                total_jsonl += 1
                jsonl_by_prefix[f.stem[:6].lower()].append(str(f))

    sidecars: dict[str, int] = {}
    jsonls: dict[str, int] = {}
    for role, rs in runs.items():
        sc = 0
        for r in rs:
            if (REPO / (r["path"].replace(".md", ".sidecar.md"))).is_file():
                sc += 1
        sidecars[role] = sc
        jsonls[role] = sum(1 for r in rs if jsonl_by_prefix.get(r["id"].lower()))
    return sidecars, jsonls, total_jsonl


def wiki_mentions(roster: dict) -> tuple[dict, int]:
    """Files under wiki/ that name each role. Counted by walk, not by grep-per-role."""
    pages: dict[str, list] = defaultdict(list)
    names = {r: re.compile(re.escape(r), re.I) for r in roster}
    scanned = 0
    for p in WIKI.rglob("*.md"):
        rel = str(p.relative_to(REPO)).replace("\\", "/")
        if rel.startswith("wiki/tracker/role-history"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        for role, rx in names.items():
            if rx.search(text):
                pages[role].append(rel)
    return pages, scanned


def governing_clauses(roster: dict) -> dict:
    """Lines in CLAUDE.md and the coordination charter that name each role."""
    srcs = []
    if CLAUDE_MD.is_file():
        srcs.append(CLAUDE_MD)
    srcs.extend(sorted((REPO / "exchange").glob(CHARTER_GLOB)))
    out: dict[str, list] = defaultdict(list)
    for src in srcs:
        rel = str(src.relative_to(REPO)).replace("\\", "/")
        lines = src.read_text(encoding="utf-8", errors="replace").split("\n")
        for i, line in enumerate(lines, 1):
            low = line.lower()
            for role in roster:
                if role.lower() in low:
                    out[role].append({"path": rel, "line": i, "text": line.strip()[:200]})
    return out


# --------------------------------------------------------------------------------------
# half B -- episodes and citations
# --------------------------------------------------------------------------------------
def load_episodes() -> list[dict]:
    if not EPISODES.is_file():
        return []
    eps = []
    with EPISODES.open(encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if line.startswith("#") or not line.strip():
                continue
            try:
                eps.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  ledger line {n}: MALFORMED -- {e}", file=sys.stderr)
    return eps


def resolve_cite(cite: dict | None) -> dict:
    """Re-find the anchor in the cited file. This is what makes the ledger checkable.

    Returns {status, path, line, detail}. status is OK / DRIFTED / BROKEN / NO-CITE.
    DRIFTED means the anchor was found but not at line_hint -- the transcript grew, which it
    does constantly, and the citation is still good. Line numbers alone would rot in a day.
    """
    if not cite:
        return {"status": "NO-CITE", "path": None, "line": None, "detail": "row carries no cite"}
    kind = cite.get("kind")
    if kind == "commit":
        sha = cite.get("sha", "")
        try:
            subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=REPO,
                           check=True, capture_output=True)
            return {"status": "OK", "path": f"commit {sha}", "line": None, "detail": "commit exists"}
        except (subprocess.CalledProcessError, OSError):
            return {"status": "BROKEN", "path": f"commit {sha}", "line": None,
                    "detail": "commit not found"}

    rel = cite.get("path")
    if not rel:
        return {"status": "BROKEN", "path": None, "line": None, "detail": "cite has no path"}
    # RESOLUTION ROOTS, in order. Added 2026-09-05 (MI-3) after --verify --strict reported
    # 14 of 15 anchors BROKEN and the honest cause turned out to be the opposite of rot.
    #
    # `[measured 2026-09-05 19:1x]` Every one of the 14 cites into `raw/transcripts/`, which
    # is GITIGNORED -- so it has never existed in N:/claude-cfl/clone, the tree CFL moved
    # to on 09-02. The files are intact at N:/claude-corpus/cfl/raw/transcripts/,
    # byte-identical to the G: copy (4,268,945 B both sides, checked on one).
    #
    # THE LEDGER DID NOT ROT. THE CORPUS MOVED OUT FROM UNDER THE RESOLVER. That distinction
    # is the whole finding: `REPO` is derived from __file__, which is correct for repo_file
    # cites and wrong for transcript cites, because the transcript corpus is deliberately not
    # in the repo. Same class as the G12 relative-path default and tonight's R4b tree-path
    # pass -- a path resolved against a tree the caller did not intend.
    roots = [REPO] + [Path(r) for r in (
        os.environ.get("CFL_CORPUS_ROOT", ""),
        r"N:\claude-corpus\cfl",
        r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer",
    ) if r]
    p = None
    for _r in roots:
        _c = _r / rel
        try:
            if _c.is_file():
                p = _c
                break
        except OSError:
            continue
    if p is None:
        # ⛔ AND THE VERDICT SPLITS, because "this anchor is wrong" and "the corpus is not
        # mounted" are different findings that printed IDENTICALLY as BROKEN. A whole
        # unmounted corpus made every row read as a rotted citation -- an accusation against
        # the data produced by a fault in the reader. UNKNOWN dominates a PASS and it must
        # also dominate a BROKEN: never accuse a row when the population was unreachable.
        corpus_seen = any(_r.exists() for _r in roots[1:])
        if not corpus_seen:
            return {"status": "UNKNOWN", "path": rel, "line": None,
                    "detail": "corpus root unreachable -- not a broken cite; roots tried: "
                              + ", ".join(str(_r) for _r in roots)}
        return {"status": "BROKEN", "path": rel, "line": None,
                "detail": "file does not exist under any known root"}
    anchor = cite.get("anchor")
    if not anchor:
        return {"status": "OK", "path": rel, "line": None, "detail": "file exists (no anchor)"}
    text = p.read_text(encoding="utf-8", errors="replace")
    idx = text.find(anchor)
    if idx < 0:
        return {"status": "BROKEN", "path": rel, "line": None,
                "detail": "anchor not found in file"}
    line_no = text.count("\n", 0, idx) + 1
    hint = cite.get("line_hint")
    status = "OK" if (hint is None or hint == line_no) else "DRIFTED"
    return {"status": status, "path": rel, "line": line_no,
            "detail": f"anchor at line {line_no}" + (f" (hint said {hint})"
                                                     if status == "DRIFTED" else "")}


def harvest_memory_candidates(roster: dict) -> tuple[list, int, int]:
    """Pre-2026-08-06 episode CANDIDATES from the CC memory store's feedback_*.md files.

    These are documented, dated corrections -- the closest thing to a pre-existing role
    history that exists. They are emitted as CANDIDATES, never folded into the ratio, because
    the memory files record WHAT went wrong without reliably recording WHICH ROLE did it or
    WHO CAUGHT IT. A role is attached only when the file names it explicitly; otherwise the
    candidate is UNATTRIBUTED and says so. Guessing here would manufacture exactly the kind of
    uncited history this whole exercise exists to replace.
    """
    if not CC_PROJECTS.is_dir():
        return [], 0, 0
    stores = [d / "memory" for d in CC_PROJECTS.iterdir()
              if d.is_dir() and (d / "memory").is_dir()]
    cands, scanned, attributed = [], 0, 0
    date_rx = re.compile(r"(20\d\d-\d\d-\d\d)")
    for store in stores:
        for f in sorted(store.glob("feedback_*.md")):
            scanned += 1
            text = f.read_text(encoding="utf-8", errors="replace")
            named = sorted({r for r in roster
                            if re.search(r"\b" + re.escape(r) + r"\b", text, re.I)})
            dates = date_rx.findall(text)
            if named:
                attributed += 1
            cands.append({
                "candidate_id": f.stem,
                "date": min(dates) if dates else None,
                "roles_named": named or ["UNATTRIBUTED"],
                "attribution": "EXPLICIT" if named else "UNATTRIBUTED",
                "title": next((l.lstrip("# ").strip() for l in text.split("\n")
                               if l.startswith("# ")), f.stem),
                "cite": {"kind": "memory_file", "path": str(f).replace("\\", "/")},
            })
    return cands, scanned, attributed


# --------------------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------------------
def build(strict: bool = False) -> tuple[dict, int]:
    problems = 0
    roster, src_counts = build_roster()
    rows, index_read = load_corpus_rows()
    if not index_read.fresh:
        # NOT "absent or empty" -- that message conflated three states and misnamed two of them.
        print(index_read.banner("role_history"), file=sys.stderr)
        print(f"Runs-per-role from the corpus = UNKNOWN, not zero "
              f"[{index_read.status}; {index_read.n_rows_on_disk} rows on disk].",
              file=sys.stderr)
        problems += 1
    runs, unattributed, sub_total = attribute_runs(rows, roster)
    sidecars, jsonls, jsonl_total = sidecar_and_jsonl(runs)
    pages, wiki_scanned = wiki_mentions(roster)
    clauses = governing_clauses(roster)

    episodes = load_episodes()
    for ep in episodes:
        ep["_cite"] = resolve_cite(ep.get("cite"))
        ep["_remedy"] = resolve_cite(ep.get("remedy")) if ep.get("remedy") else None
        if ep["_cite"]["status"] == "BROKEN":
            problems += 1
    usable = [e for e in episodes if e["_cite"]["status"] in ("OK", "DRIFTED")]
    broken = [e for e in episodes if e["_cite"]["status"] not in ("OK", "DRIFTED")]

    valence = Counter(e.get("valence") for e in usable)
    caught = Counter(e.get("caught_by") for e in usable)
    unprompted_self = [e for e in usable
                       if e.get("caught_by") == "COORDINATOR" and e.get("unprompted") is True]
    defects = [e for e in usable if e.get("valence") == "DEFECT"]
    defect_self_unprompted = [e for e in defects
                              if e.get("caught_by") == "COORDINATOR" and e.get("unprompted") is True]

    if strict and (valence.get("DEFECT", 0) == 0 or valence.get("TRIUMPH", 0) == 0):
        print("STRICT: the ledger records only one valence. Balance is a requirement.",
              file=sys.stderr)
        problems += 1

    cands, mem_scanned, mem_attributed = harvest_memory_candidates(roster)

    eps_by_role: dict[str, list] = defaultdict(list)
    for e in usable:
        eps_by_role[e.get("role", "UNATTRIBUTED")].append(e)

    roles_with_runs = [r for r in roster if runs.get(r)]
    roles_with_eps = [r for r in roster if eps_by_role.get(r)]

    return {
        "roster": roster, "src_counts": src_counts, "runs": runs,
        "unattributed": unattributed, "sub_total": sub_total,
        "sidecars": sidecars, "jsonls": jsonls, "jsonl_total": jsonl_total,
        "pages": pages, "wiki_scanned": wiki_scanned, "clauses": clauses,
        "episodes": usable, "broken": broken, "eps_by_role": eps_by_role,
        "valence": valence, "caught": caught,
        "unprompted_self": unprompted_self, "defects": defects,
        "defect_self_unprompted": defect_self_unprompted,
        "candidates": cands, "mem_scanned": mem_scanned, "mem_attributed": mem_attributed,
        "roles_with_runs": roles_with_runs, "roles_with_eps": roles_with_eps,
        "corpus_rows": len(rows),
        # The state of the read lands in the ARTIFACT, not just on stderr. A generated page that
        # reports a count without reporting whether the count could be taken is the same defect
        # one layer out.
        "index_status": index_read.status,
        "index_schema_on_disk": index_read.schema_on_disk,
        "index_schema_expected": index_read.schema_expected,
        "index_rows_on_disk": index_read.n_rows_on_disk,
    }, problems


def pct(n: int, d: int) -> str:
    return f"{n}/{d} ({100.0 * n / d:.0f}%)" if d else f"{n}/0 (no denominator)"


def render_md(D: dict) -> str:
    roster, runs = D["roster"], D["runs"]
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    L: list[str] = []
    A = L.append

    A("# Agent Role History -- what each role is, what it did, and how it went")
    A("")
    A(f"**GENERATED** by `scripts/audit/role_history.py` at {now}. **Do not hand-edit.**")
    A("Edit `wiki/tracker/role-episodes.jsonl` (the adjudicated Half-B input) or the role")
    A("definitions themselves, then regenerate. Machine rows: `wiki/tracker/role-history.jsonl`.")
    A("")
    A("> *\"And I neeeed to have agent role history. Your history as a coordinator is key. My")
    A("> definitions of skills masters, wiki masters.... Their triumphs and their failures....")
    A("> All their jsons and mds. I don't like that I can't find them organized\"*")
    A("> -- Jon, 2026-08-06. PRIMARY (resurrected 2026-08-07):")
    A("> `raw/transcripts/claude-code/code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-updates.md:32383`,")
    A("> `## Human` turn. Verified word-for-word including `neeeed`.")
    A("")
    A("Half A (what a role DID) was **scattered, not missing** -- definitions, runs, JSONLs and")
    A("wiki mentions all existed, in four different places, joined nowhere. Half B (how it")
    A("WENT) was **genuinely missing**: hundreds of wiki files record what the coordinator did")
    A("and none of them score whether it was right.")
    A("")

    # ---- the number ----
    A("## The who-caught-it ratio")
    A("")
    A("The single most useful number here. Of the episodes on record, who found the problem?")
    A("Three catchers, and the distinction is the whole point: **JON** (the human, pushing),")
    A("**COORDINATOR** (the main thread, on its own initiative or after a push), **AGENT** (a")
    A("dispatched subagent finding it from inside its own run). `caught_by` is about position in")
    A("the session hierarchy, not about which role the episode is filed under.")
    A("")
    tot = len(D["episodes"])
    A(f"- **Episodes on record (citations resolved):** {tot}")
    A(f"- **Caught by JON:** {pct(D['caught'].get('JON', 0), tot)}")
    A(f"- **Caught by the COORDINATOR (main thread):** {pct(D['caught'].get('COORDINATOR', 0), tot)}")
    A(f"- **Caught by a dispatched AGENT:** {pct(D['caught'].get('AGENT', 0), tot)}")
    A(f"- **Caught by the coordinator UNPROMPTED:** {pct(len(D['unprompted_self']), tot)}")
    A("")
    nd = len(D["defects"])
    A(f"**Restricted to DEFECTS** (the number that actually matters), denominator {nd}:")
    A("")
    A(f"- **Coordinator caught it itself, unprompted:** {pct(len(D['defect_self_unprompted']), nd)}")
    A(f"- Everything else was surfaced by Jon pushing, by a dispatched agent, or by the")
    A(f"  coordinator only after being challenged: "
      f"{pct(nd - len(D['defect_self_unprompted']), nd)}")
    A("")
    A("The coordinator's own account of the same ratio, 2026-08-06, in the ledger as")
    A("`E-2026-08-06-04`: *\"I don't retrieve at all -- I answer from context and only check")
    A("when challenged. Every check today came from you pushing, not from me reaching.\"*")
    A("")
    A(f"**Balance check:** {D['valence'].get('DEFECT', 0)} DEFECT / "
      f"{D['valence'].get('TRIUMPH', 0)} TRIUMPH. A history that records only failures is a")
    A("flagellation, not a history; `--strict` fails the build if either side is empty.")
    A("")
    if D["broken"]:
        A(f"**{len(D['broken'])} ledger row(s) have BROKEN citations and are excluded from every")
        A("number above.** An uncited failure is gossip; an uncited triumph is marketing.")
        for e in D["broken"]:
            A(f"  - `{e.get('episode_id')}` -- {e['_cite']['detail']}")
        A("")

    # ---- denominators ----
    A("## Denominators")
    A("")
    A("| quantity | value |")
    A("|---|---|")
    A(f"| roles in the roster | **{len(roster)}** |")
    A(f"| ... from `.claude/agents/*.md` | {D['src_counts']['agent_defs']} |")
    A(f"| ... from `skills/*/SKILL.md` | {D['src_counts']['skills']} "
      f"(some overlap the agent defs) |")
    A(f"| ... built-in dispatch targets with no repo file | {D['src_counts']['builtin']} |")
    A(f"| ... session roles (charter only, no agent file) | {D['src_counts']['session']} |")
    A(f"| roles with **at least one recorded run** | **{pct(len(D['roles_with_runs']), len(roster))}** |")
    A(f"| roles with **at least one scored episode** | **{pct(len(D['roles_with_eps']), len(roster))}** |")
    A(f"| subagent transcripts in the corpus index | {D['sub_total']} |")
    A(f"| ... attributed to a role by filename slug | "
      f"{pct(D['sub_total'] - len(D['unattributed']), D['sub_total'])} |")
    A(f"| ... UNATTRIBUTED | {len(D['unattributed'])} |")
    A(f"| corpus-index rows read (all kinds) | {D['corpus_rows']} |")
    A(f"| corpus-index read status | **{D['index_status']}** "
      f"(on disk `{D['index_schema_on_disk']}`, expected `{D['index_schema_expected']}`, "
      f"{D['index_rows_on_disk']} rows present) |")
    if D["index_status"] != "FRESH":
        A("")
        A(f"> **EVERY RUN COUNT BELOW IS UNKNOWN, NOT ZERO.** The corpus index read "
          f"`{D['index_status']}`: {D['index_rows_on_disk']} rows are on disk but were written "
          f"to schema `{D['index_schema_on_disk']}` while this code speaks "
          f"`{D['index_schema_expected']}`. Rebuild with `python scripts/audit/corpus_index.py` "
          f"before quoting anything here.")
        A("")
    A(f"| wiki `.md` files scanned for role mentions | {D['wiki_scanned']} |")
    A(f"| CC session `.jsonl` files on disk (all projects) | {D['jsonl_total']} |")
    A(f"| memory-store `feedback_*.md` files harvested as candidates | "
      f"{pct(D['mem_attributed'], D['mem_scanned'])} name a role explicitly |")
    A("")
    A("**Read the denominators, not the verdicts.** On 2026-07-29 a BLOCKING gate in this repo")
    A("passed by resolving nothing -- 0 unsupported out of 0 resolvable.")
    A("")

    # ---- roster table ----
    A("## Roster")
    A("")
    A("| role | kind | definition | runs | first | last | wiki pages | charter lines | episodes (D/T) |")
    A("|---|---|---|---:|---|---|---:|---:|---|")
    for name in sorted(roster, key=lambda r: (-len(runs.get(r, [])), r)):
        meta = roster[name]
        rs = runs.get(name, [])
        dates = sorted(r["date"] for r in rs) if rs else []
        eps = D["eps_by_role"].get(name, [])
        d = sum(1 for e in eps if e.get("valence") == "DEFECT")
        t = sum(1 for e in eps if e.get("valence") == "TRIUMPH")
        defn = f"`{meta['definition']}`" if meta["definition"] else "_(built-in, no file)_"
        A(f"| **{name}** | {meta['kind']} | {defn} | {len(rs)} | "
          f"{dates[0] if dates else '--'} | {dates[-1] if dates else '--'} | "
          f"{len(D['pages'].get(name, []))} | {len(D['clauses'].get(name, []))} | "
          f"{d}/{t}" + (" |" if (d or t) else " |"))
    A("")
    A("`wiki pages` counts files under `wiki/` whose text contains the role name -- a mention,")
    A("not a page about the role. The gap between that column and the `episodes` column is the")
    A("whole point: mention is cheap, scoring is not.")
    A("")

    # ---- per role ----
    A("## Per-role record")
    A("")
    for name in sorted(roster, key=lambda r: (-len(runs.get(r, [])), r)):
        meta = roster[name]
        rs = sorted(runs.get(name, []), key=lambda r: (r["date"], r["id"]))
        eps = D["eps_by_role"].get(name, [])
        A(f"### {name}")
        A("")
        A(f"- **Kind:** {meta['kind']} ({meta['def_source']})")
        if meta["definition"]:
            A(f"- **Definition:** `{meta['definition']}` ({meta['definition_bytes']} bytes)")
        if meta.get("also_skill"):
            A(f"- **Also a skill:** `{meta['also_skill']}`")
        if meta["kind"] == "session-role":
            A("- **Attribution note:** this role has no subagent transcripts because it IS the")
            A("  main thread. Its runs below are the claude-code main-thread conversations,")
            A("  attributed by VENUE rather than by filename slug -- a claim about the period,")
            A("  not a per-file fact. Argue with it here rather than downstream.")
        A(f"- **Runs (parsed `.md` transcripts):** {len(rs)}"
          + (f" -- {rs[0]['date']} to {rs[-1]['date']}" if rs else ""))
        A(f"- **Per-turn sidecars present:** {pct(D['sidecars'].get(name, 0), len(rs))}")
        A(f"- **Runs whose raw CC `.jsonl` still exists on disk:** "
          f"{pct(D['jsonls'].get(name, 0), len(rs))}"
          + ("  <-- the retention sweep eats these; the `.md` is the durable copy"
             if rs and D["jsonls"].get(name, 0) < len(rs) else ""))
        pg = D["pages"].get(name, [])
        A(f"- **Wiki pages naming it:** {len(pg)}"
          + (f" -- e.g. {', '.join('`' + x + '`' for x in pg[:5])}" if pg else ""))
        cl = D["clauses"].get(name, [])
        A(f"- **Governing clauses (CLAUDE.md / charter):** {len(cl)}")
        for c in cl[:4]:
            A(f"  - `{c['path']}:{c['line']}` -- {c['text']}")
        A("")
        if rs:
            A(f"<details><summary>All {len(rs)} runs</summary>")
            A("")
            A("| date | id | turns | description | transcript |")
            A("|---|---|---:|---|---|")
            for r in rs:
                A(f"| {r['date']} | `{r['id']}` | {r['turns'] or '--'} | "
                  f"{(r['desc'] or '--')[:70]} | `{r['path']}` |")
            A("")
            A("</details>")
            A("")
        if eps:
            A(f"**Scored episodes ({len(eps)}):**")
            A("")
            for e in sorted(eps, key=lambda x: x.get("episode_id", "")):
                mark = "FAILURE" if e.get("valence") == "DEFECT" else "TRIUMPH"
                who = e.get("caught_by")
                up = "unprompted" if e.get("unprompted") is True else "after a push"
                A(f"- **[{mark}] {e.get('title')}** (`{e.get('episode_id')}`, {e.get('date')})")
                A(f"  - {e.get('detail')}")
                A(f"  - **Caught by:** {who}, {up}")
                c = e["_cite"]
                A(f"  - **Cite:** `{c['path']}`"
                  + (f" line {c['line']}" if c["line"] else "")
                  + f" -- {c['status']}"
                  + (f" (`{e['cite'].get('anchor')}`)" if e.get("cite", {}).get("anchor") else ""))
                if e.get("_remedy"):
                    r = e["_remedy"]
                    A(f"  - **Remedy:** `{r['path']}`"
                      + (f" line {r['line']}" if r["line"] else "") + f" -- {r['status']}")
            A("")
        else:
            A("**Scored episodes: 0.** Nothing on record about how this role's runs went. "
              "That is a gap in the ledger, not evidence the runs were clean.")
            A("")

    # ---- candidates ----
    A("## Unadjudicated candidates (pre-2026-08-06)")
    A("")
    A(f"Harvested from {D['mem_scanned']} `feedback_*.md` files in the CC memory store -- the")
    A("only pre-existing corpus of dated, documented corrections. They are **candidates, not")
    A("episodes**: they record what went wrong without reliably recording which role did it or")
    A("who caught it, so **none of them enter the ratio above.** A role name is attached only")
    A("where the file states one.")
    A("")
    A("| date | file | roles named explicitly |")
    A("|---|---|---|")
    for c in sorted(D["candidates"], key=lambda x: (x["date"] or "0000", x["candidate_id"])):
        A(f"| {c['date'] or '--'} | `{c['candidate_id']}` | {', '.join(c['roles_named'])} |")
    A("")
    A("**To promote a candidate:** find the transcript that shows it, add a row to")
    A("`wiki/tracker/role-episodes.jsonl` with a resolvable anchor and an adjudicated")
    A("`caught_by`, and regenerate. The ratio moves only on cited evidence.")
    A("")

    if D["unattributed"]:
        A("## Unattributed runs")
        A("")
        A(f"{len(D['unattributed'])} subagent transcript(s) could not be mapped to a roster")
        A("role by filename slug. Listed rather than dropped.")
        A("")
        for p in D["unattributed"][:40]:
            A(f"- `{p}`")
        A("")

    A("## Method, and what it does not do")
    A("")
    A("- **Half A is a join, not a scan.** Runs come from `wiki/tracker/corpus-index.jsonl`;")
    A("  this script does not define a sixth corpus. If that index is stale, so is this page.")
    A("- **Role attribution is by filename slug**, longest-alias-first. It captures the *agent")
    A("  type dispatched*, which is not always the *role performed*: runs dispatched to the")
    A("  built-in `claude` type have carried out wiki-master and project-manager work. Those")
    A("  are counted under `claude`, and the description column is where that shows.")
    A("- **`## Human` in a transcript is not always Jon.** Hook feedback and task notifications")
    A("  render under the same header. This is why `caught_by` is adjudicated in the ledger and")
    A("  never inferred from the header.")
    A("- **Citations are re-resolved by anchor on every run**, not stored as line numbers. Live")
    A("  transcripts grow; `DRIFTED` means the anchor moved and is still good, `BROKEN` means")
    A("  the claim no longer has evidence and is dropped from every statistic.")
    A("- **The ledger is incomplete by construction.** It is seeded from one heavily-documented")
    A("  day. Roles showing 0 episodes have not been scored, which is not the same as clean.")
    return "\n".join(L) + "\n"


def render_jsonl(D: dict) -> str:
    hdr = {
        "schema": "role-history-v1",
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "generated_by": "scripts/audit/role_history.py",
        "note": "GENERATED -- do not hand-edit. Regenerate from role-episodes.jsonl + corpus-index.jsonl.",
        "roles": len(D["roster"]),
        "roles_with_runs": len(D["roles_with_runs"]),
        "roles_with_episodes": len(D["roles_with_eps"]),
        "subagent_transcripts": D["sub_total"],
        "unattributed_runs": len(D["unattributed"]),
        "episodes_resolved": len(D["episodes"]),
        "episodes_broken": len(D["broken"]),
        "defects": len(D["defects"]),
        "defects_self_caught_unprompted": len(D["defect_self_unprompted"]),
        "caught_by": dict(D["caught"]),
        "valence": dict(D["valence"]),
    }
    out = ["#" + json.dumps(hdr, sort_keys=True)]
    for name in sorted(D["roster"]):
        meta = D["roster"][name]
        rs = D["runs"].get(name, [])
        dates = sorted(r["date"] for r in rs)
        eps = D["eps_by_role"].get(name, [])
        out.append(json.dumps({
            "role": name, "kind": meta["kind"], "def_source": meta["def_source"],
            "definition": meta["definition"], "runs": len(rs),
            "first_run": dates[0] if dates else None, "last_run": dates[-1] if dates else None,
            "sidecars": D["sidecars"].get(name, 0), "jsonls_on_disk": D["jsonls"].get(name, 0),
            "wiki_pages": len(D["pages"].get(name, [])),
            "governing_clauses": len(D["clauses"].get(name, [])),
            "episodes": [{"id": e.get("episode_id"), "date": e.get("date"),
                          "valence": e.get("valence"), "caught_by": e.get("caught_by"),
                          "unprompted": e.get("unprompted"), "title": e.get("title"),
                          "cite_status": e["_cite"]["status"], "cite_path": e["_cite"]["path"],
                          "cite_line": e["_cite"]["line"]} for e in eps],
            "run_paths": [r["path"] for r in rs],
        }, sort_keys=True))
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------------------
def self_test() -> int:
    """The instrument checks itself. An index that cannot fail cannot be trusted."""
    fails = 0

    def chk(name, cond, detail=""):
        nonlocal fails
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
        if not cond:
            fails += 1

    roster, counts = build_roster()
    chk("roster non-empty", len(roster) > 0, f"{len(roster)} roles")
    chk("agent defs found", counts["agent_defs"] > 0, f"{counts['agent_defs']}")
    chk("coordinator in roster", "coordinator" in roster)

    rows, _read = load_corpus_rows()
    chk("corpus index readable", len(rows) > 0, f"{len(rows)} rows")
    chk("corpus index reports a schema STATE, not just rows",
        _read.status in ("FRESH", "STALE_SCHEMA", "ABSENT", "MALFORMED_HEADER"),
        _read.one_line())

    # STALE-SCHEMA CONTROLS — both directions, on a temp index. Real artifacts untouched.
    import tempfile
    with tempfile.TemporaryDirectory() as _td:
        _p = Path(_td) / "idx.jsonl"

        def _at(schema, n=3):
            _p.write_text("#" + json.dumps({"schema": schema}) + "\n" + "".join(
                json.dumps({"path": f"a/{i}.md", "kind": "subagent"}) + "\n"
                for i in range(n)), encoding="utf-8")
            return _CI.read_index(_p)

        chk("temp FRESH index -> FRESH", _at(_CI.SCHEMA_VERSION).status == "FRESH")
        _s = _at("corpus-index-v0")
        chk("temp STALE index -> STALE_SCHEMA (previously this reader never even LOOKED)",
            _s.status == "STALE_SCHEMA")
        chk("STALE index still names 3 rows on disk, so it cannot be called absent",
            _s.n_rows_on_disk == 3)
        chk("absent index -> ABSENT, distinct from STALE",
            _CI.read_index(Path(_td) / "nope.jsonl").status == "ABSENT")

    runs, unattr, tot = attribute_runs(rows, roster)
    chk("attribution covers >90% of subagent runs",
        tot and (tot - len(unattr)) / tot > 0.9, f"{tot - len(unattr)}/{tot}")

    # A broken cite MUST be detected. If this passes when it should not, every number lies.
    bad = resolve_cite({"kind": "repo_file", "path": "wiki/does-not-exist-zzz.md"})
    chk("missing file detected as BROKEN", bad["status"] == "BROKEN", bad["detail"])
    bad2 = resolve_cite({"kind": "repo_file", "path": "CLAUDE.md",
                         "anchor": "zzz-this-string-is-not-in-claude-md-zzz"})
    chk("missing anchor detected as BROKEN", bad2["status"] == "BROKEN", bad2["detail"])
    good = resolve_cite({"kind": "repo_file", "path": "CLAUDE.md", "anchor": "Coordinator"})
    chk("present anchor resolves OK", good["status"] in ("OK", "DRIFTED"), good["detail"])

    eps = load_episodes()
    chk("ledger loads", len(eps) > 0, f"{len(eps)} rows")
    res = [resolve_cite(e.get("cite")) for e in eps]
    nbad = sum(1 for r in res if r["status"] not in ("OK", "DRIFTED"))
    chk("every ledger row resolves", nbad == 0, f"{nbad} broken of {len(eps)}")
    val = Counter(e.get("valence") for e in eps)
    chk("ledger carries both valences",
        val.get("DEFECT", 0) > 0 and val.get("TRIUMPH", 0) > 0,
        f"{val.get('DEFECT', 0)} DEFECT / {val.get('TRIUMPH', 0)} TRIUMPH")
    cb = Counter(e.get("caught_by") for e in eps)
    chk("ledger distinguishes all three catchers",
        len({k for k in cb if k in ("JON", "COORDINATOR", "AGENT")}) == 3, str(dict(cb)))

    print(f"\n{'SELF-TEST PASS' if not fails else f'SELF-TEST FAIL ({fails})'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print summary, write nothing")
    ap.add_argument("--verify", action="store_true", help="resolve citations only; exit 1 on break")
    ap.add_argument("--strict", action="store_true", help="nonzero exit on any defect")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.verify:
        eps = load_episodes()
        bad = 0
        print(f"Resolving {len(eps)} ledger citation(s):")
        for e in eps:
            r = resolve_cite(e.get("cite"))
            print(f"  [{r['status']:8s}] {e.get('episode_id')}  {r['detail']}")
            if r["status"] not in ("OK", "DRIFTED"):
                bad += 1
        print(f"\n{len(eps) - bad}/{len(eps)} resolve. {bad} BROKEN.")
        return 1 if bad else 0

    D, problems = build(strict=args.strict)

    tot, nd = len(D["episodes"]), len(D["defects"])
    print(f"roles                      {len(D['roster'])}")
    print(f"roles with >=1 run         {pct(len(D['roles_with_runs']), len(D['roster']))}")
    print(f"roles with >=1 episode     {pct(len(D['roles_with_eps']), len(D['roster']))}")
    print(f"subagent runs attributed   {pct(D['sub_total'] - len(D['unattributed']), D['sub_total'])}")
    print(f"episodes resolved          {tot} ({len(D['broken'])} broken, excluded)")
    print(f"  valence                  {D['valence'].get('DEFECT', 0)} DEFECT / "
          f"{D['valence'].get('TRIUMPH', 0)} TRIUMPH")
    print(f"  caught by JON            {pct(D['caught'].get('JON', 0), tot)}")
    print(f"  caught by COORDINATOR    {pct(D['caught'].get('COORDINATOR', 0), tot)}")
    print(f"  caught by a subAGENT     {pct(D['caught'].get('AGENT', 0), tot)}")
    print(f"WHO-CAUGHT-IT (defects):   self-caught unprompted "
          f"{pct(len(D['defect_self_unprompted']), nd)}")
    print(f"candidates (unadjudicated) {pct(D['mem_attributed'], D['mem_scanned'])} name a role")

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 1 if (args.strict and problems) else 0

    OUT_MD.write_text(render_md(D), encoding="utf-8")
    OUT_JSONL.write_text(render_jsonl(D), encoding="utf-8")
    print(f"\nwrote {OUT_MD.relative_to(REPO)} ({OUT_MD.stat().st_size} bytes)")
    print(f"wrote {OUT_JSONL.relative_to(REPO)} ({OUT_JSONL.stat().st_size} bytes)")
    return 1 if (args.strict and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
