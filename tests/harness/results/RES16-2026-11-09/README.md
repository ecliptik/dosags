# RES16 -- 5 Days S16 on ags 0370's release, default (R2 on): the S16 guard (written 2026-11-08, re-dated 2026-11-09; pre-registration, before any data)
- Binary: REREL.EXE = main 4ee5b017 release (ags 0001-0370), stamp 9db4170acd89, build_dirty=0, sha256 f9202de6...; byte-identical
  to the reviewed R2DREL (cmp: 0 differing bytes). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2" and "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default)
  mode=4"; charreuse_final skips > 0, else VOID (boxed 0: R3 never
  boxes room 3).
- Fixture: GR16's line verbatim (as RDS16). Scorer: gatebar.py --label S16 --stamp 9db4170acd89 --room 3. Prediction: MET at
  RDS16's level (39.34 / 40.17, 99.52%, audio clean, camera CLEAN). Whole-run carries restart-save noise (rounds SU, RC).
- Round RE (ags 0370 = R2 on by default, confirmation, then patch 0163's DOSAGS_STALL_RESYNC A/B; one power-on; operator's
  decisions 2026-11-08, question tool; shape per sdlports): WARMUPRE, REC1 REC2, RES16, REA1 REB1 REB2 REA2 (the 0163 block drops first); cap 110 min.
  Budget line: need at REC1 (confirmation block) 2280 s; at REA1 (0163 block) 3040 s; whole round after the warm-up 5320 s, vs
  CAP_MIN 110 x 60 - warm-up 630 - 240 = 5730 s available. Staged while the operator's hold on the 486 stands (2026-11-08): this
  round runs only after the operator lifts it, and its dirs, READMEs and the driver's D line are re-dated before any data.

Re-dated 2026-11-09, before any data: the operator lifted the 486 hold ("Okay to power on", 2026-11-09 ~11:54Z). Nothing
else in this pre-registration changed.
