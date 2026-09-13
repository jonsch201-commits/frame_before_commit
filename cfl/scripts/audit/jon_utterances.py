#!/usr/bin/env python3
"""jon_utterances.py — THE DENOMINATOR. Jon's own words, enumerated as units.

WHY THIS EXISTS
---------------
Jon's standard, verbatim:

    "Every word I've ever said should likely impact at least one concept, or have it's
     negative citation explained. You should consider if the explanation is valid."

Measured against that standard on 2026-08-06: ~8 rulings from him in the session, one concept
page touched — and that one came from a ticket, not from him. Negative citations explained: **0,
not explained badly, ABSENT.**

But the more serious finding was upstream of the ratio. **Nothing in this repo enumerates Jon's
utterances as units.** There is no list of them anywhere. A standard of the form "every X should
do Y" cannot be measured — cannot even be *stated* as a fraction — until X has a denominator, and
X had none. The standard was not merely unmet; it was **unmeasurable**.

This module is the denominator. It does one job: turn a session's JSONLs into an explicit,
countable, printable list of the things Jon said. It makes no claim about what happened to any of
them — that is `check_jon_word_coverage.py`'s job, and keeping the two apart is deliberate, so
that a change to the impact matcher can never quietly change how many utterances there were.

WHERE JON'S WORDS ACTUALLY LIVE — TWO PLACES, AND ONLY ONE WAS EVER SCANNED
---------------------------------------------------------------------------
1. **Main-thread turns.** `type: user` records in the SESSION jsonl whose content is a string.
   This is the only place Jon's ordinary typed prose exists.
2. **Mid-turn messages to running subagents.** These are delivered *inside the subagent's turn*
   and land in `<session>/subagents/agent-*.jsonl`, never in the main thread. On 2026-08-02 nine
   of them were treated as fabrications because main never saw them. `scan_midturn_messages.py`
   already implements the detector for these, correctly and expensively (three regressions are
   recorded in its docstring). **It is imported, never re-implemented.**

NOTHING IS SILENTLY DROPPED — THE EXCLUSIONS ARE A LEDGER, NOT A FILTER
------------------------------------------------------------------------
`type: user` in a Claude Code JSONL is a wildly overloaded record class. Measured on session
f01909 (2026-08-06): 627 tool-result carriers, 27 harness meta records, 5 skill-body injections,
1 compaction summary, and 88 string records — of which **58 were `<task-notification>` payloads
and slash-command envelopes, not Jon speaking at all.**

So every record is classified into exactly one class and **every class is counted and reported**,
including the excluded ones. A denominator whose exclusions are invisible is the same defect as a
gate that passes by resolving nothing. The classes:

  COUNTED (these are Jon's words):
    `typed`       — his own prose, typed into the box.
    `slash-args`  — the argument text he typed after a slash command (`/grill-me <his words>`).
                    The command name is a harness token; the args are his.
    `midturn`     — a message sent into a running subagent.

  NOT COUNTED, BUT COUNTED (reported with their totals, never hidden):
    `invocation`  — a bare slash command with empty args (`/wake`, `/compact`, `/su`). An ACT,
                    not an utterance. It carries intent but no words to cite.
    `interrupt`   — `[Request interrupted by user]`. An act. Same reasoning.
    `envelope`    — `<task-notification>`, `<local-command-stdout>`, `<local-command-caveat>`,
                    hook feedback, system reminders. Harness-authored; Jon never typed them.
    `tool-result` — content is a list of tool_result blocks. The harness echoing tool output.
    `injected`    — `isMeta` skill bodies and command bodies the harness pastes in.
    `compact`     — the compaction summary. Assistant-authored, delivered as a user record.

THE SLASH-COMMAND CASE IS THE ONE THAT WOULD HAVE BEEN GOT WRONG
------------------------------------------------------------------
`<command-args>` is where Jon's real instruction goes when he uses a skill: on 2026-08-06 both
`/caveman explain your questions to me...` and `/grill-me in wiki orginization. I can provide
clarity on next s...` carried substantive direction inside the args. Dropping the whole envelope
because it starts with `<command-` would have deleted two real utterances from the denominator —
and a denominator that is too small makes every coverage ratio look BETTER than it is. Every
exclusion rule here was checked against real records for exactly this failure direction.

ANCHORING
---------
Utterances are joined to `T{n}` turn numbers through the sidecar, on **`uuid`**, not timestamp.
Timestamps are not monotonic in these files — verified on f01909, where T1 is stamped
`05:19:03.020Z` and T2 `05:19:02.849Z`, i.e. the second turn is stamped 171 ms BEFORE the first.
A timestamp join would have silently mis-anchored. `uuid` is exact and unique per record; the
timestamp remains as a fallback for records the sidecar carries only by time (mid-turn messages,
which live in a child transcript and have no row in the parent's sidecar).
"""
import json
import os
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# REUSE, NOT REIMPLEMENTATION. scan_midturn_messages' detector cost three recorded regressions
# to get right (isMeta required -> recall loss; "wrapper anywhere" -> false positives; the fix
# was position-0). Writing a second one here would re-open all three.
from scan_midturn_messages import midturn_messages  # noqa: E402

