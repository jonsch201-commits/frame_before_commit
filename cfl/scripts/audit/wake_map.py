#!/usr/bin/env python3
"""Write the wake map — the file a stopped session's successor provably walks.

WHY THIS EXISTS
---------------
On 2026-08-03 four build lanes hit the session limit mid-work. Nothing was lost, because
a human happened to be watching and committed every worktree by hand within minutes. That
is not a control. That is luck with a witness.

The deeper failure is subtler and it has fired repeatedly: **the record existed and was
unrouted.** The resume brief was written to `exchange/RESUME-...md` — a file a waking
session *might* read. The mirror's seven-step order lived in a subagent log, which a
waking session provably does NOT read. Ten of Jon's rulings that day arrived as mid-turn
messages into a subagent; main's own reminders said "no human input has been received"
the entire time.

So the rule this implements: **the wake map goes on the path the waking session provably
walks, and it names every unread return rather than assuming someone remembers.**

Jon, 2026-08-03: *"Ground truth is ensuring nothing is deleted by accident or lost by
accident."* And on why a checklist beats intent: *"Man forget. Checkbox not forget."*

WHAT IT WRITES
--------------
`exchange/WAKE.md` — single fixed path, overwritten every run, containing:
  - what branch/tree state existed at checkpoint time
  - every branch ahead of main with uncommitted or unmerged work
  - **every subagent return file, with whether it has been read**
  - the standing resume order, with the fallback rule inside it

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It does not commit, push, or edit `CLAUDE.md`. A checkpoint tool that mutates the
instructions it runs under is the wrong shape; the one-line pointer that makes `WAKE.md`
part of the cold-open path is a proposal for Jon, deposited alongside.

Usage:
    python scripts/audit/wake_map.py                 # write exchange/WAKE.md
    python scripts/audit/wake_map.py --dry-run       # print, write nothing
    python scripts/audit/wake_map.py --self-test

Exit: 0 on success, 2 if the repo state could not be read (never a silent pass).
"""
import argparse
import glob
import os
import re
import subprocess
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

WAKE = os.path.join("exchange", "WAKE.md")
STALE_ACTIONS = False

RESUME_ORDER = """\
0. **Wake checks.** `exchange_inbox.py` (both channels) · `git status` · `scan_midturn_messages.py`
   · `stranded_branches.py --against <branch you will merge into>`.
1. **Loss-proofing.** `cleanupPeriodDays` still 3650 · every branch pushed and reachable ·
   `~/.claude/image-cache/` swept into `raw/originals/` (pasted images are Jon input the
   corpus does not capture).
2. **Open the ratchet lane.** M5 traceability, the uncovered conversations, conformance,
   branch→ticket triage. **This route is never blocked and is where work falls back to.**
3. **Finish the WIP instruments** — sequential, not concurrent: clock → ledger → Jon-minutes.
4. **Build the three prototypes** — scoped gate, dev-promotion PR, session-date sentence.
5. **Weekend card**, mirror consult first.

**THE FALLBACK RULE, and it is the one that keeps work moving:** if a route raises a
blocker, deposit the question as a file *with a recommendation*, switch to step 2, and
keep going. **Never idle, and never stop merely because you have reached a good place to
report.**

Jon, 2026-08-03T16:00:24Z. PRIMARY (resurrected 2026-08-07) is a MID-TURN message to a
subagent, `type: user`, `isMeta: true` -- it is NOT in the main transcript, which is why
it had no citation for four days:
`~/.claude/projects/G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer/9e21da9b-.../subagents/agent-ad4f469d3bbc886f3.jsonl:110`

His words, whole, because the clause the artifact kept is the second half of a
conditional and the first half changes what it licenses:

> *"One note, their is a lot of work not all of it needs to be done in parallel. Shoudl
> consider hjelping the coordinator by giving it an order to its actions so long as this
> doesn't cause work to accidentally stop. If blocer questions hit one route, should
> continue with anather. ... Ground truth is ensuring nothing is deleted by accident or
> lost by accident. Continue as planned :)"*

So the rule is **ordering is fine; stopping is not** -- he ASKS for sequencing and only
forbids the stall. An "always parallel" reading is his words inverted.
"""


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


