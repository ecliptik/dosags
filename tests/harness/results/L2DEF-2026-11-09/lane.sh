#!/usr/bin/env bash
# L2DEF lane (display 398), serialized, one DOSBox-X at a time: gates 1 / 2 (default vs =1, =0 vs 0372's off records)
# on G, V, GCL, H, the intro and AGS Quest; LAB-L2G's controls under the default (C1 marks nothing, C2 rects 1 px short);
# the forced checks under the default and =0 (F1 control move / resize, F2 GUI visibility / transparency, F3 label text,
# F4 slot cap 2); 0373's unknown-value choice (=2, =off: on); the release cells.
set -u; source /home/claude/data/worktrees/dosags-l2def/build/l2d/lib.sh
for a in D 1 Z; do arm $a
  G G-$a "${X[@]}"; V V-$a "${X[@]}"; GCL GCL-$a "${X[@]}"; H H-$a "${X[@]}"; I I-$a "${X[@]}"; Q Q-$a "${X[@]}"
done
arm Dn; H C1-D "${X[@]}" --env DOSAGS_LAB_GC2_NOMARK=1
arm Dn; H C2-D "${X[@]}" --env DOSAGS_LAB_GC2_SHORT=1
for a in D Z; do arm $a
  H F1-$a "${X[@]}" --env DOSAGS_LAB_GC2_MOVE=50
  H F2-$a "${X[@]}" --env DOSAGS_LAB_GC2_VIS=60
  H F3-$a "${X[@]}" --env DOSAGS_LAB_GC2_TEXT=40
  H F4-$a "${X[@]}" --env DOSAGS_LAB_GC2_CAP=2
done
I I-X2 --env DOSAGS_GUI_CTRL_MARK=2
I I-Xoff --env DOSAGS_GUI_CTRL_MARK=off
$L/release.sh
echo LANE-DONE
