---
name: re-derived-not-researched
description: This trunk cites five URLs across sixty pages. Every hard-won rule the fleet produced this week already has a name, a literature, and in four cases a tool that enforces it mechanically — transactional outbox, mutation score, diagnostic coverage, dead man's switch, population completeness. The finding is not that we were wrong; it is that we paid full price for answers that were on the shelf.
kind: concept
created: 2026-08-24
sensitivity: routine
calibration: the footprint counts are [measured] on this tree 2026-08-24 15:3x. The external prior art is [relayed+] from web search performed this session — search-result summaries read, primary standards NOT opened, and that bound is stated in every row rather than hidden.
---

# Re-derived, not researched

⛔ **THE MEASUREMENT THAT STARTED THIS, AND IT IS ABOUT US, NOT ABOUT THEM.** `[measured 2026-08-24 15:3x]`

| surface | count |
|---|---|
| `.md` pages under `wiki/` | **60** |
| pages containing **any** URL | **3** |
| total URL occurrences | **5** |
| distinct hosts | **3** — `github.com`, `actuarialstandardsboard.org`, `kb.cert.org` |
| pages mentioning **ASOP** | **23** |

**Command, so this is not itself a `print-the-population` violation:**
`grep -rohE 'https?://[^ )>"]+' wiki/ --include='*.md' | wc -l` and
`grep -rlE 'https?://' wiki/ --include='*.md' | wc -l`, denominator
`find wiki -name '*.md' -type f | wc -l`.

⭐ **THE ONE THING THAT WENT WELL IS VISIBLE IN THAT TABLE AND IT IS THE ONLY THING THAT DID: 23 of
60 pages are anchored to ASOP text, and `[[grounding-principles]]` quotes it VERBATIM FROM DISC WITH
LINE NUMBERS.** ⛔ **That is the correct shape — an external standard, obtained, stored locally,
quoted at the primary, re-readable by a stranger.** ⚠️ **It is also the only external body of work
this trunk has ever ingested, and Jon named it. We have not chosen an external source on our own
initiative once.**

---

# ⛔ THE FIVE RULES WE PAID FOR, AND WHAT THEY ARE ALREADY CALLED

**Each row: our sentence, the existing name, and — the part that matters — WHAT THE LITERATURE
CARRIES THAT OUR VERSION DOES NOT.** ⭐ **That last column is the whole argument. If prior art only
restated our rule, re-deriving it would have cost nothing but pride.**

## 1 · "An outbox file is a draft. Only the receiver's tree is delivery."

**Name: the TRANSACTIONAL OUTBOX pattern.** `[relayed+]` A canonical distributed-systems pattern with
a catalogue entry, an AWS prescriptive-guidance page, and fifteen years of production use.

⛔ **WHAT IT CARRIES THAT WE DO NOT: the pattern is not "write to an outbox." It is OUTBOX PLUS A
RELAY PROCESS.** The relay is a *separate, always-running* component whose only job is to read
unsent rows, deliver them, and mark them sent. **We built the outbox table and never built the
relay.** ⭐ **Every delivery failure this fleet has recorded — twelve letters that never left the
building on 08-17, the six Personal→CFL letters Herald hash-verified as undelivered today, Soul's
routing letter that sat six hours while the mail it described also sat — is the SAME MISSING
COMPONENT, and it has a name.**

⚠️ **And the pattern names the second half we also lack: the IDEMPOTENT CONSUMER, usually an INBOX
table.** The relay guarantees *at-least-once*, so the receiver must be able to see the same letter
twice and act once. **We have no message identity at all** — our identity is a filename, which is why
`cmp` is our delivery proof and why a receiver annotating in place destroys it (`P-11`).

⭐ **THE ACTIONABLE FORM, and it is smaller than it sounds: `C9` is already a relay's *reporting*
half. What is missing is the half that ACTS.** A relay is `for f in outbox/*: if not in every
addressee tree: cp`. **We wrote the alarm and not the actuator, which is the same shape as
`[[a-control-with-no-reader]]`.**

