# WBC16R -- WB pump arm on a CLEAN S16 fixture, round BATCH (lab/wb c9e25c2c LAB-WB-data/readmes/WBC16R-README.md; written 2026-09-29, pre-registration, before any data)
- Binary (unchanged, lab-wb confirmed 2026-09-29): main d533b56d, ef123dba0adf, build_dirty 0, sha256 235a5170b366fd8f...
  = round Z's / WBC's mainz.exe, re-hashed; VOID if the staged stamp differs. Same binary as WBC8R / WBC32R.
- Fixture: clean S16, IDLE (drive 0) -- run-hw 5days --startr 13 (room 13, music 0, no PCM), native 16-bit (no FORCE_COLOR_DEPTH /
  PACK24), PGSB, --no-fine-timing --timeout 1800, S32P-ACSETUP-ON.CFG:ACSETUP.CFG (24d874f2...), DOSAGS_MAX_SCALE=1
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 DOSAGS_TAS_AUTO_EXIT_TICK=6500 SDL_HINT_DOS_AUDIO_BACKEND=wb _WB_TX_DELAY=320 _WB_DRR_POLL=1
  _WB_RTC_PUMP=1; RUNHW_MIN_WAIT_S=450.
- Valid only if: midi_tick=rtc, stamp ef123dba0adf, build_dirty 0, bpp 2, room 13, NO PCM play logged, manifest complete, card locked.
- Scorer (committed before data): LAB-WB-data/depth-score.py --sha ef123dba0adf --no-pcm 5days_music0.mid D0REF.wav 113.999
  WBC16R-seg01.ogg WBC16R/RUNMANI.LOG WBC16P-seg01.ogg WBC16P/RUNMANI.LOG. PASS = A1-A6 + B vs WBC16P + D >= 0.70 + screen CLEAN
  + clean exit; D < 0.70 with the rest passing: one re-run (operator rule).
- Prediction (lab-wb): A pass; D 0.70-0.82 (WBC32R 0.780 on this room and song); B >= 0.90.
- Round BATCH ("Batch after 0347 lands"): warm-up, CAPS8, GL16, GL32, GL8, WBC16; one power-on; dated 2026-09-30, else re-dated first.
