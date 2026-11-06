# GUSC16 -- the GUS backend (PicoGUS GUS mode) on the release flavour, 640x480 capture, round R4 (written 2026-11-05; pre-registration, before any data)
- Question: README.TXT advertises SDL_HINT_DOS_AUDIO_BACKEND=gus (PCM and MIDI through the GF1); it was last heard on hardware on
  09-15 builds (S7). DOSBox-X cannot test it (its GF1 fails the DRAM presence probe).
- Binary: release a1dba5d61624 (build/ags-release/ags.exe, sha256 1fc012c16d41..., the R1-R3 exe); VOID if the manifest stamp differs.
- Fixture: CAPS16's line verbatim (build/ws/roundCAPS/CAPS16.ARGS: 5days --startr 3, drive 2 = walk 25 2 90, S32P-ACSETUP-ON.CFG
  (24d874f2...):ACSETUP.CFG + DOSAGS_MAX_SCALE=1 = 640x480 centred 1x 16-bit, direct framebuffer, TAS 5000, --no-fine-timing,
  MIN_WAIT 300, --timeout 1800) EXCEPT --boot-profile 3 (PGGUS) and
  --env SDL_HINT_DOS_AUDIO_BACKEND=gus. Witness line: ECHO %ULTRASND% > ULTRASND.TXT, must read "240,3,3,7,7" (g2k README.TXT), else VOID.
- Valid only if: pcm=gus and midi=gus in audio_vital_status (GF1 found), room 3, STDOUT logs music 0 and >= 1 "Playing sound 3",
  manifest complete, exit 0, card locked through the span, one audio segment.
- Scorer: capture-check3.py (archive/lab-wb-2026-11-04 LAB-WB-data/, as CAPS16) <TAG>-seg01.ogg <TAG>/<TAG>.LOG 5days_sound3.wav (5ecb6a02...)
  D0REF.wav (874b8e8d...) 113.999. PASS = K1-K4, M1 (pitch +-15 cents), M2 (chroma); K5 printed
  (the SB counters read NA under GUS). M1/M2 were validated on OPL3 and the DreamBlaster only, so an M1/M2 FAIL with K1-K4 PASS
  is reported as such (GF1 patches vs the FluidR3 render), not a backend failure. vs CAPS16 (OPL3). Prediction: K1-K4 PASS, M1/M2 open.
- Round R4: WARMUPR4, DIST1, GUSC16, ADLC16; one power-on, cap 70 min; dated 2026-11-05, else re-dated first.
