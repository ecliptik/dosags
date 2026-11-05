# GL16B -- Gate S16 re-read under the ags 0347 counter, cell 2 of 2, round BATCH (written 2026-09-29; pre-registration, before any data)
- Bar (PLAN-GATES.md, verbatim, unchanged): "Bar per depth, sound ON, Mach64, fixed timestep, 512x384 centred 1x (S32: 640x480x32
  1:1): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera witness clean, x2; audio by the counters (pcm_irqs exact,
  overwrites 0, late_writes 0, silent_irqs 0 outside room loads)". Under ags 0347 silent_irqs counts dropouts only; a cold start's first
  late half (at most one IRQ per owed episode) is start_latency_irqs, reported, not in the bar.
- Binary: main 553588d4 (= 62c06f3e + ags 0347, lab/mmd 8849e57e), stamp 8249193ed041, build_dirty 0, sha256
  60b461ab57321ec1bf90b9dd162d4d46237e169182af3ec25fb7da1460f29777, 8,668,939 B (= lab-s8's AGSCN3). Player default: no other DOSAGS_ pins.
- Fixture: round GATE's GS16 line verbatim (5125f3b2; round Q's S16Q) -- run-hw 5days --startr 3, drive 2 (walk 25 2 90),
  ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, --no-fine-timing, PGSB,
  RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Scoring: tests/harness/gatebar.py (committed with this README, before data), camera sheets reviewed first:
  gatebar.py --label S16 --stamp 8249193ed041 --room 3 GL16A-2026-09-30 GL16B-2026-09-30. VOID as in its header.
- Last reading: round GATE (b7ac6c46, pre-0347 counter) 39.28/40.10 and 39.31/40.10, NOT MET on audio only (GS16A silent 2 in play,
  ticks 1864 and 4494). Prediction: ticks in band x2; silent_irqs 0 outside loads; any cold-start first half shows as startlat irqs=1.
- Round BATCH ("Batch after 0347 lands"): warm-up, CAPS8, GL16, GL32, GL8, WBC16; one power-on; dated 2026-09-30, else re-dated first.
