#!/usr/bin/env bash
# LAB-L1R timing pair T1 (information): fixture H, lever off / on
set -u; source /home/claude/git/dosags-lab-rb/docs/lab/l1r-lab/lib.sh
arm 0; T T-H-0 "${X[@]}"
arm 1; T T-H-1 "${X[@]}"
echo CHAINT-DONE
