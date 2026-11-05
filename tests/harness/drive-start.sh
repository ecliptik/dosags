#!/usr/bin/env bash
# drive-start.sh -- click 5 Days a Stranger's title-screen START on the target machine, so a
# run-hw.sh cell enters play through the game's OWN flow (room 1 -> 2 -> title -> START -> 99 -> 3)
# instead of the --startr debug jump (DUPCHAR4: the jump skips state the flow sets).
#
#   tests/harness/drive-start.sh <TAG> [TITLE_TIMEOUT_S=900]
#
# Run it in the background before run-hw.sh launches; it waits for run-hw.sh to take the input
# lock (owner run-hw-<TAG>), then:
#   1. polls the capture card (640x480 only -- the dongle cannot lock 512x384) until the START
#      plank is on screen in two consecutive polls, LOCATED as the brown blob (R > 80, B < 70,
#      R > B+50, 300-1500 px) in the frame's lower-left (x < 110, y > 330) with the LOAD plank's
#      blob level with it at x 110-230 (SB3O2: a brown intro picture fired the one-blob test) -- the card frames the
#      mode shifted on the target (SB3O: plank near (45, 407)), so no fixed pixel is assumed;
#   2. CALIBRATES the relative-only PS/2 mouse in capture coordinates: home to the corner, then
#      move (+CAL, +CAL) (default 40 counts) three times with a frame after each; the blob two frame-diffs share is the
#      cursor after 200 counts, the others after 100 and 300; those give px-per-count and where the
#      (possibly off-frame) homed corner is;
#   3. homes again, moves to the plank's centroid with that scale, and clicks press-dwell-release
#      (a low-fps poll can miss an instant click);
#   4. confirms the title is gone (the plank pixel no longer brown) and stops. It never clicks
#      again: a stray click in room 3 is a walk command.
# Every step, the calibration numbers and the frames it judged by are logged to $DRIVE_LOG and
# kept under $DRIVE_DIR, for the cell's record. It does not decide whether the run is in play --
# STDOUT's "Now in room 99 / 3" lines do.
set -u
TAG="${1:?usage: drive-start.sh <TAG> [TITLE_TIMEOUT_S]}"
TITLE_TIMEOUT_S="${2:-900}"
HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V="${VCCTRL_BIN:-$HARNESS_DIR/../../../vcctrl/bin/vcctrl}"
OWNER="run-hw-$TAG"
DRIVE_LOG="${DRIVE_LOG:-./DRIVE-START.LOG}"
DRIVE_DIR="${DRIVE_DIR:-./drive-start}"
# calibration step in mouse counts: SB3O2 showed ~2.9 px per count, so 3 x 100 counts ran the
# cursor off the frame; 3 x 40 stays on it from the top-left corner
CAL="${DRIVE_CAL:-40}"
mkdir -p "$DRIVE_DIR"

