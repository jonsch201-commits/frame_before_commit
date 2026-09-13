---
title: The Wiki Audit Program, Explained From Scratch
trunk: fl
branch: [cfl]
sub_branch: [wiki]
branch_reason: "R-REF; sub: wiki 3 vs skills 0 on authored labels"
status: onboarding doc — assumes zero prior context (for a fresh session or a first-time reader)
authored_by: claude-opus-4-8 (CC session da51cc, 2026-07-13)
---

# The Wiki Audit Program, Explained From Scratch

*If you have never seen this project before, start here. No prior context assumed. Terms are defined
as they appear.*

## What this project is

Jon keeps a **wiki** — a large collection of plain-text (Markdown) files kept under version control
(git). It works as an **external memory** for an AI assistant that helps him across many separate
conversations. Each new conversation starts with no memory of the last one, so anything worth keeping is
written down here as files that future sessions can look up. The wiki covers four areas, called
**trunks**: his main AI-tooling project, plus personal life, home/household, and professional (actuarial)
work.

Most of the wiki is made of **source pages**. A source page is a distilled write-up of *one* past
conversation: a short summary, a list of **key claims** (the important facts and decisions from that
conversation), and links to related pages. There are **183** source pages today.

## The problem we are solving

The 183 pages were written over many months at uneven quality. Two concrete problems:

1. **Most claims are not traceable.** A claim on a page usually doesn't say *where in the original
   conversation it came from*, so you can't check whether it's accurate. (About half have no such
   trace.)
2. **Some pages are simply wrong.** In a small test (below) we re-read the original conversation behind
   one page and found **four factual errors and one important omission** that had been sitting in the
   wiki, uncorrected, for months.

So the wiki — the thing meant to be trustworthy memory — currently can't be fully trusted. The goal of
the **audit program** is to bring all 183 pages up to a single, consistent, checkable quality bar, and
to keep new pages there automatically, without demanding much ongoing effort from Jon.

## What we have done so far

- **Written a quality standard** (version 3.0). It precisely defines what a good source page must have:
  the right sections; every key claim traced to its exact spot in the original conversation (a "turn
  citation"); a tag on each claim saying how faithfully it was captured; findability tags so the page
  can be searched for; and a checksum of the original conversation so we can prove it hasn't been
  altered. The standard groups these into four jobs a page must do — be verifiable, be findable, declare
  where it came from, and preserve everything without silent loss.
- **Run a pilot** on one page. Bringing it fully up to standard is what surfaced the 4 errors + 1
  omission. The lesson — and it's the central one — is that **fixing the wiki is a *correctness audit*,
  not cosmetic cleanup.** You only find the errors by re-reading the source.
- **Taken a census.** An automated script inventoried all 183 pages: how big each is, how many claims it
  has, how many other pages depend on it, how old it is, whether its original source still exists, and
  how far it is from the standard. It then scores which pages are most important and riskiest, to fix
  first.

## The next steps, in plain terms

1. **Calibration (happening now).** Before committing to fix all 183 — a large job — fix a carefully
   chosen sample of **12 pages** and *measure* three things: how long each takes, how much it costs, and
   **how often we find errors.** The pilot found errors on 1 page; we need to know if that rate is
   typical (is it 4 of 12? 10 of 12?) before we can responsibly price the full job. The main thing Jon
   reviews is the list of errors found.

2. **Build small tools.** Write programs to automate the *checkable* parts: a "linter" that grades a
   page against the standard, a checksum tool, a running scoreboard ("ledger") of each page's status,
   and — the hardest one — a "claims parser" that reads a page and verifies every claim is properly
   cited. Deterministic work is done by code, not by asking an AI model, so it's cheap and repeatable.

3. **The full sweep.** Fix all 183 pages, most-important-and-riskiest first, at a measured pace, using
   the tools above. New pages are written to standard from the start ("born-at-standard").

## What is deliberately *not* being done without Jon's sign-off

A few larger decisions are held as written proposals ("packets") for Jon to approve — no code until he
does:
- Whether pages that are *syntheses* (concept/analysis pages, not conversation summaries) need their own
  rules — about 20% of the wiki. 
- A "how confident are we this is actually true" tag on claims.
- Special privacy rules for the personal-life pages: **no automated edits there at all** until the rules
  are approved, and personal content is never copied into shared logs.

## Where things stand right now
The standard is ratified and the census is done and approved. The immediate next action is running the
12-page calibration and reporting the errors found plus the measurements — which is what prices
everything after it.
