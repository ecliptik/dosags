#!/usr/bin/env bash
# L1LAND lane 1 (display 396), serialized: gate 1 (off vs on) on G, GCL and H; LAB-L1R's controls on H (C1 stale warm,
# F1 mask change after the warm in both arms, F1-N the guard defeated); 0371's unknown-value choice (=on, =2: off).
set -u; export DOSBOX_DISPLAY_NUM=396; source /home/claude/git/dosags-l1land/build/l1/lib.sh
for a in 0 1; do arm $a; G G-$a "${X[@]}"; done
for a in 0 1; do arm $a; H H-$a "${X[@]}"; done
arm 1; H C1-1 "${X[@]}" --env DOSAGS_LAB_RPW_STALE=1
arm 0; H F1-0 "${X[@]}" --env DOSAGS_LAB_RPW_MASKCHG=1
arm 1; H F1-1 "${X[@]}" --env DOSAGS_LAB_RPW_MASKCHG=1
arm 1; H F1-N "${X[@]}" --env DOSAGS_LAB_RPW_MASKCHG=1 --env DOSAGS_LAB_RPW_NOGUARD=1
for a in 0 1; do arm $a; GCL GCL-$a "${X[@]}"; done
I I-Xon --env DOSAGS_ROUTE_PREWARM=on
I I-X2 --env DOSAGS_ROUTE_PREWARM=2
echo LANE1-DONE
