#!/usr/bin/env python3
"""skill_record.py — the accumulated session record, GENERALISED across skills.

WHY THIS EXISTS — Jon, verbatim, 2026-08-06
---------------------------------------------
    "For each skill, in the wiki, accumulated session record. Not just explicit uses, but
     implicit ones. Opportunitys where you might have considered using it but did not, and
     cases where you did and cases where you kinda did... the wiki shpuld help you improve
     the skill."

**The acceptance test is "help improve the skill", not completeness.**

WHY IT IS NOT A THIRD SCANNER — stated exactly, including where reuse stops
-----------------------------------------------------------------------------
`corpus_index.py` walks the corpus and answers the three-class query from a marker/trigger
index. `gbs_record.py` answered it for ONE skill by adding object-level precursors. This file
is the **general layer over both**, and it imports rather than re-derives:

  * `corpus_index.load_prior` / `.load_skills` / `.three_class` / `.CORPUS` — the on-disk index,
    the generated trigger table, and the reference three-class query. `CORPUS` therefore still
    resolves, transitively, to `coverage_gap.CORPUS`. **One corpus root, still.**
  * `gbs_record.spans` — the turn-span splitter (roles H/A/C/R/D via the ratified `turn_index`;
    `D` is an orchestrating agent's dispatch, **never Jon**). Imported, not copied. If it is
    wrong it is wrong in one place.
  * `gbs_record.MERGE_CHARS` — the same "two patterns in one sentence are one occurrence" rule.

**`gbs_record.py` is not superseded and is not edited by this file.** It holds GBS's eight-rule
precursor registry, which is genuinely GBS-shaped. The intended end state is that its registry
becomes the `ground-before-stating` entry in `RECORDS` below and its module keeps only the
rules; that fold is one PR and belongs to whoever owns that file. It is registered here as a
DELEGATE so a reader running `--skill ground-before-stating` is sent to it rather than served a
second, divergent answer.

WHAT THE GENERAL LAYER ADDS THAT `corpus_index` CANNOT DO
------------------------------------------------------------
`corpus_index.three_class` is presence-of-string. Three things break on that, and all three
break in the same direction — **inflation**:

 1. **The template is not a run.** `[FRAME-BEFORE-COMMIT - PURE - {N} branches]` appears in
    SKILL.md, in every file that pastes SKILL.md, and in every agent brief that quotes the
    format. B-8 measured 66 of 245 marker hits as template or filename. This file separates
    them by requiring a branch count that is a NUMBER, not the literal `{N}`.
 2. **A re-quote is not a run.** `_superseded/`, `.sidecar` companions, and extraction
    subagents re-emit earlier runs verbatim; B-8 found one delta in five files. Deltas are
    therefore deduped on normalised text, so the headline is **distinct assertions**, not hits.
 3. **`USED` and `PARTIAL` are NOT disjoint in `three_class`.** Read it: `USED` is every
    marker-bearing row and `PARTIAL` is the subset of those lacking the completion literal. So
    "252 USED vs 134 PARTIAL" is not a ratio between two classes — it is 252 files of which 134
    have no `[COMMIT]`. **This file prints them disjointly and prints the overlap**, because a
    number that reads as a ratio and is not one is the failure mode this repo keeps paying for.

WHAT IT CANNOT SEE — printed, never silently zeroed
-----------------------------------------------------
  * **Real vs cosmetic deltas.** B-8 s9.3 split corpus deltas four ways: real / cosmetic /
    empty / miscredited. Only **empty** and **miscredited** have a mechanical signature (a
    template placeholder left in the output; a source that is not a branch id). The real/cosmetic
    split is a judgment about whether an outcome changed and is reported **UNKNOWN — needs a
    cold grader**, which is exactly what B-8's Revised Improvement 2 asks for. A lexical
    cosmetic LOWER BOUND is printed and labelled as a lower bound.
  * **Whether a candidate was an occasion.** `corpus_index` learned this the expensive way and
    prints it: 4 of 4 FBC candidates opened by hand were Jon *discussing* the protocol. Every
    APPLICABLE-NOT-USED count here is a **candidate count**.
  * **Tier-2 precursors are a proxy for a judgment.** "A commitment was made on a design
    question without alternatives" is what FBC's own frontmatter describes; the lexical test for
    it over-counts and says so.

Exit code is **always 0.** An instrument, not a gate. It only ever READS `raw/`.

Usage:
  skill_record.py --skill frame-before-commit          # full report with denominators
  skill_record.py --skill frame-before-commit --anu    # enumerate the not-used candidates
  skill_record.py --skill frame-before-commit --deltas # delta-quality breakdown
  skill_record.py --self-test                          # negative controls
"""
import argparse
import hashlib
import io
import json
import re
import sys
from collections import Counter
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

import corpus_index as CI                          # noqa: E402  index + reference query
import gbs_record as GR                            # noqa: E402  turn spans + merge rule (reused)

REPO = CI.REPO
spans = GR.spans
MERGE_CHARS = GR.MERGE_CHARS

# =================================================================================================
# FBC's OWN OUTPUT SURFACE — read out of SKILL.md, not recalled. Line cites are to that file.
# =================================================================================================
# SKILL.md:69 — the pure-mode header. A GENUINE run substitutes a digit for `{N}`.
RUN_OPEN = re.compile(r"\[frame-before-commit\s*[-–—]{1,2}\s*(pure|directed)?", re.I)
# SKILL.md:69,74 — the template forms, verbatim. These are DOCUMENTATION, not runs.
TEMPLATE = re.compile(
    r"\{N\}\s*branches|label:\s*TBD|"
    r"\[DELTA:\s*Bn\s*\(LABEL\)|"
    r"\{First distinct sub-thought|\{\.\.\.same ID-only rule",
    re.I,
)
# A run header whose branch count is an actual integer.
RUN_HEADER_NUMERIC = re.compile(
    r"\[frame-before-commit[^\]]{0,40}?\b([2-9]|1[0-9])\s*branch", re.I)
BRANCH_REGISTRY = re.compile(r"\[branch registry\]", re.I)
COMMIT = re.compile(r"\[commit\]", re.I)
META = re.compile(r"\[meta\]", re.I)
DELTA = re.compile(r"\[delta:", re.I)

