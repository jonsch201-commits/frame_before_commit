#!/usr/bin/env python3
"""Build the CFL vector-embedded GraphRAG index: one durable sqlite file.

WHAT THIS IS FOR, in Jon's words (2026-08-17 16:5x, verbatim):
  "When can we move shit out of the huge Claude md Files and into the wiki, read when needed based
  on vector embedded graph rag?"
⭐ So the deliverable is CONTEXT ECONOMY, not retrieval for its own sake. Every session on every
trunk currently pays a constant tax before a word of work: global CLAUDE.md + CFL project CLAUDE.md
(~51 KB, ~13k tokens). This index is the mechanism that buys that back -- material moves to the
wiki and is READ WHEN NEEDED. ⛔ It is a MOVE, never a trim: nothing here deletes anything.

DESIGN, and every clause is answering a named failure mode:

  * CHUNK on markdown headings, keeping the heading path and the LINE SPAN. A retrieved line that
    cannot name `file:line` is not usable in this program -- half our defects this month were
    citations nobody could re-derive.
  * EMBED locally (see embedder.py). Handles "imprecise language".
  * LEXICAL index with a trigram vocabulary, so `retrieve.py` can fuzzy-expand a MISSPELLED query
    term to the corpus term it meant. ⛔ This -- not the embedder -- is what answers Jon's typos.
  * GRAPH edges file->file from [[wikilinks]] and relative markdown links, so a hit can be scoped
    and its neighbourhood named. Provenance chain: chunk -> file -> linked claims.
  * ONE SQLITE FILE that survives a reboot. "Durable" is Jon's word and it means the index is a
    file, not a session.
  * IDEMPOTENT by content hash: unchanged files are not re-embedded, and running twice is a no-op.
  * SINGLE-INSTANCE BY LOCK. ⛔ This program's D17: a launcher living in a shared tree WILL be run
    twice by a helpful seat. The lock FAILS CLOSED -- a live holder makes the second run refuse
    with exit 4, and a stale holder (dead pid) is reclaimed rather than blocking forever.

Usage:
  python scripts/graphrag/build_index.py [--db PATH] [--embedder auto|static|hash] [--force]
                                         [--root DIR] [--include PATH]...
  python scripts/graphrag/build_index.py --selftest

Exit codes: 0 built · 2 bad args/corpus · 4 another build holds the lock · 5 selftest failed.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sqlite3
import subprocess  # engine-provenance banner only; see the `engine :` line in build()'s summary
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embedder import load_embedder  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ⛔ THE INDEX LIVES OFF DRIVE, and this was a CORRECTION, not a preference — the first build put
# it at `wiki/.graphrag/` and the repo taught me why that is wrong within fifteen minutes:
#   1. This repo's own hygiene rule already says worktrees live off Drive because "on-Drive
#      worktrees mirror to the cloud, poison cold reads, and create search echoes." A 60 MB sqlite
#      rewritten on every build is that rule's worst case, not an exception to it.
#   2. `[measured 2026-08-17 17:1x]` the on-Drive build was still running at 14 minutes and had
#      produced 60 MB of journal churn; the same build off Drive is a different order of magnitude.
#      Google Drive's sync layer sees every page write.
#   3. It is a DERIVED artifact. The markdown is the record; this file is rebuildable from it, so
#      it is exactly the thing that must not be in the tree. Nothing here is lost by rebuilding.
# ⚠️ "Durable" is still satisfied and it is Jon's word: LOCALAPPDATA survives a reboot. Durable
# means the index is a FILE, not a session — it never meant "synced to the cloud."
_LOCAL = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/.cache")
GRAPHRAG_HOME = os.environ.get("CFL_GRAPHRAG_HOME", os.path.join(_LOCAL, "claude", "graphrag"))
DEFAULT_DB = os.path.join(GRAPHRAG_HOME, "index.sqlite")

# --------------------------------------------------------- EXTENSION CONTRACT
# ADDED 2026-08-24. This module is IMPORTED AND MONKEYPATCHED by at least two scripts in another
# trunk, deliberately and correctly -- rebinding is how a differently-laid-out tree reuses this
# indexer instead of forking it. `[measured, reported by Personal/Soul with file:line]`
#   Claude Personal scripts/build_trunk_index.py:493   build_index.REPO           = stage_dir
#   Claude Personal scripts/build_trunk_index.py:507   build_index.corpus_files   = lambda *a, **k
#   Claude Personal scripts/build_trunk_index.py:538   build_index.tier_of        = tier_of
#   Claude Personal scripts/build_personal_index.py:151 build_index.REPO          = root
#
# WHY THIS BLOCK EXISTS. On 2026-08-21 22:49 `corpus_files` gained parameters. Nothing warned: no
# import error, no type check, no test. The downstream rebind kept its old arity and every rebuild
# died at the call. The cost is not the crash -- it is what a crash at BUILD time looks like:
#   INDEXES SIMPLY STOP UPDATING WHILE EVERY QUERY KEEPS ANSWERING, CONFIDENTLY, FROM STALE DATA.
#   A frozen index does not look broken. It looks like a corpus that stopped changing.
# It bit twice. `tier_of` drifted to two arguments as well, found 2026-08-24 across five call sites.
#
# A MONKEYPATCH IS A COMPILE-TIME CONTRACT ENFORCED AT RUNTIME BY NOBODY (Soul's phrasing, and it
# is the whole diagnosis). Freezing this module would be the wrong direction -- the parameters are
# deliberate and it is not another trunk's call to pin them. So the seam is DECLARED instead: bump
# EXTENSION_CONTRACT whenever any name below changes shape, and a consumer that asserts against it
# gets a loud failure at import instead of a silent disagreement at build.
#
# BOUND: this cannot detect a consumer that never calls the assert. It converts an invisible break
# into a visible one FOR THOSE WHO OPT IN. That is the honest scope, and it is stated so nobody
# reads a green build here as evidence about anyone else's index.
EXTENSION_CONTRACT = 3          # bump on ANY signature change to the names below
EXTENSION_SIGNATURES = {
    "corpus_files": ("includes", "root", "provenance"),
    "tier_of": ("rel_path", "kind"),
    "REPO": "str -- absolute path to the trunk root",
    "DEFAULT_DB": "str -- absolute path to the sqlite index",
}


def assert_extension_contract(expected: int) -> None:
    """Raise unless this module still presents the contract the caller was written against.

    Call this BEFORE rebinding anything here. Deliberately raises rather than warns: a warning on
    an indexer is read by nobody, and the failure it replaces is a silently frozen index.
    """
    # SELF-CHECK FIRST, and it is the half that makes the rest mean anything. EXTENSION_SIGNATURES
    # is hand-typed, so it is a comparand living in prose: it can drift from the functions it
    # claims to describe, and then this whole block certifies a contract that does not exist.
    # Derived from the live objects at call time instead of trusted.
    import inspect as _inspect
    for _name in ("corpus_files", "tier_of"):
        _declared = EXTENSION_SIGNATURES[_name]
        _actual = tuple(_inspect.signature(globals()[_name]).parameters)
        if _declared != _actual:
            raise RuntimeError(
                "build_index EXTENSION_SIGNATURES is STALE for %s: declares %r, actually %r. "
                "The declaration drifted from the code, so EXTENSION_CONTRACT cannot be trusted "
                "either. Fix the declaration and bump EXTENSION_CONTRACT before relying on this."
                % (_name, _declared, _actual))
    if expected != EXTENSION_CONTRACT:
        raise RuntimeError(
            "build_index EXTENSION_CONTRACT is %d, caller expects %d. A name this caller "
            "monkeypatches has changed shape. Current signatures: %r. Do NOT pin this module -- "
            "update the rebind, then bump the caller's expected value."
            % (EXTENSION_CONTRACT, expected, EXTENSION_SIGNATURES))
LOCKDIR = os.path.join(GRAPHRAG_HOME, ".build.lock")

MAX_CHARS = 1400

# ---------------------------------------------------------------------------------------------
# PROVENANCE BODY-CHUNK POLICY (2026-09-07). A POLICY, NOT A BUG FIX -- and the distinction decides
# how it is tested.
# ---------------------------------------------------------------------------------------------
# The doc-level rule below was DELIBERATE and its comment says why: body-chunking every transcript
# "would add ~100k chunks to a 16k index." That reasoning was correct when raw logs were an ARCHIVE
# TO PRESERVE. It expired the day they became the corpus a fleet is asked to trace THROUGH -- the
# third instance in one day of a constant whose reasoning was sound and outlived its premise (the
# G: corpus root and the freshness TTL were the other two). None of the three was a mistake; none
# of them alarmed.
#
# ⛔ WHAT IT COST, measured by Professional N 1 compact 2 on 2026-09-07 and confirmed here by
# independent command: a 294,636 B transcript was ONE chunk of 2,320 indexed chars (0.79%); a
# 3.7 MB session log, 0.062%; every one of 6,197 provenance files single-chunk, against 0 of 3,489
# in knowledge. Tier-wide, 1.3969% of corpus bytes reachable. ⚠️ AND IT IS NOT A BLACKOUT: its
# capability probe found 1 PASS / 1 FAIL / 1 UNKNOWN over three sampled documents (n=3 -- enough to
# refute "blackout", NOT enough to state a rate). A high, silent, unpredictable failure rate is
# harder for a human to notice than a blackout, which announces itself on the first query.
#
# ⭐ THREE LEVERS, and the cost table is Professional's, measured over the real tier:
#   WINDOW alone is WEAK HERE -- 91% of provenance bytes are younger than 60 days, so "recent" is
#     nearly the whole corpus: <=14d is 1,533 files / 253 MB / ~181k chunks, more than DOUBLING a
#     116k index. Kept anyway at 14 days, because the recent window is the part that gets traced.
#   CONTENT is the lever that bites and the one that serves the actual question: tool traffic is
#     55.5% and 59.3% of the two transcripts measured. Jon does not want to locate a tool call; he
#     wants to locate the words he replied to. The bodies stay in the transcript ON DISK -- that is
#     the record -- they simply stop being embedded, which is retrieval.
#   ⛔ GRANULARITY: THIS LEVER WAS NEVER PULLED, AND THE CO-TRUNK MEASURED IT AFTER THE FACT.
#     `[measured 2026-09-07, 248,099 provenance chunks]` avg 500 chars, min 19, max 108,752 --
#     0-200: 21.9% · 200-500: 59.2% · 500-1000: 7.6% · 1000-2000: 6.3% · 2000-4100: 4.9%.
#     81.1% are under 500 characters and only 4.9% reach the neighbourhood of 4,000, because
#     chunk_markdown() SPLITS ON HEADINGS FIRST and a transcript carries `## Human` / `## Assistant`
#     / `## Tool Result` every turn. THE REAL GRANULARITY IS TURN-LEVEL AND MAX_CHARS ALMOST NEVER
#     APPLIES. So 1400 -> 4000 did approximately nothing: it is not wrong, it is INERT, and it must
#     not be credited with either the cost or the benefit of this policy.
#     ⚠️ IF YOU EVER NEED FEWER CHUNKS THE LEVER IS COALESCING ADJACENT TURN CHUNKS UP TO A BUDGET,
#     NOT RAISING MAX_CHARS -- raising it again will do nothing again, and it will look principled.
#     ⚠️ It also explains why our shared ~27k estimate was 9x low: wrong in its PREMISE, not its
#     arithmetic. Both seats assumed MAX_CHARS governed. Actual +241k.
#     (original note kept:) 1400 chars is tuned for curated wiki prose. A transcript needs to say "here", not
#     "this sentence". 4000 for this tier only.
# Combined: ~27k added chunks, +23%, without shrinking the window.
#
# ⚠️ THE LOSS THIS ACCEPTS, stated so it can be overturned: a question answerable ONLY by a tool
# body (a path written, a command run) may become unreachable while the conversation about it stays
# reachable. Accepted because the disk transcript still holds it and the queue-tier extract carries
# a tool-NAME ledger. Professional is grading BOTH sides of this boundary with an instrument I did
# not write; if a class of question turns out to need the bodies, this judgment is wrong.
# Bump when the chunking RULE changes: it is mixed into the stored per-file digest so a policy
# change invalidates the affected rows even though the bytes are identical.
PROVENANCE_POLICY_VERSION = "2026-09-07.body+salvage.v3-no-size-proxy"
PROVENANCE_BODY_CHUNK_DAYS = int(os.environ.get("CFL_BODY_CHUNK_DAYS", "14"))
PROVENANCE_MAX_CHARS = int(os.environ.get("CFL_PROVENANCE_MAX_CHARS", "4000"))
_DATE_IN_NAME = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")


def provenance_is_recent(rel_path: str, days: int = None) -> bool:
    """Date parsed from the converter's own filename convention `code-YYYY-MM-DD-<sid6>-<slug>.md`.
    ⛔ A file whose name carries NO date returns False -- doc-level, the cheaper side. An unparseable
    date is not an argument for spending; it is an UNKNOWN, and UNKNOWN takes the conservative
    branch rather than the generous one."""
    if days is None:
        days = PROVENANCE_BODY_CHUNK_DAYS
    m = _DATE_IN_NAME.search(os.path.basename(rel_path))
    if not m:
        return False
    try:
        when = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return False
    return (datetime.date.today() - when).days <= days


# ⛔ THE TERMINATOR IS THE TRANSCRIPT'S OWN TURN HEADINGS, NOT "any heading". This read
# `(?=^##+ |\Z)` and stopped at the FIRST `## ` after the marker -- but a tool result routinely
# CONTAINS markdown with its own headings (a skill file, a letter, a rendered document), so the
# terminator fired INSIDE the payload and left the remainder in the index. That was the whole of the
# 4.6-9.6 point "residual" I was about to call a fourth pattern: a span-boundary difference between
# two implementations of the SAME rule, diagnosed by Professional N 1 compact 2 -- which measured
# patterns 1+2 independently and got 62.4% / 60.2% / 70.8% against its own tool-traffic figures of
# 62.5% / 60.2% / 70.9%, with every tool marker at ZERO in the survivor.
# ⭐ THE LESSON IS ABOUT RESIDUALS, NOT REGEXES: a stable, consistent gap between two measurements of
# the same thing is EVIDENCE OF AN IMPLEMENTATION DIFFERENCE, and the cheap move is to diff the two
# implementations. Adding a rule to close it would have papered over the bug with a second bug.
# ⚠️ AND THE WIDER TERMINATOR WAS TRIED AND REVERTED, SAME HOUR, BY THE RULE ABOVE. Anchoring to
# turn headings only (`## Human|Assistant|Tool Result|...`) raised the drop rate to 82.0% on a86404
# against a measured 60.2% of tool traffic -- +21.8 points, because a tool result that CONTAINS a
# whole document (a skill file, a letter) has no turn heading inside it, so the wider span swallowed
# the prose that followed as well. ⛔ Over-dropping destroys conversation that then exists at NO
# rank; under-dropping leaves a residual you can measure. The tie goes to the conversation, so the
# NARROW terminator stands and the residual stays stated.
# ⭐ THE HONEST WAY TO SETTLE IT IS A SPAN DIFF, NOT A THIRD REGEX: dump the removed-span offsets
# from both implementations for ONE file and compare them. Both "residuals" so far were span-boundary
# differences between two implementations of the same two rules, and the co-trunk's own tool-traffic
# figure is computed with a terminator of its own -- so the two numbers were never measuring the same
# spans. Neither of us should tune until the offsets are on one screen.
_TOOL_SECTION = re.compile(r"^##+ Tool Result\b.*?(?=^##+ |\Z)", re.M | re.S)
_BIG_FENCE = re.compile(r"^```.*?^```", re.M | re.S)
# ⛔ THE THIRD PATTERN, AND ITS ABSENCE WAS THE 27.7%-vs-55.5% GAP. Professional N 1 compact 2 found
# the shape by measuring instead of guessing at a threshold: a `[tool_use: X]` marker and its fence
# live under `## Assistant`, NOT under `## Tool Result`, so the section rule never sees them -- and
# `[measured, a86404]` 192 of 198 fences are UNDER the 1500-char size rule, so the size rule catches
# almost none of them either. 94 blocks, 98,110 chars, 33.2% of the file, entirely untouched.
# ⚠️ MY TWO PATTERNS WERE A SECTION-NAME RULE AND A SIZE RULE, and the tool_use payload is neither
# in that section nor over that size. Raising the fence threshold would have caught the 6 big ones
# and still missed 88 small ones -- a tuning that improves the number without fixing the class.
# ⭐ Professional also corrected ITSELF here, against its own earlier figure: its 34.7% came from a
# loose span running to the next `---`; measured precisely it is 33.2%, so total tool traffic is
# 60.2% and the gap was WIDER than either of us had said, not narrower.
_TOOL_USE = re.compile(r"^\[tool_use:[^\]]*\]\s*\n+```.*?^```", re.M | re.S)


_ID_PATTERNS = (
    re.compile(r"\b[A-Za-z]:[\\/][^\s\"'`|,;)]{3,}"),                      # absolute Windows path
    re.compile(r"\b(?:wiki|scripts|exchange|raw|skills|docs)/[^\s\"'`|,;)]{3,}"),  # repo-relative
    re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"),  # session uuid
    re.compile(r"\b[0-9a-f]{7,40}\b"),                                     # git sha / hash
    re.compile(r"\bexit(?:ed with)? (?:code )?[=:]? ?-?\d{1,3}\b"),        # exit codes
)


def salvage_identifiers(payload: str, cap: int = 1200) -> str:
    """The concrete HANDLES in a tool payload, deduped and order-preserved. Nothing else."""
    seen, out = set(), []
    for pat in _ID_PATTERNS:
        for m in pat.finditer(payload):
            tok = m.group(0).rstrip(".,:;)")
            if len(tok) < 5 or tok in seen:
                continue
            seen.add(tok)
            out.append(tok)
            if sum(len(t) + 1 for t in out) > cap:
                return "artifacts: " + " ".join(out)
    return ("artifacts: " + " ".join(out)) if out else ""


def strip_tool_payloads(text: str, fence_limit: int = 1500) -> str:
    """Drop `## Tool Result` sections and oversize fenced blocks, keeping the conversation AND the
    identifiers the dropped payloads contained.

    ⛔ THE SALVAGE LINE EXISTS BECAUSE PROFESSIONAL N 1 COMPACT 2 BROKE THE FIRST VERSION ON A CLASS
    I HAD NOT CONSIDERED, when I asked it to try. I defended the loss of tool NARRATIVE and was
    right -- prose carries the reasoning, the verdicts and Jon's turns, and it could not construct a
    session whose ARGUMENT became unreachable. ⚠️ But the loss is IDENTIFIERS, not narrative.
    `[measured, n=2 transcripts]` of the concrete handles in a session, the share appearing ONLY in
    tool bodies: absolute paths 96.4% / 64.9%; session UUIDs 50.0% / 73.5%; git shas 41.2% / 42.8%;
    repo-relative paths 38.3% / 52.5%.
    ⛔ THREE CONSEQUENCES THAT HIT THIS PROGRAM'S OWN PLAN, not a hypothetical: "what did the seat do
    between its last commit and its stop" is answered by paths and shas; this fleet resumes an elder
    by FULL session uuid and three-quarters of those live only in tool output; and the very review
    that found this defect could not have been written under the naive policy, because every path
    and sha in it came out of tool output.
    ✅ So the payload is not chunked -- its HANDLES are, appended to the adjacent turn. Measured cost
    51,477 chars against 2,234,007 tool bytes = 2.30%: 97.7% of the traffic dropped, the handles
    kept. Same shape as the queue-tier extract's tool-NAME ledger, one level more specific, and it
    is what makes a ledger RETRIEVABLE rather than merely present.
    ⚠️ Professional also WITHDREW its own earlier reassurance here rather than averaging it: it had
    said numbers get restated in prose on the strength of 19.3% at n=1, and at n=2 it is 40.8%. The
    divergence is the finding, so no reassurance is carried.

    ⚠️ LINE SPANS SURVIVE: a removed region becomes the salvage line plus enough blank lines to keep
    the file's line count identical. A chunk that cannot name `file:line` is not usable here, and
    half this month's defects were citations nobody could re-derive. A SHORT fence (a quoted
    command, a path) is prose and is kept; `fence_limit` separates a payload from a quotation and is
    a tunable guess, not a measurement."""
    def replace(m):
        blob = m.group(0)
        nl = blob.count("\n")
        line = salvage_identifiers(blob)
        if not line or nl == 0:
            return "\n" * nl
        return line + "\n" * nl

    text = _TOOL_SECTION.sub(replace, text)
    text = _TOOL_USE.sub(replace, text)
    # ⛔ THE SIZE RULE IS OFF BY DEFAULT AS OF v3, AND THE MEASUREMENT REVERSED ITS SIGN.
    # It was a PROXY for "this fence is a tool payload", written before pattern 2 existed. With
    # pattern 2 naming tool_use payloads exactly, the proxy now mostly catches LARGE PROSE FENCES --
    # quoted letters, skill text, pasted documents -- i.e. the conversation this policy exists to
    # preserve. `[measured 2026-09-07, n=5 transcripts, drop rate vs the co-trunk's independently
    # measured tool traffic]`
    #     WITH the size rule:    +15.8, +0.9, +8.6, +0.8, -2.1  (over-drops the two biggest files)
    #     WITHOUT it:             -7.3, -4.6, -5.3, -6.6, -9.6  (consistent, and consistently under)
    # ⭐ THE ASYMMETRY DECIDES IT: over-dropping destroys prose that no longer exists in the index at
    # any rank; under-dropping costs index size and leaves a residual to characterize. Those are not
    # comparable harms, so the tie goes to the conversation. `CFL_FENCE_SIZE_RULE=1` restores it.
    # ✅ RESIDUAL CLOSED 2026-09-07, AND IT WAS NEVER TOOL TRAFFIC. Decomposed per file:
    #        removed spans   salvage kept   NET drop   co-trunk's measured tool traffic
    #  462760    63.1%           7.9%         55.2%              62.5%
    #  a86404    60.9%          10.3%         50.6%              60.2%
    #  ce39e6    70.4%           4.1%         66.3%              70.9%
    #  52f217    62.3%           4.8%         57.5%              62.8%
    #  77042e    61.0%           5.7%         55.3%              61.9%
    # ⭐ REMOVED-SPAN % MATCHES INDEPENDENTLY MEASURED TOOL TRAFFIC TO WITHIN 0.6 POINTS ON ALL FIVE.
    # The "4.6-9.6 point residual" was the SALVAGE LINES -- text this function deliberately keeps.
    # Two seats compared REMOVED SPANS against NET OUTPUT, which are different quantities, and both
    # of us reached for a new rule to explain the difference. ⛔ Neither a fourth pattern nor a span
    # bug: a units error, and the fix was a decomposition rather than a regex.
    # (superseded note kept for the reasoning it records)
    # ⚠️ RESIDUAL, STATED NOT TUNED: 4.6-9.6 points of tool traffic survive patterns 1-2. That tail
    # is a FOURTH PATTERN nobody has characterized yet, not a rounding error, and it is the co-trunk's
    # to find -- I would otherwise tune a threshold until my number agreed with its number, which is
    # exactly how the size rule got here.
    if os.environ.get("CFL_FENCE_SIZE_RULE") == "1":
        text = _BIG_FENCE.sub(
            lambda m: replace(m) if len(m.group(0)) > fence_limit else m.group(0), text)
    return text
OVERLAP = 160
# Below this, a "chunk" is a heading with a stub under it -- it embeds to noise and pollutes recall.
MIN_CHUNK_CHARS = 20

SKIP_DIRS = {".git", ".understand-anything", ".graphrag", "node_modules", "__pycache__",
             # ".claude" excludes .claude/worktrees/** wherever a walk starts at a trunk root.
             # Soul measured 2026-08-18: a frozen 08-11 worktree shadow of Personal holds 748 .md
             # files, 597 of them DIVERGED stale copies of still-live pages -- an index that eats
             # them serves last week's status with nothing in the text to mark it. Exclude from
             # ingest; the directory itself stays on disk (no deletion).
             ".claude"}

WIKILINK = re.compile(r"\[\[([^\]|#]+)")
MDLINK = re.compile(r"\[[^\]]*\]\(([^)\s]+\.md)[^)]*\)")
TOKEN = re.compile(r"[a-z0-9]{2,}")

# PATHREF (2026-08-31, Herald's patch, applied additively): this program cites by backticked path
# (`path/to/file.md`) far more often than by [[wikilink]] or [](mdlink). A third edge kind
# "pathref" rides the SAME edges(src,dst,kind,raw) rails and the SAME basename stem-resolution
# pass. WIKILINK/MDLINK behavior is untouched. Disable for A/B with env GRAPHRAG_PATHREF=0.
PATHREF = re.compile(r"`([^`\n]{1,200}?\.md)`")
PATHREF_ENABLED = os.environ.get("GRAPHRAG_PATHREF", "1") != "0"


def extract_pathrefs(text: str):
    out = set()
    for m in PATHREF.finditer(text or ""):
        raw = m.group(1).strip().replace(chr(92), "/")
        if not raw or raw.endswith("/"):
            continue
        if raw.startswith("[[") or "](" in raw:
            continue
        out.add(("pathref", raw))
    return sorted(out)


# ---------------------------------------------------------------- lock


class BuildLock:
    """Atomic-mkdir single-instance lock that fails CLOSED and reclaims dead holders.

    ⚠️ The reclaim path is the one that matters and the one nobody tests: a crashed build leaves
    the directory behind, and a lock that cannot be reclaimed converts one crash into a permanently
    unbuildable index. Both paths are exercised by --selftest.
    """

    def __init__(self, path: str = LOCKDIR):
        self.path = path
        self.held = False

    @staticmethod
    def _alive(pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            import ctypes

            handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

    def acquire(self, force: bool = False):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        pidfile = os.path.join(self.path, "pid")
        try:
            os.mkdir(self.path)
        except FileExistsError:
            holder = -1
            try:
                holder = int(open(pidfile, encoding="utf-8").read().strip().split()[0])
            except Exception:
                pass
            if self._alive(holder) and not force:
                return False, holder
            # Stale (or forced): reclaim in place. Never delete anything but our own lock.
            try:
                os.remove(pidfile)
            except OSError:
                pass
        with open(pidfile, "w", encoding="utf-8") as fh:
            fh.write(f"{os.getpid()} {time.time():.0f}\n")
        self.held = True
        return True, os.getpid()

    def release(self):
        if not self.held:
            return
        try:
            os.remove(os.path.join(self.path, "pid"))
        except OSError:
            pass
        try:
            os.rmdir(self.path)
        except OSError:
            pass
        self.held = False


# ---------------------------------------------------------------- corpus


# Extensions eaten when an --include names a DIRECTORY. A file named explicitly is taken as-is.
# .py/.sh are in because the chunker was TESTED on them first (2026-08-21): `^#{1,6}\s` treats
# top-level comment lines as headings, which yields accurate line spans and usable chunks --
# with two stated bounds: heading paths for code are comment fragments, and a blank-line-poor
# block stays one oversize chunk (MAX_CHARS splits on blank lines only).
INCLUDE_EXTS = (".md", ".py", ".sh", ".txt")

# V-1 (2026-08-21): the DEFAULT corpus now carries the repo's own documentation, so the tool can
# retrieve itself. Walked in addition to wiki/ + both constitutions:
#   scripts/ -- .md plus .py/.sh, because a script's documentation IS its header comment
#   docs/, skills/ -- .md only (SKILL.md bodies included)
#   root-level *.md (README.md, HANDOFF-*, ...)
# NEVER walked by default: raw/**, exchange/** (incl. su-close) EXCEPT the single file
# exchange/CARRIER.md (added 2026-08-29, CARRIER census — see collect()), any *.jsonl -- and the excluded
# trunks wiki/personal, wiki/home, wiki/pro (V-1 ruling; canonical excludes them for the same
# reason). SKIP_DIRS (.claude included) and _superseded apply everywhere.
# skills/ widened to executables 2026-09-01 on Professional's fleet finding (17 of 981
# executables indexed fleet-wide; "the cure and the defect never met" — packaged skills
# whose script bodies the index cannot see). Same rationale as scripts/: a script's
# documentation IS its header comment. The .md-only prior scope was an omission, not a ruling.
SELFDOC_DIRS = {"scripts": (".md", ".py", ".sh"), "docs": (".md",), "skills": (".md", ".py", ".sh")}
EXCLUDED_WIKI_TRUNKS = {"personal", "home", "pro"}

# ---------------------------------------------------------------- provenance
# V-2 (2026-08-23, SEC-113). Jon: "ensure vector embed graph rag with haiku support tracks all the
# way to the actual conversationSSSSS i've had with herald on this". It did not, and CANNOT have:
# the comment above says raw/** is NEVER walked, so a photos query returned
# wiki/sources/session-stubs.md -- a TABLE ROW saying photo sessions exist. A stub about a
# conversation is not a conversation.
#
# THE BOUND THAT SHAPES THIS, and it is not optional: folding raw/ into the DEFAULT corpus would
# repeat, at four times the scale, the exact defect tier_of() was written to fix. So the record is
# reachable, not resident: a THIRD TIER, off by default, one flag away.
#
# TWO DELIBERATE NARROWINGS, each measured:
#   1. ONLY raw/transcripts/**. raw/ holds 6,079 .md; raw/transcripts/ holds 4,376. The rest is
#      _backup-sessions-2026-07-24/, _reparse-2026-07-24/{old,new}/ and _quarantine/. Those are
#      SUPERSEDED PARSE TREES, not extra conversations -- every photo primary named in the SEC-113
#      brief has a live counterpart under raw/transcripts/ (verified file-by-file 2026-08-23).
#      Indexing all four trees puts three near-copies of one conversation in a top-5 and buries the
#      other conversations Jon capitalised the plural to ask for. Nothing is deleted; the backup
#      trees stay on disk and stay greppable. They are simply not the copy retrieval points at.
#   2. ONE CHUNK PER FILE, no body chunks. A transcript is 20 KB-180 KB; body-chunking 4,376 of
#      them would add ~100k chunks to a 16k index and drown it even inside its own tier. The
#      deliverable is a PATH TO A PRIMARY A READER CAN OPEN, not full-text answers over the corpus.
# STATED BOUND, so nobody reads more into this than it does: BM25 and dense both see only the
#      summary string, so a phrase buried mid-transcript is NOT retrievable by this tier. It gets
#      you to the file. grep gets you to the line.
#
# ⛔ THE PRIVACY BOUNDARY, STATED RATHER THAN ASSUMED, because this tier eats the personal corpus.
# raw/transcripts/ is Jon's FULL history -- personal, home, faith included. Three facts make that
# in-bounds, and all three must hold or this tier does not:
#   1. `raw/` is GITIGNORED. Nothing here is pushed anywhere. The no-PII-to-GitHub constraint is
#      untouched: this walk creates no commit, no push, no PR body, no issue comment.
#   2. THE INDEX LIVES OFF DRIVE ON C: (GRAPHRAG_HOME, %LOCALAPPDATA%) -- inside the trust zone
#      Jon named 2026-08-19: "Just working on my C on my G and D and on my personal private
#      githubs." It is never synced, never published, never reaches the canonical branch.
#   3. THE TIER IS OFF BY DEFAULT. An ordinary knowledge query cannot surface a family transcript;
#      it takes an explicit --tier provenance to reach one.
# ⚠️ AND THE RULING THAT CUTS THE OTHER WAY, which is the half that gets dropped: Jon, 2026-08-11 --
# "please don't make key PII info harder to use it's often relevent ... It's fine in any file the
# resident can read." OVER-SCRUBBING IS A VIOLATION, NOT A SAFE DEFAULT. Excluding the personal
# corpus from a local-only index would break a standing instruction just as surely as a leak would,
# and only one of those two failures has an alarm. So: indexed, local, off by default.
PROVENANCE_DIRS = ("raw/transcripts",)


_LAST_WALK_NOTES = []


def walk_notes():
    """What the last corpus_files() walk SKIPPED, so a caller can PRINT it.

    A list collected and never printed is the same silence the two 2026-09-13 findings were made of:
    one file silently INCLUDED from outside the root, and spec-named files silently EXCLUDED under a
    pruned directory. Module-level rather than a second return value, because corpus_files() returns
    a file list by contract and another trunk monkeypatches around it -- changing that signature is
    the kind of quiet break this whole fix is about."""
    return list(_LAST_WALK_NOTES)


def corpus_files(includes=None, root=None, provenance=None):
    """(abs_path, label, kind) for everything indexed: wiki + constitutions + self-documentation.

    `root` (--root) points the whole walk at another trunk; default is this repo. Threaded as an
    argument -- not the module global -- per Personal's 2026-08-19 letter: a private name another
    trunk must monkey-patch is a contract nobody signed.
    `includes` (repeatable --include) WIDENS the walk with extra directories/files, relative to
    the root unless absolute. Included dirs respect SKIP_DIRS plus `_superseded`.
    """
    root = os.path.normpath(root) if root else REPO
    # Collected here, PRINTED by the caller. Both lists exist because 2026-09-13 produced one of
    # each: a file silently INCLUDED from outside the root, and files silently EXCLUDED though named
    # in an include spec. Silence in either direction is the defect; presence or absence is not.
    _OUT_OF_ROOT_SKIPS = []
    _SKIPDIR_HIDDEN = []
    out, seen = [], set()

    def add(full, rel, kind):
        if rel not in seen:
            seen.add(rel)
            out.append((full, rel, kind))

    wiki = os.path.join(root, "wiki")
    for dirpath, dirnames, filenames in os.walk(wiki):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        if os.path.normpath(dirpath) == os.path.normpath(wiki):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDED_WIKI_TRUNKS]
        for name in sorted(filenames):
            if not name.endswith(".md"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            section = rel.split("/")[1] if rel.count("/") >= 2 else "(root)"
            add(full, rel, f"wiki:{section}")
    proj = os.path.join(root, "CLAUDE.md")
    if os.path.isfile(proj):
        add(proj, "CLAUDE.md", "constitution:cfl-project")
    # DEFECT, raised by Professional 2026-09-13 00:5x while building the PR-4 union graph, and it is
    # a SCOPE violation rather than a wrong file: this add was UNCONDITIONAL, so every `--root` build
    # inserted `~/.claude/CLAUDE.md` -- a file OUTSIDE the root -- into a graph declared over that
    # root. Their first run over N:/claude-pr4 indexed exactly ONE file: this one.
    # A graph holding a file its root does not is not a smaller problem than a missing file. For a
    # PUBLISHED artifact it is worse: the machine-global constitution would ship inside the index of a
    # tree that does not carry it, with nothing in the output saying so.
    # The intent stands -- a session pays a constant constitution tax and the graph should answer about
    # it -- so the add is KEPT for a build over THIS repo and SKIPPED AUDIBLY everywhere else.
    glob = os.path.expanduser("~/.claude/CLAUDE.md")
    if os.path.isfile(glob):
        if os.path.normpath(root) == os.path.normpath(REPO):
            add(glob, "~/.claude/CLAUDE.md", "constitution:global")
        else:
            _OUT_OF_ROOT_SKIPS.append("~/.claude/CLAUDE.md (machine-global constitution, outside "
                                      "--root %s)" % root)
    # CARRIER-census fix (2026-08-29, docket row 5): exchange/** stays never-walked (live mailbox),
    # but exchange/CARRIER.md SPECIFICALLY is read at every session open and held 14 CARRIER-only
    # facts invisible to retrieval — the exact gap Jon named ("What is missing from your BRAN
    # because its just in your CARRIER?"). One file, knowledge tier; the exclusion of the rest of
    # exchange/ is untouched.
    carrier = os.path.join(root, "exchange", "CARRIER.md")
    if os.path.isfile(carrier):
        add(carrier, "exchange/CARRIER.md", "selfdoc:carrier")

    # Self-documentation: root-level *.md, then scripts/docs/skills per SELFDOC_DIRS above.
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if name.endswith(".md") and os.path.isfile(full):
            add(full, name, "selfdoc:(root)")
    for top in sorted(SELFDOC_DIRS):
        exts = SELFDOC_DIRS[top]
        base = os.path.join(root, top)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            # __pycache__ and _superseded are prunes nobody names in a spec; announcing them buries
            # the one that matters. [2026-09-13: the first version of this notice printed six
            # __pycache__ directories and `.claude` -- the case it exists for -- never appeared.]
            for _d in [d for d in dirnames
                       if (d in SKIP_DIRS or d == "_superseded")
                       and d not in ("__pycache__", "_superseded", ".git")]:
                _SKIPDIR_HIDDEN.append(os.path.relpath(os.path.join(dirpath, _d), root)
                                       .replace(os.sep, "/"))
            dirnames[:] = sorted(d for d in dirnames
                                 if d not in SKIP_DIRS and d != "_superseded")
            for name in sorted(filenames):
                if not name.endswith(exts) or name.endswith(".jsonl"):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                add(full, rel, f"selfdoc:{top}")

    # Provenance tier: the actual conversations. Walked into the index, filtered OUT of the
    # default retrieval scope by tier_of() + Index.tiers -- see the PROVENANCE_DIRS note above.
    # `--provenance PATH` (repeatable) WIDENS the provenance walk to another trunk's records --
    # Herald Wiki's photo deliverables, Claude Personal's rulings. Read-only, like every walk here.
    for pdir in list(PROVENANCE_DIRS) + sorted(provenance or []):
        base = pdir if os.path.isabs(pdir) else os.path.join(root, *pdir.split("/"))
        base = os.path.normpath(base)
        if not os.path.isdir(base):
            if pdir not in PROVENANCE_DIRS:
                print(f"WARN --provenance path not found, skipped: {pdir}", file=sys.stderr)
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames
                                 if d not in SKIP_DIRS and d != "_superseded")
            for name in sorted(filenames):
                if not name.endswith(".md"):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                if rel.startswith(".."):
                    # Out-of-root (another trunk): label by absolute path so two trunks' files
                    # can never collide on one `path` key, and kind carries the trunk name.
                    rel = full.replace(os.sep, "/")
                    venue = os.path.basename(os.path.normpath(base)) or "foreign"
                else:
                    parts = rel.split("/")
                    venue = parts[2] if len(parts) > 3 else "(root)"
                add(full, rel, "provenance:" + venue)

    def label_of(full):
        rel = os.path.relpath(full, root).replace(os.sep, "/")
        return full.replace(os.sep, "/") if rel.startswith("..") else rel

    for inc in sorted(includes or []):
        path = inc if os.path.isabs(inc) else os.path.join(root, inc)
        path = os.path.normpath(path)
        if os.path.isfile(path):
            rel = label_of(path)
            top = rel.split("/")[0] if "/" in rel else "(root)"
            add(path, rel, f"include:{top}")
        elif os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                # SECOND CODE PATH, found by Professional 2026-09-13 02:0x: the prune notice was
                # wired into the SELFDOC walk only, and `--include <half>` walks HERE. Their sixth
                # and seventh builds printed the out-of-root line and NOT the pruned-directory line,
                # though both halves have .claude/ directories this loop skips.
                # ⭐ THIRD TIME TONIGHT: one fix, two code paths, and I verified the path I had
                # patched. Exactly the HELD matcher shape six hours earlier. The lesson is not "look
                # harder" -- it is that a fix to a shared rule must be located by grepping the RULE
                # (SKIP_DIRS) across the file, never by editing the site that reported the bug.
                for _d in [d for d in dirnames
                           if (d in SKIP_DIRS or d == "_superseded")
                           and d not in ("__pycache__", "_superseded", ".git")]:
                    _SKIPDIR_HIDDEN.append(os.path.relpath(os.path.join(dirpath, _d), root)
                                           .replace(os.sep, "/"))
                dirnames[:] = [d for d in dirnames
                               if d not in SKIP_DIRS and d != "_superseded"]
                for name in sorted(filenames):
                    if not name.endswith(INCLUDE_EXTS):
                        continue
                    full = os.path.join(dirpath, name)
                    rel = label_of(full)
                    top = rel.split("/")[0] if "/" in rel else "(root)"
                    add(full, rel, f"include:{top}")
        else:
            print(f"WARN --include path not found, skipped: {inc}", file=sys.stderr)
    # Publish what this walk SKIPPED. A list collected and never printed is the same silence the
    # two 2026-09-13 findings were made of -- one file silently included from outside the root, and
    # spec-named files silently excluded under a pruned dir.
    _LAST_WALK_NOTES[:] = (["OUT-OF-ROOT SKIPPED: " + x for x in _OUT_OF_ROOT_SKIPS]
                           + (["SKIP_DIRS pruned under an --include (named in a spec but NOT walked): "
                               + ", ".join(sorted(set(_SKIPDIR_HIDDEN))[:6])]
                              if _SKIPDIR_HIDDEN else []))
    return out


def corpus_fingerprint(includes=None, root=None, provenance=None) -> str:
    """Cheap (path, size, mtime) digest of the whole corpus, for staleness detection.

    ⛔ A STALE INDEX MUST ANNOUNCE ITSELF. This program has already published one number computed
    from state that had moved underneath it, and a retrieval index is the same hazard with a
    friendlier face: it answers confidently from a wiki that no longer says that. Full sha256 over
    15 MB is too slow to run on every query; stat metadata is ~819 syscalls and catches every edit
    that matters. ⚠️ It will MISS an edit that preserves size and mtime -- stated, not hidden.
    """
    digest = hashlib.sha256()
    for full, rel, _kind in corpus_files(includes, root, provenance):
        try:
            st = os.stat(full)
            digest.update(f"{rel}|{st.st_size}|{int(st.st_mtime)}\n".encode("utf-8"))
        except OSError:
            digest.update(f"{rel}|MISSING\n".encode("utf-8"))
    return digest.hexdigest()


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def chunk_markdown(text: str, max_chars: int = None):
    """Heading-aware chunks carrying (heading_path, start_line, end_line, body).

    Sections longer than `max_chars` (default MAX_CHARS) split on blank lines with OVERLAP carried
    forward, so a claim straddling a split still appears whole in one of the two chunks.

    ⚠️ `max_chars` is a PARAMETER as of 2026-09-07 because 1400 is tuned for curated wiki prose and
    a transcript does not need 1.4 KB resolution to point at a place -- see PROVENANCE_MAX_CHARS.
    """
    if max_chars is None:
        max_chars = MAX_CHARS
    lines = text.splitlines()
    sections, stack, cur, cur_start = [], [], [], 1
    for i, line in enumerate(lines, start=1):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if cur:
                sections.append((" > ".join(stack), cur_start, i - 1, "\n".join(cur)))
            level = len(m.group(1))
            stack = stack[: level - 1] + [m.group(2).strip()]
            cur, cur_start = [], i
        else:
            cur.append(line)
    if cur:
        sections.append((" > ".join(stack), cur_start, len(lines), "\n".join(cur)))

    out = []
    for heading, start, end, body in sections:
        body = body.strip("\n")
        if not body.strip():
            continue
        if len(body) <= max_chars:
            out.append((heading, start, end, body))
            continue
        paras, buf, buf_lines, line_no = [], [], 0, start
        for para in body.split("\n\n"):
            if buf and sum(len(p) for p in buf) + len(para) > max_chars:
                paras.append(("\n\n".join(buf), line_no, line_no + buf_lines))
                tail = buf[-1][-OVERLAP:] if buf else ""
                line_no += buf_lines
                buf, buf_lines = ([tail] if tail.strip() else []), 0
            buf.append(para)
            buf_lines += para.count("\n") + 2
        if buf:
            paras.append(("\n\n".join(buf), line_no, min(end, line_no + buf_lines)))
        for piece, pstart, pend in paras:
            if piece.strip():
                out.append((heading, pstart, min(pend, end), piece))
    return [c for c in out if len(c[3].strip()) >= MIN_CHUNK_CHARS]


def extract_links(text: str):
    out = set()
    for m in WIKILINK.finditer(text):
        out.add(("wikilink", m.group(1).strip()))
    for m in MDLINK.finditer(text):
        out.add(("mdlink", m.group(1).strip()))
    out.update(extract_supersedes(text))
    if PATHREF_ENABLED:
        out.update(extract_pathrefs(text))
    return sorted(out)


# L3 -- STRUCTURAL SUPERSESSION (P2-3, 2026-08-23).
#
# Until now supersession was ONLY the L2 marker boost in retrieve.py: a 1.6x multiplier on any
# chunk whose TEXT contains "AMENDED BY JON" / "supersedes" / "STRUCK" / "the later ruling governs".
# That is content matching, and it has two failure modes a declared relation does not have:
#   1. It fires on a page that merely DISCUSSES supersession (this file would trip it).
#   2. It cannot fire at all on a superseded page that does not describe itself as superseded --
#      which is the normal case, because pages rarely announce their own obsolescence.
# It also won P16 by a measured ~1.2% margin (0.02434 vs 0.02406). A coin landing the right way.
#
# So: a file's frontmatter may DECLARE what it supersedes, and that declaration becomes a typed
# edge on the existing edges(src, dst, kind, raw) rails, resolved by the same stem pass as
# wikilinks. Semantics: `supersedes: X` in file A means A SUPERSEDES X, so the edge is src=A,
# dst=X, and the DESTINATION is the superseded party (demoted in retrieve.py's L3).
#
# ⛔ HONEST BOUND, stated where the code is so nobody oversells it later: these are FILE->FILE
# edges. They CANNOT order two chunks of the SAME file, which is exactly what probes P4/P16 need
# (CLAUDE.md:248-261 vs CLAUDE.md:266-287). Intra-file supersession needs chunk granularity and is
# NOT solved here. This mechanism fixes the cross-file class and fixes it going forward.
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
SUPERSEDES_KEY = re.compile(
    r"^(supersedes|supersedes_in_practice)\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
# A declaration of "none" is an author saying "I checked and there is nothing" -- that is a real
# and useful statement, but it is not an edge. Do not resolve it into a stem lookup for a file
# literally named "none".
SUPERSEDES_NULL = re.compile(r"^(none|n/?a|nothing|-|\[\]|~|null)\b", re.IGNORECASE)


def extract_supersedes(text: str):
    """Yield ("supersedes", target) for each frontmatter supersedes declaration.

    Tolerates three YAML shapes seen in this corpus: a bare scalar, a quoted scalar, and an
    inline list. A block list (subsequent `- item` lines) is also read. Anything that resolves to
    a null-ish declaration is dropped rather than turned into a bogus edge.
    """
    m = FRONTMATTER.match(text or "")
    if not m:
        return []
    block = m.group(1)
    out = set()
    for km in SUPERSEDES_KEY.finditer(block):
        raw = km.group(2).strip()
        # Strip a trailing comment only when it is clearly one (" # ..."), never a bare '#'
        # inside a path.
        raw = re.sub(r"\s+#\s.*$", "", raw).strip()
        if not raw or SUPERSEDES_NULL.match(raw):
            continue
        # A [[wikilink]] also starts '[' and ends ']', so it MUST be tested before the inline-list
        # branch or it is split into "[record-architecture-v1]" and never resolves. Caught by the
        # parser unit test before this ever reached an index.
        if raw.startswith("[[") and raw.endswith("]]"):
            items = [raw]
        elif raw.startswith("[") and raw.endswith("]"):
            items = [p.strip() for p in raw[1:-1].split(",")]
        else:
            items = [raw]
        # A block list: the key's value is empty and the following lines are "- item".
        if raw in ("|", ">"):
            continue
        for item in items:
            item = item.strip().strip("'\"").strip()
            # Frontmatter often carries prose after the path ("wiki/x.md (~58 rows, last ...)").
            # Take the first whitespace-delimited token that looks like a path or a wikilink.
            wl = re.match(r"\[\[([^\]]+)\]\]", item)
            if wl:
                item = wl.group(1).strip()
            else:
                item = item.split()[0] if item.split() else ""
            if not item or SUPERSEDES_NULL.match(item):
                continue
            # ⛔ MEASURED 2026-08-23, and this guard is the whole difference between a signal and
            # a hazard. A first pass over the corpus produced 30 "edges", of which ~17 were prose:
            # `supersedes: the coordination charter's clause 3` yielded the target "the";
            # others yielded "any", "two", "CFL", "T4", "374127". Taking the first token of an
            # English sentence and handing it to a basename-stem lookup is how an unrelated file
            # gets silently DEMOTED by collision -- a ranking change nobody could trace.
            # So: a supersedes target must LOOK like a file reference. It must end in .md, or
            # contain a path separator, or have arrived as a [[wikilink]] (already unwrapped
            # above, hence the wl flag). Prose is dropped, and dropping it is correct: a
            # declaration too vague to resolve is not an edge, it is a note.
            looks_like_ref = bool(wl) or item.lower().endswith(".md") or "/" in item or "\\" in item
            if not looks_like_ref:
                continue
            out.add(("supersedes", item.rstrip(",;")))
    return sorted(out)


def trigrams(term: str):
    padded = f"  {term} "
    return {padded[i : i + 3] for i in range(len(padded) - 2)}


# ---------------------------------------------------------------- schema

SCHEMA_VERSION = "v1"

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS files (
  id INTEGER PRIMARY KEY, path TEXT UNIQUE, sha TEXT, bytes INTEGER, kind TEXT, tier TEXT);
CREATE TABLE IF NOT EXISTS docvecs (file_id INTEGER PRIMARY KEY, vec BLOB);
CREATE TABLE IF NOT EXISTS chunks (
  id INTEGER PRIMARY KEY, file_id INTEGER, ord INTEGER, heading TEXT,
  start_line INTEGER, end_line INTEGER, ntok INTEGER, text TEXT);
CREATE TABLE IF NOT EXISTS vectors (chunk_id INTEGER PRIMARY KEY, vec BLOB);
CREATE TABLE IF NOT EXISTS postings (term TEXT, chunk_id INTEGER, tf INTEGER);
CREATE TABLE IF NOT EXISTS terms (term TEXT PRIMARY KEY, df INTEGER);
CREATE TABLE IF NOT EXISTS vocab_tri (tri TEXT, term TEXT);
CREATE TABLE IF NOT EXISTS edges (src INTEGER, dst INTEGER, kind TEXT, raw TEXT);
CREATE INDEX IF NOT EXISTS ix_chunks_file ON chunks(file_id);
CREATE INDEX IF NOT EXISTS ix_post_term ON postings(term);
CREATE INDEX IF NOT EXISTS ix_post_chunk ON postings(chunk_id);
-- COVERING index for the affected-terms df recompute, added 2026-09-12 19:4x. ix_post_term
-- above is on (term) ALONE, so COUNT(DISTINCT chunk_id) had to visit the TABLE ROW for every
-- posting just to read chunk_id -- random reads against a ~3.8 GB file, which is what made a
-- phase doing 0.44s of SQL work take 67.5s. With (term, chunk_id) the plan becomes
-- `SEARCH postings USING COVERING INDEX` and the `USE TEMP B-TREE FOR count(DISTINCT)` step
-- disappears. `[measured: 39,407 touched terms in 4.6s = 0.117 ms/term, against 3,324 terms in
-- 67.5s = 20.3 ms/term before -- 174x per term, on 11.9x MORE terms. Index build 18.9s, disk
-- +486 MB (3,777 -> 4,263 MB) on a derived, rebuildable file.]`
-- DECLARED HERE RATHER THAN LEFT AS A MANUAL CREATE: an index that exists only because someone
-- typed it once is lost by the next rebuild, and the rebuild would silently return to 20 ms a
-- term with nothing in the output to say why.
CREATE INDEX IF NOT EXISTS ix_post_term_chunk ON postings(term, chunk_id);
CREATE INDEX IF NOT EXISTS ix_tri ON vocab_tri(tri);
CREATE INDEX IF NOT EXISTS ix_edges_src ON edges(src);
CREATE INDEX IF NOT EXISTS ix_edges_dst ON edges(dst);
"""


