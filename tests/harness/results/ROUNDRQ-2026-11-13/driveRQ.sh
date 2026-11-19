#!/usr/bin/env bash
# Round RQ driver (from roundRO/driveRO.sh): the heap lock-policy ABBA on MS3 (ags 0380; operator 2026-11-13 via sdlports).
# Diagnostic only (no target, no proof claim). The 0380 release (main e90a228b, DOSAGS_RELEASE=1, sha256 0e6637f4..., stamp
# b66bd61cb1df), RO's MS3 play line (DRIVE 6 ms, exit tick 12440, AGSSAVE.007, 512x384 cfg ON), memlog gone (0378):
# O = no switch (0379's behaviour), U = DOSAGS_HEAP_UNLOCK=1, P = DOSAGS_HEAP_PREGROW_KB=6144. Every cell also runs
# `DIR C:\ /A` before and after the game (ROOTPRE.TXT / ROOTPOST.TXT). Read per cell by tests/harness/rq-steps.py; the
# round's terms by `rq-steps.py verdict` at the end. ONE power-on. USB4VC 0.5.109.
# Order: WARMUPRQ -> RQCALQ [-> RQCAL on a calq miss] -> RQO1 RQU1 RQP1 RQP2 RQU2 RQO2.
set -u
HERE_L=~/git/dosags/build/ws/roundL   # cellL.sh + snapshots.py (the fixed comparator) are reused as-is
REPO=~/git/dosags; B=$REPO/build/ws/roundRQ; H=$REPO/tests/harness; RES=$H/results; S=$B/SUMMARY.txt
D=2026-11-13; export CELL_DATE=$D
CAP_MIN=120   # minutes of mains-on time from relay-on (typical ~100: WARMUP ~10.5, calq 12.5 [+ cal 12.5], ABBA 6 x 12.5)
[[ "$CAP_MIN" =~ ^[0-9]+$ ]] && (( CAP_MIN >= 30 && CAP_MIN <= 120 )) || {
  echo "STOP $(date -u +%T): CAP_MIN=$CAP_MIN is not set to a number of minutes (30-120)" >> $B/SUMMARY.txt; echo "driveRQ.sh: STOP: CAP_MIN unset" >&2; exit 1; }
# the round date names every results dir and README; a stale D is refused before anything touches the target
# (coordinator 2026-09-26): re-date the dirs, READMEs and this line in a "re-date, before any data" commit instead.
# round P9 (coordinator 2026-09-29): no --date-ok bypass; every staged cell's pre-registered results dir must carry the
# ACTUAL launch date (UTC) -- $RES/<TAG>-<today>/README.md for every tag of every staged block -- or nothing starts.
TODAY=$(date -u +%F)
if [[ "$D" != "$TODAY" ]]; then
  echo "STOP $(date -u +%T): round date D=$D != today $TODAY (UTC); re-date before any data" >> $B/SUMMARY.txt
  echo "driveRQ.sh: STOP: D=$D != $TODAY; re-date first" >&2; exit 1; fi
_miss=""
for _t in WARMUPRQ RQCALQ RQCAL RQO1 RQU1 RQP1 RQP2 RQU2 RQO2; do
  [[ -f $RES/$_t-$TODAY/README.md ]] || _miss="$_miss $_t"
done
if [[ -n "$_miss" ]]; then
  echo "STOP $(date -u +%T): no pre-registered README dated $TODAY for:$_miss (a re-date commit precedes any data)" >> $B/SUMMARY.txt
  echo "driveRQ.sh: STOP: README missing for$_miss at $TODAY" >&2; exit 1; fi
