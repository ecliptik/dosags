#!/usr/bin/env python3
"""LAB-L1B: per-symbol samples (script-event bit) from a probe-0306 PROF.BIN, window loop ticks lo..hi.
profsyms.py RESULT_DIR EXE lo hi PATTERN"""
import os, re, struct, subprocess, sys, bisect, collections
T = '/home/claude/git/dosags/tools/djgpp/bin/i586-pc-msdosdjgpp-'
d, exe, lo_t, hi_t, pat = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
raw = open(os.path.join(d, 'PROF.BIN'), 'rb').read()
magic, ver = struct.unpack_from('<2I', raw, 0)
if ver >= 4:
    _, _, hz, rtc, n, lost, dropped, nt, val0, val1, b0, b1 = struct.unpack_from('<12I', raw, 0); hl = 48
else:
    _, _, hz, rtc, n, other, dropped, nt = struct.unpack_from('<8I', raw, 0); hl = 32
marks = struct.unpack_from('<%dI' % nt, raw, hl)
samp = struct.unpack_from('<%dI' % n, raw, hl + 4 * nt)
win = samp[marks[lo_t]:marks[hi_t]]
syms = []
for l in subprocess.run([T + 'nm', '-n', '-C', exe], capture_output=True, text=True).stdout.splitlines():
    m = re.match(r'^([0-9a-f]+) ([Tt]) (.*)$', l)
    if m: syms.append((int(m.group(1), 16), m.group(3)))
addrs = [a for a, _ in syms]
c = collections.Counter(); cs = collections.Counter()
for e in win:
    a = e & 0x1FFFFFFF
    i = bisect.bisect_right(addrs, a) - 1
    s = syms[i][1] if i >= 0 else '?'
    c[s] += 1
    if e & 0x80000000: cs[s] += 1
ticks = hi_t - lo_t
print('hz=%d window %d..%d samples %d script-event %d' % (hz, lo_t, hi_t, len(win), sum(cs.values())))
for s, k in sorted(cs.items(), key=lambda kv: -kv[1]):
    if re.search(pat, s):
        print('%7d %6.3f ms/tick  %s' % (k, k * 1000.0 / hz / ticks, s))
