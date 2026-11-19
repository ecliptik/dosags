#!/usr/bin/env bash
# LAB-R2B lane B (display 395): gate 1 on V and AGS Quest AutoPilot. Serialized.
set -u; export DOSBOX_DISPLAY_NUM=395; source /home/claude/git/dosags-lab-r2b/build/r2b/lib.sh
for a in 0 2 1; do arm $a; V V-$a "${X[@]}"; done
for a in 0 2 1; do arm $a; Q Q-$a "${X[@]}"; done
echo LANEB-DONE
