#!/usr/bin/env bash
# R2DEF lane 2 (display 397), serialized. The in-place-edit forcings under the default (DYN, WBM) with their controls;
# gates 1 and 2 on V and AGS Quest; gate 3's control (i) on G; the latch (FORCE_WHOLE) forcing; then the release
# cells (P9 and regression).
set -u; export DOSBOX_DISPLAY_NUM=397; source /home/claude/git/dosags-r2def/build/r2d/lib.sh
FD_=(--env DOSAGS_LAB_CR_DYN=7)
arm D; G G-Y-D "${FD_[@]}" "${X[@]}"; arm Z; G G-Y-Z "${FD_[@]}" "${X[@]}"; arm Dn; G G-Y-N "${FD_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NONOTIFY=1
FW_=(--env DOSAGS_LAB_CR_WBM=7)
arm D; G G-W-D "${FW_[@]}" "${X[@]}"; arm Z; G G-W-Z "${FW_[@]}" "${X[@]}"; arm Dn; G G-W-N "${FW_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOWBGEN=1
for a in D 2 Z 1; do arm $a; V V-$a "${X[@]}"; done
for a in D 2 Z 1; do arm $a; Q Q-$a "${X[@]}"; done
arm Dn
G G-D-NODRAW "${X[@]}" --env DOSAGS_LAB_CR_NODRAW=1
FL_=(--env DOSAGS_LAB_FORCE_WHOLE=7)
arm Z; G G-L-Z "${FL_[@]}" "${X[@]}"; arm Dn; G G-L-D "${FL_[@]}" "${X[@]}"; G G-L-N "${FL_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOLATCH=1
$L/release.sh
echo LANE2-DONE
