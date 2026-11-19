#!/usr/bin/env bash
# R2LAND lane 3 (display 396, after lane 1): extras beyond the brief -- 0368's coarse guard forced (R3LAND's SPANMAX=1 +
# SPANPROBE=7:166), CHAR_REUSE=2 vs 0 under it; and CHAR_REUSE=2 vs 0 under DOSAGS_GUI_CLIP=1.
set -u
/home/claude/git/dosags-r2land/tools/waitfor.sh --timeout 3600 --pidfile /home/claude/git/dosags-r2land/build/r2/results/lane1.pid ||
/home/claude/git/dosags-r2land/tools/waitfor.sh --timeout 3600 --pidfile /home/claude/git/dosags-r2land/build/r2/results/lane1.pid ||
/home/claude/git/dosags-r2land/tools/waitfor.sh --timeout 3600 --pidfile /home/claude/git/dosags-r2land/build/r2/results/lane1.pid
export DOSBOX_DISPLAY_NUM=396; source /home/claude/git/dosags-r2land/build/r2/lib.sh
FS_=(--env DOSAGS_LAB_SPANMAX=1 --env DOSAGS_LAB_SPANPROBE=7:166)
arm 2; G G-S-2 "${FS_[@]}" "${X[@]}"; G G-S-0 "${FS_[@]}"
for a in 0 2; do arm $a; G G-G1-$a --env DOSAGS_GUI_CLIP=1 "${X[@]}"; done
echo LANE3-DONE
