#!/usr/bin/env python3
"""pa-fixture-sim.py -- round RT's fixture under the predicted outcome (sdlports' point c; round RN's lesson). Read-only
on existing round RS / RR records; MODEL ONLY, no new data.
MS3's 114 presses are wall-timed (DRIVE-WALK down_at, host clock); the run ends at loop tick 12440 (TAS exit); the
journeys' t_ms and the persec ms= are the engine's wall clock (uclock since start). A pacer that forgives debt makes the
same 7,003 ticks take more wall time (game time lost = the stretch). This reads, per release A cell:
  (1) press 114 against the loop end: the A cell's own margin (press 114's game ms - last persec ms), then with the loop
      stretched by g of the loop's wall span (g = 0, 1.0, 1.5, 2.0, 3.0%): the loop ends g x loop_ms later, the press does
      not move. A margin < 0 = press 114 inside the loop (PAIR-OK); > 0 = after it (only PAIR-OK-114LATE could pair it).
  (2) the room change: press 17 is the first room-2 press. From the instrumented cells' TICKS.BIN (RSI1, RSI2; the only
      per-tick 486 records), the wall time from the room-2 marker tick's end to click 17, and the debt a forgive=T rule
      could add between press 16 and room 2's first tick: the sum of (tick - 25 ms) over the ticks in [click 16, room-2
      marker) whose own time is over T, at the release level (both mappings). Press 17 lands in a different room state
      only if that added lag exceeds the margin.
  (3) any other room change: the rooms each cell visited (STDOUT "Now in room").
Usage: pa-fixture-sim.py RESULTS_DIR"""
import importlib.util, os, re, sys
R = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('ro', os.path.join(HERE, 'rs-owed.py')); ro = importlib.util.module_from_spec(sp); sp.loader.exec_module(ro)
A = ['RSA1-2026-11-19', 'RSA2-2026-11-19', 'RSA3-2026-11-19', 'RRF1-2026-11-17', 'RRF2-2026-11-17', 'RRF3-2026-11-17']
I = ['RSI1-2026-11-19', 'RSI2-2026-11-19']
G = [0.0, 1.0, 1.5, 2.0, 3.0]
print('## (1) press 114 against the loop end, loop stretched by g (A cells, release)')
print('| cell | loop_ms | press 114 game ms | last persec ms | margin now, ms | margin at g = ' + ' / '.join('%.1f%%' % g for g in G) + ' |')
print('|---|---|---|---|---|---|')
for c in A:
    rm = open(os.path.join(R, c, 'RUNMANI.LOG'), errors='replace').read()
    js = [int(t) for t in re.findall(r'journey kind=click room=\d+ t_ms=(\d+)', rm)]
    ps = [(int(a), int(b)) for a, b in re.findall(r'persec t=\d+ tick=(\d+) renders=\d+ real=\d+ skipped=\d+ ms=(\d+)', rm)]
    lm = int(re.search(r'loop_ms=(\d+)', rm).group(1))
    p114, last = js[113], ps[-1][1]
    m = p114 - last
    print('| %s | %d | %d | %d | %+d | %s |' % (c, lm, p114, last, m, ' / '.join('%+d' % (m - g / 100.0 * lm) for g in G)))
print('\n## (2) the room change (instrumented 486 cells; the release is faster, so its margin is the larger one)')
for c in I:
    T = ro.load_ticks(os.path.join(R, c, 'TICKS.BIN'))['ticks']; by = {t['lc']: t for t in T}
    cl = [t['lc'] for t in T if t.get('click')]
    r2 = [t['lc'] for t in T if t.get('room') == 2][0]
    c16, c17 = cl[15], cl[16]
    wall = lambda a, b: sum(by[l]['ugo'] for l in range(a, b) if l in by) / 1000.0
    marg = wall(r2 + 1, c17)
    out = []
    for nm, f in (('offset', lambda x: x - 1.70), ('scale', lambda x: x * 0.937)):
        for Tm in (45, 50):
            add = sum(max(0.0, f(by[l]['ugo'] / 1000.0) - 25.0) for l in range(c16, r2) if l in by and f(by[l]['ugo'] / 1000.0) > Tm)
            out.append('%s T=%d: +%.0f ms' % (nm, Tm, add))
    print('- %s: click 16 at tick %d, room-2 marker %d (load tick %.0f ms), click 17 at %d; room 2 ready -> click 17: %.0f ms; '
          'lag a forgive rule could add before room 2: %s' % (c, c16, r2, by[r2]['ugo'] / 1000.0, c17, marg, '; '.join(out)))
print('\n## (3) rooms visited')
for c in A + I:
    so = open(os.path.join(R, c, 'STDOUT.TXT'), errors='replace').read()
    print('- %s: %s' % (c, ', '.join(sorted(set(re.findall(r'Now in room (\d+)', so))))))
