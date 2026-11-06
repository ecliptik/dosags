#!/usr/bin/env python3
"""docs/lab/s8.md slice 1 scorer: name the long ticks of the S8H protocol (DOSBox-X). LAB ONLY.

s8name.py TICKCELL [TICKCELL ...] --prof PROFCELL --exe PROFEXE

TICKCELL / PROFCELL = s8-cell.sh OUT dirs (the run is OUT/cell; TICKS.BIN and PROF.BIN are copied into OUT/cell
from the cell's own stage before scoring).
Per tick cell: whole-run and steady tick rate (RUNMANI), then every tick with update_game_once > 100 ms and every
tick 50-100 ms, each with its logic/render/scene split and events (room entry R, click C). The room-entry tick is
marked and set apart.
Profile cell: the same list from its own TICKS.BIN; for each tick > 100 ms (and the largest non-entry tick), the
samples between its tick marks by function (nm -n -C), and the share in the DECODE class:
  function name matches (case-insensitive) decode|resampl|vorbis|ogg|mp3|mpg123|pcm|wav|convert_|sample_rate|
  SoundClip|sound_cache|load_sound|audio_clip
Leaf samples in libc (memcpy/memmove/memset/unnamed .text) are reported separately and NOT counted as decode.
"""
import argparse, bisect, collections, glob, os, re, struct, subprocess
NM = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'djgpp', 'bin', 'i586-pc-msdosdjgpp-nm')  # the repo's toolchain symlink
DEC = re.compile(r'decode|resampl|vorbis|ogg|mp3|mpg123|pcm|wav|convert_|sample_rate|soundclip|sound_cache|load_sound|audio_clip', re.I)
FILEIO = re.compile(r'lzw|unpack|decompress|inflate|read|fread|stream|seek|_doprnt|load_', re.I)  # S16 slice: file/decompress
LIBC = re.compile(r'^(\.text|_mem(cpy|move|set|cmp)|big_move|small_move|align_mod_4|___[a-z]*di3)$')

def text(d):
    t = ''
    for f in sorted(glob.glob(os.path.join(d, '*.LOG'))) + [os.path.join(d, 'STDOUT.TXT')]:
        if os.path.exists(f): t += open(f, 'rb').read().decode('latin1') + '\n'
    return t

def ticks(d):
    b = open(os.path.join(d, 'TICKS.BIN'), 'rb').read()
    magic, ver, n, dropped, cap = struct.unpack('<5I', b[:20]); assert magic == 0x474F4C54 and ver == 1
    r = struct.unpack('<%dI' % (2 * n), b[20:20 + 8 * n])
    out = []; cr = cs = 0; ev = ''
    for i in range(n):
        lc, k, v = r[2 * i], r[2 * i + 1] >> 28, r[2 * i + 1] & 0x0FFFFFFF
        if k == 2: cr += v
        elif k == 3: cs += v
        elif k == 4: ev += 'R'
        elif k in (5, 6): ev += 'C'
        elif k == 1:
            out.append(dict(lc=lc, ugo=v / 1000.0, render=cr / 1000.0, scene=cs / 1000.0, logic=(v - cr - cs) / 1000.0, ev=ev))
            cr = cs = 0; ev = ''
    return out, dropped

