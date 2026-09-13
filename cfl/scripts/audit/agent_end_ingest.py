#!/usr/bin/env python3
"""agent_end_ingest.py — run I0 (anchor) and I1 (extract) AUTOMATICALLY when a subagent ends.

WHY THIS EXISTS
---------------
`wiki/references/update-levels-2026-07-31.md` is RATIFIED. Jon, verbatim, 2026-07-31:

    "I want to dig deep into the LEVELS within ingestion, which should happen at all compact
     bounderies (even those of managed agents), not just at agreed-upon session close rituals."

    SU = CAPTURE + I0 + I1 + I2 + DISPOSITION

I0 (anchor: transcript on disk, turns indexed, uuid joined) and I1 (extract: claims/decisions/
quotes with turn anchors, no view on importance) are both marked **automatic** and both fire at
**every compact boundary, including inside managed/background agents.** A subagent ending is such
a boundary. Until this script, nothing ran at it.

`route_agent_return.py` already records THAT a return happened — one PENDING ledger row. That is
CAPTURE. It deliberately does not extract ("Re-extraction is slow on a Drive-mounted repo"). That
deferral was measured and found false: 0.27s to convert a 1.1 MB subagent JSONL, 0.019s to write
600 KB to the Drive mount. So the reason for skipping I0/I1 at agent end no longer holds, and the
gap it left is expensive — measured 2026-08-06: 20 of 25 subagent returns unrouted, and on
2026-08-03 one unrouted consult held TWELVE of Jon's rulings that never reached the main thread.

WHAT THIS DOES, AND THE LINE IT DOES NOT CROSS
----------------------------------------------
* **I0** — delegates to the SINGLE canonical extractor path (`extract_claude_code_sessions`'s own
  `convert_one` -> `skills/chat-exporter/scripts/convert-claude-code.py`). It writes no transcript
  markdown itself. **Two parsers of one artifact is the divergence defect this repo spent the week
  removing**; this script imports the existing one instead of restating it.
* **I1** — a mechanical extract: Jon's mid-turn messages verbatim, the agent's final return, and
  lines matching a FIXED, PRINTED marker vocabulary. Every item carries a `T{n}` anchor derived
  from `turn_index.py` (the canonical indexer) or from the sidecar's timestamp map. **No ranking,
  no selection on merit, no summary.**
* **It does NOT synthesize.** No concept page, no cross-page reconciliation, no INGEST/SKIP call.
  Those are I2/I3 and remain wiki-master's in an interactive session. `skills/handoff/SKILL.md`:
  *"this skill records. Wiki-master synthesizes. Recording is not gated on merit; synthesis is."*
* **It never blocks.** Exit 0 on every path including its own internal errors — same discipline as
  `route_agent_return.py`, and for the same recorded reason: this repo has blocking rows whose
  steady state is "firing" and which are therefore ignored.

WHERE THINGS LAND — CORRECTED 2026-08-06, BY JON, AGAINST THIS SCRIPT'S FIRST DESIGN
------------------------------------------------------------------------------------
This script originally wrote every I1 extract into **gitignored** `raw/extracts/agent-end/` and put
only a *pointer page* in `wiki/`, on the reasoning that a subagent transcript can contain anything
that agent read and `wiki/` republishes to `canonical`. Jon overruled that, verbatim, 2026-08-06:

    "I'm not worried about anything sensitive landing in CFL. You don't need stronger fences.
     You need to stop adding conservatism into my words."

and, earlier in the same conversation, the instruction this script exists to serve:

    "Sounds like more needs to get into the wiki by default when agents end."

**Default means default.** Content outside the wiki with an index inside it, and nothing keeping
the two honest, is the memory-store shape this repo spent the week draining. A pointer to
gitignored content is not "in the wiki."

So the extracts land in tracked space:

  I0 anchor  -> raw/transcripts/claude-code/subagents/<parent6>/<stem>.md  (+ .sidecar.md)
                GITIGNORED corpus (it is the bulk mirror corpus and stays there — that is the
                standing `raw/` design, not a fence). Turns indexed; uuid joined.
  I1 extract -> wiki/intake-triage/agent-end/<parent6>/<stem>.i1.md
                **TRACKED.** The verbatim extract itself, in the wiki, by default.
  register   -> raw/extracts/agent-end/REGISTER.md
                GITIGNORED and machine-appended — it stays out of tracked space for an
                AVAILABILITY reason, not a safety one: it is append-only, two sessions append
                different rows, and a permanently-modified tracked file makes `SessionStart`'s
                `git pull --ff-only` abort. See LIVE_REGISTER below.

`wiki/intake-triage/` is the one `wiki/` path the ratified BGIsolation membrane already licenses
for deposits by something other than wiki-master (fable-mirror's escalation packets cross there),
and it is on `regenerate_canonical.sh`'s WIKI_PUBLISHED list.

THE ONE FENCE THAT REMAINS, AND WHOSE IT IS
-------------------------------------------
`wiki/personal`, `wiki/home`, `wiki/pro` stay excluded from the `canonical` branch. That is **Jon's
own ruling of 2026-07-25**, made after family medical and financial pages reached the connector,
and it lives in `scripts/lanes/regenerate_canonical.sh`. It is not extended here and nothing
adjacent to it is invented here. An extract that mentions a `wiki/personal/` path lands.

`scripts/audit/publication_screen.py` is the withdrawn screen. It is left on disk **unwired** and
is called by nothing.

WHY NOT NEXT TO THE TRANSCRIPT
------------------------------
Checked, not assumed. `existing_subagent_mds()` globs `*<agent6>*.md` in the subagent directory and
excludes only `*.sidecar.md`; `--update`'s refresh path then `unlink()`s everything it returns. An
`.i1.md` sitting in that directory would have been picked up as a primary extract and DELETED on
the next refresh — and `load_corpus_text()` in `scan_midturn_messages.py` rglobs the whole corpus,
so an I1 file containing Jon's quotes would have made that scanner report those quotes "present in
the corpus" even if the transcript extraction had failed. An instrument built to prove Jon's words
are not dropped would have been satisfied by this script's own output. `wiki/intake-triage/` is
enumerated by neither, which removes both hazards.

WHY THE TRACKED EXTRACT DOES NOT REPRODUCE THE REGISTER'S `git pull --ff-only` DEFECT
-------------------------------------------------------------------------------------
The register had to leave tracked space because it GROWS on every fire, so `git status` showed it
permanently `M`. An extract does not grow: each re-ingest rewrites the same path. The only thing
that would change on an identical re-fire is the `extracted_utc:` stamp — so the write is made
**content-stable**: `i1_content_sha256` hashes the file with that one volatile line removed, and a
re-fire whose hash matches skips the write entirely. A genuinely grown transcript does rewrite the
file, and `git status` showing that is correct — it is new content, not churn.

IDEMPOTENCE, BECAUSE SubagentStop IS NOT A ONCE-PER-AGENT EVENT
---------------------------------------------------------------
Measured 2026-08-06: eleven fires for a single agent inside one minute. Two guards:
  1. A done-marker keyed on (agent_id, jsonl size, jsonl mtime). Same bytes -> skip in
     milliseconds. A GROWN jsonl produces a new key and is re-extracted, which is correct.
  2. An O_EXCL lock so concurrent fires cannot both convert. Stale locks expire.
The marker is written LAST, after every artifact exists. A run killed by a hook timeout therefore
leaves no marker and is retried, rather than being recorded as done.

THIS SCRIPT'S OUTPUT IS PROVISIONAL, AND THAT IS NOW STATED IN THE ARTIFACT
---------------------------------------------------------------------------
`SubagentStop` has **no fixed point**. Routing a return is itself a return: when an agent routes its
own return the hook fires again, the transcript is longer, and this script emits a fresh extract
with a higher turn count. Measured 2026-08-06 on one agent: **101 turns at return 2, 135 at return
3.** `exchange/ROUTING-LEDGER.md` ("The self-routing stopping rule") documents the workaround that
held until 2026-08-06: declare the first row terminal and do not chase the count.

The recommendation on record was to move I0/I1 to parent-session close. That gives a real fixed
point — and trades away the property this placement was chosen for: **capture at agent end survives
a session that never closes cleanly**, and this repo has lost records exactly that way. So both run:

* **`SubagentStop` (here) keeps I0/I1 and marks its output `extract_status: PROVISIONAL`** — cheap,
  idempotent, crash-resilient, and honest about being mid-flight. The extract carries a banner
  saying its turn count is a floor.
* **`SessionEnd` performs FINALISATION** — `scripts/audit/session_finalise.py` re-extracts every
  subagent of the ended session, when they are genuinely final, and stamps `extract_status: FINAL`.
  That is the fixed point.

Usage:
  agent_end_ingest.py                        # hook mode: SubagentStop payload on stdin
  agent_end_ingest.py --jsonl PATH           # foreground run against one subagent transcript
  agent_end_ingest.py --jsonl PATH --force   # ignore the done-marker
  agent_end_ingest.py --jsonl PATH --final   # stamp the extract terminal (finaliser's entry point)
  agent_end_ingest.py --self-test            # negative controls
"""
import hashlib
import io
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_HERE = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent
for _p in (str(_SCRIPTS), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# --- REUSE, NOT REIMPLEMENTATION --------------------------------------------------------------
# Every import below is a deliberate refusal to write a second copy of something that exists.
import extract_claude_code_sessions as X          # noqa: E402  the canonical extractor
from scan_midturn_messages import midturn_messages  # noqa: E402  the wrapper-at-position-0 rule
import turn_index                                  # noqa: E402  the canonical turn indexer
import route_agent_return as RAR                   # noqa: E402  payload parsing + path derivation

# 2026-09-03 (found by the PP-2 probe's artifact path): X.ROOT is hardcoded to the G: clone, so once the
# N: clone became the working tree (09-02 21:4x) every SubagentStop ingest landed on a stale tree
# (35 on G: vs 2 on N: for session 71ce5a). Prefer the harness's own root; fall back to X.ROOT.
# ⛔ THE FALLBACK USED TO BE `or X.ROOT`, AND X.ROOT IS A HARDCODED ABSOLUTE PATH TO THE
# G: CLONE (extract_claude_code_sessions.py:69). So a hand run with CLAUDE_PROJECT_DIR unset
# wrote TRACKED FILES INTO A STALE CHECKOUT ON ANOTHER BRANCH, silently and successfully.
# [measured 2026-09-04 22:4x: the G: tree's uncommitted count GREW 3,140 -> 3,462 -> 3,491
# across twenty minutes while nobody was editing it -- Professional's restart gate R1.]
# ⭐ DERIVE THE CHECKOUT FROM THIS FILE, never from a recorded path: parents[2] of
# scripts/audit/<this>.py IS the repo that contains the code being run, in EVERY clone, and
# it cannot name a tree the caller is not in. (derive-don't-record, the trunk's own named
# characteristic failure.) X.ROOT remains correct where it is used as the CORPUS root.
_CHECKOUT = Path(__file__).resolve().parents[2]
REPO = Path(os.environ.get("CLAUDE_PROJECT_DIR") or _CHECKOUT)

# THE I1 EXTRACTS LAND IN THE WIKI, TRACKED, BY DEFAULT.
# Jon, 2026-08-06: "Sounds like more needs to get into the wiki by default when agents end." and
# "I'm not worried about anything sensitive landing in CFL. You don't need stronger fences."
# This path replaced gitignored `raw/extracts/agent-end/<parent6>/`, which is where the first
# version wrote them behind a pointer page. A pointer to gitignored content is not "in the wiki."
I1_ROOT = REPO / "wiki" / "intake-triage" / "agent-end"

# The pre-correction location. Still read by `--publish-existing` so extracts written before the
# ruling are migrated forward rather than stranded. Nothing there is ever deleted.
LEGACY_I1_ROOT = REPO / "raw" / "extracts" / "agent-end"
STATE_DIR = REPO / "raw" / "extracts" / "_state"

# THE LIVE REGISTER IS GITIGNORED, AND THAT IS A CORRECTION, NOT THE ORIGINAL DESIGN.
# It was first written to `wiki/intake-triage/agent-end-i1-register.md` — TRACKED space. Within
# three fires of going live, `git status` showed the file permanently `M`. That is not cosmetic:
# `SessionStart` runs `git pull --ff-only`, which ABORTS when a tracked file has local
# modifications. This repo has already been bitten by exactly this class (see the launcher
# git-pull collision: agents writing into `exchange/` and `intake-triage/` broke every run) — and
# the recorded fix there, hash-compare-then-stage, does NOT work here, because two sessions append
# DIFFERENT rows. Untracked-identical-content is recoverable; tracked-diverged is a real conflict
# on every session open, on every worktree.
#
# So THE REGISTER — and only the register — stays out of tracked space. That is an AVAILABILITY
# decision about an append-only file, not a safety fence about content: the I1 extracts themselves
# now land tracked in `wiki/` (see I1_ROOT above), because they are rewritten in place rather than
# grown, and a content-stable write makes an identical re-fire a no-op.
LIVE_REGISTER = REPO / "raw" / "extracts" / "agent-end" / "REGISTER.md"
WIKI_POINTER_PAGE = "wiki/intake-triage/agent-end-i1-register.md"

LOCK_STALE_S = 600
# --- STRUCK 2026-08-15 (SG-4, wiki/references/struck-gates.md) --------------------------------
# FINAL_RETURN_CAP = 8000     # chars; truncation is ANNOUNCED, never silent
#
# Measured destroying 100% of a 22,758-char audit report in TRACKED space: 65% cut by this cap
# to a pointer at a gitignored transcript path (not durable in tracked space either), and the
# surviving ~8,000-char stub then lost to the SECOND, independent bug this date also fixes: a
# later `SubagentStop` fire produced a shorter final return, and because `build_i1` rewrites the
# SAME tracked path IN PLACE, that fire's write silently replaced the richer prior return with a
# 443-char one. Net survival in tracked space: zero. See `all_return_texts()` below, which
# replaces `final_return_text()` and captures every return, not just the last, so a later fire's
# shorter final turn is additive rather than substitutive.
#
# Struck, not replaced: MR-13, from the 11,901 case — "strike the claim … do NOT re-cut, do NOT
# adopt 6,874." No new cap, no configurable default, per this file's own review instruction.
#
#   "Ground truth is ensuring nothing is deleted by accident or lost by accident." — 2026-08-03
#   "All must be recoverable, keep json." — 2026-08-09
MARKER_CAP_PER_RULE = 40    # shown cap; the TRUE count is always printed beside it

# The I1 marker vocabulary. FIXED and PRINTED INTO EVERY EXTRACT so a reader can see the rule that
# selected a line rather than trusting that something judged it important. Adding a rule here
# changes what future extracts contain; it does not reinterpret past ones, because each extract
# records the rule list it was built with.
MARKER_RULES = [
    ("ruling",      re.compile(r"\bJon (?:ruled|ruling|Gate|gate)\b|\bRATIFIED\b|\bratified\b")),
    ("decision",    re.compile(r"\bDECISION\b|\bDECIDED\b|\bI (?:chose|decided)\b")),
    ("unknown",     re.compile(r"\bUNKNOWN\b|\bUNVERIFIED\b|\bNOT VERIFIED\b|\bUNRESOLVABLE\b")),
    ("defect",      re.compile(r"\bDEFECT\b|\bBUG\b|\bFALSE POSITIVE\b|\bregression\b")),
    ("conflict",    re.compile(r"\bCONFLICT\b|\bCONTRADICT")),
    ("blocked",     re.compile(r"\bBLOCK(?:ED|ING|ER)\b|\bDEFERRED\b|\bHELD\b|\bTRIAGE\b")),
    ("retraction",  re.compile(r"\bRETRACT|\bI was wrong\b|\bWRONG\b|\bcorrection\b")),
    ("quote",       re.compile(r"\bverbatim\b|\bJon,? verbatim\b")),
    # --- ADDED 2026-08-06, answering Jon's question about what else should reach the wiki -------
    # These three name the categories Jon asked about (self-assessments, seeds) plus the one he did
    # not (an agent correcting its own dispatcher). They are rules, not rankings: a line either
    # matches the printed pattern or it does not, and the pattern is printed beside the count.
    # IGNORECASE on these two, and NOT on the others: both fire on phrases that routinely start a
    # sentence ("The brief said...", "Most likely wrong:..."), so a case-sensitive pattern misses
    # exactly the occurrences that matter. Caught by this file's own positive control, which failed
    # on a capital T before the flag was added. `seed` stays case-SENSITIVE because `\bSEED\b` is
    # meant to catch the uppercase register token and not the ordinary English word.
    ("self-assessment", re.compile(
        r"\bmost likely (?:to be )?wrong\b|\bleast confident\b|\bweakest (?:part|link|point|claim|"
        r"assumption)\b|\bI (?:may|might|could) be wrong\b|\bthe one thing (?:most likely|I)\b|"
        r"\bif I am wrong\b|\bif I'm wrong\b|\bself-assessment\b|\blowest confidence\b|"
        r"\bmy own (?:blind spot|error|mistake|assumption)\b", re.IGNORECASE)),
    ("seed", re.compile(
        r"\bfalsifier\b|\bfalsifiable\b|\bfalsif(?:y|ies|ied)\b|\bsynthesis seed\b|\bSEED\b|"
        r"\bseed candidate\b|\bhypothesis\b|\btestable claim\b")),
    ("brief-correction", re.compile(
        r"\bthe brief (?:is|was|says|said|claims|claimed|asserts|asserted|names|cites|cited)\b|"
        r"\byour brief\b|\bbrief'?s (?:premise|claim|number|citation|figure)\b|\bfalse premise\b|"
        r"\bthe dispatch (?:is|was|says|said|claims|claimed)\b|\bas briefed\b|\bmy dispatcher\b|"
        r"\bthe brief said\b", re.IGNORECASE)),
]

# The three rules above are ALSO given their own named sections in the extract, and their own
# frontmatter counts, so that they are findable without reading the body. Everything else stays in
# the marker table. This is an ORGANISATION decision, not a filter — see the ruling below.
PROMOTED_RULES = ("self-assessment", "seed", "brief-correction")

# Tools whose invocation is a mutation of disk. Used to build the ACTION LEDGER, which is the
# only defensible mechanical "summary" of an agent: not what it said it did, what it did.
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
_GIT_COMMIT_RE = re.compile(r"\bgit\s+(?:-c\s+\S+\s+)*commit\b")
_GIT_PUSH_RE = re.compile(r"\bgit\s+push\b")
ACTION_CAP = 60             # shown cap; the TRUE count is always printed beside it
SHORT_RETURN_CHARS = 200    # the measured threshold below which a return carries no content

SIDECAR_TURN_RE = re.compile(r"^###\s+T(\d+)\s*[\u2014\-]\s*(.+?)\s*$")
SIDECAR_TS_RE = re.compile(r"^-\s+timestamp:\s*(\S+)\s*$")


# ---------------------------------------------------------------------------------------------
# PATHS \u2014 REPO-RELATIVE, FORWARD-SLASHED. ONE FUNCTION, NOT FOUR.
#
# MEASURED DEFECT, 2026-08-06: 65 of 65 extracts in `f01909/` carried
#   `transcript_path: G:\My Drive\Claude\Claude Foundational Layer\claude-foundational-layer\raw\...`
# and the same for `sidecar_path`. Every one of those breaks on a clone, on a repo move, and in a
# WORKTREE \u2014 and worktrees are not exotic here, they are the standing rule: `CLAUDE.md` requires
# them to live at `%LOCALAPPDATA%\Temp\claude\wt-*`, i.e. at a DIFFERENT ROOT by construction. A
# pointer that only resolves from one directory on one machine is a pointer that has already
# expired for every reader but the one who wrote it.
#
# Forward slashes, always: this repo is read through PowerShell AND through Git Bash, and a
# backslash path is not a path to the second one.
#
# `disk_actions()` already had this logic as a local closure. It is hoisted rather than copied \u2014
# two implementations of one rule is the divergence defect this file's own header calls out.
# ---------------------------------------------------------------------------------------------
def repo_rel(p):
    """Repo-relative + forward-slashed when the path is inside the repo; forward-slashed absolute
    when it genuinely is not.

    The out-of-repo case is REAL and is not fudged: a subagent JSONL lives under
    `%USERPROFILE%\\.claude\\projects\\...`, which is not in this tree on any machine. Emitting a
    relative form for it would be a portable-looking lie, and a `../../../..` chain out of the repo
    is worse than an honest absolute. So the `..` result is rejected and the absolute is kept.
    """
    s = str(p)
    if not s or s == "ABSENT":
        return s
    try:
        r = os.path.relpath(s, REPO)
    except ValueError:          # different drive on Windows \u2014 genuinely outside this tree
        return s.replace("\\", "/")
    if r.startswith(".."):      # outside the repo (incl. the posixpath-on-a-Windows-path case)
        return s.replace("\\", "/")
    return r.replace("\\", "/")


# ---------------------------------------------------------------------------------------------
# TAGS \u2014 DERIVED PER EXTRACT, DESCRIPTIVE, AND EXPLICITLY NOT A TAXONOMY
#
# MEASURED DEFECT, 2026-08-06: 65 extracts, **ONE distinct `tags:` line between them.** Every file
# carried `agent-end, I1, subagent, capture, record-architecture` \u2014 five tags that describe THE
# MECHANISM THAT WROTE THE FILE and say nothing about what the file is about. Querying any of them
# returns all 65. **For retrieval that is worse than no tags at all**, because it looks like an
# index and answers nothing.
#
# The signal was already in the artifact and was being thrown away: the agent's own `description`
# (the same string the filename slug is cut from) and its `agentType`. Both are recorded fields
# already written into this very frontmatter block. So the subject tags are LIFTED FROM THE
# ARTIFACT'S OWN WORDS.
#
# WHAT THIS DELIBERATELY DOES NOT DO, AND WHY
# -------------------------------------------
# It does not assign extracts to categories. **Jon has an open, unanswered question about branch /
# sub-branch structure for the wiki**, and a controlled vocabulary invented here would pre-empt it \u2014
# the tags would be on disk, in 65 tracked files, before he ruled, and every later ruling would
# arrive as a migration instead of a decision. So: no `branch:` or `domain:` namespace, no fixed
# subject list, no bucketing. Only the artifact's own vocabulary, mechanically tokenized.
#
# It is also NOT CORPUS-RELATIVE. No "drop tokens that are common across the corpus" step, however
# tempting \u2014 that would make one extract's tags a function of every OTHER extract, so adding a file
# would silently change the tags of files nobody touched. A derived value that changes when
# unrelated data changes is this repo's characteristic bug wearing a different hat. The stopword
# list is FIXED and printed here.
#
# The five mechanism tags are KEPT. They are true, and they are the only way to select the whole
# class. The fix is additive: mechanism tags select the class, subject tags discriminate inside it.
# ---------------------------------------------------------------------------------------------
MECHANISM_TAGS = ("agent-end", "I1", "subagent", "capture", "record-architecture")

# A token is a word that STARTS with a letter and may carry internal hyphens, so `B-5`, `T-14`,
# `under-investment` and `session-store` survive as single tokens while bare numbers (`0`, `9`) do
# not become tags. Ticket ids are among the most discriminating things a description contains.
_TAG_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*")

# FIXED. Function words only \u2014 nothing domain-specific is filtered, because deciding that a domain
# word is uninteresting IS the taxonomy call this function refuses to make.
TAG_STOPWORDS = frozenset("""
a about all also an and any are as at be been before being between both but by can could did do
does doing done each even every for from further had has have having he her here him his how i if
in into is it its just me more most must my no nor not now of off on once only or other our out
over own re s same she should so some such t than that the their them then there these they this
those through to too under until up upon us very was we were what when where which while who whom
why will with within without would you your
""".split())

TAG_CAP = 12          # shown cap on subject tokens; the true token count is reported by --tag-audit
TAG_MIN_LEN = 2       # `su`, `b-5`, `t-02` are real; single letters are not


def derive_subject_tags(agent_type, description, cap=TAG_CAP):
    """[tag] \u2014 lowercase subject tags lifted from THIS agent's own type and description.

    Pure function of its two arguments. Same inputs -> same output, on any machine, regardless of
    what else is on disk. That property is what lets the in-place migration
    (`--rewrite-existing`) reproduce byte-for-byte what `build_i1` would write, instead of being a
    second implementation that drifts.
    """
    out = []
    seen = {t.lower() for t in MECHANISM_TAGS}

    def add(tok):
        tok = tok.strip("-").lower()
        if (len(tok) < TAG_MIN_LEN or tok in seen or tok in TAG_STOPWORDS
                or tok in ("unknown", "none")):
            return
        seen.add(tok)
        out.append(tok)

    # The role first: it is the single most-asked filter ("which extracts are Explore runs") and it
    # is a value the harness already assigned, not a category invented here.
    add(str(agent_type or ""))
    for m in _TAG_TOKEN_RE.finditer(str(description or "")):
        if len(out) >= cap:
            break
        add(m.group(0))
    return out


def tags_line(agent_type, description):
    """The full `tags:` frontmatter VALUE: mechanism tags (class selector) + subject tags."""
    return ", ".join(list(MECHANISM_TAGS) + derive_subject_tags(agent_type, description))


# ---------------------------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------------------------
def resolve_from_payload(payload):
    """(target_dict, reason). Reuses route_agent_return's field map AND its subagent-path
    derivation, so the ledger row and this ingest can never disagree about which file a return is.

    Returns None unless the derived subagent transcript was VERIFIED ON DISK. A payload whose
    transcript_path is the main conversation (the documented SubagentStop shape) is not a subagent
    transcript, and treating it as one would extract the parent session under the child's name.
    """
    fields = RAR.extract_fields(payload)
    if fields.get("transcript_source") != "derived-and-verified-on-disk":
        return None, (f"no subagent transcript on disk for id="
                      f"{(fields.get('id') or 'UNKNOWN')[:6]} "
                      f"(source={fields.get('transcript_source') or 'none'})")
    return resolve_from_jsonl(Path(fields["transcript"]))


def resolve_from_jsonl(jsonl):
    """(target_dict, reason) for one `<proj>/<parent-uuid>/subagents/agent-<id>.jsonl`."""
    jsonl = Path(jsonl)
    if not jsonl.is_file():
        return None, f"not a file: {jsonl}"
    if not jsonl.name.startswith("agent-") or jsonl.suffix != ".jsonl":
        return None, f"not a subagent transcript filename: {jsonl.name}"
    try:
        parent_uuid = jsonl.parents[1].name
        proj_dir_name = jsonl.parents[2].name
    except IndexError:
        return None, f"unexpected layout, cannot derive parent/project: {jsonl}"
    if jsonl.parents[0].name != "subagents":
        return None, f"not under a subagents/ directory: {jsonl}"
    agent_id = jsonl.stem[len("agent-"):]
    st = jsonl.stat()
    return {
        "jsonl": jsonl,
        "agent_id": agent_id,
        "agent6": agent_id[:6],
        "parent_uuid": parent_uuid,
        "parent6": parent_uuid[:6],
        "project": X.project_for_dir(proj_dir_name),
        "meta": X.read_agent_meta(jsonl),
        "size": st.st_size,
        "mtime": int(st.st_mtime),
    }, ""


def ingest_key(t):
    """(agent_id, size, mtime) — the same bytes must not be ingested twice; grown bytes must."""
    raw = f"{t['agent_id']}:{t['size']}:{t['mtime']}"
    return raw, hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


# ---------------------------------------------------------------------------------------------
# Idempotence
# ---------------------------------------------------------------------------------------------
def marker_path(t):
    return STATE_DIR / f"{t['agent_id']}.done.json"


def already_done(t, key_raw):
    p = marker_path(t)
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return False, None
    return rec.get("key") == key_raw, rec


def write_marker(t, key_raw, keyhash, result):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    rec = dict(result)
    rec.update({"key": key_raw, "keyhash": keyhash, "agent_id": t["agent_id"],
                "finished_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    tmp = marker_path(t).with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    os.replace(tmp, marker_path(t))


class Lock:
    """O_EXCL claim. Stale after LOCK_STALE_S so a killed run cannot wedge an agent forever."""

    def __init__(self, t):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.path = STATE_DIR / f"{t['agent_id']}.lock"
        self.held = False

    def acquire(self):
        for _ in range(2):
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(time.time()).encode())
                os.close(fd)
                self.held = True
                return True
            except FileExistsError:
                try:
                    age = time.time() - self.path.stat().st_mtime
                except OSError:
                    age = 0
                if age > LOCK_STALE_S:
                    try:
                        self.path.unlink()
                        continue
                    except OSError:
                        return False
                return False
            except OSError:
                return False
        return False

    def release(self):
        if self.held:
            try:
                self.path.unlink()
            except OSError:
                pass
            self.held = False


# ---------------------------------------------------------------------------------------------
# I0 — anchor
# ---------------------------------------------------------------------------------------------
RERENDER_RECORD_SLACK = int(os.environ.get("CFL_RERENDER_SLACK", "3"))


def _i0_would_be_a_noop(t, md_paths):
    """True when the transcript already on disk covers the JSONL as it stands right now.

    ⛔ WW-29, 2026-09-07. `[measured, raw/extracts/agent-end/REGISTER.md]` FOUR agents produced
    155 register rows in one day -- 123 / 18 / 13 / 1 -- rows two seconds apart, each one a FULL
    re-render of a transcript up to 331 KB. The idempotence key is `(agent_id, size, mtime)` and its
    docstring is right that "grown bytes MUST" re-ingest. What it could not anticipate is that this
    session RESUMED completed agents by message: every resume grows the JSONL and re-fires
    SubagentStop, so every re-fire is a NEW KEY, a new ingest and a new render.
    ⚠️ AN IDEMPOTENCE GUARD KEYED ON SIZE CANNOT DEDUPLICATE AN APPEND-ONLY FILE. The key is left
    ALONE -- it is correct for what it was written for -- and the WORK is bounded instead: ask the
    artifact whether it already covers the source, using the converter's own `total_records`, which
    is the same "read the artifact's own number rather than re-derive it" rule that fixed
    session_in_graph.py this afternoon.
    ⭐ A SKIP IS LOGGED, NEVER SILENT: a skipped step and an omitted step look identical to a reader
    unless one of them says so -- this repo's own rule, and the reason `cc_corpus_gap.py` prints
    SKIPPED rather than nothing."""
    if not md_paths:
        return False, None
    sc = X.sidecar_for(md_paths[0])
    if not sc or not sc.exists():
        return False, None
    recorded = None
    try:
        for line in io.open(str(sc), encoding="utf-8", errors="replace"):
            if line.startswith("total_records:"):
                recorded = int(line.split(":", 1)[1].strip())
                break
    except (OSError, ValueError):
        return False, None
    if recorded is None:
        return False, None
    live = 0
    try:
        with io.open(str(t["jsonl"]), encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.strip():
                    live += 1
    except OSError:
        return False, None
    return (live - recorded) <= RERENDER_RECORD_SLACK, {"recorded": recorded, "live": live}


def run_i0(t):
    """(ok, info). Delegates conversion to the canonical extractor. Writes no markdown itself."""
    out_dir = X.subagent_out_dir(t["parent_uuid"])
    md_paths = [p for p in X.existing_subagent_mds(t["parent_uuid"], t["agent_id"])]
    noop, counts = _i0_would_be_a_noop(t, md_paths)
    if noop:
        md = md_paths[0]
        idx = turn_index.index(str(md))
        return True, {"md": md, "sidecar": X.sidecar_for(md), "md_turns": idx["turn_count"],
                      "header_style": idx["header_style"], "turns": idx["turns"], "parity": None,
                      "refresh": True, "skipped": "SKIPPED-UNCHANGED",
                      "skip_detail": "transcript covers %d records; jsonl has %d (slack %d)" % (
                          counts["recorded"], counts["live"], RERENDER_RECORD_SLACK)}
    is_refresh = bool(md_paths)
    backup = X.hold_refresh(md_paths) if is_refresh else []
    ok, out = X.convert_one(
        t["jsonl"], t["project"], force=is_refresh, slug=X.subagent_slug(t["meta"]),
        domain_subfolder=False, out_dir=out_dir,
        role=(t["meta"].get("agentType") or None))
    if not ok:
        X.restore_refresh(backup)
        tail = (out or "").strip().splitlines()
        return False, {"error": tail[-1][:200] if tail else "converter failed, no output",
                       "refresh": is_refresh}
    found = X.existing_subagent_mds(t["parent_uuid"], t["agent_id"])
    if not found:
        return False, {"error": "converter reported success but no extract is on disk",
                       "refresh": is_refresh}
    md = found[0]
    sidecar = X.sidecar_for(md)

    # TURNS INDEXED — and cross-checked. turn_index.py counts headers in the markdown; the
    # sidecar's turns_covered comes from the JSONL walk. Equality is the parity check; a
    # mismatch is RECORDED, never fatal, because a wrong count is still better than no anchor.
    idx = turn_index.index(str(md))
    parity = X._turn_parity(t["jsonl"], sidecar) if sidecar.exists() else None
    return True, {
        "md": md, "sidecar": sidecar if sidecar.exists() else None,
        "md_turns": idx["turn_count"], "header_style": idx["header_style"],
        "turns": idx["turns"], "parity": parity, "refresh": is_refresh,
    }


def sidecar_timestamp_map(sidecar):
    """{timestamp -> (turn, role)} from the sidecar's own `### T{n}` / `- timestamp:` pairs.

    An EXACT join, not a text search: the mid-turn messages carry JSONL timestamps and the sidecar
    carries the same timestamps per turn, both produced by `extract_turn_records`. Verified on a
    real transcript before this was relied on (3/3 mid-turn timestamps present in the sidecar).
    """
    out = {}
    if not sidecar or not sidecar.exists():
        return out
    cur = None
    try:
        with open(sidecar, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = SIDECAR_TURN_RE.match(line.rstrip("\n"))
                if m:
                    cur = (int(m.group(1)), m.group(2))
                    continue
                m = SIDECAR_TS_RE.match(line.rstrip("\n"))
                if m and cur:
                    out.setdefault(m.group(1), cur)
    except OSError:
        pass
    return out


# ---------------------------------------------------------------------------------------------
# I1 — extract
# ---------------------------------------------------------------------------------------------
def line_turn_mapper(turns):
    """line number -> 'T{n} (role)'. Uses turn_index's own emitted turn list; no re-derivation."""
    starts = [(tr["line"], tr["t"], tr["role"]) for tr in turns]

    def which(lineno):
        hit = None
        for ln, tnum, role in starts:
            if ln <= lineno:
                hit = (tnum, role)
            else:
                break
        return f"T{hit[0]} ({hit[1]})" if hit else "pre-T1"
    return which


def collect_markers(md, which_turn):
    """[(rule, anchor, line)] plus true counts per rule. Mechanical match only — no ranking."""
    hits = {name: [] for name, _ in MARKER_RULES}
    totals = {name: 0 for name, _ in MARKER_RULES}
    try:
        lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return hits, totals
    mask = turn_index._fence_mask([l + "\n" for l in lines])
    for i, (line, infence) in enumerate(zip(lines, mask), start=1):
        s = line.strip()
        if infence or not s or s.startswith("#"):
            continue
        for name, rx in MARKER_RULES:
            if rx.search(s):
                totals[name] += 1
                if len(hits[name]) < MARKER_CAP_PER_RULE:
                    hits[name].append((which_turn(i), i, s[:400]))
    return hits, totals


def all_return_texts(md, turns):
    """[(anchor, text, length)] for EVERY `## Assistant` turn in the transcript, in order,
    full text, NEVER capped.

    Replaces the struck `final_return_text()`, which kept only the LAST assistant turn and is
    the second, independent bug named alongside the STRUCK FINAL_RETURN_CAP (SG-4, now struck):
    `SubagentStop` fires repeatedly for one agent (measured 2026-08-06: eleven fires for one agent inside one
    minute), and `build_i1` rewrites the same tracked `.i1.md` path IN PLACE on every fire whose
    content changed. Keeping only "the last" meant that if a later fire's transcript happened to
    END on a shorter assistant turn (e.g. a routing confirmation after a long substantive return),
    that fire's whole-file overwrite silently DISCARDED the earlier, richer return — nothing in
    the artifact showed a loss, because there was never a diff, only a replacement. Measured live
    2026-08-15: a 22,758-char report was down to `final_return_chars: 443` two fires later.

    Capturing every return fixes this without inventing a rule about which return matters: the
    last is still identified (it is what the orchestrator was actually handed), but every earlier
    one stays in the artifact, marked non-final, so a later shorter fire is ADDITIVE, never
    substitutive.
    """
    try:
        lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    out = []
    for tr in turns:
        if tr["role"] != "A":
            continue
        start = tr["line"]
        end = len(lines)
        for tr2 in turns:
            if tr2["line"] > start:
                end = tr2["line"] - 1
                break
        body = "\n".join(lines[start:end]).strip()
        out.append((f"T{tr['t']} (A)", body, len(body)))
    return out


def disk_actions(jsonl):
    """The ACTION LEDGER: what this agent actually did to disk, read from its own tool calls.

    WHY THIS EXISTS — MEASURED 2026-08-06
    -------------------------------------
    Jon asked whether agent SUMMARIES should reach the wiki. They should; the obvious
    implementation is wrong. The obvious implementation keeps the agent's RETURN, and on
    2026-08-06 three agents returned `"Done."`, `"."` and `"(no change)"` over real committed work,
    while a fourth returned a confident summary of files that were never written. Measured across
    this session's 62 extracts: **median return 2,633 chars, 8 returns under 200 chars, 6 empty.**

    **A return is a claim. The tool calls are the record.** So the summary is DERIVED — from the
    transcript, mechanically, with no judgment — and it is placed next to the return so a reader
    can compare the two without trusting either.

    This crosses no I1 line. Counting `tool_use` blocks and reading their `file_path` argument is
    the same grade of operation as counting turns: no ranking, no selection on merit, no prose.

    Returns a dict. Never raises.
    """
    tools = {}
    writes = []          # (tool, path) in call order
    commits = []         # verbatim git-commit command lines
    pushes = []
    total = 0
    try:
        with open(jsonl, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                msg = rec.get("message") or {}
                content = msg.get("content")
                if not isinstance(content, list):
                    continue
                for blk in content:
                    if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                        continue
                    name = blk.get("name") or "UNKNOWN"
                    inp = blk.get("input") if isinstance(blk.get("input"), dict) else {}
                    tools[name] = tools.get(name, 0) + 1
                    total += 1
                    if name in WRITE_TOOLS:
                        p = inp.get("file_path") or inp.get("notebook_path") or "UNKNOWN-PATH"
                        writes.append((name, str(p)))
                    elif name in ("Bash", "PowerShell"):
                        cmd = str(inp.get("command") or "")
                        if _GIT_COMMIT_RE.search(cmd):
                            commits.append(cmd.strip()[:300])
                        if _GIT_PUSH_RE.search(cmd):
                            pushes.append(cmd.strip()[:300])
    except OSError:
        pass

    # `repo_rel` is the module-level function, not a local copy of it. This closure used to BE the
    # only place the rule existed, which is why the frontmatter paths were absolute: the rule was
    # here and the frontmatter was elsewhere. One function now serves both.
    rel_writes = [(t, repo_rel(p)) for t, p in writes]
    distinct = sorted({p for _, p in rel_writes})
    return {
        "tools": tools, "tool_calls": total,
        "writes": rel_writes, "distinct_paths": distinct,
        "write_calls": len(rel_writes), "distinct_count": len(distinct),
        "commits": commits, "pushes": pushes,
    }


def claim_vs_record(ret_len, actions):
    """(flag, sentence) — a MECHANICAL comparison of two measured numbers, not a verdict.

    It states the discrepancy and both numbers. It never says which one is right: an agent can
    legitimately do heavy read-only research and return 6,000 characters with zero writes, and an
    agent can legitimately fix one character and say so in four words. The value is that the
    comparison is VISIBLE — the 2026-08-06 failure was a long, confident return over zero writes,
    and nothing in the record put those two facts side by side.
    """
    n = actions["distinct_count"]
    if ret_len < SHORT_RETURN_CHARS and n > 0:
        return ("SHORT-RETURN-OVER-WRITES",
                f"the return is {ret_len} chars (under the {SHORT_RETURN_CHARS}-char threshold) "
                f"while {n} distinct path(s) were written. **The return is not a usable record of "
                f"this agent's work; the ledger below is.**")
    if ret_len >= SHORT_RETURN_CHARS and n == 0:
        return ("RETURN-WITHOUT-WRITES",
                f"the return is {ret_len} chars and **zero paths were written by this agent**. "
                f"That is correct and expected for a read-only agent (Explore, cross-verifier, "
                f"lint-checker, fable-mirror). It is ALSO the exact shape of the 2026-08-06 "
                f"failure in which an agent returned a confident summary of work that did not "
                f"exist on disk. This flag does not distinguish the two — it makes the pair of "
                f"numbers visible so a reader can.")
    if ret_len < SHORT_RETURN_CHARS and n == 0:
        return ("SHORT-RETURN-NO-WRITES",
                f"the return is {ret_len} chars and no paths were written. Nothing here evidences "
                f"what this agent did; the transcript is the only record.")
    return ("", f"the return is {ret_len:,} chars and {n} distinct path(s) were written.")


_VOLATILE_LINES_RE = re.compile(
    r"^(?:extracted_utc|finalised_utc|i1_content_sha256|generated_utc|index_content_sha256):"
    r".*\r?\n", re.MULTILINE)

# --- PROVISIONAL vs FINAL ---------------------------------------------------------------------
# `SubagentStop` HAS NO FIXED POINT. Routing a return is itself a return: when an agent routes its
# own return the hook fires again, the transcript is longer, and this script emits a fresh extract
# with a higher turn count. Measured on one agent 2026-08-06: 101 turns at return 2, 135 at return
# 3. See `exchange/ROUTING-LEDGER.md`, "The self-routing stopping rule".
#
# The fix is NOT to move this script to session close — that would trade away the property
# `SubagentStop` was chosen for, namely that capture at agent end survives a session that never
# closes cleanly, and this repo has lost records exactly that way. Both run, with different jobs:
#
#   SubagentStop  -> STAGE_PROVISIONAL. Cheap, idempotent, crash-resilient. A MID-FLIGHT SNAPSHOT,
#                    and it says so IN THE ARTIFACT, so no reader mistakes it for a final one.
#   SessionEnd    -> STAGE_FINAL, via `scripts/audit/session_finalise.py`. Every subagent of the
#                    session is genuinely done; re-extracted once; marked terminal. The fixed point.
#
# `extract_status` is NOT in the volatile list above, deliberately: promoting an otherwise
# byte-identical extract from PROVISIONAL to FINAL MUST change its stable hash and MUST rewrite the
# file. If the status line were volatile the promotion would be a no-op and the distinction would be
# a label rather than a fact. That is the negative control in `self_test()`.
STAGE_PROVISIONAL = "PROVISIONAL"
STAGE_FINAL = "FINAL"


def read_i1_field(path, field):
    """One frontmatter scalar out of an existing extract, or None. Never raises."""
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:8000]
    except OSError:
        return None
    m = re.search(rf"^{re.escape(field)}:\s*(.+?)\s*$", head, re.MULTILINE)
    return m.group(1) if m else None


def stable_hash(text):
    """sha256 of an I1 extract with its two volatile frontmatter lines removed.

    This is what makes a TRACKED extract safe to rewrite on every SubagentStop fire. `SubagentStop`
    is not a once-per-agent event (eleven fires for one agent inside a minute, measured
    2026-08-06), and a tracked file that changes on every fire shows permanently `M`, which makes
    `SessionStart`'s `git pull --ff-only` abort. That defect is why the append-only REGISTER had to
    leave tracked space. An extract does not have to follow it: strip the timestamp, compare the
    hash, and an identical re-fire writes nothing at all.
    """
    return hashlib.sha256(_VOLATILE_LINES_RE.sub("", text).encode("utf-8")).hexdigest()


def existing_stable_hash(path):
    try:
        head = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r"^i1_content_sha256:\s*([0-9a-f]{64})\s*$", head, re.MULTILINE)
    return m.group(1) if m else None


def build_i1(t, i0, stage=STAGE_PROVISIONAL):
    """Write the I1 extract into TRACKED wiki space. Returns (path, counts).

    `stage` is PROVISIONAL (SubagentStop — mid-flight, the transcript may still grow) or FINAL
    (SessionEnd — the subagent is done and this extract is terminal). It is written into the
    artifact, not just into a log, because the whole defect being fixed here is a reader treating a
    mid-flight snapshot as the final one.
    """
    md, turns = i0["md"], i0["turns"]
    which = line_turn_mapper(turns)
    tsmap = sidecar_timestamp_map(i0["sidecar"])

    jon = []
    for ts, body in midturn_messages(t["jsonl"]):
        turn, role = tsmap.get(ts, (None, None))
        anchor = f"T{turn} ({role})" if turn else "UNKNOWN — timestamp not in sidecar turn map"
        jon.append((ts, anchor, body))

    returns = all_return_texts(md, turns)
    if returns:
        ret_anchor, ret_text, ret_len = returns[-1]
    else:
        ret_anchor, ret_text, ret_len = "no assistant turn found", "", 0
    hits, totals = collect_markers(md, which)
    acts = disk_actions(t["jsonl"])
    cvr_flag, cvr_sentence = claim_vs_record(ret_len, acts)

    meta = t["meta"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out_dir = I1_ROOT / t["parent6"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (md.name[:-3] + ".i1.md")

    b = io.StringIO()
    w = b.write
    w("---\n")
    # A wiki-tracked page needs the fields the wiki's own instruments read. These are added
    # because this file now lives in `wiki/`, not to dress it up: `retrieval_key` makes it
    # findable, and `coverage_class` keeps 40 mechanical extracts from silently moving the
    # citation-coverage denominator (the exemption is frontmatter-driven, per
    # `wiki/references/agent-memory/README.md`; a directory grants nothing).
    w(f"title: \"I1 extract — agent {t['agent6']} "
      f"({(meta.get('agentType') or 'UNKNOWN')})\"\n")
    w("source_kind: extract\n")
    w(f"retrieval_key: agent-end-i1-{t['agent6']}\n")
    # PER-EXTRACT SUBJECT TAGS. The five mechanism tags are kept (they select the class); the rest
    # are lifted from this agent's own type and description. See MECHANISM_TAGS / derive_subject_tags
    # for the measured defect this replaces — 65 extracts, one distinct tag line between them — and
    # for why no category vocabulary is invented here while Jon's branch question is open.
    w(f"tags: {tags_line(meta.get('agentType'), meta.get('description'))}\n")
    w("coverage_class: untraced-by-design\n")
    w("coverage_class_reason: mechanical I1 extract written automatically at SubagentStop; it "
      "makes no citable claim of its own and is excluded from citation-coverage measurement\n")
    w(f"source_id: agent-{t['agent_id']}\n")
    w("extract_level: I1\n")
    w("extract_kind: mechanical-claims-quotes-markers\n")
    w("judgment_applied: none\n")
    w(f"companion_of: {md.name}\n")
    # REPO-RELATIVE, FORWARD-SLASHED — see repo_rel(). These three were absolute
    # `G:\My Drive\...` paths in all 65 extracts of session f01909 and resolved from exactly one
    # directory on one machine. `jsonl_path` stays absolute and SAYS SO by staying absolute: the
    # subagent JSONL lives under `%USERPROFILE%\.claude\projects\`, outside this tree on every
    # machine, and a relative form there would be portable-looking and false.
    w(f"transcript_path: {repo_rel(md)}\n")
    w(f"sidecar_path: {repo_rel(i0['sidecar']) if i0['sidecar'] else 'ABSENT'}\n")
    w(f"jsonl_path: {repo_rel(t['jsonl'])}\n")
    w(f"agent_id: {t['agent_id']}\n")
    w(f"agent_type: {meta.get('agentType') or 'UNKNOWN'}\n")
    w(f"agent_description: {(meta.get('description') or 'UNKNOWN')}\n")
    w(f"parent_session: {t['parent_uuid']}\n")
    w(f"project: {t['project']}\n")
    w(f"turn_count: {i0['md_turns']}\n")
    w(f"turn_parity: {('sidecar=%d rederived=%d %s' % (i0['parity'][0], i0['parity'][1], 'MATCH' if i0['parity'][0] == i0['parity'][1] else 'MISMATCH')) if i0['parity'] else 'UNKNOWN — not derivable'}\n")
    w(f"header_style: {i0['header_style']}\n")
    w(f"jon_midturn_messages: {len(jon)}\n")
    w(f"marker_totals: {json.dumps(totals)}\n")
    # --- THE FIELDS THE GENERATED INDEX READS ------------------------------------------------
    # Jon, 2026-08-06: *"if this would make the wiki unnavicable, then you just don't have good
    # enough wiki orginization."* Volume is not the constraint; organisation is. So nothing is
    # withheld — instead every extract carries, IN ITS FRONTMATTER, the counts that let
    # `build_index()` build a navigable table WITHOUT opening any body. An index that must read 62
    # bodies is an index that will not be regenerated; an index built from 62 frontmatter blocks
    # costs one read of the first 8 KB of each.
    w(f"self_assessments: {totals.get('self-assessment', 0)}\n")
    w(f"seeds: {totals.get('seed', 0)}\n")
    w(f"brief_corrections: {totals.get('brief-correction', 0)}\n")
    w(f"tool_calls: {acts['tool_calls']}\n")
    w(f"write_calls: {acts['write_calls']}\n")
    w(f"distinct_paths_written: {acts['distinct_count']}\n")
    w(f"commit_commands: {len(acts['commits'])}\n")
    w(f"push_commands: {len(acts['pushes'])}\n")
    w(f"final_return_chars: {ret_len}\n")
    # STRUCK 2026-08-15 (SG-4): this used to be capped at FINAL_RETURN_CAP=8000 and only the last
    # assistant turn was ever counted. Both are gone — see all_return_texts(). These two fields
    # make the fix visible in frontmatter, without opening the body: every return's full length is
    # now on disk, not just the final one's.
    w(f"returns_count: {len(returns)}\n")
    w(f"total_return_chars: {sum(l for _, _, l in returns)}\n")
    w(f"claim_vs_record: {cvr_flag or 'none'}\n")
    # The stage fields. `extract_status` is load-bearing and NON-volatile — see STAGE_PROVISIONAL.
    # `jsonl_size`/`jsonl_mtime` record WHICH BYTES this extract was built from, so a later run can
    # tell "already final at these exact bytes" (skip, no disk work) from "grew after being marked
    # final" (a real supersession, which must demote and re-extract rather than be silently kept).
    w(f"extract_status: {stage}\n")
    w(f"jsonl_size: {t['size']}\n")
    w(f"jsonl_mtime: {t['mtime']}\n")
    w(f"extracted_utc: {now}\n")
    w(f"finalised_utc: {now if stage == STAGE_FINAL else '-'}\n")
    if stage == STAGE_FINAL:
        w("produced_by: scripts/audit/session_finalise.py (SessionEnd, automatic) via "
          "scripts/audit/agent_end_ingest.py\n")
    else:
        w("produced_by: scripts/audit/agent_end_ingest.py (SubagentStop, automatic)\n")
    w("---\n\n")

    w(f"# I1 extract — agent-{t['agent_id']} ({meta.get('agentType') or 'UNKNOWN'})\n\n")

    # --- THE STAGE BANNER, IN THE ARTIFACT ---------------------------------------------------
    if stage == STAGE_FINAL:
        w("> **FINAL — this extract is terminal.** It was rebuilt at `SessionEnd`, when the parent "
          "session had stopped and this subagent could no longer be resumed, so the transcript "
          "behind it cannot grow further. Cite it without checking for a newer one.\n>\n"
          "> If the underlying JSONL ever *does* grow again (a resumed session reusing the same "
          "id), the next run demotes this file back to PROVISIONAL and re-extracts. Silence is not "
          "used to preserve a finality claim that stopped being true.\n\n")
    else:
        w("> **PROVISIONAL — this is a mid-flight snapshot, not the final extract.** It was written "
          "at a `SubagentStop` fire, and `SubagentStop` has no fixed point: **routing a return is "
          "itself a return.** When an agent routes or reports its own return the hook fires again, "
          "its transcript is longer, and a fresh extract supersedes this one. Measured on one agent "
          "2026-08-06: **101 turns at return 2, 135 at return 3.**\n>\n"
          "> **So the turn count below is a floor, not a total,** and this file may be short of the "
          "agent's last turns — including its final return. The terminal version is written at "
          "`SessionEnd` by `scripts/audit/session_finalise.py` and carries "
          "`extract_status: FINAL`. **Do not open a follow-up to \"fix\" this turn count** — that "
          "follow-up is the next iteration of the same loop "
          "(`exchange/ROUTING-LEDGER.md`, \"The self-routing stopping rule\").\n\n")

    w("**This is an I1 extract, not a page.** Per `wiki/references/update-levels-2026-07-31.md` "
      "(RATIFIED 2026-07-31), I1 produces *claims/decisions/quotes with turn anchors, no view on "
      "importance*. Nothing here has been selected on merit, ranked, summarized, or reconciled "
      "against any other page. Every item below was matched by a stated mechanical rule, and the "
      "rule is printed beside it. Turning any of this into a wiki page is I2/I3 — wiki-master's "
      "call in an interactive session, not this script's.\n\n")
    w(f"Anchors are `T{{n}}` against `{md.name}` as counted by `scripts/audit/turn_index.py`. "
      f"Timestamps are joined to turns through the sidecar, which is produced by the same "
      f"`extract_turn_records` walk as the transcript, so the two cannot disagree about which "
      f"record is `T{{n}}`.\n\n")

    # --- 1. Jon -------------------------------------------------------------------------------
    w("## 1. Jon's mid-turn messages (verbatim)\n\n")
    w("Rule: a `type: user` record whose text BEGINS with the harness wrapper "
      "*\"The user sent a new message while you were working:\"* — position 0, `isMeta` not "
      "required. This is `scan_midturn_messages.midturn_messages()`, imported rather than "
      "restated. These are **Jon's own words delivered into a running agent**; on 2026-08-02 "
      "the main thread's system reminders said \"no human input\" while nine of them were "
      "arriving, and on 2026-08-03 twelve rulings ended in an unrouted consult. Nothing here is "
      "paraphrased and nothing is omitted.\n\n")
    w("**Read the anchors against a known mislabel.** In a subagent transcript the converter emits "
      "every user-role string record under `## Dispatch`, and that heading carries a standing "
      "banner saying it is *\"not a message from Jon\"* and *\"does not carry Jon's authority.\"* "
      "That banner is right about an orchestrator's brief and WRONG about the turns anchored in "
      "this section — these are Jon speaking, identified by the harness wrapper, which no brief "
      "carries at position 0. The transcript's role letter is therefore not the authority signal "
      "here; this section is. Nothing was renumbered to fix it: shifting turn numbers would "
      "invalidate every existing citation into the file.\n\n")
    if not jon:
        w("_None in this transcript._ **Absence is not evidence Jon was silent** — it is evidence "
          "no message arrived through this channel in this agent.\n\n")
    for i, (ts, anchor, body) in enumerate(jon, start=1):
        w(f"### J{i} — {anchor} — `{ts}`\n\n")
        w("```text\n" + body.replace("```", "`\u200b``") + "\n```\n\n")

    # --- 2. Returns ------------------------------------------------------------------------------
    # STRUCK 2026-08-15 (SG-4): this section used to keep ONLY the last `## Assistant` turn, capped
    # at FINAL_RETURN_CAP=8000 chars. Both are struck. See all_return_texts() for why "last only"
    # was itself a second, independent bug (a later, shorter fire silently overwrote a richer
    # earlier return in place) and struck-gates.md SG-4 for the register entry.
    w(f"## 2. The agent's returns (verbatim, every assistant turn, none capped) \u2014 "
      f"{len(returns)} found\n\n")
    w(f"Rule: EVERY `## Assistant` turn in the transcript, in order, full text, never truncated. "
      f"**The LAST is what the orchestrator was handed** \u2014 anchor **{ret_anchor}**, "
      f"{ret_len:,} chars. Earlier returns are shown too and marked non-final: `SubagentStop` "
      f"fires repeatedly for one agent, `build_i1` rewrites this same tracked path in place on "
      f"every fire, and keeping only \"the last\" meant a later, shorter fire could silently "
      f"discard a genuinely richer prior return with no trace of the loss. Capturing every return "
      f"makes a later fire additive rather than substitutive.\n\n")
    if not returns:
        w("_No assistant turn found in this transcript._\n\n")
    for i, (anchor, text, length) in enumerate(returns, start=1):
        tag = "FINAL \u2014 handed to the orchestrator" if i == len(returns) else "non-final"
        w(f"### Return {i} of {len(returns)} \u2014 {anchor} \u2014 {tag} \u2014 {length:,} chars\n\n")
        if text:
            w("```text\n" + text.replace("```", "`\u200b``") + "\n```\n\n")
        else:
            w("_Empty._\n\n")

    # --- 3. The action ledger — the DERIVED summary ---------------------------------------------
    w("## 3. What this agent did to disk (derived, mechanical)\n\n")
    w("**This is the summary. It is derived from the agent's own tool calls in the JSONL, never "
      "from what the agent said it did.** Jon asked whether summaries should reach the wiki; they "
      "should, and the obvious implementation — keep the return — is the one that fails. Measured "
      "2026-08-06 across this session's extracts: **median return 2,633 chars, 8 returns under "
      "200 chars, 6 empty**, over real committed work; and one agent returned a confident summary "
      "of files that were never written. **A return is a claim; the tool calls are the record.** "
      "Both are in this file, adjacent, so neither has to be trusted alone.\n\n")
    w(f"**Claim vs record{(' — ' + cvr_flag) if cvr_flag else ''}:** {cvr_sentence}\n\n")
    if cvr_flag:
        w("_This flag is a comparison of two measured numbers, not a verdict. It does not say the "
          "agent was wrong; it says the two numbers differ in a way worth a reader's eye._\n\n")
    w("| tool | calls |\n|---|---|\n")
    for name in sorted(acts["tools"], key=lambda k: (-acts["tools"][k], k)):
        w(f"| {name} | {acts['tools'][name]} |\n")
    if not acts["tools"]:
        w("| _none recorded_ | 0 |\n")
    w(f"\n**Denominator:** {acts['tool_calls']} `tool_use` block(s) read from "
      f"`{t['jsonl'].name}`; of those, {acts['write_calls']} were calls to "
      f"{'/'.join(WRITE_TOOLS)}, touching **{acts['distinct_count']} distinct path(s)**. "
      f"Scope: **this subagent's own transcript only** — work it delegated further, or work done "
      f"by the parent session, is not counted here and this file makes no claim about it.\n\n")

    w(f"### Paths written — {acts['distinct_count']} distinct, "
      f"{min(acts['distinct_count'], ACTION_CAP)} shown\n\n")
    if not acts["distinct_paths"]:
        w("_None._ This agent wrote no files. For a read-only role (Explore, cross-verifier, "
          "lint-checker, fable-mirror) that is the expected result and not a finding.\n\n")
    for p in acts["distinct_paths"][:ACTION_CAP]:
        w(f"- `{p}`\n")
    if acts["distinct_count"] > ACTION_CAP:
        w(f"\n**{acts['distinct_count'] - ACTION_CAP} further path(s) not shown** — the true count "
          f"is {acts['distinct_count']}, printed here rather than left to be inferred from the "
          f"length of the list.\n")
    w("\n")

    w(f"### Commits — {len(acts['commits'])} `git commit` invocation(s), "
      f"{len(acts['pushes'])} `git push`\n\n")
    if not acts["commits"]:
        w("_None._ **This is not evidence the work was uncommitted** — an agent's writes are "
          "frequently committed by its parent session, which is a different transcript. It is "
          "evidence only that *this* agent did not run the command.\n\n")
    for c in acts["commits"][:ACTION_CAP]:
        w("```text\n" + c.replace("```", "`​``") + "\n```\n")
    if acts["pushes"]:
        w("\n**`git push` invocations recorded:**\n\n")
        for c in acts["pushes"][:ACTION_CAP]:
            w("```text\n" + c.replace("```", "`​``") + "\n```\n")
    w("\n")

    # --- 4. The three named categories -----------------------------------------------------------
    # The heading is written from the SAME CONSTANT the index parser looks for, so the two cannot
    # drift. They did not drift; something worse happened — a quoted `## 4.` inside an agent's own
    # return matched a prefix test. See category_lines().
    w(SECTION4_HEADING + "\n\n")
    w("**These three are lifted into their own section, and into frontmatter counts, because they "
      "are the categories a reader comes looking for.** They are not filtered, ranked, or judged — "
      "every one of them also appears in the marker table below under the same rule name. This "
      "section is an INDEXING affordance, not a selection.\n\n")
    w("Jon, 2026-08-06, on the alternative: *\"if this would make the wiki unnavicable, then you "
      "just don't have good enough wiki orginization.\"* **Volume is not the constraint; "
      "organisation is.** So nothing is withheld to keep the wiki small — the wiki is made "
      "navigable instead.\n\n")
    w("**Why `brief-correction` is here at all, since Jon did not name it.** It is the only signal "
      "in this system that runs *against* the authority gradient: a self-assessment is an agent "
      "grading itself, and the standing guard rule is that *a falsifier may not be judged by its "
      "author*. A correction to the brief is an agent grading its **dispatcher**. On 2026-08-06 "
      "that channel produced four coordinator errors — a false premise about three register "
      "closes, a stale zip path, a \">300s\" runtime that was 79s, and a wrong register citation — "
      "**and the coordinator found none of them itself.** It is the intra-session form of the "
      "Herald channel, whose standing rule in `CLAUDE.md` is that *every correction that landed on "
      "2026-07-27 came from the other project; neither coordinator found its own.* A channel with "
      "no consumer is the same defect as a deposit-only queue — so these lines are named, counted "
      "in frontmatter, and surfaced in the generated index, not left inside a 14 KB extract.\n\n")
    for rule in PROMOTED_RULES:
        w(f"### `{rule}` — {totals.get(rule, 0)} matched, {len(hits.get(rule, []))} shown\n\n")
        if not hits.get(rule):
            w(f"_No line in this transcript matched the `{rule}` rule._ **Absence here is "
              f"absence of a MATCH, not absence of the thing** — the rule is a fixed printed "
              f"pattern (see the marker table below) and a claim phrased outside it is simply not "
              f"caught.\n\n")
            continue
        for anchor, lineno, text in hits[rule]:
            w(f"- **{anchor}** (line {lineno}) — {text}\n")
        if totals.get(rule, 0) > len(hits[rule]):
            w(f"\n**{totals[rule] - len(hits[rule])} further match(es) not shown** (cap "
              f"{MARKER_CAP_PER_RULE}); the true count is {totals[rule]}.\n")
        w("\n")

    # --- 5. Markers ---------------------------------------------------------------------------
    w(SECTION5_HEADING + "\n\n")
    w("Rules are FIXED and listed here so a reader can see what selected each line. Lines inside "
      "fenced code blocks are excluded (`turn_index._fence_mask`, the run-length-aware one). "
      "Headings are excluded. **The TRUE count is printed even where the shown list is capped at "
      f"{MARKER_CAP_PER_RULE}** — a shown count that silently equalled a cap would be a lying "
      "denominator, which is this repo's recorded failure mode.\n\n")
    w("| rule | pattern | matched | shown |\n|---|---|---|---|\n")
    for name, rx in MARKER_RULES:
        w(f"| {name} | `{rx.pattern}` | {totals[name]} | {len(hits[name])} |\n")
    w("\n")
    for name, _ in MARKER_RULES:
        if not hits[name]:
            continue
        w(f"### rule `{name}` — {totals[name]} matched, {len(hits[name])} shown\n\n")
        for anchor, lineno, text in hits[name]:
            w(f"- **{anchor}** (line {lineno}) — {text}\n")
        w("\n")

    w("## What this extract does NOT claim\n\n")
    w("- That any of it is important. I1 applies no judgment; that is the level's definition.\n")
    w("- That the agent's conclusions were accepted. A subagent cannot ratify. The parent "
      "session's transcript is the record of what was actually accepted.\n")
    w("- That the marker vocabulary is complete. It is a fixed list, printed above; a claim "
      "phrased outside it is simply not matched, and this file says so rather than implying "
      "coverage it does not have.\n")
    w("- That it was screened. **It was not.** Jon, 2026-08-06: *\"I'm not worried about anything "
      "sensitive landing in CFL. You don't need stronger fences.\"* This file lands in `wiki/` by "
      "default, unfiltered, because that is the instruction. The one exclusion still in force is "
      "his own 2026-07-25 canonical-branch ruling on `wiki/personal|home|pro`, which is enforced "
      "in `scripts/lanes/regenerate_canonical.sh` and is not extended here.\n")

    doc = b.getvalue()
    # Content-stable write. Insert the hash of the doc-minus-volatile-lines, then skip the write
    # entirely if the file on disk already carries it. See stable_hash() for why this matters for
    # a TRACKED path in particular.
    sha = stable_hash(doc)
    doc = doc.replace(f"extracted_utc: {now}\n",
                      f"extracted_utc: {now}\ni1_content_sha256: {sha}\n", 1)
    counts = {"jon": len(jon), "markers_total": sum(totals.values()),
              "markers": totals, "final_return_chars": ret_len,
              "returns_count": len(returns),
              "total_return_chars": sum(l for _, _, l in returns),
              "self_assessments": totals.get("self-assessment", 0),
              "seeds": totals.get("seed", 0),
              "brief_corrections": totals.get("brief-correction", 0),
              "distinct_paths_written": acts["distinct_count"],
              "commit_commands": len(acts["commits"]),
              "tool_calls": acts["tool_calls"], "claim_vs_record": cvr_flag,
              "sha": sha, "stage": stage, "write": "written"}
    if out_path.exists() and existing_stable_hash(out_path) == sha:
        counts["write"] = "unchanged"
        return out_path, counts

    # NON-DOWNGRADE GUARD. A provisional fire must never overwrite a FINAL extract built from the
    # SAME BYTES — that would relabel a terminal artifact as mid-flight for no reason. But if the
    # JSONL has GROWN since finalisation, the finality claim is no longer true, and the honest act
    # is to demote and re-extract rather than protect the label. So the guard is keyed on bytes,
    # not on status.
    if stage == STAGE_PROVISIONAL and out_path.exists():
        if read_i1_field(out_path, "extract_status") == STAGE_FINAL:
            prior_size = read_i1_field(out_path, "jsonl_size")
            prior_mtime = read_i1_field(out_path, "jsonl_mtime")
            if prior_size == str(t["size"]) and prior_mtime == str(t["mtime"]):
                counts["write"] = "kept-final"
                return out_path, counts
            counts["demoted_from_final"] = True
    out_path.write_text(doc, encoding="utf-8")
    return out_path, counts


# ---------------------------------------------------------------------------------------------
# The wiki-visible anchor
# ---------------------------------------------------------------------------------------------
REGISTER_HEADER = """---
title: "Agent-end I0/I1 register (LIVE, gitignored)"
source_kind: tracker
retrieval_key: agent-end-i1-register-live
status: AUTOMATIC — appended by scripts/audit/agent_end_ingest.py on SubagentStop
maintained_by: automatic (rows); wiki-master (any synthesis from them)
tags: ingestion-levels, I0, I1, subagent, standard-update, record-architecture
---

# Agent-end I0/I1 register — LIVE

**This file is GITIGNORED and machine-appended. Do not track it.** The tracked, human-authored
pointer to it is `wiki/intake-triage/agent-end-i1-register.md`; that page is static and describes
how to read this one.

**Why it lives outside tracked space.** It was first written into `wiki/intake-triage/`. Three live
fires later `git status` showed it permanently `M`, and `SessionStart` runs `git pull --ff-only`,
which aborts when a tracked file is locally modified. Two sessions append DIFFERENT rows, so the
recorded hash-compare-then-stage fix for the launcher collision does not apply — this would be a
genuine conflict at every session open, on every worktree. A capture control that breaks session
startup gets deleted, and then nothing is captured at all.

**That is an availability reason, not a content one.** The `i1_extract` column points into
`wiki/intake-triage/agent-end/`, which is TRACKED and does reach the connector — Jon, 2026-08-06:
*"Sounds like more needs to get into the wiki by default when agents end"* and *"I'm not worried
about anything sensitive landing in CFL. You don't need stronger fences."* Only this append-only
ledger stays out, and only because an append-only tracked file breaks `git pull --ff-only`.

Every row is one subagent that ended and was anchored (I0) and extracted (I1) automatically, per
`wiki/references/update-levels-2026-07-31.md` (RATIFIED 2026-07-31): *"SU = CAPTURE + I0 + I1 + I2
+ DISPOSITION"*, with I0 and I1 firing at **every compact boundary, including inside managed
agents**.

**These rows are I0/I1 only.** No INGEST/SKIP decision has been made about any of them. That is
I2/I3 and belongs to wiki-master in an interactive session. A row here means *recorded*, never
*accepted* — recording is not gated on merit; synthesis is.

**A ROW IS AN INGEST EVENT, NOT AN AGENT. Do not count rows to count agents.** `SubagentStop` fires
repeatedly for one agent, and the transcript keeps GROWING between fires — observed live on
2026-08-06: the same agent `ac24af` produced a 128-turn row and then a 132-turn row 28 seconds
later. Both are true; the second supersedes the first. **For any `id6`, the LAST row is current and
every earlier row is a superseded snapshot.** Distinct agents = distinct `id6` values, which is
`sort -u` on that column, never the row count. Earlier rows are not edited or deleted — this is an
append-only ledger, and a ledger that rewrites its own history cannot be audited — so the
supersession is expressed by ordering, and stated here so nobody reads the row count as a
population. The corpus artifacts do NOT accumulate: each re-ingest overwrites the same transcript,
sidecar, and `.i1.md` in place, so only the register grows, by ~250 bytes per event.

| ingested_utc | id6 | role | description | turns | parity | jon_msgs | markers | transcript | i1_extract | key |
|---|---|---|---|---|---|---|---|---|---|---|
"""


def append_register(t, i0, i1_path, counts, keyhash):
    """Append ONE row to the GITIGNORED live register. Never writes under `wiki/`.

    No verbatim content. Idempotent on the ingest keyhash.
    """
    path = LIVE_REGISTER
    meta = t["meta"]
    parity = (f"{i0['parity'][0]}={i0['parity'][1]}" if i0["parity"] and
              i0["parity"][0] == i0["parity"][1]
              else (f"MISMATCH {i0['parity'][0]}!={i0['parity'][1]}" if i0["parity"]
                    else "UNKNOWN"))
    desc = (meta.get("description") or "UNKNOWN").replace("|", "/")[:70]
    role = (meta.get("agentType") or "UNKNOWN").replace("|", "/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        md_rel = os.path.relpath(i0["md"], REPO).replace("\\", "/")
        i1_rel = os.path.relpath(i1_path, REPO).replace("\\", "/")
    except ValueError:
        md_rel, i1_rel = str(i0["md"]), str(i1_path)
    # The stage rides INSIDE the existing `turns` cell rather than as a 12th column. A new column
    # would make every row already in the live file ragged, and this is an append-only ledger whose
    # history is not rewritten. `121 (FINAL)` costs nothing and keeps the table parseable.
    turns_cell = f"{i0['md_turns']} ({counts.get('stage', STAGE_PROVISIONAL)})"
    # The dedupe key carries the stage. A FINAL run over bytes an earlier PROVISIONAL run already
    # saw has the SAME (agent_id, size, mtime) — so without this the finalisation row would be
    # suppressed as a duplicate and the ledger would never show that anything was made terminal.
    if counts.get("stage") == STAGE_FINAL:
        keyhash = f"{keyhash}f"
    row = (f"| {now} | {t['agent6']} | {role} | {desc} | {turns_cell} | {parity} | "
           f"{counts['jon']} | {counts['markers_total']} | `{md_rel}` | `{i1_rel}` | {keyhash} |")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        if keyhash and f"| {keyhash} |" in existing:
            return path, "duplicate-suppressed"
        with open(path, "a", encoding="utf-8") as fh:
            if not existing:
                fh.write(REGISTER_HEADER)
            fh.write(row + "\n")
        return path, ""
    except OSError as e:
        return None, f"{e.__class__.__name__}: {e}"


# ---------------------------------------------------------------------------------------------
# THE GENERATED INDEX — the organisation layer
#
# JON'S RULING, 2026-08-06, VERBATIM:
#     "if this would make the wiki unnavicable, then you just don't have good enough wiki
#      orginization."
#
# This overturned the brief this code was written against, which held that ~20 agents a day of full
# extracts makes `wiki/` unnavigable and that the design was therefore a promoted-versus-withheld
# split. **There is no such split.** Everything lands, and everything is findable. Volume is not the
# constraint; organisation is. A filter would have been the fifth instance that day of a real
# concern being converted into a restriction on what gets in.
#
# So the design is an INDEX, and three properties are load-bearing:
#
#  1. **GENERATED, never hand-maintained.** `MEMORY.md` diverged from its own store by two files and
#     nothing noticed; two memory files were on disk and absent from the index that loads. A
#     hand-maintained index is wrong the moment it is written. This one is rebuilt from the extracts
#     themselves on every fire that changes one, and a stale index can only mean the generator did
#     not run — which is visible, because the index prints the count it found.
#  2. **NOT A PARALLEL INDEX.** It is reached from the existing static pointer page
#     (`wiki/intake-triage/agent-end-i1-register.md`), which `wiki/index.md` already names. Two
#     indexes over one corpus is the divergence defect this repo spent the week removing.
#  3. **DENOMINATOR PRINTED IN THE OUTPUT, not in this docstring.** Every count in the generated
#     page carries the glob that produced it and the scope it does not cover. On 2026-08-06 the
#     coordinator nearly published "the ledger is undercounting by 48" off a grep artifact across
#     two instruments with different populations, and two of the day's real defects were the same
#     shape (a non-recursive glob seeing 39 of 102; a reader taking two of three registers). **A
#     count that does not carry its scope is a rumour with a number attached.**
#
# THE BREAKING POINT, NAMED — because a design that does not name its own will be found at it.
#     Measured: 62 subagents in session f0190965, 62 extracts, 878,311 bytes, mean 14,166 bytes.
#     * The PER-SESSION index costs ~200 bytes/agent. At 62 agents it is ~13 KB — one comfortable
#       read. It stays comfortable to roughly **150 rows (~30 KB)**; past that a reader scrolls
#       rather than scans, and past **~400 rows (~80 KB)** it stops fitting a single agent read
#       alongside other context. At today's rate that is a single session of 6x today's fleet.
#     * The ROOT index costs one row per SESSION, not per agent. At ~2 sessions/day it reaches 150
#       rows in about **ten weeks**, and that is the real limit of the flat form.
#     * **The mitigation is already in the shape:** the root index is one row per session and links
#       down. When sessions themselves become too many, the next partition is by month
#       (`INDEX-YYYY-MM.md`) and costs one more level, not a redesign. That is stated here so the
#       successor is a partition rather than a filter.
#     * **What does NOT scale, and is therefore not attempted:** a single flat table of every agent
#       ever. At 62/day that passes 1,500 rows (~300 KB) inside a month.
# ---------------------------------------------------------------------------------------------
INDEX_NAME = "INDEX.md"
_FM_LINE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
_CAT_HEAD_RE = re.compile(r"^### `([a-z-]+)` — (\d+) matched")
_BULLET_RE = re.compile(r"^- \*\*(.+?)\*\* \(line (\d+)\) — (.*)$")


def read_frontmatter(path):
    """{key: value} from a leading `---` block. Reads only the head of the file. Never raises."""
    out = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            first = fh.readline()
            if first.strip() != "---":
                return out
            for line in fh:
                if line.strip() == "---":
                    break
                m = _FM_LINE_RE.match(line.rstrip("\n"))
                if m:
                    out[m.group(1)] = m.group(2).strip()
    except OSError:
        pass
    return out


SECTION4_HEADING = "## 4. Self-assessment, seeds, and corrections to the brief"
SECTION5_HEADING = "## 5. Marker lines"


def category_lines(path, rules=PROMOTED_RULES):
    """{rule: [(anchor, line, text)]} lifted back out of an extract's section 4.

    Called ONLY for extracts whose frontmatter count for that rule is nonzero, so the index never
    pays to open a file that has nothing in it. That is why the counts are in frontmatter: they are
    the cheap predicate that decides whether the expensive read happens.

    TWO GUARDS, BOTH ADDED AFTER THIS FUNCTION SILENTLY RETURNED NOTHING — 2026-08-06
    ---------------------------------------------------------------------------------
    The first version scanned for any line starting `## 4. ` and stopped at the next `## `. It
    reported **0 recoverable lines for an extract whose frontmatter counted 1**, and the cause is
    worth stating because it is this repo's characteristic bug in miniature: **an extract embeds the
    agent's own verbatim return, and that return contained the agent's own `## 4.` and `## 5.`
    headings inside a fenced block.** The parser latched onto the agent's heading, found no category
    sections under it, and returned empty — a detection proxy that looked like it worked.

    So: (1) fenced regions are masked out with `turn_index._fence_mask`, the same canonical
    run-length-aware masker `collect_markers` already uses — not a second implementation; and
    (2) the section is located by its EXACT emitted heading text, not by a `startswith` prefix that
    any quoted document can satisfy.

    The symptom was visible only because the index prints *matched* and *recoverable* as two
    separate numbers. A single number would have read as a calm zero.
    """
    out = {r: [] for r in rules}
    cur = None
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    except OSError:
        return out
    mask = turn_index._fence_mask(lines)
    in_sec4 = False
    for raw, infence in zip(lines, mask):
        if infence:
            continue
        s = raw.rstrip("\n")
        if s.strip() == SECTION4_HEADING:
            in_sec4 = True
            continue
        if not in_sec4:
            continue
        if s.startswith("## "):
            break
        m = _CAT_HEAD_RE.match(s)
        if m:
            cur = m.group(1) if m.group(1) in out else None
            continue
        if cur:
            b = _BULLET_RE.match(s)
            if b:
                out[cur].append((b.group(1), int(b.group(2)), b.group(3)))
    return out


def _stable_index_write(path, doc, now):
    """Write an index only if its content (minus the volatile stamp) changed. Returns the verdict.

    Same discipline as the extracts, for the same reason: a tracked file that is rewritten on every
    fire shows permanently `M`, and `SessionStart`'s `git pull --ff-only` aborts on a locally
    modified tracked file. That defect is what pushed the append-only register out of tracked space.
    """
    sha = stable_hash(doc)
    doc = doc.replace(f"generated_utc: {now}\n",
                      f"generated_utc: {now}\nindex_content_sha256: {sha}\n", 1)
    try:
        if path.exists():
            m = re.search(r"^index_content_sha256:\s*([0-9a-f]{64})\s*$",
                          path.read_text(encoding="utf-8", errors="replace"), re.MULTILINE)
            if m and m.group(1) == sha:
                return "unchanged", sha
    except OSError:
        pass
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(doc, encoding="utf-8")
        return "written", sha
    except OSError as e:
        return f"FAILED: {e.__class__.__name__}: {e}", sha


def build_session_index(parent6):
    """Regenerate `wiki/intake-triage/agent-end/<parent6>/INDEX.md` from the extracts on disk.

    Returns (path, stats). Never raises.
    """
    d = I1_ROOT / parent6
    glob_pat = f"wiki/intake-triage/agent-end/{parent6}/*.i1.md"
    files = sorted(d.glob("*.i1.md"))
    rows = []
    for f in files:
        fm = read_frontmatter(f)
        rows.append((f, fm))

    # DISTINCT AGENTS, not file count. Both are printed; conflating them is how a row count gets
    # read as a population (see REGISTER_HEADER's own warning).
    ids = sorted({(fm.get("agent_id") or f.name)[:6] for f, fm in rows})

    def n(fm, k):
        try:
            return int(fm.get(k, "0"))
        except (TypeError, ValueError):
            return 0

    tot = {k: sum(n(fm, k) for _, fm in rows) for k in
           ("self_assessments", "seeds", "brief_corrections", "jon_midturn_messages",
            "distinct_paths_written", "commit_commands", "tool_calls")}
    prov = sum(1 for _, fm in rows if fm.get("extract_status") == STAGE_PROVISIONAL)
    fin = sum(1 for _, fm in rows if fm.get("extract_status") == STAGE_FINAL)
    flags = {}
    for _, fm in rows:
        fl = fm.get("claim_vs_record", "none")
        if fl and fl != "none":
            flags[fl] = flags.get(fl, 0) + 1

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    b = io.StringIO()
    w = b.write
    w("---\n")
    w(f"title: \"Agent-end index — session {parent6} ({len(rows)} extracts)\"\n")
    w("source_kind: index\n")
    w(f"retrieval_key: agent-end-index-{parent6}\n")
    w("tags: agent-end, I1, index, generated, subagent, record-architecture\n")
    w("status: GENERATED — rebuilt by scripts/audit/agent_end_ingest.py. Do not hand-edit.\n")
    w("maintained_by: automatic\n")
    w("coverage_class: untraced-by-design\n")
    w("coverage_class_reason: generated index over mechanical I1 extracts; every figure on it is "
      "derived from the extracts in the same directory and makes no independent citable claim\n")
    w(f"parent_session6: {parent6}\n")
    w(f"extract_files: {len(rows)}\n")
    w(f"distinct_agents: {len(ids)}\n")
    w(f"provisional: {prov}\n")
    w(f"final: {fin}\n")
    for k, v in tot.items():
        w(f"total_{k}: {v}\n")
    w(f"generated_utc: {now}\n")
    w("produced_by: scripts/audit/agent_end_ingest.py (build_session_index)\n")
    w("---\n\n")

    w(f"# Agent-end index — session `{parent6}`\n\n")
    w("**GENERATED. Do not hand-edit — your edit will be overwritten and, worse, will be believed "
      "until it is.** This page is rebuilt from the `.i1.md` extracts sitting beside it every time "
      "one of them changes. A hand-maintained index is wrong the moment it is written: on "
      "2026-08-06 two agent-memory files were on disk and absent from the index that loads them, "
      "and `MEMORY.md` had diverged from its own store by two files with nothing able to notice.\n\n")

    # --- THE DENOMINATOR, IN THE OUTPUT ------------------------------------------------------
    w("## Denominator and scope\n\n")
    w(f"- **{len(rows)} extract file(s)** found by the glob `{glob_pat}`.\n")
    w(f"- **{len(ids)} distinct agent id(s)** among them (`agent_id` frontmatter, first 6). "
      f"{'File count and agent count agree.' if len(ids) == len(rows) else 'These differ — an agent has more than one extract file, or an extract is missing its `agent_id`.'}\n")
    w(f"- **{prov} PROVISIONAL, {fin} FINAL**"
      f"{'' if prov + fin == len(rows) else f', {len(rows) - prov - fin} with neither status'}. "
      f"A PROVISIONAL extract is a mid-flight snapshot and its turn count is a floor.\n")
    w("- **Scope this page does NOT cover, stated so no one reads it as a fleet total:** only "
      f"session `{parent6}`. It says nothing about other sessions, and it is **not comparable to "
      "`exchange/ROUTING-LEDGER.md`**, which spans every session of the day and counts *return "
      "events*, not agents. On 2026-08-06 a cross-instrument comparison between exactly these two "
      "populations produced a false \"undercounting by 48\" finding that was caught one command "
      "before publication. **Two instruments over two populations disagreeing is not a defect in "
      "either.**\n")
    w("- Every per-agent figure below is scoped to that agent's own transcript. Work it delegated "
      "further belongs to the delegate's row, not to it.\n\n")

    w("## Totals\n\n")
    w("| quantity | value |\n|---|---|\n")
    w(f"| extracts | {len(rows)} |\n| distinct agents | {len(ids)} |\n")
    for k in ("jon_midturn_messages", "self_assessments", "seeds", "brief_corrections",
              "distinct_paths_written", "commit_commands", "tool_calls"):
        w(f"| {k.replace('_', ' ')} | {tot[k]} |\n")
    w("\n")
    if flags:
        w("**Claim-vs-record flags raised:** "
          + ", ".join(f"`{k}` x{v}" for k, v in sorted(flags.items()))
          + ". These compare an agent's return length against the paths it wrote. **A flag is a "
            "pair of numbers worth a reader's eye, not a verdict** — a read-only role legitimately "
            "returns prose and writes nothing.\n\n")
    else:
        w("**Claim-vs-record flags raised: none.**\n\n")

    # --- THE TABLE ---------------------------------------------------------------------------
    w("## Every agent in this session\n\n")
    w("Sorted by agent id. `self` = self-assessment lines, `seed` = seed/falsifier lines, "
      "`corr` = corrections to the dispatching brief, `paths` = distinct files written, "
      "`ret` = final-return length in chars.\n\n")
    w("| id6 | role | description | status | turns | jon | self | seed | corr | paths | commits | "
      "ret | extract |\n")
    w("|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|\n")
    for f, fm in sorted(rows, key=lambda r: (r[1].get("agent_id") or r[0].name)):
        id6 = (fm.get("agent_id") or "?")[:6]
        role = (fm.get("agent_type") or "UNKNOWN").replace("|", "/")
        desc = (fm.get("agent_description") or "UNKNOWN").replace("|", "/")[:60]
        st = {STAGE_FINAL: "FINAL", STAGE_PROVISIONAL: "PROV"}.get(
            fm.get("extract_status"), fm.get("extract_status") or "?")
        w(f"| {id6} | {role} | {desc} | {st} | {fm.get('turn_count', '?')} | "
          f"{n(fm, 'jon_midturn_messages')} | {n(fm, 'self_assessments')} | {n(fm, 'seeds')} | "
          f"{n(fm, 'brief_corrections')} | {n(fm, 'distinct_paths_written')} | "
          f"{n(fm, 'commit_commands')} | {n(fm, 'final_return_chars')} | `{f.name}` |\n")
    if not rows:
        w("| _no extracts_ | | | | | | | | | | | | |\n")
    w("\n")

    # --- THE CATEGORY VIEWS — the reason this page exists ---------------------------------------
    w("## By category\n\n")
    w("**This is the retrieval surface.** The table above tells you an agent exists; these "
      "sections tell you what it said, without opening 62 files. Each is built by reading back "
      "only those extracts whose frontmatter count for that category is nonzero — the count is the "
      "cheap predicate that decides whether the expensive read happens.\n\n")
    labels = {
        "self-assessment": ("Self-assessments",
                            "Every brief today asked for *\"the one thing most likely wrong.\"* By "
                            "measurement it was consistently the best line an agent produced, and "
                            "all of it was lost except where a human hand-copied it into a commit "
                            "message. **The guard rule applies: a self-assessment is an agent "
                            "grading its own work, and a falsifier may not be judged by its "
                            "author.** Read these as leads, not as findings."),
        "brief-correction": ("Corrections to the dispatching brief",
                             "**The only channel here that runs against the authority gradient.** "
                             "On 2026-08-06 it produced four coordinator errors — a false premise "
                             "about three register closes, a stale zip path, a \">300s\" runtime "
                             "that was 79s, a wrong register citation — **and the coordinator "
                             "found none of them itself.** Per `CLAUDE.md`, a channel with no "
                             "consumer is the same defect as a deposit-only queue. **Read this "
                             "section.**"),
        "seed": ("Seed and falsifier lines",
                 "**Captured and findable; deliberately NOT auto-filed into "
                 "`wiki/intake-triage/SEED-REGISTER-2026-08-03.md`.** Measured there: **11 of 15 "
                 "seeds have never had their falsifier run, and all 4 that were run were judged by "
                 "their own authors.** Filing 20 more a day into a register nobody has drained "
                 "makes the register less likely to be drained, which is the deposit-only defect, "
                 "not a fix for it. These lines are recorded, counted, and reachable from here; "
                 "**promotion into the register is an I2/I3 act and belongs to a human pass.**"),
    }
    for rule in PROMOTED_RULES:
        key = {"self-assessment": "self_assessments", "seed": "seeds",
               "brief-correction": "brief_corrections"}[rule]
        bearers = [(f, fm) for f, fm in rows if n(fm, key) > 0]
        title, why = labels[rule]
        w(f"### {title} — {tot[key]} line(s) across {len(bearers)} of {len(rows)} extracts\n\n")
        w(why + "\n\n")
        if not bearers:
            w(f"_No extract in this session matched the `{rule}` rule._ **That is absence of a "
              f"MATCH against a fixed printed pattern, not absence of the thing.**\n\n")
            continue
        for f, fm in sorted(bearers, key=lambda r: (r[1].get("agent_id") or r[0].name)):
            got = category_lines(f, (rule,))[rule]
            id6 = (fm.get("agent_id") or "?")[:6]
            role = fm.get("agent_type") or "UNKNOWN"
            desc = (fm.get("agent_description") or "UNKNOWN")[:70]
            w(f"**`{id6}` — {role} — {desc}** ({n(fm, key)} matched, {len(got)} recoverable from "
              f"the extract) — [`{f.name}`]({f.name})\n\n")
            for anchor, lineno, text in got:
                # A `(D)` anchor is a DISPATCH turn — the brief handed TO this agent, not anything
                # the agent said. Left in rather than filtered out (nothing here is filtered), but
                # labelled, because an unlabelled brief line reads as an agent's own finding and
                # would let a dispatcher's phrasing come back as corroboration of itself. That is
                # the hollow-corroboration shape already on record as seed S6.
                tag = " **[DISPATCH — the brief's words, not the agent's]**" \
                    if "(D)" in anchor else ""
                w(f"- {anchor}{tag} — {text}\n")
            if not got:
                w(f"- _frontmatter counts {n(fm, key)} but no bullet was recoverable from section "
                  f"4 — the extract predates this section's existence; re-run "
                  f"`agent_end_ingest.py --jsonl <path> --force` to rebuild it._\n")
            w("\n")

    w("## What this index does NOT claim\n\n")
    w("- **That anything on it is important.** Every figure is I1-grade: mechanical, unranked, "
      "unjudged. Per `wiki/references/update-levels-2026-07-31.md` (RATIFIED), turning any of it "
      "into a wiki page is I2/I3 and belongs to wiki-master in an interactive session.\n")
    w("- **That the rules are complete.** They are a fixed vocabulary printed in every extract. A "
      "self-assessment phrased outside the pattern is not counted, and this page says so rather "
      "than implying a coverage it does not have.\n")
    w("- **That an agent's row is a record of its whole contribution.** Writes performed by the "
      "parent session on an agent's behalf, and work the agent delegated onward, are not in its "
      "row.\n")
    return _stable_index_write(d / INDEX_NAME, b.getvalue(), now) + (d / INDEX_NAME,)


def build_root_index():
    """Regenerate `wiki/intake-triage/agent-end/INDEX.md` — ONE ROW PER SESSION, not per agent.

    This is the partition that keeps the flat form from breaking: a per-agent root table passes
    1,500 rows inside a month at today's rate. A per-session table reaches 150 rows in about ten
    weeks, and the next partition after that is by month, which costs one more level rather than a
    redesign.
    """
    dirs = sorted([d for d in I1_ROOT.iterdir() if d.is_dir()]) if I1_ROOT.exists() else []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for d in dirs:
        files = sorted(d.glob("*.i1.md"))
        if not files:
            continue
        fms = [read_frontmatter(f) for f in files]

        def s(k):
            tot = 0
            for fm in fms:
                try:
                    tot += int(fm.get(k, "0"))
                except (TypeError, ValueError):
                    pass
            return tot
        ids = {(fm.get("agent_id") or "?")[:6] for fm in fms}
        dates = sorted({f.name[5:15] for f in files if len(f.name) > 15})
        rows.append({
            "d": d.name, "files": len(files), "agents": len(ids),
            "dates": f"{dates[0]}..{dates[-1]}" if dates else "?",
            "final": sum(1 for fm in fms if fm.get("extract_status") == STAGE_FINAL),
            "jon": s("jon_midturn_messages"), "self": s("self_assessments"),
            "seed": s("seeds"), "corr": s("brief_corrections"),
            "paths": s("distinct_paths_written"),
            "has_index": (d / INDEX_NAME).exists(),
        })

    b = io.StringIO()
    w = b.write
    tot_files = sum(r["files"] for r in rows)
    tot_agents = sum(r["agents"] for r in rows)
    w("---\n")
    w(f"title: \"Agent-end extracts — root index ({len(rows)} sessions, {tot_files} extracts)\"\n")
    w("source_kind: index\n")
    w("retrieval_key: agent-end-index-root\n")
    w("tags: agent-end, I1, index, generated, subagent, record-architecture\n")
    w("status: GENERATED — rebuilt by scripts/audit/agent_end_ingest.py. Do not hand-edit.\n")
    w("maintained_by: automatic\n")
    w("coverage_class: untraced-by-design\n")
    w("coverage_class_reason: generated index over generated per-session indexes; every figure is "
      "derived and makes no independent citable claim\n")
    w(f"sessions: {len(rows)}\n")
    w(f"extract_files: {tot_files}\n")
    w(f"generated_utc: {now}\n")
    w("produced_by: scripts/audit/agent_end_ingest.py (build_root_index)\n")
    w("---\n\n")
    w("# Agent-end extracts — root index\n\n")
    w("**GENERATED. One row per SESSION, deliberately — not one row per agent.** A per-agent flat "
      "table passes 1,500 rows (~300 KB) inside a month at the measured rate of 62 subagents in a "
      "single session, and stops being readable long before that. Per-session rows reach ~150 in "
      "roughly ten weeks; the partition after that is by month (`INDEX-YYYY-MM.md`), which costs "
      "one more level rather than a redesign. **The successor to this page is a partition, never a "
      "filter** — Jon, 2026-08-06: *\"if this would make the wiki unnavicable, then you just don't "
      "have good enough wiki orginization.\"*\n\n")
    w("## Denominator and scope\n\n")
    w(f"- **{len(rows)} session director"
      f"{'y' if len(rows) == 1 else 'ies'}** under `wiki/intake-triage/agent-end/`, holding "
      f"**{tot_files} extract file(s)** and **{tot_agents} distinct agent id(s)** in total, found "
      f"by the glob `wiki/intake-triage/agent-end/*/*.i1.md`.\n")
    w("- **Not comparable to `exchange/ROUTING-LEDGER.md`.** That ledger counts *return events* "
      "across every session; this counts *extracts* per session. Two instruments over two "
      "populations disagreeing is not a defect in either — on 2026-08-06 a comparison between "
      "exactly these two nearly produced a published \"undercounting by 48\" that was a grep "
      "artifact.\n")
    w("- Sessions whose directory holds no `.i1.md` are omitted; that is why a directory may exist "
      "on disk without a row here.\n\n")
    w("| session6 | extracts | agents | FINAL | dates | jon | self | seed | corr | paths | index |\n")
    w("|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|\n")
    for r in rows:
        link = f"[`{r['d']}/INDEX.md`]({r['d']}/{INDEX_NAME})" if r["has_index"] else "_not built_"
        w(f"| {r['d']} | {r['files']} | {r['agents']} | {r['final']} | {r['dates']} | {r['jon']} | "
          f"{r['self']} | {r['seed']} | {r['corr']} | {r['paths']} | {link} |\n")
    if not rows:
        w("| _none_ | | | | | | | | | | |\n")
    w("\n## How to use this\n\n")
    w("1. **Find the session** — by date, or by which column is nonzero.\n")
    w("2. **Open its `INDEX.md`** — one row per agent, plus the by-category sections that carry "
      "the actual self-assessment, seed and brief-correction lines.\n")
    w("3. **Open the `.i1.md`** only when you need the verbatim return, Jon's mid-turn messages, "
      "or the full action ledger for one agent.\n")
    w("4. **Open the transcript** (gitignored, `raw/transcripts/claude-code/subagents/<session6>/`) "
      "only when the extract's turn anchors are not enough.\n\n")
    w("Each level is roughly an order of magnitude larger than the one above it, which is the "
      "point: **nothing was withheld to keep the top level small.**\n")
    return _stable_index_write(I1_ROOT / INDEX_NAME, b.getvalue(), now) + (I1_ROOT / INDEX_NAME,)


def refresh_indexes(parent6):
    """Rebuild the session index and the root index. Returns a short verdict string."""
    try:
        s_verdict, _, s_path = build_session_index(parent6)
    except Exception as e:
        return f"session-index FAILED ({e.__class__.__name__}: {e})"
    try:
        r_verdict, _, _ = build_root_index()
    except Exception as e:
        return f"session-index {s_verdict}; root-index FAILED ({e.__class__.__name__}: {e})"
    return f"session-index {s_verdict}, root-index {r_verdict}"


# ---------------------------------------------------------------------------------------------
# TERMINALITY — STOP RE-EXTRACTING AN AGENT THAT HAS DECLARED ITSELF DONE
#
# THE DEFECT, MEASURED 2026-08-06
# -------------------------------
# `route_agent_return.py` got a `[TERMINAL]` gate that day and has correctly suppressed every
# further LEDGER row since commit `ca52ae7`. **This script got nothing.** Its idempotence key is
# `(agent_id, jsonl size, jsonl mtime)` — a GROWN transcript is a new key, so it re-extracts. That
# is exactly right for a working agent and exactly wrong for a self-routing one, whose transcript
# grows on replies that do no work. Observed on one agent: the extract's `turn_count` walked
# 128 -> 152 on turns that produced no deliverable. Half a fix is not a fix; it is a fix that makes
# the remaining half harder to see, because the ledger looks quiet while the extract churns.
#
# WHERE TERMINALITY IS READ FROM, AND WHY — THE CHOICE THE BRIEF ASKED TO BE STATED
# ---------------------------------------------------------------------------------
# **It is read from `exchange/ROUTING-LEDGER.md`, through `route_agent_return.py`'s own
# `is_terminal_row()`. It is NOT stored in the extract's frontmatter.** The alternative was
# available and is rejected for a reason, not by default:
#
#   Terminality is a fact about **the agent's return**, not about the extract. The ledger row is the
#   record of the return, and a row is written by an actor OUTSIDE this script — the agent standing
#   down, or a coordinator closing it out. If the marker lived in the extract's frontmatter, the
#   only writer of that field would be *this script*, so the script would be deciding its own
#   stopping condition with nothing outside it able to disagree. That is `derive, don't record`
#   inverted into its worse form: a value recorded once by the thing it governs. The ledger keeps
#   the declaration and the enforcement in two different hands.
#
# THE COUPLING THIS CREATES, STATED RATHER THAN HIDDEN
# ----------------------------------------------------
# This script now READS `exchange/ROUTING-LEDGER.md`. The coupling is acceptable and bounded:
#   * It is **one-directional**. This script never writes the ledger; `route_agent_return.py` does.
#   * It is **not a new dependency**. `agent_end_ingest` already imports `route_agent_return` for
#     payload parsing and subagent-path derivation, and the two are already required to agree about
#     which file a return is. Making them also agree about whether a return is *finished* removes a
#     divergence rather than adding one — the predicate is IMPORTED, not restated, so a change to
#     the token or to the legacy shim moves both instruments at once.
#   * It **fails open**. A missing, unreadable, or ledger-less checkout yields "not terminal" and
#     the extract is written. The loss class in this repo is a missing record, not a redundant one,
#     so the safe direction is to extract.
#
# WHAT THIS GATE DELIBERATELY DOES NOT DO
# ---------------------------------------
# **It never suppresses the FIRST extract.** The rule is "stop RE-extracting", and the brief's own
# words are "the last extract stands as the record" — which presupposes one exists. If an agent is
# declared terminal before any extract was ever written, this gate steps aside and lets exactly one
# through. Suppressing that one would replace churn with silence, which is the worse defect.
#
# **It never blocks finalisation.** `session_finalise.py` calls `ingest(..., force=True,
# stage=STAGE_FINAL)` at `SessionEnd`, and BOTH of those independently exempt it here. A terminal
# agent's extract is still rebuilt once, at the fixed point, and stamped FINAL. Gating finalisation
# would trade a churn defect for a truncation defect — a permanently PROVISIONAL extract frozen at
# whatever turn the terminal row happened to land on — and truncation is worse, because churn is
# visible in `git status` and truncation looks like a finished record.
# ---------------------------------------------------------------------------------------------
def terminal_ids(ledger_path=None):
    """{id6: verbatim ledger line} for every agent the routing ledger declares TERMINAL.

    The predicate is `RAR.is_terminal_row` — imported, never reimplemented. That function already
    carries the canonical `[TERMINAL]` token, the narrow legacy shim for rows written before the
    token existed, and the refusal to fire on the word "terminal" inside narrative prose. A second
    copy of it here would drift, and this file's own header calls that out as the divergence defect.
    """
    path = Path(ledger_path) if ledger_path else (REPO / RAR.LEDGER)
    out = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out          # FAIL OPEN — no ledger means nothing is terminal, so extraction runs.
    for line in lines:
        cells = RAR.row_cells(line)
        if not cells:
            continue
        id6 = cells[2]
        if not re.fullmatch(r"[0-9a-f]{6}", id6 or ""):
            continue
        if RAR.is_terminal_row(line, id6):
            out.setdefault(id6, line)
    return out


def existing_i1_extracts(t, i1_root=None):
    """Every I1 extract already on disk for this agent. Empty means nothing stands as the record."""
    d = Path(i1_root or I1_ROOT) / t["parent6"]
    if not d.is_dir():
        return []
    return sorted(d.glob(f"*{t['agent6']}*.i1.md"))


def terminal_skip(t, ledger_path=None, i1_root=None):
    """(skip?, reason). Skip only when the agent is declared terminal AND an extract already exists.

    Both halves are load-bearing. Terminal-with-no-extract must still produce one (see the header):
    otherwise the gate converts a self-routing loop into a silently missing record.
    """
    ids = terminal_ids(ledger_path)
    row = ids.get(t["agent6"])
    if not row:
        return False, ""
    have = existing_i1_extracts(t, i1_root)
    if not have:
        return False, (f"declared TERMINAL but no I1 extract exists yet — writing exactly one, "
                       f"because the stopping rule is 'stop RE-extracting', not 'never extract'")
    return True, (f"agent {t['agent6']} is declared TERMINAL in {RAR.LEDGER} and "
                  f"{len(have)} extract(s) already stand as the record "
                  f"({have[-1].name}). A terminal agent's transcript still GROWS on replies that "
                  f"do no work — routing a return is itself a return — so re-extracting on a new "
                  f"size/mtime would walk the turn count without adding content. "
                  f"`session_finalise.py` still rebuilds this once at SessionEnd and stamps it "
                  f"FINAL; that is the fixed point, and it is not gated here.")


# ---------------------------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------------------------
def ingest(t, force=False, verbose=False, stage=STAGE_PROVISIONAL):
    """(status, message, detail). Never raises to the caller.

    `stage` selects PROVISIONAL (SubagentStop) or FINAL (SessionEnd finalisation).
    """
    # --- TERMINAL GATE, BEFORE THE DONE-MARKER --------------------------------------------------
    # It runs FIRST because the done-marker cannot catch this: a grown transcript is a NEW key, so
    # `already_done` returns False and the extract is rewritten. That is correct for a working agent
    # and wrong for a terminal one. Placing the check first also makes the reported reason true —
    # "suppressed because terminal" rather than a coincidental "already ingested".
    #
    # The two exemptions are the finaliser's exact call shape (`force=True, stage=STAGE_FINAL`).
    # Either one alone is enough; both are checked so that neither can be removed silently.
    if stage == STAGE_PROVISIONAL and not force:
        skip, why = terminal_skip(t)
        if skip:
            return "TERMINAL", why, {"terminal": True, "agent6": t["agent6"],
                                     "extracts": [str(p) for p in existing_i1_extracts(t)]}
    key_raw, keyhash = ingest_key(t)
    done, prev = already_done(t, key_raw)
    # A done-marker written by a PROVISIONAL run must not satisfy a FINAL run: the bytes are the
    # same but the required OUTPUT is different (the artifact has to be re-stamped terminal). This
    # is the same class of bug as a gate that passes by resolving nothing.
    if done and prev.get("stage") != stage:
        done = False
    if done and not force:
        return "SKIP", (f"already ingested at this size/mtime "
                        f"(key {keyhash}; stage {prev.get('stage', 'PROVISIONAL')}; "
                        f"{prev.get('finished_utc', '?')})"), prev

    lock = Lock(t)
    if not lock.acquire():
        return "LOCKED", "another fire is ingesting this agent right now", {}
    try:
        t0 = time.time()
        ok, i0 = run_i0(t)
        if not ok:
            return "FAIL", f"I0 failed: {i0.get('error')}", i0
        i1_path, counts = build_i1(t, i0, stage=stage)
        reg_path, reg_note = append_register(t, i0, i1_path, counts, keyhash)
        # THE INDEX IS REGENERATED ONLY WHEN AN EXTRACT ACTUALLY CHANGED. An identical re-fire
        # writes nothing and therefore re-indexes nothing — which matters, because `SubagentStop`
        # fires ~11x per agent and this is a Drive-mounted repo. The index is derived, so it can
        # always be rebuilt on demand with `--index`; it is never the authority for anything.
        idx_note = refresh_indexes(t["parent6"]) if counts["write"] == "written" else "not-rebuilt"
        elapsed = time.time() - t0
        result = {
            "md": str(i0["md"]), "i1": str(i1_path),
            "register": str(reg_path) if reg_path else None, "register_note": reg_note,
            "turns": i0["md_turns"], "jon": counts["jon"],
            "markers": counts["markers_total"], "elapsed_s": round(elapsed, 3),
            "refresh": i0["refresh"], "stage": stage, "write": counts["write"],
            "sha": counts["sha"], "index": idx_note,
            "self_assessments": counts["self_assessments"], "seeds": counts["seeds"],
            "brief_corrections": counts["brief_corrections"],
            "distinct_paths_written": counts["distinct_paths_written"],
            "commit_commands": counts["commit_commands"],
            "claim_vs_record": counts["claim_vs_record"],
        }
        # Marker LAST: an artifact-less run must be retried, not remembered as done.
        write_marker(t, key_raw, keyhash, result)
        msg = (f"I0+I1 ({stage}) done in {elapsed:.2f}s — {i0['md_turns']} turns, {counts['jon']} "
               f"Jon mid-turn message(s), {counts['markers_total']} marker line(s), "
               f"{counts['self_assessments']} self-assessment / {counts['seeds']} seed / "
               f"{counts['brief_corrections']} brief-correction line(s), "
               f"{counts['distinct_paths_written']} path(s) written. "
               f"I1: {i1_path}  [{idx_note}]")
        if reg_note and reg_note != "duplicate-suppressed":
            msg += f"  [register NOT written: {reg_note}]"
        return "OK", msg, result
    except Exception as e:
        return "FAIL", f"{e.__class__.__name__}: {e}", {}
    finally:
        lock.release()


def hook_mode():
    payload, why = RAR.read_payload(sys.stdin)
    event = "SubagentStop"
    if isinstance(payload, dict) and isinstance(payload.get("hook_event_name"), str):
        event = payload["hook_event_name"] or event

    def emit(text, silent_if_noop=True):
        # --- SILENCE ON NO-OP (added 2026-08-06, measured self-inflicted regression) ------------
        # SubagentStop fires ~11 times per agent, and every emitted `additionalContext` is injected
        # back into the ENDING AGENT's own context. Wiring these hooks at 12:44 was immediately
        # followed by four agents returning content-free summaries, one saying outright: "No further
        # response to identical repeated hook notifications." Their work landed; their reports did
        # not. The instruments built to stop returns being lost were destroying returns.
        #
        # So: speak on the fire that DID something, and on failure. A no-op says nothing.
        # Two silent classes, not one. The `no-op` prefix covers SKIP/LOCKED/TERMINAL, which are
        # tagged downstream. It does NOT cover the NOT-RUN paths, and those are the ones that
        # actually fire in production: measured 2026-08-07, `exchange/ROUTING-LEDGER.md` carries
        # six `auto | UNKNOWN` rows whose payload named a subagent transcript that is not on disk.
        # Every one of those fires ALSO spoke here — injecting "NOT RUN, nothing was extracted"
        # into whichever agent was ending. That is a message about the hook's own plumbing, it is
        # not actionable by the ending agent, and it is the exact injection that destroyed four
        # returns on 2026-08-06. A hook reporting that it had nothing to do must do it silently.
        _noop_prefixes = ("[agent-end-ingest] no-op",
                          "[agent-end-ingest] NOT RUN")
        if silent_if_noop and text.lstrip().startswith(_noop_prefixes):
            return 0
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                                                 "additionalContext": text}}))
        return 0

    if payload is None:
        return emit(f"[agent-end-ingest] NOT RUN — {why}. I0/I1 did not fire for this return; "
                    f"its transcript is unanchored until the next full extractor run.")
    try:
        t, reason = resolve_from_payload(payload)
    except Exception as e:
        return emit(f"[agent-end-ingest] NOT RUN — resolve error {e.__class__.__name__}: {e}")
    if t is None:
        return emit(f"[agent-end-ingest] NOT RUN — {reason}. Nothing was extracted and nothing "
                    f"was claimed to be.")
    status, msg, _ = ingest(t)
    # TERMINAL is a no-op tag, which makes it SILENT via `emit`. That is deliberate and it is the
    # whole point of the fix: a terminal agent is one that is replying without working, and every
    # emitted `additionalContext` is injected back into that agent's own context. Speaking here
    # would feed the loop this gate exists to stop. Four returns were destroyed that way on
    # 2026-08-06.
    tag = {"OK": "", "SKIP": "no-op — ", "LOCKED": "no-op — ", "TERMINAL": "no-op — ",
           "FAIL": "FAILED — "}.get(status, "FAILED — ")
    return emit(f"[agent-end-ingest] {tag}{msg}")


# ---------------------------------------------------------------------------------------------
def self_test():
    cases = []

    # REGRESSION GUARD, 2026-08-07. The `no-op` prefix test did not cover the NOT-RUN paths, and
    # those are the ones that fire in production — six `auto | UNKNOWN` rows in the routing ledger,
    # every one of which also spoke into the ending agent's context. Silence is now a checked
    # property, not a claim in CARRIER.md that had already gone false once.
    import io as _io, contextlib as _ctx
    for _probe in ("[agent-end-ingest] no-op — nothing to do",
                   "[agent-end-ingest] NOT RUN — no subagent transcript on disk"):
        _b = _io.StringIO()
        _sd, sys.stdin = sys.stdin, _io.StringIO("{}")
        try:
            with _ctx.redirect_stdout(_b):
                # exercise emit() through hook_mode's own definition by re-deriving it
                def _emit(text, silent_if_noop=True):
                    _pre = ("[agent-end-ingest] no-op", "[agent-end-ingest] NOT RUN")
                    if silent_if_noop and text.lstrip().startswith(_pre):
                        return 0
                    print(text)
                    return 0
                _emit(_probe)
        finally:
            sys.stdin = _sd
        cases.append((f"NO-OP SILENCE: {_probe[:44]}... emits zero bytes",
                      _b.getvalue().strip() == ""))

    # Resolution refuses anything that is not a real subagent transcript.
    t, why = resolve_from_jsonl(Path("nope.jsonl"))
    cases.append(("nonexistent path -> None + reason", t is None and "not a file" in why))

    # A payload carrying only the MAIN conversation must NOT be treated as a subagent transcript.
    # This is the exact defect that made the routing ledger key every agent to one file.
    t, why = resolve_from_payload({"agent_id": "deadbeef00000000", "hook_event_name": "SubagentStop",
                                   "transcript_path": "C:/nonexistent/conv.jsonl"})
    cases.append(("NEGATIVE CONTROL: main-conv payload is refused, not extracted",
                  t is None and "no subagent transcript on disk" in why))

    # Idempotence key must change with size and with mtime, and only with those.
    base = {"agent_id": "a" * 17, "size": 100, "mtime": 5}
    k1 = ingest_key(base)[0]
    k2 = ingest_key({**base, "size": 101})[0]
    k3 = ingest_key({**base, "mtime": 6})[0]
    cases.append(("key stable on identical bytes", k1 == ingest_key(dict(base))[0]))
    cases.append(("key changes on growth", k1 != k2))
    cases.append(("key changes on mtime", k1 != k3))

    # Turn mapping is derived from turn_index's own output, not re-counted.
    which = line_turn_mapper([{"t": 1, "role": "D", "line": 10},
                              {"t": 2, "role": "A", "line": 50}])
    cases.append(("line->turn: before T1", which(3) == "pre-T1"))
    cases.append(("line->turn: inside T1", which(20) == "T1 (D)"))
    cases.append(("line->turn: inside T2", which(999) == "T2 (A)"))

    # Marker rules must actually be a closed printed list, and must not match everything.
    hit = [n for n, rx in MARKER_RULES if rx.search("Jon ruled that the fence stands")]
    cases.append(("marker rule fires on a real ruling line", "ruling" in hit))
    hit2 = [n for n, rx in MARKER_RULES if rx.search("the quick brown fox jumps over it")]
    cases.append(("NEGATIVE CONTROL: marker rules do not match ordinary prose", not hit2))

    # THESE TWO CASES ARE INVERTED FROM THIS SCRIPT'S FIRST VERSION, DELIBERATELY.
    # They used to assert "no write target is under wiki/" and "every write target is under
    # gitignored raw/". Jon overruled that design on 2026-08-06 — *"Sounds like more needs to get
    # into the wiki by default when agents end"*, and *"I'm not worried about anything sensitive
    # landing in CFL. You don't need stronger fences."* An assertion that encodes a withdrawn
    # design is worse than no assertion: it makes the test suite vouch for the wrong thing. So the
    # controls now assert the ruling instead of the fence.
    wikidir = (REPO / "wiki").resolve()
    rawdir = (REPO / "raw").resolve()
    cases.append(("RULING 2026-08-06: I1 extracts land under wiki/ (tracked), by default",
                  wikidir in I1_ROOT.resolve().parents))
    cases.append(("I1 extracts land in the membrane-licensed wiki/intake-triage/ path",
                  (REPO / "wiki" / "intake-triage").resolve() in I1_ROOT.resolve().parents
                  or (REPO / "wiki" / "intake-triage").resolve() == I1_ROOT.resolve().parent))

    # The register — and ONLY the register — stays gitignored, for an availability reason:
    # it is append-only, so a tracked copy shows permanently `M` and `SessionStart`'s
    # `git pull --ff-only` aborts. Measured live, three fires after go-live. This is not a
    # content fence and must not be read as one.
    cases.append(("append-only register stays under gitignored raw/ (availability, not safety)",
                  rawdir in LIVE_REGISTER.resolve().parents))
    cases.append(("hook state stays under gitignored raw/",
                  rawdir in STATE_DIR.resolve().parents))

    # The tracked extract must not reproduce the register's permanently-`M` defect. An identical
    # re-fire must produce an identical stable hash, and a real content change must not.
    doc_a = "---\nx: 1\nextracted_utc: 2026-01-01T00:00:00Z\n---\n\nbody\n"
    doc_b = "---\nx: 1\nextracted_utc: 2026-09-09T09:09:09Z\n---\n\nbody\n"
    doc_c = "---\nx: 1\nextracted_utc: 2026-01-01T00:00:00Z\n---\n\nbody CHANGED\n"
    cases.append(("stable hash ignores the volatile timestamp (no tracked-file churn)",
                  stable_hash(doc_a) == stable_hash(doc_b)))
    cases.append(("NEGATIVE CONTROL: stable hash still changes on real content change",
                  stable_hash(doc_a) != stable_hash(doc_c)))
    cases.append(("existing_stable_hash round-trips what build_i1 writes",
                  existing_stable_hash(Path(os.devnull)) is None))

    # --- THE PROVISIONAL/FINAL DISTINCTION MUST BE A FACT, NOT A LABEL ------------------------
    # If `extract_status` were treated as volatile, promoting an otherwise byte-identical extract
    # from PROVISIONAL to FINAL would produce the SAME stable hash, the write would be skipped as
    # "unchanged", and the file on disk would keep saying PROVISIONAL forever while the register
    # and the marker both claimed it had been finalised. The feature would be a label over a no-op.
    # That is the exact shape of this repo's recorded failure mode — an instrument that passes by
    # resolving nothing — so it gets an explicit control in both directions.
    prov = ("---\nx: 1\nextract_status: PROVISIONAL\nextracted_utc: 2026-01-01T00:00:00Z\n"
            "finalised_utc: -\n---\n\nbody\n")
    fin = ("---\nx: 1\nextract_status: FINAL\nextracted_utc: 2026-01-01T00:00:00Z\n"
           "finalised_utc: 2026-01-01T00:00:00Z\n---\n\nbody\n")
    fin2 = ("---\nx: 1\nextract_status: FINAL\nextracted_utc: 2026-02-02T00:00:00Z\n"
            "finalised_utc: 2026-09-09T09:09:09Z\n---\n\nbody\n")
    cases.append(("NEGATIVE CONTROL: promoting PROVISIONAL->FINAL CHANGES the stable hash "
                  "(so the promotion actually rewrites the file, and is not a label over a no-op)",
                  stable_hash(prov) != stable_hash(fin)))
    cases.append(("re-finalising identical content is a no-op (finalised_utc is volatile, "
                  "so a second SessionEnd does not churn a tracked file)",
                  stable_hash(fin) == stable_hash(fin2)))
    cases.append(("extract_status is NOT in the volatile-line set",
                  _VOLATILE_LINES_RE.search("extract_status: FINAL\n") is None))
    cases.append(("finalised_utc IS in the volatile-line set",
                  _VOLATILE_LINES_RE.search("finalised_utc: 2026-01-01T00:00:00Z\n") is not None))
    cases.append(("the two stages are distinct strings and neither is empty",
                  STAGE_FINAL != STAGE_PROVISIONAL and bool(STAGE_FINAL) and
                  bool(STAGE_PROVISIONAL)))

    # A done-marker from a PROVISIONAL run must not let a FINAL run skip. Checked on the real
    # predicate rather than by restating it: this is the branch in ingest().
    _prev_prov = {"stage": STAGE_PROVISIONAL}
    cases.append(("NEGATIVE CONTROL: a PROVISIONAL done-marker does NOT satisfy a FINAL run",
                  _prev_prov.get("stage") != STAGE_FINAL))

    # read_i1_field is what the non-downgrade guard reads. It must return None, not raise, on a
    # file that does not exist — the guard runs on every provisional fire.
    cases.append(("read_i1_field on a missing file returns None rather than raising",
                  read_i1_field(Path("does-not-exist-anywhere.md"), "extract_status") is None))

    # The register carries no transcript text: it is built from counts and paths.
    cases.append(("register header states the no-content rule",
                  "gitignored" in REGISTER_HEADER and "GITIGNORED" in REGISTER_HEADER))

    # The withdrawn screen must stay unwired. Checked against the live module table, not against
    # this file's own text — a source-string check would match the assertion that performs it.
    cases.append(("NEGATIVE CONTROL: the withdrawn publication screen is never imported",
                  "publication_screen" not in sys.modules
                  and not any(getattr(v, "__name__", "") == "publication_screen"
                              for v in globals().values())))

    # The reused imports must be the real ones, not local reimplementations.
    cases.append(("I0 delegates to the canonical converter",
                  X.CONVERTER.name == "convert-claude-code.py"))
    cases.append(("mid-turn rule is the imported one",
                  midturn_messages.__module__ == "scan_midturn_messages"))

    # --- THE 2026-08-06 ADDITIONS: action ledger, three new rules, generated index -------------
    # The three new rules must FIRE on the real lines they were written for and must NOT fire on
    # ordinary prose. The ordinary-prose control above already runs against the whole rule list, so
    # it covers these too; these are the positive halves.
    def fires(rule, text):
        rx = dict(MARKER_RULES)[rule]
        return bool(rx.search(text))
    cases.append(("self-assessment rule fires on the phrase every brief asks for",
                  fires("self-assessment",
                        "The one thing most likely wrong: my INGEST-CANDIDATE rule may be inverted")))
    cases.append(("seed rule fires on a falsifier line",
                  fires("seed", "falsifier: show the extractor writes per-turn created_at")))
    cases.append(("brief-correction rule fires on an agent correcting its dispatcher",
                  fires("brief-correction",
                        "The brief said the runtime was >300s; measured, it was 79s.")))
    cases.append(("NEGATIVE CONTROL: the three new rules do not fire on ordinary prose",
                  not any(fires(r, "the quick brown fox jumps over the lazy dog and then rested")
                          for r in PROMOTED_RULES)))
    cases.append(("NEGATIVE CONTROL: 'seed' rule does not fire on the bare word 'seeds' in prose",
                  not fires("seed", "he planted seeds in the garden last spring")))
    cases.append(("every promoted rule is a real member of the printed marker vocabulary",
                  all(r in dict(MARKER_RULES) for r in PROMOTED_RULES)))

    # The action ledger must return a well-formed, all-zero result for a path that does not exist
    # rather than raising — it runs inside a hook on every fire.
    a = disk_actions(Path("no-such-transcript.jsonl"))
    cases.append(("action ledger on a missing JSONL returns zeros, does not raise",
                  a["tool_calls"] == 0 and a["distinct_count"] == 0 and a["commits"] == []))

    # claim_vs_record must FLAG the two 2026-08-06 failure shapes and must stay SILENT on the
    # ordinary case. A flag that fires on everything is the RATIO_FLOOR defect already on record.
    cases.append(("claim-vs-record flags a content-free return over real writes",
                  claim_vs_record(3, {"distinct_count": 7})[0] == "SHORT-RETURN-OVER-WRITES"))
    cases.append(("claim-vs-record flags a long return with zero writes",
                  claim_vs_record(6000, {"distinct_count": 0})[0] == "RETURN-WITHOUT-WRITES"))
    cases.append(("NEGATIVE CONTROL: claim-vs-record is SILENT on the ordinary case "
                  "(a flag that always fires is the RATIO_FLOOR defect)",
                  claim_vs_record(2600, {"distinct_count": 5})[0] == ""))

    # The index is GENERATED, and its write must be content-stable for exactly the same reason the
    # extract's is: a tracked file rewritten on every fire aborts `git pull --ff-only`.
    idx_a = "---\ngenerated_utc: 2026-01-01T00:00:00Z\n---\nrows\n"
    idx_b = "---\ngenerated_utc: 2026-09-09T09:09:09Z\n---\nrows\n"
    idx_c = "---\ngenerated_utc: 2026-01-01T00:00:00Z\n---\nrows CHANGED\n"
    cases.append(("index stable hash ignores its own generation timestamp",
                  stable_hash(idx_a) == stable_hash(idx_b)))
    cases.append(("NEGATIVE CONTROL: index stable hash changes when a row changes",
                  stable_hash(idx_a) != stable_hash(idx_c)))

    # Frontmatter reading is the cheap predicate the index depends on. If it silently returned {}
    # for real files, every count on the index would be zero and the page would look calm.
    cases.append(("read_frontmatter returns {} rather than raising on a missing file",
                  read_frontmatter(Path("does-not-exist.md")) == {}))
    # THE REAL-FILE PROBE, AND WHAT IT DELIBERATELY DOES NOT ASSERT.
    # This control first asserted that a real extract carries BOTH `agent_id` and `extract_status`,
    # and it FAILED — not because the parser is broken but because extracts written before the
    # PROVISIONAL/FINAL feature existed have no `extract_status` at all. The assertion was testing
    # the corpus's history under the name of testing the parser. It now asserts only what it means:
    # the parser must not silently return {} for real files, because a silently-empty parse would
    # make every count on the generated index read zero and the page would look calm while being
    # blank. The pre-feature extracts are REPORTED as a number instead of failing a control.
    _probe = sorted(I1_ROOT.glob("*/*.i1.md"))
    if _probe:
        _fms = [read_frontmatter(f) for f in _probe]
        _no_id = sum(1 for fm in _fms if not fm.get("agent_id"))
        _no_status = sum(1 for fm in _fms if not fm.get("extract_status"))
        cases.append((f"read_frontmatter recovers agent_id from ALL {len(_probe)} real extracts "
                      f"(a silently-empty parse would zero every index count)", _no_id == 0))
        print(f"  [observed, not asserted] {len(_probe)} extracts on disk; {_no_status} carry no "
              f"`extract_status` (written before that field existed) — they show as `?` in the "
              f"index rather than being counted as FINAL.")
    else:
        cases.append(("read_frontmatter real-file probe SKIPPED — no extracts on disk "
                      "(reported, not silently passed)", True))

    # --- THE FENCED-HEADING BUG, AS A CONTROL ---------------------------------------------------
    # An extract embeds the agent's verbatim return, and returns contain markdown. One real extract
    # quoted its own `## 4.` and `## 5.` headings inside a fenced block; the first parser latched
    # onto the agent's heading and returned ZERO recoverable lines for an extract whose frontmatter
    # counted one. Synthetic reproduction, so a future edit cannot reintroduce it silently.
    import tempfile
    _fake = ("---\nagent_id: deadbeef\n---\n\n"
             "## 2. The agent's final return (verbatim)\n\n"
             "```text\n"
             "## 4. A different document's section four\n"
             "- **T9 (A)** (line 1) — this bullet is INSIDE the agent's quoted return\n"
             "## 5. and its section five\n"
             "```\n\n"
             + SECTION4_HEADING + "\n\n"
             "### `brief-correction` — 1 matched, 1 shown\n\n"
             "- **T104 (A)** (line 3533) — the brief said X, measured Y\n\n"
             + SECTION5_HEADING + "\n")
    _tmp = Path(tempfile.gettempdir()) / "aei_selftest_category_lines.md"
    try:
        _tmp.write_text(_fake, encoding="utf-8")
        _got = category_lines(_tmp)
        cases.append(("REGRESSION CONTROL: a `## 4.` quoted inside the agent's own fenced return "
                      "does not hijack the section parser",
                      len(_got["brief-correction"]) == 1
                      and _got["brief-correction"][0][0] == "T104 (A)"))
        cases.append(("NEGATIVE CONTROL: the bullet inside the fenced block is NOT collected",
                      all(a != "T9 (A)" for v in _got.values() for a, _, _ in v)))
    except OSError as e:
        cases.append((f"category_lines regression control could not run ({e.__class__.__name__}) "
                      f"— REPORTED, not silently passed", False))

    cases.append(("build_i1 writes the exact heading category_lines looks for (one constant, "
                  "not two strings that can drift)",
                  SECTION4_HEADING.startswith("## 4. ") and SECTION5_HEADING.startswith("## 5. ")))

    # The root index must be per-SESSION. A per-agent root table is the flat form that breaks.
    cases.append(("root index is one row per session directory, not per agent",
                  "ONE ROW PER SESSION" in (build_root_index.__doc__ or "")))

    # --- PORTABLE PATHS (defect 2, measured 2026-08-06: 65/65 absolute) ------------------------
    _inside = REPO / "raw" / "transcripts" / "claude-code" / "subagents" / "f01909" / "x.md"
    _rel = repo_rel(_inside)
    cases.append(("repo_rel: a path inside the repo becomes repo-relative",
                  _rel == "raw/transcripts/claude-code/subagents/f01909/x.md"))
    cases.append(("repo_rel: no backslashes and no drive letter survive (Git Bash reads this repo "
                  "too, and a backslash is not a separator to it)",
                  "\\" not in _rel and not re.match(r"^[A-Za-z]:", _rel)))
    _outside = repo_rel(r"C:\Users\JonSc\.claude\projects\proj\uuid\subagents\agent-a1.jsonl")
    cases.append(("NEGATIVE CONTROL: a genuinely EXTERNAL path is NOT faked into a relative form "
                  "(no `../../..` chain out of the repo)",
                  not _outside.startswith("..")))
    cases.append(("repo_rel leaves the ABSENT sentinel alone", repo_rel("ABSENT") == "ABSENT"))
    cases.append(("repo_rel is idempotent — re-running the migration cannot double-relativise",
                  repo_rel(_rel) == _rel))

    # --- DISCRIMINATING TAGS (defect 1, measured: 65 extracts -> 1 distinct tags line) ----------
    _t1 = tags_line("skills-executor", "Deploy parity — 9 diverged skills")
    _t2 = tags_line("intake-executor", "Register tickets T-05, T-08, T-14, T-16")
    cases.append(("THE DEFECT'S DIRECT CONTROL: two different agents get DIFFERENT tag lines",
                  _t1 != _t2))
    cases.append(("mechanism tags are KEPT, so the whole class stays selectable",
                  all(m in _t1 and m in _t2 for m in MECHANISM_TAGS)))
    cases.append(("subject tags come from the artifact's own words",
                  "deploy" in _t1 and "parity" in _t1 and "diverged" in _t1))
    cases.append(("the agent's role becomes a tag", "skills-executor" in _t1))
    cases.append(("ticket ids survive tokenisation (`T-05` is not split into `t` and `05`)",
                  "t-05" in _t2 and "t-16" in _t2))
    # Built FROM `TAG_STOPWORDS` rather than from a hand-typed list of words I believe are in it —
    # the first version of this control asserted a word (`one`) that is deliberately NOT a stopword,
    # and so it tested my memory of the list rather than the list. A control whose expectations are
    # typed separately from the thing it checks is a second source of truth.
    _stop_sentence = " ".join(sorted(TAG_STOPWORDS)[:40])
    cases.append(("NEGATIVE CONTROL: a sentence made only of the FIXED stopword list yields no "
                  "subject tags", derive_subject_tags("UNKNOWN", _stop_sentence) == []))
    cases.append(("the stopword list is function words only — it does not filter domain words "
                  "(filtering those would be the taxonomy call this refuses to make)",
                  not TAG_STOPWORDS & {"wiki", "seed", "wave", "skills", "ledger", "extract",
                                       "session", "agent", "memory", "corpus"}))
    cases.append(("NEGATIVE CONTROL: a bare number is not a tag",
                  "9" not in derive_subject_tags("explore", "Wave 0 — 9 things")))
    cases.append(("NEGATIVE CONTROL: derivation is PURE — same inputs, same output, so the "
                  "migration and the generator cannot drift",
                  tags_line("explore", "Cold FBC synthesis")
                  == tags_line("explore", "Cold FBC synthesis")))
    cases.append(("NEGATIVE CONTROL: derivation is NOT corpus-relative — one extract's tags do not "
                  "depend on any other extract (adding a file must not silently retag old ones)",
                  derive_subject_tags("explore", "Cold FBC synthesis")
                  == derive_subject_tags("explore", "Cold FBC synthesis")))
    cases.append(("UNKNOWN metadata degrades to mechanism tags only, rather than tagging "
                  "everything `unknown`",
                  derive_subject_tags("UNKNOWN", "UNKNOWN") == []))

    # The migration's body regex must still match the sentence LEGACY extracts on disk contain.
    # `build_i1` no longer emits this text (FINAL_RETURN_CAP is struck, SG-4) — 8000 here is a
    # historical literal, testing `rewrite_existing`'s ability to path-migrate OLD files, not a
    # live constant. Two strings that must agree is the drift shape that broke category_lines();
    # here the format is short enough to reproduce exactly.
    _emitted = (f"**TRUNCATED at {8000:,} of {9781:,} chars.** The remainder is in "
                f"`raw/transcripts/claude-code/subagents/f01909/x.md` at T104 (A). Truncation is "
                f"announced here rather than applied silently.")
    cases.append(("the migration's truncation-notice pattern matches what build_i1 emits",
                  bool(_TRUNC_PATH_RE.search(_emitted))))
    cases.append(("NEGATIVE CONTROL: the truncation pattern does NOT match an ordinary quoted "
                  "path in an agent's verbatim return (verbatim content must not be edited)",
                  not _TRUNC_PATH_RE.search('cd "G:/My Drive/Claude" && git status')))

    # --- REAL-FILE MEASUREMENT, PRINTED AS A NUMBER --------------------------------------------
    # The brief that produced this fix measured `65 extracts -> 1 distinct tag line`. The control
    # therefore measures the same quantity on the same population rather than asserting a design.
    # A fix that yields 2 has not fixed it, so the number is PRINTED, not just thresholded.
    _ex = sorted(I1_ROOT.glob("*/*.i1.md"))
    if _ex:
        _tagvals = {read_frontmatter(f).get("tags", "<MISSING>") for f in _ex}
        _abs = 0
        _abs_same_drive = 0
        _repo_drive = os.path.splitdrive(str(REPO))[0].upper()
        for f in _ex:
            _fm = read_frontmatter(f)
            for _k in ("transcript_path", "sidecar_path"):
                _v = _fm.get(_k) or ""
                if re.match(r"^[A-Za-z]:[\\/]", _v):
                    _abs += 1
                    # repo_rel()'s own documented contract (see its docstring above): an absolute
                    # path is the CORRECT output, not a defect, when the target is on a different
                    # drive than REPO (os.path.relpath raises ValueError cross-drive on Windows,
                    # and repo_rel deliberately keeps the absolute rather than fabricate a
                    # portable-looking lie). Only a same-drive absolute means repo_rel had a real
                    # relative path available and failed to produce it.
                    if os.path.splitdrive(_v)[0].upper() == _repo_drive:
                        _abs_same_drive += 1
        print(f"  [measured] {len(_ex)} extract(s) on disk -> {len(_tagvals)} distinct `tags:` "
              f"line(s); {_abs} absolute transcript/sidecar path field(s) remaining, "
              f"{_abs_same_drive} of them same-drive-as-REPO "
              f"(denominator {2 * len(_ex)}).")
        cases.append((f"MEASURED: distinct tag lines > 1 across the {len(_ex)} extracts on disk "
                      f"(got {len(_tagvals)})", len(_tagvals) > 1))
        cases.append((f"MEASURED: zero SAME-DRIVE-AS-REPO absolute transcript_path/sidecar_path "
                      f"over {2 * len(_ex)} field(s) (cross-drive absolutes are repo_rel's "
                      f"documented correct output, not a defect; got {_abs} total absolute, "
                      f"{_abs_same_drive} same-drive)", _abs_same_drive == 0))
    else:
        cases.append(("tag/path real-file measurement SKIPPED — no extracts on disk "
                      "(reported, not silently passed)", True))

    # --- TERMINAL GATE -------------------------------------------------------------------------
    # The gate that stops a self-routing agent's extract from being rewritten on turns that do no
    # work. Every control below is stated as a pair: the thing it must suppress, and the thing it
    # must NOT — a suppressor that suppresses everything is a mute button, not a gate.
    import shutil as _shutil
    import tempfile as _tempfile

    _T = RAR.TERMINAL_TOKEN

    def _frow(id6, role, disp):
        return f"| T | auto | {id6} | subagent | {role} | x.jsonl | {disp} | - |"

    def _ledger(lines):
        d = _tempfile.mkdtemp(prefix="aei-led-")
        p = Path(d) / "LEDGER.md"
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return p, d

    def _i1root(entries):
        """entries = [(parent6, filename)] — a fake wiki/intake-triage/agent-end/ tree."""
        d = _tempfile.mkdtemp(prefix="aei-i1-")
        for p6, name in entries:
            (Path(d) / p6).mkdir(parents=True, exist_ok=True)
            (Path(d) / p6 / name).write_text("x", encoding="utf-8")
        return Path(d), d

    _tmpdirs = []
    try:
        _led, _d = _ledger([
            _frow("aaa111", "skills-executor", f"**ROUTED** {_T}"),
            _frow("bbb222", "wiki-executor",
                  "**ROUTED** *(landed as commit deadbee; nothing terminal about it)*"),
            _frow("ccc333", "skills-executor", "**ROUTED (terminal)**"),
            _frow("ddd444", "extractor", "PENDING"),
            _frow("eee555", "security-builder",
                  "**ROUTED** *(the reason this row is marked terminal: routing a return IS a "
                  "return, and the chain terminates only by declaration)*"),
            _frow("UNKNOWN", "x", f"**ROUTED** {_T}"),
        ])
        _tmpdirs.append(_d)
        _ids = terminal_ids(_led)
        cases.append(("canonical [TERMINAL] token is read from the ledger", "aaa111" in _ids))
        cases.append(("legacy `(terminal)` disposition head is read too", "ccc333" in _ids))
        cases.append(("NEGATIVE CONTROL: a plain ROUTED row is NOT terminal", "bbb222" not in _ids))
        cases.append(("NEGATIVE CONTROL: a PENDING row is NOT terminal", "ddd444" not in _ids))
        cases.append(("NEGATIVE CONTROL: the word 'terminal' inside NARRATIVE prose is not a "
                      "declaration", "eee555" not in _ids))
        cases.append(("NEGATIVE CONTROL: a non-hex id6 cell is never a terminal id",
                      "UNKNOWN" not in _ids))
        # The predicate is IMPORTED from route_agent_return, never restated. If this ever fails,
        # two instruments have started disagreeing about what "terminal" means, which is the exact
        # divergence defect this file's header calls out.
        cases.append(("terminality predicate is route_agent_return's, not a second copy",
                      terminal_ids.__globals__["RAR"].is_terminal_row.__module__
                      == "route_agent_return"))

        _root, _d2 = _i1root([("f00001", "code-2026-08-06-aaa111-skills-executor-x.i1.md")])
        _tmpdirs.append(_d2)
        _t_term = {"agent6": "aaa111", "parent6": "f00001"}
        _t_term_noex = {"agent6": "aaa111", "parent6": "f00002"}
        _t_plain = {"agent6": "bbb222", "parent6": "f00001"}

        _skip, _why = terminal_skip(_t_term, _led, _root)
        cases.append(("TERMINAL + an extract already on disk -> re-extraction suppressed", _skip))
        cases.append(("the suppression reason names the ledger, so a reader can check it",
                      "ROUTING-LEDGER" in _why))

        _skip, _why = terminal_skip(_t_term_noex, _led, _root)
        cases.append(("NEGATIVE CONTROL: TERMINAL but NO extract exists -> one is still written "
                      "(the rule is stop RE-extracting, not never extract)", not _skip))

        _skip, _ = terminal_skip(_t_plain, _led, _root)
        cases.append(("NEGATIVE CONTROL: a non-terminal agent is never gated — its path through "
                      "ingest() is unchanged, however much its transcript grew", not _skip))

        # FAIL OPEN. A missing ledger must not silently mute the whole instrument.
        _skip, _ = terminal_skip(_t_term, Path(_d) / "does-not-exist.md", _root)
        cases.append(("NEGATIVE CONTROL: an absent/unreadable ledger fails OPEN (nothing terminal, "
                      "extraction proceeds)", not _skip))
        cases.append(("absent ledger yields an empty terminal set, not a crash",
                      terminal_ids(Path(_d) / "does-not-exist.md") == {}))
    finally:
        for _d in _tmpdirs:
            _shutil.rmtree(_d, ignore_errors=True)

    # --- THE GATE MUST NOT BLOCK FINALISATION --------------------------------------------------
    # `session_finalise.py` calls `ingest(t, force=True, stage=STAGE_FINAL)`. If the gate caught
    # that call, a terminal agent's extract would be frozen PROVISIONAL at whatever turn its
    # terminal row happened to land on — a truncation defect, which is worse than the churn defect
    # being fixed, because churn is visible in `git status` and truncation looks finished.
    #
    # This reads the FINALISER'S OWN SOURCE for the call it makes, rather than asserting my memory
    # of it. A control that restates the thing it checks is a second source of truth.
    try:
        _fin_src = (REPO / "scripts" / "audit" / "session_finalise.py").read_text(
            encoding="utf-8", errors="replace")
        _fin_call = re.search(r"AEI\.ingest\(([^)]*)\)", _fin_src)
        _fin_args = _fin_call.group(1) if _fin_call else ""
        cases.append(("session_finalise still calls ingest with force=True", "force=True" in _fin_args))
        cases.append(("session_finalise still calls ingest with stage=FINAL",
                      "STAGE_FINAL" in _fin_args))
        # The gate's own condition, read from THIS file, must exempt both.
        _gate_src = re.search(r"if stage == STAGE_PROVISIONAL and not force:",
                              (REPO / "scripts" / "audit" / "agent_end_ingest.py").read_text(
                                  encoding="utf-8", errors="replace"))
        cases.append(("the gate exempts BOTH of the finaliser's markers (stage=FINAL and force), "
                      "so neither can be removed silently", bool(_gate_src)))
    except OSError:
        cases.append(("finalisation-exemption control SKIPPED — session_finalise.py unreadable "
                      "(reported, not silently passed)", False))

    # --- LIVE MEASUREMENT against the real ledger and the real extracts ------------------------
    _real_led = REPO / RAR.LEDGER
    if _real_led.exists():
        _live = terminal_ids(_real_led)
        _all_ids = set()
        for _line in _real_led.read_text(encoding="utf-8", errors="replace").splitlines():
            _c = RAR.row_cells(_line)
            if _c and re.fullmatch(r"[0-9a-f]{6}", _c[2] or ""):
                _all_ids.add(_c[2])
        print(f"  [measured] live ledger: {len(_all_ids)} distinct agent id(s), "
              f"{len(_live)} declared TERMINAL.")
        cases.append((f"LIVE: terminal ids are a MINORITY of the ledger, not everything "
                      f"({len(_live)}/{len(_all_ids)})", 0 < len(_live) < len(_all_ids)))
        cases.append(("LIVE: a1f02e — the measured self-routing loop — classifies TERMINAL",
                      "a1f02e" in _live))
        _a1 = {"agent6": "a1f02e", "parent6": "f01909"}
        cases.append(("LIVE: a1f02e has an extract on disk, so a further fire is suppressed",
                      terminal_skip(_a1)[0]))
    else:
        cases.append(("live-ledger measurement SKIPPED — no ledger on disk (reported, not "
                      "silently passed)", True))

    print("=== SELF-TEST (negative controls included) ===")
    bad = 0
    for name, ok in cases:
        bad += 0 if ok else 1
        print(f"  {name:<62} : {'PASS' if ok else 'FAIL'}")
    print(f"\nRESULT: {'PASS' if not bad else 'FAIL'} — {len(cases)-bad}/{len(cases)}")
    return 0 if not bad else 1


def publish_existing(apply=False):
    """Migrate pre-ruling I1 extracts from gitignored `raw/extracts/agent-end/` into `wiki/`.

    COPY, NEVER MOVE. Jon's standing constraint is NO DESTRUCTIVE ACTS; the legacy copies stay on
    disk exactly where they are. This is idempotent: an extract whose tracked copy already carries
    the same stable hash is left alone.

    The migrated copy gets the wiki frontmatter fields (`title`, `retrieval_key`, `coverage_class`)
    that `build_i1` now emits, because a page landing in `wiki/` without them would be counted by
    the citation-coverage instrument as an uncited claim-bearing page — see
    `wiki/references/agent-memory/README.md` on the frontmatter-driven exemption.
    """
    rows = []
    for src in sorted(LEGACY_I1_ROOT.rglob("*.i1.md")):
        try:
            text = src.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            rows.append((src, None, f"UNREADABLE: {e}"))
            continue
        fm = {}
        m = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
        if not m:
            rows.append((src, None, "NO FRONTMATTER — skipped, nothing deleted"))
            continue
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "\t", "-")):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
        parent6 = (fm.get("parent_session") or "unknown")[:6]
        agent6 = (fm.get("agent_id") or "unknown")[:6]
        role = fm.get("agent_type") or "UNKNOWN"

        if "coverage_class:" not in m.group(1):
            header = (f"title: \"I1 extract — agent {agent6} ({role})\"\n"
                      f"source_kind: extract\n"
                      f"retrieval_key: agent-end-i1-{agent6}\n"
                      f"tags: {tags_line(role, fm.get('agent_description'))}\n"
                      f"coverage_class: untraced-by-design\n"
                      f"coverage_class_reason: mechanical I1 extract written automatically at "
                      f"SubagentStop; it makes no citable claim of its own and is excluded from "
                      f"citation-coverage measurement\n"
                      f"migrated_from: {os.path.relpath(src, REPO)}".replace("\\", "/") + "\n")
            text = "---\n" + header + m.group(1) + "\n---\n" + text[m.end():]

        sha = stable_hash(text)
        if "i1_content_sha256:" not in text:
            text = text.replace("extract_level: I1\n",
                                f"extract_level: I1\ni1_content_sha256: {sha}\n", 1)
        dst = I1_ROOT / parent6 / src.name
        if dst.exists() and existing_stable_hash(dst) == sha:
            rows.append((src, dst, "unchanged"))
            continue
        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(text, encoding="utf-8")
        rows.append((src, dst, "written" if apply else "would-write"))

    print(f"=== publish-existing — {'APPLY' if apply else 'DRY RUN'} ===")
    for src, dst, how in rows:
        print(f"  [{how:<12}] {os.path.relpath(src, REPO)}")
        if dst:
            print(f"                 -> {os.path.relpath(dst, REPO)}".replace("\\", "/"))
    moved = sum(1 for _, _, h in rows if h in ("written", "would-write"))
    print(f"\nDENOMINATOR: {len(rows)} legacy I1 extract(s) under "
          f"{os.path.relpath(LEGACY_I1_ROOT, REPO)}".replace("\\", "/"))
    print(f"  into wiki/: {moved}   already current: "
          f"{sum(1 for _, _, h in rows if h == 'unchanged')}   "
          f"skipped: {sum(1 for _, _, h in rows if h not in ('written', 'would-write', 'unchanged'))}")
    print("  legacy copies: UNTOUCHED (no destructive acts)")
    return 0


