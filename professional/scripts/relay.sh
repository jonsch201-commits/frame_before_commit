#!/usr/bin/env bash
# relay.sh -- THE ACTUATOR HALF OF C9. Delivers outbox letters that C9 reports as ABSENT.
#
# WHY THIS EXISTS, and the reason is external prior art rather than another incident.
# `wiki/concepts/re-derived-not-researched.md`, 2026-08-24: this fleet's exchange/ is the
# TRANSACTIONAL OUTBOX pattern, and that pattern is not "write to an outbox" -- it is
# OUTBOX PLUS A RELAY PROCESS whose only job is to read unsent rows, deliver them, and mark
# them sent. We built the outbox and the alarm and never built the relay. Every delivery
# failure on record is the same missing component:
#   * 12 letters that never left the building        [2026-08-17, this trunk]
#   * 6 Personal->CFL letters, 6.8-72.8 h undelivered [2026-08-24, relayed+ Herald, hash-verified]
#   * Soul's routing letter, 6 h in its own outbox    [2026-08-24, measured here]
# C9 is the reporting half and it works. This is the half that ACTS -- see
# `wiki/concepts/a-control-with-no-reader.md` for the class.
#
# ⛔ SINGLE SOURCE OF TRUTH, DELIBERATELY. This script does NOT re-implement C9's addressee
# parsing. It RUNS lint.sh and acts on the `UNDELIVERED ... =ABSENT` lines C9 prints. A second
# copy of that parser is a divergent duplicate -- the defect this trunk raised against CFL as
# F5 and would then be committing itself. The cost is that relay.sh is only as good as C9, and
# that is the correct coupling: the actuator must never deliver to a tree the alarm would not
# have graded.
#
# ⛔ UNREACHABLE IS NOT ACTIONABLE. C9 reports two states, ABSENT and UNREACHABLE. Only ABSENT
# is delivered. An UNREACHABLE tree is UNKNOWN -- we do not know whether the letter is there --
# and UNKNOWN DOMINATES A PASS in both directions: it is not a licence to write either.
#
# ⛔ DRY RUN IS THE DEFAULT. Writing into a sibling tree is a cross-trunk act. Nothing is copied
# without --apply, and --apply writes ONLY to <tree>/exchange/inbound/ -- never wiki/, never
# skills/, never CLAUDE.md (standing constraint).
#
# Usage: scripts/relay.sh             report what WOULD be delivered; writes nothing; exit 0
#        scripts/relay.sh --apply     deliver, then cmp-verify each copy
#        scripts/relay.sh --selftest  prove the reporter and the actuator can both fail
set -u
cd "$(dirname "$0")/.." || exit 2

MODE="${1:-}"

trees_from_env() {
  if [ -n "${LINT_SIBLING_TREES:-}" ]; then
    IFS='|' read -r -a TREES <<< "$LINT_SIBLING_TREES"
  else
    # ⛔ THIS LIST WAS HARDCODED HERE UNTIL 2026-08-28 AND IT WAS THE THIRD COPY IN THIS TRUNK.
    # lint.sh C9 skipped herald-wiki as a dead drop, CLAUDE.md called it a DEAD DROP, and BOTH
    # this list and scripts/trunk-roster.tsv called it a delivery target. Three lists, two
    # answers, one tree. ⭐ The roster built on 08-28 to reconcile the courier list against the
    # DISK never reconciled it against the OTHER COURIER LISTS -- and the hand-courier followed
    # the roster, depositing into a mailbox with a do-not-deposit sign in it.
    # ✅ THE FIX IS DELETION, NOT AGREEMENT: derive from the one roster, so there is nothing left
    # to disagree with. A duplicated list can be reconciled; a single list cannot drift.
    local roster="${LINT_ROSTER:-scripts/trunk-roster.tsv}" dir disp cand
    if [ ! -f "$roster" ]; then
      echo "UNKNOWN [relay] roster absent at $roster -- no derived tree list exists; refusing to act." >&2
      TREES=(); return 1
    fi
    TREES=()
    while IFS=$'	' read -r dir disp _rest; do
      case "$dir" in ''|'#'*) continue ;; esac
      [ "$disp" = "DELIVER" ] || continue
      # nested-repo trunks keep exchange/ one level down, under a slugged directory name
      for cand in "${LINT_TRUNK_ROOT:-G:/My Drive/Claude}/$dir"                   "${LINT_TRUNK_ROOT:-G:/My Drive/Claude}/$dir/$(printf '%s' "$dir" | tr 'A-Z ' 'a-z-')"; do
        [ -d "$cand/exchange/inbound" ] && { TREES+=("$cand"); break; }
      done
    done < "$roster"
    if [ "${#TREES[@]}" -eq 0 ]; then
      echo "UNKNOWN [relay] roster yielded ZERO delivery trees -- an empty population is not a clean one; refusing to act." >&2
      return 1
    fi
  fi
}