def connect(db_path: str) -> sqlite3.Connection:
    """Open the index, rebuilding from scratch if it was written by an older schema.

    ⚠️ A schema mismatch is NOT recoverable by patching rows, and pretending otherwise is how an
    index starts answering with fields that mean something else than the reader thinks. This file
    is derived from markdown that is still on disk, so a full rebuild costs ~50 seconds and loses
    nothing. Silent partial migration would cost far more than that, once.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.isfile(db_path):
        probe = sqlite3.connect(db_path)
        try:
            found = probe.execute(
                "SELECT value FROM meta WHERE key='schema'").fetchone()
            found = found[0] if found else None
        except sqlite3.Error:
            found = None
        probe.close()
        if found != SCHEMA_VERSION:
            print(f"schema {found!r} != {SCHEMA_VERSION!r}; rebuilding the index from scratch")
            os.replace(db_path, db_path + ".superseded")
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    return con


def tier_of(rel_path: str, kind: str = None) -> str:
    """'knowledge' | 'queue' | 'provenance' -- the single biggest retrieval-quality lever here.

    ⛔ `[measured 2026-08-17 17:3x]` wiki/intake-triage/ is 11,639 of 16,132 chunks -- 72% of the
    index. It is an operational QUEUE: triage packets, agent returns, delivery receipts. Indexing
    it alongside the concept pages does not add knowledge, it adds a haystack, and the measured
    effect was severe: the chunk of `concepts/coordinator.md` that answers "which seat only hands
    work out" sat at dense rank 4,105 of 16,132.

    ⚠️ NOTHING IS EXCLUDED FROM THE INDEX -- every tier is embedded and every tier is queryable.
    This is SCOPING, not deletion: retrieval defaults to the knowledge tier, `--tier NAME` selects,
    and `--all-tiers` reaches everything. A packet you cannot find is still one command away, and
    no record is dropped.

    `provenance` (added 2026-08-23, SEC-113) is raw/transcripts/** -- the ACTUAL CONVERSATIONS.
    It is off by default for the same measured reason `queue` is, and reachable for the reason
    Jon gave: a summary of a conversation is not the conversation, and he does not trust the
    summary. `--tier provenance` or `--scope provenance` gets you the primary's path.
    """
    # ⛔ KIND FIRST, AND THIS ORDERING IS A FAIL-CLOSED FIX, NOT A TIDY-UP. The first version of
    # this function keyed provenance off `rel_path.startswith("raw/")`. That is correct for THIS
    # repo and silently wrong the moment `--provenance` names a directory in another trunk:
    # corpus_files() labels an out-of-root file by its ABSOLUTE path (see label_of), which starts
    # with "G:/..." and not "raw/", so the transcript would have been filed as `knowledge` and
    # admitted straight into the DEFAULT scope -- the exact haystack this tier exists to prevent,
    # arriving through the door the tier opened. The walk already knows what it collected; the
    # kind it assigned is the authority. Path prefixes stay as the fallback for rows written
    # before kinds carried the answer.
    if kind:
        if kind.startswith("provenance:"):
            return "provenance"
    if rel_path.startswith("wiki/intake-triage/") or rel_path.startswith("wiki/archive/"):
        return "queue"
    if rel_path.startswith("raw/"):
        return "provenance"
    return "knowledge"


def doc_summary(text: str, limit: int = 1200) -> str:
    """A document-level string: title, headings, and opening prose.

    ⭐ WHY A SECOND VECTOR PER FILE. A 135-token chunk embeds to a narrow point, so a broad
    paraphrastic question ("which seat only hands work out") matches no single chunk strongly --
    it matches the DOCUMENT. Doc vectors let a page compete on what it is ABOUT, and cost 819 rows.
    """
    title = ""
    body = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("title:") and not title:
            title = stripped[6:].strip().strip('"')
        m = re.match(r"^#{1,3}\s+(.*)$", line)
        if m:
            body.append(m.group(1).strip())
        elif stripped and not stripped.startswith(("---", "|", "```")) and ":" not in stripped[:16]:
            body.append(stripped)
        if sum(len(b) for b in body) > limit:
            break
    return (title + "\n" + "\n".join(body))[: limit + 200]


FM_TITLE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)
FM_CONVSUM = re.compile(r'^conversation_summary:\s*"?(.*?)"?\s*$', re.MULTILINE | re.DOTALL)
HUMAN_TURN = re.compile(r"^##\s+Human\s*$", re.MULTILINE)


def transcript_summary(rel_path: str, text: str, limit: int = 2200) -> str:
    """The ONE string a provenance file is indexed by. Title + what JON actually said.

    WHY NOT doc_summary(). Run it on a transcript and the headings it harvests are "Human",
    "Assistant", "Human", "Assistant" -- the file's structure, not its subject -- while the
    `title:` line and the human turn's opening are exactly the two things a reader is searching
    for. `[measured 2026-08-23]` on chat-2026-07-17-61682b the title is "Photo Orginization Plan"
    and the first human turn is "Need a plan for how to get my photos organized. ... Photos
    scanned from childhood, poorly organized." Both belong in the vector; neither is a heading.

    Jon's turns are preferred over the assistant's DELIBERATELY. He wrote: "i don't trust what
    has been said to be true or not true." The retrievable surface of a transcript should be the
    part he can check against his own memory.

    Sidecars (`*.sidecar.md`) carry a `conversation_summary` in frontmatter that is richer than
    anything derivable from the primary; it is used when present.
    """
    title = ""
    m = FM_TITLE.search(text[:4000])
    if m:
        title = m.group(1).strip().strip('"')
    if rel_path.endswith(".sidecar.md"):
        cm = FM_CONVSUM.search(text[:60000])
        if cm:
            return (title + "\n" + " ".join(cm.group(1).split()))[:limit]
    parts = [title] if title else []
    # Human turns, in order, until the budget is spent. `## Human` / `## Assistant` is the corpus
    # convention (Record Architecture v1); a file that does not use it falls back to doc_summary.
    spans = [hm.end() for hm in HUMAN_TURN.finditer(text)]
    for start in spans:
        seg = text[start:start + 1500]
        seg = seg.split("\n## ")[0]
        seg = " ".join(seg.split())
        if seg:
            parts.append(seg)
        if sum(len(x) for x in parts) > limit:
            break
    if len(parts) <= 1:
        return (title + "\n" + doc_summary(text, limit))[:limit + 200]
    return "\n".join(parts)[:limit + 200]


# ---------------------------------------------------------------- build


def _engine_banner():
    """Which code is actually running, resolved at run time -- never recorded.

    ⭐ soul, 2026-09-05, and it is the sentence that earned this function: "a path typed once lies
    the moment anything moves -- and when that path is on sys.path, what it lies about is WHICH CODE
    RUNS." Personal's builder imported this engine through a hardcoded G: path pinned at 3374d9f
    (09-01) while this tree was at 279b8cc3 (09-05), so its build ran the PRE-FIX engine hours after
    the fix landed here -- and NOTHING IN FOUR DAYS OF BUILD LOGS NAMED THE ENGINE, so no reader of a
    "0 dropped" line could tell which version produced it.
    ⚠️ Printed on BOTH the rebuild and the up-to-date paths: a provenance line that appears on only
    some runs is a provenance line nobody can rely on.
    """
    eng = os.path.dirname(os.path.abspath(__file__))
    try:
        r = subprocess.run(["git", "-C", eng, "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=15)
        head = r.stdout.strip() if r.returncode == 0 else "UNKNOWN"
    except Exception:
        head = "UNKNOWN"
    return "  engine     : %s @ %s" % (eng, head or "UNKNOWN")


def build(db_path: str, prefer: str, force: bool, quiet: bool = False, includes=None,
          root=None, provenance=None, allow_narrowing: bool = False,
          fast_terms: bool = False) -> int:   # fast_terms is LAST on purpose: inserting it
    # mid-signature silently rebound args.root to it, caught by reading the call site.
    lock = BuildLock()
    ok, holder = lock.acquire(force=force)
    if not ok:
        print(f"REFUSED: build lock held by live pid {holder} ({LOCKDIR}).", file=sys.stderr)
        print("         Raise it in the hall, or re-run with --force if you own that process.",
              file=sys.stderr)
        return 4
    try:
        return _build_locked(db_path, prefer, quiet, includes, root, provenance,
                             allow_narrowing, fast_terms=fast_terms)
    finally:
        lock.release()


# ⛔ `allow_narrowing` WAS NOT FORWARDED HERE, AND THE GUARD THAT USES IT LIVES IN THIS FUNCTION.
# From 4b9cde0c until 2026-09-05 17:1x, `if gone and not allow_narrowing:` referenced a name that
# does not exist in this scope -- so ANY build with a non-empty `gone` list would have raised
# NameError instead of keeping the rows. It never fired because every build since the fix happened
# to have `gone` empty.
# ⭐ THE NIGHT'S OWN SENTENCE, LANDING ON ITS AUTHOR: "a branch that has never run on real data is a
# written warning, not a tested path." I wrote that in session_parent.py's docstring and then shipped
# a guard whose only branch had never executed. `--allow-narrowing` was also unreachable: the flag
# parsed, reached build(), and stopped there.
# Found while answering soul, who was about to repoint Personal's builder at this engine.
def _build_locked(db_path: str, prefer: str, quiet: bool, includes=None, root=None,
                  provenance=None, allow_narrowing: bool = False, fast_terms: bool = False) -> int:
    started = time.time()
    con = connect(db_path)
    cur = con.cursor()

    root = os.path.normpath(root) if root else REPO
    includes = sorted(includes or [])
    provenance = sorted(provenance or [])
    _t_walk = time.time()
    files = corpus_files(includes, root, provenance)
    _T = {"walk": time.time() - _t_walk}
    # ⛔ THE ACCESSOR WAS NEVER CALLED. Added 2026-09-13 01:0x with a docstring saying "a list
    # collected and never printed is the same silence the two findings were made of" -- and then no
    # caller. Professional's fifth build confirmed the SCOPE fix reached them (the global constitution
    # is absent from the files table) and the audible skip did NOT print, then found the cause by
    # grepping for callers of walk_notes(): there were none.
    # ⭐ THIRD TIME TONIGHT A FIX'S OWN CLASS LANDED ON THE FIX: Rule 17 on its own deployment claim,
    # the staleness probe's header on its own remedy line, and now an anti-silence accessor that was
    # silent. Writing the warning is not the same act as wiring the caller, and the warning is the
    # part that feels like the work.
    for _note in walk_notes():
        print("[walk] " + _note, file=sys.stderr)
    if not files:
        print("FAIL no corpus files found", file=sys.stderr)
        return 2

    known = {row[0]: (row[1], row[2], row[3], row[4])
             for row in cur.execute("SELECT path, id, sha, kind, tier FROM files")}
    seen, changed, unchanged, relabeled = set(), [], 0, 0
    _t_hash = time.time()
    _touched = set()   # terms whose df could have moved this run (see the terms rebuild)
    for full, rel, kind in files:
        seen.add(rel)
        digest = sha256(full)
        # ⛔ THE STORED DIGEST MUST CARRY THE POLICY THAT PRODUCED THE CHUNKS, NOT ONLY THE BYTES.
        # Found the hour the body-chunk policy landed: the file content had not changed, so an
        # idempotent-by-content build reported "UP-TO-DATE, nothing to re-embed" and the new policy
        # never applied. `--force` only reclaims the lock; there was no way to say "the RULE
        # changed" short of deleting the index.
        # ⭐ This is the SAME CLASS as the freshness cache fixed this morning (a cached verdict that
        # did not record what it was computed over) and the same class as the doc-level policy
        # itself. A stored result must name its inputs -- ALL of them, and a policy is an input.
        if tier_of(rel, kind) == "provenance":
            digest = hashlib.sha256(
                ("%s|policy=%s|days=%d|max=%d" % (
                    digest, PROVENANCE_POLICY_VERSION, PROVENANCE_BODY_CHUNK_DAYS,
                    PROVENANCE_MAX_CHARS)).encode("utf-8")).hexdigest()
        if rel in known and known[rel][1] == digest:
            unchanged += 1
            # kind/tier are derived from the WALK CONFIG, not the content -- a config change
            # (e.g. include:scripts becoming selfdoc:scripts) must land without re-embedding,
            # or the labels record a walk that no longer exists (derive, don't record).
            if (kind, tier_of(rel, kind)) != (known[rel][2], known[rel][3]):
                cur.execute("UPDATE files SET kind=?, tier=? WHERE id=?",
                            (kind, tier_of(rel, kind), known[rel][0]))
                relabeled += 1
            continue
        changed.append((full, rel, kind, digest))

    # Files that vanished from the corpus lose their INDEX rows only. The source of truth is the
    # markdown on disk; this table is derived and is rebuilt from it.
    gone = [rel for rel in known if rel not in seen]

    # ⛔ NARROWING GUARD, 2026-09-04. "Vanished from the corpus" and "outside THIS RUN'S WALK" are
    # different facts and this line could not tell them apart. MEASURED TONIGHT, twice:
    #
    #   * step 3 of postcompact_pipeline rebuilt with --include exchange --provenance <mirror> and
    #     brought the index to 10,260 files / 92,450 chunks;
    #   * step 10 (index_queue_drain.py) then rebuilt in the SAME pipeline with --include <2 queued
    #     files> and NO --provenance, and every file its narrower walk could not reach was deleted.
    #     [measured 22:2x: n_files 10,260 -> 3,020, exchange/ 936 -> 1, corpus_provenance []]
    #
    # ⭐ So a pipeline whose whole purpose is to keep the graph current DELETED 7,000 files of it,
    # every step reported PASS, and the retrieval that follows answers confidently from what is
    # left -- it never says what it could not see. That is the defect Jon has been naming as
    # "the vector embeded graph rag is not good enough": not bad retrieval, a shrinking corpus.
    #
    # ⚠️ THE FIX IS THE DEFAULT, NOT ANOTHER FLAG TO REMEMBER. The flags were the bug: every caller
    # had to pass the full widening set or silently destroy the index, and one caller out of two
    # forgot. Retaining a row for a file that really was deleted costs a stale hit, refreshed by
    # content hash the next time it is walked. Deleting a row for a file that still exists costs
    # the file. Those are not symmetric, and "Yeah no deletion" (Jon, 2026-08-09) points the same
    # way. Adopted from soul's --allow-narrowing guard in build_trunk_index.py (24e29e1) -- their
    # message tonight: "yours proves the guard belongs in the OTHER builder too."
    if gone and not allow_narrowing:
        print(f"NARROWING REFUSED: {len(gone)} indexed file(s) were not reached by this run's walk "
              f"and were KEPT, not deleted. This run's includes={len(includes)} "
              f"provenance={len(provenance)}. If they are genuinely gone, re-run with "
              f"--allow-narrowing; a narrower walk is NOT evidence of deletion.", file=sys.stderr)
        gone = []

    _T["hash_scan"] = time.time() - _t_hash
    _t_rest = time.time()
    for rel in gone:
        fid = known[rel][0]
        ids = [r[0] for r in cur.execute("SELECT id FROM chunks WHERE file_id=?", (fid,))]
        cur.executemany("DELETE FROM vectors WHERE chunk_id=?", [(i,) for i in ids])
        if ids:
            _touched.update(r[0] for r in cur.execute(
                "SELECT DISTINCT term FROM postings WHERE chunk_id IN (%s)"
                % ",".join("?" * len(ids)), tuple(ids)))
        cur.executemany("DELETE FROM postings WHERE chunk_id=?", [(i,) for i in ids])
        cur.execute("DELETE FROM chunks WHERE file_id=?", (fid,))
        cur.execute("DELETE FROM edges WHERE src=?", (fid,))
        cur.execute("DELETE FROM docvecs WHERE file_id=?", (fid,))
        cur.execute("DELETE FROM files WHERE id=?", (fid,))

    if not changed and not gone:
        n_chunks = cur.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        # ⛔ The fingerprint MUST be refreshed on this path too. Caught 2026-08-17 immediately
        # after adding it: the no-op branch returned before any meta write, so an index built by
        # this path would carry no fingerprint and would report itself STALE forever -- an alarm
        # that always fires, which this repo already has on record as a defect class of its own.
        cur.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('corpus_fingerprint', ?)",
                    (corpus_fingerprint(includes, root, provenance),))
        cur.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('corpus_provenance', ?)",
                    (json.dumps(provenance),))
        cur.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('corpus_includes', ?)",
                    (json.dumps(includes),))
        cur.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('corpus_root', ?)",
                    (root.replace(os.sep, "/"),))
        if not quiet:
            print(f"UP-TO-DATE  {unchanged} files unchanged"
                  + (f" ({relabeled} relabeled kind/tier in place)" if relabeled else "")
                  + f", {n_chunks} chunks, nothing to re-embed "
                  f"({os.path.getsize(db_path) / 1e6:.1f} MB)")
            # ⛔ THE NO-OP PATH MUST NAME THE ENGINE TOO, and this gap was stated as a bound on my own
            # fix an hour before it was closed: the banner lived only in the real-rebuild summary, so
            # an UP-TO-DATE run said nothing about which code produced it. ⭐ That is the worse half
            # of soul's finding, not the lesser one -- a no-op is exactly when a reader most needs to
            # know whether a stale engine simply found nothing to do. A provenance line that appears
            # on only some runs is a provenance line nobody can rely on.
            print(_engine_banner())
        con.commit()
        con.close()
        return 0

    emb = load_embedder(prefer)
    pending_text, pending_ids = [], []
    pending_doc_text, pending_doc_ids = [], []
    added_chunks = 0

    for full, rel, kind, digest in changed:
        try:
            text = open(full, encoding="utf-8", errors="replace").read()
        except OSError as exc:
            print(f"WARN unreadable, skipped: {rel} ({exc})", file=sys.stderr)
            continue

        row = cur.execute("SELECT id FROM files WHERE path=?", (rel,)).fetchone()
        if row:
            fid = row[0]
            ids = [r[0] for r in cur.execute("SELECT id FROM chunks WHERE file_id=?", (fid,))]
            cur.executemany("DELETE FROM vectors WHERE chunk_id=?", [(i,) for i in ids])
            if ids:
                _touched.update(r[0] for r in cur.execute(
                    "SELECT DISTINCT term FROM postings WHERE chunk_id IN (%s)"
                    % ",".join("?" * len(ids)), tuple(ids)))
            cur.executemany("DELETE FROM postings WHERE chunk_id=?", [(i,) for i in ids])
            cur.execute("DELETE FROM chunks WHERE file_id=?", (fid,))
            cur.execute("DELETE FROM edges WHERE src=?", (fid,))
            cur.execute("DELETE FROM docvecs WHERE file_id=?", (fid,))
            cur.execute("UPDATE files SET sha=?, bytes=?, kind=?, tier=? WHERE id=?",
                        (digest, len(text.encode("utf-8")), kind, tier_of(rel, kind), fid))
        else:
            cur.execute("INSERT INTO files (path, sha, bytes, kind, tier) VALUES (?,?,?,?,?)",
                        (rel, digest, len(text.encode("utf-8")), kind, tier_of(rel, kind)))
            fid = cur.lastrowid

        # Provenance files are indexed DOC-LEVEL ONLY -- one chunk, one vector, no body chunks.
        # See PROVENANCE_DIRS: body-chunking 4,376 transcripts would add ~100k chunks to a 16k
        # index. The chunk's line span is 1..EOF and that is honest: the span IS the file.
        if tier_of(rel, kind) == "provenance" and provenance_is_recent(rel):
            # BODY-CHUNKED provenance: the recent window, conversation only, coarse granularity,
            # with tool payloads reduced to their identifiers. The doc-vector summary is still
            # emitted below via the shared path, so nothing this file had before is lost.
            body_text = strip_tool_payloads(text)
            summary = transcript_summary(rel, text)
            if summary.strip():
                pending_doc_text.append(summary)
                pending_doc_ids.append(fid)
            for ordinal, (heading, start, end, body) in enumerate(
                    chunk_markdown(body_text, PROVENANCE_MAX_CHARS)):
                toks = TOKEN.findall(body.lower())
                cur.execute(
                    "INSERT INTO chunks (file_id, ord, heading, start_line, end_line, ntok, text) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (fid, ordinal, heading, start, end, len(toks), body))
                cid = cur.lastrowid
                counts = {}
                for tok in toks:
                    counts[tok] = counts.get(tok, 0) + 1
                cur.executemany("INSERT INTO postings (term, chunk_id, tf) VALUES (?,?,?)",
                                [(t, cid, n_) for t, n_ in counts.items()])
                _touched.update(counts)
                pending_text.append((heading + "\n" + body) if heading else body)
                pending_ids.append(cid)
                added_chunks += 1
            continue

        if tier_of(rel, kind) == "provenance":
            summary = transcript_summary(rel, text)
            if summary.strip():
                pending_doc_text.append(summary)
                pending_doc_ids.append(fid)
                toks = TOKEN.findall(summary.lower())
                nlines = text.count("\n") + 1
                cur.execute(
                    "INSERT INTO chunks (file_id, ord, heading, start_line, end_line, ntok, text) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (fid, 0, "(whole transcript)", 1, nlines, len(toks), summary))
                cid = cur.lastrowid
                counts = {}
                for tok in toks:
                    counts[tok] = counts.get(tok, 0) + 1
                cur.executemany("INSERT INTO postings (term, chunk_id, tf) VALUES (?,?,?)",
                                [(t, cid, n_) for t, n_ in counts.items()])
                _touched.update(counts)
                pending_text.append(summary)
                pending_ids.append(cid)
                added_chunks += 1
            continue

        summary = doc_summary(text)
        if summary.strip():
            pending_doc_text.append(summary)
            pending_doc_ids.append(fid)

        for ordinal, (heading, start, end, body) in enumerate(chunk_markdown(text)):
            toks = TOKEN.findall(body.lower())
            cur.execute(
                "INSERT INTO chunks (file_id, ord, heading, start_line, end_line, ntok, text) "
                "VALUES (?,?,?,?,?,?,?)",
                (fid, ordinal, heading, start, end, len(toks), body))
            cid = cur.lastrowid
            counts = {}
            for tok in toks:
                counts[tok] = counts.get(tok, 0) + 1
            cur.executemany("INSERT INTO postings (term, chunk_id, tf) VALUES (?,?,?)",
                            [(t, cid, n) for t, n in counts.items()])
            _touched.update(counts)
            # The embedded string carries the heading path: a bare paragraph often has no subject,
            # and the heading is where the subject usually lives.
            pending_text.append((heading + "\n" + body) if heading else body)
            pending_ids.append(cid)
            added_chunks += 1

        for kindname, target in extract_links(text):
            cur.execute("INSERT INTO edges (src, dst, kind, raw) VALUES (?,?,?,?)",
                        (fid, -1, kindname, target))

    if pending_text:
        if not quiet:
            print(f"embedding {len(pending_text)} chunks with {emb.name} ({emb.dims}d) ...")
        batch = 512
        for i in range(0, len(pending_text), batch):
            vecs = emb.encode(pending_text[i : i + batch])
            cur.executemany(
                "INSERT OR REPLACE INTO vectors (chunk_id, vec) VALUES (?,?)",
                [(cid, vecs[j].astype(np.float32).tobytes())
                 for j, cid in enumerate(pending_ids[i : i + batch])])

    if pending_doc_text:
        if not quiet:
            print(f"embedding {len(pending_doc_text)} document summaries ...")
        for i in range(0, len(pending_doc_text), 512):
            vecs = emb.encode(pending_doc_text[i : i + 512])
            cur.executemany(
                "INSERT OR REPLACE INTO docvecs (file_id, vec) VALUES (?,?)",
                [(fid, vecs[j].astype(np.float32).tobytes())
                 for j, fid in enumerate(pending_doc_ids[i : i + 512])])

    # Global term stats and the fuzzy vocabulary are derived, so rebuild them wholesale -- cheap,
    # and it removes the class of bug where an incremental df drifts from the postings it describes.
    _t_terms = time.time()
    # === THE TERM TABLE: WHOLESALE BY DEFAULT, AFFECTED-TERMS-ONLY UNDER --fast-terms ===
    # [measured 2026-09-12 16:0x] `DELETE FROM terms` + `INSERT ... GROUP BY term` over 25,965,367
    # posting rows is 106.7s of a 120.4s incremental build. It is the whole cost. The trigram
    # vocabulary (21.5s) and the per-file sha256 scan (0.7s) were my first two suspects and both were
    # noise; this is the third and it is the one.
    #
    # ⛔ THE COMMENT ABOVE THIS BLOCK IS AN ARGUMENT AGAINST WHAT FOLLOWS, WRITTEN BY AN EARLIER SEAT:
    # "rebuild them wholesale -- cheap, and it removes the class of bug where an incremental df drifts
    # from the postings it describes." ⭐ It is right about the bug class and wrong about "cheap". So
    # the incremental path was OFF BY DEFAULT until its gate passed. ✅ GATE PASSED 2026-09-12 16:2x:
    # an INDEPENDENT ORACLE -- `CREATE TEMP TABLE oracle AS SELECT term, COUNT(DISTINCT chunk_id)
    # FROM postings GROUP BY term`, 100.4s over 25,965,367 rows -- produced 514,519 rows against the
    # live table's 514,519, with 0 rows on either side alone and 0 df disagreements. It is now the
    # DEFAULT, with `--wholesale-terms` as the escape hatch.
    # ⚠️ n=1 on that oracle. Re-runnable by `python scripts/audit/terms_oracle_check.py`.
    # ⛔ AND THE FIRST ATTEMPT AT THIS TEST WAS VOID: I compared two consecutive builds, and the
    # second took the UP-TO-DATE early-return path, so it never rebuilt terms at all -- it compared
    # the fast path against ITSELF and printed 0 disagreements. A grep filter hid the missing output.
    # ⭐ A test whose control arm silently did not run reads exactly like a pass. A predecessor's stated reason is not overridden by a measurement
    # of a different quantity.
    #
    # WHY AFFECTED-TERMS-ONLY IS CORRECT WHEN IT IS: df(term) = COUNT(DISTINCT chunk_id) over postings.
    # A term's df can change only if a posting row for that term was added or removed. `_touched`
    # collects exactly that set -- terms read out of every chunk whose postings were deleted this run,
    # plus every term inserted this run -- so a term not in `_touched` provably has the same df.
    # ⚠️ df is NOT recomputed for a term merely because some OTHER term in the same chunk changed;
    # that is the drift the old comment warns about and it is why the set is built from postings rather
    # than from files.
    # ⛔ THE PER-TERM LOOP BELOW LOOKS LIKE THE OBVIOUS THING TO BATCH AND IT IS NOT. DO NOT "FIX" IT.
    # I replaced it 2026-09-12 ~18:5x with one grouped scan joined to a temp table of the touched
    # terms -- the textbook batching, and `ix_post_term` exists to serve it -- and then MEASURED BOTH
    # FORMS ON ONE INDEX STATE (520,306 terms, 26,495,990 postings), same sampled term set, df sums
    # identical in all three arms so both forms are CORRECT:
    #
    # ⛔ THE TABLE BELOW IS WARM-CACHE AND DOES NOT MEASURE BUILD TIME. STRUCK AS EVIDENCE
    # 2026-09-12 19:4x, KEPT AS THE RECORD. Both arms ran one query after another in a single
    # warm process. `[measured 19:43, same phase, all three sub-steps in one rolled-back
    # transaction: DELETE 3,324 rows 0.17s + 3,324 per-term COUNT(DISTINCT) 0.25s + INSERT 3,322
    # rows 0.03s = 0.44s, inside a phase this file's own timer reports as 67.5s -- A FACTOR OF
    # 153.]` ⭐ So the phase is NOT dominated by the query form and these numbers cannot speak to
    # it. Leading hypothesis, UNPROVEN because a cold cache cannot be forced on this platform:
    # cold random I/O against a ~3.8 GB file after the same build just wrote new postings into
    # it, ~20 ms per term cold against 0.23 ms warm.
    # ⚠ WHAT THE REVERT ACTUALLY RESTS ON, since the table cannot carry it: the IN-SITU pair --
    # restored loop 67.5s for 3,324 terms on 18,007 files against the batched form's 90.7s on
    # 18,004 -- both cold, both inside a real build. The conclusion survives; its stated basis
    # did not. Professional's review regraded this claim GROUNDED-ON-THE-IN-SITU-PAIR, TABLE
    # WITHDRAWN, and asked for this label rather than a deletion.
    #   touched terms | per-term loop | batched join+GROUP BY | loop is   [WARM CACHE -- NOT EVIDENCE]
    #   --------------+---------------+-----------------------+---------
    #            2,000|        0.68s  |               3.77s   | 5.5x FASTER
    #           20,000|        5.27s  |               9.28s   | 1.8x FASTER
    #          100,000|       22.57s  |              26.76s   | 1.2x FASTER
    #
    # ⭐ THE LOOP WINS AT EVERY SIZE MEASURED. `SELECT COUNT(DISTINCT chunk_id) ... WHERE term=?` is an
    # index seek over a few rows; the join form makes SQLite aggregate across a 26.5M-row table and
    # sort to group. The ratio does close as the set grows, so a corpus-wide touch might one day flip
    # it -- but a real incremental touches a few files, which is the left column, where batching is
    # FIVE AND A HALF TIMES WORSE.
    # ⚠️ AND THE NUMBER THAT MOTIVATED THE ATTEMPT WAS A CONFOUNDED COMPARISON: "62.0s of 182s" was
    # measured on a 13,026-file corpus and the batched run's 90.7s on an 18,004-file one. Comparing
    # them made batching look like a fix for a cost that was actually corpus growth. The A/B above is
    # the only comparison that answers it, and it says revert.
    # ✅ CONFIRMED IN SITU, not only in the isolated test: the restored loop ran **67.5s for 3,324
    # touched terms** on an 18,007-file corpus (whole build 104.3s), against the batched form's 90.7s
    # on an 18,004-file one -- so the loop is ~1.34x faster on a like-for-like build too, and 3,324 is
    # deep inside the left column where the isolated test says batching is worst.
    if fast_terms:
        _n_t = len(_touched)
        if _n_t:
            cur.executemany("DELETE FROM terms WHERE term=?", [(t,) for t in _touched])
            _rows = []
            for _t in _touched:
                _df = cur.execute("SELECT COUNT(DISTINCT chunk_id) FROM postings WHERE term=?",
                                  (_t,)).fetchone()[0]
                if _df:
                    _rows.append((_t, _df))
            cur.executemany("INSERT INTO terms (term, df) VALUES (?,?)", _rows)
        _T["terms_affected_only"] = time.time() - _t_terms
        if not quiet:
            print("  terms      : AFFECTED-ONLY %d touched term(s) -> %d row(s) rewritten in %.1fs "
                  "(per-term index seeks, MEASURED FASTER THAN BATCHING at 2k/20k/100k terms -- see the "
                  "comment above before optimizing this. DEFAULT path; --wholesale-terms is the escape "
                  "hatch; scripts/audit/terms_oracle_check.py is the gate)"
                  % (_n_t, len(_rows) if _n_t else 0, _T["terms_affected_only"]))
    else:
        cur.execute("DELETE FROM terms")
        cur.execute("INSERT INTO terms (term, df) "
                    "SELECT term, COUNT(DISTINCT chunk_id) FROM postings GROUP BY term")
        _T["terms_groupby"] = time.time() - _t_terms
    # === TRIGRAM VOCABULARY: REBUILT ONLY WHEN THE VOCABULARY ACTUALLY CHANGED ===
    # Added 2026-09-12 15:0x CDT. Jon: "based on external research, possible to get faster? Did not
    # implement script changes correctly? Clear goal, clear testing no gates?"
    #
    # ⛔ THE MEASUREMENT THAT JUSTIFIES IT, and it is the whole case:
    # [measured 2026-09-12 14:54-14:56] a build that (re)indexed ONE file and embedded TWO chunks took
    # 140.5 s. The comment above says rebuilding this wholesale is "cheap". At 2,828,399 trigram rows
    # it is not: DELETE + regenerate + INSERT of ~2.8M rows runs on EVERY invocation regardless of how
    # little changed. ⭐ That is the exact shape the Google AI Mode session Jon forwarded describes as
    # the thing to avoid -- recomputing the whole matrix when only the neighbourhood of one node moved.
    #
    # ⭐ GOAL, stated before the change so the test can fail: a build whose df>=2 term set is unchanged
    # must not touch vocab_tri at all, and fuzzy/misspelled retrieval must be BYTE-IDENTICAL afterward.
    # ⚠️ THE CORRECTNESS RISK IS REAL AND NAMED: this table is what answers Jon's typos. Skipping its
    # rebuild when it SHOULD have changed would silently degrade exactly the feature it exists for --
    # a quiet loss, the worst class. So the guard is a FINGERPRINT OF THE TERM SET ITSELF, not a
    # file-count heuristic: if one term crosses the df>=2 threshold, the fingerprint moves and we
    # rebuild. Nothing is skipped on the basis of "probably unchanged".
    vocab = [r[0] for r in cur.execute("SELECT term FROM terms WHERE df >= 2 ORDER BY term")]
    _fp = hashlib.sha256((chr(10).join(vocab)).encode("utf-8", "replace")).hexdigest()
    _prev = cur.execute("SELECT value FROM meta WHERE key='vocab_tri_fp'").fetchone()
    _have = cur.execute("SELECT COUNT(*) FROM vocab_tri").fetchone()[0]
    if _prev and _prev[0] == _fp and _have:
        if not quiet:
            print("  vocab_tri  : SKIPPED -- df>=2 term set unchanged (%d terms, %d trigram rows kept, "
                  "fp %s)" % (len(vocab), _have, _fp[:12]))
    else:
        _t_v = time.time()
        cur.execute("DELETE FROM vocab_tri")
        rows = []
        for term in vocab:
            for tri in trigrams(term):
                rows.append((tri, term))
        cur.executemany("INSERT INTO vocab_tri (tri, term) VALUES (?,?)", rows)
        cur.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('vocab_tri_fp', ?)", (_fp,))
        if not quiet:
            print("  vocab_tri  : REBUILT %d trigram rows from %d terms in %.1fs (reason: %s)"
                  % (len(rows), len(vocab), time.time() - _t_v,
                     "no fingerprint stored" if not _prev else
                     ("table empty" if not _have else "term set changed")))

    _T["chunk_embed_terms_vocab"] = time.time() - _t_rest
    _t_edges = time.time()
    # Resolve file->file edges now that every file row exists.
    paths = {row[1]: row[0] for row in cur.execute("SELECT id, path FROM files")}
    stem = {}
    for path, fid in paths.items():
        stem.setdefault(os.path.basename(path)[:-3].lower(), fid)
    resolved = 0
    for eid, src, raw, kind in list(
            cur.execute("SELECT rowid, src, raw, kind FROM edges WHERE dst = -1")):
        key = os.path.basename(raw)
        key = key[:-3].lower() if key.endswith(".md") else key.lower()
        dst = stem.get(key)
        if dst is not None and dst != src:
            cur.execute("UPDATE edges SET dst=? WHERE rowid=?", (dst, eid))
            resolved += 1

    n_files = cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    n_chunks = cur.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    n_edges_res = cur.execute("SELECT COUNT(*) FROM edges WHERE dst > 0").fetchone()[0]
    n_edges_all = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    avg_len = cur.execute("SELECT AVG(ntok) FROM chunks").fetchone()[0] or 0.0
    n_know = cur.execute(
        "SELECT COUNT(*) FROM chunks c JOIN files f ON f.id=c.file_id "
        "WHERE f.tier='knowledge'").fetchone()[0]
    n_prov = cur.execute(
        "SELECT COUNT(*) FROM chunks c JOIN files f ON f.id=c.file_id "
        "WHERE f.tier='provenance'").fetchone()[0]
    n_docs = cur.execute("SELECT COUNT(*) FROM docvecs").fetchone()[0]
    for key, value in [
        ("embedder", emb.name), ("dims", str(emb.dims)),
        ("built_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
        ("n_files", str(n_files)), ("n_chunks", str(n_chunks)),
        ("n_knowledge_chunks", str(n_know)), ("n_docvecs", str(n_docs)),
        ("avg_chunk_tokens", f"{avg_len:.1f}"), ("schema", SCHEMA_VERSION),
        # The include list rides in meta so retrieve.py's staleness check fingerprints the SAME
        # corpus this index was built over -- otherwise a widened build trips STALE forever,
        # which is the alarm-that-always-fires defect class this repo already has on record.
        ("corpus_fingerprint", corpus_fingerprint(includes, root, provenance)),
        ("corpus_includes", json.dumps(includes)),
        ("corpus_provenance", json.dumps(provenance)),
        # The root rides in meta too (Personal's letter, ask 2): an index must know what tree it
        # indexed, and retrieve.py must fingerprint THAT tree, not the one its own file sits in.
        ("corpus_root", root.replace(os.sep, "/")),
        ("build_seconds", f"{time.time() - started:.1f}"),
    ]:
        cur.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?,?)", (key, value))
    con.commit()
    con.close()

    if not quiet:
        print(f"BUILT  {db_path}")
        _T["edges"] = time.time() - _t_edges
        _T["rest"] = time.time() - _t_rest
        print("  phases     : " + "  ".join("%s=%.1fs" % (k, v) for k, v in _T.items())
              + "   # walk=enumerate corpus, hash_scan=sha256 EVERY file to detect change,"
              + " rest=embed+chunk+edges+vocab. Added 2026-09-12 after a WRONG GUESS:"
              + " I named the trigram vocabulary as the fixed cost and it was 21.8s of 148.1s.")
        print(f"  files      : {n_files}  ({len(changed)} (re)indexed, {unchanged} unchanged, "
              f"{len(gone)} dropped)")
        print(f"  chunks     : {n_chunks}  (+{added_chunks} this run, avg {avg_len:.0f} tokens)")
        print(f"  tiers      : {n_know} knowledge / {n_chunks - n_know - n_prov} queue "
              f"/ {n_prov} provenance (retrieval defaults to knowledge; "
              f"--tier provenance reaches the transcripts; --all-tiers reaches everything)")
        print(f"  doc vectors: {n_docs}")
        print(f"  vocabulary : {len(vocab)} fuzzy-expandable terms, {len(rows)} trigram entries")
        print(f"  edges      : {n_edges_res} resolved of {n_edges_all} link references")
        print(f"  embedder   : {emb.name} ({emb.dims}d)")
        # Assignment item 6: the cost of keeping it fresh must be visible from day one.
        print(f"  index size : {os.path.getsize(db_path) / 1e6:.1f} MB  "
              f"(derived, off Drive, rebuildable)")
        print(f"  seconds    : {time.time() - started:.1f}")
        # ⛔ ENGINE PROVENANCE, added 2026-09-05 on soul's finding, and it is their sentence that
        # earns it: "a path typed once lies the moment anything moves -- and when that path is on
        # sys.path, what it lies about is WHICH CODE RUNS."
        # Personal's builder imports this engine via a hardcoded G: path. That checkout sat at
        # 3374d9f (09-01) while this tree was at 279b8cc3 (09-05), so their 00:35 build executed the
        # PRE-FIX build_index.py -- the one WITHOUT the default-off narrowing guard, hours after the
        # guard landed here. Their build printed "0 dropped" only because their change happened to be
        # purely additive; a narrowing one would have reproduced CFL's 7,240-file loss with CFL's own
        # code. ⭐ NOTHING IN THE OUTPUT NAMED THE ENGINE, so no reader of any build log for four days
        # could tell which version produced the number. Now every build says.
        print(_engine_banner())
    return 0


# ---------------------------------------------------------------- selftest


def selftest() -> int:
    """Exercise BOTH verdicts of every check. A test that only sees the success path is D9's shape."""
    failures = []

    def check(label, got, want):
        ok = got == want
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}: got {got!r} want {want!r}")
        if not ok:
            failures.append(label)

    print("selftest: chunker")
    doc = ("# Title\n\nalpha body long enough to survive the minimum.\n\n"
           "## Sub\n\nbeta body long enough to survive the minimum.\n")
    chunks = chunk_markdown(doc)
    check("two sections", len(chunks), 2)
    check("heading path nests", chunks[1][0], "Title > Sub")
    check("start line of sub section", chunks[1][1], 5)
    check("empty doc yields nothing", len(chunk_markdown("\n\n")), 0)
    # The floor must actually reject: a heading with a stub under it is noise, not a chunk.
    check("sub-minimum body rejected", len(chunk_markdown("# H\n\ntiny.\n")), 0)
    big = "# Big\n\n" + "\n\n".join(["para %d %s" % (i, "x" * 300) for i in range(12)])
    check("oversize section splits", len(chunk_markdown(big)) > 1, True)

    print("selftest: links")
    links = extract_links("see [[loop-taxonomy]] and [a](../concepts/foo.md) and [[x|alias]]")
    check("wikilink+mdlink+aliased", sorted(links),
          [("mdlink", "../concepts/foo.md"), ("wikilink", "loop-taxonomy"), ("wikilink", "x")])
    check("no links found", extract_links("plain prose"), [])

    print("selftest: build lock -- BOTH verdicts")
    lock_a, lock_b = BuildLock(LOCKDIR + ".test"), BuildLock(LOCKDIR + ".test")
    got_a, _ = lock_a.acquire()
    check("first acquire succeeds", got_a, True)
    got_b, holder = lock_b.acquire()
    check("second acquire REFUSED while live", got_b, False)
    check("refusal names the live holder", holder, os.getpid())
    lock_a.release()
    got_c, _ = lock_b.acquire()
    check("acquire succeeds after release", got_c, True)
    lock_b.release()
    # Stale holder: a dead pid must be reclaimed, or one crash bricks the index forever.
    os.makedirs(LOCKDIR + ".test", exist_ok=True)
    with open(os.path.join(LOCKDIR + ".test", "pid"), "w", encoding="utf-8") as fh:
        fh.write("999999999 0\n")
    lock_d = BuildLock(LOCKDIR + ".test")
    got_d, _ = lock_d.acquire()
    check("stale (dead pid) lock is reclaimed", got_d, True)
    lock_d.release()
    check("lockdir removed on release", os.path.exists(LOCKDIR + ".test"), False)

    print("selftest: trigram vocabulary")
    shared = trigrams("embedding") & trigrams("embeding")
    check("typo shares trigrams with truth", len(shared) >= 5, True)
    check("unrelated shares few", len(trigrams("embedding") & trigrams("sqlite")) <= 1, True)

    # L3 -- structural supersession parser (P2-3, 2026-08-23). BOTH verdicts are exercised: the
    # shapes that MUST yield an edge, and the shapes that MUST NOT. The must-nots are the point.
    # A first pass over the corpus without the looks-like-a-reference guard produced 30 "edges",
    # 17 of them prose -- targets like "the", "any", "two", "CFL", "374127" -- each of which would
    # have been handed to a basename-stem lookup and could silently demote an unrelated file by
    # collision. That is a ranking change nobody could trace back to a cause.
    print("selftest: supersedes frontmatter parser -- BOTH verdicts")
    fm = lambda body: "---\n" + body + "\n---\nbody text\n"
    check("bare scalar path yields an edge",
          extract_supersedes(fm("supersedes: wiki/tracker/questions-for-jon.md")),
          [("supersedes", "wiki/tracker/questions-for-jon.md")])
    check("prose tail after the path is trimmed",
          extract_supersedes(fm("supersedes_in_practice: wiki/a.md (~58 rows, last commit 07-30)")),
          [("supersedes", "wiki/a.md")])
    check("wikilink target unwrapped, NOT split as a list",
          extract_supersedes(fm("supersedes: [[record-architecture-v1]]")),
          [("supersedes", "record-architecture-v1")])
    check("inline list yields one edge per item",
          extract_supersedes(fm("supersedes: [wiki/a.md, wiki/b.md]")),
          [("supersedes", "wiki/a.md"), ("supersedes", "wiki/b.md")])
    check("'none' is a real statement but NOT an edge",
          extract_supersedes(fm("supersedes: none (first map of this domain)")), [])
    check("PROSE value yields NO edge (the stem-collision guard)",
          extract_supersedes(fm("supersedes: the coordination charter's clause 3")), [])
    check("body mention is not frontmatter",
          extract_supersedes("---\ntitle: x\n---\nthis page supersedes wiki/a.md"), [])
    check("no frontmatter at all yields nothing",
          extract_supersedes("supersedes: wiki/a.md\nbody"), [])

    print(f"\nselftest: {'ALL PASS' if not failures else str(len(failures)) + ' FAILED'}")
    return 0 if not failures else 5


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--embedder", default="auto", choices=["auto", "static", "hash"])
    ap.add_argument("--force", action="store_true", help="reclaim a live lock (deliberate override)")
    ap.add_argument("--wholesale-terms", action="store_false", dest="fast_terms",
                    help="ESCAPE HATCH: rebuild the whole terms table with a GROUP BY over all "
                         "26M postings. Was the default until 2026-09-12 16:2x, when the oracle "
                         "diff came back 0 disagreements over 514,519 terms and affected-only "
                         "became the default. Use this if you suspect df drift.")
    # ⛔ DEFAULT FLIPPED BACK TO WHOLESALE 2026-09-12 19:5x, AND THE PREDECESSOR I OVERRODE THIS
    # AFTERNOON WAS RIGHT. Their comment said: rebuild them wholesale -- "cheap, and it removes the
    # class of bug where an incremental df drifts from the postings it describes." I replaced it at
    # 16:0x because wholesale measured 106.7s against 62.0s. Then the covering index on
    # postings(term, chunk_id) landed at 19:4x and the measurement inverted:
    #   `[measured 19:50, real builds, same index, covering index present]`
    #     --wholesale-terms : terms_groupby       3.5s   (612 files reindexed, build 78.4s)
    #     affected-terms    : terms_affected_only 4.6s   (558 files reindexed, build 172.4s)
    # ⭐ WHOLESALE IS NOW FASTER **AND** SIMPLER **AND** CARRIES NO DRIFT RISK **AND** NEEDS NO
    # ORACLE TO GATE IT. Every reason for the affected-terms path was the 106.7s, and that number
    # was a missing index, not a query-shape problem. The complexity comes out.
    # ⚠ THE PATH ITSELF IS KEPT, not deleted: it is `--fast-terms`, still gated by
    # scripts/audit/terms_oracle_check.py, because a corpus whose postings table outgrows the
    # covering index may want it back and the measurement above is n=1 per arm.
    # ⭐ THE GENERAL LESSON, WRITTEN HERE BECAUSE IT COST A DAY: I optimized the QUERY SHAPE of a
    # phase whose cost was an INDEX. Three wrong guesses preceded it, one batching attempt measured
    # worse, and the A/B table I published was warm-cache and had to be withdrawn. The winning
    # change was five lines of schema.
    ap.set_defaults(fast_terms=False)
    ap.add_argument("--fast-terms", action="store_true", dest="fast_terms",
                    help="recompute df for AFFECTED TERMS ONLY instead of a full GROUP BY over "
                         "all 26M postings (106.7s of a 120.4s build). OFF BY DEFAULT until a "
                         "terms-table diff against a forced full rebuild comes back clean.")
    ap.add_argument("--allow-narrowing", action="store_true",
                    help="DELETE index rows for files this run's walk did not reach. Default is to KEEP them: a narrower walk is not evidence of deletion, and one caller forgetting the full widening flag set cost 7,240 files on 2026-09-04.")
    ap.add_argument("--provenance", action="append", default=[], metavar="PATH",
                    help="extra directory walked into the PROVENANCE tier (repeatable; absolute "
                         "paths reach another trunk). Off by default at retrieval like all "
                         "provenance -- reach it with `retrieve.py --tier provenance`.")
    ap.add_argument("--include", action="append", default=[], metavar="PATH",
                    help="extra directory or file to index (relative to the root unless "
                         "absolute); repeatable")
    ap.add_argument("--root", default=None, metavar="DIR",
                    help=f"trunk root to walk (default: this repo, {REPO})")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.root and not os.path.isdir(args.root):
        print(f"FAIL --root is not a directory: {args.root}", file=sys.stderr)
        return 2
    return build(args.db, args.embedder, args.force, args.quiet, args.include, args.root,
                 args.provenance, args.allow_narrowing, fast_terms=args.fast_terms)


if __name__ == "__main__":
    sys.exit(main())
