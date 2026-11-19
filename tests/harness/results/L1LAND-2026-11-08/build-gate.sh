#!/usr/bin/env bash
# L1LAND gate build: 0001-0371 + the gate overlay (apply-overlay-l1land.py), instrumented; then vendor/ags back to 0371.
# Lab only: the overlay is never landed.
set -eu
W=/home/claude/git/dosags-l1land; L=$W/build/l1; cd $W
git -C vendor/ags diff --quiet && git -C vendor/ags diff --cached --quiet
python3 $L/apply-overlay-l1land.py vendor/ags
(cd vendor/ags && git diff; git ls-files --others --exclude-standard | while read f; do git diff --no-index /dev/null "$f"; done) > $L/gate-overlay.diff || true
make build-dirty
make game > $L/build-gate.log 2>&1
cp build/ags/ags.exe $L/exe/L1GATE.EXE
git -C vendor/ags checkout -q -- . && git -C vendor/ags clean -fdq
git -C vendor/ags status --porcelain | head -c1 | wc -c
make build-dirty
sha256sum $L/exe/L1GATE.EXE
echo GATE-DONE
