#!/usr/bin/env python3
"""Record that a subagent return EXISTS, outside the parent's context, at the moment it completes.

WHY THIS EXISTS
---------------
On 2026-08-03 an unrouted consult held twelve of Jon's rulings, none of which reached the main
thread as principal input. The record was never missing — the JSONL was on disk the whole time.
**What was missing was any trace, outside the parent's own context, that the return had happened.**
When the parent's context ends, so does the only place the return was known.

So this writes one append-only row per completed return. It does NOT claim the return was read;
`disposition: PENDING` is the honest default, and a `NOT-CONSIDERED:<reason>` row is a legitimate
outcome. **The unrecorded skip is the defect, not the skip.**

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
* **It never blocks.** Exit 0 on every path, including its own internal errors. A capture-and-ledger
  control that can halt a session would be traded away the first time it misfired — and this repo
  has measured a 15-24% false-positive rate on a different Jon-detector, plus two blocking rows
  (`RATIO_FLOOR`, `capture.extract.stale.quiescent`) whose steady state is "firing" and which are
  therefore ignored. Enforcement belongs at SU-close, where a human is already reading.
* **It does not extract.** Re-extraction is slow on a Drive-mounted repo (minutes), and a hook that
  costs minutes will be removed. The extractor's own `--update` is idempotent and runs at SU-close.
* **It never edits a prior row.** Corrections are new rows. An append-only ledger cannot be
  retroactively made to look clean.

SELF-REFERENCE WARNING, LEARNED THE HARD WAY
--------------------------------------------
This ledger names every return's id. `wake_map.py`'s routing detector asks "does a durable artifact
name this return?" — so the ledger satisfies that test for every row at once. Within minutes of the
ledger's first draft the wake map flipped from "28 of 30 unrouted" to "All 19 routed" with nothing
considered by anyone. `wake_map.py` now excludes `ROUTING-LEDGER*` by name. **If this file is ever
renamed, that exclusion must move with it or the detector goes permanently green.**

RP-29 FIX, 2026-09-02 — THE PENDING/TERMINAL GATE ABOVE IS NOT ENOUGH ON ITS OWN
--------------------------------------------------------------------------------
Measured 2026-09-01 (`wiki/intake-triage/DREAM-2026-09-01-explicit-cycle-post-reboot-six-sweeps-
and-the-queued-command-class.md`, section 3): a mirror lane hit 100 tool uses and a sweep lane hit
40, two final reports swallowed by loop text, because **every lane's terminal reply re-fired
`SubagentStop` -> a new PENDING row for the lane itself -> the lane replied to route it -> re-fire.**

Root cause, found by reading the emitted message rather than assuming the TERMINAL gate (2026-08-06)
still covers it: `append_row`'s success message says *"Route it — name its transcript... or append
a NOT-CONSIDERED row"* and **never once tells the agent to write `[TERMINAL]`.** An agent that
complies literally — edits its own row's disposition from `PENDING` to `ROUTED` — satisfies the
instruction and clears the PENDING-row gate without ever tripping the TERMINAL gate. The very next
`SubagentStop` fire (of the ~11 known per agent) finds no PENDING row and no TERMINAL declaration,
so it mints a fresh PENDING row, which speaks the same message, which the agent complies with again.
**The row's own emission is what counts as the next return.** This is the SAME defect class as the
a1f02e loop the TERMINAL gate was built for, except the trigger this time is "an agent follows the
instruction it was given," not "an agent guesses wrong" — so the fix cannot depend on the agent
remembering to add a token nobody asked it to add.

So: an append-only idempotency sidecar, `exchange/su-close/ROUTED-KEYS.jsonl`, keyed on
`(agent id, artifact/transcript path, parent session)`. The FIRST fire for a given key mints the row
(as before) and records the key. **Every subsequent fire for that exact key is suppressed — silently,
before the ledger is even read — regardless of what happens to the row's disposition afterward.**
Unlike the PENDING/TERMINAL gates (which key off the ledger's own mutable state and can therefore be
cleared by the very act of routing), the sidecar key is never mutated once written: dedup no longer
depends on an agent declaring terminality, only on identity repeating. The accepted tradeoff is the
same one the TERMINAL gate already accepted and documented: a genuine `SendMessage` resumption of
the *same* agent id, transcript, and parent session reads as a repeat and is not re-logged. That is
judged better than the measured alternative — a 100-tool-use loop that swallows real final reports.

`stop_hook_active: true` (the harness's own "you are being invoked again after a stop hook already
ran" signal) is honored the same way: skip entirely, no row, no message. It is a second, independent
handle on the identical class of re-fire.
--------------------------------------------------------------------------------

Usage:
  route_agent_return.py                 # hook mode: payload on stdin
  route_agent_return.py --self-test     # negative controls
"""
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

