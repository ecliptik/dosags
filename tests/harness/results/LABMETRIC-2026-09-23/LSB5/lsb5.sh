#!/bin/bash
# LSB5 lab count run: SB5O fixture (5 Days own flow, OPL3, sb-live), START clicked so room 99
# begins near hardware's tick 3780 (room 2 ready at tick 1053 on both; 2727 ticks at 40/s = 68 s).
set -u
S=/tmp/claude-1001/-home-claude-git-sdl-dos-ports/dcce1110-1df6-48ac-8758-1bed523f1eb1/scratchpad
L=/home/claude/git/dosags-lab-metric
H=$L/tests/harness
export DOSBOX_DISPLAY_NUM=221
LOG=$S/runs/LSB5-driver.log; mkdir -p $S/runs; : > $LOG
log(){ echo "$(date -u +%H:%M:%S) $*" >> $LOG; }
cd $H
AGS_EXE=$L/build/lab/L2/ags.exe ./run-dosbox.sh 5days --interactive --sb-live --fixed-timestep --no-verify-present \
  --conf $H/confs/dosbox-x-fast-opl3.conf --include-extra $S/cfg/sb5/ACSETUP.CFG \
  --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=16000 --timeout 1500 > $S/runs/LSB5.out 2>&1 &
RUN_PID=$!
log "runner pid $RUN_PID"
stage=""
while kill -0 $RUN_PID 2>/dev/null && [[ -z "$stage" ]]; do
  stage=$(ps -eo pid=,ppid=,args= | awk -v root="$RUN_PID" '
    { pid=$1; ppid=$2; $1=""; $2=""; sub(/^ +/,""); par[pid]=ppid; cmd[pid]=$0 }
    END { for (p in cmd) { if (cmd[p] !~ /^dosbox-x .*-c MOUNT C \/tmp\/dos-port-dosbox\./) continue
      q=p; for (n=0;n<64 && q!="" && q!="0" && q!="1";n++){ if (q==root){ match(cmd[p],/\/tmp\/dos-port-dosbox\.[A-Za-z0-9]*/); print substr(cmd[p],RSTART,RLENGTH); exit } q=par[q] } } }')
  sleep 2
done
log "stage $stage"
[[ -n "$stage" ]] || { log "no stage"; wait $RUN_PID; exit 1; }
while kill -0 $RUN_PID 2>/dev/null && ! /usr/bin/grep -aq 'event=ready room=2' "$stage/STDOUT.TXT" 2>/dev/null; do sleep 0.5; done
log "room 2 ready seen"
sleep 68
log "clicking START"
DRIVE_LOG=$S/runs/LSB5-drive.log $H/lab-drive-xdotool.sh click 56 424 0
for i in 1 2 3 4 5 6; do
  sleep 5
  /usr/bin/grep -aq 'event=start room=99' "$stage/STDOUT.TXT" && { log "room 99 start seen"; break; }
  log "no room 99 yet; click again"; DRIVE_LOG=$S/runs/LSB5-drive.log $H/lab-drive-xdotool.sh click 56 424 0
done
wait $RUN_PID; log "runner exit $?"
