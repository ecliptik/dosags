#!/usr/bin/env python3
"""LAB-RB tables from one cell's STDOUT.TXT (overlay apply-overlay-rb.py lines).
    rbtab.py CELL_DIR [--from LC]
 1. full latches (rbfull): count by (why, caller tag stack, already, post), with loop-counter ranges
 2. whole-surface presents (rbpfull) and R2b ff_full scenes (rbff): loop-counter ranges
 3. slow / GUI-redraw / route ticks (rbslow), joined with the FindRoute split (rbroute), ms
 4. GUI change marks (rbguimark) and label changes (rblabel), grouped by (gui, code, obj, script position)"""
import collections, re, sys


def ranges(xs):
    out = []
    for x in sorted(set(xs)):
        if out and x <= out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return ' '.join('%d' % a if a == b else '%d-%d' % (a, b) for a, b in out)


def kv(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))


d = sys.argv[1]
lo = int(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 0
L = open(d + '/STDOUT.TXT', 'rb').read().decode('latin1').splitlines()

print('== 1. full latches (rbfull), lc >= %d' % lo)
g = collections.defaultdict(list)
for l in L:
    m = re.search(r'rbfull lc=(\d+) why="([^"]*)" at=(\S+) already=(\d) post=(\d) fn=(\S+)', l)
    if m and int(m.group(1)) >= lo:
        g[(m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))].append(int(m.group(1)))
for k, v in sorted(g.items(), key=lambda kv_: -len(kv_[1])):
    print('%5d  why=%s at=%s already=%s post=%s fn=%s  lc: %s' % (len(v), k[0], k[1], k[2], k[3], k[4], ranges(v)[:200]))

print('\n== 2. whole-surface presents and R2b ff_full scenes')
for tag in ('rbpfull', 'rbff'):
    xs = [int(x) for x in re.findall(tag + r' lc=(\d+)', '\n'.join(L)) if int(x) >= lo]
    print('%s %d: %s' % (tag, len(xs), ranges(xs)[:400]))

print('\n== 3. slow / GUI-redraw / route ticks (ms; rbslow joined with rbroute)')
routes = {}
for l in L:
    if 'rbroute ' in l:
        r = kv(l)
        routes.setdefault(int(r['lc']), []).append(r)
ms = lambda v: '%.1f' % (int(v) / 1000.0)
print('lc us script events scene render gui(ms/n) guis path(ms) irp dij(passes,scans) see(n) fn')
for l in L:
    if 'rbslow ' not in l:
        continue
    r = kv(l)
    lc = int(r['lc'])
    if lc < lo:
        continue
    pr = routes.get(lc, [])
    rs = ';'.join('%s %s(%s,%s) %s(%s)' % (ms(x['irp']), ms(x['dij'].split('/')[0]), x['passes'], x['scans'],
                                          ms(x['see'].split('/')[0]), x['see'].split('/')[1]) for x in pr) or '-'
    gu, gn = r['gui'].split('/')
    print(lc, ms(r['us']), ms(r['script']), ms(r['events']), ms(r['scene']), ms(r['render']), '%s/%s' % (ms(gu), gn),
          r.get('guis', '-'), ms(r['path'].split('/')[0]), rs, r.get('fn', '-'))

print('\n== 4. GUI change marks (rbguimark) and label changes (rblabel), lc >= %d' % lo)
g = collections.defaultdict(list)
for l in L:
    m = re.search(r'rbguimark lc=(\d+) gui=(-?\d+) code=(\d+) obj=(-?\d+) fn=(\S+) pos=(\S+)', l)
    if m and int(m.group(1)) >= lo:
        g[('mark', m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))].append(int(m.group(1)))
    m = re.search(r'rblabel lc=(\d+) gui=(-?\d+) ctrl=(-?\d+) oldlen=\d+ newlen=\d+ fn=(\S+) pos=(\S+)', l)
    if m and int(m.group(1)) >= lo:
        g[('label', m.group(2), '-', m.group(3), m.group(4), m.group(5))].append(int(m.group(1)))
for k, v in sorted(g.items(), key=lambda kv_: -len(kv_[1])):
    print('%5d  %s gui=%s code=%s obj=%s fn=%s pos=%s  lc: %s' % (len(v), k[0], k[1], k[2], k[3], k[4], k[5], ranges(v)[:160]))
