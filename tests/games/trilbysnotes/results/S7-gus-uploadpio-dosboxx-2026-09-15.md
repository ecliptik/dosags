# S7-GUS -- .pat upload PIO + prepsong call-site cost diagnostics: patches landed, DOSBox-X validated -- 2026-09-15 (new session, continued)

Continuation of `S7-gus-voicecalls-miditick-realhw-2026-09-15.md`'s own
real-hardware result (tag `GUSV1`): `SDL_DOSGusGetState()`, all five
`SDL_DOSGus*` voice-setup/-teardown calls, and `midi_sched_tick()` itself
as a whole function are now all measured and exonerated -- none come
within three orders of magnitude of the ~6.89s single-call `slots_us`
outlier, reproduced within ~1100us of itself across three independent
real-hardware runs. That entry's own source read found the real
candidate: `AudioPlayer::Init()` (called once per song, BEFORE any of
the exonerated code ever runs) reaches `gus_sink_prepare_song()`
(`shared/audio/gus_sink.c`), which uploads every resident GM
instrument's `.pat` sample data into GUS DRAM via
`SDL_DOSGusUploadSample()` -> `gus_upload_pio()` -- a byte-wise ISA PIO
transfer loop that (with `SDL_HINT_DOS_GUS_PIO_AUTOINC` at its default
of off) re-selects the FULL DRAM address before every byte. This
instruments that candidate directly.

## Patches landed

