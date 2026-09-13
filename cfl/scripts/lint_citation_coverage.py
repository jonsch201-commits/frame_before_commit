#!/usr/bin/env python3
"""E2 coverage instrument — five methods, two numbers each, sliced by category.

Report-only. Never writes to anything it measures (hard constraint: `census.py`
mutates `wiki/references/audit-census-2026-07-13.md` as a side effect, which is
precisely why it cannot be run routinely).

WHY FIVE METHODS
----------------
`source-page-standard-v4.md` E2 specifies anchor FORM and RESOLUTION but names
neither a threshold nor a population (`:89` still lists the threshold as an open
item; the `>=95%` figure survives only in the deprecated v3 document). Three
existing implementations therefore measure three different things and none of
them measures E2's stated population:

  - `scripts/audit/lint.py:63`   page-level any-anchor boolean
  - `scripts/audit/lint.py:102`  % of pages
  - `scripts/audit/census.py:77` raw anchor count

Jon, 2026-07-25 (turn 7), ratifying E2 option 3:
    "there are multiple ways you could measure this and so I expect you should
     test a 95% threshold in multiple ways and I expect you currently are not."
He was right; this file is the answer. He asked for the same thing on 2026-04-10
("I know their are multiple ways we should test this. You should too") and for
category stratification on 2026-07-17 ("stratified random sample... Of
conversation summaries, and other types of articles. In all 4 trunks").

The five methods DISAGREE, and the disagreement is the finding. A threshold is
meaningless without naming the method — Q3's two-agreeing-enumerations principle
applied to E2.

  M1 claim-level        claims with an accepted marker / substantive claims
  M2 page-level         pages where EVERY claim is covered / pages
  M3 anchor-correctness anchors that resolve to the RIGHT turn / resolvable anchors
  M4 materiality        M1 restricted to load-bearing claims
  M5 Jon's-words        Jon-attributed claims cited to raw / Jon-attributed claims

TWO NUMBERS PER METHOD (Jon's amendment 1: "track where that hits us in terms of
your e2 threshold %"). Option 3 makes the headline ~100% by construction once
tagging completes, so every method reports:

  OPTION-3  accepts a resolvable anchor OR an explicit fidelity tag
            ([inferred] / [uncaptured] / [unrecoverable]) — the ratified rule
  STRICT    accepts a resolvable anchor ONLY, no exemption

THE GAP BETWEEN THEM IS THE HONEST RESIDUAL. Only the strict number can be
compared against 95%.

M3 IS THE ONE THAT MATTERS AND THE ONE THAT NEVER EXISTED
---------------------------------------------------------
E2's only correctness check today fails an anchor pointing PAST the verified turn
count. An anchor pointing at a wrong-but-in-range turn passes every lint. The
live example, still in the corpus:

  wiki/sources/ai-mechanics/ai-mechanics-token-encoding-2026-03-29-b43447.md:17
    "**Adjustment operation is Option B (pre-softmax)**: ... ([...:T10])"
  T10 is role A — the model PROPOSING option B.
  T11 is role H — Jon: "Yes option B, we need to get that adjusted."

Both resolve. Both pass. They are not the same claim. `source-page-standard-v4.md`
:46-50 specifies a certainty-inflation lint to catch exactly this and it was never
implemented; M3 is that implementation. It is deterministic, not sampled: a claim
reporting a DECISION must anchor to a turn Jon actually spoke in.

SLICING (Jon's amendment 2) is on the PATH, not frontmatter. `source_kind` is 8%
populated, `domain` 6%, and `trunk` does not exist as a field at all. The real
dimension is the `wiki/sources/<subdirectory>` split, which is 100% populated and
is what `wiki/index.md` itself groups by. An aggregate hides a 0% bucket behind a
74% one — `sources/reference` is 0-of-5 anchored while `sources/fbc` is 14-of-19.

Usage:
    python scripts/lint_citation_coverage.py                 # full E2 report
    python scripts/lint_citation_coverage.py --slices        # add category tables
    python scripts/lint_citation_coverage.py --m3-detail     # list every M3 flag
    python scripts/lint_citation_coverage.py --legacy        # original (a)/(b) checks
    python scripts/lint_citation_coverage.py --selftest      # unit tests
    python scripts/lint_citation_coverage.py --json          # machine-readable

Exit code: 0 always in report mode — a finder, not a gate, until the population
and threshold are ratified. --selftest exits 1 on any failure.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "audit"))
from turn_index import _fence_mask, index as turn_index_of  # noqa: E402

# --------------------------------------------------------------------------
# patterns
# --------------------------------------------------------------------------

KEY_CLAIMS_HEADING = re.compile(r"^##\s*Key Claims\s*$", re.M)
ANY_H2 = re.compile(r"^##\s", re.M)

# A claim is a TOP-LEVEL bullet: zero indent. The prior version used `^\s*-\s+`,
# which matched any indentation, so nested sub-bullets inflated the denominator.
# A nested bullet belongs to the claim above it and is folded into that claim's
# text block (its anchors count for the parent), never counted as its own claim.
TOPLEVEL_BULLET = re.compile(r"^-\s+")
NESTED_BULLET = re.compile(r"^\s+-\s+")

TURN_ANCHOR = re.compile(r"\[([A-Za-z0-9_\-]+):T(\d+)(?:\.P(\d+))?\]")
WIKI_LINK = re.compile(r"\[\[[^\]]+\]\]")
FIDELITY_TAG = re.compile(r"\[(?:inferred|uncaptured|unrecoverable)\]", re.I)
SOURCE_CITATION = re.compile(r"`[^`]+\.(?:md|py|sh|json|ya?ml)[^`]*`|\bhttps?://")

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
HASH_IN_SLUG = re.compile(r"[0-9a-f]{6,7}")

# M5 population: Jon's words are a categorical floor (turn 6, verbatim — "My
# words are a categorical floor - always load-bearing, cited to raw, negatively-
# cited words included"). Population errs toward inclusion by design.
JON_MENTION = re.compile(r"\bJon(?:'s|s')?\b")
QUOTED_SPAN = re.compile(r"[\"“][^\"”]{12,}[\"”]")

# M3/M4 decision lexicon — used for the M4 materiality population ONLY, never as
# an M3 trigger. As an M3 trigger it fired on 497 of 900 anchored claims: a
# detector that flags half its population is not a detector (cf. RATIO_FLOOR,
# which fired on 100% of primary sessions and was written off as noise while it
# was reporting real truncation).
DECISION_LEXICON = re.compile(
    r"\b(?:ruled?|ruling|decided?|decision|chose|chosen|approved?|approval"
    r"|ratified?|ratification|rejected?|confirmed?|authorized?|mandated?"
    r"|settled|directed|instructed|ordered|specified\s+that|established\s+that"
    r"|committed\s+to|signed\s+off)\b",
    re.I,
)

# M3 MECHANICAL trigger — deliberately narrow. Jon as the GRAMMATICAL SUBJECT of
# a speech or decision act ("Jon ruled", "Jon asked for", "Jon's correction was").
# If a claim reports Jon doing or saying a thing, its anchor must point at a turn
# where Jon spoke (role H). This is airtight and it fires on 17 of 900 anchored
# claims, not 497.
#
# WHAT THIS DELIBERATELY DOES NOT CATCH, and why that is honest:
# the ground-truth fixture — "**Adjustment operation is Option B (pre-softmax)**"
# anchored to T10 (role A, the model PROPOSING it) when the decision is Jon at
# T11 — contains no Jon subject and no decision verb. No regex reaches it.
# Whether T10 supports that claim requires READING T10 and judging. That is the
# sampled arm's job (--sample), not this one's. A mechanical check that claimed
# to cover it would be the RATIO_FLOOR mistake a second time.
# MEASURED REFINEMENT, PROPOSED BUT NOT SHIPPED (2026-07-26). Two candidate fixes were
# tested against real data rather than reasoned about:
#   (a) scope the trigger to the claim's BOLD LEAD (the wiki's convention for the assertion
#       itself). Corpus flags 20 -> 3. REJECTED: it drops window-repair T46, a verified
#       true positive whose lead is a neutral noun phrase with "Jon corrected..." in the
#       body. Better precision bought with recall on exactly the defect class M3 exists for.
#   (b) suppress when the claim ALSO attributes the action to the assistant ("Claude's own
#       elaboration...", "the assistant surfaces..."). Corpus 20 -> 19 (conservative, costs
#       no true positives); on a fresh page it removed 2 of 4 false positives. Directionally
#       right, incompletely validated.
# Neither is shipped. A half-validated detector refinement is how RATIO_FLOOR happened, and
# M3 already behaves correctly as a FINDER — flags go to review, not to a verdict. Recorded
# here so the next person starts from measurements instead of re-deriving them.
#
# The underlying design flaw, which is the part worth remembering: the current trigger
# PENALIZES PRECISE WRITING. A page that carefully says "Claude's elaboration, after Jon's
# ruling" gets flagged; a vaguer page saying "the elaboration" does not. Any future fix must
# not create an incentive toward mushier claims.
# KNOWN FALSE-POSITIVE SHAPE, measured 2026-07-26 and recorded rather than glossed.
# On a freshly-ingested page (44a95b, 21 claims / 42 anchors) this trigger fired once, and
# the flag was WRONG: the claim asserted what *the assistant* surfaced — correctly anchored
# to an Assistant turn — while containing "Jon had written to Opus" in a subordinate clause.
# The trigger sees a Jon-subject act; it cannot see that the claim's MAIN assertion is about
# someone else.
#
# So the honest precision statement is: of 20 corpus flags, 2 were checked by hand and were
# genuine off-by-ones; on 1 fresh page, 1 of 1 was a false positive. Precision is UNKNOWN,
# not "all real" — an earlier commit message of mine said "20 flags, and they are real,"
# which overstated what 2 verified samples support. M3-mechanical is a FINDER: every flag is
# reviewed, none is a verdict. Tightening further would trade away the true off-by-ones
# (window-repair T46-vs-T47, photo-archive T16-vs-T14) that are the whole point.
#
# MEASURED 2026-08-10 — PRECISION IS NO LONGER UNKNOWN. All 23 corpus flags were read item by
# item, the first full-class hand review this trigger has had: 7 GENUINE, 16 FALSE.
# ~30% precision, n=23, whole class, not a sample.
#
# EVERY ONE OF THE 16 IS THE SHAPE THIS COMMENT ALREADY PREDICTED — a Jon-act in a subordinate
# clause while the claim's main assertion is the assistant's: "the deliverable Jon asked for",
# "the ledger Jon asked to be read", "(Jon discussion required)". The prediction was written
# 2026-07-26 from ONE example and held across sixteen.
#
# AND THE WARNING ABOVE ABOUT TIGHTENING IS CONFIRMED, NOT OVERRIDDEN. 4 of the 7 genuine ones
# sit MID-CLAIM ("Jon stated a belief", "Jon confirmed", "Jon asked if…", "Jon corrected an
# earlier inference"), so the obvious narrowing — require the Jon-act to lead the claim —
# would drop 4 of 7 real defects to remove 16 false ones. THE REGEX IS DELIBERATELY UNCHANGED.
#
# What the review DID establish is worth more than a tighter pattern: 2 of the 7 are RULINGS
# attributed to Jon on turns Jon did not speak —
#   question-pricing-model-…-408368:T8   "Jon's ruling - APPROVED [JON, 2026-07-26 ~21:45]"
#   security-master-…-8881d3:T229        "Jon's own ruling, delivered mid-session" + quotation
# — which is the exact shape behind this repo's invented-ruling failures. A finder with 30%
# precision that surfaces those two is doing its job. REPORT THE PRECISION, KEEP THE FINDER.
JON_SUBJECT_ACT = re.compile(
    r"\bJon(?:'s)?\s+(?:\w+\s+){0,3}?"
    r"(?:ruled?|ruling|decided?|approved?|ratified?|chose|chosen|rejected?"
    r"|confirmed?|directed|instructed|said|stated|asked|wants?|wanted"
    r"|requires?|required|specified|authorized?|mandated?|clarified|corrected"
    r"|called|named|set)\b",
    re.I,
)
# Bold-lead is the wiki's own convention for a named, load-bearing claim.
BOLD_LEAD = re.compile(r"^\*\*[^*]+\*\*")

SOURCE_GLOBS = [
    "wiki/sources/**/*.md",
    "wiki/personal/sources/**/*.md",
    "wiki/home/sources/**/*.md",
    "wiki/pro/sources/**/*.md",
]
CONCEPT_GLOB = "wiki/concepts/*.md"

# EXCLUSION CLASS, built 2026-08-06 (T-02 continuation, prerequisite the pilot named and
# skipped — see wiki/references/agent-memory/README.md "What this criterion deliberately
# does not do"). The agent-memory drain lands ~49 pages that are PROCESS RECORDS from the
# CC memory store, not claims derived from a corpus conversation. They have no raw
# transcript to anchor against by construction (their "source" is a memory file, not a
# session) — E2's turn-anchor population was never meant to include them, but nothing
# EXCLUDED them either, so at n=49 they would either sink M1/M2 (denominator inflated with
# structurally-unresolvable claims) or force someone to hand-fabricate anchors for pages
# that are supposed to be citation-source material, not citation-consumers.
#
# Mechanism: a page opts into the exclusion by declaring `coverage_class:
# untraced-by-design` in its own frontmatter, with a `coverage_class_reason:` alongside it
# (the "excluded still needs a reason on record" rule applies to lint exemptions too, not
# just admission exclusions). This is NOT a path-based exemption — a page's directory does
# not grant it anything; the frontmatter field is the only thing this script reads. That
# keeps the exemption auditable (grep the field) and prevents silent scope creep if a real
# session/reference/analysis page ever lands in wiki/references/agent-memory/ by mistake.
AGENT_MEMORY_GLOB = "wiki/references/agent-memory/*.md"
UNTRACED_BY_DESIGN = "untraced-by-design"

# ---------------------------------------------------------------------------
# METHOD VERSION — bump on ANY change to what a number means.
#
# Jon, 2026-07-26: "I just know we won't count it perfectly the first time or
# the second time." Correct, and it is the design constraint, not a caveat. The
# counting rule WILL move; what must not happen is a moved rule silently
# invalidating everything measured under the old one.
#
# Three properties keep a redefinition cheap:
#   1. ALL FIVE METHODS stay computed forever, not just whichever one gates.
#      The other four are what a future definition re-reads.
#   2. EVERY NUMBER CARRIES ITS BASIS. A number without the method that produced
#      it is the model-basis failure again (fleet agents moved 4.8 -> 5 on a
#      point release; the record still said 4.8). Bump METHOD_VERSION and the
#      old series stays labelled, not overwritten.
#   3. NOTHING IS CACHED. Re-derived at every SU, per Q3.
#
# The property that makes all of this work: the wiki's history is in git and
# this instrument is a pure function of a tree, so ANY past number can be
# recomputed under a NEW definition by pointing --root at an old commit. A
# redefinition re-reads history; it does not orphan it.
#
# CAVEAT, load-bearing: `raw/` is gitignored, so an old commit's worktree has no
# transcripts. --raw-root exists for exactly this: page tree from the past,
# corpus from the present. M1/M2/M4/M5 are therefore fully recomputable across
# history; M3 is only recomputable against whatever the corpus holds NOW.
METHOD_VERSION = "e2-methods/1.0.0"


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def parse_frontmatter(text):
    m = FRONTMATTER.match(text)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line.strip())
            if mm:
                fm[mm.group(1)] = mm.group(2).strip()
    return fm


def unfenced_lines(text):
    """Lines with a fence mask applied — content inside ``` blocks is blanked.

    A bullet inside a fenced example is not a claim. Reuses turn_index.py's
    run-length-aware mask (a nested shorter fence cannot close an outer wrapper),
    so the two tools agree on what 'inside a fence' means.
    """
    lines = text.splitlines()
    mask = _fence_mask([l + "\n" for l in lines])
    return [("" if m else l) for l, m in zip(lines, mask)]


def key_claims_block(text):
    """Return the Key Claims section body as a list of lines (fence-blanked)."""
    lines = unfenced_lines(text)
    start = None
    for i, l in enumerate(lines):
        if KEY_CLAIMS_HEADING.match(l):
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if ANY_H2.match(lines[j]):
            end = j
            break
    return lines[start:end]


def split_claims(block_lines):
    """Split a Key Claims body into claim units.

    One claim = a top-level bullet plus every following line up to the next
    top-level bullet (its nested sub-bullets and continuation lines). Anchors on
    those child lines belong to the parent claim.

    Returns (claims, nested_count) — nested_count quantifies the old defect: how
    many sub-bullets the previous `^\\s*-\\s+` regex was miscounting as claims.
    """
    claims, cur, nested = [], None, 0
    for l in block_lines:
        if TOPLEVEL_BULLET.match(l):
            if cur is not None:
                claims.append("\n".join(cur))
            cur = [l]
        else:
            if NESTED_BULLET.match(l):
                nested += 1
            if cur is not None:
                cur.append(l)
    if cur is not None:
        claims.append("\n".join(cur))
    return claims, nested


def claim_text(c):
    return re.sub(r"^-\s+", "", c).strip()


# --------------------------------------------------------------------------
# page kind — E2 is kind-dependent (v4:40-45)
# --------------------------------------------------------------------------

def page_kind(path, fm):
    """session | reference | analysis.

    v4 E2: session -> turn anchor required. reference -> source-citation, turn
    anchor is N/A-by-kind. analysis (G1) -> [[slug]] transitively, or [inferred].
    """
    p = path.replace(os.sep, "/")
    if "/concepts/" in p:
        return "analysis"
    if "/sources/reference/" in p:
        return "reference"
    t = (fm.get("type") or "").lower()
    if t in ("reference", "note", "summary"):
        return "reference"
    if t in ("analysis", "concept"):
        return "analysis"
    return "session"


def slice_key(path):
    """Category slice on the PATH — the only 100%-populated dimension."""
    p = os.path.normpath(path).replace(os.sep, "/")
    p = p[p.index("wiki/"):] if "wiki/" in p else p
    parts = p.split("/")
    if parts[1] == "concepts":
        return "wiki/concepts"
    if parts[1] == "sources":                      # wiki/sources/<subdir>/file
        return "/".join(parts[:3]) if len(parts) > 3 else "wiki/sources/(root)"
    return "/".join(parts[:3])                     # wiki/<trunk>/sources


# --------------------------------------------------------------------------
# date resolution (T-03, Jon ruling 2026-08-02: cohort-split on citation
# instrument — "Lets seprately measure July-1st and later vs before").
# --------------------------------------------------------------------------

_DATE_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")

# frontmatter fields checked in priority order — the ones that name an actual
# EVENT/ingest date first, generic authoring/status fields last. `as_of` is
# excluded from this list on purpose: it is frequently the literal string
# "undated" (see wiki/references/agent-memory/*.md) and is NOT a reliable date
# field — treating it as one would silently misdate the exempt agent-memory
# cohort. Jon's amendment 2 requires this NOT be papered over: an unresolvable
# date must fall into the unknown-date bucket, not be guessed.
_DATE_FIELDS = ("date_ingested", "date", "authored", "written", "generated_by")


def page_date(path, fm):
    """Best-effort resolvable date for a page, or None (-> unknown-date bucket).

    Returns (date_str, source_label) so the report can show WHERE a date came
    from, not just that one was found — Jon's own standard for measurement
    ("a number without its basis is not a measurement").
    """
    for field in _DATE_FIELDS:
        v = fm.get(field, "")
        if not v:
            continue
        m = _DATE_RE.search(str(v))
        if m:
            return "-".join(m.groups()), f"frontmatter:{field}"
    # fall back to a date embedded in source_file / path (session-page slugs
    # commonly carry chat-YYYY-MM-DD-...)
    sf = fm.get("source_file", "")
    m = _DATE_RE.search(str(sf))
    if m:
        return "-".join(m.groups()), "source_file"
    m = _DATE_RE.search(os.path.basename(path))
    if m:
        return "-".join(m.groups()), "filename"
    return None, None


def cohort_key(date_str):
    """Three-way cohort per Jon's 2026-08-02 ruling, with the transitional
    07-01->07-13 sub-band flagged separately (source-page-standard-v4.md
    ratified 2026-07-13 — a bare July-1 boundary would put ~12 days of
    pre-standard pages inside the "new" cohort otherwise)."""
    if date_str is None:
        return "unknown-date"
    if date_str < "2026-07-01":
        return "pre-2026-07-01"
    if date_str < "2026-07-13":
        return "2026-07-01_to_07-13 (transitional, pre-v4-standard)"
    return "2026-07-13_and_later (post-v4-standard)"


# --------------------------------------------------------------------------
# anchor resolution ladder
# --------------------------------------------------------------------------

class Resolver:
    """Resolve an anchor slug to a raw transcript path, then to a turn map.

    Anchor slugs are WIKI-PAGE slugs, not raw filenames
    (`ai-mechanics-token-encoding-2026-03-29-b43447` ->
     `raw/.../chat-2026-03-29-b43447-understanding-token-representation-and-encoding.md`),
    so resolution goes through the page's `source_file:`. Measured on the live
    corpus: 783 self-referential, 60 cross-page, 302 bare-hash, 77 hash-fallback.
    """

    def __init__(self, root, raw_root=None):
        self.root = root
        self.raw_root = raw_root or root
        self.page_source = {}     # page slug -> source_file value
        self.hash_page = collections.defaultdict(list)
        self.hash_raw = collections.defaultdict(list)
        self._turns = {}          # raw path -> turn list or None
        self.raws = {}
        for p in glob.glob(os.path.join(self.raw_root, "raw/transcripts/**/*.md"), recursive=True):
            base = os.path.basename(p)[:-3]
            self.raws[base] = p
            for h in set(HASH_IN_SLUG.findall(base)):
                self.hash_raw[h].append(p)

    def register(self, path, fm):
        slug = os.path.basename(path)[:-3]
        self.page_source[slug] = fm.get("source_file", "")
        m = HASH_IN_SLUG.search(slug)
        if m:
            self.hash_page[m.group(0)].append(slug)

    def _raw_for_slug(self, slug):
        sf = self.page_source.get(slug)
        if sf and sf.lower() not in ("none", "n/a", ""):
            cand = os.path.join(self.raw_root, sf.split("#")[0].strip())
            if os.path.isfile(cand):
                return cand
        if slug in self.raws:
            return self.raws[slug]
        for h in HASH_IN_SLUG.findall(slug):
            for s in self.hash_page.get(h, []):
                sf = self.page_source.get(s)
                if sf and sf.lower() not in ("none", "n/a", ""):
                    cand = os.path.join(self.raw_root, sf.split("#")[0].strip())
                    if os.path.isfile(cand):
                        return cand
            if self.hash_raw.get(h):
                return self.hash_raw[h][0]
        return None

    def turns(self, slug):
        """Return (raw_path, [ {t,role,line} ]) or (None, None)."""
        raw = self._raw_for_slug(slug)
        if not raw:
            return None, None
        if raw not in self._turns:
            try:
                self._turns[raw] = turn_index_of(raw)["turns"]
            except Exception:
                self._turns[raw] = None
        return raw, self._turns[raw]


# --------------------------------------------------------------------------
# per-claim evaluation
# --------------------------------------------------------------------------

def evaluate_claim(text, kind, resolver):
    """Classify one claim. Returns a dict of booleans + M3 flags."""
    anchors = TURN_ANCHOR.findall(text)
    r = {
        "n_anchors": len(anchors),
        "has_wikilink": bool(WIKI_LINK.search(text)),
        "has_fidelity": bool(FIDELITY_TAG.search(text)),
        "has_source_cite": bool(SOURCE_CITATION.search(text)),
        "resolvable": False,
        "m3_flags": [],
        "is_jon": bool(JON_MENTION.search(text) or QUOTED_SPAN.search(text)),
        "is_decision": bool(DECISION_LEXICON.search(text)),
        "is_bold_lead": bool(BOLD_LEAD.match(claim_text(text))),
        "jon_subject": bool(JON_SUBJECT_ACT.search(text)),
        "resolved_anchors": [],   # (slug, tn, role, raw) — the sampling frame
    }

    for slug, tn, _pn in anchors:
        tn = int(tn)
        raw, turns = resolver.turns(slug)
        if not turns:
            r["m3_flags"].append(("UNRESOLVABLE-SLUG", slug, tn, None))
            continue
        if tn < 1 or tn > len(turns):
            r["m3_flags"].append(("OUT-OF-RANGE", slug, tn, f"file has T1..T{len(turns)}"))
            continue
        r["resolvable"] = True
        role = turns[tn - 1]["role"]
        r["resolved_anchors"].append((slug, tn, role, raw))
        # A claim reporting Jon doing or saying something must anchor to a turn
        # Jon spoke in. Anchoring to A (assistant) or D (agent dispatch) means
        # the citation points at someone else's words.
        if r["jon_subject"] and role in ("A", "D"):
            nearby = ""
            for off in (1, -1, 2, -2):
                k = tn - 1 + off
                if 0 <= k < len(turns) and turns[k]["role"] == "H":
                    nearby = f"nearest H turn is T{turns[k]['t']}"
                    break
            r["m3_flags"].append(("JON-SUBJECT-ON-NON-H", slug, tn,
                                  f"anchored turn is role {role}; {nearby}"))

    # STRICT: E2's own kind-dependent form, no fidelity-tag exemption.
    if kind == "session":
        r["strict"] = r["resolvable"]
    elif kind == "analysis":
        r["strict"] = r["resolvable"] or r["has_wikilink"]
    else:  # reference — turn anchor is N/A-by-kind; a source citation satisfies E2
        r["strict"] = r["resolvable"] or r["has_source_cite"] or r["has_wikilink"]

    # OPTION 3 (ratified): strict, OR an explicit fidelity disclosure.
    r["option3"] = r["strict"] or r["has_fidelity"]
    return r


# --------------------------------------------------------------------------
# scan
# --------------------------------------------------------------------------

def scan(root, limit=None, raw_root=None):
    paths = []
    for pat in SOURCE_GLOBS:
        paths.extend(glob.glob(os.path.join(root, pat), recursive=True))
    paths = sorted(set(os.path.normpath(p) for p in paths))
    concepts = sorted(os.path.normpath(p) for p in
                      glob.glob(os.path.join(root, CONCEPT_GLOB)))
    exempt = sorted(os.path.normpath(p) for p in
                    glob.glob(os.path.join(root, AGENT_MEMORY_GLOB)))
    if limit:
        paths, concepts = paths[:limit], concepts[:limit]

    resolver = Resolver(root, raw_root=raw_root)
    raw_texts = {}
    for p in paths + concepts + exempt:
        with open(p, encoding="utf-8", errors="ignore") as f:
            raw_texts[p] = f.read()
        resolver.register(p, parse_frontmatter(raw_texts[p]))

    pages = []
    for p in paths + concepts + exempt:
        text = raw_texts[p]
        fm = parse_frontmatter(text)
        kind = page_kind(p, fm)
        block = key_claims_block(text)
        is_untraced = fm.get("coverage_class", "").strip() == UNTRACED_BY_DESIGN
        pdate, pdate_src = page_date(p, fm)
        rec = {
            "path": p,
            "slice": slice_key(p),
            "date": pdate,
            "date_source": pdate_src,
            "cohort": cohort_key(pdate),
            "kind": kind,
            "is_concept": p in concepts,
            "is_untraced": is_untraced,
            "coverage_class_reason": fm.get("coverage_class_reason", ""),
            "has_kc": block is not None,
            "nested_miscounted": 0,
            "claims": [],
        }
        if block is not None and not is_untraced:
            claims, nested = split_claims(block)
            rec["nested_miscounted"] = nested
            for c in claims:
                rec["claims"].append(evaluate_claim(c, kind, resolver))
                rec["claims"][-1]["text"] = claim_text(c)[:110]
        pages.append(rec)
    return pages, resolver


# --------------------------------------------------------------------------
# the five methods
# --------------------------------------------------------------------------

def tree_stamp(root):
    """Identify the tree being measured, so a number is never basis-less."""
    import subprocess
    try:
        out = subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        sha = out.stdout.strip() or "unknown"
        dirty = subprocess.run(["git", "-C", root, "status", "--porcelain"],
                               capture_output=True, text=True, timeout=20)
        return f"{sha}{'+dirty' if dirty.stdout.strip() else ''}"
    except Exception:
        return "unknown"


def pct(n, d):
    return (100.0 * n / d) if d else float("nan")


def methods(pages, population="all"):
    """Compute M1-M5 under one claim population. Returns nested dict."""
    src = [p for p in pages if not p["is_concept"] and not p.get("is_untraced")]

    def claims_of(p):
        cs = p["claims"]
        if population == "bold":
            cs = [c for c in cs if c["is_bold_lead"]]
        elif population == "nontrivial":
            cs = [c for c in cs if len(c["text"]) >= 40]
        return cs

    out = {}
    allc = [c for p in src for c in claims_of(p)]
    out["M1"] = {
        "d": len(allc),
        "opt3": sum(1 for c in allc if c["option3"]),
        "strict": sum(1 for c in allc if c["strict"]),
    }
    with_claims = [p for p in src if claims_of(p)]
    out["M2"] = {
        "d": len(with_claims),
        "opt3": sum(1 for p in with_claims if all(c["option3"] for c in claims_of(p))),
        "strict": sum(1 for p in with_claims if all(c["strict"] for c in claims_of(p))),
    }
    resolvable_anchors = sum(c["n_anchors"] for c in allc)
    flagged = sum(len(c["m3_flags"]) for c in allc)
    out["M3"] = {"d": resolvable_anchors, "opt3": resolvable_anchors - flagged,
                 "strict": resolvable_anchors - flagged}
    mat = [c for c in allc if c["is_bold_lead"] or c["is_decision"]]
    out["M4"] = {
        "d": len(mat),
        "opt3": sum(1 for c in mat if c["option3"]),
        "strict": sum(1 for c in mat if c["strict"]),
    }
    jon = [c for c in allc if c["is_jon"]]
    out["M5"] = {
        "d": len(jon),
        "opt3": sum(1 for c in jon if c["option3"]),
        "strict": sum(1 for c in jon if c["strict"]),
    }
    return out


METHOD_LABEL = {
    "M1": "claim-level      claims covered / claims",
    "M2": "page-level       fully-covered pages / pages",
    "M3": "anchor-correct.  correct anchors / resolvable anchors",
    "M4": "materiality      load-bearing claims covered",
    "M5": "Jon's-words      Jon-attributed claims covered",
}


def render_methods(m, title, threshold=95.0):
    print(f"\n  {title}")
    print(f"  {'method':<48} {'OPTION-3':>18} {'STRICT':>18}   {'gap':>6}  vs {threshold:.0f}%")
    print(f"  {'-'*48} {'-'*18} {'-'*18}   {'-'*6}  {'-'*7}")
    for k in ("M1", "M2", "M3", "M4", "M5"):
        v = m[k]
        p3, ps = pct(v["opt3"], v["d"]), pct(v["strict"], v["d"])
        gap = p3 - ps
        verdict = "PASS" if ps >= threshold else "FAIL"
        print(f"  {k} {METHOD_LABEL[k]:<45} "
              f"{v['opt3']:>6}/{v['d']:<5}{p3:>5.1f}% "
              f"{v['strict']:>6}/{v['d']:<5}{ps:>5.1f}% "
              f"  {gap:>5.1f}   {verdict}")


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------

def report(pages, resolver, show_slices=False, m3_detail=False, threshold=95.0,
           root=".", raw_root=None, show_cohorts=False):
    src = [p for p in pages if not p["is_concept"] and not p.get("is_untraced")]
    con = [p for p in pages if p["is_concept"]]
    exempt = [p for p in pages if p.get("is_untraced")]
    total_claims = sum(len(p["claims"]) for p in src)
    nested = sum(p["nested_miscounted"] for p in src)

    print("=" * 92)
    print("E2 COVERAGE INSTRUMENT — five methods, two numbers each")
    print("=" * 92)
    print(f"\nBASIS (a number without its basis is not a measurement)")
    print(f"  method version                 : {METHOD_VERSION}")
    print(f"  page tree measured             : {tree_stamp(root)}")
    if raw_root and os.path.abspath(raw_root) != os.path.abspath(root):
        print(f"  raw corpus (decoupled)         : {os.path.abspath(raw_root)}")
        print(f"    ^ M3 is measured against the CURRENT corpus, not the tree's own; "
              f"raw/ is gitignored")
    print(f"\nPOPULATIONS (every number below names its own; no bare counts)")
    print(f"  source pages enumerated        : {len(src)}   <- must agree with the SU denominator")
    print(f"  concept pages (reported apart) : {len(con)}")
    print(f"  exempt (coverage_class={UNTRACED_BY_DESIGN}): {len(exempt)}   "
          f"<- never enters M1-M5; see wiki/references/agent-memory/README.md")
    if exempt:
        no_reason = [p for p in exempt if not p["coverage_class_reason"]]
        if no_reason:
            print(f"    !! {len(no_reason)} exempt page(s) with NO coverage_class_reason "
                  f"(exclusion recorded with no reason on record — a fresh defect):")
            for p in no_reason[:10]:
                print(f"       {os.path.relpath(p['path']).replace(os.sep,'/')}")
    print(f"  pages with a ## Key Claims block: {sum(1 for p in src if p['has_kc'])}")
    print(f"  top-level claims               : {total_claims}")
    print(f"  nested sub-bullets NOT counted : {nested}   <- the prior regex counted these as claims")
    print(f"  page kinds                     : " +
          ", ".join(f"{k}={v}" for k, v in
                    sorted(collections.Counter(p['kind'] for p in src).items())))

    render_methods(methods(src), "population = ALL top-level claims", threshold)
    render_methods(methods(src, "bold"), "population = BOLD-LEAD claims only ('substantive', reading 2)", threshold)
    render_methods(methods(src, "nontrivial"), "population = claims >=40 chars ('substantive', reading 3)", threshold)

    # ---- M3 detail ----
    flags = collections.Counter()
    examples = collections.defaultdict(list)
    for p in src + con:
        for c in p["claims"]:
            for kind_, slug, tn, note in c["m3_flags"]:
                flags[kind_] += 1
                if len(examples[kind_]) < (200 if m3_detail else 6):
                    rel = os.path.relpath(p["path"]).replace(os.sep, "/")
                    examples[kind_].append((rel, slug, tn, note, c["text"]))
    print(f"\n  M3 FLAG BREAKDOWN  (the check that never existed — v4:46-50, unimplemented until now)")
    if not flags:
        print("    none")
    for k, n in flags.most_common():
        print(f"    {k:<18} {n}")
    for k, n in flags.most_common():
        print(f"\n    --- {k} ({n} total{'' if m3_detail else '; first 6 — rerun --m3-detail for all'}) ---")
        # MEASURED PRECISION, PRINTED NOT COMMENTED. A finder's count reads as a defect count
        # unless the line says otherwise, and this one is ~30% genuine on a full hand review.
        # Without this, "JON-SUBJECT-ON-NON-H 23" is read as 23 broken citations. It is 7.
        if k == "JON-SUBJECT-ON-NON-H":
            print("        [precision] MEASURED 2026-08-10, whole class hand-reviewed: 7 genuine / 16 false (~30%).")
            print("        The 16 are a Jon-act in a SUBORDINATE clause while the claim's main assertion is the")
            print("        assistant's. THESE ARE REVIEW ITEMS, NOT DEFECTS -- and 2 of the 7 are RULINGS anchored")
            print("        on turns Jon did not speak, which is why the finder stays.")
        for rel, slug, tn, note, txt in examples[k]:
            print(f"      {rel}")
            print(f"        [{slug}:T{tn}]  {note or ''}")
            print(f"        claim: {txt}")

    # ---- slices ----
    if show_slices:
        print(f"\n{'='*92}\nCATEGORY SLICES (Jon's amendment 2 — an aggregate hides a 0% bucket behind a 74% one)\n{'='*92}")
        by = collections.defaultdict(list)
        for p in src:
            by[p["slice"]].append(p)
        print(f"\n  {'slice':<32} {'pages':>6} {'claims':>7} "
              f"{'M1 opt3':>9} {'M1 strict':>10} {'M2 strict':>10} {'M5 strict':>10}")
        print(f"  {'-'*32} {'-'*6} {'-'*7} {'-'*9} {'-'*10} {'-'*10} {'-'*10}")
        for s in sorted(by):
            m = methods(by[s])
            print(f"  {s:<32} {len(by[s]):>6} {m['M1']['d']:>7} "
                  f"{pct(m['M1']['opt3'], m['M1']['d']):>8.1f}% "
                  f"{pct(m['M1']['strict'], m['M1']['d']):>9.1f}% "
                  f"{pct(m['M2']['strict'], m['M2']['d']):>9.1f}% "
                  f"{pct(m['M5']['strict'], m['M5']['d']):>9.1f}%")

        by_kind = collections.defaultdict(list)
        for p in src:
            by_kind[p["kind"]].append(p)
        print(f"\n  {'page kind':<32} {'pages':>6} {'claims':>7} {'M1 opt3':>9} {'M1 strict':>10}")
        print(f"  {'-'*32} {'-'*6} {'-'*7} {'-'*9} {'-'*10}")
        for s in sorted(by_kind):
            m = methods(by_kind[s])
            print(f"  {s:<32} {len(by_kind[s]):>6} {m['M1']['d']:>7} "
                  f"{pct(m['M1']['opt3'], m['M1']['d']):>8.1f}% "
                  f"{pct(m['M1']['strict'], m['M1']['d']):>9.1f}%")

    # ---- date cohorts (T-03, Jon 2026-08-02) ----
    if show_cohorts:
        print(f"\n{'='*92}\nDATE COHORTS (T-03 — separately measure July-1 and later vs before)\n{'='*92}")
        resolved = [p for p in src if p["date"] is not None]
        print(f"\n  DATE-COVERAGE MEASUREMENT (step 1, its own number):")
        print(f"    pages with a resolvable date : {len(resolved)} / {len(src)}"
              f"  ({pct(len(resolved), len(src)):.1f}%)")
        by_src = collections.Counter(p["date_source"] for p in resolved)
        for k, n in by_src.most_common():
            print(f"      via {k:<20} {n}")
        by_cohort = collections.defaultdict(list)
        for p in src:
            by_cohort[p["cohort"]].append(p)
        order = ["pre-2026-07-01", "2026-07-01_to_07-13 (transitional, pre-v4-standard)",
                 "2026-07-13_and_later (post-v4-standard)", "unknown-date"]
        print(f"\n  {'cohort':<48} {'pages':>6} {'claims':>7} "
              f"{'M1 opt3':>9} {'M1 strict':>10} {'M2 strict':>10} {'M5 strict':>10}")
        print(f"  {'-'*48} {'-'*6} {'-'*7} {'-'*9} {'-'*10} {'-'*10} {'-'*10}")
        for coh in order:
            grp = by_cohort.get(coh, [])
            if not grp and coh not in by_cohort:
                print(f"  {coh:<48} {0:>6}  <- own n=0, printed rather than omitted")
                continue
            m = methods(grp)
            print(f"  {coh:<48} {len(grp):>6} {m['M1']['d']:>7} "
                  f"{pct(m['M1']['opt3'], m['M1']['d']):>8.1f}% "
                  f"{pct(m['M1']['strict'], m['M1']['d']):>9.1f}% "
                  f"{pct(m['M2']['strict'], m['M2']['d']):>9.1f}% "
                  f"{pct(m['M5']['strict'], m['M5']['d']):>9.1f}%")
        print(f"\n  !! unknown-date bucket is first-class (Jon amendment 2: \"an aggregate hides a "
              f"0% bucket behind a 74% one\") — never fold it into either cohort's percentage.")
    print()
    return 0


def emit_sample(pages, n, seed, root):
    """Emit a STRATIFIED random sample of resolvable anchors for adjudication.

    The mechanical arm cannot decide whether an anchored turn SUPPORTS its claim
    — that needs reading. This emits the adjudication frame: claim text, the
    anchor, and the anchored turn's actual raw text plus its neighbours, so a
    reader (human or agent) can return SUPPORTED / NOT-SUPPORTED / PARTIAL.

    Stratified by slice, proportional-with-a-floor, so no bucket vanishes —
    Jon, 2026-07-17: "stratified random sample... Of conversation summaries, and
    other types of articles. In all 4 trunks." Seeded, so the same seed yields
    the same sample and a rate can be re-derived rather than cached.
    """
    import random
    frame = []
    for p in pages:
        if p["is_concept"]:
            continue
        for c in p["claims"]:
            for (slug, tn, role, raw) in c["resolved_anchors"]:
                frame.append({"page": p["path"], "slice": p["slice"], "kind": p["kind"],
                              "claim": c["text"], "slug": slug, "tn": tn,
                              "role": role, "raw": raw})
    by = collections.defaultdict(list)
    for f in frame:
        by[f["slice"]].append(f)

    rng = random.Random(seed)
    picked, strata = [], sorted(by)
    floor = max(1, n // (2 * len(strata))) if strata else 0
    for s in strata:
        share = max(floor, round(n * len(by[s]) / len(frame))) if frame else 0
        pool = by[s][:]
        rng.shuffle(pool)
        picked.extend(pool[:min(share, len(pool))])
    rng.shuffle(picked)
    picked = picked[:n]

    print(f"# E2 M3 adjudication sample — n={len(picked)} of {len(frame)} resolvable anchors, "
          f"seed={seed}")
    print(f"# strata: {len(strata)}; proportional with a floor of {floor} per stratum")
    print(f"# For each item return: SUPPORTED | NOT-SUPPORTED | PARTIAL, and one sentence why.")
    print(f"# NOT-SUPPORTED means the anchored turn does not contain what the claim asserts")
    print(f"# (e.g. the claim reports a settled decision but the turn only PROPOSES it).\n")

    for i, f in enumerate(picked, 1):
        rel = os.path.relpath(f["page"]).replace(os.sep, "/")
        print(f"## ITEM {i}")
        print(f"page   : {rel}")
        print(f"slice  : {f['slice']}   kind: {f['kind']}")
        print(f"anchor : [{f['slug']}:T{f['tn']}]  (role {f['role']})")
        print(f"claim  : {f['claim']}")
        try:
            idx = turn_index_of(f["raw"])
            turns, lines = idx["turns"], open(f["raw"], encoding="utf-8", errors="ignore").readlines()
            k = f["tn"] - 1
            start = turns[k]["line"] - 1
            end = turns[k + 1]["line"] - 1 if k + 1 < len(turns) else len(lines)
            body = "".join(lines[start:end]).strip()
            if len(body) > 2200:
                body = body[:2200] + "\n… [truncated]"
            print(f"anchored turn T{f['tn']} ({f['role']}) from {f['raw']}:")
            print("~~~~")
            print(body)
            print("~~~~")
        except Exception as e:
            print(f"  [could not read turn: {e}]")
        print()
    return 0


def legacy_report(pages):
    """The original (a)/(b) checks, preserved. NOTE: the (a) number this printed
    before 2026-07-25 (766/1614 = 47%) was computed with a denominator that
    counted nested sub-bullets as separate claims, and with a predicate looser
    than E2 — it was an upper bound, not a measurement."""
    src = [p for p in pages if not p["is_concept"] and not p.get("is_untraced")]
    tot = sum(len(p["claims"]) for p in src)
    cited = sum(1 for p in src for c in p["claims"] if c["option3"])
    print(f"-- legacy (a) per-claim coverage, corrected denominator --")
    print(f"   claims {tot}, with an accepted marker {cited} ({pct(cited, tot):.0f}%)")
    print(f"   pages with >=1 uncovered claim: "
          f"{sum(1 for p in src if any(not c['option3'] for c in p['claims']))}")
    return 0


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

def selftest():
    fails = []

    def check(name, got, want):
        if got != want:
            fails.append(f"FAIL [{name}] got={got!r} want={want!r}")

    # 1. nested sub-bullets are folded into the parent, not counted as claims
    t = "## Key Claims\n\n- Parent claim ([s:T1]).\n  - nested detail\n  - more nested\n- Second claim ([s:T2]).\n\n## Next\n"
    claims, nested = split_claims(key_claims_block(t))
    check("nested-not-counted", len(claims), 2)
    check("nested-tallied", nested, 2)

    # 2. bullets inside a fence are not claims
    t = "## Key Claims\n\n- Real claim ([s:T1]).\n\n```\n- fake bullet in a fence\n- another\n```\n\n- Second real ([s:T2]).\n"
    claims, _ = split_claims(key_claims_block(t))
    check("fence-excluded", len(claims), 2)

    # 3. a 3-backtick fence nested in a 4-backtick wrapper cannot leak
    t = ("## Key Claims\n\n- Real ([s:T1]).\n\n````\n- fake\n```\n- deeper fake\n```\n- still fake\n````\n\n- Second ([s:T2]).\n")
    claims, _ = split_claims(key_claims_block(t))
    check("nested-fence-runlength", len(claims), 2)

    # 4. option-3 vs strict diverge on a fidelity tag
    class R:
        def turns(self, slug):
            return None, None
    c = evaluate_claim("- Claim with no anchor but disclosed ([inferred]).", "session", R())
    check("opt3-accepts-fidelity", c["option3"], True)
    check("strict-rejects-fidelity", c["strict"], False)

    # 5. kind-dependence: a wiki-link satisfies analysis, not session
    c = evaluate_claim("- Rests on [[another-page]].", "analysis", R())
    check("analysis-accepts-wikilink", c["strict"], True)
    c = evaluate_claim("- Rests on [[another-page]].", "session", R())
    check("session-rejects-wikilink", c["strict"], False)

    # 6. M3 mechanical fires when Jon is the SUBJECT of an act, on a non-H turn
    class R2:
        def turns(self, slug):
            return "raw.md", [{"t": 1, "role": "H", "line": 1}, {"t": 2, "role": "A", "line": 9}]
    c = evaluate_claim("- Jon approved the design ([s:T2]).", "session", R2())
    check("m3-jon-subject-on-A", [f[0] for f in c["m3_flags"]], ["JON-SUBJECT-ON-NON-H"])
    c = evaluate_claim("- Jon approved the design ([s:T1]).", "session", R2())
    check("m3-no-flag-on-H", c["m3_flags"], [])

    # 7. out-of-range still fires
    c = evaluate_claim("- Something ([s:T9]).", "session", R2())
    check("m3-out-of-range", [f[0] for f in c["m3_flags"]], ["OUT-OF-RANGE"])

    # 8. CALIBRATION — the loose trigger must NOT fire. A claim that merely
    # mentions Jon, or carries a decision word without Jon as subject, is not a
    # miscitation. The loose form fired on 497/900 anchored claims; this is the
    # regression test that keeps it from coming back.
    c = evaluate_claim("- Jon had installed the wrong fork before the session ([s:T2]).", "session", R2())
    check("m3-mention-only-not-flagged", c["m3_flags"], [])
    c = evaluate_claim("- The operation is Option B, a cleaner decision ([s:T2]).", "session", R2())
    check("m3-decision-word-alone-not-flagged", c["m3_flags"], [])
    c = evaluate_claim("- BPE splits rare words into subword units ([s:T2]).", "session", R2())
    check("m3-descriptive-ok", c["m3_flags"], [])

    # 9. M5 population catches a quoted span with no Jon mention
    c = evaluate_claim("- The instruction was “freeze on exposure, act on hygiene” ([s:T1]).", "session", R2())
    check("m5-quote-population", c["is_jon"], True)

    # 10. the sampling frame is populated for resolvable anchors — the sampled
    # arm has nothing to adjudicate if this is empty
    c = evaluate_claim("- Something descriptive ([s:T1]).", "session", R2())
    check("sampling-frame", c["resolved_anchors"], [("s", 1, "H", "raw.md")])

    # 11. coverage_class exclusion — an untraced-by-design page is dropped entirely from
    # scan()'s claims (not just excused at evaluate time), so it can never inflate or
    # deflate M1-M5. Build a tiny fixture tree to prove it end-to-end, not just unit-test
    # the flag-reading.
    import tempfile, shutil
    tmproot = tempfile.mkdtemp(prefix="e2-selftest-")
    try:
        amdir = os.path.join(tmproot, "wiki", "references", "agent-memory")
        os.makedirs(amdir, exist_ok=True)
        srcdir = os.path.join(tmproot, "wiki", "sources", "x")
        os.makedirs(srcdir, exist_ok=True)
        with open(os.path.join(amdir, "fixture.md"), "w", encoding="utf-8") as fh:
            fh.write(
                "---\ntitle: fixture\ncoverage_class: untraced-by-design\n"
                'coverage_class_reason: "test fixture"\n---\n\n'
                "# fixture\n\n## Key Claims\n\n- An uncited claim with no anchor at all.\n"
            )
        with open(os.path.join(srcdir, "real.md"), "w", encoding="utf-8") as fh:
            fh.write(
                "---\ntitle: real\nsource_kind: session\n---\n\n"
                "# real\n\n## Key Claims\n\n- A cited claim ([real:T1]).\n"
            )
        pages, _ = scan(tmproot)
        check("exempt-page-found", sum(1 for p in pages if p.get("is_untraced")), 1)
        check("exempt-page-has-zero-claims-scanned",
              [p["claims"] for p in pages if p.get("is_untraced")], [[]])
        m = methods([p for p in pages if not p["is_concept"] and not p.get("is_untraced")])
        check("exempt-not-in-M1-denominator", m["M1"]["d"], 1)  # only 'real''s claim
    finally:
        shutil.rmtree(tmproot, ignore_errors=True)

    for f in fails:
        print(f)
    if fails:
        print(f"\nSELFTEST: {len(fails)} failure(s)")
        return 1
    print("SELFTEST: 11/11 groups passed")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="page tree to measure (may be an old commit's worktree)")
    ap.add_argument("--raw-root", default=None,
                    help="where raw/transcripts lives; defaults to --root. Point this at the LIVE repo "
                         "when --root is a historical worktree — raw/ is gitignored, so an old "
                         "commit has no transcripts and M3 would silently read as zero-resolvable.")
    ap.add_argument("--slices", action="store_true", help="add category tables (amendment 2)")
    ap.add_argument("--cohorts", action="store_true",
                    help="add date-cohort tables split on 2026-07-01/07-13 (T-03, Jon 2026-08-02)")
    ap.add_argument("--m3-detail", action="store_true", help="list every M3 flag, not a sample")
    ap.add_argument("--threshold", type=float, default=95.0)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--legacy", action="store_true", help="original (a)/(b) checks")
    ap.add_argument("--sample", type=int, default=None,
                    help="emit N stratified anchors for support-adjudication (the sampled M3 arm)")
    ap.add_argument("--seed", type=int, default=20260725, help="sample seed (determinism)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    pages, resolver = scan(a.root, limit=a.limit, raw_root=a.raw_root)
    if not pages:
        print("ERROR: no pages found — check --root", file=sys.stderr)
        return 2
    if a.sample:
        return emit_sample(pages, a.sample, a.seed, a.root)
    if a.json:
        src = [p for p in pages if not p["is_concept"] and not p.get("is_untraced")]
        print(json.dumps({
            "method_version": METHOD_VERSION,
            "tree": tree_stamp(a.root),
            "raw_corpus": os.path.abspath(a.raw_root or a.root),
            "pages": len(src),
            "claims": sum(len(p["claims"]) for p in src),
            "all": methods(src),
            "bold": methods(src, "bold"),
            "nontrivial": methods(src, "nontrivial"),
        }, indent=2))
        return 0
    if a.legacy:
        return legacy_report(pages)
    return report(pages, resolver, show_slices=a.slices,
                  m3_detail=a.m3_detail, threshold=a.threshold,
                  root=a.root, raw_root=a.raw_root, show_cohorts=a.cohorts)


if __name__ == "__main__":
    sys.exit(main())
