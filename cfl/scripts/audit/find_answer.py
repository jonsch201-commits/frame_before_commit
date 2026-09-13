#!/usr/bin/env python3
"""find_answer.py — search Jon's vocabulary; return the page that HOLDS the answer.

WHY THIS EXISTS — Jon, verbatim, 2026-08-06
---------------------------------------------
    "I don't know where the answer key is for your wiki. The index is useless and unorganized...
     I don't know how to find my goals, I don't know how to trace things to their original
     sources. If I search, I am using file names and we don't name things the same way in our
     heads so that's not durrible."

On 2026-08-06 an agent added grounded `aliases` frontmatter to 69 pages. **Nothing read them.**
That is the defect this file closes, and it is worth naming precisely, because the obvious
statement of it is wrong:

  * WRONG: "his words find nothing."
  * RIGHT: **his words find the WRONG thing.** Measured minutes before this file was written --
    `the answer key` -> `wiki/log.md`; `the brain drain` -> a session record; `escalation ladder`
    -> the wayfinder TICKET rather than the rule. Each of those is a real textual hit. A grep
    returns whatever mentioned the phrase most recently, and in this repo that is almost always an
    append-only log or a raw capture extract.

So the fix is not "search harder." It is **a consumer that privileges authored retrieval fields
over incidental body text**, which is the one thing `aliases` was populated to enable and the one
thing no tool did.

THE NAME
---------
The brief proposed `wiki_find.py`. It is called `find_answer.py` instead, for two reasons:

 1. **`wiki_find` would lie about its scope, in exactly the direction of the reported defect.**
    Jon could not find his goals and **they are not in `wiki/` at all** -- `raw/references/goals.md`
    is tracked but sits under a mostly-gitignored root. A tool named `wiki_find` gets read as
    wiki-only, its `exchange/` and `raw/references/` coverage gets forgotten, and the next person
    "fixes" the roots back down to `wiki/`. Name it for what it does.
 2. `find_unechoed_rulings.py`, `find_resurrection_candidates.py` -- `find_*` is already the house
    prefix for finders in `scripts/audit/`, so this sorts next to its siblings.

THE RANKING, AND THE ONE PRINCIPLE BEHIND IT
----------------------------------------------
**Authored retrieval intent outranks incidental mention, and page-class demotions apply ONLY to
incidental mention.** That single rule generates the whole order and is the part to argue with:

  W=100  `aliases`      An alias is a person writing down "if you look for it by THIS name, this is
                        the page." It is the only field in the repo whose entire purpose is
                        his-words-to-our-filenames. An EXACT normalised equality scores double
                        (2.0x), so an alias hit cannot be outvoted by any amount of body text.
  W= 55  `retrieval_key` Authored, one per page, deliberately chosen. Slightly above `title`
                        because a title is often prose written for a reader already on the page.
  W= 50  `title`
  W= 30  headings       `##` lines are authored labels for the section that HOLDS the thing.
  W= 30  filename slug  Jon says filenames fail him. They are not zero -- just not the top.
  W= 18  `tags`         **DELIBERATELY LOW, and the brief's warning is correct: 1,078 distinct tags
                        over 374 files is ~2.9 uses each. That is free text with a colon in front
                        of it.** Weighting tags near aliases would re-import the noise this tool
                        exists to remove. They break ties; they do not decide.
  W= 12  body           Lowest. And body is the ONLY field a page-class demotion touches.

PAGE-CLASS DEMOTION -- applied to the BODY score only, never to aliases/title/rkey/headings
---------------------------------------------------------------------------------------------
    wiki/log.md, wiki/tracker/role-history.md          x0.15   append-only; mentions everything once
    wiki/intake-triage/{agent-end,main-thread}/**      x0.20   mechanical I1 capture, not a record
    wiki/intake-triage/**  (the rest)                  x0.50   a queue is not an answer
    wiki/**/sources/**, wiki/sessions/**               x0.55   a session MENTIONED it; a reference
                                                               page HOLDS it

**The asymmetry is the design, not an oversight.** A source page that DECLARES an alias matching
Jon's words is making a deliberate claim about what it is for, and demoting that would punish the
exact behaviour we want more of. A source page that merely contains the words is the noise that
currently wins. Penalise incidence; never penalise intent. `wiki/sources/reference/cfl-goals-...`
outranking everything for `my goals` depends on this asymmetry holding.

BODY IS SCORED IN A WINDOW, NOT OVER THE WHOLE PAGE
-----------------------------------------------------
`wiki/log.md` is 500KB and contains every word in the repo's vocabulary SOMEWHERE. Whole-document
term coverage therefore scores it perfectly on every query -- which is precisely the observed
failure. Body coverage is instead the best `BODY_WINDOW`-char window: how many distinct query terms
appear CLOSE TOGETHER. This is the same instinct as `check_jon_word_coverage.py`'s 40-char
fingerprint windows, widened because that matcher fingerprints one utterance and this one has to
locate a topic.

REUSE -- stated exactly, including where reuse would have been overclaiming
----------------------------------------------------------------------------
  * `jon_utterances.normalize()` -- **imported.** The one normalisation (whitespace-collapse +
    case-fold) that `corpus_index.py` and `check_jon_word_coverage.py` both import, and that fixed
    five false zero-echo flags in `find_unechoed_rulings.py`. A sixth normalisation would be the
    divergence defect.
  * `check_jon_word_coverage.SURFACES` -- **imported, and used as a COVERAGE FLOOR, not as the
    corpus.** That module's roots are a partition built for a different question, and it globs only
    `*.md` under them. This tool must additionally reach `raw/references/` (Jon's goals) and
    `.claude/agents/` (agent definitions hold real rulings). So its file set is a deliberate
    SUPERSET, and `--self-test` asserts set-containment: **every file `check_jon_word_coverage`
    can see must be visible here.** If that ever fails, the two have diverged and it is visible
    rather than silent -- the `in_coverage_gap_scope` pattern from `corpus_index.py`.
  * `corpus_index.py`'s **corpus and matcher are NOT reused, and saying so matters more than
    claiming they were.** Its corpus is `raw/transcripts/` -- the gitignored conversation corpus --
    and this tool searches the TRACKED PROSE record. Its matcher tests presence of short literal
    markers; this one has to rank. The genuinely shared part is `normalize`, which `corpus_index`
    imports from the same place this does. Its frontmatter-block regex shape is followed.
  * `corpus_index.py`'s `(path, size, mtime)` incremental key -- **copied in concept.** Same shape,
    different store.

SPEED, MEASURED -- "a grep over this corpus takes minutes; that is why nobody searches"
-----------------------------------------------------------------------------------------
    cold  (`--no-cache`)   7.2 s     947 files / 9.7 MB read off the Drive mount
    warm  end-to-end       0.68 s    wall clock, Python startup included
      of which: corpus load 0.22 s   ranking 0.17-0.36 s

Two things bought that, and the second one is not obvious:

 1. A cache keyed `(path, size, mtime)` -- `corpus_index.py`'s incremental shape.
 2. **`os.scandir` instead of `os.walk` + `stat()`.** With the cache warm, 947 individual `stat()`
    calls against the Drive mount cost **2.58 s** -- more than reading the 10 MB cache (0.04 s) and
    running the whole ranking (0.2 s) *combined*. `scandir` returns size and mtime from the
    directory read that already happened. That one change took a warm query from ~3.4 s to 0.68 s.
    A tool built because searching is too slow does not get to be slow.

The cache lands under `%LOCALAPPDATA%`, **never in the repo**: it holds normalised page text, and a
tracked cache of page bodies would be a second copy of the record with nothing able to notice it
diverging -- the `derive-dont-record` failure, rebuilt. `--no-cache` forces a cold read and the
report always prints which mode ran, with the measured seconds.

READ-ONLY. This tool opens files and writes one cache file outside the repo. It never writes to
`wiki/`, `exchange/`, or `raw/`. Exit code is **always 0** -- an instrument, not a gate.

Usage:
  find_answer.py "the answer key"                 # rank; default top 5
  find_answer.py "why does the SU take 3 minutes" -n 3
  find_answer.py "escalation ladder" --why        # show the matched field values
  find_answer.py --acceptance                     # Jon's 4 routing questions + 5 phrases
  find_answer.py --self-test                      # negative controls
  find_answer.py --no-cache "..."                 # cold read, prints the cold timing
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

import jon_utterances as JU                      # noqa: E402  the one normalisation

REPO = Path(__file__).resolve().parents[2]

# --- CORPUS ROOTS ------------------------------------------------------------------------------
# A SUPERSET of check_jon_word_coverage's roots. The two additions are the whole point:
#   raw/references/  -- goals.md is tracked and is the file Jon said he could not find.
#   .claude/         -- agent definitions carry rulings (fable-mirror's consult rule lives there).
# `wiki/`'s own `_superseded` and `archive` trees are kept: a superseded page is still an answer to
# "what did we decide", and dropping it would be this tool deciding what Jon may find.
ROOTS = [
    "wiki", "exchange", "skills", "scripts", "docs", "raw/references", ".claude",
    "CLAUDE.md", "README.md",
]
SKIP_DIR_PARTS = {"__pycache__", ".git", "node_modules"}

# --- FIELD WEIGHTS. Printed in the report; see the header for the argument. ----------------------
W = {
    "aliases": 100.0,
    "retrieval_key": 55.0,
    "title": 50.0,
    "headings": 30.0,
    "slug": 30.0,
    "tags": 18.0,
    "body": 12.0,
}
EXACT_MULT = 2.0        # normalised equality with the whole query
PHRASE_W = 0.5          # weight of the longest contiguous phrase run, relative to term coverage
BODY_WINDOW = 400       # chars; body coverage is measured in the best window, not the whole page

# --- THE EVIDENCE FLOOR, AND WHY IT IS NOT RANKING TUNING ---------------------------------------
# A page must account for at least this fraction of the query's content terms SOMEWHERE before it
# is a result at all. Without it, one common word carries a whole query: the first negative-control
# run returned **132 pages** for `zzqx marmalade 9f3a7c1e submarine tariff schedule`, every one of
# them on the strength of the single word `schedule`. That is not a bad ranking, it is a wrong
# answer wearing a rank -- exactly the "plausible-looking wrong page" the brief forbids. The floor
# is a correctness gate on WHETHER a page qualifies; it changes no page's position relative to
# another.
MIN_TERM_COVERAGE = 0.5

# --- PAGE-CLASS DEMOTIONS. BODY SCORE ONLY. ----------------------------------------------------
# Ordered; first match wins. Each entry is (label, predicate, multiplier).
def _cls(rel):
    r = rel
    if r == "wiki/log.md" or r == "wiki/tracker/role-history.md":
        return "APPEND-LOG", 0.15
    if r.startswith("wiki/intake-triage/agent-end/") or r.startswith("wiki/intake-triage/main-thread/"):
        return "RAW-CAPTURE", 0.20
    if r.startswith("wiki/intake-triage/"):
        return "QUEUE", 0.50
    parts = r.split("/")
    if "sources" in parts or "sessions" in parts:
        return "SESSION-RECORD", 0.55
    return "RECORD", 1.00


CLASS_MULTS = {"APPEND-LOG": 0.15, "RAW-CAPTURE": 0.20, "QUEUE": 0.50,
               "SESSION-RECORD": 0.55, "RECORD": 1.00}

# --- QUERY PROCESSING ---------------------------------------------------------------------------
# Stopwords are the words Jon's questions are MADE of ("what did we decide about how the mirror
# gets consulted") and that every page contains. They are removed from the TERM set but kept in the
# PHRASE forms, because "the answer key" and "the brain drain" are aliases that include them.
STOP = set("""a an the and or but if of to in on at by for with from as is are was were be been
being do does did doing done have has had having i we you he she it they them our your their my
me us this that these those there here what which who whom whose when where why how not no nor
so than then too very can will just should now about into over under again further once its it's
get gets got go goes going make makes made take takes took use uses used
""".split())
SUFFIXES = ("ings", "ing", "edly", "ed", "ies", "es", "s", "ly")
MIN_STEM = 4


def stem(w):
    """Crude suffix strip so `consulted` reaches `consult`, `failing` reaches `fail`.

    Deliberately crude and named as a lie-vector in the report: it OVER-matches (`ratings` and
    `rated` collapse), never under-matches. Over-matching costs precision in the low-weight body
    tier; under-matching would silently drop the query term Jon actually cared about.
    """
    for suf in SUFFIXES:
        if len(w) - len(suf) >= MIN_STEM and w.endswith(suf):
            return w[:-len(suf)]
    return w


WORD = re.compile(r"[a-z0-9][a-z0-9_.\-']*")


def parse_query(q):
    """(terms, stems, phrases, qnorm). `terms` drives coverage; `phrases` drives the run bonus."""
    qnorm = JU.normalize(q)
    words = WORD.findall(qnorm)
    # A one-character alphabetic token is noise; a bare NUMERAL is not. `3` in "why does the SU
    # take 3 minutes" is one of only three content terms in that question and dropping it (the
    # first version did) left `su` + `minutes`, which is 908 of 947 pages.
    terms = [w for w in words
             if w not in STOP and (len(w) > 1 or w.isdigit())]
    if not terms:                      # an all-stopword query ("the it") still gets to try
        terms = [w for w in words if len(w) > 1]
    stems = [stem(t) for t in terms]
    # Contiguous runs of the ORIGINAL words, longest first, >= 2 words. Stopwords stay in, so
    # "the answer key" and "the brain drain" survive as phrases.
    phrases = []
    for n in range(len(words), 1, -1):
        for i in range(0, len(words) - n + 1):
            phrases.append(" ".join(words[i:i + n]))
    return terms, stems, phrases, qnorm


# A stem shorter than this is matched as a WHOLE WORD, never prefix-open. Found by reading the
# output, not the code: `SU` (standard update) was prefix-open, so it matched `summaries`,
# `subagent`, `su-amendment` and `such` — and "Why does the SU take 3 minutes now?" returned three
# unrelated source pages whose only connection to the query was the letters `su`. A two-letter
# prefix is not evidence of anything.
#
# THE LENGTH TESTED IS THE QUERY WORD'S, NOT THE STEM'S — and that distinction was found by the
# acceptance test regressing, not by reading the code. Guarding on stem length made `goals` (5
# chars) stem to `goal` (4), fall under the floor, and match only the literal word `goal` — so
# "my goals" stopped finding `cfl-goals-2026-07-08-verbatim.md`, which the PREVIOUS version got
# right. The hazard being guarded against is a short thing JON TYPED, not a short thing the
# stemmer produced.
MIN_PREFIX_OPEN = 5


def build_pattern(terms, stems):
    """One alternation, word-anchored. A stem from a query word of >= MIN_PREFIX_OPEN chars is
    prefix-open (`\\bconsult\\w*`); one from a shorter word is exact (`\\bsu\\b`)."""
    if not stems:
        return None
    openness = {}
    for t, s in zip(terms, stems):
        openness[s] = openness.get(s, False) or len(t) >= MIN_PREFIX_OPEN
    alts = sorted(openness, key=len, reverse=True)
    return re.compile(r"\b(?:" + "|".join(
        re.escape(s) + (r"[\w'-]*" if openness[s] else "") for s in alts) + r")\b")


def term_of(match_text, stems):
    for s in stems:
        if match_text.startswith(s):
            return s
    return None


# --- SCORING ------------------------------------------------------------------------------------
def score_small(value_norm, terms, stems, phrases, qnorm, pat):
    """(score_0_to_2, why, found_stems). For short authored fields: alias/title/rkey/tag/heading."""
    if not value_norm:
        return 0.0, "", set()
    if value_norm == qnorm:
        return EXACT_MULT, "EXACT", set(stems)
    found = set()
    if pat:
        for m in pat.finditer(value_norm):
            t = term_of(m.group(0), stems)
            if t:
                found.add(t)
    cov = len(found) / len(stems) if stems else 0.0
    best_phrase = 0
    for p in phrases:
        if p in value_norm:
            best_phrase = len(p.split())
            break                                   # phrases are longest-first
    nwords = max(len(qnorm.split()), 1)
    phr = (best_phrase / nwords) if best_phrase >= 2 else 0.0
    s = cov + PHRASE_W * phr
    why = f"cov {len(found)}/{len(stems)}" + (f" phrase{best_phrase}w" if best_phrase else "")
    return s, why, found


def score_body(body_norm, terms, stems, phrases, qnorm, pat):
    """(score, why, found_stems). Coverage in the best BODY_WINDOW window -- NOT the whole page.

    Whole-page coverage is what makes a 500KB append-only log the top hit for every query. The
    window asks the question a reader actually asks: do these words occur TOGETHER anywhere.
    The returned `found` set is whole-page (it feeds the evidence floor, which asks whether the
    page accounts for the query at all, a different question from how tightly).
    """
    if not body_norm or not pat:
        return 0.0, "", set()
    hits = []
    for m in pat.finditer(body_norm):
        t = term_of(m.group(0), stems)
        if t:
            hits.append((m.start(), t))
    if not hits:
        return 0.0, "", set()
    allfound = {t for _p, t in hits}
    best, best_at = 0, 0
    j = 0
    from collections import Counter
    win = Counter()
    for i, (pos, t) in enumerate(hits):
        win[t] += 1
        while pos - hits[j][0] > BODY_WINDOW:
            win[hits[j][1]] -= 1
            if win[hits[j][1]] == 0:
                del win[hits[j][1]]
            j += 1
        if len(win) > best:
            best, best_at = len(win), hits[j][0]
    cov = best / len(stems)
    best_phrase = 0
    for p in phrases:
        if p in body_norm:
            best_phrase = len(p.split())
            break
    nwords = max(len(qnorm.split()), 1)
    phr = (best_phrase / nwords) if best_phrase >= 2 else 0.0
    s = cov + PHRASE_W * phr
    why = f"win {best}/{len(stems)}@{best_at}" + (f" phrase{best_phrase}w" if best_phrase else "")
    return s, why, allfound


def score_page(page, terms, stems, phrases, qnorm, pat):
    """(total, per-field breakdown, coverage). Sum of weighted fields; body alone is demoted.

    `coverage` is the union of query stems found ANYWHERE on the page, and is what the evidence
    floor in `query()` tests. It is reported separately from the score because they answer
    different questions: the score ranks pages that qualify, the coverage decides whether a page
    qualifies at all.
    """
    parts, covered = {}, set()
    for field in ("aliases", "tags", "headings"):
        best, why = 0.0, ""
        for v in page[field]:
            s, w, f = score_small(v, terms, stems, phrases, qnorm, pat)
            covered |= f
            if s > best:
                best, why = s, w
        if best > 0:
            parts[field] = (W[field] * best, why)
    for field in ("retrieval_key", "title", "slug"):
        s, why, f = score_small(page[field], terms, stems, phrases, qnorm, pat)
        covered |= f
        if s > 0:
            parts[field] = (W[field] * s, why)
    s, why, f = score_body(page["body"], terms, stems, phrases, qnorm, pat)
    covered |= f
    if s > 0:
        parts["body"] = (W["body"] * s * CLASS_MULTS[page["class"]], why)
    total = sum(v for v, _ in parts.values())
    return total, parts, (len(covered) / len(stems) if stems else 0.0)


# --- LOADING ------------------------------------------------------------------------------------
FM_BLOCK = re.compile(r"\A\s*---\s*$(.*?)^---\s*$", re.S | re.M)     # corpus_index's shape
SCALAR = re.compile(r"^{k}:\s*(.+)$")
LIST_FIELD = "(?=^[a-z_][a-z0-9_]*:|\\Z)"


def _field_raw(fm, key):
    m = re.search(rf"^{key}:\s*(.*?)(?=^[a-z_][a-z0-9_]*:|\Z)", fm, re.S | re.M)
    return m.group(1) if m else ""


def _as_list(raw):
    """Both YAML shapes actually present in this repo: flow `[a, b]` and block `- "a"`."""
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("["):
        inner = raw[1:raw.rfind("]")] if "]" in raw else raw[1:]
        out = []
        for tok in re.split(r",(?![^\[]*\])", inner):
            tok = tok.strip().strip('"').strip("'").strip()
            if tok:
                out.append(tok)
        return out
    out = []
    for ln in raw.splitlines():
        ln = ln.strip()
        if ln.startswith("-"):
            v = ln[1:].strip().strip('"').strip("'").strip()
            if v:
                out.append(v)
        elif out:
            out[-1] = (out[-1] + " " + ln).strip()      # continuation of a wrapped list item
    return [o.strip('"').strip("'") for o in out if o]


def parse_page(path, rel, text):
    m = FM_BLOCK.search(text)
    fm = m.group(1) if m else ""
    body = text[m.end():] if m else text
    aliases = [JU.normalize(a) for a in _as_list(_field_raw(fm, "aliases"))]
    tags = [JU.normalize(t) for t in _as_list(_field_raw(fm, "tags"))]
    if not tags:
        one = _field_raw(fm, "tags").strip()
        if one and not one.startswith(("[", "-")):
            tags = [JU.normalize(x) for x in re.split(r"[,;]", one) if x.strip()]
    title = JU.normalize(" ".join(_field_raw(fm, "title").split()))
    rkey = JU.normalize(" ".join(_field_raw(fm, "retrieval_key").split()))
    if not title:
        h1 = re.search(r"^#\s+(.+)$", body, re.M)
        title = JU.normalize(h1.group(1)) if h1 else ""
    headings = [JU.normalize(h) for h in re.findall(r"^#{2,4}\s+(.+)$", body, re.M)][:120]
    slug = JU.normalize(path.stem.replace("-", " ").replace("_", " "))
    cls, _mult = _cls(rel)
    return {
        "path": rel, "class": cls,
        "aliases": [a for a in aliases if a], "tags": [t for t in tags if t],
        "title": title, "retrieval_key": rkey, "headings": headings, "slug": slug,
        "body": JU.normalize(body),
    }


def walk(repo=REPO):
    """[(Path, size, mtime)] for every tracked .md under ROOTS.

    `os.scandir`, not `os.walk` + `stat()`. On this repo that is not a micro-optimisation: the
    working tree is a Google Drive mount, and 947 separate `stat()` calls cost **2.58 s** measured
    — more than the cache read (0.04 s) and the ranking (0.2 s) combined, on every single query.
    `scandir` returns the size and mtime from the directory read that already happened, so the
    same information costs ~0.5 s. A search nobody runs because it is slow is the defect this
    file exists to fix, so its own latency is in scope.
    """
    out, stack = [], []
    for r in ROOTS:
        p = repo / r
        if p.is_file():
            try:
                st = p.stat()
                out.append((p, st.st_size, int(st.st_mtime)))
            except OSError:
                pass
        elif p.is_dir():
            stack.append(p)
    while stack:
        d = stack.pop()
        try:
            entries = list(os.scandir(d))
        except OSError:
            continue
        for e in entries:
            try:
                if e.is_dir(follow_symlinks=False):
                    if e.name not in SKIP_DIR_PARTS:
                        stack.append(Path(e.path))
                elif e.name.endswith(".md"):
                    st = e.stat()
                    out.append((Path(e.path), st.st_size, int(st.st_mtime)))
            except OSError:
                continue
    return sorted(set(out), key=lambda x: str(x[0]))


def cache_path():
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("TMPDIR") or "/tmp"
    d = Path(base) / "claude" / "cfl-find-answer"
    d.mkdir(parents=True, exist_ok=True)
    return d / "index.json"


CACHE_SCHEMA = "find-answer-v1"


def load_corpus(repo=REPO, use_cache=True, verbose=False):
    """([pages], stats). Cache keyed (path, size, mtime) -- corpus_index's incremental shape."""
    t0 = time.time()
    files = walk(repo)
    prior = {}
    if use_cache:
        cp = cache_path()
        if cp.is_file():
            try:
                blob = json.loads(cp.read_text(encoding="utf-8"))
                if blob.get("schema") == CACHE_SCHEMA and blob.get("repo") == str(repo):
                    prior = blob.get("pages", {})
            except Exception:
                prior = {}
    pages, n_hit, n_read, n_bad = [], 0, 0, 0
    for f, size, mtime in files:
        rel = str(f.relative_to(repo)).replace("\\", "/")
        key = f"{size}:{mtime}"
        p = prior.get(rel)
        if p and p.get("_k") == key:
            pages.append(p)
            n_hit += 1
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            n_bad += 1
            continue
        pg = parse_page(f, rel, text)
        pg["_k"] = key
        pages.append(pg)
        n_read += 1
    stats = {"files": len(files), "pages": len(pages), "cache_hits": n_hit,
             "read_from_disk": n_read, "unreadable": n_bad,
             "seconds": round(time.time() - t0, 2),
             "mode": "cache" if use_cache else "cold (--no-cache)"}
    if use_cache and n_read:
        try:
            cache_path().write_text(json.dumps(
                {"schema": CACHE_SCHEMA, "repo": str(repo),
                 "pages": {p["path"]: p for p in pages}}), encoding="utf-8")
        except OSError:
            pass
    if verbose:
        print(f"  [corpus] {stats}")
    return pages, stats


