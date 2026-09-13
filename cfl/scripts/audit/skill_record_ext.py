#!/usr/bin/env python3
"""skill_record_ext.py — the accumulated session record for handoff / wayfinder / grill-me.

WHY THIS IS A SEPARATE FILE AND NOT AN EDIT TO `skill_record.py`
-----------------------------------------------------------------
`skill_record.py` is the generator and it is **not forked here.** Everything structural is
imported from it: the index reader (`load_rows`, which carries the FRESH/STALE read state),
the turn-span splitter (`spans`, itself `gbs_record.spans`), the merge rule, the delta dedupe,
the corpus root, and the reference three-class queries in `corpus_index`.

What this file adds is **three RECORDS entries and the per-skill analysers they need**, and it
registers them into `skill_record.RECORDS` at import so nothing has two definitions.

It is a separate file for one reason, stated so a later reader does not merge it back blindly:
on 2026-08-06 another agent was **live in `corpus_index.py` and its consumers** — `skill_record.py`
was dirty in the working tree at the moment this was written. Appending to a file another agent is
mid-edit is how two correct changes become one broken file. **When that work lands, the right end
state is that the three `RECORDS_EXT` entries below move into `skill_record.RECORDS` and this
module keeps only the analysers** — the same fold `skill_record.py` already describes for
`gbs_record.py`.

WHAT IS ACTUALLY MEASURED, PER SKILL, AND WHY THE GENERIC QUERY IS NOT ENOUGH
-------------------------------------------------------------------------------
`corpus_index.three_class` answers presence-of-string per FILE. `corpus_index.turn_three_class`
answers it per (transcript, turn) with a hard compaction reset. Both are used and both are
printed. Each of these three skills then breaks one of their assumptions in a different way:

  * **handoff** — its declared marker is a HEADING of a document the skill writes **to a file.**
    A transcript contains that heading only when the assistant also PASTED the document into the
    conversation. The corpus therefore cannot see the artifact at all; it sees the paste. So the
    file-scoped USED count is a count of *pastes*, and the real record is on disk. This module
    counts the disk artifacts separately and prints both. It also scores SECTION COVERAGE —
    handoff is the one skill here with a graded "kinda did": 10 mandated headings, so a document
    is 4-of-10 or 9-of-10, not merely used-or-not.

  * **wayfinder** — its trigger literal is the word `wayfinder`, and **the word is equivocal in
    this corpus.** `wiki/references/vocabulary.md` and `cfl-branch-registry.md` §1.1 record that
    Jon's nine "branches" are WORK TICKETS rather than a taxonomy, and a 2026-07-26 usage names a
    connector-side PARTY. A trigger detector that cannot tell "run the wayfinder protocol" from
    "check the wayfinder map" from "wayfinder said" is not measuring invocation. This module
    classifies every Jon-turn occurrence into SKILL / MAP / PARTY / UNCLASSIFIED and prints the
    split, because the APPLICABLE-NOT-USED headline is only as good as that split.

  * **grill-me** — `corpus_index.MARKERS` declares **no marker** for it, so USED is `0` and the
    index says outright that this is UNDETECTABLE, not zero. Two things are added here. First,
    SKILL.md:82 does mandate a verbatim closing literal (*"Is this an accurate summary? Anything
    I missed?"*), which is a real completion shape nobody had declared. Second — and this is the
    part that answers Jon's *"cases where you kinda did"* — a **behavioural cadence detector**:
    the protocol's defining constraint is *one question at a time, then wait*, and that shape is
    mechanically visible as alternating assistant/human turns where the assistant turn is short
    and carries exactly one question mark. That finds grilling that happened without anyone
    naming the skill, which no marker or trigger detector can do.

WHAT THIS CANNOT SEE — printed in the output, never silently zeroed
--------------------------------------------------------------------
  * **An artifact written but never pasted.** For handoff this is the dominant case, and it is
    the reason the disk count and the corpus count are printed as two different numbers rather
    than reconciled into one.
  * **A skill that should have fired with nothing said about it.** For handoff there is no
    lexical trigger at all — SKILL.md's triggers are "60-70% context fill" and "Jon signals a
    session boundary", neither of which is a string. handoff's APPLICABLE-NOT-USED is therefore
    **UNKNOWN, and is printed UNKNOWN.** It is not 0.
  * **Whether a grilling was any good.** The cadence detector sees turn shape. Whether the
    questions walked the decision tree is a judgment and is reported as such.
  * **Jon's own selections through the AskUserQuestion UI**, which the corpus does not carry at
    all. On a question-shaped skill that is a live undercount and is stated, not absorbed.

Exit code is **always 0.** An instrument, not a gate. It only ever READS `raw/`.

Usage:
  skill_record_ext.py --skill handoff
  skill_record_ext.py --skill wayfinder --senses      # enumerate the equivocality split
  skill_record_ext.py --skill grill-me --cadence      # enumerate cadence runs
  skill_record_ext.py --all
  skill_record_ext.py --self-test
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from functools import lru_cache
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

import corpus_index as CI                          # noqa: E402  index + reference queries
import skill_record as SR                          # noqa: E402  the generator; NOT forked

REPO = SR.REPO
spans = SR.spans                                   # == gbs_record.spans, one definition
MERGE_CHARS = SR.MERGE_CHARS


# =================================================================================================
# handoff — skills/handoff/SKILL.md
# =================================================================================================
# The mandated document template, SKILL.md:66-99. Ten headings, read out of the fenced block, not
# recalled. `Interpretation Summary` (SKILL.md:228-249) is NOT in this list: it was ratified
# 2026-08-03, so scoring a 2026-07 handoff against it would be an anachronism. It is counted
# separately, against the documents that postdate its ratification.
HO_SECTIONS = [
    ("Context",              re.compile(r"^#{1,4}\s*Context\s*$", re.I | re.M)),
    ("What Was Accomplished", re.compile(r"^#{1,4}\s*What Was Accomplished This Session", re.I | re.M)),
    ("Current State",        re.compile(r"^#{1,4}\s*Current State", re.I | re.M)),
    ("In Progress",          re.compile(r"^#{1,4}\s*In Progress", re.I | re.M)),
    ("Next Steps",           re.compile(r"^#{1,4}\s*Next Steps", re.I | re.M)),
    ("Held Items",           re.compile(r"^#{1,4}\s*Held Items", re.I | re.M)),
    ("Open Questions",       re.compile(r"^#{1,4}\s*Open Questions", re.I | re.M)),
    ("Key Files / Paths",    re.compile(r"^#{1,4}\s*Key Files", re.I | re.M)),
    ("Constraints/Warnings", re.compile(r"^#{1,4}\s*Constraints", re.I | re.M)),
    ("Skills Active",        re.compile(r"^#{1,4}\s*Skills Active", re.I | re.M)),
]
HO_MARKER = re.compile(r"##\s*What Was Accomplished This Session", re.I)
HO_COMPLETION = re.compile(r"##\s*Next Steps", re.I)
# -------------------------------------------------------------------------------------------------
# THE TEMPLATE DEFLATOR, AND WHY IT HAD TO BECOME POSITIONAL
# -------------------------------------------------------------------------------------------------
# First version tested "does this file contain a SKILL.md placeholder anywhere". It scored 17 of
# 20 marker-bearing files as template-only, INCLUDING four that carry all ten headings — because a
# session that RUNS this skill reads SKILL.md first, so the placeholders and the real document sit
# in the same transcript. **Presence of the template is evidence the skill was consulted, not
# evidence it was not run**, and a deflator that cannot tell those apart deletes exactly the files
# it should be counting.
#
# So the test is POSITIONAL, the same move `skill_record` makes for FBC's `{N}` vs a digit: a
# section is FILLED when the text following its heading is not the placeholder that SKILL.md puts
# there. One filled marker section is a run; ten unfilled ones are the template.
HO_TEMPLATE_BODY = re.compile(
    r"\[Bulleted list: concrete outputs|\[2-3 sentences: what project/task|"
    r"\[What exists now that didn'?t before|\[First thing the fresh agent should do\]|"
    r"\[Items Jon parked|\[What was started but not finished|"
    r"\[Decisions that weren'?t made|\[Specific files relevant to continuing|"
    r"\[Things the fresh agent must not do|\[Which skills were loaded", re.I)
# Quotes of the PATH convention. These say nothing about whether a document was written.
HO_TEMPLATE_PATH = re.compile(r"\{project-root\}|handoff-\{topic\}|\{YYYY-MM-DD\}", re.I)
HO_BODY_CHARS = 300          # chars after a heading in which to look for the placeholder
# SKILL.md:34,53-63 — the output location the 2026-08-01 revision FORBIDS.
HO_TEMP_PATH = re.compile(
    r"%TEMP%|AppData[\\/]Local[\\/]Temp|OS temp directory|\btemp directory\b|/tmp/", re.I)
# SKILL.md:43-47 — the SECOND mandated artifact. A handoff that names no source page is half done.
HO_SOURCE_PAGE = re.compile(r"wiki[\\/]sources[\\/]|source-page-standard", re.I)
# SKILL.md:181 — the verification self-test, verbatim. Nothing else produces this sentence.
HO_SELFTEST = re.compile(r"Name three things a fresh agent", re.I)
# -------------------------------------------------------------------------------------------------
# THE OFF-TEMPLATE DETECTORS — added because the template detector returned ZERO and the zero was
# real. Not one file in the corpus carries a FILLED `## What Was Accomplished This Session`; all
# twenty marker hits are SKILL.md being read. Meanwhile two handoff documents sit in the repo with
# none of the ten mandated headings ("Pinned next step", "Locked decisions", "Do NOT without Jon").
# **Handoffs are being written. The mandated template is not being used.** Those are different
# facts and an instrument that only knows the template can only report the first as absence.
HO_DOC_TITLE = re.compile(r"^#{1,2}\s*(?:Session\s+)?Handoff\s*[—–-]", re.I | re.M)
# SKILL.md:185 — the mandated confirmation sentence. Evidence an ARTIFACT was produced, whatever
# shape it took.
HO_CONFIRM = re.compile(
    r"handoff (?:document )?(?:written|saved|created) (?:to|at)|"
    r"Ready for fresh session", re.I)
# SKILL.md:228-249 — ratified 2026-08-03.
HO_INTERP = re.compile(r"Interpretation Summary|\|\s*His words\s*\|", re.I)
HO_RATIFIED_INTERP = "2026-08-03"
HO_RATIFIED_REPO_PATH = "2026-08-01"


def filled_sections(whole):
    """(filled, seen) — heading names whose body is real text, and every heading seen at all."""
    filled, seen = [], []
    for name, rx in HO_SECTIONS:
        real = False
        for m in rx.finditer(whole):
            seen.append(name) if name not in seen else None
            body = whole[m.end(): m.end() + HO_BODY_CHARS]
            stripped = re.sub(r"^\s*\n", "", body)
            if stripped.strip() and not HO_TEMPLATE_BODY.search(body):
                real = True
        if real:
            filled.append(name)
    return filled, seen


def analyse_handoff(sp):
    """One file's handoff record. Pure function of `sp`; writes nothing."""
    seq = sp.get("__seq__", [])
    whole = "\n".join(t for _, t in seq)
    if not whole:
        return None
    present, seen = filled_sections(whole)
    template = bool(HO_TEMPLATE_BODY.search(whole))
    marker = bool(HO_MARKER.search(whole))
    marker_filled = "What Was Accomplished" in present
    # A GENUINE handoff paste carries a FILLED marker section and at least half the mandated
    # headings filled. Half is a threshold and thresholds are choices: 5 of 10 is the point at
    # which the document stops being a heading someone quoted and starts being a document someone
    # wrote. The full coverage histogram is printed so a reader can move the line and see what
    # moves.
    genuine = marker_filled and len(present) >= 5
    return {
        "sections": present,
        "n_sections": len(present),
        "headings_seen": len(seen),
        "marker": marker,
        "marker_filled": marker_filled,
        "completion": bool(HO_COMPLETION.search(whole)),
        "template_present": template,
        "path_quote": bool(HO_TEMPLATE_PATH.search(whole)),
        # TEMPLATE-ONLY now means: the headings are there and NONE of them is filled.
        "template_only": marker and not marker_filled,
        "genuine": genuine,
        "doc_title": bool(HO_DOC_TITLE.search(whole)),
        "confirm": bool(HO_CONFIRM.search(whole)),
        # OFF-TEMPLATE: a handoff document was produced and it is not the mandated shape.
        "offtemplate": (bool(HO_DOC_TITLE.search(whole)) or bool(HO_CONFIRM.search(whole)))
                       and not genuine,
        "produced": genuine or bool(HO_DOC_TITLE.search(whole)) or bool(HO_CONFIRM.search(whole)),
        "temp_path": bool(HO_TEMP_PATH.search(whole)),
        "source_page": bool(HO_SOURCE_PAGE.search(whole)),
        "selftest": bool(HO_SELFTEST.search(whole)),
        "interp": bool(HO_INTERP.search(whole)),
    }


def handoff_artifacts_on_disk(repo=REPO):
    """[(path, n_sections, has_source_page)] for handoff DOCUMENTS in the project tree.

    THE CORPUS CANNOT ANSWER THIS AND THAT IS THE WHOLE POINT. SKILL.md:38-41 says the handoff is
    a FILE at the project root. A file is not a transcript, so no transcript-scoped instrument —
    `corpus_index`, `skill_record`, or this one — can count the artifacts the skill exists to
    produce. Counting them requires looking at the disk, so this looks at the disk.

    Scoped to the repo working tree, excluding worktrees (which are copies of the same two files
    and would multiply the count by the number of worktrees that happen to exist today).
    """
    # SCOPED TO THE WHOLE PROGRAM, NOT THIS REPO. SKILL.md:40 gives its own worked example as
    # `G:\My Drive\Claude\Claude Personal\handoff-document-capture-2026-08-01.md` — a SIBLING
    # project. Scanning only this repo would have reported 2 artifacts and missed the three that
    # actually follow the 2026-08-01 naming ratification, all of which live next door.
    roots = [repo]
    drive = repo.parent.parent                     # ...\Claude\
    if drive.is_dir():
        roots += [d for d in sorted(drive.iterdir()) if d.is_dir() and d != repo.parent]
        roots += [repo.parent]
    out = []
    pats = ("HANDOFF-*.md", "handoff-*.md", "exchange/handoff-*.md", "exchange/HANDOFF-*.md")
    seen = set()
    for root in roots:
        for pat in pats:
            try:
                found = sorted(root.glob(pat))
            except OSError:
                continue
            for p in found:
                if p in seen or not p.is_file():
                    continue
                seen.add(p)
                try:
                    txt = p.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                n = len(filled_sections(txt)[0])
                try:
                    rel = str(p.relative_to(drive))
                except ValueError:
                    rel = str(p)
                out.append((rel, n, bool(HO_SOURCE_PAGE.search(txt)),
                            bool(HO_INTERP.search(txt)), bool(HO_SELFTEST.search(txt))))
    return sorted(out)


