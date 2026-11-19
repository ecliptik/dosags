#!/usr/bin/env python3
"""rr-read.py -- round RR's readings (the route-finder levers' ABBA on MS3; ags 0382, DOSAGS_ROUTE_FAST). Read-only.

THIS READER IS FOR AGS 0382 BINARIES ONLY (round RR, 2026-11-17). It requires 0382's manifest stamp and 0382's
"DOS-PORT routefast" witness line; ags 0383 removed the switch and that line ("DOS-PORT routestamp" instead), so a cell
of a later binary reads VOID here by design. The 114EDGE rule below expired with round RR.

  rr-read.py cell CELL_DIR ARM                       one READ line for a cell (ARM = O | F)
  rr-read.py verdict CELL_DIR:ARM [CELL_DIR:ARM...]  the round's terms over the given cells

Arms: O = no switch (the pinned finder: main's behaviour); F = DOSAGS_ROUTE_FAST=1.
Arm witness (RUNMANI.LOG "DOS-PORT routefast on= stamp_allocs= stamp_peak_bytes="):
  O: on=0 stamp_allocs=0.   F: on=1, stamp_allocs >= 1 and stamp_peak_bytes = 192000 (MS3's room 2 mask is 960 x 200;
  an F cell with stamp_allocs = 0 never ran the fast search and is VOID).
Cell VALID = the arm witness, the manifest stamp binary_sha12=483247a02652 (the 0382 release) in the cell's logs,
  RUNMANIFEST exit_code=0 and "ENGINE HAS SHUTDOWN", audio underruns = overwrites = 0, and the pairing: PAIR-OK or
  PAIR-OK-114LATE (ms3-pairing.py check()), or, FOR THIS ROUND ONLY, 114EDGE:
    114EDGE = 113 journeys for 114 presses, the pairing's ONLY failures are (3a) / (3b) (press 114's estimated game time
    is not after the last persec row / the loop-end estimate), and that estimate is no more than 150 ms short of the
    loop-end estimate (margin_over_est_ms >= -150). Why it exists: the levers end the run earlier (predicted 1.7-2.5 s,
    bound 3.7 s; RQ's O cells had press 114 2.5 s before the end), so press 114 can land inside the last moments, where a
    click cannot finish its journey. Why 150 ms: a click on the 486 needs its own click tick (about 60-70 ms with the
    levers) and up to two more frames (50 ms) to be presented and logged, and the pairing's own estimates carry +-30 ms.
    A cell with 112 journeys or fewer is PAIR-VOID as always -- a STATED LIMIT of this fixture: it means the run ended
    more than about 3.7 s earlier (a saving above about 31 ms per click), and MS3's press schedule then needs changing
    before the levers can be read on it. No 113LATE rule is added.
  A 114LATE or 114EDGE cell ran one click fewer than a 114-journey cell (about 4 skips: one click-second); it is VALID,
  and its count of click seconds is printed so the difference is seen.
Readings per cell (RUNMANI.LOG):
  skips    = frames_skipped (the whole run; the exit tick is 12,440 in every cell)
  disp     = 100 x (1 - skips / 7003): frames displayed over MS3's 7,003 play ticks (as rounds RL-RQ)
  cs, ncs  = mean skips per second over the CLICK seconds and over the other seconds. A second is one persec row
             (its skips = tick delta minus renders delta against the previous row); it is a click second when a click
             journey's t_ms falls in (previous row's ms, this row's ms]. Rows from the first click second on.
The third pair (cells named RRF3 / RRO3) is read only when BOTH of its cells are valid; otherwise the verdict is over
the registered cells (RRO1 RRF1 RRF2 RRO2) and a lone third-pair cell is printed as information.
Verdict (needs >= 2 valid cells in each arm: the registered pair; else NOT READ):
  CUT  = mean(O skips) - mean(F skips);  SPREAD = the larger of the two arms' ranges (max - min) in this round.
  SUPPORTED  CUT >= 80 (0.70 skips per click-second x 114), CUT > SPREAD, and every F cell's skips < every O cell's.
  FALSIFIED  CUT < 23 (0.20 x 114).
  MIXED      anything else.
  Information beside it: the cut per click second (mean cs O - mean cs F) and the change in the other seconds (the
  control: the levers touch only click ticks), each cell's disp, and whether the proof bar for the MS3 target (a
  registered pair, both >= 99.0%: here EVERY valid F cell, and at least two) is met by the F cells.
The lab's prediction, stated before the round (lab-rb RESULT-RSW-2 and the 0382 lab result; a model, never measured on
the 486): CUT between 153 and 220 skips per run (rule H to rule P), with the ensemble's smallest member near 40. The
run is predicted to END 1.7-2.5 s earlier in the F arm (bound 3.7 s), which is what the 114LATE / 114EDGE rules are for."""
import importlib.util
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location('ms3pairing', os.path.join(HERE, 'ms3-pairing.py'))
mp = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(mp)
PLAY_TICKS = 7003
STAMP = '483247a02652'   # the ags 0382 release (RF0382-2026-11-17)
EDGE_MS = -150.0
X_SKIPS, LOW_SKIPS = 80, 23


