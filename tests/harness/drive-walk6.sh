#!/usr/bin/env bash
# drive-walk6.sh -- DRIVE 6: keep MMD's player WALKING for the whole play window of the P9M1-line fixture (AGSSAVE.007,
# TAS exit 12440). This is a sibling of drive-walk.sh and leaves DRIVE 5 unchanged. Not used by any round yet.
# Design and lab evidence: docs/lab/LAB-MOVE.md on lab-rb (fixture M; lab replica gen.py, same schedule).
#
#   tests/harness/drive-walk6.sh <TAG> [WARMUP_S=40]        (a round's cell script, as DRIVE 5's line:)
#   if [[ "$DRIVE" == 6 ]]; then DRIVE_LOG="$R/DRIVE-WALK.LOG" $H/drive-walk6.sh "$TAG" 40 > /dev/null 2>&1 & DRV=$!; fi
#   tests/harness/drive-walk6.sh --dry-run                  print the schedule and every vcctrl call; sends nothing
#
# WHY NOT DRIVE 5. DRIVE 5's cycle of 10 relative moves wanders. In room 2 every later click lands on the verb bar
# (GUI 1, y >= 143). That changes the verb, so the kid stands at the fence for the last ~2 minutes (lab: walking on 0.3%
# of room-2 ticks).
#
# HOW DRIVE 6 POINTS. The mouse is relative-only, so every press first parks the cursor in a clamped corner, then
# moves to the target from there (no dead reckoning). THE POINTER MODEL (tests/harness/drive6-pointer.py; it fits 229
# of 232 DRIVE 5 runs click by click, and round RH's RHCAL press):
#   - one `vcctrl mouse move dx dy` is ONE PS/2 packet, and the USB4VC board caps a packet at +-127 counts per axis:
#     a "+480 slam" is a 127-count move. So a corner is reached with TWO 127-count packets, never one big move;
#   - CuteMouse moves its cursor linearly, 3.0 px per count in x and 1.5 in y, clamped to the 512x384 screen;
#   - MMD's 320x200 frame sits 1:1 at (96,92) in it: game x = driver x - 96, game y = driver y - 92. The cursor can
#     hide up to 96 / 92 px outside the frame, where AGS reads a clamped position, and the next move starts from there.
# Corners: TL = 2 x (-127,-127) -> driver (0,0); TR = 2 x (+127,-127) -> (511,0); BR = 2 x (+127,+127) -> (511,383).
# Two packets reach a corner from anywhere a press leaves the cursor (driver y <= ~240); before the FIRST press the
# cursor's place is unknown (up to the screen's bottom, 383 = 2.01 packets), so the run first parks it with three
# (-127,-127) packets ("park" in the log and the dry run).
# Every press: corner, corner, (x move, +127), (0, +DY):  y = 1.5 x (127 + DY) - 92 = 98.5 + 1.5 DY (121 at DY 15;
# the target is y 120, 23 px above the verb bar at 143).
#   L    : TL, (+DXL, +127), (0, +DY) -> x = 3 DXL - 96          (60 at DXL 52)   room 1 / room 2 of fixture M
#   R    : TR, (0, +127), (0, +DY)    -> x = 319 (the clamp)
#   EXIT : TL, (0, +127), (0, +DY)    -> x = 0: room 1's exit walk
# DRIVE6_MODE=ms (MS3, the campaign fixture): room 1 and EXIT as above; room 2 off the top-right corner:
#   A    : TR, (-DXA, +127), (0, +DY) -> x = 415 - 3 DXA          (190 at DXA 75; room x 830)
#   B    : TR, (-DXB, +127), (0, +DY) -> x = 415 - 3 DXB          (289 at DXB 42; room x 929)
#   room 2 alternates A, B every ~1.2 s (114 presses in all). Lab-tested landing bands (LAB-MOVE addendum 3, +-12 px):
#   TIMING (sdlports 2026-11-11): a vcctrl call costs 0.15-0.20 s on the rig, so the split full press (6 calls + the
#   dwell, ~1.28 s) cannot keep MS3's 1.14-1.26 s gaps (latency stub: ~10 s late by the last press). The DEFAULT for ms
#   and cal is the one-call press (DRIVE6_PRESS=one, vcctrl `mouse press`): ~0.65 s a press, late <= 0.04 s.
#   DRIVE6_MS_PATH=reclamp: room 2's presses re-clamp x only -- (+127,0) to the right edge, then (-DXA|-DXB,0), the
#   same landing as the corner path (x = 511 - 3 DXA), y left where the last full press put it -- 2 moves; the first
#   room-2 press and every 10th are full presses (they re-anchor y). Latency stub: 0.96 s a press, late <= 0.16 s.
#   A 177..201, B 276..300, L 48..72, y 116..140 (the verb bar starts at y 143).
# The defaults are the model's values; the calibration cell (DRIVE6_MODE=cal) measures them on the rig.
# DRIVE6_MODE=calq: the SHORT re-check for a power-on after a full calibration PASSed (round RI's RICAL): 13 presses,
#   2 s apart, ~34 s -- room 1: CAL-C and CAL-DXL=DXL alternate 3 times; CAL-EXIT; room 2 from EXIT + 10 s: CAL-DXA=DXA and
#   CAL-DXB=DXB alternate 3 times; every press at y from DY. drive6-gate.sh --recheck checks every point at the
#   reference's values against MS3's landing bands (the same meaning as a full-cal PASS); any miss -> the full cal.
# DRIVE6_MODE=cal: the calibration cell, on the P9M1 play line (TAS exit 12440). 61 presses, ~152 s:
#   the MEASUREMENT PRELUDE, room 1, 11 presses 4 s apart -- the transfer function itself, which the lab cannot
#   reproduce (DOSBox-X has neither CuteMouse's PS/2 path nor the USB4VC board):
#     CAL-MX=d           TL, (+127,+127), (-d,+DY)  -> x = 285 - 3 d: one packet of d = 8 20 30 45 60 88 counts
#     CAL-MXS=60 / MXF=60  TL, (+127,+127), 4 x (-15,0) SLOW (0.4 s apart, split calls) / FAST (back to back: in one
#                        call at the press pace), (0,+DY): = CAL-MX=60? (FAST also shows a board merge at that pace)
#     CAL-MCLIP=200      TL, (+200,+127), (-70,+DY) -> x 75 if the board clips a packet at 127, 205 if it carries
#   Room 1 has two live regions (x 238..247 and 275..290 at y 114..134: an object under the cursor swallows the click);
#   every prelude point is clear of them.
#     CAL-MY=16 / MYS=16   TL, (+75,+127), then (0,+16) as one packet / as 4 x (0,+4) slow: equal y?
#   then, GAP s apart (default 2.0):
#   room 1, 22 presses: CAL-C and CAL-DXL=v alternate (x 319 / ~60, so consecutive presses are far apart)
#     CAL-C              TR, (0,+127), (0,+DY)      -> x must log exactly 319 (the TR corner); y at DY
#     CAL-DXL=v          TL, (+v,+127), (0,+DY)     -> x; v = DXL + (-8 -4 0 +4 +8) once, then (-4 0 +4) twice more
#   CAL-EXIT             TL, (0,+127), (0,+DY)      -> x must log 0 (the TL corner); walks the kid into room 2
#   room 2 from EXIT + 10 s, 22 presses: CAL-DXA=v/DY=w and CAL-DXB=v alternate (room x = 640 + screen x)
#     CAL-DXA=v/DY=w     TR, (-v,+127), (0,+w)      -> x for DXA: v = DXA + (-9 -6 -3 0 +3 +6) once, (-3 0 +3) / (-3 +3);
#                                                      y for DY: w = DY - 7 .. DY + 6, ascending (the largest last)
#     CAL-DXB=v          TR, (-v,+127), (0,+DY)     -> x; v = DXB + (-3 0 +3 +6 +9) once, then (-3 0 +3) twice more
#   The DY sweep rides on A, not B: B's room x reaches 938, and at y <= 111 room x 932..955 is hotspot 2 (a click
#   there walks to the hotspot's own point, 942,138: the lab replica showed it).
#   then 5 presses: CAL-BR, B, CAL-BR, B, CAL-BR
#     CAL-BR             BR, (-DXA,-120)            -> y reads the screen's bottom bound (383 expected); informational
# One run converges: every quantity is swept and fitted with a line (the model is linear), so the reader
# (drive6-cal.py) picks the value that hits the target even when it lies between or away from the default, as long
# as the rig's gains are within: x -7%..+8% (DXA, the narrowest; DXL -13..+18%, DXB -18..+8%) and y -4.6%..+4.6%.
# The measured gains are good to < 1% (229 runs, to 1 px over ~200-380 px), so that is a > 5x margin. Beyond it the
# gate re-centres (one more cal cell); a slope > 25% off the model stops. Bounds at the model's gains: room-1 presses
# at x >= 36 and y 110..130 (the verb bar starts at 143; +5% y gain still clears it); room-2 presses at room x
# 812..938 (camera clamped at 640, short of the exit at ~949).
# Witness: tests/harness/drive6-cal.py STDOUT.TXT DRIVE-WALK.LOG; decision: tests/harness/drive6-gate.sh.
#
# SCHEDULE. Absolute wall times from the first press, from one fixed table (seed "DRIVE6", the same every run, +-5%
# jitter so drive-align has one alignment):
#   room 1: R, L, R, ... every ~2.5 s (15 presses); EXIT at ~38 s;
#   room 2: from 46.5 s, L, R, L, ... every ~1.75 s, to 163 s (83 presses in all); mode ms: A, B, ... every ~1.2 s.
# A press is sent at its scheduled time. Its 3-4 pointer moves (one vcctrl call each, ~90-200 ms on the rig) start
# 0.15 s per move + 0.1 s earlier (0.7 s for 4). Every press is
# down, dwell DRIVE6_DWELL (0.2 s), up (low-fps games can miss an instant click; see drive-walk.sh). Each click line logs down_at= and
# the return codes, as drive-walk.sh's do, plus the planned time and its lateness.
set -u
DRY=0; [[ "${1:-}" == "--dry-run" ]] && { DRY=1; shift; set -- DRYRUN "$@"; }
TAG="${1:?usage: drive-walk6.sh <TAG> [WARMUP_S] | --dry-run}"
WARMUP_S="${2:-40}"
DY="${DRIVE6_DY:-15}"         # the 2nd y packet after (x, +127) from a top corner: y = 98.5 + 1.5 DY -> 121 (band 116..140)
DXL="${DRIVE6_DXL:-52}"       # from TL: x = 3 DXL - 96 -> 60 (band 48..72)
DXA="${DRIVE6_DXA:-75}"       # mode ms, from TR: x = 415 - 3 DXA -> 190 (band 177..201)
DXB="${DRIVE6_DXB:-42}"       # mode ms, from TR: x = 415 - 3 DXB -> 289 (band 276..300)
P=127                         # the board's per-packet cap: a corner is two packets of 127, never one bigger move
MODE="${DRIVE6_MODE:-m}"      # m: fixture M (room 2 pans the camera); ms: fixture MS3 (the campaign fixture); cal;
                              # calq: the short re-check (one point per quantity + the corners, 13 presses)
