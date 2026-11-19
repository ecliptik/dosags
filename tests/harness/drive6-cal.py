#!/usr/bin/env python3
"""drive6-cal.py -- read a DRIVE 6 calibration cell (drive-walk6.sh DRIVE6_MODE=cal) from the game's own log.

    drive6-cal.py STDOUT.TXT PLAN [--json]
    drive6-cal.py --play STDOUT.TXT PLAN [--json]      an MS3 play cell (DRIVE6_MODE=ms): every press's logged target
    drive6-cal.py --recheck STDOUT.TXT PLAN REF_CAL_DIR [--json]
                                                       the short re-check (DRIVE6_MODE=calq) against a full calibration

STDOUT.TXT is the cell's collected game log. PLAN is the cell's DRIVE-WALK.LOG (lines "click N  KIND planned=...") or a
drive-walk6.sh --dry-run listing (lines "press N at +Ts KIND"); either gives the presses in order, and its first line
gives the sweep's centre DY (presses without their own /DY= use it).

THE WITNESS. Every walk click logs "MoveCharacter: request move cDave: X0,Y0 to X,Y", the click's exact room point.
Room 1's camera is at 0: X,Y is the screen point. In room 2 the camera is clamped at 640 while the kid is at x >= 800:
screen x = X - 640. Press k is matched to the k-th cDave walk target after the restore, so the count must equal the
press count, or nothing passes.

THE READING. The pointer is linear (drive6-pointer.py): from a corner, x and y move a fixed number of px per count. For
each quantity every press gives a point (counts, logged coordinate): DXL (room-1 x from TL), DXA and DXB (room-2 x from
TR), DY (y of every press: all reach y the same way, TL / TR, then +127, then +DY or the press's own /DY=w). A
least-squares line through each quantity's points gives the value that hits the target; the sweep is wide, so one run
finds it even when the default is off.

THE CHECKS (DRIVE6-RIG-CHECKS.md):
  C1  every press walks: targets == presses, rooms exactly [1, 2], no GUI click, each press in its room, room-1 points
      (but CAL-EXIT) at x >= 20, every point at y <= 142
  C2  CAL-C x == 319 on every press (the TR corner)
  C3  CAL-EXIT x == 0 (the TL corner)
  C4-C7  DY / DXL / DXA / DXB: the fitted line's value for the target (>= 15) lands inside the band, AND lies inside
      the swept range (an interpolation). Outside the range it is an extrapolation: a re-centre, not a pass.
  C8  repeatability: each value's repeats within 2 px
  C9  the slope is the model's within 25%: DXL +3.0, DXA / DXB -3.0, DY +1.5 px per count. Anything else: the path is
      not the one the model and drive-walk6.sh assume
  C10 linearity over exactly the sizes the play path sends (amended after round RI, sdlports): each quantity's sweep
      points of 15 counts and up (DXL 44..60, DXA 66..81, DXB 39..51, DY 15..21: single packets, measured directly) lie
      within 2 px of their line. Any failure stops: the fit would not transfer.
      INFORMATION, not a check: the whole measurement prelude (one-packet sizes 8..88, slow / fast multi-packet moves,
      the 4-count y probe, the clip / carry probe) and every sweep value under 15 counts. Reason: the play path sends
      one packet per move, all of 15..127 counts; smaller packets lose counts upstream of INT 33h (round RI: <= 9
      counts lose 8/3; drive6-pointer.py small_loss) and multi-packet moves are never sent. A chosen value is never
      under 15 (the nearest allowed value is taken, and C4 checks it lands in band).
  Information: CAL-MCLIP (one 200-count packet) says whether the board clips a packet at 127 (x 75) or carries the
  excess (x 205); DRIVE 6 never sends more than 127 otherwise. CAL-BR (BR corner, (-DXA, -120)) reads the screen's
  bottom bound (383 expected; SDL3-DOS sets the range to the mode, 512x384).
Targets and bands: DY y 120 (116..140; 23 px above the verb bar); DXL x 60 (48..72); DXA x 190 (177..201); DXB x 289 (276..300).
Output ends with the env line for drive-walk6.sh and an overall PASS / FAIL. Exit status 0 on PASS, 1 on FAIL, 2 on
unreadable input. --json adds one JSON line: every failure under its check, and per quantity the line, the chosen
value, its predicted landing, whether it is inside the swept range, and its repeats.

--play (an MS3 cell, DRIVE6_MODE=ms): every press's walk target against its band. Bands (LAB-MOVE MS3, +-12 px):
  R x == 319 (room 1); L x 48..72 (room 1); EXIT x == 0 (room 1; the room change follows);
  A room x 817..841 and B room x 916..940 (room 2); every press y 116..140.
FAIL also on a press with no walk target, a "Mouse click over GUI" after the first press, or a return to room 1."""
import json, re, statistics as S, sys, time

