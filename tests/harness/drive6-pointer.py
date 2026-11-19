#!/usr/bin/env python3
"""drive6-pointer.py -- the Gateway 486's pointer, as measured: what a vcctrl `mouse move` does to MMD's cursor.

    drive6-pointer.py replay RESULTS_DIR...      the evidence: replay every DRIVE 5 run (drive-walk.sh's homed move list)
                                                 and RHCAL against its game log, click by click
    drive6-pointer.py plan DRYRUN [--gx G --gy G --start X Y]
                                                 the game point each press of a drive-walk6.sh --dry-run listing lands on

THE MODEL (fits 229 of 232 DRIVE 5 runs, every walk target to <= 1 px, and round RH's RHCAL corner press):
1. One `vcctrl mouse move dx dy` is ONE PS/2 packet: the board's counters show pkt_built == ev_in (RHCAL 4 / 4, RHP1
   91 / 91), and vcctrl does not split a move on this profile (no mouse_max_step).
2. The USB4VC IBM PC board caps each packet at +-127 counts per axis (firmware get_consolidated_mouse_event ->
   cap_to_127). A +-480 "slam" is a +-127 move.
3. CuteMouse moves its cursor LINEARLY, 3.0 driver px per count in x and 1.5 in y (the 2:1 vertical mickey ratio).
   No acceleration: 100 counts -> 300 px, 127 -> 381 px, 90 -> 135, 40 -> 60.
4. The driver clamps its cursor to 0..511 x 0..383, the 512x384 screen. Right / left / top bounds are measured
   (DRIVE 5 click 4 starts at 511, click 7 at 0, click 5 from y 85 after the top); the bottom (383) is the screen's
   height, not yet measured (the calibration cell's CAL-BR presses read it).
5. MMD draws its 320x200 frame 1:1 at (96,92) in that screen (STDOUT "Mouse cursor graphic area: (96,92)-(415,291)").
   AGS clamps the position it READS to the frame but never moves the driver's cursor back: the cursor can sit up to
   96 px left / right and 92 px above / below the frame, invisible, and the next move starts from there.
So: game x = clamp(cursor x - 96, 0, 319), game y = clamp(cursor y - 92, 0, 199), cursor += (3.0, 1.5) x capped counts.

THE CHAIN IN OUR CODE (what is known exactly, and what only the 486 can say):
- vcctrl (gateway2000 profile: usb4vc uinput, no mouse_max_step): one `mouse move` = one EV_REL event, any size.
- USB4VC IBM PC board: queued events summed into one PS/2 packet, each axis capped at +-127 (firmware
  get_consolidated_mouse_event -> cap_to_127; vcctrl's firmware/usb4vc-ibmpc). Clip, not carry -- the DRIVE 5 logs
  agree: 150 / 180 / 190-count moves moved exactly 127 counts (a carry would have reached the clamps).
- CuteMouse 2.1b4: PS/2 packets -> its mickey counters. UNKNOWN from code: whether its counters are speed-doubled or
  accelerated (INT 33h fn 13h double-speed applies to the cursor position in the MS spec, not to fn 0Bh's counters).
- AGS: "Mouse speed control: enabled" (STDOUT) -> Mouse::SetMovementControl(true) -> SDL relative mouse mode, with
  SDL_HINT_MOUSE_RELATIVE_SPEED_SCALE set to AGS's speed (a constant).
- SDL3-DOS (vendor/SDL src/video/dos/SDL_dosevents.c): in relative mode each pump reads INT 33h fn 0Bh (mickeys since
  the last read) and divides by the mickeys-per-pixel from fn 1Bh (defaults 8 horizontal / 16 vertical -- hence y
  moves half of x); SDL3 core multiplies by the speed scale, adds to its own cursor and clamps it to the window
  (SDL_mouse.c ConstrainMousePosition: 0..511 x 0..383). SDL3-DOS also sets the driver range to the mode (fn 7/8).
  It never calls fn 0Fh (ratio), 13h (double-speed) or 1Ah (sensitivity): the driver's defaults stand.
- AGS reads SDL's window position and maps the 1:1 frame at (96,92) (Mouse cursor graphic area), clamping only what
  it reads (device/mousew32.cpp Mouse::Poll): the hidden margins.
Everything after CuteMouse's counters is linear in them.
SMALL PACKETS (round RI, RICAL, 2026-11-11): a packet under 12 counts moves less than 3.0 / 1.5 px per count. A packet
of <= 9 counts loses 8/3 counts (x 8 counts: 16 px, not 24, so x 269; 16 y counts as 4 packets of 4: 7.5 px, so y 106),
10 lose 2, 11 lose 1, 12 and up none: small_loss() reproduces all 19 of RICAL's small-packet points to 1 px (17 exact).
It is NOT in our code: SDL3-DOS divides fn 0Bh's integer mickeys by a float mickeys-per-pixel, SDL3 keeps a float cursor
(integer mode off: AGS never sets SDL_MOUSE_INTEGER_MODE), AGS truncates only its reading; per-read truncation there
cannot lose 8 px of a 24-px move. So it is upstream of fn 0Bh (CuteMouse or the board), whose source is not here.
The y gain stays 1.5, exactly half of x (SDL3-DOS: fn 1Bh's 8 / 16 mickeys per pixel). Independent y packets: RICAL's
CAL-BR 120 counts -> 180 px from the 383 clamp; DRIVE 5's 127 / 90 / 40 counts -> 1.50 / 1.50 / 1.475 px per count.
RICAL's DY slopes (1.866 over 8..21, 1.59 over 12..21, 1.63 over 15..21) are the small-packet loss at 8..11 plus
whole-pixel readings of 1.5-px steps over a 6..9-count span; the model predicts every DY point >= 12 to 1 px (12 -> 116
and 21 -> 130 exactly). No separate y correction (vertical ratio, SDL rounding, corner state) is needed: the corners
clamp y exactly (TR / TL to 0, BR to 383, all as measured).
The play path sends only single packets of 15..127 counts (corners 127, DX 39..88, DY >= 15), so only the
calibration's small probes see the loss. The 486's logs say the whole chain is linear for single
packets of 40..127 counts (x 3.0 / y 1.5 px per count); packets under 40 counts and slow vs fast delivery are not in
any log yet: the calibration cell's measurement prelude measures them (drive6-cal.py check C10).
The lab (DOSBox-X) reproduces none of this: its own INT 33h mouse emulation, no PS/2 path, no USB4VC board, and the
lab cells place the cursor directly (DOSAGS_LABCLICKS). It reproduces only the game side: what lies under a point.
The earlier estimate (x 1.50, y 1.42-1.48 game px per count) paired DRIVE 5's moves with its points without the cap and
the hidden margins; it is withdrawn."""
import glob, os, re, sys

