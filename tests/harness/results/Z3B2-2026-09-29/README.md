# Z3B2 -- Z3 measurement cell 5 of 6 (Z3A1 Z3B1 Z3C1 Z3C2 Z3B2 Z3A2), round Z3 (pre-registration, before any data)
- Registration: lab-s8 lab/mmd 15fca729 "ROUND Z3" + b77e6948 "Z3 AMENDMENT" (lab-mmd/land-0320/README.md, dated 2026-09-29, before
  any data); nothing added. MEASUREMENT only: no verdict, no flip.
- Arm: B = `--env DOSAGS_PCM_INCR=1`. Pins in all six: DOSAGS_STATEXISTS=1 DOSAGS_PAKHANDLE=1 DOSAGS_PCM_ADOPT=0 DOSAGS_MIDI_MEM=1.
- Fixture: round V's S8 recipe -- run-hw trilbysnotes --startr 35, --timeout 1800, --no-fine-timing,
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG, drive-walk 25 2 80,
  PGSB, RUNHW_MIN_WAIT_S=270.
- Binary: AGSLAC4 staged as lac4.exe, sha256 400decf2d8a6185947250784ec722ae5ee3d2a2139f4b9485d27b51bfe57cc45, 9,218,469 B, stamp
  2f73bacd1f95 (build_dirty=1; main d533b56d + look-ahead candidate + buffered probe), hashed at source and after copy.
- Scorer: lab-mmd/land-0320/z3.py at 912453a5: z3.py 2f73bacd1f95 <Z3A1> <Z3B1> <Z3C1> <Z3C2> <Z3B2> <Z3A2>; per-cell readout and
  per-arm medians, no verdict.
- VOID: stamp, exit, room != 35, arm env/pins, pcmcache incr, LABPUMPDUMP/LABTEXTDUMP missing or dropped > 0, live probe lines, no
  sound11/sound18 first play.
- Round Z3 = WARMUPZ3 (l308) + these six, cell 5; needs its own operator OK (after Z and Z2).
