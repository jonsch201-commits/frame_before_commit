#!/usr/bin/env python3
"""HARVEST Jon's mid-turn messages -- the `queued_command` channel no renderer reads.

DO NOT ADOPT THIS INTO YOUR LINT. RUN IT. Federated by construction: point `--project-dir` at
any trunk's own project directory and it harvests that trunk. It names no trunk in its logic.

THE CHANNEL
-----------
When Jon types while a turn is still running, the harness QUEUES the message. It lands in the
session JSONL as `{"type": "attachment", "attachment": {"type": "queued_command", "prompt": ...}}`
-- NOT as `type: "user"`. Every window renderer and every transcript converter reads `type:
"user"`. So these messages:

  * do not appear in the rendered markdown transcript,
  * are not in the corpus the retrieval index embeds,
  * and if a compact consumes the queue before the message becomes a turn, the compact summary
    carries only a MACHINE PARAPHRASE of what he said.

    A searcher of rendered windows therefore concludes the primary is lost.
    It is not. The bytes are on disk, under a type nobody reads.

This is the same class as the zip-member row and the sibling-trunk row in the universal
constitution: THE VENUE IS REAL, IT IS ON THIS DISK, AND IT IS IN NO INSTRUMENT'S WALKED ROOTS.
The row for this channel was added to the universal layer on 2026-09-01; this script is
Professional's answer to it.

THE FILTER, AND IT IS THE ONLY JUDGMENT HERE
--------------------------------------------
Most queued_command entries are MACHINE traffic -- task notifications, cross-session messages,
hook output, slash-command echoes. `[m 2026-09-01, this trunk]` 205 total, 184 machine, 21
human-shaped. The filter is a PREFIX match on the machine envelopes, listed in one place below.

  * It is a heuristic and it can be wrong in BOTH directions. A Jon message that happens to open
    with one of those tokens is dropped; a machine message with a novel envelope is kept.
  * So the run prints BOTH counts, and `--all` emits the unfiltered set. A filter you cannot
    turn off is a filter nobody can check.
  * Verbatim is verbatim: typos, casing and profanity are HIS and are never cleaned. A
    "corrected" quote is an unverifiable quote, and emphasis added inside a quotation makes it
    unfindable by literal search -- which is the exact defect the constitution's typo rule
    exists to prevent, wearing the costume of formatting.

PII / EGRESS POSTURE, stated before it runs. Reads the local session JSONLs, writes a report to
stdout (or to `--out`). It never pushes, never leaves the trunk, and never writes to a sibling.
Jon 2026-08-19 places C:/G:/D: and non-public repos in one trust zone; `git remote -v` is empty
here by standing Jon gate.

Usage:
    python scripts/extract-jon-queued-commands.py              # human-shaped only
    python scripts/extract-jon-queued-commands.py --all        # unfiltered, to check the filter
    python scripts/extract-jon-queued-commands.py --out FILE   # write markdown instead of stdout
    python scripts/extract-jon-queued-commands.py --project-dir DIR   # any trunk
    python scripts/extract-jon-queued-commands.py --selftest
Exit: 0 harvested a non-empty population; 2 UNKNOWN (no files, or none readable).
"""
import glob
import json
import os
import sys

# cp1252 GUARD. Windows console stdout defaults to cp1252 while the filesystem is utf-8, so
# READING is fine and PRINTING dies -- invisible to any test that does not print. CFL hit this
# running this script on their trunk 2026-09-01 (U+2192); reproduced here 2026-09-02 on the same
# character, exit 1, before this line existed. Fails on Jon's own text: his corpus is full of
# arrows and emoji cp1252 cannot encode, and 38% of his captured utterances are the class this
# script harvests. Env-level equivalents that also work: PYTHONUTF8=1, PYTHONIOENCODING=utf-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass  # non-reconfigurable stream (piped/wrapped); the env vars remain the fallback

import time

# R4 (2026-09-04): default derived by scripts/project_dirs.py, never typed.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import project_dirs as _pd
_dirs = _pd.existing_dirs(_pd.ROOT)
DEFAULT_PROJECT_DIR = _dirs[0] if _dirs else "UNKNOWN-no-project-dir"

