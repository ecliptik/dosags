# S7 -- SDL_INIT_AUDIO-never-touched isolation: patch landed, DOSBox-X validated -- 2026-09-14 (new session)

Continuation of `S7-audio-subsystem-only-realhw-2026-09-14.md`'s own
decisive follow-up. Landed `patches/ags/0066`
(`DOSAGS_AUDIO_SUBSYSTEM_ONLY=2`): extends the same env var checked at
the very top of `sys_audio_init()`, before `SDL_InitSubSystem(SDL_INIT_
AUDIO)` is ever called. When set, `sys_audio_init()` returns `true`
having touched nothing SDL-audio-related whatsoever. `engine_init_audio()`
(`Engine/main/engine.cpp:394-409`) only gates `audio_core_init()` on this
function's own return value, so OPL3 still plays for real via `dos_midi_
backend_open()` -> `opl3_sink_open()`, which has no dependency on
`SDL_INIT_AUDIO` or any `SDL_AudioDeviceID`.

## DOSBox-X validation

`binary_sha12=406c63249f6b` (changed from `fba520c84c71`). Same recipe as
every prior S7 DOSBox-X cell:

| Tag | Config | tick_rate | audio_vital_status | pump_us mean | regwrite calls |
|---|---|---:|---|---:|---:|
| `SUBSY1` (prior entry) | `=1` (subsystem live, no device) | 33.73 | NA | 3 | 208 |
| `SUBSY2` | `=2` (subsystem never touched) | 31.40 | NA | 3 | 214 |

Banner confirms the flag fired (`DOS-PORT DOSAGS_AUDIO_SUBSYSTEM_ONLY=2
-- SDL_InitSubSystem(SDL_INIT_AUDIO) itself deliberately skipped; ...`).
`regwrite calls=214` confirms real OPL3 dispatch, same order of magnitude
as `SUBSY1`'s own 208 -- not a degenerate silent run. `audio_vital_
status=NA`, clean shutdown, no crash, no regression. `pump_us` mean=3us,
same null-cost path as `SUBSY1` (expected -- `SDL_DOSAudioPump()`'s own
`g_dos_audio_device` static is never touched in either state).

**This DOSBox-X pass establishes correctness only** -- wiring, real MIDI
dispatch, no crash -- exactly as with `SUBSY1` and every prior diagnostic
in this series. Only real hardware can answer whether this state escapes
the tax or reproduces it.

## Not yet done

1. The real-hardware cell -- the decisive test this whole sub-
   investigation has been building toward. If `tick_rate` recovers
   toward the sound-off baseline here, `SDL_InitSubSystem(SDL_INIT_
   AUDIO)`'s own bookkeeping (even with zero devices) is implicated. If
   it still shows the collapsed ~2.5-3x band (matching `SUBSY1`), the
   entire mechanism is inside the OPL3 MIDI backend/`midi_sched` path --
   redirecting this whole investigation's remaining search space away
   from SDL's audio subsystem entirely, to code (`shared/audio/opl3_
   sink.c`, `midi_sched.c`) never seriously suspected as the primary
   cause before now.
2. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0066, 0141, 0143-0144 all stay landed, all still temporary.