Q = {  # quantity: (axis, target, lo, hi, model slope px/count, check, env)
    'DY': ('y', 120, 116, 140, 1.5, 'C4', 'DRIVE6_DY'),
    'DXL': ('x', 60, 48, 72, 3.0, 'C5', 'DRIVE6_DXL'),
    'DXA': ('x', 190, 177, 201, -3.0, 'C6', 'DRIVE6_DXA'),
    'DXB': ('x', 289, 276, 300, -3.0, 'C7', 'DRIVE6_DXB'),
}
ORDER = ('DY', 'DXL', 'DXA', 'DXB')
TOL = 2.0
DRIFT_FULL = 6              # calq: a PASS with a point more than 6 px from the reference -> NEXT-FULL-CAL
SMALL = 15                  # the play path sends single packets of 15..127 counts (DY 15, DX 39..88, corners 127); the
                            # checks cover exactly those sizes (sdlports, after round RI). Smaller packets lose counts
                            # upstream of INT 33h (drive6-pointer.py small_loss; RI: 12 and up lossless): information
MCLIP_BACK = 70             # CAL-MCLIP's second x packet (drive-walk6.sh)
SLOPE_TOL = 0.25
CAMERA2 = 640
ROOM = {'CAL-C': 1, 'CAL-DXL': 1, 'CAL-EXIT': 1, 'CAL-DXA': 2, 'CAL-DXB': 2, 'CAL-BR': 2, 'CAL-MX': 1, 'CAL-MXS': 1,
        'CAL-MXF': 1, 'CAL-MCLIP': 1, 'CAL-MY': 1, 'CAL-MYS': 1}

PLAY = {'R': (1, 319, 319), 'L': (1, 48, 72), 'EXIT': (1, 0, 0), 'A': (2, 817, 841), 'B': (2, 916, 940)}
Y_BAND = (116, 140)


def plan(path, kinds=r'CAL-[A-Z]+(?:=\d+(?:/DY=\d+)?)?'):
    out = []
    for l in open(path, errors='replace'):
        m = re.search(r'\b(?:click|press) (\d+)\s+(?:at \+[\d.]+s )?(' + kinds + r')(?:\s|$)', l)
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return [k for _, k in sorted(out)]


def centre_dy(path):
    for l in open(path, errors='replace'):
        m = re.search(r'mode cal\): centre DY=(\d+)|mode cal: centre DY=(\d+)', l)
        if m:
            return int(m.group(1) or m.group(2))
    return None


def game_log(path):
    """cDave walk targets after the restore as (room, screen x, y), the rooms entered, and the GUI clicks"""
    pts, rooms, gui = [], [], []
    room = None
    for l in open(path, errors='replace'):
        m = re.search(r'Now in room (-?\d+)', l)
        if m:
            room = int(m.group(1)); rooms.append(room)
            continue
        m = re.search(r'\(room:(-?\d+)\).*MoveCharacter: request move cDave: (-?\d+),(-?\d+) to (-?\d+),(-?\d+)', l)
        if m and room in (1, 2):
            pts.append((room, int(m.group(4)) - (CAMERA2 if room == 2 else 0), int(m.group(5))))
            continue
        if pts and 'Mouse click over GUI' in l:
            gui.append(l.strip()[-60:])
    return pts, rooms, gui


