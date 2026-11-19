# Round WB -- 2026-11-07: SMARTDRV write-behind FALSIFIED as a lever -- the restart save gets ~60 ms faster, but the deferred write lands in the room load and start-up gets 210-415 ms SLOWER; no disk damage; do not adopt

Attempt 2 (attempt 1 ran only the warm-up -- my need() budget error; attempt1/README.md). One power-on: relay-on 18:10:35Z, power OFF
19:56:05Z (driver exit 0; driver-started powerguard confirmed OFF 19:56:09Z; it logged no "fired DURING cell" line), cap 20:10:35Z
not reached; vcctrld daemon_start_t unchanged. Operator, directly (question tool): "Power on now (Recommended)", after sdlports
OK'd amendment 7. Budget line: WBA1 need 5520 s vs 7200 - 630 - 240 = 6330 s (amendment 8). Every cell exit 0, stamp OK
(rcrel 4c9f83b62c5c), pre = staged = post; BLASTER ok; room 3. SMARTDRV /? syntax check passed again. SDRVON showed C: write cache
"yes" in every WB cell and "no" in every WT cell; SDRVOFF showed "C: yes no" after every cell (the wbcheck line in SUMMARY 8 / 8).
WBA4 (a WT cell) needed one harness recovery at its COLLECT step (no picture after 152 s -> power cycle -> ready in 38 s): its
RUN.BAT had finished (SDRVOFF and CHKDSK2 present), so no cache was at risk. No WB cell was lost; no scoring rule 5 event.

| Cell | arm | restart_savegame_ms | room_load_ms | start_game_ms (preloop) | whole / steady | displayed | gatebar |
|---|---|---|---|---|---|---|---|
| WBA1 | WT | 215 | 426 | 650 | 39.39 / 40.15 | 99.36% (32) | MET |
| WBB1 | WB | 151 | **699** | 859 | 39.37 / 40.10 | 99.46% (27) | MET |
| WBB2 | WB | 151 | **903** | 1,063 | 39.28 / 40.17 | 99.52% (24) | MET |
| WBA2 | WT | 214 | 428 | 652 | 39.38 / 40.13 | 99.44% (28) | MET |
| WBA3 | WT | 211 | 428 | 649 | 39.38 / 40.16 | 99.54% (23) | MET |
| WBB3 | WB | 151 | **873** | 1,033 | 39.29 / 40.17 | 99.52% (24) | MET |
| WBB4 | WB | 152 | **703** | 864 | 39.37 / 40.11 | 99.38% (31) | MET |
| WBA4 | WT | 210 | 427 | 648 | 39.41 / 40.17 | 99.34% (33) | MET |

## PRIMARY (pre-registered): FALSIFIED
Paired d = WT - WB on restart_savegame_ms: (WBA1, WBB1) +64; (WBB2, WBA2) +63; (WBA3, WBB3) +60; (WBB4, WBA4) +58. Median d = 61.5 ms
(registered >= 150; falsified if < 100); 4 complete pairs. The band assumed WT cells would carry 1-2 card stalls (420-720 ms, as in
rounds CF / SU / SW1); today every WT save took 210-215 ms (no stall), so the most write-behind could take off was the ~60 ms of
synchronous card writing -- and it did.

## REQUIRED (displayed within +-0.3 points): MET -- and the falsifier did not trip
mean(WB) 99.47% - mean(WT) 99.42% = +0.05 points. Amendment 2 (stop the line on a tripped displayed falsifier) does not apply.

## What actually happens with write-behind (information; the reason not to adopt it)
The cached save is written out by SMARTDRV during the NEXT start-up phase: room_load_ms rises from 426-428 (WT) to 699-903 (WB) --
the room file's reads queue behind the lazy write. start_game_ms (the preloop) is therefore 210-415 ms LONGER with write-behind
(859-1,063 vs 648-652), and whole-run is no better (WB 39.28-39.37, WT 39.38-39.41). The save write is not avoided, only moved,
and it costs more where it lands. Practical outcome (amendment 1): whole-run met 39.2 in all 8 cells, both arms -- on a stall-free
day for the card. Recommendation: write-behind is NOT adopted for any round (amendment 3 needed a separate decision anyway); the
restart-save line is closed on the machine side as well as the engine side (round SW1).

## SAFETY: CHKDSK before (WARMUPWB, first pre-line) and after (WBA4, after its flush) -- clean
No lost clusters, lost chains or cross-links in either. 7,877 -> 7,866 free clusters, 6,882 -> 6,892 files (the cells' own logs and
outputs). WARMUPWB-2026-11-07/ now holds attempt 2's warm-up files; attempt 1's are in git at 1ca462ab.

## Rig (vcctrl)
No USB event; one recovery (WBA4, collect step, above); daemon unchanged. 5 corrupt capture frames (decode_errs 94 of 2,124,946):
19:31:52 / 19:31:53 / 19:32:00Z (WBB4 launch) and 19:43:00 / 19:43:07Z (WBA4 launch). jobs/: the last 16 file jobs (the
warm-up's send and pull aged out).

Files: AMENDMENTS.md (1-8), attempt1/, SUMMARY.txt, driveWB.sh / cellWB.sh / powerguard.sh / daemongap.sh / expected.txt /
ORDER-CONFIRMED, POWERGUARD.txt, jobs/; per cell GATEBAR.txt, SDRVON / SDRVOFF / SVPRE / SVPOST / DIRLIST / SDRV; WARMUPWB SDHELP /
SDRV0 / CHKDSK1; WBA4 CHKDSK2. Captures and saves stay local.
