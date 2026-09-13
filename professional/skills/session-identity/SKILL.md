---
name: session-identity
description: "Measured IDENTITY pages for every session and subagent JSONL of this trunk — no defaulted field, UNKNOWN where unreadable, Jon's turns as their own measured column. Use at every compact barrier and at wake (`--coverage` must print an empty MISSING list); use before any claim about what a session was, and before grading a predecessor. Trigger: /session-identity, a compact, a wake, or any sentence of the form 'session X did/was …'."
version: "0.2 — 2026-09-07 20:2x CDT, Professional cc87418b; script sha256 in every page's measured_by"
status: "PROTOTYPE with selftest; the barrier WIRING (who runs --all at PreCompact/SessionEnd) is a separate Mechanism 1 review — nothing here fires on its own"
origin: "Jon 2026-09-05 20:4x (grades D/C/B/A/S for identity coverage) and 22:1x (raw logs of every JSON with his direct input as the floor); Antigravity's approved prototype barrier_session_identity.py (sha256 9d424c2e…) with Professional's two review conditions applied"
---

# /session-identity — who the sessions were, measured

## What it produces

- `wiki/sources/sessions/<born-date>-<sid8>.md` — one page per MAIN session under this trunk's project keys (both keys: `N--claude-professional`, `G--My-Drive-Claude-Claude-Professional-claude-professional`).
- `wiki/sources/sessions/subagents/<parent sid8>/agent-<id>.md` — one page per subagent JSONL, live and archived, deduplicated by parent + agent id (grade A).
- `wiki/sources/sessions/INDEX.md` — one row per session.

Every value is measured from the JSONL and the tree; **a field the parser could not read renders `UNKNOWN`, never 0**; a truncated file marks every count UNKNOWN. This rule exists because the first sweep (a Haiku lane, 2026-09-05 20:5x) wrote `tool_use: 0`, `models: [NONE]`, `Archived 0` on six pages for fields it never parsed.

## Fields, and what each one counts

| field | counts |
|---|---|
| `jon_turns` | `type:user` lines with `origin.kind == "human"` — the harness's own provenance mark. Where NO line in the file carries `origin` (older harness), the structural fallback (non-meta, non-tool-result, human text) is used and the value is LABELLED `(structural fallback)`. A `-p` lane's opening prompt is NOT Jon; the structural fallback cannot tell, which is why it is labelled. |
| `user_lines` / `tool_result_lines` / `meta_lines` | every `type:user` line; those carrying a `tool_result` block; those with `isMeta` |
| `queued_commands` | `type:attachment` / `queued_command` — messages typed while a turn ran |
| `tool_use` | `tool_use` blocks on assistant lines |
| `models` | distinct `message.model`, `<synthetic>` excluded |
| `compact_boundaries` | structural `subtype == compact_boundary`, never a prose grep |
| `subagents_live` / `subagents_archived` | `<key>/<sid>/subagents/agent-*.jsonl` / `raw/session-archive/<sid>/subagents/` |
| `archived`, `render`, `elder_note`, `log_mentions`, `commits` | archive dir with a non-empty jsonl; a render matched by the renderer's **6-char** prefix; `exchange/elders/NOTE-<sid8>.md`; `grep -c` in `wiki/log.md`; `git log --all --grep=<sid8>` |

## Commands

```
python scripts/session_identity.py --selftest                          # planted / truncated / no-origin / empty fixtures; rc 0 = PASS
python scripts/session_identity.py --all --trunk-root .                # every main session -> pages + INDEX
python scripts/session_identity.py --subagents --trunk-root .          # every subagent JSONL -> pages
python scripts/session_identity.py --coverage                          # GAP list; exit 3 if non-empty. --trunk-root defaults to CWD
python scripts/session_identity.py --coverage --live-sid <full uuid>   # override the seat identity (default: $CLAUDE_CODE_SESSION_ID)
python scripts/session_identity.py --jsonl <path> --trunk-root .       # one page to stdout
```

Commit message for a coverage change: `identity: <grade> <n> of <N>` (Jon's grades: D since PR-2 · C since PR-1 · B since the last all-trunk compact · A = plus every subagent log with metadata).

## Bounds, stated

- `jon_turns` by `origin.kind` undercounts where a typed slash-command wrapper carries no origin (this session: 9 by origin against ~11 typed); it never over-counts. The structural fallback over-counts `-p` prompts; it is labelled.
- Identity is not content: no page summarises what a session said. A reader who needs the words goes to the render named in `render`, or to `raw/session-archive/<sid>/`.
- Pages are regenerated in place by `--all`; hand-written sections do not survive. Put prose in the log or a reference page, not here.
- The 6-char render match can over-credit two sessions sharing a prefix (not observed).

## What can fail, and where it is checked

- `--selftest` fails if a planted count is wrong, if a truncated file yields any number instead of UNKNOWN, if a no-origin file is not labelled, or if an empty file yields anything but UNKNOWN. **Five coverage cases were added 09-07 where the fixtures had previously been built and never asserted:** C1 clean → PASS · C2 a non-live session with no page → GAP · C3 the live seat with 0 boundaries → LIVE, not a gap · **C4 the control that makes C3 failable — a live seat that HAS compacted and still has no page must be a GAP** · C5 the counter control — prose containing `compact_boundary` must not be counted. `[measured 2026-09-07 20:19]` deleting C3's `boundaries == 0` condition makes C4 fire and the selftest exit 1.
- `--coverage` exits 3 on the **GAP** list. `MISSING-LIVE` is printed and does not fail: the running seat's page cannot exist before its first barrier writes it, so the old undifferentiated MISSING made the check **structurally unable to pass from the moment a seat woke** — a standing alarm that is always true, which teaches successors to ignore it (`wikiskills-improve` §0, and the same shape as `readiness.sh` greening over a missing class). The exemption is one session wide and dies the moment that session compacts.
- ⛔ **Bare `--coverage` crashed with `TypeError: unsupported operand type(s) for /: 'NoneType' and 'str'` until 09-07** — `--trunk-root` had no default while the fleet skill's §3 and this trunk's WAKE both told successors to run it bare. A command published in three places and runnable in none.
- The barrier wiring (not in this skill): whoever runs `--all` at PreCompact/SessionEnd must have its hook line reviewed on hash by a sibling before it fires (Mechanism 1). Antigravity's daemon is the proposed owner (BP-6); until Jon rules on `wiki/sources/sessions/` ownership, it delivers to `exchange/inbound/IDENTITY-*.md` and the seat runs `--all`.
