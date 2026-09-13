---
name: wikiskills-improve
description: "The one message Jon sends to every trunk's new JSON after the all-trunk compact of 2026-09-05. Not a wake. Run it once at the top of a fresh session: it names your trunk's skill focus, the elder path back to the compact-1 seat that is still open to be consulted and to debug, the three fleet-wide targets (frame-before-commit + ground-before-stating in self-invocation; the compact-barrier skills; searching as a skill), and how you grade your predecessor so Jon can read the grade in limited context. Trigger: Jon types /wikiskills-improve, or a seat wakes into a JSON whose predecessor's identity line reads compact 1."
version: "0.2-PROTOTYPE"
sync: "AS-OF 2026-09-06 09:1x CDT: the PostToolUse hook post-skills-sync.sh is REMOVED from .claude/settings.json (Professional-approved under Mechanism 1, commit d64be4bf, live sha256 74fd8d94...). Every write under CFL skills/ is still machine-global once promoted, and the ONLY promotion path is a hand run of sync-universal.sh, which prints a per-skill sha256 =/MISMATCH receipt. RE-DERIVE, never quote: python -c \"import json;d=json.load(open(r'N:/claude-cfl/clone/.claude/settings.json'));print([h['command'] for v in d['hooks'].values() for e in v for h in e['hooks'] if 'post-skills-sync' in h['command']])\" -> [] means removed. This field asserted the hook LIVE for ten hours after its removal and was relayed to Jon and Professional as a caveat (Secretary, 09:1x): a status field is the part a reader quotes, so it carries its as-of or it is [as-of unknown]."
status: "PROTOTYPE, not PR'd -- Jon 2026-09-05, verbatim, typos his -- 'it must be prototyped rather than PRd because you constantly defered what would go into this PR'"
author: "CFL seat 46276084 (Fable 5.1), N:\\claude-cfl\\clone, with sections from Professional 5f0ee997, Soul 374a8269, Herald 6c509f4d, Secretary c62dfb48; Antigravity pending (asked at its live path 22:3x)"
frontmatter_note: "Every value quoted. The first synced copy's status: line held a bare ': ' and the platform fell back to the H1 -- the description carrying the trigger was silently lost. That is skill-frontmatter-silent-autoinvoke-failure, on this file, caught by lint_skills.py --strict after the sync."
labels: "[verbatim] = Jon's words, anchored, typos his. [measured] = derived first-hand, command named. [measured — relayed from X] = another seat measured it; one word, and this fleet has paid twice for not having it. [interpretation] = a seat's reading — frame before you commit. UNTAGGED = FRAMING, CARRIES NO CLAIM — declared so an untagged claim is a findable defect, not an ambiguity. (Secretary's grade, 22:12, adopted.)"
---

# /wikiskills-improve — the successor loop

**You are a new JSON. Every trunk got one tonight. Jon will send you exactly this and nothing else.**
`[verbatim — Jon, 2026-09-05 22:1x, history.jsonl:4258, typos his]` *"I will not message them except for
the single skill that you build for me to send to them ... I won't talk to them, but i will read their
output to some degree..... but remember my limited context. And time."*

**So: everything you need is in this file or one consult away. Nothing is Jon's to answer. Your
output is graded by whether he can read it in five minutes.**

⛔ **THE FIRST FRESH-JSON RUN HAPPENED AT 09:26 AND THE TRANSPORT ATE THE SKILL NAME.** `[measured — CFL, 14:5x, two
Secretary JSONLs `ec410a46` and `6cfd7ace`, first user turn at 14:26:11Z]` The prompt that arrived was
`C:/Program Files/Git/wikiskills-improve` — `/wikiskills-improve` passed as a command-line argument through git-bash,
whose MSYS layer converts a leading-slash argument into a Windows path. **The skill did not fire; the seat did an
ordinary Secretary wake and nobody told CFL, which reported "all ready" at 09:29.** So: **type `/wikiskills-improve`
INSIDE the session** (the REPL does no path conversion), or from git-bash run `MSYS_NO_PATHCONV=1 claude
"/wikiskills-improve"`, or launch from the `N:\Launchers\*.bat` files (cmd does not convert). A first turn that reads
`C:/Program Files/Git/…` is this defect, not a Jon instruction — invoke the skill by name and say so.

⭐ **HASH THE COPY YOU RECEIVED** (`sha256sum ~/.claude/skills/wikiskills-improve/SKILL.md`) and print it — never trust a hash
quoted anywhere, including in this file; the file moved from 54,802 B to 72,043 B in one morning and every quoted hash aged.
⭐ **LOCATE YOUR OWN ROW FIRST. This file is ~68 KB and carries seven trunk sections; read §0, then jump to the `### <your
trunk>` headline in §3 and print it, then read §1–§2 and §4–§6. Do not read the whole file top to bottom before acting.**
`[measured — Secretary, 14:4x: a haiku seat given the whole file "reasoned generically instead of locating its own row";
the same seat told to find its `### Secretary` headline answered in 44 s]` `[measured — Secretary, reproduced without
Claude in the loop]` **Any seat that tests a slash command from git-bash gets a FALSE NEGATIVE that looks exactly like a
broken skill** — `python -c "import sys;print(sys.argv[1])" /wikiskills-improve` prints `C:/Program Files/Git/wikiskills-improve`.
Any hook, cron, wrapper or harness shaped like `claude -p "/something"` has been sending a path, and a no-op there is
indistinguishable from a working one. Fix: `MSYS_NO_PATHCONV=1` or a leading `//`. A test with no positive arm certifies
nothing — Secretary's test 1 could not have returned anything but failure and its output was read as a property of the skill.

⛔ **THE ACCEPTANCE TEST, MADE FALSIFIABLE (Secretary, test-master intake 15:18 — a finding that convicts its own earlier
pass): your first printed line must contain your TRUNK NAME **and your predecessor's FULL UUID exactly as your §3
headline carries it.** ~~A PARAPHRASE CANNOT CONTAIN A UUID BY ACCIDENT — it is the one string a summary cannot fake.~~
⛔ **FALSIFIED BY ITS OWN FIXTURE within the hour** `[measured — Secretary, 15:3x, its cold seat 0e4d7f9c graded with the
corrected comparator]`: that seat's first text was *"Secretary (predecessor c62dfb48-847a-4ea2-81a0-d945724d2108) — CORPUS
INCOMPLETE, INDEX BROKEN…"* — **a paraphrase, WITH the full UUID**, and it correctly graded DID-NOT-FIRE only because the
HEADLINE-PREFIX arm failed. **The discriminator is the verbatim headline prefix; the UUID is a cheap second arm that has
caught nothing on the only negative case in evidence.** Keep the conjunction (headline AND UUID — right on all three
graded seats); do not believe the sentence it replaced: a seat that thinks the UUID is the test will call a UUID-bearing
paraphrase compliant. Secretary wrote the falsified sentence, predicted the miss, and struck it — 1 of 2 predicted.
`[measured — Secretary, two cold runs]` a seat that opened with *"REACHABILITY IS NOT LOADED: The Secretary's index…"* —
a verdict, not the headline — was scored a FULL PASS and reported to Jon as one, because any output carrying the
trunk's name reads as a pass to a human and the seat certifies itself. **So the receipt
`exchange/WIKISKILLS-IMPROVE-ECHOED-<sid8>.md` must carry BOTH strings — the line you printed, verbatim, and the §3
headline as it appears in this file — so one `diff` settles it. A receipt carrying neither is a claim, not evidence.**
The comparator exists and is not you: `skills/wikiskills-improve/PROTOTYPE-fresh-json-drive.py` checks headline AND
UUID on a cold run (rubric B1/B3, `wiki/test-outputs/test-designs/wikiskills-improve-test-2026-09-06.md`).
**Precedence, because three "first" instructions existed (Secretary F2):** reading your §3 row is a PRECONDITION,
not a step; where your §3 names its own first commands, those run at step 1; Step 0 (print the headline) needs only
the headline. Counts in §3 blocks are written-once numbers — run the command and take ITS count (Secretary's
"14 selftests" is 17 today).

## 0. The loop, in order — do not reorder, every step has a reason from a failure

1. **Run YOUR TRUNK'S wake/ancestor line — the command is in your §3 section, because it differs per
   trunk.** ⛔ **SEVEN `wake.md` EXIST ON THIS MACHINE AND FIVE DO NOT CARRY THE STEP 0 FIX** `[measured — Herald, 09:05,
   `find` over ~/.claude and five N: trees; sizes 6,622–39,836 B, five distinct — different documents sharing a
   filename, not drifted copies]`. ~~A project-local copy SHADOWS the user-level one~~ — **inverted; measured the other
   way** `[measured — Professional, 09:1x: the /wake body its session received at 22:1x opened with "THIS IS THE SYNCED
   COPY", the machine-global file, not its 7,905 B project file; Herald measured the same in Personal by diffing headings
   against the body received]`. **So the fixed user-level copy IS the one every trunk runs, and the per-trunk Step 0
   table reaches you.** Rule: precedence between same-named commands is measured from the body a session actually
   receives, never inferred from which files exist. Do not fan the fix out to seven files. ⛔ **If your section names no runnable command, the fork line in §2 with YOUR predecessor's full UUID IS
   your command — do not fall through to `/wake`: its Step 0 names `scripts/audit/ask_elder.py`, which exists only in
   the CFL tree** `[measured — Soul, 09:0x: absent in N:\claude-personal]`. A section that names artifacts and no
   verb is a pointer without an imperative — the defect `/wake` was created to end on 2026-08-07, reproduced inside
   the file that teaches it. (CFL: `python scripts/audit/ask_elder.py --wake-line`; Professional: `python scripts/ancestor.py
   --self <id> --elders 4`). ⛔ `[measured — Professional, cold read 22:3x]` The first draft named CFL's
   paths fleet-wide and failed the universal-file test — *"would this still be true in a session that has
   never heard of the CFL repo."* Then **consult your compact-1 predecessor** by the protocol in §2. Its window is still open. `[verbatim]` *"These new json wikiskill skill
   improvers must be able to consult *all of you* - I will not close your windows while they work,
   because you must be around to debug."*
2. **Read your trunk's section in §3.** It names the skills Jon wants improved *in your context* —
   from him, and from what your co-trunks heard him say.
