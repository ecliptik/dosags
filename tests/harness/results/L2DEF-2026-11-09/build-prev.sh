#!/usr/bin/env bash
# L2DEF: SDL3, then 0372's release flavour from main's series (vendor/ags = 0001-0372) as the P9 reference.
set -eu
export TMPDIR=/home/claude/data/tmp
W=/home/claude/data/worktrees/dosags-l2def; L=$W/build/l2d; cd $W
make sdl3 > $L/sdl3.log 2>&1
DOSAGS_RELEASE=1 make game > $L/build-prev.log 2>&1
cp build/ags-release/ags.exe $L/exe/PREVREL.EXE
DOSAGS_RELEASE=1 make build-dirty
sha256sum $L/exe/PREVREL.EXE
echo PREV-DONE
