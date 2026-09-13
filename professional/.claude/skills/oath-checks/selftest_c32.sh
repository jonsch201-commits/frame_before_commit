#!/usr/bin/env bash
# selftest_c32.sh -- prove C32 (check_queried_field) can FAIL and can PASS, with a control per negative.
# Run from any trunk: bash .claude/skills/oath-checks/selftest_c32.sh    (exit 0 = all fixtures held; 3 = broken)
# Fixtures live in mktemp dirs; the temp git repo below exists only to give a letter a real ADD-DATE,
# because C32 grades by git add-date and never by filename (C16 break 1). Nothing here touches the
# calling repository's index.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OATH_FAILS=0
pass() { echo "PASS [$1] $2"; }
fail() { echo "FAIL [$1] $2"; OATH_FAILS=$((OATH_FAILS+1)); }
# shellcheck source=/dev/null
. "$HERE/oath_checks.sh"
declare -F check_queried_field >/dev/null || { echo "SELFTEST BROKEN: check_queried_field is not defined by $HERE/oath_checks.sh"; exit 3; }

n=0; ok=0
say() { n=$((n+1)); ok=$((ok+1)); echo "OK   $1"; }
die() { echo "SELFTEST BROKEN: $1"; rm -rf "${BOX:-}" "${EMPTY:-}"; exit 3; }

