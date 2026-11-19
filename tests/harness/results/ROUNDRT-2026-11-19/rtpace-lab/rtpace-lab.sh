#!/usr/bin/env bash
# round RT's lab check (ROUNDRT README section 7 + FIX-UP 1 / 2): MS3 restore, release flavour, fixed timestep with fine
# timing off (the rig's line: run-hw.sh sets DOSAGS_FIXED_TIMESTEP=1; --no-fine-timing), no clicks, exit tick 7000.
# Five cells, serial, lane 398 (cellrk.sh: refuses while another emulator or a compile runs; load averages in CELL.txt).
unset TMPDIR
E=/home/claude/data/worktrees/dosags-lab-pace/build/move/exe
CK=/home/claude/data/tmp/claude-1001/-home-claude-git-dosags/8d15788e-024f-45ef-9590-8caefc025dbf/scratchpad/lab/cellrk.sh
SPIN=5600:40,5700:60,5800:80,5900:120,6000:40,6100:60,6200:80,6300:120,6400:40,6500:60,6600:80,6700:120
cell() { tag=$1; exe=$2; shift 2
  for k in $(seq 1 120); do [ "$(pgrep -c -x dosbox-x)" = 0 ] && [ "$(pgrep -c -x cc1plus)" = 0 ] && break; sleep 30; done
  FTOFF=1 TMO=3000 $CK $tag $exe 7000 --env DOSAGS_RANDSEED=1 "$@"
  echo "$tag rc=$?"; }
cell RT-LA  $E/RS0383.EXE
cell RT-L0  $E/RTPACE.EXE
cell RT-L45 $E/RTPACE.EXE --env DOSAGS_LAB_STALL_MS=45
cell RT-L0S $E/RTPACE.EXE --env DOSAGS_LAB_SPIN=$SPIN
cell RT-L45S $E/RTPACE.EXE --env DOSAGS_LAB_STALL_MS=45 --env DOSAGS_LAB_SPIN=$SPIN
echo RTLAB-DONE
