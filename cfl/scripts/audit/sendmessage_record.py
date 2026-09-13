#!/usr/bin/env python3
"""sendmessage_record.py — TAG-1. Write CFL's own SendMessage sends to disk, so its half of the
peer reasoning is traceable.

WHY, measured 2026-09-04 21:1x on Jon's question "how we should be able to better trace through
messages in the exchange or claude tag ... Thats what the @s are doing right?":

  peer-message records in CFL's graphrag index: 10
  ...of those, `pro-to-cfl-msg-*`:             10
  ...of those, written by CFL:                  0

⛔ Professional runs a PostToolUse hook that writes THEIR sends to disk, so their side of an
exchange is a file, gets couriered, gets indexed, and is retrievable. CFL had no such hook. So
every argument CFL made to a peer tonight -- the Stage 2 stdin correction, the G8 confirmation,
the unhooked-compact control -- existed only inside a transcript nobody queries. ⭐ HALF OF EVERY
CONVERSATION WAS IN THE GRAPH AND IT WAS NEVER CFL'S HALF.

That is the "delivered is not received" defect inverted: not mail that went unread, but mail that
was never written down by the sender. A reply is evidence of a question; a question with no record
makes the reply unreadable later.

WHAT THIS DOES
--------------
PostToolUse(SendMessage) hook. Reads the tool payload on stdin, writes ONE markdown file:

    exchange/outbox/cfl-to-<peer>-msg-<YYYY-MM-DDTHHMMSS>-<slug>.md

with frontmatter matching the shape Professional already emits (kind: sendmessage-record), so both
trunks' records parse the same way and neither has to special-case the other.

FENCES, each answering a failure already on record here:
  * NEVER BLOCKS. Always exits 0 -- a recording hook that can fail a tool call is worse than the
    gap it fills.
  * Writes under exchange/outbox/, which the index queue's enqueue hook already covers, so the
    record becomes retrievable by the same path as everything else. It does NOT write under
    exchange/su-close/ (the enqueue hook excludes that, and a record nobody can retrieve is the
    defect this closes).
  * An unparseable or empty payload writes NOTHING and says so on stderr. A file recording
    "unknown -> unknown" is worse than an absent one: it looks like evidence.

  sendmessage_record.py [--self-test]
"""
import io
import json
import os
import re
import sys
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(_HERE))
OUTBOX = os.path.join(ROOT, "exchange", "outbox")

MAX_SLUG = 60


