#!/usr/bin/env bash
# lab-cell.sh -- run one headless DOSBox-X cell through run-dosbox.sh and keep its
# evidence: OUT_DIR/{RUN.BAT,RUNMANI.LOG,STDOUT.TXT,SDLDBG.LOG,run.log,stage}. LAB ONLY.
#
#   tests/harness/lab-cell.sh <OUT_DIR> <run-dosbox.sh args...>
#
# e.g. lab-cell.sh results/JMSI-2026-09-23 5days --fixed-timestep --sb-live \
#        --conf confs/dosbox-x-fast-opl3.conf --ags-arg --startr --ags-arg 3 \
#        --env DOSAGS_TAS_AUTO_EXIT_TICK=8000 --env DOSAGS_UR3_STALL_EVERY=150
# Exit 1 if the run left no RUNMANI.LOG (a crash, a hang cut by the timeout).
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:?out dir}"; shift
mkdir -p "$OUT"
# Host-wide DOSBox-X lock for the whole cell (2026-09-23): EXCLUSIVE at cycles=max (a timing figure
# is only worth reading if no other worker's DOSBox-X ran beside it), SHARED when --conf runs at fixed
# cycles (hub rule bb5482c; see lab-lock.sh). A no-op inside a series that already holds it.
# --conf may be given relative to the repo root (tests/harness/confs/..., the form ratchet.sh can
# verify as fixed cycles) or to this directory; run-dosbox.sh runs from here, so make it absolute.
REPO="$(cd "$HARNESS/../.." && pwd)"; A=()
while [[ $# -gt 0 ]]; do
    if [[ "$1" == --conf && $# -ge 2 && "$2" != /* && ! -f "$HARNESS/$2" && -f "$REPO/$2" ]]; then A+=(--conf "$REPO/$2"); shift 2
    else A+=("$1"); shift; fi
done
set -- "${A[@]}"
source "$HARNESS/lab-lock.sh"; lab_lock_cell lab-cell.sh "$@" || exit $?
trap lab_lock_release EXIT
# --no-host-input (hub ee910e5 / main 05c4f4e0): nothing on the host drives a lab cell (no xdotool;
# input, if any, comes from inside the game), so a fixed-cycles cell may run under the SHARED lock
# even with a display. Click cells go through click-cell.sh, which is always EXCLUSIVE.
( cd "$HARNESS" && ./run-dosbox.sh "$@" --no-host-input ) > "$OUT/run.log" 2>&1
STAGE="$(tail -n 1 "$OUT/run.log")"
echo "$STAGE" > "$OUT/stage"
[[ -d "$STAGE" ]] || { echo "lab-cell: no stage dir (see $OUT/run.log)" >&2; exit 1; }
for f in RUN.BAT RUNMANI.LOG STDOUT.TXT SDLDBG.LOG AUTOPLT.LOG; do cp "$STAGE/$f" "$OUT/" 2>/dev/null || true; done
# DOS_PORT_LOG=1 writes the SDL debug log to LOGS\SDLDBG.LOG under --user-data-dir c:\
[[ -f "$STAGE/LOGS/SDLDBG.LOG" ]] && cp "$STAGE/LOGS/SDLDBG.LOG" "$OUT/SDLDBG.LOG"
[[ -f "$OUT/RUNMANI.LOG" ]] || { echo "lab-cell: no RUNMANI.LOG" >&2; exit 1; }
exit 0
