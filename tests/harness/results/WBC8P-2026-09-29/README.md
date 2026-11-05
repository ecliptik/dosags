# WBC8P -- clean S8 poll control for WBC8R, round WBC (lab/wb d4b2db0c LAB-WB-data/readmes/WBC8P-README.md + WBC8R-README.md; pre-registration, before any data)
- Binary: main d533b56d, ef123dba0adf, build_dirty 0, sha256 235a5170b366fd8f... = round Z's mainz.exe, re-hashed; VOID if the staged
  stamp differs.
- Fixture: clean S8, IDLE (drive 0) -- run-hw trilbysnotes --startr 40 (room 40, music 10, no PCM), PGSB, --no-fine-timing --timeout
  1800, S32P-ACSETUP-ON.CFG:ACSETUP.CFG (24d874f2...; 640x480 centred 1x, the capture mode), DOSAGS_MAX_SCALE=1
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 DOSAGS_TAS_AUTO_EXIT_TICK=6500 SDL_HINT_DOS_AUDIO_BACKEND=wb _WB_TX_DELAY=320 _WB_DRR_POLL=1
  _WB_RTC_PUMP=1 _WB_PREROLL_MS=200; RUNHW_MIN_WAIT_S=450. Arm: WBC8R's exactly **plus --env DOSAGS_MIDI_TICK=poll**.
- Valid only if: midi_tick=poll, stamp ef123dba0adf, build_dirty 0, bpp 1, room 40, "Playing music 10" before render pass 500, NO PCM
  play logged, manifest complete, card locked through the window.
- Scorer (committed before data): LAB-WB-data/depth-score.py --sha ef123dba0adf --need-preroll --switch "Playing music 10" 500
  --no-pcm trilby_music10.mid T10REF.wav 38.919 WBC8R-seg01.ogg WBC8R/RUNMANI.LOG WBC8P-seg01.ogg WBC8P/RUNMANI.LOG. WBC8P is WBC8R's
  B control; its D is information. Prediction: D 0.50-0.80.
- Round WBC: warm-up + these 4, pairs adjacent; waits for the operator (system OFF until they say). No game music in git.
