#!/usr/bin/env bash
# R2DEF release cells (R2LAND's release.sh): P9 equivalence against main's release (0369, 84c1a74fdcf6) and the regression
# set, default (unset = 2) vs =0. --fixed-timestep. Display from the caller (396/397).
set -u; source /home/claude/git/dosags-r2def/build/r2d/lib.sh
W=/home/claude/git/dosags-r2def
REL=$L/exe/R2DREL-A.EXE; MAIN=$L/exe/MAINREL.EXE
C40=$W/tests/harness/confs/dosbox-x-fixed40k-opl3.conf
CFG=$W/tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG
SAVE=/home/claude/git/dosags/build/ws/roundQ/AGSSAVE.007
P9=(--fixed-timestep --conf $C40 --no-verify-present --timeout 2400 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=7436 --env DOSAGS_TICKCLICKS=5500,60,30 --env DOSAGS_RANDSEED=1 --ags-arg --loadsavedgame --ags-arg 7 --include-extra $SAVE:AGSSAVE.007 --include-extra $CFG:ACSETUP.CFG)
D5=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 3 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG)
TN=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 35 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG --env DOSAGS_MSGSKIP=1)
stage() { sed -n 's/^rc=[0-9]* stage=\([^ ]*\) .*/\1/p' $L/results/$1/CELL.txt; }
$L/pcell.sh P9-MAIN-D $MAIN mmd "${P9[@]}"
$L/pcell.sh P9-MAIN-2 $MAIN mmd "${P9[@]}" --env DOSAGS_CHAR_REUSE=2
$L/pcell.sh P9-REL-D $REL mmd "${P9[@]}"
$L/pcell.sh P9-REL-Z $REL mmd "${P9[@]}" --env DOSAGS_CHAR_REUSE=0
for a in D Z; do X=(); [ $a = Z ] && X=(--env DOSAGS_CHAR_REUSE=0)
  $L/pcell.sh RG-5D3S-$a $REL 5days "${D5[@]}" "${X[@]}"
  $L/pcell.sh RG-TN35-$a $REL trilbysnotes "${TN[@]}" "${X[@]}"
  KEEPSTAGE=1 $L/pcell.sh RG-AQ-$a $REL agsquest --timeout 2400 "${X[@]}"
  s=$(stage RG-AQ-$a)
  (cd $W && python3 tests/harness/parse-results.py $s --out-dir $L/results/RG-AQ-$a/pr --tag RGAQ$a > $L/results/RG-AQ-$a/parse.txt 2>&1; echo "parse rc=$?" >> $L/results/RG-AQ-$a/parse.txt)
  case "$s" in /tmp/dos-port-dosbox.?*) rm -rf "$s";; esac
done
echo RELEASE-DONE
