#!/usr/bin/env python3
"""gen-driveRT.py OUTDIR -- round RT's driver, cell wrapper and guards from round RS's committed copies
(tests/harness/results/ROUNDRS-2026-11-19). Every edit is asserted to apply exactly once."""
import os, re, sys
SRC = '/home/claude/git/dosags/tests/harness/results/ROUNDRS-2026-11-19'
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def ed(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


d = open(SRC + '/driveRS.sh').read()
head_end = d.index('set -u\n')
d = '''#!/usr/bin/env bash
# Round RT driver (from roundRS/driveRS.sh): the pacer A/B on MS3 (ROUNDRT README, sdlports' review first). A = the ags 0383
# release (rs0383.exe, main's binary, no env switch); P = the same code + tests/harness/apply-pace-rig.py (rtpace.exe,
# release flavour) with DOSAGS_LAB_STALL_MS=45: a top-level tick over 45 ms is a pause, its debt forgiven (0163's rule at
# 45 ms). Round RR's MS3 play line for both (DRIVE 6 ms, exit 12440, AGSSAVE.007, 512x384 cfg ON, --no-fine-timing).
# Read per cell by tests/harness/pa-read.py; the term PACE-MS3 by `pa-read.py verdict` at the end.
# ONE power-on. USB4VC 0.5.109. MS3 target: 99% frames displayed; proof bar a registered pair (RTP1, RTP2), both >= 99.0%,
# with game time lost G <= 2.0% per run in every P cell (operator, 2026-11-19).
# Order: WARMUPRT -> RTCALQ [-> RTCAL on a calq miss] -> RTA1 RTP1 RTP2 RTA2 (the A/B block, ABBA; needed whole) -> RTP3
# (a third P cell: the time rule, never the bar; dropped first on time).
# Every vcctrl call carries </dev/null (sdlports' check, round RS).
''' + d[head_end:].replace('roundRS', 'roundRT').replace('driveRS.sh: STOP', 'driveRT.sh: STOP')
d = ed(d, 'for _t in WARMUPRS RSCALQ RSCAL RSA1 RSA2 RSI1 RSI2 RSA3; do', 'for _t in WARMUPRT RTCALQ RTCAL RTA1 RTP1 RTP2 RTA2 RTP3; do')
d = ed(d, 'declare -A STAMP=([l308.exe]=bc9c3704a839)   # + rs0383.STAMP / rsowl.STAMP below',
       'declare -A STAMP=([l308.exe]=bc9c3704a839)   # + rs0383.STAMP / rtpace.STAMP below')
d = ed(d, 'for _e in rs0383.exe rsowl.exe; do', 'for _e in rs0383.exe rtpace.exe; do')
d = ed(d, "round RS's order is not confirmed yet", "round RT's order is not confirmed yet")
d = ed(d, 'echo "round RS start', 'echo "round RT start')
d = ed(d, 'ccell WARMUPRS mmd', 'ccell WARMUPRT mmd')
d = d.replace('$RES/WARMUPRS-$D', '$RES/WARMUPRT-$D')
d = d.replace('WARMUPRS BLASTER', 'WARMUPRT BLASTER').replace('after WARMUPRS', 'after WARMUPRT')
d = ed(d, '(RSCAL) runs in-round', '(RTCAL) runs in-round')
d = ed(d, 'if need RSCALQ 1520; then', 'if need RTCALQ 1520; then')
d = ed(d, 'ccell RSCALQ mmd 6', 'ccell RTCALQ mmd 6')
d = ed(d, 'presscheck RSCALQ && G=$(gate RSCALQ --recheck "$REF")', 'presscheck RTCALQ && G=$(gate RTCALQ --recheck "$REF")')
d = ed(d, 'ccell RSCAL mmd 6', 'ccell RTCAL mmd 6')
d = ed(d, 'presscheck RSCAL && G2=$(gate RSCAL --no-recentre)', 'presscheck RTCAL && G2=$(gate RTCAL --no-recentre)')
a = d.index('# (c) the A cells'); b = d.index('DONE=()\n')
d = d[:a] + '''# (c) the A/B block: A = the 0383 release (no env switch: main's behaviour); P = rtpace.exe with the 45 ms rule. The play
# gate and the pairing are run and printed for every cell; what VALIDATES a cell is pa-read.py's rule.
PPLAY="$PLAY --env DOSAGS_LAB_STALL_MS=45"
SP=$(cat $B/rtpace.STAMP 2>/dev/null)
play() { local t=$1 kind=$2 exe=$3 ty=$4; shift 4
  DRIVE6_MODE=ms ccell $t mmd 6 $exe 1800 $ty "$@" "${BL[@]}" || return
  presscheck $t || { DONE+=("$RES/$t-$D:$kind"); return; }
  local g; g=$($H/drive6-gate.sh --play "$RES/$t-$D" 2>&1 | tail -1); echo "$t: $g (information)" >> $S
  python3 $H/ms3-pairing.py "$RES/$t-$D" > $RES/$t-$D/PAIRING.txt 2>&1; sed "s/^/$t: /" $RES/$t-$D/PAIRING.txt >> $S
  python3 $H/pa-read.py --stamp-p "$SP" --t-ms 45 cell "$RES/$t-$D" $kind > $RES/$t-$D/READ.txt 2>&1; sed "s/^/$t: /" $RES/$t-$D/READ.txt >> $S
  DONE+=("$RES/$t-$D:$kind"); }
''' + d[b:]
a = d.index('if (( CALOK )); then\n  need RSA1'); b = d.index('fi\n', a) + 3
d = d[:a] + '''if (( CALOK )); then
  need RTA1 3040 && play RTA1 A $B/rs0383.exe 750 $PLAY     # the A/B block is needed whole (A P P A)
  need RTP1 2280 && play RTP1 P $B/rtpace.exe 750 $PPLAY
  need RTP2 1520 && play RTP2 P $B/rtpace.exe 750 $PPLAY
  need RTA2 760 && play RTA2 A $B/rs0383.exe 750 $PLAY
  CUT=0   # the third P cell last, dropped first
  need RTP3 760 && play RTP3 P $B/rtpace.exe 750 $PPLAY
fi
''' + d[b:]
d = ed(d, 'python3 $H/rs-read.py --stamp-i "$SI" verdict "${DONE[@]}"', 'python3 $H/pa-read.py --stamp-p "$SP" --t-ms 45 verdict "${DONE[@]}"')
d = ed(d, 'echo "ROUND RS DONE', 'echo "ROUND RT DONE')
d = d.replace('D=2026-11-19; export CELL_DATE=$D', 'D=2026-11-19; export CELL_DATE=$D')
d = ed(d, '$B/cellRS.sh', '$B/cellRT.sh')
_left = [l for l in d.splitlines()[11:] if re.search(r'\bRS[A-Z0-9]*\b|cellRS|driveRS|round RS', l)]
assert not _left, _left[:5]
assert 'rsowl' not in d and 'rs-read' not in d and 'rs-owed' not in d and 'TPLAY' not in d and 'SI=' not in d
open(OUT + '/driveRT.sh', 'w').write(d); os.chmod(OUT + '/driveRT.sh', 0o755)

c = open(SRC + '/cellRS.sh').read()
c = ed(c, '# round RS copy of roundRR/cellRR.sh (unchanged but for this line).', '# round RT copy of roundRS/cellRS.sh (unchanged but for this line).')
open(OUT + '/cellRT.sh', 'w').write(c); os.chmod(OUT + '/cellRT.sh', 0o755)

g = open(SRC + '/powerguard.sh').read()
g = g.replace('roundRS', 'roundRT')
g = ed(g, '# round RS (from roundRR, unchanged but for the path)', '# round RT (from round RS, unchanged but for the path)'); open(OUT + '/powerguard.sh', 'w').write(g); os.chmod(OUT + '/powerguard.sh', 0o755)
q = open(SRC + '/daemongap.sh').read()
q = ed(q, '# round RS (from roundRR\'s, + the lock watch for the Gateway shared with psdoom)', '# round RT (from roundRS\'s, unchanged but for the round\'s names)')
q = ed(q, '(run-hw-<RS tag>)', '(run-hw-<RT tag>)')
q = ed(q, '"$own" != run-hw-WARMUPRS && "$own" != run-hw-RS*', '"$own" != run-hw-WARMUPRT && "$own" != run-hw-RT*')
q = q.replace('roundRS', 'roundRT').replace("(from roundRT's, unchanged", "(from round RS's, unchanged"); open(OUT + '/daemongap.sh', 'w').write(q); os.chmod(OUT + '/daemongap.sh', 0o755)
for f in ('driveRT.sh', 'cellRT.sh', 'powerguard.sh', 'daemongap.sh'):
    t = open(OUT + '/' + f).read()
    assert all(ord(ch) < 128 for ch in t), f
    assert 'roundRS' not in t.replace('(from roundRS/driveRS.sh)', '').replace("(from roundRS's", '').replace('copy of roundRS/cellRS.sh', ''), f
print('generated', OUT)
