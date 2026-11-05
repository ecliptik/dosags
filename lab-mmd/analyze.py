#!/usr/bin/env python3
"""LAB-MMD: pull the pre-registered figures out of run directories (STDOUT.TXT + RUNMANI.LOG)."""
import re, sys, os
def kv(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))
def load(d):
    so = open(os.path.join(d, 'STDOUT.TXT'), 'rb').read().decode('latin1').splitlines()
    rm = open(os.path.join(d, 'RUNMANI.LOG'), 'rb').read().decode('latin1').splitlines()
    r = {'dir': d, 'tick': {}, 'probe': [], 'evtype': {}}
    for l in rm:
        m = re.match(r'DOS-PORT tickstats_(\w+) (calls=.*)', l)
        if m: r['tick'][m.group(1)] = kv(m.group(2))
        if l.startswith('DOS-PORT tick_rate_steady'): r['steady'] = kv(l)
        if l.startswith('DOS-PORT tick_rate='): r['rate'] = kv(l)
    for l in so:
        if 'DOS-PORT mmdprobe' in l: r['probe'].append(l[l.index('mmdprobe') + 9:])
        m = re.match(r'.*DOS-PORT evtype (\w+) n=(\d+) us=(\d+)', l)
        if m: r['evtype'][m.group(1)] = (int(m.group(2)), int(m.group(3)))
        m = re.match(r'.*Now in room (-?\d+)', l)
        if m: r.setdefault('rooms', []).append(int(m.group(1)))
    return r
def us(r, k): return int(r['tick'][k]['total_us']) if k in r['tick'] else 0
def calls(r, k): return int(r['tick'][k]['calls']) if k in r['tick'] else 0
for d in sys.argv[1:]:
    r = load(d)
    ticks = int(r['steady']['ticks'])
    sc = r['evtype'].get('script', (0, 0)); fa = r['evtype'].get('fadein', (0, 0))
    disp = us(r, 'process_events_dispatch')
    print('== %s rooms=%s ticks=%d steady=%s rate=%s' % (os.path.basename(d), r.get('rooms'), ticks, r['steady'].get('tick_rate_steady'), r['rate'].get('tick_rate')))
    print('   dispatch %.3f ms/tick (excl fade %.3f) | script-event %.3f ms/tick = %.1f%% of dispatch excl fade | fade %d us | script_vm %.3f ms/tick | rb %.3f ms/call | ugo %.2f ms/tick'
          % (disp / 1000 / ticks, (disp - fa[1]) / 1000 / ticks, sc[1] / 1000 / max(sc[0], 1),
             100.0 * sc[1] / max(disp - fa[1], 1), fa[1], us(r, 'script_vm') / 1000 / ticks,
             us(r, 'render_backbuffer') / 1000 / max(calls(r, 'render_backbuffer'), 1), us(r, 'update_game_once_total') / 1000 / ticks))
    for p in r['probe']:
        if p.startswith(('seg', 'dispatch', 'dtop', 'evtype', 'evobj', 'entry', 'apitotal', 'cost')): print('   ' + p)
    # derived: API time corrected for the empty-pair reading, VM self time, per tick
    cost = [kv(p) for p in r['probe'] if p.startswith('cost')]
    ents = [kv(p) for p in r['probe'] if p.startswith('entry')]
    apit = [kv(p) for p in r['probe'] if p.startswith('apitotal')]
    if cost and ents:
        c = cost[-1]; pair = int(c.get('pair_ns', 0)); apitime = c.get('apitime') == '1'
        for e in ents:
            n = int(e['calls']); u = int(e['us']); a = int(e['api_us']); an = int(e['api_n']); ins = int(e['insns'])
            if n < 50: continue
            corr = max(a - an * pair / 1000.0, 0) if apitime else float('nan')
            print('   DERIVED %s per call: us=%.1f insns=%.0f api_n=%.1f api_us_raw=%.1f api_us_corr=%.1f vm_self_us=%.1f ns/insn=%.0f'
                  % (e['name'], u / n, ins / n, an / n, a / n, corr / n, (u - corr) / n if apitime else u / n,
                     ((u - corr) if apitime else u) * 1000.0 / max(ins, 1)))
    # per-API, corrected by one empty-pair reading per call, per tick
    if cost and cost[-1].get('apitime') == '1':
        pair = int(cost[-1]['pair_ns']) / 1000.0
        rows = []
        for p in r['probe']:
            if p.startswith('api '):
                a = kv(p); n = int(a['n']); u = int(a['us'])
                rows.append((max(u - n * pair, 0), a['name'], n, u))
        rows.sort(reverse=True)
        tot = sum(x[0] for x in rows)
        print('   API corrected total %.1f us/tick over %d calls/tick' % (tot / ticks, sum(x[2] for x in rows) / ticks))
        for c, nm, n, u in rows[:12]:
            print('     %-22s calls/tick=%5.1f corr_us/tick=%6.1f (%.1f us/call, raw %.1f)' % (nm, n / ticks, c / ticks, c / n, u / n))
    fns = [kv(p) for p in r['probe'] if p.startswith('fn ')]
    if fns:
        print('   script functions by exclusive VM instructions per tick:')
        for f in sorted(fns, key=lambda f: -int(f['insns']))[:12]:
            print('     %-40s calls/tick=%5.1f insns/tick=%6.0f api/tick=%5.1f' % (f['name'], int(f['calls']) / ticks, int(f['insns']) / ticks, int(f['api_n']) / ticks))