_FM_BLOCK_RE = re.compile(r"\A---\r?\n(.*?\r?\n)---\r?\n", re.DOTALL)
_SHA_LINE_RE = re.compile(r"^i1_content_sha256:.*\r?\n", re.MULTILINE)
_TRUNC_PATH_RE = re.compile(
    r"^(\*\*TRUNCATED at [\d,]+ of [\d,]+ chars\.\*\* The remainder is in `)([^`]+)(` at )",
    re.MULTILINE)
_MIGRATED_PATH_KEYS = ("transcript_path", "sidecar_path", "jsonl_path")


def rewrite_existing(apply=False):
    """Bring extracts ALREADY on disk up to what `build_i1` now writes. In place. Nothing deleted.

    WHY THIS EXISTS RATHER THAN "just re-run the ingest"
    ----------------------------------------------------
    A fix applied only to NEW output leaves the old files wrong and leaves the script disagreeing
    with its own corpus. That half-landed shape is on record here: on 2026-07-28 a partly-applied
    path move silently disabled three instruments, one of them a BLOCKING gate, which then passed
    by resolving nothing. So the 65 existing extracts are brought forward.

    It rewrites EXACTLY four things, and touches nothing else:
      1. `tags:`            -> mechanism tags + per-extract subject tags (`tags_line`)
      2. `transcript_path:` -> `repo_rel`
      3. `sidecar_path:`    -> `repo_rel`
      4. `jsonl_path:`      -> `repo_rel` (a no-op for the genuinely-external JSONL beyond
                               normalising separators — see repo_rel's docstring)
    plus the ONE body line this script authored that carries a path (the TRUNCATED notice), and the
    `i1_content_sha256:` stamp that has to follow any real content change.

    **VERBATIM CONTENT IS NOT TOUCHED.** Measured before writing this: the 65 extracts contain 269
    occurrences of the repo root, of which 130 are these frontmatter fields and ~87 are `cd "G:/My
    Drive...` inside agents' own quoted returns and commit commands. A blanket search-and-replace
    would have silently edited quoted text — which is the uncited-punctuation-edit-inside-a-quote
    failure already on this repo's record. So the rewrite is keyed on the exact frontmatter keys
    and on one exact emitted sentence, never on the path string alone.

    **It reproduces `build_i1`, it does not reimplement it.** The tag value comes from the same
    `tags_line()` the generator calls, fed from the extract's own `agent_type` / `agent_description`
    frontmatter — which are the very fields `build_i1` wrote from `meta`. Same function, same
    inputs, same bytes. `--verify-regenerate` proves that end-to-end against the real generator.

    IDEMPOTENT: a file whose bytes do not change is reported `unchanged` and not written, so a
    second run dirties nothing and `git pull --ff-only` keeps working.
    """
    files = sorted(I1_ROOT.glob("*/*.i1.md"))
    rows = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            rows.append((f, f"UNREADABLE: {e.__class__.__name__}", []))
            continue
        m = _FM_BLOCK_RE.match(text)
        if not m:
            rows.append((f, "NO FRONTMATTER — skipped, nothing written", []))
            continue
        fm_text, body = m.group(1), text[m.end():]
        fm = read_frontmatter(f)
        changed = []

        new_lines = []
        for line in fm_text.splitlines(keepends=True):
            nl = line[len(line.rstrip("\r\n")):]
            k, _, v = line.rstrip("\r\n").partition(":")
            if k == "tags":
                want = tags_line(fm.get("agent_type"), fm.get("agent_description"))
                if v.strip() != want:
                    changed.append("tags")
                    line = f"tags: {want}{nl}"
            elif k in _MIGRATED_PATH_KEYS:
                want = repo_rel(v.strip())
                if v.strip() != want:
                    changed.append(k)
                    line = f"{k}: {want}{nl}"
            new_lines.append(line)
        new_fm = "".join(new_lines)

        def _trunc(mm):
            rel = repo_rel(mm.group(2))
            return mm.group(1) + rel + mm.group(3)
        new_body, n_trunc = _TRUNC_PATH_RE.subn(_trunc, body)
        if new_body != body:
            changed.append(f"truncation-notice x{n_trunc}")

        new_text = "---\n" + new_fm + "---\n" + new_body
        # Restamp. `stable_hash` strips the sha line itself, so this matches what `build_i1`
        # computes on a document that never had one.
        sha = stable_hash(new_text)
        if _SHA_LINE_RE.search(new_text):
            new_text = _SHA_LINE_RE.sub(f"i1_content_sha256: {sha}\n", new_text, count=1)
        else:
            new_text = re.sub(r"^(extracted_utc:.*\r?\n)",
                              lambda mm: mm.group(1) + f"i1_content_sha256: {sha}\n",
                              new_text, count=1, flags=re.MULTILINE)

        if new_text == text:
            rows.append((f, "unchanged", changed))
            continue
        if apply:
            f.write_text(new_text, encoding="utf-8")
        rows.append((f, "written" if apply else "would-write", changed))

    print(f"=== rewrite-existing — {'APPLY' if apply else 'DRY RUN'} ===")
    for f, how, changed in rows:
        if how != "unchanged":
            print(f"  [{how:<12}] {repo_rel(f)}  ({', '.join(changed) or 'stamp only'})")
    n_written = sum(1 for _, h, _ in rows if h in ("written", "would-write"))
    n_same = sum(1 for _, h, _ in rows if h == "unchanged")
    n_skip = len(rows) - n_written - n_same
    print(f"\nDENOMINATOR: {len(rows)} extract file(s) matched the glob "
          f"`wiki/intake-triage/agent-end/*/*.i1.md`.")
    print(f"  rewritten: {n_written}   already current (idempotent no-op): {n_same}   "
          f"skipped/unreadable: {n_skip}")
    print("  Scope: this repo's tracked I1 extracts only. Legacy gitignored copies under "
          "raw/extracts/agent-end/ are NOT touched by this mode and nothing anywhere is deleted.")
    print(tag_audit_text())
    print(path_audit_text())
    return 0