class _Returns(list):
    """A list of (agent_id, routed) that also remembers what it declined to count.

    Subclassed rather than returned as a tuple so every existing caller and the negative-control
    self-test (`== []`) keep working unchanged.
    """
    skipped_non_agent = ()


def resolve_session_dir(explicit):
    """Return (dir_or_None, provenance).

    **`None` means WE DID NOT LOOK. It must never render as "there is nothing there."**

    Every wake map generated without `--session-dir` printed *"(no subagent returns found for
    this session)"* — a confident negative from a tool that was never told where to look. That
    is this program's most-repeated defect class (the `ls`-instead-of-`find` false alarm, the
    non-recursive glob at `_su_close_summaries.py:57`, the `source_id:` field-name bug that
    produced a 29-session "permanently lost" registry), reproduced inside the instrument built
    to prevent it.

    The path is derivable: Claude Code exports `CLAUDE_CODE_SESSION_ID`, and task `.output`
    files live at `<temp>/claude/<repo-slug>/<session-id>/tasks/`. So derive it — and when it
    genuinely cannot be derived, say UNKNOWN and say why.

    An explicit `--session-dir` that does not exist is an ERROR, not a cue to fall back to the
    environment. The caller named a place; silently looking somewhere else would answer a
    question nobody asked.
    """
    if explicit:
        if os.path.isdir(explicit):
            return explicit, "given by --session-dir"
        return None, f"--session-dir was given but does not exist: {explicit}"

    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    if not sid:
        return None, "no --session-dir, and CLAUDE_CODE_SESSION_ID is unset"

    tmp = os.environ.get("TEMP") or os.environ.get("TMPDIR") or "/tmp"
    root = os.path.join(tmp, "claude")
    for cand in sorted(glob.glob(os.path.join(root, "*", sid, "tasks"))):
        if os.path.isdir(cand):
            return cand, f"derived from CLAUDE_CODE_SESSION_ID ({sid[:8]})"
    return None, (f"CLAUDE_CODE_SESSION_ID is set ({sid[:8]}) but no tasks directory exists "
                  f"under {root} — the session may simply have dispatched no subagents, which "
                  f"is still UNKNOWN rather than zero")