GX, GY, CAP = 3.0, 1.5, 127
DRV_W, DRV_H = 511, 383
OFF_X, OFF_Y = 96, 92


def capc(v):
    return max(-CAP, min(CAP, v))


def small_loss(n):
    """counts a packet of n counts (per axis) loses before CuteMouse's cursor sees it -- round RI's RICAL, every
    small-packet point to 1 px: <= 9 counts lose 8/3 (8 px in x, 4 px in y), 10 lose 2, 11 lose 1, 12 and up none.
    Upstream of INT 33h fn 0Bh (CuteMouse's count handling or the board): our SDL3-DOS / AGS path is float end to end."""
    a = abs(n)
    loss = 8 / 3. if a <= 9 else {10: 2.0, 11: 1.0}.get(a, 0.0)
    loss = min(loss, a)
    return (a - loss) * (1 if n >= 0 else -1)


class Pointer:
    def __init__(self, x=256.0, y=192.0, gx=GX, gy=GY, bot=DRV_H, small=True):
        self.x, self.y, self.gx, self.gy, self.bot, self.small = float(x), float(y), gx, gy, bot, small

    def move(self, dx, dy):
        cx, cy = capc(dx), capc(dy)
        if self.small:
            cx, cy = small_loss(cx), small_loss(cy)
        self.x = min(DRV_W, max(0.0, self.x + self.gx * cx))
        self.y = min(self.bot, max(0.0, self.y + self.gy * cy))

    def game(self):
        return (min(319, max(0, int(self.x) - OFF_X)), min(199, max(0, int(self.y) - OFF_Y)))


