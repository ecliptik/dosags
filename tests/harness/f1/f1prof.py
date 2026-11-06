#!/usr/bin/env python3
"""f1prof.py -- F1 per-phase table for one cell (committed for PLAN-FPS F1, 2026-11-05, before any F1 data).

    f1prof.py CELL_DIR [--lo LOOP_TICK] [--hi LOOP_TICK]

Reads CELL_DIR/{*.LOG (RUNMANI), STDOUT.TXT, TICKS.BIN}. Prints:
  1. the rate fields (tick_rate / frames_skipped, tick_rate_steady / ticks / stall, fps_p50, fps_basis);
  2. every `DOS-PORT tickstats_<phase> calls= total_us=` line as ms per call and ms per game tick
     (game ticks = tick_rate_steady's ticks=), whole run. Coarse scopes (always on, both flavours that keep
     timers): update_game_once_total, render_to_screen, scene_construct; logic = ugo - render - scene.
     Fine scopes (DOSAGS_TICKSTATS_FINE=1) add script_vm, rep_exec_*, process_events_dispatch, present_*, sc_*, ...
     Nested scopes overlap: the table is NOT a partition; read it as "time inside each scope".
  3. with TICKS.BIN (ags 0316, DOSAGS_TICKLOG=N): per-tick logic/render/scene/ugo over the loop-tick window
     [lo, hi] (default: 40 ticks after the LAST room entry to the last record): mean, median, p95, max,
     ticks with ugo > 25 ms, the room-entry ticks and click ticks seen.
Release builds compile the timers out: sections 2-3 are then empty. Figures from DOSBox-X are emulated time.
"""
import glob, os, re, statistics, struct, sys


def text(d):
    t = ''
    for f in sorted(glob.glob(os.path.join(d, '*.LOG'))) + [os.path.join(d, 'STDOUT.TXT')]:
        if os.path.exists(f):
            t += open(f, 'rb').read().decode('latin1') + '\n'
    return t


def ticklog(d):
    p = os.path.join(d, 'TICKS.BIN')
    if not os.path.exists(p):
        return None
    b = open(p, 'rb').read()
    magic, ver, n, dropped, cap = struct.unpack('<5I', b[:20])
    if magic != 0x474F4C54 or ver != 1:
        return None
    r = struct.unpack('<%dI' % (2 * n), b[20:20 + 8 * n])
    return dropped, cap, [(r[2 * i], r[2 * i + 1] >> 28, r[2 * i + 1] & 0x0FFFFFFF) for i in range(n)]


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else float('nan')


def main():
    a = sys.argv[1:]
    d = a[0]
    lo = int(a[a.index('--lo') + 1]) if '--lo' in a else None
    hi = int(a[a.index('--hi') + 1]) if '--hi' in a else None
    t = text(d)
    g = lambda pat: (re.findall(pat, t, re.M) or [None])[-1]
    print('== %s' % d)
    print('stamp %s exit %s rooms %s' % (g(r'^binary_sha12=(\S+)'), g(r'^exit_code=(-?\d+)'),
                                         ' '.join(re.findall(r'Now in room (\d+)', t))))
    for pat in (r'^DOS-PORT tick_rate=.*$', r'^DOS-PORT tick_rate_steady=.*$', r'^fps_p50=.*$', r'^DOS-PORT fps_basis.*$'):
        v = g(pat)
        if v:
            print('  ' + v.strip())
    ticks = int(g(r'tick_rate_steady=[\d.]+ ticks=(\d+)') or 0)
    ts = {}
    for m in re.finditer(r'DOS-PORT tickstats_(\w+) calls=(\d+) .*?total_us=(\d+)', t):
        ts.setdefault(m.group(1), (int(m.group(2)), int(m.group(3))))
    if ts:
        print('-- tickstats, whole run (nested scopes overlap; ms/tick over %d game ticks)' % ticks)
        print('  %-36s %8s %10s %9s %9s' % ('phase', 'calls', 'total_ms', 'ms/call', 'ms/tick'))
        for k, (c, us) in sorted(ts.items(), key=lambda kv: -kv[1][1]):
            if c == 0:
                continue
            print('  %-36s %8d %10.1f %9.3f %9.3f' % (k, c, us / 1000.0, us / 1000.0 / c, us / 1000.0 / ticks if ticks else 0))
        u, r, s = ts.get('update_game_once_total'), ts.get('render_to_screen'), ts.get('scene_construct')
        if u and r and s and u[0]:
            print('  logic_coarse (ugo - render - scene) / ugo calls = %.3f ms' % ((u[1] - r[1] - s[1]) / u[0] / 1000.0))
        w = ts.get('wait_next_frame')
        if u and w and ticks:
            print('  busy/tick (ugo - wait_next_frame) = %.3f ms; idle wait/tick = %.3f ms' % (
                (u[1] - w[1]) / 1000.0 / ticks, w[1] / 1000.0 / ticks))
            if r and s:
                print('  split/tick: logic excl. wait (ugo - render - scene - wait) %.3f | scene %.3f | render_to_screen %.3f ms' % (
                    (u[1] - r[1] - s[1] - w[1]) / 1000.0 / ticks, s[1] / 1000.0 / ticks, r[1] / 1000.0 / ticks))
        fine = sum(1 for v in ts.values() if v[0] > 0)
        print('  phases recording: %d (fine timing %s)' % (fine, 'ON' if ts.get('script_vm', (0, 0))[0] > 0 else 'off'))
    else:
        print('-- no tickstats lines (release flavour, or timers off)')
    tl = ticklog(d)
    if tl is None:
        print('-- no TICKS.BIN')
        return 0
    dropped, cap, recs = tl
    per = {}
    rooms, clicks = [], []
    for lc, k, v in recs:
        e = per.setdefault(lc, [0, 0, 0])
        if k in (1, 2, 3):
            e[k - 1] += v
        elif k == 4:
            rooms.append((lc, v))
        elif k in (5, 6):
            clicks.append(lc)
    lcs = sorted(per)
    if lo is None:
        lo = (rooms[-1][0] + 40) if rooms else lcs[0]
    if hi is None:
        hi = lcs[-1]
    w = [lc for lc in lcs if lo <= lc <= hi]
    print('-- TICKS.BIN: %d records, dropped %d, cap %d; room entries %s; clicks/keys %d (%s)' % (
        len(recs), dropped, cap, rooms, len(clicks), ' '.join(map(str, clicks[:40]))))
    print('   window loop ticks %d..%d: %d ticks' % (lo, hi, len(w)))
    cols = {'ugo': [per[x][0] / 1000.0 for x in w], 'render': [per[x][1] / 1000.0 for x in w],
            'scene': [per[x][2] / 1000.0 for x in w]}
    cols['logic'] = [u - r - s for u, r, s in zip(cols['ugo'], cols['render'], cols['scene'])]
    print('   (per-tick logic = ugo - render - scene INCLUDES the frame wait, which TICKS.BIN does not record separately)')
    print('   %-8s %8s %8s %8s %8s' % ('ms/tick', 'mean', 'median', 'p95', 'max'))
    for k in ('logic', 'render', 'scene', 'ugo'):
        xs = cols[k]
        if xs:
            print('   %-8s %8.2f %8.2f %8.2f %8.2f' % (k, statistics.mean(xs), statistics.median(xs), pct(xs, 0.95), max(xs)))
    over = [x for x, u in zip(w, cols['ugo']) if u > 25.0]
    print('   ticks with ugo > 25 ms: %d (%s)' % (len(over), ' '.join(map(str, over[:30]))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
