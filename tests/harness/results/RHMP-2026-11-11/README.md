# RHMP -- MS3 on ags 0372's INSTRUMENTED build with TICKS: the 486's own walking / click / GUI tick costs (written 2026-11-11; pre-registration, before any data)
- Binary: RHINS.EXE = main instrumented (ags 0001-0372), stamp 01658435489c, build_dirty=0, sha256 234b5626...; = round
  RF's RFINS. VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Fixture: RDMP's line (fine timing on, DOSAGS_TICKLOG=12500, TICKS.BIN) with DRIVE 6 ms and the calibrated values; the
  same pointing witness as RHM1..RHM4 (a PLAY-VOID cell is reported, not read). Only after a calibration GATE PASS.
- Information (LAB-MOVE's largest unknown): from TICKS (docs/lab/rb-lab/ticks.py reader), the medians of ugo / scene /
  render / logic for (a) room-1 and room-2 walking ticks with no click, (b) click ticks, (c) the two GUI-redraw ticks
  after a click; and how many skips follow each click. LAB-MOVE's model: walking 24.1-24.5 ms, click route 60-122 ms, GUI
  redraw ~33 ms of draw. These figures recalibrate est486b for MS3; they are not scored. Displayed (fine timing on) is
  reported apart from RHM1..RHM4, never averaged with them.
- Round RH (operator 2026-11-11: the moving fixture MS3 -- LAB-MOVE addendum 3, lab-rb 600b90e8 / 7f1980bb -- is the
  campaign's new measure, its target set only after this baseline; 99% x2 on the P9M1 line is retired, not met; sdlports'
  shape: calibration first and gated, a P9M1 bridge pair, the MS3 baseline cells named): WARMUPRH, RHCAL [RHCAL2 only on
  a GATE RECENTRE], RHM1..RHM4, RHP1 RHP2, RHMP (first to drop). One power-on, cap 120 min. Budget line: need at RHCAL
  3800 s (CAL 760 + the MS3 block 3040); whole round after the warm-up 6100 s (760 + 3040 + 1520 + 780), 6860 s with
  RHCAL2, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with RHCAL2 the instrumented cell RHMP drops, by design.
  Cell length: MS3 and cal cells ~670-700 s on the rig, the same floor as a DRIVE 5 cell (DRIVE6-RIG-CHECKS.md).
  Harness: drive-walk6.sh / drive6-cal.py / drive6-gate.sh / cell-template-d6.sh on main (2432f136 + the gate helper).
