# N7M1 -- MMD character select on the shipped build, cell 1 of 2 (written 2026-11-06; pre-registration, before any data)
- Binary: N7REL.EXE = main c284ddfd build/ags-release/ags.exe (ags 0001-0365, DOSAGS_RELEASE=1), stamp c754df64babd, build_dirty=0,
  8,646,251 B, sha256 d680e3b6fcfc... (byte-identical to the lab-gated LREL.EXE); staged from build/ws/roundN7 (expected.txt). VOID if it differs.
- No DOSAGS_VM / DOSAGS_ENGLEV / DOSAGS_VM_FUSE in RUN.BAT: STDOUT must carry "DOS-PORT vmmode DOSAGS_VM=(default) mode=3" and
  "DOS-PORT englev DOSAGS_ENGLEV=(default) on=1", else VOID. BLASTER.TXT "A220 I7 D3 P330 T3", else VOID.
- Fixture: L5B1's line verbatim minus its two env lines (mmd, drive 0, ACSETUP-ON-512X384-ROUND.CFG, TAS 5000, --no-fine-timing,
  direct framebuffer, MIN_WAIT 270). gatebar.py --label MMD --stamp c754df64babd --room 50. Audio counters clean, else VOID.
- Basis: L5B1/L5B2 99.90% x2 (lab 23fd25201ec9, same code by digest; the series drops only lab probes and flips defaults).
- Prediction: displayed 99.5-100%, steady 39.9-40.1, fps_p50 40.00, presents/render_passes ~100%.
- MET (campaign line): both N7M1 and N7M2 >= 99.0% displayed, steady 39.2-40.8.
- FALSIFIER (the landing does not carry L5): either cell < 99.0% displayed.
- Witness: camera sheet (512x384: the card cannot lock).
- Round N7 (PLAN-FPS: the landed VM + levers on the shipped build): one power-on, cap 100 min; dated 2026-11-06.
- Order: WARMUPN7, N7M1, N7M2, N7S16, N7S32, N7S8, N7AQ (the last droppable on time).
