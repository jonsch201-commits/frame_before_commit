#!/usr/bin/env python3
"""main_thread_ingest.py — run I1 on THE MAIN CONVERSATION, which had no I1 layer at all.

THE ROOT BREAK THIS CLOSES — MEASURED, NOT INFERRED
----------------------------------------------------
`scripts/audit/agent_end_ingest.py:407-415` (`resolve_from_jsonl`) returns `None` for any
transcript that is not `agent-*.jsonl` under a `subagents/` directory:

    if not jsonl.name.startswith("agent-") or jsonl.suffix != ".jsonl":
        return None, f"not a subagent transcript filename: {jsonl.name}"
    ...
    if jsonl.parents[0].name != "subagents":
        return None, f"not under a subagents/ directory: {jsonl}"

That guard is CORRECT for what it guards — a `SubagentStop` payload carries the MAIN
conversation's `transcript_path`, and extracting the parent under a child's name would be worse
than extracting nothing. But its consequence was never noticed: **the whole I1 layer covers
subagents only.**

So on 2026-08-06 the main conversation of session `f01909` had a 1.8 MB transcript markdown on
disk (`raw/transcripts/claude-code/code-2026-08-06-f01909-consult-fable-mirror-and-review-wiki-
updates.md`, gitignored) and **no `.i1.md` anywhere in the repo**, while 65 of its subagents each
had one, tracked, in `wiki/`. The asymmetry is exactly backwards from the value: **the main
conversation is the ONLY place Jon's own typed words exist.** Everything the agent-end layer
carefully preserves — verbatim quotes, turn anchors, an action ledger — was being preserved for
the agents and not for him.

WHAT THIS DOES
--------------
* **I0** — ensures the main transcript markdown exists, by delegating to the SAME canonical
  extractor path the rest of the corpus uses (`extract_claude_code_sessions.convert_one` ->
  `skills/chat-exporter/scripts/convert-claude-code.py`). It writes no transcript markdown itself.
  Two parsers of one artifact is the divergence defect this repo spent a week removing.
* **I1** — a mechanical extract whose FIRST and largest section is **every one of Jon's turns,
  verbatim, with turn anchors**, followed by his mid-turn messages into this session's subagents,
  a marker table under the same fixed printed vocabulary `agent_end_ingest.py` uses, and the
  derived action ledger. No ranking, no selection on merit, no summary.
* **It does NOT synthesize.** No concept page, no INGEST/SKIP call, no promotion. Those are I2/I3
  and remain wiki-master's in an interactive session. `skills/handoff/SKILL.md`: *"this skill
  records. Wiki-master synthesizes. Recording is not gated on merit; synthesis is."*
* **It never blocks.** Exit 0 on every path, including its own internal errors.
* **It is silent on a no-op.** Nothing is printed when there is nothing to do. Anything this
  writes to stdout inside a hook becomes `additionalContext` injected into a live agent's window;
  on 2026-08-06 that spam destroyed four agents' returns.

WHY A SEPARATE FILE RATHER THAN A BRANCH INSIDE agent_end_ingest.py
--------------------------------------------------------------------
`agent_end_ingest.py` was under active edit by another agent at the time this was written (tag
and path fixes in flight, file mtime 5 minutes old). Racing a 2,499-line file mid-change to add a
branch is how half-landed migrations happen here — see the recorded case where a half-applied path
move silently disabled three instruments including a blocking gate. So **every shared rule is
IMPORTED from it** (`collect_markers`, `disk_actions`, `claim_vs_record`, `line_turn_mapper`,
`stable_hash`, `repo_rel`, `tags_line`, the marker vocabulary, the stage constants) and nothing is
restated. If the two are later merged, this file contributes a resolver and a body writer; it
contributes no duplicated rule.

WHERE IT LANDS
--------------
  I0 anchor  -> raw/transcripts/claude-code/[<project>/]<stem>.md  (+ .sidecar.md)
                GITIGNORED bulk corpus — the standing `raw/` design, unchanged.
  I1 extract -> wiki/intake-triage/main-thread/<uuid6>/<stem>.i1.md
                **TRACKED**, per Jon 2026-08-06: *"Sounds like more needs to get into the wiki by
                default when agents end."* and *"I'm not worried about anything sensitive landing
                in CFL. You don't need stronger fences."*

`main-thread/` is a SIBLING of `agent-end/`, deliberately: `agent_end_ingest.build_index()` globs
`I1_ROOT.glob("*/*.i1.md")` where `I1_ROOT` is `wiki/intake-triage/agent-end`, so a main-thread
extract dropped into that tree would be parsed by an index expecting subagent frontmatter. A
sibling directory is outside that glob by construction rather than by care.

PROVISIONAL vs FINAL — SAME MODEL, SHARPER PROBLEM
---------------------------------------------------
A subagent transcript stops growing when the agent stops. **A main conversation transcript grows
until the session ends, and the session is running while this script reads it.** So every extract
this script writes from a live session is a floor, and it says so in the artifact. `--final` is the
`SessionEnd` entry point. There is no version of this that is final and also written mid-session,
and pretending otherwise is the defect `extract_status` exists to prevent.

Usage:
  main_thread_ingest.py                       # every CFL session with a transcript, PROVISIONAL
  main_thread_ingest.py --session f01909      # one session (uuid substring)
  main_thread_ingest.py --jsonl PATH          # one session jsonl explicitly
  main_thread_ingest.py --session X --final   # stamp terminal (SessionEnd's entry point)
  main_thread_ingest.py --force               # ignore the content-stable skip
  main_thread_ingest.py --verbose             # print even when nothing changed
  main_thread_ingest.py --self-test           # negative controls
"""
import argparse
import io
import json
import os
import sys
import traceback
from datetime import datetime, timezone
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

