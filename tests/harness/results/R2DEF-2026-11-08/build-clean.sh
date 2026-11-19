#!/usr/bin/env bash
# R2DEF: clean builds of both flavours from the committed tree (vendor/ags = 0001-0370 applied by make patches).
# TAG A = the first builds in a fresh worktree; TAG B = after rm -rf build/ags build/ags-release (a full clean rebuild).
set -eu
W=/home/claude/git/dosags-r2def; L=$W/build/r2d; cd $W
TAG=${1:-A}
[ "$TAG" = B ] && rm -rf build/ags build/ags-release
make build-dirty
make game > $L/build-ins-$TAG.log 2>&1
cp build/ags/ags.exe $L/exe/R2DINS-$TAG.EXE
DOSAGS_RELEASE=1 make game > $L/build-rel-$TAG.log 2>&1
cp build/ags-release/ags.exe $L/exe/R2DREL-$TAG.EXE
make build-dirty
DOSAGS_RELEASE=1 make build-dirty
sha256sum $L/exe/R2DINS-$TAG.EXE $L/exe/R2DREL-$TAG.EXE
echo BUILD-DONE
