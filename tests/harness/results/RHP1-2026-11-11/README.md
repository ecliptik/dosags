# RHP1 -- MMD IN PLAY (P9M1 line, DRIVE 5) on ags 0372's release, default config: the bridge pair (written 2026-11-11; pre-registration, before any data)
- Binary: RHREL.EXE = main release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; = round RG's
  RGREL (R2 on by default; L1 / L2 off by default). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Fixture: P9M1's line verbatim (as RGA1 / RGA2: DRIVE 5 host clicks, AGSSAVE.007, TAS 12440, sound ON cfg). Witness:
  camera shows play (room 1 -> 2). Windows as ROUNDRD's rule (room 1 + entry 5480-8400, room 2 8400-9500, late).
- Purpose (sdlports): ties MS3's new line to every earlier round on the same day and build, and shows the day's drift.
  Information, not a campaign claim (P9M1 99% x2 is retired). Expected level: the same binary's default cells in rounds
  RF / RG read 98.81-98.94% (RE's 0370 build 98.97-99.06%); a pair outside 98.5-99.3% is reported as day drift.
- Round RH (operator 2026-11-11: the moving fixture MS3 -- LAB-MOVE addendum 3, lab-rb 600b90e8 / 7f1980bb -- is the
  campaign's new measure, its target set only after this baseline; 99% x2 on the P9M1 line is retired, not met; sdlports'
  shape: calibration first and gated, a P9M1 bridge pair, the MS3 baseline cells named): WARMUPRH, RHCAL [RHCAL2 only on
  a GATE RECENTRE], RHM1..RHM4, RHP1 RHP2, RHMP (first to drop). One power-on, cap 120 min. Budget line: need at RHCAL
  3800 s (CAL 760 + the MS3 block 3040); whole round after the warm-up 6100 s (760 + 3040 + 1520 + 780), 6860 s with
  RHCAL2, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with RHCAL2 the instrumented cell RHMP drops, by design.
  Cell length: MS3 and cal cells ~670-700 s on the rig, the same floor as a DRIVE 5 cell (DRIVE6-RIG-CHECKS.md).
  Harness: drive-walk6.sh / drive6-cal.py / drive6-gate.sh / cell-template-d6.sh on main (2432f136 + the gate helper).
- Timing note (sdlports): the bridge runs ~65-75 min after the warm-up, where earlier rounds ran their P9M1 cells first;
  this is stated beside its result in case the drift check reads off.
