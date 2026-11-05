# S7 -- AUDIOPRB.LOG real-hardware confirmation + a new lead -- 2026-09-14

Continuation of `S7-fix-realhw-2026-09-14.md`'s "second open question"
and `PLAN.md`'s "S7 -- AUDIOPRB.LOG real-hardware gap" section (patch
0061). Single operator-approved real-hardware cell, HW-486-66, to answer
one question only: does the rebuilt diagnostic sink (patch 0061, dumping
through `quit.cpp`'s own already-reliable RUNMANIFEST-tag handle instead
of a separately-reopened `AUDIOPRB.LOG`) actually produce data on the
real target. Not a full ABBA -- acceptance gate items 4/5 are not
re-attempted by this cell; that needs its own separately-approved
campaign, pre-registered thresholds, and (per `S7-fix-realhw-2026-09-14
.md`'s own "Not yet done" item 2) the `wait_for_stable_screen()` fix
first.

## Cell

`run-rig.sh trilbysnotes --tag AUDIOFX1 --env DOSAGS_FIXED_TIMESTEP=1
--env DOSAGS_TAS_AUTO_EXIT_TICK=200 --env SDL_HINT_DOS_AUDIO_BACKEND=opl3
--extra-file ACSETUP.CFG:ACSETUP.CFG` (minimal `[sound]\nenabled=1`
config -- not game data, a trivial engine config value). Tick cap chosen
deliberately low (200, vs the acceptance-gate ABBA's 1000) to keep real
wall-clock duration well under `wait_for_stable_screen()`'s 90s floor,
sidestepping the known low-fps false-positive hazard entirely rather
than re-triggering it for a cell that doesn't need the full acceptance
workload. Binary staged and verified byte-for-byte
(`sha256=7c78f3148b...fafb986a`, matches the local `build/ags/ags.exe`
computed before staging); `binary_sha12=cdf5cb19a6c9` (patch 0061
applied, differs from 0059+0060's `6e4c8a677027` since source changed).

## Result: real data, first time ever

```
[RUNMANIFEST-BEGIN]
schema_version=1
environment=realhw
binary_sha12=cdf5cb19a6c9
wave_tag=AUDIOFX1
duration_s=79
exit_code=0
fps_p50=0.59
fps_p95=0.61
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=639
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT memory_min_free_kb=154880
DOS-PORT tick_rate=2.97 frames_skipped=168
DOS-PORT audioprb total_calls=65 windows_recorded=1 windows_dropped=0
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=11 mean=1403 max=15270) pump_us(min=6398 mean=11137 max=15133)
```

Clean run (`exit_code=0`, `critical_count=0`, `warn_count=0`), genuine
real hardware (`environment=realhw`, not misdetected), real OPL3 chip
detected and used (`STDOUT.TXT`: "DosMidiBackend: OPL3/OPL2 chip
detected and initialized", `events=639`). `tick_rate=2.97` is in the
same collapsed regime every other real-hardware sound-on cell in this
investigation has shown (2.97-3.37 across every OPL3/WaveBlaster
sound-on cell recorded so far) -- this cell reproduces the same problem
under investigation, not a different one. Full raw files:
`AUDIOFX1.LOG`, `AUDIOFX1-STDOUT.TXT` (this directory).

**The fix works**: patch 0061's sink produced real, non-empty
`DOS-PORT audioprb` data from a genuine real-hardware sound-on run --
the first time this has ever happened in this investigation, across two
prior real-hardware sound-on attempts (2026-09-13's B1/B2, 2026-09-14's
F7B1/F7B2) that both produced nothing.

## A new lead: `slots_us` is NOT cheap on real hardware

This is genuinely new information, not previously measurable. Compare
this cell's real-hardware numbers to the DOSBox-X-measured numbers
`S7-fix-dosbox-x-2026-09-14.md` used to justify patch 0060:

| | DOSBox-X (0059's own validation) | HW-486-66 (this cell) |
|---|---|---|
| `slots_us` mean | 22-126 | **1403** |
| `slots_us` max | (not recorded, same order as mean) | **15270** |
| `pump_us` mean | 10,300-11,144 | 11,137 |
| `pump_us` max | (not recorded) | 15133 |

`pump_us` (the `dos_audio_mixer_pump()` / `SDL_DOSAudioPump()` ->
`WaitDevice()` cost patch 0060's whole fix was built around) matches
DOSBox-X closely -- ~11.1ms mean in both places. That part of the
DOSBox-X measurement generalizes fine.

`slots_us` (the slot `Poll()` loop -- MIDI scheduling, real OPL3
register I/O via `midi_sched_tick()`) does **not** generalize at all:
over 10x DOSBox-X's own mean, and its real-hardware *max* (15270us) is
in the same range as `pump_us`'s own max -- meaning on real hardware,
the MIDI-scheduling half of `audio_core_entry_poll()` can cost as much
as the mixer-pump half, something DOSBox-X's OPL3/timing emulation does
not reproduce at all (its own measurement showed `slots_us` as cheap,
"tens of microseconds", by comparison).

This plausibly explains `S7-fix-realhw-2026-09-14.md`'s own open
question #1 ("why doesn't the real-hardware cost track the
DOSBox-X-measured mechanism"): patch 0060 only removed *extra* calls to
`audio_core_entry_poll()` during catch-up bursts, leaving exactly one
call per real `GameTick()` untouched. If BOTH halves of that one
remaining call are expensive on real hardware (not just the pump half,
as DOSBox-X suggested), then reducing the call *count* was never going
to move the number much -- the surviving single call was already paying
something on the order of `slots_us + pump_us` ~= 12-26ms per real tick,
which alone is enough to explain a collapse to ~3 ticks/s regardless of
how many times it's called.

**This is one data point (one window, 65 calls, one cell) -- real, not
guessed, but not yet a confirmed mechanism.** Worth checking before
trusting it further: whether `slots_us`'s mean/max here is dominated by
genuine OPL3 register I/O wait states (plausible -- real OPL3 chips have
documented write-timing requirements DOSBox-X's emulation may not model
faithfully) or by something else in the slot `Poll()` loop unrelated to
MIDI at all. Multiple windows across a longer run (the full
`DOSAGS_TAS_AUTO_EXIT_TICK=1000` acceptance-gate workload, once
`wait_for_stable_screen()` is fixed) would also show whether this is
consistent or a one-off spike this single 65-call window happened to
catch.

## Not yet done

1. Multi-window real-hardware confirmation (this cell only crossed the
   200-call flush threshold once) -- would strengthen or weaken the
   `slots_us` lead above.
2. Investigate `slots_us`'s own real cost directly (source read of
   `midi_sched_tick()` / the OPL3 sink's real register-write path,
   per this hub's own "instrument the thing that produces the
   unexplained quantity" rule -- applied now to `slots_us`, the newly
   unexplained quantity, not `pump_us` again).
3. `wait_for_stable_screen()`'s low-fps false-positive fix -- still not
   made; this cell avoided it by using a short tick cap, not by fixing
   it. The full acceptance-gate ABBA (1000-tick workload, ~300s+
   sound-on cells) will hit it again otherwise.
4. Acceptance gate items 4 and 5 remain FAIL. This cell does not
   re-attempt them.

Patches 0059, 0060, and 0061 all stay landed, all still temporary.