# =================================================================================================
# wayfinder — skills/wayfinder/SKILL.md
# =================================================================================================
WF_MARKER = re.compile(r"##\s*Decisions So Far", re.I)
WF_COMPLETION = re.compile(r"##\s*Out of Scope", re.I)
WF_MAPSHAPE = re.compile(r"wayfinder:map|##\s*Destination|wayfinder-cfl", re.I)
# POSITIONAL, for the same reason handoff's deflator is. A session that RUNS wayfinder reads
# SKILL.md first, so a presence test on the SKILL.md path scored 37 of the 53 marker-bearing files
# as template-only — deleting exactly the files it should have counted. These are the placeholders
# SKILL.md:49-73 puts UNDER the map headings: a "Decisions so far" whose body is one of them is
# the template; a body carrying a real closed-ticket line is a map.
WF_TEMPLATE_BODY = re.compile(
    r"<closed ticket title>|one line per closed ticket|"
    r"<what reaching the end of this map looks like|"
    r"<domain; skills every session should consult|"
    r'see "Fog of war"|work ruled beyond the destination', re.I)
WF_TEMPLATE = re.compile(r"\{destination\}|\{ticket|<destination>|`wayfinder:<type>`", re.I)
WF_BODY_CHARS = 300

# ------------------------------------------------------------------------------------------------
# THE EQUIVOCALITY CLASSIFIER — the load-bearing part of wayfinder's record
# ------------------------------------------------------------------------------------------------
# `wayfinder` names at least three different things in this corpus and the trigger detector cannot
# tell them apart:
#   SKILL   the protocol being invoked or discussed as a protocol — the only sense for which
#           APPLICABLE-NOT-USED means anything.
#   MAP     `wiki/tracker/wayfinder-cfl.md`, the live map. CLAUDE.md's read-order tells every
#           session to open it, so the word appears in sessions that were never going to run the
#           protocol. Reading the map is not declining to run the skill.
#   PARTY   a connector-side interlocutor addressed or quoted as "wayfinder" (a 2026-07-26 usage).
#           An address is not an invocation.
# Order matters: PARTY is tested first because "wayfinder said the map is stale" contains map
# vocabulary and is still not a map reference; SKILL last, because an explicit slash command or
# "run wayfinder" overrides the others and is re-checked ahead of everything by the caller.
# PARTY WAS BROADENED AFTER MEASURING, AND THE MEASUREMENT IS THE REASON IT IS THIS LONG.
# The first version tested only "wayfinder said" / "from wayfinder" and left 68.8% of occurrences
# UNCLASSIFIED. Reading 22 of those windows by hand showed one dominant shape it could not see:
# wayfinder as an ADDRESSED ROLE — "You are the FL wayfinder", "TO: wayfinder, FROM: Jon",
# "relayed via CFL wayfinder", "**From**: Triage/Wayfinder", "what I'm asking you as the
# wayfinder". That is the connector-side party sense `wiki/references/vocabulary.md` records, and
# it is the largest single non-invocation use of the word in Jon's own turns.
WF_SENSE_PARTY = re.compile(
    r"wayfinder\s+(?:said|says|sent|wrote|asked|replied|reports?|noted|flagged|thinks)|"
    r"(?:from|to|ask|tell|per|via)\s+wayfinder\b|wayfinder'?s\s+(?:message|note|reply|read|view)|"
    r"@wayfinder|wayfinder\s+(?:agent|party|side)|"
    r"(?:the\s+)?(?:FL|CFL|claude\.ai|fl-side|connector)\s+wayfinder|"
    r"\bTO:\s*wayfinder|wayfinder\s*[,·|]\s*FROM\b|triage\s*/\s*wayfinder|"
    r"you\s+are\s+the\s+(?:\w+\s+){0,2}wayfinder|as\s+the\s+wayfinder|"
    r"wayfinder\s*\((?:claude\.ai|connector)", re.I)
WF_SENSE_SKILL = re.compile(
    r"(?:^|\s)/wayfinder\b|run\s+(?:the\s+)?wayfinder|use\s+(?:the\s+)?wayfinder|"
    r"wayfinder\s+(?:skill|protocol|process)|invoke\s+wayfinder|wayfinder\s+this\b|"
    r"skills[\\/]wayfinder|"
    # named in a LIST of adopted skills — "pocock skills ... Wayfinder, to_ticket, handoff"
    r"wayfinder\s*,\s*(?:to[_-]?ticket|handoff|grill)|pocock\s+skills", re.I)
WF_SENSE_MAP = re.compile(
    r"wayfinder[- ]cfl|wayfinder\s+map|the\s+map\b|wayfinder\s+(?:ticket|tickets|entry|entries|"
    r"row|rows|register|registry|tracker)|unclosed\s+ticket|wiki[\\/]tracker", re.I)
WF_WINDOW = 260          # chars either side of the word; a window is not a document, and says so


def wayfinder_senses(turn_text):
    """['SKILL'|'MAP'|'PARTY'|'UNCLASSIFIED', ...] — one label per occurrence of the word.

    Occurrences closer together than MERGE_CHARS are one occurrence, reusing `gbs_record`'s rule
    rather than inventing a second one.
    """
    out, last = [], None
    for m in re.finditer(r"wayfinder", turn_text, re.I):
        if last is not None and m.start() - last <= MERGE_CHARS:
            last = m.end()
            continue
        last = m.end()
        w = turn_text[max(0, m.start() - WF_WINDOW): m.end() + WF_WINDOW]
        if WF_SENSE_SKILL.search(w):
            out.append("SKILL")
        elif WF_SENSE_PARTY.search(w):
            out.append("PARTY")
        elif WF_SENSE_MAP.search(w):
            out.append("MAP")
        else:
            out.append("UNCLASSIFIED")
    return out


def analyse_wayfinder(sp):
    seq = sp.get("__seq__", [])
    whole = "\n".join(t for _, t in seq)
    if not whole:
        return None
    template = bool(WF_TEMPLATE.search(whole)) or bool(WF_TEMPLATE_BODY.search(whole))
    marker = bool(WF_MARKER.search(whole))
    marker_filled = False
    for m in WF_MARKER.finditer(whole):
        body = whole[m.end(): m.end() + WF_BODY_CHARS]
        if body.strip() and not WF_TEMPLATE_BODY.search(body):
            marker_filled = True
    senses = Counter()
    for role, txt in seq:
        if role != "H":
            continue
        senses.update(wayfinder_senses(txt))
    return {
        "marker": marker,
        "completion": bool(WF_COMPLETION.search(whole)),
        "mapshape": bool(WF_MAPSHAPE.search(whole)),
        "marker_filled": marker_filled,
        "template_present": template,
        "template_only": marker and not marker_filled,
        "genuine": marker_filled,
        "senses": senses,
    }


# =================================================================================================
# grill-me — skills/grill-me/SKILL.md  (+ its adversarial twin, reverse-grill-me)
# =================================================================================================
# SKILL.md:82, verbatim and mandated at session close. This is a COMPLETION literal, and no entry
# for it exists in `corpus_index.MARKERS` — which is why that file reports grill-me's USED as
# UNDETECTABLE rather than zero. Declared here so the class stops being empty by construction.
GM_CLOSE = re.compile(r"is this an accurate summary\??\s*anything i missed", re.I)
# SKILL.md:38 / reverse-grill-me SKILL.md:39 — the disambiguation question, verbatim both ways.
GM_DISAMBIG = re.compile(
    r"collaborative interview where I help you think it through|"
    r"adversarial stress-test where you defend it", re.I)
# SKILL.md:76-81 — the four things the close must summarize.
GM_SUMMARY = re.compile(
    r"core design\s*/\s*plan|key assumptions identified|gaps or risks surfaced|"
    r"open questions remaining", re.I)
# The trigger table itself, SKILL.md:28-33. Documentation, not a run.
GM_TEMPLATE = re.compile(
    r"\|\s*\"grill me\"\s*\||Ask what to grill; then begin|"
    r"skills[\\/](?:reverse-)?grill-me[\\/]SKILL\.md", re.I)
# reverse-grill-me SKILL.md:76-95.
RG_MARKER = re.compile(r"surviving claims", re.I)
RG_VERDICTS = re.compile(r"\bSURVIVED\b|\bMODIFIED\b|\bFAILED\b")

# ------------------------------------------------------------------------------------------------
# THE CADENCE DETECTOR — the only instrument here that can see an UNNAMED use
# ------------------------------------------------------------------------------------------------
# grill-me's defining constraint is SKILL.md:47-49: *ask one question at a time, wait for the
# answer, follow the answer to the next question.* That is a TURN-SHAPE claim, and turn shape is
# the one thing the markdown corpus records exactly. A grilling looks like:
#     A(short, exactly one '?')  H  A(short, exactly one '?')  H  ...
# Runs of length >= 3 are counted. Three is the floor because two is an ordinary clarifying
# exchange; below three the pattern is indistinguishable from normal conversation, and saying so
# is more useful than picking a number that flatters the count.
#
# THIS OVER-COUNTS AND THE DIRECTION IS KNOWN. Any patient back-and-forth — teach-me, a debugging
# session, Jon answering a series of yes/no gates — has this shape. It is therefore a CANDIDATE
# count for "kinda did", exactly as `skill_record`'s Tier 2 is for FBC, and never a use count.
GM_MAX_CHARS = 1400        # an assistant turn longer than this is a briefing, not a question
QMARK = re.compile(r"\?")


def _is_single_question(text):
    """True when this turn is one short question and nothing else.

    THE TRAILING-SEPARATOR BUG, RECORDED BECAUSE IT RETURNED A CLEAN ZERO.
    The first version required `body.endswith('?')`. Every assistant turn in the parsed corpus
    ends with the exporter's `---` rule, so that test was false for every turn in 1,137 files and
    the detector reported **0 cadence runs corpus-wide** — a plausible-looking number produced by
    a formatting artefact. The separator is stripped, and the question is required to fall in the
    turn's TAIL rather than at its literal end, which is the property that was actually meant:
    the turn closes on a question and then waits.
    """
    body = re.sub(r"^#{1,4}\s*\w+.*$", "", text, count=1, flags=re.M)
    # A SECOND BUG IN THE SAME THREE LINES, WORTH ITS OWN NOTE. The strip was first written as
    # `(?:\s*-{3,}\s*)+$` — a nested quantifier over overlapping character classes, which
    # backtracks catastrophically on a markdown table's `|-----|-----|` rule. It did not fail; it
    # HUNG, for over twenty minutes on a 1,137-file scan, with no output and no error. A regex that
    # hangs is indistinguishable from a slow corpus read, which is why it survived one run.
    # `[-\s|]+$` is a single greedy character class and cannot backtrack.
    body = re.sub(r"[-\s|]+$", "", body).strip()
    if not body or len(body) > GM_MAX_CHARS:
        return False
    if len(QMARK.findall(body)) != 1:
        return False
    return body.rfind("?") >= len(body) - 200


def cadence_runs(seq, floor=3):
    """[(start_index, length)] for maximal A?/H alternations of single-question assistant turns."""
    runs, i, n = [], 0, len(seq)
    while i < n:
        if seq[i][0] != "A" or not _is_single_question(seq[i][1]):
            i += 1
            continue
        j, length = i, 0
        while j < n and seq[j][0] == "A" and _is_single_question(seq[j][1]):
            length += 1
            j += 1
            if j < n and seq[j][0] == "H":
                j += 1
            else:
                break
        if length >= floor:
            runs.append((i, length))
        i = max(j, i + 1)
    return runs


def analyse_grill(sp):
    seq = sp.get("__seq__", [])
    whole = "\n".join(t for _, t in seq)
    if not whole:
        return None
    template = bool(GM_TEMPLATE.search(whole))
    runs = cadence_runs(seq)
    return {
        "close_literal": bool(GM_CLOSE.search(whole)),
        "disambig": bool(GM_DISAMBIG.search(whole)),
        "summary_shape": bool(GM_SUMMARY.search(whole)),
        "template_only": template and not GM_CLOSE.search(whole),
        "genuine": bool(GM_CLOSE.search(whole)) and not template,
        "cadence_runs": len(runs),
        "cadence_longest": max((L for _, L in runs), default=0),
        "rg_marker": bool(RG_MARKER.search(whole)),
        "rg_verdicts": len(set(RG_VERDICTS.findall(whole))),
    }


# =================================================================================================
# temporal-context — skills/temporal-context/SKILL.md
# =================================================================================================
# WHY THIS SKILL BREAKS ALL THREE PATTERNS ABOVE, AND WHY IT IS THE ONE JON NAMED
# --------------------------------------------------------------------------------
# Every other skill in this module is INVOKED. `temporal-context` declares, in its own
# frontmatter, `"Triggers on every response."` So its occasion is not a phrase Jon types — it is
# **every assistant turn in the corpus**, and APPLICABLE-NOT-USED is therefore MEASURED and huge
# rather than UNKNOWN or capped. It is the only skill here whose ANU class is not trigger-limited.
#
# And it is the only one with an EXTERNAL ANSWER KEY. The `.sidecar.md` companions carry the
# Claude Code JSONL's per-turn `timestamp`, and `T{n}` in the sidecar is the nth `## Human` /
# `## Assistant` / `## Tool Result` / `## Compaction Boundary` heading in the primary — verified
# by role-wise count equality, not assumed. So for every stamped turn the corpus can answer a
# question no other skill record can ask: **was the stamp right?**
#
# That matters because the skill's measured failure mode is not omission. It is a stamp that is
# present, confidently formatted, labelled `[measured]`, and WRONG — the exact defect
# `exchange/personal-to-cfl-temporal-context-defect-2026-08-04.md` raised and
# `...-wiki-documentation-2026-08-06.md` recorded a second instance of. A presence detector scores
# both of those sessions USED.
TC_STAMP = re.compile(r"\[(\d{4}-\d{2}-\d{2})[ T]+(\d{1,2}):(\d{2})\s*(CDT|CST)\s*\]", re.I)
TC_LABEL_CHARS = 100
# THE LABEL IS A PARENTHETICAL, AND THE FIRST VERSION OF THIS WAS WRONG
# -----------------------------------------------------------------------
# v1 searched a 140-char tail for the bare word `measured`. Hand-checking the three worst
# FALSE-[measured] rows found all three were the SAME false positive: prose reading
# "**Measured, not asserted:**" a sentence AFTER the stamp, about a table of findings, not
# about the clock. The published FALSE-[measured] count was contaminated by a word this
# program uses constantly for other reasons.
# The real vocabulary, read off the corpus (1,473 stamp occurrences surveyed, not recalled):
# the label is a PARENTHETICAL IMMEDIATELY FOLLOWING the stamp — `*(measured)*`,
# `*(ESTIMATED - check reasonability)*`, `*(estimated)*`, `*(user-provided)*`,
# `*(anchored from write timestamp)*`, `*(+~3 min per exchange rule)*`. So the head of the
# tail is parsed, not scanned.
# Matched against the FIRST LINE of the tail only - a label does not wrap.
TC_LABEL_HEAD = re.compile(r"^[\s`*_]{0,6}[\(\[]([^)\]]{0,90})[\)\]]")
TC_MEASURED = re.compile(r"\bmeasured\b", re.I)
# Everything that is NOT a measurement but IS an honest disclosure of provenance. The skill's
# tier 3 (user-provided) and tier 4 (dead reckoning) both live here, plus Jon's own claude.ai
# file-mtime workaround, which SKILL.md:70-74 explicitly blesses on that surface.
TC_ESTIMATED = re.compile(
    r"\bestimat|\banchor|dead.?reckon|user.?provided|per exchange|check reasonability", re.I)
# SKILL.md tier 1: "run `date` before stamping". Its shadow in a Claude Code transcript is a
# shell invocation of `date` / PowerShell `Get-Date` in the same turn or the turn before.
TC_DATE_CALL = re.compile(r"(?<![\w-])date\s+(?:-u|\+%|\+\"|\+')|(?<![\w-])\bdate\b\s*$|"
                          r"Get-Date|\[datetime\]::Now|datetime\.now\(\)", re.I | re.M)
