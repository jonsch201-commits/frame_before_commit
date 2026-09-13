#!/usr/bin/env python3
"""
extract_claude_code_sessions.py — DISCOVER Claude Code JSONL sessions across ALL
~/.claude/projects/ directories and extract them to raw/transcripts/claude-code/ markdown.

This is a DISCOVERY + ORCHESTRATION layer. The actual conversion is delegated to
the single canonical converter `skills/chat-exporter/scripts/convert-claude-code.py`
so every CC session gets ONE consistent convention (frontmatter, tool-call
summaries, honest thinking labeling). The old in-script renderer — which dropped
tool calls, wrote minimal frontmatter, and used a different `source_type` — has
been retired (Phase A inc.2, 2026-07-12).

Modes:
  python extract_claude_code_sessions.py            # extract NEW sessions + subagents
  python extract_claude_code_sessions.py --list     # discovery only, no writes
  python extract_claude_code_sessions.py --update    # also re-extract grown/changed sessions
  python extract_claude_code_sessions.py --update --dry-run   # show what --update would do
  python extract_claude_code_sessions.py --no-subagents        # primaries only (pre-2026-07-25 behavior)
  python extract_claude_code_sessions.py --subagents-only      # subagents only
  python extract_claude_code_sessions.py --projects-root DIR   # scan an archive copy instead of ~/.claude/projects

Discovery: every subdirectory under `~/.claude/projects/` — CFL (renamed dir + all
worktrees), `D--Kevin-Image`, `research-clarity-02cf`, and any other project dir Claude
Code has ever created there. See project_for_dir() for the attribution map; a directory
SKILL.md hasn't named yet is tagged "triage" rather than silently folded into "fl".

SUBAGENT TRANSCRIPTS (2026-07-25) — the omission this fix closes:
  Claude Code writes every delegated agent's conversation to
  `<project>/<session-uuid>/subagents/agent-<agentId>.jsonl`. iter_session_jsonls()
  below globs `proj_dir/'*.jsonl'` — TOP-LEVEL ONLY — so from the day this script was
  written it had never seen one. The docstring said they were "handled separately per
  the wiki-master subagent-ingest threshold"; that threshold was never built, so the
  deferral silently became a permanent omission. Measured 2026-07-25: 305 subagent
  JSONLs / 107,690,851 bytes live under ~/.claude/projects — 43.8% of all Claude Code
  bytes on disk — plus 71 more in the 2026-05-29 pre-deletion archive.

  EXTRACTION IS NOT INGEST. This script's job ends when the transcript exists as
  readable markdown in the local corpus. Whether any of it becomes a wiki page is
  wiki-master's separate decision. Conflating the two is what produced the original
  omission; keeping them separate is what stops it recurring.

Domain-subfolder output (raw-file-standards.md v2.0, Phase 2): a genuinely NEW session whose
project is fl/pro/research is written to OUT_DIR/{project}/ via convert-claude-code.py's
--domain-subfolder flag. A REFRESH (--update, existing md found) is always written flat at its
existing path — never relocated, even if that path is the legacy flat root — so existing wiki
source_file: citations never break. triage-tagged sessions stay flat (not yet domain-routed).

Subagent output layout (see subagent_out_dir() for the full rationale):
  OUT_DIR/subagents/<parent-uuid6>/code-<date>-<agentId6>-<slug>.md
Grouped by parent session, NOT domain-subfoldered — the parent/child relation is the
directory itself, and the domain lives in the `project:` frontmatter field exactly as
raw-file-standards.md §Required Fields prescribes for CC sessions ("do not require both
a folder AND a field on the same file"). OUT_DIR/subagents/index.md is regenerated from
what is on disk every run so ~300 opaque agent ids stay navigable.
"""
import argparse
import fnmatch
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ROOT is where the CORPUS lives.
#
# ⛔ CHANGED 2026-09-07. It read, verbatim:
#     # ROOT is where the CORPUS lives — pinned to the canonical Drive repo, deliberately
#     # absolute, because there is exactly one corpus no matter which checkout you run from.
#     ROOT = Path(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer")
#
# The reasoning was sound and it EXPIRED on 2026-09-02 when CFL moved to N:\claude-cfl\clone.
# `[measured 2026-09-07]` the graph index's own `corpus_root` is `N:/claude-cfl/clone`; it reads
# `raw/` from this checkout and the federated mirror at `N:/claude-corpus/cfl`. **It never reads
# G: at all.** So every export since the move wrote a corpus the retriever cannot see: the newest
# transcript reachable from N: was dated 2026-09-05, and the session this trunk spent a day
# reviewing had no primary transcript on N: whatsoever.
#
# ⚠️ THE SECOND HALF, which makes it not merely stale but unrecoverable-in-place: the G:->N: leg
# is `mirror_corpus_to_n.py`, owned by ANOTHER TRUNK'S DAEMON (Antigravity, 5-minute tick), and
# that daemon's BEACON has been silent since 2026-09-07 00:30 CDT. A correct write to G: would
# still not arrive. **One hardcoded path plus one silent loop, and the corpus a whole fleet grounds
# on stops advancing with no alarm anywhere.**
#
# ⚠️ WORDING CORRECTED 2026-09-07 21:2x, AND THE CORRECTION IS THE POINT. This read "one SLEEPING
# DAEMON", and CFL told Jon repeatedly today that "Antigravity is down." `[measured — CFL, own
# hands]` its wikiskills receipt `N:/antigravity-hub/exchange/WIKISKILLS-IMPROVE-ECHOED-765e466c.md`
# is stamped **06:53 on 09-07 — six hours and twenty-three minutes AFTER the beacon stopped**.
# ⛔ **THE TRUNK ACTED TODAY.** What is silent is the COURIER AND BEACON LOOP, not the seat.
# ⭐ The BOUND this fix rests on is unaffected and was correct: capture survives, ROUTING does not,
# so a write to G: still would not have arrived. **The headline over it was wrong, and the headline
# is the part that travels** — it had already hardened into this comment, where it was justifying a
# code change, which is exactly how a wrong headline outlives the claim it was drawn from.
#
# ⭐ The old comment's value is kept and inverted into a rule: there IS exactly one corpus, and
# the one that counts is THE ONE THE INDEX READS. That is a measurement, not a constant — so the
# default now follows the invoking checkout, `--out-root` states it explicitly, and the resolved
# path is printed on every run (it always was; the printed line was true and nobody compared it
# to where the retriever looks).
def _default_corpus_root():
    """The checkout this file lives in, when that checkout is a real repo; else the historical
    Drive root. Never guesses silently — main() prints the resolved value every run."""
    cand = Path(__file__).resolve().parents[1]
    if (cand / ".git").exists() or (cand / "raw").is_dir():
        return cand
    return Path(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer")


ROOT = _default_corpus_root()
# CODE_ROOT is where THIS COPY of the code lives. Split from ROOT on 2026-07-25 after
# it bit for real: repo hygiene mandates working in an off-Drive worktree, and CONVERTER
# used to resolve through ROOT — so running the extractor from a worktree silently paired
# the worktree's NEW extractor with the Drive checkout's OLD (main-branch) converter. The
# run "succeeded", 376 files, exit 0 — and every one of them was rendered by main's parser:
# tool payloads truncated to 300 chars, no subagent frontmatter, and subagent briefs
# emitted under `## Human`, i.e. the exact misattribution this feature exists to prevent.
# Nothing in the output said which converter produced it. Code follows the checkout;
# data stays put.
CODE_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_ROOT = Path.home() / ".claude" / "projects"
# ⛔ THIS WAS A SINGLE GLOB PINNED TO THE **G:** KEY, AND IT SILENTLY DEMOTED EVERY SESSION
# SINCE THE 2026-09-02 MOVE TO N:. A project dir that does not match falls through to "triage",
# so CFL's own current sessions were being classified as somebody else's -- no error, no count,
# just a corpus whose September branch is thin. [measured 2026-09-05 00:3x: the live key is
# N--claude-cfl-clone, 5 sessions; the G: key holds 83. The glob matched only the 83.]
# ⭐ A trunk's project key follows its CWD, so a RECORDED key is a claim that expires the next
# time the tree moves. The current key is DERIVED from the checkout; the historical ones stay
# listed because the corpus is history and those sessions really did happen under them.
def _key_for(path):
    """~/.claude/projects sanitises a path by replacing every non-alphanumeric run with '-'."""
    import re as _re
    # ⛔ PER CHARACTER, NOT PER RUN. The first draft of this line used `+` and derived
    # "N-claude-cfl-clone" for a tree whose real key is "N--claude-cfl-clone" -- `N:\claude-cfl`
    # contributes TWO separators (":" and "\\") and they do not collapse. ⭐ A WRONG DERIVATION
    # IS WORSE THAN A CONSTANT: it looks principled, so nobody re-checks it. Caught by printing
    # the value instead of trusting the code, 2026-09-05 00:3x.
    return _re.sub(r"[^A-Za-z0-9]", "-", str(path)).strip("-")

CFL_DIR_GLOBS = [
    "G--My-Drive-Claude-Claude-Foundational-Layer*",  # historical: the on-Drive checkout
    "N--claude-cfl*",                                 # historical + current: the NVMe clones
    _key_for(CODE_ROOT),                              # DERIVED: wherever this checkout is now
]
# kept so any external caller importing the old name still works; it is NOT the matcher
CFL_DIR_GLOB = CFL_DIR_GLOBS[0]
OUT_DIR = ROOT / "raw" / "transcripts" / "claude-code"
CONVERTER = CODE_ROOT / "skills" / "chat-exporter" / "scripts" / "convert-claude-code.py"
if not CONVERTER.exists():
    # Fallback for a copy of this script living outside a repo checkout.
    CONVERTER = ROOT / "skills" / "chat-exporter" / "scripts" / "convert-claude-code.py"

# ---------------------------------------------------------------------------------------------
# CORPUS ROOT PRECONDITION — the "silent write to nowhere" detector
# ---------------------------------------------------------------------------------------------
# Added 2026-08-08 ahead of the containerized-resident launch decision. ROOT above is a Windows
# drive path written as a raw string. On WINDOWS it parses to an absolute WindowsPath and every
# path derived from it is correct. On POSIX — i.e. inside a Linux container — `pathlib` builds a
# PosixPath, backslash is an ORDINARY FILENAME CHARACTER, and the entire string collapses to a
# SINGLE-COMPONENT RELATIVE path. Measured:
#
#     PurePosixPath(r"G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer")
#       .parts       -> ('G:\\My Drive\\Claude\\Claude Foundational Layer\\claude-foundational-layer',)
#       .is_absolute() -> False
#
# The consequence is the opposite of the intuitive one. `OUT_DIR.mkdir(parents=True,
# exist_ok=True)` does NOT raise there — it SUCCEEDS, creating a junk directory of that literal
# name under the process CWD, and every transcript is written into it. The container exits and
# the directory dies with it.
#
# **There is no exception, so no `except` clause anywhere in this chain can see it, and every
# counter reports success.** A fix that only makes the exception handlers louder does not detect
# this case at all. `is_absolute()` is the load-bearing check here, not `exists()`.
#
# This function READS ONLY. It never creates the root, never writes, and never raises — callers
# decide what to do with the verdict, and `session_finalise.py` is the first to use it.

ROOT_OK = "OK"
ROOT_NOT_ABSOLUTE = "NOT_ABSOLUTE"
ROOT_MISSING = "MISSING"
ROOT_NOT_A_DIR = "NOT_A_DIR"
ROOT_NOT_THE_REPO = "NOT_THE_REPO"

# Codes under which a write CANNOT reach the corpus, so attempting one either lands garbage
# somewhere else or throws. Distinguished from NOT_THE_REPO, which is a heuristic and only warns.
ROOT_REFUSE_CODES = (ROOT_NOT_ABSOLUTE, ROOT_MISSING, ROOT_NOT_A_DIR)


def corpus_root_status(root=None):
    """(ok, code, detail) for the corpus root. Never raises, never writes, never creates."""
    r = Path(root) if root is not None else ROOT
    try:
        if not r.is_absolute():
            return (False, ROOT_NOT_ABSOLUTE,
                    f"{r!s} is not absolute on this platform (sys.platform={sys.platform}). "
                    "A Windows drive path parsed by PosixPath becomes a RELATIVE one-component "
                    "name, so writes SUCCEED into a junk directory under the CWD instead of "
                    "reaching the corpus, and nothing raises.")
        if not r.exists():
            return (False, ROOT_MISSING, f"{r!s} does not exist")
        if not r.is_dir():
            return (False, ROOT_NOT_A_DIR, f"{r!s} exists but is not a directory")
        if not (r / "raw").is_dir() and not (r / ".git").exists():
            return (False, ROOT_NOT_THE_REPO,
                    f"{r!s} exists but has neither raw/ nor .git/ — probably not the corpus repo")
    except OSError as e:
        return (False, ROOT_MISSING, f"{r!s}: {e.__class__.__name__}: {e}")
    return (True, ROOT_OK, str(r))

# RATIO_FLOOR (was 0.20, a size-ratio floor for --update truncation detection) retired
# 2026-08-06, `43fa49d`. It was unsatisfiable — healthy range measured 0.0037-0.159, always
# below the floor — and fired on essentially every real session. Replaced by turn_parity.py's
# exact-equality check (sidecar turns_covered vs re-derived count via extract_turn_records),
# wired into needs_refresh() below. Kill condition ran and passed: 2319 == 2319 on `2b2ff8`
# (exchange/su-close/2026-08-05/capture-extract.out:33). The constant itself was dead code by
# the time of removal — declared here, never read anywhere in this file or imported elsewhere.


def discover_proj_dirs():
    """Return ALL project dirs under ~/.claude/projects/ (every subdirectory, not
    just CFL — SKILL.md's Session Startup step 2 documents this as the scan scope).
    project_for_dir() below attributes each one; unnamed dirs are flagged, not dropped.
    """
    if not PROJECTS_ROOT.exists():
        return []
    return sorted(d for d in PROJECTS_ROOT.iterdir() if d.is_dir())


def project_for_dir(dir_name):
    """Map a project directory name to a project tag for frontmatter.

    Only the patterns SKILL.md documents get a real tag. Anything else is flagged
    "triage" — matching the rescued proposal's "Others -> flag for Jon triage" — so
    an unmapped directory is never silently absorbed into "fl" (that mislabeling is
    the class of bug this fix closes).
    """
    if "D--Kevin-Image" in dir_name:
        return "pro"
    if "research-clarity-02cf" in dir_name:
        return "research"
    if any(fnmatch.fnmatch(dir_name, g) for g in CFL_DIR_GLOBS):
        return "fl"
    return "triage"


def iter_session_jsonls():
    """Yield (proj_dir, jsonl_path) for every top-level session across all discovered dirs.

    Deduplicate by UUID (a session is visited from only one dir).

    TOP-LEVEL ONLY, deliberately: `<uuid>/subagents/agent-*.jsonl` is a different
    record class with a different parent relationship and a different output layout.
    It is enumerated by iter_subagent_jsonls() below, not folded in here.
    """
    seen = set()
    for proj_dir in discover_proj_dirs():
        for jsonl_path in sorted(proj_dir.glob('*.jsonl')):
            uuid = jsonl_path.stem
            if uuid in seen:
                continue
            seen.add(uuid)
            yield proj_dir, jsonl_path


def read_agent_meta(jsonl_path):
    """Read the sibling `agent-<id>.meta.json` Claude Code writes next to a subagent
    JSONL. Carries agentType / description / toolUseId / spawnDepth (+ sometimes model).

    Present for 305/305 live subagent JSONLs (2026-07-25) but treated as OPTIONAL: a
    missing or malformed meta file costs the human-readable slug, never the transcript.
    """
    meta_path = jsonl_path.with_name(f'{jsonl_path.stem}.meta.json')
    if not meta_path.exists():
        return {}
    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}
    return meta if isinstance(meta, dict) else {}


