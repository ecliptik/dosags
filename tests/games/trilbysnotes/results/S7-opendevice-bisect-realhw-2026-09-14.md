# S7 -- OpenDevice bisection, real-hardware results: partial recovery found -- 2026-09-14

Continuation of `S7-opendevice-bisect-dosboxx-2026-09-14.md`. Three
operator-approved real-hardware cells on HW-486-66, same recipe as
every prior cell in this series (`run-rig.sh trilbysnotes --env
DOSAGS_FIXED_TIMESTEP=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=200 --env
SDL_HINT_DOS_AUDIO_BACKEND=opl3 --extra-file ACSETUP.CFG:ACSETUP.CFG`
plus the phase-specific hint(s) below). `binary_sha12=6ca3ac927604`
(the SDL/0144 build) throughout.

## Results

| Tag | Config | tick_rate | catchup_yield sw | realtick_yield sw |
|---|---|---:|---:|---:|
| `OSA4` | `OPEN_STOP_AT=4` (thread present) | 2.49 | 2 | 640 |
| `OSA1` | `OPEN_STOP_AT=1` (thread present) | 2.49 | 2 | 684 |
| `OSA1NT` | `OPEN_STOP_AT=1` + `NO_BG_THREAD=1` | **3.21** | **0** | **0** |

## Phases 4 and 1 (thread still present): no new information, but a clean internal-consistency check

Neither `OSA4` (stop just before autoinit playback starts) nor `OSA1`
(stop before the DMA controller is touched at all -- the most minimal
hardware state short of not opening the device) breaks the ~9.7x-11.8x
collapse: both land at `tick_rate=2.49`, indistinguishable from every
other sound-on arm tested so far (`DMAX1`=2.50, `AUDIOFX3`/`4`=2.96-2.97,
`NOBGT1`=2.48). **Realization mid-investigation**: neither of these two
phases disables the background `PlaybackAudioThread` (`SDL_HINT_DOS_
AUDIO_NO_BG_THREAD` is a separate, uncombined hint) -- so in both, the
thread still exists and runs its own `Iterate()`/`WaitDevice()` loop
against the ring buffer relocated earlier in patch 0144. Since nothing
ever drains that ring (DMA never starts in any of the four phases), the
thread hits the exact same permanently-full-ring/`WaitDevice`-1-second-
timeout dance already characterized for Arm B -- confirmed directly by
the yield signature: `OSA4`'s `catchup_yield mean_us` (not shown above,
see raw log) matches Arm B's own `950138` almost exactly. This means
phases 1-4 (thread present) were never actually isolating "how much
hardware setup happened" cleanly from "is the background thread busy
cycling" -- both axes were still present in all four. Not a wasted
result (it independently reproduces the tax at the most minimal
hardware-touch level reachable with the thread present, `OSA1` being
the cleanest version of that), but it doesn't narrow the search further
on its own.

## `OSA1NT`: the combined test, and the first real deviation from the pack

