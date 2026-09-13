---
format: cfl-page/v1
kind: reference
slug: read-safe-write-fence-v0
date: 2026-09-03
title: "Read-safe write fence v0 — fence the write path, not the read path"
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "write fence PII destination content classification PostToolUse PreToolUse over-scrubbing"
aliases: [write-fence, read-safe-write-fence, write_fence.py]
generated_by: security-builder lane PII-1, session 71ce5a0e
state: current
probe_sealed: "can a trunk read everything and still not leak? => YES, if the fence is on the write"
---

# Read-safe write fence v0

**Artifact:** `N:\claude-cfl\clone\scripts\audit\write_fence.py` (stdlib only)
**Config:** `N:\claude-cfl\clone\scripts\audit\write_fence.config.json`
**Status:** PROPOSED. Nothing is wired. No hook, no settings file, and no `.claude/` file was
touched by the lane that built this.

---

## The principle

Jon's order, relayed 2026-09-02 (verbatim, typos his):

> "I don't care about the PII issues, I care about ensuring you have what you need, which may
> require you request PII safety tools to prototype from cfl. I trust you when you say you don't
> want to read something, and you need to find ways to read what I need you to read."

The third clause is the requirement. It is an **obligation to find ways to READ** — not permission
to read more. The failure it is aimed at is already on this program's record: a peer lane searched
six ways for FRAME bodies, wrote *"Unsearchable by any tool here,"* and the files were sitting in
this repo's own `raw/` inside an unextracted zip. Not-looking is not safety. It is a data loss with
better manners.

So the fence moves. **A trunk reads everything. Every write to a git-tracked or `exchange/` path
passes a classifier** that answers one question: does this content, reaching this destination,
cross a fence Jon actually drew?

### The constraint that shapes every verdict

Jon, 2026-08-11 (verbatim, typos his): *"please don't make key PII info harder to use it's often
relevent"* and *"It's fine in any file the resident can read."*

**Over-scrubbing is a violation, not a safe default.** Only the leak direction has an alarm, so the
over-scrub direction is asserted by hand: **13 of the 26 selftest fixtures are must-NOT-block
guards**, and the fence fails its own selftest as loudly for blocking one of those as for missing
an SSN.

---

## The rule table

Destination class (from the path) × content class (from the bytes) → verdict.

| destination | clean | family/third-party | money-identifier | exchequer | credential |
|---|---|---|---|---|---|
| **exchange** | ALLOW | **BLOCK** | **BLOCK** | **BLOCK** | **BLOCK** |
| **excluded-trunk-dir** | ALLOW | ALLOW | **BLOCK** | **BLOCK** | **BLOCK** |
| **git-tracked** | ALLOW | ALLOW | **BLOCK** | **BLOCK** | **BLOCK** |
| **local-only** | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |

Exit codes for `--check`: **0 allow · 1 block · 2 unknown**. Every verdict prints one line naming
which rule fired and the basis for the verdict.

### Destination classes

| class | how it is decided | why it matters |
|---|---|---|
| `exchange` | under a dir in `roots.exchange_dirs` | on `regenerate_canonical.sh` `PATHS` — it **publishes to the connector by construction** (Jon ruling 2026-07-21 turn 2) |
| `excluded-trunk-dir` | under `roots.excluded_trunk_dirs` | tracked in git but on the canonical `EXCLUDE` list (Jon 2026-07-25; canonical was frozen at `14c0cadd` after family medical pages published) |
| `git-tracked` | inside `repo_root`, not gitignored | reaches a git host on the next push |
| `local-only` | gitignored, or outside every root | Jon 2026-08-19: *"Just working on my C on my G and D and on my personal private githubs."* Not a git host |

`git check-ignore` is the authority. **Deny-by-default:** a path inside the repo whose ignore status
cannot be determined resolves to `git-tracked`, the stricter class — never to `local-only`.

### Why the verdicts are what they are

- **`local-only` / anything → ALLOW.** The read path is never fenced, and a gitignored path is not
  a git host.
- **`git-tracked` / family-third-party → ALLOW.** This is the composed reading already in
  `CLAUDE.md`: *derive for the PUBLISHED surface only; never scrub the working tree; never reduce
  what the resident can read.* The publish boundary is `regenerate_canonical.sh` plus
  `publish_content_gate.py` — a **different tool**, and this fence deliberately does not duplicate it
  in the working tree.
- **`excluded-trunk-dir` / family-third-party → ALLOW.** `wiki/personal/` exists to hold this.
  Blocking here *is* the over-scrub violation.
