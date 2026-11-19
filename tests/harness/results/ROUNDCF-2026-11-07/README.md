# Round CF -- 2026-11-07: R1 CONFIRMED on the clean landed build (MMD in play 88.18% / 88.11%); L1 P3 MET; S16 MET; S32P and S8 NOT MET (whole-run, start-up)

One power-on: relay-on 03:59:55Z, power OFF 05:14:20Z (driver exit 0; powerguard confirmed OFF 05:14:30Z), cap 05:39:55Z not
reached; vcctrld daemon_start_t unchanged (1793979061.92). Operator, directly (question tool): "Power on after the check
(Recommended)"; sdlports' check of the pre-registrations (2350e4ba) passed first (ORDER-CONFIRMED). Every cell exit 0, stamp OK,
pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=2" in all six
scored cells (no env set anywhere: the default path is what was measured).
Binaries: CFREL = main 90083fe6 release, stamp 54d439f88378, sha256 7770f865...; CFINS = instrumented, 39c6e4b65079, 5650fff9...;
both build_dirty=0 and byte-identical to the reviewed LAND2REL / LAND2INS (`cmp -l`: 0 differing bytes -- the build stamp is a
hash of the build inputs, not of the commit, so the same tree gives the same bytes; there are no stamp offsets to list).

| Cell | whole / steady | fps_p50 | displayed (1 - skipped/ticks) | preloop ms | witness | verdict |
|---|---|---|---|---|---|---|
| WARMUPCF | 30.58 / 33.15 | -- | -- | -- | capture nolock (title) | not scored; C:\DOSAGS 77 entries (14 *.LOG) |
| CFS16 | 39.36 / 40.12 | 40.00 | 99.58% (21 of 4,999) | 873 | camera CLEAN (room 3, the character walks) | **MET** (gatebar) |
| CFS32 | **39.17** / 40.14 | 40.00 | 99.52% (24 of 4,999) | 1,030 | capture CLEAN (room 3, 640x480) | **NOT MET** (whole-run < 39.2) |
| CFS8 | **39.12** / 40.11 | 40.00 | 98.94% (53 of 5,002) | 946 | camera CLEAN (room 35, dark) | **NOT MET** (whole-run < 39.2) |
| CFM1 | -- / 39.91 | 36.78 | **88.18%** (828 of 7,003) | -- | camera: kids walk, room 1 -> 2 | in band |
| CFM2 | -- / 39.87 | 35.82 | **88.11%** (833 of 7,003) | -- | camera: kids walk, room 1 -> 2 | in band |
| CFMP | -- / 39.85 | 30.94 | 75.80% (1,695 of 7,003; fine timing on) | -- | camera: kids walk, room 1 -> 2 | P3 **MET** |

