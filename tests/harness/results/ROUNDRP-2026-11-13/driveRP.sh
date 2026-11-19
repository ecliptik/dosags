#!/usr/bin/env bash
# Round RP driver (from roundRO/driveRO.sh): the lockable-mode audio check owed before ags 0377 reaches a release
# (sdlports' terms, 2026-11-12/13). The 0379 release (main be0d1d37, DOSAGS_RELEASE=1, sha256 2191042b..., stamp
# d5c8fe52808a) on AGS Quest (the SB4S shape, N7AQ's rig line: agsquest, drive 0, games/5days/ACSETUP-ON.CFG,
# --no-fine-timing, 640x480 16-bit, PGSB, capture locked), memlog gone (0378). Two cells, RPAQ1 and RPAQ2, read by
# tests/harness/aq-audio-bars.py against the round's own idle floor (RPFLOOR, after the warm-up, at the post-cell MODE12
# 640x480 DOS screen) and the pcm_irqs set of five DOSBox-X reference renders of this binary and flow (REFAQ0379).
# ONE power-on. USB4VC 0.5.109. Order: WARMUPRP -> RPFLOOR -> RPAQ1 -> RPAQ2.
set -u
REPO=~/git/dosags; B=$REPO/build/ws/roundRP; H=$REPO/tests/harness; RES=$H/results; S=$B/SUMMARY.txt
D=2026-11-13; export CELL_DATE=$D
CAP_MIN=60   # minutes of mains-on time from relay-on (typical ~40: warm-up ~10, floor 1.5, 2 x AQ ~13)
[[ "$CAP_MIN" =~ ^[0-9]+$ ]] && (( CAP_MIN >= 30 && CAP_MIN <= 120 )) || {
  echo "STOP $(date -u +%T): CAP_MIN=$CAP_MIN is not set to a number of minutes (30-120)" >> $B/SUMMARY.txt; echo "driveRP.sh: STOP: CAP_MIN unset" >&2; exit 1; }
TODAY=$(date -u +%F)
if [[ "$D" != "$TODAY" ]]; then
  echo "STOP $(date -u +%T): round date D=$D != today $TODAY (UTC); re-date before any data" >> $B/SUMMARY.txt
  echo "driveRP.sh: STOP: D=$D != $TODAY; re-date first" >&2; exit 1; fi
_miss=""
for _t in WARMUPRP RPFLOOR RPAQ1 RPAQ2; do
  [[ -f $RES/$_t-$TODAY/README.md ]] || _miss="$_miss $_t"
done
if [[ -n "$_miss" ]]; then
  echo "STOP $(date -u +%T): no pre-registered README dated $TODAY for:$_miss (a re-date commit precedes any data)" >> $B/SUMMARY.txt
  echo "driveRP.sh: STOP: README missing for$_miss at $TODAY" >&2; exit 1; fi
V=~/git/vcctrl/bin/vcctrl
FB="--env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1"
MMDCFG="--extra-file $H/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG"
PCMSET=$(cat $B/PCMSET)   # the registered reference set, e.g. "180,181" (REFAQ0379 README)
sumline() { local t=$1 R=$RES/$1-$D
  echo "$t: $(/usr/bin/grep -a 'run-hw exit' $R/run-hw.out) pre=$(cut -c1-12 $R/PRE-STAGE-SHA256.txt) post=$(cut -c1-12 $R/POST-RUN-SHA256.txt) staged_has_pre=$(/usr/bin/grep -c "$(cut -c1-64 $R/PRE-STAGE-SHA256.txt)" $R/STAGED-SHA256.txt) $(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*\|build_dirty=[0-9]\|tick_rate=[0-9.]*\|tick_rate_steady=[0-9.]*' $R/*.LOG 2>/dev/null | sort -u | tr '\n' ' ') recover=$(ls $R/RECOVERY.TXT 2>/dev/null | wc -l) inputlog=$( [[ -f $R/INPUT-LOG-VOID.txt ]] && echo "VOID:$(head -c 80 $R/INPUT-LOG-VOID.txt)" || echo "ok:$(wc -l < $R/INPUT-LOG.jsonl 2>/dev/null)" ) fw=$( [[ -f $R/FW-VOID.txt ]] && echo "VOID:$(head -c 80 $R/FW-VOID.txt)" || { [[ -f $R/FIRMWARE-VERSION-UNREAD.txt ]] && echo UNREAD || echo OK; } ) xcheck=$( [[ -f $R/CROSSCHECK-NA.txt ]] && echo NA || echo ok ) capture=$( [[ -f $R/witness/WITNESS-CAPTURE-STALE.txt ]] && echo STALE || echo ok ) rooms=$(/usr/bin/grep -aho 'Now in room [0-9]*' $R/STDOUT.TXT 2>/dev/null | sort -u | tr '\n' ',') $(date -u +%T)" >> $S; }
