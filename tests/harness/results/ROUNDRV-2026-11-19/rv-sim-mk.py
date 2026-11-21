#!/usr/bin/env python3
"""rv-sim-mk.py OUTDIR -- the reader simulation for round RV (sdlports, after f776182d): scratch copies of round V1's
cells, made to look like the v0.1.1 exe's, read by tests/harness/rv-read.py and gatebar.py. Never touches the originals.
  sim1  V1S16 / V1S32 / V1S8 / DIST2 re-stamped f2e183845d2f, with the four default lines v0.1's exe lacks inserted after
        its englev line and every line kind round RS's RSA1 (the 0383 exe) prints that V1's cell has none of (by its first
        two words) inserted before the log's exit_code line / STDOUT's end -> each must read as V1 read it.
  sim2  sim1's S16 copy with one of the six default lines removed (guictrlmark) -> VOID.
  sim3  sim1's S16 copy with the stamp put back to c754df64babd -> VOID.
Names: the copies carry round RV's tags so gatebar finds <TAG>.LOG (RV16A <- V1S16, RV32A <- V1S32, RV8A <- V1S8,
RVDST <- DIST2; sim2 RV16B, sim3 RV32B is not used: sim3 is RV16X)."""
import os, re, shutil, sys
RES = '/home/claude/git/dosags/tests/harness/results'
OUT = sys.argv[1]
NEW = ['DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4',
       'DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2',
       'DOS-PORT guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=1',
       'DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=(default) mode=0']


def key(l):
    return ' '.join(l.split()[:2])


def rl(p):
    return open(p, errors='replace').read().replace('\r\n', '\n').split('\n')


rs_log = rl(RES + '/RSA1-2026-11-19/RUNMANI.LOG')
rs_out = rl(RES + '/RSA1-2026-11-19/STDOUT.TXT')


def make(src, dst_tag, stamp='f2e183845d2f', drop=None):
    s = RES + '/' + src + '-2026-11-06'; stag = src
    d = os.path.join(OUT, dst_tag + '-2026-11-19')
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    for f in ('STDOUT.TXT', 'BLASTER.TXT'):
        shutil.copy(os.path.join(s, f), d)
    log = rl(os.path.join(s, stag + '.LOG')); out = rl(os.path.join(d, 'STDOUT.TXT'))
    lk, ok = set(map(key, log)), set(map(key, out))
    add_log = [l for l in rs_log if l.strip() and key(l) not in lk and not l.startswith('binary_sha12')]
    add_out = [l for l in rs_out if l.strip() and key(l) not in ok and l not in NEW]
    log = [l.replace('binary_sha12=c754df64babd', 'binary_sha12=' + stamp) for l in log]
    i = max(j for j, l in enumerate(log) if l.startswith('exit_code='))
    log = log[:i] + add_log + log[i:]
    j = max(k for k, l in enumerate(out) if l.startswith('DOS-PORT englev '))
    out = out[:j + 1] + NEW + out[j + 1:] + add_out
    if drop:
        out = [l for l in out if not l.startswith(drop)]
    open(os.path.join(d, dst_tag + '.LOG'), 'w').write('\r\n'.join(log))
    open(os.path.join(d, 'STDOUT.TXT'), 'w').write('\r\n'.join(out))
    return len(add_log), len(add_out)


for src, dst in (('V1S16', 'RV16A'), ('V1S32', 'RV32A'), ('V1S8', 'RV8A'), ('DIST2', 'RVDST')):
    print('sim1 %s <- %s: inserted %d log lines, %d STDOUT lines (+4 default lines)' % ((dst, src) + make(src, dst)))
print('sim2 RV16B <- V1S16 without the guictrlmark line: %d / %d' % make('V1S16', 'RV16B', drop='DOS-PORT guictrlmark'))
print('sim3 RV16X <- V1S16 with stamp c754df64babd: %d / %d' % make('V1S16', 'RV16X', stamp='c754df64babd'))
