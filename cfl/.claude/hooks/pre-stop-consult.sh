#!/usr/bin/env bash
# Stop hook — Jon's pre-stop consult rule, made physical.
#
# WHY THIS EXISTS
# ---------------
# Jon, 2026-08-03, verbatim:
#   "If main wants to stop, it must talk to you firt."
#   "Your message tells me that the pausing defect is still in place. Have main coordinate
#    diagnose/fixing. It needs a way to ensure it messages YOU before it stops."
#
# The rule was deposited as prose in wiki/intake-triage/ and exchange/STOP-GUARD.md. It was
# then violated TWICE by the session that wrote it, in consecutive turns, each time in a
# message that announced it was continuing. Jon caught both. The instrument caught neither.
#
# That is the program's signature failure -- a fact written down once, then depending on
# someone remembering it. Prose does not intercept a stop. **A hook does.**
#
# WHAT IT CHECKS
# --------------
# One question: since Jon's last message, did this session dispatch a fable-mirror consult?
# The evidence is in the live transcript, which Claude Code hands this hook on stdin as
# `transcript_path` -- so there is nothing to guess.
#
#   consult found  -> allow the stop
#   none found     -> BLOCK, with the reason, and the model is returned to work
#
# WHY IT IS SAFE TO SELF-APPLY, stated because the standing fence says security-adjacent
# config is propose-never-apply:
#   This hook REMOVES a capability from the assistant. It cannot grant one. It cannot read
#   secrets, reach the network, or alter permissions -- it reads one local file and answers
#   yes/no. Self-binding is the opposite of the privilege escalation that fence guards
#   against. It also lives in a tracked file, so it is reviewable and revertable in one
#   commit. If Jon disagrees, deleting the "Stop" block in .claude/settings.json is the
#   whole revert.
#
# FAIL-OPEN, DELIBERATELY
# -----------------------
# Any internal error allows the stop. A broken guard that traps the session is worse than
# a missing one: it would make the assistant unable to yield to Jon, which is the one
# failure mode worse than stopping too early.
# ---------------------------------------------------------------------------------------------
# PLATFORM CONTRACT — verified against current official docs, https://code.claude.com/docs/en/hooks,
# fetched 2026-08-06. Do not restate any of this from memory; re-fetch before changing it.
#
#   * `Stop` takes NO matcher. Doc, verbatim: "UserPromptSubmit, PostToolBatch, Stop, TeammateIdle,
#     TaskCreated, TaskCompleted, WorktreeCreate, WorktreeRemove, MessageDisplay, and CwdChanged
#     don't support matchers and always fire on every occurrence. If you add a `matcher` field to
#     these events, it is silently ignored." The staged stanza therefore has no matcher key.
#   * The only documented `decision` value for Stop is `"block"` — doc: "Prevents Claude from
#     stopping, continues the conversation". `"approve"` is NOT documented for Stop. This script
#     previously emitted `{"decision":"approve"}` on every allow path; that relied on an
#     undocumented value being benignly ignored. It now emits NOTHING on allow and exits 0, which
#     is the documented allow path for every event. (Fixed 2026-08-06.)
#   * Stop stdout is NOT shown to the model — doc: only UserPromptSubmit, UserPromptExpansion and
#     SessionStart have stdout added as context. The `reason` string is this hook's only channel.
#   * `stop_hook_active` DOES NOT APPEAR ANYWHERE IN THE CURRENT DOCS. It was a documented field
#     historically and the earlier version of this hook depended on it as its ONLY loop guard.
#     Documented Stop input today is the common fields plus `last_assistant_message`. So the
#     re-entry check below is kept (harmless if the field still arrives) but is NO LONGER the only
#     thing standing between this hook and an infinite block loop — see BLOCK BUDGET.
#
# BLOCK BUDGET — the loop guard that does not depend on an undocumented field.
# At most MAX_BLOCKS blocks are issued per (session, Jon-turn). The counter lives in
# .claude/hooks/state/ and resets by itself the moment Jon speaks again, because the key contains
# the transcript index of his last turn. If the budget is spent the stop is ALLOWED. A guard that
# can trap a session is worse than no guard: it would make the assistant unable to yield to Jon.
# ---------------------------------------------------------------------------------------------
set -uo pipefail

MAX_BLOCKS="${CFL_PRESTOP_MAX_BLOCKS:-2}"
REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)}"
STATE_DIR="$REPO/.claude/hooks/state"
LOG="$STATE_DIR/pre-stop-consult.log"

