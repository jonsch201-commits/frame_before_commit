#!/usr/bin/env bash
# lint.sh -- Claude Professional wiki lint. TWENTY-SEVEN checks; TWENTY-FIVE are selftest-proven failable.
# C10 and C11 were UNPROVEN until 2026-09-02; both now have controls that FIRE. Kept here
# because three banners in this file used to claim three different numbers (9 / 11 / "Nine"),
# and a gate suite that cannot count itself is the first thing to disbelieve.
# (C8 added 2026-08-17 and NOT yet proven — see the banner above check_budgets).
# Usage: scripts/lint.sh            run the checks (exit 0 all pass, 1 any fail)
#        scripts/lint.sh --selftest prove every check CAN fail, then prove the tree passes
# Schema: wiki/SCHEMA.md. Created 2026-08-14 (closes cross-trunk review P1).

set -u
cd "$(dirname "$0")/.." || exit 2
FAILS=0

# --- SELF-HASH GUARD. `[m 2026-08-28]` A background run of this script was edited mid-run and
# reported `syntax error near unexpected token '('` at a line `bash -n` calls CLEAN -- because the
# file WAS clean and bash was reading an older object through a held inode. ⛔ THAT IS A STALE
# OBJECT, NOT A STALE VALUE, and no freshness check on the file can catch it: the parse was an
# honest report about something that was no longer the thing under test.
# ⭐ So the run declares ITSELF unknown. Not a check over the tree -- a precondition on the verdict.
# See wiki/concepts/the-object-moved-under-the-instrument.md.
# ⚠️ PROVEN BY A DIRECT FIXTURE, NOT BY --selftest, and the distinction is stated rather than
# blurred: `LINT_FAKE_START_HASH=deadbeef bash scripts/lint.sh` -> exit 4, both hashes named
# `[m 2026-08-28 17:4x]`; the unmodified run exits 0. It is NOT in --selftest because each
# control would be a second full run and --selftest already exceeds a 2-minute budget (T-A).
# ⛔ So it is not counted in the "13 of 15 selftest-proven failable" banner.
self_hash() { md5sum "$0" 2>/dev/null | awk '{print $1}'; }
SELF_HASH_START="${LINT_FAKE_START_HASH:-$(self_hash)}"

fail() { echo "FAIL [$1] $2"; FAILS=$((FAILS+1)); }
pass() { echo "PASS [$1] $2"; }

# --- Check 1: frontmatter (--- opener + title:/name: + date:) on concepts/references/fbc pages
check_frontmatter() {
  local bad=0 f
  for f in wiki/concepts/*.md wiki/references/*.md wiki/fbc/*.md; do
    [ -f "$f" ] || continue
    if [ "$(head -1 "$f")" != "---" ] \
       || ! head -20 "$f" | grep -qE '^(title|name):' \
       || ! head -20 "$f" | grep -qE '^(date|created|sealed):'; then
      echo "  frontmatter defect: $f"; bad=$((bad+1))
    fi
  done
  if [ "$bad" -eq 0 ]; then pass C1 "frontmatter MINIMUM present on concepts/references/fbc (opener + title-or-name + a date key) -- NOT completeness; C10 grades that"
  else fail C1 "$bad page(s) missing ---/title-or-name/date"; fi
}

# --- Check 2: index<=>disk, both directions
check_index() {
  local missing=0 unindexed=0 slug f
  # 2026-08-24: resolution WIDENED from wiki/concepts/ alone to the four directories
  # index_gen.py actually scans. C2 previously called a link to a real, indexed page on disk
  # "dangling" purely because it lived in wiki/sources/ -- the same class as C1 (non-recursive)
  # disagreeing with C10 (os.walk) about what a page is. Two gates must not hold two definitions.
  # The REVERSE direction stays concepts-only on purpose: every concept must be curated into the
  # index by hand, which is an editorial requirement, not a filesystem one.
  for slug in $(grep -o '\[\[[a-z0-9-]*\]\]' wiki/index.md | tr -d '[]' | sort -u); do
    [ -f "wiki/concepts/$slug.md" ] || [ -f "wiki/references/$slug.md" ] ||     [ -f "wiki/sources/$slug.md" ] || [ -f "wiki/fbc/$slug.md" ] ||       { echo "  index names missing page: $slug"; missing=$((missing+1)); }
  done
  for f in wiki/concepts/*.md; do
    slug=$(basename "$f" .md)
    grep -q "\[\[$slug\]\]" wiki/index.md || { echo "  page not in index: $slug"; unindexed=$((unindexed+1)); }
  done
  if [ "$missing" -eq 0 ] && [ "$unindexed" -eq 0 ]; then
    pass C2 "index<=>disk reconciled ($(ls wiki/concepts/*.md | wc -l) concepts, both directions)"
  else fail C2 "$missing dangling index link(s), $unindexed unindexed page(s)"; fi
}

# --- Check 3: WAKE.md byte budget
check_wake() {
  local budget="${WAKE_BUDGET:-6144}" size
  size=$(stat -c '%s' WAKE.md 2>/dev/null || echo 0)
  if [ "$size" -gt 0 ] && [ "$size" -le "$budget" ]; then pass C3 "WAKE.md $size B <= $budget B"
  else fail C3 "WAKE.md $size B exceeds budget $budget B (or missing)"; fi
}

# --- Check 4: no git remote (Jon gate)
check_remote() {
  local n
  if [ "${LINT_FAKE_REMOTE:-0}" = "1" ]; then n=1; else n=$(git remote | grep -c .); fi
  if [ "$n" -eq 0 ]; then pass C4 "git remote count 0 (gate holds)"
  else fail C4 "git remote count $n — Jon gate: this repo must have NO remote"; fi
}

# --- Check 5: stamp integrity (U8) — delegate to stamp-check.sh over this repo's dated artifacts
check_stamps() {
  local targets=() f out rc
  for f in wiki/log.md wiki/tracker/tracker.md; do [ -f "$f" ] && targets+=("$f"); done
  if [ "${LINT_STAMP_TARGET:-}" != "" ]; then targets=("$LINT_STAMP_TARGET"); fi
  # 2026-09-12: in a derived public tree neither target ships; a checker run over nothing printed
  # "flagged 0" under a FAIL. Name the UNKNOWN. UNKNOWN dominates a PASS, so it stays a FAIL.
  if [ "${#targets[@]}" -eq 0 ]; then fail C5 "stamp-check UNKNOWN: no stamp targets in this tree (wiki/log.md, wiki/tracker/tracker.md absent) -- no measurement, not a pass"; return; fi
  # Grandfather line = U8 instrument adoption (2026-08-15 07:49 CDT). Frozen history is audited by
  # running stamp-check.sh directly; lint holds only what was written under the rule.
  out=$(STAMP_SINCE="${STAMP_SINCE:-$(date -d '2026-08-15 07:49:00' +%s)}" bash scripts/stamp-check.sh "${targets[@]}" 2>&1); rc=$?
  if [ "$rc" -eq 0 ]; then pass C5 "stamp integrity clean ($(echo "$out" | grep -c '^READ:') file(s) audited)"
  else echo "$out" | grep '^FLAG'; fail C5 "stamp-check flagged $(echo "$out" | grep -c '^FLAG') stamp(s)"; fi
}

# --- Check 6: close-record closure (T-1). Every captured compact must have a same-or-later
# wiki/log.md entry. Built 2026-08-17 after session 5f6a442a compacted at 09:41 and left the
# newest log entry two days stale — the receipt proved the hook fired and nothing proved the
# session closed.
check_closure() {
  local rlog rdate ldate
  rlog="${LINT_RECEIPT_LOG:-exchange/precompact-receipts.log}"
  if [ ! -f "$rlog" ]; then fail C6 "receipt ledger missing at $rlog"; return; fi
  rdate=$(grep -v 'zz-selftest' "$rlog" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}' | sort | tail -1)
  ldate=$(grep -ohE '^#{2,3} [0-9]{4}-[0-9]{2}-[0-9]{2}' wiki/log.md | awk '{print $2}' | sort | tail -1)
  if [ -z "$rdate" ]; then pass C6 "no captured compact in the ledger yet"; return; fi
  if [ -z "$ldate" ]; then fail C6 "wiki/log.md carries no dated entry at all"; return; fi
  if [ "$rdate" \> "$ldate" ]; then
    fail C6 "compact captured $rdate but newest wiki/log.md entry is $ldate — a session closed without a durable record"
  else pass C6 "close-record closure (newest receipt $rdate <= newest log entry $ldate)"; fi
}

# ⛔⛔ C7 v2 (P-7) WAS WRITTEN 2026-08-17 ~16:4x BY A WOKEN SESSION THAT COULD NOT EXECUTE IT.
# `bash scripts/lint.sh`, `bash scripts/lint.sh --selftest` AND `bash -n scripts/lint.sh` are all
# refused by the permission layer in a woken session — so this edit is UNRUN AND UNPARSED. It has
# never been shown to run, to pass, or even to be syntactically valid. The FIRST session with
# execute rights must run `--selftest` BEFORE trusting any C7 verdict, and must treat a green C7
# from an unverified edit as exactly the inherited-green defect C7 was built to catch.
# Owner: Professional, 2026-08-18. Do not close this comment by reading the code — close it by running it.
#
# --- Check 7: no unproven liveness claim. Built 2026-08-17 after this trunk carried
# "wake-on-need (relay registration stands)" in WAKE.md for two days while the switchboard's
# config held exactly one target ("personal"), allowMultiTarget:false, and zero professional
# sources [measured]. The registration was a post in a thread; it was never a key in the
# instrument. A claim that another process will wake this trunk is only true once an order has
# FIRED and reached it, so the claim now requires a proof file that names the fired order.
check_liveness() {
  local wake proof
  wake="${LINT_WAKE_FILE:-WAKE.md}"
  proof="${LINT_WAKE_PROOF:-exchange/wake-path-proof.md}"
  # WITHDRAWN TEXT IS NOT A CLAIM: strike-through spans (~~...~~) are stripped before matching.
  # Found by running C7 against this trunk's own WAKE.md minutes after building it — the file
  # STRUCK the false claim and the check read the struck words as an assertion. A check that
  # cannot tell a retraction from a claim punishes the correction.
  local body
  body=$(tr '
' ' ' < "$wake" 2>/dev/null | sed 's/~~[^~]*~~//g')
  if ! printf '%s' "$body" | grep -qiE 'wake-on-need|relay registration|switchboard will wake|registered .*(relay|switchboard)'; then
    pass C7 "no wake-path claim asserted in $(basename "$wake") (asleep-with-no-wake-path is the honest default)"
    return
  fi
  # --- P-7, 2026-08-17 session 13. THE SINGLE-FILE PROOF PATH WAS NOT DISCRIMINATING.
  # Measured that day: of the five ^FIRED: lines in the single proof file, THREE were written by a
  # session other than the one woken, and two were a DIFFERENT MECHANISM (relay, not letter-watch)
  # that the file had no field to record. A check that greps one shared file for ^FIRED: cannot tell
  # one session's fire from another's, cannot tell which mechanism fired, and cannot detect that one
  # session's receipt was clobbered by a concurrent peer — all three happened on 2026-08-17.
  # C7 now grades the RECEIPTS DIRECTORY, one file per session, and requires three fields.
  local dir conformant=0 unidentified=0 crossattested="" f sid fired
  dir="${LINT_WAKE_RECEIPTS:-exchange/wake-receipts}"
  if [ -d "$dir" ]; then
    for f in "$dir"/*.md; do
      [ -f "$f" ] || continue
      grep -qE '^FIRED:' "$f" || continue
      # the declaring session id: first `session:` field carrying a uuid-shaped token
      sid=$(grep -oE 'session:[^A-Za-z0-9]*[0-9a-f]{8}-[0-9a-f-]{4,}' "$f" | head -1 |
            grep -oE '[0-9a-f]{8}-[0-9a-f-]{4,}')
      # ⛔ A RECEIPT THAT DECLARES `FIRED:` BUT CARRIES NO PARSEABLE SESSION ID USED TO VANISH HERE
      # -- skipped before `conformant` counted anything, so it left the DENOMINATOR rather than the
      # graded set, and the pass line reported a population that excluded it. C27s defect, third
      # instance, found by C28 on its first real run rather than by a peer reading this source.
      if [ -z "$sid" ]; then unidentified=$((unidentified + 1)); continue; fi
      # MECHANISM IS A REQUIRED FIELD, not an inference from prose elsewhere in the file.
      fired=$(grep -E '^FIRED:' "$f")
      printf '%s' "$fired" | grep -qiE 'letter-watch|relay-raised|relay|operator|mechanism:' || continue
      # ⛔ SELF-ATTESTATION: a receipt may not carry another session's fire. Session 13 recorded two
      # peers' fires and had to put them in the narrative file for exactly this reason.
      if printf '%s' "$fired" | grep -oE '[0-9a-f]{8}-[0-9a-f-]{4,}' | grep -qv "^$sid$"; then
        crossattested="$crossattested $(basename "$f")"
        continue
      fi
      conformant=$((conformant + 1))
    done
  fi
  if [ -n "$crossattested" ]; then
    fail C7 "receipt(s)$crossattested carry a FIRED line naming a session other than their own — a fire attested by a session that is not its subject is hearsay, not a receipt"
    return
  fi
  if [ "$conformant" -gt 0 ]; then
    pass C7 "wake-path claim backed by $conformant conformant receipt(s) in $dir (session id + mechanism + own fire only); $unidentified receipt(s) declared FIRED with no parseable session id and are counted here rather than dropped -- they are NOT in the conformant count and never were, but they are now in the printed population"
    return
  fi
  # FALLBACK, retained deliberately: the single-file path still answers when no receipts dir exists,
  # so repointing C7 cannot silently un-gate a trunk that has not migrated yet.
  if [ -f "$proof" ] && grep -qE '^FIRED:' "$proof"; then
    fail C7 "$(basename "$wake") claims a wake path and $proof has fired lines, but $dir holds NO conformant per-session receipt — the shared file cannot say WHICH session was woken or BY WHAT"
  else
    fail C7 "$(basename "$wake") claims a wake path with no fired receipt at $proof or in $dir — a registration posted in a thread is not a key in the instrument"
  fi
}

# ⛔⛔ C8 WAS WRITTEN 2026-08-17 ~17:0x BY A WOKEN SESSION THAT COULD NOT EXECUTE IT — same bound as
# C7 v2 above, re-probed the same session and refused again: `bash scripts/lint.sh`, `bash -n`, a `.ps1`
# by call operator, and a nested powershell process are ALL refused to this seat. UNRUN AND UNPARSED.
# The first seat with execute rights runs `--selftest` BEFORE trusting any C8 verdict.
# Owner: Professional (author), acceptance test owed by the first seat with execute rights, 2026-08-18.
#
# --- Check 8: constitution byte budgets (Secretary's ASSIGNMENTS §2, 2026-08-17: "a lint that fails
# when a constitution exceeds its byte budget, so the shrink cannot silently regrow"). Table-driven:
# scripts/constitution-budgets.tsv. Rule: wiki/concepts/resident-core-split-rule.md.
# C3 above is the legacy single-file form of this check and is kept deliberately — repointing a check
# must not un-gate the file the old check was holding.
check_budgets() {
  local table seat today bad=0 warned=0 graded=0 deferred=0
  table="${LINT_BUDGET_TABLE:-scripts/constitution-budgets.tsv}"
  seat="${LINT_SEAT:-professional}"
  today="${LINT_TODAY:-$(date +%Y-%m-%d)}"
  if [ ! -f "$table" ]; then fail C8 "budget table missing at $table"; return; fi
  local path budget deadline owner size
  while IFS=$'\t' read -r path budget deadline owner; do
    owner="${owner%$'\r'}"
    case "$path" in ''|'#'*|'path') continue ;; esac
    # A MALFORMED ROW FAILS LOUDLY. A budget table that silently drops rows certifies files nobody read.
    case "$budget" in ''|*[!0-9]*) echo "  MALFORMED $path — budget '$budget' is not a byte count"; bad=$((bad+1)); continue ;; esac
    if [ -z "$owner" ] || [ -z "$deadline" ]; then
      echo "  MALFORMED $path — every row needs a deadline and an owning seat"; bad=$((bad+1)); continue
    fi
    if [ "$owner" != "$seat" ]; then
      echo "  DEFERRED $path (budget $budget B by $deadline) — owner: $owner"
      deferred=$((deferred+1)); continue
    fi
    size=$(stat -c '%s' "$path" 2>/dev/null || echo "")
    # ⛔ UNREADABLE IS NOT A PASS: a row this seat OWNS and cannot read is UNKNOWN, and UNKNOWN dominates.
    if [ -z "$size" ]; then
      echo "  UNREADABLE $path — owned by this seat ($seat) and unreadable; UNKNOWN dominates a pass"
      bad=$((bad+1)); continue
    fi
    graded=$((graded+1))
    [ "$size" -le "$budget" ] && continue
    if [ "$today" \< "$deadline" ]; then
      echo "  WARN $path $size B over budget $budget B by $((size-budget)) B — deadline $deadline not reached"
      warned=$((warned+1))
    else
      echo "  OVER $path $size B > $budget B by $((size-budget)) B — deadline $deadline passed"
      bad=$((bad+1))
    fi
  done < "$table"
  if [ "$bad" -eq 0 ]; then
    pass C8 "constitution budgets: $graded graded, $warned pre-deadline warning(s), $deferred deferred (owners named above)"
  else fail C8 "$bad budget row(s) failing — over budget past deadline, unreadable, or malformed"; fi
}

# --- Check 9: a staged letter is not a delivered letter. Built 2026-08-17 22:1x CDT, attended,
# after this close measured NINE outbox letters dated 08-17 (154,139 B, written 14:42-17:39 by
# headless wakes) present in ZERO of the four sibling trees, plus three more in 1 of 4 -- while
# WAKE.md asserted one of them "Sent CFL 18:3x". Outbox membership was read as delivery by every
# seat that looked, INCLUDING the attended sweep at 17:49 that swept the same directory for a
# different purpose. Receiver-side presence is the only evidence of delivery there has ever been.
# UNREACHABLE counts as missing: a tree this seat cannot read is UNKNOWN, and UNKNOWN dominates PASS.
check_delivery() {
  local out_dir epoch graded=0 pre=0 bad=0
  out_dir="${LINT_OUTBOX:-exchange/outbox}"
  epoch="${LINT_DELIVERY_EPOCH:-2026-08-17}"
  # PER-TREE graded-from, 2026-08-30. This list used to be HARDCODED here -- the same defect
  # relay.sh was cured of on 2026-08-28, left standing inside the gate itself. It is now derived
  # from trunk-roster.tsv's DELIVER rows, and each tree carries its OWN start date from column 4.
  # WHY IT BLOCKED ANTIGRAVITY FOR TWO DAYS: graded against the global 08-17 epoch, a trunk whose
  # inbound was created 08-28 fails every letter written since 08-17 -- for a reason its owner
  # cannot fix. That is a gate that teaches seats to ignore it, so the tree was left ungraded
  # instead. With a per-tree date a trunk joins the graded set the day it becomes reachable.
  local trees=() tree_from=() _rdir _rdisp _rrest _rfrom _cand _ti2
  local roster="${LINT_ROSTER:-scripts/trunk-roster.tsv}"
  if [ -n "${LINT_SIBLING_TREES:-}" ]; then
    IFS='|' read -r -a trees <<< "$LINT_SIBLING_TREES"
    IFS='|' read -r -a tree_from <<< "${LINT_SIBLING_FROM:-}"
  elif [ -f "$roster" ]; then
    while IFS=$'	' read -r _rdir _rdisp _rrest _rfrom; do
      case "$_rdir" in ''|'#'*) continue ;; esac
      [ "$_rdisp" = "DELIVER" ] || continue
      # ⛔ 2026-09-04, C9 went 26/26 PASS -> 96/96 FAIL in one morning and NOTHING OF OURS CHANGED.
      # A peer deposited a letter at "G:/My Drive/Claude/Claude Foundational Layer/exchange/inbound"
      # at 10:14, CREATING that directory. The repo is one level deeper
      # (.../Claude Foundational Layer/claude-foundational-layer/). This loop tried the SHALLOW
      # candidate first and `break`ed on it, so every letter was graded against a one-file decoy
      # born sixty minutes earlier. [m: shallow=1 entry, deep=676.]
      # ⭐ AN ABSENT PATH FAILS LOUDLY; A DECOY PATH PASSES THE EXISTENCE TEST AND ANSWERS
      # CONFIDENTLY WRONG. `-d` is not evidence that a directory is the PEER'S.
      # FIX: prefer the repo-named (deeper) candidate, and when BOTH exist say so out loud --
      # the second one is somebody's misdelivery and a silent pick hides it.
      local _deep _shallow _picked
      _shallow="G:/My Drive/Claude/$_rdir"
      _deep="G:/My Drive/Claude/$_rdir/$(printf '%s' "$_rdir" | tr 'A-Z ' 'a-z-')"
      _picked=""
      for _cand in "$_deep" "$_shallow"; do
        if [ -d "$_cand/exchange/inbound" ]; then _picked="$_cand"; break; fi
      done
      if [ -n "$_picked" ]; then
        if [ -d "$_deep/exchange/inbound" ] && [ -d "$_shallow/exchange/inbound" ]; then
          echo "  AMBIGUOUS-ROOT $_rdir -- TWO inbound directories exist; grading against the repo-named one ($_deep). The other ($_shallow, $(ls -1 "$_shallow/exchange/inbound" 2>/dev/null | wc -l) file(s)) is a MISDELIVERY TARGET: mail left there reaches nobody, and its owner is whoever wrote it."
        fi
        trees+=("$_picked"); tree_from+=("${_rfrom:-$epoch}")
      fi
    done < "$roster"
  fi
  if [ "${#trees[@]}" -eq 0 ]; then
    fail C9 "zero sibling trees resolved -- the delivery population is UNKNOWN, and UNKNOWN dominates a PASS"
    return
  fi
  for _ti2 in "${!trees[@]}"; do [ -n "${tree_from[$_ti2]:-}" ] || tree_from[$_ti2]="$epoch"; done
  if [ ! -d "$out_dir" ]; then fail C9 "outbox missing at $out_dir"; return; fi
  # T-A FIX 2026-08-23, attended. The 08-22 close measured this check at 71 letters x 4 trees =
  # 284 stat calls over a Google Drive mount and lint.sh was KILLED at exit 143 on a 2-minute
  # budget. A gate that cannot finish inside a headless seat's default timeout is a gate that does
  # not run. Fix: list each sibling inbound ONCE into memory, then test membership with a bash
  # pattern match -- 4 directory reads and zero subprocesses per pair, instead of 284 network stats.
  # GRADING SEMANTICS ARE UNCHANGED: every graded letter must still be present in every tree, and
  # UNREACHABLE still counts as missing.
  local -a tree_list=()
  local ti
  for ti in "${!trees[@]}"; do
    if [ -d "${trees[$ti]}/exchange/inbound" ]; then
      tree_list[$ti]=$'\n'"$(ls -1 "${trees[$ti]}/exchange/inbound" 2>/dev/null)"$'\n'
    else
      tree_list[$ti]=""   # empty marks UNREACHABLE; an unreadable tree is UNKNOWN, and UNKNOWN dominates PASS
    fi
  done
  # ⚠️ RELAYED, NOT MEASURED BY THIS SEAT: CFL reports (2026-08-23) that Jon retired Herald Wiki on
  # 2026-08-08 and that 46 CFL letters landed in it afterwards. If true, grading delivery INTO a
  # retired tree compels writes to a dead trunk. This check does NOT act on a relayed ruling --
  # Herald stays graded until Jon rules here. Queued as a Jon item; see exchange/FOR-JON-REVIEW/.
  # ⛔ NAMESPACE WIDENED 2026-09-03. `[m]` The glob was `pro-to-*.md` and the outbox holds 14
  # letters that do not match it -- `pro-CORRECTION-*`, `pro-AMENDMENT-*`, `pro-DISPOSITION-*`,
  # `pro-GATE-VERDICT-*`, `RECEIPT-*-professional-*`. ⭐ THE EXCLUDED CLASS IS THE HIGH-STAKES ONE:
  # a CORRECTION is the letter whose non-delivery costs most, and C9 has been printing
  # "delivery reconciled" over a population that omitted every one of them. Found because CFL
  # logged a "misnamed addendum finding" against one of ours; the misnaming was the symptom and
  # the un-graded namespace was the defect. ⚠️ The widened class carries its OWN epoch (today):
  # grading 14 letters back to 08-08 would fail for a reason no session can now fix, which is the
  # defect the per-tree epoch above already exists to avoid. Backlog is COUNTED AND PRINTED.
  local f b d miss t wide_pre=0 wide=0
  local wepoch="${LINT_WIDE_EPOCH:-2026-09-03}"
  for f in "$out_dir"/pro-*.md "$out_dir"/RECEIPT-*-professional-*.md; do
    [ -e "$f" ] || continue
    b=$(basename "$f")
    d=$(printf '%s' "$b" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | tail -1)
    if [ -z "$d" ] || [ "$d" \< "$epoch" ]; then pre=$((pre+1)); continue; fi
    case "$b" in
      pro-to-*) ;;
      *) wide=$((wide+1))
         if [ "$d" \< "$wepoch" ]; then wide_pre=$((wide_pre+1)); continue; fi ;;
    esac
    graded=$((graded+1))
    # An explicit `staged:` line in the first 8 lines is the ONLY exemption, and it is a claim the
    # author signs -- not a silence. A letter that cannot be delivered says so in its own body.
    if head -8 "$f" | grep -qiE '(^|[^a-z])staged:'; then continue; fi
    # ADDRESSEE PARSING, added 2026-08-23 attended, because the runtime fix exposed a worse defect:
    # C9 required EVERY letter in EVERY sibling tree, so a letter correctly delivered to its ONE
    # addressee graded RED. A gate that fires red on correct behaviour teaches seats to ignore it,
    # which is the same end state as a gate that times out. Tokens are read from the filename
    # prefix -- `pro-to-cfl-secretary-...` addresses cfl and secretary. ⛔ AN UNPARSEABLE PREFIX
    # FALLS BACK TO ALL FOUR TREES: the strict old behaviour stays the default whenever this parser
    # is not certain, so the fix can only ever narrow a grade it can justify.
    local rest tok addressees=""
    rest="${b#pro-to-}"
    # ⛔ 2026-09-04. The SendMessage record hook (P4-6) began writing `pro-msg-<ts>-to-<peer>-...`
    # into this outbox at 09:20, and the parse above strips only the `pro-to-` prefix -- so every
    # hook record fell through to the ALL-TRUNKS default and graded RED against four trunks it was
    # never addressed to. ⭐ A NEW MECHANISM THAT MANUFACTURES A STANDING RED IS WORSE THAN NO
    # MECHANISM: the red is permanent, correct behaviour produces it, and seats learn to skip C9.
    # The addressee is in the name; read it where the hook puts it, after `-to-`.
    case "$b" in pro-msg-*-to-*) rest="${b#*-to-}" ;; esac
    while :; do
      tok="${rest%%-*}"
      case "$tok" in
        # `antigravity` added 2026-08-28. ⚠️ RECOGNISED AS A TOKEN ONLY -- its tree is NOT in
        # `trees` above, so this narrows nothing and grades nothing; it exists so that a letter
        # named `pro-to-antigravity-...` PARSES instead of falling through to the all-four
        # default. ⛔ Adding the tree to the graded set still waits on a PER-TREE `graded-from`
        # date -- without one, every letter since the 08-17 epoch grades RED against a trunk
        # that did not exist until 08-25, and a gate that fails for a reason its owner cannot
        # fix teaches seats to ignore it. Ticketed, not bodged.
        cfl|secretary|herald|soul|personal|ssp|antigravity|all) addressees="$addressees $tok"; rest="${rest#*-}" ;;
        *) break ;;
      esac
    done
    [ -n "$addressees" ] || addressees=" all"
    # `all` must reach every trunk the roster resolves, not the four someone remembered.
    case "$addressees" in *" all"*) addressees=" cfl secretary herald soul personal antigravity" ;; esac
    miss=""
    for ti in "${!trees[@]}"; do
      t="${trees[$ti]}"
      # A TREE IS NOT GRADED FOR LETTERS OLDER THAN ITS OWN graded-from. A trunk that did not
      # exist cannot have received a letter, and a red grade for that is a false accusation.
      [ "$d" \< "${tree_from[$ti]}" ] && continue
      # tree -> token map. soul and personal both live in the Claude Personal trunk.
      case "$(basename "$t")" in
        # ⛔ HERALD IS REACHED IN THE PERSONAL TRUNK. `[measured 2026-08-23 by this seat]`
        # herald-wiki's outbox has not been written since 2026-07-28, and all 48 pro-to-* letters
        # sitting in its inbound now have a copy in Personal (37 dual-delivered + the recovery
        # directory Herald wrote today). Grading delivery against a tree the receiver does not read
        # measures the wrong thing -- C9 exists to ask "did it reach the receiver", not "did a file
        # land in a named folder". ⭐ NOTE THE BASIS: this is NOT the relayed Jon retirement ruling,
        # which this seat still has not seen the primary bytes of. It is this seat's own measurement
        # that the receiver is elsewhere. A gate narrowed on a relayed ruling would be gate-shopping;
        # a gate narrowed on a measured receiver location is the gate doing its job.
        "Claude Personal")               [[ "$addressees" == *" soul"* || "$addressees" == *" personal"* || "$addressees" == *" herald"* ]] || continue ;;
        "claude-foundational-layer")     [[ "$addressees" == *" cfl"* ]] || continue ;;
        "herald-wiki")                   continue ;;   # dead drop; never graded, see above
        "Claude Secretary")              [[ "$addressees" == *" secretary"* ]] || continue ;;
        "Antigravity")                   [[ "$addressees" == *" antigravity"* ]] || continue ;;
      esac
      if [ -z "${tree_list[$ti]}" ]; then miss="$miss $(basename "$t")=UNREACHABLE"
      elif [[ "${tree_list[$ti]}" != *$'\n'"$b"$'\n'* ]]; then miss="$miss $(basename "$t")=ABSENT"; fi
    done
    if [ -n "$miss" ]; then bad=$((bad+1)); echo "  UNDELIVERED $b --$miss"; fi
  done
  if [ "$pre" -gt 0 ]; then echo "  PRE-EPOCH $pre letter(s) dated before $epoch -- not graded, counted here so the exemption is visible"; fi
  if [ "$wide" -gt 0 ]; then echo "  WIDENED NAMESPACE $wide letter(s) outside the pro-to-* prefix, of which $wide_pre are BACKLOG dated before $wepoch -- printed, not swept, and not graded"; fi
  if [ "$bad" -gt 0 ]; then
    fail C9 "$bad of $graded graded outbox letter(s) missing from a sibling inbound -- an outbox file is a draft, not a delivery"
  else
    local _fromlist="" _ti3
    for _ti3 in "${!trees[@]}"; do _fromlist="$_fromlist $(basename "${trees[$_ti3]}")=${tree_from[$_ti3]}"; done
    pass C9 "delivery reconciled ($graded letter(s) present in every inbound their filename addresses; ${#trees[@]} tree(s), each graded from its own date:$_fromlist). NAMESPACE: pro-to-* plus $wide letter(s) under other pro-* / RECEIPT-*-professional-* prefixes ($wide_pre of them pre-$wepoch BACKLOG, printed not graded). A prefix nobody graded is a delivery nobody checked."
  fi
}

# --- Check 10: the DERIVED index matches disk, and metadata conformance is reported
# C1 checks that a minimum exists. It said "frontmatter complete" for months while
# 30 of 37 pages carried no description: at all -- a PASS message asserting more than
# the check performed. C10 is the one that grades the metadata Jon named on 2026-08-23.
check_derived_index() {
  local out rc
  out=$(python scripts/index_gen.py --check 2>&1); rc=$?
  if [ $rc -eq 0 ]; then
    pass C10 "derived index matches disk"
  else
    echo "$out" | head -6
    fail C10 "derived index has drifted -- run: python scripts/index_gen.py"
    return
  fi
  # report conformance; do NOT fail on it yet. Failing today would block every commit
  # on a 30-page backlog, and Jon's standing rule is that rules producing stopping are
  # defective rules. This reports until the backlog is worked, then it earns teeth.
  local miss alias
  # 2026-08-24: these two lines used grep -oP. This environment's grep refuses -P
  # ("supports only unibyte and UTF-8 locales"), 2>/dev/null swallowed the error, miss came back
  # empty and the && chain short-circuited -- so the METADATA BACKLOG line, written for the exact
  # complaint Jon named, HAD NEVER ONCE PRINTED. Rewritten in portable sed. A reporting line that
  # cannot report is a-no-op-that-returns-success wearing a green tick.
  miss=$(sed -n 's/^| \*\*missing `description:`\*\* | \*\*\([0-9]\+\)\*\* |.*/\1/p' wiki/INDEX-DERIVED.md | head -1)
  alias=$(sed -n 's/^| \*\*values found under a NON-CANONICAL alias\*\* | \*\*\([0-9]\+\)\*\* |.*/\1/p' wiki/INDEX-DERIVED.md | head -1)
  [ -n "${miss:-}" ] && [ "${miss:-0}" -gt 0 ] && echo "  METADATA BACKLOG (reported, not failed): $miss page(s) with no description:, $alias value(s) under a non-canonical alias"
  return 0
}


