# Round RG -- 2026-11-09: ags 0372's L2 (DOSAGS_GUI_CTRL_MARK) on the 486 -- B fewer skips in all 4 pairs (-10 / -12 / -8 / -2; mean -8 per run, +0.11 points): P1 and P2 not falsified, both ABOVE their bands; campaign pair RGA1 / RGA2 98.89 / 98.81%: NOT MET

One power-on: relay-on 17:06:24Z, power OFF 18:47:00Z (driver exit 0; driver-started powerguard confirmed OFF 18:47:09Z, no
"fired DURING cell" line), cap 19:06:24Z not reached; vcctrld daemon_start_t unchanged (1793979061.92). Operator, directly
(question tool): "Power on now (Recommended)", after sdlports' shape check of 16f00d96 + amendment 21a66664 and vcctrl's
pre-check (rig clear 17:05Z). Budget line: need 6080 s after the warm-up vs 120 x 60 - 630 - 240 = 6330 s; every cell ran. Every
cell exit 0, stamp OK (rgrel 8c123c770d0b), pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; every witness line as
registered (STDOUT "guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=0" in A, "=1 mode=1" in B; "routeprewarm ...=(default)
mode=0", "charreuse ...=(default) mode=2", "guiclip ...=(default) mode=4" in every cell; boxed > 0 everywhere; guictrlmark_final
l2 0 in A, 14 in every B cell). Camera sheets show play in every cell (room 1 -> room 2); the bench monitor was lit from the
warm-up on (vcctrl 17:08:19Z). No recovery.
Binary: RGREL = main 35d1135f release 8c123c770d0b (sha256 5af21f2a...), build_dirty=0, = the reviewed L2REL = round RF's RFREL.

| Pair | A cell | A skips (displayed) | B cell | B skips (displayed) | B - A whole run | room 1 + entry A -> B | late A -> B |
|---|---|---|---|---|---|---|---|
| 1 | RGA1 | 78 (98.89%) | RGB1 | 68 (**99.03%**) | **-10** | 50 -> 45 (-5) | 15 -> 5 |
| 2 | RGA2 | 83 (98.81%) | RGB2 | 71 (98.99%) | **-12** | 49 -> 42 (-7) | 17 -> 17 |
| 3 | RGA3 | 83 (98.81%) | RGB3 | 75 (98.93%) | **-8** | 49 -> 38 (-11) | 21 -> 15 |
| 4 | RGA4 | 79 (98.87%) | RGB4 | 77 (98.90%) | **-2** | 49 -> 40 (-9) | 12 -> 25 |

Room 2 (8400-9500) A / B: 5 / 10, 9 / 4, 5 / 14, 10 / 4. stall_ticks 3 in every cell; catchup clamped 5-6, resyncs 0. Audio in
every cell: underruns 0, overwrites 0 (silent_irqs 41-47). Windows: ROUNDRD's rule (rescore.py, WINDOWS.txt; the room1 / entry
split there is not registered); per-second bursts: PERSEC-SKIPS.txt. Raw lines in each cell's RUNMANI.LOG.

## P1 (room 1 + entry): not falsified; above the band
Registered: B 3 fewer per pair (band 2-5); falsified if the mean over the pairs that ran is < 1 fewer. Measured: -5 / -7 / -11 /
-9, mean **8 fewer** -- above the band (the prediction was too small), every pair in the predicted direction.

## P2 (whole run): not falsified; above the band
Registered: mean(B) - mean(A) = +0.04 points (band +0.03 to +0.07), falsified if < 0. Measured: mean(A) 80.75 skips (98.85%),
mean(B) 72.75 (98.96%): **+0.11 points** (8 skips per run). Per pair: +0.14 / +0.17 / +0.11 / +0.03 points. All four pairs favour B
(a 4-of-4 sign; the registered power line put the mean's SE at ~4 skips, so -8 is about two SEs). Information (registered): RGB4's
late window is 13 skips worse than RGA4's (25 vs 12), over the 5-skip mark; its pair is still -2 whole run.
- Information (sdlports): B is not better in every window. Room 2 went the other way in pairs 1 and 3 (B 10 vs A 5, B 14 vs
  A 5), and RGB4's late window is +13 (above). B is better on the whole run and in room 1 + entry in every pair.
- Why larger than predicted (information, not tested here): LAB-L2G's estimate counted ~1-2 skips per action-label flip tick. Round
  RF's reading of the pacer says a flip tick's overrun is repaid at ~7 ms per skip unless forgiven, and L2 engaged 14 times per run;
  10 ms x 14 flips is ~140 ms of debt, ~20 skips at 7 ms, so a few to ~8 skips saved is in reach. No instrumented cell this round,
  so the flip-tick timing itself is not measured on the 486.

## Campaign confirmation pair (registered: RGA1 and RGA2 both >= 99.0%): NOT MET
RGA1 98.89% (78 skips), RGA2 98.81% (83); 99.0% allows 70. The default-config A cells (98.81-98.89) ran below round RE's
default cells of the morning (98.97-99.06) on a different binary (0372's release vs 0370's, levers off), as round RF's did
(98.89 / 98.94). The A cells' 78-83 skips ran ~10 above round RE's default cells (66-72): a day drift of that size sits
beside this NOT MET. Even with L2 on, this day would not have met it: the B cells read 99.03 / 98.99 / 98.93 / 98.90%.

## Rig (vcctrl)
No USB or uvcvideo kernel event 17:03Z to the end; stick present, 0 port cycles. 5 corrupt capture frames (decode_errs 115 ->
129, each read 2-3 times), all black, each at a RUN.BAT launch (~4.3 min into its cell): 17:11:58Z WARMUPRG, 17:54:57Z RGA2,
18:17:35Z RGB3, 18:28:48Z RGB4, 18:39:57Z RGA4. capture=STALE in every cell (the stick never locks MMD's mode); the camera is the
play witness and was lit and readable from 17:08:19Z; no password in any shot. jobs/ was not collected.

Files: SUMMARY.txt, driveRG.sh / cellRG.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt + rescore.py, PERSEC-SKIPS.txt + persec.py. Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt in each
cell).

## Note (2026-11-11, information only; not a verdict change)
Board partial packets (USB4VC 0.5.107 abandoned a partly sent PS/2 packet, leaving the mouse out of frame for the rest of a cell;
lab-rb LAB-MOVE 10.12, move-lab/rj/ARM-PARTIALS.txt): RGA4 had an in-play partial at click 12, before the late window, in pair 4
(already -2, the smallest pair); its later clicks may have landed on the verb bar and changed GUI ticks. Across rounds RC-RG,
cells with an in-play partial are 6 / 12 (A) vs 5 / 12 (B): unbiased by arm, as far as 2-vs-2 can tell.
