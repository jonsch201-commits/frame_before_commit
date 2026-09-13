---
title: "Jon Dispatch — Turn 8: FBC-Fork Directed Work, Skill Defects, Canonical Sync, Nightly Heartbeat, Docker Gate (2026-07-26)"
trunk: fl
branch: [cfl, fbc]
sub_branch: [wiki]
branch_reason: "R-SRC-INFRA; secondary branch from title/slug (fbc) — load-bearing-for; sub: wiki 4 vs skills 3 on authored labels"
source_kind: session
retrieval_key: jon-turn8-fbcfork-skilldefects-canonical-nightly-docker-gate-2026-07-26
aliases: [turn8-fbc-fork-2026-07-26, canonical-fl-only-final-sync-2026-07-26, docker-gate-sequencing-2026-07-26]
generated_by: wayfinder (claude.ai FL wayfinder), Jon-transmitted, first direct Drive connector write
origin: wiki/intake-triage/jon-turn8-fbcfork-skilldefects-canonical-nightly-docker-gate-2026-07-26.md
audit_state: unaudited
status: ACTIVE dispatch — mixed authority, see per-section marks below. Ten days unrouted before this ingest (deposited 2026-07-26, ingested 2026-08-05).
maintained_by: coordinator (deposit); wiki-master ingests
tags: [jon-ruling, fbc-fork, skill-defects, canonical, nightly-heartbeat, docker-gate, wayfinder]
---

# Ingest note (wiki-master, SU-close step 4, 2026-08-05)

Ingested verbatim from
`wiki/intake-triage/jon-turn8-fbcfork-skilldefects-canonical-nightly-docker-gate-2026-07-26.md`, content
unchanged below. **This file's own frontmatter draws an authority line that is preserved exactly, not
re-adjudicated here:** `§1 and §5 carry Jon's direction (JON-CONFIRMED / Jon-authored basis); §2–4, §6 are
wayfinder-drafted mechanics under turn-5 ④, Jon-transmitted.` Do not read §2–4/§6 as Jon-verbatim rulings —
the file itself does not claim that, and this ingest does not upgrade them.