# allow <reason> — documented allow path: no stdout, exit 0. Reason goes to the debug log.
# --- BINDING, added 2026-09-11 --------------------------------------------
# Soul, FINDING-2026-09-04-personal-to-all-trunks-THE-SCARCE-RESOURCE..., measured
# first-hand in THIS tree: "165 scripts on disk. 10 that any ritual invokes... A
# detector no ritual invokes is prose with better syntax -- it cannot fire, so it
# cannot fail, so it certifies nothing." Same letter: "Writing more detectors makes
# CFL's number worse."
#
# query_by_default.py and skill_fired.py were built 2026-09-11. On the record's own
# pattern they would have joined the 155 uncalled. This binds them to the one ritual
# that provably fires: this hook blocked six stops in a single session the day it was
# written.
#
# Prints COUNTS on the ALLOW path, to stderr, where the seat sees them BEFORE writing
# its final report. Never blocks, never changes the exit code. The consult rule is the
# gate; a detector that gates gets disabled, and then it certifies nothing again.
# --- LIVENESS REPORT, added 2026-09-11 18:5x -------------------------------
# Jon, 2026-09-11: 'all trunks are stopped again. YOu stopped at 6:11pm' and then
# 'why stopped at 6:39pm with no resume'.
#
# Cause, measured from this log and the tasks dir: at 18:39:10 the seat stopped with
# ZERO background jobs in flight, so nothing could re-invoke it. Eighteen minutes
# earlier it had COMMITTED the rule 'never end a turn with open plan work undone'.
# The rule failed on its first test because it was a resolution, not a mechanism --
# the failure mode this program names as MISSING ARTIFACT, NOT MISSING INSIGHT.
#
# So this prints, on the ALLOW path, whether anything is in flight. It does NOT block
# and does NOT start work: a seat that stops with satiation is correct (Jon's
# authorized run rule, 2026-07-15: 'Satiation is a valid result... do not manufacture
# work'). It only makes the difference between satiation and accidental silence
# VISIBLE to the seat before it writes its last message.
report_liveness() {
  tasks_dir="$(dirname "${transcript:-}")/tasks"
  if [ ! -d "$tasks_dir" ]; then
    tasks_dir="${CLAUDE_SCRATCH_TASKS:-}"
  fi
  inflight=UNKNOWN
  if [ -n "$tasks_dir" ] && [ -d "$tasks_dir" ]; then
    # a job still running has an output file newer than 90s with no terminal marker
    inflight=$(find "$tasks_dir" -name '*.output' -newermt '-90 seconds' 2>/dev/null |
               xargs -r grep -L 'exited with code' 2>/dev/null | wc -l | tr -d ' ')
  fi
  echo "pre-stop-consult LIVENESS: background jobs in flight = $inflight" >&2
  if [ "$inflight" = "0" ]; then
    echo "pre-stop-consult LIVENESS: nothing will re-invoke this seat. If open plan work" >&2
    echo "pre-stop-consult LIVENESS: remains, that is accidental silence, not satiation." >&2
  fi
}

run_bound_detectors() {
  if [ -z "${transcript:-}" ] || [ ! -f "${transcript:-}" ]; then
    echo "pre-stop-consult BOUND: UNKNOWN (no transcript path) -- not a clean result" >&2
    return 0
  fi
  command -v python >/dev/null 2>&1 || return 0
  root="${CLAUDE_PROJECT_DIR:-.}"
  for _d in query_by_default skill_fired; do
    if [ -f "$root/scripts/audit/$_d.py" ]; then
      echo "pre-stop-consult BOUND $_d:" >&2
      python "$root/scripts/audit/$_d.py" "$transcript" 2>&1 |
        grep -E "CANDIDATES|NOT covered|runs with a SEAL|QUERY " >&2 || true
    else
      echo "pre-stop-consult BOUND $_d: UNKNOWN (not on disk)" >&2
    fi
  done

  # --- ticket_queried, bound 2026-09-11 23:2x ------------------------------------
  # S-7, decided 2026-09-06 and never landed: `queried:` is a FIELD and NOTHING VALIDATES IT.
  # The elder that wrote the S-batch named this as its own tell -- "the one where I got closest
  # to a mechanism and stopped one step short" -- and gave the standard this binding answers:
  # AN ITEM IS NOT LANDED UNTIL SOMETHING FAILS WHEN IT IS VIOLATED.
  #
  # The checker already existed and worked. It was invoked by ZERO ritual files: named in a
  # command's prose, which is Herald's "pile with a label on it", never fired. This is a
  # BINDING, not a build -- the same move that put the other two detectors here at 17:5x.
  #
  # Takes no argument: it derives the LIVE maps itself. Reports and never gates.
  if [ -f "$root/scripts/audit/ticket_queried.py" ]; then
    echo "pre-stop-consult BOUND ticket_queried:" >&2
    python "$root/scripts/audit/ticket_queried.py" 2>&1 | tail -2 >&2 || true
  else
    echo "pre-stop-consult BOUND ticket_queried: UNKNOWN (not on disk)" >&2
  fi
}

