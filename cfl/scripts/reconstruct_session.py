#!/usr/bin/env python3
"""Reconstruct a Claude Code session whose JSONL is GONE, from the artifacts that survived it.

WHAT THIS IS, AND — MORE IMPORTANTLY — WHAT IT IS NOT
=====================================================
`cleanupPeriodDays` (default 30) deletes session JSONLs at startup, permanently, with no
Recycle Bin and no Anthropic recovery path. Dozens of Claude Code sessions in this program
are gone that way. But three things on `C:` outlive the JSONL:

  1. `~/.claude/history.jsonl`  — EVERY prompt Jon typed, with sessionId, epoch-ms
     timestamp, project path, and a `pastedContents` map. It survives the sweep.
  2. `~/.claude/plans/*.md`     — the assistant's structured plan at planning moments.
  3. `~/.claude/projects/*/memory/*.md` — the assistant's distilled conclusions.

This tool assembles those into one markdown file per session. **The result is a
RECONSTRUCTION, not a transcript, and the whole design goal is that no reader can
mistake it for one.** Concretely:

  - **Jon's turns are [TRANSCRIPT]-grade.** `history.jsonl` is a verbatim record of the
    text he submitted. That grade is earned and is stated per-turn.
  - **The assistant's side is ABSENT.** Not summarized, not inferred, not reconstructed
    from artifacts. Every single missing reply gets an explicit ABSENT marker in the
    timeline, because a silent gap between two of Jon's prompts is exactly the shape a
    reader's brain fills in on its own. Absence is written down so it cannot be imagined
    away.
  - **Artifacts are [ARTIFACT:mtime]-grade** — evidence that *something* was concluded
    near a moment in time. NEVER evidence of what was said, and never attributed to a
    turn as if it were a reply.

WHY NO `## Assistant` HEADER IS EVER EMITTED
--------------------------------------------
`scripts/audit/turn_index.py` — this repo's one authority on turn structure — counts any
line matching `^## Assistant$` as an assistant turn and hands that count to
`coverage_gap.py` and to every wiki citation anchor. Emitting placeholder `## Assistant`
headers would have made the file *look* well-formed while asserting, in the repo's own
canonical index, that N assistant turns exist. They do not. A reconstruction indexes as
Human-turns-only, and that is the honest reading: the file contains N things Jon said and
zero things the assistant said. The ABSENT markers are deliberately NOT headers so that
the index cannot be inflated by them.

MTIME IS A WEAK SIGNAL. THIS IS THE TOOL'S PRIMARY LIMITATION.
--------------------------------------------------------------
An artifact is matched to a session by asking whether its mtime falls inside the session's
prompt window. Every clause of that is weak, and the output says so in its own header, not
only here:

  - mtime is when a file was LAST WRITTEN, not when it was created. A memory file edited
    weeks later carries the later mtime and will match the wrong session — or, worse, will
    silently *fail* to match the session that actually created it.
  - A session window is [first prompt, last prompt]. Sessions resumed with `--resume` /
    `--continue` keep one sessionId across days, so the window can be enormous (the
    calibration fixture spans 10 days), and a wide window sweeps in artifacts that a
    different session wrote.
  - Concurrent sessions overlap. The header reports how many prompts from OTHER sessions
    fall inside the window, so the reader can size the ambiguity instead of assuming none.
  - Nothing here is a causal link. "Written during" is the only claim; "written because
    of" is never claimed and must not be read in.

PASTED CONTENT IS USUALLY NOT RECOVERABLE
-----------------------------------------
A `pastedContents` entry carries `content` only sometimes; otherwise it carries a
`contentHash` and nothing else. Measured on the whole history file (2026-07-27): 132
pasted items, 34 with retrievable content. The output distinguishes the two cases
explicitly rather than letting a hash-only paste read as an empty paste.

SAFETY
------
- `~/.claude/` is opened READ-ONLY. This tool never writes, moves, or modifies anything
  there. `history.jsonl` is the only copy of this material.
- Output lands in `raw/transcripts/reconstructed/`, which is gitignored. It is Jon's personal
  history. Commit the script; NEVER `git add -f` the output.

THE PRECONDITION: NEVER RECONSTRUCT A SESSION THAT ALREADY HAS AN EXTRACT
=========================================================================
This is the most valuable thing in the file, and it exists because the failure it prevents
very nearly happened on 2026-07-27. A dispatch named seven "permanently lost" sessions;
five of them had real extracts sitting in `raw/sessions/`. One reconstruction had already
been written before the stop arrived.

Why that is worse than doing nothing, in the herald-wiki coordinator's words:

    "Reconstructing a session that exists is not a wasted afternoon — it is a fabricated
     primary entering a corpus that grades provenance."

A reconstruction of a session that has a real transcript does not merely duplicate it. It
*competes* with it, carries a provenance grade that invites trust, and is exactly the kind
of artifact this program's `[TRANSCRIPT]` > `[THINKING-SUMMARY]` grading exists to keep out.

So the tool does not trust its caller. `assert_no_existing_extract()` runs before any
assembly and refuses (exit 3) if the corpus already holds the session. **There is no
override flag.** A session that looks partially extracted is a judgment call that belongs
to a person, not a flag that makes the alarm stop.

The root cause of the bad list is instructive and is designed against here:
`scripts/audit/cc_corpus_gap.py` read only `source_id:` from frontmatter, but 24 of 53
extracts declare `uuid:` instead. The key came back empty, a filename fallback produced the
literal string `"code-2"` for every `code-2026-*.md`, that matched no session, and the file
fell through to `lost`. The script was not finding losses; it was finding a field name.
This guard therefore reads **every** id-bearing key it has seen in the corpus
(`source_id`, `uuid`, `session_id`, `source_uuid`) AND matches on filename, and treats any
hit as disqualifying.

AND IT REFUSES TO RUN AGAINST A MISSING CORPUS
----------------------------------------------
A git worktree has no `raw/` — it is gitignored, so `git worktree add` produces a tree
without it. A guard that walks a non-existent corpus finds no extract and cheerfully
approves every reconstruction: the absence of the corpus is indistinguishable from the
absence of an extract. That is the same class of defect as the field-name bug, one level
up. So a missing corpus root is a hard error (exit 4), never an empty result.

Usage:
  reconstruct_session.py <session-id-or-prefix>            # write the reconstruction
  reconstruct_session.py <id> --dry-run                    # report what it WOULD assemble
  reconstruct_session.py <id> --check-corpus               # guard only: does an extract exist?
  reconstruct_session.py --list-absent                     # sessions in history with no JSONL
  reconstruct_session.py <id> --corpus-root <path>         # REQUIRED when raw/ is not beside the script
  reconstruct_session.py <id> --out-dir <path>             # override output directory
  reconstruct_session.py <id> --pad-hours 6                # widen the artifact window
  reconstruct_session.py <id> --all-projects               # do not restrict memory by project
  reconstruct_session.py --self-test                       # in-memory provenance fences
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    # stderr too, or the guard's refusal message mojibakes on a cp1252 console — and the
    # refusal is the one message that must be legible.
    sys.stderr.reconfigure(encoding="utf-8")

CLAUDE_HOME = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude"))
HISTORY = "history.jsonl"
PLANS_DIR = "plans"
PROJECTS_DIR = "projects"

# The one grade reserved for a real, captured assistant reply. It is defined here so the
# self-test can assert this module never emits it, rather than trusting a code reading.
FORBIDDEN_ASSISTANT_GRADES = ("[TRANSCRIPT", "[THINKING-SUMMARY")

# Trunks used by raw-file-standards.md. Only a confident mapping is asserted; anything
# else is 'unassigned' rather than a guess dressed as a fact.
PROJECT_TRUNKS = {
    "claude foundational layer": "fl",
    "claude-foundational-layer": "fl",
}


# --------------------------------------------------------------------------- reading

def read_history(claude_home):
    """Every history.jsonl record, parse-failures counted rather than swallowed.

    READ-ONLY. Returns (records, n_unparsable).
    """
    path = Path(claude_home) / HISTORY
    if not path.is_file():
        raise SystemExit(f"history.jsonl not found at {path} — nothing to reconstruct from.")
    rows, bad = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                bad += 1
                continue
            if "sessionId" in r and "timestamp" in r:
                rows.append(r)
            else:
                bad += 1
    return rows, bad


def resolve_session(rows, ident):
    """Match a full session id or an unambiguous prefix.

    An ambiguous prefix is an ERROR, never a silent pick-the-first: reconstructing the
    wrong session under the right id is the one failure that would be invisible in the
    output.
    """
    ident = ident.strip().lower()
    ids = sorted({r["sessionId"] for r in rows})
    exact = [s for s in ids if s.lower() == ident]
    if exact:
        return exact[0]
    pref = [s for s in ids if s.lower().startswith(ident)]
    if len(pref) == 1:
        return pref[0]
    if not pref:
        raise SystemExit(f"No session in history.jsonl matches '{ident}'.")
    raise SystemExit(f"'{ident}' is ambiguous — matches {len(pref)}: {', '.join(pref)}")


def jsonl_on_disk(claude_home):
    """Session ids that still have a JSONL somewhere under ~/.claude/projects/."""
    base = Path(claude_home) / PROJECTS_DIR
    out = set()
    if not base.is_dir():
        return out
    for p in base.glob("*/*.jsonl"):
        out.add(p.stem)
    return out


# ------------------------------------------------------------------ the precondition

# Every frontmatter key seen carrying a session id in this corpus. `source_id` is what
# raw-file-standards.md specifies and what convert-claude-code.py emits today; `uuid` and
# `session_id` are what the older `code-2026-*` extracts actually declare. Reading only the
# standard key is precisely the bug that produced a false loss registry — measured
# 2026-07-27: dba2c0bd's extract carries `uuid:` and `session_id:`, and no `source_id:`.
ID_KEYS = ("source_id", "uuid", "session_id", "source_uuid")
ID_KEY_RX = re.compile(r"^(" + "|".join(ID_KEYS) + r"):\s*(.+)$", re.M)
FRONTMATTER_BYTES = 4000


def find_existing_extracts(corpus_root, sid):
    """Every place in the corpus that may already hold this session.

    Returns (strong, weak, prior):
      strong — a frontmatter id key matches the full session uuid, and the file is NOT a
               reconstruction. This IS a real extract. Disqualifying.
      weak   — the 6-hex prefix appears in a filename but no frontmatter id matched. Could
               be an extract with unreadable frontmatter, or a different file that merely
               mentions the id (a subagent transcript named for an audit of it, say).
               Disqualifying.
      prior  — a file this tool itself wrote (`capture_state: RECONSTRUCTED-FROM-ARTIFACTS`
               / `not_a_transcript: true`). NOT disqualifying — it is overwritten.

    THE `prior` BUCKET IS A BUG FIX, AND THE BUG WAS THIS TOOL'S OWN THESIS FAILING ON
    ITSELF. First live run: the guard found the reconstruction it had written sixty seconds
    earlier and reported `EXTRACT (frontmatter id matches)` — i.e. the instrument built to
    stop a reconstruction being mistaken for a transcript mistook its own reconstruction for
    a transcript. Every id-bearing file looked alike to it because it read the id key and
    nothing else. A reconstruction declares what it is in `capture_state`; the guard now
    reads that declaration instead of assuming.

    strong and weak BOTH disqualify. That split exists so a human reading the refusal can
    tell "a real extract exists" from "something merely mentions this id" without the tool
    collapsing the distinction into one scary word. Failing closed on the weak case is
    deliberate: the cost of a needless refusal is a question; the cost of a false approval
    is a fabricated primary in a provenance-graded corpus.
    """
    root = Path(corpus_root)
    if not root.is_dir():
        # SystemExit(str) exits 1 and prints the string — it does NOT set an exit code, so
        # a caller checking for 4 would see 1 and a script branching on it would mis-route.
        # Print, then exit with the code.
        print(f"[REFUSED — exit 4] corpus root does not exist: {root}", file=sys.stderr)
        print("  A git worktree has NO raw/ (it is gitignored), so walking a missing corpus", file=sys.stderr)
        print("  would find no extract and approve every reconstruction — absence of the", file=sys.stderr)
        print("  corpus is indistinguishable from absence of an extract. Pass --corpus-root", file=sys.stderr)
        print("  pointing at the MAIN checkout's raw/ directory. This tool will not guess.", file=sys.stderr)
        raise SystemExit(4)
    sid_low = sid.lower()
    p6 = sid_low[:6]
    strong, weak, prior = [], [], []
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            p = Path(dirpath) / fn
            name_hit = p6 in fn.lower()
            fm_hit = False
            head = ""
            if fn.lower().endswith(".md"):
                try:
                    head = open(p, encoding="utf-8", errors="ignore").read(FRONTMATTER_BYTES)
                except Exception:
                    head = ""
                for m in ID_KEY_RX.finditer(head):
                    if sid_low in m.group(2).strip().lower():
                        fm_hit = True
                        break
            is_recon = ("capture_state: RECONSTRUCTED-FROM-ARTIFACTS" in head
                        or "not_a_transcript: true" in head)
            if fm_hit and is_recon:
                prior.append(str(p))
            elif fm_hit:
                strong.append(str(p))
            elif name_hit and is_recon:
                prior.append(str(p))
            elif name_hit:
                weak.append(str(p))
    return sorted(strong), sorted(weak), sorted(prior)


def assert_no_existing_extract(corpus_root, sid, quiet=False):
    """Hard precondition. Exits 3 if the corpus already holds this session. NO OVERRIDE.

    Deliberately un-bypassable: the whole point is that a caller with a bad list cannot
    make this stop complaining. A session that genuinely needs a reconstruction despite a
    partial extract is a decision for a person, and should arrive as an escalation with a
    reason, not as a flag someone added at 1am.
    """
    strong, weak, prior = find_existing_extracts(corpus_root, sid)
    if not strong and not weak:
        if not quiet:
            if prior:
                print(f"[guard] no extract for {sid[:8]}; {len(prior)} PRIOR RECONSTRUCTION(S) found "
                      f"— these are this tool's own output and will be overwritten:")
                for p in prior:
                    print(f"          {p}")
            print(f"[guard] no extract found for {sid[:8]} under {corpus_root} — reconstruction permitted")
        return
    print(f"[REFUSED — exit 3] session {sid} ALREADY HAS material in the corpus.", file=sys.stderr)
    print("", file=sys.stderr)
    for p in strong:
        print(f"  EXTRACT (frontmatter id matches): {p}", file=sys.stderr)
    for p in weak:
        print(f"  filename mentions {sid[:6]} (frontmatter did not match): {p}", file=sys.stderr)
    for p in prior:
        print(f"  (prior reconstruction, not an extract — would have been overwritten): {p}", file=sys.stderr)
    print("", file=sys.stderr)
    print("  Reconstructing a session that already has a transcript is not a wasted", file=sys.stderr)
    print("  afternoon — it is a fabricated primary entering a corpus that grades", file=sys.stderr)
    print("  provenance. It competes with the real record and carries a grade that", file=sys.stderr)
    print("  invites trust. There is no override flag; if a reconstruction is genuinely", file=sys.stderr)
    print("  wanted alongside a partial extract, escalate that as a decision.", file=sys.stderr)
    raise SystemExit(3)


# --------------------------------------------------------------------------- artifacts

def mangle_project(project_path):
    """Claude Code's own project-directory mangling: every non-alphanumeric -> '-'.

    Verified against the live tree, not assumed: 'G:\\My Drive\\Claude\\Claude Foundational
    Layer' is stored as 'G--My-Drive-Claude-Claude-Foundational-Layer'.
    """
    return re.sub(r"[^A-Za-z0-9]", "-", project_path)


def collect_artifacts(claude_home, projects, lo_ms, hi_ms, all_projects=False):
    """Plans and memory files whose mtime falls in [lo_ms, hi_ms].

    Returns a list of dicts with an explicit `scope` field recording HOW the match was
    made, because the two artifact classes are not equally attributable:

      - memory/  lives under a project directory, so a project-scoped match is a real
        (if still weak) constraint: same project AND same time window.
      - plans/   is a FLAT GLOBAL directory with no project association whatsoever. A
        plan can only ever be matched on time, so it is tagged 'project-ambiguous' and
        the output says as much on the line itself. Silently mixing the two classes
        would let the weaker evidence borrow the stronger one's credibility.
    """
    home = Path(claude_home)
    wanted_dirs = {mangle_project(p) for p in projects}
    found = []

    plans = home / PLANS_DIR
    if plans.is_dir():
        for p in sorted(plans.glob("*.md")):
            st = p.stat()
            ms = int(st.st_mtime * 1000)
            if lo_ms <= ms <= hi_ms:
                found.append({"path": p, "mtime_ms": ms, "kind": "plan",
                              "scope": "project-ambiguous (plans/ is a flat global dir)",
                              "bytes": st.st_size})

    projroot = home / PROJECTS_DIR
    if projroot.is_dir():
        for d in sorted(projroot.iterdir()):
            if not d.is_dir():
                continue
            in_scope = all_projects or d.name in wanted_dirs
            mem = d / "memory"
            if not mem.is_dir():
                continue
            for p in sorted(mem.glob("*.md")):
                st = p.stat()
                ms = int(st.st_mtime * 1000)
                if lo_ms <= ms <= hi_ms and in_scope:
                    found.append({"path": p, "mtime_ms": ms, "kind": "memory",
                                  "scope": ("project-matched" if not all_projects or d.name in wanted_dirs
                                            else "cross-project (--all-projects)"),
                                  "bytes": st.st_size, "project_dir": d.name})
    found.sort(key=lambda a: a["mtime_ms"])
    return found


# --------------------------------------------------------------------------- assembly

def ts(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0)


def fmt(ms):
    return ts(ms).strftime("%Y-%m-%d %H:%M:%S")


def trunk_for(projects):
    for p in projects:
        low = p.replace("\\", "/").lower()
        for key, trunk in PROJECT_TRUNKS.items():
            if key in low:
                return trunk
    return "unassigned"


def gather(rows, sid, claude_home, pad_hours=0.0, all_projects=False):
    """Everything needed to render or to dry-run report. Pure measurement, no formatting."""
    mine = sorted([r for r in rows if r["sessionId"] == sid], key=lambda r: r["timestamp"])
    if not mine:
        raise SystemExit(f"session {sid} has no prompts in history.jsonl")
    lo, hi = mine[0]["timestamp"], mine[-1]["timestamp"]
    pad = int(pad_hours * 3600 * 1000)
    projects = sorted({r.get("project", "") for r in mine if r.get("project")})

    pasted_total = pasted_with_content = 0
    for r in mine:
        for _k, v in (r.get("pastedContents") or {}).items():
            pasted_total += 1
            if isinstance(v, dict) and v.get("content"):
                pasted_with_content += 1

    foreign = [r for r in rows if r["sessionId"] != sid and lo <= r["timestamp"] <= hi]
    foreign_sessions = sorted({r["sessionId"] for r in foreign})

    arts = collect_artifacts(claude_home, projects, lo - pad, hi + pad, all_projects)

    return {
        "sid": sid, "prompts": mine, "lo": lo, "hi": hi, "pad_ms": pad,
        "projects": projects, "trunk": trunk_for(projects),
        "pasted_total": pasted_total, "pasted_with_content": pasted_with_content,
        "chars": sum(len(r.get("display", "")) for r in mine),
        "foreign_prompts": len(foreign), "foreign_sessions": foreign_sessions,
        "artifacts": arts,
        "span_hours": (hi - lo) / 3600000.0,
    }


def render(g, jsonl_present):
    """Build the markdown body. Every provenance claim in here is load-bearing."""
    sid = g["sid"]
    short = sid[:6]
    lines = []
    a = lines.append

    a(f"# RECONSTRUCTION — Claude Code session `{short}` — {ts(g['lo']):%Y-%m-%d}")
    a("")
    a("> ## THIS IS NOT A TRANSCRIPT.")
    a("> ")
    a("> This session's JSONL no longer exists. Nothing below was read from a recording of")
    a("> the conversation, because no recording survives. This file was assembled after the")
    a("> fact from artifacts that outlived it. Read every line with that in mind.")
    a("> ")
    a("> **PRESENT — and what it is worth:**")
    a("> ")
    a(f"> - **{len(g['prompts'])} prompts typed by Jon**, verbatim and in timestamp order,")
    a(">   from `~/.claude/history.jsonl`. These are `[TRANSCRIPT]`-grade: history.jsonl")
    a(">   records the text actually submitted. This is the only strong evidence in the file.")
    a(f"> - **{len(g['artifacts'])} artifacts** (plans / memory files) whose mtime falls inside")
    a(">   the session window, placed at the point in the timeline where they were written.")
    a(">   These are `[ARTIFACT:mtime]`-grade — evidence that *something* was concluded near")
    a(">   a moment, never evidence of what was said.")
    a("> ")
    a("> **ABSENT — and it is not recoverable:**")
    a("> ")
    a("> - **Every assistant reply.** All of them. Not summarized, not inferred, not")
    a(">   reconstructed. Each missing reply is marked in place below. A marker means the")
    a(">   reply is gone, NOT that the assistant said nothing.")
    a("> - Tool calls, tool results, thinking blocks, file edits, compaction boundaries,")
    a(">   and any prompt Jon sent by a route history.jsonl does not record.")
    a("> - Whether the prompts below are even contiguous. A deleted or unrecorded prompt")
    a(">   leaves no trace here, so the sequence may have holes it cannot show you.")
    a("> ")
    a("> **THE ARTIFACT TIMESTAMPS ARE A WEAK SIGNAL. Specifically:**")
    a("> ")
    a("> - An mtime is when a file was **last written**, not when it was created. A file")
    a(">   edited later carries the later time — so an artifact this session produced may be")
    a(">   missing below, and an artifact from a different session may be listed below.")
    a(f"> - The session window spans **{g['span_hours']:.1f} hours**"
      f"{' — wide, because a resumed session keeps one id across days' if g['span_hours'] > 24 else ''}.")
    a(">   The wider the window, the more it sweeps in.")
    if g["foreign_prompts"]:
        a(f"> - **{g['foreign_prompts']} prompts from {len(g['foreign_sessions'])} OTHER session(s)**")
        a(f">   fall inside this window (`{', '.join(s[:6] for s in g['foreign_sessions'])}`).")
        a(">   Those sessions were running in the same period and mtime cannot tell you which")
        a(">   session wrote a given artifact. Attribution below is *temporal co-occurrence only*.")
    else:
        a("> - No prompts from other sessions fall inside this window **in history.jsonl**.")
        a(">   That is not proof no other session ran — only that none is recorded here.")
    a("> ")
    a("> **Placement is chronological, not causal.** An artifact appearing after a prompt")
    a("> means it was written after that prompt. It does not mean it was written *because*")
    a("> of it.")
    a("")
    a("---")
    a("")
    a("## Reconstruction basis")
    a("")
    a(f"- Session id: `{sid}`")
    a(f"- JSONL on disk at reconstruction time: **{'YES — prefer the JSONL over this file' if jsonl_present else 'NO (deleted)'}**")
    a(f"- Window: `{fmt(g['lo'])}` -> `{fmt(g['hi'])}` (local time; history stores epoch-ms)")
    if g["pad_ms"]:
        a(f"- Artifact window padded by {g['pad_ms']/3600000:.1f}h on each side (`--pad-hours`)")
    a(f"- Project path(s) recorded on the prompts: {', '.join('`'+p+'`' for p in g['projects']) or '(none)'}")
    a(f"- Prompts: {len(g['prompts'])}  |  characters typed: {g['chars']}")
    a(f"- Pasted items: {g['pasted_total']} total, **{g['pasted_with_content']} with retrievable content** "
      f"({g['pasted_total'] - g['pasted_with_content']} carry a contentHash only — the pasted text itself is gone)")
    a(f"- Artifacts matched: {len(g['artifacts'])} "
      f"({sum(1 for x in g['artifacts'] if x['kind']=='plan')} plan, "
      f"{sum(1 for x in g['artifacts'] if x['kind']=='memory')} memory)")
    a("")
    a("---")
    a("")
    a("## Timeline")
    a("")
    a("*Jon's turns are verbatim. Between them, the assistant's replies are gone and are")
    a("marked as such. Artifacts are interleaved at their mtime.*")
    a("")

    arts = list(g["artifacts"])
    ai = 0
    prompts = g["prompts"]

    def flush_artifacts(until_ms):
        nonlocal ai
        while ai < len(arts) and arts[ai]["mtime_ms"] <= until_ms:
            art = arts[ai]
            ai += 1
            a(f"### [ARTIFACT:{fmt(art['mtime_ms'])}] — {art['kind']}: `{art['path'].name}`")
            a("")
            a(f"- Path: `{art['path']}`")
            a(f"- mtime: `{fmt(art['mtime_ms'])}` — **last-write time, not creation time**")
            a(f"- Size: {art['bytes']} bytes")
            a(f"- Attribution: {art['scope']}")
            a("- Grade: `[ARTIFACT:mtime]`. Evidence that something was concluded around this")
            a("  time. NOT a record of anything the assistant said, and NOT a reply to the")
            a("  prompt above it. Content is not inlined — read the file itself.")
            a("")

    for i, r in enumerate(prompts, start=1):
        flush_artifacts(r["timestamp"])
        a("## Human")
        a("")
        a(f"*Prompt {i} of {len(prompts)} — `{fmt(r['timestamp'])}` — "
          f"`[TRANSCRIPT]` verbatim from history.jsonl*")
        a("")
        a(r.get("display", ""))
        a("")
        pc = r.get("pastedContents") or {}
        for key in sorted(pc, key=lambda k: (len(k), k)):
            v = pc[key] if isinstance(pc[key], dict) else {}
            a(f"**[PASTED ITEM {key} — attached by Jon, not typed]** "
              f"(type: `{v.get('type','?')}`, id: `{v.get('id','?')}`)")
            a("")
            if v.get("content"):
                a("```text")
                a(str(v["content"]))
                a("```")
            else:
                a(f"*Content NOT RECOVERABLE — history.jsonl kept only a contentHash "
                  f"(`{str(v.get('contentHash',''))[:16]}...`). Something was pasted here and its "
                  f"text is gone. This is not an empty paste.*")
            a("")
        a("*[ASSISTANT REPLY ABSENT — the assistant answered this prompt and no record of the")
        a("answer survives. Not summarized, not inferred, not reconstructed. This gap is a")
        a("deletion, not a silence.]*")
        a("")
        a("---")
        a("")

    if ai < len(arts):
        a("### Artifacts written after the last recorded prompt")
        a("")
        flush_artifacts(float("inf"))

    a("## End of reconstruction")
    a("")
    a(f"{len(prompts)} prompts recovered. {len(prompts)} assistant replies missing. "
      f"{len(g['artifacts'])} artifacts co-occurring by mtime.")
    a("")
    return "\n".join(lines) + "\n"


def frontmatter(g, body, jsonl_present):
    """Frontmatter modelled on raw-file-standards.md as emitted by convert-claude-code.py
    (source_id / title / date / extraction_date / source_type / extraction_mode /
    extraction_completeness / thinking_blocks / compaction_boundaries / char_count /
    raw_sha256 / project), so existing readers do not choke — PLUS the reconstruction
    fields. `capture_state` is the field a future instrument should filter on: it is the
    one flag that separates this class of file from a captured transcript, and it is
    deliberately loud.
    """
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    fm = [
        "---",
        f"source_id: {g['sid']}",
        f"title: RECONSTRUCTION — Claude Code session {g['sid'][:6]} (user turns only, assistant side absent)",
        f"date: {ts(g['lo']):%Y-%m-%d}",
        f"extraction_date: {dt.datetime.now():%Y-%m-%d}",
        "source_type: session",
        "extraction_mode: reconstruct-from-artifacts",
        "capture_state: RECONSTRUCTED-FROM-ARTIFACTS",
        "extraction_completeness: PARTIAL — Jon's prompts only; EVERY assistant turn is ABSENT",
        "thinking_blocks: none — no JSONL exists to hold any",
        "compaction_boundaries: unknown — not recorded in history.jsonl",
        f"char_count: {len(body)}",
        f"raw_sha256: {sha}",
        f"project: {g['trunk']}",
        "provenance_grades: |",
        "  user turns   -> [TRANSCRIPT]      (history.jsonl is verbatim submitted text)",
        "  artifacts    -> [ARTIFACT:mtime]  (WEAK: last-write time, not creation; not causal)",
        "  assistant    -> ABSENT            (no grade — nothing survives to grade)",
        f"reconstruction_sources: history.jsonl ({len(g['prompts'])} prompts); "
        f"{sum(1 for x in g['artifacts'] if x['kind']=='plan')} plan(s); "
        f"{sum(1 for x in g['artifacts'] if x['kind']=='memory')} memory file(s)",
        f"session_window: {fmt(g['lo'])} -> {fmt(g['hi'])}",
        f"window_span_hours: {g['span_hours']:.1f}",
        f"foreign_prompts_in_window: {g['foreign_prompts']}",
        f"foreign_sessions_in_window: {', '.join(s[:6] for s in g['foreign_sessions']) or 'none recorded'}",
        f"pasted_items: {g['pasted_total']} ({g['pasted_with_content']} recoverable)",
        f"jsonl_present_at_reconstruction: {'yes' if jsonl_present else 'no'}",
        "not_a_transcript: true",
        "---",
        "",
    ]
    return "\n".join(fm)


def out_name(g):
    """`recon-` prefix so the class is legible at a glance; the 6-hex id sits before the
    slug so `coverage_gap.py`'s HEX6 grouping picks the session id and not a hex-looking
    word later in the name.

    NO PROMPT-DERIVED SLUG. convert-claude-code.py titles a file from Jon's first prompt;
    doing that here would push personal prompt text into a filename that gets quoted in
    reports and PR bodies. The class name is fixed instead.
    """
    return f"recon-{ts(g['lo']):%Y-%m-%d}-{g['sid'][:6]}-reconstructed.md"


# --------------------------------------------------------------------------- self-test

def self_test():
    """Provenance fences, asserted rather than eyeballed."""
    fake = [
        {"sessionId": "aaaaaaaa-1", "timestamp": 1700000000000, "display": "first",
         "project": "G:\\proj", "pastedContents": {}},
        {"sessionId": "aaaaaaaa-1", "timestamp": 1700000600000, "display": "second",
         "project": "G:\\proj",
         "pastedContents": {"1": {"id": 1, "type": "text", "contentHash": "deadbeefcafe"}}},
        {"sessionId": "bbbbbbbb-2", "timestamp": 1700000300000, "display": "other session",
         "project": "G:\\proj", "pastedContents": {}},
    ]
    g = gather(fake, "aaaaaaaa-1", CLAUDE_HOME)
    body = render(g, jsonl_present=False)
    fm = frontmatter(g, body, jsonl_present=False)
    doc = fm + body

    assert "## Assistant" not in doc, "emitted an ## Assistant header — would inflate turn_index"
    assert "## Compaction Boundary" not in doc and "## Dispatch" not in doc
    assert doc.count("## Human") == 2, f"expected 2 Human turns, got {doc.count('## Human')}"
    assert doc.count("ASSISTANT REPLY ABSENT") == 2, "every prompt needs an explicit absence marker"
    # the reserved grades must never appear attached to assistant-side content
    for line in doc.splitlines():
        if any(bad in line for bad in FORBIDDEN_ASSISTANT_GRADES):
            assert "user turns" in line or "[TRANSCRIPT]` verbatim from history.jsonl" in line \
                or "history.jsonl is verbatim" in line or "TRANSCRIPT]`-grade" in line \
                or "PRESENT" in line or "NOT A TRANSCRIPT" in line or "not_a_transcript" in line, \
                f"reserved grade on a non-Jon line: {line[:90]}"
    assert "capture_state: RECONSTRUCTED-FROM-ARTIFACTS" in doc
    assert g["foreign_prompts"] == 1, "foreign-session overlap not detected"
    assert g["pasted_total"] == 1 and g["pasted_with_content"] == 0
    assert "NOT RECOVERABLE" in doc, "hash-only paste must be flagged as unrecoverable"
    assert "mangle" not in doc
    assert mangle_project("G:\\My Drive\\Claude\\Claude Foundational Layer") == \
        "G--My-Drive-Claude-Claude-Foundational-Layer"

    # ---- the precondition, asserted against the exact bug that motivated it ----
    import tempfile as _tf
    corpus = Path(_tf.mkdtemp()) / "raw"
    (corpus / "sessions" / "claude-code").mkdir(parents=True)
    # frontmatter declares `uuid:` and NOT `source_id:` — the real shape of 24 of 53
    # extracts, and the shape cc_corpus_gap.py was blind to.
    (corpus / "sessions" / "claude-code" / "code-2026-05-31-abc123-something.md").write_text(
        "---\nuuid: abc12345-0000-0000-0000-000000000000\nsession_id: abc12345-0000-0000-0000-000000000000\n---\n\n## Human\n\nhi\n",
        encoding="utf-8")
    try:
        assert_no_existing_extract(corpus, "abc12345-0000-0000-0000-000000000000")
        raise AssertionError("guard did NOT refuse a session whose extract declares `uuid:` not `source_id:`")
    except SystemExit as e:
        assert e.code == 3, f"expected exit 3, got {e.code}"
    # a clear session passes
    assert_no_existing_extract(corpus, "ffffffff-0000-0000-0000-000000000000", quiet=True)

    # A PRIOR RECONSTRUCTION must NOT be mistaken for an extract. This regression is the
    # tool's own thesis applied to itself: the first live run had the guard report its own
    # output as `EXTRACT (frontmatter id matches)`.
    recon_dir = corpus / "sessions" / "reconstructed"
    recon_dir.mkdir(parents=True)
    (recon_dir / "recon-2026-01-01-eeeeee-reconstructed.md").write_text(
        "---\nsource_id: eeeeeeee-0000-0000-0000-000000000000\n"
        "capture_state: RECONSTRUCTED-FROM-ARTIFACTS\nnot_a_transcript: true\n---\n\n## Human\n\nhi\n",
        encoding="utf-8")
    s2, w2, p2 = find_existing_extracts(corpus, "eeeeeeee-0000-0000-0000-000000000000")
    assert not s2 and not w2 and len(p2) == 1, \
        f"prior reconstruction misclassified: strong={s2} weak={w2} prior={p2}"
    assert_no_existing_extract(corpus, "eeeeeeee-0000-0000-0000-000000000000", quiet=True)
    # a MISSING corpus must be a hard error, never an empty (approving) result
    try:
        assert_no_existing_extract(corpus / "does-not-exist", "ffffffff-0000-0000-0000-000000000000")
        raise AssertionError("guard approved against a MISSING corpus — the worktree failure mode")
    except SystemExit as e:
        assert e.code == 4, f"expected exit 4 for missing corpus, got {e.code}"

    # turn_index must read it as Human-only
    sys.path.insert(0, str(Path(__file__).resolve().parent / "audit"))
    try:
        from turn_index import index as turn_index
        import tempfile
        tmp = Path(tempfile.mkdtemp()) / out_name(g)
        tmp.write_text(doc, encoding="utf-8")
        idx = turn_index(str(tmp))
        assert idx["turn_count"] == 2, f"turn_index saw {idx['turn_count']} turns, expected 2"
        assert {t["role"] for t in idx["turns"]} == {"H"}, "turn_index saw a non-Human role"
        print(f"self-test OK — turn_index: {idx['turn_count']} turns, "
              f"roles {sorted({t['role'] for t in idx['turns']})}, style {idx['header_style']}")
    except ImportError:
        print("self-test OK (turn_index not importable from here — provenance fences still passed)")


# --------------------------------------------------------------------------- cli

def cmd_list_absent(rows, claude_home):
    on_disk = jsonl_on_disk(claude_home)
    by = {}
    for r in rows:
        by.setdefault(r["sessionId"], []).append(r)
    print(f"{'session':10} {'prompts':>7} {'chars':>8} {'span_h':>7}  window")
    absent = 0
    for sid, rs in sorted(by.items(), key=lambda kv: min(x["timestamp"] for x in kv[1])):
        if sid in on_disk:
            continue
        absent += 1
        lo = min(x["timestamp"] for x in rs)
        hi = max(x["timestamp"] for x in rs)
        print(f"{sid[:8]:10} {len(rs):>7} {sum(len(x.get('display','')) for x in rs):>8} "
              f"{(hi-lo)/3600000:>7.1f}  {fmt(lo)} -> {fmt(hi)}")
    print(f"\n{absent} session(s) in history.jsonl have NO JSONL under {Path(claude_home)/PROJECTS_DIR}.")
    print("That is 'no JSONL in the live projects tree' — archives elsewhere are not checked here.")


def main():
    ap = argparse.ArgumentParser(description="Reconstruct a JSONL-less Claude Code session from surviving artifacts.")
    ap.add_argument("session", nargs="?", help="session id or unambiguous prefix")
    ap.add_argument("--claude-home", default=str(CLAUDE_HOME), help="default ~/.claude (READ-ONLY)")
    ap.add_argument("--corpus-root", default=None,
                    help="the MAIN checkout's raw/ dir. Default <repo>/raw. Must exist — a worktree has none.")
    ap.add_argument("--out-dir", default=None,
                    help="default <corpus-root>/transcripts/reconstructed (gitignored — never commit output)")
    ap.add_argument("--check-corpus", action="store_true",
                    help="run the existing-extract guard and stop; write nothing")
    ap.add_argument("--dry-run", action="store_true", help="report what would be assembled; write nothing")
    ap.add_argument("--pad-hours", type=float, default=0.0, help="widen the artifact mtime window")
    ap.add_argument("--all-projects", action="store_true", help="do not restrict memory artifacts by project")
    ap.add_argument("--list-absent", action="store_true", help="list history sessions with no JSONL on disk")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    a = ap.parse_args()

    if a.self_test:
        self_test()
        return 0

    rows, bad = read_history(a.claude_home)
    if bad:
        print(f"[warn] {bad} history.jsonl line(s) unparsable or missing keys — excluded.", file=sys.stderr)

    if a.list_absent:
        cmd_list_absent(rows, a.claude_home)
        return 0
    if not a.session:
        ap.error("session is required unless --list-absent or --self-test is passed")

    sid = resolve_session(rows, a.session)

    # THE PRECONDITION — before any assembly, and before --dry-run too. A dry run that
    # reports "would yield 111 prompts" for a session that already has a real transcript
    # is how a bad list survives review: the number looks like a finding.
    corpus_root = Path(a.corpus_root) if a.corpus_root else Path(__file__).resolve().parent.parent / "raw"
    assert_no_existing_extract(corpus_root, sid)
    if a.check_corpus:
        print(f"[guard] {sid} is clear — no extract in the corpus.")
        return 0

    on_disk = jsonl_on_disk(a.claude_home)
    jsonl_present = sid in on_disk
    g = gather(rows, sid, a.claude_home, a.pad_hours, a.all_projects)

    body = render(g, jsonl_present)
    doc = frontmatter(g, body, jsonl_present) + body
    name = out_name(g)

    out_dir = Path(a.out_dir) if a.out_dir else corpus_root / "transcripts" / "reconstructed"
    target = out_dir / name

    print(f"session          : {sid}")
    print(f"jsonl on disk    : {'YES (prefer it)' if jsonl_present else 'no — reconstruction is the only record'}")
    print(f"window           : {fmt(g['lo'])} -> {fmt(g['hi'])}  ({g['span_hours']:.1f}h)")
    print(f"prompts          : {len(g['prompts'])}   chars typed: {g['chars']}")
    print(f"pasted items     : {g['pasted_total']} ({g['pasted_with_content']} with recoverable content)")
    print(f"artifacts matched: {len(g['artifacts'])} "
          f"({sum(1 for x in g['artifacts'] if x['kind']=='plan')} plan / "
          f"{sum(1 for x in g['artifacts'] if x['kind']=='memory')} memory)")
    for art in g["artifacts"]:
        print(f"    [ARTIFACT:{fmt(art['mtime_ms'])}] {art['kind']:6} {art['path'].name}  ({art['scope']})")
    print(f"foreign prompts  : {g['foreign_prompts']} from {len(g['foreign_sessions'])} other session(s) "
          f"{[s[:6] for s in g['foreign_sessions']]}")
    print(f"output bytes     : {len(doc.encode('utf-8'))}")
    print(f"output path      : {target}")

    if a.dry_run:
        print("\nDRY RUN — nothing written.")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    print(f"\nWROTE {target} ({target.stat().st_size} bytes)")
    print("Output is under raw/ — gitignored, personal. NEVER `git add -f` it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
