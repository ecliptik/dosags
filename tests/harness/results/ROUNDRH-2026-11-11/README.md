# Round RH -- 2026-11-11: the DRIVE 6 calibration gate STOPPED the round before any MS3 cell (a harness bug: drive-walk6.sh sent 1 press of 40 because vcctrl swallowed the schedule on stdin; fixed in 8ce6fb19); its one press shows the pointer model is wrong (y 39, predicted 125-130); the P9M1 bridge pair ran: 98.91 / 98.80%

One power-on: relay-on 17:30:19Z, power OFF 18:14:00Z (driver exit 0; driver-started powerguard confirmed OFF 18:14:02Z, no
"fired DURING cell" line), cap 19:30:19Z not reached; vcctrld daemon_start_t unchanged (1793979061.92). Operator, directly
(question tool): "Power on now (Recommended)", after sdlports' shape check of b7a03d2a + amendment 1bf77e03 and vcctrl's
pre-check (rig clear 17:29Z; watches armed 17:31Z; warm-up camera shot 17:31:18Z lit and readable, no password). Every cell
that ran exited 0 with stamp OK (8c123c770d0b), pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; witness lines as
registered (charreuse (default) mode=2, guiclip mode=4, routeprewarm (default) mode=0, guictrlmark (default) mode=0).

| Cell | what | result |
|---|---|---|
| WARMUPRH | warm-up | exit 0; BLASTER ok; capture locked after |
| RHCAL | DRIVE 6 calibration (gated) | **GATE STOP C1**: rooms entered [1], want [1, 2]. The driver sent 1 press of 40 (below) |
| RHCAL2 | conditional re-centre | not run (the gate said STOP, not RECENTRE) |
| RHM1..RHM4 | MS3 baseline | **not run**: "MS3 block not run: DRIVE 6 calibration did not PASS (17:51:22)", as registered |
| RHP1 | P9M1 bridge, DRIVE 5 | 98.91% (76 of 7,003) |
| RHP2 | P9M1 bridge, DRIVE 5 | 98.80% (84 of 7,003) |
| RHMP | instrumented MS3 | not run (needs a calibration PASS), as registered |

The gate did what it was registered to do: no MS3 cell ran on an uncalibrated drive, and the bridge still ran.

## RHCAL: why only one press (a harness defect, now fixed)
DRIVE-WALK.LOG: the lock was taken at 17:44:22Z, then "click 1 CAL-C ... rc_down=0 rc_up=0" at 17:45:03Z, then "done: 1 presses".
vcctrl's input log agrees (2 mouse_move, 1 down, 1 up, 2 release-all, all ok; usb4vc ev_in +4, no error counter moved; no
stuck button). Cause: drive-walk6.sh's schedule loop is fed by `<<<"$SCHED"`, and every vcctrl call went through bin/vcctrl,
an ssh wrapper that forwards the caller's stdin (vcctrl's finding), so the first press's `mouse down` read the rest of the
schedule and the loop ended. DRIVE 5's drive-walk.sh loops on a counter and never hit it; the stub vcctrl used in testing
ignored stdin. Fix: main 8ce6fb19 (every vcctrl call in drive-walk6.sh reads /dev/null), verified with a stdin-reading stub:
the old script stops at 1 press, the fixed one sends 40 (cal) and 114 presses / 341 moves (ms). vcctrl is also fixing the
wrapper (ssh -n unless the command needs stdin).

## RHCAL's one press: the pointer model is wrong (information; drives the next design)
CAL-C (corner (+480,-480), then (0,+DY 88)) logged `MoveCharacter: request move cDave: 203,136 to 319,39`. The corner clamp
holds (x 319, check C2's condition), but y = 39 where the log-derived model (be61dea0) predicted 125-130: about 0.44 game px
per count, not ~1.45. DRIVE 5's targets in this power-on are identical to rounds RF / RG (204,98 319,98 34,128 0,128 925,69),
so the 486's pointer behaved as before; the model built from those logs does not carry over to DRIVE 6's moves (report-size
acceleration, or a mis-paired derivation). LAB-MOVE's agent is re-deriving it and redesigning the calibration cell to converge
from badly-off defaults before any re-run. Had the full cal cell run, its DY sweep (84 / 88 / 92) would have landed near y
~37-41, far outside 116..140.

## Bridge pair (P9M1, DRIVE 5, default config): 98.91 / 98.80%
| Cell | displayed | room 1 + entry | room 2 | late | catchup ticks / events / clamped | stall_ticks | audio |
|---|---|---|---|---|---|---|---|
| RHP1 | 98.91% (76) | 49 | 10 | 9 | 76 / 42 / 5 | 3 | 0 / 0 |
| RHP2 | 98.80% (84) | 49 | 4 | 23 | 84 / 45 / 5 | 3 | 0 / 0 |

Inside the registered 98.5-99.3% (no day-drift flag); the same binary's default cells in rounds RF / RG read 98.81-98.94%.
Timing note (registered): the pair ran ~10-25 min after the warm-up here, not ~65-75 min, because the MS3 block did not run.
Camera sheets show play in both (room 1 -> room 2). This pair is information only: P9M1's 99% x2 is retired as the campaign line
(operator 2026-11-11), and the MS3 line it was meant to bridge has no cells yet.

## Rig (vcctrl)
No USB event on the capture stick for the whole round (the first clean round since the 2026-11-10 23:38Z churn; device 80, no
port cycles). 3 corrupt capture frames (decode_errs 129 -> 136, each read 2-3 times), all black, all at cell launches:
17:35:53Z WARMUPRH, 17:55:40Z RHP1, 18:07:03Z RHP2. Mouse: one dropped PS/2 packet in RHP1 at 17:58:54Z (partial / timeout;
reported, not a bar); no stuck button (down / up balanced per cell). Lock handed over cleanly per cell. jobs/ not collected.

Files: SUMMARY.txt, driveRH.sh / cellRH.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt; RHCAL's DRIVE-WALK.LOG, CAL-RESULT.txt, GATE.txt. Captures and saves stay local (AUDIO-SHA256.txt,
SAVE-SHA256.txt in each cell).
