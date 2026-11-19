# RQCAL -- DRIVE 6 full calibration (runs only on a calq miss) (written 2026-11-13; pre-registration, before any data)
- Binary: R0380.EXE = main e90a228b release (ags 0001-0380; 0380 sdlports-APPROVED), DOSAGS_RELEASE=1, sha256
  0e6637f41c3a2a72..., 8,670,423 B, stamp b66bd61cb1df, build_dirty=0 (two clean builds byte-identical; LOCK0380-2026-11-13).
  Staged from build/ws/roundRQ (expected.txt: r0380.exe, l308.exe, AGSSAVE.007); a mismatch stops the round before
  power-on; a manifest stamp other than b66bd61cb1df is STAMP-VOID. BLASTER.TXT "A220 I7 D3 P330 T3" (else STOP at the
  warm-up). 0377's bounded ring is unconditional (0379); memlog is gone (0378).
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440),
  as rounds RN / RO; plus `DIR C:\ /A` before and after the game (ROOTPRE.TXT / ROOTPOST.TXT) in every cell.
- Runs ONLY if RQCALQ's gate is not GATE PASS; otherwise not run (its dir keeps this README only). As ROCAL: read with
  `drive6-gate.sh RQCAL --no-recentre`; GATE PASS -> its values go to every ABBA cell; anything else -> no ABBA cell runs.
- Round RQ (operator 2026-11-13 via sdlports; diagnostic only): the heap lock-policy ABBA on MS3. WARMUPRQ, RQCALQ
  [-> RQCAL on a calq miss], RQO1 RQU1 RQP1 RQP2 RQU2 RQO2. One power-on, CAP_MIN 120. Budget line (as RO): need at RQCALQ
  1520 s (calq 760 + the full cal 760, counted up front); the ABBA's graded needs RQO1 4560 / RQU1 3800 / RQP1 3040 /
  RQP2 2280 / RQU2 1520 / RQO2 760 (counted from the ABBA alone). After the warm-up: 6080 s with the full cal, 5320
  without, vs 120 x 60 - warm-up 630 - 240 = 6330 s: with the full cal, a warm-up more than ~250 s over its 630 (or cells
  running long) drops RQO2 first, and the terms then read on the registered O1-only fallback baseline (RQO1 cell).
  DIAGNOSTIC ONLY: no cell is scored against a target or counts toward a proof pair. MS3 target: not yet set (operator).
- USB4VC firmware 0.5.109. Reported per cell: pkt_partial / pkt_timeout / mouse.dropped and ev_in == pkt_built; a partial
  voids an MS3 cell from that press (rule M0).