LEDGER = os.path.join("exchange", "ROUTING-LEDGER.md")
MARKER = "# Rows — appended by route_agent_return.py"

# --- IDEMPOTENCY SIDECAR (RP-29, 2026-09-02) ---------------------------------------------------
# Append-only, never rewritten (same discipline as LEDGER). One JSON line per (agent id,
# transcript/artifact path, parent session) key that has EVER minted a row. Presence alone
# suppresses further minting for that key — it does not matter what happened to the ledger row
# afterward. See the RP-29 docstring block above for why the ledger-state-based gates cannot do
# this on their own.
ROUTED_KEYS_SIDECAR = os.path.join("exchange", "su-close", "ROUTED-KEYS.jsonl")


def dedupe_key(aid, transcript, parent6):
    """sha256 of the three identity components that make a SubagentStop fire 'the same return'."""
    raw = f"{aid}\x1f{transcript}\x1f{parent6}"
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]


def sidecar_seen(root, key):
    """Has this key ever been recorded? Fail OPEN (treat as not-seen) on any read problem —
    the ledger's own PENDING/TERMINAL gates remain as a second layer, so failing open here risks
    at most a duplicate row, never a silently dropped genuine return."""
    path = os.path.join(root, ROUTED_KEYS_SIDECAR)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("key") == key:
                    return True
    except FileNotFoundError:
        return False
    except OSError:
        return False
    return False


def sidecar_append(root, key, meta):
    """Append one JSON line. Never rewrites an existing byte. Best-effort: a write failure here
    must not raise or block — the row it is protecting has already been written."""
    path = os.path.join(root, ROUTED_KEYS_SIDECAR)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        rec = dict(meta)
        rec["key"] = key
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        return True
    except OSError:
        return False

# --- TERMINALITY (added 2026-08-06, from a measured three-iteration loop) --------------------
# `[TERMINAL]` is the canonical machine field. It is a real field, not a mood: an agent that is
# standing down writes this exact token into its row's disposition or role cell, and this script
# then refuses to append any further row for that id6 — forever.
#
# WHY A TOKEN AND NOT A WORD. The prose rule said "marked terminal" and rows said `(terminal)`,
# but the same word also appears inside the long narrative parentheticals of rows that are NOT
# declarations. Grepping the whole line for "terminal" would fire on narration; that is the same
# defect class as the prose rule it replaces. `[TERMINAL]` cannot be written by accident.
TERMINAL_TOKEN = "[TERMINAL]"

# LEGACY SHIM, deliberately narrow. Rows written before the token existed declare terminality as
# `**ROUTED (terminal)**` in the disposition HEAD or `— **TERMINAL, no further <id> rows**` in the
# role cell. Those rows are evidence and are never rewritten (NO DESTRUCTIVE ACTS), so the
# predicate has to read them where they are. It is scoped to the disposition head — the text
# BEFORE the first `*(` narrative — and to the role cell, never the narrative body.
_TERMINAL_WORD = re.compile(r"(?<![A-Za-z])terminal(?![A-Za-z])", re.IGNORECASE)


def repo_root():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def read_payload(stream):
    """Parse the hook payload. A malformed payload is UNKNOWN, never an assumed-empty return."""
    try:
        raw = stream.read()
    except Exception:
        return None, "stdin unreadable"
    if not raw or not raw.strip():
        return None, "empty payload"
    try:
        return json.loads(raw), ""
    except Exception as e:
        return None, f"payload not JSON: {e.__class__.__name__}"


