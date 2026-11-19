#!/usr/bin/env python3
"""Per-click logic (ugo - scene - render) from TICKS.BIN, and the tick rows around a click (docs/lab/rb-lab/ticks.py's reader)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../docs/lab/rb-lab'))
from ticks import load
for d in sys.argv[1:]:
    T = load(os.path.join(d, 'TICKS.BIN'))
    print('==', os.path.basename(d.rstrip('/')), 'rooms', T['rooms'][:4])
    for t in T['ticks']:
        if t.get('click') and t['lc'] >= 5436:
            u = t['ugo'] / 1e3; sc = t.get('scene', 0) / 1e3; rn = t.get('render', 0) / 1e3
            print('  click lc=%d ugo=%.1f scene=%.1f render=%.1f logic=%.1f' % (t['lc'], u, sc, rn, u - sc - rn))
    for c in [t['lc'] for t in T['ticks'] if t.get('click') and t['lc'] >= 5436][:1] + [t['lc'] for t in T['ticks'] if t.get('click') and t['lc'] > T['rooms'][1][0]][:1]:
        print('  rows %d..%d (lc%%1000, D drawn / s skipped, ugo/scene ms):' % (c - 1, c + 25))
        print('   ', ' '.join('%d%s%.0f/%.0f' % (t['lc'] % 1000, 'D' if t['drawn'] else 's', t['ugo'] / 1e3, t.get('scene', 0) / 1e3)
                             for t in T['ticks'] if c - 1 <= t['lc'] <= c + 25))
