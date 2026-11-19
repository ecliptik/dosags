# SW1A2 -- 5 Days S32P line, save-write lever OFF (DOSAGS_SAVEMEM=0), timing cell, trace OFF (written 2026-11-07; pre-registration, before any data)
- Binary: SWREL2.EXE = LAB release record (main 41d82c06 + docs/lab/sw-lab-patches/lab-sw2.diff), build_dirty=1, stamp 761f64ceccac,
  sha256 3b76f3dc...; NOT a landing (a 0369+ landing gets its own review and a clean-build confirmation); no SW1 result enters hub figures.
  VOID if the staged stamp differs. BLASTER.TXT witness.
- Fixture: GR32P's line verbatim (as SU32*), + round SU's mechanism lines (SVPRE / DIRLIST / SDRV / SVPOST).
- Witness: STDOUT "DOS-PORT savemem DOSAGS_SAVEMEM mode=0 path=stream" for slot=999, else VOID.
- Scored on restart_savegame_ms (the engine's own line). PRIMARY (floor): median paired saving d = OFF - ON over the 4 pairs
  (SW1A1,SW1B1) (SW1B2,SW1A2) (SW1A3,SW1B3) (SW1B4,SW1A4) is >= 30 ms (estimate 31-92, central ~50; mean reported beside it).
  FALSIFIED if the median d < 20 ms. Fixed before data: median and 30, not a mean and 35 (one ~212 ms stall moves a 4-pair mean
  by ~50 ms; round SU had one such pair).
- If a pair is lost anyway (cap, recovery), the primary is the median of the COMPLETE pairs, n stated; < 3 complete pairs = VOID.
- H1 (second hypothesis, not the headline): every ON cell reads 110-210 ms. Falsified if any ON cell > 260 ms while its adjacent
  OFF cell >= 400 ms. VOID unless >= 3 of 4 OFF cells read >= 400 ms. If H1 is VOID or falsified, the next lever class is faster
  serialisation (~94% of the save at 40k; ~100-150 ms on the 486 that no I/O lever can touch).
- Round SW1 (save-write lever 1 on the 486; operator decision via sdlports: an exact, byte-identical speed-up of the restart-point save; sdlports: SW1 goes now, S8 dropped for time): WARMUPSW, SW1A1 SW1B1 SW1B2 SW1A2 SW1A3 SW1B3 SW1B4 SW1A4, SW1TA SW1TB; one power-on, cap 120 min; dated 2026-11-07.
