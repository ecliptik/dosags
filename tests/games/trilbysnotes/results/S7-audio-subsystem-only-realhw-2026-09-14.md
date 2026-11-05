# S7 -- SDL_INIT_AUDIO-subsystem-only, real-hardware result: the SB16 device is NOT necessary -- 2026-09-14 (new session)

Operator-approved cell (tag `SUBSY1`, `binary_sha12=fba520c84c71`, the
patch-0065 build), HW-486-66, same recipe as every prior S7 cell plus
`DOSAGS_AUDIO_SUBSYSTEM_ONLY=1`. `run-rig.sh` completed cleanly end to
end (180s wait for the stable-screen detector, no harness intervention
needed).

## Result

`SUBSY1.LOG`:

```
[RUNMANIFEST-BEGIN]
binary_sha12=fba520c84c71
duration_s=93
exit_code=0
fps_p50=0.48
fps_p95=0.49
audio_vital_status=NA
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=2.52 frames_skipped=168
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=16 mean=3023 max=23663) pump_us(min=19 mean=21 max=30) regwrite(calls=6079 min_us=20 mean_us=21 max_us=150)
DOS-PORT tickfx total_calls=34 window_calls=34 catchup_n_sum=167 catchup_us(min=969122 mean=2432760 max=34369945) realtick_us(min=118476 mean=456751 max=510692) catchup_yield(switches=0 min_us=0 mean_us=0 max_us=0) realtick_yield(switches=0 min_us=0 mean_us=0 max_us=0)
```

`STDOUT.TXT` confirms the flag fired (`DOS-PORT DOSAGS_AUDIO_SUBSYSTEM_
ONLY=1 -- ...`), `AudioCore: DOS mixer status: NA` (no device ever
opened, matching the design), real gameplay progressed normally (room 1
loaded, `Playing music 1`, `DosMidiBackend: OPL3/OPL2 chip detected and
initialized`), clean shutdown.

## Verdict: the SB16/PCM device is NOT necessary for the tax -- a completely new, decisive finding

**`tick_rate=2.52`** -- not the ~5x-floor band (`OSA1NT`-`OSA4NT`:
3.21-3.23) this investigation expected going in, but squarely inside the
**full ~10-12x collapsed band** (`DMAX1`=2.50, `NOBGT1`=2.48,
`AUDIOFX3`/`4`=2.96-2.97). Per-tick cost confirms it precisely:
`catchup_us` mean (2,432,760us / (167/34=4.91 ticks/burst) =
**495.3ms/tick**) and `realtick_us` mean (**456.8ms**) both land at
**11.8x** and **10.9x** against the ~42ms/tick sound-off baseline --
statistically indistinguishable from `NOBGT1`'s own 498.0ms/472.6ms
(11.9x/11.3x) and `DMAX1`'s 495.8ms/469.3ms.

**This is the opposite of what every prior entry in this investigation
assumed going in.** Every hypothesis tested from `S7-opendevice-bisect-
realhw-2026-09-14.md` onward treated `OpenDevice` (the SB16 backend's own
hardware bring-up) as the thing narrowing toward a floor -- the ~5x floor
found in `OSA1NT`-`OSA4NT` was the *best* result found across eleven
real-hardware cells, and this entry's own working hypothesis (stated in
`S7-audio-subsystem-only-dosboxx-2026-09-14.md`) was that removing
`OpenDevice` ENTIRELY would recover further still, toward the sound-off
baseline. **It did the opposite**: `SUBSY1` (no `SDL_OpenAudioDeviceStream()`
call at all -- no ring buffer, no DSP reset, no DMA, no IRQ hook, no
thread, nothing the SB16 backend owns) shows a *worse* tick_rate (2.52)
than `OSA1NT` (3.21, the minimal-but-actually-opened state). The SB16
device being open-but-inert is measurably *better* than not opening it
at all.

