# Round G1 -- 2026-11-06: GUSS0 as predicted (gus-pcm-fix holds on hardware); GUSS1 VOID (stray keystroke); ADLC16R/MPUNB16 not run

One power-on 02:39:42Z-03:43:35Z; the driver stopped after GUSS1 (run-hw exit 1) and powered off (powerguard confirmed).
Operator's standing order + "fix both before v0.1" (ORDER-CONFIRMED). Pre-registrations f665bb42. vcctrl: no USB event, the
audio stream never restarted; 2 corrupt video frames (02:46:29Z warm-up, 03:29:45Z after GUSS1's game window).

| Cell | Binary | Result |
|---|---|---|
| WARMUPG1 | l308 | 29.69 / 32.98, BLASTER OK; close-watch passed |
| GUSS0 | lab S0 854228747226 (no SDL 0270), PGGUS | valid; capture-check3 **K3 FAIL** (sound 3 logged x2, not found: 0.40 vs null 0.43) -- as predicted; K2 FAIL (1.98 s), M1 -24 cents, M2 0.472 vs 0.616; K1, K4 PASS. **underruns=0** (GUSC16: 39,631) and "DOS-PORT gusstreams opens=2 open_failures=0 reuses=7": the hub gus-pcm-fix (6f3f66e+f2515cf) + dosags 0356-0358 hold on the real PicoGUS |
| GUSS1 | lab S1 2d00e8b416f0 (SDL 0270) | **VOID -- rig input fault, no evidence about 0270**: the witness frame (witness/BADCOMMAND-00003.jpg) shows "C:\>3CD C:\DOSAGS -- Bad command or file name" then "C:\>RUN.BAT -- Bad command or file name": a stray "3" from the boot-profile selection (attempt 1 missed, attempt 2 landed) was prepended to the first typed command, so AGS.EXE never ran (the card's STDOUT.TXT was still GUSS0's, byte-identical; no GUSS1.LOG). run-hw retried collection to its 1800 s budget, exit 1; the driver stopped the round |
| ADLC16R, MPUNB16 | release 340584af1155 | not run (round stopped after GUSS1) |

Pre-registered DC-mean check: not usable on the rig -- the line-out-to-capture path is AC-coupled (GUSS0 capture mean 0.0,
whereas DOSBox-X's digital capture read -11,804). K3 alone decides the sign question.

Next (G2): GUSS0/GUSS1 re-run as a pair in one power-on with new tags, plus ADLC16R/MPUNB16, after the stray-key fault is
fixed (reported to vcctrl) or guarded (every --boot-profile cell's witness checked for "Bad command" -> VOID).
