# Round RE -- 2026-11-09: ags 0370 (R2 on by default) confirmed on the 486, REC1 / REC2 98.97 / 99.04% (MET); patch 0163's DOSAGS_STALL_RESYNC FALSIFIED (B 0.25 points WORSE, not better: keep it off); RES16 MET; three of the four default-config MMD cells >= 99%

One power-on: relay-on 11:56:37Z, power OFF 13:24:38Z (driver exit 0; driver-started powerguard confirmed OFF 13:24:40Z, no
"fired DURING cell" line), cap 13:46:37Z not reached; vcctrld daemon_start_t unchanged (1793979061.92). Operator, directly, in
the coordinator session: "Okay to power on" (2026-11-09 ~11:54Z, after lifting the 2026-11-08 hold; also relayed by vcctrl);
vcctrl pre-check: rig clear 11:56:11Z. Pre-registrations: 10665cbc, re-dated before any data in 83172a53 (sdlports checked the
re-date). Budget line: need 5320 s after the warm-up vs 110 x 60 - 630 - 240 = 5730 s; used 78 min after the warm-up, every
cell ran. Every cell exit 0, stamp OK (9db4170acd89), pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; every witness line
as registered ("charreuse DOSAGS_CHAR_REUSE=(default) mode=2" and "guiclip ...=(default) mode=4" in every cell; boxed > 0 in
every MMD cell; RUN.BAT carries SET DOSAGS_STALL_RESYNC=1 in REB1 / REB2 only). Camera sheets show play in every MMD cell (room
1 -> room 2; REC2 is back in room 1 at its end) and room 3 in RES16. No recovery.
Binary: REREL = main 4ee5b017 release, stamp 9db4170acd89 (sha256 f9202de6...), build_dirty=0, byte-identical to the reviewed
R2DREL.

| Cell | arm | displayed (1 - skipped/ticks) | room 1 + entry 5480-8400 | room 2 8400-9500 | late 9500-end | catchup ticks / events / clamped / resyncs | stall_ticks | loop_ms |
|---|---|---|---|---|---|---|---|---|
| REC1 | default | 98.97% (72 of 7,003) | 48 | 8 | 9 | 72 / 38 / 4 / 0 | 3 | 181,286 |
| REC2 | default | **99.04%** (67) | 43 | 0 | 17 | 67 / 36 / 5 / 0 | 4 | 183,424 |
| RES16 | default, 5 Days S16 | 99.48% (26 of 4,999) | -- | -- | -- | 26 / 7 / 4 / 0 | 3 | 125,742 |
| REA1 | A (resync unset) | **99.04%** (67) | 43 | 5 | 12 | 67 / 33 / 5 / 0 | 3 | 181,284 |
| REB1 | B (=1) | 98.76% (87) | 53 | 10 | 21 | 87 / 49 / 2 / 3 | 3 | 181,167 |
| REB2 | B (=1) | 98.84% (81) | 47 | 14 | 17 | 81 / 43 / 3 / 3 | 3 | 181,275 |
| REA2 | A (resync unset) | **99.06%** (66) | 47 | 0 | 12 | 66 / 34 / 5 / 0 | 3 | 181,439 |

Windows: ticks - renders between the first persec rows at or after each edge (ROUNDRD's rule; rescore.py, WINDOWS.txt; the
windows exclude the restore second before 5480, so they do not sum to the total). Per-second skip bursts and the tick_stall
lines: PERSEC-SKIPS.txt. Audio in every cell: underruns 0, overwrites 0 (silent_irqs 42-44, REC2 85). guiclip_final:
latch_fullrestore 0 and fb_coarse 0 in every cell. Raw lines in each cell's RUNMANI.LOG.

## REC (0370 confirmation), pre-registered: MET
Band 98.6-99.4% (central 99.0), falsified if either cell < 98.3%. REC1 98.97, REC2 99.04: both in. The 0370 default reproduces
round RD's explicit =2 cells (98.97 / 99.07) on the 0370 binary.

## RES16 (the S16 guard): MET
gatebar S16: whole-run 39.39 / steady 40.17, fps_p50 40.00, 99.48% (26 of 4,999), audio clean (1,238 pcm IRQs, 0 underruns /
overwrites / late writes); camera CLEAN (room 3). As registered, boxed 0 (R3 never boxes room 3), charreuse skips 4,543.
GATEBAR.txt in RES16-2026-11-09/.

