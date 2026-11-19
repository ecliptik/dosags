#!/usr/bin/env bash
# L2DEF release cells (L2LAND's release.sh): P9 -- 0373's release default vs 0372's release (8c123c770d0b) with =1, and
# 0373 =0 vs 0372 unset; regression -- 0373 default (unset) vs =0. --fixed-timestep. Display 398.
set -u; source /home/claude/data/worktrees/dosags-l2def/build/l2d/lib.sh
W=/home/claude/data/worktrees/dosags-l2def
REL=$L/exe/L2DREL-A.EXE; PREV=$L/exe/PREVREL.EXE
C40=$W/tests/harness/confs/dosbox-x-fixed40k-opl3.conf
CFG=$W/tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG
SAVE=/home/claude/git/dosags/build/ws/roundQ/AGSSAVE.007
P9=(--fixed-timestep --conf $C40 --no-verify-present --timeout 2400 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=7436 --env DOSAGS_TICKCLICKS=5500,60,30 --env DOSAGS_RANDSEED=1 --ags-arg --loadsavedgame --ags-arg 7 --include-extra $SAVE:AGSSAVE.007 --include-extra $CFG:ACSETUP.CFG)
D5=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 3 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG)
TN=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 35 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG --env DOSAGS_MSGSKIP=1)
stage() { sed -n 's/^rc=[0-9]* stage=\([^ ]*\) .*/\1/p' $L/results/$1/CELL.txt; }
$L/pcell.sh P9-PREV-D $PREV mmd "${P9[@]}"
$L/pcell.sh P9-PREV-1 $PREV mmd "${P9[@]}" --env DOSAGS_GUI_CTRL_MARK=1
$L/pcell.sh P9-REL-D $REL mmd "${P9[@]}"
$L/pcell.sh P9-REL-Z $REL mmd "${P9[@]}" --env DOSAGS_GUI_CTRL_MARK=0
for a in D Z; do X=(); [ $a = Z ] && X=(--env DOSAGS_GUI_CTRL_MARK=0)
  $L/pcell.sh RG-5D3S-$a $REL 5days "${D5[@]}" "${X[@]}"
  $L/pcell.sh RG-TN35-$a $REL trilbysnotes "${TN[@]}" "${X[@]}"
  KEEPSTAGE=1 $L/pcell.sh RG-AQ-$a $REL agsquest --timeout 2400 "${X[@]}"
  s=$(stage RG-AQ-$a)
  [ -d "$s" ] && (cd $W && python3 tests/harness/parse-results.py $s --out-dir $L/results/RG-AQ-$a/pr --tag RGAQ$a > $L/results/RG-AQ-$a/parse.txt 2>&1; echo "parse rc=$?" >> $L/results/RG-AQ-$a/parse.txt)
  case "$s" in */dos-port-dosbox.?*) rm -rf "$s" "$s.meta";; esac
done
echo RELEASE-DONE