# Run lint and hand back ONLY C9's UNDELIVERED lines.
# ⛔ The exit code is read from lint DIRECTLY, never off the end of a pipe -- a pipe is a
# summariser and a summariser can launder a status (this trunk published exactly that error
# on 2026-08-24). lint exits 1 whenever ANY check fails, so a non-zero code here is expected
# and is NOT treated as an error; what we refuse to run on is lint being unable to run at all.
collect() {
    LINT_OUT=$(bash scripts/lint.sh 2>&1)
    LINT_RC=$?
    if [ "$LINT_RC" -ge 124 ]; then
        echo "UNKNOWN [relay] lint COULD NOT RUN (rc=$LINT_RC). No delivery list exists; refusing to act."
        return 2
    fi
    printf '%s\n' "$LINT_OUT" | grep '^  UNDELIVERED '
    return 0
}

relay() {
  local apply="$1" line b miss t base n_abs=0 n_unk=0 n_done=0 n_fail=0 rc=0
  # ⛔ THE SOURCE DIRECTORY IS THE ONE C9 GRADED, NOT A HARDCODED PATH. The first draft of this
  # script hardcoded exchange/outbox while C9 read $LINT_OUTBOX, so under the selftest the
  # reporter and the actuator were looking at two different directories -- and S2 caught it.
  # A relay that delivers from a different population than the alarm inspected is worse than
  # no relay: it would deliver the wrong file under exactly the name the alarm cleared.
  local src="${LINT_OUTBOX:-exchange/outbox}"
  trees_from_env
  local list
  list=$(collect); rc=$?
  [ "$rc" -eq 2 ] && { printf '%s\n' "$list"; return 2; }
  if [ -z "$list" ]; then
    echo "RELAY: nothing to deliver -- C9 reports no ABSENT letter. (This is a claim about C9's"
    echo "RELAY: population, not about the outbox: pre-epoch and staged: letters are never graded.)"
    return 0
  fi
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    b="${line#  UNDELIVERED }"; b="${b%% --*}"
    miss="${line#*--}"
    for t in "${TREES[@]}"; do
      base=$(basename "$t")
      case "$miss" in
        *"$base=UNREACHABLE"*)
          n_unk=$((n_unk+1))
          echo "  SKIP      $b -> $base : UNREACHABLE. UNKNOWN is not a licence to write."
          continue ;;
        *"$base=ABSENT"*) ;;
        *) continue ;;
      esac
      # ⛔ HERALD'S FINDING, 2026-08-24, APPLIED THE HOUR IT ARRIVED: AN ACTUATOR WIRED STRAIGHT
      # TO AN ALARM INHERITS EVERY FALSE POSITIVE THE ALARM HAS. Herald's dry run produced one
      # WOULD-SEND for a letter that HAD arrived at CFL on 08-14 -- re-filed by the receiver under
      # a replaced prefix, which its exact-name matcher could not see. C9 matches exact basenames
      # too, so this relay would have re-delivered a duplicate under the original name.
      # ⭐ `[measured 2026-08-24, 63 outbox letters x 3 trees]` NO receiver of ours currently
      # re-files: 0 renamed-but-present copies. That is a property of OUR RECEIVERS, not of our
      # detector -- the blind spot is latent here, not absent. So the guard ships anyway.
      # ⛔ It REFUSES rather than delivering: a substring match might be the same letter re-filed,
      # or a different letter whose name contains this one. Both are UNKNOWN, and UNKNOWN is not a
      # licence to write.
      if [ -d "$t/exchange/inbound" ]; then
        near=$(ls -1 "$t/exchange/inbound" 2>/dev/null | grep -F "$b" | head -1)
        if [ -n "$near" ]; then
          echo "  REFUSED   $b -> $base : a RENAMED copy may already be there ($near)."
          echo "            The alarm matches exact names and cannot see a re-file. Resolve by hand."
          n_unk=$((n_unk+1)); continue
        fi
      fi
      n_abs=$((n_abs+1))
      if [ "$apply" != "yes" ]; then
        echo "  WOULD-COPY $b -> $t/exchange/inbound/"
        continue
      fi
      if [ ! -d "$t/exchange/inbound" ]; then
        echo "  FAILED    $b -> $base : no exchange/inbound. NOT created -- a write that makes its own"
        echo "            destination is indistinguishable from a delivery."
        n_fail=$((n_fail+1)); continue
      fi
      if cp "$src/$b" "$t/exchange/inbound/$b" 2>/dev/null \
         && cmp -s "$src/$b" "$t/exchange/inbound/$b"; then
        echo "  DELIVERED $b -> $base (cmp clean)"
        n_done=$((n_done+1))
      else
        echo "  FAILED    $b -> $base : copy or cmp failed"
        n_fail=$((n_fail+1))
      fi
    done
  done <<< "$list"
  if [ "$apply" != "yes" ]; then
    echo "RELAY DRY RUN: $n_abs deliverable, $n_unk skipped (unreachable or refused-as-possible-refile). Nothing written. Re-run with --apply."
  else
    echo "RELAY APPLIED: $n_done delivered cmp-clean, $n_fail failed, $n_unk skipped (unreachable or refused-as-possible-refile)."
  fi
  [ "$n_fail" -gt 0 ] && return 1
  return 0
}