# --- REUSE, NOT REIMPLEMENTATION -------------------------------------------------------------
import extract_claude_code_sessions as X                    # noqa: E402  canonical extractor
import turn_index                                           # noqa: E402  canonical turn indexer
import agent_end_ingest as AEI                              # noqa: E402  every shared I1 rule
import jon_utterances as JU                                 # noqa: E402  the denominator

# ⛔ X.ROOT IS THE **CORPUS** ROOT AND IS PINNED TO THE G: CLONE ON PURPOSE (the gitignored
# bulk transcript corpus lives there). I1 extracts are TRACKED WIKI PAGES, not corpus, so keying
# them off X.ROOT wrote every one of them into a stale clone sitting on branch
# feat/post-pr2-open-2026-08-29 -- where they are never committed on the live branch and are
# invisible to every census run from the working tree. `[measured 2026-09-04 19:3x: main-thread/
# held 6 i1 pages on G: and 5 on N:; today's only new page landed on G: alone.]`
# ⭐ THE FIX IS NOT NEW. agent_end_ingest.py:172 -- THIS SCRIPT'S OWN SIBLING, which this file
# imports as AEI -- made exactly this correction on 2026-09-03 with the same measurement
# ("35 on G: vs 2 on N: for session 71ce5a"), and it was never propagated to the other two call
# sites. Recorded, correct, and not on the acting path.
# ⛔ THE FALLBACK USED TO BE `or X.ROOT`, AND X.ROOT IS A HARDCODED ABSOLUTE PATH TO THE
# G: CLONE (extract_claude_code_sessions.py:69). So a hand run with CLAUDE_PROJECT_DIR unset
# wrote TRACKED FILES INTO A STALE CHECKOUT ON ANOTHER BRANCH, silently and successfully.
# [measured 2026-09-04 22:4x: the G: tree's uncommitted count GREW 3,140 -> 3,462 -> 3,491
# across twenty minutes while nobody was editing it -- Professional's restart gate R1.]
# ⭐ DERIVE THE CHECKOUT FROM THIS FILE, never from a recorded path: parents[2] of
# scripts/audit/<this>.py IS the repo that contains the code being run, in EVERY clone, and
# it cannot name a tree the caller is not in. (derive-don't-record, the trunk's own named
# characteristic failure.) X.ROOT remains correct where it is used as the CORPUS root.
_CHECKOUT = Path(__file__).resolve().parents[2]
REPO = Path(os.environ.get("CLAUDE_PROJECT_DIR") or _CHECKOUT)
I1_ROOT = REPO / "wiki" / "intake-triage" / "main-thread"
STATE_DIR = AEI.STATE_DIR

