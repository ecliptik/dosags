#!/usr/bin/env python3
"""LAB-R2 Q1: the split of a drawn tick over a loop-tick window, from a timing cell's TICKS.BIN (lab kinds 7-14).

    r2split.py CELL_DIR [--lo 5480] [--hi 7889] [--detail DETAIL_CELL_DIR]

busy = ugo - wait (the frame wait is idle time, not work). logic = busy - scene - render. scene and render are the
coarse scopes (bg_restore and sc_prep_chars sit inside scene; character blits and rb_sprite_time inside render).
Character work = sc_prep_chars + character blits + character share of bg_restore, where that share is the detail
cell's per-tick (restore px inside character rects / restore px) on the same tick (the fixture is deterministic), or
its window mean if the tick is missing there. Drawn ticks only; "steady" also drops ticks with ugo >= 40 ms.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ticks import load, med, pct


def main():
    a = sys.argv[1:]
    d = a[0]
    lo = int(a[a.index('--lo') + 1]) if '--lo' in a else 5480
    hi = int(a[a.index('--hi') + 1]) if '--hi' in a else 7889
    det = a[a.index('--detail') + 1] if '--detail' in a else None
    T = load(os.path.join(d, 'TICKS.BIN'))
    ratio, rmean = {}, None
    if det:
        D = load(os.path.join(det, 'TICKS.BIN'))
        for t in D['ticks']:
            if t.get('bgall'):
                ratio[t['lc']] = t.get('bgchar', 0) / t['bgall']
        w = [t for t in D['ticks'] if lo <= t['lc'] <= hi and t.get('bgall')]
        rmean = sum(t.get('bgchar', 0) for t in w) / max(1, sum(t['bgall'] for t in w))
        pxa = [t['bgall'] for t in w]; pxc = [t.get('bgchar', 0) for t in w]
        print('detail %s: window restores %d, restore px/tick mean %.0f median %.0f; in character rects mean %.0f median %.0f;'
              ' px share %.3f' % (det, len(w), sum(pxa) / max(1, len(w)), med(pxa), sum(pxc) / max(1, len(w)), med(pxc), rmean))
    if T['bad']:
        print('clamped negative lab records (counted 0): %s' % T['bad'])
    W = [t for t in T['ticks'] if lo <= t['lc'] <= hi]
    dr = [t for t in W if t['drawn']]
    st = [t for t in dr if t['ugo'] < 40000]
    print('== %s window %d..%d: ticks %d, drawn %d, skipped %d, spike ticks (ugo >= 40 ms) %d; ticklog dropped %d' % (
        d, lo, hi, len(W), len(dr), len(W) - len(dr), sum(1 for t in W if t['ugo'] >= 40000), T['dropped']))
    for name, S in (('drawn', dr), ('steady drawn', st)):
        rows = []
        for t in S:
            wait = t.get('wait', 0); busy = t['ugo'] - wait
            r = t.get('render', 0); s = t.get('scene', 0)
            bg = t.get('bg', 0)
            share = ratio.get(t['lc'], rmean if rmean is not None else float('nan'))
            cbg = bg * share
            ch = t.get('prep', 0) + t.get('cblit', 0) + cbg
            rows.append(dict(ugo=t['ugo'], wait=wait, busy=busy, logic=busy - r - s, scene=s, render=r, prep=t.get('prep', 0),
                             cblit=t.get('cblit', 0), bg=bg, cbg=cbg, char=ch, rbspr=t.get('rbspr', 0), cpx=t.get('cpx', 0)))
        if not rows:
            continue
        print('-- %s ticks: %d (ms; shares of busy = ugo - wait; mean shares sum to 100%%)' % (name, len(rows)))
        mb = sum(x['busy'] for x in rows) / len(rows)
        mdb = med([x['busy'] for x in rows])
        print('   %-8s %8s %8s %8s %8s %9s %9s' % ('', 'mean', 'median', 'p95', 'max', 'mean-shr', 'med/medb'))
        for k in ('ugo', 'wait', 'busy', 'logic', 'scene', 'render', 'prep', 'cblit', 'bg', 'cbg', 'char', 'rbspr', 'cpx'):
            xs = [x[k] for x in rows]
            m = sum(xs) / len(xs)
            div = 1.0 if k == 'cpx' else 1000.0
            print('   %-8s %8.3f %8.3f %8.3f %8.3f %8.1f%% %8.1f%%' % (k, m / div, med(xs) / div, pct(xs, 0.95) / div, max(xs) / div,
                  100.0 * m / mb if k not in ('cpx', 'ugo', 'wait') else float('nan'),
                  100.0 * med(xs) / mdb if k not in ('cpx', 'ugo', 'wait') else float('nan')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
