#!/usr/bin/env python3
"""jon_ask_preflight.py — the mechanical pre-flight T-13 asks for.

WHY THIS EXISTS
---------------
Jon, 2026-07-22, verbatim
(`wiki/intake-triage/jon-turn5-deploy-phase-and-delegation-2026-07-22.md:34`):

    "I see most of this coordination as something I've already approved, and then it's just a
     matter of best practice judgement from you on how to get there, and how to budget my limited
     review time that you have access to."

The same clause (④, `:36`) draws the line mechanically, and this script is that line in code:

    Delegated  : sequencing, packaging, routing, and the budgeting of Jon's review-minutes.
    RESERVED   : merges to origin/main · gates G1-G4 and successors · anything IDENTITY-ADJACENT ·
                 new ratifications (roles, charters, membrane crossings) · registration OF AGENTS ·
                 spend/plan changes · anything the wayfinder itself flags as exceeding scope.

Register ticket T-13 (`exchange/RATIFIED-BUT-UNAPPLIED-2026-08-05.md:521`) closes on: *"a mechanical
pre-flight on any packet addressed to Jon — every 'open question for Jon' must either cite a
reserved category from turn-5 ④ or be re-owned by an agent."* T-13 is the PARENT of T-04, T-11 and
T-12; those three were each an agent holding a completed Jon act open as a Jon gate. Closing them
without this just refills the queue with new instances.

WHAT IT DOES, AND WHAT IT DELIBERATELY DOES NOT
-----------------------------------------------
It finds Jon-addressed ask sites in tracked prose and asks ONE question of each: does this ask cite
a reserved category, or not? An ask that cites one is lawful. An ask that cites none is a candidate
for re-owning by an agent — *candidate*, not verdict. **This script never decides that an ask is
illegitimate; a human or a role session does.** It converts "somebody should check whether we are
over-asking Jon" into a number with a denominator, which is the only thing that was missing.

It is ADVISORY by default and exits 0. `--strict` exits 1 when UNRESERVED > 0, for a caller that
wants it to bite. Nothing here blocks by default: an alarm calibrated to always fire stops being
read, which this repo has a scar from (RATIO_FLOOR, retired 2026-08-06).

FALSE POSITIVES ARE HANDLED BY NAMING THEM, NOT BY WIDENING THE PATTERN
-----------------------------------------------------------------------
Documents *about* the over-asking defect quote its vocabulary constantly. Excluding them silently
would be the same defect one level up, so `SELF_REFERENTIAL` is a short, printed list and the
report states how many sites it suppressed. If that number ever grows, it is visible.

THE BUCKETS, AND WHY THERE ARE SEVEN OF THEM (added 2026-08-07, from one live re-owning pass)
---------------------------------------------------------------------------------------------
The first version had three states and the re-owning lane immediately needed four more. Every
site lands in exactly one bucket, and the report prints the sum against the denominator, because
a bucket list nobody adds up is a place for a site to go missing. In precedence order:

  prose ABOUT asking  a NAMED, per-site disposition with a written reason. Outranks everything
                      else because it is the only human-adjudicated one. Keyed on a distinctive
                      SUBSTRING, never a line number, so it travels with the line it dispositions
                      and goes visibly STALE rather than silently covering some other line.
  annotated CLOSED    he ruled and the site now says so, with the quote.
  RE-OWNED            not his; an agent or role owns it. **Must name an owner** -- "not Jon's"
                      with no successor is how a decision becomes nobody's.
  in a GENERATED file a site here cannot be re-owned by editing the file; the next regeneration
                      would erase the edit. The fix is the generator. Bucketed, never hidden.
  peer-authored       Herald / Claude Personal mail under `exchange/inbound/`. CFL's write scope
                      into peer trees is delivery only, never mutation, so CFL cannot re-own an
                      ask inside someone else's message.
  cites a reserved    lawful under turn-5 (4).
  cites NONE          the review queue. Still a candidate list, still not a verdict.

Three of these exist because the instrument got its own first pass wrong and the run was read
instead of trusted: `generated_by:` frontmatter (model attribution) was misread as "a script
wrote this"; a RE-OWNED block written for the section BELOW a site fell inside that site's
lookahead and relabelled an unrelated line; and a re-owning annotation, which necessarily quotes
the reserved list to explain why a site is NOT reserved, tripped `explicit-turn5-cite` and
re-scored four freshly re-owned sites as "lawfully reserved to Jon" -- the report asserting the
exact opposite of the prose it was reporting on.
"""