# SKILL.md:74 — the delta template line, left in an output verbatim = an EMPTY delta.
DELTA_EMPTY = re.compile(
    r"Bn\s*\(LABEL\)|"
    r"without it,?\s*X\b|with it,?\s*Y\b|"
    r"commit would have said:\s*X\b|commit says:\s*Y\b|"
    r"\bby:\s*\.\.\.|\.\.\.\s*\]?\s*$",
    re.I,
)
# A delta whose credited source is not a branch. B-8 s9.3: `[DELTA: your messages - ...]`.
DELTA_MISCREDIT = re.compile(
    r"^\s*(your messages|jon|user|the human|your (?:input|correction|reply))\b", re.I)
# A delta crediting a branch id, which is the shape Discipline Rule 6 requires.
DELTA_BRANCHED = re.compile(r"^\s*(B\d|P\d|M\d|FRAME\s*\d)", re.I)
# LOWER BOUND ONLY — presentation-level words. Absence proves nothing.
DELTA_COSMETIC_LEX = re.compile(
    r"closing frame|reframe|re-frame|framing|wording|phrasing|added (?:a )?(?:caveat|justification|"
    r"nuance)|sharpen|strengthen(?:ed|s)? the (?:case|argument)|presentation|"
    r"same conclusion|conclusion (?:is )?unchanged",
    re.I,
)

# -------------------------------------------------------------------------------------------------
# TWO DEFLATORS THAT ARE PATH FACTS, NOT TEXT FACTS
# -------------------------------------------------------------------------------------------------
# An EXTRACTION subagent re-emits an earlier session's run verbatim into a new file with a new
# date. Counting those as runs is what makes "FBC is still in use" true in July when the run being
# counted happened in May. B-8 s9.1 measured the same duplication (one delta in five files).
REEMISSION = re.compile(r"/subagents/.*(extract|retriev|corpus|mirror-read)|/_superseded/", re.I)
# SELF-CONTAMINATION. B-8 s9.2 caught this and named it: the agents auditing FBC quote FBC's
# markers, so an audit of FBC inflates FBC's own usage on the day the audit runs. Named by
# filename slug rather than by date, so the guard survives the date changing.
#
# THE PATTERN WAS WRONG BY TWO CHARACTERS AND THAT IS THE WHOLE LESSON, 2026-08-07
# ----------------------------------------------------------------------------------
# The first version missed the ticket's OWN record page and the FBC record-page agent:
#   * `b-8-improve` vs `B-8-improv[ing]` -- `improve` ends `...v-e`, `improving` ends `...v-i-n-g`.
#     One character, and the alternative never fires.
#   * `fbc.?gbs` vs `fbc-and-gbs` -- `.?` spans ONE char; `-and-` is five.
#   * `gbs-skill-session-record` was declared and `fbc-skill-session-record` was not, so the
#     GBS record-page agent was deflated and its FBC twin, written the same hour by the same
#     coordinator, was counted as a genuine FBC run.
# A deflator that names its targets by exact slug is a `derive-don't-record` instance: the slug
# is written once here and again by whoever names the agent, and the two diverge silently. The
# repair below is STEMMED (`improv`, `record`) and SIDE-AGNOSTIC (`(?:fbc|gbs)`) so a new agent
# has to leave the vocabulary entirely, not merely inflect a verb, to escape it.
SELF_AUDIT = re.compile(
    # -- original six, unchanged; nothing that matched before stops matching --------------
    r"break-b-8|b-8-improve|search-corpus-for-real-fbc|fbc.?gbs|"
    r"gbs-skill-session-record|consult-fable-mirror-and-review-wiki|"
    # -- the two verified misses, repaired at the stem rather than the inflection ----------
    r"b-?8-improv|fbc[-_ ]?(?:and[-_ ]?)?gbs|(?:fbc|gbs)-skill-session-record|"
    # -- agents whose TASK was to audit, measure, record or repair FBC/GBS -----------------
    #    Each of these emits the markers of the thing it is auditing. Verified by opening the
    #    frontmatter `agent_description` of the four sampled below, not inferred from the slug.
    r"(?:fbc|gbs)-(?:trigger|decision-log|seal|fork)|"
    r"fbc-decision-log|fbc-seal-the-instinct|gbs-object-level-trigger|"
    r"gbs-trigger-gap-audit|design-a-fix-for-ground-before-stat|"
    r"(?:evaluate|analyze|analyse|read|deep-read|explore)-.{0,12}"
    r"(?:frame-before-commit|fbc\b)|"
    r"skill-evolution-framework-and-fbc|the-fbc-decision-log|cross-check-meta-fbc",
    re.I)

# -------------------------------------------------------------------------------------------------
# FAN-OUT — one run dispatched as N branch agents is ONE run, not N. NEW 2026-08-07.
# -------------------------------------------------------------------------------------------------
# This is a DIFFERENT defect from self-contamination and folding it into `SELF_AUDIT` would hide
# it. On 2026-07-13, 2026-07-16 and 2026-08-06 an FBC run was executed by dispatching each BRANCH
# to its own subagent, plus a cold synthesiser. Every one of those transcripts carries a genuine
# branch shape -- they ARE real FBC work -- so no template deflator and no self-audit deflator can
# touch them. Counted naively they turn 3 runs into 22 files.
#
# The fix is not to delete them: a branch agent is evidence the protocol ran. It is to count them
# as MEMBERS OF A RUN, keyed on the parent session directory, so the headline is runs and the
# member count is printed beside it. Verified against frontmatter: the 2026-07-16 `fbc-frame-a`
# agent declares `parent_session: da51cc75-...` and `spawn_depth: 1`; the 2026-08-06 `fbc-frame-1`
# agent declares `parent_session: f0190965-...` and `spawn_depth: 2`.
#
# DELIBERATELY NOT MATCHED: `raw/transcripts/claude-ai/fl/fbc-pure-3branch-...`, `fbc-4branch`,
# `fbc-6branch`, `fbc-true-null` (2026-04-15). Those are test-master CONDITION runs -- one whole
# protocol execution per file, in one conversation, with its own [DELTA] set. Deflating them would
# delete the only clean FBC runs in the record, which is the failure direction that costs most.
# The frame identifier is NOT always a digit or a letter. The 2026-07-13 family names its
# branches by TOPIC (`meta-fbc-frame-group`, `-search`, `-null`, `-on-instinct`), and a first
# version of this pattern requiring a digit-or-[a-f] matched 0 of those 6 — the same class of
# two-character miss the SELF_AUDIT repair above exists to close, reproduced 40 lines later and
# caught only because the before/after was printed. So the discriminator is the PREFIX, which is
# what actually names the shape.
FANOUT = re.compile(
    r"(?:meta-)?fbc-frame-|"
    r"cold-(?:fbc-)?synthes(?:is|izer|iser)", re.I)
