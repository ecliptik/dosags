#!/usr/bin/env bash
# lab-drive-xdotool.sh -- the DOSBox-X stand-in for drive-walk.sh (lab only, no vcctrl).
#
# drive-walk.sh keeps a no-AutoPilot game in play on real hardware by clicking at wandering
# points through vcctrl. A lab run of the same cell (LAB-METRIC.md) needs the same kind of
# input on the emulator so its WORK counts describe a walking scene, not an idle room. This
# does that with xdotool on the private display run-dosbox.sh --interactive opened.
#
#   DOSBOX_DISPLAY_NUM=221 tests/harness/lab-drive-xdotool.sh walk  [WARMUP_S=25] [PERIOD_S=2] [MAX_CLICKS=90]
#   DOSBOX_DISPLAY_NUM=221 tests/harness/lab-drive-xdotool.sh click X Y [WARMUP_S]    # one click, window-relative
#
# Window-relative coordinates, absolute moves (xdotool moves the X pointer; DOSBox-X turns the
# motion into DOS mouse deltas). Every click is press, dwell 0.4 s, release, as on hardware.
# xdotool --window is ignored by DOSBox-X (XSendEvent), so the window is focused once and bare
# commands follow. Stops when the dosbox-x window is gone. Logs to $DRIVE_LOG (./DRIVE.LOG).
set -u
MODE="${1:?usage: lab-drive-xdotool.sh walk|click ...}"; shift
export DISPLAY=":${DOSBOX_DISPLAY_NUM:?set DOSBOX_DISPLAY_NUM}"
DRIVE_LOG="${DRIVE_LOG:-./DRIVE.LOG}"
log() { printf '%s %s\n' "$(date -u +%H:%M:%S)" "$*" | tee -a "$DRIVE_LOG" >&2; }

win=""
for _ in $(seq 1 120); do
    win="$(xdotool search --name 'DOSBox' 2>/dev/null | head -1)"
    [[ -n "$win" ]] && break
    sleep 1
done
[[ -n "$win" ]] || { log "no DOSBox-X window on $DISPLAY"; exit 1; }
alive() { xdotool getwindowname "$win" >/dev/null 2>&1; }
geom() { eval "$(xdotool getwindowgeometry --shell "$win")"; }
click_at() {   # window-relative x y
    geom
    xdotool mousemove $((X + $1)) $((Y + $2)); sleep 0.1
    xdotool mousedown 1; sleep 0.4; xdotool mouseup 1
}

case "$MODE" in
walk)
    WARMUP_S="${1:-25}"; PERIOD_S="${2:-2}"; MAX_CLICKS="${3:-90}"
    log "window $win; warming up ${WARMUP_S}s"
    sleep "$WARMUP_S"
    xdotool windowfocus --sync "$win" 2>/dev/null || true
    geom; log "geometry ${WIDTH}x${HEIGHT} at ${X},${Y}"
    # A fixed sweep of fractions of the window, the same shape drive-walk.sh's relative
    # moves take: left, right, up, down, so each click is somewhere new.
    PTS=("0.30 0.75" "0.70 0.75" "0.70 0.60" "0.25 0.60" "0.25 0.85" "0.45 0.85"
         "0.80 0.70" "0.55 0.55" "0.35 0.80" "0.75 0.85")
    i=0
    while (( i < MAX_CLICKS )) && alive; do
        read -r fx fy <<<"${PTS[$(( i % ${#PTS[@]} ))]}"
        geom
        cx=$(python3 -c "print(int($WIDTH*$fx))"); cy=$(python3 -c "print(int($HEIGHT*$fy))")
        click_at "$cx" "$cy"
        i=$(( i + 1 ))
        log "click $i at $cx,$cy"
        sleep "$PERIOD_S"
    done
    log "done: $i clicks"
    ;;
click)
    CX="${1:?x}"; CY="${2:?y}"; WARMUP_S="${3:-0}"
    sleep "$WARMUP_S"
    xdotool windowfocus --sync "$win" 2>/dev/null || true
    alive && click_at "$CX" "$CY" && log "click at $CX,$CY"
    ;;
*) echo "unknown mode $MODE" >&2; exit 1 ;;
esac
