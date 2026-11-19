#!/usr/bin/env bash
# R2LAND lane 1 (display 396), serialized: gate 1 on G, GCL, the intro; gate 2 on GCL (GUI_CLIP=2 and 0); control (i)
# on GCL; forced guards: old-rect mark (TOGGLE) and camera / whole invalidation (CAM) on G.
set -u; export DOSBOX_DISPLAY_NUM=396; source /home/claude/git/dosags-r2land/build/r2/lib.sh
for a in 0 2 1; do arm $a; G G-$a "${X[@]}"; done
for a in 0 2 1; do arm $a; GCL GCL-$a "${X[@]}"; done
for a in 0 2 1; do arm $a; I I-$a "${X[@]}"; done
for g in 2 0; do for a in 0 2; do arm $a; GCL GCL-G$g-$a --env DOSAGS_GUI_CLIP=$g "${X[@]}"; done; done
arm 2n
GCL GCL-2-NODRAW "${X[@]}" --env DOSAGS_LAB_CR_NODRAW=1
FT_=(--env DOSAGS_LAB_CR_TOGGLE=7)
G G-T-0 "${FT_[@]}"; G G-T-2 "${FT_[@]}" "${X[@]}"; G G-T-N "${FT_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOMARK=1
FC_=(--env DOSAGS_LAB_CR_CAM=7)
G G-C-0 "${FC_[@]}"; G G-C-2 "${FC_[@]}" "${X[@]}"; G G-C-N "${FC_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOCAM=1
echo LANE1-DONE
