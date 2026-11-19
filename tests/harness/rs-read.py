#!/usr/bin/env python3
"""rs-read.py -- round RS's readings (MS3 on the ags 0383 release, the confirmation pair; plus the instrumented per-call
log runs, read by rs-owed.py). Read-only. Written before any data.

  rs-read.py cell CELL_DIR KIND                    one READ line (KIND = A: the 0383 release; I: the instrumented RSOWL run)
  rs-read.py verdict CELL_DIR:KIND [...]           the round's term over the A cells, and the watch list over all

The A cells (the 0383 release, sha256 c6824107..., stamp f2e183845d2f; RM0383-2026-11-17):
  VALID = the manifest stamp f2e183845d2f in the cell's logs; the search witness in RUNMANI.LOG "DOS-PORT routestamp
  allocs= peak_bytes=" with allocs >= 1 and peak_bytes = 192000 (room 2's 960 x 200 mask; a cell whose search never ran
  is VOID); RUNMANIFEST exit_code=0 and "ENGINE HAS SHUTDOWN"; audio underruns = overwrites = 0; the pairing PAIR-OK or
  PAIR-OK-114LATE (ms3-pairing.py check()). 114EDGE expired with round RR and is not used.
  skips = frames_skipped; disp = 100 x (1 - skips / 7003), as round RR.
The I cells (RSOWL = the 0383 instrumented + apply-owedlog-rig.py; stamp in the round's expected stamps): VALID = its
  stamp, a "DOS-PORT labowed ... write=ok" line, clean exit, audio as A. Their skips are printed, never compared with
  the A cells (another flavour, fine timing on, the per-tick and per-call logs on); their reads are rs-owed.py's.
The term, over the valid A cells (RSA1, RSA2 registered; RSA3 enters only if valid), against round RR's F arm, which
  ran the code 0383 kept byte for byte (RR F: 359 / 324 / 409 skips, mean 364.0, same-binary range 85):
  CONSISTENT   >= 2 valid A cells, every one within RR F's range widened by its own spread (239..494), and their mean
               within RR F's mean +- 85 (279..449).
  INCONSISTENT >= 2 valid A cells and either test fails.
  NOT READ     fewer than 2 valid A cells.
  Information: the MS3 proof bar (a registered pair, both >= 99.0%) -- expected "no" (RR F: 94.2-95.4%).
  The pacer's microsecond sensitivity (lab-rb RESULT-OWEDLOG; round RR's same-binary range 85): no difference between
  two A cells, or between an A cell and RR, smaller than 85 skips is read as a difference at all.
The watch list from round RR, per cell (information, no term):
  partial_waits: the board's resume.partial_waits, MSTATS-RELEASE minus MSTATS-TAKE (RR: +2 in every F cell, +1 in O;
    RESULT-SBRK: the fast search's extra heap growth at click 1 -- 0383 always has it, so +2 is expected in every play
    cell); pkt_partial / pkt_timeout beside it.
  press 3: the skips in the persec second holding press 3's journey, beside presses 2 and 4 (RESULT-SBRK's estimated
    25-40 ms locked commit at click 3). The I cells read click 3's own tick length from TICKS.BIN (rs-owed.py).
  memory_min_free_kb (RR: 146,176 in F, 146,048 in O, unexplained; the lab reads the other way). The I binary carries
    196,608 bytes more .bss for its log buffer: its figure is printed apart."""
import importlib.util
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location('ms3pairing', os.path.join(HERE, 'ms3-pairing.py'))
mp = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(mp)
PLAY_TICKS = 7003
STAMP = {'A': 'f2e183845d2f', 'I': None}   # I: set from the round's RSOWL stamp (the --stamp-i argument)
RR_F = [359, 324, 409]
SPREAD = 85


def rd(p):
    try:
        return open(p, errors='replace').read()
    except OSError:
        return ''


def board(c):
    try:
        a = json.load(open(os.path.join(c, 'MSTATS-TAKE.json'))); b = json.load(open(os.path.join(c, 'MSTATS-RELEASE.json')))
        return {'partial_waits': b['resume']['partial_waits'] - a['resume']['partial_waits'],
                'pkt_partial': b['counters']['pkt_partial'] - a['counters']['pkt_partial'],
                'pkt_timeout': b['counters']['pkt_timeout'] - a['counters']['pkt_timeout']}
    except Exception:
        return None


