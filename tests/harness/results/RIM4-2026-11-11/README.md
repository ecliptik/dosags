# RIM4 -- MS3 (moving fixture) on ags 0372's release, default config: the campaign baseline cell (written 2026-11-11; pre-registration, before any data)
- Binary: RIREL.EXE = main release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; = round RG's
  RGREL (R2 on by default; L1 / L2 off by default). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- MS3: DRIVE 6, DRIVE6_MODE=ms, the calibrated DRIVE6_DY / DXL / DXA / DXB from RICAL (or RICAL2); room 1 walks then the
  exit walk (fixture M's), room 2 alternates A (room x ~829) and B (~928) every ~1.2 s off the top-right corner; 114
  presses. Runs only after a calibration GATE PASS.
- Pointing witness (DRIVE6-RIG-CHECKS G0 / G1 / D1+, drive6-gate.sh --play): all 114 presses sent and ok, every press logs a walk target (walks == presses, no
  "Mouse click over GUI"); rooms exactly [1, 2] (no return to room 1); A targets room 817..841, B 916..940, y 116..140;
  A PLAY-VOID cell is VOID for the baseline (reported, not scored); two VOIDs stop the block. Reported, not a bar
  (DRIVE6-RIG-CHECKS D2): INPUT-LOG mouse.dropped; a dropped move VOIDs a cell only through the walk and landing checks.
- The MS3 baseline (the campaign's new measure): RIM1..RIM4, default config on this build. Reported: displayed = 1 -
  frames_skipped/ticks per cell, their mean and SD, the run-to-run spread (the noise any later MS3 A/B is judged
  against), skips per window (room 1 + exit, room 2), catchup and audio lines.
  Model figure, NOT a falsifiable prediction (LAB-MOVE section 5: est486b, error band validated on static fixtures
  only, not covering MS3): ~1,117-1,209 skips, ~83-84% displayed. A measured mean outside 71-89% is reported as the
  model being wrong for MS3, and LAB-MOVE's walking-tick cost is the first suspect.
  Scene rule (sdlports): MS3's displayed % is a different scene from the P9M1 line's; it is never reported in the same
  column or compared with P9M1 / earlier rounds' figures as if one measure. No target is set by this round.
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
