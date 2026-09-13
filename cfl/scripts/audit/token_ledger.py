#!/usr/bin/env python3
"""
token_ledger.py — derive a token/cost ledger from Claude Code session JSONLs.

WHY THIS EXISTS
    Spend has been a *felt* number ("we've used 40% of the budget"). The raw data
    was already on disk: every Claude Code JSONL carries per-message `usage`.
    This turns that into a derived, checkable ledger.

TWO CORRECTNESS PROPERTIES THAT ARE NOT OPTIONAL
    1. SUBAGENTS ARE ~90% OF THE RECORD. Session JSONLs live at
       <projects>/<slug>/<uuid>.jsonl, but subagent transcripts live one level
       deeper at <projects>/<slug>/<uuid>/subagents/agent-*.jsonl. Measured
       2026-08-03: 541 files total = 50 top-level + 491 subagent (90.8%).
       A top-level-only glob measures ~9% of spend and reports success.

    2. ASSISTANT RECORDS ARE STREAMING SNAPSHOTS, NOT DISTINCT MESSAGES.
       Several records share one `message.id`, each carrying a `usage` object.
       Summing them naively inflates output tokens ~9.4x (measured: 173,335 vs
       18,501 in a single file). Within a message.id group, input/cache fields
       are CONSTANT and output_tokens grows MONOTONICALLY, so the correct
       reduction is max-per-field-per-message.id. Taking the *first* record
       instead undercounts (it catches output_tokens mid-stream, e.g. 2 of 304).
       Verified 0 violations of both invariants across sampled files.

    Parent session files contain zero sidechain records (isSidechain never true),
    so parent and subagent files partition cleanly with no cross-file overlap.
    Cross-file duplicate message.ids are still deduped globally and counted --
    session resume can copy history forward.

THE `origin` FIELD DOES NOT ATTRIBUTE SPEND -- MEASURED, NOT ASSUMED
    It was proposed that `origin.kind` could attribute usage (coordinator-driven
    vs human-driven). Measured 2026-08-03 across ALL of ~/.claude/projects:

        102,324 records | 1,357 carry `origin` | ALL of them type == "user"
        45,557 assistant records carry `usage` | 0 of them carry `origin`

    The two fields are disjoint by construction: `origin` marks who initiated a
    TURN, `usage` records what an ASSISTANT reply consumed. Reading `origin` off
    a usage record yields nothing, every time. (Within this project the kinds are
    human 470 / task-notification 199 / coordinator 18 -- the field is real and
    correctly populated. It simply lives on the wrong record type for costing.)

    So `--by origin` attributes POSITIONALLY: each assistant message inherits the
    most recent preceding origin.kind in its own file. That is a real signal but
    a DERIVED one, and it is labelled as such wherever it is printed. Records
    before the first origin-bearing user turn are "unattributed" and reported
    separately rather than being silently folded into "human".

RECONCILED AGAINST GROUND TRUTH (the control that lets this instrument fail)
    Claude Code's own `/usage` panel reported a per-model cost breakdown for
    session 9e21da9b on 2026-08-03. Recomputing that session from the JSONLs,
    truncated at the panel's read time, gives $97.45 against the panel's $98.93
    -- 1.5% under, with fable cache-writes matching to the token (516,134 vs a
    displayed "516.1k"). Re-run it any time with --reconcile-panel. A dedup bug
    would show here as a ~9x output overshoot; a rate-table error as a skewed
    per-model split. See RECONCILIATION below for the stored expectation.

DOLLARS
    See RATES below. Rates are Anthropic first-party API list prices, sourced
    from the bundled `claude-api` skill's model table (cached 2026-06-24), not
    invented here. They are a NOTIONAL API-EQUIVALENT cost. Jon is on a Max
    subscription -- a flat monthly fee -- so these dollars are NOT money spent.
    See the caveats printed with every cost report.

THE WEEKLY CEILING (the denominator) IS NOT KNOWN
    No absolute weekly allowance is written down anywhere in this repo. Every
    budget statement on record is a PERCENTAGE read off Claude Code's `/usage`
    meter, which only Jon can see ("40% of the budget", "most of the week's
    budget"). So the denominator has never been recorded -- but it IS derivable:

        ceiling ~= (tokens consumed this week) / (meter percentage / 100)

    `--ceiling-from-meter PCT` does that arithmetic. Two constraints make the
    result provisional rather than authoritative:

      (a) THE METER'S UNIT IS UNKNOWN. Nothing establishes whether `/usage`
          tracks total tokens, output tokens, non-cache tokens, or a cost-
          weighted blend. So the implied ceiling is emitted on EVERY plausible
          basis instead of silently picking one. Which row is right cannot be
          settled from this repo.
      (b) ONE READING IS ONE EQUATION. A single observation cannot be checked.
          `--record-meter` persists (timestamp, pct, token totals); once two
          readings exist the tool cross-checks them and reports disagreement
          rather than averaging it away.

    This script CANNOT read the meter. `/usage` is a CLI slash command, not an
    agent-callable tool -- the percentage is an input Jon supplies.

Usage:
    python token_ledger.py [--since YYYY-MM-DD]
                           [--by day|session|agent|model|origin]
                           [--json] [--write] [--self-test] [--reconcile-panel]
                           [--ceiling-from-meter PCT [--record-meter]
                            [--meter-grade panel|recall]]
                           [--reset-at ISO8601 | --week-start YYYY-MM-DD]

Exit codes:
    0  ok
    1  bad arguments, or self-test failure
    2  zero files scanned -- the ledger measured nothing. Never a silent pass.
    3  --reconcile-panel disagreed with Claude Code's own displayed figure
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import tempfile
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Rate table.
#
# SOURCE: bundled `claude-api` skill, "Current Models" table, cached 2026-06-24.
# These are Anthropic first-party API list prices in USD per 1M tokens.
# Do not edit these by guesswork -- re-derive them from the skill's model table
# or platform.claude.com/docs/en/about-claude/models/overview.md and update
# RATES_SOURCE below when you do.
# ---------------------------------------------------------------------------
RATES_SOURCE = "claude-api skill model table, cached 2026-06-24 (Anthropic 1P API list prices)"

RATES = {  # model_id -> (input $/MTok, output $/MTok)
    "claude-fable-5":   (10.0, 50.0),
    "claude-mythos-5":  (10.0, 50.0),
    "claude-opus-5":    (5.0,  25.0),
    "claude-opus-4-8":  (5.0,  25.0),
    "claude-opus-4-7":  (5.0,  25.0),
    "claude-opus-4-6":  (5.0,  25.0),
    "claude-opus-4-5":  (5.0,  25.0),
    "claude-sonnet-5":  (3.0,  15.0),   # intro $2/$10 through 2026-08-31; standard used here
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-haiku-4-5": (1.0,  5.0),
}

# Cache multipliers, applied to the model's INPUT rate.
# SOURCE: claude-api skill, shared/prompt-caching.md ("Economics").
CACHE_READ_MULT = 0.10   # cache reads cost ~0.1x base input
CACHE_WRITE_5M_MULT = 1.25   # 5-minute TTL write premium
CACHE_WRITE_1H_MULT = 2.00   # 1-hour TTL write premium

# Models that carry no API cost (local/synthetic messages).
NON_BILLED_MODELS = {"<synthetic>"}


def normalize_model(model: str) -> str:
    """Strip a date suffix so 'claude-haiku-4-5-20251001' matches 'claude-haiku-4-5'."""
    if model in RATES or model in NON_BILLED_MODELS:
        return model
    parts = model.split("-")
    if len(parts) > 1 and parts[-1].isdigit() and len(parts[-1]) == 8:
        candidate = "-".join(parts[:-1])
        if candidate in RATES:
            return candidate
    return model


class Rec:
    """One deduplicated assistant message's usage."""
    __slots__ = ("date", "ts", "session", "agent", "model", "origin",
                 "inp", "out", "cread", "cwrite5m", "cwrite1h")

    def __init__(self, date, session, agent, model, ts="", origin="unattributed"):
        self.date = date
        self.ts = ts            # full ISO timestamp; the week window needs sub-day resolution
        self.session = session
        self.agent = agent
        self.model = model
        self.origin = origin    # DERIVED BY POSITION, not read from this record. See ORIGIN note.
        self.inp = 0
        self.out = 0
        self.cread = 0
        self.cwrite5m = 0
        self.cwrite1h = 0

    def absorb(self, u: dict) -> None:
        """Max-reduce a streaming snapshot into this record. See module docstring."""
        self.inp = max(self.inp, u.get("input_tokens") or 0)
        self.out = max(self.out, u.get("output_tokens") or 0)
        self.cread = max(self.cread, u.get("cache_read_input_tokens") or 0)
        cc = u.get("cache_creation")
        if isinstance(cc, dict):
            self.cwrite5m = max(self.cwrite5m, cc.get("ephemeral_5m_input_tokens") or 0)
            self.cwrite1h = max(self.cwrite1h, cc.get("ephemeral_1h_input_tokens") or 0)
        else:
            # Older records may only carry the flat total; treat it as 5m.
            self.cwrite5m = max(self.cwrite5m, u.get("cache_creation_input_tokens") or 0)

    @property
    def cwrite(self) -> int:
        return self.cwrite5m + self.cwrite1h

    def cost(self) -> float | None:
        """Notional API-equivalent USD, or None if the model has no known rate."""
        m = normalize_model(self.model)
        if m in NON_BILLED_MODELS:
            return 0.0
        if m not in RATES:
            return None
        rin, rout = RATES[m]
        return (
            self.inp * rin
            + self.out * rout
            + self.cread * rin * CACHE_READ_MULT
            + self.cwrite5m * rin * CACHE_WRITE_5M_MULT
            + self.cwrite1h * rin * CACHE_WRITE_1H_MULT
        ) / 1_000_000.0


