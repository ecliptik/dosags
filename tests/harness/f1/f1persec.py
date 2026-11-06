#!/usr/bin/env python3
"""f1persec.py -- frames-displayed figures from the per-second series, for cells gatebar cannot read whole-run
(LAB helper, build/ws/f1prep; not committed).

    f1persec.py CELL_DIR [--skip-s N] [--room R]

Why: a --loadsavedgame cell restores GameTimer's LoopCounter and RenderCounter from the save, so the manifest's
whole-run `tick_rate` (loop counter / time) and `fps_basis render_passes` carry the save's base (7 Days restore:
tick_rate 151.02, render_passes 9495 for ~2357 ticks run) and gatebar's whole-run band and presents_real/render_passes
are wrong for such a cell (not VOID: wrong). `ticks=` (tick_rate_steady line) and frames_skipped are per-run and stay valid.

The `DOS-PORT persec t= tick= renders= real= skipped= ms=` rows (cumulative, one per real second; present in both
flavours) give the same figures over any window by differencing. Window: from row 1 + --skip-s (default 5: past the
restore/room load) to the last row. Prints, over the window: ticks, renders, real presents, ticks/s, renders/ticks,
real/renders, and the cell's own manifest frames_skipped / ticks for comparison.
"""
import re, sys, glob, os


def main():
    a = sys.argv[1:]
    d = a[0]
    skip = int(a[a.index('--skip-s') + 1]) if '--skip-s' in a else 5
    t = ''
    for f in sorted(glob.glob(os.path.join(d, '*.LOG'))):
        t += open(f, 'rb').read().decode('latin1')
    rows = [tuple(int(x) for x in m) for m in
            re.findall(r'DOS-PORT persec t=(\d+) tick=(\d+) renders=(\d+) real=(\d+) skipped=(\d+) ms=(\d+)', t)]
    if len(rows) < skip + 2:
        print('too few persec rows: %d' % len(rows)); return 1
    a0, a1 = rows[skip], rows[-1]
    dt, dtick, dren, dreal = (a1[5] - a0[5]) / 1000.0, a1[1] - a0[1], a1[2] - a0[2], a1[3] - a0[3]
    fs = re.findall(r'frames_skipped=(\d+)', t); tk = re.findall(r'tick_rate_steady=[\d.]+ ticks=(\d+)', t)
    print('== %s  persec rows %d, window t=%d..%d (%.2f s)' % (d, len(rows), a0[0], a1[0], dt))
    print('   ticks %d  renders %d  real %d  ticks/s %.2f  renders/ticks %.2f%%  real/renders %.2f%%' % (
        dtick, dren, dreal, dtick / dt, 100.0 * dren / dtick, 100.0 * dreal / dren if dren else 0))
    if fs and tk:
        print('   manifest: frames_skipped %s of ticks %s -> 1 - fs/ticks = %.2f%% (whole run of this process)' % (
            fs[-1], tk[-1], 100.0 * (1 - int(fs[-1]) / int(tk[-1]))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