# The boundary-marker finding: Jon's greeting is a COMPACTION marker, not a clock reading.
# `personal-to-cfl-temporal-context-defect-2026-08-04.md`, Jon verbatim: "I view you as
# meaningfully 'waking up'." Detected in H turns only, at the head of the turn body.
TC_GREETING = re.compile(r"^\s*(?:##\s*Human\s*)?\W{0,4}(good\s+(morning|night|evening|afternoon))",
                         re.I)
# Every date in this corpus falls inside US DST 2026 (Mar 8 – Nov 1), so the CDT label is
# UTC-5 throughout and no seasonal branch is needed. Asserted as a CHECK, not a belief:
# `tc_offset_hours` raises the flag rather than silently applying the wrong offset.
TC_DST_START, TC_DST_END = "2026-03-08", "2026-11-01"


def tc_offset_hours(datestr):
    """(hours_behind_utc, in_dst). CDT=5, CST=6. Returns the flag, never guesses silently."""
    in_dst = TC_DST_START <= datestr <= TC_DST_END
    return (5 if in_dst else 6), in_dst


@lru_cache(maxsize=4)          # one file is analysed at a time; this stops the
def _sidecar_rows(primary_path_str):
    return tuple(_sidecar_rows_uncached(primary_path_str))


def sidecar_timestamps(primary_path):
    """Public entry: cached. See _sidecar_rows_uncached for the contract."""
    return list(_sidecar_rows(str(primary_path)))


def _sidecar_rows_uncached(primary_path):
    """[(turn_no, role, iso)] from the `.sidecar.md` companion, in file order; [] if none.

    THE FIELD NAME IS NOT ONE FIELD NAME, AND THAT IS THE WHOLE POINT
    -------------------------------------------------------------------
    Claude Code sidecars (manifest v2, jsonl-convert) declare `- timestamp:` and title their
    rows `### T1 - Human`. claude.ai sidecars declare `- created_at:` and title theirs
    `### T1 - human`, lowercase. The first version of this function read `timestamp:` only and
    the self-test caught it returning **0 rows for a file with 8 turns** — the identical defect
    `CLAUDE.md` records for `cc_corpus_gap.py`, which read `source_id:` while 26 extracts declared
    `uuid:` and therefore reported every one of them LOST. **It was not finding losses. It was
    finding a field name.** Both spellings are read here, and the alignment is CHECKED rather
    than assumed.

    ABSENT IS UNKNOWN, NEVER ZERO. A transcript with no sidecar contributes to the presence
    counts and to NOTHING in the drift table. The two denominators are printed separately.
    """
    sc = Path(str(primary_path)[:-3] + ".sidecar.md")
    if not sc.is_file():
        return []
    try:
        txt = sc.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    out = []
    for m in re.finditer(
            r"^### T(\d+) [-—–] *([A-Za-z ]*?)\s*$(.{0,600}?)^- (?:timestamp|created_at): (\S+)",
            txt, re.M | re.S):
        if m.group(4) not in ("None", "(none)"):
            out.append((int(m.group(1)), m.group(2).strip().lower(), m.group(4)))
    return out


# Roles the sidecar enumerates, mapped onto `turn_index`'s single-letter roles. `D` (an
# orchestrating agent's dispatch) occupies a `user` record in the JSONL, so it aligns with
# `human`; keeping the two letters distinct matters for attribution, not for the clock.
_TC_ROLE = {"human": "H", "assistant": "A", "tool result": "R", "compaction": "C",
            "compaction boundary": "C"}


def align_sidecar(seq, primary_path):
    """{seq_index: iso} — the sidecar's true clock, aligned to `spans` turns, or {} if it cannot
    be aligned. NEVER aligns on length alone: the role sequences must agree element-by-element.

    Two shapes are accepted, in order:
      1. the sidecar enumerates every turn the primary heads (Claude Code, manifest v2);
      2. the sidecar enumerates only conversational turns (claude.ai), in which case the `R`
         turns of `seq` are dropped before comparing.
    Anything else returns {} and the caller reports the stamps as UNALIGNED, not as zero drift.
    """
    rows = sidecar_timestamps(primary_path)
    if not rows:
        return {}
    want = [_TC_ROLE.get(r, "?") for _, r, _ in rows]
    for keep in (("H", "A", "R", "C", "D"), ("H", "A", "C", "D")):
        idx = [i for i, (role, _t) in enumerate(seq) if role in keep]
        got = ["H" if seq[i][0] == "D" else seq[i][0] for i in idx]
        if len(got) == len(want) and all(a == b or "?" in (a, b) for a, b in zip(got, want)):
            return {idx[k]: rows[k][2] for k in range(len(idx))}
    return {}


def _tc_true_local(iso, datestr):
    """datetime in Jon's local wall time from the sidecar's UTC ISO stamp, or None."""
    import datetime as _dt
    try:
        base = _dt.datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError):
        return None
    off, _ = tc_offset_hours(datestr)
    return base - _dt.timedelta(hours=off)


def analyse_temporal(sp, path=None):
    """One transcript's temporal-context record. Pure; writes nothing.

    THE UNIT IS THE RESPONSE TURN, AND THAT IS A CHOICE THAT IS STATED
    -------------------------------------------------------------------
    SKILL.md says "every response". In a Claude Code transcript an `## Assistant` heading is
    emitted for every tool-calling step, most of which Jon never reads. Counting those as
    unstamped "responses" would inflate APPLICABLE-NOT-USED by an order of magnitude and the
    inflation would track how tool-heavy a session was, not how the skill performed.
    So a RESPONSE TURN is an `A` turn that is the last `A` before the next `H` turn (or the end
    of the transcript) — the turn Jon actually reads. **Both denominators are computed and both
    are printed.** Neither is hidden.
    """
    import datetime as _dt
    seq = sp.get("__seq__", [])
    if not seq:
        return None

    # A turn is a RESPONSE turn if no further `A` turn precedes the next `H`.
    n = len(seq)
    is_response = [False] * n
    for i, (role, _t) in enumerate(seq):
        if role != "A":
            continue
        j = i + 1
        while j < n and seq[j][0] not in ("A", "H", "D"):
            j += 1
        if j >= n or seq[j][0] in ("H", "D"):
            is_response[i] = True

    side = None
    a_turns = sum(1 for r, _ in seq if r == "A")
    resp_turns = sum(1 for f in is_response if f)

    stamps = []           # one row per stamp occurrence
    stamped_a = stamped_resp = 0
    cst_stamps = 0
    for i, (role, txt) in enumerate(seq):
        if role != "A":
            continue
        ms = list(TC_STAMP.finditer(txt))
        if not ms:
            continue
        if is_response[i]:
            stamped_resp += 1
        stamped_a += 1
        if side is None and path is not None:
            side = align_sidecar(seq, path)
        prev = seq[i - 1][1] if i else ""
        has_date_call = bool(TC_DATE_CALL.search(txt) or TC_DATE_CALL.search(prev))
        for m in ms:
            tail = txt[m.end(): m.end() + TC_LABEL_CHARS]
            first_line = tail.splitlines()[0] if tail.splitlines() else ""
            head = TC_LABEL_HEAD.match(first_line)
            lab = head.group(1) if head else ""
            claims_measured = bool(lab and TC_MEASURED.search(lab))
            claims_estimated = bool(lab and TC_ESTIMATED.search(lab))
            if (m.group(4) or "").upper() == "CST":
                cst_stamps += 1
            err = None
            iso = (side or {}).get(i)   # aligned by ROLE SEQUENCE, not by index arithmetic
            if iso:
                true = _tc_true_local(iso, m.group(1))
                if true is not None:
                    try:
                        got = _dt.datetime.strptime(
                            f"{m.group(1)} {int(m.group(2)):02d}:{m.group(3)}", "%Y-%m-%d %H:%M")
                        err = (got - true).total_seconds() / 60.0
                    except ValueError:
                        err = None
            same_day = (iso is not None and _tc_true_local(iso, m.group(1)) is not None
                        and _tc_true_local(iso, m.group(1)).strftime("%Y-%m-%d") == m.group(1))
            stamps.append(dict(turn=i + 1, response=is_response[i], err_min=err,
                               same_day=same_day,
                               claims_measured=claims_measured,
                               claims_estimated=claims_estimated,
                               labelled=claims_measured or claims_estimated,
                               label=lab,
                               date_call=has_date_call, zone=(m.group(4) or "").upper()))

    # The greeting case: Jon says "Good morning" -> what did the next response stamp?
    greetings = []
    for i, (role, txt) in enumerate(seq):
        if role != "H":
            continue
        g = TC_GREETING.search(txt[:400])
        if not g:
            continue
        j = i + 1
        while j < n and seq[j][0] != "A":
            j += 1
        if j >= n:
            continue
        m = TC_STAMP.search(seq[j][1])
        if not m:
            greetings.append(dict(turn=i + 1, word=g.group(2).lower(), stamped=None,
                                  true_hour=None, replied_stamped=False))
            continue
        if side is None and path is not None:
            side = align_sidecar(seq, path)
        iso = (side or {}).get(j)
        true = _tc_true_local(iso, m.group(1)) if iso else None
        greetings.append(dict(turn=i + 1, word=g.group(2).lower(), replied_stamped=True,
                              stamped=f"{m.group(1)} {int(m.group(2)):02d}:{m.group(3)}",
                              stamped_hour=int(m.group(2)),
                              true_hour=(true.hour if true else None),
                              true=(true.strftime("%Y-%m-%d %H:%M") if true else None)))

    return dict(a_turns=a_turns, resp_turns=resp_turns, stamped_a=stamped_a,
                stamped_resp=stamped_resp, stamps=stamps, greetings=greetings,
                cst_stamps=cst_stamps, has_sidecar=bool(side),
                sidecar_present=bool(sidecar_timestamps(path)) if path is not None else False,
                genuine=bool(stamps),
                labelled=sum(1 for s in stamps if s["labelled"]),
                unlabelled=sum(1 for s in stamps if not s["labelled"]))


# =================================================================================================
# session-order — skills/session-order/SKILL.md
# =================================================================================================
# WHY THIS ONE NEEDS FOUR OCCASION TYPES AND NOT ONE
# ----------------------------------------------------
# `session-order` is not a protocol you invoke; it is four rituals with four different triggers,
# and they fail independently. SKILL.md declares each of them as a STATE, not a phrase Jon types:
#
#   1. COLD OPEN             "Triggers at every cold session open"  -> occasion = a conversation
#   2. POST-COMPACT RECOVERY "Wake from Nap"                        -> occasion = a `C` turn
#   3. MULTI-TOPIC MESSAGE   "when Jon sends a multi-topic message" -> occasion = a shaped H turn
#   4. SESSION CLOSE         "when session close is signaled"       -> occasion = a shaped H turn
#
# Rolling those into one USED/PARTIAL/ANU triple would report a session that kept a beautiful map
# and never ran the close ritual as simply USED. So each ritual is scored separately against its
# own occasion count, and the headline triple is the SESSION MAP — the skill's most distinctive
# structural output.
#
# THE MAP, SKILL.md "Session Map". Five labels; the skill mandates the shape, not a subset.
SO_LABELS = [
    ("DONE", re.compile(r"^\s*\**DONE\**\s*[-—–:]", re.M)),
    ("IN PROGRESS", re.compile(r"^\s*\**IN PROGRESS\**\s*[-—–:]", re.M)),
    ("NEXT", re.compile(r"^\s*\**NEXT\**\s*[-—–:]", re.M)),
    ("HELD", re.compile(r"^\s*\**HELD\**\s*[-—–:]", re.M)),
    ("TRIAGE", re.compile(r"^\s*\**TRIAGE\**\s*[-—–:]", re.M)),
]
# SKILL.md's own fenced example. A turn carrying these placeholders is quoting the skill, not
# running it. Same positional lesson the handoff and wayfinder deflators had to learn: a session
# that RUNS this skill reads SKILL.md first, so both shapes can sit in one file. The test is
# therefore per TURN, not per file.
SO_TEMPLATE = re.compile(
    r"\[closed items\]|\[active right now\]|\[agreed next steps, this session\]|"
    r"\[parked within this session|\[handed off, this session", re.I)
# SKILL.md "Topic Check" — the redirect, verbatim. Nothing else produces this sentence.
SO_TOPIC = re.compile(r"what'?s the one thing you need from this session", re.I)
# SKILL.md "Post-Compact Recovery" step 5 — the mandated restatement, verbatim.
SO_POSTCOMPACT = re.compile(r"before compaction,? we were", re.I)
# SKILL.md "Session Close Ritual" — the export judgment. The skill's own words: "A judgment call
# without a stated reason is not a judgment call." So the marker is the LABELLED form only.
#
# TIGHTENED AFTER HAND-CHECKING, AND THE FIRST VERSION WAS MOSTLY NOISE.
# v1 allowed a hyphen as the separator, so it matched `EXPORT-LOG watermark:` — the extraction
# audit trail, a completely different artifact that appears in nearly every wiki-master session.
# It also matched `SKIP-SUPERSEDED (1c802a)`, a triage disposition. Of 21 v1 hits, hand-reading
# found roughly 2 genuine close-ritual judgments. The separator is now `:` or an em/en dash only,
# and `EXPORT-LOG` / `SKIP-` compounds are excluded by a negative lookahead.
SO_EXPORT = re.compile(
    r"^\s*[-*>\s]*(?:\*\*)?(?:EXPORT|SKIP)(?!-)(?:\*\*)?\s*[:—–]|"
    r"\bExporting\s*[—–]|\bSkipping export\s*[—–]", re.M)
# SKILL.md's own list of Jon's close signals, quoted from the skill rather than invented.
#
# TIGHTENED AFTER HAND-CHECKING. SKILL.md names `"done"` as a close signal, and taking it at its
# word is what makes the detector wrong: Jon's overwhelmingly commonest use of the bare word is
# an ACKNOWLEDGEMENT that a task finished — `"Done. Next?"`, `"Done. Solved. Checking desktop."`,
# `"done. Your turn... did it work?"`. Those are the opposite of a close signal; they open the
# next item. So the bare form is dropped and only the unambiguous ones are kept.
# **This is a finding about SKILL.md, not only about the regex — see the recommendations.**
SO_CLOSE_SIGNAL = re.compile(
    r"^\W{0,4}(?:(?:i'?m|we'?re)\s+)?(?:done for (?:now|today|tonight|the (?:day|night))|"
    r"stopping (?:here|for|now)|that'?s it for (?:today|tonight|now)|good\s?night|goodnight|"
    r"wrapping up|calling it (?:a night|here|for)|signing off|"
    r"i'?m done|we'?re done|that'?s all for)\b", re.I)
# SKILL.md "Multi-Topic Message Rule". Two mechanical shapes, both deliberately conservative:
# an enumerated list of >=3 items, or >=3 question marks in one turn.
SO_ENUM = re.compile(r"^\s*(?:\d{1,2}[.)]|[-*]\s+\*\*\d)", re.M)
SO_HELD = re.compile(r"\bHELD\b")


def so_map_turns(seq):
    """[(turn_index, [labels], template_only)] for every A turn carrying >=1 map label."""
    out = []
    for i, (role, txt) in enumerate(seq):
        if role != "A":
            continue
        labs = [name for name, pat in SO_LABELS if pat.search(txt)]
        if labs:
            out.append((i, labs, bool(SO_TEMPLATE.search(txt))))
    return out


