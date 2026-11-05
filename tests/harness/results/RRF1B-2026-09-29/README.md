# RRF1B -- 0319 re-cut 2 re-test cell 4 of 4 (RRF1A RRF0A RRF0B RRF1B), round Z2 (pre-registration, before any data)
- Registration: lab-s8 lab/mmd 54f4ff73 lab-mmd/rp486/README.md "RE-TEST OF 0319 RE-CUT 2" (dated 2026-09-29, before any data);
  nothing added.
- Arm: F1 = DOSAGS_RP_FAST not set (0319 re-cut 2's fast path).
- Binary: lab-s8's AGSRPW2 (lab/mmd build/lab/AGSRPW2.EXE) staged as rpw2.exe, sha256
  51063c8f96182e6135bf4d8d818b7313225fb762589557195b822c5c3260cfe3, 8,675,201 B, stamp 514d0a6cb094 (build_dirty=1 expected) = main
  d533b56d + 0319 re-cut 2 (lab-mmd/patches/ags/0319-* at 6c599b0e) + the RT3 probe; hashed at source and after copy.
- Fixture: RP486's round W2 fixture exactly -- run-hw 5days --startr 3, --timeout 2400, --no-fine-timing,
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=1150, DOSAGS_RT_BENCH=@RTBENCH.TXT (sha256 05cab28e...),
  DOSAGS_RT_RAND=300,7, sound OFF cfg ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG, drive 0 (no clicks), PGSB, no RUNHW_MIN_WAIT_S.
- Scorer: lab-mmd/rp486/rp486b.py at lab/mmd 240dd83f: rp486b.py 514d0a6cb094 <RRF1A> <RRF0A> <RRF0B> <RRF1B>. VERDICT = rp486's
  registered rule unchanged: DELETE on identity failure or < 10% in either pair; LANDING GATES at >= 20% in both; REPORT otherwise.
- Reported predictions (docs/lab/s8.md 63e9b9ff): P-row0 F1 row 0 <= F0 row 0 in both pairs; P-label label_us <= 10 ms; P-mean saving
  >= 25% in both pairs. VOID rules as rp486 (stamp, exit, room 3, 339 rows, RUN.BAT arm, rpcache line, no audio device).
- Round Z2 = WARMUPZ2 (l308) + these four; outside the 2026-09-29 five-round approval (operator asked separately).