import argparse
import os
import re
import sys
import tempfile

# ---------------------------------------------------------------------------
# Ask-site detection. Deliberately broad: a missed ask is worse than a flagged
# non-ask, because the whole failure mode is asks nobody noticed were asks.
# ---------------------------------------------------------------------------
ASK_PATTERNS = [
    r"open questions? for jon",
    r"questions? for jon",
    r"jon rules the open",
    r"jon-minutes to rule",
    r"awaiting jon",
    r"\bpending (?:a |the )?jon(?:'s)?\b",
    r"held pending jon",
    r"jon gate\b",
    r"for jon to (?:rule|decide|answer|approve)",
    r"needs jon(?:'s)? (?:input|decision|ruling|answer|approval)",
    r"jon:? (?:live verification|decision required|to decide)",
]
ASK_RE = re.compile("|".join("(?:%s)" % p for p in ASK_PATTERNS), re.I)

# ---------------------------------------------------------------------------
# The reserved categories, straight off turn-5 ④. A site "cites a reserved
# category" if any of these appears within LOOKAHEAD lines of the ask.
# ---------------------------------------------------------------------------
RESERVED = {
    "merge-to-main": r"merge(?:s|d)? (?:to|into) (?:origin/)?main|origin/main merge|merge the pr",
    "gate-G1-G4": r"\bG[1-4]\b|gates? G1|goalpost",
    "identity-adjacent": r"identity[- ]adjacent|\[IDENTITY",
    "new-ratification": r"new ratification|ratif(?:y|ication) (?:of |a )?(?:role|charter|membrane)"
                        r"|membrane crossing|charter change",
    "agent-registration": r"registration of agents?|register the agent|agent registration",
    "spend-or-plan": r"\bspend\b|budget change|plan change|reallocat",
    "exceeds-scope": r"exceeds? (?:the )?scope|outside (?:the )?delegation|beyond (?:my|its) scope",
    "explicit-turn5-cite": r"turn-5 ?[④4]|reserved to jon|delegation clause",
}
RESERVED_RE = {k: re.compile(v, re.I) for k, v in RESERVED.items()}

# A THIRD state the first draft of this script did not have, and needed within one live run.
# An ask that has since been ANNOTATED AS CLOSED is not a candidate to re-own -- it is already
# handled. Without this bucket the instrument reports register T-12's own successful fix as an
# outstanding defect, which would make the tool an argument for redoing work that is done: the
# exact failure the register exists to stop. Found by reading the first live output instead of
# trusting it.
CLOSED_PATTERNS = [
    r"RESOLVED-BY",
    r"CLOSED-BY",
    r"CLOSED 20\d\d-\d\d",
    r"RESOLVED 20\d\d-\d\d",
    r"(?:no longer|not|neither)[^.\n]{0,40}an open question",
    r"already (?:answered|ruled|approved|resolved)",
    r"\bsuperseded\b",
    r"\banswered\b",
    r"\bresolved\b",
]
CLOSED_RE = re.compile("|".join("(?:%s)" % p for p in CLOSED_PATTERNS), re.I)

