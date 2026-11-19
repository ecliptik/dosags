# ROP1 -- MMD IN PLAY (P9M1 line, DRIVE 5) on RNREL (0377 on), default config, memlog off (written 2026-11-12; pre-registration, before any data)
- Binary: RNREL.EXE, round RN's binary unchanged = main 987ddce1 release (ags 0001-0373 + 0376 + 0377; sdlports-reviewed),
  stamp 93df50d751a8, build_dirty=0, sha256 ce8d275f.... 0377 bounds the mixer's per-voice ring (patch 0049's
  Voice::ring: the consumed prefix is dropped once it reaches 64 KB) and is ON by default; its TEMPORARY
  DOSAGS_RING_LEGACY=1 switch restores the old unbounded growth (removal owed after this round's verdict, with 0376).
  VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Fixture: P9M1's line verbatim (DRIVE 5 host clicks). Counts by the board-counter rule (no in-play pkt_partial, no
  mouse.dropped). Same binary as RNP1 (99.37%), so this ties the day to RNP1 / RMP1 (98.96%) / RLP1 (99.11%).
  Expectation: 98.6-99.5%; outside it is reported as day drift. First to drop.
- USB4VC firmware 0.5.109 (as rounds RL / RM / RN). Reported per cell: pkt_partial / pkt_timeout / mouse.dropped and
  ev_in == pkt_built; a partial voids an MS3 cell from that press (rule M0).
- Round RO (the verdict round for ags 0377): WARMUPRO, ROCALQ [-> ROCAL on a calq miss], ROF1 ROL1 ROL2 ROF2 (the ring
  ABBA), RODT (DPMITIM2, information), ROP1 (P9M1 on RNREL; first to drop). One power-on, cap 120 min. Budget line: need
  at ROCALQ 1520 s (calq 760 + the full cal 760, counted up front); the ABBA block's graded needs ROF1 3040 / ROL1 2280 /
  ROL2 1520 / ROF2 760 (counted from the ABBA alone, so it never waits on what follows); then RODT 900 and ROP1 760, each
  under its own need after the ABBA (CUT reset): ROP1 and then RODT are dropped before any ABBA arm is. Whole round after
  the warm-up 6220 s with the full cal, 5460 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with the
  full cal, a warm-up more than ~110 s over its 630 costs ROP1 (then RODT), not an arm. (Round RN, same shape: warm-up
  593 s from relay-on, no full cal, every cell ran, power off at 90 min.)
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
