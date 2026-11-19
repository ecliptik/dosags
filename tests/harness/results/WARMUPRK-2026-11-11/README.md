# WARMUPRK -- rig warm-up (and the powered check of USB4VC 0.5.108) (written 2026-11-11; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored. Checks: BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP; capture device present
  at the pre-flight; a capture STALE of any kind but "nolock" stops the round. DIRLIST.TXT: a read-only listing of C:\DOSAGS.
  The cell types RUN.BAT through the rig's keyboard on the new firmware: a typing failure (the cell not running) stops the round.
- USB4VC firmware 0.5.108 (flashed 2026-11-11 22:36Z by vcctrl, operator's OK: an interrupted PS/2 packet is resumed, never
  abandoned; +-127 summing unchanged; counters reset at the flash). Firmware verdict for this round (sdlports), from each DRIVE 6
  cell's INPUT-LOG.jsonl mouse.dropped rows (pkt_partial) and vcctrl's per-cell report of the board's "resume" counter page
  (pkt_resumed, partial_waits, inhibit_retry, abandon_budget, max_wait_ms): PASS if pkt_partial is 0 in every in-play window
  AND pkt_resumed / partial_waits rise within +-5 s of the known stall times (~+132 / ~+178 s after each MS3 cell's lock);
  FAIL (falsified) if any pkt_partial > 0 (rule M0 then voids that cell); information only, not a fix claim, if pkt_resumed
  stays 0 while pkt_partial is 0 (no stall reached the board). vcctrl's powered check of 0.5.108 (keyboard typing, LEDs, a few
  clicks at a DOS prompt) rides on WARMUPRK and RKCALQ: a keyboard or click failure there stops the round.
- Capture stick: on probation (back on the Pi's usb1-2 since 22:38:11Z after the operator's reseat; it failed on this port
  before). Pre-flight video_state / camera_state before relay-on. A capture drop mid-round does not stop the round on its own:
  the camera is the play witness (the stick never locks MMD's mode anyway) and the game's own log is the pointing witness.
- Round RK (the hardware test of USB4VC 0.5.108 and the MS3 baseline, first round on ags 0373; sdlports' shape): WARMUPRK,
  RKCALQ (the short re-check against round RJ's passing full cal RJCAL) [-> RKCAL, the full cal, on any calq miss],
  RKM1..RKM4 (MS3), RKP1 RKP2 (P9M1 bridge), RKMP (MS3 instrumented, TICKS; first to drop). One power-on, cap 120 min.
  Budget line: need at RKCALQ 4560 s (calq 760 + the full cal 760, counted up front + the MS3 block 3040); whole round after
  the warm-up 6100 s without the full cal (760 + 3040 + 1520 + 780), 6860 s with it, vs CAP_MIN 120 x 60 - warm-up 630 - 240
  = 6330 s: if the full cal runs, RKMP drops, by design. Harness: local main 5d3bfebe (drive-walk6.sh one-call presses;
  drive6-cal.py / drive6-gate.sh with C10 on >= 15-count packets, calq's drift report and NEXT-FULL-CAL flag, and rule M0:
  an MS3 cell is VOID from the press whose call meets a board pkt_partial). Campaign context: MS3 is the campaign's measure,
  its target set only after a baseline exists; P9M1's 99% x2 is retired, not met.
