#!/usr/bin/env python
"""turn_cost_report.py -- per-turn token/cost instrumentation over a Claude Code session JSONL.

Jon's demand (2026-08-20, verbatim): "I don't gate the denominator, i need YOU to get me the
informmation i need to actually review your work in terms of cost and output at the turn-level
at a minimum." This is INSTRUMENTATION, not a forecast.

Measured field shapes (probed against session 643640a7 on 2026-08-21, not assumed):
  - assistant records carry message.usage with input_tokens, output_tokens,
    cache_creation_input_tokens, cache_read_input_tokens, and
    usage.cache_creation.{ephemeral_1h_input_tokens, ephemeral_5m_input_tokens}.
  - ONE API message spans MULTIPLE assistant records (same message.id, up to 9 records,
    usage byte-identical across them) -> usage is counted ONCE per message.id, else the
    report over-counts by ~2x.
  - Turn boundary = a 'user' record whose message content is NOT tool_result-only
    (tool_result carriers are intra-turn plumbing, not turns).
  - origin.kind is 'human' on typed prompts, 'task-notification' on agent-completion pings,
    absent otherwise; isMeta marks harness-injected user records.

COST PROXY, not dollars: proxy units = input-token equivalents using published Anthropic
price RATIOS (output 5x input; 5m cache write 1.25x; 1h cache write 2x; cache read 0.1x).
No dollar figure is printed because the model/price table is not an input this script
verifies. The formula is printed in the report header so the number is auditable.

ASCII-safe output by construction (19 of 59 instruments here die on non-ASCII stdout).
"""

import argparse
import glob
import json
import os
import re
import sys

# Force ASCII-safe stdout on cp1252 consoles.
sys.stdout.reconfigure(errors="replace")

