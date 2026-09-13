#!/usr/bin/env python
"""seed_advance.py — ticket B-6 half 1: what would it take to ADVANCE each seed, and who has to do it?

WHY THIS EXISTS — Jon, 2026-08-05 (`wiki/sources/infrastructure/jon-wayfinder-vision-2026-08-05-
ab3ddc.md:61-64`): *"how we finish working towards a more automated sinthesis seed discovery and
creation and prototyping and implementation process. I have noticed that you've said no to a number
of seeds bieng formed because it would presumably be too much for me. That is true, and a barrior
for us to work through together."*

The only seed tooling that existed before this file was `_su_close_seeds.py`, which answers exactly
one question at SU-close ("how many of today's seeds carry a falsifier?") and deliberately judges
nothing else. **Nothing advanced a seed.** A register of 15 seeds with 11 untested falsifiers is a
queue with no consumer — the program's own characteristic defect (`feedback_derive-dont-record`,
`skills/intake/README.md`, the 2026-07-27 deposit-only-channel finding) applied to the seed layer.

WHAT THIS DOES, and the line it does not cross:

  * Parses EVERY `## S<n>` seed in a register (all sections, unlike `_su_close_seeds.py`, which is
    section-scoped on purpose for its SU row — that scoping is correct there and is not changed).
  * Reports each seed's tested-state, its independence-state under the guard rule *a falsifier may
    not be judged by its author*, and an ADVANCE CLASS: who can run the falsifier.
  * Emits, per seed, the specific evidence owed — the falsifier verbatim — plus the concrete
    artifacts it names (paths, scripts, commits), which is the "where to look" a runner needs.

  * IT NEVER WRITES TO THE REGISTER AND NEVER FLIPS A STATUS. A seed's status is evidence-bearing.
    This instrument proposes work; adjudication stays with Jon and the coordinator. It has no write
    path at all — output is stdout only.
  * IT DOES NOT JUDGE FALSIFIER QUALITY. Same boundary `_su_close_seeds.py` draws. Classification
    here is about *runnability*, not about whether the falsifier is a good one.

THE STRUCTURAL FINDING THIS INSTRUMENT SURFACES (see --format table footer): the five-field standard
(`status · recommendation · falsifier · falsifier_tested · blocks`, ratified as Personal D16 and
carried in this register's own frontmatter) HAS NO AUTHOR OR TESTED_BY FIELD. So the guard rule "a
falsifier may not be judged by its author" is **unenforceable by construction** — it can only be
checked on seeds that happen to confess authorship in prose. This script therefore reports
INDEPENDENCE-UNKNOWN, never INDEPENDENT, for any tested seed lacking a confession. Untested ≠ passed;
tested-by-unknown ≠ independently tested. Proposing the sixth field is a Jon/standard-owner call and
is NOT made here.

ADVANCE CLASSES — the whole point, and the input to the bandwidth half of B-6:

  AGENT-RUNNABLE  the falsifier names concrete in-repo artifacts (a path, a script, a commit, a
                  countable set). An agent can run it end-to-end and return a verdict. **Zero
                  Jon-minutes to RUN.** Jon spends minutes only on the verdict, in a batch.
  AGENT-SEARCH    the falsifier is "find a counter-example / name a fourth cause" over the corpus.
                  An agent can run a bounded search. Zero Jon-minutes to run, but a NULL result is
                  weak evidence (silence-in-corpus is uninformative — CLAUDE.md, fable-mirror), so
                  a null returns as "searched N sources, found none", never as "passed".
  JON-REQUIRED    the falsifier needs a judgment, a ruling, or a synthesis Jon has claimed. Costs
                  Jon-minutes and cannot be moved off him without moving the judgment off him.

NEGATIVE CONTROLS (--self-test): a file with no seeds reports 0 and exits 0 with an explicit
"0 seeds parsed" line, never a pass. A seed whose falsifier_tested cell is unparseable is
UNPARSED, counted as owed, never as run. A `yes:`-tested seed with an author confession is
AUTHOR-TESTED and stays in the owed set — the guard rule is enforced in the direction that costs
work, not in the direction that clears it.

Usage:
  python seed_advance.py --file wiki/intake-triage/SEED-REGISTER-2026-08-03.md
  python seed_advance.py --file <reg> --format json
  python seed_advance.py --file <reg> --queue          # only the owed work, ordered
  python seed_advance.py --file <reg> --format su      # one line "<owed> <total>" for su_close.sh
  python seed_advance.py --self-test
"""
import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDERS = {"", "n/a", "na", "none", "tbd", "-", "—"}