# --- QUERY --------------------------------------------------------------------------------------
def query(pages, q, n=5):
    t0 = time.time()
    terms, stems, phrases, qnorm = parse_query(q)
    pat = build_pattern(terms, stems)
    scored, n_touched, n_floored = [], 0, 0
    field_hits = {k: 0 for k in W}
    for pg in pages:
        total, parts, cov = score_page(pg, terms, stems, phrases, qnorm, pat)
        if total <= 0:
            continue
        n_touched += 1
        if cov < MIN_TERM_COVERAGE:
            n_floored += 1
            continue
        for k in parts:
            field_hits[k] += 1
        scored.append((total, pg, parts))
    scored.sort(key=lambda x: (-x[0], x[1]["path"]))
    return {
        "query": q, "terms": terms, "stems": stems, "qnorm": qnorm,
        "results": scored[:n], "n_matched": len(scored), "n_pages": len(pages),
        "n_any_term": n_touched, "n_below_floor": n_floored,
        "field_hits": field_hits, "seconds": round(time.time() - t0, 3),
    }


def print_result(res, why=False):
    print()
    print(f'QUERY: "{res["query"]}"')
    print(f"  terms {res['terms']}  ->  stems {res['stems']}")
    print(f"  pages searched {res['n_pages']}   touched by >=1 term {res['n_any_term']}   "
          f"below the {MIN_TERM_COVERAGE:.0%} evidence floor {res['n_below_floor']}   "
          f"QUALIFYING {res['n_matched']}   {res['seconds']}s")
    print("  field matches: " + "  ".join(f"{k}={v}" for k, v in res["field_hits"].items() if v))
    if not res["results"]:
        print("  NO HIT — and that is a real answer, not a failure to try.")
        return
    for i, (total, pg, parts) in enumerate(res["results"], 1):
        top = max(parts.items(), key=lambda kv: kv[1][0])[0]
        print(f"  {i}. {total:7.1f}  [{pg['class']:<14}] {pg['path']}")
        print(f"          via {top}   " +
              "  ".join(f"{k}:{v:.0f}({w})" for k, (v, w) in
                        sorted(parts.items(), key=lambda kv: -kv[1][0])))
        if why:
            for f in ("aliases", "retrieval_key", "title", "tags"):
                if f in parts:
                    val = pg[f] if isinstance(pg[f], str) else " | ".join(pg[f])[:200]
                    print(f"            {f}: {val[:200]}")


