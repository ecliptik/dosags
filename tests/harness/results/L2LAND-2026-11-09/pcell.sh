#!/usr/bin/env bash
# L2LAND generic cell (L1LAND's pcell.sh, paths and display only): pcell.sh TAG EXE PKG [run-dosbox args...]   (copies the records, deletes the stage dir)
#   KEEPSTAGE=1 keeps the stage dir (parse-results needs it); the caller deletes it. Display 398 only.
set -uo pipefail
W=/home/claude/git/dosags-l2land
TAG=$1; EXE=$2; PKG=$3; shift 3
OUT=$W/build/l2/results/$TAG; rm -rf $OUT; mkdir -p $OUT
export DOSBOX_DISPLAY_NUM=${DOSBOX_DISPLAY_NUM:-398}
case $DOSBOX_DISPLAY_NUM in 398) ;; *) echo "display must be 398" >&2; exit 2;; esac
cd $W
AGS_EXE=$EXE timeout 3300 tests/harness/run-dosbox.sh $PKG "$@" > $OUT/run.stdout 2> $OUT/run.stderr
rc=$?
STAGE=$(tail -1 $OUT/run.stdout)
echo "rc=$rc stage=$STAGE exe=$EXE sha256=$(sha256sum $EXE | cut -c1-64) pkg=$PKG args=$*" > $OUT/CELL.txt
for f in STDOUT.TXT RUNMANI.LOG AUTOPLT.LOG RUN.BAT TICKS.BIN FHASH.TXT; do [ -f "$STAGE/$f" ] && cp "$STAGE/$f" $OUT/; done
if [ -z "${KEEPSTAGE:-}" ]; then case "$STAGE" in /tmp/dos-port-dosbox.?*) rm -rf "$STAGE";; esac; fi
echo "$TAG rc=$rc"