def fitline(pts):
    n = len(pts)
    mx = sum(v for v, c in pts) / float(n)
    my = sum(c for v, c in pts) / float(n)
    sxx = sum((v - mx) ** 2 for v, c in pts)
    if sxx == 0:
        return None, None
    b = sum((v - mx) * (c - my) for v, c in pts) / sxx
    return my - b * mx, b


PARTIAL_LAG = 1.0           # the board's drop counters are polled about once a second: a pkt_partial polled at T happened
                            # in (T - 1 s, T]


def board_partials(walk_log, npress):
    """The board's partial-packet record for a DRIVE 6 cell (round RJ; pre-registered for the next round): vcctrld's
    INPUT-LOG.jsonl beside DRIVE-WALK.LOG, its `mouse.dropped` rows with pkt_partial > 0 (polled_t = the board poll that
    saw it). A partial packet leaves CuteMouse's PS/2 byte framing shifted for the rest of the run (RJM1 / RJM2: every
    press after it lands bottom-left, docs/lab/LAB-MOVE.md section 10), so the cell is void from the press whose time
    window can hold it: the first press whose call ENDS at or after polled_t - PARTIAL_LAG (a partial before press 1,
    in the park, voids from press 1). Press windows come from the same file's own cmd rows (mouse_press, or a split
    press's mouse_up), by the lock's owner, so both times are on vcctrld's clock.
    Returns (void_from, reason, info lines); void_from None = no partial within the presses; 0 = unreadable."""
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(walk_log)), 'INPUT-LOG.jsonl')
    if not os.path.exists(path):
        return 0, 'no INPUT-LOG.jsonl beside DRIVE-WALK.LOG: the board\'s partial-packet record is missing', []
    rows = []
    for l in open(path, errors='replace'):
        try:
            rows.append(json.loads(l))
        except ValueError:
            pass
    owner = next((r.get('owner') for r in rows if r.get('kind') == 'lock.acquired'), None)
    ends = [r['t'] for r in rows if r.get('kind') == 'cmd' and r.get('cmd') in ('mouse_press', 'mouse_up')
            and (owner is None or r.get('by') == owner)]
    drops = [r for r in rows if r.get('kind') == 'mouse.dropped']
    utc = lambda t: time.strftime('%H:%M:%S', time.gmtime(t)) + ('%.3fZ' % (t % 1))[1:]
    info = ['board drop polled %s: %s' % (utc(r['polled_t']), ' '.join('%s=%s' % (k, v) for k, v in sorted(r.items())
            if k not in ('kind', 'seq', 't', 'polled_t'))) for r in drops]
    parts = sorted(r['polled_t'] for r in drops if r.get('pkt_partial'))
    if not parts or not ends or parts[0] - PARTIAL_LAG > ends[-1]:
        return None, '', info
    if len(ends) != npress:
        return 0, 'board pkt_partial polled %s, but INPUT-LOG holds %d press calls for %d presses: cannot place it' % (
            utc(parts[0]), len(ends), npress), info
    k = next(i + 1 for i, e in enumerate(ends) if e >= parts[0] - PARTIAL_LAG)
    return k, ('framing slip at press %d (pkt_partial polled t=%s, INPUT-LOG mouse.dropped; press %d\'s call ended %s): '
               'presses %d..%d void' % (k, utc(parts[0]), k, utc(ends[k - 1]), k, npress)), info


