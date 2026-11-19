#!/usr/bin/env bash
# LAB-R2B lane E (display ${DOSBOX_DISPLAY_NUM}): lab timing (information) on GCL, mode 0 vs 2, same binary.
#   T: fixed timestep, fine timing on, TICKLOG, lab kinds (DOSAGS_LAB_TK=1), checkpoints (LAB-R2's T-cell shape)
#   S: fixed timestep, fine timing off, TICKLOG, no lab kinds (LAB-R2's S-cell shape)
set -u; source /home/claude/git/dosags-lab-r2b/build/r2b/lib.sh
CK=5480,7890,8100,12430
for a in 0 2; do X=(); [ $a = 2 ] && X=(--env DOSAGS_CHAR_REUSE=2)
  FT=1 TL=30000 $L/cell.sh T-$a $GATE 12440 --env DOSAGS_RANDSEED=1 --env DOSAGS_LABCLICKS=GCL --env DOSAGS_LAB_TK=1 --env DOSAGS_LAB_CKPT=$CK "${X[@]}"
done
for a in 0 2; do X=(); [ $a = 2 ] && X=(--env DOSAGS_CHAR_REUSE=2)
  FTOFF=1 TL=30000 $L/cell.sh S-$a $GATE 12440 --env DOSAGS_RANDSEED=1 --env DOSAGS_LABCLICKS=GCL "${X[@]}"
done
echo LANEE-DONE