def extract_fields(payload):
    """Pull id and transcript from whatever shape the payload arrives in.

    Field names are NOT guessed silently: every key actually looked at is listed here, and anything
    not found is reported as UNKNOWN rather than defaulted. A field-name mismatch once produced a
    29-session 'permanently lost' registry in this program; the fix is to say which key was missing.
    """
    got = {}
    for key in ("agent_id", "agentId", "subagent_id", "session_id", "sessionId"):
        if isinstance(payload.get(key), str) and payload[key]:
            got.setdefault("id", payload[key])
    for key in ("transcript_path", "transcriptPath", "jsonl_path"):
        if isinstance(payload.get(key), str) and payload[key]:
            got.setdefault("transcript", payload[key])
    # `agent_name` added 2026-08-06: it is a documented SubagentStop event-specific input field
    # alongside `agent_type`, and omitting it would have rendered role UNKNOWN for any payload
    # that carries only the name.
    for key in ("agent_type", "agentType", "subagent_type", "agent_name", "role"):
        if isinstance(payload.get(key), str) and payload[key]:
            got.setdefault("role", payload[key])

    # --- SUBAGENT TRANSCRIPT RESOLUTION (added 2026-08-06, from a measured live defect) -------
    # SubagentStop's `transcript_path` is the MAIN CONVERSATION jsonl, not the subagent's own.
    # Observed within minutes of wiring the hook: every row recorded the same conversation file,
    # so the ledger keyed EVERY agent to one identical path. The drainer dedupes on transcript
    # path — which would have collapsed all agents into a single entry. That is worse than the
    # duplicate rows it was meant to prevent: it looks clean and loses the whole population.
    #
    # The real transcript is <conv-dir>/<conv-id>/subagents/agent-<full-id>.jsonl. Derive it, and
    # only use it if it exists on disk. Never fabricate a path that isn't there.
    aid = got.get("id")
    conv = got.get("transcript")
    if aid and conv and conv.endswith(".jsonl"):
        conv_dir = os.path.dirname(conv)
        conv_id = os.path.basename(conv)[:-len(".jsonl")]
        cand = os.path.join(conv_dir, conv_id, "subagents", f"agent-{aid}.jsonl")
        if os.path.isfile(cand):
            got["transcript"] = cand
            got["transcript_source"] = "derived-and-verified-on-disk"
        else:
            # Say what was tried. An unresolved path must never render as a confident one.
            got["transcript"] = f"{conv}  [MAIN-CONV — subagent transcript not found at {cand}]"
            got["transcript_source"] = "payload-fallback"
    return got


def row_for(fields, now_iso):
    """One ledger row. Missing values render as UNKNOWN — never as a plausible blank."""
    aid = fields.get("id") or "UNKNOWN"
    id6 = aid[:6] if aid != "UNKNOWN" else "UNKNOWN"
    transcript = fields.get("transcript") or "UNKNOWN — not in payload"
    role = fields.get("role") or "UNKNOWN"
    return (f"| {now_iso} | auto | {id6} | subagent | {role} | {transcript} | "
            f"PENDING | - |")


def row_cells(line):
    """Split a ledger row into its 8 declared cells, or None if the shape is not exactly 8.

    Verified 2026-08-06 against the live ledger: 141 of 141 table lines yield exactly 8 cells, so
    positional reads are safe on real data. A line that does not is NOT force-fitted — an
    off-by-one column read would silently point the terminality test at the wrong cell, and this
    program has already paid for one field-name mismatch.
    """
    s = line.strip()
    if not s.startswith("|") or not s.endswith("|"):
        return None
    cells = [c.strip() for c in s[1:-1].split("|")]
    return cells if len(cells) == 8 else None


def is_terminal_row(line, id6):
    """Does `line` declare id6 TERMINAL — no further rows are owed for this agent, ever?

    Columns: 0 closed_utc | 1 parent6 | 2 id6 | 3 kind | 4 role-slug | 5 extract |
             6 disposition | 7 routed_by
    """
    if not id6 or id6 == "UNKNOWN":
        return False
    cells = row_cells(line)
    if cells is None:
        # Unknown shape: trust ONLY the canonical token, and only alongside this id on the line.
        return TERMINAL_TOKEN in line and f"| {id6} |" in line
    if cells[2] != id6:
        return False
    role, disposition = cells[4], cells[6]
    if TERMINAL_TOKEN in role or TERMINAL_TOKEN in disposition:
        return True
    # Legacy: the declaration lives in the disposition HEAD or the role cell, never the narrative.
    head = disposition.split("*(")[0]
    return bool(_TERMINAL_WORD.search(head) or _TERMINAL_WORD.search(role))


