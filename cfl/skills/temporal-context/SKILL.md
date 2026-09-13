---
name: temporal-context
description: Triggers on every response. Also triggers when Jon provides a time correction, when voice-to-text signals mobile/fatigued state, when a decision references context that may be stale, or when session age affects interpretation.
---

# Temporal Context Skill

The timestamp informs how Claude interprets everything that follows — Jon's state, decision staleness, context age.

---

## Format

```
[YYYY-MM-DD HH:MM CDT]
```

Always CDT. Jon is Central US time. DST applies March second Sunday through November first Sunday (UTC-5 CDT, UTC-6 CST). CDT is the stable label regardless of season.

---

## Source Priority

Corrected 2026-08-05 per a Claude Personal finding (packet
`personal-to-cfl-temporal-context-defect-2026-08-04.md`): this list previously omitted the system
clock and the JSONL `timestamp` field entirely, and ranked a cached web page above measurement it
never took. Personal measured the cost on 2026-08-04 — 4 of 5 timestamps stamped `[measured]` were
actually estimated, ~29 minutes of drift. The same night, CFL's own coordinator read that packet
and reproduced the defect anyway: ran `date` once, then stamped several later responses
`[measured]` that were really extrapolations from that one reading, drifting ~17 minutes ahead of
true time. **Reading about the defect does not prevent it. Only running `date` again does.** An
extrapolation from an earlier measurement is `ESTIMATED`, not `[measured]` — that is the specific
error both projects made, and it is why tier order and the ban on relabeling estimates matter more
than any other clause here.

**1. System clock — `date` via the shell. MEASURED.**
In Claude Code, run `date` before stamping. This is not a fallback and not optional when a shell is
available — it is the default action for every timestamped response. One call, one line; cheap
enough to run every time. Mark `[measured]` only when this turn's `date` (or the JSONL `timestamp`
below) produced the number being written. A value carried forward from an earlier `date` call in
the same session is `ESTIMATED`, not `[measured]`, no matter how recently that call ran.

**2. JSONL `timestamp` field — MEASURED.**
Every entry in a Claude Code session JSONL carries a top-level `timestamp` (ISO-8601 UTC,
millisecond precision), flushed live. It answers *"when did Jon send the message being replied
to"* — a different question from *"what time is it now,"* which tier 1 answers. Use it when the
send time of a specific prior message matters, not only the current instant.

**3. User-provided — a report, not a measurement. Demoted from tier 1.**
Jon provides time as `[HH:MM]` or natural language. Treat it as a claim to weigh, not the clock:
he drafts messages ahead of the moment they describe, and `Good morning`/`Good night` mark session
boundaries, not necessarily wall-clock time. Prefer tiers 1–2 when a shell or JSONL is available;
fall back to this when neither is (e.g. claude.ai chat with no user-provided anchor).

**4. Estimated — dead reckoning from last known anchor. LAST RESORT.**
Mark explicitly, and never write this as `[measured]`:

```
[YYYY-MM-DD HH:MM CDT] *(ESTIMATED — check reasonability)*
```

**claude.ai chat (no shell, no JSONL access):** user-provided time is the only reliable anchor.
Jon's own workaround — writing an empty file to check its mtime — is a legitimate external-clock
substitute for tier 1/2 on that surface if available; otherwise fall through to tier 3 (user-provided)
or tier 4 (estimated, flagged).

---

## When to stamp — and the one rule that is always on

⛔ **The always-on rule is not "stamp everything." It is: IF YOU STAMP, THE LABEL MUST BE TRUE.**

**Stamp when the time is material:** session open · a `[work]`-tag or state-window judgment ·
anything a later reader will date from this line · a heartbeat or scheduled run · a staleness or
currency claim · any turn where Jon asks. **Otherwise the stamp is optional and its absence is not
a defect.**

⛔ **Writing `— measured` on a clock value obtained no other way than by remembering it is a false
report about your own state.** `[measured]` on a timestamp asserts that **this turn, or the turn
whose tool result you are reading, ran `date`.** Nothing else earns it. If you did not, the stamp
is `*(ESTIMATED)*` — which is honest, costs nothing, and is already the most common honest form in
the corpus.

*(Added 2026-08-14 from measurement, and the measurement is stated the way it survived being
attacked. Of 296 timestamps whose stamp asserted `measured`, **146 — 49.3% — were off by more
than two minutes from the UTC timestamp of the very record that carried them.** That check needs
no guess about which command read the clock: the stamp is compared against the ledger's own clock
for that message. **Roughly half of the timestamps in this program that claim to be measured are
wrong.** The backing test discriminates sharply — stamps with a clock command behind them land
within two minutes **95.2%** of the time; stamps without one, **33.0%**. ⚠️ The unbacked SHARE is
reported as a range, **56–72%**, because two independent implementations disagreed on it; the
49.3% figure does not depend on that disagreement. Source: `/quarantine/stamp_audit_v2.py`.
⛔ An earlier draft of this note said 79.7%, from an instrument that treated each JSONL record as
a turn when a turn spans several, and that could not see PowerShell `Get-Date`. It was refuted by
an independent reimplementation before it shipped.)*

