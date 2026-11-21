#!/usr/bin/env python3
"""gen-driveRV3.py OUTDIR -- round RV's THIRD power-on (operator, via sdlports' question tool, 2026-11-19: "One more
power-on, 3 runs"): WARMUPRX (WARMUPRV's line), then RV16C (RV16A's line), RV32C (RV32A's line), RV8C (RV8A's line), in a
clean workspace (build/ws/roundRV3). From the second power-on's committed driver and guards (RV2/), which carry the
lock-watch fix (hw-guard-<tag> = GUARD LOCK, recorded, not foreign). Every edit is asserted to apply exactly once."""
import os, sys
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RV2')
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def ed(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


d = open(SRC + '/driveRV2.sh').read().replace('build/ws/roundRV2', 'build/ws/roundRV3')
d = ed(d, '# Round RV, SECOND power-on (gen-driveRV2.py, from driveRV.sh;', '# Round RV, THIRD power-on (gen-driveRV3.py, from RV2/driveRV2.sh;')
d = ed(d, 'for _t in WARMUPRW RV32B RV8B; do', 'for _t in WARMUPRX RV16C RV32C RV8C; do')
d = ed(d, 'echo "round RV2 start', 'echo "round RV3 start')
d = ed(d, 'ccell WARMUPRW mmd 0', 'ccell WARMUPRX mmd 0')
d = d.replace('$RES/WARMUPRW-$D', '$RES/WARMUPRX-$D').replace('WARMUPRW BLASTER', 'WARMUPRX BLASTER').replace('after WARMUPRW', 'after WARMUPRX')
d = ed(d, '''# the two second readings the first power-on did not reach (it stopped after RV16B on the lock-watch false positive)
need RV32B 1520 && s32 RV32B
need RV8B 760 && s8 RV8B
''', '''# the three third readings (RV16B tainted, RV32B's registered witness missing, RV8B late_writes 3): one block, graded
need RV16C 2280 && s16 RV16C
need RV32C 1520 && s32 RV32C
need RV8C 760 && s8 RV8C
''')
d = ed(d, 'echo "ROUND RV2 DONE', 'echo "ROUND RV3 DONE')
d = ed(d, "round RV2's order is not confirmed yet", "round RV3's order is not confirmed yet")
_code = [l for l in d.splitlines() if not l.lstrip().startswith('#')]
_bad = [l for l in _code if 'RV32B' in l or 'WARMUPRW' in l]
assert not _bad, _bad[:3]
open(OUT + '/driveRV3.sh', 'w').write(d); os.chmod(OUT + '/driveRV3.sh', 0o755)

c = open(SRC + '/cellRV.sh').read()
c = ed(c, '# round RV2 copy of roundRV/cellRV.sh (unchanged but for this line).', '# round RV3 copy of the second power-on'"'"'s cellRV.sh (unchanged but for this line).')
open(OUT + '/cellRV.sh', 'w').write(c); os.chmod(OUT + '/cellRV.sh', 0o755)
g = open(SRC + '/powerguard.sh').read().replace('roundRV2', 'roundRV3')
g = ed(g, '# round RV2 (from round RV, unchanged but for the path)', '# round RV3 (from round RV2, unchanged but for the path)')
open(OUT + '/powerguard.sh', 'w').write(g); os.chmod(OUT + '/powerguard.sh', 0o755)
q = open(SRC + '/daemongap.sh').read().replace('roundRV2', 'roundRV3')
q = ed(q, '"$own" == hw-guard-WARMUPRW || "$own" == hw-guard-RV*', '"$own" == hw-guard-WARMUPRX || "$own" == hw-guard-RV*')
q = ed(q, '"$own" != run-hw-WARMUPRW && "$own" != run-hw-RV*', '"$own" != run-hw-WARMUPRX && "$own" != run-hw-RV*')
q = ed(q, "# round RV2 (from round RV's;", "# round RV3 (from round RV2's, unchanged but for the names; as RV2:")
open(OUT + '/daemongap.sh', 'w').write(q); os.chmod(OUT + '/daemongap.sh', 0o755)
for f in ('driveRV3.sh', 'cellRV.sh', 'powerguard.sh', 'daemongap.sh'):
    t = open(OUT + '/' + f).read()
    assert all(ord(ch) < 128 for ch in t), f
    assert 'roundRV2' not in t and 'WARMUPRW' not in t, f
print('generated', OUT)