FANOUT_PARENT = re.compile(r"/subagents/([0-9a-f]{6,})/", re.I)

# B-8 s9.4 — convergence being scored as the run's best result.
CONVERGENCE = re.compile(
    r"that stands\b|conclusion (?:survives|stands|held)|instinct (?:survives|stands|held)|"
    r"branches converged|converged on|convergence finding|survived attack from all|"
    r"all (?:three|four|five|3|4|5) branches (?:agreed|arrived|converged)",
    re.I,
)
# SKILL.md:69 opening sentence of META and COMMIT.
WITHOUT_BRANCHING = re.compile(r"without branching,? I would have said", re.I)

# -------------------------------------------------------------------------------------------------
# TIER-2 PRECURSOR — the OBJECT-LEVEL occasion, taken from FBC's own frontmatter
# -------------------------------------------------------------------------------------------------
# SKILL.md frontmatter, verbatim: "especially valuable for design decisions, research framing,
# statistical choices, and any question where motivated reasoning or anchoring is a real risk",
# and CLAUDE.md: "Default to Frame-Before-Commit on complex questions, design decisions, or
# anything that smells pre-answered."
#
# The detectable shadow of that occasion is a COMMITMENT being made on a DESIGN question with no
# alternatives generated. All three parts are required, and the third is a NEGATIVE condition,
# which is what keeps this from matching every turn in the corpus.
P_COMMITMENT = re.compile(
    r"\bI recommend\b|\bmy recommendation\b|\bthe right (?:call|approach|answer|move) is\b|"
    r"\bthe correct (?:approach|answer|design) is\b|\bwe should\b|\bthe answer is\b|"
    r"\bI'd go with\b|\bgo with\b|\bthe decision is\b", re.I)
P_DESIGN = re.compile(
    r"\bdesign\b|\barchitecture\b|\bapproach\b|\bprotocol\b|\bschema\b|\btrade-?off\b|"
    r"\bwhich (?:option|approach|one)\b|\bstructure\b|\bstrategy\b", re.I)
P_ALTERNATIVES = re.compile(
    r"\boption\s*(?:a\b|b\b|1\b|2\b)|\balternativ|\btwo options\b|\bthree options\b|"
    r"\binstead we could\b|\bon the other hand\b|\bcounter(?:-|\s)?argument\b|"
    r"\[branch|\bB1\b|\bthe case against\b|\bversus\b|\bvs\.", re.I)

# =================================================================================================
# THE REGISTRY — this is the general part. One entry per skill.
# =================================================================================================
RECORDS = {
    "frame-before-commit": {
        "src": "skills/frame-before-commit/SKILL.md:69,74,267-292 (format + discipline rules)",
        "run_open": RUN_OPEN,
        "numeric_header": RUN_HEADER_NUMERIC,
        "template": TEMPLATE,
        "completion": COMMIT,
        "extras": True,
        "tier2": dict(role="A", commit=P_COMMITMENT, topic=P_DESIGN, absent=P_ALTERNATIVES),
    },
    "ground-before-stating": {
        "delegate": "scripts/audit/gbs_record.py",
        "note": "GBS's precursor registry is eight rules deep and lives there. Running it here "
                "would produce a second, divergent answer for the same skill.",
    },
}


def load_rows():
    """(rows, how, read) — the index, with its READ STATE, never just its rows.

    WHY THIS IS NOT JUST `CI.load_prior()`, AND THE INCIDENT THAT PUT IT HERE
    ---------------------------------------------------------------------------
    `corpus_index.load_prior` discards the whole file when the header's `schema` does not equal
    the CURRENT `SCHEMA_VERSION` constant, which is correct for it: mixing schemas silently is
    how an index starts lying about its own fields. But it means **an edit to the SCRIPT
    invalidates the DATA**. On 2026-08-06 that happened mid-run: a concurrent agent bumped
    `SCHEMA_VERSION` to `corpus-index-v2` in the working copy while the on-disk index was still
    `v1`, and this file went from 1,167 usable rows to 0 between two invocations with no change
    to the corpus and no error — the exact silent-divergence class the repo has been draining.

    The first patch here hand-rolled its own header parser. That was a THIRD copy of the same
    header logic (corpus_index, this, role_history), which is the duplication class the index
    exists to close — so the state machine now lives once, in `corpus_index.read_index`, and this
    calls it. Behaviour is unchanged where it was right: on a stale schema the rows are still
    returned, because the fields this file uses (`path, date, kind, venue, trunk, markers,
    completions, triggers_human`) are shaped identically across v1/v2. What changed is that the
    caller now receives the `IndexRead` and **cannot report a count without knowing it is
    degraded.** A stale read is UNKNOWN, and is labelled UNKNOWN in the report header.
    """
    read = CI.require_index("skill_record")
    if read.fresh:
        return read.rows, f"corpus_index.read_index — FRESH (schema {read.schema_expected})", read
    if read.status == CI.INDEX_ABSENT:
        return {}, f"NONE — {read.one_line()}", read
    # STALE / MALFORMED: rows exist and are field-compatible. Degrade KNOWINGLY and say so.
    return read.rows, (f"DEGRADED / {read.status} — index on disk declares "
                       f"`{read.schema_on_disk}`, corpus_index.py expects "
                       f"`{read.schema_expected}`; {read.n_rows_on_disk} rows read anyway. "
                       f"EVERY COUNT BELOW IS UNKNOWN, NOT MEASURED."), read


def _delta_payloads(text, limit=400):
    """[str] — the text following each `[DELTA:`, to the closing bracket or line end."""
    out = []
    for m in DELTA.finditer(text):
        tail = text[m.end(): m.end() + limit]
        end = tail.find("]")
        out.append((tail[:end] if end != -1 else tail.split("\n")[0]).strip())
    return out


