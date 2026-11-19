# RGB1 -- MMD IN PLAY on ags 0372's release, arm B (DOSAGS_GUI_CTRL_MARK=1), L2 A/B cell (written 2026-11-09; pre-registration, before any data)
- Binary: RGREL.EXE = main 35d1135f release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; hash-identical
  to the reviewed L2REL and to round RF's RFREL (0371 and 0372 default OFF; R2 default ON). VOID if the staged stamp differs.
  BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4",
  "DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=(default) mode=0" and "DOS-PORT guictrlmark DOSAGS_GUI_CTRL_MARK=1 mode=1" (the
  *_final mode= lines in RUNMANI.LOG stand in if a startup line is missing); charreuse_final skips > 0 and boxed > 0;
  guictrlmark_final l2 > 0, else VOID.
- Arm B: SET DOSAGS_GUI_CTRL_MARK=1 in RUN.BAT.
- Fixture: P9M1's line verbatim (as RFA1..RFA2: AGSSAVE.007 f486d0e9..., DRIVE 5 host clicks, TAS 12440, sound ON cfg). Witness:
  the camera sheet shows play (room 1 -> 2), else VOID. displayed = 1 - frames_skipped/ticks. Registered windows: room 1 + entry
  as ONE window 5480-8400, room 2 8400-9500, late 9500-end, ticks - renders between the first persec rows at or after each edge
  (ROUNDRE-2026-11-09/rescore.py; its room1 / entry split at 7890 is not registered). Raw guiclip_final, charreuse_final,
  guictrlmark_final, catchup lines.
- L2 ABBA x2 (RGA1 RGB1 RGB2 RGA2, then RGA3 RGB3 RGB4 RGA4; one binary, only the env differs; pairs A1/B1, B2/A2, A3/B3,
  B4/A4). A = DOSAGS_GUI_CTRL_MARK unset; B = DOSAGS_GUI_CTRL_MARK=1 (a GUI whose only change is some controls marks only those
  controls' rects). Basis: LAB-L2G sections 5-6 and 8 (lab: MMD's action-label flip ticks render 5.31 -> 2.05 ms, scene 10.21 ->
  8.25 ms at 40k; 486 estimate about -10 ms per flip tick, band 7-13). Round RF's reading of the pacer (ROUNDRF README) applies:
  a flip tick's overrun is repaid at ~7 ms per skipped frame unless forgiven, so -10 ms per flip tick is worth ~1-2 skips each.
  P1 (room 1 + entry): B has 3 fewer skips than A per pair (band 2-5), LAB-L2G section 6's draft. FALSIFIED if the MEAN over the
  pairs that ran is < 1 fewer. (Changed from the draft's "either pair < 1" before any data: round RF showed one pair's room 1 +
  entry moving by +6 against -2 for the other with a lever of similar size, so a per-pair falsifier cannot tell a 3-skip effect
  from noise; that is also why this round runs two ABBAs.)
  P2 (whole run): mean(B) - mean(A) = +0.04 points (3 skips per run; band +0.03 to +0.07). FALSIFIED if < 0. Each pair's
  whole-run difference is reported next to the verdict. Information: a B cell whose late window is worse than its pair's A by
  > 5 skips is reported.
  Power, stated before data: round RF's whole-run pair differences were -10 and +1 skips (SD 7.8), so with 4 pairs the mean's
  standard error is ~4 skips against a 3-skip prediction (~3 if round RE's 0163 pairs, +20 / +15, are pooled around their own
  mean). Two or four pairs are a thin basis for an SD. A null here would not rule out a gain of that size.
  Audio clean in every cell (underruns 0, overwrites 0). No instrumented cell this round (no budget), so the flip-tick
  mechanism is not measured on the 486 here; guictrlmark_final l2 / ctrls / px in B are reported.
  Drift note: the A arms are compared within the round only. Rounds RE / RF's default-config cells read 98.89-99.06%.
- Round RG (ags 0372's L2 to the 486, one power-on; operator 2026-11-09: L2 alone vs off, same-build ABBA, everything else
  default; sdlports: L2's ABBA after RF): WARMUPRG, RGA1 RGB1 RGB2 RGA2, RGA3 RGB3 RGB4 RGA4 (the second ABBA drops first);
  cap 120 min. Budget line: need at RGA1 3040 s (first ABBA), at RGA3 3040 s; whole round after the warm-up 6080 s, vs
  CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s.
