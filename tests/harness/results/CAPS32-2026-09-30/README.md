# CAPS32 -- S32 capture check at 640x480, round CAPS (lab/wb 6def499d LAB-WB-data/readmes/CAPS32-README.md; written 2026-09-30, pre-registration, before any data)
- Binary (amended 2026-09-30 before any data): main 3aee50b4 (62c06f3e's series + ags 0347 + 0348, .sdl-dos-ports at hub 8e6a9c9, the
  C-based opl3_sink table), stamp 64d449a5b895, build_dirty 0, sha256 c042092b8344979ed85ea0d8bab1cbe76500ce990cb7a86ec157fd5a5ad51bd8,
  8,670,065 B, staged as mainc.exe; VOID on any other binary.
- Fixture: round BATCH's GL32 line verbatim, no change (already at the capture mode): run-hw 5days --startr 3, drive 2 = walk 25 2 90,
  S32P-ACSETUP-ON.CFG:ACSETUP.CFG (24d874f2...), DOSAGS_FORCE_COLOR_DEPTH=32 DOSAGS_MAX_SCALE=1 SDL_DOS_PACK24=1 direct framebuffer,
  TAS 5000, --no-fine-timing, PGSB, RUNHW_MIN_WAIT_S=270, --timeout 1800. One cell. Audio only: its tick figures are not a gate reading.
- Valid only if: the amended stamp, build_dirty 0, room 3, bpp 4, STDOUT logs music 0 and >= 1 "Playing sound 3", manifest complete,
  exit 0, card locked through the span. (Walked 486 GL32A/B logged sound 3 twice / three times; lab-wb's idle DOSBox-X C32G none.)
- Scorer (committed before data, lab/wb 33cde13b): capture-check3.py CAPS32-seg01.ogg CAPS32/RUNMANI.LOG 5days_sound3.wav (5ecb6a02...)
  D0REF.wav (874b8e8d...) 113.999. PASS = K1-K4, M1, M2 PASS + K5 counters meet the gate bar's audio line.
- Prediction (lab-wb, restated 2026-09-30): K1-K4 PASS; M1 within +-5 cents; M2 about 0.74-0.75 against controls <= ~0.56.
- Round CAPS (operator "Power on at 9:30 pt" = 04:30Z): warm-up, CAPS16, CAPS32; one power-on; dated 2026-09-30, else re-dated first.
  The capture (game music) stays local; its sha256 goes in AUDIO-SHA256.txt.