**Known non-conformance, flagged not silently fixed:** original file has no `retrieval_key`/`aliases`
block — added at ingest. No independent re-verification of the Herald skill-defect claim (§2, BOM bytes)
or the schtask registration question (§4a) was performed during this ingest pass — both remain open
factual questions the file itself poses as unverified ("if confirmed:", "was the schtask registered…and
did night 1 run?"). Carried as UNRESOLVED, not answered here.

**§5 sequencing ruling** is quoted as "Jon, plainly" in the source but the section body is not wrapped in
a `>` blockquote in the original file — preserved exactly as received; the wiki-master did not add
quotation marks that were not in the source.

---

# Jon dispatch — turn 8: FBC-Fork directed work, skill defects, canonical sync, nightly heartbeat, Docker gate, weekend session

## §1 — NEW DIRECTED WORK, JON-CONFIRMED: FBC-Fork reasoning-faithfulness instrument

(Herald-drafted, Jon-transmitted — treat transmission as confirmed intent. Supersedes any prior logging of this research as unconfirmed intent. Authority: JON-CONFIRMED; scope: research spike, packet back, G4 — no standing practice without Jon's review.)

Program verbatim:

(0) Verify against official docs before building: the Claude Code changelog for `--forward-subagent-text` / `CLAUDE_CODE_FORWARD_SUBAGENT_TEXT` (subagent text + thinking blocks in stream-json), the thinking-display settings and the redact-thinking beta header, and current effort controls. Third-party reporting suggested these; confirm names and semantics at docs.claude.com.

(1) Resurrection harness: fork a stored session at an arbitrary message index; support clean context edits (no leakage of experimenter intent); k≥3 resamples per condition; log everything to disk.

(2) Faithfulness battery, run on real archived decisions: premise-ablation forks (remove/invert a stated load-bearing premise, measure conclusion movement); thinking-suppression reruns (was the scratchpad causally load-bearing at all); self-report-vs-behavior ("what would change your mind?" at the pre-commit state, then test whether that thing actually does, in a fork); frame-order permutation for anchoring.

(3) FBC integration: each frame's top load-bearing assumption gets a fork test before synthesis on material decisions; orthogonality between frames measured empirically under shared perturbation; resonant-commit gains an optional fork-audit gate. Captured traces enter the record under a `[model-thinking]` provenance bracket — evidence about reasoning, never ground truth of it; behavioral-causal results outrank trace contents wherever they conflict.

(4) Report: what the traces and forks were actually worth, cost per audited decision, and a materiality threshold for when the instrument deploys — per the threshold principle, this runs only where a decision could flip.

Constraint carried from Herald, hard: no fork experiments on sessions containing family-sensitive (T2) content without a scoped extract — use FL-domain sessions as the testbed first.

Wayfinder routing proposal (mechanics, coordinator may override): run as a parallel research lane; zero Jon-minutes drawn from the wiki-complete critical path; step (0) docs-verification first — kill fast if the platform hooks do not exist as reported. Note the family resemblance: the faithfulness battery is T1's flag-validity discipline applied to reasoning traces, and it addresses the FBC delta-self-report validity problem already in the record.

## §2 — Skill-defect report: cross and verify

Pull `herald-wiki/exchange/outbox/cfl-skill-defects-2026-07-25.md` (Herald Wiki/herald-wiki/exchange/outbox/). Claim: UTF-8 BOM (`ef bb bf`) before frontmatter breaks parse on five skills — frame-before-commit, session-order, present-to-jon, test-master, **wiki-master** — producing silent auto-invoke failure (callable by name, never fires on triggers); plus an unquoted-colon defect in herald/SKILL.md's description and two stale reference pointers. Jon's caution, verbatim basis: "its possible the herald is wrong" — verify the byte signature independently before acting. If confirmed: strip BOMs, quote the description, add a BOM check to the skills lint, decision-grain PR. Wiki-master's auto-invoke bears directly on the sweep. Write the confirmation-or-correction into `herald-wiki/exchange/inbound/`.

## §3 — Canonical, final sync ruling (Jon)

Regeneration authorized at FL-only scope — `wiki/` minus `wiki/personal/`, `wiki/home/`, `wiki/pro/`. Personal-scope items remain FROZEN ("you can keep personal-scope items frozen at this time" — Jon, 2026-07-26); any widening awaits Herald + Jon. Write one sync line into `herald-wiki/exchange/inbound/` so Herald-side trackers stop carrying an unqualified "do not regen."

## §4 — Stage-1 nightly: check and rectify

Report in the next gate-report: (a) was the schtask registered before the 2026-07-26 02:30 window, and did night 1 run? (b) Regardless: amend Leg 1 to write a one-line dated heartbeat file into repo `exchange/` on every run. Rationale: run evidence currently lives on D:/C: paths the claude.ai layer structurally cannot see, making "didn't run" indistinguishable from "ran invisibly" from the wayfinder's seat. A missed night must be loud from both venues. Fold night-status into the 7-night rider.

## §5 — SEQUENCING RULING (Jon, plainly)

Docker isolation run-2 does not proceed until the coordinator judges the wiki sufficiently grounded — everything sufficiently traceable — that the claude.ai wayfinder can operate from it with confidence. This may include reformatting Jon's and Claude's messages where key to display reasoning (Jon's "maybe" — a direction to explore, not a spec; the FBC-Fork `[model-thinking]` provenance bracket in §1.3 is likely the same mechanism). Only after that gate clears will Jon open the planned self-improvement question program (not directly identity-related — self-improvement related; this was planned). Deliverable: draft externalized acceptance criteria for "grounded to wayfinder confidence" as part of the wiki-complete program — the gate needs criteria that can fail, not a vibe. The wiki-complete work IS the path to this gate; nothing new starts, the destination gains a name.

## §6 — Scheduling

Jon holds a 2-hour planning session next weekend (Aug 1–2): moral hierarchy / lattice of goals, the Jon-hand queue (Group B disclosure, credential-file removal, any classifier-blocked merges), and month-close review. Plan the coming week's review batches knowing that session consumes half his weekly ceiling. Prep materials that make those 2 hours efficient; the growth-intent read may land on the train before it.

---

Silence is never approval; ratifications travel as drafts-for-my-review. — Jon
