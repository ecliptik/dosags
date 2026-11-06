# Round L5 -- 2026-11-06: MMD MEETS the 99% line on the 486 -- 99.90% displayed x2 at 40.00 ticks/s (engine levers on, VM fast); 5 Days S16 MET

One power-on 10:23:28Z-11:27:06Z (driver; powerguard confirmed OFF), cap 11:53:28Z not reached; every cell exit 0, stamp
matched, pre = staged = post. Operator's standing order (ORDER-CONFIRMED). Pre-registrations a73ebe8c. Binary VM9REL.EXE (lab
release of vm-slice3c.diff = VM slice 3 + engine levers 1, 2, 3), stamp 23fd25201ec9, build_dirty=1 -- figures read from the
manifests, as registered. STDOUT's "englev DOSAGS_ENGLEV=<arm> on=<arm>" and "vmmode DOSAGS_VM=fast mode=3" matched every
cell; BLASTER.TXT "A220 I7 D3 P330 T3" everywhere; audio counters clean everywhere. vcctrl: no USB event; one corrupt video
frame (10:59:47Z, inside L5B2, which is not scored from the capture).

| Cell | levers | whole / steady | fps_p50 | displayed (1 - skipped/ticks) | presents / passes | verdict |
|---|---|---|---|---|---|---|
| WARMUPL5 | -- | 30.21 / 32.95 | -- | -- | -- | not scored; capture locked after |
| L5A1 | off | 39.13 / 39.99 | 36.27 | 91.28% (436) | -- | A in band (88.5-92.0) |
| L5B1 | **on** | 39.13 / 40.00 | **40.00** | **99.90%** (5) | 100.24% | **MET** |
| L5B2 | **on** | 39.13 / 40.00 | **40.00** | **99.90%** (5) | 100.24% | **MET** |
| L5A2 | off | 39.13 / 39.99 | 36.27 | 91.24% (438) | -- | A in band |
| L5S16 | on, 5 Days S16 | 39.29 / 40.17 | 40.00 | **99.52%** (24) | 100.24% | **MET** (no regression) |

## L5 ABBA -- scored as registered
- B - A = +8.62 / +8.66 points (predicted +7 to +10.5). GAIN (>= +3.0 both pairs): met. **MET (both B >= 99.0%): met.**
  FALSIFIER (B - A < +2.0): not tripped. Drift within the round: 0.04 points.
- The 486 saw far more than fixed cycles predicted (fixed-40k x r 0.34 would give ~+1.9 points): the levers were estimated
  from 486 samples, and the named mechanism (cache misses over 102 CharacterInfo records, not modelled by DOSBox-X) fits.
- MMD character select over the campaign: 25-28% displayed at 36.5 ticks/s (legacy) -> 99.90% at 40.00 (fast VM + levers).

## L5S16 -- MET
Every prediction line met: displayed 99.52% (99.3-99.6), whole 39.29 (39.15-39.40), steady 40.17 (40.0-40.3), fps_p50 40.00;
overwrites / underruns / silent_irqs / late_writes 0. Camera sheet: 5 Days room 3 on the LCD, the character in a different
place frame to frame, dark after the TAS exit -- CLEAN.

## What this is and is not
A lab binary (build_dirty=1), and the VM / levers default OFF in it (env-selected). The KPI claim for a shipped build needs
the series landed in patches/ags, fast + levers made the default, and an x2 re-run on the clean main release build (PLAN-FPS).

Files: SUMMARY.txt, driver and helpers, ORDER-CONFIRMED, POWERGUARD.txt, jobs/*.json.
