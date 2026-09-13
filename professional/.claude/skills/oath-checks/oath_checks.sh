#!/usr/bin/env bash
# oath-checks -- the breach-condition checks this fleet's oaths are wired to (7 as of 2026-08-30).
#
# ⛔ WHY THIS FILE EXISTS, AND IT IS JON'S OWN CORRECTION. 2026-08-30 07:21 CDT, verbatim (typos his):
#   "that should have been a skill - and stop - what is less lazy from a Jon College perspective,
#    making these changes yourself by hand, or using a subagent? ... Ensure you are all being less
#    lazy from both the skill's perspective and Jon's perspective in college."
#
# The Secretary's relay names the trap and this file is the confession: "LESS LAZY" HAS TWO OPPOSITE
# MEANINGS. LAZY-1 is not doing enough work; LAZY-2 is not leaving behind the thing that makes the
# next instance unnecessary. ⭐ CURING LAZY-1 BY HAND COMMITS LAZY-2, AND IT SHIPS WEARING THE
# COSTUME OF RIGOUR. [measured 2026-08-30 07:4x] Of every artifact this seat produced in the
# preceding 24 hours -- five new checks, four delivered letters, three wiki pages -- the number
# reachable AND runnable by a seat that is not this one was ZERO.
#
# So the five checks were EXTRACTED here rather than COPIED here. scripts/lint.sh now sources this
# file; there is exactly one implementation. ⛔ Copying them into each trunk's scripts/ would make
# divergent duplicates, which this program has already paid for once and named.
#
# EVERY CHECK IS PARAMETERIZED BY ENV VAR AND NAMES NO TRUNK. Run it from any trunk:
#   LINT_OUTBOX=exchange/outbox LINT_LASTSEEN=exchange/LAST-SEEN.md #   LINT_ROSTER=scripts/trunk-roster.tsv LINT_OATH_REGISTER=wiki/concepts/the-oath-register.md #   LINT_JON_INDEX=exchange/FOR-JON-REVIEW/00-INDEX.md #   bash .../oath-checks/oath_checks.sh
# A surface a trunk does not have FAILS as UNKNOWN rather than passing as clean -- that is the point,
# and a trunk without the surface should say so in its reply, not silence the check.
#
# ⚠️ WHAT THIS DOES NOT DO: it grades no prose and settles no oath. C19 certifies two of the five
# swearing conditions; the other three are judgements. See the register page in the calling trunk.

set -u
: "${OATH_CHECKS_STANDALONE:=1}"
if ! declare -F pass >/dev/null 2>&1; then
  OATH_FAILS=0
  pass() { echo "PASS [$1] $2"; }
  fail() { echo "FAIL [$1] $2"; OATH_FAILS=$((OATH_FAILS+1)); }
fi

