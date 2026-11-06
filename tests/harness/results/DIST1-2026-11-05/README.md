# DIST1 -- the player zip as shipped, run the way README.TXT says, round R4 (written 2026-11-05; pre-registration, before any data)
- Question: does `make dist`'s zip, set up only as its README.TXT tells a player, play an AGS game on this machine at the gate rate,
  with music and effects? Every gate cell so far added harness settings; this one adds as few as the harness allows.
- Files: AGS.EXE and CWSDPMI.EXE from build/ws/roundR4/dosags-dev.zip (make-dist --repo-url https://github.com/ecliptik/dosags; zip
  sha256 89d012b9...; check-dist PASS); AGS.EXE = release a1dba5d61624 byte for byte, CWSDPMI.EXE = the pinned r7, OPL3BANK.DAT = the staged bank. VOID if any differs.
- Player settings: ACSETUP.CFG = README.TXT's example verbatim (tests/harness/presentation/dist/ACSETUP-README.CFG: [graphics]
  fullscreen = 512x384, game_scale_fs = round, windowed = 0; no [sound] section); NO SET of DOSAGS_FIXED_TIMESTEP (--no-fixed-timestep:
  the release default), SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER (engine default ON), DOSAGS_TICKSTATS_FINE (--no-fine-timing) or
  SDL_HINT_DOS_AUDIO_BACKEND (auto); PGSB's BLASTER. Harness-only: the log tags, TAS 5000 (the exit), --startr 3, drive 2 (walk
  25 2 90), MIN_WAIT 270, the BLASTER line.
- PASS = exit 0, room 3, the fixed-timestep log line reads on, midi=opl3, STDOUT logs music 0 and >= 1 "Playing sound 3", and
  gatebar.py --label S16 --stamp a1dba5d61624 --room 3 (one cell twice) MET with the camera sheet CLEAN. Otherwise FAIL, with the cause.
- Comparison: GR16R3 (round R3) and GL16A/B 39.29 / 40.13, 39.29 / 40.10. Prediction: PASS at about GR16R3's figures.
- Round R4: WARMUPR4, DIST1, GUSC16, ADLC16; one power-on, cap 70 min; dated 2026-11-05, else re-dated first.
