# RICAL2 -- DRIVE 6 rig calibration cell (gated) (written 2026-11-11; pre-registration, before any data)
- Binary: RIREL.EXE = main release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; = round RG's
  RGREL (R2 on by default; L1 / L2 off by default). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- Runs ONLY if RICAL's gate says GATE RECENTRE, centred on the values that line names; otherwise not run (its dir
  stays with this README only).
- DRIVE 6, DRIVE6_MODE=cal (drive-walk6.sh, one-call presses): 61 presses, ~152 s. A measurement prelude in room 1
  (11 presses, 4 s slots, every point clear of room 1's two live object regions): single x packets of 8 / 20 / 30 / 45 /
  60 / 88 counts; 60 counts as 4 slow vs 4 fast packets; 16 y counts as 1 vs 4 slow; one 200-count clip / carry probe.
  Then room 1: the top-right corner check (x 319) alternating with a DXL sweep 44..60; one EXIT press (top-left corner, x
  0) into room 2; room 2: DXA 66..81 carrying the DY sweep 8..21, alternating with DXB 39..51; 5 bottom-bound presses.
  First centres: the pointer model's defaults DY 15 (y 121), DXL 52 (x 60), DXA 75 (x 190, room 830), DXB 42 (x 289,
  room 929).
- Read with tests/harness/drive6-gate.sh. Checks and stop rules, verbatim from tests/harness/DRIVE6-RIG-CHECKS.md: G0
  presses sent == planned (else STOP); G1 no failed press (else STOP); C1 every press walks (walks == presses, rooms
  exactly [1, 2], no GUI click, each press in its room, room-1 x >= 20, all y <= 142); C2 / C3 corners x 319 / 0; C10 the
  prelude's single-packet sizes on one line within 2 px with a slope within 25% of the model, slow == fast within 2 px
  (else STOP: a size- or speed-dependent gain transfers to no line fit); C9 each sweep's slope within 25% of the model;
  C8 repeats and every point within 2 px of its line; C4-C7 each fitted value in its band (DY y 116..140, DXL x 48..72,
  DXA x 177..201, DXB x 276..300) AND inside its swept range. No extrapolated value passes: inside the range -> PASS;
  outside the range but in band -> GATE RECENTRE (one re-run, RICAL2, gated with --no-recentre); otherwise STOP.
  Clip vs carry is reported, not a bar. GATE PASS -> the values go to every MS3 cell of this power-on; GATE STOP or a
  second non-PASS -> no MS3 cell runs; the bridge pair still runs.
- Prediction (information; the gate is the rule): GATE PASS on RICAL with the model's centres: x 3.0 and y 1.5 px per
  count on one line, slow == fast, the 200-count probe at x 75 (clip), landings within 2 px of y 121 / x 60 / 190 / 289.
  The model fits 229 of 232 DRIVE 5 runs click by click and RH's one press (predicted (319, 40-41), logged (319, 39)).
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
