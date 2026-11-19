# REC1 -- MMD IN PLAY on ags 0370's release, default (R2 on): the 0370 confirmation (written 2026-11-08, re-dated 2026-11-09; pre-registration, before any data)
- Binary: REREL.EXE = main 4ee5b017 release (ags 0001-0370), stamp 9db4170acd89, build_dirty=0, sha256 f9202de6...; byte-identical
  to the reviewed R2DREL (cmp: 0 differing bytes). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2" and "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default)
  mode=4"; charreuse_final skips > 0 and boxed > 0, else VOID.
- Fixture: P9M1's line verbatim (as RDA1..RDA2: AGSSAVE.007 f486d0e9..., DRIVE 5 host clicks, TAS 12440, sound ON cfg). Witness:
  the camera sheet shows play (room 1 -> 2), else VOID. displayed = 1 - frames_skipped/ticks. Windows (information): room 1 +
  entry as ONE window 5480-8400, room 2 8400-9500, late 9500-end, ticks - renders between the first persec rows at or after each
  edge (ROUNDRD's rule). Raw guiclip_final, charreuse_final and catchup lines.
- Prediction (0370 confirmation; RD's R2 cells RDB1 / RDB2 98.97 / 99.07% with =2 on the 0369 binary): each cell 98.6-99.4%
  displayed (central 99.0). FALSIFIED if either cell < 98.3% (below RC's best R3-only cell, i.e. R2's gain gone).
  Drift note (sdlports 2026-11-08): RD's R3-only arms ran 0.5-0.8 points below round RC's; a day's offset of that size is
  expected and is why the confirmation band is wide.
- Round RE (ags 0370 = R2 on by default, confirmation, then patch 0163's DOSAGS_STALL_RESYNC A/B; one power-on; operator's
  decisions 2026-11-08, question tool; shape per sdlports): WARMUPRE, REC1 REC2, RES16, REA1 REB1 REB2 REA2 (the 0163 block drops first); cap 110 min.
  Budget line: need at REC1 (confirmation block) 2280 s; at REA1 (0163 block) 3040 s; whole round after the warm-up 5320 s, vs
  CAP_MIN 110 x 60 - warm-up 630 - 240 = 5730 s available. Staged while the operator's hold on the 486 stands (2026-11-08): this
  round runs only after the operator lifts it, and its dirs, READMEs and the driver's D line are re-dated before any data.

Re-dated 2026-11-09, before any data: the operator lifted the 486 hold ("Okay to power on", 2026-11-09 ~11:54Z). Nothing
else in this pre-registration changed.
