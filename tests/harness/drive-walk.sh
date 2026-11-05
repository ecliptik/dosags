#!/usr/bin/env bash
# drive-walk.sh -- keep a no-AutoPilot AGS game "in play" during a run-hw.sh cell by
# clicking at wandering points, so the picture changes and the cell measures drawing
# rather than an idle room. Run it in the background BEFORE run-hw.sh reaches the
# launch step; it waits for run-hw.sh to take the input lock and stops when it lets go.
#
#   tests/harness/drive-walk.sh <TAG> [WARMUP_S=25] [PERIOD_S=8] [MAX_CLICKS=60]
#
# The mouse on this target is relative-only (PS/2), so positions are not known. That is
# deliberate and enough: AGS walks the player to the nearest walkable point for any click,
# and it clamps the pointer to the game area, so relative moves that keep sweeping left,
# right, up and down give a click somewhere new every time. What is NOT enough is an
# instant click: a low-fps game can miss a press and release that fall between two polls,
# so every click is press, dwell, release (see the memory note on low-fps input).
#
# Every action is logged with a millisecond UTC timestamp to $DRIVE_LOG (default
# ./DRIVE.LOG); each click line carries down_at= (the instant before the press was sent)
# and the exit codes of the press and release sends, so a refused or failed send is not
# counted as a click that reached the target. Whether it actually kept the game in play is
# judged from the run's own numbers (presents_real as a fraction of render passes), not
# from this script.
#
# This script clicks for as long as run-hw.sh holds the input lock, which is not the
# game's input window (it can end before the game quits, or run on at the DOS prompt).
# tests/harness/drive-align.py RESULTS_DIR places the window on this log's clock after
# the run, from the engine's own click journeys, and classes every click; compare host
# clicks with mouse_presses_hw only through it. The gap after each click is jittered
# (gap= in the log) so that alignment is unique.
set -u
TAG="${1:?usage: drive-walk.sh <TAG> [WARMUP_S] [PERIOD_S] [MAX_CLICKS]}"
WARMUP_S="${2:-25}"
PERIOD_S="${3:-8}"
MAX_CLICKS="${4:-60}"
HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V="${VCCTRL_BIN:-$HARNESS_DIR/../../../vcctrl/bin/vcctrl}"
OWNER="run-hw-$TAG"
DRIVE_LOG="${DRIVE_LOG:-./DRIVE.LOG}"

log() { printf '%s %s\n' "$(date -u +%H:%M:%S.%3N)" "$*" | tee -a "$DRIVE_LOG" >&2; }
owner_now() { "$V" lock status 2>/dev/null | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("owner"))
except Exception: print("UNKNOWN")' 2>/dev/null; }
vc() { "$V" "$@" --as "$OWNER"; }

log "waiting for the input lock to be taken by $OWNER"
until [[ "$(owner_now)" == "$OWNER" ]]; do sleep 2; done
log "lock is ${OWNER}'s; warming up ${WARMUP_S}s (RUN.BAT is typed, AGS is starting)"
sleep "$WARMUP_S"

# Home the pointer into the top-left corner; PS/2 deltas clamp at the screen edge.
for _ in 1 2 3 4; do vc mouse move -120 -120 >/dev/null 2>&1; done
log "homed to top-left"

# (dx dy) relative moves, sweeping the whole game area.
MOVES=("100 150" "180 0" "0 -70" "-190 0" "0 90" "-90 0" "190 -40" "-150 -50" "60 120" "170 0")
i=0
while (( i < MAX_CLICKS )); do
    [[ "$(owner_now)" == "$OWNER" ]] || { log "lock no longer ${OWNER}'s -- run ended, stopping after $i clicks"; break; }
    read -r dx dy <<<"${MOVES[$(( i % ${#MOVES[@]} ))]}"
    vc mouse move "$dx" "$dy" >/dev/null 2>&1
    t_down="$(date -u +%H:%M:%S.%3N)"
    vc mouse down left >/dev/null 2>&1; rc_down=$?
    sleep 0.4
    vc mouse up left >/dev/null 2>&1; rc_up=$?
    i=$(( i + 1 ))
    # Jittered gap (0.6-1.4 x PERIOD_S, from a generator seeded by the tag, so a rerun of the same tag
    # repeats it): a fixed cadence lets drive-align pair host and engine clicks at several whole-period
    # offsets (C3512, LAB-JOURNEYS 8.29); irregular gaps have one alignment.
    GAP="$(python3 -c "import random,sys; r=random.Random(sys.argv[1]+':'+sys.argv[2]); print('%.2f' % (float(sys.argv[3]) * r.uniform(0.6, 1.4)))" "$TAG" "$i" "$PERIOD_S")"
    log "click $i  move $dx $dy  down_at=$t_down rc_down=$rc_down rc_up=$rc_up gap=$GAP"
    sleep "$GAP"
done
vc mouse release-all >/dev/null 2>&1 || true
log "done: $i clicks"
