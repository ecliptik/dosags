#!/usr/bin/env bash
# gate-present.sh -- the STANDING present-correctness gate (DOSBox-X, no hardware).
#
# Every fixture arm x every rung that exists x both depths, plus the AGS Quest AutoPilot demo at
# defaults, each run with the ags 0192 verifier on. A row passes only if the verifier reads
# stale_frames=0 AND the capture hash equals its baseline in tests/harness/expected/. Exit 1 if any
# row fails, is missing its verifier line, or is missing its capture.
#
# WHY IT EXISTS AND WHY IT MUST COVER THE RUNGS. Every other check in this repo reads the engine's own RAM
# frame, so none can see a region that changed in RAM and was never pushed to the screen. The verifier can,
# but only where the narrowed present is on the path and only on presents that actually happen:
#   - at a 2x rung the narrowing rejects every present (a full push), so it cannot fail there;
#   - at 8-bit the unchanged-frame path decides which ticks present at all (52 of 1041 in the gui arm), which
#     hid a stage-1 bug until DOSAGS_PRESENT_NO_SKIP=1 or a 16-bit rung forced a present every tick.
# So a change to GUI invalidation or the present rect is gated ONLY by the centred-1x and alias rows, at both
# depths. ags 0191 was gated at the default rungs alone, which is how its skip bug got through.
#
# Rungs (where they exist): 8-bit alias = Mode 13h native (320x200 only); 2x = the default 640x480; centred 1x =
# 640x480 with DOSAGS_MAX_SCALE=1. There is no 16-bit Mode 13h.
#
#   tests/harness/gate-present.sh [--out DIR] [--no-aq] [--arms "idle walk ..."]
#   AGS_EXE=path/to/ags.exe overrides the binary.
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HARNESS/../.." && pwd)"
OUT=""; DO_AQ=1; ARMS="idle walk anim4 anim12 text gui full"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --out) OUT="$2"; shift 2 ;;
        --no-aq) DO_AQ=0; shift ;;
        --arms) ARMS="$2"; shift 2 ;;
        *) echo "usage: $0 [--out DIR] [--no-aq] [--arms \"a b\"]" >&2; exit 2 ;;
    esac
done
[[ -n "$OUT" ]] || OUT="$(mktemp -d)"
mkdir -p "$OUT"
# Host-wide DOSBox-X lock (hub 258d04f, 2026-09-23): EXCLUSIVE once around the whole gate, so no other
# worker's DOSBox-X starts between two rows or during a capture; the runs inside do not re-take it.
source "$HARNESS/dosbox-lock.sh"; dosbox_lock_series "$(basename "$0")" || exit $?
trap dosbox_lock_release EXIT
FIX="$REPO/tests/fixtures/bench/cfg"
NATIVE="$HARNESS/presentation/bench8/ACSETUP-OFF-NATIVE.CFG"
C1X="$HARNESS/presentation/bench8/ACSETUP-OFF-640X480.CFG"
declare -A SCENE=( [idle]=idle [walk]=walk [anim4]=anim [anim12]=anim [text]=text [gui]=gui [full]=full )
SUMMARY="$OUT/summary.txt"; : > "$SUMMARY"
FAILS=0