def subagent_returns(session_dir):
    """Every subagent task-output file, with whether its content was ROUTED anywhere.

    A return nobody has referenced is not 'reviewed and dismissed' — it is unrouted, and on
    2026-08-03 an unrouted consult held twelve of Jon's rulings, none of which reached the
    main thread as principal input.

    ROUTED, not READ — the distinction is deliberate and the first build got it wrong.

    v1 tested whether the agent id appeared in `exchange/`. It reported **12 of 12 UNREAD**
    on a session where most returns had been acted on in detail, because agent ids are
    internal handles that never appear in artifacts by convention. **A flag whose steady
    state is "alarming" carries no information** — the same cry-wolf shape as EMPTY-reported-
    as-FAILED, fixed in the extractor hours earlier, reproduced here within the hour.

    The honest signal is whether the return's *extracted transcript* is referenced by
    anything durable, because that IS the name artifacts use. Checked across `exchange/`,
    `wiki/intake-triage/`, and `skills/intake/`.

    **It remains a proxy and is labelled as one.** A routed return may still have been
    skimmed; an unrouted one may have been fully absorbed into work that never named it.
    It is a prompt to look, not a verdict.
    """
    out = _Returns()
    if not session_dir or not os.path.isdir(session_dir):
        return out

    # FILES THAT MERELY ENUMERATE RETURNS MUST NOT COUNT AS ROUTING THEM.
    #
    # Two self-referential traps, both live when this exclusion was added on 2026-08-06:
    #
    #   * `exchange/WAKE.md` is this script's own output and lists every unrouted id. Scanning it
    #     back in makes the map evidence for itself.
    #   * The SACU routing ledger lists every return's extract FILENAME. The moment it was
    #     deposited, this detector went from "28 of 30 unrouted" to "**All 19 routed**" — with no
    #     return actually considered by anyone. The ledger's own text says "naming in the ledger
    #     is not routing"; the detector could not tell, because naming is exactly what it measures.
    #
    # An index of the problem is not a solution to it. Excluded by name, and the exclusion is
    # listed rather than pattern-guessed so that adding a new register is a deliberate act.
    SELF_REFERENTIAL = ("WAKE.md",)
    SELF_REFERENTIAL_PREFIX = ("ROUTING-LEDGER",)

    corpus = ""
    for base in ("exchange", "wiki/intake-triage", "skills/intake"):
        for root, _, files in os.walk(base):
            for f in files:
                if not f.endswith(".md"):
                    continue
                if f in SELF_REFERENTIAL or f.startswith(SELF_REFERENTIAL_PREFIX):
                    continue
                try:
                    corpus += open(os.path.join(root, f), encoding="utf-8",
                                   errors="ignore").read()
                except OSError:
                    pass

    # Extract basenames for THIS session's subagents only.
    #
    # PERFORMANCE IS A CORRECTNESS PROPERTY HERE. v2 walked all 559 subagent extracts under
    # a Google-Drive-mounted path and took over two minutes. **A stop-guard that is too slow
    # to run at the wall does not run at the wall** — which is precisely when it matters. The
    # parent session id is derivable from session_dir, so the scan is one directory.
    parent6 = ""
    parts = [p for p in os.path.normpath(session_dir).split(os.sep) if p]
    for p in reversed(parts):
        if len(p) >= 8 and p.count("-") >= 4:      # a session UUID
            parent6 = p[:6]
            break

    extracts = []
    if parent6:
        sub_dir = os.path.join("raw", "transcripts", "claude-code", "subagents", parent6)
        try:
            extracts = [f for f in os.listdir(sub_dir) if f.endswith(".md")]
        except OSError:
            extracts = []

    # TWO POPULATIONS SHARE THIS DIRECTORY, AND COUNTING THEM TOGETHER INFLATES THE ALARM.
    #
    # `tasks/*.output` holds BOTH subagent returns and Bash background-task outputs. They are
    # different namespaces: an agent id is 17 hex chars (`abfa7ecf4b17604ae`); a background-task
    # id is 9 mixed alphanumerics (`bqw8t8h0e`, `b4d6ijv62`) and its file is a command's stdout,
    # not a return. Measured 2026-08-06: 18 agent + 12 background = the "30 subagent returns"
    # this function used to report, and the headline "28 of 30 unrouted" that went to Jon twice.
    # **The honest figure was 16 of 18.** A background task cannot be routed or unrouted; it has
    # no transcript and nothing to consider.
    #
    # Skipped files are COUNTED AND REPORTED, never silently dropped — a filter that quietly
    # discards is the same defect as a scan that quietly finds nothing.
    skipped_non_agent = []
    for f in sorted(os.listdir(session_dir)):
        if not f.endswith(".output"):
            continue
        agent_id = f[:-len(".output")]
        if len(agent_id) < 16 or any(c not in "0123456789abcdef" for c in agent_id):
            skipped_non_agent.append(agent_id)
            continue
        a6 = agent_id[:6]
        # Three ways a return counts as routed, cheapest first.
        named = (f"-{a6}-" in corpus                      # short id, as reports cite it
                 or agent_id in corpus                    # full id, rare but decisive
                 or any(a6 in n and n[:-3] in corpus for n in extracts))
        out.append((agent_id, named))
    out.skipped_non_agent = skipped_non_agent
    return out


