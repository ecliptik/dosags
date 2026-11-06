#!/usr/bin/env bash
# round BATCH (from WBC): power-off guard (coordinator: if the driver's power-off fails while the daemon is down, retry once it's back).
# Waits for the driver to end (ROUND P DONE / driver exit in SUMMARY) or for the cap; then, while power reads ON or
# unreadable, retries `vcctrl power off` every 15 s until it reads on=False. Sends nothing while the driver runs.
V=~/git/vcctrl/bin/vcctrl; S=~/git/dosags/build/ws/roundF1b/SUMMARY.txt; L=~/git/dosags/build/ws/roundF1b/POWERGUARD.txt
CAP=$(( $(date -u -d "$(sed -n "s/^relay-on \([0-9:]*\), cap.*/\1/p" $S)" +%s) + $(sed -n "s/.*(CAP_MIN=\([0-9]*\)).*/\1/p" $S)*60 ))
until /usr/bin/grep -q '^driver exit' $S || (( $(date -u +%s) >= CAP )); do sleep 10; done
echo "$(date -u +%T) guard active (driver ended or cap reached)" >> $L
for i in $(seq 1 240); do
  st=$(timeout 8 $V power state 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin)["power"]; print(d["on"], d.get("power_mw"))' 2>/dev/null)
  if [[ "$st" == False* ]]; then echo "$(date -u +%T) power confirmed OFF: $st" >> $L; touch ${S%/*}/POWERGUARD-DONE; exit 0; fi
  echo "$(date -u +%T) power reads [${st:-unreadable}] -> power off" >> $L
  timeout 20 $V power off > /dev/null 2>&1
  sleep 15
done
echo "$(date -u +%T) GUARD GAVE UP after 60 min: power not confirmed off" >> $L
