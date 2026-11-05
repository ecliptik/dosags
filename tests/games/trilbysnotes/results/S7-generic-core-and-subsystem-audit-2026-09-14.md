# S7 -- generic SDL core + SDL_INIT_AUDIO-subsystem-axis source audit -- 2026-09-14 (new session)

Continuation of `S7-full-bisection-matrix-realhw-2026-09-14.md`'s own
"Not yet found" list. Pure source read this entry -- no patch, no real
hardware, no DOSBox-X. Picked up the two named candidates plus one the
prior session's own call-graph reading had not reached yet.

## Candidate 1 (named in the handoff): SDL3's generic audio core beyond `SDL_UpdateAudio()` -- refuted as a per-tick mechanism

Read `SDL_OpenAudioDevice()`/`SDL_CreateAudioStream()` (`vendor/SDL/src/
audio/SDL_audio.c`) and `SDL_PumpEventMaintenance()`/`SDL_WaitEventTimeoutNS()`
(`vendor/SDL/src/events/SDL_events.c`) fresh, computing plausibility rather
than assuming:

- `SDL_CreateAudioStream()`'s resampler/format-conversion setup and
  `SDL_OpenAudioDevice()`'s own device-list bookkeeping are **one-time,
  open-time costs** -- they cannot produce a *recurring per-tick* charge,
  and this port's own `S7-tickfix-diag-realhw-2026-09-14.md` already
  established the tax is paid on **every** `UpdateGameOnce()` call
  uniformly, catch-up ticks included. Ruled out on structural grounds
  alone, no measurement needed.
- `sys_evt_process_pending()` -> `while (SDL_PollEvent(&event))` ->
  `SDL_WaitEventTimeoutNS(event, 0)`: read the actual function body.
  With `timeoutNS == 0` it takes the early-return path at line ~1722-1726
  (`result == 0 && timeoutNS == 0` -> `return false`) -- it calls
  `SDL_PumpEventsInternal(true)` **once**, per `SDL_PollEvent` call, and
  never reaches `SDL_WaitEventTimeout_Device()` (the joystick/sensor/tray
  polling-interval machinery) at all for a zero-timeout poll. Confirmed
  by reading the guard (`SDL_assert(timeoutNS != 0)` sits *after* the
  zero-timeout return, i.e. the device-wait path is structurally
  unreachable from `SDL_PollEvent`).
- `SDL_PumpEventsInternal()` -> `SDL_PumpEventMaintenance()` calls
  `SDL_UpdateAudio()` (already refuted,
  `S7-opendevice-bisect-realhw-2026-09-14.md`), `SDL_UpdateCamera()`,
  `SDL_UpdateSensors()`, `SDL_UpdateJoysticks()`,
  `SDL_SendPendingPenProximity()`, `SDL_UpdateCursorAnimation()`,
  `SDL_UpdateTrays()`, `SDL_SendPendingSignalEvents()` -- every one of
  these is either compile-time-disabled for this build or gated on its
  *own* subsystem's init/update flag (camera, sensor, joystick), none of
  which changes state when `SDL_INIT_AUDIO` toggles. No audio-conditioned
  branch exists anywhere in this function.

