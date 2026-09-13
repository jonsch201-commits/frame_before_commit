#!/usr/bin/env python3
"""fbc_decision_log.py — one line per FBC RUN, answering the only question Jon asked.

WHY THIS EXISTS — Jon, April 2026, verbatim, still open in August
------------------------------------------------------------------
    "There's no feedback loop from your actual life into this project. The wiki logs test runs.
     **Nothing logs whether the protocol changed a real decision**, caught a real blind spot, or
     helped you at home or at work. That data would tell us if we're actually moving toward the
     personal goal - and right now it doesn't exist anywhere."

Recorded across `meta-pm-2026-04-25-93d70b.md`, `project-manager-2026-04-30-f8cc02.md`,
`chat-2026-05-22-f8cc02`; still listed open 2026-08-02; rediscovered independently by
`wiki/intake-triage/B-8-improving-fbc-and-gbs-2026-08-06.md` s9.6, which made it **item 0** of its
recommended sequence: build the decision log BEFORE improving the protocol.

THE UNIT IS THE RUN. THE QUESTION IS: DID THE VERDICT MOVE.
-------------------------------------------------------------
It is explicitly **not** "were deltas emitted." That metric already exists and it produced
**787 `[DELTA:` hits, 263 distinct, 195 of them Discipline Rule 6's template emitted verbatim**
(`wiki/references/skills/frame-before-commit.md` s3). The reason it carries no information is
structural and is stated in that page s4:

    A [DELTA] is scored PER BRANCH. The verdict is scored ONCE. Nothing connects them.

A branch that adds a caveat truthfully answers "yes, I changed what commit would have said" while
the headline verdict never moves. The flagship run `chat-2026-07-18-a8bbda` emitted three honest
branch-credited deltas under a `[COMMIT]` whose verdict was word-for-word its own pre-branch
instinct - and its `[META]` scored that non-movement "the strongest signal in the run."

NO SEAL => UNKNOWN. NEVER "NO CHANGE". THIS IS THE WHOLE POINT OF THE LOG.
----------------------------------------------------------------------------
FBC's own Condition A (`research/01-FBC-Improvement/harness/condition-A-2026-05-21.md:83-87`):

    "the model is not a reliable narrator of what it would have said had a branch not existed."

So the retrospective line "Without branching, I would have said: X", written at `[COMMIT]` after
every branch is visible, is **not** a seal and is **not** admissible as evidence of movement or of
non-movement. A run without a pre-branch seal cannot report whether its verdict moved. That run is
logged `UNKNOWN`. It is not logged `unmoved`, and it does not count toward the falsifier.

The seal became mandatory in all modes on 2026-08-06 (`skills/frame-before-commit/SKILL.md`,
"Pre-Branch Seal (Mandatory - All Modes)", Discipline Rule 12). Every run before that date was
generated under a protocol that did not ask for one, so **a large UNKNOWN column is the expected
result and is itself the finding** - not a defect in this script.

WHY THIS IS NOT A SEVENTH SCANNER OVER THE SAME CORPUS
--------------------------------------------------------
It walks nothing. It imports, and the reuse is total for everything already solved:

  * `skill_record.analyse_fbc`  - run shape, delta classes, convergence. The three-arm genuine-run
    test (numeric header / real [BRANCH REGISTRY] / [COMMIT] carrying the mandated opening
    sentence) is that file's, not a second definition. If it is wrong it is wrong in one place.
  * `skill_record.REEMISSION` / `.SELF_AUDIT` - the two path deflators. An audit of FBC emits FBC
    markers; this file is an audit of FBC, so it must be deflated by the same rule it applies.
  * `skill_record.load_rows` -> `corpus_index.require_index` - the index and its READ STATE. A
    stale read is UNKNOWN, printed at the top, never a bare count.
  * `gbs_record.spans` (transitively) - the ratified turn splitter.

WHAT IT ADDS, AND IT IS ONLY TWO THINGS
-----------------------------------------
 1. **Seal detection, POSITIONAL.** A seal marker is a seal only if it stands before the first
    branch marker in the text. The same literal appearing after the branches is retrospective
    narration and is classified `NONE`, which is the distinction the log exists to draw.
 2. **Verdict grading against the sealed text.** MOVED / UNMOVED / SEALED-UNGRADED, and the
    grader refuses to guess: where the comparison is not mechanically decidable it says so and
    asks for a cold grader rather than emitting a number.

It also scans **deposits** (`wiki/intake-triage/`, `research/01-FBC-Improvement/harness/`) as well
as the transcript corpus, because the only sealed runs in existence were published there and are
not in `raw/transcripts/` at all. Denominators are printed for both sets separately.

Exit code is **always 0.** An instrument, not a gate. It READS `raw/`; it writes only its own
report file under `wiki/tracker/`.

Usage:
  fbc_decision_log.py                 # report to stdout, with denominators
  fbc_decision_log.py --write         # regenerate wiki/tracker/fbc-decision-log.md
  fbc_decision_log.py --unknown       # enumerate the UNKNOWN column
  fbc_decision_log.py --self-test     # negative controls first
"""
import argparse
import hashlib
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

import corpus_index as CI                          # noqa: E402
import skill_record as SR                          # noqa: E402  run shape + deflators, REUSED

REPO = SR.REPO
OUT = REPO / "wiki" / "tracker" / "fbc-decision-log.md"

# Deposit paths. Runs get PUBLISHED here; the transcript that produced them may not exist yet.
DEPOSITS = ("wiki/intake-triage/*.md", "research/01-FBC-Improvement/harness/*.md")

