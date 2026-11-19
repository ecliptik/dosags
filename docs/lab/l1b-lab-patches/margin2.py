#!/usr/bin/env python3
"""LAB-L1B margin model, v2. GCMP TICKS.BIN (486, R1 on, instrumented, fine timing on), room-2 early stretch
loop ticks 8000..8689: render ~2.35 ms on drawn ticks there, the regime R3 brings to the whole room (LAB-R3).
Every tick's logic is shifted by one constant so the mean drawn tick is 24.1 ms (coordinator: 17.4 + 2.7 + 4.0 after
R1 + R3 central). A lever's 486 saving s comes off every tick's logic (LAB-L1: the per-tick script is fixed per tick).
Prints the drawn-tick mean / p95 / share over 25 ms, and a lag simulation of displayed frames (information only):
the loop owes L ms; a tick draws if L <= 25 (else skips render+scene); L += cost - 25, floored at 0.
margin2.py GCMP_DIR [lo hi]"""
import struct, sys, os, statistics
d = sys.argv[1]; lo = int(sys.argv[2]) if len(sys.argv) > 2 else 8000; hi = int(sys.argv[3]) if len(sys.argv) > 3 else 8689
b = open(os.path.join(d, 'TICKS.BIN'), 'rb').read()
magic, ver, n, dropped, cap = struct.unpack('<5I', b[:20]); r = struct.unpack('<%dI' % (2 * n), b[20:20 + 8 * n])
# Grouped by TICK (2026-11-06 fix): a tick's update_game_once close is stamped lc+1 (patch 0316), so records up to
# and including each kind-1 record form tick lc-1. The first version keyed by raw lc (the f1prof off-by-one).
per = {}
cur = [0, 0, 0]
for i in range(n):
    lc, k, v = r[2 * i], r[2 * i + 1] >> 28, r[2 * i + 1] & 0x0FFFFFFF
    if k == 1:
        cur[0] += v; per[lc - 1] = cur; cur = [0, 0, 0]
    elif k in (2, 3):
        cur[k - 1] += v
T = [lc for lc in sorted(per) if lo <= lc <= hi]
D = [lc for lc in T if per[lc][1] > 0]
comp = {lc: ((per[lc][0] - per[lc][1] - per[lc][2]) / 1000.0, per[lc][1] / 1000.0, per[lc][2] / 1000.0) for lc in T}
def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))]
mean_drawn = statistics.mean(sum(comp[lc]) for lc in D)
rs = statistics.mean(comp[lc][1] for lc in D); ss = statistics.mean(comp[lc][2] for lc in D)
sh = 24.1 - mean_drawn
print('window %d..%d: %d ticks, %d drawn (%.1f%%); drawn means logic %.2f render %.2f scene %.2f ugo %.2f; shift logic %+.2f' % (
    lo, hi, len(T), len(D), 100.0 * len(D) / len(T), statistics.mean(comp[lc][0] for lc in D), rs, ss, mean_drawn, sh))
pass_ms = rs + ss
print('%-10s %9s %9s %9s %9s %11s' % ('s (ms)', 'mean', 'p50', 'p95', '>25 ms', 'sim displ.'))
for s in [float(x) for x in (sys.argv[4].split(",") if len(sys.argv) > 4 else "0,0.04,0.07,0.09,0.25,0.34,0.40,0.48,0.55,0.65,0.8,1.0".split(","))]:
    V = [comp[lc][0] + sh - s + comp[lc][1] + comp[lc][2] for lc in D]
    # lag simulation over all ticks of the window: a drawn tick costs logic + pass (its own when it drew, else the mean)
    L = 0.0; drawn = 0
    for lc in T:
        lg = comp[lc][0] + sh - s if per[lc][1] > 0 else comp[lc][0] + sh - s  # logic of the tick
        if per[lc][1] == 0:
            lg = statistics.mean([comp[x][0] for x in D]) + sh - s  # an undrawn GCMP tick's 'logic' holds its wait: use the drawn mean
        draw = L <= 25.0
        c = lg + ((comp[lc][1] + comp[lc][2]) if per[lc][1] > 0 else pass_ms) if draw else lg
        drawn += draw
        L = max(0.0, L + c - 25.0)
    print('%-10.2f %9.2f %9.2f %9.2f %8.1f%% %10.1f%%' % (s, statistics.mean(V), statistics.median(V), pct(V, 0.95),
          100.0 * sum(1 for v in V if v > 25) / len(V), 100.0 * drawn / len(T)))
