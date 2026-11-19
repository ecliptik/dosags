#!/usr/bin/env bash
# L2LAND lane (display 398), serialized: gate 1 (off vs on) on G, V, GCL, H, the intro and AGS Quest; LAB-L2G's controls
# on H (C1 marks nothing, C2 rects 1 px short); the forced checks on H in both arms (F1 control move / resize, F2 GUI
# visibility / transparency, F3 label text growth, F4 slot cap 2); L1 + L2 together on H (HP-1 vs HP-0); the release cells.
set -u; source /home/claude/git/dosags-l2land/build/l2/lib.sh
for a in 0 1; do arm $a
  G G-$a "${X[@]}"; V V-$a "${X[@]}"; GCL GCL-$a "${X[@]}"; H H-$a "${X[@]}"; I I-$a "${X[@]}"; Q Q-$a "${X[@]}"
done
arm 1n; H C1-1 "${X[@]}" --env DOSAGS_LAB_GC2_NOMARK=1
arm 1n; H C2-1 "${X[@]}" --env DOSAGS_LAB_GC2_SHORT=1
for a in 0 1; do arm $a
  H F1-$a "${X[@]}" --env DOSAGS_LAB_GC2_MOVE=50
  H F2-$a "${X[@]}" --env DOSAGS_LAB_GC2_VIS=60
  H F3-$a "${X[@]}" --env DOSAGS_LAB_GC2_TEXT=40
  H F4-$a "${X[@]}" --env DOSAGS_LAB_GC2_CAP=2
done
H HP-0 --env DOSAGS_ROUTE_PREWARM=1
arm 1; H HP-1 --env DOSAGS_ROUTE_PREWARM=1 "${X[@]}"
$L/release.sh
echo LANE-DONE
