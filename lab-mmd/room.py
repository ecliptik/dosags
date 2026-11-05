#!/usr/bin/env python3
"""LAB-MMD: one room segment's figures from a probe run's STDOUT.TXT. Usage: room.py STDOUT.TXT ROOM"""
import re, sys
L = open(sys.argv[1], 'rb').read().decode('latin1').splitlines(); room = sys.argv[2]
kv = lambda l: dict(re.findall(r'(\w+)=(\S+)', l))
pr = [l[l.index('mmdprobe') + 9:] for l in L if 'mmdprobe' in l and ('room=%s ' % room) in l]
cost = [kv(l) for l in pr if l.startswith('cost')][0]; pair = int(cost['pair_ns']) / 1000
seg = [kv(l) for l in pr if l.startswith('seg')][0]; d = [kv(l) for l in pr if l.startswith('dispatch')][0]
tops = [kv(l) for l in pr if l.startswith('dtop')]
for l in pr:
    if l.startswith(('seg', 'dispatch', 'dtop', 'evtype', 'evobj')): print(l[:320])
top = tops[0]; n = int(d['n']) - 1; dus = int(d['us']) - int(top['us'])
print('room %s dispatches excluding the top one: n=%d  %.2f ms/tick; ugo/tick=%.2f ms' % (room, n, dus / 1000 / n, int(seg['ugo_us']) / 1000 / int(seg['ugo_n'])))
for l in pr:
    if l.startswith('entry'):
        e = kv(l); c = int(e['calls'])
        print('  %s calls=%d %.2f ms/call insns/call=%.0f api/call=%.1f nested_us=%s max_us=%s' % (e['name'], c, int(e['us']) / c / 1000, int(e['insns']) / c, int(e['api_n']) / c, e['nested_us'], e['max_us']))
rows = []
for l in pr:
    if l.startswith('api '):
        a = kv(l); rows.append((int(a['us']) - int(a['n']) * pair, a['name'], int(a['n']), int(a['max_us'])))
rows.sort(reverse=True); tot = sum(r[0] for r in rows)
print('  api corrected total %.2f ms/tick' % (tot / 1000 / n))
for c, nm, k, mx in rows[:12]: print('    %-22s %.2f calls/tick %.3f ms/tick max_us=%d' % (nm, k / n, c / 1000 / n, mx))
for l in pr:
    if l.startswith('fn '):
        f = kv(l)
        if int(f['insns']) / n > 50: print('    fn %-40s calls/tick=%.2f insns/tick=%.0f' % (f['name'], int(f['calls']) / n, int(f['insns']) / n))