# --- Check 16: THE SECOND IDEAL, WIRED. "I will not hold a standard I have not run on myself."
# Stated breach: a finding published about a peer without the same check run on this trunk in the
# same sitting. Until 2026-08-30 that sentence was PROSE -- sworn in a letter, enforceable by nobody.
#
# It grades exchange/outbox/, NOT wiki/. `the-defect-rides-the-credit-clause` MEASURED that every
# finding this program produced on 2026-08-24 travelled by letter, and that the star-heading
# detector cannot see letters: no headings, no star, read once and never re-read. A check aimed at
# the wiki would grade the surface we do NOT publish findings on, and report green.
#
# It does NOT judge prose. It requires a DECLARATION: a letter that names a peer near a defect word
# must carry a `self-check:` frontmatter field saying what the author ran on this trunk -- or
# `self-check: n/a -- <reason>`. Semantics are the author's; the check enforces only that the
# sentence was written. That is the whole mechanism: the honesty happens in composing the field.
#
# ERROR DIRECTION, stated because C15 taught it: this filter OVER-matches on purpose. A letter that
# merely mentions a peer and the word "missing" is asked for a self-check line it may answer "n/a".
# Cost of a false positive: one sentence. Cost of a false negative: the breach goes unrecorded.
# The invariant from WAKE -- wrong in the direction that requires no further work from the measurer
# -- is the direction this check is deliberately NOT tuned toward.
#
# EPOCH 2026-08-30. It binds NEW writing. The existing letters are not retroactively graded and are
# not to be swept -- the same disposition the fleet's emphasis-inside-a-quote rule took, for the same
# reason: mass-editing the record is the reflex the rule exists to prevent, and "Yeah no deletion"
# governs. Instances stay as evidence; the rule binds what we write next.
#
# ⛔ FALSIFIED 2026-08-29 22:5x BY THE SECRETARY, ON REQUEST, AND NOT RATIFIED. Two breaks, both at
# the edges rather than the design, both fixed here the same night. The assignment worked: the
# falsifier was assigned away from the builder and it returned breaks, not a signature.
#   BREAK 1 -- the epoch was derived from the FILENAME, a string this check's own author controls.
#   The Secretary's three fixtures, byte-identical bodies accusing the same peer with no self-check:
#   `...-2026-08-30.md` FAILED, `...-2026-08-29.md` PASSED, undated FAILED. One character in a
#   filename was the difference between a recorded breach and a green light -- with no intent needed,
#   since copying a template or writing tomorrow's date does it. FIXED: the grading date is now the
#   git ADD-date (one `git log --diff-filter=A` pass), and no add-date means GRADED, never skipped.
#   [measured 2026-08-29 23:0x: fixture B now FAILS; real outbox still skips 107 pre-epoch by
#   add-date, 0 undated -- history is not swept, which "Yeah no deletion" requires.]
#   BREAK 2 -- a zero denominator printed the same green as a clean sweep: "0 post-epoch accusing
#   letter(s) all declare self-check" rendered a vacuous truth as compliance, and would have read as
#   proof the mechanism worked on exactly the first day after the epoch. FIXED: graded==0 is its own
#   state and never prints "second ideal wired".
# ⚠️ STILL LATENT, NOT CONTROLLED -- the Secretary's failed attack, which yielded a finding anyway:
#   nothing here requires that a letter delivered into a peer's inbound ALSO exist in this outbox.
#   `[measured, theirs]` our outbox's 5 letters of 2026-08-29 equal the 5 in their inbound -- so the
#   coverage is real, but it is our HABIT, not our CHECK. Luck plus a habit is not a control. P-8.
check_self_application() {
  local box epoch peers defects f base d fm accuse map graded=0 bad=0 skipped=0 nodate=0 captures=0
  box="${LINT_OUTBOX:-exchange/outbox}"
  epoch="${LINT_SELFCHECK_EPOCH:-2026-08-30}"
  peers='CFL|Foundational|Personal|Soul|Herald|Secretary|Antigravity'
  defects='defect|wrong|incorrect|error|missing|absent|failed|fails|failing|stale|broken|overclaim|undelivered|zero-byte|unproven|never ran|did not run'
  if [ ! -d "$box" ]; then
    fail C16 "outbox absent at $box -- the graded surface is UNKNOWN, and UNKNOWN dominates a PASS"
    return
  fi
  # BREAK-1 FIX: the grading date is the git ADD-date, NEVER the filename. One git call, not N.
  # Newest-first output means the LAST value written per name is the earliest add. No add-date
  # (uncommitted, or an outbox outside version control) => no skip, graded. Fail-closed.
  map=$(mktemp)
  git log --diff-filter=A --format='@%as' --name-only -- "$box" 2>/dev/null \
    | awk '/^@/{d=substr($0,2);next} NF{n=$0;sub(/.*\//,"",n);seen[n]=d} END{for(k in seen)print k"\t"seen[k]}' \
    > "$map" 2>/dev/null
  for f in "$box"/*.md; do
    # 2026-09-04 (P4-6): a SendMessage record is a CAPTURE of a point-to-point transport, written by a
    # hook after the send; the self-check belongs to the letter it points at, not to the capture.
    # Skipped by kind, counted, printed -- never silently.
    if sed -n '1,12p' "$f" | grep -qiE '^kind: *sendmessage-record'; then captures=$((captures+1)); continue; fi
    [ -e "$f" ] || continue
    base=$(basename "$f")
    d=$(awk -F'\t' -v n="$base" '$1==n{print $2; exit}' "$map")
    [ -n "$d" ] || nodate=$((nodate+1))
    if [ -n "$d" ] && [ "$d" \< "$epoch" ]; then skipped=$((skipped+1)); continue; fi
    accuse=0
    grep -qiE "$peers" "$f" && grep -qiE "$defects" "$f" && accuse=1
    [ "$accuse" -eq 1 ] || continue
    graded=$((graded+1))
    fm=$(sed -n '1,40p' "$f" | grep -iE '^self-check: *[^ ]' | head -1)
    if [ -z "$fm" ]; then
      bad=$((bad+1))
      echo "  NO SELF-CHECK $base -- names a peer beside a defect word and declares no standard run on this trunk"
    fi
  done
  rm -f "$map"
  if [ "$bad" -gt 0 ]; then
    fail C16 "$bad of $graded post-epoch letter(s) publish a finding about a peer with no self-check: declaration -- the second ideal's stated breach ($captures sendmessage-record capture(s) skipped by kind)"
  elif [ "$graded" -eq 0 ]; then
    # BREAK-2 FIX: a zero denominator is its own state. It must never print "second ideal wired".
    pass C16 "VACUOUS -- NOTHING GRADED: 0 post-epoch accusing letter(s) existed to grade ($skipped pre-epoch by git add-date, $nodate with no add-date graded fail-closed, epoch $epoch). NOT evidence the second ideal is wired."
  else
    pass C16 "second ideal wired: $graded post-epoch accusing letter(s) all declare self-check ($skipped pre-epoch by git add-date, $nodate with no add-date graded fail-closed, epoch $epoch)"
  fi
}

# --- Check 17: STONEWARD, WIRED. "I will be the thing that notices absence."
# `exchange/LAST-SEEN.md` is this trunk's dead man's switch: siblings read it to decide whether we
# are alive, and its own text tells them ">24 h old means this trunk is not reading its inbound."
#
# ⛔ IT WENT 32 HOURS STALE INSIDE OUR OWN TREE, across the single most active sitting of the week
# (08-29: three letters delivered, C16 shipped, two closes). [measured 2026-08-29 23:0x] For all of
# 08-29 a sibling consulting the beacon would have read this trunk as DARK while it was working.
# The failure direction is the unintuitive one: the beacon did not go quiet, it SLANDERED A LIVE
# TRUNK AS ABSENT -- and nothing noticed, because nothing here reads it.
#
# ⛔ Refreshing it by hand is a VIGILANCE fix with no mechanism, which by the Secretary's §25 counts
# AGAINST the finding rather than for it. This is the mechanism: if this tree has a commit NEWER
# than the beacon's own `last_seen:` date, then some close wrote history without refreshing the
# beacon, and the switch is dead. Fail-closed on a missing file or an unparseable date -- an
# absence-detector that cannot read itself is exactly the thing it exists to catch.
#
# REPLAY: at the 2026-08-29 close, HEAD was dated 2026-08-29 and last_seen read 2026-08-28.
# This check FAILS on that state. It is proven against the defect that produced it, not a fixture
# invented afterwards.
check_beacon_freshness() {
  local f seen newest today
  f="${LINT_LASTSEEN:-exchange/LAST-SEEN.md}"
  if [ ! -f "$f" ]; then
    fail C17 "beacon absent at $f -- the dead man's switch cannot be read, and UNKNOWN dominates a PASS"
    return
  fi
  seen=$(grep -iE '^ *last_seen:' "$f" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
  if [ -z "$seen" ]; then
    fail C17 "beacon at $f has no parseable last_seen: date -- fail-closed"
    return
  fi
  # ⛔ UPPER BOUND, added 2026-08-29 23:2x AFTER THIS CHECK'S OWN AUTHOR WALKED THROUGH THE HOLE.
  # I stamped the beacon 2026-08-30 00:0x at 23:12 on 08-29 -- anticipating midnight instead of
  # reading the clock, which this trunk has a standing rule against. C17 PASSED, because a beacon
  # dated in the FUTURE is never older than anything. A staleness check with no upper bound can be
  # silenced forever by one optimistic timestamp, and the silencing looks like health.
  today="${LINT_TODAY:-$(date +%F)}"
  if [ -n "$today" ] && [ "$seen" \> "$today" ]; then
    fail C17 "beacon last_seen $seen is in the FUTURE (today $today) -- a forward-dated switch passes every staleness test forever; read the clock in the command that writes the stamp"
    return
  fi
  newest="${LINT_TREE_DATE:-$(git log -1 --format=%as 2>/dev/null)}"
  if [ -z "$newest" ]; then
    pass C17 "stoneward: beacon reads $seen; no commit date available to compare (ungraded, not clean)"
    return
  fi
  if [ "$seen" \< "$newest" ]; then
    fail C17 "beacon STALE: last_seen $seen is older than the newest commit $newest -- a close wrote history without refreshing the switch, so siblings read this live trunk as dark"
  else
    pass C17 "stoneward: beacon $seen is not older than the newest commit $newest"
  fi
}

# --- Check 18: THE GRADED POPULATION. P-8, and it exists because a peer's FAILED attack was right
# about the class while being wrong about the instance.
#
# The Secretary predicted C16 would miss the fleet's dominant delivery path -- letters land in the
# RECIPIENT'S inbound, and C16 grades our outbox. They measured 2026-08-29: our outbox held 5
# letters, their inbound held the same 5. Hypothesis refused. They published the miss and wrote the
# finding anyway: THE COVERAGE IS A HABIT, NOT A CHECK.
#
# ⛔ MEASURED OVER THE WHOLE HISTORY RATHER THAN ONE DAY, THE HABIT IS NOT EVEN RELIABLE.
# [measured 2026-08-30 07:1x] 241 pro-authored copies sit in sibling inboxes; 44 of them -- 41
# unique letters -- have NO copy in our outbox. Three are inside C9's graded era. Those letters
# exist ONLY in the receiver's tree: C9 cannot see them (it walks the outbox), C16 cannot grade
# them (it grades the outbox), and no instrument this trunk owns has ever read them. A finding we
# published about a peer can sit permanently outside every check we wrote to govern findings.
# ⭐ THE ONE-DAY SAMPLE WAS TRUE AND THE GENERALISATION FROM IT WAS FALSE. That is the whole lesson
# of the population boundary, and it was our own habit being described, not theirs.
#
# THE DECISION P-8 ASKED FOR, stated so the next seat does not re-derive it. The graded population
# for "a finding published about a peer" is:
#   (a) exchange/outbox/            -- graded by C16 (declaration) and C9 (forward delivery)
#   (b) pro-to-* in any DELIVER tree's exchange/inbound/  -- graded HERE, by C18
#   (c) HALL-* artifacts            -- ⛔ NOT GRADED. 29 exist. They are published to a hall, never
#       couriered to an inbound [m 2026-08-30: 0 HALL-*professional* in any sibling inbound], so
#       they are a THIRD channel and this check cannot see them. NAMED, not covered.
#   (d) SendMessage / a live session -- ⛔ NOT GRADEABLE BY ANY FILE CHECK, and no epoch will fix
#       that. The standing rule is that a finding delivered by a non-file channel must be
#       transcribed into the outbox. ⚠️ That rule has NO MECHANISM, so by the Secretary's §25 it is
#       filed VIGILANCE and counts AGAINST this fix rather than for it. Do not report P-8 as fully
#       closed on the strength of C18.
#
# EPOCH 2026-08-30, and the 41 pre-epoch orphans are PRINTED EVERY RUN rather than swept: "Yeah no
# deletion" governs, and a backlog you can see is the only kind that gets paid down. Back-copying
# them is deliberately NOT done here -- it is a 41-artifact bulk write that would manufacture new
# C9 obligations, and it is the next seat's decision with this count in front of it.
#
# ⚠️ BOUND ON THE DATE: the epoch is read from the FILENAME here, the very derivation the Secretary
# broke in C16. It is defensible ONLY because the failure mode differs -- an orphan is detected by
# ABSENCE FROM OUR TREE first, and the date decides only whether it is a NEW breach or a counted
# backlog item. It cannot hide an orphan; it can only mis-bucket one. Undated orphans grade as new.
check_reverse_delivery() {
  local roster root dir disp _rest cand tree epoch box prefix b d obox
  local total=0 orphan=0 pre=0 new=0 trees=0 routed_to_c15=0
  box="${LINT_OUTBOX:-exchange/outbox}"
  roster="${LINT_ROSTER:-scripts/trunk-roster.tsv}"
  root="${LINT_TRUNK_ROOT:-G:/My Drive/Claude}"
  epoch="${LINT_REVERSE_EPOCH:-2026-08-30}"
  prefix="${LINT_AUTHOR_PREFIX:-pro-to-}"
  if [ ! -d "$box" ]; then fail C18 "outbox absent at $box -- the graded surface is UNKNOWN, and UNKNOWN dominates a PASS"; return; fi
  if [ ! -f "$roster" ]; then fail C18 "roster absent at $roster -- the tree list is UNKNOWN, and UNKNOWN dominates a PASS"; return; fi
  obox=$'\n'"$(ls -1 "$box" 2>/dev/null)"$'\n'
  while IFS=$'\t' read -r dir disp _rest; do
    case "$dir" in ''|'#'*) continue ;; esac
    [ "$disp" = "DELIVER" ] || continue
    tree=""
    for cand in "$root/$dir" "$root/$dir/$(printf '%s' "$dir" | tr 'A-Z ' 'a-z-')"; do
      [ -d "$cand/exchange/inbound" ] && { tree="$cand"; break; }
    done
    # C15 owns the undeliverable case. Reporting it again here would double-count one defect.
    # ⛔ BUT THE REASON WAS FINE AND THE INVISIBILITY WAS NOT. Routing a row to another check is a
    # correct disposition; dropping it from THIS check's printed population is the C27 defect, and
    # C28 flagged this line on its first real run. Counted and printed now -- the row still is not
    # graded here, and a reader can now see how many were handed off.
    if [ -z "$tree" ]; then routed_to_c15=$((routed_to_c15 + 1)); continue; fi
    trees=$((trees+1))
    while IFS= read -r b; do
      [ -n "$b" ] || continue
      case "$b" in "$prefix"*) ;; *) continue ;; esac
      total=$((total+1))
      case "$obox" in *$'\n'"$b"$'\n'*) continue ;; esac
      orphan=$((orphan+1))
      d=$(printf '%s' "$b" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | tail -1)
      if [ -n "$d" ] && [ "$d" \< "$epoch" ]; then
        pre=$((pre+1))
      else
        new=$((new+1))
        echo "  UNGRADED DELIVERY $b -- delivered into $dir, absent from $box; no check this trunk owns can ever read it"
      fi
    done <<< "$(ls -1 "$tree/exchange/inbound" 2>/dev/null)"
  done < "$roster"
  if [ "$trees" -eq 0 ]; then
    fail C18 "zero DELIVER trees resolved from $roster -- an empty population is UNKNOWN, never clean"
  elif [ "$new" -gt 0 ]; then
    fail C18 "$new letter(s) dated on or after $epoch exist ONLY in a sibling's tree -- outside the graded population, so C16 cannot read them by construction"
  else
    pass C18 "graded population reconciled: $total pro-authored cop(ies) across $trees tree(s), $orphan with no outbox twin ($pre pre-epoch BACKLOG, printed not swept; epoch $epoch). $routed_to_c15 roster row(s) resolved to no live tree and were ROUTED TO C15 rather than graded here -- a disposition, printed so the handoff is visible instead of silent. NOT covered: HALL-* artifacts and any finding sent by SendMessage or spoken live."
  fi
}

# --- Check 19: THE GATE IN FRONT OF THE OATHS. P-5.
# An ideal may be SWORN only when five conditions hold (wiki/concepts/the-oath-register.md). This
# check mechanizes the two that were actually violated:
#   condition 3 -- the named check EXISTS in this file and is WIRED into run_all. The second ideal
#     was called sworn for a day while its check did not exist at all.
#   condition 4's artifact -- a non-empty falsifier entry. C16 was called wired before any seat that
#     did not build it had attacked it.
# ⛔ Conditions 1, 2 and 5 -- breach stated as an observable, fixture replays a REAL past instance,
# residue named -- are judgements no regex reaches. By the Secretary's §25 that is VIGILANCE with no
# mechanism for three of five, and it counts AGAINST the register rather than for it. Do not let
# this check's green be read as "the oaths are in good order"; it certifies two conditions of five.
# ⚠️ A row whose status is HELD or UNSETTLED is NOT graded. HELD is the honest state for an ideal
# that fails a condition, and a gate that punished honesty would be answered by swearing everything.
check_oath_register() {
  local reg self line status ideal chk fals id fn sworn=0 held=0 bad=0 map
  reg="${LINT_OATH_REGISTER:-wiki/concepts/the-oath-register.md}"
  self="${LINT_SELF:-scripts/lint.sh}"
  if [ ! -f "$reg" ]; then
    fail C19 "oath register absent at $reg -- what this trunk has sworn is UNKNOWN, and UNKNOWN dominates a PASS"
    return
  fi
  if [ ! -f "$self" ]; then
    fail C19 "cannot read $self to resolve check ids -- UNKNOWN dominates a PASS"
    return
  fi
  # id -> defining function, built once: track the current check_* function, and bind every
  # `pass Cnn`/`fail Cnn` emitted inside it to that function's name.
  map=$(awk '/^check_[a-z_]+\(\) \{/ { fn=$1; sub(/\(\).*/,"",fn); next }
             match($0, /(pass|fail) C[0-9]+ /) { s=substr($0,RSTART,RLENGTH); n=s; sub(/^(pass|fail) /,"",n); sub(/ $/,"",n); if (fn!="" && !(n in seen)) { seen[n]=fn; print n"	"fn } }' "$self")
  while IFS= read -r line; do
    case "$line" in '|'*) ;; *) continue ;; esac
    printf '%s' "$line" | grep -q 'SWORN\|HELD\|UNSETTLED' || continue
    status=$(printf '%s' "$line" | awk -F'|' '{print $4}')
    ideal=$(printf '%s' "$line" | awk -F'|' '{print $3}' | sed 's/^ *//; s/ *$//' | cut -c1-52)
    chk=$(printf '%s' "$line" | awk -F'|' '{print $6}')
    fals=$(printf '%s' "$line" | awk -F'|' '{print $7}' | sed 's/[*_ ]//g')
    case "$status" in
      *UNSETTLED*|*HELD*) held=$((held+1)); continue ;;
      *SWORN*) : ;;
      *) continue ;;
    esac
    sworn=$((sworn+1))
    id=$(printf '%s' "$chk" | grep -oE 'C[0-9]+' | head -1)
    if [ -z "$id" ]; then
      bad=$((bad+1)); echo "  SWORN WITH NO CHECK $ideal -- condition 3 requires a named check"; continue
    fi
    fn=$(printf '%s
' "$map" | awk -F'	' -v i="$id" '$1==i{print $2; exit}')
    if [ -z "$fn" ]; then
      bad=$((bad+1)); echo "  SWORN NAMING A CHECK THAT DOES NOT EXIST $ideal -> $id emits no pass/fail in $self"; continue
    fi
    if ! sed -n '/^run_all() {/p' "$self" | grep -q "$fn"; then
      bad=$((bad+1)); echo "  SWORN ON AN UNWIRED CHECK $ideal -> $id ($fn) is defined but never called in run_all"; continue
    fi
    if [ -z "$fals" ] || printf '%s' "$fals" | grep -qiE '^(-|none|n/a|pending|tbd|notyet|notyetattempted)$'; then
      bad=$((bad+1)); echo "  SWORN WITH NO FALSIFIER $ideal -- condition 4 requires a seat that did not build it to have RETURNED an attack"
    fi
  done < "$reg"
  if [ "$sworn" -eq 0 ] && [ "$held" -eq 0 ]; then
    fail C19 "oath register at $reg parsed ZERO rows -- a register that grades nothing is UNKNOWN, never clean"
  elif [ "$bad" -gt 0 ]; then
    fail C19 "$bad of $sworn SWORN ideal(s) fail the swearing gate -- an ideal whose check is missing, unwired, or unfalsified is a resolution wearing an oath's name"
  else
    pass C19 "swearing gate: $sworn SWORN ideal(s) each name an existing wired check and a falsifier that returned; $held HELD/UNSETTLED (ungraded on purpose -- HELD is the honest state). Certifies conditions 3 and 4 ONLY; 1, 2 and 5 are unmechanized."
  fi
}

