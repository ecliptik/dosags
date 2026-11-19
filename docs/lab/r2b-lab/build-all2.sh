#!/usr/bin/env bash
# LAB-R2B v2 builds (fix: mode 1 records its composites, so R2a can hit in mode 1). vendor/ags rebuilt from the scripts.
set -eu
W=/home/claude/git/dosags-lab-r2b; L=$W/build/r2b; cd $W
git -C vendor/ags checkout -q -- .
python3 $L/lever-r2b.py vendor/ags
git -C vendor/ags diff > $L/lab-r2b.diff
make game > $L/build2-ins.log 2>&1
cp build/ags/ags.exe $L/exe/R2BINS.EXE
DOSAGS_RELEASE=1 make game > $L/build2-rel.log 2>&1
cp build/ags-release/ags.exe $L/exe/R2BREL.EXE
python3 $L/apply-overlay-r2b.py vendor/ags
make game > $L/build2-gate.log 2>&1
cp build/ags/ags.exe $L/exe/R2BGATE.EXE
git -C vendor/ags diff > $L/lab-r2b-gate-full.diff
git -C vendor/ags checkout -q -- .
git -C vendor/ags apply $L/lab-r2b.diff
git -C vendor/ags diff | cmp - $L/lab-r2b.diff && echo "vendor back to lever only"
sha256sum $L/exe/*.EXE
echo BUILDALL-DONE
