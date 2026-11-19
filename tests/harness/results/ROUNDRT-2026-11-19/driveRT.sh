#!/usr/bin/env bash
# Round RT driver (from roundRS/driveRS.sh): the pacer A/B on MS3 (ROUNDRT README, sdlports' review first). A = the ags 0383
# release (rs0383.exe, main's binary, no env switch); P = the same code + tests/harness/apply-pace-rig.py (rtpace.exe,
# release flavour) with DOSAGS_LAB_STALL_MS=45: a top-level tick over 45 ms is a pause, its debt forgiven (0163's rule at
# 45 ms). Round RR's MS3 play line for both (DRIVE 6 ms, exit 12440, AGSSAVE.007, 512x384 cfg ON, --no-fine-timing).
# Read per cell by tests/harness/pa-read.py; the term PACE-MS3 by `pa-read.py verdict` at the end.
# ONE power-on. USB4VC 0.5.109. MS3 target: 99% frames displayed; proof bar a registered pair (RTP1, RTP2), both >= 99.0%,
# with game time lost G <= 2.0% per run in every P cell (operator, 2026-11-19).
# Order: WARMUPRT -> RTCALQ [-> RTCAL on a calq miss] -> RTA1 RTP1 RTP2 RTA2 (the A/B block, ABBA; needed whole) -> RTP3
# (a third P cell: the time rule, never the bar; dropped first on time).
# Every vcctrl call carries </dev/null (sdlports' check, round RS).
set -u
HERE_L=~/git/dosags/build/ws/roundL   # cellL.sh + snapshots.py (the fixed comparator) are reused as-is
REPO=~/git/dosags; B=$REPO/build/ws/roundRT; H=$REPO/tests/harness; RES=$H/results; S=$B/SUMMARY.txt
D=2026-11-19; export CELL_DATE=$D
CAP_MIN=120   # minutes of mains-on time from relay-on (expected ~80, ~91 with a full cal; the README's arithmetic)
[[ "$CAP_MIN" =~ ^[0-9]+$ ]] && (( CAP_MIN >= 30 && CAP_MIN <= 120 )) || {
  echo "STOP $(date -u +%T): CAP_MIN=$CAP_MIN is not set to a number of minutes (30-120)" >> $B/SUMMARY.txt; echo "driveRT.sh: STOP: CAP_MIN unset" >&2; exit 1; }
# the round date names every results dir and README; a stale D is refused before anything touches the target
# (coordinator 2026-09-26): re-date the dirs, READMEs and this line in a "re-date, before any data" commit instead.
# round P9 (coordinator 2026-09-29): no --date-ok bypass; every staged cell's pre-registered results dir must carry the
# ACTUAL launch date (UTC) -- $RES/<TAG>-<today>/README.md for every tag of every staged block -- or nothing starts.
TODAY=$(date -u +%F)
if [[ "$D" != "$TODAY" ]]; then
  echo "STOP $(date -u +%T): round date D=$D != today $TODAY (UTC); re-date before any data" >> $B/SUMMARY.txt
  echo "driveRT.sh: STOP: D=$D != $TODAY; re-date first" >&2; exit 1; fi
_miss=""
for _t in WARMUPRT RTCALQ RTCAL RTA1 RTP1 RTP2 RTA2 RTP3; do
  [[ -f $RES/$_t-$TODAY/README.md ]] || _miss="$_miss $_t"
done
if [[ -n "$_miss" ]]; then
  echo "STOP $(date -u +%T): no pre-registered README dated $TODAY for:$_miss (a re-date commit precedes any data)" >> $B/SUMMARY.txt
  echo "driveRT.sh: STOP: README missing for$_miss at $TODAY" >&2; exit 1; fi
