# S7-GUS -- GUS voice-setup call + midi_sched_tick() call-site cost diagnostics: patches landed, DOSBox-X validated -- 2026-09-15 (new session)

Continuation of `S7-gus-getstate-cost-realhw-2026-09-15.md`'s own "Not yet
done" items. `SDL_DOSGusGetState()` (patch SDL/0145) came back exonerated
on real hardware (tags GUST1/GUSD1): only 28 calls, 27-170us each, ~3ms
total, nowhere near `slots_us`'s own 101ms mean / 6.9s max. That entry
also found the ~6.89s outlier is ONE single call inside the MIDI slot
`Poll()` loop, nearly identical across two independent runs (175us apart
out of 6.89 SECONDS) -- a deterministic mechanism tied to the song/scene
content, not I/O jitter or call-volume aggregation. This measures the
remaining unmeasured candidates before proposing any fix, per this hub's
own "instrument the thing that produces the unexplained quantity, not its
neighbors" rule, applied a third time in this sub-investigation.

## Patches landed

- **`patches/SDL/0146`** (`vendor/SDL/src/audio/dos/SDL_dosaudio_gus.c`):
  brackets `SDL_DOSGusSetVoiceFreq`, `SetVoiceVol`, `SetVoicePan`,
  `StartVoice`, and `StopVoice` -- the five SDL_DOSGus* functions
  `gus_sink.c`'s `sink_note_on`/`sink_note_off`/`reap_finished_voices`/
  `sink_on_tick` call -- with the same uclock()-based accumulate-and-
  snapshot idiom as `SDL_DOSGusGetState()` (patch SDL/0145). Five
  independent accessors, not one combined total, so a real-hardware run
  can attribute the outlier to a specific function. `StopVoice` is a real
  addition beyond the four functions originally flagged (SetVoiceFreq/
  Vol/Pan/StartVoice): it sits in the same reap/note-off call graph, is
  equally unmeasured, and costs nothing extra to add to the same
  real-hardware run.
- **`patches/ags/0070`** (`Engine/media/audio/audio_core.cpp`): folds the
  five new snapshots into the existing `DOS-PORT audioprb` log line as
  `voicefreq(...)`, `voicevol(...)`, `voicepan(...)`, `voicestart(...)`,
  `voicestop(...)`, same discard-snapshot-before-the-slot-loop pattern as
  `regwrite`/`gusscan`.
