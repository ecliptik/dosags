#!/usr/bin/env bash
# L2LAND: the gate exe = 0001-0372 + apply-overlay-l2land.py (instrumented), then vendor/ags back to the committed series.
set -eu
W=/home/claude/git/dosags-l2land; L=$W/build/l2; R=$W/tests/harness/results/L2LAND-2026-11-09; cd $W
git -C vendor/ags status --porcelain | head -c1 | wc -c | grep -q '^0$'
python3 $R/apply-overlay-l2land.py vendor/ags
(cd vendor/ags && git diff; git ls-files --others --exclude-standard | while read f; do git diff --no-index /dev/null "$f"; done) > $R/gate-overlay.diff || true
make game > $L/build-gate.log 2>&1
cp build/ags/ags.exe $L/exe/L2GATE.EXE
git -C vendor/ags checkout -q -- . && git -C vendor/ags clean -fdq
make build-dirty
sha256sum $L/exe/L2GATE.EXE; ls -l $L/exe/L2GATE.EXE
echo GATE-DONE
