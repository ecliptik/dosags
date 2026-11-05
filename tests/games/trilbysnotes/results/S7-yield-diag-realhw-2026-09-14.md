# S7 -- DOS_Yield() diagnostic, real-hardware result: yield-switching ruled out -- 2026-09-14

Continuation of `S7-yield-diag-dosboxx-2026-09-14.md`. Operator-approved
cell (tag `AUDIOFX4`, `binary_sha12=7d2309fcdef7`), same recipe as
`AUDIOFX1`-`3`. `run-rig.sh` completed cleanly end to end again (no
recurrence of the `AUDIOFX2` collect-phase stall).

## Result

```
DOS-PORT tick_rate=2.97 frames_skipped=168
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=16 mean=2283 max=34355) pump_us(min=6440 mean=11392 max=15245) regwrite(calls=4434 min_us=20 mean_us=21 max_us=219)
DOS-PORT tickfx total_calls=34 window_calls=34 catchup_n_sum=167
  catchup_us(min=775489 mean=1998419 max=29093073)
  realtick_us(min=96212 mean=408063 max=466797)
  catchup_yield(switches=2 min_us=243 mean_us=736554 max_us=1472865)
  realtick_yield(switches=704 min_us=37 mean_us=76620 max_us=3412312)
```

Same collapsed regime as every prior sound-on cell (`tick_rate=2.97`,
same `events=639`, `duration_s=79`), and `catchup_us`/`realtick_us`
reconfirm `AUDIOFX3`'s own numbers almost exactly (407.2ms/tick class of
result, reproduced). This time the diagnostic caught what actually
happens with the scheduler.

## Yield-switching does NOT explain the catch-up tick tax

```python
catchup total time (34 calls, mean=1998419us each):  67.95s
catchup yield-switch total time (2 switches):          1.47s
fraction of catchup time explained by yield-switches:  2.2%
```

**Only 2 real `DOS_Yield()` switches happened during the ENTIRE
catch-up burst across all 34 `dos_run_tick_fixed()` calls (167
individual catch-up ticks total).** Even taking their summed duration
at face value (1.47s), that is a small fraction (2.2%) of the 67.95s
the catch-up ticks actually cost this window. **This rules out, with
real data rather than a DOSBox-X proxy, the cooperative-scheduler-yield
hypothesis this investigation has been pursuing since
`S7-tick-starvation-source-investigation-2026-09-14.md`.** Whatever
costs a catch-up `UpdateGameOnce()` call ~407ms on real hardware, it is
not being switched away to the audio thread (or anything else) via
`DOS_Yield()`. The DOSBox-X sanity run's own directional finding
(near-zero catch-up switches) generalized correctly this time, even
though DOSBox-X itself doesn't reproduce the underlying collapse.

## A real measurement-methodology finding: yield brackets can overlap across threads

`realtick_yield`'s summed duration (704 x 76620us = 53.94s) **exceeds**
the entire `realtick_us` window it's supposed to fit inside (13.87s
total across 34 calls) -- structurally impossible if every yield
bracket were a clean, non-overlapping round trip. The likely mechanism:
`DOS_YieldDiagSnapshot()`'s underlying counters are global, not
per-thread -- `DOS_Yield()` is instrumented once, at the scheduler
level, so a call made by the autonomous `PlaybackAudioThread` (e.g.
inside its own `WaitDevice()` ring-full spin loop, which calls
`DOS_Yield()` on every iteration while waiting) is counted and timed
exactly the same as a call made by main. While main's own yield-out
bracket is still open (waiting to be switched back to), the audio
thread can make several of its *own* `DOS_Yield()` calls, each with its
own bracketed duration -- these overlap main's own bracket in real wall-
clock time, and summing all of them independently double- (or multi-)
counts real time rather than partitioning it. This does not invalidate
the catch-up finding above (2 switches, unambiguous either way), but it
means `realtick_yield`'s own `mean_us`/`max_us` should be read as "total
scheduler churn attributable to yields touched during this phase,"
not "cost of one clean round trip" -- a real caveat on this
instrument's own design that would need per-thread attribution to fix
properly (out of scope for this investigation).

## Where this leaves the investigation

Two real mechanisms are now conclusively ruled out as explanations for
the catch-up-tick tax specifically: `audio_core_entry_poll()`'s own
direct cost (regwrite result), and cooperative-scheduler yield-switching
(this result). Both were well-motivated, source-grounded hypotheses,
and both failed real-hardware testing. What remains: something applies
a near-uniform ~9.7x tax to *every* `UpdateGameOnce()` call, catch-up
included, that is not mediated by explicit yields.

**A new candidate, qualitatively different from everything tested so
far**: real ISA-bus DMA cycle-stealing. The Sound Blaster's DMA
controller actively streams the whole time the device is open
(`pcm=sb@11025m16` in every sound-on cell); on some ISA-bus chipsets, an
active DMA channel can add real wait-states to *ordinary* CPU bus
cycles (memory/IO access), independent of any software scheduling --
this would tax literally every instruction touching the bus, uniformly,
for as long as the DMA is running, with no dependency on which code path
executes or whether it yields. This would explain: the uniform
catch-up-vs-real-tick tax (both run instructions on the same bus); why
sound-off is ~9.7x cheaper (no DMA channel active at all); and why
DOSBox-X does not reproduce it (an emulator's own bus-timing model has
no reason to charge cycle-stealing overhead the way real ISA hardware
electrically does). This is a hardware/electrical hypothesis, not a
software one -- it cannot be confirmed or refuted by more source reading,
and would need either hardware/chipset documentation research or a
differently-shaped empirical test (e.g. isolating "SB16 device open,
IRQ armed" from "DMA channel actively transferring" to see whether the
tax tracks DMA activity specifically rather than mere device state).

Patches 0059-0064 all stay landed, all still temporary. Acceptance gate
items 4 and 5 remain FAIL.

## Not yet done

1. The DMA-cycle-stealing hypothesis is untested -- no experiment has
   been designed or run.
2. `regwrite`'s pre-existing data-corruption bug (flagged in the DOSBox-X
   entry) did NOT recur in this real-hardware cell's own `regwrite` line
   (clean: `mean_us=21 max_us=219`) -- consistent with it being a rare,
   intermittent `uclock()` non-monotonicity hazard rather than something
   this session's patches introduced.
3. The per-thread yield-attribution gap (above) is a real instrument
   limitation, not fixed.