log() { printf '%s %s\n' "$(date -u +%H:%M:%S)" "$*" | tee -a "$DRIVE_LOG" >&2; }
owner_now() { "$V" lock status 2>/dev/null | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("owner"))
except Exception: print("UNKNOWN")' 2>/dev/null; }
vc() { "$V" "$@" --as "$OWNER"; }
shot() { rm -f "$1"; "$V" shot --out "$1" >/dev/null 2>&1 && [[ -f "$1" ]]; }
plank() { python3 - "$1" <<'EOF'
# The START plank is the leftmost brown blob in the lower-left of the frame. Located, not
# assumed: on the target the capture card frames the 640x480 mode shifted (SB3O: the plank sat at
# about (45, 407), not DOSBox-X's (60, 448)). Prints "brown <cx> <cy> <n>" or "no 0 0 <n>".
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB").resize((640, 480))
def brown(x0, x1):
    xs = ys = n = 0
    for x in range(x0, x1):
        for y in range(330, 480):
            r, g, b = im.getpixel((x, y))
            if r > 80 and b < 70 and r > b + 50:
                xs += x; ys += y; n += 1
    return (xs // n if n else 0), (ys // n if n else 0), n
# START (x < 110) AND the LOAD plank beside it (x 110-230): a brown intro picture is not two planks
sx_, sy_, n = brown(0, 110)
lx_, ly_, ln = brown(110, 230)
if 300 <= n <= 1500 and 300 <= ln <= 1500 and abs(sy_ - ly_) <= 12 and sy_ >= 360:
    print("brown", sx_, sy_, n)
else:
    print("no", 0, 0, n)
EOF
}
cursor_blobs() { python3 - "$@" <<'EOF'
# The cursor positions that differ between two frames: connected blobs of changed pixels, as
# "x y" top-left points (a moved cursor shows twice -- where it was and where it went).
import sys
from PIL import Image, ImageChops
a = Image.open(sys.argv[1]).convert("L").resize((640, 480))
b = Image.open(sys.argv[2]).convert("L").resize((640, 480))
d = ImageChops.difference(a, b).point(lambda v: 255 if v > 28 else 0).load()
seen = set(); out = []
for x in range(640):
    for y in range(480):
        if d[x, y] and (x, y) not in seen:
            stack = [(x, y)]; seen.add((x, y)); pts = []
            while stack:
                p = stack.pop(); pts.append(p)
                for q in ((p[0]+i, p[1]+j) for i in (-2,-1,0,1,2) for j in (-2,-1,0,1,2)):
                    if 0 <= q[0] < 640 and 0 <= q[1] < 480 and d[q] and q not in seen:
                        seen.add(q); stack.append(q)
            if len(pts) >= 12:
                out.append((min(p[0] for p in pts), min(p[1] for p in pts)))
print(" ".join("%d,%d" % o for o in out) or "none")
EOF
}
home() { for _ in 1 2 3 4 5 6; do vc mouse move -120 -120 >/dev/null 2>&1; done; }

log "waiting for the input lock to be taken by $OWNER"
until [[ "$(owner_now)" == "$OWNER" ]]; do sleep 2; done
log "lock is ${OWNER}'s; polling for the title START plank at (60,448)"
t0=$(date +%s); n=0
while :; do
    [[ "$(owner_now)" == "$OWNER" ]] || { log "lock gone before the title -- stopping, no click"; exit 1; }
    (( $(date +%s) - t0 > TITLE_TIMEOUT_S )) && { log "no title within ${TITLE_TIMEOUT_S}s -- stopping, no click"; exit 1; }
    n=$((n + 1))
    if shot "$DRIVE_DIR/poll.jpg"; then
        read -r verdict tx ty npx <<<"$(plank "$DRIVE_DIR/poll.jpg")"
        if [[ "$verdict" == brown ]]; then
            seen=$(( ${seen:-0} + 1 ))
            if (( seen >= 2 )); then
                cp "$DRIVE_DIR/poll.jpg" "$DRIVE_DIR/title.jpg"
                log "title seen on 2 consecutive polls, after ${n}: START plank centroid ($tx,$ty), $npx px"; break
            fi
        else
            seen=0
        fi
    fi
    sleep 3
done

home; sleep 1.5
for k in 1 2 3; do
    vc mouse move "$CAL" "$CAL" >/dev/null 2>&1; sleep 1.5
    shot "$DRIVE_DIR/cal-$k.jpg" || { log "no frame at calibration -- stopping, no click"; exit 1; }
done
b12=$(cursor_blobs "$DRIVE_DIR/cal-1.jpg" "$DRIVE_DIR/cal-2.jpg"); b23=$(cursor_blobs "$DRIVE_DIR/cal-2.jpg" "$DRIVE_DIR/cal-3.jpg")
log "calibration blobs: 1->2 [$b12]  2->3 [$b23]"
# the position after 2*CAL counts is the blob both diffs share; after CAL and 3*CAL, the others
read -r x1 y1 x3 y3 <<<"$(python3 -c "
def pts(s): return [tuple(map(int,t.split(','))) for t in s.split()] if s!='none' else []
A=pts('$b12'); B=pts('$b23')
near=lambda p,q: abs(p[0]-q[0])<=6 and abs(p[1]-q[1])<=6
common=[p for p in A if any(near(p,q) for q in B)]
if len(common)!=1 or len(A)!=2 or len(B)!=2: print('x x x x')
else:
    p2=common[0]; p1=[p for p in A if not near(p,p2)][0]; p3=[q for q in B if not near(q,p2)][0]
    print(p1[0],p1[1],p3[0],p3[1])")"
if [[ "$x1" == x ]]; then
    # Fallback (SB5O, 2026-09-23): a calibration diff can miss one cursor position on a
    # same-brightness background. DRIVE_FALLBACK_COUNTS="dx dy" (from earlier calibrations on
    # this machine; SB3O2/SB3W/SB4O/SB4W all gave 19 274) is used instead, and logged as such.
    if [[ -n "${DRIVE_FALLBACK_COUNTS:-}" ]]; then
        read -r dx dy <<<"$DRIVE_FALLBACK_COUNTS"
        log "calibration could not pick the cursor out -- using DRIVE_FALLBACK_COUNTS $dx,$dy"
        x1=fallback
    else
        log "calibration could not pick the cursor out -- stopping, no click"; exit 1
    fi
fi
# 2*CAL counts between the points: px per count; the homed corner by extrapolating CAL counts back
if [[ "$x1" != fallback ]]; then
read -r sx sy ox oy dx dy <<<"$(python3 -c "
sx=max(($x3-$x1)/(2.0*$CAL),0.05); sy=max(($y3-$y1)/(2.0*$CAL),0.05)
ox=$x1-$CAL*sx; oy=$y1-$CAL*sy
print(sx, sy, ox, oy, round(($tx-ox)/sx), round(($ty-oy)/sy))")"
log "calibration: cursor at ($x1,$y1) after $CAL counts, ($x3,$y3) after $((3*CAL)) => $sx,$sy px/count, corner at ($ox,$oy); START ($tx,$ty) needs $dx,$dy counts"
fi
(( dx > 0 && dy > 0 )) || { log "calibration gave a non-positive move -- stopping, no click"; exit 1; }

home; sleep 1
remaining_x=$dx; remaining_y=$dy
while (( remaining_x > 0 || remaining_y > 0 )); do
    stepx=$(( remaining_x > 100 ? 100 : remaining_x )); stepy=$(( remaining_y > 100 ? 100 : remaining_y ))
    vc mouse move "$stepx" "$stepy" >/dev/null 2>&1
    remaining_x=$(( remaining_x - stepx )); remaining_y=$(( remaining_y - stepy ))
done
sleep 1.5
shot "$DRIVE_DIR/aim.jpg" && log "aim frame saved"
vc mouse down left >/dev/null 2>&1; sleep 0.5; vc mouse up left >/dev/null 2>&1
log "clicked START"
sleep 6
if shot "$DRIVE_DIR/after.jpg"; then
    read -r verdict _ _ npx <<<"$(plank "$DRIVE_DIR/after.jpg")"
    log "after click: plank $verdict ($npx px) -- 'no' means the title is gone"
fi
vc mouse release-all >/dev/null 2>&1 || true
log "done"
