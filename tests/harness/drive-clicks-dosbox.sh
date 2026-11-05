#!/usr/bin/env bash
# drive-clicks-dosbox.sh -- inject real mouse clicks (and optionally keys) into an
# interactive DOSBox-X run, for the click/key response journey (ags patch 0250) and
# the lost-click count (SDL patch 0220). LAB ONLY: DOSBox-X on a private Xvfb.
#
#   DOSBOX_DISPLAY=:231 tests/harness/drive-clicks-dosbox.sh <STAGE_DIR> <LOG> \
#       [--clicks N] [--hold-ms MS] [--gap-ms MS] [--start-after S] [--keys N] [--key KEYSYM]
#
# Waits until <STAGE_DIR>/STDOUT.TXT shows the engine is in a room, focuses the
# DOSBox-X window once (xdotool ignores --window for DOSBox-X), clicks once to take
# the mouse capture (DOSBox-X autolock), then injects N clicks of MS hold each, GAP
# apart, and optionally N key taps. Every injected press is logged with a host
# timestamp to <LOG>: the host count of presses is the third witness beside the
# mouse driver's own count (mouse_presses_hw) and what the engine saw
# (mouse_presses_seen / journey kind=click n).
#
# It stages nothing and decides nothing; RUNMANI.LOG's journey lines are the result.
set -u
STAGE="${1:?stage dir}"; LOG="${2:?log}"; shift 2
CLICKS=20; HOLD_MS=80; GAP_MS=1500; START_AFTER=5; KEYS=0; KEY=z; TIMEOUT_S=300
THROUGH_TITLE=0; WAIT_ROOM=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --clicks) CLICKS="$2"; shift 2 ;;
        --hold-ms) HOLD_MS="$2"; shift 2 ;;
        --gap-ms) GAP_MS="$2"; shift 2 ;;
        --start-after) START_AFTER="$2"; shift 2 ;;
        --keys) KEYS="$2"; shift 2 ;;
        --key) KEY="$2"; shift 2 ;;
        --timeout) TIMEOUT_S="$2"; shift 2 ;;
        --through-title) THROUGH_TITLE=1; shift ;;   # 5 Days: click text + START until room 99
        --wait-room) WAIT_ROOM="$2"; shift 2 ;;      # start the click series once this room is entered
        *) echo "unknown arg $1" >&2; exit 2 ;;
    esac
done
export DISPLAY="${DOSBOX_DISPLAY:?set DOSBOX_DISPLAY}"
log() { printf '%s %s\n' "$(date +%s.%3N)" "$*" >> "$LOG"; }
: > "$LOG"
ms() { sleep "$(awk -v m="$1" 'BEGIN{printf "%.3f", m/1000}')"; }
# press-hold-release in ONE xdotool process, so the hold is the hold (no process start in it)
click_hold() { xdotool mousedown 1 sleep "$(awk -v m="$1" 'BEGIN{printf "%.3f", m/1000}')" mouseup 1; }

# 1. the engine is in a room
for _ in $(seq 1 "$TIMEOUT_S"); do
    [[ -f "$STAGE/STDOUT.TXT" ]] && /usr/bin/grep -q 'Now in room' "$STAGE/STDOUT.TXT" && break
    sleep 1
done
/usr/bin/grep -q 'Now in room' "$STAGE/STDOUT.TXT" 2>/dev/null || { log "ABORT no room in ${TIMEOUT_S}s"; exit 1; }
log "in_room"
sleep "$START_AFTER"

# 2. focus once, centre the pointer, take the capture
WID="$(xdotool search --class dosbox 2>/dev/null | head -1)"
[[ -n "$WID" ]] || WID="$(xdotool search --name DOSBox 2>/dev/null | head -1)"
[[ -n "$WID" ]] || { log "ABORT no DOSBox-X window"; exit 1; }
xdotool windowfocus --sync "$WID" 2>/dev/null || true
eval "$(xdotool getwindowgeometry --shell "$WID")"
xdotool mousemove --window "$WID" $((WIDTH / 2)) $((HEIGHT / 2))
sleep 0.5
xdotool mousedown 1; ms 200; xdotool mouseup 1
log "press capture hold_ms=200"
sleep 2

# 2b. 5 Days natural flow: room 2's intro text waits for a click per line, then the
# title's START plank. The DOSBox-X pointer maps 1:1 into the 640x480 picture, so one
# window-relative point (START's centre, 63,426 in a 640x497 window with DOSBox-X's
# 17 px menu bar) both advances the text and hits START. Stop when room 99 loads.
if [[ $THROUGH_TITLE -eq 1 ]]; then
    xdotool mousemove --window "$WID" 63 426
    for i in $(seq 1 120); do
        /usr/bin/grep -q 'Now in room 99' "$STAGE/STDOUT.TXT" && break
        xdotool mousedown 1; log "press title i=$i hold_ms=200"; ms 200; xdotool mouseup 1
        sleep 2.5
    done
    log "title_done room99=$(/usr/bin/grep -c 'Now in room 99' "$STAGE/STDOUT.TXT")"
fi
if [[ -n "$WAIT_ROOM" ]]; then
    for _ in $(seq 1 "$TIMEOUT_S"); do
        /usr/bin/grep -q "Now in room $WAIT_ROOM\b" "$STAGE/STDOUT.TXT" && break
        sleep 1
    done
    log "in_room_$WAIT_ROOM"
    sleep "$START_AFTER"
    xdotool mousemove --window "$WID" $((WIDTH / 2)) $((HEIGHT / 2))
fi

# 3. the clicks: small moves between them so each is a distinct walk target
for i in $(seq 1 "$CLICKS"); do
    dx=$(( (i % 5) * 12 - 24 )); dy=$(( (i % 3) * 10 - 10 ))
    xdotool mousemove_relative -- "$dx" "$dy"
    ms 100
    log "press click i=$i hold_ms=$HOLD_MS"
    click_hold "$HOLD_MS"
    ms "$GAP_MS"
done
# 4. the keys
for i in $(seq 1 "$KEYS"); do
    xdotool keydown "$KEY"; log "key i=$i key=$KEY"
    ms "$HOLD_MS"
    xdotool keyup "$KEY"
    ms "$GAP_MS"
done
log "done presses_injected=$(/usr/bin/grep -c ' press ' "$LOG") keys_injected=$KEYS"