def listing(name, d):
    t = text(d); T, dropped = ticks(d)
    m = re.search(r'tick_rate_steady=(\S+) ticks=(\d+) stall_ticks=\d+ loop_ms=(\d+)', t)
    wr = int(m.group(2)) / (int(m.group(3)) / 1000.0) if m else float('nan')
    print('%s: ticks=%d dropped=%d  tick_rate whole-run %.2f  steady %s' % (name, len(T), dropped, wr, m.group(1) if m else '?'))
    for i, x in enumerate(T):
        if x['ugo'] >= 50:
            print('  %s tick#%-5d lc=%-6d ugo %7.1f ms = logic %7.1f + render %6.1f + scene %5.1f  events=%s'
                  % ('>100' if x['ugo'] > 100 else '50+ ', i, x['lc'], x['ugo'], x['logic'], x['render'], x['scene'], x['ev'] or '-'))
    return T

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cells', nargs='+'); ap.add_argument('--prof'); ap.add_argument('--exe'); ap.add_argument('--click', type=int, default=0)
    a = ap.parse_args()
    cd = lambda c: os.path.join(c, 'cell') if os.path.isdir(os.path.join(c, 'cell')) else c   # 486 dirs: no cell/
    for c in a.cells: listing(os.path.basename(c.rstrip('/')), cd(c))
    if not a.prof: return
    d = cd(a.prof); T = listing('PROFILE ' + os.path.basename(a.prof.rstrip('/')), d)
    b = open(os.path.join(d, 'PROF.BIN'), 'rb').read()
    h = struct.unpack('<12I', b[:48]); n, ntm = h[4], h[7]
    marks = struct.unpack('<%dI' % ntm, b[48:48 + 4 * ntm])
    s = struct.unpack('<%dI' % n, b[48 + 4 * ntm:48 + 4 * ntm + 4 * n])
    syms = []
    for l in subprocess.run([NM, '-n', '-C', a.exe], capture_output=True, text=True).stdout.splitlines():
        p = l.split(None, 2)
        # 2026-09-26: a .S file's local '.text' shares its function's address; nm -n lists it second, so it masked the name (docs/lab/s8.md)
        if len(p) == 3 and p[1] in 'tTwW' and p[2] != '.text': syms.append((int(p[0], 16), p[2]))
    addrs = [x for x, _ in syms]
    fn = lambda e: syms[bisect.bisect_right(addrs, e) - 1][1] if bisect.bisect_right(addrs, e) else '?'
    nonentry = [x for x in T if 'R' not in x['ev']]
    big = max(nonentry, key=lambda x: x['ugo'])
    for x in [y for y in T if y['ugo'] > 100 or y is big]:
        lc = x['lc']   # the ugo record's loop counter is the tick's end; its samples lie between marks lc-1 and lc
        lo, hi = (marks[lc - 1] if 0 < lc <= ntm else None), (marks[lc] if lc < ntm else None)
        if lo is None or hi is None or hi <= lo:
            print('  lc=%d: no tick-mark window' % lc); continue
        c = collections.Counter(fn(e & 0x1FFFFFFF) if (e & 0x1FFFFFFF) != 1 else '<marker>' for e in s[lo:hi])
        tot = sum(c.values()); dec = sum(k for f, k in c.items() if DEC.search(f)); lib = sum(k for f, k in c.items() if LIBC.search(f))
        print('  lc=%d ugo %.1f ms%s: samples %d  DECODE %.1f%%  libc-leaf %.1f%%  ccInstance::Run %.1f%%'
              % (lc, x['ugo'], '  <- largest non-entry tick' if x is big else '', tot, 100.0 * dec / tot, 100.0 * lib / tot,
                 100.0 * c.get('ccInstance::Run(long)', 0) / tot))
        for f, k in c.most_common(12): print('      %5.1f%%  %5d  %s' % (100.0 * k / tot, k, f[:100]))
    intervals(marks, s, fn)
    clickticks(T, marks, s, fn, ntm)
    if a.click: nthclick(d, a.click, marks, s, fn, ntm)

def intervals(marks, s, fn, top=10):
    # 2026-09-26 addition, before S8PB's data: a blocking script (the opening dialogue) runs nested ticks inside one
    # outer update_game_once, so an outer ugo record spans the whole dialogue (S8T1B: 36.9 s) and is not a stall.
    # The interval between two loop-counter increments is: its sample count ~ its ms (1024 Hz).
    iv = sorted(((marks[i] - marks[i - 1], i) for i in range(1, len(marks)) if marks[i] >= marks[i - 1]), reverse=True)[:top]
    print('  longest loop-counter intervals (samples ~ ms at 1024 Hz):')
    for k, i in iv:
        c = collections.Counter(fn(e & 0x1FFFFFFF) if (e & 0x1FFFFFFF) != 1 else '<marker>' for e in s[marks[i - 1]:marks[i]])
        tot = max(sum(c.values()), 1); dec = sum(v for f, v in c.items() if DEC.search(f)); lib = sum(v for f, v in c.items() if LIBC.search(f))
        fio = sum(v for f, v in c.items() if FILEIO.search(f) and not DEC.search(f)); run = c.get('ccInstance::Run(long)', 0)
        print('   lc %d->%d: %d samples (~%.0f ms)  DECODE %.1f%%  FILEIO %.1f%%  Run %.1f%%  libc-leaf %.1f%%  top: %s'
              % (i - 1, i, k, k * 1000.0 / 1024, 100.0 * dec / tot, 100.0 * fio / tot, 100.0 * run / tot, 100.0 * lib / tot,
                 '; '.join('%s %.0f%%' % (f[:40], 100.0 * v / tot) for f, v in c.most_common(5))))

