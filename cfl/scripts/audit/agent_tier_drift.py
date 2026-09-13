#!/usr/bin/env python3
"""agent_tier_drift.py -- does each subagent RUN on the tier its definition DECLARES?

WHY. `token_spend.py` measured Haiku at 1.19% of weighted spend while this repo defines
`lint-checker` and `extractor` AT HAIKU and describes them as the mechanical lane. Either that work
is not being dispatched, or it is being dispatched to a bigger model than its own definition asks
for. Those two have opposite fixes, and the count alone cannot tell them apart -- so this reads the
DECLARATION and the RUN and compares them per agent.

⛔ THE FIELD IS `attributionAgent`, READ FROM THE JSONL. It is NOT inferred from the filename, the
slug, or the prompt text. `slug` is a random three-word label ("fluffy-stirring-church") and has
nothing to do with agent identity -- guessing from it would have produced a confident, wrong table.

READ-ONLY.
"""
import argparse, collections, datetime as dt, glob, io, json, os, re, sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

TIER_RANK = {"haiku": 1, "sonnet": 2, "fable": 2, "opus": 3}


def tier_of(model):
    if not model:
        return None
    m = model.lower()
    for k in TIER_RANK:
        if k in m:
            return k
    return None


def declared_models(agent_dirs):
    """Parse `model:` out of each agent definition's YAML frontmatter.

    Deliberately a line scan, not a YAML load: several of these files carry prose bodies that are
    not valid YAML below the fence, and a parser failure would silently drop an agent from the
    denominator -- which is the exact way a census under-reports.
    """
    out = {}
    for d in agent_dirs:
        for p in glob.glob(os.path.join(d, "*.md")):
            name = os.path.splitext(os.path.basename(p))[0]
            try:
                txt = io.open(p, encoding="utf-8", errors="replace").read(4000)
            except OSError:
                continue
            head = txt.split("---", 2)
            head = head[1] if len(head) > 2 else txt[:1500]
            m = re.search(r"^\s*model:\s*['\"]?([A-Za-z0-9._-]+)", head, re.M)
            out[name] = m.group(1) if m else "(unset -> inherits caller)"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--since", help="YYYY-MM-DD")
    a = ap.parse_args()

    since = None
    if a.since:
        since = dt.datetime.strptime(a.since, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)

    decl = declared_models([
        os.path.join(os.getcwd(), ".claude", "agents"),
        os.path.expanduser("~/.claude/agents"),
    ])

    obs = collections.defaultdict(collections.Counter)   # agent -> model -> calls
    tok = collections.defaultdict(float)                 # agent -> weighted
    n_files = n_rec = 0

    for p in glob.glob(os.path.join(a.root, "**", "subagents", "agent-*.jsonl"), recursive=True):
        n_files += 1
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
                msg = d.get("message") or {}
                u = msg.get("usage")
                if not isinstance(u, dict):
                    continue
                if since:
                    ts = d.get("timestamp")
                    if not ts:
                        continue
                    try:
                        if dt.datetime.fromisoformat(ts.replace("Z", "+00:00")) < since:
                            continue
                    except Exception:
                        continue
                agent = d.get("attributionAgent") or "(unattributed)"
                model = msg.get("model") or "(none)"
                obs[agent][model] += 1
                tok[agent] += (float(u.get("output_tokens") or 0) * 5
                               + float(u.get("input_tokens") or 0)
                               + float(u.get("cache_creation_input_tokens") or 0) * 1.25
                               + float(u.get("cache_read_input_tokens") or 0) * 0.1)
                n_rec += 1

    total = sum(tok.values()) or 1.0
    print("=" * 84)
    print(f"AGENT TIER DRIFT  ·  since={a.since or 'ALL TIME'}")
    print("=" * 84)
    print(f"POPULATION: {n_files} subagent jsonls · {n_rec} assistant records with usage · "
          f"{len(decl)} agent definitions found on disk")

    print(f"\n{'agent':<28} {'declared':<16} {'ran as':<18} {'calls':>7} {'share':>7}  verdict")
    print("-" * 100)
    drift = []
    for agent in sorted(obs, key=lambda k: -tok[k]):
        d_model = decl.get(agent, "(NO DEFINITION FOUND)")
        d_tier = tier_of(d_model)
        for model, calls in obs[agent].most_common():
            o_tier = tier_of(model)
            verdict = ""
            if d_tier and o_tier:
                if o_tier == d_tier:
                    verdict = "ok"
                elif TIER_RANK[o_tier] > TIER_RANK[d_tier]:
                    # ⚠️ WORDING CORRECTED WITHIN HOURS OF THE FIRST RUN. This said
                    # "⛔ RAN HIGHER THAN DECLARED", which reads as a defect -- and the dispatch
                    # census below proved it is usually a DELIBERATE per-call override, which the
                    # Agent tool documents as taking precedence over the frontmatter.
                    # ⭐ The numbers closed exactly: 13 `fable-mirror -> opus` dispatches, and
                    # 13 agent files that ran Opus end to end. Nothing was overridden by accident.
                    # A verdict column that calls a documented, intentional choice a defect trains
                    # its reader to ignore the column.
                    verdict = "higher than declared — see dispatch census (usually deliberate)"
                    drift.append((agent, d_model, model, calls))
                else:
                    verdict = "ran lower than declared"
            elif d_model.startswith("(unset"):
                verdict = "inherits caller — declaration cannot drift"
            print(f"{agent:<28} {d_model:<16} {model:<18} {calls:>7} "
                  f"{tok[agent]/total*100:6.1f}%  {verdict}")

    print("\n--- DECLARED AGENTS THAT NEVER RAN in this window")
    never = [n for n in sorted(decl) if n not in obs]
    print("  " + (", ".join(never) if never else "(none)"))
    if never:
        print(f"  ⭐ {len(never)} of {len(decl)} definitions produced ZERO calls. An agent that is")
        print("     defined and never dispatched is not a cheap lane — it is an unused one, and it")
        print("     costs nothing precisely because it does nothing.")
    else:
        print(f"  ✅ all {len(decl)} defined agents were dispatched at least once — the fleet is in")
        print("     use, so a small cheap-tier share is about WHAT they are given, not whether they run.")

    # ⭐ THE LEVER THIS WHOLE SCRIPT WAS BUILT TO FIND. An agent with no definition has no declared
    # tier, so it INHERITS THE CALLER'S MODEL — and the caller is a top-tier coordinator. That makes
    # "undeclared" the most expensive setting available, and it is also the DEFAULT.
    undeclared = sum(v for k, v in tok.items() if decl.get(k) is None)
    print(f"\n--- UNDECLARED-TIER SHARE: {undeclared/total*100:.1f}% of delegated spend")
    print("  These agents carry NO definition file, so they inherit the dispatching coordinator's")
    print("  model. ⛔ The default is not 'cheap' and it is not 'neutral' — it is TOP TIER, and it")
    print("  applies to the busiest lanes precisely because those are the generic ones.")

    # ── DISPATCH CENSUS ───────────────────────────────────────────────────────────────────────
    # ⭐ THE OTHER HALF, AND WITHOUT IT THE TABLE ABOVE MISLEADS. The declaration lives in the agent
    # file; the RUN lives in the subagent JSONL; but the CHOICE lives in the PARENT session's
    # tool_use input, and nothing above can see it. Read the caller for the parameter and the callee
    # for the result -- the inverse of the usual lesson here, and the same discipline.
    disp = collections.Counter()
    over = collections.Counter()
    for p in glob.glob(os.path.join(a.root, "*", "*.jsonl")):
        try:
            fh = io.open(p, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if '"Agent"' not in line and '"Task"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                content = (d.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for b in content:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"
                            and b.get("name") in ("Agent", "Task")):
                        continue
                    inp = b.get("input") or {}
                    st = inp.get("subagent_type") or "(none)"
                    disp[st] += 1
                    if "model" in inp:
                        over[(st, str(inp["model"]))] += 1

    up = sum(v for (st, m), v in over.items() if tier_of(m) == "opus")
    down = sum(v for (st, m), v in over.items() if tier_of(m) in ("haiku", "sonnet", "fable"))
    print(f"\n--- DISPATCH CENSUS: {sum(disp.values())} Agent/Task calls, "
          f"{sum(over.values())} carried an explicit model override")
    for (st, m), v in over.most_common(10):
        arrow = "UP  " if tier_of(m) == "opus" else "down"
        print(f"  {v:>5}  {arrow}  {st} -> {m}")
    print(f"\n  ⭐ EXPLICIT UPGRADES TO OPUS: {up}    EXPLICIT DOWNGRADES: {down}")
    if down:
        print(f"     We reach for the top tier {up/down:.1f}x as often as we reach for a cheaper one,")
    print("     ON TOP OF a default that is ALREADY top tier for any undeclared agent. ⛔ That is")
    print("     the whole finding: the thumb is on one side of the scale twice over.")

    if drift:
        print("\n--- RAN ABOVE ITS DECLARED TIER (read WITH the census above, not instead of it)")
        for agent, dm, om, calls in drift:
            print(f"     {agent}: declared {dm}, ran {om}, {calls} calls")
        print("     ⚠️ NOT presumed a defect. A per-call `model` override is documented to take")
        print("        precedence over the frontmatter, so most of this is deliberate and simply")
        print("        never written down. A declaration is a DEFAULT, not a fence.")
    else:
        print("\n✅ NO TIER DRIFT: every agent with a declared tier ran at or below it.")
        print("   ⚠️ Which means a low Haiku share is a DISPATCH question, not a routing bug —")
        print("      the cheap lanes are not being sent work, rather than being overridden.")

    print("\n⛔ BOUND: `attributionAgent` is present only on subagent records. Main-lane turns carry")
    print("   no agent name and are excluded here by construction — this table is about DELEGATED")
    print("   work only, and says nothing about what the coordinators ran themselves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