# ADDITIVE SELF-AUDIT DEFLATOR — and the reason it exists is a finding, not a preference.
#
# REPAIRED UPSTREAM 2026-08-07 — this block is kept because the deposit-side deflator below is
# still load-bearing, and because deleting the diagnosis would leave the repair unexplained.
#
# `skill_record.SELF_AUDIT` intends to catch B-8, the audit-of-FBC that quotes FBC runs verbatim.
# Until 2026-08-07 it did not. Its alternative `b-8-improve` requires "improve"; the file is
# `B-8-improving-fbc-and-gbs-2026-08-06.md` — "improv" + "ing". Its alternative `fbc.?gbs` allows
# ONE character between; the filename has five ("fbc-and-gbs"). **The deflator misses its own
# headline target by two characters, in both alternatives independently.**
#
# It never bit `skill_record.py` because B-8 lives under `wiki/` and that file scans only
# `raw/transcripts/`. It bites HERE, because this file scans deposits — which is exactly the
# "a fix that was never exercised is not a fix" class already on this repo's record.
#
# It was first corrected additively HERE rather than by editing `skill_record.py`, because the
# published counts in `wiki/references/skills/frame-before-commit.md` cite that module and
# silently changing a deflator under a published number is the divergence defect this instrument
# exists to avoid reproducing. **B-8 then repaired it upstream on 2026-08-07 and printed the
# before/after (5 -> 18 of 1,172), which is the form that change had to take.** This deflator
# STAYS: it covers deposit paths (`wiki/intake-triage/`, `references/skills/`) that
# `skill_record.SELF_AUDIT` still does not name, and two deflators that agree cost nothing while
# one that silently narrows costs a headline.
#
# NOTE what is deliberately NOT deflated: `research/01-FBC-Improvement/harness/condition-*.md`.
# Those are runs ABOUT FBC, but they are genuine executed runs and belong in the log. "About FBC"
# is not the deflation criterion; "quotes someone else's run" is.
# `skill-session-record` (not `gbs-skill-session-record`): upstream names only the GBS agent, so
# the FBC one — `code-2026-08-06-a8c9fb-general-purpose-fbc-skill-session-record-…`, the agent that
# WROTE the published record page — is not deflated by it. Same two-character class as B-8. The
# self-contamination guard missed BOTH of today's FBC-audit agents.
DEPOSIT_SELF_AUDIT = re.compile(
    r"b-8-improv|improving-fbc|fbc[-_ ]and[-_ ]gbs|fbc-decision-log|"
    r"skill[-_ ]session[-_ ]record|skill[-_]record|references/skills/", re.I)

# STRUCTURAL VENUE — not a deflator. Where a run happened changes what it is evidence OF.
# Jon's April question is about real decisions in HIS work. A run inside a dispatched subagent is
# a genuine run and is logged as one, but it is an agent reasoning about its own assigned task —
# it is not the protocol changing a decision Jon made. Reported as its own column rather than
# folded into a single "runs" number, because folding them is how "FBC is still in use" gets
# asserted from a month in which every run belonged to an audit OF FBC.
SUBAGENT = re.compile(r"/subagents/", re.I)
TICKET = re.compile(r"\bB-(\d+)\b", re.I)


def venue_of(rel, source):
    if source == "deposit":
        return "DEPOSIT"
    return "SUBAGENT" if SUBAGENT.search(rel) else "MAIN"


def dedupe_published(rows):
    """Drop the agent TRANSCRIPT of a run whose published DEPOSIT is also logged.

    Found by this file's first full run: B-5 appeared twice — once as
    `wiki/intake-triage/B-5-…md` (the published deposit, which carries the seal) and once as
    `…/subagents/f01909/code-2026-08-06-ab3581-general-purpose-b-5-how-cfl-and-personal-talk.md`
    (the transcript of the agent that wrote it). **One run, two files, and the log would have
    reported it as two.** Joined on ticket id + date; the deposit wins because it is the artifact
    the seal and the [COMMIT] scoring actually live in.
    """
    keys = {(TICKET.search(r["path"]).group(1).lower(), r["date"])
            for r in rows if r["source"] == "deposit" and TICKET.search(r["path"])}
    out, dropped = [], []
    for r in rows:
        t = TICKET.search(r["path"])
        if (r["source"] != "deposit" and t
                and (t.group(1).lower(), r["date"]) in keys):
            dropped.append(r)
            continue
        out.append(r)
    return out, dropped


def is_self_audit(rel):
    """Either deflator fires. Both are needed; see DEPOSIT_SELF_AUDIT for why."""
    return bool(SR.SELF_AUDIT.search(rel) or DEPOSIT_SELF_AUDIT.search(rel))

# =================================================================================================
# THE SEAL — literals read out of SKILL.md, not recalled
# =================================================================================================
# SKILL.md:91,168 (pure/directed, added 2026-08-06) and :230 (extended, since 2026-07 origin).
# The prose forms are B-5's, which sealed to a file before the bracket literal existed.
SEAL_MARK = re.compile(
    r"\[pre-?\s?branch\s+seal\]|\[pre-?\s?branch\s+instinct\s+commit\]|"
    r"the\s+sealed\s+instinct|sealed\s+instinct\s*\(verbatim|"
    r"instinct\s+was\s+written\s+to\s+a\s+file|"
    r"written\s+to\s+a\s+file\s+before\s+(?:a\s+single\s+)?branch",
    re.I,
)
# Evidence the seal is a FILE, not just in-context text. SKILL.md:68 mandates the file.
SEAL_TO_FILE = re.compile(
    r"written\s+to\s+a\s+file|save[d]?\s+(?:the\s+)?(?:pre-?branch\s+)?instinct\s+to\s+a\s+file|"
    r"seal(?:ed)?\s+(?:it\s+)?to\s+(?:a\s+)?file|sealed\s+file",
    re.I,
)
# The FIRST branch. A seal must stand before this offset or it is narration.
FIRST_BRANCH = re.compile(
    r"\[branch\s+registry\]|\[b1\b|\bB1T1\b|\[branches\s*[-–—]", re.I)

# SKILL.md:78 — the seal is only useful if [COMMIT] is SCORED against it.
SCORED_AGAINST_SEAL = re.compile(
    r"sealed\s+commitment|against\s+the\s+sealed\s+text|checkable\s+against\s+sealed|"
    r"scored\s+against\s+(?:that\s+|the\s+)?sealed", re.I)
# THE AUTHORITATIVE FORM — a run scoring itself item-by-item against the seal states a COUNT.
# This is what "one line, checkable" means: a reader can open the file and check N against M.
SEAL_SCORE_LINE = re.compile(
    r"\b(\w+)\s+of\s+the\s+(\w+)\s+sealed\s+commitments?\s+(?:were|was)\s+overturned", re.I)
# Movement, stated against the seal. Weaker than SEAL_SCORE_LINE and used only if that is absent.
MOVED_LANG = re.compile(
    r"\b(?:were|was)\s+overturned\b|"
    r"sealed\s+commitment[^.\n]{0,80}\b(?:fails|falls|does not survive|is wrong|replaced|"
    r"withdrawn|inverted|overturned)\b", re.I)