DWELL="${DRIVE6_DWELL:-0.2}"  # press hold: MMD polls every 25 ms tick, so 0.2 s is 8 ticks (was 0.4 s)
# DRIVE6_PRESS: one = a press is ONE `vcctrl --as OWNER mouse press --moves "dx,dy ..." --dwell D --pace P` call
# (vcctrl 9bad5fd, live 2026-11-11: the moves, down, dwell and up in one daemon call, ~0.45 s); split = one vcctrl
# call per packet, then down / dwell / up (~1.3 s a full press: too slow for MS3's 1.2 s gaps). Default: one for ms and
# cal, split for m. A press with pauses between its packets (the cal prelude's slow probes) is always sent split.
case $MODE in ms|cal|calq) PRESS="${DRIVE6_PRESS:-one}";; *) PRESS="${DRIVE6_PRESS:-split}";; esac
# the pace between a one-call press's events: the USB4VC board sums every event queued before it sends a packet and
# caps the sum at 127, so two 127-count corner moves 12 ms apart (vcctrl's default pace) could merge into ONE capped
# packet. 0.05 s is past the PS/2 report interval (10-25 ms); the cal prelude's FAST probe (4 packets in one call)
# would show a merge (check C10)
PACE="${DRIVE6_PACE:-0.05}"
MSPATH="${DRIVE6_MS_PATH:-full}"  # mode ms, room 2: full = every press parks in the corner (4 moves); reclamp = x only:
                              # (+127,0) clamps x at the right edge, (-DXA|-DXB,0) lands it (2 moves), y stays where the
                              # last full press put it; a full press every 10th room-2 press and the first one