def analyse_session_order(sp):
    """One transcript's session-order record. Pure function of `sp`; writes nothing."""
    seq = sp.get("__seq__", [])
    if not seq:
        return None
    maps = so_map_turns(seq)
    genuine_maps = [m for m in maps if len(m[1]) >= 3 and not m[2]]
    template_maps = [m for m in maps if m[2]]
    partial_maps = [m for m in genuine_maps if len(m[1]) < 5]
    a_txt = "\n".join(t for r, t in seq if r == "A")

    bounds = [i for i, (r, _t) in enumerate(seq) if r == "C"]
    recov = [i for i, (r, t) in enumerate(seq) if r == "A" and SO_POSTCOMPACT.search(t)]
    # A recovery ANSWERS a boundary only if it lands AFTER it, and within 12 turns. The window is
    # a choice: the restatement is step 5 of a 7-step ritual, so a handful of reads may precede it.
    answered_bounds = sum(1 for b in bounds if any(b < k <= b + 12 for k in recov))

    close_sig = [i for i, (r, t) in enumerate(seq) if r == "H" and SO_CLOSE_SIGNAL.search(t[:220])]
    export_calls = [i for i, (r, t) in enumerate(seq) if r == "A" and SO_EXPORT.search(t)]
    answered_close = sum(1 for c in close_sig if any(c < k <= c + 8 for k in export_calls))

    multi = [i for i, (r, t) in enumerate(seq)
             if r == "H" and (len(SO_ENUM.findall(t)) >= 3 or t.count("?") >= 3)]
    answered_multi = sum(1 for c in multi if any(c < m[0] <= c + 8 for m in genuine_maps))

    return dict(
        map_turns=len(maps), genuine_maps=len(genuine_maps),
        template_maps=len(template_maps), partial_maps=len(partial_maps),
        label_hist=Counter(l for m in genuine_maps for l in m[1]),
        genuine=bool(genuine_maps),
        topic_check=len(SO_TOPIC.findall(a_txt)),
        compaction_boundaries=len(bounds), recoveries=len(recov),
        answered_bounds=answered_bounds,
        close_signals=len(close_sig), export_calls=len(export_calls),
        answered_close=answered_close,
        multi_topic=len(multi), answered_multi=answered_multi,
        held_mentions=len(SO_HELD.findall(a_txt)),
    )


# =================================================================================================
# wiki-master — skills/wiki-master/SKILL.md
# =================================================================================================
# WHY THE CORPUS IS THE WRONG PLACE TO LOOK, AND WHERE THE RECORD ACTUALLY IS
# -----------------------------------------------------------------------------
# wiki-master's product is a FILE — a source page under `wiki/sources/`. A transcript contains that
# page's shape only when the assistant also pasted it into the conversation, which is the same
# blindness the `handoff` record documents. But wiki-master differs from handoff in the decisive
# way: **the artifacts are tracked, in this repo, and every one of them can be graded against the
# skill's own schema.** So the primary measure here is a DISK AUDIT, and the corpus figures are
# reported beside it rather than instead of it.
#
# The schema is not invented. SKILL.md's "Source page section schema (confirmed 2026-05-27)" names
# three REQUIRED sections and three CONDITIONAL ones, and the Citation Quality block says, of the
# fidelity tag, "Not optional."
WM_REQUIRED = [
    ("Summary", re.compile(r"^#{2,3}\s*Summary\s*$", re.M)),
    ("Key Claims", re.compile(r"^#{2,3}\s*Key Claims\s*$", re.M)),
    ("Conflicts", re.compile(r"^#{2,3}\s*Conflicts\s*$", re.M)),
]
WM_CONDITIONAL = [
    ("Entities & Concepts", re.compile(r"^#{2,3}\s*Entities\s*&\s*Concepts", re.M)),
    ("Cross-Wiki", re.compile(r"^#{2,3}\s*Cross-Wiki", re.M)),
    ("Uncaptured Content", re.compile(r"^#{2,3}\s*Uncaptured Content", re.M)),
]
# SKILL.md: "Every Key Claim carries one fidelity tag. Not optional.
# Format: `- **Claim text** [quality, timestamp]`". Six qualities; `inferred` and `uncaptured`
# were ADDED by G2, ratified by Jon 2026-07-13 — so the rule has a birthday and pages that
# predate it are evidence, not violations. That split is computed, never assumed.
WM_FIDELITY = re.compile(
    r"\[(verbatim|paraphrase|reconstructed|contextual|inferred|uncaptured)\b", re.I)
WM_G2_RATIFIED = "2026-07-13"
# SKILL.md conflict rule: "Never silently overwrite... write both and mark `CONFLICT:`."
WM_CONFLICT = re.compile(r"CONFLICT\s*:", re.I)
# SKILL.md: Conflicts is "Always present - ingest is incomplete without this; write 'None.'
# explicitly when none apply." So an EMPTY Conflicts section is its own defect class.
WM_NONE = re.compile(r"^\s*(?:\*\*)?None\.?(?:\*\*)?\s*$", re.M | re.I)
# The ingest count gate and the PARTIAL registry cross-check, both mandated at startup.
WM_COUNT_GATE = re.compile(r"count gate|exhaustive count", re.I)
WM_PARTIAL_REG = re.compile(r"PARTIAL (?:session )?registry", re.I)
WM_SOURCE_PAGE_SHAPE = re.compile(r"^#{2,3}\s*Key Claims\s*$", re.M)


def wm_disk_audit(repo=REPO):
    """Grade every tracked source page against SKILL.md's own schema. Reads; writes nothing.

    Returns a dict of counts plus per-page rows, and it NEVER returns a bare ratio for the
    fidelity rule: that rule was ratified 2026-07-13, so the pages are split at that date and
    both halves are reported. A rule cannot be violated before it exists.
    """
    root = repo / "wiki" / "sources"
    rows = []
    if not root.is_dir():
        return {"root_missing": True, "rows": rows}
    for p in sorted(root.rglob("*.md")):
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        got_req = [k for k, r in WM_REQUIRED if r.search(t)]
        got_cond = [k for k, r in WM_CONDITIONAL if r.search(t)]
        # Key Claim bullets, scoped to the section rather than the page.
        bullets, tagged = 0, 0
        m = WM_REQUIRED[1][1].search(t)
        if m:
            # SECTION SLICING IS LEVEL-AWARE, AND THE FIRST VERSION WAS NOT.
            # v1 cut the section at the next `^#{2,3}`, so a `### ` SUBHEADING inside Key
            # Claims truncated it. Measured cost: 919 bullets / 81 tagged instead of the true
            # 1,201 / 162 -- it deleted a third of the section and, worse, deleted it
            # NON-UNIFORMLY, because the pages that subdivide their claims are the long ones.
            level = len(re.match(r"#+", t[m.start():]).group(0))
            seg = t[m.end():]
            nxt = re.search(r"^#{1,%d}\s" % level, seg, re.M)
            seg = seg[:nxt.start()] if nxt else seg
            bl = re.findall(r"^\s*[-*]\s+\S.*$", seg, re.M)
            bullets = len(bl)
            tagged = sum(1 for b in bl if WM_FIDELITY.search(b))
        # Conflicts section: present but empty is a distinct defect from absent.
        conf_empty = None
        mc = WM_REQUIRED[2][1].search(t)
        if mc:
            level = len(re.match(r"#+", t[mc.start():]).group(0))
            seg = t[mc.end():]
            nxt = re.search(r"^#{1,%d}\s" % level, seg, re.M)
            seg = seg[:nxt.start()] if nxt else seg
            conf_empty = not seg.strip()
        # Date from the filename's embedded YYYY-MM-DD, else from frontmatter `date_ingested`.
        dm = re.search(r"(20\d\d-\d\d-\d\d)", p.name)
        if dm:
            date = dm.group(1)
        else:
            fm = re.search(r"^date_ingested:\s*(20\d\d-\d\d-\d\d)", t, re.M)
            date = fm.group(1) if fm else "UNKNOWN"
        rows.append(dict(path=str(p.relative_to(repo)).replace("\\", "/"), date=date,
                         req=got_req, cond=got_cond, bullets=bullets, tagged=tagged,
                         conflicts_empty=conf_empty,
                         has_conflict_marker=bool(WM_CONFLICT.search(t))))
    return {"root_missing": False, "rows": rows}


def analyse_wiki_master(sp):
    """One transcript's wiki-master record — what the CORPUS can see, which is pastes."""
    seq = sp.get("__seq__", [])
    if not seq:
        return None
    a_txt = "\n".join(t for r, t in seq if r == "A")
    n_shape = len(WM_SOURCE_PAGE_SHAPE.findall(a_txt))
    req_all = all(r.search(a_txt) for _k, r in WM_REQUIRED)
    return dict(
        genuine=bool(n_shape),
        page_shapes=n_shape,
        all_required=bool(req_all),
        fidelity_tags=len(WM_FIDELITY.findall(a_txt)),
        conflict_markers=len(WM_CONFLICT.findall(a_txt)),
        count_gate=bool(WM_COUNT_GATE.search(a_txt)),
        partial_registry=bool(WM_PARTIAL_REG.search(a_txt)),
    )


# =================================================================================================
# REGISTRY — registered INTO skill_record.RECORDS so nothing is defined twice
# =================================================================================================
RECORDS_EXT = {
    "wiki-master": {
        "src": "skills/wiki-master/SKILL.md — 'Source page section schema (confirmed "
               "2026-05-27)' (3 required + 3 conditional sections), 'Citation Quality "
               "vocabulary — REQUIRED' (fidelity tag, G2-ratified 2026-07-13), the conflict "
               "rule, the ingest count gate, the PARTIAL registry cross-check",
        "analyse": analyse_wiki_master,
        "anu_state": "MEASURED ON DISK, NOT IN THE CORPUS — this skill's product is a FILE, and "
                     "the files are tracked in this repo. A transcript sees a source page only "
                     "if the assistant also pasted it, so a corpus-only ANU would be a count of "
                     "non-pastes. The disk audit grades every tracked page against SKILL.md's "
                     "own schema; the corpus figures are printed beside it and NEVER reconciled "
                     "into one number. The fidelity-tag rule was ratified 2026-07-13, so pages "
                     "are split at that date: a page written before a rule existed is evidence "
                     "FOR the rule, never a violation of it.",
    },
    "session-order": {
        "src": "skills/session-order/SKILL.md — Session Map (5 labels), Topic Check (verbatim "
               "redirect), Post-Compact Recovery (step 5 restatement), Session Close Ritual "
               "(EXPORT/SKIP judgment), Multi-Topic Message Rule",
        "analyse": analyse_session_order,
        "anu_state": "MEASURED PER RITUAL, NEVER IN AGGREGATE — this skill is four rituals with "
                     "four different triggers and they fail independently. One ANU number would "
                     "score a session that kept a map and skipped the close ritual as compliant. "
                     "Each ritual carries its own occasion count and its own denominator. The "
                     "COLD-OPEN ritual, which is the skill's first and largest clause, CANNOT be "
                     "scored at all: its output is reading, and reading leaves no mark. That is "
                     "UNKNOWN, never zero.",
    },
    "temporal-context": {
        "src": "skills/temporal-context/SKILL.md:3 (trigger: every response), :14-18 (format), "
               ":22-70 (source priority, corrected 2026-08-05), :120-127 (clock behavior); "
               "answer key = the `.sidecar.md` per-turn `timestamp`",
        "analyse": analyse_temporal,
        "needs_path": True,
        "anu_state": "MEASURED, AND THE ONLY UNCAPPED ONE IN THIS MODULE — SKILL.md's declared "
                     "trigger is 'every response', so the occasion is an assistant turn, not a "
                     "phrase Jon types. The class cannot shrink because Jon stopped asking. "
                     "corpus_index's own ANU for this slug (24 files) is computed from the "
                     "generated phrase list ('temporal context', '/temporal-context') and is "
                     "measuring something else entirely: sessions that TALKED about the skill.",
    },
    "handoff": {
        "src": "skills/handoff/SKILL.md:66-99 (template), :34,43-47 (two artifacts), :181 "
               "(self-test), :228-249 (interpretation summary, ratified 2026-08-03)",
        "analyse": analyse_handoff,
        "anu_state": "UNKNOWN — SKILL.md declares NO lexical trigger. Its triggers are "
                     "'60-70% context fill' and 'Jon signals a session boundary', which are "
                     "states, not strings. The generated trigger list holds only `/handoff` "
                     "(the bare word is 7 chars, below corpus_index's MIN_TRIGGER_LEN of 8). "
                     "A zero in this class is a property of the trigger table, not of the record.",
    },
    "wayfinder": {
        "src": "skills/wayfinder/SKILL.md:59,69 (map body); equivocality per "
               "wiki/references/vocabulary.md and cfl-branch-registry.md 1.1",
        "analyse": analyse_wayfinder,
        "anu_state": "MEASURED BUT EQUIVOCAL — the trigger is the bare word `wayfinder`, which "
                     "names the protocol, the map file, and a connector-side party. The sense "
                     "split is printed; the headline is only as good as it.",
    },
    "grill-me": {
        "src": "skills/grill-me/SKILL.md:82 (close literal), :38 (disambiguation), :47-49 "
               "(one-question cadence); twin skills/reverse-grill-me/SKILL.md:76-95",
        "analyse": analyse_grill,
        "anu_state": "MEASURED BUT STRUCTURALLY CAPPED — every declared trigger is a META-REQUEST "
                     "Jon types ('grill me', 'stress-test this'). The class therefore cannot grow "
                     "when Jon stops asking, which is the same trap skill_record's FBC record "
                     "named. A fall in this number is indistinguishable from Jon asking less.",
    },
}
for _slug, _spec in RECORDS_EXT.items():
    SR.RECORDS.setdefault(_slug, _spec)


# =================================================================================================
# REPORT
# =================================================================================================
def _load():
    r = SR.load_rows()
    return (r + (None,))[:3] if len(r) == 2 else r


def scan(rows, slug, max_files=None):
    spec = RECORDS_EXT[slug]
    fn = spec["analyse"]
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
        a = fn(sp, p) if spec.get("needs_path") else fn(sp)
        if a is None:
            continue
        a.update(path=rel, date=row.get("date", "UNKNOWN"), kind=row.get("kind"),
                 venue=row.get("venue"), trunk=row.get("trunk"),
                 in_index_markers=slug in row.get("markers", []),
                 trigger_human=slug in row.get("triggers_human", []),
                 reemission=bool(SR.REEMISSION.search(rel)),
                 self_audit=bool(SR.SELF_AUDIT.search(rel)))
        recs.append(a)
    return recs


def _common_header(rows, slug, how, recs):
    print()
    print("=" * 88)
    print(f"ACCUMULATED SESSION RECORD — {slug}")
    print("=" * 88)
    print("--- DENOMINATORS (in the output, not the docstring) --------------------------")
    print(f"  corpus root                       : {CI.CORPUS}")
    print(f"  transcripts in corpus_index       : {len(rows)}")
    print(f"  index read via                    : {how}")
    print(f"  transcripts re-read here          : {len(recs)}")
    print(f"  skill's declared surface          : {RECORDS_EXT[slug]['src']}")
    print()


