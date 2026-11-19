# RJCAL -- DRIVE 6 rig calibration cell (gated) (written 2026-11-11; pre-registration, before any data)
- Binary: RJREL.EXE = main release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; = round RG's
  RGREL (R2 on by default; L1 / L2 off by default). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- DRIVE 6, DRIVE6_MODE=cal (drive-walk6.sh, one-call presses): 61 presses, ~152 s. A measurement prelude in room 1
  (11 presses, 4 s slots, every point clear of room 1's two live object regions): single x packets of 8 / 20 / 30 / 45 /
  60 / 88 counts; 60 counts as 4 slow vs 4 fast packets; 16 y counts as 1 vs 4 slow; one 200-count clip / carry probe.
  Then room 1: the top-right corner check (x 319) alternating with a DXL sweep 44..60; one EXIT press (top-left corner, x
  0) into room 2; room 2: DXA 66..81 carrying the DY sweep 8..21, alternating with DXB 39..51; 5 bottom-bound presses.
  First centres: the pointer model's defaults DY 15 (y 121), DXL 52 (x 60), DXA 75 (x 190, room 830), DXB 42 (x 289,
  room 929).
- Read with tests/harness/drive6-gate.sh. Checks and stop rules, verbatim from tests/harness/DRIVE6-RIG-CHECKS.md (84ca3445):
  G0 presses sent == planned; G1 no failed press; C1 every press walks (walks == presses, rooms exactly [1, 2], no GUI
  click, each press in its room, room-1 x >= 20, all y <= 142); C2 / C3 corners x 319 / 0; C10 (AMENDED) linearity over
  exactly the play path's sizes: each sweep's points of >= 15 counts (DXL 44..60, DXA 66..81, DXB 39..51, DY 15..21, all
  single packets) within 2 px of its line; the WHOLE measurement prelude (the single-packet sizes, the slow / fast
  probes, the y probe, the clip probe) and every sweep value under 15 counts are INFORMATION, with the reason (the play
  path sends one packet per move, all 15..127 counts); C9 each sweep's slope within 25% of the model; C8 repeatability
  within 2 px; C4-C7 each fitted value in its band (DY y 116..140, DXL x 48..72, DXA x 177..201, DXB x 276..300) and
  inside its swept range, each fitted on values >= 15 counts (a chosen value under 15 is raised to 15). No extrapolated value passes: inside the range ->
  PASS; outside the range but in band -> GATE RECENTRE (one re-run, RJCAL2, gated with --no-recentre); otherwise STOP.
  GATE PASS -> the values go to every MS3 cell of this power-on; GATE STOP or a second non-PASS -> no MS3 cell runs; the
  bridge pair still runs.
- Prediction (information; the gate is the rule): GATE PASS on RJCAL at the model's centres DY 15 / DXL 52 / DXA 75 /
  DXB 42, landing within 2 px of y 120 / x 60 / 190 / 289 (round RI measured exactly these, 0-1 px spread); the 200-count
  probe at x 75 (clip); the small-packet probes reading the per-packet loss (8 counts -> x 269; 4 x 4 y -> 106).
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