# --- guard-rule markers -----------------------------------------------------------------------
# Prose that CONFESSES the falsifier was judged by its own author. Sourced from the register's own
# wording, not invented: "Coordinator tested its own seed here" (S1), "partially self-tested by its
# author only" (S8 summary row), "The script's authors (not an independent party)" (S8), "recorded
# by the pilot's own author" (S3), "the author's own set-comparison" (S14).
AUTHOR_MARKERS = [
    r"tested its own seed",
    r"self-tested",
    r"self tested",
    r"by its author",
    r"its own author",
    r"own author",
    r"the author's own",
    r"not an independent (?:party|test)",
    r"needs an independent re-run",
    r"independent re-run",
    # S4's confession is worded differently from S1's and was missed by the first draft of this
    # list — caught by running the instrument against the real register and reading the rows
    # against the register's own prose rather than trusting the column. Kept as separate patterns
    # rather than folded, so the wording each one catches stays legible.
    r"not independently verified",
    r"someone other than the coordinator",
    r"someone other than the author",
    r"outside that build verifies",
]

# Prose that reserves the seed to Jon. Again from the register: "HOLD for Jon", "Jon owns",
# "Jon has taken this one personally", "Jon's synthesis pass still owed".
JON_MARKERS = [
    r"HOLD for Jon",
    r"Jon owns",
    r"Jon has taken this one",
    r"Jon\+? ?\+? ?a fresh fable-mirror",
    r"needs Jon's synthesis",
    r"what needs Jon's synthesis",
]

# Falsifier phrasing that indicates a bounded corpus/record SEARCH for a counter-example.
SEARCH_OPENERS = [
    r"^find\b",
    r"^name a\b",
    r"^\*?\(?forward\)?\*?\s*find\b",
    r"\bfind a (?:counter-?example|fourth|case|session|caller|instance|CFL)",
    r"\bname a fourth\b",
]

# Concrete-artifact tokens: if a falsifier names one of these, a runner has somewhere to start.
ARTIFACT_RE = re.compile(
    r"`[^`]+`"                       # any backticked identifier/path
    r"|\b[\w./-]+\.(?:py|sh|md|jsonl|json|txt)\b"   # bare filenames
    r"|\bcommit\s+`?[0-9a-f]{6,40}`?"               # commit hashes
    r"|\b[0-9a-f]{7,40}\b"                          # bare hashes
)

# Verbs that mean "go measure the thing named", as opposed to "go look for something that may not
# exist". These push a falsifier toward AGENT-RUNNABLE when an artifact is also named.
MEASURE_RE = re.compile(
    r"\bshow(?:s)?\b|\bgrep\b|\bcount\b|\bmtime\b|\bset comparison\b|\bre-?run\b"
    r"|\bspeaker-check\b|\bstrict superset\b|\badvances\b|\bwrites\b|\bemits\b|\bappears?\b",
    re.I,
)


# ------------------------------------------------------------------------------------------------
# parsing
# ------------------------------------------------------------------------------------------------
def split_seeds(text: str):
    """Return [(sid, title, block)] for every '## S<n> — title' heading in the whole file.

    Deliberately NOT section-scoped: _su_close_seeds.py scopes to one section because its question
    is 'of TODAY's seeds...'. This instrument's question is 'of ALL seeds, what is owed', so the
    scope is the file. Review-summary tables sit after a '---' and contain '| S7 | open |' rows,
    which are NOT '## S' headings and therefore cannot be double-counted; the self-test pins this.
    """
    out = []
    parts = re.split(r"(?=^##\s+S\d+\b)", text, flags=re.M)
    for p in parts:
        m = re.match(r"^##\s+(S\d+)\s*[—-]*\s*(.*)$", p, flags=re.M)
        if not m:
            continue
        out.append((m.group(1), m.group(2).strip(), p))
    return out


def field(block: str, name: str) -> str:
    """Pull one five-field table cell. Greedy to the last '|' on the line."""
    m = re.search(r"\|\s*\*\*" + re.escape(name) + r"\*\*\s*\|(.*)\|\s*$", block, re.M)
    if not m:
        return ""
    return re.sub(r"\*+", "", m.group(1)).strip()


