#!/usr/bin/env python3
"""LAB-R2B: skipped ticks per R2-FORECAST window from a TICKLOG cell's TICKS.BIN (a tick with no render record is skipped).
    winskips.py CELL_DIR...   windows: restore 5437-5441, room 1 5480-7889, entry 7890-8399, room 2 8400-9499, late 9500-end"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ticks import load
WIN = (('restore 5437-5441', 5437, 5441), ('room1 5480-7889', 5480, 7889), ('entry 7890-8399', 7890, 8399),
       ('room2 8400-9499', 8400, 9499), ('late 9500-end', 9500, 10**9), ('all', 0, 10**9))
for d in sys.argv[1:]:
    T = load(os.path.join(d, 'TICKS.BIN'))
    out = []
    for nm, lo, hi in WIN:
        W = [t for t in T['ticks'] if lo <= t['lc'] <= hi]
        sk = [t['lc'] for t in W if not t['drawn']]
        out.append('%s: %d/%d skipped%s' % (nm, len(sk), len(W), (' ' + ','.join(str(x) for x in sk[:30])) if sk and nm != 'all' else ''))
    print('== %s (dropped %d)\n   ' % (d, T['dropped']) + '\n   '.join(out))
