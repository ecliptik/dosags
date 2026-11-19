# RDMP -- MMD in play on the clean INSTRUMENTED build, DOSAGS_CHAR_REUSE=2: scene + render per room-1 tick (written 2026-11-08; pre-registration, before any data)
- Binary: RDINS.EXE = main 1e3609c2 instrumented (ags 0001-0369), stamp f9f8dd6614c8, build_dirty=0, sha256 0e59c82b...; byte-identical
  to the reviewed R2INS (cmp: 0 differing bytes). VOID if the staged stamp differs. BLASTER.TXT.
- Witness (as arm B): SET DOSAGS_CHAR_REUSE=2; STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=2 mode=2" and "DOS-PORT guiclip
  DOSAGS_GUI_CLIP=(default) mode=4"; charreuse_final skips > 0 and boxed > 0, else VOID.
- Fixture: RCMP's line verbatim (fine timing on, DOSAGS_TICKLOG=12500, TICKS.BIN). Reader: tests/harness/f1/f1prof.py (grouped by
  tick, c457cda9), room-1 window 5480..7890: median scene + median render from its window table (all loop ticks in the window,
  as RCMP-2026-11-07/F1PROF-room1.txt; LAB-R2B 7's "drawn ticks" wording corrected -- RCMP's figure is over all 2,411 window
  ticks). Reference: RCMP (R3 default, RCINS aa334361a087, same fixture and reader; a different binary and day, stated as such):
  median scene 5.60 + render 4.09 = 9.69 ms.
- Prediction (LAB-R2 6.2's 486 band, unchanged): scene + render (medians, as above) cut by central 5.5 ms, band 3.5-6.5, i.e.
  3.2-6.2 ms. FALSIFIED if the cut is < 3.0 ms (LAB-R2 6.3's line). LAB-R2B section 6's lab cut, scaled by LAB-R2's ratios, is
  4.4-5.9 (inside the band).
- Information: script_vm per tick (RCMP 12.47), sc_prep_chars, bg_restore, rb_sprite_time per drawn frame (RCMP 1.97), displayed
  (RCMP 90.55%), charreuse_final. Camera shows play. Also (information, sdlports 2026-11-08): scene and render medians over room-1
  DRAWN ticks only, for both RCMP and RDMP -- R2 changes room 1's drawn fraction, which alone can move an all-tick median.
- Round RD (R2 = ags 0369, DOSAGS_CHAR_REUSE=2 on the R3 default, vs R3-only, to the 486, one power-on; sdlports' design 2026-11-08, LAB-R2B section 7): WARMUPRD, RDA1 RDB1 RDB2 RDA2, RDMP, RDS16 (first to drop); cap 100 min; dated 2026-11-08.
  Budget line: need at RDA1 (the ABBA block) 3040 s, whole round after the warm-up 4580 s (3040 + RDMP 780 + RDS16 760), vs
  CAP_MIN 100 x 60 - warm-up 630 - 240 = 5130 s available.
