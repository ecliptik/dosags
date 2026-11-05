# ADPB2 -- 0322 safety ABBA cell 3 of 4 (ADPA1 ADPB1 ADPB2 ADPA2), round W (pre-registration, before any data)
- Registration: lab-s8 lab/mmd 017050ef docs/lab/s8.md "0322 safety re-test, round W" (coordinator option (a)); nothing added.
- Arm: B = `--env DOSAGS_PCM_ADOPT=1`; the pcmcache line must read adopted>=1.
- Pins, identical in all four: DOSAGS_STATEXISTS=1 DOSAGS_PAKHANDLE=1 DOSAGS_MIDI_MEM=1 DOSAGS_PCM_INCR=0 (main's default at
  round-W staging: 0320 stayed OFF after round V's NOT SEPARABLE).
- Fixture: the standard S16 fixture (round U's $IOF) -- run-hw 5days --startr 3, presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG
  :ACSETUP.CFG (sound on, PGSB), SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, DOSAGS_TICKLOG=5200,
  --no-fine-timing, --collect TICKS.BIN, drive-walk 25 2 90, RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Binary ("landed main at round-W staging"): main d533b56d, binary_sha12 ef123dba0adf, build_dirty 0, sha256 235a5170b366fd8f...
- Scorer: lab-mmd/land-0322/abba322.py at lab/mmd c19cb451, first argument ef123dba0adf.
- FLIP ON: B's summed silent IRQs <= A's, none in a room load; B's late_writes, underruns, overwrites 0; whole-run drift |A1-A2|
  < 0.30. KEEP OFF: B's silent IRQs > A's, one in a room load, or a B counter nonzero. NOT SEPARABLE otherwise.
- VOID: stamp or dirty wrong; exit != 0; any room but 3; RUN.BAT ADOPT != the arm's value; adopted not 0 (A) / >= 1 (B); pins differ.
- Reported, not gated: stall100 and the sound10-tick stall (TICKS.BIN); expected direction B about 60 ms shorter (IO22: 66.4 ms).