def append_row(root, row, id6=None):
    """Append-only. Creates the section if absent; never rewrites an existing byte.

    DEDUPE (added 2026-08-06, from a measured live defect): SubagentStop fired ELEVEN times for a
    single agent within minutes of the hook going live — it is not a once-per-agent event. Eleven
    rows for one return is not a record, it is noise that buries the ten real returns around it.

    So: if a PENDING row for this id6 already exists, do not append a second. This is the only
    place in the script that reads the ledger to decide anything, and it still never rewrites a
    byte — the append-only guarantee holds. A row already dispositioned (not PENDING) does NOT
    suppress a new one: that would silently drop a genuine second run of the same agent.

    TERMINAL GATE (added 2026-08-06, and it is the fix for a THREE-ITERATION LOOP that ran the
    same day the stopping rule was written as prose)
    ------------------------------------------------------------------------------------------
    **The PENDING gate above cannot catch self-routing, structurally.** Routing a row means
    overwriting its disposition cell from PENDING to ROUTED — so the act of routing DESTROYS the
    very state the gate keys on. The next SubagentStop finds no PENDING row and appends a fresh
    one, which is a new routing obligation, which is another turn, which fires SubagentStop again.
    Measured on agent `a1f02e` at ~22:41-22:45 UTC: commits `6099c45` -> `1c84be2` -> `ac3e88f`,
    **each row marked terminal, each one triggering the next**, plus a fourth PENDING row after
    the last. One commit of real work, three of ceremony, ~153k tokens.

    So terminality — which PERSISTS, unlike PENDING — becomes the gate. Once any row for an id6
    declares `[TERMINAL]`, every further row for that id6 is suppressed. This makes the ledger's
    prose stopping rule mechanical: it now *does* what it said agents *should* do.

    WHAT THIS KNOWINGLY SUPPRESSES, stated rather than hidden behind a heuristic
    ---------------------------------------------------------------------------
    A SubagentStop can only repeat for one id6 if the SAME agent instance runs again — a fresh
    dispatch gets a fresh id. The one legitimate way that happens is a `SendMessage` resumption
    carrying genuinely new work. **If that agent had already declared itself TERMINAL, its new
    return will not be recorded here.** There is no signal in the hook payload that distinguishes
    "resumed with new work" from "routing my own row"; both are just another turn on the same
    transcript. Rather than guess, terminality wins — the agent said it was standing down, and an
    honest missed row for an agent that declared itself done beats an unbounded loop. **The fix
    if it ever bites: do not declare TERMINAL on an agent you intend to message again.**
    """
    path = os.path.join(root, LEDGER)
    try:
        existing = ""
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                existing = fh.read()
        if id6 and id6 != "UNKNOWN":
            for line in existing.splitlines():
                if is_terminal_row(line, id6):
                    return True, (f"duplicate-suppressed (TERMINAL row for {id6} exists; the "
                                  f"self-routing stopping rule is enforced here, not just "
                                  f"documented)")
            for line in existing.splitlines():
                if f"| {id6} |" in line and "| PENDING |" in line:
                    return True, f"duplicate-suppressed (PENDING row for {id6} exists)"
        block = ""
        if MARKER not in existing:
            block += (f"\n\n{MARKER}\n\n"
                      "*Written at completion, outside the parent's context. `PENDING` is honest: "
                      "it records that a return happened, not that anyone read it.*\n\n"
                      "| closed_utc | parent6 | id6 | kind | role-slug | extract | disposition | routed_by |\n"
                      "|---|---|---|---|---|---|---|---|\n")
        block += row + "\n"
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(block)
        return True, ""
    except OSError as e:
        return False, f"{e.__class__.__name__}"