## 0163 A/B (REA1 REB1 REB2 REA2), pre-registered verbatim
- **P1 (displayed): FALSIFIED, in the opposite direction.** Registered: B 6-15 fewer skips per pair, falsified if mean(B) -
  mean(A) < +0.05 points. Measured: pair 1 REA1 67 -> REB1 87 (**+20** skips), pair 2 REA2 66 -> REB2 81 (**+15**); mean(B) -
  mean(A) = 98.80 - 99.05 = **-0.25 points**.
- **P2 (the 250 ms edge): MET.** B cells resyncs 3 == stall_ticks 3 (both); A cells resyncs 0. P1 is therefore not VOID: the
  lever engaged exactly as designed.
- **P3 (information): loop_ms did not grow.** Predicted B +0.3 to +0.5 s; measured B 181,167 / 181,275 vs A 181,284 / 181,439
  (B 0.12-0.16 s shorter). tick_rate_steady 39.97 / 39.97 vs 39.96 / 39.93: within +-0.05, as registered.
- **P4 (audio clean): MET.** underruns 0 and overwrites 0 in all four cells.
- What the per-second rows show (information, PERSEC-SKIPS.txt): the skips right after the stalls are there in BOTH arms -- 5 in
  the second of the 3.7 s room-load stall and 6-7 after the ~345 ms stall that follows it (A: 7694:5 / 7762:6, 8105:5 / 8170:7;
  B: 8219:5 / 8334:7, 7802:10 / 8001:7). So on the 486 these are not the repaid debt that the resync declines; B's clamped count
  drops (5 / 5 -> 2 / 3) but its skips do not. B's extra skips sit in room 2 and late (9065:9, 9995:7; 8613:10, 11324:10).
  With n = 2 per arm, and the rig's wall-timed clicks landing at different game ticks after each resync (room-2 load at A
  7657 / 8105, B 8219 / 7760), that excess may be click timing rather than the lever; the registered measure says no either
  way. An inference, not tested: the post-load skips come from the first slow ticks of the new room (ordinary catch-up), which
  is where L1 (0371) aims, not from the stall itself.
- Outcome: 0163 stays default OFF; not adopted, and no further rig time for it. Its stale "=0 disables" comment (the code
  reads exactly "1" = on) stays on the cleanup list.

## Campaign line (>= 99% x2): not met by the registered REC pair (98.97 / 99.04); 3 of 4 default-config cells >= 99.0% (REA1 / REA2 99.04 / 99.06; mean of the four 99.03)
The confirmation pair REC1 / REC2 is 98.97 / 99.04: REC1 is 2 skips over the 70 that 99% allows on 7,003 ticks. The A arms of
the 0163 block run the same binary, fixture and env as REC (DOSAGS_STALL_RESYNC unset = the default): REA1 99.04, REA2 99.06.
So three of the round's four default-config MMD cells are >= 99%, mean 99.03%, with margins of 3-4 skips: on the edge, and the 0163
cells were registered as an A/B, not as campaign cells. It is
reported here, not claimed by any registered prediction. L1 (0371; LAB-RB s7 draft: 3-9 fewer per run) and L2 (0372; LAB-L2G: 2-5 fewer) are the
margin.

## Rig (vcctrl)
No USB event across three watch windows (17 rounds without a drop, R2 through RE), stick present throughout, no recovery,
daemon unchanged. 3 corrupt capture frames (decode_errs 99 -> 105, each read twice), all black, all at a launch or reboot:
12:10:59.3Z (REC1 launch), 12:18:06.2Z (REC2's reboot), 12:54:59.5Z (REB1 launch). capture=STALE in every cell: the stick
never locks this video mode (vcctrl checked during REC1: byte-identical frames while the camera showed MMD in play); the camera
is the play witness. REB1 has no WITNESS-send.jpg (its send step read "no-picture"; the reboot witness itself passed). jobs/ was
not collected this round.

Files: SUMMARY.txt, driveRE.sh / cellRE.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt + rescore.py, PERSEC-SKIPS.txt + persec.py; RES16 GATEBAR.txt. Captures and saves stay local (AUDIO-SHA256.txt,
SAVE-SHA256.txt in each cell).
