#!/usr/bin/env bash
# round RS (from roundRR's, + the lock watch for the Gateway shared with psdoom): record vcctrld availability AND the input
# lock's owner every 10 s. Read-only: `vcctrl activity` and `vcctrl lock status` only, both with </dev/null.
# Logs every failure, every recovery, every daemon_start_t change, and every lock owner that is not this round's
# (run-hw-<RS tag>) or nobody: "FOREIGN LOCK <owner>" -- the driver reads that file after each cell.
V=~/git/vcctrl/bin/vcctrl; L=~/git/dosags/build/ws/roundRS/DAEMON-GAPS.txt; last=""; down=""; lastown=""
while true; do
  now=$(date -u +%T); st=$(timeout 8 $V activity </dev/null 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))' 2>/dev/null)
  if [[ -z "$st" || "$st" == None ]]; then [[ -z "$down" ]] && { down=$now; echo "$now DAEMON DOWN (no answer)" >> $L; }
  else
    [[ -n "$down" ]] && { echo "$now daemon back (down since $down)" >> $L; down=""; }
    [[ -n "$last" && "$st" != "$last" ]] && echo "$now daemon_start_t CHANGED $last -> $st" >> $L
    last=$st
  fi
  own=$(timeout 8 $V lock status </dev/null 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("owner"))' 2>/dev/null)
  if [[ -n "$own" && "$own" != None && "$own" != run-hw-WARMUPRS && "$own" != run-hw-RS* ]]; then
    [[ "$own" != "$lastown" ]] && echo "$now FOREIGN LOCK $own" >> $L; fi
  lastown=$own
  [[ -f ~/git/dosags/build/ws/roundRS/POWERGUARD-DONE ]] && exit 0
  sleep 10
done
