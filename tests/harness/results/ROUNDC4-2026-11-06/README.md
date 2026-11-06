# Round C4 -- 2026-11-06: the cache hypothesis is FALSIFIED on both readings -- slice 3's 486 shortfall is not the 8 KB cache

One power-on 06:05:55Z-07:21:11Z (driver; powerguard confirmed OFF 07:21:13Z). Operator's standing order (ORDER-CONFIRMED).
Pre-registrations a6d0d8ac. Same binaries as round E: VM3REL.EXE 1781fe2bf36c (R4*), VM3INS.EXE 4bbb3f1224a5 (P4*, fine timing
on), both build_dirty=1 (figures from the manifests). Every cell exit 0, stamp matched, pre = staged = post; the "vmfuse mask="
STDOUT line and RUN.BAT's SET named the arm's mask in every cell; BLASTER.TXT correct; audio counters clean everywhere.
P4N NOT RUN: the cap guard dropped it (650 s left < 700 s; cells took ~12.5 min, not ~11). vcctrl: capture fully clean all
round (no USB event, no corrupt frame).

| Cell | mask | displayed | fps_p50 | script_vm ms/tick | render ms/pass |
|---|---|---|---|---|---|
| R4F | 0x3F all six | 90.16% (492 skipped) | 36.13 | -- | -- |
| R4B | 0x03 farcall + localload | 88.72% (564) | 35.29 | -- | -- |
| R4N | 0x00 fusion off | 87.52% (624) | 35.12 | -- | -- |
| P4F | 0x3F | 73.81% (fine timing on; not a KPI reading) | 29.35 | **12.689** | 6.525 |
| P4B | 0x03 | 71.71% (fine timing on) | 28.94 | **12.859** | 6.530 |

All cells steady 39.99. Scored as registered:
- Release: **R4B - R4F = -1.44 points <= -1.0 -> the cache hypothesis is FALSIFIED**; inside H-CPI's -1.1 to -1.7.
  R4N - R4F = -2.64 (H-CPI predicted -3.0 to -4.7: missed small). R4F 90.16% under its 91.0-92.0 band (round E's arm read
  91.5%: across-round drift, the draft's ~1.2 points).
- Profile: **P4B - P4F = +0.170 ms/tick >= +0.08 -> FALSIFIED**; P4F 12.689 inside 11.7-12.9; render per pass unchanged.
- Both readings agree, so the claim is made: dropping ~1.1-1.5 KB of executed superop code costs time on the 486, it does
  not save it. The 6.7 KB hot loop is not what held slice 3 below its band; the 486 simply realizes less per fixed-cycle
  ms saved than the model assumed (release: ~0.24 ms of logic for 0.701 fixed ms, r ~0.34; information only -- P4N, which
  was to measure r directly, did not run).
- Consequence: all six superinstructions stay. The next MMD gains are engine-side (docs/lab/MMD-REMAINDER.md: character
  update skip, GetCharIDAtRoom memo; lever 3 exact in the lab).

Files: SUMMARY.txt, driver and helpers, ORDER-CONFIRMED, POWERGUARD.txt, jobs/*.json.