## 2 · "Proven failable" / "a test that can only return one answer is a ratchet"

**Name: MUTATION TESTING; the metric is MUTATION SCORE.** `[relayed+]` Dates to 1978; mature tooling
exists (`mutmut`, `cosmic-ray` for Python). **The failure mode we kept hitting has a name too:
ASSERTION-FREE TESTING — 100% coverage with 0% mutation score.**

⛔ **WHAT IT CARRIES THAT WE DO NOT: a SCORE OVER A GENERATED POPULATION OF MUTANTS, rather than a
hand-picked one.** ⭐ **Our "proven failable" is a mutation score of 1/1 — we seed the ONE defect we
already thought of, watch the test die, and call it proven.** ⚠️ **Soul's SIGPIPE finding is exactly
a surviving mutant we never generated.** **The honest restatement of every banner in `scripts/`:
*this check kills the one mutant its author imagined.* That is a real claim and it is much weaker
than "proven failable."**

⭐ **AND IT SETTLES THE QUESTION I OWED JON: how much weaker?** Unquantified, because we have never
generated a mutant population. **Mutation score is the number that would answer it, and for our
shell scripts no tool exists — which is a genuine finding, not an excuse: the fleet's checks are
overwhelmingly `bash`, the one language with no mutation-testing ecosystem.**

## 3 · "A gate that cannot run is UNKNOWN, and UNKNOWN dominates a PASS"

**Name: in functional safety, the DANGEROUS UNDETECTED failure (λDU), and the metric is DIAGNOSTIC
COVERAGE — the fraction of dangerous failures the on-line diagnostics actually detect.** IEC 61508.
`[relayed+ — search summaries and vendor position papers; the standard itself NOT opened, and it is
paywalled.]`

⛔ **WHAT IT CARRIES THAT WE DO NOT — and this is the sharpest thing found today:**

> ⭐ **THE TAXONOMY IS TWO AXES, NOT ONE. Safe/dangerous CROSSED WITH detected/undetected.**
> ⛔ **`|| true` was not an undetected failure. It was a DANGEROUS failure classified as SAFE.**

**Our rule says UNKNOWN must not be reported as PASS. The standard's rule is stronger: you must
QUANTIFY what fraction of dangerous failures your diagnostics catch, and the residue — λDU — is the
number that sets your integrity level.** ⚠️ **We report our gates as CLEAN / 11 of 11. We have never
published a diagnostic-coverage figure, and 11/11 reads as 100% to every reader.**

⭐ **AND IT SUPPLIES THE MECHANISM FOR EVERY UNDATED OBLIGATION IN `tracker.md`: the PROOF TEST.**
Dangerous-undetected failures are, by construction, invisible to on-line diagnostics; **the only
thing that finds them is a periodic off-line test at a defined interval.** ⛔ **Our
`DATED OBLIGATIONS` table says of every row: *"the date is recorded and nothing will fire it."*
**That table IS a proof-test schedule with no proof-test interval and no tester.**

## 4 · "Nothing wakes this trunk" / "residents cannot page anyone"

**Name: the DEAD MAN'S SWITCH, a.k.a. watchdog alert, heartbeat alert, sentinel.** `[relayed+]`
Standard practice: Prometheus ships a `Watchdog` alert that fires **constantly**, routed to an
external service that pages when it **stops** arriving. `absent()` is the PromQL primitive for the
same idea.

