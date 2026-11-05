#!/usr/bin/env bash
# S8MP: which Trilby rooms start MIDI when entered with --startr (exploratory, fixed 40k, headless, sound on)
set -u
cd ~/git/dosags-lab-journeys/tests/harness
OUT=results/S8MP-2026-09-23; mkdir -p "$OUT/cfg"; cp presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG "$OUT/cfg/ACSETUP.CFG"
for r in ${ROOMS:-$(seq "${1:-1}" 42)}; do
    d="$OUT/r$r"
    ./lab-cell.sh "$d" trilbysnotes --fixed-timestep --conf confs/dosbox-x-fixed40k-opl3.conf --include-extra "$OUT/cfg/ACSETUP.CFG" \
        --ags-arg --startr --ags-arg "$r" --env DOSAGS_TAS_AUTO_EXIT_TICK=400 --timeout ${PROBE_TIMEOUT:-300} >/dev/null 2>&1
    m="$(/usr/bin/grep -a -o 'Playing music [0-9]*' "$d/STDOUT.TXT" 2>/dev/null | sort -u | tr '\n' ',')"
    rooms="$(/usr/bin/grep -a -o 'Now in room [0-9]*' "$d/STDOUT.TXT" 2>/dev/null | sort -u | tr '\n' ',')"
    ev="$(/usr/bin/grep -a -o 'midi=[a-z0-9]*,events=[0-9]*' "$d/RUNMANI.LOG" 2>/dev/null | tail -1)"
    echo "room $r | $rooms | $m | $ev" | tee -a "$OUT/summary.txt"
    rm -f "$d/STDOUT.TXT.full" 2>/dev/null
done
