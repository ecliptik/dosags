#!/usr/bin/env python3
"""rq-steps.py -- round RQ's readings (the heap lock-policy ABBA on MS3; ags 0380). Read-only.

  rq-steps.py cell CELL_DIR ARM                    one STEPS line for a cell (ARM = O | U | P)
  rq-steps.py verdict CELL_DIR:ARM [CELL_DIR:ARM...] the round's terms over the given cells

Definitions (presses and journeys 1-based, as tests/harness/ms3-pairing.py; offset = press down_at (wall ms) minus
journey t_ms (game ms)):
  pre  = median offset of presses 6-15 (room 1, before the room-2 load)
  S17  = offset(17) - pre      the press-17 step: wall time the game clock lost across the room-2 load
  S18  = offset(18) - offset(17)  the press-18 step: the 192-page commit at room-2 entry +43..+81 ticks
  L2   = room-2 load_end - load_begin t_ms (STDOUT DOSAGS_XT, game ms): the load as the game clock counted it
  W17  = L2 + S17              the room-2 entry's wall cost (counted + lost). Motivation (RO / RN records, before RQ):
                               S17 is bimodal (+194..+386) but trades against L2 (1,713..1,876): W17 = 2,070..2,122 ms.
  j1   = journey 1's t_ms: game ms at press 1, which is wall-timed from the lock; a clock-stopped stall before press 1
         (PREGROW's commit at the hook) shows as fewer game ms than the O cells'. Information.
Arm witness (RUNMANI.LOG "DOS-PORT heappolicy_exit"): O = unlock=0 pregrow_kb=0 flags kept 0x1080->0x1080;
  U = unlock=1 pregrow_kb=0 flags 0x1080->0x80; P = unlock=0 pregrow_kb=6144 grown=1 flags kept.
Cell VALID = arm witness as its ARM, RUNMANIFEST exit_code=0 and "ENGINE HAS SHUTDOWN", the pairing reads PAIR-OK or
  PAIR-OK-114LATE (ms3-pairing.py check()), audio underruns = overwrites = 0, and the room-2 load lines present.
P cover: heappolicy_exit free_pages within 16 pages of free_at_hook's post value (6,144 KB covered MS3's growth after
  the hook). A P cell outside that reads "pre-grow exceeded": information, not a P reading (it does not count as P).
(d) pageability (U cells): heappolicy_exit free_pages >= 512, else PAGEABILITY FALSIFIED. Information beside it: the
  largest sustained +offset shift (5-press medians) over presses 23-108 outside the registered room-2 stay brackets
  (33-36, 52-54, 90-95), every cell; and ROOTPRE.TXT / ROOTPOST.TXT's CWSDPMI.SWP line (CWSDPMI deletes its swap file
  when it exits -- round RM: none at rest -- so the post-run DIR is expected to show none in every arm).

Verdict terms (resolution +-30 ms). OFF baseline B = the valid in-round O cells, if both are valid; if exactly one O
cell is valid, B = that cell plus the four RO / RN fixed cells (ROF1, ROF2, RNF1, RNF2, read from their committed
records by this script); if no O cell is valid, the S18 and W17 terms are NOT READ.
  S18, per arm X in {U, P}: SUPPORTED if X has >= 2 valid cells, each S18 <= 60, and every B cell's S18 >= 120;
       FALSIFIED if any valid X cell's S18 >= 120; else INCONCLUSIVE (NOT READ with < 2 valid X cells).
  W17, PREGROW: SUPPORTED if >= 2 valid P cells (cover ok), each W17 < min(B W17) - 60; FALSIFIED if any such cell's
       W17 >= min(B W17) - 30; else INCONCLUSIVE.
  W17 / S17 / L2 for UNLOCK: information (prediction: S17 down, L2 up, W17 within +-60 of B's median).
  UNLOCK FAILED: a U cell without a clean exit, or a STOP in a U cell attributed to the game (the README's attribution
       rule: a STOP outside AGS with its clean shutdown on record is a rig STOP) -- the ISR audit was static only. Read by
       the driver and the README, not here.
"""
import os
import re
import statistics as st
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location('ms3pairing', os.path.join(HERE, 'ms3-pairing.py'))
mp = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(mp)
BASE = ['ROF1-2026-11-12', 'ROF2-2026-11-12', 'RNF1-2026-11-12', 'RNF2-2026-11-12']
BR = ((33, 36), (52, 54), (90, 95))


def rd(p):
    try:
        return open(p, errors='replace').read()
    except OSError:
        return ''


