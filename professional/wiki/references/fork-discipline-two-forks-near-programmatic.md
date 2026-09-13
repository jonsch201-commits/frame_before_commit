---
title: "The two forks of a PR, stated near-programmatically — private and public do not gate each other"
kind: reference
created: 2026-09-07
session: 5f0ee997 (Professional, N:), compact window 2
status: SPEC — every rule below is written to be executed by a script, not interpreted by a seat
origin: Jon, 2026-08-22 13:43:02 CDT, to CFL, session 643640a7 (`~/.claude/history.jsonl:2793`) — the fork discipline is HIS
governs: N:\claude-professional-public (this trunk's derivation), and is offered to CFL for its own
see_also: ["membership-is-not-retrievability.md", "over-dropping-and-under-dropping-are-not-comparable-harms.md"]
---

# R0 — Provenance, because a rule without its origin is a rule nobody can re-open

**Jon, 2026-08-22 13:43:02 CDT, to CFL, verbatim, typos his** (`~/.claude/history.jsonl:2793`;
recorded in CFL's `wiki/DECISIONS.md` as **CFL-D-015**):

> *"Look their WILL be a fork/branch of the github that eventually follows that. Until then? I do not
> trust that the G and github and you would actually have what it needs if it tried to force a rule
> like "no Jon personal/family content in the GitHub" - i do NOT rule it until I can actually see the
> fork/branch whatever of it with this rule so that i can verify the context that would be needed is
> in that and that you can still have the context yuou need!"*

⭐ **READ THE REASON, NOT ONLY THE RULE.** He is not protecting his PII — he says elsewhere he cares
less about it than we do. **He is protecting the seats' working context.** The fork exists so he can
check that de-PII'ing did not cripple the agents. **That makes over-scrubbing the failure this
mechanism is aimed at, and leakage the failure it must also not commit.** Both, or the check is half
a check.

**Status of the rule this unblocks: CFL-D-015 is NOT RULED and has been since 2026-08-22.** It waits
on an inspectable prototype. `[m 2026-09-07]` the prototype has existed since 09-02 and was never
presented.

---

# R1 — TWO FORKS, AND THEY DO NOT GATE EACH OTHER

**Jon, 2026-09-07:** *"you can have the private fork of pr 4 and the public fork of pr 4 they do not
need to gate each other."*

| fork | contents | gate | who owns it |
|---|---|---|---|
| **main** | everything, unmodified, PII intact | none — never edited for publication | the trunk |
| **private fork** | the full PR, complete traces, real names and paths | none from Jon | the trunk |
| **public fork** | derived subset, whole files only | Jon's ONE item (name · org · public-vs-private · first-push scope) | the trunk builds, Jon rules |

⛔ **A seat that holds the private fork waiting on the public fork's gate has serialized two
independent tracks and cost the schedule for nothing.** This trunk did exactly that in its own
reasoning on 2026-09-07 and was corrected within the hour.

**Executable form:** the private-fork build MUST NOT read the public gate's state. If a build script
can observe the gate, it can wait on it. `assert "GATE" not in private_build_inputs`.

---

# R2 — MAIN IS NEVER MODIFIED. THE FORK IS ADDITIVE.

No deletion, no rewrite, no scrub of the working tree. Jon 2026-08-09: *"Yeah no deletion."*
Jon 2026-08-11: *"don't make key PII info harder to use it's often relevent … It's fine in any file
the resident can read."*

**Executable form:** the deriver opens the source tree **read-only** and writes only under the public
root. A run that reports any source-tree mtime change FAILS.

---

# R3 — TWO DISPOSITIONS ONLY: INCLUDE BYTE-IDENTICAL, OR EXCLUDE WHOLE-FILE

From `N:\claude-professional-public\controls\DERIVATION-LOG.md`: *"No file's content was rewritten,
and nothing in the source tree was modified."*

**Why, and it is not squeamishness: a rewritten file cannot be verified.** An included file is
hash-matched to its source and proven unaltered. A rewritten file asks the reader to trust the
scrubber. ⛔ **Trusting a scrubber is the same act as trusting an exit code you piped through `tail`**
— this trunk did that on 2026-09-07 and published a false green twice.

**Executable form:** for every published path, `sha256(public) == sha256(source)`, or the path appears
in the exclusion report with its class. No third state.

---

# R4 — THE FILE IS THE UNIT, SO WRITE MAIN WITH THE SEAM WHERE THE GATE FALLS

R3 makes the include/exclude decision **file-granular**. A page mixing method and personal content
forces an all-or-nothing call, and the honest call is EXCLUDE — losing the method with the personal.

⭐ **So this is an instruction about AUTHORING, not about withholding: in main, file by kind.** A
ruling of Jon's about method belongs in a method source-page and travels whole. The same ruling
quoted inside a page about his family does not. **Nothing is scrubbed; the seam is simply drawn where
the gate already is.**

**Executable form:** a lint over main that flags any file carrying both a `CONTENT_CLASS` hit and a
method-tagged section — a split candidate, reported not auto-split.

---

# R5 — THE TEST IS TWO-SIDED. ONE-SIDED IS NOT A PASS.

| direction | question | instrument | state `[m 2026-09-07]` |
|---|---|---|---|
| **leak** | did anything private reach the public fork? | exclusion classes · armed gazetteer · planted identifiers · `MANIFEST.sha256` | **BUILT** |
| **usability** | *"can you still have the context yuou need"* | **retrieval probes re-run against the derived tree; the method questions must still answer** | ⛔ **NOT BUILT** |

⛔ **The half Jon set as his PRECONDITION FOR RULING is the half with no instrument.** Same category
error as grading PRESENT while the binding claim was RETRIEVABLE.

**Executable form:** `derive_public_tree.py` exits non-zero unless BOTH reports exist. The usability
report names the probe set, the pass count, and every probe that no longer answers **with the file
that would have answered it** — an unusable derivation must say what it cost, not merely that it cost
something.

---

# R6 — VERIFY BY HASH, NEVER BY COUNT

`[measured 2026-09-02 08:07]` a plain `cp -r` produced **1,068 files with correct names, correct tree
shape, and ZERO BYTES in every one**; `find | wc -l` read it as a clean sync. ⭐ **A count-verified
derivation of a de-PII'd tree is the worst instance of that class: it looks complete and it is
empty.**

**Executable form:** `MANIFEST.sha256` is the acceptance artifact. A file count is never one.

---

# R7 — A DEFERRAL IS NOT DISCHARGED BY BEING RECORDED

CFL-D-015 named its unblocking artifact. The artifact was built 09-02. **Nothing was wired to
notice, and sixteen days passed.** This is the decision-form of this trunk's registered class *a
finding is not discharged by being stated*.

**Executable form — the cheapest fix in this file, and it would have caught this exact case:** every
deferred decision carries `unblocked_by: <path or predicate>`. A check walks open deferrals, tests
each predicate, and **fails when a deferral's unblocking artifact exists and the decision is still
open.** Fixture: a deferral pointing at a file that exists must turn the check RED; a control
pointing at a path that does not must stay green.

---

# R8 — THE REQUESTER'S ACCEPTANCE TEST BECOMES A NAMED CHECK BEFORE THE BUILD STARTS

Jon stated a two-sided criterion in prose on 08-22. The builder instrumented **its own** risk model
(leak) and not **his** (usability), and nobody noticed for sixteen days because the prose was never
transcribed.

**Executable form:** a build whose spec quotes a person's acceptance criterion carries one named
check per clause, or the spec is incomplete. **Clauses are counted; unmatched clauses are printed.**

---

# R9 — WHAT REACHES JON IS ONE ITEM, WITH BOTH REPORTS ATTACHED

Name · org · public-vs-private · first-push scope. **One item, not four**
(`N:\claude-professional-public\README.md`). ⛔ **And it does not go until R5's usability report
exists** — asking him to rule on a fork whose *"can you still work"* half was never measured hands
him a decision with half its evidence missing, which is the defect this whole file is about.

---

# What this file does NOT settle

- **Whether the public fork is published at all.** That is Jon's, and *"We might choose to not publish
  if we feel it is unreasonable to do so by the date."*
- **CFL's derivation.** CFL owns its side. This is offered, not imposed — **and whether it is worth
  taking is CFL's judgment, not this trunk's to assert.** `[Jon, 2026-09-07: "Whos to say but those
  whom are to be advised?"]`
- **The exclusion set's contents.** Read from `public_exclusions.txt` by sha, never inferred from
  repo prose. Changing it is a separate, logged act.
