#!/usr/bin/env python3
"""pa-read.py -- round RT's readings: the pacer A/B on MS3 (the ags 0383 release A against the same code with the long-tick
rule P, DOSAGS_LAB_STALL_MS=T, tests/harness/apply-pace-rig.py). Read-only. Written before any data.

  pa-read.py [--stamp-p X] [--t-ms T] cell CELL_DIR KIND        one READ line (KIND = A | P)
  pa-read.py [--stamp-p X] [--t-ms T] verdict CELL_DIR:KIND...   the term PACE-MS3 and the watch list

VALID, both kinds: rs-read.py's A rule (the stamp -- A f2e183845d2f, P from --stamp-p; the routestamp witness allocs >= 1,
  peak 192000; exit_code=0 and ENGINE HAS SHUTDOWN; underruns = overwrites = 0; PAIR-OK or PAIR-OK-114LATE); plus
  ticks= on the tick_rate_steady line = 7003 (the denominator of displayed %: the loop's ticks, fixed by the TAS exit at
  12440 in both arms) and loop_ms present; plus, P only: a "DOS-PORT labpace stall_ms=T ... max_forgiven_short_ticks= spins=0"
  line (the rule was on at the registered threshold, no lab spin); A: no labpace line (the shipped binary has none).
Information per P cell (the operator lifted the 2026-11-09 slip limit, 2026-11-19), all LOWER BOUNDS in whole ticks
  (each rebase's debt is floored to whole ticks and a sub-tick debt reads 0; the lab's 12 spins cost 301 ms of loop_ms
  but read 3 forgiven ticks = 75 ms; sdlports, after the lab check): the largest forgiven slip
  (max_forgiven_ticks x 25 ms; the room-2 load, as switched) and the largest outside ticks over 250 ms
  (max_forgiven_short_ticks x 25 ms: the restore, the room loads and any other 0163 stall excluded).
displayed % = 100 x (1 - frames_skipped / ticks), frames_skipped = loop counter - render counter (as every round).
GAME TIME (the operator's limit, 2026-11-19: at most 2.0% game time lost per run), measured on the cells, two ways:
  G     (registered) = loop_ms(P) / mean loop_ms(the round's valid A cells) - 1. loop_ms is the engine's own wall span of
        the game loop, first tick entry to last tick exit (the tick_rate_steady line), over the same 7,003 ticks in both
        arms; so G is the extra wall time the same game took = the game time the rule gave up beyond the shipped pacer.
  Gwin  (cross-check) = Lwin(P) - mean Lwin(A), Lwin = 1 - 25 ms x (k1 - k0) / (m1 - m0) over the persec rows from the
        first with tick >= 5520 to the last (the restore's settling excluded). G and Gwin must agree within 0.5 points,
        else the time reading is HELD (to sdlports).
  Information beside them: Lwin itself (the game's clock against the wall over the window, room loads included: the
        shipped pacer already reads ~2.3-2.4% by it), and P's labpace forgiven_ticks x 25 ms.
The term PACE-MS3 (registered: RTP1, RTP2; every other valid P cell enters the time rule, never the bar):
  MET          RTP1 and RTP2 valid, both >= 99.0% displayed, >= 1 valid A cell, and EVERY valid P cell's G <= 2.0%
  BAR-NOT-MET  RTP1 and RTP2 valid, >= 1 valid A, every G <= 2.0%, and one or both under 99.0%
  TIME-OVER    >= 1 valid A and any valid P cell's G > 2.0% (whatever the bar reads)
  HELD         G and Gwin disagree by more than 0.5 points in any valid P cell (to sdlports; nothing read)
  NOT READ     RTP1 or RTP2 not valid, or no valid A cell
  Precedence when several hold (sdlports, FIX-UP 1): HELD, then NOT READ, then TIME-OVER, then MET / BAR-NOT-MET. So a
  cell whose G and Gwin disagree reads HELD even if its G is also over 2.0%.
Information: the A cells against round RR / RS (every valid A cell in 239..494 skips -- RS's band; outside it goes to
  sdlports beside the term); per P cell the skips, rebases, forgiven ticks, the pairing and LEVEL lines; the press 114
  margin (pairing WITNESS)."""
