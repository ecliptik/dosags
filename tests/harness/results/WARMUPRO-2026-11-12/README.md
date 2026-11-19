# WARMUPRO -- rig warm-up (written 2026-11-12; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored. Checks: BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP; capture device present
  at the pre-flight; a capture STALE of any kind but "nolock" stops the round.
- The question: is ags 0377 the fix for the 486's room-2 freezes? Rounds RL / RM: the 486 freezes machine-wide (IRQ0
  unserviced) ~0.2 / ~0.65 / ~1.5 s in the room-2 stay, each at a DPMI physical-page commit (192 / 512 / 992 pages). The
  lab (move) named the owner: patch 0049's per-voice ring grows ~22 KB/s on a live SB with 2x reallocations. Round RN ran
  this ABBA and gave NO VERDICT by its letter: with the freezes gone, the wall-timed press 114 lands after the 12440 TAS
  exit, so both F cells logged 113 journeys for 114 presses (GATE PLAY-VOID; journeys != presses), which RN's terms did
  not read. Post-data (information, labelled in ROUNDRN-2026-11-12): F flat (-4..+9 ms), L 217-221 / 605-657 /
  1,426-1,490 ms. Round RO repeats the ABBA with the pairing rule registered before any data (operator 2026-11-12: "Keep
  12440, new rule"; the exit tick stays, so RO's cells compare directly with RL / RM / RN).
- Release relevance (information; sdlports): any long or looping PCM voice on a live SB grows ~22 KB/s on the v0.1 line,
  so 0377 is release-relevant; any v0.1.x is the operator's call. Before 0377 reaches a release, one harness audio check
  of the fixed default on a lockable mode is still owed (not in this round).
- Round RO (the verdict round for ags 0377): WARMUPRO, ROCALQ [-> ROCAL on a calq miss], ROF1 ROL1 ROL2 ROF2 (the ring
  ABBA), RODT (DPMITIM2, information), ROP1 (P9M1 on RNREL; first to drop). One power-on, cap 120 min. Budget line: need
  at ROCALQ 1520 s (calq 760 + the full cal 760, counted up front); the ABBA block's graded needs ROF1 3040 / ROL1 2280 /
  ROL2 1520 / ROF2 760 (counted from the ABBA alone, so it never waits on what follows); then RODT 900 and ROP1 760, each
  under its own need after the ABBA (CUT reset): ROP1 and then RODT are dropped before any ABBA arm is. Whole round after
  the warm-up 6220 s with the full cal, 5460 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with the
  full cal, a warm-up more than ~110 s over its 630 costs ROP1 (then RODT), not an arm. (Round RN, same shape: warm-up
  593 s from relay-on, no full cal, every cell ran, power off at 90 min.)
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
