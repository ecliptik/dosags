#!/usr/bin/env bash
# R2DEF lane 1 (display 396), serialized. Gate 1 (default vs =2) and gate 2 (=0 and =1, against R2LAND's 0369 records)
# on G, GCL and the intro; gate 3's control (i) on GCL; gate 4's old-rect mark (TOGGLE) and whole invalidation (CAM)
# forcings under the default; extras: the default under DOSAGS_GUI_CLIP=0 and =2 on G; then gate 3's control (ii)
# under the forced baseline (BASEL) and the coarse-flag forcing (SPANMAX/SPANPROBE).
set -u; export DOSBOX_DISPLAY_NUM=396; source /home/claude/git/dosags-r2def/build/r2d/lib.sh
for a in D 2 Z 1; do arm $a; G G-$a "${X[@]}"; done
for a in D 2 Z 1; do arm $a; GCL GCL-$a "${X[@]}"; done
for a in D 2 Z 1; do arm $a; I I-$a "${X[@]}"; done
arm Dn
GCL GCL-D-NODRAW "${X[@]}" --env DOSAGS_LAB_CR_NODRAW=1
FT_=(--env DOSAGS_LAB_CR_TOGGLE=7)
arm Z; G G-T-Z "${FT_[@]}" "${X[@]}"; arm Dn; G G-T-D "${FT_[@]}" "${X[@]}"; G G-T-N "${FT_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOMARK=1
FC_=(--env DOSAGS_LAB_CR_CAM=7)
arm Z; G G-C-Z "${FC_[@]}" "${X[@]}"; arm Dn; G G-C-D "${FC_[@]}" "${X[@]}"; G G-C-N "${FC_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOCAM=1
for g in 0 2; do for a in Z Dn; do arm $a; G G-G$g-$a --env DOSAGS_GUI_CLIP=$g "${X[@]}"; done; done
FB_=(--env DOSAGS_LAB_CR_BASEL=7)
arm Z; G G-B-Z "${FB_[@]}" "${X[@]}"; arm Dn; G G-B-D "${FB_[@]}" "${X[@]}"; G G-B-N "${FB_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOBASEL=1
FS_=(--env DOSAGS_LAB_SPANMAX=1 --env DOSAGS_LAB_SPANPROBE=7:166)
arm Z; G G-S-Z "${FS_[@]}" "${X[@]}"; arm Dn; G G-S-D "${FS_[@]}" "${X[@]}"
echo LANE1-DONE
