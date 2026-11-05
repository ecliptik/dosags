# S32FF1 -- 0240 killswitch pair cell (S32FF1 of S32FF0 S32FF1), round V (pre-registration, before any data)
- Registration: lab-metric lab/metric S32P-FF-HW-PREREG/README.md with its amendments 00a30802, 7d30fe8d (--no-fine-timing) and
  f5d2a7a6 (round V; binary = the landed main at round-V staging); nothing added to those rules.
- Arm: `--env DOSAGS_FADEFAST32=1` (0240 on, its default); nothing else differs.
- Fixture: S32P as round T ran it -- run-hw 5days --startr 3, DOSAGS_FORCE_COLOR_DEPTH=32, DOSAGS_MAX_SCALE=1 (640x480 centred 1x),
  SDL_DOS_PACK24=1, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, cfg-on ACSETUP.CFG (sha256 24d874f2...,
  sound on), drive-walk 25 2 90, PGSB, --no-fine-timing, RUNHW_MIN_WAIT_S=270, --timeout 1800.
- Binary: main 5bec55aa, binary_sha12 d18d63368af6, build_dirty 0, sha256 8360f23da57ab80f... (0241/0242 ON in both arms).
- Entry fade = room-3 DOSAGS_XT fadein_end - fadein_begin (STDOUT). Scorer: lab-s32p-ff-hw.py --sha d18d63368af6 --witness-clean <tags>.
- PASS iff FF1 fade <= 0.9 s AND <= 0.6 x FF0's AND whole-run gain >= +0.15. FALSIFIED iff FF1 fade > 0.6 x FF0's OR gain < +0.15;
  a fast fade over 0.9 s but under 0.6x is VOID-stated. Also a first S32 gate reading.
- Prediction (fixed): entry fade ~2.2 s -> <= 0.9 s; whole-run +0.3 to +0.6.
