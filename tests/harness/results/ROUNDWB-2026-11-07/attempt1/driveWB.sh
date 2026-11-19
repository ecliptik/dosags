#!/usr/bin/env bash
# Round WB driver (copy of roundRC/driveRC.sh): SMARTDRV write-behind on C: PER CELL (RUN.BAT only; CONFIG.SYS / AUTOEXEC.BAT untouched)
# vs write-through (today), same-binary ABBA x2 on the S32P line, rcrel.exe = main 9e54b6d9 release 4c9f83b62c5c (build_dirty=0).
# Order: WARMUPWB (SMARTDRV /? + /S + CHKDSK before) -> WBA1 WT, WBB1 WB, WBB2 WB, WBA2 WT, WBA3 WT, WBB3 WB, WBB4 WB, WBA4 WT
# (+ CHKDSK after, in WBA4). STOPs: help text lacks the drive+ / /C syntax; any cell leaves C: write-caching on. ONE power-on.
set -u
HERE_L=~/git/dosags/build/ws/roundL   # cellL.sh + snapshots.py (the fixed comparator) are reused as-is
REPO=~/git/dosags; B=$REPO/build/ws/roundWB; H=$REPO/tests/harness; RES=$H/results; S=$B/SUMMARY.txt
D=2026-11-07; export CELL_DATE=$D
CAP_MIN=115   # minutes of mains-on time from relay-on (typical ~96: WARMUP 9, 8 S32P-line cells ~10.8; +15)
[[ "$CAP_MIN" =~ ^[0-9]+$ ]] && (( CAP_MIN >= 30 && CAP_MIN <= 120 )) || {
  echo "STOP $(date -u +%T): CAP_MIN=$CAP_MIN is not set to a number of minutes (30-120)" >> $B/SUMMARY.txt; echo "driveWB.sh: STOP: CAP_MIN unset" >&2; exit 1; }
# the round date names every results dir and README; a stale D is refused before anything touches the target
# (coordinator 2026-09-26): re-date the dirs, READMEs and this line in a "re-date, before any data" commit instead.
# round P9 (coordinator 2026-09-29): no --date-ok bypass; every staged cell's pre-registered results dir must carry the
# ACTUAL launch date (UTC) -- $RES/<TAG>-<today>/README.md for every tag of every staged block -- or nothing starts.
TODAY=$(date -u +%F)
if [[ "$D" != "$TODAY" ]]; then
  echo "STOP $(date -u +%T): round date D=$D != today $TODAY (UTC); re-date before any data" >> $B/SUMMARY.txt
  echo "driveWB.sh: STOP: D=$D != $TODAY; re-date first" >&2; exit 1; fi
_miss=""
for _t in WARMUPWB WBA1 WBB1 WBB2 WBA2 WBA3 WBB3 WBB4 WBA4; do
  [[ -f $RES/$_t-$TODAY/README.md ]] || _miss="$_miss $_t"
done
if [[ -n "$_miss" ]]; then
  echo "STOP $(date -u +%T): no pre-registered README dated $TODAY for:$_miss (a re-date commit precedes any data)" >> $B/SUMMARY.txt
  echo "driveWB.sh: STOP: README missing for$_miss at $TODAY" >&2; exit 1; fi
V=~/git/vcctrl/bin/vcctrl
FB="--env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1"
MMDCFG="--extra-file $H/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG"
C512="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
sumline() { local t=$1 R=$RES/$1-$D
  echo "$t: $(/usr/bin/grep -a 'run-hw exit' $R/run-hw.out) pre=$(cut -c1-12 $R/PRE-STAGE-SHA256.txt) post=$(cut -c1-12 $R/POST-RUN-SHA256.txt) staged_has_pre=$(/usr/bin/grep -c "$(cut -c1-64 $R/PRE-STAGE-SHA256.txt)" $R/STAGED-SHA256.txt) $(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*\|build_dirty=[0-9]\|tick_rate=[0-9.]*\|tick_rate_steady=[0-9.]*' $R/*.LOG 2>/dev/null | sort -u | tr '\n' ' ') recover=$(ls $R/RECOVERY.TXT 2>/dev/null | wc -l) inputlog=$( [[ -f $R/INPUT-LOG-VOID.txt ]] && echo "VOID:$(head -c 80 $R/INPUT-LOG-VOID.txt)" || echo "ok:$(wc -l < $R/INPUT-LOG.jsonl 2>/dev/null)" ) fw=$( [[ -f $R/FW-VOID.txt ]] && echo "VOID:$(head -c 80 $R/FW-VOID.txt)" || { [[ -f $R/FIRMWARE-VERSION-UNREAD.txt ]] && echo UNREAD || echo OK; } ) xcheck=$( [[ -f $R/CROSSCHECK-NA.txt ]] && echo NA || echo ok ) capture=$( [[ -f $R/witness/WITNESS-CAPTURE-STALE.txt ]] && echo STALE || echo ok ) rooms=$(/usr/bin/grep -aho 'Now in room [0-9]*' $R/STDOUT.TXT 2>/dev/null | sort -u | tr '\n' ',') $(date -u +%T)" >> $S; }
