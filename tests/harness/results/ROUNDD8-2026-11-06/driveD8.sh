#!/usr/bin/env bash
# Round D8 driver (copy of roundV1/driveV1.sh): the C:\DOSAGS start-up test. Operator 2026-11-06 ("Ok"): the collected
# logs leave C:\DOSAGS and the directory is REBUILT by vcctrl at the DOS prompt BEFORE this driver runs (FAT dirs never shrink:
# amendment 2026-11-06, sdlports) -- nothing deleted. Order: WARMUPD8 (l308; read-only DIR listings) -> close-watch stop ->
# D8S16 -> D8S32 -> D8S8 (the gate scenes' lines, as N7/V1) on d8rel.exe = the v0.1 exe c754df64babd -> D8MP (MMD in play,
# instrumented profile). ONE power-on, cap CAP_MIN.
set -u
HERE_L=~/git/dosags/build/ws/roundL   # cellL.sh + snapshots.py (the fixed comparator) are reused as-is
REPO=~/git/dosags; B=$REPO/build/ws/roundD8; H=$REPO/tests/harness; RES=$H/results; S=$B/SUMMARY.txt
D=2026-11-06; export CELL_DATE=$D
CAP_MIN=85    # minutes of mains-on time from relay-on (typical ~63: WARMUP 11, S16/S32/S8 ~12.5 each, D8MP ~13)
[[ "$CAP_MIN" =~ ^[0-9]+$ ]] && (( CAP_MIN >= 30 && CAP_MIN <= 120 )) || {
  echo "STOP $(date -u +%T): CAP_MIN=$CAP_MIN is not set to a number of minutes (30-120)" >> $B/SUMMARY.txt; echo "driveD8.sh: STOP: CAP_MIN unset" >&2; exit 1; }
# the round date names every results dir and README; a stale D is refused before anything touches the target
# (coordinator 2026-09-26): re-date the dirs, READMEs and this line in a "re-date, before any data" commit instead.
# round D8 (coordinator 2026-09-29): no --date-ok bypass; every staged cell's pre-registered results dir must carry the
# ACTUAL launch date (UTC) -- $RES/<TAG>-<today>/README.md for every tag of every staged block -- or nothing starts.
TODAY=$(date -u +%F)
if [[ "$D" != "$TODAY" ]]; then
  echo "STOP $(date -u +%T): round date D=$D != today $TODAY (UTC); re-date before any data" >> $B/SUMMARY.txt
  echo "driveD8.sh: STOP: D=$D != $TODAY; re-date first" >&2; exit 1; fi
_miss=""
for _t in WARMUPD8 D8S16 D8S32 D8S8 D8MP; do
  [[ -f $RES/$_t-$TODAY/README.md ]] || _miss="$_miss $_t"
done
if [[ -n "$_miss" ]]; then
  echo "STOP $(date -u +%T): no pre-registered README dated $TODAY for:$_miss (a re-date commit precedes any data)" >> $B/SUMMARY.txt
  echo "driveD8.sh: STOP: README missing for$_miss at $TODAY" >&2; exit 1; fi