def iter_subagent_jsonls():
    """Yield (proj_dir, parent_uuid, jsonl_path, meta) for every subagent transcript.

    Layout Claude Code writes:
        ~/.claude/projects/<project-dir>/<session-uuid>/subagents/agent-<agentId>.jsonl
        ~/.claude/projects/<project-dir>/<session-uuid>/subagents/agent-<agentId>.meta.json

    Deduplicated by agentId, mirroring iter_session_jsonls()'s dedupe-by-UUID: the same
    agent id can appear under two project dirs when a session directory was copied
    (worktree renames have already produced exactly that for primary sessions).
    """
    seen = set()
    for proj_dir in discover_proj_dirs():
        for sess_dir in sorted(d for d in proj_dir.iterdir() if d.is_dir()):
            sub_dir = sess_dir / 'subagents'
            if not sub_dir.is_dir():
                continue
            for jsonl_path in sorted(sub_dir.glob('agent-*.jsonl')):
                agent_id = jsonl_path.stem[len('agent-'):]
                if agent_id in seen:
                    continue
                seen.add(agent_id)
                yield proj_dir, sess_dir.name, jsonl_path, read_agent_meta(jsonl_path)


def subagent_root():
    """OUT_DIR/subagents — computed, never a module constant, so a caller that
    reassigns OUT_DIR (the measurement harness does exactly this) can't end up with
    a subagent root pointing at the real corpus.
    """
    return OUT_DIR / 'subagents'


