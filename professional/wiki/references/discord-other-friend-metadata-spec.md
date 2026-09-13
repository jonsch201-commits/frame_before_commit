---
title: Stripping other-friend metadata from the Discord extract — measured schema, and why most of this is not a model problem
created: 2026-08-23
kind: reference
owner: professional
re: Jon's Ollama chain, link 2. SEC-114.
consent-basis: see §0. This rests on third-party consent, NOT on Jon's 2026-08-19 PII amendment.
---

# 0 · ⛔ The consent basis, stated first because it does not travel with the other PII rules

**Jon's 2026-08-19 amendment relaxed concerns about HIS OWN PII on non-public surfaces** — his C:, G:,
D:, and his own private repos are one trust zone. ⛔ **That amendment does not reach this artifact.**

**A Discord extract is other people's conversation.** The people in it agreed to nothing, and the
third-party-consent rule rests on that basis rather than on a PII basis — so it survives the
amendment untouched, exactly as the family-member rule and the money-identifier rule do.

⚠️ **The failure mode is one careless paragraph away at all times: "Jon's PII is fine here" becoming
"everyone's is."** It is written at the top of this file so that a future reader who quotes any other
section has to walk past it.

**What was done to produce this page:** keys and types only, plus counts of distinct ids. **No
message text was read, no person's name was read, and none appears here.**

# 1 · What exists, measured

`[measured 2026-08-23]` `D:\My Tone Agent project\discord_export` — **906.5 MB, 173 files**,
exported 2026-03-22. ⚠️ **It is NOT the official Discord export format**: it is DiscordChatExporter
output, one flat JSON per channel. Anything written against `messages/`, `channel.json` and
`index.json` will not run against it.

⭐ **There is prior art and it is the same corpus:** CFL's Stylomantic POC (2026-03-22 onward) already
ran *Discord history → Gemma 2 via Ollama* over this data for tone modelling. **This is the second
consumer of the extract, not the first.**

# 2 · The identity surface — FIVE locations, not one

Measured from the message schema, not assumed:

| # | where identity lives | fields |
|---|---|---|
| 1 | `message.author` | `id`, `name`, `discriminator`, `nickname`, `avatarUrl`, `color`, `roles[].name` |
| 2 | `message.mentions[]` | same seven fields, per mentioned person |
| 3 | `message.reactions[].users[]` | same, per reacting person — **an identity surface most designs forget entirely** |
| 4 | `message.attachments[]` | `fileName`, `url` — uploaded filenames routinely carry names |
| 5 | ⛔ **the channel name and the FILE name** | `channel.name`, `guild.name`, and the `.json` filename itself |

⛔ **ROW 5 IS THE ONE THAT BREAKS A CONTENT-ONLY SCRUBBER, AND IT IS NOT HYPOTHETICAL HERE:** the
export's own filenames are built from per-person channel names. **A scrubber that reads file contents
and never file paths leaves every person fully identified by the name of the file its redacted output
is written to.**

⭐ **This independently reproduces CFL's P2-6 in a different corpus** — their de-PII prototype's one
known defect is *nine files leak names in filenames* because *"the scrubber reads content only, never
paths."* **Two corpora, same defect, discovered separately. That is a defect CLASS, and the general
form is: a redaction pass scoped to file CONTENTS treats the filesystem as metadata rather than as
part of the record.**

# 3 · ⭐ The design finding: most of this is not a model problem

**Jon's chain reads *"using OLLAMA to get all other-friend metadata out of Discord extract."* The
measured schema says the local model is needed for a minority of the work, and saying so is cheaper
and more testable than building the obvious thing.**

- **Locations 1–5 are STRUCTURED.** Every identity is a named field at a known path with a stable
  numeric `id`. Stripping them is a **deterministic transform with 100% recall by construction** —
  not a judgement, not an inference, and not something an LLM should be asked to do. An LLM asked to
  do it has recall below 100% and no way to prove otherwise.
- ⭐ **The right transform is PSEUDONYMISATION, not deletion, and `id` is what makes it possible.**
  Map each `id` to a stable handle (`FRIEND-07`) in a side table Jon keeps. **Who-said-what threading
  survives, reply chains survive, reaction attribution survives — and the conversation stays useful.**
  Deletion destroys the thing being protected, which is the whole content of Jon's *"don't make key
  PII info harder to use it's often relevent."*
- ⛔ **The model earns its place on exactly one field: `message.content`,** where names appear inline
  in free text, misspelled, nicknamed, and inflected. **That is a genuine judgement task with
  unmeasurable recall — which is precisely why it must be the small residual and not the whole job.**

**So the pipeline is: deterministic pass first (5 locations, provable), local model second (1 field,
bounded), and the model never touches what the deterministic pass already guarantees.**

# 4 · Requirements inherited, not invented

From CFL's shipped link 1 (`scripts/pii/ollama_strip.py`), adopted rather than re-derived:

1. ⛔ **BOTH DIRECTIONS OR IT IS NOT TESTED.** A leak control AND an over-scrub control.
   **A tool that deleted everything scores zero PII violations** — without the second control, the
   selftest passes for exactly that tool. Over-scrubbing is a violation in its own right, per Jon
   2026-08-11.
2. ⛔ **No `--in-place`; refuse `infile == outfile`.** **The source is the only evidence of what a
   redaction removed** — destroy it and over-scrubbing becomes permanently unmeasurable. This is not
   only a data-loss guard; it preserves the ability to detect the other failure mode at all.
3. **An empty model response is a FAILURE, never "nothing needed redacting."** A passthrough that
   reads as a redaction is the worst outcome available. ⭐ **Third instance of this fail-open shape
   this week** (CFL's N1, this trunk's N3, and now this) — **the class is: a no-op that returns
   success.**
4. **HTTP API at `127.0.0.1:11434/api/generate` with `{"stream": false}`** — the `ollama run` CLI
   floods stdout with spinner escape codes. Cold load of a 5.4 GB model exceeds two minutes; **a
   cold-start timeout is not a failure.**
5. **State recall honestly.** A seeded probe proves the mechanism, not coverage. ⛔ **And that bound
   bites hardest HERE: a seeded probe contains the identifiers you thought to seed, and other
   people's names in a years-old chat log are exactly the class nobody can enumerate in advance.**

# 5 · Local capacity, measured

`[measured]` Ollama **0.32.15**, running. Models: `gemma2:latest` 5.4 GB · `deepseek-r1:32b` 19 GB ·
`wiki-master:latest` 19 GB — **23.56 GB store**. Free: **C: 57.9 GB · D: 1,330 GB**.
**No pull is needed; nothing must be installed.** ⚠️ The extract lives on D: and the model store on
C:; a run that copies 906 MB to C: for convenience is the one avoidable disk risk here.

# 6 · What is NOT settled, and needs Jon rather than a lane

1. **What "other-friend metadata" means to him** — pseudonymise (threading survives) or remove
   entirely (conversation degrades)? **§3 argues pseudonymise, and the argument is his own ruling
   about not making things harder to use. He may still want removal for a specific surface.**
2. **Whether the id→handle map is retained.** Retained, it is reversible and therefore still
   third-party data. Discarded, the transform is one-way and the corpus can never be re-joined.
   **This is the real decision in the ticket and it is not a technical one.**