row() { # arm depth rungname cfg extra-env
    local arm="$1" depth="$2" rung="$3" cfg="$4" extra="$5"
    local tag="b${depth}-${rung}-${arm}"
    local d="$OUT/$tag"; mkdir -p "$d"
    cp "$cfg" "$d/ACSETUP.CFG"; cp "$FIX/$arm.cfg" "$d/BENCH.CFG"
    local envs=(--env "DOSAGS_SCENE=${SCENE[$arm]}" --env "DOSAGS_TAS_AUTO_EXIT_TICK=1500")
    [[ -n "$extra" ]] && envs+=(--env "$extra")
    ( cd "$HARNESS" && timeout 400 ./run-dosbox.sh "bench$depth" --fixed-timestep \
        --include-extra "$d/ACSETUP.CFG" --include-extra "$d/BENCH.CFG" "${envs[@]}" --timeout 300 ) > "$d/run.log" 2>&1
    local st; st="$(/usr/bin/grep -o '/tmp/dos-port-dosbox\.[A-Za-z0-9]*' "$d/run.log" | tail -1)"
    local pv want got mode alias verdict
    pv="$(/usr/bin/grep -a 'presentverify frames=' "$st/STDOUT.TXT" 2>/dev/null | tr -d '\r' | tail -1)"
    mode="$(/usr/bin/grep -a -m1 'Graphics mode set: [0-9]* x' "$st/STDOUT.TXT" 2>/dev/null | tr -d '\r' | sed 's/Graphics mode set: //;s/, on display 0//')"
    alias="$(/usr/bin/grep -a -c 'vscreen alias ON' "$st/STDOUT.TXT" 2>/dev/null)"
    got="$(sha256sum "$st/PH01.BMP" 2>/dev/null | cut -d' ' -f1)"
    want="$(python3 -c "import json;print(json.load(open('$HARNESS/expected/bench$depth/dosbox-x.json'))['$arm']['PH01.BMP'])")"
    verdict="ok"
    if [[ -z "$pv" ]]; then verdict="FAIL(no verifier line)"
    elif ! /usr/bin/grep -q 'stale_frames=0 ' <<<"$pv"; then verdict="FAIL(stale)"
    elif [[ -z "$got" ]]; then verdict="FAIL(no capture)"
    elif [[ "$got" != "$want" ]]; then verdict="FAIL(hash)"; fi
    [[ "$verdict" == ok ]] || FAILS=$((FAILS + 1))
    printf '%-7s bench%-2s %-9s | %-42s alias=%s | %s | hash %s | %s\n' "$arm" "$depth" "$rung" "$mode" "$alias" \
        "$(sed 's/DOS-PORT presentverify //;s/ stale_px=.*//' <<<"$pv")" "$([[ "$got" == "$want" ]] && echo equal || echo DIFFERS)" "$verdict" >> "$SUMMARY"
    echo "$st" > "$d/stage"
}

for arm in $ARMS; do
    row "$arm" 8  alias "$NATIVE" ""
    row "$arm" 8  x2    "$HARNESS/games/bench8/ACSETUP-OFF.CFG" ""
    row "$arm" 8  c1x   "$C1X" "DOSAGS_MAX_SCALE=1"
    row "$arm" 16 x2    "$HARNESS/games/bench16/ACSETUP-OFF.CFG" ""
    row "$arm" 16 c1x   "$C1X" "DOSAGS_MAX_SCALE=1"
done

if [[ $DO_AQ -eq 1 ]]; then
    ( cd "$HARNESS" && timeout 700 ./run-dosbox.sh agsquest --fixed-timestep ) > "$OUT/aq.run.log" 2>&1
    st="$(/usr/bin/grep -o '/tmp/dos-port-dosbox\.[A-Za-z0-9]*' "$OUT/aq.run.log" | tail -1)"
    ( cd "$HARNESS" && python3 parse-results.py "$st" ) > "$OUT/aq.parse.txt" 2>&1; rc=$?
    pv="$(/usr/bin/grep -a 'presentverify frames=' "$st/STDOUT.TXT" | tr -d '\r' | tail -1)"
    v="ok"; if [[ $rc -ne 0 ]]; then v="FAIL(parse-results exit $rc)"; FAILS=$((FAILS + 1)); fi
    printf 'agsquest AutoPilot at defaults | %s | %s\n' "$(sed 's/DOS-PORT presentverify //;s/ stale_px=.*//' <<<"$pv")" "$v" >> "$SUMMARY"
    /usr/bin/grep -a -E 'DOS-PORT (guiskip|guitally|biggui_final|dirtypresent narrow=|dirtycarry)' "$st/STDOUT.TXT" | tr -d '\r' > "$OUT/aq.counters.txt"
fi

echo "gate-present: $FAILS failing row(s); table in $SUMMARY" >&2
cat "$SUMMARY"
[[ $FAILS -eq 0 ]]