def slugify(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", (s or "").strip()).strip("-")
    return (s[:MAX_SLUG].rstrip("-") or "no-summary")


def build(payload, now=None):
    """(filename, text) or (None, reason). A payload we cannot read writes NOTHING."""
    ti = payload.get("tool_input") or {}
    to = (ti.get("to") or "").strip()
    msg = ti.get("message") or ""
    summary = (ti.get("summary") or "").strip()
    if not to or not msg.strip():
        return None, ("payload has no `to` or no `message` -- recording NOTHING rather than a "
                      "placeholder, because a file saying unknown->unknown looks like evidence")
    now = now or datetime.now()
    stamp = now.strftime("%Y-%m-%dT%H%M%S")
    peer = slugify(to)[:24]
    name = "cfl-to-%s-msg-%s-%s.md" % (peer, stamp, slugify(summary))
    sess = (payload.get("session_id") or "unknown")[:8]
    # reader_token_cost is required by exchange_write_check.py -- declared, not estimated
    nbytes = len(msg.encode("utf-8"))
    text = (
        "---\n"
        "kind: sendmessage-record\n"
        "from: cfl (session %s)\n"
        "to: %s\n"
        "sent: %s\n"
        "summary: %s\n"
        "transport: SendMessage\n"
        "record: written by the SENDER after the send, PostToolUse hook "
        "scripts/audit/sendmessage_record.py (TAG-1, 2026-09-04)\n"
        "reader_token_cost: \"~%d tokens (%d bytes / 4, measured post-write)\"\n"
        "on_silence: \"nothing acts; this is a RECORD of a message already delivered live, not a request\"\n"
        "---\n\n"
        "%s\n"
    ) % (sess, to, now.strftime("%Y-%m-%d %H:%M:%S %Z") or now.strftime("%Y-%m-%d %H:%M:%S"),
         json.dumps(summary or "(none)"), nbytes // 4, nbytes, msg.rstrip())
    return name, text


def main():
    if "--self-test" in sys.argv:
        return self_test()
    raw = ""
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
    except Exception:
        pass
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}
    name, text = build(payload)
    if not name:
        # NEVER a silent success and NEVER a placeholder file
        print("sendmessage_record: %s" % text, file=sys.stderr)
        return 0
    try:
        os.makedirs(OUTBOX, exist_ok=True)
        with io.open(os.path.join(OUTBOX, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except OSError as e:
        print("sendmessage_record: could not write (%s)" % e.__class__.__name__, file=sys.stderr)
    return 0


def self_test():
    import tempfile
    global OUTBOX
    print("=== SELF-TEST -- sendmessage_record ===")
    np = nf = 0

    def ok(n, got, want):
        nonlocal np, nf
        if got == want:
            np += 1; print("  PASS  %s" % n)
        else:
            nf += 1; print("  FAIL  %s\n        want: %r\n        got : %r" % (n, want, got))

    good = {"session_id": "71ce5a0e-d253", "tool_input": {
        "to": "soul", "summary": "G8 confirmed and fixed",
        "message": "Body line one.\nBody line two."}}
    name, text = build(good, datetime(2026, 9, 4, 21, 30, 0))
    ok("1 filename names the peer and the time", name.startswith("cfl-to-soul-msg-2026-09-04T213000-"), True)
    ok("2 body is carried verbatim", "Body line one.\nBody line two." in text, True)
    ok("3 frontmatter declares the sender", "from: cfl (session 71ce5a0e)" in text, True)
    ok("4 reader_token_cost is declared (exchange_write_check requires it)",
       "reader_token_cost:" in text, True)

    # NEGATIVE CONTROLS -- a payload we cannot read must write NOTHING, not a placeholder
    ok("5 no `to` -> writes nothing", build({"tool_input": {"message": "x"}})[0], None)
    ok("6 empty message -> writes nothing", build({"tool_input": {"to": "soul", "message": "  "}})[0], None)
    ok("7 empty payload -> writes nothing", build({})[0], None)

    # a summary with path/shell characters must not escape the filename
    n2, _ = build({"tool_input": {"to": "a/../b", "summary": "x/y `z`", "message": "m"}},
                  datetime(2026, 9, 4, 21, 30, 0))
    ok("8 slug is filename-safe", bool(re.fullmatch(r"[A-Za-z0-9.\-]+\.md", n2)), True)

    # ⛔ argv MUST be cleared before calling main(): main() re-reads sys.argv, sees --self-test
    # still there, and re-enters self_test() forever. Measured on this script's first run --
    # 303 KB of repeated PASS lines. A harness that invokes its own entry point must strip the
    # flag that selected the harness, or the test becomes its own input.
    d = tempfile.mkdtemp(); OUTBOX = d
    saved_argv, saved_stdin = sys.argv, sys.stdin
    try:
        sys.argv = [saved_argv[0]]
        sys.stdin = io.StringIO(json.dumps(good))
        main()
    finally:
        sys.argv, sys.stdin = saved_argv, saved_stdin
    ok("9 end-to-end writes exactly one file", len(os.listdir(d)), 1)
    # 10 NEGATIVE CONTROL for 9: an unreadable payload writes NO file through the same path
    d2 = tempfile.mkdtemp(); OUTBOX = d2
    try:
        sys.argv = [saved_argv[0]]
        sys.stdin = io.StringIO("{}")
        main()
    finally:
        sys.argv, sys.stdin = saved_argv, saved_stdin
    ok("10 control: empty payload writes NO file", len(os.listdir(d2)), 0)
    print("  %d passed, %d failed" % (np, nf))
    return 0 if nf == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
