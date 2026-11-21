#!/usr/bin/env python3
"""ry-sim-mk.py RESULTS OUT KERN_RV -- scratch copies of round RV's cells as S2NR at 640x480 2x would leave them, for
ry-read.py's simulation before any RY data (sdlports' review of the RY draft). Never writes into RESULTS.

Every copy: stamp f42436aadd7b, build_dirty=1, PRE/POST sha256 = S2NR, render dest 640x480 2x, and a scale2 line
(on=1 break=0 verify=0 narrow=4985 full=15) in <TAG>.LOG. RV's REAL witness/card-state.log, DRIVE-WALK.LOG and START.UTC
are kept, so the stick rule reads RV's real stick record.

OUT/real/   RV's ten scored cells as B cells, read against the REAL kernel slice (KERN_RV). First power-on cells have
            no kernel coverage (the journal starts 17:49:02Z), so they must read VOID on coverage.
OUT/plant/  planted cases, each read against OUT/plant/kern.txt (KERN_RV plus a planted WINDOW for the first
            power-on, with no drop lines in it), or against its own OUT/plant/<case>/kern.txt for the k* cases:
  pos16 pos32 pos8   RV16A / RV32A / RV8A: read as RV read them
  noscale2           the scale2 line removed -> VOID
  pathoff            narrow=4500 full=500 (90%) -> PATH-OFF
  nopack24           RV32A without the pack24 line -> VOID
  dirtynosha         PRE-STAGE sha256 = PLAIN's -> VOID (build_dirty 1 without the sha witness)
  cardin             a card-state sample "unavailable" at +60 s -> VOID
  cardout            the same at +400 s (outside the play window) -> read normally
  cardage            a "locked" sample with last_frame_age_s=3.1 at +60 s -> VOID
  nocard             witness/card-state.log removed -> VOID
  nowalk             DRIVE-WALK.LOG removed -> VOID
  kstick             a planted kernel "USB disconnect" on the stick's port at +60 s -> VOID
  kunattr            the same on port 1-9, tied to no device -> VOID
  kother             the same on port 1-1, tied to another device (a camera ID line) -> read normally
  norelease          DRIVE-WALK.LOG without its lock-release line -> the window ends at the last run-hw job + 5 s
  noend              the same, and no run-hw job after the lock -> VOID
  noanchor           run-hw.out's trace with no "changing" sample (no exit anchor) -> VOID (window exit)
  a16 / a16bad       RV16A as the A16 anchor: as RV read it / with a scale2 line -> VOID
"""
import datetime
import os
import re
import shutil
import sys

R, O, K = sys.argv[1:4]
SHA = '9599809419c821e0aed4a1740e82f311a07cbea663a4580e7544f892be539043'
PLAIN = 'c68241073cb0dbcc6f0870c22ba31a0d904dd2261e72a44fbb7ba75f6cfb7f43'
S2LINE = ('DOS-PORT scale2 on=1 break=0 verify=0 narrow=4985 full=15 fullfast=15 pal=0 rects=11000 px_src=6000000 '
          'skipcheck=0 rej geom=0 hint=0 fmt=0 nolatch=1 noscene=12 latched=2 norects=0 whole=0 latch_sets=15 '
          'latch_drops=0 vfy=0 vfy_bad=0 vfy_bad_px=0 vfy_first=-1')
DEST = re.compile(r'render dest \([^)]*\)')
CELLS = ['RVDST', 'RV16A', 'RV16B', 'RV16C', 'RV32A', 'RV32B', 'RV32C', 'RV8A', 'RV8B', 'RV8C']


def sub(p, f):
    s = open(p, errors='replace').read()
    open(p, 'w').write(f(s))


def mk(src_tag, dst, s2=True, dest2x=True):
    s = os.path.join(R, src_tag + '-2026-11-19')
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(s, dst, ignore=shutil.ignore_patterns('*.ogg', 'AGSSAVE*', '*.jpg', '*.png', 'frames', 'camera'))
    for r, ds, fs in os.walk(dst):
        for n in ds + fs:
            os.chmod(os.path.join(r, n), 0o755 if n in ds else 0o644)
    log = os.path.join(dst, src_tag + '.LOG')
    sub(log, lambda t: re.sub(r'^binary_sha12=\S+', 'binary_sha12=f42436aadd7b', t, flags=re.M))
    sub(log, lambda t: re.sub(r'^DOS-PORT build_dirty=\d+', 'DOS-PORT build_dirty=1', t, flags=re.M))
    if s2:
        sub(log, lambda t: t.rstrip('\n') + '\n' + S2LINE + '\n')
    for f in ('PRE-STAGE-SHA256.txt', 'POST-RUN-SHA256.txt'):
        open(os.path.join(dst, f), 'w').write('%s  /stage/S2NR.EXE\n' % SHA)
    if dest2x:
        sub(os.path.join(dst, 'STDOUT.TXT'), lambda t: DEST.sub('render dest (0, 0, 639, 479 : 640 x 480)', t))
    return dst


def t0(d, tag):
    dw = open(os.path.join(d, 'DRIVE-WALK.LOG')).read()
    day = open(os.path.join(d, 'START.UTC')).read().strip()[:10]
    m = re.search(r"^(\d\d:\d\d:\d\d\.\d+) lock is run-hw-" + re.escape(tag) + "'s", dw, re.M)
    return datetime.datetime.fromisoformat(day + 'T' + m.group(1)).replace(tzinfo=datetime.timezone.utc)


