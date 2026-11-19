#!/usr/bin/env bash
# L1LAND lane 2 (display 397), serialized: gate 1 on V, the intro and AGS Quest; then the release cells (P9, regression).
set -u; export DOSBOX_DISPLAY_NUM=397; source /home/claude/git/dosags-l1land/build/l1/lib.sh
for a in 0 1; do arm $a; V V-$a "${X[@]}"; done
for a in 0 1; do arm $a; I I-$a "${X[@]}"; done
for a in 0 1; do arm $a; Q Q-$a "${X[@]}"; done
$L/release.sh
echo LANE2-DONE
