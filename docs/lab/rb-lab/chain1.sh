#!/usr/bin/env bash
# LAB-RB chain 1 (serial, one DOSBox-X at a time, display 398)
R=/home/claude/git/dosags-lab-rb/build/rb/runA.sh
TAG=H4 FIX=H $R
TAG=A3 FIX=GCL $R
TAG=HSR FIX=H $R --env DOSAGS_STALL_RESYNC=1
TAG=GSR FIX=GCL $R --env DOSAGS_STALL_RESYNC=1
echo CHAIN1-DONE
