# S7 -- OPL3 register-write cost diagnostic, real-hardware result -- 2026-09-14

Continuation of `S7-regwrite-diag-dosboxx-2026-09-14.md`. Operator-approved
single real-hardware cell, HW-486-66, to test the hypothesis that
hypothesis document raised: does `SDL_DOSOpl3WriteRegister()`'s own cost
(the "6 dummy status reads x2" AdLib delay loop) explain most of
`slots_us`'s real-hardware blowup. **Result: partially confirmed, but the
underlying mechanism is different from the hypothesis as originally
stated -- see "What this changes" below.**

## Cell

Same recipe as `AUDIOFX1` (`S7-audioprb-fix-realhw-2026-09-14.md`), new
tag: `run-rig.sh trilbysnotes --tag AUDIOFX2 --env DOSAGS_FIXED_TIMESTEP=1
--env DOSAGS_TAS_AUTO_EXIT_TICK=200 --env SDL_HINT_DOS_AUDIO_BACKEND=opl3
--extra-file ACSETUP.CFG:ACSETUP.CFG`. Binary `binary_sha12=342a0b306336`,
confirmed matching `make build-sha12` against the committed tree at
`db0b56e`/`99b62c7` (SDL/0141 + ags/0062 applied, discard-snapshot fix
included) -- the exact diagnostic validated under DOSBox-X, unmodified,
ran on real hardware.

**A real harness bug surfaced during collection**: the underlying vcctrl
pull job finished cleanly (`running: false`, `AUDIOFX2.LOG` and the other
core files verified and retrievable) several minutes before `run-rig.sh`'s
own `wait_for_job_done` (called after `vc get-file`) detected that and let
the script proceed -- confirmed by querying `vc file-status` directly
while the script sat in its poll loop (`sleep 10`, not stuck in a hung
subprocess) well past the job's own `finished_at` timestamp. Not yet
root-caused; the data was recovered directly via `vc pulled save` per
file instead of waiting on the wrapper, and the stuck script process was
stopped. Screenshot files (`PH01-3.BMP`) never came back (`"a file did
not come back and the prompt's state cannot be trusted -- stopping
rather than typing blind"`) -- not needed for this cell's question, not
chased further. Worth a follow-up fix to `run-rig.sh`'s collect-phase
wait loop; not fixed this session (out of scope for the S7 question, and
the workaround already got clean data).

## Result

```
[RUNMANIFEST-BEGIN]
schema_version=1
environment=realhw
binary_sha12=342a0b306336
wave_tag=AUDIOFX2
duration_s=79
exit_code=0
fps_p50=0.58
fps_p95=0.63
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=639
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT memory_min_free_kb=154880
DOS-PORT tick_rate=2.96 frames_skipped=168
DOS-PORT audioprb total_calls=65 windows_recorded=1 windows_dropped=0
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=17 mean=2268 max=34203) pump_us(min=5991 mean=11082 max=15240) regwrite(calls=4434 min_us=20 mean_us=21 max_us=123)
```

Clean run (`exit_code=0`, `critical_count=0`, `warn_count=0`), real OPL3
chip path (`STDOUT.TXT`: "DosMidiBackend: OPL3/OPL2 chip detected and
initialized"). Remarkably close to `AUDIOFX1`'s own workload shape
(`total_calls=65`, `duration_s=79`, `events=639` -- identical;
`tick_rate=2.96` vs `2.97` -- noise): this is a deterministic TAS-style
replay with no player input, so the underlying game execution is
essentially unchanged between the two cells. The only real difference is
the diagnostic itself.

## regwrite explains most of slots_us's mean -- but not the way the hypothesis predicted

`regwrite` total time this window: `4434 * 21us = 93.1ms`, spread across
65 calls =~ **1433us/call, 63% of `slots_us`'s own mean (2268us)**. That
is a real, substantial fraction -- register I/O genuinely is most of
what `slots_us` measures on real hardware, not a rounding error.

But `regwrite`'s own **per-write mean (21us) is not anomalous** -- it is
in the same range as DOSBox-X's own regwrite measurement (21-23us,
`S7-regwrite-diag-dosboxx-2026-09-14.md`). The original hypothesis was
that a single `SDL_DOSOpl3WriteRegister()` call costs far more on real
hardware than the "~1us per dummy read, bullet-proof" comment assumes
(the PicoGUS-firmware-vs-real-silicon angle, reinforced by the MPU-401
IOCHRDY precedent). **This measurement does not support that** -- at
least not at a magnitude anywhere near what would be needed to explain
`slots_us`'s blowup through per-write cost alone.

