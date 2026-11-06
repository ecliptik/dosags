#!/usr/bin/env bash
# round BATCH (from WBC): record vcctrld availability every 10 s (coordinator alert: d5aeb64 deploy may restart the daemon mid-round).
# Read-only: `vcctrl activity` only. Logs every failure, every recovery and every daemon_start_t change.
V=~/git/vcctrl/bin/vcctrl; L=~/git/dosags/build/ws/roundE/DAEMON-GAPS.txt; last=""; down=""
while true; do
  now=$(date -u +%T); st=$(timeout 8 $V activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))' 2>/dev/null)
  if [[ -z "$st" || "$st" == None ]]; then [[ -z "$down" ]] && { down=$now; echo "$now DAEMON DOWN (no answer)" >> $L; }
  else
    [[ -n "$down" ]] && { echo "$now daemon back (down since $down)" >> $L; down=""; }
    [[ -n "$last" && "$st" != "$last" ]] && echo "$now daemon_start_t CHANGED $last -> $st" >> $L
    last=$st
  fi
  [[ -f ~/git/dosags/build/ws/roundE/POWERGUARD-DONE ]] && exit 0
  sleep 10
done
