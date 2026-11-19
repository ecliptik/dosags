#!/usr/bin/env bash
# LAB-R2B generic cell: pcell.sh TAG EXE PKG [run-dosbox args...]   (R3LAND's pcell.sh; copies the records, deletes the stage dir)
#   KEEPSTAGE=1 keeps the stage dir (parse-results needs it); the caller deletes it. Display 394/395 only.
set -uo pipefail
W=/home/claude/git/dosags-lab-r2b
TAG=$1; EXE=$2; PKG=$3; shift 3
OUT=$W/build/r2b/results/$TAG; rm -rf $OUT; mkdir -p $OUT
export DOSBOX_DISPLAY_NUM=${DOSBOX_DISPLAY_NUM:-394}
case $DOSBOX_DISPLAY_NUM in 394|395) ;; *) echo "display must be 394/395" >&2; exit 2;; esac
cd $W
AGS_EXE=$EXE timeout 3300 tests/harness/run-dosbox.sh $PKG "$@" > $OUT/run.stdout 2> $OUT/run.stderr
rc=$?
STAGE=$(tail -1 $OUT/run.stdout)
echo "rc=$rc stage=$STAGE exe=$EXE sha256=$(sha256sum $EXE | cut -c1-64) pkg=$PKG args=$*" > $OUT/CELL.txt
for f in STDOUT.TXT RUNMANI.LOG AUTOPLT.LOG RUN.BAT TICKS.BIN FHASH.TXT; do [ -f "$STAGE/$f" ] && cp "$STAGE/$f" $OUT/; done
if [ -z "${KEEPSTAGE:-}" ]; then case "$STAGE" in /tmp/dos-port-dosbox.?*) rm -rf "$STAGE";; esac; fi
echo "$TAG rc=$rc"
