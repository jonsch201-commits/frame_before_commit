#!/usr/bin/env python3
"""selftest_extract_compact_summary.py — fixture-based self-test for
extract_compact_summary.py.

Builds a synthetic session JSONL with:
  1. A real user turn Jon typed verbatim, still present in the window.
  2. A compact-summary record (isCompactSummary: true) that:
       - quotes turn 1 VERBATIM (must grade FOUND-VERBATIM)
       - paraphrases a second thing Jon said, close but not exact
         (must grade FOUND-NEAR)
       - quotes a sentence that exists ONLY as a queued_command attachment
         entry, never as a normal user turn (must grade
         FOUND-IN-QUEUED-ONLY — the RP-27 class)
  3. The queued_command attachment entry backing case 3.
  4. A PreCompact receipt bounding the window, so diff_one_summary can
     locate real bounds instead of falling back to whole-session UNKNOWN.

Also proves the queued_command branch is load-bearing: re-running the same
quote with check_queued=False must NOT return FOUND-IN-QUEUED-ONLY. If
someone disables/removes that branch, the case-3 assertion below fails.
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_compact_summary as ecs  # noqa: E402

SESSION_ID = "abc12345-0000-4000-8000-000000000001"
SESS6 = SESSION_ID.replace("-", "")[:6]

VERBATIM_TEXT = "Rules that produce stopping are defective rules and I want that fixed today"
PARAPHRASE_SOURCE = "the fence around what you may do is wider than you think it is"
PARAPHRASE_IN_SUMMARY = "the fence around what he may do is much wider than assumed"
QUEUED_ONLY_TEXT = "sorry for the spam, please also add the unlazy skill now"

failures = []
n_checks = [0]


def check(name, ok, detail=""):
    n_checks[0] += 1
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" -- " + str(detail)) if detail else ""))
    if not ok:
        failures.append(name)


def build_fixture(tmpdir):
    jsonl_path = os.path.join(tmpdir, SESSION_ID + ".jsonl")
    receipts_dir = os.path.join(tmpdir, "precompact")
    os.makedirs(receipts_dir, exist_ok=True)

    t0 = datetime(2026, 9, 1, 12, 0, 0)

    def ts(offset_s):
        return (t0 + timedelta(seconds=offset_s)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    records = []
    # 1. real human turn, still in-window, quoted verbatim by the summary
    records.append({
        "type": "user", "sessionId": SESSION_ID, "session_id": SESSION_ID,
        "timestamp": ts(10), "origin": {"kind": "human"},
        "message": {"role": "user", "content": VERBATIM_TEXT},
    })
    # matching assistant turn so mint_window's bar (assistant_text_blocks>0) is real
    records.append({
        "type": "assistant", "sessionId": SESSION_ID, "session_id": SESSION_ID,
        "timestamp": ts(11),
        "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Understood, fixing the stopping-rule defect now."},
            {"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {"command": "echo hi"}},
        ]},
    })
    # 2. real human turn Jon typed, present in-window but WORDED differently
    #    than the summary's paraphrase of it
    records.append({
        "type": "user", "sessionId": SESSION_ID, "session_id": SESSION_ID,
        "timestamp": ts(20), "origin": {"kind": "human"},
        "message": {"role": "user", "content": PARAPHRASE_SOURCE},
    })
    # 3. queued_command attachment — the ONLY place QUEUED_ONLY_TEXT exists;
    #    it never becomes a normal `user` turn inside this window
    records.append({
        "type": "attachment", "sessionId": SESSION_ID, "session_id": SESSION_ID,
        "timestamp": ts(25), "isSidechain": False,
        "attachment": {
            "type": "queued_command", "prompt": QUEUED_ONLY_TEXT,
            "source_uuid": "src-1", "commandMode": "prompt",
            "origin": {"kind": "human"}, "timestamp": ts(25),
        },
    })

    # 4. the compact summary itself — paraphrases everything, quoting case 1
    #    verbatim, case 2 near, case 3 (queued-only) verbatim-quoted too
    summary_text = (
        "This session is being continued from a previous conversation that ran out "
        "of context. The summary below covers the earlier portion of the conversation.\n\n"
        "Summary:\n"
        "1. Primary Request and Intent:\n"
        '   - Jon said: "%s"\n'
        '   - He also noted that "%s"\n'
        '   - Separately, verbatim: "%s"\n'
    ) % (VERBATIM_TEXT, PARAPHRASE_IN_SUMMARY, QUEUED_ONLY_TEXT)
    summary_ts = ts(30)
    records.append({
        "type": "user", "sessionId": SESSION_ID, "session_id": SESSION_ID,
        "timestamp": summary_ts, "isCompactSummary": True,
        "isVisibleInTranscriptOnly": True,
        "message": {"role": "user", "content": summary_text},
    })

    with open(jsonl_path, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            # minified, no spaces after ':'/',' -- matches the real harness's
            # own JSONL wire format, which last_ts_at_or_before() (and the
            # committed auto_mint_windows.py it mirrors) scans for literally
            f.write(json.dumps(r, separators=(",", ":")) + "\n")

    # PreCompact receipt bounding the window: fires BEFORE the compact
    # writes its summary (real ordering — see auto_mint_windows.py), so its
    # wall time sits just before summary_ts, excluding the summary record
    # itself from the window it bounds. Named <utc>-<session6>.md per the
    # real convention.
    receipt_dt = t0 + timedelta(seconds=29)
    receipt_name = "%sT%s-%s.md" % (
        receipt_dt.strftime("%Y%m%d"), receipt_dt.strftime("%H%M%S"), SESS6)
    receipt_path = os.path.join(receipts_dir, receipt_name)
    with open(receipt_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# PreCompact receipt — %s-0000\n\nfixture receipt.\n" %
                 receipt_dt.strftime("%Y-%m-%dT%H:%M:%S"))

    return jsonl_path, receipts_dir, summary_ts


def main():
    tmpdir = tempfile.mkdtemp(prefix="ecs_selftest_")
    jsonl_path, receipts_dir, summary_ts = build_fixture(tmpdir)

    summaries = ecs.find_compact_summaries(jsonl_path, all_summaries=False)
    check("summary-found", len(summaries) == 1, "found %d" % len(summaries))
    if not summaries:
        print("SELFTEST FAIL: no summary found, cannot continue")
        return 1
    summary = summaries[0]
    check("isCompactSummary-flag-detected", summary["flagged_isCompactSummary"] is True)

    quotes = ecs.extract_quotes(summary["text"])
    check("three-quotes-extracted", len(quotes) == 3, quotes)

    diff = ecs.diff_one_summary(jsonl_path, SESSION_ID, summary, receipts_dir)
    check("window-synthesized-in-memory", diff["window_source"] == "synthesized-in-memory",
          diff["window_source"])
    check("window-not-written-to-disk", diff["window_path"] is None)

    verdicts = {r["quote"]: r["verdict"] for r in diff["rows"]}
    check("case-1-FOUND-VERBATIM", verdicts.get(VERBATIM_TEXT) == "FOUND-VERBATIM",
          verdicts.get(VERBATIM_TEXT))
    check("case-2-FOUND-NEAR", verdicts.get(PARAPHRASE_IN_SUMMARY) == "FOUND-NEAR",
          verdicts.get(PARAPHRASE_IN_SUMMARY))
    check("case-3-FOUND-IN-QUEUED-ONLY", verdicts.get(QUEUED_ONLY_TEXT) == "FOUND-IN-QUEUED-ONLY",
          verdicts.get(QUEUED_ONLY_TEXT))

    # --- the load-bearing branch check ---
    # Same quote, same window, but with the queued_command lookup DISABLED.
    # This must NOT reproduce FOUND-IN-QUEUED-ONLY -- if it does, the branch
    # is not doing anything and case-3 above would be passing by accident.
    window = ecs.find_committed_window(SESSION_ID, summary_ts) or \
        ecs.synthesize_window(jsonl_path, SESSION_ID, summary_ts, receipts_dir,
                               summary_line=summary["line"])
    core_body = ecs.core_window_body(window["body"])
    queued = ecs.find_queued_commands(jsonl_path)
    check("queued-command-entry-present-in-fixture", len(queued) == 1, len(queued))
    check("queued-text-absent-from-core-window-body",
          ecs._norm(QUEUED_ONLY_TEXT) not in ecs._norm(core_body))
    v_enabled = ecs.verdict_for_quote(QUEUED_ONLY_TEXT, core_body, queued, check_queued=True)
    v_disabled = ecs.verdict_for_quote(QUEUED_ONLY_TEXT, core_body, queued, check_queued=False)
    check("queued-lookup-enabled-matches-case-3", v_enabled["verdict"] == "FOUND-IN-QUEUED-ONLY",
          v_enabled["verdict"])
    check("queued-lookup-disabled-changes-verdict", v_disabled["verdict"] != "FOUND-IN-QUEUED-ONLY",
          v_disabled["verdict"])
    check("queued-lookup-disabled-is-NOT-IN-WINDOW", v_disabled["verdict"] == "NOT-IN-WINDOW",
          v_disabled["verdict"])

    # --- artifact write + frontmatter contract ---
    out_dir = os.path.join(tmpdir, "artifacts")
    path, sha, nbytes = ecs.write_artifact(out_dir, SESSION_ID, summary, diff)
    check("artifact-written", os.path.isfile(path))
    with open(path, encoding="utf-8") as f:
        doc = f.read()
    check("frontmatter-has-status-never-a-ruling",
          'status: "MACHINE PARAPHRASE, never a ruling; grade against the window"' in doc)
    check("frontmatter-has-sha256", ("sha256: %s" % sha) in doc)
    check("body-has-compact-summary-heading", "## [COMPACT-SUMMARY:" in doc)
    check("body-has-diff-section", "## DIFF" in doc)
    check("body-quotes-verbatim-text-present", VERBATIM_TEXT in doc)

    # --- self-leak safety cap: no receipt on record for this session at all
    # (true for a still-open live session) must NOT fall back to the
    # summary's own timestamp as the window's hi bound, or the summary
    # leaks into the window it is graded against and everything trivially
    # matches itself. Measured real-world case: session e515d858, 2026-09-02.
    empty_receipts_dir = os.path.join(tmpdir, "no_receipts")
    os.makedirs(empty_receipts_dir, exist_ok=True)
    leak_window = ecs.synthesize_window(jsonl_path, SESSION_ID, summary_ts,
                                         empty_receipts_dir, summary_line=summary["line"])
    check("no-receipt-fallback-excludes-summary-preamble",
          ecs.SUMMARY_PREFIX not in leak_window["body"], leak_window["body"][:120])
    check("no-receipt-fallback-position-truncated",
          "position-truncated" in leak_window["bound_note"], leak_window["bound_note"])
    leak_diff_quotes = ecs.extract_quotes(summary["text"])
    leak_core = ecs.core_window_body(leak_window["body"])
    leak_verdict_case3 = ecs.verdict_for_quote(
        QUEUED_ONLY_TEXT, leak_core, ecs.find_queued_commands(jsonl_path), check_queued=True)
    check("no-receipt-fallback-case-3-still-FOUND-IN-QUEUED-ONLY",
          leak_verdict_case3["verdict"] == "FOUND-IN-QUEUED-ONLY", leak_verdict_case3["verdict"])

    # --- suspicious-zero-diff construction check ---
    # A synthetic summary with a real user turn in-window but zero quotes.
    no_quote_summary = dict(summary)
    no_quote_summary["text"] = (SUMMARY_PREFIX_FOR_TEST())
    diff2 = ecs.diff_one_summary(jsonl_path, SESSION_ID, no_quote_summary, receipts_dir)
    check("suspicious-zero-diff-flagged", diff2["suspicious_zero_diff"] is True, diff2)

    if failures:
        print("\nSELFTEST FAIL: %d assertion(s) failed: %s" % (len(failures), failures))
        return 1
    print("\nSELFTEST PASS: all %d assertions passed." % n_checks[0])
    return 0


def SUMMARY_PREFIX_FOR_TEST():
    return ecs.SUMMARY_PREFIX + " that ran out of context. Summary:\n1. No quotes here at all, just prose."


if __name__ == "__main__":
    sys.exit(main())