Combining `OPEN_STOP_AT=1` with `NO_BG_THREAD=1` -- no DMA controller
touch, no IRQ hook, no DSP command beyond the mandatory reset, AND no
background thread at all -- produces `tick_rate=3.21`, **the first
result in this entire investigation to land outside the tight
2.48-2.97 cluster every other sound-on arm has occupied.** `catchup_
yield`/`realtick_yield` are both exactly 0 (mechanistically confirmed:
nothing to yield to, matching `NOBGT1`'s own signature).

**But the underlying data shape changed too, not just the aggregate
number**: `catchup_us(min=16 mean=1747174 max=25062476)` -- a huge
spread (16 microseconds to 25 *seconds*) that no other arm showed (every
other arm's `catchup_us` min/max sat within a much narrower band, all
uniformly slow). Cross-checked against `STDOUT.TXT`: `Game : (room:1)
DOS-PORT room_transition t_ms=19673` -- a **19.673-second room
transition**, matching the `catchup_us` max almost exactly. This is the
same pre-existing, audio-unrelated stall flagged as a possible
confound as far back as `S7-tickfix-diag-dosboxx-2026-09-14.md`'s own
"max outlier" discussion (a one-time room/asset-load cost this hardware
tier pays regardless of audio state) -- not something this diagnostic
introduced.

**Quantifying how much is that one outlier vs. genuine remaining tax**:
removing the single 25.06s-outlier burst from the 34-burst total
(59.40s) leaves 34.34s across the other 33 bursts, averaging ~1.04s/
burst -- against a fully-fixed expectation of ~0.20s/burst (baseline's
~42ms/tick x ~4.85 catchup ticks/burst). **The tax is reduced by this
combination (from ~9.7x-11.8x down to roughly ~5x against baseline) but
is not eliminated.** This is real, measurable progress -- the first
combination in nine tested (Arms A-D, the IRQ7 hypothesis, phases 1-4,
and this combined test) to move the needle at all -- but the core
mechanism survives even in the most minimal state reachable through
this port's own DOS SB backend: an `SDL_AudioDeviceID` that exists at
all, with nothing else touched and no background thread.

## Where this leaves the investigation

**Every hardware/scheduling axis this port's own DOS backend controls
has now been tried and either fully or partially ruled out**: DMA
activity (full refute), thread existence (full refute on its own), IRQ
hook/DMA-controller-programming/DSP-speaker-enable extent (full refute
at every phase with the thread present), and now the maximally-minimal
combination (thread absent + nothing touched) still shows roughly half
the original tax surviving. The remaining, still-unidentified mechanism
is not eliminated by anything this port's own `vendor/SDL/src/audio/
dos/SDL_dosaudio_sb.c` controls at OpenDevice time.

**New leading candidate for a future session**: SDL3's own *generic*
(platform-independent) audio core, not the DOS backend. `SDL_PumpEvents()`
-> `SDL_PumpEventMaintenance()` -> `SDL_UpdateAudio()`
(`vendor/SDL/src/audio/SDL_audio.c`) runs on **every** `sys_evt_process_
pending()` call -- i.e. every single `UpdateGameOnce()`, catch-up ticks
included, matching this investigation's oldest structural clue exactly
-- gated only by the `SDL_AUDIO_DISABLED` *compile-time* flag, not any
runtime "is a device actually doing anything" check. Read so far:
`SDL_UpdateAudio()` itself looks cheap (an RWLock-for-reading check that
early-exits when no pending device events are queued), so it is not
yet a confirmed mechanism -- but it is the first genuinely new, untried
code path in this whole investigation (SDL3's *generic* core, never
audited before now; everything ruled out so far was either the DOS
backend specifically or the AGS engine layer). Not yet instrumented or
measured. The residual ~1.04s/burst tax found in `OSA1NT` needs its own
explanation too, independent of whatever the original full-tax
mechanism turns out to be.

## `SDL_UpdateAudio()` / RWLock-cost checked and refuted (source read, no hardware)

Read `SDL_LockRWLockForReading_generic()` (`vendor/SDL/src/thread/
generic/SDL_sysrwlock.c`, the only RWLock implementation DOS builds
against -- no DOS-specific override exists) and DOS's own `SDL_LockMutex()`
(`vendor/SDL/src/thread/dos/SDL_sysmutex.c`). The RWLock's read-lock path
is `SDL_LockMutex` + `SDL_AddAtomicInt` + `SDL_UnlockMutex`; DOS's mutex
fast (uncontended) path is `DOS_DisableInterrupts()` / owner check /
`DOS_EnableInterrupts()` -- a handful of instructions, no `DOS_Yield()`
unless genuinely contended (confirmed: contention is the only branch
that yields). `SDL_UpdateAudio()`'s own common-case cost (no pending
device events queued, true in every cell this investigation has run) is
one such cheap read-lock plus an early-exit pointer check. **This
refutes `SDL_UpdateAudio()`/RWLock cost as the mechanism** -- a
few-instruction, CLI/STI-protected operation cannot explain a
per-tick cost in the hundreds of milliseconds, called once per tick or
a thousand times per tick alike. The candidate named in this entry's
own "not yet done" is dead; still true that `SDL_PumpEvents()` ->
`SDL_UpdateAudio()` is a genuinely new, never-before-audited code path
compared to everything else ruled out, but this specific mechanism
within it is not it.

## Not yet done

1. `SDL_UpdateAudio()`/RWLock cost is refuted (above) -- the search for
   a mechanism in SDL3's generic (non-DOS) audio core continues, but
   not via this specific function. Other generic-core candidates
   (`SDL_CreateAudioStream`'s own resampler/mixer setup, format-
   negotiation code reachable from a periodic re-check) not yet
   audited.
2. Explain the residual ~5x tax `OSA1NT` still shows, independent of
   the one identified room-transition outlier.
3. Whether `SDL_INIT_AUDIO` subsystem-level initialization itself
   (distinct from any specific device open -- this investigation's own
   `OPEN_STOP_AT` bisection only varies what `DOSSOUNDBLASTER_
   OpenDevice()` does, never whether `SDL_InitSubSystem(SDL_INIT_AUDIO)`
   runs at all) is a genuinely untested axis -- not yet designed.
4. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0064, 0141, 0143-0144 all stay landed, all still
temporary.
