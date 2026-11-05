S1C0 -- does gCredits actually change? (slice C, first move, DOSBox-X, no hardware)

Binary: ags patch 0190 (instrument only), binary_sha12=a32b8346c983, build_dirty=0,
sha256 f135ed55510cc1e1e27cdfd2e54b6cbc113661c50542892d89c2d696fe7eb544.
Run: tests/harness/run-dosbox.sh agsquest --fixed-timestep, parsed by parse-results.py
(PASS, all phases ok, PH01-PH03 hashes match).

gui-counters.txt              this binary: real pre-clear flags
gui-counters-export-binary.txt the export binary (tautological flags), same harness
Read: gCredits (idx 7) displayed 421 frames, real changed on 1 (its first render).
      gTitleMenu (idx 1) 1 of 1. dirtysrc uisprite is identical to the export
      binary's (11,723,320 px), as it must be for an instrument-only patch.
DOSBox-X: pixel accounting only, no rate claim.
