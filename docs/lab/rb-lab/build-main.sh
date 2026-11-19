#!/usr/bin/env bash
set -eu
W=/home/claude/git/dosags-lab-rb; L=$W/build/rb; cd $W
make patches > $L/patches.log 2>&1
make sdl3 > $L/sdl3.log 2>&1
make game > $L/ins.log 2>&1
cp build/ags/ags.exe $L/exe/MAININS.EXE
DOSAGS_RELEASE=1 make game > $L/rel.log 2>&1
cp build/ags-release/ags.exe $L/exe/MAINREL.EXE
sha256sum $L/exe/*.EXE
echo BUILD-DONE
