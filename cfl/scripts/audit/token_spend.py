#!/usr/bin/env python3
"""token_spend.py -- where the tokens actually go, measured from the JSONLs.

WHY THIS EXISTS. Jon, 2026-08-10: "Could you do to begen testing token efficency? We should be
looking for ways to improve model selection and compact effectiveness and efficiency. ANd I expect
some things.... do not need fable attention. You are all coordinators for a reason, not just between
but below."

The last spend number this program had was "the mirror is 29% of spend" (2026-08-03), and it was
produced once, by hand, for one question. Nothing has measured spend since. This is the instrument.

WHAT IT REFUSES TO DO, because every instrument here over-reported on its first run:
  - It never infers a model tier from an agent NAME. It reads message.model.
  - It never treats a missing usage block as zero; those records are counted and reported separately.
  - It prints its own DENOMINATOR and its own BOUND. A number without the population it came from is
    the defect this repo keeps paying for.

READ-ONLY. Touches nothing but the JSONLs it counts.
"""
import argparse, collections, datetime as dt, glob, io, json, os, sys

# ⛔ Windows consoles default to cp1252 and this file's own glyphs are outside it. The FIRST run
# printed every number correctly and then died on a warning-glyph in the last paragraph -- so the
# most alarming line in the report was the one guaranteed not to survive. Reconfigure once, here.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Price ratios, NOT dollars. Anchored at Haiku = 1. Deliberately relative: the point is "this
# workload could have run one tier down", and a ratio survives price changes that an absolute
# figure does not. Tiers not listed fall to UNKNOWN and are excluded from the ratio math rather
# than silently priced at zero.
TIER = {"opus": 15.0, "sonnet": 3.0, "haiku": 1.0, "fable": 3.0}


def tier_of(model: str):
    if not model:
        return None
    m = model.lower()
    for k in TIER:
        if k in m:
            return k
    return None


_UUID = __import__("re").compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def trunk_of(path: str) -> str:
    """Walk UP to the real trunk directory.

    ⛔ THE FIRST VERSION OF THIS WAS WRONG AND THE OUTPUT SAID SO IN A WAY THE COUNT COULD NOT.
    It took `dirname`, and one extra level for `subagents/`. But the real layout is
    `<trunk>/<session-uuid>/subagents/agent-*.jsonl`, so that landed on the SESSION UUID and
    reported it as a trunk. The delegation table then came out a perfect 0%/100% bimodal split --
    every named trunk 0% delegated, every UUID 100% -- because the two lanes had been sorted into
    SEPARATE BUCKETS rather than compared within one.
    ⭐ A ratio that comes out exactly 0 and exactly 100 across every row is not a finding about
    delegation; it is a grouping bug wearing a finding's clothes. Caught by READING THE LIST, which
    is now seven for seven on first-run over-reports in this repo -- never once by re-reading the
    number.
    """
    d = os.path.dirname(os.path.abspath(path))
    for _ in range(4):
        base = os.path.basename(d)
        if base and base != "subagents" and not _UUID.match(base):
            return base
        d = os.path.dirname(d)
    return "(unresolved)"


