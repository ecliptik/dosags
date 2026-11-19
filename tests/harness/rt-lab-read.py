#!/usr/bin/env python3
"""rt-lab-read.py RESULTS_DIR -- round RT's lab check (ROUNDRT README section 7 as replaced by FIX-UP 1 and 2), read from
the five DOSBox-X cells RT-LA, RT-L0, RT-L45, RT-L0S, RT-L45S (scratch rtpace-lab.sh; MS3 restore, release flavour,
fixed timestep, fine timing off, no clicks, exit tick 7000). Read-only. Written and committed before any cell was read.
Registered checks (each prints PASS / FAIL; "info" lines are not checks):
  LA    frames_skipped 5; catchup ticks=5 events=1 clamped=1 resyncs=0; no labpace line.
  L0    labpace stall_ms=0 rebases=0 max_forgiven_short_ticks=0 spins=0.  info: frames_skipped / catchup against LA.
  L45   frames_skipped 0; catchup ticks=0; resyncs 1; labpace stall_ms=45 rebases=1 forgiven_ticks 57..59,
        max_forgiven_ticks = forgiven_ticks, max_forgiven_short_ticks=0, spins=0.
  L0S   precondition: frames_skipped - LA's >= 6 (else the spin checks are VOID); labpace rebases=0 spins=12.
        info: each labspin self_ms.
  L45S  frames_skipped 0; resyncs = labpace rebases = 1 + the spins flagged; every labspin flagged == (self_ms > 45);
        max_forgiven_short_ticks <= 4 and = the largest flagged spin's debt (FIX-UP 2: it equals max_forgiven_ticks over
        the spin rebases, i.e. the restore's ~58 stays out of it: short < max_forgiven_ticks).
  Every cell: rc 0 in CELL.txt, the exe's sha256 (RS0383 = c6824107..., RTPACE as built), ENGINE HAS SHUTDOWN, and the
  manifest stamp printed (RTPACE's becomes build/ws/roundRT/rtpace.STAMP)."""
import os, re, sys
R = sys.argv[1]
WANT = {'RT-LA': 'c68241073cb0dbcc6f0870c22ba31a0d904dd2261e72a44fbb7ba75f6cfb7f43',
        'RT-L0': '57d33a6ef957ce79cdbc4377d1359fd9edd1a8a1b4abc4b6f408d24513b7c067'}
for t in ('RT-L45', 'RT-L0S', 'RT-L45S'):
    WANT[t] = WANT['RT-L0']


def rd(p):
    try:
        return open(p, errors='replace').read()
    except OSError:
        return ''


def load(t):
    d = os.path.join(R, t); rm = rd(d + '/RUNMANI.LOG'); ce = rd(d + '/CELL.txt'); so = rd(d + '/STDOUT.TXT')
    g = lambda pat, conv=int: (lambda m: conv(m.group(1)) if m else None)(re.search(pat, rm))
    lp = re.search(r'DOS-PORT labpace stall_ms=(\d+) rebases=(\d+) forgiven_ticks=(\d+) max_forgiven_ticks=(\d+) '
                   r'max_forgiven_short_ticks=(\d+) spins=(\d+)', rm)
    cu = re.search(r'DOS-PORT catchup ticks=(\d+) events=(\d+) clamped=(\d+) resyncs=(\d+)', rm)
    sp = [dict(x.split('=') for x in m.group(1).split()) for m in re.finditer(r'DOS-PORT labspin (.*)', rm)]
    return dict(t=t, rc=(re.search(r'rc=(\d+)', ce) or [None, None])[1], sha=(re.search(r'sha256=(\w+)', ce) or [None, None])[1],
                load=' '.join(re.findall(r'loadavg_\w+=\S+', ce)), shut='ENGINE HAS SHUTDOWN' in so,
                stamp=(re.search(r'binary_sha12=(\w+)', rm) or [None, None])[1], fs=g(r'frames_skipped=(\d+)'),
                cu=tuple(map(int, cu.groups())) if cu else None, lp=tuple(map(int, lp.groups())) if lp else None,
                anylp='DOS-PORT labpace' in rm, sp=sp, ticks=g(r'tick_rate_steady=[\d.]+ ticks=(\d+)'),
                loop_ms=g(r'tick_rate_steady=[\d.]+ ticks=\d+ stall_ticks=\d+ loop_ms=(\d+)'))


C = {t: load(t) for t in ('RT-LA', 'RT-L0', 'RT-L45', 'RT-L0S', 'RT-L45S')}
res = []


def chk(t, name, ok, got):
    res.append(ok)
    print('%s %s: %s -- %s' % (t, name, 'PASS' if ok else '**FAIL**', got))


