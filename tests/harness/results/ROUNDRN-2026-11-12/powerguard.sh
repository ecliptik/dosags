#!/usr/bin/env bash
# round BATCH (from WBC): power-off guard (coordinator: if the driver's power-off fails while the daemon is down, retry once it's back).
# Waits for the driver to end (ROUND P DONE / driver exit in SUMMARY) or for the cap; then, while power reads ON or
# unreadable, retries `vcctrl power off` every 15 s until it reads on=False. Sends nothing while the driver runs.
V=~/git/vcctrl/bin/vcctrl; S=~/git/dosags/build/ws/roundRN/SUMMARY.txt; L=~/git/dosags/build/ws/roundRN/POWERGUARD.txt
# Refuse to run without the driver's relay-on line (round CF 2026-11-07: a guard started by hand before relay-on computed its cap
# from an empty time, read power OFF and wrote POWERGUARD-DONE, which stopped the driver's daemongap). The driver starts this
# guard itself right after relay-on; never start it by hand.
_ron=$(sed -n "s/^relay-on \([0-9:]*\), cap.*/\1/p" $S 2>/dev/null); _cap=$(sed -n "s/.*(CAP_MIN=\([0-9]*\)).*/\1/p" $S 2>/dev/null)
if [[ -z "$_ron" || -z "$_cap" ]]; then echo "$(date -u +%T) REFUSED: no relay-on / CAP_MIN line in SUMMARY.txt yet; not guarding, no marker written" >> $L; exit 2; fi
CAP=$(( $(date -u -d "$_ron" +%s) + _cap*60 ))
until /usr/bin/grep -q '^driver exit' $S || (( $(date -u +%s) >= CAP )); do sleep 10; done
echo "$(date -u +%T) guard active (driver ended or cap reached)" >> $L
A=${S%/*}/ACTIVE-CELL.txt; [[ -s $A ]] && echo "$(date -u +%T) guard fired DURING cell: $(cat $A)" | tee -a $L >> $S
for i in $(seq 1 240); do
  st=$(timeout 8 $V power state 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin)["power"]; print(d["on"], d.get("power_mw"))' 2>/dev/null)
  if [[ "$st" == False* ]]; then echo "$(date -u +%T) power confirmed OFF: $st" >> $L; touch ${S%/*}/POWERGUARD-DONE; exit 0; fi
  echo "$(date -u +%T) power reads [${st:-unreadable}] -> power off" >> $L
  timeout 20 $V power off > /dev/null 2>&1
  sleep 15
done
echo "$(date -u +%T) GUARD GAVE UP after 60 min: power not confirmed off" >> $L