# --- STRUCK 2026-08-15 (SG-5, wiki/references/struck-gates.md) --------------------------------
# JON_QUOTE_CAP = 6000        # per-utterance; truncation is ANNOUNCED, never silent
#
# This cut JON'S OWN UTTERANCES at 6,000 characters in the tracked record. The "see remainder
# at…" pointer resolved to `AEI.repo_rel(md)` — the GITIGNORED bulk-corpus transcript, outside
# tracked space — so the stored copy of his own words was, by construction, incomplete: the
# remainder pointer never resolved to anything the tracked record itself carries. The value 6,000
# was never chosen deliberately and was never tested against a real boundary.
#
# Struck, not replaced: MR-13, from the 11,901 case — "strike the claim … do NOT re-cut, do NOT
# adopt 6,874." No new cap, no configurable default.
#
#   "Ground truth is ensuring nothing is deleted by accident or lost by accident." — 2026-08-03
#   "All must be recoverable, keep json." — 2026-08-09

# The class selector for these extracts. Deliberately NOT `agent_end_ingest.MECHANISM_TAGS` —
# that tuple contains `subagent`, which is the one thing a main-thread extract is defined as not
# being. `jon-verbatim` is the tag that matters: it selects every file in the repo that carries
# Jon's own words as primary content, which before 2026-08-06 was an empty set.
MECHANISM_TAGS = ("main-thread", "jon-verbatim", "I1", "capture", "record-architecture")


# ---------------------------------------------------------------------------------------------
# Resolution — the mirror image of agent_end_ingest.resolve_from_jsonl()
# ---------------------------------------------------------------------------------------------
def resolve_main(jsonl):
    """(target dict, reason) for one TOP-LEVEL session jsonl.

    The predicate is the exact complement of the one that excluded main all along: a session
    transcript is a `*.jsonl` sitting DIRECTLY in a project directory, not under `subagents/`.
    Stated as a complement on purpose — if the two predicates ever both reject a file, the file is
    visible in neither layer, which is the condition this script exists to end.
    """
    jsonl = Path(jsonl)
    if not jsonl.is_file():
        return None, f"not a file: {jsonl}"
    if jsonl.suffix != ".jsonl":
        return None, f"not a jsonl: {jsonl.name}"
    if jsonl.parent.name == "subagents":
        return None, "subagent transcript — agent_end_ingest.py owns this one"
    uuid = jsonl.stem
    if len(uuid) < 6:
        return None, f"session id too short to anchor: {uuid}"
    st = jsonl.stat()
    return {
        "jsonl": jsonl,
        "uuid": uuid,
        "uuid6": uuid[:6],
        "project": X.project_for_dir(jsonl.parent.name),
        "size": st.st_size,
        "mtime": int(st.st_mtime),
    }, ""


def iter_cfl_sessions(only=None):
    """Top-level session JSONLs, deduped by uuid, as the canonical extractor enumerates them."""
    for _proj, jf in X.iter_session_jsonls():
        if only and only not in jf.stem:
            continue
        yield jf


# ---------------------------------------------------------------------------------------------
# I0 — anchor
# ---------------------------------------------------------------------------------------------
def run_i0(t, refresh=None):
    """(ok, info). Delegates conversion to the canonical extractor; writes no markdown itself.

    `refresh=None` means AUTO: re-extract when the JSONL is newer than the markdown, which for a
    live session it always is. The refresh goes through `hold_refresh`/`restore_refresh` — the
    fail-safe path — because the plain path is `unlink -> convert -> report failure`, and a
    converter failure after the unlink leaves NO extract at all in a GITIGNORED tree, which git
    cannot give back.
    """
    mds = X.existing_mds(t["uuid6"])
    if refresh is None:
        refresh = bool(mds) and any(t["mtime"] > int(p.stat().st_mtime) for p in mds)
    if mds and not refresh:
        md = mds[0]
    else:
        if X.session_is_empty(t["jsonl"]):
            # EMPTY is not FAILED. Nine sessions in this corpus hold zero conversational
            # records; calling them failures is the cry-wolf shape the extractor already
            # documents at session_is_empty().
            return False, {"error": "session holds no turns (EMPTY, not failed)", "empty": True}
        _msgs, title = X.quick_meta(t["jsonl"])
        backup = X.hold_refresh(mds) if mds else []
        ok, out = X.convert_one(t["jsonl"], t["project"], force=bool(mds),
                                slug=(title or None), domain_subfolder=not mds)
        if not ok:
            X.restore_refresh(backup)
            tail = (out or "").strip().splitlines()
            return False, {"error": tail[-1][:200] if tail else "converter failed, no output"}
        mds = X.existing_mds(t["uuid6"])
        if not mds:
            X.restore_refresh(backup)
            return False, {"error": "converter reported success but no extract is on disk"}
        md = mds[0]

    sidecar = X.sidecar_for(md)
    idx = turn_index.index(str(md))
    parity = X._turn_parity(t["jsonl"], sidecar) if sidecar.exists() else None
    return True, {
        "md": md, "sidecar": sidecar if sidecar.exists() else None,
        "md_turns": idx["turn_count"], "header_style": idx["header_style"],
        "turns": idx["turns"], "parity": parity, "refreshed": refresh,
    }


