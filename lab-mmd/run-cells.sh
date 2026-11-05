#!/usr/bin/env bash
# LAB-MMD cell runner (9.2): every cell in the spec under ONE exclusive hub DOSBox-X lock, at the conf in
# MMD_CONF (default tools/dosbox-x.conf: core=normal, cycles=fixed 40000 -- deterministic).
# Spec lines (| separated): TAG | PKG | EXE (in build/lab/, 8.3 name) | TICKS | CFG path or - | ags args or - | ENV=VAL ... | OPTS
# OPTS (optional 8th field): 'nofixed' drops --fixed-timestep; 'freeze=a,b,c' adds --freeze-capture <out>/freeze with
# DOSAGS_FREEZE_TICKS=a,b,c on DOSBOX_DISPLAY_NUM (default 261) -- a screen run; use MMD_LOCK=exclusive for those.
# Fixed for every cell: --fixed-timestep, --no-verify-present, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1.
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; H="$REPO/tests/harness"; DATE="${MMD_DATE:-2026-09-23}"
CONF="${MMD_CONF:-$REPO/tools/dosbox-x.conf}"
# Lock: through the port's tests/harness/dosbox-lock.sh (hub dosbox-lock-lib.sh underneath, writer-priority intent
# lock; dosags f125b997). SHARED for fixed-cycles cells, EXCLUSIVE otherwise or with MMD_LOCK=exclusive.
source "$H/dosbox-lock.sh"
MODE=exclusive
if [[ "${MMD_LOCK:-}" != "exclusive" ]] && /usr/bin/grep -q '^cycles *= *fixed' "$CONF"; then MODE=shared; fi
# SHARED (fixed cycles): each cell is independent, so the lock is taken PER CELL (inside the loop) -- a
# series-long shared hold made a waiting writer wait for the whole series (2026-09-24). EXCLUSIVE (screen
# runs): held once around the series, as the harness's gates do.
if [[ "$MODE" == exclusive ]]; then
    dosbox_lock_series "lab-mmd/run-cells.sh:$(basename "$1")" exclusive || exit $?
    trap dosbox_lock_release EXIT
    export DOSBOX_LOCK_HELD=1 DOSBOX_LOCK_HELD_MODE=exclusive
    echo "run-cells: holding the DOSBox-X lock exclusive for the series" >&2
else
    echo "run-cells: shared lock per cell (run-dosbox.sh takes it)" >&2
fi
while IFS='|' read -r tag pkg exe ticks cfg agsargs envs opts; do
    tag="$(echo $tag)"; [[ -z "$tag" || "$tag" == \#* ]] && continue
    pkg="$(echo $pkg)"; exe="$(echo $exe)"; ticks="$(echo $ticks)"; cfg="$(echo $cfg)"
    out="$H/results/$tag-$DATE"; mkdir -p "$out"
    ft=(--fixed-timestep); fz=()
    for o in ${opts:-}; do
        case "$o" in
            nofixed) ft=() ;;
            freeze=*) fz=(--freeze-capture "$out/freeze" --env "DOSAGS_FREEZE_TICKS=${o#freeze=}") ;;
        esac
    done
    # --no-host-input (hub ee910e5 / b79e724): every lab-mmd cell is AutoPilot- or TAS-driven; nothing on
    # the host drives its input.
    args=("${ft[@]}" "${fz[@]}" --no-host-input --no-verify-present --timeout 1800 --conf "$CONF"
          --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK="$ticks")
    [[ "$cfg" != "-" && -n "$cfg" ]] && args+=(--include-extra "$cfg")
    for a in $agsargs; do [[ "$a" != "-" ]] && args+=(--ags-arg "$a"); done
    for e in $envs; do args+=(--env "$e"); done
    marker="$(mktemp)"; t0=$(date +%s)
    DOSBOX_DISPLAY_NUM="${DOSBOX_DISPLAY_NUM:-261}" AGS_EXE="$REPO/build/lab/$exe" "$H/run-dosbox.sh" "$pkg" "${args[@]}" >"$out/run.stdout" 2>"$out/run.stderr"
    rc=$?
    stage="$(find /tmp -maxdepth 1 -name 'dos-port-dosbox.*' -newer "$marker" -type d 2>/dev/null | while read -r d; do
        /usr/bin/grep -qa "^$exe " "$d/RUN.BAT" 2>/dev/null && /usr/bin/grep -qa "AUTO_EXIT_TICK=$ticks" "$d/RUN.BAT" && echo "$d"; done | tail -1)"
    rm -f "$marker"
    echo "$tag pkg=$pkg exe=$exe sha12=$(sha256sum "$REPO/build/lab/$exe" | cut -c1-12) ticks=$ticks cfg=$cfg ags=[$agsargs] env=[$envs] opts=[${opts:-}] conf=$(basename "$CONF") rc=$rc stage=$stage wall_s=$(( $(date +%s) - t0 ))" | tee "$out/RUN.txt"
    for f in STDOUT.TXT RUNMANI.LOG RUN.BAT AUTOPLT.LOG PROF.BIN; do [[ -n "$stage" && -f "$stage/$f" ]] && cp "$stage/$f" "$out/"; done
    for f in "$stage"/PH*.BMP "$stage"/FRZ*.TXT; do [[ -f "$f" ]] && cp "$f" "$out/"; done
done < "$1"