# C11 -- SKILL SCRIPT REACHABILITY. Herald measured 2026-08-24 that sync-universal.sh
# copies skills/ and has NEVER copied scripts/, so every skill body naming a script was
# written against CFL's tree. Professional: 17 of 17 references dead, 7 of 7 skills fully
# broken; Personal: 16 of the same 17. The MATCHING reference counts prove the bodies copy
# faithfully; the DIFFERING dead counts prove resolution is local. REPORTS, never fails --
# the fix is declaring dependencies, not copying scripts/ into every trunk, which would
# manufacture the divergent-duplicate defect this trunk documented on 2026-08-23.
check_skill_reach() {
  local out dead
  out=$(python scripts/skill_reach.py 2>&1) || { fail C11 "skill_reach.py errored -- reachability UNEVALUATED"; return; }
  # UNKNOWN DOMINATES A PASS. The first version of this check called pass() on the UNKNOWN branch
  # while printing "UNKNOWN is not a PASS" -- a gate that could not fail, shipped the same morning
  # this trunk published a-gate-that-fires-red-on-correct-behaviour. Caught by an adversarial audit
  # 40 minutes later. UNKNOWN now FAILS, which is the only reading consistent with U12-N.
  if printf '%s' "$out" | grep -q '^UNKNOWN'; then
    printf '%s
' "$out" | tail -2
    fail C11 "skill reachability UNEVALUATED (no ~/.claude/skills) -- UNKNOWN dominates a PASS"
    return
  fi
  dead=$(printf '%s' "$out" | sed -n 's/.*| \([0-9]\+\) DEAD.*/\1/p' | head -1)
  case "${dead:-x}" in ''|*[!0-9]*) fail C11 "could not parse a dead-count from skill_reach output"; return;; esac
  if [ "$dead" -gt 0 ]; then
    printf '%s
' "$out" | tail -3
    pass C11 "skill script reachability MEASURED: ${dead} dead reference(s) -- reported, not failed (declare deps; do NOT copy scripts/)"
  else
    pass C11 "skill script reachability: every referenced script resolves in this trunk"
  fi
  return 0
}

