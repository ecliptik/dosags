# WBD8P -- WB S8 same-binary poll control for WBD8R, round Z (lab/wb 4a4585d0 LAB-WB-data/readmes/WBD8P-README.md + WBD8R-README.md; pre-registration, before any data)
- Binary (amended 2026-09-28 before data): main d533b56d, ef123dba0adf, build_dirty 0, sha256 235a5170b366fd8f... = round W's
  mainw.exe, re-hashed; VOID if the staged stamp differs.
- Fixture S8 at the capture mode: run-hw trilbysnotes, drive-walk 25 2 80, PGSB, --no-fine-timing --timeout 1800 --ags-arg --startr
  --ags-arg 35, S32P-ACSETUP-ON.CFG:ACSETUP.CFG (sha256 24d874f2...; 640x480 centred 1x, deliberately: the dongle records silence at
  512x384), DOSAGS_MAX_SCALE=1 SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 DOSAGS_TAS_AUTO_EXIT_TICK=6500 SDL_HINT_DOS_AUDIO_BACKEND=wb
  _WB_TX_DELAY=320 _WB_DRR_POLL=1 _WB_RTC_PUMP=1 _WB_PREROLL_MS=200; RUNHW_MIN_WAIT_S=330. Arm: WBD8R's exactly **plus --env
  DOSAGS_MIDI_TICK=poll** (pump and pre-roll hints stay set).
- Valid only if: midi_tick=poll, stamp ef123dba0adf, bpp 1, room 35, "Playing music 4" before render pass 1500, manifest complete,
  card locked through the window.
- Scorer (committed before data): LAB-WB-data/depth-score.py --sha ef123dba0adf --pre trilby_music9.mid 20 45 --need-preroll --switch
  "Playing music 4" 1500 trilby_music4.mid T4REF.wav 37.711 WBD8R-seg01.ogg WBD8R/RUNMANI.LOG WBD8P-seg01.ogg WBD8P/RUNMANI.LOG. WBD8P
  is WBD8R's B control; its D is information (poll is not a candidate). Prediction: D 0.50-0.72.
- Round Z: WARMUPZ, WBD8P WBD8R, WBD32P WBD32R (pairs adjacent). Game-music captures/renders: never committed.