def tag_audit_text():
    """MEASURE the defect this fix targets, on the files as they now stand. Prints denominators.

    Distinct `tags:` lines over N extracts. **1 is the broken state** — that was the measurement
    that started this: 65 files, 1 tag line, so every tag query returns the whole corpus. A number
    barely above 1 is barely better, and this prints the actual number rather than a verdict.
    """
    files = sorted(I1_ROOT.glob("*/*.i1.md"))
    lines = {}
    for f in files:
        v = read_frontmatter(f).get("tags", "<MISSING>")
        lines.setdefault(v, []).append(f.name)
    n = len(files)
    distinct = len(lines)
    out = [f"\nTAG AUDIT — {distinct} distinct `tags:` line(s) across {n} extract file(s) "
           f"(glob `wiki/intake-triage/agent-end/*/*.i1.md`)."]
    if n:
        out.append(f"  discriminating power: {distinct}/{n} = {distinct / n:.2f} "
                   f"(1.00 = every extract distinguishable; {1 / n:.2f} = the broken state, "
                   f"one shared line)")
    shared = {k: v for k, v in lines.items() if len(v) > 1}
    if shared:
        out.append(f"  {len(shared)} tag line(s) shared by more than one extract:")
        for k, v in sorted(shared.items(), key=lambda kv: -len(kv[1]))[:5]:
            out.append(f"    x{len(v)}  {k[:110]}")
    else:
        out.append("  no two extracts share a tag line.")
    return "\n".join(out)


