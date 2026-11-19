#!/usr/bin/env python3
"""LAB-R2: per-frame character log (DOS-PORT r2f lines, detail mode) -> per-character medians and reuse classes.
    r2frames.py CELL_DIR"""
import os, re, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ticks import med

d = sys.argv[1]
t = open(os.path.join(d, 'STDOUT.TXT'), 'rb').read().decode('latin1')
fr = defaultdict(dict)
for line in t.splitlines():
    if 'DOS-PORT r2f ' not in line:
        continue
    kv = dict(re.findall(r'(\w+)=(\S+)', line))
    fr[int(kv['lc'])][int(kv['ch'])] = kv
chs = sorted({c for f in fr.values() for c in f})
print('frames logged %d (lc %d..%d), characters %s' % (len(fr), min(fr), max(fr), chs))
for c in chs:
    rows = [f[c] for f in fr.values() if c in f]
    ks = [r for r in rows if r['ks'] == '1']
    nk = [r for r in rows if r['ks'] != '1']
    paths = defaultdict(int)
    for r in rows: paths[r['path']] += 1
    isd = sum(1 for r in rows if r['is'] == '0'); iss = sum(1 for r in rows if r['is'] == '1')
    ksd = sum(1 for r in ks if r['is'] == '0')
    print('ch %d: frames %d paths %s | key same %d (img same %d, img DIFF %d) | key changed %d | hash same %d diff %d' % (
        c, len(rows), dict(paths), len(ks), sum(1 for r in ks if r['is'] == '1'), ksd, len(nk), iss, isd))
    for nm, S in (('key same', ks), ('key changed', nk)):
        if S:
            print('   %-11s us_c median %.0f mean %.1f | us_p median %.0f mean %.1f | crop changed %d | sizes %s | mir %s | pics %d' % (
                nm, med([int(r['us_c']) for r in S]), sum(int(r['us_c']) for r in S) / len(S),
                med([int(r['us_p']) for r in S]), sum(int(r['us_p']) for r in S) / len(S),
                sum(1 for r in S if r['crop'] == '1'), sorted({r['sz'] for r in S}), sorted({r['mir'] for r in S}),
                len({r['pic'] for r in S})))
    scl = sum(1 for r in rows if r['sz'] != r['sp']); tin = sum(1 for r in rows if r['tint'] != '0/0/0/0/255' or r['lev'] != '0')
    print('   scaled frames %d, tinted/lit frames %d, zoom %s, transparency %s' % (scl, tin, sorted({r['zoom'] for r in rows}),
          sorted({r['tr'] for r in rows})))
allks = sum(1 for f in fr.values() if all(f[c]['ks'] == '1' for c in f))
print('frames with every character key-same: %d of %d (%.1f%%)' % (allks, len(fr), 100.0 * allks / len(fr)))
# runs of Dave moving
