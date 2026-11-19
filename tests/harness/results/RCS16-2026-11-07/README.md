# RCS16 -- 5 Days S16 on the R3-default release build: the S16 guard (written 2026-11-07; pre-registration, before any data)
- Binary: RCREL.EXE = main 9e54b6d9 release (ags 0001-0368), stamp 4c9f83b62c5c, build_dirty=0, sha256 7deb7ca9...; byte-identical
  to the reviewed R3REL (cmp -l: 0 differing bytes; stamp = hash of build inputs). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4". R3 does not engage here (flagged > 0, skipped 0, boxed 0);
  boxed > 0 is a finding. latch_fullrestore= and fb_whole= recorded (expected 0).
- Fixture: GR16's line verbatim (as CFS16). Scorer: gatebar.py --label S16 --stamp 4c9f83b62c5c --room 3. Prediction: MET (CFS16
  39.36 / 40.12 / 99.58%). Whole-run carries the restart-save noise (round SU). The first cell to drop if the cap is short.
- Round RC (R3 = ags 0368, default since main 9e54b6d9, to the 486 + round SW1's save-trace pair first, one power-on; sdlports' design 2026-11-07): WARMUPRC, SW1TA, SW1TB, RCA1 RCB1 RCB2 RCA2, RCMP, RCS16 (first to drop); cap 115 min; dated 2026-11-07.