def readings(c):
    js, dn, ps, _ = mp.load(c)
    ts = [t for _, t in js]
    n = min(len(ts), len(dn))
    off = [dn[i] - ts[i] for i in range(n)]
    pre = st.median(off[5:15])
    so = rd(c + '/STDOUT.TXT')
    lb = re.search(r'DOSAGS_XT t_ms=(\d+) phase=load_begin room=2\b', so)
    le = re.search(r'DOSAGS_XT t_ms=(\d+) phase=load_end room=2\b', so)
    L2 = int(le.group(1)) - int(lb.group(1)) if lb and le else None
    S17, S18 = off[16] - pre, off[17] - off[16]

    def inb(q):
        return any(q - 5 <= b and q + 4 >= a + 1 for a, b in BR)
    m = min(n, 109)
    sp = max((mp.sustained(off, q), q) for q in range(23, m) if not inb(q)) if m > 28 else (None, None)
    return dict(pre=pre, S17=S17, S18=S18, L2=L2, W17=(L2 + S17) if L2 is not None else None, j1=ts[0] if ts else None,
                shift=sp)


def heap(c):
    m = re.search(r'DOS-PORT heappolicy_exit unlock=(\d+) pregrow_kb=(\d+) grown=(\d+) crt0_flags=(0x[0-9a-f]+)->'
                  r'(0x[0-9a-f]+) free_at_hook=(\d+)->(\d+) hook_us=(-?\d+) free_pages=(\d+) phys_pages=(\d+)',
                  rd(c + '/RUNMANI.LOG'))
    if not m:
        return None
    k = ('unlock', 'kb', 'grown', 'f0', 'f1', 'h0', 'h1', 'us', 'free', 'phys')
    return dict(zip(k, [int(v, 0) for v in m.groups()]))


def arm_ok(h, arm):
    if not h:
        return False
    if arm == 'O':
        return h['unlock'] == 0 and h['kb'] == 0 and h['f0'] == h['f1'] == 0x1080
    if arm == 'U':
        return h['unlock'] == 1 and h['kb'] == 0 and h['f0'] == 0x1080 and h['f1'] == 0x80
    if arm == 'P':
        return h['unlock'] == 0 and h['kb'] == 6144 and h['grown'] == 1 and h['f0'] == h['f1'] == 0x1080
    return False


def swp(c, f):
    t = rd(os.path.join(c, f))
    if not t:
        return 'NA'
    m = re.search(r'^CWSDPMI\s+SWP\s+([\d,]+)', t, re.M | re.I)
    return m.group(1).replace(',', '') if m else 'none'


def cell(c, arm):
    rm, so = rd(c + '/RUNMANI.LOG'), rd(c + '/STDOUT.TXT')
    why = []
    h = heap(c)
    if not arm_ok(h, arm):
        why.append('arm witness')
    ec = re.search(r'^exit_code=(\d+)', rm, re.M)
    if not (ec and ec.group(1) == '0' and 'ENGINE HAS SHUTDOWN' in so):
        why.append('no clean exit')
    try:
        pv = mp.check(c)[0]
    except Exception:
        pv = 'PAIR-VOID'
    if pv not in ('PAIR-OK', 'PAIR-OK-114LATE'):
        why.append(pv)
    ur = re.search(r'underruns=(\d+)', rm)
    ow = re.search(r'overwrites=(\d+)', rm)
    if not (ur and ow and ur.group(1) == '0' and ow.group(1) == '0'):
        why.append('audio')
    try:
        r = readings(c)
    except Exception as e:
        r = None
        why.append('readings (%s)' % type(e).__name__)
    if r and r['L2'] is None:
        why.append('no room-2 load lines')
    cover = None
    if arm == 'P' and h:
        cover = abs(h['free'] - h['h1']) <= 16
    pg = None
    if arm == 'U' and h:
        pg = h['free'] >= 512
    return dict(c=c, arm=arm, valid=not why, why=why, h=h, r=r, pair=pv, cover=cover, pg=pg,
                swp=(swp(c, 'ROOTPRE.TXT'), swp(c, 'ROOTPOST.TXT')))


