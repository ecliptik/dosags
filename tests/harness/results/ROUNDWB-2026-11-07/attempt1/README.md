# Round WB, attempt 1 -- 2026-11-07 17:55:41Z-18:06:16Z: no test cell ran (my time-budget error); no write-behind was ever enabled
Relay-on 17:55:41Z; WARMUPWB ran (exit 0, stamp OK, BLASTER ok, capture locked) and its SMARTDRV /? syntax check PASSED on the
target (SDHELP.TXT: "SMARTDRV [/X] [[drive[+|-]]...] ... + Enables write-behind caching ... /C Writes all information currently in
write-cache to hard disk"); SDRV0.TXT: C: read cache yes, write cache no; CHKDSK1.TXT: no errors, 7,881 free clusters, 6,881 files.
Then need() dropped the whole ABBA at 18:06:11 (6030 s left < 6080 s needed) and the driver powered off (18:06:16; guard confirmed
OFF 18:06:23). Cause: I kept SW1's 760 s-per-cell thresholds (8 x 760 = 6080) while sizing CAP_MIN at 115 instead of 120 -- the
budget could never fit after a 10.5-minute warm-up. No WB cell started, so there was no cache exposure; CHKDSK2 was not needed for
safety, but per amendment 6 the next power-on still begins with CHKDSK C:. Files: the as-run driveWB.sh / powerguard.sh,
SUMMARY.txt, POWERGUARD.txt, ORDER-CONFIRMED; WARMUPWB-2026-11-07/ holds the warm-up's SDHELP / SDRV0 / CHKDSK1.