**Verdict: candidate 1, as named, is dead.** The generic core's only
audio-reachable hook (`SDL_UpdateAudio()`) was already measured cheap by
source reading in the prior session; this session's fresh read of
everything *around* it (`SDL_PollEvent`'s actual call depth,
`SDL_CreateAudioStream`/`SDL_OpenAudioDevice`'s one-time nature) finds no
other candidate in SDL3's generic core that could plausibly reach
hundreds of milliseconds per tick, let alone one gated on audio state.

## A never-examined AGS-side call site, found and cleared: `update_audio_system_on_game_loop()`

Not named in the handoff, but a real gap in the existing call-graph
audit: `game_run.cpp:1475` calls `update_audio_system_on_game_loop()`
**unconditionally**, before the `skip_render_and_wait` branch -- a
second, distinct site from `audio_core_entry_poll()` (gated, line 1567)
that every prior entry in this investigation focused on exclusively.
This runs on every catch-up tick too, which matters because catch-up
ticks pay the *same* tax as real ticks despite calling neither
`audio_core_entry_poll()` nor `dos_audio_mixer_pump()` at all post-patch-
0060 -- so any per-tick audio-side mechanism has to live somewhere both
tick types actually call.

Read the full chain (`audio.cpp`'s `update_audio_system_on_game_loop()`
-> `sync_audio_playback()` -> `SoundClip::update()` ->
`AudioPlayer::GetPositionMs()`/`GetPlayStateNormal()`,
`audio_update_polled_stuff()`, `process_scheduled_music_update()`,
`IsMusicPlaying()`):

- `sync_audio_playback()` loops `TOTAL_AUDIO_CHANNELS` channels but only
  calls `ch->update()` on channels actually playing -- one channel (music)
  in this scene.
- `SoundClip::update()` for a MIDI-mode `AudioPlayer` (`_isMidi == true`)
  early-returns `0.0f`/no-ops on `GetPositionMs()`, `SetVolume()`,
  `SetSpeed()`, `SetPanning()` (`audioplayer.cpp:340-368`, each explicitly
  `if (_isMidi) return ...`) -- confirmed no null-deref risk from the
  unconstructed `_source` either, since every MIDI accessor guards before
  touching it.
- `audio_core_get_player()` takes `std::lock_guard<std::mutex>` on
  `g_acore.mixer_mutex_m` -- checked whether this is a real lock: DJGPP's
  `std::mutex` shim (`Common/platform/dos_compat.h:173-183`, added by
  patch 0014, its own commit message states "every operation is a
  correct no-op") really is `lock() {}` / `unlock() {}` / `try_lock() {
  return true; }` -- empty inline bodies, not even a CLI/STI pair. Not a
  cost center by construction.
- `audio_update_polled_stuff()` (`audio.cpp:274`) and
  `process_scheduled_music_update()`/`IsMusicPlaying()`
  (`global_audio.cpp:199`) are pure game-logic bookkeeping (crossfade
  step counters, channel-state checks) with no I/O, no DOS backend call,
  no lock beyond the already-cleared one above.

**Verdict: cleared.** This call site is real and was genuinely
unaudited, but costs nothing that could explain the tax. Recorded here
so a future session doesn't have to re-derive that this path was
checked.

## Candidate 2 (named in the handoff): `SDL_InitSubSystem(SDL_INIT_AUDIO)` as its own axis -- confirmed genuinely untested, and now cheaply designed

Found the engine's own call site first, as instructed, rather than
guessing: `engine_init_audio()` (`Engine/main/engine.cpp:394-399`) calls
`sys_audio_init()` **only if** `usetup.AudioEnabled` -- so the existing
sound-off arm (Arm A, every real-hardware baseline this investigation has
used) never calls `SDL_InitSubSystem(SDL_INIT_AUDIO)` at all. Inside
`sys_audio_init()` (`platform/base/sys_main.cpp:280-329`), the non-GUS
path (this port's only path so far -- OPL3/WaveBlaster, not GUS) always
calls `SDL_InitSubSystem(SDL_INIT_AUDIO)` **immediately followed by**
`dos_audio_mixer_init()` (which is what eventually reaches
`DOSSOUNDBLASTER_OpenDevice()`) -- the two are unconditionally bundled on
every real-hardware cell this whole investigation has ever run,
including `OSA1NT` (`OPEN_STOP_AT=1`, the earliest possible return point
inside `OpenDevice` -- but `OpenDevice` itself still ran and still
returned `true`, meaning `SDL_OpenAudioDevice()` still succeeded and SDL
still considers a device "open"). **No cell in this entire investigation
has ever tested "subsystem initialized, zero devices ever opened."** This
confirms the handoff's own suspicion directly from the call site rather
than assuming it.

**This axis is buildable cheaply, and would compose with real OPL3
playback, not just a silent smoke test**: `dos_midi_backend_open()`
(`platform/dos/dos_midi_backend.cpp:88`) for the OPL3 case calls
`opl3_sink_open()` (hub `shared/audio/opl3_sink.c`), which talks to the
OPL3 chip directly via `SDL_DOSOpl3WriteRegister()` port I/O
(`vendor/SDL/src/core/dos/SDL_dos_audio_synth.c`) -- **it has no
dependency on an `SDL_AudioDeviceID` existing at all.** This is the same
structural pattern the GUS "Model B, out-of-band" path
(`sys_main.cpp:280-314`) already uses to skip `SDL_INIT_AUDIO` entirely
for MIDI-only playback -- OPL3 could, in principle, run identically with
zero PCM devices ever opened. A new arm that inits `SDL_INIT_AUDIO` but
never calls `dos_audio_mixer_init()`'s `SDL_OpenAudioDevice()` would
still play real MIDI, giving a genuine apples-to-apples `tick_rate`
comparison against every existing sound-on arm, not a degenerate silent
run.

**Not yet built.** This needs a new dosags-side hint (not an SDL-layer
one -- the decision point is `sys_audio_init()`, before `dos_audio_mixer_
init()` is ever called), a narrow patch, and a DOSBox-X validation pass
before any real-hardware time. See "Next steps" below.

## Where this leaves the investigation

**Candidate 1 is dead** (source-verified, no new hardware/DOSBox-X time
spent). **A second, previously-unaudited AGS-side call site
(`update_audio_system_on_game_loop()`) is now cleared too**, closing the
gap in the per-tick call-graph audit -- between this and everything
already read in prior entries, essentially the entire reachable call
graph from both `UpdateGameOnce()` tick types (catch-up and real) has now
been read at the source level and found cheap, with the sole exception of
whatever runs *inside* `dos_audio_mixer_pump()`'s slow path (already
measured, not the catch-up-tick mechanism since catch-up ticks don't call
it). **Candidate 2 is alive and now concretely designed**, not just
named -- the next real step is a new hint + patch to isolate it, not more
reading.

**A genuinely new class of hypothesis worth naming, not yet designed as a
patch**: given how little software surface remains unaudited or
unmeasured (essentially none, after this session), and given the floor
survives in the single most minimal software state this port can reach
(`OSA1NT`: no thread, no DMA, no IRQ hook, no DSP command beyond one
mandatory reset), the remaining candidate may not be a software cost at
all. A real ISA-bus/electrical mechanism -- the PicoGUS card inserting
real wait-states on ordinary bus cycles once its emulated DSP leaves a
fully-idle/uninitialized firmware state (distinct from DMA-cycle-stealing,
which was refuted; this would apply to *all* bus traffic, not just
DMA-competing traffic) -- would explain: why it survives every software
axis tested, why DOSBox-X never reproduces any of this investigation's
findings (no emulator models real ISA electrical timing), and why the
tax is *uniform* regardless of what code runs. This is untested and
would need a qualitatively different diagnostic (a synthetic CPU-bound
counting loop instrumented independently of any audio call, run with the
device closed vs. at the `OSA1NT`-equivalent minimal-open state, to see
if pure non-audio CPU throughput itself craters) -- not a source-reading
question, not designed this entry.

Acceptance gate items 4 and 5 remain FAIL. No patches landed this entry.
Patches 0059-0064, 0141, 0143-0144 all stay landed, all still temporary.

## Next steps (not yet started, for operator direction)

1. **Isolate `SDL_INIT_AUDIO`-subsystem-only** (candidate 2, now
   designed above): add a narrow dosags-side hint/env var checked in
   `sys_audio_init()` to call `SDL_InitSubSystem(SDL_INIT_AUDIO)` and
   then skip `dos_audio_mixer_init()`'s device-open call entirely,
   verify `dos_audio_mixer_status_string()` and any other "is a device
   open" consumer degrade gracefully, DOSBox-X-validate, then a fresh
   real-hardware go-ahead.
2. **Design a synthetic CPU-throughput probe** (the new hardware/
   electrical hypothesis above): a diagnostic that counts iterations of
   a fixed, audio-unrelated busy loop over a fixed real-wall-clock
   window, comparable device-closed vs. device-open-minimal
   (`OSA1NT`-equivalent), to test whether non-audio CPU throughput itself
   degrades when the card is merely open.

Neither started this entry -- flagging both for the operator to
prioritize (or run in sequence) before more real-hardware time is spent.
