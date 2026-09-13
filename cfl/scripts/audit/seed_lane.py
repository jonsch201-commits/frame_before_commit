#!/usr/bin/env python
"""seed_lane.py -- ticket B-6: the seed pipeline, as a state machine with a mechanical advance rule.

WHY THIS EXISTS. Jon, 2026-08-05 (`wiki/sources/infrastructure/jon-wayfinder-vision-2026-08-05-
ab3ddc.md:63-64`, typos his): *"I have noticed that you've said no to a number of seeds bieng formed
because it would presumably be too much for me. That is true, and a barrior for us to work through
together."*

`seed_advance.py` (B-6 half 1) answers "who could run each falsifier". It is read-only, it has no
states, and it cannot tell you whether a seed has MOVED. This file is the pipeline: it reads the
three states B-6 D1 defined (FORMED -> RUN -> SYNTHESIS), enforces the advance rule mechanically,
and computes the bandwidth arithmetic that decides whether the design actually works.

THE BANDWIDTH CLAIM THIS INSTRUMENT EXISTS TO TEST, stated as arithmetic so it can be wrong:

    Jon-minutes per week = f(min(eligible, CAP)) and is INVARIANT to pool size.

That invariance is the whole answer to the barrier. Seeds may form without limit; the SYNTHESIS
window is fixed at CAP per week; so unbounded formation raises LATENCY and never raises Jon's cost.
Volume is not a reason to filter -- Jon ruled 2026-08-06, *"if this would make the wiki unnavicable,
then you just don't have good enough wiki orginization"*
(`wiki/intake-triage/jon-ruling-navigability-is-organization-2026-08-06.md`). Under this design the
correct response to a growing pool is never "form fewer seeds"; it is to raise the FIRE RATE by
running more falsifiers, which is 0 Jon-minutes, or for Jon to raise CAP, which is his call.

WHAT IT DOES NOT DO. It writes nothing to any register and flips no seed status. Its only write is
the batch page under --write-batch, and a batch page is a PROPOSAL addressed to Jon, not a status.
An agent may KILL a seed by its own pre-registered rule and may NEVER promote one (B-6 D2); this
file enforces that by rejecting any run record carrying `promote:` other than `no`.

Usage:
  python seed_lane.py                       # full pipeline report against the real lane
  python seed_lane.py --format json
  python seed_lane.py --batch               # render the next SYNTHESIS batch (<=CAP items)
  python seed_lane.py --write-batch <path>  # ... and write it
  python seed_lane.py --format su           # "<eligible> <pool>" for su_close.sh
  python seed_lane.py --self-test
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))

# seed_advance.py owns falsifier classification (AGENT-RUNNABLE / AGENT-SEARCH / JON-REQUIRED).
# Reused rather than reimplemented -- a sixth scanner is the failure this ticket named by name.
from seed_advance import (  # noqa: E402
    advance_class,
    field,
    independence_state,
    tested_state,
)

# ---------------------------------------------------------------------------------------------
# Lane configuration. CAP and CADENCE are Jon's numbers to set; 3/week is B-6 D3's READING of
# "One thing from you one thing from me" and is explicitly NOT his stated figure (B-6 UNKNOWNs).
# ---------------------------------------------------------------------------------------------
CAP_PER_BATCH = 3
BATCHES_PER_WEEK = 1
MIN_PER_ITEM = 4          # 2 min read + 2 min decide, B-6's ESTIMATED four-line item format
MIN_SKIM_RETIRED = 2      # skimming the below-the-fold auto-retired list
BUDGET_PER_BATCH = 15     # the ratified <=15 Jon-min/batch envelope (turn-5 Rider 1)

REGISTER = "wiki/intake-triage/SEED-REGISTER-2026-08-03.md"
FORMED_GLOB = "wiki/intake-triage/seeds-harvest/FORMED-*.md"
RUNS_DIR = "wiki/intake-triage/seeds-harvest/runs"
BATCH_GLOB = "wiki/intake-triage/seeds-harvest/BATCH-*.md"

VALID_VERDICTS = {"FIRED", "SURVIVED", "UNRUNNABLE"}


# ---------------------------------------------------------------------------------------------
# parsing
# ---------------------------------------------------------------------------------------------
def split_any_seeds(text):
    """Every '# S<n>' / '## S<n>' / '# H<n>' heading. Both streams, one parser.

    seed_advance.split_seeds is register-only ('## S<n>'). The harvest lane writes '# H<n>' at
    depth 1. Rather than a second scanner, this generalises the heading pattern and keeps the id
    prefix, which is what the Ruling-1 priority rule keys on: S* before H*, always.
    """
    out = []
    parts = re.split(r"(?=^#{1,2}\s+[SH]\d+\b)", text, flags=re.M)
    for p in parts:
        m = re.match(r"^#{1,2}\s+([SH]\d+)\s*[—-]*\s*(.*)$", p, flags=re.M)
        if not m:
            continue
        out.append((m.group(1), m.group(2).strip(), p))
    return out


def parse_frontmatter(text):
    """Minimal YAML-subset reader: `key: value`, quoted or bare, plus `key: |` blocks.

    Deliberately not PyYAML -- this must run with the stdlib only, same as every other instrument
    in scripts/audit/. An unparseable frontmatter returns {} and the caller reports the record
    MALFORMED, which keeps the seed owed. Failing toward 'owed' is the direction that costs work.
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    out, key, block = {}, None, []
    for line in m.group(1).split("\n"):
        if key is not None:
            if line.startswith(("  ", "\t")) or not line.strip():
                block.append(line.strip())
                continue
            out[key] = "\n".join(block).strip()
            key, block = None, []
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not km:
            continue
        k, v = km.group(1), km.group(2).strip()
        if v in ("|", ">"):
            key, block = k, []
            continue
        out[k] = v.strip().strip('"').strip("'")
    if key is not None:
        out[key] = "\n".join(block).strip()
    return out


def load_seeds(repo):
    """Every seed in both streams, with its source file and stream."""
    seeds = []
    reg = repo / REGISTER
    files = ([(reg, "register")] if reg.is_file() else [])
    files += [(p, "harvest") for p in sorted(repo.glob(FORMED_GLOB))]
    for path, stream in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for sid, title, block in split_any_seeds(text):
            fals = field(block, "falsifier")
            tcell = field(block, "falsifier_tested")
            ts = tested_state(tcell)
            seeds.append({
                "seed": sid,
                "stream": stream,
                "source": str(path.relative_to(repo)).replace("\\", "/"),
                "title": title,
                "falsifier": fals,
                "author": field(block, "author") or "UNKNOWN",
                "tested_by": field(block, "tested_by") or "UNKNOWN",
                "tested_state": ts,
                "independence_state": independence_state(block, ts),
                "advance_class": advance_class(fals, block),
                "blocks": field(block, "blocks") or "UNPARSED",
            })
    return seeds


