#!/usr/bin/env python3
"""LAB-R2 Q3: which skipped frames come from spike ticks (ugo 40-250 ms: click pathfinding, room entry) and which from
budget-bound ticks (a drawn tick > 25 ms), for one cell's TICKS.BIN.

    q3sim.py CELL_DIR [--lo L] [--hi H] [--spike 40] [--list]

1. Observed: skipped ticks (no render record) and the spike ticks, and a local rule: a skip is SPIKE-LOCAL if the last
   drawn-or-spike tick before its burst was a spike (the burst opens right behind the spike).
2. A replay of dos_run_tick_fixed (game_run.cpp: owed = elapsed/25 ms - ticks; up to MAX_CATCHUP=5 render-skipped
   ticks; a resync forgives what is still owed after 5 or when more than 5 ahead; the normal tick waits to its slot)
   on per-tick costs: drawn cost = logic + scene + render, skipped cost = logic, logic = ugo - scene - render - wait
   (wait from lab kind 7 when present, else 0). A tick whose actual state lacks the other cost takes the median of the
   nearest 40 ticks that have it. Counterfactuals: NOSPIKE (spike ticks get the local median costs), NOBUDGET (every
   non-spike drawn cost capped at 24.9 ms), NEITHER. FIFO labels: each tick's excess over 25 ms is a debt packet
   tagged spike/budget; a catch-up tick repays the oldest packets and takes the tag it mostly repaid.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ticks import load, med

SLOT = 25.0


def costs(T, spike):
    n = len(T)
    lg, rs = [None] * n, [None] * n
    for i, t in enumerate(T):
        r = (t.get('render', 0) + t.get('scene', 0)) / 1000.0
        w = t.get('wait', 0) / 1000.0
        if t['drawn']:
            rs[i] = r; lg[i] = t['ugo'] / 1000.0 - r - w
        else:
            lg[i] = t['ugo'] / 1000.0
    def near(arr, i, ok):
        xs = []
        for d in range(1, 400):
            for j in (i - d, i + d):
                if 0 <= j < n and arr[j] is not None and ok(j):
                    xs.append(arr[j])
            if len(xs) >= 40:
                break
        return med(xs) if xs else 0.0
    nonspk = lambda j: T[j]['ugo'] < spike * 1000
    rs_f = [rs[i] if rs[i] is not None else near(rs, i, nonspk) for i in range(n)]
    lg_med = [near(lg, i, nonspk) for i in range(n)]
    rs_med = [near(rs, i, nonspk) for i in range(n)]
    return lg, rs_f, lg_med, rs_med


OVH = 0.0


def sim(lg, rs, tags):
    """returns list of (drawn?, tag-of-skip or None) per simulated tick, plus resync count"""
    t = 0.0; k = 0; i = 0; n = len(lg); out = []; resync = 0
    pk = []   # FIFO debt packets [amount, tag]
    def add(c, tag):
        ex = c - SLOT
        if ex > 0:
            pk.append([ex, tag])
        elif ex < 0:
            pay(-ex)
    def pay(x):
        got = {}
        while x > 1e-9 and pk:
            a = min(x, pk[0][0]); pk[0][0] -= a; x -= a
            got[pk[0][1]] = got.get(pk[0][1], 0) + a
            if pk[0][0] <= 1e-9:
                pk.pop(0)
        return got
    while i < n:
        owed = int(t // SLOT) - k
        m = 0
        while owed > 0 and m < 5 and i < n:
            c = lg[i] + OVH; t += c; k += 1; owed -= 1; m += 1
            ex = c - SLOT
            got = pay(-ex) if ex < 0 else {}
            if ex > 0:
                pk.append([ex, tags[i]])
            lab = max(got, key=got.get) if got else ('spike' if any(p[1] == 'spike' for p in pk) else 'budget')
            out.append((i, False, lab)); i += 1
        if owed > 0 or owed < -5:
            t = 0.0; k = 0; resync += 1; pk.clear()
        if i >= n:
            break
        c = lg[i] + rs[i] + OVH
        add(c, tags[i])
        t += c; k += 1
        if t < k * SLOT:
            t = k * SLOT   # the normal tick waits to its slot (ahead of schedule: no debt)
            pk.clear()
        out.append((i, True, None)); i += 1
    return out, resync


def main():
    a = sys.argv[1:]
    d = a[0]
    spike = float(a[a.index('--spike') + 1]) if '--spike' in a else 40.0
    global OVH
    OVH = float(a[a.index('--ovh') + 1]) if '--ovh' in a else 0.0
    A = load(os.path.join(d, 'TICKS.BIN'))
    T = A['ticks']
    lo = int(a[a.index('--lo') + 1]) if '--lo' in a else T[0]['lc']
    hi = int(a[a.index('--hi') + 1]) if '--hi' in a else T[-1]['lc']
    T = [t for t in T if lo <= t['lc'] <= hi]
    n = len(T)
    sk = [i for i, t in enumerate(T) if not t['drawn']]
    sp = [i for i, t in enumerate(T) if spike * 1000 <= t['ugo'] <= 250000]
    big = [i for i, t in enumerate(T) if t['ugo'] > 250000]
    print('== %s ticks %d..%d (%d): skipped %d (%.2f%%), spike ticks %d-250 ms: %d, > 250 ms: %d; rooms %s' % (
        d, lo, hi, n, len(sk), 100.0 * len(sk) / n, int(spike), len(sp), len(big), A['rooms']))
    print('   spike ticks: %s' % ' '.join('%d(%.0f%s)' % (T[i]['lc'], T[i]['ugo'] / 1000.0,
          ',click' if T[i].get('click') else (',room' if 'room' in T[i] else '')) for i in sp + big))
    # observed local rule
    loc_sp, loc_bu = [], []
    for i in sk:
        j = i - 1
        while j >= 0 and not T[j]['drawn'] and T[j]['ugo'] < spike * 1000:
            j -= 1
        (loc_sp if j >= 0 and T[j]['ugo'] >= spike * 1000 else loc_bu).append(T[i]['lc'])
    print('-- observed, local rule: spike-local skips %d, other %d' % (len(loc_sp), len(loc_bu)))
    if '--list' in a:
        print('   spike-local: %s' % ' '.join(map(str, loc_sp)))
        print('   other: %s' % ' '.join(map(str, loc_bu)))
    lg, rs, lgm, rsm = costs(T, spike)
    dl = float(a[a.index('--dlogic') + 1]) if '--dlogic' in a else 0.0   # ms taken off every tick's logic (release estimate)
    lg = [max(0.0, x - dl) for x in lg]; lgm = [max(0.0, x - dl) for x in lgm]
    tags = ['spike' if T[i]['ugo'] >= spike * 1000 else 'budget' for i in range(n)]
    out, rsy = sim(lg, rs, tags)
    ssk = [i for i, dr, _ in out if not dr]
    agree = sum(1 for i, dr, _ in out if dr == T[i]['drawn'])
    lab = {}
    for i, dr, l in out:
        if not dr:
            lab[l] = lab.get(l, 0) + 1
    print('-- replay (actual costs): skipped %d (observed %d), per-tick state agreement %.1f%%, resyncs %d, FIFO labels %s' % (
        len(ssk), len(sk), 100.0 * agree / n, rsy, lab))
    if '--list' in a:
        print('   replay FIFO spike skips: %s' % ' '.join(str(T[i]['lc']) for i, dr, l in out if not dr and l == 'spike'))
    lg2 = [lgm[i] if tags[i] == 'spike' else lg[i] for i in range(n)]
    rs2 = [rsm[i] if tags[i] == 'spike' else rs[i] for i in range(n)]
    o2, _ = sim(lg2, rs2, tags)
    rs3 = [rs[i] if tags[i] == 'spike' else max(0.0, min(rs[i], 24.9 - OVH - lg[i])) for i in range(n)]
    o3, _ = sim(lg, rs3, tags)
    rs4 = [max(0.0, min(rs2[i], 24.9 - OVH - lg2[i])) for i in range(n)]
    o4, _ = sim(lg2, rs4, tags)
    c = lambda o: sum(1 for _, dr, _ in o if not dr)
    s1, s2, s3, s4 = c(out), c(o2), c(o3), c(o4)
    print('-- counterfactual replays: actual %d | NOSPIKE %d | NOBUDGET %d | NEITHER %d' % (s1, s2, s3, s4))
    print('   spike-attributable: marginal (actual - NOSPIKE) %d = %.2f%% of ticks; standalone (NOBUDGET) %d = %.2f%%' % (
        s1 - s2, 100.0 * (s1 - s2) / n, s3, 100.0 * s3 / n))
    print('   budget-attributable: marginal (actual - NOBUDGET) %d = %.2f%%; standalone (NOSPIKE) %d = %.2f%%' % (
        s1 - s3, 100.0 * (s1 - s3) / n, s2, 100.0 * s2 / n))
    if '--list' in a:
        print('   NOBUDGET skips (spike-only): %s' % ' '.join(str(T[i]['lc']) for i, dr, _ in o3 if not dr))
    return 0


if __name__ == '__main__':
    sys.exit(main())