PATH = re.compile(r'pathfind|walkable|route|ProcessClick|MoveCharacter|MoveToward|navig|find_nearest|can_see|jps|mask|walk_', re.I)

def clickticks(T, marks, s, fn, ntm):
    # 2026-09-26 addition (coordinator: resolve what dominates a click tick), before S16PC/S16WPC data: pool the
    # samples of every tick that dequeued a click (0316 kind 5) and class them: PATH (the walk-path search and the
    # walkable-mask lookups), Run (script VM, e.g. on_mouse_click), DECODE, FILEIO, other.
    tot = collections.Counter(); n = 0; per = []
    for x in T:
        if 'C' not in x['ev']: continue
        lc = x['lc']
        if not (0 < lc < ntm) or marks[lc] <= marks[lc - 1]: continue
        c = collections.Counter(fn(e & 0x1FFFFFFF) if (e & 0x1FFFFFFF) != 1 else '<marker>' for e in s[marks[lc - 1]:marks[lc]])
        tot.update(c); n += 1; per.append((sum(c.values()), lc, c))
    if not n:
        print('  click ticks: none'); return
    t = max(sum(tot.values()), 1)
    cls = lambda f: 'PATH' if PATH.search(f) else 'Run' if f == 'ccInstance::Run(long)' else 'DECODE' if DEC.search(f) else 'FILEIO' if FILEIO.search(f) else 'other'
    cc = collections.Counter()
    for f, v in tot.items(): cc[cls(f)] += v
    print('  click ticks: %d; samples %d (mean %.0f ~ms/tick); classes: %s' % (n, t, t / n, ', '.join('%s %.1f%%' % (k, 100.0 * v / t) for k, v in cc.most_common())))
    for f, v in tot.most_common(15): print('      %5.1f%%  %6d  %s' % (100.0 * v / t, v, f[:100]))
    per.sort(reverse=True)
    for k, lc, c in per[:3]:
        print('    largest click tick lc=%d: %d samples; top: %s' % (lc, k, '; '.join('%s %.0f%%' % (f[:45], 100.0 * v / max(k, 1)) for f, v in c.most_common(5))))

def nthclick(d, k, marks, s, fn, ntm):
    # PROF16 (docs/lab/s8.md): the k-th dequeued click (0316 kind 5, in time order), then the longest loop-counter
    # interval starting within 40 ticks (~1 s) after it, by function, with the PATH / FILEIO / Run / DECODE shares.
    b = open(os.path.join(d, 'TICKS.BIN'), 'rb').read()
    n = struct.unpack('<5I', b[:20])[2]; r = struct.unpack('<%dI' % (2 * n), b[20:20 + 8 * n])
    clicks = [r[2 * i] for i in range(n) if (r[2 * i + 1] >> 28) == 5]
    if len(clicks) < k:
        print('  click #%d: only %d click records' % (k, len(clicks))); return
    lc0 = clicks[k - 1]
    best = max(((marks[i] - marks[i - 1], i) for i in range(max(lc0, 1), min(lc0 + 41, ntm)) if marks[i] >= marks[i - 1]), default=None)
    if not best:
        print('  click #%d at lc %d: no interval' % (k, lc0)); return
    kk, i = best
    c = collections.Counter(fn(e & 0x1FFFFFFF) if (e & 0x1FFFFFFF) != 1 else '<marker>' for e in s[marks[i - 1]:marks[i]])
    t = max(sum(c.values()), 1)
    sh = lambda rx: 100.0 * sum(v for f, v in c.items() if rx.search(f)) / t
    print('  CLICK #%d (lc %d): longest interval lc %d->%d = %d samples (~%.0f ms); PATH %.1f%%  FILEIO %.1f%%  DECODE %.1f%%  Run %.1f%%'
          % (k, lc0, i - 1, i, kk, kk * 1000.0 / 1024, sh(PATH), sh(FILEIO), sh(DEC), 100.0 * c.get('ccInstance::Run(long)', 0) / t))
    for f, v in c.most_common(15): print('      %5.1f%%  %5d  %s' % (100.0 * v / t, v, f[:100]))

if __name__ == '__main__':
    main()