def subagent_out_dir(parent_uuid):
    """OUT_DIR/subagents/<parent-uuid6> — one directory per PARENT session.

    Why grouped-by-parent rather than flat-with-parent-in-the-filename:

    1. It makes existing_mds()'s collision impossible BY CONSTRUCTION rather than by
       care. `Path.rglob("*<uuid6>*.md")` matches the FILENAME component only (verified
       empirically, not assumed) — so a parent's uuid6 sitting in a DIRECTORY name can
       never match. Had the parent uuid6 gone in the filename, existing_mds(parent6)
       would have returned the parent's md AND all of its subagent mds, and the
       `--update` refresh path (`for p in md_paths: p.unlink()`) would have DELETED
       every subagent extract for that session on the next refresh. existing_mds()
       also excludes this subtree outright — belt and braces, since one guard is a
       naming convention and the other is code.
    2. Parent -> children is `ls`; child -> parent is the directory name. Both
       directions recoverable without opening a file. (The authoritative record is
       still the `parent_session:` frontmatter field the converter derives from the
       JSONL's own `sessionId`, which survives the file being moved.)
    3. It bounds directory width: 12 parent dirs of 1-70 files rather than one
       305-file directory dropped next to the 54 primary extracts.

    NOT domain-subfoldered. raw-file-standards.md's Required Fields table says CC
    sessions express domain via the `project:` frontmatter field and explicitly warns
    "do not require both a folder AND a field on the same file"; the subagent's own
    domain is its parent's, and it is written into `project:` by the converter.
    """
    return subagent_root() / parent_uuid[:6]


def existing_mds(uuid6):
    """Return existing extracted MD paths for a uuid6 (glob — slug may vary).

    Recursive (rglob, not glob): since Phase 2, new fl/pro/research extractions land one level
    down at OUT_DIR/{project}/, while ~50 grandfathered sessions remain flat at OUT_DIR itself. A
    flat glob would miss the subfoldered ones and silently re-extract duplicates on the next run.

    The subagents/ subtree is EXCLUDED (2026-07-25). Two independent reasons, either
    one sufficient: (a) a 6-hex-char agentId prefix can collide with a session uuid6 —
    ~350 ids in a 16^6 space is a small but real birthday risk, and a collision would
    make a subagent extract answer for a primary session; (b) if any subagent filename
    ever did contain its parent's uuid6, the `--update` unlink-then-rewrite path would
    delete the whole subagent set for that parent. Scoping here removes both classes
    regardless of what the naming convention does later.
    """
    if not OUT_DIR.exists():
        return []
    sub_root = subagent_root()
    return [p for p in OUT_DIR.rglob(f"*{uuid6}*.md") if sub_root not in p.parents]


def existing_subagent_mds(parent_uuid, agent_id):
    """Existing extract(s) for one subagent, scoped to its own parent directory."""
    d = subagent_out_dir(parent_uuid)
    if not d.exists():
        return []
    return [p for p in d.glob(f"*{agent_id[:6]}*.md") if not p.name.endswith('.sidecar.md')]


def hold_refresh(md_paths):
    """Read the extracts about to be replaced into memory, then unlink them.

    WHY THIS IS NOT PARANOIA (2026-08-03). The refresh path has always been
    `unlink() -> convert() -> if not ok: record a failure` — so a conversion that failed
    AFTER the unlink left NO extract on disk at all. That was survivable while the path
    was rare (only genuinely grown/truncated files took it). Adding the sidecar clause to
    needs_extract() puts 621 existing extracts through it in a single pass, which turns a
    latent hazard into a mass-deletion hazard: one converter regression during the backfill
    would delete the corpus it was backfilling, and `raw/` is gitignored, so git would not
    get it back.

    Holding the bytes costs one file's memory at a time and makes the refresh
    fail-safe rather than fail-destructive. Same lesson as the stale-index-lock incident:
    the recoverable version of a destructive step is worth its cost.
    """
    held = []
    for p in md_paths:
        try:
            held.append((p, p.read_bytes()))
        except OSError:
            held.append((p, None))
        try:
            p.unlink()
        except OSError:
            pass
    return held


def restore_refresh(held):
    """Put back anything we unlinked for a refresh that then failed. Never deletes."""
    for p, data in held:
        if data is not None and not p.exists():
            try:
                p.write_bytes(data)
            except OSError:
                pass


def sidecar_for(md_path):
    """The per-turn provenance companion this extract should have. Naming is
    convert-claude-code.py's (`<stem>.sidecar.md`) and is asserted by its self-test."""
    return md_path.with_name(md_path.name[:-3] + '.sidecar.md')


def needs_extract(jsonl_path, md_paths, update):
    """(bool, reason). New → always. Existing → only under --update if grown/truncated,
    OR if its per-turn provenance companion is missing.

    THE SIDECAR CLAUSE IS A BACKFILL THAT HEALS ITSELF (2026-08-03). Turning the sidecar
    on for subagents only helps files extracted AFTER the flip; 583 subagent extracts and
    38 primaries already on disk would have kept their missing per-turn time forever, and
    the usual answer — "run a one-off backfill script" — is precisely the shape that
    produced this gap: a step that lives in someone's memory instead of in the program.
    Deriving the requirement here means an extract missing its companion is simply STALE,
    healed by the same `--update` the standard update already runs, and re-derived from
    the filesystem every pass rather than recorded once. It cannot silently regress: if a
    sidecar is deleted, the next run rewrites it.
    """
    if not md_paths:
        return True, "new"
    if not update:
        return False, "exists (use --update to refresh)"
    md = md_paths[0]
    if not sidecar_for(md).exists():
        return True, "per-turn provenance sidecar missing"
    if jsonl_path.stat().st_mtime > md.stat().st_mtime:
        return True, "jsonl newer than md (grew/changed)"
    # TURN PARITY REPLACES THE BYTE RATIO. See scripts/audit/turn_parity.py for the full argument.
    #
    # The old test asked whether the markdown was >=20% of the JSONL's bytes. It was UNSATISFIABLE:
    # the markdown legitimately summarizes tool payloads the JSONL stores in full, so healthy
    # extracts measured 0.0037-0.159 and every one of them was flagged stale forever. Two LOSS-tier
    # blocking SU rows were wired under it and had been red long enough that nobody read them.
    #
    # Turn parity compares the sidecar's `turns_covered` against the turn count re-derived NOW with
    # this program's own `extract_turn_records`. **Exact equality, no tunable constant** — so the
    # recalibration decision class is deleted rather than re-parameterized, which is what took this
    # out of the standing in-code reservation to Jon (that reservation covered choosing a new ratio;
    # there is no longer a ratio to choose).
    #
    # Kill condition, run before this shipped: the shared counter returns exactly 2,319 on 2b2ff8 —
    # the extract the old floor flagged stale immediately after a successful full refresh. MEASURED
    # 2026-08-06: CURRENT, sidecar 2319 == re-derived 2319.
    #
    # An underivable count is NOT a refresh trigger and NOT a pass — it is left to the mtime check
    # above and reported by `turn_parity.py` as UNKNOWN. Guessing in either direction is how a
    # detector becomes either an always-firing alarm or a rubber stamp.
    parity = _turn_parity(jsonl_path, sidecar_for(md))
    if parity is not None:
        sidecar_n, rederived_n = parity
        if sidecar_n < rederived_n:
            return True, (f"turn parity: sidecar {sidecar_n} < source {rederived_n} "
                          f"({rederived_n - sidecar_n} turns missing)")
        if sidecar_n > rederived_n:
            return True, (f"turn parity ERROR: sidecar {sidecar_n} > source {rederived_n} — the "
                          f"extract claims turns the source does not hold; re-extracting cannot "
                          f"fix this, investigate")
    return False, "current"


