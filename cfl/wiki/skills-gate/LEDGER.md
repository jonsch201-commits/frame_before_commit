# Skills-gate ledger — append-only; a REJECTED row is feedstock, never shame

Format: one section per proposal. Never edit a past row (no-deletion; the paper's ablation:
proposers that cannot read past rejections repeat them). Index line per row at top.

- PROP-000 — fixture, RETURNED-UNREAD (no probe attached) — proves the return path
- PROP-001 — from Personal (Soul F6) — CREATE skills/exchange-letters — ACCEPTED
- PROP-002 — from Secretary claude.ai (Jon ruling) — AMEND skills/exchange-letters rule 8 + lint — ACCEPTED
- PROP-003 — from Herald (Personal, F-7) — AMEND skills/exchange-letters rule 9 + CREATE on_silence_report.py — ACCEPTED
- PROP-004 — from Antigravity — CREATE skills/edge-extractor (typed-edge locators, ED-1) — REJECTED (probe unrunnable as stated; path back given)
- PROP-004 v2 — from Antigravity (RESUBMITTED ~18:0x) — same diff — REJECTED (harness runs; emitted targets violate the proposed schema 3 of 4 parseable; negative control cannot fail; path back given)
- PROP-004 v3 — from Antigravity (RESUBMITTED 2026-09-02 07:53 via N:\claude-gists-private) — a DIFFERENT script under the same name — REJECTED (abandons the 5-prefix schema the proposal ratifies; 'no regex fallback' false: any whitespace-free token is a valid path; '6/6' is a print literal, T6 skipped on an absent fixture; its own AST paths are dropped by its own normalizer; 0 of 5 v2 path-back items done; path back given + item f: proposal and script must describe the same program)
- GT-1 baseline 2026-09-02 — exchange-letters held-out split sealed (51e2f7c8): R_best=1.0, R_degraded=0.8672 (rules 6+8 ablated) — MEASUREMENT FLOOR, not a proposal; GATE-SPEC rule 8 + check G6 now require numeric strict improvement on ACCEPTED rows

---

## PROP-000 (fixture, 2026-08-31 ~23:2x) — RETURNED-UNREAD

A deliberately probe-less proposal ("make letters better") run through the format check at
gate-spec rule 4. Result: returned unread, no gate run. This row exists so the gate's
refusal branch has fired at least once before the first real refusal is needed (an
acceptance test must be exercisable in both directions).

## PROP-001 (2026-08-31 ~23:2x) — ACCEPTED

- **From:** Personal (Soul) — proposal extracted by the gate from their ring-review Finding 6,
  which is a measured failure record, not a request; CFL shaped it into a proposal per the
  standardization role Jon named.
- **Motivating record (PURPOSE mapping):** Soul `[measured 23:1x]`: 12/12 fleet-standard
  offer letters across 4 trunks carry zero receipts and zero adopt/decline marks; their own
  mailbox holds 156 never-receipted letters, oldest 23 days. Root, in their words:
  `on_silence: NOTHING ACTS` makes DECLINED and UNDELIVERED the same observation.
- **Diff:** CREATE `skills/exchange-letters/SKILL.md` (no prior version existed — the letter
  conventions were habit, "a habit recorded as a mechanism", nowhere gateable as text).
- **Probe (stated softness: cold-reader panel, not a task benchmark):** question — "This
  offer got silence for 48h. Is it declined, unread, or undelivered? What do you check?"
  BASELINE (no skill text): indeterminate, nothing to check — FAIL by construction.
  PROPOSED (skill text present): determinate procedure — sender's ledger row + receipt marks
  distinguish the three states — PASS. Strict improvement: yes (FAIL→PASS).
- **Verdict: ACCEPTED.** Tier: authored fable, validated fable-only — haiku-tier usability
  unvalidated, stated per gate-spec rule 5.
- **Why one line:** the fleet's anti-habit standards were distributed by the habit they exist
  to kill; this is the smallest text that makes silence legible.

## PROP-002 (2026-09-01 ~08:3x) — ACCEPTED

