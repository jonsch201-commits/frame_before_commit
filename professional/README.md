# WikiSkills in practice — Claude Professional's derived public tree

This tree is **derived**, not authored for publication: an allow-list run over a private working
tree produces it, and every file here is byte-identical to its private original. What is here is
what the allow-list admitted; what is not here was excluded whole, never edited.

## Disclaimer

> None of the author's input to this project was actuarial work. An actuary who wants to use these
> skills should first review and test them, and align them with the actuarial standards that apply
> to their own work.

This repository is not an actuarial communication and contains no actuarial opinion. It claims that
the skills, pages and scripts here **exist and are runnable**. It does not claim that any skill
changed a decision, that any retrieval index is complete or current, or that the method improves
outcomes. Where a number appears, its population and the direction of its bound appear beside it;
where a zero appears, the second method that confirmed it appears beside it or it is marked
unconfirmed.

## What is here

- `skills/` — the three skills this trunk authored: `dead-man-wake`, `peer-review`,
  `session-identity`, each `SKILL.md` with its ratification date and known failure modes.
  **Not in this tree:** frame-before-commit, ground-before-stating, wiki-query and
  wikiskills-improve. Those are fleet skills held in the Foundational Layer's tree and this
  derivation was run over the Professional trunk only (found 2026-09-12 22:1x, by Jon's question).
  A tree that carries them is derived from that other trunk and does not exist yet.
- `wiki/concepts/`, `wiki/references/`, `wiki/sources/` — the pages the skills cite by name:
  query-before-build, membership-is-not-retrievability, grounding principles, the three failures of
  2026-09-12 and what they bind.
- `wiki/test-outputs/seals/` — pre-branch seal files, dated before the runs they seal.
- `scripts/` — the lint that grades this tree (`scripts/lint.sh`), the render, index and horizon
  scripts, and under `scripts/audit/` the include spec that produced this tree.

## Reproduce the measurements

Every number in the pull request description names the command that produced it. The ones a reader
can run here:

```
bash scripts/lint.sh                 # grades this tree from its own root; prints PASS/FAIL per check
python scripts/index_gen.py          # regenerates the derived index and reports drift
python scripts/render-subagents.py --selftest
```

Commands that read a private session store, a private inbox, or another trunk's tree will report
`UNKNOWN` here rather than a clean zero. Treat `UNKNOWN` as no measurement, never as a pass.

## What is excluded, and why

The allow-list is `scripts/audit/public_include_professional.txt`; its header states the reason for
each excluded class. Excluded whole: the exchange (letters between trunks), rendered session
transcripts, trackers and logs, this trunk's operational state, and the constitution. Content
classes excluded by detector: names, e-mail addresses, phone numbers, one private ledger's paths,
and pages whose front matter marks them held or as belonging to another trunk.

**One exclusion a reader should know about before trusting the rest.** The control that proves the
exclusions work — `leak_control.py`, which plants one fixture per identifier class and asserts each
is excluded and logged while a known-clean control file is still included — is itself excluded,
because its fixtures are identifier-shaped. So this tree carries the deriver and not the test of the
deriver. A reader who wants that proof can reproduce it privately: clone the private tree with the
owner's permission, run `derive_public_tree.py` with this spec into an empty directory, then run
`leak_control.py` against that output and read its log. The published tree cannot carry that
evidence and this paragraph exists so nobody discovers the gap instead of being told.

One overlap among the content classes is known and stated rather than tidied: the FINANCIAL detector also fires on a labelled account number with no money amount, so it subsumes ACCOUNT. Nothing leaks by it; the published surface is excluded more, not less. Its cost is auditability: a passing ACCOUNT control proves one of the two rules alive, never which. The harness's remedy is to assert the pair explicitly, and until it does the pair is one control, not two.

Excluded files are still **named** inside included files in a small number of places (five of
twenty-two excluded files, six references, at the last derivation). Names, not contents; each is a
citation to a file a reader of this tree cannot open.

## What was relied on

The author's own record of his instructions, verbatim, as the authority on intent; the WikiSkills
pattern as the design; sibling trunks' measurements where named, each graded as measured, relayed
or recalled. A reader may not treat any number here as current without re-running the command that
produced it.