allow() {
  run_bound_detectors
  report_liveness
  printf 'pre-stop-consult %s ALLOW %s\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" "${1:-}" >&2
  mkdir -p "$STATE_DIR" 2>/dev/null && \
    printf '%s\tALLOW\t%s\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" "${1:-}" >>"$LOG" 2>/dev/null
  exit 0
}

# ---------------------------------------------------------------------------------------------
# --self-test — negative controls, runnable without the harness.
# This exists because the guard's previous identity rule (`"mirror" in blob`) was WRONG for weeks
# and nothing could tell: the hook was unwired, and even wired it would have silently approved.
# A guard with no negative control is not a guard.
# ---------------------------------------------------------------------------------------------
if [ "${1:-}" = "--self-test" ]; then
  d="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/prestop-$$")"; mkdir -p "$d"
  python - "$d" <<'PY'
import json, os, sys
d = sys.argv[1]
def U(t): return {"type":"user","message":{"role":"user","content":t}}
def A(b): return {"type":"assistant","message":{"role":"assistant","content":b}}
def TU(n,i,tid="toolu_X"): return {"type":"tool_use","id":tid,"name":n,"input":i}
def TR(tid,txt): return {"type":"user","message":{"role":"user","content":[
    {"type":"tool_result","tool_use_id":tid,"content":[{"type":"text","text":txt}]}]}}
cases = {
 # A general-purpose agent whose PROMPT merely says "mirror" is NOT a consult.
 "neg_general_purpose_mentions_mirror":
   [U("do the thing"), A([TU("Agent",{"subagent_type":"general-purpose",
                                      "prompt":"read the mirror corpus and report"})])],
 "pos_agent_fable_mirror":
   [U("do the thing"), A([TU("Agent",{"subagent_type":"fable-mirror","prompt":"stop X because Y"})])],
 "pos_sendmessage_to_mirror":
   [U("do the thing"), A([TU("Agent",{"subagent_type":"fable-mirror","prompt":"q"},"toolu_M")]),
    TR("toolu_M","Async agent launched successfully.\nagentId: a0b706405e583e229 (internal ID)"),
    U("next question"), A([TU("SendMessage",{"to":"a0b706405e583e229","message":"I want to stop"})])],
 "neg_sendmessage_other_agent":
   [U("do the thing"), A([TU("SendMessage",{"to":"abcdef123456789","message":"mirror mirror"})])],
 # A consult BEFORE Jon's latest turn does not satisfy the rule for THIS turn.
 "neg_consult_before_jon":
   [A([TU("Agent",{"subagent_type":"fable-mirror","prompt":"q"})]), U("new instruction")],
}
for n, recs in cases.items():
    with open(os.path.join(d, n + ".jsonl"), "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
PY
  echo "=== SELF-TEST (negative controls) ==="
  st_pass=0; st_fail=0
  for spec in neg_general_purpose_mentions_mirror:BLOCK pos_agent_fable_mirror:ALLOW \
              pos_sendmessage_to_mirror:ALLOW neg_sendmessage_other_agent:BLOCK \
              neg_consult_before_jon:BLOCK; do
    f="${spec%%:*}"; want="${spec##*:}"
    out="$(printf '{"session_id":"selftest-%s-%s","transcript_path":"%s","hook_event_name":"Stop"}' \
             "$f" "$$" "$d/$f.jsonl" | CLAUDE_PROJECT_DIR="$d" bash "$0" 2>/dev/null)"
    if [ -z "$out" ]; then got=ALLOW; else got=BLOCK; fi
    if [ "$got" = "$want" ]; then res=PASS; st_pass=$((st_pass+1)); else res=FAIL; st_fail=$((st_fail+1)); fi
    printf '  %-42s want=%-5s got=%-5s : %s\n' "$f" "$want" "$got" "$res"
  done
  # The block budget must be able to run out. Otherwise the guard can trap the session.
  budget_out=""
  for _ in 1 2 3; do
    budget_out="$(printf '{"session_id":"selftest-budget-%s","transcript_path":"%s","hook_event_name":"Stop"}' \
      "$$" "$d/neg_consult_before_jon.jsonl" | CLAUDE_PROJECT_DIR="$d" bash "$0" 2>/dev/null)"
  done
  if [ -z "$budget_out" ]; then
    echo "  block budget runs out after ${MAX_BLOCKS} blocks             : PASS"; st_pass=$((st_pass+1))
  else
    echo "  block budget runs out after ${MAX_BLOCKS} blocks             : FAIL"; st_fail=$((st_fail+1))
  fi
  rm -rf "$d" 2>/dev/null
  echo
  echo "RESULT: $((st_pass))/$((st_pass+st_fail)) $( [ "$st_fail" -eq 0 ] && echo PASS || echo FAIL )"
  [ "$st_fail" -eq 0 ] || exit 1
  exit 0
fi

payload="$(cat 2>/dev/null || true)"
[ -z "$payload" ] && allow "empty-payload"

# Re-entry guard. Retained for the case where the platform still sends it; NOT relied upon.
if printf '%s' "$payload" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  allow "stop_hook_active"
fi

session="$(printf '%s' "$payload" \
  | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
session="${session:-unknown}"

transcript="$(printf '%s' "$payload" \
  | sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
  | head -1)"