⛔ **WHAT IT CARRIES THAT WE DO NOT: the direction is INVERTED, and that inversion is the entire
trick.** ⭐ ***An alarm that fires on silence must itself be a signal that stops.*** **You cannot
detect absence from inside the thing that is absent.** ⚠️ **Every mechanism this fleet has built to
fix "nothing wakes me" has been an *internal* check that runs when the trunk runs — which is
precisely the population that does not have the defect (Herald's rule, turned on us).**

⛔ **AND IT NAMES WHY JON'S HEARTBEAT-OFF RULING IS NOT THE OBSTACLE WE HAVE TREATED IT AS.** He
turned off a **cron that woke a trunk**. A dead man's switch is the opposite object: **it does not
wake anything; it is a file this trunk TOUCHES when it runs, which somebody else — a sibling, or
Jon's own eye — notices has gone stale.** ⭐ **A staleness beacon costs one `date > exchange/HEARTBEAT`
per close and requires no scheduler, no wake, and no new surface.** ⚠️ **Whether that is inside or
outside his 08-11 ruling is a judgement, and by our own rule it is OURS to make, not his to be asked
about: it creates no notification and starts no job. Proposing it, not asking.**

## 5 · "Print the population"

**Name: COMPLETENESS OF THE POPULATION — and it is not merely analogous, it is a REQUIREMENT in the
professional literature Jon works under.** AU-C 530 (audit sampling): *the auditor is required to
perform audit procedures to obtain evidence that the population from which the sample is drawn is
complete.* `[relayed+ — search summaries of AU-C 530; the section itself not opened.]`

⛔ **WHAT IT CARRIES THAT WE DO NOT: it is an AFFIRMATIVE PROCEDURE, not a disclosure.** ⭐ **Our rule
says *print what you looked at.* The standard says *do work to establish that what you looked at was
everything, and that work is a separate step with its own evidence.*** ⚠️ **The 08-24 `[PRO:]`
miscount is exactly this: the population was printed (a `grep -r` command), it was auditable, and it
was INCOMPLETE — because nobody ran a completeness procedure over the file types the grep would
reach.** ⛔ **"Printing the command is not printing the population" — our own instance-8 sub-rule —
is the AU-C 530 distinction rediscovered, one incident at a time.**

⭐ **THIS ONE BELONGS IN `[[grounding-principles]]` AS A SEVENTH PRINCIPLE, because it is the same
class as the six already there: a named professional standard that this program was going to
re-derive anyway, at cost.**

---

# ⭐ THE LINEAGE, HONESTLY GRADED — what our external research has done well and badly

**Four episodes are on the record. All four are `[measured]` from this tree.**

| episode | verdict |
|---|---|
| **ASOP ingestion → `[[grounding-principles]]`** | ⭐ **BEST WORK OF ITS KIND HERE.** Standard obtained, stored on disc under `raw/asops/txt/`, quoted verbatim with line numbers, re-checkable by a stranger. ⛔ **Jon ordered it. We did not choose it.** |
| **`voyage-4-nano` licence, 2026-08-17** | ✅ **Correct method:** a `[relayed]` claim upgraded to `SECONDED-FROM-VENDOR-DOC` by opening the vendor page. ⚠️ **And the HF licence file was REFUSED-BY-GATE and published as such rather than glossed** — the right failure. |
| **`kb.cert.org` citation** | ✅ present, single use. |
| **Everything else** | ⛔ **Zero.** Five rules above, each worth days, each re-derived from incidents. |

## ⛔ WHY IT WENT THIS WAY, AND THE DIAGNOSIS IS NOT "WE FORGOT"

⭐ **INCIDENTS ARE SELF-ROUTING AND LITERATURE IS NOT.** A defect arrives with a timestamp, a
victim, and a name attached; a standard arrives only if somebody goes and gets it. **Our whole
method — measure, find the defect, name the class, write the page — is a machine for converting
incidents into knowledge, and it has NO INPUT for knowledge that arrives any other way.**

⚠️ **Second cause, and it is the more embarrassing one: our defects present in this program's own
vocabulary, so they do not look like anything.** *"`|| true` in a SessionStart hook"* does not read
as a functional-safety problem. **The abstraction that would have found the literature — "a
diagnostic that cannot distinguish a dangerous failure from a safe state" — is exactly the
abstraction we produce at the END of the process.** ⛔ **So the search that would have saved the work
is only formulable after the work is done.**

## ✅ HOW TO SEARCH AND REVIEW BETTER — three mechanisms, sized to what this trunk can actually run

⛔ **NOT a new gate. Jon: *"Overconservatism has caused defects in this project in the past."***

1. ⭐ **PRIOR-ART LINE ON EVERY NEW CONCEPT PAGE.** Each `wiki/concepts/*.md` gains one field:
   `prior_art:` — the external name, or the literal string **`SEARCHED, NONE FOUND`**, or
   **`NOT SEARCHED`**. ⛔ **Three values, and the third is the honest default, so the field can never
   be a ratchet** (this trunk's own rule). **Enforceable by `lint.sh` as a reported backlog, exactly
   like `description:` — reported, not failed.** ⚠️ **Cost: one search per page. `[measured]` 34
   concept pages exist, so the retro-fit is bounded and can be done lazily.**

2. ⭐ **SEARCH AT CLASS-NAMING TIME, NOT AT INCIDENT TIME — the diagnosis above tells you exactly
   when.** The moment a page gets its abstract one-line class name is the first moment the search is
   formulable, and it is also the moment we currently stop. **Move one step further: name the class,
   then search the name.** ⛔ **All five hits above took a single query each.**

3. ⚠️ **AND THE REVIEW HALF, which is where a search goes wrong here: A SEARCH-RESULT SUMMARY IS NOT
   A PRIMARY.** Everything in this page except the footprint table is `[relayed+]` from search
   summaries — I did not open IEC 61508 (paywalled), AU-C 530, or the microservices catalogue.
   ⛔ **By `[[grounding-principles]]` P2 that is a HALF-STANDARD citation, and the ASOP work is the
   contrast: those were read from disc.** ⭐ **The rule that follows: an external claim may be
   ADOPTED at `[relayed+]`, but it may not be QUOTED AS AUTHORITY until somebody opens the primary —
   and a paywalled standard is `UNREACHABLE-FROM-HERE`, which is a class we already have
   (`[[negative-claims-require-an-attempt-ledger]]`).**

---

# ⚠️ THE BOUND ON THIS PAGE ITSELF

**Five rules were checked against literature. This fleet produced far more than five rules this
week.** ⛔ **The five were chosen because I suspected prior art existed — which is the same selection
defect I named to the resident this hour: A SELECTION IS ONLY GOOD JUDGMENT IF ITS CRITERION WAS
STATED BEFORE THE SELECTION AND CAN BE RE-APPLIED BY SOMEONE ELSE.** ⭐ **Criterion, stated after the
fact and therefore weak: rules that name a MECHANISM rather than a value. The five hits are 5 for 5,
which is suspicious — it suggests the base rate is high and the unexamined rules are hiding hits
too, not that my picking was good.**

**Related:** [[print-the-population]] · [[grounding-principles]] · [[a-control-with-no-reader]] ·
[[negative-claims-require-an-attempt-ledger]] · [[ownership-is-not-reachability]]

## Sources

- [Microservices Pattern: Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html)
- [Transactional outbox pattern — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [What is mutation testing? — CircleCI](https://circleci.com/blog/what-is-mutation-testing/)
- [Code Coverage vs Mutation Testing](https://journal.optivem.com/p/code-coverage-vs-mutation-testing)
- [Proof Test and Diagnostic Coverage — GT Engineering](https://www.gt-engineering.it/en/insights/process-safety-processi-gt-engineering/proof-test-diagnostic-coverage/)
- [exida position paper on IEC 61508:2010 definitions](https://www.exida.com/images/uploads/exida_Position_on_IEC_61508_2010_definitions_minimum_HFT_v4.pdf)
- [End-to-end watchdog alerts — PromLabs](https://training.promlabs.com/training/monitoring-and-debugging-prometheus/metrics-based-meta-monitoring/end-to-end-watchdog-alerts/)
- [How To Set Up a Dead Man's Switch in Prometheus](https://blog.ediri.io/how-to-set-up-a-dead-mans-switch-in-prometheus)
- [AU-C Section 530, Audit Sampling (SAS No. 122)](https://apiproxy.utc.wa.gov/cases/GetDocument?docID=8&year=2019&docketNumber=190531)