# --- Check 12: a [verbatim] GRADE inside a TABLE ROW must carry a CITE in that row.
#
# Herald's clause ([SECRETARY] CLAUDE-STANDARDS.md s4, f30a0ab): A GRADE COLUMN WITHOUT A CITE COLUMN
# MANUFACTURES UNFALSIFIABLE PROVENANCE. Their instance: a kids'-medical row graded
# [verbatim] with a date column, a grade column, and no cite -- and every channel searched
# returned zero. Not a lapse by whoever filled it: THE SCHEMA PERMITTED IT.
#
# This program's rule -- a quotation carries its file and line or it travels unquoted --
# had been enforced in PROSE and NEVER IN A TABLE. A structured artifact with no cite
# column is where an ungrounded quote is SAFEST, because the grade makes it look adjudicated.
#
# THE THREE STATES, and only the third is safe (Secretary, 2026-08-24, from this seat's
# own formulation "a table that happens to contain only grounded quotes is not a
# controlled table"):
#   REALISED  -- schema permits it AND a quote is ungrounded.
#   LATENT    -- schema permits it, quotes happen to be grounded. LUCK PLUS A HABIT.
#   CONTROLLED-- the schema CANNOT express a graded quote without a cite.
# [m 2026-08-24 19:5x] This trunk measured LATENT: 3 [verbatim] table rows, 3 cited, 0
# ungrounded. THIS CHECK IS WHAT MOVES IT TO CONTROLLED. A declaration at the head of the
# file was the first fix and it is a WRITTEN WARNING -- which this seat spent 2026-08-24
# proving is not a mechanism (six heredoc failures against a standing warning).
#
# DELIBERATELY NARROW. An earlier detector tried to find QUOTES and ran at ~86% false
# positives across three successive rules (72 -> 7 -> 1). The grade TOKEN is unambiguous
# and needs no extraction, so this check fails loudly instead of reporting quietly.
# BOUND: it cannot see an ungrounded quote that carries NO grade. That is real and stated;
# a narrow check that fails beats a broad one that reports.
check_table_cites() {
  local bad total root cite hits uncited
  root="${LINT_CITE_ROOT:-.}"
  # ONE grep pass. A line-by-line bash version did not finish in 7 minutes on this tree and
  # was killed -- A GATE TOO SLOW TO RUN IS A GATE THAT GETS DISABLED.
  cite='\.(md|jsonl|tsv|txt|json|py|sh|ps1)|history\.jsonl|:[0-9]{1,5}|raw/transcripts|paste-cache|§[0-9]|`[0-9a-f]{7}`|PR #[0-9]'
  # ⛔ CAPTURE THE EXIT CODE BEFORE THE PIPE. grep: 0=matched, 1=ran-and-found-nothing,
  # 2+=ERROR. Only 0 and 1 are ANSWERS. An empty result with rc>=2 means the scan DID NOT
  # RUN, and a scan that did not run is UNKNOWN, not clean -- a command that did not run
  # and a command that found nothing look identical from the output.
  local rc
  hits=$(grep -rn --include='*.md' -E '^[[:space:]]*\|.*\[verbatim\]' "$root" 2>/dev/null)
  rc=$?
  if [ "$rc" -ge 2 ]; then
    fail C12 "the [verbatim] scan of $root could not run (grep rc=$rc); UNKNOWN dominates a PASS"
    return
  fi
  hits=$(printf '%s\n' "$hits" | grep -v '/exchange/inbound/' || true)   # peer captures are out of population
  # ⛔ AND SO ARE MACHINE-RENDERED TRANSCRIPTS. Added 2026-09-01, the hour raw/transcripts/
  # went 0 -> 74 files: C12 grades what THIS TRUNK ASSERTS; a rendered transcript records what
  # was SAID. The inbound exclusion above is the precedent -- both are captures, neither is
  # authorship. Without this, every past conversation holding a table row is a permanent lint
  # failure, and no-deletion means it never ages out. The exclusion is PRINTED below, because
  # a population you shrink without saying so is the defect this check exists to catch.
  hits=$(printf '%s
' "$hits" | grep -v '/raw/transcripts/' || true)
  total=$(printf '%s\n' "$hits" | awk 'END{print NR+0}')
  # ⛔ STRIP grep's OWN `path:line:` PREFIX BEFORE GRADING. Leaving it on made every row
  # look cited -- `:1:` matches the line-reference branch of $cite -- and C12 COULD NOT
  # FAIL. Caught by the selftest in the same patch that introduced it.
  # A CHECK MUST NEVER TEST ITS OWN FORMATTING.
  uncited=$(printf '%s\n' "$hits" | sed -E 's/^[^:]*:[0-9]+://' | grep -vE "$cite" | awk 'END{print NR+0}')
  bad=${uncited:-0}
  if [ "$bad" -gt 0 ]; then
    printf '%s\n' "$hits" | while IFS= read -r h; do
      [ -n "$h" ] || continue
      printf '%s' "$h" | sed -E 's/^[^:]*:[0-9]+://' | grep -qE "$cite" && continue
      echo "  UNCITED GRADE $(printf '%s' "$h" | cut -d: -f1,2) — [verbatim] table row with no cite in the row"
    done
    fail C12 "$bad [verbatim] table row(s) carry a grade and no cite (of ${total:-0} graded row(s)). POPULATION: exchange/inbound/ (peer captures) and raw/transcripts/ (machine-rendered history) EXCLUDED BY CONSTRUCTION -- this grades what this trunk ASSERTS, never what a transcript RECORDS."
  else
    pass C12 "every [verbatim] table row carries a cite (${total:-0} graded row(s) checked). POPULATION: exchange/inbound/ and raw/transcripts/ EXCLUDED by construction -- a CLEAN here is a claim about authored rows only."
  fi
}

# --- Check 13: every check_* DEFINED must be CALLED in run_all. PRESENT-AND-UNCALLED.
#
# The Secretary's third face of a-control-with-no-reader (2026-08-24): their new check
# existed, its selftest PASSED, and it was never invoked in the real run. Not absent, not
# too slow -- DEFINED AND NEVER CALLED, which is a control that checks nothing while
# reporting green. After "no reader" and "too slow to run", that is a third face.
#
# [m 2026-08-24 20:1x] This file measured 12 defined / 12 called / 0 uncalled -- BY
# INSPECTION. That is LATENT on this seat's own three-state model: a habit, not a control.
# C13 is what makes it CONTROLLED.
#
# BOUND: proves every DEFINED check is CALLED. Does NOT prove the call does anything
# useful, and cannot see a check nobody wrote.
check_wired() {
  local src defined called uncalled n_def n_call
  src="${LINT_SELF:-scripts/lint.sh}"
  if [ ! -f "$src" ]; then fail C13 "cannot read $src to verify wiring; UNKNOWN dominates"; return; fi
  defined=$(grep -oE '^check_[a-z_]+\(\)' "$src" | sed 's/()//' | sort -u)
  # only the run_all BODY, so a definition is never mistaken for a call
  # ONE-LINE run_all: `/^}/` never matches its own line, so a range-sed runs on into the
  # selftest and counts a check MENTIONED IN A FIXTURE as CALLED. [m] that read 15 called
  # against 13 defined. A check named only in its own selftest would have passed C13 --
  # the precise hole C13 exists to close, in C13.
  called=$(grep -E '^run_all\(\) \{' "$src" | grep -oE 'check_[a-z_]+' | sort -u)
  n_def=$(printf '%s\n' "$defined" | awk 'END{print NR+0}')
  n_call=$(printf '%s\n' "$called" | awk 'END{print NR+0}')
  # AN EMPTY POPULATION IS NOT A CLEAN POPULATION. [m 2026-08-24 20:3x] C13 returned
  # PASS on `0 defined, 0 called`, so a lint file that lost every check definition -- or
  # a grep that FAILED TO SPAWN -- reported green. The Secretary's E4-sibling from the
  # spawn side: A COMMAND THAT DID NOT RUN AND A COMMAND THAT FOUND NOTHING LOOK
  # IDENTICAL FROM THE OUTPUT. This landed on the gate that shipped 20 minutes earlier.
  if [ "${n_def:-0}" -eq 0 ]; then
    fail C13 "ZERO check definitions found in $src -- a scan that finds nothing is UNKNOWN, not clean"
    return
  fi
  uncalled=$(comm -23 <(printf '%s\n' "$defined") <(printf '%s\n' "$called"))
  if [ -n "$uncalled" ]; then
    printf '%s\n' "$uncalled" | while IFS= read -r u; do
      [ -n "$u" ] && echo "  PRESENT-AND-UNCALLED $u — defined in $src and never invoked by run_all"
    done
    fail C13 "$(printf '%s\n' "$uncalled" | grep -c .) check(s) defined but never called (${n_def} defined, ${n_call} called)"
  else
    pass C13 "every defined check is wired into run_all (${n_def} defined, ${n_call} called)"
  fi
}

# --- Check 14: roster drift. The courier tree list is hand-enumerated; nothing reconciled it
# against the disk until 2026-08-28, when a trunk that had been writing to the fleet for three
# days turned out to be invisible to every automated delivery path in the program (0 hits for
# "antigravity" across all five trunks' scripts/). A ROSTER NOTHING RECONCILES IS A COMMENT.
# The failing condition is entirely ours to satisfy: every directory gets a row, or C14 fails.
check_roster() {
  local roster root listed=0 missing=0 d n
  roster="${LINT_ROSTER:-scripts/trunk-roster.tsv}"
  root="${LINT_TRUNK_ROOT:-G:/My Drive/Claude}"
  if [ ! -f "$roster" ]; then fail C14 "roster absent at $roster -- UNKNOWN dominates a PASS"; return; fi
  if [ ! -d "$root" ]; then fail C14 "trunk root unreadable at $root -- a scan that cannot run is UNKNOWN, never clean"; return; fi
  # AN EMPTY POPULATION IS NOT A CLEAN POPULATION (C13's lesson, applied here on purpose):
  # if the glob returns nothing, the disk is unreadable, not empty.
  local dirs=()
  for d in "$root"/*/; do [ -d "$d" ] && dirs+=("$(basename "$d")"); done
  if [ "${#dirs[@]}" -eq 0 ]; then
    fail C14 "ZERO directories found under $root -- a scan that finds nothing is UNKNOWN, not clean"
    return
  fi
  for n in "${dirs[@]}"; do
    if grep -qE "^$(printf '%s' "$n" | sed 's/[][\.*^$/]/\\&/g')	" "$roster"; then
      listed=$((listed+1))
    else
      missing=$((missing+1))
      echo "  UNROSTERED $n -- present under $root, no row in $roster (add DELIVER / REACHABLE-NOT-ROUTED / EXCLUDED / NOT-A-TRUNK + reason)"
    fi
  done
  if [ "$missing" -gt 0 ]; then
    fail C14 "$missing of $((listed+missing)) director(ies) under the trunk root have no roster row -- a new trunk is invisible to every courier until it does"
  else
    pass C14 "roster reconciled ($listed director(ies) under $root, every one dispositioned)"
  fi
}


# --- Check 15: A DELIVER ROW MUST BE DELIVERABLE. C14 proves every directory HAS a disposition;
# it says nothing about whether the disposition is TRUE, and the very first roster it certified
# carried a false one. `[m 2026-08-28]` `Herald Wiki` was rowed DELIVER while Jon had retired that
# wiki on 2026-08-08, lint.sh C9 already skipped it as a dead drop, CLAUDE.md already called it a
# DEAD DROP -- and its own exchange/inbound/ held 00-DEAD-ADDRESS-DO-NOT-DEPOSIT-HERE.md, written
# by Herald on 08-23. This seat hand-couriered a letter there anyway on 08-28 BECAUSE THE ROSTER
# SAID DELIVER. Secretary CLAUDE-STANDARDS §21 (raised by Herald) named it the same afternoon:
# the letter announcing that a trunk could not be reached was deposited where it could not be read.
# ⭐ A RECONCILIATION AGAINST THE DISK IS NOT A RECONCILIATION AGAINST THE TRUTH. C14 counted rows;
# C15 reads the destination and lets the destination speak.
check_deliverable() {
  local roster root row dir disp cand tree bad=0 ok=0 marker
  roster="${LINT_ROSTER:-scripts/trunk-roster.tsv}"
  root="${LINT_TRUNK_ROOT:-G:/My Drive/Claude}"
  if [ ! -f "$roster" ]; then fail C15 "roster absent at $roster -- UNKNOWN dominates a PASS"; return; fi
  while IFS=$'	' read -r dir disp _rest; do
    case "$dir" in ''|'#'*) continue ;; esac
    [ "$disp" = "DELIVER" ] || continue
    tree=""
    for cand in "$root/$dir" "$root/$dir/$(printf '%s' "$dir" | tr 'A-Z ' 'a-z-')"; do
      [ -d "$cand/exchange/inbound" ] && { tree="$cand"; break; }
    done
    if [ -z "$tree" ]; then
      bad=$((bad+1))
      echo "  UNDELIVERABLE $dir -- rowed DELIVER, no exchange/inbound/ exists under $root/$dir"
      continue
    fi
    # The destination's own words override our row. Two forms, because a marker can be named
    # or declared: a DO-NOT-DEPOSIT/DEAD-ADDRESS filename, or frontmatter `kind: archive-marker`.
    # ⛔ THIS MATCHED A DIRECTORY ON ITS FIRST REAL RUN. `ls -1` lists directories too, and Herald
    # had just created Claude Personal/exchange/inbound/recovered-from-dead-address-2026-08-28/ --
    # a folder whose existence proves that address is LIVE (it is where letters were RESCUED TO).
    # C15 read it as a do-not-deposit notice and failed the fleet's busiest mailbox.
    # ⭐ A FILTER THAT OVER-MATCHES MANUFACTURES A FINDING -- this trunk published that sentence on
    # 2026-08-28 about a `*pro*` substring sweep and reproduced the error in the fix for it, eight
    # hours later, in a different costume. -type f, top level only: a NOTICE IS A FILE.
    marker=$(find "$tree/exchange/inbound" -maxdepth 1 -type f \( -iname '*DEAD-ADDRESS*' -o -iname '*DO-NOT-DEPOSIT*' \) -printf '%f
' 2>/dev/null | head -1)
    if [ -z "$marker" ]; then
      marker=$(grep -l --include='*.md' -m1 '^kind: *archive-marker' "$tree/exchange/inbound"/*.md 2>/dev/null | head -1)
      [ -n "$marker" ] && marker=$(basename "$marker")
    fi
    if [ -n "$marker" ]; then
      bad=$((bad+1))
      echo "  DEAD-ADDRESS $dir -- rowed DELIVER, but its inbound holds $marker. THE DESTINATION SAYS NO."
    else
      ok=$((ok+1))
    fi
  done < "$roster"
  if [ "$((ok+bad))" -eq 0 ]; then
    fail C15 "ZERO DELIVER rows in $roster -- an empty courier list is UNKNOWN, not clean"
  elif [ "$bad" -gt 0 ]; then
    fail C15 "$bad of $((ok+bad)) DELIVER row(s) name a destination that is absent or has posted a do-not-deposit marker -- a row is not a receipt"
  else
    pass C15 "every DELIVER row is deliverable ($ok destination(s): inbound exists, no dead-address marker)"
  fi
}







# ⭐ THE FIVE OATH CHECKS LIVE IN A SKILL, NOT HERE -- extracted 2026-08-30 on Jon's correction
# ("that should have been a skill"). One implementation, reachable by any trunk. If the skill is
# absent the gate FAILS rather than silently running four fewer checks.
OATH_CHECKS="${OATH_CHECKS:-.claude/skills/oath-checks/oath_checks.sh}"

# ⛔ C23's DECLARATION, and it is a declaration rather than a discovery ON PURPOSE.
# Jon, 2026-08-31 wake: "Shift all search and file-scan tooling from G: Drive to the N: Drive NVMe
# mirror." Naming the mirror here is what makes that order FALSIFIABLE: from this line on, every
# close asks whether the corpus we query still contains the work we did. Unset it and C23 says so
# in its PASS line rather than going quietly green.
LINT_CORPUS_MIRROR="${LINT_CORPUS_MIRROR:-N:/claude-corpus/professional}"
export LINT_CORPUS_MIRROR
# ⛔ C25/C26's DECLARATION -- the PER-TRUNK VECTOR INDEX `scripts/graphrag.sh query` answers from.
# C23 grades the corpus; C24 grades the SHARED index. Until 2026-08-31 nothing graded the one this
# trunk actually queries, and it was 7.7 days stale with 2.59% of its chunks reachable by default.
# LINT_VECTOR_DEFAULT_TIERS mirrors retrieve.py's allow-set (`self.tiers = {"knowledge"}`). If that
# allow-set changes and this line does not, C26 grades a scope this trunk no longer has -- so the
# value is DECLARED here and named in C26's own output rather than discovered from the retriever.
LINT_VECTOR_DB="${LINT_VECTOR_DB:-${LOCALAPPDATA:-$HOME/.cache}/claude/graphrag/professional.sqlite}"
# ⛔ '*' MEANS EVERY TIER, and it is only correct here because `scripts/graphrag.sh query` was
# reversed to default to --all-tiers on 2026-08-31 after an A/B measurement (proto/tier-scope:
# recall 0/6 -> 6/6, noise 6/6 -> 6/6 with none lost). ⭐ C26 CROSS-CHECKS THIS LINE AGAINST THE
# WRAPPER via LINT_VECTOR_WRAPPER and FAILS if they disagree -- so this value cannot be edited to
# silence the check without also editing the artifact it describes.
LINT_VECTOR_DEFAULT_TIERS="${LINT_VECTOR_DEFAULT_TIERS:-*}"
LINT_VECTOR_WRAPPER="${LINT_VECTOR_WRAPPER:-scripts/graphrag.sh}"
# C28 -- the lint that lints this lint. DECLARE the sources; never discover them, or a file that
# stops being scanned looks identical to a file with nothing to find.
LINT_SKIPLINT_FILES="${LINT_SKIPLINT_FILES:-.claude/skills/oath-checks/oath_checks.sh scripts/lint.sh}"
# C29 -- the compact-boundary durable-record pairing, against Jon's 2026-09-01 charge that the
# all-trunk standard update be "indeed the default and not just the hoped outcome."
LINT_BOUNDARY_RECEIPTS="${LINT_BOUNDARY_RECEIPTS:-exchange/precompact-receipts.log}"
LINT_BOUNDARY_RECORD="${LINT_BOUNDARY_RECORD:-wiki/log.md}"
# ADVISORY ONLY -- C29 does not gate on this. 2h is the shape the duty actually has;
# the gate is the window-free criterion (a record before the next boundary).
LINT_BOUNDARY_WINDOW_H="${LINT_BOUNDARY_WINDOW_H:-2}"
LINT_BOUNDARY_GRACE_H="${LINT_BOUNDARY_GRACE_H:-6}"
export LINT_VECTOR_DB LINT_VECTOR_DEFAULT_TIERS LINT_VECTOR_WRAPPER
LINT_INDEX_DB="${LINT_INDEX_DB:-N:/claude-indexes/graphrag-federated/index.sqlite}"
LINT_INDEX_TRUNK="${LINT_INDEX_TRUNK:-Professional}"
export LINT_INDEX_DB LINT_INDEX_TRUNK
if [ -f "$OATH_CHECKS" ]; then
  # shellcheck source=/dev/null
  . "$OATH_CHECKS"
else
  check_self_application()  { fail C16 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_beacon_freshness()  { fail C17 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_reverse_delivery()  { fail C18 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_oath_register()     { fail C19 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_jon_surface()       { fail C20 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_obligation_reachable() { fail C21 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_body_links()        { fail C22 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_corpus_currency()   { fail C23 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_index_coverage()    { fail C24 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_vector_index_age()  { fail C25 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_vector_index_scope(){ fail C26 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_stamp_future()      { fail C27 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_uncounted_skip()    { fail C28 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_inbound_reconciled(){ fail C31 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_boundary_record()   { fail C29 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
  check_queried_field()    { fail C32 "oath-checks skill absent at $OATH_CHECKS -- UNKNOWN dominates a PASS"; }
fi

# --- Check 30: population exclusions (arm 4). A check can have a domain that is NON-EMPTY,
# CORRECTLY MEASURED and OWNED, and still EXCLUDE THE ARTIFACT IT EXISTS TO PROTECT.
# 2026-09-02, two instances in one day, two trunks:
#   Professional: corpus-sync.sh ROOTS held DIRECTORIES, so SEVEN root-level docs -- WAKE.md,
#     CLAUDE.md, START-HERE.md, RESUME.md among them -- were outside its population. It reported
#     already-fresh=667 while the mirror carried a 34-hour-old WAKE.md. Four of seven were stale.
#   Personal [relayed+ soul, measured their seat]: check 2 globs exchange/inbound/*.md at DEPTH 1
#     over 440 files while 566 exist on disk. 126 invisible, 28 of them under Jon-Threads/.
#     THE CHECK THAT EXISTS TO ENSURE JON'S MAIL IS READ COULD NOT SEE A DIRECTORY CALLED
#     Jon-Threads.
# ⛔ THE EXCLUSION IS A PROPERTY OF THE ENUMERATOR, NOT OF THE DIRECTORY [relayed+ soul, and the
# first draft of this check got it wrong: it named "ls -1 / -maxdepth 1" as one rule].
# THIS TRUNK IS CURRENTLY CLEAN ON THAT INSTANCE and that is luck, not design: C9 enumerates with
# `ls -1` (lint.sh:293) and oath_checks.sh:254 does the same, so the day a peer deposits into a
# subdirectory the delivery check goes blind WITHOUT CHANGING ITS OUTPUT. This check exists to
# make that day loud instead of silent.
# ITS OWN BOUND, stated because arm 4 is the easiest of the four to overclaim: it counts only the
# exclusions somebody thought to NAME. An exclusion nobody has noticed is still invisible here.
check_population_exclusions() {
  local root="${LINT_EXCL_ROOT:-.}" d shallow deep diff total=0 detail=""
  for d in exchange/inbound exchange/outbox; do
    [ -d "$root/$d" ] || continue
    shallow=$(find "$root/$d" -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l)
    deep=$(find "$root/$d" -type f -name '*.md' 2>/dev/null | wc -l)
    diff=$((deep - shallow))
    total=$((total + diff))
    detail="$detail $d: depth1=$shallow all-depths=$deep excluded=$diff;"
  done
  if [ "$total" -eq 0 ]; then
    pass C30 "0 file(s) excluded by depth from the enumerated populations --$detail RULE PRINTED BESIDE THE TOTAL, AND THE PRIMITIVE NAMED WITH IT: this check counts *.md by find at depth 1 vs any depth. THAT IS NOT THE PRIMITIVE C9 USES. C9 enumerates with ls -1 (lint.sh:293), which returns the SUBDIRECTORY NAME as an entry and no .md filter at all -- measured: ls -1 gives [Jon-Threads, top.md] where find gives [top.md]. SAME DIRECTORY, TWO POPULATIONS, TWO FAILURE MODES: a buried letter is INVISIBLE to a find/*.md consumer and reads as UNDELIVERED to C9. A zero here is a claim about *.md files at depth, in THESE two paths, by THIS enumerator. It does not grade C9 and does not grade any other exclusion rule."
  else
    fail C30 "$total file(s) invisible to the depth-1 enumerations --$detail A subdirectory letter is undelivered mail that no check can see"
  fi
}

run_all() { check_population_exclusions; check_frontmatter; check_index; check_wake; check_remote; check_stamps; check_closure; check_liveness; check_budgets; check_delivery; check_derived_index; check_skill_reach; check_table_cites; check_wired; check_roster; check_deliverable; check_self_application; check_beacon_freshness; check_reverse_delivery; check_oath_register; check_jon_surface; check_obligation_reachable; check_body_links; check_corpus_currency; check_index_coverage; check_vector_index_age; check_vector_index_scope; check_stamp_future; check_uncounted_skip; check_boundary_record; check_inbound_reconciled; check_queried_field; }

if [ "${1:-}" = "--selftest" ]; then
  echo "== SELFTEST: proving each check can fail =="
  CANARY="wiki/concepts/zz-lint-selftest-canary.md"
  trap 'rm -f "$CANARY"' EXIT
  printf 'no frontmatter here\n' > "$CANARY"      # violates C1 (no ---) and C2 (unindexed)
  OUT=$(FAILS=0; check_frontmatter; check_index)
  echo "$OUT" | grep -q "FAIL \[C1\]" && echo "OK C1 can fail" || { echo "SELFTEST BROKEN: C1 cannot fail"; exit 3; }
  echo "$OUT" | grep -q "FAIL \[C2\]" && echo "OK C2 can fail" || { echo "SELFTEST BROKEN: C2 cannot fail"; exit 3; }
  rm -f "$CANARY"
  OUT=$(WAKE_BUDGET=1 check_wake)
  echo "$OUT" | grep -q "FAIL \[C3\]" && echo "OK C3 can fail" || { echo "SELFTEST BROKEN: C3 cannot fail"; exit 3; }
  OUT=$(LINT_FAKE_REMOTE=1 check_remote)
  echo "$OUT" | grep -q "FAIL \[C4\]" && echo "OK C4 can fail" || { echo "SELFTEST BROKEN: C4 cannot fail"; exit 3; }
  bash scripts/stamp-check.sh --selftest >/dev/null 2>&1 || { echo "SELFTEST BROKEN: stamp-check selftest failed"; exit 3; }
  # C32 fixtures live WITH the skill, so any trunk can run them without this lint: one implementation.
  bash "$(dirname "$OATH_CHECKS")/selftest_c32.sh" >/dev/null 2>&1 || { echo "SELFTEST BROKEN: C32 selftest failed -- run bash $(dirname "$OATH_CHECKS")/selftest_c32.sh"; exit 3; }
  echo "OK C32 selftest held (both verdicts, control per negative; $(dirname "$OATH_CHECKS")/selftest_c32.sh)"
  STAMP_CANARY=$(mktemp); echo "X — 2026-08-15 08:00 CDT [measured]" > "$STAMP_CANARY"
  OUT=$(LINT_STAMP_TARGET="$STAMP_CANARY" check_stamps); rm -f "$STAMP_CANARY"
  echo "$OUT" | grep -q "FAIL \[C5\]" && echo "OK C5 can fail" || { echo "SELFTEST BROKEN: C5 cannot fail"; exit 3; }
  CLOSURE_CANARY=$(mktemp)
  printf '2099-01-01 00:00:00 CDT | canary | 0 files 0 B | HEAD none | OK
' > "$CLOSURE_CANARY"
  OUT=$(LINT_RECEIPT_LOG="$CLOSURE_CANARY" check_closure); rm -f "$CLOSURE_CANARY"
  echo "$OUT" | grep -q "FAIL \[C6\]" && echo "OK C6 can fail" || { echo "SELFTEST BROKEN: C6 cannot fail"; exit 3; }
  LIVE_CANARY=$(mktemp)
  printf 'Professional is wake-on-need; the relay registration stands.
' > "$LIVE_CANARY"
  # ⚠️ EVERY C7 CASE BELOW PINS LINT_WAKE_RECEIPTS. Without it the selftest reads the REAL receipts
  # directory and "C7 can pass" passes for a reason the selftest did not construct — the same
  # inherited-green defect C7 exists to catch.
  RECEIPTS_CANARY=$(mktemp -d)
  OUT=$(LINT_WAKE_FILE="$LIVE_CANARY" LINT_WAKE_PROOF="/nonexistent/proof.md" LINT_WAKE_RECEIPTS="$RECEIPTS_CANARY" check_liveness)
  echo "$OUT" | grep -q "FAIL \[C7\]" && echo "OK C7 can fail" || { echo "SELFTEST BROKEN: C7 cannot fail"; rm -rf "$LIVE_CANARY" "$RECEIPTS_CANARY"; exit 3; }
  # P-7 case a: a shared proof file with fired lines is NO LONGER ENOUGH — it cannot say which session.
  PROOF_CANARY=$(mktemp); printf 'FIRED: wake-t99999 reached professional 2099-01-01
' > "$PROOF_CANARY"
  OUT=$(LINT_WAKE_FILE="$LIVE_CANARY" LINT_WAKE_PROOF="$PROOF_CANARY" LINT_WAKE_RECEIPTS="$RECEIPTS_CANARY" check_liveness)
  echo "$OUT" | grep -q "FAIL \[C7\]" || { echo "SELFTEST BROKEN: C7 still passes on a shared proof file with no per-session receipt"; rm -rf "$LIVE_CANARY" "$PROOF_CANARY" "$RECEIPTS_CANARY"; exit 3; }
  # P-7 case b: a conformant receipt — session id + mechanism + its own fire only — PASSES.
  printf 'session: 11111111-2222-3333-4444-555555555555
FIRED: wake-t99999 reached professional via operator letter-watch 2099-01-01
' > "$RECEIPTS_CANARY/good.md"
  OUT=$(LINT_WAKE_FILE="$LIVE_CANARY" LINT_WAKE_PROOF="/nonexistent/proof.md" LINT_WAKE_RECEIPTS="$RECEIPTS_CANARY" check_liveness)
  echo "$OUT" | grep -q "PASS \[C7\]" || { echo "SELFTEST BROKEN: C7 cannot pass on a conformant per-session receipt"; rm -rf "$LIVE_CANARY" "$PROOF_CANARY" "$RECEIPTS_CANARY"; exit 3; }
  # P-7 case c: a receipt attesting ANOTHER session's fire is hearsay and must FAIL even though a
  # conformant receipt sits beside it — the real 2026-08-17 shape, where session 13 held two peers' fires.
  printf 'session: 11111111-2222-3333-4444-555555555555
FIRED: wake-t99998 reached professional via relay-raised order, session 99999999-8888-7777-6666-555555555555
' > "$RECEIPTS_CANARY/hearsay.md"
  OUT=$(LINT_WAKE_FILE="$LIVE_CANARY" LINT_WAKE_PROOF="/nonexistent/proof.md" LINT_WAKE_RECEIPTS="$RECEIPTS_CANARY" check_liveness)
  echo "$OUT" | grep -q "FAIL \[C7\]" || { echo "SELFTEST BROKEN: C7 accepts a fire attested by a session that is not its subject"; rm -rf "$LIVE_CANARY" "$PROOF_CANARY" "$RECEIPTS_CANARY"; exit 3; }
  rm -f "$RECEIPTS_CANARY/hearsay.md"
  STRUCK_CANARY=$(mktemp)
  printf 'Old line: ~~Professional is wake-on-need, relay registration stands~~ STRUCK today.
' > "$STRUCK_CANARY"
  OUT=$(LINT_WAKE_FILE="$STRUCK_CANARY" LINT_WAKE_PROOF="/nonexistent/proof.md" LINT_WAKE_RECEIPTS="$RECEIPTS_CANARY" check_liveness)
  echo "$OUT" | grep -q "PASS \[C7\]" || { echo "SELFTEST BROKEN: C7 reads a STRUCK claim as an assertion"; rm -rf "$LIVE_CANARY" "$PROOF_CANARY" "$STRUCK_CANARY" "$RECEIPTS_CANARY"; exit 3; }
  rm -f "$LIVE_CANARY" "$PROOF_CANARY" "$STRUCK_CANARY"; rm -rf "$RECEIPTS_CANARY"
  # --- C8 cases. FOUR, because C8 has three non-pass verdicts and each has to be constructed.
  BUDGET_CANARY=$(mktemp)
  # case a: over budget with the deadline PASSED -> FAIL (budget 1 B against a file that exists)
  printf 'path\tbudget_bytes\tdeadline\towning_seat\nWAKE.md\t1\t2000-01-01\tprofessional\n' > "$BUDGET_CANARY"
  OUT=$(LINT_BUDGET_TABLE="$BUDGET_CANARY" check_budgets)
  echo "$OUT" | grep -q "FAIL \[C8\]" && echo "OK C8 can fail (over budget, deadline passed)" || { echo "SELFTEST BROKEN: C8 cannot fail on an over-budget file"; rm -f "$BUDGET_CANARY"; exit 3; }
  # case b: a row this seat OWNS and cannot read -> FAIL. Unreadable must never read as clean.
  printf 'path\tbudget_bytes\tdeadline\towning_seat\n/nonexistent/CLAUDE.md\t5120\t2000-01-01\tprofessional\n' > "$BUDGET_CANARY"
  OUT=$(LINT_BUDGET_TABLE="$BUDGET_CANARY" check_budgets)
  echo "$OUT" | grep -q "FAIL \[C8\]" && echo "OK C8 fails on an unreadable owned row" || { echo "SELFTEST BROKEN: C8 passes a row it could not read"; rm -f "$BUDGET_CANARY"; exit 3; }
  # case c: over budget BEFORE the deadline -> PASS, but the delta must be printed. A warning that
  # prints nothing is indistinguishable from a pass, which is the defect this line exists to block.
  printf 'path\tbudget_bytes\tdeadline\towning_seat\nWAKE.md\t1\t2999-01-01\tprofessional\n' > "$BUDGET_CANARY"
  OUT=$(LINT_TODAY=2026-08-17 LINT_BUDGET_TABLE="$BUDGET_CANARY" check_budgets)
  echo "$OUT" | grep -q "PASS \[C8\]" || { echo "SELFTEST BROKEN: C8 fails a pre-deadline row"; rm -f "$BUDGET_CANARY"; exit 3; }
  echo "$OUT" | grep -q "  WARN WAKE.md" || { echo "SELFTEST BROKEN: C8 pre-deadline row printed no WARN with its delta"; rm -f "$BUDGET_CANARY"; exit 3; }
  echo "OK C8 warns pre-deadline and prints the delta"
  # case d: another seat's row is DEFERRED WITH ITS OWNER NAMED — never graded, never silently dropped.
  printf 'path\tbudget_bytes\tdeadline\towning_seat\n/nonexistent/CLAUDE.md\t5120\t2000-01-01\tcfl\n' > "$BUDGET_CANARY"
  OUT=$(LINT_BUDGET_TABLE="$BUDGET_CANARY" check_budgets)
  echo "$OUT" | grep -q "DEFERRED /nonexistent/CLAUDE.md .* owner: cfl" || { echo "SELFTEST BROKEN: C8 did not name the owner of a deferred row"; rm -f "$BUDGET_CANARY"; exit 3; }
  echo "$OUT" | grep -q "PASS \[C8\]" || { echo "SELFTEST BROKEN: C8 failed on another seat's row"; rm -f "$BUDGET_CANARY"; exit 3; }
  echo "OK C8 defers other seats' rows by name"
  rm -f "$BUDGET_CANARY"
  # --- C9 cases. FOUR: absent, delivered, unreachable, pre-epoch. The unreachable case is the one
  # that matters -- a seat that cannot read a sibling tree must not report that tree as clean.
  DEL_OUT=$(mktemp -d); DEL_TREE=$(mktemp -d); DEL_DARK=$(mktemp -d)
  mkdir -p "$DEL_TREE/exchange/inbound"
  printf 'body\n' > "$DEL_OUT/pro-to-all-CANARY-2026-08-17.md"
  OUT=$(LINT_OUTBOX="$DEL_OUT" LINT_SIBLING_TREES="$DEL_TREE" check_delivery)
  echo "$OUT" | grep -q "FAIL \[C9\]" && echo "OK C9 can fail (letter in no sibling inbound)" || { echo "SELFTEST BROKEN: C9 cannot fail"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK"; exit 3; }
  echo "$OUT" | grep -q "ABSENT" || { echo "SELFTEST BROKEN: C9 failed without naming the tree"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK"; exit 3; }
  cp "$DEL_OUT/pro-to-all-CANARY-2026-08-17.md" "$DEL_TREE/exchange/inbound/"
  OUT=$(LINT_OUTBOX="$DEL_OUT" LINT_SIBLING_TREES="$DEL_TREE" check_delivery)
  echo "$OUT" | grep -q "PASS \[C9\]" || { echo "SELFTEST BROKEN: C9 cannot pass on a delivered letter"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK"; exit 3; }
  OUT=$(LINT_OUTBOX="$DEL_OUT" LINT_SIBLING_TREES="$DEL_DARK" check_delivery)
  echo "$OUT" | grep -q "UNREACHABLE" || { echo "SELFTEST BROKEN: C9 read a tree with no inbound as clean"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK"; exit 3; }
  echo "$OUT" | grep -q "FAIL \[C9\]" || { echo "SELFTEST BROKEN: C9 passed while a tree was unreachable"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK"; exit 3; }
  echo "OK C9 treats an unreachable tree as missing, not as clean"
  rm -f "$DEL_OUT"/*.md; printf 'body\n' > "$DEL_OUT/pro-to-all-OLD-2026-08-09.md"
  OUT=$(LINT_OUTBOX="$DEL_OUT" LINT_SIBLING_TREES="$DEL_TREE" check_delivery)
  echo "$OUT" | grep -q "PRE-EPOCH 1 letter" || { echo "SELFTEST BROKEN: C9 dropped a pre-epoch letter silently"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK"; exit 3; }
  echo "OK C9 exempts pre-epoch letters and counts them out loud"
  # cases e/f, added 2026-08-23 with the addressee parser. The parser can only NARROW a grade, so
  # it needs both halves proven: a non-addressee tree must be skipped, and the addressee's own tree
  # must still fail. A narrowing rule that cannot fail is an exemption wearing a gate's name.
  rm -f "$DEL_OUT"/*.md
  DEL_ADDR=$(mktemp -d)
  mkdir -p "$DEL_ADDR/claude-foundational-layer/exchange/inbound" "$DEL_ADDR/Claude Personal/exchange/inbound"
  printf 'body\n' > "$DEL_OUT/pro-to-cfl-CANARY-2026-08-17.md"
  cp "$DEL_OUT/pro-to-cfl-CANARY-2026-08-17.md" "$DEL_ADDR/claude-foundational-layer/exchange/inbound/"
  OUT=$(LINT_OUTBOX="$DEL_OUT" LINT_SIBLING_TREES="$DEL_ADDR/claude-foundational-layer|$DEL_ADDR/Claude Personal" check_delivery)
  echo "$OUT" | grep -q "PASS \[C9\]" || { echo "SELFTEST BROKEN: C9 graded a cfl-addressed letter against a tree it was never sent to"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK" "$DEL_ADDR"; exit 3; }
  echo "OK C9 grades a letter only against the trees its filename addresses"
  rm -f "$DEL_ADDR/claude-foundational-layer/exchange/inbound/"*.md
  OUT=$(LINT_OUTBOX="$DEL_OUT" LINT_SIBLING_TREES="$DEL_ADDR/claude-foundational-layer|$DEL_ADDR/Claude Personal" check_delivery)
  echo "$OUT" | grep -q "FAIL \[C9\]" || { echo "SELFTEST BROKEN: C9 cannot fail on the addressee's own tree"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK" "$DEL_ADDR"; exit 3; }
  echo "OK C9 still fails when the addressee's own inbound is the one missing it"
  # cases g/h/i, added 2026-08-30 with the PER-TREE graded-from. Both halves again, because a
  # per-tree exemption that cannot fail is an excuse wearing a gate's name. The fixture is
  # Antigravity's real shape: a trunk whose inbound did not exist when the letter was written.
  printf 'body
' > "$DEL_OUT/pro-to-cfl-LATE-2026-08-20.md"
  cp "$DEL_OUT/pro-to-cfl-LATE-2026-08-20.md" "$DEL_ADDR/claude-foundational-layer/exchange/inbound/" 2>/dev/null
  rm -f "$DEL_OUT/pro-to-cfl-CANARY-2026-08-17.md"
  OUT=$(LINT_OUTBOX="$DEL_OUT" LINT_SIBLING_TREES="$DEL_ADDR/claude-foundational-layer" LINT_SIBLING_FROM="2026-08-25" check_delivery)
  echo "$OUT" | grep -q "PASS \[C9\]" || { echo "SELFTEST BROKEN: C9 graded a letter against a tree whose graded-from is LATER than the letter -- a trunk that did not exist cannot have received it"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK" "$DEL_ADDR"; exit 3; }
  echo "OK C9 does not grade a letter older than a tree's own graded-from"
  rm -f "$DEL_ADDR/claude-foundational-layer/exchange/inbound/"*.md
  OUT=$(LINT_OUTBOX="$DEL_OUT" LINT_SIBLING_TREES="$DEL_ADDR/claude-foundational-layer" LINT_SIBLING_FROM="2026-08-18" check_delivery)
  echo "$OUT" | grep -q "FAIL \[C9\]" || { echo "SELFTEST BROKEN: the per-tree graded-from exempted a letter it should have graded -- an exemption that cannot fail"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK" "$DEL_ADDR"; exit 3; }
  echo "OK C9 still grades a letter dated on or after that tree's graded-from (the exemption can fail)"
  OUT=$(LINT_OUTBOX="$DEL_OUT" LINT_ROSTER="/nonexistent/roster.tsv" check_delivery)
  echo "$OUT" | grep -q "FAIL \[C9\]" || { echo "SELFTEST BROKEN: C9 passed with zero trees resolved -- an empty delivery population is UNKNOWN, never clean"; rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK" "$DEL_ADDR"; exit 3; }
  echo "OK C9 treats zero resolved trees as UNKNOWN, not clean"
  rm -rf "$DEL_OUT" "$DEL_TREE" "$DEL_DARK" "$DEL_ADDR"
  # --- C12 cases. BOTH DIRECTIONS, because a one-directional fixture cannot show its
  # guard discriminates -- the Secretary's own SEC-166 correction, adopted here.
  CITE_DIR=$(mktemp -d)
  printf '| row | Jon, 2026-08-07 `[verbatim]`: "some words he said" |\n' > "$CITE_DIR/bad.md"
  OUT=$(FAILS=0; LINT_CITE_ROOT="$CITE_DIR" check_table_cites)
  echo "$OUT" | grep -q "FAIL \[C12\]" && echo "OK C12 can fail (graded table row, no cite)" || { echo "SELFTEST BROKEN: C12 cannot fail"; rm -rf "$CITE_DIR"; exit 3; }
  echo "$OUT" | grep -q "UNCITED GRADE" || { echo "SELFTEST BROKEN: C12 failed without naming the row"; rm -rf "$CITE_DIR"; exit 3; }
  printf '| row | Jon `[verbatim]`, `history.jsonl:1759`: "some words" |\n' > "$CITE_DIR/bad.md"
  OUT=$(FAILS=0; LINT_CITE_ROOT="$CITE_DIR" check_table_cites)
  echo "$OUT" | grep -q "PASS \[C12\]" || { echo "SELFTEST BROKEN: C12 cannot pass on a cited row"; rm -rf "$CITE_DIR"; exit 3; }
  echo "OK C12 passes when the same row carries a cite"
  # a section cite is a cite: the ASOP rows in this tree are cited as §2.5 and nothing else
  printf '| row | ASOP No. 1 `[verbatim]` §2.5: "known means actual knowledge" |\n' > "$CITE_DIR/bad.md"
  OUT=$(FAILS=0; LINT_CITE_ROOT="$CITE_DIR" check_table_cites)
  echo "$OUT" | grep -q "PASS \[C12\]" || { echo "SELFTEST BROKEN: C12 rejects a section cite"; rm -rf "$CITE_DIR"; exit 3; }
  echo "OK C12 accepts a section cite"
  # peer-authored captures are OUT OF POPULATION -- grading another seat's letter as our
  # own defect is the sender-authored-delivery error in a new place.
  mkdir -p "$CITE_DIR/exchange/inbound"
  printf '| row | Jon `[verbatim]`: "words with no cite" |\n' > "$CITE_DIR/exchange/inbound/peer.md"
  printf 'clean\n' > "$CITE_DIR/bad.md"
  OUT=$(FAILS=0; LINT_CITE_ROOT="$CITE_DIR" check_table_cites)
  echo "$OUT" | grep -q "PASS \[C12\]" || { echo "SELFTEST BROKEN: C12 graded a peer capture as our defect"; rm -rf "$CITE_DIR"; exit 3; }
  echo "OK C12 excludes exchange/inbound as peer-authored captures"
  # A SCAN THAT COULD NOT RUN IS NOT A CLEAN SCAN. An unreadable root makes grep exit 2,
  # and before 2026-08-24 20:3x that was indistinguishable from "no graded rows here".
  OUT=$(FAILS=0; LINT_CITE_ROOT="$CITE_DIR/does-not-exist" check_table_cites)
  echo "$OUT" | grep -q "FAIL \[C12\]" || { echo "SELFTEST BROKEN: C12 reported clean on a scan that could not run"; rm -rf "$CITE_DIR"; exit 3; }
  echo "$OUT" | grep -q "could not run" || { echo "SELFTEST BROKEN: C12 failed without saying the scan could not run"; rm -rf "$CITE_DIR"; exit 3; }
  echo "OK C12 treats an unrunnable scan as UNKNOWN, not clean"
  rm -rf "$CITE_DIR"
  # --- C13 cases. BOTH DIRECTIONS on a synthetic lint file, so the fixture cannot be
  # satisfied by this file happening to be correct today.
  WIRE=$(mktemp)
  printf 'check_a() {\n  :\n}\ncheck_b() {\n  :\n}\nrun_all() { check_a; }\n' > "$WIRE"
  OUT=$(FAILS=0; LINT_SELF="$WIRE" check_wired)
  echo "$OUT" | grep -q "FAIL \[C13\]" && echo "OK C13 can fail (check defined, never called)" || { echo "SELFTEST BROKEN: C13 cannot fail"; rm -f "$WIRE"; exit 3; }
  echo "$OUT" | grep -q "PRESENT-AND-UNCALLED check_b" || { echo "SELFTEST BROKEN: C13 failed without naming the uncalled check"; rm -f "$WIRE"; exit 3; }
  printf 'check_a() {\n  :\n}\ncheck_b() {\n  :\n}\nrun_all() { check_a; check_b; }\n' > "$WIRE"
  OUT=$(FAILS=0; LINT_SELF="$WIRE" check_wired)
  echo "$OUT" | grep -q "PASS \[C13\]" || { echo "SELFTEST BROKEN: C13 cannot pass on a fully wired file"; rm -f "$WIRE"; exit 3; }
  echo "OK C13 passes when every defined check is wired"
  # UNREADABLE IS NOT A PASS: a wiring check that cannot read the file must not report clean.
  OUT=$(FAILS=0; LINT_SELF="$WIRE.nope" check_wired)
  echo "$OUT" | grep -q "FAIL \[C13\]" || { echo "SELFTEST BROKEN: C13 passed on an unreadable source"; rm -f "$WIRE"; exit 3; }
  echo "OK C13 treats an unreadable source as UNKNOWN, not clean"
  # AN EMPTY POPULATION IS NOT CLEAN: a source with no checks at all, or a grep that
  # never spawned, must not report green. [m] C13 PASSED this until 20:3x.
  printf '# no checks here\nrun_all() { :; }\n' > "$WIRE"
  OUT=$(FAILS=0; LINT_SELF="$WIRE" check_wired)
  echo "$OUT" | grep -q "FAIL \[C13\]" || { echo "SELFTEST BROKEN: C13 passed on a source with ZERO checks"; rm -f "$WIRE"; exit 3; }
  echo "$OUT" | grep -q "ZERO check definitions" || { echo "SELFTEST BROKEN: C13 failed without naming the empty population"; rm -f "$WIRE"; exit 3; }
  echo "OK C13 treats an empty population as UNKNOWN, not clean"
  rm -f "$WIRE"
  # C13 IS ITSELF A check_* FUNCTION, so it must appear in its own run_all or it fails
  # itself. Asserted rather than left as a happy accident.
  sed -n '/^run_all() {/,/^}/p' scripts/lint.sh | grep -q 'check_wired' || { echo "SELFTEST BROKEN: C13 is not wired into its own run_all"; exit 3; }
  echo "OK C13 is wired into its own run_all"
  # --- C14 controls: a roster check that has never failed is an assertion, not a gate.
  RST="$(mktemp -d)"; mkdir -p "$RST/root/Alpha" "$RST/root/Beta"
  printf 'Alpha	DELIVER	fixture
' > "$RST/roster.tsv"
  OUT=$(FAILS=0; LINT_ROSTER="$RST/roster.tsv" LINT_TRUNK_ROOT="$RST/root" check_roster)
  echo "$OUT" | grep -q "FAIL \[C14\]" || { echo "SELFTEST BROKEN: C14 passed with an unrostered directory"; rm -rf "$RST"; exit 3; }
  echo "$OUT" | grep -q "UNROSTERED Beta" || { echo "SELFTEST BROKEN: C14 failed without naming the unrostered trunk"; rm -rf "$RST"; exit 3; }
  echo "OK C14 fails on a directory with no roster row, and names it"
  OUT=$(FAILS=0; LINT_ROSTER="$RST/absent.tsv" LINT_TRUNK_ROOT="$RST/root" check_roster)
  echo "$OUT" | grep -q "FAIL \[C14\]" || { echo "SELFTEST BROKEN: C14 passed with no roster file"; rm -rf "$RST"; exit 3; }
  echo "OK C14 treats a missing roster as UNKNOWN, not clean"
  OUT=$(FAILS=0; LINT_ROSTER="$RST/roster.tsv" LINT_TRUNK_ROOT="$RST/no-such-root" check_roster)
  echo "$OUT" | grep -q "FAIL \[C14\]" || { echo "SELFTEST BROKEN: C14 passed with an unreadable trunk root"; rm -rf "$RST"; exit 3; }
  echo "OK C14 treats an unreadable trunk root as UNKNOWN, not clean"
  printf 'Beta	NOT-A-TRUNK	fixture
' >> "$RST/roster.tsv"
  OUT=$(FAILS=0; LINT_ROSTER="$RST/roster.tsv" LINT_TRUNK_ROOT="$RST/root" check_roster)
  echo "$OUT" | grep -q "PASS \[C14\]" || { echo "SELFTEST BROKEN: C14 did not pass on a complete roster -- a check that cannot pass is not a gate"; rm -rf "$RST"; exit 3; }
  echo "OK C14 passes once every directory is dispositioned (positive control)"
  rm -rf "$RST"
  # --- C15 controls. ⛔ THE FIRST FIXTURE IS THIS TRUNK'S OWN 2026-08-28 ERROR, reproduced:
  # a roster row that says DELIVER pointed at a mailbox that had posted a do-not-deposit notice.
  # C14 passed on that roster. A check that certifies a row's EXISTENCE must not be mistaken for
  # one that certifies its TRUTH, and only a failing fixture proves the difference.
  DLV="$(mktemp -d)"; mkdir -p "$DLV/root/Live/exchange/inbound" "$DLV/root/Dead/exchange/inbound" "$DLV/root/Gone"
  printf 'a letter
' > "$DLV/root/Live/exchange/inbound/somebody-elses.md"
  printf 'a letter
' > "$DLV/root/Dead/exchange/inbound/somebody-elses.md"
  printf 'Live	DELIVER	fixture
' > "$DLV/roster.tsv"
  OUT=$(FAILS=0; LINT_ROSTER="$DLV/roster.tsv" LINT_TRUNK_ROOT="$DLV/root" check_deliverable)
  echo "$OUT" | grep -q "PASS \[C15\]" || { echo "SELFTEST BROKEN: C15 did not pass on a live destination -- a check that cannot pass is not a gate"; rm -rf "$DLV"; exit 3; }
  echo "OK C15 passes on a DELIVER row whose destination is live (positive control)"
  printf 'Dead	DELIVER	fixture
' >> "$DLV/roster.tsv"
  printf 'x
' > "$DLV/root/Dead/exchange/inbound/00-DEAD-ADDRESS-DO-NOT-DEPOSIT-HERE.md"
  OUT=$(FAILS=0; LINT_ROSTER="$DLV/roster.tsv" LINT_TRUNK_ROOT="$DLV/root" check_deliverable)
  echo "$OUT" | grep -q "FAIL \[C15\]" || { echo "SELFTEST BROKEN: C15 passed on a DELIVER row with a do-not-deposit marker -- THE 08-28 DEFECT ITSELF"; rm -rf "$DLV"; exit 3; }
  echo "$OUT" | grep -q "DEAD-ADDRESS Dead" || { echo "SELFTEST BROKEN: C15 failed without naming the dead address"; rm -rf "$DLV"; exit 3; }
  echo "OK C15 fails on a DELIVER row whose destination posted a do-not-deposit notice (the 08-28 fixture)"
  # A marker can be DECLARED rather than NAMED. A detector that only greps filenames passes
  # forever on a correctly-marked archive that happens to be called something else.
  rm -f "$DLV/root/Dead/exchange/inbound/00-DEAD-ADDRESS-DO-NOT-DEPOSIT-HERE.md"
  printf -- '---
kind: archive-marker
---
' > "$DLV/root/Dead/exchange/inbound/README.md"
  OUT=$(FAILS=0; LINT_ROSTER="$DLV/roster.tsv" LINT_TRUNK_ROOT="$DLV/root" check_deliverable)
  echo "$OUT" | grep -q "FAIL \[C15\]" || { echo "SELFTEST BROKEN: C15 missed a DECLARED archive marker (kind: archive-marker)"; rm -rf "$DLV"; exit 3; }
  echo "OK C15 fails on a declared archive-marker, not only a named one"
  printf 'Gone	DELIVER	fixture
' > "$DLV/roster.tsv"
  OUT=$(FAILS=0; LINT_ROSTER="$DLV/roster.tsv" LINT_TRUNK_ROOT="$DLV/root" check_deliverable)
  echo "$OUT" | grep -q "UNDELIVERABLE Gone" || { echo "SELFTEST BROKEN: C15 passed on a DELIVER row with no inbound directory at all"; rm -rf "$DLV"; exit 3; }
  echo "OK C15 fails on a DELIVER row whose destination has no inbound at all"
  # AN EMPTY COURIER LIST IS NOT A CLEAN ONE (C13's lesson, third application).
  printf '# comments only
' > "$DLV/roster.tsv"
  OUT=$(FAILS=0; LINT_ROSTER="$DLV/roster.tsv" LINT_TRUNK_ROOT="$DLV/root" check_deliverable)
  echo "$OUT" | grep -q "ZERO DELIVER rows" || { echo "SELFTEST BROKEN: C15 treated an empty courier list as clean"; rm -rf "$DLV"; exit 3; }
  echo "OK C15 treats a roster with zero DELIVER rows as UNKNOWN, not clean"
  rm -rf "$DLV"
  # --- C16 cases. FOUR, because the check has three verdicts and an epoch boundary, and each has
  # to be constructed. The accusing-with-no-declaration case is the one that matters: it is the
  # second ideal's stated breach, and before this fixture existed nothing could fire on it.
  SC_BOX=$(mktemp -d)
  # case a: post-epoch letter names a peer beside a defect word, no self-check field -> FAIL
  printf -- '---\ntitle: finding\n---\nCFL letter is missing its receipt.\n' > "$SC_BOX/pro-to-cfl-x-2999-01-01.md"
  OUT=$(LINT_OUTBOX="$SC_BOX" check_self_application)
  echo "$OUT" | grep -q "FAIL \[C16\]" && echo "OK C16 can fail (accusation with no self-check)" || { echo "SELFTEST BROKEN: C16 cannot fail"; rm -rf "$SC_BOX"; exit 3; }
  echo "$OUT" | grep -q "NO SELF-CHECK pro-to-cfl-x-2999-01-01.md" || { echo "SELFTEST BROKEN: C16 failed without naming the letter"; rm -rf "$SC_BOX"; exit 3; }
  # case b: same letter WITH a self-check declaration -> PASS. A check that cannot pass is a wall.
  printf -- '---\ntitle: finding\nself-check: ran C9 on our own outbox first; 0 absent here\n---\nCFL letter is missing its receipt.\n' > "$SC_BOX/pro-to-cfl-x-2999-01-01.md"
  OUT=$(LINT_OUTBOX="$SC_BOX" check_self_application)
  echo "$OUT" | grep -q "PASS \[C16\]" || { echo "SELFTEST BROKEN: C16 cannot pass on a declared self-check"; rm -rf "$SC_BOX"; exit 3; }
  echo "OK C16 passes on a declared self-check"
  # case c: an EMPTY declaration must not buy a pass -- a field present and blank is the cheapest
  # way to launder this check, so it is constructed explicitly rather than assumed.
  printf -- '---\ntitle: finding\nself-check:\n---\nCFL letter is missing its receipt.\n' > "$SC_BOX/pro-to-cfl-x-2999-01-01.md"
  OUT=$(LINT_OUTBOX="$SC_BOX" check_self_application)
  echo "$OUT" | grep -q "FAIL \[C16\]" || { echo "SELFTEST BROKEN: C16 accepts an empty self-check field"; rm -rf "$SC_BOX"; exit 3; }
  echo "OK C16 rejects an empty declaration"
  # case d: a PRE-epoch letter is NOT graded -- the rule binds new writing, and a check that
  # retroactively condemned the record would invite the sweep the fleet has ruled out.
  # ⛔ REWRITTEN 2026-08-29. The old fixture dated the letter IN ITS FILENAME, which is exactly the
  # break the Secretary found: the epoch was derived from a string the author controls. The date is
  # now the git ADD-date, so this fixture must build a real repo and backdate a real commit --
  # and MY OWN CHANGE BROKE THIS FIXTURE, which the real run could not have told me.
  rm -f "$SC_BOX"/*.md
  ( cd "$SC_BOX" && git init -q . && git config user.email s@t && git config user.name s ) >/dev/null 2>&1
  printf -- '---\ntitle: finding\n---\nCFL letter is missing its receipt.\n' > "$SC_BOX/pro-to-cfl-old.md"
  ( cd "$SC_BOX" && git add -A && GIT_AUTHOR_DATE='2026-08-24T12:00:00' GIT_COMMITTER_DATE='2026-08-24T12:00:00' git commit -qm old ) >/dev/null 2>&1
  OUT=$(cd "$SC_BOX" && LINT_OUTBOX="." check_self_application)
  echo "$OUT" | grep -q "PASS \[C16\]" || { echo "SELFTEST BROKEN: C16 graded a letter git-added before the epoch"; rm -rf "$SC_BOX"; exit 3; }
  echo "$OUT" | grep -q "1 pre-epoch" || { echo "SELFTEST BROKEN: C16 skipped a letter without printing the skip count"; rm -rf "$SC_BOX"; exit 3; }
  echo "OK C16 leaves letters git-added pre-epoch ungraded and prints the count"
  # ⛔ case d2: THE SECRETARY'S BREAK 1, AS A REGRESSION TEST. A letter whose FILENAME says
  # 2026-08-29 (pre-epoch) but which entered git AFTER the epoch must be GRADED. Before the fix this
  # passed on the filename alone: one character between a recorded breach and a green light.
  printf -- '---\ntitle: finding\n---\nCFL letter is missing its receipt.\n' > "$SC_BOX/pro-to-cfl-x-2026-08-29.md"
  ( cd "$SC_BOX" && git add -A && GIT_AUTHOR_DATE='2026-09-02T12:00:00' GIT_COMMITTER_DATE='2026-09-02T12:00:00' git commit -qm new ) >/dev/null 2>&1
  OUT=$(cd "$SC_BOX" && LINT_OUTBOX="." check_self_application)
  echo "$OUT" | grep -q "FAIL \[C16\]" || { echo "SELFTEST BROKEN: C16 skipped a post-epoch letter on the strength of its FILENAME -- the Secretary's break 1 has regressed"; rm -rf "$SC_BOX"; exit 3; }
  echo "OK C16 grades on the git add-date, not the author-controlled filename (Secretary break 1)"
  # ⛔ case d3: THE SECRETARY'S BREAK 2. A zero denominator must NOT print "second ideal wired" --
  # a vacuous truth rendered as compliance would read as proof on exactly the first day it misleads.
  SC_EMPTY=$(mktemp -d)
  OUT=$(LINT_OUTBOX="$SC_EMPTY" check_self_application)
  echo "$OUT" | grep -q "VACUOUS" || { echo "SELFTEST BROKEN: C16 reported a zero-denominator run as a normal pass -- the Secretary's break 2 has regressed"; rm -rf "$SC_BOX" "$SC_EMPTY"; exit 3; }
  echo "$OUT" | grep -q "second ideal wired" && { echo "SELFTEST BROKEN: C16 claimed the second ideal is wired while grading nothing"; rm -rf "$SC_BOX" "$SC_EMPTY"; exit 3; }
  echo "OK C16 reports a zero denominator as VACUOUS, never as wired (Secretary break 2)"
  rm -rf "$SC_EMPTY"
  # case e: outbox absent -> FAIL. Unreadable must never read as clean.
  OUT=$(LINT_OUTBOX="/nonexistent/outbox" check_self_application)
  echo "$OUT" | grep -q "FAIL \[C16\]" || { echo "SELFTEST BROKEN: C16 passes when it cannot read the outbox"; rm -rf "$SC_BOX"; exit 3; }
  echo "OK C16 fails on an unreadable outbox"
  rm -rf "$SC_BOX"
  # --- C17 controls. ⛔ THE FIRST FIXTURE IS THIS TRUNK'S OWN 2026-08-29 DEFECT, REPLAYED: at that
  # close HEAD was dated 2026-08-29 and the beacon still read 2026-08-28. Proven against the failure
  # that produced it, not against a fixture invented afterwards.
  BC=$(mktemp -d)
  printf 'last_seen: 2026-08-28 16:5x CDT\n' > "$BC/b.md"
  OUT=$(LINT_LASTSEEN="$BC/b.md" LINT_TODAY=2026-08-29 LINT_TREE_DATE=2026-08-29 check_beacon_freshness)
  echo "$OUT" | grep -q "FAIL \[C17\]" || { echo "SELFTEST BROKEN: C17 passed the 2026-08-29 stale-beacon state -- the defect it exists for"; rm -rf "$BC"; exit 3; }
  echo "OK C17 fails on the replayed 08-29 stale beacon (the defect itself)"
  printf 'last_seen: 2026-08-30 00:0x CDT\n' > "$BC/b.md"
  OUT=$(LINT_LASTSEEN="$BC/b.md" LINT_TODAY=2026-08-30 LINT_TREE_DATE=2026-08-30 check_beacon_freshness)
  echo "$OUT" | grep -q "PASS \[C17\]" || { echo "SELFTEST BROKEN: C17 cannot pass on a fresh beacon -- a check that cannot pass is a wall"; rm -rf "$BC"; exit 3; }
  echo "OK C17 passes when the beacon is not older than the newest commit (positive control)"
  OUT=$(LINT_LASTSEEN="$BC/nope.md" LINT_TODAY=2026-08-30 LINT_TREE_DATE=2026-08-30 check_beacon_freshness)
  echo "$OUT" | grep -q "FAIL \[C17\]" || { echo "SELFTEST BROKEN: C17 treats an absent beacon as clean"; rm -rf "$BC"; exit 3; }
  echo "OK C17 fails when the beacon is absent (UNKNOWN dominates a PASS)"
  printf 'last_seen: soon\n' > "$BC/b.md"
  OUT=$(LINT_LASTSEEN="$BC/b.md" LINT_TODAY=2026-08-30 LINT_TREE_DATE=2026-08-30 check_beacon_freshness)
  echo "$OUT" | grep -q "FAIL \[C17\]" || { echo "SELFTEST BROKEN: C17 accepts an unparseable last_seen"; rm -rf "$BC"; exit 3; }
  echo "OK C17 fails on an unparseable last_seen (fail-closed)"
  # ⛔ THE AUTHOR'S OWN ERROR, AS A FIXTURE: a beacon stamped in the future silences the check
  # forever and the silence looks like health. This one was live in this tree for eleven minutes.
  printf 'last_seen: 2026-08-30 00:0x CDT
' > "$BC/b.md"
  OUT=$(LINT_LASTSEEN="$BC/b.md" LINT_TODAY=2026-08-29 LINT_TREE_DATE=2026-08-29 check_beacon_freshness)
  echo "$OUT" | grep -q "FAIL \[C17\]" || { echo "SELFTEST BROKEN: C17 accepts a FUTURE-dated beacon -- the author's own 08-29 error"; rm -rf "$BC"; exit 3; }
  echo "OK C17 fails on a future-dated beacon (the author's own error, fixtured)"
  rm -rf "$BC"
  # --- C18 controls. SIX, because the check has a fail verdict, a pass verdict, an epoch boundary,
  # a fail-closed undated case, and two UNKNOWN-dominates-PASS cases. ⛔ The first fixture is the
  # real defect: a letter that exists ONLY in the receiver's tree, which no check of ours can read.
  RD=$(mktemp -d)
  mkdir -p "$RD/box" "$RD/root/Peer/exchange/inbound"
  printf 'Peer\tDELIVER\tfixture\n' > "$RD/roster.tsv"
  : > "$RD/root/Peer/exchange/inbound/pro-to-peer-a-finding-2026-09-01.md"
  OUT=$(LINT_OUTBOX="$RD/box" LINT_ROSTER="$RD/roster.tsv" LINT_TRUNK_ROOT="$RD/root" check_reverse_delivery)
  echo "$OUT" | grep -q "FAIL \[C18\]" || { echo "SELFTEST BROKEN: C18 passed a letter that exists only in the receiver's tree"; rm -rf "$RD"; exit 3; }
  echo "$OUT" | grep -q "UNGRADED DELIVERY pro-to-peer-a-finding-2026-09-01.md" || { echo "SELFTEST BROKEN: C18 failed without naming the ungraded delivery"; rm -rf "$RD"; exit 3; }
  echo "OK C18 fails on a letter delivered but absent from the graded population"
  # positive control: the same letter twinned in the outbox -> PASS. A check that cannot pass is a wall.
  : > "$RD/box/pro-to-peer-a-finding-2026-09-01.md"
  OUT=$(LINT_OUTBOX="$RD/box" LINT_ROSTER="$RD/roster.tsv" LINT_TRUNK_ROOT="$RD/root" check_reverse_delivery)
  echo "$OUT" | grep -q "PASS \[C18\]" || { echo "SELFTEST BROKEN: C18 cannot pass on a correctly twinned letter"; rm -rf "$RD"; exit 3; }
  echo "OK C18 passes when the delivered letter is twinned in the outbox (positive control)"
  # epoch boundary: a PRE-epoch orphan is BACKLOG, counted and printed, never swept and never a fail.
  rm -f "$RD/box"/*.md
  rm -f "$RD/root/Peer/exchange/inbound"/*.md
  : > "$RD/root/Peer/exchange/inbound/pro-to-peer-old-2026-08-24.md"
  OUT=$(LINT_OUTBOX="$RD/box" LINT_ROSTER="$RD/roster.tsv" LINT_TRUNK_ROOT="$RD/root" check_reverse_delivery)
  echo "$OUT" | grep -q "PASS \[C18\]" || { echo "SELFTEST BROKEN: C18 condemned a pre-epoch orphan instead of carrying it as backlog"; rm -rf "$RD"; exit 3; }
  echo "$OUT" | grep -q "1 pre-epoch BACKLOG" || { echo "SELFTEST BROKEN: C18 carried a backlog item without printing the count"; rm -rf "$RD"; exit 3; }
  echo "OK C18 carries pre-epoch orphans as a printed backlog, not a sweep and not a failure"
  # ⛔ fail-closed: an UNDATED orphan must grade as NEW. The epoch is read from a filename, so the
  # one thing it must never do is let a missing date buy silence.
  : > "$RD/root/Peer/exchange/inbound/pro-to-peer-undated.md"
  OUT=$(LINT_OUTBOX="$RD/box" LINT_ROSTER="$RD/roster.tsv" LINT_TRUNK_ROOT="$RD/root" check_reverse_delivery)
  echo "$OUT" | grep -q "FAIL \[C18\]" || { echo "SELFTEST BROKEN: C18 let an undated orphan fall into the backlog -- not fail-closed"; rm -rf "$RD"; exit 3; }
  echo "OK C18 grades an undated orphan as new (fail-closed on the author-controlled date)"
  # UNKNOWN dominates a PASS, twice.
  printf '# comments only\n' > "$RD/roster.tsv"
  OUT=$(LINT_OUTBOX="$RD/box" LINT_ROSTER="$RD/roster.tsv" LINT_TRUNK_ROOT="$RD/root" check_reverse_delivery)
  echo "$OUT" | grep -q "FAIL \[C18\]" || { echo "SELFTEST BROKEN: C18 treated zero DELIVER trees as clean"; rm -rf "$RD"; exit 3; }
  echo "OK C18 treats zero resolved trees as UNKNOWN, not clean"
  OUT=$(LINT_OUTBOX="$RD/box" LINT_ROSTER="$RD/nope.tsv" LINT_TRUNK_ROOT="$RD/root" check_reverse_delivery)
  echo "$OUT" | grep -q "FAIL \[C18\]" || { echo "SELFTEST BROKEN: C18 passed with no roster to read"; rm -rf "$RD"; exit 3; }
  echo "OK C18 fails when the roster is unreadable"
  rm -rf "$RD"
  # --- C19 controls. SEVEN. ⛔ The first two are the two states this trunk was ACTUALLY in: an
  # ideal called sworn whose check did not exist (2026-08-29 all day), and one called wired before
  # any seat that did not build it had attacked it (2026-08-29 23:2x).
  OR=$(mktemp -d)
  printf 'check_real() {\n  pass C97 "ok"\n}\ncheck_orphan() {\n  pass C98 "ok"\n}\nrun_all() { check_real; }\n' > "$OR/self.sh"
  HDR='| # | ideal | status | breach | check | falsifier |'
  printf '%s\n' "$HDR" > "$OR/reg.md"
  printf '| 1 | an ideal | SWORN | observable | C97 | Peer 2026-08-30 returned two attacks |\n' >> "$OR/reg.md"
  OUT=$(LINT_OATH_REGISTER="$OR/reg.md" LINT_SELF="$OR/self.sh" check_oath_register)
  echo "$OUT" | grep -q "PASS \[C19\]" || { echo "SELFTEST BROKEN: C19 cannot pass a properly sworn ideal -- a check that cannot pass is a wall"; rm -rf "$OR"; exit 3; }
  echo "OK C19 passes an ideal whose check exists, is wired, and has a falsifier (positive control)"
  printf '%s\n' "$HDR" > "$OR/reg.md"
  printf '| 1 | an ideal | SWORN | observable |  | Peer 2026-08-30 returned two attacks |\n' >> "$OR/reg.md"
  OUT=$(LINT_OATH_REGISTER="$OR/reg.md" LINT_SELF="$OR/self.sh" check_oath_register)
  echo "$OUT" | grep -q "SWORN WITH NO CHECK" || { echo "SELFTEST BROKEN: C19 allowed an ideal sworn with no check named -- THE 08-29 STATE"; rm -rf "$OR"; exit 3; }
  echo "OK C19 fails an ideal sworn with no check named (the 08-29 state, replayed)"
  printf '%s\n' "$HDR" > "$OR/reg.md"
  printf '| 1 | an ideal | SWORN | observable | C99 | Peer 2026-08-30 returned two attacks |\n' >> "$OR/reg.md"
  OUT=$(LINT_OATH_REGISTER="$OR/reg.md" LINT_SELF="$OR/self.sh" check_oath_register)
  echo "$OUT" | grep -q "DOES NOT EXIST" || { echo "SELFTEST BROKEN: C19 accepted a check id that emits no pass/fail anywhere"; rm -rf "$OR"; exit 3; }
  echo "OK C19 fails an ideal naming a check that does not exist"
  printf '%s\n' "$HDR" > "$OR/reg.md"
  printf '| 1 | an ideal | SWORN | observable | C98 | Peer 2026-08-30 returned two attacks |\n' >> "$OR/reg.md"
  OUT=$(LINT_OATH_REGISTER="$OR/reg.md" LINT_SELF="$OR/self.sh" check_oath_register)
  echo "$OUT" | grep -q "UNWIRED" || { echo "SELFTEST BROKEN: C19 accepted a check that is DEFINED but never called in run_all -- the exact distinction condition 3 exists for"; rm -rf "$OR"; exit 3; }
  echo "OK C19 fails an ideal sworn on a defined-but-unwired check"
  printf '%s\n' "$HDR" > "$OR/reg.md"
  printf '| 1 | an ideal | SWORN | observable | C97 | - |\n' >> "$OR/reg.md"
  OUT=$(LINT_OATH_REGISTER="$OR/reg.md" LINT_SELF="$OR/self.sh" check_oath_register)
  echo "$OUT" | grep -q "NO FALSIFIER" || { echo "SELFTEST BROKEN: C19 let an ideal be sworn with no falsifier -- ratification-by-default is the failure this condition exists for"; rm -rf "$OR"; exit 3; }
  echo "OK C19 fails an ideal sworn with no falsifier returned"
  # ⚠️ HELD must NOT be graded. A gate that punished the honest state would be answered by swearing
  # everything, which is the opposite of what it is for.
  printf '%s\n' "$HDR" > "$OR/reg.md"
  printf '| 1 | an ideal | HELD | not yet observable |  |  |\n' >> "$OR/reg.md"
  OUT=$(LINT_OATH_REGISTER="$OR/reg.md" LINT_SELF="$OR/self.sh" check_oath_register)
  echo "$OUT" | grep -q "PASS \[C19\]" || { echo "SELFTEST BROKEN: C19 graded a HELD row -- HELD is the honest state and must not be punished"; rm -rf "$OR"; exit 3; }
  echo "OK C19 leaves HELD and UNSETTLED rows ungraded"
  OUT=$(LINT_OATH_REGISTER="$OR/nope.md" LINT_SELF="$OR/self.sh" check_oath_register)
  echo "$OUT" | grep -q "FAIL \[C19\]" || { echo "SELFTEST BROKEN: C19 passed with no register to read"; rm -rf "$OR"; exit 3; }
  echo "OK C19 fails when the register is unreadable (UNKNOWN dominates a PASS)"
  rm -rf "$OR"
  # --- C20 controls. FIVE. ⛔ The second is THE LIVE DEFECT this check found on Jon's own surface:
  # a decorative star in the number cell made row 8 invisible to the counter that speaks at wake
  # time, so it reported "7 items await your word" while eight were open -- and the hidden row was
  # one of Jon's OWN questions. Replayed here so it can never return silently.
  JS=$(mktemp -d)
  HDRA='## A — rows awaiting Jon-s word'
  printf '%s\n| **1** | [status:OPEN] **asked-by:** Professional, 2026-08-30 — why him | default |\n' "$HDRA" > "$JS/idx.md"
  OUT=$(LINT_JON_INDEX="$JS/idx.md" check_jon_surface)
  echo "$OUT" | grep -q "PASS \[C20\]" || { echo "SELFTEST BROKEN: C20 cannot pass a well-formed surface -- a check that cannot pass is a wall"; rm -rf "$JS"; exit 3; }
  echo "OK C20 passes a row that says who asked and is in the counted shape (positive control)"
  printf '%s\n| ⭐ **8** | [status:OPEN] **asked-by:** Jon, Q24 — why him | default |\n' "$HDRA" > "$JS/idx.md"
  OUT=$(LINT_JON_INDEX="$JS/idx.md" check_jon_surface)
  echo "$OUT" | grep -q "UNCOUNTABLE ROW" || { echo "SELFTEST BROKEN: C20 missed a decorated number cell -- THE 08-24 DEFECT that hid one of Jon's own questions from the counter"; rm -rf "$JS"; exit 3; }
  echo "OK C20 fails a row whose number cell carries decoration (the 08-24 defect, replayed)"
  printf '%s\n| **1** | [status:OPEN] no provenance here | default |\n' "$HDRA" > "$JS/idx.md"
  OUT=$(LINT_JON_INDEX="$JS/idx.md" check_jon_surface)
  echo "$OUT" | grep -q "NO PROVENANCE" || { echo "SELFTEST BROKEN: C20 accepted a row that does not say who asked -- SEC-108's whole content"; rm -rf "$JS"; exit 3; }
  echo "OK C20 fails a row that does not say who asked"
  # ⚠️ a row OUTSIDE section A must not be graded -- section B exists for things that LOOK like asks
  # and are not, and grading it would push noise onto the surface this check exists to keep readable.
  printf '%s\n| **1** | [status:OPEN] **asked-by:** Professional, 2026-08-30 — why him | default |\n## B — not rows\n| **9** | [status:OPEN] not an ask at all | none |\n' "$HDRA" > "$JS/idx.md"
  OUT=$(LINT_JON_INDEX="$JS/idx.md" check_jon_surface)
  echo "$OUT" | grep -q "PASS \[C20\]" || { echo "SELFTEST BROKEN: C20 graded a row outside section A"; rm -rf "$JS"; exit 3; }
  echo "$OUT" | grep -q "1 open row" || { echo "SELFTEST BROKEN: C20 counted a section-B row into section A's total"; rm -rf "$JS"; exit 3; }
  echo "OK C20 grades section A only and stops at the next heading"
  OUT=$(LINT_JON_INDEX="$JS/nope.md" check_jon_surface)
  echo "$OUT" | grep -q "FAIL \[C20\]" || { echo "SELFTEST BROKEN: C20 passed with no surface to read"; rm -rf "$JS"; exit 3; }
  echo "OK C20 fails when Jon's surface cannot be read (UNKNOWN dominates a PASS)"
  rm -rf "$JS"
  # --- C21 controls. FOUR. ⛔ The first is the REAL 2026-08-30 state that Soul measured and this
  # trunk re-measured worse: an obligation surface holding files that no read-at-open document names.
  OB=$(mktemp -d)
  mkdir -p "$OB/surface"
  : > "$OB/surface/PRO-J1-a-row.md"
  printf 'read the inbound and the wake note\n' > "$OB/doc.md"
  OUT=$(LINT_OBLIGATION_DIR="$OB/surface" LINT_READ_AT_OPEN="$OB/doc.md" check_obligation_reachable)
  echo "$OUT" | grep -q "FAIL \[C21\]" || { echo "SELFTEST BROKEN: C21 passed a surface holding files that NO read-at-open document names -- the 08-30 state"; rm -rf "$OB"; exit 3; }
  echo "OK C21 fails an obligation surface no read-at-open document routes to (the 08-30 state)"
  printf 'read %s at session open\n' "$OB/surface" >> "$OB/doc.md"
  OUT=$(LINT_OBLIGATION_DIR="$OB/surface" LINT_READ_AT_OPEN="$OB/doc.md" check_obligation_reachable)
  echo "$OUT" | grep -q "PASS \[C21\]" || { echo "SELFTEST BROKEN: C21 cannot pass a routed surface -- a check that cannot pass is a wall"; rm -rf "$OB"; exit 3; }
  echo "OK C21 passes once a read-at-open document names the surface (positive control)"
  OUT=$(LINT_OBLIGATION_DIR="$OB/surface" LINT_READ_AT_OPEN="$OB/absent.md" check_obligation_reachable)
  echo "$OUT" | grep -q "FAIL \[C21\]" || { echo "SELFTEST BROKEN: C21 treated an unreadable read-at-open document as clean"; rm -rf "$OB"; exit 3; }
  echo "OK C21 fails when a read-at-open document cannot be read (UNKNOWN dominates a PASS)"
  # ⚠️ an EMPTY surface must not fail -- nothing awaits routing, and failing it would teach seats to
  # delete rows to go green, which is the opposite of what this check is for.
  rm -f "$OB/surface"/*.md
  OUT=$(LINT_OBLIGATION_DIR="$OB/surface" LINT_READ_AT_OPEN="$OB/doc.md" check_obligation_reachable)
  echo "$OUT" | grep -q "PASS \[C21\]" || { echo "SELFTEST BROKEN: C21 failed an EMPTY surface -- that teaches seats to delete rows to go green"; rm -rf "$OB"; exit 3; }
  echo "OK C21 passes an empty surface without demanding routing"
  rm -rf "$OB"
  # --- C22: body wikilinks. FOUR fixtures, and A/B are a PAIR on purpose.
  # ⛔ The exclusion is the dangerous half: a filter that drops everything also reports zero
  # unresolved. So case A proves the SAME ref fails when it is a link, and case B proves it passes
  # when it is backticked prose. Neither alone proves anything -- A is B's positive control.
  # Built 2026-08-30 because a /dream run found 5 dangling refs on 08-24, ticketed this check, and
  # a /dream run on 08-30 found THE SAME FIVE. The second measurement was the price of not building it.
  BL="$(mktemp -d)"; mkdir -p "$BL/wiki"
  printf -- '---
title: real
---

See [[real-page]].
' > "$BL/wiki/real-page.md"
  printf -- '---
title: a
---

[[page-that-was-never-written]]
' > "$BL/wiki/case-a.md"
  OUT=$( cd "$BL" && LINT_LINK_EXTRA="" check_body_links )
  echo "$OUT" | grep -q "FAIL \[C22\]" || { echo "SELFTEST BROKEN: C22 passed a dangling BODY wikilink"; rm -rf "$BL"; exit 3; }
  echo "OK C22 fails a dangling body wikilink"
  rm "$BL/wiki/case-a.md"
  printf -- '---
title: b
---

Write it as `[[page-that-was-never-written]]` in prose.
' > "$BL/wiki/case-b.md"
  OUT=$( cd "$BL" && LINT_LINK_EXTRA="" check_body_links )
  echo "$OUT" | grep -q "PASS \[C22\]" || { echo "SELFTEST BROKEN: C22 called backticked syntax documentation a link -- the false-positive family this check exists to avoid"; rm -rf "$BL"; exit 3; }
  echo "OK C22 excludes the SAME ref when it is backticked prose (case A is this case's positive control)"
  printf -- '---
title: d
---

[[Map|wiki/tracker/no-such-map.md]]
' > "$BL/wiki/case-d.md"
  OUT=$( cd "$BL" && LINT_LINK_EXTRA="" check_body_links )
  echo "$OUT" | grep -q "FAIL \[C22\]" || { echo "SELFTEST BROKEN: C22 passed a piped ref whose path does not exist"; rm -rf "$BL"; exit 3; }
  echo "OK C22 fails a piped ref whose target path is absent"
  rm -rf "$BL"
  OUT=$(LINT_LINK_ROOTS=nosuchdir-xyz LINT_LINK_EXTRA="" check_body_links)
  echo "$OUT" | grep -q "FAIL \[C22\]" || { echo "SELFTEST BROKEN: C22 went silent when its population was absent"; exit 3; }
  echo "OK C22 fails when its link root is absent (UNKNOWN dominates a PASS)"
  # --- C23: corpus currency. FIVE fixtures, and A/B are a PAIR on purpose.
  # ⛔ The danger here is the mirror image of C22's: a currency check that compares NOTHING reports
  # the same "0 divergent" as one that compared everything, and a stale corpus answers as fast and
  # as confidently as a current one. So case B proves the check goes GREEN on a genuinely current
  # mirror -- without B, case A's red proves only that the check can print red.
  # Built 2026-08-31 after the mirror this fleet's retrieval actually reads was measured holding a
  # PRE-C22 copy of the oath-checks skill: 27,710 B, zero occurrences of "C22", against 33,700 live.
  CC="$(mktemp -d)"; mkdir -p "$CC/src/wiki" "$CC/mir/wiki"
  printf -- 'alpha\n' > "$CC/src/wiki/a.md"
  printf -- 'beta\n'  > "$CC/src/wiki/b.md"
  cp -p "$CC/src/wiki/a.md" "$CC/src/wiki/b.md" "$CC/mir/wiki/"
  OUT=$( cd "$CC/src" && LINT_CORPUS_MIRROR="$CC/mir" LINT_CORPUS_ROOTS=wiki check_corpus_currency )
  echo "$OUT" | grep -q "PASS \[C23\]" || { echo "SELFTEST BROKEN: C23 failed a genuinely current mirror -- a check that cannot go green is not a check"; rm -rf "$CC"; exit 3; }
  echo "OK C23 passes a current mirror (this is case A's positive control, not decoration)"
  rm "$CC/mir/wiki/b.md"
  OUT=$( cd "$CC/src" && LINT_CORPUS_MIRROR="$CC/mir" LINT_CORPUS_ROOTS=wiki check_corpus_currency )
  echo "$OUT" | grep -q "FAIL \[C23\]" || { echo "SELFTEST BROKEN: C23 passed a corpus missing a file the working tree has"; rm -rf "$CC"; exit 3; }
  echo "OK C23 fails when the query corpus is missing a file"
  cp -p "$CC/src/wiki/b.md" "$CC/mir/wiki/b.md"
  printf -- 'beta grew a second line\n' > "$CC/src/wiki/b.md"
  OUT=$( cd "$CC/src" && LINT_CORPUS_MIRROR="$CC/mir" LINT_CORPUS_ROOTS=wiki LINT_CORPUS_MAXLAG_S=999999 check_corpus_currency )
  echo "$OUT" | grep -q "FAIL \[C23\]" || { echo "SELFTEST BROKEN: C23 passed a corpus holding a STALE VERSION of a live file -- the exact defect it was built for"; rm -rf "$CC"; exit 3; }
  echo "OK C23 fails when the corpus holds an outdated copy of a file that still exists"
  cp -p "$CC/src/wiki/b.md" "$CC/mir/wiki/b.md"
  # Age the MIRROR rather than touching the source: a same-second fixture yields an integer
  # lag of 0 and proves nothing, which is how this fixture first failed.
  touch -d "2020-01-01 00:00:00" "$CC/mir/wiki/a.md" "$CC/mir/wiki/b.md"
  OUT=$( cd "$CC/src" && LINT_CORPUS_MIRROR="$CC/mir" LINT_CORPUS_ROOTS=wiki LINT_CORPUS_MAXLAG_S=0 check_corpus_currency )
  echo "$OUT" | grep -q "FAIL \[C23\]" || { echo "SELFTEST BROKEN: C23 ignored a lag beyond its declared tolerance"; rm -rf "$CC"; exit 3; }
  echo "OK C23 fails when newest-file lag exceeds the declared tolerance"
  OUT=$( cd "$CC/src" && LINT_CORPUS_MIRROR="$CC/mir/nosuchdir-xyz" LINT_CORPUS_ROOTS=wiki check_corpus_currency )
  echo "$OUT" | grep -q "FAIL \[C23\]" || { echo "SELFTEST BROKEN: C23 went silent when the corpus it declared does not exist"; rm -rf "$CC"; exit 3; }
  echo "OK C23 fails when the declared query corpus is absent (UNKNOWN dominates a PASS)"
  rm -rf "$CC"
  # --- C24: index coverage. FIVE fixtures, and A/B are a PAIR on purpose.
  # ⛔ Case B is the one that matters: an index that contains OTHER trunks and not this one. That is
  # not a hypothetical -- it is the literal state two seats read at 08:2x this morning and reported
  # as "this index holds one trunk", when what they had actually caught was a rebuild in progress.
  # Case A proves the check can go green on a covering index; without it, B's red proves only that
  # the check can print red.
  IX="$(mktemp -d)"
  python - "$IX/ok.sqlite" "$IX/notme.sqlite" "$IX/empty.sqlite" "$IX/wrongschema.sqlite" <<'PYFIX'
import sqlite3, sys
ok, notme, empty, wrong = sys.argv[1:5]
for path, rows in ((ok, [("Professional",), ("CFL",), ("CFL",)]), (notme, [("CFL",), ("Personal",)]), (empty, [])):
    c = sqlite3.connect(path)
    c.execute("CREATE TABLE docs_meta (slug TEXT, trunk TEXT)")
    c.executemany("INSERT INTO docs_meta (slug, trunk) VALUES ('s', ?)", rows)
    c.commit(); c.close()
c = sqlite3.connect(wrong)
c.execute("CREATE TABLE something_else (x TEXT)")
c.commit(); c.close()
PYFIX
  OUT=$(LINT_INDEX_DB="$IX/ok.sqlite" LINT_INDEX_TRUNK=Professional check_index_coverage)
  echo "$OUT" | grep -q "PASS \[C24\]" || { echo "SELFTEST BROKEN: C24 failed an index that DOES contain this trunk -- a check that cannot go green is not a check"; rm -rf "$IX"; exit 3; }
  echo "OK C24 passes an index containing this trunk (case B's positive control, not decoration)"
  OUT=$(LINT_INDEX_DB="$IX/notme.sqlite" LINT_INDEX_TRUNK=Professional check_index_coverage)
  echo "$OUT" | grep -q "FAIL \[C24\]" || { echo "SELFTEST BROKEN: C24 passed a well-populated index that does not contain this trunk -- the 08:2x state, replayed"; rm -rf "$IX"; exit 3; }
  echo "OK C24 fails an index full of OTHER trunks and empty of this one"
  OUT=$(LINT_INDEX_DB="$IX/empty.sqlite" LINT_INDEX_TRUNK=Professional check_index_coverage)
  echo "$OUT" | grep -q "FAIL \[C24\]" || { echo "SELFTEST BROKEN: C24 called an EMPTY index covered -- fast and empty is the defect, not the baseline"; rm -rf "$IX"; exit 3; }
  echo "OK C24 fails a 0-document index (VACUOUS)"
  OUT=$(LINT_INDEX_DB="$IX/wrongschema.sqlite" LINT_INDEX_TRUNK=Professional check_index_coverage)
  echo "$OUT" | grep -q "FAIL \[C24\]" || { echo "SELFTEST BROKEN: C24 went quiet when the index schema was not the one declared"; rm -rf "$IX"; exit 3; }
  echo "OK C24 fails when the declared table is absent (the index is not what this trunk thinks it queries)"
  OUT=$(LINT_INDEX_DB="$IX/ok.sqlite" LINT_INDEX_TRUNK="" check_index_coverage)
  echo "$OUT" | grep -q "FAIL \[C24\]" || { echo "SELFTEST BROKEN: C24 passed without being told which trunk is its own -- it cannot have asked its question"; rm -rf "$IX"; exit 3; }
  echo "OK C24 fails when it was never told which trunk is its own (UNKNOWN dominates a PASS)"
  OUT=$(LINT_INDEX_DB="$IX/nosuchfile.sqlite" LINT_INDEX_TRUNK=Professional check_index_coverage)
  echo "$OUT" | grep -q "FAIL \[C24\]" || { echo "SELFTEST BROKEN: C24 went silent when its declared index was absent"; rm -rf "$IX"; exit 3; }
  echo "OK C24 fails when the declared index file is absent"
  rm -rf "$IX"
  # --- C25 + C26: the per-trunk VECTOR index. SEVEN fixtures across the two checks.
  # ⛔ A/B ARE A PAIR ON PURPOSE. A check proven only to FAIL is a check that might never pass, and
  # a check proven only to PASS is decoration. Each of these two is proven in BOTH directions
  # against a hand-built sqlite whose meta.built_utc and tier mix are chosen, not inherited.
  VX=$(mktemp -d)
  VX_PY="$VX/mk.py"
  cat > "$VX_PY" <<'MKEOF'
import sqlite3, sys, datetime, os
path, age_days, tiers = sys.argv[1], float(sys.argv[2]), sys.argv[3]
con = sqlite3.connect(path)
con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
con.execute("CREATE TABLE files (id INTEGER PRIMARY KEY, path TEXT, tier TEXT)")
con.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, file_id INTEGER)")
if age_days >= 0:
    built = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=age_days)
    con.execute("INSERT INTO meta VALUES ('built_utc', ?)",
                (built.strftime('%Y-%m-%dT%H:%M:%SZ'),))
fid = cid = 0
for spec in tiers.split(','):
    if not spec:
        continue
    name, n = spec.split('=')
    fid += 1
    con.execute("INSERT INTO files VALUES (?,?,?)", (fid, 'f%d' % fid, name))
    for _ in range(int(n)):
        cid += 1
        con.execute("INSERT INTO chunks VALUES (?,?)", (cid, fid))
con.commit()
MKEOF
  python "$VX_PY" "$VX/fresh_wide.sqlite"  0.1 "knowledge=800,queue=200"
  python "$VX_PY" "$VX/stale_wide.sqlite" 30.0 "knowledge=800,queue=200"
  python "$VX_PY" "$VX/fresh_narrow.sqlite" 0.1 "knowledge=20,claude_ai=980"
  python "$VX_PY" "$VX/empty.sqlite"       0.1 ""
  python "$VX_PY" "$VX/nostamp.sqlite"    -1   "knowledge=800,queue=200"
  # C25 case A -- a FRESH index passes. The positive control: without it, "C25 can fail" is
  # satisfied by a check that fails on everything.
  OUT=$(LINT_VECTOR_DB="$VX/fresh_wide.sqlite" check_vector_index_age)
  echo "$OUT" | grep -q "PASS \[C25\]" || { echo "SELFTEST BROKEN: C25 failed a freshly built index -- a check that cannot go green is not a check"; rm -rf "$VX"; exit 3; }
  echo "OK C25 passes a freshly built index (positive control, not decoration)"
  # C25 case B -- a 30-day-old index fails. The 2026-08-31 state, replayed.
  OUT=$(LINT_VECTOR_DB="$VX/stale_wide.sqlite" LINT_VECTOR_WRAPPER="" check_vector_index_age)
  echo "$OUT" | grep -q "FAIL \[C25\]" || { echo "SELFTEST BROKEN: C25 passed a 30-day-old index -- the state that made 29 of 80 wiki pages unreachable"; rm -rf "$VX"; exit 3; }
  echo "OK C25 fails a stale index"
  # C25 case C -- 0 chunks is VACUOUS, not fresh. Fast and empty is the defect, not the baseline.
  OUT=$(LINT_VECTOR_DB="$VX/empty.sqlite" LINT_VECTOR_WRAPPER="" check_vector_index_age)
  echo "$OUT" | grep -q "FAIL \[C25\]" || { echo "SELFTEST BROKEN: C25 called a 0-chunk index current -- VACUOUS DOMINATES A PASS"; rm -rf "$VX"; exit 3; }
  echo "OK C25 fails a 0-chunk index (VACUOUS)"
  # C25 case D -- no meta.built_utc means the age is UNKNOWN. Absence of a stamp is not freshness.
  OUT=$(LINT_VECTOR_DB="$VX/nostamp.sqlite" LINT_VECTOR_WRAPPER="" check_vector_index_age)
  echo "$OUT" | grep -q "FAIL \[C25\]" || { echo "SELFTEST BROKEN: C25 read a missing build stamp as fresh -- absence is not freshness"; rm -rf "$VX"; exit 3; }
  echo "OK C25 fails when the index carries no build stamp (UNKNOWN dominates a PASS)"
  # C25 case E -- a declared index that does not exist must fail, never pass quietly.
  OUT=$(LINT_VECTOR_DB="$VX/nosuchfile.sqlite" LINT_VECTOR_WRAPPER="" check_vector_index_age)
  echo "$OUT" | grep -q "FAIL \[C25\]" || { echo "SELFTEST BROKEN: C25 went silent when its declared index was absent"; rm -rf "$VX"; exit 3; }
  echo "OK C25 fails when the declared index file is absent"
  # C26 case A -- a wide default scope passes (800/1000 = 80%).
  OUT=$(LINT_VECTOR_DB="$VX/fresh_wide.sqlite" LINT_VECTOR_DEFAULT_TIERS=knowledge LINT_VECTOR_WRAPPER="" check_vector_index_scope)
  echo "$OUT" | grep -q "PASS \[C26\]" || { echo "SELFTEST BROKEN: C26 failed an index whose default scope is 80% -- a check that cannot go green is not a check"; rm -rf "$VX"; exit 3; }
  echo "OK C26 passes an index with a wide default scope (positive control)"
  # C26 case B -- 20/1000 = 2% fails. THE FIXTURE IS THIS TRUNK'S OWN 2026-08-31 SHAPE: a large
  # index whose bulk sits in a tier the default query cannot see. Note it is FRESH -- proving C26
  # is independent of C25 and that a current index of the wrong scope does not get a free pass.
  OUT=$(LINT_VECTOR_DB="$VX/fresh_narrow.sqlite" LINT_VECTOR_DEFAULT_TIERS=knowledge LINT_VECTOR_WRAPPER="" check_vector_index_scope)
  echo "$OUT" | grep -q "FAIL \[C26\]" || { echo "SELFTEST BROKEN: C26 passed an index reaching 2% of its own chunks by default -- the defect Jon named on 08-31"; rm -rf "$VX"; exit 3; }
  echo "OK C26 fails a fresh index whose default scope reaches 2% (independent of C25)"
  # C26 case C -- THE DIFFERENTIAL SCOPE ORACLE, replacing a string check that could not fail on the
  # thing it existed to catch. Specified by the Secretary while grading C26 at this seat's request:
  # "a grep for a literal string in your own wrapper ... tests that YOU still say --all-tiers; it
  # cannot test that CFL still MEANS it." The stubs below are fake wrappers that emit JSON, so the
  # oracle is exercised WITHOUT touching the real index or costing a real query.
  cat > "$VX/w_widens.sh" <<'WEOF'
#!/usr/bin/env bash
# a wrapper whose default scope genuinely reaches further than its narrow scope
for a in "$@"; do [ "$a" = "--knowledge-only" ] && { echo '[{"source":"wiki/a.md"}]'; exit 0; }; done
echo '[{"source":"wiki/a.md"},{"source":"raw/asops/asop017.txt"}]'
WEOF
  cat > "$VX/w_converges.sh" <<'CEOF'
#!/usr/bin/env bash
# a wrapper whose widening flag has stopped widening -- renamed, dropped, or no longer honoured
echo '[{"source":"wiki/a.md"}]'
CEOF
  cat > "$VX/w_silent.sh" <<'SEOF'
#!/usr/bin/env bash
exit 0
SEOF
  chmod +x "$VX"/w_*.sh
  OUT=$(LINT_VECTOR_DB="$VX/fresh_wide.sqlite" LINT_VECTOR_DEFAULT_TIERS="*" LINT_VECTOR_WRAPPER="$VX/w_converges.sh" check_vector_index_scope)
  echo "$OUT" | grep -q "FAIL \[C26\]" || { echo "SELFTEST BROKEN: the scope oracle did not fire when default and narrow queries CONVERGED -- that is the silent 4% failure it exists to catch"; rm -rf "$VX"; exit 3; }
  echo "OK C26 fails when the default and narrow scopes CONVERGE (the flag stopped widening)"
  OUT=$(LINT_VECTOR_DB="$VX/fresh_wide.sqlite" LINT_VECTOR_DEFAULT_TIERS="*" LINT_VECTOR_WRAPPER="$VX/w_widens.sh" check_vector_index_scope)
  echo "$OUT" | grep -q "PASS \[C26\]" || { echo "SELFTEST BROKEN: the scope oracle cannot go green against a wrapper that DOES widen -- an oracle that always fails is not an oracle"; rm -rf "$VX"; exit 3; }
  echo "OK C26 passes when the default scope genuinely reaches further (oracle positive control)"
  OUT=$(LINT_VECTOR_DB="$VX/fresh_wide.sqlite" LINT_VECTOR_DEFAULT_TIERS="*" LINT_VECTOR_WRAPPER="$VX/w_silent.sh" check_vector_index_scope)
  echo "$OUT" | grep -q "FAIL \[C26\]" || { echo "SELFTEST BROKEN: the scope oracle went GREEN when the wrapper returned nothing -- a check that could not run is UNKNOWN"; rm -rf "$VX"; exit 3; }
  echo "OK C26 fails when the wrapper returns nothing (UNKNOWN dominates a PASS)"
  OUT=$(LINT_VECTOR_DB="$VX/fresh_wide.sqlite" LINT_VECTOR_DEFAULT_TIERS="*" LINT_VECTOR_WRAPPER="$VX/nosuch.sh" check_vector_index_scope)
  echo "$OUT" | grep -q "FAIL \[C26\]" || { echo "SELFTEST BROKEN: C26 went silent when its declared wrapper was absent"; rm -rf "$VX"; exit 3; }
  echo "OK C26 fails when the declared wrapper is absent"
  # C26/C25 case D -- THE THIN-DENOMINATOR PAIR. `0/0` was guarded from the start; `1/1` was NOT and
  # cleared C26 at 100%. Raised 2026-08-31 by the Secretary after the identical hole fired in their
  # own degree-zero meter; verified here by RUNNING it before believing it.
  python "$VX_PY" "$VX/onechunk.sqlite" 0.1 "knowledge=1"
  OUT=$(LINT_VECTOR_DB="$VX/onechunk.sqlite" LINT_VECTOR_DEFAULT_TIERS="*" LINT_VECTOR_WRAPPER="$VX/w_widens.sh" check_vector_index_scope)
  echo "$OUT" | grep -q "FAIL \[C26\]" || { echo "SELFTEST BROKEN: C26 passed a ONE-CHUNK index at 100% -- any ratio clears a denominator that small"; rm -rf "$VX"; exit 3; }
  echo "OK C26 fails a one-chunk index (thin denominator, not just empty)"
  OUT=$(LINT_VECTOR_DB="$VX/onechunk.sqlite" LINT_VECTOR_WRAPPER="" check_vector_index_age)
  echo "$OUT" | grep -q "FAIL \[C25\]" || { echo "SELFTEST BROKEN: C25 called a FRESH one-chunk index current -- the stamp would certify a degenerate corpus"; rm -rf "$VX"; exit 3; }
  echo "OK C25 fails a fresh one-chunk index (a stamp over a degenerate corpus is not currency)"
  OUT=$(LINT_VECTOR_DB="$VX/fresh_wide.sqlite" LINT_VECTOR_DEFAULT_TIERS="*" LINT_VECTOR_WRAPPER="$VX/w_widens.sh" LINT_VECTOR_MIN_CHUNKS=100 check_vector_index_scope)
  echo "$OUT" | grep -q "PASS \[C26\]" || { echo "SELFTEST BROKEN: the floor is a blanket refusal -- a 1,000-chunk index must still pass"; rm -rf "$VX"; exit 3; }
  echo "OK C26 still passes a 1,000-chunk index above the floor (the floor is not a blanket refusal)"
  # --- C27: a frontmatter date AHEAD of the artifact's own mtime. Jon flagged the shape; the
  # Secretary measured it. Three fixtures, and the empty case is graded because a stamp audit over
  # an empty population is the cheapest false green there is.
  SF=$(mktemp -d)
  printf -- '---
date: 2099-01-01
---
body
' > "$SF/pro-future.md"
  printf -- '---
date: 2001-01-01
---
body
' > "$SF/pro-past.md"
  OUT=$(LINT_STAMPF_DIR="$SF" check_stamp_future)
  echo "$OUT" | grep -q "FAIL \[C27\]" || { echo "SELFTEST BROKEN: C27 passed a letter stamped 2099 with today's mtime -- the fresher-than-it-is direction"; rm -rf "$SF"; exit 3; }
  echo "OK C27 fails a frontmatter date ahead of the artifact's own mtime"
  rm -f "$SF/pro-future.md"
  OUT=$(LINT_STAMPF_DIR="$SF" check_stamp_future)
  echo "$OUT" | grep -q "PASS \[C27\]" || { echo "SELFTEST BROKEN: C27 cannot go green on a correctly-stamped population -- a check that cannot pass is not a check"; rm -rf "$SF"; exit 3; }
  echo "OK C27 passes a correctly-stamped population (positive control)"
  rm -f "$SF/pro-past.md"
  OUT=$(LINT_STAMPF_DIR="$SF" check_stamp_future)
  echo "$OUT" | grep -q "FAIL \[C27\]" || { echo "SELFTEST BROKEN: C27 passed over ZERO dated artifacts -- a stamp audit with no population is VACUOUS"; rm -rf "$SF"; exit 3; }
  echo "OK C27 fails on an empty population (VACUOUS dominates a PASS)"
  # C27 case D -- FAIL-CLOSED ON UNPARSEABLE. The first loop skipped these WITHOUT counting them, so
  # the PASS line reported a population that silently excluded whatever the regex could not read.
  # Graded by the Secretary from the source; C16 in the same file already did it correctly.
  printf -- '---
date: "Monday, the first of September"
---
body
' > "$SF/pro-unparseable.md"
  printf -- '---
date: 2001-01-01
---
body
' > "$SF/pro-ok.md"
  OUT=$(LINT_STAMPF_DIR="$SF" check_stamp_future)
  echo "$OUT" | grep -q "FAIL \[C27\]" || { echo "SELFTEST BROKEN: C27 went GREEN past a date it could not parse -- unparseable is UNKNOWN, and UNKNOWN dominates a PASS"; rm -rf "$SF"; exit 3; }
  echo "$OUT" | grep -q "1 unparseable" || { echo "SELFTEST BROKEN: C27 failed but did not COUNT the unparseable artifact -- absent from the denominator is the defect, not merely ungraded"; rm -rf "$SF"; exit 3; }
  echo "OK C27 counts and fails an unparseable date (fail-closed, in the denominator)"
  # and an ISO-with-time date must still PARSE rather than being silently dropped
  rm -f "$SF/pro-unparseable.md"
  printf -- '---
date: 2001-01-01T03:52:00Z
---
body
' > "$SF/pro-iso.md"
  OUT=$(LINT_STAMPF_DIR="$SF" check_stamp_future)
  echo "$OUT" | grep -q "PASS \[C27\]" || { echo "SELFTEST BROKEN: C27 cannot read an ISO date with a time component -- it would count a well-formed stamp as unparseable"; rm -rf "$SF"; exit 3; }
  echo "OK C27 parses an ISO date carrying a time component (not everything with extra text is unparseable)"
  rm -rf "$SF"
  rm -rf "$VX"

  # ===================================================================================================
  # C28 -- THE LINT ON THIS LINT. Every fixture PINS its own source list; C7 in this file records what
  # happens when a fixture inherits a global and passes for a reason it did not construct.
  # ⛔ THE POSITIVE CONTROL IS NOT DECORATION HERE: the first build of C28 went GREEN against the bug
  # fixture below because an exemption was written `line ~ /\</`, and in awk `\<` is the WORD-BOUNDARY
  # metacharacter -- it matched nearly every line and exempted the entire file. ⭐ Caught by this
  # fixture on its first run. Re-reading the source had not caught it, and would not have.
  SK=$(mktemp -d)
  cat > "$SK/bug.sh" <<'BUGEOF'
demo_loop_fixture() {
  local n=0
  for f in "$dir"/*.md; do
    [ -f "$f" ] || continue
    raw=$(grep -m1 '^date:' "$f")
    [ -n "$raw" ] || continue
    n=$((n + 1))
  done
}
BUGEOF
  cat > "$SK/clean.sh" <<'CLEANEOF'
demo_loop_fixture() {
  local n=0 undated=0
  for f in "$dir"/*.md; do
    [ -f "$f" ] || continue
    n=$((n + 1))
    raw=$(grep -m1 '^date:' "$f")
    if [ -z "$raw" ]; then undated=$((undated + 1)); continue; fi
  done
}
CLEANEOF
  cat > "$SK/filters.sh" <<'FILTEOF'
demo_loop_fixture() {
  local n=0
  while IFS= read -r line; do
    case "$line" in ''|'#'*) continue ;; esac
    [ "$disp" = "DELIVER" ] || continue
    n=$((n + 1))
  done < "$src"
}
FILTEOF
  OUT=$(LINT_SKIPLINT_FILES="$SK/bug.sh" check_uncounted_skip)
  echo "$OUT" | grep -q "FAIL \[C28\]" || { echo "SELFTEST BROKEN: C28 went GREEN against C27's exact original bug -- a skip before the counter, which is the only thing it exists to find"; rm -rf "$SK"; exit 3; }
  echo "$OUT" | grep -q 'bug.sh:6' || { echo "SELFTEST BROKEN: C28 failed but did not NAME the offending line -- a finding you cannot locate is not a finding"; rm -rf "$SK"; exit 3; }
  echo "OK C28 fails a continue that runs before the loop's first counter increment, and names the line"
  OUT=$(LINT_SKIPLINT_FILES="$SK/clean.sh" check_uncounted_skip)
  echo "$OUT" | grep -q "PASS \[C28\]" || { echo "SELFTEST BROKEN: C28 cannot go green on the CORRECTED form of the same loop -- a check that always fails is not a check"; rm -rf "$SK"; exit 3; }
  echo "OK C28 passes the corrected loop (positive control -- it is the fix that turns it green)"
  OUT=$(LINT_SKIPLINT_FILES="$SK/filters.sh" check_uncounted_skip)
  echo "$OUT" | grep -q "PASS \[C28\]" || { echo "SELFTEST BROKEN: C28 flagged POPULATION-DEFINITION filters (blank/comment lines, a value filter) as if they were failed reads -- that discrimination IS the check, and without it C28 is a firehose nobody will keep"; rm -rf "$SK"; exit 3; }
  echo "OK C28 exempts population-DEFINITION filters while flagging population-EXCLUSION skips"
  OUT=$(LINT_SKIPLINT_FILES="$SK/nosuch.sh" check_uncounted_skip)
  echo "$OUT" | grep -q "FAIL \[C28\]" || { echo "SELFTEST BROKEN: C28 went silent when its declared source was ABSENT -- a check that could not run is UNKNOWN"; rm -rf "$SK"; exit 3; }
  echo "OK C28 fails when a declared lint source is absent (UNKNOWN dominates a PASS)"
  rm -rf "$SK"

  # ===================================================================================================
  # C29 -- COMPACT BOUNDARY -> DURABLE RECORD. Jon, 2026-09-01: "please ensure this all trunk standard
  # update is indeed the default and not just the hoped outcome."
  # ⚠️ THE WINDOW IS THE CHECK, and the fixtures cannot prove that -- it is a property of the real
  # repo's base rate, measured and printed in the check's own comment (12h pairs ~51% of RANDOM
  # instants here; 1h pairs 19% against an observed 87%). A fixture proves the machinery; only the
  # negative control proves the number means anything.
  BR=$(mktemp -d)
  # ⛔ PIN THE FIXTURE'S OWN INPUTS. The first version drew `head -3`, which are all PRE-EPOCH rows,
  # so the fixture graded ZERO boundaries and failed as VACUOUS -- passing or failing for a reason
  # the fixture had not constructed. That is C7's defect, in this file, in a fixture written to
  # prevent exactly it.
  sed -n '20,22p' exchange/precompact-receipts.log > "$BR/paired.log" 2>/dev/null || : > "$BR/paired.log"
  # ⛔ THIS FIXTURE HAD TO BE REBUILT: the first one used a 2019 stamp, which is PRE-EPOCH, so it
  # failed as VACUOUS and never exercised the silent-boundary branch at all. It was GREEN on a
  # verdict it had not constructed -- C7's defect, caught only when the assertion below demanded
  # the message NAME the boundary. ⭐ An assertion on the reason, not just the verdict, is what
  # separates a fixture from a coincidence.
  # Two POST-EPOCH boundaries one second apart: no durable record can possibly land between them.
  printf '2026-08-17 09:41:47 CDT | fixture | 1 files 1 B | HEAD 000000 | OK
2026-08-17 09:41:48 CDT | fixture | 1 files 1 B | HEAD 000000 | OK
' > "$BR/orphan.log"
  printf 'a line carrying no timestamp at all
' > "$BR/unparsed.log"
  printf '2026-08-15 20:34:37 CDT | zz-selftest | 1 files 19 B | HEAD 1e644e0 | OK
' > "$BR/selftestonly.log"
  : > "$BR/empty.log"
  OUT=$(LINT_BOUNDARY_RECEIPTS="$BR/paired.log" LINT_BOUNDARY_RECORD="wiki/log.md" LINT_BOUNDARY_EPOCH="2026-08-16" LINT_BOUNDARY_GRACE_H="6" check_boundary_record)
  echo "$OUT" | grep -q "PASS \[C29\]" || { echo "SELFTEST BROKEN: C29 cannot go green on boundaries that DID produce a durable record -- a check that cannot pass is not a check"; rm -rf "$BR"; exit 3; }
  echo "OK C29 passes when every graded boundary produced a durable record"
  OUT=$(LINT_BOUNDARY_RECEIPTS="$BR/orphan.log" LINT_BOUNDARY_RECORD="wiki/log.md" LINT_BOUNDARY_EPOCH="2026-08-16" LINT_BOUNDARY_GRACE_H="6" check_boundary_record)
  echo "$OUT" | grep -q "FAIL \[C29\]" || { echo "SELFTEST BROKEN: C29 went GREEN on a compact boundary with NO durable record after it -- the silent boundary is the whole point"; rm -rf "$BR"; exit 3; }
  echo "$OUT" | grep -q "SILENT-BOUNDARY" || { echo "SELFTEST BROKEN: C29 failed but did not NAME the silent boundary"; rm -rf "$BR"; exit 3; }
  echo "OK C29 fails a compact boundary with no durable record, and names it"
  OUT=$(LINT_BOUNDARY_RECEIPTS="$BR/unparsed.log" LINT_BOUNDARY_RECORD="wiki/log.md" LINT_BOUNDARY_EPOCH="2026-08-16" LINT_BOUNDARY_GRACE_H="6" check_boundary_record)
  echo "$OUT" | grep -q "FAIL \[C29\]" || { echo "SELFTEST BROKEN: C29 went GREEN past a receipt line it could not parse -- unparseable is UNKNOWN"; rm -rf "$BR"; exit 3; }
  echo "OK C29 fails on an unparseable receipt line (fail-closed)"
  OUT=$(LINT_BOUNDARY_RECEIPTS="$BR/selftestonly.log" LINT_BOUNDARY_RECORD="wiki/log.md" LINT_BOUNDARY_EPOCH="2026-08-16" LINT_BOUNDARY_GRACE_H="6" check_boundary_record)
  echo "$OUT" | grep -q "FAIL \[C29\]" || { echo "SELFTEST BROKEN: C29 PASSED over a population consisting only of its own selftest rows -- that is a green earned from zero real boundaries"; rm -rf "$BR"; exit 3; }
  echo "OK C29 fails when the only rows are selftest rows (VACUOUS dominates a PASS)"
  OUT=$(LINT_BOUNDARY_RECEIPTS="$BR/empty.log" LINT_BOUNDARY_RECORD="wiki/log.md" LINT_BOUNDARY_EPOCH="2026-08-16" LINT_BOUNDARY_GRACE_H="6" check_boundary_record)
  echo "$OUT" | grep -q "FAIL \[C29\]" || { echo "SELFTEST BROKEN: C29 passed over an EMPTY receipt log"; rm -rf "$BR"; exit 3; }
  echo "OK C29 fails over an empty receipt log (VACUOUS)"
  OUT=$(LINT_BOUNDARY_RECEIPTS="$BR/nosuch.log" LINT_BOUNDARY_RECORD="wiki/log.md" LINT_BOUNDARY_EPOCH="2026-08-16" LINT_BOUNDARY_GRACE_H="6" check_boundary_record)
  echo "$OUT" | grep -q "FAIL \[C29\]" || { echo "SELFTEST BROKEN: C29 went silent when its declared receipt log was ABSENT"; rm -rf "$BR"; exit 3; }
  echo "OK C29 fails when the declared receipt log is absent (UNKNOWN dominates a PASS)"
  rm -rf "$BR"
  # --- C10 + C11: shipped 2026-08 with NO selftest coverage, and lint printed
  # "C10+C11 UNPROVEN" on every clean run for weeks. That is exactly soul's class
  # (2026-09-01): a check whose failure has never been shown to differ from its pass.
  # Surfaced 2026-09-02 by this session's own PRE-COMPACT ELDER, which found the two
  # names printed at line 610 of its transcript and noted the seat never connected them
  # to the class it had spent the day cataloguing. Both controls below FIRE.
  C10_CANARY="wiki/concepts/zz-c10-selftest-canary.md"
  printf -- '---
name: zz-c10-selftest-canary
title: canary
date: 2026-09-02
---
canary
' > "$C10_CANARY"
  OUT=$(check_derived_index); rm -f "$C10_CANARY"
  echo "$OUT" | grep -q "FAIL \[C10\]" && echo "OK C10 can fail (derived index drifts when a page appears on disk)" || { echo "SELFTEST BROKEN: C10 cannot fail -- a page absent from INDEX-DERIVED.md did not trip it"; exit 3; }
  OUT=$(check_derived_index)
  echo "$OUT" | grep -q "PASS \[C10\]" || { echo "SELFTEST BROKEN: C10 did not return to PASS after the canary was removed -- the selftest has damaged the tree"; exit 3; }
  echo "OK C10 returns to PASS once the canary is gone (both directions proven)"
  OUT=$(LINT_SKILL_ROOTS="/nonexistent-skill-root-for-selftest" check_skill_reach)
  echo "$OUT" | grep -q "FAIL \[C11\]" && echo "OK C11 can fail (UNKNOWN dominates a PASS when no skill root exists)" || { echo "SELFTEST BROKEN: C11 cannot fail -- an absent skill root did not produce UNKNOWN"; exit 3; }

  echo "== SELFTEST: 30 of 30 checks proven failable (C10, C11, C30 covered 2026-09-02); now the real run =="
  # --- C30 controls. POSITIVE FIRST: a planted subdirectory letter must be SEEN.
  EXC=$(mktemp -d); mkdir -p "$EXC/exchange/inbound/Jon-Threads" "$EXC/exchange/outbox"
  printf 'x
' > "$EXC/exchange/inbound/top.md"
  printf 'x
' > "$EXC/exchange/inbound/Jon-Threads/buried.md"
  OUT=$(FAILS=0; LINT_EXCL_ROOT="$EXC" check_population_exclusions)
  echo "$OUT" | grep -q "FAIL \[C30\]" && echo "OK C30 fails on a letter buried one directory down (the Jon-Threads case)" || { echo "SELFTEST BROKEN: C30 cannot see a subdirectory letter"; rm -rf "$EXC"; exit 3; }
  rm -rf "$EXC/exchange/inbound/Jon-Threads"
  OUT=$(FAILS=0; LINT_EXCL_ROOT="$EXC" check_population_exclusions)
  echo "$OUT" | grep -q "PASS \[C30\]" || { echo "SELFTEST BROKEN: C30 cannot pass on a flat tree -- a check that cannot pass is a wall"; rm -rf "$EXC"; exit 3; }
  echo "OK C30 returns to PASS when the subdirectory is gone (positive control)"
  rm -rf "$EXC"

  # --- C31 controls. THE RECEIVING DIRECTION. Negative first: a sibling letter addressed here by
  # its own filename, dated after the epoch, and absent from our inbound must FIRE.
  IRD="$(mktemp -d)"
  mkdir -p "$IRD/root/Sibling/exchange/outbox" "$IRD/in"
  printf 'dir	disposition	reason	from
' > "$IRD/roster.tsv"
  printf 'Sibling	DELIVER	fixture	2026-09-01
' >> "$IRD/roster.tsv"
  : > "$IRD/root/Sibling/exchange/outbox/sib-to-all-trunks-URGENT-2026-09-02.md"
  OUT=$(FAILS=0; LINT_ROSTER="$IRD/roster.tsv" LINT_TRUNK_ROOT="$IRD/root" LINT_INBOUND_DIR="$IRD/in" check_inbound_reconciled)
  echo "$OUT" | grep -q "FAIL \[C31\]" || { echo "SELFTEST BROKEN: C31 went GREEN on a sibling letter addressed here that never arrived -- that is the only thing it exists to catch"; rm -rf "$IRD"; exit 3; }
  echo "$OUT" | grep -q "UNRECEIVED" || { echo "SELFTEST BROKEN: C31 failed but did not NAME the unreceived letter"; rm -rf "$IRD"; exit 3; }
  echo "OK C31 fails on a sibling letter addressed here and absent from inbound, and names it"
  # POSITIVE CONTROL: the same letter, delivered. A check that cannot pass is a wall, not a gate.
  : > "$IRD/in/sib-to-all-trunks-URGENT-2026-09-02.md"
  OUT=$(FAILS=0; LINT_ROSTER="$IRD/roster.tsv" LINT_TRUNK_ROOT="$IRD/root" LINT_INBOUND_DIR="$IRD/in" check_inbound_reconciled)
  echo "$OUT" | grep -q "PASS \[C31\]" || { echo "SELFTEST BROKEN: C31 cannot pass once the letter is delivered"; rm -rf "$IRD"; exit 3; }
  echo "OK C31 returns to PASS when the letter is present (positive control)"
  # EMPTY POPULATION IS UNKNOWN, NEVER CLEAN -- the vacuous-green failure this suite has hit before.
  printf '# no DELIVER rows
' > "$IRD/empty.tsv"
  OUT=$(FAILS=0; LINT_ROSTER="$IRD/empty.tsv" LINT_TRUNK_ROOT="$IRD/root" LINT_INBOUND_DIR="$IRD/in" check_inbound_reconciled)
  echo "$OUT" | grep -q "FAIL \[C31\]" || { echo "SELFTEST BROKEN: C31 PASSED over zero sender trees -- an empty population is UNKNOWN"; rm -rf "$IRD"; exit 3; }
  echo "OK C31 fails over an empty sender population (UNKNOWN dominates a PASS)"
  rm -rf "$IRD"

fi

run_all

# ⛔ THE VERDICT IS VOID IF THE SOURCE MOVED WHILE IT WAS BEING PRODUCED. Checked BEFORE the
# pass/fail branch on purpose: a run whose own source changed cannot certify CLEAN and cannot
# honestly certify a failure count either -- UNKNOWN dominates both.
SELF_HASH_END="$(self_hash)"
if [ -z "$SELF_HASH_START" ] || [ -z "$SELF_HASH_END" ]; then
  echo "UNKNOWN [run] could not hash $0 -- a run that cannot verify its own source is UNKNOWN, not clean"; exit 4
fi
if [ "$SELF_HASH_START" != "$SELF_HASH_END" ]; then
  echo "UNKNOWN [run] $0 CHANGED ON DISK DURING THIS RUN ($SELF_HASH_START -> $SELF_HASH_END)."
  echo "UNKNOWN [run] This run read two different objects. Its verdict is VOID -- re-run without editing the script."
  exit 4
fi

# COUNT THE ROSTER, NEVER RESTATE IT. This banner read "27 checks run; 25 selftest-proven
# failable" for as long as the roster was 29/27, because the numbers were typed in and the roster
# grew underneath them. A success message is where a stale number does the most damage: it is the
# line a reader trusts when nothing looks wrong. "NEVER STATE A NUMBER YOU HAVE NOT JUST MEASURED"
# applies to the instrument's own report of itself.
# ⛔ AND THE FIRST VERSION OF THIS LINE COUNTED 33 WHERE THE ROSTER IS 29. `run_all` is a SINGLE
# line whose closing brace is not at column 0, so a `/^run_all/,/^}/` range ran past it and swallowed
# the fallback stub definitions below. ⭐ A STALE HARDCODED NUMBER REPLACED BY A FRESHLY COMPUTED
# WRONG ONE IS WORSE THAN THE STALE ONE: it carries the authority of a measurement. Count the ONE
# line, and assert it is plausible rather than trusting it.
_ROSTER=$(grep -m1 '^run_all() {' "$0" | grep -oE 'check_[a-z_]+' | sort -u | wc -l)
if [ "$FAILS" -eq 0 ]; then echo "LINT CLEAN ($_ROSTER checks run; $_ROSTER selftest-proven failable; source unchanged during run)"; exit 0
else echo "LINT: $FAILS check(s) failing"; exit 1; fi
