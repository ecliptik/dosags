#!/usr/bin/env bash
# L1LAND release cells (R2DEF's release.sh): P9 -- 0371's release unset vs 0370's release (r2def R2DREL f9202de6, 9db4170acd89)
# unset, plus 0371 =1 (information); regression -- 0371 off (unset) vs on (=1). --fixed-timestep. Display from the caller.
set -u; source /home/claude/git/dosags-l1land/build/l1/lib.sh
W=/home/claude/git/dosags-l1land
REL=$L/exe/L1REL-A.EXE; PREV=$L/exe/R2DREL.EXE
C40=$W/tests/harness/confs/dosbox-x-fixed40k-opl3.conf
CFG=$W/tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG
SAVE=/home/claude/git/dosags/build/ws/roundQ/AGSSAVE.007
P9=(--fixed-timestep --conf $C40 --no-verify-present --timeout 2400 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=7436 --env DOSAGS_TICKCLICKS=5500,60,30 --env DOSAGS_RANDSEED=1 --ags-arg --loadsavedgame --ags-arg 7 --include-extra $SAVE:AGSSAVE.007 --include-extra $CFG:ACSETUP.CFG)
D5=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 3 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG)
TN=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 35 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG --env DOSAGS_MSGSKIP=1)
stage() { sed -n 's/^rc=[0-9]* stage=\([^ ]*\) .*/\1/p' $L/results/$1/CELL.txt; }
$L/pcell.sh P9-PREV-D $PREV mmd "${P9[@]}"
$L/pcell.sh P9-REL-0 $REL mmd "${P9[@]}"
$L/pcell.sh P9-REL-1 $REL mmd "${P9[@]}" --env DOSAGS_ROUTE_PREWARM=1
for a in 0 1; do X=(); [ $a = 1 ] && X=(--env DOSAGS_ROUTE_PREWARM=1)
  $L/pcell.sh RG-5D3S-$a $REL 5days "${D5[@]}" "${X[@]}"
  $L/pcell.sh RG-TN35-$a $REL trilbysnotes "${TN[@]}" "${X[@]}"
  KEEPSTAGE=1 $L/pcell.sh RG-AQ-$a $REL agsquest --timeout 2400 "${X[@]}"
  s=$(stage RG-AQ-$a)
  (cd $W && python3 tests/harness/parse-results.py $s --out-dir $L/results/RG-AQ-$a/pr --tag RGAQ$a > $L/results/RG-AQ-$a/parse.txt 2>&1; echo "parse rc=$?" >> $L/results/RG-AQ-$a/parse.txt)
  case "$s" in /tmp/dos-port-dosbox.?*) rm -rf "$s";; esac
done
echo RELEASE-DONE
