# Round V1 -- 2026-11-06: the v0.1 zip PASSES as shipped (DIST2); gate second readings: S16 MET, S32P / S8 NOT MET on whole-run only

One power-on 15:36:31Z-16:28:15Z (driver exit 0; powerguard confirmed OFF 16:28:24Z), cap 16:51:31Z not reached. Operator's
standing order (ORDER-CONFIRMED; measurement only); pre-registrations 4527978b. Binary distv1.exe = AGS.EXE of
build/dist/dosags-v0.1.zip (sha256 c0c6fe00...) = release c754df64babd (main c284ddfd), the exe round N7 measured. Every cell
exit 0, stamp OK, pre = staged = post; defaults witnessed ("vmmode (default) mode=3", "englev (default) on=1"); BLASTER.TXT
"A220 I7 D3 P330 T3" in all five. First round after vcctrl's FTP rotation (daemon_start_t 1793979061.92).

| Cell | whole / steady | fps_p50 | displayed | audio | preloop / tail ms | witness | verdict |
|---|---|---|---|---|---|---|---|
| WARMUPV1 | 29.81 / 33.02 | -- | -- | -- | -- | nolock | not scored; close-watch passed |
| DIST2 (zip, README.TXT settings) | 39.22 / 40.17 | 40.00 | 99.42% (29) | clean, 1558 = 1558 | 952 / 839 | camera CLEAN | **PASS** |
| V1S16 | 39.21 / 40.13 | 40.00 | 99.40% (30) | clean | 926 / 1056 | camera CLEAN | **MET** |
| V1S32 | **39.18** / 40.12 | 40.00 | **99.64%** (18) | clean | 1004 / 710 | capture CLEAN | **NOT MET** (whole-run < 39.2) |
| V1S8 | **39.13** / 40.25 | 40.00 | 99.44% (28) | clean | 971 / 1058 | camera CLEAN (dark) | **NOT MET** (whole-run < 39.2) |

- DIST2: every PASS condition met -- exit 0, room 3, fixed timestep on (release default), OPL3 detected, music 0, 7 clips played
  (10 x5, 9 x2), gatebar S16 MET, camera CLEAN. RUN.BAT carries only the log tags and the TAS exit. The v0.1 zip plays at the
  gate rate with music and effects, as shipped.
- V1S32 / V1S8 miss PLAN-GATES' whole-run band by 0.02 / 0.07 and are recorded NOT MET as registered (REGRESSION line: a tick
  figure out of band). In-play figures are at or above N7's (displayed 99.64 / 99.44%, steady 40.12 / 40.25; the game loop's own
  time is equal: loop_ms 125,936 / 125,773 vs N7 126,004 / 125,815). The difference is outside the loop: engine start-up before
  the first tick (preloop) 926-1,004 ms in every V1 cell vs 722-864 ms in N7's three, and the exit tail 710-1,058 vs 533-843 ms,
  on the byte-identical exe. Systematic across this round, cause not named (the card's files changed in the FTP rotation
  between the rounds; disk/DOS state is a candidate). Target (b), not a speed-up regression.
- Shipped-exe gate record (c754df64babd): S16 MET x2 (N7S16, V1S16); S32P MET x1 + NOT MET x1; S8 MET x1 + NOT MET x1; MMD
  99.90% x2 (N7). The operator decides what v0.1 claims.
- Rig (vcctrl): 3 single corrupt capture frames (15:50:48.6Z in DIST2, 16:11:10.7Z in V1S32, 16:21:55.3Z in V1S8), decode_errs
  0 -> 9; no USB event, no recovery; V1S32's capture sheet is clean (the corrupt frame is not on it). 10 file jobs (jobs/).

Files: SUMMARY.txt, driveV1.sh / cellV1.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
jobs/*.json, GATEBAR.txt per scored cell. Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt).