def cell(c, kind):
    rm, so = rd(c + '/RUNMANI.LOG'), rd(c + '/STDOUT.TXT')
    why = []
    logs = ''.join(rd(os.path.join(c, f)) for f in sorted(os.listdir(c)) if f.upper().endswith('.LOG')) if os.path.isdir(c) else ''
    stamps = set(re.findall(r'binary_sha12=([0-9A-Za-z]+)', logs))
    if STAMP[kind] is None or stamps != {STAMP[kind]}:
        why.append('stamp %s' % (','.join(sorted(stamps)) or 'missing'))
    w = re.search(r'DOS-PORT routestamp allocs=(\d+) peak_bytes=(\d+)', rm)
    wit = tuple(int(x) for x in w.groups()) if w else None
    if not (wit and wit[0] >= 1 and wit[1] == 192000):
        why.append('search witness')
    if kind == 'I' and not re.search(r'DOS-PORT labowed .*write=ok', rm):
        why.append('no labowed write=ok')
    ec = re.search(r'^exit_code=(\d+)', rm, re.M)
    if not (ec and ec.group(1) == '0' and 'ENGINE HAS SHUTDOWN' in so):
        why.append('no clean exit')
    try:
        pv, pwhy, pw, _n = mp.check(c)
    except Exception:
        pv = 'PAIR-VOID'
    if kind == 'A' and pv not in ('PAIR-OK', 'PAIR-OK-114LATE'):
        why.append(pv)
    ur = re.search(r'underruns=(\d+)', rm); ow = re.search(r'overwrites=(\d+)', rm)
    if not (ur and ow and ur.group(1) == '0' and ow.group(1) == '0'):
        why.append('audio')
    fs = re.search(r'frames_skipped=(\d+)', rm)
    skips = int(fs.group(1)) if fs else None
    if skips is None:
        why.append('no frames_skipped')
    mm = re.search(r'memory_min_free_kb=(\d+)', rm)
    rows = [(int(a), int(b), int(d)) for a, b, d in re.findall(r'DOS-PORT persec t=\d+ tick=(\d+) renders=(\d+) real=\d+ skipped=\d+ ms=(\d+)', rm)]
    jt = [int(x) for x in re.findall(r'journey kind=click [^\n]*?t_ms=(\d+)', rm)]
    sec = []   # skips in the second holding presses 2, 3 and 4
    for x in jt[1:4]:
        s_ = [(t1 - t0) - (r1 - r0) for (t0, r0, m0), (t1, r1, m1) in zip(rows, rows[1:]) if m0 < x <= m1]
        sec.append(s_[0] if s_ else None)
    return dict(c=c, kind=kind, valid=not why, why=why, pair=pv, skips=skips,
                disp=(100.0 * (1 - skips / float(PLAY_TICKS)) if skips is not None else None),
                mem=int(mm.group(1)) if mm else None, board=board(c), press234=sec, journeys=len(jt), wit=wit)


def line(x):
    f = lambda v, p='%.2f': ('n/a' if v is None else p % v)
    b = x['board']
    return ('READ %s kind=%s valid=%s%s pair=%s routestamp=%s skips=%s disp=%s%% journeys=%d | watch: partial_waits=%s '
            'pkt_partial=%s pkt_timeout=%s press2/3/4-second skips=%s memory_min_free_kb=%s' % (
                os.path.basename(x['c'].rstrip('/')), x['kind'], 'yes' if x['valid'] else 'no',
                '' if x['valid'] else ' (' + '; '.join(x['why']) + ')', x['pair'],
                'none' if x['wit'] is None else 'allocs=%d,peak=%d' % x['wit'], x['skips'], f(x['disp']), x['journeys'],
                b['partial_waits'] if b else '?', b['pkt_partial'] if b else '?', b['pkt_timeout'] if b else '?',
                '/'.join('?' if v is None else str(v) for v in x['press234']), x['mem']))


def verdict(args):
    cells = [cell(*a.rsplit(':', 1)) for a in args]
    for x in cells:
        print(line(x))
    A = [x for x in cells if x['kind'] == 'A' and x['valid']]
    print('valid A cells: %d' % len(A))
    if len(A) < 2:
        print('0383-CONFIRMS-RR: NOT READ (fewer than 2 valid A cells)'); return
    s = [x['skips'] for x in A]; m = st.mean(s)
    lo, hi = min(RR_F) - SPREAD, max(RR_F) + SPREAD
    mlo, mhi = st.mean(RR_F) - SPREAD, st.mean(RR_F) + SPREAD
    ok = all(lo <= v <= hi for v in s) and mlo <= m <= mhi
    print('0383-CONFIRMS-RR: %s -- A skips %s (mean %.1f); every cell in %d..%d: %s; mean in %.0f..%.0f: %s (RR F %s, mean %.1f)' % (
        'CONSISTENT' if ok else 'INCONSISTENT', s, m, lo, hi, 'yes' if all(lo <= v <= hi for v in s) else 'NO',
        mlo, mhi, 'yes' if mlo <= m <= mhi else 'NO', RR_F, st.mean(RR_F)))
    print('information: displayed %s; MS3 proof bar (a registered pair, both >= 99.0%%): %s' % (
        ', '.join('%.2f%%' % x['disp'] for x in A), 'YES' if all(x['disp'] >= 99.0 for x in A) else 'no'))
    print('information: differences under %d skips are within the pacer\'s same-binary range and are not read' % SPREAD)
    print('what follows: CONSISTENT -> 0383 on main is what round RR measured, recorded; INCONSISTENT -> to sdlports '
          '(an unexpected change between 0382-F and 0383, or the rig), nothing shipped on it')


if __name__ == '__main__':
    if '--stamp-i' in sys.argv:
        i = sys.argv.index('--stamp-i'); STAMP['I'] = sys.argv[i + 1]; del sys.argv[i:i + 2]
    if len(sys.argv) >= 4 and sys.argv[1] == 'cell':
        print(line(cell(sys.argv[2], sys.argv[3])))
    elif len(sys.argv) >= 3 and sys.argv[1] == 'verdict':
        verdict(sys.argv[2:])
    else:
        sys.exit(__doc__)
