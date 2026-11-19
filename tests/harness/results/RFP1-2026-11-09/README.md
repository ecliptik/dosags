# RFP1 -- 5 Days S32P on ags 0372's release, DOSAGS_ROUTE_PREWARM =1: the S32P guard pair (information) (written 2026-11-09; pre-registration, before any data)
- Binary: RFREL.EXE = main 35d1135f release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; hash-identical
  to the reviewed L2REL (0371 and 0372 default OFF; R2 default ON since 0370). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4",
  "DOS-PORT guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=0" and "DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=1 mode=1" (the
  routeprewarm_final / guictrlmark_final mode= in RUNMANI.LOG stand in if the startup line is missing); charreuse_final skips > 0 (boxed 0: R3 never boxes room 3); routeprewarm_final prewarms >= 1 (the room-3 entry), else VOID.
- Fixture: round RC's S32 line verbatim (as GR32P: --startr 3, FORCE_COLOR_DEPTH=32, MAX_SCALE=1, PACK24=1,
  S32P-ACSETUP-ON.CFG 24d874f2..., TAS 5000) plus SET DOSAGS_ROUTE_PREWARM=1. Scorer: gatebar.py --label S32P
  --stamp 8c123c770d0b --room 3.
- Information against the 39.2 whole-run floor, not a falsifier (operator 2026-11-08): LAB-L1R section 7 predicts the warm
  costs 77-170 ms once at the room-3 load on the 486, so whole-run -0.024 to -0.039 ticks/s for RFP1 against RFP0; steady
  unchanged (+-0.05). A pair with RFP0 >= 39.2 and RFP1 < 39.2 is reported as a guard concern for any default-on decision.
  GR32P (2026-11-05, a pre-R2 binary) read 39.29 / 40.12; S32P has not run under R2's default before. Audio clean.
- Round RF (ags 0371's L1 to the 486, one power-on; per LAB-RB section 7 and the operator's 2026-11-08 decisions: L1 lands
  default off, its S16 / S32P paired cells are information against the 39.2 floor if the budget allows; L2 (0372) is NOT in
  this round, its ABBA follows this one, sdlports 2026-11-09): WARMUPRF, RFA1 RFB1 RFB2 RFA2, RFMP, RFP0 RFP1 (the S32P pair
  drops first); cap 110 min. Budget line: need at RFA1 3040 s; whole round after the warm-up 5340 s (3040 + RFMP 780 + 1520),
  vs CAP_MIN 110 x 60 - warm-up 630 - 240 = 5730 s. An S16 pair as well does not fit (6860 > 6330 s even at 120 min): a later
  round.

Amendment (before any data, sdlports 2026-11-09): this is ONE pair, and its predicted delta (-0.024 to -0.039 ticks/s) lies
well inside S32P's whole-run noise. The pair checks the 39.2 floor only: it cannot measure the warm's cost, and a difference
between RFP0 and RFP1 is not evidence either way.