# --- WK-1 (2026-09-02): the actions file can be STALE and nothing said so ---
# Found 2026-09-02 21:3x: WAKE.md carried a 2026-08-17 action set (switchboard watcher) while the
# live map's newest amendment was 2026-09-02, and the main seat had told Jon "the WAKE file carries
# the resume order". It did not. Regeneration carried the old set forward faithfully -- durability
# without freshness. So: derive the newest "WAKE ACTION SET <date>" heading and the newest
# "## Amendment <date>" across LIVE maps; an action set older than the newest amendment is STALE,
# printed at the top of WAKE.md and returned as exit 3 (file still written; the alarm is in-band).
_ACTION_RE = re.compile(r"^##.*WAKE ACTION SET (\d{4}-\d{2}-\d{2})", re.M)
_AMEND_RE = re.compile(r"^## Amendment (\d{4}-\d{2}-\d{2})", re.M)


def live_maps(tracker_dir=os.path.join("wiki", "tracker")):
    """kind: wayfinder:map files whose frontmatter says status: LIVE -- derived, never hardcoded."""
    out = []
    try:
        names = sorted(os.listdir(tracker_dir))
    except OSError:
        return out
    for n in names:
        if not (n.startswith("wayfinder-") and n.endswith(".md")):
            continue
        try:
            head = open(os.path.join(tracker_dir, n), encoding="utf-8", errors="replace").read(4000)
        except OSError:
            continue
        fm = head.split("\n---", 2)[0] if head.startswith("---") else ""
        if "wayfinder:map" in fm and re.search(r"^status:\s*\"?LIVE", fm, re.M):
            out.append(n)
    return out


# --- 2026-09-03: regeneration silently dropped hand-written action sets, twice in one night ---
# `## ⛔ WAKE ACTION SET <date>` headings are meant to be SOURCED in exchange/WAKE-ACTIONS.md and
# only ever APPEAR in exchange/WAKE.md as the read-only rendering of that source (see the "inlined
# from a file this script does not own" block below). Twice on 2026-09-03 a set was instead typed
# straight into WAKE.md -- the DERIVED file -- and the next `wake_map.py` run overwrote it clean,
# 59 lines gone with no error. A regenerator that silently discards hand-written content is the
# same defect class as the field-name bug that produced a 29-session "permanently lost" registry:
# it did not fail: it succeeded at the wrong thing. So: before writing, diff the ACTION SET
# headings already in WAKE.md against WAKE-ACTIONS.md, and refuse to overwrite if any are orphaned.
_ACTION_HEADER_RE = re.compile(r"^##\s*⛔?\s*WAKE ACTION SET\s+(\d{4}-\d{2}-\d{2}(?:\s+[0-9x:]+)?)",
                                re.M)


def orphaned_action_sets(wake_text, actions_text):
    """Date-strings of `## WAKE ACTION SET <date>` headings present in `wake_text` (the file
    this script is about to overwrite) whose date-string does not appear anywhere in
    `actions_text` (exchange/WAKE-ACTIONS.md, the only file this script is allowed to source
    action sets from). A non-empty result means WAKE.md carries a hand-written set that was
    never moved to its source -- regenerating now would delete it silently.

    Sorted, de-duplicated, and returns [] (never None) so a caller can test truthiness directly.
    """
    wake_dates = _ACTION_HEADER_RE.findall(wake_text or "")
    actions_text = actions_text or ""
    return sorted({d for d in wake_dates if d not in actions_text})


def actions_staleness(actions_text, map_texts):
    """(newest_action_date, newest_amendment_date, stale). Missing dates -> None, stale=False."""
    a = sorted(_ACTION_RE.findall(actions_text or ""))
    m = sorted(d for t in map_texts for d in _AMEND_RE.findall(t or ""))
    na = a[-1] if a else None
    nm = m[-1] if m else None
    return na, nm, bool(na and nm and na < nm)