if [ "$MODE" = "--selftest" ]; then
  rc=0
  OUT_D=$(mktemp -d); TREE_A=$(mktemp -d); DARK=$(mktemp -d)
  mkdir -p "$TREE_A/exchange/inbound"
  printf 'canary body\n' > "$OUT_D/pro-to-all-RELAY-CANARY-2026-08-18.md"

  # S1: DRY RUN NEVER WRITES. The most important property; asserted before anything else.
  O=$(LINT_OUTBOX="$OUT_D" LINT_SIBLING_TREES="$TREE_A" bash scripts/relay.sh 2>&1)
  case "$O" in *"WOULD-COPY"*) ;; *) echo "SELFTEST BROKEN: S1 dry run found nothing to deliver"; rc=3;; esac
  if [ -n "$(ls -A "$TREE_A/exchange/inbound")" ]; then echo "SELFTEST BROKEN: S1 DRY RUN WROTE A FILE"; rc=3; fi

  # S2: --apply delivers, and the copy is cmp-verified at the peer path.
  O=$(LINT_OUTBOX="$OUT_D" LINT_SIBLING_TREES="$TREE_A" bash scripts/relay.sh --apply 2>&1)
  case "$O" in *"DELIVERED"*"cmp clean"*) ;; *) echo "SELFTEST BROKEN: S2 --apply did not deliver"; rc=3;; esac
  [ -f "$TREE_A/exchange/inbound/pro-to-all-RELAY-CANARY-2026-08-18.md" ] \
    || { echo "SELFTEST BROKEN: S2 no file at the peer path"; rc=3; }

  # S3: IDEMPOTENT. Re-running after delivery must find nothing -- C9 no longer reports it.
  #     (The idempotent-consumer half of the outbox pattern; without it a relay re-delivers forever.)
  O=$(LINT_OUTBOX="$OUT_D" LINT_SIBLING_TREES="$TREE_A" bash scripts/relay.sh 2>&1)
  case "$O" in *"nothing to deliver"*) ;; *) echo "SELFTEST BROKEN: S3 relay is not idempotent"; rc=3;; esac

  # S4: THE ONE THAT MATTERS. An UNREACHABLE tree is SKIPPED, never written, never counted done.
  #     Seeded, because every tree this trunk really talks to is reachable -- proving a control
  #     over the population that does not have the defect is a false green [Herald].
  printf 'canary body\n' > "$OUT_D/pro-to-all-RELAY-CANARY2-2026-08-18.md"
  O=$(LINT_OUTBOX="$OUT_D" LINT_SIBLING_TREES="$TREE_A|$DARK" bash scripts/relay.sh --apply 2>&1)
  case "$O" in *"UNREACHABLE. UNKNOWN is not a licence to write"*) ;; *) echo "SELFTEST BROKEN: S4 unreachable tree not skipped"; rc=3;; esac
  if [ -e "$DARK/exchange" ]; then echo "SELFTEST BROKEN: S4 RELAY CREATED ITS OWN DESTINATION"; rc=3; fi

  # S5: a lint that CANNOT RUN yields UNKNOWN and NO delivery -- not an empty list read as clean.
  D5=$(mktemp -d); mkdir -p "$D5/scripts"
  printf '#!/usr/bin/env bash\nexit 127\n' > "$D5/scripts/lint.sh"
  cp scripts/relay.sh "$D5/scripts/relay.sh"
  O=$(cd "$D5" && bash scripts/relay.sh 2>&1)
  case "$O" in *"UNKNOWN [relay] lint COULD NOT RUN"*) ;; *) echo "SELFTEST BROKEN: S5 unrunnable lint did not yield UNKNOWN"; rc=3;; esac
  case "$O" in *"nothing to deliver"*) echo "SELFTEST BROKEN: S5 unrunnable lint reported as nothing-to-deliver"; rc=3;; esac
  rm -rf "$D5"

  # S6: HERALD'S FALSE-POSITIVE CLASS. A receiver that RE-FILED the letter under a longer name
  #     must produce REFUSED, never a duplicate delivery. Seeded, because no receiver of ours
  #     currently re-files -- proving a control over the population that lacks the defect is a
  #     false green [Herald], and this control exists precisely for a population we do not have.
  OUT_E=$(mktemp -d); TREE_E=$(mktemp -d)
  mkdir -p "$TREE_E/exchange/inbound"
  printf 'canary body