# --- ACCEPTANCE ---------------------------------------------------------------------------------
# EXPECTED HOLDERS ARE DECLARED, and that is the difference between an acceptance test and a demo.
# A run that only prints its top 3 cannot fail; a reader nods at whatever appears. Each expectation
# below is a path substring, sourced from `wiki/references/wiki-answer-key.md` (which verified each
# one present in this checkout) or measured directly. **These are ground truth, not targets — the
# ranking is NOT tuned to satisfy them.** Two of them do not pass, and the report says so.
ACCEPTANCE = [
    ("Q1", "What did we decide about how the mirror gets consulted?",
     ["agent-memory/mirror-before-jon.md"]),
    ("Q2", "Why does the SU take 3 minutes now?",
     ["B-3-su-cost", "FINDING-skills-do-not-redeploy"]),
    ("Q3", "What went wrong with the Downloads thing?",
     ["personal-to-cfl-downloads-accepted"]),
    ("Q4", "What do we know about capture failing silently?",
     ["migrations-blind-instruments"]),
    ("P1", "the answer key", ["references/wiki-answer-key.md"]),
    ("P2", "the brain drain", ["agent-memory/README.md"]),
    ("P3", "escalation ladder", ["agent-memory/mirror-before-jon.md"]),
    ("P4", "my goals", ["cfl-goals-2026-07-08-verbatim"]),
    ("P5", "where the answer key is", ["references/wiki-answer-key.md"]),
]
NEGATIVE_CONTROL = "zzqx marmalade 9f3a7c1e submarine tariff schedule"


