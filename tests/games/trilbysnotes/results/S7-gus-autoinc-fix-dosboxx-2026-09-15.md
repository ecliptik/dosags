# S7-GUS -- default GUS DRAM upload to auto-increment mode: patch landed, DOSBox-X validated -- 2026-09-15 (new session, continued)

Continuation of `S7-gus-uploadpio-realhw-2026-09-15.md`'s own real-hardware
result (tag `GUSU1`): `prepsong` (the `gus_sink_prepare_song()` call site)
measured `max_us=6,891,245`, within 218us of `slots_us`'s own ~6.89s
outlier -- the same event. Within it, `uploadpio`/`uploadsample` (the
byte-wise GUS DRAM upload) accounted for ~6.05s of it at a measured
~115 KB/s (~8.5us/byte). Root cause: `gus_upload_pio()`'s default path
re-selects the full GF1 DRAM address before every single byte
(`g_gus_pio_autoinc` defaults `false`). This lands the fix.

## Patch landed

- **`patches/ags/0074`** (`Engine/platform/dos/dos_midi_backend.cpp`):
  `dos_midi_backend_open()`'s GUS case now sets
  `SDL_HINT_DOS_GUS_PIO_AUTOINC=1` as this port's own DEFAULT (via a
  null-hint check, not an unconditional `SDL_SetHint`) before
  `gus_sink_open()` -> `SDL_DOSGusInit()` first reads and caches it. An
  explicit `SDL_HINT_DOS_GUS_PIO_AUTOINC=0` or `=1` set elsewhere
  (`RUN.BAT`'s own `SET`, or a direct `SDL_SetHint` call) still wins, so
  a real-hardware A/B comparison cell can still force either path
  deliberately. Deliberately a dosags-side default (this file, not the
  vendored `SDL_dosaudio_gus.c`) -- keeps the original SDL author's own
  conservative default untouched, scoped entirely to this port's own
  `patches/ags/` series, trivially revertible.

**Important safety context, not resolved by this entry**: autoinc mode
was originally written (SDL patch SDL/0112) as the fix for a documented
real CPU-freeze hazard on real GF1 hardware (a PicoGUS RP2040 can
assert IOCHRDY under the per-byte path's port-op flood, stalling the ISA
bus indefinitely while interrupts are disabled), left off by default
"until g2k confirms autoinc reaches gameplay, then flip to ON" -- a
confirmation this hub's own history shows never happened. Autoinc mode
itself has NEVER been exercised on real GF1 hardware before this patch.
**Nothing in this entry validates autoinc's real-hardware safety** --
see "What this does not confirm" below.

## Build

`make all` succeeded cleanly with `patches/ags/0074` applied on top of
the full existing series (`./scripts/verify-patches-applied.sh`
confirmed clean before and after) -- no new compiler errors or warnings
beyond this project's existing DJGPP inline-cost noise. `make
build-sha12` -> `54d51604e8d8`.

## DOSBox-X validation

Two runs against the same binary, `tests/harness/run-dosbox.sh
trilbysnotes`, `DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`,
a "sound on" `ACSETUP.CFG` (`[sound] enabled=1`, freshly regenerated via
`tools/port-game/port_game.py layout` against the already-staged
`tests/harness/games/trilbysnotes/NOTES.ags`) staged via
`--include-extra`.

### Run 1 -- GUS backend (matches this sub-investigation's own established recipe)

`SDL_HINT_DOS_AUDIO_BACKEND=gus`, `ULTRASND=240,3,3,7,7`,
`ULTRADIR=C:\ULTRASND`, scratch `[gus]` section (`gus=true gusbase=240
gusirq=7 gusdma=3`) appended to `tools/dosbox-x-fast.conf`, reverted
immediately after (sha256 of the reverted file matches the pre-edit
original exactly). Same known, already-documented gap as every prior
GUS-backend DOSBox-X pass in this investigation: DOSBox-X's `[gus]`
emulation does not present as real GF1 hardware with this
configuration.

```
[RUNMANIFEST-BEGIN]
schema_version=1
environment=dosbox-x
binary_sha12=54d51604e8d8
duration_s=7
exit_code=0
fps_p50=33.65
fps_p95=41.35
audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=none,events=0
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=33.11 frames_skipped=34
DOS-PORT audioprb total_calls=198 window_calls=198 slots_us(min=4 mean=4 max=9) pump_us(min=4 mean=5 max=12) regwrite(calls=0 min_us=0 mean_us=0 max_us=0) gusscan(calls=0 min_us=0 mean_us=0 max_us=0) voicefreq(calls=0 min_us=0 mean_us=0 max_us=0) voicevol(calls=0 min_us=0 mean_us=0 max_us=0) voicepan(calls=0 min_us=0 mean_us=0 max_us=0) voicestart(calls=0 min_us=0 mean_us=0 max_us=0) voicestop(calls=0 min_us=0 mean_us=0 max_us=0) miditick(calls=0 min_us=0 mean_us=0 max_us=0) uploadpio(calls=0 min_us=0 mean_us=0 max_us=0 bytes=0) uploadsample(calls=0 min_us=0 mean_us=0 max_us=0 bytes=0) prepsong(calls=0 min_us=0 mean_us=0 max_us=0)
```

`STDOUT.TXT`: `DosMidiBackend: SDL_HINT_DOS_AUDIO_BACKEND=gus requested,
no GF1 detected -- MIDI disabled this session`. All twelve fields parse
correctly, all GUS-specific fields (including the three upload-chain
fields this whole fix targets) correctly read `calls=0` -- expected,
not a regression: `_midiSink` stays null when GF1 presence fails, so
neither `Init()`'s GUS-specific work (autoinc-gated or not) nor any of
the brackets ever run. Clean shutdown, no crash, no hang.

### Run 2 -- OPL3 backend (no-regression check)

`SDL_HINT_DOS_AUDIO_BACKEND=opl3`, scratch `oplmode = opl3` in
`tools/dosbox-x-fast.conf`, reverted immediately after (sha256 confirmed
matching the original). This backend never touches any GUS code path at
all (wrong backend), so it cannot exercise this fix either way --
purpose here is a cheap confirmation that the fix introduces no
regression to the pre-existing OPL3 path.

```
[RUNMANIFEST-BEGIN]
schema_version=1
environment=dosbox-x
binary_sha12=54d51604e8d8
duration_s=10
exit_code=0
fps_p50=22.86
fps_p95=25.96
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=58
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=27.82 frames_skipped=86
DOS-PORT audioprb total_calls=146 window_calls=146 slots_us(min=4 mean=48 max=4826) pump_us(min=42 mean=11333 max=16018) regwrite(calls=214 min_us=4 mean_us=21 max_us=23) gusscan(calls=0 min_us=0 mean_us=0 max_us=0) voicefreq(calls=0 min_us=0 mean_us=0 max_us=0) voicevol(calls=0 min_us=0 mean_us=0 max_us=0) voicepan(calls=0 min_us=0 mean_us=0 max_us=0) voicestart(calls=0 min_us=0 mean_us=0 max_us=0) voicestop(calls=0 min_us=0 mean_us=0 max_us=0) miditick(calls=60 min_us=6 mean_us=100 max_us=4816) uploadpio(calls=0 min_us=0 mean_us=0 max_us=0 bytes=0) uploadsample(calls=0 min_us=0 mean_us=0 max_us=0 bytes=0) prepsong(calls=0 min_us=0 mean_us=0 max_us=0)
```

`miditick(calls=60, mean_us=100, max_us=4816)` and `regwrite(calls=214,
...)` both real, non-zero, and consistent in character with every prior
OPL3-backend pass in this investigation -- **no regression from this
fix**. `STDOUT.TXT` confirms `DosMidiBackend: OPL3/OPL2 chip detected
and initialized`. Clean shutdown, no crash, no hang.

## What this confirms, and what it does not

**Confirms**: the patch compiles and links cleanly into the full stack;
the fix introduces no regression to the pre-existing OPL3 path or to
the log line's own parsing (all twelve fields present and correct in
both configurations); the GUS-side no-op behavior under DOSBox-X's own
known GF1-detection gap is unchanged from every prior pass.

**Does NOT confirm, and cannot**: anything about autoinc mode's real
GF1-hardware behavior, safety, or correctness. DOSBox-X's `[gus]`
emulation does not present as real GF1 hardware under this
configuration (the same boundary every GUS-specific field in this
investigation has hit) -- it cannot exercise `gus_upload_pio()` under
real GF1 semantics at all, autoinc or not. Per this hub's "DOSBox-X is
a correctness gate, not a performance proxy" discipline (and, here,
not a real-hardware-behavior proxy either), nothing in this entry
should be read as evidence that autoinc mode is safe on real hardware.

## Not yet done

1. **The real, carefully-supervised real-hardware validation.** Autoinc
   mode has never been exercised on real GF1 hardware before this
   patch -- its first real-hardware run must be treated as a first-time
   validation of previously-unexercised code (originally written as a
   fix for a documented CPU-freeze hazard in the path it replaces), not
   a routine re-measure. This is the parent session's own next step,
   with its own fresh, separately-asked operator go-ahead.
2. If confirmed safe and effective: compare the new real-hardware
   `prepsong`/`uploadpio`/`uploadsample` numbers directly against
   `GUSU1`'s own baseline to measure the actual (not extrapolated)
   speedup, then revert the now-fully-spent S7/S7-GUS diagnostic
   patches, then a proper ABBA before claiming acceptance gate items
   4/5.
3. If a hang or instability is observed instead: this fix must NOT be
   kept as the default -- revert `patches/ags/0074` and record the
   observation as confirmation of the original #41 freeze hazard
   persisting on this rig's current PicoGUS firmware.
