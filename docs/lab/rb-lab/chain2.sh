#!/usr/bin/env bash
# LAB-RB chain 2 (serial, display 398): Q3 -- fixture H under other random seeds, v7 exe
R=/home/claude/git/dosags-lab-rb/build/rb/runA.sh
EXE=RBGATE7.EXE TAG=H7 FIX=H SEED=1 $R
EXE=RBGATE7.EXE TAG=HS2 FIX=H SEED=2 $R
EXE=RBGATE7.EXE TAG=HS3 FIX=H SEED=3 $R
echo CHAIN2-DONE
