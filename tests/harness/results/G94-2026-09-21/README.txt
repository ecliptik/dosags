G94 -- the standing present-correctness gate (tests/harness/gate-present.sh) on the ags 0194 binary
binary_sha12 e8d4b76c5cd9, build_dirty=0, oracle 6e73ba0db8a5..., sha256 7243c1884ba3...

summary.txt: 35 rows (7 arms x {8-bit alias, 8-bit 2x, 8-bit centred 1x, 16-bit 2x, 16-bit centred 1x}) + the AGS Quest AutoPilot
run at defaults. 0 failing rows, 0 capture-hash differences, verifier stale_frames=0 in every row.
The previously failing row (bench16 gui, 16-bit centred 1x) reads 0 / 1038 (was 480 / 1038 on the 0193 binary).
aq-counters.txt: gCredits skipped 419 of 420, changed 1; guiskip flushed 51 late 0; the stage-1 skip is intact.
masked-check-8bit-alias.txt: the pre-registered check that the 8-bit alias rung hid the same bug.
Not reachable under DOSBox-X: 512x384 (needs UniVBE's mode; the oversized conf falls back to 640x400 2x). The 640x480
centred-1x rows stand in for it at both depths; the alias does not engage there (alias=0: not full width).
