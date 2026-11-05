# S16Q1 -- Gate S16 cell, round Q (pre-registration, before any data; PLAN-GATES claim procedure)
- Binary: landed main 75543c93, binary_sha12 b1cd5ccee175, build_dirty 0, sha256 e73f9deda5f79389adb44b6aea11ba12370c3b92fcddce55c11fa55fe7cac411.
- Fixture: SB2C1's exactly = the S16 gate fixture, the SAME as round F's S16 figures (whole-run 39.14/39.13, steady
  39.98/39.95), so the reading is comparable: run-hw 5days --startr 3, DOSAGS_TAS_AUTO_EXIT_TICK=5000,
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, ACSETUP-ON-512X384-ROUND.CFG (sound on, OPL3, no hint), drive-walk 25 2 90,
  PGSB, --timeout 1800, RUNHW_MIN_WAIT_S=270 (5000-tick auto-exit ~178 s after launch, S16U1), --no-fine-timing.
- 2026-09-26 (coordinator, before any data): reads at the player default (fine off); round F's 39.14/39.13 were
  fine-on (pre-0315, timers always on), so the comparison with F includes ~0.7 ms/tick of logic that 0315 removed;
  the claim is the bar, not the delta.
- Bar (per cell, x2 for the claim): tick_rate and tick_rate_steady both 39.2-40.8; fps_p50 >= 40; completeness >= 95%;
  camera witness CLEAN; pcm_irqs exact, overwrites 0, late_writes 0, silent_irqs 0 outside room loads.
- Prediction: both tick figures IN BAND (>= 39.2): the landed gains since round F (SDL 0240 inputs, ags 0315, 0215/0216
  decode, SDL 0250-0256) against a 0.06-0.07 shortfall; late_writes 0, overwrites 0.
- Void: stamp != b1cd5ccee175 or build_dirty != 0; not room 3; run-hw exit != 0; witness not clean; INPUT-LOG pair missing.
- Result: one STATUS.md row per cell, in the result commit.
