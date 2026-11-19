#!/usr/bin/env python3
"""LAB-R2B: the split of a drawn tick over a loop-tick window (LAB-R2's T-cell shape), from a DOSAGS_LAB_TK=1 cell's TICKS.BIN.

    r2bsplit.py CELL_DIR [CELL_DIR...] [--lo 5480] [--hi 7889]

busy = ugo - wait; logic = busy - scene - render (LAB-R2 r2split.py's definitions). prep = sc_prep_chars, cblit = character
composites per pass (every character entry, R2b's per-box rects included), bg = the room restore, rbspr = rb_sprite_time.
Character work here = prep + cblit + bg x (LAB-R2 L4's measured share of restored px inside character rects, 0.957, for
mode 0; for mode 2 the restore is reported whole, as R2b removes the kids' rects from it). Drawn ticks; steady = ugo < 40 ms.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ticks import load, med, pct
a = sys.argv[1:]
lo = int(a[a.index('--lo') + 1]) if '--lo' in a else 5480
hi = int(a[a.index('--hi') + 1]) if '--hi' in a else 7889
cells = [x for i, x in enumerate(a) if not x.startswith('--') and (i == 0 or a[i - 1] not in ('--lo', '--hi'))]
K = ('ugo', 'wait', 'busy', 'logic', 'scene', 'render', 'prep', 'cblit', 'bg', 'rbspr', 'cpx')
for d in cells:
    T = load(os.path.join(d, 'TICKS.BIN'))
    W = [t for t in T['ticks'] if lo <= t['lc'] <= hi]
    dr = [t for t in W if t['drawn']]
    st = [t for t in dr if t['ugo'] < 40000]
    print('== %s window %d..%d: ticks %d, drawn %d, skipped %d, spike ticks %d, ticklog dropped %d, clamped %d' % (
        d, lo, hi, len(W), len(dr), len(W) - len(dr), sum(1 for t in W if t['ugo'] >= 40000), T['dropped'], len(T['bad'])))
    for name, S in (('drawn', dr), ('steady', st)):
        rows = []
        for t in S:
            wait = t.get('wait', 0); busy = t['ugo'] - wait
            r = t.get('render', 0); s = t.get('scene', 0)
            rows.append(dict(ugo=t['ugo'], wait=wait, busy=busy, logic=busy - r - s, scene=s, render=r, prep=t.get('prep', 0),
                             cblit=t.get('cblit', 0), bg=t.get('bg', 0), rbspr=t.get('rbspr', 0), cpx=t.get('cpx', 0)))
        if not rows: continue
        mb = sum(x['busy'] for x in rows) / len(rows)
        print('-- %s n=%d (ms except cpx; share = mean / mean busy)' % (name, len(rows)))
        print('   %-7s %8s %8s %8s %7s' % ('', 'mean', 'median', 'p95', 'share'))
        for k in K:
            xs = [x[k] for x in rows]; m = sum(xs) / len(xs)
            f = 1.0 if k == 'cpx' else 1000.0
            print('   %-7s %8.3f %8.3f %8.3f %6.1f%%' % (k, m / f, med(xs) / f, pct(xs, 0.95) / f, 100.0 * m / mb if k != 'cpx' else float('nan')))
