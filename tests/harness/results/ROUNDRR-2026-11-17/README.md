# Round RR -- the route-finder levers' ABBA on MS3 (ags 0382, DOSAGS_ROUTE_FAST) on the Gateway 486: results

2026-11-17. Pre-registration: 05d41e01 + 19cbf0b2 (on origin before any data; sdlports reviewed and confirmed the order).
Power-on: the operator's direct OK ("Power on now"), one power-on, relay-on 14:55:47Z, power OFF 16:25:14Z (1 h 29 min),
driver exit 0, no STOP, no recovery cycle. Binary R0382.EXE = the ags 0382 release, sha256 5ea0d5cc..., stamp
483247a02652 in every cell. Gateway 2000 486DX2-66, PicoGUS (SB, A220 I7 D3), USB4VC 0.5.109. Read by
tests/harness/rr-read.py (VERDICT.txt is the driver's own run of it).

## The result
**R-SKIPS: SUPPORTED. With DOSAGS_ROUTE_FAST=1 MS3 skips 364 frames per run instead of 578 (CUT 214.3); every F cell is
below every O cell; all six cells are valid.** Displayed frames: 91.7% -> 94.8% (means). The lab's prediction was a cut
of 153-220: the measurement is inside it.

| cell | arm | skips | displayed | skips per click second | per other second | press 114's margin, ms | pairing | witness |
|---|---|---|---|---|---|---|---|---|
| RRO1 | O | 558 | 92.03% | 3.886 | 2.432 | -1,509 | PAIR-OK 114 / 114 | on=0 allocs=0 |
| RRF1 | F | 359 | 94.87% | 2.254 | 2.136 | -1,080 | PAIR-OK 114 / 114 | on=1 allocs=2 peak=192000 |
| RRF2 | F | 324 | 95.37% | 2.246 | 1.333 | -1,955 | PAIR-OK 114 / 114 | on=1 allocs=2 peak=192000 |
| RRO2 | O | 572 | 91.83% | 3.816 | 2.867 | -2,045 | PAIR-OK 114 / 114 | on=0 allocs=0 |
| RRF3 | F | 409 | 94.16% | 2.991 | 1.333 | -1,788 | PAIR-OK 114 / 114 | on=1 allocs=2 peak=192000 |
| RRO3 | O | 605 | 91.36% | 4.193 | 2.705 | -1,384 | PAIR-OK 114 / 114 | on=0 allocs=0 |

- **The term, as pre-registered:** CUT = mean(O) 578.3 - mean(F) 364.0 = 214.3 skips per run (1.880 per click-second over
  114) >= 80; CUT > SPREAD (85, the F arm's range 324..409); max F 409 < min O 558. SUPPORTED.
- The registered four alone (RRO1 RRF1 RRF2 RRO2): CUT 223.5, SPREAD 35. The third pair ran whole and valid, so by the
  pre-registered rule it is in the verdict; it widens both arms (F3 409, O3 605).
- **The MS3 target (99% displayed; a registered pair, both >= 99.0%): NOT met,** as stated before the round. The best
  cell is 95.37%.
- Every cell: run-hw exit 0, manifest stamp 483247a02652, GATE PLAY-OK, PAIR-OK (worst sustained offset shift -19..-29
  ms), audio underruns 0 / overwrites 0 (pcm_irqs 3,342-3,356), the room-step levels within 11 ms of the registered
  +830 / +1,730 / +3,540, env_block_sha eec4d5b41015 in the O cells and c51945b26b99 in the F cells. RRCALQ: GATE PASS
  with 0 px drift on every axis, so RRCAL did not run. WARMUPRR: BLASTER "A220 I7 D3 P330 T3", stamp bc9c3704a839.
- Memory witness: every F cell allocated the stamp grid twice (room 1's 64,000 bytes, then room 2's 192,000) and peaked
  at 192,000 bytes; every F cell exited clean.

## Against what was stated before the round
- **The cut: as predicted.** Lab model 153 (rule H) .. 220 (rule P); measured 214.3 (223.5 on the registered four). The
  measurement sits at the rule-P end: the lab's rule H, with its "hidden click" handling, was the pessimistic one.
- **Displayed: as predicted.** About 94.0-95.0% in F against about 91.6-91.8% in O; measured 94.2-95.4% against
  91.4-92.0%.
- **Press 114: a WRONG prediction** (change A of the pre-registration, sdlports' estimate, adopted by the lead). It
  expected the F run to end 1.7-2.5 s earlier and built the 114EDGE rule for it. The run did not shorten: loop_ms is
  181,289 / 181,351 / 181,330 in O and 181,180 / 181,270 / 181,253 in F -- about 0.09 s. clamped=4 in both arms: a click
  tick's overrun is caught up by skipping frames, and the game clock does not move. Every cell has 114 journeys; the
  margins of the two arms overlap (O -1,509 / -2,045 / -1,384 ms; F -1,080 / -1,955 / -1,788). **114EDGE was not used
  and expires with this round.** The rule for next time: a shift of the run's end is predicted only from CLAMPED stalls,
  not from overruns the pacer catches up.
- **"Other seconds" was not a control -- a WRONG label in the pre-registration.** Skips per other second fell from 2.668
  (O mean) to 1.601 (F mean), more than the O cells differ among themselves. The counts behind it:

  | cell | other seconds right after a click second: n, skips each | the remaining other seconds: n, skips each |
  |---|---|---|
  | RRO1 / RRO2 / RRO3 | 34, 3.00 / 35, 3.54 / 34, 3.35 | 10, 0.50 in each |
  | RRF1 / RRF2 / RRF3 | 34, 2.62 / 35, 1.57 / 35, 1.57 | 10, 0.50 in each |

  34-35 of the 44-45 "other" seconds directly follow a click second and carry the click's repaid skips; the ten that do
  not are at 0.50 skips each in every cell of BOTH arms. So the seconds a click cannot reach did not move at all, and the
  class as defined mixed the two. (A reading made after the data; information only; it does not touch the term. That
  class is not to be called a control in a later round -- the ten click-free seconds are the candidate.)
- **Memory at the minimum: not explained.** memory_min_free_kb is 146,176 in all three F cells and 146,048 in all three
  O cells: F shows 128 KB MORE free at its minimum while holding a 192,000-byte stamp grid. I did not find the reason
  cheaply (the per-call beenhere buffer is allocated in both arms); it is stated, not explained.

## The rig watcher's observation (vcctrl; theirs, recorded here)
- No input event lost in any cell: ev_in = pkt_ok +687 per play cell (+81 for RRCALQ), 0 inhibit / timeout / partial /
  discarded, 127 input-log rows per play cell, every lock release unforced. Capture: 0 bad frames, 0 USB events.
- One hold at about +43 s from the lock in every play cell, max_wait_ms unchanged at 2,407.
- **The one difference by arm:** the board's partial_waits counter moved +2 (with +1 resume) in each of the three F
  cells and +1 / +1 in RRCALQ and the three O cells. The firmware has no per-stall length counter, so the counters
  cannot say what the extra wait is. The pairing shows no missing or shifted journey in any cell. Not explained; it
  follows the arm in all seven cells, so it is carried as an open observation for the next round on this binary.

## What follows (the pre-registration's words)
SUPPORTED -> the switch's default goes to the operator; after their ruling a following patch removes the switch and the
body that lost. Not in this round, as stated before it: Trilby's Notes (the lab read the levers 1.5% slower per request
in its room; no rig fixture asks it for routes) and a dispatch-cost measurement for the native-compilation research.

## Records
Per cell: tests/harness/results/<TAG>-2026-11-17/ (README.md = the pre-registration; READ.txt, PAIRING.txt, RUNMANI.LOG,
STDOUT.TXT, DRIVE-WALK.LOG, INPUT-LOG.*, the witness sheets). Here: SUMMARY.txt, VERDICT.txt, POWERGUARD.txt,
ORDER-CONFIRMED, the driver, the cell wrapper and the guards as run, expected.txt, the stamp. Audio captures and the
run-created saves stay local (AUDIO-SHA256.txt / SAVE-SHA256.txt per cell).