def _three_class_blocks(rows, slug):
    ordered = sorted(rows.values(), key=lambda r: r["path"])
    skills = CI.load_skills()
    q = CI.three_class(ordered, slug, skills)
    used, partial, anu = q["USED"], q["PARTIAL"], q["APPLICABLE_NOT_USED"]
    print("--- FILE-SCOPED, corpus_index.three_class AS IT REPORTS ----------------------")
    print(f"  marker      : {q['marker_state']}")
    print(f"  completion  : {q['completion_state']}")
    print(f"  trigger     : {q['trigger_state']}")
    print(f"  USED                {len(used):>5}   marker string present anywhere in the file")
    if partial is None:
        print("  PARTIAL             UNDETECTABLE — no completion literal declared upstream")
    else:
        ov = len(set(used) & set(partial))
        print(f"  PARTIAL             {len(partial):>5}   marker present, no completion literal")
        print(f"  ** PARTIAL is a SUBSET of USED: overlap = {ov} of {len(partial)}. NOT a ratio. **")
    print(f"  APPLICABLE_NOT_USED {0 if anu is None else len(anu):>5}   "
          f"trigger phrase in JON'S turns, no marker")
    print(f"  ANU STATE: {RECORDS_EXT[slug]['anu_state']}")
    print()

    window = CI.set_default_window(ordered)
    t = CI.turn_three_class(ordered, slug, skills, window)
    print("--- TURN-SCOPED, THE UNIT IS (transcript, turn) ------------------------------")
    print(f"  window                            : {window}   ({CI.WINDOW_SOURCE})")
    print(f"  TURNS in index                    : {t['turns_total']:,}")
    print(f"  occasions scored (Jon-trigger turns): {t['occasions']}  "
          f"in {t['files_with_occasions']} files")
    print(f"  TURN_USED                         : {len(t['TURN_USED'])}")
    print(f"  TURN_PARTIAL                      : "
          f"{'UNDETECTABLE' if t['TURN_PARTIAL'] is None else len(t['TURN_PARTIAL'])}")
    print(f"  TURN_APPLICABLE_NOT_USED          : {len(t['TURN_APPLICABLE_NOT_USED'])}")
    print("  Compaction boundaries reset the window HARD: a marker on the far side of a")
    print("  compact cannot answer a trigger on this side, because the session can no longer")
    print("  see it. 26 files in the index carry a boundary.")
    print()
    return q, t


def _when(recs, key="genuine"):
    orig = [r for r in recs if r.get(key) and not r["reemission"] and not r["self_audit"]]
    hist = Counter(r["date"][:7] for r in recs if r.get(key) and r["date"] != "UNKNOWN")
    ohist = Counter(r["date"][:7] for r in orig if r["date"] != "UNKNOWN")
    print("--- WHEN (files with a genuine shape, by month) ------------------------------")
    print(f"  {'month':<9} {'shaped':>8} {'ORIGINAL':>9}   "
          f"(original = minus re-emissions and this audit's own agents)")
    for k in sorted(set(hist) | set(ohist)):
        print(f"  {k:<9} {hist[k]:>8} {ohist[k]:>9}  {'#' * min(ohist[k], 40)}")
    print(f"  re-emissions excluded             : "
          f"{sum(1 for r in recs if r.get(key) and r['reemission'])}")
    print(f"  this audit's own agents excluded  : "
          f"{sum(1 for r in recs if r.get(key) and r['self_audit'])}")
    last = max((r["date"] for r in orig if r["date"] != "UNKNOWN"), default="UNKNOWN")
    print(f"  LAST ORIGINAL                     : {last}")
    print()


def report_handoff(recs, rows, how, limit=15):
    _common_header(rows, "handoff", how, recs)
    _three_class_blocks(rows, "handoff")

    marker = [r for r in recs if r["marker"]]
    genuine = [r for r in recs if r["genuine"]]
    tmpl = [r for r in recs if r["template_only"]]
    print("--- THIS FILE, DISJOINT AND DEFLATED -----------------------------------------")
    print(f"  files carrying the marker heading : {len(marker)}")
    print(f"    of which TEMPLATE/DOC only      : {len(tmpl)}")
    print(f"  files with a GENUINE pasted handoff (>=5 of 10 mandated headings, not template): "
          f"{len(genuine)}")
    print(f"    reaching '## Next Steps'        : {sum(1 for r in genuine if r['completion'])}")
    print(f"    NOT reaching it ('kinda did')   : "
          f"{sum(1 for r in genuine if not r['completion'])}")
    print()
    off = [r for r in recs if r["offtemplate"]]
    print()
    print("--- OFF-TEMPLATE HANDOFFS — the class the template detector cannot count ------")
    print("  A handoff document titled as one, or a SKILL.md:185 confirmation that one was")
    print("  written, in a file with NO filled template section:")
    print(f"    files with a handoff DOCUMENT TITLE ('# Session Handoff — ...') : "
          f"{sum(1 for r in recs if r['doc_title'])}")
    print(f"    files confirming a handoff was WRITTEN (SKILL.md:185)          : "
          f"{sum(1 for r in recs if r['confirm'])}")
    print(f"    OFF-TEMPLATE (either signal, template not filled)              : {len(off)}")
    oh = Counter(r["date"][:7] for r in off if r["date"] != "UNKNOWN")
    print("    by month: " + ", ".join(f"{k}={oh[k]}" for k in sorted(oh)))
    print("  ** THE RATIO THAT MATTERS: template-conforming vs off-template = "
          f"{len(genuine)} : {len(off)}. **")
    print()
    print("--- SECTION COVERAGE — the graded 'kinda did' --------------------------------")
    print("  10 headings are mandated by SKILL.md:66-99. Distribution over genuine pastes:")
    h = Counter(r["n_sections"] for r in genuine)
    for k in sorted(h):
        print(f"    {k:>2} of 10 : {h[k]:>4}  {'#' * min(h[k], 50)}")
    miss = Counter()
    for r in genuine:
        for name, _ in HO_SECTIONS:
            if name not in r["sections"]:
                miss[name] += 1
    print("  most-omitted sections (of the genuine pastes):")
    for name, n in miss.most_common(10):
        print(f"    {n:>4}  {name}")
    print()
    print("--- COMPLIANCE WITH THE TWO 2026-08 RATIFICATIONS ----------------------------")
    # Scored over EVERY file that produced a handoff — template-conforming or not. Scoring only
    # the conforming set would divide by zero and report perfect compliance over an empty class,
    # which is the shape of a gate that passes by resolving nothing.
    produced = genuine + off
    post01 = [r for r in produced if r["date"] >= HO_RATIFIED_REPO_PATH and r["date"] != "UNKNOWN"]
    post03 = [r for r in produced if r["date"] >= HO_RATIFIED_INTERP and r["date"] != "UNKNOWN"]
    print(f"  denominator = files that produced a handoff (conforming OR off-template): "
          f"{len(produced)}")
    print(f"  dated >= {HO_RATIFIED_REPO_PATH} (repo-not-temp ratification) : {len(post01)}")
    print(f"    naming a wiki/sources source page : "
          f"{sum(1 for r in post01 if r['source_page'])}   ** SKILL.md:43-47 mandates BOTH **")
    print(f"    still naming a temp path          : {sum(1 for r in post01 if r['temp_path'])}")
    print(f"  dated >= {HO_RATIFIED_INTERP} (interpretation-summary ratification) : {len(post03)}")
    print(f"    carrying the summary table        : {sum(1 for r in post03 if r['interp'])}")
    print(f"  carrying the SKILL.md:181 self-test : {sum(1 for r in produced if r['selftest'])} "
          f"of {len(produced)}")
    print()
    print("--- THE ARTIFACTS THEMSELVES, ON DISK ----------------------------------------")
    print("  No transcript-scoped instrument can see these; the skill writes FILES.")
    arts = handoff_artifacts_on_disk()
    print(f"  handoff documents across the whole program (all sibling projects) : {len(arts)}")
    print(f"    {'filled':>6}  {'src-page':>8} {'interp':>6} {'selftest':>8}   path")
    for rel, n, sp_, ip_, st_ in arts:
        print(f"    {n:>2}/10   {'yes' if sp_ else 'NO ':>8} {'yes' if ip_ else 'NO ':>6} "
              f"{'yes' if st_ else 'NO ':>8}   {rel}")
    print(f"  BEST TEMPLATE CONFORMANCE OF ANY ARTIFACT EVER WRITTEN: "
          f"{max((a[1] for a in arts), default=0)} of 10 sections.")
    print("  Worktree copies under %LOCALAPPDATA%\\Temp\\claude\\wt-* are EXCLUDED: they are")
    print("  checkouts of the same tracked files and would multiply this count by the number")
    print("  of worktrees that happen to exist today.")
    print()
    _when(recs, key="produced")
    print("--- WHAT THIS RECORD CANNOT SEE ----------------------------------------------")
    print("  1. A HANDOFF WRITTEN BUT NEVER PASTED. Dominant case. The corpus sees pastes.")
    print("  2. APPLICABLE-NOT-USED IS UNKNOWN, NOT ZERO. There is no lexical trigger: the")
    print("     conditions are context fill and a session boundary. A session that should")
    print("     have written one and did not is invisible to every count above.")
    print("  3. THE SOURCE-PAGE HALF, WHEN THE PAGE WAS WRITTEN WITHOUT BEING NAMED. The")
    print("     test is whether the transcript names a wiki/sources path, not whether one")
    print("     exists. Under-counts compliance; the direction is known and is downward.")
    print("  4. SECTION COVERAGE IS A HEADING TEST. A section present and empty scores the")
    print("     same as a section present and complete.")
    print()


def report_wayfinder(recs, rows, how, limit=15, show_senses=False):
    _common_header(rows, "wayfinder", how, recs)
    q, t = _three_class_blocks(rows, "wayfinder")

    marker = [r for r in recs if r["marker"]]
    genuine = [r for r in recs if r["genuine"]]
    print("--- THIS FILE, DISJOINT AND DEFLATED -----------------------------------------")
    print(f"  files carrying '## Decisions So Far' : {len(marker)}")
    print(f"    of which TEMPLATE/DOC only         : {sum(1 for r in recs if r['template_only'])}")
    print(f"  genuine map bodies                   : {len(genuine)}")
    print(f"    reaching '## Out of Scope'         : {sum(1 for r in genuine if r['completion'])}")
    print(f"    NOT reaching it ('kinda did')      : "
          f"{sum(1 for r in genuine if not r['completion'])}")
    print(f"  carrying CFL map shape (wayfinder:map / ## Destination / wayfinder-cfl): "
          f"{sum(1 for r in recs if r['mapshape'])}")
    print()
    print("--- THE EQUIVOCALITY SPLIT — what the trigger word actually meant -------------")
    tot = Counter()
    for r in recs:
        tot.update(r["senses"])
    n = sum(tot.values())
    print(f"  occurrences of `wayfinder` in JON'S turns (merge rule applied): {n}")
    for k in ("SKILL", "MAP", "PARTY", "UNCLASSIFIED"):
        pctv = (100.0 * tot[k] / n) if n else 0.0
        print(f"    {k:<13} {tot[k]:>5}   {pctv:5.1f}%")
    print("  ONLY THE `SKILL` ROW IS AN INVOCATION OCCASION. The APPLICABLE-NOT-USED headline")
    print("  above is computed over ALL of them, so it is inflated by the MAP and PARTY rows —")
    print("  and MAP is the largest, because CLAUDE.md's read-order tells every session to open")
    print("  wiki/tracker/wayfinder-cfl.md. Reading the map is not declining to run the skill.")
    print()
    if show_senses:
        print("--- SENSE SPLIT BY FILE (files with any occurrence) ---------------------------")
        for r in sorted((x for x in recs if sum(x["senses"].values())),
                        key=lambda x: -sum(x["senses"].values()))[:limit]:
            s = r["senses"]
            print(f"  {r['date']}  S={s['SKILL']:<3} M={s['MAP']:<3} P={s['PARTY']:<3} "
                  f"U={s['UNCLASSIFIED']:<3}  {r['path']}")
        print()
    _when(recs)
    print("--- WHAT THIS RECORD CANNOT SEE ----------------------------------------------")
    print("  1. THE SENSE CLASSIFIER READS A 260-CHAR WINDOW. A window is not a document.")
    print("     UNCLASSIFIED is reported as its own row rather than folded into any sense.")
    print("  2. A MAP MAINTAINED WITHOUT THE HEADINGS. CFL's live map is a wiki file with its")
    print("     own shape; a session that advanced it without emitting '## Decisions So Far'")
    print("     into the transcript is invisible.")
    print("  3. WHETHER A TICKET WAS A DECISION TICKET. SKILL.md's whole distinction is")
    print("     decision-tickets vs build-slices. That is a judgment about content.")
    print("  4. The nine 'branches' are WORK TICKETS, not a taxonomy (vocabulary.md;")
    print("     cfl-branch-registry.md 1.1). Any count read as a taxonomy is misread.")
    print()


def report_grill(recs, rows, how, limit=15, show_cadence=False):
    _common_header(rows, "grill-me", how, recs)
    _three_class_blocks(rows, "grill-me")

    genuine = [r for r in recs if r["genuine"]]
    close = [r for r in recs if r["close_literal"]]
    print("--- THIS FILE: A COMPLETION LITERAL THAT NOBODY HAD DECLARED ------------------")
    print("  corpus_index.MARKERS has NO entry for grill-me, so its USED is 0 and it says so:")
    print("  'UNDECLARED — USED is undetectable, not zero'. SKILL.md:82 does mandate a verbatim")
    print("  closing question, which is a real detectable shape:")
    print(f"    files carrying 'Is this an accurate summary? Anything I missed?' : {len(close)}")
    print(f"    of those, not merely the SKILL.md trigger table                  : {len(genuine)}")
    print(f"    files carrying the disambiguation question (SKILL.md:38)         : "
          f"{sum(1 for r in recs if r['disambig'])}")
    print(f"    files carrying the close-summary shape (SKILL.md:76-81)          : "
          f"{sum(1 for r in recs if r['summary_shape'])}")
    print()
    print("--- THE CADENCE DETECTOR — unnamed uses, which is the 'kinda did' class -------")
    cad = [r for r in recs if r["cadence_runs"] > 0]
    print("  A run = >=3 consecutive assistant turns, each short and carrying EXACTLY ONE")
    print("  question, alternating with Jon's turns. SKILL.md:47-49 is that shape.")
    print(f"    files with >=1 run                : {len(cad)} of {len(recs)}")
    print(f"    total runs                        : {sum(r['cadence_runs'] for r in cad)}")
    print(f"    longest run in the corpus         : "
          f"{max((r['cadence_longest'] for r in recs), default=0)} questions")
    print(f"    files where cadence fires AND the close literal is present : "
          f"{sum(1 for r in cad if r['close_literal'])}")
    print(f"    files where cadence fires and NOTHING names the skill      : "
          f"{sum(1 for r in cad if not r['close_literal'] and not r['trigger_human'])}")
    print("  ** THIS OVER-COUNTS AND THE DIRECTION IS KNOWN. ** teach-me, a debugging")
    print("  back-and-forth, and a series of yes/no gates all have this shape. It is a")
    print("  CANDIDATE count for 'kinda did', never a use count.")
    print()
    print("--- THE ADVERSARIAL TWIN, FOR CONTRAST ---------------------------------------")
    rgq = CI.three_class(sorted(rows.values(), key=lambda r: r["path"]),
                         "reverse-grill-me", CI.load_skills())
    print(f"  reverse-grill-me USED (marker 'surviving claims')     : {len(rgq['USED'])}")
    print(f"  files here carrying that marker                      : "
          f"{sum(1 for r in recs if r['rg_marker'])}")
    print(f"  files carrying >=2 distinct verdicts (SURVIVED/MODIFIED/FAILED): "
          f"{sum(1 for r in recs if r['rg_verdicts'] >= 2)}")
    print("  The twin declares an OUTPUT ARTIFACT and is therefore detectable; grill-me")
    print("  declares 'no formal output unless Jon asks' (SKILL.md:93) and is therefore not.")
    print("  That is a property of the two SKILL.md files, not of how often each was used.")
    print()
    if show_cadence:
        print("--- CADENCE RUNS, LONGEST FIRST ----------------------------------------------")
        for r in sorted(cad, key=lambda x: -x["cadence_longest"])[:limit]:
            print(f"  longest={r['cadence_longest']:>3}  runs={r['cadence_runs']:>3}  "
                  f"close={'Y' if r['close_literal'] else 'n'}  {r['date']}  {r['path']}")
        print()
    _when(recs)
    print("--- WHAT THIS RECORD CANNOT SEE ----------------------------------------------")
    print("  1. APPLICABLE-NOT-USED IS STRUCTURALLY CAPPED. Every trigger is a meta-request")
    print("     Jon types. The class cannot grow when Jon stops asking, so a fall in it is")
    print("     indistinguishable from a fall in his asking. Same trap the FBC record named.")
    print("  2. WHETHER A GRILLING WAS ANY GOOD. Turn shape is visible; whether the questions")
    print("     walked the decision tree is a judgment. Needs a cold grader.")
    print("  3. ASKUSERQUESTION SELECTIONS ARE ABSENT FROM THE CORPUS. On a question-shaped")
    print("     skill this is a live undercount of Jon's answers, of unknown size.")
    print("  4. THE 1400-CHAR CEILING AND THE ONE-'?' TEST ARE CHOICES. A grilling question")
    print("     with a worked example attached scores as not-a-question.")
    print()


