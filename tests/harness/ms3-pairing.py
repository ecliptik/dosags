#!/usr/bin/env python3
"""ms3-pairing.py CELL_DIR... -- MS3 press/journey pairing and the room-2 level read (round RO onward).

From move's lab checker (lab-rb 957760ea, docs/lab/move-lab/rj/rn/clocksteps-ro.py). The changes: condition (3) is
pinned to the last persec line's ms= field, strictly greater, with no tolerance (operator + sdlports, 2026-11-12). move's
extrapolated loop end must also be exceeded, again strictly. Every cell prints the witness triple. Read-only.

Why: MS3's presses are wall-timed but the run ends at a TAS exit tick (12440). With the room-2 freezes gone (ags 0377),
press 114 can land after the game loop has ended, so it has no journey (round RN: RNF1 / RNF2, 113 / 114).

Reads RUNMANI.LOG (journey kind=click t_ms, persec), DRIVE-WALK.LOG (down_at; the UTC date from the cell dir name),
RUN.BAT (DOSAGS_TAS_AUTO_EXIT_TICK, default 12440).

Offset of press k = its DRIVE-WALK down_at (wall ms) minus journey k's t_ms (game ms).

PAIR line, one verdict:
- PAIR-OK            journeys == presses == 114, t_ms strictly increasing, and the first room-2 journey is #17. Also no
                     sustained offset shift <= -150 ms in presses 6-109 (a missing journey hidden by an extra one).
- PAIR-OK-114LATE    journeys == 113, presses == 114, and all of:
                     (1) t_ms strictly increasing; the first room-2 journey is #17;
                     (2) presses 1-113 pair 1:1: no sustained offset shift <= -150 ms in presses 6-108 (a missing journey
                         at press k shifts every later offset by about minus one press interval, >= ~1 s). No sustained
                         shift >= +150 ms in presses 23-108 unless its 5-press windows overlap a registered step bracket
                         (presses 33-36, 52-54, 90-95). Sustained = the median offset of the 5 presses from press q minus
                         the median of the 5 before it;
                     (3) press 114's game time, = its down_at minus the median offset of presses 95-113:
                         (3a) is STRICTLY GREATER than the last persec line's ms= field (no tolerance), and
                         (3b) is STRICTLY GREATER than move's loop-end estimate: the last persec ms plus (exit tick - its
                              tick) times the ms per tick of the last 5 persec rows (no tolerance).
- PAIR-VOID <reasons> anything else; every failed condition is listed.
WITNESS line (every cell): press114_game_ms, last_persec_ms, diff_ms (= press114_game_ms - last_persec_ms). For a
114-journey cell, press114_game_ms is journey 114's t_ms. Also printed: the loop-end estimate and press 114's margin
over it.
LEVEL line (PAIR-OK / PAIR-OK-114LATE only): each step = the change of the median offset between the step-free
stretches 21-33 | 36-52 | 54-90 | 95-114 (95-113 under PAIR-OK-114LATE). The steps: +830 (33->36), +1,730 (52->54),
+3,540 (90->95); resolution +-30 ms."""
import bisect
import datetime as D
import re
import statistics as st
import sys

BRACKETS = ((33, 36), (52, 54), (90, 95))


