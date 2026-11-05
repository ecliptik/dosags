# S7 -- SDL_INIT_AUDIO-never-touched, real-hardware result: the entire mechanism is outside SDL's audio subsystem -- 2026-09-14 (new session)

Operator-approved cell (tag `SUBSY2`, `binary_sha12=406c63249f6b`, the
patch-0066 build), HW-486-66, same recipe as `SUBSY1` plus `DOSAGS_AUDIO_
SUBSYSTEM_ONLY=2`. `run-rig.sh` completed cleanly end to end.

## Result

`SUBSY2.LOG`:

```
[RUNMANIFEST-BEGIN]
binary_sha12=406c63249f6b
duration_s=93
exit_code=0
fps_p50=0.48
fps_p95=0.52
audio_vital_status=NA
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=2.53 frames_skipped=168
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=16 mean=3029 max=24245) pump_us(min=19 mean=22 max=30) regwrite(calls=6079 min_us=21 mean_us=21 max_us=150)
DOS-PORT tickfx total_calls=34 window_calls=34 catchup_n_sum=167 catchup_us(min=965425 mean=2427968 max=34434427) realtick_us(min=118528 mean=459526 max=518752) catchup_yield(switches=0 min_us=0 mean_us=0 max_us=0) realtick_yield(switches=0 min_us=0 mean_us=0 max_us=0)
```

## Verdict: decisive and conclusive -- SDL's entire audio subsystem is uninvolved

**`tick_rate=2.53`** -- essentially identical to `SUBSY1`'s own **2.52**
(the "subsystem live, zero devices" arm). `catchup_us`/`realtick_us`
(495.1ms/459.5ms here vs. 495.3ms/456.8ms in `SUBSY1`) and, most
strikingly, **`regwrite calls=6079` -- the EXACT same count as `SUBSY1`**,
not just a similar order of magnitude. This means `SUBSY1` and `SUBSY2`
are, from the game's own perspective, doing byte-identical work: whether
`SDL_InitSubSystem(SDL_INIT_AUDIO)` is called or not makes zero
observable difference to anything, because nothing downstream ever reads
that state when the OPL3 MIDI backend is what's actually driving
playback.

**Conclusion**: `SDL_InitSubSystem(SDL_INIT_AUDIO)`'s own bookkeeping
contributes nothing. Combined with `SUBSY1`'s own finding (the SB16
backend contributes nothing), **the entire ~10-12x tax mechanism lives
entirely outside `vendor/SDL/src/audio/` -- not in `SDL_dosaudio_sb.c`,
not in SDL3's generic `SDL_audio.c` core, not in `SDL_InitSubSystem`
itself.** Fifteen real-hardware cells (`AUDIOFX1`-`4`, `DMAX1`, `NOBGT1`,
`OSA1`-`4`, `OSA1NT`-`4NT`, `SUBSY1`, `SUBSY2`) and this whole
investigation's search space up to this point were exploring code that,
while real and worth ruling out, was never where the mechanism could
have been.

## A promising-looking lead chased and correctly killed: the OPL PIT/IRQ-0 timer hijack