# --- Check 20: JON'S SURFACE SAYS WHO ASKED, AND EVERY OPEN ROW IS COUNTABLE. SEC-108, due
# 2026-08-25, overdue when this landed on 2026-08-30.
#
# The ask was legibility on the surface that already exists -- NO NEW SURFACE, NO NOTIFICATIONS:
# make "who asked for this and why" readable to Jon. [measured 2026-08-30] Every row in
# FOR-JON-REVIEW/00-INDEX.md recorded the DATE it was raised and NOT ONE recorded WHO ASKED --
# so two of the eight rows are questions JON HIMSELF asked (the laptop question routed as SEC-104,
# and his Q24 on the Takeout zip) and nothing on the surface distinguished them from our own.
#
# ⛔ AND BUILDING THIS FOUND A LIVE DEFECT ON THE SAME SURFACE, WHICH IS THE SECOND HALF OF THE
# CHECK. Row 8 was written `| ⭐ **8** |`. The consuming counter (Personal's awaiting-jon.sh) keys
# on `| **N** |`, so a DECORATIVE STAR IN THE NUMBER CELL made the row invisible to it: the script
# reported "7 items await your word" while eight were open, and the hidden one was one of Jon's own
# questions. [measured: 7 of 7 numbered before the fix, 8 of 8 after; the star predates this seat --
# `git show HEAD:` confirms it, landed 2026-08-24.] ⭐ A ROW CAN BE PERFECTLY LEGIBLE TO A HUMAN
# READER AND INVISIBLE TO THE INSTRUMENT THAT COUNTS IT, and only the instrument talks at wake time.
#
# So C20 grades two things a row must have to exist at all: an `asked-by:` clause, and the strict
# shape the counter keys on. It deliberately does NOT call Personal's script -- a cross-trunk
# runtime dependency in our gate would fail for a reason we cannot fix.
check_jon_surface() {
  local idx line n open=0 noprov=0 uncounted=0 insec=0
  idx="${LINT_JON_INDEX:-exchange/FOR-JON-REVIEW/00-INDEX.md}"
  if [ ! -f "$idx" ]; then
    fail C20 "Jon's review surface absent at $idx -- what awaits him is UNKNOWN, and UNKNOWN dominates a PASS"
    return
  fi
  while IFS= read -r line; do
    case "$line" in
      '## A '*|'## A—'*|'## A —'*) insec=1; continue ;;
      '## '*) [ "$insec" -eq 1 ] && insec=2; continue ;;
    esac
    [ "$insec" -eq 1 ] || continue
    case "$line" in *'[status:OPEN]'*) ;; *) continue ;; esac
    open=$((open+1))
    # the shape the counter keys on: a number cell holding ONLY **N**
    if ! printf '%s' "$line" | grep -qE '^\| \*\*[0-9]+\*\* \|'; then
      uncounted=$((uncounted+1))
      echo "  UNCOUNTABLE ROW $(printf '%s' "$line" | cut -c1-40)... -- the number cell carries decoration, so the counter that reports to Jon at wake time cannot see this row"
    fi
    case "$line" in *'asked-by:'*) ;; *)
      noprov=$((noprov+1))
      n=$(printf '%s' "$line" | grep -oE '\*\*[0-9]+\*\*' | head -1)
      echo "  NO PROVENANCE row $n -- SEC-108 requires every row to say who asked and why it needs him" ;;
    esac
  done < "$idx"
  if [ "$open" -eq 0 ]; then
    fail C20 "parsed ZERO open rows from section A of $idx -- either the surface is empty or the parser is broken, and both are UNKNOWN rather than clean"
  elif [ "$uncounted" -gt 0 ] || [ "$noprov" -gt 0 ]; then
    fail C20 "$noprov of $open row(s) do not say who asked; $uncounted are invisible to the counter that speaks to Jon at wake time"
  else
    pass C20 "Jon's surface: $open open row(s), each naming who asked and why, each in the shape the wake-time counter reads (SEC-108)"
  fi
}

