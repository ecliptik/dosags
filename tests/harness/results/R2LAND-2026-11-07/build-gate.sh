#!/usr/bin/env bash
# R2LAND gate build: 0001-0369 + the overlay (apply-overlay-r2land.py), instrumented; then vendor/ags back to 0369.
set -eu
W=/home/claude/git/dosags-r2land; L=$W/build/r2; cd $W
git -C vendor/ags diff --quiet && git -C vendor/ags diff --cached --quiet
python3 $L/apply-overlay-r2land.py vendor/ags
git -C vendor/ags diff > $L/gate-overlay.diff
make build-dirty
make game > $L/build-gate.log 2>&1
cp build/ags/ags.exe $L/exe/R2GATE.EXE
git -C vendor/ags checkout -q -- .
git -C vendor/ags status --porcelain | head -c1 | wc -c
make build-dirty
sha256sum $L/exe/R2GATE.EXE
echo GATE-DONE