# A FOURTH state, and the one that closes the loop this instrument opened. Re-owning is the
# ACTION the report asks for, so the report has to be able to see that it happened -- otherwise
# the only way to make a site disappear is to delete the prose, and an instrument that rewards
# deletion is worse than no instrument.
#
# A re-owning must NAME AN OWNER. That is not decoration: "not Jon's" without a successor is how
# a decision becomes nobody's. The marker and the `owner:` must both be in the window.
#
# It must also outrank RESERVED. Found live on 2026-08-07: a re-owning annotation that explains
# WHY a site is not reserved necessarily quotes the reserved list, which tripped
# `explicit-turn5-cite` and re-scored four freshly re-owned sites as "lawfully reserved to Jon."
# The prose said the opposite of what the instrument then reported about it.
REOWNED_RE = re.compile(r"RE-OWNED", re.I)
REOWNED_OWNER_RE = re.compile(r"owner:\s*\S", re.I)

LOOKAHEAD = 12  # lines after the ask line in which a reserved citation counts
LOOKBEHIND = 3  # ...and before it. A measured need, not a guess: the coordination charter
                # writes "No third crossing exists without a new ratification." on one line
                # and "the membrane is a Jon Gate, not a coordinator decision." on the NEXT.
                # A forward-only window read the second half and scored a lawful, ratified
                # clause UNRESERVED because its citation sat one line ABOVE the ask.

# Files whose SUBJECT is this defect. They quote the vocabulary by necessity.
SELF_REFERENTIAL = {
    "exchange/RATIFIED-BUT-UNAPPLIED-2026-08-05.md",
    "exchange/T-01-DO-NOT-APPLY-published-path-finding-2026-08-06.md",
    "scripts/audit/jon_ask_preflight.py",
    # The ruling queue is the ONE page whose purpose is asking Jon; its `aliases:` line lists
    # "questions for jon" so the page can be FOUND by that phrase. Flagging the index of asks
    # as an unlawful ask is the detector reading its own filing system.
    "wiki/tracker/ruling-queue-cfl.md",
}

# Named false positives: the ask VOCABULARY appearing in prose ABOUT the asking mechanism rather
# than in an actual ask. Keyed on a distinctive SUBSTRING, never a line number, so an annotation
# travels with the line it dispositions and goes visibly STALE instead of silently matching some
# other line that drifted into its place.
#
# Each entry must carry a reason. A suppression without a reason is a suppression nobody can audit,
# which is the defect this whole instrument exists to measure, one level up.
PROSE_ABOUT_ASKING = [
    ("exchange/coordination-charter-2026-07-21.md",
     "STANDS UNCHANGED: a mirror consult is never a substitute",
     "ratified charter defining what a Jon Gate IS. Not an ask; a clause about asks."),
    ("exchange/coordination-charter-2026-07-21.md",
     "It is RETIRED as a description of reliability",
     "ratified charter, A3. Same: the term 'Jon Gate' used definitionally."),
    ("exchange/AUTO-RUN-2026-08-06.md",
     "said fable-mirror registration was awaiting Jon",
     "a run report of a stale gate FOUND AND FIXED. Reporting a removed ask is not asking."),
    ("exchange/corpus-fix-groupB-held-2026-07-25.md",
     "ends on a framing question about a new protocol awaiting Jon",
     "describes where a TRANSCRIPT ended. Summarising a recording is not an ask."),
    ("exchange/packet-a-escalations-2026-07-18.md",
     '"questions-for-jon lines" section',
     "a format-mapping table row, disposition 'Mapped'. Names the mechanism, does not use it."),
    ("exchange/coordination-plan-2026-07-19.md",
     "with two open Questions for Jon about scope) was considered for the same bundle",
     "a worked NEGATIVE EXAMPLE about PR bundling. Describes another PR's contents; the ask "
     "it mentions belongs to PR #104's source page, not to this document."),
    ("exchange/fable-2026-07/000-cc-to-fable-handshake.md",
     "handshake (draft; not sent",
     "a 2026-07-15 draft header for a message never sent. The exchange proceeded anyway "
     "(cc-return-2026-07-15.md); nothing is waiting."),
]

