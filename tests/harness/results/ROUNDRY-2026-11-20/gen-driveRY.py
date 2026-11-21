#!/usr/bin/env python3
"""gen-driveRY.py OUTDIR DATE -- round RY (ROUNDRY-2026-11-20 README): the narrowed 2x present on the 486 at 640x480, one
power-on. From round RV3's committed driver and guards (../ROUNDRV-2026-11-19/RV3/), which carry the lock-watch fix
(hw-guard-<tag> = GUARD LOCK, recorded, not foreign). Every edit is asserted to apply exactly once.

  OUTDIR  the workspace, build/ws/roundRY (driveRY.sh, cellRY.sh, powerguard.sh, daemongap.sh, expected.txt)
  DATE    the launch date (UTC, YYYY-MM-DD). The driver refuses any other day. Each cell's pre-registered README is
          written to tests/harness/results/<TAG>-<DATE>/README.md (a dated "before any data" commit carries them).

Order: WARMUPRY -> RY16B1 RY32B1 RY8B1 (one block, needed whole) -> RY16B2 RY32B2 RY8B2 (one block) -> RY16A (last).
The exe is staged as OUTDIR/s2nr.exe (= S2NR.EXE, sha256 9599809419c8...; manifest stamp f42436aadd7b in s2nr.STAMP).
Staging is a separate step, after sdlports' check; this script writes text files only."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'ROUNDRV-2026-11-19', 'RV3')
RES = os.environ.get('RY_RES_TEST') or os.path.normpath(os.path.join(HERE, '..'))  # RY_RES_TEST: a scratch dir, for a dry run only
OUT, DATE = sys.argv[1], sys.argv[2]
assert re.match(r'^\d{4}-\d\d-\d\d$', DATE), DATE
os.makedirs(OUT, exist_ok=True)
SHA = '9599809419c821e0aed4a1740e82f311a07cbea663a4580e7544f892be539043'
L308 = '425c1609f50ac62cb712109f383e1fff99955d77830f93943dc3d491d849607f'
CFG = '24d874f2c61db7b0027e5b3c192876d4c750520dc237030dd278329621451a17'
TAGS = ['WARMUPRY', 'RY16B1', 'RY32B1', 'RY8B1', 'RY16B2', 'RY32B2', 'RY8B2', 'RY16A']


def ed(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


d = open(SRC + '/driveRV3.sh').read().replace('build/ws/roundRV3', 'build/ws/roundRY')
d = ed(d, '# Round RV, THIRD power-on (gen-driveRV3.py, from RV2/driveRV2.sh; the scored lines are round V1\'s, verbatim): the S8 / S16 / S32P gates on the\n'
          '# v0.1.1 release as shipped.',
       '# Round RY (gen-driveRY.py, from ROUNDRV-2026-11-19/RV3/driveRV3.sh): the narrowed 2x present (SCALE2-NARROW) at the 640x480\n'
       '# 2x rung on S2NR.EXE (s2nr.exe, sha256 9599809419c8..., the exe LAB2X gate3 passed), read by tests/harness/ry-read.py.\n'
       '# Order: WARMUPRY -> RY16B1 RY32B1 RY8B1 -> RY16B2 RY32B2 RY8B2 -> RY16A. The lines below until "Every vcctrl call" are\n'
       '# round RV\'s header, kept as the record of where this driver comes from:\n'
       '# (RV) the S8 / S16 / S32P gates on the\n'
       '# v0.1.1 release as shipped.')
d = ed(d, 'D=2026-11-19; export CELL_DATE=$D', 'D=%s; export CELL_DATE=$D' % DATE)
d = ed(d, 'for _t in WARMUPRX RV16C RV32C RV8C; do', 'for _t in %s; do' % ' '.join(TAGS))
d = ed(d, 'for _e in distv11.exe; do', 'for _e in s2nr.exe; do')
d = ed(d, '# + distv11.STAMP below', '# + s2nr.STAMP below')
d = ed(d, "round RV3's order is not confirmed yet (build/ws/roundRY/ORDER-CONFIRMED missing)",
       "round RY's order is not confirmed yet (build/ws/roundRY/ORDER-CONFIRMED missing)")
d = ed(d, 'cell() { local t=$1; shift; $B/cellRV.sh "$t" "$@"', 'cell() { local t=$1; shift; $B/cellRY.sh "$t" "$@"')
d = ed(d, 'echo "round RV3 start', 'echo "round RY start')
d = ed(d, 'ccell WARMUPRX mmd 0', 'ccell WARMUPRY mmd 0')
d = d.replace('$RES/WARMUPRX-$D', '$RES/WARMUPRY-$D').replace('WARMUPRX BLASTER', 'WARMUPRY BLASTER').replace('after WARMUPRX', 'after WARMUPRY')
# RY stop rule (sdlports, before any data): any stick drop in the warm-up -- its boot, the game's mode set and the exit to
# text mode -- or no live stick record (vcctrl's kernel tee) stops the round before the B blocks: one warm-up lost
# instead of ~85 min of VOID cells.
WARMCHK = '''if [[ "$_vs" != True* ]]; then echo "STOP after WARMUPRY: capture device not present [$_vs]" >> $S; poweroff; exit 1; fi
'''
d = ed(d, WARMCHK, WARMCHK + '''# RY: the warm-up stick rule (README sec. 2): ry-read.py warmup exits 1 on a drop or on no live record
warmstick() { python3 -I $H/ry-read.py --kern $B/KERN-TEE.txt warmup $RES/WARMUPRY-$D >> $S 2>&1; }
if ! warmstick; then echo "STOP after WARMUPRY: stick drop or no live stick record in the warm-up -> power off, report" >> $S; poweroff; exit 1; fi
''')
d = ed(d, '# (b) the gate cells: round V1\'s lines verbatim (DIST2, V1S16, V1S32, V1S8) on distv11.exe. RUNHW_MIN_WAIT_S=270 as V1.\n'
          'E=$B/distv11.exe\n',
       '# (b) the RY cells (README sec. 2) on s2nr.exe. RUNHW_MIN_WAIT_S=270 as V1 / RV.\n'
       'E=$B/s2nr.exe\n')
old_cells = d[d.index('# RVDST and the first readings ran on the first power-on'):d.index('CUT=0\nunset RUNHW_MIN_WAIT_S')]
assert old_cells.count('need RV8C 760 && s8 RV8C') == 1
new_cells = '''CUT=0
# B cells: RV's scene lines at the 640x480 2x rung (S32P-ACSETUP-ON.CFG at every depth: its one difference from
# ACSETUP-ON-512X384-ROUND.CFG is "fullscreen = full_window"), DOSAGS_MAX_SCALE=2, DOSAGS_SCALE2_NARROW=1; the lab
# controls DOSAGS_SCALE2_BREAK / DOSAGS_SCALE2_VERIFY stay unset.
C640="--extra-file $B/S32P-ACSETUP-ON.CFG:ACSETUP.CFG"
N2="--env DOSAGS_MAX_SCALE=2 --env DOSAGS_SCALE2_NARROW=1"
b16() { ccell $1 5days 2 $E 1800 750 --no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 \\
  --ags-arg --startr --ags-arg 3 $C640 $N2 "${BL[@]}"; }
b32() { ccell $1 5days 2 $E 1800 750 --no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 \\
  --ags-arg --startr --ags-arg 3 $C640 $N2 --env DOSAGS_FORCE_COLOR_DEPTH=32 --env SDL_DOS_PACK24=1 "${BL[@]}"; }
b8() { ccell $1 trilbysnotes 3 $E 1800 750 --no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 \\
  --ags-arg --startr --ags-arg 35 $C640 $N2 --env DOSAGS_MSGSKIP=1 "${BL[@]}"; }
# A16: RV16A's line verbatim (1x, 512x384), switch unset; information only
a16() { ccell $1 5days 2 $E 1800 750 --no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 \\
  --ags-arg --startr --ags-arg 3 $CFGON "${BL[@]}"; }
# the first readings: one block, needed whole
need RY16B1 2280 && b16 RY16B1
need RY32B1 1520 && b32 RY32B1
need RY8B1 760 && b8 RY8B1
CUT=0
# the second readings: one block, graded
need RY16B2 2280 && b16 RY16B2
need RY32B2 1520 && b32 RY32B2
need RY8B2 760 && b8 RY8B2
CUT=0
# the information anchor, last (dropped first)
need RY16A 760 && a16 RY16A
'''
d = d.replace(old_cells, new_cells)
d = ed(d, 'echo "ROUND RV3 DONE', 'echo "ROUND RY DONE')
_code = [l for l in d.splitlines() if not l.lstrip().startswith('#')]
_bad = [l for l in _code if re.search(r'RV3|WARMUPRX|distv11|RV16C|RV32C|RV8C|cellRV', l)]
assert not _bad, _bad[:3]
open(OUT + '/driveRY.sh', 'w').write(d)
os.chmod(OUT + '/driveRY.sh', 0o755)

c = open(SRC + '/cellRV.sh').read()
c = ed(c, "# round RV3 copy of the second power-on's cellRV.sh (unchanged but for this line).",
       "# round RY copy of round RV3's cellRV.sh (unchanged but for this line).")
open(OUT + '/cellRY.sh', 'w').write(c)
os.chmod(OUT + '/cellRY.sh', 0o755)
g = open(SRC + '/powerguard.sh').read().replace('roundRV3', 'roundRY')
g = ed(g, '# round RV3 (from round RV2, unchanged but for the path)', '# round RY (from round RV3, unchanged but for the path)')
open(OUT + '/powerguard.sh', 'w').write(g)
os.chmod(OUT + '/powerguard.sh', 0o755)
q = open(SRC + '/daemongap.sh').read().replace('roundRV3', 'roundRY')
q = ed(q, '"$own" == hw-guard-WARMUPRX || "$own" == hw-guard-RV*', '"$own" == hw-guard-WARMUPRY || "$own" == hw-guard-RY*')
q = ed(q, '"$own" != run-hw-WARMUPRX && "$own" != run-hw-RV*', '"$own" != run-hw-WARMUPRY && "$own" != run-hw-RY*')
q = ed(q, "# round RV3 (from round RV2's, unchanged but for the names; as RV2:", "# round RY (from round RV3's, unchanged but for the names; as RV2:")
open(OUT + '/daemongap.sh', 'w').write(q)
os.chmod(OUT + '/daemongap.sh', 0o755)
open(OUT + '/expected.txt', 'w').write('%s  s2nr.exe\n%s  l308.exe\n%s  S32P-ACSETUP-ON.CFG\n' % (SHA, L308, CFG))
for f in ('driveRY.sh', 'cellRY.sh', 'powerguard.sh', 'daemongap.sh', 'expected.txt'):
    t = open(OUT + '/' + f).read()
    assert all(ord(ch) < 128 for ch in t), f
    assert 'roundRV3' not in t and 'WARMUPRX' not in t, f

# the per-cell pre-registrations (at most 15 lines each; PLAN-GATES' claim procedure)
COMMON = [
    '- Binary: s2nr.exe = S2NR.EXE, LAB2X gate3\'s exe (sha256 9599809419c8...; stamp f42436aadd7b, build_dirty=1 accepted only',
    '  with pre-stage = post-run = that sha256). Round RY README sec. 1. VOID otherwise.',
    '- Witness: RV\'s six default STDOUT lines and BLASTER "A220 I7 D3 P330 T3" (README sec. 5); else VOID.',
]
B = COMMON + [
    '- Fixture: RV%s\'s scene line at the 640x480 2x rung: S32P-ACSETUP-ON.CFG (24d874f2...), DOSAGS_MAX_SCALE=2,',
    '  DOSAGS_SCALE2_NARROW=1%s. Witness: the scale2 line on=1 break=0 verify=0, render dest (0, 0, 639, 479 : 640 x 480)%s.',
    '- Bar (owner 01M7XPBAR870HGWWG15X2AAXRV, "Same bar, new rung"): PLAN-GATES\' numbers unchanged at 640x480 integer 2x;',
    '  99% displayed is the REGRESSION line. Read by tests/harness/ry-read.py: MET / NOT MET / PATH-OFF (narrow share',
    '  < 95%, not MET) / VOID.',
    '- Screen witness: the capture stick. A stick drop in the play window (card-state.log or the kernel slice keyed to',
    '  idVendor=0001 idProduct=ff02) VOIDS the cell; a missing record is VOID. No camera fallback (decision 01M7X8X4).%s',
    '- Prediction (information, against RV\'s A readings, cross-day): %s',
    '- With %s this is the depth\'s registered pair on the overlay build S2NR; no release claim (README sec. 8).',
]
SPEC = {
    'RY16B1': ('16A', '', '', '', 'steady 40.0-40.3, fps_p50 40.00, whole-run 39.03-39.38, displayed RV - 0.3..1.5 pp.', 'RY16B2'),
    'RY16B2': ('16A', '', '', '', 'steady 40.0-40.3, fps_p50 40.00, whole-run 39.03-39.38, displayed RV - 0.3..1.5 pp.', 'RY16B1'),
    'RY32B1': ('32A', ', DOSAGS_FORCE_COLOR_DEPTH=32, SDL_DOS_PACK24=1', ', "DOS-PORT pack24 engaged mode=0x0112 640x480"',
               '\n- CLEAN also needs no stale or garbage rectangle at the walker or the cursor (pack24\'s pushed rects).',
               'steady 40.0-40.3, fps_p50 40.00, whole-run 38.88-39.35 (likeliest NOT MET), displayed RV - 0.3..2.5 pp.', 'RY32B2'),
    'RY32B2': ('32A', ', DOSAGS_FORCE_COLOR_DEPTH=32, SDL_DOS_PACK24=1', ', "DOS-PORT pack24 engaged mode=0x0112 640x480"',
               '\n- CLEAN also needs no stale or garbage rectangle at the walker or the cursor (pack24\'s pushed rects).',
               'steady 40.0-40.3, fps_p50 40.00, whole-run 38.88-39.35 (likeliest NOT MET), displayed RV - 0.3..2.5 pp.', 'RY32B1'),
    'RY8B1': ('8A', ', DOSAGS_MSGSKIP=1', '', '', 'steady 40.0-40.3, fps_p50 40.00, whole-run 39.12-39.28, displayed RV - 0.3..1.5 pp.', 'RY8B2'),
    'RY8B2': ('8A', ', DOSAGS_MSGSKIP=1', '', '', 'steady 40.0-40.3, fps_p50 40.00, whole-run 39.12-39.28, displayed RV - 0.3..1.5 pp.', 'RY8B1'),
}
TITLE = {'RY16B': '5 Days S16 (room 3, 16-bit)', 'RY32B': '5 Days S32P (room 3, forced 32-bit, pack24)',
         'RY8B': "Trilby's Notes S8 (room 35, 8-bit, msgskip)"}
for t in TAGS:
    p = os.path.join(RES, '%s-%s' % (t, DATE))
    os.makedirs(p, exist_ok=True)
    if t in SPEC:
        rv, extra, wit, clean, pred, other = SPEC[t]
        head = '# %s -- %s at the 640x480 2x rung, SCALE2-NARROW on S2NR (written %s; round RY; pre-registration, before any data)' % (
            t, TITLE[t[:-1]], DATE)
        body = [x % rv if i == 3 else x for i, x in enumerate(B)]
        body[4] = B[4] % (extra, wit)
        body[9] = B[9] % clean
        body[10] = B[10] % pred
        body[11] = B[11] % other
        body = [head] + body
    elif t == 'RY16A':
        body = ['# RY16A -- 5 Days S16 at 512x384 centred 1x on S2NR, switch unset: information anchor (written %s; round RY; before any data)' % DATE] + COMMON + [
            '- Fixture: RV16A\'s line verbatim (ACSETUP-ON-512X384-ROUND.CFG); DOSAGS_SCALE2_NARROW unset. Witness: no scale2 line,',
            '  render dest (96, 72, 415, 311 : 320 x 240); else VOID.',
            '- Information only, not scored into any pair: S2NR\'s switch-off path on the rig beside RV16A / RV16C (39.40 / 39.38,',
            '  steady 40.16 / 40.14, displayed 99.34 / 99.38%) on c68241073cb0. Camera witness (512x384 does not lock).',
            '- Last cell of the round; dropped first if the cap is short (README sec. 2).']
    else:
        body = ['# WARMUPRY -- rig health and the round\'s first BLASTER read (written %s; round RY; not scored)' % DATE,
                '- WARMUPRV\'s line verbatim (l308.exe, MMD title, 1000 ticks, ACSETUP-OFF-512X384-ROUND.CFG) + a read-only DIR of',
                '  the package dir to PKGDIR.TXT. The driver stops on BLASTER != "A220 I7 D3 P330 T3", a capture STALE other than',
                '  "nolock", or no capture device (round RV\'s rules).']
    txt = '\n'.join(body) + '\n'
    assert all(ord(ch) < 128 for ch in txt), t
    assert len(body) <= 15, (t, len(body))
    open(os.path.join(p, 'README.md'), 'w').write(txt)
print('generated', OUT, 'and the cell READMEs for', DATE)