def rd(p):
    try:
        return open(p, errors='replace').read()
    except OSError:
        return ''


def cell(c, arm):
    rm, so = rd(c + '/RUNMANI.LOG'), rd(c + '/STDOUT.TXT')
    why = []
    w = re.search(r'DOS-PORT routefast on=(\d+) stamp_allocs=(\d+) stamp_peak_bytes=(\d+)', rm)
    wit = tuple(int(x) for x in w.groups()) if w else None
    if arm == 'O':
        ok = wit is not None and wit[0] == 0 and wit[1] == 0
    else:
        ok = wit is not None and wit[0] == 1 and wit[1] >= 1 and wit[2] == 192000
    if not ok:
        why.append('arm witness')
    logs = ''.join(rd(os.path.join(c, f)) for f in sorted(os.listdir(c)) if f.upper().endswith('.LOG')) if os.path.isdir(c) else ''
    stamps = set(re.findall(r'binary_sha12=([0-9A-Za-z]+)', logs))
    if stamps != {STAMP}:
        why.append('stamp %s' % (','.join(sorted(stamps)) or 'missing'))
    ec = re.search(r'^exit_code=(\d+)', rm, re.M)
    if not (ec and ec.group(1) == '0' and 'ENGINE HAS SHUTDOWN' in so):
        why.append('no clean exit')
    try:
        pv, pwhy, pw, _n = mp.check(c)
    except Exception:
        pv, pwhy, pw = 'PAIR-VOID', 'pairing unreadable', ''
    if pv == 'PAIR-VOID':
        fails = [f.strip() for f in pwhy.split(' | ')[0].split(';') if f.strip()]
        mg = re.search(r'margin_over_est_ms=([+-]?[0-9.]+)', pw)
        if (fails and all(f.startswith('(3a)') or f.startswith('(3b)') for f in fails) and 'journeys 113 / presses 114' in pwhy
                and mg and float(mg.group(1)) >= EDGE_MS):
            pv = '114EDGE(margin %+.0f ms)' % float(mg.group(1))
    if not (pv in ('PAIR-OK', 'PAIR-OK-114LATE') or pv.startswith('114EDGE')):
        why.append(pv)
    ur = re.search(r'underruns=(\d+)', rm)
    ow = re.search(r'overwrites=(\d+)', rm)
    if not (ur and ow and ur.group(1) == '0' and ow.group(1) == '0'):
        why.append('audio')
    fs = re.search(r'frames_skipped=(\d+)', rm)
    skips = int(fs.group(1)) if fs else None
    if skips is None:
        why.append('no frames_skipped')
    rows = [(int(a), int(b), int(d)) for a, b, d in re.findall(r'DOS-PORT persec t=\d+ tick=(\d+) renders=(\d+) real=\d+ skipped=\d+ ms=(\d+)', rm)]
    jt = [int(x) for x in re.findall(r'journey kind=click [^\n]*?t_ms=(\d+)', rm)]
    cs, ncs = [], []
    started = False
    for (t0, r0, m0), (t1, r1, m1) in zip(rows, rows[1:]):
        sk = (t1 - t0) - (r1 - r0)
        click = any(m0 < x <= m1 for x in jt)
        started = started or click
        if started:
            (cs if click else ncs).append(sk)
    return dict(c=c, arm=arm, valid=not why, why=why, wit=wit, pair=pv, skips=skips,
                disp=(100.0 * (1 - skips / float(PLAY_TICKS)) if skips is not None else None),
                cs=(st.mean(cs) if cs else None), ncs=(st.mean(ncs) if ncs else None), ncsec=len(cs), nosec=len(ncs),
                journeys=len(jt))