def _turn_parity(jsonl_path, sidecar_path):
    """(sidecar_turns, rederived_turns), or None if either is underivable.

    Delegates to scripts/audit/turn_parity.py so THE COUNTING RULE IS IMPLEMENTED ONCE. A second,
    independently-written counter is exactly how false fires would return — divergent handling of
    isMeta records, signature-only thinking, or tool-result-only events would reintroduce the
    disease under a new name.
    """
    try:
        import importlib.util
        tp_path = ROOT / "scripts" / "audit" / "turn_parity.py"
        spec = importlib.util.spec_from_file_location("turn_parity", tp_path)
        tp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tp)
        s = tp.sidecar_turns(str(sidecar_path))
        r, _why = tp.rederived_turns(str(jsonl_path))
        return None if (s is None or r is None) else (s, r)
    except Exception:
        return None


def quick_meta(jsonl_path):
    """Lightweight message-count + title for --list (avoids a full parse)."""
    msgs = 0
    title = ''
    try:
        text = jsonl_path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return 0, ''
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = obj.get('type', '')
        if t == 'custom-title':
            title = obj.get('title', '') or title
        elif t == 'ai-title' and not title:
            title = obj.get('aiTitle', '')
        elif t in ('user', 'assistant'):
            m = obj.get('message', {})
            c = m.get('content', '')
            if (m.get('role') == 'user' and isinstance(c, str) and c.strip()) or \
               (m.get('role') == 'assistant' and isinstance(c, list)):
                msgs += 1
    return msgs, title


def session_is_empty(jsonl_path):
    """True when a JSONL parses cleanly and holds no conversation at all.

    WHY THIS EXISTS — EMPTY is not FAILED, and conflating them is the cry-wolf shape.

    Nine sessions returned `No turns extracted` on every run. Claude Personal opened all
    nine and counted their entries by `type` (relayed 2026-08-03): zero user or assistant
    entries, zero unparseable lines, largest file 4,284 bytes. Four hold only `ai-title` +
    `agent-name` — launched, named, abandoned. Five hold `mode`, `permission-mode`,
    `system` and a `last-prompt` — opened and closed without a turn. CFL had independently
    reached the same reading on 2026-08-02; two projects converged.

    The converter is correct. There are no turns. The defect is the label, and it costs
    three things: a real parse break is indistinguishable from an abandoned session; the
    failure count can never reach zero because these files are permanent; and a count whose
    steady state is "alarming" stops being read. It has already cost something small and
    real — Personal reported one of the nine to CFL as a defect. It was not one.

    Predicate is Personal's, deliberately: clean parse AND zero {user, assistant} records.
    It reads entry TYPES only, never content. Anything else producing no turns stays a
    genuine `Failed` and stays loud.

    NOT a loss claim. These sessions contain nothing to lose; they belong in no
    lost-session register.
    """
    try:
        text = jsonl_path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return False
    turns = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            return False          # unparseable → a genuine failure, never EMPTY
        if obj.get('type') in ('user', 'assistant'):
            turns += 1
    return turns == 0


def convert_one(jsonl_path, project, force, slug=None, domain_subfolder=False,
                out_dir=None, role=None, sidecar=True):
    """Delegate to the canonical converter. Returns (ok, stdout).

    Passing the session's aiTitle/custom-title as --slug gives clean filenames;
    without it the converter derives the slug from the first user turn, which for
    CC sessions is often a slash-command (garbage). Falls back cleanly if no title.

    domain_subfolder=True (new sessions only — never on refresh) asks the converter to route
    fl/pro/research projects under OUT_DIR/{project}/ per raw-file-standards.md v2.0 Phase 2.

    out_dir overrides OUT_DIR for subagents (they go under OUT_DIR/subagents/<parent6>/).
    sidecar=False suppresses the per-turn provenance .sidecar.md — see extract_subagents().
    """
    cmd = [sys.executable, str(CONVERTER), str(jsonl_path), "--run",
           "--out", str(out_dir or OUT_DIR), "--project", project]
    if slug:
        cmd += ["--slug", slug]
    if role:
        cmd += ["--role", role]
    if force:
        cmd.append("--force")
    if domain_subfolder:
        cmd.append("--domain-subfolder")
    if not sidecar:
        cmd.append("--no-sidecar")
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, (r.stdout or '') + (r.stderr or '')


def subagent_slug(meta):
    """--slug for a subagent: "<agentType>: <description>" from its meta.json.

    Without this the converter would fall back to the opening 60 chars of the
    orchestrator's brief, which is prose, not a label. meta.json's `description` is
    the short human-written task name the dispatcher already wrote ("Fix #92
    identity-fence violations"), and `agentType` is the role that ran it.

    Measured 2026-07-25 over all 305 live subagent metas: len(agentType + ' ' +
    description) is min 25 / median 46 / p90 57 / max 80 chars, so 84 of 305 (27.5%)
    get truncated by slugify()'s 50-char cap. That truncation costs the tail of the
    filename only — the untruncated `agent_type` and `agent_description` are both in
    the file's frontmatter and in subagents/index.md.
    """
    atype = (meta.get('agentType') or '').strip()
    desc = (meta.get('description') or '').strip()
    if atype and desc:
        return f'{atype}: {desc}'
    return atype or desc or None


FRONTMATTER_FIELDS_FOR_INDEX = (
    'date', 'agent_type', 'agent_description', 'agent_models', 'project', 'char_count')


def read_frontmatter(md_path, fields):
    """Pull a few top-level `key: value` frontmatter fields out of an extracted md.

    Deliberately a line scan of the leading `---` block, not a YAML parse: the corpus
    has no yaml dependency, values here are flat scalars, and a parse failure on one
    file must not take the index generation down with it.
    """
    out = {}
    try:
        with open(md_path, 'r', encoding='utf-8', errors='replace') as f:
            if f.readline().strip() != '---':
                return out
            for line in f:
                line = line.rstrip('\n')
                if line.strip() == '---':
                    break
                if ':' in line:
                    k, _, v = line.partition(':')
                    if k.strip() in fields:
                        out[k.strip()] = v.strip()
    except OSError:
        pass
    return out


