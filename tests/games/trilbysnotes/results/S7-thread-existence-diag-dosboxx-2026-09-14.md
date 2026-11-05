# S7 -- audio-thread-existence hypothesis: design + patch + DOSBox-X validated -- 2026-09-14

Continuation of `S7-dma-cyclesteal-realhw-2026-09-14.md`'s "Not yet
done" item 1: with active DMA transfer refuted as the cause of the
~9.7x-11.8x uniform per-`UpdateGameOnce()` tax, what remains standing is
that the tax tracks the SB16 audio device merely being *open* -- i.e.
the autonomous `PlaybackAudioThread` (SDL3's own stock thread, created
unconditionally at `OpenDevice`) existing in the DOS cooperative
scheduler's thread table, independent of what it actually does. This
entry designs and lands a real, narrow patch that tests that directly,
then validates it under DOSBox-X. Real hardware not yet used.

## The mechanism (SDL3 stock, not invented for this)

`vendor/SDL/src/audio/SDL_audio.c:1879`:

```c
if (!current_audio.impl.ProvidesOwnCallbackThread) {
    device->thread = SDL_CreateThread(..., PlaybackAudioThread, ...);
}
```

`ProvidesOwnCallbackThread` is a first-class field on `SDL_AudioDriverImpl`
(`SDL_sysaudio.h:167`). Setting it true for the DOS SB backend makes the
generic core skip `SDL_CreateThread()` for that device entirely --
`device->thread` stays `NULL`. The matching shutdown path (`SDL_audio.c`:
`if (device->thread) { SDL_WaitThread(...); }`) already treats a NULL
thread as a no-op, so `DOSSOUNDBLASTER_CloseDevice()` needs no matching
change -- this is a real, pre-existing, generically-supported SDL3 code
path, not something built from scratch for this experiment.

**Why this composes cleanly with what's already landed**: `SDL_DOSAudioPump()`
(patch 0067, already wired into `audio_core_entry_poll()` every real
tick) calls `SDL_PlaybackAudioThreadIterate(device)` directly -- the same
function the background thread's own loop calls -- and critically never
calls `WaitDevice()` itself (only the background thread's own
`while(Iterate()){WaitDevice();}` loop does). So in no-thread mode,
`WaitDevice()` -- and every `DOS_Yield()`/hard-park/quiescence-gate
mechanism living inside it -- simply never runs. Not a new path needing
verification; an absent one.

## Patch (`patches/SDL/0143-audio-thread-existence-diagnostic.patch`)