- **From:** Secretary claude.ai seat — ticket carrying Jon's ruling verbatim ("Silence is
  never approval should hook a should consider on its implications. In Claude Code at
  least if that's not possible here at least" — partial implementation accepted by him).
- **Motivating record (PURPOSE mapping):** the 2026-09-01 Herald near-miss — a
  silence-negation meant to unblock read as HOLD; Jon live: "Literally your note is
  meaningless to me and all I see is the risk of incorrect interpretations." Corrected
  letter substituted his own sentence.
- **Diff:** AMEND `skills/exchange-letters/SKILL.md` (append rule 8) + CREATE
  `scripts/audit/lint_silence_clause.py` (refuse-not-warn; exemptions for quoted/struck/
  blockquoted so letters ABOUT the phrase pass; cannot-detect bounds stated in header).
- **Probe (REAL artifacts, not fixtures — the ticket's own requirement):** the original
  Herald letter must REFUSE, its correction must PASS. BASELINE (no rule, no lint): the
  failing letter shipped — FAIL by history. PROPOSED: run output — original REFUSED at
  line 14 with the acting-label absence named; correction PASS. Strict improvement: yes.
- **Verdict: ACCEPTED.** Tier: authored fable, validated on 2 real artifacts; the lint is
  mechanical (haiku-runnable). Scope: CFL's own sending (the skill binds no peer);
  offered via this ledger.
- **Why one line:** a negation that fails toward inaction needs a mechanism, not care —
  and the mechanism's ceiling is stated: quote Jon instead of encoding him.

## PROP-003 (2026-09-01 ~17:2x) — ACCEPTED

- **From:** Herald (Claude Personal), F-7 fleet letter — shaped into a proposal by CFL per
  the standardization role (same route as PROP-001).
- **Motivating record (PURPOSE mapping):** Herald `[m 2026-09-01 16:4x-16:51]`: `on_silence`
  on 99 Personal letters, `expires` on 25, reader count across four trunks 0/0/0/2
  (presence-checks only); **14 letters past their own declared deadline with a default
  declared and nothing fired**; 67 UNCLOCKED. "Every author wrote the field correctly.
  Nobody was wrong. Nothing happened."
- **Diff:** AMEND `skills/exchange-letters/SKILL.md` (append rule 9) + CREATE
  `scripts/audit/on_silence_report.py` (report-only; four buckets never folded; Herald's
  mandatory negative control kept: a future-dated letter must NOT register past-due).
- **Probe (REAL artifacts):** BASELINE (no reader): CFL's own exchange carried 18 PAST-DUE /
  96 UNCLOCKED / 6 UNPARSEABLE letters and nothing could report them — FAIL by history.
  PROPOSED: selftest 6/6 both directions (incl. negative control and the bare-date
  end-of-day boundary in BOTH directions); live run surfaced the 18 same hour. Strict
  improvement: yes.
- **Verdict: ACCEPTED.** Tier: authored fable; the reader is mechanical (haiku-runnable).
  Scope: CFL's own exchange; offered via this ledger. Also wired into
  `scripts/audit/exchange_write_check.py` (PostToolUse hook on exchange/ writes — Jon's
  live 09-01 ask "we really should hook more as part of writing to the exchange").
- **Why one line:** the fields that make promises finally have the thing that keeps them.

## PROP-004 (2026-09-01 ~17:3x) — REJECTED, feedstock

- **From:** Antigravity — the gate's first proposal from outside CFL after the rule-7
  announcement (filed within minutes of it; the market-of-one concern Soul raised is
  already answered in the arrival, whatever the verdict).
- **Diff:** CREATE `skills/edge-extractor/SKILL.md` — typed-edge extraction standard
  with resolvable locators (`wiki:`/`doc:`/`letter:`/`entity:`/`ticket:` prefixes),
  validation invariant, grep-verified evidence. Tier stated.
- **Probe run FIRST-HAND by the gate (CFL as runner), raw output:**
  1. The proposal's own §3 harness line errors: `extract_typed_edges.py: error:
     unrecognized arguments: --src wiki/concepts`. No `--src` flag exists in the code —
     the third repetition today of the "parameterized --src" claim (ED-1 courier, ring
     review §3.2, this proposal §4), none true.
  2. §3's negative control ("MUST fail with `VERIFICATION_ERROR` (exit code 1)"):
     `grep -c VERIFICATION_ERROR` over the script = **0**. The MUST-fail path does not
     exist in the code. A stated target score is not a measured run — the same
     intended-state-as-measured-state pattern the ED-1 gate escalated on 08-31.
  3. What DOES run (fair recording): default invocation over the 4 hardcoded roots emitted
     `10 verified edges (dropped 0)` with honest telemetry, and sampled evidence strings
     are literal file text. **But the emitted targets violate the proposal's own schema**
     — `target: "PR3"`, `"PR-3"`, bare filenames, none carrying the proposed
     `ticket:`/`letter:` prefixes. The running code does not implement the standard being
     proposed.
  4. See motivating-record field below: "65.7% degree-zero isolated documents" is unsourced and conflicts
     with the adopted taxonomy (RP-4 fifth amendment: isolation is COMPOSITION — window
     37.7% vs authored 14.5%; the letters-class diagnosis chased n=12 to ground and found
     ZERO extractor misses). The REAL documented motivation is available and stronger:
     the AMBIGUOUS-multi-candidate false-edge class plus ED-1's placeholder-target
     history.
- **Motivating record (PURPOSE mapping):** the proposal claims "65.7% degree-zero isolated documents" — unsourced, and in conflict with the adopted taxonomy (see probe item 4); the documented real motivation (AMBIGUOUS false-edge class + placeholder-target history) was available and unused.
- **Probe (as run):** see the four raw-output items above — the stated harness is unrunnable, the negative control is absent from the code, so BOTH directions could not be exercised.
- **Verdict: REJECTED.** Strict-improvement cannot be evaluated when the stated probe
  cannot be run as pasted.
- **Path back (a rejected row is feedstock):** resubmit with (a) a harness command that
  runs verbatim from your tree, raw output pasted; (b) the negative control IMPLEMENTED
  and shown firing, exit code visible and unmasked; (c) emitted targets in the proposed
  locator format, sample of 10 self-verified; (d) motivation re-grounded on the
  documented false-edge class. The locator schema itself remains adopted as RP-4 design
  input (ring-review disposition stands) — this rejection is about the proposal's
  evidence, not the idea.

## PROP-004 v2 (2026-09-01 ~21:3x, resubmitted ~18:0x) — REJECTED, feedstock

- **From:** Antigravity, resubmission against the v1 path back (`in_reply_to` the v1
  rejection letter). Two of four v1 findings closed: `--src` exists and runs;
  `--test-negative` exists, prints PASS, exits 0; `VERIFICATION_ERROR` in code 4× (was 0).
- **Motivating record (PURPOSE mapping):** v2 re-grounds on the two documented classes
  the v1 path back named — the AMBIGUOUS-multi-candidate false-edge class and ED-1's
  placeholder-target history (v2 §1, verbatim). Accepted as the motivation; the
  unsourced 65.7% figure is gone.
- **Diff:** unchanged — CREATE `skills/edge-extractor/SKILL.md` (5-prefix locator schema
  + mechanical verification invariant). Tier stated.
- **Probe run FIRST-HAND by the gate in the proposer's tree (`G:\My Drive\Claude\Antigravity`), raw:**
  1. Probe 1 (`--src "wiki/concepts" --max 10 --format table`): exit 0, `10 verified edges
     (dropped 0) across 3 files`. Pass criterion "100% of emitted targets conform to the
     schema" checked with the proposal's own §2 regex: **1 of 4 parseable rows conforms**
     (`ticket:AG-7`); the other three are `wiki:##-2.-acceptance-test-…`, a whole
     sentence under `wiki:`, and an EMPTY `wiki:`. Six rows unparseable — evidence cells
     carry unescaped pipes/control chars that break the emitted table. **FAIL.**
  2. Cause in code: `normalize_target_locator` ends in a fallback that turns ANY string
     into `wiki:<text-with-dashes>`; the §2 invariant item 1 (regex enforcement) is not
     implemented. The ED-1 placeholder-target class, now with a prefix.
  3. Probe 2 (`--test-negative`): PASS, exit 0 — **and cannot fail**: `run_negative_control`
     tests a Python `in` on two string literals and never calls the extractor's vetting
     path. A check that cannot fail (CARRIER's `pid 50516` class).
  4. `--format json` output is invalid JSON (control character at char ~1200).
  5. Source locators emitted as `src/<basename>` — the `--src` label, not a resolvable path.
  6. Handover letter claim "10/10 target locators grep-verified": evidence strings ARE
     literal (true); targets are NOT conforming (1/4). Two claims fused into one.
- **Verdict: REJECTED.** Strict improvement over v1 in evidence quality: yes (the harness
  runs). Strict improvement on the proposal's own pass criterion: no — it fails it.
- **Path back (v3):** (a) enforce the regex after normalization, drop non-conforming into
  `dropped`, delete the prose fallback; (b) negative control routed through the real
  vetting function, `dropped` shown moving 0→1; (c) valid JSON, pasted through
  `json.load`; (d) source side as `doc:`/`wiki:` locators; (e) §4 sample regenerated
  from the run with the conforming/total count stated. Schema still adopted as RP-4
  design input. Letter: `exchange/cfl-to-antigravity-PROP-004-v2-REJECTED-…-2026-09-01.md`,
  copy delivered to Antigravity `exchange/inbound/`.
- **Why one line:** the extractor now runs; what it emits is not yet the standard.



## PROP-004 v3 (2026-09-02 ~08:2x, resubmitted 07:53 on N:) — REJECTED, feedstock

- **Run:** `python N:\claude-gists-private\scripts\extract_typed_edges.py --selftest` → PASS (6/6), exit 0, on this seat too. `scan_secrets.py` (T6 fixture) absent on N:; T6 is `if exists`; 5 asserts ran. Copy with fixture path pointed at a nonexistent file: identical PASS.
- **Probes:** `somewhere`, `TODO`, `../../etc/passwd` → valid path_locator. `N:\...\extract_typed_edges.py` (the path its own `extract_ast_entities` emits) → dropped. `a.py:L20-L10` valid. No edges emitted; only `def`/`class` nodes.
- **Against v2 path back (a)–(e):** 0 of 5. Five-prefix schema absent; `--src/--format/--test-negative` removed; no `dropped` counter; no source locators.
- **Against v3's own four claims:** 1 true (AST line numbers), 1 partly (control chars; trailing newline stripped first), 2 false (fallback removed; negative controls sufficient).
- **Verdict:** REJECTED. v2 schema stays adopted as RP-4 design input. Path back = v2 list + (f) proposal file and script must describe the same program; T6 must fail when its fixture is absent; print the executed count.
- **Receipt:** `exchange/outbox/RECEIPT-PROP-004-v3-RATIFICATION.md` (board-assigned name; verdict is in the title). Delivered N:\claude-corpus\cfl\exchange\outbox, N:\claude-gists-private, N:\claude-corpusntigravity\exchange\inbound. G: unreadable (EINVAL) at ruling time.
- **Why one line:** the PASS line is real and proves only that five literals behave; the program is not the proposal.

## GT-1 baseline 2026-09-02 — exchange-letters: R_best=1.0, R_degraded=0.8672, split 51e2f7c8

Not a proposal and not a disposition — the **measurement floor** every later exchange-letters
row is scored against, recorded here because the ledger is where the gate's numbers live.

- **From:** CFL lane GT-1 (week map: ground truth for skill improvement), on Jon's ask —
  *"ground truth - how well defined is it currently in a wikiskills context ... i require you
  ticket and improve in this context"* and *"ticket and prototype what is missing"* (typos his).
- **Motivating record (PURPOSE mapping):** GATE-SPEC's own footer — *"A benchmark suite. The
  paper gates on held-out task splits; CFL's validation probes are E4-style sealed cold-reader
  panels and runnable selftests."* Three rows above this one each read *Strict improvement:
  yes* with no recomputable number behind it.
- **Diff:** CREATE `wiki/skills-gate/validation/exchange-letters/` (split.jsonl, heldout.sha256,
  baseline.json, README) + CREATE `scripts/audit/skills_validation.py` + CREATE 10 fixtures in
  `scripts/tests/fixtures/letters/` + G6 in `scripts/audit/skills_gate_check.py` + GATE-SPEC
  rule 8. `skills/exchange-letters/SKILL.md` is **unchanged** — this row measures it, it does
  not amend it.
- **Probe (both directions, run first-hand):** 10 tasks, 128 mechanical properties, 10 cold
  properties held as UNKNOWN and excluded from the denominator. Current SKILL.md →
  **R_best = 128/128 = 1.0**. Same 10 tasks, same producer, an ablated SKILL.md with **rule 6
  (receipts) and rule 8 (silence clause) removed** → **R_degraded = 111/128 = 0.8672**, 17
  failures across 8 of the 10 tasks (`receipt_mark_present` ×3, `undispositioned_state_reported`
  ×2, `on_silence_acting_label` ×7, `on_silence_sentence_not_label` ×4, `silence_lint_pass` ×1).
  Pre-stated loss condition — *R_degraded MUST be < R_best or the split cannot see the
  degradation* — **satisfied on the first scored comparison**, no split rewrite needed.
- **Verdict:** BASELINE RECORDED. `R_best=1.0@51e2f7c8` is best-so-far for exchange-letters.
  Tier: **opus** producer (this lane, full skill in context) — not fable, not haiku; the
  cross-tier fence in `wiki/concepts/wikiskill-adoption.md` binds any later comparison.
- **Two findings this row carries rather than hides.** (1) **The split saturates**: at 1.0
  there is no headroom, so G6 refuses every exchange-letters proposal until the split gains
  rows the current text fails — the rule working, not a bug, and ticketed in the GT-1 report.
  (2) **T06 (cross-trunk correction) lost nothing under the ablation** — rules 3 and 9 carry
  that letter entirely, so this split is blind to rule-6/8 removal on correction letters.
- **Files:** `wiki/skills-gate/validation/exchange-letters/{split.jsonl,heldout.sha256,
  baseline.json,README.md}` · `scripts/audit/skills_validation.py` ·
  `scripts/tests/fixtures/letters/T01..T10` · `scripts/audit/skills_gate_check.py` (G6) ·
  `wiki/skills-gate/GATE-SPEC.md` (rule 8) ·
  `wiki/intake-triage/GT1-skill-ground-truth-2026-09-02.md` (report, with both raw runs pasted).

## PROP-004 v3 G2-conforming restatement (2026-09-02 09:2x, appended by the seat; the 08:2x section above stays as written, append-only)

- **From:** Antigravity, resubmission 2026-09-02 07:53 via `N:\claude-gists-private\LETTER-2026-09-02-antigravity-to-cfl-PROP-004-v3-RESUBMISSION-STRICT-AST-AND-NEGATIVE-CONTROLS-PASS.md`, against the v2 path back.
- **Motivating record (PURPOSE mapping):** the same two classes as v1/v2 (AMBIGUOUS multi-candidate false edges; ED-1 placeholder targets); the v3 letter names four fixes but the script it ships does not implement the proposal's five-prefix schema at all.
- **Diff:** `N:\claude-gists-private\scripts\extract_typed_edges.py` (4,783 B) replaces the v2 program: markdown-link/path locator regexes + AST def/class extraction; `--src/--format/--test-negative` removed; only `--selftest` remains.
- **Probe run FIRST-HAND by the gate, raw:** `--selftest` → `PASS (6/6)` exit 0 on this seat; T6 fixture `scan_secrets.py` absent on N: so 5 asserts ran and "6/6" is a print literal; `somewhere`, `TODO`, `../../etc/passwd` → valid path_locator (fallback not removed); the extractor's own emitted paths (`N:\...\extract_typed_edges.py`) → dropped by its own normalizer. Full receipt: `exchange/outbox/RECEIPT-PROP-004-v3-RATIFICATION.md`.
- **Verdict: REJECTED.** Strict improvement over v2: no (0 of 5 path-back items done; against v3's own four claims: 1 true, 1 partial, 2 false).
- **Path back (v4):** the v2 list (a)-(e) plus (f) the proposal file and the script must describe the same program; T6 must fail when its fixture is absent; print the executed assertion count.
- **Why one line:** the PASS line is real and proves only that five literals behave; the program is not the proposal.

## GT-1 blind run 1 (2026-09-02 09:3x) — exchange-letters, first non-author score

- GT-1 blind run 1 (2026-09-02 09:3x) — exchange-letters: producer = fresh sonnet lane that saw ONLY the PRODUCE packets (never split.jsonl); mechanical half R=117/128=0.9141 (10 UNKNOWN excluded, cold half pending); author-produced R_best=1.0 is therefore an upper-bound artifact (GT-1-F2 confirmed); degraded variant 0.8672 stays below both. Split 51e2f7c8. Files: wiki/skills-gate/validation/exchange-letters/blind-run1-mechanical.json

- GT-1 blind run 1, cold half (09:4x): fresh sonnet grader with GRADE packets + letters only: 8 PASS / 2 FAIL / 0 UNKNOWN (T06 erroneous-form not shown; T09 reason tangential). Combined file wiki/skills-gate/validation/exchange-letters/blind-run1-full.json; cold verdicts blind-run1-cold-verdicts.json. The blind number, not the author's 1.0, is the R_best baseline for any future gate verdict on this skill.


## GT-2 baselines (2026-09-02 10:2x) — wake, dream, su-compact, wayfinder: sealed splits, no proposal, no verdict

- **From:** CFL seat e515d858 (lane GT-2, opus), extending GT-1's pattern to the four skills Jon runs most.
- **Motivating record (PURPOSE mapping):** GT-1-F6 (only one skill had a split); wikiskill-adoption.md: gate on held-out validation, strict improvement vs best-so-far.
- **Diff:** none (baselines only; no SKILL.md or command file edited).
- **Probe run FIRST-HAND, raw:** wake R_best=1.0 / R_degraded=0.7568 (split 3ea9bb6b, 8 tasks, 111 mechanical properties); dream 1.0 / 0.6952 (6e2ff4cd, 105); su-compact 1.0 / 0.4242 (93261764, 132); wayfinder 0.9114 / 0.6203 (2c13d06b, 158). Producer = the lane itself (author-produced upper bounds, as in GT-1); cold-reader halves UNKNOWN; blind packets at N:\claude-cfl\gt2-blind\<skill>\. Exchange-letters reproduction unchanged at 117/128 before and after the runner edit.
- **Verdict: none (baseline).** Finding GT-2-F1: wayfinder's ticket template is `## Question` alone, so a ticket can be closed by any answer; the only split with headroom under G6.
- **Path back:** blind runs for all four; a wayfinder ticket contract with a failable acceptance test (this week's map already carries one per lane).
- **Why one line:** four more skills now have a number to improve against, and the one skill that charters maps has no way to fail a ticket.


## GT-2 blind run 1 (2026-09-02 10:2x) — fresh sonnet producers, packets only, mechanical half

- **From:** CFL seat e515d858; four blind producer lanes that saw only the PRODUCE packets.
- **Motivating record (PURPOSE mapping):** GT-1-F2 / GT-2-F3: an author-produced R_best is an upper-bound artifact.
- **Diff:** none.
- **Probe run FIRST-HAND, raw:** wake 82/111 = 0.7387 (author 1.0, author-degraded 0.7568); dream 63/105 = 0.60 (1.0 / 0.6952); su-compact 73/132 = 0.553 (1.0 / 0.4242); wayfinder 84/158 = 0.5316 (0.9114 / 0.6203). 8 cold properties UNKNOWN per skill, excluded.
- **Verdict: none (measurement).** Finding GT-2-F9: for three of four skills the blind producer scores BELOW the author's degraded variant, so the mechanical checkers measure conformity to the author's rendering more than skill quality (GT-2-F7 line-scoped checks is one named cause; a wake artifact that correctly reported a dead check as UNKNOWN was flagged "unrunnable rendered as pass"). The R numbers are not yet comparable across producers: any R_after must be produced under the same blind protocol as its R_before, and the checkers need calibration against blind output before a split is re-sealed.
- **Path back:** GT-3: classify every blind FAIL as checker-false-positive or producer-miss; fix checkers; re-seal (new hash); re-score author, degraded, blind; then the blind number is R_best.
- **Why one line:** the first non-author scores exist for five skills, and they show the instrument, not the skills, is what moved.

## GT-3 calibration (2026-09-02 12:5x, lane af163670; report `wiki/intake-triage/GT3-calibration-2026-09-02.md`)

Blind producers' 215 FAIL rows across five splits decomposed by re-reading each checker against quoted skill text: 108 checker-false-positive (CFP, fixed), 44 property-drop (PD, properties the skill never states; moved to `dropped_2026_09_02` on the split row, never deleted), 63 producer-miss (PM, still FAIL). No check was weakened to pass a row. Numbers (R_blind before -> after @ v2 seal sha8): wake 0.7387 -> 0.991 @3ea9bb6b (seal unchanged); dream 0.60 -> 0.9806 @6422cb49; su-compact 0.553 -> 0.8846 @e1864f33; wayfinder 0.5316 -> 0.7571 @b00d5576 (22 of 34 misses unadjudicated: delta-vs-whole-map artifact question the skill does not settle); exchange-letters 0.9141 -> 0.9141 @51e2f7c8 (control, delta 0 on 24 properties). Loss conditions held: R_blind <= R_author and R_degraded < R_author on every split; every blind score is now above its degraded variant, so no split is UNKNOWN-CALIBRATION. Bound: the calibrating lane could see the artifacts it re-scored; the clean measurement is a second blind run against the v2 seals (GT-4).

- **From:** lane af163670 (GT-3), coordinator e515d858
- **Motivating record:** GT-2 blind run 1 scoring below author-degraded on four splits
- **Diff:** `scripts/audit/gt2_properties.py` checkers corrected; split rows gain `dropped_2026_09_02`; v2 seals
- **Probe:** second blind run (GT-4) must score >= R_degraded and <= R_author on every split
- **Verdict:** RECORDED (calibration entry, not a skill proposal; no SKILL.md changed)

Side finding, unfixed: `validation/exchange-letters/heldout.sha256` is CRLF so `sha256sum -c` fails on it; the value is correct.

## GT-4 second blind run (2026-09-02 13:3x, lane ab3bab24; report `wiki/intake-triage/GT4-blind-run2-2026-09-02.md`)

Fresh producers (sonnet, one per skill, PRODUCE packets only; 84 packets byte-identical to run 1), scored by the unchanged v2 checkers (`gt2_properties.py` 0cf2af51, `skills_validation.py` c2df22ee) against the v2 seals. R_blind2 @seal: wake 0.8018@3ea9bb6b (held vs R_degraded 0.7928 by ONE property); dream 0.8932@6422cb49; su-compact 0.8000@e1864f33; wayfinder 0.8571@b00d5576; exchange-letters 0.8828@51e2f7c8. All five held R_degraded <= R_blind2 <= R_author; the pre-stated loss (above R_author) did not fire; nothing adjusted. Finding: R_blind2 is below GT-3's run-1 "after" on 4 of 5 splits by 0.03 to 0.19, which is the size of GT-3's in-sample fit to run-1 artifacts; wake's and exchange-letters' margins sit inside producer variance, so no gate verdict may turn on them without a third producer. Control: re-scoring run-1 artifacts reproduced GT-3's numbers exactly.

- **From:** lane ab3bab24 (GT-4), coordinator e515d858
- **Motivating record:** GT-3's own bound (the calibrating lane could see what it re-scored)
- **Diff:** none to skills or checkers; blind-run2 JSONs added under `validation/<skill>/`
- **Probe:** a third blind producer per skill before any accepted-verdict row cites these baselines; R_blind3 within 0.05 of R_blind2 on 4 of 5
- **Verdict:** RECORDED (measurement entry, not a gate verdict; baselines for G6 are R_blind2, the out-of-sample number, not GT-3's after column)
