#!/usr/bin/env bash
# R2LAND: clean builds of both flavours from the committed tree (vendor/ags = 0001-0369 applied by make patches).
set -eu
W=/home/claude/git/dosags-r2land; L=$W/build/r2; cd $W
TAG=${1:-A}
make build-dirty
make game > $L/build-ins-$TAG.log 2>&1
cp build/ags/ags.exe $L/exe/R2INS-$TAG.EXE
DOSAGS_RELEASE=1 make game > $L/build-rel-$TAG.log 2>&1
cp build/ags-release/ags.exe $L/exe/R2REL-$TAG.EXE
DOSAGS_RELEASE=1 make build-dirty
sha256sum $L/exe/R2INS-$TAG.EXE $L/exe/R2REL-$TAG.EXE
echo BUILD-DONE