What actually differs is **volume**: `4434` writes over `65` calls
(**68.2/call**) vs DOSBox-X's `210` writes over `188` calls
(**1.12/call**) -- and even per dispatched MIDI event, real hardware
needed `6.94` writes/event vs DOSBox-X's `3.89`. The likely reason isn't
a hardware difference in the events themselves: `midi_sched_tick()`'s
playback position is driven by real wall-clock (`uclock()`), not game
ticks, and the SAME `DOSAGS_TAS_AUTO_EXIT_TICK=200` cap corresponds to
wildly different real elapsed time in each environment -- `9s` under
DOSBox-X `--fast`/`cycles=max` vs `79s` on real hardware (the same
collapse this whole investigation is about). Given only 65 real
audio-serviced ticks survive across that 79s on real hardware, each
surviving `audio_core_entry_poll()` call's `midi_sched_tick()` has to
catch up a correspondingly larger chunk of the song's timeline in one
shot -- more due events per call, hence more register writes bunched
into each call. **The register-write volume is a downstream symptom of
the same tick-starvation collapse already known to be the core problem,
not an independent OPL3-hardware-timing defect.**

## A real methodological caveat: the diagnostic's own overhead is not free on real hardware

`slots_us` itself did NOT reproduce between `AUDIOFX1` (mean=1403,
max=15270, no regwrite instrumentation) and this cell (mean=2268,
max=34203, regwrite instrumentation added) despite the underlying
workload being essentially identical (same call count, same event count,
same duration). The delta (865us/call) divided by the average write
count (68.2/call) works out to **~12.7us of apparent added cost per
register write** -- suspiciously close to `regwrite`'s own reported
21us/write mean. The most likely explanation: `uclock()` itself (a
PIT-channel-0 read + conversion) is not free on real DOS/486 hardware,
and this diagnostic calls it **twice per register write** (4434 writes
this window = 8868 extra `uclock()` calls). At this granularity (tens of
microseconds per operation), the measurement instrument's own cost is
plausibly a significant fraction of what it's measuring -- the same
"your measurement instrument can lie" class of hazard `docs/audio.md`
already documents for a PIT-driven pump corrupting SDL's own clock,
applied here to a much smaller timescale. This means `regwrite`'s
absolute `mean_us=21` likely overstates the TRUE underlying per-write
cost somewhat; if anything, correcting for that moves the real number
further from the original hypothesis, not closer to it.

**One data point, one cell -- the same caveat as every real-hardware
result in this investigation.** Both the volume-vs-event-timeline
explanation and the measurement-overhead caveat are inferences from a
single window's numbers, not independently re-confirmed.

## What this changes

The originally-proposed next step ("bisect the 12-dummy-read assumption,
A/B a reduced read count") is **not well-motivated by this result** --
per-write cost isn't the anomaly here, so cutting the delay loop would
likely buy little. The productive next step is back where the
investigation's second round left off: **why do so few real GameTicks
ever reach an audio-serviced point** (`tick_rate` collapsing to ~2.96-2.97
regardless of what's been tried so far -- patch 0060's call-count
reduction, this diagnostic's own register-write-volume finding). That is
the fixed-timestep/audio-poll interaction root cause this whole S7
investigation started from, not a new OPL3-specific lever.

Patches 0059, 0060, 0061 (ags), SDL/0141, and ags/0062 all stay landed,
all still temporary. Acceptance gate items 4 and 5 remain FAIL.

## Not yet done

1. `run-rig.sh`'s collect-phase `wait_for_job_done` anomaly (this
   session's own finding) -- not root-caused, not fixed.
2. `wait_for_stable_screen()`'s low-fps false-positive bug -- still open,
   sidestepped again via the short tick cap.
3. No further real-hardware register-write-timing work is recommended
   without a new, source-grounded hypothesis -- the PicoGUS-per-op-cost
   theory this diagnostic was built to test did not hold up.
4. Acceptance gate items 4 and 5 remain FAIL; no re-attempt this cell.
