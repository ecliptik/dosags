#!/usr/bin/env bash
# LAB-L1R gates G1 (frames, every tick rendered), then controls C1 / F1, then release game lines G2. Serial, display 398.
set -u; source /home/claude/git/dosags-lab-rb/docs/lab/l1r-lab/lib.sh
for a in 0 1; do arm $a
  G G-$a "${X[@]}"; V V-$a "${X[@]}"; GCL GCL-$a "${X[@]}"; H H-$a "${X[@]}"; I I-$a "${X[@]}"; Q Q-$a "${X[@]}"
done
arm 1; H C1-1 "${X[@]}" --env DOSAGS_LAB_RPW_STALE=1
arm 0; H F1-0 "${X[@]}" --env DOSAGS_LAB_RPW_MASKCHG=1
arm 1; H F1-1 "${X[@]}" --env DOSAGS_LAB_RPW_MASKCHG=1
arm 1; H F1-N "${X[@]}" --env DOSAGS_LAB_RPW_MASKCHG=1 --env DOSAGS_LAB_RPW_NOGUARD=1
# release game lines (LAB-R2B lane D's lines; DOSAGS_CHAR_REUSE=2 in both arms)
W=/home/claude/git/dosags-lab-rb
C40=$W/tests/harness/confs/dosbox-x-fixed40k-opl3.conf
CFG=$W/tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG
D5=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 3 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG --env DOSAGS_CHAR_REUSE=2)
TN=(--fixed-timestep --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --ags-arg --startr --ags-arg 35 --env DOSAGS_TAS_AUTO_EXIT_TICK=3000 --env DOSAGS_RANDSEED=1 --include-extra $CFG:ACSETUP.CFG --env DOSAGS_MSGSKIP=1 --env DOSAGS_CHAR_REUSE=2)
stage() { sed -n 's/^rc=[0-9]* stage=\([^ ]*\) .*/\1/p' $L/results/$1/CELL.txt; }
for a in 0 1; do arm $a
  $D/pcell.sh RG-5D3S-$a $REL 5days "${D5[@]}" "${X[@]}"
  $D/pcell.sh RG-TN35-$a $REL trilbysnotes "${TN[@]}" "${X[@]}"
  KEEPSTAGE=1 $D/pcell.sh RG-AQ-$a $REL agsquest --timeout 2400 --env DOSAGS_CHAR_REUSE=2 "${X[@]}"
  s=$(stage RG-AQ-$a)
  (cd $W && python3 tests/harness/parse-results.py $s --out-dir $L/results/RG-AQ-$a/pr --tag RGAQ$a > $L/results/RG-AQ-$a/parse.txt 2>&1; echo "parse rc=$?" >> $L/results/RG-AQ-$a/parse.txt)
  case "$s" in /tmp/dos-port-dosbox.?*) rm -rf "$s";; esac
done
echo CHAING-DONE
