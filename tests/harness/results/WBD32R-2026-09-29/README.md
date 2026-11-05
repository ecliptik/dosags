# WBD32R -- WB pump arm on S32P (per-depth WB bar, D bar 0.70), round Z (lab/wb 4a4585d0 LAB-WB-data/readmes/WBD32R-README.md; pre-registration, before any data)
- Binary (amended 2026-09-28 before data): main d533b56d, ef123dba0adf, build_dirty 0, sha256 235a5170b366fd8f... = round W's
  mainw.exe, re-hashed; VOID if the staged stamp differs.
- Fixture S32P, sound on at WB: run-hw 5days, drive-walk 25 2 90, PGSB, --no-fine-timing --timeout 1800 --ags-arg --startr --ags-arg
  3, S32P-ACSETUP-ON.CFG:ACSETUP.CFG (sha256 24d874f2...), DOSAGS_FORCE_COLOR_DEPTH=32 DOSAGS_MAX_SCALE=1 SDL_DOS_PACK24=1
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 DOSAGS_TAS_AUTO_EXIT_TICK=6500 SDL_HINT_DOS_AUDIO_BACKEND=wb _WB_TX_DELAY=320 _WB_DRR_POLL=1
  _WB_RTC_PUMP=1 (pump only, no pre-roll hint); RUNHW_MIN_WAIT_S=360. Arm: as listed (midi_tick rtc).
- Valid only if: midi_tick=rtc, stamp ef123dba0adf, build_dirty 0, bpp 4, room 3, manifest complete, card locked through the window.
  (lab-wb's Valid line read round T's 883a862a2d79 at 4a4585d0; fixed to ef123dba0adf before any data in lab/wb c080538f.)
- Scorer (committed before data): LAB-WB-data/depth-score.py --sha ef123dba0adf 5days_music0.mid D0REF.wav 113.999 WBD32R-seg01.ogg
  WBD32R/RUNMANI.LOG WBD32P-seg01.ogg WBD32P/RUNMANI.LOG (depth-window.py, end-anchored, W 24.7).
- PASS = A1-A6 + B vs WBD32P over min(W) + D >= 0.70 + screen CLEAN + clean exit. D < 0.70, rest passing: one re-run (operator rule);
  one late byte or stuck repair: a second run; more, or a stall: report, no verdict.
- Prediction: A pass; D 0.68-0.76; B chroma >= 0.93; the 486 line must read pace=0/... . DOSBox-X Z32A: late 0, preroll=0/0/0/0.
- Round Z: WARMUPZ, WBD8P WBD8R, WBD32P WBD32R (pairs adjacent). Game-music captures/renders: never committed.