def load(c):
    day = re.search(r'(\d{4}-\d{2}-\d{2})', c).group(1)
    rm = open(c + '/RUNMANI.LOG', errors='replace').read()
    js = [(int(r), int(t)) for r, t in re.findall(r'journey kind=click room=(\d+) t_ms=(\d+)', rm)]
    dn, prev = [], None
    for x in re.findall(r'click \d+ .*?down_at=(\S+)', open(c + '/DRIVE-WALK.LOG', errors='replace').read()):
        t = D.datetime.strptime(day + ' ' + x, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000
        if prev and t < prev - 43200e3:
            t += 86400e3
        dn.append(t)
        prev = t
    ps = [tuple(int(v) for v in m) for m in
          re.findall(r'persec t=\d+ tick=(\d+) renders=\d+ real=\d+ skipped=\d+ ms=(\d+)', rm)]
    try:
        exit_tick = int(re.search(r'DOSAGS_TAS_AUTO_EXIT_TICK=(\d+)',
                                  open(c + '/RUN.BAT', errors='replace').read()).group(1))
    except Exception:
        exit_tick = 12440
    return js, dn, ps, exit_tick


def sustained(off, q, k=5):
    """median(off[q..q+k-1]) - median(off[q-k..q-1]), presses 1-based"""
    return st.median(off[q - 1:q - 1 + k]) - st.median(off[q - 1 - k:q - 1])


def loop_end(ps, exit_tick):
    ks = [k for k, _ in ps]
    ms = [m for _, m in ps]
    rate = (ms[-1] - ms[-6]) / float(ks[-1] - ks[-6])
    return ms[-1], ks[-1], ms[-1] + max(0, exit_tick - ks[-1]) * rate, rate


def check(c):
    js, dn, ps, exit_tick = load(c)
    nj, np_ = len(js), len(dn)
    ts = [t for _, t in js]
    last_ms, last_tick, end_est, rate = loop_end(ps, exit_tick)
    fails, wit, n = [], None, None
    if any(b <= a for a, b in zip(ts, ts[1:])):
        fails.append('t_ms not strictly increasing')
    r2 = next((i + 1 for i, (r, _) in enumerate(js) if r == 2), None)
    if r2 != 17:
        fails.append('first room-2 journey is #%s, not #17' % r2)
    if nj == np_ == 114:
        off = [d - t for d, t in zip(dn, ts)]
        wn = min((sustained(off, q), q) for q in range(6, 110))
        if wn[0] <= -150:
            fails.append('sustained offset shift %+.0f ms at press %d (a missing journey)' % wn)
        wit = float(ts[113])
        why = 'journeys 114 / presses 114 (worst sustained shift %+.0f ms at press %d)' % wn
        verdict, n = 'PAIR-OK', 114
    elif nj == 113 and np_ == 114:
        off = [d - t for d, t in zip(dn[:113], ts)]
        wn = min((sustained(off, q), q) for q in range(6, 109))
        if wn[0] <= -150:
            fails.append('sustained offset shift %+.0f ms at press %d (a missing journey)' % wn)

        def in_bracket(q):
            return any(q - 5 <= b and q + 4 >= a + 1 for a, b in BRACKETS)
        wp = max((sustained(off, q), q) for q in range(23, 109) if not in_bracket(q))
        if wp[0] >= 150:
            fails.append('sustained offset shift %+.0f ms at press %d outside the step brackets' % wp)
        wit = dn[113] - st.median(off[94:113])
        if not wit > last_ms:
            fails.append('(3a) press 114 game time not after the last persec ms')
        if not wit > end_est:
            fails.append('(3b) press 114 game time not after the loop-end estimate')
        why = ('journeys 113 / presses 114 (worst sustained shift %+.0f ms at press %d; outside brackets %+.0f ms at '
               'press %d)' % (wn[0], wn[1], wp[0], wp[1]))
        verdict, n = 'PAIR-OK-114LATE', 113
    else:
        fails.append('journeys %d / presses %d' % (nj, np_))
        why = ''
    if fails:
        verdict, n = 'PAIR-VOID', None
        why = '; '.join(fails) + (' | ' + why if why else '')
    if wit is None:
        w = 'WITNESS press114_game_ms=NA last_persec_ms=%d diff_ms=NA' % last_ms
    else:
        w = ('WITNESS press114_game_ms=%.1f last_persec_ms=%d diff_ms=%+.1f | loop_end_est_ms=%.1f (last persec tick '
             '%d, exit tick %d, %.2f ms/tick) margin_over_est_ms=%+.1f' % (
                 wit, last_ms, wit - last_ms, end_est, last_tick, exit_tick, rate, wit - end_est))
    return verdict, why, w, n


def level(c, n):
    js, dn, ps, _ = load(c)
    ts = [t for _, t in js][:n]
    off = [d - t for d, t in zip(dn[:n], ts)]
    lvl = lambda a, b: st.median(off[a - 1:b])
    L0, L1, L2, L3 = lvl(21, 33), lvl(36, 52), lvl(54, 90), lvl(95, n)
    return ('LEVEL +830 (33->36) %+.0f ms | +1,730 (52->54) %+.0f ms | +3,540 (90->95) %+.0f ms | last stretch 95-%d'
            % (L1 - L0, L2 - L1, L3 - L2, n))


if __name__ == '__main__':
    for c in sys.argv[1:]:
        name = c.rstrip('/').split('/')[-1]
        try:
            verdict, why, w, n = check(c)
        except Exception as e:  # a missing or unreadable log: VOID, reported
            print('PAIR %s PAIR-VOID unreadable (%s: %s)' % (name, type(e).__name__, e))
            continue
        print('PAIR %s %s %s' % (name, verdict, why))
        print('%s %s' % (w.split(' ', 1)[0], name + ' ' + w.split(' ', 1)[1]))
        if n:
            print('LEVEL %s %s' % (name, level(c, n)[6:]))
