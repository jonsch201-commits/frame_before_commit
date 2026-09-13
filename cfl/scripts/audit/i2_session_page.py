#!/usr/bin/env python3
"""i2_session_page.py — the I2 half. Build ONE session source page from that session's I1 extracts.

WHAT THIS ANSWERS, AND WHY IT IS NOT WHAT THE TICKET LITERALLY ASKED FOR
------------------------------------------------------------------------
Ticket B-2, Jon verbatim: *"We could make a wiki master subagent resume any time a json closed to
update the wiki."*

The capture half he was reaching for **already exists and is finished**, further than the ticket row
said. Measured 2026-08-07:

  route_agent_return.py   CAPTURE   one ledger row per subagent return
  agent_end_ingest.py     I0 + I1   SubagentStop, extract_status: PROVISIONAL
  session_finalise.py     I0 + I1   SessionEnd, extract_status: FINAL   <- the fixed point
  -> 88 tracked `.i1.md` extracts under `wiki/intake-triage/agent-end/`, 3 session dirs holding
     extracts out of 5 dirs, 56 FINAL / 29 PROVISIONAL at the 12:09Z read.

And **every one of those scripts explicitly declines to do the next level.** Their own words:
`agent_end_ingest.py:35` *"It does NOT synthesize... Those are I2/I3"*; `main_thread_ingest.py:38`
same; `session_finalise.py:435` *"They are I1. INGEST/SKIP is I2/I3"*; `publication_screen.py:458`
same. `grep -rn "I2" scripts/` returns five files and **not one of them produces an I2 artifact.**

So the honest finding is: **the capture half is done; the missing half is I2 — synthesis.**
`wiki/references/update-levels-2026-07-31.md` (RATIFIED 2026-07-31) defines it exactly:

  | I2 page | source page: Key Claims, Conflicts, cross-links | bounded | session close | unattended |

Three columns of that row are load-bearing here and each contradicts part of the literal ticket:

* **cadence = session close**, NOT agent close. I0/I1 are the compact-boundary levels; I2 is not.
* **venue = unattended.** This licenses an automatic producer. It does not require an agent.
* **judgment = bounded.** Bounded means the rules are fixed and printed, which a script can be held
  to and an agent cannot.

WHY "RESUME A SUBAGENT ON EVERY JSON CLOSE" IS THE WRONG SHAPE — THREE MEASURED REASONS
---------------------------------------------------------------------------------------
1. **`SubagentStop` fires ~11x per agent** (measured 2026-08-06: eleven fires for one agent inside
   one minute). One dispatch per fire is eleven wiki-master runs per agent, over an extract that is
   PROVISIONAL by construction and will be superseded at `SessionEnd` anyway.

2. **A wiki-master subagent is itself a subagent, so its own close fires `SubagentStop`, which
   dispatches another wiki-master.** This is the repo's recorded no-fixed-point defect — *"routing a
   return is itself a return"*, 101 turns -> 135 — promoted one level up, where each iteration costs
   a model run instead of a ledger row. **The literal design does not terminate, and it does not
   fail loudly; it fails as spend.**

3. **A hook cannot dispatch an agent.** Hooks are shell commands. The only channel from a hook to
   the model is `hookSpecificOutput.additionalContext`, and at `SubagentStop` that text is injected
   into the ENDING agent's context — the spam that destroyed four agents' returns on 2026-08-06 and
   forced both hooks silent. Any design that reaches the model from this event re-opens that wound.

THE TERMINATION ARGUMENT — STATED EXPLICITLY, BECAUSE THE BRIEF REQUIRES ONE
----------------------------------------------------------------------------
Four independent reasons this cannot loop. Independent means removing any one leaves it terminating.

  T1. **THE PRODUCER IS A SCRIPT, NOT AN AGENT.** It emits no `SubagentStop`. The event that would
      re-trigger it is one it cannot cause. This is the whole reason the mechanical half is a script:
      not because a script is better at synthesis, but because a script has a fixed point and an
      agent does not.

  T2. **THE TRIGGER IS `SessionEnd`.** Verified against the hook behaviour already documented in
      `session_finalise.py`'s header rather than assumed: it fires when a session terminates, has NO
      decision control, its output is used for side effects only and is injected into nobody's
      context, and it cannot block (exit 2 shows stderr only). A session that has ended cannot end
      again.

  T3. **PROVENANCE SELF-EXCLUSION** — this is the leg that survives if the judgment half is ever
      handed to a real wiki-master subagent, which is the only version of B-2 that could loop.
      **Any I1 extract whose action ledger shows it wrote this page is excluded from this page's
      input set.** An agent that wrote the page cannot be an input to the page. So dispatching a
      wiki-master to enrich `I2-SESSION.md` produces an extract that is, by construction, not new
      input — the next run sees an unchanged input set and writes nothing. The fixed point is
      MECHANICAL, not a declaration to stop looking (which is what `ROUTING-LEDGER.md`'s `[TERMINAL]`
      token is, honestly labelled as such).

  T4. **CONTENT-STABLE WRITE.** `i2_content_sha256` hashes the page with its volatile timestamp
      lines removed. An identical re-run writes zero bytes, so a tracked file cannot churn and
      `SessionStart`'s `git pull --ff-only` cannot be broken by it. Same discipline, same reason, as
      `agent_end_ingest.stable_hash`.

  Residual, stated not glossed: T2 is a fixed point for a session that terminates THROUGH THE
  HARNESS. A process kill may not fire `SessionEnd` — UNKNOWN, unverified, the same residue
  `session_finalise.py` records about itself. The mitigation is the same: `--all` re-derives from
  disk at any time and is idempotent, so a missed event costs latency, never a record.

THE HAZARD THIS DESIGN INHERITS AND DOES NOT FIX
-------------------------------------------------
**A git merge writes files with no tool call**, so `PostToolUse` sees nothing and the ACTION LEDGER
in every I1 extract — which this page aggregates — cannot see it either. **This page therefore
undercounts disk change by exactly the amount any agent moved through `git merge`, `git checkout`,
`git restore`, `git stash` or a script it invoked.** That is inherited, not introduced, and it is
stated in the generated page itself rather than only here. Partial mitigation, and it is only
partial: the I1 ledger DOES capture `git commit` and `git push` command lines from Bash/PowerShell
calls, so a committed merge result leaves a trace even when the merge itself does not. An
uncommitted merge leaves none. **`distinct_paths_written` is a floor, never a total** — the page
says so in situ.

WHERE IT LANDS, AND THE FENCE THAT DECIDED IT
----------------------------------------------
  wiki/intake-triage/agent-end/<parent6>/I2-SESSION.md   TRACKED.

Not `wiki/sources/`. `skills/wiki-master/SKILL.md:18` — *"You are the only agent that writes to
`wiki/`. No other agent, role, or skill may write to any `wiki/` subdirectory."* `wiki/intake-triage/`
is the one `wiki/` path the ratified BGIsolation membrane already licenses for deposits by something
other than wiki-master, it is on `regenerate_canonical.sh`'s published list, and `agent_end_ingest.py`
already writes there under exactly this reasoning. **Promotion to `wiki/sources/` is named in the
page's own DISPOSITION section as wiki-master's call. That promotion is I3 and is not attempted
here** — the ratified table puts I3 in an interactive venue, and this script has no venue at all.

This is NOT the "pointer to gitignored content" defect Jon corrected on 2026-08-06. The page is
tracked, published, and carries the content itself. Jon: *"Sounds like more needs to get into the
wiki by default when agents end."* **Default means default.**

WHAT "BOUNDED JUDGMENT" MEANS HERE, PRECISELY
----------------------------------------------
Every selection rule is a FIXED PREDICATE, PRINTED INTO THE PAGE beside the count it produced.
Nothing is ranked. Nothing is dropped for being uninteresting. The page does not decide what
matters; it decides what is COMPARABLE — putting two mechanically-derived numbers side by side so a
reader can see a discrepancy that no single extract can show. **That is the one thing 88 separate
I1 files structurally cannot do, and it is the entire value added at I2.**

Usage:
  i2_session_page.py                       # hook mode: SessionEnd payload on stdin
  i2_session_page.py --session <uuid|6>    # build one session's page
  i2_session_page.py --all                 # every session dir holding extracts
  i2_session_page.py --all --dry-run       # report; writes nothing
  i2_session_page.py --self-test           # negative controls
"""
import hashlib
import io
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parents[2]
I1_ROOT = REPO / "wiki" / "intake-triage" / "agent-end"
PAGE_NAME = "I2-SESSION.md"

