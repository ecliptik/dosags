# CSV8H3 -- probe v3 486 round cell, round CS2 (pre-registration, before any data)
- Registration: lab-s8 lab/mmd d92d7382 lab-mmd/gate/COLDSTART3.md "486 ROUND" + 61ac39db (amendment A: the S8 cells) + 32e0dc72
  (CS1/CS2 staging); nothing added. MEASUREMENT: a decision readout, no verdict.
- Fixture: GATE S8 line verbatim (round R S8R) -- run-hw trilbysnotes --startr 35, drive 3 (walk 25 2 80),
  ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=5000, --no-fine-timing,
  PGSB, RUNHW_MIN_WAIT_S=270, --timeout 1800; no MSGSKIP. Player default: no DOSAGS_ pins.
- Binary: AGSCS3 = main b7ac6c46 + probe v3 (lab/mmd build/lab/AGSCS3.EXE), staged as cs3.exe, sha256
  16a346cabd5da41665cbc1bdb54fbb2b9e30ca5ea4372319f34a37e4a7d521ab, 8,671,182 B, stamp 95519022159e; hashed at source and after copy.
- Scorer: lab-mmd/gate/coldstart3.py at 3a55115d over all 9 CS cells, once, after CS2: coldstart3.py CSV16H1 CSV32H1 CSV16H2 CSV32H2
  CSV16H3 CSV32H3 CSV8H1 CSV8H2 CSV8H3. VOID: stamp != 95519022159e, exit != 0, room != 35, or coldstart3.py's own (dump missing,
  dropped > 0, chunk != 512, scorer charges != engine charges).
- Readout (reported): share of charged silent IRQs IN-PUMP vs GAP / FEED / IN-PUMP-OWED; whether any GAP/FEED exists; per cell with
  and without IN-PUMP; (d) the class of any charge within 3 ticks after sound11's and sound18's first plays.
- Round CS2: warm-up + this block (cell 3 of 3); operator approved "All three" (CS1 -> CS2 -> S8M) 2026-09-29.