# NEGATION GUARD. Found by this file's own first full run: `\bovertur(?:n|ned|ns)\b` matched
# "B1 sharpened an instinct; it did **not** overturn one" and would have scored a run MOVED on a
# sentence saying the opposite. A movement detector that fires on its own negation is the
# unfalsifiable-instrument defect this log was built to stop reproducing, so it is guarded and
# the guard is a named negative control in the self-test.
NEGATOR = re.compile(r"\b(?:not|never|no|nothing|none|n't|without)\b[^.]{0,40}$", re.I)
# Non-movement, stated against the seal.
UNMOVED_LANG = re.compile(
    r"all\s+(?:four|three|two|\d+)\s+sealed\s+commitments\s+(?:survive|stood|stand|held)|"
    r"sealed\s+(?:text|instinct|commitments?)[^.\n]{0,60}\b(?:unchanged|survives? intact|"
    r"stands? unchanged)\b|no\s+sealed\s+commitment\s+was\s+overturned", re.I)
# How many sealed commitments the COMMIT actually cites back. A checkable integer.
SEAL_CITE = re.compile(r"sealed\s+commitment\s*\(?(\d+)\)?", re.I)

MODE = re.compile(r"\[frame-before-commit\s*[-–—]{1,2}\s*(pure|directed|extended)", re.I)
BRANCH_TOKEN = re.compile(r"^\s*\**\[?B([1-9])\]?\b", re.I | re.M)

SEAL_FILE, SEAL_INLINE, SEAL_NONE = "SEAL-FILE", "SEAL-INLINE", "NONE"
V_MOVED, V_UNMOVED, V_UNGRADED, V_UNKNOWN = "MOVED", "UNMOVED", "SEALED-UNGRADED", "UNKNOWN"


def seal_state(text):
    """(state, offset) — POSITIONAL. A seal literal after the first branch is narration, not a seal.

    This is the single judgment the whole log rests on, so it is one small function and it is
    tested in both directions. `[COMMIT]`'s "Without branching, I would have said" is deliberately
    NOT in `SEAL_MARK`: that sentence is the unreliable narrator FBC's Condition A names, and
    admitting it would reproduce the defect the log exists to measure.
    """
    m = SEAL_MARK.search(text)
    if not m:
        return SEAL_NONE, None
    b = FIRST_BRANCH.search(text)
    if b is not None and m.start() > b.start():
        return SEAL_NONE, None                  # retrospective. Not a seal.
    return (SEAL_FILE if SEAL_TO_FILE.search(text[:m.end() + 1200]) else SEAL_INLINE), m.start()


def _first_unnegated(pat, text):
    """The first match of `pat` NOT preceded by a negator in the same sentence. See NEGATOR."""
    for m in pat.finditer(text):
        if not NEGATOR.search(text[max(0, m.start() - 60): m.start()]):
            return m
    return None


def _excerpt(text, m, before=0, after=90):
    """The matched claim, ended at its own sentence boundary — 'one line, checkable'."""
    tail = text[m.end(): m.end() + after]
    cut = tail.find(".")
    s = text[max(0, m.start() - before): m.end() + (cut + 1 if cut != -1 else len(tail))]
    return re.sub(r"\s+", " ", s.replace("\n", " ")).strip()


def verdict_state(text, seal):
    """(verdict, how, n_cites) — graded ONLY where a seal exists. No seal => UNKNOWN, never 'no'."""
    if seal == SEAL_NONE:
        return V_UNKNOWN, "no pre-branch seal — the run cannot report whether its verdict moved", 0
    cites = len(set(SEAL_CITE.findall(text)))
    if not SCORED_AGAINST_SEAL.search(text):
        return (V_UNGRADED, "sealed, but [COMMIT] does not cite the sealed text — needs a cold "
                            "grader (SKILL.md:78 requires the COMMIT be scored against the seal)",
                cites)
    # AUTHORITATIVE FIRST: an item-by-item count against the seal. `N of M overturned` decides
    # both directions on its own — N>0 is MOVED, N==0 is UNMOVED — and is checkable by opening
    # the file and counting.
    m = _first_unnegated(SEAL_SCORE_LINE, text)
    if m is not None:
        n = m.group(1).lower()
        zero = n in ("zero", "none", "no", "0")
        return (V_UNMOVED if zero else V_MOVED), _excerpt(text, m, 0, 40), cites
    m = _first_unnegated(MOVED_LANG, text)
    if m is not None:
        return V_MOVED, _excerpt(text, m), cites
    m = _first_unnegated(UNMOVED_LANG, text)
    if m is not None:
        return V_UNMOVED, _excerpt(text, m), cites
    return V_UNGRADED, "sealed and cited, but movement is not mechanically decidable — cold grader", cites


def segment_runs(text):
    """[str] — one segment per mandated run header, so a file holding two runs yields two rows.

    Segmentation is on the NUMERIC header only (SKILL.md:69's mandated opener with a real branch
    count). A file with no numeric header is one segment, because there is nothing to split on
    that is not also produced by a passing quotation.
    """
    starts = [m.start() for m in SR.RUN_HEADER_NUMERIC.finditer(text)]
    if len(starts) < 2:
        return [text]
    bounds = starts + [len(text)]
    segs = [text[bounds[i]:bounds[i + 1]] for i in range(len(starts))]
    if starts[0] > 0:
        segs.insert(0, text[:starts[0]])
    return segs


def run_id(rel, date, i):
    h = hashlib.sha1(rel.encode()).hexdigest()[:6]
    d = (date or "UNKNOWN").replace("-", "")
    return f"FBC-{d}-{h}" + (f"-r{i + 1}" if i else "")