def sibling_sessions_with_returns(resolved):
    """WK-3: other `<temp>/claude/<slug>/<session>/tasks` dirs of ANY slug that hold agent-*.output.

    Returns [(dir, count, newest-mtime-iso)] newest first, excluding `resolved` itself. Read-only;
    any slug is scanned because the same repo has been driven from two cwds (G: and the N: clone)
    and the returns of one are invisible to a seat launched from the other.
    """
    import datetime as _dt
    out = []
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.normpath(resolved))))
    for cand in glob.glob(os.path.join(root, "*", "*", "tasks")):
        try:
            if os.path.normpath(cand) == os.path.normpath(resolved):
                continue
            # no size filter: a return's .output file is routinely 0 B while the real report
            # sits in the subagent JSONL (memory: subagent-final-reports-get-swallowed)
            # same discriminator as subagent_returns(): >=16 hex chars = agent id; the file is
            # `<agent_id>.output` with NO "agent-" prefix (first build globbed the prefix: 0 hits)
            files = [f for f in glob.glob(os.path.join(cand, "*.output"))
                     if len(os.path.basename(f)) >= 16 + len(".output")
                     and all(c in "0123456789abcdef" for c in os.path.basename(f)[:-len(".output")])]
            if not files:
                continue
            newest = max(os.path.getmtime(f) for f in files)
            out.append((cand, len(files),
                        _dt.datetime.fromtimestamp(newest).strftime("%Y-%m-%d %H:%M")))
        except (OSError, ValueError):
            # one unreadable dir must not silence the rest (first build did exactly that)
            continue
    out.sort(key=lambda t: t[2], reverse=True)
    return out


