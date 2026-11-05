#!/usr/bin/env bash
# s8-cell.sh -- one Gate S8 lab cell on DOSBox-X (lab/journeys, 2026-09-23). LAB ONLY.
# Trilby's Notes in play in room 3, 512x384x8 centred 1x with the pillarbox alias (ags 0196; the
# S2T2 fixture), driven by host clicks at a 2 s cadence (drive-walk.sh's cadence, S2T2), at FIXED
# 40k cycles (deterministic emulated time; ranks by instruction count, not 486 time).
#
#   DOSBOX_DISPLAY_NUM=231 [S8_ROOM=N] tests/harness/s8-cell.sh OUT ARM [--env K=V]...
# S8_ROOM (default 3, the S2T2 room) picks the --startr room; room 16 plays MIDI (music 4), room 3 none.
# S8_SERIES=1 also photographs the emulated screen every 2 s into OUT/series (sheet.png): the witness
# for a fixture-suitability cell -- not for a ranking cell, whose cost it would perturb.
#
# ARM   cfg (tests/harness/presentation/trilbysnotes)   conf                          extra env
# off   ACSETUP-OFF-512X384-ROUND.CFG (sound off)        dosbox-x-fixed40k-opl3.conf   -
# pcm   ACSETUP-ON-512X384-ROUND.CFG                     dosbox-x-fixed40k-opl3.conf   DOSAGS_MIDI_NO_BACKEND=1
# opl3  ACSETUP-ON-512X384-ROUND.CFG                     dosbox-x-fixed40k-opl3.conf   -  (MIDI on the ISR replay)
# wb    ACSETUP-ON-512X384-ROUND.CFG                     dosbox-x-fixed40k-mpu401.conf -  (MIDI to the MPU-401, poll)
#
# Writes OUT/cell (click-cell.sh evidence), OUT/facts.txt (ratchet-facts.py + journeys.py) and
# OUT/s8.txt (s8-facts.py: the per-arm figures the pre-registration names).
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:?out dir}"; ARM="${2:?off|pcm|opl3|wb}"; shift 2
PRES="$HARNESS/presentation/trilbysnotes"
case "$ARM" in
    off)  CFG="$PRES/ACSETUP-OFF-512X384-ROUND.CFG"; CONF=confs/dosbox-x-fixed40k-opl3.conf; ENV=() ;;
    pcm)  CFG="$PRES/ACSETUP-ON-512X384-ROUND.CFG";  CONF=confs/dosbox-x-fixed40k-opl3.conf; ENV=(--env DOSAGS_MIDI_NO_BACKEND=1) ;;
    opl3) CFG="$PRES/ACSETUP-ON-512X384-ROUND.CFG";  CONF=confs/dosbox-x-fixed40k-opl3.conf; ENV=() ;;
    wb)   CFG="$PRES/ACSETUP-ON-512X384-ROUND.CFG";  CONF=confs/dosbox-x-fixed40k-mpu401.conf; ENV=() ;;
    *) echo "s8-cell.sh: ARM must be off|pcm|opl3|wb" >&2; exit 2 ;;
esac
mkdir -p "$OUT/cfg"
cp "$CFG" "$OUT/cfg/ACSETUP.CFG"
"$HARNESS/ratchet-cell.sh" "$OUT" click --pkg trilbysnotes --startr "${S8_ROOM:-3}" --exit-tick 5000 --conf "$CONF" \
    --include-extra "$OUT/cfg/ACSETUP.CFG" "${ENV[@]}" ${S8_SERIES:+--screen-series "$OUT/series"} "$@" \
    -- --wait-room "${S8_ROOM:-3}" --clicks 45 --hold-ms 200 --gap-ms 2000 --start-after 3 --timeout 600
rc=$?
python3 "$HARNESS/s8-facts.py" "$OUT/cell" > "$OUT/s8.txt" 2>&1
cat "$OUT/s8.txt"
exit $rc
