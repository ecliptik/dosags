# RNCAL -- DRIVE 6 full calibration (runs only on a calq miss) (written 2026-11-12; pre-registration, before any data)
- Binary: RNREL.EXE = main 987ddce1 release (ags 0001-0373 + 0376 + 0377; sdlports-reviewed), stamp 93df50d751a8, build_dirty=0,
  sha256 ce8d275f..., +796 B over round RM's 2725928f2e37. 0377 bounds the mixer's per-voice ring (patch 0049's Voice::ring:
  the consumed prefix is dropped once it reaches 64 KB) and is ON by default; its TEMPORARY DOSAGS_RING_LEGACY=1 switch
  restores the old unbounded growth (removal owed after this round, with 0376). VOID if the staged stamp differs.
  BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- Runs ONLY if RNCALQ's gate is not GATE PASS; otherwise not run (its dir keeps this README only). As RLCAL: read with
  `drive6-gate.sh RNCAL --no-recentre`; GATE PASS -> its values go to every ABBA cell; anything else -> no ABBA cell runs.
- USB4VC firmware 0.5.109 (as rounds RL / RM). Reported per cell: pkt_partial / pkt_timeout / mouse.dropped and ev_in ==
  pkt_built; a partial voids an MS3 cell from that press (rule M0).
- Round RN (the fix round for ags 0377): WARMUPRN, RNCALQ [-> RNCAL on a calq miss], RNF1 RNL1 RNL2 RNF2 (the ring ABBA),
  RNDT (DPMITIME, information), RNP1 (P9M1 on RNREL; first to drop). One power-on, cap 120 min. Budget line: need at
  RNCALQ 1520 s (calq 760 + the full cal 760, counted up front); the ABBA block's graded needs RNF1 3040 / RNL1 2280 /
  RNL2 1520 / RNF2 760 (counted from the ABBA alone, so it never waits on what follows); then RNDT 900 and RNP1 760, each
  under its own need after the ABBA (CUT reset): RNP1 and then RNDT are dropped before any ABBA arm is. Whole round after
  the warm-up 6220 s with the full cal, 5460 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with the
  full cal, a warm-up more than ~110 s over its 630 costs RNP1 (then RNDT), not an arm.
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
