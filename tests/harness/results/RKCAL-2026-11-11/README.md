# RKCAL -- DRIVE 6 full calibration (runs only on a calq miss) (written 2026-11-11; pre-registration, before any data)
- Binary: RKREL.EXE = main 728706d9 release (ags 0001-0373), stamp 942ad0260d36, build_dirty=0, sha256 36473d61...; = the
  reviewed L2DREL (R2 on and L2 on by default; L1 off; the 0374 cap not in this build). VOID if the staged stamp differs.
  BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- Runs ONLY if RKCALQ's gate is not GATE PASS; otherwise not run (its dir keeps this README only).
- DRIVE 6, DRIVE6_MODE=cal (61 presses, ~152 s), as RJCAL: the measurement prelude (information), the corner checks, and the
  DXL / DXA / DXB / DY sweeps. Read with `drive6-gate.sh RKCAL --no-recentre`: G0, G1, C1, C2 / C3, C10 (each sweep's >= 15-count
  single packets within 2 px of its line), C9, C8 repeatability, C4-C7 (in band, inside the swept range, >= 15 counts). GATE
  PASS -> its values go to every MS3 cell; anything else (a RECENTRE included: no third cal this power-on) -> no MS3 cell runs;
  the bridge pair still runs. A press-path STOP (G0 / G1) is never answered mid-round.
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
