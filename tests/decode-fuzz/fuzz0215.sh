#!/usr/bin/env bash
# fuzz0215.sh -- ags patch 0215's bit-exactness fuzz: dos_audio_decode_pcm before vs after 0215,
# sample for sample, over synthesized WAV (1-3 ch, 8/16 bit, 13 rates, odd tails) and VOC clips.
#
#   tests/decode-fuzz/fuzz0215.sh [CASES=3000] [--dos] [--control]
#
# Old and new come from the vendor tree's own commits (the parent of "patch 0215 --" and that
# commit), so run it with the series applied (`make patches`). Builds on the host twice (SSE, and
# -m32 x87 like DJGPP); --dos also builds a DJGPP -O3 exe and runs it under DOSBox-X (shared lock).
# --control removes 0215's exact-integer fallback from the new side: the fuzz must then FAIL,
# which is what shows it can see what the fallback prevents. PASS prints mismatches=0.
set -eu
CASES="${1:-3000}"; DOS=0; CTL=0
for a in "$@"; do case "$a" in --dos) DOS=1 ;; --control) CTL=1 ;; esac; done
[[ "$CASES" =~ ^[0-9]+$ ]] || CASES=3000
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
V="$ROOT/vendor/ags"; F=Engine/platform/dos/dos_audio_decode.cpp
C=$(git -C "$V" log --format=%H -1 --grep='^DOS-PORT: patch 0215 --')
[[ -n "$C" ]] || { echo "fuzz0215: no 'patch 0215 --' commit in vendor/ags (make patches?)" >&2; exit 2; }
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
git -C "$V" show "$C^:$F" | grep -v '^#include' > "$W/old_body.inc"
git -C "$V" show "$C:$F" | grep -v '^#include' > "$W/new_body.inc"
if (( CTL )); then
    sed -i 's/? static_cast<int16_t>(q) : interp_double(src, i, src_rate);/? static_cast<int16_t>(q) : static_cast<int16_t>(q);/' "$W/new_body.inc"
    grep -q 'static_cast<int16_t>(q) : static_cast<int16_t>(q)' "$W/new_body.inc" || { echo "fuzz0215: control edit did not apply" >&2; exit 2; }
fi
cp "$ROOT/tests/decode-fuzz/fuzz0215.cpp" "$W/fuzz.cpp"
OUT="$W/results.txt"; : > "$OUT"
g++ -O3 -std=c++17 -o "$W/f64" "$W/fuzz.cpp"
"$W/f64" "$CASES" | tail -1 | sed 's/^/host-sse  /' >> "$OUT" || true
g++ -O3 -std=c++17 -m32 -mfpmath=387 -o "$W/f387" "$W/fuzz.cpp"
"$W/f387" "$CASES" | tail -1 | sed 's/^/host-x87  /' >> "$OUT" || true
N=2
if (( DOS )); then
    PATH="$ROOT/tools/djgpp/bin:$ROOT/tools/djgpp/i586-pc-msdosdjgpp/bin:$PATH" \
        i586-pc-msdosdjgpp-g++ -O3 -std=gnu++17 -o "$W/fuzzdos.exe" "$W/fuzz.cpp"
    "$ROOT/.sdl-dos-ports/shared/tools/dosbox-run.sh" --exe "$W/fuzzdos.exe" \
        --include "$ROOT/vendor/cwsdpmi/cwsdpmi.exe" --args "$CASES" --fast --stdout "$W/dos.out" > "$W/dosrun.log" 2>&1 || true
    sed 's/^/djgpp-dos /' "$W/dos.out" >> "$OUT"
    N=3
fi
cat "$OUT"
clean=$(grep -c 'mismatches=0 length_or_result_mismatches=0' "$OUT" || true)
ran=$(grep -c 'FUZZ0215 ' "$OUT" || true)
if (( CTL )); then
    # the control must be seen by every build: all ran, none clean
    (( ran == N && clean == 0 )) && { echo "CONTROL OK: every build found the missing fallback"; exit 0; }
    echo "CONTROL NOPOWER: ran $ran of $N, $clean clean"; exit 1
fi
(( ran == N && clean == N )) && { echo "PASS: $N of $N builds bit-exact"; exit 0; }
echo "FAIL: ran $ran of $N, $clean bit-exact"; exit 1