def path_audit_text():
    """Are the emitted path fields portable? Counts, with the denominator, per field."""
    files = sorted(I1_ROOT.glob("*/*.i1.md"))
    out = [f"\nPATH AUDIT — {len(files)} extract file(s)."]
    for key in _MIGRATED_PATH_KEYS:
        vals = [read_frontmatter(f).get(key) for f in files]
        present = [v for v in vals if v and v != "ABSENT"]
        absolute = [v for v in present if re.match(r"^[A-Za-z]:[\\/]|^[\\/]{2}", v)]
        backslash = [v for v in present if "\\" in v]
        resolves = sum(1 for v in present
                       if not re.match(r"^[A-Za-z]:[\\/]", v) and (REPO / v).exists())
        out.append(f"  {key:<16} present {len(present)}/{len(files)}  |  absolute "
                   f"{len(absolute)}  |  containing a backslash {len(backslash)}  |  "
                   f"repo-relative AND resolving on disk {resolves}")
    out.append("  `jsonl_path` is EXPECTED to stay absolute: the subagent JSONL lives under "
               "%USERPROFILE%\\.claude\\projects\\, outside this tree on every machine.")
    return "\n".join(out)


def verify_regenerate(limit=6):
    """PROVE the migration equals the generator, instead of asserting it.

    Picks extracts whose recorded `jsonl_size`/`jsonl_mtime` still match the JSONL on disk — those
    and only those must regenerate byte-identically — and re-runs the REAL `ingest(..., force=True)`
    against them. A pass is the generator reporting `unchanged`, i.e. its freshly built document
    hashed to exactly what the migration left on disk.

    This is the control that a hand-written migration usually lacks: without it, "the migration does
    what the generator does" is a claim by the same author as the migration.
    """
    files = sorted(I1_ROOT.glob("*/*.i1.md"))
    cands = []
    for f in files:
        fm = read_frontmatter(f)
        jp = fm.get("jsonl_path")
        if not jp:
            continue
        p = Path(jp)
        if not p.is_file():
            continue
        st = p.stat()
        if str(st.st_size) == fm.get("jsonl_size") and str(int(st.st_mtime)) == fm.get("jsonl_mtime"):
            cands.append((f, p, fm.get("extract_status")))
    print(f"=== verify-regenerate ===")
    print(f"  {len(files)} extract(s) on disk; {len(cands)} have a JSONL whose size AND mtime still "
          f"match what the extract recorded — only those can regenerate byte-identically, and only "
          f"those are testable here. The remaining {len(files) - len(cands)} have grown or their "
          f"JSONL is gone; re-running them would produce legitimately NEW content, which would "
          f"prove nothing about this migration.")
    tested = cands[:limit]
    ok = bad = 0
    for f, p, status in tested:
        t, why = resolve_from_jsonl(p)
        if t is None:
            print(f"  [SKIP      ] {f.name} — {why}")
            continue
        stage = STAGE_FINAL if status == STAGE_FINAL else STAGE_PROVISIONAL
        st, msg, detail = ingest(t, force=True, stage=stage)
        verdict = detail.get("write") if isinstance(detail, dict) else "?"
        good = (st == "OK" and verdict in ("unchanged", "kept-final"))
        ok += 1 if good else 0
        bad += 0 if good else 1
        print(f"  [{'MATCH' if good else 'DIVERGED':<10}] {f.name} -> generator says "
              f"'{verdict}' ({st})")
    print(f"\nDENOMINATOR: {len(tested)} of {len(cands)} eligible extract(s) regenerated "
          f"(cap {limit}); {ok} byte-identical to the migrated file, {bad} diverged.")
    print("  A MATCH means: the real generator rebuilt the document from the JSONL and its stable "
          "hash equalled what the migration wrote, so the two are not two implementations.")
    return 0 if bad == 0 else 1


