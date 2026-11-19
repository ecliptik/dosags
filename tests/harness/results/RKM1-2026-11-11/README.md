# RKM1 -- MS3 (moving fixture) on ags 0373's release, default config: the campaign baseline cell (written 2026-11-11; pre-registration, before any data)
- Binary: RKREL.EXE = main 728706d9 release (ags 0001-0373), stamp 942ad0260d36, build_dirty=0, sha256 36473d61...; = the
  reviewed L2DREL (R2 on and L2 on by default; L1 off; the 0374 cap not in this build). VOID if the staged stamp differs.
  BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- MS3: DRIVE 6, DRIVE6_MODE=ms, one-call presses, the values from RKCALQ (or RKCAL); 114 presses. Runs only after a
  calibration GATE PASS. Pointing witness (drive6-gate.sh --play): M0 first (a board pkt_partial voids from the press whose
  call meets it), then G0 / G1 / D1+ (all 114 presses sent and ok, every press walks, rooms exactly [1, 2], A room 817..841,
  B 916..940, y 116..140). A PLAY-VOID cell is VOID for the baseline (reported, not scored); two VOIDs stop the block.
  INPUT-LOG mouse.dropped is reported; a drop VOIDs a cell only through M0 or the walk / landing checks.
- The MS3 baseline (the campaign's measure): RKM1..RKM4, default config on ags 0373 (L2 on). Reported: displayed = 1 -
  frames_skipped/ticks per cell, the mean and SD, skips per window (room 1 + exit, room 2), catchup and audio lines.
  Model figure, not a falsifiable prediction: round RJ's RJMP measured MS3 on the 486 over presses 17-51 at 75.8% displayed
  (398 of 1,648 ticks; walking ticks 24.9 ms against a 25 ms budget, click ticks 63.6 ms of logic); est486b with the click
  scale refitted gives the whole-run model. Expectation, information only: ~76-84% displayed (L2 on now trims the GUI
  redraw ticks after each click, measured -8 skips per P9M1 run in round RG). Scene rule: MS3's displayed % is never
  reported in the same column as P9M1's. No target is set by this round; the operator sets it from this baseline.
- USB4VC firmware 0.5.108 (flashed 2026-11-11 22:36Z by vcctrl, operator's OK: an interrupted PS/2 packet is resumed, never
  abandoned; +-127 summing unchanged; counters reset at the flash). Firmware verdict for this round (sdlports), from each DRIVE 6
  cell's INPUT-LOG.jsonl mouse.dropped rows (pkt_partial) and vcctrl's per-cell report of the board's "resume" counter page
  (pkt_resumed, partial_waits, inhibit_retry, abandon_budget, max_wait_ms): PASS if pkt_partial is 0 in every in-play window
  AND pkt_resumed / partial_waits rise within +-5 s of the known stall times (~+132 / ~+178 s after each MS3 cell's lock);
  FAIL (falsified) if any pkt_partial > 0 (rule M0 then voids that cell); information only, not a fix claim, if pkt_resumed
  stays 0 while pkt_partial is 0 (no stall reached the board). vcctrl's powered check of 0.5.108 (keyboard typing, LEDs, a few
  clicks at a DOS prompt) rides on WARMUPRK and RKCALQ: a keyboard or click failure there stops the round.
- Round RK (the hardware test of USB4VC 0.5.108 and the MS3 baseline, first round on ags 0373; sdlports' shape): WARMUPRK,
  RKCALQ (the short re-check against round RJ's passing full cal RJCAL) [-> RKCAL, the full cal, on any calq miss],
  RKM1..RKM4 (MS3), RKP1 RKP2 (P9M1 bridge), RKMP (MS3 instrumented, TICKS; first to drop). One power-on, cap 120 min.
  Budget line: need at RKCALQ 4560 s (calq 760 + the full cal 760, counted up front + the MS3 block 3040); whole round after
  the warm-up 6100 s without the full cal (760 + 3040 + 1520 + 780), 6860 s with it, vs CAP_MIN 120 x 60 - warm-up 630 - 240
  = 6330 s: if the full cal runs, RKMP drops, by design. Harness: local main 5d3bfebe (drive-walk6.sh one-call presses;
  drive6-cal.py / drive6-gate.sh with C10 on >= 15-count packets, calq's drift report and NEXT-FULL-CAL flag, and rule M0:
  an MS3 cell is VOID from the press whose call meets a board pkt_partial). Campaign context: MS3 is the campaign's measure,
  its target set only after a baseline exists; P9M1's 99% x2 is retired, not met.
