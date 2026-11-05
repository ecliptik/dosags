# S7 -- tick-starvation root cause, source investigation -- 2026-09-14

Continuation per the regwrite real-hardware result's own conclusion:
register-write volume/cost is a downstream symptom, not the driver.
This is a pure source-reading investigation (no new patch, no real
hardware) to find where the real cost lives. No fix proposed yet --
per this hub's own "do not guess at the fix without a real
before/after measurement" discipline, this is the hypothesis-forming
step that should precede the next diagnostic.

## The numbers that need explaining

From `S7-abba-2026-09-13.md` (the original ABBA) and this session's own
math:

| Arm | tick_rate | implied real cost per `UpdateGameOnce()` (aggregate) |
|---|---:|---:|
| sound-off | 23.8-23.9/s | ~42ms |
| sound-on (OPL3 or WB) | 3.2-3.3/s | ~303ms |

Both arms run `dos_run_tick_fixed()` permanently catch-up-saturated
(backlog never clears against the 40Hz target even sound-off, so every
call does the full `MAX_CATCHUP=5` + 1 = 6 `UpdateGameOnce()` calls --
confirmed by the original ABBA's own root-cause section). The known,
directly-measured audio cost per real (non-catchup) tick is
`pump_us`(~11ms) + `slots_us`(~1-34ms, this session's own two real-hardware
cells) =~ 12-45ms. Even charged against all 6 calls in a burst (the
pre-patch-0060 behavior), that is at most ~6x45ms=270ms -- and
post-patch-0060 (audio polled on only 1 of the 6 calls) it is ~45ms.
Neither comes close to explaining the ~261ms/tick gap between the
sound-off and sound-on baselines, and this matches what was actually
observed: **patch 0060 (removing 5 of 6 audio-poll calls per burst)
measured ~zero real-hardware effect, even a slight regression** (4.42 ->
4.615 fps cost). Something other than `audio_core_entry_poll()`'s own
call cost is responsible for most of the ~261ms/tick gap.

## The DOS backend's threading model is real cooperative multitasking, not just SB16 plumbing

Read `vendor/SDL/src/core/dos/SDL_dos_scheduler.c`/`.h` fresh (never
previously examined in this investigation). This is a genuine
`setjmp`/`longjmp`-based **cooperative, round-robin, non-preemptive**
user-space thread scheduler -- up to `DOS_MAX_THREADS=16` cooperative
"threads" sharing one physical CPU, switching ONLY at explicit
`DOS_Yield()` calls. Critically: **while one thread runs, no other
thread runs at all** -- there is no timer-interrupt-driven preemption
here. `SDL_systhread.c` confirms SDL3's own generic audio subsystem
creates a real cooperative thread (via `DOS_CreateThread()`) for the
playback loop when a device opens -- this is not a metaphor, it is an
actual second execution context that owns the CPU for as long as it
runs before its own next `DOS_Yield()`.

`DOSSOUNDBLASTER_WaitDevice()` (the audio thread's own loop body) calls
`DOS_Yield()` **on every iteration** -- both the room-available path
(`SDL/0086`'s "hand CPU back to main... audio thread cannot monopolize")
and the ring-full path (loops calling `DOS_Yield()` each pass while
waiting for the IRQ-5 ISR to drain the ring). So `DOS_Yield()` is not a
cheap no-op probe here: calling it from ANYWHERE hands the CPU to the
audio thread if it's `READY`, and the audio thread runs uninterrupted
(mixing, DSP writes, its own real-time-paced ring servicing) until IT
decides to yield back. **The cost of "yielding" is entirely determined
by how much real work the other side does before its own next yield --
this is the exact mechanism SDL/0021's own comment already documented
for one call site** ("the per-pump `DOS_Yield()` was measured at ~115ms/
flip on real HW... cost is the cooperative-thread round-trip into the
audio thread's `WaitDevice` spin").

## Checking the two other real per-tick `DOS_Yield()`/`SDL_Delay()` candidates

1. **`WaitForNextFrame()`'s own pacing wait** (`ac/timer.cpp`): when
   badly behind schedule (which we know we are), `next_frame_timestamp <
   now - MAXIMUM_FALL_BEHIND*frameDuration` fires, resetting
   `next_frame_timestamp = now`, making `frame_time_remaining <= 0` --
   the `std::this_thread::sleep_for()` call is skipped entirely.
   **Ruled out**: this path should be near-instant when lagging, not a
   source of the gap.
2. **`DOSVESA_PumpEvents()`'s own `DOS_Yield()`** (`SDL_dosevents.c`,
   called every tick via `sys_evt_process_pending()` ->
   `GameUpdateProcessEvents()`, including catch-up ticks -- this call
   is NOT gated by `skip_render_and_wait`): patch `SDL/0021` already
   default-skips this specific yield
   (`yield_skip_cached`, `SDL_HINT_DOS_FORCE_PUMP_YIELD` unset in every
   cell this investigation has run). **Confirmed inert** in our config
   -- `SDL_HINT_DOS_FORCE_PUMP_YIELD` grepped clean across
   `vendor/ags/`, `tests/harness/run-rig.sh`, `profiles/`.

Neither of the two OTHER per-tick call sites that reach `DOS_Yield()`/
`SDL_Delay()` appears to fire under our configuration. That leaves
`dos_audio_mixer_pump()`'s own direct call (already measured, too small)
as the only ACCOUNTED-FOR yield site on the per-tick path -- which does
not explain the gap on its own.

**A real, explicit contract this port never fulfills**: `SDL_dosevents.c`'s
own comment states outright: "the engine is expected to call
`SDL_Delay(0)` once per flip to keep the audio thread scheduled." Grepped
`vendor/ags/Engine/` for `SDL_Delay` -- the only hits are in the
emscripten/ios platform files, never compiled for DOS. **dosags never
calls `SDL_Delay(0)` anywhere.** Whether this contract violation is itself
consequential (starving the audio thread of scheduling opportunities
outside `dos_audio_mixer_pump()`'s own explicit call, which could in turn
make the ring run drier and change how much real work the audio thread
does the NEXT time it IS scheduled) is a real, plausible, but
**not yet confirmed** mechanism -- consistent with patch 0060 regressing
slightly (servicing the ring less often could starve it further, not
less).

## What this does and doesn't establish

**Established, source-verified:**
- The DOS backend is cooperatively (not preemptively) multitasked --
  `DOS_Yield()` calls are real, potentially expensive, context switches,
  not cheap probes.
- `audio_core_entry_poll()`'s own measured cost cannot explain the
  sound-off-vs-sound-on gap, confirming (with a source-level mechanism,
  not just the earlier empirical result) why patch 0060 had ~zero effect.
- Only one per-tick call site (`dos_audio_mixer_pump()`, already
  measured) is confirmed to actually invoke `DOS_Yield()` under this
  port's current configuration; the two other candidates are ruled out
  or confirmed inert.

**Not yet established:**
- Where the remaining ~250ms/tick actually goes. If no other
  `DOS_Yield()`/`SDL_Delay()` call fires per tick, the audio thread
  should get scheduled only once per real tick (inside
  `dos_audio_mixer_pump()` itself) -- meaning the missing cost may not
  be a cooperative-scheduling artifact at all, and could instead be
  concentrated in ordinary non-audio per-tick work (rendering, script
  execution, room/path-finding logic) that simply IS this expensive on
  real 486-class hardware, independent of audio, and that the sound-off
  baseline's own ~42ms/tick doesn't reflect for some reason not yet
  understood (e.g. the sound-off arm's own workload/scene differs from
  the sound-on arm's -- worth checking whether A1/A2 and B1/B2 actually
  reached the same room/script state, not just the same tick count).
- This investigation has not yet searched for `DOS_Yield()`/`SDL_Delay()`
  calls reachable from room/script logic, path-finding, or asset loading
  (a much larger search than the three call sites checked here) --
  genuinely possible another site exists that only fires under specific
  game content, not a fixed per-tick call.

## Recommended next step

Per this hub's "instrument the thing that produces the unexplained
quantity" rule, applied one level up from where this investigation has
been working: bracket `dos_run_tick_fixed()` itself, splitting real
wall-clock time into (a) the summed cost of the up-to-5 catch-up
`UpdateGameOnce()` calls, (b) the one real `UpdateGameOnce()` call's
total cost, and (c) that real call's already-known audio-specific
sub-cost (existing AUDIOPRB instrumentation). If (a) dominates, the
mechanism is somewhere in ordinary per-tick logic run on EVERY tick
(catch-up included) -- the DOS_Yield()/SDL_Delay() search should widen
there. If (b) minus (c) dominates, the mechanism is specific to the one
real (rendering) tick -- rendering cost, GUI update, or something
`skip_render_and_wait` doesn't skip would be the next read. Either
result is genuinely informative and narrows the search space
significantly from "the whole engine." Not yet implemented or validated
under DOSBox-X -- checkpoint before writing new instrumentation, since
this would be the third temporary diagnostic layer in this
investigation and deserves a decision point rather than continuing to
add code unprompted.

No patches landed this entry. Acceptance gate items 4 and 5 remain FAIL.