V=~/git/vcctrl/bin/vcctrl
FB="--env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1"
MMDCFG="--extra-file $H/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG"
C512="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
sumline() { local t=$1 R=$RES/$1-$D
  echo "$t: $(/usr/bin/grep -a 'run-hw exit' $R/run-hw.out) pre=$(cut -c1-12 $R/PRE-STAGE-SHA256.txt) post=$(cut -c1-12 $R/POST-RUN-SHA256.txt) staged_has_pre=$(/usr/bin/grep -c "$(cut -c1-64 $R/PRE-STAGE-SHA256.txt)" $R/STAGED-SHA256.txt) $(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*\|build_dirty=[0-9]\|tick_rate=[0-9.]*\|tick_rate_steady=[0-9.]*' $R/*.LOG 2>/dev/null | sort -u | tr '\n' ' ') recover=$(ls $R/RECOVERY.TXT 2>/dev/null | wc -l) inputlog=$( [[ -f $R/INPUT-LOG-VOID.txt ]] && echo "VOID:$(head -c 80 $R/INPUT-LOG-VOID.txt)" || echo "ok:$(wc -l < $R/INPUT-LOG.jsonl 2>/dev/null)" ) fw=$( [[ -f $R/FW-VOID.txt ]] && echo "VOID:$(head -c 80 $R/FW-VOID.txt)" || { [[ -f $R/FIRMWARE-VERSION-UNREAD.txt ]] && echo UNREAD || echo OK; } ) xcheck=$( [[ -f $R/CROSSCHECK-NA.txt ]] && echo NA || echo ok ) capture=$( [[ -f $R/witness/WITNESS-CAPTURE-STALE.txt ]] && echo STALE || echo ok ) rooms=$(/usr/bin/grep -aho 'Now in room [0-9]*' $R/STDOUT.TXT 2>/dev/null | sort -u | tr '\n' ',') $(date -u +%T)" >> $S; }
