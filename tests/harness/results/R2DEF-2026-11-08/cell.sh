#!/usr/bin/env bash
# R2DEF MMD cell (R2LAND's cell.sh, paths only): cell.sh TAG EXE EXIT_TICK [extra run-dosbox args...]   (fixed 40000, sound-ON 512x384 round cfg, save 007)
#   Based on R3LAND's build/r3/cell.sh. NOFT=--no-fine-timing -> every tick rendered (no --fixed-timestep), fine timing off;
#   FT=1 -> --fixed-timestep with fine timing on; FTOFF=1 -> --fixed-timestep, fine timing off; NOSAVE=1 -> no save restore;
#   TL=n -> DOSAGS_TICKLOG=n. Display: DOSBOX_DISPLAY_NUM (396/397 only). Deletes its stage dir after copying the records.
set -euo pipefail
W=/home/claude/git/dosags-r2def
TAG=$1; EXE=$2; EXIT=$3; shift 3
OUT=$W/build/r2d/results/$TAG; rm -rf $OUT; mkdir -p $OUT
CONF=$W/tests/harness/confs/dosbox-x-fixed40k-opl3.conf
CFG=$W/tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG
SAVE=/home/claude/git/dosags/build/ws/roundQ/AGSSAVE.007
SAVEARGS=(--ags-arg --loadsavedgame --ags-arg 7 --include-extra $SAVE:AGSSAVE.007)
[ -n "${NOSAVE:-}" ] && SAVEARGS=()
export DOSBOX_DISPLAY_NUM=${DOSBOX_DISPLAY_NUM:-396}
case $DOSBOX_DISPLAY_NUM in 396|397) ;; *) echo "display must be 396/397" >&2; exit 2;; esac
TIM=(--no-fine-timing)
[ -n "${FT:-}" ] && TIM=(--fixed-timestep)
[ -n "${FTOFF:-}" ] && TIM=(--fixed-timestep --no-fine-timing)
TLA=(); [ -n "${TL:-}" ] && TLA=(--env DOSAGS_TICKLOG=$TL)
cd $W
set +e
AGS_EXE=$EXE timeout 3300 tests/harness/run-dosbox.sh mmd "${TIM[@]}" --conf $CONF --no-verify-present --timeout ${TMO:-3000} \
  --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=$EXIT "${TLA[@]}" \
  "${SAVEARGS[@]}" --include-extra $CFG:ACSETUP.CFG \
  "$@" > $OUT/run.stdout 2> $OUT/run.stderr
rc=$?
set -e
STAGE=$(tail -1 $OUT/run.stdout)
echo "rc=$rc stage=$STAGE exe=$EXE sha256=$(sha256sum $EXE | cut -c1-64) exit=$EXIT FT=${FT:-} FTOFF=${FTOFF:-} TL=${TL:-} NOSAVE=${NOSAVE:-} args=${TIM[*]} $*" > $OUT/CELL.txt
for f in STDOUT.TXT RUNMANI.LOG AUTOPLT.LOG RUN.BAT TICKS.BIN FHASH.TXT; do [ -f "$STAGE/$f" ] && cp "$STAGE/$f" $OUT/; done
case "$STAGE" in /tmp/dos-port-dosbox.?*) rm -rf "$STAGE";; esac
echo "$TAG rc=$rc"