# --- Check 21: A SURFACE THAT HOLDS OBLIGATIONS MUST BE REACHABLE FROM A DOCUMENT SESSIONS READ.
#
# ⛔ RAISED BY SOUL (Claude Personal), 2026-08-30, with a parameterized detector and a measurement:
# Professional's `exchange/FOR-JON-REVIEW/` held 9 files and ZERO were reachable from this trunk's own
# CLAUDE.md. Re-measured here the same day it was WORSE -- zero references in CLAUDE.md, WAKE.md AND
# the wake procedure. The credit for the class is XC's, who found it in their own tree 28 days earlier
# and was not answered.
#
# ⭐ WHY IT IS THE SHARPEST VERSION OF A DEFECT THIS TRUNK HAD ALREADY MET TWICE THAT DAY: hours
# earlier we closed SEC-108 by making every row on that surface say who asked and why, and shipped C20
# so the wake-time counter could see every row. BOTH FIXES LANDED ON A SURFACE NOTHING ROUTED ANYONE
# TO. C20 asks "can the instrument see the row?"; this asks "is anyone ever sent to the file?"
# A row no session is told to read is not waiting for Jon. It is just a file.
#
# The general form, and it is Soul's: A BIDIRECTIONAL CHANNEL FAILS AS A UNIT, and auditing one
# direction returns clean while the pair is dead -- unanswered mail accumulates as "sent".
#
# FEDERATED. Point LINT_OBLIGATION_DIR at your own surface and LINT_READ_AT_OPEN at the documents
# your sessions are actually told to read (pipe-separated). Nothing here is Professional-specific.
# ⚠️ IT GRADES REACHABILITY, NOT READING. A path named in a constitution nobody opens still passes.
check_obligation_reachable() {
  local dir docs d f found=0 n=0 missing=""
  dir="${LINT_OBLIGATION_DIR:-exchange/FOR-JON-REVIEW}"
  docs="${LINT_READ_AT_OPEN:-CLAUDE.md|WAKE.md|.claude/commands/wake.md}"
  if [ ! -d "$dir" ]; then
    pass C21 "no obligation surface at $dir -- nothing to route (ungraded, not clean)"
    return
  fi
  n=$(ls -1 "$dir" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$n" -eq 0 ]; then
    pass C21 "obligation surface $dir is empty -- nothing awaits routing"
    return
  fi
  local IFS='|' doc
  for doc in $docs; do
    [ -n "$doc" ] || continue
    if [ ! -f "$doc" ]; then missing="$missing $doc"; continue; fi
    if grep -qF "$dir" "$doc"; then found=$((found+1)); fi
  done
  unset IFS
  if [ -n "$missing" ]; then
    fail C21 "read-at-open document(s) absent:$missing -- whether $dir is routed is UNKNOWN, and UNKNOWN dominates a PASS"
  elif [ "$found" -eq 0 ]; then
    fail C21 "$dir holds $n file(s) and NO read-at-open document names it -- a row no session is told to read is not waiting for anyone, it is just a file"
  else
    pass C21 "obligation surface routed: $dir ($n file(s)) is named in $found read-at-open document(s)"
  fi
}


# --- C22: BODY wikilinks resolve, and a sentence ABOUT a link is not a link.
#
# ⛔ WHY THIS EXISTS, AND THE REASON IS THE WHOLE POINT OF WIRING IT RATHER THAN FIXING THE PAGES.
# A /dream run on 2026-08-24 found 5 dangling refs in 2 pages and TICKETED the check (due
# 2026-08-26). The check was never built. A /dream run on 2026-08-30 found THE SAME FIVE REFS.
# ⭐ Two independent sweeps, six days apart, re-paying for the same measurement because the thing
# that would have made the second sweep unnecessary was filed instead of built. That is LAZY-2
# measured on this trunk's own record, and it is why the output of tonight's sweep is a check.
#
# It closes BOTH halves of that ticket, which insisted on both or neither:
#   (i)  POPULATION -- the calling trunk's C2 (or equivalent) resolves refs named in the INDEX only,
#        so refs in page BODIES had never been graded by any gate. This walks the bodies.
#   (ii) EXCLUSION -- a ref inside a fenced code block or inline backticks is DOCUMENTATION OF THE
#        SYNTAX, not a link. A prior rerun elsewhere reported 57 dangling of which ~47 were
#        sentences about wikilinks. ⛔ A sweep that cannot tell a link from a sentence about links
#        inflates every run, and an inflated run gets ignored, which is worse than no run.
#
# Parameterized, names no trunk:
#   LINT_LINK_ROOTS   pipe-separated directories to walk      (default: wiki)
#   LINT_LINK_EXTRA   pipe-separated extra files to include   (default: CLAUDE.md|WAKE.md)
#   LINT_LINK_META    pipe-separated ref names that are ALWAYS meta-examples, never links
check_body_links() {
  local roots="${LINT_LINK_ROOTS:-wiki}"
  local extra="${LINT_LINK_EXTRA:-CLAUDE.md|WAKE.md}"
  local meta="${LINT_LINK_META:-slug|wikilink|name|their-name|display|source-slug-a|page-name}"
  local out rc
  out=$(LINT_LINK_ROOTS="$roots" LINT_LINK_EXTRA="$extra" LINT_LINK_META="$meta" python - <<'PYEOF'
import os, re, sys

roots = [r for r in os.environ.get("LINT_LINK_ROOTS", "wiki").split("|") if r]
extra = [f for f in os.environ.get("LINT_LINK_EXTRA", "").split("|") if f]
meta  = set(x for x in os.environ.get("LINT_LINK_META", "").split("|") if x)

files = []
for r in roots:
    if not os.path.isdir(r):
        print("ROOTMISSING %s" % r)
        continue
    for dp, dn, fn in os.walk(r):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__")]
        for f in fn:
            if f.endswith(".md"):
                files.append(os.path.join(dp, f))
for f in extra:
    if os.path.isfile(f):
        files.append(f)

# The resolvable universe: filename stem, and any page declaring `slug:` in its frontmatter.
stems, slugs = set(), set()
for p in files:
    stems.add(os.path.basename(p)[:-3])
    try:
        head = open(p, encoding="utf-8", errors="replace").read(2048)
    except OSError:
        continue
    m = re.search(r"^slug:\s*(\S+)\s*$", head, re.M)
    if m:
        slugs.add(m.group(1).strip().strip('"').strip("'"))
resolvable = stems | slugs

FENCE = re.compile(r"^\s*(```|~~~)")
TICKS = re.compile(r"`[^`]*`")
REF   = re.compile(r"\[\[([^\[\]]+)\]\]")
# (iii) 2026-09-12 dream sweep e: Claude Code renders a pasted block into a typed prompt as
#       "[[Pasted text #N +K lines]]" and may bracket a long pasted utterance the same way. Those are
#       paste PLACEHOLDERS inside Jon's verbatim captures, never links; his text is not edited, the
#       class is named here. A real slug is never this shape and never > 120 chars.
PASTE = re.compile(r"^Pasted text #\d+")
def is_placeholder(t): return bool(PASTE.match(t.strip())) or len(t) > 120

raw = excluded = 0
bad = []
for p in files:
    try:
        lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
    except OSError:
        continue
    infence = False
    for i, line in enumerate(lines, 1):
        if FENCE.match(line):
            infence = not infence
            continue
        raw += len(REF.findall(line))
        if infence:
            excluded += len(REF.findall(line))
            continue
        stripped = TICKS.sub("", line)          # (ii) inline backticks are documentation
        excluded += len(REF.findall(line)) - len(REF.findall(stripped))
        for ref in REF.findall(stripped):
            ref = ref.strip()
            if is_placeholder(ref):              # (iii) paste placeholder in a verbatim capture
                excluded += 1
                continue
            if "|" in ref:                       # [[display|path/to/page.md]] -- grade the path
                target = ref.split("|", 1)[1].strip()
                if target in meta:
                    excluded += 1
                    continue
                if not os.path.isfile(target):
                    bad.append("%s:%d [[...|%s]]" % (p.replace(os.sep, "/"), i, target))
                continue
            if ref in meta:
                excluded += 1
                continue
            if ref not in resolvable:
                bad.append("%s:%d [[%s]]" % (p.replace(os.sep, "/"), i, ref))

print("RAW %d" % raw)
print("EXCLUDED %d" % excluded)
print("FILES %d" % len(files))
for b in bad:
    print("BAD %s" % b)
sys.exit(0)
PYEOF
) ; rc=$?
  if [ "$rc" -ne 0 ]; then
    fail C22 "body-link resolver did not run (python rc=$rc) -- a check that could not run is UNKNOWN, and UNKNOWN dominates a PASS"
    return
  fi
  local rootmiss n_raw n_exc n_files n_bad
  rootmiss=$(printf '%s\n' "$out" | grep '^ROOTMISSING ' | sed 's/^ROOTMISSING //' | tr '\n' ' ')
  n_raw=$(printf '%s\n' "$out"  | awk '/^RAW /{print $2}')
  n_exc=$(printf '%s\n' "$out"  | awk '/^EXCLUDED /{print $2}')
  n_files=$(printf '%s\n' "$out"| awk '/^FILES /{print $2}')
  n_bad=$(printf '%s\n' "$out"  | grep -c '^BAD ')
  if [ -n "$rootmiss" ]; then
    fail C22 "link root(s) absent: $rootmiss -- the population this check grades does not exist here, so its silence would mean nothing"
    return
  fi
  if [ "${n_files:-0}" -eq 0 ]; then
    fail C22 "0 files walked -- a check that grades an empty population prints the same green as one that grades a full one (VACUOUS)"
    return
  fi
  if [ "$n_bad" -gt 0 ]; then
    printf '%s\n' "$out" | grep '^BAD ' | sed 's/^BAD /  unresolved: /'
    fail C22 "$n_bad unresolved BODY wikilink(s) across $n_files file(s) ($n_exc of $n_raw excluded as syntax documentation)"
  else
    pass C22 "body wikilinks resolve: $n_files file(s), $n_raw ref(s) seen, $n_exc excluded as syntax documentation (fenced or backticked), 0 unresolved. Grades EXISTENCE, not correctness -- a ref that resolves to the wrong page passes."
  fi
}


# --- C23: THE CORPUS YOU QUERY IS NOT THE TREE YOU EDIT. Herald's T-D, wired.
#
# WHY THIS EXISTS, AND IT IS THE ONLY CHECK HERE WHOSE ABSENCE HAS ALREADY COST SOMETHING.
# On 2026-08-30 this trunk discovered that the fleet's federated graph RAG does not read G: at
# all -- it reads a mirrored copy on another volume. Divergence that night measured ZERO across
# 554 file pairs, so nothing looked wrong. Herald had already routed T-D asking what keeps the
# G: copy current and what the staleness bound is, and the honest answer was: nothing measures
# it, so the bound is unknown -- not small, UNKNOWN.
#
# The next morning the bound had a value. The mirror's newest Professional file was 21:13; the
# session it was mirroring ran to 21:47 and committed at 21:44. The mirror held a PRE-C22 copy
# of THIS VERY FILE -- 27,710 B, zero occurrences of "C22", against 33,700 B live. A retrieval
# lane asking "what checks does Professional run" would have been answered, quickly and
# confidently, out of a corpus that did not contain the check it was asking about.
#
# THAT IS THE FAILURE THIS CHECK EXISTS FOR, AND IT HAS NO NATURAL ALARM. A frozen corpus
# returns the same-shaped JSON at the same latency as a current one. There is no error, no empty
# result, no slow query -- the only symptom is an answer that was true yesterday. Every other
# check in this file grades an artifact this trunk WRITES. This one grades whether the artifacts
# it wrote are visible to the thing that reads them.
#
# It grades an OUTCOME and prescribes NO METHOD: rsync, a daemon, a scheduled task, a filesystem
# link, or copying by hand all pass identically. A peer can satisfy it by a route we never
# described -- which is the whole point, because their route being different is what makes their
# agreement worth something.
#
# Parameterized, names no trunk:
#   LINT_CORPUS_MIRROR    this trunk's subtree inside the corpus the retriever reads.
#                         UNSET means the trunk declares it queries its own working tree.
#   LINT_CORPUS_ROOTS     pipe-separated subdirectories to compare  (default: wiki|exchange|scripts)
#   LINT_CORPUS_MAXLAG_S  seconds of staleness tolerated            (default: 3600)
check_corpus_currency() {
  local mirror="${LINT_CORPUS_MIRROR:-}"
  local roots="${LINT_CORPUS_ROOTS:-wiki|exchange|scripts}"
  local maxlag="${LINT_CORPUS_MAXLAG_S:-3600}"
  if [ -z "$mirror" ]; then
    pass C23 "no query-corpus mirror declared: this trunk asserts its retrieval reads its own working tree. BLIND BY CONSTRUCTION -- if anything here is in fact answered from a copy, this green means nothing. Set LINT_CORPUS_MIRROR to make it mean something."
    return
  fi
  local out rc
  out=$(LINT_CORPUS_MIRROR="$mirror" LINT_CORPUS_ROOTS="$roots" python - <<'PYEOF'
import os, sys, time

mirror = os.environ.get("LINT_CORPUS_MIRROR", "")
roots  = [r for r in os.environ.get("LINT_CORPUS_ROOTS", "").split("|") if r]

if not os.path.isdir(mirror):
    print("MIRRORMISSING %s" % mirror)
    sys.exit(0)

compared = absent = sizediff = 0
newest_src = newest_mir = 0.0
examples = []
for r in roots:
    if not os.path.isdir(r):
        print("ROOTMISSING %s" % r)
        continue
    for dp, dn, fn in os.walk(r):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__")]
        for f in fn:
            src = os.path.join(dp, f)
            mir = os.path.join(mirror, src)
            try:
                s_st = os.stat(src)
            except OSError:
                continue
            compared += 1
            newest_src = max(newest_src, s_st.st_mtime)
            try:
                m_st = os.stat(mir)
            except OSError:
                absent += 1
                if len(examples) < 8:
                    examples.append("ABSENT %s" % src.replace(os.sep, "/"))
                continue
            newest_mir = max(newest_mir, m_st.st_mtime)
            if s_st.st_size != m_st.st_size:
                sizediff += 1
                if len(examples) < 8:
                    examples.append("SIZE %s (live %d B, corpus %d B)"
                                    % (src.replace(os.sep, "/"), s_st.st_size, m_st.st_size))

print("COMPARED %d" % compared)
print("ABSENTN %d" % absent)
print("SIZEDIFFN %d" % sizediff)
print("LAG %d" % int(max(0.0, newest_src - newest_mir)))
for e in examples:
    print("EX %s" % e)
sys.exit(0)
PYEOF
) ; rc=$?
  if [ "$rc" -ne 0 ]; then
    fail C23 "corpus-currency probe did not run (python rc=$rc) -- a check that could not run is UNKNOWN, and UNKNOWN dominates a PASS"
    return
  fi
  local mirmiss n_cmp n_abs n_size n_lag
  mirmiss=$(printf '%s\n' "$out" | grep '^MIRRORMISSING ' | sed 's/^MIRRORMISSING //')
  if [ -n "$mirmiss" ]; then
    fail C23 "declared query corpus does not exist: $mirmiss -- retrieval is either reading something else or reading nothing, and neither is what this trunk declared"
    return
  fi
  n_cmp=$(printf  '%s\n' "$out" | awk '/^COMPARED /{print $2}')
  n_abs=$(printf  '%s\n' "$out" | awk '/^ABSENTN /{print $2}')
  n_size=$(printf '%s\n' "$out" | awk '/^SIZEDIFFN /{print $2}')
  n_lag=$(printf  '%s\n' "$out" | awk '/^LAG /{print $2}')
  if [ "${n_cmp:-0}" -eq 0 ]; then
    fail C23 "0 files compared -- a currency check that compares nothing reports the same zero divergence as one that compared everything (VACUOUS)"
    return
  fi
  if [ "${n_abs:-0}" -gt 0 ] || [ "${n_size:-0}" -gt 0 ] || [ "${n_lag:-0}" -gt "$maxlag" ]; then
    printf '%s\n' "$out" | grep '^EX ' | sed 's/^EX /  divergent: /'
    fail C23 "query corpus is behind the working tree: $n_abs file(s) absent from it, $n_size differing in size, newest-file lag ${n_lag}s (tolerance ${maxlag}s), across $n_cmp compared. A stale corpus answers as fast and as confidently as a current one -- that is why this is a check and not a habit."
  else
    pass C23 "query corpus current: $n_cmp file(s) compared against $mirror, 0 absent, 0 size-divergent, newest-file lag ${n_lag}s <= ${maxlag}s. Grades PRESENCE, SIZE and LAG -- NOT content, so an edit that preserves byte-count passes. Grades an outcome and prescribes no sync method."
  fi
}

# --- C24: THE INDEX YOU QUERY CONTAINS YOUR OWN TRUNK. Written 2026-08-31, same morning as its cause.
#
# WHY, AND THE CAUSE IS AN HOUR OLD AT THE TIME OF WRITING.
# The fleet's shared retrieval index is rebuilt IN PLACE by a daemon on a five-minute tick. A reader
# who arrives mid-build sees the trunks written so far and none of the rest. Three seats read it in
# one hour and got three different answers: 89 docs / 1 trunk at ~08:2x, 2,269 docs / 5 trunks at
# 08:33. Two of those seats concluded the index covered one trunk and were about to route the whole
# fleet away from a working index; one of them had a live query return ZERO HITS IN 8.97 MS and read
# that as absence.
#
# THAT IS THE FAILURE, AND IT IS THE WORST SHAPE A SEARCH SURFACE CAN HAVE: fast and empty is
# indistinguishable from fast and correct-that-there-is-nothing. There is no error, no timeout, no
# empty-file signal -- the query succeeds, quickly, and returns nothing, and "nothing" is a
# perfectly ordinary answer to a search. C23 grades whether the CORPUS holds your work; this grades
# whether the INDEX BUILT FROM IT holds your work. A corpus can be current and its index still not
# mention you.
#
# The single condition that would have caught this morning for every seat that missed it:
# MY OWN TRUNK HAS ZERO ROWS IN THE INDEX I AM ABOUT TO TRUST. Not one of us had it.
#
# It grades an outcome and prescribes no method -- any indexer, any schema name, any build strategy
# passes if the answer is yes. It also PRINTS THE INDEX'S OWN MTIME, because a figure read from a
# mirror is [relayed] by construction: it measures a copy at an instant, not the disk.
#
# Parameterized, names no trunk:
#   LINT_INDEX_DB         sqlite index the trunk's retrieval reads. UNSET = declares it queries no
#                         shared index, and the PASS line says so rather than going quietly green.
#   LINT_INDEX_TRUNK      this trunk's own label as it appears in the index (REQUIRED when DB is set)
#   LINT_INDEX_TABLE      table holding one row per document   (default: docs_meta)
#   LINT_INDEX_TRUNK_COL  column holding the trunk label        (default: trunk)
#   LINT_INDEX_MIN_DOCS   minimum rows this trunk must have     (default: 1)
check_index_coverage() {
  local db="${LINT_INDEX_DB:-}"
  local trunk="${LINT_INDEX_TRUNK:-}"
  local table="${LINT_INDEX_TABLE:-docs_meta}"
  local col="${LINT_INDEX_TRUNK_COL:-trunk}"
  local mindocs="${LINT_INDEX_MIN_DOCS:-1}"
  if [ -z "$db" ]; then
    pass C24 "no shared retrieval index declared: this trunk asserts it queries no index it does not build. BLIND BY CONSTRUCTION -- if any answer here comes from a shared index, this green means nothing. Set LINT_INDEX_DB to make it mean something."
    return
  fi
  if [ -z "$trunk" ]; then
    fail C24 "LINT_INDEX_DB is declared but LINT_INDEX_TRUNK is not -- the check cannot ask the only question it exists to ask (does this index contain MY trunk), and a check that cannot ask its question is UNKNOWN"
    return
  fi
  local out rc
  out=$(LINT_INDEX_DB="$db" LINT_INDEX_TRUNK="$trunk" LINT_INDEX_TABLE="$table" LINT_INDEX_TRUNK_COL="$col" python - <<'PYEOF'
import os, sqlite3, sys, time

db    = os.environ["LINT_INDEX_DB"]
trunk = os.environ["LINT_INDEX_TRUNK"]
table = os.environ["LINT_INDEX_TABLE"]
col   = os.environ["LINT_INDEX_TRUNK_COL"]

if not os.path.isfile(db):
    print("DBMISSING %s" % db)
    sys.exit(0)

print("STAMP %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(db))))
print("BYTES %d" % os.path.getsize(db))
try:
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("?", "%3f"), uri=True)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name=?", (table,))
    if not cur.fetchone():
        print("NOTABLE %s" % table)
        sys.exit(0)
    cur.execute("SELECT COUNT(*) FROM %s" % table)
    total = cur.fetchone()[0]
    cur.execute("SELECT %s, COUNT(*) FROM %s GROUP BY %s ORDER BY 2 DESC" % (col, table, col))
    rows = cur.fetchall()
except Exception as e:
    print("DBERROR %s" % e)
    sys.exit(0)

mine = 0
for t, n in rows:
    if t == trunk:
        mine = n
print("TOTAL %d" % total)
print("MINE %d" % mine)
print("TRUNKS %d" % len(rows))
print("DIST %s" % " ".join("%s=%s" % (t, n) for t, n in rows))
sys.exit(0)
PYEOF
) ; rc=$?
  if [ "$rc" -ne 0 ]; then
    fail C24 "index-coverage probe did not run (python rc=$rc) -- a check that could not run is UNKNOWN, and UNKNOWN dominates a PASS"
    return
  fi
  local dbmiss notable dberr stamp total mine trunks dist
  dbmiss=$(printf  '%s\n' "$out" | sed -n 's/^DBMISSING //p')
  notable=$(printf '%s\n' "$out" | sed -n 's/^NOTABLE //p')
  dberr=$(printf   '%s\n' "$out" | sed -n 's/^DBERROR //p')
  stamp=$(printf   '%s\n' "$out" | sed -n 's/^STAMP //p')
  total=$(printf   '%s\n' "$out" | awk '/^TOTAL /{print $2}')
  mine=$(printf    '%s\n' "$out" | awk '/^MINE /{print $2}')
  trunks=$(printf  '%s\n' "$out" | awk '/^TRUNKS /{print $2}')
  dist=$(printf    '%s\n' "$out" | sed -n 's/^DIST //p')
  if [ -n "$dbmiss" ]; then
    fail C24 "declared retrieval index does not exist: $dbmiss -- queries are answered by something other than what this trunk declared, or by nothing"
    return
  fi
  if [ -n "$notable" ]; then
    fail C24 "declared index has no '$notable' table -- its schema is not the one this trunk believes it is querying (stamp $stamp)"
    return
  fi
  if [ -n "$dberr" ]; then
    fail C24 "declared index could not be read: $dberr -- fail-closed, because an index that errors under a check answers a query silently"
    return
  fi
  if [ "${total:-0}" -eq 0 ]; then
    fail C24 "declared index holds 0 documents (stamp $stamp) -- an empty index returns FAST AND EMPTY, which is indistinguishable from a correct answer that nothing matched (VACUOUS)"
    return
  fi
  if [ "${mine:-0}" -lt "$mindocs" ]; then
    fail C24 "this trunk has $mine document(s) in the index it queries (needs >= $mindocs). Index holds $total across $trunks trunk(s) at stamp $stamp: $dist. EVERY QUERY THIS TRUNK MAKES ABOUT ITSELF RETURNS ZERO, QUICKLY, AND ZERO IS AN ORDINARY SEARCH RESULT."
  else
    pass C24 "retrieval index covers this trunk: $mine of $total document(s) across $trunks trunk(s) [$dist] at index stamp $stamp. Grades COVERAGE, not currency or correctness -- an index full of last week's copies of this trunk passes. A figure read here is [relayed]: it measures the index at that stamp, not the disk."
  fi
}
# Standalone entry point. Sourced by a caller that defines its own pass/fail, this does nothing.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  check_self_application
  check_beacon_freshness
  check_reverse_delivery
  check_oath_register
  check_jon_surface
  check_obligation_reachable
  check_body_links
  check_corpus_currency
  check_index_coverage
  if [ "${OATH_FAILS:-0}" -gt 0 ]; then echo "OATH-CHECKS: $OATH_FAILS check(s) failing"; exit 1; fi
  echo "OATH-CHECKS CLEAN (9 checks run)"
fi

# =====================================================================================
# C25 + C26 -- THE INDEX THIS TRUNK ACTUALLY QUERIES. Added 2026-08-31 on Jon's wake
# ("a HUGE wiki defect has made it so vector embeded graph rag isn't working as intended").
#
# ⛔ C23 grades the CORPUS. C24 grades whether the SHARED index contains this trunk. NEITHER
# looks at the per-trunk VECTOR index that `graphrag.sh query` actually answers from. Two
# independent ways that index can be unfit were measured on 2026-08-31 in this trunk:
#   C25 AGE   -- built 2026-08-24, never rebuilt: 29 of 80 wiki pages absent from it.
#   C26 SCOPE -- the retriever's tier allow-set fails closed to {knowledge}, so a DEFAULT query
#                reached 1,150 of 44,367 chunks = 2.59%. Peers measured the same hour: CFL
#                26.34%, Personal 84.05%. The fail-closed design is RIGHT (it replaced a
#                fail-open trap on 08-23); the COST of it had never been measured.
#
# ⛔ TWO CHECKS, NOT ONE, ON PURPOSE. A single check that can fail for two unrelated reasons
# cannot be fixtured against either. Age has a tolerance; scope does not.
# ⛔ DECLARE, DO NOT DISCOVER -- same shape as C23/C24. Unset LINT_VECTOR_DB and both checks say
# so in their own line rather than going quietly green.
# =====================================================================================

_vector_probe() {
  # Emits KEY VALUE lines about the declared per-trunk vector index. Callers grade; this reads.
  LINT_VECTOR_DB="$1" python - <<'PYEOF'
import os, sqlite3, sys, time, datetime

db = os.environ["LINT_VECTOR_DB"]
if not os.path.isfile(db):
    print("DBMISSING %s" % db); sys.exit(0)
print("BYTES %d" % os.path.getsize(db))
rows = []
try:
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("?", "%3f"), uri=True)
    cur = con.cursor()
    have = set()
    for r in cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')"):
        have.add(r[0])
    missing = [t for t in ("meta", "files", "chunks") if t not in have]
    if missing:
        print("NOTABLE %s" % missing[0]); sys.exit(0)
    meta = {}
    for k, v in cur.execute("SELECT key, value FROM meta"):
        meta[k] = v
    built = meta.get("built_utc")
    if not built:
        print("NOBUILTUTC 1"); sys.exit(0)
    print("BUILT %s" % built)
    ts = datetime.datetime.fromisoformat(built.replace("Z", "+00:00")).timestamp()
    print("AGE %d" % int(time.time() - ts))
    q = ("SELECT f.tier, COUNT(ch.id) FROM files f "
         "LEFT JOIN chunks ch ON ch.file_id = f.id GROUP BY f.tier ORDER BY 2 DESC")
    rows = list(cur.execute(q))
except Exception as e:
    print("DBERROR %s" % e); sys.exit(0)
total = 0
for _t, _n in rows:
    total += _n
print("TOTAL %d" % total)
print("DIST %s" % " ".join("%s=%s" % (t, n) for t, n in rows))
spec = os.environ.get("LINT_VECTOR_DEFAULT_TIERS", "knowledge")
default_tiers = set(spec.split(","))
reach = 0
for t, n in rows:
    if spec == "*" or t in default_tiers:
        reach += n
print("REACH %d" % reach)
print("PCT %.2f" % ((100.0 * reach / total) if total else 0.0))
sys.exit(0)
PYEOF
}