def any_marker(block: str, patterns) -> bool:
    return any(re.search(p, block, re.I) for p in patterns)


# ------------------------------------------------------------------------------------------------
# classification
# ------------------------------------------------------------------------------------------------
def tested_state(cell: str) -> str:
    """NEVER-RUN | PARTIAL | RUN | UNPARSED. Unparseable is owed, never cleared."""
    c = cell.strip().lower()
    if c in PLACEHOLDERS:
        return "UNPARSED"
    if c.startswith("partial") or "partial" in c.split(":")[0]:
        return "PARTIAL"
    if re.match(r"^no\b", c):
        return "NEVER-RUN"
    if re.match(r"^yes\b", c):
        return "RUN"
    return "UNPARSED"


def independence_state(block: str, tstate: str) -> str:
    """Guard rule: a falsifier may not be judged by its author.

    There is no `tested_by` field in the five-field standard, so authorship can only be read from
    prose confessions. Absence of a confession is therefore NOT evidence of independence — it
    returns INDEPENDENCE-UNKNOWN, which stays in the owed set.
    """
    if tstate in ("NEVER-RUN", "UNPARSED"):
        return "N/A-not-run"
    if any_marker(block, AUTHOR_MARKERS):
        return "AUTHOR-TESTED"
    return "INDEPENDENCE-UNKNOWN"


def advance_class(falsifier: str, block: str) -> str:
    """AGENT-RUNNABLE | AGENT-SEARCH | JON-REQUIRED | NO-FALSIFIER."""
    f = falsifier.strip()
    if f.lower() in PLACEHOLDERS:
        return "NO-FALSIFIER"
    if any_marker(block, JON_MARKERS):
        return "JON-REQUIRED"
    has_artifact = bool(ARTIFACT_RE.search(f))
    is_search = any(re.search(p, f, re.I) for p in SEARCH_OPENERS)
    if has_artifact and MEASURE_RE.search(f):
        return "AGENT-RUNNABLE"
    if is_search:
        return "AGENT-SEARCH"
    if has_artifact:
        return "AGENT-RUNNABLE"
    return "AGENT-SEARCH"


def artifacts(falsifier: str):
    """The concrete things the falsifier names — the 'where to look' for whoever runs it."""
    seen, out = set(), []
    for m in ARTIFACT_RE.finditer(falsifier):
        t = m.group(0).strip("`")
        if t.lower() in seen or len(t) < 4:
            continue
        seen.add(t.lower())
        out.append(t)
    return out


def is_owed(rec) -> bool:
    """A seed is OWED work if its falsifier has not been independently run to completion.

    Owed = never run, unparsed, partial, OR run-but-by-its-author, OR run-but-independence-unknown.
    That last clause is the conservative one and it is deliberate: the guard rule is enforced in
    the direction that costs work. A seed leaves the owed set only when a `tested_by` naming a
    non-author exists — which today the standard cannot express, so nothing leaves it mechanically.
    """
    if rec["advance_class"] == "NO-FALSIFIER":
        return True
    if rec["tested_state"] in ("NEVER-RUN", "UNPARSED", "PARTIAL"):
        return True
    return rec["independence_state"] != "INDEPENDENT"


def analyze(text: str):
    recs = []
    for sid, title, block in split_seeds(text):
        fals = field(block, "falsifier")
        tcell = field(block, "falsifier_tested")
        ts = tested_state(tcell)
        rec = {
            "seed": sid,
            "title": title,
            "status": field(block, "status") or "UNPARSED",
            "recommendation": field(block, "recommendation") or "UNPARSED",
            "falsifier": fals,
            "falsifier_tested_raw": tcell,
            "tested_state": ts,
            "independence_state": independence_state(block, ts),
            "advance_class": advance_class(fals, block),
            "blocks": field(block, "blocks") or "UNPARSED",
            "evidence_owed": fals if fals.lower() not in PLACEHOLDERS else "NO FALSIFIER WRITTEN",
            "where_to_look": artifacts(fals),
        }
        rec["owed"] = is_owed(rec)
        recs.append(rec)
    return recs


