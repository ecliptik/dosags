#!/usr/bin/env python3
"""rs-owed.py -- round RS's reader for the per-call pacer log (OWED.BIN, apply-owedlog-rig.py) and the per-tick log
(TICKS.BIN, DOSAGS_TICKLOG) of an instrumented MS3 cell. Read-only. Written before any cell.
  rs-owed.py cell CELLDIR            one cell: validity, click-tick lengths by room, per-call debt
  rs-owed.py compare ONDIR OFFDIR    the lab check: the same binary with the log on / off (the log's own cost)
Validity of a cell's log (all must hold, else the per-call read is VOID and only the TICKS.BIN read is made):
  OWED.BIN present, magic "OWD1", version 1, record size 24, n records = the header's n;
  RUNMANIFEST "DOS-PORT labowed ... write=ok" with the same n / before / dropped;
  the loop counter strictly increasing over the records;
  every record's drawn tick (lc + catchup) is drawn in TICKS.BIN, and the sum of catchup equals the ticks TICKS.BIN marks
  skipped between the first record's lc and the last record's drawn tick (the engine's own two logs agree);
  dropped = 0 -- if not, the per-call read covers the logged prefix only and says so (not VOID).
Reads (information; no term -- the run is not an A/B and makes no displayed-% claim):
  click-tick lengths (the click tick's ugo, and the two ticks after it), by room: p10 / median / p90, how many over 50,
  75, 100 ms; mapped to the release level two ways (the model's mappings: offset d = -1.70 ms per tick; scale k = 0.937);
  the per-call debt: calls by owed (<= -1, 0, 1, 2-5, > 5), rebases by kind, waits (count > 0, resets), and the grid
  offset (now - epoch mod 25 ms) over the calls after the restore's settling ticks (5441-5499);
  the press-3 tick (round RR's watch item, RESULT-SBRK: the 63-page growth at click 3): click 3's tick length beside
  clicks 2 and 4."""
import os, re, struct, statistics as S, sys


def load_ticks(path):
    b = open(path, 'rb').read()
    magic, ver, n, dropped, cap = struct.unpack('<5I', b[:20])
    assert magic == 0x474F4C54 and ver == 1, 'not a TICKS.BIN v1'
    r = struct.unpack('<%dI' % (2 * n), b[20:20 + 8 * n])
    ticks, cur = [], {}
    for i in range(n):
        lc, k, v = r[2 * i], r[2 * i + 1] >> 28, r[2 * i + 1] & 0x0FFFFFFF
        if k == 1:
            t = {'lc': lc - 1, 'ugo': v}
            t.update(cur); t['drawn'] = 'render' in cur
            ticks.append(t); cur = {}
        elif k == 4:
            cur['room'] = v
        elif k == 5:
            cur['click'] = cur.get('click', 0) + 1
        elif k == 2:
            cur['render'] = cur.get('render', 0) + v
        elif k == 3:
            cur['scene'] = cur.get('scene', 0) + v
    room = None
    for t in ticks:
        room = t.get('room', room); t['inroom'] = room
    return {'ticks': ticks, 'dropped': dropped, 'cap': cap}


def load_owed(path):
    b = open(path, 'rb').read()
    magic, ver, n, before, dropped, frm, rs = struct.unpack('<7I', b[:28])
    if magic != 0x3144574F or ver != 1 or rs != 24 or len(b) != 28 + 24 * n:
        raise ValueError('header: magic %08x ver %d recsize %d n %d bytes %d' % (magic, ver, rs, n, len(b)))
    recs = []
    for i in range(n):
        lc, t_us, since, wait, owed, cu, rb, rs_ = struct.unpack('<iIiihBBB3x', b[28 + 24 * i:52 + 24 * i])
        recs.append({'lc': lc, 't_us': t_us, 'since': since, 'wait': wait, 'owed': owed, 'catchup': cu, 'rebase': rb, 'reset': rs_})
    return {'n': n, 'before': before, 'dropped': dropped, 'from': frm, 'recs': recs}


def q(xs, f):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(f * len(xs)))] if xs else float('nan')