def _merge_occurrences(pat, txt):
    """Occurrence count with the gbs_record merge rule: two hits within MERGE_CHARS are one."""
    n, last = 0, None
    for m in pat.finditer(txt):
        if last is not None and m.start() - last <= MERGE_CHARS:
            last = m.end()
            continue
        last = m.end()
        n += 1
    return n


def analyse_fbc(sp):
    """One file's FBC record from its turn spans. Pure function of `sp`; writes nothing."""
    seq = sp.get("__seq__", [])
    whole = "\n".join(t for _, t in seq)
    if not whole:
        return None

    n_open = len(RUN_OPEN.findall(whole))
    n_numeric = len(RUN_HEADER_NUMERIC.findall(whole))
    template_only = bool(TEMPLATE.search(whole)) and n_numeric == 0

    payloads = _delta_payloads(whole)
    empty = [d for d in payloads if DELTA_EMPTY.search(d) or len(d) < 25]
    rest = [d for d in payloads if d not in empty]
    miscredit = [d for d in rest if DELTA_MISCREDIT.search(d)]
    branched = [d for d in rest if d not in miscredit and DELTA_BRANCHED.search(d)]
    unattributed = [d for d in rest if d not in miscredit and d not in branched]
    cosmetic_lex = [d for d in branched if DELTA_COSMETIC_LEX.search(d)]

    completed = bool(COMMIT.search(whole))
    # THREE ARMS, AND THE THIRD WAS ADDED BECAUSE THE FIRST TWO MISSED THE FLAGSHIP RUN.
    # `chat-2026-07-18-a8bbda` is the run B-8 s9.4 built its central finding on. It carries
    # [META], [COMMIT], three branch-credited deltas and the mandated opening sentence -- and
    # NEITHER `[FRAME-BEFORE-COMMIT` NOR `[BRANCH REGISTRY]`. So `corpus_index` scores it as
    # not-a-use at all (`markers` empty) and a header/registry test scores it as not-a-run.
    # **The most consequential run in the record is invisible to the marker registry.** That is
    # a finding about the protocol's own compliance, not only about the detector: SKILL.md:69
    # mandates both literals. The third arm is the completion shape itself -- a [COMMIT] carrying
    # the required opening sentence "Without branching, I would have said" -- which no template
    # and no passing mention produces.
    wb = bool(WITHOUT_BRANCHING.search(whole))
    genuine = (n_numeric > 0
               or (BRANCH_REGISTRY.search(whole) is not None and not template_only)
               or (completed and wb))

    return {
        "run_open_hits": n_open,
        "numeric_header": n_numeric,
        "template_present": bool(TEMPLATE.search(whole)),
        "template_only": template_only,
        "genuine_run": genuine,
        "registry": bool(BRANCH_REGISTRY.search(whole)),
        "meta": bool(META.search(whole)),
        "commit": completed,
        "n_deltas": len(payloads),
        "deltas": payloads,
        "d_empty": len(empty),
        "d_miscredit": len(miscredit),
        "d_branched": len(branched),
        "d_unattributed": len(unattributed),
        "d_cosmetic_lex": len(cosmetic_lex),
        "zero_delta_completed": genuine and completed and (len(payloads) - len(empty)) == 0,
        "convergence": bool(CONVERGENCE.search(whole)),
        "without_branching": wb,
        "header_compliant": n_numeric > 0,
    }


def tier2_hits(sp, spec):
    """Object-level precursor occurrences: a commitment on a design question, no alternatives."""
    n = 0
    for role, txt in sp.get("__seq__", []):
        if role != spec["role"]:
            continue
        for m in spec["commit"].finditer(txt):
            w = txt[max(0, m.start() - 400): m.end() + 400]
            if not spec["topic"].search(w):
                continue
            if spec["absent"].search(w):
                continue
            n += 1
            break                      # one occasion per turn; turns are the unit, not sentences
    return n


def scan(rows, slug, max_files=None, want_tier2=True):
    spec = RECORDS[slug]
    recs = []
    paths = sorted(rows)
    if max_files:
        paths = paths[:max_files]
    for rel in paths:
        p = REPO / rel
        if not p.is_file():
            continue
        row = rows[rel]
        sp = spans(p)
        if not sp:
            continue
        a = analyse_fbc(sp)
        if a is None:
            continue
        a.update(path=rel, date=row.get("date", "UNKNOWN"), kind=row.get("kind"),
                 venue=row.get("venue"), trunk=row.get("trunk"),
                 in_index_markers=slug in row.get("markers", []),
                 trigger_human=slug in row.get("triggers_human", []),
                 reemission=bool(REEMISSION.search(rel)),
                 self_audit=bool(SELF_AUDIT.search(rel)),
                 fanout=bool(FANOUT.search(rel)),
                 # KEYED ON (parent session, date), NOT parent alone. Session `da51cc`
                 # dispatched TWO separate fan-outs — 2026-07-13 (7 files) and 2026-07-16
                 # (5 files). Keying on the parent id alone merged them into one run and
                 # under-counted by one, which is the same error as over-counting, in the
                 # opposite direction.
                 fanout_parent=(FANOUT_PARENT.search(rel).group(1) + "@"
                                + str(row.get("date", "UNKNOWN"))
                                if FANOUT.search(rel) and FANOUT_PARENT.search(rel) else None))
        a["tier2"] = (tier2_hits(sp, spec["tier2"])
                      if (want_tier2 and spec.get("tier2") and not a["genuine_run"]) else 0)
        recs.append(a)
    return recs


def _dedupe(deltas):
    """Distinct delta ASSERTIONS. B-8 s9.1: one delta was found re-quoted across five files."""
    seen = set()
    for d in deltas:
        k = hashlib.sha1(re.sub(r"\s+", " ", d.lower()).strip().encode()).hexdigest()
        seen.add(k)
    return len(seen)