# The machine envelopes. One place, so removing one is a deliberate edit.
MACHINE_PREFIXES = (
    "<task-notification>",
    "<cross-session-message",
    "<system-reminder>",
    "<local-command",
    "<command-name>",
    "<command-message>",
    "<user-prompt-submit-hook>",
    "[Cross-session",
)


def is_machine(prompt):
    return prompt.lstrip().startswith(MACHINE_PREFIXES)


def harvest(project_dir, keep_all=False):
    """-> (rows, stats). A file we cannot read is UNKNOWN and is COUNTED, never dropped."""
    rows = []
    stats = {"files": 0, "unreadable": 0, "lines": 0, "queued": 0, "machine": 0, "unparseable": 0}
    for path in sorted(glob.glob(os.path.join(project_dir, "*.jsonl"))):
        stats["files"] += 1
        sid = os.path.basename(path)[:-6]
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            stats["unreadable"] += 1
            continue
        with fh:
            for lineno, line in enumerate(fh, 1):
                stats["lines"] += 1
                # ⛔ PARSE FIRST, FILTER SECOND. The first draft used `if '"queued_command"'
                #    not in line: continue` as a fast path BEFORE the parse -- so a CORRUPT
                #    line was skipped without ever being counted, and a record we could not
                #    read was reported as a record that was not there. Its own selftest
                #    caught it on the first run, which is the entire argument for writing the
                #    negative case before trusting the instrument.
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    stats["unparseable"] += 1
                    continue
                if not isinstance(obj, dict):
                    stats["unparseable"] += 1
                    continue
                att = obj.get("attachment") or {}
                if att.get("type") != "queued_command":
                    continue
                stats["queued"] += 1
                prompt = (att.get("prompt") or "").strip()
                if not prompt:
                    continue
                if is_machine(prompt):
                    stats["machine"] += 1
                    if not keep_all:
                        continue
                rows.append({
                    "session": sid,
                    "short": sid[:8],
                    "line": lineno,
                    "ts": obj.get("timestamp", ""),
                    "prompt": prompt,
                    "machine": is_machine(prompt),
                })
    rows.sort(key=lambda r: (r["ts"], r["short"], r["line"]))
    return rows, stats


def render(rows, stats, project_dir, keep_all, fm_name=None):
    out = []
    if fm_name:
        # Frontmatter is EMITTED BY THE GENERATOR, never hand-added afterwards. A generated
        # page whose header a human maintains is a page that drifts from its own generator on
        # the first re-run, and this file is re-run every time the population changes.
        out.append("---")
        out.append("name: %s" % fm_name)
        out.append("description: Jon's own words typed MID-TURN in this trunk, harvested from the "
                   "`queued_command` attachment class that no transcript renderer reads. "
                   "GENERATED -- re-run the script, never edit this file.")
        out.append("kind: source")
        out.append("created: %s" % time.strftime("%Y-%m-%d"))
        out.append("sensitivity: routine -- Jon's own words to his own tooling, local-only, "
                   "no third party named by this harvest")
        out.append("calibration: [measured] -- every quote is a verbatim `prompt` field with its "
                   "JSONL file and line number; typos, casing and profanity are his and are not cleaned")
        out.append("generated_by: scripts/extract-jon-queued-commands.py")
        out.append("---")
        out.append("")
    out.append("# Jon's mid-turn messages -- the `queued_command` channel")
    out.append("")
    out.append("`[measured]` harvested by `scripts/extract-jon-queued-commands.py` from")
    out.append("`%s`" % project_dir)
    out.append("")
    out.append("| population | count |")
    out.append("|---|---|")
    out.append("| session JSONL files scanned | %d |" % stats["files"])
    out.append("| files UNREADABLE (UNKNOWN, counted not dropped) | %d |" % stats["unreadable"])
    out.append("| JSONL lines read | %d |" % stats["lines"])
    out.append("| `queued_command` attachments | %d |" % stats["queued"])
    out.append("| of those, machine envelopes (filtered) | %d |" % stats["machine"])
    out.append("| unparseable lines (UNKNOWN, counted not dropped) | %d |" % stats["unparseable"])
    out.append("| **emitted below** | **%d** |" % len(rows))
    out.append("")
    out.append("**The filter is a PREFIX match on machine envelopes and it can be wrong in BOTH "
               "directions.** Re-run with `--all` to see the unfiltered set. "
               "**Typos, casing and profanity are his and are never cleaned.**")
    out.append("")
    for r in rows:
        tag = " *(machine envelope)*" if r["machine"] else ""
        out.append("---")
        out.append("")
        out.append("**`%s`  ·  `%s.jsonl:%d`**%s" % (r["ts"][:19] or "no timestamp", r["session"],
                                                     r["line"], tag))
        out.append("")
        for para in r["prompt"].split("\n"):
            out.append("> %s" % para if para.strip() else ">")
        out.append("")
    return "\n".join(out) + "\n"


