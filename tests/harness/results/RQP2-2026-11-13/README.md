# RQP2 -- MS3 on the 0380 release, heap lock policy arm P (written 2026-11-13; pre-registration, before any data)
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
- DRIVE 6, DRIVE6_MODE=ms, the calibrated values (RQCALQ / RQCAL).
- Arm: P (DOSAGS_HEAP_PREGROW_KB=6144), second P cell.
- Read by tests/harness/rq-steps.py (committed with this pre-registration; its docstring is the rule): `rq-steps.py cell`
  per cell (STEPS.txt), `rq-steps.py verdict` over every cell that ran (VERDICT.txt). Definitions (offset = press down_at
  minus journey t_ms, ms3-pairing.py's load(); presses 1-based):
  pre = median offset of presses 6-15; S17 = offset(17) - pre (the press-17 step: clock lost across the room-2 load);
  S18 = offset(18) - offset(17) (the press-18 step: the 192-page commit at room-2 entry +43..+81 ticks);
  L2 = room-2 load_end - load_begin t_ms (STDOUT DOSAGS_XT; the load as the game clock counted it);
  W17 = L2 + S17 (the room-2 entry's wall cost, counted + lost); j1 = journey 1's t_ms (information).
- Motivation (read before RQ, from committed RO / RN records; sdlports verified the S17 / S18 table independently): on 0377
  the press-17 step is bimodal (S17 +194..+386) but trades against L2 (1,713..1,876 game ms); the sum W17 is tight:
  ROF1 1714 + 386 = 2100, ROF2 1872 + 212 = 2084, RNF1 1876 + 194 = 2070, RNF2 1760 + 354 = 2114 (legacy cells ROL1 2122, ROL2 2077, RNL1 2085, RNL2 2084).
  S18 on 0377: ROF1 +163, ROF2 +161, RNF1 +151, RNF2 +155 (rq-steps.py's own read of those records; legacy +168..+191).
  So W17 is the reading for a saved commit, not S17: a lever that only moves the commit's time from lost clock to counted
  clock lowers S17 and raises L2 with W17 unchanged.
- VALID cell: the arm witness (RUNMANI "DOS-PORT heappolicy_exit": O unlock=0 pregrow_kb=0 flags 0x1080->0x1080; U unlock=1
  pregrow_kb=0 flags 0x1080->0x80; P unlock=0 pregrow_kb=6144 grown=1 flags kept), RUNMANIFEST exit_code=0 and "ENGINE HAS
  SHUTDOWN", the pairing PAIR-OK or PAIR-OK-114LATE (ms3-pairing.py), audio underruns = overwrites = 0, the room-2 load
  lines present; plus the driver's stamp (b66bd61cb1df) and BLASTER checks. A VOID cell is reported and read by no term.
- P cover (sdlports): a P cell's heappolicy_exit free_pages must be within 16 pages of free_at_hook's post value (6,144 KB
  covered MS3's growth after the hook; lab: 1,344 pages grown against 1,536 pre-grown). Outside that it reads "pre-grow
  exceeded": information, not a P reading.
- OFF baseline B: both in-round O cells if both are valid. If exactly one is valid (e.g. RQO2 dropped on time), B = that
  cell + ROF1 / ROF2 / RNF1 / RNF2 (the 0377 fixed cells; NB they ran with DOSAGS_MEMLOG=1, an extra difference -- hence the
  in-round O is preferred). No valid O cell: the S18 and W17 terms are NOT READ.
- Terms (resolution +-30 ms):
  S18, per arm X in {U, P}: SUPPORTED if X has >= 2 valid cells (P: covered), each S18 <= 60, and every B cell's
    S18 >= 120; FALSIFIED if any such X cell's S18 >= 120; else INCONCLUSIVE; NOT READ with < 2 such cells.
  W17, PREGROW: SUPPORTED if >= 2 valid covered P cells, each W17 < min(B W17) - 60; FALSIFIED if any such cell's
    W17 >= min(B W17) - 30; else INCONCLUSIVE.
  W17 / S17 / L2, UNLOCK: information. Prediction (stated, not a bar): S17 down, L2 up, W17 within +-60 of B's median
    (lazy first-touch commits still cost per page; RODT).
  STOP IN A U CELL (sdlports): the driver labels it "STOP IN U CELL (UNLOCK FAILED unless attributed to the rig)" and the
    round stops there with NO recovery cycle (any power cycle goes to the operator through sdlports). Attribution, read
    from the cell's records after the round:
    - UNLOCK FAILED if the game was in play at the stop: AGS had started per STDOUT.TXT / RUNMANI.LOG (a timeout or hang
      in play -- e.g. a page fault in an ISR; the ISR audit, lab-rb c8af8810, was static only), or the camera or capture
      frame shows the game or a frozen game screen.
    - A RIG STOP if the stop came outside AGS: before launch (staging, a run-hw refusal, a capture or lock failure), or at
      the FTP collect / return reboot (e.g. the post-FTP keyboard hang) with the game's clean shutdown on record (RUNMANIFEST
      exit_code=0 and "ENGINE HAS SHUTDOWN"). A rig STOP says nothing about UNLOCK; the U arm is then NOT READ this round.
  UNLOCK FAILED also if a U cell ends without a clean exit while the round continues (STEPS valid=no, "no clean exit";
    the driver labels it "UNLOCK FAILED (a U cell without a clean exit)").
  (d) PAGEABILITY (U cells): FALSIFIED if any U cell's heappolicy_exit free_pages < 512. CWSDPMI.SWP: CWSDPMI deletes its
    swap file when it exits (round RM, WARMUPRM's `DIR C:\ /A`: no CWSDPMI.SWP at rest, 254,771,200 bytes free), so the
    before / after DIR shows only that no swap file is left behind (expected: none in every arm; the O cells are the
    control); it cannot see paging during a run. Information beside it, every cell: the largest sustained +offset shift
    over presses 23-108 outside the room-2 stay brackets (33-36 / 52-54 / 90-95), which a paging stall would raise.
- PREGROW's startup cost (sdlports): the heappolicy hook_us (uclock: blind to lost ticks, a lower bound) and j1 against the
  O cells' j1 (press 1 is wall-timed from the lock; a clock-stopped commit at the hook shows as fewer game ms at press 1).
  Information. Prediction: ~1.5-2 s (RODT c(K) ~1.0-1.2 ms/page x 1,552 pages).
- Open item (sdlports): if UNLOCK is ever proposed as the DEFAULT, a real in-run pageability witness is owed first (an
  engine-side sample of physical free pages / paging during play); this round's exit free_pages and the shift readings
  suffice only for a diagnostic arm.
- Simulation (before any data; scratch copies of RO / RN records with appended heappolicy_exit lines): unchanged records
  read S18 / W17 FALSIFIED for both arms (as they must); the O1-only fallback reads B = RQO1 + the four F cells; a synthetic
  P pair 300 ms faster at press 17 and 150 ms at press 18 reads S18 and W17 PREGROW SUPPORTED; a P cell 292 pages short of
  cover is excluded; a U exit at 400 free pages reads (d) FALSIFIED; wrong arm witnesses void the cell.
- Round RQ (operator 2026-11-13 via sdlports; diagnostic only): the heap lock-policy ABBA on MS3. WARMUPRQ, RQCALQ
  [-> RQCAL on a calq miss], RQO1 RQU1 RQP1 RQP2 RQU2 RQO2. One power-on, CAP_MIN 120. Budget line (as RO): need at RQCALQ
  1520 s (calq 760 + the full cal 760, counted up front); the ABBA's graded needs RQO1 4560 / RQU1 3800 / RQP1 3040 /
  RQP2 2280 / RQU2 1520 / RQO2 760 (counted from the ABBA alone). After the warm-up: 6080 s with the full cal, 5320
  without, vs 120 x 60 - warm-up 630 - 240 = 6330 s: with the full cal, a warm-up more than ~250 s over its 630 (or cells
  running long) drops RQO2 first, and the terms then read on the registered O1-only fallback baseline (RQO1 cell).
  DIAGNOSTIC ONLY: no cell is scored against a target or counts toward a proof pair. MS3 target: not yet set (operator).
- USB4VC firmware 0.5.109. Reported per cell: pkt_partial / pkt_timeout / mouse.dropped and ev_in == pkt_built; a partial
  voids an MS3 cell from that press (rule M0).
