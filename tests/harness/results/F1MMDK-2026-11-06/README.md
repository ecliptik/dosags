# F1MMDK -- Maniac Mansion Deluxe character select, KPI baseline on the release exe, round F1a (written 2026-11-06; pre-registration, before any data)
- Binary: release a1dba5d61624 (build/ags-release/ags.exe, sha256 1fc012c16d41...), sound ON; VOID if the stamp differs.
- Fixture (F1 prep, build/ws/f1prep k-mmd50): run-hw mmd, ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG, direct framebuffer, TAS 5000,
  --no-fine-timing, drive none (idle select screen, room 50), PGSB, MIN_WAIT 270, --timeout 1800 + the BLASTER line.
- KPI (PLAN-FPS): frames displayed = 1 - frames_skipped/ticks and presents_real/render_passes (gatebar.py, amended c08f8dc4), steady,
  fps_p50; >= 99% displayed at steady 39.2-40.8 = MET. Reported per cell; x1 here (a baseline, not a claim).
- Witness: camera sheet (512x384 / 320x200 modes: the card cannot lock); BLASTER.TXT "A220 I7 D3 P330 T3" else VOID.
  First round on vcctrl 1e5a1e7's transfer BATs (VCCHK dadb6a50, VCGET 2ea736aa, VCLIST af3a192b): job logs checked.
- Scorer: gatebar.py --label MMD --stamp a1dba5d61624 --room 50 F1MMDK F1MMDK (one cell twice; its cell line is the reading).
- Comparison: MABSP1/2 (instr a30ee9702c2a, 09-26): steady 36.48 / 36.47, fps_p50 8.92 / 9.76, displayed 25% (750 / 751 of 999 skipped).
- Prediction: about MABSP's figures (displayed 20-35%, steady 35-38); a large change means the binary moved MMD and is named.
- Round F1a (PLAN-FPS step 2): WARMUPF1, F1MMDK, F1MMDP, F17DK, F17DP, F1AQK; one power-on, cap 85 min; dated 2026-11-06, else re-dated first.