def selftest():
    import tempfile
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "0123456789abcdef.jsonl")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "attachment", "timestamp": "2026-01-01T00:00:00Z",
                                 "attachment": {"type": "queued_command",
                                                "prompt": "real words from a person"}}) + "\n")
            fh.write(json.dumps({"type": "attachment", "timestamp": "2026-01-01T00:00:01Z",
                                 "attachment": {"type": "queued_command",
                                                "prompt": "<task-notification> machine"}}) + "\n")
            fh.write(json.dumps({"type": "user", "message": {"content": "an ordinary turn"}}) + "\n")
            fh.write("{ this line is not json\n")

        rows, stats = harvest(d)
        if len(rows) != 1 or rows[0]["prompt"] != "real words from a person":
            print("FAIL [filter] expected exactly the human row, got %r" % [r["prompt"] for r in rows])
            fails += 1
        else:
            print("PASS [filter] machine envelope dropped, human row kept")

        if stats["machine"] != 1:
            print("FAIL [count-machine] the dropped row must still be COUNTED; got %d" % stats["machine"])
            fails += 1
        else:
            print("PASS [count-machine] filtered row counted, not silently vanished")

        if stats["unparseable"] != 1:
            print("FAIL [unparseable] a bad line must be counted as UNKNOWN; got %d" % stats["unparseable"])
            fails += 1
        else:
            print("PASS [unparseable] bad line counted as UNKNOWN, never dropped silently")

        allrows, _ = harvest(d, keep_all=True)
        if len(allrows) != 2:
            print("FAIL [--all] the filter must be defeatable; got %d row(s)" % len(allrows))
            fails += 1
        else:
            print("PASS [--all] filter is defeatable, so it can be checked")

        # a type: user turn must NOT be harvested -- this channel is specifically the one
        # renderers already read nothing from
        if any("ordinary turn" in r["prompt"] for r in allrows):
            print("FAIL [scope] a type:user turn leaked into the queued_command harvest")
            fails += 1
        else:
            print("PASS [scope] type:user turns are out of scope by construction")

        empty, st2 = harvest(os.path.join(d, "nope"))
        if empty or st2["files"] != 0:
            print("FAIL [empty] a missing dir must yield zero files, and the caller returns UNKNOWN")
            fails += 1
        else:
            print("PASS [empty] missing dir -> 0 files -> caller returns UNKNOWN, never a pass")

    print("---")
    print("SELFTEST: %s (%d failing)" % ("PASS" if fails == 0 else "FAIL", fails))
    return 0 if fails == 0 else 3


def main(argv):
    if "--selftest" in argv:
        return selftest()
    project_dir = DEFAULT_PROJECT_DIR
    if "--project-dir" in argv:
        project_dir = argv[argv.index("--project-dir") + 1]
    keep_all = "--all" in argv
    rows, stats = harvest(project_dir, keep_all)

    if stats["files"] == 0:
        print("UNKNOWN -- no session JSONL found under %s. A zero population is UNKNOWN, never a pass."
              % project_dir)
        return 2
    if stats["unreadable"] == stats["files"]:
        print("UNKNOWN -- all %d file(s) unreadable." % stats["files"])
        return 2

    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    fm_name = os.path.basename(out)[:-3] if out and out.endswith(".md") else None
    text = render(rows, stats, project_dir, keep_all, fm_name)
    if out:
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %d row(s) -> %s" % (len(rows), out))
        print("scanned %d file(s), %d line(s); %d queued_command, %d machine-filtered, "
              "%d unreadable, %d unparseable"
              % (stats["files"], stats["lines"], stats["queued"], stats["machine"],
                 stats["unreadable"], stats["unparseable"]))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
