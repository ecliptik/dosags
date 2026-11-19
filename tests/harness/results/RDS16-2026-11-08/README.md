# RDS16 -- 5 Days S16 on the R2 release build with DOSAGS_CHAR_REUSE=2: the S16 guard (written 2026-11-08; pre-registration, before any data)
- Binary: RDREL.EXE = main 1e3609c2 release (ags 0001-0369), stamp 84c1a74fdcf6, build_dirty=0, sha256 ffe49dab...; byte-identical
  to the reviewed R2REL (cmp: 0 differing bytes; stamp = hash of build inputs). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=2 mode=2" and "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4", else
  VOID. R2 engages here (lab: ~854 skips on room 3, all drawn in full since R3 never boxes there); charreuse_final recorded; boxed
  > 0 is a finding.
- Fixture: GR16's line verbatim (as RCS16). Scorer: gatebar.py --label S16 --stamp 84c1a74fdcf6 --room 3. Prediction: MET (RCS16
  39.29 / 40.15 / 99.48%). Whole-run carries the restart-save noise (rounds SU, RC). The first cell to drop if the cap is short.
- Round RD (R2 = ags 0369, DOSAGS_CHAR_REUSE=2 on the R3 default, vs R3-only, to the 486, one power-on; sdlports' design 2026-11-08, LAB-R2B section 7): WARMUPRD, RDA1 RDB1 RDB2 RDA2, RDMP, RDS16 (first to drop); cap 100 min; dated 2026-11-08.
  Budget line: need at RDA1 (the ABBA block) 3040 s, whole round after the warm-up 4580 s (3040 + RDMP 780 + RDS16 760), vs
  CAP_MIN 100 x 60 - warm-up 630 - 240 = 5130 s available.
