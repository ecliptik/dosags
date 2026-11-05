#!/usr/bin/env bash
# ratchet-cell.sh -- one tests/ratchet.yaml unit: run a DOSBox-X cell, then write every figure
# the ratchet reads to OUT/facts.txt ("RATCHET k=v" lines from ratchet-facts.py and, when the
# binary carries ags patch 0250, journeys.py). LAB ONLY.
#
#   tests/harness/ratchet-cell.sh OUT lab   <run-dosbox.sh args...>     # headless cell (lab-cell.sh)
#   tests/harness/ratchet-cell.sh OUT click <click-cell.sh args...>     # interactive click/key cell
#
# The cell goes to OUT/cell. Exit status is the cell's; facts.txt is written whenever the cell left
# a RUNMANI.LOG (a figure it cannot give is NA, which a ratchet check reads as ERROR).
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:?out dir}"; MODE="${2:?lab|click}"; shift 2
mkdir -p "$OUT"
CELL="$OUT/cell"
case "$MODE" in
    lab)   "$HARNESS/lab-cell.sh" "$CELL" "$@"; rc=$? ;;
    click) "$HARNESS/click-cell.sh" "$CELL" "$@"; rc=$? ;;
    *) echo "ratchet-cell.sh: mode must be lab or click" >&2; exit 2 ;;
esac
{
    python3 "$HARNESS/ratchet-facts.py" "$CELL"
    if [[ "$MODE" == click ]]; then
        python3 "$HARNESS/journeys.py" "$CELL" --host-clicks "$CELL/CLICKS.LOG"
    else
        python3 "$HARNESS/journeys.py" "$CELL"
    fi
} > "$OUT/facts.txt" 2>&1
/usr/bin/grep '^RATCHET' "$OUT/facts.txt"
exit $rc
