---
title: "What Jon has actually said a session boundary must do — five requirements, and the lists that are not his"
created: 2026-08-07 16:40 CDT (session 2)
provenance: "[relayed — fable-mirror consult a0d88bd6, 2026-08-07, corpus current through 2026-08-07 for claude-code and 2026-08-05 for claude-ai. Every cite below is the mirror's; I have not re-opened the primaries.]"
purpose: "Defensive. This project built /wake and /su-compact on 2026-08-07 by copying sibling designs. This page records which parts trace to Jon and which are project design, so a later session does not cite the latter as the former."
---

# The five, in his words

`[TRANSCRIPT:2026-06-27]` `[CFL] raw/transcripts/claude-code/code-2026-06-27-a13169-…md:40382`

> *"you are about to auto compact be ready for a sudden nap. WHen you wake up, yes check your work as
> described and explain what your checks should do"*

Same file, `:40494`:

> *"When you wake up, plan to launch a wiki master subagent for a standard update THEN to STAGE the
> wiki updates in a 'wiki-temp' folder…. Sory I just need to see all of it before I'll trust it was
> done as intended… you will have to be prepared to follow our safety standards."*

`[TRANSCRIPT:2026-07-25]` `[CFL] …/code-2026-07-25-0fb7ca-…md:42800`

> *"You should only pause if you are ready for a compact nap and have my message ready for you when
> you wake up."*

Same file, `:28899`:

> *"a standard update should have occurred with your literal session logs in it based on the zips. If
> it hasn't that's a defect."*

`[TRANSCRIPT:2026-07-27, relayed via a 2026-08-02 quote]` `…/code-2026-08-02-a85aea-…md:12859`

> *"if nothing waits on me, when what is the reason why you have chosen to pause?"*

**Reduced:**

1. **Verify on wake** — check the prior work, and be able to say what the checks are for.
2. **Stage before applying** — he wants to see it before he trusts it was done as intended.
3. **Preserve literal session logs**, for reviewability. Their absence is a defect, in his word.
4. **Have a message ready for the future self** before pausing.
5. **Never pause without a reason.** A pause is not a status report.

---

# What is NOT his, and the reason this page exists

**The boundary-content list at `[CFL] raw/transcripts/claude-ai/fl/how-to-use-claude/chat-2026-04-06-037ce1-…md:1124-1131`** — milestone status, last action, open questions, carry-forwards, staleness timestamp — **is Claude's proposal, not Jon's requirement.** His contribution in that exchange was `:1139`:

> *"Before you suggest how he changes it, read it. Lets get on the same page before suggesting process
> changs"*

**The doctrine "it should get shorter over time… every self-check is a scar"** (`a85aea:18106`) is likewise **Claude-authored**, approved by Jon through plan acceptance rather than stated by him. Grade it accordingly.

**And "parse them into the corpus"** was Claude's operationalization of requirement 3, not Jon's words — flagged in the same corpus at `code-2026-07-29-627c1e-…md:21414`.

This is the attribution trap Claude Personal warned about on 2026-08-02: eight cites of one theme across two sessions, every instance the assistant speaking. **Their sentence: *"We nearly wrote the page."*** Everything more elaborate than the five above is project design layered on top, and it should be defended on its own merits rather than by borrowing his authority.

---

# Coverage of this project's commands, measured against the five

`.claude/commands/wake.md` and `su-compact.md`, written 2026-08-07.

| Requirement | Covered? |
|---|---|
| 1. Verify on wake | Yes — `/wake` steps 1–4 measure rather than recall. |
| 2. Stage before applying | **No.** Nothing in either command stages for review before writing. |
| 3. Preserve literal session logs | **No.** This repo has no capture script; CFL's `capture_all_jsonl.py` is CFL's. |
| 4. Message ready for the future self | Yes — `WAKE.md`, refreshed at `/su-compact` step 1, budgeted at 6,144 B. |
| 5. Never pause without a reason | Partly — the rule lives in the heartbeat prompt, not in either command. |

**Two of five are absent and one is partial. Recorded rather than built.** Requirement 3 needs an instrument this project does not have, and requirement 2 is a workflow change rather than a text change; neither is a heartbeat's call, and `CLAUDE.md` warns specifically against scaffolding nobody asked for.

---

# Open

- **I have not re-opened any of these primaries.** All cites are the mirror's, and the corpus is
  lossy and never authoritative over the wiki. Before any of the five is quoted as a governing
  requirement, read the turn.
- **Requirements 2 and 3 were stated in a CFL context** (wiki-master subagents, zips, `wiki-temp`).
  Whether they transfer to this project as stated, or only in principle, is not established.