def line(x):
    f = lambda v, p='%.3f': ('n/a' if v is None else p % v)
    return ('READ %s arm=%s valid=%s%s pair=%s routefast=%s skips=%s disp=%s%% click-seconds=%d cs=%s other-seconds=%d ncs=%s journeys=%d' % (
        os.path.basename(x['c'].rstrip('/')), x['arm'], 'yes' if x['valid'] else 'no',
        '' if x['valid'] else ' (' + '; '.join(x['why']) + ')', x['pair'],
        'none' if x['wit'] is None else 'on=%d,allocs=%d,peak=%d' % x['wit'], x['skips'], f(x['disp'], '%.2f'),
        x['ncsec'], f(x['cs']), x['nosec'], f(x['ncs']), x['journeys']))


def verdict(args):
    cells = []
    for a in args:
        c, arm = a.rsplit(':', 1)
        cells.append(cell(c, arm))
    for x in cells:
        print(line(x))
    third = [x for x in cells if os.path.basename(x['c'].rstrip('/')).startswith(('RRF3', 'RRO3'))]
    if third and not (len(third) == 2 and all(x['valid'] for x in third) and {x['arm'] for x in third} == {'O', 'F'}):
        for x in third:
            print('third pair incomplete: %s is NOT in the verdict (information only: skips=%s valid=%s)' % (
                os.path.basename(x['c'].rstrip('/')), x['skips'], 'yes' if x['valid'] else 'no'))
        cells = [x for x in cells if x not in third]
    O = [x for x in cells if x['arm'] == 'O' and x['valid']]
    F = [x for x in cells if x['arm'] == 'F' and x['valid']]
    print('valid cells: O %d, F %d' % (len(O), len(F)))
    if len(O) < 2 or len(F) < 2:
        print('R-SKIPS: NOT READ (a registered pair per arm needs >= 2 valid cells in each)')
        return
    so, sf = [x['skips'] for x in O], [x['skips'] for x in F]
    cut = st.mean(so) - st.mean(sf)
    spread = max(max(so) - min(so), max(sf) - min(sf))
    sep = max(sf) < min(so)
    if cut >= X_SKIPS and cut > spread and sep:
        v = 'SUPPORTED'
    elif cut < LOW_SKIPS:
        v = 'FALSIFIED'
    else:
        v = 'MIXED'
    print('R-SKIPS: %s -- O skips %s (mean %.1f), F skips %s (mean %.1f); CUT %.1f per run (%.3f per click-second over 114); '
          'SPREAD %d; every F below every O: %s' % (v, so, st.mean(so), sf, st.mean(sf), cut, cut / 114.0, spread, 'yes' if sep else 'no'))
    print('lab prediction (model): CUT 153..220, smallest ensemble member near 40 -- measured CUT is %s the predicted range' % (
        'inside' if 153 <= cut <= 220 else ('below' if cut < 153 else 'above')))
    co, cf = st.mean(x['cs'] for x in O), st.mean(x['cs'] for x in F)
    no, nf = st.mean(x['ncs'] for x in O), st.mean(x['ncs'] for x in F)
    print('information: skips per CLICK second O %.3f -> F %.3f (cut %.3f); per OTHER second O %.3f -> F %.3f (change %+.3f: the control)' % (
        co, cf, co - cf, no, nf, nf - no))
    print('information: displayed O %s, F %s; MS3 proof bar (a registered pair, both >= 99.0%%) met by the F cells: %s' % (
        ', '.join('%.2f%%' % x['disp'] for x in O), ', '.join('%.2f%%' % x['disp'] for x in F),
        'YES' if (len(F) >= 2 and all(x['disp'] >= 99.0 for x in F)) else 'no'))
    print('what follows: SUPPORTED -> the default goes to the operator; FALSIFIED or MIXED -> back to the lab (sdlports), no default question')


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'cell':
        print(line(cell(sys.argv[2], sys.argv[3])))
    elif len(sys.argv) >= 3 and sys.argv[1] == 'verdict':
        verdict(sys.argv[2:])
    else:
        sys.exit(__doc__)
