---
name: su-compact
description: "[CLAUDE PROFESSIONAL ONLY] Session-close ritual for the Professional trunk — durable record, verify, commit, then hand Jon the /compact block. DOES NOT ITSELF COMPACT; step 4 gives Jon the invocation and says the version he pastes is the one that runs. Contract matches CFL's, NOT Personal's — Personal's step 4 invokes /compact directly, so the same six characters mean different things in different windows. This repo has NO REMOTE by standing gate: the close ends at the commit, never a push. Written 2026-08-07 in Professional; verify steps are Professional's own because CFL's and Personal's name instruments this repo does not contain. Not synced."
argument-hint: "[optional: YYYY-MM-DD]"
arguments: as_of
disable-model-invocation: true
shell: bash
allowed-tools: Bash(git add*), Bash(git commit*), Bash(git status*), Bash(git log*), Bash(git rev-parse*), Bash(git remote*), Bash(ls*), Bash(wc*), Bash(stat*), Bash(grep*), Read, Grep, Glob, Write, Edit
---

**This command belongs to Claude Professional** (`G:\My Drive\Claude\Claude Professional\claude-professional`).

**Confirm the repo before running it.** `git rev-parse --show-toplevel` must end in
`claude-professional`. If it does not, you have resolved a sibling's command; stop. CFL's and
Personal's versions of this command specify instruments this repo does not contain — `gen_index.py`,
`lint.sh`, `capture_all_jsonl.py`, `su_gate.sh`. This repo's `scripts/` holds `asop.sh` and
`fetch_asops.sh`. See `wiki/concepts/ownership-is-not-reachability.md`.

Four steps, fixed order. Do not reach step 4 early. Context is full now — this is when to write, not
after.

---

## 1 — Durable record

Everything from this session that belongs in the wiki, written to these targets:

- **`wiki/log.md`** — append this session's close entry, including the re-grounding receipt from
  `/wake` step 8 if this session has not already logged one. Errors belong here on purpose. A session
  that logs no error has either had none or has not looked.
- **`wiki/concepts/`** — any finding that will outlive this session. One page per finding, with a
  provenance grade in the frontmatter.
- **`wiki/index.md`** — this project has no index generator. Update it by hand, then reconcile:
  `ls -1 wiki/concepts/ | wc -l` must equal the number of rows in the Concepts table. An index that
  lists fewer pages than exist on disk is the same staleness defect as a tracker that lists a closed
  ticket as open; both have occurred here.
- **`wiki/tracker/tracker.md`** and any wayfinder map or ticket this session opened or closed. Close
  the rows. A map that describes a resolved ticket as open will cause the next session to re-run it.
- **`WAKE.md`** — refresh `AS OF`, the gates, `DO NOT REDO`, and the resume point. Keep it at or under
  6,144 bytes; if it has outgrown that, move detail into a wiki page and leave a pointer.

## 2 — Verify

This project has no lint script. These are the checks that exist:

- **Index/disk reconciliation** — the count from step 1. Report both numbers.
- **Concept pages resolve** — every `[[slug]]` in `wiki/index.md` has a matching file in
  `wiki/concepts/`.
- **Delivery, receiver-side** — for every letter this session deposited into a sibling's
  `exchange/inbound/`, confirm the file exists at the target path with a non-zero byte count, measured
  from the receiver's tree. A write that creates its own destination is indistinguishable from a
  successful delivery; this project learned that on its first day by writing to
  `G:\My Drive\Herald Wiki\herald-wiki`, a path with no `.git` and no reader.
- **No remote** — `git remote -v` empty. Standing gate.

Report each as a number or a pass/fail, not as an assurance.

## 3 — Commit

Stage the exact paths this session touched. Do not use `git add -A` while background agents are live.
Commit in this repo's existing message convention — check `git log` for the current pattern.

**Do not push. There is no remote and adding one is a Jon gate.** The close is complete at the commit.

## 4 — Only then: the `/compact` block

Before handing this to Jon, consider a `fable-mirror` consult on anything claim-bearing this session
produced that has not yet been checked against the corpus. The trigger is not only publication — it
also fires where a message of Jon's admitted more than one reading and the corpus plausibly holds the
same shape.

Then give Jon the invocation. **State that it is a suggestion and that the version he pastes is the
one that runs** — a close whose final step is "Jon pastes this text" puts a human in the loop at the
moment the human is out of context, and that step has failed before.

Carry preserve-verbatim **classes**, not an item list. A class survives a session that produced
something the list never anticipated:

> Absolute file paths, exactly as written. All numbers, dates, and measured counts — byte sizes, file
> counts, sha256 fragments, deadlines. A number restated approximately is worse than one dropped,
> because it still reads as fact. Jon's directives and rulings in his words, with their qualifiers.
> Standing prohibitions — anything phrased as never, do not, or only. The fence on disclosure
> judgment calls and the family exemption from it. Anything dropped, deferred, held, or gated, and
> what it waits on. Errors logged this session. Open questions Jon has not answered.

And the bridge sentence:

> After the boundary, read `WAKE.md`, then `BRIEFING-2026-08-07.md`, then `exchange/inbound/` before
> acting. Run `CronList` — recreate the heartbeat only if absent.

---

**What this serves:** a boundary the next session can cross without needing anything that is not in
the wiki. Steps 1–3 make that true at the moment of compaction; step 4 makes the boundary survivable
if it is not quite true yet.
