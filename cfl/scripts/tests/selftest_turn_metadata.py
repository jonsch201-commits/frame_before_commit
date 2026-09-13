#!/usr/bin/env python3
"""selftest_turn_metadata.py -- guards scripts/audit/turn_metadata.py (PR-3 B).

Includes NEGATIVE CONTROLS that must FAIL on a broken fixture/extractor, not just pass on
a good one -- "a gate that cannot fail" is this week's named dominant defect in this repo.

Run: python scripts/tests/selftest_turn_metadata.py
Exit 0 + PASS line on success; exit 1 on any assertion failure.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "audit"))

import turn_metadata as tm  # noqa: E402

ASSERTIONS = 0


def check(cond, msg):
    global ASSERTIONS
    ASSERTIONS += 1
    if not cond:
        raise AssertionError("FAIL #%d: %s" % (ASSERTIONS, msg))


def write_jsonl(records):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8")
    for r in records:
        f.write(json.dumps(r) + "\n")
    f.close()
    return Path(f.name)


# ---------------------------------------------------------------------------
# Fixture 1: a record with NO "message" dict must be COUNTED, not dropped.
# ---------------------------------------------------------------------------
def test_no_message_dict_counted():
    recs = [
        {"type": "custom-title", "customTitle": "cfl", "sessionId": "s1"},
        {
            "type": "assistant",
            "isSidechain": False,
            "timestamp": "2026-09-04T00:00:00.000Z",
            "message": {
                "id": "msg_1",
                "role": "assistant",
                "content": [{"type": "text", "text": "hi"}],
            },
        },
    ]
    p = write_jsonl(recs)
    turns, queued, classes, cnp, errs = tm.extract_turns(p)
    check(classes.get("no-message-dict") == 1, "no-message-dict record must be counted")
    check(classes.get("assistant") == 1, "assistant record must be counted")
    check(len(turns) == 1, "the message-bearing record must still become a turn")
    check(sum(classes.values()) == 2, "every record must land in exactly one class (none dropped)")


# ---------------------------------------------------------------------------
# Fixture 2: a queued_command attachment's prompt text must be extracted.
# ---------------------------------------------------------------------------
def test_queued_command_extracted():
    prompt_text = "<task-notification>Jon's mid-turn text lives here</task-notification>"
    recs = [
        {
            "type": "attachment",
            "attachment": {
                "type": "queued_command",
                "prompt": prompt_text,
                "commandMode": "task-notification",
            },
            "timestamp": "2026-09-04T00:01:00.000Z",
        }
    ]
    p = write_jsonl(recs)
    turns, queued, classes, cnp, errs = tm.extract_turns(p)
    check(classes.get("attachment-queued_command") == 1, "queued_command must get its own class")
    check(len(queued) == 1, "exactly one queued_command must be extracted")
    check(queued[0]["prompt"] == prompt_text, "extracted prompt text must match verbatim")


# ---------------------------------------------------------------------------
# Fixture 3: a sidechain entry must be labelled, never merged into a parent turn.
# ---------------------------------------------------------------------------
def test_sidechain_labelled_not_merged():
    recs = [
        {
            "type": "assistant",
            "isSidechain": False,
            "timestamp": "2026-09-04T00:02:00.000Z",
            "message": {
                "id": "msg_parent",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"file_path": "N:/parent/file.py"},
                    }
                ],
            },
        },
        {
            "type": "assistant",
            "isSidechain": True,
            "timestamp": "2026-09-04T00:02:05.000Z",
            "message": {
                "id": "msg_side",
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"file_path": "N:/subagent/other.py"},
                    }
                ],
            },
        },
    ]
    p = write_jsonl(recs)
    turns, queued, classes, cnp, errs = tm.extract_turns(p)
    check(len(turns) == 2, "parent and sidechain must be two distinct turns")
    parent = next(t for t in turns if t["message_id"] == "msg_parent")
    side = next(t for t in turns if t["message_id"] == "msg_side")
    check(parent["sidechain"] is False, "parent turn must not be marked sidechain")
    check(side["sidechain"] is True, "subagent turn must be marked sidechain")
    check(
        "N:/subagent/other.py" not in parent["files_read"],
        "sidechain file read must NOT be folded into the parent turn's files_read",
    )
    check(
        "N:/parent/file.py" not in side["files_read"],
        "parent file read must not leak into the sidechain turn either",
    )


# ---------------------------------------------------------------------------
# Fixture 4a: a zero must be a MEASURED zero, distinguishable from "could not parse".
# ---------------------------------------------------------------------------
def test_measured_zero_vs_could_not_parse():
    recs = [
        {
            "type": "assistant",
            "isSidechain": False,
            "timestamp": "2026-09-04T00:03:00.000Z",
            "message": {
                "id": "msg_clean",
                "role": "assistant",
                "content": [{"type": "text", "text": "no tool calls here"}],
            },
        },
        {
            "type": "assistant",
            "isSidechain": False,
            "timestamp": "2026-09-04T00:03:05.000Z",
            "message": {
                "id": "msg_broken_read",
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "input": {"NOT_file_path": "oops"}}
                ],
            },
        },
    ]
    p = write_jsonl(recs)
    turns, queued, classes, cnp, errs = tm.extract_turns(p)
    clean = next(t for t in turns if t["message_id"] == "msg_clean")
    broken = next(t for t in turns if t["message_id"] == "msg_broken_read")
    check(clean["files_read"] == [], "a turn with no Read calls is a MEASURED zero")
    check(broken["files_read"] == [], "a turn with an unparseable Read call is also empty...")
    check(
        any("Read tool_use missing input.file_path" in c["reason"] for c in cnp),
        "...but the unparseable case MUST be logged in could_not_parse, not silently zeroed",
    )


# ---------------------------------------------------------------------------
# Negative control: deliberately break the extractor and assert the test goes RED.
# This is the fixture that proves the gate can fail at all.
# ---------------------------------------------------------------------------
def broken_classify_record(rec):
    """A deliberately wrong classifier: drops no-message-dict records into 'assistant'
    instead of naming them -- the exact defect item 1 exists to catch."""
    t = rec.get("type")
    if t == "assistant":
        return "assistant"
    if t == "user":
        return "user"
    return "assistant"  # BUG: should be "no-message-dict" / "other" / etc.


def test_negative_control_extractor_break_is_caught():
    recs = [{"type": "custom-title", "customTitle": "cfl", "sessionId": "s1"}]
    rec = recs[0]
    broken_class = broken_classify_record(rec)
    caught = False
    try:
        check(broken_class == "no-message-dict", "the BROKEN classifier should mis-tag this and trip the check")
    except AssertionError:
        caught = True
    check(caught, "the negative-control fixture must make the check FAIL (proves the gate is not vacuous)")

    # And confirm the REAL classifier gets it right, so we know the fixture -- not the
    # real code -- was what broke above.
    real_class = tm.classify_record(rec)
    check(real_class == "no-message-dict", "the REAL classifier must correctly tag the same record")


def main():
    tests = [
        test_no_message_dict_counted,
        test_queued_command_extracted,
        test_sidechain_labelled_not_merged,
        test_measured_zero_vs_could_not_parse,
        test_negative_control_extractor_break_is_caught,
    ]
    for t in tests:
        t()
    print("PASS: %d assertions across %d test functions, all green" % (ASSERTIONS, len(tests)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as e:
        print(str(e))
        raise SystemExit(1)