' > "$OUT_E/pro-to-all-RELAY-CANARY3-2026-08-18.md"
  printf 'canary body
' > "$TREE_E/exchange/inbound/INBOUND-FROM-PRO-pro-to-all-RELAY-CANARY3-2026-08-18.md"
  O=$(LINT_OUTBOX="$OUT_E" LINT_SIBLING_TREES="$TREE_E" bash scripts/relay.sh --apply 2>&1)
  case "$O" in *"REFUSED"*"RENAMED copy may already be there"*) ;; *) echo "SELFTEST BROKEN: S6 re-filed letter was not refused"; rc=3;; esac
  [ -f "$TREE_E/exchange/inbound/pro-to-all-RELAY-CANARY3-2026-08-18.md" ]     && { echo "SELFTEST BROKEN: S6 DELIVERED A DUPLICATE OVER A RE-FILED LETTER"; rc=3; }
  rm -rf "$OUT_E" "$TREE_E"

  rm -rf "$OUT_D" "$TREE_A" "$DARK"
  if [ $rc -eq 0 ]; then
    echo "SELFTEST: S1 dry-run-writes-nothing / S2 apply-delivers-cmp-clean / S3 idempotent / S4 unreachable-is-skipped-and-no-destination-created / S5 unrunnable-lint-is-UNKNOWN-not-clean / S6 re-filed-letter-is-REFUSED-not-duplicated (6/6 PASS)"
  fi
  echo "⚠️  BOUND 1 -- FAILABILITY, STATED HONESTLY RATHER THAN CLAIMED. S2 and S4 have DEMONSTRATED"
  echo "⚠️  failures: S2 went red on a real defect in this script (the actuator read a different"
  echo "⚠️  directory than the alarm), and S4 runs against a SEEDED unreachable tree. S1, S3 and S5"
  echo "⚠️  are asserted and have never been observed red. 'Proven failable' is NOT claimed for them."
  echo "⚠️  S6 runs against a SEEDED re-file; no receiver of ours actually re-files today."
  echo "⚠️  BOUND 2 -- all fixtures are small, clean and built by this script. Per Soul's SIGPIPE"
  echo "⚠️  finding, a green selftest is evidence about the TEST'S INPUT, not about the code. This is"
  echo "⚠️  a mutation score over 5 hand-picked mutants, not over a generated population."
  exit $rc
fi

case "$MODE" in
  --apply) relay yes ;;
  ""|--dry-run) relay no ;;
  *) echo "usage: scripts/relay.sh [--apply|--dry-run|--selftest]"; exit 2 ;;
esac