def replay(dirs):
    runs = ok = 0
    walks = walk_ok = 0
    bad = []
    for d in dirs:
        for log in sorted(glob.glob(os.path.join(d, '*', 'DRIVE-WALK.LOG'))) or sorted(glob.glob(os.path.join(d, 'DRIVE-WALK.LOG'))):
            cell = os.path.dirname(log)
            st = os.path.join(cell, 'STDOUT.TXT')
            if not os.path.exists(st):
                continue
            text = open(log, errors='replace').read()
            moves = [tuple(int(v) for v in m) for m in re.findall(r'click \d+\s+move (-?\d+) (-?\d+)', text)]
            if 'homed to top-left' not in text or not moves:
                continue
            ev, room = [], None
            for l in open(st, errors='replace'):
                m = re.search(r'Now in room (-?\d+)', l)
                if m:
                    room = int(m.group(1)); continue
                m = re.search(r'MoveCharacter: request move cDave: (-?\d+),(-?\d+) to (-?\d+),(-?\d+)', l)
                if m:
                    ev.append(('walk', room, int(m.group(1)), int(m.group(3)), int(m.group(4)))); continue
                m = re.search(r'Mouse click over GUI (\d+)', l)
                if m:
                    ev.append(('gui', int(m.group(1))))
            p = Pointer(0, 0)                     # drive-walk.sh homes with 4 x (-120,-120): the driver sits at (0,0)
            pred = []
            for dx, dy in moves:
                p.move(dx, dy); pred.append(p.game())
            good = True
            for k, e in enumerate(ev[:7]):        # the first 7 clicks: before any verb change
                if k >= len(pred):
                    break
                x, y = pred[k]
                if e[0] == 'walk':
                    cam = 0 if e[1] == 1 else max(0, min(640, e[2] - 160))
                    walks += 1
                    if abs(e[3] - cam - x) <= 1 and abs(e[4] - y) <= 1:
                        walk_ok += 1
                    else:
                        good = False
                elif (e[1] == 1 and y < 143) or (e[1] == 10 and y > 0):
                    good = False                  # GUI 1 is the verb bar (y >= 143); GUI 10 the top strip
            runs += 1; ok += good
            if not good:
                bad.append(os.path.basename(cell))
    print('runs %d: first 7 clicks as predicted in %d; walk targets within 1 px: %d / %d' % (runs, ok, walk_ok, walks))
    if bad:
        print('not as predicted: %s' % ', '.join(bad))
    # round RH's calibration press: the corner (+480,-480) from wherever the cursor started, then (0,+88)
    p = Pointer(256, 192); p.move(480, -480); p.move(0, 88)
    print('RHCAL press 1 (corner +480,-480 then 0,+88) predicted %s; logged (319,39)' % (p.game(),))


def plan(path, a):
    gx = float(a[a.index('--gx') + 1]) if '--gx' in a else GX
    gy = float(a[a.index('--gy') + 1]) if '--gy' in a else GY
    sx, sy = ((float(a[a.index('--start') + 1]), float(a[a.index('--start') + 2])) if '--start' in a else (256, 192))
    p = Pointer(sx, sy, gx, gy)
    cur = None
    for l in open(path):
        m = re.match(r'press (\d+) at \+([\d.]+)s (\S+)', l)
        if m:
            if cur:
                print('%s %s %s %d %d' % (cur + p.game()))
            cur = (m.group(1), m.group(2), m.group(3))
            continue
        m = re.search(r'mouse move (-?\d+) (-?\d+)|\(move (-?\d+) (-?\d+)\)', l)   # split calls, or one-call press moves
        if m:                                   # moves before the first press too (the park)
            p.move(int(m.group(1) or m.group(3)), int(m.group(2) or m.group(4)))
    if cur:
        print('%s %s %s %d %d' % (cur + p.game()))


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] not in ('replay', 'plan'):
        print(__doc__); sys.exit(2)
    if a[0] == 'replay':
        replay(a[1:])
    else:
        plan(a[1], a[2:])
