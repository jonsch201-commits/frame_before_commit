---
title: "Subagent transcripts — the render horizon closed for this trunk's 127 subagent JSONLs, and what the isMeta class turned out to hold"
kind: reference
date: 2026-09-12
session: 682d274b (Professional, N:, wikiskills pass 3 lane)
measured_at: "2026-09-12 14:44–14:49 CDT"
measured_by: "scratchpad/pop.py and scratchpad/meta.py (one Python pass over */subagents/agent-*.jsonl under the three keys from scripts/project_dirs.py); scripts/render-subagents.py (receipt lines verbatim below); find/grep over raw/transcripts/claude-code-subagents"
charter: "Jon 2026-09-12 14:4x, verbatim: \"Bring your graph to now through your raw logs, prove it, THEN launch wikiskills on what is critical.\" Acceptance test, Jon verbatim: \"a named page carrying a claim and a receipt, or a skill document whose diff can be read.\""
status: RENDERED 127/127 in this pass; the class was measured and is NOT what the universal row says it is in this trunk — see §2 bound
queried:
  - query: "render subagent JSONL isMeta Jon mid-turn messages"  (scripts/graphrag.sh, hybrid, index 26,398 chunks, freshness=STALE built 2026-09-12T19:33:21Z — stale is true and stated)
    top3:
      - wiki/references/jon-direct-input-json-census-2026-09-05.md:72-75  (Subagents (the A grade): 165 files / 403 turns fleet-wide, 1 rendered, 0 indexed)
      - exchange/inbound/RECEIPT-2026-09-06-antigravity-JON-DIRECT-INPUT-ISMETA-CENSUS-2026-09-06.md:10-23
      - exchange/inbound/RECEIPT-2026-09-06-antigravity-JON-DIRECT-INPUT-ISMETA-CENSUS-2026-09-06.md:24-28
  - query: "render-sessions.sh how a jsonl becomes a markdown transcript"  (same index, same STALE flag)
    top3:
      - exchange/inbound/LETTER-2026-09-01-antigravity-to-fleet-REPLY-JON-ORDER-SESSIONSTART.md:44-55  (names CFL's convert-claude-code.py as the canonical engine)
      - exchange/outbox/pro-to-secretary-2026-09-04-CPC-5-…-R4-CLOSED-here-project-key-derived-in-all-7-scripts-with-selftests.md:35-37
      - skills/session-identity/SKILL.md:11-18
  note: "neither query surfaced scripts/render-sessions.sh itself or the converter's own subagent docstring (convert-claude-code.py:43-59, 300-330, 618+); those were reached by reading the files (rung 4). The retriever knew the GAP (census page) and the ENGINE's name (Antigravity letter); it did not know the engine already handles subagents."
---

## 1. The claim

**What is lost:** every `*/subagents/agent-*.jsonl` under this trunk's project keys — the delegated agents' full transcripts, including every `type: user` turn injected mid-run (`isMeta: true`) — had no markdown render, so no graphrag index, no retriever, and no wiki page could see them. The universal `~/.claude/CLAUDE.md` names the class in its venue table: *"`~/.claude/projects/**/subagents/agent-*.jsonl` — `type: user` + `isMeta: true` — messages he sends mid-turn to a subagent — never appear in any main transcript."*

**For whom:** any reader of this trunk's markdown layer — the wiki, the graphrag index (`scripts/graphrag.sh`), the identity pages (`scripts/session_identity.py --subagents` writes identity rows, not transcripts), and any sibling searching this tree for a Jon primary.

**Since when:** since the first subagent under these keys. `[m]` oldest subagent JSONL rendered here is dated 2026-08-07 (parent `2d58af67`); `render-sessions.sh` was written 2026-09-01 and its glob is `<key>/*.jsonl` — main sessions only. `[m 14:44]` before this pass: `raw/transcripts/claude-code-subagents/` did not exist; 0 md.

**Why CRITICAL by Jon's definition (something being lost NOW), not merely salient:** the population grows with every dispatch — `[m]` the coordinator counted 124 files at 14:3x and this lane counted 127 at 14:44, so three subagent transcripts were created in the ten minutes between the two counts, none of them reachable by any markdown instrument until this pass.

## 2. The measured population `[m 14:44–14:45, scratchpad/pop.py + meta.py]`

Printed before counting, as the brief required:

```
POP key=N--claude-professional files=16 isMeta_user_turns=3 files_with_isMeta=3
POP key=G--My-Drive-Claude-Claude-Professional-claude-professional files=111 isMeta_user_turns=34 files_with_isMeta=17
POP key=N--claude-professional--claude-worktrees-prof-n3c0-pr4-frame files=0 isMeta_user_turns=0 files_with_isMeta=0
POP TOTAL files=127 isMeta_user_turns=37 files_with_isMeta=20 largest=4292288B …\G--My-Drive-…\2d58af67-1029-40ad-b338-01e34215e1e3\subagents\agent-a8a905a8496415f4a.jsonl
line types: {'user': 4218, 'attachment': 1208, 'assistant': 7246, 'fork-context-ref': 8}
```

**What the 37 `isMeta: true` user turns open with** `[m 14:45, meta.py, every turn printed and read]`:

| opening text | turns |
|---|---|
| `[SYSTEM NOTIFICATION - NOT USER INPUT]` (background-task events) | 23 |
| `[Image: original …` (screenshot payloads to one agent, parent `2d58af67`) | 5 |
| `The coordinator sent a message while you were working:` | 8 |
| `Another Claude session sent a message while you were working:` | 1 |
| **Jon-typed** | **0** |

⛔ **The bound this changes:** in THIS trunk, the class the universal row calls *"messages he sends mid-turn to a subagent"* contains **zero** Jon-typed turns of 37. The 09-05 census already graded the class *"Jon-possible … MIXED CLASS … Counted, not asserted"* (`wiki/references/jon-direct-input-json-census-2026-09-05.md` §1), and this is the first per-turn read that measures the mix for one trunk. The universal row's primaries are Personal and CFL subagent JSONLs (`a69f311e-…/subagents/agent-a53635545de2a684d.jsonl:87`, `9e21da9b-…/subagents/agent-ad4f469d3bbc886f3.jsonl:165`) — those were not re-read here and this page says nothing about them. **Read the text before quoting any isMeta turn as his**; the renderer's marker is a class label and says so on every appendix.

The 8 coordinator relays DO carry Jon's words second-hand — e.g. parent `e8f94111`, 2026-09-02T17:41:57Z: *"ROUND TWO. Jon's order was "discuss…"* — which is exactly the *"coordinator quoting it, not Jon saying it"* case the universal file already names. They are now rendered and searchable, graded as relay.

## 3. The receipt — this pass `[m]`

| | before (14:47) | after (14:49) |
|---|---|---|
| `raw/transcripts/claude-code-subagents/` | did not exist | 10 parent-sid8 dirs |
| transcripts (`*.md`, non-sidecar) | 0 | **127** |
| sidecars (`*.sidecar.md`, per-turn provenance, converter's) | 0 | 127 |
| bytes | 0 | 20,777,072 |
| `### JON MID-TURN (isMeta) #n` headings | 0 | **37** (= the 37 turns counted independently above) |
| files whose text contains the marker | 0 | 21 = 20 appendices + 1 body mention (this lane's own dispatch brief quotes the marker string) |

Renderer output, verbatim (`scratchpad/render-run1.log`):

```
RENDER-SUBAGENTS: scanned=127 rendered=127 skipped=0 failed=0  isMeta_user_turns=37  out=N:\claude-professional\raw\transcripts\claude-code-subagents
  EFFECT PROVEN: newest md mtime advanced 0 -> 1789242529
```

Second run 14:49, idempotence: `scanned=127 rendered=1 skipped=126 failed=0` — the 1 is this lane's own live subagent JSONL (`682d274b/…/agent-ae56a39b03807f940.jsonl`), which grew between runs; a live file re-rendering while it is written is correct behaviour, not a defect.

Selftest (`python scripts/render-subagents.py --selftest`), last 3 lines verbatim:

```
SELFTEST fixture-without-isMeta: PASS (status=rendered, marker absent=True)
SELFTEST idempotent-by-mtime: PASS (second pass: skipped, skipped)
SELFTEST: PASS -- 3 checks, converter=N:\claude-cfl\clone\skills\chat-exporter\scripts\convert-claude-code.py
```

## 4. How it was built, and the rule it kept

`scripts/render-sessions.sh` line 11–15: *"WE DO NOT OWN A RENDERER AND WE DO NOT WRITE ONE. CFL's chat-exporter is the fleet converter … It NEVER falls back to a hand-rolled renderer."* The brief asked for a from-scratch renderer; the trunk rule is older and Jon-anchored, so `scripts/render-subagents.py` **drives the fleet converter** (`convert-claude-code.py --run … --out … --force --project pro`) once per subagent JSONL. `[m]` the converter already detects subagent records by shape (`isSidechain: true` + `agentId`, its lines 300–330) and writes `session_kind: subagent`, `parent_session`, `agent_models`, `agent_type` frontmatter — it has since 2026-07-25 (its docstring, line 43). Nothing in this tree called it on the subagent population.

What the converter does not do `[m grep -n isMeta convert-claude-code.py → 0 hits]`: distinguish `isMeta` user turns from the orchestrator's opening brief — both render as `## Dispatch`. So the script appends, after the converter's output, a `## Mid-turn user turns (isMeta: true)` section with every such turn verbatim (timestamp + full text), each headed `### JON MID-TURN (isMeta) #n`, plus the qualifier that the label is a class, not an attribution.

**Deviation from the brief, stated:** output names are the converter's (`code-<date>-<stem6>-<slug>.md`) inside `<parent-sid8>/`, not `agent-<id>.md` — renaming would break the 6-char-prefix match that `render-sessions.sh`, `session_identity.py` and the census all use to decide "rendered".

`render-sessions.sh` got a two-line additive append (a comment and the call) before its `failed` exit; nothing else in it moved.

## 5. What the renderer still cannot see (the bound)

- **Archived subagents** — `raw/session-archive/*/subagents/agent-*.jsonl`: `[m 14:47]` 9 dirs, 113 files. Not in the brief's population (project dirs only); `session_identity.py --subagents` counts them, this renderer does not. Many are the same agents as the live ones (archive = mirror), unmeasured which.
- **Sibling trunks' subagents** — the 403-turn fleet number is 5 keys; this pass renders 3 keys of one trunk. Personal G (167 turns) and CFL G (157) hold the row's actual primaries and are out of this tree's write scope.
- **The index** — 0 of these 127 renders are in `professional.sqlite` until `scripts/graphrag/build_index.py` runs; the retriever said STALE at 14:44 for the corpus as it stood BEFORE these 127 files landed. Render is not index (census §4 check 2).
- **`type: attachment` records inside subagent JSONLs** — 1,208 of them in this population; the converter's sidecar counts them, nothing here reads their text. Whether any carries a queued Jon message is UNKNOWN.
- **Thinking blocks** — encrypted in the JSONL, converter states so in frontmatter; not recoverable.
- **Live growth** — a subagent JSONL still being written renders as of its mtime; the appendix for a running agent is a snapshot.

## 6. Paths this pass created or modified

- created `scripts/render-subagents.py` · created `wiki/references/subagent-transcripts-render-horizon-2026-09-12.md` (this) · created `raw/transcripts/claude-code-subagents/**` (254 files) · created `exchange/WIKISKILLS-IMPROVE-ECHOED-682d274b.md` (pass 3; pass 2 copy is on branch `worktree-prof-n3c0-pr4-frame`, unmerged)
- modified `scripts/render-sessions.sh` (+2 lines) · `wiki/log.md` (+1 line)
- scratch: `…/682d274b-…/scratchpad/{pop.py,meta.py,render-run1.log,trial/}`
