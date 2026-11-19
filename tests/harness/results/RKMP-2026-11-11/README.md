# RKMP -- MS3 on ags 0373's INSTRUMENTED build with TICKS: the 486's tick costs and the two known stalls (written 2026-11-11; pre-registration, before any data)
- Binary: RKINS.EXE = main 728706d9 instrumented (ags 0001-0373), stamp 39abbc4b5c34, build_dirty=0, sha256 5fc33941...; = the
  reviewed L2DINS. VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Fixture: RDMP's line (fine timing on, DOSAGS_TICKLOG=12500, TICKS.BIN) with DRIVE 6 ms and the calibrated values; the same
  pointing witness as RKM1..RKM4. Only after a calibration GATE PASS; first to drop.
- Information: (1) a second 486 sample of the two fixed-game-time stalls round RJ's RJMP found -- read the ticks at lc 9508
  (RJMP: 119.5 ms, undrawn, 112.6 ms outside every timed phase) and lc 11294 (RJMP: 201.5 ms), and whether the board reports a
  resume (not a partial) at each; (2) MS3's walking / click / GUI-redraw tick costs on ags 0373 (L2 on) against RJMP's on 0372.
  Displayed (fine timing on) is reported apart from RKM1..RKM4, never averaged with them.
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