# Generated files. A site here CANNOT be re-owned by editing the file -- the edit would be
# overwritten by the next regeneration, which is the derive-don't-record defect performed
# deliberately. The fix, if one is needed, is the generator. Bucketed and printed, never hidden.
GENERATED_MARKER = re.compile(r"\*\*GENERATED\*\*", re.I | re.M)

# Peer-authored mail. Herald and Claude Personal write into `exchange/inbound/` and CFL's write
# scope into their trees is symmetrical: delivery only, never mutation. CFL cannot re-own an ask
# in someone else's message. Bucketed so it is visible and not mistaken for CFL's own backlog.
PEER_INBOUND_PREFIX = "exchange/inbound/"

DEFAULT_ROOTS = ["exchange", "wiki/tracker"]

# Bucket counts from the most recent run(), so --self-test can ASSERT the partition instead
# of printing it and hoping somebody reads the line.
LAST_RUN = {}


def ascii_safe(t):
    """Windows consoles here are cp1252. File-derived text carries em dashes, circled digits
    and smart quotes, and a report that CRASHES on the content it is reporting is worse than
    one that transliterates it. Output only -- never applied to a file on disk."""
    return t.encode("ascii", "replace").decode("ascii")


def scan_text(text, path):
    """Return (sites, ...) for one document. A site is one ask line + its verdict."""
    lines = text.splitlines()
    sites = []
    in_fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not ASK_RE.search(line):
            continue
        window = "\n".join(lines[max(0, i - LOOKBEHIND):i + LOOKAHEAD + 1])
        cites = sorted(k for k, rx in RESERVED_RE.items() if rx.search(window))
        closed = bool(CLOSED_RE.search(window))
        reowned = bool(REOWNED_RE.search(window) and REOWNED_OWNER_RE.search(window))
        prose_reason = None
        for pa_path, pa_sub, pa_reason in PROSE_ABOUT_ASKING:
            if path == pa_path and pa_sub in line:
                prose_reason = pa_reason
                break
        sites.append({
            "path": path,
            "line": i + 1,
            "text": line.strip()[:150],
            "cites": cites,
            "reserved": bool(cites),
            "closed": closed,
            "reowned": reowned,
            "prose_reason": prose_reason,
        })
    return sites