case $MSPATH in full|reclamp) ;; *) echo "DRIVE6_MS_PATH must be full or reclamp" >&2; exit 2;; esac
case $PRESS in one|split) ;; *) echo "DRIVE6_PRESS must be one or split" >&2; exit 2;; esac
case $MODE in m|ms|cal|calq) ;; *) echo "DRIVE6_MODE must be m, ms, cal or calq" >&2; exit 2;; esac
CAL_GAP="${DRIVE6_CAL_GAP:-2.0}"
# values from the withdrawn pointer model (DY 88 / 170, DXB 21, ...) would put presses on the verb bar or the exit
inr() { [[ "$2" =~ ^[0-9]+$ ]] && (( $2 >= $3 && $2 <= $4 )) || { echo "drive-walk6.sh: $1=$2 outside $3..$4 (the pointer model of drive6-pointer.py; an old-model value?)" >&2; exit 2; }; }
inr DRIVE6_DY "$DY" 15 40;   # >= 15: the play path sends packets of 15..127 counts only (C10's range; under 12 a packet
                              # loses counts, round RI, drive6-pointer.py small_loss)
 inr DRIVE6_DXL "$DXL" 32 110; inr DRIVE6_DXA "$DXA" 40 115; inr DRIVE6_DXB "$DXB" 30 80
HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V="${VCCTRL_BIN:-$HARNESS_DIR/../../../vcctrl/bin/vcctrl}"
OWNER="run-hw-$TAG"
DRIVE_LOG="${DRIVE_LOG:-./DRIVE.LOG}"

# Time and logging without spawning a process (the live loop must stay inside MS3's ~1.2 s gaps; sdlports 2026-11-11):
# $EPOCHREALTIME in integer microseconds, bash's printf %(...)T for the clock, a builtin sleep (read -t on a pipe that
# never delivers), and log lines written with printf, not date | tee.
export TZ=UTC0
now_us() { local e=$EPOCHREALTIME; NOW=$(( 10#${e%.*} * 1000000 + 10#${e#*.} )); }
s_to_us() { local a=${1%.*} f=${1#*.}; [[ $1 == *.* ]] || f=0; f=${f}000000; US=$(( 10#$a * 1000000 + 10#${f:0:6} )); }
SFD=; bsleep_us() { (( $1 > 0 )) || return 0; [[ -n $SFD ]] || exec {SFD}<> <(:); local s; printf -v s '%d.%06d' $(( $1 / 1000000 )) $(( $1 % 1000000 )); read -r -t "$s" -u "$SFD" _ || true; }
clock() { now_us; printf -v CLK '%(%H:%M:%S)T.%03d' $(( NOW / 1000000 )) $(( NOW / 1000 % 1000 )); }
log() { clock; printf '%s %s\n' "$CLK" "$*" >> "$DRIVE_LOG"; printf '%s %s\n' "$CLK" "$*" >&2; }
# vcctrl reads stdin (round RH, 2026-11-11: inside the schedule loop, which is fed by <<<"$SCHED", the first press's
# "mouse down" swallowed the rest of the schedule, so the cal cell sent 1 press of 40). Every vcctrl call reads /dev/null.
vc() { if (( DRY )); then echo "  vcctrl $* --as $OWNER"; return 0; fi; "$V" "$@" --as "$OWNER" </dev/null; }
# Never leave the 486's left button held (sdlports review 2026-11-11): the cell script kills this driver by PID, and
# in ms mode a press holds the button 0.2 s of every ~1.2 s, so a kill can land between "mouse down" and "mouse up".
# On any exit or signal, release every mouse button. Not in --dry-run (it sends nothing).
if (( ! DRY )); then trap '"$V" mouse release-all --as "$OWNER" </dev/null >/dev/null 2>&1 || true' EXIT; trap 'exit 143' TERM; trap 'exit 130' INT; fi
owner_now() { "$V" lock status </dev/null 2>/dev/null | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("owner"))
except Exception: print("UNKNOWN")' 2>/dev/null; }

# The schedule: "index wall_s kind" lines, the same algorithm and seed as LAB-MOVE's gen.py schedule().
SCHED="$(python3 - "$MODE" "$CAL_GAP" "$DY" "$DXL" "$DXA" "$DXB" <<'PY'
import random, sys
if sys.argv[1] == 'calq':
    # the short re-check (round RI's proposal): the values in hand, one point per quantity, 3 times each, + the corners
    gap = float(sys.argv[2])
    dy, dxl, dxa, dxb = (int(v) for v in sys.argv[3:7])
    r1 = ['CAL-C', 'CAL-DXL=%d' % dxl] * 3
    r2 = ['CAL-DXA=%d' % dxa, 'CAL-DXB=%d' % dxb] * 3
    out = [(i * gap, k) for i, k in enumerate(r1)]
    t_exit = len(r1) * gap
    out.append((t_exit, 'CAL-EXIT'))
    out += [(t_exit + 10.0 + i * gap, k) for i, k in enumerate(r2)]
    for i, (t, k) in enumerate(out):
        print('%d %.3f %s' % (i + 1, t, k))
    sys.exit(0)
if sys.argv[1] == 'cal':
    gap = float(sys.argv[2])
    dy, dxl, dxa, dxb = (int(v) for v in sys.argv[3:7])
    ol = (-8, -4, 0, 4, 8, -4, 0, 4, -4, 0, 4)          # wide once, then the centre +-1 step twice more
    oa = (-9, -6, -3, 0, 3, 6, -3, 0, 3, -3, 3)          # A never above DXA + 6: room x >= 812, camera clamped
    ob = (-3, 0, 3, 6, 9, -3, 0, 3, -3, 0, 3)           # B never below DXB - 3: room x <= 938, short of the exit
    oy = (-7, -6, -5, -4, -3, -2, -1, 0, 1, 3, 6)       # ascending: the press nearest the verb bar comes last
    # the measurement prelude (room 1, 3 s apart): the transfer function itself -- one packet of each size, the same
    # 60 / 16 counts sent slow (4 packets 0.4 s apart) and fast (4 back to back), and one 200-count packet (clip or carry)
    # x = 285 - 3 d: 21 261 105 225 105 (75 | 205) 195 105 (129) 150 (129) -- clear of room 1's two live regions
    # (x 238..247 and 275..290 at y 114..134: the lab hover map, HOVER1 / HOVER2)
    pre = ['CAL-MX=88', 'CAL-MX=8', 'CAL-MX=60', 'CAL-MX=20', 'CAL-MXS=60', 'CAL-MCLIP=200', 'CAL-MX=30', 'CAL-MXF=60',
           'CAL-MY=16', 'CAL-MX=45', 'CAL-MYS=16']
    r1 = []
    for o in ol:                                        # room 1: x 319 / ~60 alternate, far apart
        r1 += ['CAL-C', 'CAL-DXL=%d' % (dxl + o)]
    r2 = []
    for a, b, w in zip(oa, ob, oy):                     # room 2: A (~830) and B (~929) alternate; the DY sweep rides
        r2 += ['CAL-DXA=%d/DY=%d' % (dxa + a, dy + w), 'CAL-DXB=%d' % (dxb + b)]   # on A (room x 812..857: no hotspot)
    r2 += ['CAL-BR', 'CAL-DXB=%d' % dxb, 'CAL-BR', 'CAL-DXB=%d' % dxb, 'CAL-BR']
    out = [(i * 4.0, k) for i, k in enumerate(pre)]      # 4 s slots: the slow probes carry 1.6 s of pauses
    t1 = len(pre) * 4.0
    out += [(t1 + i * gap, k) for i, k in enumerate(r1)]
    t_exit = t1 + len(r1) * gap
    out.append((t_exit, 'CAL-EXIT'))
    out += [(t_exit + 10.0 + i * gap, k) for i, k in enumerate(r2)]
    for i, (t, k) in enumerate(out):
        print('%d %.3f %s' % (i + 1, t, k))
    sys.exit(0)
ms = sys.argv[1] == 'ms'
gap2, kinds = (1.2, ('A', 'B')) if ms else (1.75, ('L', 'R'))
rnd = random.Random('DRIVE6'); out = []; t = 0.0
for i in range(15):
    out.append((t, 'R' if i % 2 == 0 else 'L')); t += 2.5 * rnd.uniform(0.95, 1.05)
out.append((t, 'EXIT')); t = max(t + 8.5, 46.0); k = 0
while t <= 163.0:
    out.append((t, kinds[k % 2])); t += gap2 * rnd.uniform(0.95, 1.05); k += 1
for i, (t, k) in enumerate(out):
    print('%d %.3f %s' % (i + 1, t, k))
PY
)"

# moves KIND: the pointer moves before KIND's press, one "dx dy" per line = one packet each (corner first)
TL="-$P -$P"; TR="$P -$P"; BR="$P $P"
moves() {
    local k=${1%%=*} v=${1#*=} w=$DY
    [[ "$v" == */DY=* ]] && { w=${v#*/DY=}; v=${v%%/*}; }
    case $k in
        L|CAL-DXL) [[ $k == L ]] && v=$DXL; printf '%s\n%s\n%s %s\n0 %s\n' "$TL" "$TL" "$v" "$P" "$w";;
        R|CAL-C) printf '%s\n%s\n0 %s\n0 %s\n' "$TR" "$TR" "$P" "$w";;
        EXIT|CAL-EXIT) printf '%s\n%s\n0 %s\n0 %s\n' "$TL" "$TL" "$P" "$w";;
        A|CAL-DXA) [[ $k == A ]] && v=$DXA; printf '%s\n%s\n-%s %s\n0 %s\n' "$TR" "$TR" "$v" "$P" "$w";;
        B|CAL-DXB) [[ $k == B ]] && v=$DXB; printf '%s\n%s\n-%s %s\n0 %s\n' "$TR" "$TR" "$v" "$P" "$w";;
        CAL-BR) printf '%s\n%s\n-%s -120\n' "$BR" "$BR" "$DXA";;
        # the measurement prelude: x from TL then one +127 packet (x 285), so a test packet -d lands at 285 - 3 d
        CAL-MX) printf '%s\n%s\n%s %s\n-%s %s\n' "$TL" "$TL" "$P" "$P" "$v" "$w";;
        CAL-MXS|CAL-MXF) printf '%s\n%s\n%s %s\n' "$TL" "$TL" "$P" "$P"
            for _ in 1 2 3 4; do printf -- '-%s 0\n' $(( v / 4 )); [[ $k == CAL-MXS ]] && printf 'sleep 0.4\n'; done
            printf '0 %s\n' "$w";;
        CAL-MCLIP) printf '%s\n%s\n%s %s\n-70 %s\n' "$TL" "$TL" "$v" "$P" "$w";;
        CAL-MY|CAL-MYS) printf '%s\n%s\n75 %s\n' "$TL" "$TL" "$P"
            if [[ $k == CAL-MY ]]; then printf '0 %s\n' "$v"; else
                for _ in 1 2 3 4; do printf '0 %s\nsleep 0.4\n' $(( v / 4 )); done; fi;;
        *) echo "drive-walk6.sh: unknown press kind $1" >&2; return 1;;
    esac
}

