#!/usr/bin/env bash
# sendmessage-record.sh — P4-6: `SendMessage` leaves no artifact; this hook writes one, in the sender's hand.
#
# Fired by PostToolUse (matcher "SendMessage", see .claude/settings.json). Contract, from Jon 2026-09-04:
# "I've wanted raw md files hook-updated by default on any exchange, and sendmessage is an exchange."
# Transport stays SendMessage; the RECORD is written here by the SENDER after the send — never the
# receiver copying its own mail. Three copies, each with a reader:
#   1. raw/exchange-messages/<file>           the raw record (gitignored raw/, on Drive)
#   2. exchange/outbox/<file>                 graded by C9 -- named pro-to-<peer>-msg-... so C9's addressee parser grades ONE tree
#   3. <peer trunk>/exchange/inbound/<file>   the courier-file rule (Secretary §24), by plain cp into an
#                                             inbox that MUST already exist. No mkdir. Unknown peer = LOUD FAIL.
#
# Hook stdin (Claude Code PostToolUse): JSON with tool_name, tool_input{to,message,summary}, session_id.
#   --selftest   three controls: planted send -> 3 files; unknown peer -> exit 1, nothing created;
#                a non-SendMessage tool -> no-op exit 0. Exit 0 PASS / 3 FAIL.
export PYTHONIOENCODING=utf-8
set -u
cd "$(dirname "$0")/.." || exit 2
REPO="$(pwd)"
TRUNK_ROOT="${LINT_TRUNK_ROOT:-G:/My Drive/Claude}"
# R4b (2026-09-05): a peer's LIVE home may be on N: (CFL now; Secretary and Professional after the restart). The roster
# scripts/trunk-live-roots.tsv is the ONE place that says where each peer lives; when it names a peer, that absolute
# path wins over TRUNK_ROOT/<dir>. Personal stays on G: until its R4/R5 pass.
LIVE_ROOTS="$(dirname "${BASH_SOURCE[0]}")/trunk-live-roots.tsv"
live_root() { [ -z "${LINT_TRUNK_ROOT:-}" ] || return 1; [ -f "$LIVE_ROOTS" ] && awk -F"\t" -v p="$1" '$1==p && $2!="" {print $2; exit}' "$LIVE_ROOTS"; }
RAW_DIR="${SMR_RAW_DIR:-raw/exchange-messages}"
OUT_DIR="${SMR_OUT_DIR:-exchange/outbox}"

# peer name (as ListAgents prints it) -> trunk directory under TRUNK_ROOT. Personal hosts herald and soul.
peer_dir() {
  case "$1" in
    cfl)               echo "Claude Foundational Layer/claude-foundational-layer" ;;
    secretary)         echo "Claude Secretary" ;;
    herald|soul|personal) echo "Claude Personal" ;;
    *)                 return 1 ;;
  esac
}

