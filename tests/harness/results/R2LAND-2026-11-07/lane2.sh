#!/usr/bin/env bash
# R2LAND lane 2 (display 397), serialized: the in-place-edit forcings first (dynamic sprite DYN, walk-behind mask WBM),
# gate 1 on V and AGS Quest; gate 2 on G; control (i) on G; control (ii) under the forced baseline; the latch forcing;
# then the release cells (P9 and regression).
set -u; export DOSBOX_DISPLAY_NUM=397; source /home/claude/git/dosags-r2land/build/r2/lib.sh
FD_=(--env DOSAGS_LAB_CR_DYN=7)
arm 2; G G-D-2 "${FD_[@]}" "${X[@]}"; G G-D-0 "${FD_[@]}"; arm 2n; G G-D-N "${FD_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NONOTIFY=1
FW_=(--env DOSAGS_LAB_CR_WBM=7)
arm 2; G G-W-2 "${FW_[@]}" "${X[@]}"; G G-W-0 "${FW_[@]}"; arm 2n; G G-W-N "${FW_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOWBGEN=1
for a in 0 2 1; do arm $a; V V-$a "${X[@]}"; done
for a in 0 2 1; do arm $a; Q Q-$a "${X[@]}"; done
for g in 2 0; do for a in 0 2; do arm $a; G G-G$g-$a --env DOSAGS_GUI_CLIP=$g "${X[@]}"; done; done
arm 2n
G G-2-NODRAW "${X[@]}" --env DOSAGS_LAB_CR_NODRAW=1
FB_=(--env DOSAGS_LAB_CR_BASEL=7)
G G-B-0 "${FB_[@]}"; G G-B-2 "${FB_[@]}" "${X[@]}"; G G-B-N "${FB_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOBASEL=1
FL_=(--env DOSAGS_LAB_FORCE_WHOLE=7)
G G-L-0 "${FL_[@]}"; G G-L-2 "${FL_[@]}" "${X[@]}"; G G-L-N "${FL_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOLATCH=1
$L/release.sh
echo LANE2-DONE