def play(a):
    """--play: an MS3 cell's pointing, press by press. VOID first of all from a board partial packet (board_partials)."""
    presses = plan(a[1], r'R|L|EXIT|A|B')
    pts, gui, rooms = [], [], []
    room = None
    for l in open(a[0], errors='replace'):
        m = re.search(r'Now in room (-?\d+)', l)
        if m:
            room = int(m.group(1)); rooms.append(room); continue
        m = re.search(r'\(room:(-?\d+)\).*MoveCharacter: request move cDave: (-?\d+),(-?\d+) to (-?\d+),(-?\d+)', l)
        if m and room in (1, 2):
            pts.append((room, int(m.group(4)), int(m.group(5)))); continue
        if pts and 'Mouse click over GUI' in l:
            gui.append(l.strip()[-50:])
    fails = []
    vfrom, why, info = board_partials(a[1], len(presses))
    for l in info:
        print('  %s' % l)
    if vfrom is not None:
        fails.append(why)                       # first: the gate's PLAY-VOID line names it
        print('BOARD PARTIAL: %s' % why)
    print('presses planned / sent: %d; walk targets logged: %d; rooms entered: %s' % (len(presses), len(pts), rooms))
    if len(pts) != len(presses):
        fails.append('logged %d walk targets for %d presses' % (len(pts), len(presses)))
    if rooms.count(1) > 1 or (2 in rooms and rooms.index(2) != len(rooms) - 1):
        fails.append('a room change after room 2 (rooms %s): the exit fired' % rooms)
    for g in gui:
        fails.append('GUI click: %s' % g)
    per = {}
    for i, (k, (room, x, y)) in enumerate(zip(presses, pts)):
        want_room, lo, hi = PLAY[k]
        per.setdefault(k, []).append(x)
        bad = []
        if room != want_room:
            bad.append('room %d, want %d' % (room, want_room))
        if not lo <= x <= hi:
            bad.append('x %d outside %d..%d' % (x, lo, hi))
        if not Y_BAND[0] <= y <= Y_BAND[1]:
            bad.append('y %d outside %d..%d' % (y, Y_BAND[0], Y_BAND[1]))
        if bad:
            fails.append('press %d %s at (%d,%d): %s' % (i + 1, k, x, y, '; '.join(bad)))
    for k in ('R', 'L', 'EXIT', 'A', 'B'):
        if k in per:
            v = per[k]
            print('  %-4s n %3d  x %d..%d (median %g)' % (k, len(v), min(v), max(v), S.median(v)))
    print('RESULT: %s' % ('PASS' if not fails else 'FAIL'))
    for f in fails[:40]:
        print('  FAIL: %s' % f)
    if len(fails) > 40:
        print('  ... %d more' % (len(fails) - 40))
    if '--json' in a:
        print(json.dumps({'pass': not fails, 'fails': fails}))
    sys.exit(0 if not fails else 1)


