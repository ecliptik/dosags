# Round N7 -- 2026-11-06: the shipped build carries L5 -- MMD 99.90% displayed x2 at 40.00 ticks/s; S16 / S32P / S8 MET; AGS Quest unchanged

One power-on 14:12:59Z-15:26:16Z (driver exit 0; powerguard confirmed OFF 15:26:22Z), cap 15:52:59Z not reached. Operator's
standing order (ORDER-CONFIRMED); pre-registrations 2d636de2. Binary n7rel.exe = main c284ddfd release (ags 0001-0365, the
script VM and engine levers on by default), stamp c754df64babd, build_dirty=0, sha256 d680e3b6... (byte-identical to the
lab-gated LREL.EXE); every cell exit 0, stamp OK, pre = staged = post. No VM/lever env in any RUN.BAT: every scored cell's
STDOUT reads "vmmode DOSAGS_VM=(default) mode=3" and "englev DOSAGS_ENGLEV=(default) on=1". BLASTER.TXT "A220 I7 D3 P330 T3"
in all seven cells.

| Cell | scene | whole / steady | fps_p50 | displayed (1 - skipped/ticks) | presents / passes | audio | witness | verdict |
|---|---|---|---|---|---|---|---|---|
| WARMUPN7 | l308, MMD title | 30.08 / 32.96 | -- | -- | -- | -- | nolock (as always) | not scored; close-watch passed |
| N7M1 | MMD character select | 39.08 / 40.00 | 40.00 | **99.90%** (5 of 4,999) | 100.24% | clean | camera CLEAN | **MET** |
| N7M2 | MMD character select | 39.08 / 40.00 | 40.00 | **99.90%** (5 of 4,999) | 100.24% | clean | camera CLEAN | **MET** |
| N7S16 | 5 Days room 3, 16-bit 512x384 | 39.24 / 40.13 | 40.00 | 99.44% (28) | 100.24% | clean, 930 = 930 | camera CLEAN | **MET** (band 99.3-99.6) |
| N7S32 | 5 Days room 3, 32-bit 640x480 | 39.26 / 40.10 | 40.00 | 99.52% (24) | 100.24% | clean, 576 = 576 | capture CLEAN | **MET** (= GR32P) |
| N7S8 | Trilby room 35, 8-bit | 39.23 / 40.23 | 40.00 | 99.32% (34 of 5,002) | 100.28% | clean, 2073 = 2073 | camera CLEAN (dark room) | **MET** (band bottom) |
| N7AQ | AGS Quest AutoPilot | 19.55 / 41.09 | 39.96 | 93.04% (249 of 3,576) | -- | -- | capture ok | exit 0, 18 phases ok; information |

- MMD: the falsifier (either cell < 99.0%) is not tripped; the shipped build reproduces L5's lab figure exactly (99.90%, 40.00).
  Whole-run 39.08 is below PLAN-GATES' 39.2 band (gatebar prints NOT MET on it): stall_ms 966 / 970, the boot room load --
  target (b), as L5's 39.13. MMD is not a gate scene; its registered line is steady + displayed.
- S8 at 99.32% is the band's bottom (R1R1 / R1R2: 26 / 28 skipped, here 34): within one reading's spread; the v0.1 round's
  second gate reading decides whether it is real.
- AGS Quest: displayed 93.04% with 249 skipped -- the same count as F1AQK on the pre-VM release; stall_ms 91,966 (F1AQK 89,926).
  The fast VM and levers do not move it: its cost is GUI + room loads (target d), as registered. No image committed (IMAGE-SHA256.txt).
- Camera sheets: MMD character select through the span; 5 Days room 3 with the character moving; room 35 dark as in GL8A/R1.
- Rig (vcctrl): 3 single corrupt capture frames (14:48:45.7Z in N7S16, 15:09:06.5Z in N7S8, 15:15:32.1Z at N7AQ's boot);
  decode_errs 33 -> 40; no USB kernel event, no recovery cycle, stick present, audio spawns 1, camera capturing throughout.
  vcctrld daemon_start_t unchanged (1793917032.97). 14 file jobs (jobs/), every one complete.

Files: SUMMARY.txt, driveN7.sh / cellN7.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
jobs/*.json, GATEBAR.txt per scored cell. Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt).
