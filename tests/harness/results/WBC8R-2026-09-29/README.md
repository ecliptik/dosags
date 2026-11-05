# WBC8R -- WB pump + pre-roll arm on the clean S8 fixture (replaces WBD8R's), round WBC (lab/wb d4b2db0c LAB-WB-data/readmes/WBC8R-README.md; pre-registration, before any data)
- Binary: main d533b56d, ef123dba0adf, build_dirty 0, sha256 235a5170b366fd8f... = round Z's mainz.exe, re-hashed; VOID if the staged
  stamp differs.
- Fixture: clean S8, IDLE (drive 0) -- run-hw trilbysnotes --startr 40 (room 40, music 10, no PCM), PGSB, --no-fine-timing --timeout
  1800, S32P-ACSETUP-ON.CFG:ACSETUP.CFG (24d874f2...; 640x480 centred 1x, the capture mode), DOSAGS_MAX_SCALE=1
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 DOSAGS_TAS_AUTO_EXIT_TICK=6500 SDL_HINT_DOS_AUDIO_BACKEND=wb _WB_TX_DELAY=320 _WB_DRR_POLL=1
  _WB_RTC_PUMP=1 _WB_PREROLL_MS=200; RUNHW_MIN_WAIT_S=450. Arm: as listed (midi_tick rtc).
- Valid only if: midi_tick=rtc, stamp ef123dba0adf, build_dirty 0, bpp 1, room 40, "Playing music 10" before render pass 500, NO PCM
  play logged, preroll= on with messages moved, manifest complete, card locked through the window.
- Scorer (committed before data): LAB-WB-data/depth-score.py --sha ef123dba0adf --need-preroll --switch "Playing music 10" 500
  --no-pcm trilby_music10.mid T10REF.wav 38.919 WBC8R-seg01.ogg WBC8R/RUNMANI.LOG WBC8P-seg01.ogg WBC8P/RUNMANI.LOG.
- PASS = A1-A6 as registered + B vs WBC8P over min(W) + D >= 0.70 + screen CLEAN + clean exit. D < 0.70, rest passing: one re-run
  (operator rule).
- Prediction: A pass (late 0, stuck 0); D 0.62-0.80; B >= 0.90.
- Round WBC: warm-up + these 4, pairs adjacent; waits for the operator (system OFF until they say). No game music in git.