# manifest stamps per staged exe (LAB-WB 36; LAB-JOURNEYS 8.35 note; PLAN D35HW; round H cap3c; round L); a mismatch VOIDs the cell
declare -A STAMP=([l308.exe]=bc9c3704a839)
for _s in $B/*.STAMP; do [[ -f $_s ]] && STAMP[$(basename $_s .STAMP).exe]=$(cat $_s); done
[[ -f $B/ORDER-CONFIRMED ]] || { echo "STOP: round RQ's order is not confirmed yet (build/ws/roundRQ/ORDER-CONFIRMED missing)"; exit 1; }
export FW_EXPECT=0.5.109
export FLASH_REPORT="vcctrl flash report 2026-09-25: USB4VC 0.5.107 counters build, hex sha256 98a8b9aa..."
stampcheck() { local t=$1 e=$2 R=$RES/$1-$D got; got=$(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*' $R/*.LOG 2>/dev/null | head -1 | cut -d= -f2)
  if [[ "$got" == "${STAMP[$(basename $e)]}" ]]; then echo "$t: stamp OK $got" >> $S
  else echo "$t: STAMP-VOID manifest $got, want ${STAMP[$(basename $e)]} ($(basename $e))" >> $S; fi; }
cell() { local t=$1; shift; $B/cellRQ.sh "$t" "$@" > /dev/null 2>&1; sumline "$t"; stampcheck "$t" "$3"
  /usr/bin/grep -q 'run-hw exit=0' $RES/$t-$D/run-hw.out || { echo "STOP after $t" >> $S
    # pre-registered (sdlports 2026-11-13): a STOP in a U cell is UNLOCK FAILED unless attributed to the rig (README's
    # attribution rule, read by hand from STDOUT / RUNMANI / camera / capture); no recovery cycle from this driver --
    # any power cycle goes to the operator through sdlports
    [[ $t == RQU* ]] && echo "$t: STOP IN U CELL (UNLOCK FAILED unless attributed to the rig)" >> $S
    poweroff; exit 1; }; }
poweroff() { [[ -s $B/ACTIVE-CELL.txt ]] && echo "poweroff() fired DURING cell: $(cat $B/ACTIVE-CELL.txt)" >> $S; $V power off >/dev/null 2>&1; sleep 5; echo "power OFF $(date -u +%T): $($V power state 2>&1 | python3 -c 'import json,sys; d=json.load(sys.stdin)["power"]; print("on=%s mW=%s" % (d.get("on"), d.get("mw", d.get("power_mw"))))' 2>&1)" >> $S
  kill $CW 2>/dev/null; }
trap 'echo "driver exit $? $(date -u +%T)" >> $S' EXIT
echo "round RQ start $(date -u +%T)" >> $S
( cd $B && sha256sum -c expected.txt ) >> $S 2>&1 || { echo "STOP: a staged binary does not match its record" >> $S; exit 1; }
if [[ "$($V power state | python3 -c 'import json,sys; print(json.load(sys.stdin)["power"]["on"])')" != False ]]; then
  echo "STOP: target already on -- not this driver's power-on" >> $S; exit 1; fi
# capture pre-flight (2026-09-27, after round T ran with the capture stick absent): the card's state is printed before the
# power-on so a dead capture is seen before the first cell. Reported, not a stop: the camera still witnesses.
echo "capture pre-flight: $($V video state 2>&1 | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("device_present=%s state=%s last_frame_age_s=%s" % (d.get("device_present"), d.get("state"), d.get("last_frame_age_s")))
except Exception as e: print("UNREADABLE (%s)" % e)' 2>&1)" >> $S
START=$(date -u +%s); $V power on; CAP=$(( START + CAP_MIN*60 ))
echo "relay-on $(date -u -d @$START +%T), cap $(date -u -d @$CAP +%T) (CAP_MIN=$CAP_MIN)" >> $S
# the safeguards start here, from the driver itself (round R: a separate post-launch command was denied)
setsid nohup $B/powerguard.sh > /dev/null 2>&1 < /dev/null &
setsid nohup $B/daemongap.sh > /dev/null 2>&1 < /dev/null &
echo "powerguard + daemongap started $(date -u +%T)" >> $S
echo "vcctrld daemon_start_t at round start: $($V activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))')" >> $S
# cap watchdog: power off at cap - 45 s if still on
( T=$(( CAP - 45 )); while (( $(date -u +%s) < T )); do sleep 15; done
  if [[ "$($V power state | python3 -c 'import json,sys; print(json.load(sys.stdin)["power"]["on"])')" == True ]]; then
    $V power off; echo "capwatch: powered OFF at $(date -u +%T)" >> $S; fi ) & CW=$!
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
jobstate() { $V file-status 1 2>/dev/null | python3 -c '
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
  $V file-status 100 > $O/file-status.json 2>&1
  if (( ! seen )); then echo "pull never seen running (last: $last)"; elif [[ "$last" != "pull False" ]]; then echo "pull not finished in ${cap}s (last: $last)"; else echo "pull finished"; fi
}
wedge_fetch() {  # round L's: the cell's one recovery (mains cycle), then a read-only fetch (pull-wait fixed)
  local t=$1; shift; local O=$RES/$t-$D/fetch f got=""; mkdir -p $O
  echo "$t: wedged at exit -> one recovery (power cycle), then read-only fetch ($(date -u +%T))" >> $S
  $V power cycle --confirm cycle >/dev/null 2>&1 || $V power cycle >/dev/null 2>&1; sleep 90
  $V get-file "$@" --return --from 'C:\DOSAGS' > $O/get-file.out 2>&1
  echo "$t fetch: $(pull_wait $O 600)" >> $S
  for f in "$@"; do $V pulled save "$f" --out "$O/$f" >/dev/null 2>&1 || true; [[ -s $O/$f ]] && got="$got $f"; done
  ( cd $O && [[ -n "$got" ]] && sha256sum $got > SHA256SUMS ); echo "$t fetch collected: [${got# }] (not collected = the rest)" >> $S
}
# (a) warm-up: rig health and the round's first BLASTER read; not scored
BL=(--pre-line 'ECHO %BLASTER% > BLASTER.TXT' --collect BLASTER.TXT)
ccell WARMUPRQ mmd 0 $B/l308.exe 1500 480 $MM "${BL[@]}"
_bl=$(tr -d '\r' < $RES/WARMUPRQ-$D/BLASTER.TXT 2>/dev/null | sed 's/[[:space:]]*$//')
echo "WARMUPRQ BLASTER.TXT: [$_bl]" >> $S
if [[ "$_bl" != "A220 I7 D3 P330 T3" ]]; then echo "STOP after WARMUPRQ: BLASTER witness [$_bl] != [A220 I7 D3 P330 T3]" >> $S; poweroff; exit 1; fi
# close watch (as P9): the warm-up's 320x200 title is never locked ("nolock"); any other STALE kind, or no capture device, stops
if [[ -f $RES/WARMUPRQ-$D/witness/WITNESS-CAPTURE-STALE.txt ]] && ! grep -q '"stale_kind": "nolock"' $RES/WARMUPRQ-$D/witness/WITNESS-CAPTURE-STALE.txt; then
  echo "STOP after WARMUPRQ: capture STALE in the warm-up ($(head -c 200 $RES/WARMUPRQ-$D/witness/WITNESS-CAPTURE-STALE.txt))" >> $S; poweroff; exit 1; fi
_vs=$($V video state 2>&1 | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("%s %s" % (d.get("device_present"), d.get("state")))
except Exception as e: print("UNREADABLE")' 2>&1)
echo "after WARMUPRQ: capture $_vs" >> $S
if [[ "$_vs" != True* ]]; then echo "STOP after WARMUPRQ: capture device not present [$_vs]" >> $S; poweroff; exit 1; fi
CFGON="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
export RUNHW_MIN_WAIT_S=270
# (b) DRIVE 6 calibration (DRIVE6-RIG-CHECKS Q0-Q4 / G0 G1 C1-C10; drive6-gate.sh). The short re-check (calq, 13 presses)
# against round RJ's passing full cal (RJCAL); on ANY calq miss the full cal (RQCAL) runs in-round; a full-cal RECENTRE or
# STOP ends the MS3 block (no third cal this power-on). A press-path STOP is never answered mid-round (sdlports).
PLAY="--no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=12440 --ags-arg --loadsavedgame --ags-arg 7 --extra-file $B/AGSSAVE.007:AGSSAVE.007 $CFGON"
export DRIVE6_DY=15 DRIVE6_DXL=52 DRIVE6_DXA=75 DRIVE6_DXB=42
REF=$RES/RJCAL-2026-11-11
CALOK=0
gate() { local t=$1 g; shift; g=$($H/drive6-gate.sh "$RES/$t-$D" "$@" 2>&1 | tail -1); echo "$t: $g" >> $S; echo "$g"; }
apply() { local v; for v in $(sed -n 's/^GATE [A-Z]* //p' <<<"$1"); do [[ "$v" =~ ^DRIVE6_(DY|DXL|DXA|DXB)=[0-9]+$ ]] && export "$v"; done
  echo "DRIVE6 values now: DY=$DRIVE6_DY DXL=$DRIVE6_DXL DXA=$DRIVE6_DXA DXB=$DRIVE6_DXB" >> $S; }
if need RQCALQ 1520; then   # calq 760 + full cal 760 (counted up front); the ABBA block keeps its own graded needs
  DRIVE6_MODE=calq ccell RQCALQ mmd 6 $B/r0380.exe 1800 750 $PLAY "${BL[@]}"
  G=$(gate RQCALQ --recheck "$REF")
  case "$G" in
    "GATE PASS "*) apply "$G"; CALOK=1 ;;
    *) DRIVE6_MODE=cal ccell RQCAL mmd 6 $B/r0380.exe 1800 750 $PLAY "${BL[@]}"
       G2=$(gate RQCAL --no-recentre); case "$G2" in "GATE PASS "*) apply "$G2"; CALOK=1 ;; esac ;;
  esac
fi
(( CALOK )) || echo "ABBA block not run: DRIVE 6 calibration did not PASS ($(date -u +%T))" >> $S
CUT=0
# (c) the heap lock-policy ABBA: DRIVE 6 ms on RO's play line, the calibrated values; arms by env only (0380's switches,
# both on the env allowlist, so env_block_sha differs per arm). Every cell: DIR C:\ /A before and after the game.
ROOT=(--pre-line 'DIR C:\ /A > ROOTPRE.TXT' --post-line 'DIR C:\ /A > ROOTPOST.TXT' --collect ROOTPRE.TXT --collect ROOTPOST.TXT)
UNL=(--env DOSAGS_HEAP_UNLOCK=1)
PRE=(--env DOSAGS_HEAP_PREGROW_KB=6144)
playread() { local t=$1 g=$2 p=$3 R=$RES/$1-$D only
  only=$(tail -1 $R/PLAY-RESULT.txt 2>/dev/null | python3 -c 'import json,sys
try: f=json.load(sys.stdin).get("fails") or []
except Exception: f=["?"]
print(1 if f==["logged 113 walk targets for 114 presses"] else 0)' 2>/dev/null)
  if [[ "$g" == "GATE PLAY-OK" ]]; then echo "$t: PLAYREAD OK" >> $S
  elif [[ "$g" == "GATE PLAY-VOID "* && "$only" == 1 && "$p" == *" PAIR-OK-114LATE "* ]]; then echo "$t: PLAYREAD OK-114LATE" >> $S
  else echo "$t: PLAYREAD VOID (gate [$g]; pairing [${p:0:60}])" >> $S; fi; }
ab() { local t=$1 arm=$2; shift 2
  DRIVE6_MODE=ms ccell $t mmd 6 $B/r0380.exe 1800 750 $PLAY "${BL[@]}" "${ROOT[@]}" "$@" || return
  local g p; g=$($H/drive6-gate.sh --play "$RES/$t-$D" 2>&1 | tail -1); echo "$t: $g" >> $S
  python3 $H/ms3-pairing.py "$RES/$t-$D" > $RES/$t-$D/PAIRING.txt 2>&1; sed "s/^/$t: /" $RES/$t-$D/PAIRING.txt >> $S
  p=$(/usr/bin/grep -m1 '^PAIR ' $RES/$t-$D/PAIRING.txt)
  playread $t "$g" "$p"
  python3 $H/rq-steps.py cell "$RES/$t-$D" $arm > $RES/$t-$D/STEPS.txt 2>&1; sed "s/^/$t: /" $RES/$t-$D/STEPS.txt >> $S
  [[ $arm == U ]] && ! /usr/bin/grep -q 'valid=yes' $RES/$t-$D/STEPS.txt && /usr/bin/grep -q 'no clean exit' $RES/$t-$D/STEPS.txt && \
    echo "$t: UNLOCK FAILED (a U cell without a clean exit)" >> $S
  DONE+=("$RES/$t-$D:$arm"); }
DONE=()
if (( CALOK )); then
  need RQO1 4560 && ab RQO1 O
  need RQU1 3800 && ab RQU1 U "${UNL[@]}"
  need RQP1 3040 && ab RQP1 P "${PRE[@]}"
  need RQP2 2280 && ab RQP2 P "${PRE[@]}"
  need RQU2 1520 && ab RQU2 U "${UNL[@]}"
  need RQO2 760 && ab RQO2 O
fi
(( ${#DONE[@]} )) && python3 $H/rq-steps.py verdict "${DONE[@]}" > $B/VERDICT.txt 2>&1 && sed 's/^/VERDICT: /' $B/VERDICT.txt >> $S
CUT=0
unset RUNHW_MIN_WAIT_S
echo "vcctrld daemon_start_t at round end: $($V activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))')" >> $S
poweroff
echo "ROUND RQ DONE $(date -u +%T)" >> $S