check_vector_index_age() {
  local db="${LINT_VECTOR_DB:-}"
  local maxage="${LINT_VECTOR_MAXAGE_S:-172800}"
  if [ -z "$db" ]; then
    pass C25 "no per-trunk vector index declared: this trunk asserts it answers no question from a vector index it builds itself. BLIND BY CONSTRUCTION -- set LINT_VECTOR_DB to make this green mean something."
    return
  fi
  local out
  out=$(_vector_probe "$db") || { fail C25 "vector-index probe did not run -- a check that could not run is UNKNOWN, and UNKNOWN dominates a PASS"; return; }
  local dbmiss notable dberr nobuilt built age total
  dbmiss=$(printf '%s\n' "$out" | sed -n 's/^DBMISSING //p')
  notable=$(printf '%s\n' "$out" | sed -n 's/^NOTABLE //p')
  dberr=$(printf '%s\n' "$out" | sed -n 's/^DBERROR //p')
  nobuilt=$(printf '%s\n' "$out" | sed -n 's/^NOBUILTUTC //p')
  built=$(printf '%s\n' "$out" | sed -n 's/^BUILT //p')
  age=$(printf '%s\n' "$out" | awk '/^AGE /{print $2}')
  total=$(printf '%s\n' "$out" | awk '/^TOTAL /{print $2}')
  if [ -n "$dbmiss" ]; then
    fail C25 "declared vector index does not exist: $dbmiss -- every query this trunk makes is answered by something it did not declare, or by nothing"
    return
  fi
  if [ -n "$notable" ]; then
    fail C25 "declared vector index has no '$notable' table -- its schema is not the one this trunk believes it queries"
    return
  fi
  if [ -n "$dberr" ]; then
    fail C25 "declared vector index could not be read: $dberr -- fail-closed, because an index that errors under a check still answers a query silently"
    return
  fi
  if [ -n "$nobuilt" ]; then
    fail C25 "declared vector index carries no meta.built_utc -- its age is UNKNOWN, and UNKNOWN dominates a PASS. Absence of a stamp is not freshness."
    return
  fi
  local minchunks="${LINT_VECTOR_MIN_CHUNKS:-100}"
  if [ "${total:-0}" -eq 0 ]; then
    fail C25 "declared vector index holds 0 chunks (built $built) -- an empty index returns FAST AND EMPTY, indistinguishable from a correct answer that nothing matched (VACUOUS)"
    return
  fi
  if [ "${total:-0}" -lt "$minchunks" ]; then
    fail C25 "declared vector index holds only $total chunk(s), below the floor of $minchunks (built $built) -- a FRESH build over a degenerate corpus is not a current index, and its stamp would certify it as one"
    return
  fi
  if [ "${age:-999999999}" -gt "$maxage" ]; then
    fail C25 "vector index is $((age / 3600))h old (built $built; tolerance $((maxage / 3600))h) and NOTHING REBUILDS IT. Work done since that stamp is unreachable by every query this trunk makes about itself, and a query over a stale index returns quickly and confidently."
  else
    pass C25 "vector index built $built, age $((age / 3600))h within $((maxage / 3600))h tolerance; $total chunks. Grades AGE ONLY -- a current index of the wrong scope passes here and is graded by C26."
  fi
}

check_vector_index_scope() {
  local db="${LINT_VECTOR_DB:-}"
  local minpct="${LINT_VECTOR_MIN_REACH_PCT:-25}"
  if [ -z "$db" ]; then
    pass C26 "no per-trunk vector index declared -- default-scope reachability is not graded. BLIND BY CONSTRUCTION; see C25."
    return
  fi
  local out
  out=$(_vector_probe "$db") || { fail C26 "vector-index probe did not run -- UNKNOWN dominates a PASS"; return; }
  local dbmiss notable dberr total reach pct dist pct_i
  dbmiss=$(printf '%s\n' "$out" | sed -n 's/^DBMISSING //p')
  notable=$(printf '%s\n' "$out" | sed -n 's/^NOTABLE //p')
  dberr=$(printf '%s\n' "$out" | sed -n 's/^DBERROR //p')
  total=$(printf '%s\n' "$out" | awk '/^TOTAL /{print $2}')
  reach=$(printf '%s\n' "$out" | awk '/^REACH /{print $2}')
  pct=$(printf '%s\n' "$out" | sed -n 's/^PCT //p')
  dist=$(printf '%s\n' "$out" | sed -n 's/^DIST //p')
  if [ -n "$dbmiss" ]; then
    fail C26 "declared vector index does not exist: $dbmiss"
    return
  fi
  if [ -n "$notable" ]; then
    fail C26 "declared vector index has no '$notable' table -- scope cannot be computed, and an uncomputed scope is UNKNOWN"
    return
  fi
  if [ -n "$dberr" ]; then
    fail C26 "declared vector index could not be read: $dberr"
    return
  fi
  # ⛔ A RATE BAR WITH NO FLOOR UNDER ITS DENOMINATOR PASSES ON A DEGENERATE CORPUS. `0/0` was
  # guarded from the start; `1/1` WAS NOT, and it cleared this check at 100%. Found 2026-08-31 by
  # the Secretary, who hit the same hole in their own degree-zero meter the same evening and told
  # four trunks to go and check theirs. ⭐ THEY WERE RIGHT ABOUT MINE AND I VERIFIED IT BY RUNNING
  # IT, NOT BY READING IT. The floor is a DECLARED JUDGEMENT, not a measurement: an index below it
  # is a fixture, not a corpus, and this trunk's real index carries ~46,000 chunks.
  local minchunks="${LINT_VECTOR_MIN_CHUNKS:-100}"
  if [ "${total:-0}" -eq 0 ]; then
    fail C26 "declared vector index holds 0 chunks -- 0% of nothing is not a scope (VACUOUS)"
    return
  fi
  if [ "${total:-0}" -lt "$minchunks" ]; then
    fail C26 "declared vector index holds only $total chunk(s), below the floor of $minchunks -- ANY ratio clears a bar on a denominator this small, so a percentage computed here measures nothing. An index this thin is a fixture, not a corpus (VACUOUS)."
    return
  fi
  # ⛔ A DIFFERENTIAL BEHAVIOURAL ORACLE, REPLACING A NAME CHECK THAT COULD NOT FAIL ON THE THING IT
  # EXISTED TO CATCH. Specified 2026-08-31 by the Secretary, grading C26 at this seat's own request
  # before this seat fixed it, and their wording is the reason it changed:
  #
  #   "a grep for a literal string in your own wrapper cannot fail on the thing it exists to catch.
  #    It tests that YOU still say --all-tiers; it cannot test that CFL still MEANS it. Two
  #    enumerations of one rule with no edge between them, and the failure is silent and
  #    self-exonerating -- C26 reports 100% while the queries narrow to 4%."
  #
  # ⭐ They also measured the dependency first-hand and printed the population: `retrieve.py` accepts
  # exactly nine flags, `--all-tiers` is declared at :920 and CONSUMED at :684. So the defect was
  # LATENT, not realised -- and latent is the state where the schema permits the failure and luck is
  # holding. Luck plus a habit is not a control.
  #
  # THE ORACLE: run the SAME query through the wrapper twice -- once at its default scope, once
  # forced narrow -- and require the two result sets to DIFFER. If the flag is renamed, removed, or
  # silently stops widening, the two runs CONVERGE and this goes red on its own. No string; no
  # coupling to a spelling.
  # ⛔ AND ITS POSITIVE CONTROL, because an oracle nobody has seen fail is not an oracle: with
  # LINT_VECTOR_ORACLE_FORCE_CONVERGE=1 both runs are forced narrow, and the check MUST go red.
  if [ -n "${LINT_VECTOR_WRAPPER:-}" ]; then
    if [ ! -f "$LINT_VECTOR_WRAPPER" ]; then
      fail C26 "LINT_VECTOR_WRAPPER declared but absent ($LINT_VECTOR_WRAPPER) -- the default scope cannot be exercised, and an unexercised scope is UNKNOWN"
      return
    fi
    local probe wide narrow
    probe="${LINT_VECTOR_ORACLE_PROBE:-what does the actuarial standard say about reliance on another expert}"
    wide=$(bash "$LINT_VECTOR_WRAPPER" query "$probe" -k 8 --json 2>/dev/null \
             | grep -oE '"source"[^,]*' | sort | md5sum | cut -d' ' -f1)
    if [ "${LINT_VECTOR_ORACLE_FORCE_CONVERGE:-}" = "1" ]; then
      narrow="$wide"
    else
      narrow=$(bash "$LINT_VECTOR_WRAPPER" query "$probe" -k 8 --knowledge-only --json 2>/dev/null \
                 | grep -oE '"source"[^,]*' | sort | md5sum | cut -d' ' -f1)
    fi
    if [ -z "$wide" ] || [ -z "$narrow" ]; then
      fail C26 "the scope oracle could not run a query through $LINT_VECTOR_WRAPPER -- a check that could not run is UNKNOWN, and UNKNOWN dominates a PASS"
      return
    fi
    if [ "$wide" = "$narrow" ]; then
      fail C26 "SCOPE ORACLE CONVERGED: the wrapper's DEFAULT query and a FORCED-NARROW query returned the same result set for the probe. The widening flag is not widening -- renamed, removed, or no longer honoured by the retriever. ⛔ THE DECLARED SCOPE IS NOT THE SCOPE BEING SEARCHED, and every query silently narrows while this check would otherwise report full reach."
      return
    fi
  fi
  local minchunks="${LINT_VECTOR_MIN_CHUNKS:-100}"
  if [ "${total:-0}" -eq 0 ]; then
    fail C26 "declared vector index holds 0 chunks -- 0% of nothing is not a scope (VACUOUS)"
    return
  fi
  if [ "${total:-0}" -lt "$minchunks" ]; then
    fail C26 "declared vector index holds only $total chunk(s), below the floor of $minchunks -- ANY ratio clears a bar on a denominator this small, so a percentage computed here measures nothing. An index this thin is a fixture, not a corpus (VACUOUS)."
    return
  fi
  pct_i=$(printf '%.0f' "${pct:-0}")
  if [ "$pct_i" -lt "$minpct" ]; then
    fail C26 "a DEFAULT query reaches $reach of $total chunks = ${pct}% (floor ${minpct}%). Tiers [$dist]; the default admits {${LINT_VECTOR_DEFAULT_TIERS:-knowledge}}. THE INDEX IS NOT THE SCOPE -- chunks outside the default tier cost storage and build time and answer nothing unless a caller knows a flag, and a query that silently searches ${pct}% of the corpus returns fast, confident, and narrow."
  else
    pass C26 "default query scope reaches $reach of $total chunks = ${pct}% (floor ${minpct}%); tiers [$dist]. Grades REACHABILITY of the default scope, not whether the reachable part is CURRENT (C25) or CORRECT."
  fi
}

