# S8R2 -- Gate S8 cell, round R: sound-on re-baseline on the current engine (pre-registration, before any data)
- Gate S8 (PLAN.md "Gates S8 / S16 / S32": Trilby's Notes in play, 8-bit, 512x384x8), at the ORIGINAL S8H protocol
  (PLAN-GATES table; S8H-O1/S8HO2, rounds D/F): run-hw trilbysnotes --startr 35, DOSAGS_TAS_AUTO_EXIT_TICK=5000,
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG (sound on, OPL3, default
  drain), drive-walk 25 2 80, PGSB, --timeout 1800, RUNHW_MIN_WAIT_S=270 (5000-tick exit ~207 s after launch, CAP3d-D1).
- Binary: main 5ca997b3, binary_sha12 9297b7d42365, build_dirty 0; --no-fine-timing (the player default).
- Reference (not comparable as a delta): S8H-O1 38.04/40.24, S8HO2 38.24/40.27 whole-run/steady on 32cc99df4761
  (fine on, pre-decode-fix, pre-CAP3/PACE).
- Bar: both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera CLEAN, audio counters clean, x2.
- Prediction: steady >= 40.0; whole-run 38.3-38.9 -- still UNDER 39.2 (the end-of-dialogue stall, 1.1-1.7 s, is not
  fixed; PLAN-GATES lever 1 expected +0.3..0.6); late_writes 0 (CAP3/PACE), fps_p50 40.
- Void: stamp != 9297b7d42365 or build_dirty != 0; not room 35; run-hw exit != 0; witness not clean; INPUT-LOG pair missing.
- Result: one STATUS.md row per cell.
