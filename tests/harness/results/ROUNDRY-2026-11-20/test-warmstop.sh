#!/usr/bin/env bash
# test-warmstop.sh DRIVER SCRATCH -- dry test of driveRY.sh's warm-up stick stop (README sec. 2), before any data.
# Runs the driver's own warmstick lines (grepped out of DRIVER, not retyped) with poweroff stubbed, against fixtures:
#   clean      card-state clean, tee started before START.UTC, ALIVE now, no drop  -> continue (no STOP, no poweroff)
#   card       a card-state "unavailable" sample                                 -> STOP + poweroff
#   kdrop      a kernel "USB disconnect" on the stick's port after START.UTC     -> STOP + poweroff
#   notee      KERN-TEE.txt missing                                              -> STOP + poweroff
#   stale      the last ALIVE heartbeat 5 min old                                -> STOP + poweroff
#   latetee    TEE-START after START.UTC                                         -> STOP + poweroff
set -u
DRV=$1 X=$2
H=$(cd "$(dirname "$0")/../.." && pwd)
WS=$(grep -E '^warmstick\(\)|^if ! warmstick' "$DRV")
[[ $(printf '%s\n' "$WS" | wc -l) == 2 ]] || { echo "the driver's warmstick lines not found"; exit 2; }
now() { date -u -d "@$(( $(date -u +%s) + ${1:-0} ))" '+%Y-%m-%d %H:%M:%S'; }
iso() { date -u -d "@$(( $(date -u +%s) + ${1:-0} ))" '+%Y-%m-%dT%H:%M:%S.000000+00:00'; }
mk() {  # case: fixture dir $X/<case>/{ws,res/WARMUPRY-D}
  local c=$1 R=$X/$1/res/WARMUPRY-D W=$X/$1/ws
  rm -rf "${X:?}/$c"; mkdir -p "$R/witness" "$W"
  date -u -d "@$(( $(date -u +%s) - 600 ))" '+%Y-%m-%dT%H:%M:%SZ' > "$R/START.UTC"
  printf '110130.595 state=locked frames=1 last_frame_age_s=0.02\n110132.722 state=frozen frames=9 last_frame_age_s=0.03\n' > "$R/witness/card-state.log"
  { echo "### TEE-START $(now -900) UTC"; echo "### STICK-PORT 1-2"
    echo "$(iso -2000) daemon-host kernel: usb 1-2: USB disconnect, device number 4   (before START: not counted)"
    echo "### ALIVE $(now -20) UTC"; } > "$W/KERN-TEE.txt"
}
run() {  # case expect(continue|STOP)
  local c=$1 want=$2 B=$X/$1/ws RES=$X/$1/res D=D S=$X/$1/ws/SUMMARY.txt POW=0
  poweroff() { POW=1; echo "poweroff (stub)" >> $S; }
  : > "$S"
  ( eval "$WS"; echo "continue" >> $S ) ; local got
  got=$(grep -q '^STOP after WARMUPRY: stick' "$S" && echo STOP || echo continue)
  local pw; pw=$(grep -c 'poweroff (stub)' "$S")
  printf '%-8s want %-8s got %-8s poweroff %s  | %s\n' "$c" "$want" "$got" "$pw" "$(grep -m1 '^WARMUP stick' "$S" | cut -c1-150)"
  [[ "$got" == "$want" ]] && { [[ "$want" == continue && "$pw" == 0 ]] || [[ "$want" == STOP && "$pw" == 1 ]]; }
}
fail=0
mk clean;   run clean continue || fail=1
mk card;    echo '110134.824 state=unavailable frames=9 last_frame_age_s=6.786' >> $X/card/res/WARMUPRY-D/witness/card-state.log; run card STOP || fail=1
mk kdrop;   echo "$(iso -120) daemon-host kernel: usb 1-2: USB disconnect, device number 5" >> $X/kdrop/ws/KERN-TEE.txt; run kdrop STOP || fail=1
mk notee;   rm $X/notee/ws/KERN-TEE.txt; run notee STOP || fail=1
mk stale;   sed -i "s/^### ALIVE .*/### ALIVE $(now -300) UTC/" $X/stale/ws/KERN-TEE.txt; run stale STOP || fail=1
mk latetee; sed -i "s/^### TEE-START .*/### TEE-START $(now -60) UTC/" $X/latetee/ws/KERN-TEE.txt; run latetee STOP || fail=1
echo "warm-up stop dry test: $([[ $fail == 0 ]] && echo PASS || echo FAIL)"
exit $fail
