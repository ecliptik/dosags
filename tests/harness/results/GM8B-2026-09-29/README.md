# GM8B -- Gate S8 re-reading with DOSAGS_MSGSKIP=1, cell 2 of 2, round S8M (pre-registration, before any data)
- Bar (PLAN-GATES.md, verbatim): "Bar per depth, sound ON, Mach64, fixed timestep, 512x384 centred 1x (S32: 640x480x32 1:1): both tick
  figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera witness clean, x2; audio by the counters (pcm_irqs exact, overwrites
  0, late_writes 0, silent_irqs 0 outside room loads)".
- Fixture: round GATE's GS8 line verbatim (round R's S8R: trilbysnotes --startr 35, drive 3 walk 25 2 80,
  ACSETUP-ON-512X384-ROUND.CFG, direct framebuffer, TAS 5000, --no-fine-timing, PGSB, MIN_WAIT 270, --timeout 1800) PLUS --env
  DOSAGS_MSGSKIP=1 (the operator's "click promptly"; lab-s8 325ba13f MSGSKIP.md). No other pins.
- Binary: main a504b469 (ags 0324 landed; 0241/0242/0246/0319 ON), stamp d8c3aa2eafdf, build_dirty 0, sha256
  882d33abdda3710daf4f85aabe59afcf8f9561cd7b8926e2db8582db505aed2d, 8,668,036 B.
- Scoring: PLAN-GATES' claim procedure (sumline tick figures + RUNMANI counters, no script). VOID: stamp, exit != 0, room != 35, or
  not exactly one "DOS-PORT msgskip n=1" line.
- Comparability: whole-run and stall_ms are NOT comparable with pre-change S8 readings (rounds R, GATE, the V/X/X2/ID A arms) --
  MSGSKIP.md "Comparability".
- Round S8M: warm-up + GM8A GM8B (cell 2 of 2); operator approved "All three" (CS1 -> CS2 -> S8M) 2026-09-29.
