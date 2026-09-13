---
title: "Membership is not retrievability — an index that contains a document and cannot reach inside it"
kind: concept
created: 2026-09-07
session: 5f0ee997 (Professional, N:), compact window 2
status: measured
class: capability-claim-graded-as-existence-claim
see_also: ["salient-is-not-critical-retrieval-escalation.md", "grounding-principles.md"]
---

# The class

**A retrieval index can hold a document, report it PRESENT, rank it, return it as a hit — and be
unable to reach a single sentence inside it.** Membership is an EXISTENCE claim. *"A fresh context
window can find the right place in this document"* is a CAPABILITY claim. **A capability claim fails
by never having been run, so the fix is a test, not a paragraph** — and an acceptance instrument that
checks membership will certify the capability it never measured.

This is the same defect as a peer review that records a disposition without recording whether the
reviewer RAN the artifact or READ it. One field, never captured, and the record cannot tell a strong
approval from a weak one.

# The instance, measured 2026-09-07

CFL's graph index, `C:\Users\JonSc\AppData\Local\claude\graphrag\index.sqlite`, built
2026-09-07T20:20:04Z, 116,335 chunks, `corpus_root = N:/claude-cfl/clone`.

`scripts/graphrag/build_index.py:958-961` — its own comment, verbatim:

```
# Provenance files are indexed DOC-LEVEL ONLY -- one chunk, one vector, no body chunks.
# See PROVENANCE_DIRS: body-chunking 4,376 transcripts would add ~100k chunks to a 16k
# index. The chunk's line span is 1..EOF and that is honest: the span IS the file.
```

| measured | value |
|---|---|
| CFL N2 C0 wikiskills transcript | 297,592 B → **1 chunk, 2,320 chars indexed = 0.78%** |
| CFL N1 seat's whole-day transcript | 3,784,000 B → **1 chunk, 2,351 chars = 0.062%** |
| provenance files > 100 KB that are single-chunk | **1,943 of 1,943 = 100%** |
| knowledge tier, same test | 0 of 22 |
| queue tier, same test | 0 of 115 |
| provenance tier as a whole | 817,832,808 corpus bytes → 11,424,501 indexed chars = **1.3969%** |

**The falsifier, run twice, both RED.** A phrase present verbatim in exactly one corpus file
(`grep -rlF` returns one path) was **absent from the top 20** under `--scope provenance` and under
`--all-tiers`. A second probe on a subagent render was absent from the top 10, outranked by a chat
about a solar provider and one about park-district activities.

**The document was a hit in earlier queries.** It matched on the 2.3 KB summary standing in for
297 KB of body. That is what makes the class dangerous: the index does not go quiet. It answers.

# Why the reasoning expired rather than was wrong

The comment's arithmetic was correct when written: body-chunking the archive at `MAX_CHARS = 1400`
is on the order of **580,000 chunks against 116,335** — roughly a 5× index. **The constant did not
become false. Its PURPOSE changed** — the moment raw session logs stopped being an archive to
preserve and became the corpus a fleet is asked to *trace through*, doc-level indexing stopped being
a thrifty choice about storage and became a silent exclusion of the primary evidence.

⭐ **Same shape as the hardcoded corpus root fixed the same morning** (an absolute path whose reason
expired when the checkout moved). One of the pair was found and shipped as the root cause; its
structural twin sat three files away, and the twin was the one binding the instruction.

# The detector, so this is an artifact and not an insight

1. **Any coverage or acceptance instrument reports RETRIEVABLE beside PRESENT, never blended.**
   RETRIEVABLE is earned by querying a verbatim phrase from the document's own last 25% and
   requiring the document itself in top-k. PRESENT stays as the membership grade.
2. **A retriever prints the chunking mode of every hit.** A hit whose span is `1..EOF` on a large
   file says `doc-level: body not indexed`, in the same line as freshness. **An exclusion the caller
   cannot see is the whole defect**; whether it is by tier or by chunking is a detail.
3. **Before citing a retrieved document as evidence, check the span.** `1..EOF` on a large file means
   the hit is a filename, not a passage — escalate to a direct read of the primary, per
   `salient-is-not-critical-retrieval-escalation.md`.

# Jon asked this, in these words, twelve hours before it was measured

`exchange/inbound/ASK-JON-ARRIVAL-2026-09-07-0310-step-4635.md`, captured 2026-09-07T03:07:57Z,
verbatim, typos his:

> *"you are saying the json has the metadata neeeded for graph rag to work as intended through the
> raw conversations? YOu have framed things a certain way. What alternitive frames should you have
> considered before you committed? Or, can you use the tool that you just built to litteraly trace
> to the words you replied to mme - rather could a fresh context window without using the json
> directly just query the graph to find the right context? Or - is the transcrfipt at least easy to
> read and the graph points to the right place in context and has the metadata in it?"*

**Measured answer to his three branches: the transcript is easy to read; the graph does NOT point to
the right place in context — it points to the file, span 1..EOF, on a 2.3 KB summary; and a fresh
window querying the graph instead of the JSONL is NO today.** His middle branch is the acceptance
test the fleet needs and did not have.
