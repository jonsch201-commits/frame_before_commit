#!/usr/bin/env bash
# asop.sh -- search and read the local ASOP corpus.
#
#   ./scripts/asop.sh list                     # every standard, with text size
#   ./scripts/asop.sh show 56                  # print ASOP 56 in full
#   ./scripts/asop.sh sec 1 2.1                # print one section of one ASOP
#   ./scripts/asop.sh find "reliance on others" # search ALL standards, with ASOP number + line
#   ./scripts/asop.sh find -i modeling 56 43   # search only the standards listed
#   ./scripts/asop.sh phrase "reliance on others"  # multi-word phrases across line breaks
#
# ⚠️ `find` searches line by line. pdftotext -layout preserves the PDF's line
# wrapping, so a phrase split across two lines will NOT match -- "reliance on
# others" really is split at asop056:684/685. Use `phrase` for anything longer
# than one word; it collapses whitespace first and reports the ASOP, not a line
# number. Use `find` for single words and regexes, where line numbers are useful.
#
# The corpus is built by fetch_asops.sh and lives in raw/asops/ (gitignored).
# ASOPs are copyright the Actuarial Standards Board. This is a local reading
# copy for one actuary; it is not redistributed and this repo has no remote.

set -uo pipefail
cd "$(dirname "$0")/.."

TXT="raw/asops/txt"
MAN="raw/asops/MANIFEST.tsv"

[ -d "$TXT" ] || { echo "No corpus. Run: bash scripts/fetch_asops.sh" >&2; exit 1; }

# Map an ASOP number to its text file. Primary route is the manifest's URL
# basename; rows sourced from CFL carry a note instead of a URL, so fall back to
# globbing the txt dir by zero-padded number.
path_for() {
  local n="$1" p
  p="$(awk -F'\t' -v n="$n" 'NR>1 && $1==n {
    f=$3; sub(/.*\//,"",f); sub(/\.pdf$/,".txt",f); print "'"$TXT"'/" f; exit
  }' "$MAN")"
  [ -n "$p" ] && [ -f "$p" ] && { printf '%s\n' "$p"; return; }
  # Fallback: asop009_105.txt, asop046and047repeal_219.txt, asop-021_183.txt …
  p="$(ls "$TXT"/asop-?0*"$n"_*.txt "$TXT"/asop$(printf '%03d' "$n")*.txt 2>/dev/null | head -1)"
  [ -n "$p" ] && printf '%s\n' "$p"
}

title_for() { awk -F'\t' -v n="$1" 'NR>1 && $1==n {print $2; exit}' "$MAN"; }

cmd="${1:-list}"; shift 2>/dev/null || true

case "$cmd" in

  list)
    printf '%-5s %-72s %9s\n' ASOP TITLE TEXT
    awk -F'\t' 'NR>1 {printf "%-5s %-72.72s %8dB\n", $1, $2, $6}' "$MAN" | sort -n
    awk -F'\t' 'NR>1{n++; b+=$6} END{printf "\n%d standards, %.2f MB of searchable text\n", n, b/1048576}' "$MAN"
    ;;

  show)
    p="$(path_for "${1:?usage: asop.sh show <number>}")"
    [ -n "$p" ] && [ -f "$p" ] || { echo "ASOP $1 not in corpus." >&2; exit 1; }
    cat "$p"
    ;;

  sec)
    n="${1:?usage: asop.sh sec <asop> <section>}"; s="${2:?}"
    p="$(path_for "$n")"
    [ -n "$p" ] && [ -f "$p" ] || { echo "ASOP $n not in corpus." >&2; exit 1; }
    # Print from the section heading to the next same-or-shallower heading.
    awk -v s="$s" '
      $0 ~ "^[[:space:]]*"s"([[:space:]]|--|—)" { on=1 }
      on && ++ln > 1 && /^[[:space:]]*[0-9]+\.[0-9]*[[:space:]]/ && $0 !~ "^[[:space:]]*"s"([[:space:]]|--|—)" { exit }
      on
    ' "$p"
    ;;

  find)
    # Collect flags, then the pattern, then optional ASOP numbers to scope to.
    flags=(); while [[ "${1:-}" == -* ]]; do flags+=("$1"); shift; done
    pat="${1:?usage: asop.sh find [flags] <pattern> [asop ...]}"; shift
    targets=("$@")
    if [ "${#targets[@]}" -eq 0 ]; then
      mapfile -t targets < <(awk -F'\t' 'NR>1{print $1}' "$MAN" | sort -n)
    fi
    hits=0
    for n in "${targets[@]}"; do
      p="$(path_for "$n")"; [ -n "$p" ] && [ -f "$p" ] || continue
      out="$(grep -n "${flags[@]+"${flags[@]}"}" -- "$pat" "$p" 2>/dev/null)" || continue
      [ -z "$out" ] && continue
      c=$(printf '%s\n' "$out" | wc -l)
      hits=$((hits + c))
      printf '\n\033[1m== ASOP %s -- %s  (%d)\033[0m\n' "$n" "$(title_for "$n")" "$c"
      printf '%s\n' "$out" | sed 's/^/  /'
    done
    printf '\n%d matching lines.\n' "$hits"
    ;;

  phrase)
    # Collapse each standard to one whitespace-normalised line, then match.
    # Defeats pdftotext -layout's line wrapping, at the cost of line numbers.
    pat="${1:?usage: asop.sh phrase <words> [asop ...]}"; shift
    targets=("$@")
    if [ "${#targets[@]}" -eq 0 ]; then
      mapfile -t targets < <(awk -F'\t' 'NR>1{print $1}' "$MAN" | sort -n)
    fi
    found=0
    for n in "${targets[@]}"; do
      p="$(path_for "$n")"; [ -n "$p" ] && [ -f "$p" ] || continue
      # tr -d '\r' FIRST. pdftotext emits CRLF on Windows; without stripping it,
      # a phrase spanning a line break keeps a stray CR in the middle and
      # SILENTLY never matches. That bug hid a real ASOP 1 quote for one session.
      hits="$(tr -d '\r' < "$p" | tr '\n' ' ' | tr -s ' ' | grep -o -i -- ".\{0,70\}$pat.\{0,70\}" 2>/dev/null)" || continue
      [ -z "$hits" ] && continue
      found=$((found + $(printf '%s\n' "$hits" | wc -l)))
      printf '\n\033[1m== ASOP %s -- %s\033[0m\n' "$n" "$(title_for "$n")"
      printf '%s\n' "$hits" | sed 's/^/  …/; s/$/…/'
    done
    printf '\n%d occurrences across %d standards searched.\n' "$found" "${#targets[@]}"
    ;;

  *) sed -n '2,20p' "$0"; exit 1 ;;
esac