V=~/git/vcctrl/bin/vcctrl
FB="--env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1"
MMDCFG="--extra-file $H/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG"
C512="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
sumline() { local t=$1 R=$RES/$1-$D
  echo "$t: $(/usr/bin/grep -a 'run-hw exit' $R/run-hw.out) pre=$(cut -c1-12 $R/PRE-STAGE-SHA256.txt) post=$(cut -c1-12 $R/POST-RUN-SHA256.txt) staged_has_pre=$(/usr/bin/grep -c "$(cut -c1-64 $R/PRE-STAGE-SHA256.txt)" $R/STAGED-SHA256.txt) $(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*\|build_dirty=[0-9]\|tick_rate=[0-9.]*\|tick_rate_steady=[0-9.]*' $R/*.LOG 2>/dev/null | sort -u | tr '\n' ' ') recover=$(ls $R/RECOVERY.TXT 2>/dev/null | wc -l) inputlog=$( [[ -f $R/INPUT-LOG-VOID.txt ]] && echo "VOID:$(head -c 80 $R/INPUT-LOG-VOID.txt)" || echo "ok:$(wc -l < $R/INPUT-LOG.jsonl 2>/dev/null)" ) fw=$( [[ -f $R/FW-VOID.txt ]] && echo "VOID:$(head -c 80 $R/FW-VOID.txt)" || { [[ -f $R/FIRMWARE-VERSION-UNREAD.txt ]] && echo UNREAD || echo OK; } ) xcheck=$( [[ -f $R/CROSSCHECK-NA.txt ]] && echo NA || echo ok ) capture=$( [[ -f $R/witness/WITNESS-CAPTURE-STALE.txt ]] && echo STALE || echo ok ) rooms=$(/usr/bin/grep -aho 'Now in room [0-9]*' $R/STDOUT.TXT 2>/dev/null | sort -u | tr '\n' ',') $(date -u +%T)" >> $S; }
# manifest stamps per staged exe (LAB-WB 36; LAB-JOURNEYS 8.35 note; PLAN D35HW; round H cap3c; round L); a mismatch VOIDs the cell
declare -A STAMP=([l308.exe]=bc9c3704a839)   # + rs0383.STAMP / rtpace.STAMP below
for _s in $B/*.STAMP; do [[ -f $_s ]] && STAMP[$(basename $_s .STAMP).exe]=$(cat $_s); done
for _e in rs0383.exe rtpace.exe; do [[ "${STAMP[$_e]:-}" =~ ^[0-9a-f]{12}$ ]] || { echo "STOP: no 12-hex manifest stamp recorded for $_e ($B/${_e%.exe}.STAMP)" >> $B/SUMMARY.txt; exit 1; }; done
[[ -f $B/ORDER-CONFIRMED ]] || { echo "STOP: round RT's order is not confirmed yet (build/ws/roundRT/ORDER-CONFIRMED missing)"; exit 1; }
export FW_EXPECT=0.5.109
export FLASH_REPORT="vcctrl flash report 2026-09-25: USB4VC 0.5.107 counters build, hex sha256 98a8b9aa..."
stampcheck() { local t=$1 e=$2 R=$RES/$1-$D got; got=$(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*' $R/*.LOG 2>/dev/null | head -1 | cut -d= -f2)
  if [[ "$got" == "${STAMP[$(basename $e)]}" ]]; then echo "$t: stamp OK $got" >> $S
  else echo "$t: STAMP-VOID manifest $got, want ${STAMP[$(basename $e)]} ($(basename $e))" >> $S; fi; }
cell() { local t=$1; shift; $B/cellRT.sh "$t" "$@" > /dev/null 2>&1; sumline "$t"; stampcheck "$t" "$3"; lockcheck "$t"
  /usr/bin/grep -q 'run-hw exit=0' $RES/$t-$D/run-hw.out || { echo "STOP after $t" >> $S
    # no recovery cycle from this driver: any power cycle goes to the operator. A STOP is attributed by hand from the
    # cell's records (README): in play = a finding about the binary; outside AGS = a rig stop.
    poweroff; exit 1; }; }
# a foreign input-lock owner during a cell (daemongap's lock watch) taints it and ends the round after it (psdoom)
lockcheck() { local t=$1 n; n=$(/usr/bin/grep -c 'FOREIGN LOCK' $B/DAEMON-GAPS.txt 2>/dev/null)
  if (( ${n:-0} > ${LOCKSEEN:-0} )); then echo "$t: TAINTED -- a foreign input-lock owner during the cell: $(/usr/bin/grep 'FOREIGN LOCK' $B/DAEMON-GAPS.txt | tail -1)" >> $S
    LOCKSEEN=$n; echo "STOP after $t: foreign lock" >> $S; poweroff; exit 1; fi; }
LOCKSEEN=0
# presses sent == planned, before any gate: the DRIVE-WALK.LOG header's planned count against its ok=1 click lines
presscheck() { local t=$1 R=$RES/$1-$D p n; p=$(sed -n 's/.*, \([0-9]*\) presses.*/\1/p' $R/DRIVE-WALK.LOG 2>/dev/null | head -1)
  n=$(/usr/bin/grep -c ' click [0-9]* .* ok=1 ' $R/DRIVE-WALK.LOG 2>/dev/null)
  if [[ -n "$p" && "$p" == "$n" ]]; then echo "$t: PRESSES OK $n of $p" >> $S; return 0; fi
  echo "$t: PRESSES SHORT: sent $n of planned ${p:-?} -- not gated, not read as a play cell" >> $S; return 1; }
