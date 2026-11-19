# WARMUPRP -- rig warm-up (written 2026-11-13; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored (WARMUPRO's checks verbatim). BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP;
  capture device present at the pre-flight; a capture STALE of any kind but "nolock" stops the round.
- Round RP: the lockable-mode audio check owed before ags 0377 (the bounded mixer voice ring; the 486 room-2 freeze fix,
  round RO SUPPORTED) reaches a release (sdlports' terms, 2026-11-12, amended 2026-11-13). One power-on, CAP_MIN 60.
  Order: WARMUPRP -> RPFLOOR -> RPAQ1 -> RPAQ2. Driver build/ws/roundRP/driveRP.sh (from driveRO.sh), cell
  build/ws/roundRP/cellRP.sh (cellRO.sh verbatim: audio-sampler.sh + audio-rec.py run in every cell). Budget: warm-up
  ~630 s from relay-on (RO: 593-630), floor 60-130 s, RPAQ1 / RPAQ2 typical 780 s each (N7AQ's line) = ~2,320 s vs
  60 x 60 - 240 = 3,360 s; a cell that does not fit (ccell's typical-time rule) is dropped and reported, never cut short.
- Binary: the 0379 release, main be0d1d37, sha256 2191042b343cfd66..., binary_sha12 d5c8fe52808a (r0379.STAMP; a mismatch is
  STAMP-VOID), staged from build/ws/roundRP (expected.txt; a mismatch stops the round before power-on). Memlog is gone
  (0378), the legacy switch is gone (0379): the cells run the default, as a release would.
- Not in this round: the LOCK_MEMORY lever (lab study only; move). Its swap / free-page prediction (sdlports' (d)) belongs
  to the round whose binary carries the lever, not this one. MS3 target: not yet set (operator). Diagnostic and release
  check only; no cell counts toward any fps goal.
