#!/usr/bin/env bash
# LAB-L1R: rebuild only the gate exe (lever + gate overlay), then put vendor/ags back to the lever only
set -eu
W=/home/claude/git/dosags-lab-rb; L=$W/build/l1r; D=$W/docs/lab/l1r-lab; cd $W
git -C vendor/ags checkout -q -- . && git -C vendor/ags clean -fdq
git -C vendor/ags apply $D/lab-l1r.diff
python3 $D/apply-overlay-l1r.py vendor/ags
make game > $L/build-gate.log 2>&1
cp build/ags/ags.exe $L/exe/L1RGATE.EXE
(cd vendor/ags && git diff; git ls-files --others --exclude-standard | while read f; do git diff --no-index /dev/null "$f"; done) > $D/lab-l1r-gate-full.diff || true
git -C vendor/ags checkout -q -- . && git -C vendor/ags clean -fdq
git -C vendor/ags apply $D/lab-l1r.diff
sha256sum $L/exe/L1RGATE.EXE
echo GATE-DONE