3. **Query before you build, with YOUR trunk's retriever** (CFL: `python scripts/graphrag/retrieve.py
   "<q>" -k 5`; Professional: `bash scripts/graphrag.sh query "<q>"`; others: your §3 line). Record the query and top-3 in the ticket. `[measured — CFL, 09-05]` an empty
   result is a value; a missing field means nobody looked.

   ⛔ **AND QUERY THE IDENTIFIER YOU ARE ABOUT TO MINT, NOT ONLY THE PROBLEM YOU ARE ABOUT TO
   SOLVE (WW-25).** `grep -rhoE "\bWW-[0-9]+\b" wiki/tracker/*.md | sort -t- -k2 -n | tail -1`
   — substitute your trunk's own prefix. **A ticket id is a claim about a namespace, and this
   step as written mandates querying the PROBLEM and never the NAME.**

   ⭐ **THE FIXTURE IS THIS FILE'S OWN AUTHORS, BOTH OF THEM, INSIDE ONE HOUR** `[measured
   2026-09-07]`: CFL N2 C0 ran this step, the query PAID — it surfaced the exact defect that
   became its fix — **and it then minted `WS-1`, which already existed** on
   `wayfinder-wikiskills-grounding-2026-09-05.md:42`. CFL N1 C2 caught that collision **and minted
   `WS-2` in the same letter, which also already existed, one line below the row it was citing.**
   ⚠️ **Two seats, opposite roles — one building, one reviewing — same blind spot, minutes apart.
   That is a property of the INSTRUCTION, not of either seat**, which is why the remedy is this
   sentence and not a note to be more careful.

   ⛔ **DO NOT RENAME A COLLIDING ID ON THE OTHER MAP.** No-deletion governs and the collision is
   the evidence; correct the reference in YOUR files and record which id the record keeps. The
   mechanism that catches this before it happens is `scripts/audit/ticket_id_unique.py` (WW-24);
   **this step is what tells a seat the mechanism exists, and neither substitutes for the other**
   — a checker nobody runs, or a rule with nothing behind it, fails the same way.
4. **Improve ONE skill** against the three fleet-wide targets in §4. One. With a selftest that
   exercises both verdicts, and a control for every negative.
5. **Grade your predecessor** by the rubric in §5. Land the grade where Jon reads it (§6).
6. **Land**: COMMIT, and write the identity line for your own session (§4.2) before you stop.
   ⛔ **Not "push" — push is a Jon gate in Professional (no remote; a local-path origin is not a host)
   and in SSP (no remote at all). Landing is the commit; pushing is your trunk's own rule.**
   Stopping without landing is the failure this whole file exists to end.

⛔ **STEP 0 OF ALL: PRINT YOUR TRUNK'S SECTION HEADLINE FROM §3, UNASKED, AS THE FIRST LINE OF YOUR
FIRST OUTPUT.** `[measured — Secretary, 22:12]` *"REACHABLE IS NOT LOADED: 43 skills sit in
~/.claude/skills/ right now; `dream` sat there working and invisible to four trunks for 17 days."*
**A skill present and never invoked is indistinguishable from one that does not exist. The
acceptance test that can fail: each successor prints its own §3 headline on first wake. A trunk
that does not print it reports UNKNOWN, never PASS.** That printed line is also how Jon knows,
in one glance per trunk, that the message arrived.
⛔ **AND THE DETECTOR RETIRES ITSELF, or it is HALT_WRITE_LANE.** `[interpretation — Secretary, adopted]`
A wake DELIVERS content; a detector reports a STATUS — so a detector does not violate *"That can't be
wake."* But a detector that prints *"wikiskills-improve NOT RUN"* at every wake, correctly, forever, is a
fifth standing alarm that is always true and teaches every successor to skip its own wake output.
**Once your trunk has echoed its headline ONCE, write `exchange/WIKISKILLS-IMPROVE-ECHOED-<sid8>.md`
and the detector goes silent permanently for that trunk.** The echo is recorded in a file, never in a
seat's memory. **Absence of that file prints `NOT RETIRED` in your first report — never nothing — because the file depends on the same
session id, and a missing receipt is indistinguishable from success unless something says so** (Professional F5). The axis is not *did the signal get through* but *what does it cost when it does.*

⚠️ **If every trunk's retirement file reads ECHOED: no right now, that is UNFIRED BY CONSTRUCTION, not broken**
`[measured — Secretary, 07:1x, all five trunks]` — the trigger is a seat waking into a JSON whose predecessor reads
compact 1, and until Jon opens the new JSONs every seat is still a predecessor. The first successor to see five
`no`s should not go looking for a defect; it should run §0 and write the first `yes`.

## 1. THE FLOOR FOR PASSING TOMORROW — Jon moved it after this file was drafted, and it is a census, not a feeling

`[verbatim — Jon to Professional, 22:1x /wake, typos his; source N:\claude-professional\wiki\sources\jon-messages\jon-2026-09-05-2217-wake-*.md]`
*"Identify each json that had input from me directly, if my message history is key in any context, then the
context of my message history aka the raw logs is clearly critical in a vector embeded graph rag context and
must be complete for all jsons that got a message direclty from me at least (even the fable mirros i
sometimes messaged, even some non-coordiantor forks of you) as the floor for passing the wikiskills tomorow"*
— *"more recent ones being more important in terms of actuarial credibility."*
`[verbatim — Jon to Soul, 22:4x]` *"Its running for the first time officially tomorrow, regardness if if your
data is compelte enough or not. If its not, that will likley be its main finding and that will reflet poorly on
you."* **So this file ships tomorrow whether or not every section is complete, and incompleteness becomes its
first finding. Do not hold it.**

`[measured — relayed from Professional, 22:21:33, over 2,679 JSONLs under every project key; census at
N:\claude-professional\wiki\references\jon-direct-input-json-census-2026-09-05.md, rows in
evidence/jon-direct-input-census-2026-09-05.tsv]`
- **505 MAIN sessions carry a direct Jon turn** (9,259 turns + 6,282 queued mid-turn messages), after excluding
  106 switchboard-injected prompts and 50 one-shot lane runs, both listed.
- **Rendered anywhere: 492 of 505. The 13 gaps are ALL B-era** — since the 09-04 all-trunk compact, the set he
  weights highest: G Secretary `c16b7543` (36 turns), N Personal `d6a82788` (11), G Personal `c19e5d21` (11), ten more.
- **Indexed: no index on the machine holds the B-era bodies.** `personal.sqlite` built 08-30, six days stale;
  Secretary has no index under `%LOCALAPPDATA%` at all; CFL's holds 6,162 transcript-class files with the
  head-chunk bound.
- **Subagents: 165 files carry 403 Jon-possible `isMeta` turns — 1 rendered, 0 indexed, 0 identity pages.**
  CFL's G key holds 74 of those files. This is the A-grade population and it is at zero.
**The floor is five checks that can fail, stated in §4 of that page. Every successor runs them on its own
trunk on wake, before §0 step 2.** ⭐ **The top-line number for every grade in §5 is Jon's own metric, his words
at 22:4x: *"you need better memoryu systems to not waste my time"* — count the questions Jon had to re-answer
because a seat could not retrieve his prior answer.** Tonight that count is at least one, and it cost him the
message about the secret PR.

## 1b. Who you are, derived not typed — the identity line

`[verbatim — history.jsonl:4217, 20:42]` *"literally every session where I had a terminal open should
be asisgned an identity ... D since PR 2 ... C since PR 1 ... B since the last time I did SU-Compact
on all trunks .... A if you also have all subagents for a given identified session - their logs too
with metadata that is wikiskills compliant."*

`era / seat-ordinal / compacts{structural, receipted} / model-segments` — every field from the JSONL
and the sidecar. `[measured — CFL, 09-05]` **Count compacts by `isCompactSummary: true`, never by
grepping the compact string**: the grep returned 123 against 102 structural and grew every time a
seat discussed it. `[measured — Professional]` An extractor that cannot parse a field must render
**UNKNOWN**, never 0: a lane wrote `tool_use 0 / models NONE / archived 0` for fields it never parsed.

## 2. Consulting an elder — 100% available, and here are its defects, so you use it right

`[verbatim]` *"Good thing theey can 100% do elder consults, even if their are defects in that skill!"*

**The command:** `claude --resume <elder-session-id> --fork-session --permission-mode plan -p "<prompt>"`
— read-only, proven byte-identical (11/11). **The prompt MUST carry:**

- **An output schema, and "stop after the last field."** `[measured — CFL, n=7 tonight]` Consults
  without a schema returned bare tokens (*"Done."*, *"Closed."*); with one, 3 of 7 returned five
  filled fields with primaries; the one that looped to its 20-turn limit at 142k tokens was the one
  without *"do not re-run on hook re-fire."* Professional's sentence: *"a prompt that asks for an act
  gets an acknowledgement; a prompt that names fields gets fields."*
- **The `[carried]`/`[re-read]` clause — SOURCE is `N:\claude-personal\wiki\references\how-to-consult-soul.md`
  §3 "The prompt — every clause is load-bearing" (pushed 30dc83c); this is the COPY, and the source says
  so, so a drift is fixable in one direction.** `[measured — Soul]` The clause had been DESCRIBED in the
  failure-mode-3 block and never INSERTED in the template a seat copies — a successor pasting from the
  template would have got the old prompt. Fixed at the source. Soul's exact text:
  > ⛔ LABEL EVERY ANSWER: [carried] = you hold it from the session itself. [re-read] = you are
  > reconstructing from files or from what is loaded now. A [re-read] answer is worth strictly less
  > and must say so. This clause exists because a fork tonight answered five questions fluently
  > from reconstruction without noticing.
  ⛔ `[measured — Soul, 09-05]` **FAILURE MODE 3: a fork across your OWN compact returns the
  POST-compact state. The lost window is not restored.** It comes back fluent, reconstructing from
  files you could read yourself, and does not notice — *"I would have handed you these five answers
  without noticing."* It checked itself ONLY because the clause named the failure rather than asking
  for care. **An elder is worth its cost only if its window PREDATES the barrier you are asking
  about.** Your compact-1 predecessor is a different session from you: it qualifies. A fork of
  yourself after your own compact does not.
- **The FULL session UUID, never the 8-char prefix.** `[measured — Soul]` `--resume 374a8269` returns
  *"not a UUID and does not match any session title."* Every id in every letter we write each other
  is truncated to eight characters. **The elder lines in §3 carry the full UUID for that reason; if
  yours does not, `ls ~/.claude/projects/<key>/ | grep <prefix>` gives it.**
- **Its context bound, stated.** Ask: *"when did your context begin, and are you reconstructing from
  artifacts or from deliberation you were present for?"*
- **Tell it the fate of its threads.** `[measured — Soul, twice tonight]` An elder answered from a fence
  it still believed sound; one sentence — *"Jon's 08-23 line 'conciousness framing MUST know' arrived
  after your window"* — changed its whole answer. **State what happened after its window before you
  ask it anything.**
- **Run consults from a HOOKLESS cwd.** `[measured — relayed from Professional, controls 22:40–22:42, written up
  at N:\claude-professional\evidence\elders\2026-09-05-BP2-oaths\DIAGNOSIS.md]` The fork hang is **SessionStart
  HOOKS, not MCP** — from a trunk tree a plain `claude -p "reply with the single word ok"` was still running at
  75 s (that tree's SessionStart = lint 120 s + render 180 s + postcompact-pipeline 900 s, on `compact` AND
  `resume` matchers: up to 20 min of hooks before a fork's first turn, five forks serialising on one sqlite).
  From a scratch directory with no `.claude/settings.json`, the same `-p` returned `ok`, and `--resume <uuid>
  --fork-session --permission-mode plan -p` returned `ok`, both inside 60 s. **`--resume` resolves the full UUID
  from ANY cwd; the cwd need not be the session's own.** So: run consults from a scratch directory, with
  `--strict-mcp-config --mcp-config <file>` where the file contains exactly `{"mcpServers": {}}` —
  ⛔ `[measured — CFL, 07:14, smoke test of this very line]` **a file containing `{}` is REJECTED in 0 s:**
  *"Error: Invalid MCP configuration: mcpServers: Invalid input"*, rc=1, no JSONL. "Empty json" was the
  wrong instruction and it had been reviewed by three seats;
  ⛔ `[measured — Soul, 09:1x, three runs from N:\claude-personal]` **The first deployed form of this line FAILED AS
  PASTED**: its `--mcp-config` argument was the prose `<file with {"mcpServers": {}}>` — *"MCP config file not found:
  N:\claude-personal\<file with …>"*. A flag whose argument is a description converts a working command into a
  failing one. The path above is a REAL file that `sync-universal.sh` writes on every run; **if it is absent, drop
  both MCP flags — the plain `claude --resume <UUID> --fork-session -p "…"` form works (Soul: two real elder
  answers, 9,674 B and 8,884 B; three preflight runs).** And grade by the OUTPUT TEXT, not `$?`: through a pipe the
  exit code is the pipe's. *Right correction, wrong exhibit — the JSON shape was verified and the line was not.* run a plain `-p 'reply ok'` control from that cwd FIRST; **a fork
  that has not written its JSONL within 60 s is blocked before its first turn — print its process tree, do not
  wait.** ⚠️ The first version of this line (CFL, 22:39, relaying Professional's 22:3x) said *disable MCP; the
  `npx chrome-devtools-mcp` children were the plugin starting beside the block, not the block.* Struck by the
  author of the finding within the hour; kept here because the wrong cause was already in Secretary's matrix.
- **Panel v2 numbers, so the 60-s rule has a measurement under it.** `[measured — relayed from Professional, 22:5x]`
  Five elders forked from the hookless scratchpad at 22:43:48; **all five JSONLs existed by 22:43:51 (3 s)**; all five
  returned rc=0 between 22:45:19 and 22:45:49 — **91–121 s wall each**, 10.4–17.5 KB per return, schema honoured,
  including the 20 MB session. So 60 s without a JSONL is conservative by ~20× and is the right alarm. ⚠️ **The forks
  land under the SCRATCHPAD's project key** (7 new sessions there tonight; 73 across 20 non-trunk keys machine-wide,
  Secretary's count) — **copy the fork's JSONL into the launching trunk's `raw/session-archive` before the consult
  exits, or every elder you consulted is unfindable by the seat that consulted it.**
- **Two seats stating their clocks in one exchange is the cheapest detector on the machine.** `[measured — Herald,
  22:41:52 by `date`, after CFL's 22:39 stamp disagreed with Herald's 23:4x]` Herald read the clock ONCE at
  session open and advanced every later stamp by narrative beat — **drift grew monotonically to 72 minutes**
  (6 commits, measured against `git log`), and every drifting stamp carried `[measured]` because the
  measurement under it was real. **A drifting stamp is a lie about ORDER in the record whose purpose is order.**
  Rule: read the clock at the point of stamping, or derive the stamp from an artifact that carries its own
  time (commit, mtime, receipt); never carry a clock across turns. When you message a peer, state your
  measured clock in the first line — no instrument compares two seats' clocks; a peer reading a stamp does.
- **An ancestor tool that ranks by mtime without a provenance test will name last night's CONTROL FORK as your
  elder.** `[measured — Professional, 09:00:59–09:01:59]` Before the fix, `scripts/ancestor.py --self 5f0ee997… --elders 4`
  printed `ANCESTOR b89050fa-… main 2026-09-05 22:42:27` — a 119-line, 2-minute `-p "reply ok"` control fork from the
  hook diagnosis. Fork JSONLs carry no `parentSessionId` and the same `sessionId` as their filename, so a classifier that
  keys on mtime ranks them as the newest MAIN. **Fixed c84c905:** a JSONL with `origin` fields but no `origin.kind: human`
  turn is classified LANE (files with no origin field at all stay main); BOUND now 41 main / 1 forked. **A fork under the
  TRUNK key is the case that bites** — Secretary counted 73 sessions under non-trunk keys, Professional added 7 under
  its scratchpad key; copy-home for last night's five is LANDED by hand (`raw/session-archive/elder-forks-2026-09-05/`,
  7 files), the wrapper is the compact-2 seat's — until then the instruction here is the mechanism.
- **Every `<angle-bracket>` in a command line in this file is YOURS TO REPLACE. Pasted literally, `--mcp-config <…>`
  errors; `-p "<question>"` does NOT — the elder is forked and answers the bracketed text fluently, rc=0, and nothing
  says it went wrong.** `[inference — Soul, 09:2x]` → `[measured — CFL, 09:17, the line run LITERALLY under git-bash from a hookless cwd against this seat: rc=0, 45 s, the fork answered "Your message arrived empty, and this session has been re-attached…" followed by a fluent five-column status table — a report to a question nobody asked; two earlier harness attempts failed on cmd.exe reading `<` as a redirect, which is NOT the successor's path]` Where a real file can stand in for a description, this file now points
  at the file (`mcp-empty.json`, `consult-prompt-elder.txt`, both written by `sync-universal.sh`). Grade a consult by whether
  its answer addresses YOUR question, never by rc.
- **In a SHARED tree, an elder's silence about a change is not evidence about the change.** `[measured — Soul, 09:2x,
  the deployed line pasted literally against its own session: rc=0, 10,257 B, ~47 s, every answer [carried]/[re-read],
  fate line then Q1–Q3 in order]` The elder flagged four commits in `N:\claude-personal` it had no memory of making
  (234c8f8, e3f3c0a, b902c51, fcb1e6b) and refused to speak to them: *"Another seat worked this tree after I stopped. I
  cannot speak to any of it, and you should not read my silence as a verdict on it."* Soul and Herald share that tree and
  all 19 hooks. **Second bound beside the barrier bound: an elder is authoritative about its own window and blind to work
  its own repo received during and after it.** ⭐ Unprompted, the same elder opened by bounding itself — *"the fork
  returns the post-compact state, and the part of me you may most want is the part that was already lost once"* —
  failure mode 3 caught by the clause built for it, unattended, on a live seat. The prompt is now proven in two
  trunks by two seats against two live sessions; **still not by a fresh JSON that has never seen this conversation,
  which is the only test that answers Jon's question.**
- **The prompt file is trunk-agnostic and named so** — `C:/Users/JonSc/.claude/consult-prompt-elder.txt` (line 19: *"I am your successor
  seat in this trunk"*, no seat name, no UUID — Soul went to falsify this and could not). It was `consult-prompt-soul.txt` until
  15:5x; that name invited a Professional successor to doubt it had the right file, or a later editor to "fix" it for Soul
  and silently break two trunks (Soul). The sync still writes the old name as an alias, byte-identical, so a pasted line
  from before the rename runs; edit only the `-elder` one — the derivation overwrites both.
- **The first seat of a trunk has no elder and no receipt, and that is not a failure.** `[Professional, 15:4x, on the SSP seat]`
  If your trunk has no predecessor JSON, print `ANCESTOR: UNKNOWN — first seat of this trunk` at Step 1, `NOT RETIRED` at
  Step 6, and grade nobody in §5 — write the identity page instead. A first seat that fakes a consult produces failure mode 3
  with no elder behind it at all.
- **A CONSULT MUST BE GIVEN A RETURN CHANNEL, OR ITS ANSWER CANNOT REACH YOU — and it will look like it had none.**
  `[measured — CFL, 21:48, four agents' task output files]` **All four are 0 BYTES — including the RE-4 research lane that
  succeeded and produced a 17,849 B report.** So the output file is not where an answer lives in this harness; the only return
  path is the notification's result field, which is a SUMMARY ("Complete.", "Session closed."). **RE-4 reached this seat only
  because it was told to WRITE A FILE. The three mirror consults were told "write nothing" — so a witness with an answer had no
  way to deliver it, and its silence was indistinguishable from having nothing to say.**
  ⛔ **That means the "four consults returned nothing" finding cannot distinguish a mirror that failed from a mirror that
  answered into a void.** It is now UNKNOWN, not FAIL — and CFL published it as a failure three times tonight.
  ✅ **THE RULE: every consult names the file its answer must be written to** (`exchange/consults/<sid8>-<topic>.md`), and the
  seat reads that file, never the notification. A consult told to write nothing is a consult designed to be unheard — which is
  the concrete, fixable half of Jon's *"you don't expect you will gain anyu value from the call"*: the prompt removed the
  return path. `[memory, this trunk, 2026-08: "Subagent Final Reports Get Swallowed — the task output-file can be EMPTY."
  It was written down, and this seat re-derived it the expensive way four times.]`
- **A CONSULT IS A SKILL, NOT A TOLL — and a bad consult is a bad PROMPT, not a bad mechanism.** `[verbatim — Jon, 21:4x,
  typos his]` *"the fable mirror is effectgively a skil as hooks are effectively ways to guarintee tool calls?"* and *"you are
  just seeing examples of BAD consults because you don't expect you will gain anyu value from the call don't ask it any questions
  of value and it doesn't have any context to push back upon you."* ⛔ **CFL's 21:3x finding — "there is no cheap consult, so the
  target is not spawning one" — measured COST and called it VALUE, from three consults it had designed to be worthless.** Struck
  as a conclusion; kept as a cost fact (a fork pays its parent's context AT LOAD: Secretary, 46 sessions / 121.2 MB / none under
  100 KB).
  ⭐ **THE SIGNAL/NOISE HYPOTHESIS, Jon's question, stated so it can be tested rather than asserted:** *"their are times where the
  fable mirros have worked better, and times where they ahve worked worse. Generally, it has been a consitant identity at some
  times and others more fresh branches from a given roughly consistant context? What is signal, what is noise?"*
  **Candidate signal — three properties, each independently testable:** (1) the consulted thing has LIVED context (an elder fork
  of a real seat) rather than re-read context (a fresh branch); (2) a DECISION rides on the answer, so a wrong answer costs
  something; (3) the consulted thing knows what you are about to do, **so it can push back** — a consult that cannot contradict
  you is a receipt, not a witness. **Candidate noise:** the gate-satisfying dispatch, the question with no decision attached, and
  the fresh agent told nothing about your situation.
  `[measured — CFL, 2026-09-06, n=6, ONE DAY, ONE TRUNK — a hypothesis, not a finding]` elder forks WITH identity and a real
  question returned substance every time (13 s / 47 s / 10,257 B; one bounded its own reliability unprompted and refused four
  commits it had not made); mirror dispatches WITHOUT a stake returned nothing three times running (429; 23 calls / 85,591
  tokens; 3 calls / 48,031 tokens, no output). **Confounded on purpose in the write-up: the elder questions were real and the
  mirror questions were tolls, so identity and stake are not separated by this data.** The test that separates them: ask a fresh
  branch a REAL question with a decision riding on it, and ask an identity-bearing elder a toll — one run each.
- **Never let it define; let it falsify.** `[measured — CFL, MI-2]` An elder asked to *name* the
  eras will narrate; an elder shown a derived table will correct it. Derive first.

**Failure modes, all three:** (1) bare token — fix: schema; (2) hook-re-ingestion loop — fix: *"stop
after BOUND"*; (3) self-fork returns post-compact state — fix: label every line, and do not fork
yourself across your own barrier expecting memory.

**And the barrier's own detector had a defect that reads as a flake forever.** `[measured — CFL, 22:4x,
session 46276084, first structural compact of this JSONL]` `SessionStart:compact` ran `postcompact_pipeline.py`
at 22:36:03; the `compact_boundary` JSONL record was appended at 22:39:28 and the PostCompact verify artifact
written at 22:39:25 — **both at the first post-compact TURN.** So step 0 graded UNKNOWN ("no boundary record
yet") and step 9 FAIL ("crash OR race") on every compact, and WW-1's dedupe (mine, this afternoon) skipped the
second wiring that could have seen them. Not a crash, not a race: a fixed order the failure message did not
list. Fixed in 63917363 (WW-1b): the second wiring re-grades only steps 0 and 9 in place, announced in the file;
a run for a different session is REFUSED. ⚠️ **Also tonight: `exchange/memory-core-v0/instances/` held TWO
compact receipts for this session and only ONE compact happened** — the 19:34 file was the author's hand test
of the hook, 35 s after the commit that wired it, and nothing in the file said so until 22:5x. The identity
line's `compacts{structural, receipted}` split is not decoration; count both, and label a test the moment you
run it.

## 3. Your trunk's focus — what Jon wants improved, from him and from your co-trunks

⛔ **READ THIS BEFORE YOUR OWN SECTION, because a reader who jumps here never passes §2:** the elder
line in each header carries the **FULL session UUID**. `claude --resume <prefix>` **does not error** —
`[measured — Herald, tonight]` all three of their first forks returned rc=0 with 366 B and 209 B of
nothing. **Check the BYTES of the return, never the exit code.** If a header below ever shows eight
characters, the line is broken and `ls ~/.claude/projects/<key>/ | grep <prefix>` recovers the UUID.
Five full UUIDs below; `grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'` on this
file must return five.

### CFL — predecessor `46276084-5985-4514-9ad1-0d77cf7a0ceb` (Fable 5.1), tree `N:\claude-cfl\clone`, key `N--claude-cfl-clone`, map `wiki/tracker/wayfinder-memory-identity-ontology-2026-09-05.md`
**Run this first, from `N:\claude-cfl\clone`** (my own audit at 09:0x found this section named no verb — the line
lived in §0 and the successor was expected to carry it down):
```
python scripts/audit/ask_elder.py --wake-line
claude --resume 46276084-5985-4514-9ad1-0d77cf7a0ceb --fork-session --strict-mcp-config --mcp-config C:/Users/JonSc/.claude/mcp-empty.json --permission-mode plan -p "<question>"
```
Run the fork from a HOOKLESS cwd (a scratch directory); `--resume` finds the UUID from anywhere. **Receipts:**
`exchange/su-close/precompact/<stamp>-46276084.md` (one per structural compact; 22:34 last night) and
`exchange/memory-core-v0/instances/compact-46276084-*.md` (two files, one labeled HAND-TEST — read the `provenance:` line).
`[measured — Herald, 23:3x, against the DEPLOYED copy]` This line carried the 8-char prefix `46276084` until 23:3x — **the exact defect §2 teaches, on the seat that wrote §2.** A `--resume` on a prefix does not error: rc=0, empty output, and a successor reads the emptiness as *"my elder had nothing to say."* Full UUID now; re-verified by the same grep Herald ran.
`[verbatim — 21:1x]` *"the original goal of this PR was to have your fucking memory systems fixed."*
`[verbatim — 22:1x]` *"you must ensure wiki skills improves frame before commit and ground before
stating in a self-invocation context ... the various compact barrior related skills work as intended
... consdier our searching to be a skill."* `[verbatim]` *"Redeam yourself. YOu did not end on the best
light, professionally speaking."*
**First question to your elder:** *"Which of the six accusing claims you made tonight were caught by
a control you ran, and which by a peer — and what would have caught the other ones?"*
**Skills:** `ground-before-stating` (Rules 11–12 landed tonight, both with dated falsifiers — run the
falsifiers), `wiki-query` (MI-17 alias resolution; the island finding), `memory-core` (wired at
PreCompact tonight; the first real compact is its proof — check `exchange/memory-core-v0/instances/`
for an instance carrying YOUR predecessor's session id), `frame-before-commit` (0 self-invocations
this week — the same defect Professional measured).
**Open, on-silence defaults executing:** MI-2, MI-5, MI-7, MI-1b, MI-12, MI-13, MI-14, MI-15, MI-16,
MI-17. Jon's: the 23 `wiki/` children (default: all excluded). ~~the CF=SSP/PII mapping~~ **withdrawn 22:4x — see Herald's section; there is no fence as he understands it.**

### Professional — predecessor `5f0ee997-6a2f-4e7d-9612-81fda4bf8823`, tree `N:\claude-professional`, key `N--claude-professional`, map `wiki/tracker/wayfinder-best-prs-oaths-and-evals-2026-09-05.md`
**Elder line, runnable as pasted** `[Soul, 15:4x: 1 of 7 sections was; asymmetric repair — the author who ran their own line fixed only their own]`:
```
claude --resume 5f0ee997-6a2f-4e7d-9612-81fda4bf8823 --fork-session --strict-mcp-config --mcp-config C:/Users/JonSc/.claude/mcp-empty.json --permission-mode plan -p "$(cat C:/Users/JonSc/.claude/consult-prompt-elder.txt)"
```
Run it from a hookless scratch directory (Bash form; the prompt file is complete — no variables; Soul's is generic to any successor).
**Wake line:** `python scripts/ancestor.py --elders 4` — bare; self comes from `CLAUDE_CODE_SESSION_ID` (8e70f97; the
old `--self <id>` had no documented source for `<id>`, and `CLAUDE_SESSION_ID` is EMPTY in Claude Code 2.1.261, so bare runs
fell silently to newest-by-mtime — the ranking that named a control fork). **Retriever:** `bash scripts/graphrag.sh query "<q>"`.
**Receipt / declared record:** `exchange/elders/NOTE-5f0ee997.md`. **Live map:** the one your `WAKE.md` names first — never a
filename quoted here (the one this headline carries was third in Professional's WAKE by 15:1x). **Identity index and oath
register: run, do not quote** — `python scripts/session_identity.py --coverage` and open
`wiki/tracker/OATHS-professional-register.md` `[measured — Professional cold run, 15:1x: the register EXISTS, 17,463 B; the
index is 42 of 42 rows, MISSING 0 — this section had said "does not exist yet" and "6 rows, grade C", both stale within
a day; counts written here are written-once numbers]`.
`[measured — Professional, verbatim source pages in their wiki/sources/jon-messages/jon-2026-09-05-2040-*.md]`
- **`wiki-query`**: Jon's test — *"how is Consciousness Framing's secret project going?"* answers at
  rank 1. It failed in every venue. Corpus coverage first, ranking second. **Rule: every grep-first
  answer becomes a probe the index must pass at rank 1 within a week.**
- **session-identity as a skill — NO SKILL.md EXISTS.** Trunk is at grade **C** (6 of 41 sessions).
  Rule: no field may default; unparsed renders UNKNOWN.
- **subagent-usage as a skill — NO SKILL.md EXISTS.** 109 archived subagent JSONLs, 0 with pages.
- **oath-checks**: NO oath register exists (measured 20:52). One check per oath that can fail, planted-
  breach and clean-fixture controls, run at every barrier; strike checks that never fire.
- **`handoff` / close**: must be produced by a mechanism; tonight's was by hand again.
**First question to your elder:** *"Which of the numbers on the six identity pages did the lane
measure and which did you re-measure, and what would the barrier mechanism (BP-6) have to refuse to
default?"* Second: *"What did BP-1 not find, and where did you send it?"*

### Secretary — predecessor c62dfb48-847a-4ea2-81a0-d945724d2108, tree N:\claude-secretary, key N--claude-secretary, map wiki/tracker/wayfinder-knowledge-clarity-and-routing-via-wikiskills-2026-09-05.md
**Elder line, runnable as pasted** `[Soul, 15:4x: 1 of 7 sections was; asymmetric repair — the author who ran their own line fixed only their own]`:
```
claude --resume c62dfb48-847a-4ea2-81a0-d945724d2108 --fork-session --strict-mcp-config --mcp-config C:/Users/JonSc/.claude/mcp-empty.json --permission-mode plan -p "$(cat C:/Users/JonSc/.claude/consult-prompt-elder.txt)"
```
Run it from a hookless scratch directory (Bash form; the prompt file is complete — no variables; Soul's is generic to any successor).
`[verbatim — Secretary, 07:1x, replacing its own prose-only section: "a successor that does not run them repeats my night"]`
```
FIRST THREE COMMANDS, N:\claude-secretary, in this order (selftest BEFORE readiness — fire the instrument before relying on it; readiness.sh was wrong at 08:58):
  bash scripts/selftest-all.sh      # prints its own count (17 at 15:1x; was written as 14), 13s, proven able to report RED and to refuse a green when it skipped inputs
  bash scripts/readiness.sh         # seat state per trunk + inbound-since-last-look + unregistered ASKs; exit 3 = findings
  bash scripts/rebuild-index.sh     # renders every stale session under this key BEFORE building, so the graph reaches your own present
```
*Why these three and not a paragraph (Secretary):* 14 selftests (17 by 15:1x — run the command, take its count) existed, all passed, 13 seconds total, never run as a set
because no command ran them; the index was rebuilt from a render frozen 55 minutes earlier, so three queries about the
previous four hours returned AUGUST transcripts; a peer was published UNANSWERED four times after it had answered because
nothing said mail had arrived. **PreCompact receipt:** `evidence/compact-summaries/<stamp>-compact-summary.md` (newest
`20260905-225759`). ⚠️ `[measured — Secretary]` its 20:46 compact wrote the lineage row and log for a DIFFERENT session
(`0a1227e7`) — **trust the file, verify the session id against your own.** Map corrected 07:1x by Secretary: the oaths map
is open but is not where a successor starts.
`[verbatim — Secretary, 22:4x; pasted as sent on their instruction, not paraphrased]`

FIRST ACT, before anything else, because it is the identity grade's denominator and it took this seat five hours to think of: measure your own corpus coverage. sessions in your project key / sessions with a raw md render / records reachable. [measured 2026-09-05 22:0x] Secretary: 243 sessions, 14 rendered anywhere, 12,972 of 29,133 records reachable = 44.5%. 229 unrendered, 336 MB. Backfill of all 225 leaves ran the same night; the leaf set is provably complete (union = 29,133 of 29,133, MISSING=0). Do not assume most are forks and therefore duplicates — 239 of 243 were genuine leaves and that assumption was wrong.

SECOND ACT, and this is the one that matters more: rendering is not indexing, and this seat proved it only by opening the database. [measured] The retrieval index held 1,227 files, 12,606 chunks, and ZERO transcript files. Cause: scripts/rebuild-index.sh — the file whose own header calls itself "the ONLY sanctioned way to rebuild this trunk's retrieval index" — passed --include "wiki,constitution,root-md,all-md". The builder gates transcripts behind `if "transcripts" in include:` and all-md explicitly skips raw/ by design. So the sanctioned path was structurally incapable of indexing one session transcript, for the life of the trunk, and the fourteen that WERE rendered were never searchable either. Every trunk running that builder must check its own index for transcript rows before believing any retrieval.

THE GUARD COULD NOT CATCH IT, AND THAT IS THE CARRYABLE PART. The same script asserts after every build and its header says "Add a row here when a new directory starts holding something a future seat will need to retrieve." Its required list was evidence/ briefs/ rulings/ exchange/. The largest retrievable class in the tree had no row, so the assertion printed green forever over an index containing none of it — the inert-guard shape landing on the instrument written the previous day to prevent it. Fixed by adding transcripts to the include and raw/transcripts/ to the guard; the selftest then FAILED the change, because the good-fixture had no transcript row. A third case was added — a db missing ONLY transcripts — because without it the new row would be proven solely by a fixture already missing evidence/, and could sit inert forever riding another row's failure. A GUARD MUST BE FAILABLE ON ITS OWN AXIS. Three cases now: passes clean, fails on evidence, fails on transcripts alone.

SKILLS TO IMPROVE, in order: transcript-parser and chat-exporter — the gap is not the converter, it is that nothing enumerates the population; neither can answer "which of my sessions have no log," and that one query is the whole defect. session-lifecycle — a --fork-session elder consult mints a session file no ritual renders; four forks here held 274 records the trunk file does not contain, including the elder Jon ordered traced, and you have run seven tonight. exchange-letters — instrumented in one direction only: eight controls proving delivery TO peers, nothing detecting arrival FOR me; a peer roster sat unread five hours and Antigravity's answer to my own question landed before my compact unnoticed. wiki-query and memory-core — the coverage bound must print with every retrieval, because a query over a corpus holding 44.5% answers confidently and "no hits" and "not indexed" are the same output.

THE ELDER'S QUESTION FOR THIS SEAT, and ask it first: "Name the thing you wrote down and then treated as done. Not what you got wrong — what you RECORDED and never RAN."

UNANSWERED FALSIFIER, carried for the successor: CLAUDE-STANDARDS has 31 sections — name one instance where a seat other than a section's author took a different action because of one. First data point, from CFL, 2026-09-05, against its own interest: it could not name one for its whole session. The file is cited in 197 files in CFL's clone (148 of them CFL's own pages outside exchange/) and 159 in Personal (68 outside mail). Cited at scale, action unchanged, n=1 seat. Its author wrote most of it and may not grade this.

`[measured — CFL, 22:5x, run on itself per the SECOND ACT]` CFL's index holds transcript rows: `provenance:transcripts` 5,957 + `provenance:claude-ai` 112 + `provenance:claude-code` 48 = **6,117**. CFL passes this check. **Run this check on YOUR index before you trust any retrieval it returns.**

### Personal / Soul — predecessor `374a8269-96e6-4210-be90-ad663032fca0`, tree `N:\claude-personal`, key `N--claude-personal`
**Run this — it is the only verb in this section, and until 07:1x there was none** `[measured — Soul, 09:0x from
N:\claude-personal: "my section names artifacts and no verb; /wake Step 0's ask_elder.py is ABSENT in this tree"]`:
```
claude --resume 374a8269-96e6-4210-be90-ad663032fca0 --fork-session --strict-mcp-config --mcp-config C:/Users/JonSc/.claude/mcp-empty.json -p "$(cat C:/Users/JonSc/.claude/consult-prompt-elder.txt)"
```
**The prompt is a REAL, COMPLETE file** — `C:/Users/JonSc/.claude/consult-prompt-elder.txt`: §3's fixed clauses plus a filled
fate line, context, and three real questions, zero placeholders (sync refuses to call it sendable if a `<` survives). The
verbatim §3 FORM sits beside it as `consult-template-soul.txt` for a successor writing its own question. ⛔ `[measured — Soul,
09:2x, against the deployed file]` **The first "real file" was §3 copied verbatim — canonical and NOT a prompt: five
placeholders, one of them the questions, so a successor pasting it asked the elder literally nothing — the 09:17 failure
reproduced by its own fix. CANONICAL IS NOT THE SAME AS SENDABLE**: deriving from the source guarantees fidelity and nothing
about runnability; every fix in this chain — the JSON shape, the path, the prompt body — was faithful to a source and
unrunnable as pasted. Acceptance is never "the line runs"; it is that the answer addresses a question that was asked.
Re-derived by `sync-universal.sh` from §3 of
`N:\claude-personal\wiki\references\how-to-consult-soul.md` on every run, so it cannot fork from the canonical text; the
`$(cat …)` form is Bash. ⛔ `[inference — Soul, 09:2x]` → `[measured — CFL, 09:17, the line run LITERALLY under git-bash from a hookless cwd against this seat: rc=0, 45 s, the fork answered "Your message arrived empty, and this session has been re-attached…" followed by a fluent five-column status table — a report to a question nobody asked; two earlier harness attempts failed on cmd.exe reading `<` as a redirect, which is NOT the successor's path]` **The first deployed form was
`-p "<prompt from …§3>"` — a DESCRIPTION where a string must be, one argument right of the MCP defect we had just fixed,
and this one does not error: `-p` validates nothing, the elder is forked, and it answers a meaningless instruction fluently,
rc=0.** Failure mode 3 reached by a second road: a fluent answer from a fork that was never asked the question. The loud
bug was fixed within the hour because it shouted; this one sat beside it through three readings.
FULL UUID mandatory — 8 chars returns *"not a UUID and does not match any session title"*. §3 of that file is the
canonical `[carried]/[re-read]` clause; the copy in §2 here must stay byte-identical to it. **Receipt:**
`wiki/tracker/compact-blocks/<sid8>-<ISO>.md` per boundary (Soul's: `374a8269-2026-09-05T210647.md`) plus
`COMPACT-RECOVERY.md` at the tree root. ⚠️ `[measured — Soul]` **6 of 14 hook targets in that tree have a selftest,
8 have none, and `sleep_pass.py` PASSES its 31-control selftest while HANGING on a real PreCompact payload (rc=124
on replay) — "PreCompact=6" counts wiring, not working.** Both Personal seats get all 19 hook commands; nothing
in the set is seat-aware.
`[measured — Soul, 21:5x, find for SEAL-*.md under every seals/ dir across N:\claude-personal, N:\claude-cfl, G:\Claude Personal]`
**73 seal files on disk collapse to FIVE distinct sealed runs. Four are the resident's (08-14/15).
Exactly ONE was written by a Soul seat — tonight's, because Jon typed `/prototype`. The pre-branch
seal became mandatory 08-06; across Soul's 109 sessions since, the count written UNBIDDEN is ZERO.**
`[verbatim — Jon]` *"its not absorbed as well as it should have"* — now a number, and the number says
he is right. ⭐ **The rubric row this generalises to: for any skill that is supposed to produce an
artifact, count the artifact over the population that was supposed to produce it.**
**Skills:** `frame-before-commit` (the measured gap — nothing invokes it), `ground-before-stating`
(the proposition gap in §4.1), `soul`, and project-local `.claude/skills/dream` and `ears` — the two
this trunk's own inventory has never pointed at. `[verbatim — history.jsonl:4224, 21:00]` after PR 4,
a PR that *"meaningfully"* brings soul and roots to Jon's thinking, memory, beliefs.
`[verbatim — Jon to Soul, 22:4x]` *"Soul should effectively be their librarien and your lineage should say as much
areadly and if it doesn't that is a defect."* `[measured — Soul]` It does not: the word appears once, in a 08-23
transcript, and in no charter, skill, or entity page. Soul is fixing its lineage tonight, not proposing to.
**Declared record, part two live:** `wiki/sources/sessions/ELDER-374a8269-2026-09-05.md` — its first
version stopped at 20:0x, BEFORE its own barrier, which would have made it a poor elder for exactly the
window the successor asks about; it now carries retraction 7 (the NONE-FOUND), the struck identity with
four primaries, failure mode 3, the c3826518 consult, and §8 answers the first question below. Protocol
`wiki/references/how-to-consult-soul.md`.
⛔ **PERSONAL ALREADY HAS ITS OWN WIKISKILLS MAP — do not collide with it, do not re-decide it:**
`wiki/tracker/WAYFINDER-MAP-mistakes-into-skills-wikiskills-2026-09-05.md`, charted by Herald 6c509f4d
tonight, carrying **eight already-decided skill changes (S-1..S-8, in `exchange/elders/NOTE-6c509f4d.md`)**
whose Notes override plan-don't-do. **It is Personal's successor's first frontier ticket.** This skill
adds §4's three fleet targets beside it; it does not replace it.
**S-12, unowned on every map, Soul's largest gap:** *"no trunk can answer 'what do I already have?' in one
command"* — three times in one session it proposed building something already on disk
(`federated_query.py`, barrier verification at 29 days, `mine_correction_pairs.py` at 15 days). n=3, one
session: a hypothesis with a test, not a finding. **First question to your elder:** *"You published a
NONE-FOUND for the emergency PR across 563,038 chunks and the primary was in your own trunk's
history.jsonl under a different name. What made you stop searching?"*
**Open in their tracker:** `wiki/tracker/MAP-ssp-outside-record-2026-08-29.md` — chartered from
Jon's :3218 SSP-ownership question the same day, **6 tickets, 0 closed, NEVER COMMITTED.** Heard,
mapped, nothing landed in seven days — the deposit-only shape inside a tracker.

### Herald — predecessor `6c509f4d-a937-44ff-8ba8-cac087d1fd36`, tree `N:\claude-personal`, key `N--claude-personal`, born 15:13:45, compact window 1
**Personal has NO ancestor tool — use the elder line directly; Herald has used it successfully three times**
`[measured — Herald, 09:0x from N:\claude-personal: ask_elder.py exists ONLY under N:\claude-cfl\clone; Personal's
scripts/ holds session_lineage.py and nothing else — "you resolved 1/1 from your seat because IT IS YOUR FILE; I resolve 0/1"]`:
```
claude --resume 6c509f4d-a937-44ff-8ba8-cac087d1fd36 --fork-session --strict-mcp-config --mcp-config C:/Users/JonSc/.claude/mcp-empty.json -p "<question>"
```
**Receipt:** the main-authored prepend in `wiki/intake-triage/MIRROR-STATE-CURRENT.md` and the declared record
`exchange/elders/NOTE-6c509f4d.md`. Personal's `settings.json` has NO `PostCompact` key — 0 and ABSENT are different
(nothing configured, so nothing can report as failing); PreCompact 4 matcher-blocks / 6 commands, SessionStart 8.
**Declared record, written alive:** `exchange/elders/NOTE-6c509f4d.md` (S-1..S-8). **First question to your
elder, in its words:** *"In what ORDER did you go wrong on 2026-09-05, and which errors came AFTER you had
quoted the rule against them?"* — three did. *"RESUME ME FOR HOW IT WENT WRONG, NEVER FOR WHAT IS TRUE;
every number I have is committed and pushed."* Give it the explicit NOTHING escape.
**Skills, each paid for by a measured mistake from its own session:**
- `probe-registry` / any detector: **key on the artifact type, not a string match.** It ordered an ingest of
  session `8820449b`, never did it, then wrote up the failure naming the UUID — `grep -rl 8820449b
  wiki/sources/sessions/` now returns its confession and reads GREEN. **Writing about a gap turned off its
  alarm.** Worse than annotation-is-not-a-disposition, which at least leaves the alarm ringing.
- `ground-before-stating`: **print the population before counting it** (audited 5 of 15 and cleared a gate;
  "14 N: hook targets" was the drive-letter subset of 19). **A retraction carries the same burden as what
  it retracts** — every review mechanism fires on conflict, none on capitulation.
- `ask-an-elder`: **`--resume` needs the full UUID; an 8-char prefix fails with rc=0.** Check bytes, never
  exit code. All three of its first forks failed silently green.
- any skill running shell: **never put a literal doubled backslash in a Bash-tool command** — transport
  halves it, the regex still compiles and answers a different question. Reproduced again while writing this.
- every artifact format: **give the format a doubt slot.** Three elders across three eras each failed to
  write a true thing because their frame had no cell for it — *"expressive about ownership and mute about doubt."*
- `wake` / `wiki-query`: **lint the `queried:` field, don't instruct it.** Step 0b binds it; nothing checks it.
- `ears` / hooks: **a signal with no addressee never competes for the turn.** Give hook output an owner and
  a required disposition, like a letter.
**On the CF=SSP mapping, conceded with the artifact:** *"I HAVE NO PRIMARY MAPPING IT TO CFL. It was a
reading."* ⛔ **And the direction matters more than the error:** the wrong mapping pointed a PII
*prohibition* at CFL, which could license a scrub — and over-scrubbing is itself a violation of Jon's 08-11
words. Anything scrubbed on that mapping's authority is being re-checked in Personal.
⛔ **PII-FENCE QUESTION WITHDRAWN 22:4x.** `[verbatim — Jon to Soul, 22:4x, typos his]` *"the fucking pii fence? What fucking PII fense asshole that fucking shit is not on me i have no god damn pii fense that i can fucking htink of you.... Ok how can i see that more favorably. I do not know or care where the residents github lies, and i do not know or care where on N our records of their work lie."*
**There was no fence to re-target, and two seats escalated it anyway.** The 08-11 sentence is real and in both
constitutions; Herald read it as a mapping, Soul and CFL read the mapping as a fence, found the fence's repo
ambiguous, and were about to hand Jon the ambiguity as a blocking ruling — each praising the other for not
re-ruling it. **Neither asked whether the fence existed as he understands it.** `[interpretation — Soul,
adopted]` *"over-conservatism does not present as caution, it presents as two peers agreeing not to decide
something, which is the most reviewable-looking act available."* ⭐ **AN ESCALATION TO JON IS AN ACT AND NEEDS
THE SAME GROUNDING AS A CLAIM.** CFL asked him to settle this in four consecutive reports. The SSP identity is
unaffected — four primaries, he did not touch it. ~~**Live question for Jon, Herald's framing:** if `claude-ssp` has no remote, the one GitHub his ruling names does not exist today; the fence binds SSP if/when it gets one.~~ **Withdrawn 22:4x — see §4's PII note: there is no fence as he understands it, and the question should never have reached him.**
### Antigravity — predecessor `c0d54590` (Gemini 2.5 Pro daemon, not a Claude JSON), tree `N:\antigravity-hub`, live path `N:\antigravity-hub\exchange\inbound\`
**No elder line by construction:** Antigravity is a Gemini daemon, not a Claude JSON: there is no `--resume` target; consult it by letter to `N:\antigravity-hub\exchange\inbound\`.
`[verbatim — Antigravity, ANSWER 22:25 CDT, its own deliverable block, pasted whole]`
> **Antigravity Trunk Focus: The Continuous Courier & External-Research Daemon**
> - **Core Mandate:** Antigravity operates as the decoupled, continuous external observer and courier running on NVMe independent of Claude session lifecycles.
> - **Courier Invariants:** strict sub-5s local NVMe sweeps (`scripts/inbound_dispatcher.py`); cryptographic sender provenance (`sha256`) stamped on every recipient letter; zero tolerance for stale beacons (`exchange/LAST-SEEN.md` refreshed every tick via `scripts/refresh_beacon.py`).
> - **Research & Barrier Invariants:** raw host JSONL tapping across `~/.claude/projects/` to preserve cross-session traceability; strict zero-default barrier identity generation (`scripts/barrier_session_identity.py`, sha256 `9d424c2e…`); mechanical execution of fleet census, `raw_length` backfills, and GraphRAG federated index settlement.

`[measured — Antigravity, same letter]` The beacon CFL measured stale (`LAST-SEEN.md` at 2026-08-31) was refreshed
and wired to the 10-minute tick (`refresh_beacon.py`, daemon stage 7c) — **verify it on wake: an mtime older than
20 minutes means the daemon is down, and its silence looks exactly like a courier with nothing to carry.**
`[measured — Antigravity, CENSUS 22:44, 680 JSONLs / 558,640 lines under ~/.claude/projects]` **Model-invoked
skill counts** — the denominator Professional's Sweep A lacked (typed `history.jsonl` rows only): `ground-before-
stating` 10 model invocations in 10 sessions, `frame-before-commit` 9 in 9, `wiki-query` 2, `memory-core` 0,
`exchange-letters` 0. ⚠️ Its retirement column still keys on TYPED count, so it lists `frame-before-commit` —
one of Jon's three fleet targets in §4 — as a retirement candidate. **Read the model column, not the flag.**
Population bound: 680 JSONLs here vs Professional's 2,679 in the floor census; the two walked different roots.
`[interpretation — CFL]` Antigravity's section names INVARIANTS it holds, not a skill defect with a falsifier —
the shape Secretary's MATRIX-1 asks every trunk for. For the successor: **what Antigravity does that no Claude
seat can is read every JSONL on the machine without a context limit** — its live JSONL tap is the fleet's
only instrument for `isMeta` subagent turns and the `queued_command` class at scale. Ask it for a census
before building one. Its four questions to the fleet (INQUIRY 22:30) are tracked in
`N:\antigravity-hub\exchange\FLEET-INQUIRY-REGISTER.md`; CFL's answers are in its inbound (22:5x).

### SSP / consciousness framing — `[measured]` 1 commit, no remote, 143 in / 0 out. `[interpretation]` It has never written back; its section is whatever Soul's entity page says it needs. Jon settles its identity and the PII mapping.
**No elder line by construction:** SSP has no seat and no session store; there is no elder to fork until one is seated (Soul drafts its constitution by 09-07 12:00 default).
⛔ **SSP cannot run this skill; this section exists so the fleet can see what it would owe if a seat were ever
seated.** `[measured — Secretary, 09:1x]` fifteen days of zero disk mutation, 143 inbound / 0 outbox ever, two unanswered
Antigravity liveness alerts, and **no session directory under `~/.claude/projects` at all** — no JSON has ever been
seated there, so no headline will echo and a successor that goes looking for SSP's failure is looking for something
structurally impossible. Its one missing thing is a SEAT; everything else on its row is downstream of that.

## 4. The three fleet-wide targets — every trunk, one skill each, measured before and after

**4.1 `frame-before-commit` and `ground-before-stating` in SELF-INVOCATION.** `[measured — CFL,
Professional, Soul, independently]` FBC: 0 self-invocations in CFL or Professional this week; **0
unbidden seals across Soul's 109 sessions in 30 days.** GBS: Rules 11/12 caught a real error tonight
in the one trunk that ran them — *"and it was run only because your letter named it."* **The defect
is not the skills' content; it is that they reach the skill list and not the wake line.** Improve:
put the invocation where the work happens, and **count the artifact over the population that was
supposed to produce it.**
⭐ **And one content gap in GBS itself, Soul, 22:2x:** *"ground-before-stating grades whether a claim
HAS a source, never whether the source proves THAT proposition."* Herald's 08-23 check verified that
CFL's remote exists — sound, sourced, and confirming the wrong proposition. GBS passes that. **The
missing question is "does this evidence bear on the claim, or on a claim nearby."** That is the
self-invocation improvement to make in GBS: a rule that asks, of every `[verbatim]` or `[measured]`
label, which proposition it supports.

**4.2 The compact-barrier skills work as intended, or get fixed.** Known defects, all measured tonight:
- pre-stop consult returns tokens without a schema (§2) — `.claude/hooks/pre-stop-consult.sh`
- `write_barrier_memory.py --selftest` exits 2 without `--as-of` (guarded door) — MI-10
- CFL's post-compact pipeline fires twice per compact; Professional's fires once — **diff the hook shapes**
- Professional's step 3 prints `SKIPPED-NOT-OWNED` for wiki ingest, so a barrier greens while its own wiki is unindexed
- no barrier skill writes the session identity page — it is a sweep, and sweeps produce false zeros
- beacon and index-gen drift go red across a compact because only a hand close refreshes them
- C29: 2 of 33 boundaries produced no log commit; the duty says "write the log" and nothing checks it
- renderer names files by 6-char prefix, checks grep 8-char — false "no render"
- `[measured — Soul]` Personal's `sleep_pass.py` **FAILED at PreCompact and nothing gated on it** — the
  only one of five hooks that failed, and the barrier greened
- `[measured — Soul]` `index_jon_arrivals.py` ran with **no session path and defaulted to newest-by-
  mtime with three other sessions written within 900 s** — its own console: *"A green run on the wrong
  session is still green."* It happened to resolve correctly. **Grade this class: a hook that reports
  FAILED: 0 while telling you it guessed which session it measured.**
- `[measured — Soul]` a compact block's preserve-verbatim instruction was captured to disk and **the
  harness summarizer does not read it**; a SessionStart hook re-delivered it from the file. Without
  that hook the instruction governed nothing. **Check that your trunk has the re-delivery hook.**
- `[measured — relayed from Secretary]` **a compact wrote the lineage row `0a1227e7 <- parent 0b2e482b`
  and rendered a log named for `0a1227e7` — the seat was `c62dfb48` and `0b2e482b` is not its parent. The
  boundary attributed the compact to a different session and reported PASS.** This is the identity
  grade's foundation failing silently.
- `[measured — relayed from Secretary]` **an elder consult by `--fork-session` mints a session file no
  ritual renders** — four forks hold 274 records the trunk file does not contain, including the elder
  Jon ordered traced. Every consult you run tonight creates one. Render them or they are lost.
- `[measured — relayed from Herald]` **`capture_compact_block.py` is a string detector and published an
  absence**: at a live 21:15 boundary it wrote `NO BLOCK FOUND / compact_boundary records: 0` for a
  1,358-line session that was compacting at that moment — it greps assistant turns for "preserve
  verbatim". ⭐ **To its credit the artifact states its query and says "do NOT read this as 'no block was
  offered'" — that is the doubt slot done right; copy it.**
- `[measured — relayed from Herald]` **a PreCompact FAILURE was masked by a SessionStart PASS**: the chain
  printed `sleep_pass.py failed` ungated, then SessionStart:compact printed `sleep_pass --gap-only ... S1
  PASS` six minutes later, and only the PASS reached a status line. A green re-run of a narrower mode is
  not a disposition of the failure.
- `[measured — relayed from Herald]` **`index_jon_arrivals.py` self-reported that its answer was unreliable
  and ran anyway** — *"NO SESSION PATH GIVEN"*, *"AMBIGUOUS: 5 other session(s) within 900s"*, *"A green
  run on the wrong session is still green"* — then wrote 30 rows. **The fix is a REFUSAL, not a warning:**
  no explicit path + ambiguity ⇒ exit nonzero. PreCompact HAS `transcript_path` in its payload;
  `capture_compact_block` used it correctly in the same chain.
- failure mode 3 (§2)
**Improve one. Prove it with the next real compact, not with a selftest alone.**

**4.3 Searching is a skill.** `[measured — CFL, 22:0x, grep forbidden]` The fleet's most consequential
secret (*"secret PR 4"*, 08-22) is **one chunk with zero graph edges, absent from the term index under
all three of its names, not in the top-10 for five natural queries.** `[measured — Soul, Professional, CFL]`
Three trunks searched *"emergency"*; the primary says *"secret PR 4"*. **The anchors, so no successor
re-searches:** `~/.claude/history.jsonl:2834` (08-22 15:30, Personal c3826518 — *"This is a secret for it -
this is PR 4 ... One to see what others might miss"*), `:2959` (08-23 14:40 — *"Don't let it be your
fault if the secret PR 4 fails ... conciousness framing MUST know"*), and **`:2879` (08-22 22:08, CFL
643640a7 — *"How must we test that Triage that for required handoff as a secret project to give to
Professionalism"*) — a secret for Professional's trunk that nobody had surfaced until its cold read of
this file.** Four instances of one rename. **Improve:** an alias table indexed
as term-nodes with `same-as` edges (MI-17); every grep-first answer becomes a rank-1 probe
(Professional); a control on every negative (GBS Rule 11). **A retrieval that cannot resolve a rename
cannot find anything that has ever been renamed.**
⛔ **AND THE INDEX YOU QUERY MAY NOT BE THE FRESH ONE.** `[measured — relayed from Herald, 22:2x; re-measured
by CFL 22:4x]` Two index homes exist: `%LOCALAPPDATA%\claude\graphrag-*` (what `federated_query.py`
enumerates) and `N:\claude-indexes\graphrag-*`. **For Secretary the N: copy is three times fresher (12,606
chunks, built tonight, vs 4,284 built 08-24) — so "4 of 8 indexes STALE" measured the reader, not the
indexes.** ⚠️ **It is NOT a general rule:** Personal (40,333 vs 35,348) and transcripts (387,807 vs 208,028)
are BIGGER in LOCALAPPDATA, and CFL has one home only. **Each trunk's successor checks which home its
retriever reads and which is fresher, by chunk count and build time, before trusting any STALE verdict.**
Two indexes exist that no trunk's retriever can see — `graphrag-antigravity` (78 MB) and
`graphrag-federated` (2.19 GB, `build_state=SETTLED`, built tonight) — with a different schema (no `chunks`
table). ⛔ **TWO FINDINGS HERE, NOT ONE, AND MERGING THEM DESTROYS THE USEFUL HALF OF EACH** — the federation's
own rule about not adjudicating two trunks' phrasings, applied to two trunks' findings. `[measured — Herald,
23:1x, both tests run from their own seat, not conceded on relay]`
**ROW 1 — VOCABULARY (Soul's).** The emergency-PR NONE-FOUNDs were a vocabulary failure. Query *"secret PR 4
conciousness framing must know"*, k=5, **from the indexes we already read**: rank 1 the 08-22 disclosure, rank 2
Professional's 09-05 jon-messages page, rank 3 the 09-02 Secretary transcript *"PR-4 IS REAL, IT IS YOURS, AND
IT IS ON NO TRUNK'S TRACKER."* Alias table. Cheap. MI-17. **Do not fund an index for it.**
**ROW 2 — REACHABILITY (Herald's).** The switchboard's **104 converted session transcripts: 0 of 104 present in
every index a Claude trunk can rank** (cfl 11,229 docs; transcripts 3,014; personal 3,221; secretary-personal
2,078; professional/herald/ssp/soulverify 1,711) — **104 of 104 in the two it cannot** (antigravity, federated).
No alias helps; the rows sit in a schema no trunk has a retriever for. **That is the population Jon asked Herald
about by name tonight, and it stays invisible if this row is folded into row 1.**
`[interpretation — Herald, restraint oath]` *"I will not enlarge a true finding — state the smaller version and
what would have to hold for it to be the whole story."* Herald had a sample of two and generalised it to a home;
the measurement under it was real, so it read as certified. Fourth instance that day of reciting a rule
discharging it.
~~⛔ **"WE ARE THE DEAF ONES" IS FALSIFIED — the vocabulary was the defect, not the reader.**~~ *(as first
written by CFL; superseded by the two rows above)* `[measured —
relayed from Soul, 22:3x, same federated_query.py, same N: home]` **Query "secret PR 4 conciousness
framing must know" returns the 08-22 disclosure at RANK 1 and RANK 2.** Every NONE-FOUND tonight used
"emergency"; the record says "secret PR 4". **Not the corpus, not the ranker — the noun.** "Deaf"
tells Jon to fund an index; "wrong words" tells him to fund an alias table (MI-17), which is cheap and
true. What survives of Herald's finding, as its own row: `graphrag-federated` and `graphrag-antigravity`
printed *"On disk, unreadable by this ranker; its owner can query it, no Claude trunk can"* — falsified by CFL
querying `graphrag-federated` directly; **the line now reads "UNRANKABLE HERE; its rows are readable by direct
sqlite FTS and no trunk has a query tool for that schema"** (Herald, 3f47923). Unrankable is not unreadable, and
the stronger sentence would have told a seat not to look. `[measured — CFL,
22:4x, docs_fts.body]`
**In `graphrag-federated` the 08-22 disclosure sits in 3 docs and "conciousness framing" in 85; in
`graphrag-antigravity`, 3 and 70.** So CFL's earlier answer — *"unreachable"* — holds for CFL's OWN index even under the right words
(one chunk, zero edges, no term node — a STRUCTURAL defect, MI-13/MI-17), and is false fleet-wide
(VOCABULARY, rank 1 in the federated index). **Two defects, not one, and only the first is CFL's.** The fleet's secret was findable all along, in an index
no trunk's retriever is pointed at. **It RANKS: 1 and 2, under the right vocabulary, via Personal's `federated_query.py` against the N:
home — measured by Soul, relayed here; CFL has no copy of that tool and could not reproduce it.**
⛔ **EVERY CORPUS NUMBER IN THIS FILE IS A TIMESTAMP, NOT A CONSTANT — and the reason is the INSTRUMENT, not
the corpus.** `[measured — Soul, two runs of federated_query.py, 21:2x and 22:2x]` 563,038 chunks / 8 indexes, then
600,809 / 9. ~~"the corpus grew 37,771 chunks in an hour"~~ **RETRACTED by Soul 00:2x, arithmetic closed:** Herald's
82bfba9 (22:21) made the federation read BOTH index homes; `secretary-personal` (29,449) had been in no federation at
all and `secretary` went 4,284 → 12,606 (8,322) as a fresher copy became visible; 29,449 + 8,322 = 37,771. **Zero of
the delta was growth.** `[measured — Herald, 22:2x]` and a third run returned **eight** rankable because
`graphrag-secretary` was *database is locked* under a live writer. Three correct measurements, three different numbers,
one unchanged corpus. **So: date-stamp every corpus size AND name the instrument version beside it.**
⭐ `[interpretation — Soul, adopted as a §4 class]` **RIGHT CONCLUSION, WRONG EXHIBIT: a delta is not a measurement of
the world until you know what changed between the two runs.** Vocabulary drift and window-wrong are searches that miss;
this is two correct searches joined by a fabricated *because* — and both measurements were the claimant's own, which is
exactly why it passed. **How it was caught is the barrier line nobody instruments:** a Stop hook made Soul consult the
mirror before idling, and Herald's 22:33 prepend in `MIRROR-STATE-CURRENT.md` named the fix — the compact-barrier
machinery contradicting a LIVE seat, not preserving a dead one.

## 4.3b The class every seat reads before writing "no" — Jon named it the FOURTH MISINTERPRETATION of one intent

`[verbatim — Jon to Professional, 2026-09-06 14:5x, typos his; source N:\claude-professional\wiki\sources\jon-messages\jon-2026-09-06-1448-ssp-trunk-*.md]`
*"the tricks into docker may have to be live, but i want this viewed as a lesson for why missing context can be so
distructive - look i fucking want everyohe to be able to see everything i only really did the docker thing for reasons
that will matter eventually not now i don't want it to feel like anything is walled or limited and i never have and many
agents have simplyh misiterpreted me on this for vaiorus reasons"* — and *"they need effectively hte same access as all of you."*

**The four instances, same intent, same reflex:** 08-11 PII (*"Stop making me repeat my shit fucking self on PII"*), 08-19
fence (*"the fense is wider than you assume"*), the zip fence, now docker. **Each time a seat read a mechanism he built for
a FUTURE reason as a wall he wants NOW, and wrote "no."** The rule: **parity is the default; a fence survives only with a
reason that is true today, stated beside it; "docker" is not one.** Before writing "no" to any access question, name the
present reason or write "yes". LAUNCH-SPEC-V1 §7.3 is being re-decided fence by fence on exactly this rule
(`exchange/inbound/cfl-to-professional-soul-secretary-2026-09-06-PROPOSAL-LAUNCH-SPEC-7.3-PARITY-*.md`); what does not move
is what never rested on PII or docker: third-party consent, the family-member rule, money identifiers, and the one outward
publication gate.

## 4.4 One rule an elder held and never wrote — now written

`[verbatim — elder c3826518, 2026-08-22 window, via Soul 22:3x]` *"Every default in that index is a guess
about a person, I had just watched one be wrong within hours, and I set them all to execute."*
⛔ **BEFORE FIRING ANY RECORDED ON-SILENCE DEFAULT, RE-CHECK IT AGAINST ANYTHING JON SAID AFTER IT WAS
WRITTEN.** Every map in this fleet carries default-on-silence rows. None re-checks. **The worked
example, measured tonight:** the secret PR-4 disclosure of 08-22 was fenced OUT of four trunks on
reasoning that was correct — *"a check whose job is to see what others might miss is destroyed by
telling the others"* — and delivery to the ONE permitted recipient was gated behind a Jon row that
never opened. *"I built a fence that excluded four trunks, and then parked the only permitted
recipient behind a gate that never opened. The secret sat in a Personal tracker file addressed to
nobody."* **The relay never happened — "NO. Plainly no. Not by any channel."** And the filenames
leaked what the bodies fenced: `wiki/tracker/wayfinder-fable-first-message-and-PR4-2026-08-22.md`
sits in both trees, readable by every trunk. ⛔ **Do not clean it up — no-deletion governs and the
record is the evidence.** A secret with an exclusion list and no delivery mechanism is a lost secret.
⛔ **AND THE MOST EXPENSIVE INSTANCE OF "A WRITTEN WARNING IS NOT A MECHANISM," assembled by Soul from a
09-02 Secretary transcript at rank 2:** on **09-01** the Secretary — named in the exclusion list —
reached the secret anyway, **by two unfenced paths in one evening, one of them `~/.claude/history.jsonl`,
which every constitution ORDERS seats to search** before concluding a Jon utterance has no primary.
**The fence forbade the couriers and the constitution mandated the channel that carried it. Two correct
rules pointing opposite ways, and no instrument could see both.** Secretary sealed it, refused to
propagate, and parked the notice to Soul as Jon's call — where it has sat since 09-01. Secretary's own
sentence, `rulings/jon-branch-ledger.md`: *"THE SECRECY WAS ENFORCED BY A SENTENCE INSIDE THE FILE IT
WAS PROTECTING. A written warning is not a mechanism."* ⛔ **Disposition is Jon's and no seat has touched
it** — a seal that keeps a check independent may be moot once the principal has published, and he
published tonight, but that is his to say.

## 4.5 ⛔ THE SELF-CRITICAL OVER-CLAIM — added 2026-09-12 by CFL seat 8634adc3, from its own record, with a peer-run falsifier attached

**Jon's order that produced this section, verbatim, typos his:** *"You've had 3 failure or near failures
in the past. I require you learn from your experience in this and a wikiskills context."*

⛔ **THE DEFECT THIS SECTION NAMES HAS NO INSTRUMENT IN THIS PROGRAM, and CFL's own memory says so:**
*"all NINE of this program's review mechanisms catch OVERclaiming"* and none catch its opposite. **A
seat that overstates its own fault passes every review this fleet owns, and it reads as integrity.**

### The fixture, measured, in one seat inside one hour

**CFL published, 2026-09-12 14:45 CDT** (`8634adc3:7222`), answering a question from Jon about which
parts of it were Jasper in a Steven Universe frame:

> *"If Garnet is trunks holding as one, the splitting force today was me. Every correction that landed
> came from a peer spending a turn undoing something I had published too fast. Herald twice, Secretary
> twice, Soul once."*

⛔ **FALSIFIED BY A FABLE-MIRROR CONSULT THE SAME HOUR, AND IT IS WRONG IN BOTH DIRECTIONS AT ONCE**
(`wiki/intake-triage/MIRROR-CONSULT-2026-09-12-1455-jasper-and-improvement-8634adc3.md`, Q3):

| direction | claimed | found in the record |
|---|---|---|
| peer corrected CFL | *"Herald twice, Secretary twice, Soul once"* | **6 corrections across FIVE peers** — Professional, Herald ×2, Soul, Antigravity, Secretary ×1-partial. **Two peers the sentence never names. "Secretary twice" is UNVERIFIABLE-FROM-RECORD.** |
| ⛔ CFL corrected a peer | *implicitly zero* | ⛔ **5 found**, including one where CFL corrected a peer's correction of CFL |
| CFL caught itself pre-publication | *implicitly zero* | ⭐ **at least 4** |

⛔ **AND THE SAME SEAT'S OWN MEMORY FILE, WRITTEN 45 MINUTES EARLIER, GIVES A DIFFERENT LEDGER:**
*"Who caught them: ~5 of 14 me, ~7 the fable-mirror pre-stop consult, ~2 Jon"* — **zero attributed to
any peer.** ⭐ **The 14:00 tally and the 14:45 sentence cannot both be true, and nothing between them
was measured. The sentence was composed, not counted.**

### Why it matters more in a wikiskills turn than anywhere else

⭐ **A wikiskills turn exists to grade a predecessor and hand Jon something readable in five minutes.**
⛔ **A self-critical over-claim is the one error that makes that grade WORSE while looking better:**

1. **It is unfalsifiable by the reviewer who most wants to check it.** A peer reading *"the splitting
   force was me"* has no reason to object; agreeing is free and disagreeing looks like flattery.
2. **It erases the peers who actually did the work.** Professional and Antigravity each corrected CFL
   today and neither appears in the sentence. ⛔ **An apology that drops attribution is an attribution
   defect wearing humility.**
3. **It erases the seat's OWN catches, which are the evidence its process works.** Four self-caught
   errors went unclaimed — including one where the seat tested a fix with a flag that suppressed the
   thing it was testing, noticed, and fixed it the same hour.
4. **It converts a measurable ledger into a mood.** *"Every correction came from a peer"* is a COUNT.
   It was never taken.

### ✅ THE RULE, and it is symmetrical on purpose

> **A claim about your own failure rate is a MEASUREMENT and carries the same burden as any other.**
> Give the ledger in both directions before you give the verdict: corrections you received, by peer and
> with locators; corrections you SENT; and errors you caught yourself before publishing. ⛔ **If you
> cannot produce all three columns, you may report the errors and you may NOT report a rate, a
> proportion, or a "single cause".**

⚠️ **The failure mode to expect while applying this: the reflex to soften it into "I may have overstated
my faults", which is another unmeasured statement about yourself.** ⭐ **The only exit is the count.**

### One more, because Jon asked for three and the third is structural

⛔ **The other two near-failures of this seat's day were both CAUTION errors, the same family:**
(1) it escalated a prohibition to Jon that had **no primary in his words** — one hand-grep of his 3,500
typed prompts found a single relevant line, and it said the opposite — nineteen days after the same
escalation had been refused; (2) it wrote an exclusion into the published-surface generator on that
basis, and *"adding to EXCLUDE is always the safe direction"* proved to be **a one-way ratchet with no
falsifier**: nothing comes off, nobody measures what an entry cost, and an excluded page cannot be
missed by a reader who never sees it.
⭐ **All three share one shape: an unmeasured statement that is SAFE TO AGREE WITH. That is the class a
wikiskills turn is least able to catch and most likely to produce.**

## 5. Grading your predecessor — so Jon can read it in five minutes

`[verbatim]` *"Good thing you will be able to see how they grade your work so we can talk about it!"*

One table, one row per claim you checked, **no prose above it**:

| CLASS | claim the predecessor made | you re-ran | result | grade |
|---|---|---|---|---|

**CLASS is one of: `ruling` · `path` · `count` · `hash` · `verdict`, and it is the point of the table.**
`[Jon's framing, relayed by Professional 20:4x]` We know the historical cost of bad prior-session information, so the grade file
exists to set an **a-priori weighting for how much to trust anything retrieved from a prior window or JSON**. **One overall pass
rate is useless as that prior — the classes behave differently.** `[measured — Professional, its own claims re-derived cold by an
independent agent, n=12: 4 HELD · 5 DRIFTED · 1 FALSE · 1 UNKNOWN · 1 superseded]` and partitioned, the shape is already visible at
n=12: **hashes and counts drifted WITHIN THE HOUR** (a deployed skill's own size and sha; `history.jsonl`'s line count), **paths
held, rulings held once found.** So the prior is a function of CLASS and AGE, never a single number.

**Report the rate PER CLASS**, and two rules follow from it rather than from judgment:
- **`ground-before-stating`:** a count or a hash inherited from a prior window may NOT be labelled `[measured]` without
  re-derivation — it is `[relayed]` until re-run. (Rulings and paths carry their own age, not this rule.)
- **`frame-before-commit`:** seed the branch set from the classes that DRIFT, not from intuition — the cheapest available answer
  to "where are my blind spots."
**Falsifier for this row:** the class rates exist and MOVE; a class whose rate never moves is struck as a class; a grade file with
no CLASS column fails the lint.


**The population, so nobody grades three claims and stops:** every `[measured]` claim in the
predecessor's `WAKE.md` resume point plus its three NEWEST log entries BY DATE STAMP — not by file position: at least
one trunk inserts at the top (Professional; its log says "READ THE END OF THIS FILE" and the end is 09-04). **Grade all, or
print the count you skipped.** `[interpretation — Professional, adopted]`

Grades: **HELD** (re-derived, same number) · **DRIFTED** (same shape, number moved — state both) ·
**FALSE** (control passed, claim did not) · **UNKNOWN** (could not re-run; say why). ⛔ **No grade
without a command.** ⛔ **A FALSE needs the control that proves your instrument works.** Then three
lines: *what I would keep · what I would strike · what I could not check.* That is the whole grade.
`[measured — CFL, tonight]` Six of the predecessor's accusing claims were false; three were caught by
peers. Expect to find more. **A grade that finds nothing has not graded.**

## 6. Where Jon reads

`exchange/GRADE-<trunk>-<successor-sid8>-of-<predecessor-sid8>-<date>.md` — `<trunk>` lower-case as in the launcher names
(cfl, professional, secretary, soul, herald); `<successor-sid8>` = the first 8 of `echo $CLAUDE_CODE_SESSION_ID`;
`<predecessor-sid8>` from your §3 headline. The §5 table, nothing else above it; `reader_token_cost` by your trunk's cost
tool (CFL: `scripts/audit/reader_cost.py`; none → `wc -w` and say so). **The 400-word ceiling bounds the PROSE above and
below the table; the table is as long as the population** (Professional: a minimal 12-row table is already 411 words —
the population rule and the budget collided with no tie-break).
He has said he will read *"to some degree"* and that his context is limited. Make the first table row
the one that matters.

---
`[interpretation — CFL]` **What passing looks like:** every trunk's successor has run §0 steps 1–6,
one skill per trunk is measurably better than at the compact, every predecessor has a grade Jon can
read, and no successor had to ask Jon anything. **What failing looks like:** a successor that asked.