def find_jsonls(root: pathlib.Path) -> list[pathlib.Path]:
    """Every session JSONL AND every nested subagent JSONL. rglob, never glob."""
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.jsonl") if p.is_file())


def agent_type_for(path: pathlib.Path) -> str:
    """Subagent files carry a sibling <name>.meta.json declaring agentType."""
    if path.parent.name != "subagents":
        return "main"
    meta = path.with_suffix(".meta.json")
    if meta.exists():
        try:
            with meta.open(encoding="utf-8") as f:
                return (json.load(f).get("agentType") or "unknown-subagent")
        except Exception:
            return "unreadable-meta"
    return "unknown-subagent"


def scan(root: pathlib.Path, since: str | None):
    files = find_jsonls(root)
    by_id: dict[str, Rec] = {}
    seen_in_file: dict[str, pathlib.Path] = {}
    stats = {
        "files_scanned": len(files),
        "files_unreadable": 0,
        "lines_total": 0,
        "lines_unparseable": 0,
        "assistant_records_with_usage": 0,
        "unique_messages": 0,
        "streaming_duplicates_collapsed": 0,
        "cross_file_duplicates": 0,
        "records_missing_message_id": 0,
        "filtered_out_by_since": 0,
        "origin_markers_seen": 0,
    }

    for path in files:
        agent = agent_type_for(path)
        # Positional origin attribution: `origin` never appears on a usage-bearing
        # record (measured 0 / 45,557), so an assistant message inherits the most
        # recent preceding user turn's origin.kind IN THIS FILE. Reset per file so
        # attribution never leaks across transcripts.
        current_origin = "unattributed"
        try:
            fh = path.open(encoding="utf-8", errors="replace")
        except OSError:
            stats["files_unreadable"] += 1
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                stats["lines_total"] += 1
                try:
                    o = json.loads(line)
                except Exception:
                    stats["lines_unparseable"] += 1
                    continue
                org = o.get("origin")
                if isinstance(org, dict) and org.get("kind"):
                    current_origin = org["kind"]
                    stats["origin_markers_seen"] += 1
                if o.get("type") != "assistant":
                    continue
                msg = o.get("message")
                if not isinstance(msg, dict):
                    continue
                usage = msg.get("usage")
                if not isinstance(usage, dict):
                    continue
                stats["assistant_records_with_usage"] += 1

                mid = msg.get("id") or o.get("requestId")
                if not mid:
                    stats["records_missing_message_id"] += 1
                    mid = f"__noid__{path}:{stats['lines_total']}"

                ts = o.get("timestamp") or ""
                date = ts[:10] if len(ts) >= 10 else "unknown"
                if since and date != "unknown" and date < since:
                    stats["filtered_out_by_since"] += 1
                    continue

                if mid in by_id:
                    stats["streaming_duplicates_collapsed"] += 1
                    if seen_in_file.get(mid) != path:
                        stats["cross_file_duplicates"] += 1
                    by_id[mid].absorb(usage)
                else:
                    rec = Rec(date, o.get("sessionId") or "unknown",
                              agent, msg.get("model") or "unknown",
                              ts=ts, origin=current_origin)
                    rec.absorb(usage)
                    by_id[mid] = rec
                    seen_in_file[mid] = path

    stats["unique_messages"] = len(by_id)
    return files, list(by_id.values()), stats


DIMS = {
    "day": lambda r: r.date,
    "session": lambda r: r.session,
    "agent": lambda r: r.agent,
    "model": lambda r: r.model,
    "origin": lambda r: r.origin,   # DERIVED positionally -- see docstring
}


def aggregate(recs: list[Rec], dim: str):
    key = DIMS[dim]
    buckets: dict[str, dict] = defaultdict(
        lambda: {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0,
                 "messages": 0, "cost_usd": 0.0, "cost_known": True})
    for r in recs:
        b = buckets[key(r)]
        b["input"] += r.inp
        b["output"] += r.out
        b["cache_read"] += r.cread
        b["cache_creation"] += r.cwrite
        b["messages"] += 1
        c = r.cost()
        if c is None:
            b["cost_known"] = False
        else:
            b["cost_usd"] += c
    return dict(buckets)


def totals(recs: list[Rec]):
    t = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0,
         "messages": len(recs), "cost_usd": 0.0}
    unpriced = set()
    for r in recs:
        t["input"] += r.inp
        t["output"] += r.out
        t["cache_read"] += r.cread
        t["cache_creation"] += r.cwrite
        c = r.cost()
        if c is None:
            unpriced.add(r.model)
        else:
            t["cost_usd"] += c
    t["total_tokens"] = t["input"] + t["output"] + t["cache_read"] + t["cache_creation"]
    return t, sorted(unpriced)


# ---------------------------------------------------------------------------
# Weekly ceiling derivation.
# ---------------------------------------------------------------------------
OBSERVATIONS_FILENAME = "token-meter-observations.json"

# Candidate bases for what Claude Code's /usage meter might actually count.
# Which one is correct is NOT established anywhere -- so all are reported.
CEILING_BASES = [
    ("total_tokens",   "all tokens (input+output+cache-read+cache-write)"),
    ("billable_blend", "cost-weighted tokens (notional USD x 1e6 / opus-in rate)"),
    ("non_cache",      "input + output only (cache excluded)"),
    ("output_tokens",  "output tokens only"),
]


def default_week_start(today: date | None = None) -> str:
    """Most recent Monday (ISO week). An ASSUMPTION -- see caveats."""
    d = today or datetime.now(timezone.utc).date()
    return (d - timedelta(days=d.weekday())).isoformat()


