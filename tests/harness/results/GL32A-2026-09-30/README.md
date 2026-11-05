# GL32A -- Gate S32 re-read under the ags 0347 counter, cell 1 of 2, round BATCH (written 2026-09-29; pre-registration, before any data)
- Bar (PLAN-GATES.md, verbatim, unchanged): "Bar per depth, sound ON, Mach64, fixed timestep, 512x384 centred 1x (S32: 640x480x32
  1:1): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera witness clean, x2; audio by the counters (pcm_irqs exact,
  overwrites 0, late_writes 0, silent_irqs 0 outside room loads)". Under ags 0347 silent_irqs counts dropouts only; a cold start's first
  late half (at most one IRQ per owed episode) is start_latency_irqs, reported, not in the bar.
- Binary: main 553588d4 (= 62c06f3e + ags 0347, lab/mmd 8849e57e), stamp 8249193ed041, build_dirty 0, sha256
  60b461ab57321ec1bf90b9dd162d4d46237e169182af3ec25fb7da1460f29777, 8,668,939 B (= lab-s8's AGSCN3). Player default: no other DOSAGS_ pins.
- Fixture: round GATE's GS32 line verbatim (S32P) -- run-hw 5days --startr 3, drive 2 (walk 25 2 90), S32P-ACSETUP-ON.CFG:ACSETUP.CFG
  (24d874f2...), DOSAGS_FORCE_COLOR_DEPTH=32 DOSAGS_MAX_SCALE=1 SDL_DOS_PACK24=1 SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1,
  DOSAGS_TAS_AUTO_EXIT_TICK=5000, --no-fine-timing, PGSB, RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Scoring: tests/harness/gatebar.py (committed with this README, before data), camera sheets reviewed first:
  gatebar.py --label S32 --stamp 8249193ed041 --room 3 GL32A-2026-09-30 GL32B-2026-09-30. VOID as in its header.
- Last reading: round GATE (b7ac6c46, pre-0347 counter) 39.32/40.12 and 39.28/40.08, NOT MET on audio only (silent in play: GS32A
  921, 1421; GS32B 4912). Prediction: ticks in band x2; silent_irqs 0 outside loads; cold-start first halves show as startlat irqs=1.
- Round BATCH ("Batch after 0347 lands"): warm-up, CAPS8, GL16, GL32, GL8, WBC16; one power-on; dated 2026-09-30, else re-dated first.
