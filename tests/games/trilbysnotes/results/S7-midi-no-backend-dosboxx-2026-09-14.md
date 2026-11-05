# S7 -- no-MIDI-backend-at-all isolation: patch landed, DOSBox-X validated -- 2026-09-14 (new session)

Continuation of `S7-midi-silent-chip-realhw-2026-09-14.md`'s own
decisive follow-up. Landed `patches/ags/0068` (`DOSAGS_MIDI_NO_
BACKEND=1`): checked in `AudioPlayer`'s MIDI-mode constructor, skips
`dos_midi_backend_open()` entirely -- no backend, OPL3 or otherwise, is
ever touched -- leaving `_midiSink` null. `midi_sched_open()` still
runs (parses the SMF into an in-memory event array) and `audio_core_
slot_init_midi()`'s own `DOSMIDI.TMP` scratch write still happens
(both upstream of this constructor). `MidiInit()`'s own existing
success check already handles a null `_midiSink` gracefully (the same
path "wb requested but cold-init failed" already exercises).

## DOSBox-X validation

`binary_sha12=433340f66668`. Same recipe as every prior S7 DOSBox-X
cell:

| Tag | Config | tick_rate | audio_vital_status | regwrite calls | slots_us mean |
|---|---|---:|---|---:|---:|
| `BASE4` | normal (sounding) regression check | 30.63 | midi=opl3,events=58 | 214 | 33 |
| `NOBK1` | `DOSAGS_MIDI_NO_BACKEND=1` | 30.58 | midi=none,events=0 | 0 | 3 |

`NOBK1`'s own `audio_vital_status` shows `midi=none,events=0` --
confirming `dos_midi_backend_open()` was never reached (its own
`DosMidiBackend: OPL3/OPL2 chip detected and initialized` banner does
not appear anywhere in `STDOUT.TXT`, checked directly, not inferred).
`slots_us` collapses to 3us, matching `SILNT1`'s own collapse. Clean
shutdown, no crash, no regression against `BASE4`.

**This DOSBox-X pass establishes correctness only.** Only real hardware
can answer whether "no MIDI backend touched at all" escapes the tax.

## Not yet done

1. The real-hardware cell -- the most decisive test in this whole
   sub-investigation. If `tick_rate` recovers toward the sound-off
   baseline (~23.8-23.9), the mechanism requires SOME backend (OPL3 or
   WaveBlaster specifically, or the generic `dos_midi_backend_open()`
   dispatch call itself) to have run at least once. If it still shows
   the collapsed ~2.5x band, the mechanism is entirely inside AGS's own
   generic MIDI-clip machinery above that dispatch point (`audio_core_
   slot_init_midi()`'s `DOSMIDI.TMP` write, or `midi_sched_open()`'s SMF
   parse, or simply having a `_isMidi` `AudioPlayer` object alive in
   `g_acore.slots_`) -- nothing to do with any DOS audio hardware at
   all, which would completely redirect this entire investigation's
   remaining search space to purely portable, hardware-independent
   engine code.
2. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0068, 0141, 0143-0144 all stay landed, all still temporary.
