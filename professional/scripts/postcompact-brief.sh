#!/usr/bin/env bash
# postcompact-brief.sh — the WIKI half of Jon's compact command (T-1 extension).
#
# PreCompact capture (precompact-capture.sh) saves the LOST half. This closes the FRICTION half:
# fired by SessionStart with matcher "compact", its stdout is injected into the fresh post-compact
# context — so the very first thing a compacted session sees is its own close duty, with the
# mechanical state already measured. Plain /compact → wiki fully updated, nothing typed by Jon.
#
#   --selftest   prove the duty block, both receipt states, the identity verdict and the
#                fire-log append; exit 0/3.
set -u
cd "$(dirname "$0")/.." || exit 2

RECEIPT="exchange/last-precompact-receipt.md"
FIRELOG="${POSTCOMPACT_FIRELOG:-exchange/postcompact-brief.log}"

# Read the SessionStart hook's JSON payload from stdin WITHOUT ever blocking a session start.
# Added 2026-08-17: this hook had no fire log at all, so nobody could tell whether the duty was
# ever delivered — its own lesson ("trust the fire log, not the install") did not apply to it.
# The session id is also what makes Soul's 08-17 correction real: a freshness check against wall
# clock fails open whenever Jon compacts and walks away; identity does not.
hook_session_id() {
  local raw=""
  if [ "${POSTCOMPACT_FAKE_STDIN:-}" != "" ]; then raw="$POSTCOMPACT_FAKE_STDIN"
  else IFS= read -r -t 1 -d "" raw 2>/dev/null || true; fi
  printf '%s' "${raw:-}" | tr ',{}' '


' | grep -oE '"session_id"[[:space:]]*:[[:space:]]*"[^"]+"'     | head -1 | sed 's/.*: *"//; s/"$//'
}

receipt_session_id() {
  [ -f "$RECEIPT" ] || return 0
  grep -m1 -oE '^session: [^ ]+' "$RECEIPT" | awk '{print $2}'
}

# MATCH / MISMATCH / NO-RECEIPT / SESSION-UNKNOWN — the verdict is about IDENTITY, not staleness.
verdict() {
  local cur="$1" rcp="$2"
  if [ ! -f "$RECEIPT" ]; then echo "NO-RECEIPT"; return; fi
  if [ -z "$cur" ]; then echo "SESSION-UNKNOWN"; return; fi
  if [ "$cur" = "$rcp" ]; then echo "MATCH"; else echo "MISMATCH"; fi
}

emit() {
  local CUR RCP V
  CUR="${CUR_SESSION:-}"; RCP="${RCP_SESSION:-}"; V="${VERDICT:-SESSION-UNKNOWN}"
  echo "<postcompact-duty source=\"SessionStart(compact) hook — Jon's compact command: 'ensure wiki is fully updated every time'\">"
  echo "A compact just fired in this session. BEFORE resuming any other work, perform the"
  echo "su-compact durable record from what you retain plus the receipt below:"
  echo "  1. Append the session close entry to wiki/log.md (errors included, on purpose)."
  echo "  2. Refresh WAKE.md (AS OF, gates, DO NOT REDO, resume point; <= 6,144 B)."
  echo "  3. Update wiki/tracker/tracker.md top block; close closed rows."
  echo "  4. bash scripts/lint.sh — then commit the exact touched paths. NO push (Jon gate)."
  echo "If your retained context is too thin to write the close honestly, say so IN the log entry"
  echo "and reconstruct from raw/session-archive/<session>/ — never fabricate a close."
  echo ""
  if [ "$V" = "MISMATCH" ]; then
    echo "⛔ RECEIPT IDENTITY MISMATCH — the receipt below belongs to session $RCP, this session is"
    echo "$CUR. THIS compact's capture did not write a receipt: treat the receipt as another"
    echo "session's and record the miss as a T-1 finding. (Identity check, not staleness: a"
    echo "wall-clock freshness test fails open whenever Jon compacts and walks away — Soul, 08-17.)"
    echo ""
  fi
  if [ -f "$RECEIPT" ]; then
    echo "--- your ANCESTOR (scripts/ancestor.py: newest MAIN session other than you, forks excluded, every project key scanned) ---"
    echo "Jon 2026-09-04 22:3x: grep a JSONL as a LAST resort; resume an elder, or improve the wiki / graph RAG, by default."
    python "$(dirname "$0")/ancestor.py" --self "${CUR:-}" 2>&1 | head -4
    echo ""
    echo "--- capture receipt (written at PreCompact fire time) ---"
    cat "$RECEIPT"
  else
    echo "⚠ NO CAPTURE RECEIPT at $RECEIPT — the PreCompact hook did NOT fire or did not finish."
    echo "That is a T-1 failure: record it as a finding before anything else."
  fi
  echo "--- mechanical state, measured now ---"
  echo "HEAD: $(git rev-parse --short HEAD 2>/dev/null || echo '?') · dirty: $(git status --porcelain 2>/dev/null | wc -l) path(s) · clock: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "receipt identity: $V (this session ${CUR:-unknown} · receipt ${RCP:-none}) · fire log: $FIRELOG"
  echo "</postcompact-duty>"
}

