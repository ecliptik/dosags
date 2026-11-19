# Round RD -- 2026-11-08: R2 (ags 0369, DOSAGS_CHAR_REUSE=2) on the 486 -- MMD in play 97.7% -> 99.0% displayed (ABBA); F2 MET, F1 FALSIFIED on one pair's margin (a moving burst crossed the fixed room-1 window edge), RDMP cut 5.52 ms (band 3.5-6.5); 99% x2 not met (98.97 / 99.07)

One power-on: relay-on 15:21:38Z, power OFF 16:38:31Z (driver exit 0; driver-started powerguard confirmed OFF 16:38:41Z, no "fired
DURING cell" line), cap 17:01:38Z not reached; vcctrld daemon_start_t unchanged (1793979061.92). Operator, directly (question tool):
"Power on now (Recommended)", after sdlports' check of 6ab5432c passed and vcctrl's pre-check (rig clear). Budget line: 3040 s at
RDA1 (4580 s for the whole round) vs 100 x 60 - 630 - 240 = 5130 s; used 67 min after the warm-up. Every cell exit 0, stamp OK, pre =
staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; every witness line as registered (arm A "charreuse ...=(default) mode=0", arm B
"=2 mode=2", all "guiclip ...=(default) mode=4", boxed > 0 in every MMD cell). Camera sheets show play in every MMD cell (the kids
walk in room 1, then room 2; RDMP also goes back to room 1 at loop tick 10017) and room 3 in RDS16. No recovery.
Binaries: RDREL = main 1e3609c2 release 84c1a74fdcf6 (sha256 ffe49dab...), RDINS = instrumented f9f8dd6614c8 (0e59c82b...), both
build_dirty=0 and byte-identical to the reviewed R2REL / R2INS (cmp: 0 differing bytes).

| Cell | arm | displayed (1 - skipped/ticks) | room 1 5480-7890 | entry 7890-8400 | room 2 8400-9500 | late 9500-end | late stretch |
|---|---|---|---|---|---|---|---|
| RDA1 | R3-only (default) | 97.93% (145 of 7,003) | 79 | 37 | 8 | 13 | 99.5% |
| RDB1 | R2 (=2) | **98.97%** (72) | **31** | 18 | 4 | 11 | 99.6% |
| RDB2 | R2 (=2) | **99.07%** (65) | **30** | 13 | 0 | 15 | 99.5% |
| RDA2 | R3-only (default) | 97.44% (179) | 53 | 79 | 18 | 21 | 99.3% |
| RDMP | R2, instrumented | 98.66% (94; fine timing on) | 55 | 7 | 9 | 15 | 99.5% |
| RDS16 | R2 (=2), 5 Days S16 | 99.52% (24 of 4,999) | -- | -- | -- | -- | -- |

Window skips = ticks - renders between the first persec rows at or after each edge (this rule reproduces round RC's published
RCB1 79 / 8 / 0 / 15 and RCB2 75 / 21 / 0 / 19 exactly). charreuse_final, R2 cells: RDB1 hits 11,984 skips 11,920 forced_full 64
mark_old 8 keyfail 0 refused 0; RDB2 hits 11,723 skips 11,659 forced_full 64 mark_old 8; RDMP hits 16,162 skips 16,050 forced_full
112; RDS16 hits 4,597 skips 4,597 (boxed 0: R3 never boxes room 3, so every skip there is drawn in full, as registered). Arm A cells
read hits 0. guiclip_final: latch_fullrestore 0 and fb_coarse 0 in every cell -- no guard fired naturally. Raw lines in RUNMANI.LOG.

## F1 (room 1), pre-registered verbatim: FALSIFIED by its second clause, on pair 2
- R2 cells' room-1 skips 31 / 30: band 20-40 (central 30) -- in; neither > 50.
- Fewer than its same-binary R3-only arm: pair 1 RDA1 79 -> RDB1 31 = **48** (>= 25, met); pair 2 RDA2 53 -> RDB2 30 = **23** (< 25:
  **the falsifier trips**). The verdict stands as registered.
- Information (not a rescue; the windows were fixed before data): the skip burst around the room change moves with where the host
  clicks land. Bursts of >= 5 skips per second: RDA1 at ticks 7790-7872 (inside the room-1 window), RDA2 at 7942-8026 (just past its
  7890 edge, so they count in "entry": 79). Room 1 + entry together: pair 1 116 -> 49 (-67), pair 2 132 -> 43 (-89). A future
  registration should window by the TICKS-recorded room entry, or score room 1 + entry as one window.

## F2 (whole fixture), pre-registered verbatim: MET
R2 cells 98.97% / 99.07%: band 98.9-99.5% (central 99.1) -- both in; neither < 98.6%. mean(R2) - mean(R3-only) = 99.02 - 97.69 =
**+1.34 points** (>= +0.5 required). The R3-only arms (97.93 / 97.44) sit below round RC's R3 cells (98.43 / 98.24), as their entry
windows took more of the click bursts today.

## F3 (mechanism, other windows): no loss (not falsified); the entry and room-2 gains are findings
Entry: 37 -> 18 (-19), 79 -> 13 (-66); room 2: 8 -> 4, 18 -> 0 (-18); late: 13 -> 11, 21 -> 15. No window lost skips under R2. The
entry gains > 10 skips are mostly the room-1 burst crossing the window edge (above); room 2's -18 in pair 2 is a finding (registered
expectation: near 0 there, since R2b draws a scrolled room's characters in full).

## Campaign line (>= 99% x2): NOT met
98.97 / 99.07. One R2 cell is 0.03 points short (2 skips of 7,003). Not claimed by F2 ("on the edge").

## RDMP (mechanism, pre-registered): MET, at the central value
f1prof.py window 5480..7890, medians over all 2,411 window ticks (as RCMP-2026-11-07/F1PROF-room1.txt): scene 2.81 + render 1.36 =
**4.17 ms** vs RCMP 5.60 + 4.09 = 9.69 ms: cut **5.52 ms** (band 3.5-6.5, central 5.5; falsified < 3.0). A different binary and day,
stated as such.
- Information (sdlports 2026-11-08), medians over room-1 DRAWN ticks only (render > 0): RCMP 1,974 drawn: 5.60 + 4.13 = 9.74; RDMP
  2,360 drawn: 2.81 + 1.36 = 4.17; cut 5.57. The all-tick result is not a drawn-fraction artifact.
- Information: RDMP entered room 2 at loop tick 7711 (RCMP 8296), so 180 of the registered window's ticks are room 2. Restricted to
  5480..7710 (2,231 ticks, room 1 only): 2.81 + 1.36 = 4.16, cut 5.53. Same answer.
- Information: script_vm 12.24 ms/tick (RCMP 12.47); displayed 98.66% with fine timing on (RCMP 90.55%); late window 9500-end
  (which for RDMP includes its return to room 1) render median 1.41, scene 2.80.

## RDS16 (the S16 guard, R2 =2): MET
gatebar S16: whole-run 39.34 / steady 40.17, fps_p50 40.00, 99.52% (24 of 4,999), audio clean (984 pcm IRQs, 0 underruns / late
writes); camera CLEAN (room 3, the character walks). R2 engaged (4,597 skips, all drawn in full; boxed 0), as registered. preloop 800 ms.

## Rig (vcctrl)
No USB event across three watch windows, no recovery, daemon unchanged. 2 corrupt capture frames (decode_errs 94 -> 99), both black
and both at a game launch: 15:27:10.7Z (the warm-up's launch) and 16:21:12.3Z (RDMP's launch at 16:20:54Z + 18 s). Capture "STALE"
in every cell is the known "nolock" kind (the stick never locks this mode); the camera is the play witness. jobs/: all 14 of this
round's file jobs (7 sends, 7 pulls).

Files: SUMMARY.txt, driveRD.sh / cellRD.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt, jobs/;
RDS16 GATEBAR.txt; RDMP F1PROF.txt / F1PROF-room1.txt / F1PROF-late.txt / TICKS.BIN. Captures and saves stay local
(AUDIO-SHA256.txt, SAVE-SHA256.txt).

## Note (2026-11-11, information only; not a verdict change)
Board partial packets (USB4VC 0.5.107 abandoned a partly sent PS/2 packet, leaving the mouse out of frame for the rest of a cell;
lab-rb LAB-MOVE 10.12, move-lab/rj/ARM-PARTIALS.txt): RDB1 had an in-play partial at click 9, after its room-1 window, so its
room-1 count predates it; later clicks may have landed on the verb bar and changed later GUI ticks. Across rounds RC-RG, cells with
an in-play partial are 6 / 12 (A) vs 5 / 12 (B): unbiased by arm, as far as 2-vs-2 can tell. R2's ~1-point direction is far
larger than a single late slip could move.
