# Round RF -- 2026-11-09: ags 0371's L1 (DOSAGS_ROUTE_PREWARM) on the 486 -- the warm works (room-2 click 370 -> 122 ms, stall_ticks 3 -> 2) but skips barely move: P1 FALSIFIED (pair 2), P2 MET at +0.06 points, P3 FALSIFIED by 2.5 ms, P4 MET; the reason is the pacer: a debt over 5 ticks is forgiven, a smaller one is repaid at ~7 ms per skipped frame

One power-on: relay-on 15:04:06Z, power OFF 16:31:45Z (driver exit 0; driver-started powerguard confirmed OFF 16:31:49Z, no
"fired DURING cell" line), cap 16:54:06Z not reached; vcctrld daemon_start_t unchanged (1793979061.92). Operator, directly
(question tool): "Power on now (Recommended)", after sdlports' shape check of 51e7cb41 (+ amendment 90b25205 and the RFB1 need
fix) and vcctrl's pre-check (rig clear 15:03Z). Budget line: need 5340 s after the warm-up vs 110 x 60 - 630 - 240 = 5730 s; every
cell ran. Every cell exit 0, stamp OK (rfrel 8c123c770d0b, rfins 01658435489c), pre = staged = post; BLASTER.TXT "A220 I7 D3 P330
T3"; every witness line as registered (STDOUT "routeprewarm DOSAGS_ROUTE_PREWARM=(default) mode=0" in A and RFP0, "=1 mode=1" in
B, RFMP and RFP1; "guictrlmark ...=(default) mode=0", "charreuse ...=(default) mode=2", "guiclip ...=(default) mode=4" in every
cell; boxed > 0 in every MMD cell; routeprewarm_final prewarms 0 in A / RFP0, 2 in B / RFMP, 1 in RFP1). Camera sheets show play
in every cell (room 1 -> room 2 in the MMD cells; room 3 in RFP0 / RFP1), including RFA1: the bench camera's warm-up shot at
15:05:57Z was black (the operator fixed the monitor at the bench during the round, on my question), but the cells' own camera
frames are lit throughout. No recovery.
Binaries: RFREL = main 35d1135f release 8c123c770d0b (sha256 5af21f2a...), RFINS = instrumented 01658435489c (234b5626...), both
build_dirty=0 and hash-identical to the reviewed L2REL / L2INS (ags 0001-0372; 0371 and 0372 default off; R2 default on).

| Cell | arm | displayed (1 - skipped/ticks) | room 1 + entry 5480-8400 | room 2 8400-9500 | late 9500-end | stall_ticks (tick_stall ms) | warm us (max) |
|---|---|---|---|---|---|---|---|
| RFA1 | A (unset) | 98.89% (78 of 7,003) | 49 | 4 | 17 | 3 (2006 / 3835 / 378) | -- |
| RFB1 | B (=1) | **99.03%** (68) | 47 | 0 | 13 | **2** (2121 / 4036) | 358,184 (247,476) |
| RFB2 | B (=1) | 98.93% (75) | 55 | 7 | 5 | **2** (2122 / 4093) | 357,911 (247,210) |
| RFA2 | A (unset) | 98.94% (74) | 49 | 4 | 13 | 3 (2007 / 3778 / 354) | -- |
| RFMP | B (=1), instrumented | 98.61% (97; fine timing on) | 63 | 4 | 22 | 2 (2128 / 4072) | 359,251 (247,744) |
| RFP0 | S32P, unset | 99.54% (23 of 4,999); 39.38 / 40.16 | -- | -- | -- | 2 | -- |
| RFP1 | S32P, =1 | 99.52% (24); 39.41 / 40.11 | -- | -- | -- | 3 | 105,719 |

Windows: ROUNDRD's rule (rescore.py, WINDOWS.txt; only room 1 + entry, room 2 and late were registered -- WINDOWS.txt's room1 /
entry split at 7890 is post-data reporting); per-second bursts: PERSEC-SKIPS.txt; per-click logic and tick rows: CLICKS.txt
(clicks.py, docs/lab/rb-lab/ticks.py's reader). Audio in every cell: underruns 0, overwrites 0. catchup resyncs 0 everywhere.

## P1 (per pair, room 1 + entry): FALSIFIED
Registered: B has 6 fewer skips than A (band 3-9); falsified if either pair has < 2 fewer. Pair 1 RFA1 49 -> RFB1 47 (2 fewer: at
the edge, not below it); pair 2 RFA2 49 -> RFB2 55 (**6 more**). The falsifier trips on pair 2.

## P2 (whole run): MET
Registered: mean(B) - mean(A) = +0.09 points (band +0.04 to +0.13); falsified if < +0.02, or if a B cell's late window is > 5
skips worse than its A. Measured: (99.03 + 98.93) / 2 - (98.89 + 98.94) / 2 = **+0.06 points** (76 -> 71.5 skips per run); late
windows B 13 vs A 17, B 5 vs A 13 (B better in both). In the band, but the gain rests on pair 1: whole run, pair 1 is B 68
vs A 78 (+0.14 points) and pair 2 is B 75 vs A 74 (-0.01 points). With P1 falsified and n = 2, this is not a consistent gain.

## P3 (RFMP, mechanism): FALSIFIED by 2.5 ms on the room-2 click; the restore click MET
Logic (ugo - scene - render) of the first room click after the restore: **74.6 ms** (registered <= 80; RDMP 232.7). Of the first
room-2 click (room 2 entered at 7772, click at 7990): **122.5 ms** (registered <= 100, falsified if > 120; RDMP 7895: 369.7).
The warm cut that click by 247 ms, but a warm route search on the 486 still costs ~120-130 ms: RDMP's warm room-1 click 7315 read
127.1 and RFMP's 7469 reads 126.6 (LAB-RB 3.2's "warm 131 ms"). The <= 100 bar was set below the known warm cost; the miss is the
prediction's, recorded as registered.