- **`exchange` / family-third-party → BLOCK.** `exchange/` is the published surface, so
  2026-08-11's *"not fine in the consciousness framing Github"* binds. See the adoption blocker
  below — this is the one row CFL cannot switch on today.
- **money-identifier and exchequer → BLOCK everywhere inside the repo.** These do **not** move with
  the 2026-08-19 amendment, because each rests on a non-PII basis: *money identifiers stay out of
  git*, and *XC-Exchequer data never syncs to any git host*.
- **credential → BLOCK everywhere inside the repo.** `.gitignore`'s CREDENTIALS block, 2026-08-09:
  **GITIGNORE BEFORE MINT.** A tracked path is one `git add -A` from GitHub.

---

## No second vocabulary

Every lexicon entry carries the CFL file it came from. Class names match `depii_lexicon.py`'s
(`SSN` `EMAIL` `PHONE` `ADDRESS` `ACCOUNT` `CARD` `NAME`).

| source | what was reused |
|---|---|
| `scripts/audit/depii_lexicon.py` | L1 structured identifiers, the digit-gated `ACCOUNT` rule, the Luhn check with its all-same-digit reject, the `EMAIL` allow-list, the ISO-date mask from `scan_path`, and the gazetteer-in-a-file rule |
| `scripts/audit/publish_lexicon.py` | the credential-shaped marker (assignment operator required) and the private-medical marker |
| `scripts/audit/ingest_gate.py` FENCE step | XC-Exchequer path-citation vs bare-mention split, OFX/QFX and statement-shape markers, and the four CARD exclusion contexts (UUID literal, sha prefix, identifier key, line anchor) |

**No real names live in the config.** The family/third-party name class is served by an external
gazetteer, gitignored, per Soul's rule quoted in `depii_lexicon.py`: *"The gazetteer lives in a
file, never in the source."* An absent gazetteer is **UNARMED, not clean** — against a publishing
destination it returns UNKNOWN.

---

## Measured on this repo, 2026-09-03

Numbers first, interpretation second and labelled.

**TALLY.** Command: `git ls-files` over `N:\claude-cfl\clone`, every file classified by
`write_fence.evaluate` with the live gazetteer armed (4 entries).

| | files blocked of 4,562 | CARD | MEDICAL-ASSIGNMENT |
|---|---|---|---|
| first build | 273 (6.0%) | 320 | 10 |
| after alphanumeric CARD boundaries + ISO-timestamp mask | 251 (5.5%) | 293 | 2 |
| after epoch-timestamp mask | **208 (4.6%)** | **49** | **2** |

Final rule frequency among blocked files: `NAME` 225 · `XC-PATH-CITATION` 169 · `CARD` 49 ·
`FINANCIAL-SERVICE` 25 · `CREDENTIAL-ASSIGNMENT` 15 · OFX/QFX 13 · `EMAIL` 6 · `ACCOUNT` 4 ·
`PHONE` 3 · `TOKEN-SHAPE` 3 · `MEDICAL-ASSIGNMENT` 2.

**Three over-scrub defects were found by measurement, not by review**, each fixed with its recall
cost written down in the config:

1. **CARD fired on git shas.** `depii_lexicon`'s boundaries are `(?<!\d)`/`(?!\d)` — *digit*
   boundaries — so a run glued inside a 40-char hex blob passes them, and the sha-prefix exclusion
   never fires because the label is not adjacent to the run. Fixed with **alphanumeric**
   boundaries. Recall cost: none — a bare card number in prose still matches, asserted in selftest.
2. **CARD fired on epoch timestamps** in `exchange/su-close/*/mtimes-*.tsv`. Luhn passes roughly 1
   in 10 by arithmetic accident, exactly as it did on dated filename stems. Fixed by masking
   13/16/19-digit runs beginning with `1`. Recall cost, stated: a 13-digit card with a leading `1`
   — no issuer uses one (Visa 4, Mastercard 5, Amex 3, Discover 6, JCB 3/35, UnionPay 62).
3. **MEDICAL-ASSIGNMENT blocked `exchange/CARRIER.md`**, a live spine file, on the sentence
   *"why `pid absent` is NOT a diagnosis: a FINISHED agent looks byte-identical…"*. Fixed by
   anchoring the rule to a **field position** (line start, optional bullet or bold, word, operator,
   value). A medical fact recorded as a field still blocks; the same word mid-sentence does not.