# The 2026-08-06 failure shape: a long confident return over zero writes. The threshold is
# `agent_end_ingest.SHORT_RETURN_CHARS`, restated here as a NAMED CONSTANT rather than a bare
# literal so a reader can see it is the same number and not a coincidence.
SHORT_RETURN_CHARS = 200

FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]\|]{1,120})(?:\|[^\]]*)?\]\]")
WIKIPATH_RE = re.compile(r"\b(wiki/[A-Za-z0-9_\-./]+\.md)\b")
PROMOTED = ("self-assessment", "seed", "brief-correction")

# The selection predicates, fixed and printed. Adding one changes future pages; it does not
# reinterpret past ones, because every page prints the list it was built with.
CONFLICT_RULES = [
    ("RETURN-WITHOUT-WRITES",
     "frontmatter `claim_vs_record: RETURN-WITHOUT-WRITES` — a return of at least "
     f"{SHORT_RETURN_CHARS} chars over zero written paths. **This is correct and expected for a "
     "read-only agent (Explore, cross-verifier, lint-checker, fable-mirror) AND it is the exact "
     "shape of the 2026-08-06 failure in which an agent returned a confident summary of work that "
     "did not exist on disk. The rule does not distinguish the two and does not try to.**"),
    ("SHORT-RETURN-OVER-WRITES",
     "frontmatter `claim_vs_record: SHORT-RETURN-OVER-WRITES` — real writes behind a return too "
     "short to describe them. The return is not a usable record of that agent's work; its ledger "
     "is."),
    ("PATH-COLLISION",
     "two or more agents in this session wrote the same repo-relative path. Derived by intersecting "
     "the `Paths written` bullet lists. **Not a defect by itself** — sequential agents on one file "
     "is normal — but it is the only mechanical signal of a lost update, and it is invisible from "
     "inside any single extract."),
    ("TURN-PARITY-MISMATCH",
     "frontmatter `turn_parity` reports sidecar and re-derived turn counts that disagree, so the "
     "`T{n}` anchors in that extract may not resolve against its transcript."),
    ("STILL-PROVISIONAL",
     "`extract_status: PROVISIONAL` on a session being written up at close. Its turn count is a "
     "floor and it may be missing the agent's own final return. **The page inherits this and marks "
     "itself PROVISIONAL rather than presenting a floor as a total.**"),
    ("JON-MIDTURN-PRESENT",
     "`jon_midturn_messages > 0` — Jon spoke into a running subagent. **The main thread does not "
     "see these** (8 messages to one agent on 2026-08-06, one surfaced; `exchange/CARRIER.md`). "
     "Every one is a candidate ruling that reached no coordinator."),
]


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if mm:
            out[mm.group(1)] = mm.group(2).strip()
    return out


