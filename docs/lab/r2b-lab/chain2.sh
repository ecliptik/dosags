#!/usr/bin/env bash
# LAB-R2B chain 2 (display 395): lane B (gate 1 on V, AGS Quest), lane D (camera, baseline, release), lane E (timing)
L=/home/claude/git/dosags-lab-r2b/build/r2b
$L/laneB.sh > $L/results/laneB.log 2>&1
$L/laneD.sh > $L/results/laneD.log 2>&1
DOSBOX_DISPLAY_NUM=395 $L/laneE.sh > $L/results/laneE.log 2>&1
echo CHAIN2-DONE
