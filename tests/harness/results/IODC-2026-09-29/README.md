# IODC -- ags 0245/0246 IO arm 3 of 6 (IOB0 IODS IODC IORD IOBB IOB1), round Y (pre-registration, before any data)
- Registration: lab/metric 167e2a91 tests/harness/results/S16-IOARMS2-HW-PREREG/README.md (rules there, nothing added); scorer
  tests/harness/lab-io2-hw.py --sha labUSY0 --witness-clean <tags> (ee0de7b0).
- Arm (DOSAGS_-prefixed): DIRCACHE=1 READDIRECT=0. Pins, all six cells (main's defaults): STATEXISTS=1 PAKHANDLE=1 MIDI_MEM=1
  PCM_ADOPT=0 PCM_INCR=0.
- Fixture: round U's S16 cell, contiguous, env only -- run-hw 5days --startr 3,
  presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1,
  DOSAGS_TAS_AUTO_EXIT_TICK=5000, DOSAGS_TICKLOG=5200, --collect TICKS.BIN, --no-fine-timing, drive-walk 25 2 90, PGSB,
  RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Binary: probe labUSY0 (a label, not a hex stamp) = main d533b56d + usprobe-LAB-ONLY.diff, 8,658,301 B, sha256 3d4f1c1d54fe7093...
  checked before power-on and after collection; RUNMANI binary_sha12 must read labUSY0.
- Registered: GATE IODS mode=1 shadow=1 compared>0 mismatches=0; 0245 FALSIFIED if open(OFF) - open(IODC) < 3 ms; 0246 FALSIFIED if
  summed saving < 25% of summed midpoints; VOID: OFF-OFF open drift > 10 ms, pins differ/unset, or a cell invalid; silent IRQs
  comparative ("audio clean" iff <= max(IOB0, IOB1), none in a room load).
- Round Y = WARMUPY (l308) + these six; WB S8 -> round Z (coordinator 2026-09-28); round U comparisons: information only.
