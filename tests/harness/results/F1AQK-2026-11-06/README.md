# F1AQK -- AGS Quest AutoPilot, KPI baseline on the release exe, round F1a (written 2026-11-06; pre-registration, before any data)
- Binary: release a1dba5d61624 (build/ags-release/ags.exe, sha256 1fc012c16d41...), sound ON; VOID if the stamp differs.
- Fixture (F1 prep k-aq; AQF1's rung, 640x480 16-bit letterboxed): run-hw agsquest, --extra-file games/5days/ACSETUP-ON.CFG:ACSETUP.CFG,
  direct framebuffer, --no-fine-timing, no TAS (AutoPilot quits at loop tick 3570), drive AutoPilot, PGSB, MIN_WAIT 240 + the BLASTER line.
- KPI (PLAN-FPS): frames displayed = 1 - frames_skipped/ticks and presents_real/render_passes (gatebar.py, amended c08f8dc4), steady,
  fps_p50; >= 99% displayed at steady 39.2-40.8 = MET. Reported per cell; x1 here (a baseline, not a claim).
  Crosses rooms 1-4 by design (no single-room reading); ends in room 3; reported whole and per room from STDOUT/per-second rows.
- Witness: camera sheet + capture sheet (640x480 locks); BLASTER.TXT "A220 I7 D3 P330 T3" else VOID.
  First round on vcctrl 1e5a1e7's transfer BATs (VCCHK dadb6a50, VCGET 2ea736aa, VCLIST af3a192b): job logs checked.
- Scorer: gatebar.py --label AQ --stamp a1dba5d61624 --room 3 F1AQK F1AQK (reported; room-crossing makes MET not applicable).
- Comparison: AQF1/AQF2 (09-21, old build) 38.0 stable, steady 41.18. Prediction: steady above 40.8 by construction, displayed 90-97%.
- Round F1a (PLAN-FPS step 2): WARMUPF1, F1MMDK, F1MMDP, F17DK, F17DP, F1AQK; one power-on, cap 85 min; dated 2026-11-06, else re-dated first.