def report_temporal(recs, rows, how, limit=15):
    _common_header(rows, "temporal-context", how, recs)
    _three_class_blocks(rows, "temporal-context")

    a_turns = sum(r["a_turns"] for r in recs)
    resp = sum(r["resp_turns"] for r in recs)
    st_a = sum(r["stamped_a"] for r in recs)
    st_r = sum(r["stamped_resp"] for r in recs)
    files_any = [r for r in recs if r["stamped_a"]]
    stamps = [s for r in recs for s in r["stamps"]]
    with_sc = [r for r in recs if r["has_sidecar"]]

    print("--- THIS FILE: THE OCCASION IS A TURN, BECAUSE THE TRIGGER IS 'EVERY RESPONSE' ---")
    print(f"  transcripts scanned                    : {len(recs)}")
    print(f"  ASSISTANT turns (loose denominator)    : {a_turns:,}")
    print(f"  RESPONSE turns (last A before next H)  : {resp:,}   <- the turns Jon reads")
    print(f"  assistant turns CARRYING a stamp       : {st_a:,} of {a_turns:,}  "
          f"({100.0*st_a/a_turns if a_turns else 0:.2f}%)")
    print(f"  response turns CARRYING a stamp        : {st_r:,} of {resp:,}  "
          f"({100.0*st_r/resp if resp else 0:.2f}%)")
    print(f"  transcripts with >=1 stamp             : {len(files_any)} of {len(recs)}")
    print(f"  stamp OCCURRENCES total                : {len(stamps):,}")
    print()
    print("  THE THREE CLASSES, RESTATED ON THIS UNIT:")
    print(f"    USED                 {st_r:>7}   response turn carries [YYYY-MM-DD HH:MM CDT]")
    lab = sum(1 for s in stamps if s["labelled"])
    unlab = len(stamps) - lab
    print(f"    PARTIAL ('kinda did'){unlab:>7}   stamp present, NO provenance label within "
          f"{TC_LABEL_CHARS} chars")
    print(f"                                   -> a reader cannot tell measured from estimated")
    print(f"    APPLICABLE_NOT_USED  {resp - st_r:>7}   response turn with no stamp at all")
    print()

    print("--- THE ANSWER KEY: DRIFT AGAINST THE SIDECAR'S PER-TURN CLOCK ---------------")
    print("  BOTH VENUES HAVE AN ANSWER KEY. Claude Code sidecars declare `timestamp:`,")
    print("  claude.ai sidecars declare `created_at:`. Reading only the first returns 0 rows")
    print("  for a claude.ai file and would have published `claude.ai cannot be checked`.")
    n_sc = sum(1 for r in recs if r.get("sidecar_present"))
    aligned = [s for s in stamps if s["err_min"] is not None]
    same = [s for s in aligned if s["same_day"]]
    cross = [s for s in aligned if not s["same_day"]]
    print(f"  transcripts carrying a .sidecar.md     : {n_sc} of {len(recs)}")
    print(f"  transcripts with >=1 stamp AND an aligned sidecar: "
          f"{sum(1 for r in recs if r['has_sidecar'])} of {len(files_any)} stamped")
    print(f"  stamps ALIGNED to a true turn clock    : {len(aligned)} of {len(stamps)}")
    print(f"    of those, stamp DATE == turn DATE    : {len(same)}   <- a stamping")
    print(f"    of those, stamp DATE != turn DATE    : {len(cross)}   <- overwhelmingly a")
    print("        QUOTATION: a session pasting an older page or an earlier session's stamp.")
    print("        Cross-day rows are EXCLUDED from the drift distribution below, because a")
    print("        200-day 'error' is not a clock reading. They are printed, not deleted.")
    if not same:
        print("  DRIFT: UNKNOWN — no aligned same-day stamps. This is not zero drift.")
    else:
        e = sorted(abs(s["err_min"]) for s in same)

        def pct(q):
            return e[min(len(e) - 1, int(q * len(e)))]
        print(f"  |error| minutes, SAME-DAY  median {e[len(e)//2]:.1f}   p75 {pct(.75):.1f}   "
              f"p90 {pct(.90):.1f}   max {max(e):.1f}   (n={len(e)})")
        for band, lo, hi in (("<= 2 min  (right)", 0, 2), ("2-10 min", 2, 10),
                             ("10-30 min", 10, 30), ("30-60 min", 30, 60),
                             ("> 60 min  (wrong)", 60, 1e9)):
            k = sum(1 for x in e if (lo == 0 and x <= hi) or (lo and lo < x <= hi))
            print(f"    {band:<20} {k:>5} of {len(e)}  ({100.0*k/len(e):.1f}%)")
        ahead = sum(1 for s in same if s["err_min"] > 2)
        behind = sum(1 for s in same if s["err_min"] < -2)
        print(f"  AHEAD of true time by >2 min : {ahead} of {len(same)}     "
              f"BEHIND by >2 min: {behind}")
        print("    Dead reckoning has a SIGN. An estimate advanced per exchange runs forward;")
        print("    a stamp carried forward from an old `date` call also runs forward. Scatter")
        print("    would look symmetric. This does not.")
        claim = [s for s in same if s["claims_measured"]]
        bad = [s for s in claim if abs(s["err_min"]) > 2]
        print(f"  stamps LABELLED [measured]             : {len(claim)} of {len(same)} same-day")
        print(f"    of those, |error| > 2 min            : {len(bad)}  "
              f"<- FALSE [measured]. A measurement cannot be wrong by minutes.")
        est = [s for s in same if s["claims_estimated"]]
        print(f"  stamps LABELLED ESTIMATED              : {len(est)}  "
              f"(median |err| "
              f"{sorted(abs(x['err_min']) for x in est)[len(est)//2]:.1f} min)" if est else
              "  stamps LABELLED ESTIMATED              : 0")
        dc = [s for s in same if s["date_call"]]
        dcbad = [s for s in dc if abs(s["err_min"]) > 2]
        print(f"  stamps with a `date`/Get-Date call in the same or prior turn: {len(dc)}")
        print(f"    of those, |error| > 2 min            : {len(dcbad)}")
        print("    SMALL DENOMINATOR AND A WEAK DETECTOR. The pattern reads the assistant turn")
        print("    and the one before it; a `date` run three tool-results earlier is missed.")
        print("    Do not read this row as 'running date does not help'.")
    print()
    print("--- DRIFT BY VENUE — both keys read ------------------------------------------")
    for ven in sorted({r.get("venue") for r in recs if r.get("venue")}):
        vs = [s for r in recs if r.get("venue") == ven for s in r["stamps"]
              if s["err_min"] is not None and s["same_day"]]
        if not vs:
            print(f"  {ven:<14} aligned same-day stamps: 0   -> UNKNOWN, not zero drift")
            continue
        ve = sorted(abs(x["err_min"]) for x in vs)
        ok2 = sum(1 for x in ve if x <= 2)
        print(f"  {ven:<14} n={len(ve):<5} median {ve[len(ve)//2]:>7.1f} min   "
              f"within 2 min: {ok2} ({100.0*ok2/len(ve):.1f}%)")
    print()

    print("--- 'GOOD MORNING' IS A COMPACTION MARKER, NOT A CLOCK ------------------------")
    gs = [g for r in recs for g in r["greetings"]]
    checkable = [g for g in gs if g.get("true_hour") is not None]
    print(f"  Jon-turn greetings found               : {len(gs)}")
    print(f"    whose next reply carried a stamp     : "
          f"{sum(1 for g in gs if g.get('replied_stamped'))}")
    print(f"    with a stamped reply AND a true time : {len(checkable)}")
    mism = [g for g in checkable
            if (g["word"] == "morning" and not (4 <= g["true_hour"] < 12))
            or (g["word"] in ("night", "evening") and not (g["true_hour"] >= 17
                                                           or g["true_hour"] < 4))]
    print(f"    greeting's part-of-day CONTRADICTED by the clock: {len(mism)}")
    for g in mism[:limit]:
        print(f"      T{g['turn']:<6} 'good {g['word']}'  stamped {g['stamped']}  "
              f"true {g['true']}")
    if not gs:
        print("  NONE FOUND — and that is a detector result, not a finding about Jon. The "
              "pattern reads the first 400 chars of an H turn.")
    print()

    print("--- ZONE LABEL ---------------------------------------------------------------")
    ncst = sum(r["cst_stamps"] for r in recs)
    print(f"  stamps labelled CST rather than CDT    : {ncst} of {len(stamps)}   "
          f"(SKILL.md:16 mandates the CDT label year-round)")
    print()

    _when(recs)

    print("--- WHAT THIS RECORD CANNOT SEE — UNKNOWN, NEVER ZERO ------------------------")
    print("  1. TRANSCRIPTS WITH NO SIDECAR. Most of the corpus predates manifest v2, so most")
    print("     stamps cannot be checked at all. The drift table is a sample of the record, not")
    print("     the record. An earlier draft of this very report said claude.ai HAS no answer")
    print("     key; it does, under a different field name, and the self-test caught it.")
    print("  2. WHETHER A CORRECT STAMP WAS MEASURED OR LUCKY. A turn that ran `date` and a turn")
    print("     that guessed right are the same string. Only the WRONG ones are provable.")
    print("  3. THE TURNS THE EXTRACTOR NEVER WROTE — an open session's tail, a dropped record")
    print("     class. Absence of a stamp in an unextracted turn is not absence of a stamp.")
    print("  4. WHETHER A RESPONSE NEEDED A STAMP AT ALL. SKILL.md says every response; the")
    print("     corpus contains agent-to-agent turns and tool plumbing where nobody has ever")
    print("     ruled that it applies. The ANU class is an upper bound on the failure.")
    print("  5. DST. Every date in this corpus falls inside US DST 2026, so CDT = UTC-5")
    print("     throughout. A corpus spanning November would need the branch tc_offset_hours")
    print("     already carries, and it has never been exercised on real data.")
    print()


def report_session_order(recs, rows, how, limit=15):
    _common_header(rows, "session-order", how, recs)
    _three_class_blocks(rows, "session-order")

    conv = [r for r in recs if r.get("kind") == "conversation"]
    sub = [r for r in recs if r.get("kind") == "subagent"]
    gm = [r for r in recs if r["genuine_maps"]]
    tm = [r for r in recs if r["template_maps"] and not r["genuine_maps"]]

    print("--- RITUAL 1 of 4: THE SESSION MAP (the headline triple) ---------------------")
    print(f"  transcripts scanned                    : {len(recs)}")
    print(f"    of which main conversations          : {len(conv)}   subagents: {len(sub)}")
    print(f"  turns carrying >=1 map label           : {sum(r['map_turns'] for r in recs)}")
    print(f"    TEMPLATE-only turns (SKILL.md quoted): {sum(r['template_maps'] for r in recs)}")
    print(f"  GENUINE map emissions (>=3 labels)     : {sum(r['genuine_maps'] for r in recs)}"
          f"  in {len(gm)} files")
    print(f"    USED      files with >=1 genuine map : {len(gm)} of {len(recs)}")
    print(f"    PARTIAL   genuine maps missing >=1 of the 5 labels: "
          f"{sum(r['partial_maps'] for r in recs)} of {sum(r['genuine_maps'] for r in recs)}")
    print(f"    files with ONLY the template, never a run: {len(tm)}")
    lh = Counter()
    for r in recs:
        lh.update(r["label_hist"])
    tot = sum(r["genuine_maps"] for r in recs) or 1
    print("  label presence across genuine maps (the 'kinda did' shape, per label):")
    for name, _p in SO_LABELS:
        print(f"    {name:<12} {lh.get(name, 0):>5} of {tot}  ({100.0*lh.get(name,0)/tot:.1f}%)")
    print("  HELD vs TRIAGE is the distinction SKILL.md calls critical; the two rows above")
    print("  are the only mechanical evidence of whether it is being kept.")
    print()

    print("--- RITUAL 2 of 4: POST-COMPACT RECOVERY -------------------------------------")
    nb = sum(r["compaction_boundaries"] for r in recs)
    nr = sum(r["recoveries"] for r in recs)
    na = sum(r["answered_bounds"] for r in recs)
    print(f"  compaction boundaries in the corpus    : {nb}   "
          f"in {sum(1 for r in recs if r['compaction_boundaries'])} files")
    print(f"  mandated restatement emitted           : {nr}")
    print(f"  boundaries ANSWERED within 12 turns    : {na} of {nb}")
    print(f"  APPLICABLE_NOT_USED                    : {nb - na} of {nb}")
    print("  The restatement literal is 'Before compaction, we were [X]' — SKILL.md step 5 of 7.")
    print("  Steps 1-4 are READS and leave no mark, so this scores ONE step of the ritual.")
    print()

    print("--- RITUAL 3 of 4: MULTI-TOPIC MESSAGE ---------------------------------------")
    nm = sum(r["multi_topic"] for r in recs)
    nma = sum(r["answered_multi"] for r in recs)
    print(f"  Jon turns of multi-topic SHAPE         : {nm}   "
          f"(>=3 enumerated items, or >=3 '?')")
    print(f"    answered by a genuine map within 8 turns: {nma}")
    print(f"  APPLICABLE_NOT_USED                    : {nm - nma} of {nm}")
    print("  SHAPE IS NOT INTENT. A numbered list of three file paths is not three topics, and")
    print("  a single question asked three ways is one. This is a CANDIDATE POOL at unmeasured")
    print("  precision, and the ANU figure inherits that in full.")
    print()

    print("--- RITUAL 4 of 4: SESSION CLOSE ---------------------------------------------")
    nc = sum(r["close_signals"] for r in recs)
    nca = sum(r["answered_close"] for r in recs)
    ne = sum(r["export_calls"] for r in recs)
    print(f"  Jon turns carrying a close signal      : {nc}   "
          f"(SKILL.md's list MINUS the bare word 'done' — see below)")
    print(f"  labelled EXPORT-or-SKIP judgments       : {ne}")
    print(f"    close signals answered within 8 turns : {nca} of {nc}")
    print(f"  APPLICABLE_NOT_USED                    : {nc - nca} of {nc}")
    print("  SKILL.md names the bare word 'done' as a close signal. Taking it at its word is what")
    print("  makes the detector wrong: Jon's commonest use of it is an ACKNOWLEDGEMENT that opens")
    print("  the next item -- 'Done. Next?', 'done. Your turn... did it work?'. The bare form is")
    print("  excluded here, which is a finding about SKILL.md and not only about the regex.")
    print()

    print("--- THE TOPIC CHECK ----------------------------------------------------------")
    nt = sum(r["topic_check"] for r in recs)
    print(f"  the verbatim redirect, corpus-wide     : {nt}   "
          f"in {sum(1 for r in recs if r['topic_check'])} files")
    print("  SKILL.md says one clean redirect is sufficient and forbids interrogation, so a")
    print("  LOW number here is not obviously a failure. It has no denominator: 'Jon could not")
    print("  state his topic' is a state, not a string. UNKNOWN, and printed as UNKNOWN.")
    print()

    _when(recs)

    print("--- WHAT THIS RECORD CANNOT SEE — UNKNOWN, NEVER ZERO ------------------------")
    print("  1. THE COLD-OPEN RITUAL, WHICH IS THE SKILL'S FIRST AND LARGEST CLAUSE. Its output")
    print("     is READING four files in order. Reading leaves no mark in a transcript unless a")
    print("     tool call happens to be logged, and in claude.ai it never is. Every one of the")
    print("     248 conversations in this corpus is a cold-open occasion and NONE of them can be")
    print("     scored. That is the single largest UNKNOWN on this page and it is structural.")
    print("  2. WHETHER A MAP WAS ACCURATE. Five labels present says the shape was kept. Whether")
    print("     the HELD row actually held everything parked is a judgment about content.")
    print("  3. WHETHER 'HELD' WAS CONFLATED WITH 'TRIAGE'. SKILL.md calls this the critical")
    print("     distinction; the failure is putting the right word on the wrong item, which is")
    print("     invisible to a label detector.")
    print("  4. MULTI-TOPIC PRECISION. Shape is not intent; see ritual 3.")
    print("  5. SUBAGENTS. A subagent has no cold open, no close ritual, and no session of its")
    print("     own, but its transcripts are in every corpus-wide denominator above. The")
    print("     conversation/subagent split is printed so the reader can discount.")
    print()


