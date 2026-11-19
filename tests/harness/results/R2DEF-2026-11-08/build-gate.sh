#!/usr/bin/env bash
# R2DEF gate build: 0001-0370 + R2LAND's overlay (apply-overlay-r2land.py, unchanged), instrumented; then vendor/ags
# back to 0370. Lab only: the overlay is never landed.
set -eu
W=/home/claude/git/dosags-r2def; L=$W/build/r2d; cd $W
git -C vendor/ags diff --quiet && git -C vendor/ags diff --cached --quiet
python3 $L/apply-overlay-r2land.py vendor/ags
git -C vendor/ags diff > $L/gate-overlay.diff
make build-dirty
make game > $L/build-gate.log 2>&1
cp build/ags/ags.exe $L/exe/R2DGATE.EXE
git -C vendor/ags checkout -q -- .
git -C vendor/ags status --porcelain | head -c1 | wc -c
make build-dirty
sha256sum $L/exe/R2DGATE.EXE
echo GATE-DONE
