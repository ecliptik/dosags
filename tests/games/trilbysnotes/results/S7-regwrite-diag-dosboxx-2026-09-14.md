# S7 -- OPL3 register-write cost diagnostic, DOSBox-X validated -- 2026-09-14

Continuation of `S7-audioprb-fix-realhw-2026-09-14.md`'s "Not yet done"
item 2 (`slots_us`'s own real cost, source-read + instrumented) and the
hub's own "instrument the thing that produces the unexplained quantity,
not its neighbors" rule -- applied now to `slots_us` itself, since
`pump_us` already generalized from DOSBox-X to real hardware and
`slots_us` did not (1403us mean / 15270us max on HW-486-66 vs.
DOSBox-X's own 22-126us mean).

## Source read: why register I/O is a real candidate, not a guess

`midi_sched_tick()` (`.sdl-dos-ports/shared/audio/midi_sched.c`) is pure
computation plus sink callbacks -- no I/O of its own. The actual OPL3
register I/O lives in `SDL_DOSOpl3WriteRegister()`
(`vendor/SDL/src/core/dos/SDL_dos_audio_synth.c`): every register write
is bracketed by two loops of 6 dummy `inportb(0x388)` reads each (12
total), a canonical AdLib/OPL timing technique, with a comment claiming
"~1 us per read... well past the requirement, bullet-proof on PODP83 +
Cirrus 5434." A single `sink_note_on()` (`opl3_sink.c`) issues 13
register writes (`SDL_DOSOpl3VoiceWritePatch` = 11, `..VoiceNoteOn` = 2)
-- 156 dummy reads alone, before counting the address/data writes
themselves.

Two independent facts make that "~1us per read, bullet-proof" comment
worth doubting rather than trusting on this specific rig:

1. **HW-486-66's sound device is a PicoGUS in OPL3 mode** (confirmed
   elsewhere in this port's own history -- `PLAN.md`'s S1/S5 sections,
   `docs/audio.md`'s GUS/PicoGUS section) -- an RP2040-firmware ISA-bus
   emulation, not discrete YMF262 silicon. The 12-dummy-read delay was
   sized against a real chip's datasheet timing; nothing in this hub's
   history has ever independently measured what a single `inportb(0x388)`
   read actually costs against a PicoGUS's own firmware response latency.
2. **This exact file already has one confirmed precedent** of a similarly
   naive per-`inportb` timing assumption being wrong enough to matter on
   real hardware: `SDL_DOSMpu401WaitDRR()`'s own comment (SDL/0093)
   describes a real ISA IOCHRDY bus wait-state that made a status-port
   `inportb()` **hard-stall the CPU mid-instruction** on the WaveBlaster
   path when the target chip was absent -- severe enough that the fix was
   "never issue the read," not "wait longer." The OPL3 write path issues
   12 such reads per register write, unconditionally, with no comparable
   escape hatch.

This is not proof, but it is a real, source-grounded, falsifiable
hypothesis: **on real hardware, `SDL_DOSOpl3WriteRegister()`'s own
per-call cost (dominated by the dummy-read delay loop) may be the actual
driver of `slots_us`, not scheduling logic (event-list traversal, voice
allocation bookkeeping) in `midi_sched_tick()`/`opl3_sink.c`.**

## Instrumentation (SDL/0141 + ags/0062, both temporary)

`SDL/0141` (`patches/SDL/`) brackets `SDL_DOSOpl3WriteRegister()` itself
with `uclock()`-based microsecond timestamps, in-memory accumulate only
(no I/O in that function), exposed via a snapshot-and-reset accessor
`SDL_DOSOpl3RegWriteDiagSnapshot()`. `ags/0062` (`patches/ags/`) calls
that accessor once per `audio_core_entry_poll()` invocation -- right
after the slot loop -- and folds the result into the existing
`AudioPollWindow`/`AudioPollDiag` structures (0059/0061) as a new
`regwrite(calls=.. min_us=.. mean_us=.. max_us=..)` field on the same
`DOS-PORT audioprb` log line, through the same already-open
`quit.cpp`-owned handle. No new log, no new file I/O anywhere.

Both patches land in this port's own `patches/SDL/` and `patches/ags/`
(per the 2026-09-01 per-port-vendoring migration -- `patches/SDL/` is a
real, standalone series now, not a hub-synced one; see
`.sdl-dos-ports/docs/patch-conventions.md`), not the hub's
`shared/patches/sdl3-dos/` reference library. If this investigation
concludes with a real, generalizable finding about OPL3 register-write
timing, relaying it back to the hub is a separate, deliberate act (same
doc, "When a port discovers a shared/-relevant fix").

## DOSBox-X validation: a real bug caught and fixed before real hardware

First run (`dosbox-run.sh`, scratch `oplmode=opl3` fast conf, Trilby's
Notes, `DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`,
`SDL_HINT_DOS_AUDIO_BACKEND=opl3`) produced:

```
DOS-PORT audioprb total_calls=180 windows_recorded=1 windows_dropped=0
DOS-PORT audioprb total_calls=180 window_calls=180 slots_us(min=2 mean=35 max=4807) pump_us(min=35 mean=10727 max=16054) regwrite(calls=236 min_us=7 mean_us=254 max_us=54950)
```

`regwrite max_us=54950` **exceeds that same window's own `slots_us`
max=4807** -- structurally impossible if register-write time is truly a
subset of the slot-loop time it sits inside. Root cause, found by reading
the call graph: `SDL_DOSOpl3WriteRegister()` is also called from OUTSIDE
`audio_core_entry_poll()` entirely -- `audio_core_slot_init_midi()`
(triggered by the engine's own music dispatch, not this poll loop)
constructs the MIDI `AudioPlayer`, whose constructor calls
`dos_midi_backend_open()` -> `opl3_sink_open()` -> `SDL_DOSOpl3InitChip()`,
which alone issues dozens of register writes (silencing 18 voices,
enabling OPL3 mode, etc.). Those writes sat in the SDL-side accumulator
until whichever `audio_core_entry_poll()` call happened to run next,
which then reported them as if they were part of its own slot loop --
misattribution, not a real slots_us/regwrite disagreement.

Fixed with a discard-snapshot: `audio_core_entry_poll()` now calls
`SDL_DOSOpl3RegWriteDiagSnapshot()` once (discarding the result) right at
entry, before the slot loop, so anything that accumulated between calls
from an unrelated code path is flushed out rather than misattributed to
the next call. Second run, same recipe:

```
DOS-PORT audioprb total_calls=188 windows_recorded=1 windows_dropped=0
DOS-PORT audioprb total_calls=188 window_calls=188 slots_us(min=2 mean=34 max=4797) pump_us(min=36 mean=10656 max=15965) regwrite(calls=210 min_us=11 mean_us=23 max_us=23)
```

Internally consistent this time: `regwrite max_us=23` is comfortably
under `slots_us max=4797`, and the numbers cross-check --
210 writes / 188 calls =~ 1.12 writes/call average, at ~21-23us/write
=~ 23-26us/call of register-write time, close to `slots_us`'s own
mean=34us (leaving a small remainder for scheduling logic + the many
calls with zero due events, which cost near-nothing). In DOSBox-X,
register I/O is cheap and accounts for most of `slots_us`'s own small
cost -- consistent with the *original* DOSBox-X measurement
(`S7-fix-dosbox-x-2026-09-14.md`: 22-126us mean for the whole slot loop).
This only establishes the new diagnostic is wired correctly and produces
a sane, self-consistent shape of data locally -- per this hub's own
DOSBox-X-is-a-correctness-gate-not-a-performance-proxy rule, it says
nothing about whether register I/O is what makes `slots_us` expensive on
**real** hardware. DOSBox-X already proved unreliable for that exact
question once already in this investigation (`slots_us` itself was the
generalization failure this diagnostic exists to explain).

## Not yet done

1. **A real HW-486-66 cell** is required to actually test the hypothesis:
   does `regwrite` account for most of `slots_us` on real hardware (as it
   does in DOSBox-X), or does real hardware show a large *scheduling-logic*
   remainder instead (which would point away from register I/O and back
   toward `midi_sched_tick()`/`opl3_sink.c`'s own bookkeeping)? Needs a
   fresh, separately-asked operator go-ahead -- not taken this session.
2. If `regwrite` does dominate on real hardware, the next falsifiable
   step is bisecting the 12-dummy-read assumption itself (e.g. a
   hint-gated reduced read count, A/B'd against audible/functional
   correctness -- a PicoGUS's actual minimum requirement is unknown, and
   cutting it wrong risks corrupted OPL3 register state, not just a
   performance regression, so this needs real correctness verification,
   not just a timing measurement).
3. `wait_for_stable_screen()`'s low-fps false-positive fix -- still open,
   unrelated to this diagnostic, will bite the next full acceptance-gate
   ABBA exactly as before.
4. Acceptance gate items 4 and 5 remain FAIL. This diagnostic addition
   does not re-attempt them.

Patches 0059, 0060, 0061 (ags), and now SDL/0141 + ags/0062 all stay
landed, all still temporary.
