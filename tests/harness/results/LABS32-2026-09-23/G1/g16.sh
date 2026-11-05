#!/bin/bash
# Gate G1-16 (LAB-S32.md section 7, coordinator addition): C1 must not change 16-bit output. AGS Quest native 16-bit.
# A = DOSAGS_ALPHAFAST=0, B = fast path on. Fixed 40000 (tools/dosbox-x.conf); one EXCLUSIVE lock per run via the hub library.
set -u
L=/home/claude/git/dosags-lab-metric; H=$L/tests/harness; R=$H/results/LABS32-2026-09-23/G1
CFG=${CFG:-/tmp/claude-1001/-home-claude-git-sdl-dos-ports/dcce1110-1df6-48ac-8758-1bed523f1eb1/scratchpad/cfg/s2q/ACSETUP.CFG}
EXE=${EXE:-$L/build/lab/C1L/ags.exe}
CONF=${CONF:-}
cd $H
# Lock (coordinator 2026-09-23): EXCLUSIVE per run, fixed cycles (tools/dosbox-x.conf: fixed 40000,
# core=normal; deterministic). AGS Quest has a known one-tick AutoPilot divergence under host load at
# cycles=max, so a shared-lock, cycles=max A/B could fail spuriously or pass for the wrong reason.
CONF=${CONF:-$L/tools/dosbox-x.conf}
own_stage() { ps -eo pid=,ppid=,args= | awk -v root="$1" '
    { pid=$1; ppid=$2; $1=""; $2=""; sub(/^ +/,""); par[pid]=ppid; cmd[pid]=$0 }
    END { for (p in cmd) { if (cmd[p] !~ /^dosbox-x .*-c MOUNT C \/tmp\/dos-port-dosbox\./) continue
      q=p; for (n=0;n<64 && q!="" && q!="0" && q!="1";n++){ if (q==root){ match(cmd[p],/\/tmp\/dos-port-dosbox\.[A-Za-z0-9]*/); print substr(cmd[p],RSTART,RLENGTH); exit } q=par[q] } } }'; }
n=0
for arm in ${ARMS:-A B A B}; do
  n=$((n+1)); envs=(); [[ $arm == A ]] && envs=(--env DOSAGS_ALPHAFAST=0)
  confs=(); [[ -n "$CONF" ]] && confs=(--conf $CONF)
  ( # hub lock library (b9b7364): intent lock, a waiting writer blocks new readers (coordinator 2026-09-24)
    source /home/claude/git/sdl-dos-ports/shared/tools/dosbox-lock-lib.sh; dbxlock_acquire exclusive ${LOCK_WAIT_S:-21600} "tool=lab-metric-g1-$arm-$n" || exit 75
    export DOSBOX_LOCK_HELD=1; trap dbxlock_release EXIT
  AGS_EXE=$EXE ./run-dosbox.sh agsquest --fixed-timestep --no-verify-present --include-extra $CFG "${confs[@]}" \
      --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 ${EXTRA_ENV:-} "${envs[@]}" --timeout 1800 >/dev/null 2>&1 &
    rp=$!; st=""
    while kill -0 $rp 2>/dev/null; do [[ -z "$st" ]] && st=$(own_stage $rp); sleep 2; done
    d=$R/${TAG:-g16}-$arm-$n; mkdir -p $d
    [[ -n "$st" ]] && cp $st/RUNMANI.LOG $st/STDOUT.TXT $st/RUN.BAT $st/AUTOPLT.LOG $st/PH*.BMP $d/ 2>/dev/null
    echo "$(date -u +%T) $arm $n $st" >> $R/INDEX16.TXT
  )
done