def _key_for(path):
    """~/.claude/projects sanitises a path by replacing every non-alphanumeric
    CHARACTER (not run) with '-'. Mirrors extract_claude_code_sessions.py's _key_for."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(path)).strip("-")


_PROJECTS_ROOT = os.path.join(os.path.expanduser("~"), ".claude", "projects")
_CODE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ⛔ THIS WAS PINNED TO THE G: KEY, AND THE 2026-09-02 G:->N: MOVE SILENTLY DEMOTED IT
# TO A TRUNK CFL LEFT THREE DAYS AGO -- --session lookups against current work would
# report "no session file matches" (or worse, resolve a stale same-prefix G: session)
# with no error naming the real cause. This script has no --project-dir override, so
# resolve_session() below now searches EVERY candidate dir (current-derived first,
# then historical) rather than a single hardcoded PROJECT_DIR.
PROJECT_DIR_CANDIDATES = [
    os.path.join(_PROJECTS_ROOT, _key_for(_CODE_ROOT)),  # DERIVED: current checkout
    os.path.join(_PROJECTS_ROOT,
                 "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer"),  # historical
]
# kept so any external caller importing the old name still works; searched dirs are
# PROJECT_DIR_CANDIDATES, not this single value.
PROJECT_DIR = PROJECT_DIR_CANDIDATES[0]

# Relative price weights (input-token equivalents). Ratios from Anthropic pricing;
# a PROXY, not dollars.
W_INPUT, W_CACHE_5M, W_CACHE_1H, W_CACHE_READ, W_OUTPUT = 1.0, 1.25, 2.0, 0.1, 5.0


def asc(s):
    """Coerce any string to plain ASCII."""
    return str(s).encode("ascii", "replace").decode("ascii")


def resolve_session(arg):
    if os.path.isfile(arg):
        return arg
    hits = []
    for d in PROJECT_DIR_CANDIDATES:
        for h in sorted(glob.glob(os.path.join(d, arg + "*.jsonl"))):
            if os.path.isfile(h) and h not in hits:
                hits.append(h)
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit("ERROR: no session file matches %r under any of %s"
                 % (arg, PROJECT_DIR_CANDIDATES))
    sys.exit("ERROR: %d session files match %r: %s" % (len(hits), arg, [os.path.basename(h) for h in hits]))


def is_turn_boundary(rec):
    """A user record opens a new turn unless it is a tool_result carrier."""
    m = rec.get("message") or {}
    cont = m.get("content")
    if isinstance(cont, list):
        kinds = set(b.get("type") for b in cont if isinstance(b, dict))
        return kinds != {"tool_result"}
    return True  # plain-string user content


def origin_label(rec):
    kind = (rec.get("origin") or {}).get("kind")
    if kind:
        return kind
    return "meta" if rec.get("isMeta") else "user"


def user_snippet(rec, width=38):
    m = rec.get("message") or {}
    cont = m.get("content")
    if isinstance(cont, list):
        cont = " ".join(b.get("text", "") for b in cont if isinstance(b, dict))
    text = re.sub(r"\s+", " ", str(cont or "")).strip()
    return asc(text[:width])


class Tally(object):
    __slots__ = ("inp", "out", "c5m", "c1h", "cread", "msgs")

    def __init__(self):
        self.inp = self.out = self.c5m = self.c1h = self.cread = self.msgs = 0

    def add_usage(self, u):
        cc = u.get("cache_creation") or {}
        c5m = cc.get("ephemeral_5m_input_tokens")
        c1h = cc.get("ephemeral_1h_input_tokens")
        if c5m is None and c1h is None:
            # fall back to the flat field, attributed as 5m (bound printed by caller)
            c5m, c1h = u.get("cache_creation_input_tokens", 0), 0
        self.inp += u.get("input_tokens", 0) or 0
        self.out += u.get("output_tokens", 0) or 0
        self.c5m += c5m or 0
        self.c1h += c1h or 0
        self.cread += u.get("cache_read_input_tokens", 0) or 0
        self.msgs += 1

    def proxy(self):
        return (W_INPUT * self.inp + W_CACHE_5M * self.c5m + W_CACHE_1H * self.c1h
                + W_CACHE_READ * self.cread + W_OUTPUT * self.out)

    def cache_write(self):
        return self.c5m + self.c1h


def scan_file(path, as_of, bounds):
    """Yield (record, parsed-ok) in file order; count bounds."""
    out = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            bounds["lines"] += 1
            try:
                rec = json.loads(line)
            except ValueError:
                bounds["parse_errors"] += 1
                continue
            ts = rec.get("timestamp") or ""
            if ts and ts[:10] > as_of:
                bounds["beyond_as_of"] += 1
                continue
            out.append(rec)
    return out


def tally_assistants(records, bounds, seen_ids):
    """Per-file rollup of assistant usage, deduped by message.id."""
    t = Tally()
    for rec in records:
        if rec.get("type") != "assistant":
            continue
        bounds["assistant_records"] += 1
        m = rec.get("message") or {}
        u = m.get("usage")
        if not u:
            bounds["usage_absent"] += 1
            continue
        mid = m.get("id") or rec.get("uuid")
        if mid in seen_ids:
            bounds["dup_msgid_records"] += 1
            continue
        seen_ids.add(mid)
        if "cache_creation" not in u:
            bounds["flat_cache_fallback"] += 1
        t.add_usage(u)
    return t


def main():
    ap = argparse.ArgumentParser(description="Per-turn token/cost report over a session JSONL.")
    ap.add_argument("--session", required=True, help="session uuid (or prefix) or a path to a .jsonl")
    ap.add_argument("--as-of", required=True, metavar="YYYY-MM-DD",
                    help="reporting date; records timestamped after this date are excluded (no default, repo convention)")
    ap.add_argument("--max-turn-rows", type=int, default=0,
                    help="print only the last N turn rows (0 = all)")
    args = ap.parse_args()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.as_of):
        sys.exit("ERROR: --as-of must be YYYY-MM-DD")

    path = resolve_session(args.session)
    bounds = {"lines": 0, "parse_errors": 0, "beyond_as_of": 0, "assistant_records": 0,
              "usage_absent": 0, "dup_msgid_records": 0, "flat_cache_fallback": 0}
    records = scan_file(path, args.as_of, bounds)

    # ---- per-turn walk (main file only) ----
    turns = []  # dicts: n, ts, origin, snippet, tally
    cur = None
    seen_ids = set()
    pre_turn = Tally()  # assistant usage before any turn boundary (compact-resume tails)
    for rec in records:
        t = rec.get("type")
        if t == "user" and is_turn_boundary(rec):
            cur = {"n": len(turns) + 1, "ts": (rec.get("timestamp") or "")[:19],
                   "origin": origin_label(rec), "snippet": user_snippet(rec), "tally": Tally()}
            turns.append(cur)
        elif t == "assistant":
            m = rec.get("message") or {}
            u = m.get("usage")
            bounds["assistant_records"] += 1
            if not u:
                bounds["usage_absent"] += 1
                continue
            mid = m.get("id") or rec.get("uuid")
            if mid in seen_ids:
                bounds["dup_msgid_records"] += 1
                continue
            seen_ids.add(mid)
            if "cache_creation" not in u:
                bounds["flat_cache_fallback"] += 1
            (cur["tally"] if cur else pre_turn).add_usage(u)

    # ---- subagents rollup ----
    sub_dir = os.path.splitext(path)[0]
    sub_dir = os.path.join(sub_dir, "subagents")
    sub_rows = []
    sub_total = Tally()
    sub_bounds = {"lines": 0, "parse_errors": 0, "beyond_as_of": 0, "assistant_records": 0,
                  "usage_absent": 0, "dup_msgid_records": 0, "flat_cache_fallback": 0}
    sub_files = sorted(glob.glob(os.path.join(sub_dir, "agent-*.jsonl"))) if os.path.isdir(sub_dir) else []
    for sf in sub_files:
        recs = scan_file(sf, args.as_of, sub_bounds)
        st = tally_assistants(recs, sub_bounds, set())
        for k in ("inp", "out", "c5m", "c1h", "cread", "msgs"):
            setattr(sub_total, k, getattr(sub_total, k) + getattr(st, k))
        sub_rows.append((os.path.basename(sf), st))

    # ---- report ----
    P = print
    P("TURN COST REPORT  (as-of %s)" % args.as_of)
    P("session file : %s" % asc(path))
    P("cost proxy   : input-token equivalents = 1.0*input + 1.25*cache_5m_write + 2.0*cache_1h_write")
    P("               + 0.1*cache_read + 5.0*output   (price RATIOS, not dollars)")
    P("")
    hdr = "%-5s %-19s %-13s %9s %7s %12s %11s %13s %15s  %s" % (
        "turn", "timestamp(UTC)", "origin", "out_tok", "in_tok", "cache_write",
        "cache_read", "proxy_units", "cum_proxy", "prompt_snippet")
    P(hdr)
    P("-" * len(hdr))
    cum = pre_turn.proxy()
    if pre_turn.msgs:
        P("%-5s %-19s %-13s %9d %7d %12d %11d %13.0f %15.0f  %s" % (
            "pre", "-", "pre-boundary", pre_turn.out, pre_turn.inp, pre_turn.cache_write(),
            pre_turn.cread, pre_turn.proxy(), cum,
            "(assistant usage before first turn boundary)"))
    rows = turns if not args.max_turn_rows else turns[-args.max_turn_rows:]
    hidden = len(turns) - len(rows)
    if hidden:
        for t in turns[:hidden]:
            cum += t["tally"].proxy()
        P("... %d earlier turn rows elided (--max-turn-rows); their proxy is in the cumulative ..." % hidden)
    for t in rows:
        ty = t["tally"]
        cum += ty.proxy()
        P("%-5d %-19s %-13s %9d %7d %12d %11d %13.0f %15.0f  %s" % (
            t["n"], t["ts"], asc(t["origin"]), ty.out, ty.inp, ty.cache_write(),
            ty.cread, ty.proxy(), cum, t["snippet"]))

    def rollup(name, t):
        P("%-28s msgs=%-5d out=%-9d in=%-8d cache_write=%-11d (5m=%d 1h=%d) cache_read=%-11d proxy=%.0f" % (
            name, t.msgs, t.out, t.inp, t.cache_write(), t.c5m, t.c1h, t.cread, t.proxy()))

    P("")
    P("PER-SESSION ROLLUP (main file, deduped by message.id)")
    total = Tally()
    for t in [pre_turn] + [x["tally"] for x in turns]:
        for k in ("inp", "out", "c5m", "c1h", "cread", "msgs"):
            setattr(total, k, getattr(total, k) + getattr(t, k))
    rollup("  main session", total)

    if sub_files:
        P("")
        P("SUBAGENTS ROLLUP (%d agent files under %s)" % (len(sub_files), asc(sub_dir)))
        for name, st in sorted(sub_rows, key=lambda r: -r[1].proxy())[:15]:
            rollup("  " + name, st)
        if len(sub_rows) > 15:
            P("  ... %d more agent files in the total below ..." % (len(sub_rows) - 15))
        rollup("  SUBAGENT TOTAL", sub_total)
        P("")
        grand = Tally()
        for src in (total, sub_total):
            for k in ("inp", "out", "c5m", "c1h", "cread", "msgs"):
                setattr(grand, k, getattr(grand, k) + getattr(src, k))
        rollup("  GRAND TOTAL (main+subs)", grand)

    P("")
    P("MEASURED BOUNDS (this run, not assumptions)")
    P("  main file : %d lines, %d parse errors, %d records beyond --as-of excluded" % (
        bounds["lines"], bounds["parse_errors"], bounds["beyond_as_of"]))
    P("  main file : usage absent on %d of %d assistant records; %d duplicate-message.id records skipped (one API message spans multiple records; usage counted once per id)" % (
        bounds["usage_absent"], bounds["assistant_records"], bounds["dup_msgid_records"]))
    P("  main file : %d messages lacked usage.cache_creation split; their flat cache_creation_input_tokens was weighted as 5m" % bounds["flat_cache_fallback"])
    if sub_files:
        P("  subagents : %d files; %d lines, %d parse errors, %d beyond --as-of; usage absent on %d of %d assistant records; %d dup-id skipped; %d flat-cache fallback" % (
            len(sub_files), sub_bounds["lines"], sub_bounds["parse_errors"], sub_bounds["beyond_as_of"],
            sub_bounds["usage_absent"], sub_bounds["assistant_records"],
            sub_bounds["dup_msgid_records"], sub_bounds["flat_cache_fallback"]))
    else:
        P("  subagents : no subagents/ directory for this session")
    P("  NOT measured: dollar cost (proxy ratios only), tokens of sessions this one spawned in OTHER projects, ")
    P("  and any records the harness never wrote (a crash mid-turn leaves no usage record).")


if __name__ == "__main__":
    main()