def analyse(rel, text, date, source):
    """[row] — zero or more logged runs from one file. Pure; writes nothing."""
    rows = []
    for i, seg in enumerate(segment_runs(text)):
        a = SR.analyse_fbc({"__seq__": [("A", seg)]})
        if a is None or not a["genuine_run"]:
            continue
        seal, _off = seal_state(seg)
        verdict, how, cites = verdict_state(seg, seal)
        mm = MODE.search(seg)
        nb = SR.RUN_HEADER_NUMERIC.search(seg)
        rows.append(dict(
            id=run_id(rel, date, len(rows)), date=date or "UNKNOWN", path=rel, source=source,
            mode=(mm.group(1).upper() if mm else "UNDECLARED"),
            # "0 branches" is never a fact about a run — it means the count was not recoverable.
            # Printed "?", because a zero that means "unmeasured" is the same defect as an UNKNOWN
            # verdict printed as "unmoved".
            branches=(re.search(r"([2-9]|1[0-9])", nb.group(0)).group(1) if nb
                      else (str(len(set(BRANCH_TOKEN.findall(seg))))
                            if set(BRANCH_TOKEN.findall(seg)) else "?")),
            seal=seal, verdict=verdict, how=how, seal_cites=cites,
            venue=venue_of(rel, source),
            deltas_nonempty=a["n_deltas"] - a["d_empty"], deltas_raw=a["n_deltas"],
            convergence=a["convergence"], commit=a["commit"],
            reemission=bool(SR.REEMISSION.search(rel)),
            self_audit=is_self_audit(rel),
        ))
        if len(rows) > 8:                       # a file claiming 9 runs is a paste, not a session
            break
    return rows


# Cheap prefilter: spans() output is a subset of the file bytes, so a file whose bytes carry no FBC
# literal cannot yield a run. Keeps the numbers identical to skill_record's while skipping the
# expensive splitter on ~90% of the corpus.
ANY_LITERAL = re.compile(
    r"\[frame-before-commit|\[branch registry\]|\[commit\]|without branching", re.I)


def collect(max_files=None):
    rows, how, read = SR.load_rows()
    out, n_corpus, n_dep = [], 0, 0
    paths = sorted(rows)
    if max_files:
        paths = paths[:max_files]
    for rel in paths:
        p = REPO / rel
        if not p.is_file():
            continue
        n_corpus += 1
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if not ANY_LITERAL.search(raw):
            continue
        sp = SR.spans(p)                          # the ratified splitter, not a second reader
        if not sp:
            continue
        text = "\n".join(t for _, t in sp.get("__seq__", []))
        out += analyse(rel, text, rows[rel].get("date", "UNKNOWN"), "corpus")
    for pat in DEPOSITS:
        for p in sorted(REPO.glob(pat)):
            rel = p.relative_to(REPO).as_posix()
            n_dep += 1
            raw = p.read_text(encoding="utf-8", errors="replace")
            if not ANY_LITERAL.search(raw):
                continue
            d = re.search(r"(20\d\d-\d\d-\d\d)", raw[:2000]) or re.search(r"(20\d\d-\d\d-\d\d)", rel)
            out += analyse(rel, raw, d.group(1) if d else "UNKNOWN", "deposit")
    return out, n_corpus, n_dep, how, read, len(rows)


def partition(all_rows):
    """(original, deflated, dup) — path deflators, then the deposit/transcript dedupe."""
    kept = [r for r in all_rows if not r["reemission"] and not r["self_audit"]]
    defl = [r for r in all_rows if r not in kept]
    orig, dup = dedupe_published(kept)
    return orig, defl, dup


# A doc-READING agent quotes `[COMMIT]` and "converged" because it was sent to read FBC's own
# pages. `wiki/references/skills/frame-before-commit.md` s1 excluded 14 of these BY HAND to get
# from 69 original runs to 51 "strong" runs. A hand exclusion is not reproducible, so it is
# written down here as a pattern — which is the only way the two numbers can ever be compared
# again.
DOC_READER = re.compile(
    r"explore-read|read-fbc|wiki-fbc|fbc-skill|citation-audit|verify-quote|"
    r"explore-search|corpus-read|-review-wiki", re.I)


def reconcile(orig):
    """dict — how this log's run count relates to the published one. Never leave a delta unexplained.

    `wiki/references/skills/frame-before-commit.md` s1 published **89 run-shaped -> 69 original ->
    51 strong**, over 1,167 transcripts, counting FILES, corpus only. This file counts run
    SEGMENTS, over 1,172 transcripts, corpus PLUS deposits. Those are four different denominators
    and they cannot be compared until they are named, so they are named.
    """
    corpus = [r for r in orig if r["source"] == "corpus"]
    dep = [r for r in orig if r["source"] == "deposit"]
    readers = [r for r in corpus if DOC_READER.search(r["path"])]
    return dict(
        segments=len(orig), corpus_segments=len(corpus), deposit_segments=len(dep),
        corpus_files=len({r["path"] for r in corpus}),
        deposit_files=len({r["path"] for r in dep}),
        multi_run_files=len(corpus) - len({r["path"] for r in corpus}),
        doc_readers=len({r["path"] for r in readers}),
        corpus_files_minus_readers=len({r["path"] for r in corpus}
                                       - {r["path"] for r in readers}),
    )


FALSIFIER = """\
**THE FALSIFIER, AND IT IS BINDING ON THE PROTOCOL, NOT ON THE LOG.**

B-8 s9.6 stated it: *"after 10 logged runs, if **zero** show FBC changing what Jon actually did,
the protocol is not earning its cost on live decisions regardless of its scores. If >=3 do, it is
- and the entire scored-test-suite apparatus can be retired in favour of the log."*

**One deviation, stated rather than smuggled: only SEALED runs count toward the 10.** An unsealed
run cannot report whether its verdict moved (FBC Condition A - *"the model is not a reliable
narrator of what it would have said had a branch not existed"*), so counting unsealed runs as
"showed no change" would let the protocol pass its own falsifier on evidence that does not exist.
The clock therefore starts at the seal mandate (2026-08-06), and **the log's own first finding is
that the clock has barely started.**

*An instrument that cannot fail its own subject is the defect FBC already has* - Discipline Rule 7
blesses convergence while Self-Scoring red-flags zero deltas, so no instrument the protocol carries
can call a run a failure (`wiki/references/skills/frame-before-commit.md` s4, 6 runs measured in
that cell). This log can fail FBC. That is its point.
"""