record() {  # reads hook JSON on stdin
  local json; json="$(cat)"
  local tool; tool="$(printf '%s' "$json" | python -c 'import sys,json;print(json.load(sys.stdin).get("tool_name",""))' 2>/dev/null)"
  [ "$tool" = "SendMessage" ] || exit 0          # not ours; a no-op is correct here, not a failure
  local to msg summ sid
  to="$(printf '%s' "$json"   | python -c 'import sys,json;print(json.load(sys.stdin).get("tool_input",{}).get("to",""))')"
  summ="$(printf '%s' "$json" | python -c 'import sys,json;print(json.load(sys.stdin).get("tool_input",{}).get("summary",""))')"
  sid="$(printf '%s' "$json"  | python -c 'import sys,json;print(json.load(sys.stdin).get("session_id","")[:8])')"
  msg="$(printf '%s' "$json"  | python -c 'import sys,json;print(json.load(sys.stdin).get("tool_input",{}).get("message",""))')"
  # 2026-09-11 20:5x: ListAgents names carry a session suffix ("secretary N3c0", "herald N3 c0",
  # "professional trunk backup"); the roster is keyed by the bare first token. Before this line took
  # the first token, every send of 2026-09-11 (51 by one seat) failed here as an unknown peer and
  # WC-1 wrote nothing. Strip the [ref], then everything after the first space, then lowercase.
  local peer; peer="$(printf '%s' "$to" | sed -E 's/ *\[.*$//' | sed -E 's/ .*$//' | tr 'A-Z' 'a-z')"
  local dir; dir="$(peer_dir "$peer")" || { echo "SENDMESSAGE-RECORD: FAIL unknown peer '$peer' -- no roster row, nothing written, nothing created" >&2; exit 1; }
  local lr; lr="$(live_root "$peer")"
  local inbox; if [ -n "$lr" ]; then inbox="$lr/exchange/inbound"; else inbox="$TRUNK_ROOT/$dir/exchange/inbound"; fi
  [ -d "$inbox" ] || { echo "SENDMESSAGE-RECORD: FAIL inbox absent: $inbox -- a write that creates its own destination looks like delivery" >&2; exit 1; }
  local ts slug fn; ts="$(date '+%Y-%m-%dT%H%M%S')"
  slug="$(printf '%s' "$summ" | tr -cs 'A-Za-z0-9' '-' | sed -E 's/^-+|-+$//g' | cut -c1-60)"
  fn="pro-to-${peer}-msg-${ts}-${slug:-untitled}.md"   # pro-to-<peer>- first: C9 parses the addressee from that prefix and grades ONE tree
  mkdir -p "$RAW_DIR"                                     # OUR raw dir, not a destination
  {
    printf -- '---\nkind: sendmessage-record\nfrom: professional (session %s)\nto: %s\nsent: %s\nsummary: "%s"\ntransport: SendMessage\nrecord: written by the SENDER after the send, PostToolUse hook scripts/sendmessage-record.sh\n---\n\n' "$sid" "$peer" "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$summ"
    printf '%s\n' "$msg"
  } > "$RAW_DIR/$fn"
  cp -f "$RAW_DIR/$fn" "$OUT_DIR/$fn"     || { echo "SENDMESSAGE-RECORD: FAIL outbox copy" >&2; exit 1; }
  cp -f "$RAW_DIR/$fn" "$inbox/$fn"       || { echo "SENDMESSAGE-RECORD: FAIL inbox copy: $inbox" >&2; exit 1; }
  echo "SENDMESSAGE-RECORD: $fn -> raw + outbox + $inbox ($(wc -c < "$RAW_DIR/$fn") B)"
}

selftest() {
  local fx; fx="$(mktemp -d)"; local fails=0
  mkdir -p "$fx/root/Claude Secretary/exchange/inbound" "$fx/raw" "$fx/out"
  local pos='{"session_id":"deadbeef-0000","tool_name":"SendMessage","tool_input":{"to":"secretary","summary":"planted test send","message":"planted body line 1\nline 2"}}'
  local neg='{"session_id":"deadbeef-0000","tool_name":"SendMessage","tool_input":{"to":"nobody","summary":"x","message":"y"}}'
  local nop='{"session_id":"deadbeef-0000","tool_name":"Read","tool_input":{"file_path":"z"}}'
  # positive: three files
  out="$(printf '%s' "$pos" | LINT_TRUNK_ROOT="$fx/root" SMR_RAW_DIR="$fx/raw" SMR_OUT_DIR="$fx/out" bash "$0")"; rc=$?
  n=$(find "$fx/raw" "$fx/out" "$fx/root" -name 'pro-to-secretary-msg-*.md' | wc -l)
  echo "  positive control      : exit=$rc files=$n (expect 0, 3)"; { [ "$rc" -eq 0 ] && [ "$n" -eq 3 ]; } || fails=$((fails+1))
  grep -q "planted body line 1" "$fx/out"/pro-to-secretary-msg-*.md 2>/dev/null || { echo "  body missing from record"; fails=$((fails+1)); }
  # negative: unknown peer -> exit 1, nothing created anywhere
  printf '%s' "$neg" | LINT_TRUNK_ROOT="$fx/root" SMR_RAW_DIR="$fx/raw" SMR_OUT_DIR="$fx/out" bash "$0" 2>/dev/null; rc=$?
  n2=$(find "$fx" -name 'pro-to-nobody-msg-*.md' | wc -l); d=$(find "$fx/root" -type d -name inbound | wc -l)
  echo "  negative unknown peer : exit=$rc files=$n2 inbox-dirs=$d (expect 1, 0, 1 -- no mkdir)"; { [ "$rc" -eq 1 ] && [ "$n2" -eq 0 ] && [ "$d" -eq 1 ]; } || fails=$((fails+1))
  # no-op: other tool
  printf '%s' "$nop" | LINT_TRUNK_ROOT="$fx/root" SMR_RAW_DIR="$fx/raw" SMR_OUT_DIR="$fx/out" bash "$0"; rc=$?
  echo "  no-op other tool      : exit=$rc (expect 0)"; [ "$rc" -eq 0 ] || fails=$((fails+1))
  rm -rf "$fx"
  if [ "$fails" -eq 0 ]; then echo "SELFTEST PASS"; exit 0; else echo "SELFTEST FAIL ($fails)"; exit 3; fi
}

case "${1:-}" in --selftest) selftest ;; *) record ;; esac