declare -A STAMP=([l308.exe]=bc9c3704a839)
for _s in $B/*.STAMP; do [[ -f $_s ]] && STAMP[$(basename $_s .STAMP).exe]=$(cat $_s); done
[[ -f $B/ORDER-CONFIRMED ]] || { echo "STOP: round RP's order is not confirmed yet (build/ws/roundRP/ORDER-CONFIRMED missing)"; exit 1; }
export FW_EXPECT=0.5.109
export FLASH_REPORT="vcctrl flash report 2026-09-25: USB4VC 0.5.107 counters build, hex sha256 98a8b9aa..."
stampcheck() { local t=$1 e=$2 R=$RES/$1-$D got; got=$(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*' $R/*.LOG 2>/dev/null | head -1 | cut -d= -f2)
  if [[ "$got" == "${STAMP[$(basename $e)]}" ]]; then echo "$t: stamp OK $got" >> $S
  else echo "$t: STAMP-VOID manifest $got, want ${STAMP[$(basename $e)]} ($(basename $e))" >> $S; fi; }
cell() { local t=$1; shift; $B/cellRP.sh "$t" "$@" > /dev/null 2>&1; sumline "$t"; stampcheck "$t" "$3"
  /usr/bin/grep -q 'run-hw exit=0' $RES/$t-$D/run-hw.out || { echo "STOP after $t" >> $S; poweroff; exit 1; }; }
poweroff() { [[ -s $B/ACTIVE-CELL.txt ]] && echo "poweroff() fired DURING cell: $(cat $B/ACTIVE-CELL.txt)" >> $S; $V power off >/dev/null 2>&1; sleep 5; echo "power OFF $(date -u +%T): $($V power state 2>&1 | python3 -c 'import json,sys; d=json.load(sys.stdin)["power"]; print("on=%s mW=%s" % (d.get("on"), d.get("mw", d.get("power_mw"))))' 2>&1)" >> $S
  kill $CW 2>/dev/null; }
trap 'echo "driver exit $? $(date -u +%T)" >> $S' EXIT
echo "round RP start $(date -u +%T)" >> $S
( cd $B && sha256sum -c expected.txt ) >> $S 2>&1 || { echo "STOP: a staged binary does not match its record" >> $S; exit 1; }
[[ "$PCMSET" =~ ^[0-9]+(,[0-9]+)*$ ]] || { echo "STOP: PCMSET [$PCMSET] is not a registered set" >> $S; exit 1; }
if [[ "$($V power state | python3 -c 'import json,sys; print(json.load(sys.stdin)["power"]["on"])')" != False ]]; then
  echo "STOP: target already on -- not this driver's power-on" >> $S; exit 1; fi
echo "capture pre-flight: $($V video state 2>&1 | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("device_present=%s state=%s last_frame_age_s=%s" % (d.get("device_present"), d.get("state"), d.get("last_frame_age_s")))
except Exception as e: print("UNREADABLE (%s)" % e)' 2>&1)" >> $S
echo "audio pre-flight: $($V audio state 2>&1 | tr -d '\n' | cut -c1-300)" >> $S
START=$(date -u +%s); $V power on; CAP=$(( START + CAP_MIN*60 ))
echo "relay-on $(date -u -d @$START +%T), cap $(date -u -d @$CAP +%T) (CAP_MIN=$CAP_MIN)" >> $S
setsid nohup $B/powerguard.sh > /dev/null 2>&1 < /dev/null &
setsid nohup $B/daemongap.sh > /dev/null 2>&1 < /dev/null &
echo "powerguard + daemongap started $(date -u +%T)" >> $S
echo "vcctrld daemon_start_t at round start: $($V activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))')" >> $S
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
# (a) warm-up: rig health and the round's BLASTER read; not scored (WARMUPRO's checks verbatim)
BL=(--pre-line 'ECHO %BLASTER% > BLASTER.TXT' --collect BLASTER.TXT)
ccell WARMUPRP mmd 0 $B/l308.exe 1500 480 $MM "${BL[@]}"
_bl=$(tr -d '\r' < $RES/WARMUPRP-$D/BLASTER.TXT 2>/dev/null | sed 's/[[:space:]]*$//')
echo "WARMUPRP BLASTER.TXT: [$_bl]" >> $S
if [[ "$_bl" != "A220 I7 D3 P330 T3" ]]; then echo "STOP after WARMUPRP: BLASTER witness [$_bl] != [A220 I7 D3 P330 T3]" >> $S; poweroff; exit 1; fi
if [[ -f $RES/WARMUPRP-$D/witness/WITNESS-CAPTURE-STALE.txt ]] && ! grep -q '"stale_kind": "nolock"' $RES/WARMUPRP-$D/witness/WITNESS-CAPTURE-STALE.txt; then
  echo "STOP after WARMUPRP: capture STALE in the warm-up ($(head -c 200 $RES/WARMUPRP-$D/witness/WITNESS-CAPTURE-STALE.txt))" >> $S; poweroff; exit 1; fi
_vs=$($V video state 2>&1 | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("%s %s" % (d.get("device_present"), d.get("state")))
except Exception as e: print("UNREADABLE")' 2>&1)
echo "after WARMUPRP: capture $_vs" >> $S
if [[ "$_vs" != True* ]]; then echo "STOP after WARMUPRP: capture device not present [$_vs]" >> $S; poweroff; exit 1; fi
# (b) RPFLOOR: the idle floor, 60 s of audio-sampler.sh (1.5 s windows) at the post-cell screen (run-hw ends every cell with
# C:\VGACAP\MODE12: the 640x480 DOS screen, capture locked). F = the median mean dBFS. A wedged reader (every sample the same
# value, or NA) gets ONE vcctrl audio release + acquire and a second 60 s; a floor still unreadable, or F > -50 dBFS, STOPS
# the round before any AQ cell (the level bar would be unreadable).
FL=$RES/RPFLOOR-$D; mkdir -p $FL
floor() { local o=$1; : > $o; $H/audio-sampler.sh $o & local sp=$!; sleep 60; kill $sp 2>/dev/null; wait $sp 2>/dev/null
  python3 - "$o" <<'PYEOF'
import re, statistics as st, sys
v = [float(m) for m in re.findall(r'mean/peak=(-?[0-9.]+) ', open(sys.argv[1]).read())]
n = len(open(sys.argv[1]).read().splitlines())
if len(v) < 20 or len(set(v)) == 1:
    print('BAD samples=%d numeric=%d distinct=%d' % (n, len(v), len(set(v))))
else:
    print('OK %.2f samples=%d min=%.2f max=%.2f' % (st.median(v), len(v), min(v), max(v)))
PYEOF
}
echo "RPFLOOR start $(date -u +%T); capture $($V video state 2>&1 | python3 -c 'import json,sys
try: d=json.load(sys.stdin); print(d.get("state"))
except Exception: print("UNREADABLE")')" >> $S
F1=$(floor $FL/FLOOR.log); echo "RPFLOOR: $F1" >> $S
if [[ "$F1" != OK* ]]; then
  echo "RPFLOOR: audio release + acquire ($(date -u +%T)): $($V audio release 2>&1 | tr -d '\n' | cut -c1-120) / $($V audio acquire 2>&1 | tr -d '\n' | cut -c1-120)" >> $S
  sleep 3; F1=$(floor $FL/FLOOR-2.log); echo "RPFLOOR (second): $F1" >> $S; fi
FDB=$(awk '{print $2}' <<<"$F1")
if [[ "$F1" != OK* ]] || ! python3 -c "import sys; sys.exit(0 if float('$FDB') <= -50 else 1)"; then
  echo "STOP after RPFLOOR: floor unreadable or above -50 dBFS [$F1]" >> $S; poweroff; exit 1; fi
echo "$FDB" > $FL/FLOOR-DB.txt
echo "RPFLOOR end $(date -u +%T): F = $FDB dBFS; capture $($V video state 2>&1 | python3 -c 'import json,sys
try: d=json.load(sys.stdin); print(d.get("state"))
except Exception: print("UNREADABLE")')" >> $S
# (c) the AQ cells: N7AQ's line on the 0379 release; then the bars (tests/harness/aq-audio-bars.py), one PASS / FAIL / VOID
# per cell. BLASTER witness per cell (else the cell is VOID, reported).
export RUNHW_MIN_WAIT_S=240
AQ="--no-fine-timing $FB --extra-file $H/games/5days/ACSETUP-ON.CFG:ACSETUP.CFG"
aq() { local t=$1
  ccell $t agsquest 0 $B/r0379.exe 1800 780 $AQ "${BL[@]}" || return
  local b; b=$(tr -d '\r' < $RES/$t-$D/BLASTER.TXT 2>/dev/null | sed 's/[[:space:]]*$//'); echo "$t BLASTER.TXT: [$b]$( [[ "$b" == "A220 I7 D3 P330 T3" ]] || echo ' -> BLASTER-VOID')" >> $S
  python3 $H/aq-audio-bars.py $RES/$t-$D "$FDB" "$PCMSET" > $RES/$t-$D/AUDIO-BARS.txt 2>&1
  sed "s/^/$t: /" $RES/$t-$D/AUDIO-BARS.txt >> $S; }
aq RPAQ1
aq RPAQ2
unset RUNHW_MIN_WAIT_S
echo "vcctrld daemon_start_t at round end: $($V activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))')" >> $S
poweroff
echo "ROUND RP DONE $(date -u +%T)" >> $S
