# RFB1 -- MMD IN PLAY on ags 0372's release, arm B (DOSAGS_ROUTE_PREWARM=1), L1 A/B cell (written 2026-11-09; pre-registration, before any data)
- Binary: RFREL.EXE = main 35d1135f release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; hash-identical
  to the reviewed L2REL (0371 and 0372 default OFF; R2 default ON since 0370). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4",
  "DOS-PORT guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=0" and "DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=1 mode=1" (the
  routeprewarm_final / guictrlmark_final mode= in RUNMANI.LOG stand in if the startup line is missing); charreuse_final skips > 0 and boxed > 0; routeprewarm_final prewarms > 0, else VOID.
- Arm B: SET DOSAGS_ROUTE_PREWARM=1 in RUN.BAT.
- Fixture: P9M1's line verbatim (as REA1..REA2: AGSSAVE.007 f486d0e9..., DRIVE 5 host clicks, TAS 12440, sound ON cfg). Witness:
  the camera sheet shows play (room 1 -> 2), else VOID. displayed = 1 - frames_skipped/ticks. Windows: room 1 + entry as ONE
  window 5480-8400, room 2 8400-9500, late 9500-end, ticks - renders between the first persec rows at or after each edge
  (ROUNDRD's rule; ROUNDRE-2026-11-09/rescore.py). Raw guiclip_final, charreuse_final, routeprewarm_final, catchup lines.
- L1 ABBA (RFA1 RFB1 RFB2 RFA2, one binary, only the env differs; pairs RFA1/RFB1 and RFB2/RFA2). A = DOSAGS_ROUTE_PREWARM
  unset; B = DOSAGS_ROUTE_PREWARM=1 (the legacy pathfinder's per-mask analysis built at FadeIn, inside the restore and room-load
  stalls). Basis: LAB-RB section 7 (the sdlports-reviewed draft), LAB-L1R. Round RE's per-second rows put a 6-skip burst at the
  first room-1 click after the restore (~6160-6210 in all six RE MMD cells) and a 6-7 skip burst after the ~345 ms tick that
  follows the room-2 load (RDMP: the first room-2 click, 370 ms of logic); those are L1's two targets.
  P1 (per pair, room 1 + entry window): B has 6 fewer skips than A (band 3-9). FALSIFIED if either pair has < 2 fewer.
  P2 (whole run): mean(B) - mean(A) = +0.09 points (band +0.04 to +0.13). FALSIFIED if < +0.02, or if a B cell is worse than
  its pair's A cell in the late window by > 5 skips.
  P4 (stall edge, mechanism): the first room-2 click drops under threshold_ms 250, so B cells log stall_ticks 2 (the restore and
  the room-2 load) where A cells log 3, and B's tick_stall list has no ~345 ms entry. Information, not a falsifier: a B cell
  with stall_ticks 3 is reported with its tick_stall lines.
  Audio clean in every cell (underruns 0, overwrites 0), as round RE.
  Note (as RE): the rig's DRIVE host clicks are wall-timed; the warm lengthens the two stall ticks by ~0.1-0.2 s on the 486
  (LAB-L1R section 7: 77-170 ms per warm), so later clicks may land a few ticks later in B. The fixed windows are P1's measure as
  registered; the per-second rows are reported for each pair.
  Drift note: RD's R3-only arms ran 0.5-0.8 points below RC's on another day, so P1 / P2 are paired within the round, not
  against RE. RE's default-config cells (98.97 / 99.04 / 99.04 / 99.06) are the A arms' expected level on a like day.
- Round RF (ags 0371's L1 to the 486, one power-on; per LAB-RB section 7 and the operator's 2026-11-08 decisions: L1 lands
  default off, its S16 / S32P paired cells are information against the 39.2 floor if the budget allows; L2 (0372) is NOT in
  this round, its ABBA follows this one, sdlports 2026-11-09): WARMUPRF, RFA1 RFB1 RFB2 RFA2, RFMP, RFP0 RFP1 (the S32P pair
  drops first); cap 110 min. Budget line: need at RFA1 3040 s; whole round after the warm-up 5340 s (3040 + RFMP 780 + 1520),
  vs CAP_MIN 110 x 60 - warm-up 630 - 240 = 5730 s. An S16 pair as well does not fit (6860 > 6330 s even at 120 min): a later
  round.