V=~/git/vcctrl/bin/vcctrl
FB="--env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1"
MMDCFG="--extra-file $H/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG"
C512="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
sumline() { local t=$1 R=$RES/$1-$D
  echo "$t: $(/usr/bin/grep -a 'run-hw exit' $R/run-hw.out) pre=$(cut -c1-12 $R/PRE-STAGE-SHA256.txt) post=$(cut -c1-12 $R/POST-RUN-SHA256.txt) staged_has_pre=$(/usr/bin/grep -c "$(cut -c1-64 $R/PRE-STAGE-SHA256.txt)" $R/STAGED-SHA256.txt) $(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*\|build_dirty=[0-9]\|tick_rate=[0-9.]*\|tick_rate_steady=[0-9.]*' $R/*.LOG 2>/dev/null | sort -u | tr '\n' ' ') recover=$(ls $R/RECOVERY.TXT 2>/dev/null | wc -l) inputlog=$( [[ -f $R/INPUT-LOG-VOID.txt ]] && echo "VOID:$(head -c 80 $R/INPUT-LOG-VOID.txt)" || echo "ok:$(wc -l < $R/INPUT-LOG.jsonl 2>/dev/null)" ) fw=$( [[ -f $R/FW-VOID.txt ]] && echo "VOID:$(head -c 80 $R/FW-VOID.txt)" || { [[ -f $R/FIRMWARE-VERSION-UNREAD.txt ]] && echo UNREAD || echo OK; } ) xcheck=$( [[ -f $R/CROSSCHECK-NA.txt ]] && echo NA || echo ok ) capture=$( [[ -f $R/witness/WITNESS-CAPTURE-STALE.txt ]] && echo STALE || echo ok ) rooms=$(/usr/bin/grep -aho 'Now in room [0-9]*' $R/STDOUT.TXT 2>/dev/null | sort -u | tr '\n' ',') $(date -u +%T)" >> $S; }