def walk(roots, repo):
    for root in roots:
        base = os.path.join(repo, root)
        if os.path.isfile(base):
            yield base
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def run(repo, roots, strict, show_all):
    files = 0
    sites = []
    suppressed = 0
    suppressed_files = set()
    for full in walk(roots, repo):
        rel = os.path.relpath(full, repo).replace("\\", "/")
        try:
            text = open(full, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        files += 1
        found = scan_text(text, rel)
        if rel in SELF_REFERENTIAL:
            if found:
                suppressed += len(found)
                suppressed_files.add(rel)
            continue
        gen = bool(GENERATED_MARKER.search(chr(10).join(text.splitlines()[:12])))
        for site in found:
            site["generated"] = gen
            site["peer"] = rel.startswith(PEER_INBOUND_PREFIX)
        sites.extend(found)

    # STALE-ANNOTATION CHECK. A named suppression whose substring no longer appears anywhere in
    # its file is not "clean" -- it is an annotation that stopped pointing at anything, and the
    # site it used to cover is now unlabelled somewhere else in the list. Printed, never silent.
    stale = []
    for pa_path, pa_sub, pa_reason in PROSE_ABOUT_ASKING:
        if not any(x["path"] == pa_path and x["prose_reason"] == pa_reason for x in sites):
            stale.append((pa_path, pa_sub))

    # Bucket precedence, in order, most-settled first. Every site lands in exactly one.
    prose = [s for s in sites if s["prose_reason"]]
    rest = [s for s in sites if not s["prose_reason"]]
    closed = [s for s in rest if s["closed"]]
    rest = [s for s in rest if not s["closed"]]
    reowned = [s for s in rest if s["reowned"]]
    rest = [s for s in rest if not s["reowned"]]
    generated = [s for s in rest if s["generated"]]
    rest = [s for s in rest if not s["generated"]]
    peer = [s for s in rest if s["peer"]]
    rest = [s for s in rest if not s["peer"]]
    reserved = [s for s in rest if s["reserved"]]
    unreserved = [s for s in rest if not s["reserved"]]

    print("JON-ASK PRE-FLIGHT (register T-13 -- turn-5 (4) reserved-category test)")
    print("=" * 78)
    print("  roots scanned          : %s" % ", ".join(roots))
    print("  markdown files read    : %d" % files)
    print("  ask sites found        : %d   <- the denominator" % len(sites))
    print("  annotated CLOSED       : %d   <- he ruled; the site now says so" % len(closed))
    print("  RE-OWNED (owner named) : %d   <- not his; an agent or role owns it" % len(reowned))
    print("  prose ABOUT asking     : %d   <- named false positives, reasons below" % len(prose))
    print("  in a GENERATED file    : %d   <- fix the generator, never the file" % len(generated))
    print("  peer-authored inbound  : %d   <- Herald/Personal mail; CFL must not mutate it"
          % len(peer))
    print("  cites a reserved cat.  : %d   <- lawful under turn-5 (4)" % len(reserved))
    print("  cites NONE             : %d   <- candidates to re-own by an agent"
          % len(unreserved))
    print("  suppressed as self-ref : %d across %d file(s): %s"
          % (suppressed, len(suppressed_files), ", ".join(sorted(suppressed_files)) or "none"))
    # Arithmetic, printed. A bucket list nobody adds up is a place for a site to go missing.
    parts = (len(closed) + len(reowned) + len(prose) + len(generated) + len(peer)
             + len(reserved) + len(unreserved))
    print("  buckets sum            : %d %s %d sites"
          % (parts, "==" if parts == len(sites) else "!= (BUG)", len(sites)))
    LAST_RUN.clear()
    LAST_RUN.update(sites=len(sites), closed=len(closed), reowned=len(reowned),
                    prose=len(prose), generated=len(generated), peer=len(peer),
                    reserved=len(reserved), unreserved=len(unreserved), parts=parts,
                    stale=len(stale))
    if stale:
        print("\n  !! STALE ANNOTATIONS -- the line each was written against is gone. The")
        print("     site it covered is now UNLABELLED above. Re-key it or delete it:")
        for pa_path, pa_sub in stale:
            print(ascii_safe("       %s  <- %r" % (pa_path, pa_sub[:60])))
    if not sites:
        print("\n  !! ZERO ask sites found. That is a DETECTOR result, not a clean bill of health.")
        print("     Verify the roots exist and the patterns still match how asks are written.")

    print("")
    print("  The detector is deliberately BROAD: a missed ask is worse than a flagged non-ask,")
    print("  because the failure mode is asks nobody noticed were asks. The UNRESERVED list is a")
    print("  REVIEW QUEUE, not a verdict list -- some entries are prose ABOUT asking Jon.")

    if unreserved:
        print("\n  UNRESERVED ask sites -- each must cite a reserved category or be re-owned:")
        for s in unreserved:
            print(ascii_safe("    %s:%d  %s" % (s["path"], s["line"], s["text"])))
    if prose:
        print("\n  PROSE ABOUT ASKING -- dispositioned false positives, the reason for each:")
        for s in prose:
            print(ascii_safe("    %s:%d" % (s["path"], s["line"])))
            print(ascii_safe("        %s" % s["prose_reason"]))
    if generated:
        print("\n  IN GENERATED FILES -- editing these IS derive-don't-record, done on purpose:")
        for g in sorted({x["path"] for x in generated}):
            print(ascii_safe("    %s  (%d site(s))"
                  % (g, sum(1 for x in generated if x["path"] == g))))
    if peer:
        print("\n  PEER-AUTHORED INBOUND -- CFL writes to peer trees delivery-only, never mutation:")
        for s in peer:
            print(ascii_safe("    %s:%d  %s" % (s["path"], s["line"], s["text"][:110])))
    if reowned:
        print("\n  RE-OWNED -- each of these names an owner in its own annotation:")
        for s in reowned:
            print(ascii_safe("    %s:%d  %s" % (s["path"], s["line"], s["text"][:110])))
    if show_all and reserved:
        print("\n  RESERVED ask sites (lawful under turn-5 (4)):")
        for s in reserved:
            print(ascii_safe("    %s:%d  [%s]  %s"
                  % (s["path"], s["line"], ",".join(s["cites"]), s["text"])))

    print("\n  Reserved to Jon, always (turn-5 (4), jon-turn5-deploy-phase-and-delegation-2026-07-22.md:36):")
    print("    merges to origin/main  /  gates G1-G4  /  IDENTITY-ADJACENT  /  new ratifications")
    print("    (roles, charters, membrane crossings)  /  registration OF AGENTS  /  spend/plan changes")
    print("     /  anything the wayfinder itself flags as exceeding scope.")
    print("  Everything else is delegated mechanics and is NOT a question for him.")

    if strict and unreserved:
        return 1
    return 0


# ---------------------------------------------------------------------------
# Self-test. It must be able to FAIL, or it proves nothing — the standing rule
# in this repo. Fixtures are written to a temp dir, never to the checkout.
# ---------------------------------------------------------------------------
def self_test():
    ok = True

    def t(name, expected, got):
        nonlocal ok
        good = expected == got
        ok = ok and good
        print("  %-52s %s  (want %s, got %s)"
              % (name, "PASS" if good else "FAIL", expected, got))

    lawful = ("## Open questions for Jon\n"
              "1. Merge PR #80 into origin/main — reserved to Jon.\n")
    unlawful = ("## Open questions for Jon\n"
                "1. Should the packet be sequenced before or after the digest?\n")
    neither = "Nothing here addresses anybody in particular.\n"
    fenced = ("```\n## Open questions for Jon\n1. sequencing?\n```\n")

    closed_ask = ("## Open questions for Jon\n"
                  "1. Should the packet be sequenced first?\n"
                  "> [RESOLVED-BY-TURN-5] Jon answered. Not an open question.\n")
    t("lawful ask is RESERVED", True, scan_text(lawful, "x")[0]["reserved"])
    t("annotated-closed ask is CLOSED", True, scan_text(closed_ask, "x")[0]["closed"])
    t("live mechanics ask is NOT closed", False, scan_text(unlawful, "x")[0]["closed"])
    t("mechanics ask is UNRESERVED", False, scan_text(unlawful, "x")[0]["reserved"])
    t("non-ask prose yields no site", 0, len(scan_text(neither, "x")))
    t("ask inside a code fence is ignored", 0, len(scan_text(fenced, "x")))
    t("detector is not vacuous (finds the ask)", 1, len(scan_text(unlawful, "x")))

    # Negative control for the word-boundary fix. "sPENDING Jon-minutes" is the phrase this repo
    # uses for BUDGETING his time -- the opposite of asking for it -- and the unanchored `pending`
    # pattern scored it an unreserved ask. One live false positive, found by printing which
    # pattern fired at each site instead of trusting the count.
    spending = "This is a mechanism for spending Jon-minutes better, not a question.\n"
    t("'spending Jon-minutes' is NOT an ask", 0, len(scan_text(spending, "x")))
    t("'pending Jon's ratification' still IS an ask", 1,
      len(scan_text("Row D-C4 -- PROPOSED, pending Jon's ratification.\n", "x")))

    # Negative control for LOOKBEHIND: a citation on the line ABOVE the ask is still a citation.
    behind = ("No third crossing exists without a new ratification. Any proposed flow across\n"
              "the membrane is a Jon Gate, not a coordinator decision.\n")
    t("reserved citation ABOVE the ask counts", True, scan_text(behind, "x")[0]["reserved"])
    t("...an unrelated line above does NOT create one", False,
      scan_text("The weather is fine.\nthe membrane is a Jon Gate.\n", "x")[0]["reserved"])

    # RE-OWNING must NAME AN OWNER. "not Jon's" with no successor is how a decision becomes
    # nobody's, so the marker alone must not be enough to clear a site.
    reowned_ok = ("## Open questions for Jon\n"
                  "1. Should the packet be sequenced first?\n"
                  "> [RE-OWNED 2026-08-07 - owner: coordinator] Sequencing is delegated mechanics.\n")
    reowned_bad = ("## Open questions for Jon\n"
                   "1. Should the packet be sequenced first?\n"
                   "> RE-OWNED. Not a Jon gate.\n")
    t("RE-OWNED with an owner counts", True, scan_text(reowned_ok, "x")[0]["reowned"])
    t("RE-OWNED without an owner does NOT", False, scan_text(reowned_bad, "x")[0]["reowned"])

    # A named per-site disposition must outrank every window-based one. Measured need: a RE-OWNED
    # block written for the section BELOW a site fell inside that site's lookahead and relabelled
    # an unrelated line with a disposition nobody wrote for it.
    # A named prose disposition must attach to the line carrying its substring, and to no other.
    pa_path, pa_sub, pa_reason = PROSE_ABOUT_ASKING[0]
    hit = scan_text("Open questions for Jon: " + pa_sub + "\n", pa_path)
    miss = scan_text("Open questions for Jon: something else entirely\n", pa_path)
    t("named prose entry attaches to its own line", pa_reason, hit[0]["prose_reason"])
    t("...and to no other line in the same file", None, miss[0]["prose_reason"])

    # Buckets must partition. A bucket list that does not add up is a place for a site to hide.
    with tempfile.TemporaryDirectory() as td2:
        os.makedirs(os.path.join(td2, "exchange", "inbound"))
        os.makedirs(os.path.join(td2, "wiki", "tracker"))
        open(os.path.join(td2, "exchange", "a.md"), "w", encoding="utf-8").write(unlawful)
        open(os.path.join(td2, "exchange", "b.md"), "w", encoding="utf-8").write(lawful)
        open(os.path.join(td2, "exchange", "c.md"), "w", encoding="utf-8").write(closed_ask)
        open(os.path.join(td2, "exchange", "d.md"), "w", encoding="utf-8").write(reowned_ok)
        open(os.path.join(td2, "exchange", "inbound", "e.md"), "w",
             encoding="utf-8").write(unlawful)
        open(os.path.join(td2, "wiki", "tracker", "f.md"), "w", encoding="utf-8").write(
            "# Roles\n\n**GENERATED** by a script. Do not hand-edit.\n\n" + unlawful)
        run(td2, ["exchange", "wiki/tracker"], strict=False, show_all=False)
    t("buckets partition the sites exactly", LAST_RUN["sites"], LAST_RUN["parts"])
    t("the peer-inbound bucket catches inbound/", 1, LAST_RUN["peer"])
    t("the GENERATED bucket catches the banner", 1, LAST_RUN["generated"])
    t("the RE-OWNED bucket catches an owned site", 1, LAST_RUN["reowned"])
    t("...and one real unreserved site survives all of it", 1, LAST_RUN["unreserved"])



    # end-to-end, including the strict exit code, against a throwaway tree
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "exchange"))
        open(os.path.join(td, "exchange", "a.md"), "w", encoding="utf-8").write(unlawful)
        rc_advisory = run(td, ["exchange"], strict=False, show_all=False)
        rc_strict = run(td, ["exchange"], strict=True, show_all=False)
    t("advisory run exits 0 with a finding", 0, rc_advisory)
    t("strict run exits 1 with a finding", 1, rc_strict)

    print("\n  SELF-TEST: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")))
    ap.add_argument("--roots", nargs="*", default=DEFAULT_ROOTS)
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any ask site cites no reserved category")
    ap.add_argument("--all", action="store_true", help="also list the lawful sites")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return run(a.repo, a.roots, a.strict, a.all)


if __name__ == "__main__":
    sys.exit(main())
