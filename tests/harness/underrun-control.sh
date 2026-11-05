#!/usr/bin/env bash
# underrun-control.sh OUT -- the control for tests/ratchet.yaml's underruns-* checks: the counters-only RUNMANIFEST block of
# the ratchet's own sb-5days run on the reverted ags 0348 (build e92a46ae084f, ratchet 20260930T014839Z): its cold-start prime
# ran a voice dry at the next top-up, underruns=6 = primes=6 (lab/mmd 569df3b1: a ~46 ms hole ~186 ms into every cold start).
# Kept as tests/harness/fixtures/underrun-0348-sb5days/RUNMANI.LOG (no game data), read by the same ratchet-facts.py. Like
# sb-alive-control.sh it proves the parser and the limit, not a live starvation on the ratchet's own build (main carries no
# starvation switch). Writes OUT/facts.txt. No DOSBox-X.
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:?out dir}"
mkdir -p "$OUT/cell"
cp "$HARNESS/fixtures/underrun-0348-sb5days/RUNMANI.LOG" "$OUT/cell/"
python3 "$HARNESS/ratchet-facts.py" "$OUT/cell" > "$OUT/facts.txt"
/usr/bin/grep -o 'underruns=[^ ]*' "$OUT/facts.txt"
