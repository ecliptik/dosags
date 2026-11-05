#!/usr/bin/env python3
"""ophist.py STDOUT.TXT [room]: per-tick opcode histogram from probe 0291, with the asm handler-size estimate."""
import re, sys
L = open(sys.argv[1], 'rb').read().decode('latin1').splitlines()
room = sys.argv[2] if len(sys.argv) > 2 else None
segs = {}; seq = 0; cur = None
for l in L:
    m = re.search(r'DOS-PORT opcount room=(-?\d+) (.*)', l)
    if not m: continue
    r, rest = m.group(1), m.group(2)
    if rest.startswith('why='): seq += 1
    key = '%s#%d' % (r, seq)
    s = segs.setdefault(key, {'hist': {}})
    if rest.startswith('why='):
        s.update(dict(re.findall(r'(\w+)=(\S+)', rest)))
    elif rest.startswith('op='):
        d = dict(re.findall(r'(\w+)=(\S+)', rest)); s['hist'][d['op']] = int(d['n'])
    elif rest.startswith('fixups'):
        s['fix'] = dict(re.findall(r'(\w+)=(\d+)', rest))
    elif rest.startswith('mar_type'):
        d = dict(re.findall(r'(\w+)=(\d+)', rest)); s.setdefault('mar', {})[d['mar_type']] = (int(d['reads']), int(d['writes']))
for r, s in segs.items():
    if room and r.split('#')[0] != room: continue
    t = int(s.get('ticks', 1)) or 1; ops = int(s.get('ops', 0))
    print('== room %s why=%s ticks=%d ops/tick=%.0f argmat/tick=%.0f lsp_calls/tick=%.0f lsp_steps/tick=%.0f fw_steps/tick=%.0f'
          % (r, s.get('why'), t, ops / t, int(s['argmat']) / t, int(s['lsp_calls']) / t, int(s['lsp_steps']) / t, int(s['fw_steps']) / t))
    print('   fixups/tick: ' + ' '.join('%s=%.0f' % (k, int(v) / t) for k, v in s.get('fix', {}).items() if int(v)))
    print('   MAR reads/writes per tick by type: ' + ' '.join('%s:%.0f/%.0f' % (k, a / t, b / t) for k, (a, b) in s.get('mar', {}).items()))
    for op, n in sorted(s['hist'].items(), key=lambda x: -x[1])[:22]:
        print('   %-14s %7.0f /tick  %5.1f%%' % (op, n / t, 100.0 * n / ops))