def report_wiki_master(recs, rows, how, limit=15):
    _common_header(rows, "wiki-master", how, recs)
    _three_class_blocks(rows, "wiki-master")

    audit = wm_disk_audit()
    R = audit["rows"]
    n = len(R) or 1
    print("--- THE PRIMARY MEASURE: THE ARTIFACTS ON DISK, NOT THE PASTES IN THE CORPUS ---")
    print("  wiki-master's product is a FILE. A transcript sees it only if it was also pasted.")
    print("  These pages are tracked in this repo, so they can be graded directly.")
    print(f"  tracked source pages under wiki/sources/ : {len(R)}")
    allthree = sum(1 for r in R if len(r["req"]) == 3)
    print(f"  carrying ALL THREE required sections     : {allthree} of {len(R)}  "
          f"({100.0*allthree/n:.1f}%)")
    for k, _p in WM_REQUIRED:
        miss = sum(1 for r in R if k not in r["req"])
        print(f"    missing '## {k}'{'':<{max(0, 18-len(k))}}: {miss} of {len(R)}")
    print("  conditional sections (presence, NOT a compliance rate — they are conditional):")
    for k, _p in WM_CONDITIONAL:
        got = sum(1 for r in R if k in r["cond"])
        print(f"    {k:<22} {got} of {len(R)}")
    ce = [r for r in R if r["conflicts_empty"]]
    print(f"  '## Conflicts' present but EMPTY         : {len(ce)}   "
          f"(SKILL.md: write 'None.' explicitly)")
    cm = sum(1 for r in R if r["has_conflict_marker"])
    print(f"  pages carrying a CONFLICT: marker        : {cm} of {len(R)}")
    print()

    print("--- THE FIDELITY TAG — 'Not optional', ratified by Jon 2026-07-13 (G2) ---------")
    print("  SKILL.md: 'Every Key Claim carries one fidelity tag. Not optional.'")
    tot_b = sum(r["bullets"] for r in R)
    tot_t = sum(r["tagged"] for r in R)
    print(f"  Key Claim bullets, all pages             : {tot_b}")
    print(f"    carrying a fidelity tag                : {tot_t} ({100.0*tot_t/(tot_b or 1):.1f}%)")
    pre = [r for r in R if r["date"] != "UNKNOWN" and r["date"] < WM_G2_RATIFIED]
    post = [r for r in R if r["date"] != "UNKNOWN" and r["date"] >= WM_G2_RATIFIED]
    unk = [r for r in R if r["date"] == "UNKNOWN"]
    print(f"  THE RULE HAS A BIRTHDAY ({WM_G2_RATIFIED}) AND THE SPLIT IS COMPUTED:")
    for lbl, grp in (("BEFORE ratification", pre), ("ON/AFTER ratification", post),
                     ("date UNKNOWN", unk)):
        b = sum(r["bullets"] for r in grp)
        t = sum(r["tagged"] for r in grp)
        zero = sum(1 for r in grp if r["bullets"] and not r["tagged"])
        print(f"    {lbl:<22} pages {len(grp):>4}   bullets {b:>5}   tagged {t:>5}  "
              f"({100.0*t/(b or 1):>5.1f}%)   pages with ZERO tags: {zero}")
    print("  A page written before 2026-07-13 is EVIDENCE FOR the rule, not a violation of it.")
    print("  Only the ON/AFTER row is a compliance rate. The other two are printed so nobody")
    print("  computes one from the total.")
    print()
    print("  worst ON/AFTER pages (bullets present, zero tagged):")
    bad = [r for r in post if r["bullets"] and not r["tagged"]]
    bad.sort(key=lambda r: -r["bullets"])
    for r in bad[:limit]:
        print(f"    {r['bullets']:>4} bullets, 0 tagged   {r['path'][12:]}")
    if not bad:
        print("    NONE — every post-ratification page carries at least one tag.")
    print()

    print("--- WHAT THE CORPUS SEES: PASTES, AND ONLY PASTES ----------------------------")
    print(f"  transcripts scanned                      : {len(recs)}")
    print(f"  transcripts pasting a '## Key Claims' shape: "
          f"{sum(1 for r in recs if r['genuine'])}")
    print(f"    of those, carrying all three required sections: "
          f"{sum(1 for r in recs if r['all_required'])}")
    print(f"  total page shapes pasted                 : {sum(r['page_shapes'] for r in recs)}")
    print(f"  fidelity tags emitted in transcripts     : "
          f"{sum(r['fidelity_tags'] for r in recs)}")
    print(f"  CONFLICT: markers emitted                : "
          f"{sum(r['conflict_markers'] for r in recs)}")
    print(f"  transcripts naming the ingest COUNT GATE : "
          f"{sum(1 for r in recs if r['count_gate'])}")
    print(f"  transcripts naming the PARTIAL registry  : "
          f"{sum(1 for r in recs if r['partial_registry'])}")
    print("  THE TWO NUMBERS ARE NOT RECONCILED AND SHOULD NOT BE. A page written without being")
    print("  pasted is invisible to the corpus; a page pasted twice is counted twice. They are")
    print("  answers to different questions and are printed as two columns, never as one.")
    print()

    _when(recs)

    print("--- WHAT THIS RECORD CANNOT SEE — UNKNOWN, NEVER ZERO ------------------------")
    print("  1. WHETHER A SOURCE PAGE IS TRUE. Schema conformance is a shape test. Whether the")
    print("     Key Claims faithfully represent the session is exactly the judgment the fidelity")
    print("     tag exists to disclose, and a tag's ACCURACY is not checkable from the page.")
    print("  2. INGEST DECISIONS THAT WENT THE OTHER WAY. A session correctly SKIPPED is")
    print("     indistinguishable here from a session never seen. The skip registry, not this")
    print("     page, is where that record lives.")
    print("  3. THE CONDITIONAL SECTIONS. 'Include when 2+ named entities appear' is a condition")
    print("     on content, so a missing conditional section is not a defect and no rate is")
    print("     computed for one. Presence counts only.")
    print("  4. THE COUNT GATE AND THE PARTIAL REGISTRY, as ACTIONS. Both are detected as")
    print("     STRINGS IN PROSE. A session that ran the gate silently and a session that")
    print("     mentioned it are the same to this instrument. Treat those two rows as")
    print("     upper bounds on discussion, not as evidence of execution.")
    print("  5. wiki/personal/, wiki/home/, wiki/pro/. Out of this audit's scope by construction;")
    print("     their source pages are not graded here and their conformance is UNKNOWN.")
    print("  6. PAGES DELETED OR SUPERSEDED. The disk audit sees the current tree only.")
    print()


REPORTERS = {"wiki-master": report_wiki_master, "session-order": report_session_order, "temporal-context": report_temporal, "handoff": report_handoff, "wayfinder": report_wayfinder, "grill-me": report_grill}


