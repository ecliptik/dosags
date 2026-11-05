# S7 -- silence-vs-sounding OPL3 isolation: patch landed, DOSBox-X validated -- 2026-09-14 (new session)

Continuation of `S7-audio-subsystem-only-v2-realhw-2026-09-14.md`'s own
"Not yet done" item 1. Landed `patches/ags/0067`
(`DOSAGS_MIDI_SILENT_CHIP=1`): a strict-"1" env killswitch checked in
`AudioPlayer::MidiInit()` (`Engine/media/audio/audioplayer.cpp`). By the
time `MidiInit()` runs, `dos_midi_backend_open()` (called earlier, in
this class's own MIDI constructor) has already fully programmed the
OPL3 chip via `SDL_DOSOpl3InitChip()` (OPL3 mode enabled, 4-op disabled,
all 18 voices key-off) regardless of this flag. Skipping only `midi_
sched_start()` leaves `midi_sched`'s own `m->playing` at its
`calloc()`-zeroed default -- verified by reading `midi_sched_tick()`'s
own entry guard (`if (!m || !m->playing || m->nevents == 0) return`)
that this makes every subsequent tick call a safe, immediate no-op: no
note-on ever dispatched, no register write beyond the `InitChip`
sequence. Isolates "chip initialized, never producing audible output"
from "chip initialized and actively synthesizing real music" (every
prior S7 sound-on cell) for the first time.

## DOSBox-X validation

`binary_sha12=218a42297d8f`. Same recipe as every prior S7 DOSBox-X
cell:

| Tag | Config | tick_rate | audio_vital_status events | regwrite calls | slots_us mean |
|---|---|---:|---:|---:|---:|
| `BASE3` | normal (sounding) regression check | 29.59 | 54 | 210 | 33 |
| `SILNT1` | `DOSAGS_MIDI_SILENT_CHIP=1` | 30.08 | 0 | 0 | 4 |

`SILNT1`'s own `events=0` confirms zero MIDI events ever dispatched
(the design intent, not just the banner claiming it), `regwrite
calls=0` confirms zero register writes happened inside the poll loop
beyond the one-time `InitChip` sequence (which this diagnostic doesn't
track, by design -- it runs before `audio_core_entry_poll()` ever
exists for this clip), and `slots_us` collapsing to a mean of 4us (from
33us) confirms the slot `Poll()` loop found nothing to do, exactly as
`midi_sched_tick()`'s own early-return guard predicts. `STDOUT.TXT`
confirms `DosMidiBackend: OPL3/OPL2 chip detected and initialized` still
fired (the chip WAS opened and programmed) alongside `events=0`. Clean
shutdown both cells, no crash, no regression.

**This DOSBox-X pass establishes correctness only** -- wiring, zero
dispatch confirmed via `events`/`regwrite`, no crash -- exactly like
every prior diagnostic in this series. Only real hardware can answer
whether "chip initialized but silent" escapes the tax or reproduces it.

## Not yet done

1. The real-hardware cell -- the decisive test. If `tick_rate` recovers
   toward the sound-off baseline (~23.8-23.9) with the chip merely
   initialized-but-silent, that would point squarely at active OPL3
   synthesis (a real hardware/electrical effect, most likely tied to
   this rig's PicoGUS emulation specifically) as the trigger condition.
   If it still shows the collapsed ~2.5x band (matching `SUBSY1`/
   `SUBSY2`), the mechanism is tied to the chip merely being
   initialized/opened, not to it actually producing sound -- which
   would point back toward something in `opl3_sink_open()`'s own
   one-time setup sequence, or an even more fundamental hardware state
   change from the `SDL_DOSOpl3InitChip()` register writes themselves.
2. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0067, 0141, 0143-0144 all stay landed, all still temporary.
