#!/bin/bash
# LOCK1: a gate and an --sb-live cell started together must serialise.
cd ~/git/dosags; O=build/ws/lock1; rm -rf $O; mkdir -p $O
ts() { date -u +%T.%N | cut -c1-12; }
echo "$(ts) gate start" >> $O/timeline
( AGS_EXE=$PWD/build/ws/gate-0209/ags.exe tests/harness/gate-alias.sh --out $PWD/$O/gate --arms idle --no-aq --no-pillarbox --no-bench16 --no-catalogue --no-control > $O/gate.log 2>&1; echo "$(ts) gate end" >> $O/timeline ) &
sleep 3
echo "$(ts) sb-live start" >> $O/timeline
( cd tests/harness && ./run-dosbox.sh bench8 --sb-live --env DOSAGS_TAS_AUTO_EXIT_TICK=200 --timeout 120 > ../../$O/sblive.log 2>&1; echo "$(ts) sb-live end" >> ../../$O/timeline ) &
# watch: who holds, and which dosbox-x runs (with their parents' tool), once a second
while pgrep -f "gate-alias.sh --out $PWD/$O" >/dev/null || pgrep -f 'run-dosbox.sh bench8 --sb-live' >/dev/null; do
  echo "$(ts) who=[$(head -1 /tmp/dos-port-dosbox.lock.who 2>/dev/null)] dbx=[$(pgrep -a dosbox-x | awk '{print $1, ($0 ~ /-silent/ ? "silent" : "live"), $NF}' | tr '\n' ';')]" >> $O/watch
  sleep 1
done
echo done