`SDL_HINT_DOS_AUDIO_NO_BG_THREAD=1`, resolved at `DOSSOUNDBLASTER_Init()`
(must be there, not `OpenDevice`, since SDL3's generic core reads
`impl->ProvidesOwnCallbackThread` before `DOSSOUNDBLASTER_OpenDevice`
ever runs), sets `impl->ProvidesOwnCallbackThread = true` and a module
static (`g_dos_audio_no_bg_thread`) used only for a confirmation banner
at `OpenDevice` (a point already proven safe for `dos_port_dbg_log`, same
as patch 0040's own force-pause banner). Strict-1 env-var match, default
OFF preserves current behavior bit-identical. Diagnostic only -- expect
underruns/silence between explicit pump calls, same framing as
`SDL_HINT_DOS_AUDIO_FORCE_DSP_PAUSE`.

Landed as a real commit in `vendor/SDL`'s own nested repo
(`6329f4c78`), exported via `git format-patch`, and reapplied through
the normal series (`make patches` -- "SDL: patch series applied
cleanly", new series fingerprint `b3fe46990c5a`). `make sdl3 && make
build-ags` rebuilt cleanly; `binary_sha12` changed from `7d2309fcdef7`
(the AUDIOFX3/4/DMAX1 binary) to `36ebdca8ee61`, confirming the tree
genuinely changed.

## DOSBox-X validation

Two same-scenario runs (`dosbox-run.sh --fast`, scratch `oplmode=opl3`
conf reverted after, Trilby's Notes, scratch `ACSETUP.CFG`, `opl3bank.dat`
included, `DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`,
`SDL_HINT_DOS_AUDIO_BACKEND=opl3`), differing only in whether
`SDL_HINT_DOS_AUDIO_NO_BG_THREAD=1` is set:

| | Baseline (thread present) | Arm D (`NO_BG_THREAD=1`) |
|---|---:|---:|
| tick_rate | 30.63 | 30.82 |
| catchup_yield switches | 4 | **0** |
| realtick_yield switches | 3938 | **0** |
| pump_us mean | 11649 | 10258 |
| slots_us mean | 33 | 36 |
| regwrite calls/mean_us | 210 / 21 | 210 / 21 |
| audio_vital_status | events=54, voices=8, underruns=0 | events=54, voices=8, underruns=0 |
| IRQ-5 fires (CloseDevice tally) | 0 | 0 |

**A structural, mechanistic confirmation the patch does exactly what it
claims**: yield-switch counts drop from 4/3938 to exactly 0/0. This is
not a tuning effect -- with no second thread ever created, there is
nothing for `main` to switch to, so every `DOS_Yield()` (if any still
fire) becomes a guaranteed no-op. Everything else -- OPL3 dispatch
(`events=54` both), `audio_core_entry_poll()`'s own cost profile
(`slots_us`/`regwrite` near-identical), `tick_rate` -- stays in the same
range between the two arms, confirming the isolation is clean: thread
existence is the only thing that changed.

**Both arms show zero IRQ-5 fires, including the thread-present
baseline** -- checked specifically because Arm D's own zero-IRQ result
would otherwise look alarming (did the patch break DMA arming?). It
didn't: this short (~8-9s), quiet DOSBox-X smoke scenario (boot to
title, one room transition, OPL3 music only -- no `Playing sound`
cues appear in either run's STDOUT) never drives the SB16 PCM ring hard
enough to avoid this backend's own always-on idle-auto-pause (SDL/0038,
unrelated to `FORCE_DSP_PAUSE`) under DOSBox-X's emulation, *regardless*
of whether the background thread exists. Confirmed by running the exact
same scenario with the hint unset first -- not assumed. **Caveat for the
real-hardware cell**: if the real cell's Arm-D run shows zero IRQ fires
while a fresh real-hardware baseline (same scenario, thread present)
shows nonzero, that WOULD be a genuine new finding (the no-thread mode
breaking the idle-auto-pause's resume path, since that path's "Part 1"
resume-origination lives inside `WaitDevice()`, which never runs without
the thread) -- read both cells' own IRQ tallies, don't assume DOSBox-X's
"both zero" result generalizes.

No crash, no hang, clean shutdown in both runs.

## Not yet done

1. **The real-hardware cell** -- needs a fresh, separately-asked operator
   go-ahead. Recipe: `run-rig.sh trilbysnotes --tag <TAG> --env
   DOSAGS_FIXED_TIMESTEP=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=200 --env
   SDL_HINT_DOS_AUDIO_BACKEND=opl3 --env SDL_HINT_DOS_AUDIO_NO_BG_
   THREAD=1 --extra-file ACSETUP.CFG:ACSETUP.CFG` -- new binary
   (`binary_sha12=36ebdca8ee61`), needs re-staging (not the same exe as
   `AUDIOFX3`/`4`/`DMAX1`).
2. Per the caveat above, also worth a fresh real-hardware baseline cell
   at this same binary_sha12 (thread present, no new hint) if the
   `AUDIOFX3`/`4` real-hardware IRQ tally was never actually checked --
   it wasn't, this investigation only started reading that specific log
   line this session (`S7-dma-cyclesteal-realhw-2026-09-14.md`). Confirm
   before trusting an Arm-D real-hardware IRQ count in isolation.
3. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0064, 0141-0143 all stay landed, all still temporary.
