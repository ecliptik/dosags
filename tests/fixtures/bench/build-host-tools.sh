#!/usr/bin/env bash
# build-host-tools.sh -- build AGS's own headless toolchain (agscc,
# agf2dta, agfexport, spritepak, crmpak, agspak) natively on this host,
# plus this fixture's one own tool, mkroom.
#
# Usage: build-host-tools.sh [AGS_SRC] [OUT_DIR]
#   AGS_SRC  an AGS source tree at the pinned revision (vendor/
#            sources.manifest). Default: vendor/ags. A PRISTINE checkout
#            is the safer input -- vendor/ags carries this port's DOS
#            patch series and may be reset/re-patched by other work; a
#            local `git clone vendor/ags X && git -C X checkout <pin>` is
#            the cheap way to get one.
#   OUT_DIR  default: build/host-tools
#
# The one gap against a stock configure, found 2026-09-16: Common/util/
# stdio_compat.c needs _GNU_SOURCE under -std=c11 for truncate(). Passed
# through CMAKE_C_FLAGS -- a build flag, not a source change.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
AGS_SRC="$(cd "${1:-$REPO/vendor/ags}" && pwd)"
OUT="${2:-$REPO/build/host-tools}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"

if [[ ! -x "$OUT/Tools/agspak" || ! -x "$OUT/Compiler/agscc" ]]; then
    cmake -S "$AGS_SRC" -B "$OUT" -DCMAKE_BUILD_TYPE=Release \
        -DAGS_BUILD_ENGINE=OFF -DAGS_BUILD_TOOLS=ON -DAGS_BUILD_COMPILER=ON \
        -DAGS_TESTS=OFF -DCMAKE_C_FLAGS=-D_GNU_SOURCE > "$OUT/cmake.log" 2>&1
    make -C "$OUT" -j"$(nproc)" > "$OUT/make.log" 2>&1
fi

# mkroom links against the same libtools the AGS tools use. The tools are
# built with LTO and thin objects, so mkroom must be too.
c++ -std=c++11 -O2 -flto=auto -DNDEBUG -D_FILE_OFFSET_BITS=64 \
    -I"$AGS_SRC/Tools" -I"$AGS_SRC/Common" \
    -I"$AGS_SRC/libsrc/allegro/include" -I"$AGS_SRC/libsrc/tinyxml2" \
    -I"$AGS_SRC/libsrc/miniz" -I"$AGS_SRC/libsrc/stb" \
    "$HERE/tools/mkroom.cpp" -o "$OUT/mkroom" \
    "$OUT/Tools/liblibtools.a" "$OUT/libsrc/miniz/libminiz.a" \
    "$OUT/libsrc/stb/libstb.a" "$OUT/libsrc/tinyxml2/libtinyxml2.a"

for t in Compiler/agscc Tools/agf2dta Tools/agfexport Tools/spritepak Tools/crmpak Tools/agspak mkroom; do
    [[ -x "$OUT/$t" ]] || { echo "build-host-tools.sh: $t missing" >&2; exit 1; }
done
echo "$OUT"