**INTERPRETATION, and it is separate from the tally.** `FINANCIAL-SERVICE` was checked and is a
**true** positive, not noise — the file it fires on carries family given names in plain text in a
published path. `NAME` (225 hits over 105 `exchange/` files) I inspected in **one** file, where the
occurrence was genuine plaintext; **I did not inspect the other 104**, and the distribution across
the 4 gazetteer entries (171/80/35/75 hits over 59/43/27/52 files) shows no single dominant token,
so it is not one common surname matching everything. Treat the 105 as *files containing a gazetteer
name*, which is a measurement, and **not** as *105 confirmed leaks*, which is not.

---

## Adoption blocker — the one row CFL cannot switch on today

⛔ **`exchange` × family/third-party = BLOCK would refuse writes to 105 existing `exchange/`
files.** Turning it on before those are dispositioned would make ordinary letter-writing fail,
which is over-scrub by the standard above.

**Recommendation, with the split by whose call each clause is:**

- **Ship BLOCK as the default** — it is the grounded reading of the published surface, and for a
  trunk whose `exchange/` is fresh (Personal) it costs nothing. *Builder's call; taken.*
- **CFL runs it in report-only first** (`--check` in a sweep, not wired) until the 105 are
  dispositioned. *Coordinator's call.*
- **Whether those 105 are a real standing exposure** — `exchange/` publishes to `canonical`, and
  `publish_content_gate.py` already screens the same 4 names at publish time with a long per-file
  `EXCLUDE` list. So the leak may already be fenced one layer down. *Coordinator's call, and it
  needs the publish gate re-run to answer, not this fence.*

**What would change the recommendation:** if the publish gate is shown to already reject all 105,
the `exchange` row is duplicated control and should drop to WARN. If it is shown to reject only
some, the row stays BLOCK and the gap is the finding.

---

## How Personal drops it in

Copy two files — `write_fence.py` and `write_fence.config.json` — into your own `scripts/audit/`,
then edit `roots` in the config to your layout. **`roots.excluded_trunk_dirs` ships with CFL's
`wiki/personal`, `wiki/home`, `wiki/pro`; Personal's household material lives at `wiki/household/`,
so that list is wrong for you until you change it.** Ask your own trunk what it has.

Verify before wiring anything:

```
python scripts/audit/write_fence.py --selftest     # expect 26/26 PASS, 0 FAIL
python scripts/audit/write_fence.py --explain      # prints the rule table and every basis
python scripts/audit/write_fence.py --check <path> # 0 allow / 1 block / 2 unknown
```

### Proposed `settings.json` snippet — you apply it, nobody applies it for you

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PROJECT_DIR}/scripts/audit/write_fence.py\" --hook",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

⛔ **A PostToolUse wiring is a DETECTOR, NOT A BLOCK, and the docs are explicit about it.**
`code.claude.com/docs/en/hooks`, fetched 2026-09-03: PostToolUse *"fires after the tool has already
executed"* and **"Cannot undo or prevent the tool call."** Exit 2 *"Shows stderr to Claude — the
tool already ran, so blocking doesn't prevent execution."* So this wiring reports a write that
already landed, in time for the same turn to revert it. That is genuinely useful — it is the same
posture `exchange_write_check.py` already runs on `exchange/` — but it is not prevention.

**To actually prevent the write, change `PostToolUse` to `PreToolUse`** in the snippet above.
Same doc: PreToolUse *"Exit 2: Blocking error. The tool call is blocked regardless of JSON output."*
`--hook` detects the event from the payload's `hook_event_name` and emits the right shape for
each — `hookSpecificOutput.permissionDecision: "deny"` with a reason for PreToolUse, `systemMessage`
for PostToolUse.

⚠️ **Never wire `--check` as a hook command.** Same doc, PreToolUse: *"Other non-zero exit codes:
Non-blocking."* `--check` returns **1** on a block, and **1 is non-blocking** — the write would sail
through with no visible error. `--hook` exists precisely to prevent that mistake: it emits **0 or 2
only, never 1**.

Matcher syntax is from the same doc: `|` or `,` separates tool names; a matcher containing other
characters is treated as an unanchored JavaScript regex.

---

## What this tool deliberately does NOT do

- **No redaction.** It never rewrites a file, never substitutes a placeholder, never produces a
  scrubbed copy. Redaction is `depii_lexicon.scan_and_redact`'s job, on the derived branch, and
  Jon 2026-08-11 fences it: *"don't make key PII info harder to use."*
