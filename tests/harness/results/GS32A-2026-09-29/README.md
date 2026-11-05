# GS32A -- Gate S32 (S32P) re-reading, cell 1 of 2, round GATE (pre-registration, before any data)
- Bar (PLAN-GATES.md, verbatim): "Bar per depth, sound ON, Mach64, fixed timestep, 512x384 centred 1x (S32: 640x480x32 1:1): both tick
  figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera witness clean, x2; audio by the counters (pcm_irqs exact, overwrites
  0, late_writes 0, silent_irqs 0 outside room loads)".
- Binary: main b7ac6c46 (0241/0242 ON, 0246 ON via 0249, 0319 ON, 0245/0320/0322 OFF), stamp 3074cd9ce099, build_dirty 0, sha256
  480ca90d5730b40b..., 8,667,381 B. Player default: no DOSAGS_ pins.
- Fixture: S32P (operator-ruled S32 fixture) as round V ran it, arm env dropped -- run-hw 5days --startr 3, drive 2 (walk 25 2 90),
  S32P-ACSETUP-ON.CFG:ACSETUP.CFG (24d874f2...), DOSAGS_FORCE_COLOR_DEPTH=32 DOSAGS_MAX_SCALE=1 SDL_DOS_PACK24=1
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, --no-fine-timing, PGSB, RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Scoring: PLAN-GATES' claim procedure -- the cell's sumline tick figures (whole-run, steady) + RUNMANI (fps_p50, completeness, audio
  counters); no scorer script (as round R's S8 and round Q's S16). VOID: stamp, exit != 0, wrong room.
- Last S32P reading: round V S32FF1 (0240 on) whole-run 39.30, steady 40.10 -- an arm cell, not a gate reading.
- Round GATE: warm-up + GS8A/B, GS16A/B, GS32A/B; waits for the operator (system OFF until they say); a re-date precedes any data.
