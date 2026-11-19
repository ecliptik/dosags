#!/usr/bin/env bash
set -eu
/home/claude/git/dosags-l2land/build/l2/build-clean.sh A
/home/claude/git/dosags-l2land/build/l2/build-clean.sh B
L=/home/claude/git/dosags-l2land/build/l2/exe
cmp $L/L2INS-A.EXE $L/L2INS-B.EXE && echo "INS A=B"
cmp $L/L2REL-A.EXE $L/L2REL-B.EXE && echo "REL A=B"
ls -l $L/*.EXE
echo AB-DONE
