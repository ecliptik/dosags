#!/usr/bin/env python3
"""gen-driveRV.py OUTDIR -- round RV's driver, cell wrapper and guards from round RT's committed copies
(tests/harness/results/ROUNDRT-2026-11-19); the scored cells are round V1's gate lines verbatim
(tests/harness/results/ROUNDV1-2026-11-06/driveV1.sh) on the v0.1.1 zip's AGS.EXE. Every edit is asserted to apply
exactly once."""
import os, re, sys
SRC = '/home/claude/git/dosags/tests/harness/results/ROUNDRT-2026-11-19'
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def ed(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


TAGS = 'WARMUPRV RVDST RV16A RV32A RV8A RV16B RV32B RV8B'
d = open(SRC + '/driveRT.sh').read()
head_end = d.index('set -u\n')
d = '''#!/usr/bin/env bash
# Round RV driver (from roundRT/driveRT.sh; the scored lines are round V1's, verbatim): the S8 / S16 / S32P gates on the
# v0.1.1 release as shipped. distv11.exe = AGS.EXE extracted from dosags-v0.1.1.zip (sha256 e36ef5f9...) = release
# f2e183845d2f (sha256 c68241073cb0...), the exe rounds RS / RT measured as their A cells. ONE power-on. USB4VC 0.5.109.
# Order: WARMUPRV (l308; + a read-only listing of the package dir) -> RVDST (DIST2's line: README.TXT's settings) ->
# RV16A RV32A RV8A (first readings) -> RV16B RV32B RV8B (second readings). Each depth's registered pair is <depth>A + B.
# Scored after the round by tests/harness/gatebar.py (PLAN-GATES bar); the driver gates nothing but rig health.
# Every vcctrl call carries </dev/null (sdlports' check, round RS).
''' + d[head_end:].replace('roundRT', 'roundRV').replace('driveRT.sh: STOP', 'driveRV.sh: STOP')
d = ed(d, 'CAP_MIN=120   # minutes of mains-on time from relay-on (expected ~80, ~91 with a full cal; the README\'s arithmetic)',
       'CAP_MIN=120   # minutes of mains-on time from relay-on (expected ~85; the README\'s arithmetic)')
d = ed(d, 'for _t in WARMUPRT RTCALQ RTCAL RTA1 RTP1 RTP2 RTA2 RTP3; do', 'for _t in %s; do' % TAGS)
d = ed(d, 'declare -A STAMP=([l308.exe]=bc9c3704a839)   # + rs0383.STAMP / rtpace.STAMP below',
       'declare -A STAMP=([l308.exe]=bc9c3704a839)   # + distv11.STAMP below')
d = ed(d, 'for _e in rs0383.exe rtpace.exe; do', 'for _e in distv11.exe; do')
d = ed(d, "round RT's order is not confirmed yet", "round RV's order is not confirmed yet")
d = ed(d, '$B/cellRT.sh', '$B/cellRV.sh')
# presscheck stays defined (unused): no DRIVE 6 cell in this round
d = ed(d, 'echo "round RT start', 'echo "round RV start')
d = ed(d, 'ccell WARMUPRT mmd 0 $B/l308.exe 1500 480 $MM "${BL[@]}"',
       '# + a read-only listing of the package dir (the start-up lead of round V1: every cell leaves its <TAG>.LOG there)\n'
       'ccell WARMUPRV mmd 0 $B/l308.exe 1500 480 $MM "${BL[@]}" --pre-line \'DIR > PKGDIR.TXT\' --collect PKGDIR.TXT')
d = d.replace('$RES/WARMUPRT-$D', '$RES/WARMUPRV-$D')
d = d.replace('WARMUPRT BLASTER', 'WARMUPRV BLASTER').replace('after WARMUPRT', 'after WARMUPRV')
a = d.index('# (b) DRIVE 6 calibration'); b = d.index('unset RUNHW_MIN_WAIT_S\n')
d = d[:a] + '''# (b) the gate cells: round V1's lines verbatim (DIST2, V1S16, V1S32, V1S8) on distv11.exe. RUNHW_MIN_WAIT_S=270 as V1.
E=$B/distv11.exe
need RVDST 760 && ccell RVDST 5days 2 $E 1800 750 --no-fixed-timestep --no-fine-timing \\
  --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 3 \\
  --extra-file $H/presentation/dist/ACSETUP-README.CFG:ACSETUP.CFG "${BL[@]}"
CUT=0
s16() { ccell $1 5days 2 $E 1800 750 --no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 \\
  --ags-arg --startr --ags-arg 3 $CFGON "${BL[@]}"; }
s32() { ccell $1 5days 2 $E 1800 750 --no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 \\
  --ags-arg --startr --ags-arg 3 --extra-file $B/S32P-ACSETUP-ON.CFG:ACSETUP.CFG \\
  --env DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_MAX_SCALE=1 --env SDL_DOS_PACK24=1 "${BL[@]}"; }
S8=(--no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 35
  --extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG --env DOSAGS_MSGSKIP=1)
s8() { ccell $1 trilbysnotes 3 $E 1800 750 "${S8[@]}" "${BL[@]}"; }
# the first readings as one block (needed whole), then the second readings as one block (graded: a short round loses
# the last depths' second readings, never a first)
need RV16A 2280 && s16 RV16A
need RV32A 1520 && s32 RV32A
need RV8A 760 && s8 RV8A
CUT=0
need RV16B 2280 && s16 RV16B
need RV32B 1520 && s32 RV32B
need RV8B 760 && s8 RV8B
CUT=0
''' + d[b:]
d = ed(d, 'echo "ROUND RT DONE', 'echo "ROUND RV DONE')
assert 'pa-read' not in d and 'rtpace' not in d and 'rs0383' not in d and 'DRIVE6_MODE' not in d and 'PPLAY' not in d
_left = [l for l in d.splitlines()[9:] if re.search(r'\bRT[A-Z0-9]*\b|cellRT|driveRT|round RT', l)]
assert not _left, _left[:5]
open(OUT + '/driveRV.sh', 'w').write(d); os.chmod(OUT + '/driveRV.sh', 0o755)

c = open(SRC + '/cellRT.sh').read()
c = ed(c, '# round RT copy of roundRS/cellRS.sh (unchanged but for this line).', '# round RV copy of roundRT/cellRT.sh (unchanged but for this line).')
open(OUT + '/cellRV.sh', 'w').write(c); os.chmod(OUT + '/cellRV.sh', 0o755)

g = open(SRC + '/powerguard.sh').read()
g = g.replace('roundRT', 'roundRV')
g = ed(g, '# round RT (from round RS, unchanged but for the path)', '# round RV (from round RT, unchanged but for the path)')
open(OUT + '/powerguard.sh', 'w').write(g); os.chmod(OUT + '/powerguard.sh', 0o755)
q = open(SRC + '/daemongap.sh').read()
q = ed(q, "# round RT (from round RS's, unchanged but for the round's names): record", "# round RV (from round RT's, unchanged but for the round's names): record")
q = ed(q, '(run-hw-<RT tag>)', '(run-hw-<RV tag>)')
q = ed(q, '"$own" != run-hw-WARMUPRT && "$own" != run-hw-RT*', '"$own" != run-hw-WARMUPRV && "$own" != run-hw-RV*')
q = q.replace('roundRT', 'roundRV')
open(OUT + '/daemongap.sh', 'w').write(q); os.chmod(OUT + '/daemongap.sh', 0o755)
for f in ('driveRV.sh', 'cellRV.sh', 'powerguard.sh', 'daemongap.sh'):
    t = open(OUT + '/' + f).read()
    assert all(ord(ch) < 128 for ch in t), f
    assert 'roundRT' not in t.replace('(from roundRT/driveRT.sh', '').replace("(from roundRT's", '').replace('copy of roundRT/cellRT.sh', ''), f
print('generated', OUT)