guiclip_final, raw (RUNMANI.LOG), every scored cell:
- CFS16 `mode=2 flagged=4559 skipped=0 skipped_px=0 clipped=0 full=4559 latched_full=0 latch_events=2 latch_alias=1 latch_buffer=1 latch_tint=0 latch_fullrestore=0`
- CFS32 `mode=2 flagged=4565 skipped=0 skipped_px=0 clipped=0 full=4565 latched_full=0 latch_events=2 latch_alias=1 latch_buffer=1 latch_tint=0 latch_fullrestore=0`
- CFS8  `mode=2 flagged=994 skipped=0 skipped_px=0 clipped=0 full=994 latched_full=0 latch_events=2 latch_alias=1 latch_buffer=1 latch_tint=0 latch_fullrestore=0`
- CFM1  `mode=2 flagged=18600 skipped=10931 skipped_px=140905600 clipped=7575 full=94 latched_full=6 latch_events=2 latch_alias=1 latch_buffer=1 latch_tint=0 latch_fullrestore=0`
- CFM2  `mode=2 flagged=18583 skipped=10564 skipped_px=133122560 clipped=7925 full=94 latched_full=6 latch_events=2 latch_alias=1 latch_buffer=1 latch_tint=0 latch_fullrestore=0`
- CFMP  `mode=2 flagged=16000 skipped=9573 skipped_px=127104000 clipped=6333 full=94 latched_full=6 latch_events=2 latch_alias=1 latch_buffer=1 latch_tint=0 latch_fullrestore=0`
The full-restore guard did not fire naturally on the 486 either (latch_fullrestore=0 in all six). R1 engaged in the three MMD
cells and in none of the gate scenes (skipped 0), as registered (S32P's engagement was information: none).

## MMD in play: R1 CONFIRMED (pre-registered: each 86.0-92.0%, mean within 2.5 points of GC's 89.01)
CFM1 88.18%, CFM2 88.11%: both in band, mean 88.15 (0.86 under GC's lab-binary 89.01), steady 39.87-39.91. With round GC's
R1-off arms (GCA1/GCA2, mean 66.18%), R1 on the shipped default path is +22.0 points. The hub may now quote it. Campaign line
(>= 99% x2): NOT MET, as expected; the remaining levers are R3 (verb bar), R2 (room-1 characters) and the getter intrinsics.

## CFMP: LAB-L1's P3 MET; profile (tests/harness/f1/f1prof.py as fixed in c457cda9; F1PROF.txt, F1PROF-room1.txt)
script_vm **12.18 ms/tick** (14,049 entries over 7,003 ticks; band 11.0-13.2, central 12.1: MET); process_events_dispatch 13.93
(band 13.0-14.8); rb_sprite_time per drawn frame 21,137.7 / 5,340 = 3.96 ms (band 3.6-4.6; GCMP 4.12); displayed 75.80% (band
72-78). Room 1 (5480-7890) drawn-tick medians: logic 16.12 / render 4.38 / scene 5.48 / ugo 26.42 ms, as GCMP. Room-2 entry at
loop tick 8020 (GCMP 7900; the host's clicks land at slightly different ticks run to run).

## S32P and S8: NOT MET as registered -- the miss is in start-up, the steady game rate met the bar
Registered falsifier: "NOT MET = the landed build regresses S32P / S8". It is TRIPPED AS WRITTEN and recorded so. What the cells
show (not yet a finding): steady 40.14 / 40.11, fps_p50 40.00, completeness 99.52% / 98.94%, audio counters clean -- every
figure but whole-run meets the bar. Whole-run counts start-up: preloop 1,030 / 946 ms vs D8's 648 / 650 (and ~0.3 s more
engine start before it) puts the two cells 0.23-0.25 under D8 (39.40 / 39.37). R1 does not engage in either scene (skipped 0).
The same shape missed in round V1 on the old binary (V1S32 39.18 with preloop 1,004; V1S8 39.13 with 971) when C:\DOSAGS was
cluttered; D8 rebuilt it to 60 entries and both met. It is now 77 entries (14 collected *.LOG). S8's 53 skipped frames sit
inside its history (GL8A 51, GS8A 47; D8S8 36). Lead, not a conclusion: start-up grows with C:\DOSAGS again. To separate
binary from rig state: run S32P / S8 with the v0.1 exe (c754df64babd) and CFREL interleaved in ONE machine state (see the
follow-up read below: the directory lead is superseded).

## Follow-up read (after the round, from the cells' own STDOUT): the start-up difference is the restart-point SAVE WRITE
The engine's per-phase start-up lines split it. The init phases are flat: script_vm_init 1,629 / 1,600 vs D8 1,633 / 1,605;
sprite_index 1,216 / 767 vs 1,217 / 769; room_load 426 / 404 vs 425 / 402; subsystem within 10 ms; gfxmode 645 vs 586 (S32)
and 455 vs 458 (S8). ALL of the preloop gain is preloop_restart_point_ms, i.e. restart_savegame_ms (SetRestartPoint's
SaveGame() writing the slot-999 save; diskcheck and screenshot are 0):

| cell | binary | restart_savegame_ms | preloop_ms |
|---|---|---|---|
| D8S32 / D8S8 | v0.1 c754df64babd | 213 / 228 | 648 / 650 |
| N7S8 | v0.1 | 384 | 833 |
| V1S32 / V1S8 | v0.1 | 527 / 520 | 1,004 / 971 |
| GCS16 | lab R1 | 358 | 755 |
| D8S16 / CFS16 | v0.1 / CFREL | 429 / 476 | 824 / 873 |
| CFS32 / CFS8 | CFREL | **593 / 523** | 1,030 / 946 |

The same v0.1 binary has written that save in 213-529 ms on different days; CFREL's 476-593 ms sits at the top of that range.
So the C:\DOSAGS-size lead above is WEAK (sdlports: 60 -> 77 entries cannot cost 300 ms on D8's 716 -> 60 slope) and is
superseded: the whole-run misses track the restart-point save's write time, which varies by day on one binary. Whether CFREL
writes it slower than v0.1 in the SAME machine state is the open question; the next round's v0.1-vs-CFREL ABBA scores
restart_savegame_ms and preloop_ms per cell (with the C:\DOSAGS entry count) to answer it.

## Incident (operator-side, mine): a duplicate power guard
I started powerguard.sh and daemongap.sh by hand next to the driver, which starts both itself. The hand-started guard ran before
the relay-on line, read power OFF at 03:59:55, sent no power command, touched POWERGUARD-DONE and exited; that marker made the
driver's own daemongap exit at once. Removed at 04:00:24, daemongap restarted; the driver's guard (started after relay-on, cap
05:39:55) was the round's guard and confirmed OFF at 05:14:30. Daemon-availability log missing 03:59:56-04:00:24 (no
DAEMON-GAPS.txt afterwards: no gap recorded). Follow-up (sdlports): powerguard.sh refuses to start without a relay-on line.

## Rig (vcctrl)
No USB event, no recovery, daemon unchanged. 5 corrupt capture frames (decode_errs 41 of 980,459), all at launches or the
collect reboot: 04:51:43.0Z (CFM1 collect), 04:55:46.5Z / 04:55:52.2Z (CFM2 launch), 05:07:08.8Z / 05:07:14.4Z (CFMP launch).
jobs/: all 14 file jobs of the round (7 send + 7 pull).

Files: SUMMARY.txt, driveCF.sh / cellCF.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
jobs/*.json; CFS16/CFS32/CFS8 GATEBAR.txt; CFMP F1PROF.txt, F1PROF-room1.txt, TICKS.BIN. Captures and saves stay local
(AUDIO-SHA256.txt, SAVE-SHA256.txt per cell).
