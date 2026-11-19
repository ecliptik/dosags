# REB2 -- MMD IN PLAY on ags 0370's release, arm B (DOSAGS_STALL_RESYNC=1), 0163 A/B cell (written 2026-11-08, re-dated 2026-11-09; pre-registration, before any data)
- Binary: REREL.EXE = main 4ee5b017 release (ags 0001-0370), stamp 9db4170acd89, build_dirty=0, sha256 f9202de6...; byte-identical
  to the reviewed R2DREL (cmp: 0 differing bytes). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2" and "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default)
  mode=4"; charreuse_final skips > 0 and boxed > 0, else VOID.
- Arm B: SET DOSAGS_STALL_RESYNC=1; the catchup line's resyncs= > 0 (see P2).
- Fixture: P9M1's line verbatim (as RDA1..RDA2: AGSSAVE.007 f486d0e9..., DRIVE 5 host clicks, TAS 12440, sound ON cfg). Witness:
  the camera sheet shows play (room 1 -> 2), else VOID. displayed = 1 - frames_skipped/ticks. Windows (information): room 1 +
  entry as ONE window 5480-8400, room 2 8400-9500, late 9500-end, ticks - renders between the first persec rows at or after each
  edge (ROUNDRD's rule). Raw guiclip_final, charreuse_final and catchup lines.
- 0163 A/B (REA1 REB1 REB2 REA2, one binary, only the env differs; pairs REA1/REB1 and REB2/REA2). A = DOSAGS_STALL_RESYNC
  unset; B = DOSAGS_STALL_RESYNC=1 ("rebase the epoch after a stall tick instead of repaying it"; default OFF since 0163).
  P1 (displayed): per pair, B skips 6-15 fewer than A (central 11), i.e. +0.09 to +0.21 points. FALSIFIED if mean(B) - mean(A)
  < +0.05 points. Basis: LAB-RB Q4 (lab GCL 15 -> 2, H 20 -> 13); RD's R2 cells show stall_ticks 3 and catchup clamped 5.
  P2 (the 250 ms edge): resyncs= on the catchup line counts only ticks over threshold_ms 250. B cells: resyncs == stall_ticks
  (expected 3: the restore, the room 1 -> 2 load, and a > 250 ms click such as RDMP's 7895 at 374 ms); A cells: resyncs 0.
  A B cell with resyncs 0 VOIDs P1. Clicks under 250 ms (RDMP's 6154 at 237 ms) keep their catch-up skips in both arms.
  P3 (tick rates, information): ticks are fixed by TAS 12440, so B's loop_ms runs longer by about resyncs x 125 ms (+0.3 to
  +0.5 s); tick_rate_steady within +-0.05 of A. The whole-run tick_rate of a --loadsavedgame cell carries the save's base and is
  not read.
  P4 (audio clean): underruns 0 and overwrites 0 in every cell, as RD; a B cell with underruns > 0 where its pair's A cell has
  0 FALSIFIES "no audio cost". silent_irqs recorded.
  Note: the rig's DRIVE host clicks are wall-timed, so after each resync they land about 5 ticks later in game time; the room-2
  entry and click ticks may shift between arms. The fixed windows are information; whole-run displayed is P1's measure.
  Drift note (sdlports 2026-11-08): RD's R3-only arms ran 0.5-0.8 points below round RC's; a day's offset of that size is
  expected and is why the confirmation band is wide.
- Round RE (ags 0370 = R2 on by default, confirmation, then patch 0163's DOSAGS_STALL_RESYNC A/B; one power-on; operator's
  decisions 2026-11-08, question tool; shape per sdlports): WARMUPRE, REC1 REC2, RES16, REA1 REB1 REB2 REA2 (the 0163 block drops first); cap 110 min.
  Budget line: need at REC1 (confirmation block) 2280 s; at REA1 (0163 block) 3040 s; whole round after the warm-up 5320 s, vs
  CAP_MIN 110 x 60 - warm-up 630 - 240 = 5730 s available. Staged while the operator's hold on the 486 stands (2026-11-08): this
  round runs only after the operator lifts it, and its dirs, READMEs and the driver's D line are re-dated before any data.

Re-dated 2026-11-09, before any data: the operator lifted the 486 hold ("Okay to power on", 2026-11-09 ~11:54Z). Nothing
else in this pre-registration changed.
