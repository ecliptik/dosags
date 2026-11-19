# WARMUPRN -- rig warm-up (written 2026-11-12; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored. Checks: BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP; capture device present
  at the pre-flight; a capture STALE of any kind but "nolock" stops the round.
- The question: rounds RL / RM found the 486 freezing machine-wide (IRQ0 unserviced) ~0.2 / ~0.65 / ~1.5 s in the room-2
  stay, each at a DPMI physical-page commit (192 / 512 / 992 pages, the same with and without CWSDPMI's swap). The lab
  (move, lab-rb move-lab/rj/rm LAB-RING.txt / LAB-RING377.txt) named the owner: patch 0049's per-voice ring drops its
  consumed prefix only when fully drained, so with a live SB the looping room-2 ambient voice (sound 96, channel 1) grows
  ~22 KB/s with 2x reallocations (0.75 / 2 / 3.9 MB), and each reallocation's copy commits the new block at once. Under
  test: ags 0377 (bounded ring) against its own legacy switch, same binary, same line.
- Release relevance (information; sdlports): the leak is not MMD-only. Any long or looping PCM voice on a live SB grows
  ~22 KB/s on the v0.1 line (~20 MB in a 15-minute stay; the ratchet's live-SB 5 Days unit compacts too), so 0377 is a
  release-relevant fix; any v0.1.x is the operator's call. Before 0377 reaches a release, one harness audio check of the
  fixed default on a lockable mode (an existing 640x480 audio cell against its reference) is owed: not in this round
  (budget), the next one.
- Round RN (the fix round for ags 0377): WARMUPRN, RNCALQ [-> RNCAL on a calq miss], RNF1 RNL1 RNL2 RNF2 (the ring ABBA),
  RNDT (DPMITIME, information), RNP1 (P9M1 on RNREL; first to drop). One power-on, cap 120 min. Budget line: need at
  RNCALQ 1520 s (calq 760 + the full cal 760, counted up front); the ABBA block's graded needs RNF1 3040 / RNL1 2280 /
  RNL2 1520 / RNF2 760 (counted from the ABBA alone, so it never waits on what follows); then RNDT 900 and RNP1 760, each
  under its own need after the ABBA (CUT reset): RNP1 and then RNDT are dropped before any ABBA arm is. Whole round after
  the warm-up 6220 s with the full cal, 5460 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with the
  full cal, a warm-up more than ~110 s over its 630 costs RNP1 (then RNDT), not an arm.
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
