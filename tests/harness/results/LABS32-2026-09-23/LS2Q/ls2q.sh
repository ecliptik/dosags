#!/bin/bash
# LS2Q: lab count run of the S2Q1 fixture (AGS Quest forced-32, 640x480x32 1:1, AutoPilot to tick 1500, sound off).
S=/tmp/claude-1001/-home-claude-git-sdl-dos-ports/dcce1110-1df6-48ac-8758-1bed523f1eb1/scratchpad
L=/home/claude/git/dosags-lab-metric; H=$L/tests/harness
cd $H
AGS_EXE=${EXE:-$L/build/lab/L2/ags.exe} ./run-dosbox.sh agsquest --fixed-timestep --no-verify-present --include-extra ${CFG:-$S/cfg/s2q/ACSETUP.CFG} \
  --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_TAS_AUTO_EXIT_TICK=1500 "$@" --timeout 900 2>&1 | tail -1
