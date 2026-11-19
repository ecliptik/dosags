# Round RI -- 2026-11-11: the DRIVE 6 calibration gate STOPPED on C10 (small-packet linearity), so no MS3 cell ran; every quantity the play path uses PASSED directly (DXL / DXA / DXB at exactly 3.000 px per count with 0 px residual, DY y 120 over 46 repeats, corners, clip), and the one-call press ran 61 / 61 with 0 errors; P9M1 cells 99.00 / 98.70%, both touched by a DRIVE 5 mouse drop, so no bridge this round

One power-on: relay-on 19:56:41Z, power OFF 20:40:09Z (driver exit 0; driver-started powerguard confirmed OFF 20:40:13Z, no
"fired DURING cell" line), cap 21:56:41Z not reached; vcctrld daemon_start_t unchanged across the round (1794424802.12; vcctrld
was restarted at 19:20:01Z, before the round, for vcctrl 9bad5fd's `mouse press`). Operator, directly (question tool): "Power
on now (Recommended)", after sdlports' shape check of dc0337b8 (harness 8be9d05f + 5bfb2baa) and vcctrl's pre-check (rig clear,
watches armed 19:56Z; warm-up camera shot 19:57:41Z lit and readable, no password). Every cell that ran exited 0 with stamp OK
(8c123c770d0b), pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; witness lines as registered.

| Cell | what | result |
|---|---|---|
| WARMUPRI | warm-up | exit 0; BLASTER ok; capture locked after |
| RICAL | DRIVE 6 calibration (gated) | **GATE STOP C10**: "prelude: one-packet sizes off one line by 4.5 px (> 2)" |
| RICAL2 | conditional re-centre | not run (STOP, not RECENTRE) |
| RIM1..RIM4 | MS3 baseline | **not run**: "MS3 block not run: DRIVE 6 calibration did not PASS (20:17:40)", as registered |
| RIP1 | P9M1 bridge, DRIVE 5 | 99.00% (70 of 7,003); a DRIVE 5 mouse drop at 20:25:09Z (below) |
| RIP2 | P9M1 bridge, DRIVE 5 | 98.70% (91 of 7,003); a DRIVE 5 mouse drop at 20:35:55Z (below) |
| RIMP | instrumented MS3 | not run (needs a calibration PASS), as registered |

The gate did what was registered: no MS3 cell ran on a calibration that did not PASS. Nothing here is re-read under rules
written after this round's data.

## RICAL (tests/harness/results/RICAL-2026-11-11/CAL-RESULT.txt, GATE.txt)
- **Press path (the first live `mouse press` with the Gateway on):** DRIVE-WALK.LOG "presses planned / sent: 61"; 61 / 61 presses
  `press=one rc_press=0 ok=1`, dwell_s 0.2 on all 61 (no click_hold_s floor), late max 0.03 s. First press, as logged:
  `click 1 CAL-MX=88 ... press=one rc_press=0 ok=1 failed_at=- dwell_s=0.2 elapsed_ms=459 wall_ms=549`; its input-log
  record: `mouse_press ok true ms 459.1 detail "left dwell=0.2 moves=-127,-127 -127,-127 127,127 -88,15"`. The full JSON
  reply (per-step t_ms, release) is not stored by drive-walk6.sh; vcctrl's input log saw 59 mouse_press + the two slow
  probes' separate calls, all ok, 0 cmd.error / input.refused / mouse.dropped, daemon latency 425-512 ms (median 472); USB4VC
  counters unchanged across RICAL.
- **Passed, everything the play path uses:** 61 walks for 61 presses, rooms [1, 2], no GUI click; corners x 319 / 0; the
  200-count probe at x 75 (clip, not carry); bottom bound 383 (as predicted); DXL x = -96 + 3.000 d, DXA / DXB x = 415 - 3.000 d,
  each 0.0 px residual, landing exactly 60 / 190 / 289 at the model's centres 52 / 75 / 42; DY at 15 -> y 120 on 46 repeats
  (spread 1). The pointer model (drive6-pointer.py) holds for every packet size the play path sends.
- **Failed C10 (registered STOP):** one 8-count x packet landed x 269 (2.50 px per count, 4.5 px off the 20-88 count line), and
  16 y counts sent as 4 slow 4-count packets landed y 106 against 122 for one 16-count packet. The DY sweep's line read slope
  1.866 (model 1.5; inside C9) because its 8-11-count points sit low.
- **Records note:** while testing the follow-up harness, the lab agent ran the gate directly on this cell's dir and overwrote
  CAL-RESULT.txt and GATE.txt (not yet committed), then regenerated them with main's unchanged gate on the same inputs. Re-run here
  on a copy of STDOUT.TXT and DRIVE-WALK.LOG with main 5bfb2baa's gate: both files are byte-identical to the committed ones; the
  driver's SUMMARY line, written at run time, carries the same gate line.
- **Follow-up (information, not a re-reading of this cell):** the lab fitted the small-packet loss to one rule (a packet of
  <= 9 counts loses 8/3 counts, 10 loses 2, 11 loses 1, 12 and up none; all 19 small points within 1 px) upstream of INT 33h,
  and proposes C10 on packets >= 12 counts only, with a short re-check cell (drive6e 9ea1126c). That is for the next round's
  pre-registration and sdlports' review; this round's verdict stays STOP.

## Bridge pair (P9M1, DRIVE 5, default config): 99.00 / 98.70%
| Cell | displayed | room 1 + entry | room 2 | late | catchup ticks / events / clamped | stall_ticks | audio | GUI clicks logged |
|---|---|---|---|---|---|---|---|---|
| RIP1 | 99.00% (70) | 49 | 5 | 8 | 70 / 40 / 5 | 3 | 0 / 0 | 14 |
| RIP2 | 98.70% (91) | 50 | 13 | 20 | 91 / 47 / 4 | 3 | 0 / 0 | 12 |

Inside the registered 98.5-99.3% (no day-drift flag). Walk targets in both equal every earlier DRIVE 5 run's (204,98 319,98
34,128 0,128 925,69). Both cells had a PS/2 mouse drop in DRIVE 5's separate move / down / up calls (vcctrl): RIP1 at 20:25:09Z
(a partial / timed-out packet, probably the up edge: a ~6 s hold) and RIP2 at 20:35:55Z (partial / timed-out, then an edge
merge: probably a lost click). The game logs agree that each drop changed the clicks the game saw: RIP1 logged 14 "Mouse click
over GUI" lines and RIP2 12, against 13 in both of round RH's bridge cells for the same 29 / 30 presses. Under sdlports' rule,
both bridge cells are information only: **this round has no bridge.** The walk targets were not moved. Timing note: the pair ran ~10-25
min after the warm-up, not 65-75 as registered, because the MS3 block did not run.

## Rig (vcctrl)
No USB event on the capture stick (device 80; the second clean round in a row). 3 corrupt capture frames (decode_errs 0 -> 8,
reads deduplicated): 20:10:50Z (black, RICAL launch), 20:26:49Z (not black: a dark AGS scene still on screen 9 s after RIP1's
reboot chord, a slow POST blank; its JPEG broke mid-stream) and 20:33:09Z (black, RIP2 launch). Mouse: pkt_timeout
/ partial and edge_merged rose only with the two DRIVE 5 drops above (plus one at power-on, attributed by vcctrl to its own
19:22Z deploy-check press); 0 drops on the mouse_press path (61 presses). jobs/ not collected.

Files: SUMMARY.txt, driveRI.sh / cellRI.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt; RICAL's DRIVE-WALK.LOG, CAL-RESULT.txt, GATE.txt. Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt in
each cell).