def human(n):
    for unit, div in (("B", 1e9), ("M", 1e6), ("k", 1e3)):
        if n >= div:
            return f"{n/div:.1f}{unit}"
    return str(int(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--since", help="YYYY-MM-DD; omit for all time")
    ap.add_argument("--top", type=int, default=12)
    a = ap.parse_args()

    since = None
    if a.since:
        since = dt.datetime.strptime(a.since, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)

    files = glob.glob(os.path.join(a.root, "**", "*.jsonl"), recursive=True)

    Z = lambda: collections.defaultdict(float)
    by_model, by_trunk, by_lane, by_effort = Z(), Z(), Z(), Z()
    deleg = collections.defaultdict(lambda: {"main": 0.0, "subagent": 0.0})
    calls = collections.Counter()
    cache_read = cache_write = raw_in = out = 0.0
    n_records = n_usage = n_nousage = n_undated = 0
    unknown_models = collections.Counter()

    for p in files:
        try:
            fh = io.open(p, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("type") != "assistant":
                    continue
                n_records += 1
                msg = d.get("message") or {}
                u = msg.get("usage")
                if not isinstance(u, dict):
                    n_nousage += 1
                    continue
                ts = d.get("timestamp")
                if since:
                    if not ts:
                        n_undated += 1
                        continue
                    try:
                        t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    except Exception:
                        n_undated += 1
                        continue
                    if t < since:
                        continue
                n_usage += 1

                model = msg.get("model") or "(none)"
                tier = tier_of(model)
                if tier is None:
                    unknown_models[model] += 1

                oi = float(u.get("output_tokens") or 0)
                ii = float(u.get("input_tokens") or 0)
                cr = float(u.get("cache_read_input_tokens") or 0)
                cw = float(u.get("cache_creation_input_tokens") or 0)
                out += oi; raw_in += ii; cache_read += cr; cache_write += cw

                # Weighted spend. Output dominates cost per token, and cache READS are the cheap
                # path -- counting them at full freight would hide the very lever we are looking for.
                # Weights are structural (output 5x input, cache-read 0.1x), stated here rather than
                # buried, so a reader can disagree with the model and not the arithmetic.
                weighted = oi * 5 + ii + cw * 1.25 + cr * 0.1

                trunk = trunk_of(p)
                lane = "subagent" if d.get("isSidechain") else "main"

                by_model[model] += weighted
                by_trunk[trunk] += weighted
                by_lane[lane] += weighted
                by_effort[str(d.get("effort") or "(unset)")] += weighted
                deleg[trunk][lane] += weighted
                calls[(model, lane)] += 1

    total = sum(by_model.values()) or 1.0

    print("=" * 78)
    print(f"TOKEN SPEND  ·  root={a.root}  ·  since={a.since or 'ALL TIME'}")
    print("=" * 78)
    print(f"POPULATION: {len(files)} jsonl files · {n_records} assistant records · "
          f"{n_usage} carried usage · {n_nousage} had NO usage block (excluded, not zeroed)"
          + (f" · {n_undated} undated and dropped by --since" if n_undated else ""))
    print(f"RAW TOKENS: output {human(out)} · input {human(raw_in)} · "
          f"cache-write {human(cache_write)} · cache-read {human(cache_read)}")
    creadable = cache_read + raw_in + cache_write
    if creadable:
        print(f"CACHE HIT RATIO: {cache_read/creadable*100:.1f}% of all input arrived from cache "
              f"-- this is the compact/caching lever, and it is the cheapest one.")

    def table(title, dd, note=""):
        print(f"\n--- {title} {note}")
        for k, v in sorted(dd.items(), key=lambda x: -x[1])[: a.top]:
            print(f"  {v/total*100:6.2f}%  {human(v):>8}  {k}")

    table("WEIGHTED SPEND BY MODEL", by_model)
    table("BY LANE", by_lane, "(main = a coordinator's own turns; subagent = delegated)")
    table("BY TRUNK", by_trunk)
    table("BY REASONING EFFORT", by_effort)

    # ⭐ THE DELEGATION RATIO, per trunk. This is the row Jon's question is actually about:
    # "You are all coordinators for a reason, not just between but below." The charter says a
    # coordinator "runs nothing itself -- delegation is the whole job". This measures whether that
    # is true of the SPEND, which is the only place the claim can be falsified.
    print("\n--- DELEGATION RATIO BY TRUNK (share of that trunk's spend that is DELEGATED)")
    print("    low = the coordinator is doing the work in its own top-tier context")
    for t in sorted(by_trunk, key=lambda k: -by_trunk[k])[: a.top]:
        d = deleg[t]
        tot = d["main"] + d["subagent"]
        if tot < total * 0.01:      # skip trunks under 1% -- a ratio on a tiny base is noise
            continue
        print(f"  {d['subagent']/tot*100:5.1f}% delegated   {human(tot):>8} total   {t}")

    # The actual question Jon asked: what could have run one tier down?
    print("\n--- MODEL SELECTION: what the top tier is costing")
    opus = sum(v for k, v in by_model.items() if tier_of(k) == "opus")
    print(f"  Opus-tier is {opus/total*100:.1f}% of weighted spend.")
    if opus:
        print(f"  At Sonnet prices that same work would weigh "
              f"{opus*TIER['sonnet']/TIER['opus']/total*100:.1f}% -- a "
              f"{(1-TIER['sonnet']/TIER['opus'])*100:.0f}% reduction ON THAT SLICE.")
        print("  ⚠️ NOT a recommendation to move it. This says what the tier costs, not whether the")
        print("     work needed it. Which turns needed Opus is a JUDGEMENT and this tool does not")
        print("     make it -- a number that recommends is a number that has stopped measuring.")

    if unknown_models:
        print("\n⚠️ MODELS NOT MAPPED TO A TIER (counted in spend, excluded from tier math):")
        for m, c in unknown_models.most_common(8):
            print(f"     {c:>6} records  {m}")

    print("\n⛔ BOUND, PRINTED NOT COMMENTED: this counts ~/.claude/projects only. Work billed")
    print("   through claude.ai, and any session whose JSONL was swept by cleanupPeriodDays before")
    print("   it was set to 3650, is NOT in this population. Treat every share as a share OF WHAT")
    print("   SURVIVED ON DISK, never as a share of what was spent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