PROJECTS_ROOT = Path(os.path.expanduser("~")) / ".claude" / "projects"

# Harness-authored envelopes. Matched at position 0 only — the same discriminator
# scan_midturn_messages arrived at, and for the same reason: a message that MENTIONS
# `<task-notification>` is Jon talking about the harness, not the harness talking.
ENVELOPE_PREFIXES = (
    "<task-notification>",
    "<local-command-stdout>",
    "<local-command-caveat>",
    "<system-reminder>",
    "<user-prompt-submit-hook>",
    "<bash-stdout>",
    "<bash-stderr>",
    "Stop hook feedback:",
    "PreToolUse:",
    "PostToolUse:",
    "Caveat: The messages below were generated by the user while running local commands",
)

_CMD_ARGS_RE = re.compile(r"<command-args>(.*?)</command-args>", re.DOTALL)
_CMD_NAME_RE = re.compile(r"<command-name>(.*?)</command-name>", re.DOTALL)
_INTERRUPT_RE = re.compile(r"^\[Request interrupted by user")

# A bare slash command with no prose: `/wake`, `/compact`, `/su`, `/clear`.
_BARE_SLASH_RE = re.compile(r"^/[A-Za-z][\w:-]*\s*$")

COUNTED_CLASSES = ("typed", "slash-args", "midturn")
LEDGER_CLASSES = COUNTED_CLASSES + (
    "invocation", "interrupt", "envelope", "tool-result", "injected", "compact", "empty")