def report(recs, rows, slug, limit=15, show_anu=False, show_deltas=False, how="?", read=None):
    N = len(recs)
    # A degraded read must be visible at the TOP of the report, not buried in a `how` string
    # halfway down it. The failure mode being closed is a reader who scrolls to the counts.
    if read is not None and not read.fresh:
        print(read.banner("skill_record"))
        print("*** EVERY NUMBER IN THIS REPORT IS **UNKNOWN**, NOT MEASURED — the index and this")
        print("*** code disagree about row shape. Rebuild before quoting anything below.")
    q = CI.three_class(sorted(rows.values(), key=lambda r: r["path"]), slug, CI.load_skills())
    ci_used, ci_partial = q["USED"], (q["PARTIAL"] or [])
    ci_anu = q["APPLICABLE_NOT_USED"] or []

    marker = [r for r in recs if r["in_index_markers"]]
    genuine = [r for r in recs if r["genuine_run"]]
    tmpl_only = [r for r in recs if r["in_index_markers"] and r["template_only"]]
    complete = [r for r in genuine if r["commit"]]
    partial = [r for r in genuine if not r["commit"]]

    all_deltas = [d for r in recs for d in r["deltas"]]
    distinct = _dedupe(all_deltas)

    print()
    print("=" * 88)
    print(f"ACCUMULATED SESSION RECORD — {slug}")
    print("=" * 88)
    print("--- DENOMINATORS (in the output, not the docstring) --------------------------")
    print(f"  corpus root                       : {CI.CORPUS}  (== coverage_gap.CORPUS)")
    print(f"  transcripts in corpus_index       : {len(rows)}")
    print(f"  index read via                    : {how}")
    print(f"  transcripts re-read here          : {N}")
    print(f"  skill's declared marker source    : {RECORDS[slug]['src']}")
    print()
    print("--- corpus_index.three_class, AS IT REPORTS ----------------------------------")
    print(f"  USED                {len(ci_used):>5}   marker string present anywhere in the file")
    print(f"  PARTIAL             {len(ci_partial):>5}   marker present, no [COMMIT]")
    print(f"  APPLICABLE_NOT_USED {len(ci_anu):>5}   trigger phrase in JON'S turns, no marker")
    ov = len(set(ci_used) & set(ci_partial))
    print(f"  ** PARTIAL is a SUBSET of USED: overlap = {ov} of {len(ci_partial)}. **")
    print("     Those two numbers are not a ratio between classes. Disjointly, below.")
    print()
    print("--- THIS FILE, DISJOINT AND DEFLATED -----------------------------------------")
    print(f"  files carrying the marker         : {len(marker)}")
    print(f"    of which TEMPLATE/DOC only      : {len(tmpl_only)}   "
          f"(`{{N}} branches`, `label: TBD`, `[DELTA: Bn (LABEL)`) -- NOT runs")
    print(f"  files with a GENUINE run shape    : {len(genuine)}   "
          f"(numeric branch count or a real [BRANCH REGISTRY])")
    print(f"    COMPLETE  (reached [COMMIT])    : {len(complete)}")
    print(f"    PARTIAL   ('kinda did')         : {len(partial)}   started, never committed")
    print(f"  files with NEITHER                : {N - len(marker)}")
    print()
    print("--- DELTAS: HITS vs DISTINCT ASSERTIONS --------------------------------------")
    print(f"  [DELTA: occurrences (raw hits)    : {len(all_deltas)}")
    print(f"  DISTINCT after dedupe on text     : {distinct}   "
          f"(deflator {len(all_deltas) - distinct} = re-quotes across files)")
    print(f"  EMPTY (template left in output)   : {sum(r['d_empty'] for r in recs)}")
    print(f"  MISCREDITED (source is not a branch): {sum(r['d_miscredit'] for r in recs)}")
    print(f"  credited to a branch id           : {sum(r['d_branched'] for r in recs)}")
    print(f"  credited to nothing identifiable  : {sum(r['d_unattributed'] for r in recs)}")
    print(f"  of the branch-credited, LEXICALLY cosmetic: "
          f"{sum(r['d_cosmetic_lex'] for r in recs)}   ** LOWER BOUND **")
    print("  REAL vs COSMETIC                  : UNKNOWN — needs a cold grader.")
    print("     Whether an outcome changed is a judgment, not a string. B-8's Revised")
    print("     Improvement 2 asks for exactly this grader; it has not been run.")
    print()
    print("--- THE FAILURE THE PROTOCOL CANNOT SCORE ------------------------------------")
    zd = [r for r in genuine if r["zero_delta_completed"]]
    cv = [r for r in genuine if r["convergence"]]
    zc = [r for r in zd if r["convergence"]]
    print(f"  runs that COMPLETED with zero non-empty deltas : {len(zd)} of {len(complete)} complete")
    print(f"  runs whose text SCORES convergence             : {len(cv)} of {len(genuine)}")
    print(f"  both at once (zero delta AND convergence named): {len(zc)}")
    print("  Discipline Rule 7 blesses honest convergence; Self-Scoring calls zero deltas a")
    print("  red flag. A run in the last row satisfies both readings, so no instrument the")
    print("  protocol carries can call it a failure. That is the structural finding, counted.")
    print()
    print("--- WHEN (genuine runs, by month) --------------------------------------------")
    orig = [r for r in genuine if not r["reemission"] and not r["self_audit"]]
    hist = Counter(r["date"][:7] for r in genuine if r["date"] != "UNKNOWN")
    ohist = Counter(r["date"][:7] for r in orig if r["date"] != "UNKNOWN")
    print(f"  {'month':<9} {'run-shaped':>11} {'ORIGINAL':>9}   (original = minus re-emissions "
          f"and minus this audit's own agents)")
    for k in sorted(set(hist) | set(ohist)):
        print(f"  {k:<9} {hist[k]:>11} {ohist[k]:>9}  {'#' * min(ohist[k], 40)}")
    print(f"  re-emissions excluded            : {sum(1 for r in genuine if r['reemission'])}")
    print(f"  THIS AUDIT'S OWN AGENTS excluded : {sum(1 for r in genuine if r['self_audit'])}   "
          f"** an audit of FBC emits FBC markers; B-8 s9.2 caught this and so must this file **")
    # FAN-OUT, NEW 2026-08-07. Printed as its own row because it is a DIFFERENT deflator from the
    # two above: a branch agent is real FBC work, so deleting it would be wrong, but counting each
    # of N branch agents as a separate RUN is the inflation. Runs, then members, both with the
    # denominator they came out of.
    fo = [r for r in genuine if r["fanout"]]
    fo_parents = sorted({r["fanout_parent"] for r in fo if r["fanout_parent"]})
    print(f"  FAN-OUT branch agents            : {len(fo)} files of {len(genuine)} run-shaped, "
          f"belonging to {len(fo_parents)} parent session(s) -> {len(fo_parents)} RUNS, not "
          f"{len(fo)}")
    if fo_parents:
        print(f"    parent sessions                : {', '.join(fo_parents)}")
    print(f"  RUN-SHAPED FILES {len(genuine)}  ->  DISTINCT RUNS "
          f"{len(genuine) - len(fo) + len(fo_parents)}   "
          f"(each fan-out family collapsed to one)")
    last = max((r["date"] for r in orig if r["date"] != "UNKNOWN"), default="UNKNOWN")
    print(f"  LAST ORIGINAL RUN                : {last}")
    print()
    print("--- PROTOCOL COMPLIANCE OF THE RUNS THEMSELVES -------------------------------")
    print(f"  original runs                     : {len(orig)}")
    print(f"    with the mandated numeric header: {sum(1 for r in orig if r['header_compliant'])}")
    print(f"    with [BRANCH REGISTRY]          : {sum(1 for r in orig if r['registry'])}")
    print(f"    with [META]                     : {sum(1 for r in orig if r['meta'])}")
    print(f"    with [COMMIT]                   : {sum(1 for r in orig if r['commit'])}")
    print(f"    INVISIBLE to corpus_index's marker registry: "
          f"{sum(1 for r in orig if not r['in_index_markers'])}")
    print("  SKILL.md:69 mandates both the header and the registry. A run missing both is")
    print("  undetectable by any marker-presence instrument, including this one's first two")
    print("  arms. The flagship 2026-07-18 run is in that set.")
    print()
    print("--- APPLICABLE-NOT-USED, TWO TIERS -------------------------------------------")
    print(f"  TIER 1 (corpus_index): {len(ci_anu)}   Jon typed a declared trigger, no marker")
    t1_recent = [p for p in ci_anu if re.search(r"2026-0[78]", p)]
    print(f"     of those dated 2026-07 or later (by filename): {len(t1_recent)}")
    t2 = [r for r in recs if r["tier2"] > 0]
    print(f"  TIER 2 (object-level): {len(t2)} files, "
          f"{sum(r['tier2'] for r in t2)} occasions")
    print("     a commitment made on a design question with no alternatives in the window,")
    print("     in a file with no genuine run. FBC's own frontmatter names this occasion:")
    print("     'especially valuable for design decisions ... where motivated reasoning or")
    print("     anchoring is a real risk'. THIS OVER-COUNTS and is a CANDIDATE list.")
    t2h = Counter(r["date"][:7] for r in t2 if r["date"] != "UNKNOWN")
    print("     by month: " + ", ".join(f"{k}={t2h[k]}" for k in sorted(t2h)))
    print()

    if show_anu:
        print("--- TIER 1 ENUMERATED (all of them; this is the whole class) ------------------")
        for p in sorted(ci_anu):
            r = next((x for x in recs if x["path"] == p), None)
            d = r["date"] if r else "?"
            print(f"  {d}  {p}")
        print()
        print("--- TIER 2, top files by occasions -------------------------------------------")
        for r in sorted(t2, key=lambda r: -r["tier2"])[:limit]:
            print(f"  {r['tier2']:>3}x  {r['date']}  {r['path']}")
        print()

    if show_deltas:
        print("--- DELTA PAYLOAD SAMPLES BY MECHANICAL CLASS --------------------------------")
        for label, test in (("EMPTY", lambda d: DELTA_EMPTY.search(d) or len(d) < 25),
                            ("MISCREDITED", DELTA_MISCREDIT.search),
                            ("COSMETIC (lexical lower bound)", DELTA_COSMETIC_LEX.search)):
            print(f"  [{label}]")
            shown = 0
            for r in recs:
                for d in r["deltas"]:
                    if test(d) and shown < limit:
                        print(f"    {r['date']}  {d[:150]}")
                        shown += 1
            print()

    print("--- WHAT WOULD MAKE THIS RECORD LIE ------------------------------------------")
    print("  1. PRESENCE IS NOT USE. Every count is over strings. A run pasted into a brief,")
    print("     a wiki page quoting a COMMIT, and a real execution are the same bytes.")
    print("  2. THE TEMPLATE DEFLATOR IS LEXICAL. It catches `{N} branches` and `label: TBD`.")
    print("     A brief that paraphrases the format without those literals still counts.")
    print("  3. TIER 2 IS A PROXY FOR A JUDGMENT. 'A design decision was made without")
    print("     alternatives' is not a string. The negative condition (no alternatives in a")
    print("     +/-400 char window) is the whole guard, and a window is not a document.")
    print("  4. REAL vs COSMETIC IS NOT COMPUTED. It is printed UNKNOWN. Any reader who")
    print("     collapses 'branch-credited' into 'real' has done the thing this file refuses.")
    print("  5. DATES COME FROM FILENAMES. A re-quote carries the QUOTING file's date, which")
    print("     is why the month histogram is over GENUINE runs only and still over-reports")
    print("     recent months.")
    print()


