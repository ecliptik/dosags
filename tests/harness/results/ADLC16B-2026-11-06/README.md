# ADLC16B -- ADLC16 re-run with model C (ags 0355): OPL2 on PGADLIB, backend auto, round G2 (G1's ADLC16R re-run, new tag; written 2026-11-06; pre-registration, before any data)
- Question: with no BLASTER, does the engine keep audio on (model C) and play the S16 song right on a real OPL2?
- Binary: release main e2663e6c (ags 0355 landed), build/ags-release/ags.exe stamp 340584af1155, build_dirty 0, sha256 38db55f09e7c...; VOID otherwise.
- Fixture: CAPS16's line verbatim EXCEPT --boot-profile 2 (PGADLIB) and --env SDL_HINT_DOS_AUDIO_BACKEND=auto (PGADLIB's AUTOEXEC sets
  "adlib", which this port fails closed on; ADLC16's README said "unset" -- wrong). Witness lines BLASTER.TXT, BACKEND.TXT.
- Valid only if: BLASTER.TXT empty ("ECHO is off"), BACKEND.TXT "auto", the "DOS audio mode: MIDI-only (model C)" line, "say OPL2",
  pcm=none, midi=opl3, midi_tick=poll, events > 0, room 3, music 0 logged, exit 0, manifest complete, card locked, one audio segment.
- Scorer: capture-check3.py (archive/lab-wb-2026-11-04 LAB-WB-data/, as CAPS16/GUSC16) <TAG>-seg01.ogg <TAG>/<TAG>.LOG 5days_sound3.wav
  (5ecb6a02...) D0REF.wav (874b8e8d...) 113.999. PASS = K1, K2, M1, M2; K3 FAIL by design (no DAC); K4/K5 reported.
- PCM timing witness (information): every "DOS-PORT midionly ... released" line has active_ms >= audio_ms; max excess reported.
- Prediction: PASS (7-note song, voices 0-8). Risks: poll-tick lateness (DOSBox-X late_max 121 ms) on M2; 38Ah aliasing on an OPL2.
- G1 VOID cause fixed in vcctrl 988d843 (select_boot_profile flushes the command line after menu keys). Safety net: any cell whose
  witness shows "Bad command" is VOID. Tags are new (manifests append on a reused tag).
- Round G2 (G1's re-run): WARMUPG2, GUSS0B, GUSS1B, ADLC16B, MPUNB16B; one power-on, cap 75 min; dated 2026-11-06, else re-dated first.