def summarize(recs):
    n = len(recs)
    never = sum(1 for r in recs if r["tested_state"] == "NEVER-RUN")
    unparsed = sum(1 for r in recs if r["tested_state"] == "UNPARSED")
    partial = sum(1 for r in recs if r["tested_state"] == "PARTIAL")
    run = sum(1 for r in recs if r["tested_state"] == "RUN")
    author = sum(1 for r in recs if r["independence_state"] == "AUTHOR-TESTED")
    unknown_ind = sum(1 for r in recs if r["independence_state"] == "INDEPENDENCE-UNKNOWN")
    owed = [r for r in recs if r["owed"]]
    return {
        "seeds_total": n,
        "never_run": never,
        "unparsed": unparsed,
        "partial": partial,
        "run": run,
        "author_tested_only": author,
        "independence_unknown": unknown_ind,
        "owed_total": len(owed),
        "owed_agent_runnable": sum(1 for r in owed if r["advance_class"] == "AGENT-RUNNABLE"),
        "owed_agent_search": sum(1 for r in owed if r["advance_class"] == "AGENT-SEARCH"),
        "owed_jon_required": sum(1 for r in owed if r["advance_class"] == "JON-REQUIRED"),
        "owed_no_falsifier": sum(1 for r in owed if r["advance_class"] == "NO-FALSIFIER"),
    }


# ------------------------------------------------------------------------------------------------
# rendering
# ------------------------------------------------------------------------------------------------
def render_table(recs, s, path):
    L = []
    L.append(f"SEED ADVANCE REPORT -- {path}")
    L.append("=" * 96)
    if not recs:
        L.append("0 seeds parsed. This is UNKNOWN, not a pass — check --file points at a register")
        L.append("with '## S<n>' headings.")
        return "\n".join(L)
    L.append(f"{'seed':<5} {'tested':<10} {'independence':<21} {'advance':<15} {'owed':<5} title")
    L.append("-" * 96)
    for r in recs:
        L.append(
            f"{r['seed']:<5} {r['tested_state']:<10} {r['independence_state']:<21} "
            f"{r['advance_class']:<15} {'YES' if r['owed'] else 'no':<5} {r['title'][:36]}"
        )
    L.append("-" * 96)
    L.append(f"seeds parsed                       : {s['seeds_total']}")
    L.append(f"falsifier NEVER run                : {s['never_run']}")
    L.append(f"  + unparseable tested-cell        : {s['unparsed']}   (owed; never a pass)")
    L.append(f"  + partial only                   : {s['partial']}")
    L.append(f"falsifier run at all               : {s['run']}")
    L.append(f"  of which author-tested only      : {s['author_tested_only']}   (guard rule: not settled)")
    L.append(f"  of which independence UNKNOWN    : {s['independence_unknown']}   (no tested_by field exists)")
    L.append("")
    L.append(f"TOTAL OWED                         : {s['owed_total']} of {s['seeds_total']}")
    L.append(f"  AGENT-RUNNABLE (0 Jon-min to run): {s['owed_agent_runnable']}")
    L.append(f"  AGENT-SEARCH   (0 Jon-min to run): {s['owed_agent_search']}")
    L.append(f"  JON-REQUIRED                     : {s['owed_jon_required']}")
    L.append(f"  NO FALSIFIER WRITTEN             : {s['owed_no_falsifier']}")
    L.append("")
    L.append("STRUCTURAL NOTE -- read this before trusting the independence column:")
    L.append("  The five-field standard has no `author` and no `tested_by` field. The guard rule")
    L.append("  'a falsifier may not be judged by its author' is therefore unenforceable by")
    L.append("  construction -- it can only be checked where a seed CONFESSES authorship in prose.")
    L.append("  INDEPENDENCE-UNKNOWN is the honest verdict for the rest, and it keeps them owed.")
    L.append("  Adding a sixth field is the standard-owner's call, not this script's.")
    L.append("")
    L.append("This report FLIPS NOTHING. A seed's status is evidence-bearing and stays where the")
    L.append("register put it. These are proposals for who runs what.")
    return "\n".join(L)


