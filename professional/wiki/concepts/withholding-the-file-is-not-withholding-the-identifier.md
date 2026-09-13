---
name: withholding-the-file-is-not-withholding-the-identifier
title: Withholding the file is not withholding the identifier
date: 2026-09-02
type: concept
---

# Withholding the file is not withholding the identifier

**A per-file exclusion list operates on FILES. An identifier is a STRING, and a string replicates.**

`[measured 2026-09-02, N:\claude-professional-public]` A live Google Drive folder ID
(`1ro48…`, created 2026-07-11) was found at `skills/cross-venue-intake/SKILL.md:65` and the file was
withheld — **overriding a peer's PUBLIC-OK**, on the ground that a folder ID is not PII but an
**access locator**: if the folder is ever link-shared, the ID is the credential. Jon's standing rule
decides it directly — *"Capture the facts, leave the identifiers — where a document lives, not its
account numbers."*

⭐ **The withhold then failed on its own terms.** A tree-wide `grep` for the ID itself found it a
second time, in a file nobody had graded:
`wiki/sources/infrastructure/triage-project-model-direction-2026-07-11-a3e6cf.md:31`. **The
exclusion had removed the file that INTRODUCED the identifier and left the identifier in the tree.**

## The rule

✅ **Every identifier-class withhold triggers a tree-wide grep FOR THE IDENTIFIER, and the exit
criterion is a tree-wide count of zero — not a decision about the file that carried it.**

⚠️ **This is a DIFFERENT rule from walking the reference graph by name** (inbound `[[slug]]` and
path references to an excluded page, or files sharing its session-id suffix). That walk finds
documents that POINT AT the withheld file. **This one walks by VALUE and finds documents that
independently CONTAIN the same string.** A tree can be clean under the first and leaking under the
second: the second file cited no slug, shared no suffix, and referenced nothing — it had simply
recorded the same fact on the same day.

## Why it is easy to miss

**The disclosure decision feels finished the moment the file moves.** The reviewer's attention is on
a per-file list, the log records a per-file row, and the manifest reconciles per file — **every
instrument in the pipeline is file-shaped, and the leak is string-shaped.**

Related: [[the-refuting-artifact-was-in-hand]] · [[a-control-with-no-reader]]