def self_test():
    ok = True

    def chk(label, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")

    print("=== SELF-TEST — skill_record (negative controls first) ===")

    # STALE-SCHEMA POSTURE — the 2026-08-06 silent-zero, tested in both directions.
    # A temp index; the real one is never touched.
    import tempfile
    with tempfile.TemporaryDirectory() as _td:
        _p = Path(_td) / "idx.jsonl"

        def _at(schema, n=3):
            hdr = "#" + json.dumps({"schema": schema, "rows": n}) + "\n"
            _p.write_text(hdr + "".join(
                json.dumps({"path": f"a/{i}.md", "markers": [], "completions": [],
                            "triggers_human": [], "kind": "session", "venue": "claude-ai",
                            "trunk": "fl", "date": "2026-01-01"}) + "\n" for i in range(n)),
                encoding="utf-8")
            return CI.require_index("self-test", _p, stream=io.StringIO())

        _fresh = _at(CI.SCHEMA_VERSION)
        _stale = _at("corpus-index-v0")
        chk("temp FRESH index reads FRESH", _fresh.status == CI.INDEX_FRESH)
        chk("temp STALE index reads STALE_SCHEMA, not ABSENT", _stale.status == CI.INDEX_STALE)
        chk("STALE read still yields 3 usable rows here (fields are v1/v2-compatible)",
            len(_stale.rows) == 3 and _stale.n_rows_on_disk == 3)
        chk("STALE read is NOT reported as fresh", not _stale.fresh)
        chk("STALE banner says UNKNOWN (so the report cannot print a bare count)",
            "UNKNOWN" in _stale.banner("skill_record"))
        chk("FRESH banner is empty — no false alarm on the happy path",
            _fresh.banner("skill_record") == "")
        _missing = CI.read_index(Path(_td) / "nope.jsonl")
        chk("a genuinely absent index is ABSENT with 0 rows, distinct from STALE",
            _missing.status == CI.INDEX_ABSENT and _missing.n_rows_on_disk == 0)

    A = lambda t: analyse_fbc({"__seq__": [("A", t)]})

    # NEGATIVE CONTROL — the direction that matters is the one that INFLATES.
    chk("plain prose is not a run and carries no deltas",
        (lambda a: not a["genuine_run"] and a["n_deltas"] == 0)(A("We shipped the page today.")))
    # THE TEMPLATE DEFLATOR — the single largest inflator B-8 measured (66 of 245).
    chk("the SKILL.md template header is NOT a genuine run",
        not A("[FRAME-BEFORE-COMMIT - PURE - {N} branches]\nB1 | label: TBD")["genuine_run"])
    chk("a numeric header IS a genuine run",
        A("[FRAME-BEFORE-COMMIT - PURE - 4 branches]")["genuine_run"])
    chk("a real [BRANCH REGISTRY] with no template literals IS a genuine run",
        A("[BRANCH REGISTRY]\nB1 | label: STRUCTURAL")["genuine_run"])
    # THE THIRD ARM — added because arms 1 and 2 missed the flagship run entirely.
    chk("a run with NO header and NO registry but a compliant [COMMIT] IS a genuine run",
        A("[META] ...\n[COMMIT]\nWithout branching, I would have said: NO-GO."
          )["genuine_run"])
    chk("a bare [COMMIT] with no opening sentence is NOT promoted to a run",
        not A("[COMMIT] we shipped it.")["genuine_run"])
    # DEFLATOR CONTROLS — path facts, and both must be able to say no.
    chk("an extraction subagent path is flagged as a re-emission",
        bool(REEMISSION.search("raw/transcripts/claude-code/subagents/6a2c31/"
                               "code-2026-07-21-a5c013-explore-extract-project-manager.md")))
    chk("an ordinary session path is NOT flagged as a re-emission",
        not REEMISSION.search("raw/transcripts/claude-ai/fl/project-manager/"
                              "project-manager-2026-04-30-f8cc02.md"))
    chk("this audit's own agent is flagged as self-contamination",
        bool(SELF_AUDIT.search("subagents/f01909/code-2026-08-06-a82ba7-explore-"
                               "search-corpus-for-real-fbc-runs.md")))
    chk("an unrelated 2026-08-06 session is NOT flagged as self-contamination",
        not SELF_AUDIT.search("raw/transcripts/claude-code/code-2026-08-06-"
                              "a69f31-fix-claude-code-settings-hook-configuration.md"))
    # THE TWO-CHARACTER MISSES, 2026-08-07. Each of these returned False before the repair and
    # each was a file the deflator was WRITTEN to catch — the ticket's own record page and the
    # FBC twin of a GBS agent named in the same pattern. Regression tests, not decoration.
    chk("B-8's OWN record page is self-contamination "
        "(`b-8-improve` did not match `B-8-improving`: improve ends -v-e, improving -v-i-n-g)",
        bool(SELF_AUDIT.search("wiki/intake-triage/B-8-improving-fbc-and-gbs-2026-08-06.md")))
    chk("`fbc-and-gbs` is caught (`fbc.?gbs` spans ONE char; `-and-` is five)",
        bool(SELF_AUDIT.search("some-note-about-fbc-and-gbs.md")))
    chk("the FBC record-page agent is caught, as its GBS twin already was",
        bool(SELF_AUDIT.search("subagents/f01909/code-2026-08-06-a8c9fb-general-purpose-"
                               "fbc-skill-session-record-1-second.md")))
    chk("the GBS twin STILL matches — the repair is additive, nothing was traded away",
        bool(SELF_AUDIT.search("subagents/f01909/code-2026-08-06-a0654d-general-purpose-"
                               "gbs-skill-session-record-1-first-p.md")))
    chk("an agent that AUDITS the GBS triggers is self-contamination",
        bool(SELF_AUDIT.search("code-2026-08-06-a68808-skills-executor-g-unit-1-"
                               "gbs-trigger-gap-audit.md")))
    chk("an ordinary session merely NAMING a frame is NOT self-contamination "
        "(the deflator must be able to say no)",
        not SELF_AUDIT.search("raw/transcripts/claude-ai/fl/chat-2026-07-18-a8bbda-"
                              "packet-a-go-no-go.md"))
    # FAN-OUT — a different class from self-audit, and the two must not collapse.
    chk("a numbered FBC branch agent is FAN-OUT",
        bool(FANOUT.search("code-2026-08-06-a70066-general-purpose-fbc-frame-1-economic.md")))
    chk("a LETTERED FBC branch agent is FAN-OUT",
        bool(FANOUT.search("code-2026-07-16-a9b53a-general-purpose-fbc-frame-a-resource-deadline.md")))
    chk("a TOPIC-named branch agent is FAN-OUT — the identifier is not always a digit or letter, "
        "and requiring one matched 0 of the 6 in the 2026-07-13 family",
        bool(FANOUT.search("code-2026-07-13-a6c14b-general-purpose-meta-fbc-frame-on-instinct.md")))
    chk("the cold synthesiser of a fan-out is FAN-OUT",
        bool(FANOUT.search("code-2026-08-06-a3cbee-general-purpose-cold-fbc-synthesis.md")))
    chk("a 2026-04-15 test-master CONDITION run is NOT fan-out — it is one whole run in one "
        "file, and deflating it would delete the cleanest runs in the record",
        not FANOUT.search("raw/transcripts/claude-ai/fl/fbc-pure-3branch-delta-capability/"
                          "fbc-pure-3branch-2026-04-15-d03c80.md"))
    chk("an ordinary session is NOT fan-out",
        not FANOUT.search("raw/transcripts/claude-code/fl/code-2026-05-23-ee177e-"
                          "skills-inventory-refresh.md"))
    chk("FAN-OUT and SELF_AUDIT are DISJOINT on the corpus — they are different defects and "
        "folding one into the other would hide it",
        not (FANOUT.search("code-2026-08-06-a70066-general-purpose-fbc-frame-1-economic.md")
             and SELF_AUDIT.search("code-2026-08-06-a70066-general-purpose-fbc-frame-1-economic.md")))
    # DELTA CLASSES — each must fire, and must not fire on the others.
    chk("the delta TEMPLATE line classifies EMPTY, not real",
        A("[DELTA: Bn (LABEL) - Without this branch, commit would have said: X. With it, "
          "commit says: Y instead.]")["d_empty"] == 1)
    chk("a trailing-off delta classifies EMPTY",
        A("[DELTA: B2 (ADVERSARIAL) changed the committed answer by: ...]")["d_empty"] == 1)
    chk("a Jon-caused delta classifies MISCREDITED, not branch-credited",
        (lambda a: a["d_miscredit"] == 1 and a["d_branched"] == 0)(
            A("[DELTA: your messages - I dropped the registry claim.]")))
    chk("a branch-credited concrete delta is branch-credited and NOT empty",
        (lambda a: a["d_branched"] == 1 and a["d_empty"] == 0)(
            A("[DELTA: B2 (STRUCTURAL) - Without: two files. With: three files, "
              "confound named.]")))
    chk("a presentation-only delta trips the COSMETIC lower bound",
        A("[DELTA: B5 (EPISTEMIC) - it gave the commit its closing frame, conclusion "
          "unchanged.]")["d_cosmetic_lex"] == 1)
    # THE STRUCTURAL FINDING must be computable in both directions.
    chk("a completed run with only an EMPTY delta counts as ZERO-delta",
        A("[FRAME-BEFORE-COMMIT - PURE - 3 branches]\n[COMMIT]\n"
          "[DELTA: Bn (LABEL) - without it, X; with it, Y]")["zero_delta_completed"])
    chk("a completed run with a real delta does NOT count as zero-delta",
        not A("[FRAME-BEFORE-COMMIT - PURE - 3 branches]\n[COMMIT]\n"
              "[DELTA: B2 (ADVERSARIAL) - Without: ship now. With: gate first.]"
              )["zero_delta_completed"])
    chk("the flagship 2026-07-18 COMMIT shape is detected as convergence",
        A("Without branching, I would have said: NO-GO until Packet A. With branching, "
          "that stands, amended four ways.")["convergence"])
    # TIER 2 — the negative condition is the whole guard, so it must actually guard.
    t2 = lambda t: tier2_hits({"__seq__": [("A", t)]}, RECORDS["frame-before-commit"]["tier2"])
    chk("a bare commitment with no design topic does not fire",
        t2("I recommend the blue one.") == 0)
    chk("a commitment on a design question with no alternatives DOES fire",
        t2("I recommend we should adopt this schema for the packet design.") == 1)
    chk("the same commitment WITH alternatives present does NOT fire",
        t2("I recommend this schema for the packet design, though the alternative "
           "is a flat file.") == 0)
    chk("a commitment in JON's turn does not fire (the precursor is an ASSISTANT act)",
        tier2_hits({"__seq__": [("H", "I recommend we should adopt this schema design.")]},
                   RECORDS["frame-before-commit"]["tier2"]) == 0)
    chk("a commitment in a DISPATCH turn does not fire — an agent brief is not Jon",
        tier2_hits({"__seq__": [("D", "I recommend we should adopt this schema design.")]},
                   RECORDS["frame-before-commit"]["tier2"]) == 0)
    # DEDUPE — B-8 measured one delta re-quoted across five files.
    chk("five verbatim re-quotes of one delta dedupe to one assertion",
        _dedupe(["[B2] without X with Y"] * 5) == 1)
    chk("two genuinely different deltas do not dedupe",
        _dedupe(["without X with Y", "without P with Q"]) == 2)
    # REUSE, not redefinition.
    chk("CORPUS resolves transitively to coverage_gap's, via corpus_index",
        CI.CORPUS == __import__("coverage_gap").CORPUS)
    chk("turn-span splitter is gbs_record's, not a second copy", spans is GR.spans)
    chk("GBS is registered as a DELEGATE, never scanned twice",
        RECORDS["ground-before-stating"].get("delegate", "").endswith("gbs_record.py"))
    # raw/ UNTOUCHED — Jon's standing NO DESTRUCTIVE ACTS constraint, tested as a property.
    sample = [p for p, _ in CI.walk_corpus()][::97]
    before = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    rows, _how, _read = load_rows()
    scan(dict(list(rows.items())[:40]), "frame-before-commit")
    after = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    chk(f"a scan leaves raw/ byte- and mtime-identical ({len(sample)} sampled)", before == after)

    print("\nRESULT: " + ("PASS — controls fire in both directions." if ok
                          else "FAIL — do not trust its counts."))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skill", default="frame-before-commit")
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--max-files", type=int, default=None)
    ap.add_argument("--anu", action="store_true", help="enumerate applicable-not-used")
    ap.add_argument("--deltas", action="store_true", help="delta payload samples by class")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    spec = RECORDS.get(args.skill)
    if spec is None:
        print(f"[no record definition for `{args.skill}`] — this is NOT zero use. "
              f"Known: {', '.join(sorted(RECORDS))}", file=sys.stderr)
        return 0
    if spec.get("delegate"):
        print(f"`{args.skill}` is served by {spec['delegate']}. {spec['note']}")
        return 0

    rows, how, read = load_rows()
    if not rows:
        # `if not rows` alone CANNOT tell ABSENT from STALE — that conflation is the whole bug.
        # `read.status` and `read.n_rows_on_disk` are what separate them, so print both.
        print(f"[{read.status}] {read.one_line()}", file=sys.stderr)
        print(f"Records for `{args.skill}` = UNKNOWN, not zero. "
              f"Build/rebuild: python scripts/audit/corpus_index.py", file=sys.stderr)
        print("This is NOT a result. Nothing was scanned.", file=sys.stderr)
        return 0
    recs = scan(rows, args.skill, max_files=args.max_files)
    report(recs, rows, args.skill, limit=args.limit,
           show_anu=args.anu, show_deltas=args.deltas, how=how, read=read)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(0)
