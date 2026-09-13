#!/usr/bin/env python3
"""trace_forward.py -- take one of Jon's sentences and print what changed while it was live.

WHY THIS EXISTS
---------------
Every tracing instrument in this repo runs BACKWARD: from a claim to its primary.
Jon asked for the other direction and nobody noticed for a day.

Jon, 2026-09-04, /wake, verbatim (typos his):

    if you can't trace the wiki through the conversation wtih vector embeded
    graph rag to the state of things as of my comments and the state of the
    agents which have done input on the PR thats an issue

PROFESSIONAL caught that CFL's fresh-PR-3 destination had encoded only the
backward half (2026-09-04 16:5x), as their one framed charter review:

    the destination runs claim->primary only. Which test traces one of Jon's
    09-04 sentences FORWARD to the diff it caused, and what single command prints
    that pair? If none, the destination is half of what he asked for and every
    gate under it passes.

Ticket N3-8. Professional framed it and deliberately does not build it.

V1 WAS WRONG AND PROFESSIONAL SAID SO WITHIN THE HOUR
------------------------------------------------------
v1 joined a sentence to a commit by grepping commit messages for the sentence.
It reported 4 of 4 traced, and that number was luck: those four commits quoted
him because THIS session happened to quote him. Their finding:

    The join is right in direction and wrong in its key. A grep of git log for
    Jon's verbatim sentence depends on the committer having quoted him -- a
    discipline, not a mechanism -- so an empty result cannot tell "no diff was
    caused" from "the quote was not carried."

That is the exact property CFL had asked them to check and had already named as
the one that would make it useless. A discipline-keyed join measures THE CARE OF
THE COMMITTER and reports it as traceability.

AND THEIR PROPOSED FIX ASSUMES A FIELD THAT DOES NOT EXIST. They wrote "commits
carry the session in the trailer." [measured 2026-09-04 17:2x: every commit
trailer in this repo is `Co-Authored-By` and nothing else. No session id, in any
commit, ever.] That is Herald's F-7 running backwards -- a reader designed for a
field nobody ships. Ticket N3-9: commits carry their session id.

SO THE JOIN IS THE STRONGEST THE AVAILABLE FIELDS SUPPORT, WITH THE GAP NAMED
------------------------------------------------------------------------------
Three legs, printed as three columns, never collapsed into one verdict:

  LEG 1  his sentence -> timestamp + trunk + session, from ~/.claude/history.jsonl
         (`timestamp`, `project` and `sessionId` are on every record, so leg 1
         needs no new field from anyone).
  LEG 2  commits in this repo in a FIXED window from that timestamp (default 12h,
         --max-window-hours). NOT bounded by his next message: an instruction
         stays live until SUPERSEDED, and bounding on the next utterance builds
         in a false negative that grows the more he talks -- so the more he
         engages, the less traceable his words become, which is backwards. The
         count of his other messages overlapping the window is PRINTED instead.
         TIME-KEYED ONLY. Seat attribution is impossible today because of the
         missing trailer above, so leg 2 answers "what changed while his sentence
         was the live instruction", NOT "what changed because of it". Unrelated
         commits landing in the window appear here. That false-positive class is
         labelled, not hidden.
  LEG 3  does the commit ALSO cite him verbatim (whitespace collapsed, nothing
         else changed).

READ THE COLUMNS TOGETHER, WHICH IS THE WHOLE POINT:
  leg 2 hits, leg 3 empty  -> the common, honest state. Work happened; nobody
                              carried the quote. Not a failure of tracing.
  leg 2 hits, leg 3 hits   -> the strong case. A committer carried his words.
  leg 2 EMPTY              -> THE REAL GAP. His sentence was live and nothing in
                              this repo changed. The finding this exists to make.

RELAY BOUND, Professional's, printed on every run: a sentence typed to one trunk
reaches another as a letter AFTER his timestamp, so the correct window is
per-receiver on letter mtime. Not implemented here; a co-trunk's response to a
relayed sentence is INVISIBLE to this. Ticket N3-10.

LEG 3 STILL EARNS ITS PLACE: it is the only mechanical cost the no-tidying rule
has ever had. A paraphrase, or emphasis added inside a quote, drops out of it.

Exit: 0 every sentence reached at least one commit | 3 a sentence was live and
NOTHING changed | 2 UNKNOWN (git or history unreadable).
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HISTORY = os.path.join(os.path.expanduser("~"), ".claude", "history.jsonl")


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=180)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "%s: %s" % (type(e).__name__, e)
    if r.returncode != 0:
        return None, (r.stderr or "").strip()[:200]
    return r.stdout, None


def norm_ws(s):
    """Collapse runs of whitespace to one space. NOTHING ELSE.

    Added after v1's first run returned 0 of 3: commit bodies wrap at 72 columns,
    so a perfectly verbatim sentence is split by a newline and a literal grep
    cannot match across it.

    Case, punctuation, spelling, typos and emphasis markup all stay significant.
    Wrapping is a rendering of the same words; `**bold**` inserted inside a quote
    is a different string and must still break the join. The rule being enforced
    is "do not EDIT the quote", not "do not wrap it"."""
    return " ".join(s.split())


def jon_messages(history=HISTORY):
    """Every prompt Jon typed, oldest first: (epoch_seconds, project, session, text)."""
    out = []
    try:
        with open(history, encoding="utf-8", errors="replace") as f:
            for ln in f:
                try:
                    d = json.loads(ln)
                except Exception:
                    continue
                ts = d.get("timestamp")
                if not isinstance(ts, (int, float)):
                    continue
                out.append((ts / 1000.0, d.get("project", "?"),
                            d.get("sessionId", "?"), d.get("display", "")))
    except OSError as e:
        return None, "%s: %s" % (type(e).__name__, e)
    out.sort(key=lambda r: r[0])
    return out, None


def locate(msgs, sentence):
    """The EARLIEST message containing the sentence, plus the next message's time.

    Earliest, not latest: a sentence he repeats is answered the first time it is
    said, and keying on the last occurrence would silently exclude the work the
    first one caused."""
    want = norm_ws(sentence)
    for i, (ts, proj, sess, text) in enumerate(msgs):
        if want in norm_ws(text):
            nxt = msgs[i + 1][0] if i + 1 < len(msgs) else None
            return {"ts": ts, "project": proj, "session": sess, "next_ts": nxt}
    return None


def commits_in_window(repo, start, end):
    args = ["log", "--all", "--format=%H%x1f%cI%x1f%h%x1f%s%x1f%B%x1e",
            "--since", datetime.fromtimestamp(start, timezone.utc).isoformat()]
    if end:
        args += ["--until", datetime.fromtimestamp(end, timezone.utc).isoformat()]
    out, err = git(repo, *args)
    if out is None:
        return None, err
    rows = []
    for rec in out.split("\x1e"):
        parts = rec.split("\x1f")
        if len(parts) < 5:
            continue
        if not parts[0].strip():
            continue
        rows.append({"sha": parts[0].strip(), "date": parts[1], "short": parts[2],
                     "subject": parts[3], "body": parts[4]})
    return rows, None


def files_of(repo, sha):
    out, _ = git(repo, "show", "--name-only", "--format=", sha)
    return [f for f in (out or "").split("\n") if f.strip()]


def self_check():
    fails = []
    if norm_ws("a  b\nc") != "a b c":
        fails.append("whitespace normalisation is wrong")
    if norm_ws("Dont") == norm_ws("Don't"):
        fails.append("normalisation is eating punctuation; it must collapse WHITESPACE "
                     "ONLY, or a tidied quote would start matching")

    msgs = [
        (100.0, "P", "s1", "an earlier unrelated thing"),
        (200.0, "P", "s2", "I don't feel like I have a proper map of\nhow they branch"),
        (300.0, "P", "s3", "something later"),
        (400.0, "P", "s4", "I don't feel like I have a proper map of how they branch again"),
    ]
    got = locate(msgs, "I don't feel like I have a proper map of how they branch")
    if not got or got["ts"] != 200.0:
        fails.append("a WRAPPED sentence did not locate; this is the false negative that "
                     "made v1's first run return 0 of 3")
    if got and got["next_ts"] != 300.0:
        fails.append("the next-message time was not reported (it is context, NOT the "
                     "window boundary -- see the window comment in main)")
    if got and got["ts"] == 400.0:
        fails.append("located the LAST occurrence; work caused by the first would fall "
                     "outside the window")
    if locate(msgs, "I don't feel like I have a **proper** map"):
        fails.append("emphasis added inside a quote still matched; the no-tidying rule "
                     "would cost nothing again")
    if locate(msgs, "a sentence that appears nowhere in this fixture at all"):
        fails.append("a sentence he never said still located")
    res, _ = jon_messages(os.path.join(os.sep, "no", "such", "history.jsonl"))
    if res is not None:
        fails.append("an unreadable history returned a list instead of an error; "
                     "'could not look' would render as 'he never said it'")
    res2, _ = commits_in_window(os.path.join(os.sep, "no", "such", "repo"), 0, 1)
    if res2 is not None:
        fails.append("an unreadable repo returned a result list instead of an error")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quote", action="append", default=[],
                    help="a Jon sentence, verbatim. Repeatable.")
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--history", default=HISTORY)
    ap.add_argument("--max-window-hours", type=float, default=12.0,
                    help="cap the leg-2 window when his next message is far away")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()

    if a.self_check:
        f = self_check()
        if f:
            print("SELF-CHECK: FAIL -- %d" % len(f))
            for x in f:
                print("  " + x)
            return 1
        print("SELF-CHECK: PASS -- 9 assertions: the wrapped-sentence fixture that made v1 "
              "return 0 of 3, EARLIEST-not-latest occurrence, the control that added "
              "EMPHASIS still breaks the match, whitespace-only normalisation, and "
              "unreadable history/repo as errors rather than empty results")
        return 0

    if not a.quote:
        print("UNKNOWN: no --quote given. This is not 'nothing traced'.")
        return 2
    msgs, err = jon_messages(a.history)
    if msgs is None:
        print("UNKNOWN: cannot read %s (%s)" % (a.history, err))
        return 2

    print("=== FORWARD TRACE: Jon's sentence -> what changed while it was live ===")
    print("  LEG 1  his sentence -> timestamp, trunk, session   (history.jsonl)")
    print("  LEG 2  commits in this repo in that window         (TIME-KEYED ONLY)")
    print("  LEG 3  does the commit also CITE him verbatim")
    print()
    print("  BOUNDS, printed every run because a pass means less than it looks:")
    print("   - Seat attribution is IMPOSSIBLE today: no commit carries a session id in")
    print("     its trailer. Leg 2 answers 'what changed while his sentence was the live")
    print("     instruction', NOT 'what changed because of it'. Unrelated commits in the")
    print("     window appear. Ticket N3-9.")
    print("   - RELAYED sentences reach a co-trunk AFTER his timestamp, so the correct")
    print("     window is per-receiver on letter mtime. Not implemented; a co-trunk's")
    print("     response is INVISIBLE here. Professional's bound. Ticket N3-10.")
    print("   - Leg 3 empty with leg 2 hits is the COMMON HONEST STATE, not a failure.")
    print()

    dead, unlocated = 0, 0
    for s in a.quote:
        shown = s if len(s) <= 76 else s[:73] + "..."
        loc = locate(msgs, s)
        if not loc:
            # ⛔ COUNTED AND EXITED ON, added 2026-09-04 17:4x. It previously printed
            # this and returned 0, so a sentence that could not be located at all
            # reported as a clean run -- "could not look" rendering as "nothing
            # wrong", which is the failure mode every other instrument here guards.
            # Found by Professional's demand for a negative control, not by use.
            unlocated += 1
            print("  NOT FOUND  %s" % shown)
            print("             He may not have typed it, or he said it in a claude.ai")
            print("             seat, which this venue structurally never holds.")
            print("             UNKNOWN, not 'he never said it'.")
            print()
            continue
        # THE WINDOW DOES NOT END WHEN HE SPEAKS AGAIN.
        #
        # ⛔ The first version set end = his NEXT message. Both real sentences then
        # reported "NOTHING CHANGED" while commits acting on them landed minutes
        # later -- because he types several messages in a row and the window
        # collapsed to about two minutes.
        #
        # The model was wrong, not the data. An instruction stays live until it is
        # SUPERSEDED, not until the next thing he says; his messages overlap, and
        # work on the first continues while the third is arriving. Keying on the
        # next utterance builds in a false negative that scales with how talkative
        # he is -- so the more he engages, the less traceable his words become,
        # which is exactly backwards.
        #
        # So the window is a fixed span, and the count of his OTHER messages
        # inside it is printed rather than used as a boundary: overlap is a fact
        # about the window a reader needs, not an error to design away.
        end = loc["ts"] + a.max_window_hours * 3600
        overlap = sum(1 for (t, _p, _s, _x) in msgs if loc["ts"] < t < end)
        when = datetime.fromtimestamp(loc["ts"]).strftime("%Y-%m-%d %H:%M")
        trunk = os.path.basename(str(loc["project"]).rstrip("\\/")) or "?"
        print("  %s" % shown)
        print("    LEG 1  %s  trunk=%s  session=%s" % (when, trunk, str(loc["session"])[:8]))
        print("           window %.0fh; %d other Jon message(s) overlap it -- an "
              "instruction" % (a.max_window_hours, overlap))
        print("           stays live until SUPERSEDED, not until he speaks again")
        rows, err = commits_in_window(a.repo, loc["ts"], end)
        if rows is None:
            print("    LEG 2  UNKNOWN -- git failed: %s" % err)
            print()
            continue
        if not rows:
            dead += 1
            print("    LEG 2  ** NOTHING CHANGED IN THIS REPO WHILE IT WAS LIVE **")
            print("           This is the finding the instrument exists to produce.")
            print()
            continue
        want = norm_ws(s)
        cited = [r for r in rows if want in norm_ws(r["body"])]
        print("    LEG 2  %d commit(s) in the window" % len(rows))
        for r in rows[:6]:
            mark = "CITES HIM" if r in cited else "         "
            print("           %s %s  %s" % (r["short"], mark, r["subject"][:56]))
            if r in cited:
                for fn in files_of(a.repo, r["sha"])[:5]:
                    print("                       %s" % fn)
        if len(rows) > 6:
            print("           ... and %d more in the window" % (len(rows) - 6))
        print("    LEG 3  %d of %d commit(s) carry his words verbatim%s"
              % (len(cited), len(rows),
                 " -- nobody carried the quote" if not cited else ""))
        print()

    print("  %d sentence(s); %d were live while NOTHING in this repo changed; "
          "%d could not be located at all." % (len(a.quote), dead, unlocated))
    if unlocated:
        print("  EXIT 2: a sentence that cannot be LOCATED is UNKNOWN and dominates. It is")
        print("  not evidence he never said it -- history.jsonl structurally never holds a")
        print("  claude.ai-seat utterance -- and it is certainly not a clean run.")
        return 2
    if dead:
        print("  EXIT 3: a sentence live over an empty window is the real gap.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
