#!/usr/bin/env bash
# L2DEF: full clean builds of both flavours from the committed tree (vendor/ags = 0001-0373 applied by make patches).
# Each TAG (A, then B after the gate build) removes build/ags and build/ags-release first.
set -eu
export TMPDIR=/home/claude/data/tmp
W=/home/claude/data/worktrees/dosags-l2def; L=$W/build/l2d; cd $W
TAG=${1:-A}
rm -rf build/ags build/ags-release
make build-dirty
make game > $L/build-ins-$TAG.log 2>&1
cp build/ags/ags.exe $L/exe/L2DINS-$TAG.EXE
DOSAGS_RELEASE=1 make game > $L/build-rel-$TAG.log 2>&1
cp build/ags-release/ags.exe $L/exe/L2DREL-$TAG.EXE
make build-dirty
DOSAGS_RELEASE=1 make build-dirty
sha256sum $L/exe/L2DINS-$TAG.EXE $L/exe/L2DREL-$TAG.EXE
echo BUILD-DONE
