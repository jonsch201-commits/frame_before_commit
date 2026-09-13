---
name: transcript-parser
description: Parses the claude.ai data-export zip into the mirror corpus — one markdown file per conversation, incremental on (uuid, updated_at). Wraps the existing convert-export.py extractor (no second extractor). Use when refreshing the fable-mirror corpus after Jon downloads an export zip, or when the standard update runs the corpus-refresh step. Produces the read-only corpus the fable-mirror agent consults. Ratified 2026-07-21 (fable-mirror pipeline, items 9–11 + stub amendments).
---

# transcript-parser

Turns a claude.ai **data-export zip** into the **mirror corpus**: one markdown file
per conversation, refreshed incrementally. The corpus is what the `fable-mirror`
agent reads — nothing else writes to it.

This skill **wraps existing code**. It does not contain a parser. Per the 2026-07-21
ratification, there is exactly one extractor: `skills/chat-exporter/scripts/convert-export.py`.
The only addition is a manifest-diff wrapper so the refresh is incremental and correctly
re-parses **updated** conversations.

## Pipeline

1. **Jon downloads the export zip** (manual — no programmatic trigger exists) and unzips
   it to a directory containing `conversations.json`.
2. **Diff + parse** (zero-token, pure Python):
   ```
   python scripts/lanes/transcript_corpus_diff.py <export-dir>
   ```
   This computes `{uuid: updated_at}` from `conversations.json`, diffs it against the
   saved manifest, and calls `convert-export.py --run --ids <new+changed> --force` for
   only the conversations that are new or whose `updated_at` moved. No delta → no-op.
3. The corpus lands in the **corpus location** (below). The manifest lives **off-Drive**
   (state dir), matching the nightly-lane pattern (MEMORY: Drive-lag stale reads).

## Manifest-v2 sidecar files (2026-07-24) — naming note

`convert-export.py` now also writes a `<conversation>.sidecar.md` companion per
conversation by default (block timestamps, untruncated tool-read log, attachment
text, thinking fidelity, branch metadata — additive only, primary-file turn numbers
unchanged). It is deliberately called a **sidecar**, not a "manifest," to avoid
colliding with *this* skill's own "manifest" term below (the `transcript_corpus_diff.py`
uuid:updated_at diff-state file) — "manifest-v2" is the feature/field-set name; the
per-conversation artifact is the sidecar. See `skills/chat-exporter/SKILL.md` for the
field list. This wrapper's diff/incremental logic is unaffected — it still targets
`convert-export.py --run`; sidecars ride along with whatever primary files get written.

## The one real code gap this fixes

`convert-export.py`'s own incremental (`existing_uuid_prefixes`) skips a conversation if a
file with its 6-char uuid prefix already exists — so an **updated** conversation (new turns
appended) is **silently skipped**. The mirror would then answer from a stale transcript.
`transcript_corpus_diff.py` keys on `(uuid, updated_at)` instead, so edited conversations
re-parse. This is a sibling of Stage-1 Leg 1's zero-token manifest diff
(`scripts/lanes/nightly_corpus_delta.py`), not a new extractor.

## Corpus location

- **Gitignored, on-Drive.** `raw/transcripts/` (covered by the `raw/` gitignore), organized per
  Record Architecture v1 as `{claude-ai,claude-code,external}/{fl,personal,pro,home}/<branch>/`,
  plus `_routing/{incoming,ambiguous}/` per venue and a shared `_superseded/`. This is the
  **2026-07-28 L1 move**: the corpus root moved from `raw/sessions/` (which held the leaf-name
  question and open ratification this section used to describe) to `raw/transcripts/`.
  `raw/sessions/` is now empty except a `POINTER.md` (`.claude/agents/fable-mirror.md:25-26`,
  corrected 2026-07-30). The move is ratified and landed — the leaf-name question this section
  previously described as unadjudicated is resolved by the move itself. The corpus is the
  *entire* claude.ai and CC history — personal, home, faith included — so it is **never pushed
  to GitHub**. The `fable-mirror` agent is CC-resident and reads it from local disk; the
  claude.ai connector is served separately by the `canonical` branch, not by this corpus.
- **One canonical location.** `raw/transcripts/` is the one corpus root; the subdirectories under
  it are organizational, not competing copies. Drive surfaces are included per the standing
  canonical-copy rule; no second copy.
- **Unified-sources model.** Jon rejected a hard raw/sources firewall ("treat all as sources,
  just of different categories"). The corpus is the *gitignored bulk* source category; the
  *material* subset is curated into the tracked wiki by wiki-master judgment (existing ingest
  path). A full raw→sources taxonomy unification is queued for wiki-master.
- **Read-only to everyone except this parser.** No agent writes to the corpus.

## Thinking blocks — mandatory first diagnostic (stub amendment i)

Jon's belief that thinking blocks are in the export was `[JON/instinct]`; it is now
**verified** — `convert-export.py` records 773 thinking blocks across a 173-conversation
export (2026-07-12). They are preserved by default as `<details>` collapsibles, and every
file's frontmatter carries `thinking_blocks: preserved | omitted (N) | none`, so their
presence is **never silent**.

The wrapper still runs the diagnostic on **every** parse: it inspects `conversations.json`
content-block types. **If a non-empty export contains zero `thinking` blocks, the wrapper
REFUSES to build and escalates to Jon** — it never silently produces a transcripts-only
corpus. (Export schemas change; the verification above is a snapshot, not a guarantee.)

## Provenance grades (stub amendment ii) — for the mirror and for citations

Two grades, ordered, double-discount mandatory:

- `[TRANSCRIPT:date]` — a claim grounded in a **visible** turn. Stronger.
- `[THINKING-SUMMARY:date]` — a claim grounded in a **thinking block**. Weaker, because a
  thinking block is a *displayed summary*, not 1:1 with the underlying reasoning tokens: it is
  a paraphrase of reasoning, read by an interpreter, about another interpreter. Discount twice,
  not once.

Corpus is **lossy and never authoritative over the wiki**: exports can silently miss assistant
replies, drop deleted conversations, and drop project structure. **On any conflict, the wiki
wins.** Freshness is always stamped: "corpus current through export YYYY-MM-DD."

## Landing proposal for wiki-master

- Corpus dir: `raw/transcripts/` (gitignored) — landed via the 2026-07-28 L1 move, per
  `.claude/agents/fable-mirror.md:25-26`. The gitignored + one-canonical-location + read-only +
  wiki-wins-on-conflict properties are fixed by Jon's 2026-07-21 ratification; the path itself is
  now also settled by the landed move, not open.
- Material-subset curation into tracked `wiki/sources/` remains wiki-master's ingest, by
  judgment (Jon delegated the materiality call).

## Do not

- Do not write a second extractor. Reuse `convert-export.py`.
- Do not push the corpus to GitHub (keep it gitignored).
- Do not let any agent but this parser write to the corpus.
- Do not treat the corpus as authoritative over the wiki.
