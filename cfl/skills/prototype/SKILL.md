---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered — from the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file — free-play buttons plus tabbed guided walkthroughs — that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

The two branches produce very different artifacts — getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious — but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner — `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file the user double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE — wipe me" name.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Capture it when done.** Fold any validated decision into the real code, then capture the prototype itself as a **primary source**: commit it to a throwaway branch, out of main, and leave a context pointer to that branch on the implementation issue. Capture the answer too — the verdict and the question it settled — in the issue or a commit. The main branch keeps only the validated decision.

---

## CFL Adaptation Note (appended 2026-08-31; upstream body above is VERBATIM, commit 84fdeff)

Adopted at Jon's direction, live at the PR-3 sitting: *"prototype should be a skill from matt
pocock and it didn't trigger."* Vetted per `~/.claude/skills/UPSTREAM.md` step 3 the same hour:
no auto-exec vectors, no network/credential/destructive content (TRUE-EXIT=1 on both greps,
after re-running the second unpiped — the first run's exit was masked by `head`).

Substitutions for this machine:

- **"the implementation issue" / issue tracker** → the live wayfinder map's decision rows
  (`wiki/tracker/wayfinder-*.md`, `status: LIVE`) or `wiki/tracker/projects.md`. The context
  pointer to the prototype goes there.
- **Throwaway branch** → `proto/<name>`, built in an OFF-Drive worktree
  (`%LOCALAPPDATA%\Temp\claude\wt-*`, core.longpaths, empty-porcelain check first — on-Drive
  worktrees poison cold reads). The branch is KEPT after capture, never deleted (no-deletion
  rule governs; rule 6's "main keeps only the validated decision" means main, not history).
- **Instrument-shaped questions** (most CFL prototypes are scripts, not UIs): the LOGIC
  branch's "single HTML file" substitutes as **a single runnable script plus its measured
  output** — Jon ruling 1, 2026-08-31: a ticket closes on a RUNNING artifact + measured
  output, never on text. The HTML free-play form stays right for anything Jon himself will
  drive by hand.
- **Rule 6 ("capture it when done") composes with CFL's record pipeline:** the verdict and
  the question it settled are a `[measured]` row on the map, and the prototype is a primary
  source — the same standard as every other instrument here.