# Every press's moves, built once (dry run and live alike): the live loop spawns nothing but vcctrl itself.
NP=0; PI=(); PT=(); PK=(); PMV=(); PLEAD=(); POM=(); r2=0
while read -r i t k; do
    if [[ $MODE == ms && $MSPATH == reclamp && ( $k == A || $k == B ) ]] && (( r2 % 10 != 0 )); then
        [[ $k == A ]] && v=$DXA || v=$DXB
        mv="$P 0"$'\n'"-$v 0"            # x re-clamped at the right edge, then landed; y unchanged
    else
        mv="$(moves "$k")"
    fi
    [[ $k == A || $k == B ]] && r2=$(( r2 + 1 ))
    nm=0; ns=0
    while read -r a b; do if [[ $a == sleep ]]; then s_to_us "$b"; ns=$(( ns + US )); else nm=$(( nm + 1 )); fi; done <<<"$mv"
    s_to_us "$t"
    PI[NP]=$i; PT[NP]=$US; PK[NP]=$k; PMV[NP]=$mv
    POM[NP]=; [[ $PRESS == one ]] && (( ns == 0 )) && { POM[NP]="$(tr ' \n' ', ' <<<"$mv")"; POM[NP]=${POM[NP]% }; }
    if [[ -n ${POM[NP]} ]]; then
        s_to_us "$PACE"; PLEAD[NP]=$(( US * nm + 100000 ))   # one call: the down comes ~0.1 s + the moves' pacing in
    else
        PLEAD[NP]=$(( 200000 * nm + ns + 100000 ))   # split: 0.2 s per move (RHP1's median call) + any pauses + 0.1 s
    fi
    NP=$(( NP + 1 ))
