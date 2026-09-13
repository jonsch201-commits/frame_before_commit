#!/usr/bin/env python3
"""selftest_mint_window.py — runs mint_window.py against the REAL session JSONL
and asserts equality against independently measured constants.

The constants below were measured by a separate hand-written probe, not by the
emitter. If a run disagrees, adjust the EMITTER, never these.

Also runs a synthetic fixture (fixture_queued_command) covering the
queued_command / commandMode render path (RP-27, v1.1): one Jon-typed row as
a plain string, one Jon-typed row as a content-block list, one machine row
carrying commandMode, and one machine row with NO commandMode at all (must
be caught by the MACHINE_PREFIXES fallback). This fixture FAILS against the
v1 emitter (etype "attachment" is not handled at all — no queued_human /
queued_machine / queued_by_mode keys ever appear in frontmatter) and PASSES
against v1.1.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MINT = os.path.join(HERE, "mint_window.py")
JSONL = (r"C:\Users\JonSc\.claude\projects"
         r"\G--My-Drive-Claude-Claude-Foundational-Layer-claude-foundational-layer"
         r"\9041f3b0-5102-4a06-a459-b076681a76bd.jsonl")
LO = "2026-08-31T18:27:22"
HI = "2026-08-31T20:39:43"

EXPECTED = {
    "total_messages": 209,
    "user_text_turns": 7,
    "assistant_text_blocks": 7,
    "tool_calls": 45,
    "thinking_blocks": 30,
}

failures = []


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                       (" — " + str(detail)) if detail else ""))
    if not ok:
        failures.append(name)


def run_mint(out, jsonl=None, lo=None, hi=None):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, MINT, jsonl or JSONL, lo or LO, hi or HI,
                        "--out", out], capture_output=True, text=True, env=env)
    return r


FIXTURE_LO = "2026-01-01T00:00:00"
FIXTURE_HI = "2026-01-01T00:01:00"

FIXTURE_ROWS = [
    # 1. Jon-typed, prompt is a plain string.
    {"type": "attachment", "timestamp": "2026-01-01T00:00:10.000Z",
     "attachment": {"type": "queued_command", "commandMode": "prompt",
                    "prompt": "fix the wiki gap you keep skipping"}},
    # 2. Jon-typed, prompt is a content-block list (Secretary hit this shape).
    {"type": "attachment", "timestamp": "2026-01-01T00:00:20.000Z",
     "attachment": {"type": "queued_command", "commandMode": "prompt",
                    "prompt": [{"type": "text", "text": "and check the "},
                               {"type": "text", "text": "other trunk too"}]}},
    # 3. Machine row, commandMode says so directly.
    {"type": "attachment", "timestamp": "2026-01-01T00:00:30.000Z",
     "attachment": {"type": "queued_command", "commandMode": "task-notification",
                    "prompt": "Background task completed: pipeline run finished"}},
    # 4. Machine row with NO commandMode at all — must be caught by the
    #    MACHINE_PREFIXES fallback, not silently defaulted to human.
    {"type": "attachment", "timestamp": "2026-01-01T00:00:40.000Z",
     "attachment": {"type": "queued_command",
                    "prompt": "<system-reminder>session state refreshed</system-reminder>"}},
]


def fixture_queued_command():
    tmpdir = tempfile.mkdtemp(prefix="mint_selftest_fixture_")
    fixture_jsonl = os.path.join(tmpdir, "fixture.jsonl")
    with open(fixture_jsonl, "w", encoding="utf-8", newline="\n") as f:
        for row in FIXTURE_ROWS:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    out = os.path.join(tmpdir, "fixture_out.md")

    r = run_mint(out, jsonl=fixture_jsonl, lo=FIXTURE_LO, hi=FIXTURE_HI)
    check("fixture: emitter exit 0", r.returncode == 0, r.stderr.strip()[:300])
    if r.returncode != 0:
        return

    with open(out, encoding="utf-8") as f:
        doc = f.read()
    fm_end = doc.index("\n---\n", 4)
    fm = doc[:fm_end]
    body = doc[fm_end + 5:]

    for key, want in (("queued_human", 2), ("queued_machine", 2)):
        m = re.search(r"^%s: (\d+)$" % key, fm, re.M)
        got = int(m.group(1)) if m else None
        check("fixture: frontmatter %s == %d" % (key, want), got == want, "got %s" % got)

    # Distribution, not row count — this is the assertion that stays honest
    # if commandMode ever stops being read: prompt=2, task-notification=1,
    # (none)=1. A row-count-only check would pass even if every row silently
    # fell into one bucket.
    m = re.search(r"^queued_by_mode: \{(.*)\}$", fm, re.M)
    dist = {}
    if m:
        for part in m.group(1).split(", "):
            if not part.strip():
                continue
            k, v = part.rsplit(": ", 1)
            dist[k] = int(v)
    want_dist = {"prompt": 2, "task-notification": 1, "(none)": 1}
    check("fixture: queued_by_mode distribution == %r" % want_dist,
          dist == want_dist, "got %r" % dist)

    check("fixture: body has 2 '## Human (queued, commandMode=prompt)' headings",
          len(re.findall(r"^## Human \(queued, commandMode=prompt\) \[", body, re.M)) == 2)
    check("fixture: body has the list-form prompt text joined",
          "and check the \n\nother trunk too" in body)
    check("fixture: body has 1 machine row with commandMode=task-notification",
          len(re.findall(r"^## Machine \(queued, commandMode=task-notification\) \[", body, re.M)) == 1)
    check("fixture: body has 1 machine row with commandMode=(none) (prefix fallback)",
          len(re.findall(r"^## Machine \(queued, commandMode=\(none\)\) \[", body, re.M)) == 1)
    check("fixture: no '## Human' heading precedes the machine-shaped text",
          not re.search(r"^## Human[^\n]*\n\n[^\n]*<system-reminder>", body, re.M))


def main():
    tmpdir = tempfile.mkdtemp(prefix="mint_selftest_")
    out1 = os.path.join(tmpdir, "run1.md")
    out2 = os.path.join(tmpdir, "run2.md")

    r = run_mint(out1)
    check("emitter exit 0", r.returncode == 0, r.stderr.strip()[:200])
    if r.returncode != 0:
        return 1

    with open(out1, encoding="utf-8") as f:
        doc = f.read()
    fm_end = doc.index("\n---\n", 4)
    fm = doc[:fm_end]
    body = doc[fm_end + 5:]

    # Frontmatter values
    for key, want in EXPECTED.items():
        m = re.search(r"^%s: (\d+)$" % key, fm, re.M)
        got = int(m.group(1)) if m else None
        check("frontmatter %s == %d" % (key, want), got == want, "got %s" % got)

    # Body heading counts must equal frontmatter counts
    n_assist = len(re.findall(r"^## Assistant \[", body, re.M))
    n_human = len(re.findall(r"^## Human \[", body, re.M))
    check("body '## Assistant' headings == %d" % EXPECTED["assistant_text_blocks"],
          n_assist == EXPECTED["assistant_text_blocks"], "got %d" % n_assist)
    check("body '## Human' headings == %d" % EXPECTED["user_text_turns"],
          n_human == EXPECTED["user_text_turns"], "got %d" % n_human)

    # No '## Assistant' heading without a following nonempty text line
    lines = body.split("\n")
    empty_headed = 0
    for i, ln in enumerate(lines):
        if ln.startswith("## Assistant ["):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or lines[j].startswith(("## ", "- TOOL ", "- RESULT ")):
                empty_headed += 1
    check("zero '## Assistant' headings without following nonempty text",
          empty_headed == 0, "found %d" % empty_headed)

    # Reproducibility: run twice, byte-identical
    r2 = run_mint(out2)
    check("second run exit 0", r2.returncode == 0, r2.stderr.strip()[:200])
    with open(out1, "rb") as a, open(out2, "rb") as b:
        check("two runs byte-identical", a.read() == b.read())

    fixture_queued_command()

    print("RESULT: %s (%d failures)" %
          ("ALL PASS" if not failures else "FAIL", len(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
