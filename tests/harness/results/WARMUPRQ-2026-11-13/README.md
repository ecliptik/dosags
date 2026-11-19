# WARMUPRQ -- rig warm-up (written 2026-11-13; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored (WARMUPRO's checks verbatim). BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP;
  capture device present at the pre-flight; a capture STALE of any kind but "nolock" stops the round.
- Binary: R0380.EXE = main e90a228b release (ags 0001-0380; 0380 sdlports-APPROVED), DOSAGS_RELEASE=1, sha256
  0e6637f41c3a2a72..., 8,670,423 B, stamp b66bd61cb1df, build_dirty=0 (two clean builds byte-identical; LOCK0380-2026-11-13).
  Staged from build/ws/roundRQ (expected.txt: r0380.exe, l308.exe, AGSSAVE.007); a mismatch stops the round before
  power-on; a manifest stamp other than b66bd61cb1df is STAMP-VOID. BLASTER.TXT "A220 I7 D3 P330 T3" (else STOP at the
  warm-up). 0377's bounded ring is unconditional (0379); memlog is gone (0378).
- Round RQ (operator 2026-11-13 via sdlports; diagnostic only): the heap lock-policy ABBA on MS3. WARMUPRQ, RQCALQ
  [-> RQCAL on a calq miss], RQO1 RQU1 RQP1 RQP2 RQU2 RQO2. One power-on, CAP_MIN 120. Budget line (as RO): need at RQCALQ
  1520 s (calq 760 + the full cal 760, counted up front); the ABBA's graded needs RQO1 4560 / RQU1 3800 / RQP1 3040 /
  RQP2 2280 / RQU2 1520 / RQO2 760 (counted from the ABBA alone). After the warm-up: 6080 s with the full cal, 5320
  without, vs 120 x 60 - warm-up 630 - 240 = 6330 s: with the full cal, a warm-up more than ~250 s over its 630 (or cells
  running long) drops RQO2 first, and the terms then read on the registered O1-only fallback baseline (RQO1 cell).
  DIAGNOSTIC ONLY: no cell is scored against a target or counts toward a proof pair. MS3 target: not yet set (operator).
- USB4VC firmware 0.5.109. Reported per cell: pkt_partial / pkt_timeout / mouse.dropped and ev_in == pkt_built; a partial
  voids an MS3 cell from that press (rule M0).