def recheck(a):
    """--recheck: a calq cell's 13 presses. The reference (REF_CAL_DIR: the last full calibration; its STDOUT.TXT and
    DRIVE-WALK.LOG) is re-read with this script's current rules and must PASS, and the calq cell must use its values.
    Every press must walk (rooms [1, 2], no GUI click) and land inside MS3's landing bands -- the same bands a full
    calibration's values must hit and MS3's own play check uses -- so a re-check PASS means for MS3 what a full-cal PASS
    means. Any miss: the full cal.
    Drift (information, and one flag): each point's distance from the reference's own measurement (x per kind, corners
    319 / 0; y the reference's DY median) is printed beside it, and the worst point of each quantity in the summary and
    the gate's PASS line. A PASS with any point more than DRIFT_FULL px from the reference is flagged NEXT-FULL-CAL:
    the next power-on runs the full calibration instead of chaining calq on a drifting reference."""
    import os, subprocess
    presses = plan(a[1])
    pts3, rooms, gui = game_log(a[0])
    ref_dir = a[2]
    r = subprocess.run([sys.executable, os.path.abspath(__file__), os.path.join(ref_dir, 'STDOUT.TXT'),
                        os.path.join(ref_dir, 'DRIVE-WALK.LOG'), '--json'], capture_output=True, text=True)
    fails = []
    try:
        ref = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        print('UNREADABLE: the reference %s gave no reading' % ref_dir); sys.exit(2)
    if not ref.get('pass'):
        fails.append('the reference calibration does not PASS under the current rules: %s' % (ref.get('fails') or ['?'])[0])
    head = open(a[1], errors='replace').readline()
    used = dict((k, int(v)) for k, v in re.findall(r'\b(DY|DXL|DXA|DXB)=(\d+)', head))
    renv = ref.get('env', {})
    for k in ('DY', 'DXL', 'DXA', 'DXB'):
        if used.get(k) != renv.get('DRIVE6_' + k):
            fails.append('calq uses %s=%s, the reference chose %s' % (k, used.get(k), renv.get('DRIVE6_' + k)))
    q = ref.get('quantities', {})
    # the pass bands are MS3's landing bands (sdlports): a re-check PASS means for MS3 what a full-cal PASS means
    band = {'CAL-C': (319, 319), 'CAL-EXIT': (0, 0), 'CAL-DXL': (Q['DXL'][2], Q['DXL'][3]),
            'CAL-DXA': (Q['DXA'][2], Q['DXA'][3]), 'CAL-DXB': (Q['DXB'][2], Q['DXB'][3])}
    yband = (Q['DY'][2], Q['DY'][3])
    refm = {}
    for k, qq in (('CAL-DXL', 'DXL'), ('CAL-DXA', 'DXA'), ('CAL-DXB', 'DXB'), ('DY', 'DY')):
        m = q.get(qq, {}).get('measured_at_chosen') or []
        refm[k] = S.median(m) if m else None
    print('recheck against %s (env %s): pass bands = MS3\'s: x C 319 / DXL %d..%d / EXIT 0 / DXA %d..%d / DXB %d..%d, '
          'y %d..%d; the reference measured DXL %s / DXA %s / DXB %s / y %s (information)' % (
              ref_dir, ' '.join('%s=%s' % kv for kv in sorted(renv.items())), band['CAL-DXL'][0], band['CAL-DXL'][1],
              band['CAL-DXA'][0], band['CAL-DXA'][1], band['CAL-DXB'][0], band['CAL-DXB'][1], yband[0], yband[1],
              refm['CAL-DXL'], refm['CAL-DXA'], refm['CAL-DXB'], refm['DY']))
    print('presses planned / sent: %d; walk targets logged: %d; rooms entered: %s' % (len(presses), len(pts3), rooms))
    if len(pts3) != len(presses):
        fails.append('logged %d walk targets for %d presses' % (len(pts3), len(presses)))
    if rooms != [1, 2]:
        fails.append('rooms entered %s, want [1, 2]' % rooms)
    for g in gui:
        fails.append('GUI click: %s' % g)
    refx = {'CAL-C': 319, 'CAL-EXIT': 0, 'CAL-DXL': refm['CAL-DXL'], 'CAL-DXA': refm['CAL-DXA'], 'CAL-DXB': refm['CAL-DXB']}
    worst = {}                                          # quantity -> (abs drift, landing, reference, drift)

    def dr(name, v, r):                                 # 'DXL 57 (ref 60, -3 px)'; keeps each quantity's worst point
        if r is None:
            return '%s %d (no reference)' % (name, v)
        d = v - r
        if name not in worst or abs(d) > worst[name][0]:
            worst[name] = (abs(d), v, r, d)
        return '%s %d (ref %g, %+g px)' % (name, v, r, d)
    for i, (k, (room, x, y)) in enumerate(zip(presses, pts3)):
        kk = k.partition('=')[0]
        lo, hi = band.get(kk, (None, None))
        bad = []
        if room != ROOM.get(kk, 1):
            bad.append('room %d' % room)
        if lo is None or not lo <= x <= hi:
            bad.append('x %d outside %s..%s' % (x, lo, hi))
        if not yband[0] <= y <= yband[1]:
            bad.append('y %d outside %d..%d' % (y, yband[0], yband[1]))
        drift = '   %s / %s' % (dr({'CAL-C': 'C', 'CAL-EXIT': 'EXIT'}.get(kk, kk[4:]), x, refx.get(kk)), dr('y', y, refm['DY']))
        print('   %2d %-12s (%3d,%3d) %s%s' % (i + 1, k, x, y, 'ok' if not bad else 'MISS: ' + '; '.join(bad), drift))
        if bad:
            fails.append('press %d %s at (%d,%d): %s' % (i + 1, k, x, y, '; '.join(bad)))
    names = [n for n in ('DXL', 'DXA', 'DXB', 'y') if n in worst]
    summary = ' / '.join('%s %d (ref %g, %+g px)' % ((n,) + worst[n][1:]) for n in names)
    maxd = max([w[0] for w in worst.values()] or [0])
    nfc = not fails and maxd > DRIFT_FULL
    print('drift from the reference (each quantity\'s worst point): %s; max %g px over all points' % (summary or 'none', maxd))
    print('RESULT: %s' % ('PASS' if not fails else 'FAIL'))
    for f in fails:
        print('  FAIL: %s' % f)
    if nfc:
        print('NEXT-FULL-CAL: a point is %g px from the reference (> %d): this power-on may use the values (every press is'
              ' in MS3\'s bands), but the next power-on runs the full calibration, not calq on this reference' % (maxd, DRIFT_FULL))
    if '--json' in a:
        print(json.dumps({'pass': not fails, 'env': renv, 'fails': fails, 'drift': summary, 'max_drift': maxd,
                          'next_full_cal': nfc}, sort_keys=True))
    sys.exit(0 if not fails else 1)


