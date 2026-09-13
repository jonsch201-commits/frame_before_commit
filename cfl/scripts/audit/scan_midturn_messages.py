#!/usr/bin/env python3
"""scan_midturn_messages.py — did Jon's mid-turn messages reach the corpus?

WHY THIS EXISTS
---------------
On 2026-08-02 Jon sent nine messages into a running fable-mirror subagent. Claude Code
delivers those *inside the subagent's turn* as `type: user` + `isMeta: true` records whose
text is wrapped in "The user sent a new message while you were working:". None of them
arrived in the coordinator's main thread as a principal user turn, and main's system
reminders said "No human input has been received" throughout. The coordinator spent four
hours treating the agent's relays of those real instructions as fabrications.

Jon ratified the fix in his own words, 2026-08-02:

    "I strongly agree we always need all subagent jsons, and their is a good path
     demonstrated towards this."

This is that check. It is a REQUIRED STANDARD-UPDATE STEP, and it must be able to fail.

WHAT IT CHECKS
--------------
For every session JSONL in the tree (parent AND `subagents/agent-*.jsonl`, which nest one
level down and which a flat glob silently misses):

  1. Extract every mid-turn user message.
  2. For each, look for its fingerprint in the EXTRACTED MARKDOWN corpus.
  3. A message present in a JSONL but absent from every extract is a LOSS — Jon's words
     living only in %LOCALAPPDATA%\\Temp on C:, which is the condition this exists to end.

Exit 0 = every mid-turn message is represented in the corpus.
Exit 1 = at least one is not.  Exit 2 = bad usage / nothing scanned (never a silent pass).

DELIBERATELY NOT DONE
---------------------
No content is printed. Fingerprints are truncated and the full text never leaves the file --
`raw/` is Jon's full personal history and this script's output goes into reports.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

PROJECTS_ROOT = Path(os.path.expanduser("~")) / ".claude" / "projects"
REPO = Path(__file__).resolve().parents[2]
CORPUS = REPO / "raw" / "transcripts" / "claude-code"

WRAPPER = "The user sent a new message while you were working:"
TRAILER = "This is how Claude Code surfaces messages the user sends mid-turn"

# Fingerprint length. Long enough to be distinctive, short enough to survive the
# extractor's own reflowing/escaping. 60 chars was chosen because the extractor wraps
# at ~100 and a 60-char slice has not crossed a wrap boundary in observed output.
FP_LEN = 60


def midturn_messages(jsonl_path):
    """Yield (timestamp, text) for each mid-turn user message in one JSONL.

    A record qualifies when it is type=user and its text BEGINS with the harness WRAPPER.

    THE WRAPPER AT POSITION 0 IS THE DISCRIMINATOR. isMeta is NOT required, and
    "wrapper appears anywhere" is NOT sufficient.

    Built 2026-08-03 requiring `type=user AND isMeta=true AND wrapper`. On its FIRST
    live use -- the very next mirror dispatch, hours later -- the harness delivered a
    real Jon mid-turn message with the wrapper present and **isMeta absent**. The scan
    reported `88/88 PASS` while that message was outside its denominator entirely.
    An instrument built to prove Jon's words are not being dropped dropped one.

    The original reasoning was half right: isMeta ALONE over-counts (Claude Personal
    measured 32 vs 3 unfiltered), because the harness marks other injected content with
    it. The error was concluding that isMeta must therefore be REQUIRED. The wrapper
    alone already excludes everything isMeta was added to exclude -- it is a literal
    harness string that appears on nothing else -- so isMeta contributed no precision
    and cost recall the moment the harness stopped setting it.

    General form, and this is the third instance in two days: **a conjunctive predicate
    is only as broad as its narrowest clause, and an AND added "for safety" against a
    field you do not control is a silent recall cut.** Same shape as the mail checker
    with one peer hardcoded and the gate that passed by resolving nothing.

    AND THE SAME-DAY OVERCORRECTION, recorded because it is the more instructive half:
    dropping isMeta for "wrapper appears anywhere" immediately produced FALSE POSITIVES
    -- a dispatch brief that merely QUOTED the wrapper string, and task-notification
    payloads echoing it, all counted as Jon speaking. Loosening a predicate is not the
    inverse of tightening it. **The fix for a wrong discriminator is the right
    discriminator, not a weaker one:** the harness always emits this wrapper as the
    FIRST characters of the record, so position 0 is exact, and it depends on no field
    the harness may stop setting.
    """
    try:
        fh = open(jsonl_path, encoding="utf-8", errors="ignore")
    except OSError:
        return
    with fh:
        for line in fh:
            line = line.strip()
            if not line or WRAPPER not in line:
                continue  # cheap prefilter before the JSON parse
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") != "user":
                continue  # isMeta deliberately NOT required -- see docstring
            c = o.get("message", {}).get("content")
            if isinstance(c, list):
                text = " ".join(
                    b.get("text", "") for b in c
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            else:
                text = str(c)
            # Position 0, not "anywhere". A brief that quotes the wrapper, or a
            # task-notification payload echoing it, is not Jon speaking.
            if not text.lstrip().startswith(WRAPPER):
                continue
            body = text.split(WRAPPER, 1)[1]
            body = body.split(TRAILER)[0].strip()
            if body:
                yield o.get("timestamp"), body


def fingerprint(body):
    """A whitespace-normalized slice, skipping any leading list marker.

    Jon's messages often open with "1. " or "Ok. " which are not distinctive; the slice
    starts after the first sentence-ish boundary when one appears very early.
    """
    flat = " ".join(body.split())
    m = re.match(r"^(?:\d+[.)]\s+|Ok[.,]\s+|/\w+\s+)", flat)
    if m:
        flat = flat[m.end():]
    return flat[:FP_LEN]


def load_corpus_text():
    """Concatenate every extracted markdown body once. Returns (blob, file_count).

    Sidecars are excluded -- they carry per-message metadata, not message text, so a hit
    there would not prove the message is readable in the transcript.
    """
    blob, n = [], 0
    if not CORPUS.is_dir():
        return "", 0
    for p in CORPUS.rglob("*.md"):
        if p.name.endswith(".sidecar.md") or p.name == "index.md":
            continue
        try:
            blob.append(" ".join(p.read_text(encoding="utf-8", errors="ignore").split()))
            n += 1
        except OSError:
            continue
    return "\n".join(blob), n


def iter_jsonls(root, only_session=None):
    """Every session JSONL plus every nested subagent JSONL.

    The nesting is the whole point: subagent logs live at
    <slug>/<session-uuid>/subagents/agent-*.jsonl. A top-level glob takes ~9% of the
    record (measured 2026-08-03: 49 top-level vs 481 subagent) and reports success.
    """
    if not root.is_dir():
        return
    for slug in sorted(d for d in root.iterdir() if d.is_dir()):
        for jf in sorted(slug.glob("*.jsonl")):
            if only_session and only_session not in jf.stem:
                continue
            yield jf
        for sess in sorted(d for d in slug.iterdir() if d.is_dir()):
            if only_session and only_session not in sess.name:
                continue
            sub = sess / "subagents"
            if sub.is_dir():
                for jf in sorted(sub.glob("agent-*.jsonl")):
                    yield jf


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="restrict to one session uuid (substring match)")
    ap.add_argument("--projects-root", default=str(PROJECTS_ROOT))
    ap.add_argument("--verbose", action="store_true", help="list every message, not just misses")
    ap.add_argument("--self-test", action="store_true",
                    help="run the negative control and exit; proves the check can fail")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    corpus, corpus_files = load_corpus_text()
    if corpus_files == 0:
        print(f"[exit 2] corpus is empty or missing: {CORPUS}", file=sys.stderr)
        print("  An empty corpus makes every message look LOST. Refusing to report.",
              file=sys.stderr)
        return 2

    found = missing = 0
    per_file = []
    scanned = 0
    for jf in iter_jsonls(Path(args.projects_root), args.session):
        scanned += 1
        msgs = list(midturn_messages(jf))
        if not msgs:
            continue
        hits = miss = 0
        for ts, body in msgs:
            fp = fingerprint(body)
            if fp and fp in corpus:
                hits += 1
                if args.verbose:
                    print(f"  ok      {jf.name}  {ts}  {fp[:40]!r}")
            else:
                miss += 1
                print(f"  MISSING {jf.name}  {ts}  {fp[:40]!r}")
        found += hits
        missing += miss
        per_file.append((jf, len(msgs), hits, miss))

    if scanned == 0:
        print(f"[exit 2] scanned 0 JSONL files under {args.projects_root}", file=sys.stderr)
        print("  Zero scanned is not zero findings. Refusing to report a pass.", file=sys.stderr)
        return 2

    print()
    print("=== MID-TURN MESSAGE SCAN ===")
    print(f"  JSONL files scanned      : {scanned}")
    print(f"  files with mid-turn msgs : {len(per_file)}")
    print(f"  mid-turn messages found  : {found + missing}")
    print(f"  present in corpus        : {found}")
    print(f"  MISSING from corpus      : {missing}")
    print(f"  corpus files searched    : {corpus_files}")
    for jf, tot, hits, miss in per_file:
        flag = "  <- LOSS" if miss else ""
        print(f"    {jf.name:<44} {hits}/{tot}{flag}")

    if missing:
        print("\nRESULT: FAIL — Jon's words exist in a JSONL and in no extract.")
        return 1
    print("\nRESULT: PASS — every mid-turn message is represented in the corpus.")
    return 0


def self_test():
    """Negative control. A check that has never failed is not known to be able to.

    Feeds a synthetic mid-turn message that cannot be in the corpus and asserts the
    detector reports it MISSING; then feeds one that is trivially present and asserts
    it is found. Both must hold or the instrument is decoration.
    """
    corpus, n = load_corpus_text()
    if n == 0:
        print("SELF-TEST INCONCLUSIVE: corpus empty", file=sys.stderr)
        return 2

    absent_body = ("ZZQX-negative-control-" + "9f3a7c1e" * 4 +
                   " this string is not in any transcript")
    fp_absent = fingerprint(absent_body)
    ok_absent = fp_absent not in corpus

    # A string known to be in the corpus (one of Jon's real 2026-08-02 messages).
    present_body = "memores are KEY reference files for conversation, likable to and in G."
    fp_present = fingerprint(present_body)
    ok_present = fp_present in corpus

    # Wrapper filter must reject a non-mid-turn isMeta record.
    fake = json.dumps({"type": "user", "isMeta": True,
                       "message": {"content": [{"type": "text", "text": "some other meta"}]}})
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(fake + "\n")
        tmp = tf.name
    ok_filter = len(list(midturn_messages(tmp))) == 0
    os.unlink(tmp)

    # REGRESSION, 2026-08-03: the harness delivered a real Jon message with the wrapper
    # and NO isMeta field. The first build required isMeta and silently dropped it while
    # reporting PASS. A wrapper-bearing user record must qualify with isMeta absent.
    no_meta = json.dumps({"type": "user", "message": {"content": [
        {"type": "text", "text": WRAPPER + " a real message with no isMeta field"}]}})
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(no_meta + "\n")
        tmp2 = tf.name
    ok_nometa = len(list(midturn_messages(tmp2))) == 1
    os.unlink(tmp2)

    # REGRESSION, same day: dropping isMeta for "wrapper anywhere" counted a dispatch
    # brief that merely QUOTED the wrapper as Jon speaking. Position 0 or it is not his.
    quoted = json.dumps({"type": "user", "message": {"content":
        "Fences restated: the harness writes '" + WRAPPER + "' when Jon messages mid-turn."}})
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(quoted + "\n")
        tmp3 = tf.name
    ok_quoted = len(list(midturn_messages(tmp3))) == 0
    os.unlink(tmp3)

    print("=== SELF-TEST (negative control) ===")
    print(f"  absent string reported MISSING : {'PASS' if ok_absent else 'FAIL'}")
    print(f"  present string reported FOUND  : {'PASS' if ok_present else 'FAIL'}")
    print(f"  non-mid-turn isMeta rejected   : {'PASS' if ok_filter else 'FAIL'}")
    print(f"  wrapper WITHOUT isMeta accepted: {'PASS' if ok_nometa else 'FAIL'}")
    print(f"  wrapper merely QUOTED rejected : {'PASS' if ok_quoted else 'FAIL'}")
    if ok_absent and ok_present and ok_filter and ok_nometa and ok_quoted:
        print("\nRESULT: PASS — the check can both fire and stay silent.")
        return 0
    print("\nRESULT: FAIL — instrument is not trustworthy.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
