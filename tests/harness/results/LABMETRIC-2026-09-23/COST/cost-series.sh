#!/bin/bash
# Counter-cost series (LAB-METRIC.md 1.5 / 4.3). Fixed-cycles DOSBox-X (confs/dosbox-x-fixed25k.conf),
# taken EXCLUSIVE once around the whole series. Arms: A2 = rebased base without ags 0230,
# B2 = 0230 timed build, L2 = 0230 lab build (script_ins counted). Order A B L L B A per fixture.
# M* = the predecessor's 0208-base arm A binary re-run, to compare with its overlapped runs.
set -u
L=/home/claude/git/dosags-lab-metric; H=$L/tests/harness; R=$H/results/LABMETRIC-2026-09-23/COST
cd $H
source $H/dosbox-lock.sh; dosbox_lock_series lab-metric-cost || exit $?; trap dosbox_lock_release EXIT
exe() { case $1 in A) echo $L/build/lab/A2/ags.exe;; B) echo $L/build/lab/B2/ags.exe;; L) echo $L/build/lab/L2/ags.exe;; M) echo $L/build/lab/A/ags.exe;; esac; }
run() { # fx arm n
  local fx=$1 arm=$2 n=$3 out
  if [[ $fx == anim ]]; then
    out=$(AGS_EXE=$(exe $arm) ./run-dosbox.sh bench8 --fixed-timestep --no-verify-present --conf $H/confs/dosbox-x-fixed25k.conf \
      --include-extra $R/cfg/anim/ACSETUP.CFG --include-extra $R/cfg/anim/BENCH.CFG --timeout 1200 2>/dev/null | tail -1)
  else
    out=$(AGS_EXE=$(exe $arm) ./run-dosbox.sh mmd --fixed-timestep --no-verify-present --conf $H/confs/dosbox-x-fixed25k.conf \
      --include-extra $R/cfg/mmd/ACSETUP.CFG --env DOSAGS_TAS_AUTO_EXIT_TICK=1000 --env DOSAGS_DIRECT_VSCREEN=0 --timeout 1200 2>/dev/null | tail -1)
  fi
  local d=$R/$fx-$arm-$n; mkdir -p $d
  [[ -d "$out" ]] && cp "$out"/RUNMANI.LOG "$out"/STDOUT.TXT "$out"/RUN.BAT $d/ 2>/dev/null
  echo "$(date -u +%T) $fx $arm $n $out" >> $R/INDEX.TXT
}
: > $R/INDEX.TXT
n=0; for a in A B L L B A; do n=$((n+1)); run anim $a $n; done
n=0; for a in A B L L B A; do n=$((n+1)); run mmd $a $n; done
run anim M 1; run mmd M 1
echo "$(date -u +%T) ALLDONE" >> $R/INDEX.TXT