def build(session_dir):
    br = git("rev-parse", "--abbrev-ref", "HEAD")
    if br.returncode != 0:
        return None
    branch = br.stdout.strip()
    porcelain = [l for l in git("status", "--porcelain").stdout.splitlines()
                 if l and not l[3:].startswith("raw/")]
    unpushed = git("log", "--oneline", "@{u}..HEAD").stdout.strip().splitlines()
    ahead = git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin").stdout.split()

    # ONE git call, not one per branch.
    #
    # v2 ran `rev-list --count` per branch: 33 subprocesses against a Google-Drive-hosted
    # repo, ~90 seconds. Same lesson as the extract walk above and it is worth stating once:
    # **at the wall, a slow instrument is an absent instrument.** `ahead-behind` computes the
    # whole set server-side in a single traversal.
    live = []
    ab = git("for-each-ref", "--format=%(refname:short) %(ahead-behind:origin/main)",
             "refs/remotes/origin")
    if ab.returncode == 0 and ab.stdout.strip():
        for line in ab.stdout.splitlines():
            bits = line.split()
            if len(bits) < 2 or bits[0] in ("origin/HEAD", "origin/main", "origin/canonical"):
                continue
            try:
                n = int(bits[1])
            except ValueError:
                continue
            if n:
                live.append((n, bits[0][len("origin/"):]))
    else:
        # Fallback for git without ahead-behind. Slower, and says so rather than reporting 0.
        for b in ahead:
            if b in ("origin/HEAD", "origin/main", "origin/canonical"):
                continue
            c = git("rev-list", "--count", f"origin/main..{b}")
            if c.returncode == 0 and (c.stdout.strip() or "0") != "0":
                live.append((int(c.stdout.strip()), b[len("origin/"):]))
    live.sort(reverse=True)

    resolved, provenance = resolve_session_dir(session_dir)
    rets = subagent_returns(resolved)
    unread = [a for a, seen in rets if not seen]

    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    L = []
    L.append("---")
    L.append('title: "WAKE — read this first. Written at checkpoint, not after the fact."')
    L.append(f"written: {now}")
    L.append("status: LIVE — overwritten by scripts/audit/wake_map.py on every checkpoint")
    L.append("---\n")
    L.append("<!-- GENERATED. -->")
    L.append("<!-- Hand-written action sets go in exchange/WAKE-ACTIONS.md, never here. -->\n")
    L.append("# Wake map\n")
    L.append("**This file is regenerated. If its timestamp is old, the last session stopped "
             "without checkpointing — that is itself the first finding.**\n")
    # The read-chain must be real. Until 2026-08-06 this file never named the map, CLAUDE.md never
    # named this file, and the map asserted a chain that existed nowhere — so a session woke with
    # repo state and no role state. This line is the second link; CLAUDE.md carries the first.
    # WK-1: this line named `wayfinder-cfl.md` (SUPERSEDED since 2026-08-24) until 2026-09-02.
    _maps = live_maps()
    _maps_txt = ", ".join("`wiki/tracker/%s`" % m for m in _maps) if _maps else "UNKNOWN (no LIVE map derived)"
    L.append("**Role state lives in the LIVE wayfinder maps (derived: `status: LIVE`): " + _maps_txt +
             ". Resume at the newest `## Amendment` of the one whose scope matches your directive.** "
             "This file is *repo* state; it tells you whether work is stranded, not what you were in the middle of.\n")
    # --- session-specific wake actions, INLINED from a file this script does not own ---
    # Found 2026-08-07: the 08-07 close hand-wrote a "FIRST TWO ACTIONS ON WAKE" block into
    # WAKE.md. The next checkpoint regenerated the file and the block vanished. It had survived
    # only because no checkpoint ran in between. A hand-written imperative inside a REGENERATED
    # file is not durable, and nothing reports its loss -- the same defect class as a pointer
    # with no imperative, one layer down.
    #
    # So the actions live in exchange/WAKE-ACTIONS.md, which this script READS and never writes.
    # Regeneration carries them forward instead of erasing them. An absent file emits nothing and
    # is the ordinary case, not an alarm.
    _wa = os.path.join("exchange", "WAKE-ACTIONS.md")
    try:
        _body = open(_wa, encoding="utf-8").read().strip()
    except OSError:
        _body = ""
    _map_texts = []
    for _m in live_maps():
        try:
            _map_texts.append(open(os.path.join("wiki", "tracker", _m), encoding="utf-8", errors="replace").read())
        except OSError:
            pass
    _na, _nm, _stale = actions_staleness(_body, _map_texts)
    global STALE_ACTIONS
    STALE_ACTIONS = _stale
    if _stale:
        L.append("## ⛔ WAKE-ACTIONS STALE: newest action set %s, newest live-map amendment %s. "
                 "The actions below predate the map. Read the map's newest amendment FIRST, then "
                 "write a new action set at the top of exchange/WAKE-ACTIONS.md.\n" % (_na, _nm))
    if _body:
        if _body.startswith("---"):
            _end = _body.find("\n---", 3)
            if _end != -1:
                _body = _body[_end + 4:].strip()
        L.append(_body + "\n")

    L.append(f"## State at checkpoint\n")
    L.append(f"- branch: `{branch}`")
    L.append(f"- working tree (excluding gitignored `raw/`): "
             f"**{len(porcelain)} changed**")
    L.append(f"- unpushed commits: **{len(unpushed)}**")
    L.append(f"- branches ahead of main: **{len(live)}**\n")

    if porcelain or unpushed:
        L.append("**UNCOMMITTED OR UNPUSHED WORK EXISTS.** Land it before anything else — "
                 "on 2026-08-03 four lanes died mid-build and only a watching human saved "
                 "them.\n")

    L.append("## Subagent returns — routed or not\n")
    if resolved is None:
        L.append(f"**UNKNOWN — this map DID NOT LOOK.** {provenance}.\n")
        L.append("This is not a report of zero returns. It is a report that the question was "
                 "never asked. Re-run with `--session-dir <path holding agent-*.output>`, or "
                 "from a session where `CLAUDE_CODE_SESSION_ID` is set.\n")
    elif not rets:
        L.append(f"*(looked in `{resolved}` — no subagent returns for this session)*\n")
        # WK-3 (2026-09-02 23:1x): a FRESH seat has no returns of its own, and until tonight this
        # branch let the previous seat's census (60 rows at HEAD c9dac2e4) vanish from WAKE.md
        # with nothing in its place. Zero-for-this-session is not zero-for-this-repo. Name the
        # sibling sessions that DO hold returns, labelled as ungraded, so the reader can re-run
        # with --session-dir against them instead of concluding nothing was ever dispatched.
        sibs = sibling_sessions_with_returns(resolved)
        if sibs:
            L.append("**Other sessions on this machine (any trunk, any cwd) hold subagent returns that this map did NOT "
                     "grade** (routed/unrouted is per-session; re-run with `--session-dir` to "
                     "grade one):\n")
            for d, n, newest in sibs[:5]:
                L.append(f"- `{d}` — {n} return(s), newest {newest}")
            L.append("")
    else:
        L.append("**ROUTED means some durable artifact names this return's transcript.** "
                 "It is a proxy, not a verdict — a routed return may still have been "
                 "skimmed, and an unrouted one may have been absorbed into work that never "
                 "named it. Treat UNROUTED as a prompt to look.\n")
        for agent_id, seen in rets:
            L.append(f"- {'routed  ' if seen else '**UNROUTED**'} — `{agent_id[:6]}`")
        L.append("")
        skipped = list(getattr(rets, "skipped_non_agent", ()))
        if skipped:
            L.append(f"*({len(skipped)} background-task output(s) in the same directory were "
                     f"NOT counted — they are command stdout, not agent returns, and have no "
                     f"transcript to route: {', '.join(sorted(skipped)[:6])}"
                     f"{'…' if len(skipped) > 6 else ''})*\n")
        if unread:
            L.append(f"**{len(unread)} of {len(rets)} unrouted.** On 2026-08-03 an unrouted "
                     "consult held twelve of Jon's rulings, none of which reached the main "
                     "thread as principal input. The defect is never that the record was "
                     "missing — it is that it was unrouted.\n")
        else:
            L.append(f"**All {len(rets)} routed.**\n")

    L.append("## Branches holding work\n")
    for n, name in live[:12]:
        L.append(f"- `{name}` — {n} ahead")
    if len(live) > 12:
        L.append(f"- *…and {len(live) - 12} more — run `stranded_branches.py`*")
    L.append("")
    L.append("## Resume order\n")
    L.append(RESUME_ORDER)
    return "\n".join(L)