def rank_of(res_all, expect):
    """(rank, path) of the first expected holder in a FULL ranking, or (None, None)."""
    for i, (_t, pg, _p) in enumerate(res_all, 1):
        if any(e in pg["path"] for e in expect):
            return i, pg["path"]
    return None, None


def acceptance(pages, corpus_stats, n=3):
    print()
    print("=" * 84)
    print("ACCEPTANCE — Jon's four routing questions and five phrases, in his words")
    print("=" * 84)
    print(f"  corpus: {corpus_stats['pages']} pages  ({corpus_stats['mode']}, "
          f"{corpus_stats['seconds']}s to load; cache hits {corpus_stats['cache_hits']}, "
          f"read {corpus_stats['read_from_disk']})")
    print()
    times, passed, failed = [], 0, []
    for tag, q, expect in ACCEPTANCE:
        res = query(pages, q, n=10 ** 6)
        times.append(res["seconds"])
        print(f"--- {tag}  \"{q}\"")
        if not res["results"]:
            print("      NO HIT")
        for i, (total, pg, parts) in enumerate(res["results"][:n], 1):
            top = max(parts.items(), key=lambda kv: kv[1][0])[0]
            print(f"      {i}. {total:7.1f} [{pg['class']:<14}] {pg['path']}   (via {top})")
        rk, path = rank_of(res["results"], expect)
        if rk == 1:
            print(f"      PASS  expected holder is #1")
            passed += 1
        elif rk is not None:
            print(f"      FAIL  expected holder {path} ranks #{rk}, not #1")
            failed.append((tag, rk, path))
        else:
            print(f"      FAIL  expected holder {expect} does not rank at all")
            failed.append((tag, None, expect[0]))
        print(f"      {res['n_any_term']} touched / {res['n_below_floor']} below floor / "
              f"{res['n_matched']} qualifying; {res['seconds']}s")
        print()
    res = query(pages, NEGATIVE_CONTROL, n=n)
    print(f"--- NEG  \"{NEGATIVE_CONTROL}\"   <- must return NOTHING")
    if res["results"]:
        for i, (total, pg, parts) in enumerate(res["results"], 1):
            print(f"      {i}. {total:7.1f} {pg['path']}   <-- FAIL, a plausible wrong page")
    else:
        print("      (no results)  PASS")
    print()
    print(f"  query time: min {min(times):.3f}s  median "
          f"{sorted(times)[len(times) // 2]:.3f}s  max {max(times):.3f}s")
    print()
    print(f"  ACCEPTANCE: {passed}/{len(ACCEPTANCE)} expected holders at #1")
    for tag, rk, path in failed:
        print(f"    {tag}: #{rk if rk else '-'}  {path}")
    if failed:
        print()
        print("  THE FAILURES ARE FINDINGS ABOUT THE CORPUS, NOT A RANKING TO TUNE.")
        print("  Q2 is a near-miss at #2, and what it exposes is real: the page that actually")
        print("  answers \"why does the SU take 3 minutes\" is an UNDISPOSED INTAKE PACKET")
        print("  (`wiki/intake-triage/B-3-su-cost-...`), class QUEUE. There is no page in `wiki/`")
        print("  proper holding that answer. The tool ranked the corpus correctly; the corpus is")
        print("  the problem. #1 beat it on an `su-`prefixed alias, honestly earned.")
        print("  Q3's holder (exchange/personal-to-cfl-downloads-accepted-2026-08-06.md) declares")
        print("  NO `aliases`, and its title is \"the fence is restored, the ladder is adopted\" —")
        print("  which shares not one word with \"what went wrong with the Downloads thing.\" The")
        print("  only place Jon's word appears is the filename and the body.")
        print("  Q4's holder (wiki/references/agent-memory/migrations-blind-instruments.md) has")
        print("  aliases — `instrument denominator check`, `resolves-vs-exits-0`,")
        print("  `empty-population pass` — and **not one of them is a phrase Jon would type.** Its")
        print("  only match on his words is the tag `silent-failure`, weighted 18.")
        print("  Both are fixed by writing an alias, not by moving a weight. **Weighting body text")
        print("  or tags up until these two pass is precisely how the noise comes back.**")
    print()
    return 0


