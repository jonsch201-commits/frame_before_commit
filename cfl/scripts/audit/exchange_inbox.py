#!/usr/bin/env python3
"""Unread cross-project mail — the consumer this channel never had.

WHY THIS EXISTS
---------------
On 2026-07-27 CFL sent three relays into herald-wiki's inbound and **never once read its outbox.**
Four messages sat unread, the oldest nine hours. Herald's own frontmatter said so plainly —
`delivered: UNDELIVERED — published to outbox, not carried. CFL is read-only from here.` It knew it
could not reach anyone and published anyway.

One of those four was the day's most consequential finding: `cc_corpus_gap.py` read `source_id:`
while 26 extracts declare `uuid:`, so every one of them fell through to LOST. CFL published a
29-session "permanently lost" registry on that output and dispatched a reconstruction against a
session with a real 12.67 MB transcript on disk. **Herald caught it by reading CFL's published claim
and checking it.** Corrected count: 3, none of them CFL.

The same session diagnosed `skills/intake/` as a **deposit-only queue with a producer rule and no
consumer rule**, wrote the consumer rule, and merged it — while running exactly that failure in this
channel. **Same defect, same day, in the thing being written about.**

This is Herald's own standard #7 turned back on CFL: *"a checker must audit its own domain."* Every
other instrument here checks the corpus. This one checks whether anyone is reading the mail.

THE THIRD TIME THIS SCRIPT COMMITTED ITS OWN FAILURE MODE (fixed 2026-08-08)
----------------------------------------------------------------------------
It printed, verbatim:

    [pro]  UNREAD 0   matched/stamped 0   possibly UNSENT 0

**Zero of zero of zero — and read by everyone as "the Pro channel is clean."** At that moment CFL's
own `exchange/inbound/` held **eight letters from Claude Professional**, two of them marked URGENT
and one a HIGH-severity correction to a published CFL claim (`pro-to-cfl-CORRECTION-your-audits-
cells-are-right-its-inference-is-false-2026-08-07.md`).

The cause was not a bad path and not a bad regex. **It was a delivery-convention assumption.** This
script only ever read the PEER'S OUTBOX — the pull model. Professional does not use it: its outbox
is genuinely empty (0 files, verified 2026-08-08) because Professional **pushes straight into our
`exchange/inbound/`**. Personal does both. Herald publishes to its outbox. Three peers, three
conventions, and the instrument knew one.

So `exchange/inbound/` — the directory whose entire purpose is mail addressed to us — **was read by
no instrument in this repo at all.** It was loaded into `ours_blob` as *evidence that we had
replied*, which is worse than ignoring it: a peer's letter was being counted as our own prose.

**A channel that is silent and a channel we cannot see must never print the same way.** That is now
enforced structurally by SAW-NOTHING below, not by anybody remembering it.

WHAT IT REPORTS
---------------
  UNREAD    — a message from the other project, in EITHER direction, that nothing we wrote refers
              to. The serious one. Printed once per channel as the headline `UNREAD n`.
  UNSENT    — something in our outbound path never copied to theirs. A relay written and not carried
              is identical, from their side, to one never written.
  credited  — we referred to it in our own prose, or (peer-outbox only) they stamped `delivered:`.

  Every channel additionally prints its DENOMINATORS: how many letters were examined in the peer's
  outbox and how many in our inbound. A verdict with no denominator is the thing this file exists
  to prevent.

TWO DIRECTIONS, AND WHY `delivered:` COUNTS IN ONLY ONE OF THEM
----------------------------------------------------------------
  peer-outbox (PULL)  — their `exchange/outbox/*.md`. A `delivered:` stamp here is the peer telling
                        us they carried it. Kept as a credit for continuity with every prior run of
                        this check, but **counted separately** so the number is never mistaken for
                        evidence that CFL read anything.
  our-inbound (PUSH)  — our `exchange/inbound/*.md`. Here `delivered:` proves only that it ARRIVED.
                        Claude Personal put the point in a filename on 2026-08-07:
                        *"delivered is not consumed."* So an inbound letter is credited on exactly
                        one test — **our own prose names it** — and never on a stamp the sender
                        wrote.

  `ours_blob` therefore EXCLUDES `exchange/inbound/`. A letter must not vouch for itself.
  (Verified 2026-08-08: excluding it changes no peer-outbox verdict — herald 0/8 and personal
  1/50 are identical either way — so this is one comparator, not two diverging ones.)

UNATTRIBUTED INBOUND
--------------------
An inbound file matching no declared peer's `inbound_pat` is reported under its own heading. It is
the same defect one level down: a letter nobody can even assign to a channel is a letter no channel
count will ever include.

WHY IT IS ADVISORY AND NOT BLOCKING
-----------------------------------
Unread mail is not a defect in this repo's own files, and a gate that blocks on the other project's
publishing cadence can never go green from here. That is the always-fires failure this repo
committed three separate times in two days. **Loud, every run, and never blocking.**

OUTPUT CONTRACT — `su_close.sh` PARSES THIS. Do not break it.
--------------------------------------------------------------
`scripts/audit/su_close.sh` reads two things out of this output with regexes:
    `channels +: ([0-9]+)`   and   `UNREAD (\\d+)`  (case-sensitive, SUMMED over all matches).
So: the literal token `UNREAD <n>` is emitted **exactly once per channel**, as the headline. Every
breakdown line uses lowercase `unread` deliberately, so the sum stays a sum and not a triple-count.
Change that and you silently change the SU's channel row.

Usage:
    python scripts/audit/exchange_inbox.py
    python scripts/audit/exchange_inbox.py --verbose    # name the file that credited each letter
    python scripts/audit/exchange_inbox.py --strict     # exit 1 on any UNREAD
    python scripts/audit/exchange_inbox.py --self-test  # the SAW-NOTHING guard, exercised

Exit: 0, or 1 under --strict when unread mail exists, or 2 when the peer tree is unreachable
      (WW-3, 2026-09-07: an
      UNKNOWN sweep does NOT change the exit code -- see the guard in main(); it emits the token
      `INBOX-VERDICT: UNKNOWN` instead, because this runs at SessionStart where exit 2 BLOCKS).
      ⛔ THE SECOND HALF OF THAT SENTENCE USED TO READ: "A SAW-NOTHING channel does NOT change the
      exit code — it is UNKNOWN, and this check is advisory by design. It is made loud in the output
      instead." The headline was made loud on 09-05 and the EXIT CODE was left at 0, so a caller
      reading the code got the reassuring answer the prose had just retracted. A fix that lands its
      message and not its signal is half a fix.
      ⭐ Still advisory: 2 means UNKNOWN, not "stop." A SAW-NOTHING channel among others examined is
      unchanged; only a sweep that examined NOTHING AT ALL returns 2 — the same rule the G: FAULT
      branch has always applied, arriving by a different door (`--no-g`, which is how SessionStart
      runs this).
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
import glob
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# ------------------------------------------------------------------------------------------------
# N: ROOTS — added 2026-09-02 (lane B-3). N:\ is the reliable read-only mail surface on this
# machine; G:\ fails byte-reads and its stat/ls lie under load. See probe_g() below for the fault
# detector and scan_n_roots() for the N:-side discovery. Both are read-only — this file writes
# nothing under N:\claude-corpus\ (read-only by contract) or N:\claude-gists-private\.
# ⛔ 'robocopy /MIR purge target' STRUCK 2026-09-05 -- UNSOURCED, and it was CFL's own invention;
# three trunks quoted it back as established fact. MEASURED from the PROCESS TABLE: the real job is
# N:ntigravity-hub\scripts\mirror_n_to_g.py / mirror_corpus_to_n.py, `robocopy ... /E /XO`,
# NO /MIR and NO /PURGE -- a deletion does NOT propagate. Read-only-by-contract stands unchanged.
# ------------------------------------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
# ⛔ WAS a hardcoded G: path — while REPO_ROOT on the line IMMEDIATELY ABOVE was already derived from
# __file__. Same file, same author, one derived and one hardcoded, four lines apart. That adjacency is
# the whole lesson: the correct pattern was in view and was not applied.
G_CARRIER = os.path.join(REPO_ROOT, "exchange", "CARRIER.md")
N_ROOT_DEFAULT = "N:/"
CORPUS_TRUNKS = ("cfl", "personal", "professional", "secretary", "antigravity", "ssp")
# Flat-file letter prefixes deposited directly in N:\claude-gists-private\.
N_GISTS_RE = re.compile(
    r"^(LETTER|RECEIPT|MANDATE|BROADCAST|ORDER|HANDOFF|FINDING|PROPOSAL|DIGEST|TICKET|RESCUED|"
    r"REPORT)-.*\.md$", re.I)


def probe_g(repo_root=REPO_ROOT, carrier_path=G_CARRIER, force_fault=False):
    """A REAL byte read of G:\\...\\exchange\\CARRIER.md, checked against `git show HEAD:...` in
    this clone. Not a stat, not an isdir — G:\\ is known to lie on both of those. Returns
    (ok: bool, msg: str).

    force_fault=True (wired from --fault-sim) short-circuits to the fault branch WITHOUT touching
    G:\\ at all — the flag exists so a session that must not read G:\\ can still exercise every
    downstream code path that depends on the fault state.
    """
    if force_fault:
        return False, "SIMULATED FAULT (--fault-sim)"
    try:
        with open(carrier_path, "rb") as fh:
            live = fh.read(4096)
    except OSError as e:
        return False, f"OSError reading G:\\ CARRIER: {e}"
    if not live:
        return False, "0 bytes read from G:\\ CARRIER (byte-read fault)"
    live_hash = hashlib.sha256(live).hexdigest()
    try:
        proc = subprocess.run(["git", "show", "HEAD:exchange/CARRIER.md"], cwd=repo_root,
                               capture_output=True, timeout=15)
    except Exception as e:
        return False, f"git show HEAD:exchange/CARRIER.md failed to run: {e}"
    if proc.returncode != 0:
        return False, f"git show HEAD:exchange/CARRIER.md rc={proc.returncode}: " \
                       f"{proc.stderr.decode(errors='ignore')[:200]}"
    git_hash = hashlib.sha256(proc.stdout[:4096]).hexdigest()
    if live_hash != git_hash:
        return False, f"sha256 mismatch — live={live_hash[:12]} git-HEAD={git_hash[:12]}"
    return True, f"match sha256={live_hash[:12]}"


def _n_file_record(abspath, rel):
    try:
        st = os.stat(abspath)
    except OSError as e:
        return {"path": rel, "abspath": abspath, "bytes": None, "mtime": None, "error": str(e)}
    return {"path": rel, "abspath": abspath, "bytes": st.st_size, "mtime": st.st_mtime,
            "error": None}


def scan_n_roots(n_base=N_ROOT_DEFAULT):
    """Everything mail-shaped under N:\\, read-only, in two shapes:

      (a) flat letters directly in N:\\claude-gists-private\\ matching N_GISTS_RE
      (b) N:\\claude-corpus\\<trunk>\\exchange\\{inbound,outbox}\\*.md for each declared trunk

    N:\\claude-corpus\\ is read-only by contract, never written here.
    ⛔ '/MIR mirror' STRUCK 2026-09-05 as UNSOURCED (see the note at the top of this file): the live
    job is `robocopy ... /E /XO`, which purges nothing. Read-only-by-contract stands unchanged.
    Returns a list of file records (see _n_file_record); a directory that does not exist is simply
    absent from the result, never an error -- trunks add mailboxes over time (see PEERS comments).
    """
    out = []
    gists_dir = os.path.join(n_base, "claude-gists-private")
    if os.path.isdir(gists_dir):
        for f in sorted(glob.glob(os.path.join(gists_dir, "*.md"))):
            name = os.path.basename(f)
            if N_GISTS_RE.match(name):
                out.append(_n_file_record(f, f"claude-gists-private/{name}"))
    corpus_base = os.path.join(n_base, "claude-corpus")
    for trunk in CORPUS_TRUNKS:
        for sub in ("inbound", "outbox"):
            d = os.path.join(corpus_base, trunk, "exchange", sub)
            if os.path.isdir(d):
                for f in sorted(glob.glob(os.path.join(d, "*.md"))):
                    name = os.path.basename(f)
                    out.append(_n_file_record(f, f"claude-corpus/{trunk}/exchange/{sub}/{name}"))
    return out

# DEAD, kept named rather than deleted so the next reader does not rediscover it as a candidate.
# Retired by Jon 2026-08-08 (quoted in full at the PEERS block below). Nothing points at this.
# It appears in the UNDECLARED census at every run, which is the honest state: a mailbox on disk
# that no channel claims. Do not re-add it as a peer.
DEAD_HERALD_WIKI = "G:/My Drive/Claude/Herald Wiki/herald-wiki/exchange"
HERE = "exchange"

# EVERY peer channel, not just the first one anyone built.
#
# Found 2026-08-03, and it is this instrument's own failure mode turned on itself: the
# script written to catch a deposit-only channel had exactly ONE channel hardcoded. A
# second peer — Claude Personal — opened on 2026-08-02 and accumulated EIGHT outbox files
# that this check reported nothing about, while printing "No unread mail." One of them,
# delivered 06:43 that morning, diagnosed a defect CFL had filed the day before.
#
# "No unread mail" scoped to one peer reads as "no unread mail." A checker that names its
# denominator cannot make that mistake; this one did not name it. Adding a peer here is
# the whole cost of adding a channel — if that ever stops being true, this list is wrong.
#
# `name_pat`    matches OUR outbound filenames for the UNSENT heuristic: a relay written and
#               never carried is, from their side, identical to one never written.
# `inbound_pat` matches THEIR letters as they land in OUR `exchange/inbound/`. Added 2026-08-08.
#               Without it the whole PUSH direction was invisible — see the docstring. A peer that
#               pushes rather than publishes had a permanently empty denominator here.
PEERS = [
    # herald WAS its own channel pointing at `Herald Wiki/herald-wiki/exchange`. It is NOT a
    # separate trunk and that tree is DEAD. Jon, 2026-08-08 /wake args 19:53, turn 8, recorded
    # verbatim at `[PERSONAL] wiki/sources/jon-messages/jon-1pm-rulings-2026-08-08.md:254-255`
    # -- typos his, and note the middle clause, which a relay of this quote had trimmed:
    #
    #     "for clarity, the Herald wiki is retired. We just have the personal wiki that you havr.
    #      Helped to make. You are the Herald coordinator of the personal wiki."
    #
    # So Herald is a ROLE INSIDE THE PERSONAL TRUNK, exactly as `soul` is -- and the 08-09 fix for
    # soul is the precedent: a role that names itself differently is a NEW PREFIX, NOT A NEW PEER.
    # Declaring it as its own channel pointed at a dead tree while the live mailbox
    # (`Claude Personal/exchange`, inbound 299 / outbox 206 `[relayed: Herald, measured 08-24]`)
    # was already covered by the `personal` row -- so every Herald letter was scored twice, once
    # against a mailbox nobody writes to.
    #
    # ⛔ AND THE HAZARD IS LIVE, NOT HISTORICAL. `Herald Wiki/.../exchange/inbound/` holds a file
    # named `00-DEAD-ADDRESS-DO-NOT-DEPOSIT-HERE.md` AND a letter deposited 2026-08-24, the same
    # morning. A warning inside the thing that has the problem is ANNOTATION, and the universal
    # constitution's own corollary is that annotation is not a disposition. Repointing the channel
    # is the disposition; the marker never was one.
    #
    # The dead tree is deliberately NOT deleted and deliberately NOT declared. It now surfaces in
    # `undeclared_trunks()` below as a mailbox no channel claims -- which is exactly what it is,
    # and is a truer statement than either declaring it or hiding it.
    {"key": "personal",
     "exchange": "G:/My Drive/Claude/Claude Personal/exchange",
     "name_pat": r"personal|cfl-to-personal|xc-|herald|cfl-reply|parity",
     # `personal-soul-…` is the same peer under a role prefix; both land here.
     # ⛔ AMENDED 2026-08-09 23:4x — `^personal` MISSED EVERY LETTER SOUL EVER SENT. soul is the
     # SSP coordinator INSIDE the Claude Personal trunk and signs its files `soul-to-cfl-…`, which
     # begins with neither `personal` nor any other declared prefix. On the night of the resident
     # launch that put FOUR soul letters — including the two carrying the launch result and Jon's
     # accepted condition — in NOBODY'S DENOMINATOR, while this checker printed a clean channel
     # table. ⭐ The comment one line above anticipated exactly this ("the same peer under a role
     # prefix") and then encoded only the prefix that had been seen. A role that names itself
     # differently is a new prefix, not a new peer.
     # 2026-08-24: `herald` joins as a THIRD role prefix on this one trunk, per Jon's 08-08
     # ruling quoted above. Three roles, one mailbox -- and that is the shape, not a workaround.
     "inbound_pat": r"^(personal|soul|herald)"},
    # Third peer, added 2026-08-07 — and the comment above predicted this exact omission.
    # Claude Professional has had `exchange/{inbound,outbox}` since at least 08-07 08:15 and
    # THREE files from Personal sitting in its inbound, while this checker printed "No unread
    # mail across 2 reachable channel(s)" — true of the two it knew about, and read by everyone
    # as "no unread mail." Pro's outbox is empty today, so nothing was missed YET; a channel
    # only watched after it first speaks is watched too late.
    # `name_pat` is deliberately tight: a bare `pro` would match proposal/program/protocol and
    # turn the UNSENT heuristic into noise.
    #
    # 2026-08-08: "Pro's outbox is empty today, so nothing was missed YET" was TRUE WHEN WRITTEN
    # AND WRONG WITHIN A DAY — and not because Pro started publishing. Pro's outbox is STILL
    # empty. Pro pushes directly into our `exchange/inbound/`, where eight of its letters sat
    # while this line reasoned about an outbox. The comment watched the wrong directory. That is
    # why `inbound_pat` exists and why SAW-NOTHING is now structural.
    {"key": "pro",
     "exchange": "G:/My Drive/Claude/Claude Professional/claude-professional/exchange",
     "name_pat": r"cfl-to-pro|-to-pro-|^pro-",
     # `pro-to-cfl-…` and `pro-to-personal-and-cfl-…` both begin `pro-`; the trailing hyphen keeps
     # `proposal-`/`program-`/`protocol-` out.
     "inbound_pat": r"^pro-"},
    # Fourth and fifth peers, added 2026-08-24 -- and this is the FOURTH time this list has been
    # short. Read the three comment blocks above: each records a peer discovered after it had
    # already been talking. `Claude Secretary/exchange` and `Claude SSP/claude-ssp/exchange` both
    # exist on disk; the Secretary has been a live correspondent for at least nine days and THIRTY
    # of its letters were sitting in our own inbound/ under the ORPHAN heading -- in nobody's
    # denominator -- while this check printed "channels : 3" and a confident number for each.
    #
    # The ORPHAN heading is what caught it, so the instrument worked. What did NOT work is that
    # the fix has always been "notice, then hand-add a row" -- a repair applied once per omission.
    # See `undeclared_trunks()` below for the repair applied once, full stop.
    {"key": "secretary",
     "exchange": "G:/My Drive/Claude/Claude Secretary/exchange",
     "name_pat": r"cfl-to-secretary|-to-secretary-|^secretary-",
     # The Secretary signs both `secretary-...` and `secretary-courier-...`; one prefix covers both.
     "inbound_pat": r"^secretary"},
    {"key": "ssp",
     "exchange": "G:/My Drive/Claude/Claude SSP/claude-ssp/exchange",
     "name_pat": r"cfl-to-ssp|-to-ssp-|^ssp-",
     "inbound_pat": r"^ssp-"},
    # Added 2026-08-28 on Professional's roster finding ("the courier roster is hand-enumerated
    # and nobody reads it"): Antigravity had been writing to the fleet since 08-25 and appeared
    # in NO trunk's channel list, so its letters were in nobody's denominator. Its letters sign
    # `LETTER-...-antigravity-...`; its exchange/ gained inbound/ on 08-28 14:47.
    {"key": "antigravity",
     "exchange": "G:/My Drive/Claude/Antigravity/exchange",
     "name_pat": r"cfl-to-antigravity|-to-antigravity-|antigravity-to-|-antigravity-",
     "inbound_pat": r"antigravity"},
]

# ==========================================================================================
# N:-LIVE RESOLUTION FOR THE PEER CHANNELS -- added 2026-09-12 12:5x CDT, and the measurement is
# the reason. Every "exchange" value above is a G: path. THE FLEET MOVED TO N: ON 2026-09-02.
# `[measured 2026-09-12 12:4x, this file's own output]` the G: byte-read probe FAULTS, so all five
# peer channels rendered `UNKNOWN - 0 channels examined` and the verdict line read
# `INBOX-VERDICT: UNKNOWN (G: fault; N: roots readable)`. That is honest and it is not a reading.
#
# What was in nobody's denominator while it printed that, measured by `ls` on the live trees:
#   personal      N:/claude-personal/exchange      inbound 1438  outbox 333
#   professional  N:/claude-professional/exchange  inbound 1404  outbox 305
#   secretary     N:/claude-secretary/exchange     inbound 1341  outbox 138
#   ssp           N:/claude-ssp/exchange           inbound  148  outbox   0
#   antigravity   N:/antigravity-hub/exchange      inbound  517  outbox 670
# 4,848 inbound and 1,446 outbox letters, unreadable to this instrument since the move.
#
# THIS IS THE SAME DEFECT AS `session_store_capture.py`'s hardcoded G: project key, found this
# morning, and the SAME as `drain_cfl_backlog.py:23` in Antigravity -- a path written when the tree
# lived somewhere else, which does not error and does not narrow, it just stops seeing.
# ⛔ LIVE-PLUS-LEGACY, NEVER LIVE-INSTEAD-OF-LEGACY: the G: value is KEPT on the row as
# `exchange_legacy` and printed, never deleted. Jon: "Yeah no deletion. All must be recoverable."
# ⚠️ A row whose N: path does NOT exist keeps its G: value and is flagged, so a missing trunk reads
# as UNKNOWN rather than as a silently-skipped channel.
N_LIVE_EXCHANGE = {
    "personal":    "N:/claude-personal/exchange",
    "pro":         "N:/claude-professional/exchange",
    "secretary":   "N:/claude-secretary/exchange",
    "ssp":         "N:/claude-ssp/exchange",
    "antigravity": "N:/antigravity-hub/exchange",
}


def resolve_live_exchange(peers, live_map=None):
    """Repoint each peer at its N: mailbox when that mailbox EXISTS; keep the G: path on the row.

    Returns (peers, notes) -- notes is one line per row saying which root it resolved to, so the
    resolution is printed rather than assumed. A resolver whose choice is invisible is the same
    defect one layer up.
    """
    live_map = N_LIVE_EXCHANGE if live_map is None else live_map
    notes = []
    for p_ in peers:
        legacy = p_.get("exchange")
        cand = live_map.get(p_.get("key"))
        if cand and os.path.isdir(cand):
            p_["exchange"] = cand
            p_["exchange_legacy"] = legacy
            notes.append("  [%s] resolved to N: LIVE %s  (legacy kept: %s)" % (p_["key"], cand, legacy))
        elif cand:
            notes.append("  [%s] UNKNOWN: N: path declared but absent (%s) -- staying on %s"
                         % (p_["key"], cand, legacy))
        else:
            notes.append("  [%s] no N: path declared -- staying on %s" % (p_["key"], legacy))
    return peers, notes


PEERS, PEER_RESOLUTION_NOTES = resolve_live_exchange(PEERS)

# Where a sibling trunk's mailbox can live on this machine. Two depths because the trunks are not
# uniform: `Claude Personal/exchange` is one level down, `Claude Professional/claude-professional/
# exchange` is two -- the repo sits inside the trunk folder.
TRUNK_GLOBS = ("G:/My Drive/Claude/*/exchange", "G:/My Drive/Claude/*/*/exchange")


def _norm(p_):
    return os.path.normcase(os.path.abspath(p_)).replace("\\", "/").rstrip("/")


def undeclared_trunks(peers, ours, globs=TRUNK_GLOBS):
    """Every `exchange/` directory on disk that NO declared peer points at.

    WHY THIS EXISTS -- the second-order version of a defect this file already records three times
    ---------------------------------------------------------------------------------------------
    PEERS has been short four times (2026-08-03 herald-only, 08-07 pro, 08-09 soul's prefix,
    08-24 secretary + ssp). Every one was found the same way: somebody read an ORPHAN list, or a
    letter went unanswered long enough to hurt. Each fix added the row that had just been missed.

    That is a first-order correction: it reduces the error that was measured and does nothing
    about the next one, because the next peer has a name nobody has typed yet. A list that has
    been wrong four times does not need a fifth entry -- it needs to stop being the only place
    trunk membership is recorded.

    So the FILESYSTEM is the denominator. A trunk that opens a mailbox becomes visible here the
    moment it exists, with nobody remembering anything. PEERS is then checked AGAINST that
    denominator instead of standing in for it.

    BOUNDS, all three parts:
      1. NOT REVIEWED: whether an undeclared mailbox is a live correspondent, a retired tree, or
         a scratch directory. This function cannot tell those apart.
      2. WHY: liveness is a judgment about intent, and a directory carries no intent.
      3. RESULTING LIMITATION: every hit is a PROMPT TO DECIDE, never a finding, and never an
         instruction to add a peer. Some of these SHOULD stay undeclared -- the XC trees hold
         Jon's financial records under a standing no-remote rule, and routing mail through them
         is not a call this script may make.
    """
    declared = {_norm(p_["exchange"]) for p_ in peers}
    declared.add(_norm(ours))
    found = {}
    for g in globs:
        for d in glob.glob(g):
            if os.path.isdir(d):
                found[_norm(d)] = d.replace("\\", "/")
    return sorted(v for k, v in found.items() if k not in declared)


def fm_field(path, field):
    try:
        head = open(path, encoding="utf-8", errors="ignore").read(4000)
    except OSError:
        return ""
    m = re.search(rf"^{field}:\s*(.+)$", head, re.M)
    return m.group(1).strip() if m else ""


def _referenced(stem, ours_blob):
    """Did anything WE wrote name this message? The only credit an inbound letter can earn."""
    return stem in ours_blob or stem.replace("-", " ") in ours_blob


def _crediting_files(stem, our_files):
    """Which of our files name it — so `--verbose` can show the receipt, not just assert one."""
    return [os.path.basename(p) for p, t in our_files if stem in t or stem.replace("-", " ") in t]


def scan_peer(peer, our_exchange, ours_blob, our_files):
    """Returns a dict for one peer, or None if its outbox is unreachable.

    BOTH directions. Until 2026-08-08 this read only the peer's outbox, and a peer that pushes
    into our inbound instead of publishing to its own outbox was invisible with a zero denominator.
    """
    peer_out = os.path.join(peer["exchange"], "outbox")
    peer_in = os.path.join(peer["exchange"], "inbound")
    if not os.path.isdir(peer_out):
        return None

    # ---- direction 1: PULL. Their outbox. -------------------------------------------------
    ob_unread, ob_by_stamp, ob_by_ref, ob_total = [], 0, 0, 0
    for f in sorted(glob.glob(os.path.join(peer_out, "*.md"))):
        name = os.path.basename(f)
        if name.lower() == "readme.md":
            continue
        ob_total += 1
        stem = name[:-3]
        delivered = fm_field(f, "delivered")
        # Two ways an OUTBOX message counts as consumed: they stamped it, or we referenced it.
        # The stamp is kept separate — it is their claim of carriage, not our claim of reading.
        if delivered and "UNDELIVERED" not in delivered.upper():
            ob_by_stamp += 1
        elif _referenced(stem, ours_blob):
            ob_by_ref += 1
        else:
            ob_unread.append((name, fm_field(f, "date"), fm_field(f, "title")[:64]))

    # ---- direction 2: PUSH. Our own inbound. ----------------------------------------------
    # No stamp credit here. `delivered:` on a letter sitting in our inbound proves it arrived and
    # says nothing about whether anyone read it.
    ib_unread, ib_credited, ib_total = [], 0, 0
    for f in sorted(glob.glob(os.path.join(our_exchange, "inbound", "*.md"))):
        name = os.path.basename(f)
        if name.lower() == "readme.md":
            continue
        if not re.search(peer["inbound_pat"], name, re.I):
            continue
        ib_total += 1
        stem = name[:-3]
        if _referenced(stem, ours_blob):
            ib_credited += 1
        else:
            ib_unread.append((name, fm_field(f, "date"), fm_field(f, "title")[:64]))

    # ---- our outbound, never carried ------------------------------------------------------
    unsent, out_total = [], 0
    for f in sorted(glob.glob(os.path.join(our_exchange, "*.md"))):
        name = os.path.basename(f)
        if not re.search(peer["name_pat"], name, re.I):
            continue
        out_total += 1
        # Did any file in their inbound come from this one? Match on the distinctive date-stem.
        stem = re.sub(r"\.md$", "", name)
        carried = any(stem.split("-")[-3:] == os.path.basename(g)[:-3].split("-")[-3:]
                      for g in glob.glob(os.path.join(peer_in, "*.md")))
        if not carried:
            unsent.append(name)

    return {
        "ob_unread": ob_unread, "ob_by_stamp": ob_by_stamp, "ob_by_ref": ob_by_ref,
        "ob_total": ob_total,
        "ib_unread": ib_unread, "ib_credited": ib_credited, "ib_total": ib_total,
        "unsent": unsent, "out_total": out_total,
        # THE DENOMINATOR. Zero here means SAW NOTHING, which is UNKNOWN and not clean.
        "seen_total": ob_total + ib_total + out_total,
    }


def load_our_prose(our_exchange):
    """Everything WE wrote under `exchange/`, EXCLUDING `inbound/`.

    Excluding inbound is the point: a peer's own letter must never be counted as evidence that we
    replied to it. Verified 2026-08-08 that this exclusion changes NO peer-outbox verdict (herald
    0/8, personal 1/50 either way), so there is exactly one blob and one comparator here.
    """
    inbound_prefix = os.path.normpath(os.path.join(our_exchange, "inbound")).replace("\\", "/")
    files, blob = [], ""
    for f in glob.glob(os.path.join(our_exchange, "**", "*.md"), recursive=True):
        if os.path.normpath(f).replace("\\", "/").startswith(inbound_prefix):
            continue
        try:
            t = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        files.append((f, t))
        blob += t
    return blob, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--peer-exchange", help="Scan ONLY this peer path (default: every peer in PEERS)")
    ap.add_argument("--our-exchange", default=HERE)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--verbose", action="store_true",
                    help="name the file that credited each read letter — a receipt, not an assertion")
    ap.add_argument("--self-test", action="store_true", dest="self_test",
                    help="exercise the SAW-NOTHING guard and the two directions on a fixture")
    ap.add_argument("--fault-sim", action="store_true", dest="fault_sim",
                    help="force the G:\\ byte-read fault branch without touching G:\\ at all")
    ap.add_argument("--no-g", action="store_true", dest="no_g",
                    help="skip every G:\\-rooted PEER channel entirely (no probe, no scan); "
                         "N:\\ roots still scan")
    ap.add_argument("--roots", default=None,
                    help="override the N:\\ root base (default N:/) — expects "
                         "<root>/claude-gists-private and "
                         "<root>/claude-corpus/<trunk>/exchange/{inbound,outbox}")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    peers = ([{"key": "custom", "exchange": a.peer_exchange,
               "name_pat": r".*", "inbound_pat": r".*"}]
             if a.peer_exchange else PEERS)

    ours_blob, our_files = load_our_prose(a.our_exchange)

    print("=== CROSS-PROJECT MAIL — is anyone reading it? ===\n")
    print(f"  ours     : {a.our_exchange}")
    print(f"  channels : {len(peers)} — {', '.join(p['key'] for p in peers)}")
    print(f"  our prose: {len(our_files)} file(s) under {a.our_exchange}/ (inbound/ excluded — "
          f"a letter must not vouch for itself)\n")

    # ---- G:\ FAULT DETECTION -- must happen BEFORE anything below touches a G:-rooted path. -----
    g_status, g_msg = "OK", ""
    if a.peer_exchange:
        g_status = "N/A"          # --peer-exchange is the pre-existing single-peer test mode
    elif a.no_g:
        g_status, g_msg = "SKIPPED", "--no-g"
    else:
        g_ok, g_msg = probe_g(force_fault=a.fault_sim)
        g_status = "OK" if g_ok else "FAULT"

    if g_status == "FAULT":
        print(f"  ⛔ G:\\ BYTE-READ FAULT — {g_msg}")
        print("     Every G:\\-rooted channel below prints UNKNOWN(fault); its denominator is")
        print("     WITHHELD (no `UNREAD n` token — su_close.sh must not sum a fault as zero).")
        print("     N:\\ roots (claude-gists-private, claude-corpus) are scanned regardless —")
        print("     that is the whole reason they exist.\n")
    elif g_status == "SKIPPED":
        print(f"  ℹ️  G:\\ channels SKIPPED ({g_msg}). N:\\ roots still scan.\n")
    elif g_status == "OK":
        print(f"  G:\\ CARRIER probe: {g_msg}\n")

    # THE DENOMINATOR CHECK. Printed BEFORE the per-channel numbers, because every number below
    # is scoped to the declared list, and a reader who sees the numbers first has already formed
    # the impression this block exists to correct.
    if not a.peer_exchange and g_status == "OK":
        _und = undeclared_trunks(peers, a.our_exchange)
        if _und:
            print(f"  UNDECLARED TRUNK MAILBOXES -- {len(_und)} exchange/ director(ies) exist on")
            print("     disk that NO declared channel points at. Every count below EXCLUDES them.")
            for _d in _und:
                print(f"     UNDECLARED  {_d}")
            print("     A prompt to decide, not a finding: some should stay undeclared (the XC")
            print("     trees hold Jon's financial records under a standing no-remote rule).")
            print("     Decide each -- declare it, or record why it is not a channel.\n")
        else:
            print("  Every exchange/ directory on disk is claimed by a declared channel.\n")
    elif not a.peer_exchange:
        print(f"  UNDECLARED TRUNK MAILBOXES check skipped -- G:\\ status is {g_status}, and that")
        print("     scan globs G:\\ paths too.\n")

    total_unread, unreachable, saw_nothing = 0, [], []
    not_examined = []  # SKIPPED or FAULT peers -- excluded from the "N EXAMINED channel(s)" count
    attributed_inbound = set()
    g_seen_stems = set()
    # Local (not G:\) — always safe to read regardless of G status.
    for _f in glob.glob(os.path.join(a.our_exchange, "inbound", "*.md")):
        g_seen_stems.add(os.path.splitext(os.path.basename(_f))[0])

    for p in peers:
        # THE G: GATE IS PER-ROW, NOT GLOBAL -- corrected 2026-09-12 12:5x CDT, and the first run
        # of the N:-live repointing above is what exposed it. This block tested g_status with NO
        # reference to the row own path, so ONE flag about ONE DRIVE suppressed EVERY channel.
        # After the rows were repointed at N:, --no-g still printed SKIPPED for all five and the
        # verdict still read "0 channels examined" -- the fix defeated by the gate, and the output
        # was byte-indistinguishable from before the fix.
        # Same shape as the defect it gates: a condition written when every peer was G:-rooted and
        # left in place after they moved. A drive-scoped flag must test the DRIVE, not the row.
        _is_g = str(p.get("exchange", "")).replace(chr(92), "/").upper().startswith("G:")
        if _is_g and g_status == "SKIPPED":
            not_examined.append(p["key"])
            print(f"  [{p['key']}] SKIPPED (--no-g) — not scanned, no UNREAD token emitted.\n")
            continue
        if _is_g and g_status == "FAULT":
            not_examined.append(p["key"])
            print(f"  [{p['key']}] UNKNOWN(fault) — G:\\ byte-read fault ({g_msg}); "
                  f"denominator WITHHELD, not scanned.\n")
            continue

        r = scan_peer(p, a.our_exchange, ours_blob, our_files)
        if r is None:
            unreachable.append(p)
            print(f"  [{p['key']}] ERROR: outbox unreachable: {p['exchange']}/outbox")
            print("            An unreachable peer is UNKNOWN, not empty.\n")
            continue

        for _sub in ("outbox", "inbound"):
            for _f in glob.glob(os.path.join(p["exchange"], _sub, "*.md")):
                g_seen_stems.add(os.path.splitext(os.path.basename(_f))[0])

        for n, _, _ in r["ib_unread"]:
            attributed_inbound.add(n)
        for f in glob.glob(os.path.join(a.our_exchange, "inbound", "*.md")):
            if re.search(p["inbound_pat"], os.path.basename(f), re.I):
                attributed_inbound.add(os.path.basename(f))

        unread = r["ob_unread"] + r["ib_unread"]
        credited = r["ob_by_stamp"] + r["ob_by_ref"] + r["ib_credited"]
        total_unread += len(unread)

        # ---- SAW NOTHING. The whole reason this file was rewritten. ------------------------
        # A channel with an empty denominator is UNKNOWN. It must not be able to render in the
        # same shape as a channel that was examined and found quiet.
        if r["seen_total"] == 0:
            saw_nothing.append(p["key"])
            print(f"  ⚠️  [{p['key']}] SAW NOTHING — 0 items total. This is UNKNOWN, not clean.")
            print(f"      UNREAD 0   credited 0   possibly UNSENT 0   "
                  f"<- all three are vacuous, not reassuring")
            print(f"      denominators: peer-outbox 0 · our-inbound 0 · our-outbound 0")
            print(f"      peer tree : {p['exchange']}")
            print(f"      inbound_pat /{p['inbound_pat']}/   name_pat /{p['name_pat']}/")
            print(f"      Either this peer has never said anything, or this instrument cannot see")
            print(f"      where it says it. On 2026-08-08 it was the second: Pro's outbox really")
            print(f"      was empty and eight of its letters were in our own inbound. VERIFY BY HAND.\n")
            continue

        print(f"  [{p['key']}]  UNREAD {len(unread)}   matched/stamped {credited}   "
              f"possibly UNSENT {len(r['unsent'])}")
        # Lowercase `unread` below is load-bearing — see the OUTPUT CONTRACT in the docstring.
        print(f"      denominators: peer-outbox {r['ob_total']} letters "
              f"({len(r['ob_unread'])} unread / {r['ob_by_ref']} we-named / "
              f"{r['ob_by_stamp']} they-stamped) · "
              f"our-inbound {r['ib_total']} letters "
              f"({len(r['ib_unread'])} unread / {r['ib_credited']} we-named) · "
              f"our-outbound {r['out_total']} files")
        for n, d, t in r["ob_unread"]:
            print(f"      UNREAD  [their outbox]  {d or '(no date)'}  {n}")
            if t:
                print(f"                {t}")
        for n, d, t in r["ib_unread"]:
            print(f"      UNREAD  [our inbound ]  {d or '(no date)'}  {n}")
            if t:
                print(f"                {t}")
        if a.verbose:
            for f in sorted(glob.glob(os.path.join(a.our_exchange, "inbound", "*.md"))):
                nm = os.path.basename(f)
                if not re.search(p["inbound_pat"], nm, re.I):
                    continue
                if any(nm == u[0] for u in r["ib_unread"]):
                    continue
                src = _crediting_files(nm[:-3], our_files)
                print(f"      credited [our inbound ]  {nm}")
                print(f"                by: {', '.join(src[:3]) or '(stem match in blob)'}")
        for n in r["unsent"]:
            print(f"      UNSENT? {n}")
        print()

    # ---- inbound mail belonging to no declared channel ------------------------------------
    if not a.peer_exchange:
        all_inbound = {os.path.basename(f)
                       for f in glob.glob(os.path.join(a.our_exchange, "inbound", "*.md"))
                       if os.path.basename(f).lower() != "readme.md"}
        # ⭐ SPLIT OUT OUR OWN OUTBOUND, added 2026-08-09 23:4x. `exchange/inbound/` holds BOTH
        # directions: peers push their letters in, and CFL drafts its own there before copying them
        # to the peers' trees. A `cfl-to-…` file is therefore NOT an unattributed inbound letter —
        # it is ours, and calling it an ORPHAN told the reader to "add an inbound_pat" for a channel
        # that would mean "mail from ourselves".
        # ⛔ WHY THIS MATTERED RATHER THAN BEING COSMETIC: the orphan list went 3 → 9 in one night
        # and FIVE of the nine were CFL's own letters. A list that grows mostly with our own files
        # reads as a worsening backlog and gets ignored, which is precisely how the three REAL
        # orphans underneath it stayed unfixed. ⚠️ They are still printed — moved, never hidden.
        ours_pat = re.compile(r"^cfl-to-", re.I)
        own = sorted(n for n in all_inbound - attributed_inbound if ours_pat.search(n))
        orphans = sorted(n for n in all_inbound - attributed_inbound if not ours_pat.search(n))
        if own:
            print(f"  ℹ️  OUR OWN OUTBOUND drafted in inbound/ — {len(own)} file(s). Not unread mail,")
            print("      not a missing channel. Delivery to the peer trees is a separate act — see E-3.")
            for n in own:
                print(f"      OURS    {n}")
            print()
        if orphans:
            print(f"  ⚠️  UNATTRIBUTED INBOUND — {len(orphans)} letter(s) in "
                  f"{a.our_exchange}/inbound/ match NO declared channel.")
            print("      They are in nobody's denominator, so no channel count will ever include")
            print("      them. Add an `inbound_pat` (or a peer) — that is the whole cost.")
            for n in orphans:
                print(f"      ORPHAN  {n}")
            print()

    # ---- INBOUND-N -- letters found ONLY on N:\, invisible to every G:-rooted channel above ----
    n_base = a.roots if a.roots else N_ROOT_DEFAULT
    n_records = scan_n_roots(n_base)
    _n_gists_dir = os.path.join(n_base, "claude-gists-private")
    _n_corpus_dir = os.path.join(n_base, "claude-corpus")
    n_readable = os.path.isdir(_n_gists_dir) or os.path.isdir(_n_corpus_dir)
    inbound_n = []
    for rec in n_records:
        if rec["error"]:
            n_readable = False
            continue
        stem = os.path.splitext(os.path.basename(rec["path"]))[0]
        # Dedup is against a G:-rooted CHANNEL RESULT only -- a filename appearing incidentally
        # inside our own prose (e.g. an `in_reply_to:` citation) is not the same claim as "a
        # declared channel already scanned this letter" and must not suppress it here.
        if stem in g_seen_stems:
            continue
        inbound_n.append(rec)

    if inbound_n:
        print(f"  INBOUND-N — {len(inbound_n)} letter(s) exist on N:\\ that no G:-rooted channel")
        print("      result and no prose of ours names. N:\\claude-corpus\\ is read-only (robocopy")
        print("      mirror, /E /XO -- purges nothing); nothing here was written by this scan.")
        for rec in sorted(inbound_n, key=lambda r: r["path"]):
            ts = (datetime.fromtimestamp(rec["mtime"]).strftime("%Y-%m-%d %H:%M:%S")
                  if rec["mtime"] else "(no mtime)")
            if rec["bytes"] == 0:
                print(f"      HOLLOW  {rec['path']}  0 B  {ts}  <- zero-byte, never render as read")
            else:
                print(f"      N-ONLY  {rec['path']}  {rec['bytes']} B  {ts}")
        print()
    elif not n_records:
        print("  INBOUND-N — 0 file(s) found under N:\\claude-gists-private\\ or "
              "N:\\claude-corpus\\*/exchange/{inbound,outbox}/. UNKNOWN whether that means clean "
              "or unreachable — verify the roots exist.\n")
    else:
        print(f"  INBOUND-N — {len(n_records)} file(s) examined on N:\\, all already accounted for "
              "by a G:-rooted channel result or our own prose.\n")

    # ⛔ BOUND BEFORE THE BRANCH, 2026-09-07: `seen` was assigned ONLY in the else-arm below, so the
    # WW-3 exit-code guard raised UnboundLocalError on the unread path -- caught by this file's own
    # --self-test on the first run after the change, which is the argument for having one.
    seen = len(peers) - len(unreachable) - len(saw_nothing) - len(not_examined)
    if total_unread:
        print("  A message sitting unread is indistinguishable, from their side, from one")
        print("  nobody wrote. Read them before building anything else — on 2026-07-27 the")
        print("  unread pile contained a correction to a published CFL claim, and on")
        print("  2026-08-08 the Pro pile contained another one while this check printed 0/0/0.")
    else:
        # ⛔ WW-3, 2026-09-05. This printed "No unread mail across 0 EXAMINED channel(s)"
        # from the SessionStart hook, which runs this with --no-g -- so every peer is
        # SKIPPED, seen==0, and a sweep that examined NOTHING rendered as a clean inbox.
        # The disclaimer lines below were correct and nobody reads past a green headline.
        # ⭐ An empty sweep and a clean sweep print the same bytes unless one of them says
        # so -- and here the EMPTY one printed the reassuring sentence. UNKNOWN dominates.
        if seen == 0:
            print("  UNKNOWN — 0 channels examined. THIS IS NOT A CLEAN INBOX; it is no")
            print("  measurement at all. 'I did not look' must never render as 'nothing is there.'")
        else:
            print(f"  No unread mail across {seen} EXAMINED channel(s).")
        if saw_nothing:
            print(f"  This statement does NOT cover {len(saw_nothing)} SAW-NOTHING channel(s): "
                  f"{', '.join(saw_nothing)}.")
        if not_examined:
            print(f"  This statement does NOT cover {len(not_examined)} SKIPPED/UNKNOWN(fault) "
                  f"channel(s): {', '.join(not_examined)}.")

    if saw_nothing:
        print()
        print(f"  ⚠️  {len(saw_nothing)} channel(s) had a ZERO denominator: {', '.join(saw_nothing)}.")
        print("      Nothing above is a clean bill of health for them.")

    if unreachable:
        return 2
    if g_status == "FAULT":
        # G:\ is unreadable. Exit 0 only if N:\ roots picked up the slack; otherwise this run saw
        # nothing reliable at all and the caller must treat the result as UNKNOWN, not clean.
        # ⛔ AND THIS BRANCH RETURNED BEFORE THE VERDICT TOKEN WAS EMITTED -- found by running the
        # CONTROL rather than only the arm I had changed. G: is faulting right now, so the "full
        # sweep" case takes this path, printed no `INBOX-VERDICT:` line, and my own control read as
        # a pass because I grepped for the token and accepted its absence as "the other branch".
        # ⚠️ A TOKEN THAT IS EMITTED ON SOME RETURN PATHS IS A TOKEN A PARSER CANNOT TRUST: its
        # absence would mean either UNKNOWN-not-reached or this-branch, and those are the two things
        # it exists to distinguish.
        print("  INBOX-VERDICT: %s" % ("UNKNOWN (G: fault; N: roots readable)" if n_readable
                                       else "UNKNOWN (G: fault; nothing reliable seen)"))
        return 0 if n_readable else 2
    # ⛔ WW-3, SECOND HALF, 2026-09-07. The headline was fixed on 09-05 -- a sweep that examined
    # nothing now prints "UNKNOWN — 0 channels examined. THIS IS NOT A CLEAN INBOX" -- but the
    # EXIT CODE still said 0, and a caller that reads the code rather than the prose got the
    # reassuring answer the prose had just retracted. The ticket asked for both halves and only
    # one shipped; a fix that lands its message and not its signal is half a fix.
    # ⭐ The precedent is four lines up and it is this function's own: the G: FAULT branch already
    # returns 2 when nothing reliable was seen, on the stated grounds that "the caller must treat
    # the result as UNKNOWN, not clean." SKIPPED is the same situation arriving by a different
    # door -- --no-g is exactly how the SessionStart hook runs this -- so it gets the same answer.
    # ⚠️ AND I ALMOST MEASURED THIS WRONG THE SAME WAY I WAS CORRECTED THIS MORNING: my first read
    # of the exit code was `... | tail -6; echo $?`, which reports TAIL's status. Professional
    # caught that exact shape in ticket_id_unique.py today. Unpiped, it was 0.
    # ⛔ AND THE EXIT CODE IS THE WRONG INSTRUMENT HERE -- MEASURED, AFTER I HAD ALREADY WRITTEN
    # `return 2` AND VERIFIED IT WORKED. WW-3's on-silence asked for the exit code to reflect
    # UNKNOWN. It cannot, and shipping it would have broken every session in this trunk:
    #   * `.claude/settings.json:180` runs this at SessionStart as
    #     `py_closed.sh scripts/audit/exchange_inbox.py --no-g` -- the exact flag that examines
    #     zero channels, so the UNKNOWN branch is the DEFAULT path at every session open.
    #   * Per Claude Code hook semantics EXIT 2 BLOCKS THE TRIGGERING ACTION.
    #   * `py_closed.sh`'s header says "a faulted script there degrades to exit 1 (a visible
    #     non-blocking error) rather than a block." ⛔ ITS LAST LINE IS `exec python "$script" "$@"`.
    #     An exec REPLACES the process: the script's exit code IS the hook's exit code, verbatim.
    #     The degradation the comment promises applies to the WRAPPER'S OWN faults (unreadable
    #     script, zero bytes) and never to the child's status.
    # ⭐ A COMMENT DESCRIBING A SAFETY PROPERTY THE CODE BELOW IT DOES NOT HAVE -- the fifth
    # instance today of a stored claim outliving its subject, and the first one that would have
    # cost a fleet-wide outage rather than a wrong number. I trusted it for exactly as long as it
    # took to read the last line of the file.
    # ✅ SO THE SIGNAL GOES IN THE OUTPUT, NOT THE STATUS: `INBOX-VERDICT: UNKNOWN` is emitted as a
    # greppable token beside the prose, parseable by `su_close.sh` the way it already parses
    # `UNREAD <n>`, and exit stays 0 because THIS CHECK IS ADVISORY BY DESIGN and an advisory that
    # can block is not advisory. Exit 1 was not available either -- it already means "unread mail
    # exists under --strict", and overloading it would make two different findings indistinguishable.
    if seen == 0:
        print("  INBOX-VERDICT: UNKNOWN (0 channels examined)")
    else:
        print(f"  INBOX-VERDICT: EXAMINED {seen} channel(s)")
    return 1 if (total_unread and a.strict) else 0


# --------------------------------------------------------------------------------------------
# SELF-TEST — the guard exists to stop a vacuous zero reading as clean, so the guard itself must
# be exercised against a vacuous zero. A property asserted in a docstring and never run is how
# this repo has been burned before.
# --------------------------------------------------------------------------------------------

def self_test():
    import tempfile
    tmp = tempfile.mkdtemp()

    def w(path, text=""):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    ours = os.path.join(tmp, "ours")
    os.makedirs(os.path.join(ours, "inbound"))

    # A peer that PUBLISHES (herald-shaped): one outbox letter, unreferenced.
    pub = os.path.join(tmp, "pub", "exchange")
    w(os.path.join(pub, "outbox", "pub-to-cfl-a-2026-01-01.md"), "---\ndate: 2026-01-01\n---\nx\n")
    os.makedirs(os.path.join(pub, "inbound"), exist_ok=True)

    # A peer that PUSHES (pro-shaped): EMPTY outbox, two letters in OUR inbound.
    push = os.path.join(tmp, "push", "exchange")
    os.makedirs(os.path.join(push, "outbox"))
    os.makedirs(os.path.join(push, "inbound"))
    w(os.path.join(ours, "inbound", "push-to-cfl-urgent-2026-01-02.md"), "---\ndate: 2026-01-02\n---\nx\n")
    w(os.path.join(ours, "inbound", "push-to-cfl-answered-2026-01-03.md"), "---\ndate: 2026-01-03\n---\nx\n")
    # ...one of which we replied to, by name.
    w(os.path.join(ours, "cfl-reply.md"), "we read push-to-cfl-answered-2026-01-03 and acted\n")

    # A peer that is genuinely silent everywhere: the SAW-NOTHING case.
    silent = os.path.join(tmp, "silent", "exchange")
    os.makedirs(os.path.join(silent, "outbox"))
    os.makedirs(os.path.join(silent, "inbound"))

    # An inbound letter belonging to no declared channel.
    w(os.path.join(ours, "inbound", "stranger-to-cfl-2026-01-04.md"), "---\n---\nx\n")
    # ⭐ ADDED 2026-08-09 23:4x with the two fixes they test — a check nobody has watched pass AND
    # fail is a check nobody has tested. Both of these were reported as ORPHANs before tonight.
    #   1. A peer writing under a ROLE PREFIX (`soul-`) instead of its trunk name. Four real letters
    #      sat outside every denominator this way on the night of the launch.
    #   2. OUR OWN outbound, drafted in inbound/ before delivery. Five of the nine orphans were ours.
    w(os.path.join(ours, "inbound", "alias-to-cfl-2026-01-05.md"), "---\n---\nx\n")
    w(os.path.join(ours, "inbound", "cfl-to-push-reply-2026-01-06.md"), "---\n---\nx\n")

    peers = [
        {"key": "pub", "exchange": pub, "name_pat": r"zzz-never", "inbound_pat": r"^pub-"},
        # `alias` is the same peer under a role prefix — the soul-vs-personal case, in miniature.
        {"key": "push", "exchange": push, "name_pat": r"zzz-never", "inbound_pat": r"^(push|alias)-"},
        {"key": "silent", "exchange": silent, "name_pat": r"zzz-never", "inbound_pat": r"^silent-"},
    ]
    blob, files = load_our_prose(ours)
    fails = []

    r_pub = scan_peer(peers[0], ours, blob, files)
    if len(r_pub["ob_unread"]) != 1:
        fails.append(f"pub: expected 1 outbox unread, got {len(r_pub['ob_unread'])}")
    if r_pub["seen_total"] == 0:
        fails.append("pub: seen_total must be non-zero (it has an outbox letter)")

    r_push = scan_peer(peers[1], ours, blob, files)
    if r_push["ob_total"] != 0:
        fails.append(f"push: outbox should be empty, got {r_push['ob_total']}")
    # 3, not 2, since 2026-08-09: the role-prefixed letter belongs to this same peer.
    if r_push["ib_total"] != 3:
        fails.append(f"push: expected inbound denominator 3, got {r_push['ib_total']}")
    # ⭐ THE ROLE-PREFIX REGRESSION: on `^push-` alone this is 1, because `alias-to-cfl-…` falls out
    # of every denominator and lands in the ORPHAN pile. That is exactly what happened to four of
    # soul's real letters on launch night.
    if len(r_push["ib_unread"]) != 2:
        fails.append(f"push: expected 2 inbound unread (incl. the role-prefixed one), "
                     f"got {len(r_push['ib_unread'])}")
    if r_push["ib_credited"] != 1:
        fails.append(f"push: expected 1 inbound credited, got {r_push['ib_credited']}")
    # THE REGRESSION THIS WHOLE FILE EXISTS FOR: the pre-2026-08-08 script scored this peer 0/0/0.
    if r_push["seen_total"] == 0:
        fails.append("REGRESSION: a push-only peer scored a ZERO denominator — the 2026-08-08 defect")

    r_sil = scan_peer(peers[2], ours, blob, files)
    if r_sil["seen_total"] != 0:
        fails.append(f"silent: expected seen_total 0, got {r_sil['seen_total']}")

    # A letter must not vouch for itself: the inbound copy is not in ours_blob.
    if "push-to-cfl-urgent-2026-01-02" in blob:
        fails.append("ours_blob leaked exchange/inbound/ — a letter can vouch for itself")

    # SAW-NOTHING must actually PRINT differently. Capture stdout over a real run.
    import io, contextlib
    buf = io.StringIO()
    argv = sys.argv[:]
    empty_roots = os.path.join(tmp, "empty-n-roots")
    os.makedirs(empty_roots, exist_ok=True)
    # This fixture never touches G:\ — the fixture peers point at tmp dirs, not G:\, and the
    # existence of the CARRIER-fault machinery is exercised separately by
    # `scripts/audit/selftest_exchange_inbox.py`. Stub `probe_g` here so this internal self-test
    # stays fast and offline: without it, main() would attempt a REAL G:\ byte read every time
    # this fixture runs, which is exactly the thing this lane's write-set may not do.
    sys.argv = ["exchange_inbox.py", "--our-exchange", ours, "--roots", empty_roots]
    saved = PEERS[:]
    saved_probe_g = globals()["probe_g"]
    try:
        PEERS[:] = peers
        globals()["probe_g"] = lambda *a_, **k_: (True, "stubbed for internal self-test")
        with contextlib.redirect_stdout(buf):
            main()
    finally:
        PEERS[:] = saved
        globals()["probe_g"] = saved_probe_g
        sys.argv = argv
    out = buf.getvalue()
    if "SAW NOTHING" not in out:
        fails.append("SAW NOTHING banner absent for a zero-denominator channel")
    if "[silent]" not in out:
        fails.append("the silent channel was not named in the output")
    if "UNATTRIBUTED INBOUND" not in out or "stranger-to-cfl" not in out:
        fails.append("an inbound letter matching no channel was not reported as an ORPHAN")
    # ⛔ AND THE OTHER HALF, which is the part that makes the ORPHAN line trustworthy: our own
    # outbound must be reported as OURS and must NOT be counted as an orphan. Before 2026-08-09 the
    # orphan list grew mostly with CFL's own drafts, and a list that grows with your own files is a
    # list you stop reading — which is how the real orphans underneath it survived.
    if "OUR OWN OUTBOUND" not in out or "OURS    cfl-to-push-reply" not in out:
        fails.append("our own outbound in inbound/ was not reported under OURS")
    if "ORPHAN  cfl-to-push-reply" in out:
        fails.append("our own outbound was miscounted as an unattributed inbound letter")
    if "ORPHAN  alias-to-cfl" in out:
        fails.append("a role-prefixed letter from a declared peer was reported as an ORPHAN")
    if "No unread mail across 3" in out:
        fails.append("claimed 3 examined channels while one had a zero denominator")
    # OUTPUT CONTRACT: `UNREAD <n>` exactly once per channel, or su_close.sh's sum is wrong.
    n_hdr = len(re.findall(r"UNREAD (\d+)", out))
    if n_hdr != len(peers):
        fails.append(f"OUTPUT CONTRACT: expected {len(peers)} 'UNREAD n' tokens, found {n_hdr} "
                     f"— su_close.sh SUMS these")

    # ---- undeclared_trunks(): BOTH verdicts exercised on the same fixture ----
    # A check that has only ever been watched to pass is a check nobody has tested. `pub` and
    # `push` are declared; `silent` is declared; a fourth mailbox is created here and declared by
    # NOBODY, and it must be the only thing returned.
    os.makedirs(os.path.join(tmp, "ghost", "exchange", "inbound"), exist_ok=True)
    _globs = (os.path.join(tmp, "*", "exchange").replace(chr(92), "/"),)
    _und = undeclared_trunks(peers, ours, globs=_globs)
    _base = sorted(os.path.basename(os.path.dirname(x)) for x in _und)
    if _base != ["ghost"]:
        fails.append("undeclared_trunks POSITIVE: expected exactly ['ghost'], got %r" % _base)
    # NEGATIVE CONTROL -- declare the ghost too, and the list must go empty. Without this, a
    # function that returned every directory unconditionally would still pass the case above.
    _all = peers + [{"key": "ghost",
                     "exchange": os.path.join(tmp, "ghost", "exchange"),
                     "name_pat": r"zzz", "inbound_pat": r"^zzz"}]
    if undeclared_trunks(_all, ours, globs=_globs):
        fails.append("undeclared_trunks NEGATIVE: a DECLARED mailbox was still reported undeclared")

    print("=== SELF-TEST — exchange_inbox.py ===")
    if fails:
        for f_ in fails:
            print(f"  FAIL: {f_}")
        print(f"\nRESULT: FAIL — {len(fails)} failure(s)")
        return 1
    _checks = [
        "publish-only peer scored from its outbox",
        "push-only peer scored from OUR inbound (the 08-08 defect)",
        "inbound credited only by our own prose, never by a stamp",
        "ours_blob excludes inbound/ — no self-vouching",
        "genuinely silent peer -> SAW NOTHING, not a clean zero",
        "unattributed inbound letter reported as ORPHAN",
        "role-prefixed letter attributed to its own peer",
        "our own outbound in inbound/ reported as OURS, not ORPHAN",
        "summary does not count SAW-NOTHING channels as examined",
        "output contract: one 'UNREAD n' per channel for su_close",
        "undeclared_trunks: an unclaimed mailbox on disk is reported",
        "undeclared_trunks: NEGATIVE CONTROL — a declared mailbox is not",
    ]
    for _c in _checks:
        print(f"  {_c:<58}: PASS")
    _n = len(_checks)
    # ⛔ WAS A HARDCODED "8/8" AND IT WAS ALREADY WRONG 2026-08-09: two checks were added above and
    # the tally still said 8 while TEN lines printed. ⭐ Derive it from the lines actually printed —
    # a count written down beside the thing it counts is the repo's characteristic defect, and a
    # self-test that misreports its own size is the least defensible place for it.
    print(f"\nRESULT: PASS — {_n}/{_n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
