# R1I2 -- R1 RELEASE ABBA (S8 fixture; PLAN-NEXT step 4: does the release flavour carry the S8 gate?), cell 4 of 4 (R1I1 R1R1 R1R2 R1I2), arm A instrumented (written 2026-11-05; pre-registration, before any data)
- Binaries, main f2228d5e (= origin/main), build_dirty 0, both with step 1b (ags 0352/0353, SDL 0269) and ags 0354: A instr.exe =
  build/ags/ags.exe 7e5dfe26f272 (8,636,055 B, sha256 d72fe181d8fa...); B rel.exe = build/ags-release/ags.exe a1dba5d61624
  (DOSAGS_RELEASE=1, 8,598,425 B, sha256 1fc012c16d41...). Staged from build/ws/roundR1 (expected.txt). VOID if the stamp is not the arm's.
- Fixture: GL8A's line verbatim (build/ws/roundBATCH/GL8.ARGS: trilbysnotes --startr 35, drive 3 = walk 25 2 80, ACSETUP-ON-512X384-ROUND.CFG
  :ACSETUP.CFG, direct framebuffer, TAS 5000, MSGSKIP=1, --no-fine-timing, fixed timestep, PGSB, MIN_WAIT 270, --timeout 1800) + the BLASTER line.
- Witness: BLASTER.TXT (RUN.BAT `ECHO %BLASTER% > BLASTER.TXT` before AGS.EXE, --collect) must read "A220 I7 D3 P330 T3" stripped
  (profiles/dosags.yaml profile_witness), else VOID. Camera sheet first; capture STALE reported (stick dropouts 11-04 18:23-18:37 PST).
- Scorer (committed before data): abba-r1.py --stamp-a 7e5dfe26f272 --stamp-b a1dba5d61624 R1I1 R1R1 R1R2 R1I2, gatebar.py's cell() per cell.
  Rule (operator 2026-11-05): NOT SEPARABLE if |A1-A2| >= 0.30 on either tick figure; EQUIVALENT if mean(B) >= mean(A) - 0.10 on both,
  else LOSS; B MET x2 = the release S8 x2 (R2 then drops GR8). Gate cells move to release iff EQUIVALENT and B MET x2.
- Comparison (reported): GL8A/B on 8249193ed041, 39.26/40.23 and 39.35/40.29. Whole-run here includes ags 0354's stdout commit in the
  pre-loop (about -39.26 x C / 127400 for C ms); steady and stall_ms do not. DOSAGS_XT load bracket reported (GL8A 212 -> 630 ms).
- Both arms carry 0269 (SDL_DOSOpl3WriteRegister), so the ABBA cannot isolate it. Prediction: B >= A on both tick figures; all MET.
- Round R1: WARMUPR1, R1I1, R1R1, R1R2, R1I2, CAPR8; one power-on, cap 80 min; dated 2026-11-05, else re-dated first.