def write_subagent_index():
    """(re)generate OUT_DIR/subagents/index.md from what is actually on disk.

    This is the mitigation for the volume question: 305 files named for 17-hex-char
    agent ids are not navigable, and dropping them into the corpus without a map is
    how a records-reader ends up grepping blind. The index is built by READING the
    extracts (not by re-walking ~/.claude/projects), so it describes the corpus rather
    than the machine — it stays correct when run against an archive extraction, and it
    can never claim a file that isn't there.

    Deterministic by construction — sorted, and carrying NO extraction timestamp — and
    written only when the bytes actually change, so a second run of the script is a
    true no-op rather than an mtime churn.
    """
    root = subagent_root()
    if not root.exists():
        return None, 0

    groups = {}
    total_bytes = 0
    for md in sorted(root.rglob('*.md')):
        if md.name == 'index.md' or md.name.endswith('.sidecar.md'):
            continue
        fm = read_frontmatter(md, FRONTMATTER_FIELDS_FOR_INDEX)
        groups.setdefault(md.parent.name, []).append((md, fm))
        total_bytes += md.stat().st_size

    count = sum(len(v) for v in groups.values())
    lines = [
        '# Subagent transcript index',
        '',
        'Generated by `scripts/extract_claude_code_sessions.py` from the extracts on disk.',
        'Deterministic and regenerated in place — do not hand-edit.',
        '',
        f'- Subagent transcripts: **{count}** across **{len(groups)}** parent session(s)',
        f'- Total extracted bytes: **{total_bytes:,}**',
        '',
        'Every `## Dispatch` turn in these files was written by the ORCHESTRATING agent in',
        'the parent session — not by Jon, and carrying none of Jon\'s authority. A subagent',
        'never ratifies; the parent session\'s transcript is the record of what was accepted.',
        '',
    ]
    for parent6 in sorted(groups):
        rows = sorted(groups[parent6], key=lambda r: (r[1].get('date', ''), r[0].name))
        lines.append(f'## Parent session `{parent6}` — {len(rows)} subagent run(s)')
        lines.append('')
        lines.append('| date | agent type | description | models | file |')
        lines.append('|---|---|---|---|---|')
        for md, fm in rows:
            rel = f'{parent6}/{md.name}'
            desc = (fm.get('agent_description') or '').replace('|', '\\|')
            models = (fm.get('agent_models') or '').replace('|', '\\|')
            lines.append(
                f'| {fm.get("date", "?")} | {fm.get("agent_type", "?")} | {desc} | '
                f'{models} | [{md.name}]({rel}) |')
        lines.append('')

    content = '\n'.join(lines)
    index_path = root / 'index.md'
    if index_path.exists() and index_path.read_text(encoding='utf-8') == content:
        return index_path, count
    index_path.write_text(content, encoding='utf-8')
    return index_path, count


# ---------------------------------------------------------------------------------------
# BIDIRECTIONAL CORPUS LINKS (2026-08-03)
#
# THE GAP: measured on 2026-08-03, all 14 of that session's subagent extracts named their
# parent (`parent_session:` frontmatter, a UUID) and NOTHING pointed the other way. A reader
# who opened a parent extract could not find its children; a reader who opened one consult
# could not find the consult that corrected it. subagent_out_dir()'s docstring says
# "parent -> children is `ls`" — true of the DIRECTORY, false of the DOCUMENT, and a
# citation follows documents. A UUID is not a link: resolving `parent_session:` to a file
# requires knowing the corpus layout and running a glob.
#
# WHY A BLOCK IN THE PREAMBLE AND NOT FRONTMATTER: a reader skimming an extract has to SEE
# the relation, and a parent's child list is a table, not a scalar. The block sits between
# the H1 and `## Summary` — above the first turn separator — so it is outside every citation
# anchor: turn_index.py counts `^##\s+(Human|Assistant|Compaction Boundary|Tool Result|
# Dispatch)\s*$` headers in order, and `## Linked transcripts` matches none of them, while
# P anchors count paragraphs WITHIN a turn's content and never see the preamble. This is
# verified by a real before/after turn_index run, not asserted.
#
# WHY SIBLINGS ARE REACHED VIA THE PARENT AND THE GROUP INDEX, NOT ENUMERATED IN EACH OTHER:
# fan-out is 136 children on the largest parent (measured), so a full sibling list inside
# every sibling is O(n^2) — 18,360 rows for that one group. Parent-link + group-index-link
# gives complete reachability in two hops at O(n). The index already existed and was already
# regenerated from disk; the defect was that nothing pointed AT it.
#
# WHY IT IS RE-DERIVED EVERY RUN RATHER THAN WRITTEN ONCE: the block is a pure function of
# what is on disk, so scripts/audit/corpus_links.py verifies it by RE-DERIVING and comparing,
# not by trusting the text it finds. That is what keeps su_close.sh's property 3 intact — the
# check is not satisfiable by editing the record, because the only edit that passes is the
# one the deriver would have made.
# ---------------------------------------------------------------------------------------

LINK_BEGIN = '<!-- corpus-links:begin -->'
LINK_END = '<!-- corpus-links:end -->'


def _rel(target, start_dir):
    """POSIX-style path from start_dir to target — what a markdown link needs.

    Deliberately relative to the CONTAINING FILE, which is how every markdown renderer
    resolves a link. A path rooted at raw/transcripts/ would read tidier and would not
    click through from an extract sitting in fl/.
    """
    import os
    return Path(os.path.relpath(target, start_dir)).as_posix()


def scan_corpus_relations():
    """Everything the link blocks need, read from the corpus on disk exactly once.

    Returns (primaries, children) where
      primaries: uuid6 -> Path of the primary extract
      children:  parent6 -> [(Path, frontmatter dict), ...] sorted deterministically

    SCOPE, STATED RATHER THAN LEFT TO A FILENAME PREFIX. This walks OUT_DIR and keeps
    only PIPELINE EXTRACTS — files this extractor produced, named
    `code-YYYY-MM-DD-XXXXXX-slug.md`. Measured 2026-08-03, that admits 97 primaries + 583
    subagent extracts and excludes exactly 8 files, none of them a session extract:
      · 4 `_routing-note.md` — administrative notes about a directory, not transcripts;
      · 4 under `_routing/incoming/` — one hand-written note and three `recon-*.md`
        reconstructions, which have no JSONL, no session uuid, and no subagents, so there
        is no parent/child relation for a link block to express.
    They are outside the denominator BY THIS RULE, not by accident, and the count is
    recorded here so a future reader can tell "excluded" from "overlooked" — the
    distinction this program keeps paying to relearn.

    UUID6 COLLISIONS ARE KEPT, NOT OVERWRITTEN. Two extracts sharing a uuid6 (a legacy
    flat file and a domain-subfoldered one, say) used to mean the second silently replaced
    the first in this map and vanished from every denominator computed over it. A
    collision now keeps the lexically-first path — deterministic — and both files still
    appear in `all_primaries`, so nothing drops out of a count.
    """
    primaries, children = {}, {}
    if not OUT_DIR.exists():
        return primaries, children
    sub_root = subagent_root()
    for md in sorted(OUT_DIR.rglob('*.md')):
        if md.name == 'index.md' or md.name.endswith('.sidecar.md'):
            continue
        if sub_root in md.parents:
            children.setdefault(md.parent.name, []).append(
                (md, read_frontmatter(md, FRONTMATTER_FIELDS_FOR_INDEX)))
        else:
            # `code-YYYY-MM-DD-XXXXXX-slug.md` — the uuid6 is the 4th dash-field.
            parts = md.stem.split('-')
            if len(parts) >= 5 and parts[0] == 'code':
                primaries.setdefault(parts[4], md)
    for k in children:
        children[k].sort(key=lambda r: (r[1].get('date', ''), r[0].name))
    return primaries, children


def corpus_link_block(md, primaries, children):
    """The link block THIS file should carry — a pure function of (path, corpus state).

    Purity is the point: corpus_links.py calls this same function to decide whether the
    block on disk is correct, so "correct" has exactly one definition and it lives here.
    Returns '' when the file warrants no block at all.
    """
    d = md.parent
    lines = [LINK_BEGIN, '', '## Linked transcripts', '']

    side = sidecar_for(md)
    is_child = subagent_root() in md.parents

    if is_child:
        parent6 = d.name
        pmd = primaries.get(parent6)
        if pmd is not None:
            lines.append(f'- **Parent session:** [`{pmd.name}`]({_rel(pmd, d)})')
        else:
            # Stated, never omitted. An orphan is a capture question owned by
            # su_close.sh's capture.pipeline.absent rows — this row owns link
            # INTEGRITY, and silently dropping the line would hide the orphan
            # from both.
            lines.append(f'- **Parent session:** `{parent6}` — no primary extract '
                         f'in the corpus (capture gap, not a broken link)')
        sibs = len(children.get(parent6, [])) - 1
        idx = subagent_root() / 'index.md'
        lines.append(
            f'- **Sibling subagent transcripts:** {sibs} other transcript(s) dispatched '
            f'from the same session, in this directory — indexed in '
            f'[`subagents/index.md`]({_rel(idx, d)})')
    else:
        uuid6 = md.stem.split('-')[4] if len(md.stem.split('-')) >= 5 else ''
        kids = children.get(uuid6, [])
        if kids:
            idx = subagent_root() / 'index.md'
            lines.append(
                f'- **Subagent transcripts:** {len(kids)} dispatched from this session '
                f'(full index: [`subagents/index.md`]({_rel(idx, d)}))')

    if side.exists():
        lines.append(f'- **Per-turn provenance:** [`{side.name}`]({_rel(side, d)}) — '
                     f'timestamp and model for every turn below')

    if not is_child:
        kids = children.get(md.stem.split('-')[4] if len(md.stem.split('-')) >= 5 else '', [])
        if kids:
            lines += ['', '| date | agent type | description | transcript |',
                      '|---|---|---|---|']
            for kmd, fm in kids:
                desc = (fm.get('agent_description') or '').replace('|', '\\|')
                lines.append(
                    f'| {fm.get("date", "?")} | {fm.get("agent_type", "?")} | {desc} | '
                    f'[`{kmd.name}`]({_rel(kmd, d)}) |')

    if len(lines) <= 4:          # header only — nothing to say about this file
        return ''
    lines += ['', LINK_END]
    return '\n'.join(lines)