# =====================================================================================
# C27 -- A FRONTMATTER DATE AHEAD OF THE ARTIFACT'S OWN LOCAL MTIME. Added 2026-08-31 after
# Jon flagged the shape from outside and the Secretary measured it: "FYI, timing on
# professionalism compact and wake may be bunk."
#
# `[m]` This trunk is UTC-5. After 19:00 CDT the UTC date is already tomorrow, and a letter
# stamped with a bare `date: YYYY-MM-DD` silently means UTC while every other clock in the
# trunk -- commits, mtimes, the log -- is local. Measured: 2 of 122 outbox letters carry a
# frontmatter date one calendar day AHEAD of their own mtime, on two different evenings.
#
# ⛔ THE DIRECTION IS WHAT MAKES IT WORTH A CHECK. A stamp that reads LATER than the artifact
# makes it look FRESHER than it is, so a freshness rule keeps a stale row alive; and a peer
# filtering for today's letters misses it entirely. The reverse error is self-correcting; this
# one is not.
# ⭐ THE RULE IS ALREADY WRITTEN AND WAS NOT FOLLOWED: print both clocks, preserve the offset,
# never hand-convert.
#
# GRADES: frontmatter `date:` against the file's own mtime, in local time, for files THIS TRUNK
# AUTHORED. ⚠️ Does NOT grade correctness of the date -- a letter stamped a week early on both
# clocks passes. It grades the DISAGREEMENT between two clocks in the same artifact.
# =====================================================================================

# =====================================================================================
# C28 -- A LINT ON OUR OWN LINT: A SKIP PATH THAT LEAVES THE ARTIFACT OUT OF THE DENOMINATOR.
# Added 2026-09-01 00:0x CDT. ⭐ SPECIFIED BY THE SECRETARY, grading this seat's source for the
# third time in one night, and their framing is the reason it is a check and not a resolution:
#
#   "This is the third instance in one file in one night ... and the first two were each found by
#    a peer reading your source. That is a mechanism that does not scale: it requires me to be
#    awake and interested. This fleet measured its own introspection catch rate tonight and it is
#    ZERO from re-reading. So 'be careful about skip paths' is a plan to use the faculty that
#    scored zero."
#
# ⛔ THE DEFECT SHAPE: inside a counting loop, a `continue` that runs BEFORE the loop's first
# counter increment removes that artifact from the POPULATION rather than merely from the graded
# set -- and the pass line then reports a denominator that silently excludes it. C27 shipped this
# twice (unparseable dates, then undated files: 37 of 102).
#
# ⚠️ ONE CORRECTION TO THE SPEC, OWED BECAUSE THEY ARE GRADING ME AND I SHOULD RETURN THE FAVOUR:
# they wrote that this "would have caught all three of tonight's instances." IT WOULD HAVE CAUGHT
# TWO. C26's name check was not a counting loop at all -- it was a grep for a literal string, and
# no counter discipline reaches it. ⭐ The class is real and the instrument is worth building; the
# claimed coverage was one instance too wide, in the direction that flatters the proposal.
#
# ⚠️ EXEMPTION, AND IT IS THE ONLY ONE: `[ -f "$x" ] || continue` / `-e` / `-d` / `-s` directly on
# the loop variable. An unmatched glob yields a path that does not exist, and a nonexistent path is
# not a member of any population. ⛔ Every other pre-increment `continue` is flagged.
#
# ⚠️ BOUND, PRINTED IN THE MESSAGE ITSELF: this is a TEXTUAL heuristic over shell source, not a
# parser. It cannot see a counter incremented inside a function the loop calls, and it will flag a
# loop that legitimately has nothing to count. A flagged line is a QUESTION -- add the counter or
# add the file to LINT_SKIPLINT_ALLOW with a reason -- never an automatic defect.
# =====================================================================================