if [ "${1:-}" = "--selftest" ]; then
  rc=0
  # State A: receipt present (capture full output first — grep -q on a live pipe SIGPIPEs emit)
  had=0; [ -f "$RECEIPT" ] && had=1
  [ $had -eq 0 ] && printf 'canary receipt\n' > "$RECEIPT"
  OUT=$(emit)
  echo "$OUT" | grep -q "capture receipt" || { echo "SELFTEST BROKEN: receipt state not emitted"; rc=3; }
  echo "$OUT" | grep -q "postcompact-duty" || { echo "SELFTEST BROKEN: duty block missing"; rc=3; }
  [ $had -eq 0 ] && rm -f "$RECEIPT"
  # State B: receipt absent (only test if we can safely simulate)
  if [ ! -f "$RECEIPT" ]; then
    OUT=$(emit)
  else
    mv "$RECEIPT" "$RECEIPT.bak"; OUT=$(emit); mv "$RECEIPT.bak" "$RECEIPT"
  fi
  echo "$OUT" | grep -q "NO CAPTURE RECEIPT" || { echo "SELFTEST BROKEN: missing-receipt not detected"; rc=3; }
  # State C: identity mismatch must be detected and must reach the duty block
  OUT=$(CUR_SESSION="zz-current" RCP_SESSION="zz-other" VERDICT="MISMATCH" emit)
  echo "$OUT" | grep -q "RECEIPT IDENTITY MISMATCH" || { echo "SELFTEST BROKEN: mismatch not surfaced"; rc=3; }
  OUT=$(CUR_SESSION="zz-same" RCP_SESSION="zz-same" VERDICT="MATCH" emit)
  echo "$OUT" | grep -q "RECEIPT IDENTITY MISMATCH" && { echo "SELFTEST BROKEN: mismatch warned on a MATCH"; rc=3; }
  # State D: the fire log must actually gain a row (this hook had no fire log before 2026-08-17)
  FL=$(mktemp)
  before=$(wc -l < "$FL")
  POSTCOMPACT_FIRELOG="$FL" POSTCOMPACT_FAKE_STDIN='{"session_id":"zz-selftest","source":"compact"}'     bash "$0" >/dev/null 2>&1
  after=$(wc -l < "$FL"); rm -f "$FL"
  [ "$after" -gt "$before" ] || { echo "SELFTEST BROKEN: fire log gained no row"; rc=3; }
  [ $rc -eq 0 ] && echo "SELFTEST: duty block + both receipt states + identity verdict + fire log proven (5/5)"
  exit $rc
fi

CUR_SESSION=$(hook_session_id)
RCP_SESSION=$(receipt_session_id)
VERDICT=$(verdict "$CUR_SESSION" "$RCP_SESSION")
export CUR_SESSION RCP_SESSION VERDICT
printf '%s | session %s | receipt %s | %s | HEAD %s
'   "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${CUR_SESSION:-unknown}" "${RCP_SESSION:-none}" "$VERDICT"   "$(git rev-parse --short HEAD 2>/dev/null || echo '?')" >> "$FIRELOG"

emit
