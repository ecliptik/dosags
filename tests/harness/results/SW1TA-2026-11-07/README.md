# SW1TA -- S32P line, lever OFF, TRACE cell (DOSAGS_SW=1, SWTRACE.TXT) (written 2026-11-07; pre-registration, before any data)
- Binary: SWLAB2.EXE = LAB instrumented record (same base + diff), build_dirty=1, stamp c72796d35101, sha256 6c1a2f2d...; NOT a
  landing; no SW1 result enters hub figures. VOID if the staged stamp differs. BLASTER.TXT witness.
- Fixture: GR32P's line verbatim (as SU32*), + round SU's mechanism lines (SVPRE / DIRLIST / SDRV / SVPOST).
- Witness: STDOUT "DOS-PORT savemem DOSAGS_SAVEMEM mode=0 path=stream" for slot=999, else VOID.
- Purpose: per-INT-21h time attribution of the 486 save (which single call holds any 200-300 ms excess: a data write, a patch,
  the truncate, or the close). Timings NOT scored (the tracer itself costs ~18-35 ms per save). Predicted counts (as LAB-SW): INT 21h 117; 40h 16 (9 in place); 42h 82; 44h 14.
- Round SW1 (save-write lever 1 on the 486; operator decision via sdlports: an exact, byte-identical speed-up of the restart-point save; sdlports: SW1 goes now, S8 dropped for time): WARMUPSW, SW1A1 SW1B1 SW1B2 SW1A2 SW1A3 SW1B3 SW1B4 SW1A4, SW1TA SW1TB; one power-on, cap 120 min; dated 2026-11-07.
- Amendment (before any data of this cell, 2026-11-07): not run in round SW1 (dropped by the time guard); runs FIRST in round RC
  (sdlports), same line, binary and witness. Round RC: WARMUPRC, SW1TA, SW1TB, RCA1 RCB1 RCB2 RCA2, RCMP, RCS16.
