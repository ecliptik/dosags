# IDA5 -- 0320 candidacy-2 decisive test, block 3 of 3 (IDA5 IDD5 IDD6 IDA6), round ID3 (pre-registration, before any data)
- Registration: lab-s8 lab/mmd 3804a35d "CANDIDACY 2" (land-0320/README.md) + dba9d4bd (post-0319 binary base); nothing added.
- Arm: A = `--env DOSAGS_PCM_INCR=0`. Pins in all 12: DOSAGS_STATEXISTS=1 DOSAGS_PAKHANDLE=1 DOSAGS_PCM_ADOPT=0 DOSAGS_MIDI_MEM=1.
- Fixture: round V's S8 line literally -- run-hw trilbysnotes --startr 35, --timeout 1800, --no-fine-timing,
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG, drive-walk 25 2 80,
  PGSB, RUNHW_MIN_WAIT_S=270.
- Binary: main b7ac6c46 + lab 0323 (patch sha256 e7c4b61d...), built via make patches in a scratch clone that reproduces main
  3074cd9ce099 exactly: build_dirty 0, stamp f17997f06baa, sha256 b0207e50d61da7230ba8b24a961f8deba7fc69e6ea1582c59ef5ac755902d8c0,
  8,667,516 B.
- Scorer (pooled, only after ID1 + ID2 + ID3): lab-mmd/land-0320/abba320d.py at 8ba5b21c: abba320d.py f17997f06baa IDA1 IDD1 IDD2 IDA2
  IDA3 IDD3 IDD4 IDA4 IDA5 IDD5 IDD6 IDA6. KEEP OFF: a D counter nonzero; a D silent IRQ in a room load; any SLICE-ONLY D silent IRQ;
  in-play silent-IRQ cells D vs A at one-sided Fisher p < 0.10; or 4+ of 6 pair deltas > -150 ms. FLIP ON: otherwise, if all 6 deltas
  <= -150 ms and every drift < 250 ms. NOT SEPARABLE otherwise.
- Round ID3: warm-up + this block (cell 1 of 4); waits for the operator (system OFF); re-dated before any data.