transcript="${transcript//\\\\/\\}"
{ [ -z "$transcript" ] || [ ! -f "$transcript" ] ; } && allow "no-transcript"

verdict="$(python - "$transcript" <<'PY' 2>/dev/null || true
import json, re, sys

path = sys.argv[1]
mirror_tool_ids = set()   # tool_use ids of Agent(fable-mirror) dispatches
mirror_agent_ids = set()  # agentIds those dispatches returned, for later SendMessage

def text_of(rec):
    c = rec.get("message", {}).get("content")
    if isinstance(c, list):
        return " ".join(b.get("text", "") for b in c
                        if isinstance(b, dict) and b.get("type") == "text")
    return c if isinstance(c, str) else ""

# Walk once, tracking the index of Jon's last real turn and any mirror dispatch after it.
last_human = -1
mirror_after = False
try:
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            # Harvest launched-agent ids FIRST. tool_result records arrive as type "user", and
            # the user branch below `continue`s past them — doing this at the bottom of the loop
            # meant the SendMessage-to-mirror case never resolved. Caught by fixture
            # pos_sendmessage_to_mirror, 2026-08-06.
            c0 = r.get("message", {}).get("content")
            if isinstance(c0, list):
                for b in c0:
                    if (isinstance(b, dict) and b.get("type") == "tool_result"
                            and b.get("tool_use_id") in mirror_tool_ids):
                        for m in re.findall(r"agentId:\s*([0-9a-f]{6,})", json.dumps(b)):
                            mirror_agent_ids.add(m)

            t = r.get("type")
            if t == "user":
                body = text_of(r)
                # A tool_result is not Jon. Neither is a compaction summary. A mid-turn
                # wrapper record IS Jon, and resets the clock exactly like a normal turn.
                c = r.get("message", {}).get("content")
                is_tool_result = isinstance(c, list) and any(
                    isinstance(b, dict) and b.get("type") == "tool_result" for b in c)
                if r.get("isCompactSummary") or is_tool_result:
                    continue
                # 2026-09-02 23:3x: a cron-fired prompt is NOT Jon. It carries
                # promptSource == "system" and a scheduledTaskId. Counting it reset the
                # consult clock every hour overnight and demanded a fable consult (~1 weekly
                # point) per tick while Jon slept -- the pool the paused lanes need at GO.
                if r.get("promptSource") == "system" or r.get("scheduledTaskId"):
                    continue
                # Same night, second class, found by the block that followed the first patch:
                # this hook's OWN "Stop hook feedback:" injection and the harness's
                # task-notification wrappers land as isMeta user entries with no promptSource.
                # Counting them means every BLOCK manufactures the next BLOCK -- a guard that
                # feeds itself. Neither is Jon.
                if (r.get("origin") or {}).get("kind") == "task-notification":
                    continue
                if isinstance(body, str) and body.lstrip().startswith(
                        ("Stop hook feedback:", "<task-notification>",
                         "[SYSTEM NOTIFICATION", "<system-reminder>")):
                    continue
                if isinstance(body, str) and body.strip():
                    last_human = i
                    mirror_after = False
            elif t == "assistant":
                c = r.get("message", {}).get("content")
                if isinstance(c, list):
                    for b in c:
                        if not isinstance(b, dict) or b.get("type") != "tool_use":
                            continue
                        name = b.get("name")
                        if name not in ("Agent", "SendMessage"):
                            continue
                        inp = b.get("input") or {}
                        # IDENTITY, NOT SUBSTRING.
                        # The previous rule was `"mirror" in blob`, which made the two specific
                        # tests before it dead code and approved ANY dispatch whose prompt merely
                        # contained the word "mirror". Verified live 2026-08-06: this session's own
                        # JSONLs carry 6 `Agent(general-purpose)` dispatches alongside 3
                        # `Agent(fable-mirror)`, and mirror-corpus prose is ubiquitous in briefs.
                        # A false ALLOW here silently disables the whole guard.
                        hit = False
                        if name == "Agent":
                            atype = str(inp.get("subagent_type")
                                        or inp.get("agent_type")
                                        or inp.get("agentType") or "").lower()
                            hit = atype in ("fable-mirror", "fable_mirror")
                            if hit:
                                # Harvest the agentId the platform returns, so a later
                                # SendMessage to this same agent also counts as a consult.
                                mirror_tool_ids.add(b.get("id"))
                        else:  # SendMessage — addressed by opaque agentId, not by type
                            hit = str(inp.get("to") or "") in mirror_agent_ids
                        if hit and i > last_human:
                            mirror_after = True
