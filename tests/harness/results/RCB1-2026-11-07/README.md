# RCB1 -- MMD IN PLAY, arm B (R3, default), R3 ABBA cell (written 2026-11-07; pre-registration, before any data)
- Binary: RCREL.EXE = main 9e54b6d9 release (ags 0001-0368), stamp 4c9f83b62c5c, build_dirty=0, sha256 7deb7ca9...; byte-identical
  to the reviewed R3REL (cmp -l: 0 differing bytes; stamp = hash of build inputs). VOID if the staged stamp differs. BLASTER.TXT.
- Arm B (R3, the default): no env; STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4" and boxed > 0, else VOID.
- Fixture: P9M1's line verbatim (as CFM1/CFM2: AGSSAVE.007 f486d0e9..., DRIVE 5 host clicks, TAS 12440, sound ON cfg). Witness:
  the camera sheet shows play (room 1 -> 2), else VOID. Score as CF: displayed = 1 - frames_skipped/ticks; late stretch = renders /
  ticks over loop ticks 9500-end from the persec lines; guiclip_final raw line (incl. boxed, fb_coarse, fb_whole, latch_fullrestore).
- ABBA (RCA1 RCB1 RCB2 RCA2, one binary, only the env differs). LAB-R3 section 3's bands, registered before any R3 data, verbatim:
  (a) late stretch, R3 cells: central 97%, band 93-100%; FALSIFIED if either R3 cell < 92% renders/ticks over 9500-end, or less
  than +10 points over its same-binary R1-only arm in that stretch. (b) whole fixture, R3 cells: central 96.5%, band 94.0-98.5%;
  FALSIFIED if either R3 cell < 93%, or mean(R3) - mean(R1) < +4 points. R1 arms expected at CF's 88.1% (86.0-92.0). 99% x2 is
  NOT predicted (remainder: room 1 = R2, the room-2 entry, clicks).
- Round RC (R3 = ags 0368, default since main 9e54b6d9, to the 486 + round SW1's save-trace pair first, one power-on; sdlports' design 2026-11-07): WARMUPRC, SW1TA, SW1TB, RCA1 RCB1 RCB2 RCA2, RCMP, RCS16 (first to drop); cap 115 min; dated 2026-11-07.