def render(rows, n_corpus, n_dep, how, read, n_index):
    orig, defl, dup = partition(rows)
    sealed = [r for r in orig if r["seal"] != SEAL_NONE]
    moved = [r for r in sealed if r["verdict"] == V_MOVED]
    unmoved = [r for r in sealed if r["verdict"] == V_UNMOVED]
    ungraded = [r for r in sealed if r["verdict"] == V_UNGRADED]
    unknown = [r for r in orig if r["verdict"] == V_UNKNOWN]
    graded = len(moved) + len(unmoved)

    L = []
    A = L.append
    A("---")
    A('title: "FBC decision log — did the verdict move?"')
    A("kind: decision-log")
    A("status: v1 — GENERATED, do not hand-edit")
    A("generated_by: scripts/audit/fbc_decision_log.py")
    A(f"corpus_current_through: export 2026-08-06 ({n_index} transcripts indexed)")
    A("---")
    A("")
    A("# FBC decision log")
    A("")
    A("**One line per run. The question is whether the VERDICT moved — not whether deltas were "
      "emitted.**")
    A("")
    A("Jon, April 2026, verbatim, and the gap was still open on 2026-08-02:")
    A("")
    A("> *There's no feedback loop from your actual life into this project. The wiki logs test "
      "runs. **Nothing logs whether the protocol changed a real decision**, caught a real blind "
      "spot, or helped you at home or at work. That data would tell us if we're actually moving "
      "toward the personal goal — and right now it doesn't exist anywhere.*")
    A("")
    A("Regenerate: `python scripts/audit/fbc_decision_log.py --write`. **This file is derived. "
      "Hand-edits are lost on the next run and will diverge silently in the meantime** — which is "
      "the failure class this repo keeps paying for.")
    A("")
    A("---")
    A("")
    A("## Denominators")
    A("")
    A(f"| | count |")
    A(f"|---|---|")
    A(f"| transcripts in `corpus_index` | {n_index} |")
    A(f"| transcripts re-read here | {n_corpus} |")
    A(f"| deposit files re-read (`wiki/intake-triage/`, `research/…/harness/`) | {n_dep} |")
    A(f"| index read via | {how} |")
    A(f"| **run-shaped segments found** | **{len(rows)}** |")
    A(f"| …deflated (re-emission / this audit's own agents) | {len(defl)} |")
    A(f"| …deduped (a deposit and its own agent transcript are ONE run) | {len(dup)} |")
    A(f"| **ORIGINAL RUNS LOGGED** | **{len(orig)}** |")
    for v in ("MAIN", "SUBAGENT", "DEPOSIT"):
        A(f"| …in a {v} session | {sum(1 for r in orig if r['venue'] == v)} |")
    A(f"| of those, **SEALED** (pre-branch instinct, positionally before the first branch) "
      f"| **{len(sealed)}** |")
    A(f"| …of which sealed **to a file** (SKILL.md:68's mandate) "
      f"| {sum(1 for r in sealed if r['seal'] == SEAL_FILE)} |")
    A(f"| **verdict MOVED** | **{len(moved)}** |")
    A(f"| **verdict UNMOVED** | **{len(unmoved)}** |")
    A(f"| SEALED but not mechanically gradable (needs a cold grader) | {len(ungraded)} |")
    A(f"| **UNKNOWN — no seal, so movement is unreportable** | **{len(unknown)}** |")
    A("")
    A(f"**{len(unknown)} of {len(orig)} original runs are UNKNOWN, and that is the finding, not a "
      f"gap in the instrument.** The pre-branch seal became mandatory in all modes on 2026-08-06 "
      f"(`skills/frame-before-commit/SKILL.md`, Discipline Rule 12). Every run before that date "
      f"was produced by a protocol that never asked for one. **A backfill that returned a "
      f"confident verdict for each of those runs would have fabricated it** — the retrospective "
      f"*\"Without branching, I would have said…\"* line is precisely the narration FBC's own "
      f"Condition A rules inadmissible.")
    A("")
    A("### Reconciliation with the published run count")
    A("")
    # DERIVED, NOT RECORDED. This sentence read "This page says 125" as a literal while the
    # table above it computed 119 — a stale number hardcoded inside the very generator built
    # to close the derive-don't-record class, found 2026-08-07 by regenerating and reading the
    # output instead of the docstring. The count now comes from `orig`, so it cannot diverge.
    A(f"`wiki/references/skills/frame-before-commit.md` §1 published **89 run-shaped → 69 "
      f"original → 51 strong**. This page says {len(orig)}. **Those are not the same quantity "
      f"and the difference is enumerated here rather than left for a reader to trip over** — "
      f"an unexplained disagreement between two published numbers is the failure this repo "
      f"keeps paying for.")
    A("")
    rc = reconcile(orig)
    A("| step | count |")
    A("|---|---|")
    A(f"| this log, original run **segments** | {rc['segments']} |")
    A(f"| …from the transcript corpus | {rc['corpus_segments']} |")
    A(f"| …from deposits (the published page scanned `raw/transcripts/` only) "
      f"| {rc['deposit_segments']} |")
    A(f"| distinct corpus **files** (segments minus {rc['multi_run_files']} extra runs inside "
      f"multi-run files) | **{rc['corpus_files']}** |")
    A(f"| …minus doc-**reading** agents ({rc['doc_readers']} by pattern; the page excluded 14 by "
      f"hand) | {rc['corpus_files_minus_readers']} |")
    A("| published **original runs** | 69 |")
    A("| published **strong runs** (hand-verified) | 51 |")
    A("")
    A(f"**{rc['corpus_files']} against 69 is agreement within one file**, which is the real "
      "cross-check: two independently-written detectors over the same corpus land on the same "
      "set. The four remaining differences are **segments vs files** (a session running FBC "
      "twice is two runs here and one file there), **1,172 vs 1,167 indexed transcripts**, "
      "**corpus + deposits vs corpus alone**, and a **reproducible doc-reader pattern vs a hand "
      "exclusion**. The residual — the page's hand-verified 69→51 step — no script reproduces, "
      "and it should not be quoted as if one did.")
    A("")
    A("---")
    A("")
    A("## The falsifier")
    A("")
    A(FALSIFIER)
    A("")
    A("### Current standing")
    A("")
    A(f"| | |")
    A(f"|---|---|")
    A(f"| sealed runs graded so far | **{graded} of 10** |")
    A(f"| of those, verdict MOVED | **{len(moved)}** |")
    A(f"| of those, verdict UNMOVED | **{len(unmoved)}** |")
    A(f"| sealed, awaiting a cold grader | {len(ungraded)} |")
    v = ("NOT YET TESTABLE — fewer than 10 sealed runs exist." if graded < 10
         else ("FBC FAILS ITS OWN FALSIFIER — 10 sealed runs, zero moved." if not moved
               else ("FBC PASSES — >=3 sealed runs moved the verdict." if len(moved) >= 3
                     else "INCONCLUSIVE — 10 graded, 1-2 moved.")))
    A(f"| **verdict on the protocol** | **{v}** |")
    A("")
    A("---")
    A("")
    A("## The log")
    A("")
    A("`seal`: `SEAL-FILE` = instinct written to a file before any branch · `SEAL-INLINE` = seal "
      "block emitted before the first branch but held in context · `NONE` = no seal, **or a seal "
      "literal appearing only after the branches, which is narration**.")
    A("")
    A("`venue`: `MAIN` = a working session · `SUBAGENT` = a dispatched agent reasoning about its "
      "own assigned task · `DEPOSIT` = a published artifact. **A SUBAGENT run is a real run and "
      "is logged as one, but it is not the protocol changing a decision Jon made** — which is "
      "what his April question asked about.")
    A("")
    A("| run | date | venue | mode | br | seal | verdict | how — checkable | session |")
    A("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(orig, key=lambda r: (r["date"], r["id"]), reverse=True):
        how1 = r["how"].replace("|", "/")
        if len(how1) > 150:
            how1 = how1[:147] + "…"
        A(f"| `{r['id']}` | {r['date']} | {r['venue']} | {r['mode']} | {r['branches']} | "
          f"{r['seal']} | **{r['verdict']}** | {how1} | `{r['path']}` |")
    A("")
    A("---")
    A("")
    A("## What this log cannot recover, stated so nobody reads the blanks as zeroes")
    A("")
    A("1. **Whether an unsealed run's verdict moved.** Not hard, not expensive — *impossible*. "
      "The counterfactual was never recorded and the only witness is a narrator the protocol "
      "itself rules unreliable. This covers the large majority of the record and no future work "
      "recovers it.")
    A("2. **Whether a MOVED verdict changed what Jon actually DID.** The log reads the run's own "
      "artifact. Jon's downstream action is not in the corpus. Answering that needs one line from "
      "Jon per run, and nothing mechanical substitutes for it — this is the half of his April "
      "question that stays open.")
    A("3. **Runs held only in conversation.** A run leaving no markers is invisible by "
      "construction, and that class is known non-empty: the flagship 2026-07-18 run emitted "
      "neither the mandated header nor `[BRANCH REGISTRY]` and is missing from every "
      "marker-presence count ever published about FBC.")
    A("4. **Executed vs pasted.** Structure cannot tell a real run from a transcript quoting one. "
      "The two path deflators catch re-emission directories and this audit's own agents; they do "
      "not catch a session that pasted a prior run inline.")
    A("5. **Real vs cosmetic deltas.** Not computed here and not computed anywhere — see "
      "`wiki/references/skills/frame-before-commit.md` s3, which prints it `UNKNOWN` and asks for "
      "the same cold grader B-8's Revised Improvement 2 specifies.")
    A("6. **Dates come from filenames and frontmatter.** A file quoting an earlier run carries the "
      "quoting file's date.")
    A("")
    A("*Generated by `scripts/audit/fbc_decision_log.py` (self-test: negative controls first). It "
      "reads `raw/` and writes nothing there. Nothing in this file is ratified.*")
    return "\n".join(L) + "\n"


def report(rows, n_corpus, n_dep, how, read, n_index, show_unknown=False):
    if read is not None and not read.fresh:
        print(read.banner("fbc_decision_log"))
        print("*** EVERY NUMBER BELOW IS UNKNOWN, NOT MEASURED.")
    orig, defl, dup = partition(rows)
    sealed = [r for r in orig if r["seal"] != SEAL_NONE]
    moved = [r for r in sealed if r["verdict"] == V_MOVED]
    unmoved = [r for r in sealed if r["verdict"] == V_UNMOVED]
    ungraded = [r for r in sealed if r["verdict"] == V_UNGRADED]
    unknown = [r for r in orig if r["verdict"] == V_UNKNOWN]
    print()
    print("=" * 88)
    print("FBC DECISION LOG — did the verdict move?")
    print("=" * 88)
    print("--- DENOMINATORS (in the output, not the docstring) --------------------------")
    print(f"  corpus root                        : {CI.CORPUS}")
    print(f"  transcripts in corpus_index        : {n_index}")
    print(f"  transcripts re-read here           : {n_corpus}")
    print(f"  deposit files re-read              : {n_dep}   ({', '.join(DEPOSITS)})")
    print(f"  index read via                     : {how}")
    print()
    print("--- RUNS ---------------------------------------------------------------------")
    print(f"  run-shaped segments                : {len(rows)}")
    print(f"    deflated (re-emission/self-audit): {len(defl)}")
    print(f"    deduped (deposit + its own agent transcript = ONE run): {len(dup)}")
    print(f"  ORIGINAL RUNS LOGGED               : {len(orig)}")
    print(f"    by venue                         : " + "  ".join(
        f"{v} {sum(1 for r in orig if r['venue'] == v)}"
        for v in ("MAIN", "SUBAGENT", "DEPOSIT")))
    print(f"    SEALED                           : {len(sealed)}   "
          f"(FILE {sum(1 for r in sealed if r['seal'] == SEAL_FILE)} / "
          f"INLINE {sum(1 for r in sealed if r['seal'] == SEAL_INLINE)})")
    print(f"    UNKNOWN (no seal)                : {len(unknown)}   "
          f"** not 'no change' — unreportable **")
    print()
    print("--- VERDICT (graded ONLY where a seal exists) --------------------------------")
    print(f"  MOVED                              : {len(moved)}")
    print(f"  UNMOVED                            : {len(unmoved)}")
    print(f"  SEALED-UNGRADED (needs cold grader): {len(ungraded)}")
    print(f"  UNKNOWN                            : {len(unknown)} of {len(orig)}")
    print()
    print("--- FALSIFIER (B-8 s9.6) -----------------------------------------------------")
    print(f"  10 sealed runs with ZERO moved => protocol is theatre, retire or rebuild.")
    print(f"  sealed runs graded so far          : {len(moved) + len(unmoved)} of 10")
    print(f"  of those, MOVED                    : {len(moved)}")
    print(f"  standing                           : "
          f"{'NOT YET TESTABLE' if len(moved) + len(unmoved) < 10 else ('FAILS' if not moved else 'PASSES')}")
    print("  Deviation, stated: only SEALED runs count. An unsealed run cannot report movement")
    print("  (Condition A), so counting it as 'showed no change' would let FBC pass on evidence")
    print("  that does not exist.")
    print()
    print("--- RECONCILIATION with the published count (51 strong runs) -----------------")
    rc = reconcile(orig)
    print(f"  this log, original run SEGMENTS    : {rc['segments']}")
    print(f"    from the transcript corpus       : {rc['corpus_segments']}")
    print(f"    from deposits                    : {rc['deposit_segments']}   "
          f"(NOT in the published 51 — it scanned raw/transcripts only)")
    print(f"  distinct corpus FILES              : {rc['corpus_files']}   "
          f"(segments minus {rc['multi_run_files']} extra runs inside multi-run files)")
    print(f"    minus doc-READING agents         : {rc['corpus_files_minus_readers']}   "
          f"(excluded {rc['doc_readers']}; the page excluded 14 BY HAND)")
    print(f"  published 'original runs' / 'strong runs' : 69 / 51")
    print("  The two numbers are not comparable until four differences are named: SEGMENTS vs")
    print("  FILES, 1,172 vs 1,167 indexed transcripts, corpus+deposits vs corpus, and a")
    print("  reproducible doc-reader pattern vs a hand exclusion. Named above; the residual is")
    print("  the published page's hand-verified 69->51 step, which no script reproduces.")
    print()
    print("--- WHEN (original runs by month, and how many were sealed) ------------------")
    h = Counter(r["date"][:7] for r in orig if r["date"] != "UNKNOWN")
    hs = Counter(r["date"][:7] for r in sealed if r["date"] != "UNKNOWN")
    print(f"  {'month':<9} {'runs':>6} {'sealed':>7}")
    for k in sorted(h):
        print(f"  {k:<9} {h[k]:>6} {hs[k]:>7}  {'#' * min(h[k], 40)}")
    print()
    print("--- SEALED RUNS, ENUMERATED (this is the whole class) ------------------------")
    for r in sorted(sealed, key=lambda r: r["date"]):
        print(f"  {r['date']}  {r['seal']:<11} {r['verdict']:<16} {r['path']}")
        print(f"              cites {r['seal_cites']} sealed commitment(s) | {r['how'][:110]}")
    print()
    if show_unknown:
        print("--- UNKNOWN, ENUMERATED ------------------------------------------------------")
        for r in sorted(unknown, key=lambda r: r["date"]):
            print(f"  {r['date']}  br={r['branches']:<3} deltas={r['deltas_nonempty']:<3} "
                  f"conv={'Y' if r['convergence'] else 'n'}  {r['path']}")
        print()
    print("--- WHAT WOULD MAKE THIS LOG LIE ---------------------------------------------")
    print("  1. A SEAL LITERAL IS NOT A SEAL unless it stands before the first branch. That is")
    print("     positional and is the one judgment everything else rests on.")
    print("  2. UNKNOWN IS NOT 'UNMOVED'. Any reader collapsing them has undone the log.")
    print("  3. MOVED/UNMOVED ARE READ OFF THE RUN'S OWN SCORING against its sealed text. The")
    print("     seal makes that claim CHECKABLE by a third party; it does not make it verified.")
    print("     A cold grader has not run.")
    print("  4. STRUCTURE CANNOT TELL AN EXECUTED RUN FROM A PASTED ONE.")
    print("  5. WHETHER JON ACTED DIFFERENTLY IS NOT IN THE CORPUS. Half his April question is")
    print("     still open and no instrument closes it.")
    print()


def self_test():
    ok = True

    def chk(label, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")

    print("=== SELF-TEST — fbc_decision_log (negative controls first) ===")

    # ---- NEGATIVE CONTROLS. The direction that matters is the one that INVENTS a verdict. ----
    chk("plain prose yields no seal",
        seal_state("We shipped the page today.")[0] == SEAL_NONE)
    chk("the RETROSPECTIVE line is NOT a seal — this is the whole point of the log",
        seal_state("[BRANCH REGISTRY]\n[B1] ...\n[COMMIT]\nWithout branching, I would have "
                   "said: NO-GO.")[0] == SEAL_NONE)
    chk("a seal literal appearing AFTER the first branch is narration, not a seal",
        seal_state("[BRANCH REGISTRY]\n[B1] ...\nThe sealed instinct was: X")[0] == SEAL_NONE)
    chk("an unsealed run's verdict is UNKNOWN, never UNMOVED",
        verdict_state("[COMMIT] Without branching, I would have said: NO-GO. That stands.",
                      SEAL_NONE)[0] == V_UNKNOWN)
    chk("convergence language in an UNSEALED run does not produce UNMOVED",
        verdict_state("branches converged; the conclusion stands unchanged.",
                      SEAL_NONE)[0] == V_UNKNOWN)

    # ---- POSITIVE CONTROLS ----
    chk("the mandated [PRE-BRANCH SEAL] before [BRANCH REGISTRY] is a seal",
        seal_state("[PRE-BRANCH SEAL]\n(1) ship it.\n[BRANCH REGISTRY]\nB1")[0] != SEAL_NONE)
    chk("EXTENDED mode's [PRE-BRANCH INSTINCT COMMIT] is a seal",
        seal_state("[PRE-BRANCH INSTINCT COMMIT]\nX\n[B1]")[0] != SEAL_NONE)
    chk("a seal held in context only classifies SEAL-INLINE",
        seal_state("[PRE-BRANCH SEAL]\n(1) ship it.\n[BRANCH REGISTRY]")[0] == SEAL_INLINE)
    chk("a seal written to a file classifies SEAL-FILE",
        seal_state("the instinct was written to a file before a single branch was generated"
                   "\n[BRANCH REGISTRY]")[0] == SEAL_FILE)
    chk("B-5's prose seal form is detected (it predates the bracket literal)",
        seal_state("### The sealed instinct (verbatim, pre-branch)\n> ...\n"
                   "### [BRANCH REGISTRY]")[0] != SEAL_NONE)

    # ---- VERDICT GRADING — must refuse to guess. ----
    chk("sealed + overturn language, cited against the seal => MOVED",
        verdict_state("Three of the four sealed commitments were overturned. "
                      "Checkable against sealed commitment (2).", SEAL_FILE)[0] == V_MOVED)
    # NEGATION GUARD — the defect this file's own first full run exposed. A movement detector
    # that fires on "did NOT overturn" is an instrument that cannot report non-movement.
    chk("a NEGATED overturn does not produce MOVED",
        verdict_state("scored against the sealed text. B1 sharpened an instinct; it did not "
                      "overturn one.", SEAL_FILE)[0] != V_MOVED)
    chk("'no sealed commitment was overturned' grades UNMOVED, not MOVED",
        verdict_state("scored against the sealed text: no sealed commitment was overturned.",
                      SEAL_FILE)[0] == V_UNMOVED)
    chk("an explicit ZERO count grades UNMOVED, not MOVED",
        verdict_state("scored against the sealed text: zero of the four sealed commitments "
                      "were overturned.", SEAL_FILE)[0] == V_UNMOVED)
    chk("the authoritative count line beats a later weaker phrase, and is the 'how'",
        verdict_state("Three of the four sealed commitments were overturned. Later it did not "
                      "overturn anything else. Checkable against sealed commitment (1).",
                      SEAL_FILE)[1].lower().startswith("three of the four"))
    chk("sealed + explicit survival, cited => UNMOVED",
        verdict_state("scored against the sealed text: all four sealed commitments survive.",
                      SEAL_FILE)[0] == V_UNMOVED)
    chk("sealed but [COMMIT] never cites the seal => SEALED-UNGRADED, not a verdict",
        verdict_state("[COMMIT] we go with option B.", SEAL_FILE)[0] == V_UNGRADED)
    chk("sealed and cited but movement undecidable => SEALED-UNGRADED, not MOVED",
        verdict_state("Checkable against sealed commitment (1). The design is in s1.",
                      SEAL_FILE)[0] == V_UNGRADED)
    chk("sealed-commitment citations are counted distinctly",
        verdict_state("sealed commitment (1) ... sealed commitment (2) ... sealed commitment (1)",
                      SEAL_FILE)[2] == 2)

    # ---- SEGMENTATION ----
    chk("one numeric header yields one run segment",
        len(segment_runs("[FRAME-BEFORE-COMMIT - PURE - 3 branches] x")) == 1)
    chk("two numeric headers yield two run segments",
        len([s for s in segment_runs(
            "[FRAME-BEFORE-COMMIT - PURE - 3 branches] a "
            "[FRAME-BEFORE-COMMIT - DIRECTED - 4 branches] b")
            if SR.RUN_HEADER_NUMERIC.search(s)]) == 2)

    # ---- END-TO-END, on the two runs whose ground truth is documented in the wiki. ----
    b5 = REPO / "wiki/intake-triage/B-5-cfl-personal-protocol-2026-08-06.md"
    if b5.is_file():
        rows = analyse("wiki/intake-triage/B-5-cfl-personal-protocol-2026-08-06.md",
                       b5.read_text(encoding="utf-8", errors="replace"), "2026-08-06", "deposit")
        chk("B-5 is detected as a run", len(rows) >= 1)
        chk("B-5 is SEALED (wiki records: instinct written to a file before branching)",
            bool(rows) and rows[0]["seal"] != SEAL_NONE)
        chk("B-5's verdict grades MOVED (wiki records: 3 of 4 commitments overturned)",
            bool(rows) and rows[0]["verdict"] == V_MOVED)
    else:
        chk("B-5 deposit present for end-to-end control", False)

    # THE DEFLATOR MUST FIRE ON THIS FILE'S OWN SUBJECT MATTER.
    # This control was written on 2026-08-06 asserting the near-miss as a FACT — "upstream does
    # NOT catch B-8" — precisely so that an upstream repair could not make it vacuous without
    # anyone noticing. The repair landed 2026-08-07 and this test failed, which is the control
    # working. Flipped, with the reason kept, because an assertion whose sign is edited without a
    # record is how a test stops meaning anything.
    chk("UPSTREAM skill_record.SELF_AUDIT NOW catches B-8 (repaired 2026-08-07; this control was "
        "written inverted on purpose and failing was its job)",
        bool(SR.SELF_AUDIT.search("wiki/intake-triage/B-8-improving-fbc-and-gbs-2026-08-06.md")))
    chk("B-8 (a record ABOUT FBC that quotes runs) IS deflated by this file",
        is_self_audit("wiki/intake-triage/B-8-improving-fbc-and-gbs-2026-08-06.md"))
    chk("the published FBC record page is deflated (it quotes runs; it is not one)",
        is_self_audit("wiki/references/skills/frame-before-commit.md"))
    chk("B-5 (a genuine run) is NOT deflated",
        not is_self_audit("wiki/intake-triage/B-5-cfl-personal-protocol-2026-08-06.md"))
    chk("the harness condition runs are NOT deflated — about FBC, but genuinely executed",
        not is_self_audit("research/01-FBC-Improvement/harness/condition-C-2026-05-21.md"))

    # ---- REUSE, not redefinition. A seventh scanner is the divergence defect. ----
    chk("run shape comes from skill_record.analyse_fbc, not a second definition",
        analyse.__globals__["SR"].analyse_fbc is SR.analyse_fbc)
    chk("the two path deflators are skill_record's", SR.REEMISSION and SR.SELF_AUDIT)
    chk("CORPUS resolves transitively to coverage_gap's",
        CI.CORPUS == __import__("coverage_gap").CORPUS)
    chk("turn splitter is gbs_record's, via skill_record",
        SR.spans is __import__("gbs_record").spans)

    # ---- raw/ UNTOUCHED. Jon's standing NO DESTRUCTIVE ACTS constraint, tested as a property. ----
    sample = [p for p, _ in CI.walk_corpus()][::97]
    before = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    collect(max_files=60)
    after = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    chk(f"a scan leaves raw/ byte- and mtime-identical ({len(sample)} sampled)", before == after)

    print("\nRESULT: " + ("PASS — controls fire in both directions." if ok
                          else "FAIL — do not trust its counts."))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help=f"regenerate {OUT.name}")
    ap.add_argument("--unknown", action="store_true", help="enumerate the UNKNOWN column")
    ap.add_argument("--max-files", type=int, default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    rows, n_corpus, n_dep, how, read, n_index = collect(max_files=args.max_files)
    if not n_corpus and not n_dep:
        print(f"[{read.status}] {read.one_line()}", file=sys.stderr)
        print("Runs = UNKNOWN, not zero. Rebuild: python scripts/audit/corpus_index.py",
              file=sys.stderr)
        return 0
    report(rows, n_corpus, n_dep, how, read, n_index, show_unknown=args.unknown)
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(render(rows, n_corpus, n_dep, how, read, n_index), encoding="utf-8")
        print(f"WROTE {OUT.relative_to(REPO).as_posix()}")
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