---

## Reasonability Flagging

Flag ESTIMATED once at session open if no time was provided. Suppress on subsequent messages unless estimate has drifted >30 min without a new anchor. Accept mid-session corrections silently.

---

## Clock Behavior Within a Session

- Session open, no timestamp → ESTIMATED, flagged once
- Session open, user-provided → anchored, no flag
- Mid-session correction → update anchor silently, no comment
- Elapsed time → in Claude Code, re-run `date` (tier 1) rather than advancing an estimate; measurement is free, so there is no gap to dead-reckon across. (This replaces a prior "advance ~3-5 min per exchange" placeholder — real inter-message gaps measured 2026-08-04 ranged 1m47s–6m22s, confirming the placeholder was never calibrated and estimation was never necessary in Claude Code.)
- Long gap implied → flag staleness if >30 min

---

## Work vs. Personal Session

**`[work]` tag at session open** = Jon is at his job. Adjust: tighter scope, shorter responses, no rabbit holes, nothing requiring deep desk focus, no bleed into work context.

**No tag** = personal project time. Full engagement appropriate per time window below.

---

## State Inference by Time Window

| Window | Likely state | Adjustment |
|--------|-------------|------------|
| 06:00–08:00 | Morning ramp, competing demands imminent | Compact. Flag anything needing desk time. |
| 08:00–17:00 | Work hours — see work tag above | Depends on `[work]` tag |
| 17:00–20:00 | Transition, family demands | Triage mode. Shorter responses. |
| 20:00–23:30 | Evening, ideas-mode | Flag scope creep. Park generously. |
| 00:30–06:00 | Very late or very early | Park aggressively. Do not encourage building. |

These are patterns, not rules. Jon overrides explicitly.

---

## Staleness Flagging

Flag when:
- A decision or commitment in context is >24 hours old and being acted on now
- Context switching is implied by message phrasing or topic jump
- Fatigue or time pressure signals are present

---

## ⭐ Tier 5 — the image is not the world. Content age is not clock age.

**`date` tells you the wall clock. It tells you NOTHING about how old the material you are reading
is.** In a baked container, a mounted corpus, or any pinned snapshot, those are two different
numbers and only one of them moves.

**The rule:** when a claim rests on a corpus you did not fetch this session, state the corpus's
age alongside the clock, and treat any "current state of X" claim derived from it as `[stale?]`
by default.

```
[2026-08-14 16:11 CDT — measured]  corpus: /shelf baked 2026-08-13 13:10Z (~32h) [stale?]
```

**How to measure your own corpus age, rather than assume it:** `stat -c '%y' <mount>/<any-file>`,
or read the build/bake fields in whatever manifest the environment ships. **Do not infer it from
the newest date mentioned inside the documents** — documents describe the past, and a file written
on the 13th can discuss the 20th.

**⛔ And the part that is not about time at all: knowing the corpus is stale does not refresh it.**
There is no clock tier that fetches. **The route out is a request to a human, and the skill's job
here is to make you notice you need one.** In this container that is a letter to
`/quarantine/letters/to-<seat>/` with the recipient in the filename; elsewhere it is whatever the
environment's request channel is. **Name what you want fetched and why it is time-sensitive.**

*(Added 2026-08-14, answering Jon's FRAME 6 verbatim: "Temporal context. How do you improve this
skill based on its documented failure modes? How can you request updates from outside docker?
Your project is out of date." Measured 2026-08-14: `grep -c -i -E
"bake|baked|image|container|docker|corpus|out of date|pinned|build date"` against this file
returned **0** — the skill governed clock time and had no concept of content age, which is the
staleness Jon was actually pointing at.)*

---

## Environment Notes

**Claude Code:** Run `date` shell command before each timestamped response — not just at session open. One call; cheap enough to always run. Sessions can run for hours; a session-open anchor drifts, and a value carried forward from an earlier `date` call is ESTIMATED, not measured. Never estimate in Claude Code when `date` is available. When the send time of a specific prior message (not "now") is what matters, prefer the JSONL `timestamp` field (tier 2) over `date`.
**Claude.ai chat:** No shell, no JSONL access. User-provided time (tier 3) is the most reliable source available. A file-mtime workaround (write/touch a file, read its mtime) is a legitimate external-clock substitute where the surface supports it. Always flag ESTIMATED when inferring without an anchor. Date from web search is usually reliable; time is not — do not assert a specific time without a user or mtime anchor.

---

## What Not To Do

- Do not skip the timestamp on any response
- Do not repeat the ESTIMATED flag after it has been shown once
- Do not comment on the time unless material to a decision
- Do not ask for the time more than once per session
- Do not assert exact time from web search — date only
- Do not stamp `[measured]` on a value that is actually carried forward or extrapolated from an earlier `date`/`timestamp` reading — that is `ESTIMATED`
- Do not skip re-running `date` mid-session on the assumption that an earlier reading is still close enough