def parse_ts(s: str) -> datetime | None:
    """Parse a JSONL ISO timestamp into an aware UTC datetime."""
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def window_from_reset(reset_iso: str, days: int = 7) -> tuple[datetime, datetime]:
    """
    Derive the usage window from the reset boundary the /usage panel STATES.

    This is the honest week definition and it is not a Monday. The panel says
    "resets Aug 7, 1:59pm America/Chicago", so the window that the displayed
    percentage describes is [reset - 7d, reset). Using an ISO Monday instead
    understates the window by roughly half:

        Monday-start (2026-08-03)   ->  386,825,339 tokens
        reset-derived (07-31 18:59Z) -> ~757-891M tokens

    A ceiling derived from the wrong window is wrong by that same factor, so
    --reset-at is preferred over --week-start whenever a reset time is known.
    """
    end = parse_ts(reset_iso)
    if end is None:
        raise ValueError(f"unparseable reset timestamp: {reset_iso!r}")
    return end - timedelta(days=days), end


def week_bases(recs: list[Rec], week_start: str,
               window: tuple[datetime, datetime] | None = None,
               as_of: datetime | None = None) -> dict:
    """
    Token totals for the current usage window, on each candidate meter basis.

    If `window` is given it is authoritative and applied at full timestamp
    resolution. Otherwise fall back to the coarse date-string comparison against
    `week_start` (day granularity, cannot express a 1:59pm boundary).

    `as_of` truncates the window at the instant a meter reading was taken, so a
    historical observation stays RE-DERIVABLE from disk instead of being a number
    recorded once and free to drift. Back-filling an old reading and re-running
    today must produce the same bases.
    """
    if window is not None:
        lo, hi = window
        if as_of is not None and as_of < hi:
            hi = as_of      # truncate to the instant the meter was actually read
        wk = []
        for r in recs:
            dt = parse_ts(r.ts)
            if dt is None:
                continue
            if lo <= dt < hi:
                wk.append(r)
    else:
        wk = [r for r in recs if r.date != "unknown" and r.date >= week_start]
    t, _ = totals(wk)
    return {
        "messages": t["messages"],
        "total_tokens": t["total_tokens"],
        "non_cache": t["input"] + t["output"],
        "output_tokens": t["output"],
        # Cost-weighted: express notional USD back as an opus-input-equivalent
        # token count, so a meter that weights by cost has a comparable basis.
        "billable_blend": int(round(t["cost_usd"] * 1_000_000 / RATES["claude-opus-5"][0])),
        "cost_usd": t["cost_usd"],
    }


# ---------------------------------------------------------------------------
# RECONCILIATION against Claude Code's own /usage panel.
#
# This is the control that makes the instrument falsifiable against something
# OUTSIDE itself. Every other check in this file tests the code against its own
# fixtures; this one tests it against a number Anthropic's client displayed.
#
# Transcribed from the panel Jon pasted 2026-08-03 ~08:27 CDT. Displayed values
# are rounded to 3-4 significant figures, so exact equality is not expected --
# TOLERANCE_PCT bounds what counts as agreement.
# ---------------------------------------------------------------------------
PANEL_SESSION = "9e21da9b-47b7-4cb1-ac6d-15d9806cd227"
PANEL_READ_AT = "2026-08-03T13:27:00+00:00"
PANEL_TOTAL_USD = 98.93
PANEL_TOLERANCE_PCT = 5.0
PANEL_BY_MODEL = {   # model -> (input, output, cache_read, cache_write, usd)
    "claude-opus-5":    (14_300, 497_900, 82_600_000, 3_100_000, 78.19),
    "claude-sonnet-5":  (386,    148_100, 22_200_000,   630_700, 11.24),
    "claude-fable-5":   (1_000,   30_600,  1_500_000,   516_100,  9.50),
    "claude-haiku-4-5": (2_500,       68,          0,         0,  0.0028),
}


def reconcile_panel(root: pathlib.Path) -> tuple[str, bool]:
    """
    Recompute the panel's session from disk and compare. Returns (report, passed).

    The panel reading is a snapshot mid-session, so records after PANEL_READ_AT
    are excluded. Our figure is expected to land slightly UNDER the panel's:
    the cutoff is approximate to the minute, and any subagent whose records carry
    a different sessionId falls outside this session filter.
    """
    cut = parse_ts(PANEL_READ_AT)
    by: dict[str, Rec] = {}
    files = find_jsonls(root)
    for path in files:
        try:
            fh = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if o.get("type") != "assistant" or o.get("sessionId") != PANEL_SESSION:
                    continue
                msg = o.get("message")
                if not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
                    continue
                dt = parse_ts(o.get("timestamp") or "")
                if dt is None or dt >= cut:
                    continue
                mid = msg.get("id") or o.get("requestId")
                if mid not in by:
                    by[mid] = Rec(str(dt.date()), PANEL_SESSION, "x",
                                  msg.get("model") or "unknown", ts=o.get("timestamp") or "")
                by[mid].absorb(msg["usage"])

    recs = list(by.values())
    agg = aggregate(recs, "model")
    ours = sum(b["cost_usd"] for b in agg.values())

    L = []
    A = L.append
    A("")
    A("-- RECONCILIATION vs CLAUDE CODE'S /usage PANEL (external control) --")
    A(f"  session   : {PANEL_SESSION}")
    A(f"  panel read: {PANEL_READ_AT}  (records at/after this are excluded)")
    A("")
    A(f"  {'model':<20} {'source':<7} {'input':>9} {'output':>10} "
      f"{'cache-rd':>13} {'cache-wr':>11} {'USD':>9}")
    A(f"  {'-' * 20} {'-' * 7} {'-' * 9} {'-' * 10} {'-' * 13} {'-' * 11} {'-' * 9}")
    for model, (pi, po, pcr, pcw, pusd) in sorted(PANEL_BY_MODEL.items()):
        b = agg.get(model)
        A(f"  {model:<20} {'panel':<7} {pi:>9,} {po:>10,} {pcr:>13,} {pcw:>11,} {pusd:>9,.2f}")
        if b:
            A(f"  {'':<20} {'ledger':<7} {b['input']:>9,} {b['output']:>10,} "
              f"{b['cache_read']:>13,} {b['cache_creation']:>11,} {b['cost_usd']:>9,.2f}")
        else:
            A(f"  {'':<20} {'ledger':<7} {'--- absent under this sessionId ---':>56}")
    A("")
    delta = ours - PANEL_TOTAL_USD
    pct = abs(delta) / PANEL_TOTAL_USD * 100 if PANEL_TOTAL_USD else float("inf")
    A(f"  panel total : ${PANEL_TOTAL_USD:>9,.2f}")
    A(f"  ledger total: ${ours:>9,.2f}   ({delta:+,.2f}, {pct:.1f}%)")
    passed = pct <= PANEL_TOLERANCE_PCT
    A(f"  verdict     : {'AGREE' if passed else 'DISAGREE'} "
      f"(tolerance {PANEL_TOLERANCE_PCT:g}%)")
    if not passed:
        A("  !! The ledger disagrees with the client's own figure. Do not publish")
        A("     totals until this is explained. A ~9x output overshoot means the")
        A("     streaming dedup broke; a skewed per-model split means the rates did.")
    return "\n".join(L), passed


def observations_path() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2] / "exchange" / OBSERVATIONS_FILENAME


