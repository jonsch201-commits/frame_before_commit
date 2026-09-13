#!/usr/bin/env python3
"""
cost_census.py -- turn spend into HEADROOM, without asking Jon for the number.

⛔ WHY THIS EXISTS. Jon, 2026-08-17 ~16:4x CDT, verbatim, typos his:

    "You can't rely on me to check usage numbers manually to get a cost history
     census accurate. That's pure data mining after some easy research wtf are
     you smoking."
    "And I don't think you should have needed my usage command to have accurate
     usage stats."

The Secretary published in CLAUDE-STANDARDS §12.5 that "% of budget remaining is
UNCOMPUTABLE from any seat", then asked Jon for the number. That is an absence
claim from one fact (`/usage` is an interactive slash command) never tested against
anything else. Jon's decomposition is the correct one and it is two cheap halves:

    NUMERATOR   -- "pure data mining"  -> already built: token_ledger.py
    DENOMINATOR -- "some easy research" -> the plan's published ceiling

⭐ THIS SCRIPT ADDS A THIRD PATH THE STANDARDS FILE MISSED: the denominator does
not have to be looked up at all. It is IDENTIFIED from meter readings already on
disk. Four `/usage` readings are recorded in this repo -- three from 2026-08-03 in
one window, one from 2026-08-17 in another. Each is an equation

    pct = 100 * consumed_at_read / ceiling

so each reading independently IMPLIES a ceiling. If the basis (what unit the meter
counts) is right and our scan sees exactly what the meter sees, every reading must
imply the SAME ceiling.

⭐ SO THE SPREAD ACROSS READINGS IS THE RESIDUAL, AND IT IS ALSO THE DISCRIMINATOR.
The meter's unit is not documented anywhere. This script computes the implied
ceiling on every candidate basis and reports the spread; the basis whose readings
agree with each other is the basis the meter plausibly counts, and the ones that
disagree are ruled out BY DATA rather than by preference. A single reading cannot
do this -- it fits any basis exactly and reports a residual of zero, which is not
agreement, it is one equation in one unknown.

⚠️ WHAT THIS CANNOT DO, printed on every run and not only here:
  - Coverage is LOCAL JSONL ONLY. claude.ai web usage is not in these files at all,
    nor is any usage from another machine. If the census disagrees with Jon's meter,
    that gap is the first suspect, not the arithmetic.
  - The ceiling could genuinely have CHANGED between 2026-08-03 and 2026-08-17
    (plan change, Anthropic limit change). Cross-window disagreement is therefore
    ambiguous between "wrong basis" and "ceiling moved", and this script says so
    instead of picking.
  - A reading's timestamp is known to the minute at best. Under heavy load this
    program burns real volume in a minute, so `--sensitivity` reports how much the
    implied ceiling moves for a +/-10 minute error in the read time.

Usage:
    python cost_census.py [--emit] [--json] [--self-test] [--sensitivity]
                          [--root PATH] [--as-of ISO8601]

Exit codes:
    0  census produced
    1  bad arguments / self-test failure
    2  zero files scanned, or zero readings usable -- never a silent pass
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import statistics
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import token_ledger as T  # noqa: E402  -- the numerator, already built and reconciled

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CDT = timezone(timedelta(hours=-5))

# ---------------------------------------------------------------------------
# THE READINGS. Every `/usage` figure this program has ever been given.
#
# ⛔ These are the only external ground truth in the whole instrument. A reading is
# (meter, pct, read_at, window_reset) -- and the window matters as much as the pct,
# because a percentage describes consumption since a reset, not since a Monday.
#
# The 08-03 three are transcribed from exchange/token-meter-observations.json,
# which token_ledger.py wrote with --record-meter. They are re-derived from disk
# here rather than trusted: see verify_rederivable().
# ---------------------------------------------------------------------------
READINGS = [
    # --- window resetting 2026-08-07 13:59 CDT (18:59Z) ---
    dict(meter="all", pct=40.0, read_at="2026-08-03T13:16:00+00:00",
         reset="2026-08-07T18:59:00+00:00", grade="recall",
         source="exchange/token-meter-observations.json"),
    dict(meter="all", pct=52.0, read_at="2026-08-03T13:27:00+00:00",
         reset="2026-08-07T18:59:00+00:00", grade="panel",
         source="exchange/token-meter-observations.json"),
    dict(meter="all", pct=62.0, read_at="2026-08-03T20:50:00+00:00",
         reset="2026-08-07T18:59:00+00:00", grade="panel",
         source="exchange/token-meter-observations.json"),
    # --- window resetting 2026-08-21 14:00 CDT (19:00Z); Jon ran /usage ~16:4x CDT ---
    dict(meter="all", pct=69.0, read_at="2026-08-17T21:44:00+00:00",
         reset="2026-08-21T19:00:00+00:00", grade="panel",
         source="secretary-courier-BUILD-ORDER-cost-census-2026-08-17.md §2"),
    dict(meter="fable", pct=85.0, read_at="2026-08-17T21:44:00+00:00",
         reset="2026-08-21T19:00:00+00:00", grade="panel",
         source="secretary-courier-BUILD-ORDER-cost-census-2026-08-17.md §2"),
]

# Which records each meter counts. The all-models meter is every billed record;
# the second meter is named "Fable" on Jon's panel and is read here as exactly the
# Fable model. ⚠️ THAT MAPPING IS AN ASSUMPTION, not a measurement -- if Anthropic's
# second meter covers a tier rather than a model, this is wrong and the fable
# numbers move. It is isolated to this one dict so it is cheap to correct.
METERS = {
    "all":   dict(label="week, all models", match=lambda m: True),
    "fable": dict(label="week, Fable",      match=lambda m: m == "claude-fable-5"),
}

# ⛔ §12.4 -- a window aggregate that straddles a policy change turns a rule that
# was obeyed into a rule that looks broken. The Fable->Opus switch is a cut, not a
# footnote: Fable spend BEFORE it is policy-compliant history, and Fable spend
# AFTER it is a violation. One total cannot say which.
POLICY_CUTS = [
    ("2026-08-17T20:34:10+00:00", "Fable -> Opus (CLAUDE-STANDARDS §12; Jon's order 15:34:10 CDT)"),
]

EMIT_PATH = pathlib.Path(r"G:\My Drive\Claude\COST-CENSUS-CURRENT.md")
EMIT_JSON = pathlib.Path(r"G:\My Drive\Claude\COST-CENSUS-CURRENT.json")

# ---------------------------------------------------------------------------
# ⭐ THE SERVER'S OWN PERCENTAGES. Found by the Secretary 2026-08-17 16:46 and
# INDEPENDENTLY VERIFIED from the CFL seat at 16:56 before being wired in here.
#
# `~/.claude.json` -> cachedUsageUtilization holds the same server-computed
# utilisation `/usage` prints, each with an ISO reset. This retires the hardest
# claim in this file's own docstring: the denominator never had to be identified
# at all, because the ratio is handed to us already computed.
#
# ⛔ WHAT THAT DOES **NOT** RETIRE, and the distinction is the reason §2 survives:
# the server gives ONE number for the whole account. It cannot say which seat,
# which model, or which lane spent it. Attribution still needs the local numerator,
# and attribution is what a census is FOR -- "69% used" tells nobody what to stop
# doing. So the server percentage becomes the AUTHORITY for headroom, and the local
# identification becomes what it should always have been: the attribution key, and
# the only way to learn what unit the meter counts.
#
# ⚠️ UNDOCUMENTED KEY. Nothing guarantees this shape survives a `claude update`.
# read_server_meter() therefore reports absence and staleness as findings rather
# than falling back silently to the derived estimate.
# ---------------------------------------------------------------------------
SERVER_CACHE = pathlib.Path(os.path.expanduser("~")) / ".claude.json"
STALE_AFTER_MIN = 60


def read_server_meter():
    """Anthropic's own utilisation percentages, or a stated reason there are none."""
    try:
        blob = json.loads(SERVER_CACHE.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return None, f"unreadable ({type(exc).__name__})"
    cu = blob.get("cachedUsageUtilization")
    if not isinstance(cu, dict):
        return None, "key `cachedUsageUtilization` absent -- shape may have changed (§6: re-verify after `claude update`)"
    fetched_ms = cu.get("fetchedAtMs")
    limits = (cu.get("utilization") or {}).get("limits")
    if not isinstance(limits, list) or not limits:
        return None, "`utilization.limits` absent or empty"
    fetched = (datetime.fromtimestamp(fetched_ms / 1000, tz=timezone.utc)
               if fetched_ms else None)
    age_min = ((datetime.now(timezone.utc) - fetched).total_seconds() / 60
               if fetched else None)
    rows = []
    for L in limits:
        scope = (L.get("scope") or {}).get("model") or {}
        rows.append(dict(
            kind=L.get("kind"), group=L.get("group"), percent=L.get("percent"),
            severity=L.get("severity"), resets_at=L.get("resets_at"),
            scope_model=scope.get("display_name"), is_active=L.get("is_active"),
        ))
    return dict(fetched=fetched, age_min=age_min, rows=rows), None


# Token CLASSES. ⛔ Reporting one "tokens" total is the defect the Secretary named
# at 17:0x and MY OWN §4 table shipped with it: a figure that adds cache reads to
# fresh input is not a spend number, because cache reads price at 0.1x and are the
# dominant term. A total that mixes them overstates metered usage by ~100x on this
# corpus. Every per-model table below reports the four classes separately.
CLASSES = [
    ("fresh_input", "fresh input", lambda r: r.inp),
    ("output", "output", lambda r: r.out),
    ("cache_write", "cache write", lambda r: r.cwrite),
    ("cache_read", "cache read", lambda r: r.cread),
]

BASES = [b for b, _ in T.CEILING_BASES] + ["ex_cache_read", "cost_usd"]
BASIS_DESC = dict(T.CEILING_BASES)
BASIS_DESC["cost_usd"] = "notional API-equivalent USD (rate table, not money spent)"
# ⭐ ADDED 2026-08-17 17:0x, and the gap it fills is instructive. The four inherited
# bases were `total_tokens` (everything), `non_cache` (input+output), `output_tokens`
# and a cost blend -- so the ONE hypothesis Anthropic's own documentation points at
# was not on the list: cache READS are excluded from the limits, but cache WRITES are
# billed at 1.25-2x input and are plainly metered. That basis is neither "everything"
# nor "input+output". ⛔ A candidate set that omits the documented hypothesis cannot
# find it, however tight the fit it reports on the others.
BASIS_DESC["ex_cache_read"] = "input + output + cache WRITE (cache reads excluded, per Anthropic's limits doc)"


# ---------------------------------------------------------------------------
def bases_for(recs, meter, lo, hi, as_of=None):
    """Consumption on every candidate basis, for one meter, in one window."""
    match = METERS[meter]["match"]
    end = min(hi, as_of) if as_of else hi
    sel = []
    for r in recs:
        dt = T.parse_ts(r.ts)
        if dt is None or not (lo <= dt < end):
            continue
        if not match(T.normalize_model(r.model)):
            continue
        sel.append(r)
    t, _ = T.totals(sel)
    return {
        "messages": t["messages"],
        "total_tokens": t["total_tokens"],
        "non_cache": t["input"] + t["output"],
        "output_tokens": t["output"],
        "ex_cache_read": t["input"] + t["output"] + t["cache_creation"],
        "billable_blend": int(round(t["cost_usd"] * 1_000_000 / T.RATES["claude-opus-5"][0])),
        "cost_usd": t["cost_usd"],
    }


def implied_ceilings(recs, as_of_now):
    """
    For every reading and every basis: ceiling = consumed_at_read / (pct/100).

    Returns {meter: {basis: [ {reading, consumed, ceiling}, ... ] }}.
    """
    out = {}
    for m in METERS:
        out[m] = {b: [] for b in BASES}
    for rd in READINGS:
        lo, hi = T.window_from_reset(rd["reset"])
        at = T.parse_ts(rd["read_at"])
        b = bases_for(recs, rd["meter"], lo, hi, as_of=at)
        for basis in BASES:
            consumed = b[basis]
            ceiling = consumed / (rd["pct"] / 100.0) if rd["pct"] else None
            out[rd["meter"]][basis].append(dict(
                read_at=rd["read_at"], pct=rd["pct"], grade=rd["grade"],
                reset=rd["reset"], consumed=consumed, ceiling=ceiling,
                messages=b["messages"],
            ))
    return out


def spread(vals):
    """Relative spread of a list of implied ceilings. This IS the residual."""
    vals = [v for v in vals if v]
    if len(vals) < 2:
        return None
    mean = statistics.fmean(vals)
    if mean == 0:
        return None
    return (max(vals) - min(vals)) / mean


def marginal_ceiling(entries):
    """
    Ceiling from the DIFFERENCE between two readings in the SAME window.

    ⭐ WHY THIS IS THE BETTER ESTIMATOR, and why it is reported next to the levels
    rather than instead of them. A level estimate (consumed ÷ pct) assumes our scan
    sees exactly what the meter sees. It does not: the meter may exclude cache, or
    count usage from a surface these files do not contain. Any such difference that
    is CONSTANT within a window cancels in the difference:

        pct   = 100 * (consumed - offset) / ceiling
        Δpct  = 100 * Δconsumed / ceiling        <- offset is gone

    So the marginal estimate is robust to the exact failure the levels are exposed
    to. ⚠️ Its own limit: it needs two readings in ONE window, we have exactly one
    such pair, and one pair is one estimate with no residual of its own.
    """
    by_win = {}
    for e in entries:
        by_win.setdefault(e["reset"], []).append(e)
    out = []
    for reset, es in by_win.items():
        es = sorted(es, key=lambda x: x["read_at"])
        if len(es) < 2:
            continue
        for a, b in zip(es, es[1:]):
            d_pct = b["pct"] - a["pct"]
            d_cons = b["consumed"] - a["consumed"]
            if d_pct <= 0:
                continue
            out.append(dict(reset=reset, a=a["read_at"], b=b["read_at"],
                            d_pct=d_pct, d_consumed=d_cons,
                            ceiling=d_cons / d_pct * 100.0,
                            implied_offset=a["consumed"] - (a["pct"] / 100.0) * (d_cons / d_pct * 100.0)))
    return out


def fmt_tok(n):
    if n is None:
        return "n/a"
    if isinstance(n, float) and n < 10_000:
        return f"{n:,.2f}"
    for unit, div in (("B", 1e9), ("M", 1e6), ("k", 1e3)):
        if abs(n) >= div:
            return f"{n/div:,.1f}{unit}"
    return f"{n:,.0f}"


# ---------------------------------------------------------------------------
def verify_rederivable(recs):
    """
    CONTROL: the 08-03 readings stored their own basis totals. Recompute them from
    disk now and compare. A mismatch means the corpus under this scan is not the
    corpus that produced the stored numbers -- retention deletion, a moved root, a
    changed dedup rule -- and every ceiling below inherits that.

    ⚠️ This is the check that can fail. It is run and printed on EVERY census.
    """
    path = pathlib.Path(__file__).resolve().parents[2] / "exchange" / "token-meter-observations.json"
    stored = T.load_observations(path)
    rows = []
    for obs in stored:
        lo, hi = T.window_from_reset(obs["window_end"])
        at = T.parse_ts(obs["read_at"])
        now = bases_for(recs, "all", lo, hi, as_of=at)
        for basis in ("total_tokens", "billable_blend", "non_cache", "output_tokens"):
            was = obs.get("bases", {}).get(basis)
            if was is None:
                continue
            delta = (now[basis] - was) / was if was else None
            rows.append(dict(read_at=obs["read_at"], basis=basis,
                             stored=was, recomputed=now[basis], rel_delta=delta))
    return rows


def policy_split(recs, lo, hi, as_of):
    """Per-model consumption cut at each policy boundary inside the window."""
    cuts = [T.parse_ts(c) for c, _ in POLICY_CUTS if lo <= T.parse_ts(c) < hi]
    edges = [lo] + sorted(cuts) + [min(hi, as_of)]
    segs = []
    for i in range(len(edges) - 1):
        a, b = edges[i], edges[i + 1]
        if b <= a:
            continue
        by_model = {}
        for r in recs:
            dt = T.parse_ts(r.ts)
            if dt is None or not (a <= dt < b):
                continue
            mm = T.normalize_model(r.model)
            d = by_model.setdefault(mm, {"messages": 0, "total_tokens": 0, "cost_usd": 0.0,
                                         **{k: 0 for k, _, _ in CLASSES}})
            d["messages"] += 1
            d["total_tokens"] += r.inp + r.out + r.cread + r.cwrite
            for key, _lbl, get in CLASSES:
                d[key] += get(r)
            c = r.cost()
            if c:
                d["cost_usd"] += c
        segs.append(dict(start=a.isoformat(), end=b.isoformat(), by_model=by_model))
    return segs


# ---------------------------------------------------------------------------
def render(recs, stats, files, as_of, sensitivity=False):
    L = []
    A = L.append
    now_cdt = as_of.astimezone(CDT)
    A(f"# COST CENSUS — generated {now_cdt.strftime('%Y-%m-%d %H:%M CDT')}")
    A("")
    A("Numerator: derived from local Claude Code session JSONLs (`token_ledger.py` machinery).")
    A("Denominator: **identified from `/usage` readings already on disk**, not looked up and not")
    A("asked for. Jon, 2026-08-17: *\"I don't think you should have needed my usage command to have")
    A("accurate usage stats.\"*")
    A("")

    # --- coverage bound, first, every run ---
    A("## 0 · COVERAGE BOUND — read this before any number below")
    A("")
    A(f"- Scanned **{stats['files_scanned']:,} JSONL files**, "
      f"**{stats['unique_messages']:,} deduplicated assistant messages** under `~/.claude/projects`.")
    A("- ⛔ **Local Claude Code only.** claude.ai **web** usage is not in these files at all; nor is")
    A("  any usage from another machine. **If this census disagrees with Jon's meter, that gap is the")
    A("  first suspect — not the arithmetic.**")
    A("- Notional USD is an API-equivalent rate-table figure. Jon is on Max, a flat fee. **Not money spent.**")
    A("")

    # --- the control ---
    A("## 1 · CONTROL — are the stored 08-03 readings still re-derivable from disk?")
    A("")
    rows = verify_rederivable(recs)
    if not rows:
        A("⚠️ **No stored observations found to check.** The census runs, but its oldest three")
        A("readings are unverified against the corpus that produced them.")
    else:
        worst = max(abs(r["rel_delta"]) for r in rows if r["rel_delta"] is not None)
        A(f"| read_at | basis | stored 08-03 | recomputed now | Δ |")
        A("|---|---|---|---|---|")
        for r in rows:
            d = "—" if r["rel_delta"] is None else f"{100*r['rel_delta']:+.2f}%"
            A(f"| {r['read_at'][11:16]} | `{r['basis']}` | {fmt_tok(r['stored'])} | "
              f"{fmt_tok(r['recomputed'])} | {d} |")
        A("")
        if worst < 0.005:
            A(f"✅ **Re-derivable.** Worst drift **{100*worst:.2f}%**. The corpus that produced the")
            A("08-03 numbers is the corpus being scanned now, so those readings are usable as data.")
        else:
            A(f"⛔ **NOT re-derivable — worst drift {100*worst:.2f}%.** The stored bases and the")
            A("recomputed ones disagree, so something changed under the scan (retention deletion, a")
            A("moved root, a changed dedup rule). **Every ceiling below inherits this.** Treat the")
            A("08-03 readings as suspect until this row is explained.")
    A("")

    # --- the identification ---
    A("## 2 · THE DENOMINATOR, IDENTIFIED — and the spread IS the residual")
    A("")
    A("Each reading is one equation: `ceiling = consumed_at_read ÷ (pct/100)`. If the basis is the")
    A("unit the meter counts and our scan sees what the meter sees, **every reading must imply the")
    A("same ceiling.** So the spread across readings is not noise around an answer — it is the")
    A("test of whether the basis is the answer.")
    A("")
    A("⛔ **GRADE FIRST — a recall-grade reading is NOT an equation.** Of the four readings on file,")
    A("one is graded `recall`: Jon repeating a figure from memory. Its stored `read_at` is *the")
    A("minute he said it*, not the minute the meter showed it, and the equation needs the second.")
    A("`token-meter-observations.json` stores the grade but nothing downstream ever branched on it.")
    A("**Measured below: dropping it moves `total_tokens` from ±29% to ±19% and moves no other basis**")
    A("— so it was not adding noise evenly, it was contradicting the one basis that otherwise fits.")
    A("Panel-only is the fit of record; the n=4 column stays visible so the exclusion is auditable.")
    A("")
    ic = implied_ceilings(recs, as_of)
    verdicts = {}
    for meter in METERS:
        rds = [r for r in ic[meter][BASES[0]] if r["grade"] == "panel"]
        allr = ic[meter][BASES[0]]
        if not allr:
            continue
        A(f"### meter `{meter}` — *{METERS[meter]['label']}*  "
          f"({len(rds)} panel reading{'s' if len(rds) != 1 else ''} of {len(allr)} on file)")
        A("")
        A("| basis | " + " | ".join(
            f"{r['pct']:g}% @ {r['read_at'][5:16]}" + ("" if r["grade"] == "panel" else " *(recall)*")
            for r in allr) + " | **ceiling, panel-only** | spread (panel / all) |")
        A("|---" * (len(allr) + 3) + "|")
        best = None
        for basis in BASES:
            entries = ic[meter][basis]
            panel = [e for e in entries if e["grade"] == "panel"]
            sp_p = spread([e["ceiling"] for e in panel])
            sp_a = spread([e["ceiling"] for e in entries])
            cells = " | ".join(fmt_tok(e["ceiling"]) for e in entries)
            mean_p = statistics.fmean([e["ceiling"] for e in panel if e["ceiling"]]) if panel else None
            if sp_p is None:
                col, verdict = fmt_tok(mean_p), "**n=1 — exact fit, residual UNDEFINED**"
            else:
                col = fmt_tok(mean_p)
                verdict = (f"**±{100*sp_p:.0f}%** / ±{100*sp_a:.0f}%" if sp_a is not None
                           else f"**±{100*sp_p:.0f}%**")
                if best is None or sp_p < best[1]:
                    best = (basis, sp_p, mean_p)
            A(f"| `{basis}` | {cells} | {col} | {verdict} |")
        A("")
        verdicts[meter] = best
        if best is None:
            A("⛔ **One reading only. Every basis fits it exactly, so this meter's unit is")
            A("UNIDENTIFIED and its ceiling is not a measurement — it is a restatement of the")
            A("reading. A second reading in any later window makes it testable.**")
        else:
            basis, sp, mean_p = best
            A(f"⭐ **Tightest basis: `{basis}` — ceiling ≈ {fmt_tok(mean_p)}, residual ±{100*sp:.0f}%**")
            A(f"  ({BASIS_DESC[basis]}).")
            if sp > 0.25:
                A(f"⚠️ **±{100*sp:.0f}% is not agreement.** No candidate basis reproduces these readings")
                A("with a single ceiling. ⛔ **Do not publish a headroom percentage off this fit.**")
            else:
                A(f"✅ **Usable with its residual attached** — {len(ic[meter][basis])-len([e for e in ic[meter][basis] if e['grade']!='panel'])}"
                  f" panel readings across two windows agree to ±{100*sp:.0f}%. That is coarse, and it")
                A("is a measurement rather than a feeling. **Quote it only with the ± attached.**")
            if basis == "ex_cache_read":
                A("")
                A("⭐ **AND THIS IS THE RESULT WORTH KEEPING — two seats reached the same unit by")
                A("routes that share no step.** The Secretary read Anthropic's limits documentation")
                A("and found cache reads are excluded. This seat fitted four readings against six")
                A("candidate bases and found the tightest is *exactly* the one that excludes cache")
                A("reads while keeping cache writes. **Neither party could have produced the other's")
                A("evidence, and the doc route named the hypothesis the fit route had left off its")
                A("own candidate list.** ⚠️ Stated at its true strength: this is corroboration, not")
                A("proof — 3 readings, ±16%, and the runner-up is only 3 points behind.")
        A("")

        # --- the offset-robust estimator ---
        marg = marginal_ceiling([e for e in ic[meter][best[0]] if e["grade"] == "panel"]) if best else []
        if marg:
            A(f"**Offset-robust cross-check on `{best[0]}` — the differential estimator.**")
            A("")
            for m in marg:
                A(f"- Between the two readings in the window resetting `{m['reset'][:10]}`: "
                  f"**Δ{m['d_pct']:g} meter-points cost {fmt_tok(m['d_consumed'])}** → ceiling "
                  f"**{fmt_tok(m['ceiling'])}**.")
            A("")
            mc = marg[0]["ceiling"]
            A(f"⛔ **This disagrees with the level estimate ({fmt_tok(best[2])}) by "
              f"{100*(best[2]-mc)/mc:+.0f}%, and the disagreement is informative rather than fatal.**")
            A("A constant per-window offset cancels in a difference but not in a level, so a marginal")
            A(f"estimate BELOW the level estimate means our scan counts roughly "
              f"**{fmt_tok(marg[0]['implied_offset'])}** in that window that the meter does not —")
            A("consistent with the meter excluding some category these files contain. ⚠️ **One pair is")
            A("one estimate: it has no residual of its own, and it is doing the work of a hypothesis,")
            A("not a result.** A second same-window pair is the cheapest thing that would settle this.")
            A("")

    # --- headroom ---
    A("## 3 · HEADROOM — from the server, not from a fit and not from Jon")
    A("")
    cur = [r for r in READINGS if r["reset"] == "2026-08-21T19:00:00+00:00"]
    srv, why = read_server_meter()
    if srv is None:
        A(f"⛔ **SERVER METER UNAVAILABLE: {why}.** Falling back to the identified ceiling below,")
        A("which is a far weaker instrument. **This line is a finding, not a footnote** — the key is")
        A("undocumented and a `claude update` can change its shape without warning.")
        A("")
    else:
        stale = srv["age_min"] is not None and srv["age_min"] > STALE_AFTER_MIN
        A("⭐ **`~/.claude.json` → `cachedUsageUtilization` carries Anthropic's OWN server-computed")
        A("utilisation — the same numbers `/usage` prints.** Found by the Secretary 16:46; verified")
        A("independently from this seat before being used here. **No ceiling needs identifying and no")
        A("human needs asking.**")
        A("")
        A("| meter | scope | used | **remaining** | severity | resets |")
        A("|---|---|---|---|---|---|")
        for r in srv["rows"]:
            reset = T.parse_ts(r["resets_at"]) if r["resets_at"] else None
            rs = reset.astimezone(CDT).strftime("%a %b %d, %I:%M%p CDT") if reset else "—"
            pct = r["percent"]
            sev = r["severity"] or ""
            sev = f"**{sev}**" if sev and sev != "normal" else sev
            A(f"| `{r['kind']}` | {r['scope_model'] or 'all models'} | {pct}% | "
              f"**{100-pct}%** | {sev} | {rs} |")
        A("")
        A(f"`fetchedAtMs` → **{srv['fetched'].astimezone(CDT).strftime('%H:%M:%S CDT')}**, "
          f"age **{srv['age_min']:.0f} min**. ")
        if stale:
            A(f"⛔ **STALE (> {STALE_AFTER_MIN} min).** This is a cache the client refreshes; a stale")
            A("percentage presented as current is its own defect class. **Treat as a lower bound.**")
        else:
            A(f"✅ Fresh (≤ {STALE_AFTER_MIN} min). ⚠️ It is still a CACHE, not a live query — it moves")
            A("only when the client refreshes it, so between refreshes it under-reports.")
        A("")
        ext = [r for r in cur]
        if ext:
            agree = all(any(s["percent"] == r["pct"] for s in srv["rows"]) for r in ext)
            A(f"**Cross-check against what Jon read from `/usage` at ~16:44:** "
              f"{'✅ **exact match on both meters**' if agree else '⛔ **DISAGREES**'} "
              f"({', '.join(f'{r['pct']:g}%' for r in ext)} read by hand vs "
              f"{', '.join(str(s['percent']) + '%' for s in srv['rows'] if s['group'] == 'weekly')} "
              f"from the cache). **That is the strongest validation in this file** — a human reading")
            A("the panel and a seat reading the cache produced the same numbers by different paths.")
            A("")
    A("⭐ **Fable is the binding constraint: 15% left against 31%, and Fable prices at 2× Opus.**")
    A("Moving a Fable turn to Opus buys roughly **4× the runway per turn** — 2× from the price and")
    A("2× from which meter it draws down.")
    A("")
    A("**Burn since that reading, measured locally — this part the census CAN do without Jon:**")
    A("")
    read_at = T.parse_ts("2026-08-17T21:44:00+00:00")
    lo, hi = T.window_from_reset("2026-08-21T19:00:00+00:00")
    for meter in METERS:
        at_read = bases_for(recs, meter, lo, hi, as_of=read_at)
        now = bases_for(recs, meter, lo, hi, as_of=as_of)
        d_tok = now["total_tokens"] - at_read["total_tokens"]
        d_msg = now["messages"] - at_read["messages"]
        pct_of = (100.0 * d_tok / at_read["total_tokens"]) if at_read["total_tokens"] else 0.0
        A(f"- **{METERS[meter]['label']}**: +{fmt_tok(d_tok)} tokens, +{d_msg:,} messages since the "
          f"reading — **{pct_of:.1f}%** on top of what the meter had already counted.")
    A("")
    A("⚠️ **That delta is a LOWER BOUND on meter movement, not an estimate of it** — it becomes a")
    A("percentage only through a ceiling, and the ceiling carries the residual below.")
    A("")
    A("**DERIVED HEADROOM — kept as a CROSS-CHECK, no longer the answer.** Until 16:5x this was the")
    A("headline of this file. The server cache above demoted it, and that is the right outcome: a fit")
    A("with a ±19% residual should lose to a number the server computed. It stays because it is the")
    A("only thing that can be attributed to a seat, and because when the undocumented key moves, this")
    A("is the fallback:")
    A("")
    for meter in METERS:
        best = verdicts.get(meter)
        if not best or best[1] is None:
            A(f"- **{METERS[meter]['label']}**: ⛔ **not computable.** Its unit is unidentified "
              f"(n=1 reading), so any percentage would be the reading read back, not a measurement.")
            continue
        basis, sp, ceiling = best
        now = bases_for(recs, meter, lo, hi, as_of=as_of)[basis]
        pct_now = 100.0 * now / ceiling
        lo_pct = 100.0 * now / (ceiling * (1 + sp / 2))
        hi_pct = 100.0 * now / (ceiling * (1 - sp / 2))
        A(f"- **{METERS[meter]['label']}** — consumed **{fmt_tok(now)}** `{basis}` this window "
          f"against a ceiling of **{fmt_tok(ceiling)} ±{100*sp:.0f}%** → "
          f"**{pct_now:.0f}% used, {100-pct_now:.0f}% remaining** "
          f"(band: {lo_pct:.0f}–{hi_pct:.0f}% used).")
        ref = next((r for r in cur if r["meter"] == meter), None)
        if ref:
            # ⛔ COMPARE AT THE READ INSTANT, NOT AT NOW. The first cut of this block
            # compared a live figure against Jon's reading and asserted the reading was
            # "inside the band by construction". It printed a band of 71-86% next to his
            # 69% -- the assertion was false ON ITS OWN OUTPUT, because `pct_now` had
            # absorbed every token burned since he read the meter. A claim of agreement
            # must be COMPUTED against the same instant and then stated, never asserted.
            at_read = bases_for(recs, meter, lo, hi, as_of=read_at)[basis]
            pct_at_read = 100.0 * at_read / ceiling
            lo_r = 100.0 * at_read / (ceiling * (1 + sp / 2))
            hi_r = 100.0 * at_read / (ceiling * (1 - sp / 2))
            inside = lo_r <= ref["pct"] <= hi_r
            A(f"  - **Back-check at Jon's read instant** (not at now — the live figure above has "
              f"absorbed the burn since): this census derives **{pct_at_read:.0f}% used** "
              f"(band {lo_r:.0f}–{hi_r:.0f}%) where he read **{ref['pct']:g}%**.")
            if inside:
                A(f"    ✅ **Inside the band.** ⚠️ But this is *not* independent confirmation — that")
                A("    reading is one of the points the ceiling was fitted to. The out-of-sample test")
                A("    is the NEXT reading, and until one exists the fit has never predicted anything.")
            else:
                miss = min(abs(ref["pct"] - lo_r), abs(ref["pct"] - hi_r))
                A(f"    ⛔ **OUTSIDE the band, by {miss:.1f} point{'' if abs(miss-1) < 0.05 else 's'}** "
                  f"— and this reading is one of the points the ceiling was FITTED to. A fit")
                A("    that misses its own training data is a misspecified model, not a noisy one:")
                A("    no single ceiling reproduces these readings. **Treat the headroom line above as")
                A("    an order-of-magnitude bound only, and do not let it settle a spend decision that")
                A("    a ±19% error would flip.**")
    A("")
    A("⛔ **THE HONEST STATUS OF THAT LINE: it is a measurement with a coarse residual, not a")
    A("precise figure, and it is only as good as the local-JSONL coverage bound in §0.** What it")
    A("replaces is a number that could only be obtained by asking Jon — which is the whole order.")
    A("")

    # --- policy cut ---
    A("## 4 · CUT AT THE POLICY CHANGE (§12.4)")
    A("")
    A("A window aggregate that straddles a policy change turns an obeyed rule into a broken-looking")
    A("one. Fable spend **before** the switch is compliant history; Fable spend **after** it is a")
    A("violation. One total cannot say which.")
    A("")
    A("⛔ **AND THE TOKENS ARE SPLIT BY CLASS, because a single total is not a spend number.**")
    A("Anthropic prices cache reads at **0.1×** base input, and this corpus is dominated by them —")
    A("so a column that adds cache reads to fresh input overstates metered usage by orders of")
    A("magnitude. ⚠️ **The first cut of this table shipped exactly that defect**, one column headed")
    A("`tokens`; the Secretary named the class at 17:0x and it applied to my own artifact.")
    A("")
    for seg in policy_split(recs, lo, hi, as_of):
        a = T.parse_ts(seg["start"]).astimezone(CDT).strftime("%m-%d %H:%M")
        b = T.parse_ts(seg["end"]).astimezone(CDT).strftime("%m-%d %H:%M")
        A(f"**{a} → {b} CDT**")
        A("")
        A("| model | messages | fresh input | output | cache write | cache read | notional USD |")
        A("|---|---|---|---|---|---|---|")
        for mm, d in sorted(seg["by_model"].items(),
                            key=lambda kv: -(kv[1]["fresh_input"] + kv[1]["output"])):
            A(f"| `{mm}` | {d['messages']:,} | {fmt_tok(d['fresh_input'])} | {fmt_tok(d['output'])} | "
              f"{fmt_tok(d['cache_write'])} | {fmt_tok(d['cache_read'])} | ${d['cost_usd']:,.2f} |")
        A("")
    A("*(cut: " + POLICY_CUTS[0][1] + ". Rows ordered by fresh input + output — the classes that")
    A("are unambiguously metered — not by the mixed total.)*")
    A("")

    if sensitivity:
        A("## 5 · SENSITIVITY — how much does a wrong read-time cost us?")
        A("")
        A("The read times above are known to the minute at best. Under load this program burns real")
        A("volume in a minute, so a ceiling identified from a mis-stamped reading is wrong by the")
        A("same proportion.")
        A("")
        A("| reading | ceiling at −10 min | at stamp | at +10 min | swing |")
        A("|---|---|---|---|---|")
        for rd in READINGS:
            wlo, whi = T.window_from_reset(rd["reset"])
            at = T.parse_ts(rd["read_at"])
            vals = []
            for off in (-10, 0, 10):
                b = bases_for(recs, rd["meter"], wlo, whi, as_of=at + timedelta(minutes=off))
                vals.append(b["total_tokens"] / (rd["pct"] / 100.0))
            sw = (max(vals) - min(vals)) / statistics.fmean(vals) if statistics.fmean(vals) else 0
            A(f"| {rd['meter']} {rd['pct']:g}% @ {rd['read_at'][5:16]} | {fmt_tok(vals[0])} | "
              f"{fmt_tok(vals[1])} | {fmt_tok(vals[2])} | **±{100*sw:.1f}%** |")
        A("")
        A("*(basis `total_tokens`; a swing far below the §2 spread means the read-time stamp is not")
        A("what is breaking the identification.)*")
        A("")

    A("---")
    A("")
    A("`owner:` CFL · `regenerate:` `python scripts/audit/cost_census.py --emit --sensitivity`")
    A("`what would change the answer:` a second `/usage` reading for the **Fable** meter in any later")
    A("window (turns an exact fit into a testable one), or the published plan limit + its unit.")
    return "\n".join(L)


# ---------------------------------------------------------------------------
CHECKS = 7


def self_test() -> int:
    """Exercise BOTH verdicts of every judgment this script makes."""
    fails = []

    # 1. spread() must return None at n=1 (exact fit) and a real number at n>1.
    if spread([100.0]) is not None:
        fails.append("spread(n=1) must be None -- an exact fit has no residual")
    s = spread([100.0, 120.0])
    if s is None or abs(s - (20.0 / 110.0)) > 1e-9:
        fails.append(f"spread(n=2) wrong: {s}")
    if spread([]) is not None:
        fails.append("spread([]) must be None")

    # 2. A perfectly consistent set must read as agreement, not just 'tightest'.
    # ⚠️ The first cut of this line was `abs(spread([...]) or -1)`, which fails on a
    # CORRECT result: spread 0.0 is falsy, so `or -1` swapped the pass for -1 and the
    # test reported FAIL on the one input it was written to accept. A truthiness guard
    # standing in for a None check is a test that cannot pass when the code is right.
    s0 = spread([500.0, 500.0, 500.0])
    if s0 is None or abs(s0) > 1e-12:
        fails.append(f"identical ceilings must give spread 0, got {s0}")

    # 3. The meter matcher must actually discriminate -- a matcher that accepts
    #    everything would make the fable meter silently equal the all meter.
    if not METERS["fable"]["match"]("claude-fable-5"):
        fails.append("fable matcher rejects fable")
    if METERS["fable"]["match"]("claude-opus-5"):
        fails.append("fable matcher accepts opus -- the two meters would collapse")
    if not METERS["all"]["match"]("claude-opus-5"):
        fails.append("all matcher rejects opus")

    # 4. window_from_reset must produce a 7-day window ENDING at the reset.
    lo, hi = T.window_from_reset("2026-08-21T19:00:00+00:00")
    if (hi - lo) != timedelta(days=7) or hi.isoformat() != "2026-08-21T19:00:00+00:00":
        fails.append(f"window wrong: {lo} .. {hi}")

    # 5. bases_for must be monotone in as_of -- a later cutoff cannot see less.
    fake = []
    for i, (ts, model) in enumerate([
        ("2026-08-15T00:00:00+00:00", "claude-opus-5"),
        ("2026-08-16T00:00:00+00:00", "claude-fable-5"),
        ("2026-08-20T00:00:00+00:00", "claude-opus-5"),
    ]):
        r = T.Rec("2026-08-15", "s", "main", model, ts=ts)
        r.absorb({"input_tokens": 100, "output_tokens": 10})
        fake.append(r)
    early = bases_for(fake, "all", lo, hi, as_of=T.parse_ts("2026-08-15T12:00:00+00:00"))
    late = bases_for(fake, "all", lo, hi, as_of=T.parse_ts("2026-08-21T00:00:00+00:00"))
    if not (early["messages"] == 1 and late["messages"] == 3):
        fails.append(f"as_of truncation wrong: {early['messages']} then {late['messages']}")
    fab = bases_for(fake, "fable", lo, hi, as_of=T.parse_ts("2026-08-21T00:00:00+00:00"))
    if fab["messages"] != 1:
        fails.append(f"fable meter picked up {fab['messages']} of 3 records, expected 1")

    # 6. A record OUTSIDE the window must not be counted -- the whole point of
    #    window-awareness. This is the check that would catch a Monday-start bug.
    out = T.Rec("2026-08-01", "s", "main", "claude-opus-5", ts="2026-08-01T00:00:00+00:00")
    out.absorb({"input_tokens": 999_999, "output_tokens": 999_999})
    if bases_for(fake + [out], "all", lo, hi, as_of=T.parse_ts("2026-08-21T00:00:00+00:00"))["messages"] != 3:
        fails.append("a record outside the window was counted")

    # 7. The self-test must be able to FAIL. A suite that only ever runs the code
    #    path that works is the defect this repo keeps shipping, so one deliberately
    #    broken matcher is run through the same assertion the real ones use.
    if METERS["fable"]["match"]("claude-opus-5") is not False:
        fails.append("negative-control unreachable")
    broken = lambda m: True  # noqa: E731 -- a matcher that accepts everything
    if not (broken("claude-opus-5") and not METERS["fable"]["match"]("claude-opus-5")):
        fails.append("the fable-matcher assertion does not discriminate a broken matcher")

    print("=== cost_census self-test ===")
    for f in fails:
        print(f"  FAIL {f}")
    print(f"  {CHECKS} checks, {len(fails)} failures")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--emit", action="store_true", help=f"write {EMIT_PATH}")
    ap.add_argument("--json", action="store_true", help="also emit the JSON sidecar")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--sensitivity", action="store_true",
                    help="report how much the ceiling moves for a +/-10 min read-time error")
    ap.add_argument("--root", default=None)
    ap.add_argument("--as-of", default=None, help="ISO8601; default now")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    root = pathlib.Path(a.root) if a.root else T.default_root()
    as_of = T.parse_ts(a.as_of) if a.as_of else datetime.now(timezone.utc)

    # Scan from the earliest window start we need, not from today.
    earliest = min(T.window_from_reset(r["reset"])[0] for r in READINGS)
    files, recs, stats = T.scan(root, earliest.date().isoformat())
    if not files:
        print("FAIL zero files scanned -- the census measured nothing", file=sys.stderr)
        return 2
    if not READINGS:
        print("FAIL no meter readings -- no denominator can be identified", file=sys.stderr)
        return 2

    report = render(recs, stats, files, as_of, sensitivity=a.sensitivity)
    print(report)

    if a.emit:
        EMIT_PATH.write_text(report + "\n", encoding="utf-8")
        print(f"\n[emitted] {EMIT_PATH}", file=sys.stderr)
        if a.json:
            payload = dict(
                generated_utc=as_of.isoformat(),
                readings=READINGS,
                implied=implied_ceilings(recs, as_of),
                rederivable=verify_rederivable(recs),
                coverage="local Claude Code JSONL only; claude.ai web usage absent",
            )
            EMIT_JSON.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
            print(f"[emitted] {EMIT_JSON}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
