#!/usr/bin/env bash
# LAB-R2B lane A (display 394): gate 1 (mode 1 and 2 vs 0) on G, GCL, the intro; then controls. Serialized.
set -u; export DOSBOX_DISPLAY_NUM=394; source /home/claude/git/dosags-lab-r2b/build/r2b/lib.sh
for a in 0 2 1; do arm $a; G G-$a "${X[@]}"; done
for a in 0 2 1; do arm $a; GCL GCL-$a "${X[@]}"; done
for a in 0 2 1; do arm $a; I I-$a "${X[@]}"; done
echo LANEA-DONE