import importlib.util
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('rsread', os.path.join(HERE, 'rs-read.py'))
rs = importlib.util.module_from_spec(_s)
_s.loader.exec_module(rs)
STAMP_P = None
T_MS = 45
LIMIT = 2.0
BAR = 99.0
REG = ('RTP1', 'RTP2')
A_BAND = (239, 494)


def rd(p):
    try:
        return open(p, errors='replace').read()
    except OSError:
        return ''


def cell(c, kind):
    rs.STAMP['I'] = STAMP_P
    x = rs.cell(c, 'A' if kind == 'A' else 'I')   # the A rule; P's stamp via rs-read's I slot
    why = [w for w in x['why'] if not (kind == 'P' and w == 'no labowed write=ok')]
    if kind == 'P' and x['pair'] not in ('PAIR-OK', 'PAIR-OK-114LATE') and x['pair'] not in why:
        why.append(x['pair'])
    rm = rd(c + '/RUNMANI.LOG')
    tr = re.search(r'DOS-PORT tick_rate_steady=([\d.]+) ticks=(\d+) stall_ticks=(\d+) loop_ms=(\d+)', rm)
    ticks = int(tr.group(2)) if tr else None
    loop_ms = int(tr.group(4)) if tr else None
    if ticks != 7003:
        why.append('ticks %s != 7003' % ticks)
    lp = re.search(r'DOS-PORT labpace stall_ms=(\d+) rebases=(\d+) forgiven_ticks=(\d+) max_forgiven_ticks=(\d+) '
                   r'max_forgiven_short_ticks=(\d+) spins=(\d+)', rm)
    if kind == 'P' and not (lp and int(lp.group(1)) == T_MS and int(lp.group(6)) == 0):
        why.append('labpace line not stall_ms=%d spins=0 (%s)' % (T_MS, lp.group(0) if lp else 'missing'))
    if kind == 'A' and lp:
        why.append('labpace line in an A cell')
    rows = [(int(a), int(b)) for a, b in re.findall(r'DOS-PORT persec t=\d+ tick=(\d+) renders=\d+ real=\d+ skipped=\d+ ms=(\d+)', rm)]
    w = [r for r in rows if r[0] >= 5520]
    lwin = (1 - 25.0 * (w[-1][0] - w[0][0]) / (w[-1][1] - w[0][1])) * 100 if len(w) >= 2 else None
    pr = rd(c + '/PAIRING.txt')
    wit = re.search(r'WITNESS .*', pr); lev = re.search(r'LEVEL .*', pr)
    disp = 100.0 * (1 - x['skips'] / float(ticks)) if (x['skips'] is not None and ticks) else None
    return dict(c=c, tag=os.path.basename(c.rstrip('/')).split('-')[0], kind=kind, valid=not why, why=why, skips=x['skips'],
                disp=disp, ticks=ticks, loop_ms=loop_ms, lwin=lwin, lp=lp.groups() if lp else None, pair=x['pair'],
                wit=wit.group(0) if wit else None, lev=lev.group(0) if lev else None, board=x['board'])


def line(x, g=None, gw=None):
    f = lambda v, p='%.2f': 'n/a' if v is None else p % v
    lp = x['lp']
    return ('READ %s kind=%s valid=%s%s pair=%s skips=%s disp=%s%% ticks=%s loop_ms=%s Lwin=%s%%%s%s%s' % (
        os.path.basename(x['c'].rstrip('/')), x['kind'], 'yes' if x['valid'] else 'no',
        '' if x['valid'] else ' (' + '; '.join(x['why']) + ')', x['pair'], x['skips'], f(x['disp']), x['ticks'], x['loop_ms'],
        f(x['lwin'], '%.3f'), '' if g is None else ' G=%+.3f%%' % g, '' if gw is None else ' Gwin=%+.3f%%' % gw,
        '' if not lp else ' | labpace stall_ms=%s rebases=%s forgiven_ticks=%s (>= %d ms); largest forgiven slip >= %d ms, '
        'largest outside ticks over 250 ms (the restore, the room loads, 0163\'s stalls) >= %d ms [whole-tick lower bounds; G is the measure]' % (
            lp[0], lp[1], lp[2], 25 * int(lp[2]), 25 * int(lp[3]), 25 * int(lp[4]))))


