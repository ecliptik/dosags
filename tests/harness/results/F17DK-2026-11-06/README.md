# F17DK -- 7 Days a Skeptic room 2 in play, KPI baseline on the release exe, round F1a (written 2026-11-06; pre-registration, before any data)
- Binary: release a1dba5d61624 (build/ags-release/ags.exe, sha256 1fc012c16d41...), sound ON; VOID if the stamp differs.
- Fixture (F1 prep k-7days-tc): run-hw 7days --ags-arg --loadsavedgame --ags-arg 71, --extra-file AGSSAVE.071 (untracked, sha256
  dd0e6e89469bb361...), ACSETUP-ON-512X384-ROUND.CFG, direct framebuffer, TAS 12150, DOSAGS_TICKCLICKS=7263,80,62 (engine clicks, no
  host drive: host clicks hit the icon bar's Quit), --no-fine-timing, PGSB, MIN_WAIT 270, --timeout 1800 + the BLASTER line.
- KPI (PLAN-FPS): frames displayed = 1 - frames_skipped/ticks and presents_real/render_passes (gatebar.py, amended c08f8dc4), steady,
  fps_p50; >= 99% displayed at steady 39.2-40.8 = MET. Reported per cell; x1 here (a baseline, not a claim).
  RESTORE cell: whole-run and presents_real/render_passes restore from the save -- read presents via f1/f1persec.py; 1-fs/ticks
  and steady stand. Valid only if room 2 throughout the window and exit 0.
- Witness: camera sheet (512x384 / 320x200 modes: the card cannot lock); BLASTER.TXT "A220 I7 D3 P330 T3" else VOID.
  First round on vcctrl 1e5a1e7's transfer BATs (VCCHK dadb6a50, VCGET 2ea736aa, VCLIST af3a192b): job logs checked.
- Scorer: gatebar.py --label 7D --stamp a1dba5d61624 --room 2 F17DK F17DK + f1/f1persec.py F17DK. No prior 486 figure.
- Round F1a (PLAN-FPS step 2): WARMUPF1, F1MMDK, F1MMDP, F17DK, F17DP, F1AQK; one power-on, cap 85 min; dated 2026-11-06, else re-dated first.
