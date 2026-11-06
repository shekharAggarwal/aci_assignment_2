#!/usr/bin/env bash
# Builds the single ZIP the brief requires: Question1_Group.ipynb plus one PDF per member.
# Usage: ./make_submission_zip.sh <number-of-members> <pdf-folder>
# Example: ./make_submission_zip.sh 4 pdfs
set -euo pipefail

members="${1:?Give the number of group members}"
pdf_dir="${2:?Give the folder holding the PDFs of all members}"
notebook="Question1_Group.ipynb"
zip_name="Group107_Assignment2.zip"

[ -f "$notebook" ] || { echo "Missing $notebook" >&2; exit 1; }

shopt -s nullglob
pdfs=("$pdf_dir"/*.pdf)
if [ "${#pdfs[@]}" -ne "$members" ]; then
  echo "Found ${#pdfs[@]} PDF(s) for $members member(s). Every member needs one PDF." >&2
  exit 1
fi

for pdf in "${pdfs[@]}"; do
  name="$(basename "$pdf")"
  if ! [[ "$name" =~ ^20[0-9]{2}[A-Za-z0-9]+\.pdf$ ]]; then
    echo "$name does not look like a BITS ID filename such as 2025XXXXXX.pdf" >&2
    exit 1
  fi
done

rm -f "$zip_name"
zip -j -X -q "$zip_name" "$notebook" "${pdfs[@]}"   # -j: no folders, -X: no macOS extras

count="$(unzip -Z1 "$zip_name" | wc -l | tr -d ' ')"
expected=$((members + 1))
if [ "$count" -ne "$expected" ]; then
  echo "ZIP holds $count file(s), expected $expected." >&2
  exit 1
fi

echo "Created $zip_name with $count files:"
unzip -Z1 "$zip_name"