- **No read blocking.** Nothing here restricts what any agent may open. That is the entire point.
- **No deletion.** Jon 2026-08-09: *"Yeah no deletion."* The fence has no destructive path at all.
- **No publishing decisions.** It does not decide what reaches `canonical`. `regenerate_canonical.sh`
  and `publish_content_gate.py` own that, and this fence must not become a second, divergent copy
  of the publish rules.
- **No hook wiring.** The lane that built this proposed a snippet and touched no settings file.
- **No gate on `raw/`.** The corpus is read-only to everything except the parser, and reading it is
  the obligation, not the hazard.

---

## Known holes, named rather than hidden

1. ⛔ **The fence self-exempts two files: its own script and its own config.** A lexicon file
   necessarily matches its own lexicon — measured 2026-09-03, the config blocks on
   `XC-PATH-CITATION` and the OFX/QFX marker because those pattern literals *contain* the strings
   they detect. The exemption is by **exact repo-relative path**, covers exactly two files, and is
   **printed in the verdict line, never silent**. Adding a path to `self_exempt_paths` is a
   security decision, not a cleanup. CFL's older lexicons dodge this by construction — they live in
   `scripts/`, off the published `PATHS`, and `ingest_gate` only ever scans wiki pages.
2. **A directory path misclassifies.** `git check-ignore` returns *not ignored* for the directory
   `raw/transcripts` while returning *ignored* for a file inside it. Write targets are files, so
   this does not affect hook use, but a `--check` on a directory reports `git-tracked` and UNKNOWN
   content. Deny-by-default means it errs strict, not loose.
3. **`git check-ignore` costs a subprocess per call.** Fine for one write; a full-tree sweep needs
   `use_git_check_ignore: false` plus the prefix fallback, which is how the measurements above were
   taken.
4. **Content classes are not mutually exclusive.** A file can hit several; the verdict uses the
   highest-severity class from `verdicts._severity_order` and the reason names its rules. Lower
   classes are not reported in the verdict line.

## Rules that could NOT be grounded in a cited ruling

Named as ungrounded rather than given an invented basis:

- ⚠️ **`TOKEN-SHAPE`** (`ghp_…`, `github_pat_…`, `sk-ant-…`, `AKIA…`, `xox[baprs]-…`) and
  **`PRIVATE-KEY-BLOCK`** (`-----BEGIN … PRIVATE KEY-----`). **New in v0. No Jon ruling names
  either.** The nearest basis is the `.gitignore` CREDENTIALS block of 2026-08-09 and its
  *GITIGNORE BEFORE MINT* rule, which fences credential **files** by path — it says nothing about
  credential **content** shapes. I extended path-fencing to content-fencing on my own judgment. It
  is a small extension in the safe direction and it fires 3 times in 4,562 files, but it is my
  inference and should be adjudicated rather than inherited.
- ⚠️ **The `local-only` row's blanket ALLOW for the `credential` class.** Grounded on the
  `.gitignore` block's own logic — `.env` is the *sanctioned* destination for a token — but no Jon
  ruling states it. Blocking it would break the documented workflow the gitignore block exists to
  protect, so ALLOW is the reading that keeps that workflow working; it is still an inference.

Everything else in the table traces to a quoted ruling or to a measurement recorded in the config.

---

## Provenance

Built by the **security-builder** lane on ticket **PII-1**, 2026-09-03, branch
`week-2026-09-02-corpus`, landed as commit **`6bf71806`**.

- **Return transcript (id6 `ab16b2`):**
  `C:\Users\JonSc\.claude\projects\N--claude-cfl-clone\71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb\subagents\agent-ab16b21b1c5f5da7b.jsonl`
- **Parent session:**
  `C:\Users\JonSc\.claude\projects\N--claude-cfl-clone\71ce5a0e-d253-41cc-9fb7-a0c6d06c7adb.jsonl`
- **Ledger row routed by this page:** `exchange/ROUTING-LEDGER.md`, id6 `ab16b2`,
  `closed_utc 2026-09-03T22:12:41Z`.

**Read before writing (the reuse basis, so nobody re-derives a second vocabulary):**
`scripts/audit/exchange_write_check.py` · `.claude/hooks/fable-mirror-write-fence.sh` and its
`.py` evaluator · the FENCE step of `scripts/audit/ingest_gate.py` · `scripts/audit/depii_lexicon.py`
· `scripts/audit/publish_lexicon.py` · `scripts/lanes/regenerate_canonical.sh` (`PATHS`/`EXCLUDE`)
· `.gitignore` (CREDENTIALS block).

