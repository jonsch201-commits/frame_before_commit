#!/usr/bin/env bash
# fetch_asops.sh -- download the current ASOP catalogue and extract to text.
#
# Source of URLs: http://www.actuarialstandardsboard.org/standards-of-practice/
# fetched 2026-08-07. ASOPs are public documents published by the Actuarial
# Standards Board. Nothing here touches work systems, work email, or client data.
#
# Output:
#   raw/asops/pdf/asopNNN_DDD.pdf   -- the PDF as published
#   raw/asops/txt/asopNNN_DDD.txt   -- pdftotext -layout extraction
#   raw/asops/MANIFEST.tsv          -- number, title, url, bytes, sha256, txt bytes
#
# raw/ is gitignored. Re-running is safe: existing PDFs are not re-downloaded.

set -uo pipefail
cd "$(dirname "$0")/.."

PDF_DIR="raw/asops/pdf"
TXT_DIR="raw/asops/txt"
MANIFEST="raw/asops/MANIFEST.tsv"
URLS="raw/asops/urls.tsv"

mkdir -p "$PDF_DIR" "$TXT_DIR"

printf 'asop\ttitle\turl\tpdf_bytes\tsha256\ttxt_bytes\tstatus\n' > "$MANIFEST"

ok=0; fail=0; skip=0

while IFS=$'\t' read -r num title url; do
  [ -z "${num:-}" ] && continue
  case "$num" in \#*) continue ;; esac

  base="$(basename "$url")"
  pdf="$PDF_DIR/$base"
  txt="$TXT_DIR/${base%.pdf}.txt"

  if [ -s "$pdf" ]; then
    status="cached"; skip=$((skip+1))
  else
    curl -fsSL --max-time 60 -o "$pdf" "$url"
    if [ $? -ne 0 ] || [ ! -s "$pdf" ]; then
      printf '%s\t%s\t%s\t0\t-\t0\tDOWNLOAD_FAILED\n' "$num" "$title" "$url" >> "$MANIFEST"
      rm -f "$pdf"; fail=$((fail+1)); echo "FAIL  ASOP $num  $url" >&2; continue
    fi
    status="downloaded"
  fi

  # A truthful PDF starts with %PDF. An HTML 404 page does not.
  if ! head -c 4 "$pdf" | grep -q '%PDF'; then
    printf '%s\t%s\t%s\t%s\t-\t0\tNOT_A_PDF\n' "$num" "$title" "$url" "$(wc -c < "$pdf")" >> "$MANIFEST"
    fail=$((fail+1)); echo "FAIL  ASOP $num  not a PDF" >&2; continue
  fi

  pdftotext -layout "$pdf" "$txt" 2>/dev/null

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$num" "$title" "$url" \
    "$(wc -c < "$pdf")" \
    "$(sha256sum "$pdf" | cut -d' ' -f1)" \
    "$( [ -f "$txt" ] && wc -c < "$txt" || echo 0 )" \
    "$status" >> "$MANIFEST"
  ok=$((ok+1))
done < "$URLS"

echo "---"
echo "ok=$ok (of which cached=$skip)  failed=$fail"
echo "manifest: $MANIFEST"