def load_runs(repo):
    """Every run record, each carrying its contract violations. A violation never advances a seed."""
    runs = []
    d = repo / RUNS_DIR
    if not d.is_dir():
        return runs
    for p in sorted(d.glob("RUN-*.md")):
        fm = parse_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        # Seed id from the FILENAME when the frontmatter cannot supply it. Found by running the
        # contract against a real garbage file on disk rather than a fixture: without this, a
        # malformed record cannot be attached to any seed, so the seed reports FORMED -- "no run
        # record exists" -- while a broken run record sits right there. A check that reports a pass
        # by resolving nothing is this program's most-repeated defect; the live negative control is
        # what caught it, and a unit test alone would not have.
        fname_seed = ""
        fm_name = re.match(r"^RUN-([SH]\d+)-", p.name)
        if fm_name:
            fname_seed = fm_name.group(1)
        rec = {
            "path": str(p.relative_to(repo)).replace("\\", "/"),
            "seed": fm.get("seed", "") or fname_seed,
            "seed_from_filename": (not fm.get("seed", "")) and bool(fname_seed),
            "verdict": (fm.get("verdict", "") or "").strip().upper(),
            "author": fm.get("author", "UNKNOWN"),
            "run_by": fm.get("run_by", ""),
            "promote": (fm.get("promote", "") or "").strip().lower(),
            "survives_narrowly": fm.get("survives_narrowly", "").strip(),
            "sources_searched": fm.get("sources_searched", "").strip(),
            "independent_of": fm.get("independent_of", "").strip(),
            "run_date": fm.get("run_date", ""),
            "malformed": not fm,
        }
        rec["violations"] = check_run(rec)
        rec["valid"] = not rec["violations"]
        runs.append(rec)
    return runs


# ---------------------------------------------------------------------------------------------
# THE ADVANCE RULE -- four checks, each one a rule that was prose before this file existed
# ---------------------------------------------------------------------------------------------
def check_run(r):
    """Contract violations. Empty list == the run may advance its seed.

    Each check is a rule that existed only as prose until now. S11 is the seed that says a control
    in the rejected shape (prose, unenforced) passes every review of its content and then does
    nothing -- MR-7 is the worked example, a correct ruling that produced zero seeds. So these are
    checks, not sentences.
    """
    v = []
    if r["malformed"]:
        return ["MALFORMED -- no parseable frontmatter; seed stays owed"]
    if r["verdict"] not in VALID_VERDICTS:
        v.append("BAD-VERDICT -- %r not in %s" % (r["verdict"], sorted(VALID_VERDICTS)))
    # 1. agents may kill, never promote (B-6 D2)
    if r["promote"] != "no":
        v.append("PROMOTE-VIOLATION -- promote:%r; an agent may never promote a seed" % r["promote"])
    # 2. a falsifier may not be judged by its author (register guard rule, now enforceable)
    if not r["run_by"]:
        v.append("NO-RUNNER -- run_by is empty; independence cannot be established")
    elif r["author"] != "UNKNOWN" and r["run_by"].strip() == r["author"].strip():
        v.append("SELF-RUN -- run_by == author (%s); guard rule blocks this" % r["run_by"])
    elif r["author"] == "UNKNOWN" and not r["independent_of"]:
        v.append("UNKNOWN-AUTHOR -- author unknown and no independent_of attestation")
    # 3. FIRED requires survives_narrowly (mirror ruling item 4; the S4 precedent)
    if r["verdict"] == "FIRED" and not r["survives_narrowly"]:
        v.append("NO-SURVIVES-NARROWLY -- a fired falsifier may not retire a seed silently")
    # 4. a null is never a pass; it needs its denominator
    if r["verdict"] == "SURVIVED":
        if not re.match(r"^\d+$", r["sources_searched"]):
            v.append("NO-DENOMINATOR -- SURVIVED requires an integer sources_searched")
        elif int(r["sources_searched"]) == 0:
            v.append("ZERO-DENOMINATOR -- 'searched 0 sources, found none' is not a run")
    return v


def batched_seeds(repo):
    """Seed ids that already appear in a batch page -- they are with Jon, not in the pool."""
    out = set()
    for p in sorted(repo.glob(BATCH_GLOB)):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"^##\s+\**([SH]\d+)\b", text, re.M):
            out.add(m.group(1))
    return out


DISPOSITIONS = "wiki/intake-triage/seeds-harvest/DISPOSITIONS.md"
DISPOSITION_STATE = {
    "synthesize": ("SYNTHESIZED", "Jon ruled synthesize -> prototype ticket owed"),
    "hold": ("HELD", "Jon ruled hold -> returns to a later batch, not dropped"),
    "retire": ("RETIRED-BY-JON", "Jon ruled retire"),
    "re-specify": ("RESPEC", "Jon ruled re-specify -> a new falsifier is owed, agent-writable"),
    "respec": ("RESPEC", "Jon ruled re-specify -> a new falsifier is owed, agent-writable"),
}


def load_dispositions(repo):
    """Jon's one-word answers, transcribed. `| S9 | synthesize | 2026-08-07 | note |`.

    He never edits this file. He answers a batch page in one word per item and the coordinator
    transcribes -- which is the whole point: his interface is a word, not a schema. The file is the
    machine's copy of what he said, and the `note` column is where his actual words go verbatim.
    """
    out = {}
    p = repo / DISPOSITIONS
    if not p.is_file():
        return out
    for m in re.finditer(r"^\|\s*\**([SH]\d+)\**\s*\|\s*([a-z-]+)\s*\|([^|]*)\|",
                         p.read_text(encoding="utf-8", errors="ignore"), re.M | re.I):
        out[m.group(1)] = (m.group(2).strip().lower(), m.group(3).strip())
    return out


def pipeline_state(seed, runs, already_batched, dispositions=None):
    """FORMED | RUN-BLOCKED | NEEDS-RESPEC | RETIRED | ELIGIBLE | BATCHED | <Jon's disposition>."""
    mine = [r for r in runs if r["seed"] == seed["seed"]]
    valid = [r for r in mine if r["valid"]]
    d = (dispositions or {}).get(seed["seed"])
    if d:
        state, why = DISPOSITION_STATE.get(d[0], ("DISPOSED", "unrecognised disposition %r" % d[0]))
        return state, (why + (" -- " + d[1] if d[1] else "")), mine
    if seed["seed"] in already_batched:
        return "BATCHED", "with Jon", mine
    if not mine:
        # A JON-REQUIRED seed can never acquire an agent run BY DEFINITION -- its falsifier needs
        # a judgment or a synthesis Jon has claimed. Left in FORMED it would sit there forever,
        # invisible, waiting for a run that is not possible. That is the deposit-only defect
        # reproducing itself INSIDE the mechanism built to end it, which is how S11 says these
        # things fail. So it goes to Jon on the strength of the classification alone, honestly
        # priced: he pays for the run as well as the synthesis.
        if seed.get("advance_class") == "JON-REQUIRED":
            return ("ELIGIBLE-JON",
                    "falsifier needs Jon -- no agent run is possible; he pays for the run too",
                    mine)
        return "FORMED", "no run record exists", mine
    if not valid:
        return "RUN-BLOCKED", "; ".join(sorted(set(v for r in mine for v in r["violations"]))), mine
    if any(r["verdict"] == "FIRED" for r in valid):
        return "RETIRED", "falsifier fired; retired as stated by its own pre-registered rule", mine
    if any(r["verdict"] == "SURVIVED" for r in valid):
        n = max(int(r["sources_searched"]) for r in valid if r["verdict"] == "SURVIVED")
        return "ELIGIBLE", "searched %d sources, found none -- eligible, NOT confirmed" % n, mine
    return "NEEDS-RESPEC", "falsifier not executable as written; re-spec owed before Jon sees it", mine


