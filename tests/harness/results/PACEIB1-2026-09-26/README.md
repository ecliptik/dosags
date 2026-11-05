# PACEIB1 -- PACEI cell 2 of 4 (A1 B1 B2 A2), round S (pre-registration, before any data)
- Registration: dosags-lab-journeys LAB-JOURNEYS.md 8.50 (lab/journeys 179af48c; notes 1-3, 2b281e27): does PicoGUS window
  pacing cause the extra silent SB IRQs? A same-binary ABBA; this README adds nothing to 8.50's rules.
- Arm: B = pace OFF: no pace hint, SDL 0256's default (the manifest must read pace=0/2570).
- Fixture: C3-512 exactly as PACE-H / PACEL (round P): run-hw trilbysnotes --startr 35, DOSAGS_TAS_AUTO_EXIT_TICK=5000,
  SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG (sound on, OPL3),
  SDL_HINT_DOS_MIDI_DEFER_DRAIN_STI=0, drive-walk 60 2 80, PGSB, RUNHW_MIN_WAIT_S=270, harness-default fine timing ON.
- Binary: landed main 0cb807ee (0317 + 0240), binary_sha12 794a45491c4b, build_dirty 0 -- pacei-score.py's --binary.
- Scorer: lab/journeys tests/harness/pacei-score.py (179af48c, sha256 19ba7d52ce9f6289...), run by lab-journeys over all four.
- Rules (8.50, fixed before data): CONVICTED if min(A TOTAL) > max(B TOTAL) and mean(A)-mean(B) >= 1, or an A cell fails a
  non-silent health row both B cells pass; CLEARED if mean(A)-mean(B) <= 0.5 and max(A) <= max(B)+1 and no A health fail;
  else INCONCLUSIVE (a second ABBA follows, pre-registered as its own round).
- VOID (8.50): wrong binary; dirty; not isr; pgdetect != 1; pace not the arm's; no TPIT witness; duration < 170; plus
  run-hw exit != 0, witness not clean, INPUT-LOG pair missing.
- Result: one STATUS.md row per cell; the ABBA verdict is lab-journeys'.
