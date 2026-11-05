#!/usr/bin/env bash
# audio-sampler.sh -- log the capture's level and spectrum every ~1.5 s while a cell runs.
#   tests/harness/audio-sampler.sh OUT.log [WINDOW_MS=1500]   (stop it with kill)
# One line per sample: "HH:MM:SS mean/peak=<dBFS> <dBFS> active_bands=<n>" -- the LEVEL.log
# format every earlier step-8 cell used. vcctrl's one-word audio verdict is NOT used: it calls
# the idle floor "AUDIO PRESENT" (PLAN.md step 8). Numbers only.
set -u
OUT="${1:?usage: audio-sampler.sh OUT.log [WINDOW_MS]}"; W="${2:-1500}"
HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V="${VCCTRL_BIN:-$HARNESS_DIR/../../../vcctrl/bin/vcctrl}"
while :; do
    l=$("$V" level "$W" 2>/dev/null | python3 -c 'import json,sys
try: d=json.load(sys.stdin); print(d.get("mean_db"), d.get("peak_db"))
except Exception: print("NA NA")')
    b=$("$V" spectrum "$W" 2>/dev/null | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("active_bands"))
except Exception: print("NA")')
    printf '%s mean/peak=%s active_bands=%s\n' "$(date +%H:%M:%S)" "$l" "$b" >> "$OUT"
done
