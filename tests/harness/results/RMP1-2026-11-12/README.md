# RMP1 -- MMD IN PLAY (P9M1 line, DRIVE 5) on RMREL, default config, memlog off: the bridge (written 2026-11-12; pre-registration, before any data)
- Binary: RMREL.EXE = main 4aff3001 release (ags 0001-0373 + 0376, the TEMPORARY DOSAGS_MEMLOG=1 diagnostic, off unless
  set; sdlports-reviewed), stamp 2725928f2e37, build_dirty=0, sha256 b221866b..., +1,879 B over round RL's 942ad0260d36. Off path: one
  cached int test per sample (lab: tick-phase call counts identical to the unpatched build). VOID if the staged stamp
  differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Fixture: P9M1's line verbatim (DRIVE 5 host clicks). Counts by the board-counter rule (no in-play pkt_partial, no
  mouse.dropped). Expectation: 98.6-99.3% (RLP1 99.11%); outside it is reported as day drift. First to drop.
- USB4VC firmware 0.5.109 (as round RL, where it passed: strict FIFO, one event per packet, original spacing). Reported per
  cell: pkt_partial / pkt_timeout / mouse.dropped and ev_in == pkt_built; a partial voids an MS3 cell from that press (rule M0).
- Round RM (the freeze-cause round; sdlports' shape): WARMUPRM, RMCALQ [-> RMCAL on a calq miss], RMA1 RMB1 RMB2 RMA2 (the
  swap ABBA), RMP1 (P9M1 bridge; first to drop). One power-on, cap 120 min. Budget line: need at RMCALQ 1520 s (calq 760 +
  the full cal 760, counted up front); the ABBA block's graded needs RMA1 3040 / RMB1 2280 / RMB2 1520 / RMA2 760; whole round
  after the warm-up 5320 s with the full cal, 4560 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s.
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