Before concluding the above, `SDL_dos_audio_synth.c` was searched for
anything OPL3-adjacent that could plausibly explain a uniform, per-tick,
"active MIDI backend" tax -- and a real, load-bearing-*looking*
mechanism was found: `SDL_DOSOplTimerPumpStart()` (`SDL_dosopltimer.h`)
reprograms PIT channel 0 (IRQ-0/INT-8, the system timer) to a custom
rate via `DOS_HookInterruptReplace`, replacing the timer ISR entirely
and driving `s_pump_tick_cb()` (the MIDI tick callback) directly from
interrupt context on every fire -- exactly the shape of thing that could
explain a system-wide, uniform slowdown independent of any specific
per-tick call site, since it would affect the PIT rate everything else
in DOS depends on. Its own guard (`if (SDL_DOSAudioSB_IsDeviceHot())
{ refused; }` -- "SINGLE OWNER of PIT ch0: never coexist with the SB
IRQ-5 clock... the PIT pump is the no-SB AdLib path only") means it
would have been REFUSED in every one of this investigation's prior
fifteen cells (all of which had `g_dos_sb_device_open=true` from
`OpenDevice`'s own earliest return point onward) but would be eligible
for the first time in `SUBSY1`/`SUBSY2` (which never call `OpenDevice`
at all, so `SDL_DOSAudioSB_IsDeviceHot()` is false).

**This was killed before being written up as a finding, by re-verifying
with `/usr/bin/grep` rather than trusting the first (Bash-builtin
`ugrep`-backed) search**, per this session's own standing note about
that tool's real false-negative history: `SDL_DOSOplTimerPumpStart` is
declared and exported (`SDL3/SDL_dosopltimer.h`), and its only OTHER
reference anywhere in `vendor/SDL`, `vendor/ags`, or `.sdl-dos-ports/
shared/audio` is a comment in `SDL_dosaudio_sb.c` -- **no caller exists
anywhere in this codebase.** `opl3_sink_open()` (`shared/audio/opl3_sink.c`)
calls only `SDL_DOSOpl3InitChip()` (register writes only, no interrupt
hooking, confirmed by reading its body). This port never wires the OPL
timer pump in at all -- a real, exported doskutsu-era feature this port
simply doesn't use. A correctly-avoided false lead, not a red herring
left unexamined.

## What remains: a genuinely narrow set of candidates, all pointing toward the OPL3 chip itself, not software

The only thing common to `SUBSY1`/`SUBSY2` (both show the full tax) and
absent from the sound-off baseline is: **a real OPL3 MIDI backend is
open and actively producing sound** (`dos_midi_backend_open()` ->
`opl3_sink_open()` -> `SDL_DOSOpl3InitChip()`, plus whatever `midi_sched_
tick()`/`SDL_DOSOpl3WriteRegister()` do when actually called). Critically,
**catch-up ticks call NEITHER `audio_core_entry_poll()` NOR any MIDI
function at all** (structurally confirmed since patch 0060 -- the call
is gated to `play.fast_forward` only) -- yet catch-up ticks pay the same
~495ms/tick tax as real ticks, identically in every cell measured so
far. This rules out, by construction, any hypothesis of the shape "MIDI
scheduling software work costs X per tick," since catch-up ticks
execute zero MIDI-related code and still pay the full tax.

**The only mechanism class left standing that can explain a cost paid by
ticks that call no audio-related code at all**: a real, continuous
hardware/electrical effect from the OPL3 chip (this rig's PicoGUS in
OPL3-emulation mode) actively synthesizing audio, independent of DOS-side
polling -- e.g. the PicoGUS's own RP2040 firmware needing to run a
real-time FM-synthesis loop for as long as any voice is sounding, with a
side effect on ISA bus response time/wait-states that a discrete OPL3
chip (pure analog-adjacent silicon, no firmware loop) would never have.
This is structurally the same SHAPE of hypothesis as the already-refuted
"DMA cycle-stealing" idea, but attributed to a completely different
chip/mechanism (OPL3 synthesis firmware, not SB16 DMA) that nothing in
this investigation has tested before, because nothing before this
session isolated OPL3 activity from the SB16 device's own concurrent
hardware state.

## Where this leaves the investigation

**Fourteen hypotheses now checked and refuted as the FULL explanation**
(everything listed in `S7-full-bisection-matrix-realhw-2026-09-14.md`,
plus SDL's generic audio core, `SDL_InitSubSystem(SDL_INIT_AUDIO)`, and
now confirmed: the entire SB16 backend and SDL audio subsystem
combined). **The search space has been correctly and dramatically
narrowed for the first time in this investigation**: from "somewhere in
SDL3-DOS's audio backend or generic core" to "the OPL3 chip's own
real-time synthesis activity, or something inside `shared/audio/opl3_
sink.c`/`midi_sched.c` never yet suspected as a primary mechanism
(only their per-write/per-tick software COST was ever checked, never
whether merely having an active chip is sufficient by itself)."

Acceptance gate items 4 and 5 remain FAIL. Patches 0059-0066, 0141,
0143-0144 all stay landed, all still temporary.

## Not yet done

1. **Silence-vs-sounding OPL3 test**: does the tax appear the moment
   `SDL_DOSOpl3InitChip()` runs (chip initialized, all voices key-off,
   never actually producing audible output), or only once a real note
   is key-on and audibly synthesizing? This would distinguish "chip
   merely initialized" from "chip actively synthesizing" as the trigger
   condition -- needs a new diagnostic (e.g. a hint that opens the OPL3
   chip but never dispatches any MIDI note-on event) and would need its
   own DOSBox-X validation pass before real hardware, per this
   investigation's own established rhythm.
2. A source read of `shared/audio/midi_sched.c`'s own `midi_sched_tick()`
   and `opl3_sink.c`'s own per-note dispatch, specifically looking for
   anything that could impose a cost OUTSIDE the already-measured
   `audio_core_entry_poll()` call path (the only site examined so far) --
   e.g. anything registered as a periodic callback reachable from a
   generic per-tick site this investigation hasn't traced yet.
3. Acceptance gate items 4 and 5 remain FAIL.