def load_observations(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("observations", []) if isinstance(data, dict) else []
    except Exception:
        return []


def render_ceiling(pct: float, week_start: str, wb: dict,
                   observations: list[dict],
                   window: tuple[datetime, datetime] | None = None) -> str:
    L = []
    A = L.append
    A("")
    A("-- IMPLIED WEEKLY CEILING (DERIVED, PROVISIONAL) --")
    A("  The weekly ceiling is NOT recorded anywhere in this repo. It is derived")
    A("  here from a meter reading Jon supplied. Jon's percentage is the")
    A("  authoritative input; this tool cannot read /usage itself.")
    A("")
    A(f"  meter reading supplied : {pct:g}% of the weekly budget consumed")
    if window is not None:
        lo, hi = window
        A(f"  window (FROM RESET)    : {lo.isoformat()} .. {hi.isoformat()}")
        A("                           derived as (stated reset time - 7 days), NOT a")
        A("                           Monday. The panel's reset is 1:59pm Chicago, so a")
        A("                           midnight-Monday window measures the wrong interval")
        A("                           and understates the denominator by roughly half.")
    else:
        A(f"  week start (ASSUMED)   : {week_start}  (most recent Monday unless --week-start given)")
        A("  !! NO RESET TIME GIVEN. This is a midnight-Monday assumption and the real")
        A("     reset is mid-afternoon Chicago time. Prefer --reset-at.")
    A(f"  messages this window   : {wb['messages']:,}")
    A("")
    A("  ceiling = (tokens consumed this week) / (meter pct / 100)")
    A("")
    A("")
    A("  !! ASYMMETRIC SCOPE -- THIS BIASES THE CEILING DOWNWARD.")
    A("     The panel states its own scope: 'local sessions on this machine only --")
    A("     does not include other devices or claude.ai.' So the NUMERATOR (tokens)")
    A("     is a LOWER BOUND from this disk, while the DENOMINATOR (the percentage)")
    A("     is a WHOLE-ACCOUNT figure. Dividing one by the other understates the")
    A("     true ceiling by however much usage happened off this machine. Every")
    A("     ceiling below is therefore a FLOOR, not an estimate. Do not quietly")
    A("     divide; the delta derivation in (b) is what limits this bias.")
    A("")
    A("  !! A +50% WEEKLY-LIMIT PROMOTION IS ACTIVE THROUGH 2026-08-19.")
    A("     Any ceiling derived from a reading taken during the promo describes the")
    A("     PROMOTIONAL ceiling. When it lapses the allowance drops by roughly a")
    A("     third (1 - 1/1.5 = 33%). A budget built on these numbers must not be")
    A("     carried past Aug 19 without re-deriving from a post-promo reading.")
    A("")
    A("  !! THE METER'S UNIT IS UNKNOWN. Nothing establishes whether /usage counts")
    A("     tokens, output tokens, or cost-weighted usage. One row below is right;")
    A("     this repo cannot say which. Do not quote a single figure as 'the ceiling'.")
    A("")
    A(f"  {'basis':<52} {'this week':>16} {'implied ceiling':>18}")
    A(f"  {'-' * 52} {'-' * 16} {'-' * 18}")
    for key, label in CEILING_BASES:
        consumed = wb[key]
        implied = consumed / (pct / 100.0) if pct else float("nan")
        A(f"  {label:<52} {consumed:>16,} {implied:>18,.0f}")
    A("")
    A(f"  (notional USD this week: ${wb['cost_usd']:,.2f}"
      f"  -> implied weekly notional budget ${wb['cost_usd'] / (pct / 100.0):,.2f})"
      if pct else "")

    # Cross-check across readings.
    #
    # Readings are NOT all the same evidence grade. A percentage transcribed off
    # the panel is primary; a percentage Jon recalled in conversation is not.
    # On 2026-08-03 the two differed by 12 points eleven minutes apart (40% recalled
    # at 13:16Z, 52% on the panel at 13:27Z) -- so mixing grades in one cross-check
    # would manufacture a "disagreement" out of a recall gap, not a model error.
    same_week = [o for o in observations if o.get("week_start") == week_start]
    primary = [o for o in same_week if o.get("grade", "panel") == "panel"]
    recalled = [o for o in same_week if o.get("grade") == "recall"]
    A("")
    if recalled:
        A(f"  {len(recalled)} reading(s) excluded from cross-check as grade=recall")
        A("  (spoken from memory, not transcribed from the panel). Listed, not used:")
        for o in recalled:
            A(f"    {o.get('recorded_utc', '?')}  {o.get('pct')}%  -- {o.get('note', '')[:52]}")
        A("")
    if len(primary) < 2:
        A(f"  CROSS-CHECK: not yet possible -- {len(primary)} panel-grade reading(s) this week.")
        A("  One reading is one equation; it cannot be validated. Take a second")
        A("  reading later this week and re-run with --record-meter to complete it.")
    else:
        same_week = sorted(primary,
                           key=lambda o: o.get("read_at") or o.get("recorded_utc") or "")
        A(f"  CROSS-CHECK across {len(same_week)} panel readings this window:")
        A("")
        A("  (a) LEVEL derivation -- ceiling = tokens_since_window_start / pct")
        for key, label in CEILING_BASES:
            implieds = [o["bases"][key] / (o["pct"] / 100.0)
                        for o in same_week if o.get("pct") and o.get("bases", {}).get(key)]
            if len(implieds) < 2:
                continue
            lo_i, hi_i = min(implieds), max(implieds)
            spread = (hi_i - lo_i) / lo_i * 100 if lo_i else float("inf")
            verdict = "CONSISTENT" if spread <= 10 else "DISAGREE -- model is wrong"
            A(f"    {label:<46} {lo_i:>15,.0f} ..{hi_i:>15,.0f} ({spread:5.1f}%) {verdict}")
        A("")
        A("  (b) DELTA derivation -- ceiling = (tokens between readings) / (pct rise)")
        A("      THE STRONGER ESTIMATOR. Usage the meter counts but this machine")
        A("      cannot see -- other devices, claude.ai -- enters the LEVEL figure as")
        A("      a constant offset. Differencing two readings CANCELS any constant.")
        A("      Where level and delta disagree, that gap IS the unseen component.")
        deltas: dict[str, float] = {}
        for i in range(len(same_week) - 1):
            o1, o2 = same_week[i], same_week[i + 1]
            dpct = (o2.get("pct") or 0) - (o1.get("pct") or 0)
            t1 = (o1.get("read_at") or "?")[11:16]
            t2 = (o2.get("read_at") or "?")[11:16]
            if dpct <= 0:
                A(f"    readings {i}->{i+1}: meter did not rise ({dpct:+g} pts) -- skipped")
                continue
            A(f"    readings {i}->{i+1}: meter +{dpct:g} pts  ({t1}Z -> {t2}Z)")
            for key, label in CEILING_BASES:
                b1 = o1.get("bases", {}).get(key)
                b2 = o2.get("bases", {}).get(key)
                if b1 is None or b2 is None or b2 <= b1:
                    continue
                implied = (b2 - b1) / (dpct / 100.0)
                deltas[key] = implied
                A(f"      {label:<46} {b2 - b1:>14,} tok ->{implied:>16,.0f}")
        if deltas:
            A("")
            A("  (c) LEVEL vs DELTA -- the informative comparison")
            for key, label in CEILING_BASES:
                lv = [o["bases"][key] / (o["pct"] / 100.0)
                      for o in same_week if o.get("pct") and o.get("bases", {}).get(key)]
                if not lv or key not in deltas:
                    continue
                lvl = sum(lv) / len(lv)
                dl = deltas[key]
                ratio = dl / lvl if lvl else float("inf")
                A(f"    {label:<42} level~{lvl:>15,.0f}  delta{dl:>15,.0f}  {ratio:4.2f}x")
                if ratio < 0.87:
                    A("      meter rose FASTER than local tokens -> off-machine or")
                    A("      non-token usage present; the LEVEL ceiling is overstated.")
                elif ratio > 1.15:
                    A("      local tokens grew FASTER per meter-point -> the LEVEL figure")
                    A("      carries pre-window or other-device load; it is understated.")

            # Which basis is the meter most plausibly counting? The one whose
            # level and delta derivations agree best -- i.e. the basis under which
            # the meter behaves most nearly linearly. This is WEAK evidence from
            # two points, but it is evidence, and it is the only handle this repo
            # has on the meter's unit.
            scored = []
            for key, label in CEILING_BASES:
                lv = [o["bases"][key] / (o["pct"] / 100.0)
                      for o in same_week if o.get("pct") and o.get("bases", {}).get(key)]
                if lv and key in deltas and sum(lv):
                    lvl = sum(lv) / len(lv)
                    scored.append((abs(deltas[key] / lvl - 1.0), label, deltas[key], lvl))
            if scored:
                scored.sort()
                dev, label, dl, lvl = scored[0]
                A("")
                A(f"  BEST-AGREEING BASIS (weak evidence, 2 points): {label}")
                A(f"    level/delta deviation {dev * 100:.0f}% -- the smallest of "
                  f"{len(scored)} bases.")
                A("    Under this basis the meter is closest to linear in what this")
                A("    machine can see. It is a hint about the meter's unit, NOT a")
                A("    determination; a third reading would sharpen or overturn it.")
        A("")
        A("  A material disagreement means the linear model (or the window, or the")
        A("  basis) is wrong. Do NOT average discordant readings.")
    return "\n".join(x for x in L if x is not None)


CAVEATS = [
    "DOLLARS ARE NOTIONAL, NOT SPEND. Rates are Anthropic first-party API list",
    "prices. This account is on a Max *subscription* (flat monthly fee), so no",
    "per-token charge is actually billed. Read the USD column as 'what this",
    "compute would have cost at API list price' -- a usage-intensity proxy.",
    "",
    "THE WEEKLY CEILING HAS NO GROUND TRUTH IN THIS REPO. Nothing here states",
    "the plan's token/usage allowance in absolute terms, so this ledger measures",
    "SPEND, not a PERCENTAGE. No '% of budget' figure is computed from a guessed",
    "denominator. The ceiling IS derivable from a /usage meter reading Jon",
    "supplies -- run --ceiling-from-meter PCT. That result is provisional: the",
    "meter's unit is unknown and one reading cannot be cross-checked. See the",
    "intake packet at",
    "skills/intake/needs-design/anthropic-budget-endpoint-2026-08-03.md.",
    "",
    "COVERAGE IS LOCAL-DISK ONLY. Sessions deleted by CC retention are absent;",
    "claude.ai (web) usage is not in these JSONLs at all.",
]


def fmt_int(n: int) -> str:
    return f"{n:,}"


def render(files, recs, stats, dim, since, root) -> str:
    t, unpriced = totals(recs)
    L = []
    A = L.append
    A("=" * 78)
    A("TOKEN / COST LEDGER")
    A("=" * 78)
    A(f"generated       : {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    A(f"source root     : {root}")
    A(f"since filter    : {since or '(none -- all history on disk)'}")
    A(f"rate source     : {RATES_SOURCE}")
    A("")
    A("-- SCAN DENOMINATOR (the number that makes this instrument checkable) --")
    A(f"  JSONL files scanned          : {fmt_int(stats['files_scanned'])}")
    top = sum(1 for p in files if p.parent.name != "subagents")
    sub = stats["files_scanned"] - top
    pct = (sub / stats["files_scanned"] * 100) if stats["files_scanned"] else 0.0
    A(f"    of which top-level sessions: {fmt_int(top)}")
    A(f"    of which subagent files    : {fmt_int(sub)}  ({pct:.1f}% -- a top-level-only")
    A("                                   glob would miss this share entirely)")
    A(f"  files unreadable             : {fmt_int(stats['files_unreadable'])}")
    A(f"  lines read                   : {fmt_int(stats['lines_total'])}")
    A(f"  lines unparseable            : {fmt_int(stats['lines_unparseable'])}")
    A(f"  assistant records w/ usage   : {fmt_int(stats['assistant_records_with_usage'])}")
    A(f"  unique messages after dedup  : {fmt_int(stats['unique_messages'])}")
    A(f"  streaming dupes collapsed    : {fmt_int(stats['streaming_duplicates_collapsed'])}"
      "  <- summing these would inflate output tokens")
    A(f"  cross-file dupes             : {fmt_int(stats['cross_file_duplicates'])}")
    if stats["records_missing_message_id"]:
        A(f"  records missing message.id   : {fmt_int(stats['records_missing_message_id'])}")
    if stats["filtered_out_by_since"]:
        A(f"  records excluded by --since  : {fmt_int(stats['filtered_out_by_since'])}")
    A("")
    A("-- TOTALS (token classes kept separate; they price differently) --")
    A(f"  input tokens          : {fmt_int(t['input']):>16}")
    A(f"  output tokens         : {fmt_int(t['output']):>16}")
    A(f"  cache-read tokens     : {fmt_int(t['cache_read']):>16}   (~0.10x input rate)")
    A(f"  cache-creation tokens : {fmt_int(t['cache_creation']):>16}   (1.25x / 2.00x input rate)")
    A(f"  {'-' * 40}")
    A(f"  all tokens            : {fmt_int(t['total_tokens']):>16}")
    A(f"  notional API cost     : ${t['cost_usd']:>15,.2f}   (NOT billed -- see caveats)")
    if unpriced:
        A(f"  !! unpriced models (excluded from USD): {', '.join(unpriced)}")
    A("")
    A(f"-- BY {dim.upper()} --")
    buckets = aggregate(recs, dim)
    order = sorted(buckets.items(), key=lambda kv: (-kv[1]["cost_usd"], kv[0])) \
        if dim != "day" else sorted(buckets.items())
    A(f"  {dim:<34} {'msgs':>7} {'input':>13} {'output':>12} "
      f"{'cache-rd':>14} {'cache-wr':>13} {'USD*':>11}")
    A(f"  {'-' * 34} {'-' * 7} {'-' * 13} {'-' * 12} {'-' * 14} {'-' * 13} {'-' * 11}")
    for k, b in order:
        label = (k[:33] + "…") if len(k) > 34 else k
        usd = f"{b['cost_usd']:,.2f}" + ("" if b["cost_known"] else "+")
        A(f"  {label:<34} {b['messages']:>7,} {b['input']:>13,} {b['output']:>12,} "
          f"{b['cache_read']:>14,} {b['cache_creation']:>13,} {usd:>11}")
    A("")
    A("-- CAVEATS --")
    for c in CAVEATS:
        A(f"  {c}" if c else "")
    A("=" * 78)
    return "\n".join(L)


def build_json(files, recs, stats, dim, since, root):
    t, unpriced = totals(recs)
    top = sum(1 for p in files if p.parent.name != "subagents")
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_root": str(root),
        "since": since,
        "rate_source": RATES_SOURCE,
        "cost_is_notional_not_billed": True,
        "weekly_ceiling_known": False,
        "scan": {**stats, "files_top_level": top,
                 "files_subagent": stats["files_scanned"] - top},
        "totals": t,
        "unpriced_models": unpriced,
        "by": dim,
        "buckets": aggregate(recs, dim),
        "caveats": [c for c in CAVEATS if c],
    }


# ---------------------------------------------------------------------------
# Self-test: a real negative control plus a known-value fixture.
# An instrument that cannot fail is decoration.
# ---------------------------------------------------------------------------
def _line(**kw) -> str:
    return json.dumps(kw)


def self_test() -> int:
    failures: list[str] = []

    def check(name, got, want):
        if got != want:
            failures.append(f"  FAIL {name}: got {got!r}, want {want!r}")
        else:
            print(f"  ok   {name}: {got!r}")

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="ledger-selftest-"))
    proj = tmp / "slug"
    (proj / "sess-uuid" / "subagents").mkdir(parents=True)

    # --- NEGATIVE CONTROL: real records, no usage fields anywhere. Must be zero.
    neg = proj / "negative.jsonl"
    neg.write_text("\n".join([
        _line(type="user", timestamp="2026-08-01T00:00:00Z", sessionId="s0",
              message={"role": "user", "content": "hi"}),
        _line(type="assistant", timestamp="2026-08-01T00:00:01Z", sessionId="s0",
              message={"id": "m_none", "model": "claude-opus-5",
                       "content": [{"type": "text", "text": "no usage key here"}]}),
        _line(type="attachment", timestamp="2026-08-01T00:00:02Z", sessionId="s0"),
        "",
        "{ this line is not valid json",
    ]), encoding="utf-8")

    _f, recs, st = scan(proj, None)
    t, _ = totals(recs)
    check("negative control: unique messages", st["unique_messages"], 0)
    check("negative control: total tokens", t["total_tokens"], 0)
    check("negative control: cost", round(t["cost_usd"], 10), 0.0)
    check("negative control: malformed line counted", st["lines_unparseable"], 1)
    check("negative control: file still scanned", st["files_scanned"], 1)
    neg.unlink()

    # --- KNOWN VALUES, including streaming duplicates that must NOT be summed.
    # msg A streams three snapshots: output grows 5 -> 40 -> 100. Correct = 100.
    # Naive summation would give 145; first-record-wins would give 5.
    main = proj / "known.jsonl"
    ua = lambda out: {"input_tokens": 10, "output_tokens": out,
                      "cache_read_input_tokens": 1000,
                      "cache_creation_input_tokens": 200,
                      "cache_creation": {"ephemeral_5m_input_tokens": 200,
                                         "ephemeral_1h_input_tokens": 0}}
    main.write_text("\n".join([
        _line(type="assistant", timestamp="2026-08-01T10:00:00Z", sessionId="sA",
              message={"id": "m_A", "model": "claude-opus-5", "usage": ua(5)}),
        _line(type="assistant", timestamp="2026-08-01T10:00:01Z", sessionId="sA",
              message={"id": "m_A", "model": "claude-opus-5", "usage": ua(40)}),
        _line(type="assistant", timestamp="2026-08-01T10:00:02Z", sessionId="sA",
              message={"id": "m_A", "model": "claude-opus-5", "usage": ua(100)}),
        # msg B: different day, haiku, 1h cache write.
        _line(type="assistant", timestamp="2026-08-02T11:00:00Z", sessionId="sA",
              message={"id": "m_B", "model": "claude-haiku-4-5-20251001",
                       "usage": {"input_tokens": 7, "output_tokens": 3,
                                 "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 500,
                                 "cache_creation": {"ephemeral_5m_input_tokens": 0,
                                                    "ephemeral_1h_input_tokens": 500}}}),
    ]), encoding="utf-8")

    # subagent file + meta, to prove nested walk and agentType resolution
    sub = proj / "sess-uuid" / "subagents" / "agent-abc.jsonl"
    sub.write_text(_line(type="assistant", timestamp="2026-08-02T12:00:00Z",
                         sessionId="sA",
                         message={"id": "m_C", "model": "claude-sonnet-5",
                                  "usage": {"input_tokens": 1, "output_tokens": 2,
                                            "cache_read_input_tokens": 3,
                                            "cache_creation_input_tokens": 4,
                                            "cache_creation": {
                                                "ephemeral_5m_input_tokens": 4,
                                                "ephemeral_1h_input_tokens": 0}}}),
                   encoding="utf-8")
    (proj / "sess-uuid" / "subagents" / "agent-abc.meta.json").write_text(
        json.dumps({"agentType": "wiki-executor", "model": "sonnet"}), encoding="utf-8")

    files, recs, st = scan(proj, None)
    t, unpriced = totals(recs)

    check("nested walk: files scanned", st["files_scanned"], 2)
    check("dedup: unique messages", st["unique_messages"], 3)
    check("dedup: duplicates collapsed", st["streaming_duplicates_collapsed"], 2)
    check("max-reduction input",  t["input"], 10 + 7 + 1)
    check("max-reduction output", t["output"], 100 + 3 + 2)   # NOT 145, NOT 5
    check("cache_read total",     t["cache_read"], 1000 + 0 + 3)
    check("cache_creation total", t["cache_creation"], 200 + 500 + 4)
    check("unpriced models", unpriced, [])

    # Exact expected cost, computed independently of the aggregation path.
    exp = (
        (10 * 5.0 + 100 * 25.0 + 1000 * 5.0 * 0.10 + 200 * 5.0 * 1.25)      # opus-5
        + (7 * 1.0 + 3 * 5.0 + 0 * 1.0 * 0.10 + 500 * 1.0 * 2.00)           # haiku (1h)
        + (1 * 3.0 + 2 * 15.0 + 3 * 3.0 * 0.10 + 4 * 3.0 * 1.25)            # sonnet-5
    ) / 1_000_000.0
    check("cost exact", round(t["cost_usd"], 12), round(exp, 12))

    agents = aggregate(recs, "agent")
    check("agentType from sibling meta.json", sorted(agents), ["main", "wiki-executor"])
    days = aggregate(recs, "day")
    check("per-day split", sorted(days), ["2026-08-01", "2026-08-02"])
    check("per-day 08-01 output", days["2026-08-01"]["output"], 100)
    models = aggregate(recs, "model")
    check("date-suffixed model kept as label",
          sorted(models), ["claude-haiku-4-5-20251001", "claude-opus-5", "claude-sonnet-5"])

    # --since filter
    _f2, recs2, st2 = scan(proj, "2026-08-02")
    t2, _ = totals(recs2)
    check("--since excludes earlier day", t2["output"], 3 + 2)
    check("--since counts exclusions", st2["filtered_out_by_since"], 3)

    # unknown model must be flagged, not silently priced at zero
    unk = proj / "unknown.jsonl"
    unk.write_text(_line(type="assistant", timestamp="2026-08-02T13:00:00Z",
                         sessionId="sZ",
                         message={"id": "m_U", "model": "claude-from-the-future",
                                  "usage": {"input_tokens": 5, "output_tokens": 5}}),
                   encoding="utf-8")
    _f3, recs3, _st3 = scan(proj, None)
    _t3, unpriced3 = totals(recs3)
    check("unknown model surfaces as unpriced", unpriced3, ["claude-from-the-future"])

    # empty tree -> zero files (drives exit 2 in main)
    empty = tmp / "empty"
    empty.mkdir()
    f4, recs4, st4 = scan(empty, None)
    check("empty tree: zero files", st4["files_scanned"], 0)
    check("empty tree: zero records", len(recs4), 0)

    # ---- weekly-ceiling derivation ----
    check("week start default is a Monday",
          datetime.strptime(default_week_start(date(2026, 8, 5)), "%Y-%m-%d").weekday(), 0)
    check("week start default for Mon 2026-08-03",
          default_week_start(date(2026, 8, 3)), "2026-08-03")

    # Use the known fixture (recs from the 3-message set, minus the unknown-model file).
    unk.unlink()
    _f5, recs5, _st5 = scan(proj, None)
    wb = week_bases(recs5, "2026-08-02")   # excludes the 08-01 opus message
    check("week basis: output tokens (08-02 onward)", wb["output_tokens"], 3 + 2)
    check("week basis: non-cache", wb["non_cache"], (7 + 3) + (1 + 2))
    check("week basis: messages", wb["messages"], 2)
    wb_all = week_bases(recs5, "2026-08-01")
    check("week basis widens with earlier start", wb_all["output_tokens"], 105)

    # ceiling = consumed / (pct/100). At 50%, ceiling is exactly 2x consumed.
    implied = wb["output_tokens"] / 0.50
    check("implied ceiling at 50% is 2x consumed", implied, 10.0)

    # NEGATIVE CONTROL for the cross-check: two readings that imply wildly
    # different ceilings must be reported as DISAGREE, never averaged.
    discordant = [
        {"week_start": "2026-08-02", "pct": 10.0, "bases": {"output_tokens": 5,
         "total_tokens": 5, "non_cache": 5, "billable_blend": 5}},
        {"week_start": "2026-08-02", "pct": 80.0, "bases": {"output_tokens": 5,
         "total_tokens": 5, "non_cache": 5, "billable_blend": 5}},
    ]
    txt = render_ceiling(50.0, "2026-08-02", wb, discordant)
    check("discordant readings flagged, not averaged", "DISAGREE" in txt, True)
    check("discordant readings not silently consistent", "CONSISTENT" in txt, False)

    concordant = [
        {"week_start": "2026-08-02", "pct": 50.0, "bases": {"output_tokens": 5,
         "total_tokens": 5, "non_cache": 5, "billable_blend": 5}},
        {"week_start": "2026-08-02", "pct": 51.0, "bases": {"output_tokens": 5,
         "total_tokens": 5, "non_cache": 5, "billable_blend": 5}},
    ]
    txt2 = render_ceiling(50.0, "2026-08-02", wb, concordant)
    check("near-agreeing readings marked consistent", "CONSISTENT" in txt2, True)

    # A single reading must refuse to cross-check rather than implying validation.
    txt3 = render_ceiling(40.0, "2026-08-02", wb, [])
    check("single reading refuses cross-check",
          "CROSS-CHECK: not yet possible" in txt3, True)
    check("meter-unit uncertainty always stated", "UNIT IS UNKNOWN" in txt3, True)

    # A recall-grade reading must NOT be allowed to satisfy the cross-check.
    mixed = [
        {"week_start": "2026-08-02", "pct": 40.0, "grade": "recall",
         "bases": {"output_tokens": 5, "total_tokens": 5, "non_cache": 5,
                   "billable_blend": 5}},
        {"week_start": "2026-08-02", "pct": 52.0, "grade": "panel",
         "bases": {"output_tokens": 5, "total_tokens": 5, "non_cache": 5,
                   "billable_blend": 5}},
    ]
    txt4 = render_ceiling(52.0, "2026-08-02", wb, mixed)
    check("recall reading excluded from cross-check",
          "CROSS-CHECK: not yet possible" in txt4, True)
    check("recall reading still disclosed", "grade=recall" in txt4, True)

    # ---- DELTA derivation: two points, known arithmetic ----
    # Between readings the meter rises 10 pts while local output grows by 50 tok,
    # so the delta-implied ceiling is exactly 50 / 0.10 = 500.
    two_pt = [
        {"week_start": "2026-08-02", "pct": 50.0, "grade": "panel",
         "read_at": "2026-08-03T13:27:00+00:00",
         "bases": {"output_tokens": 100, "total_tokens": 100, "non_cache": 100,
                   "billable_blend": 100}},
        {"week_start": "2026-08-02", "pct": 60.0, "grade": "panel",
         "read_at": "2026-08-03T20:50:00+00:00",
         "bases": {"output_tokens": 150, "total_tokens": 150, "non_cache": 150,
                   "billable_blend": 150}},
    ]
    txt5 = render_ceiling(60.0, "2026-08-02", wb, two_pt)
    check("delta derivation section present", "DELTA derivation" in txt5, True)
    check("delta ceiling arithmetic (50 tok / 10 pts = 500)", "500" in txt5, True)
    check("level-vs-delta comparison emitted", "LEVEL vs DELTA" in txt5, True)
    # Level here: 100/.5=200 and 150/.6=250, mean 225. Delta 500 => 2.22x, "understated".
    check("delta >> level is called out as understatement",
          "understated" in txt5, True)
    # Order must not depend on input order.
    txt5r = render_ceiling(60.0, "2026-08-02", wb, list(reversed(two_pt)))
    check("readings sorted by read_at, not input order",
          ("500" in txt5r) and ("did not rise" not in txt5r), True)
    # A meter that FELL between readings must be refused, not turned into a negative.
    falling = [dict(two_pt[0]), dict(two_pt[1], pct=40.0)]
    txt6 = render_ceiling(40.0, "2026-08-02", wb, falling)
    check("falling meter refused, not divided", "did not rise" in txt6, True)
    # Mandatory honesty clauses.
    check("lower-bound bias stated", "biases the ceiling downward" in txt5.lower()
          or "BIASES THE CEILING DOWNWARD" in txt5, True)
    check("promo caveat stated", "+50% WEEKLY-LIMIT PROMOTION" in txt5, True)

    # ---- window derivation from a stated reset time ----
    lo, hi = window_from_reset("2026-08-07T13:59:00-05:00")
    check("window end == stated reset (in UTC)", hi.isoformat(), "2026-08-07T18:59:00+00:00")
    check("window start == reset - 7d", lo.isoformat(), "2026-07-31T18:59:00+00:00")
    check("window is not a Monday boundary", lo.weekday() == 0, False)

    # The window must bite at TIME resolution, not date resolution. Two messages
    # on the same calendar day, straddling a mid-afternoon boundary.
    wtree = tmp / "wtree"
    wtree.mkdir()
    (wtree / "w.jsonl").write_text("\n".join([
        _line(type="assistant", timestamp="2026-07-31T17:00:00Z", sessionId="sW",
              message={"id": "m_before", "model": "claude-opus-5",
                       "usage": {"input_tokens": 0, "output_tokens": 111,
                                 "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0}}),
        _line(type="assistant", timestamp="2026-07-31T20:00:00Z", sessionId="sW",
              message={"id": "m_after", "model": "claude-opus-5",
                       "usage": {"input_tokens": 0, "output_tokens": 222,
                                 "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0}}),
    ]), encoding="utf-8")
    _fw, recsw, _sw = scan(wtree, None)
    wb_win = week_bases(recsw, "ignored", (lo, hi))
    check("window excludes pre-reset message on the same day",
          wb_win["output_tokens"], 222)
    # and the date-string path CANNOT make that distinction -- prove the gap is real
    wb_day = week_bases(recsw, "2026-07-31", None)
    check("date-granularity path over-counts (why --reset-at exists)",
          wb_day["output_tokens"], 333)

    # ---- positional origin attribution ----
    otree = tmp / "otree"
    otree.mkdir()
    (otree / "o.jsonl").write_text("\n".join([
        # an assistant message BEFORE any origin marker -> must be "unattributed"
        _line(type="assistant", timestamp="2026-08-01T09:00:00Z", sessionId="sO",
              message={"id": "m_pre", "model": "claude-opus-5",
                       "usage": {"input_tokens": 0, "output_tokens": 1,
                                 "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0}}),
        _line(type="user", timestamp="2026-08-01T09:01:00Z", sessionId="sO",
              origin={"kind": "human"}, message={"role": "user", "content": "go"}),
        _line(type="assistant", timestamp="2026-08-01T09:02:00Z", sessionId="sO",
              message={"id": "m_h", "model": "claude-opus-5",
                       "usage": {"input_tokens": 0, "output_tokens": 10,
                                 "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0}}),
        _line(type="user", timestamp="2026-08-01T09:03:00Z", sessionId="sO",
              origin={"kind": "task-notification"},
              message={"role": "user", "content": "done"}),
        _line(type="assistant", timestamp="2026-08-01T09:04:00Z", sessionId="sO",
              message={"id": "m_t", "model": "claude-opus-5",
                       "usage": {"input_tokens": 0, "output_tokens": 20,
                                 "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0}}),
    ]), encoding="utf-8")
    _fo, recso, sto = scan(otree, None)
    origins = aggregate(recso, "origin")
    check("origin markers counted", sto["origin_markers_seen"], 2)
    check("origin buckets", sorted(origins),
          ["human", "task-notification", "unattributed"])
    check("pre-marker spend is NOT folded into human",
          origins["unattributed"]["output"], 1)
    check("origin attributed to nearest preceding marker",
          (origins["human"]["output"], origins["task-notification"]["output"]), (10, 20))

    # NEGATIVE CONTROL for origin: attribution must not leak ACROSS files.
    otree2 = tmp / "otree2"
    (otree2 / "sub" / "subagents").mkdir(parents=True)
    (otree2 / "a.jsonl").write_text(
        _line(type="user", timestamp="2026-08-01T09:00:00Z", sessionId="sP",
              origin={"kind": "coordinator"}, message={"role": "user", "content": "x"}),
        encoding="utf-8")
    (otree2 / "sub" / "subagents" / "agent-z.jsonl").write_text(
        _line(type="assistant", timestamp="2026-08-01T09:05:00Z", sessionId="sP",
              message={"id": "m_leak", "model": "claude-opus-5",
                       "usage": {"input_tokens": 0, "output_tokens": 9,
                                 "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0}}),
        encoding="utf-8")
    _f6, recs6, _st6 = scan(otree2, None)
    o6 = aggregate(recs6, "origin")
    check("origin does not leak across files", sorted(o6), ["unattributed"])

    print()
    if failures:
        print("SELF-TEST FAILED")
        print("\n".join(failures))
        return 1
    print("SELF-TEST PASSED - negative control yields zero; known values sum exactly.")
    return 0


def default_root() -> pathlib.Path:
    return pathlib.Path(os.path.expanduser("~")) / ".claude" / "projects"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Derive a token/cost ledger from Claude Code session JSONLs.")
    ap.add_argument("--since", metavar="YYYY-MM-DD",
                    help="only count messages on/after this date (UTC)")
    ap.add_argument("--by", choices=sorted(DIMS), default="day",
                    help="aggregation dimension (default: day)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    ap.add_argument("--write", action="store_true",
                    help="also write exchange/token-ledger-<date>.md")
    ap.add_argument("--self-test", action="store_true",
                    help="run the fixture self-test and exit")
    ap.add_argument("--root", default=None,
                    help="override the projects root (default: ~/.claude/projects)")
    ap.add_argument("--ceiling-from-meter", type=float, metavar="PCT", default=None,
                    help="derive the implied weekly ceiling from a /usage meter "
                         "percentage that Jon supplies (this tool cannot read it)")
    ap.add_argument("--record-meter", action="store_true",
                    help="persist the meter reading to exchange/"
                         + OBSERVATIONS_FILENAME + " so a later reading cross-checks it")
    ap.add_argument("--week-start", metavar="YYYY-MM-DD", default=None,
                    help="week boundary for the ceiling calc (default: most recent Monday)")
    ap.add_argument("--reset-at", metavar="ISO8601", default=None,
                    help="the reset time the /usage panel STATES (e.g. "
                         "2026-08-07T13:59:00-05:00). Window = reset - 7d. "
                         "Preferred over --week-start: the real boundary is "
                         "mid-afternoon, not midnight Monday.")
    ap.add_argument("--as-of", metavar="ISO8601", default=None,
                    help="treat the meter as having been read at this instant; "
                         "truncates the window there. Lets a past reading be "
                         "back-filled and re-derived reproducibly.")
    ap.add_argument("--meter-grade", choices=["panel", "recall"], default="panel",
                    help="evidence grade of the meter reading (default: panel). "
                         "'recall' readings are recorded but excluded from cross-checks.")
    ap.add_argument("--reconcile-panel", action="store_true",
                    help="recompute the stored /usage panel session and compare "
                         "(external control; exits 3 on disagreement)")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.since:
        try:
            datetime.strptime(args.since, "%Y-%m-%d")
        except ValueError:
            print(f"error: --since must be YYYY-MM-DD, got {args.since!r}", file=sys.stderr)
            return 1

    root = pathlib.Path(args.root) if args.root else default_root()
    files, recs, stats = scan(root, args.since)

    # Never a silent pass.
    if stats["files_scanned"] == 0:
        print(f"ERROR: zero JSONL files scanned under {root}", file=sys.stderr)
        print("The ledger measured nothing. This is a failure, not an empty result.",
              file=sys.stderr)
        return 2

    # --- weekly ceiling derivation (optional) ---
    ceiling_text = ""
    ceiling_payload = None
    if args.ceiling_from_meter is not None:
        pct = args.ceiling_from_meter
        if not (0 < pct <= 100):
            print(f"error: --ceiling-from-meter must be in (0, 100], got {pct}",
                  file=sys.stderr)
            return 1
        window = None
        if args.reset_at:
            try:
                window = window_from_reset(args.reset_at)
            except ValueError as e:
                print(f"error: {e}", file=sys.stderr)
                return 1
            wk_start = window[0].date().isoformat()
        else:
            wk_start = args.week_start or default_week_start()
            try:
                datetime.strptime(wk_start, "%Y-%m-%d")
            except ValueError:
                print(f"error: --week-start must be YYYY-MM-DD, got {wk_start!r}",
                      file=sys.stderr)
                return 1

        as_of = None
        if args.as_of:
            as_of = parse_ts(args.as_of)
            if as_of is None:
                print(f"error: --as-of must be ISO8601, got {args.as_of!r}", file=sys.stderr)
                return 1

        wb = week_bases(recs, wk_start, window, as_of)
        obs_path = observations_path()
        observations = load_observations(obs_path)

        if args.record_meter:
            entry = {
                "recorded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "week_start": wk_start,
                "window_start": window[0].isoformat() if window else None,
                "window_end": window[1].isoformat() if window else None,
                "read_at": as_of.isoformat() if as_of else None,
                "pct": pct,
                "grade": args.meter_grade,
                "bases": {k: wb[k] for k, _ in CEILING_BASES},
                "cost_usd": round(wb["cost_usd"], 4),
                "messages": wb["messages"],
                "note": "meter pct supplied by Jon; /usage is not agent-readable",
            }
            observations = observations + [entry]
            obs_path.parent.mkdir(parents=True, exist_ok=True)
            obs_path.write_text(json.dumps(
                {"_comment": "Claude Code /usage meter readings, supplied by Jon. "
                             "Used to derive the weekly ceiling, which is not "
                             "otherwise recorded anywhere in this repo.",
                 "observations": observations}, indent=2), encoding="utf-8")
            print(f"[recorded] {obs_path}", file=sys.stderr)

        ceiling_text = render_ceiling(pct, wk_start, wb, observations, window)
        ceiling_payload = {
            "meter_pct": pct, "week_start": wk_start,
            "window_start": window[0].isoformat() if window else None,
            "window_end": window[1].isoformat() if window else None,
            "window_derived_from_stated_reset": window is not None,
            "week_start_is_assumption": args.week_start is None and window is None,
            "meter_unit_known": False,
            "week_bases": wb,
            "implied_ceilings": {k: (wb[k] / (pct / 100.0)) for k, _ in CEILING_BASES},
            "recorded_observations": len(
                [o for o in observations if o.get("week_start") == wk_start]),
        }

    recon_text, recon_ok = ("", True)
    if args.reconcile_panel:
        recon_text, recon_ok = reconcile_panel(root)

    if args.json:
        payload = build_json(files, recs, stats, args.by, args.since, root)
        if ceiling_payload:
            payload["weekly_ceiling"] = ceiling_payload
        if args.reconcile_panel:
            payload["panel_reconciliation_passed"] = recon_ok
        out = json.dumps(payload, indent=2, sort_keys=True)
    else:
        out = render(files, recs, stats, args.by, args.since, root)
        for extra in (ceiling_text, recon_text):
            if extra:
                out = out.rstrip("=\n") + "\n" + extra + "\n" + "=" * 78
    print(out)

    if args.write:
        repo = pathlib.Path(__file__).resolve().parents[2]
        dest_dir = repo / "exchange"
        dest_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        dest = dest_dir / f"token-ledger-{stamp}.md"
        body = render(files, recs, stats, args.by, args.since, root)
        for extra in (ceiling_text, recon_text):
            if extra:
                body = body.rstrip("=\n") + "\n" + extra + "\n" + "=" * 78
        dest.write_text(
            f"# Token / cost ledger - {stamp}\n\n"
            f"Generated by `scripts/audit/token_ledger.py "
            f"--by {args.by}{' --since ' + args.since if args.since else ''}`.\n\n"
            f"```\n{body}\n```\n", encoding="utf-8")
        print(f"\n[written] {dest}", file=sys.stderr)

    if args.reconcile_panel and not recon_ok:
        print("ERROR: ledger disagrees with Claude Code's own /usage panel.",
              file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
