# S7 -- scheduler mechanism investigation (continuation) -- 2026-09-14

Continuation of `S7-tickfix-diag-realhw-2026-09-14.md`'s open question:
what actually causes the ~9.7x uniform per-`UpdateGameOnce()` tax when
the audio device is open. Pure source read (`SDL_sysmutex.c`,
`SDL_syssem.c`, and SDL3's generic `SDL_audio.c`), no new patch, no real
hardware.

## Two real findings

**1. Lock/semaphore contention is a second, more general trigger for the
same cooperative round-trip.** `SDL_LockMutex()` (`SDL_sysmutex.c`) and
`SDL_WaitSemaphoreTimeoutNS()` (`SDL_syssem.c`) both spin-call
`DOS_Yield()` when contended. This matters because it means the
mechanism under investigation is not limited to an *explicit*
`DOS_Yield()` call site somewhere in AGS's own code -- **any** blocked
lock or semaphore wait, anywhere in the SDL/DJGPP runtime, is an
equally-real entry point into the same "hand the CPU to the audio
thread" round-trip this investigation has been chasing.

**2. There is a real, autonomous, continuously-looping cooperative audio
thread -- not just the explicit `SDL_DOSAudioPump()` main-thread call
this investigation has focused on until now.** `SDL_audio.c:1882`:
`device->thread = SDL_CreateThread(PlaybackAudioThread, ...)` -- stock
SDL3 code, unconditional, runs the instant the audio device opens.
`PlaybackAudioThread`'s own loop (`SDL_audio.c:1314-1329`):

```c
while (SDL_PlaybackAudioThreadIterate(device)) {
    if (!device->WaitDevice(device)) { ... }
}
```

This thread mixes/converts/writes audio (`Iterate()`, real CPU work --
float32 mixing across up to 8 voices, format conversion, `PlayDevice()`)
then calls `WaitDevice()` (`DOSSOUNDBLASTER_WaitDevice()`,
`SDL_dosaudio_sb.c`), which -- on the common "ring has room" path --
calls `DOS_Yield()` exactly once (patch `SDL/0086`'s own documented
purpose: "hand CPU back to main... audio thread cannot monopolize") then
loops back to `Iterate()` again. **This thread exists and runs
independently of `dos_audio_mixer_pump()`/`SDL_DOSAudioPump()` -- that
call (already measured via `pump_us`, ~11ms mean) is a SEPARATE,
additional main-thread-initiated path that also drives the same
`Iterate()`/`WaitDevice()` pair, guarded by `device->lock` against this
autonomous thread running the same code concurrently
(`SDL_DOSAudioPump()`'s own `SDL_TryLockMutex`/timeout backstop exists
specifically because this autonomous thread can hold that lock for a
real, sometimes-long duration).**

## The strengthened, still-unconfirmed hypothesis

Given (1) and (2): once the audio device is open, the autonomous
`PlaybackAudioThread` is *always* `READY` in the scheduler's thread
table. Any `DOS_Yield()` (explicit, or via lock/semaphore contention)
anywhere in main's own per-tick code hands the CPU to it; it runs one
real `Iterate()` pass (real mixing cost, not yet measured directly) plus
one `DOS_Yield()` before handing back. If `sys_evt_process_pending()`
(called unconditionally at the very start of *every* `UpdateGameOnce()`,
catch-up ticks included -- `game_run.cpp:1415`) triggers even one such
round-trip via a path this investigation has not yet pinned down (its
own explicit `DOS_Yield()` in `DOSVESA_PumpEvents()` is confirmed
default-skipped, so it would have to be something else in that call
chain, or a lock/semaphore wait per finding (1)), that would explain the
near-identical tax paid by catch-up ticks and the real tick alike:
**every single `UpdateGameOnce()` call may be paying for one real
`Iterate()` pass of the autonomous audio thread, regardless of whether
it does anything audio-related itself.**

This is plausible and consistent with everything measured so far, but
**not confirmed** -- the exact trigger inside `sys_evt_process_pending()`
(or wherever it actually is) has not been identified by source reading
alone, despite auditing the scheduler, both cooperative primitives, and
the autonomous thread's own loop.

## Recommended next step

Per this hub's own discipline, this is the point to measure rather than
keep reading. Two candidate diagnostics, either of which would close
the loop:

1. **Instrument `DOS_Yield()` itself** (`SDL_dos_scheduler.c`, shared
   code): count calls and total real time spent between a `DOS_Yield()`
   call and control returning to the same thread, per `UpdateGameOnce()`
   call. Directly answers "how many round-trips per tick, and how
   expensive is each" -- the most direct instrument for the actual
   unexplained quantity (scheduler hand-off cost), but touches
   `shared/`-equivalent code (this port's own vendored
   `patches/SDL/`, not the hub's stale reference series -- see
   `docs/patch-conventions.md`) and needs its own DOSBox-X validation
   pass first, like every prior diagnostic in this series.
2. **Instrument `SDL_PlaybackAudioThreadIterate()`'s own per-call cost**
   directly (a smaller, more targeted addition) -- confirms or refutes
   whether one `Iterate()` pass alone is large enough to explain
   ~400ms, without needing full scheduler-wide accounting.

Neither has been implemented this entry -- a checkpoint before writing a
fourth temporary diagnostic layer, matching this investigation's own
established practice of pausing at exactly these points rather than
compounding diagnostics unprompted.

No patches landed, no real hardware used this entry. Acceptance gate
items 4 and 5 remain FAIL.
