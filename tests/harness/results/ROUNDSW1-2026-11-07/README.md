# Round SW1 -- 2026-11-07: save-write lever 1 (DOSAGS_SAVEMEM) FALSIFIED on the 486 -- the restart save still takes ~505 ms with one write instead of 117 DOS calls

One power-on: relay-on 09:31:40Z, power OFF 11:08:29Z (driver exit 0; powerguard -- driver-started, the fixed one -- confirmed OFF
11:08:34Z), cap 11:31:40Z not reached; vcctrld daemon_start_t unchanged (1793979061.92). Operator, directly (question tool): "Power
on after the check (Recommended)"; sdlports' check of f23fd8f5 passed with one fix, made before data (bdc64a2c). Every cell exit 0,
stamp OK, pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; room 3; every savemem witness as registered (OFF: mode=0
path=stream; ON: mode=1 path=mem bytes=59538 fallback=0). Binaries are LAB records (swrel2 761f64ceccac, build_dirty=1): gatebar
VOIDs them by design and no SW1 figure enters hub figures.
**The two trace cells (SW1TA / SW1TB) did NOT run**: need() at 11:08:23 had 1157 s left (cap - 240 s margin) < 1540 s -- the eight
timing cells took ~10.8 min each, not the ~10.3 planned -- so the per-call attribution and CHKDSK-after are missing.

| Cell | arm | restart_savegame_ms | preloop_ms | room_load_ms | whole / steady | AGSSAVE.999 before -> after | bytes free (before) |
|---|---|---|---|---|---|---|---|
| SW1A1 | OFF | 420 | 857 | 426 | 39.33 / 40.15 | 146,822 -> 59,538 (shrink) | 258,801,664 |
| SW1B1 | ON | **725** | 1,104 | 367 | 39.22 / 40.12 | 59,538 -> 59,538 | 258,867,200 |
| SW1B2 | ON | 507 | 888 | 368 | 39.37 / 40.12 | same | 258,834,432 |
| SW1A2 | OFF | 509 | 946 | 425 | 39.27 / 40.16 | same | 258,801,664 |
| SW1A3 | OFF | 505 | 942 | 425 | 39.23 / 40.13 | same | 258,768,896 |
| SW1B3 | ON | 503 | 883 | 367 | 39.31 / 40.12 | same | 258,736,128 |
| SW1B4 | ON | 503 | 883 | 367 | 39.31 / 40.12 | same | 258,703,360 |
| SW1A4 | OFF | 508 | 948 | 428 | 39.23 / 40.15 | same | 258,670,592 |

## Primary (pre-registered): FALSIFIED
Paired d = OFF - ON: (SW1A1, SW1B1) **-305**; (SW1B2, SW1A2) **+2**; (SW1A3, SW1B3) **+2**; (SW1B4, SW1A4) **+5**. Median d = **2 ms**
(registered: >= 30; falsified if < 20); mean -74 ms; 4 complete pairs. Collapsing 117 INT 21h calls (16 writes incl. 9 in-place
patches, 82 seeks) into 11 (5 writes, no seeks, no patches) did not change the restart save's wall time on this machine: 503-509
ms ON vs 505-509 ms OFF in three of the four pairs.

## H1 (second hypothesis): FALSIFIED
Valid (OFF cells 420 / 509 / 505 / 508: all >= 400). SW1B1 (ON) read 725 ms with its adjacent OFF at 420: an ON cell > 260 ms next to
an OFF >= 400 ms.

## What the cells do show (information; not pre-registered, not a claim)
- The save's wall time sits at a ~505 ms plateau whatever the engine issues, with excursions (SW1B1 725, ~+220; SW1A1 420). The CPU
  part the lever removed (~14 ms at 40k, x1.5-2.3 on the 486) is not visible in it either. Whatever holds the ~500 ms is not the
  number or order of DOS calls -- most likely the card / close path, which the missing trace cells were meant to place.
- The shrink lead is dead: SU32A1's shrinking write took 210 ms; SW1A1's identical shrink (146,822 -> 59,538 after the warm-up's MMD
  save) took 420 ms.
- room_load_ms -- the phase right AFTER the save in start_game() -- is 58-61 ms lower in all four ON cells (367-368 vs 425-428 OFF),
  and preloop falls by the same amount (883-888 vs 942-948 in the clean pairs). Unregistered and unexplained; candidates are heap
  state after the 256 KB image is freed, or DOS/SMARTDRV state after 11 rather than 117 calls. It would need its own prediction.
- CHKDSK before (CHKDSK1.TXT): 2,014,511,104-byte volume, 32 KB clusters, 61,478 clusters of which 7,898 free (87% used), 6,860
  files in 317 directories; no errors reported. Free bytes fall 32,768 per cell (one cluster) through the round.
- Whole-run: all eight 39.22-39.37 (>= 39.2), both arms.

## Next (proposal, for sdlports / the operator)
1. Place the ~500 ms before any further save lever: a short trace-first round (SW1TA / SW1TB as registered, run FIRST), so the
   per-INT-21h times say which call holds it.
2. Lever 1 is not landed on the strength of SW1. Its exactness gates (G1-G5) stand; it can be revisited if the trace shows a cost it
   addresses, and the room_load effect would need its own pre-registration.

## Rig (vcctrl)
No USB event, no recovery, daemon unchanged. 5 corrupt capture frames (decode_errs 70 of 1,541,715), at 10:39:31 / 10:39:40Z (SW1B3
launch) and 11:01:06 x2 / 11:01:14Z (SW1A4 launch). jobs/: 16 file jobs (the warm-up's send and pull aged out of vcctrld's last 16).

Files: SUMMARY.txt, driveSW.sh / cellSW.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt, jobs/;
per cell GATEBAR.txt (VOID: lab binary), SVPRE / SVPOST / DIRLIST / SDRV; WARMUPSW CHKDSK1.TXT. Captures and saves stay local.
