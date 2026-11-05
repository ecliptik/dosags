# S7 -- root-cause instrumentation + fix, DOSBox-X validated -- 2026-09-14

Continuation of `S7-abba-2026-09-13.md`. That session found (source
reading only, not yet measured) that `dos_run_tick_fixed()`'s catch-up
loop (patch 0047) re-invokes `audio_core_entry_poll()` up to
`MAX_CATCHUP+1=6x` per `GameTick()` call once a MIDI backend is live and
the hardware falls behind the 40Hz target, and left "instrument the
poll/pump cost directly" as the next step rather than guessing at a fix.
This session did that, then implemented and DOSBox-X-validated a fix.
**No real-hardware time was used this session** -- everything below is
DOSBox-X only, per this hub's own "DOSBox-X is not authoritative for
performance" rule. Acceptance gate items 4 and 5 stay open until a real
HW-486-66 A/B/B/A re-run confirms this on the actual target hardware.

## Instrumentation (patch 0059, temporary)

Added `AUDIOPRB.LOG` diagnostic: brackets `audio_core_entry_poll()`'s two
real components (the slot `Poll()` loop -- MIDI scheduling included --
and `dos_audio_mixer_pump()`) with `uclock()`-based microsecond
timestamps, accumulates per-window min/mean/max (200-call windows, reset
each flush), writes no I/O on the hot path (same lesson
`.sdl-dos-ports/shared/patches/sdl3-dos/0136` already recorded: even
"every 20 frames" logging cost a real ~0.4-0.5fps there).

**Result** (DOSBox-X, `--fast`/`cycles=max`, scratch conf with
`oplmode=opl3` -- stock hub confs ship `oplmode=none` by design, same as
S4/S7's own prior precedent; Trilby's Notes, `DOSAGS_FIXED_TIMESTEP=1`,
OPL3 MIDI + SB PCM device open):

| Arm | slots_us mean | pump_us mean | pump_us vs sound-off |
|---|---|---|---|
| sound-off (no device) | 2-3 | 2-3 | baseline |
| sound-on (OPL3) | 22-126 | 10,300-11,144 | ~3400-4700x |

The slot `Poll()` loop (MIDI scheduling, `midi_sched_tick()`) is cheap --
tens of microseconds even with real dispatch happening (`events=432`
confirms it's not idle). **`dos_audio_mixer_pump()` alone is the cost**:
consistently ~10-11ms/call (mean close to max, not a rare outlier),
~3400x+ the sound-off baseline. Root-cause read of
`vendor/SDL/src/audio/dos/SDL_dosaudio_sb.c`: `dos_audio_mixer_pump()` ->
`SDL_DOSAudioPump()` -> `SDL_PlaybackAudioThreadIterate()` ->
`DOSSOUNDBLASTER_WaitDevice()`. `WaitDevice`'s fast path (ring already has
room: `DOS_Yield(); return true`) is cheap; its slow path spins on
`DOS_Yield()` until the hardware ring drains at least one `chunk_size`
worth of room -- a real-time-paced wait tied to the device's own sample
rate, not a cheap poll. Calling this far more often than the ring's real
playback-rate drain requires (up to 6x per `GameTick()`) means most calls
land in the slow path and pay a real wall-clock wait. This is the
mechanism candidate (b) in the prior session's writeup named
("blocking/wait component that scales badly when called back-to-back") --
confirmed directly, not guessed.

## Fix (patch 0060)

`game_run.cpp`'s `play.fast_forward || skip_render_and_wait` branch
(game_run.cpp:1514) calls `audio_core_entry_poll()` before returning, so
the fast-forwarded/catch-up tick's own audio still gets serviced (S1's
original reason for the call). Restricted that call to `play.fast_forward`
only. `skip_render_and_wait` (a fixed-timestep catch-up tick) no longer
triggers it: a catch-up burst is bounded by `MAX_CATCHUP` and is
unconditionally followed, in the very next `GameTick()` call, by one real
tick that reaches `WaitForNextFrame()` and pumps audio there -- so a
catch-up tick is never more than one bounded burst away from a real pump,
matching the ~1x/iteration cost profile S0's original fixed-timestep
design was validated against (before any Sound milestone patch existed).
`play.fast_forward` (cutscene skip) keeps the call -- it has no such bound
and can run an arbitrarily long, unbounded run of iterations before a
real tick happens again; removing the call there would reintroduce the
audio-starvation bug S1 originally fixed.

## DOSBox-X before/after (patch 0060)

The `--fast`/`cycles=max` conf mostly keeps up with the 40Hz target on its
own (tick_rate ~37 even sound-on, nowhere near HW-486-66's chronic
backlog), so it under-exercises the catch-up path. Re-ran the A/B under a
deliberately slower scratch conf instead: the hub's own parity conf
(`cycles=fixed 40000`) with `oplmode=opl3` added -- chosen because it
already reproduces the right REGIME (chronically behind the 40Hz target,
backlog never clears), even though its absolute rate differs from real
HW-486-66 (DOSBox-X's own WaitDevice/DOS_Yield/SDL_Delay timing model is
known not to match real hardware 1:1 -- see this backend's own
`[[dosbox_not_proxy]]` precedent for the real-SB16 IRQ wedge that never
reproduces under DOSBox-X either).

Same binary SHA/source otherwise, same `NOTES.ags`/`ACSETUP.CFG`
(sound=on, OPL3), same `DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_
TICK=200`:

| Build | fps_p50 | tick_rate | AUDIOPRB.LOG windows flushed (200 calls/window) |
|---|---|---|---|
| sound-off, this conf (context only) | n/a | 17.35 | n/a |
| pre-fix (diagnostic only, patch 0059) | 4.76 | 13.85 | 1 flush in 18s |
| post-fix (0059+0060) | 6.67 | 15.37 | 0 flushes in 17s |

tick_rate recovers about half the sound-on/sound-off gap in this conf
(13.85 -> 15.37 against a 17.35 sound-off ceiling), and `audio_core_entry_
poll()`'s own call rate measurably drops (a 200-call window didn't even
fill once in 17s post-fix, vs filling in 18s pre-fix) -- both real,
measured, same-direction effects. This is NOT the ~86% collapse recovery
the real-hardware numbers would need to pass acceptance items 4/5 --
DOSBox-X's own timing model doesn't reproduce that magnitude (expected;
same reason its numbers were never used for acceptance-gate claims
before). Binaries verified different before comparing
(`sha256sum` on the two exes) so this is a real A/B, not a rerun of the
same build.

## Not yet done

Real-hardware A/B/B/A re-run of the exact S7-abba-2026-09-13.md block
(HW-486-66, same Trilby's Notes workload, `DOSAGS_FIXED_TIMESTEP=1`,
sound-off vs sound-on/OPL3) against the patch-0060 build, to see whether
tick_rate/fps_p50 recover close to the sound-off baseline on the actual
target hardware. Acceptance gate items 4 and 5 stay open until that runs
and passes the pre-registered `<= 1.5 fps` bar. Patch 0059's diagnostic
is temporary and should be reverted in a follow-up patch once that
real-hardware confirmation lands (same convention as
`.sdl-dos-ports/shared/patches/sdl3-dos/0136`).