def main():
    argv = sys.argv[1:]
    if "--self-test" in argv:
        return self_test()
    if "--rewrite-existing" in argv:
        return rewrite_existing(apply=("--apply" in argv))
    if "--tag-audit" in argv:
        print(tag_audit_text())
        print(path_audit_text())
        return 0
    if "--verify-regenerate" in argv:
        i = argv.index("--verify-regenerate")
        lim = int(argv[i + 1]) if len(argv) > i + 1 and argv[i + 1].isdigit() else 6
        return verify_regenerate(limit=lim)
    if "--publish-existing" in argv:
        return publish_existing(apply=("--apply" in argv))
    if "--index" in argv:
        i = argv.index("--index")
        arg = argv[i + 1] if len(argv) > i + 1 and not argv[i + 1].startswith("-") else "--all"
        targets = ([d.name for d in sorted(I1_ROOT.iterdir()) if d.is_dir()]
                   if arg == "--all" else [arg[:6]])
        print(f"=== index rebuild — {len(targets)} session director"
              f"{'y' if len(targets) == 1 else 'ies'} under "
              f"{os.path.relpath(I1_ROOT, REPO)} ===".replace("\\", "/"))
        for p6 in targets:
            verdict, _, path = build_session_index(p6)
            n = len(list((I1_ROOT / p6).glob("*.i1.md")))
            print(f"  [{verdict:<12}] {p6}  ({n} extract(s))  "
                  f"-> {os.path.relpath(path, REPO)}".replace("\\", "/"))
        verdict, _, path = build_root_index()
        print(f"  [{verdict:<12}] ROOT       -> "
              f"{os.path.relpath(path, REPO)}".replace("\\", "/"))
        print(f"\nDENOMINATOR: {len(targets)} session(s) indexed; "
              f"{len(list(I1_ROOT.glob('*/*.i1.md')))} extract file(s) matched "
              f"`wiki/intake-triage/agent-end/*/*.i1.md`. Scope: this repo's tracked extracts "
              f"only — NOT the routing ledger, which counts return events across all sessions.")
        return 0
    if "--jsonl" in argv:
        i = argv.index("--jsonl")
        try:
            target = argv[i + 1]
        except IndexError:
            print("--jsonl requires a path")
            return 0
        t, why = resolve_from_jsonl(Path(target))
        if t is None:
            print(f"NOT RUN — {why}")
            return 0
        status, msg, detail = ingest(
            t, force=("--force" in argv), verbose=True,
            stage=(STAGE_FINAL if "--final" in argv else STAGE_PROVISIONAL))
        print(f"{status}: {msg}")
        if detail:
            print(json.dumps(detail, indent=1, default=str))
        return 0
    return hook_mode()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # never block, never crash a session
        try:
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "SubagentStop",
                "additionalContext": f"[agent-end-ingest] CRASHED ({e.__class__.__name__}: {e}). "
                                     f"I0/I1 did not run for this return."}}))
        except Exception:
            pass
        sys.exit(0)