- **`patches/ags/0071`** (`audioplayer.cpp` + `audio_core.cpp`): brackets
  the `midi_sched_tick()` CALL SITE inside `AudioPlayer::MidiPoll()`
  (this port's own file) -- deliberately NOT `shared/audio/midi_sched.c`
  itself, which is hub-owned code every port consumes via the
  `.sdl-dos-ports/` subtree/submodule; the exact same measurement is
  available by timing the call site instead, with zero blast radius
  beyond this port. Exposes `DOSAGS_MidiTickDiagSnapshot()`, folded into
  the same log line as a sixth new field, `miditick(...)`.

All three source-verified (every one of the five SDL_DOSGus* functions is
a bounded handful of `outportb()`/`inportb()` calls, cli/sti-wrapped, no
retry/poll loop anywhere in their own call graph -- `gus_select_voice`,
`gus_w8`, `gus_w16`, `gus_hz_to_fc`, `gus_linear_to_logvol`,
`gus_encode_addr` all checked) -- but that was also true of
`SDL_DOSGusGetState()` before it was measured, and this file's own
`SDL_DOSMpu401WaitDRR`/SDL/0093 precedent shows a single outportb/inportb
CAN cost far more than source reading predicts on a real ISA bus,
regardless of loop structure. Measuring, not trusting the read.

## Build

`make all` (SDL3 + AGS engine stage) succeeded cleanly with all three new
patches applied -- no new compiler errors or warnings beyond this
project's existing DJGPP inline-cost noise. `make build-sha12` ->
`760ec38b22ea`, confirmed matching `binary_sha12` in both RUNMANIFEST
blocks below.

## DOSBox-X validation

Two runs against the same binary (`binary_sha12=760ec38b22ea`), reusing
the already-converted `NOTES.AGS`/`ACSETUP.CFG` package staged by a prior
session (no game-data re-download needed), `DOSAGS_FIXED_TIMESTEP=1`,
`DOSAGS_TAS_AUTO_EXIT_TICK=200`, `--fast` (cycles=max).

### Run 1 -- OPL3 backend (real non-zero `miditick` confirmation)

`SDL_HINT_DOS_AUDIO_BACKEND=opl3`, scratch `oplmode = opl3` in
`dosbox-x-fast.conf` (stock hub confs ship `oplmode=none` by design, same
precedent as `TNSNDON2`), reverted immediately after (`diff` against the
pre-edit copy confirmed clean). OPL3 dispatches for real under DOSBox-X
(unlike GUS), so this is the one run that can confirm `miditick`'s own
wiring end-to-end with real numbers, the same way `regwrite` was
originally validated.

```
exit_code=0
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=54
DOS-PORT tick_rate=28.86 frames_skipped=51
DOS-PORT audioprb total_calls=181 window_calls=181 slots_us(min=3 mean=38 max=4731) pump_us(min=37 mean=11328 max=15970) regwrite(calls=210 min_us=4 mean_us=21 max_us=23) gusscan(calls=0 min_us=0 mean_us=0 max_us=0) voicefreq(calls=0 min_us=0 mean_us=0 max_us=0) voicevol(calls=0 min_us=0 mean_us=0 max_us=0) voicepan(calls=0 min_us=0 mean_us=0 max_us=0) voicestart(calls=0 min_us=0 mean_us=0 max_us=0) voicestop(calls=0 min_us=0 mean_us=0 max_us=0) miditick(calls=89 min_us=5 mean_us=66 max_us=4723)
```

**`miditick(calls=89 min_us=5 mean_us=66 max_us=4723)`** -- real,
non-zero, sane numbers (89 calls across the run, matching `AudioPlayer::
MidiPoll()`'s own once-per-real-tick call rate). **Confirms the
call-site bracket's wiring works end-to-end.** `gusscan`/`voicefreq`/
`voicevol`/`voicepan`/`voicestart`/`voicestop` all correctly read
`calls=0` here -- expected, not a gap: this run uses the OPL3 backend, so
no `SDL_DOSGus*` function is ever called. `regwrite(calls=210...)` is the
pre-existing OPL3 diagnostic, also real and non-zero, cross-confirming
the log line's overall parsing is intact with all nine fields (three
pre-existing + six new) present.

### Run 2 -- GUS backend (matches this sub-investigation's own established recipe)

`SDL_HINT_DOS_AUDIO_BACKEND=gus`, `ULTRASND=240,3,3,7,7`,
`ULTRADIR=C:\ULTRASND`, scratch `[gus]` section (`gus=true gusbase=240
gusirq=7 gusdma=3`) appended to `dosbox-x-fast.conf`, reverted immediately
after (`diff` clean). Same known, already-documented gap as
`S7-gus-midi-dosboxx-2026-09-14.md` and
`S7-gus-getstate-cost-dosboxx-2026-09-14.md`: DOSBox-X's `[gus]`
emulation does not present as real GF1 hardware.

```
exit_code=0
audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=none,events=0
STDOUT.TXT: DosMidiBackend: SDL_HINT_DOS_AUDIO_BACKEND=gus requested, no GF1 detected -- MIDI disabled this session
DOS-PORT tick_rate=33.39 frames_skipped=24
DOS-PORT audioprb total_calls=200 window_calls=200 slots_us(min=3 mean=3 max=6) pump_us(min=4 mean=4 max=7) regwrite(calls=0 min_us=0 mean_us=0 max_us=0) gusscan(calls=0 min_us=0 mean_us=0 max_us=0) voicefreq(calls=0 min_us=0 mean_us=0 max_us=0) voicevol(calls=0 min_us=0 mean_us=0 max_us=0) voicepan(calls=0 min_us=0 mean_us=0 max_us=0) voicestart(calls=0 min_us=0 mean_us=0 max_us=0) voicestop(calls=0 min_us=0 mean_us=0 max_us=0) miditick(calls=0 min_us=0 mean_us=0 max_us=0)
DOS-PORT audioprb total_calls=208 window_calls=8 slots_us(min=3 mean=3 max=4) pump_us(min=4 mean=4 max=5) regwrite(calls=0 ...) gusscan(calls=0 ...) voicefreq(calls=0 ...) voicevol(calls=0 ...) voicepan(calls=0 ...) voicestart(calls=0 ...) voicestop(calls=0 ...) miditick(calls=0 ...)
```

All six new fields correctly read `calls=0 min_us=0 mean_us=0 max_us=0`
here, including `miditick` -- **this is expected, not a wiring failure**:
GF1 presence-detection fails under DOSBox-X's `[gus]` emulation with this
configuration (the same pre-existing gap `gusscan` already hit), so
`_midiSink` stays null, `AudioPlayer::MidiInit()`'s own success check
fails, `_playState` becomes `PlayStateError`, and `MidiPoll()` returns
before ever reaching the `midi_sched_tick()` call this bracket wraps --
correctly zero calls, matching the discard-snapshot idiom's own
attribution-correctness design. Clean shutdown, no crash, no hang, no
regression against the prior binary (`433340f66668`/`c6d6f6626df8`
family).

## What this confirms, and what it does not

**Confirms**: all three patches compile and link cleanly into the full
stack; the log line parses correctly with all nine fields (three
pre-existing + six new) in both configurations; `miditick`'s wiring is
proven correct with real, non-zero, sane numbers (Run 1); the GUS-side
fields correctly read zero under both the "wrong backend" (Run 1) and
"GF1 not detected" (Run 2) cases, matching established precedent exactly.

**Does not confirm**: anything about the actual ~6.89s real-hardware
outlier. DOSBox-X cannot exercise the GUS voice-setup/`midi_sched_tick()`
code paths under real GF1 dispatch at all (the same boundary `gusscan`
already hit) -- per this hub's "DOSBox-X is a correctness gate, not a
performance proxy" discipline, no DOSBox-X number in this entry should be
read as a performance result, real-hardware or otherwise.

## Not yet done

1. The real-hardware cell -- the actual measurement. Will show whether
   the five per-voice-call snapshots (`voicefreq`/`voicevol`/`voicepan`/
   `voicestart`/`voicestop`) fully account for `GUST1`/`GUSD1`'s own
   ~6.89s `slots_us` outlier once summed, or whether a residual remains
   inside `midi_sched_tick()` itself once `miditick`'s own total is
   compared against their sum -- pointing at the `delta_ms>10000`
   catch-up clamp, the dispatch `for(;;)` loop, or `SDL_DOSGusAllocVoice()`
   (none of which are separately instrumented this pass).
2. Needs the manual LED-polling boot-profile workaround
   (`--boot-profile 3` / `select_boot_profile()` is still a known,
   unfixed gap for this rig/profile combination) and a fresh, separately-
   asked operator go-ahead before touching real hardware.
3. Acceptance gate items 4 and 5 (re-targeted at GUS) remain open.
