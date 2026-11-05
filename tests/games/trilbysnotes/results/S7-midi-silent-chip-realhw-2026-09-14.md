# S7 -- silence-vs-sounding OPL3, real-hardware result: sounding is NOT required either -- 2026-09-14 (new session)

Operator-approved cell (tag `SILNT1`, `binary_sha12=218a42297d8f`, the
patch-0067 build), HW-486-66, same recipe as every prior S7 cell plus
`DOSAGS_MIDI_SILENT_CHIP=1`. `run-rig.sh` completed cleanly end to end.

## Result

`SILNT1.LOG`:

```
[RUNMANIFEST-BEGIN]
binary_sha12=218a42297d8f
duration_s=95
exit_code=0
fps_p50=0.48
fps_p95=0.51
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=0
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=2.48 frames_skipped=168
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=16 mean=29 max=87) pump_us(min=6576 mean=11323 max=15210) regwrite(calls=0 min_us=0 mean_us=0 max_us=0)
DOS-PORT tickfx total_calls=34 window_calls=34 catchup_n_sum=167 catchup_us(min=973470 mean=2447965 max=34769004) realtick_us(min=119109 mean=467657 max=513674) catchup_yield(switches=2 min_us=245 mean_us=918301 max_us=1836357) realtick_yield(switches=648 min_us=39 mean_us=101601 max_us=4166232)
```

`events=0` and `regwrite calls=0` confirm the design worked exactly as
intended: zero MIDI events ever dispatched, zero register writes beyond
the one-time `SDL_DOSOpl3InitChip()` sequence (which this diagnostic
does not track, by construction). `slots_us` mean collapsed to 29us
(matching the DOSBox-X prediction of ~4-30us for an idle slot loop).
`DosMidiBackend: OPL3/OPL2 chip detected and initialized` still fired in
`STDOUT.TXT` -- the chip genuinely was opened and programmed.

## Verdict: `tick_rate=2.48` -- the FULL tax, identical to a fully-sounding run

**`tick_rate=2.48`** matches `NOBGT1`/`DMAX1` (2.48-2.50) almost exactly
-- **not** a partial recovery, **not** the ~5x floor, the **full**
~10-12x collapsed band, with the OPL3 chip never told to play a single
note for the entire 95-second run. `catchup_us`/`realtick_us`
(499.6ms/467.7ms, computing catchup per-tick as 2447965/(167/34)) are
statistically indistinguishable from every other full-tax cell.

**This conclusively rules out "active synthesis" as the trigger
condition.** Merely opening/programming the OPL3 chip (`SDL_
DOSOpl3InitChip()`'s roughly twenty register writes: enable OPL3 mode,
disable 4-op, key-off all 18 voices) is sufficient by itself -- whether
the chip ever subsequently produces audible output makes no measurable
difference.

## A real cross-check this entry has to reconcile: WaveBlaster already showed the same collapse, with zero OPL3 involvement at all

`S7-abba-2026-09-13.md`'s own diagnostic cell (`TNWB1`, the very first
session of this whole investigation) swapped OPL3 for WaveBlaster --
completely different hardware (MPU-401 UART passthrough, no `SDL_
DOSOpl3WriteRegister()` calls, no `SDL_DOSOpl3InitChip()` at all) -- and
the collapse reproduced almost exactly (0.55 fps, tick_rate 3.22,
explicitly noted as "not OPL3-specific" at the time). `TNWB1` genuinely
dispatched MIDI events (real `midi_sched_start()`/`midi_sched_tick()`
activity, unlike `SILNT1`).

**Reconciling these two facts**: the mechanism cannot be specific to
`SDL_DOSOpl3InitChip()`'s own register writes (WaveBlaster never calls
that function at all) and cannot require real dispatch/scheduling
activity either (`SILNT1` proves the tax with `midi_sched_start()`
never even called). The only code genuinely common to *every* sound-on
cell in this entire investigation, across every combination of backend
and every diagnostic tried so far, is the generic, backend-agnostic path
above `dos_midi_backend_open()`'s own dispatch: `audio_core_slot_init_
midi()` (writes the SMF bytes to `DOSMIDI.TMP` via `fopen`/`fwrite`/
`fclose`, then constructs an `AudioPlayer` in MIDI mode) and `midi_sched_
open()` (parses the SMF into an in-memory event array) -- both one-time,
both already run identically in `SILNT1` (since `DOSAGS_MIDI_SILENT_
CHIP=1` only skips `midi_sched_start()`, nothing upstream of it).

**None of these are per-tick actions**, which is the same structural
puzzle every OPL3/SB16-hardware hypothesis already ran into: something
established ONCE, near the start of a song, has to be leaving the
system in a persistently altered state that taxes literally every
subsequent tick uniformly -- catch-up ticks included, which call zero
audio-related code of any kind. The candidate pool for that one-time
action, given everything ruled out so far (SB16 backend entirely,
SDL's audio subsystem entirely, OPL3 register-write activity, MIDI
scheduling/dispatch activity), is now down to: `dos_midi_backend_open()`
itself (even the "detect chip, program it" call, independent of
subsequent dispatch), or something even further upstream in `audio_
core_slot_init_midi()`/`midi_sched_open()`'s own one-time work that has
never been isolated from backend selection at all.

## Where this leaves the investigation

**Fifteen hypotheses now checked and refuted as the full explanation**,
plus this entry's "active synthesis" candidate. The search space is
narrower than ever but the mechanism is still not found: it must be a
one-time action taken somewhere between "no MIDI backend touched at
all" (the sound-off baseline) and "OPL3 chip programmed, never played"
(`SILNT1`, still fully collapsed) -- and it must generalize across
completely different physical backends (OPL3, WaveBlaster/MPU-401),
which rules out any hardware-electrical hypothesis tied to a SPECIFIC
chip (the PicoGUS-OPL3-emulation-firmware idea from the prior entry is
now also dead, since WaveBlaster doesn't touch that emulation path at
all).

Acceptance gate items 4 and 5 remain FAIL. Patches 0059-0067, 0141,
0143-0144 all stay landed, all still temporary.

## Not yet done

1. **The decisive next test**: skip `dos_midi_backend_open()` entirely
   in `AudioPlayer`'s MIDI constructor (so no backend -- OPL3, WB, or
   otherwise -- is ever touched), while still writing `DOSMIDI.TMP` and
   calling `midi_sched_open()` to parse it. If the tax survives even
   here, the entire mechanism is somewhere in AGS's own generic
   MIDI-clip machinery (`audio_core_slot_init_midi()`, `midi_sched_
   open()`, or simply having a `_isMidi` `AudioPlayer` object alive in
   `g_acore.slots_`) -- nothing to do with any DOS hardware backend at
   all, which would be the most surprising finding of this entire
   investigation. If it recovers, the one-time backend-open call itself
   (chip detection/programming, independent of a specific chip) is
   implicated -- needs a new diagnostic, DOSBox-X validation, then real
   hardware, per this investigation's own established rhythm.
2. Acceptance gate items 4 and 5 remain FAIL.
