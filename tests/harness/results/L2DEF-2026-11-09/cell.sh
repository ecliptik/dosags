#!/usr/bin/env bash
# L2DEF MMD cell (L2LAND's cell.sh: paths, TMPDIR stages under /home/claude/data/tmp): cell.sh TAG EXE EXIT_TICK [extra run-dosbox args...]   (fixed 40000, sound-ON 512x384 round cfg, save 007)
#   Based on R3LAND's build/r3/cell.sh. NOFT=--no-fine-timing -> every tick rendered (no --fixed-timestep), fine timing off;
#   FT=1 -> --fixed-timestep with fine timing on; FTOFF=1 -> --fixed-timestep, fine timing off; NOSAVE=1 -> no save restore;
#   TL=n -> DOSAGS_TICKLOG=n. Display: DOSBOX_DISPLAY_NUM (398 only). Deletes its stage dir after copying the records.
set -euo pipefail
export TMPDIR=/home/claude/data/tmp
W=/home/claude/data/worktrees/dosags-l2def
TAG=$1; EXE=$2; EXIT=$3; shift 3
OUT=$W/build/l2d/results/$TAG
# RESUME=1: a cell that already finished (CELL.txt rc=0 and a RUNMANI.LOG) is kept and not re-run
if [ -n "${RESUME:-}" ] && grep -q "^rc=0 " $OUT/CELL.txt 2>/dev/null && [ -f $OUT/RUNMANI.LOG ]; then echo "$TAG kept"; exit 0; fi
rm -rf $OUT; mkdir -p $OUT
CONF=$W/tests/harness/confs/dosbox-x-fixed40k-opl3.conf
CFG=$W/tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG
SAVE=/home/claude/git/dosags/build/ws/roundQ/AGSSAVE.007
SAVEARGS=(--ags-arg --loadsavedgame --ags-arg 7 --include-extra $SAVE:AGSSAVE.007)
[ -n "${NOSAVE:-}" ] && SAVEARGS=()
export DOSBOX_DISPLAY_NUM=${DOSBOX_DISPLAY_NUM:-398}
case $DOSBOX_DISPLAY_NUM in 398) ;; *) echo "display must be 398" >&2; exit 2;; esac
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
case "$STAGE" in */dos-port-dosbox.?*) rm -rf "$STAGE" "$STAGE.meta";; esac
echo "$TAG rc=$rc"