def card_line(d, tag, dt, state, age):
    from zoneinfo import ZoneInfo
    t = (t0(d, tag) + datetime.timedelta(seconds=dt)).astimezone(ZoneInfo('America/Los_Angeles'))
    ln = '%s state=%s frames=1 last_frame_age_s=%s\n' % (t.strftime('%H%M%S.') + '%03d' % (t.microsecond // 1000), state, age)
    p = os.path.join(d, 'witness', 'card-state.log')
    rows = open(p).read().splitlines(True) + [ln]
    rows.sort(key=lambda x: x.split()[0])
    open(p, 'w').write(''.join(rows))


def kern_line(d, tag, dt, port):
    t = t0(d, tag) + datetime.timedelta(seconds=dt)
    return '%s daemon-host kernel: usb %s: USB disconnect, device number 99\n' % (t.isoformat(timespec='microseconds'), port)


real = os.path.join(O, 'real')
plant = os.path.join(O, 'plant')
for c in CELLS:
    mk(c, os.path.join(real, c + '-2026-11-19'))
kern = open(K).read()
kp = kern + '### WINDOW 2026-11-19 16:20:00 UTC .. 2026-11-19 17:31:00 UTC (UTC) [PLANTED for the sim: no lines]\n'
os.makedirs(plant, exist_ok=True)
P = lambda name, tag: os.path.join(plant, name, tag + '-2026-11-19')
for name, tag in (('pos16', 'RV16A'), ('pos32', 'RV32A'), ('pos8', 'RV8A')):
    mk(tag, P(name, tag))
mk('RV16A', P('noscale2', 'RV16A'), s2=False)
d = mk('RV16A', P('pathoff', 'RV16A'))
sub(os.path.join(d, 'RV16A.LOG'), lambda t: t.replace('narrow=4985 full=15', 'narrow=4500 full=500'))
d = mk('RV32A', P('nopack24', 'RV32A'))
sub(os.path.join(d, 'STDOUT.TXT'), lambda t: re.sub(r'^DOS-PORT pack24 engaged.*\n', '', t, flags=re.M))
d = mk('RV16A', P('dirtynosha', 'RV16A'))
open(os.path.join(d, 'PRE-STAGE-SHA256.txt'), 'w').write('%s  /stage/S2NR.EXE\n' % PLAIN)
d = mk('RV16A', P('cardin', 'RV16A')); card_line(d, 'RV16A', 60, 'unavailable', '2.553')
d = mk('RV16A', P('cardout', 'RV16A')); card_line(d, 'RV16A', 400, 'unavailable', '2.553')
d = mk('RV16A', P('cardage', 'RV16A')); card_line(d, 'RV16A', 60, 'locked', '3.1')
d = mk('RV16A', P('nocard', 'RV16A')); os.remove(os.path.join(d, 'witness', 'card-state.log'))
d = mk('RV16A', P('nowalk', 'RV16A')); os.remove(os.path.join(d, 'DRIVE-WALK.LOG'))
open(os.path.join(plant, 'kern.txt'), 'w').write(kp)
# the kernel plants: each case has its own kernel file (plant/<case>/kern.txt), so no plant leaks into another case
d = mk('RV16A', P('kstick', 'RV16A'))
open(os.path.join(plant, 'kstick', 'kern.txt'), 'w').write(kp + kern_line(d, 'RV16A', 60, '1-2'))
d = mk('RV32A', P('kunattr', 'RV32A'))
open(os.path.join(plant, 'kunattr', 'kern.txt'), 'w').write(kp + kern_line(d, 'RV32A', 60, '1-9'))
d = mk('RV8A', P('kother', 'RV8A'))
open(os.path.join(plant, 'kother', 'kern.txt'), 'w').write(kp + (
    '2026-11-19T16:00:00.000000+00:00 daemon-host kernel: usb 1-1: New USB device found, idVendor=046d, '
    'idProduct=0825, bcdDevice= 0.10\n') + kern_line(d, 'RV8A', 60, '1-1'))
d = mk('RV16A', P('norelease', 'RV16A'))
sub(os.path.join(d, 'DRIVE-WALK.LOG'), lambda t: re.sub(r'^.* lock no longer .*\n', '', t, flags=re.M))
d = mk('RV16A', P('noanchor', 'RV16A'))
sub(os.path.join(d, 'run-hw.out'), lambda t: re.sub(r'^(\s+t\+\s*[\d.]+s\s+)changing', r'\1static', t, flags=re.M))
d = mk('RV16A', P('noend', 'RV16A'))
sub(os.path.join(d, 'DRIVE-WALK.LOG'), lambda t: re.sub(r'^.* lock no longer .*\n', '', t, flags=re.M))
sub(os.path.join(d, 'run-hw.out'), lambda t: re.sub(r'"started_at": [\d.]+', '"started_at": 1000.0', t))
mk('RV16A', P('a16', 'RV16A'), s2=False, dest2x=False)
mk('RV16A', P('a16bad', 'RV16A'), dest2x=False)
print('sim copies ready:', O)