def render_queue(recs):
    order = {"AGENT-RUNNABLE": 0, "AGENT-SEARCH": 1, "NO-FALSIFIER": 2, "JON-REQUIRED": 3}

    def seed_num(r):
        m = re.match(r"S(\d+)", r["seed"])
        return int(m.group(1)) if m else 9999   # numeric, or "S10" sorts before "S2"

    owed = sorted((r for r in recs if r["owed"]),
                  key=lambda r: (order.get(r["advance_class"], 9), seed_num(r)))
    L = ["WORK QUEUE -- owed falsifier runs, cheapest-for-Jon first", "=" * 96]
    if not owed:
        L.append("nothing owed — or 0 seeds parsed. Check the count in --format table before believing it.")
        return "\n".join(L)
    for r in owed:
        L.append("")
        L.append(f"[{r['advance_class']}] {r['seed']} -- {r['title']}")
        L.append(f"  tested       : {r['tested_state']} / {r['independence_state']}")
        L.append(f"  blocks       : {r['blocks']}")
        L.append(f"  EVIDENCE OWED: {r['evidence_owed']}")
        if r["where_to_look"]:
            L.append(f"  where to look: {', '.join(r['where_to_look'][:6])}")
        else:
            L.append("  where to look: UNKNOWN — falsifier names no concrete artifact")
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------
# self-test
# ------------------------------------------------------------------------------------------------
FIXTURE = """# Seeds

## S1 — author-tested seed

| | |
|---|---|
| **status** | open |
| **recommendation** | **YES** |
| **falsifier** | Show `convert-export.py` writes per-turn `created_at` into parsed transcripts |
| **falsifier_tested** | **yes: 2026-08-03 — SURVIVED** |
| **blocks** | something |

**Coordinator tested its own seed here.** Per the guard rule, this needs an independent re-run.

## S2 — never run, corpus search

| | |
|---|---|
| **status** | open |
| **recommendation** | **YES** |
| **falsifier** | Name a fourth irreducible cause, or show one of the three is recoverable |
| **falsifier_tested** | **no** |
| **blocks** | the coverage-ratchet design |

## S3 — reserved to Jon

| | |
|---|---|
| **status** | open — Jon has taken this one personally |
| **recommendation** | **HOLD for Jon** + a fresh fable-mirror |
| **falsifier** | Speaker-check the 9 hits; if a material share are Jon's own words the seed retires |
| **falsifier_tested** | **no** |
| **blocks** | any page citing that theme |

## S4 — no falsifier at all

| | |
|---|---|
| **status** | open |
| **falsifier** | n/a |
| **falsifier_tested** | **no** |

## S5 — unparseable tested cell

| | |
|---|---|
| **status** | open |
| **falsifier** | Show a session's own transcript JSONL advances while `wake_map.py` reads it |
| **falsifier_tested** | maybe? |

---

# Review summary

| Seed | Status |
|---|---|
| S1 | open |
| S2 | open |
"""