# ---------------------------------------------------------------------------------------------
# bandwidth arithmetic -- the half of B-6 that is actually about Jon
# ---------------------------------------------------------------------------------------------
def bandwidth(rows):
    """Every number here carries its denominator. The invariance claim is the deliverable."""
    DONE = ("BATCHED", "SYNTHESIZED", "HELD", "RETIRED-BY-JON", "RESPEC", "DISPOSED")
    # Fire rate is computed from the RUN RECORDS, not from current states. Using states was wrong
    # and the error was self-flattering: a batched seed leaves ELIGIBLE, so shipping survivors to
    # Jon shrank the denominator and drove the reported fire rate UP -- the design would have
    # looked better precisely as it did more of the thing that costs him time. Caught by watching
    # the number move after writing the first batch page. Evidence does not un-happen when a seed
    # advances, so the denominator must be the runs.
    valid_runs = [x for r in rows for x in r.get("runs", [])
                  if x.get("valid") and x.get("verdict") in ("FIRED", "SURVIVED")]
    completed = [r for r in rows if r["state"] in ("RETIRED", "ELIGIBLE")]
    fired = [r for r in completed if r["state"] == "RETIRED"]
    eligible = [r for r in rows if r["state"] == "ELIGIBLE"]
    eligible_jon = [r for r in rows if r["state"] == "ELIGIBLE-JON"]
    pool = [r for r in rows if r["state"] not in DONE]
    owed = [r for r in rows if r["state"] in ("FORMED", "RUN-BLOCKED", "NEEDS-RESPEC")]

    cap_wk = CAP_PER_BATCH * BATCHES_PER_WEEK
    # ELIGIBLE-JON items are priced at DOUBLE, because he pays for the falsifier run as well as
    # the synthesis. Pricing them the same as an agent-run item would understate the batch and is
    # the kind of quietly-wrong number this program keeps catching after it has already been used.
    n_agent = min(len(eligible), CAP_PER_BATCH)
    n_jon = min(len(eligible_jon), CAP_PER_BATCH - n_agent)
    n_batch = n_agent + n_jon
    jon_min = (n_agent * MIN_PER_ITEM + n_jon * MIN_PER_ITEM * 2
               + (MIN_SKIM_RETIRED if fired else 0))

    b = {
        "pool_total": len(pool),
        "owed_runs": len(owed),
        "runs_completed": len(completed),
        "fired": len(fired),
        "eligible": len(eligible),
        "eligible_jon": len(eligible_jon),
        "cap_per_week": cap_wk,
        "items_next_batch": n_batch,
        "jon_min_next_batch": jon_min,
        "jon_min_budget": BUDGET_PER_BATCH,
        "within_budget": jon_min <= BUDGET_PER_BATCH,
    }
    n_fired_runs = len([x for x in valid_runs if x["verdict"] == "FIRED"])
    b["runs_recorded"] = len(valid_runs)
    # Seeds carrying at least one completed valid non-author run. This -- not the state-based
    # count -- is what the SU drain row must report: a batched seed HAS been run, and reporting it
    # as un-run would understate the drain by exactly the seeds that got furthest. Same defect
    # class as the fire-rate denominator above, pointing the other way.
    b["seeds_with_valid_run"] = len(set(
        r["seed"] for r in rows
        if any(x.get("valid") and x.get("verdict") in ("FIRED", "SURVIVED")
               for x in r.get("runs", []))))
    if valid_runs:
        b["fire_rate_num"] = n_fired_runs
        b["fire_rate_den"] = len(valid_runs)
        b["fire_rate"] = n_fired_runs / float(len(valid_runs))
        b["projected_eligible_from_owed"] = round(len(owed) * (1 - b["fire_rate"]), 1)
        tot = len(eligible) + b["projected_eligible_from_owed"]
        b["weeks_to_drain"] = round(tot / float(cap_wk), 1) if cap_wk else None
        b["max_sustainable_inflow_per_week"] = (
            round(cap_wk / (1 - b["fire_rate"]), 1) if b["fire_rate"] < 1 else float("inf")
        )
    else:
        b["fire_rate"] = None          # ABSENT renders UNKNOWN, never a pass
        b["weeks_to_drain"] = None
        b["max_sustainable_inflow_per_week"] = None
    return b


def select_batch(rows):
    """<=CAP eligible seeds. Ruling 1: the legacy 15 hold absolute priority over the new stream.

    Enforced, not asserted: if ANY register seed is eligible or still owed a run, no harvest seed
    may take a batch slot. That is the mirror's sequencing constraint made mechanical -- it was
    prose in MIRROR-RULING-seed-harvest-ordering-2026-08-06.md until this line.
    """
    eligible = [r for r in rows if r["state"] == "ELIGIBLE"]
    eligible_jon = [r for r in rows if r["state"] == "ELIGIBLE-JON"]
    register_unfinished = any(
        r["stream"] == "register" and r["state"] in ("FORMED", "RUN-BLOCKED", "NEEDS-RESPEC",
                                                     "ELIGIBLE", "ELIGIBLE-JON")
        for r in rows
    )
    if register_unfinished:
        eligible = [r for r in eligible if r["stream"] == "register"]
        eligible_jon = [r for r in eligible_jon if r["stream"] == "register"]

    def key(r):
        m = re.match(r"[SH](\d+)", r["seed"])
        return (0 if r["stream"] == "register" else 1, int(m.group(1)) if m else 9999)

    # Agent-run items fill the batch first: they are cheaper for him per item and they carry
    # independent evidence. JON-REQUIRED items fill any remaining slot rather than being stranded.
    out = sorted(eligible, key=key)[:CAP_PER_BATCH]
    out += sorted(eligible_jon, key=key)[:CAP_PER_BATCH - len(out)]
    return out, register_unfinished