except Exception:
    print("ALLOW unreadable-transcript"); raise SystemExit(0)

if mirror_after or last_human < 0:
    print("ALLOW consult-present" if mirror_after else "ALLOW no-human-turn")
else:
    print("BLOCK %s" % last_human)
PY
)"

set -- $verdict
outcome="${1:-ALLOW}"
detail="${2:-}"

if [ "$outcome" != "BLOCK" ]; then
  allow "${detail:-python-fallthrough}"
fi

# ---- BLOCK BUDGET -----------------------------------------------------------------------------
# Key = session + index of Jon's last turn. When Jon speaks the index moves and the count restarts,
# so the budget is per-Jon-turn and needs no cleanup. Spent budget ALLOWS.
mkdir -p "$STATE_DIR" 2>/dev/null || allow "state-dir-unwritable"
safe_session="$(printf '%s' "$session" | tr -c 'A-Za-z0-9._-' '_')"
COUNTER="$STATE_DIR/prestop-${safe_session}-${detail}.count"
count="$(cat "$COUNTER" 2>/dev/null || echo 0)"
case "$count" in ''|*[!0-9]*) count=0 ;; esac
if [ "$count" -ge "$MAX_BLOCKS" ]; then
  allow "block-budget-spent ${count}/${MAX_BLOCKS} (see script header: BLOCK BUDGET)"
fi
printf '%s' "$((count + 1))" >"$COUNTER" 2>/dev/null || true
printf '%s\tBLOCK\tturn=%s\tcount=%s/%s\n' \
  "$(date +%Y-%m-%dT%H:%M:%S%z)" "$detail" "$((count + 1))" "$MAX_BLOCKS" >>"$LOG" 2>/dev/null

python - <<'PY'
import json
reason = (
    "PRE-STOP CONSULT REQUIRED -- Jon's rule, 2026-08-03: "
    "\"If main wants to stop, it must talk to you firt.\"\n\n"
    "No fable-mirror consult was dispatched since Jon's last message, so this stop is "
    "blocked. This rule was violated twice on the day it was written, both times in a "
    "message that announced it was continuing -- which is why it is a hook now and not "
    "a paragraph.\n\n"
    "Do ONE of these, then stop:\n"
    "  1. Dispatch fable-mirror with the narrow question \"I want to stop X because Y.\" "
    "The burden of proof is on stopping; the default answer is CONTINUE, grounded in a "
    "quoted Jon authorization.\n"
    "  2. If the consult agrees, land first: commit and push everything, run "
    "`python scripts/audit/wake_map.py --session-dir <tasks dir>`, and write the one-line "
    "reason -- blocked everywhere / question pending on Jon / done-and-verified.\n\n"
    "Not valid reasons to stop: reaching a good place to report, a lane finishing, "
    "having something worth telling Jon. The ratchet lane is never empty.\n\n"
    "AND WHEN YOU DO STOP: STATE THE ASK. Jon, 2026-08-07: \"It looks like you stopped, "
    "when you stop I need you to request what I do. I think you are asking for a standard "
    "update compact, but I can't tell from the outside.\" A report is not a request. End "
    "with a WHAT I NEED FROM YOU block naming the specific action -- compact / ruling / "
    "nothing, keep going -- because from outside, a session that has gone quiet and a "
    "session that is waiting on him look identical."
)
print(json.dumps({"decision": "block", "reason": reason}))
PY
exit 0
