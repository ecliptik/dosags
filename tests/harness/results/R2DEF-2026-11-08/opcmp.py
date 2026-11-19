#!/usr/bin/env python3
"""opcmp.py OFF ON -- (cell dirs holding STDOUT.TXT and RUNMANI.LOG) the operation-level control for R2: what the lever
changes, not the picture. Reads, in each arm: the startup witness ("DOS-PORT charreuse DOSAGS_CHAR_REUSE=.. mode=.."),
charreuse_final hits/skips (RUNMANI.LOG), and the running restore / composite / present counters the engine prints
every 500 scenes on STDOUT (bgstruct px = background restored, rbstruct hitpx/fullpx = GUI composite px clipped/full,
dirtypresent px_narrow+px_full = px presented, boxes = present boxes), at the last checkpoint both arms reached.
DIFF when the witness mode, the skips or any of those counts differ."""
import os, re, sys
def rd(d, n):
    p = os.path.join(d, n)
    return open(p, 'rb').read().decode('latin1') if os.path.exists(p) else ''
def kv(line):
    return dict(re.findall(r'(\w+)=(-?\d+)', line))
def load(d):
    out, rm = rd(d, 'STDOUT.TXT'), rd(d, 'RUNMANI.LOG')
    w = re.search(r'DOS-PORT charreuse DOSAGS_CHAR_REUSE=(\S+) mode=(\d)', out)
    f = re.search(r'DOS-PORT charreuse_final (.*)', rm)
    cp = {}
    for k in ('bgstruct', 'rbstruct', 'dirtypresent'):
        for l in out.splitlines():
            if l.startswith('DOS-PORT %s ' % k):
                cp.setdefault(k, []).append(kv(l))
    return w, kv(f.group(1)) if f else {}, cp
def ops(cp, i):
    b, r, p = cp['bgstruct'][i], cp['rbstruct'][i], cp['dirtypresent'][i]
    return {'calls': int(b['calls']), 'restore_px': int(b['px']), 'gui_hitpx': int(r['hitpx']), 'gui_fullpx': int(r['fullpx']),
            'present_px': int(p['px_narrow']) + int(p['px_full']), 'present_boxes': int(p['boxes'])}
a, b = load(sys.argv[1]), load(sys.argv[2])
n = min(len(a[2].get('bgstruct', [])), len(b[2].get('bgstruct', [])), len(a[2].get('dirtypresent', [])), len(b[2].get('dirtypresent', [])))
oa, ob = (ops(a[2], n - 1), ops(b[2], n - 1)) if n else ({}, {})
wa = '%s/m%s' % a[0].groups() if a[0] else 'MISSING'; wb = '%s/m%s' % b[0].groups() if b[0] else 'MISSING'
diff = []
if wa.split('/m')[-1] != wb.split('/m')[-1]: diff.append('witness')
if a[1].get('skips') != b[1].get('skips'): diff.append('skips')
for k in ('restore_px', 'gui_hitpx', 'gui_fullpx', 'present_px', 'present_boxes'):
    if oa.get(k) != ob.get(k): diff.append(k)
print('%s vs %s: witness %s | %s; hits %s | %s; skips %s | %s; at scene checkpoint %s: restore_px %s | %s; '
      'gui_hitpx %s | %s; present_px %s | %s; present_boxes %s | %s -> %s' % (
      sys.argv[1], sys.argv[2], wa, wb, a[1].get('hits'), b[1].get('hits'), a[1].get('skips'), b[1].get('skips'),
      oa.get('calls'), oa.get('restore_px'), ob.get('restore_px'), oa.get('gui_hitpx'), ob.get('gui_hitpx'),
      oa.get('present_px'), ob.get('present_px'), oa.get('present_boxes'), ob.get('present_boxes'),
      ('DIFF (' + ', '.join(diff) + ')') if diff else 'EQUAL'))