- **`patches/SDL/0147`** (`vendor/SDL/src/audio/dos/SDL_dosaudio_gus.c`):
  brackets `gus_upload_pio()` and `SDL_DOSGusUploadSample()` (the
  function it's called from) each with their own uclock()-based
  accumulate-and-snapshot accessor -- `SDL_DOSGusUploadPioDiagSnapshot()`
  and `SDL_DOSGusUploadSampleDiagSnapshot()` -- each ALSO tracking total
  bytes transferred, so a real-hardware run can compute effective
  us/byte throughput and confirm or refute the byte-wise-overhead
  hypothesis quantitatively.
- **`patches/ags/0072`** (`Engine/platform/dos/dos_midi_backend.cpp`):
  brackets the `gus_sink_prepare_song()` CALL SITE inside
  `dos_midi_backend_prepare_song()` -- this port's own file, deliberately
  not `shared/audio/gus_sink.c` itself, same zero-blast-radius reasoning
  as the existing `miditick` call-site bracket. Captures the FULL
  per-song prepare cost (file I/O + every GUS upload it triggers + loop
  overhead), so the real-hardware run can compare this total against
  SDL/0147's own upload-specific numbers.
- **`patches/ags/0073`** (`Engine/media/audio/audio_core.cpp`): folds all
  three new snapshots into the existing `DOS-PORT audioprb` log line as
  `uploadpio(calls=... min_us=... mean_us=... max_us=... bytes=...)`,
  `uploadsample(...)` (same shape), and `prepsong(calls=... min_us=...
  mean_us=... max_us=...)` -- same discard-snapshot-before-the-slot-loop
  pattern as every earlier field.

## Build

`make all` succeeded cleanly with all three new patches applied on top
of the full existing series (SDL through 0147, ags through 0073,
`./scripts/verify-patches-applied.sh` confirmed clean before and after)
-- no new compiler errors or warnings beyond this project's existing
DJGPP inline-cost noise. `make build-sha12` -> `172b2d9ad4c6`, confirmed
matching `binary_sha12` in the OPL3 run's own RUNMANIFEST block below.

## DOSBox-X validation

Two runs against the same binary, `tests/harness/run-dosbox.sh
trilbysnotes`, `DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`,
`--fast` (cycles=max), a "sound on" `ACSETUP.CFG` (`[sound]
enabled=1`) staged via `--include-extra`.

### Run 1 -- GUS backend (matches this sub-investigation's own established recipe)

`SDL_HINT_DOS_AUDIO_BACKEND=gus`, `ULTRASND=240,3,3,7,7`,
`ULTRADIR=C:\ULTRASND`, scratch `[gus]` section (`gus=true gusbase=240
gusirq=7 gusdma=3`) appended to `dosbox-x-fast.conf`, reverted
immediately after (`diff` against the pre-edit copy confirmed clean).
Same known, already-documented gap as every prior GUS-backend DOSBox-X
pass in this investigation: DOSBox-X's `[gus]` emulation does not
present as real GF1 hardware with this configuration.

```
exit_code=0
audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=none,events=0
STDOUT.TXT: DosMidiBackend: SDL_HINT_DOS_AUDIO_BACKEND=gus requested, no GF1 detected -- MIDI disabled this session
DOS-PORT tick_rate=34.01 frames_skipped=30
DOS-PORT audioprb total_calls=200 window_calls=200 slots_us(min=3 mean=4 max=6) pump_us(min=4 mean=5 max=7) regwrite(calls=0 min_us=0 mean_us=0 max_us=0) gusscan(calls=0 min_us=0 mean_us=0 max_us=0) voicefreq(calls=0 min_us=0 mean_us=0 max_us=0) voicevol(calls=0 min_us=0 mean_us=0 max_us=0) voicepan(calls=0 min_us=0 mean_us=0 max_us=0) voicestart(calls=0 min_us=0 mean_us=0 max_us=0) voicestop(calls=0 min_us=0 mean_us=0 max_us=0) miditick(calls=0 min_us=0 mean_us=0 max_us=0) uploadpio(calls=0 min_us=0 mean_us=0 max_us=0 bytes=0) uploadsample(calls=0 min_us=0 mean_us=0 max_us=0 bytes=0) prepsong(calls=0 min_us=0 mean_us=0 max_us=0)
```

All twelve fields (nine pre-existing + three new) parse correctly. The
three new fields (`uploadpio`/`uploadsample`/`prepsong`) all correctly
read `calls=0 min_us=0 mean_us=0 max_us=0 bytes=0` here -- **expected,
not a wiring failure**: GF1 presence-detection fails under DOSBox-X's
`[gus]` emulation with this configuration (the same pre-existing gap
`gusscan`/the voice-call fields/`miditick` already hit), so `_midiSink`
stays null, `AudioPlayer::MidiInit()`'s own success check fails, and
neither `Init()`'s GUS-specific work nor `MidiPoll()`'s bracket ever
runs. Clean shutdown, no crash, no hang.

### Run 2 -- OPL3 backend (regression + log-pipeline confirmation)

`SDL_HINT_DOS_AUDIO_BACKEND=opl3`, scratch `oplmode = opl3` in
`dosbox-x-fast.conf` (stock hub confs ship `oplmode=none` by design),
reverted immediately after (`diff` clean). This backend cannot exercise
the three new GUS-specific fields either (wrong backend, same reasoning
as Run 1's own `voicefreq`/etc. zeros in every prior entry) -- its
purpose here is a cheap second confirmation that the whole build +
log-line-parsing pipeline is intact and unregressed.

```
exit_code=0
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=54
STDOUT.TXT: DosMidiBackend: OPL3/OPL2 chip detected and initialized
binary_sha12=172b2d9ad4c6
DOS-PORT tick_rate=30.63 frames_skipped=41
DOS-PORT audioprb total_calls=192 window_calls=192 slots_us(min=3 mean=36 max=4678) pump_us(min=36 mean=11716 max=15954) regwrite(calls=210 min_us=5 mean_us=21 max_us=22) gusscan(calls=0 min_us=0 mean_us=0 max_us=0) voicefreq(calls=0 min_us=0 mean_us=0 max_us=0) voicevol(calls=0 min_us=0 mean_us=0 max_us=0) voicepan(calls=0 min_us=0 mean_us=0 max_us=0) voicestart(calls=0 min_us=0 mean_us=0 max_us=0) voicestop(calls=0 min_us=0 mean_us=0 max_us=0) miditick(calls=92 min_us=5 mean_us=63 max_us=4670) uploadpio(calls=0 min_us=0 mean_us=0 max_us=0 bytes=0) uploadsample(calls=0 min_us=0 mean_us=0 max_us=0 bytes=0) prepsong(calls=0 min_us=0 mean_us=0 max_us=0)
```

`miditick(calls=92 min_us=5 mean_us=63 max_us=4670)` -- real, non-zero,
sane numbers, consistent with the prior `S7-gus-voicecalls-miditick-
dosboxx-2026-09-15.md` entry's own OPL3 confirmation (`calls=89
mean_us=66 max_us=4723` there) -- **no regression from these three new
patches**. `regwrite(calls=210...)` likewise real and unchanged in
character. All twelve fields present and parsing correctly; the three
new GUS-specific fields correctly zero (wrong backend). Clean shutdown,
no crash, no hang.

## What this confirms, and what it does not

**Confirms**: all three patches compile and link cleanly into the full
stack; the log line parses correctly with all twelve fields (nine
pre-existing + three new) in both configurations; no regression to any
pre-existing field (`miditick`, `regwrite` both still report real,
sane, in-line-with-precedent numbers under OPL3); the new GUS-specific
fields correctly read zero under both the "wrong backend" (OPL3) and
"GF1 not detected" (GUS) cases, matching established precedent exactly.

**Does not confirm**: anything about the actual ~6.89s real-hardware
outlier, or the byte-wise-PIO-overhead hypothesis itself. DOSBox-X
cannot exercise the `.pat`-upload code path under real GF1 dispatch at
all (the same boundary every GUS-specific field in this investigation
has hit) -- per this hub's "DOSBox-X is a correctness gate, not a
performance proxy" discipline, no DOSBox-X number in this entry should
be read as a performance result, real-hardware or otherwise.

## Not yet done

1. The real-hardware cell -- the actual measurement. Will show whether
   `uploadpio`/`uploadsample`'s own totals (and their `bytes` fields, for
   computing us/byte throughput) account for `GUST1`/`GUSD1`/`GUSV1`'s
   own ~6.89s outlier, whether `prepsong`'s own total (file I/O + every
   upload) is close to `uploadsample`'s sum (PIO transfer dominates) or
   notably larger (`.pat` file I/O is a separate real contributor), and
   whether the outlier is even the RIGHT ORDER OF MAGNITUDE for a
   byte-wise ISA PIO transfer of a real GM instrument set at this rig's
   real bus timing.
2. Needs the manual LED-polling boot-profile workaround (flagged as
   timing-sensitive per-session in the `GUSV1` entry -- may need fresh
   video-frame-extraction recalibration again, not assumed stable) and a
   fresh, separately-asked operator go-ahead before touching real
   hardware.
3. If confirmed: `SDL_HINT_DOS_GUS_PIO_AUTOINC=1` (an existing hint,
   never enabled by default) could plausibly cut the cost ~6x with zero
   new code -- a real, likely-fixable software cost, unlike the OPL3/
   WaveBlaster hardware constant this whole S7 arc otherwise reached.
4. Acceptance gate items 4 and 5 (re-targeted at GUS) remain open.