def main():
    a = sys.argv[1:]
    if a and a[0] == '--recheck':
        try:
            recheck(a[1:])
        except OSError as e:
            print('UNREADABLE: %s' % e); sys.exit(2)
    if a and a[0] == '--play':
        try:
            play(a[1:])
        except OSError as e:
            print('UNREADABLE: %s' % e); sys.exit(2)
    if len(a) < 2:
        print(__doc__); sys.exit(2)
    try:
        presses = plan(a[1])
        dy0 = centre_dy(a[1])
        pts3, rooms, gui = game_log(a[0])
    except OSError as e:
        print('UNREADABLE: %s' % e); sys.exit(2)
    if not presses:
        print('UNREADABLE: no CAL- presses in %s' % a[1]); sys.exit(2)
    if dy0 is None:
        print('UNREADABLE: no "mode cal: centre DY=" line in %s' % a[1]); sys.exit(2)
    fails = []
    checks = {c: [] for c in ('C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10')}

    def fail(c, msg):
        fails.append(msg); checks[c].append(msg)

    print('presses planned / sent: %d; walk targets logged: %d; rooms entered: %s; centre DY %d' % (
        len(presses), len(pts3), rooms, dy0))
    if len(pts3) != len(presses):
        fail('C1', 'logged %d walk targets for %d presses: a press did not walk (GUI / object / hotspot / dropped)' % (
            len(pts3), len(presses)))
    if rooms != [1, 2]:
        fail('C1', 'rooms entered %s, want [1, 2] (one room change, after CAL-EXIT)' % rooms)
    for g in gui:
        fail('C1', 'GUI click: %s' % g)
    data = {q: [] for q in Q}
    corner, exitp, br = [], [], []
    pre = {'MX': [], 'MXS': [], 'MXF': [], 'MCLIP': [], 'MY': [], 'MYS': []}
    for k, (room, x, y) in zip(presses, pts3):
        q, _, v = k.partition('=')
        w = dy0
        if '/DY=' in v:
            v, w = v.split('/DY=')
            w = int(w)
        if room != ROOM.get(q, 1):
            fail('C1', '%s logged in room %d, want room %d' % (k, room, ROOM.get(q, 1)))
        if y > 142 or (room == 1 and q != 'CAL-EXIT' and x < 20):
            fail('C1', '%s logged (%d,%d): outside x >= 20, y <= 142' % (k, x, y))
        if q == 'CAL-BR':
            br.append(y); continue
        if q == 'CAL-MYS':                              # the slow y probe: compared, not fitted
            pre['MYS'].append((int(v), y)); continue
        if q == 'CAL-MY':
            pre['MY'].append((int(v), y)); data['DY'].append((int(v), y)); continue
        if q in ('CAL-MX', 'CAL-MXS', 'CAL-MXF', 'CAL-MCLIP'):
            pre[q[4:]].append((int(v), x))
        data['DY'].append((w, y))
        if q == 'CAL-C':
            corner.append(x)
        elif q == 'CAL-EXIT':
            exitp.append(x)
        elif q == 'CAL-DXL':
            data['DXL'].append((int(v), x))
        elif q == 'CAL-DXA':
            data['DXA'].append((int(v), x))
        elif q == 'CAL-DXB':
            data['DXB'].append((int(v), x))
    ok_c = bool(corner) and all(x == 319 for x in corner)
    print('CAL-C    TR corner: x %s -> %s' % (sorted(set(corner)), 'PASS' if ok_c else 'FAIL (x must be 319)'))
    if not ok_c:
        fail('C2', 'TR corner: CAL-C x %s, want 319' % sorted(set(corner)))
    ok_e = exitp == [0]
    print('CAL-EXIT TL corner: x %s -> %s' % (exitp, 'PASS' if ok_e else 'FAIL (x must be 0, once)'))
    if not ok_e:
        fail('C3', 'TL corner: CAL-EXIT x %s, want [0]' % exitp)
    # C10: the transfer function, from the prelude
    trans = {}
    if pre['MX']:
        a0, b = fitline(pre['MX']) if len(set(v for v, c in pre['MX'])) > 1 else (None, None)
        if b is None:
            fail('C10', 'prelude: fewer than 2 CAL-MX sizes logged')
        else:
            big = [(v, c) for v, c in pre['MX'] if v >= SMALL]
            small = [(v, c) for v, c in pre['MX'] if v < SMALL]
            if len(set(v for v, c in big)) > 1:
                a0, b = fitline(big)                    # the line is fitted on the play path's sizes only (>= 12)
            resid = max(abs(c - (a0 + b * v)) for v, c in big) if big else 0.0
            print('PRELUDE  (information) one packet of d >= %d counts from x %.1f: x = %.1f %+.3f d (model 285 - 3.0 d); max residual %.1f px' % (
                SMALL, a0, a0, b, resid))
            for v, c in sorted(pre['MX']):
                print('   %3d counts: x %d  (%.2f px/count)%s' % (v, c, (a0 - c) / float(v),
                      ('   information: under %d counts, %.1f counts short of the line (the small-packet loss)' % (
                          SMALL, (c - (a0 + b * v)) / -b)) if v < SMALL else ''))
            trans['small_x'] = [(v, round((c - (a0 + b * v)) / -b, 2)) for v, c in small]
            trans.update({'intercept': round(a0, 2), 'slope': round(b, 4), 'max_residual': round(resid, 2)})
            # information only (sdlports, after round RI): C10 is the sweeps' linearity over the play path's sizes
            ref = [c for v, c in pre['MX'] if v == 60]
            for kind, lab in (('MXS', 'slow'), ('MXF', 'fast')):
                for v, c in pre[kind]:
                    r = ref[0] if ref else a0 + b * v
                    print('   %3d counts as 4 %s packets: x %d (one packet: %s)' % (v, lab, c, ref[0] if ref else '%.1f' % r))
                    trans[kind] = c - r                 # information: the play path sends one packet per move
            for v, c in pre['MCLIP']:
                clip = a0 + b * MCLIP_BACK                # +200 clipped to +127, then -70
                carry = min(415.0, (a0 + 96) * v / 127.0 - 96) + b * MCLIP_BACK
                kind = 'clip' if abs(c - clip) <= 3 else ('carry' if abs(c - carry) <= 3 else 'neither')
                print('   one %d-count packet then -%d: x %d -> %s (clip predicts %.0f, carry %.0f)' % (v, MCLIP_BACK, c, kind, clip, carry))
                trans['packet_over_127'] = kind
    for (v, y), (v2, y2) in zip(pre['MY'], pre['MYS']):
        # 4 slow packets of v/4 counts: under 12 counts each, so the small-packet loss, not a speed effect -- information
        print('   y: %d counts in one packet y %d; as 4 slow packets of %d y %d (%+d px)%s' % (v, y, v // 4, y2, y2 - y,
              ('   information: packets under %d counts, %.1f counts short each (the small-packet loss)' % (
                  SMALL, (y - y2) / 1.5 / 4)) if v // 4 < SMALL else ''))
        trans['MYS'] = y2 - y                           # information
    env, quant = {}, {}
    for q in ORDER:
        axis, target, lo, hi, slope0, cq, en = Q[q]
        pts = data[q]
        info = sorted(set((v, c) for v, c in pts if v < SMALL))   # the line on the play path's sizes only
        if info:
            print('%-4s information: values under %d counts (not sent in play; not fitted): %s' % (
                q, SMALL, ' '.join('%d->%s %d' % (v, axis, c) for v, c in info)))
        pts = [(v, c) for v, c in pts if v >= SMALL]
        vals = sorted(set(v for v, c in pts))
        if len(vals) < 2:
            fail('C1', '%s: %d distinct values logged, need >= 2' % (q, len(vals))); continue
        a0, b = fitline(pts)
        if b is None or b == 0:
            fail('C9', '%s: no response to the sweep' % q); continue
        resid = max(abs(c - (a0 + b * v)) for v, c in pts)
        chosen = int(round((target - a0) / b))
        if chosen < SMALL:                              # nearest value the play path may send: >= SMALL counts
            chosen = SMALL
        pred = a0 + b * chosen
        in_range = vals[0] <= chosen <= vals[-1]
        reps = [c for v, c in pts if v == chosen]
        print('%-4s %s target %d (band %d..%d): line %s = %.1f %+.3f x counts (model slope %+.1f); max residual %.1f px' % (
            q, axis, target, lo, hi, axis, a0, b, slope0, resid))
        for v in vals:
            cs = [c for vv, c in pts if vv == v]
            print('   %3d counts: %s %s  (n %d, spread %d)%s' % (v, axis, ' '.join(str(c) for c in cs), len(cs),
                  max(cs) - min(cs), '   <- chosen' if v == chosen else ''))
        if abs(b / slope0 - 1.0) > SLOPE_TOL:
            fail('C9', '%s: slope %+.3f px/count, model %+.1f (more than %d%% off)' % (q, b, slope0, SLOPE_TOL * 100))
        for v in vals:
            cs = [c for vv, c in pts if vv == v]
            if max(cs) - min(cs) > TOL:
                fail('C8', '%s=%d: repeats %s spread %d px > %d' % (q, v, cs, max(cs) - min(cs), TOL))
        if resid > TOL:
            fail('C10', '%s: a point of %d+ counts is %.1f px off the line (> %d): not linear over the play path\'s sizes' % (
                q, SMALL, resid, TOL))
        if not lo <= pred <= hi:
            fail(cq, '%s: the value nearest the target, %d, lands at %.1f, outside %d..%d' % (q, chosen, pred, lo, hi))
        elif not in_range:
            fail(cq, '%s: %d (landing %.1f) is outside the swept %d..%d: an extrapolation, re-centre' % (
                q, chosen, pred, vals[0], vals[-1]))
        print('   -> %s=%d: predicted %s %.1f, %s, measured %d time(s)%s' % (
            en, chosen, axis, pred, 'inside the sweep' if in_range else 'OUTSIDE the sweep (extrapolated)', len(reps),
            (' at %s' % reps) if reps else ''))
        env[en] = chosen
        quant[q] = {'env': en, 'chosen': chosen, 'predicted': round(pred, 1), 'in_band': lo <= pred <= hi,
                    'in_range': in_range, 'swept': [vals[0], vals[-1]], 'slope': round(b, 4), 'intercept': round(a0, 2),
                    'max_residual': round(resid, 2), 'measured_at_chosen': reps}
    bottom = None
    if br:
        bottom = S.median(br) + 92 + 1.5 * 120
        print('CAL-BR   bottom bound (information): y %s -> driver bottom %.0f (383 expected)' % (br, bottom))
    print('env: %s' % ' '.join('%s=%s' % (Q[q][6], env.get(Q[q][6], '?')) for q in ORDER))
    print('RESULT: %s' % ('PASS' if not fails else 'FAIL'))
    for f in fails:
        print('  FAIL: %s' % f)
    if '--json' in a:
        print(json.dumps({'pass': not fails, 'env': env, 'fails': fails, 'checks': checks, 'quantities': quant,
                          'bottom': bottom, 'transfer': trans}, sort_keys=True))
    sys.exit(0 if not fails else 1)


if __name__ == '__main__':
    main()