def cell(d):
    log = open(os.path.join(d, 'RUNMANI.LOG'), errors='replace').read().replace('\r', '')
    T = load_ticks(os.path.join(d, 'TICKS.BIN'))
    ticks = T['ticks']; by = {t['lc']: t for t in ticks}
    print('## %s' % os.path.basename(d.rstrip('/')))
    stamp = (re.search(r'binary_sha12=(\w+)', log) or [None, '?'])[1]
    sk = (re.search(r'frames_skipped=(\d+)', log) or [None, '?'])[1]
    mm = (re.search(r'memory_min_free_kb=(\d+)', log) or [None, '?'])[1]
    print('stamp %s; frames_skipped %s; memory_min_free_kb %s; TICKS.BIN ticks %d (dropped %d, cap %d)' % (
        stamp, sk, mm, len(ticks), T['dropped'], T['cap']))
    # click ticks
    clicks = [t['lc'] for t in ticks if t.get('click')]
    print('\n### click ticks: %d (TICKS.BIN click markers)' % len(clicks))
    rooms = sorted(set(by[c]['inroom'] for c in clicks))
    print('| room | tick | n | p10 / median / p90 ms | > 50 / 75 / 100 ms | release level by offset (-1.70) median | by scale (x 0.937) median |')
    print('|---|---|---|---|---|---|---|')
    for rm in rooms:
        for off, nm in ((0, 'click'), (1, 'click+1'), (2, 'click+2')):
            v = [by[c + off]['ugo'] / 1000.0 for c in clicks if by[c]['inroom'] == rm and (c + off) in by]
            if not v:
                continue
            print('| %s | %s | %d | %.1f / %.1f / %.1f | %d / %d / %d | %.1f | %.1f |' % (
                rm, nm, len(v), q(v, .1), S.median(v), q(v, .9), sum(x > 50 for x in v), sum(x > 75 for x in v),
                sum(x > 100 for x in v), S.median(v) - 1.70, S.median(v) * 0.937))
    if len(clicks) >= 4:
        print('press-3 watch (RESULT-SBRK): click ticks 2 / 3 / 4 = %s ms (ticks %s)' % (
            ' / '.join('%.1f' % (by[c]['ugo'] / 1000.0) for c in clicks[1:4]), ' / '.join(str(c) for c in clicks[1:4])))
    # the per-call log
    print('\n### the per-call log (OWED.BIN)')
    p = os.path.join(d, 'OWED.BIN')
    m = re.search(r'DOS-PORT labowed from=(-?\d+) n=(\d+) before=(\d+) dropped=(\d+) bytes=(\d+) write=(\w+)', log)
    why = []
    try:
        O = load_owed(p)
    except (OSError, ValueError, struct.error) as e:
        print('per-call read VOID: %s' % e); return
    if not m or m.group(6) != 'ok':
        why.append('no labowed line with write=ok')
    elif (int(m.group(2)), int(m.group(3)), int(m.group(4))) != (O['n'], O['before'], O['dropped']):
        why.append('labowed line and OWED.BIN header differ')
    recs = O['recs']
    if any(b['lc'] <= a['lc'] for a, b in zip(recs, recs[1:])):
        why.append('loop counter not increasing')
    nd = [r for r in recs if not by.get(r['lc'] + r['catchup'], {}).get('drawn')]
    if nd:
        why.append('%d records whose drawn tick is not drawn in TICKS.BIN (first lc %d)' % (len(nd), nd[0]['lc']))
    if recs:
        lo, hi = recs[0]['lc'], recs[-1]['lc'] + recs[-1]['catchup']
        sk_t = sum(1 for t in ticks if lo <= t['lc'] <= hi and not t['drawn'])
        cu = sum(r['catchup'] for r in recs)
        if sk_t != cu:
            why.append('catch-up sum %d != TICKS.BIN skipped %d over %d..%d' % (cu, sk_t, lo, hi))
    print('n %d, before %d, dropped %d, from %d -> %s' % (O['n'], O['before'], O['dropped'], O['from'],
          ('VOID: ' + '; '.join(why)) if why else ('VALID' + ('' if O['dropped'] == 0 else ' (PREFIX ONLY: %d calls not logged)' % O['dropped']))))
    if why:
        return
    ow = [r['owed'] for r in recs]
    print('calls by owed: <= -1 %d, 0 %d, 1 %d, 2-5 %d, > 5 %d; catch-up ticks %d; rebases: flag %d, clamp %d, ahead %d' % (
        sum(x <= -1 for x in ow), sum(x == 0 for x in ow), sum(x == 1 for x in ow), sum(2 <= x <= 5 for x in ow), sum(x > 5 for x in ow),
        sum(r['catchup'] for r in recs), sum(r['rebase'] == 1 for r in recs), sum(r['rebase'] == 2 for r in recs), sum(r['rebase'] == 3 for r in recs)))
    w = [r['wait'] for r in recs if r['wait'] > 0]
    print('waits: %d of %d drawn ticks waited (median %.2f ms); frame-time resets %d' % (
        len(w), len(recs), S.median(w) / 1000.0 if w else 0, sum(r['reset'] for r in recs)))
    g = [(r['since'] % 25000) / 1000.0 for r in recs if 5441 <= r['lc'] <= 5499]
    if g:
        print('grid offset (now - epoch mod 25 ms) over calls 5441-5499: %d calls, %.3f .. %.3f ms' % (len(g), min(g), max(g)))


def compare(a, b):
    A, B = load_ticks(os.path.join(a, 'TICKS.BIN'))['ticks'], load_ticks(os.path.join(b, 'TICKS.BIN'))['ticks']
    ba = {t['lc']: t for t in A}; bb = {t['lc']: t for t in B}
    common = [l for l in sorted(ba) if l in bb and l >= 5450]
    print('## the log\'s own cost: %s (log on) against %s (log off), ticks from 5450 in both: %d' % (
        os.path.basename(a.rstrip('/')), os.path.basename(b.rstrip('/')), len(common)))
    print('drawn flags differ on %d ticks; skipped: on %d, off %d' % (
        sum(ba[l]['drawn'] != bb[l]['drawn'] for l in common), sum(not ba[l]['drawn'] for l in common), sum(not bb[l]['drawn'] for l in common)))
    for rm in sorted(set(ba[l]['inroom'] for l in common)):
        d = [ba[l]['ugo'] - bb[l]['ugo'] for l in common if ba[l]['inroom'] == rm and ba[l]['drawn'] and bb[l]['drawn']
             and not ba[l].get('click') and not bb[l].get('click')]
        if d:
            print('room %s, drawn non-click ticks in both: %d; ugo on - off median %+d us (p10 %+d, p90 %+d)' % (rm, len(d), S.median(d), q(d, .1), q(d, .9)))


if __name__ == '__main__':
    if sys.argv[1] == 'cell':
        cell(sys.argv[2])
    elif sys.argv[1] == 'compare':
        compare(sys.argv[2], sys.argv[3])
