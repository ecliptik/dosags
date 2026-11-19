#!/usr/bin/env bash
# L2DEF gate build: 0001-0373 + L2LAND's gate overlay (apply-overlay-l2land.py), instrumented; then vendor/ags back to
# 0373. Lab only: the overlay is never landed.
set -eu
export TMPDIR=/home/claude/data/tmp
W=/home/claude/data/worktrees/dosags-l2def; L=$W/build/l2d; cd $W
git -C vendor/ags diff --quiet && git -C vendor/ags diff --cached --quiet
python3 $L/apply-overlay-l2land.py vendor/ags
(cd vendor/ags && git diff; git ls-files --others --exclude-standard | while read f; do git diff --no-index /dev/null "$f"; done) > $L/gate-overlay.diff || true
make build-dirty
make game > $L/build-gate.log 2>&1
cp build/ags/ags.exe $L/exe/L2DGATE.EXE
git -C vendor/ags checkout -q -- . && git -C vendor/ags clean -fdq
git -C vendor/ags status --porcelain | head -c1 | wc -c
make build-dirty
sha256sum $L/exe/L2DGATE.EXE
echo GATE-DONE
