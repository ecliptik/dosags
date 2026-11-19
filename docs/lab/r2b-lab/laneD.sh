#!/usr/bin/env bash
# LAB-R2B lane D (display 395): the camera-move forcing and the forced baseline (control ii) on G; then release
# regression and P9 equivalence (release exes). Serialized.
set -u; export DOSBOX_DISPLAY_NUM=395; source /home/claude/git/dosags-lab-r2b/build/r2b/lib.sh
arm 2n
# guard (2b), camera move / whole-surface invalidation: invalidate_screen() every 7th scene (room 1 is 320 wide, the camera
# cannot move); N = R2b ignores it
FC_=(--env DOSAGS_LAB_CR_CAM=7)
G G-C-0 "${FC_[@]}"; G G-C-2 "${FC_[@]}" "${X[@]}"; G G-C-N "${FC_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOCAM=1
# control (ii) forced: Dave's draw baseline +1000 on alternate 7-scene windows; N = the key ignores the baseline
FB_=(--env DOSAGS_LAB_CR_BASEL=7)
G G-B-0 "${FB_[@]}"; G G-B-2 "${FB_[@]}" "${X[@]}"; G G-B-N "${FB_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOBASEL=1
# a real camera move: the room camera moved by 1 px every 7th scene where the room is wider (room 2, 960 wide; room 1
# falls back to invalidate_screen())
FC1_=(--env DOSAGS_LAB_CR_CAM=7:1)
G G-C1-0 "${FC1_[@]}"; G G-C1-2 "${FC1_[@]}" "${X[@]}"
# release
W=/home/claude/git/dosags-lab-r2b
REL=$L/exe/R2BREL.EXE; MAIN=$L/exe/MAINREL.EXE
C40=$W/tests/harness/confs/dosbox-x-fixed40k-opl3.conf
CFG=$W/tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG
SAVE=/home/claude/git/dosags/build/ws/roundQ/AGSSAVE.007
P9=(--fixed-timestep --conf $C40 --no-verify-present --timeout 2400 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=7436 --env DOSAGS_TICKCLICKS=5500,60,30 --env DOSAGS_RANDSEED=1 --ags-arg --loadsavedgame --ags-arg 7 --include-extra $SAVE:AGSSAVE.007 --include-extra $CFG:ACSETUP.CFG)
D5=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 3 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG)
TN=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 35 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG --env DOSAGS_MSGSKIP=1)
stage() { sed -n 's/^rc=[0-9]* stage=\([^ ]*\) .*/\1/p' $L/results/$1/CELL.txt; }
$L/pcell.sh P9-MAIN-D $MAIN mmd "${P9[@]}"
$L/pcell.sh P9-REL-0 $REL mmd "${P9[@]}"
$L/pcell.sh P9-REL-2 $REL mmd "${P9[@]}" --env DOSAGS_CHAR_REUSE=2
for a in 0 2; do X=(); [ $a = 2 ] && X=(--env DOSAGS_CHAR_REUSE=2)
  $L/pcell.sh RG-5D3S-$a $REL 5days "${D5[@]}" "${X[@]}"
  $L/pcell.sh RG-TN35-$a $REL trilbysnotes "${TN[@]}" "${X[@]}"
  KEEPSTAGE=1 $L/pcell.sh RG-AQ-$a $REL agsquest --timeout 2400 "${X[@]}"
  s=$(stage RG-AQ-$a)
  (cd $W && python3 tests/harness/parse-results.py $s --out-dir $L/results/RG-AQ-$a/pr --tag RGAQ$a > $L/results/RG-AQ-$a/parse.txt 2>&1; echo "parse rc=$?" >> $L/results/RG-AQ-$a/parse.txt)
  case "$s" in /tmp/dos-port-dosbox.?*) rm -rf "$s";; esac
done
echo LANED-DONE
