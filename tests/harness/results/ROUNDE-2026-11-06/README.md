# Round E -- 2026-11-06: VM slice 3 on the 486 -- MMD GAIN (91.5% displayed, x2), short of 99% and of its band; 5 Days S16 with the fast VM MET

One power-on 04:51:28Z-05:57:28Z (driver; powerguard confirmed OFF 05:57:32Z), cap 06:16:28Z not reached; every cell exit 0,
stamp matched, pre-stage = staged = post-run. Operator's standing order (ORDER-CONFIRMED). Pre-registrations 9c98045d.
Binary VM3REL.EXE (lab release of vm-slice3.diff, 1781fe2bf36c, build_dirty=1 -- figures read from the manifests, as
registered); the arm is the env only. BLASTER.TXT "A220 I7 D3 P330 T3" in every cell. vcctrl: no USB event (dev 41 all
round), 2 corrupt video frames (05:29:19, 05:40:20Z), audio and camera captured throughout; no cell here is scored from audio.

| Cell | Arm | whole / steady | fps_p50 | displayed (1 - skipped/ticks) | audio counters | verdict |
|---|---|---|---|---|---|---|
| WARMUPE | l308 | 29.95 / 32.95 | -- | -- | -- | not scored; capture locked after |
| VM3A1 | legacy | 34.70 / 35.42 | 9.95 | 27.97% | clean | A as predicted (20-35%, 35.0-37.5) |
| VM3B1 | fast (6 superops) | 39.00 / 39.99 | 36.89 | **91.52%** (424 skipped) | clean | **GAIN** |
| VM3B2 | fast | 39.07 / 39.99 | 36.89 | **91.56%** (422 skipped) | clean | **GAIN** |
| VM3A2 | legacy | 34.65 / 35.43 | 9.96 | 27.97% | clean | A as predicted |
| VM3S16 | fast, 5 Days S16 | 39.30 / 40.08 | 40.00 | **99.38%** (presents 100.24%) | clean incl. late_writes 0 | **MET** (no regression) |

env_block_sha differs A vs B (33f0861465fe / b2a6255591e3); vmmode lines legacy mode=0 / fast mode=3.

## E1 (MMD character select ABBA) -- scored as registered
- GAIN (both B >= 90% and steady >= 39.2): **met**. The 99% line (both B >= 99.0%): **not met**. FALSIFIER (either B < 88%):
  not tripped. The registered prediction (B 95-100%) **missed on the low side**.
- vs slice 2 (F1b VMB1/VMB2 86.94% x2, 653 skipped): +4.6 points, 424 skipped. Slice 3 cut 16% of the VM's time at fixed
  40k cycles; the 486 shows less. The suspect named before the run is the hot loop (4.4 -> 6.7 KB) against the 486's 8 KB
  cache; untested -- no profile cell this round.
- Under PLAN-FPS's wall rule this is the first lever to miss its band (slice 2 met its own).

## E2 (VM3S16, F1b's deferred D3) -- MET
Prediction met on every line: whole 39.30 (39.15-39.40), steady 40.08 (40.0-40.3), displayed 99.38% (>= 99.3%), fps_p50
40.00, overwrites / underruns / silent_irqs / late_writes 0. Camera sheet: 5 Days room 3 on the LCD from 21:50:28 PST, the
character in a different place frame to frame through 21:52:23; dark from 21:52:33 (the TAS exit: 5,000 ticks at 40/s
after the room's entry) -- CLEAN. The fast VM costs nothing at the gate.

## Workspace note
build/ws/roundE already existed from a September round (its old executables and SUMMARY lines stayed in place); the driver
appended. The guard keyed on this round's relay-on line and confirmed the right cap; SUMMARY.txt here is this round's part
only. New rounds use a never-used workspace name.

Files: SUMMARY.txt, driver and helpers, ORDER-CONFIRMED, POWERGUARD.txt, jobs/*.json.