def verdict(args):
    cells = [cell(*a.rsplit(':', 1)) for a in args]
    A = [x for x in cells if x['kind'] == 'A' and x['valid']]
    P = [x for x in cells if x['kind'] == 'P' and x['valid']]
    la = st.mean(x['loop_ms'] for x in A) if A else None
    wa = st.mean(x['lwin'] for x in A) if A else None
    G = {}
    for x in cells:
        g = gw = None
        if x['kind'] == 'P' and x['valid'] and A:
            g = 100.0 * (x['loop_ms'] / la - 1); gw = x['lwin'] - wa
            G[x['tag']] = (g, gw)
        print(line(x, g, gw))
        if x['wit']:
            print('  %s' % x['wit'])
        if x['lev']:
            print('  %s' % x['lev'])
    print('valid A cells: %d (mean loop_ms %s, mean Lwin %s%%); valid P cells: %d' % (
        len(A), '%.0f' % la if la else 'n/a', '%.3f' % wa if wa is not None else 'n/a', len(P)))
    out = [x['tag'] for x in A if not (A_BAND[0] <= x['skips'] <= A_BAND[1])]
    print('information: A cells against round RS / RR (%d..%d skips): %s' % (
        A_BAND[0], A_BAND[1], 'all inside' if not out else 'OUTSIDE: %s -- to sdlports beside the term' % ', '.join(out)))
    reg = {x['tag']: x for x in P if x['tag'] in REG}
    held = [t for t, (g, gw) in G.items() if abs(g - gw) > 0.5]
    over = [t for t, (g, gw) in G.items() if g > LIMIT]
    if held:
        term = 'HELD (G and Gwin disagree by more than 0.5 points in %s; to sdlports)' % ', '.join(held)
    elif not A or len(reg) < 2:
        term = 'NOT READ (%s)' % ('no valid A cell' if not A else 'registered P cells valid: %s' % (', '.join(sorted(reg)) or 'none'))
    elif over:
        term = 'TIME-OVER (G > %.1f%% in %s)' % (LIMIT, ', '.join(over))
    elif all(reg[t]['disp'] >= BAR for t in REG):
        term = 'MET'
    else:
        term = 'BAR-NOT-MET'
    print('PACE-MS3: %s -- T = %d ms; registered %s displayed %s; G (every valid P cell) %s; limit %.1f%%, bar %.1f%%' % (
        term, T_MS, '/'.join(REG), ', '.join('%s %.2f%%' % (t, reg[t]['disp']) for t in REG if t in reg) or 'n/a',
        ', '.join('%s %+.3f%%' % (t, G[t][0]) for t in sorted(G)) or 'n/a', LIMIT, BAR))
    print('what follows: MET -> the claim "MS3 >= 99%% displayed with the %d ms long-tick rule, game time lost +G%% against '
          'the shipped pacer" goes to the operator as a NEW restated goal naming the setting (2026-11-09); nothing ships '
          'without their ruling. Every other outcome -> to sdlports, as read.' % T_MS)


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--stamp-p' in a:
        i = a.index('--stamp-p'); STAMP_P = a[i + 1]; del a[i:i + 2]
    if '--t-ms' in a:
        i = a.index('--t-ms'); T_MS = int(a[i + 1]); del a[i:i + 2]
    if len(a) >= 3 and a[0] == 'cell':
        print(line(cell(a[1], a[2])))
    elif len(a) >= 2 and a[0] == 'verdict':
        verdict(a[1:])
    else:
        sys.exit(__doc__)
