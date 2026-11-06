#!/usr/bin/env bash
# witness-ftp-check.sh -- run before committing result dirs: OCR every STAGED WITNESS-send/collect frame and refuse
# (exit 1) if one shows an FTP session ("Password", "Login successful", "230 ", "331 "). Prints file names only, never
# the OCR text (it may hold a credential). Operator decision 2026-11-06, after 5 frames from 2026-09-28 leaked one.
set -u
command -v tesseract >/dev/null || { echo "witness-ftp-check: tesseract missing -- cannot check" >&2; exit 2; }
bad=0
while IFS= read -r -d '' f; do
  if tesseract "$f" - 2>/dev/null | grep -q -i -E 'password|login successful|^ *230 |^ *331 '; then
    echo "FTP SESSION VISIBLE: $f"; bad=1; fi
done < <(git diff --cached --name-only -z --diff-filter=AM -- '*WITNESS-send.jpg' '*WITNESS-collect.jpg')
exit $bad
