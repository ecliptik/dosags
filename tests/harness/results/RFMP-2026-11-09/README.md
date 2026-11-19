# RFMP -- MMD in play on ags 0372's INSTRUMENTED build, DOSAGS_ROUTE_PREWARM=1: click logic after the warm (written 2026-11-09; pre-registration, before any data)
- Binary: RFINS.EXE = main 35d1135f instrumented (ags 0001-0372), stamp 01658435489c, build_dirty=0, sha256 234b5626...; hash-
  identical to the reviewed L2INS. VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4",
  "DOS-PORT guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=0" and "DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=1 mode=1" (the
  routeprewarm_final / guictrlmark_final mode= in RUNMANI.LOG stand in if the startup line is missing); charreuse_final skips > 0 and boxed > 0; routeprewarm_final prewarms > 0, else VOID.
- Fixture: RDMP's line verbatim (fine timing on, DOSAGS_TICKLOG=12500, TICKS.BIN; R2 at its default where RDMP set =2, the same
  mode) plus SET DOSAGS_ROUTE_PREWARM=1. Reader: tests/harness/f1/f1prof.py (grouped by tick). Camera shows play, else VOID.
- P3 (mechanism): logic (ugo - scene - render) of the tick carrying the first room click after the restore <= 80 ms (RDMP 233),
  and of the tick carrying the first room-2 click <= 100 ms (RDMP 370). FALSIFIED if either > 120 ms. Clicks are TICKS kinds
  5 / 6; the room-2 entry is kind 4. Information: the warm's own cost inside the two stall ticks (routeprewarm_final us /
  max_us; LAB-L1R section 7 predicts 77-170 ms per warm on the 486), stall_ticks and the tick_stall list (P4's shape), and
  displayed with fine timing on (RDMP 98.66%).
- Round RF (ags 0371's L1 to the 486, one power-on; per LAB-RB section 7 and the operator's 2026-11-08 decisions: L1 lands
  default off, its S16 / S32P paired cells are information against the 39.2 floor if the budget allows; L2 (0372) is NOT in
  this round, its ABBA follows this one, sdlports 2026-11-09): WARMUPRF, RFA1 RFB1 RFB2 RFA2, RFMP, RFP0 RFP1 (the S32P pair
  drops first); cap 110 min. Budget line: need at RFA1 3040 s; whole round after the warm-up 5340 s (3040 + RFMP 780 + 1520),
  vs CAP_MIN 110 x 60 - warm-up 630 - 240 = 5730 s. An S16 pair as well does not fit (6860 > 6330 s even at 120 min): a later
  round.