**Conclusion, source-verified and now measurement-confirmed**: `SDL_
DOSAudioPump()`'s own null-device early-return (confirmed by this cell's
own `pump_us` collapsing to a mean of 21us, matching the DOSBox-X
prediction and the source-read null-check) proves the SB16 backend
contributes *nothing* to this state -- and the full tax survives anyway.
**The mechanism cannot live anywhere in `vendor/SDL/src/audio/dos/
SDL_dosaudio_sb.c`, `DOSSOUNDBLASTER_OpenDevice()`, or any DMA/IRQ/
thread/ring machinery that file owns** -- all of that is now proven
absent in this run, by construction, not by inference. Every hypothesis
this investigation spent eleven real-hardware cells testing inside that
file (thread existence, DMA activity, IRQ hooking, register-write
volume/cost measured via `slots_us`, `OpenDevice`'s own bring-up extent)
was investigating the wrong subsystem entirely, or at best a subsystem
that only ever mattered together with something else that is the real
cause.

## What remains, now narrowed to exactly two candidates

Everything present in `SUBSY1` that is absent in the sound-off baseline
(Arm A) is now exactly:

1. **`SDL_InitSubSystem(SDL_INIT_AUDIO)` succeeded** -- the generic SDL3
   audio core's own subsystem-level init (driver struct, `subsystem_
   rwlock`, `pending_events` list, whatever internal bookkeeping
   `SDL_AudioInit()` sets up), with **zero devices ever opened**.
2. **A real, actively-dispatching OPL3 MIDI backend** -- `dos_midi_
   backend_open()` -> `opl3_sink_open()` -> `SDL_DOSOpl3WriteRegister()`
   port I/O, `midi_sched_tick()`'s own scheduling/event-list traversal --
   entirely independent of SDL_INIT_AUDIO or any SDL audio device (this
   was already established structurally before this cell ran, and this
   cell's own 6079 real `regwrite` calls confirm it dispatched for real).

**Neither has ever been isolated from the other in this entire
investigation.** Every sound-on cell so far, including this one, keeps
both live simultaneously; every sound-off cell (Arm A) has neither
(`usetup.AudioEnabled=false` skips `engine_init_audio()`'s whole body,
so `sys_audio_init()`/`SDL_InitSubSystem(SDL_INIT_AUDIO)` AND `audio_
core_init()`/`dos_midi_backend_open()` are both skipped together). A
genuinely new, still-unbuilt diagnostic is needed to split them: does
`sys_audio_init()` return success WITHOUT ever calling `SDL_InitSubSystem(
SDL_INIT_AUDIO)` at all (while `engine_init_audio()` still proceeds to
`audio_core_init()`, and OPL3 still plays for real)? `engine_init_audio()`'s
own structure (`Engine/main/engine.cpp:394-409`) makes this buildable:
it only requires `sys_audio_init()` to return `true`.

## Where this leaves the investigation

**A completely new axis is now the leading, and only remaining,
candidate class**: either SDL3's generic audio-subsystem-init
bookkeeping (untested in isolation from a real device until this cell,
and this cell couldn't isolate it from MIDI either), or the OPL3 MIDI
backend / `midi_sched` path itself (never suspected as the PRIMARY
mechanism before now -- only its per-write *cost* was checked and
refuted, `S7-regwrite-diag-realhw-2026-09-14.md`, never whether merely
*having an active MIDI backend at all*, independent of SDL audio, is
sufficient). The hardware/electrical wait-state hypothesis named in the
prior entry is now far less likely to be SB16/PicoGUS-specific (nothing
SB16-specific was even touched in this run) -- if a hardware mechanism
is still in play, it would have to be tied to the OPL3 chip itself, not
the SB16/DMA path this investigation spent most of its time on.

Acceptance gate items 4 and 5 remain FAIL. Patches 0059-0065, 0141,
0143-0144 all stay landed, all still temporary.

## Not yet done

1. **The decisive follow-up**: isolate "OPL3 MIDI active, `SDL_
   InitSubSystem(SDL_INIT_AUDIO)` never called at all" as its own
   condition -- a small extension of patch 0065 (or a new value),
   DOSBox-X validated, then a real-hardware cell. If the tax survives
   even there, the entire mechanism is inside the OPL3 MIDI backend /
   `midi_sched` path, nothing to do with SDL's audio subsystem at all --
   a finding that would redirect this whole investigation's remaining
   search space to code never seriously suspected before. If it
   recovers, `SDL_InitSubSystem(SDL_INIT_AUDIO)`'s own generic-core
   bookkeeping is implicated instead.
2. Acceptance gate items 4 and 5 remain FAIL.
