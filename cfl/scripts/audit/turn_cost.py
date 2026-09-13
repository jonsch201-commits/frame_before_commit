#!/usr/bin/env python
"""turn_cost.py — per-turn token/cost instrumentation over Claude Code session JSONLs.

Built 2026-08-21 for Soul's ask 3 (Jon: "i need YOU to get me the informmation i need
to actually review your work in terms of cost and output at the turn-level at a minimum").

Reads the session JSONLs under ~/.claude/projects/<project>/ (READ-ONLY — this script
never writes anything) and emits a per-turn table: turn number, timestamp, model,
output tokens, fresh input tokens, cache-read tokens, cache writes (1h/5m buckets),
and a USD cost estimate.

A "turn" = one prompt-initiating user record (human dispatch, task-notification, or
harness wake — anything that is not a tool_result and not an isMeta injection) plus
every assistant message until the next such record. Assistant usage is deduplicated
by message.id: the harness writes one JSONL record per content block, each carrying
an identical copy of the whole message's usage (verified 2026-08-21: 5,982 assistant
records -> 2,956 unique message ids in session 643640a7; all 3,026 duplicates
byte-identical).

Bounds printed with every run:
  - assistant records missing a usage block (denominator shown)
  - records whose model has no price row (their tokens are listed, cost counted as 0)
  - what the JSONL does NOT record at all (see --help epilog / report notes)
"""

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# PRICE TABLE — USD per 1M tokens.
# Source: Anthropic first-party API pricing as carried by the bundled claude-api
# skill, cache date 2026-06-24 (skill v2.1.239). Cache multipliers per the same
# skill's shared/prompt-caching.md: read = 0.1x input, 5m write = 1.25x input,
# 1h write = 2x input. Sonnet 5 listed at standard rate ($3/$15), NOT the intro
# rate ($2/$10 through 2026-08-31) — flip SONNET5_INTRO below if the intro rate
# applies to this account.
# EDIT HERE AND ONLY HERE when prices change.
# ---------------------------------------------------------------------------
PRICES_AS_OF = "2026-06-24"
SONNET5_INTRO = False
PRICES = {
    # model-id prefix        (input $/M, output $/M)
    "claude-fable-5":   (10.00, 50.00),
    "claude-mythos-5":  (10.00, 50.00),
    "claude-opus-5":    (5.00, 25.00),
    "claude-opus-4-8":  (5.00, 25.00),
    "claude-opus-4-7":  (5.00, 25.00),
    "claude-opus-4-6":  (5.00, 25.00),
    "claude-sonnet-5":  (2.00, 10.00) if SONNET5_INTRO else (3.00, 15.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "<synthetic>":      (0.00, 0.00),  # harness-synthesized records, no API call
}
CACHE_READ_MULT = 0.10
CACHE_5M_MULT = 1.25
CACHE_1H_MULT = 2.00

def _key_for(path):
    """~/.claude/projects sanitises a path by replacing every non-alphanumeric
    CHARACTER (not run) with '-'. Mirrors extract_claude_code_sessions.py's _key_for."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(path)).strip("-")


_PROJECTS_ROOT = os.path.join(os.path.expanduser("~"), ".claude", "projects")
_CODE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ⛔ THIS WAS PINNED TO THE G: KEY, AND THE 2026-09-02 G:->N: MOVE SILENTLY DEMOTED
# IT TO A TRUNK CFL LEFT THREE DAYS AGO -- no error, just a default reading stale
# session data. Fixed the same way extract_claude_code_sessions.py's CFL_DIR_GLOBS
# was: try the CURRENT checkout's DERIVED key first, fall back to the historical G:
# checkout (so an explicit --project-dir-less invocation against an old archive still
# resolves to something that exists) rather than trusting a recorded constant.
_PROJECT_DIR_CANDIDATES = [
    _key_for(_CODE_ROOT),  # DERIVED: wherever this checkout is now (current)
    "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer",  # historical
]


def _default_project_dir():
    for key in _PROJECT_DIR_CANDIDATES:
        d = os.path.join(_PROJECTS_ROOT, key)
        if os.path.isdir(d):
            return d
    # Neither exists yet (e.g. fresh machine) -- keep the derived-current path so the
    # eventual "no such directory" error names the checkout actually in use.
    return os.path.join(_PROJECTS_ROOT, _PROJECT_DIR_CANDIDATES[0])


DEFAULT_PROJECT_DIR = _default_project_dir()

UUID_RE = re.compile(r"^[0-9a-f-]{8,36}\.jsonl$")


def price_for(model):
    """Return (in_rate, out_rate) or None if the model has no price row."""
    if not model:
        return None
    for prefix, rates in PRICES.items():
        if model.startswith(prefix):
            return rates
    return None


def usage_cost(model, u):
    """USD cost of one usage block; None if model unpriced."""
    rates = price_for(model)
    if rates is None:
        return None
    in_rate, out_rate = rates
    c = u.get("cache_creation") or {}
    c1h = c.get("ephemeral_1h_input_tokens", 0) or 0
    c5m = c.get("ephemeral_5m_input_tokens", 0) or 0
    return (
        (u.get("input_tokens", 0) or 0) * in_rate
        + (u.get("cache_read_input_tokens", 0) or 0) * in_rate * CACHE_READ_MULT
        + c5m * in_rate * CACHE_5M_MULT
        + c1h * in_rate * CACHE_1H_MULT
        + (u.get("output_tokens", 0) or 0) * out_rate
    ) / 1e6


def is_prompt_record(r):
    """True if this user record starts a turn (a prompt, not a tool_result/meta)."""
    if r.get("type") != "user" or r.get("isMeta"):
        return False
    content = (r.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        return not any(isinstance(b, dict) and b.get("type") == "tool_result"
                       for b in content)
    return False


def new_stats():
    return {"output": 0, "input": 0, "cache_read": 0, "c1h": 0, "c5m": 0,
            "cost": 0.0, "models": set(), "n_msgs": 0}


def add_usage(stats, model, u, unpriced_models):
    c = u.get("cache_creation") or {}
    stats["output"] += u.get("output_tokens", 0) or 0
    stats["input"] += u.get("input_tokens", 0) or 0
    stats["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
    stats["c1h"] += c.get("ephemeral_1h_input_tokens", 0) or 0
    stats["c5m"] += c.get("ephemeral_5m_input_tokens", 0) or 0
    stats["n_msgs"] += 1
    if model and model != "<synthetic>":
        stats["models"].add(model)
    cost = usage_cost(model, u)
    if cost is None:
        unpriced_models[model] += 1
    else:
        stats["cost"] += cost


def scan_file(path, turns=None, unpriced_models=None):
    """Scan one JSONL. If turns is a list, append per-turn dicts; always return
    (totals, n_assistant_records, n_missing_usage, n_unique_msgs)."""
    totals = new_stats()
    seen_ids = set()
    n_asst = n_missing = 0
    if unpriced_models is None:
        unpriced_models = defaultdict(int)
    cur = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                r = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            t = r.get("type")
            if turns is not None and is_prompt_record(r):
                origin = (r.get("origin") or {}).get("kind") or "harness"
                cur = {"n": len(turns) + 1, "ts": r.get("timestamp", "?"),
                       "origin": origin, "stats": new_stats()}
                turns.append(cur)
                continue
            if t != "assistant":
                continue
            n_asst += 1
            m = r.get("message") or {}
            u = m.get("usage")
            if not u:
                n_missing += 1
                continue
            mid = m.get("id") or r.get("uuid")
            if mid in seen_ids:
                continue  # streamed split of an already-counted message
            seen_ids.add(mid)
            model = m.get("model")
            add_usage(totals, model, u, unpriced_models)
            if turns is not None:
                if cur is None:  # assistant output before the first prompt
                    cur = {"n": 0, "ts": r.get("timestamp", "?"),
                           "origin": "(pre-prompt)", "stats": new_stats()}
                    turns.insert(0, cur)
                add_usage(cur["stats"], model, u, unpriced_models)
    return totals, n_asst, n_missing, len(seen_ids)


def fmt_row(cols, widths):
    return "  ".join(str(c).rjust(w) if i else str(c).ljust(w)
                     for i, (c, w) in enumerate(zip(cols, widths)))


def model_label(models):
    if not models:
        return "-"
    short = sorted(m.replace("claude-", "") for m in models)
    return ",".join(short)


def print_table(rows, header):
    widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
    print(fmt_row(header, widths))
    print(fmt_row(["-" * w for w in widths], widths))
    for r in rows:
        print(fmt_row(r, widths))


def stats_cols(stats):
    return [stats["output"], stats["input"], stats["cache_read"],
            stats["c1h"], stats["c5m"], "%.4f" % stats["cost"]]


def run_session(path, include_subagents, as_of):
    turns = []
    unpriced = defaultdict(int)
    totals, n_asst, n_missing, n_uniq = scan_file(path, turns, unpriced)
    sid = os.path.basename(path).replace(".jsonl", "")
    print("Session: %s" % sid)
    print("File: %s" % path)
    header = ["turn", "timestamp", "origin", "model", "out_tok", "in_tok",
              "cache_rd", "cw_1h", "cw_5m", "cost_usd"]
    rows = []
    for t in turns:
        s = t["stats"]
        ts = t["ts"][:19].replace("T", " ") if t["ts"] != "?" else "?"
        rows.append([t["n"], ts, t["origin"], model_label(s["models"])] + stats_cols(s))
    rows.append(["TOTAL", "", "", model_label(totals["models"])] + stats_cols(totals))
    print_table(rows, header)
    print()
    print("Assistant records: %d; unique billed messages: %d; records MISSING a "
          "usage block: %d of %d" % (n_asst, n_uniq, n_missing, n_asst))
    if unpriced:
        print("UNPRICED models (tokens listed above, cost counted as $0): %s"
              % dict(unpriced))
    grand = totals["cost"]

    if include_subagents:
        subdir = os.path.join(os.path.dirname(path), sid, "subagents")
        agent_files = sorted(glob.glob(os.path.join(subdir, "agent-*.jsonl")))
        if not agent_files:
            print("No subagent JSONLs found under %s" % subdir)
        else:
            print()
            print("Subagents (%d files under %s):" % (len(agent_files), subdir))
            sub_total = new_stats()
            sub_missing = sub_asst = 0
            srows = []
            for ap in agent_files:
                st, na, nm, _ = scan_file(ap, None, unpriced)
                sub_asst += na
                sub_missing += nm
                for k in ("output", "input", "cache_read", "c1h", "c5m", "cost",
                          "n_msgs"):
                    sub_total[k] += st[k]
                sub_total["models"] |= st["models"]
                srows.append([os.path.basename(ap).replace(".jsonl", ""),
                              model_label(st["models"])] + stats_cols(st))
            srows.append(["SUBAGENT TOTAL", model_label(sub_total["models"])]
                         + stats_cols(sub_total))
            print_table(srows, ["agent", "model", "out_tok", "in_tok", "cache_rd",
                                "cw_1h", "cw_5m", "cost_usd"])
            print("Subagent assistant records: %d; missing usage: %d"
                  % (sub_asst, sub_missing))
            grand += sub_total["cost"]
            print()
            print("SESSION GRAND TOTAL (main + subagents): $%.4f" % grand)
    return grand


def run_all_sessions(project_dir, include_subagents):
    files = sorted(glob.glob(os.path.join(project_dir, "*.jsonl")),
                   key=os.path.getmtime, reverse=True)
    rows = []
    unpriced = defaultdict(int)
    gtot = new_stats()
    gsub_cost = 0.0
    for path in files:
        st, na, nm, _ = scan_file(path, None, unpriced)
        sub_cost = 0.0
        n_agents = 0
        if include_subagents:
            sid = os.path.basename(path).replace(".jsonl", "")
            for ap in glob.glob(os.path.join(project_dir, sid, "subagents",
                                             "agent-*.jsonl")):
                sst, _, snm, _ = scan_file(ap, None, unpriced)
                sub_cost += sst["cost"]
                nm += snm
                n_agents += 1
        for k in ("output", "input", "cache_read", "c1h", "c5m", "cost"):
            gtot[k] += st[k]
        gtot["models"] |= st["models"]
        gsub_cost += sub_cost
        row = [os.path.basename(path).replace(".jsonl", "")[:12],
               model_label(st["models"])] + stats_cols(st)
        if include_subagents:
            row += [n_agents, "%.4f" % sub_cost,
                    "%.4f" % (st["cost"] + sub_cost)]
        row += [nm]
        rows.append(row)
    header = ["session", "model", "out_tok", "in_tok", "cache_rd", "cw_1h",
              "cw_5m", "main_usd"]
    if include_subagents:
        header += ["agents", "sub_usd", "total_usd"]
    header += ["miss_usage"]
    trow = ["TOTAL", model_label(gtot["models"])] + stats_cols(gtot)
    if include_subagents:
        trow += ["", "%.4f" % gsub_cost, "%.4f" % (gtot["cost"] + gsub_cost)]
    trow += [""]
    rows.append(trow)
    print_table(rows, header)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass  # pre-3.7; ASCII-only output anyway
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--session", help="session uuid prefix (default: most recently "
                    "modified session JSONL in the project dir)")
    ap.add_argument("--as-of", required=True, metavar="YYYY-MM-DD",
                    help="the date you are running this analysis (required; no "
                    "today() default by repo rule)")
    ap.add_argument("--project-dir", default=DEFAULT_PROJECT_DIR,
                    help="Claude Code project directory holding the JSONLs")
    ap.add_argument("--all-sessions", action="store_true",
                    help="one summary row per session JSONL instead of per-turn")
    ap.add_argument("--include-subagents", action="store_true",
                    help="also price <session>/subagents/agent-*.jsonl (the bulk "
                    "of spend on dispatch-heavy sessions)")
    args = ap.parse_args()

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.as_of):
        ap.error("--as-of must be YYYY-MM-DD")

    print("=" * 70)
    print("WARNING: prices are as-of %s (source: bundled claude-api skill cache)."
          % PRICES_AS_OF)
    print("Analysis run --as-of %s. If Anthropic pricing has changed since "
          "%s, every cost below is wrong; update PRICES at the top of this "
          "script." % (args.as_of, PRICES_AS_OF))
    print("Costs are ESTIMATES from JSONL usage blocks at first-party API list "
          "rates; Jon is on a Max subscription, so these are shadow-prices of "
          "the compute, not an invoice.")
    print("=" * 70)
    print()

    if args.all_sessions:
        run_all_sessions(args.project_dir, args.include_subagents)
        return

    if args.session:
        matches = [p for p in glob.glob(os.path.join(args.project_dir, "*.jsonl"))
                   if os.path.basename(p).startswith(args.session)]
        if not matches:
            sys.exit("No session JSONL starting with %r in %s"
                     % (args.session, args.project_dir))
        if len(matches) > 1:
            sys.exit("Ambiguous prefix %r: %s" % (args.session,
                     [os.path.basename(m) for m in matches]))
        path = matches[0]
    else:
        files = [p for p in glob.glob(os.path.join(args.project_dir, "*.jsonl"))]
        if not files:
            sys.exit("No session JSONLs in %s" % args.project_dir)
        path = max(files, key=os.path.getmtime)

    run_session(path, args.include_subagents, args.as_of)
    print()
    print("NOT RECORDED IN THE JSONL (known bounds):")
    print("  - No dollar field exists anywhere; cost is derived, never logged.")
    print("  - Server-side tool spend (web_search_requests etc.) is counted but "
          "not priced here (0 in every record inspected 2026-08-21).")
    print("  - Cache-write TTL split exists only in cache_creation buckets; "
          "records from older harness versions may lack them (counted as 0).")
    print("  - Subagent spend lives in separate files; without "
          "--include-subagents the session total is a floor, not a total.")
    print("  - <synthetic> records are harness-generated (no API call), "
          "priced $0.")


if __name__ == "__main__":
    main()
