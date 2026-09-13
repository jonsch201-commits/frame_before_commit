#!/usr/bin/env bash
# precompact-capture.sh — T-1 (Jon's compact command), Professional's adoption.
#
# Fired by the PreCompact hook (see .claude/settings.json). Contract: a PLAIN /compact — no
# ritual, no Jon friction — durably lands (1) the raw transcript, (2) the tree's dirty durable
# state, (3) a RECEIPT the post-compact session can find from disk alone. "Can not accept the
# friction, will not accept the lost."
#
# Hook stdin (Claude Code PreCompact): JSON with session_id and transcript_path. We read both,
# fall back to env, and fail LOUD (nonzero + receipt line) rather than silently — a hook that
# doesn't fire and a hook that fires into a void are the same defect (silent inheritance).
#
#   --selftest   prove the capture failable + runnable against a synthetic session; exit 0/3.
set -u
cd "$(dirname "$0")/.." || exit 2

REPO="$(pwd)"
ARCHIVE_ROOT="raw/session-archive"          # gitignored, on-Drive: durable, never in git history (PII posture)
RECEIPT="exchange/last-precompact-receipt.md"

capture() {
  local sid="$1" tpath="$2" now bytes=0 files=0 status="OK"
  now="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  mkdir -p "$ARCHIVE_ROOT/$sid"

  if [ -f "$tpath" ]; then
    cp -f "$tpath" "$ARCHIVE_ROOT/$sid/" || status="COPY-FAIL"
    local sdir="${tpath%.jsonl}/subagents"
    [ -d "$sdir" ] && cp -rf "$sdir" "$ARCHIVE_ROOT/$sid/" 2>/dev/null
    bytes=$(du -sb "$ARCHIVE_ROOT/$sid" | cut -f1)
    files=$(find "$ARCHIVE_ROOT/$sid" -type f | wc -l)
  else
    status="NO-TRANSCRIPT-AT-PATH"
  fi

  # BP-6 (2026-09-06 15:1x): the session IDENTITY page at the barrier, from measured fields, no defaulted value.
  # Antigravity proposed this block (REVIEW-RESPONSE 09-05 23:25, its script sha 9752324e); Professional reviewed
  # and applied it with this trunk's own validated script (scripts/session_identity.py, selftest PASS, jon_turns by
  # origin.kind) and TWO changes: stderr goes to a log, never /dev/null (oath M-4: a swallowed error is a false green),
  # and the page lands under wiki/sources/sessions/ directly (this trunk's own tree; posture (a) applies to a DAEMON
  # writing into a sibling, not to a seat's own hook). Non-zero exit is recorded in the receipt and never blocks the compact.
  if [ -f "$tpath" ] && [ -f scripts/session_identity.py ]; then
    python scripts/session_identity.py --jsonl "$tpath" --trunk-root "$REPO" \
      --outdir "$REPO/wiki/sources/sessions" \
      2>>"$REPO/exchange/precompact-identity.err.log" || status="$status+IDENTITY-FAIL"
  fi

  # Durable-state commit: exact durable paths only, never -A. Empty commit is fine to skip.
  git add WAKE.md wiki/ exchange/inbound/ 2>/dev/null
  if ! git diff --cached --quiet 2>/dev/null; then
    git commit -q -m "precompact-capture: auto-land durable state (session $sid, $now)" || status="$status+COMMIT-FAIL"
  fi

  {
    echo "# PRECOMPACT RECEIPT — read me first after any compact"
    echo "captured: $now [measured — written by the hook at fire time]"
    echo "session: $sid"
    echo "transcript: $tpath -> $ARCHIVE_ROOT/$sid/ ($files files, $bytes B)"
    echo "tree: HEAD $(git rev-parse --short HEAD 2>/dev/null || echo '?') AT CAPTURE TIME · status: $status"
    echo "# A LATER head is NORMAL -- the seat kept working after this receipt was written. An EARLIER"
    echo "# head, or a head not containing this one, is the defect. Check it with a command, never by"
    echo "# string equality:  git merge-base --is-ancestor <receipt head> HEAD  (exit 0 = fine)."
    echo "# Raised by Secretary as outside reader 2026-09-07 22:3x: the receipt said 5713e5f, HEAD was"
    echo "# 50599bf ten minutes later, and the exam line below told the next seat those must AGREE."
    echo "post-compact exam: WAKE.md resume point + wiki/log.md newest entry + this receipt must agree"
    echo "  on SESSION, CAPTURED TIME and ARCHIVE COUNTS. HEAD is an ancestry check, not an equality check."
  } > "$RECEIPT"
  # The pointer file is last-writer-wins (measured 2026-08-15 20:30 — a manual capture clobbered
  # a live session's receipt). The ledger below is append-only; history survives the pointer.
  printf '%s | %s | %s files %s B | HEAD %s | %s\n' "$now" "$sid" "$files" "$bytes" \
    "$(git rev-parse --short HEAD 2>/dev/null || echo '?')" "$status" >> exchange/precompact-receipts.log

  [ "$status" = "OK" ]
}

if [ "${1:-}" = "--selftest" ]; then
  # Preserve the PRODUCTION receipt/ledger — a selftest that destroys live artifacts is a defect
  # (measured 2026-08-15 20:4x: this selftest deleted the live receipt; the ledger saved history).
  SAVED_RECEIPT=""; [ -f "$RECEIPT" ] && SAVED_RECEIPT=$(cat "$RECEIPT")
  trap '[ -n "$SAVED_RECEIPT" ] && printf "%s" "$SAVED_RECEIPT" > "$RECEIPT"' EXIT
  tmp=$(mktemp -d); rc=0
  printf '{"fake":"session"}\n' > "$tmp/zz-selftest.jsonl"
  capture "zz-selftest" "$tmp/zz-selftest.jsonl" >/dev/null 2>&1 || { echo "SELFTEST BROKEN: happy path failed"; rc=3; }
  grep -q "session: zz-selftest" "$RECEIPT" || { echo "SELFTEST BROKEN: receipt missing"; rc=3; }
  capture "zz-selftest-miss" "$tmp/does-not-exist.jsonl" >/dev/null 2>&1 && { echo "SELFTEST BROKEN: missing transcript did not fail"; rc=3; }
  grep -q "NO-TRANSCRIPT-AT-PATH" "$RECEIPT" || { echo "SELFTEST BROKEN: failure not named in receipt"; rc=3; }
  rm -rf "$tmp" "$ARCHIVE_ROOT/zz-selftest" "$ARCHIVE_ROOT/zz-selftest-miss"; rm -f "$RECEIPT"
  [ $rc -eq 0 ] && echo "SELFTEST: capture proven runnable AND failable-with-named-failure (receipt both ways)"
  exit $rc
fi

# Real invocation: parse hook JSON from stdin (python for robustness), env fallback.
IN="$(cat 2>/dev/null || true)"
SID=$(printf '%s' "$IN" | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('session_id',''))" 2>/dev/null || true)
TPATH=$(printf '%s' "$IN" | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('transcript_path',''))" 2>/dev/null || true)
[ -z "$SID" ] && SID="${CLAUDE_SESSION_ID:-unknown-$(date +%s)}"
capture "$SID" "$TPATH"