# The extract's own turn headers — the boundary the link block must never cross.
# Prefix match (\b, not \s*$) so a future heading suffix (e.g. the origin tag the
# converter renders on `## Human` turns) still counts as a turn header here.
TURN_HEADER_RE = re.compile(r'^## (?:Human|Assistant|Compaction Boundary|Tool Result|Dispatch)\b')
SUMMARY_HEADER_RE = re.compile(r'^## Summary\s*$')

# Status values apply_link_block() can return alongside the new text.
LINK_OK = 'ok'                        # inserted / replaced / removed / unchanged, in preamble
LINK_SKIPPED_BODY = 'skipped-body-marker'   # marker found only BELOW the first turn header
                                            # (or inside a fence) — file left byte-identical


def _fence_line_mask(lines):
    """True per line when the line is a fence delimiter or inside an open fence.

    Same CommonMark run-length rule as scripts/audit/turn_index.py's _fence_mask(): a
    fence closes only on a same-character run >= the OPENING run's length. Duplicated
    here (12 lines) rather than imported so this module keeps zero sys.path surgery —
    turn_index.py lives under scripts/audit/, not on this module's import path.
    """
    mask, fence_run = [], 0
    open_re = re.compile(r'^(`{3,})([^`]*)$')
    close_re = re.compile(r'^(`{3,})\s*$')
    for ln in lines:
        s = ln.rstrip('\r')
        if fence_run:
            mask.append(True)
            m = close_re.match(s)
            if m and len(m.group(1)) >= fence_run:
                fence_run = 0
            continue
        m = open_re.match(s)
        if m:
            fence_run = len(m.group(1))
            mask.append(True)
            continue
        mask.append(False)
    return mask


def _first_turn_header_line(lines, mask):
    """0-based index of the first real (non-fenced) turn header, or None."""
    for i, (ln, fenced) in enumerate(zip(lines, mask)):
        if not fenced and TURN_HEADER_RE.match(ln):
            return i
    return None


def apply_link_block(text, block):
    """Insert/replace/remove the link block in an extract. Returns (new_text, status).

    THE BOUNDARY (2026-08-21, Personal's citation-drift letter): the block belongs to
    the PREAMBLE — above the first turn header — and this function must never write
    below that line. The previous version anchored insertion on the FIRST
    `\\n## Summary` anywhere in the file and replaced the FIRST `LINK_BEGIN` anywhere,
    so when a transcript BODY quoted either string (a pasted source-page template, an
    agent discussing this very block), the block landed INSIDE the record and was then
    re-maintained there on every run — 28 files measured 2026-08-19, deepest at line
    4,645, and every one of those blocks shifted every `:line` citation below it.

    So, in order:
      - A marker in the preamble (above the first non-fenced turn header, itself not
        fenced) is THE block: replace / remove it there. Status LINK_OK.
      - A marker only in the body (below the first turn header, or fenced) is either
        quoted content or a block a previous version misplaced. Either way it is part
        of the record now: LEAVE THE FILE BYTE-IDENTICAL and return LINK_SKIPPED_BODY
        so the caller reports it instead of editing around it.
      - Insertion anchors on the extract's OWN `## Summary` — the first non-fenced
        `^## Summary$` line ABOVE the first turn header. No such line -> fall back to
        'straight after the frontmatter' (also above every turn header) so a hand-made
        file is never silently skipped. Never inserts below the first turn header.
    """
    lines = text.split('\n')
    mask = _fence_line_mask(lines)
    first_turn = _first_turn_header_line(lines, mask)

    def in_preamble(i):
        return (not mask[i]) and (first_turn is None or i < first_turn)

    # FIRST SUBSTRING OCCURRENCE, deliberately the same detection the old code used —
    # so every file the old code was maintaining a body block in is caught, including
    # the ones where the marker string sits inside a quoted `cat -n` dump or a fenced
    # template rather than on a clean line of its own. A file whose first occurrence is
    # not a well-formed preamble marker line gets NOTHING written — not even a fresh
    # preamble block, because inserting one would itself shift every citation below it,
    # and the letter's ask is that these files be inventoried and decided deliberately.
    pos = text.find(LINK_BEGIN)
    if pos != -1:
        marker = text.count('\n', 0, pos)
        if not in_preamble(marker) or lines[marker].strip() != LINK_BEGIN:
            return text, LINK_SKIPPED_BODY
        start = sum(len(l) + 1 for l in lines[:marker])
        end = text.find(LINK_END, start)
        if end != -1:
            end += len(LINK_END)
            while end < len(text) and text[end] == '\n':
                end += 1
            return text[:start] + (block + '\n\n' if block else '') + text[end:], LINK_OK
        # Marker with no END in the preamble: malformed — refuse rather than guess a span.
        return text, LINK_SKIPPED_BODY

    if not block:
        return text, LINK_OK

    anchor_line = None
    for i, ln in enumerate(lines):
        if first_turn is not None and i >= first_turn:
            break
        if not mask[i] and SUMMARY_HEADER_RE.match(ln):
            anchor_line = i
            break
    if anchor_line is not None:
        anchor = sum(len(l) + 1 for l in lines[:anchor_line])
        return text[:anchor] + block + '\n\n' + text[anchor:], LINK_OK
    fm_end = text.find('\n---\n', 4) if text.startswith('---') else -1
    anchor = (fm_end + len('\n---\n')) if fm_end != -1 else 0
    return text[:anchor] + '\n' + block + '\n\n' + text[anchor:], LINK_OK


def stamp_corpus_links_lines(text):
    """Publish the block's extent as frontmatter `corpus_links_lines: A-B` (or `none`).

    Personal's letter, item 3: a citing layer that KNOWS the block's extent can compute
    the offset instead of guessing. 1-based inclusive line numbers of LINK_BEGIN..LINK_END
    in the PREAMBLE (a body marker is content, not the block — reported `none`).

    Only ever called on text this run is already writing: adding the field to an
    otherwise-untouched extract would itself shift every line below the frontmatter by
    one, i.e. the exact class of drift this whole fix exists to stop. Idempotent — the
    key is replaced in place once present, so re-runs shift nothing.
    """
    if not text.startswith('---'):
        return text  # no frontmatter to publish into — hand-made file, leave it alone

    def compute(t):
        lines = t.split('\n')
        mask = _fence_line_mask(lines)
        first_turn = _first_turn_header_line(lines, mask)
        begin = end = None
        for i, ln in enumerate(lines):
            if first_turn is not None and i >= first_turn:
                break
            if mask[i]:
                continue
            if begin is None and ln.strip() == LINK_BEGIN:
                begin = i
            elif begin is not None and ln.strip() == LINK_END:
                end = i
                break
        return f'{begin + 1}-{end + 1}' if begin is not None and end is not None else 'none'

    def put(t, value):
        head, sep, rest = t.partition('\n---\n')
        if not sep:
            return t
        fm_lines = head.split('\n')
        for i, ln in enumerate(fm_lines):
            if ln.startswith('corpus_links_lines:'):
                fm_lines[i] = f'corpus_links_lines: {value}'
                break
        else:
            fm_lines.append(f'corpus_links_lines: {value}')
        return '\n'.join(fm_lines) + sep + rest

    # Two passes: the field's own first insertion moves the block down one line, so
    # stamp a placeholder, then re-measure and replace in place (line count stable).
    text = put(text, 'none')
    return put(text, compute(text))


