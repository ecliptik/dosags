#!/usr/bin/env bash
# R2DEF lane 3 (display 397, after lane 2): 0370's choice for an unknown value -- DOSAGS_CHAR_REUSE=3 and =off must
# read as the default (mode 2). Intro fixture, no verify.
set -u; export DOSBOX_DISPLAY_NUM=397; source /home/claude/git/dosags-r2def/build/r2d/lib.sh
I I-X3 --env DOSAGS_CHAR_REUSE=3
I I-Xoff --env DOSAGS_CHAR_REUSE=off
echo LANE3-DONE
