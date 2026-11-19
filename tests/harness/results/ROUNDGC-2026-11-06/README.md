# Round GC -- 2026-11-06: lever R1 (DOSAGS_GUI_CLIP=2) WORKS on the 486 -- MMD in play 66.2% -> 89.0% displayed (ABBA); 99% not reached

One power-on: relay-on 21:06:54Z, power OFF 22:44:25Z (driver exit 0; powerguard confirmed OFF 22:44:29Z), cap 23:01:54Z not
reached; vcctrld daemon_start_t unchanged. Operator, directly (question tool): "Power on now" (ORDER-CONFIRMED). Pre-registrations
4557bf43. Every cell exit 0, stamp OK, pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3", vmmode mode=3, englev on=1 in all.
Binaries: gcrel.exe = lab R1REL (f81265edd05e, sha256 50b02ec9...) and gcins.exe = lab R1INS (5dc54892ad56, sha256 f5089493...),
both build_dirty=1 (lab-play.diff on the 0365 head, ~/git/dosags-lab-play) -- lab binaries, not shipped.

| Cell | R1 | displayed (1 - skipped/ticks) | steady | fps_p50 | guiclip_final | verdict |
|---|---|---|---|---|---|---|
| WARMUPGC | -- | -- | 33.14 | -- | -- | not scored; C:\DOSAGS 68 entries (5 *.LOG) after D8's rebuild |
| GCS16 | on | 99.48% (26 of 4,999) | 40.17 (whole 39.36) | 40.00 | flagged 4,552, skipped 0 | guard: every bar figure met; **gatebar VOID (build_dirty 1)** |
| GCA1 | off | 66.39% (2,354 of 7,003) | 39.83 | 27.32 | mode=0 flagged=0 | A |
| GCB1 | on | **88.72%** (790 of 7,003) | 39.88 | 36.20 | skipped 10,606, clipped 8,012, full 94 (latched 6) | B |
| GCB2 | on | **89.30%** (749 of 7,003) | 39.87 | 36.74 | skipped 11,349, clipped 7,392, full 94 (latched 6) | B |
| GCA2 | off | 65.97% (2,383 of 7,003) | 39.87 | 26.92 | mode=0 flagged=0 | A |
| GCMP | on (instr.) | 75.25% (1,733 of 7,003; fine timing on) | 39.86 | 29.00 | -- | profile; **mechanism falsifier TRIPPED** |
| GCAQA | off | 93.01% (250 of 3,576) | 41.22 | 39.37 | mode=0 flagged=0 | information; AutoPilot 18 ok, 0 fail |
| GCAQB | on | **97.09%** (104 of 3,572) | 41.21 | 40.00 | skipped 6,144, clipped 2,059, full 11 | information; AutoPilot 18 ok, 0 fail |

