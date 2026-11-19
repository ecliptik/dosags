# RPFLOOR -- the round's idle floor (written 2026-11-13; pre-registration, before any data)
- After WARMUPRP, with the target at the post-cell screen (every run-hw cell ends with C:\VGACAP\MODE12: a 640x480 DOS
  screen, capture locked; sdlports: "the 640x480 idle floor measured in the same round"), 60 s of
  tests/harness/audio-sampler.sh (vcctrl level / spectrum, 1.5 s windows) into FLOOR.log. F = the median mean dBFS.
- A wedged reader (fewer than 20 numeric samples, or every sample the same value; the 8.3 round saw a constant -91.0) gets
  ONE `vcctrl audio release` + `acquire` and a second 60 s (FLOOR-2.log). Still unreadable, or F > -50 dBFS: STOP before
  any AQ cell (the level bar could not be read). Earlier floors: -67.6 (2026-09-22), -67.9 (SB4-FLOOR 2026-09-23).
- F is written to FLOOR-DB.txt and passed to tests/harness/aq-audio-bars.py for both AQ cells.
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