poweroff() { [[ -s $B/ACTIVE-CELL.txt ]] && echo "poweroff() fired DURING cell: $(cat $B/ACTIVE-CELL.txt)" >> $S; $V </dev/null power off >/dev/null 2>&1; sleep 5; echo "power OFF $(date -u +%T): $($V </dev/null power state 2>&1 | python3 -c 'import json,sys; d=json.load(sys.stdin)["power"]; print("on=%s mW=%s" % (d.get("on"), d.get("mw", d.get("power_mw"))))' 2>&1)" >> $S
  kill $CW 2>/dev/null; }
trap 'echo "driver exit $? $(date -u +%T)" >> $S' EXIT
echo "round RT start $(date -u +%T)" >> $S
( cd $B && sha256sum -c expected.txt ) >> $S 2>&1 || { echo "STOP: a staged binary does not match its record" >> $S; exit 1; }
if [[ "$($V </dev/null power state | python3 -c 'import json,sys; print(json.load(sys.stdin)["power"]["on"])')" != False ]]; then
  echo "STOP: target already on -- not this driver's power-on" >> $S; exit 1; fi
# the Gateway is shared with psdoom: nothing else may hold the input lock when this round powers on
_own=$($V </dev/null lock status 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("owner"))' 2>/dev/null)
if [[ "$_own" != None ]]; then echo "STOP: the input lock is held by [$_own] -- not powering on" >> $S; exit 1; fi
echo "pre-power-on: lock unheld; activity: $($V </dev/null activity 2>&1 | head -c 300 | tr '\n' ' ')" >> $S
# capture pre-flight (2026-09-27, after round T ran with the capture stick absent): the card's state is printed before the
# power-on so a dead capture is seen before the first cell. Reported, not a stop: the camera still witnesses.
echo "capture pre-flight: $($V </dev/null video state 2>&1 | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("device_present=%s state=%s last_frame_age_s=%s" % (d.get("device_present"), d.get("state"), d.get("last_frame_age_s")))
except Exception as e: print("UNREADABLE (%s)" % e)' 2>&1)" >> $S
START=$(date -u +%s); $V </dev/null power on; CAP=$(( START + CAP_MIN*60 ))
echo "relay-on $(date -u -d @$START +%T), cap $(date -u -d @$CAP +%T) (CAP_MIN=$CAP_MIN)" >> $S
# the safeguards start here, from the driver itself (round R: a separate post-launch command was denied)
setsid nohup $B/powerguard.sh > /dev/null 2>&1 < /dev/null &
setsid nohup $B/daemongap.sh > /dev/null 2>&1 < /dev/null &
echo "powerguard + daemongap started $(date -u +%T)" >> $S
echo "vcctrld daemon_start_t at round start: $($V </dev/null activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))')" >> $S
# cap watchdog: power off at cap - 45 s if still on
( T=$(( CAP - 45 )); while (( $(date -u +%s) < T )); do sleep 15; done
  if [[ "$($V </dev/null power state | python3 -c 'import json,sys; print(json.load(sys.stdin)["power"]["on"])')" == True ]]; then
    $V </dev/null power off; echo "capwatch: powered OFF at $(date -u +%T)" >> $S; fi ) & CW=$!
sleep 75
ccell() {  # tag pkg drive exe normal_timeout typical_s args...
  local t=$1 pkg=$2 d=$3 e=$4 nt=$5 ty=$6; shift 6
  local left=$(( CAP - 240 - $(date -u +%s) ))
  if (( left < ty )); then echo "$t dropped: ${left}s left, typical ${ty}s ($(date -u +%T)) -> a later round" >> $S; return 2; fi
  local to=$(( nt < left ? nt : left ))
  echo "$t start $(date -u +%T) --timeout $to" >> $S
  echo "$t $(date -u +%T)" > $B/ACTIVE-CELL.txt
  cell "$t" "$pkg" "$d" "$e" --timeout "$to" "$@"; local rc=$?
  : > $B/ACTIVE-CELL.txt
  return $rc
}
MM="$FB --env DOSAGS_TAS_AUTO_EXIT_TICK=1000 $MMDCFG"
CUT=0
left() { echo $(( CAP - 240 - $(date -u +%s) )); }
need() {
  if (( CUT )); then echo "$1 dropped: an earlier block was cut ($(date -u +%T)) -> a later round" >> $S; return 1; fi
  local l; l=$(left); if (( l < $2 )); then CUT=1; echo "$1 dropped as a block: ${l}s left < ${2}s ($(date -u +%T)) -> a later round" >> $S; return 1; fi; }