# ---------------------------------------------------------------------------------------------
# I1 — extract
# ---------------------------------------------------------------------------------------------
def build_i1(t, i0, stage=AEI.STAGE_PROVISIONAL):
    """(path, wrote_bool, counts). Content-stable: an identical re-fire writes nothing."""
    md, turns = i0["md"], i0["turns"]
    which = AEI.line_turn_mapper(turns)

    enum = JU.enumerate_session(t["jsonl"], i0["sidecar"])
    utts = enum["utterances"]
    counts = enum["class_counts"]
    anchored = sum(1 for u in utts if u["turn"])

    hits, totals = AEI.collect_markers(md, which)
    acts = AEI.disk_actions(t["jsonl"])

    _msgs, title = X.quick_meta(t["jsonl"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out_dir = I1_ROOT / t["uuid6"]
    out_path = out_dir / (md.name[:-3] + ".i1.md")

    b = io.StringIO()
    w = b.write
    w("---\n")
    w(f"title: \"I1 extract — MAIN THREAD {t['uuid6']} ({title or 'untitled'})\"\n")
    w("source_kind: extract\n")
    w(f"retrieval_key: main-thread-i1-{t['uuid6']}\n")
    # Mechanism tags select the class; subject tags discriminate inside it — the same split as
    # agent_end_ingest, and the SAME derivation function for the subject half, so the two cannot
    # drift. The mechanism half is NOT reused: `AEI.tags_line()` hardcodes `subagent`, and tagging
    # a main-thread extract `subagent` would put it in the one bucket it is defined as not being.
    # A tag that is false is worse than a tag that is missing, because it answers a query wrongly.
    # Deduped: derive_subject_tags() seeds its seen-set from AEI's mechanism tuple, not this
    # one, so `main-thread` would otherwise appear twice — a duplicated tag is a small lie about
    # how many times a subject was mentioned.
    _seen, _tags = set(), []
    for _tk in list(MECHANISM_TAGS) + AEI.derive_subject_tags("main-thread", title or ""):
        if _tk not in _seen:
            _seen.add(_tk)
            _tags.append(_tk)
    w("tags: " + ", ".join(_tags) + "\n")
    w("coverage_class: untraced-by-design\n")
    w("coverage_class_reason: mechanical I1 extract written automatically from the main session "
      "transcript; it makes no citable claim of its own and is excluded from citation-coverage "
      "measurement\n")
    w(f"source_id: {t['uuid']}\n")
    w("extract_level: I1\n")
    w("extract_kind: mechanical-jon-turns-quotes-markers\n")
    w("judgment_applied: none\n")
    w(f"companion_of: {md.name}\n")
    w(f"transcript_path: {AEI.repo_rel(md)}\n")
    w(f"sidecar_path: {AEI.repo_rel(i0['sidecar']) if i0['sidecar'] else 'ABSENT'}\n")
    w(f"jsonl_path: {AEI.repo_rel(t['jsonl'])}\n")
    w(f"session_uuid: {t['uuid']}\n")
    w(f"project: {t['project']}\n")
    w(f"turn_count: {i0['md_turns']}\n")
    w(f"turn_parity: {('sidecar=%d rederived=%d %s' % (i0['parity'][0], i0['parity'][1], 'MATCH' if i0['parity'][0] == i0['parity'][1] else 'MISMATCH')) if i0['parity'] else 'UNKNOWN — not derivable'}\n")
    w(f"header_style: {i0['header_style']}\n")
    # THE FIELDS THAT MAKE THIS FILE'S WHOLE POINT READABLE WITHOUT OPENING IT.
    w(f"jon_utterances: {len(utts)}\n")
    w(f"jon_turns_main: {counts.get('typed', 0) + counts.get('slash-args', 0)}\n")
    w(f"jon_midturn_messages: {counts.get('midturn', 0)}\n")
    w(f"jon_utterances_anchored: {anchored}\n")
    w(f"jon_utterance_chars: {sum(u['chars'] for u in utts)}\n")
    w(f"user_record_ledger: {json.dumps(counts)}\n")
    w(f"marker_totals: {json.dumps(totals)}\n")
    w(f"self_assessments: {totals.get('self-assessment', 0)}\n")
    w(f"seeds: {totals.get('seed', 0)}\n")
    w(f"brief_corrections: {totals.get('brief-correction', 0)}\n")
    w(f"tool_calls: {acts['tool_calls']}\n")
    w(f"write_calls: {acts['write_calls']}\n")
    w(f"distinct_paths_written: {acts['distinct_count']}\n")
    w(f"commit_commands: {len(acts['commits'])}\n")
    w(f"push_commands: {len(acts['pushes'])}\n")
    w(f"extract_status: {stage}\n")
    w(f"jsonl_size: {t['size']}\n")
    w(f"jsonl_mtime: {t['mtime']}\n")
    w(f"extracted_utc: {now}\n")
    w(f"finalised_utc: {now if stage == AEI.STAGE_FINAL else '-'}\n")
    w("produced_by: scripts/audit/main_thread_ingest.py\n")
    w("---\n\n")

    w(f"# I1 extract — MAIN THREAD {t['uuid']} ({title or 'untitled'})\n\n")

    if stage == AEI.STAGE_FINAL:
        w("> **FINAL — this extract is terminal.** It was rebuilt after the session ended, so the "
          "transcript behind it cannot grow further. Cite it without checking for a newer one.\n\n")
    else:
        w("> **PROVISIONAL — mid-session snapshot, not the final extract.** A subagent transcript "
          "stops growing when the agent stops. **A main conversation transcript grows until the "
          "session ends, and this was written while the session was still running.** So the turn "
          "count and every count below are FLOORS, not totals, and Jon may have said things after "
          "the last utterance listed here. The terminal version is written at `SessionEnd` with "
          "`extract_status: FINAL`.\n\n")

    w("**This is an I1 extract, not a page.** Per `wiki/references/update-levels-2026-07-31.md` "
      "(RATIFIED 2026-07-31), I1 produces *claims/decisions/quotes with turn anchors, no view on "
      "importance*. Nothing here has been selected on merit, ranked, summarized, or reconciled "
      "against any other page. Turning any of it into a concept page is I2/I3 — wiki-master's "
      "call in an interactive session, not this script's.\n\n")

    w("**Why this file exists at all.** Until 2026-08-06 the I1 layer covered **subagents only**: "
      "`agent_end_ingest.resolve_from_jsonl()` returns `None` for any transcript not under a "
      "`subagents/` directory. So 65 agent transcripts from this session had tracked extracts in "
      "`wiki/` and the main conversation — **the only place Jon's own words exist** — had none. "
      "That asymmetry is exactly backwards from the value.\n\n")

    # --- 1. JON, VERBATIM ---------------------------------------------------------------------
    w("## 1. Jon's own words — every utterance, verbatim\n\n")
    w(f"**{len(utts)} utterance(s).** This is the DENOMINATOR for Jon's standard — *\"Every word "
      f"I've ever said should likely impact at least one concept, or have it's negative citation "
      f"explained\"* — and before `scripts/audit/jon_utterances.py` it did not exist anywhere in "
      f"this repo. Enumeration is that module's; the classification rules and their exclusions are "
      f"printed in the ledger below rather than trusted.\n\n")
    w(f"Split: **{counts.get('typed', 0)} typed**, **{counts.get('slash-args', 0)} slash-command "
      f"argument(s)** (the text Jon typed after `/skill` — his words, not a harness token), "
      f"**{counts.get('midturn', 0)} mid-turn message(s)** sent into running subagents. "
      f"{anchored} of {len(utts)} carry a `T{{n}}` anchor.\n\n")
    if anchored < len(utts):
        w(f"**{len(utts) - anchored} utterance(s) are UNANCHORED, and that is itself a finding.** "
          f"An utterance is anchored by joining its record `uuid` to the per-turn sidecar. A "
          f"main-thread utterance with no anchor means the sidecar does not yet carry that turn — "
          f"i.e. **the corpus extract is older than the live JSONL**. Mid-turn messages are "
          f"unanchored by construction: they live in a child transcript and have no row in this "
          f"session's sidecar at all.\n\n")
    w("**Ordering note:** anchors join on `uuid`, never on timestamp. Timestamps in these files "
      "are not monotonic — on this corpus T1 has been observed stamped 171 ms *after* T2 — so a "
      "timestamp join mis-anchors silently.\n\n")

    if not utts:
        w("_No utterance found._ **Absence here is not evidence Jon was silent.** It is evidence "
          "that no record in this JSONL matched the counted classes; check the ledger below for "
          "where the records went.\n\n")
    for u in utts:
        anchor = f"T{u['turn']} ({u['role']})" if u["turn"] else f"UNANCHORED ({u['venue']})"
        extra = ""
        if u["cls"] == "midturn":
            extra = " — delivered to agent(s) " + ", ".join(
                f"`{a}`" for a in u.get("delivered_to", []))
        w(f"### J{u['n']} — {anchor} — `{u['cls']}` — `{u['timestamp']}`{extra}\n\n")
        body = u["text"]
        # STRUCK 2026-08-15 (SG-5): JON_QUOTE_CAP is gone. Jon's own words are written in full,
        # always — see the struck constant above for why a cap here was never safe: its pointer
        # resolved outside the tracked record.
        w("```text\n" + body.replace("```", "`​``") + "\n```\n\n")

    # --- 2. The ledger of what was NOT counted ------------------------------------------------
    w("## 2. Record ledger — what was counted, and what was set aside\n\n")
    w("`type: user` is a wildly overloaded record class in a Claude Code JSONL. **Every record is "
      "classified into exactly one class and every class is reported, including the excluded "
      "ones.** A denominator whose exclusions are invisible is the same defect as a gate that "
      "passes by resolving nothing.\n\n")
    w("| class | records | counted as an utterance? |\n|---|---:|---|\n")
    for cls in JU.LEDGER_CLASSES:
        w(f"| `{cls}` | {counts.get(cls, 0)} | "
          f"{'**yes**' if cls in JU.COUNTED_CLASSES else 'no'} |\n")
    w(f"\n**Denominator:** {sum(counts.values())} `type: user` record(s) read from "
      f"`{t['jsonl'].name}` plus this session's `subagents/` tree; "
      f"{len(utts)} are Jon speaking. Mid-turn raw hits before de-duplication: "
      f"{enum['midturn_raw']} ({enum['midturn_dupes']} duplicate deliveries — one message sent "
      f"while three agents are running lands three times on disk and is **one** thing Jon "
      f"said).\n\n")
    if enum["excluded_samples"]:
        w("One sample per excluded class, so the labels can be checked rather than believed:\n\n")
        for cls, sample in enum["excluded_samples"]:
            w(f"- `{cls}` — {sample}\n")
        w("\n")

    # --- 3. Action ledger ----------------------------------------------------------------------
    w("## 3. What this session did to disk (derived, mechanical)\n\n")
    w("Derived from the session's own `tool_use` blocks, never from what it said it did. "
      "**Scope: the MAIN transcript only** — work done inside subagents is in their own extracts "
      "under `wiki/intake-triage/agent-end/`, and this file makes no claim about it.\n\n")
    w("| tool | calls |\n|---|---|\n")
    for name in sorted(acts["tools"], key=lambda k: (-acts["tools"][k], k)):
        w(f"| {name} | {acts['tools'][name]} |\n")
    if not acts["tools"]:
        w("| _none recorded_ | 0 |\n")
    w(f"\n**Denominator:** {acts['tool_calls']} `tool_use` block(s); {acts['write_calls']} were "
      f"write calls touching **{acts['distinct_count']} distinct path(s)**; "
      f"{len(acts['commits'])} `git commit` and {len(acts['pushes'])} `git push` invocation(s).\n\n")
    for p in acts["distinct_paths"][:AEI.ACTION_CAP]:
        w(f"- `{p}`\n")
    if acts["distinct_count"] > AEI.ACTION_CAP:
        w(f"\n**{acts['distinct_count'] - AEI.ACTION_CAP} further path(s) not shown** — the true "
          f"count is {acts['distinct_count']}, printed rather than left to be inferred from the "
          f"length of the list.\n")
    w("\n")

    # --- 4. Markers ----------------------------------------------------------------------------
    w("## 4. Marker matches (fixed printed vocabulary)\n\n")
    w("Rules are `agent_end_ingest.MARKER_RULES`, imported so the two layers cannot drift. Lines "
      "inside fenced code blocks and headings are excluded. **The TRUE count is printed even where "
      f"the shown list is capped at {AEI.MARKER_CAP_PER_RULE}** — a shown count silently equal to "
      f"a cap is a lying denominator.\n\n")
    w("| rule | pattern | matched | shown |\n|---|---|---|---|\n")
    for name, rx in AEI.MARKER_RULES:
        w(f"| {name} | `{rx.pattern}` | {totals[name]} | {len(hits[name])} |\n")
    w("\n")
    for name, _ in AEI.MARKER_RULES:
        if not hits[name]:
            continue
        w(f"### rule `{name}` — {totals[name]} matched, {len(hits[name])} shown\n\n")
        for anchor, lineno, text in hits[name]:
            w(f"- **{anchor}** (line {lineno}) — {text}\n")
        w("\n")

    w("## What this extract does NOT claim\n\n")
    w("- **Not that any of this reached a concept page.** That is measured separately by "
      "`scripts/audit/check_jon_word_coverage.py`, and on its first run the answer was mostly no.\n"
      "- **Not that the utterance list is complete for the session.** While `extract_status` is "
      "`PROVISIONAL` the session is still running and the list is a floor.\n"
      "- **Not that an unmatched marker rule means the thing is absent.** It means no line matched "
      "a fixed printed pattern.\n"
      "- **Not a judgment of importance.** Nothing here was ranked. That is I2/I3.\n")

    doc = b.getvalue()
    # Content-stable write, the same mechanism agent_end_ingest uses and for the same reason: this
    # is a TRACKED path, `SubagentStop`/`SessionEnd` are not once-per-session events, and a tracked
    # file that changes on every fire shows permanently `M`, which makes `SessionStart`'s
    # `git pull --ff-only` ABORT. Strip the volatile stamps, compare the hash, write nothing when
    # the content is identical.
    sha = AEI.stable_hash(doc)
    doc = doc.replace(f"extracted_utc: {now}\n",
                      f"extracted_utc: {now}\ni1_content_sha256: {sha}\n", 1)
    info = {"utterances": len(utts), "anchored": anchored, "counts": counts, "sha": sha}
    if out_path.exists() and AEI.existing_stable_hash(out_path) == sha:
        return out_path, False, info

    # NON-DOWNGRADE GUARD, keyed on BYTES rather than on the label. A provisional fire must not
    # relabel a terminal artifact as mid-flight for no reason — but if the JSONL has GROWN since
    # finalisation, the finality claim stopped being true, and the honest act is to demote and
    # re-extract rather than protect the label with silence.
    if stage == AEI.STAGE_PROVISIONAL and out_path.exists():
        if AEI.read_i1_field(out_path, "extract_status") == AEI.STAGE_FINAL:
            if (AEI.read_i1_field(out_path, "jsonl_size") == str(t["size"])
                    and AEI.read_i1_field(out_path, "jsonl_mtime") == str(t["mtime"])):
                info["kept_final"] = True
                return out_path, False, info
            info["demoted_from_final"] = True

    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(doc, encoding="utf-8")
    os.replace(tmp, out_path)
    return out_path, True, info


# ---------------------------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------------------------
def ingest_one(jsonl, stage, force, verbose):
    """(status, message). Never raises."""
    try:
        t, why = resolve_main(jsonl)
        if not t:
            return "skip", why
        ok, i0 = run_i0(t)
        if not ok:
            return ("empty" if i0.get("empty") else "error"), i0.get("error", "unknown")
        path, wrote, c = build_i1(t, i0, stage=stage)
        rel = AEI.repo_rel(path)
        if not wrote and not force:
            return "unchanged", f"{rel} ({c['utterances']} utterances)"
        if not wrote and force:
            # --force means rewrite even when content-stable. Touch the stamp by rewriting.
            path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        return "wrote", (f"{rel} — {c['utterances']} Jon utterance(s), "
                         f"{c['anchored']} anchored, {i0['md_turns']} turns")
    except Exception:
        return "error", traceback.format_exc(limit=3).strip().splitlines()[-1][:200]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jsonl", help="one session transcript explicitly")
    ap.add_argument("--session", help="session uuid substring")
    ap.add_argument("--final", action="store_true", help="stamp the extract terminal")
    ap.add_argument("--force", action="store_true", help="rewrite even when content-stable")
    ap.add_argument("--verbose", action="store_true", help="print unchanged/skipped too")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    stage = AEI.STAGE_FINAL if args.final else AEI.STAGE_PROVISIONAL
    targets = [Path(args.jsonl)] if args.jsonl else list(iter_cfl_sessions(args.session))

    results = []
    for jf in targets:
        status, msg = ingest_one(jf, stage, args.force, args.verbose)
        results.append((status, jf, msg))

    wrote = [r for r in results if r[0] == "wrote"]
    errs = [r for r in results if r[0] == "error"]
    # SILENT ON A NO-OP. Anything printed here becomes additionalContext inside a live agent.
    if wrote or errs or args.verbose:
        print(f"=== MAIN-THREAD I1 — {len(targets)} session(s) considered, "
              f"{len(wrote)} written, {len(errs)} error(s) ===")
        for status, jf, msg in results:
            if status in ("wrote", "error") or args.verbose:
                print(f"  {status:<10} {jf.name[:12]}  {msg}")
    return 0


def self_test():
    """Negative controls. The instrument must be able to reject as well as accept."""
    import tempfile
    ok = True
    print("=== SELF-TEST — main_thread_ingest ===")

    # 1. A SUBAGENT transcript must be REJECTED here. If both resolvers accepted it the file
    #    would get two extracts under two names; if both rejected it, it would be invisible.
    with tempfile.TemporaryDirectory() as d:
        sub = Path(d) / "proj" / "uuid-1234567890" / "subagents"
        sub.mkdir(parents=True)
        f = sub / "agent-abcdef123.jsonl"
        f.write_text("{}\n", encoding="utf-8")
        t, why = resolve_main(f)
        good = t is None and "subagent" in why
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  subagent transcript rejected by the main resolver")

        # 2. A TOP-LEVEL session must be ACCEPTED. This is the complement, and it is the exact
        #    case agent_end_ingest.resolve_from_jsonl() rejects — the root break being closed.
        top = Path(d) / "proj" / "f0190965-96ce-4e41-996f-c2b8585272b2.jsonl"
        top.write_text("{}\n", encoding="utf-8")
        t2, why2 = resolve_main(top)
        good2 = t2 is not None and t2["uuid6"] == "f01909"
        ok = ok and good2
        print(f"  {'PASS' if good2 else 'FAIL'}  top-level session accepted (uuid6 derived)")

        # 3. THE COMPLEMENT PROPERTY ITSELF. agent_end_ingest rejects exactly what this accepts.
        a_t, a_why = AEI.resolve_from_jsonl(top)
        good3 = a_t is None
        ok = ok and good3
        print(f"  {'PASS' if good3 else 'FAIL'}  agent_end_ingest still rejects it "
              f"(the gap this closes: {a_why[:48]!r})")

    # 4. Content stability: the stable hash must ignore the timestamp line and NOTHING else.
    a = "extracted_utc: 2026-01-01T00:00:00Z\njon_utterances: 45\n"
    b = "extracted_utc: 2099-12-31T23:59:59Z\njon_utterances: 45\n"
    c = "extracted_utc: 2026-01-01T00:00:00Z\njon_utterances: 46\n"
    good4 = AEI.stable_hash(a) == AEI.stable_hash(b) and AEI.stable_hash(a) != AEI.stable_hash(c)
    ok = ok and good4
    print(f"  {'PASS' if good4 else 'FAIL'}  stable hash ignores the stamp, not the counts")

    # 5. The landing path must be OUTSIDE agent_end_ingest's index glob, or a main-thread
    #    extract would be parsed by an index expecting subagent frontmatter.
    good5 = AEI.I1_ROOT.resolve() != I1_ROOT.resolve() and \
        AEI.I1_ROOT.resolve() not in I1_ROOT.resolve().parents
    ok = ok and good5
    print(f"  {'PASS' if good5 else 'FAIL'}  landing path is a sibling of agent-end/, not inside")

    print("\nRESULT: " + ("PASS — resolver, hash and path guards all hold."
                          if ok else "FAIL — do not wire this."))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        # NEVER BLOCKS. A hook-wired script that can exit non-zero is a hook that can wedge a
        # session, and this repo already has blocking rows whose steady state is "firing".
        sys.exit(0)