def write_corpus_links():
    """Refresh the link block on every extract. Returns (updated, total, skipped).

    `skipped` is the list of extracts whose only `corpus-links` marker sits in the
    transcript BODY — left byte-identical and reported, never edited around.
    """
    primaries, children = scan_corpus_relations()
    updated, total, skipped = 0, 0, []
    targets = list(primaries.values()) + [p for v in children.values() for p, _ in v]
    for md in targets:
        total += 1
        block = corpus_link_block(md, primaries, children)
        try:
            old = md.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        new, status = apply_link_block(old, block)
        if status == LINK_SKIPPED_BODY:
            skipped.append(md)
            continue
        if new != old:
            md.write_text(stamp_corpus_links_lines(new), encoding='utf-8')
            updated += 1
    return updated, total, skipped


def main():
    global PROJECTS_ROOT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--list', action='store_true', help='Discovery only; write nothing')
    ap.add_argument('--update', action='store_true',
                    help='Also re-extract grown/changed sessions (mtime + size-ratio)')
    ap.add_argument('--dry-run', action='store_true', help='With --update: show, do not write')
    ap.add_argument('--verbose', action='store_true',
                    help='List the ids behind the EMPTY count (they are stable and permanent)')
    ap.add_argument('--no-subagents', action='store_false', dest='subagents',
                    help='Skip subagent transcripts (the pre-2026-07-25 behavior)')
    ap.add_argument('--subagents-only', action='store_true',
                    help='Extract ONLY subagent transcripts; leave primary sessions alone')
    ap.add_argument('--projects-root', metavar='DIR',
                    help='Scan DIR instead of ~/.claude/projects. Same layout expected. This is '
                         'how an ARCHIVE copy is extracted — e.g. the 2026-05-29 pre-deletion '
                         'snapshot, which holds 71 subagent JSONLs for sessions whose live '
                         'JSONLs the retention sweep destroyed and which therefore exist nowhere '
                         'else. Discovery, dedupe, naming, and output layout are identical; only '
                         'the scan root changes.')
    ap.add_argument('--out-root', metavar='DIR',
                    help='Write the corpus under DIR/raw/transcripts/claude-code instead of the '
                         'default (the checkout this script lives in). Use it to target the '
                         'historical Drive corpus explicitly, e.g. --out-root "G:\\My Drive\\'
                         'Claude\\Claude Foundational Layer\\claude-foundational-layer". The '
                         'resolved path is printed every run as "Corpus:".')
    ap.set_defaults(subagents=True)
    args = ap.parse_args()

    global ROOT, OUT_DIR
    if args.out_root:
        ROOT = Path(args.out_root)
        OUT_DIR = ROOT / "raw" / "transcripts" / "claude-code"
    ok, code, detail = corpus_root_status(ROOT)
    if not ok and code in ROOT_REFUSE_CODES:
        sys.exit(f"ERROR: corpus root unusable ({code}): {detail}")

    if args.subagents_only and not args.subagents:
        ap.error('--subagents-only and --no-subagents are contradictory')

    if args.projects_root:
        PROJECTS_ROOT = Path(args.projects_root)
        if not PROJECTS_ROOT.is_dir():
            sys.exit(f"ERROR: --projects-root not a directory: {PROJECTS_ROOT}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not CONVERTER.exists():
        sys.exit(f"ERROR: converter not found at {CONVERTER}")

    # CAPABILITY GATE, not a version string. A converter without is_subagent_record()
    # will happily render subagent briefs under `## Human` and exit 0 — the failure is
    # silent, and it already happened once (see the CODE_ROOT comment at the top). Check
    # the behavior we depend on before writing anything that depends on it.
    if args.subagents:
        converter_src = CONVERTER.read_text(encoding='utf-8', errors='replace')
        if 'def is_subagent_record(' not in converter_src:
            sys.exit(
                f"ERROR: {CONVERTER} predates subagent support — it would emit subagent\n"
                f"       briefs under '## Human' (misattributing an orchestrator's prompt to\n"
                f"       Jon) and drop the subagent frontmatter. Point CONVERTER at a checkout\n"
                f"       that has it, or pass --no-subagents.")

    # Print BOTH paths every run. They can legitimately differ (worktree code, canonical
    # corpus) and the difference is exactly what went unnoticed before the gate above.
    print(f"Converter: {CONVERTER}")
    print(f"Corpus:    {OUT_DIR}")
    dirs = discover_proj_dirs()
    print(f"Discovered {len(dirs)} project dir(s) under {PROJECTS_ROOT}:")
    grand_jsonl, grand_bytes = 0, 0
    grand_sub, grand_sub_bytes = 0, 0
    for d in dirs:
        jsonls = list(d.glob('*.jsonl'))
        dir_bytes = sum(p.stat().st_size for p in jsonls)
        subs = list(d.glob('*/subagents/agent-*.jsonl'))
        sub_bytes = sum(p.stat().st_size for p in subs)
        grand_jsonl += len(jsonls)
        grand_bytes += dir_bytes
        grand_sub += len(subs)
        grand_sub_bytes += sub_bytes
        print(f"  {d.name}  → project={project_for_dir(d.name)}  "
              f"({len(jsonls)} jsonl, {dir_bytes:,} bytes"
              f"{f'; {len(subs)} subagent, {sub_bytes:,} bytes' if subs else ''})")
    print(f"  TOTAL: {grand_jsonl} jsonl, {grand_bytes:,} bytes"
          f"  |  {grand_sub} subagent jsonl, {grand_sub_bytes:,} bytes")
    print()

    written, refreshed, skipped, failed, empty = [], [], [], [], []

    for proj_dir, jsonl_path in (() if args.subagents_only else iter_session_jsonls()):
        uuid = jsonl_path.stem
        uuid6 = uuid[:6]
        project = project_for_dir(proj_dir.name)

        if args.list:
            msgs, title = quick_meta(jsonl_path)
            mtime = datetime.fromtimestamp(jsonl_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            md = "md✓" if existing_mds(uuid6) else "md✗"
            tag = f"{project}:{proj_dir.name}" if project == "triage" else project
            print(f"  {uuid6}  {msgs:>4} msgs  {mtime}  {md}  {tag:<8} {title[:44]}")
            continue

        md_paths = existing_mds(uuid6)
        need, reason = needs_extract(jsonl_path, md_paths, args.update)
        if not need:
            skipped.append((uuid6, reason))
            continue

        is_refresh = bool(md_paths)
        if args.dry_run:
            action = "REFRESH" if is_refresh else "EXTRACT"
            print(f"  [{action}] {uuid6}  ({reason})  project={project}")
            continue

        # On refresh, remove stale md(s) first so a changed slug can't leave a duplicate.
        # HELD IN MEMORY, NOT JUST DELETED (2026-08-03) — see hold_refresh() for why this
        # became load-bearing the moment the sidecar backfill widened this path.
        backup = hold_refresh(md_paths) if is_refresh else []

        title = quick_meta(jsonl_path)[1]  # aiTitle/custom-title → clean --slug
        # domain_subfolder only for genuinely NEW sessions — a refresh always rewrites at its
        # existing (possibly flat, grandfathered) path so existing wiki citations never break.
        ok, out = convert_one(jsonl_path, project, force=is_refresh, slug=title or None,
                              domain_subfolder=not is_refresh)
        if not ok:
            restore_refresh(backup)
            if session_is_empty(jsonl_path):
                empty.append(uuid6)
                continue
            failed.append((uuid6, out.strip().splitlines()[-1] if out.strip() else "unknown"))
            print(f"  FAIL {uuid6}: {out.strip()[:160]}")
            continue
        line = next((l for l in out.splitlines() if l.startswith(('WROTE', 'SKIP'))), out.strip()[:80])
        (refreshed if is_refresh else written).append((uuid6, line))
        print(f"  {'REFRESHED' if is_refresh else 'WROTE'} {uuid6}: {line}")

    # ---- subagent transcripts -------------------------------------------------
    sub_written, sub_refreshed, sub_skipped, sub_failed, sub_empty = [], [], [], [], []
    if args.subagents:
        if not args.list:
            print()
        for proj_dir, parent_uuid, jsonl_path, meta in iter_subagent_jsonls():
            agent_id = jsonl_path.stem[len('agent-'):]
            agent6 = agent_id[:6]
            parent6 = parent_uuid[:6]
            project = project_for_dir(proj_dir.name)
            atype = meta.get('agentType', '?')

            if args.list:
                mtime = datetime.fromtimestamp(jsonl_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                md = "md✓" if existing_subagent_mds(parent_uuid, agent_id) else "md✗"
                print(f"  sub {parent6}/{agent6}  {jsonl_path.stat().st_size:>9,} B  "
                      f"{mtime}  {md}  {project:<8} {atype[:18]:<18} "
                      f"{(meta.get('description') or '')[:40]}")
                continue

            md_paths = existing_subagent_mds(parent_uuid, agent_id)
            need, reason = needs_extract(jsonl_path, md_paths, args.update)
            if not need:
                sub_skipped.append((agent6, reason))
                continue

            is_refresh = bool(md_paths)
            if args.dry_run:
                action = "REFRESH" if is_refresh else "EXTRACT"
                print(f"  [{action}] sub {parent6}/{agent6}  ({reason})  project={project}")
                continue

            backup = hold_refresh(md_paths) if is_refresh else []

            # SIDECAR NOW ON FOR SUBAGENTS TOO (2026-08-03). The previous call passed
            # sidecar=False, and its reasoning was SOUND WHEN WRITTEN — quoted here rather
            # than deleted, because what changed is the world, not the logic:
            #
            #   "Subagent files carry no wiki citations (they had never been extracted),
            #    and 299 of 305 measured transcripts run on exactly ONE model — so a
            #    per-turn model column is a constant, and writing one would double the
            #    file count added to the corpus (305 -> 610) to restate the frontmatter."
            #
            # Both halves are now false.
            #
            # (1) IT IS NO LONGER A RESTATEMENT OF FRONTMATTER. Jon's rulings are delivered
            #     as mid-turn messages INTO running subagents — 130 measured on 2026-08-02,
            #     27 into a single consult. Subagent transcripts are therefore the primary
            #     record of Jon's own words, and the extract a future session reads carries
            #     NO turn-level time at all: a citation into one can say only
            #     [TRANSCRIPT:session-date] while the JSONL knows the minute. The
            #     near-constant MODEL column was the weak half of the old argument, and it
            #     was used to drop the TIMESTAMP column too — which is per-turn-varying by
            #     definition. That was the error, and it stayed invisible because nothing
            #     measured it. su_close.sh's `capture.temporal.subagents` row is added with
            #     this change so the same gap cannot sit unmeasured again.
            #
            # (2) "DOUBLE" WAS A FILE COUNT, NOT A COST. Measured 2026-08-03 by generating
            #     sidecars for four real subagent JSONLs spanning the size distribution of
            #     513 live files (min / median / p90 / max): a sidecar is 10.5%-36% of its
            #     primary's bytes, ~13% at the median. File count doubles; BYTES rise ~13%.
            #     write_subagent_index() already skips `*.sidecar.md`, so navigability —
            #     the thing file count actually threatened — is unchanged.
            #
            # The residual objection was discoverability, and that was a DEFECT rather than
            # a reason: until today the primary never NAMED its companion (67 sidecars on
            # disk, 0 files pointing at one). It does now — `sidecar_file:` frontmatter in
            # convert-claude-code.py — so the extra file is a followable pointer.
            #
            # Inline-in-body was never available and still is not: turn_index.py's header
            # regex is END-ANCHORED and covers `## Dispatch`, so appending a stamp to the
            # header would index every subagent file as ZERO turns, and inserting a metadata
            # line beneath it would shift every P anchor. The sidecar is the only placement
            # that touches no anchor, and it REUSES build_cc_sidecar_markdown() — the same
            # extract_turn_records() walk that produces the primary — so the two can never
            # disagree about which record is T{n}. A parallel frontmatter turn-table would
            # have been a second place turn numbering is computed: this repo's signature
            # failure, written down once and then diverging with nothing able to notice.
            ok, out = convert_one(
                jsonl_path, project, force=is_refresh, slug=subagent_slug(meta),
                domain_subfolder=False, out_dir=subagent_out_dir(parent_uuid),
                role=meta.get('agentType') or None)
            if not ok:
                restore_refresh(backup)
                if session_is_empty(jsonl_path):
                    sub_empty.append(agent6)
                    continue
                sub_failed.append((agent6, out.strip().splitlines()[-1] if out.strip() else "unknown"))
                print(f"  FAIL sub {parent6}/{agent6}: {out.strip()[:160]}")
                continue
            line = next((l for l in out.splitlines() if l.startswith(('WROTE', 'SKIP'))),
                        out.strip()[:80])
            (sub_refreshed if is_refresh else sub_written).append((agent6, line))
            print(f"  {'REFRESHED' if is_refresh else 'WROTE'} sub {parent6}/{agent6}: {line}")

    index_path, index_count = (None, 0)
    links_updated, links_total, links_skipped = (None, 0, [])
    if args.subagents and not args.list and not args.dry_run:
        index_path, index_count = write_subagent_index()
    if not args.list and not args.dry_run:
        # AFTER extraction, never before: a refresh rewrites the primary from the JSONL and
        # WIPES any block already in it, so the pass has to follow the writing.
        #
        # DELIBERATELY NOT GATED ON args.subagents (2026-08-03). The first version of this
        # sat inside the `if args.subagents` branch above, which meant `--no-subagents`
        # re-extracted primaries — destroying their blocks — and then skipped the pass that
        # rebuilds them, leaving the corpus worse than before the run. The link block is a
        # property of every extract, so its refresh belongs to every writing run.
        #
        # This is also why the block is DERIVED rather than stored anywhere else: two
        # extractor runs can race (a concurrent session extracting while this one links),
        # and the loser's blocks go stale. Because the pass is a pure function of the corpus
        # and idempotent, the next run repairs it and su_close.sh's links.bidirectional row
        # sees any window where it did not. Measured: a second pass immediately after the
        # first rewrote 0 of 682.
        links_updated, links_total, links_skipped = write_corpus_links()

    print()
    if args.list:
        n_sessions = 0 if args.subagents_only else sum(1 for _ in iter_session_jsonls())
        n_subs = sum(1 for _ in iter_subagent_jsonls()) if args.subagents else 0
        print(f"Listed {n_sessions} session(s) + {n_subs} subagent transcript(s) "
              f"across {len(dirs)} dir(s).")
    elif args.dry_run:
        print("(--dry-run: nothing written.)")
    else:
        # EMPTY is reported separately and quietly; Failed is reported loudly and now means
        # what it says, so a non-zero value is worth reading again. See session_is_empty().
        print(f"Sessions  — New: {len(written)}  Refreshed: {len(refreshed)}  "
              f"Skipped: {len(skipped)}  EMPTY: {len(empty)}  Failed: {len(failed)}")
        if empty:
            print(f"  EMPTY (no turns to extract, not a loss): {len(empty)}"
                  + (f" — {', '.join(sorted(empty))}" if args.verbose else " (--verbose for ids)"))
        for u6, r in failed:
            print(f"  FAILED {u6}: {r}")
        if args.subagents:
            print(f"Subagents — New: {len(sub_written)}  Refreshed: {len(sub_refreshed)}  "
                  f"Skipped: {len(sub_skipped)}  EMPTY: {len(sub_empty)}  Failed: {len(sub_failed)}")
            if sub_empty:
                print(f"  EMPTY sub (no turns to extract, not a loss): {len(sub_empty)}"
                      + (f" — {', '.join(sorted(sub_empty))}" if args.verbose else ""))
            for a6, r in sub_failed:
                print(f"  FAILED sub {a6}: {r}")
            if index_path:
                print(f"Index: {index_path}  ({index_count} subagent transcript(s))")
        if links_updated is not None:
            print(f"Links: {links_updated} block(s) rewritten / {links_total} extract(s)"
                  + (f"  SKIPPED (marker in body): {len(links_skipped)}" if links_skipped else ""))
            for p in links_skipped:
                print(f"  SKIPPED (marker in body): {p}")
        print(f"\nOutput dir: {OUT_DIR}")


if __name__ == "__main__":
    main()
