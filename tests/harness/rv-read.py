#!/usr/bin/env python3
"""rv-read.py -- round RV's readings (ROUNDRV-2026-11-19 README section 4): the S8 / S16 / S32P gates on the v0.1.1 exe.
Read-only. Written and simulated before any data (sdlports' review of f776182d).

  rv-read.py [--stamp S] cell DIR LABEL           one cell: gatebar's reading + the witness checks
  rv-read.py [--stamp S] pair LABEL DIR_A DIR_B   a depth's registered pair: MET x2 / MET x1 / NOT MET
  rv-read.py [--stamp S] dist DIR                 RVDST's PASS / FAIL (DIST2's terms)

LABEL: S16 (room 3), S32 (room 3), S8 (room 35, --msgskip). Default stamp f2e183845d2f.
A cell is VOID when gatebar.py voids it (stamp, exit_code, build_dirty, room, a missing field, msgskip) OR when the
witness check fails: STDOUT must carry each of the six default lines below, and BLASTER.TXT must read
"A220 I7 D3 P330 T3". A VOID cell counts as not MET in its pair and is named.
Per cell, beside the verdict: REGRESSION if displayed (1 - frames_skipped / ticks) < 99.0% or any audio counter
(overwrites, underruns, late_writes) is non-zero; and preloop_ms / loop_ms / tail_ms (information).
Every MET is "subject to the screen witness CLEAN" (camera / capture sheet), as gatebar prints."""
import argparse
import contextlib
import importlib.util
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('gatebar', os.path.join(HERE, 'gatebar.py'))
gb = importlib.util.module_from_spec(_s)
_s.loader.exec_module(gb)

WITNESS = ['DOS-PORT vmmode DOSAGS_VM=(default) mode=3',
           'DOS-PORT englev DOSAGS_ENGLEV=(default) on=1',
           'DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4',
           'DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2',
           'DOS-PORT guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=1',
           'DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=(default) mode=0']
BLASTER = 'A220 I7 D3 P330 T3'
ROOM = {'S16': 3, 'S32': 3, 'S8': 35}


def rd(p):
    try:
        return open(p, errors='replace').read()
    except OSError:
        return ''


def cell(d, label, stamp):
    """-> (state, lines) with state in MET / NOT MET / VOID."""
    tag = os.path.basename(d.rstrip('/')).split('-')[0]
    a = argparse.Namespace(stamp=stamp, room=ROOM[label], msgskip=(label == 'S8'))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = gb.cell(d, a)
    lines = buf.getvalue().rstrip('\n').splitlines()
    out = rd(os.path.join(d, 'STDOUT.TXT'))
    log = rd(os.path.join(d, tag + '.LOG'))
    have = set(l.strip() for l in out.splitlines())
    miss = [w for w in WITNESS if w not in have]
    bl = rd(os.path.join(d, 'BLASTER.TXT')).replace('\r', '').strip()
    wv = []
    if miss:
        wv.append('witness line(s) missing: ' + ' | '.join(miss))
    if bl != BLASTER:
        wv.append('BLASTER.TXT [%s] != [%s]' % (bl, BLASTER))
    lines.append('   witness: %s' % ('six default lines + BLASTER OK' if not wv else 'FAIL -- ' + '; '.join(wv)))
    g = lambda k: (re.findall(r'\b' + k + r'=(\d+)', log) or ['?'])[-1]
    lines.append('   start-up (information): preloop_ms %s loop_ms %s tail_ms %s' % (g('preloop_ms'), g('loop_ms'), g('tail_ms')))
    if r is None or wv:
        state = 'VOID'
    else:
        state = 'MET' if r else 'NOT MET'
        fs = re.findall(r'^DOS-PORT tick_rate=[\d.]+ frames_skipped=(\d+)', log, re.M)
        tk = re.findall(r'^DOS-PORT tick_rate_steady=[\d.]+ ticks=(\d+)', log, re.M)
        disp = 100.0 * (1 - int(fs[-1]) / int(tk[-1])) if fs and tk else None
        avs = (re.findall(r'^audio_vital_status=(.*)$', log, re.M) or [''])[-1]
        bad = [k for k in ('overwrites', 'underruns', 'late_writes')
               if int((re.findall(r'\b' + k + r'=(\d+)', avs) or ['0'])[-1])]
        reg = (['displayed %.2f%% < 99.0%%' % disp] if disp is not None and disp < 99.0 else []) + \
              ['%s non-zero' % k for k in bad]
        lines.append('   REGRESSION: %s' % ('; '.join(reg) if reg else 'none'))
    lines.append('READ %s %s: %s' % (os.path.basename(d.rstrip('/')), label, state))
    return state, lines


def main():
    a = sys.argv[1:]
    stamp = 'f2e183845d2f'
    if '--stamp' in a:
        i = a.index('--stamp'); stamp = a[i + 1]; del a[i:i + 2]
    if len(a) == 3 and a[0] == 'cell':
        print('\n'.join(cell(a[1], a[2], stamp)[1]))
    elif len(a) == 4 and a[0] == 'pair':
        lab = a[1]
        if os.path.realpath(a[2]) == os.path.realpath(a[3]):
            sys.exit('pair: the same cell twice')
        st = []
        for d in a[2:]:
            s, ls = cell(d, lab, stamp); st.append((os.path.basename(d.rstrip('/')), s)); print('\n'.join(ls))
        n = sum(1 for _, s in st if s == 'MET')
        v = 'MET x2' if n == 2 else 'MET x1' if n == 1 else 'NOT MET'
        notmet = ', '.join('%s %s' % (t, s) for t, s in st if s != 'MET')
        print('DEPTH %s on %s: %s%s (subject to the screen witness CLEAN in each MET cell)' % (
            lab, stamp, v, (' -- not MET: ' + notmet) if notmet else ''))
    elif len(a) == 2 and a[0] == 'dist':
        d = a[1]
        s, ls = cell(d, 'S16', stamp)
        print('\n'.join(ls))
        out = rd(os.path.join(d, 'STDOUT.TXT'))
        chk = [('fixed timestep on', 'DOS-PORT fixed-timestep: ENABLED' in out),
               ('OPL3 detected', 'DosMidiBackend: OPL3/OPL2 chip detected' in out),
               ('music 0', bool(re.search(r'Playing music 0\b', out))),
               ('>= 1 Playing sound', len(re.findall(r'Playing sound \d+', out)) >= 1),
               ('gatebar S16 MET + witness', s == 'MET')]
        for k, ok in chk:
            print('   %s: %s' % (k, 'yes' if ok else 'NO'))
        print('RVDST-TERM %s: %s (subject to the camera sheet CLEAN)' % (
            os.path.basename(d.rstrip('/')), 'PASS' if all(ok for _, ok in chk) else
            'VOID' if s == 'VOID' else 'FAIL'))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
