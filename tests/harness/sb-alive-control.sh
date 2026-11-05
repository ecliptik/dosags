#!/usr/bin/env bash
# sb-alive-control.sh OUT -- the control for tests/ratchet.yaml's sb-alive-* checks: the counters-only
# RUNMANIFEST block of a run whose SB DIED (lab/journeys CAP3b DLY-v1b, 2026-09-24: 0226 v1 + a 70 ms
# interrupts-on drain at SB IRQ 600 -- the SB's second IRQ was chained to the old vector, nobody acked
# the DSP, the SB never interrupted again: MIDI song clock 27099 ms over 127 s, pcm_irqs 0), kept as
# tests/harness/fixtures/sb-dead-dlyv1b/RUNMANI.LOG (no game data), read by the same ratchet-facts.py.
# It proves the parser and the limit, not a live SB death on the ratchet's own build (that needs a
# dead-SB build, which main does not carry; the live proof is LAB-JOURNEYS' DLY-v1b and the lab-only
# tests/ratchet-lab-sbalive.yaml). Writes OUT/facts.txt. No DOSBox-X.
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:?out dir}"
mkdir -p "$OUT/cell"
cp "$HARNESS/fixtures/sb-dead-dlyv1b/RUNMANI.LOG" "$OUT/cell/"
python3 "$HARNESS/ratchet-facts.py" "$OUT/cell" > "$OUT/facts.txt"
/usr/bin/grep 'sb_clk_permille' "$OUT/facts.txt"
