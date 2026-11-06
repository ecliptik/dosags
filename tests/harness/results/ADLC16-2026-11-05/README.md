# ADLC16 -- OPL2 (PicoGUS AdLib mode) with the README's default backend, release flavour, round R4 (written 2026-11-05; pre-registration, before any data)
- Question: README.TXT says auto drives an OPL3/OPL2. On an OPL2 the sink still drives 18 voices (ags 0205: voices 9-17 cannot
  sound there); the S16 song peaks at 7 notes, so only voices 0-8 should be used. Is the music right on a real OPL2?
- Binary: release a1dba5d61624 (build/ags-release/ags.exe, sha256 1fc012c16d41..., the R1-R3 exe); VOID if the manifest stamp differs.
- Fixture: CAPS16's line verbatim (build/ws/roundCAPS/CAPS16.ARGS: 5days --startr 3, drive 2 = walk 25 2 90, S32P-ACSETUP-ON.CFG
  (24d874f2...):ACSETUP.CFG + DOSAGS_MAX_SCALE=1 = 640x480 centred 1x 16-bit, direct framebuffer, TAS 5000, --no-fine-timing,
  MIN_WAIT 300, --timeout 1800) EXCEPT --boot-profile 2 (PGADLIB);
  backend unset (auto). PGADLIB has no DSP: no PCM by design (g2k README.TXT). Witness line: ECHO %BLASTER% > BLASTER.TXT, recorded.
- Valid only if: the "status bits 1-2 say OPL2" log line, midi=opl3, room 3, STDOUT logs music 0, manifest complete, exit 0, card
  locked through the span, one audio segment.
- Scorer: capture-check3.py (archive/lab-wb-2026-11-04 LAB-WB-data/, as CAPS16) <TAG>-seg01.ogg <TAG>/<TAG>.LOG 5days_sound3.wav (5ecb6a02...)
  D0REF.wav (874b8e8d...) 113.999. PASS = K1, K2, M1, M2 PASS (the music);
  K3 (PCM effect) is expected absent by design and K4 is reported. A FAIL on M2 or K2 is the finding the cell exists to look for.
- Prediction: PASS (7-note song, voices 0-8). Risk: the second-bank writes at init land on 388h if the card aliases 38Ah.
- Round R4: WARMUPR4, DIST1, GUSC16, ADLC16; one power-on, cap 70 min; dated 2026-11-05, else re-dated first.
