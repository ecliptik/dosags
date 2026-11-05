# S32PA2 -- S32P-HW cell 4 of 4 (A1 B1 B2 A2), round T (pre-registration, before any data)
- Registration: lab/metric 81c46b3b S32P-HW-PREREG/README.md (486 ABBA of ags 0239 on S32P, band rule) + amendments 8f38fdf0
  (cfg-on) and 7d30fe8d (--no-fine-timing); nothing added to those rules. Also the first S32P 486 gate reading.
- Arm A: `DOSAGS_FADE_RESYNC=0` (0239 off, the landed default); nothing else differs between the arms.
- Fixture S32P: run-hw 5days --startr 3, DOSAGS_FORCE_COLOR_DEPTH=32, DOSAGS_MAX_SCALE=1 (640x480 centred 1x), SDL_DOS_PACK24=1,
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, fixed timestep, DOSAGS_TAS_AUTO_EXIT_TICK=5000, sound ON (PGSB/OPL3) via
  S32-INPLAY-2026-09-26/cfg-on/ACSETUP.CFG (sha256 24d874f2c61db7b0...) staged as ACSETUP.CFG, drive-walk 25 2 90,
  --no-fine-timing, RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Binary: landed main 397d1f2a, binary_sha12 883a862a2d79, sha256 429851a4f28ba525..., build_dirty 0 (0239 landed default off).
  486 default after SDL 0257: PicoGUS window pacing ON (K=128), the intended shipping default, constant across the arms.
- Scorer: lab/metric tests/harness/lab-s32p-hw.py --sha 883a862a2d79 --witness-clean <tags> (committed with 81c46b3b).
- VOID if any cell is invalid (per the scorer, incl. a witness trail) or the A-A or B-B whole-run spread exceeds 0.10.
- FLIP iff both B cells have whole-run and steady in 39.2-40.8, mean skips B <= mean A - 8, mean proxy B >= A, and mean
  whole-run B >= mean A - 0.10; otherwise NO FLIP (the flip is a separate one-line default change).
- Prediction (81c46b3b): B cuts skips by ~10 against A; whole-run B within 0.10 of A. Result: one STATUS.md row per cell.
