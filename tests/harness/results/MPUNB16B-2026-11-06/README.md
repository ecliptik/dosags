# MPUNB16B -- MPU-401 without BLASTER (PROXY), wb, model C (ags 0355), round G2 (G1's MPUNB16 re-run, new tag; written 2026-11-06; pre-registration, before any data)
- No g2k boot profile has an MPU-401 and no SB, so this is a PROXY: PGSB (default) with BLASTER cleared in RUN.BAT; the DSP exists but
  is never opened. It tests "no BLASTER -> model C -> MPU at the 330h default", not "no SB on the bus". Labelled a proxy in the result.
- Binary: as ADLC16R (340584af1155). Fixture: CAPS16's line verbatim EXCEPT --env BLASTER= and --env SDL_HINT_DOS_AUDIO_BACKEND=wb.
- Valid only if: BLASTER.TXT empty, BACKEND.TXT "wb", "WaveBlaster/MPU-401 cold-init succeeded", the model C line, pcm=none, midi=wb,
  midi_tick=poll, events > 0, room 3, music 0 logged, exit 0, manifest complete, card locked, one audio segment.
- Scorer: capture-check3.py (archive/lab-wb-2026-11-04 LAB-WB-data/, as CAPS16/GUSC16) <TAG>-seg01.ogg <TAG>/<TAG>.LOG 5days_sound3.wav
  (5ecb6a02...) D0REF.wav (874b8e8d...) 113.999. PASS = K1, K2, M1, M2 (the DreamBlaster plays the song); K3 FAIL by design; K4/K5 reported.
- Prediction: PASS. Risk: the blind MPU transport on the poll tick bursts (DOSBox-X burst=30 at song start).
- G1 VOID cause fixed in vcctrl 988d843 (select_boot_profile flushes the command line after menu keys). Safety net: any cell whose
  witness shows "Bad command" is VOID. Tags are new (manifests append on a reused tag).
- Round G2 (G1's re-run): WARMUPG2, GUSS0B, GUSS1B, ADLC16B, MPUNB16B; one power-on, cap 75 min; dated 2026-11-06, else re-dated first.