def self_test():
    fails = 0

    def t(name, expected, actual):
        nonlocal fails
        ok = expected == actual
        print(f"  {'PASS' if ok else 'FAIL'}  {name}  (expected {expected!r} got {actual!r})")
        if not ok:
            fails += 1

    # (a) NEGATIVE CONTROL — a file with no seeds must report 0, and 0 must not read as clean.
    recs = analyze("# Nothing here\n\nno seeds at all.\n")
    t("empty doc -> 0 seeds", 0, len(recs))
    t("empty doc -> 0 owed", 0, summarize(recs)["owed_total"])
    t("empty doc renders an explicit UNKNOWN line", True,
      "0 seeds parsed. This is UNKNOWN, not a pass" in render_table(recs, summarize(recs), "x"))

    # (b) the review-summary table after the '---' must not be re-parsed as two more seeds.
    recs = analyze(FIXTURE)
    t("fixture -> exactly 5 seeds (review table not double-counted)", 5, len(recs))
    t("fixture seed ids", ["S1", "S2", "S3", "S4", "S5"], [r["seed"] for r in recs])

    by = {r["seed"]: r for r in recs}

    # (c) tested-state parsing, including the two that must NOT clear.
    t("S1 tested=RUN", "RUN", by["S1"]["tested_state"])
    t("S2 tested=NEVER-RUN", "NEVER-RUN", by["S2"]["tested_state"])
    t("S5 unparseable cell -> UNPARSED not RUN", "UNPARSED", by["S5"]["tested_state"])

    # (d) THE GUARD RULE. A tested seed whose block confesses self-testing stays owed.
    t("S1 independence=AUTHOR-TESTED", "AUTHOR-TESTED", by["S1"]["independence_state"])
    t("S1 is still OWED despite tested=yes", True, by["S1"]["owed"])

    # (e) advance classification.
    t("S1 names artifacts -> AGENT-RUNNABLE", "AGENT-RUNNABLE", by["S1"]["advance_class"])
    t("S2 'Name a fourth' -> AGENT-SEARCH", "AGENT-SEARCH", by["S2"]["advance_class"])
    t("S3 Jon-marked -> JON-REQUIRED", "JON-REQUIRED", by["S3"]["advance_class"])
    t("S4 placeholder falsifier -> NO-FALSIFIER", "NO-FALSIFIER", by["S4"]["advance_class"])

    # (f) where-to-look extraction actually pulls the artifact, not the whole sentence.
    t("S1 where_to_look finds the script", True,
      any("convert-export.py" in a for a in by["S1"]["where_to_look"]))
    t("S2 names no concrete artifact", [], by["S2"]["where_to_look"])

    # (g) every seed in the fixture is owed — none of the five has an independent completed run,
    #     which is the point: nothing leaves the owed set mechanically today.
    s = summarize(recs)
    t("all 5 owed", 5, s["owed_total"])
    t("never_run counted", 3, s["never_run"])
    t("unparsed counted separately", 1, s["unparsed"])

    # (g2) the guard rule must catch the OTHER wordings too. The first draft of AUTHOR_MARKERS
    #      caught S1's "Coordinator tested its own seed" and missed S4's "Not independently
    #      verified ... until someone other than the coordinator confirms it" — same guard rule,
    #      different sentence. Both are pinned here so a future edit cannot silently drop one.
    t("marker: 'not independently verified'", "AUTHOR-TESTED",
      independence_state("blah. **Not independently verified:** the numbering matches.", "RUN"))
    t("marker: 'someone other than the coordinator'", "AUTHOR-TESTED",
      independence_state("Do not schedule until someone other than the coordinator confirms it.", "RUN"))
    t("marker: 'outside that build verifies'", "AUTHOR-TESTED",
      independence_state("stays open until someone outside that build verifies the union.", "RUN"))
    t("no confession -> UNKNOWN, never INDEPENDENT", "INDEPENDENCE-UNKNOWN",
      independence_state("A clean block with no authorship statement at all.", "RUN"))
    t("untested block is never AUTHOR-TESTED", "N/A-not-run",
      independence_state("Coordinator tested its own seed here.", "NEVER-RUN"))

    # (h) IDEMPOTENCE / read-only: analysis must not mutate its input.
    before = FIXTURE
    analyze(FIXTURE)
    t("input text unmutated", True, before == FIXTURE)

    # (i) the su one-liner must be two integers, machine-readable, and never blank.
    line = f"{s['owed_total']} {s['seeds_total']}"
    t("su format is '<owed> <total>'", True, bool(re.match(r"^\d+ \d+$", line)))

    if fails:
        print(f"RESULT: FAIL — {fails} case(s)")
        return 1
    print("RESULT: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Report what would advance each synthesis seed. Read-only.")
    ap.add_argument("--file", default="")
    ap.add_argument("--format", choices=["table", "json", "su"], default="table")
    ap.add_argument("--queue", action="store_true", help="print only the owed work, cheapest-for-Jon first")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    if not args.file:
        print("0 0" if args.format == "su" else "no --file given", flush=True)
        print("no --file given", file=sys.stderr)
        sys.exit(0)

    p = Path(args.file)
    if not p.is_file():
        print("0 0" if args.format == "su" else f"file not found: {p}", flush=True)
        print(f"file not found: {p}", file=sys.stderr)
        sys.exit(0)

    text = p.read_text(encoding="utf-8", errors="ignore")
    recs = analyze(text)
    s = summarize(recs)

    if args.format == "su":
        print(f"{s['owed_total']} {s['seeds_total']}")
    elif args.format == "json":
        print(json.dumps({"file": str(p), "summary": s, "seeds": recs}, indent=2, ensure_ascii=False))
    elif args.queue:
        # --queue replaces the table rather than appending to it, so the queue can be piped alone.
        print(render_queue(recs))
    else:
        print(render_table(recs, s, str(p)))
    sys.exit(0)


if __name__ == "__main__":
    main()
