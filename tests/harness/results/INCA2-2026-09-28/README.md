# INCA2 -- 0320 same-binary ABBA cell 4 of 4 (INCA1 INCB1 INCB2 INCA2), round V (pre-registration, before any data)
- Registration: lab-s8 lab/mmd 6bc62599 lab-mmd/land-0320/README.md "COMPLETE ROUND V SPEC" + amendments e33f53be (silent IRQs read
  comparatively; per-cell 486 gate-bar line) and 141e8167 (scorer of record abba320.py at d3dc8239); nothing added to those rules.
- Arm: A = `--env DOSAGS_PCM_INCR=0`; the pcmcache line must read incr=0.
- Pins, identical in all four cells (the spec's flip rule: 0241/0242 flipped ON before staging, 5bec55aa): DOSAGS_STATEXISTS=1
  DOSAGS_PAKHANDLE=1 DOSAGS_PCM_ADOPT=0 DOSAGS_MIDI_MEM=1.
- Fixture: round R's S8R1 line -- run-hw trilbysnotes --startr 35, presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG
  (sound on, OPL3, default drain), SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, --no-fine-timing, drive-walk
  25 2 80, PGSB, RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Binary ("landed main at round-V staging"): main 5bec55aa, binary_sha12 d18d63368af6, build_dirty 0, sha256 8360f23da57ab80f...
- Scorer: python3 lab-mmd/land-0320/abba320.py d18d63368af6 <INCA1> <INCB1> <INCB2> <INCA2> (d3dc8239). M1 = the largest
  "DOS-PORT stall100 ... journey=0". FLIP ON iff both deltas <= -150 ms, drift |A1-A2| < 250 ms, B counters 0, B silent IRQs <= A's
  and none in a room load; KEEP OFF iff both deltas > -150 ms or a B counter nonzero; else NOT SEPARABLE. VOID rules as the spec.
- Prediction (reported, not a gate): both deltas in [-500, -250] ms (ADOPT pinned 0).