def self_test():
    cases = []
    cases.append(("repo is readable", git("rev-parse", "HEAD").returncode == 0))
    body = build(None)
    cases.append(("builds a map with no session dir", bool(body)))
    # NEGATIVE CONTROL: the map must never claim a clean tree it did not check.
    cases.append(("map states its own denominators",
                  bool(body) and "branches ahead of main" in body
                  and "Subagent returns" in body))
    # A missing session dir must yield zero returns, not a crash and not a silent "all read".
    cases.append(("NEGATIVE CONTROL: absent session dir -> no returns claimed",
                  subagent_returns("does-not-exist-anywhere") == []))
    # THE DEFECT THIS FILE WAS BUILT WITH: "I did not look" rendered as "there is nothing there."
    # An explicit-but-absent --session-dir must resolve to None and must NOT quietly fall back
    # to the environment, or the tool answers a question the caller did not ask.
    _d, _why = resolve_session_dir("does-not-exist-anywhere")
    cases.append(("NEGATIVE CONTROL: bad --session-dir -> UNKNOWN, no env fallback",
                  _d is None and "does not exist" in _why))
    # And the rendered map must say UNKNOWN, never the empty-case sentence, when it did not look.
    _unlooked = build(None) if not os.environ.get("CLAUDE_CODE_SESSION_ID") else None
    cases.append(("NEGATIVE CONTROL: unlooked map says UNKNOWN, not zero",
                  _unlooked is None or "DID NOT LOOK" in _unlooked))
    # WK-1 fixtures: an 08-17 action set beside a 09-02 amendment is STALE; same-day is not;
    # a missing action set is not stale (absent file is the ordinary case).
    _stale = actions_staleness("## WAKE ACTION SET 2026-08-17 x", ["## Amendment 2026-09-02 y"])
    cases.append(("WK-1: older action set than map amendment -> STALE", _stale == ("2026-08-17", "2026-09-02", True)))
    _fresh = actions_staleness("## WAKE ACTION SET 2026-09-02 x\n## WAKE ACTION SET 2026-08-17 y",
                               ["## Amendment 2026-09-02 y", "## Amendment 2026-08-30 z"])
    cases.append(("WK-1: newest action set == newest amendment -> fresh", _fresh[2] is False))
    cases.append(("WK-1: no action set -> not stale, dates None",
                  actions_staleness("", ["## Amendment 2026-09-02"]) == (None, "2026-09-02", False)))
    _lm = live_maps()
    cases.append(("WK-1: live maps derived, superseded wayfinder-cfl.md excluded",
                  bool(_lm) and "wayfinder-cfl.md" not in _lm))
    # 2026-09-03: hand-written action sets in WAKE.md that never made it into WAKE-ACTIONS.md
    # must be DETECTED, not silently overwritten.
    _hand_written = "## ⛔ WAKE ACTION SET 2026-09-01 12:0x — HAND-WRITTEN, NEVER SOURCED\n"
    cases.append(("regen-guard: hand-written set absent from WAKE-ACTIONS.md -> flagged",
                  orphaned_action_sets(_hand_written, "") == ["2026-09-01 12:0x"]))
    _sourced = "## ⛔ WAKE ACTION SET 2026-09-02 21:4x — SOURCED, SAME TEXT\n"
    cases.append(("CONTROL: action set present verbatim in WAKE-ACTIONS.md -> not flagged",
                  orphaned_action_sets(_sourced, _sourced) == []))
    cases.append(("CONTROL: no action-set headings at all -> not flagged",
                  orphaned_action_sets("no headings here", "") == []))
    print("=== SELF-TEST (negative control) ===")
    bad = 0
    for name, ok in cases:
        bad += 0 if ok else 1
        print(f"  {name:<52} : {'PASS' if ok else 'FAIL'}")
    print(f"\nRESULT: {'PASS' if not bad else 'FAIL'} — {len(cases)-bad}/{len(cases)}")
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-dir", help="Path holding this session's agent-*.output files")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    body = build(a.session_dir)
    if body is None:
        print("ERROR: could not read repo state. An unreadable tree is UNKNOWN, not clean.",
              file=sys.stderr)
        return 2

    if a.dry_run:
        print(body)
        return 0

    # Refuse to overwrite a hand-written action set that was never moved to its source.
    try:
        existing_wake = open(WAKE, encoding="utf-8").read()
    except OSError:
        existing_wake = ""
    try:
        actions_now = open(os.path.join("exchange", "WAKE-ACTIONS.md"), encoding="utf-8").read()
    except OSError:
        actions_now = ""
    orphaned = orphaned_action_sets(existing_wake, actions_now)
    if orphaned:
        print("REFUSED: WAKE.md carries hand-written action set(s) %s absent from "
              "exchange/WAKE-ACTIONS.md; move them there first (source), then re-run"
              % ", ".join(orphaned), file=sys.stderr)
        return 4

    os.makedirs(os.path.dirname(WAKE), exist_ok=True)
    with open(WAKE, "w", encoding="utf-8") as fh:
        fh.write(body + "\n")
    print(f"wrote {WAKE}")
    if STALE_ACTIONS:
        print("WARNING: WAKE-ACTIONS.md is STALE relative to the live map (see top of WAKE.md)", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
