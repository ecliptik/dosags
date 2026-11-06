# GR32P -- Gate S32 (S32P) on the RELEASE flavour, x1, round R2 (written 2026-11-05; pre-registration, before any data)
- Bar (PLAN-GATES, unchanged; x1 here, PLAN-NEXT R2): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera
  witness clean; audio by the counters (overwrites 0, late_writes 0, silent_irqs 0 outside room loads).
- Binary: rel.exe = build/ags-release/ags.exe (DOSAGS_RELEASE=1, main f2228d5e; minstack 512k explicit since 806b0ec1, exe unchanged),
  stamp a1dba5d61624, build_dirty 0, 8,598,425 B, sha256 1fc012c16d41...; R1's binary. VOID if the staged stamp differs.
- Fixture: GL32A's line verbatim (build/ws/roundBATCH/GL32.ARGS: 5days --startr 3, drive 2 = walk 25 2 90, S32P-ACSETUP-ON.CFG (24d874f2...)
  :ACSETUP.CFG, FORCE_COLOR_DEPTH=32 MAX_SCALE=1 PACK24=1, direct framebuffer, TAS 5000, --no-fine-timing, PGSB, MIN_WAIT 270) + BLASTER line.
- Witness: BLASTER.TXT (RUN.BAT `ECHO %BLASTER% > BLASTER.TXT`, --collect) must read "A220 I7 D3 P330 T3" stripped, else VOID.
  Camera sheet first. Capture: operator 2026-11-05 bar -- R2 only after a named stick/cable swap + 90 min clean (vcctrl).
- Scorer: gatebar.py --label S32 --stamp a1dba5d61624 --room 3 GR32P-2026-11-05 GR32P-2026-11-05 (one cell given twice; its own MET line is the reading).
- Comparison: GL32A/B on 8249193ed041, 39.28 / 40.12 and 39.34 / 40.07. Prediction: at or above them.
- Out of band: one x2 re-run on the same binary before v0.1; the 09-30 claim is not withdrawn by an x1 miss, and the miss is recorded.
- Round R2: WARMUPR2, GR16WBP, GR16WBR, GR16, GR32P; one power-on, cap 75 min; dated 2026-11-05, else re-dated first.
