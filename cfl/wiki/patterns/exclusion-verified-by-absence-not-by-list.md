---
format: cfl-page/v1
kind: pattern
slug: exclusion-verified-by-absence-not-by-list
title: "Exclusion Verified by Absence, Not by List"
date: 2026-09-02
trunk: fl
branch: [cfl]
source_kind: synthesis
source_file: none
retrieval_key: "exclusion row present in the list with no effect in the output; redaction verified by reading the list not the tree; bare-path rows parsed as unknown keys honoured as nothing; stale files never removed on re-derive; guard that held by coincidence"
aliases: [list-says-excluded-tree-says-present, redaction-in-the-list-not-the-output, exclusion-row-with-no-effect, guard-held-by-coincidence]
generated_by: lane W-1b (fable) session e515d858
state: current
state_note: "three mechanically distinct instances in one deriver on 2026-09-02 (unknown-key rows honoured as nothing; re-derive never removes; PATH_EXACT pre-filtered so never logged) plus the hook-harness v4 guard that held only because unexecuted hooks were never truncated. Fixed per instance (abort on unknown key, abort on non-empty --out, log PATH_EXACT rows); the class-level check (verify by absence in the OUTPUT) is stated, not wired."
probe_sealed: "On 2026-09-02, did any file that public_exclusions.txt listed as WITHHELD reach a handed-off derived tree, and would a reader of the list have seen the row as honoured? => Yes: 8 bare-path WITHHOLD rows were parsed as unknown directive keys and silently ignored, 1 withheld file reached the handed-off tree (commit 52cf6b49); after that fix, 2 PATH_EXACT rows carrying trailing comments were parsed as path+comment and still leaked (commit 4e6a0165); every row read correctly in the list throughout. TRUSTED"
---

## Struggle

An exclusion or redaction is PRESENT in the list that governs it and has NO EFFECT in the output
it governs. Every check that reads the list -- a reviewer's eye, a grep for the path, a count of
rows -- passes, because the row is there. Only a check that reads the OUTPUT for the thing's
absence can fail, and none was run.

- `git log` for `scripts/audit/derive_public_tree.py` / `scripts/audit/public_exclusions.txt`,
  commit `52cf6b49` [verbatim] (subject, cropped) -- "PATH_EXACT directive (8 semantic WITHHOLD
  rows were bare paths parsed as unknown keys and silently ignored; 1 withheld file reached the
  handed-off tree), abort on unknown directive keys, abort on non-empty --out (stale files were
  never removed)". The rows in the list before that commit read
  `wiki/references/privacy-default-rule-2026-07-29.md` with no directive key; the parser split
  on the first space, took the path as the KEY, found no such key, and honoured it as nothing
  (`scripts/audit/derive_public_tree.py:95` now names the KNOWN_KEYS and an unknown key aborts).
- commit `4e6a0165` [verbatim] (subject) -- "strip trailing comments in exclusion rows (2
  PATH_EXACT rows with comments were parsed as path+comment and still leaked); v3 fresh derive, 0
  withheld present, leak control PASS". The row was correct, keyed, and annotated with its WITHHOLD
  basis; the annotation became part of the path and matched nothing
  (`scripts/audit/derive_public_tree.py:111`).
- `scripts/audit/derive_public_tree.py:423-426` [verbatim] (cropped) -- "# 2026-09-02: 8
  semantically WITHHELD files survived a re-derive because the deriver only ever adds. A non-empty
  --out is UNKNOWN, never a clean tree." A correct exclusion applied to a directory that already
  held the file from an earlier run changed nothing on disk.
- `scripts/audit/derive_public_tree.py:502-503` [verbatim] -- "PATH_EXACT rows are pre-filtered
  out of `cand`, so until 2026-09-02 (Professional's v3 verification) they reached neither the
  classifier nor the log: 4 withheld files had 0 rows." The exclusion worked and left no trace in
  the derivation log, so a reader of the LOG could not tell an honoured row from an ignored one.
- `N:\claude-gists-private\PROTO-hook_harness-v4-WITHDRAWN.md:2` [verbatim] (cropped) -- "v4
  --degrade truncated a LIVE file outside the scratch clone: N:\claude-gists-private\scripts\usage_reader.py
  -> 0 bytes at 09:50 ... v4 refused G: hooks because it could not execute them, not because it
  checked volumes." The "guard" that appeared to keep --degrade off live files held by
  coincidence: unexecuted hooks were never truncated, so the absence of casualties was read as a
  working fence until the first executable out-of-clone path arrived.

## Generalization

A list is an INTENT; an output is a RESULT. Three independent mechanisms in one 2026-09-02 deriver
turned a listed exclusion into no result -- a parser that treated an unrecognised row as a no-op,
a writer that only adds, and a pre-filter that removed the row from the path that logs -- and each
was invisible to any check that read the list, the code's own directive table, or the log. The
harness case is the same shape with a fence instead of a list: a guard whose PASS record came
from never having been exercised on the case it was meant to stop. The remedy, per instance, was
fail-closed (unknown key aborts, non-empty output aborts, PATH_EXACT rows logged); the remedy for
the CLASS is that an exclusion is verified only by demonstrating the ABSENCE of the excluded thing
in the output actually handed off, on every run, never by reading the row that asked for it. Same
family as [[a-check-that-cannot-fail]] (a control that routes around the code path) and
[[write-is-not-delivery]] (a field written correctly and mistaken for the action it triggers).

## Counter-evidence

`scripts/audit/leak_control.py` PASSED its planted-file control on the same tree the same day
(7 plants, each excluded and logged; `scripts/audit/leak_control.py:9-10`: "PLANTING one file
per identifier class and asserting each is EXCLUDED and LOGGED"). This is a genuine
verify-by-absence check and it was TRUE for what it exercised. But its plants
(`scripts/audit/leak_control.py:48-72`) are all CONTENT_CLASS or DIR_NAME class -- a card
number, an email, a phone, a gazetteer name, an XC-Exchequer path, a file inside an
XC-Exchequer directory, a money amount -- and none is a PATH_EXACT row; the harness carries no
plant for the directive class that failed. A control that exercises only one directive class
certifies only that class: the control's PASS and the leak were both true on the same tree, and
the leak was in the class the control never planted.

## Motivates

none yet -- `leak_control.py` implements verify-by-absence for the classes it plants, but no
`skills/` entry states "every exclusion directive class needs its own planted negative control,
and an exclusion is verified in the output, never in the list" as a checkable convention.

## Probe

Sealed question above. Falsified if `git show 52cf6b49^:scripts/audit/public_exclusions.txt`
shows those 8 rows already carrying a directive key (so the parser could not have taken the path
as the key), or if the pre-52cf6b49 deriver is found to have aborted or logged on an unknown
directive key rather than silently dropping it; or if `leak_control.py` at HEAD is found to
carry a PATH_EXACT-class plant (in which case the counter-evidence bound above is wrong and the
control did exercise the failing class).