# manifest stamps per staged exe (LAB-WB 36; LAB-JOURNEYS 8.35 note; PLAN D35HW; round H cap3c; round L); a mismatch VOIDs the cell
declare -A STAMP=([l308.exe]=bc9c3704a839)
for _s in $B/*.STAMP; do [[ -f $_s ]] && STAMP[$(basename $_s .STAMP).exe]=$(cat $_s); done
[[ -f $B/ORDER-CONFIRMED ]] || { echo "STOP: round D8's order is not confirmed yet (build/ws/roundD8/ORDER-CONFIRMED missing)"; exit 1; }
export FW_EXPECT=0.5.107
export FLASH_REPORT="vcctrl flash report 2026-09-25: USB4VC 0.5.107 counters build, hex sha256 98a8b9aa..."
stampcheck() { local t=$1 e=$2 R=$RES/$1-$D got; got=$(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*' $R/*.LOG 2>/dev/null | head -1 | cut -d= -f2)
  if [[ "$got" == "${STAMP[$(basename $e)]}" ]]; then echo "$t: stamp OK $got" >> $S
  else echo "$t: STAMP-VOID manifest $got, want ${STAMP[$(basename $e)]} ($(basename $e))" >> $S; fi; }
cell() { local t=$1; shift; $B/cellD8.sh "$t" "$@" > /dev/null 2>&1; sumline "$t"; stampcheck "$t" "$3"
  /usr/bin/grep -q 'run-hw exit=0' $RES/$t-$D/run-hw.out || { echo "STOP after $t" >> $S; poweroff; exit 1; }; }
poweroff() { $V power off >/dev/null 2>&1; sleep 5; echo "power OFF $(date -u +%T): $($V power state 2>&1 | python3 -c 'import json,sys; d=json.load(sys.stdin)["power"]; print("on=%s mW=%s" % (d.get("on"), d.get("mw", d.get("power_mw"))))' 2>&1)" >> $S
  kill $CW 2>/dev/null; }
trap 'echo "driver exit $? $(date -u +%T)" >> $S' EXIT
echo "round D8 start $(date -u +%T)" >> $S
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
  cell "$t" "$pkg" "$d" "$e" --timeout "$to" "$@"
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
# (a) warm-up: rig health, the round's first BLASTER read; not scored
BL=(--pre-line 'ECHO %BLASTER% > BLASTER.TXT' --collect BLASTER.TXT)
ccell WARMUPD8 mmd 0 $B/l308.exe 1500 480 $MM "${BL[@]}" --pre-line 'DIR C:\DOSAGS /A /B > DIRAFTER.TXT' --pre-line 'DIR C:\DOSAGS\LOGS /A /B > DIRLOGSA.TXT' --pre-line 'DIR C:\OLDLOG /A /B > DIROLD.TXT' --pre-line 'DIR C:\DOSAGSO /A /B > DIROLDD.TXT' --collect DIRAFTER.TXT --collect DIRLOGSA.TXT --collect DIROLD.TXT --collect DIROLDD.TXT
_bl=$(tr -d '\r' < $RES/WARMUPD8-$D/BLASTER.TXT 2>/dev/null | sed 's/[[:space:]]*$//')
echo "WARMUPD8 BLASTER.TXT: [$_bl]" >> $S
if [[ "$_bl" != "A220 I7 D3 P330 T3" ]]; then echo "STOP after WARMUPD8: BLASTER witness [$_bl] != [A220 I7 D3 P330 T3]" >> $S; poweroff; exit 1; fi
# close watch (operator 2026-11-05, WARMUPD8 README). The warm-up's 320x200 title is never locked by the card ("nolock", as
# WARMUPBT and WARMUPR1); any other STALE kind, or no capture device after the warm-up, stops the round before any scored cell.
if [[ -f $RES/WARMUPD8-$D/witness/WITNESS-CAPTURE-STALE.txt ]] && ! grep -q '"stale_kind": "nolock"' $RES/WARMUPD8-$D/witness/WITNESS-CAPTURE-STALE.txt; then
  echo "STOP after WARMUPD8: capture STALE in the warm-up ($(head -c 200 $RES/WARMUPD8-$D/witness/WITNESS-CAPTURE-STALE.txt))" >> $S; poweroff; exit 1; fi
_vs=$($V video state 2>&1 | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("%s %s" % (d.get("device_present"), d.get("state")))
except Exception as e: print("UNREADABLE")' 2>&1)
echo "after WARMUPD8: capture $_vs" >> $S
if [[ "$_vs" != True* ]]; then echo "STOP after WARMUPD8: capture device not present [$_vs]" >> $S; poweroff; exit 1; fi
CFGON="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
export RUNHW_MIN_WAIT_S=270
# (b) D8S16: GR16's line verbatim (as N7S16 / V1S16 / P9S16) on d8rel.exe
need D8S16 760 && ccell D8S16 5days 2 $B/d8rel.exe 1800 750 --no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 \
  --ags-arg --startr --ags-arg 3 $CFGON "${BL[@]}"
# (c) D8S32: GR32P's line verbatim (as N7S32 / V1S32) on d8rel.exe
need D8S32 760 && ccell D8S32 5days 2 $B/d8rel.exe 1800 750 --no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 \
  --ags-arg --startr --ags-arg 3 --extra-file $B/S32P-ACSETUP-ON.CFG:ACSETUP.CFG \
  --env DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_MAX_SCALE=1 --env SDL_DOS_PACK24=1 "${BL[@]}"
# (d) D8S8: R1R1's S8 line verbatim (as N7S8 / V1S8) on d8rel.exe
S8=(--no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 35
  --extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG --env DOSAGS_MSGSKIP=1)
need D8S8 760 && ccell D8S8 trilbysnotes 3 $B/d8rel.exe 1800 750 "${S8[@]}" "${BL[@]}"
# (e) D8MP: MMD IN PLAY, per-phase profile (amendment before data, after P9M1/M2 read 67.6% displayed): P9M's line on the
# INSTRUMENTED exe d8ins.exe (main c284ddfd, f3a8774e03c8), fine timing ON, DOSAGS_TICKLOG, TICKS.BIN collected; host clicks
need D8MP 780 && ccell D8MP mmd 5 $B/d8ins.exe 1800 770 $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=12440 --env DOSAGS_TICKLOG=12500 \
  --ags-arg --loadsavedgame --ags-arg 7 --extra-file $B/AGSSAVE.007:AGSSAVE.007 $CFGON --collect TICKS.BIN "${BL[@]}"
unset RUNHW_MIN_WAIT_S
echo "vcctrld daemon_start_t at round end: $($V activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))')" >> $S
poweroff
echo "ROUND D8 DONE $(date -u +%T)" >> $S
