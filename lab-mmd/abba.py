#!/usr/bin/env python3
"""LAB-MMD 18.4 ABBA scorer (pre-registered rule; committed before the round it scores).
abba.py A1 B1 B2 A2 [band_lo band_hi]   (result dirs, in run order; band in ms/tick, e.g. -0.65 -0.30)
Metric: 'DOS-PORT evtype script' total us / its event count (999 in the MMD cell), per run.
N = max(|A1-A2|, |B1-B2|); D = mean(B) - mean(A).
Primary (net effect): D < -N GAIN; |D| <= N NO MEASURABLE EFFECT; D > +N REGRESSION. N > 0.3 -> NOISE-BOUND.
Secondary (band): inside -> met; outside by <= N + 0.5 -> consistent with band + layout; else missed.
Also prints each run's binary_sha12, build_dirty and power-on state, so the reader can check the arms."""
import os, re, sys
def one(d):
    t = open(os.path.join(d, 'STDOUT.TXT'), 'rb').read().decode('latin1')
    m = re.search(r'DOS-PORT evtype script n=(\d+) us=(\d+)', t)
    ms = int(m.group(2)) / int(m.group(1)) / 1000.0
    man = open(os.path.join(d, 'RUNMANI.LOG'), 'rb').read().decode('latin1') if os.path.exists(os.path.join(d, 'RUNMANI.LOG')) else ''
    sha = (re.search(r'binary_sha12=(\w+)', man) or [None, '?'])[1]
    dirty = (re.search(r'build_dirty=(\d)', man) or [None, '?'])[1]
    po = '?'
    rh = os.path.join(d, 'run-hw.out')
    if os.path.exists(rh):
        r = open(rh, 'rb').read().decode('latin1')
        m2 = re.search(r'-- powering on --.*?"power_mw":\s*(\d+)', r, re.S)
        po = 'POWER-ON' if (m2 and int(m2.group(1)) == 0) else 'warm'
    return ms, sha, dirty, po
a1, b1, b2, a2 = sys.argv[1:5]
band = (float(sys.argv[5]), float(sys.argv[6])) if len(sys.argv) > 6 else None
R = {k: one(d) for k, d in (('A1', a1), ('B1', b1), ('B2', b2), ('A2', a2))}
for k, (ms, sha, dirty, po) in R.items(): print(f'{k}: {ms:.3f} ms/tick  sha12={sha} build_dirty={dirty} {po}')
A = [R['A1'][0], R['A2'][0]]; B = [R['B1'][0], R['B2'][0]]
N = max(abs(A[0] - A[1]), abs(B[0] - B[1])); D = sum(B) / 2 - sum(A) / 2
print(f'N = {N:.3f}  D = {D:+.3f} ms/tick')
if N > 0.3: print('PRIMARY: NOISE-BOUND (N > 0.3) -- band not scored')
elif D < -N: print('PRIMARY: GAIN')
elif D > N: print('PRIMARY: REGRESSION')
else: print('PRIMARY: NO MEASURABLE EFFECT')
if band and N <= 0.3:
    lo, hi = band
    if lo <= D <= hi: print('SECONDARY: band met')
    elif (D < lo and lo - D <= N + 0.5) or (D > hi and D - hi <= N + 0.5): print('SECONDARY: consistent with band + layout')
    else: print('SECONDARY: band missed')