for t, c in C.items():
    chk(t, 'ran', c['rc'] == '0' and c['sha'] == WANT[t] and c['shut'], 'rc=%s sha=%s shutdown=%s' % (c['rc'], (c['sha'] or '?')[:16], c['shut']))
    print('%s info: stamp %s; frames_skipped %s; catchup %s; labpace %s; ticks %s loop_ms %s; %s' % (
        t, c['stamp'], c['fs'], c['cu'], c['lp'], c['ticks'], c['loop_ms'], c['load']))
a, z, f, zs, fs = (C[t] for t in ('RT-LA', 'RT-L0', 'RT-L45', 'RT-L0S', 'RT-L45S'))
chk('RT-LA', 'frames_skipped 5, catchup 5/1/1, resyncs 0, no labpace', a['fs'] == 5 and a['cu'] == (5, 1, 1, 0) and not a['anylp'],
    'fs=%s cu=%s labpace=%s' % (a['fs'], a['cu'], a['anylp']))
chk('RT-L0', 'labpace 0/0/short 0/spins 0', bool(z['lp']) and z['lp'][0] == 0 and z['lp'][1] == 0 and z['lp'][4] == 0 and z['lp'][5] == 0, z['lp'])
print('RT-L0 info: frames_skipped %s / catchup %s against LA %s / %s -> %s' % (z['fs'], z['cu'], a['fs'], a['cu'],
      'equal' if (z['fs'], z['cu']) == (a['fs'], a['cu']) else 'DIFFERENT (to sdlports)'))
lp = f['lp']
chk('RT-L45', 'frames_skipped 0, catchup 0, resyncs 1', f['fs'] == 0 and f['cu'] is not None and f['cu'][0] == 0 and f['cu'][3] == 1, 'fs=%s cu=%s' % (f['fs'], f['cu']))
chk('RT-L45', 'labpace 45 / rebases 1 / forgiven 57..59 / max = forgiven / short 0 / spins 0',
    bool(lp) and lp[0] == 45 and lp[1] == 1 and 57 <= lp[2] <= 59 and lp[3] == lp[2] and lp[4] == 0 and lp[5] == 0, lp)
pre = zs['fs'] is not None and a['fs'] is not None and zs['fs'] - a['fs'] >= 6
chk('RT-L0S', 'PRECONDITION frames_skipped - LA >= 6', pre, 'L0S %s - LA %s = %s' % (zs['fs'], a['fs'], (zs['fs'] or 0) - (a['fs'] or 0)))
chk('RT-L0S', 'labpace rebases 0, spins 12', bool(zs['lp']) and zs['lp'][1] == 0 and zs['lp'][5] == 12, zs['lp'])
print('RT-L0S info: spin self_ms %s' % ' '.join('%s:%s' % (s.get('nominal_ms'), s.get('self_ms')) for s in zs['sp']))
if not pre:
    print('RT-L0S / RT-L45S: the spin checks are VOID (precondition failed) -- reported, not worked around')
else:
    lp = fs['lp']; nfl = sum(1 for s in fs['sp'] if s.get('flagged') == '1')
    chk('RT-L45S', 'frames_skipped 0', fs['fs'] == 0, fs['fs'])
    chk('RT-L45S', 'resyncs = labpace rebases = 1 + flagged', bool(lp) and fs['cu'] is not None and lp[1] == 1 + nfl and fs['cu'][3] == lp[1],
        'rebases %s resyncs %s flagged %d' % (lp[1] if lp else None, fs['cu'][3] if fs['cu'] else None, nfl))
    bad = [s for s in fs['sp'] if (s.get('flagged') == '1') != (int(s.get('self_ms', -1)) > 45)]
    chk('RT-L45S', 'every spin flagged == (self_ms > 45)', len(fs['sp']) == 12 and not bad, '%d spins; mismatches %s' % (len(fs['sp']), bad))
    chk('RT-L45S', 'short <= 4 and < max_forgiven (the restore kept out)', bool(lp) and lp[4] <= 4 and lp[4] < lp[3],
        'short %s max %s forgiven %s' % (lp[4] if lp else None, lp[3] if lp else None, lp[2] if lp else None))
    print('RT-L45S info: spin nominal:self:flagged %s' % ' '.join('%s:%s:%s' % (s.get('nominal_ms'), s.get('self_ms'), s.get('flagged')) for s in fs['sp']))
print('LAB CHECK: %d of %d registered checks PASS%s' % (sum(res), len(res), '' if all(res) else ' -- FAILURES above, to sdlports'))
