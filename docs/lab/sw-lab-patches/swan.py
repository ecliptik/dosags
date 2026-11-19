#!/usr/bin/env python3
"""swan.py SWTRACE.TXT [--cluster 32768] -- LAB-SW trace analysis (counts, histogram, extend vs overwrite)."""
import re, sys, collections
path = sys.argv[1]
CL = 32768
if '--cluster' in sys.argv: CL = int(sys.argv[sys.argv.index('--cluster') + 1])
SEC = 512
lines = open(path, encoding='ascii', errors='replace').read().splitlines()
hdr = {}
for l in lines[:20]:
    for k, v in re.findall(r'(\w+)=([-\d.]+)', l):
        hdr.setdefault(k, v)
D = []; F = []; S = []
for l in lines:
    if l.startswith('D '):
        p = l.split(); d = dict(x.split('=') for x in p[3:])
        D.append(dict(t=float(p[1]), dt=float(p[2]), ah=int(d['ah'], 16), al=int(d['al'], 16), bx=int(d['bx']),
                      cx=int(d['cx']), dx=int(d['dx']), cf=int(d['cf']), out=int(d['out'])))
    elif l.startswith('W '):
        p = l.split(); F.append(int(p[3].split('=')[1]))
    elif l.startswith('S '):
        S.append(l)
fd = None
for l in lines:
    if l.startswith('O '): fd = int(l.split()[3].split('=')[1])
byah = collections.Counter(d['ah'] for d in D)
print('save fd', fd, ' int21 by AH:', ' '.join('%02Xh:%d' % (k, v) for k, v in sorted(byah.items())))
seeks = collections.Counter(d['al'] for d in D if d['ah'] == 0x42)
print('42h by AL:', dict(sorted(seeks.items())))
# simulate the DOS file: position + size, from the save handle's own calls
pos = 0; size = None; ext = []; inplace = []; trunc = 0; clusters_alloc = 0; rmw = 0; sectors = 0
w40 = []
for d in D:
    if d['bx'] != fd: continue
    if d['ah'] == 0x42 and not d['cf']:
        pos = d['out'] & 0xffffffff
    elif d['ah'] == 0x40:
        n = d['cx']
        if size is None: size = 0  # created or truncated at open
        if n == 0:
            trunc += 1; size = pos; continue
        w40.append(n)
        end = pos + n
        ov = max(0, min(size, end) - pos); ex = n - ov
        oldcl = (size + CL - 1) // CL; newcl = (max(size, end) + CL - 1) // CL
        clusters_alloc += max(0, newcl - oldcl)
        # partial sectors inside existing data => DOS must hold the old sector (read-modify-write)
        first_sec = pos // SEC; last_sec = (end - 1) // SEC
        sectors += last_sec - first_sec + 1
        for s in {first_sec, last_sec}:
            s0, s1 = s * SEC, (s + 1) * SEC
            partial = pos > s0 or end < s1
            if partial and s0 < size: rmw += 1
        (inplace if ex == 0 else ext).append((pos, n, ov, ex))
        pos = end; size = max(size, end)
print('40h data writes: %d (+%d zero-length truncates); sizes: %s' % (len(w40), trunc, w40))
print('  extending: %d  (bytes %d)   in-place only: %d (bytes %d)   final size %s' % (len(ext), sum(e[1] for e in ext),
      len(inplace), sum(e[1] for e in inplace), size))
print('  clusters allocated (cl=%d): %d ; sectors touched: %d ; partial-sector writes into existing data (RMW candidates): %d'
      % (CL, clusters_alloc, sectors, rmw))
h = collections.Counter()
for n in F:
    b = '1-16' if n <= 16 else '17-511' if n < 512 else '512-4095' if n < 4096 else '4096-8191' if n < 8192 else '8192' if n == 8192 else '>8192'
    h[b] += 1
print('fwrite calls: %d bytes %d histogram %s' % (len(F), sum(F), dict(h)))
print('FileStream seeks: %d' % len(S))
t21 = sum(d['dt'] for d in D) / 1000
tw = sum(d['dt'] for d in D if d['ah'] == 0x40) / 1000; ts = sum(d['dt'] for d in D if d['ah'] == 0x42) / 1000
print('int21 ms total %.2f (40h %.2f, 42h %.2f, other %.2f)' % (t21, tw, ts, t21 - tw - ts))