# manifest stamps per staged exe (LAB-WB 36; LAB-JOURNEYS 8.35 note; PLAN D35HW; round H cap3c; round L); a mismatch VOIDs the cell
declare -A STAMP=([l308.exe]=bc9c3704a839)
for _s in $B/*.STAMP; do [[ -f $_s ]] && STAMP[$(basename $_s .STAMP).exe]=$(cat $_s); done
[[ -f $B/ORDER-CONFIRMED ]] || { echo "STOP: round WB's order is not confirmed yet (build/ws/roundWB/ORDER-CONFIRMED missing)"; exit 1; }
export FW_EXPECT=0.5.107
export FLASH_REPORT="vcctrl flash report 2026-09-25: USB4VC 0.5.107 counters build, hex sha256 98a8b9aa..."
stampcheck() { local t=$1 e=$2 R=$RES/$1-$D got; got=$(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*' $R/*.LOG 2>/dev/null | head -1 | cut -d= -f2)
  if [[ "$got" == "${STAMP[$(basename $e)]}" ]]; then echo "$t: stamp OK $got" >> $S
  else echo "$t: STAMP-VOID manifest $got, want ${STAMP[$(basename $e)]} ($(basename $e))" >> $S; fi; }
cell() { local t=$1; shift; $B/cellWB.sh "$t" "$@" > /dev/null 2>&1; sumline "$t"; stampcheck "$t" "$3"
  /usr/bin/grep -q 'run-hw exit=0' $RES/$t-$D/run-hw.out || { echo "STOP after $t" >> $S; poweroff; exit 1; }; }
poweroff() { $V power off >/dev/null 2>&1; sleep 5; echo "power OFF $(date -u +%T): $($V power state 2>&1 | python3 -c 'import json,sys; d=json.load(sys.stdin)["power"]; print("on=%s mW=%s" % (d.get("on"), d.get("mw", d.get("power_mw"))))' 2>&1)" >> $S
  kill $CW 2>/dev/null; }
trap 'echo "driver exit $? $(date -u +%T)" >> $S' EXIT
echo "round WB start $(date -u +%T)" >> $S
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
# (a) warm-up: rig health, the round's first BLASTER read, a read-only DIR listing of C:\DOSAGS; not scored
BL=(--pre-line 'ECHO %BLASTER% > BLASTER.TXT' --collect BLASTER.TXT)
ccell WARMUPWB mmd 0 $B/l308.exe 1500 480 $MM "${BL[@]}" --pre-line 'DIR C:\DOSAGS /A /B > DIRLIST.TXT' --collect DIRLIST.TXT --pre-line 'SMARTDRV /? > SDHELP.TXT' --pre-line 'SMARTDRV /S > SDRV0.TXT' --pre-line 'CHKDSK C: < NUL > CHKDSK1.TXT' --collect SDHELP.TXT --collect SDRV0.TXT --collect CHKDSK1.TXT
_bl=$(tr -d '\r' < $RES/WARMUPWB-$D/BLASTER.TXT 2>/dev/null | sed 's/[[:space:]]*$//')
echo "WARMUPWB BLASTER.TXT: [$_bl]" >> $S
if [[ "$_bl" != "A220 I7 D3 P330 T3" ]]; then echo "STOP after WARMUPWB: BLASTER witness [$_bl] != [A220 I7 D3 P330 T3]" >> $S; poweroff; exit 1; fi
# close watch (as P9): the warm-up's 320x200 title is never locked ("nolock"); any other STALE kind, or no capture device, stops
if [[ -f $RES/WARMUPWB-$D/witness/WITNESS-CAPTURE-STALE.txt ]] && ! grep -q '"stale_kind": "nolock"' $RES/WARMUPWB-$D/witness/WITNESS-CAPTURE-STALE.txt; then
  echo "STOP after WARMUPWB: capture STALE in the warm-up ($(head -c 200 $RES/WARMUPWB-$D/witness/WITNESS-CAPTURE-STALE.txt))" >> $S; poweroff; exit 1; fi
_vs=$($V video state 2>&1 | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("%s %s" % (d.get("device_present"), d.get("state")))
except Exception as e: print("UNREADABLE")' 2>&1)
echo "after WARMUPWB: capture $_vs" >> $S
if [[ "$_vs" != True* ]]; then echo "STOP after WARMUPWB: capture device not present [$_vs]" >> $S; poweroff; exit 1; fi
# warm-up check (sdlports 2026-11-07: "check the exact MS-DOS 6.22 SMARTDRV syntax on the target first"): the help text must
# show the per-drive + (write-behind) form, a "+" line naming write-behind, and /C naming the write cache; else STOP.
_h=$RES/WARMUPWB-$D/SDHELP.TXT
if ! { tr -d '\r' < $_h | grep -q 'drive\[+|-\]' && tr -d '\r' < $_h | grep -qiE '^ *\+ .*write-behind' && tr -d '\r' < $_h | grep -qiE '^ */C .*write'; }; then
  echo "STOP after WARMUPWB: SMARTDRV /? does not show the drive+ / /C syntax this round relies on (SDHELP.TXT kept)" >> $S; poweroff; exit 1; fi
