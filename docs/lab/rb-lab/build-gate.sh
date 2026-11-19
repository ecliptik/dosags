#!/usr/bin/env bash
set -eu
W=/home/claude/git/dosags-lab-rb; L=$W/build/rb; cd $W
make game > $L/gate.log 2>&1
cp build/ags/ags.exe $L/exe/${OUTEXE:-RBGATE.EXE}
(cd vendor/ags && git diff; git ls-files --others --exclude-standard | while read f; do git diff --no-index /dev/null "$f"; done) > $L/lab-rb-overlay.diff || true
sha256sum $L/exe/${OUTEXE:-RBGATE.EXE}
echo GATE-DONE
