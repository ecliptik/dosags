# WBC32R -- WB pump arm on the clean S32P fixture (replaces WBD32R's), round WBC (lab/wb d4b2db0c LAB-WB-data/readmes/WBC32R-README.md; pre-registration, before any data)
- Binary: main d533b56d, ef123dba0adf, build_dirty 0, sha256 235a5170b366fd8f... = round Z's mainz.exe, re-hashed; VOID if the staged
  stamp differs.
- Fixture: clean S32P, IDLE (drive 0) -- run-hw 5days --startr 13 (room 13, music 0, no PCM), PGSB, --no-fine-timing --timeout 1800,
  S32P-ACSETUP-ON.CFG:ACSETUP.CFG (24d874f2...), DOSAGS_FORCE_COLOR_DEPTH=32 DOSAGS_MAX_SCALE=1 SDL_DOS_PACK24=1
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 DOSAGS_TAS_AUTO_EXIT_TICK=6500 SDL_HINT_DOS_AUDIO_BACKEND=wb _WB_TX_DELAY=320 _WB_DRR_POLL=1
  _WB_RTC_PUMP=1 (pump only); RUNHW_MIN_WAIT_S=450. Arm: as listed (midi_tick rtc).
- Valid only if: midi_tick=rtc, stamp ef123dba0adf, build_dirty 0, bpp 4, room 13, NO PCM play logged, manifest complete, card locked
  through the window.
- Scorer (committed before data): LAB-WB-data/depth-score.py --sha ef123dba0adf --no-pcm 5days_music0.mid D0REF.wav 113.999
  WBC32R-seg01.ogg WBC32R/RUNMANI.LOG WBC32P-seg01.ogg WBC32P/RUNMANI.LOG.
- PASS = A1-A6 as registered + B vs WBC32P over min(W) + D >= 0.70 + screen CLEAN + clean exit. D < 0.70, rest passing: one re-run
  (operator rule).
- Prediction: A pass (late 0, pace=0/...); D 0.68-0.76; B >= 0.90.
- Round WBC: warm-up + these 4, pairs adjacent; waits for the operator (system OFF until they say). No game music in git.