def as_int(fm, key, default=0):
    try:
        return int(str(fm.get(key, default)).strip())
    except (TypeError, ValueError):
        return default


def section(text, num):
    """Body of `## {num}. ...` up to the next `## `. Empty string when absent."""
    m = re.search(rf"^##\s+{num}\.\s.*?$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


def first_fenced(body, lang="text"):
    m = re.search(rf"```{lang}\r?\n(.*?)```", body, re.DOTALL)
    return m.group(1).rstrip() if m else ""


def paths_written(text):
    body = section(text, 3)
    m = re.search(r"^###\s+Paths written.*?$(.*?)(?=^###\s|\Z)", body, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    return re.findall(r"^-\s+`([^`]+)`\s*$", m.group(1), re.MULTILINE)


def promoted_bullets(text, rule):
    body = section(text, 4)
    m = re.search(rf"^###\s+`{re.escape(rule)}`.*?$(.*?)(?=^###\s|^##\s|\Z)",
                  body, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    return [b.strip() for b in re.findall(r"^-\s+(\*\*T.*)$", m.group(1), re.MULTILINE)]


def jon_quotes(text):
    body = section(text, 1)
    return [b.strip() for b in re.findall(r"^-\s+(\*\*T.*)$", body, re.MULTILINE)]


def load_extract(path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    fm = read_frontmatter(text)
    if fm.get("extract_level") != "I1":
        return None
    ret = first_fenced(section(text, 2))
    return {
        "path": path,
        "rel": os.path.relpath(path, REPO).replace("\\", "/"),
        "fm": fm,
        "agent_id": fm.get("agent_id", "UNKNOWN"),
        "agent6": (fm.get("agent_id") or "UNKNOWN")[:6],
        "agent_type": fm.get("agent_type", "UNKNOWN"),
        "description": fm.get("agent_description", "UNKNOWN"),
        "status": fm.get("extract_status", "UNKNOWN"),
        "turns": as_int(fm, "turn_count"),
        "jon_n": as_int(fm, "jon_midturn_messages"),
        "ret_len": as_int(fm, "final_return_chars"),
        "cvr": fm.get("claim_vs_record", "none"),
        "parity": fm.get("turn_parity", "UNKNOWN"),
        "tool_calls": as_int(fm, "tool_calls"),
        "write_calls": as_int(fm, "write_calls"),
        "distinct": as_int(fm, "distinct_paths_written"),
        "commits": as_int(fm, "commit_commands"),
        "pushes": as_int(fm, "push_commands"),
        "self_n": as_int(fm, "self_assessments"),
        "seed_n": as_int(fm, "seeds"),
        "corr_n": as_int(fm, "brief_corrections"),
        "extracted": fm.get("extracted_utc", "UNKNOWN"),
        "return_text": ret,
        "paths": paths_written(text),
        # Section 3 verbatim — "what this agent did to disk". Carries both the `Paths written`
        # bullets and the captured `git commit`/`git push` command lines. This is the ONLY region
        # T3 is allowed to search; see `self_excluded()` for why the scope is not the whole body.
        "disk_section": section(text, 3),
        "promoted": {r: promoted_bullets(text, r) for r in PROMOTED},
        "jon": jon_quotes(text),
        "text": text,
    }


# --- T3: PROVENANCE SELF-EXCLUSION -------------------------------------------------------------
# The fixed point that survives handing the judgment half to a real subagent. An agent whose own
# action ledger shows it touched THIS page is not an input to THIS page.
#
# THE FIRST VERSION OF THIS FUNCTION WAS WRONG, AND ITS OWN AGENT'S EXTRACT CAUGHT IT
# -----------------------------------------------------------------------------------
# v1 tested `page_rel in ex["paths"]` — the `Paths written` bullets — and nothing else. Those
# bullets are built from `Write|Edit|MultiEdit|NotebookEdit` tool calls ONLY. **This page is
# generated by RUNNING THIS SCRIPT, which is a `Bash` call, so the producing agent writes the page
# with no write-tool call and the bullets never name it.**
#
# Measured 2026-08-07, on the extract of the very agent that built this file: paths written were
# `.claude/settings.json`, `scripts/audit/i2_session_page.py`,
# `wiki/intake-triage/i2-design-note-2026-08-07.md` — and NOT `I2-SESSION.md`. `self_excluded()`
# returned **False** for the page's own author, so it was carried as an input to its own output.
# **T3 did not hold.**
#
# This is the SAME class as the git-merge hazard this file documents for path counts — *a write
# that happens without a tool call is invisible to the action ledger* — and the header called that
# out for the counts while missing that it also undermined the termination argument itself. A
# hazard named in one place and not followed to its other consequence is this repo's characteristic
# defect, and it recurred here inside the very function written to prevent a loop.
#
# THE FIX, AND WHY IT IS SCOPED THE WAY IT IS
# -------------------------------------------
# The `git commit`/`git push` command lines ARE captured in the action ledger, and an agent that
# generates this page commits it — `git add .../I2-SESSION.md` appears verbatim. So provenance is
# the UNION of two mechanical traces, both of them inside section 3:
#
#   (a) the `Paths written` bullets      — the page was written by a write tool
#   (b) the captured git command lines   — the page was staged/committed by this agent
#
# **Scope is section 3 ONLY — "what this agent did to disk" — never the whole extract body.**
# Testing the whole body would exclude any agent that merely *mentions* the page in its return or
# reasoning, silently dropping legitimate inputs. Precision matters in both directions here: a
# too-narrow test loops, a too-broad test swallows. The negative control in `self_test()` pins
# exactly this — an extract that names the page only in prose is NOT excluded.
def self_excluded(ex, page_rel):
    if page_rel in ex["paths"]:
        return True
    return page_rel in ex.get("disk_section", "")


def collect(parent6, page_rel):
    d = I1_ROOT / parent6
    kept, excluded = [], []
    for p in sorted(d.glob("*.i1.md")):
        ex = load_extract(p)
        if ex is None:
            excluded.append((p.name, "not an I1 extract (missing or wrong `extract_level`)"))
            continue
        if self_excluded(ex, page_rel):
            excluded.append((p.name, f"PROVENANCE SELF-EXCLUSION — this agent wrote `{page_rel}`"))
            continue
        kept.append(ex)
    kept.sort(key=lambda e: (e["extracted"], e["agent6"]))
    return kept, excluded


def find_conflicts(exs):
    hits = {name: [] for name, _ in CONFLICT_RULES}
    for e in exs:
        if e["cvr"] == "RETURN-WITHOUT-WRITES":
            hits["RETURN-WITHOUT-WRITES"].append(
                (e, f"{e['ret_len']:,} chars returned, 0 paths written"))
        if e["cvr"] == "SHORT-RETURN-OVER-WRITES":
            hits["SHORT-RETURN-OVER-WRITES"].append(
                (e, f"{e['ret_len']} chars returned, {e['distinct']} path(s) written"))
        if "MISMATCH" in e["parity"]:
            hits["TURN-PARITY-MISMATCH"].append((e, e["parity"]))
        if e["status"] != "FINAL":
            hits["STILL-PROVISIONAL"].append((e, f"extract_status: {e['status']}"))
        if e["jon_n"] > 0:
            hits["JON-MIDTURN-PRESENT"].append((e, f"{e['jon_n']} message(s)"))
    owners = {}
    for e in exs:
        for p in e["paths"]:
            owners.setdefault(p, []).append(e)
    for p, es in sorted(owners.items()):
        if len(es) > 1:
            hits["PATH-COLLISION"].append(
                (es[0], f"`{p}` — {len(es)} agents: " + ", ".join(x["agent6"] for x in es)))
    return hits


def cross_links(exs):
    """(resolved, unresolved, slugs). Only links found in EXTRACT BODIES, never invented."""
    paths, slugs = {}, {}
    for e in exs:
        body = e["text"]
        for m in WIKIPATH_RE.finditer(body):
            paths.setdefault(m.group(1), set()).add(e["agent6"])
        for m in WIKILINK_RE.finditer(body):
            slugs.setdefault(m.group(1).strip(), set()).add(e["agent6"])
    resolved, unresolved = [], []
    for p, who in sorted(paths.items()):
        (resolved if (REPO / p).exists() else unresolved).append((p, sorted(who)))
    return resolved, unresolved, sorted((s, sorted(w)) for s, w in slugs.items())


VOLATILE_RE = re.compile(r"^(?:generated_utc|i2_content_sha256):.*\r?\n", re.MULTILINE)


def stable_hash(text):
    return hashlib.sha256(VOLATILE_RE.sub("", text).encode("utf-8")).hexdigest()


def render(parent6, exs, excluded, page_rel):
    hits = find_conflicts(exs)
    resolved, unresolved, slugs = cross_links(exs)
    n = len(exs)
    final_n = sum(1 for e in exs if e["status"] == "FINAL")
    prov_n = n - final_n
    stage = "FINAL" if (n and prov_n == 0) else "PROVISIONAL"
    dates = sorted({e["extracted"][:10] for e in exs if e["extracted"] != "UNKNOWN"})
    jon_total = sum(e["jon_n"] for e in exs)
    all_paths = sorted({p for e in exs for p in e["paths"]})
    conflict_total = sum(len(v) for v in hits.values())

    b = io.StringIO()
    w = b.write
    w("---\n")
    w(f'title: "I2 session page — {parent6} ({n} agents)"\n')
    w("source_kind: session-page\n")
    w(f"retrieval_key: i2-session-{parent6}\n")
    w("tags: I2, session-page, agent-end, synthesis, record-architecture, "
      + ", ".join(sorted({e["agent_type"] for e in exs})) + "\n")
    w("extract_level: I2\n")
    w("judgment_applied: bounded — fixed predicates, printed in situ, nothing ranked\n")
    w("coverage_class: untraced-by-design\n")
    w("coverage_class_reason: derived wholly from the I1 extracts it enumerates; every figure is a "
      "count over a stated denominator and it makes no independent citable claim\n")
    w(f"parent_session6: {parent6}\n")
    w(f"agents: {n}\n")
    w(f"extracts_final: {final_n}\n")
    w(f"extracts_provisional: {prov_n}\n")
    w(f"extracts_excluded: {len(excluded)}\n")
    w(f"page_status: {stage}\n")
    w(f"conflicts: {conflict_total}\n")
    w(f"jon_midturn_total: {jon_total}\n")
    w(f"distinct_paths_written: {len(all_paths)}\n")
    w(f"self_assessments: {sum(e['self_n'] for e in exs)}\n")
    w(f"seeds: {sum(e['seed_n'] for e in exs)}\n")
    w(f"brief_corrections: {sum(e['corr_n'] for e in exs)}\n")
    w(f"crosslinks_resolved: {len(resolved)}\n")
    w(f"crosslinks_unresolved: {len(unresolved)}\n")
    w(f"date_range: {(dates[0] + '..' + dates[-1]) if dates else 'UNKNOWN'}\n")
    w(f"generated_utc: {now_utc()}\n")
    w("produced_by: scripts/audit/i2_session_page.py (SessionEnd, automatic)\n")
    w("---\n\n")

    w(f"# I2 session page — {parent6}\n\n")

    if stage == "FINAL":
        w("> **FINAL.** Every I1 extract behind this page carries `extract_status: FINAL`, meaning "
          "each was rebuilt at `SessionEnd` when its subagent could no longer be resumed. The "
          "counts below are totals, not floors.\n\n")
    else:
        w(f"> **PROVISIONAL — {prov_n} of {n} input extract(s) are themselves PROVISIONAL.** A "
          "PROVISIONAL extract was written at a `SubagentStop` fire, and `SubagentStop` has no "
          "fixed point: routing a return is itself a return. Its turn count is a floor and it may "
          "be missing its agent's final return. **This page inherits that and reports a floor "
          "rather than presenting one as a total.** Re-run after `session_finalise.py` has stamped "
          "the inputs FINAL and this banner changes.\n\n")

    w("**This is an I2 page.** Per `wiki/references/update-levels-2026-07-31.md` (RATIFIED "
      "2026-07-31): *I2 page — source page: Key Claims, Conflicts, cross-links | bounded judgment | "
      "session close | unattended.* All three qualifiers are honoured literally. **Bounded** means "
      "every selection rule below is a fixed predicate printed beside the count it produced. "
      "**Nothing is ranked, nothing is dropped for being uninteresting, and no INGEST/SKIP call is "
      "made** — that is I3, it requires an interactive venue, and this script has no venue at "
      "all.\n\n")

    # --- 1. DENOMINATOR --------------------------------------------------------------------
    w("## 1. Denominator and basis\n\n")
    w(f"- **{n} I1 extract(s)** read from `wiki/intake-triage/agent-end/{parent6}/*.i1.md` — "
      f"**{final_n} FINAL, {prov_n} PROVISIONAL**.\n")
    w(f"- **{len(excluded)} file(s) excluded**, each with its reason, listed below. Excluded is not "
      f"the same as absent and is never silent.\n")
    w(f"- Date range of extraction: **{(dates[0] + ' .. ' + dates[-1]) if dates else 'UNKNOWN'}**.\n")
    w(f"- **{len(all_paths)} distinct repo path(s)** written across all agents, and **that is a "
      f"FLOOR.**\n\n")
    w("> **THE INHERITED HAZARD, STATED WHERE IT BITES.** The path counts on this page come from "
      "the I1 ACTION LEDGERS, which read `tool_use` blocks out of each subagent JSONL. **A `git "
      "merge`, `checkout`, `restore` or `stash` writes files with no tool call**, so neither "
      "`PostToolUse` nor any I1 ledger nor this page can see it. This gap is identified and "
      "unfixed; it is inherited here, not introduced. Partial mitigation, and it is only partial: "
      "the ledgers do capture `git commit`/`git push` command lines, so a **committed** merge "
      "result leaves a trace. An **uncommitted** one leaves none.\n\n")
    if excluded:
        w("| excluded file | reason |\n|---|---|\n")
        for name, why in excluded:
            w(f"| `{name}` | {why} |\n")
        w("\n")

    # --- 2. KEY CLAIMS ---------------------------------------------------------------------
    w("## 2. Key claims\n\n")
    w("**Rule (fixed):** one row per agent. The claim column is that agent's own final return, "
      "verbatim, first 300 characters. **A return is a claim; the ledger columns beside it are the "
      "record.** They are placed adjacent deliberately so neither has to be trusted alone — the "
      "2026-08-06 failure was a long confident return over zero writes, and nothing in the record "
      "put those two facts side by side.\n\n")
    w("| agent6 | type | turns | return chars | write calls | paths | commits | flag |\n")
    w("|---|---|---:|---:|---:|---:|---:|---|\n")
    for e in exs:
        w(f"| [`{e['agent6']}`]({Path(e['rel']).name}) | {e['agent_type']} | {e['turns']} | "
          f"{e['ret_len']:,} | {e['write_calls']} | {e['distinct']} | {e['commits']} | "
          f"{e['cvr'] if e['cvr'] != 'none' else ''} |\n")
    w("\n")
    for e in exs:
        w(f"### `{e['agent6']}` — {e['agent_type']} — {e['description']}\n\n")
        w(f"Extract: [`{Path(e['rel']).name}`]({Path(e['rel']).name}) · status **{e['status']}** · "
          f"{e['turns']} turns · {e['tool_calls']} tool calls\n\n")
        rt = (e["return_text"] or "").strip()
        if rt:
            snippet = rt[:300].replace("\n", " ").strip()
            w(f"> {snippet}{'…' if len(rt) > 300 else ''}\n\n")
        else:
            w("> _No final return captured in this extract._ **Absence here is absence of a "
              "captured return, not evidence the agent said nothing** — a PROVISIONAL extract can "
              "stop short of the agent's last turn.\n\n")
        for rule in PROMOTED:
            items = e["promoted"][rule]
            if items:
                w(f"**`{rule}` — {len(items)} line(s):**\n\n")
                for it in items:
                    w(f"- {it}\n")
                w("\n")
        if e["paths"]:
            w(f"**Wrote {len(e['paths'])} path(s):** "
              + ", ".join(f"`{p}`" for p in e["paths"][:12])
              + (f" … (+{len(e['paths']) - 12} more)" if len(e["paths"]) > 12 else "") + "\n\n")

    # --- 3. CONFLICTS ----------------------------------------------------------------------
    w("## 3. Conflicts\n\n")
    w("**Every rule is a fixed predicate over I1 frontmatter or ledger bullets, printed here beside "
      "its count. A hit is a thing worth LOOKING AT, never a verdict.** This section is the whole "
      "reason I2 exists as a level: each predicate compares extracts to each other or to the "
      "session, and **no single I1 file can evaluate any of them about itself.**\n\n")
    w(f"**{conflict_total} hit(s) across {len(CONFLICT_RULES)} rules, over {n} extract(s).**\n\n")
    for name, desc in CONFLICT_RULES:
        rows = hits[name]
        w(f"### `{name}` — {len(rows)} hit(s)\n\n")
        w(f"*Rule:* {desc}\n\n")
        if not rows:
            w("_No hit._ **Absence here is absence of a MATCH against a fixed printed predicate, "
              "not absence of the thing.**\n\n")
            continue
        for e, detail in rows:
            w(f"- **`{e['agent6']}`** ({e['agent_type']}) — {detail} — "
              f"[`{Path(e['rel']).name}`]({Path(e['rel']).name})\n")
        w("\n")

    # --- 4. CROSS-LINKS --------------------------------------------------------------------
    w("## 4. Cross-links\n\n")
    w("**Rule (fixed):** every `wiki/**.md` path and every `[[slug]]` literally present in an "
      "extract body, resolved against this working tree. **Nothing is inferred and no link is "
      "invented.** An unresolved path is reported as unresolved, never quietly dropped — a link "
      "that does not resolve is the cheapest possible detection of a half-landed move, which is a "
      "recorded failure class here (a path migration silently disabled three instruments, one of "
      "them a blocking gate).\n\n")
    w(f"- **{len(resolved)} resolved**, **{len(unresolved)} unresolved**, "
      f"**{len(slugs)} distinct `[[slug]]` reference(s)**.\n\n")
    if unresolved:
        w("### Unresolved — these paths appear in an extract and are NOT in this working tree\n\n")
        for p, who in unresolved:
            w(f"- `{p}` — cited by {', '.join('`' + x + '`' for x in who)}\n")
        w("\n")
    if resolved:
        w(f"### Resolved — {len(resolved)} path(s)\n\n")
        for p, who in resolved[:80]:
            w(f"- `{p}` — cited by {', '.join('`' + x + '`' for x in who)}\n")
        if len(resolved) > 80:
            w(f"\n_…and {len(resolved) - 80} more; the frontmatter count is the total._\n")
        w("\n")
    if slugs:
        w("### `[[slug]]` references\n\n")
        for s, who in slugs[:60]:
            w(f"- `[[{s}]]` — cited by {', '.join('`' + x + '`' for x in who)}\n")
        w("\n")

    # --- 5. DISPOSITION --------------------------------------------------------------------
    w("## 5. Disposition — what is owed, and to whom\n\n")
    w("**This section is a QUEUE, not a decision.** `SU = CAPTURE + I0 + I1 + I2 + DISPOSITION` "
      "(RATIFIED 2026-07-31). Everything below is I3 or I4 and belongs to an interactive venue.\n\n")
    owed = []
    if prov_n:
        owed.append(f"**Re-run after finalisation** — {prov_n} of {n} inputs are PROVISIONAL, so "
                    f"this page is a floor. `python scripts/audit/session_finalise.py --session "
                    f"{parent6}` then re-run this script.")
    if jon_total:
        owed.append(f"**{jon_total} mid-turn message(s) from Jon** are quoted in section 1 of the "
                    f"listed extracts. **The main thread does not see these.** Each is a candidate "
                    f"ruling that may never have reached a coordinator — the highest-value item on "
                    f"this page, and the only one with a recorded history of being lost.")
    sa = sum(e["self_n"] for e in exs)
    sd = sum(e["seed_n"] for e in exs)
    bc = sum(e["corr_n"] for e in exs)
    if sd:
        owed.append(f"**{sd} `seed` line(s)** — candidates for "
                    f"`wiki/intake-triage/SEED-REGISTER-2026-08-03.md`. Registration is a "
                    f"Jon-facing act, not this script's.")
    if bc:
        owed.append(f"**{bc} `brief-correction` line(s)** — an agent correcting its dispatcher. "
                    f"This is the only signal here that runs AGAINST the authority gradient, and on "
                    f"2026-08-06 it carried four coordinator errors that the coordinator found none "
                    f"of itself.")
    if sa:
        owed.append(f"**{sa} `self-assessment` line(s)** — where each agent said it was weakest. "
                    f"Standing guard rule: **a falsifier may not be judged by its author.**")
    if unresolved:
        owed.append(f"**{len(unresolved)} unresolved cross-link(s)** — each is either a typo, a "
                    f"half-landed move, or a file that was never written. All three are worth one "
                    f"`find_answer.py` query before anything is called absent.")
    if hits["PATH-COLLISION"]:
        owed.append(f"**{len(hits['PATH-COLLISION'])} path collision(s)** — two agents on one file. "
                    f"Check for a lost update.")
    owed.append("**Promotion of this page to `wiki/sources/` is wiki-master's call, not this "
                "script's.** `skills/wiki-master/SKILL.md:18` reserves every `wiki/` subdirectory "
                "to wiki-master; `wiki/intake-triage/` is the licensed deposit path and is where "
                "this page therefore lands.")
    for i, o in enumerate(owed, 1):
        w(f"{i}. {o}\n")
    w("\n")

    # --- 6. NEGATIVE SPACE -----------------------------------------------------------------
    w("## 6. What this page does NOT claim\n\n")
    w("- **Not that anything here is important.** No ranking was applied. Importance is I3.\n")
    w("- **Not that the path counts are complete.** They are a floor — see the merge hazard in "
      "§1.\n")
    w("- **Not that a conflict hit is a defect.** Every rule fires on shapes that are routinely "
      "innocent; the value is that the comparison is visible, not that it is adjudicated.\n")
    w("- **Not that a rule's silence means the thing is absent.** Each rule is a fixed printed "
      "pattern; a real instance phrased outside it is simply not matched.\n")
    w("- **Not a substitute for reading the extracts.** Every row links to its source.\n")
    w("- **Not a Jon Gate, not a ratification, and not an INGEST/SKIP decision.**\n\n")
    w("---\n\n_Generated by `scripts/audit/i2_session_page.py`. The termination argument T1–T4 is "
      "in that file's header and is the reason this is a script rather than the subagent that "
      "ticket B-2 literally asked for._\n")

    return b.getvalue(), stage, conflict_total


def write_page(parent6, dry_run=False):
    page_rel = f"wiki/intake-triage/agent-end/{parent6}/{PAGE_NAME}"
    exs, excluded = collect(parent6, page_rel)
    if not exs:
        return {"session": parent6, "action": "skip", "reason": "no I1 extracts", "n": 0}
    text, stage, conflicts = render(parent6, exs, excluded, page_rel)
    h = stable_hash(text)
    text = text.replace("generated_utc:", f"i2_content_sha256: {h}\ngenerated_utc:", 1)
    out = REPO / page_rel
    if out.exists():
        prev = out.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^i2_content_sha256:\s*([0-9a-f]{64})\s*$", prev, re.MULTILINE)
        if m and m.group(1) == h:
            return {"session": parent6, "action": "unchanged", "n": len(exs),
                    "stage": stage, "conflicts": conflicts}
    if dry_run:
        return {"session": parent6, "action": "would-write", "n": len(exs),
                "stage": stage, "conflicts": conflicts, "bytes": len(text)}
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, out)
    return {"session": parent6, "action": "wrote", "n": len(exs), "stage": stage,
            "conflicts": conflicts, "bytes": len(text), "excluded": len(excluded)}


def sessions_on_disk():
    if not I1_ROOT.is_dir():
        return []
    return sorted(d.name for d in I1_ROOT.iterdir()
                  if d.is_dir() and any(d.glob("*.i1.md")))


# ---------------------------------------------------------------------------------------------
# NEGATIVE CONTROLS. A test that only proves the happy path proves that the code ran.
# ---------------------------------------------------------------------------------------------
def self_test():
    ok = True

    def chk(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}{(' — ' + note) if note else ''}")
        ok = ok and bool(cond)

    print("=== i2_session_page.py self-test ===\n")

    print("A. Frontmatter + section parsing")
    doc = ("---\ntitle: \"x\"\nextract_level: I1\nagent_id: abcdef123\n"
           "turn_count: 7\nclaim_vs_record: RETURN-WITHOUT-WRITES\n---\n\n"
           "## 2. The agent's final return (verbatim)\n\n```text\nhello\n```\n\n"
           "## 3. What this agent did to disk\n\n### Paths written — 1 distinct, 1 shown\n\n"
           "- `wiki/a.md`\n\n## 4. Self-assessment\n\n### `seed` — 1 matched, 1 shown\n\n"
           "- **T4 (A)** (line 9) — a falsifier\n")
    fm = read_frontmatter(doc)
    chk("frontmatter parsed", fm.get("extract_level") == "I1")
    chk("final return lifted from the fence", first_fenced(section(doc, 2)) == "hello")
    chk("paths written parsed", paths_written(doc) == ["wiki/a.md"])
    chk("promoted bullet parsed", len(promoted_bullets(doc, "seed")) == 1)
    chk("NEGATIVE: absent rule yields [] not a crash",
        promoted_bullets(doc, "brief-correction") == [])
    chk("NEGATIVE: absent section yields ''", section(doc, 9) == "")
    chk("NEGATIVE: no frontmatter yields {}", read_frontmatter("no fm here") == {})
    chk("NEGATIVE: non-numeric int field falls back",
        as_int({"turn_count": "UNKNOWN"}, "turn_count", -1) == -1)

    print("\nB. T3 — PROVENANCE SELF-EXCLUSION (the fixed point)")
    page_rel = "wiki/intake-triage/agent-end/aaaaaa/I2-SESSION.md"
    writer = {"paths": [page_rel, "wiki/other.md"], "disk_section": ""}
    other = {"paths": ["wiki/other.md"], "disk_section": ""}
    chk("an agent that wrote the page by TOOL CALL is excluded", self_excluded(writer, page_rel))
    chk("NEGATIVE: an agent that did not touch it is NOT excluded",
        not self_excluded(other, page_rel))
    chk("NEGATIVE: exclusion is exact-path, not substring — a SIBLING path does not exclude",
        not self_excluded({"paths": ["wiki/intake-triage/agent-end/aaaaaa/I2-SESSION.md.bak"],
                           "disk_section": ""}, page_rel))
    # THE REGRESSION THAT T3 v1 MISSED, PINNED. This page is produced by RUNNING THIS SCRIPT — a
    # Bash call — so the producing agent has NO write-tool call naming the page. v1 tested only the
    # `Paths written` bullets and therefore carried the page's own author as an input to its own
    # output. Measured live on agent aaf142, 2026-08-07.
    generator = {"paths": [".claude/settings.json", "scripts/audit/i2_session_page.py"],
                 "disk_section": ("### Paths written — 2 distinct\n\n- `x`\n\n"
                                  "### Commits — 1 `git commit`\n\n```text\n"
                                  f"git add {page_rel}\n```\n")}
    chk("REGRESSION: an agent that GENERATED the page via script + git add IS excluded",
        self_excluded(generator, page_rel),
        "T3 v1 returned False here and the loop was open")
    # And the other direction: scope is section 3 only. An agent that merely TALKS about the page
    # in its return must remain an input, or a too-broad fix silently swallows legitimate work.
    talker = {"paths": ["wiki/other.md"],
              "disk_section": "### Paths written — 1 distinct\n\n- `wiki/other.md`\n"}
    chk("NEGATIVE: an agent that only MENTIONS the page in prose is NOT excluded",
        not self_excluded(talker, page_rel),
        "too-broad exclusion silently drops real inputs")

    print("\nC. T4 — content-stable hash")
    a = ("---\nx: 1\ni2_content_sha256: " + "0" * 64
         + "\ngenerated_utc: 2026-01-01T00:00:00Z\n---\nbody\n")
    bb = ("---\nx: 1\ni2_content_sha256: " + "f" * 64
          + "\ngenerated_utc: 2026-09-09T09:09:09Z\n---\nbody\n")
    c = ("---\nx: 2\ni2_content_sha256: " + "0" * 64
         + "\ngenerated_utc: 2026-01-01T00:00:00Z\n---\nbody\n")
    chk("timestamp-only difference hashes EQUAL", stable_hash(a) == stable_hash(bb))
    chk("NEGATIVE: a real content difference hashes DIFFERENT", stable_hash(a) != stable_hash(c))

    print("\nD. Conflict predicates")

    def mk(**kw):
        d = {"agent6": "aaaaaa", "agent_type": "t", "cvr": "none", "parity": "MATCH",
             "status": "FINAL", "jon_n": 0, "ret_len": 0, "distinct": 0, "paths": [],
             "rel": "x.i1.md"}
        d.update(kw)
        return d

    h = find_conflicts([mk(cvr="RETURN-WITHOUT-WRITES"), mk(status="PROVISIONAL"),
                        mk(jon_n=3), mk(parity="sidecar=5 rederived=7 MISMATCH")])
    chk("RETURN-WITHOUT-WRITES fires", len(h["RETURN-WITHOUT-WRITES"]) == 1)
    chk("STILL-PROVISIONAL fires", len(h["STILL-PROVISIONAL"]) == 1)
    chk("JON-MIDTURN-PRESENT fires", len(h["JON-MIDTURN-PRESENT"]) == 1)
    chk("TURN-PARITY-MISMATCH fires", len(h["TURN-PARITY-MISMATCH"]) == 1)
    chk("NEGATIVE: a clean set fires NOTHING",
        sum(len(v) for v in find_conflicts([mk(), mk()]).values()) == 0)
    coll = find_conflicts([mk(agent6="a1", paths=["wiki/z.md"]),
                           mk(agent6="a2", paths=["wiki/z.md"])])
    chk("PATH-COLLISION fires on a shared path", len(coll["PATH-COLLISION"]) == 1)
    chk("NEGATIVE: distinct paths do NOT collide",
        len(find_conflicts([mk(agent6="a1", paths=["wiki/p.md"]),
                            mk(agent6="a2", paths=["wiki/q.md"])])["PATH-COLLISION"]) == 0)

    print("\nE. NEGATIVE: an empty session writes nothing")
    r = write_page("__nonexistent_session__", dry_run=True)
    chk("no extracts -> skip, no write", r["action"] == "skip")

    print(f"\n=== {'ALL PASS' if ok else 'FAILURES PRESENT'} ===")
    return 0 if ok else 1


def main(argv):
    args = list(argv[1:])
    if "--self-test" in args:
        return self_test()
    dry = "--dry-run" in args
    explicit = False
    if "--all" in args:
        targets = sessions_on_disk()
        explicit = True
    elif "--session" in args:
        v = args[args.index("--session") + 1]
        targets = [v[:6]]
        explicit = True
    else:
        # Hook mode: SessionEnd payload on stdin. SILENT ON NO-OP, exit 0 on every path — the
        # discipline every hook-facing script in this repo follows, and for the recorded reason
        # that a blocking row whose steady state is "firing" gets ignored.
        payload = {}
        try:
            raw = sys.stdin.read() if not sys.stdin.isatty() else ""
            if raw.strip():
                payload = json.loads(raw)
        except Exception:
            payload = {}
        sid = str(payload.get("session_id") or "")
        targets = [sid[:6]] if sid else sessions_on_disk()
    results = []
    for t in targets:
        try:
            results.append(write_page(t, dry_run=dry))
        except Exception as e:
            results.append({"session": t, "action": "error",
                            "reason": f"{type(e).__name__}: {e}"})
    noisy = [r for r in results if r["action"] in ("wrote", "would-write", "error")]
    if noisy or explicit:
        for r in results:
            if r["action"] == "skip" and not explicit:
                continue
            line = f"[i2] {r['session']}: {r['action']}"
            if "n" in r and r["action"] != "skip":
                line += (f" — {r['n']} extract(s), {r.get('stage')}, "
                         f"{r.get('conflicts')} conflict hit(s)")
            if r.get("reason"):
                line += f" — {r['reason']}"
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
