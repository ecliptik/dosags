#!/usr/bin/env bash
# L2LAND: build/ags/ags.exe back to the clean instrumented 0372 (the gate build left the overlay's objects there)
set -eu
W=/home/claude/git/dosags-l2land; L=$W/build/l2; cd $W
git -C vendor/ags status --porcelain | head -c1 | wc -c | grep -q '^0$'
make game > $L/rebuild-ins.log 2>&1
make build-dirty
cmp build/ags/ags.exe $L/exe/L2INS-A.EXE && echo "build/ags/ags.exe = L2INS-A"
echo REBUILD-DONE
