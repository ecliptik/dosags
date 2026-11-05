# S7 -- dos_run_tick_fixed() catch-up-vs-real-tick, real-hardware result -- 2026-09-14

Continuation of `S7-tickfix-diag-dosboxx-2026-09-14.md`. Operator-approved
single real-hardware cell (tag `AUDIOFX3`, `binary_sha12=ec9459908706`,
matching `make build-sha12`), same recipe as `AUDIOFX1`/`AUDIOFX2`. This
time `run-rig.sh` completed cleanly end to end (including the screenshot
files that failed to come back in the `AUDIOFX2` cell) -- the collect-phase
stall observed last time did not recur.

## Result

```
[RUNMANIFEST-BEGIN]
environment=realhw
binary_sha12=ec9459908706
wave_tag=AUDIOFX3
duration_s=79
exit_code=0
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=639
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=2.96 frames_skipped=168
DOS-PORT audioprb total_calls=65 windows_recorded=1 windows_dropped=0
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=18 mean=2261 max=33959) pump_us(min=6405 mean=11257 max=15141) regwrite(calls=4434 min_us=21 mean_us=21 max_us=223)
DOS-PORT tickfx total_calls=34 windows_recorded=1 windows_dropped=0
DOS-PORT tickfx total_calls=34 window_calls=34 catchup_n_sum=167 catchup_us(min=776476 mean=2000193 max=29037896) realtick_us(min=87510 mean=409471 max=474587)
```

Clean run, same collapsed regime as every prior sound-on cell
(`tick_rate=2.96`), `audioprb`'s own numbers reconfirm the regwrite result
(`slots_us`/`pump_us`/`regwrite` all consistent with `AUDIOFX2`).

## The answer: the tax is uniform, not concentrated in either bucket

```python
catchup_n_per_call = 167 / 34            = 4.91   # of a MAX_CATCHUP=5 cap -- saturated
per_catchup_tick_us = 2000193 / 4.91     = 407225  # 407.2ms per INDIVIDUAL catch-up tick
realtick_us mean                          = 409471  # 409.5ms for the one real tick
```

**A single catch-up `UpdateGameOnce()` call (logic-only: no render, no
`WaitForNextFrame()`, and -- since patch 0060 -- no `audio_core_entry_
poll()` either) costs 407.2ms on average. The one real tick (renders,
waits, and does poll audio) costs 409.5ms. These are the same number,
within 0.5%.**

Comparing against the sound-off baseline (`S7-abba-2026-09-13.md`:
`tick_rate=23.8-23.9`, i.e. ~42.0ms/`UpdateGameOnce()` call, aggregated
across catch-up and real ticks alike, since that arm is also permanently
catch-up-saturated):

| | ms/`UpdateGameOnce()` call | vs. sound-off |
|---|---:|---:|
| sound-off (any tick) | ~42.0 | 1x (baseline) |
| sound-on, catch-up tick | 407.2 | **9.7x** |
| sound-on, real tick | 409.5 | **9.7x** |

**This is the actual finding this whole diagnostic chain was built to
get: whatever the mechanism is, it applies almost exactly the SAME
~9.7x multiplier to EVERY `UpdateGameOnce()` call once the audio device
is open -- independent of whether that call renders, waits, or touches
audio at all.** Catch-up ticks don't call `audio_core_entry_poll()`
(patch 0060), don't render, and don't call `WaitForNextFrame()`'s pacing
wait -- and still cost essentially the same as the one tick that does
all three. This rules out, conclusively, every hypothesis this
investigation has tested so far that was scoped to "audio servicing
cost" or "how often audio gets polled": `audio_core_entry_poll()`'s own
cost (pump_us/slots_us/regwrite, all separately measured and all far too
small), the poll-count multiplier patch 0060 targeted, and register-write
volume/cost (this session's earlier regwrite result). None of those are
large enough or gated correctly to produce a near-identical tax on a
call path that does not invoke any of them.

## What this points at instead

The mechanism must be something reachable from **every** `UpdateGameOnce()`
call, unconditionally, near its entry (both catch-up and real ticks pay
it, and pay almost exactly the same amount). The strongest structural
candidate found so far: `UpdateGameOnce()` calls `sys_evt_process_pending()`
unconditionally at its own entry (`game_run.cpp:1415`, before any
`skip_render_and_wait` branch) -- `while (SDL_PollEvent(&event)) { ... }`,
which (by SDL's own normal semantics) pumps the DOS video backend's event
source on every call. `DOSVESA_PumpEvents()`'s own explicit `DOS_Yield()`
is confirmed default-skipped in this configuration (`S7-tick-starvation-
source-investigation-2026-09-14.md`), so the mechanism -- if it lives here
at all -- is not that specific, already-known yield call. Not yet
identified: whether something else in this same call chain (keyboard IRQ
servicing contending with the SB16 IRQ, an SDL-internal mutex/lock shared
with the audio thread, or a still-unaudited `DOS_Yield()`/`SDL_Delay()`
site) is the actual trigger. `SDL_sysmutex.c`/`SDL_syssem.c` (both contain
`DOS_Yield()` references, per this investigation's earlier broad grep) have
not yet been read in this investigation and are the next natural read.

## Not yet done

1. Identify the actual mechanism (candidates above) -- needs more source
   reading, specifically `SDL_sysmutex.c`/`SDL_syssem.c` and a closer
   look at whether anything in the keyboard-IRQ/event-pump path is
   genuinely gated by audio-thread activity.
2. An empirical alternative to more source reading: test whether the
   cooperative audio thread's mere existence (not its call frequency) is
   the lever, e.g. by A/B'ing a build that never creates a background
   audio thread at all (fully synchronous `SDL_DOSAudioPump()`-only
   servicing) against this one -- a real, falsifiable test of "does the
   thread's existence alone cause this," not just its call frequency
   (already ruled out by patch 0060). Not attempted -- would be a real
   architecture change, not a diagnostic, and needs its own design
   review before touching real hardware again.
3. `run-rig.sh`'s collect-phase stall (found in the `AUDIOFX2` cell) did
   NOT recur this cell -- inconclusive on whether it was transient or
   fixed by something incidental; still not root-caused.
4. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0063 all stay landed, all still temporary.
