# L5A2 -- engine levers 1+2 on the 486, MMD character select ABBA cell 4 of 4, arm A ENGLEV=0, VM fast (written 2026-11-06; pre-registration, before any data)
- Binary: VM9REL.EXE (lab release of vm-slice3c.diff = slice 3 + engine levers 1, 2, 3), stamp 23fd25201ec9, build_dirty=1,
  8,643,269 B, sha256 1dee66de1501...; VOID if it differs. Same file both arms; the arm is the env only.
- Fixture: F1MMDK's line verbatim (as C4's R4F) + DOSAGS_VM=fast in all four + DOSAGS_ENGLEV=0 (A) / 1 (B). Witness: STDOUT
  "DOS-PORT englev DOSAGS_ENGLEV=<arm> on=<0|1>" must match, else VOID (env_block_sha is the same in both); BLASTER.TXT.
  gatebar.py --label MMD --stamp 23fd25201ec9 --room 50. Audio counters clean in every cell, else VOID.
- Basis: C4 R4F 90.16% -> logic 17.15 ms (displayed = (25 - logic)/9.04 + 0.033). From 486 samples (r not applied): lever 1
  (skip 101 of 102 provably no-op off-room character updates) -0.4 to -0.6 ms; lever 2 (3 of 4 in-VM hit tests memoised,
  0 shadow mismatches) -0.25 to -0.35 ms; lever 3 nil; the off arm's lever code <= +0.02 ms.
- Fixed cycles see far less (-0.424 and -0.076 fixed ms; x r 0.34 = -0.17); the named mechanism for the gap is cache misses
  over 102 CharacterInfo records, which DOSBox-X does not model.
- Prediction A 88.5-92.0%, steady >= 39.2. B: logic -0.65 to -0.95 -> B - A +7 to +10.5 points; B 96-100% (central 99%).
- GAIN: B - A >= +3.0 in both pairs. MET (campaign line): both B >= 99.0%. FALSIFIER: B - A < +2.0 in either pair.
- Order: WARMUPL5, L5A1, L5B1, L5B2, L5A2, then L5S16. Lab gates: docs/lab/LEVERS-REPORT.md.
- Round L5 (PLAN-FPS engine levers): one power-on, cap 90 min; dated 2026-11-06.