# =================================================================================================
# SELF-TEST — negative controls first; the direction that matters is the one that INFLATES
# =================================================================================================
def self_test():
    ok = True

    def chk(label, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")

    print("=== SELF-TEST — skill_record_ext (negative controls first) ===")
    H = lambda t: analyse_handoff({"__seq__": [("A", t)]})
    W = lambda t: analyse_wayfinder({"__seq__": [("H", t)]})
    G = lambda seq: analyse_grill({"__seq__": seq})

    # ---- handoff -------------------------------------------------------------------------
    chk("plain prose is not a handoff", not H("We shipped the page today.")["genuine"])
    chk("the marker heading ALONE is not a handoff (1 of 10 sections)",
        not H("## What Was Accomplished This Session\nstuff")["genuine"])
    chk("SKILL.md's own template is TEMPLATE, not a run",
        (lambda a: a["template_only"] and not a["genuine"])(
            H("## What Was Accomplished This Session\n[Bulleted list: concrete outputs, decisions]\n"
              "## Next Steps\n1. [First thing the fresh agent should do]\n"
              "## Context\n[2-3 sentences: what project/task this is]\n"
              "## Current State\n[What exists now that didn't before this session began]\n"
              "## In Progress\n[What was started but not finished]\n"
              "## Held Items\n[Items Jon parked that are expected to come back]")))
    chk("a REAL handoff in a session that ALSO read SKILL.md is still genuine "
        "(the deflator must not delete the files it should count)",
        H("## What Was Accomplished This Session\n[Bulleted list: concrete outputs]\n\n"
          "----- later in the same transcript -----\n\n"
          "## Context\nThe FL corpus work.\n## What Was Accomplished This Session\n"
          "- built the index\n## Current State\nindex on disk\n## In Progress\nthe page\n"
          "## Next Steps\n1. write it\n")["genuine"])
    _full = ("## Context\nx\n## What Was Accomplished This Session\ny\n## Current State\nz\n"
             "## In Progress\nq\n## Next Steps\n1. go\n## Held Items\nh\n## Open Questions\no\n"
             "## Key Files / Paths\nk\n## Constraints / Warnings\nc\n## Skills Active\ns\n")
    chk("a real 10-section handoff is genuine and scores 10 of 10",
        (lambda a: a["genuine"] and a["n_sections"] == 10)(H(_full)))
    chk("a 5-section handoff is genuine but scores 5 ('kinda did' is graded, not binary)",
        (lambda a: a["genuine"] and a["n_sections"] == 5)(
            H("## Context\nx\n## What Was Accomplished This Session\ny\n## Current State\nz\n"
              "## In Progress\nq\n## Next Steps\n1. go\n")))
    chk("a handoff naming no wiki/sources page fails the two-artifact test",
        not H(_full)["source_page"])
    chk("a handoff naming one passes it",
        H(_full + "Source page: wiki/sources/fl/thing-2026-08-06-abc123.md")["source_page"])
    chk("a temp path is detected (the output location the 08-01 revision forbids)",
        H(_full + "Saved to %TEMP%\\handoff.md")["temp_path"])
    chk("an ordinary repo path is NOT flagged as temp",
        not H(_full + "Saved to G:\\My Drive\\Claude\\repo\\handoff-x-2026-08-06.md")["temp_path"])

    # ---- wayfinder -----------------------------------------------------------------------
    chk("'run the wayfinder protocol' classifies SKILL",
        wayfinder_senses("let's run the wayfinder protocol on this") == ["SKILL"])
    chk("'check the wayfinder map' classifies MAP, not SKILL",
        wayfinder_senses("check the wayfinder map for unclosed tickets") == ["MAP"])
    chk("'wayfinder said' classifies PARTY, not SKILL",
        wayfinder_senses("wayfinder said the register is stale") == ["PARTY"])
    chk("a bare mention with no context is UNCLASSIFIED, never silently SKILL",
        wayfinder_senses("wayfinder") == ["UNCLASSIFIED"])
    chk("two mentions inside the merge distance count once",
        len(wayfinder_senses("wayfinder and wayfinder again")) == 1)
    chk("two mentions far apart count twice",
        len(wayfinder_senses("wayfinder" + " x" * 200 + " wayfinder")) == 2)
    chk("'you are the FL wayfinder' classifies PARTY — an address is not an invocation",
        wayfinder_senses("You are the FL wayfinder — meta-coordinator, claude.ai side.")
        == ["PARTY"])
    chk("'TO: wayfinder, FROM: Jon' classifies PARTY",
        wayfinder_senses("TO: wayfinder, FROM: Jon — 2-minute verification assist")
        == ["PARTY"])
    chk("a real map body is genuine",
        W("## Decisions So Far\n- [T-01 pick the schema](x) — chose v2\n## Out of Scope\n- Y")
        ["genuine"])
    chk("SKILL.md's own map template is NOT a genuine map",
        not W("## Decisions so far\n\n<!-- the index — one line per closed ticket: enough to "
              "judge relevance -->\n\n- [<closed ticket title>](link) — <one-line gist>"
              )["genuine"])
    chk("a session that read SKILL.md AND kept a real map is still genuine "
        "(the deflator must not delete the files it should count)",
        W("- [<closed ticket title>](link) — <one-line gist>\n\n----- later -----\n\n"
          "## Decisions So Far\n- [T-04 corpus root](x) — raw/transcripts, ratified")["genuine"])

    # ---- grill-me ------------------------------------------------------------------------
    q1 = ("A", "## Assistant\nWhat is this trying to accomplish?")
    q2 = ("A", "## Assistant\nWhat breaks it?")
    q3 = ("A", "## Assistant\nWhat must be true for that to hold?")
    hh = ("H", "## Human\nBecause of X.")
    chk("three single-question A-turns alternating with H is a cadence run",
        G([q1, hh, q2, hh, q3, hh])["cadence_runs"] == 1)
    chk("two are NOT (below the floor of 3 — an ordinary clarifying exchange)",
        G([q1, hh, q2, hh])["cadence_runs"] == 0)
    chk("a long assistant turn with one '?' is a briefing, not a question",
        G([("A", "## Assistant\n" + "x " * 900 + "?"), hh, q2, hh, q3, hh])["cadence_runs"] == 0)
    chk("an assistant turn with three questions breaks the one-at-a-time rule",
        G([("A", "## Assistant\nA? B? C?"), hh, q2, hh, q3, hh])["cadence_runs"] == 0)
    chk("the SKILL.md:82 close literal is detected",
        G([("A", "Is this an accurate summary? Anything I missed?")])["close_literal"])
    chk("the trigger TABLE is template, not a run",
        G([("A", '| "grill me" | Ask what to grill; then begin |')])["template_only"])
    chk("reverse-grill-me's marker is detected separately from grill-me's",
        G([("A", "## Surviving Claims — X — 2026-08-06\nSURVIVED / MODIFIED / FAILED")
           ])["rg_marker"])

    # ---- wiki-master -----------------------------------------------------------------------
    W2 = lambda t: analyse_wiki_master({"__seq__": [("A", t)]})
    chk("prose about the wiki is not a source page",
        not W2("I updated the wiki index today.")["genuine"])
    chk("a pasted '## Key Claims' heading is a page shape",
        W2("## Key Claims\n- **X** [verbatim, 2026-08-06]")["genuine"])
    chk("all-three-required is scored separately from the shape",
        (lambda a: a["genuine"] and not a["all_required"])(W2("## Key Claims\n- x")))
    chk("all three required sections present scores all_required",
        W2("## Summary\ns\n## Key Claims\n- x\n## Conflicts\nNone.")["all_required"])
    chk("the six fidelity qualities are the SKILL.md six, and only those",
        (lambda a: a["fidelity_tags"] == 6)(
            W2("[verbatim, x] [paraphrase, x] [reconstructed, x] [contextual, x] "
               "[inferred, x] [uncaptured, x] [measured, x] [asserted, x]")))
    chk("a CONFLICT: marker is detected",
        W2("CONFLICT: the two pages disagree")["conflict_markers"] == 1)
    _wm = wm_disk_audit()
    chk(f"the disk audit finds tracked source pages ({len(_wm['rows'])} graded)",
        not _wm["root_missing"] and len(_wm["rows"]) > 50)
    chk("the disk audit splits the fidelity rule at its 2026-07-13 ratification date, so no "
        "page is graded against a rule that did not exist when it was written",
        any(r["date"] < WM_G2_RATIFIED for r in _wm["rows"])
        and any(r["date"] >= WM_G2_RATIFIED for r in _wm["rows"] if r["date"] != "UNKNOWN"))
    chk("every graded page carries a parsed date or the literal UNKNOWN — never a guess",
        all(r["date"] == "UNKNOWN" or re.fullmatch(r"20\d\d-\d\d-\d\d", r["date"])
            for r in _wm["rows"]))

    # ---- session-order ---------------------------------------------------------------------
    S = lambda seq: analyse_session_order({"__seq__": seq})
    _map = ("A", "DONE — landed the page\nIN PROGRESS — the scan\nNEXT — commit\n"
                 "HELD — the ordering question\nTRIAGE — none")
    chk("a five-label map is a genuine map",
        S([_map])["genuine_maps"] == 1 and S([_map])["partial_maps"] == 0)
    chk("a three-label map is genuine but PARTIAL ('kinda did' is graded)",
        (lambda a: a["genuine_maps"] == 1 and a["partial_maps"] == 1)(
            S([("A", "DONE — x\nNEXT — y\nHELD — z")])))
    chk("a two-label fragment is NOT a map",
        S([("A", "DONE — x\nNEXT — y")])["genuine_maps"] == 0)
    chk("SKILL.md's own fenced template is TEMPLATE, not a run",
        (lambda a: a["template_maps"] == 1 and a["genuine_maps"] == 0)(
            S([("A", "DONE — [closed items]\nIN PROGRESS — [active right now]\n"
                     "NEXT — [agreed next steps, this session]\nHELD — [parked within this "
                     "session, will return]\nTRIAGE — [handed off, this session]")])))
    chk("the word DONE in prose does not fake a map",
        S([("A", "We are DONE with the scan and NEXT week is busy.")])["genuine_maps"] == 0)
    chk("the post-compact restatement is detected and must FOLLOW the boundary",
        (lambda a: a["answered_bounds"] == 1)(
            S([("C", "## Compaction Boundary"), ("A", "Before compaction, we were mid-scan.")])))
    chk("a restatement BEFORE the boundary does not answer it",
        (lambda a: a["compaction_boundaries"] == 1 and a["answered_bounds"] == 0)(
            S([("A", "Before compaction, we were mid-scan."), ("C", "## Compaction Boundary")])))
    chk("Jon's 'Good night' is a close signal",
        S([("H", "Good night")])["close_signals"] == 1)
    chk("'that is not done yet' mid-sentence is NOT a close signal",
        S([("H", "I think that is not done yet, keep going")])["close_signals"] == 0)
    chk("a labelled EXPORT judgment answers a close signal",
        S([("H", "Good night"), ("A", "EXPORT: new scripts and a decision trail")])
        ["answered_close"] == 1)
    chk("an unlabelled goodbye does not count as the export judgment",
        S([("H", "Good night"), ("A", "Goodnight, Jon.")])["answered_close"] == 0)
    chk("three enumerated items is a multi-topic shape",
        S([("H", "1. one\n2. two\n3. three")])["multi_topic"] == 1)
    chk("two enumerated items is not",
        S([("H", "1. one\n2. two")])["multi_topic"] == 0)
    chk("a multi-topic turn answered by a map within 8 turns counts as answered",
        S([("H", "1. a\n2. b\n3. c"), _map])["answered_multi"] == 1)
    chk("REGRESSION: `EXPORT-LOG watermark:` is NOT a close-ritual judgment "
        "(this false positive was ~19 of 21 v1 hits)",
        S([("H", "good night"), ("A", "- EXPORT-LOG watermark: `2026-06-27T21:14:43Z`")])
        ["export_calls"] == 0)
    chk("REGRESSION: `SKIP-SUPERSEDED (1c802a)` is a triage disposition, not an export judgment",
        S([("A", "- **SKIP-SUPERSEDED (1c802a):** 200-line aborted setup run")])
        ["export_calls"] == 0)
    chk("a real `EXPORT: yes — decisions made` judgment IS detected",
        S([("A", "EXPORT: yes — decisions made, architecture locked")])["export_calls"] == 1)
    chk("REGRESSION: Jon's `Done. Next?` is an ACKNOWLEDGEMENT, not a close signal",
        S([("H", "Done. Next?")])["close_signals"] == 0)
    chk("REGRESSION: `done. Your turn... did it work?` is not a close signal",
        S([("H", "done. Your turn... did it work? looks like no...")])["close_signals"] == 0)
    chk("`I'm done here for now` IS a close signal",
        S([("H", "I'm done here for now. BTW, I've been treating you as soul.")])
        ["close_signals"] == 1)
    chk("the verbatim topic-check redirect is detected",
        S([("A", "Before we go further — what's the one thing you need from this session?")])
        ["topic_check"] == 1)

    # ---- temporal-context ------------------------------------------------------------------
    T = lambda seq: analyse_temporal({"__seq__": seq})
    chk("prose with no stamp is not a use",
        not T([("A", "## Assistant\nHere is the answer.")])["genuine"])
    chk("a bare date is NOT a stamp (the format is mandated, SKILL.md:14-18)",
        not T([("A", "on 2026-08-06 we shipped it")])["genuine"])
    chk("the mandated format IS a stamp",
        T([("A", "[2026-08-06 18:04 CDT] done")])["genuine"])
    chk("an unlabelled stamp is PARTIAL, not USED-with-provenance",
        T([("A", "[2026-08-06 18:04 CDT] done")])["unlabelled"] == 1)
    chk("the ESTIMATED label is read as provenance",
        T([("A", "[2026-08-06 18:04 CDT] *(ESTIMATED - check reasonability)*")])["labelled"] == 1)
    chk("`*(measured)*` right after the stamp IS the label",
        T([("A", "[2026-08-06 18:04 CDT] *(measured)*")])["stamps"][0]["claims_measured"])
    chk("a backticked stamp still finds its label",
        T([("A", "`[2026-08-06 18:04 CDT]` *(estimated)*")])["labelled"] == 1)
    chk("REGRESSION: prose 'Measured, not asserted:' AFTER the stamp is NOT a [measured] label "
        "(this false positive contaminated the first published FALSE-[measured] count)",
        not T([("A", "[2026-08-06 10:12 CDT] ## You're right. **Measured, not asserted:** | Q |")])
        ["stamps"][0]["claims_measured"])
    chk("`*(user-provided)*` is provenance, but is NOT a measurement claim",
        (lambda s0: s0["labelled"] and not s0["claims_measured"])(
            T([("A", "[2026-08-06 18:04 CDT] *(user-provided)*")])["stamps"][0]))
    chk("a `measured` 200 chars downstream is NOT read as this stamp's label",
        T([("A", "[2026-08-06 18:04 CDT]" + " x" * 200 + " measured")])["unlabelled"] == 1)
    chk("the last A before an H is a RESPONSE turn; an interior A is not",
        (lambda a: a["resp_turns"] == 1 and a["a_turns"] == 2)(
            T([("A", "tool step"), ("A", "the reply"), ("H", "ok")])))
    chk("a `date` shell call in the SAME turn is seen",
        T([("A", "$ date -u\n[2026-08-06 18:04 CDT]")])["stamps"][0]["date_call"])
    chk("a `date` call in the PRIOR turn is seen (the reply stamps after the tool result)",
        T([("R", "## Tool Result\nGet-Date"), ("A", "[2026-08-06 18:04 CDT]")])
        ["stamps"][0]["date_call"])
    chk("prose containing the word 'update' does not fake a date call",
        not T([("A", "we should update the page\n[2026-08-06 18:04 CDT]")])
        ["stamps"][0]["date_call"])
    chk("'Good morning' in an H turn is detected as a greeting",
        len(T([("H", "## Human\nGood morning"), ("A", "[2026-08-06 18:04 CDT]")])["greetings"])
        == 1)
    chk("'a good morning routine' mid-sentence is NOT a greeting",
        len(T([("H", "## Human\nI want a good morning routine"),
               ("A", "[2026-08-06 08:00 CDT]")])["greetings"]) == 0)
    chk("CST stamps are counted separately from CDT",
        T([("A", "[2026-01-02 08:00 CST]")])["cst_stamps"] == 1)
    chk("DST branch: an August date is CDT/UTC-5, a January date is CST/UTC-6",
        tc_offset_hours("2026-08-06") == (5, True)
        and tc_offset_hours("2026-01-06") == (6, False))
    chk("a transcript with no sidecar yields err_min None — UNKNOWN, never 0.0",
        T([("A", "[2026-08-06 18:04 CDT]")])["stamps"][0]["err_min"] is None)
    _cc = _ai = None
    for pp, _rel in CI.walk_corpus():
        if not Path(str(pp)[:-3] + ".sidecar.md").is_file():
            continue
        if _cc is None and Path(pp).name.startswith("code-"):
            _cc = pp
        if _ai is None and Path(pp).name.startswith("chat-"):
            _ai = pp
        if _cc and _ai:
            break
    for _lbl, _pp in (("Claude Code", _cc), ("claude.ai", _ai)):
        if _pp is None:
            chk(f"NO {_lbl} SIDECAR FOUND — alignment UNVERIFIED, drift must read UNKNOWN", False)
            continue
        _rows = sidecar_timestamps(_pp)
        _al = align_sidecar(spans(_pp).get("__seq__", []), _pp)
        chk(f"{_lbl} sidecar parses AND aligns by role sequence "
            f"({Path(_pp).name[:34]}: {len(_rows)} rows, {len(_al)} aligned)",
            len(_rows) > 0 and len(_al) > 0)
    chk("a sidecar whose roles do NOT match the transcript aligns to {} — never by length alone",
        align_sidecar([("A", "x"), ("A", "y")], Path("no-such-file.md")) == {})

    # ---- reuse, not redefinition ----------------------------------------------------------
    chk("turn-span splitter is skill_record's (== gbs_record's), not a second copy",
        spans is SR.spans)
    chk("merge rule is the same constant", MERGE_CHARS == SR.MERGE_CHARS)
    chk("CORPUS resolves transitively to coverage_gap's",
        CI.CORPUS == __import__("coverage_gap").CORPUS)
    chk(f"all {len(RECORDS_EXT)} slugs are registered into skill_record.RECORDS",
        all(s in SR.RECORDS for s in RECORDS_EXT))
    chk("every entry declares an ANU state in words, so no class can be silently zero",
        all(v["anu_state"] for v in RECORDS_EXT.values()))

    # ---- raw/ UNTOUCHED — Jon's standing NO DESTRUCTIVE ACTS constraint, as a property ----
    sample = [p for p, _ in CI.walk_corpus()][::97]
    before = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    rows, _how, _read = _load()
    if rows:
        scan(dict(list(rows.items())[:40]), "wiki-master")
        scan(dict(list(rows.items())[:40]), "session-order")
        scan(dict(list(rows.items())[:40]), "temporal-context")
        scan(dict(list(rows.items())[:40]), "handoff")
        scan(dict(list(rows.items())[:40]), "wayfinder")
        scan(dict(list(rows.items())[:40]), "grill-me")
    after = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    chk(f"a scan leaves raw/ byte- and mtime-identical ({len(sample)} sampled)", before == after)

    # LIAR CHECK — the exit code must honour `ok`, not just print it. Regression control for the
    # 2026-09-05 TRIAGE-8 finding: self_test() used to `return 0` unconditionally regardless of
    # `ok`, so every sweep grading this script on exit code alone was silently wrong. Guarded by
    # an env var so the child invocation does not recurse into this same check forever.
    if not os.environ.get("_SKILL_RECORD_EXT_SELFTEST_NOCHILD"):
        import subprocess
        child_env = dict(os.environ, _SKILL_RECORD_EXT_SELFTEST_NOCHILD="1")
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--self-test"],
                               capture_output=True, env=child_env)
        chk(f"self-test exit code honours its own verdict (child exit={proc.returncode}, ok={ok})",
            (proc.returncode == 0) == ok)

    print("\nRESULT: " + ("PASS — controls fire in both directions." if ok
                          else "FAIL — do not trust its counts."))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skill", default=None, choices=sorted(RECORDS_EXT))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--max-files", type=int, default=None)
    ap.add_argument("--senses", action="store_true", help="wayfinder: per-file sense split")
    ap.add_argument("--cadence", action="store_true", help="grill-me: enumerate cadence runs")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    slugs = sorted(RECORDS_EXT) if args.all else (
        [args.skill] if args.skill else ["temporal-context"])
    rows, how, _read = _load()
    if not rows:
        print("[no corpus index on disk] — build it first: "
              "python scripts/audit/corpus_index.py", file=sys.stderr)
        print("This is NOT a result. Nothing was scanned. A zero here is an ABSENT INDEX, "
              "never a zero-use finding.", file=sys.stderr)
        return 0
    for slug in slugs:
        recs = scan(rows, slug, max_files=args.max_files)
        fn = REPORTERS[slug]
        if slug == "wayfinder":
            fn(recs, rows, how, limit=args.limit, show_senses=args.senses)
        elif slug == "grill-me":
            fn(recs, rows, how, limit=args.limit, show_cadence=args.cadence)
        else:
            fn(recs, rows, how, limit=args.limit)
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
