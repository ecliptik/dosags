#!/usr/bin/env bash
# MMD-PLAY (LAB-MMD.md 2.3): interactive run on DOSBOX_DISPLAY_NUM=261, driven by hand (xdotool, hold
# then release) through the game's own flow; exclusive hub lock for the whole run.
# Usage: run-play.sh TAG EXE TICKS [ENV=VAL ...]
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; H="$REPO/tests/harness"; DATE=2026-09-23
CFG="${MMD_CFG:?}"; TAG="$1"; EXE="$2"; TICKS="$3"; shift 3
# Lock: only through the hub library (coordinator rule 2026-09-24, hub b9b7364, writer-priority intent lock)
source "$(readlink -f "$HOME/git/sdl-dos-ports/shared/tools/dosbox-lock-lib.sh")"
dbxlock_acquire exclusive "${DOSBOX_LOCK_WAIT:-7200}" "tool=lab-mmd/run-play.sh tag=$TAG" || exit 75
trap dbxlock_release EXIT
export DOSBOX_LOCK_HELD=1
out="$H/results/$TAG-$DATE"; mkdir -p "$out"
envs=(--env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK="$TICKS")
for e in "$@"; do envs+=(--env "$e"); done
marker="$(mktemp)"; t0=$(date +%s)
echo "$(date -u +%H:%M:%S) start" > "$out/RUN.txt"
DOSBOX_DISPLAY_NUM=261 AGS_EXE="$REPO/build/lab/$EXE" "$H/run-dosbox.sh" mmd --interactive --fixed-timestep \
    --no-verify-present --timeout 1500 ${MMD_CONF:+--conf "$MMD_CONF"} --screen-series "$out/series" --series-every 3 --include-extra "$CFG" "${envs[@]}" >"$out/run.stdout" 2>"$out/run.stderr"
rc=$?
stage="$(find /tmp -maxdepth 1 -name 'dos-port-dosbox.*' -newer "$marker" -type d 2>/dev/null | while read -r d; do
    /usr/bin/grep -qa "^$EXE " "$d/RUN.BAT" 2>/dev/null && /usr/bin/grep -qa "AUTO_EXIT_TICK=$TICKS" "$d/RUN.BAT" && echo "$d"; done | tail -1)"
rm -f "$marker"
echo "$TAG exe=$EXE sha12=$(sha256sum "$REPO/build/lab/$EXE" | cut -c1-12) ticks=$TICKS env=[$*] rc=$rc stage=$stage wall_s=$(( $(date +%s) - t0 ))" | tee -a "$out/RUN.txt"
for f in STDOUT.TXT RUNMANI.LOG RUN.BAT; do [[ -n "$stage" && -f "$stage/$f" ]] && cp "$stage/$f" "$out/"; done