done <<<"$SCHED"

if (( DRY )); then
    if [[ $MODE == calq ]]; then
        echo "DRIVE 6 dry run (mode calq): DY=$DY DXL=$DXL DXA=$DXA DXB=$DXB P=$P GAP=$CAL_GAP, $(wc -l <<<"$SCHED") presses"
    elif [[ $MODE == cal ]]; then
        echo "DRIVE 6 dry run (mode cal): centre DY=$DY DXL=$DXL DXA=$DXA DXB=$DXB P=$P GAP=$CAL_GAP, $(wc -l <<<"$SCHED") presses"
    elif [[ $MODE == ms ]]; then
        echo "DRIVE 6 dry run (mode ms): DY=$DY DXL=$DXL DXA=$DXA DXB=$DXB P=$P, $(wc -l <<<"$SCHED") presses"
    else
        echo "DRIVE 6 dry run: DY=$DY DXL=$DXL P=$P, $(wc -l <<<"$SCHED") presses"
    fi
    echo "park"
    for _ in 1 2 3; do vc mouse move "-$P" "-$P"; done
    while read -r i t k; do
        echo "press $i at +${t}s $k"
        if [[ -n ${POM[i-1]} ]]; then
            while read -r mx my; do echo "  (move $mx $my)"; done <<<"${PMV[i-1]}"
            echo "  vcctrl --as $OWNER mouse press --moves \"${POM[i-1]}\" --button left --dwell $DWELL --pace $PACE"
            continue
        fi
        while read -r mx my; do
            if [[ $mx == sleep ]]; then echo "  (sleep $my s)"; else vc mouse move "$mx" "$my"; fi
        done <<<"${PMV[i-1]}"
        vc mouse down left; echo "  ($DWELL s)"; vc mouse up left
    done <<<"$SCHED"
    exit 0
fi

