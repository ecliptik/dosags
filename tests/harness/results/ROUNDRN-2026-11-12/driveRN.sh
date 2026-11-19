#!/usr/bin/env bash
# Round RN driver (copy of roundRM/driveRM.sh): the fix round for ags 0377 (bounded mixer voice ring), diagnostic only
# (no target, no proof claim). A same-binary ABBA with the DOSAGS_MEMLOG=1 diagnostic (ags 0376) on in all four arms:
# F = the fixed ring (0377's default), L = DOSAGS_RING_LEGACY=1 (0377's TEMPORARY switch: the old unbounded growth).
# ONE power-on. rnrel = main + 0376 + 0377 release (stamp in rnrel.STAMP). USB4VC 0.5.109.
# Order: WARMUPRN -> RNCALQ [-> RNCAL on a calq miss] -> RNF1 RNL1 RNL2 RNF2 -> RNDT (DPMITIME, information) -> RNP1
# (P9M1 on rnrel, DRIVE 5; first to drop).
set -u
HERE_L=~/git/dosags/build/ws/roundL   # cellL.sh + snapshots.py (the fixed comparator) are reused as-is
REPO=~/git/dosags; B=$REPO/build/ws/roundRN; H=$REPO/tests/harness; RES=$H/results; S=$B/SUMMARY.txt
D=2026-11-12; export CELL_DATE=$D
CAP_MIN=120   # minutes of mains-on time from relay-on (typical ~100: WARMUP 9, calq 12.5, ABBA 4 x 12.5, DPMITIME ~14, P9M1 12.5)
[[ "$CAP_MIN" =~ ^[0-9]+$ ]] && (( CAP_MIN >= 30 && CAP_MIN <= 120 )) || {
  echo "STOP $(date -u +%T): CAP_MIN=$CAP_MIN is not set to a number of minutes (30-120)" >> $B/SUMMARY.txt; echo "driveRN.sh: STOP: CAP_MIN unset" >&2; exit 1; }
# the round date names every results dir and README; a stale D is refused before anything touches the target
# (coordinator 2026-09-26): re-date the dirs, READMEs and this line in a "re-date, before any data" commit instead.
# round P9 (coordinator 2026-09-29): no --date-ok bypass; every staged cell's pre-registered results dir must carry the
# ACTUAL launch date (UTC) -- $RES/<TAG>-<today>/README.md for every tag of every staged block -- or nothing starts.
TODAY=$(date -u +%F)
if [[ "$D" != "$TODAY" ]]; then
  echo "STOP $(date -u +%T): round date D=$D != today $TODAY (UTC); re-date before any data" >> $B/SUMMARY.txt
  echo "driveRN.sh: STOP: D=$D != $TODAY; re-date first" >&2; exit 1; fi
_miss=""
for _t in WARMUPRN RNCALQ RNCAL RNF1 RNL1 RNL2 RNF2 RNDT RNP1; do
  [[ -f $RES/$_t-$TODAY/README.md ]] || _miss="$_miss $_t"
done
if [[ -n "$_miss" ]]; then
  echo "STOP $(date -u +%T): no pre-registered README dated $TODAY for:$_miss (a re-date commit precedes any data)" >> $B/SUMMARY.txt
  echo "driveRN.sh: STOP: README missing for$_miss at $TODAY" >&2; exit 1; fi
V=~/git/vcctrl/bin/vcctrl
FB="--env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1"
MMDCFG="--extra-file $H/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG"
C512="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
sumline() { local t=$1 R=$RES/$1-$D
  echo "$t: $(/usr/bin/grep -a 'run-hw exit' $R/run-hw.out) pre=$(cut -c1-12 $R/PRE-STAGE-SHA256.txt) post=$(cut -c1-12 $R/POST-RUN-SHA256.txt) staged_has_pre=$(/usr/bin/grep -c "$(cut -c1-64 $R/PRE-STAGE-SHA256.txt)" $R/STAGED-SHA256.txt) $(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*\|build_dirty=[0-9]\|tick_rate=[0-9.]*\|tick_rate_steady=[0-9.]*' $R/*.LOG 2>/dev/null | sort -u | tr '\n' ' ') recover=$(ls $R/RECOVERY.TXT 2>/dev/null | wc -l) inputlog=$( [[ -f $R/INPUT-LOG-VOID.txt ]] && echo "VOID:$(head -c 80 $R/INPUT-LOG-VOID.txt)" || echo "ok:$(wc -l < $R/INPUT-LOG.jsonl 2>/dev/null)" ) fw=$( [[ -f $R/FW-VOID.txt ]] && echo "VOID:$(head -c 80 $R/FW-VOID.txt)" || { [[ -f $R/FIRMWARE-VERSION-UNREAD.txt ]] && echo UNREAD || echo OK; } ) xcheck=$( [[ -f $R/CROSSCHECK-NA.txt ]] && echo NA || echo ok ) capture=$( [[ -f $R/witness/WITNESS-CAPTURE-STALE.txt ]] && echo STALE || echo ok ) rooms=$(/usr/bin/grep -aho 'Now in room [0-9]*' $R/STDOUT.TXT 2>/dev/null | sort -u | tr '\n' ',') $(date -u +%T)" >> $S; }
