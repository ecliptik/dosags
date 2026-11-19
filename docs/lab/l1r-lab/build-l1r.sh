#!/usr/bin/env bash
# LAB-L1R builds: lever (instrumented + release), then lever + gate overlay (instrumented). vendor/ags rebuilt from scripts.
set -eu
W=/home/claude/git/dosags-lab-rb; L=$W/build/l1r; D=$W/docs/lab/l1r-lab; cd $W
git -C vendor/ags checkout -q -- . && git -C vendor/ags clean -fdq
python3 $D/lever-l1r.py vendor/ags
git -C vendor/ags diff > $D/lab-l1r.diff
make game > $L/build-ins.log 2>&1
cp build/ags/ags.exe $L/exe/L1RINS.EXE
DOSAGS_RELEASE=1 make game > $L/build-rel.log 2>&1
cp build/ags-release/ags.exe $L/exe/L1RREL.EXE
python3 $D/apply-overlay-l1r.py vendor/ags
make game > $L/build-gate.log 2>&1
cp build/ags/ags.exe $L/exe/L1RGATE.EXE
(cd vendor/ags && git diff; git ls-files --others --exclude-standard | while read f; do git diff --no-index /dev/null "$f"; done) > $D/lab-l1r-gate-full.diff || true
git -C vendor/ags checkout -q -- . && git -C vendor/ags clean -fdq
git -C vendor/ags apply $D/lab-l1r.diff
git -C vendor/ags diff | cmp - $D/lab-l1r.diff && echo "vendor back to lever only"
sha256sum $L/exe/*.EXE
echo BUILDL1R-DONE
