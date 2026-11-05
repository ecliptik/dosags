#!/usr/bin/env bash
# run-linux-ref.sh -- run one BENCH arm on AGS's OFFICIAL Linux engine
# build and compare its capture with the DOS baseline (verification
# ladder step 1: "known-working on a desktop AGS runtime"). License: MIT.
#
# Usage: run-linux-ref.sh <arm> [--ref DIR] [--depth 8|16|32]
#   --ref DIR  unpacked ags_3.6.3.13_linux.tar.gz (default /tmp/ags-linux-ref)
# Reference build, from the pinned release's own page
# (https://github.com/adventuregamestudio/ags/releases/tag/v3.6.3.13):
#   https://github.com/adventuregamestudio/ags/releases/download/v3.6.3.13/ags_3.6.3.13_linux.tar.gz
#   sha256 5270d78cc5b56db379e6e242ccce86512163a8460769b4f6e8832e19a69f7c9a
#   (the digest GitHub's release API lists for that asset; verify after
#   fetching, the engine is NOT vendored here)
# Runs on a private Xvfb (:233, not the DOSBox-X harness's display), with
# SDL's dummy audio driver. Exit 0 only if the engine quit cleanly, the
# scene logged ok, and PH01.BMP matches expected/bench<depth>/dosbox-x.json.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
ARM="${1:?arm}"; shift
REF=/tmp/ags-linux-ref; DEPTH=8
while [[ $# -gt 0 ]]; do
    case "$1" in
        --ref) REF="$2"; shift 2 ;;
        --depth) DEPTH="$2"; shift 2 ;;
        *) echo "run-linux-ref.sh: unknown arg $1" >&2; exit 1 ;;
    esac
done
[[ -x "$REF/data/ags64" ]] || { echo "run-linux-ref.sh: $REF/data/ags64 not found (see header for the release URL + sha256)" >&2; exit 1; }
PKGDIR="$REPO/tests/harness/games/bench$DEPTH"
R="$REPO/build/bench-work/linuxref-$ARM"
rm -rf "$R"; mkdir -p "$R/game" "$R/user"
cp "$PKGDIR/BENCH$DEPTH.ags" "$R/game/"
cp "$PKGDIR/ACSETUP-OFF.CFG" "$R/game/acsetup.cfg"
cp "$HERE/cfg/$ARM.cfg" "$R/game/BENCH.CFG"
export DISPLAY=:233
xdpyinfo >/dev/null 2>&1 || { Xvfb :233 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2; }
RC=0
( cd "$R" && SDL_AUDIODRIVER=dummy ALLEGRO_MODULES="$REF/data/lib64" LD_LIBRARY_PATH="$REF/data/lib64" \
    timeout 180 "$REF/data/ags64" --gfxdriver software --windowed --test --log-stdout=+mgs:all \
    --user-data-dir "$R/user" "$R/game/BENCH$DEPTH.ags" > "$R/stdout.txt" 2>&1 ) || RC=$?
SCENE="${ARM%%[0-9]*}"
GOT="$(sha256sum "$R/user/PH01.BMP" 2>/dev/null | cut -c1-64 || true)"
WANT="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get(sys.argv[2],{}).get('PH01.BMP',''))" \
    "$REPO/tests/harness/expected/bench$DEPTH/dosbox-x.json" "$ARM")"
OK=1
[[ $RC -eq 0 ]] || OK=0
grep -q "AUTOPILOT phase=$SCENE status=ok" "$R/user/AUTOPLT.LOG" 2>/dev/null || OK=0
[[ -n "$GOT" && "$GOT" == "$WANT" ]] || OK=0
echo "run-linux-ref.sh: $ARM exit=$RC capture=${GOT:-none} baseline=${WANT:-none} -> $([[ $OK -eq 1 ]] && echo MATCH || echo DIFFER)"
[[ $OK -eq 1 ]]
