#!/usr/bin/env bash
# LAB-R2B chain 1 (display 394): lane A (gate 1 on G, GCL, intro), then lane C (controls, forced guards)
L=/home/claude/git/dosags-lab-r2b/build/r2b
$L/laneA.sh > $L/results/laneA.log 2>&1
$L/laneC.sh > $L/results/laneC.log 2>&1
echo CHAIN1-DONE
