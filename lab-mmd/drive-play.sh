#!/usr/bin/env bash
# Drive MMD through its own flow on DOSBOX_DISPLAY :261 (window at its default place, 2x scale):
# pick Syd + Bernard, START, let the intro play, then in room 1 hover over named things and
# hold-then-release walk clicks. Coordinates are root-window pixels read off MMDPLAY-P1's frames.
set -u
export DISPLAY=:261
LOG="${1:?log file}"; TICKS="${2:?ticks}"; STAGE_WAIT="${3:-600}"
log() { echo "$(date -u +%H:%M:%S) $*" >> "$LOG"; }
click() { xdotool mousemove "$1" "$2"; sleep 0.4; xdotool mousedown 1; sleep 0.4; xdotool mouseup 1; log "click $1,$2"; }
until xdotool search --name DOSBox >/dev/null 2>&1; do sleep 1; done
sleep 2
ST=""; for _ in $(seq 1 120); do ST=$(for d in $(ls -td /tmp/dos-port-dosbox.* 2>/dev/null); do /usr/bin/grep -qa "AUTO_EXIT_TICK=$TICKS" "$d/RUN.BAT" 2>/dev/null && echo "$d" && break; done); [[ -n "$ST" && -f "$ST/STDOUT.TXT" ]] && /usr/bin/grep -qa 'Now in room 50' "$ST/STDOUT.TXT" && break; sleep 1; done
log "stage $ST"; sleep 6
W=$(xdotool search --name DOSBox | head -1); xdotool windowactivate --sync "$W" 2>/dev/null
click 669 755; sleep 1.5; click 909 755; sleep 1.5; click 1094 664
for _ in $(seq 1 "$STAGE_WAIT"); do /usr/bin/grep -qaE 'Now in room 1([^0-9]|$)' "$ST/STDOUT.TXT" && break; sleep 1; done
log "room 1 reached"; sleep 45   # room 1's own entry cutscene (39.8 s at fixed 40000 in P1)
log "in-play driving starts"
HOV=("560 730" "600 700" "920 700" "995 700" "1075 700" "650 640" "800 620" "540 780")
WALK=("750 780" "620 785" "900 790" "700 775")
i=0
while xdotool search --name DOSBox >/dev/null 2>&1; do
    for h in "${HOV[@]}"; do xdotool mousemove $h; sleep 1; done
    click ${WALK[$((i % 4))]}; i=$((i + 1)); sleep 2
done
