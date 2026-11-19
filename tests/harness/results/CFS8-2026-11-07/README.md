# CFS8 -- Trilby's Notes S8 (room 35) on the clean landed build, R1 by default (written 2026-11-07; pre-registration, before any data)
- Binary: CFREL.EXE = main 90083fe6 release (ags 0001-0367), stamp 54d439f88378, build_dirty=0, 8,649,343 B, sha256 7770f865...;
  byte-identical to the reviewed LAND2REL (cmp -l: 0 differing bytes). VOID if the staged stamp differs. BLASTER.TXT "A220 I7 D3 P330 T3".
- R1 witness (no env: R1 is the default): STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=2", RUNMANI guiclip_final mode=2,
  else VOID. latch_fullrestore= is a scored field in every cell: expected 0; any value > 0 is the guard's first natural firing (a finding).
- Fixture: R1R1's S8 line verbatim (as D8S8): --startr 35, ACSETUP-ON 512x384 round cfg, DOSAGS_MSGSKIP=1, TAS 5000. R1 does
  not engage here (landing regression: flagged 835, all drawn in full); skipped > 0 is a finding.
- Scorer: gatebar.py --label S8 --stamp 54d439f88378 --room 35 --msgskip (one cell). Bar (PLAN-GATES, unchanged) as S16.
- Prediction: MET -- whole 39.25-39.40, steady 40.0-40.3, displayed 99.1-99.5% (D8S8 39.37 / 40.23 / 99.28).
  Falsifier: NOT MET = the landed build regresses S8. Witness: the camera sheet (room 35 is dark).
- Round CF (R1 confirmation on the clean landed build; operator via sdlports: "a confirmation round on the clean release build"; S16/S32P/S8 gate cells + P9 fixture x2 + CFMP): WARMUPCF, CFS16, CFS32, CFS8, CFM1, CFM2, CFMP; one power-on, cap 100 min; dated 2026-11-07.