if [[ $MODE == calq ]]; then
    log "DRIVE 6 mode calq: DY=$DY DXL=$DXL DXA=$DXA DXB=$DXB P=$P GAP=$CAL_GAP press=$PRESS dwell=$DWELL pace=$PACE, $(wc -l <<<"$SCHED") presses (the short re-check; room 1 then room 2; TAS exit 12440)"
elif [[ $MODE == cal ]]; then
    log "DRIVE 6 mode cal: centre DY=$DY DXL=$DXL DXA=$DXA DXB=$DXB P=$P GAP=$CAL_GAP press=$PRESS dwell=$DWELL pace=$PACE, $(wc -l <<<"$SCHED") presses (room 1 then room 2; TAS exit 12440)"
elif [[ $MODE == ms ]]; then
    log "DRIVE 6 mode ms: DY=$DY DXL=$DXL DXA=$DXA DXB=$DXB P=$P press=$PRESS path=$MSPATH dwell=$DWELL pace=$PACE, $(wc -l <<<"$SCHED") presses ($( [[ -n "${DRIVE6_DY:-}" && -n "${DRIVE6_DXL:-}" && -n "${DRIVE6_DXA:-}" && -n "${DRIVE6_DXB:-}" ]] && echo calibrated || echo UNCALIBRATED defaults))"
else
    log "DRIVE 6: DY=$DY DXL=$DXL P=$P, $(wc -l <<<"$SCHED") presses ($( [[ -n "${DRIVE6_DY:-}" && -n "${DRIVE6_DXL:-}" ]] && echo calibrated || echo UNCALIBRATED defaults))"
fi
log "waiting for the input lock to be taken by $OWNER"
until [[ "$(owner_now)" == "$OWNER" ]]; do sleep 2; done
log "lock is ${OWNER}'s; warming up ${WARMUP_S}s (RUN.BAT is typed, AGS is starting)"
sleep "$WARMUP_S"
# park: the cursor's place is unknown before the first press; three (-127,-127) packets put it at the driver's (0,0)
rcp=0; for _ in 1 2 3; do vc mouse move "-$P" "-$P" >/dev/null 2>&1 || rcp=1; done
log "parked at the top-left (3 x -$P,-$P) rc=$rcp"
s_to_us "$DWELL"; DWELL_US=$US

