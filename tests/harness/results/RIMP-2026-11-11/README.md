# RIMP -- MS3 on ags 0372's INSTRUMENTED build with TICKS: the 486's own walking / click / GUI tick costs (written 2026-11-11; pre-registration, before any data)
- Binary: RIINS.EXE = main instrumented (ags 0001-0372), stamp 01658435489c, build_dirty=0, sha256 234b5626...; = round
  RF's RFINS. VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Fixture: RDMP's line (fine timing on, DOSAGS_TICKLOG=12500, TICKS.BIN) with DRIVE 6 ms and the calibrated values; the
  same pointing witness as RIM1..RIM4 (a PLAY-VOID cell is reported, not read). Only after a calibration GATE PASS.
- Information (LAB-MOVE's largest unknown): from TICKS (docs/lab/rb-lab/ticks.py reader), the medians of ugo / scene /
  render / logic for (a) room-1 and room-2 walking ticks with no click, (b) click ticks, (c) the two GUI-redraw ticks
  after a click; and how many skips follow each click. LAB-MOVE's model: walking 24.1-24.5 ms, click route 60-122 ms, GUI
  redraw ~33 ms of draw. These figures recalibrate est486b for MS3; they are not scored. Displayed (fine timing on) is
  reported apart from RIM1..RIM4, never averaged with them.
- Round RI (round RH's registered shape, re-run: RH's calibration cell sent 1 press of 40 -- a vcctrl stdin defect,
  fixed -- and its one press showed the pointer model was wrong; the harness was rebuilt on a measured model and a
  one-call press, main 8be9d05f, sdlports-reviewed). The campaign context is unchanged: MS3 -- LAB-MOVE addendum 3,
  lab-rb 600b90e8 / 7f1980bb -- is the campaign's measure, its target set only after this baseline; P9M1's 99% x2 is
  retired, not met. WARMUPRI, RICAL [RICAL2 only on a GATE RECENTRE], RIM1..RIM4, RIP1 RIP2, RIMP (first to drop).
  One power-on, cap 120 min. Budget line: need at RICAL 3800 s (cal 760 + the MS3 block 3040); whole round after the
  warm-up 6100 s (760 + 3040 + 1520 + 780), 6860 s with RICAL2, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with
  RICAL2 the instrumented cell RIMP drops, by design. Cell length ~670-700 s (run-hw's floor; the cal cell's 61 presses
  end ~152 s after the first, ~12 s of game time before the TAS exit).
  Harness: drive-walk6.sh (DRIVE6_PRESS=one: vcctrl 9bad5fd `mouse press`, pace 0.05, dwell 0.2, every packet <= 127
  counts), drive6-pointer.py (the model: one move = one PS/2 packet capped at +-127 by the USB4VC board; 3.0 / 1.5 px
  per count in a 512x384 screen; MMD's frame at (96,92)), drive6-cal.py / drive6-gate.sh, cell-template-d6.sh.
  Press-path stop rule (sdlports): a cal STOP for press-path reasons (G0 short run, G1 failed press, the fast-probe
  merge) is never answered mid-round; any fallback to DRIVE6_PRESS=split is for a later round.
