# S7 -- SDL_INIT_AUDIO-subsystem-only isolation: patch landed, DOSBox-X validated -- 2026-09-14 (new session)

Continuation of `S7-generic-core-and-subsystem-audit-2026-09-14.md`'s own
designed-but-not-built candidate 2. Designed and landed `patches/ags/0065`
(`DOSAGS_AUDIO_SUBSYSTEM_ONLY=1`): a strict-"1" env killswitch checked in
`sys_audio_init()` (`Engine/platform/base/sys_main.cpp`) right after
`SDL_InitSubSystem(SDL_INIT_AUDIO)` succeeds. When set, `dos_audio_mixer_
init()` (which reaches `SDL_OpenAudioDeviceStream()` ->
`DOSSOUNDBLASTER_OpenDevice()`) is skipped entirely -- no device is ever
opened -- while the subsystem itself stays live.

## Safety verified by reading before running

Confirmed by source read, not assumed, that this state cannot crash:
`dos_audio_mixer_pump()` (called every real tick via `audio_core_entry_
poll()` regardless of PCM device state -- `WaitForNextFrame()` calls it
unconditionally whenever `AGS_DISABLE_THREADS` is defined, which is
always true for this DOS build) falls through its `if (g_stream)` block
(false in this state) straight to an unconditional `SDL_DOSAudioPump()`
call. `SDL_DOSAudioPump()`'s own first lines (`SDL_dosaudio_sb.c:3611`)
check its private `g_dos_audio_device` static pointer -- set only inside
`DOSSOUNDBLASTER_OpenDevice()`, which never runs in this state -- and
return `false` immediately. This is the exact same null-device path the
existing sound-off arm (Arm A) already exercises on every real tick via
this same unconditional call site, so `SDL_DOSAudioPump()`'s own
per-call cost in this new state was already implicitly proven cheap by
every prior sound-off baseline in this investigation, before ever
running the new arm.

Also confirmed `dos_midi_backend_open()`'s OPL3 path (`opl3_sink_open()`,
hub `shared/audio/opl3_sink.c`) has no dependency on an
`SDL_AudioDeviceID` at all -- it talks to the OPL3 chip directly via
`SDL_DOSOpl3WriteRegister()` port I/O -- so this arm was expected to play
real music, not run silent.

## DOSBox-X validation

`binary_sha12=fba520c84c71` (changed from `6ca3ac927604`, confirming the
tree changed). Same recipe as every prior S7 DOSBox-X cell (`dosbox-run.sh
--fast`, scratch `oplmode=opl3` conf, reverted after, Trilby's Notes,
`DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`,
`SDL_HINT_DOS_AUDIO_BACKEND=opl3`, `--user-data-dir c:\` per this file's
own `check_write_access()` note):

| Tag | Config | tick_rate | audio_vital_status | pump_us mean | regwrite calls |
|---|---|---:|---|---:|---:|
| `BASE1` | normal full open (regression check) | 30.12 | pcm=sb@...;midi=opl3,events=54 | 11236 | 210 |
| `SUBSY1` | `DOSAGS_AUDIO_SUBSYSTEM_ONLY=1` | 33.73 | NA | 3 | 208 |

**The banner confirms the flag fired** (`DOS-PORT DOSAGS_AUDIO_SUBSYSTEM_
ONLY=1 -- SDL_INIT_AUDIO initialized but dos_audio_mixer_init() (device
open) deliberately skipped; MIDI still plays, PCM/SFX will not`).
`audio_vital_status=NA` confirms no PCM device was ever considered open
(the same sentinel the existing sound-off arm reports) -- but
**`regwrite` shows 208 real OPL3 register-write calls, confirming MIDI
genuinely dispatched real music**, not a degenerate silent run. `pump_us`
collapsed to a mean of 3us (from 11236us in the normal-open baseline) --
**exactly the null-device early-return cost predicted by reading
`SDL_DOSAudioPump()`'s source above**, a real, mechanistic confirmation
of the wiring rather than just "didn't crash." Clean shutdown, no crash,
no hang, `exit_code=0` both cells.

**This DOSBox-X pass establishes correctness only** (wiring, real MIDI
dispatch, no regression, no crash) -- as with every prior diagnostic in
this series, DOSBox-X's own timing model cannot answer whether this
state reproduces or escapes the real-hardware tax. `tick_rate` here
(33.73, slightly higher than the 30.12 baseline) is not informative for
that question by itself.

## Not yet done

1. The real-hardware cell -- this is the decisive test. If it recovers
   close to the sound-off baseline (~23.8-23.9), that proves `OpenDevice`'s
   own minimal one-time actions (ring allocation + the mandatory DSP
   reset, both skipped entirely in this state) are responsible for the
   remaining ~5x floor -- pointing toward a persistent hardware/electrical
   state change from that one-time reset command, consistent with the
   ISA-bus-wait-state hypothesis named in the prior entry. If it still
   shows the collapsed ~3.2ish tick_rate, that means `SDL_InitSubSystem(
   SDL_INIT_AUDIO)` succeeding (or simply having a real, dispatching MIDI
   backend active) is sufficient by itself, independent of the PCM
   device ever existing -- a different and arguably more useful finding,
   since it would redirect the search entirely away from the SB16
   backend's own hardware bring-up.
2. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0065, 0141, 0143-0144 all stay landed, all still temporary.
