# RJM4 -- MS3 (moving fixture) on ags 0372's release, default config: the campaign baseline cell (written 2026-11-11; pre-registration, before any data)
- Binary: RJREL.EXE = main release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; = round RG's
  RGREL (R2 on by default; L1 / L2 off by default). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- MS3: DRIVE 6, DRIVE6_MODE=ms, the calibrated DRIVE6_DY / DXL / DXA / DXB from RJCAL (or RJCAL2); room 1 walks then the
  exit walk (fixture M's), room 2 alternates A (room x ~829) and B (~928) every ~1.2 s off the top-right corner; 114
  presses. Runs only after a calibration GATE PASS.
- Pointing witness (DRIVE6-RIG-CHECKS G0 / G1 / D1+, drive6-gate.sh --play): all 114 presses sent and ok, every press logs a walk target (walks == presses, no
  "Mouse click over GUI"); rooms exactly [1, 2] (no return to room 1); A targets room 817..841, B 916..940, y 116..140;
  A PLAY-VOID cell is VOID for the baseline (reported, not scored); two VOIDs stop the block. Reported, not a bar
  (DRIVE6-RIG-CHECKS D2): INPUT-LOG mouse.dropped; a dropped move VOIDs a cell only through the walk and landing checks.
- The MS3 baseline (the campaign's new measure): RJM1..RJM4, default config on this build. Reported: displayed = 1 -
  frames_skipped/ticks per cell, their mean and SD, the run-to-run spread (the noise any later MS3 A/B is judged
  against), skips per window (room 1 + exit, room 2), catchup and audio lines.
  Model figure, NOT a falsifiable prediction (LAB-MOVE section 5: est486b, error band validated on static fixtures
  only, not covering MS3): ~1,117-1,209 skips, ~83-84% displayed. A measured mean outside 71-89% is reported as the
  model being wrong for MS3, and LAB-MOVE's walking-tick cost is the first suspect.
  Scene rule (sdlports): MS3's displayed % is a different scene from the P9M1 line's; it is never reported in the same
  column or compared with P9M1 / earlier rounds' figures as if one measure. No target is set by this round.
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
