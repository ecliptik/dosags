# RDB2 -- MMD IN PLAY, arm B (R2, =2), R2 ABBA cell (written 2026-11-08; pre-registration, before any data)
- Binary: RDREL.EXE = main 1e3609c2 release (ags 0001-0369), stamp 84c1a74fdcf6, build_dirty=0, sha256 ffe49dab...; byte-identical
  to the reviewed R2REL (cmp: 0 differing bytes; stamp = hash of build inputs). VOID if the staged stamp differs. BLASTER.TXT.
- Arm B (R2): SET DOSAGS_CHAR_REUSE=2; STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=2 mode=2" and "DOS-PORT guiclip
  DOSAGS_GUI_CLIP=(default) mode=4"; charreuse_final skips > 0 and boxed > 0, else VOID.
- Fixture: P9M1's line verbatim (as RCA1..RCA2: AGSSAVE.007 f486d0e9..., DRIVE 5 host clicks, TAS 12440, sound ON cfg). Witness:
  the camera sheet shows play (room 1 -> 2), else VOID. Score as RC: displayed = 1 - frames_skipped/ticks; per-window skips from the
  persec lines (room 1 5480-7890, entry 7890-8400, room 2 8400-9500, late 9500-end); raw guiclip_final and charreuse_final lines.
- ABBA (RDA1 RDB1 RDB2 RDA2, one binary, only the env differs; pairs RDA1/RDB1 and RDB2/RDA2). docs/lab/R2-FORECAST.md's bands,
  registered before any R2 data, verbatim:
  F1 (room 1): "R2 cells' room-1 skips 20-40 (central 30), i.e. room 1 98.3-99.2% (central 98.8). Falsifier: either R2 cell's
  room-1 skips > 50, or less than 25 fewer than its same-binary R3-only arm (DOSAGS env toggle, ABBA) in that window."
  F2 (whole fixture): "R2 cells 98.9-99.5% displayed (central 99.1; 35-77 skips). Falsifier: either R2 cell < 98.6%, or
  mean(R2) - mean(R3-only) < +0.5 points. 99% x2 is ON THE EDGE of this band, not claimed."
  F3 (mechanism, per room): "entry, room 2 and late windows each within +-10 skips of the R3-only arm ...; a > 10-skip gain
  there is a finding, a loss falsifies." R3-only arms expected at RCB1 / RCB2's 98.43 / 98.24% (room 1 79 / 75 skips).
- Round RD (R2 = ags 0369, DOSAGS_CHAR_REUSE=2 on the R3 default, vs R3-only, to the 486, one power-on; sdlports' design 2026-11-08, LAB-R2B section 7): WARMUPRD, RDA1 RDB1 RDB2 RDA2, RDMP, RDS16 (first to drop); cap 100 min; dated 2026-11-08.
  Budget line: need at RDA1 (the ABBA block) 3040 s, whole round after the warm-up 4580 s (3040 + RDMP 780 + RDS16 760), vs
  CAP_MIN 100 x 60 - warm-up 630 - 240 = 5130 s available.
