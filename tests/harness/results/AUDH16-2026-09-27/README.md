# AUDH16 -- 486 audio split of the S16 fixture, round T (pre-registration, before any data)
- Registration: lab-s8's lab/mmd d5e3deba `lab-mmd/audh16/README.md` (docs/lab/s8.md audio slice) with its dated amendment
  b868fef1 (2026-09-27, before any data); P1-P3/VOID as there. A probe cell, not a gate figure.
- Binary (amendment): build/lab/AGSAUDP4.EXE staged as audh16.exe, sha256 e2fa70108d752a86af652325b9d0457f8e578bdb6a6da6705e51ffe9c25f35ff,
  8,642,025 B, stamp 90f81deaa3fc = main 397d1f2a (post SDL 0257: PicoGUS pacing ON, K=128) + lab-mmd/probe-audio-v2-on-397d1f2a.diff.
- Cell: the S16 gate fixture, SOUND ON: run-hw 5days --tag AUDH16 --timeout 1800 --no-fine-timing, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1,
  DOSAGS_TAS_AUTO_EXIT_TICK=5000, DOSAGS_TICKLOG=5200, --startr 3, presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG
  (sha256 33b76f5c...), --collect TICKS.BIN; drive-walk 25 2 90; PGSB (SB2.0 + OPL3); RUNHW_MIN_WAIT_S=270.
- P1: sound1.wav's first play (the walk click near lc 561) costs >= 200 ms, asset_open + asset_read >= 50% of it.
- P2: sound10.wav's (215 KB) first play costs >= 250 ms, asset_read >= 50% of it, in a tick > 250 ms.
- P3: every tick > 250 ms other than the room entry and the blocking-script outer tick holds a first play (F) and/or a click (C).
- Scorer (lab-s8, after the round): python3 lab-mmd/audh16/audh.py <dir>.
- VOID: stamp != 90f81deaa3fc; run-hw exit != 0; staged CWSDPMI.EXE != 2de899fe...; no LABPROBE lines; room other than 3;
  pcm accounting broken (pcm_irqs 0).
- Result: one STATUS.md row; the scoring is lab-s8's.
