# CAPS32R -- the CAPS32 re-run (S32 capture check at 640x480), round C32R (lab/wb 49aa373f re-run rule + 32378c49 binary; written 2026-09-30, pre-registration, before any data)
- Why: round CAPS's CAPS32 was VOID as registered (no "Playing sound 3"; 3ba3b0ec). lab/wb 49aa373f: "a VOID cell is re-run once under a new
  tag (CAPS32R); same fixture, binary and scorer; the invocation takes the new tag's files; a second VOID ends the attempt."
- Binary (amended again 2026-09-30 before any re-run data, lab/wb 32378c49; operator "Revert now, fix in lab"): main 8f439c0f (62c06f3e's
  series + ags 0347, .sdl-dos-ports at hub 8e6a9c9, ags 0348 reverted), stamp e3a83135dc9c, build_dirty 0, sha256
  75093c1a676f27912feeb59a29ff00764a09f42f6f83f0a97817f3385634b75b, 8,668,939 B, staged as mainc.exe; VOID on any other binary.
- Fixture: CAPS32's = round BATCH's GL32 line verbatim: run-hw 5days --startr 3, drive 2 = walk 25 2 90, S32P-ACSETUP-ON.CFG:ACSETUP.CFG
  (24d874f2...), DOSAGS_FORCE_COLOR_DEPTH=32 DOSAGS_MAX_SCALE=1 SDL_DOS_PACK24=1 direct framebuffer, TAS 5000, --no-fine-timing, PGSB,
  RUNHW_MIN_WAIT_S=270, --timeout 1800. One cell. Audio only: its tick figures are not a gate reading.
- Valid only if: the amended stamp, build_dirty 0, room 3, bpp 4, STDOUT logs music 0 and >= 1 "Playing sound 3", manifest complete,
  exit 0, card locked through the span. A second VOID ends the attempt.
- Scorer (committed before data, lab/wb 33cde13b): capture-check3.py CAPS32R-seg01.ogg CAPS32R/RUNMANI.LOG 5days_sound3.wav (5ecb6a02...)
  D0REF.wav (874b8e8d...) 113.999. PASS = K1-K4, M1, M2 PASS + K5 counters meet the gate bar's audio line.
- Prediction (lab-wb, 2026-09-30): K1-K4 PASS; M1 within +-5 cents; M2 about 0.74-0.75 against controls <= ~0.56. Underruns 0 (0348 out).
- Round C32R: warm-up + CAPS32R, one power-on; dated 2026-09-30, else re-dated first. The capture stays local (AUDIO-SHA256.txt).