BOX=$(mktemp -d)
# a: planted breach -- a post-epoch letter (no add-date => graded fail-closed) with no queried: field -> FAIL, named
printf -- '---\ntitle: finding\nself-check: ran C9 here first\n---\nCFL letter is missing its receipt.\n' > "$BOX/pro-to-cfl-x-2999-01-01.md"
OUT=$(LINT_OUTBOX="$BOX" check_queried_field)
echo "$OUT" | grep -q "FAIL \[C32\]" && say "C32 can fail (post-epoch letter, no queried: field)" || die "C32 cannot fail"
echo "$OUT" | grep -q "NO QUERIED pro-to-cfl-x-2999-01-01.md" && say "C32 names the letter it fails" || die "C32 failed without naming the letter"
echo "$OUT" | grep -q "1 with no add-date graded fail-closed" && say "C32 prints the no-add-date count (fail-closed, not skipped)" || die "C32 hid the no-add-date population"
# b: clean fixture -- same letter WITH a queried: value -> PASS. A check that cannot pass is a wall.
printf -- '---\ntitle: finding\nqueried: "CFL receipt for letter X" -> exchange/inbound/x.md:1-9 (rank 1), STALE=no\n---\nCFL letter is missing its receipt.\n' > "$BOX/pro-to-cfl-x-2999-01-01.md"
OUT=$(LINT_OUTBOX="$BOX" check_queried_field)
echo "$OUT" | grep -q "PASS \[C32\]" && echo "$OUT" | grep -q "wired on the letter surface" && say "C32 passes on a queried: value in frontmatter" || die "C32 cannot pass on a declared query"
# b2: the field in the BODY, as a bullet, bolded -- the shape the one real instance uses -> PASS
printf -- '---\ntitle: finding\n---\nBody.\n- **queried:** "secret PR 4" -> history.jsonl:2834 (1)\n' > "$BOX/pro-to-cfl-x-2999-01-01.md"
OUT=$(LINT_OUTBOX="$BOX" check_queried_field)
echo "$OUT" | grep -q "PASS \[C32\]" && say "C32 accepts the field in the body as a bolded bullet (the real instance's shape)" || die "C32 rejects the body-bullet shape the fleet actually writes"
# b3: an honest 'none -- <reason>' IS a value -> PASS (an empty result is a value; saying why is looking)
printf -- '---\ntitle: finding\nqueried: none -- receipt-only letter, no claim made\n---\nReceived.\n' > "$BOX/pro-to-cfl-x-2999-01-01.md"
OUT=$(LINT_OUTBOX="$BOX" check_queried_field)
echo "$OUT" | grep -q "PASS \[C32\]" && say "C32 accepts 'queried: none -- <reason>' as a value" || die "C32 refuses an honest none-with-reason"
# c: control for b -- a PRESENT-AND-BLANK field must not buy a pass
printf -- '---\ntitle: finding\nqueried:\n---\nCFL letter is missing its receipt.\n' > "$BOX/pro-to-cfl-x-2999-01-01.md"
OUT=$(LINT_OUTBOX="$BOX" check_queried_field)
echo "$OUT" | grep -q "FAIL \[C32\]" && say "C32 rejects an empty queried: field (control for the pass)" || die "C32 accepts a blank field"
# d: PRE-epoch by real git add-date -> not graded, counted, VACUOUS pass
rm -f "$BOX"/*.md
( cd "$BOX" && git init -q . && git config user.email s@t && git config user.name s ) >/dev/null 2>&1
printf -- '---\ntitle: old\n---\nno query here\n' > "$BOX/pro-to-cfl-old.md"
( cd "$BOX" && git add -A && GIT_AUTHOR_DATE='2026-08-24T12:00:00' GIT_COMMITTER_DATE='2026-08-24T12:00:00' git commit -qm old ) >/dev/null 2>&1
OUT=$(cd "$BOX" && LINT_OUTBOX="." check_queried_field)
echo "$OUT" | grep -q "PASS \[C32\]" && echo "$OUT" | grep -q "1 pre-epoch" && say "C32 leaves a letter git-added pre-epoch ungraded and prints the count" || die "C32 graded or hid a pre-epoch letter"
echo "$OUT" | grep -q "VACUOUS" && say "C32 reports the zero-graded state as VACUOUS, not as wired" || die "C32 printed a normal pass over zero graded letters"
# d2: control for d -- FILENAME says pre-epoch, add-date is post-epoch -> GRADED and FAILS (C16 break 1)
printf -- '---\ntitle: new\n---\nno query here\n' > "$BOX/pro-to-cfl-x-2026-08-29.md"
( cd "$BOX" && git add -A && GIT_AUTHOR_DATE='2026-09-06T12:00:00' GIT_COMMITTER_DATE='2026-09-06T12:00:00' git commit -qm new ) >/dev/null 2>&1
OUT=$(cd "$BOX" && LINT_OUTBOX="." check_queried_field)
echo "$OUT" | grep -q "FAIL \[C32\]" && echo "$OUT" | grep -q "NO QUERIED pro-to-cfl-x-2026-08-29.md" && say "C32 grades by git add-date, not the author-controlled filename" || die "C32 skipped a post-epoch letter on its filename"
# f: a sendmessage-record capture is skipped BY KIND and counted, never graded
rm -f "$BOX"/*.md
printf -- '---\nkind: sendmessage-record\n---\ncaptured send, no query field\n' > "$BOX/pro-to-cfl-msg-2999-01-01T000000-x.md"
OUT=$(LINT_OUTBOX="$BOX" check_queried_field)
echo "$OUT" | grep -q "PASS \[C32\]" && echo "$OUT" | grep -q "1 capture(s) skipped by kind" && say "C32 skips a sendmessage-record capture by kind and prints the count" || die "C32 graded or hid a capture"
# e: absent outbox -> FAIL (UNKNOWN dominates a PASS)
OUT=$(LINT_OUTBOX="/nonexistent/outbox-c32" check_queried_field)
echo "$OUT" | grep -q "FAIL \[C32\]" && say "C32 fails on an unreadable outbox" || die "C32 passes when it cannot read the outbox"
# g: the name cap caps NAMES and never the COUNT
rm -rf "$BOX"; BOX=$(mktemp -d)
for i in 1 2 3; do printf -- '---\ntitle: t\n---\nno query\n' > "$BOX/pro-to-x-$i.md"; done
OUT=$(LINT_OUTBOX="$BOX" LINT_QUERIED_SHOW=1 check_queried_field)
[ "$(echo "$OUT" | grep -c '^  NO QUERIED ')" -eq 1 ] && echo "$OUT" | grep -q "2 more NO QUERIED" && echo "$OUT" | grep -q "FAIL \[C32\] 3 of 3" && say "C32's name cap hides names only; the count and the remainder are printed" || die "C32's cap changed the count"
rm -rf "$BOX"
echo "SELFTEST C32: $ok of $n fixtures held (both verdicts exercised; a control beside every negative)"
[ "$ok" -eq "$n" ] || exit 3
exit 0
