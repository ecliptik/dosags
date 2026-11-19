# RHCAL2 -- DRIVE 6 rig calibration cell (gated) (written 2026-11-11; pre-registration, before any data)
- Binary: RHREL.EXE = main release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; = round RG's
  RGREL (R2 on by default; L1 / L2 off by default). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- Runs ONLY if RHCAL's gate says GATE RECENTRE, centred on the values that line names; otherwise not run (its dir
  stays with this README only).
- DRIVE 6, DRIVE6_MODE=cal (drive-walk6.sh): 40 presses, ~105 s. Room 1: 3 repeats of the corner check, DXL 36/40/44
  interleaved with DY 84/88/92; one EXIT press (the home clamp) into room 2; room 2: DXA 83/87/91 alternating with DXB
  19/21/23, 3 repeats (A / B are calibrated in room 2, where MS3 clicks them). First centres: the log-derived defaults
  DY 88, DXL 40, DXA 87, DXB 21 (be61dea0).
- Read with tests/harness/drive6-gate.sh (drive6-cal.py over STDOUT.TXT's MoveCharacter targets and DRIVE-WALK.LOG).
  Checks and stop rules, verbatim from tests/harness/DRIVE6-RIG-CHECKS.md: C1 every press walks (walks == 40, no GUI
  click, rooms exactly [1, 2], each press in its room); C2 corner x == 319 on all 3; C3 slam x == 319 on the DY presses,
  EXIT x == 0; C4 DY median y 116..140 (target 128); C5 DXL x 48..72 (60); C6 DXA screen x 177..201 (189; room 817..841);
  C7 DXB screen x 276..300 (288; room 916..940); C8 each value's 3-repeat spread <= 2 px.
  GATE PASS -> the chosen values go to every MS3 cell of this power-on. GATE RECENTRE (only C4-C7 at a sweep edge; C1-C3
  and C8 pass) -> one re-run, RHCAL2. GATE STOP, or a second non-PASS -> no MS3 cell runs; the bridge pair still runs.
- Prediction (information; the gate is the rule): GATE PASS on RHCAL with the default centres, landing near y 125-130,
  x ~60, room ~829 / ~928, 0 px spread (DRIVE 5's identical moves logged identical targets on three days).
- Round RH (operator 2026-11-11: the moving fixture MS3 -- LAB-MOVE addendum 3, lab-rb 600b90e8 / 7f1980bb -- is the
  campaign's new measure, its target set only after this baseline; 99% x2 on the P9M1 line is retired, not met; sdlports'
  shape: calibration first and gated, a P9M1 bridge pair, the MS3 baseline cells named): WARMUPRH, RHCAL [RHCAL2 only on
  a GATE RECENTRE], RHM1..RHM4, RHP1 RHP2, RHMP (first to drop). One power-on, cap 120 min. Budget line: need at RHCAL
  3800 s (CAL 760 + the MS3 block 3040); whole round after the warm-up 6100 s (760 + 3040 + 1520 + 780), 6860 s with
  RHCAL2, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with RHCAL2 the instrumented cell RHMP drops, by design.
  Cell length: MS3 and cal cells ~670-700 s on the rig, the same floor as a DRIVE 5 cell (DRIVE6-RIG-CHECKS.md).
  Harness: drive-walk6.sh / drive6-cal.py / drive6-gate.sh / cell-template-d6.sh on main (2432f136 + the gate helper).
