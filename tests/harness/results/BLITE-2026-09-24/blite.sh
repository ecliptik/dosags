#!/bin/bash
# B-lite validation runs (LAB-METRIC.md section 10). One EXCLUSIVE lock per cell (others interleave
# between cells). Binary: build/lab/B2 (0230 timed build: work vector, no script_ins). Fixed 40000,
# core=normal: tools/dosbox-x.conf; SB5O: confs/dosbox-x-fixed40k-opl3.conf.
#   blite.sh CELL...     (F2B1 S2F2 AQF1 S2M1 SB5O)
set -u
L=/home/claude/git/dosags-lab-metric; H=$L/tests/harness; R=$H/results/BLITE-2026-09-24
EXE=$L/build/lab/B2/ags.exe; CONF=$L/tools/dosbox-x.conf; CONF_OPL3=$H/confs/dosbox-x-fixed40k-opl3.conf
export DOSBOX_DISPLAY_NUM=221
cd $H
own_stage() { ps -eo pid=,ppid=,args= | awk -v root="$1" '
    { pid=$1; ppid=$2; $1=""; $2=""; sub(/^ +/,""); par[pid]=ppid; cmd[pid]=$0 }
    END { for (p in cmd) { if (cmd[p] !~ /^dosbox-x .*-c MOUNT C \/tmp\/dos-port-dosbox\./) continue
      q=p; for (n=0;n<64 && q!="" && q!="0" && q!="1";n++){ if (q==root){ match(cmd[p],/\/tmp\/dos-port-dosbox\.[A-Za-z0-9]*/); print substr(cmd[p],RSTART,RLENGTH); exit } q=par[q] } } }'; }
log() { echo "$(date -u +%T) $*" >> $R/INDEX.TXT; }
run_cell() {   # cell interactive(0/1) then run-dosbox args...
  local cell=$1 inter=$2; shift 2
  ( # hub lock library (b9b7364): intent lock, a waiting writer blocks new readers (coordinator 2026-09-24)
    source /home/claude/git/sdl-dos-ports/shared/tools/dosbox-lock-lib.sh; dbxlock_acquire exclusive ${LOCK_WAIT_S:-21600} "tool="lab-metric-blite-$cell"" || exit 75
    export DOSBOX_LOCK_HELD=1; trap dbxlock_release EXIT
    log "$cell start"
    AGS_EXE=$EXE ./run-dosbox.sh "$@" --fixed-timestep --no-verify-present --timeout 2400 > $R/$cell.out 2>&1 &
    local rp=$! st="" clicked=0
    while kill -0 $rp 2>/dev/null; do
      [[ -z "$st" ]] && st=$(own_stage $rp)
      if [[ -n "$st" && $inter == 1 ]]; then
        if [[ $cell == S2F2 && $clicked == 0 ]]; then
          DRIVE_LOG=$R/$cell-DRIVE.LOG $H/lab-drive-xdotool.sh walk 25 2 90 >/dev/null 2>&1 & clicked=1
        fi
        if [[ $cell == SB5O && $clicked == 0 ]] && /usr/bin/grep -aq 'event=ready room=2' $st/STDOUT.TXT 2>/dev/null; then
          log "SB5O room 2 ready; START in ${SB5O_CLICK_S:-68.2} s"; sleep ${SB5O_CLICK_S:-68.2}
          DRIVE_LOG=$R/$cell-DRIVE.LOG $H/lab-drive-xdotool.sh click 56 424 0 >/dev/null 2>&1; clicked=1; log "SB5O clicked"
        fi
        # interactive DOSBox-X never exits by itself: stop our own runner once the manifest is complete
        if /usr/bin/grep -aq '^exit_code=' $st/RUNMANI.LOG 2>/dev/null && /usr/bin/grep -aq 'DOS-PORT work scope=excluded' $st/RUNMANI.LOG 2>/dev/null; then
          sleep 3; kill -TERM $rp 2>/dev/null
        fi
      fi
      sleep 2
    done
    mkdir -p $R/$cell
    [[ -n "$st" ]] && cp $st/RUNMANI.LOG $st/STDOUT.TXT $st/RUN.BAT $st/ACSETUP.CFG $R/$cell/ 2>/dev/null
    log "$cell done stage=$st"
  )
}
for c in "$@"; do
  case $c in
    F2B1) run_cell F2B1 0 bench8 --conf $CONF --include-extra $R/cfg/f2b/ACSETUP.CFG --include-extra $R/cfg/f2b/BENCH.CFG ;;
    AQF1) run_cell AQF1 0 agsquest --conf $CONF --include-extra $R/cfg/aqf/ACSETUP.CFG --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 ;;
    S2M1) run_cell S2M1 0 mmd --conf $CONF --include-extra $R/cfg/s2m/ACSETUP.CFG --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 \
            --env DOSAGS_TAS_AUTO_EXIT_TICK=1000 --env DOSAGS_DIRECT_VSCREEN=0 ;;
    S2F2) run_cell S2F2 1 5days --interactive --conf $CONF --include-extra $R/cfg/s2f/ACSETUP.CFG --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 \
            --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 3 ;;
    SB5O) run_cell SB5O 1 5days --interactive --sb-live --conf $CONF_OPL3 --include-extra $R/cfg/sb5/ACSETUP.CFG \
            --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=16000 ;;
  esac
done
log ALLDONE