echo "WARMUPWB SMARTDRV /? syntax check: OK (drive[+|-], + write-behind, /C)" >> $S
CFGON="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
export RUNHW_MIN_WAIT_S=270
MECH=(--pre-line 'DIR C:\DOSAGS\AGSSAVE.999 > SVPRE.TXT' --pre-line 'DIR C:\DOSAGS /A /B > DIRLIST.TXT'
  --pre-line 'SMARTDRV /S > SDRV.TXT' --post-line 'DIR C:\DOSAGS\AGSSAVE.999 > SVPOST.TXT'
  --collect SVPRE.TXT --collect DIRLIST.TXT --collect SDRV.TXT --collect SVPOST.TXT)
# The arm lines. Pre: the LAST lines before AGS.EXE. Post: the FIRST lines after it exits -- flush, back to read-only, witness --
# so the cache is committed and write-through restored before the SDL-log copy, MODE12, the screen-settle wait, and any
# collect / FTP / reboot step (all of which follow RUN.BAT's end). WT cells run the same lines with "C" (no +): symmetric.
WBPRE=(--pre-line 'SMARTDRV C+' --pre-line 'SMARTDRV /S > SDRVON.TXT' --collect SDRVON.TXT)
WTPRE=(--pre-line 'SMARTDRV C' --pre-line 'SMARTDRV /S > SDRVON.TXT' --collect SDRVON.TXT)
POST=(--post-line 'SMARTDRV /C' --post-line 'SMARTDRV C' --post-line 'SMARTDRV /S > SDRVOFF.TXT' --collect SDRVOFF.TXT)
# after EVERY attempted cell, failed or not: C: must read "read cache yes, write cache no" in SDRVOFF.TXT, else STOP (never leave write-behind on)
wbcheck() { local f=$RES/$1-$D/SDRVOFF.TXT
  if tr -d '\r' < $f 2>/dev/null | grep -qE '^ *C: +yes +no'; then echo "$1: C: write cache off after the cell (SDRVOFF ok)" >> $S
  else echo "STOP after $1: C: write caching not confirmed OFF after the cell (SDRVOFF.TXT missing or not 'C: yes no')" >> $S; poweroff; exit 1; fi; }
S32=(--no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 3 --extra-file $B/S32P-ACSETUP-ON.CFG:ACSETUP.CFG
  --env DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_MAX_SCALE=1 --env SDL_DOS_PACK24=1)
# argument order POST, MECH, BL, arm-PRE: the arm's SMARTDRV line is the LAST pre-line before AGS.EXE, the flush the FIRST post-line
need WBA1 6080 && { ccell WBA1 5days 2 $B/rcrel.exe 1800 750 "${S32[@]}" "${POST[@]}" "${MECH[@]}" "${BL[@]}" "${WTPRE[@]}"; wbcheck WBA1; }
need WBB1 760 && { ccell WBB1 5days 2 $B/rcrel.exe 1800 750 "${S32[@]}" "${POST[@]}" "${MECH[@]}" "${BL[@]}" "${WBPRE[@]}"; wbcheck WBB1; }
need WBB2 4560 && { ccell WBB2 5days 2 $B/rcrel.exe 1800 750 "${S32[@]}" "${POST[@]}" "${MECH[@]}" "${BL[@]}" "${WBPRE[@]}"; wbcheck WBB2; }
need WBA2 760 && { ccell WBA2 5days 2 $B/rcrel.exe 1800 750 "${S32[@]}" "${POST[@]}" "${MECH[@]}" "${BL[@]}" "${WTPRE[@]}"; wbcheck WBA2; }
need WBA3 3040 && { ccell WBA3 5days 2 $B/rcrel.exe 1800 750 "${S32[@]}" "${POST[@]}" "${MECH[@]}" "${BL[@]}" "${WTPRE[@]}"; wbcheck WBA3; }
need WBB3 760 && { ccell WBB3 5days 2 $B/rcrel.exe 1800 750 "${S32[@]}" "${POST[@]}" "${MECH[@]}" "${BL[@]}" "${WBPRE[@]}"; wbcheck WBB3; }
need WBB4 1520 && { ccell WBB4 5days 2 $B/rcrel.exe 1800 750 "${S32[@]}" "${POST[@]}" "${MECH[@]}" "${BL[@]}" "${WBPRE[@]}"; wbcheck WBB4; }
need WBA4 760 && { ccell WBA4 5days 2 $B/rcrel.exe 1800 750 "${S32[@]}" "${POST[@]}" "${MECH[@]}" \
  --post-line 'CHKDSK C: < NUL > CHKDSK2.TXT' --collect CHKDSK2.TXT "${BL[@]}" "${WTPRE[@]}"; wbcheck WBA4; }
unset RUNHW_MIN_WAIT_S
echo "vcctrld daemon_start_t at round end: $($V activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))')" >> $S
poweroff
echo "ROUND WB DONE $(date -u +%T)" >> $S
