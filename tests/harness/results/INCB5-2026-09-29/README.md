# INCB5 -- 0320 confirmation block 3 cell 2 of 4 (INCA5 INCB5 INCB6 INCA6), round X2 (pre-registration, before any data)
- Registration: lab-s8 lab/mmd cee07b0f docs/lab/s8.md "0320 follow-up -- PRE-REGISTRATION" (2) + amendments f227b8b6 (CLICK within
  0.5 s before, interpolated time) and 7f0c43c9 (iii: cost thresholds for blocks 2-3 only); nothing added.
- Arm: B = `--env DOSAGS_PCM_INCR=1` (pcmcache line must read incr=1). Pins, all cells as round V: DOSAGS_STATEXISTS=1
  DOSAGS_PAKHANDLE=1 DOSAGS_PCM_ADOPT=0 DOSAGS_MIDI_MEM=1.
- Fixture: round V's, unchanged -- run-hw trilbysnotes --startr 35,
  presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1,
  DOSAGS_TAS_AUTO_EXIT_TICK=5000, --no-fine-timing, drive-walk 25 2 80, PGSB, RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Binary: round V's file, copied: main 5bec55aa, binary_sha12 d18d63368af6, build_dirty 0, sha256 8360f23da57ab80f...
- Scorer, pooled, run only after X and X2 are both done: python3 lab-mmd/land-0320/abba320c.py d18d63368af6 INCA1 INCB1 INCB2 INCA2
  INCA3 INCB3 INCB4 INCA4 INCA5 INCB5 INCB6 INCA6 (7f0c43c9). KEEP OFF: a B counter nonzero; a B silent IRQ in a room load; any
  SLICE-only B silent IRQ in INCB3-INCB6; in-play silent IRQ B vs A at one-sided Fisher p < 0.10; or >= 4 of the 6 pair deltas > -150
  ms. FLIP ON: otherwise, if all 6 deltas <= -150 ms and every drift < 250 ms. NOT SEPARABLE: anything else.
- Round X2 = WARMUPX2 (l308) + this block only; round X is separate (coordinator 2026-09-28). A re-date is its own commit before data.