def main():
    if "--self-test" in sys.argv:
        return self_test()

    payload, why = read_payload(sys.stdin)
    root = repo_root()

    # `hookEventName` is REQUIRED inside hookSpecificOutput. Verified 2026-08-06 against
    # https://code.claude.com/docs/en/hooks: SubagentStop's hookSpecificOutput is
    # {hookEventName: "SubagentStop", additionalContext}. This script emitted additionalContext
    # with no hookEventName, which is the shape most likely to be dropped on the floor — and it
    # would have been dropped silently, in a hook that has never once fired. Default to
    # SubagentStop (the event this is staged for) but echo back whatever event actually invoked
    # us, so the same script is correct if it is ever wired to Stop or TaskCompleted.
    event = "SubagentStop"
    if isinstance(payload, dict) and isinstance(payload.get("hook_event_name"), str):
        event = payload["hook_event_name"] or event

    if payload is None:
        # NEVER block, and never pretend a return was recorded when it was not.
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext":
              f"[routing-ledger] NOT RECORDED — {why}. This return exists only in your context; "
              f"name its transcript in a durable artifact or it is invisible after this turn."}}))
        return 0

    # --- RP-29: `stop_hook_active` is the harness's own signal that this delivery is a re-fire
    # of a stop hook, not a fresh stop. Honor it exactly like a suppressed duplicate: no row, no
    # message. See the RP-29 docstring block at the top of this file.
    if payload.get("stop_hook_active") is True:
        return 0

    fields = extract_fields(payload)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _aid = fields.get("id") or "UNKNOWN"
    _id6 = _aid[:6] if _aid != "UNKNOWN" else "UNKNOWN"

    # --- RP-29 IDEMPOTENCY KEY, CHECKED BEFORE THE LEDGER-STATE GATES -----------------------
    # (agent id, transcript/artifact path, parent session). Parent session is the payload's own
    # `session_id` — for SubagentStop this is documented as the invoking (parent) session, and
    # even in the ambiguous case where no separate agent id is present in the payload and `_aid`
    # falls back to `session_id` itself, the key stays internally consistent (aid == parent6) and
    # still dedupes correctly across repeated fires of the SAME stop.
    _parent_sid = payload.get("session_id")
    _parent6 = _parent_sid[:6] if isinstance(_parent_sid, str) and _parent_sid else "UNKNOWN"
    _transcript = fields.get("transcript") or "UNKNOWN"
    _key = dedupe_key(_aid, _transcript, _parent6) if _aid != "UNKNOWN" else None

    if _key and sidecar_seen(root, _key):
        # Silent, before the ledger is even touched. This is the fire that RP-29 measured: the
        # agent's own routing edit cleared the PENDING/TERMINAL ledger gates, and without this
        # key check a fresh PENDING row would be minted here, re-injecting the "route it" message
        # and continuing the loop.
        return 0

    ok, err = append_row(root, row_for(fields, now_iso), id6=_id6)

    if ok and _key and not err.startswith("duplicate-suppressed"):
        # A row actually landed for this key — record it so no future fire for this exact
        # (agent id, transcript, parent session) can mint again, no matter what happens to this
        # row's disposition afterward.
        sidecar_append(root, _key, {"id6": _id6, "aid": _aid, "transcript": _transcript,
                                    "parent6": _parent6, "written_utc": now_iso})

    if ok and err.startswith("duplicate-suppressed"):
        # Do NOT say "logged" when nothing was written. A success message that overstates what
        # happened is the same defect the ledger exists to catch, committed by the ledger's own
        # writer. Found 2026-08-06 by checking the row count instead of believing the message.
        msg = (f"[routing-ledger] not appended — {err}. The earlier PENDING row still stands and "
               f"is the one to route. SubagentStop fires repeatedly for a single agent; this is "
               f"expected, not an error.")
    elif ok:
        msg = ("[routing-ledger] return logged as PENDING in exchange/ROUTING-LEDGER.md. "
               "Route it — name its transcript in a durable artifact — or append a "
               "NOT-CONSIDERED row with a reason. A recorded skip is fine; an unrecorded one is "
               "the defect.")
    else:
        msg = (f"[routing-ledger] WRITE FAILED ({err}). The return is NOT recorded anywhere outside "
               f"this context. Treat that as the finding.")
    # --- SILENCE ON NO-OP (added 2026-08-06, from a measured self-inflicted regression) --------
    # SubagentStop fires ~11 times for ONE agent. Every fire that emits `additionalContext` injects
    # that text back into the ending agent's own context. Wiring this hook at 12:44 was immediately
    # followed by FOUR agents returning content-free summaries — "[Session complete]", "Terminal.
    # Done.", "Standing down.", and one that said outright: "No further response to identical
    # repeated hook notifications." Their WORK landed; their REPORTS did not.
    #
    # The instrument built to stop returns being lost was itself destroying returns. Speak once —
    # on the fire that actually wrote a row, or on failure. A suppressed duplicate says nothing.
    if err.startswith("duplicate-suppressed"):
        return 0
    # Second silent class, found 2026-08-07 by piping `{}` into this script and watching it both
    # append a row AND speak. When the payload carries no resolvable agent id, the row is still
    # written — the ledger is append-only and a return that happened must leave a trace — but the
    # MESSAGE is suppressed. "Route it, name its transcript" is un-actionable when there is no
    # agent to name, and every emitted additionalContext is injected back into the ending agent's
    # own context. Six such rows already exist in the ledger; each one spoke.
    if _aid == "UNKNOWN":
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                                            "additionalContext": msg}}))
    return 0