# ---------------------------------------------------------------------------------------------
# PROMOTION -- the back of the pipeline. Jon's words were "seed discovery and creation and
# PROTOTYPING and IMPLEMENTATION", and a pipeline that stops at his decision has built the front
# three quarters of what he asked for.
#
# A seed Jon marks `synthesize` becomes a prototype ticket with NO FURTHER GATE, because there is a
# standing approval covering exactly this: *"I approve prototyping everything."* Re-asking would be
# the over-gating he has corrected four or more times. The ticket is emitted, not requested.
#
# `hold` is deliberately NOT a synonym for dropped -- a held seed returns to a later batch. That
# distinction is his own triage discipline (HELD returns, TRIAGE hands off) and it is the reason
# `hold` costs him one word instead of a decision he has to remember.
# ---------------------------------------------------------------------------------------------
def render_promotions(rows):
    prom = [r for r in rows if r["state"] == "SYNTHESIZED"]
    L = ["PROMOTION -- seeds Jon synthesized, now owed a prototype", "=" * 100]
    if not prom:
        L.append("0 seeds carry a `synthesize` disposition.")
        L.append("That is UNKNOWN about the design, not a pass: no batch has come back yet.")
        return "\n".join(L)
    for r in prom:
        L.append("")
        L.append("[PROTOTYPE OWED] %s -- %s" % (r["seed"], r["title"]))
        L.append("  survived      : %s" % r["why"])
        L.append("  blocks        : %s" % r["blocks"][:150])
        L.append("  source        : %s" % r["source"])
        L.append("  gate          : NONE. Standing approval covers it -- 'I approve prototyping")
        L.append("                  everything.' Build it; do not open a ticket asking to build it.")
    L.append("")
    L.append("%d of %d seeds in the lane are at PROTOTYPE." % (len(prom), len(rows)))
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------
# DISCOVERY -- the front of the pipeline. "seed discovery and creation", Jon's own words.
#
# `agent_end_ingest.py` already flags seed-shaped lines in every agent-end extract and prints the
# count in frontmatter. Nothing consumed them. That is the same deposit-only defect as the register
# itself, one stage earlier: a detector whose output nobody reads.
#
# THE LINE THIS DOES NOT CROSS, and it is the mirror's Ruling 2 constraint (1): the harvester may
# NOT synthesize a falsifier the originating agent did not imply. A falsifier retro-fitted by a
# third party to make an observation admissible is the author-judgment defect moved one seat over.
# So this stage NEVER forms a seed. It partitions flagged lines into:
#   ADMISSIBLE  -- the line itself states a falsifier with an operation. A harvester can form it
#                  without inventing anything.
#   FOG         -- claim-shaped, no author-stated falsifier. Routes to skills/intake or dies.
#                  The precedent is the aecd03 lane's own refusal: "not yet specifiable -- this is
#                  fog, not a sharp ticket".
# Both counts are reported. FOG is not a failure; an unrecorded FOG line is.
# ---------------------------------------------------------------------------------------------
SEED_SECTION_RE = re.compile(r"^### `seed` — (\d+) matched", re.M)
SEED_LINE_RE = re.compile(r"^- \*\*(T\d+) \(([A-Z])\)\*\* \(line (\d+)\) — (.*)$", re.M)

# An author-stated falsifier needs BOTH a falsifier token and a concrete operation. "hypothesis"
# and "testable claim" fire agent_end_ingest's detector but do not, alone, state a falsifier.
FALSIFIER_TOKEN_RE = re.compile(r"\bfalsifier\b|\bfalsifiable\b|\bfalsif(?:y|ies|ied)\b"
                                r"|\bretirement condition\b|\bfires if\b|\bkill condition\b", re.I)
OPERATION_RE = re.compile(r"\bfind\b|\bshow\b|\bgrep\b|\bname a\b|\bcount\b|\brun\b|\bsearch\b"
                          r"|\bmeasure\b|\bre-?run\b|\bcompare\b|\benumerate\b|\bcheck\b", re.I)

STOPWORDS = set("""a an and are as at be but by for from has have if in into is it its no not of on
or that the their then there this to was were what when which who will with would you your it's
its own not never every all any one two three""".split())


def _content_tokens(s):
    return set(w for w in re.findall(r"[a-z_][a-z0-9_.-]{2,}", (s or "").lower())
               if w not in STOPWORDS)


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


# Path/filename tokens are stripped BEFORE the admission test. Reported by the 2026-08-07
# harvester auditing this instrument: `RUN-S9-2026-08-07-falsifier-runner-f01909.md` contains the
# falsifier token AND the operation verb `run`, so a bare filename satisfied BOTH halves of the
# admission test at once and five run-record filenames were flagged ADMISSIBLE. The lane's own
# artifacts were polluting the lane's own discovery stage. That is seed H7's shape exactly -- a
# detector whose positive condition is satisfied by an artifact that merely NAMES the thing.
PATHISH_RE = re.compile(r"`[^`]*`|[^ ]*/[^ ]*|[^ ]+[.](?:md|py|sh|jsonl|json|txt)")


def _classify_line(txt, seeds, dup_threshold=0.28):
    """(verdict, duplicate_of) for one flagged line. The admission test, isolated so it is testable.

    ADMISSIBLE requires BOTH a falsifier token and a concrete operation. That conjunction is the
    whole guard: it is what stops the harvester from admitting an interesting sentence and then
    supplying the falsifier itself.
    """
    # The admission test runs on PROSE, not on cited paths. A claim must be made in a sentence.
    prose = PATHISH_RE.sub(" ", txt)
    has_f = bool(FALSIFIER_TOKEN_RE.search(prose))
    has_op = bool(OPERATION_RE.search(prose))
    toks = _content_tokens(txt)
    for s in seeds:
        if _jaccard(toks, _content_tokens(s["title"] + " " + s["falsifier"])) >= dup_threshold:
            return "DUPLICATE", s["seed"]
    return ("ADMISSIBLE" if (has_f and has_op) else "FOG"), ""


