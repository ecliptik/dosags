# IO22 -- S16-IOARMS-HW cell 5 of 6 (IOA0 IOES IO41 IO42 IO22 IOA1, contiguous), round U (pre-registration, before any data)
- Registration: lab-metric lab/metric 1dbb648f S16-IOARMS-HW-PREREG/README.md + amendments dce69329 (env per arm, IO22 repeat)
  and 62dcbf82 (host binary); nothing added to those rules. Scorer: tests/harness/lab-io-hw.py --sha 80463ed30b91 --witness-clean <tags>.
- Arm env: DOSAGS_STATEXISTS=1 DOSAGS_PAKHANDLE=1 DOSAGS_PCM_ADOPT=1 (0241+0242+0322, informational repeat); nothing else differs between the cells.
- Binary: lab-s8's IO-arm probe AGSIOH.EXE (lab/mmd 18f1eb05) staged as iop.exe, sha256 687f819a2d640ee9e803ec0ca9f53e2c7c79120bfa1ac7ee87cbae4c31cc15fa,
  8,660,104 B, stamp 80463ed30b91 (build_dirty=1 expected, the probe applied uncommitted) = main 4dd196a4 + lab-mmd/io/probe-io-on-4dd196a4.diff.
  0321 (MIDI from memory) and SDL 0257 (PicoGUS pacing, K=128) are ON on that main, constant across the arms.
- Fixture: AUDH16's S16 cell -- run-hw 5days --startr 3, presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG (sound on,
  PGSB), SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, DOSAGS_TICKLOG=5200, --no-fine-timing, --collect TICKS.BIN,
  drive-walk 25 2 90, RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Outcome: per first-play open in play, the probe's "LABPROBE asset_open ... ms=" (lc > 0); mean and max per cell.
- GATE: IOES existfast mode=1 shadow=1 compared>0 mismatches=0, else IO41/IO42 do not count and 0241 stays off.
- VOID: |mean IOA0 - mean IOA1| > 10 ms, or any cell invalid (binary, exit, room 3 only, >= 3 opens, arm switches read back, witness).
- Predictions (AUDH16 baseline 55 ms/open): IO41 -25 to -45 ms (FALSIFIED if < 10); IO42 a further -15 to -25 ms (FALSIFIED if < 5).
- FILES= via WARMUPU (CONFIGSY.TXT). Re-dated 09-28 before data; capture stick unavailable (vcctrl 09-28 ~17:1xZ): witness = camera only, by operator decision.
