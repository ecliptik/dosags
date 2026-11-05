#!/usr/bin/env bash
# run-scene.sh -- run ONE BENCH scene under DOSBox-X through the normal
# harness runner, staging BENCH.CFG next to the package. License: MIT.
#
# Usage: run-scene.sh <scene> [--depth 8|16|32] [--hold-ticks N] [--objects N]
#                     [--midshot] [--sound] [--cfg FILE] [--timeout S] [--conf PATH]
# --cfg FILE stages that file as BENCH.CFG verbatim (e.g. cfg/anim12.cfg);
# <scene> is then only the RUNMANIFEST scene label.
# A developer convenience; the gate of record is tools/port-game's
# `validate` against tests/games/bench8/manifest.yaml, which stages the
# committed cfg/<arm>.cfg files instead of generating one.
# DOSAGS_FIXED_TIMESTEP=1 is set, as every benchmark cell in this repo is.
# Prints the staged run directory (run-dosbox.sh's last line).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
SCENE="${1:?scene}"; shift
DEPTH=8; HOLD=1000; OBJ=4; MID=0; SND=OFF; CFGFILE=""; TIMEOUT=300; CONF=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --depth) DEPTH="$2"; shift 2 ;;
        --hold-ticks) HOLD="$2"; shift 2 ;;
        --objects) OBJ="$2"; shift 2 ;;
        --midshot) MID=1; shift ;;
        --sound) SND=ON; shift ;;
        --cfg) CFGFILE="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        --conf) CONF=(--conf "$2"); shift 2 ;;
        *) echo "run-scene.sh: unknown arg $1" >&2; exit 1 ;;
    esac
done
PKGDIR="$REPO/tests/harness/games/bench$DEPTH"
[[ -f "$PKGDIR/BENCH$DEPTH.ags" ]] || "$HERE/build.sh" --depth "$DEPTH" >&2
CFGDIR="$REPO/build/bench-work/cfg-$SCENE-$$"
mkdir -p "$CFGDIR"
if [[ -n "$CFGFILE" ]]; then cp "$CFGFILE" "$CFGDIR/BENCH.CFG"; else
    printf 'scene=%s\nhold_ticks=%s\nobjects=%s\nmidshot=%s\n' "$SCENE" "$HOLD" "$OBJ" "$MID" > "$CFGDIR/BENCH.CFG"
fi
cp "$PKGDIR/ACSETUP-$SND.CFG" "$CFGDIR/ACSETUP.CFG"
"$REPO/tests/harness/run-dosbox.sh" "bench$DEPTH" --timeout "$TIMEOUT" \
    --env "DOSAGS_SCENE=$SCENE" --env "DOSAGS_FIXED_TIMESTEP=1" --include-extra "$CFGDIR/ACSETUP.CFG" \
    --include-extra "$CFGDIR/BENCH.CFG" "${CONF[@]}"