def _text_of(content):
    """Flatten a message content field to text, or '' when it carries no text blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text")
    return ""


def classify_user_record(o):
    """(cls, text) for one `type: user` JSONL record. Exactly one class, always.

    `text` is Jon's words when cls is counted, and the raw payload otherwise (kept so the caller
    can show a sample of what it excluded rather than asking the reader to trust the label).
    """
    if o.get("isCompactSummary"):
        return "compact", _text_of((o.get("message") or {}).get("content"))
    content = (o.get("message") or {}).get("content")
    if isinstance(content, list):
        if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
            return "tool-result", ""
        txt = _text_of(content).strip()
        if _INTERRUPT_RE.match(txt):
            return "interrupt", txt
        # isMeta list-text records are harness injections (skill bodies, command bodies).
        if o.get("isMeta"):
            return "injected", txt
        return ("typed", txt) if txt else ("empty", "")
    if not isinstance(content, str):
        return "empty", ""

    s = content.strip()
    if not s:
        return "empty", ""
    if o.get("isMeta"):
        # isMeta strings on this path are hook feedback and local-command caveats.
        return "envelope", s
    for p in ENVELOPE_PREFIXES:
        if s.startswith(p):
            return "envelope", s
    if _INTERRUPT_RE.match(s):
        return "interrupt", s
    if "<command-name>" in s or "<command-message>" in s:
        m = _CMD_ARGS_RE.search(s)
        args = (m.group(1).strip() if m else "")
        if args:
            # THE CASE THAT WOULD HAVE BEEN LOST. `/grill-me <real instruction>` — the command
            # name is a harness token, the args are Jon dictating scope.
            name = _CMD_NAME_RE.search(s)
            prefix = (name.group(1).strip() + " ") if name else ""
            return "slash-args", (prefix + args).strip()
        return "invocation", s
    if _BARE_SLASH_RE.match(s):
        return "invocation", s
    return "typed", s


def sidecar_anchor_map(sidecar_path):
    """({uuid -> (turn, role)}, {timestamp -> (turn, role)}) from a per-turn provenance sidecar.

    Both maps are built in one pass. `uuid` is the join that is used; `timestamp` is the fallback
    for records with no sidecar row of their own. See the module docstring for why the timestamp
    join alone is not safe here.
    """
    by_uuid, by_ts = {}, {}
    p = Path(sidecar_path) if sidecar_path else None
    if not p or not p.is_file():
        return by_uuid, by_ts
    cur = None
    hdr = re.compile(r"^###\s+T(\d+)\s*[—\-]\s*(.+?)\s*$")
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\n")
                m = hdr.match(line)
                if m:
                    cur = (int(m.group(1)), m.group(2))
                    continue
                if not cur:
                    continue
                m = re.match(r"^-\s+uuid:\s*(\S+)\s*$", line)
                if m:
                    by_uuid.setdefault(m.group(1), cur)
                    continue
                m = re.match(r"^-\s+timestamp:\s*(\S+)\s*$", line)
                if m:
                    by_ts.setdefault(m.group(1), cur)
    except OSError:
        pass
    return by_uuid, by_ts


def main_thread_utterances(jsonl_path, sidecar_path=None):
    """([utterance dicts], {class -> count}, [(class, sample) ...]).

    Every `type: user` record is classified; the counts dict is the full ledger, so
    sum(counts.values()) is the record total and the reader can see what was set aside.
    """
    by_uuid, by_ts = sidecar_anchor_map(sidecar_path)
    out, counts, samples = [], {c: 0 for c in LEDGER_CLASSES}, []
    seen_sample = set()
    idx = 0
    try:
        fh = open(jsonl_path, encoding="utf-8", errors="ignore")
    except OSError:
        return out, counts, samples
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get("type") != "user":
                continue
            cls, text = classify_user_record(o)
            counts[cls] = counts.get(cls, 0) + 1
            if cls not in COUNTED_CLASSES:
                if cls not in seen_sample and text:
                    seen_sample.add(cls)
                    samples.append((cls, " ".join(text.split())[:110]))
                continue
            idx += 1
            uid = o.get("uuid")
            ts = o.get("timestamp")
            anchor = by_uuid.get(uid) or by_ts.get(ts)
            out.append({
                "n": idx,
                "cls": cls,
                "text": text,
                "chars": len(text),
                "uuid": uid,
                "timestamp": ts,
                "turn": anchor[0] if anchor else None,
                "role": anchor[1] if anchor else None,
                "venue": "main",
                "source": str(jsonl_path),
            })
    return out, counts, samples


def subagent_dir_for(jsonl_path):
    """`<session>/subagents/` for a top-level session JSONL, or None."""
    p = Path(jsonl_path)
    d = p.with_suffix("")            # ~/.claude/projects/<slug>/<uuid>
    sub = d / "subagents"
    return sub if sub.is_dir() else None


def midturn_utterances(jsonl_path, start_n=0):
    """([utterance dicts], n_raw, n_duplicate) for Jon's mid-turn messages into this session's
    subagents.

    Deduplicated on normalised text WITHIN the session: one message sent while three agents are
    running is delivered to all three and appears three times on disk. It is ONE thing Jon said.
    The duplicate count is returned rather than discarded, because a duplicate is evidence of
    fan-out and a reader should see it.
    """
    sub = subagent_dir_for(jsonl_path)
    out, raw, dup = [], 0, 0
    if not sub:
        return out, raw, dup
    seen = {}
    for jf in sorted(sub.glob("agent-*.jsonl")):
        agent_id = jf.stem[len("agent-"):]
        for ts, body in midturn_messages(jf):
            raw += 1
            key = normalize(body)
            if key in seen:
                dup += 1
                seen[key]["delivered_to"].append(agent_id[:6])
                continue
            rec = {
                "n": start_n + len(out) + 1,
                "cls": "midturn",
                "text": body,
                "chars": len(body),
                "uuid": None,
                "timestamp": ts,
                "turn": None,
                "role": None,
                "venue": "subagent",
                "delivered_to": [agent_id[:6]],
                "source": str(jf),
            }
            seen[key] = rec
            out.append(rec)
    return out, raw, dup


def normalize(text):
    """Whitespace-collapsed, case-folded. The one normalisation, used by every matcher.

    `find_unechoed_rulings.py` learned this the hard way on 2026-08-06: matching raw substrings
    against a wiki that hard-wraps its prose produced **five zero-echo flags, all five false** —
    the echoes were sitting on the next line. Collapsing every whitespace run (newlines included)
    to one space, and case-folding, fixed all five. Both halves are needed; the T4001 case had a
    line-wrap AND a sentence-start re-capitalisation stacked.
    """
    return " ".join(str(text or "").split()).casefold()


def enumerate_session(jsonl_path, sidecar_path=None):
    """The whole denominator for one session.

    Returns a dict with `utterances` (the counted units, main-thread first then mid-turn),
    `class_counts` (the full ledger including exclusions), `excluded_samples`,
    `midturn_raw`, `midturn_dupes`.
    """
    main, counts, samples = main_thread_utterances(jsonl_path, sidecar_path)
    mid, raw, dup = midturn_utterances(jsonl_path, start_n=len(main))
    counts = dict(counts)
    counts["midturn"] = len(mid)
    return {
        "jsonl": str(jsonl_path),
        "utterances": main + mid,
        "class_counts": counts,
        "excluded_samples": samples,
        "midturn_raw": raw,
        "midturn_dupes": dup,
    }


def self_test():
    """Negative control. Each classification rule is asserted against a record it must NOT eat.

    The direction that matters is the one that inflates a score: a rule that over-excludes shrinks
    the denominator and makes coverage look better than it is. Every case below is checked in that
    direction as well as the obvious one.
    """
    def rec(content, **kw):
        d = {"type": "user", "message": {"content": content}}
        d.update(kw)
        return d

    cases = [
        # (label, record, expected class, expected-text-contains or None)
        ("plain prose is Jon",
         rec("Getting worse is getting better if worse is more true than the prior measure."),
         "typed", "Getting worse"),
        ("task-notification is NOT Jon",
         rec("<task-notification>\n<task-id>abc</task-id>\n"), "envelope", None),
        ("bare slash is an act, not an utterance", rec("/wake"), "invocation", None),
        ("slash WITH args keeps the args",
         rec("<command-message>grill-me</command-message>\n<command-name>/grill-me</command-name>"
             "\n<command-args>in wiki orginization. I can provide clarity.</command-args>"),
         "slash-args", "wiki orginization"),
        ("slash with EMPTY args is an invocation",
         rec("<command-name>/compact</command-name>\n<command-args></command-args>"),
         "invocation", None),
        ("tool_result carrier is not a turn",
         rec([{"type": "tool_result", "content": "x"}]), "tool-result", None),
        ("interrupt is an act", rec("[Request interrupted by user]"), "interrupt", None),
        ("isMeta skill body is injected",
         rec([{"type": "text", "text": "Base directory for this skill: ..."}], isMeta=True),
         "injected", None),
        ("compact summary is assistant-authored",
         rec("This session is being continued...", isCompactSummary=True), "compact", None),
        ("hook feedback is not Jon", rec("Stop hook feedback:\nPRE-STOP CONSULT", isMeta=True),
         "envelope", None),
        # THE OVER-EXCLUSION CONTROL: prose that merely MENTIONS an envelope token is still Jon.
        ("prose mentioning <task-notification> is still Jon",
         rec("Stop dumping <task-notification> payloads into my context, they are noise."),
         "typed", "Stop dumping"),
        # THE OVER-INCLUSION CONTROL: a slash-looking word mid-sentence is not an invocation.
        ("a slash mid-sentence is prose",
         rec("Use the /wake path, not the other one."), "typed", "Use the"),
    ]
    ok = True
    print("=== SELF-TEST — jon_utterances classification (negative controls) ===")
    for label, r, want, contains in cases:
        got, text = classify_user_record(r)
        good = (got == want) and (contains is None or contains in text)
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  {label:<52} -> {got}")

    # normalize() must defeat a hard line-wrap AND a case change — the find_unechoed_rulings bug.
    a = normalize("Focusing on 100%\n   generally makes things Worse")
    b = normalize("focusing on 100% generally makes things worse")
    print(f"  {'PASS' if a == b else 'FAIL'}  wrap+case normalisation collapses to one form")
    ok = ok and (a == b)

    print("\nRESULT: " + ("PASS — the classifier can both admit and reject."
                          if ok else "FAIL — do not trust the denominator."))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    if len(sys.argv) > 1:
        d = enumerate_session(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
        print(f"counted utterances : {len(d['utterances'])}")
        print(f"class ledger       : {json.dumps(d['class_counts'])}")
        for u in d["utterances"]:
            anc = f"T{u['turn']}" if u["turn"] else u["venue"]
            print(f"  {u['n']:>3}  {u['cls']:<11} {anc:<8} {u['chars']:>6}  "
                  f"{' '.join(u['text'].split())[:90]}")
        sys.exit(0)
    print(__doc__)
    sys.exit(0)
