# RCMP -- MMD in play on the clean INSTRUMENTED build, R3 default: render per drawn tick, late stretch (written 2026-11-07; pre-registration, before any data)
- Binary: RCINS.EXE = main 9e54b6d9 instrumented, stamp aa334361a087, build_dirty=0, sha256 1cb00ce1...; byte-identical to the
  reviewed R3INS (cmp -l: 0 differing bytes). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4", boxed > 0. Fixture: CFMP's line verbatim (fine timing on,
  DOSAGS_TICKLOG=12500, TICKS.BIN). Reader: tests/harness/f1/f1prof.py (grouped by tick, c457cda9), drawn ticks, loop 9500-end.
- LAB-R3 (c), verbatim: median render per drawn tick over 9500-end, central 2.7 ms, band 2.4-3.6. FALSIFIED if > 3.6 ms, or less
  than 2.5 ms below the same-flavour R1-only arm. This round has no instrumented R1 arm; the R1 reference is CFMP (CFINS
  39c6e4b65079, R1 default, same fixture, same reader), read the same way -- a different binary and day, stated as such.
- Information: script_vm (CFMP 12.18 ms/tick), displayed (CFMP 75.80%), rb_sprite per drawn frame (CFMP 3.96). Camera shows play.
- Round RC (R3 = ags 0368, default since main 9e54b6d9, to the 486 + round SW1's save-trace pair first, one power-on; sdlports' design 2026-11-07): WARMUPRC, SW1TA, SW1TB, RCA1 RCB1 RCB2 RCA2, RCMP, RCS16 (first to drop); cap 115 min; dated 2026-11-07.
