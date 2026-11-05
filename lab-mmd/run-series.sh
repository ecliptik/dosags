#!/usr/bin/env bash
# LAB-MMD series runner: every run under ONE exclusive hub DOSBox-X lock (hub dosbox-lock-lib.sh).
# Usage: run-series.sh <spec-file>; each spec line: TAG EXE TICKS [ENV=VAL ...]
# The stage dir is found by its own RUN.BAT (run-dosbox.sh exits non-zero under set -e/pipefail before
# printing it when no presentverify line exists, i.e. with --no-verify-present -- reported, not patched).
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; H="$REPO/tests/harness"; DATE=2026-09-23
CFG="${MMD_CFG:?MMD_CFG must name a file called ACSETUP.CFG}"
# Lock: only through the hub library (coordinator rule 2026-09-24, hub b9b7364, writer-priority intent lock)
source "$(readlink -f "$HOME/git/sdl-dos-ports/shared/tools/dosbox-lock-lib.sh")"
dbxlock_acquire exclusive "${DOSBOX_LOCK_WAIT:-7200}" "tool=lab-mmd/run-series.sh spec=$(basename "$1")" || exit 75
trap dbxlock_release EXIT
export DOSBOX_LOCK_HELD=1
while read -r tag exe ticks rest; do
    [[ -z "$tag" || "$tag" == \#* ]] && continue
    out="$H/results/$tag-$DATE"; mkdir -p "$out"
    envs=(--env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK="$ticks")
    for e in $rest; do envs+=(--env "$e"); done
    marker="$(mktemp)"; t0=$(date +%s)
    AGS_EXE="$REPO/build/lab/$exe" "$H/run-dosbox.sh" mmd --fixed-timestep --no-verify-present --timeout 1800 ${MMD_CONF:+--conf "$MMD_CONF"} \
        --include-extra "$CFG" "${envs[@]}" >"$out/run.stdout" 2>"$out/run.stderr"
    rc=$?
    stage="$(find /tmp -maxdepth 1 -name 'dos-port-dosbox.*' -newer "$marker" -type d 2>/dev/null | while read -r d; do
        /usr/bin/grep -qa "^$exe " "$d/RUN.BAT" 2>/dev/null && /usr/bin/grep -qa "AUTO_EXIT_TICK=$ticks" "$d/RUN.BAT" && echo "$d"; done | tail -1)"
    rm -f "$marker"
    echo "$tag exe=$exe sha12=$(sha256sum "$REPO/build/lab/$exe" | cut -c1-12) ticks=$ticks env=[$rest] rc=$rc stage=$stage wall_s=$(( $(date +%s) - t0 ))" | tee "$out/RUN.txt"
    for f in STDOUT.TXT RUNMANI.LOG RUN.BAT; do [[ -n "$stage" && -f "$stage/$f" ]] && cp "$stage/$f" "$out/"; done
done < "$1"