def discover(repo, seeds, dup_threshold=0.28):
    """Partition every seed-flagged line in every agent-end extract. Returns (candidates, stats)."""
    cands, stats = [], {"extracts_scanned": 0, "extracts_with_seed_lines": 0,
                        "lines_flagged": 0, "admissible": 0, "fog": 0, "duplicate": 0}
    for p in sorted(repo.glob("wiki/intake-triage/agent-end/*/*.i1.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        stats["extracts_scanned"] += 1
        m = SEED_SECTION_RE.search(text)
        if not m or m.group(1) == "0":
            continue
        stats["extracts_with_seed_lines"] += 1
        body = text[m.end():]
        nxt = re.search(r"^### ", body, re.M)
        body = body[:nxt.start()] if nxt else body
        for turn, speaker, line_no, txt in SEED_LINE_RE.findall(body):
            stats["lines_flagged"] += 1
            verdict, dup = _classify_line(txt, seeds, dup_threshold)
            stats[verdict.lower()] += 1
            toks = _content_tokens(txt)
            top = max([_jaccard(toks, _content_tokens(s["title"] + " " + s["falsifier"]))
                       for s in seeds] or [0.0])
            stats["max_similarity"] = max(stats.get("max_similarity", 0.0), top)
            cands.append({
                "extract": str(p.relative_to(repo)).replace("\\", "/"),
                "turn": turn, "speaker": speaker, "line": int(line_no),
                "verdict": verdict, "duplicate_of": dup,
                "text": txt.strip()[:400],
            })
    return cands, stats


def render_discovery(cands, stats):
    L = ["SEED DISCOVERY -- flagged lines in agent-end extracts, partitioned", "=" * 100]
    L.append("extracts scanned                 : %d" % stats["extracts_scanned"])
    L.append("  with >=1 seed-flagged line     : %d of %d"
             % (stats["extracts_with_seed_lines"], stats["extracts_scanned"]))
    L.append("seed-flagged lines               : %d" % stats["lines_flagged"])
    L.append("  ADMISSIBLE (author-stated falsifier + operation) : %d of %d"
             % (stats["admissible"], stats["lines_flagged"]))
    L.append("  DUPLICATE  (matches a seed already in the lane)  : %d of %d"
             % (stats["duplicate"], stats["lines_flagged"]))
    L.append("  FOG        (claim-shaped, no author falsifier)   : %d of %d"
             % (stats["fog"], stats["lines_flagged"]))
    L.append("")
    L.append("!! THE DUPLICATE CHECK IS NOT VALIDATED AND IS PROBABLY NOT WORKING. Measured this")
    L.append("   run: the HIGHEST token-overlap between any of the %d flagged lines and any seed"
             % stats["lines_flagged"])
    L.append("   already in the lane is %.3f, against a %.2f threshold -- so the check cannot have"
             % (stats.get("max_similarity", 0.0), 0.28))
    L.append("   fired even once, and a 0 duplicate count is NOT evidence there are no duplicates.")
    L.append("   Known positives exist: the mirror ruling names 6 seed lines in one scanned extract")
    L.append("   as this lane's 'first dedup test case', and H1-H9 were harvested from these very")
    L.append("   extracts. A one-line transcript excerpt and a formed seed share few content tokens")
    L.append("   because the seed is a REWRITE, not a quote. Lowering the threshold does not fix")
    L.append("   this; it would only manufacture a plausible number. Ruling 2's dedup obligation")
    L.append("   therefore still sits with the HARVESTING AGENT, by reading. This counter is")
    L.append("   instrumentation for that agent, not a substitute for it.")
    L.append("")
    L.append("FOG IS NOT A FAILURE. An unrecorded fog line is. The harvester may not invent a")
    L.append("falsifier the originating agent did not imply -- that is the author-judgment defect")
    L.append("moved one seat over (mirror Ruling 2). Fog routes to skills/intake or dies, recorded.")
    L.append("")
    if stats["admissible"]:
        L.append("ADMISSIBLE candidates -- a harvester can form these WITHOUT inventing a falsifier:")
        L.append("-" * 100)
        for c in cands:
            if c["verdict"] != "ADMISSIBLE":
                continue
            L.append("  %s:%s (%s)" % (c["extract"], c["line"], c["turn"]))
            L.append("    %s" % c["text"][:160])
    L.append("")
    L.append("This stage forms NOTHING, and it does NOT guarantee that no seed-shaped line is")
    L.append("dropped. That claim was written here on 2026-08-07 and falsified the same day by the")
    L.append("harvester auditing this instrument:")
    L.append("  * PRECISION measured 2 of 27 ADMISSIBLE (7.4%). The filter only checks that a")
    L.append("    falsifier token and an operation verb co-occur. It is a cheap pre-filter, and it")
    L.append("    is not a verdict -- a human or agent must read every candidate at source.")
    L.append("  * RECALL has at least three known misses, TWO OF THEM TOTAL: two extracts were")
    L.append("    flagged ZERO lines and each carried a seed that was then admitted by reading.")
    L.append("    Neither agent used the words falsifier / falsifiable / seed / hypothesis in the")
    L.append("    sentence that made the claim. A TOKEN-KEYED PASS CANNOT SEE A CLAIM STATED IN")
    L.append("    PLAIN LANGUAGE -- which is how the sharpest ones are usually stated.")
    L.append("So: this is a cheap net with measured holes, not a guarantee. Reading the extracts is")
    L.append("still owed. All of it still costs Jon zero minutes -- none of it is addressed to him.")
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------------------------
def render_report(rows, b, batch, gated, all_runs=None):
    L = ["SEED LANE -- pipeline state, FORMED -> RUN -> SYNTHESIS", "=" * 100]
    if not rows:
        L.append("0 seeds parsed. This is UNKNOWN, not a pass -- check the lane paths in this file.")
        return "\n".join(L)
    L.append("%-5s %-9s %-13s %-15s %s" % ("seed", "stream", "state", "class", "why"))
    L.append("-" * 100)
    for r in rows:
        L.append("%-5s %-9s %-13s %-15s %s" % (r["seed"], r["stream"], r["state"],
                                               r["advance_class"], r["why"][:52]))
    L.append("-" * 100)
    n_reg = sum(1 for r in rows if r["stream"] == "register")
    n_har = sum(1 for r in rows if r["stream"] == "harvest")
    L.append("seeds in lane            : %d  (register %d + harvest %d)" % (len(rows), n_reg, n_har))
    L.append("owed a non-author run    : %d of %d" % (b["owed_runs"], b["pool_total"]))
    L.append("runs completed & valid   : %d" % b["runs_completed"])
    L.append("  FIRED (auto-retired)   : %d" % b["fired"])
    L.append("  SURVIVED (eligible)    : %d" % b["eligible"])
    L.append("eligible w/o a run       : %d  (JON-REQUIRED -- no agent run is POSSIBLE; these would"
             % b["eligible_jon"])
    L.append("                           be stranded in FORMED forever if they were not batched)")
    orphans = [r for r in (all_runs or []) if not r["seed"]]
    if orphans:
        L.append("")
        L.append("!! %d ORPHANED RUN RECORD(S) -- no seed id in frontmatter OR filename, so these"
                 % len(orphans))
        L.append("   cannot block any seed and would otherwise be invisible. They are NOT a pass:")
        for r in orphans:
            L.append("     %s" % r["path"])
    L.append("")
    L.append("BANDWIDTH ARITHMETIC -- the half of B-6 that is about Jon, not about tooling")
    L.append("-" * 100)
    if b["fire_rate"] is None:
        L.append("  fire rate              : UNKNOWN -- 0 completed runs. UNKNOWN, never a pass.")
    else:
        L.append("  fire rate              : %d of %d completed runs = %.0f%%"
                 % (b["fire_rate_num"], b["fire_rate_den"], 100 * b["fire_rate"]))
        L.append("  projected eligible     : %s more from the %d owed runs, at that rate"
                 % (b["projected_eligible_from_owed"], b["owed_runs"]))
        L.append("  weeks to drain pool    : %s at %d/week" % (b["weeks_to_drain"], b["cap_per_week"]))
        L.append("  max sustainable inflow : %s new seeds/week  (above this the pool grows --"
                 " LATENCY grows, Jon-minutes do NOT)" % b["max_sustainable_inflow_per_week"])
    L.append("")
    L.append("  NEXT BATCH             : %d items (cap %d)" % (b["items_next_batch"], CAP_PER_BATCH))
    L.append("  JON-MINUTES NEXT BATCH : %d of a %d-minute budget  [%s]"
             % (b["jon_min_next_batch"], b["jon_min_budget"],
                "WITHIN" if b["within_budget"] else "OVER"))
    L.append("")
    L.append("  THE INVARIANCE, which is the answer to the barrier:")
    L.append("    Jon-minutes/week = min(eligible, %d) x %d + %d"
             % (CAP_PER_BATCH, MIN_PER_ITEM, MIN_SKIM_RETIRED))
    L.append("    -> bounded above by %d minutes REGARDLESS of how many seeds exist."
             % (CAP_PER_BATCH * MIN_PER_ITEM + MIN_SKIM_RETIRED))
    L.append("    Forming a seed cannot raise his cost. It can only raise latency. So the correct")
    L.append("    response to a growing pool is to RUN MORE FALSIFIERS (0 Jon-min) or for Jon to")
    L.append("    raise the cap. It is never 'form fewer seeds' -- volume is not a reason to filter.")
    if gated:
        L.append("")
        L.append("  RULING-1 GATE ACTIVE: register seeds S1-S15 are not drained, so no harvest-stream")
        L.append("  seed may take a batch slot. Enforced here, not merely asserted.")
    L.append("")
    L.append("This report flips no seed status and edits no register. A batch page is a PROPOSAL.")
    L.append("")
    L.append("READ THIS BEFORE COMPARING NUMBERS WITH seed_advance.py. That instrument will keep")
    L.append("reporting '15 of 15 owed' for the register no matter how many runs land here, and")
    L.append("that is CORRECT, not stale. It answers 'what does the register say about itself',")
    L.append("and the register is deliberately never edited by this lane -- its falsifier_tested")
    L.append("cells still read 'no'. This instrument answers 'what has actually been run', from")
    L.append("the run records. Two right answers to two different questions. The failure mode to")
    L.append("avoid is quoting one as a correction of the other; only Jon's disposition, or a")
    L.append("register edit he authorises, ever reconciles them.")
    return "\n".join(L)


def render_batch(rows, batch, b, as_of):
    """The ONLY artifact addressed to Jon. One page, four lines per item, four fixed options."""
    L = ["# Seed synthesis batch -- %s" % as_of, ""]
    L.append("**%d seeds, %d minutes.** Four options each, one word is a complete answer:"
             " **synthesize / hold / retire / re-specify**." % (len(batch), b["jon_min_next_batch"]))
    L.append("")
    L.append("Everything else in the lane -- **%d seeds total, %d still owed a run** -- is"
             " deliberately not on this page and costs you nothing."
             % (b["pool_total"], b["owed_runs"]))
    L.append("")
    if not batch:
        L.append("**No seed is eligible this week.** Nothing survived an independent falsifier run.")
        L.append("That is a real state, not an error, and it costs 0 minutes.")
        L.append("")
    for r in batch:
        L.append("## %s -- %s" % (r["seed"], r["title"]))
        L.append("")
        L.append("- **The claim:** %s" % r["title"])
        L.append("- **What the falsifier asked:** %s" % r["falsifier"][:400])
        L.append("- **What the independent run found:** %s" % r["why"])
        L.append("- **The one decision owed:** synthesize / hold / retire / re-specify the falsifier")
        L.append("- *source: `%s`*" % r["source"])
        L.append("")
    retired = [r for r in rows if r["state"] == "RETIRED"]
    L.append("---")
    L.append("")
    L.append("## Below the fold -- auto-retired this cycle (%d), skim only" % len(retired))
    L.append("")
    if not retired:
        L.append("None.")
    else:
        L.append("Each died by a rule written before the evidence. **What survives narrowly** is shown"
                 " because a fired falsifier is not always a dead claim -- S4 is the precedent.")
        L.append("")
        for r in retired:
            sn = ""
            for x in r["runs"]:
                if x["valid"] and x["verdict"] == "FIRED":
                    sn = x["survives_narrowly"]
                    break
            L.append("- **%s** -- %s. *Survives narrowly:* %s" % (r["seed"], r["title"], sn or "NOTHING"))
    L.append("")
    L.append("---")
    L.append("")
    L.append("*Generated by `scripts/audit/seed_lane.py`. Regenerate to refresh; do not hand-edit."
             " Nothing on this page changed a seed's status -- only your answer does.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------
# self-test -- negative controls first
# ---------------------------------------------------------------------------------------------
def _row(seed, stream, state):
    return {"seed": seed, "stream": stream, "state": state, "title": "t", "falsifier": "f",
            "why": "w", "source": "s", "advance_class": "AGENT-SEARCH", "blocks": "b", "runs": []}


def self_test():
    fails = [0]

    def t(name, expected, actual):
        ok = expected == actual
        print("  %s  %s  (expected %r got %r)" % ("PASS" if ok else "FAIL", name, expected, actual))
        if not ok:
            fails[0] += 1

    # (a) NEGATIVE CONTROL -- zero seeds must render an explicit UNKNOWN, never a clean pass.
    b0 = bandwidth([])
    t("0 seeds -> pool 0", 0, b0["pool_total"])
    t("0 completed runs -> fire rate UNKNOWN not 0", None, b0["fire_rate"])
    t("0 seeds renders UNKNOWN line", True,
      "0 seeds parsed. This is UNKNOWN, not a pass" in render_report([], b0, [], False))

    # (b) frontmatter parsing, including the block form.
    fm = parse_frontmatter("---\nseed: S9\nverdict: FIRED\nsurvives_narrowly: \"a smaller claim\"\n"
                           "commands_run: |\n  one\n  two\n---\nbody\n")
    t("fm seed", "S9", fm["seed"])
    t("fm quoted value unquoted", "a smaller claim", fm["survives_narrowly"])
    t("fm block scalar", "one\ntwo", fm["commands_run"])
    t("no frontmatter -> {}", {}, parse_frontmatter("no frontmatter here"))

    # (c) THE FOUR CONTRACT CHECKS. Each must block, and blocking must keep the seed owed.
    good = {"malformed": False, "verdict": "SURVIVED", "author": "coordinator", "run_by": "agent-x",
            "promote": "no", "survives_narrowly": "", "sources_searched": "9", "independent_of": ""}

    def mut(**kw):
        d = dict(good)
        d.update(kw)
        return d

    t("valid SURVIVED run passes", [], check_run(mut()))
    t("promote:yes blocked", True,
      any("PROMOTE-VIOLATION" in v for v in check_run(mut(promote="yes"))))
    t("self-run blocked", True,
      any("SELF-RUN" in v for v in check_run(mut(run_by="coordinator"))))
    t("unknown author w/o attestation blocked", True,
      any("UNKNOWN-AUTHOR" in v for v in check_run(mut(author="UNKNOWN"))))
    t("unknown author WITH attestation allowed", [],
      check_run(mut(author="UNKNOWN", independent_of="fresh agent, no prior contact")))
    t("FIRED without survives_narrowly blocked", True,
      any("NO-SURVIVES-NARROWLY" in v for v in check_run(mut(verdict="FIRED", sources_searched=""))))
    t("FIRED with survives_narrowly=NOTHING allowed", [],
      check_run(mut(verdict="FIRED", survives_narrowly="NOTHING", sources_searched="")))
    t("SURVIVED without denominator blocked", True,
      any("NO-DENOMINATOR" in v for v in check_run(mut(sources_searched=""))))
    t("SURVIVED with 0 sources blocked", True,
      any("ZERO-DENOMINATOR" in v for v in check_run(mut(sources_searched="0"))))
    t("bad verdict blocked", True,
      any("BAD-VERDICT" in v for v in check_run(mut(verdict="PASSED"))))
    t("malformed blocked", True,
      any("MALFORMED" in v for v in check_run(mut(malformed=True))))

    # (d) a blocked run must NOT advance its seed -- the direction that costs work.
    seed = {"seed": "S1", "stream": "register"}
    bad = mut(seed="S1", promote="yes")
    bad["violations"] = check_run(bad)
    bad["valid"] = False
    t("blocked run -> RUN-BLOCKED not ELIGIBLE", "RUN-BLOCKED", pipeline_state(seed, [bad], set())[0])

    ok = mut(seed="S1")
    ok["violations"], ok["valid"] = [], True
    t("valid SURVIVED -> ELIGIBLE", "ELIGIBLE", pipeline_state(seed, [ok], set())[0])
    fire = mut(seed="S1", verdict="FIRED", survives_narrowly="x", sources_searched="")
    fire["violations"], fire["valid"] = [], True
    t("valid FIRED -> RETIRED", "RETIRED", pipeline_state(seed, [fire], set())[0])
    unrun = mut(seed="S1", verdict="UNRUNNABLE", sources_searched="")
    unrun["violations"], unrun["valid"] = [], True
    t("valid UNRUNNABLE -> NEEDS-RESPEC", "NEEDS-RESPEC", pipeline_state(seed, [unrun], set())[0])
    t("no runs -> FORMED", "FORMED", pipeline_state(seed, [], set())[0])
    t("already batched -> BATCHED", "BATCHED", pipeline_state(seed, [ok], set(["S1"]))[0])

    # (e) THE INVARIANCE CLAIM -- Jon-minutes must not rise with pool size. This is the whole design.
    def rows_with(n):
        return [_row("S%d" % i, "register", "ELIGIBLE") for i in range(n)]
    b3, b50, b500 = bandwidth(rows_with(3)), bandwidth(rows_with(50)), bandwidth(rows_with(500))
    t("Jon-min at 3 eligible == at 50", b3["jon_min_next_batch"], b50["jon_min_next_batch"])
    t("Jon-min at 50 == at 500 (INVARIANT to pool)", b50["jon_min_next_batch"], b500["jon_min_next_batch"])
    t("Jon-min within the 15-min budget at 500 seeds", True, b500["within_budget"])
    t("pool DOES grow (latency is the price, and it is visible)", 500, b500["pool_total"])

    # (f) RULING 1 -- the legacy 15 must not be displaced by the harvest stream.
    mixed = [_row("S2", "register", "ELIGIBLE"),
             _row("S3", "register", "FORMED"),
             _row("H1", "harvest", "ELIGIBLE")]
    sel, gated = select_batch(mixed)
    t("Ruling-1 gate fires while register unfinished", True, gated)
    t("harvest seed excluded from batch", ["S2"], [r["seed"] for r in sel])
    sel2, gated2 = select_batch([_row("H1", "harvest", "ELIGIBLE")])
    t("gate releases when register is drained", False, gated2)
    t("harvest seed then admitted", ["H1"], [r["seed"] for r in sel2])

    # (g) batch size can never exceed the cap.
    t("batch capped", CAP_PER_BATCH, len(select_batch(rows_with(20))[0]))

    # (h) heading parser: both streams, and a review-summary table must not become seeds.
    txt = "## S1 -- a\n\nbody\n\n# H1 -- b\n\nbody\n\n---\n\n| Seed | Status |\n|---|---|\n| S7 | open |\n"
    t("parses both '## S' and '# H'", ["S1", "H1"], [s[0] for s in split_any_seeds(txt)])

    # (i) DISCOVERY admission test -- Ruling 2. A falsifier may not be invented by the harvester.
    seedset = [{"seed": "S9", "title": "union denominator", "falsifier": "show either source is a "
                "strict superset of the other, history.jsonl vs subagent"}]
    t("line with falsifier + operation -> ADMISSIBLE", ("ADMISSIBLE", ""),
      _classify_line("falsifier: find a caller of the routine where it inverts", seedset))
    t("hypothesis with no falsifier -> FOG", ("FOG", ""),
      _classify_line("hypothesis: the wiki is probably getting harder to navigate", seedset))
    t("falsifier word with no operation -> FOG", ("FOG", ""),
      _classify_line("this claim is falsifiable in principle, someday", seedset))
    t("near-copy of a lane seed -> DUPLICATE", "DUPLICATE",
      _classify_line("falsifier: show either source is a strict superset of the other -- every "
                     "history.jsonl message wrapper-matched in a subagent record", seedset)[0])
    t("a run-record FILENAME is not a seed candidate", "FOG",
      _classify_line("RUN-S9-2026-08-07-falsifier-runner-f01909.md", seedset)[0])
    t("a cited path is not a seed candidate", "FOG",
      _classify_line("- `wiki/intake-triage/seeds-harvest/runs/RUN-S4-2026-08-07-a55600.md`", seedset)[0])
    t("NEGATIVE CONTROL: stripping paths does not kill a real claim", "ADMISSIBLE",
      _classify_line("the falsifier is: show the extractor writes per-turn created_at", seedset)[0])
    t("NEGATIVE CONTROL: unrelated falsifier line is not a duplicate", "",
      _classify_line("falsifier: find a home thermostat that reports humidity", seedset)[1])

    # (i2) JON-REQUIRED must never be stranded in FORMED. It can NEVER acquire an agent run by
    #      definition, so a rule that waits for one waits forever -- the deposit-only defect
    #      reproducing inside the mechanism built to end it. Found by reading the real table, not
    #      by a test: S6 and S14 sat at FORMED with no possible path out.
    jonseed = {"seed": "S6", "stream": "register", "advance_class": "JON-REQUIRED"}
    t("JON-REQUIRED with no run -> ELIGIBLE-JON, not FORMED", "ELIGIBLE-JON",
      pipeline_state(jonseed, [], set())[0])
    t("NEGATIVE CONTROL: a normal seed with no run is still FORMED", "FORMED",
      pipeline_state({"seed": "S5", "stream": "register", "advance_class": "AGENT-SEARCH"},
                     [], set())[0])
    jr = _row("S6", "register", "ELIGIBLE-JON")
    t("ELIGIBLE-JON is priced at DOUBLE (he runs the falsifier too)",
      MIN_PER_ITEM * 2, bandwidth([jr])["jon_min_next_batch"])
    t("ELIGIBLE-JON reaches the batch rather than being stranded", ["S6"],
      [r["seed"] for r in select_batch([jr])[0]])
    t("agent-run items fill the batch before JON-REQUIRED ones",
      ["S2", "S3", "S4"],
      [r["seed"] for r in select_batch(
          [_row("S2", "register", "ELIGIBLE"), _row("S3", "register", "ELIGIBLE"),
           _row("S4", "register", "ELIGIBLE"), jr])[0]])

    # (i3) FIRE RATE MUST NOT MOVE WHEN A SEED IS BATCHED. The first implementation computed it
    #      from current states, so shipping a survivor to Jon removed it from the denominator and
    #      the reported rate went UP -- the design scoring itself better precisely as it did more
    #      of the thing that costs him time. Pinned here so it cannot come back.
    def _with_runs(state, verdict):
        r = _row("S1", "register", state)
        r["runs"] = [{"valid": True, "verdict": verdict, "survives_narrowly": "x",
                      "sources_searched": "5"}]
        return r
    pre = [_with_runs("RETIRED", "FIRED"), _with_runs("ELIGIBLE", "SURVIVED")]
    post = [_with_runs("RETIRED", "FIRED"), _with_runs("BATCHED", "SURVIVED")]
    t("fire rate is unchanged by batching a survivor",
      bandwidth(pre)["fire_rate"], bandwidth(post)["fire_rate"])
    t("fire rate denominator counts runs, not current states", 2, bandwidth(post)["fire_rate_den"])

    # (j) DISPOSITIONS -- the back of the pipeline. Jon's one word must move the seed, and `hold`
    #     must NOT be a synonym for dropped. His own triage discipline: HELD returns, TRIAGE hands off.
    t("synthesize -> SYNTHESIZED", "SYNTHESIZED",
      pipeline_state(seed, [ok], set(), {"S1": ("synthesize", "")})[0])
    t("hold -> HELD (returns to a later batch, not dropped)", "HELD",
      pipeline_state(seed, [ok], set(), {"S1": ("hold", "")})[0])
    t("retire -> RETIRED-BY-JON", "RETIRED-BY-JON",
      pipeline_state(seed, [ok], set(), {"S1": ("retire", "")})[0])
    t("re-specify -> RESPEC", "RESPEC",
      pipeline_state(seed, [ok], set(), {"S1": ("re-specify", "")})[0])
    t("unrecognised disposition -> DISPOSED, never silently ELIGIBLE", "DISPOSED",
      pipeline_state(seed, [ok], set(), {"S1": ("maybe", "")})[0])
    t("a disposition overrides BATCHED", "SYNTHESIZED",
      pipeline_state(seed, [ok], set(["S1"]), {"S1": ("synthesize", "")})[0])
    t("HELD leaves the pool (it is with Jon, not owed a run)", 0,
      bandwidth([_row("S1", "register", "HELD")])["pool_total"])
    t("no promotions -> explicit UNKNOWN, not a pass", True,
      "UNKNOWN about the design, not a pass" in render_promotions([_row("S1", "register", "FORMED")]))
    t("a SYNTHESIZED seed is owed a prototype with NO further gate", True,
      "gate          : NONE" in render_promotions([_row("S1", "register", "SYNTHESIZED")]))

    # (k) a batch page must be re-readable: the ids it names come back as BATCHED next run.
    page = render_batch([_row("S2", "register", "ELIGIBLE")], [_row("S2", "register", "ELIGIBLE")],
                        bandwidth([_row("S2", "register", "ELIGIBLE")]), "2026-08-07")
    t("batch page round-trips its seed ids", True, bool(re.search(r"^##\s+\**S2\b", page, re.M)))

    if fails[0]:
        print("RESULT: FAIL -- %d case(s)" % fails[0])
        return 1
    print("RESULT: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Seed pipeline: states, advance rule, bandwidth math.")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--format", choices=["table", "json", "su", "su-runs"], default="table")
    ap.add_argument("--promote", action="store_true",
                    help="list seeds Jon synthesized that are owed a prototype")
    ap.add_argument("--discover", action="store_true",
                    help="partition seed-flagged lines in agent-end extracts; forms nothing")
    ap.add_argument("--batch", action="store_true", help="render the next SYNTHESIS batch page")
    ap.add_argument("--write-batch", default="", help="also write it to this path")
    ap.add_argument("--as-of", default="", help="date stamp for the batch page")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    # Windows console defaults to cp1252 and the corpus is full of em-dashes and arrows. Without
    # this, a real run dies on an encoding error partway through printing a correct answer --
    # which is a broken instrument producing a plausible-looking partial output (seed S13).
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if args.self_test:
        sys.exit(self_test())

    repo = Path(args.repo)
    seeds = load_seeds(repo)

    if args.discover:
        cands, stats = discover(repo, seeds)
        if args.format == "json":
            print(json.dumps({"stats": stats, "candidates": cands}, indent=2, ensure_ascii=False))
        else:
            print(render_discovery(cands, stats))
        sys.exit(0)

    runs = load_runs(repo)
    done = batched_seeds(repo)
    disp = load_dispositions(repo)

    rows = []
    for s in seeds:
        st, why, mine = pipeline_state(s, runs, done, disp)
        r = dict(s)
        r.update({"state": st, "why": why, "runs": mine})
        rows.append(r)

    b = bandwidth(rows)
    batch, gated = select_batch(rows)

    if args.format == "su":
        print("%d %d" % (b["eligible"], b["pool_total"]))
        sys.exit(0)
    if args.format == "su-runs":
        # The SU row that matters is not "how many are eligible" but "is the lane DRAINING":
        # seeds carrying a completed, contract-valid, non-author falsifier run, out of seeds in
        # the lane. 0/N is UNKNOWN, never a pass -- an empty lane and a stalled lane must not
        # render the same, which is the failure `wiki.seeds` itself had before 2026-08-06.
        print("%d %d" % (b["seeds_with_valid_run"], len(rows)))
        sys.exit(0)
    if args.format == "json":
        print(json.dumps({"summary": b, "gated_by_ruling_1": gated,
                          "batch": [r["seed"] for r in batch],
                          "seeds": [dict((k, v) for k, v in r.items() if k != "runs") for r in rows],
                          "runs": runs}, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.promote:
        print(render_promotions(rows))
        sys.exit(0)

    as_of = args.as_of or "UNDATED"
    if args.batch or args.write_batch:
        page = render_batch(rows, batch, b, as_of)
        print(page)
        if args.write_batch:
            out = Path(args.write_batch)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page + "\n", encoding="utf-8")
            sys.stderr.write("\n[written] %s\n" % out)
        sys.exit(0)

    print(render_report(rows, b, batch, gated, runs))
    sys.exit(0)


if __name__ == "__main__":
    main()