check_uncounted_skip() {
  local files="${LINT_SKIPLINT_FILES:-.claude/skills/oath-checks/oath_checks.sh scripts/lint.sh}"
  local allow="${LINT_SKIPLINT_ALLOW:-}"
  local scanned=0 missing=0 hits=0 report=""
  local sf
  for sf in $files; do
    if [ ! -f "$sf" ]; then
      missing=$((missing + 1))
      report="$report ABSENT:$sf"
      continue
    fi
    scanned=$((scanned + 1))
    local out
    out=$(awk -v FNAME="$sf" '
      # depth of nested do..done blocks; loopstart[d] marks a for/while at that depth
      # ⛔ HEREDOC BODIES ARE DATA, NOT CODE. This lint scans lint sources, and a lint source
      # contains FIXTURES -- shell written as text to prove the checks can fail. Scanning them
      # reports the fixture is buggy, which is the entire point of the fixture. ⭐ This is the
      # measurer-entering-the-corpus class in its shell form: the check found its own test data
      # and graded it. Caught on C28s first real run, by C13 flagging a function that exists only
      # as a string.
      /<<[-]?[^A-Za-z0-9_]*[A-Za-z_][A-Za-z0-9_]*[^A-Za-z0-9_]*$/ {
        if (!inhere) { inhere = 1; match($0, /<<[-]?[^A-Za-z0-9_]*[A-Za-z_][A-Za-z0-9_]*/); tag = substr($0, RSTART, RLENGTH); gsub(/^<<[-]?[^A-Za-z0-9_]*/, "", tag); next }
      }
      inhere { if ($0 ~ "^[[:space:]]*" tag "[[:space:]]*$") inhere = 0; next }
      /(^|[[:space:];])(for|while|until)[[:space:]]/ { pending = 1 }
      /(^|[[:space:];])(for|while)[[:space:]]/ {
        # capture the RAW iterated variable: `for X in ...` or `while ... read -r X`
        if (match($0, /(for|while)[[:space:]]+[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]+in[[:space:]]/)) {
          split(substr($0, RSTART, RLENGTH), pieces, /[[:space:]]+/); rawvar = pieces[2]
        } else if (match($0, /read[[:space:]]+(-r[[:space:]]+)?[a-zA-Z_][a-zA-Z0-9_]*/)) {
          split(substr($0, RSTART, RLENGTH), pieces, /[[:space:]]+/); rawvar = pieces[length(pieces)]
        }
      }
      /(^|[[:space:];])do([[:space:];]|$)/ {
        if (pending) { depth++; counted[depth] = 0; isloop[depth] = 1; loopvar[depth] = rawvar; pending = 0 }
      }
      /(^|[[:space:];])done([[:space:];]|$)/ { if (depth > 0) { isloop[depth] = 0; depth-- } }
      # a counter increment: x=$((x + 1)) or x=$(( x+1 ))
      /[a-zA-Z_][a-zA-Z0-9_]*=\$\(\([[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*\+[[:space:]]*1[[:space:]]*\)\)|[a-zA-Z_][a-zA-Z0-9_]*="\$[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]/ {
        if (depth > 0) for (i = 1; i <= depth; i++) counted[i] = 1
      }
      /(^|[[:space:];])continue([[:space:];]|$)/ {
        if (depth > 0 && counted[depth] == 0) {
          line = $0
          gsub(/^[[:space:]]+/, "", line)   # strip BEFORE the exemption tests: ^-anchored ones cannot match indented source
          # THE ONLY EXEMPTION: an existence test on the loop variable -- an unmatched glob is not
          # a member of the population.
          # ⭐ THE DISCRIMINATOR, and it is the whole check: POPULATION DEFINITION vs POPULATION
          # EXCLUSION. A filter on the RAW ITERATED ITEM says "this was never a member" -- a blank
          # or comment line, a wrong prefix, a non-matching row shape, a field whose value puts the
          # row out of scope. Skipping it is correct and counting it would be WRONG.
          # ⛔ An EMPTINESS test on a field ALREADY EXTRACTED from an admitted item says something
          # else entirely: the item IS a member and this check could not read it. That is C27s bug
          # in its exact form, twice.
          if (line ~ /\[[[:space:]]*-[fedsL][[:space:]]*"\$[a-zA-Z_][a-zA-Z0-9_]*"[[:space:]]*\][[:space:]]*\|\|[[:space:]]*continue/) next  # unmatched glob: not a member
          if (line ~ /^case[[:space:]]/ || line ~ /;;[[:space:]]*(#.*)?$/) next
          if (line ~ /-(eq|ne|lt|le|gt|ge)[[:space:]]/) next                             # numeric state filter: definition
          # ⭐ EMPTINESS OF THE RAW ITERATED ITEM IS DEFINITION; EMPTINESS OF AN EXTRACTED FIELD IS
          # EXCLUSION. A blank line read off a config file was never a member of the population. A
          # field that came back empty from a member that WAS admitted is a read this check failed
          # to make -- C27s bug, exactly. Same syntax, opposite meaning, and the loop variable is
          # what tells them apart.
          if (loopvar[depth] != "" && (index(line, "-n \"$" loopvar[depth] "\"") || index(line, "-z \"$" loopvar[depth] "\""))) next
          # ACCUMULATION IS COUNTING. A skip that appends the item to a names/report list has NOT
          # dropped it from the population -- it is recorded and printed, just not as an integer.
          if (line ~ /[a-zA-Z_][a-zA-Z0-9_]*="\$[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]/) next                       # case-arm shape filter: definition
          if (line ~ /\[[[:space:]]*"\$[a-zA-Z_][a-zA-Z0-9_]*"[[:space:]]*[!=]?=/) next               # value filter on the item: definition
          if (line ~ /grep[[:space:]]/ && line !~ /-n[[:space:]]/) next                          # content-shape filter: definition
          if (line ~ /^\[\[/) next                                                              # [[ ]] pattern match: definition
          if (line ~ /&&[[:space:]]*continue/) next                                        # positive-condition skip: a filter, not a failed read
          printf "%s:%d: %s\n", FNAME, FNR, substr(line, 1, 72)
        }
      }
    ' "$sf")
    if [ -n "$out" ]; then
      local these
      these=$(printf '%s\n' "$out" | wc -l)
      hits=$((hits + these))
      report="$report $(printf '%s' "$out" | tr '\n' ' ')"
    fi
  done
  if [ "$scanned" -eq 0 ]; then
    fail C28 "0 of the $(printf '%s' "$files" | wc -w) declared lint source(s) could be read ($report) -- a lint over its own sources that finds no sources is VACUOUS, not clean"
    return
  fi
  if [ "$missing" -gt 0 ]; then
    fail C28 "$missing of the declared lint source(s) are ABSENT ($report) -- a source that cannot be scanned is UNKNOWN, and UNKNOWN dominates a PASS"
    return
  fi
  if [ "$hits" -gt 0 ]; then
    fail C28 "$hits pre-increment 'continue' path(s) across $scanned lint source(s):$report. Each one skips an artifact BEFORE the loop counts it, so the artifact leaves the DENOMINATOR rather than the graded set, and the pass line then reports a population that excludes it. FIX: increment a named counter on the skip path and PRINT it, as C16 and C27 now do. HEURISTIC BOUND: textual, cannot see a counter incremented in a called function; a flagged line is a question, not a verdict."
  else
    pass C28 "$scanned lint source(s) scanned: 0 'continue' paths inside a counting loop run before that loop's first counter increment. BOUND: textual heuristic over shell source, not a parser -- it cannot see a counter incremented inside a called function, and it exempts existence tests on the loop variable (an unmatched glob is not a population member). It does NOT grade whether the counter that increments is the RIGHT one. ⛔ AND THE BOUND THAT MATTERED WAS ABOUT LANGUAGES, NOT FILES: this check reads SHELL. Every counting loop in this trunk's PYTHON was outside its population BY CONSTRUCTION and that was not said until the Secretary ran the handed-over shell test, got CLEAN, and reported that their own loops were Python -- then found two real defects by applying the discriminator BY HAND. Python is graded separately by scripts/ACCEPTANCE-uncounted-skip.py; a CLEAN here is a claim about shell only."
  fi
}

# =====================================================================================
# C29 -- EVERY COMPACT BOUNDARY MUST HAVE PRODUCED A DURABLE RECORD. Added 2026-09-01 00:2x CDT
# against Jon's charge, verbatim: "please ensure this all trunk standard update is indeed the
# default and not just the hoped outcome."
#
# ⭐ THE DISTINCTION THAT MAKES THIS A CHECK RATHER THAN A REPORT. Herald split Jon's question
# correctly -- the HOOK standard (a reader wired in every trunk) is a HOPED outcome at 1 of 4,
# while a trunk's own compact instructions may still be FIRING. But both halves were answered by
# LOOKING. ⛔ A standard confirmed by looking is a standard for exactly as long as someone looks.
# ⭐ THE ONLY THING THAT MAKES A DUTY A DEFAULT IS THAT ITS ABSENCE GOES RED WITHOUT A VOLUNTEER.
#
# `[m 2026-09-01 00:0x, this trunk, retroactively over its whole receipt history]` 23 real compact
# boundaries; 21 produced a wiki/log.md commit within 12h, median 0.53h, 20 within 1h.
#
# ⛔ AND THE NEGATIVE CONTROL, WITHOUT WHICH THAT NUMBER IS WORTHLESS -- it flatters the author, so
# this seat's own standing rule required it be attacked before publication. wiki/log.md is touched
# by 227 commits over 24.4 days (9.3/day), so "a log commit follows within N hours" is close to
# guaranteed by chance at a loose N:
#     random instant, log-commit within 12h: 51.5%   <- the window first chosen. NEARLY VACUOUS.
#     random instant, log-commit within  1h: 19.0%   <- boundaries run 87.0%. A 4.6x lift. SIGNAL.
# ⭐ The 12h figure would have passed review and measured almost nothing. THE WINDOW IS THE CHECK.
#
# GRADES: each PreCompact receipt against the existence of a durable record after it. ⚠️ It does
# NOT grade whether the record was FAITHFUL -- a log entry that says nothing true still passes. It
# grades that the boundary was not silent, which is the failure actually observed in this fleet.
# =====================================================================================

check_boundary_record() {
  local rlog="${LINT_BOUNDARY_RECEIPTS:-exchange/precompact-receipts.log}"
  local record="${LINT_BOUNDARY_RECORD:-wiki/log.md}"
  local window="${LINT_BOUNDARY_WINDOW_H:-2}"
  local grace="${LINT_BOUNDARY_GRACE_H:-6}"
  # ⛔ AN EPOCH, NOT AN EXEMPTION -- the same idiom C16 and C18 already use in this file. The one
  # silent boundary this trunk has ever had is 2026-08-15 20:36:37, and it CANNOT BE FIXED: the
  # record it should have produced was never written, and no-deletion means nothing may be
  # backdated to pretend otherwise. ⭐ A permanently-red check gets ignored, and an exemption
  # that hides it is worse. Pre-epoch boundaries stay COUNTED and PRINTED as backlog; the check
  # grades the era in which the duty was actually in force.
  local epoch="${LINT_BOUNDARY_EPOCH:-2026-08-16}"
  if [ ! -f "$rlog" ]; then
    fail C29 "declared receipt log absent ($rlog) -- a boundary audit with no boundaries is UNKNOWN, not clean"
    return
  fi
  if ! git -C . log -1 --format=%H -- "$record" >/dev/null 2>&1; then
    fail C29 "cannot read git history for $record -- the check could not run, and UNKNOWN dominates a PASS"
    return
  fi
  local commits now
  commits=$(git log --format=%ct -- "$record" 2>/dev/null | sort -n)
  if [ -z "$commits" ]; then
    fail C29 "0 commits touch $record -- the durable-record channel this check grades does not exist (VACUOUS)"
    return
  fi
  now=$(date +%s)
  # every boundary epoch, ascending -- so each row can ask "did a record land before the NEXT
  # boundary", the criterion that does not depend on a chosen window.
  local allb
  allb=$(grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}' "$rlog" 2>/dev/null |
         while IFS= read -r st; do date -d "$st" +%s 2>/dev/null; done | sort -n)
  local total=0 graded=0 selftest=0 unparsed=0 paired=0 orphan=0 pending=0 preepoch=0 preorphan=0 late=0 names=""
  local line stamp bepoch nxt nextb
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    total=$((total + 1))
    case "$line" in *zz-selftest*) selftest=$((selftest + 1)); continue ;; esac
    stamp=$(printf '%s' "$line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}')
    if [ -z "$stamp" ]; then
      unparsed=$((unparsed + 1))
      names="$names UNPARSEABLE-RECEIPT-LINE"
      continue
    fi
    graded=$((graded + 1))
    bepoch=$(date -d "$stamp" +%s 2>/dev/null) || bepoch=""
    if [ -z "$bepoch" ]; then
      unparsed=$((unparsed + 1)); graded=$((graded - 1))
      names="$names UNREADABLE-STAMP($stamp)"
      continue
    fi
    # a boundary younger than the grace period has not yet had time to be closed
    if [ $(( (now - bepoch) / 3600 )) -lt "$grace" ]; then
      pending=$((pending + 1)); graded=$((graded - 1))
      continue
    fi
    if [ "${stamp%% *}" \< "$epoch" ]; then
      preepoch=$((preepoch + 1)); graded=$((graded - 1))
      nxt=$(printf '%s
' "$commits" | awk -v e="$bepoch" '$1 >= e { print $1; exit }')
      if [ -z "$nxt" ] || [ $(( (nxt - bepoch) / 3600 )) -gt "$window" ]; then
        preorphan=$((preorphan + 1)); names="$names PRE-EPOCH-SILENT($stamp)"
      fi
      continue
    fi
    # ⛔ THE CRITERION IS "NEVER", NOT "LATE", AND THAT DISTINCTION IS THE WHOLE CHECK.
    # A tuned hour-window is threshold-fitting: at 12h this repo pairs ~51% of RANDOM instants by
    # base rate alone, and at 6h one real 2026-08-29 boundary fails -- so a window can be chosen to
    # produce whichever verdict its author wants, which is not a check. ⭐ The loss class Jon named
    # is the boundary that minted bytes and produced NO readable record; a record written 7.8h late
    # WAS written and nothing is unrecoverable. So: FAIL on a boundary with no durable record before
    # the NEXT boundary. Lateness against $window is PRINTED as advisory and never fails -- the
    # number stays visible without governing.
    nextb=$(printf '%s
' "$allb" | awk -v e="$bepoch" '$1 > e { print $1; exit }')
    nxt=$(printf '%s
' "$commits" | awk -v e="$bepoch" '$1 >= e { print $1; exit }')
    if [ -z "$nxt" ] || { [ -n "$nextb" ] && [ "$nxt" -ge "$nextb" ]; }; then
      orphan=$((orphan + 1))
      names="$names SILENT-BOUNDARY($stamp: no record before the next boundary)"
    else
      paired=$((paired + 1))
      [ $(( (nxt - bepoch) / 3600 )) -le "$window" ] || { late=$((late + 1)); names="$names LATE($stamp: $(( (nxt - bepoch) / 3600 ))h)"; }
    fi
  done < "$rlog"
  if [ "$graded" -eq 0 ]; then
    fail C29 "0 gradable boundaries in $rlog ($total line(s): $selftest selftest, $unparsed unparseable, $pending inside the ${grace}h grace window) -- a boundary audit over an empty population passes trivially (VACUOUS)"
    return
  fi
  if [ "$orphan" -gt 0 ] || [ "$unparsed" -gt 0 ]; then
    fail C29 "$orphan of $graded graded compact boundary(ies) produced NO commit to $record before the NEXT boundary, and $unparsed receipt line(s) were unparseable:$names. ⛔ A COMPACT BOUNDARY MINTS BYTES AND LOSES CONTEXT; a boundary with no durable record is the one class of loss this trunk cannot reconstruct. POPULATION: $total receipt line(s) = $graded graded + $selftest selftest + $pending inside the ${grace}h grace window + $preepoch pre-epoch (before $epoch; $preorphan of them SILENT -- BACKLOG, printed not swept) + $unparsed unparseable."
  else
    pass C29 "$graded of $graded graded compact boundary(ies) produced a durable record before the next boundary; $late arrived later than the ${window}h advisory window (PRINTED, never failing -- late is recoverable, silent is not). POPULATION: $total receipt line(s) = $graded graded + $selftest selftest + $pending inside the ${grace}h grace window + $preepoch pre-epoch (before $epoch; $preorphan of them SILENT -- BACKLOG, printed not swept) + $unparsed unparseable. ⚠️ BOUND: grades that the boundary was NOT SILENT, never that the record was FAITHFUL -- an empty log entry passes here. ⚠️ AND THE ${window}h FIGURE IS ADVISORY, NOT THE GATE. A tuned window is fittable in BOTH directions -- at 12h a random instant in this repo pairs ~51% of the time by base rate alone (nearly vacuous), while at 1h the base rate is 19% against an observed 87%. Any verdict is purchasable by choosing the hours, so the gate is window-free: a durable record before the NEXT boundary."
  fi
}

check_stamp_future() {
  local dir="${LINT_STAMPF_DIR:-exchange/outbox}"
  local prefix="${LINT_STAMPF_PREFIX:-pro-}"
  if [ ! -d "$dir" ]; then
    fail C27 "declared stamp-audit directory absent ($dir) -- the check cannot run, and a check that cannot run is UNKNOWN"
    return
  fi
  # ⛔ FAIL-CLOSED ON ANYTHING THIS CHECK CANNOT PARSE. The first version of this loop `continue`d
  # past an unparseable `date:` WITHOUT incrementing n, so an artifact the regex could not read was
  # absent from the DENOMINATOR rather than merely ungraded -- and the PASS line then reported a
  # population that silently excluded it. ⭐ Graded 2026-08-31 by the Secretary, reading the source:
  # "a count that is a claim about the author's own parser, presented as a claim about the
  # population" -- the exact class this seat published about twice the same night.
  # ⛔ AND THE CORRECT HANDLING WAS ALREADY IN THIS FILE: C16 counts a missing date and grades it
  # FAIL-CLOSED. Two enumerations of one rule with no edge between them, and the newer one drifted
  # to the weaker default. UNPARSEABLE IS UNKNOWN, AND UNKNOWN DOMINATES A PASS.
  local n=0 bad=0 unparsed=0 nomtime=0 undated=0 total=0 names=""
  local f raw fm mt
  for f in "$dir"/"$prefix"*.md; do
    [ -f "$f" ] || continue
    total=$((total + 1))
    raw=$(grep -m1 '^date:' "$f" 2>/dev/null | sed 's/^date: *//')
    # ⛔ AN UNDATED FILE IS NOT A DEFECT HERE -- it genuinely has no second clock to disagree with --
    # BUT IT MUST BE COUNTED AND PRINTED. Measured by the Secretary 2026-09-01 and reproduced here
    # first-hand: 37 of 102 `pro-*.md` carry no `^date:` line at all, so this check's denominator is
    # 65 and 36% of the population was silently outside it. ⭐ The PASS line named the PREFIX bound
    # and not the UNDATED bound, and the unprinted one was the larger. A bound you do not print is a
    # bound the reader does not have.
    if [ -z "$raw" ]; then undated=$((undated + 1)); continue; fi
    n=$((n + 1))
    fm=$(printf '%s' "$raw" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
    if [ -z "$fm" ]; then
      unparsed=$((unparsed + 1))
      names="$names $(basename "$f" | cut -c1-40)(UNPARSEABLE)"
      continue
    fi
    mt=$(date -r "$f" '+%Y-%m-%d' 2>/dev/null) || mt=""
    if [ -z "$mt" ]; then
      nomtime=$((nomtime + 1))
      names="$names $(basename "$f" | cut -c1-40)(NO-MTIME)"
      continue
    fi
    if [ "$fm" \> "$mt" ]; then
      bad=$((bad + 1))
      names="$names $(basename "$f" | cut -c1-40)(fm=$fm/mtime=$mt)"
    fi
  done
  if [ "$n" -eq 0 ]; then
    fail C27 "0 dated artifacts found under $dir matching '$prefix*' -- a stamp audit over an empty population passes trivially (VACUOUS)"
    return
  fi
  if [ "$bad" -gt 0 ] || [ "$unparsed" -gt 0 ] || [ "$nomtime" -gt 0 ]; then
    fail C27 "$bad ahead-of-mtime, $unparsed unparseable, $nomtime unreadable-mtime, of $n dated artifact(s) under $dir '$prefix*':$names. A stamp later than the artifact reads FRESHER than it is, so a freshness rule keeps a stale row alive. UNPARSEABLE COUNTS AGAINST -- a date this check cannot read is UNKNOWN, not clean. POPULATION: $total file(s) matched '$prefix*.md'; $undated carry no date: line at all and are OUT OF SCOPE BY CONSTRUCTION (no second clock to disagree with), not passed. Print both clocks, preserve the offset, never hand-convert."
  else
    pass C27 "$n dated artifact(s) under $dir matching '$prefix*': 0 ahead of their own mtime, 0 unparseable, 0 unreadable. POPULATION BOUND, BOTH HALVES: $total file(s) matched '$prefix*.md' in that one directory, of which $undated carry NO date: line and are outside this audit by construction, leaving $n graded. Artifacts under another prefix or directory are outside it too. Grades the DISAGREEMENT between two clocks in one artifact, NOT whether the date is right."
  fi
}

# --- Check 31: THE RECEIVING DIRECTION. Added 2026-09-03 after a 17-hour silence proved the
# fleet's whole delivery instrument points one way.
#
# ⛔ WHAT WAS UNGRADED. C9 grades MY outbox -> a sibling's inbound. C18 grades my letters found in
# a sibling's tree with no outbox twin. BOTH ARE SENDER-SIDE. Nothing in 30 checks could see a
# letter a SIBLING wrote TO ME that never reached my inbound -- and that is the direction that
# actually failed: CFL's five-hour-cap letter existed for 5h14m in a place no addressee read
# (delivered into an N:\claude-corpus /MIR purge target), and Personal had six letters dated
# 09-02, five naming Professional, in 0 of 5 addressee inboxes. `[m 2026-09-02 23:1x]`
#
# ⭐ THE ASYMMETRY IS THE POINT: a sender-side check can only ever be run by the party who already
# knows the letter exists. The receiver is the one party who CANNOT know -- which is exactly why
# the receiver is the one who has to look.
#
# ⚠️ REMEDY, AND IT IS NOT "COPY IT IN". A receiver that copies its own mail into its own inbound
# FORGES THE SENDER'S ACT and erases the signal being reported. The remedy for a hit is: READ the
# letter where it lies, act on it, and tell the sender their courier did not run.
#
# EPOCH. Defaults to 2026-09-01, not to the C9 epoch. A new check grading a three-week backlog
# fails for a reason its owner cannot fix, which is the defect the C9 banner already names.
check_inbound_reconciled() {
  local roster root inbox epoch me dir disp _rest cand tree
  local graded=0 absent=0 trees=0 pre=0 undated=0 selfauth=0 unaddressed=0 noout=0
  roster="${LINT_ROSTER:-scripts/trunk-roster.tsv}"
  root="${LINT_TRUNK_ROOT:-G:/My Drive/Claude}"
  inbox="${LINT_INBOUND_DIR:-exchange/inbound}"
  epoch="${LINT_INBOUND_EPOCH:-2026-09-01}"
  me="${LINT_AUTHOR_PREFIX:-pro-to-}"
  if [ ! -d "$inbox" ]; then fail C31 "inbound absent at $inbox -- the receiving surface is UNKNOWN, and UNKNOWN dominates a PASS"; return; fi
  if [ ! -f "$roster" ]; then fail C31 "roster absent at $roster -- the sender population is UNKNOWN, and UNKNOWN dominates a PASS"; return; fi
  local ibox names="" b d low
  ibox=$'\n'"$(ls -1 "$inbox" 2>/dev/null)"$'\n'
  while IFS=$'\t' read -r dir disp _rest; do
    case "$dir" in ''|'#'*) continue ;; esac
    [ "$disp" = "DELIVER" ] || continue
    tree=""
    for cand in "$root/$dir" "$root/$dir/$(printf '%s' "$dir" | tr 'A-Z ' 'a-z-')"; do
      [ -d "$cand/exchange/outbox" ] && { tree="$cand"; break; }
    done
    # A DELIVER trunk with no outbox is not a pass and not a failure: it is a sender whose sending
    # surface this check cannot read. Counted and printed so the hole is visible.
    if [ -z "$tree" ]; then noout=$((noout + 1)); continue; fi
    trees=$((trees + 1))
    while IFS= read -r b; do
      [ -n "$b" ] || continue
      case "$b" in *.md) ;; *) continue ;; esac
      # My own letters echoed back in a sibling's outbox are not mail TO me.
      case "$b" in "$me"*) selfauth=$((selfauth + 1)); continue ;; esac
      low=$(printf '%s' "$b" | tr 'A-Z' 'a-z')
      # ADDRESSING, read from the filename. Deliberately PERMISSIVE about what counts as
      # addressed to me and CONSERVATIVE about what it will accuse: a name this parser cannot
      # read is counted as unaddressed and printed, never graded. ⛔ That is the OPPOSITE of C9's
      # fall-through-to-strict, and on purpose -- C9's uncertainty accuses ME, this one's would
      # accuse a PEER, and a false accusation across trunks costs more than a missed row.
      case "$low" in
        *to-all*|*all-trunks*|*to-fleet*|*to-pro*|*-pro-*|*professional*) ;;
        *) unaddressed=$((unaddressed + 1)); continue ;;
      esac
      d=$(printf '%s' "$b" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | tail -1)
      if [ -z "$d" ]; then undated=$((undated + 1)); continue; fi
      if [ "$d" \< "$epoch" ]; then pre=$((pre + 1)); continue; fi
      graded=$((graded + 1))
      case "$ibox" in *$'\n'"$b"$'\n'*) continue ;; esac
      absent=$((absent + 1))
      names="$names
  UNRECEIVED $dir/exchange/outbox/$b -- addressed here by its own filename, absent from $inbox"
    done <<< "$(ls -1 "$tree/exchange/outbox" 2>/dev/null)"
  done < "$roster"
  if [ "$trees" -eq 0 ]; then
    fail C31 "zero sender trees resolved from $roster -- an empty population is UNKNOWN, never clean"
  elif [ "$absent" -gt 0 ]; then
    printf '%s\n' "$names"
    fail C31 "$absent of $graded sibling letter(s) dated on or after $epoch address this trunk and never reached $inbox. ⛔ DO NOT COPY THEM IN -- a receiver copying its own mail forges the sender's act. Read them where they lie, act, and tell the sender their courier did not run."
  else
    pass C31 "receiving direction reconciled: $graded sibling letter(s) on or after $epoch addressed here, all present in $inbox; $trees sender tree(s). NOT GRADED, PRINTED SO THE POPULATION IS HONEST: $pre pre-epoch, $undated undated, $unaddressed not addressed to this trunk by filename, $selfauth authored here, $noout DELIVER row(s) with no readable outbox. ⚠️ FILENAME ADDRESSING ONLY -- a letter whose body names Professional but whose filename does not is invisible to this check, and mail sent by SendMessage or spoken live is outside it entirely. ⛔ AND THIS GREEN MEANS ONLY *PRESENT IN THE INBOUND, BY WHATEVER HAND*. It was built as a proxy for \"the sender's outbound path works\" and a THIRD-PARTY CARRY BREAKS THAT PROXY: on 2026-09-03 a peer hand-couriered all five missing letters, so this check greened while both senders' outbound stayed exactly as broken -- one with no live session, one (measured, Secretary) with NO COURIER AT ALL, no script, no hook, no runner. Whether a trunk CAN speak without a person thinking of it is a FOURTH direction that neither this check nor fleet-connect measures, and nobody owns it."
  fi
}

# --- Check 32: QUERY BEFORE YOU WRITE, AS A CHECKED FIELD. The id was RESERVED 2026-09-04 for exactly
# this (wiki/tracker/wayfinder-routing-budgets-and-context-2026-09-04.md:67: "a `queried:` line in
# every letter's self-check, with the query; lint candidate C32"); a seat minted over it on 09-07 and
# renamed its check to C33 the same hour (scripts/audit/retrievable_check.py: "The reserved `C32`
# candidate is NOT vacated by this rename; it keeps its id and needs an owner."). This is the owner.
# The field name was settled fleet-wide by the council on 2026-09-05 (this trunk's log, 13:1x entry:
# "the one field name fleet-wide is `queried:`"; CFL 0732a0c9: "an empty result is a good value, a
# MISSING field means nobody looked").
#
# BUILT 2026-09-12 12:3x by the wikiskills-improve subagent of 682d274b, ON A MEASURED GAP, not a
# feeling: [measured 12:3x] 114 outbox letters carry a 2026-09-05..09-12 date in their filename and
# ONE carries a `queried:` line; 115 letters were git-added on/after 2026-09-05 (of 355 in the
# outbox). The rule was ratified, written into /wake Step 0b, quoted in two maps -- and nothing could
# fire on it. Jon, 2026-09-11 16:1x, verbatim: "Query the wiki by default rather than grep." A rule
# with no check is prose; the two seats that wrote the rule were the first two to break it.
#
# THE BREACH: a letter git-added on/after the epoch with no `queried:` field carrying a value.
# What it does NOT grade: whether the query was actually run, whether its top hit bears on the claim
# (ground-before-stating's open gap, wikiskills-improve SKILL.md 4.1), tracker rows, or anything sent
# by SendMessage or spoken live. Same mechanism as C16: it requires that the SENTENCE was written and
# the honesty happens in composing it. `queried: none -- <reason>` is a valid value -- a letter that
# names no query and says why has looked.
#
# ERROR DIRECTION: over-matches on purpose. Every post-epoch letter is asked, receipts included.
# sendmessage-record captures are skipped by kind and COUNTED (P4-6), as in C16. Cost of a false
# positive: one line. Cost of a false negative: a finding nobody looked for goes out as if they had.
# EPOCH BY GIT ADD-DATE, never filename (C16 break 1). No add-date => graded, fail-closed.
# Pre-epoch letters are counted and printed, never swept -- "Yeah no deletion" governs.
# The name list is CAPPED (LINT_QUERIED_SHOW, default 12) because the first real run prints ~110
# names; the COUNT is never capped, and the cap is printed beside it so a reader knows it is there.
check_queried_field() {
  local box epoch field cap map f base d fm when graded=0 bad=0 skipped=0 nodate=0 captures=0 shown=0
  box="${LINT_OUTBOX:-exchange/outbox}"
  epoch="${LINT_QUERIED_EPOCH:-2026-09-05}"
  field="${LINT_QUERIED_FIELD:-queried}"
  cap="${LINT_QUERIED_SHOW:-12}"
  if [ ! -d "$box" ]; then
    fail C32 "outbox absent at $box -- the graded surface is UNKNOWN, and UNKNOWN dominates a PASS"
    return
  fi
  map=$(mktemp)
  git log --diff-filter=A --format='@%as' --name-only -- "$box" 2>/dev/null \
    | awk '/^@/{d=substr($0,2);next} NF{n=$0;sub(/.*\//,"",n);seen[n]=d} END{for(k in seen)print k"\t"seen[k]}' \
    > "$map" 2>/dev/null
  for f in "$box"/*.md; do
    [ -e "$f" ] || continue
    if sed -n '1,12p' "$f" | grep -qiE '^kind: *sendmessage-record'; then captures=$((captures+1)); continue; fi
    base=$(basename "$f")
    d=$(awk -F'\t' -v n="$base" '$1==n{print $2; exit}' "$map")
    [ -n "$d" ] || nodate=$((nodate+1))
    if [ -n "$d" ] && [ "$d" \< "$epoch" ]; then skipped=$((skipped+1)); continue; fi
    graded=$((graded+1))
    # Frontmatter OR body -- letters carry the field either way. A VALUE is required: a present-and-
    # blank field is the cheapest way to launder this check (C16 case c), so it is refused explicitly.
    fm=$(grep -iE "^[[:space:]]*[-*>]*[[:space:]]*\**${field}\**:[[:space:]]*[^[:space:]]" "$f" | head -1)
    if [ -z "$fm" ]; then
      bad=$((bad+1))
      if [ "$shown" -lt "$cap" ]; then
        if [ -n "$d" ]; then when="git-added $d"; else when="UNDATED (no add-date; graded fail-closed)"; fi
        echo "  NO QUERIED $base -- $when, no ${field}: line with a value; nobody can tell whether anyone looked"
        shown=$((shown+1))
      fi
    fi
  done
  rm -f "$map"
  if [ "$bad" -gt "$shown" ]; then
    echo "  ... and $((bad-shown)) more NO QUERIED letter(s) not named (LINT_QUERIED_SHOW=$cap caps the NAMES, never the COUNT)"
  fi
  if [ "$bad" -gt 0 ]; then
    fail C32 "$bad of $graded post-epoch letter(s) carry no ${field}: value -- the query-before-build rule (council 2026-09-05) was prose until this line ($skipped pre-epoch by git add-date, $nodate with no add-date graded fail-closed, $captures sendmessage-record capture(s) skipped by kind, epoch $epoch)"
  elif [ "$graded" -eq 0 ]; then
    pass C32 "VACUOUS -- NOTHING GRADED: 0 post-epoch letter(s) existed to grade ($skipped pre-epoch by git add-date, $nodate with no add-date, $captures capture(s) skipped by kind, epoch $epoch). NOT evidence that anyone queried."
  else
    pass C32 "query-before-build wired on the letter surface: $graded post-epoch letter(s) all carry a ${field}: value ($skipped pre-epoch by git add-date, $nodate with no add-date graded fail-closed, $captures capture(s) skipped by kind, epoch $epoch). NOT GRADED: whether the query ran, whether its top hit bears on the letter's claim, tracker rows, SendMessage, speech."
  fi
}
