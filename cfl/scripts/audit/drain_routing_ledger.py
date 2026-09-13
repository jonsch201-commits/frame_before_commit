#!/usr/bin/env python3
"""Drain the PENDING rows of exchange/ROUTING-LEDGER.md into ONE triage manifest.

WHY THIS EXISTS
---------------
`route_agent_return.py` is the capture half: it records that a return happened. Capture without a
drain is the recorded defect of `skills/intake/` — a deposit-only queue that nobody empties. On
2026-08-03 an unrouted consult held twelve of Jon's rulings. **The record was never missing. It was
unrouted.**

Jon, B-2: *"We could make a wiki master subagent resume any time a json closed to update the wiki."*
This is that, built as **fan-IN rather than fan-out**.

WHY ONE DRAINER AND NOT ONE WRITER PER RETURN
---------------------------------------------
wiki-master is the only wiki writer by standing convention, and N concurrent wiki writers is a
recorded live defect (2026-07-03, plus two fresh instances on 2026-08-06 where one agent's staged
files were absorbed into another's commit). A queue with a single drainer preserves the invariant
that the fan-out design would break. It also buys the thing per-agent writers structurally cannot:
**dedup across returns.** Two agents on 2026-08-06 independently found the same defect class (an
audit script reading N-1 of N registers). Per-agent writers would have written it twice, with
nothing able to notice.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
* **It does not write the wiki.** Not one byte under `wiki/`. It emits a manifest to `exchange/`.
  A script that decides ingest-worthiness has taken a judgment call it cannot make. Every
  recommendation here is produced by a stated mechanical rule, printed beside it, so wiki-master
  overrides it by reading rather than by trusting.
* **It never blocks.** Exit 0 on every path including its own internal errors, for the same reason
  `route_agent_return.py` never blocks: this repo has two blocking rows whose steady state is
  "firing" and which are therefore ignored.
* **It never edits a prior ledger row.** It reads the ledger; in `--populate` it appends only.
* **It does not extract transcripts into the corpus.** Re-extraction is minutes on a Drive-mounted
  repo. It reads each JSONL once, in-process, and keeps only a bounded summary.

IDEMPOTENCE, WHICH IS TESTED AND NOT ASSUMED
--------------------------------------------
The harness says explicitly that an agent may notify more than once. Keying is on the **resolved
transcript path** (case- and separator-normalized), not on the ledger row, so two rows naming the
same transcript collapse to one manifest entry. The manifest is regenerated whole from current
ledger state, so a second drain cannot append a second copy of anything. `state.json` exists only to
report NEW-since-last-drain; deleting it changes the report, never the manifest.

Usage:
  drain_routing_ledger.py                  # drain: read ledger, write manifest
  drain_routing_ledger.py --populate       # append PENDING rows for un-rowed transcripts, then drain
  drain_routing_ledger.py --dry-run        # print manifest to stdout, write nothing
  drain_routing_ledger.py --self-test      # negative controls
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

# Windows consoles default to cp1252 and a stray arrow in a status line would crash the run --
# which for a never-blocks tool is the worst possible failure: it dies before it can report. Caught
# on the first real invocation, 2026-08-06.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LEDGER = os.path.join("exchange", "ROUTING-LEDGER.md")
OUT_DIR = os.path.join("exchange", "routing-drain")
MANIFEST = os.path.join(OUT_DIR, "MANIFEST.md")
STATE = os.path.join(OUT_DIR, "state.json")

# Agent ids are 17 hex chars. A 9-char mixed-alphanumeric id is a Bash background task, not an
# agent return -- measured 2026-08-06, after "28 of 30 unrouted" reached Jon twice and the honest
# number was 16 of 18. Shape is the discriminator.
AGENT_ID_RE = re.compile(r"^[0-9a-f]{17}$")
ID6_RE = re.compile(r"^[0-9a-f]{6}$")

PATH_RE = re.compile(r"(?:[\w.\-]+[/\\])+[\w.\-]+\.(?:py|md|sh|json|jsonl|ps1|yml|yaml|txt|html)")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z_\-]{4,}")

# Words that appear in almost every agent return and therefore carry no grouping signal.
STOPWORDS = set("""
about above after again against because before being below between both cannot could during each
found further having howeveritself might other should still such than that their theirs them then
there these thing think this those through under until using where which while whose would
agent agents return returns session sessions ticket tickets report reports repo repository file
files finding findings work working commit commits branch script scripts read reads reading write
writes writing wrote change changes changed check checks checked result results output outputs
claude wiki exchange jon coordinator subagent subagents
""".split())


# ---------------------------------------------------------------- infrastructure

def repo_root():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def norm_key(path):
    """Canonical dedup key for a transcript.

    Separator- and case-normalized because the same transcript arrives as a Windows path from the
    harness payload, a POSIX path from a Bash-authored row, and a bare basename from a hand-written
    one. Three spellings of one file must not become three manifest entries.
    """
    if not path:
        return ""
    p = path.replace("\\", "/").strip().strip("`").rstrip("/")
    return os.path.normpath(p).replace("\\", "/").lower()


# ---------------------------------------------------------------- ledger parsing

def parse_ledger(text):
    """Every pipe-table row in the ledger, as dicts. Prose and headers are skipped.

    Deliberately shape-driven rather than section-driven: the ledger has three separately-authored
    row blocks and a fourth appended by the hook, and a parser keyed on headings would silently
    read N-1 of N blocks. That exact defect -- an audit script reading N-1 of N registers -- was
    found twice on 2026-08-06.
    """
    cols = ["closed_utc", "parent6", "id6", "kind", "role", "extract", "disposition", "routed_by"]
    rows = []
    for lineno, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s.startswith("|") or not s.endswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) != len(cols):
            continue
        if cells[0] == "closed_utc":
            continue  # header
        # Separator row = EVERY cell is dashes/colons. Testing only the first cell silently ate
        # every real row, because the live ledger writes "-" as the closed_utc placeholder. The
        # self-test caught it; nothing else would have, since the result was a clean empty queue.
        if all(c and set(c) <= set("-: ") for c in cells):
            continue
        row = dict(zip(cols, cells))
        row["_lineno"] = lineno
        rows.append(row)
    return rows


def is_pending(row):
    d = row.get("disposition", "")
    return d.upper().startswith("PENDING")


def clean_id6(raw):
    m = re.search(r"\b([0-9a-f]{6})\b", raw or "")
    return m.group(1) if m else ""


# ---------------------------------------------------------------- transcript resolution

def transcript_index(roots):
    """id17 -> jsonl path, for every subagents/ dir under the given roots."""
    idx = {}
    for root in roots:
        if not root or not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            if os.path.basename(dirpath) != "subagents":
                continue
            for fn in filenames:
                if fn.startswith("agent-") and fn.endswith(".jsonl"):
                    aid = fn[len("agent-"):-len(".jsonl")]
                    idx.setdefault(aid, os.path.join(dirpath, fn))
    return idx


def default_transcript_roots(root):
    """Where CC keeps this project's session transcripts. Read-only, always.

    ⛔ THE SLUG DERIVATION HERE WAS WRONG, and it is exactly the per-character-vs-per-run
    trap: `.replace(":", "")` DELETES the colon instead of mapping it to '-', so
    "N:\\claude-cfl\\clone" produced "N-claude-cfl-clone" (one dash) where the real
    ~/.claude/projects key -- every non-alphanumeric CHARACTER replaced with '-',
    verified against extract_claude_code_sessions.py's _key_for -- is
    "N--claude-cfl-clone" (two dashes: ':' and the following '\\' each contribute one).
    Measured 2026-09-05: the old slug matched NO directory on disk, so
    default_transcript_roots() silently fell through to the G: historical root only for
    a current-checkout root, and the caller (dict.fromkeys + isdir filter) swallowed the
    miss without a word. Fixed to derive the same way the model fix does; PRINT AND CHECK
    before trusting a slug function again.
    """
    home = os.path.expanduser("~")
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(root)).strip("-")
    cand = [os.path.join(home, ".claude", "projects", slug),
            os.path.join(home, ".claude", "projects",
                         "G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer")]
    return [c for c in dict.fromkeys(cand) if os.path.isdir(c)]


def session_of(path):
    """The session uuid owning a transcript: <project>/<session-uuid>/subagents/agent-*.jsonl."""
    p = os.path.normpath(path).replace("\\", "/").split("/")
    return p[-3] if len(p) >= 3 else ""


def pick_session(idx, want=None):
    """Which session --populate backfills. NEVER all of them by default.

    The first real run of --populate swept every historical session in the project directory and
    appended 302 rows to a live shared ledger when the ticket asked for one session's 34. Scope
    defaults to the session holding the newest transcript, and the number of sessions DECLINED is
    printed rather than silently swept -- the same discipline `wake_map.py` adopted after the
    '28 of 30' denominator reached Jon twice.
    """
    sessions = {}
    for aid, p in idx.items():
        sessions.setdefault(session_of(p), []).append(p)
    if not sessions:
        return None, 0, {}
    if want:
        hits = [s for s in sessions if s.startswith(want)]
        if len(hits) == 1:
            return hits[0], len(sessions) - 1, sessions
        return None, len(sessions), sessions
    newest = max(sessions, key=lambda s: max(os.path.getmtime(p) for p in sessions[s]))
    return newest, len(sessions) - 1, sessions


def resolve(row, idx):
    """Resolve a row to a transcript path. UNRESOLVED is a reported state, never a silent drop."""
    extract = row.get("extract", "")
    # 1. the row names a real file
    for cand in re.findall(r"[^\s`|]+\.jsonl", extract):
        if os.path.isfile(cand):
            return cand, "row-path"
    # 2. the row names a full agent id
    for m in re.findall(r"\b([0-9a-f]{17})\b", extract + " " + row.get("id6", "")):
        if m in idx:
            return idx[m], "id17"
    # 3. id6 prefix -- the ledger's own column
    six = clean_id6(row.get("id6", ""))
    if six:
        hits = [p for a, p in idx.items() if a.startswith(six)]
        if len(hits) == 1:
            return hits[0], "id6-prefix"
        if len(hits) > 1:
            return None, f"AMBIGUOUS-id6 ({len(hits)} transcripts start with {six})"
    return None, "UNRESOLVED"


# ---------------------------------------------------------------- transcript summary

def summarize(path, meta_hint=None):
    """One bounded summary per transcript. Reads the file once; keeps nothing large.

    Never raises: a transcript that cannot be read yields a summary that SAYS it could not be read.
    An unreadable return is a finding, not an empty one.
    """
    s = {"path": path, "bytes": 0, "turns": 0, "tools": Counter(), "wrote": [], "commits": 0,
         "brief": "", "ret": "", "agent_type": "", "description": "", "error": "",
         "spawn_depth": None, "parent_agent": ""}
    meta = os.path.splitext(path)[0] + ".meta.json"
    # The .meta.json sidecar carries agentType/description without parsing the transcript at all.
    if os.path.isfile(meta):
        try:
            with open(meta, encoding="utf-8", errors="replace") as fh:
                m = json.load(fh)
            s["agent_type"] = m.get("agentType", "") or ""
            s["description"] = m.get("description", "") or ""
            s["spawn_depth"] = m.get("spawnDepth")
            s["parent_agent"] = m.get("parentAgentId", "") or ""
        except Exception as e:
            s["error"] = f"meta unreadable: {e.__class__.__name__}"
    if meta_hint:
        s.setdefault("hint", meta_hint)
    try:
        s["bytes"] = os.path.getsize(path)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                s["turns"] += 1
                msg = d.get("message") or {}
                content = msg.get("content")
                if isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                if not isinstance(content, list):
                    continue
                for blk in content:
                    if not isinstance(blk, dict):
                        continue
                    if blk.get("type") == "tool_use":
                        name = blk.get("name", "?")
                        s["tools"][name] += 1
                        inp = blk.get("input") or {}
                        if name in ("Write", "Edit", "NotebookEdit"):
                            fp = inp.get("file_path") or inp.get("notebook_path")
                            if fp:
                                s["wrote"].append(fp)
                        if name in ("Bash", "PowerShell"):
                            if "git commit" in (inp.get("command") or ""):
                                s["commits"] += 1
                    elif blk.get("type") == "text":
                        t = (blk.get("text") or "").strip()
                        if not t:
                            continue
                        if d.get("type") == "user" and not s["brief"]:
                            s["brief"] = t
                        elif d.get("type") == "assistant":
                            s["ret"] = t  # last assistant text wins == the return
    except Exception as e:
        s["error"] = (s["error"] + "; " if s["error"] else "") + \
                     f"transcript unreadable: {e.__class__.__name__}"
    return s


# ---------------------------------------------------------------- grouping (the point)

REPO_MARK = "claude-foundational-layer/"


def repo_rel(p):
    """Collapse every spelling of a repo file to one repo-relative key.

    Returns cite the same file three ways -- absolute Drive path, repo-relative, and a truncated
    middle fragment. Left alone they count as three different files, which fragments the
    document-frequency statistics and makes hub detection under-fire: `wiki/index.md` looked rare
    while actually being touched by most returns.
    """
    p = norm_key(p)
    i = p.rfind(REPO_MARK)
    if i != -1:
        p = p[i + len(REPO_MARK):]
    # a leading fragment of the repo path that survived truncation ("layer/claude-foundational-…")
    p = re.sub(r"^(?:[\w.\-]*layer/)+", "", p)
    return p.lstrip("./")


def signature(s):
    """What this return is ABOUT, reduced to two comparable sets.

    `paths` is the strong signal -- two returns naming the same three files are about the same
    thing far more reliably than two returns using the same adjectives. `words` is the weak signal
    and is only ever used to corroborate.
    """
    blob = " ".join([s.get("description", ""), s.get("ret", "")[:6000]])
    paths = {repo_rel(p) for p in PATH_RE.findall(blob)}
    paths |= {repo_rel(p) for p in s.get("wrote", [])}
    paths = {p for p in paths if p and not p.endswith(".jsonl")}
    words = {w.lower() for w in WORD_RE.findall(blob)}
    words -= STOPWORDS
    return paths, words


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def drop_hub_paths(entries, max_doc_frac=0.20, min_docs=3):
    """Remove paths so common they carry no discriminating signal, and SAY which ones.

    The first real run produced a single 22-member cluster containing nearly every return. The
    cause was not a threshold: it was that `wiki/index.md` and `exchange/CARRIER.md` are touched by
    almost everything in this repo, so union-find chained unrelated returns together through hub
    files. This is the path analogue of a stopword list, and without it the grouping asserts that
    all work is one topic -- which is exactly the kind of always-fires signal this repo has learned
    to ignore.
    """
    # Document frequency is not estimable on a handful of returns: with 4 entries, a path in 3 of
    # them looks like a hub and is actually the signal. Below this population the correction is
    # worse than the problem, so it is not applied -- and that is a guard, not a silent skip.
    if len(entries) < 8:
        return set()
    df = Counter()
    for e in entries:
        for p in e["sig"][0]:
            df[p] += 1
    cutoff = max(min_docs, int(len(entries) * max_doc_frac))
    hubs = {p for p, c in df.items() if c >= cutoff}
    for e in entries:
        paths, words = e["sig"]
        e["sig"] = (paths - hubs, words)
    return hubs


def pair_sim(a, b):
    """Similarity of two returns, plus the sentence explaining it. 0.0 means unrelated.

    SIBLINGS OF ONE FAN-OUT ARE RELATED BY CONSTRUCTION, not by resemblance. `meta.json` records
    `parentAgentId`, so when one dispatch spawns five agents to answer one question five ways, that
    is a structural fact -- and it beats any lexical guess. Before this was used, five FBC frame
    agents from a single fan-out landed in three different clusters with unrelated returns mixed in,
    while the evidence that they were one family sat unread in a sidecar file.
    """
    pa_id = (a["sum"].get("parent_agent") or "") if isinstance(a.get("sum"), dict) else ""
    pb_id = (b["sum"].get("parent_agent") or "") if isinstance(b.get("sum"), dict) else ""
    if pa_id and pa_id == pb_id:
        return 1.0, f"siblings of one fan-out (parent `{pa_id[:6]}`) -- structural, not inferred"
    pa, wa = a["sig"]
    pb, wb = b["sig"]
    shared = pa & pb
    jw = jaccard(wa, wb)
    sim = min(1.0, 0.30 * len(shared) + jw)
    if not shared and jw < 0.20:
        return 0.0, ""
    bits = []
    if shared:
        bits.append(f"{len(shared)} shared path(s): " + ", ".join(sorted(shared)[:3]))
    if jw >= 0.10:
        bits.append(f"lexical {jw:.2f}")
    return sim, "; ".join(bits)


def group(entries, threshold=0.50):
    """AVERAGE-LINKAGE agglomerative clustering. Deliberately NOT union-find.

    The first real run put 22 of 49 returns in one cluster. Hub-path removal did not fix it and the
    thresholds were not the cause: **single-linkage union-find chains.** A is related to B, B to C,
    C to D, and transitivity swallows the session. A cluster that contains everything says nothing,
    and this repo has already learned to ignore signals whose steady state is "firing."

    Average linkage cannot chain: a candidate must be related to the group ON AVERAGE, not to one
    lucky member. Merging stops when the best available average similarity falls below threshold.
    Thresholds stay conservative -- a false group hides one return inside another's summary, a
    missed group only costs a duplicate line, so the asymmetry says under-group.
    """
    n = len(entries)
    sim = {}
    reasons = {}
    for i in range(n):
        for j in range(i + 1, n):
            s, why = pair_sim(entries[i], entries[j])
            if s > 0:
                sim[(i, j)] = s
                if why:
                    reasons[frozenset((i, j))] = why

    clusters = {i: [i] for i in range(n)}

    def avg(ca, cb):
        tot = sum(sim.get((min(x, y), max(x, y)), 0.0) for x in ca for y in cb)
        return tot / float(len(ca) * len(cb))

    while True:
        best, bs = None, threshold
        keys = list(clusters)
        for x in range(len(keys)):
            for y in range(x + 1, len(keys)):
                a, b = keys[x], keys[y]
                v = avg(clusters[a], clusters[b])
                if v >= bs:
                    best, bs = (a, b), v
        if not best:
            break
        a, b = best
        clusters[a] = clusters[a] + clusters.pop(b)

    return {k: sorted(v) for k, v in clusters.items()}, reasons


# ---------------------------------------------------------------- recommendation

def recommend(s, resolved):
    """A MECHANICAL rule, and the rule is printed next to its verdict.

    NEEDS-READ is the default and will be the answer most of the time. That is correct: the
    judgment of what is wiki-worthy stays with wiki-master. This function allocates reading
    effort; it does not decide content.
    """
    if not resolved:
        return "NEEDS-READ", "transcript unresolved -- cannot be dispositioned without finding it"
    if s.get("error"):
        return "NEEDS-READ", f"summary incomplete ({s['error']})"
    if s["turns"] == 0:
        return "SKIP", "zero parsable turns -- no return content exists"
    if not s["ret"]:
        return "NEEDS-READ", "no final assistant text found -- agent may have been interrupted"
    if s["commits"] or s["wrote"]:
        return "INGEST-CANDIDATE", (f"produced durable artifacts ({len(set(s['wrote']))} files"
                                    f"{', ' + str(s['commits']) + ' commit calls' if s['commits'] else ''})")
    if len(s["ret"]) < 400 and s["turns"] < 8:
        return "SKIP", f"short return ({len(s['ret'])} chars, {s['turns']} turns), no artifacts"
    return "NEEDS-READ", f"read-only return, {len(s['ret'])} chars of findings"


# ---------------------------------------------------------------- manifest

def esc(t, n=None):
    t = re.sub(r"\s+", " ", (t or "")).replace("|", "\\|").strip()
    return t[:n] + ("…" if n and len(t) > n else "") if n else t


def render(entries, groups, reasons, stats, now):
    L = []
    A = L.append
    A("---")
    A('title: "Routing-ledger drain manifest"')
    A("status: GENERATED — regenerated whole on every drain. Do not hand-edit; edit the ledger.")
    A("generator: scripts/audit/drain_routing_ledger.py")
    A(f"generated_utc: {now}")
    A("---")
    A("")
    A("# What this is, and what it is not")
    A("")
    A("The PENDING rows of `exchange/ROUTING-LEDGER.md`, resolved to transcripts, summarized, and "
      "**grouped**. It is a *triage manifest*: it says what exists and how much reading each item "
      "is worth. **It is not a wiki edit and it does not decide ingest-worthiness** — that "
      "judgment stays with wiki-master, which is the only wiki writer.")
    A("")
    A("Every recommendation below is produced by a mechanical rule that is printed beside it. "
      "`INGEST-CANDIDATE` means *this return produced durable artifacts*, which is a fact about "
      "the transcript — not a claim that the wiki should say so.")
    A("")
    A("## Run")
    A("")
    A(f"- ledger rows parsed: **{stats['rows']}**")
    A(f"- PENDING rows: **{stats['pending']}**")
    A(f"- collapsed by transcript key (same return, >1 row): **{stats['dupe_rows']}**")
    A(f"- distinct returns after collapse: **{len(entries)}**")
    A(f"- resolved to a transcript on disk: **{stats['resolved']}** "
      f"(unresolved: **{stats['unresolved']}**)")
    A(f"- grouped into **{stats['groups']}** topic clusters "
      f"(**{stats['in_multi']}** returns sit in a multi-member cluster)")
    A(f"- NEW since last drain: **{stats['new']}**  ·  already manifested: **{stats['seen']}**")
    A("")
    A(f"**Coverage watermark: {stats['live']} of {len(entries)} transcripts were modified within "
      f"5 minutes of this run — those agents were still writing.** Two drains a minute apart "
      f"produced different cluster counts for exactly this reason; the drainer itself is "
      f"deterministic (verified back-to-back, identical bodies). **A summary here is a snapshot of "
      f"a live file, not a closed record.** Re-drain after the session quiesces.")
    A("")
    if stats.get("hubs"):
        A(f"- ignored as hub paths (touched by >={stats['hub_pct']}% of returns, "
          f"no discriminating signal): "
          + ", ".join(f"`{h}`" for h in stats["hubs"][:8])
          + (f" +{len(stats['hubs'])-8} more" if len(stats["hubs"]) > 8 else ""))
        A("")
    A("## Clusters")
    A("")
    multi = [g for g in groups.values() if len(g) > 1]
    singles = [g for g in groups.values() if len(g) == 1]
    for gi, members in enumerate(sorted(multi, key=len, reverse=True), 1):
        A(f"### Cluster {gi} — {len(members)} returns")
        A("")
        pair_why = [w for k, w in reasons.items() if set(k) <= set(members)]
        for w in sorted(set(pair_why))[:4]:
            A(f"- grouped because: {w}")
        A("")
        A("| id6 | agent | brief | recommend | rule |")
        A("|---|---|---|---|---|")
        for i in members:
            e = entries[i]
            A(f"| `{e['id6']}` | {esc(e['sum']['agent_type'], 22)} | "
              f"{esc(e['sum']['description'] or e['label'], 60)} | **{e['rec']}** | {esc(e['why'], 70)} |")
        A("")
        A("> **Dedup note.** These returns cover overlapping ground. Read them together; a "
          "per-agent writer would have written this finding once per member.")
        A("")
    if not multi:
        A("*No multi-member clusters this run.*")
        A("")
    A("## Ungrouped returns")
    A("")
    A("| id6 | agent | brief | wrote | recommend | rule |")
    A("|---|---|---|---|---|---|")
    for members in singles:
        e = entries[members[0]]
        A(f"| `{e['id6']}` | {esc(e['sum']['agent_type'], 22)} | "
          f"{esc(e['sum']['description'] or e['label'], 54)} | {len(set(e['sum']['wrote']))} | "
          f"**{e['rec']}** | {esc(e['why'], 60)} |")
    A("")
    A("## Per-return detail")
    A("")
    for e in sorted(entries, key=lambda x: x["id6"]):
        s = e["sum"]
        A(f"### `{e['id6']}` — {s['agent_type'] or 'UNKNOWN agent type'}")
        A("")
        A(f"- transcript: `{e['path'] or 'UNRESOLVED'}`  ({e['how']})")
        A(f"- brief: {esc(s['description'] or e['label'], 200)}")
        A(f"- size: {s['bytes']:,} B · {s['turns']} turns · "
          f"tools: {', '.join(f'{k}×{v}' for k, v in s['tools'].most_common(5)) or 'none'}")
        if s["wrote"]:
            A(f"- wrote: {', '.join(sorted(set(s['wrote']))[:6])}"
              f"{' …' if len(set(s['wrote'])) > 6 else ''}")
        if s["commits"]:
            A(f"- git commit invocations: {s['commits']}")
        if s["error"]:
            A(f"- **incomplete**: {s['error']}")
        A(f"- recommend: **{e['rec']}** — {e['why']}")
        A("")
        if s["ret"]:
            A("<details><summary>return, first 900 chars</summary>")
            A("")
            A("```")
            A(s["ret"][:900].replace("```", "``'`"))
            A("```")
            A("")
            A("</details>")
            A("")
        else:
            A("*No final assistant text recovered.* **Absence here is uninformative** — it may mean "
              "the agent was interrupted, not that it returned nothing.")
            A("")
    A("---")
    A("")
    A("**Routing is not complete when this file is written.** Naming a return in a register does "
      "not route it — that trap was found by building the register (`ROUTING-LEDGER.md`, "
      "\"the self-reference trap\"). A return is ROUTED when an artifact *outside* the register "
      "family consumes its content. Append the ROUTED row to the ledger; never edit a prior row.")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- populate

def populate(root, idx, existing_rows, session=None):
    """Append a PENDING row for every on-disk transcript no ledger row resolves to.

    This is what the SubagentStop hook would have done at completion time. Doing it after the fact
    is strictly worse -- it can only see returns whose JSONL still exists -- and it is here so the
    drainer can be tested against real data before Jon pastes the hook stanza.
    """
    known = set()
    for r in existing_rows:
        p, _ = resolve(r, idx)
        if p:
            known.add(norm_key(p))
    sess, declined, all_sessions = pick_session(idx, session)
    if sess is None:
        print(f"[drain] --populate: session selector matched {declined} sessions, not 1. "
              f"NOTHING APPENDED. Pass --session <uuid-prefix>. "
              f"Available: {', '.join(sorted(s[:8] for s in all_sessions))}")
        return 0, ""
    print(f"[drain] --populate scope: session {sess[:8]} "
          f"({len(all_sessions.get(sess, []))} transcripts). "
          f"DECLINED {declined} other session(s) in this project — pass --session to widen.")

    new = []
    for aid, path in sorted(idx.items()):
        if session_of(path) != sess:
            continue
        if norm_key(path) in known:
            continue
        s = summarize(path)
        new.append((aid, path, s))
    if not new:
        return 0, ""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    block = ["", "", f"# Rows — backfilled by drain_routing_ledger.py --populate ({now})", "",
             "*The hook stanza is not installed, so these were added after the fact from "
             "transcripts still on disk. **This can only see returns whose JSONL survived** — it is "
             "not equivalent to capture at completion.*", "",
             "| closed_utc | parent6 | id6 | kind | role-slug | extract | disposition | routed_by |",
             "|---|---|---|---|---|---|---|---|"]
    for aid, path, s in new:
        label = esc(s["description"] or "UNKNOWN", 60)
        block.append(f"| {now} | backfill | {aid[:6]} | subagent | "
                     f"{esc(s['agent_type'] or 'UNKNOWN', 24)}, {label} | "
                     f"`{path.replace(chr(92), '/')}` | PENDING | - |")
    text = "\n".join(block) + "\n"
    with open(os.path.join(root, LEDGER), "a", encoding="utf-8") as fh:
        fh.write(text)
    return len(new), text


# ---------------------------------------------------------------- drain

def drain(root, roots=None, dry_run=False, do_populate=False, session=None):
    lpath = os.path.join(root, LEDGER)
    try:
        with open(lpath, encoding="utf-8", errors="replace") as fh:
            ledger_text = fh.read()
    except OSError as e:
        print(f"[drain] ledger unreadable ({e.__class__.__name__}) at {lpath} — "
              f"NOTHING DRAINED. That is the finding, not an empty queue.")
        return 0

    roots = roots or default_transcript_roots(root)
    idx = transcript_index(roots)
    rows = parse_ledger(ledger_text)

    if do_populate:
        n, _ = populate(root, idx, rows, session=session)
        print(f"[drain] --populate appended {n} PENDING row(s).")
        if n:
            with open(lpath, encoding="utf-8", errors="replace") as fh:
                ledger_text = fh.read()
            rows = parse_ledger(ledger_text)

    pending = [r for r in rows if is_pending(r)]

    entries, by_key, dupe_rows = [], {}, 0
    resolved_n = unresolved_n = 0
    for r in pending:
        path, how = resolve(r, idx)
        key = norm_key(path) if path else \
            f"id6:{clean_id6(r.get('id6',''))}|extract:{norm_key(r.get('extract',''))}"
        if key in by_key:
            dupe_rows += 1
            by_key[key]["rows"].append(r["_lineno"])
            continue
        s = summarize(path) if path else {
            "path": None, "bytes": 0, "turns": 0, "tools": Counter(), "wrote": [], "commits": 0,
            "brief": "", "ret": "", "agent_type": "", "description": r.get("role", ""),
            "error": "", "spawn_depth": None, "parent_agent": ""}
        rec, why = recommend(s, path)
        e = {"key": key, "id6": clean_id6(r.get("id6", "")) or (r.get("id6") or "?"),
             "path": path, "how": how, "sum": s, "rec": rec, "why": why,
             "label": r.get("role", ""), "rows": [r["_lineno"]], "sig": signature(s)}
        by_key[key] = e
        entries.append(e)
        if path:
            resolved_n += 1
        else:
            unresolved_n += 1

    HUB_FRAC = 0.20
    hubs = drop_hub_paths(entries, max_doc_frac=HUB_FRAC)
    groups, reasons = group(entries)
    in_multi = sum(len(g) for g in groups.values() if len(g) > 1)

    prev = {}
    spath = os.path.join(root, STATE)
    if os.path.isfile(spath):
        try:
            with open(spath, encoding="utf-8") as fh:
                prev = json.load(fh)
        except Exception:
            prev = {}
    seen_keys = set(prev.get("keys", []))
    new_n = sum(1 for e in entries if e["key"] not in seen_keys)

    import time
    live = 0
    for e in entries:
        try:
            if e["path"] and time.time() - os.path.getmtime(e["path"]) < 300:
                live += 1
        except OSError:
            pass

    stats = {"live": live, "rows": len(rows), "pending": len(pending), "dupe_rows": dupe_rows,
             "resolved": resolved_n, "unresolved": unresolved_n,
             "groups": len(groups), "in_multi": in_multi, "hubs": sorted(hubs), "hub_pct": int(HUB_FRAC * 100),
             "new": new_n, "seen": len(entries) - new_n}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = render(entries, groups, reasons, stats, now)

    if dry_run:
        print(out)
        return 0

    os.makedirs(os.path.join(root, OUT_DIR), exist_ok=True)
    with open(os.path.join(root, MANIFEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    with open(spath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"last_drain_utc": now, "keys": sorted(by_key.keys())}, fh, indent=1)

    print(f"[drain] {stats['pending']} PENDING → {len(entries)} distinct returns "
          f"({dupe_rows} row(s) collapsed as same transcript); "
          f"{resolved_n} resolved / {unresolved_n} unresolved; "
          f"{len(groups)} clusters, {in_multi} returns in multi-member clusters; "
          f"{new_n} new since last drain.")
    print(f"[drain] manifest → {MANIFEST}")
    rc = Counter(e["rec"] for e in entries)
    print("[drain] recommendations: " + ", ".join(f"{k}={v}" for k, v in rc.most_common()))
    return 0


# ---------------------------------------------------------------- self-test

def self_test():
    import shutil
    import tempfile
    cases = []
    tmp = tempfile.mkdtemp(prefix="drain-st-")
    try:
        os.makedirs(os.path.join(tmp, "exchange"))
        sub = os.path.join(tmp, "proj", "sess1", "subagents")
        os.makedirs(sub)

        def mk(aid, atype, desc, ret, wrote=None, turns=3):
            p = os.path.join(sub, f"agent-{aid}.jsonl")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"type": "user", "agentId": aid,
                                     "message": {"content": [{"type": "text", "text": desc}]}}) + "\n")
                for w in (wrote or []):
                    fh.write(json.dumps({"type": "assistant", "message": {"content": [
                        {"type": "tool_use", "name": "Write", "input": {"file_path": w}}]}}) + "\n")
                for _ in range(turns):
                    fh.write(json.dumps({"type": "assistant", "message": {"content": [
                        {"type": "text", "text": ret}]}}) + "\n")
            with open(os.path.join(sub, f"agent-{aid}.meta.json"), "w", encoding="utf-8") as fh:
                json.dump({"agentType": atype, "description": desc}, fh)
            return p

        long_a = ("The register audit script scripts/audit/index_counts.py reads only four of the "
                  "five registers; wiki/tracker/wayfinder-cfl.md is omitted from its glob so the "
                  "denominator excludes it entirely. " * 3)
        long_b = ("Independent finding: scripts/audit/index_counts.py enumerates registers by an "
                  "incomplete glob and therefore skips wiki/tracker/wayfinder-cfl.md, understating "
                  "the denominator. " * 3)
        long_c = ("Investigated the HVAC damper schedule and the vehicle maintenance log; nothing "
                  "here touches repository tooling whatsoever, purely a household matter. " * 3)
        pa = mk("aaaaaaaaaaaaaaaa1", "lint-checker", "register audit", long_a)
        pb = mk("bbbbbbbbbbbbbbbb2", "general-purpose", "register glob", long_b)
        pc = mk("cccccccccccccccc3", "explore", "home matters", long_c)
        pd = mk("dddddddddddddddd4", "wiki-executor", "wrote pages", long_a,
                wrote=["wiki/x.md", "wiki/y.md"])

        ledger = os.path.join(tmp, LEDGER)
        hdr = ("| closed_utc | parent6 | id6 | kind | role-slug | extract | disposition | routed_by |\n"
               "|---|---|---|---|---|---|---|---|\n")
        rows = hdr
        rows += f"| - | p | aaaaaa | subagent | lint | `{pa}` | PENDING | - |\n"
        rows += f"| - | p | bbbbbb | subagent | gp | `{pb}` | PENDING | - |\n"
        rows += f"| - | p | cccccc | subagent | ex | `{pc}` | PENDING | - |\n"
        rows += f"| - | p | dddddd | subagent | wk | `{pd}` | PENDING | - |\n"
        # SAME transcript, second notification -- the harness says this happens.
        rows += f"| - | p | aaaaaa | subagent | lint | `{pa.replace(os.sep, '/')}` | PENDING | - |\n"
        rows += f"| - | p | eeeeee | subagent | done | `{pa}` | ROUTED | some/artifact.md |\n"
        rows += "| - | p | ffffff | subagent | ghost | `nowhere/agent-x.jsonl` | PENDING | - |\n"
        with open(ledger, "w", encoding="utf-8") as fh:
            fh.write("prose that is not a table\n\n" + rows)

        parsed = parse_ledger(open(ledger, encoding="utf-8").read())
        cases.append(("parses every table row, skips prose+header", len(parsed) == 7))
        cases.append(("ROUTED row excluded from PENDING",
                      len([r for r in parsed if is_pending(r)]) == 6))

        roots = [os.path.join(tmp, "proj")]
        idx = transcript_index(roots)
        cases.append(("transcript index finds all 4 by id17", len(idx) == 4))

        drain(tmp, roots=roots)
        m1 = open(os.path.join(tmp, MANIFEST), encoding="utf-8").read()
        st1 = json.load(open(os.path.join(tmp, STATE), encoding="utf-8"))

        cases.append(("6 PENDING rows collapse to 5 distinct returns (dup transcript merged)",
                      "distinct returns after collapse: **5**" in m1))
        cases.append(("separator-different spelling of same path is ONE key",
                      len(st1["keys"]) == 5))
        cases.append(("unresolvable row surfaces as UNRESOLVED, not dropped",
                      "unresolved: **1**" in m1 and "ffffff" in m1))
        cases.append(("related returns grouped (a+b+d share paths)",
                      "Cluster 1 — 3 returns" in m1))
        cases.append(("NEGATIVE CONTROL: unrelated return NOT grouped",
                      "| `cccccc` |" in m1.split("## Ungrouped returns")[1]))
        # Asserted against the ROW, not the whole document: the word appears in the preamble, so
        # the loose version of this check passed while the drainer was returning zero entries.
        drow = [ln for ln in m1.splitlines() if ln.startswith("| `dddddd`")]
        crow = [ln for ln in m1.splitlines() if ln.startswith("| `cccccc`")]
        cases.append(("artifact-producing return's ROW says INGEST-CANDIDATE",
                      bool(drow) and all("INGEST-CANDIDATE" in ln for ln in drow)))
        cases.append(("NEGATIVE CONTROL: read-only return's ROW does NOT say INGEST-CANDIDATE",
                      bool(crow) and not any("INGEST-CANDIDATE" in ln for ln in crow)))

        # ---- IDEMPOTENCE, run twice.
        drain(tmp, roots=roots)
        m2 = open(os.path.join(tmp, MANIFEST), encoding="utf-8").read()
        st2 = json.load(open(os.path.join(tmp, STATE), encoding="utf-8"))
        # Two lines legitimately differ between runs: the generation timestamp and the
        # NEW-since-last-drain counter, which is a report ABOUT drain history. Everything that
        # constitutes the manifest's content must be byte-identical -- that is what "draining
        # twice must not double-ingest" means, and it is asserted on the substantive body, not
        # waved at with a whole-file diff that a volatile counter would defeat.
        body = lambda t: t.split("## Clusters", 1)[1]
        cases.append(("IDEMPOTENT: substantive body byte-identical on second drain",
                      body(m1) == body(m2) and len(body(m1)) > 500))
        strip = lambda t: re.sub(r"(generated_utc: \S+|NEW since last drain.*)", "", t)
        cases.append(("IDEMPOTENT: whole manifest identical modulo timestamp + new-counter",
                      strip(m1) == strip(m2)))
        cases.append(("NEGATIVE CONTROL: no entry duplicated on second drain",
                      m2.count("### `dddddd`") == 1 and m1.count("### `dddddd`") == 1))
        cases.append(("IDEMPOTENT: key set unchanged", st1["keys"] == st2["keys"]))
        cases.append(("second drain reports 0 new", "NEW since last drain: **0**" in m2))
        cases.append(("first drain reported 5 new", "NEW since last drain: **5**" in m1))

        # ---- populate is idempotent too
        n1, _ = populate(tmp, idx, parse_ledger(open(ledger, encoding="utf-8").read()))
        n2, _ = populate(tmp, idx, parse_ledger(open(ledger, encoding="utf-8").read()))
        cases.append(("populate adds nothing when all transcripts already rowed",
                      n1 == 0 and n2 == 0))

        # ---- REGRESSION: populate must not sweep every session in the project.
        # The first real --populate run appended 302 rows across all historical sessions when one
        # session's returns were asked for. Two sessions, one un-rowed transcript each.
        sub2 = os.path.join(tmp, "proj", "sess2", "subagents")
        os.makedirs(sub2)
        # Ids must differ in the FIRST SIX chars -- the ledger's id6 column is all the assertion
        # can see, and a shared prefix makes the discriminating half of the test unfalsifiable.
        old_id, new_id = "1111111111111111a", "2222222222222222b"
        for sd, aid in ((sub, old_id), (sub2, new_id)):
            with open(os.path.join(sd, f"agent-{aid}.jsonl"), "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"type": "assistant",
                                     "message": {"content": [{"type": "text", "text": "hi"}]}}) + "\n")
        os.utime(os.path.join(sub2, f"agent-{new_id}.jsonl"), (2 ** 31, 2 ** 31))
        idx2 = transcript_index(roots)
        n3, txt3 = populate(tmp, idx2, parse_ledger(open(ledger, encoding="utf-8").read()))
        cases.append(("populate scopes to ONE session, not all (regression: 302-row sweep)",
                      n3 == 1))
        cases.append(("populate picked the session holding the newest transcript",
                      new_id[:6] in txt3 and old_id[:6] not in txt3))
        n4, _ = populate(tmp, transcript_index(roots),
                         parse_ledger(open(ledger, encoding="utf-8").read()))
        cases.append(("populate idempotent: re-run adds nothing", n4 == 0))
        n5, txt5 = populate(tmp, idx2, parse_ledger(open(ledger, encoding="utf-8").read()),
                            session="sess1")
        cases.append(("--session selects the other session explicitly",
                      n5 == 1 and old_id[:6] in txt5))

        # ---- never writes the wiki
        wiki_touched = os.path.exists(os.path.join(tmp, "wiki"))
        cases.append(("NEGATIVE CONTROL: no wiki/ path created or written", not wiki_touched))

        # ---- garbage ledger, still exit 0
        with open(ledger, "w", encoding="utf-8") as fh:
            fh.write("\x00\x01 not a ledger | | | broken\n| a | b |\n")
        cases.append(("garbage ledger → exit 0, no crash", drain(tmp, roots=roots) == 0))
        missing = os.path.join(tmp, "nope")
        cases.append(("missing ledger → exit 0, says NOTHING DRAINED",
                      drain(missing, roots=roots) == 0))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n=== SELF-TEST ===")
    bad = 0
    for name, ok in cases:
        bad += 0 if ok else 1
        print(f"  {name:<62} : {'PASS' if ok else 'FAIL'}")
    print(f"\nRESULT: {'PASS' if not bad else 'FAIL'} — {len(cases)-bad}/{len(cases)}")
    return 0 if not bad else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sess = None
    if "--session" in sys.argv:
        i = sys.argv.index("--session")
        if i + 1 < len(sys.argv):
            sess = sys.argv[i + 1]
    try:
        return drain(repo_root(),
                     dry_run="--dry-run" in sys.argv,
                     do_populate="--populate" in sys.argv,
                     session=sess)
    except Exception as e:
        # Never block. An internal error is reported and swallowed, by the same argument that
        # keeps route_agent_return.py from ever halting a session.
        print(f"[drain] INTERNAL ERROR ({e.__class__.__name__}: {e}) — nothing drained. "
              f"Treat that as the finding.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
