# CSV32H2 -- probe v3 486 round cell, round CS1 (pre-registration, before any data)
- Registration: lab-s8 lab/mmd d92d7382 lab-mmd/gate/COLDSTART3.md "486 ROUND" + 61ac39db (amendment A: the S8 cells) + 32e0dc72
  (CS1/CS2 staging); nothing added. MEASUREMENT: a decision readout, no verdict.
- Fixture: GATE S32P line verbatim -- as S16 with S32P-ACSETUP-ON.CFG:ACSETUP.CFG (24d874f2...), DOSAGS_FORCE_COLOR_DEPTH=32
  DOSAGS_MAX_SCALE=1 SDL_DOS_PACK24=1; room 3, --timeout 1800. Player default: no DOSAGS_ pins.
- Binary: AGSCS3 = main b7ac6c46 + probe v3 (lab/mmd build/lab/AGSCS3.EXE), staged as cs3.exe, sha256
  16a346cabd5da41665cbc1bdb54fbb2b9e30ca5ea4372319f34a37e4a7d521ab, 8,671,182 B, stamp 95519022159e; hashed at source and after copy.
- Scorer: lab-mmd/gate/coldstart3.py at 3a55115d over all 9 CS cells, once, after CS2: coldstart3.py CSV16H1 CSV32H1 CSV16H2 CSV32H2
  CSV16H3 CSV32H3 CSV8H1 CSV8H2 CSV8H3. VOID: stamp != 95519022159e, exit != 0, room != 3, or coldstart3.py's own (dump missing,
  dropped > 0, chunk != 512, scorer charges != engine charges).
- Readout (reported): share of charged silent IRQs IN-PUMP vs GAP / FEED / IN-PUMP-OWED; whether any GAP/FEED exists; per cell with
  and without IN-PUMP.
- Round CS1: warm-up + this block (cell 4 of 6); operator approved "All three" (CS1 -> CS2 -> S8M) 2026-09-29.
