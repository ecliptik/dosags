# S32R1 -- Gate S32 cell, round R: sound-on reading on the current engine (pre-registration, before any data)
- Gate S32 (PLAN.md "Gates S8 / S16 / S32": AGS Quest forced-32, 640x480x32 1:1), at the S2Q1 fixture (PLAN.md S2Q1;
  = round J's C3P cells) with sound ON: run-hw agsquest, DOSAGS_FORCE_COLOR_DEPTH=32, DOSAGS_TAS_AUTO_EXIT_TICK=1500,
  SDL_DOS_PACK24=1, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, games/5days/ACSETUP-ON.CFG (= S2Q1's trilbysnotes/ACSETUP-OFF.CFG
  except [sound] enabled=1; as rounds D/F's S32S1/S32F1), AutoPilot, --timeout 1800, RUNHW_MIN_WAIT_S=180 (1500 ticks
  ~89 s at C3P's whole-run 16.9/s + load).
- Binary: main 5ca997b3, binary_sha12 9297b7d42365, build_dirty 0; --no-fine-timing (the player default).
- Reference: C3PF1/F2 (sound off, round J): steady 40.67, fps_p50 40.00, skipped 64, whole-run 16.87.
- 2026-09-26 OPERATOR RULING (before any data): S32 "needs a new fixture"; the S32 bar stays both tick figures. The
  1500-tick demo cannot give a meaningful whole-run figure, so this cell is a sound-on BASELINE only -- NO gate verdict.
- Prediction: steady 39.8-40.8, fps_p50 40.00, skipped 50-120 (sound adds mixing), whole-run ~15-17; late_writes 0.
- Void: stamp != 9297b7d42365 or build_dirty != 0; run-hw exit != 0; the demo not reaching tick 1500; witness not clean.