## P4 (stall edge): MET
B cells and RFMP log stall_ticks 2 with no ~350-380 ms entry; A cells log 3 (378, 354 ms). The first room-2 click left the stall
list, as predicted.

## Why the skips did not follow the logic (information; CLICKS.txt rows, and 0047's dos_run_tick_fixed)
The pacer computes owed = expected - actual once per call, runs min(owed, 5) catch-up ticks with render and wait suppressed, and
REBASES the epoch if owed is still > 0 (the debt beyond 5 ticks is dropped). A catch-up tick in MMD still costs 16-20 ms of logic
on the 486 (the rows' "s17", "s19"), so each skipped frame repays only ~6-8 ms of a 25 ms budget. Two consequences, both visible:
- A tick long enough that owed > 5 (over ~150 ms) costs 5 skips and is then forgiven. RDMP's 369.7 ms room-2 click: 5 skips, a
  rebase, then ~1 skip per following GUI tick -- 10 skips over 7896-7910.
- A tick under the clamp is repaid in full at ~7 ms per skip. RFMP's 122.5 ms room-2 click (owed 4): 4 skips, still behind,
  4 more after the 53 ms GUI tick, 4 more after the next -- **19 skips** over 7991-8015.
- The restore click: RDMP 232.7 ms -> 7 skips; RFMP 74.6 ms -> 7 skips (2 owed, then the two 50 ms GUI ticks that follow a
  click, each scene 24-25 ms).
So L1 turned a forgiven 370 ms debt into a repaid 125 ms one: more skips at that click, not fewer, and the restore click broke even.
This accounts for P1's miss without a lab run; it is read from the rows and the code, not yet reproduced in the lab. It also
fits round RE's 0163 result (ticks over 250 ms were already forgiven by the clamp). For the campaign it means a click or spike
only stops costing skips when its tick gets near the 25 ms budget (or when the pacer forgives it), and the post-click GUI ticks
(scene 24-26 ms, L2's target) are a steady part of every click's cost.

## Warm cost and the S32P pair (information)
The warm took 358 ms per MMD run: 247 ms in the room-2 load (LAB-L1R section 7 predicted 77-170 ms per warm) and ~111 ms in the
restore; the stall ticks grew by the same (restore 2006 -> 2121, room-2 load ~3.8 s -> ~4.1 s). On S32P the room-3 warm took 106 ms
(in band). RFP0 / RFP1 whole-run 39.38 / 39.41, steady 40.16 / 40.11, 99.54 / 99.52%, audio clean, camera CLEAN: both above the
39.2 floor. Per the amendment (90b25205), this one pair checks the floor only; the +0.03 between the cells is not evidence about the
warm's cost.

## Campaign line (>= 99% x2): not met
B cells 99.03 / 98.93; the A cells (98.89 / 98.94) ran 0.1-0.17 below round RE's default cells of the same morning (98.97-99.06)
on a different binary (0372's release vs 0370's, both with these levers off; P9-equal in the lab).

## Rig (vcctrl)
Capture stick: one USB drop during RFB2 at 15:44:38Z (uvcvideo EPROTO, disconnect), re-enumerated by itself 15:44:40.75Z, no
port cycle; video back by 15:44:41Z; rig audio capture out 15:44:38-46Z (RFB2's .ogg has the gap; the engine's own audio counters
are clean). The first drop since round R2. 4 corrupt capture frames (decode_errs 105 -> 115), all black, all at a launch or exit:
16:04:01Z (RFMP launch), 16:10:34Z (RFMP exit), 16:24:53Z (RFP1 launch), 16:27:02Z (RFP1 exit). capture=STALE in WARMUPRF and the
MMD cells (the stick never locks that mode); capture=ok in RFP0 / RFP1, the first time the stick has locked 5 Days. Bench camera:
black at 15:05:57Z, readable again by 15:34:02Z; no password in any shot. jobs/ was not collected.

Files: SUMMARY.txt, driveRF.sh / cellRF.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt + rescore.py, PERSEC-SKIPS.txt + persec.py, CLICKS.txt + clicks.py; RFP0 / RFP1 GATEBAR.txt. Captures and saves stay
local (AUDIO-SHA256.txt, SAVE-SHA256.txt in each cell).

## Note (2026-11-11, information only; not a verdict change)
Board partial packets (USB4VC 0.5.107 abandoned a partly sent PS/2 packet, leaving the mouse out of frame for the rest of a cell;
lab-rb LAB-MOVE 10.12, move-lab/rj/ARM-PARTIALS.txt): 3 of RF's 4 cells carry an in-play partial, so later clicks in those cells
may have landed on the verb bar and changed their GUI ticks; P2's +0.06 points, already resting on pair 1, carries that noise too.
Across rounds RC-RG, cells with an in-play partial are 6 / 12 (A) vs 5 / 12 (B): unbiased by arm, as far as 2-vs-2 can tell.
