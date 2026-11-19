# CFS32 -- 5 Days S32P on the clean landed build, R1 by default (written 2026-11-07; pre-registration, before any data)
- Binary: CFREL.EXE = main 90083fe6 release (ags 0001-0367), stamp 54d439f88378, build_dirty=0, 8,649,343 B, sha256 7770f865...;
  byte-identical to the reviewed LAND2REL (cmp -l: 0 differing bytes). VOID if the staged stamp differs. BLASTER.TXT "A220 I7 D3 P330 T3".
- R1 witness (no env: R1 is the default): STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=2", RUNMANI guiclip_final mode=2,
  else VOID. latch_fullrestore= is a scored field in every cell: expected 0; any value > 0 is the guard's first natural firing (a finding).
- Fixture: GR32P's line verbatim (as D8S32): 5days --startr 3, S32P-ACSETUP-ON.CFG (24d874f2...), FORCE_COLOR_DEPTH=32
  MAX_SCALE=1 PACK24=1, direct framebuffer, TAS 5000. R1 engagement here is not predicted (information: flagged / skipped).
- Scorer: gatebar.py --label S32 --stamp 54d439f88378 --room 3 (one cell). Bar (PLAN-GATES, unchanged) as S16.
- Prediction: MET -- whole 39.30-39.45, steady 40.0-40.3, displayed 99.3-99.6% (D8S32 39.40 / 40.17 / 99.52; GR32P 39.29 / 40.12).
  Falsifier: NOT MET = the landed build regresses S32P. Witness: the capture sheet (640x480), camera as backup.
- Round CF (R1 confirmation on the clean landed build; operator via sdlports: "a confirmation round on the clean release build"; S16/S32P/S8 gate cells + P9 fixture x2 + CFMP): WARMUPCF, CFS16, CFS32, CFS8, CFM1, CFM2, CFMP; one power-on, cap 100 min; dated 2026-11-07.