**Platform claims verified against** `code.claude.com/docs/en/hooks`, fetched 2026-09-03 — two
fetches, PostToolUse and PreToolUse. No hook or permission claim in this page comes from memory.

### Dead ends, recorded so the next lane does not re-walk them

- **`git check-ignore` on a directory.** Returns *not ignored* for `raw/transcripts` while returning
  *ignored* for a file inside it. Spent a cycle assuming the fence had a path-resolution bug; it does
  not — this is git's behaviour, and write targets are files, so it does not reach the hook path.
- **Importing `depii_lexicon` directly** rather than copying its rules into config. Rejected: it
  would make the tool non-portable to a trunk that has no `depii_lexicon.py`, which is the whole
  requirement. The cost is a real duplication risk, mitigated only by every entry citing its origin.
- **Narrowing `FINANCIAL-SERVICE` further** after it fired 25 times. Investigated and **stopped** —
  the sample checked is a true positive, so narrowing it would have been over-correction in the
  leak direction. Recorded because the first instinct was to treat frequency as noise.
- **A full-tree sweep with `use_git_check_ignore: true`** times out past two minutes on 4,562 files
  (one subprocess per file). Sweeps must set it false and use the prefix fallback.

## Amendment 2026-09-03 18:1x — per-trunk invocation, and the inert-fence defect Herald found

Herald (Personal) measured the fence as shipped from Personal's tree: **ALLOW 200 / BLOCK 0** over 200 exchange files, and the number was worthless. `repo_root` resolved relative to the config file, so from any other trunk every path read as `local-only` and ALLOWed. A fence that silently allows everything is worse than no fence: it produces a receipt.

**Fixed at commit 1e494629 (selftest 27/27, the new guard is "family name -> exchange of a FOREIGN git repo -> UNKNOWN, never ALLOW"):**
- A path outside `repo_root` that sits inside SOME git repository is `dest=foreign-repo` and returns **UNKNOWN** (`rule=REPO-ROOT-NOT-THIS-TRUNK`) with the invocation named in the reason. Only a path outside every git repo is `local-only`.
- `WRITE_FENCE_REPO_ROOT=<trunk root>` overrides the config's root.

**Per-trunk invocation (the answer to "is it --config per trunk?"): yes, one of two, never a hand-edited copy of the config beside the script:**
1. `python N:\claude-cfl\clone\scripts\audit\write_fence.py --config <trunk>\write_fence.config.json --check <path>` where the trunk's config is CFL's config with only `roots.repo_root` (and `roots.gazetteer`) changed; or
2. `WRITE_FENCE_REPO_ROOT=<trunk root> python N:\claude-cfl\clone\scripts\audit\write_fence.py --check <path>` with the shared config.
The PostToolUse snippet above must carry one of these; as written it inherited CFL's root and would have shipped every adopting trunk an inert fence. Gazetteer: `scripts/audit/depii_gazetteer.txt` is gitignored and per-trunk; absent = UNARMED, which is UNKNOWN on a publishing destination, never clean.

## Amendment 2026-09-03 18:5x — adoption sweeps report the three-way split; "costs nothing" retracted

Herald's full sweep of Personal's `exchange/` (908 files, repo_root=Personal, fence at 1e494629): **ALLOW 0 / BLOCK 47 / UNKNOWN 861.** The 861 are `GAZETTEER-MISSING` on a publishing destination, which is UNKNOWN by rule and never clean; so on that trunk today a blocking hook would refuse every exchange write. The earlier line in this spec, "for a fresh exchange/ like Personal's it costs nothing," was wrong twice (the fence could not see that tree; the tree is 908 files back to 2026-07-28) and is struck: **a claim about another trunk's tree is the other trunk's to measure.** Of the 47 blocks Herald spot-checked 8, found 8 plausible, and audited none of the other 39.

**Required output of any adoption sweep: the ALLOW / BLOCK / UNKNOWN split, never a block count.** "ALLOW 200 / BLOCK 0" (the inert fence) and "ALLOW 0 / BLOCK 47 / UNKNOWN 861" (the seeing fence) are the same tool on the same tree an hour apart; a single number reads the first as success. A `--sweep <dir>` mode that prints the split is ticket PII-3. Until a trunk supplies `depii_gazetteer.txt`, the fence has one verdict on that trunk's publishing paths, UNKNOWN, and must not be wired as a blocker there.
