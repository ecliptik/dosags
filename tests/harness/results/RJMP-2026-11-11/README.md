# RJMP -- MS3 on ags 0372's INSTRUMENTED build with TICKS: the 486's own walking / click / GUI tick costs (written 2026-11-11; pre-registration, before any data)
- Binary: RJINS.EXE = main instrumented (ags 0001-0372), stamp 01658435489c, build_dirty=0, sha256 234b5626...; = round
  RF's RFINS. VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Fixture: RDMP's line (fine timing on, DOSAGS_TICKLOG=12500, TICKS.BIN) with DRIVE 6 ms and the calibrated values; the
  same pointing witness as RJM1..RJM4 (a PLAY-VOID cell is reported, not read). Only after a calibration GATE PASS.
- Information (LAB-MOVE's largest unknown): from TICKS (docs/lab/rb-lab/ticks.py reader), the medians of ugo / scene /
  render / logic for (a) room-1 and room-2 walking ticks with no click, (b) click ticks, (c) the two GUI-redraw ticks
  after a click; and how many skips follow each click. LAB-MOVE's model: walking 24.1-24.5 ms, click route 60-122 ms, GUI
  redraw ~33 ms of draw. These figures recalibrate est486b for MS3; they are not scored. Displayed (fine timing on) is
  reported apart from RJM1..RJM4, never averaged with them.
- Round RJ (round RI's registered shape, re-run: RI's calibration stopped on C10 -- small-packet linearity, a part of
  the pointer path the play presses never use -- while every play-path quantity passed directly; the amended C10 and
  the small-packet model were written after RI's data and reviewed by sdlports, so RI's calibration is NOT re-read: RJ
  opens with a fresh full cal under the amended rules, registered here before power-on; the short re-check (calq) is for
  the round after, with RJ's passing cal as its reference). Campaign context unchanged: MS3 (LAB-MOVE addendum 3) is the
  campaign's measure, its target set only after this baseline; P9M1's 99% x2 is retired, not met. WARMUPRJ, RJCAL [RJCAL2
  only on a GATE RECENTRE], RJM1..RJM4, RJP1 RJP2, RJMP (first to drop). One power-on, cap 120 min. Budget line as RI:
  need at RJCAL 3800 s; whole round after the warm-up 6100 s, 6860 s with RJCAL2, vs 6330 s: with RJCAL2, RJMP drops.
  Harness (local main 84ca3445, sdlports-reviewed): drive-walk6.sh (one-call press, pace 0.05, dwell 0.2, every packet
  15..127 counts; FIRST-PRESS.json / FAILED-PRESS-<n>.json kept), drive6-pointer.py (one move = one PS/2 packet capped at
  +-127; 3.0 / 1.5 px per count; packets <= 11 counts lose counts upstream of INT 33h), drive6-cal.py / drive6-gate.sh.
  Press-path stop rule (sdlports): a cal STOP for press-path reasons (G0 / G1 / the fast-probe merge) is never answered
  mid-round; any fallback to DRIVE6_PRESS=split is for a later round.