## ABBA (pre-registered): R1 WORKS
Both B >= 85% (88.72, 89.30); each B above each A by >= 15 points (smallest gap 22.33); steady 39.83-39.88 in all four; mean(B) -
mean(A) = 89.01 - 66.18 = **22.83 points** (falsifier < 15: not tripped). Band 88-100%: inside, at its BOTTOM edge -- central ~96%
missed by 7 points. A's prediction 66.0-69.5% missed by GCA2 (65.97%, 0.03 under). Campaign line (>= 99% x2): NOT MET.
Per window (renders / ticks, 25-row persec blocks): loop ticks ~5,480-9,500 (room 1, then room 2's entry; GCMP's TICKS.BIN puts
the entry at tick 7,900) A 60-71% -> B 90-99%; the last ~2,000 ticks (room 2) A 68-71% -> B 78-82%. R1 lifts the first two
thirds of the play nearly to the bar; the end of room 2 keeps most of its shortfall. Camera: kids walk, room 1 -> 2, in all four (GCB1 read
frame by frame; the screen is lit to the game's exit).

## GCMP vs D8MP (same fixture, instrumented, fine timing on)
rb_sprite_time per drawn frame: D8MP 7.97 ms (29,946 ms / 3,756) -> GCMP **4.12 ms** (21,825 / 5,302): cut 48%, but the
pre-registered falsifier (> 4.0) is TRIPPED -- R1 removed less sprite time than the lab predicted (1.5-3.7). Medians per drawn
tick (TICKS.BIN, ms): room 1 logic 16.6 -> 16.2, render 8.2 -> 4.1, scene 3.9 -> 5.6, total 30.4 -> 26.5; room 2 logic 17.7 ->
17.4, render 8.2 -> 5.5, scene 4.0 -> 4.2, total 29.7 -> 26.6. A drawn tick is still ~1.5 ms over the 25 ms budget in both rooms,
and per-tick LOGIC (~17 ms: process_events_dispatch 13.9, script_vm 12.1 ms/tick) is now the largest cost, not drawing.
Next levers re-ranked: logic in play first; room 2's remaining render (5.5 ms); R3 (verb bar to its dirty boxes) after.
**Correction (2026-11-06, later): f1prof.py paired TICKS.BIN records off by one tick** (a tick's update_game_once close
is stamped with the next loop counter; found by LAB-R2), and D8MP entered room 2 at loop tick 7715, inside the 5480-7890
window used for it. Re-read with the fixed reader, drawn ticks only (GCMP room 1 5480-7890, room 2 7940-12439; D8MP room 1
5480-7714, room 2 7755-12439), medians D8MP -> GCMP: room 1 logic 16.3 -> 16.2, render 10.0 -> 4.4, scene 5.5 -> 5.6,
total 31.8 -> 26.6; room 2 logic 17.7 -> 17.3, render 8.3 -> 6.7, scene 4.2 -> 4.2, total 30.3 -> 28.1. So R1 cut room 1's
drawn-tick render by 5.6 ms (not 4.1), and room 2's drawn tick is ~3 ms over budget, not ~1.5 (the verb-bar stretch; R3).
F1PROF.txt / F1PROF-room1.txt are regenerated with the fixed reader (old versions in git history); D8MP/F1PROF-room1-to7714.txt
is the room-1-only window. The ABBA verdict (displayed %) does not use TICKS.BIN and is unchanged.

## GCS16 -- the guard, not a gate reading
Figures: whole 39.36 / steady 40.17, fps_p50 40.00, completeness 99.48% / presents 4,986 of 4,974 passes, audio counters clean
(overwrites 0, late_writes 0, silent_irqs 0, underruns 0), camera CLEAN (room 3, the character walks), preloop 755 ms. R1 did not
engage (skipped 0), as predicted. gatebar.py VOIDs it (build_dirty 1): the pre-registration called it "scored as a gate cell"
on a lab exe, which gatebar can never score -- a pre-registration error, recorded here. It answers the guard's question (the R1
binary does not slow S16); the gate reading comes from a clean build of the landed patch.

## GCAQA / GCAQB (information, one pair, not a claim)
AGS Quest AutoPilot 93.01% -> 97.09% displayed with R1 on (N7AQ 93.04%); stall_ms 81.1 s / 80.1 s; every phase ok in both.

## Rig (vcctrl)
No USB event (15 rounds without a drop), stick present throughout, audio unbroken. decode_errs 15 -> 31: 6 distinct corrupt
frames, ALL black, all at a mode switch or reboot, none mid-play: 21:12:15.8Z (WARMUPGC launch), 21:42:15.7Z (GCB1 launch),
21:53:27.0Z (GCB2), 22:04:38.2Z (GCA2), 22:36:56.4Z (GCAQB launch), 22:43:50.9Z (GCAQB collect reboot). Two stray "5" lines at
the DOS prompt after each NET boot come from send-file's own blind menu selection, ahead of VCCHK (harmless, by design).
jobs/: 16 file jobs; the first two (WARMUPGC send/pull) had aged out of vcctrld's last-16 list when read.

Files: SUMMARY.txt, driveGC.sh / cellGC.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
jobs/*.json; GCS16/GATEBAR.txt; GCMP/F1PROF.txt, F1PROF-room1.txt, TICKS.BIN. Captures and saves stay local (AUDIO-SHA256.txt,
SAVE-SHA256.txt); no AGS Quest image is committed.
