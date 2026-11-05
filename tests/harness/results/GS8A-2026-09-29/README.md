# GS8A -- Gate S8 re-reading, cell 1 of 2, round GATE (pre-registration, before any data)
- Bar (PLAN-GATES.md, verbatim): "Bar per depth, sound ON, Mach64, fixed timestep, 512x384 centred 1x (S32: 640x480x32 1:1): both tick
  figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera witness clean, x2; audio by the counters (pcm_irqs exact, overwrites
  0, late_writes 0, silent_irqs 0 outside room loads)".
- Binary: main b7ac6c46 (0241/0242 ON, 0246 ON via 0249, 0319 ON, 0245/0320/0322 OFF), stamp 3074cd9ce099, build_dirty 0, sha256
  480ca90d5730b40b..., 8,667,381 B. Player default: no DOSAGS_ pins.
- Fixture: round R's S8R line verbatim -- run-hw trilbysnotes --startr 35, drive 3 (walk 25 2 80),
  ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, --no-fine-timing,
  PGSB, RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Scoring: PLAN-GATES' claim procedure -- the cell's sumline tick figures (whole-run, steady) + RUNMANI (fps_p50, completeness, audio
  counters); no scorer script (as round R's S8 and round Q's S16). VOID: stamp, exit != 0, wrong room.
- Last reading (round R, main 5ca997b3 `9297b7d42365`): whole-run 38.76/38.76, steady 40.24/40.27, silent 6/4, NOT MET.
- Round GATE: warm-up + GS8A/B, GS16A/B, GS32A/B; waits for the operator (system OFF until they say); a re-date precedes any data.
