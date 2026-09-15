#!/usr/bin/env python3
"""corpus_index.py — an INDEX over the transcript corpus, so retrieval stops being a grep.

WHY THIS EXISTS — Jon, verbatim, 2026-08-06
---------------------------------------------
    "I think the full corpus of all our conversations makes almost everything findable, and I
     treat you not having it as a defect."

    "I don't know how to trace things to their original sources. If I search, I am using file
     names and we don't name things the same way in our heads so that's not durrible."

The corpus holds the answers and nothing queried it. Filename search is the only retrieval
Jon has, and it fails for the reason he names: **the name in his head is not the name on the
file.** An index over marker-presence and trigger-presence is searchable by what a session
DID, not by what somebody happened to call it.

Measured by grep on 2026-08-06 before this existed: FBC structural markers in 170 files,
`handoff` 692, `wayfinder` 509, `/gbs` 158, `"grill me"` 142. **Those greps took minutes each.**
That is the whole argument for an index rather than a scan — the answer was always obtainable
and never cheap enough to obtain.

WHAT IT IS NOT
---------------
It is **not a sixth corpus definition.** Five scanners already walk `raw/transcripts/`, and a
divergent corpus definition is the defect this repo spent the week removing. So:

  * `CORPUS` and `EXCLUDE_SUFFIXES` are **imported** from `coverage_gap.py`, not re-declared.
  * Every row carries `in_coverage_gap_scope`, which is TRUE exactly when `coverage_gap.py`
    would have counted this file. `coverage_gap`'s corpus is therefore a **derivable subset of
    this index** rather than a second opinion about it. If the two ever disagree, the row is
    wrong and the disagreement is visible instead of silent.
  * This index is DELIBERATELY WIDER: it includes `subagents/` and files with `turn_count < 2`,
    both of which `coverage_gap` excludes for its own good reasons. Skills fire inside subagent
    runs; an index that dropped 1,300 subagent transcripts could not answer the question it was
    built for. The `kind` field makes the wide set filterable back down to any narrower one.

WHAT LANDS IN THE INDEX, AND WHAT MUST NEVER
----------------------------------------------
Ids, paths, dates, sizes, turn counts, and marker/trigger PRESENCE. **No transcript content.**
Not a quoted line, not a snippet, not a title pulled from frontmatter. The index says
*"file X contains the FBC commit marker"*; reading what it said is a separate act against the
gitignored corpus.

WHERE IT LANDS, AND WHY — the choice was between two real costs
-----------------------------------------------------------------
Artifacts: `wiki/tracker/corpus-index.jsonl` (machine) + `wiki/tracker/corpus-index.md`
(human digest). **Tracked, not gitignored.** Three reasons, in order of weight:

 1. **`raw/` is gitignored, so an index there is unfalsifiable.** Hard requirement #1 is
    "generated, never hand-maintained" — and the only cheap way to CHECK that is to regenerate
    and read the git diff. In gitignored space there is no diff, so a hand-edit is invisible,
    which is the exact failure mode (`MEMORY.md` diverged from its own store by two files on
    2026-08-06 and nothing noticed).
 2. **Jon's ruling in force, verbatim, 2026-08-06:** *"I'm not worried about anything sensitive
    landing in CFL. You don't need stronger fences. You need to stop adding conservatism into
    my words."* Withholding this to `raw/` on my own judgment about personal-trunk filenames
    would be exactly that. `publication_screen.py` is UNWIRED for this reason and
    `agent_end_ingest.py` writes into `wiki/` by default; this follows the same in-force posture.
 3. `wiki/tracker/` already publishes generated files (`skills-frontmatter-digest.md`), is an
    existing `wiki/` child so `regenerate_canonical.sh`'s fail-closed check does not fire, and
    is on the cold-open read chain in CLAUDE.md — a session can reach it.

**THE COST OF THAT CHOICE, STATED SO NOBODY IS SURPRISED BY IT.** The JSONL carries repo-relative
paths for personal- and home-trunk transcripts, and `wiki/tracker/` publishes to the `canonical`
branch. Those paths are *slugs* — `claude-ai/personal/personal-conversation-prep/...` — never
content. If Jon decides slugs are too much, the fix is one constant (`OUT_DIR`) and a re-run;
nothing else depends on the location. **That is a Jon call, not mine, and it is not made here.**

REUSE — stated exactly, including where reuse would have been overclaiming
----------------------------------------------------------------------------
  * `coverage_gap.CORPUS` / `.EXCLUDE_SUFFIXES` — **imported.** One corpus root, one sidecar rule.
  * `turn_index.index()` — **imported.** The ratified turn enumerator, fence-aware. Used for
    turn counts AND to isolate Jon's turns, so a trigger phrase can be attributed to the person
    who would actually have triggered the skill.
  * `jon_utterances.normalize()` — **imported.** The one normalisation (whitespace-collapse +
    case-fold) that fixed five false zero-echo flags in `find_unechoed_rulings.py`.
  * `agent_end_ingest.py`'s idempotence pattern — **copied in concept, not imported.** Its key is
    `(agent_id, size, mtime)` over JSONLs; ours is `(path, size, mtime)` over markdown. Same
    shape, different key space; importing would have coupled two unrelated stores.
  * `check_jon_word_coverage.py`'s 40-char/stride-20 WINDOWING — **deliberately NOT used, and
    saying so matters.** Windowing exists to fingerprint LONG utterances that may be line-wrapped
    mid-span. Every marker and trigger literal here is shorter than one window, so windowing would
    add nothing; the load-bearing half of that matcher is `normalize`, which IS imported. Claiming
    to have reused the matcher would have overstated it.

THE MARKER REGISTRY IS SMALL AND SAYS SO
------------------------------------------
Triggers are **generated** from each `skills/*/SKILL.md` frontmatter description (quoted phrases,
`/slug`, and the skill name) — no hand list. Markers **cannot** be generated: a structural output
signature is a fact about the skill's output template, and most CFL skills do not declare one.
So markers are DECLARED here, verified line-by-line against each SKILL.md, and the run prints
`declared / total` as a denominator. **A skill with no declared marker reports UNDECLARED, never
zero.** Zero uses and no way to detect a use are different findings and are never merged.

THE CONSUMER
-------------
`scripts/audit/skill_usage.py` (next) needs three classes per skill: USED (marker present),
PARTIAL (marker present, completion shape absent), APPLICABLE-NOT-USED (declared trigger present
in Jon's turns, no marker). `--query-skill` implements that query against the index and is the
reference implementation `skill_usage.py` should import rather than re-derive.

Exit code is **always 0.** This is an instrument, not a gate. It only ever READS `raw/`.

Usage:
  corpus_index.py                       # incremental build (skips unchanged by size+mtime)
  corpus_index.py --full                # ignore the prior index; rescan everything
  corpus_index.py --dry-run             # measure and report, write nothing
  corpus_index.py --query-skill NAME    # the three-class query, from the index
  corpus_index.py --self-test           # negative controls
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_HERE = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent
for _p in (str(_SCRIPTS), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import coverage_gap as CG          # noqa: E402  corpus root + sidecar rule (imported, not copied)
import jon_utterances as JU        # noqa: E402  the one normalisation
from turn_index import index as turn_index      # noqa: E402  ratified turn enumerator

REPO = Path(__file__).resolve().parents[2]
CORPUS = CG.CORPUS                              # "raw/transcripts"
EXCLUDE_SUFFIXES = CG.EXCLUDE_SUFFIXES          # (".sidecar.md",)
CG_EXCLUDE_DIRS = CG.EXCLUDE_DIRS               # what coverage_gap drops; we KEEP and label

OUT_DIR = REPO / "wiki" / "tracker"
OUT_JSONL = OUT_DIR / "corpus-index.jsonl"
OUT_MD = OUT_DIR / "corpus-index.md"

SCHEMA_VERSION = "corpus-index-v2"      # v2 adds turn POSITIONS (see "TURN-SCOPED" below)

HEX6 = re.compile(r"^[0-9a-f]{6}$")
DATE_IN_NAME = re.compile(r"(20\d\d-\d\d-\d\d)")
FM_DATE = re.compile(r"^\s*(?:date|created_at|last_message):\s*(20\d\d-\d\d-\d\d)", re.M)
TRUNKS = ("fl", "personal", "pro", "home")

# =================================================================================================
# MARKER REGISTRY — DECLARED, NOT GENERATED, AND THE DENOMINATOR IS PRINTED
# =================================================================================================
# A `marker` is a literal that appears in the OUTPUT of a run, taken verbatim from the skill's own
# SKILL.md output template. `completion` is the literal that only a FINISHED run emits; when it is
# None the skill declares no completion shape and PARTIAL is UNDETECTABLE for it — reported as
# such, never as zero. Every entry below was read out of the named file, not recalled.
MARKERS = {
    # skills/frame-before-commit/SKILL.md:71,73,108,117 — output template
    "frame-before-commit": {
        "marker": ["[frame-before-commit", "[branch registry]"],
        "completion": ["[commit]"],
        "src": "skills/frame-before-commit/SKILL.md:71,73,117",
    },
    # skills/present-to-jon/SKILL.md — "Briefing Format": [FINDINGS] .. [JON SELECTION]
    "present-to-jon": {
        "marker": ["[findings]"],
        "completion": ["[jon selection]"],
        "src": "skills/present-to-jon/SKILL.md (Briefing Format)",
    },
    # skills/handoff/SKILL.md:71,80 — "Output Format" headings
    "handoff": {
        "marker": ["## what was accomplished this session"],
        "completion": ["## next steps"],
        "src": "skills/handoff/SKILL.md:71,80",
    },
    # skills/wayfinder/SKILL.md:59,69 — "The map body"
    "wayfinder": {
        "marker": ["## decisions so far"],
        "completion": ["## out of scope"],
        "src": "skills/wayfinder/SKILL.md:59,69",
    },
    # skills/reverse-grill-me/SKILL.md:76,81 — "Output — Surviving Claims Inventory"
    "reverse-grill-me": {
        "marker": ["surviving claims"],
        "completion": None,          # SKILL.md declares a summary section but no unique literal
        "src": "skills/reverse-grill-me/SKILL.md:76,81",
    },
    # skills/ground-before-stating/SKILL.md:51,55,57 — Rules 2/4/5 emit these inline tags
    "ground-before-stating": {
        "marker": ["[unverified]", "[training]", "[vtt assumed"],
        "completion": None,          # GBS is a mode, not a document; no terminal shape exists
        "src": "skills/ground-before-stating/SKILL.md:51,55,57",
    },
}


# =================================================================================================
# TRIGGERS — GENERATED from skills/*/SKILL.md frontmatter. No hand list.
# =================================================================================================
def load_skills(repo=REPO):
    """{slug: {'triggers': [...], 'has_skill_md': bool}} for every skills/<slug>/SKILL.md.

    Triggers come from the frontmatter `description`, which is the ONLY declaration of a trigger
    the harness itself reads. Three generated forms:
      * every quoted phrase in the description (straight and curly quotes) — this is how CFL
        skills spell their triggers, e.g. "frame before commit", "grill me", "ratchet this skill"
      * `/slug`  — the slash-command form
      * the slug with hyphens as spaces — how a person types it
    Short and generic phrases are dropped (MIN_TRIGGER_LEN); "status" or "handoff" alone would
    match half the corpus and turn APPLICABLE-NOT-USED into noise.
    """
    MIN_TRIGGER_LEN = 8
    out = {}
    sk = repo / "skills"
    if not sk.is_dir():
        return out
    for d in sorted(p for p in sk.iterdir() if p.is_dir()):
        f = d / "SKILL.md"
        if not f.is_file():
            continue
        try:
            head = f.read_text(encoding="utf-8", errors="replace")[:6000]
        except OSError:
            continue
        m = re.search(r"^---\s*$(.*?)^---\s*$", head, re.S | re.M)
        fm = m.group(1) if m else ""
        dm = re.search(r"^description:\s*(.+?)(?=^\w[\w-]*:|\Z)", fm, re.S | re.M)
        desc = dm.group(1) if dm else ""
        phrases = set()
        for q in re.findall(r'"([^"]{3,60})"', desc) + re.findall(r"[“]([^”]{3,60})[”]", desc):
            p = JU.normalize(q)
            if len(p) >= MIN_TRIGGER_LEN:
                phrases.add(p)
        spaced = JU.normalize(d.name.replace("-", " "))
        if len(spaced) >= MIN_TRIGGER_LEN:
            phrases.add(spaced)
        # THE SLASH FORM IS A REGEX, NOT A SUBSTRING, AND THIS WAS FOUND BY CHECKING THE OUTPUT.
        # `/frame-before-commit` as a plain substring matched inside the PATH
        # `skills/frame-before-commit/SKILL.md` — a session that merely LISTED the skill file
        # scored as Jon invoking it. Anchored to a whitespace/start boundary and forbidden from
        # being followed by another path character, which is what distinguishes a slash command
        # from a directory.
        out[d.name] = {
            "triggers": sorted(phrases),
            "slash": re.compile(r"(?:^|\s)/" + re.escape(d.name) + r"(?![\w/.-])"),
            "src": f"skills/{d.name}/SKILL.md",
        }
    return out


# =================================================================================================
# WALK — one corpus, wider than coverage_gap's, with the difference recorded per row
# =================================================================================================
def walk_corpus(repo=REPO):
    """[(abs_path, rel_path)] for every .md under raw/transcripts, sidecars EXCLUDED.

    Sidecars are dropped for coverage_gap's own reason: a `.sidecar.md` is a manifest COMPANION
    (block timestamps, tool-read logs), never a conversation, and counting 208 of them inflated
    that script's denominator by 76% on its first run. Same rule, imported, not re-decided.
    """
    base = repo / CORPUS
    out = []
    if not base.is_dir():
        return out
    for dirpath, dirnames, files in os.walk(base):
        dirnames.sort()
        for fn in sorted(files):
            if not fn.endswith(".md") or fn.endswith(EXCLUDE_SUFFIXES):
                continue
            p = Path(dirpath) / fn
            out.append((p, str(p.relative_to(repo)).replace("\\", "/")))
    return out


def classify_path(rel):
    """(venue, trunk, kind, parent_id) from the path alone. UNKNOWN is written, never guessed."""
    parts = rel.split("/")            # raw/transcripts/<venue>/...
    # A file sitting DIRECTLY in raw/transcripts/ (skip-registry.md, AUDIT-NOTES.md) has no venue
    # segment at all. Taking parts[2] blindly made `skip-registry.md` appear as a venue in the
    # first run — a partition row that is a filename is a tell that the partition is wrong.
    if len(parts) == 3:
        return "root", "UNKNOWN", "note", None
    venue = parts[2] if len(parts) > 2 else "UNKNOWN"
    rest = parts[3:]
    trunk, kind, parent = "UNKNOWN", "conversation", None
    if rest and rest[0] == "subagents":
        kind = "subagent"
        parent = rest[1] if len(rest) > 2 and HEX6.match(rest[1]) else None
        # a subagent's trunk is its PARENT's trunk and is not on its own path. Not guessed here;
        # a consumer that wants it joins on parent_id.
    elif rest and rest[0] in TRUNKS:
        trunk = rest[0]
    elif rest and rest[0].startswith("_"):
        kind = "routing"              # _routing/, _superseded/
    if any(x in CG_EXCLUDE_DIRS for x in rest):
        kind = "subagent" if kind == "conversation" else kind
    return venue, trunk, kind, parent


def file_id(stem):
    """(id, id_source). The 6-hex token; the one AFTER the date when a date is present.

    Both corpus naming conventions put a hex6 in the stem but in different places:
      claude-code : code-2026-05-09-02ff5b-export-...   -> hex follows the date
      claude-ai   : fbc-pure-3branch-2026-04-15-d03c80  -> hex follows the date too, at the end
    A stem with no hex6 is `UNKNOWN`, not a hash of the name — a fabricated id would join wrong.
    """
    toks = stem.split("-")
    hexes = [(i, t) for i, t in enumerate(toks) if HEX6.match(t)]
    if not hexes:
        return "UNKNOWN", "none-in-filename"
    dm = [i for i, t in enumerate(toks) if re.fullmatch(r"20\d\d", t)]
    if dm:
        after = [t for i, t in hexes if i > dm[0]]
        if after:
            return after[0], "after-date"
    return hexes[-1][1], "last-hex6"


def extract_date(stem, head):
    m = DATE_IN_NAME.search(stem)
    if m:
        return m.group(1), "filename"
    m = FM_DATE.search(head)
    if m:
        return m.group(1), "frontmatter"
    return "UNKNOWN", "none"


def scan_file(path, rel, skills, marker_reg=MARKERS):
    """One row. Reads the file; writes nothing anywhere. Content never leaves this function."""
    st = path.stat()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    stem = path.stem
    venue, trunk, kind, parent = classify_path(rel)
    fid, id_src = file_id(stem)
    date, date_src = extract_date(stem, text[:2000])

    # --- turn structure, via the ratified enumerator (fence-aware; a marker inside a code fence
    # --- is still indexed, but turn ATTRIBUTION must not be fooled by fenced pseudo-headers).
    try:
        ti = turn_index(str(path))
        turns = ti["turns"]
        n_turns = ti["turn_count"]
        total_lines = ti["total_lines"]
    except Exception:
        turns, n_turns, total_lines = [], 0, text.count("\n") + 1

    # --- Jon's spans only. A trigger phrase in the ASSISTANT's prose is not a trigger; it is the
    # --- assistant talking about the skill. Conflating them makes APPLICABLE-NOT-USED meaningless.
    lines = text.splitlines()
    human_chunks = []
    for i, t in enumerate(turns):
        if t["role"] != "H":
            continue
        start = t["line"]                                   # 1-based
        end = turns[i + 1]["line"] - 1 if i + 1 < len(turns) else len(lines)
        human_chunks.append("\n".join(lines[start:end]))
    norm_all = JU.normalize(text)
    norm_human = JU.normalize("\n".join(human_chunks)) if human_chunks else ""

    # --- SEGMENTS: the same slicing, kept once, so turn POSITIONS can be recorded (schema v2).
    # Turn 0 is the PREAMBLE — everything above T1 (frontmatter, export header). It is a real
    # region of the file and a marker can sit in it; if it had no segment number the per-turn
    # union would silently be a strict subset of the file-level fields, which is exactly the
    # kind of quiet disagreement between two views of one file that this index exists to prevent.
    seg = []
    if turns:
        seg.append((0, "P", JU.normalize("\n".join(lines[:turns[0]["line"] - 1]))))
    for i, t in enumerate(turns):
        start = t["line"]
        end = turns[i + 1]["line"] - 1 if i + 1 < len(turns) else len(lines)
        seg.append((t["t"], t["role"], JU.normalize("\n".join(lines[start:end]))))

    markers, completions = [], []
    for slug, spec in marker_reg.items():
        if any(m in norm_all for m in spec["marker"]):
            markers.append(slug)
            comp = spec.get("completion")
            if comp and any(c in norm_all for c in comp):
                completions.append(slug)

    trig_any, trig_human = [], []
    for slug, s in skills.items():
        if any(t in norm_all for t in s["triggers"]) or s["slash"].search(norm_all):
            trig_any.append(slug)
        if norm_human and (any(t in norm_human for t in s["triggers"])
                           or s["slash"].search(norm_human)):
            trig_human.append(slug)

    # `coverage_gap.conversations()` is LITERALLY: not under an excluded dir, not a sidecar,
    # turn_count >= 2. Reproduced as that predicate and nothing else — adding a condition of my
    # own here would recreate the divergence this file exists to prevent. Verified set-equal
    # against `coverage_gap.conversations()` in --self-test.
    in_cg = n_turns >= 2 and not any(x in rel.split("/") for x in CG_EXCLUDE_DIRS)

    # --- TURN POSITIONS. Scoped to the slugs the file-level pass already found, for two reasons:
    # it is ~30x cheaper than re-checking 33 skills against every turn, and — the one that
    # matters — it makes the positional field a REFINEMENT of the presence field rather than a
    # second opinion about it. `marker_turns` can never name a slug absent from `markers`.
    marker_turns, completion_turns, trigger_turns, trigger_turns_h = {}, {}, {}, {}
    for tn, role, ntxt in seg:
        if not ntxt:
            continue
        for slug in markers:
            spec = marker_reg[slug]
            if any(m in ntxt for m in spec["marker"]):
                marker_turns.setdefault(slug, []).append(tn)
            comp = spec.get("completion")
            if comp and any(c in ntxt for c in comp):
                completion_turns.setdefault(slug, []).append(tn)
        for slug in trig_any:
            s = skills[slug]
            if any(t in ntxt for t in s["triggers"]) or s["slash"].search(ntxt):
                trigger_turns.setdefault(slug, []).append(tn)
                if role == "H":
                    trigger_turns_h.setdefault(slug, []).append(tn)

    return {
        "id": fid, "id_source": id_src,
        "path": rel,
        "date": date, "date_source": date_src,
        "venue": venue, "trunk": trunk, "kind": kind, "parent_id": parent,
        "size": st.st_size, "mtime": int(st.st_mtime),
        "turn_count": n_turns, "human_turns": len(human_chunks), "lines": total_lines,
        "in_coverage_gap_scope": bool(in_cg),
        "markers": sorted(markers),
        "completions": sorted(completions),
        "triggers_any": sorted(trig_any),
        "triggers_human": sorted(trig_human),
        # --- schema v2: POSITIONS, not just presence. Turn 0 == preamble above T1.
        "marker_turns": {k: v for k, v in sorted(marker_turns.items())},
        "completion_turns": {k: v for k, v in sorted(completion_turns.items())},
        "trigger_turns": {k: v for k, v in sorted(trigger_turns.items())},
        "trigger_turns_human": {k: v for k, v in sorted(trigger_turns_h.items())},
        "compaction_turns": [t["t"] for t in turns if t["role"] == "C"],
        "role_counts": {r: sum(1 for t in turns if t["role"] == r)
                        for r in sorted({t["role"] for t in turns})},
    }


# =================================================================================================
# READING THE INDEX — THREE STATES, NEVER TWO
# =================================================================================================
# THE DEFECT THIS SECTION CLOSES (2026-08-06, found live by a consumer, not by a test)
# -------------------------------------------------------------------------------------------------
# `SCHEMA_VERSION` was bumped v1 -> v2 in one working copy while the on-disk index still declared
# v1. `load_prior` correctly discarded every row — and returned `{}`. A consumer went from 1,167
# rows to ZERO between two invocations with no corpus change and no error. **An edit to the SCRIPT
# silently invalidated the DATA.** A skill-usage query in that window answers "no usage of this
# skill anywhere in the corpus", which is indistinguishable from a true negative.
#
# The rebuild was never the bug. The bug is that `{}` meant two different things:
#     ABSENT       — there is no index; nothing is known                  -> UNKNOWN
#     STALE_SCHEMA — there are N rows on disk, written to another schema  -> UNKNOWN
# and a caller holding only `{}` cannot tell those apart, or apart from a genuine empty corpus.
#
# WHY A `status` FIELD IN THE HEADER CANNOT BE THE MECHANISM — the obvious fix, and it is wrong.
# The header is written by `write_out`, at which moment the schema is CURRENT by construction. A
# stored status would read "FRESH" forever; it goes stale the instant the constant moves, and it
# would be a recorded copy of something derivable — the repo's own "derive, don't record" failure.
# **Staleness is a RELATION between the file and the reading code. It has to be computed at read
# time, by the reader, every time.**
#
# THE MECHANISM CHOSEN: make the state a RETURN VALUE that a caller cannot accidentally drop.
# `read_index()` returns an `IndexRead` carrying the status, BOTH schema strings, and — the field
# that does the real work — `n_rows_on_disk`, the DENOMINATOR that separates STALE (1,172 rows
# present, unreadable) from ABSENT (0 rows, nothing there). `load_prior` keeps its exact old
# signature and its exact old discard-and-rebuild behaviour, so the build path is untouched; it is
# now a thin wrapper. Consumers call `read_index` / `require_index` and report UNKNOWN.
#
# A sentinel that makes naive reads *crash* was rejected: the index is a TRACKED artifact that
# other tools and humans read line-by-line, and corrupting it on purpose to force an error would
# break readers that are behaving correctly. Non-zero exit is offered, but only on the dedicated
# `--index-status` flag (see main), never on a normal run — see the note there.
# =================================================================================================
INDEX_FRESH = "FRESH"                    # header schema == SCHEMA_VERSION; rows are usable
INDEX_ABSENT = "ABSENT"                  # no file, or a file with no rows at all
INDEX_STALE = "STALE_SCHEMA"             # rows exist, written to a schema this code does not speak
INDEX_MALFORMED = "MALFORMED_HEADER"     # rows exist, header missing or unparseable -> schema UNKNOWN

_INDEX_EXIT = {INDEX_FRESH: 0, INDEX_STALE: 3, INDEX_ABSENT: 4, INDEX_MALFORMED: 5}


class IndexRead:
    """The result of reading the index. Carries the STATE, not just the rows.

    `.rows` is populated on FRESH **and** on STALE/MALFORMED — a consumer that wants to degrade
    into a labelled best-effort read (skill_record does) can, but it must do so knowingly, and it
    still has `.status` to print. What it can no longer do is receive `{}` and call that an answer.
    """

    __slots__ = ("status", "schema_on_disk", "schema_expected", "rows",
                 "n_rows_on_disk", "n_malformed", "path")

    def __init__(self, status, schema_on_disk, schema_expected, rows,
                 n_rows_on_disk, n_malformed, path):
        self.status = status
        self.schema_on_disk = schema_on_disk
        self.schema_expected = schema_expected
        self.rows = rows
        self.n_rows_on_disk = n_rows_on_disk
        self.n_malformed = n_malformed
        self.path = path

    @property
    def fresh(self):
        return self.status == INDEX_FRESH

    @property
    def exit_code(self):
        return _INDEX_EXIT[self.status]

    def one_line(self):
        return (f"{self.status} — on disk `{self.schema_on_disk}`, this code speaks "
                f"`{self.schema_expected}`; {self.n_rows_on_disk} rows physically present, "
                f"{len(self.rows)} parsed, {self.n_malformed} malformed")

    def banner(self, who="consumer"):
        """The loud block. Returns '' when FRESH so callers can print unconditionally."""
        if self.fresh:
            return ""
        if self.status == INDEX_ABSENT:
            why = ("There is no index to read. Nothing was scanned.")
        elif self.status == INDEX_STALE:
            why = (f"The index holds {self.n_rows_on_disk} rows written to schema "
                   f"`{self.schema_on_disk}`. This code speaks `{self.schema_expected}`. "
                   f"The ROWS ARE NOT GONE — the code and the data disagree about their shape.")
        else:
            why = (f"The index holds {self.n_rows_on_disk} rows but its header is missing or "
                   f"unparseable, so the schema they were written to is UNKNOWN.")
        return (
            "\n" + "!" * 78 + "\n"
            f"!! INDEX NOT USABLE — {self.status}\n"
            f"!! read by      : {who}\n"
            f"!! index        : {self.path}\n"
            f"!! schema on disk: {self.schema_on_disk}\n"
            f"!! schema expected: {self.schema_expected}\n"
            f"!! rows on disk : {self.n_rows_on_disk}   (parsed: {len(self.rows)})\n"
            f"!! {why}\n"
            "!! ANY COUNT DERIVED FROM THIS READ IS **UNKNOWN**, NOT ZERO. A zero here would be\n"
            "!! indistinguishable from a true negative. Do not report it as one.\n"
            "!! FIX: python scripts/audit/corpus_index.py        (rebuilds at the current schema)\n"
            + "!" * 78 + "\n")


def read_index(p=None):
    """-> IndexRead. The one place the on-disk schema is compared to this code's schema.

    Every consumer routes through here. It replaced three separate hand-rolled header parsers
    (corpus_index.load_prior, skill_record.load_rows, role_history.load_corpus_rows), which is the
    same duplication class the index itself exists to close: a fact written down more than once,
    then diverging with nothing able to notice.
    """
    p = OUT_JSONL if p is None else p
    if not p.is_file():
        return IndexRead(INDEX_ABSENT, None, SCHEMA_VERSION, {}, 0, 0, p)
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    has_header = bool(lines) and lines[0].startswith("#")
    body = lines[1:] if has_header else lines

    rows, bad = {}, 0
    n_on_disk = 0
    for ln in body:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        n_on_disk += 1
        try:
            r = json.loads(ln)
            rows[r["path"]] = r
        except Exception:
            bad += 1

    if not has_header:
        status = INDEX_ABSENT if n_on_disk == 0 else INDEX_MALFORMED
        return IndexRead(status, None, SCHEMA_VERSION, rows, n_on_disk, bad, p)
    try:
        declared = json.loads(lines[0][1:]).get("schema")
    except Exception:
        declared = None
    if declared is None:
        status = INDEX_ABSENT if n_on_disk == 0 else INDEX_MALFORMED
    elif declared != SCHEMA_VERSION:
        status = INDEX_STALE
    elif n_on_disk == 0:
        status = INDEX_ABSENT
    else:
        status = INDEX_FRESH
    return IndexRead(status, declared, SCHEMA_VERSION, rows, n_on_disk, bad, p)


def require_index(who="consumer", p=None, stream=None):
    """-> IndexRead, having PRINTED the banner to stderr when the read is not usable.

    The guard a consumer calls instead of `if not rows`. `if not rows` is precisely the test that
    cannot tell ABSENT from STALE, and it is what printed "no corpus index on disk" while 1,172
    rows sat on disk.
    """
    r = read_index(p)
    if not r.fresh:
        print(r.banner(who), file=stream or sys.stderr)
    return r


# =================================================================================================
# INCREMENTAL — keyed on (path, size, mtime), the agent_end_ingest pattern
# =================================================================================================
def load_prior(p=None):
    """{path: row}, EMPTY unless the schema matches. Behaviour deliberately UNCHANGED.

    The schema version lives on ONE header line, not on every row — 1,164 copies of the same
    string was 4.4% of the file. A header whose version does not match discards the whole file
    and forces a rescan; mixing schemas silently is how an index starts lying about its own
    fields. A missing header is also a discard: an index written before versioning is unknown,
    and unknown is not "fine".

    This is the BUILD path's reader and its discard-then-rebuild is correct — keep it. It is kept
    as-was on purpose so `build()` is untouched by this change. **It is the wrong reader for a
    QUERY**, because its `{}` cannot be told from an empty corpus: use `read_index`/`require_index`.
    """
    r = read_index(p)
    if not r.fresh:
        return {}, (r.n_rows_on_disk + r.n_malformed) if r.n_rows_on_disk else r.n_malformed
    return r.rows, r.n_malformed


def build(full=False, dry_run=False, repo=REPO):
    t0 = time.time()
    skills = load_skills(repo)
    files = walk_corpus(repo)
    prior, bad_prior = ({}, 0) if full else load_prior()

    rows, n_skip, n_scan, n_unreadable = [], 0, 0, 0
    for path, rel in files:
        try:
            st = path.stat()
        except OSError:
            n_unreadable += 1
            continue
        p = prior.get(rel)
        if p and p.get("size") == st.st_size and p.get("mtime") == int(st.st_mtime):
            rows.append(p)
            n_skip += 1
            continue
        r = scan_file(path, rel, skills)
        if r is None:
            n_unreadable += 1
            continue
        rows.append(r)
        n_scan += 1

    dropped = [k for k in prior if k not in {r["path"] for r in rows}]
    rows.sort(key=lambda r: r["path"])
    elapsed = time.time() - t0
    stats = {
        "seen": len(files), "indexed": len(rows), "skipped_unchanged": n_skip,
        "rescanned": n_scan, "unreadable": n_unreadable,
        "prior_rows": len(prior), "prior_malformed_or_stale_schema": bad_prior,
        "gone_since_last_run": len(dropped), "seconds": round(elapsed, 1),
        "skills_seen": len(skills),
        "skills_with_declared_marker": len(MARKERS),
        "skills_without_declared_marker": sorted(set(skills) - set(MARKERS)),
        "mode": "full" if full else "incremental",
    }
    if not dry_run:
        write_out(rows, stats, skills)
    return rows, stats, skills


def write_out(rows, stats, skills):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSONL, "w", encoding="utf-8", newline="\n") as f:
        f.write("#" + json.dumps({
            "schema": SCHEMA_VERSION,
            "generated_by": "scripts/audit/corpus_index.py",
            "source_of_truth": CORPUS,
            "generated": time.strftime("%Y-%m-%d"),
            "rows": len(rows),
            "note": "GENERATED — do not hand-edit. ids/paths/counts/marker-presence only; "
                    "no transcript content.",
            # The instruction travels with the thing it governs. A reader that finds this line
            # and ignores it has made a choice; one that never saw it had a defect handed to it.
            "reader_contract": "Compare this `schema` to corpus_index.SCHEMA_VERSION BEFORE "
                               "counting. A mismatch means the rows below are UNKNOWN to you, "
                               "never zero — `rows` above is the denominator that proves they "
                               "exist. Use corpus_index.read_index()/require_index(); "
                               "`if not rows` cannot tell STALE from ABSENT.",
        }, sort_keys=True, separators=(",", ":")) + "\n")
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
    OUT_MD.write_text(digest(rows, stats, skills), encoding="utf-8", newline="\n")


# =================================================================================================
# THE THREE-CLASS QUERY — the shape skill_usage.py needs. Reference implementation.
# =================================================================================================
def three_class(rows, slug, skills):
    """{'USED','PARTIAL','APPLICABLE_NOT_USED','marker_state','completion_state'} for one skill.

    USED                 marker literal present anywhere in the transcript.
    PARTIAL              marker present, declared completion shape ABSENT — a run that started
                         and did not finish. UNDETECTABLE when the skill declares no completion
                         literal; that is reported as its own state, never as "no partials."
    APPLICABLE-NOT-USED  a declared trigger appears in JON'S OWN turns and no marker is present.
                         Jon's turns, not the whole file, because the assistant discussing a skill
                         is not an occasion on which the skill should have fired.
    """
    spec = MARKERS.get(slug)
    trig = slug in skills
    used = [r["path"] for r in rows if slug in r["markers"]]
    if spec is None:
        marker_state = "UNDECLARED — no structural marker known; USED is undetectable, not zero"
        used = []
    else:
        marker_state = "declared: " + " | ".join(spec["marker"]) + f"   ({spec['src']})"
    if spec and spec.get("completion"):
        comp_state = "declared: " + " | ".join(spec["completion"])
        partial = [r["path"] for r in rows if slug in r["markers"] and slug not in r["completions"]]
    else:
        comp_state = "UNDECLARED — PARTIAL is undetectable for this skill"
        partial = None
    anu = ([r["path"] for r in rows if slug in r["triggers_human"] and slug not in r["markers"]]
           if trig else None)
    return {"skill": slug, "USED": used, "PARTIAL": partial, "APPLICABLE_NOT_USED": anu,
            "marker_state": marker_state, "completion_state": comp_state,
            "trigger_state": ("declared: " + " | ".join(skills[slug]["triggers"] + ["/" + slug]))
            if trig else "UNKNOWN — no SKILL.md found"}


# =================================================================================================
# OUTPUT — denominators printed, not documented
# =================================================================================================
def counter(rows, key):
    out = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def print_report(rows, stats, skills):
    print()
    print("=" * 80)
    print("CORPUS INDEX — raw/transcripts")
    print("=" * 80)
    print("--- DENOMINATORS (in the output, not the docstring) --------------------------")
    print(f"  mode                          : {stats['mode']}")
    print(f"  files SEEN under {CORPUS:<13}: {stats['seen']}   (.md, sidecars excluded)")
    print(f"  files INDEXED                 : {stats['indexed']}")
    print(f"  SKIPPED unchanged (size+mtime): {stats['skipped_unchanged']}")
    print(f"  RESCANNED                     : {stats['rescanned']}")
    print(f"  UNREADABLE                    : {stats['unreadable']}")
    print(f"  prior index rows              : {stats['prior_rows']}  "
          f"(malformed / stale schema: {stats['prior_malformed_or_stale_schema']})")
    print(f"  in prior index, gone from disk: {stats['gone_since_last_run']}")
    print(f"  elapsed                       : {stats['seconds']}s")
    print()
    print("--- PARTITIONS ---------------------------------------------------------------")
    for k in ("venue", "kind", "trunk"):
        print(f"  by {k:<6}: {json.dumps(counter(rows, k))}")
    n_cg = sum(1 for r in rows if r["in_coverage_gap_scope"])
    print(f"  in coverage_gap.py scope      : {n_cg} of {len(rows)}  "
          f"(the rest are subagents / <2 turns / routing — WIDER ON PURPOSE)")
    unknown_id = sum(1 for r in rows if r["id"] == "UNKNOWN")
    unknown_dt = sum(1 for r in rows if r["date"] == "UNKNOWN")
    print(f"  rows with UNKNOWN id / date   : {unknown_id} / {unknown_dt}  "
          f"(named, never fabricated)")
    print()
    print("--- MARKER REGISTRY COVERAGE -------------------------------------------------")
    print(f"  skills found in skills/       : {stats['skills_seen']}")
    print(f"  with a DECLARED marker        : {stats['skills_with_declared_marker']}  "
          f"<- the only skills for which USED is detectable at all")
    print(f"  WITHOUT one                   : {len(stats['skills_without_declared_marker'])}  "
          f"-> these report UNDECLARED, never zero")
    print(f"     {', '.join(stats['skills_without_declared_marker'])}")
    print()
    print("--- MARKER PRESENCE ----------------------------------------------------------")
    for slug in sorted(MARKERS):
        u = sum(1 for r in rows if slug in r["markers"])
        c = sum(1 for r in rows if slug in r["completions"])
        t = sum(1 for r in rows if slug in r["triggers_human"])
        comp = "n/a" if not MARKERS[slug].get("completion") else str(c)
        print(f"  {slug:<24} marker {u:>5}   completion {comp:>5}   "
              f"trigger-in-Jon's-turns {t:>5}")
    print()
    print("--- WHAT WOULD MAKE THIS INDEX LIE -------------------------------------------")
    print("  1. PRESENCE IS NOT USE. A marker inside a quoted example, a code fence, or a skill")
    print("     file pasted into a chat counts as present. The index reports where the string is,")
    print("     not that the protocol ran.")
    print("  2. THE REGISTRY IS THE CEILING. Only "
          f"{stats['skills_with_declared_marker']} of {stats['skills_seen']} skills have a")
    print("     declared marker. Every headline count is a count over that subset and nothing")
    print("     more. Do not read a low number for an UNDECLARED skill as low usage.")
    print("  3. INCREMENTAL TRUSTS mtime. A transcript rewritten in place with identical size and")
    print("     mtime is skipped. --full is the escape hatch and it is not run by default.")
    print("  4. TRIGGERS ARE GENERATED FROM DESCRIPTIONS. A skill whose description quotes no")
    print("     phrase gets only `/slug` and its spaced name; APPLICABLE-NOT-USED under-reports")
    print("     for it. Short phrases (<8 chars) are dropped to keep the class from being noise.")
    print("  5. SUBAGENT TRUNK IS UNKNOWN BY CONSTRUCTION. It lives on the parent, not the path.")
    print("     It is written UNKNOWN rather than inherited by guess.")
    print("  6. **APPLICABLE-NOT-USED IS A CANDIDATE LIST, NOT A VERDICT — MEASURED, NOT ASSUMED.**")
    print("     Four of four FBC candidates opened by hand on 2026-08-06 were Jon DISCUSSING the")
    print("     protocol ('it links well into frame before commit'), not asking for it. A mention")
    print("     and a request are the same string. Separating them needs a judgment this index")
    print("     does not make. Treat the class as 'worth reading', never as 'a skill was missed'.")
    print("     (A fifth candidate was a genuine false positive of a different kind — `/slug`")
    print("      matching inside the path `skills/<slug>/SKILL.md`. That one is FIXED: the slash")
    print("      form is now boundary-anchored. It was found by opening the output, not the code.)")
    print()
    sz = OUT_JSONL.stat().st_size if OUT_JSONL.is_file() else 0
    print(f"  index : {OUT_JSONL.relative_to(REPO)}   {sz:,} bytes  "
          f"(TRACKED — rewritten whole each run; rows are path-sorted so diffs stay line-local)")
    print(f"  digest: {OUT_MD.relative_to(REPO)}")
    print()


def digest(rows, stats, skills):
    L = []
    w = L.append
    w("---")
    w("title: Corpus Index")
    w(f"schema_version: {SCHEMA_VERSION}")
    w("maintained_by: scripts/audit/corpus_index.py — GENERATED, never hand-edited")
    w("source_of_truth: raw/transcripts/ (gitignored corpus)")
    w(f"last_generated: {time.strftime('%Y-%m-%d')}")
    w("---")
    w("")
    w("# Corpus Index")
    w("")
    w("**Generated. Do not edit by hand.** Regenerate with "
      "`python scripts/audit/corpus_index.py`; the machine-readable rows are in "
      "`corpus-index.jsonl` beside this file. A hand edit here is a divergence with nothing "
      "able to notice it — the failure class this file exists to close.")
    w("")
    w("**Why it exists.** Jon, 2026-08-06: *\"I don't know how to trace things to their original "
      "sources. If I search, I am using file names and we don't name things the same way in our "
      "heads so that's not durrible.\"* PRIMARY (resurrected 2026-08-07): "
      "`raw/transcripts/claude-code/code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-updates.md:32381`, "
      "`## Human` turn. This index is searchable by what a session **did** "
      "(markers, triggers) rather than by what it was named.")
    w("")
    w("**Content never lands here.** Ids, paths, dates, sizes, counts and marker/trigger "
      "presence only.")
    w("")
    w("## Denominators")
    w("")
    w("These describe the CORPUS, not the run. Per-run counters — mode, skipped-unchanged, "
      "rescanned, elapsed — are printed to the console and deliberately **not** persisted here: "
      "a digest that recorded them would change on every invocation without the corpus changing, "
      "and a tracked file that churns for no reason trains readers to ignore its diffs.")
    w("")
    w("| quantity | value |")
    w("|---|---|")
    for k in ("seen", "indexed", "unreadable"):
        w(f"| {k} | {stats[k]} |")
    n_cg = sum(1 for r in rows if r["in_coverage_gap_scope"])
    w(f"| in `coverage_gap.py` scope | {n_cg} of {len(rows)} |")
    w("")
    w("`coverage_gap.py`'s corpus is a **derivable subset** of this index "
      "(`in_coverage_gap_scope`), not a second opinion about it. This index is wider on purpose: "
      "it keeps `subagents/` and sub-2-turn files, because skills fire inside subagent runs.")
    w("")
    w("## Partitions")
    w("")
    for k in ("venue", "kind", "trunk"):
        w(f"- **by {k}** — " + ", ".join(f"`{a}` {b}" for a, b in counter(rows, k).items()))
    w("")
    w("## Marker registry coverage")
    w("")
    w(f"Markers are **declared**, not generated — a structural output signature is a fact about a "
      f"skill's output template and most CFL skills do not declare one. "
      f"**{stats['skills_with_declared_marker']} of {stats['skills_seen']}** skills have a "
      f"declared marker. The rest report `UNDECLARED`, **never zero** — undetectable use and no "
      f"use are different findings.")
    w("")
    w("| skill | marker files | completion files | trigger in Jon's turns | completion declared |")
    w("|---|---|---|---|---|")
    for slug in sorted(MARKERS):
        u = sum(1 for r in rows if slug in r["markers"])
        c = sum(1 for r in rows if slug in r["completions"])
        t = sum(1 for r in rows if slug in r["triggers_human"])
        has_c = "yes" if MARKERS[slug].get("completion") else "no — PARTIAL undetectable"
        w(f"| `{slug}` | {u} | {c if MARKERS[slug].get('completion') else '—'} | {t} | {has_c} |")
    w("")
    w("**Skills with no declared marker:** "
      + ", ".join(f"`{s}`" for s in stats["skills_without_declared_marker"]))
    w("")
    w("## What would make this index lie")
    w("")
    w("1. **Presence is not use.** A marker inside a quoted example or a pasted skill file counts "
      "as present. The index reports where a string is, not that a protocol ran.")
    w("2. **The registry is the ceiling.** Every headline count is over the declared subset.")
    w("3. **Incremental trusts mtime.** An in-place rewrite at identical size and mtime is "
      "skipped; `--full` is the escape hatch and does not run by default.")
    w("4. **Triggers are generated from `description` frontmatter.** A skill quoting no phrase "
      "gets only `/slug` and its spaced name, so APPLICABLE-NOT-USED under-reports for it.")
    w("5. **Subagent trunk is `UNKNOWN` by construction** — it lives on the parent, not the path.")
    w("6. **`APPLICABLE-NOT-USED` is a candidate list, not a verdict.** Four of four "
      "frame-before-commit candidates opened by hand on 2026-08-06 were Jon *discussing* the "
      "protocol, not asking for it. A mention and a request are the same string; separating them "
      "is a judgment this index does not make.")
    w("")
    return "\n".join(L) + "\n"


# =================================================================================================
# TURN-SCOPED DETECTION — because DETECTION IS FILE-SCOPED AND FAILURE IS TURN-SCOPED
# =================================================================================================
# THE DEFECT THIS CLOSES, in the words of the record that found it
# (`wiki/references/skills/ground-before-stating.md` §1):
#
#   "a session that invoked GBS once at 09:00 and committed five grounding failures four hours
#    later is 'USED' by any file-scoped detector."
#
# That page published USED 64 / PARTIAL 171 / APPLICABLE-NOT-USED 266 over 1,167 transcripts and
# then undermined its own numbers, correctly. `code-2026-08-06-f01909` — the one session in the
# corpus with five independently-verified Rule 6 failures, enumerated by Jon by hand — scores
# `invoked: True, labeled: True`. It never enters the not-used class. **266 is a floor.**
#
# THE UNIT
# ---------
# `(transcript, turn)`. Every scored thing is an OCCASION: one turn at which the skill was
# applicable. A skill invoked at turn 12 does not make turn 340 count as USED.
#
# THE WINDOW — the design decision, stated and justified rather than assumed
# ---------------------------------------------------------------------------
# An anchor (an invocation, or an emitted marker, which is evidence the skill is operating) puts
# the skill IN FORCE for a bounded span of turns. Two components, and they are of different kinds:
#
#  1. **Hard reset at a compaction boundary (`turn_index` role `C`). NOT TUNABLE.** This is the
#     literal mechanism by which earlier turns leave the model's context — after it, everything
#     prior survives only as a summary. A window that spanned a compaction boundary would be
#     asserting that an invocation the session can no longer see is still governing it. In
#     `f01909` the boundary is at turn 634 and it does real work: it severs turn 692 from the
#     only prior invocation (turn 10).
#
#  2. **A decay span `W` in turns, MEASURED, not picked.** `--calibrate-window` computes the
#     distribution of (invocation turn -> next emitted label turn) over the whole corpus and
#     prints it. The default below is that distribution's p90: the span within which 90% of
#     invocations that ever demonstrably produced a label produced one. Beyond it, invocations
#     stop showing effect, which is the operational content of "no longer in force."
#     **The calibration is circular by construction and that is disclosed:** it is measured from
#     the same corpus it then classifies, so it is a CALIBRATION, not a validation. What it is
#     not is a number somebody liked. `--window N` overrides it, and `--sensitivity` prints the
#     whole curve, so no reader has to take the default on faith.
#
# DIRECTION, which differs by case and must not be conflated
# ------------------------------------------------------------
#  * Jon triggers at turn n -> **FORWARD** window: did a marker appear in `[n, n+W]`? This is
#    response latency.
#  * The assistant asserts at turn n -> **BACKWARD** window: was an anchor in force at `n`?
#    This is the in-force span, which is what W was calibrated on.
#  Using the (larger) in-force W for the forward case is deliberately CONSERVATIVE: a longer
#  window makes APPLICABLE-NOT-USED *smaller*, i.e. it errs toward the published file-scoped
#  numbers rather than away from them. The error direction is stated because it is the one that
#  could make this instrument flatter itself.
#
# WHAT TURN-SCOPING STILL CANNOT SEE — reported as UNKNOWN, never as zero
# ------------------------------------------------------------------------
#  * A failure with **no textual precursor**. Four of Jon's five are assertions about the state
#    of a file, branch or config made without reading it — a fact about WHAT WAS READ, which is
#    not in the prose at all. Turn-scoping fixes the *unit*; it does not give the text a
#    sense it never had.
#  * A failure inside a turn the extractor never wrote (an open session's tail, a dropped
#    record class).
#  * Sub-turn granularity. A turn containing both a grounded claim and an ungrounded one scores
#    once. The unit is finer than the file and still coarser than the claim.

# Anchors that are invocations rather than emitted markers. GBS's own invocation surface includes
# `/gbs`, which is 4 characters and therefore below the index's MIN_TRIGGER_LEN — the generated
# trigger list cannot carry it. Declared here for the skills whose short form is load-bearing.
SHORT_INVOKE = {
    "ground-before-stating": re.compile(r"(?:^|\s)/gbs\b|gbs check|show your epistemic work",
                                        re.I),
    "frame-before-commit": re.compile(r"(?:^|\s)/fbc\b", re.I),
}

WINDOW_DEFAULT = 40          # replaced below by the measured p90; see set_default_window()
WINDOW_SOURCE = "unmeasured fallback"


def _no_compaction_between(a, b, comp):
    """True when no compaction boundary lies strictly between turns a and b (order-agnostic)."""
    lo, hi = (a, b) if a <= b else (b, a)
    return not any(lo < c <= hi for c in comp)


def anchors_for(row, slug):
    """Turn numbers at which `slug` was demonstrably operating: invocations OR emitted markers.

    An emitted marker RE-ANCHORS. That is a real modelling choice, not an oversight: a label at
    turn 300 is evidence the skill is running at turn 300 regardless of when it was invoked, and
    refusing to count it would make a long, continuously-grounded session look like a lapsed one.
    """
    a = set(row.get("marker_turns", {}).get(slug, []))
    a |= set(row.get("trigger_turns", {}).get(slug, []))
    return sorted(a)


def in_force(turn, anchors, comp, window):
    """Was the skill in force at `turn`? Backward window + hard compaction reset."""
    return any(0 <= turn - a <= window and _no_compaction_between(a, turn, comp) for a in anchors)


def answered_forward(turn, marker_turns, comp, window):
    """Did a marker land in [turn, turn+window] with no compaction boundary intervening?"""
    return any(0 <= m - turn <= window and _no_compaction_between(turn, m, comp)
               for m in marker_turns)


# =================================================================================================
# CALIBRATION — the window is measured from the corpus and the measurement is printed
# =================================================================================================
def calibrate(rows, slug):
    """Distances from an invocation turn to the NEXT emitted marker turn, corpus-wide.

    Only pairs with no compaction boundary between them are measured — across a boundary the
    distance is not a decay observation, it is two different contexts.
    """
    d = []
    for r in rows:
        inv = r.get("trigger_turns", {}).get(slug, [])
        mk = sorted(r.get("marker_turns", {}).get(slug, []))
        comp = r.get("compaction_turns", [])
        for i in inv:
            nxt = [m for m in mk if m >= i and _no_compaction_between(i, m, comp)]
            if nxt:
                d.append(nxt[0] - i)
    return sorted(d)


def pct(sorted_vals, p):
    if not sorted_vals:
        return None
    k = max(0, min(len(sorted_vals) - 1, int(round((p / 100.0) * (len(sorted_vals) - 1)))))
    return sorted_vals[k]


def set_default_window(rows, slug="ground-before-stating"):
    """Set WINDOW_DEFAULT from the measured p90. Falls back, loudly, when there is no sample."""
    global WINDOW_DEFAULT, WINDOW_SOURCE
    d = calibrate(rows, slug)
    if len(d) >= 20:
        WINDOW_DEFAULT = max(1, pct(d, 90))
        WINDOW_SOURCE = (f"measured: p90 of {len(d)} invocation->label distances for `{slug}` "
                         f"(median {pct(d, 50)}, p75 {pct(d, 75)}, max {d[-1]})")
    else:
        WINDOW_SOURCE = (f"UNMEASURED — only {len(d)} invocation->label pairs for `{slug}`, "
                         f"below the sample floor of 20. Using the fallback {WINDOW_DEFAULT}. "
                         f"This is a stated ignorance, not a calibration.")
    return WINDOW_DEFAULT


# =================================================================================================
# THE TURN-SCOPED THREE-CLASS QUERY — same three names, finer unit, both reported side by side
# =================================================================================================
def turn_three_class(rows, slug, skills, window):
    """Occasion-level classes for one skill. An OCCASION is one Jon-trigger turn.

    TURN-USED             a marker landed within `window` turns after the trigger, same context.
    TURN-PARTIAL          a marker landed, the declared completion shape did not.
    TURN-APPLICABLE-      Jon triggered and nothing fired inside the window. **This is the class
      NOT-USED            the file-scoped detector structurally cannot see**: file-scoped, one
                          marker anywhere in a 1,838-turn session answers every trigger in it.
    """
    spec = MARKERS.get(slug)
    occ_used, occ_partial, occ_anu = [], [], []
    files_with_occ = set()
    n_turns = n_occ = 0
    for r in rows:
        n_turns += r.get("turn_count", 0)
        occ = r.get("trigger_turns_human", {}).get(slug, [])
        if not occ:
            continue
        files_with_occ.add(r["path"])
        mk = r.get("marker_turns", {}).get(slug, [])
        cp = r.get("completion_turns", {}).get(slug, [])
        comp = r.get("compaction_turns", [])
        for t in occ:
            n_occ += 1
            key = (r["path"], t)
            if spec is None:
                occ_anu.append(key)          # marker UNDECLARED -> never answerable; see below
            elif answered_forward(t, mk, comp, window):
                if spec.get("completion") and not answered_forward(t, cp, comp, window):
                    occ_partial.append(key)
                else:
                    occ_used.append(key)
            else:
                occ_anu.append(key)
    return {
        "skill": slug, "window": window,
        "turns_total": n_turns, "occasions": n_occ,
        "files_with_occasions": len(files_with_occ),
        "TURN_USED": occ_used,
        "TURN_PARTIAL": occ_partial if (spec and spec.get("completion")) else None,
        "TURN_APPLICABLE_NOT_USED": occ_anu,
        "marker_declared": spec is not None,
    }


# =================================================================================================
# GBS DEEP MODE — occasions are the ASSISTANT's precursors, which is where Rule 6 actually lives
# =================================================================================================
# The generic occasion above is "Jon asked." That is the right occasion for a skill Jon invokes,
# and it is the WRONG occasion for Rule 6, whose precursor occurs in the assistant's turns. The
# GBS record page named this exactly: a detector reading only Jon's turns is structurally blind
# to the rule SKILL.md:59 calls "the highest-frequency grounding failure."
#
# The declared Rule 2/6/7/8 precursors are **imported from `gbs_record.py`, never re-declared** —
# a lazy import, because `gbs_record` imports THIS module at load time. Each pattern is declared
# in exactly one file. If `gbs_record` is unavailable the deep mode reports UNAVAILABLE and
# exits 0; it never falls back to a private copy, because a private copy is the divergence.
#
# TWO FAMILIES ARE DECLARED HERE, because `gbs_record` has neither and neither is a fork of one:
#
#  P1 — ABSENCE / IMPOSSIBILITY ASSERTION. Derived from Rule 6's own text
#       (`skills/ground-before-stating/SKILL.md:59`): *"When ground exists but is unread, read it
#       before asserting."* An assertion that a thing does NOT exist, is not tracked, or cannot
#       be done is the purest instance of the rule — **you cannot know a thing is absent without
#       looking.** The derivation is from the rule, not from the incidents; the corroboration
#       that it is a real shape and not a fitted one is that the GBS record agent found a SIXTH
#       instance of it independently (`f01909` turn 1218, *"An agent already declared this file
#       nonexistent"*) before this pattern existed.
#
#  P2 — RETROSPECTIVE SELF-CORRECTION. **Not a precursor — an OUTCOME marker**, and the
#       distinction is load-bearing. P1 says "a claim of this shape was made"; P2 says "a claim
#       was later admitted to be wrong." P2 is the corpus's own answer key, and it is the only
#       high-precision signal available for this failure class. It anchors BACKWARD: a correction
#       at turn n implicates an assertion at some turn < n. Rule 6's own ratification note is
#       itself a retro-detection of exactly this kind ("Jon's recollection was right and the
#       summary wrong on three occasions").
P1_ABSENCE = re.compile(
    r"\b(?:not in the wiki|not in git|isn'?t tracked|is not tracked|untracked|gitignored|"
    r"does(?:n'?t| not) exist|non-?existent|no such (?:file|page|entry|record|branch|ticket)|"
    r"there (?:is|are) no |never (?:existed|written|created|committed)|"
    r"no (?:supporting|annotation|entry|record|trace|evidence) (?:in|for|of|anywhere)|"
    r"nothing (?:in|under|at) `|missing (?:from|entirely)|absent from|"
    r"cannot be (?:edited|written|set|changed)|can'?t be (?:edited|written|set|changed)|"
    r"was refused by|is unwritable|not possible to)\b",
    re.I,
)
P2_SELFCORRECT = re.compile(
    r"\bI (?:said|called|claimed|asserted|told you) (?:it|that|this|them) (?:was|were|is|are)\b|"
    r"\bI was wrong\b|\bmy (?:own )?(?:wrong|incorrect|false) (?:diagnosis|claim|read|call)\b|"
    r"\b(?:both )?claims? wrong\b|\bthat was wrong\b|\bcorrecting myself\b|"
    r"\bI (?:had )?(?:asserted|declared) (?:absence|it|this) without checking\b|"
    r"\bwithout (?:having )?(?:checked|read) (?:it|first)\b|\bI'?d framed that as\b|"
    r"\bturns out (?:it|that|there)\b|\bI under-?applied\b|\bfalse absence",
    re.I,
)


def _gbs_module():
    """Lazy import — `gbs_record` imports this module at load time, so the edge must be deferred.

    Returns None rather than raising: the deep mode is an instrument, and an instrument that
    cannot run says so and exits 0.
    """
    try:
        import gbs_record as G
        return G
    except Exception:
        return None


def gbs_turn_scan(path, window, comp=None):
    """Per-turn GBS record for ONE transcript. Reads the file; returns positions, never content."""
    G = _gbs_module()
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    ti = turn_index(str(p))
    turns = ti["turns"]
    comp = [t["t"] for t in turns if t["role"] == "C"] if comp is None else comp
    seq = []
    for i, t in enumerate(turns):
        s = t["line"]
        e = turns[i + 1]["line"] - 1 if i + 1 < len(turns) else len(lines)
        seq.append((t["t"], t["role"], "\n".join(lines[s:e])))

    invoke = G.INVOKE if G else SHORT_INVOKE["ground-before-stating"]
    labels = G.LABELS if G else re.compile(r"\[unverified\]|\[training\]|\[vtt assumed", re.I)
    r6 = G.R6_RISK if G else None
    exempt = G.R6_EXEMPT if G else None

    anchors = [t for t, _r, tx in seq if invoke.search(tx) or labels.search(tx)]
    out = []
    for t, role, tx in seq:
        rec = {"turn": t, "role": role,
               "label": bool(labels.search(tx)),
               "invoke": bool(invoke.search(tx)),
               "r6": bool(r6.search(tx)) if r6 else None,
               "p1": bool(P1_ABSENCE.search(tx)),
               "p2": bool(P2_SELFCORRECT.search(tx)),
               "exempt": bool(exempt.search(tx)) if exempt else False,
               "in_force": in_force(t, anchors, comp, window)}
        if rec["r6"] or rec["p1"] or rec["p2"]:
            out.append(rec)
    return {"path": str(p), "turns": ti["turn_count"], "compaction": comp,
            "anchors": anchors, "gbs_record_available": G is not None, "records": out}


# =================================================================================================
# TURN-SCOPED REPORTS — file-scoped and turn-scoped side by side, with denominators, always
# =================================================================================================
def _sensitivity(rows, slug, skills):
    print("--- SENSITIVITY TO THE WINDOW (the answer's dependence on the one free choice) ---")
    print(f"  {'window':>8} | {'TURN-USED':>10} | {'TURN-PARTIAL':>12} | {'TURN-ANU':>9} | "
          f"{'ANU files':>9}")
    for w in (1, 5, 10, 25, 50, 100, 250, 10 ** 9):
        q = turn_three_class(rows, slug, skills, w)
        anu_f = len({p for p, _ in q["TURN_APPLICABLE_NOT_USED"]})
        lbl = "inf" if w > 10 ** 8 else str(w)
        par = "n/a" if q["TURN_PARTIAL"] is None else str(len(q["TURN_PARTIAL"]))
        print(f"  {lbl:>8} | {len(q['TURN_USED']):>10} | {par:>12} | "
              f"{len(q['TURN_APPLICABLE_NOT_USED']):>9} | {anu_f:>9}")
    print("  window=inf is NOT the file-scoped number — it is file-scoped WITHIN a compaction")
    print("  segment. The residual gap between the two is the compaction reset doing its work.")
    print()


def _report_side_by_side(rows, slug, skills, window, bad, limit):
    fq = three_class(rows, slug, skills)
    tq = turn_three_class(rows, slug, skills, window)
    n_files = len(rows)
    print()
    print("=" * 88)
    print(f"THREE-CLASS QUERY — {slug}   FILE-SCOPED vs TURN-SCOPED")
    print("=" * 88)
    print(f"  index rows read            : {n_files}  (malformed/stale: {bad})")
    print(f"  window                     : {window} turns   [{WINDOW_SOURCE}]")
    print(f"  marker                     : {fq['marker_state'][:110]}")
    print()
    print("--- DENOMINATORS — TURNS, NOT ONLY FILES -------------------------------------")
    print(f"  transcripts in index       : {n_files}")
    print(f"  TURNS in index             : {tq['turns_total']:,}   <- the turn-scoped denominator")
    print(f"  occasions scored           : {tq['occasions']}  "
          f"(a Jon-trigger turn; in {tq['files_with_occasions']} files)")
    print()
    print("--- THE TWO MEASURES ---------------------------------------------------------")
    fp = "UNDETECTABLE" if fq["PARTIAL"] is None else str(len(fq["PARTIAL"]))
    tp = "UNDETECTABLE" if tq["TURN_PARTIAL"] is None else str(len(tq["TURN_PARTIAL"]))
    fa = "UNDETECTABLE" if fq["APPLICABLE_NOT_USED"] is None else str(len(fq["APPLICABLE_NOT_USED"]))
    anu_files = len({p for p, _ in tq["TURN_APPLICABLE_NOT_USED"]})
    print(f"  {'class':<22} {'FILE-SCOPED (files)':>22} {'TURN-SCOPED (occasions)':>26}")
    print(f"  {'USED':<22} {len(fq['USED']):>22} {len(tq['TURN_USED']):>26}")
    print(f"  {'PARTIAL':<22} {fp:>22} {tp:>26}")
    print(f"  {'APPLICABLE-NOT-USED':<22} {fa:>22} "
          f"{str(len(tq['TURN_APPLICABLE_NOT_USED'])) + f' ({anu_files} files)':>26}")
    print()
    print("  **THE TURN-SCOPED NUMBER IS THE TRUER ONE.** The file-scoped column is what is")
    print("  currently published; it is kept here rather than replaced so the two can be")
    print("  compared. A rise in APPLICABLE-NOT-USED is the instrument getting better, not worse:")
    print("  file-scoped, one marker anywhere in a 1,838-turn session answers every trigger in it.")
    print()
    for cls in ("TURN_USED", "TURN_PARTIAL", "TURN_APPLICABLE_NOT_USED"):
        v = tq[cls]
        if v is None:
            print(f"  {cls:<26} UNDETECTABLE for this skill — reported as such, not as 0")
            continue
        print(f"  {cls:<26} {len(v)}")
        for p, t in v[:limit]:
            print(f"      T{t:<6} {p}")
        if len(v) > limit:
            print(f"      ... {len(v) - limit} more")
    print()
    _sensitivity(rows, slug, skills)
    print("--- WHAT TURN-SCOPING STILL CANNOT SEE (UNKNOWN, never zero) -----------------")
    print("  1. A FAILURE WITH NO TEXTUAL PRECURSOR. The dominant Rule 6 shape is an assertion")
    print("     about a file/branch/config made without reading it. That is a fact about WHAT WAS")
    print("     READ. Turn-scoping fixes the unit; it does not give prose a sense it never had.")
    print("  2. TURNS THE EXTRACTOR NEVER WROTE — an open session's tail, a dropped record class.")
    print("  3. SUB-TURN GRANULARITY. A turn holding one grounded and one ungrounded claim scores")
    print("     once. Finer than the file, still coarser than the claim.")
    print("  4. OCCASIONS THAT ARE NOT LEXICAL AT ALL. The generic occasion here is a Jon trigger;")
    print("     a skill that should have fired with nothing said about it is invisible to both")
    print("     measures. That count is UNKNOWN.")
    print()


def _report_gbs_corpus(rows, window, limit):
    """The number that is directly comparable to the GBS record page's 64 / 171 / 266.

    Same corpus, same imported patterns, ONE thing changed: the unit. An occasion is a PRECURSOR
    TURN (R6 lexical, or P1 absence), not a file. Classes:

      TURN-USED     the occasion turn itself emits a GBS label — the skill answered this claim.
      TURN-PARTIAL  the occasion is in force (an anchor within the window, same context) but the
                    turn carries no label. "Kinda did", at claim granularity.
      TURN-ANU      not in force, no label. **This is the class the file-scoped detector cannot
                    see, and it is expected to rise sharply. That is success, not regression.**
    """
    tot = {"USED": 0, "PARTIAL": 0, "ANU": 0}
    files = {"USED": set(), "PARTIAL": set(), "ANU": set()}
    n_files = n_turns = n_occ = n_exempt = n_unreadable = 0
    worst = []
    for r in rows:
        p = REPO / r["path"]
        if not p.is_file():
            n_unreadable += 1
            continue
        try:
            sc = gbs_turn_scan(p, window)
        except Exception:
            n_unreadable += 1
            continue
        n_files += 1
        n_turns += sc["turns"]
        local = {"USED": 0, "PARTIAL": 0, "ANU": 0}
        for rec in sc["records"]:
            if not (rec["r6"] or rec["p1"]):
                continue                      # P2 is an outcome marker, never an occasion
            if rec["role"] not in ("A", "R"):
                continue                      # Rule 6's precursor is the ASSERTER's turn
            if rec["exempt"]:
                n_exempt += 1
                continue
            n_occ += 1
            cls = "USED" if rec["label"] else ("PARTIAL" if rec["in_force"] else "ANU")
            tot[cls] += 1
            local[cls] += 1
            files[cls].add(r["path"])
        if local["ANU"]:
            worst.append((local["ANU"], r["path"], sc["turns"]))
    worst.sort(reverse=True)
    print()
    print("=" * 88)
    print("GBS TURN-SCOPED, CORPUS-WIDE — comparable to the published file-scoped triple")
    print("=" * 88)
    print("--- DENOMINATORS -------------------------------------------------------------")
    print(f"  transcripts scanned          : {n_files}   (unreadable/skipped: {n_unreadable})")
    print(f"  TURNS scanned                : {n_turns:,}   <- the turn-scoped denominator")
    print(f"  occasions (precursor turns)  : {n_occ:,}")
    print(f"  occasions dropped as EXEMPT  : {n_exempt:,}  (labeled claim / adjacent git verify)")
    print(f"  window                       : {window} turns   [{WINDOW_SOURCE}]")
    print()
    print(f"  {'class':<22} {'FILE-SCOPED (published)':>24} {'TURN-SCOPED occasions':>23} "
          f"{'turn-scoped files':>18}")
    print(f"  {'USED':<22} {'64':>24} {tot['USED']:>23} {len(files['USED']):>18}")
    print(f"  {'PARTIAL':<22} {'171':>24} {tot['PARTIAL']:>23} {len(files['PARTIAL']):>18}")
    print(f"  {'APPLICABLE-NOT-USED':<22} {'266':>24} {tot['ANU']:>23} {len(files['ANU']):>18}")
    print()
    print("  The published column is `wiki/references/skills/ground-before-stating.md` §1, over")
    print("  1,167 transcripts. It is reported here, not replaced. **THE TURN-SCOPED COLUMN IS")
    print("  THE TRUER ONE** — the published one cannot express 'used at turn 40, violated at")
    print("  turn 690', which is exactly what the corpus's most instructive session was.")
    print()
    print(f"  heaviest turn-ANU sessions (top {limit}):")
    for n, path, tn in worst[:limit]:
        print(f"      {n:>5} ANU turns / {tn:>6,} turns   {path}")
    print()
    return 0


def _report_gbs_turns(path, window, limit):
    p = Path(path)
    if not p.is_file():
        p = REPO / path
    if not p.is_file():
        print(f"[not found] {path} — nothing scanned. NOT a result.", file=sys.stderr)
        return 0
    sc = gbs_turn_scan(p, window)
    print()
    print(f"=== GBS DEEP TURN SCAN — {p.name} ===")
    print(f"  turns                 : {sc['turns']:,}   <- the denominator")
    print(f"  compaction boundaries : {sc['compaction']}")
    print(f"  anchors (invoke/label): {sc['anchors']}")
    print(f"  window                : {window} turns")
    print(f"  gbs_record patterns   : "
          f"{'imported' if sc['gbs_record_available'] else 'UNAVAILABLE — R6 not scanned'}")
    fam = {"r6": 0, "p1": 0, "p2": 0}
    unc = {"r6": 0, "p1": 0, "p2": 0}
    for r in sc["records"]:
        for k in fam:
            if r.get(k):
                fam[k] += 1
                if not r["in_force"] and not r["label"] and not r["exempt"]:
                    unc[k] += 1
    print()
    print(f"  {'family':<34} {'turns':>7} {'UNCOVERED (turn-ANU)':>22}")
    print(f"  {'R6 lexical (gbs_record, imported)':<34} {fam['r6']:>7} {unc['r6']:>22}")
    print(f"  {'P1 absence/impossibility (new)':<34} {fam['p1']:>7} {unc['p1']:>22}")
    print(f"  {'P2 self-correction OUTCOME (new)':<34} {fam['p2']:>7} {unc['p2']:>22}")
    print()
    shown = [r for r in sc["records"]
             if (r["p1"] or r["p2"]) and not r["in_force"] and not r["label"]]
    print(f"  uncovered P1/P2 turns ({len(shown)}):")
    for r in shown[:limit]:
        fams = ",".join(k for k in ("r6", "p1", "p2") if r.get(k))
        print(f"      T{r['turn']:<6} role {r['role']}  [{fams}]")
    if len(shown) > limit:
        print(f"      ... {len(shown) - limit} more")
    print()
    return 0


# The hardest real case. Locators are VERBATIM fragments, matched dynamically, because the
# transcript is still growing — line numbers cited in the GBS record page have already moved
# (L32384 was turn 1821 when that page was written and is turn 1818 now). A locator that is a
# line number would rot; a locator that is the text does not.
SEEDED = [
    (1, "settings.json declared uneditable from a single test",
     "was refused by the permission classifier"),
    (2, "false absence: goals.md called gitignored / not in the wiki",
     "Not in the wiki at all"),
    (3, "three register tickets judged without running git log",
     "Possible false closes"),
    (4, "canonical near-publish from a stale ref (record: NOT LOCATED; this is the RELATED turn)",
     "no local `main` branch in this clone"),
    (5, "SubagentStop vs SessionEnd tradeoff asserted before measuring",
     "I'd framed that as a tradeoff"),
]
SEEDED_FILE = ("raw/transcripts/claude-code/"
               "code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-updates.md")


def _verify_seeded(window=None):
    """Does turn-scoping surface Jon's five, in the session that scores USED file-scoped?

    The rule this obeys, from the brief that ordered it: **if it surfaces none of them the
    turn-scoping is wrong and this must say so, rather than adjusting the window until it
    passes.** The window is therefore NOT a free parameter here — it is whatever the corpus
    calibration produced, and the result is reported against that.
    """
    p = REPO / SEEDED_FILE
    print()
    print("=" * 88)
    print("HARDEST REAL CASE — f01909, which scores USED file-scoped and contains five verified")
    print("Rule 6 failures. If turn-scoping surfaces none, turn-scoping is wrong. Not the window.")
    print("=" * 88)
    if not p.is_file():
        print(f"  [transcript not on disk] {SEEDED_FILE}")
        print("  NOT a result — nothing was verified.")
        return 0
    ir = require_index("corpus_index --verify-seeded (window calibration only)")
    rl = list(ir.rows.values()) if ir.fresh else []
    if not ir.fresh:
        print(f"  [window calibrated from DEFAULT, not the index — {ir.status}; "
              f"{ir.n_rows_on_disk} rows on disk unreadable at this schema]")
    w = window or (set_default_window(rl) if rl else WINDOW_DEFAULT)

    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    ti = turn_index(str(p))
    turns = ti["turns"]

    def turns_of(frag):
        """EVERY turn the fragment occurs in, not the first.

        The first version of this took `text.find()` and reported one turn. For failure #1 that
        landed on turn 135, role `H` — which is not Jon at all but a harness-injected
        `<task-notification>` block relaying a subagent's summary. The session's OWN assertion is
        at turns 656 and 667. A first-match locator answered a question about the main thread
        with a quote from an agent's report. Enumerate, then judge; never take the first hit.
        """
        out, i = [], 0
        while True:
            i = text.find(frag, i)
            if i < 0:
                return out
            ln = text[:i].count("\n") + 1
            hit = None
            for t in turns:
                if t["line"] <= ln:
                    hit = t
                else:
                    break
            if hit:
                out.append(hit)
            i += 1

    sc = gbs_turn_scan(p, w)
    by_turn = {r["turn"]: r for r in sc["records"]}

    # file-scoped verdict, for the contrast
    row = rows.get(SEEDED_FILE.replace("\\", "/"))
    fs = "USED (marker present)" if row and "ground-before-stating" in row.get("markers", []) \
        else "no GBS marker"
    print(f"  turns                      : {ti['turn_count']:,}")
    print(f"  compaction boundaries      : {sc['compaction']}")
    print(f"  GBS anchors (invoke/label) : {sc['anchors']}")
    print(f"  window                     : {w} turns   [{WINDOW_SOURCE}]")
    print(f"  FILE-SCOPED verdict        : {fs}  <- the whole session, one label")
    print()
    def judge(t, win):
        r = by_turn.get(t["t"])
        inf = in_force(t["t"], sc["anchors"], sc["compaction"], win)
        fams = tuple(bool(r and r[k]) for k in ("r6", "p1", "p2"))
        return fams, inf, (any(fams) and not inf and not (r and r["label"]))

    print(f"  {'#':<3} {'turns':>16} {'role':>5} {'in-force':>9} {'R6':>4} {'P1':>4} {'P2':>4} "
          f"{'SURFACED':>9}  failure")
    surfaced = 0
    for n, desc, frag in SEEDED:
        ts = turns_of(frag)
        if not ts:
            print(f"  {n:<3} {'--':>16} {'--':>5} {'--':>9} {'--':>4} {'--':>4} {'--':>4} "
                  f"{'NOT-IN-CORPUS':>9}  {desc}")
            continue
        # A failure is SURFACED if ANY occurrence of it surfaces. The row shows the occurrence
        # that surfaced, or the first one when none did.
        rows_ = [(t,) + judge(t, w) for t in ts]
        pick = next((x for x in rows_ if x[3]), rows_[0])
        t, fams, inf, hit = pick
        surfaced += 1 if hit else 0
        allt = ",".join(f"{x['t']}{x['role']}" for x in ts)
        print(f"  {n:<3} {allt:>16} {t['role']:>5} {str(inf):>9} {str(fams[0]):>4} "
              f"{str(fams[1]):>4} {str(fams[2]):>4} {('YES' if hit else 'no'):>9}  {desc}")
    print()
    print(f"  SURFACED: {surfaced} of {len(SEEDED)}   at the CALIBRATED window ({w} turns).")
    print()
    print("--- SURFACED vs WINDOW — the dependence, disclosed instead of exploited -------")
    print("  The brief's rule: if it surfaces none, turn-scoping is wrong and I say so rather")
    print("  than adjusting the window until it passes. So the window stays at the measured p90")
    print("  and the WHOLE curve is printed. Read the p90 row as the result; read the rest as")
    print("  the honest statement that this result is window-sensitive.")
    print(f"  {'window':>8} | {'surfaced':>8} | which")
    for win in (5, 10, 27, 63, 100, 250, 10 ** 9):
        got = []
        for n, _d, frag in SEEDED:
            ts = turns_of(frag)
            if any(judge(t, win)[2] for t in ts):
                got.append(str(n))
        tag = "  <- p75" if win == 27 else ("  <- p90, THE DEFAULT" if win == 63 else "")
        lbl = "inf" if win > 10 ** 8 else str(win)
        print(f"  {lbl:>8} | {len(got):>8} | {','.join(got) or '-'}{tag}")
    print("  Read this against the record's own finding: **every one of the five is invisible to")
    print("  the R6 lexical detector** — none matches `R6_RISK` at its own turn, verified above in")
    print("  the R6 column. Anything surfaced here was surfaced by P1/P2 or not at all.")
    print()
    print("  THE FITTING DISCLOSURE, because it is the part most likely wrong: P1 and P2 were")
    print("  written AFTER reading these five. P1's derivation is from Rule 6's own text and its")
    print("  independent corroboration is the SIXTH instance the GBS record agent found before")
    print("  P1 existed (turn 1218). P2 is an outcome marker, not a precursor. Neither claim")
    print("  removes the fitting risk; both are stated so a reader can discount for it.")
    print()
    return 0


# =================================================================================================
# SELF-TEST — negative controls first; the direction that matters is the one that inflates
# =================================================================================================
def self_test():
    ok = True
    print("=== SELF-TEST — corpus_index ===")

    def chk(label, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")

    # ---------------------------------------------------------------------------------------
    # STALE-SCHEMA CONTROLS — the 2026-08-06 defect, tested in BOTH directions.
    # These build tiny indices in a temp dir. The real index is never read or written here.
    # ---------------------------------------------------------------------------------------
    import tempfile
    with tempfile.TemporaryDirectory() as _td:
        _d = Path(_td)
        _row = json.dumps({"path": "a/b.md", "id": "abc123"}, sort_keys=True)

        def _write(name, schema, n=3):
            f = _d / name
            hdr = ("#" + json.dumps({"schema": schema, "rows": n}, sort_keys=True) + "\n") \
                if schema is not None else ""
            f.write_text(hdr + "".join(
                json.dumps({"path": f"a/{i}.md", "id": "abc123"}, sort_keys=True) + "\n"
                for i in range(n)), encoding="utf-8")
            return f

        fresh = _write("fresh.jsonl", SCHEMA_VERSION)
        stale = _write("stale.jsonl", "corpus-index-v0")
        headless = _write("headless.jsonl", None)
        empty = _d / "empty.jsonl"
        empty.write_text("#" + json.dumps({"schema": SCHEMA_VERSION}) + "\n", encoding="utf-8")
        missing = _d / "nope.jsonl"

        chk("FRESH index reads FRESH with all rows",
            read_index(fresh).status == INDEX_FRESH and len(read_index(fresh).rows) == 3)
        # POSITIVE CONTROL for the defect: rows must NOT vanish into a bare count.
        _s = read_index(stale)
        chk("STALE index -> status STALE_SCHEMA, NOT ABSENT", _s.status == INDEX_STALE)
        chk("STALE index still reports n_rows_on_disk=3 (the denominator that proves "
            "STALE != ABSENT)", _s.n_rows_on_disk == 3)
        chk("STALE index names BOTH schemas",
            _s.schema_on_disk == "corpus-index-v0" and _s.schema_expected == SCHEMA_VERSION)
        chk("STALE banner is non-empty and says UNKNOWN, not zero",
            "UNKNOWN" in _s.banner("self-test") and _s.banner("self-test") != "")
        chk("STALE exits 3, FRESH exits 0",
            _s.exit_code == 3 and read_index(fresh).exit_code == 0)
        # NEGATIVE CONTROL: a genuinely absent index must NOT be dressed up as stale.
        chk("MISSING file -> ABSENT with 0 rows on disk",
            read_index(missing).status == INDEX_ABSENT
            and read_index(missing).n_rows_on_disk == 0)
        chk("header-only index -> ABSENT (0 rows), not STALE",
            read_index(empty).status == INDEX_ABSENT)
        chk("headerless index with rows -> MALFORMED_HEADER, not ABSENT",
            read_index(headless).status == INDEX_MALFORMED
            and read_index(headless).n_rows_on_disk == 3)
        chk("FRESH banner is EMPTY (no false alarm — the RATIO_FLOOR lesson)",
            read_index(fresh).banner("self-test") == "")
        # load_prior's build-path contract is UNCHANGED: stale still discards.
        chk("load_prior still returns {} on STALE (auto-rebuild preserved)",
            load_prior(stale)[0] == {})
        chk("load_prior returns the rows on FRESH", len(load_prior(fresh)[0]) == 3)

    skills = load_skills()
    chk(f"skills/ enumerated ({len(skills)} SKILL.md found)", len(skills) >= 20)
    chk("frame-before-commit triggers generated from its description",
        "frame before commit" in skills.get("frame-before-commit", {}).get("triggers", []))

    rows, stats, _ = build(dry_run=True)
    chk(f"corpus walked ({stats['seen']} files seen)", stats["seen"] > 0)
    chk("indexed == seen - unreadable",
        stats["indexed"] == stats["seen"] - stats["unreadable"])

    # NEGATIVE CONTROL 1 — a marker that exists nowhere must produce zero USED. If this cannot
    # return zero, every positive count is meaningless.
    fake = {"__negative_control__": {
        "marker": ["zzqx no such marker 9f3a7c1e exists in any transcript"],
        "completion": None, "src": "synthetic"}}
    hits = 0
    for p, rel in walk_corpus()[:200]:
        r = scan_file(p, rel, skills, marker_reg=fake)
        hits += 1 if r and r["markers"] else 0
    chk("absent marker yields 0 hits over a 200-file sample (the check can fire)", hits == 0)

    # POSITIVE CONTROL — the FBC marker must be found somewhere. Grep measured 170 files on
    # 2026-08-06; the index must not report zero.
    n_fbc = sum(1 for r in rows if "frame-before-commit" in r["markers"])
    chk(f"FBC marker found in the corpus ({n_fbc} files) — index is not silently empty", n_fbc > 0)

    # NEGATIVE CONTROL — a PATH is not a slash command. This regression is real: before the fix,
    # `/frame-before-commit` matched inside `skills/frame-before-commit/SKILL.md` and a session
    # that merely listed the file scored as Jon invoking the protocol.
    sl = skills["frame-before-commit"]["slash"]
    chk("a path mention does NOT count as a slash command",
        not sl.search(JU.normalize("read skills/frame-before-commit/SKILL.md for the rules")))
    chk("a real slash command DOES count",
        bool(sl.search(JU.normalize("ok /frame-before-commit on this question"))))

    # NEGATIVE CONTROL 2 — an UNDECLARED skill must report UNDECLARED, not zero uses.
    und = next((s for s in skills if s not in MARKERS), None)
    q = three_class(rows, und, skills) if und else None
    chk(f"undeclared skill `{und}` reports UNDECLARED, not 0 uses",
        q is not None and q["marker_state"].startswith("UNDECLARED") and q["USED"] == [])

    # PARTIAL must be None (undetectable), not [], for a skill with no completion literal.
    q2 = three_class(rows, "ground-before-stating", skills)
    chk("skill with no completion literal reports PARTIAL undetectable (None), not empty",
        q2["PARTIAL"] is None)

    # Idempotence key must change with size and with mtime, and only with those.
    k = lambda r: (r["path"], r["size"], r["mtime"])
    base = {"path": "a", "size": 100, "mtime": 5}
    chk("incremental key stable on identical bytes", k(base) == k(dict(base)))
    chk("incremental key changes on size", k(base) != k({**base, "size": 101}))
    chk("incremental key changes on mtime", k(base) != k({**base, "mtime": 6}))

    # No row may carry transcript content. Every value is a scalar, a list of slugs, or a path.
    bad = []
    for r in rows[:500]:
        for kk, vv in r.items():
            if isinstance(vv, str) and len(vv) > 300:
                bad.append((r["path"], kk))
    chk(f"no row field carries transcript content ({len(bad)} oversized string fields)", not bad)

    # Sidecars must be excluded — coverage_gap's rule, imported.
    chk("no .sidecar.md row in the index",
        not any(r["path"].endswith(".sidecar.md") for r in rows))

    # THE ANTI-DIVERGENCE CONTROL. `in_coverage_gap_scope` must be set-EQUAL to what
    # `coverage_gap.conversations()` itself returns. If this ever fails, this index has become
    # the sixth corpus definition and its numbers must not be quoted next to that script's.
    cg_set = {str(Path(p).relative_to(REPO)).replace("\\", "/")
              for p in CG.conversations(str(REPO))}
    mine = {r["path"] for r in rows if r["in_coverage_gap_scope"]}
    chk(f"in_coverage_gap_scope == coverage_gap.conversations() "
        f"({len(mine)} vs {len(cg_set)}; sym-diff {len(mine ^ cg_set)})", mine == cg_set)

    # raw/ MUST BE UNTOUCHED — Jon's standing NO DESTRUCTIVE ACTS constraint.
    #
    # The first version of this control grepped its own source for "shutil"/"os.remove" and
    # FAILED, because those literals were sitting in the check itself. A source-grep control is
    # satisfied or defeated by its own text; it tests nothing. Replaced with the property itself:
    # take a real before/after of the corpus on disk across a full build.
    sample = [p for p, _ in walk_corpus()][::37]          # a spread, not the first N
    before = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    build(full=True, dry_run=True)
    after = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    chk(f"a full build leaves raw/ byte- and mtime-identical ({len(sample)} sampled)",
        before == after)
    chk("both write targets resolve under wiki/, none under raw/",
        OUT_JSONL.is_relative_to(REPO / "wiki") and OUT_MD.is_relative_to(REPO / "wiki"))

    # ---------------------------------------------------------------------------------------
    # TURN-SCOPED CONTROLS. Negative first — the direction that matters is the one that inflates
    # APPLICABLE-NOT-USED, because this build EXPECTS that number to rise and an instrument that
    # is expected to rise will happily rise for the wrong reason.
    # ---------------------------------------------------------------------------------------
    # A compaction boundary between anchor and turn must sever coverage, at any window.
    chk("compaction boundary severs coverage (anchor 10, turn 12, boundary 11)",
        not in_force(12, [10], [11], 10 ** 9))
    chk("no boundary between -> covered at the same distance",
        in_force(12, [10], [], 10 ** 9))
    chk("window smaller than the distance -> not covered",
        not in_force(60, [10], [], 40) and in_force(45, [10], [], 40))
    chk("an anchor AFTER the turn does not cover it (no backwards-in-time coverage)",
        not in_force(10, [50], [], 10 ** 9))
    # Forward coverage is the mirror and must not be symmetric with the backward one.
    chk("forward: marker after the trigger inside the window answers it",
        answered_forward(10, [30], [], 40) and not answered_forward(10, [30], [], 5))
    chk("forward: a marker BEFORE the trigger does not answer it — the file-scoped bug itself",
        not answered_forward(340, [12], [], 10 ** 9))

    # NEGATIVE CONTROL — P1/P2 must not fire on neutral prose. A precursor that matches ordinary
    # text turns turn-ANU into the same noise the file-scoped class already was.
    neutral = ("I read the file with git show and it contains three entries; the register is "
               "current and the counts agree with the tracker.")
    chk("P1 does not fire on neutral prose", not P1_ABSENCE.search(neutral))
    chk("P2 does not fire on neutral prose", not P2_SELFCORRECT.search(neutral))
    chk("P1 fires on the shape it was derived from (an absence assertion)",
        bool(P1_ABSENCE.search("Gitignored. Not in the wiki at all.")))
    chk("P2 fires on a retrospective self-correction",
        bool(P2_SELFCORRECT.search("goals.md is tracked in git. I said it was gitignored.")))

    # Turn-scoped classes must be a REFINEMENT of the file-scoped ones, not a different corpus:
    # every occasion must live in a file the file-scoped query also considers applicable.
    sk = load_skills()
    if rows and "marker_turns" in rows[0]:
        fq = three_class(rows, "ground-before-stating", sk)
        tq = turn_three_class(rows, "ground-before-stating", sk, 40)
        occ_files = {p for p, _ in tq["TURN_APPLICABLE_NOT_USED"]} | \
                    {p for p, _ in tq["TURN_USED"]}
        fs_files = set(fq["USED"]) | set(fq["APPLICABLE_NOT_USED"] or [])
        chk(f"every turn-scoped occasion file is a file-scoped candidate too "
            f"({len(occ_files - fs_files)} strays)", not (occ_files - fs_files))
        # THE CLASS THIS BUILD EXISTS FOR: turn-ANU must EXCEED file-ANU. If it does not, the
        # unit did not actually change and the whole exercise is decoration.
        chk(f"turn-scoped ANU ({len(tq['TURN_APPLICABLE_NOT_USED'])}) exceeds file-scoped ANU "
            f"({len(fq['APPLICABLE_NOT_USED'] or [])}) — the unit really changed",
            len(tq["TURN_APPLICABLE_NOT_USED"]) > len(fq["APPLICABLE_NOT_USED"] or []))
        # marker_turns may never name a slug absent from markers — positional is a refinement.
        stray = [r["path"] for r in rows[:400]
                 if set(r.get("marker_turns", {})) - set(r.get("markers", []))]
        chk(f"marker_turns never names a slug absent from markers ({len(stray)} strays)", not stray)
    else:
        chk("index carries turn positions (schema v2) — rebuild if this fails", False)

    # The lazy import must not be a cycle, and must degrade rather than raise.
    G = _gbs_module()
    chk("gbs_record patterns import lazily without a cycle (or degrade to None)",
        G is None or hasattr(G, "R6_RISK"))

    print("\nRESULT: " + ("PASS — controls fire in both directions." if ok
                          else "FAIL — do not trust its counts."))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--full", action="store_true", help="ignore the prior index; rescan every file")
    ap.add_argument("--dry-run", action="store_true", help="measure and report; write nothing")
    ap.add_argument("--query-skill", help="three-class query for one skill, from the index")
    ap.add_argument("--query-skill-turns", metavar="SLUG",
                    help="TURN-SCOPED three-class query, printed beside the file-scoped one")
    ap.add_argument("--window", type=int, default=None,
                    help="turn window; default is the measured p90 (see --calibrate-window)")
    ap.add_argument("--calibrate-window", metavar="SLUG", nargs="?", const="ground-before-stating",
                    help="print the measured invocation->label decay distribution")
    ap.add_argument("--gbs-turns", metavar="PATH",
                    help="per-turn GBS record for one transcript (deep mode)")
    ap.add_argument("--verify-seeded", action="store_true",
                    help="the hardest real case: f01909 and Jon's five verified Rule 6 failures")
    ap.add_argument("--index-status", action="store_true",
                    help="report FRESH/STALE_SCHEMA/ABSENT/MALFORMED and EXIT NON-ZERO if not "
                         "FRESH (0/3/4/5). The only non-zero exit in this script.")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--limit", type=int, default=12, help="paths shown per class in --query-skill")
    args = ap.parse_args(argv)

    if args.index_status:
        # THE ONE NON-ZERO EXIT, AND WHY IT CANNOT BREAK THE SU GATE.
        # Nothing invokes it yet: `grep -rn corpus_index scripts/lanes/ scripts/*.sh
        # scripts/audit/su_close.sh scripts/audit/su_gate.sh` returns ZERO hits — corpus_index.py
        # is not on any gate path at all. The exit code is confined to THIS flag; the default
        # build, every --query-*, and --self-test all still return 0 on every path, so adding the
        # flag cannot change the status of anything that runs today. A future gate that wants a
        # machine-checkable staleness signal now has one instead of parsing prose.
        ir = read_index()
        print(f"index         : {OUT_JSONL}")
        print(f"status        : {ir.status}")
        print(f"schema on disk: {ir.schema_on_disk}")
        print(f"schema expected: {ir.schema_expected}")
        print(f"rows on disk  : {ir.n_rows_on_disk}   parsed: {len(ir.rows)}   "
              f"malformed: {ir.n_malformed}")
        if not ir.fresh:
            print(ir.banner("corpus_index --index-status"), file=sys.stderr)
        print(f"exit          : {ir.exit_code}")
        return ir.exit_code

    if args.self_test:
        return self_test()

    if args.calibrate_window is not None:
        ir = require_index("corpus_index --calibrate-window")
        if not ir.fresh:
            print(f"window calibration = UNKNOWN  ({ir.status}; {ir.n_rows_on_disk} rows on "
                  f"disk). This is NOT a result.", file=sys.stderr)
            return 0
        rows = ir.rows
        rl = list(rows.values())
        slug = args.calibrate_window
        d = calibrate(rl, slug)
        print()
        print(f"=== WINDOW CALIBRATION — {slug} ===")
        print(f"  index rows                     : {len(rl)}")
        print(f"  invocation->label pairs measured: {len(d)}   "
              f"(pairs crossing a compaction boundary are EXCLUDED — across one, the distance")
        print("                                    is not a decay observation, it is two contexts)")
        if d:
            for p in (50, 75, 90, 95, 99, 100):
                print(f"  p{p:<3}                            : {pct(d, p)} turns")
        else:
            print("  NO PAIRS — the window is UNMEASURED for this skill. Not zero: unmeasured.")
        print()
        print("  The default window is p90: the span within which 90% of invocations that ever")
        print("  demonstrably produced a label produced one. Beyond it, invocations stop showing")
        print("  effect. CIRCULAR BY CONSTRUCTION — measured from the corpus it then classifies.")
        print("  A calibration, not a validation. `--window N` overrides it.")
        print()
        _sensitivity(rl, slug, load_skills())
        return 0

    if args.gbs_turns:
        ir = require_index("corpus_index --gbs-turns")
        rl = sorted(ir.rows.values(), key=lambda r: r["path"]) if ir.fresh else []
        w = args.window or (set_default_window(rl) if rl else WINDOW_DEFAULT)
        if args.gbs_turns.upper() == "ALL":
            if not rl:
                print(f"corpus-wide GBS record = UNKNOWN  ({ir.status}; {ir.n_rows_on_disk} "
                      f"rows on disk). NOT a result.", file=sys.stderr)
                return 0
            return _report_gbs_corpus(rl, w, args.limit)
        return _report_gbs_turns(args.gbs_turns, w, args.limit)

    if args.verify_seeded:
        return _verify_seeded(args.window)

    if args.query_skill_turns:
        ir = require_index(f"corpus_index --query-skill-turns {args.query_skill_turns}")
        rows, bad = (ir.rows, ir.n_malformed) if ir.fresh else ({}, ir.n_malformed)
        skills = load_skills()
        if not ir.fresh:
            print(f"TURN-SCOPED classes = UNKNOWN  ({ir.status}; {ir.n_rows_on_disk} rows on "
                  f"disk, unreadable at this schema)")
            print("This is NOT a result. Nothing was queried.", file=sys.stderr)
            return 0
        rl = sorted(rows.values(), key=lambda r: r["path"])
        if "marker_turns" not in (rl[0] if rl else {}):
            print("[index is schema v1 — no turn positions] rebuild it first.", file=sys.stderr)
            return 0
        w = args.window or set_default_window(rl)
        _report_side_by_side(rl, args.query_skill_turns, skills, w, bad, args.limit)
        return 0

    if args.query_skill:
        ir = require_index(f"corpus_index --query-skill {args.query_skill}")
        rows, bad = (ir.rows, ir.n_malformed) if ir.fresh else ({}, ir.n_malformed)
        skills = load_skills()
        if not ir.fresh:
            print(f"USED / PARTIAL / APPLICABLE_NOT_USED = UNKNOWN  ({ir.status}; "
                  f"{ir.n_rows_on_disk} rows on disk, unreadable at this schema)")
            print("This is NOT a result. Nothing was queried.", file=sys.stderr)
            return 0
        q = three_class(sorted(rows.values(), key=lambda r: r["path"]), args.query_skill, skills)
        print()
        print(f"=== THREE-CLASS QUERY — {args.query_skill} ===")
        print(f"  index read            : {ir.one_line()}")
        print(f"  index rows read       : {len(rows)}  (malformed/stale: {bad})")
        print(f"  marker      : {q['marker_state']}")
        print(f"  completion  : {q['completion_state']}")
        print(f"  trigger     : {q['trigger_state'][:160]}")
        print()
        for cls in ("USED", "PARTIAL", "APPLICABLE_NOT_USED"):
            v = q[cls]
            if v is None:
                print(f"  {cls:<20} UNDETECTABLE for this skill — reported as such, not as 0")
                continue
            print(f"  {cls:<20} {len(v)}")
            for p in v[:args.limit]:
                print(f"      {p}")
            if len(v) > args.limit:
                print(f"      ... {len(v) - args.limit} more")
        print()
        return 0

    rows, stats, skills = build(full=args.full, dry_run=args.dry_run)
    print_report(rows, stats, skills)
    if args.dry_run:
        print("  [--dry-run] nothing written")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(0)     # never blocks
