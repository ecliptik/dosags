#!/usr/bin/env bash
# LAB-L1R warm cost on the 5 Days gate scenes (release lever exe; lab fixed 40k): S16 = GR16/RDS16's line (+ R2 as RDS16),
# S32P = round WB's line (32-bit 640x480: S32P-ACSETUP-ON.CFG, FORCE_COLOR_DEPTH=32, MAX_SCALE=1, SDL_DOS_PACK24=1). Off / on.
set -u; source /home/claude/git/dosags-lab-rb/docs/lab/l1r-lab/lib.sh
W=/home/claude/git/dosags-lab-rb
C40=$W/tests/harness/confs/dosbox-x-fixed40k-opl3.conf
CFG=$W/tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG
S32CFG=$W/build/l1r/S32P-ACSETUP-ON.CFG   # copy of ~/git/dosags/build/ws/roundWB/S32P-ACSETUP-ON.CFG
S16=(--fixed-timestep --no-fine-timing --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=5000
     --ags-arg --startr --ags-arg 3 --include-extra $CFG:ACSETUP.CFG --env DOSAGS_CHAR_REUSE=2)
S32=(--fixed-timestep --no-fine-timing --conf $C40 --timeout 1500 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=5000
     --ags-arg --startr --ags-arg 3 --include-extra $S32CFG:ACSETUP.CFG --env DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_MAX_SCALE=1 --env SDL_DOS_PACK24=1)
for a in 0 1; do arm $a
  $D/pcell.sh W-S16-$a $REL 5days "${S16[@]}" "${X[@]}"
  $D/pcell.sh W-S32P-$a $REL 5days "${S32[@]}" "${X[@]}"
done
echo CHAINW-DONE
