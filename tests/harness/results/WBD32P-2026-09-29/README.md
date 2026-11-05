# WBD32P -- WB S32P same-binary poll control for WBD32R, round Z (lab/wb 4a4585d0 LAB-WB-data/readmes/WBD32P-README.md + WBD32R-README.md; pre-registration, before any data)
- Binary (amended 2026-09-28 before data): main d533b56d, ef123dba0adf, build_dirty 0, sha256 235a5170b366fd8f... = round W's
  mainw.exe, re-hashed; VOID if the staged stamp differs.
- Fixture S32P, sound on at WB: run-hw 5days, drive-walk 25 2 90, PGSB, --no-fine-timing --timeout 1800 --ags-arg --startr --ags-arg
  3, S32P-ACSETUP-ON.CFG:ACSETUP.CFG (sha256 24d874f2...), DOSAGS_FORCE_COLOR_DEPTH=32 DOSAGS_MAX_SCALE=1 SDL_DOS_PACK24=1
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 DOSAGS_TAS_AUTO_EXIT_TICK=6500 SDL_HINT_DOS_AUDIO_BACKEND=wb _WB_TX_DELAY=320 _WB_DRR_POLL=1
  _WB_RTC_PUMP=1 (pump only, no pre-roll hint); RUNHW_MIN_WAIT_S=360. Arm: WBD32R's exactly **plus --env DOSAGS_MIDI_TICK=poll** (the
  pump hint stays set).
- Valid only if: midi_tick=poll, stamp ef123dba0adf, build_dirty 0, bpp 4, room 3, manifest complete, card locked through the window.
  (lab-wb's Valid line read round T's 883a862a2d79 at 4a4585d0; fixed to ef123dba0adf before any data in lab/wb c080538f.)
- Scorer (committed before data): LAB-WB-data/depth-score.py --sha ef123dba0adf 5days_music0.mid D0REF.wav 113.999 WBD32R-seg01.ogg
  WBD32R/RUNMANI.LOG WBD32P-seg01.ogg WBD32P/RUNMANI.LOG (depth-window.py, end-anchored, W 24.7). WBD32P is WBD32R's B control; its D
  is information. Prediction: D 0.55-0.68.
- Round Z: WARMUPZ, WBD8P WBD8R, WBD32P WBD32R (pairs adjacent). Game-music captures/renders: never committed.