def self_test():
    cases = []
    import io

    # REGRESSION GUARD, 2026-08-07. `CARRIER.md` asserted "both hooks are now silent on no-op"
    # and that assertion was FALSE when measured: `echo {} | route_agent_return.py` printed 323
    # bytes of additionalContext. A property recorded in prose and never checked is this repo's
    # characteristic defect; so the property is checked here, where it can fail loudly.
    import contextlib as _ctx
    _buf = io.StringIO()
    _argv, sys.argv = sys.argv, ["route_agent_return.py"]
    _stdin, sys.stdin = sys.stdin, io.StringIO("{}")
    try:
        with _ctx.redirect_stdout(_buf):
            main()
    finally:
        sys.argv, sys.stdin = _argv, _stdin
    cases.append(("NO-OP SILENCE: unresolvable payload emits ZERO bytes of additionalContext",
                  _buf.getvalue().strip() == ""))

    # A malformed payload must not crash and must not fabricate a row.
    p, why = read_payload(io.StringIO("not json"))
    cases.append(("malformed payload -> None + reason", p is None and "not JSON" in why))
    p, why = read_payload(io.StringIO(""))
    cases.append(("empty payload -> None + reason", p is None and why == "empty payload"))

    # Missing fields render UNKNOWN, never a plausible blank.
    r = row_for({}, "T")
    cases.append(("absent fields render UNKNOWN, not blank",
                  r.count("UNKNOWN") >= 3 and "|  |" not in r))

    # Present fields are used, and the id is truncated to 6 for the id6 column.
    r = row_for({"id": "abfa7ecf4b17604ae", "transcript": "/x/y.jsonl", "role": "fable-mirror"}, "T")
    cases.append(("present fields used; id6 truncated",
                  "abfa7e" in r and "/x/y.jsonl" in r and "fable-mirror" in r))

    # NEGATIVE CONTROL: the default disposition must be PENDING, never ROUTED.
    cases.append(("NEGATIVE CONTROL: default disposition is PENDING, never ROUTED",
                  "PENDING" in r and "ROUTED" not in r))

    # --- TERMINAL GATE -------------------------------------------------------------------
    import shutil
    import tempfile

    def try_append(lines, id6):
        """Append one row for id6 against a ledger made of `lines`. Returns (appended?, why)."""
        tmp = tempfile.mkdtemp(prefix="rar-")
        try:
            os.makedirs(os.path.join(tmp, "exchange"), exist_ok=True)
            with open(os.path.join(tmp, LEDGER), "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + "\n")
            ok, why = append_row(tmp, row_for({"id": id6 + "0000"}, "T"), id6=id6)
            return (ok and not why.startswith("duplicate-suppressed")), why
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def frow(id6, role, disp):
        return f"| T | auto | {id6} | subagent | {role} | x.jsonl | {disp} | - |"

    # The exact disposition-head shapes the real loop used, so the test is machine-independent.
    legacy_term = frow("aaa111", "skills-executor", "**ROUTED (terminal)**")
    legacy_term2 = frow("aaa111", "skills-executor, return 2",
                        "**ROUTED (terminal) — marked per the self-routing rule**")
    plain_routed = frow("bbb222", "wiki-executor",
                        "**ROUTED** *(landed as commit deadbee; nothing terminal about it)*")
    token_row = frow("ccc333", "general-purpose", f"**ROUTED** {TERMINAL_TOKEN}")
    pending_row = frow("ddd444", "extractor", "PENDING")

    appended, _ = try_append([legacy_term], "aaa111")
    cases.append(("legacy `(terminal)` head suppresses a further row", not appended))
    appended, _ = try_append([legacy_term, legacy_term2], "aaa111")
    cases.append(("still suppressed after a second terminal row", not appended))
    appended, _ = try_append([token_row], "ccc333")
    cases.append(("canonical [TERMINAL] token suppresses", not appended))
    appended, _ = try_append([pending_row], "ddd444")
    cases.append(("pre-existing PENDING gate still suppresses (unchanged)", not appended))

    # NEGATIVE CONTROLS: a suppressor that suppresses everything is not a fix.
    appended, _ = try_append([legacy_term, plain_routed, token_row], "eee555")
    cases.append(("NEGATIVE CONTROL: fresh id6 still appends", appended))
    appended, _ = try_append([plain_routed], "bbb222")
    cases.append(("NEGATIVE CONTROL: non-terminal ROUTED does NOT suppress (genuine 2nd run)",
                  appended))
    appended, _ = try_append([legacy_term], "aaa112")
    cases.append(("NEGATIVE CONTROL: terminal row for a NEIGHBOURING id6 does not suppress",
                  appended))
    cases.append(("NEGATIVE CONTROL: 'terminal' inside narrative prose is NOT a declaration",
                  not is_terminal_row(
                      frow("fff666", "security-builder",
                           "**ROUTED** *(the reason this row is marked terminal: routing a "
                           "return IS a return, and the chain terminates only by declaration)*"),
                      "fff666")))
    cases.append(("UNKNOWN id6 is never treated as terminal",
                  not is_terminal_row(frow("UNKNOWN", "x", "**ROUTED (terminal)**"), "UNKNOWN")))

    # --- RP-29: IDEMPOTENCY SIDECAR + stop_hook_active, run against a real scratch repo -------
    # This is the exact loop DREAM-2026-09-01 measured: the SAME agent's SubagentStop fires
    # repeatedly, and between fires the agent's OWN edit clears the PENDING gate (self-routing to
    # ROUTED, no [TERMINAL]). Without the sidecar, fire 2 would mint a fresh PENDING row.
    def scratch_repo():
        tmp = tempfile.mkdtemp(prefix="rar-rp29-")
        os.makedirs(os.path.join(tmp, "exchange", "su-close"), exist_ok=True)
        return tmp

    def fire(root, payload):
        """One hook_mode invocation of THIS module's main() against `root`, via env override."""
        buf = io.StringIO()
        _stdin, sys.stdin = sys.stdin, io.StringIO(json.dumps(payload))
        _argv, sys.argv = sys.argv, ["route_agent_return.py"]
        _env = os.environ.get("CLAUDE_PROJECT_DIR")
        os.environ["CLAUDE_PROJECT_DIR"] = root
        try:
            with _ctx.redirect_stdout(buf):
                main()
        finally:
            sys.stdin = _stdin
            sys.argv = _argv
            if _env is None:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)
            else:
                os.environ["CLAUDE_PROJECT_DIR"] = _env
        return buf.getvalue()

    def pending_count(root, id6):
        p = os.path.join(root, LEDGER)
        if not os.path.exists(p):
            return 0
        with open(p, encoding="utf-8", errors="replace") as fh:
            return sum(1 for l in fh if f"| {id6} |" in l)

    def any_row_count(root, id6):
        p = os.path.join(root, LEDGER)
        if not os.path.exists(p):
            return 0
        with open(p, encoding="utf-8", errors="replace") as fh:
            return sum(1 for l in fh if (row_cells(l) or ["", "", ""])[2] == id6)

    root = scratch_repo()
    try:
        payload = {"session_id": "rp29aaa1112223334445556667778889990",
                   "transcript_path": os.path.join(root, "main.jsonl"),
                   "hook_event_name": "SubagentStop", "stop_hook_active": False}
        fire(root, payload)                       # fire 1: real return, mints PENDING
        n1 = any_row_count(root, "rp29aa")
        # Simulate the agent self-routing its own row WITHOUT [TERMINAL] — the exact gap RP-29
        # found: the emitted message never told it to write the token.
        p = os.path.join(root, LEDGER)
        with open(p, encoding="utf-8") as fh:
            body = fh.read()
        body = body.replace("| PENDING | - |", "| **ROUTED** *(self-routed, no token)* | rp29aa |")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(body)
        fire(root, payload)                       # fire 2: same identity, re-fire
        n2 = any_row_count(root, "rp29aa")
        cases.append(("RP-29: same (agent,transcript,parent) fired twice -> exactly 1 row total",
                      n1 == 1 and n2 == 1))

        # A genuinely new agent (different session/parent) still gets its own row.
        payload_new = dict(payload, session_id="rp29bbb2223334445556667778889990001")
        fire(root, payload_new)
        cases.append(("RP-29: genuinely new agent still appends 1 row",
                      any_row_count(root, "rp29bb") == 1))

        # An agent whose key is already routed (present in the sidecar) -> 0 new rows even
        # though the ledger row now shows ROUTED, not PENDING (the case the old gate missed).
        before = any_row_count(root, "rp29aa")
        fire(root, payload)
        cases.append(("RP-29: already-routed key -> 0 new rows on a third fire",
                      any_row_count(root, "rp29aa") == before))

        # stop_hook_active True is honored as already-handled: no row at all for a fresh id.
        root2 = scratch_repo()
        try:
            payload_sha = {"session_id": "rp29ccc3334445556667778889990001112",
                           "transcript_path": os.path.join(root2, "main.jsonl"),
                           "hook_event_name": "SubagentStop", "stop_hook_active": True}
            out = fire(root2, payload_sha)
            cases.append(("RP-29: stop_hook_active=true -> zero rows, zero bytes emitted",
                          any_row_count(root2, "rp29cc") == 0 and out.strip() == ""))
        finally:
            shutil.rmtree(root2, ignore_errors=True)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # --- LIVE REPLAY against the real a1f02e loop, if the real ledger is present -----------
    real = os.path.join(repo_root(), LEDGER)
    if os.path.exists(real):
        with open(real, encoding="utf-8", errors="replace") as fh:
            all_lines = fh.read().splitlines()
        idx = [i for i, l in enumerate(all_lines)
               if (row_cells(l) or ["", "", ""])[2] == "a1f02e"]
        if idx:
            # Before the first a1f02e row ever existed, the hook MUST record the return.
            appended, _ = try_append(all_lines[:idx[0]], "a1f02e")
            cases.append(("REPLAY: first a1f02e fire appends (row 1 is real work)", appended))
            for n, i in enumerate(idx, start=1):
                appended, why = try_append(all_lines[:i + 1], "a1f02e")
                cases.append((f"REPLAY: fire after real a1f02e row {n} suppressed", not appended))
        else:
            cases.append(("REPLAY: a1f02e rows present in live ledger", False))
        terminal_ids = sorted({(row_cells(l) or ["", "", ""])[2] for l in all_lines
                               if row_cells(l) and is_terminal_row(l, (row_cells(l))[2])})
        row_ids = [(row_cells(l))[2] for l in all_lines
                   if row_cells(l) and re.fullmatch(r"[0-9a-f]{6}", (row_cells(l))[2] or "")]
        print(f"live ledger: {len(row_ids)} agent rows, {len(set(row_ids))} distinct ids, "
              f"{len(terminal_ids)} classified TERMINAL -> {', '.join(terminal_ids)}")
        cases.append(("live ledger: terminal ids are a MINORITY, not everything",
                      0 < len(terminal_ids) < len(set(row_ids))))

    print("=== SELF-TEST (negative control) ===")
    bad = 0
    for name, ok in cases:
        bad += 0 if ok else 1
        print(f"  {name:<58} : {'PASS' if ok else 'FAIL'}")
    print(f"\nRESULT: {'PASS' if not bad else 'FAIL'} — {len(cases)-bad}/{len(cases)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
