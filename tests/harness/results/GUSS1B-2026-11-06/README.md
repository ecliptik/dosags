# GUSS1B -- GUS sign-flip pair cell 2 of 2 (S1: SDL 0270, 8-bit flipped to signed), round G2 (G1's GUSS1 re-run, new tag; written 2026-11-06; pre-registration, before any data)
- Lab binaries (~/git/dosags-lab-gus: dosags main 4904a638 + ags 0356-0358 + hub gus-pcm-fix f2515cf in .sdl-dos-ports/shared/audio;
  release flavour), identical except SDL 0270 (8-bit uploads flipped to signed): S0 build/ws/gusbisect/bin/s0/ags.exe stamp
  854228747226 sha256 a61c2c6a574a...; S1 bin/s1 stamp 2d00e8b416f0 sha256 f9a10e1576d7.... VOID if the staged stamp differs.
- Fixture: GUSC16 verbatim (5days --startr 3, drive 2 = walk 25 2 90, --boot-profile 3 PGGUS, SDL_HINT_DOS_AUDIO_BACKEND=gus,
  S32P-ACSETUP-ON.CFG + DOSAGS_MAX_SCALE=1, direct framebuffer, TAS 5000, --no-fine-timing, MIN_WAIT 300, --timeout 1800) + witness lines
  ECHO %ULTRASND% > ULTRASND.TXT (must read 240,3,3,7,7) and the BLASTER line.
- Valid only if: midi=gus, room 3, >= 1 "Playing sound 3", exit 0, manifest complete, card locked, one audio segment, no "Bad command".
- Scorer: capture-check3.py (archive/lab-wb-2026-11-04 LAB-WB-data/, as CAPS16/GUSC16) <TAG>-seg01.ogg <TAG>/<TAG>.LOG 5days_sound3.wav
  (5ecb6a02...) D0REF.wav (874b8e8d...) 113.999.
- Prediction if the GF1 reads 8-bit signed: S1 K3 PASS where S0 K3 FAILs (G1's GUSS0 failed K3); M1/M2 about equal (music
  is 16-bit .pat); both underruns 0, open_failures=0. FALSIFIED if S0 K3 PASS, or S1 K3 FAIL with S0's: then 0270 must not land.
  (G1's DC-mean check dropped: the rig's capture path is AC-coupled, GUSS0 mean 0.0.)
- G1 VOID cause fixed in vcctrl 988d843 (select_boot_profile flushes the line after menu keys). New tags (manifests append).
- Round G2 (G1's re-run): WARMUPG2, GUSS0B, GUSS1B, ADLC16B, MPUNB16B; one power-on, cap 75 min; dated 2026-11-06, else re-dated first.
