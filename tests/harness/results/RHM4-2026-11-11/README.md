# RHM4 -- MS3 (moving fixture) on ags 0372's release, default config: the campaign baseline cell (written 2026-11-11; pre-registration, before any data)
- Binary: RHREL.EXE = main release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; = round RG's
  RGREL (R2 on by default; L1 / L2 off by default). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- MS3: DRIVE 6, DRIVE6_MODE=ms, the calibrated DRIVE6_DY / DXL / DXA / DXB from RHCAL (or RHCAL2); room 1 walks then the
  exit walk (fixture M's), room 2 alternates A (room x ~829) and B (~928) every ~1.2 s off the top-right corner; 114
  presses. Runs only after a calibration GATE PASS.
- Pointing witness (DRIVE6-RIG-CHECKS D1+, drive6-gate.sh --play): every press logs a walk target (walks == presses, no
  "Mouse click over GUI"); rooms exactly [1, 2] (no return to room 1); A targets room 817..841, B 916..940, y 116..140.
  A PLAY-VOID cell is VOID for the baseline (reported, not scored); two VOIDs stop the block. Reported, not a bar
  (DRIVE6-RIG-CHECKS D2): INPUT-LOG mouse.dropped; a dropped move VOIDs a cell only through the walk and landing checks.
- The MS3 baseline (the campaign's new measure): RHM1..RHM4, default config on this build. Reported: displayed = 1 -
  frames_skipped/ticks per cell, their mean and SD, the run-to-run spread (the noise any later MS3 A/B is judged
  against), skips per window (room 1 + exit, room 2), catchup and audio lines.
  Model figure, NOT a falsifiable prediction (LAB-MOVE section 5: est486b, error band validated on static fixtures
  only, not covering MS3): ~1,117-1,209 skips, ~83-84% displayed. A measured mean outside 71-89% is reported as the
  model being wrong for MS3, and LAB-MOVE's walking-tick cost is the first suspect.
  Scene rule (sdlports): MS3's displayed % is a different scene from the P9M1 line's; it is never reported in the same
  column or compared with P9M1 / earlier rounds' figures as if one measure. No target is set by this round.
- Round RH (operator 2026-11-11: the moving fixture MS3 -- LAB-MOVE addendum 3, lab-rb 600b90e8 / 7f1980bb -- is the
  campaign's new measure, its target set only after this baseline; 99% x2 on the P9M1 line is retired, not met; sdlports'
  shape: calibration first and gated, a P9M1 bridge pair, the MS3 baseline cells named): WARMUPRH, RHCAL [RHCAL2 only on
  a GATE RECENTRE], RHM1..RHM4, RHP1 RHP2, RHMP (first to drop). One power-on, cap 120 min. Budget line: need at RHCAL
  3800 s (CAL 760 + the MS3 block 3040); whole round after the warm-up 6100 s (760 + 3040 + 1520 + 780), 6860 s with
  RHCAL2, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with RHCAL2 the instrumented cell RHMP drops, by design.
  Cell length: MS3 and cal cells ~670-700 s on the rig, the same floor as a DRIVE 5 cell (DRIVE6-RIG-CHECKS.md).
  Harness: drive-walk6.sh / drive6-cal.py / drive6-gate.sh / cell-template-d6.sh on main (2432f136 + the gate helper).
