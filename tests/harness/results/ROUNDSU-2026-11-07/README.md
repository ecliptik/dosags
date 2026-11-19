# Round SU -- 2026-11-07: the landed build does NOT regress start-up (H0 holds: 3 of 4 pairs within 2 ms); the whole-run margin is the restart-save write, on both binaries

One power-on: relay-on 05:26:03Z, power OFF 07:07:50Z (driver exit 0; powerguard -- the fixed one, started by the driver only --
confirmed OFF 07:07:58Z), cap 07:26:03Z not reached; vcctrld daemon_start_t unchanged (1793979061.92). Operator, directly
(question tool): "Power on now (Recommended)", after sdlports' check of the pre-registrations (80a197d9) passed. Every cell exit 0,
stamp OK, pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; rooms 3 (S32P) and 35 (S8) as registered. SU8B1 needed one harness
recovery at its send step (no picture after 153 s -> power cycle -> DOS prompt in 39 s, 61 s lost); its run then completed normally.

| Cell | binary | restart_savegame_ms | preloop_ms | whole / steady | displayed | AGSSAVE.999 before -> after (B) | bytes free | C:\DOSAGS entries | gatebar |
|---|---|---|---|---|---|---|---|---|---|
| SU32A1 | v0.1 | **210** | 644 | 39.36 / 40.11 | 99.52% | 146,822 -> 59,538 | 259,227,648 | 86 | MET |
| SU32B1 | CFREL | 426 | 859 | 39.38 / 40.11 | 99.50% | 59,538 -> 59,538 | 259,227,648 | 89 | MET |
| SU32B2 | CFREL | 516 | 954 | 39.32 / 40.16 | 99.54% | 59,538 -> 59,538 | 259,194,880 | 90 | MET |
| SU32A2 | v0.1 | 514 | 948 | 39.23 / 40.14 | 99.34% | 59,538 -> 59,538 | 259,162,112 | 91 | MET |
| SU8A1 | v0.1 | 501 | 924 | **39.18** / 40.17 | 99.22% | 59,538 -> 61,199 | 259,129,344 | 92 | **NOT MET** (whole-run) |
| SU8B1 | CFREL | 500 | 924 | 39.25 / 40.17 | 99.20% | 61,199 -> 61,199 | 258,899,968 | 93 | MET |
| SU8B2 | CFREL | 506 | 928 | 39.25 / 40.18 | 99.26% | 61,199 -> 61,199 | 258,867,200 | 94 | MET |
| SU8A2 | v0.1 | 505 | 927 | 39.22 / 40.17 | 99.20% | 61,199 -> 61,199 | 258,834,432 | 95 | MET |

(v0.1 = d8rel.exe c754df64babd; CFREL = 54d439f88378, main 90083fe6. Size and free bytes from SVPRE.TXT / SVPOST.TXT, entries from
DIRLIST.TXT, all plain DOS DIR output taken in RUN.BAT just before / after AGS.EXE.)

## H0 (pre-registered): HOLDS -- the build does not regress the restart-point save
Paired d = CFREL - adjacent v0.1: (SU32A1, SU32B1) **+216**; (SU32B2, SU32A2) **+2**; (SU8A1, SU8B1) **-1**; (SU8B2, SU8A2) **+1**.
Mean d = +54.5 ms (|mean| <= 100) and the signs are mixed: H0 holds; the falsifier (CFREL slower in all 4 AND mean > 100) is not
tripped. The one large pair is the confound registered in advance: SU32A1 is the first cell after the warm-up's MMD save (146,822 B)
and the only cell in which the save SHRANK; it wrote in 210 ms, every other cell in 426-516 ms whatever the binary. Init phases,
paired: script_vm_init, sprite_index, room_load and subsystem within 10 ms; gfxmode within 20 ms except SU32A1's 661 (vs 589-606; S8 451-471).

## What decides the whole-run gate figure here
- The bar's whole-run figure counts start-up, and restart_savegame_ms moves it by ~0.1: at ~500 ms the two scenes read 39.18-39.32
  (S8 39.18-39.25), at 210 ms S32P read 39.36. SU8A1 -- the OLD v0.1 exe -- missed at 39.18 with a 501 ms write. Round CF's two
  misses (593 / 523 ms) were the same effect on the new exe; D8's passes (213 / 228 ms) the fast side of it on the old one.
- Information (registered): the 8-cell spread is 306 ms (>= 100: yes) and is NOT sorted by binary (yes). Free bytes fall
  monotonically by 393 KB over the round and do not track it; C:\DOSAGS grows by one entry per cell (86 -> 95) and does not track it.
  The only field that separates the fast cell is the file shrinking (n = 1; D8S8's 228 ms after a GROWING write says it is not the
  whole story). SMARTDRV /S identical in all 8 (4 MB, C: read cache yes / write cache no = write-through).
- Leading remaining explanations (sdlports): the CF card's own write latency (housekeeping) and DOS's FAT free-cluster search on
  allocation. Not separated by this round.
- Known, symmetric perturbation (sdlports' note): the four redirect files (SVPRE, DIRLIST, SDRV, SVPOST) are written in C:\DOSAGS just
  before / after the engine in every cell of both arms; after the first cell they are overwritten in place.

## Consequences
- 0366 / 0367 are cleared of a start-up regression: round CF's S32P / S8 whole-run misses are rig-side restart-save timing.
- The gate bar's whole-run figure has ~0.1-0.2 of day-to-day start-up noise around 39.2 on S32P / S8 with EITHER binary. That is a
  property of the bar and the rig, recorded here; the bar is not changed by this round. Options for the operator / coordinator
  (not decided here): a faster or deferred restart-point write (exactness to be argued), or reading whole-run from loop start.

## Rig (vcctrl)
No USB event; one harness recovery (SU8B1, above); daemon unchanged. 5 corrupt capture frames (decode_errs 50 of 1,259,878), at
06:22:41 / 06:22:50Z (SU8A1 launch) and 06:49:32 x2 / 06:49:41Z (SU8B2 launch). jobs/: the last 16 file jobs (the WARMUPSU send and
pull had aged out of vcctrld's last-16 list when read).

Files: SUMMARY.txt, driveSU.sh / cellSU.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt, jobs/;
per cell GATEBAR.txt, SVPRE.TXT, SVPOST.TXT, DIRLIST.TXT, SDRV.TXT. Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt).
