#!/usr/bin/env bash
# click-cell.sh -- one DOSBox-X click/key journey cell: an interactive run on a private
# Xvfb with drive-clicks-dosbox.sh injecting real mouse presses (and key taps), then
# journeys.py over the result. LAB ONLY (DOSBox-X; no hardware).
#
#   DOSBOX_DISPLAY_NUM=231 tests/harness/click-cell.sh <OUT_DIR> [--pkg 5days] [--startr N]
#       [--exit-tick T] [--env K=V]... [--conf CONF] [--include-extra FILE]... [--screen-series DIR]
#       [--verify-present]
#       [-- drive-clicks-dosbox.sh options]   (--screen-series: frames every SERIES_EVERY s, default 2,
#       and DIR/sheet.png, via run-dosbox.sh)
#
# Examples (LAB-JOURNEYS.md):
#   click-cell.sh results/JC40 --startr 3 -- --wait-room 3 --clicks 20 --hold-ms 80 --keys 5
#   click-cell.sh results/JC6Q --startr 3 --env DOSAGS_MI_RENDER_DELAY_MS=150 -- --wait-room 3 --clicks 20 --hold-ms 20
#   click-cell.sh results/JNAT --exit-tick 9600 -- --through-title --wait-room 3 --clicks 10
#
# Writes OUT_DIR/{RUNMANI.LOG,STDOUT.TXT,RUN.BAT,CLICKS.LOG,journeys.txt,run.log}. Exit 0 if the
# run produced a RUNMANIFEST; the numbers are judged by the reader or tests/ratchet.yaml.
#
# The present verifier (ags 0192) is OFF here by default (2026-09-26): run-dosbox.sh turns it on for
# every run, and it compares the whole surface twice per present with DJGPP's byte-loop memcmp, so on
# 5 Days at fixed 40000 cycles most of an ~80-97 ms render tick was the verifier (lab-s8). A click
# cell measures render and input timing, and none of its ratchet checks reads the verifier line
# (lost-inputs, lost-clicks, clicks/keys-injected; the stale-frames gate runs on the aq-journeys lab
# cell). --verify-present turns it back on for a cell that wants it; an explicit
# --env DOSAGS_PRESENT_VERIFY=... still wins either way (run-dosbox.sh).
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:?out dir}"; shift
PKG=5days; STARTR=""; EXIT_TICK=4000; ENVS=(); DRV=(); CONFARG=(); INCL=(); VERIFY=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --pkg) PKG="$2"; shift 2 ;;
        --startr) STARTR="$2"; shift 2 ;;
        --exit-tick) EXIT_TICK="$2"; shift 2 ;;
        --conf) c="$2"; [[ "$c" != /* && ! -f "$HARNESS/$c" && -f "$HARNESS/../../$c" ]] && c="$(cd "$HARNESS/../.." && pwd)/$c"
                CONFARG=(--conf "$c"); shift 2 ;;
        --include-extra) INCL+=(--include-extra "$2"); shift 2 ;;
        --screen-series) INCL+=(--screen-series "$2" --series-every "${SERIES_EVERY:-2}"); shift 2 ;;
        --env) ENVS+=(--env "$2"); shift 2 ;;
        --verify-present) VERIFY=1; shift ;;
        --) shift; DRV=("$@"); break ;;
        *) echo "unknown arg $1" >&2; exit 2 ;;
    esac
done
mkdir -p "$OUT"
# Host-wide DOSBox-X lock for the whole cell (2026-09-23): taken here, before the run, so the 120 s
# wait for our own dosbox-x below never counts time spent queued behind another worker. ALWAYS
# EXCLUSIVE (2026-09-24): this cell's input is xdotool at wall-clock times, which is not deterministic
# beside other runs even at fixed cycles; see lab-lock.sh.
source "$HARNESS/lab-lock.sh"; lab_lock_cell click-cell.sh --exclusive "${CONFARG[@]}" || exit $?
trap lab_lock_release EXIT
export DOSBOX_DISPLAY_NUM="${DOSBOX_DISPLAY_NUM:-231}"
export DOSBOX_DISPLAY=":$DOSBOX_DISPLAY_NUM"
ARGS=("$PKG" --fixed-timestep --interactive --timeout 900 --env "DOSAGS_TAS_AUTO_EXIT_TICK=$EXIT_TICK" "${ENVS[@]}" "${CONFARG[@]}" "${INCL[@]}")
[[ -n "$STARTR" ]] && ARGS+=(--ags-arg --startr --ags-arg "$STARTR")
[[ $VERIFY -eq 1 ]] || ARGS+=(--no-verify-present)
( cd "$HARNESS" && exec ./run-dosbox.sh "${ARGS[@]}" ) > "$OUT/run.log" 2>&1 &
RUN_PID=$!

# this run's own dosbox-x: the one whose parent chain reaches RUN_PID
own_stage() {
    local pid p
    for pid in $(pgrep -x dosbox-x 2>/dev/null); do
        p=$pid
        while [[ -n "$p" && "$p" -gt 1 ]]; do
            if [[ "$p" -eq "$RUN_PID" ]]; then
                tr '\0' ' ' < "/proc/$pid/cmdline" | sed -n 's#.*-c MOUNT C \(/tmp/dos-port-dosbox\.[A-Za-z0-9]*\).*#\1#p'
                return 0
            fi
            p=$(sed 's/.*) //' "/proc/$p/stat" 2>/dev/null | awk '{print $2}')   # ppid; comm may hold spaces
            [[ "$p" =~ ^[0-9]+$ ]] || break
        done
    done
}
STAGE=""
for _ in $(seq 1 120); do STAGE="$(own_stage)"; [[ -n "$STAGE" ]] && break; sleep 1; done
[[ -n "$STAGE" ]] || { echo "click-cell: no dosbox-x of our own after 120 s" >&2; wait "$RUN_PID"; exit 1; }
echo "$STAGE" > "$OUT/stage"
"$HARNESS/drive-clicks-dosbox.sh" "$STAGE" "$OUT/CLICKS.LOG" "${DRV[@]}"
# interactive DOSBox-X sits at the DOS prompt after the program exits: stop OUR dosbox-x
# (matched on its own stage dir) once the manifest is complete
for _ in $(seq 1 900); do
    /usr/bin/grep -q 'RUNMANIFEST-END' "$STAGE/RUNMANI.LOG" 2>/dev/null && /usr/bin/grep -q 'stalls100' "$STAGE/RUNMANI.LOG" && break
    kill -0 "$RUN_PID" 2>/dev/null || break
    sleep 1
done
sleep 2
pkill -TERM -f "dosbox-x .*-c MOUNT C $STAGE( |$)" 2>/dev/null || true
wait "$RUN_PID"
for f in RUNMANI.LOG STDOUT.TXT RUN.BAT; do cp "$STAGE/$f" "$OUT/" 2>/dev/null || true; done
[[ -f "$OUT/RUNMANI.LOG" ]] || { echo "click-cell: no RUNMANI.LOG" >&2; exit 1; }
"$HARNESS/journeys.py" "$OUT" --host-clicks "$OUT/CLICKS.LOG" > "$OUT/journeys.txt"
cat "$OUT/journeys.txt"
