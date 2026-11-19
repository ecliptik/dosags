#!/usr/bin/env python3
"""gates.py RESULTS -- LAB-SW lever-1 gate tables G1-G5 (sha256 only; saves stay local)."""
import os, re, subprocess, sys
R = sys.argv[1]; T = os.path.dirname(os.path.abspath(__file__))
def saves(c):
    d = {}
    p = os.path.join(R, c, 'SAVE-SHA256.txt')
    if os.path.exists(p):
        for l in open(p):
            sha, sz, name = l.split(); d[name.upper()] = (sha, int(sz))
    return d
def wit(c):
    p = os.path.join(R, c, 'STDOUT.TXT')
    if not os.path.exists(p): return []
    return re.findall(r'DOS-PORT savemem DOSAGS_SAVEMEM (mode=\d+ slot=\d+ path=\w+ bytes=\d+ mem=\d+ fallback=\d+ stream=\d+ short=\d+ failknob=\d)', open(p, 'rb').read().decode('latin1'))
def stamp(c):
    p = os.path.join(R, c, 'RUNMANI.LOG')
    s = open(p, 'rb').read().decode('latin1') if os.path.exists(p) else ''
    return ' '.join(sorted(set(re.findall(r'binary_sha12=\w+|build_dirty=\d', s))))
def eq(a, b):
    return subprocess.run([sys.executable, os.path.join(T, 'eqcmp.py'), os.path.join(R, a), os.path.join(R, b)], capture_output=True, text=True).stdout.strip().splitlines()[0]
def fh(a, *b):
    out = subprocess.run([sys.executable, os.path.join(T, 'fhcmp.py'), os.path.join(R, a)] + [os.path.join(R, x) for x in b], capture_output=True, text=True)
    return ' / '.join(l.strip() for l in (out.stdout + out.stderr).strip().splitlines())
print('## G1 byte equality (SAVEMEM=0 vs =1)\n')
print('| fixture | file | =0 sha256 (size) | =1 sha256 (size) | equal | =0 witness | =1 witness |')
print('|---|---|---|---|---|---|---|')
for fx, a, b, f in [('S32P', 'R-S32-m0', 'R-S32-m1', 'AGSSAVE.999'), ('S16', 'R-S16-m0', 'R-S16-m1', 'AGSSAVE.999'),
                    ('S8 Trilby r35', 'R-S8-m0', 'R-S8-m1', 'AGSSAVE.999'), ('MMD title', 'R-MM-m0', 'R-MM-m1', 'AGSSAVE.999'),
                    ('G: normal save slot 1 (deflated)', 'I-G-m0', 'I-G-m1', 'AGSSAVE.001')]:
    sa, sb = saves(a).get(f), saves(b).get(f)
    wa = [w for w in wit(a) if ('slot=%d ' % int(f[-3:])) in w + ' ']; wb = [w for w in wit(b) if ('slot=%d ' % int(f[-3:])) in w + ' ']
    print('| %s | %s | %s | %s | %s | %s | %s |' % (fx, f, '%s (%d)' % sa if sa else '-', '%s (%d)' % sb if sb else '-',
          'EQUAL' if sa and sb and sa == sb else 'DIFF/missing', '; '.join(wa) or '-', '; '.join(wb) or '-'))
print('\n## G3 game output lines and frame digest (=0 vs =1)\n')
for a, b in [('R-S32-m0', 'R-S32-m1'), ('R-S16-m0', 'R-S16-m1'), ('R-S8-m0', 'R-S8-m1'), ('R-MM-m0', 'R-MM-m1'), ('I-G-m0', 'I-G-m1')]:
    print('- ' + eq(a, b))
print('- frame digest, fixture G: ' + fh('I-G-m0', 'I-G-m1'))
print('\n## G4 forced fallback (DOSAGS_LAB_SAVEMEM_FAIL)\n')
print('| cell | file | OFF (=0) sha256 | ON (=1) sha256 | fallback sha256 | equal to OFF | equal to ON | witness |')
print('|---|---|---|---|---|---|---|---|')
for c, off, on, f in [('I-S8-f1', 'R-S8-m0', 'R-S8-m1', 'AGSSAVE.999'), ('I-S8-f2', 'R-S8-m0', 'R-S8-m1', 'AGSSAVE.999'),
                      ('I-Gs-f1', 'I-G-m0', 'I-G-m1', 'AGSSAVE.001'), ('I-Gs-f2', 'I-G-m0', 'I-G-m1', 'AGSSAVE.001')]:
    s0, s1, sf = saves(off).get(f), saves(on).get(f), saves(c).get(f)
    print('| %s | %s | %s | %s | %s | %s | %s | %s |' % (c, f, s0[0][:16] if s0 else '-', s1[0][:16] if s1 else '-', sf[0][:16] if sf else '-',
          'EQUAL' if sf and s0 and sf == s0 else 'DIFF', 'EQUAL' if sf and s1 and sf == s1 else 'DIFF', '; '.join(wit(c)) or '-'))
print('\n## G2 round trips (save with X, restore with Y; vs 0/0)\n')
for base, arms in [('R-S8R-00', ['R-S8R-10', 'R-S8R-01', 'R-S8R-11']), ('I-GR-00', ['I-GR-10', 'I-GR-01', 'I-GR-11'])]:
    for a in arms: print('- ' + eq(base, a))
print('- frame digest, slot-1 restores: ' + fh('I-GR-00', 'I-GR-10', 'I-GR-01', 'I-GR-11'))
print('\n## stamps\n')
for c in sorted(os.listdir(R)):
    if c.startswith(('R-', 'I-')) and os.path.isdir(os.path.join(R, c)): print('- %s: %s' % (c, stamp(c)))
