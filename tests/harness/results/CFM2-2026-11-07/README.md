# CFM2 -- MMD IN PLAY on the clean landed build, R1 by default, cell 2 of 2 (written 2026-11-07; pre-registration, before any data)
- Binary: CFREL.EXE = main 90083fe6 release (ags 0001-0367), stamp 54d439f88378, build_dirty=0, 8,649,343 B, sha256 7770f865...;
  byte-identical to the reviewed LAND2REL (cmp -l: 0 differing bytes). VOID if the staged stamp differs. BLASTER.TXT "A220 I7 D3 P330 T3".
- R1 witness (no env: R1 is the default): STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=2", RUNMANI guiclip_final mode=2,
  else VOID. latch_fullrestore= is a scored field in every cell: expected 0; any value > 0 is the guard's first natural firing (a finding).
- Here R1 must engage: guiclip_final skipped > 0, else VOID.
- Fixture: P9M1's line verbatim, as GCB1/GCB2 without the env (AGSSAVE.007 sha256 f486d0e9... restores room 1; DRIVE 5 host
  clicks; TAS 12440; sound ON cfg). Score as GC: displayed = 1 - frames_skipped/ticks (tick_rate_steady's ticks=), steady,
  fps_p50, rooms, stalls. Witness: the camera sheet shows play (kids walk, room 1 -> 2), else VOID.
- Prediction (against GC's lab binary, GCB1 88.72% / GCB2 89.30%, mean 89.01): each cell 86.0-92.0% displayed, central 89.0;
  steady 39.2-40.8. CONFIRMED if both cells are in band and |mean(CFM1, CFM2) - 89.01| <= 2.5 points. Falsifier: either cell
  outside 86.0-92.0%. 99% is not claimed (campaign line reported). Only a CONFIRMED pair lets the hub quote R1's gain.
- Round CF (R1 confirmation on the clean landed build; operator via sdlports: "a confirmation round on the clean release build"; S16/S32P/S8 gate cells + P9 fixture x2 + CFMP): WARMUPCF, CFS16, CFS32, CFS8, CFM1, CFM2, CFMP; one power-on, cap 100 min; dated 2026-11-07.
