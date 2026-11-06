# GR16R3 -- Gate S16 on the RELEASE flavour, x1, round R3 (the GR16 re-run owed by R2) (written 2026-11-05; pre-registration, before any data)
- Bar (PLAN-GATES, unchanged; x1 here, PLAN-NEXT R2): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera
  witness clean; audio by the counters (overwrites 0, late_writes 0, silent_irqs 0 outside room loads).
- Binary: rel.exe = build/ags-release/ags.exe (DOSAGS_RELEASE=1, main f2228d5e; minstack 512k explicit since 806b0ec1, exe unchanged),
  stamp a1dba5d61624, build_dirty 0, 8,598,425 B, sha256 1fc012c16d41...; R1's binary. VOID if the staged stamp differs.
- Fixture: GL16A's line verbatim (build/ws/roundBATCH/GL16.ARGS: 5days --startr 3, drive 2 = walk 25 2 90, ACSETUP-ON-512X384-ROUND.CFG
  :ACSETUP.CFG, direct framebuffer, TAS 5000, --no-fine-timing, fixed timestep, PGSB, MIN_WAIT 270, --timeout 1800) + the BLASTER line.
- Witness: BLASTER.TXT (RUN.BAT `ECHO %BLASTER% > BLASTER.TXT`, --collect) must read "A220 I7 D3 P330 T3" stripped, else VOID.
  Camera sheet first: R2's GR16 had no screen witness (camera pointed away; the card does not lock 512x384); camera on the LCD now.
- Scorer: gatebar.py --label S16 --stamp a1dba5d61624 --room 3 GR16R3-2026-11-05 GR16R3-2026-11-05 (one cell given twice; its own MET line is the reading).
- Comparison: GL16A/B on 8249193ed041, 39.29 / 40.13 and 39.29 / 40.10. Prediction: at or above them (R1: release = instrumented at S8).
- Out of band: one x2 re-run on the same binary before v0.1; the 09-30 claim is not withdrawn by an x1 miss, and the miss is recorded.
- Round R3: WARMUPR3, GR16R3; one power-on, cap 35 min; operator "yes, start next run" 2026-11-05. Dated 2026-11-05, else re-dated first.
