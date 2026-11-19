#!/usr/bin/env python3
"""LAB-L1B margin model from GCMP's TICKS.BIN (486, R1 on, instrumented, fine timing on).
Drawn tick = a room-2 loop tick with a render record (render > 0). Each component is shifted by a constant so its mean over
drawn ticks equals the coordinator's post-R1+R3 central (logic 17.4, render 2.7, scene 4.0 ms); a lever's saving s is then
taken off logic on every tick (the per-tick script cost is fixed per tick, LAB-L1 P1/P2).
margin.py GCMP_DIR [lo hi]"""
import struct, sys, os, statistics
d = sys.argv[1]
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 7940
hi = int(sys.argv[3]) if len(sys.argv) > 3 else 12439
b = open(os.path.join(d, 'TICKS.BIN'), 'rb').read()
magic, ver, n, dropped, cap = struct.unpack('<5I', b[:20])
r = struct.unpack('<%dI' % (2 * n), b[20:20 + 8 * n])
per = {}
kinds = {}
cur = [0, 0, 0]
for i in range(n):
    lc, k, v = r[2 * i], r[2 * i + 1] >> 28, r[2 * i + 1] & 0x0FFFFFFF
    kinds[k] = kinds.get(k, 0) + 1
    # Grouped by TICK (2026-11-06 fix): the update_game_once close is stamped lc+1 (patch 0316); the first
    # version keyed by raw lc (the f1prof off-by-one). Superseded by margin2.py, kept for the record.
    if k == 1:
        cur[0] += v; per[lc - 1] = cur; cur = [0, 0, 0]
    elif k in (2, 3):
        cur[k - 1] += v
ticks = [lc for lc in sorted(per) if lo <= lc <= hi]
drawn = [lc for lc in ticks if per[lc][1] > 0]
def comp(lc):
    u, rr, s = (x / 1000.0 for x in per[lc])
    return u - rr - s, rr, s
L = [comp(lc) for lc in drawn]
def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))]
print('kinds %s; window %d..%d: %d ticks, %d drawn (%.1f%%)' % (kinds, lo, hi, len(ticks), len(drawn), 100.0 * len(drawn) / len(ticks)))
for nm, i in (('logic', 0), ('render', 1), ('scene', 2)):
    xs = [x[i] for x in L]
    print('  drawn %-6s mean %6.2f median %6.2f p95 %6.2f' % (nm, statistics.mean(xs), statistics.median(xs), pct(xs, 0.95)))
U = [sum(x) for x in L]
print('  drawn ugo    mean %6.2f median %6.2f p95 %6.2f  >25ms %.1f%%' % (statistics.mean(U), statistics.median(U), pct(U, 0.95),
      100.0 * sum(1 for u in U if u > 25) / len(U)))
tgt = (17.4, 2.7, 4.0)
sh = [tgt[i] - statistics.mean([x[i] for x in L]) for i in range(3)]
print('shifts to the post-R1+R3 central: logic %+.2f render %+.2f scene %+.2f' % tuple(sh))
allL = [comp(lc)[0] + sh[0] for lc in ticks]
print('  all-tick logic (shifted) mean %.2f p50 %.2f p95 %.2f; ticks with logic > 25 - 6.7: %.1f%%' % (
    statistics.mean(allL), statistics.median(allL), pct(allL, 0.95), 100.0 * sum(1 for x in allL if x > 18.3) / len(allL)))
print('%-26s %8s %8s %8s %9s %9s' % ('saving s (ms/tick, 486)', 'mean', 'p50', 'p95', '>25 ms', 'logic>18.3'))
for s in [0, 0.1, 0.2, 0.3, 0.45, 0.65, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0, 4.0]:
    V = [x[0] + sh[0] - s + x[1] + sh[1] + x[2] + sh[2] for x in L]
    A = [comp(lc)[0] + sh[0] - s for lc in ticks]
    print('%-26.2f %8.2f %8.2f %8.2f %8.1f%% %8.1f%%' % (s, statistics.mean(V), statistics.median(V), pct(V, 0.95),
          100.0 * sum(1 for v in V if v > 25) / len(V), 100.0 * sum(1 for a in A if a > 18.3) / len(A)))