jobstate() { $V </dev/null file-status 1 2>/dev/null | python3 -c '
import json,sys
try: d=json.load(sys.stdin)
except Exception: print("? ?"); sys.exit()
j=d.get("job") or d.get("status") or d
print(j.get("kind"), j.get("running"))' ; }
pull_wait() {  # outdir cap_s : the pull must be SEEN running, then finished; its status JSON saved (round O fix)
  local O=$1 cap=$2 seen=0 last="" end=$(( $(date -u +%s) + $2 ))
  while (( $(date -u +%s) < end )); do
    last=$(jobstate); [[ "$last" == "pull True" ]] && seen=1
    (( seen )) && [[ "$last" == "pull False" ]] && break
    sleep 5
  done
  $V </dev/null file-status 100 > $O/file-status.json 2>&1
  if (( ! seen )); then echo "pull never seen running (last: $last)"; elif [[ "$last" != "pull False" ]]; then echo "pull not finished in ${cap}s (last: $last)"; else echo "pull finished"; fi
}
wedge_fetch() {  # round L's: the cell's one recovery (mains cycle), then a read-only fetch (pull-wait fixed)
  local t=$1; shift; local O=$RES/$t-$D/fetch f got=""; mkdir -p $O
  echo "$t: wedged at exit -> one recovery (power cycle), then read-only fetch ($(date -u +%T))" >> $S
  $V </dev/null power cycle --confirm cycle >/dev/null 2>&1 || $V </dev/null power cycle >/dev/null 2>&1; sleep 90
  $V </dev/null get-file "$@" --return --from 'C:\DOSAGS' > $O/get-file.out 2>&1
  echo "$t fetch: $(pull_wait $O 600)" >> $S
  for f in "$@"; do $V </dev/null pulled save "$f" --out "$O/$f" >/dev/null 2>&1 || true; [[ -s $O/$f ]] && got="$got $f"; done
  ( cd $O && [[ -n "$got" ]] && sha256sum $got > SHA256SUMS ); echo "$t fetch collected: [${got# }] (not collected = the rest)" >> $S
}
# (a) warm-up: rig health and the round's first BLASTER read; not scored
BL=(--pre-line 'ECHO %BLASTER% > BLASTER.TXT' --collect BLASTER.TXT)
ccell WARMUPRT mmd 0 $B/l308.exe 1500 480 $MM "${BL[@]}"
_bl=$(tr -d '\r' < $RES/WARMUPRT-$D/BLASTER.TXT 2>/dev/null | sed 's/[[:space:]]*$//')
echo "WARMUPRT BLASTER.TXT: [$_bl]" >> $S
if [[ "$_bl" != "A220 I7 D3 P330 T3" ]]; then echo "STOP after WARMUPRT: BLASTER witness [$_bl] != [A220 I7 D3 P330 T3]" >> $S; poweroff; exit 1; fi
# close watch (as P9): the warm-up's 320x200 title is never locked ("nolock"); any other STALE kind, or no capture device, stops
if [[ -f $RES/WARMUPRT-$D/witness/WITNESS-CAPTURE-STALE.txt ]] && ! grep -q '"stale_kind": "nolock"' $RES/WARMUPRT-$D/witness/WITNESS-CAPTURE-STALE.txt; then
  echo "STOP after WARMUPRT: capture STALE in the warm-up ($(head -c 200 $RES/WARMUPRT-$D/witness/WITNESS-CAPTURE-STALE.txt))" >> $S; poweroff; exit 1; fi
_vs=$($V </dev/null video state 2>&1 | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("%s %s" % (d.get("device_present"), d.get("state")))
except Exception as e: print("UNREADABLE")' 2>&1)
echo "after WARMUPRT: capture $_vs" >> $S
if [[ "$_vs" != True* ]]; then echo "STOP after WARMUPRT: capture device not present [$_vs]" >> $S; poweroff; exit 1; fi
CFGON="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
export RUNHW_MIN_WAIT_S=270
# (b) DRIVE 6 calibration (DRIVE6-RIG-CHECKS Q0-Q4 / G0 G1 C1-C10; drive6-gate.sh). The short re-check (calq, 13 presses)
# against round RJ's passing full cal (RJCAL); on ANY calq miss the full cal (RTCAL) runs in-round; a full-cal RECENTRE or
# STOP ends the MS3 block (no third cal this power-on). A press-path STOP is never answered mid-round (sdlports).
PLAY="--no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=12440 --ags-arg --loadsavedgame --ags-arg 7 --extra-file $B/AGSSAVE.007:AGSSAVE.007 $CFGON"
export DRIVE6_DY=15 DRIVE6_DXL=52 DRIVE6_DXA=75 DRIVE6_DXB=42
REF=$RES/RJCAL-2026-11-11
CALOK=0
gate() { local t=$1 g; shift; g=$($H/drive6-gate.sh "$RES/$t-$D" "$@" 2>&1 | tail -1); echo "$t: $g" >> $S; echo "$g"; }
apply() { local v; for v in $(sed -n 's/^GATE [A-Z]* //p' <<<"$1"); do [[ "$v" =~ ^DRIVE6_(DY|DXL|DXA|DXB)=[0-9]+$ ]] && export "$v"; done
  echo "DRIVE6 values now: DY=$DRIVE6_DY DXL=$DRIVE6_DXL DXA=$DRIVE6_DXA DXB=$DRIVE6_DXB" >> $S; }
if need RTCALQ 1520; then   # calq 760 + full cal 760 (counted up front); the blocks after keep their own graded needs
  DRIVE6_MODE=calq ccell RTCALQ mmd 6 $B/rs0383.exe 1800 750 $PLAY "${BL[@]}"
  G="GATE NOT RUN"; presscheck RTCALQ && G=$(gate RTCALQ --recheck "$REF")
  case "$G" in
    "GATE PASS "*) apply "$G"; CALOK=1 ;;
    *) DRIVE6_MODE=cal ccell RTCAL mmd 6 $B/rs0383.exe 1800 750 $PLAY "${BL[@]}"
       G2="GATE NOT RUN"; presscheck RTCAL && G2=$(gate RTCAL --no-recentre); case "$G2" in "GATE PASS "*) apply "$G2"; CALOK=1 ;; esac ;;
  esac