# send_press N: press N's moves (one vcctrl call per packet), a wait to its planned time, then down / dwell / up.
# Sets RC_H RC_X RC_Y RC_DOWN RC_UP, LATE_US and TDOWN. A one-call `mouse press` (DRIVE6_PRESS=onecall) replaces this.
send_press() {
    local n=$1 a b rcs=() line
    while read -r a b; do
        if [[ $a == sleep ]]; then s_to_us "$b"; bsleep_us "$US"; continue; fi
        "$V" mouse move "$a" "$b" --as "$OWNER" </dev/null >/dev/null 2>&1; rcs+=($?)
    done <<<"${PMV[n]}"
    if (( ${#rcs[@]} >= 3 )); then RC_H=$(( ${rcs[0]} | ${rcs[1]} )); RC_X=${rcs[2]}; else RC_H=${rcs[0]}; RC_X=${rcs[1]}; fi
    RC_Y=${rcs[${#rcs[@]}-1]}
    now_us; bsleep_us $(( T0 + PT[n] - NOW ))
    now_us; LATE_US=$(( NOW - T0 - PT[n] )); clock; TDOWN=$CLK
    "$V" mouse down left --as "$OWNER" </dev/null >/dev/null 2>&1; RC_DOWN=$?
    bsleep_us "$DWELL_US"
    "$V" mouse up left --as "$OWNER" </dev/null >/dev/null 2>&1; RC_UP=$?
}

# send_press_one N: the whole press in one `vcctrl mouse press` call. Its JSON gives the daemon's elapsed_ms and each
# step's t_ms; the down's wall time is estimated as call start + half the call's overhead (wall - elapsed) + the down
# step's t_ms. Sets RC_PRESS (the call's exit), PRESS_OK (every step ok), EL_MS, WALL_MS, LATE_US, TDOWN, FAILED_AT,
# DWELL_S (the reply's dwell_s: the dwell actually used, after the profile's click_hold_s floor; MOUSE.md 10b) and
# PRESS_REPLY (the call's whole output: the JSON, and on a failure vcctrl's one-line error, as they arrived).
send_press_one() {
    local n=$1 out s e down_ms=0
    now_us; bsleep_us $(( T0 + PT[n] - PLEAD[n] - NOW ))
    now_us; s=$NOW
    out="$("$V" --as "$OWNER" mouse press --moves "${POM[n]}" --button left --dwell "$DWELL" --pace "$PACE" </dev/null 2>&1)"
    RC_PRESS=$?; PRESS_REPLY=$out
    now_us; e=$NOW; WALL_MS=$(( (e - s) / 1000 ))
    EL_MS=0; [[ $out =~ \"elapsed_ms\":\ *([0-9]+) ]] && EL_MS=${BASH_REMATCH[1]}
    # the dwell the daemon actually used: the requested one, raised to the profile's click_hold_s floor if it has one
    DWELL_S=-; [[ $out =~ \"dwell_s\":\ *([0-9.]+) ]] && DWELL_S=${BASH_REMATCH[1]}
    [[ $out =~ \"step\":\ *\"down\"[^}]*\"t_ms\":\ *([0-9]+) ]] && down_ms=${BASH_REMATCH[1]}
    FAILED_AT=-; [[ $out =~ \"failed_at\":\ *\"([a-z]+)\" ]] && FAILED_AT=${BASH_REMATCH[1]}
    PRESS_OK=1; [[ $out =~ \"ok\":\ *false ]] && PRESS_OK=0
    (( RC_PRESS == 0 && EL_MS > 0 )) || PRESS_OK=0
    local over=0; (( PRESS_OK )) && over=$(( (e - s - EL_MS * 1000) / 2 ))
    LATE_US=$(( s + over + down_ms * 1000 - T0 - PT[n] ))
    NOW=$(( s + over + down_ms * 1000 )); printf -v TDOWN '%(%H:%M:%S)T.%03d' $(( NOW / 1000000 )) $(( NOW / 1000 % 1000 ))
}

# vcctrl's full reply to the FIRST one-call press, and to any failed one, is kept beside DRIVE_LOG in the cell's
# results dir: FIRST-PRESS.json, FAILED-PRESS-<click>.json (the reply as printed: the JSON on stdout and, on a failure,
# vcctrl's one-line error on stderr, in the order they arrived).
# Builtin printf into a file: no process, and nothing on the other presses.
[[ $DRIVE_LOG == */* ]] && LOGDIR=${DRIVE_LOG%/*} || LOGDIR=.
FIRST_KEPT=0
now_us; T0=$(( NOW + PLEAD[0] + 500000 ))   # the first press, after its pointer moves (+0.5 s: the first calls are slower)
n=0; bad=0
while (( n < NP )); do
    # the lock is checked every 10 presses (offset from reclamp's full presses) and after any failed call, not every
    # press (one vcctrl + python3: ~0.2 s)
    if (( n % 10 == 5 || bad )); then
        [[ "$(owner_now)" == "$OWNER" ]] || { log "lock no longer ${OWNER}'s -- run ended, stopping after $n presses"; break; }
    fi
    if [[ -n ${POM[n]} ]]; then
        send_press_one "$n"
        bad=$(( RC_PRESS != 0 || PRESS_OK == 0 ))
        rcf="press=one rc_press=$RC_PRESS ok=$PRESS_OK failed_at=$FAILED_AT dwell_s=$DWELL_S elapsed_ms=$EL_MS wall_ms=$WALL_MS"
        if (( ! FIRST_KEPT )); then
            printf '%s\n' "$PRESS_REPLY" > "$LOGDIR/FIRST-PRESS.json"; FIRST_KEPT=1; rcf+=" reply=FIRST-PRESS.json"
        fi
        if (( bad )); then
            printf '%s\n' "$PRESS_REPLY" > "$LOGDIR/FAILED-PRESS-${PI[n]}.json"; rcf+=" reply=FAILED-PRESS-${PI[n]}.json"
        fi
    else
        now_us; bsleep_us $(( T0 + PT[n] - PLEAD[n] - NOW ))
        send_press "$n"
        bad=$(( RC_H | RC_X | RC_Y | RC_DOWN | RC_UP ))
        rcf="rc_home=$RC_H rc_x=$RC_X rc_y=$RC_Y rc_down=$RC_DOWN rc_up=$RC_UP dwell_s=$DWELL"
    fi
    if (( LATE_US < 0 )); then printf -v late -- '-%d.%02d' $(( -LATE_US / 1000000 )) $(( -LATE_US / 10000 % 100 ))
    else printf -v late '%d.%02d' $(( LATE_US / 1000000 )) $(( LATE_US / 10000 % 100 )); fi
    printf -v pl '%d.%03d' $(( PT[n] / 1000000 )) $(( PT[n] / 1000 % 1000 ))
    log "click ${PI[n]}  ${PK[n]} planned=+${pl}s late=${late}s down_at=$TDOWN $rcf"
    n=$((n + 1))
done
vc mouse release-all >/dev/null 2>&1 || true
log "done: $n presses"
