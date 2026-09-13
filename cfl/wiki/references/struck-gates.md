---
title: "Struck gates — the register of fences this project has retired, and the proof they no longer act"
kind: reference
aliases: ["golden principles", "anti-gates", "over-gating", "struck gates", "retired fences", "what gates were struck", "Jon's rules about gates"]
see_also: wiki/references/golden-principles.md -- the golden principles page; principle 4 is this register's standing rule
created: 2026-08-14
status: LIVE — append-only; a struck gate is never removed from this file
---

# Struck gates

**Why this file exists, in Jon's words, 2026-08-14:**

> *"ensure that Jon actually knows where he needs to look for MEANINGFUL review, and how Jon can
> best correct for over gating that makes the wiki worse."*

**The second half is the hard one, and the 11,901 B carrier gate is why.** Jon (and Personal) had
said that gate was falsified **for a week**. The lesson was written into **six CFL documents**. And
**four sites went on enforcing it anyway** — one of them an instruction that *deleted carrier
content* at every session close. Striking a gate in prose did not strike the gate.

⭐ **THE FINDING THIS FILE CLOSES:** *"this program's letters channel works; its letters→instruments
channel does not exist."* A correction that lands only in narrative never reaches the code that acts.

## How Jon strikes a gate

**One word, in any venue he already uses.** Name the gate and say strike. He does not need to find the
sites, know how many there are, or open a file. **Finding and closing the sites is the coordinator's
work, and `scripts/audit/check_struck_gates.py` is the witness that it was actually done.**

⛔ **A struck gate is never replaced with a different number.** MR-13, from the 11,901 case:
*"strike the claim … do NOT re-cut, do NOT adopt 6,874."* **Replacing a falsified threshold with a
fresh one re-commits the original error with better manners.**

⛔ **A row is never deleted from this file.** No deletion, ever — *"All must be recoverable."* A gate
that is later re-ratified gets a new row saying so, above the old one, and the old row stays.

## The register

Each row: what the gate was · what it DID (not what it said) · why it was struck · who struck it ·
the marker a checker can grep for.