fi
(( CALOK )) || echo "play blocks not run: DRIVE 6 calibration did not PASS ($(date -u +%T))" >> $S
CUT=0
# (c) the A/B block: A = the 0383 release (no env switch: main's behaviour); P = rtpace.exe with the 45 ms rule. The play
# gate and the pairing are run and printed for every cell; what VALIDATES a cell is pa-read.py's rule.
PPLAY="$PLAY --env DOSAGS_LAB_STALL_MS=45"
SP=$(cat $B/rtpace.STAMP 2>/dev/null)
play() { local t=$1 kind=$2 exe=$3 ty=$4; shift 4
  DRIVE6_MODE=ms ccell $t mmd 6 $exe 1800 $ty "$@" "${BL[@]}" || return
  presscheck $t || { DONE+=("$RES/$t-$D:$kind"); return; }
  local g; g=$($H/drive6-gate.sh --play "$RES/$t-$D" 2>&1 | tail -1); echo "$t: $g (information)" >> $S
  python3 $H/ms3-pairing.py "$RES/$t-$D" > $RES/$t-$D/PAIRING.txt 2>&1; sed "s/^/$t: /" $RES/$t-$D/PAIRING.txt >> $S
  python3 $H/pa-read.py --stamp-p "$SP" --t-ms 45 cell "$RES/$t-$D" $kind > $RES/$t-$D/READ.txt 2>&1; sed "s/^/$t: /" $RES/$t-$D/READ.txt >> $S
  DONE+=("$RES/$t-$D:$kind"); }
DONE=()
if (( CALOK )); then
  need RTA1 3040 && play RTA1 A $B/rs0383.exe 750 $PLAY     # the A/B block is needed whole (A P P A)
  need RTP1 2280 && play RTP1 P $B/rtpace.exe 750 $PPLAY
  need RTP2 1520 && play RTP2 P $B/rtpace.exe 750 $PPLAY
  need RTA2 760 && play RTA2 A $B/rs0383.exe 750 $PLAY
  CUT=0   # the third P cell last, dropped first
  need RTP3 760 && play RTP3 P $B/rtpace.exe 750 $PPLAY
fi
(( ${#DONE[@]} )) && python3 $H/pa-read.py --stamp-p "$SP" --t-ms 45 verdict "${DONE[@]}" > $B/VERDICT.txt 2>&1 && sed 's/^/VERDICT: /' $B/VERDICT.txt >> $S
CUT=0
unset RUNHW_MIN_WAIT_S
echo "vcctrld daemon_start_t at round end: $($V </dev/null activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))')" >> $S
poweroff
echo "ROUND RT DONE $(date -u +%T)" >> $S