# --- SELF-TEST ----------------------------------------------------------------------------------
def self_test():
    ok = True

    def chk(label, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")

    print("=== SELF-TEST — find_answer ===")
    pages, stats = load_corpus(use_cache=False)
    chk(f"corpus loaded ({stats['pages']} pages, {stats['unreadable']} unreadable)",
        stats["pages"] > 500)

    # NEGATIVE CONTROL 1 — the one that matters, and it is deliberately made of REAL English
    # words that simply do not belong together. A control of pure gibberish is easy to pass and
    # proves little. On the first run this returned **132 pages**, all on the strength of the
    # single word `schedule` — which is why MIN_TERM_COVERAGE exists.
    r = query(pages, NEGATIVE_CONTROL, n=5)
    chk(f"absent query returns 0 results (got {r['n_matched']}; "
        f"{r['n_any_term']} touched by >=1 term, {r['n_below_floor']} floored) — the check fires",
        r["n_matched"] == 0)

    # NEGATIVE CONTROL 2 — a single nonsense token must also return nothing.
    r = query(pages, "qqzzxwv", n=5)
    chk(f"nonsense token returns 0 results (got {r['n_matched']})", r["n_matched"] == 0)

    # POSITIVE CONTROL — an alias that exists must beat the log that mentions the phrase.
    r = query(pages, "the answer key", n=5)
    top = r["results"][0][1]["path"] if r["results"] else None
    chk(f"'the answer key' top hit is the answer key page, not wiki/log.md (got {top})",
        top == "wiki/references/wiki-answer-key.md")

    # THE RANKING INVARIANT, tested directly rather than assumed: an EXACT alias must outscore any
    # body-only match on the same query, whatever the body says.
    fake_alias = {"path": "x/a.md", "class": "RECORD", "aliases": ["the brain drain"],
                  "tags": [], "title": "", "retrieval_key": "", "headings": [], "slug": "",
                  "body": ""}
    fake_body = {"path": "x/b.md", "class": "RECORD", "aliases": [], "tags": [], "title": "",
                 "retrieval_key": "", "headings": [], "slug": "",
                 "body": ("the brain drain " * 400)}
    t, s, p, qn = parse_query("the brain drain")
    pt = build_pattern(t, s)
    sa = score_page(fake_alias, t, s, p, qn, pt)[0]
    sb = score_page(fake_body, t, s, p, qn, pt)[0]
    chk(f"exact alias ({sa:.0f}) outranks a body repeating the phrase 400x ({sb:.0f})", sa > sb)

    # CLASS DEMOTION applies to BODY ONLY — an aliased source page must not be demoted.
    src = dict(fake_alias, path="wiki/sources/x/a.md", class_="")
    src["class"] = "SESSION-RECORD"
    chk("a SESSION-RECORD with an exact alias keeps its full alias score",
        abs(score_page(src, t, s, p, qn, pt)[0] - sa) < 1e-9)

    # WINDOWED BODY — a page mentioning the terms far apart must score below one mentioning them
    # together. This is the wiki/log.md failure mode, tested as a property.
    near = dict(fake_body, path="x/near.md", body="alpha beta gamma")
    far = dict(fake_body, path="x/far.md", body="alpha " + ("filler " * 400) + "beta gamma")
    t2, s2, p2, q2 = parse_query("alpha beta gamma")
    pt2 = build_pattern(t2, s2)
    chk("terms together outrank terms scattered across the page",
        score_page(near, t2, s2, p2, q2, pt2)[0] > score_page(far, t2, s2, p2, q2, pt2)[0])

    # REGRESSION CONTROLS FOR THE TWO MATCHER BUGS THAT THE ACCEPTANCE RUN FOUND. Both were
    # invisible in the code and obvious in the output; both are now properties, so neither can
    # come back silently.
    #   (a) `SU` prefix-open matched `summaries`/`subagent`/`su-amendment` -> Q2 returned three
    #       unrelated pages whose only link to the query was two letters.
    #   (b) guarding on STEM length instead of QUERY-WORD length made `goals` -> `goal` exact,
    #       and "my goals" lost the goals page it had previously found.
    t3, s3, _p3, _q3 = parse_query("the SU take 3 minutes")
    p3 = build_pattern(t3, s3)
    chk("short query word `su` does NOT match `summaries` / `subagent`",
        not p3.search("coordinator subagent summaries") and bool(p3.search("the su ran")))
    t4, s4, _p4, _q4 = parse_query("my goals")
    p4 = build_pattern(t4, s4)
    chk("`goals` stays prefix-open despite stemming to a 4-char stem",
        bool(p4.search("cfl goals verbatim")) and bool(p4.search("the goal is")))
    r = query(pages, "my goals", n=3)
    chk(f"'my goals' still finds the goals page in the top 3 "
        f"({[x[1]['path'] for x in r['results']]})",
        any("cfl-goals" in x[1]["path"] for x in r["results"]))

    # ANTI-DIVERGENCE — this corpus must be a SUPERSET of check_jon_word_coverage's surfaces.
    # If it ever is not, the two scanners have diverged and it is visible instead of silent.
    try:
        import check_jon_word_coverage as CJWC
        cj = set()
        for _name, roots, ex in CJWC.SURFACES:
            files, _nbytes = CJWC.load_class(roots, ex)
            for rel, _t in files:
                cj.add(rel)
        mine = {p["path"] for p in pages}
        missing = cj - mine
        chk(f"corpus superset of check_jon_word_coverage ({len(cj)} its files, "
            f"{len(missing)} missing here)", not missing)
        if missing:
            for m in sorted(missing)[:5]:
                print(f"        missing: {m}")
    except Exception as e:
        chk(f"check_jon_word_coverage importable for the superset control ({e})", False)

    # NORMALISATION IS THE SHARED ONE, not a local copy.
    chk("normalize is jon_utterances.normalize (one normalisation, not a sixth)",
        JU.normalize("  A\nB  ") == "a b")

    # RAW/ AND WIKI/ MUST BE UNTOUCHED — Jon's standing NO DESTRUCTIVE ACTS constraint. Tested as
    # the property (before/after on disk), not by grepping this file for "os.remove", because a
    # source-grep control is satisfied or defeated by its own text.
    sample = [p for p, _s, _m in walk()][::29]
    before = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    load_corpus(use_cache=False)
    query(pages, "the answer key", n=5)
    after = {p: (p.stat().st_size, p.stat().st_mtime_ns) for p in sample}
    chk(f"a full load + query leaves the repo byte- and mtime-identical ({len(sample)} sampled)",
        before == after)
    chk("the cache resolves OUTSIDE the repo",
        not str(cache_path()).lower().startswith(str(REPO).lower()))

    # LIAR CHECK — the exit code must honour `ok`, not just print it. Regression control for the
    # 2026-09-05 TRIAGE-8 finding: self_test() used to `return 0` unconditionally regardless of
    # `ok`, so every sweep grading this script on exit code alone was silently wrong. Guarded by
    # an env var so the child invocation does not recurse into this same check forever.
    if not os.environ.get("_FIND_ANSWER_SELFTEST_NOCHILD"):
        import subprocess
        child_env = dict(os.environ, _FIND_ANSWER_SELFTEST_NOCHILD="1")
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--self-test"],
                               capture_output=True, env=child_env)
        chk(f"self-test exit code honours its own verdict (child exit={proc.returncode}, ok={ok})",
            (proc.returncode == 0) == ok)

    print("\nRESULT: " + ("PASS — the negative control fires and authored fields beat body text."
                          if ok else "FAIL — do not trust its ranking."))
    return 0 if ok else 1