def line(x):
    r, h = x['r'] or {}, x['h'] or {}
    f = lambda v: 'NA' if v is None else '%+.0f' % v
    return ('STEPS %s arm=%s valid=%s%s pair=%s pre=%s S17=%s S18=%s L2=%s W17=%s j1=%s | heap unlock=%s kb=%s flags=%s->%s '
            'hook %s->%s us=%s exit_free=%s phys=%s%s%s | max+shift outside steps %s at %s | SWP pre=%s post=%s') % (
        os.path.basename(x['c'].rstrip('/')), x['arm'], 'yes' if x['valid'] else 'no', '' if x['valid'] else ' (' + '; '.join(x['why']) + ')',
        x['pair'], f(r.get('pre')) if r.get('pre') is None else '%.0f' % r['pre'], f(r.get('S17')), f(r.get('S18')),
        r.get('L2'), f(r.get('W17')), r.get('j1'), h.get('unlock'), h.get('kb'),
        hex(h['f0']) if h else None, hex(h['f1']) if h else None, h.get('h0'), h.get('h1'), h.get('us'), h.get('free'),
        h.get('phys'), '' if x['cover'] is None else ' cover=%s' % ('ok' if x['cover'] else 'PRE-GROW EXCEEDED'),
        '' if x['pg'] is None else ' pageability=%s' % ('ok' if x['pg'] else 'FALSIFIED (free < 512)'),
        f((r.get('shift') or (None, None))[0]), (r.get('shift') or (None, None))[1], x['swp'][0], x['swp'][1])


def verdict(args):
    res = RES = os.path.join(HERE, 'results')
    cells = [cell(a.rsplit(':', 1)[0], a.rsplit(':', 1)[1]) for a in args]
    for x in cells:
        print(line(x))
    O = [x for x in cells if x['arm'] == 'O' and x['valid']]
    nO = len([x for x in cells if x['arm'] == 'O'])
    if len(O) >= 2:
        B, src = [x['r'] for x in O], 'in-round O x%d' % len(O)
    elif len(O) == 1:
        B = [O[0]['r']] + [readings(os.path.join(RES, b)) for b in BASE]
        src = 'O1-only fallback: %s + %s' % (os.path.basename(O[0]['c']), ' '.join(BASE))
    else:
        print('BASELINE none (no valid O cell of %d): S18 and W17 terms NOT READ' % nO)
        B = None
    if B is not None:
        print('BASELINE %s | S18 %s | W17 %s | min W17 %.0f' % (
            src, ' '.join('%+.0f' % b['S18'] for b in B), ' '.join('%.0f' % b['W17'] for b in B), min(b['W17'] for b in B)))
    for X, name in (('U', 'UNLOCK'), ('P', 'PREGROW')):
        xs = [x for x in cells if x['arm'] == X and x['valid'] and (X != 'P' or x['cover'])]
        if B is None:
            print('TERM S18 %s NOT READ (no baseline)' % name)
        elif len(xs) < 2:
            print('TERM S18 %s NOT READ (%d valid cells)' % (name, len(xs)))
        elif any(x['r']['S18'] >= 120 for x in xs):
            print('TERM S18 %s FALSIFIED (%s)' % (name, ' '.join('%+.0f' % x['r']['S18'] for x in xs)))
        elif all(x['r']['S18'] <= 60 for x in xs) and all(b['S18'] >= 120 for b in B):
            print('TERM S18 %s SUPPORTED (%s vs baseline >= 120)' % (name, ' '.join('%+.0f' % x['r']['S18'] for x in xs)))
        else:
            print('TERM S18 %s INCONCLUSIVE (%s)' % (name, ' '.join('%+.0f' % x['r']['S18'] for x in xs)))
        if X == 'P':
            if B is None:
                print('TERM W17 PREGROW NOT READ (no baseline)')
            elif len(xs) < 2:
                print('TERM W17 PREGROW NOT READ (%d valid covered P cells)' % len(xs))
            else:
                mn = min(b['W17'] for b in B)
                w = ' '.join('%.0f' % x['r']['W17'] for x in xs)
                if any(x['r']['W17'] >= mn - 30 for x in xs):
                    print('TERM W17 PREGROW FALSIFIED (%s vs min baseline %.0f)' % (w, mn))
                elif all(x['r']['W17'] < mn - 60 for x in xs):
                    print('TERM W17 PREGROW SUPPORTED (%s < %.0f - 60)' % (w, mn))
                else:
                    print('TERM W17 PREGROW INCONCLUSIVE (%s vs min baseline %.0f)' % (w, mn))
    U = [x for x in cells if x['arm'] == 'U' and x['h']]
    if U:
        print('TERM (d) PAGEABILITY %s (U exit free pages %s)' % (
            'FALSIFIED' if any(not x['pg'] for x in U) else 'not falsified', ' '.join(str(x['h']['free']) for x in U)))


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'cell':
        print(line(cell(sys.argv[2], sys.argv[3])))
    elif len(sys.argv) >= 3 and sys.argv[1] == 'verdict':
        verdict(sys.argv[2:])
    else:
        print(__doc__)
        sys.exit(2)