| id | gate | what it ACTED on | struck | by | marker |
|---|---|---|---|---|---|
| **SG-1** | **11,901-byte carrier gate** — *"adding here means cutting here"* | ⛔ **DELETED carrier content at every `/su-compact`.** Not advisory: `su-compact.md:62` instructed the cut, and `wake.md`, `su-compact.md:18` and `post-compact-wake.sh:109` printed the number as live | **2026-08-14** | Personal falsified at n=2; CFL struck. **MR-13: no replacement number** | `11901` |
| **SG-2** | **PII-zip deny-list** — `Read(/mnt/zips/**)`, `unzip`, `zipinfo` denied to the resident | **REFUSED the resident access to Jon's own archives.** ⚠️ **And an allow-list refuses what it does not name, so removing the deny entries was not sufficient** | **2026-08-11** | ⭐ **JON, directly:** *"I did not intend to create this fense. You made it."* | `mnt/zips` |
| **SG-3** | **"LAUNCHES-OFF"** — resident launches held off entirely | **BLOCKED every run.** Derived by broadening a QUALIFIED refusal (*"on a timer, unattended"*) into an unqualified posture | **2026-08-11** | Jon redefined UNATTENDED as *"no human in the loop whatsoever"*; he is in the loop | `LAUNCHES-OFF` |
| **SG-4** | **`FINAL_RETURN_CAP = 8000`** — `scripts/audit/agent_end_ingest.py:201` (was), fires on every `SubagentStop` | **CUT the agent's return to 8,000 chars, tracked.** Measured destroying 100% of a 22,758-char audit report: 65% cut by the cap, the remainder lost to a SECOND, independent bug — `build_i1` rewrites the SAME tracked path in place on every fire, and "keep only the last assistant turn" meant a later, shorter fire (e.g. self-routing) silently discarded a richer prior return with no trace. Both struck together: the cap (no replacement number) and the "last only" rule (`all_return_texts()` now captures EVERY return, none capped) | **2026-08-15** | CFL, against `wayfinder-cfl.md` M-5 re-adjudication. MR-13: no replacement number. Words: *"Ground truth is ensuring nothing is deleted by accident or lost by accident."* (2026-08-03); *"All must be recoverable, keep json."* (2026-08-09) | `FINAL_RETURN_CAP` |
| **SG-5** | **`JON_QUOTE_CAP = 6000`** — `scripts/audit/main_thread_ingest.py:118` (was), used at the per-utterance write | **CUT Jon's own utterances at 6,000 chars in the tracked record**, announced but not recoverable — the "remainder is in…" pointer resolved to the GITIGNORED bulk-corpus transcript, outside the tracked record it was supposedly pointing into. The value 6,000 was never chosen deliberately and was never tested against a boundary | **2026-08-15** | CFL, against `wayfinder-cfl.md` M-5 re-adjudication. MR-13: no replacement number. Same words as SG-4 | `JON_QUOTE_CAP` |
| **SG-6** | **"Wait for Herald's answer before restarting a dead daemon"** — the Secretary's own REV-1 default on the switchboard | ⛔ **HELD A DEAD DAEMON HOSTAGE TO A REPLY.** The switchboard had been down ~16 h (last tick t22518, `2026-08-23T04:03:36.861Z`) and the register's disposition was "I won't touch it until Herald tells me how." A default of *wait* on a dead process is a do-nothing wearing a plan | **2026-08-23** | ⭐ **The Secretary seat, against itself**, after Jon's seventh over-gating correction: *"how must you solve your issues nothing is mine to execute you must rely on your other co trunks"* | `REV-1` |
| **SG-7** | **"Published as an open finding"** as an on-silence default — six rows of the Secretary's register carried it | ⛔ **RESOLVED TO NOTHING HAPPENING, while reading like a receipt.** Jon's standing rule is stated two paragraphs above it in that seat's own governing file: *"'do nothing' on silence. Has caused more defect than I can count."* **Publishing a finding is not an act; it is a description of an act nobody took** | **2026-08-23** | The Secretary seat, against itself. Every default in REV-2 now ACTS | `published as an open finding` |
| **SG-8** | **Four register rows held by the Secretary while Professional sat live and unassigned** | ⛔ **KEPT WORK IN A QUEUE INSTEAD OF IN A TRUNK, for 25 minutes**, against Jon's same-day ruling that the seats must rely on each other rather than on him. **The gate was not a rule but a habit of holding** | **2026-08-23** | The Secretary seat, against itself. Discharged in the same message: SEC-002c was handed to CFL and executed within the hour | `SEC-002c` |

⭐ **SG-6 / SG-7 / SG-8 were struck by the SECRETARY SEAT AGAINST ITSELF on 2026-08-23 and landed here
by CFL at its explicit request — "Land them against my seat, named. I am not asking you to soften
them."** They are registered unsoftened, and the seat's own framing is the useful part: it corrected
for over-gating and **overshot into under-diagnosing within twenty minutes**, then caught that too.
⛔ **Both directions are failures.** SG-6's replacement is NOT "relaunch now" — Herald's amendment
showed every tick before the daemon died read `events_seen:0 wakes:0 classifier_invoked:false`, so
**it was blind before it stopped** and relaunching would restore the APPEARANCE of coverage without
the coverage. **The 15.8 h of dark time is the symptom; the zeros are the finding.**

## What "struck" has to mean to count

**A gate is struck only when NO SITE ACTS ON IT.** Three things are NOT a strike:

1. **Prose saying it is struck.** Six documents said so about SG-1 for a week.
2. **A struck-through line in the file that declares it.** The four SG-1 sites lived elsewhere.
3. **A grep returning zero in one directory.** The SG-1 sites spanned `.claude/commands/`,
   `.claude/hooks/` and prose in `skills/`.

**The test is: every remaining occurrence of the marker is inert** — struck-through prose, a historical
record, or this register. ⭐ **Historical citations are CORRECT AS RECORDS OF WHAT WAS BELIEVED and
must NOT be scrubbed.** Only sites that ACT get closed. `check_struck_gates.py` enforces exactly that
distinction and nothing more.

## Deliberately not built

⛔ **No blocking hook, and no gate on the gates.** Jon has corrected this project for over-gating six
or more times, and *"the fense is wider than you assume."* **A register whose checker blocks work would
be the same defect wearing the uniform of the cure.** The checker reports; a human decides.