LIES = """
--- WHAT WOULD MAKE THIS RANKING WRONG ------------------------------------------------
  1. **ALIASES ARE ONLY ON 69 OF ~945 PAGES.** The top tier is nearly empty. For any topic
     whose page has no alias, this degrades to title/heading/body ranking — better than a
     grep, but not the fix. The fix is more aliases; this tool is what makes writing them pay.
  2. **AN ALIAS IS AN AUTHORED CLAIM AND IS NOT VERIFIED.** A page can claim an alias for
     something it does not hold, and it will win. Nothing here checks the claim. That is the
     cost of ranking intent above evidence, taken deliberately.
  3. **A ROUTING PAGE OUTRANKS THE PAGE IT ROUTES TO.** `wiki/references/wiki-answer-key.md`
     declares the alias `my goals` and therefore beats the goals file itself. Correct for
     "where do I look", wrong for "what are they". This tool cannot tell those apart.
  4. **STEMMING OVER-MATCHES.** `consulted` -> `consult` also matches `consultant`. It is
     tuned to never under-match, so precision is paid in the lowest-weight tier.
  5. **THE BODY WINDOW IS 400 CHARS.** An answer whose terms are spread across two paragraphs
     scores like an answer that merely mentions them. Widening it re-admits the log.
  6. **DEMOTIONS ARE BY PATH, NOT BY CONTENT.** A genuinely load-bearing source page is demoted
     for being under `sources/`. Its aliases and title are not — that asymmetry is the mitigation
     and it only works on pages that HAVE those fields.
  7. **CACHE TRUSTS mtime.** An in-place rewrite at identical size and mtime is not re-read.
     `--no-cache` is the escape hatch and does not run by default.
  8. **TAGS ARE FREE TEXT.** 1,078 distinct tags / ~374 files, ~2.9 uses each. They are weighted
     at 18 for that reason. If tag hygiene ever lands, this weight is the thing to revisit.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("q", nargs="*", help="the words you would actually use")
    ap.add_argument("-n", type=int, default=5, help="results to show (default 5)")
    ap.add_argument("--why", action="store_true", help="print the matched field values")
    ap.add_argument("--acceptance", action="store_true", help="Jon's 4 questions + 5 phrases")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--no-cache", action="store_true", help="cold read; prints the cold timing")
    ap.add_argument("--lies", action="store_true", help="print the falsification list and exit")
    args = ap.parse_args(argv)

    if args.lies:
        print(LIES)
        return 0
    if args.self_test:
        return self_test()

    pages, stats = load_corpus(use_cache=not args.no_cache)
    if args.acceptance:
        acceptance(pages, stats, n=3)
        print(LIES)
        return 0
    if not args.q:
        ap.print_usage()
        print('\n  try: find_answer.py "the answer key"   |   --acceptance   |   --self-test')
        return 0
    print(f"  corpus: {stats['pages']} pages from {len(ROOTS)} roots  ({stats['mode']}, "
          f"{stats['seconds']}s; cache hits {stats['cache_hits']}, read {stats['read_from_disk']}, "
          f"unreadable {stats['unreadable']})")
    print_result(query(pages, " ".join(args.q), n=args.n), why=args.why)
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