# manifest stamps per staged exe (LAB-WB 36; LAB-JOURNEYS 8.35 note; PLAN D35HW; round H cap3c; round L); a mismatch VOIDs the cell
declare -A STAMP=([l308.exe]=bc9c3704a839)
for _s in $B/*.STAMP; do [[ -f $_s ]] && STAMP[$(basename $_s .STAMP).exe]=$(cat $_s); done
[[ -f $B/ORDER-CONFIRMED ]] || { echo "STOP: round RN's order is not confirmed yet (build/ws/roundRN/ORDER-CONFIRMED missing)"; exit 1; }
export FW_EXPECT=0.5.109
export FLASH_REPORT="vcctrl flash report 2026-09-25: USB4VC 0.5.107 counters build, hex sha256 98a8b9aa..."
stampcheck() { local t=$1 e=$2 R=$RES/$1-$D got; got=$(/usr/bin/grep -aho 'binary_sha12=[0-9A-Za-z]*' $R/*.LOG 2>/dev/null | head -1 | cut -d= -f2)
  if [[ "$got" == "${STAMP[$(basename $e)]}" ]]; then echo "$t: stamp OK $got" >> $S
  else echo "$t: STAMP-VOID manifest $got, want ${STAMP[$(basename $e)]} ($(basename $e))" >> $S; fi; }
cell() { local t=$1; shift; $B/cellRN.sh "$t" "$@" > /dev/null 2>&1; sumline "$t"; stampcheck "$t" "$3"
  /usr/bin/grep -q 'run-hw exit=0' $RES/$t-$D/run-hw.out || { echo "STOP after $t" >> $S; poweroff; exit 1; }; }
poweroff() { [[ -s $B/ACTIVE-CELL.txt ]] && echo "poweroff() fired DURING cell: $(cat $B/ACTIVE-CELL.txt)" >> $S; $V power off >/dev/null 2>&1; sleep 5; echo "power OFF $(date -u +%T): $($V power state 2>&1 | python3 -c 'import json,sys; d=json.load(sys.stdin)["power"]; print("on=%s mW=%s" % (d.get("on"), d.get("mw", d.get("power_mw"))))' 2>&1)" >> $S
  kill $CW 2>/dev/null; }
trap 'echo "driver exit $? $(date -u +%T)" >> $S' EXIT
echo "round RN start $(date -u +%T)" >> $S
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
ccell WARMUPRN mmd 0 $B/l308.exe 1500 480 $MM "${BL[@]}"
_bl=$(tr -d '\r' < $RES/WARMUPRN-$D/BLASTER.TXT 2>/dev/null | sed 's/[[:space:]]*$//')
echo "WARMUPRN BLASTER.TXT: [$_bl]" >> $S
if [[ "$_bl" != "A220 I7 D3 P330 T3" ]]; then echo "STOP after WARMUPRN: BLASTER witness [$_bl] != [A220 I7 D3 P330 T3]" >> $S; poweroff; exit 1; fi
# close watch (as P9): the warm-up's 320x200 title is never locked ("nolock"); any other STALE kind, or no capture device, stops
if [[ -f $RES/WARMUPRN-$D/witness/WITNESS-CAPTURE-STALE.txt ]] && ! grep -q '"stale_kind": "nolock"' $RES/WARMUPRN-$D/witness/WITNESS-CAPTURE-STALE.txt; then
  echo "STOP after WARMUPRN: capture STALE in the warm-up ($(head -c 200 $RES/WARMUPRN-$D/witness/WITNESS-CAPTURE-STALE.txt))" >> $S; poweroff; exit 1; fi
_vs=$($V video state 2>&1 | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("%s %s" % (d.get("device_present"), d.get("state")))
except Exception as e: print("UNREADABLE")' 2>&1)
echo "after WARMUPRN: capture $_vs" >> $S
if [[ "$_vs" != True* ]]; then echo "STOP after WARMUPRN: capture device not present [$_vs]" >> $S; poweroff; exit 1; fi
CFGON="--extra-file $H/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG"
export RUNHW_MIN_WAIT_S=270
# (b) DRIVE 6 calibration (DRIVE6-RIG-CHECKS Q0-Q4 / G0 G1 C1-C10; drive6-gate.sh). The short re-check (calq, 13 presses)
# against round RJ's passing full cal (RJCAL); on ANY calq miss the full cal (RNCAL) runs in-round; a full-cal RECENTRE or
# STOP ends the MS3 block (no third cal this power-on). A press-path STOP is never answered mid-round (sdlports).
PLAY="--no-fine-timing $FB --env DOSAGS_TAS_AUTO_EXIT_TICK=12440 --ags-arg --loadsavedgame --ags-arg 7 --extra-file $B/AGSSAVE.007:AGSSAVE.007 $CFGON"
export DRIVE6_DY=15 DRIVE6_DXL=52 DRIVE6_DXA=75 DRIVE6_DXB=42
REF=$RES/RJCAL-2026-11-11
CALOK=0
gate() { local t=$1 g; shift; g=$($H/drive6-gate.sh "$RES/$t-$D" "$@" 2>&1 | tail -1); echo "$t: $g" >> $S; echo "$g"; }
apply() { local v; for v in $(sed -n 's/^GATE [A-Z]* //p' <<<"$1"); do [[ "$v" =~ ^DRIVE6_(DY|DXL|DXA|DXB)=[0-9]+$ ]] && export "$v"; done
  echo "DRIVE6 values now: DY=$DRIVE6_DY DXL=$DRIVE6_DXL DXA=$DRIVE6_DXA DXB=$DRIVE6_DXB" >> $S; }
if need RNCALQ 1520; then   # calq 760 + full cal 760 (counted up front); the ABBA block keeps its own graded needs
  DRIVE6_MODE=calq ccell RNCALQ mmd 6 $B/rnrel.exe 1800 750 $PLAY "${BL[@]}"
  G=$(gate RNCALQ --recheck "$REF")
  case "$G" in
    "GATE PASS "*) apply "$G"; CALOK=1 ;;
    *) DRIVE6_MODE=cal ccell RNCAL mmd 6 $B/rnrel.exe 1800 750 $PLAY "${BL[@]}"
       G2=$(gate RNCAL --no-recentre); case "$G2" in "GATE PASS "*) apply "$G2"; CALOK=1 ;; esac ;;
  esac
fi
(( CALOK )) || echo "ABBA block not run: DRIVE 6 calibration did not PASS ($(date -u +%T))" >> $S
CUT=0
# (c) the ring ABBA: DRIVE 6 ms on P9M1's play line, default config, the calibrated values, DOSAGS_MEMLOG=1 in every arm.
# F = 0377's default (the bounded ring); L = DOSAGS_RING_LEGACY=1 (the old growth; env allowlist, so env_block_sha differs).
# Per-cell arm witness from RUNMANI.LOG's "DOS-PORT voicering legacy= compact_at= compactions= moved_bytes= cap_max=" line:
# F needs legacy=0 and compactions >= 1 and cap_max <= 196608; L needs legacy=1 and compactions=0; cap_max is reported. A
# cell without the line, or failing its arm's terms, is VOID for the ABBA (reported). A cell that exits with RUNMANI but
# without a clean finish (RUNMANIFEST exit_code != 0, or STDOUT.TXT without "***** ENGINE HAS SHUTDOWN") is VOID-NOFINISH.
# The memlog header (flags, samples, dropped) is printed as information. Pointing is reported (drive6-gate.sh --play), not a
# stop: the verdict is the freeze steps, not displayed %.
MEMLOG="--env DOSAGS_MEMLOG=1"
LEGACY=(--env DOSAGS_RING_LEGACY=1)
armcheck() { local t=$1 arm=$2 R=$RES/$1-$D hdr ec vr lg cp cm ok=0
  ec=$(/usr/bin/grep -a -m1 '^exit_code=' $R/RUNMANI.LOG 2>/dev/null | cut -d= -f2 | tr -d '\r')
  if [[ "$ec" != 0 ]] || ! /usr/bin/grep -aq 'ENGINE HAS SHUTDOWN' $R/STDOUT.TXT 2>/dev/null; then
    echo "$t: VOID-NOFINISH (RUNMANIFEST exit_code=${ec:-none}; STDOUT tail: $(tail -c 160 $R/STDOUT.TXT 2>/dev/null | tr -d '\r' | tr '\n' '|'))" >> $S; return; fi
  vr=$(/usr/bin/grep -a -m1 'DOS-PORT voicering legacy=' $R/RUNMANI.LOG 2>/dev/null | tr -d '\r')
  lg=$(sed -n 's/.* legacy=\([0-9]*\) .*/\1/p' <<<"$vr"); cp=$(sed -n 's/.* compactions=\([0-9]*\) .*/\1/p' <<<"$vr")
  cm=$(sed -n 's/.* cap_max=\([0-9]*\).*/\1/p' <<<"$vr")
  if [[ -n "$lg" && -n "$cp" && -n "$cm" ]]; then
    if [[ $arm == F ]]; then [[ $lg == 0 ]] && (( cp >= 1 && cm <= 196608 )) && ok=1
    else [[ $lg == 1 ]] && (( cp == 0 )) && ok=1; fi; fi
  hdr=$(/usr/bin/grep -a -m1 'DOS-PORT memlog dpmi_version' $R/RUNMANI.LOG 2>/dev/null)
  echo "$t: arm $arm witness $( ((ok)) && echo OK || echo VOID ) (voicering: [${vr:-none}]; memlog flags=$(sed -n 's/.* flags=\(0x[0-9a-f]*\) .*/\1/p' <<<"$hdr") samples=$(sed -n 's/.* samples=\([0-9]*\) .*/\1/p' <<<"$hdr") dropped=$(sed -n 's/.* dropped=\([0-9]*\) .*/\1/p' <<<"$hdr"))" >> $S; }
