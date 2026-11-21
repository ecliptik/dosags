#!/usr/bin/env python3
"""gen-driveRV2.py OUTDIR -- round RV's SECOND power-on (operator, directly, 2026-11-19: "fix and then do the followup
power on to fix the missing runs"): the two second readings the first power-on did not reach (RV32B, RV8B), after a
fresh warm-up (WARMUPRW), in a clean workspace (build/ws/roundRV2). From round RV's committed driver and guards in
this directory. The fix: daemongap.sh's lock watch also accepts run-hw's own recovery identity hw-guard-<this round's
tag> and logs it as "GUARD LOCK <owner>" (recorded, not FOREIGN); any other owner is still FOREIGN and still taints.
Every edit is asserted to apply exactly once."""
import os, sys
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def ed(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


d = open(SRC + '/driveRV.sh').read()
d = d.replace('build/ws/roundRV', 'build/ws/roundRV2').replace('$REPO/build/ws/roundRV;', '$REPO/build/ws/roundRV2;')
d = ed(d, '# Round RV driver (from roundRT/driveRT.sh;', '# Round RV, SECOND power-on (gen-driveRV2.py, from driveRV.sh;')
d = ed(d, 'for _t in WARMUPRV RVDST RV16A RV32A RV8A RV16B RV32B RV8B; do', 'for _t in WARMUPRW RV32B RV8B; do')
d = ed(d, 'echo "round RV start', 'echo "round RV2 start')
d = ed(d, 'ccell WARMUPRV mmd 0', 'ccell WARMUPRW mmd 0')
d = ed(d, "--pre-line 'DIR > PKGDIR.TXT' --collect PKGDIR.TXT", "--pre-line 'DIR > PKGDIR.TXT' --collect PKGDIR.TXT  # as WARMUPRV")
d = d.replace('$RES/WARMUPRV-$D', '$RES/WARMUPRW-$D').replace('WARMUPRV BLASTER', 'WARMUPRW BLASTER').replace('after WARMUPRV', 'after WARMUPRW')
a = d.index('need RVDST 760'); b = d.index('CUT=0\ns16()')
d = d[:a] + '# RVDST and the first readings ran on the first power-on (16:24-17:30Z)\n' + d[b:]
old = '''# the first readings as one block (needed whole), then the second readings as one block (graded: a short round loses
# the last depths' second readings, never a first)
need RV16A 2280 && s16 RV16A
need RV32A 1520 && s32 RV32A
need RV8A 760 && s8 RV8A
CUT=0
need RV16B 2280 && s16 RV16B
need RV32B 1520 && s32 RV32B
need RV8B 760 && s8 RV8B
'''
new = '''# the two second readings the first power-on did not reach (it stopped after RV16B on the lock-watch false positive)
need RV32B 1520 && s32 RV32B
need RV8B 760 && s8 RV8B
'''
d = ed(d, old, new)
d = ed(d, 'echo "ROUND RV DONE', 'echo "ROUND RV2 DONE')
d = ed(d, "round RV's order is not confirmed yet", "round RV2's order is not confirmed yet")
assert 'RV16A' not in d.split('set -u', 1)[1] and 'RVDST' not in d.split('set -u', 1)[1].replace('# RVDST and the first', '')
open(OUT + '/driveRV2.sh', 'w').write(d); os.chmod(OUT + '/driveRV2.sh', 0o755)

c = open(SRC + '/cellRV.sh').read()
c = ed(c, '# round RV copy of roundRT/cellRT.sh (unchanged but for this line).', '# round RV2 copy of roundRV/cellRV.sh (unchanged but for this line).')
open(OUT + '/cellRV.sh', 'w').write(c); os.chmod(OUT + '/cellRV.sh', 0o755)

g = open(SRC + '/powerguard.sh').read().replace('roundRV', 'roundRV2')
g = ed(g, '# round RV (from round RT, unchanged but for the path)', '# round RV2 (from round RV, unchanged but for the path)')
open(OUT + '/powerguard.sh', 'w').write(g); os.chmod(OUT + '/powerguard.sh', 0o755)

q = open(SRC + '/daemongap.sh').read().replace('roundRV', 'roundRV2')
q = ed(q, "# round RV (from round RT's, unchanged but for the round's names): record",
       "# round RV2 (from round RV's; FIX: run-hw's own recovery identity hw-guard-<tag> is the harness, not foreign): record")
q = ed(q, '''  if [[ -n "$own" && "$own" != None && "$own" != run-hw-WARMUPRV && "$own" != run-hw-RV* ]]; then
    [[ "$own" != "$lastown" ]] && echo "$now FOREIGN LOCK $own" >> $L; fi''',
       '''  if [[ "$own" == hw-guard-WARMUPRW || "$own" == hw-guard-RV* ]]; then
    [[ "$own" != "$lastown" ]] && echo "$now GUARD LOCK $own (run-hw's own recovery; recorded, not foreign)" >> $L
  elif [[ -n "$own" && "$own" != None && "$own" != run-hw-WARMUPRW && "$own" != run-hw-RV* ]]; then
    [[ "$own" != "$lastown" ]] && echo "$now FOREIGN LOCK $own" >> $L; fi''')
open(OUT + '/daemongap.sh', 'w').write(q); os.chmod(OUT + '/daemongap.sh', 0o755)
for f in ('driveRV2.sh', 'cellRV.sh', 'powerguard.sh', 'daemongap.sh'):
    t = open(OUT + '/' + f).read()
    assert all(ord(ch) < 128 for ch in t), f
    assert 'ws/roundRV/' not in t and 'ws/roundRV;' not in t, f
print('generated', OUT)
