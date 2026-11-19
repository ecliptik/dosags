#!/usr/bin/env python3
"""rs-pacesim.py -- MODEL ONLY: pacesim.py over round RS's measured 486 per-tick logs (RSI1, RSI2; the 0383
instrumented flavour), mapped to the release level by the model's two mappings (logic offset -1.70 ms, floor at
half; or logic and draw x 0.937), under the shipped pacer and the forgive=T rule. Information for PREREG-PACEAB."""
import sys, os
sys.path.insert(0, '/home/claude/data/worktrees/dosags-lab-rb/docs/lab/pace-lab')
import pacesim as P
from ticks import load
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
POLS = ['base', 'forgive=75', 'forgive=60', 'forgive=55', 'forgive=50', 'forgive=45', 'forgive=40', 'maxc=0']
def mapped(costs, how):
    tk, lg, dr, st, fx = costs
    if how == 'none': return costs
    if how == 'offset': lg = [max(0.5 * x, x - 1.70) for x in lg]
    else: lg = [x * 0.937 for x in lg]; dr = [x * 0.937 for x in dr]
    return (tk, lg, dr, st, fx)
for c in ('RSI1', 'RSI2'):
    T = load(os.path.join(R, c + '-2026-11-19', 'TICKS.BIN'))
    base = P.build_costs(T, 5450)
    for how in ('none', 'offset', 'scale'):
        co = mapped(base, how)
        for pol in POLS:
            r = P.simulate(co, pol)
            print('%s %-6s %-11s skipped %4d displayed %6.2f%% rebases %3d lost_total %6.0f ms beyond_stalls %6.0f ms (%.2f%% of %.0f s wall) biggest slip %3.0f' % (
                c, how, pol, r['skipped'], r['displayed'], r['rebases'], r['lost_total_ms'], r['lost_beyond_stalls_ms'],
                100 * r['lost_beyond_stalls_ms'] / r['wall_ms'], r['wall_ms'] / 1000, r['biggest_slip_ms']))