ab() { local t=$1 arm=$2; shift 2
  DRIVE6_MODE=ms ccell $t mmd 6 $B/rnrel.exe 1800 750 $PLAY $MEMLOG "${BL[@]}" "$@" || return
  local g; g=$($H/drive6-gate.sh --play "$RES/$t-$D" 2>&1 | tail -1); echo "$t: $g" >> $S
  armcheck $t $arm; }
if (( CALOK )); then
  need RNF1 3040 && ab RNF1 F
  need RNL1 2280 && ab RNL1 L "${LEGACY[@]}"
  need RNL2 1520 && ab RNL2 L "${LEGACY[@]}"
  need RNF2 760 && ab RNF2 F
fi
CUT=0
# (d) DPMITIME (lab tool, lab-rb ba816420; information): the host's per-page commit cost on the 486, one process per size,
# largest first, so each rep 1 is a cold commit from a fresh host (move: CWSDPMI may keep pages within a process); A = the
# default host (autoloaded per process), B = `CWSDPMI -s-` before each line (it serves that one client and unloads). Run
# before an MMD title launch of l308 (the launch only carries the lines; not scored).
DT=(--extra-file $B/DPMITIME.EXE:DPMITIME.EXE)
for _n in 992 512 192 32; do DT+=(--pre-line "DPMITIME $_n -n 3 > DPA$_n.TXT" --collect DPA$_n.TXT); done
for _n in 992 512 192 32; do DT+=(--pre-line 'CWSDPMI -s-' --pre-line "DPMITIME $_n -n 3 > DPB$_n.TXT" --collect DPB$_n.TXT); done
need RNDT 900 && ccell RNDT mmd 0 $B/l308.exe 1500 840 $MM "${BL[@]}" "${DT[@]}"
CUT=0
# (e) P9M1 on rnrel (0377 on), default config (DRIVE 5, memlog off): ties this binary and day to RMP1 / RLP1; first to drop
need RNP1 760 && ccell RNP1 mmd 5 $B/rnrel.exe 1800 750 $PLAY "${BL[@]}"
CUT=0
unset RUNHW_MIN_WAIT_S
echo "vcctrld daemon_start_t at round end: $($V activity 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("daemon_start_t"))')" >> $S
poweroff
echo "ROUND RN DONE $(date -u +%T)" >> $S
