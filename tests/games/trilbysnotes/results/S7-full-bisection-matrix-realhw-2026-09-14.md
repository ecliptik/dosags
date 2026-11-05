# S7 -- full thread x DMA-activity bisection matrix, real hardware -- 2026-09-14

Continuation of `S7-opendevice-bisect-realhw-2026-09-14.md`. Six more
real-hardware cells complete the bisection this entry's predecessor
left half-done, and correct an overclaim from an earlier entry in this
same investigation. `binary_sha12=6ca3ac927604` throughout except
`OSAMID0` (see below, same binary, existing hint only).

## The corrected picture: two independent "boosters" over a real, unexplained floor

Testing phases 2 and 3 combined with `SDL_HINT_DOS_AUDIO_NO_BG_THREAD=1`
(`OSA2NT`, `OSA3NT`) and finishing phase 4 combined with the same
(`OSA4NT`) all landed at **`tick_rate=3.21-3.23`** -- identical to
`OSA1NT`. Neither DMA-controller arming (phase 2), IRQ-hooking (phase
3), nor DSP speaker-enable (phase 4) reintroduces any of the tax when
the background thread is absent and the DMA channel is never actually
told to start transferring. Only `NOBGT1`/`Arm D` (no thread, but the
device opened *normally* -- DMA genuinely autoinit-started, ~1948 real
IRQ fires) showed the full ~10x tax.

**This means the full real-hardware matrix, now complete, is**:

| | DMA never started | DMA genuinely autoinit-started |
|---|---:|---:|
| Thread present | 2.49-2.50 (`OSA1`,`OSA4`,`DMAX1`\*) | 2.49-2.97 (`AUDIOFX3`/`4`, `OSAMID0`) |
| Thread absent | **3.21-3.23** (`OSA1NT`-`OSA4NT`) | 2.48 (`NOBGT1`) |

(\*`DMAX1` force-paused *after* starting, not quite the same as never
starting, but structurally equivalent for IRQ purposes: 0 real fires.)

**Correction to `S7-irq7-lpt1-hypothesis-refuted-2026-09-14.md`**: that
entry concluded "the tax doesn't scale with IRQ activity at all,"
comparing `DMAX1` (thread present, 0 IRQ) against `NOBGT1` (thread
absent, ~1948 IRQ) and finding both near-identical. **That comparison
varies two axes at once (thread state AND DMA state) and its conclusion
does not hold up against the now-complete matrix.** The correct,
unconfounded reading:
- **Holding thread state at "present" constant** (`DMAX1` vs
  `AUDIOFX3`/`4`/`OSAMID0`): IRQ activity going from 0 to ~1638-2000
  genuinely has no effect (2.50 vs 2.96-2.97 -- if anything slightly
  *better* with real activity, consistent with the already-identified
  `WaitDevice`-timeout artifact explaining `DMAX1`'s own small excess,
  not a DMA-activity cost).
- **Holding thread state at "absent" constant** (`OSA1NT`-`OSA4NT` vs
  `NOBGT1`): IRQ activity going from 0 to ~1948 costs real, measurable
  degradation (3.21 -> 2.48, roughly halving `tick_rate`).
- **Net effect**: thread presence and real DMA/IRQ activity are each
  independently *sufficient* to reach the same ~10x ceiling, but
  neither is *necessary* on its own -- removing only one still leaves
  the other able to reach the same ceiling. Only removing *both*
  reveals a lower floor, and that floor is still ~5x above the fully-
  closed baseline, not 1x.

## The real, still-unexplained floor: ~5x tax from the device merely existing

Even in the best case found across eleven real-hardware cells now
(`OSA1NT`-`OSA4NT`, thread absent, DMA never started): `catchup_us`
mean, after excluding the one already-identified ~19.7-25s room-
transition outlier common to all of them, sits at ~1.0-1.07s per
33-burst average against a ~0.20s fully-fixed expectation -- **a real
~5x tax that survives the most minimal state this port's DOS backend
can reach.** This is not explained by anything ruled out so far
(`audio_core_entry_poll()` cost, register-write cost, yield-switch
volume, DMA transfer, thread existence, IRQ7/LPT1 sharing,
`SDL_UpdateAudio()`/RWLock cost -- see prior entries). It must come from
something that exists the moment `SDL_OpenAudioDevice()` succeeds at
all, independent of the DOS backend's own hardware-specific behavior.

## Dormant feature found: this port never enables the SB16 backend's own idle-auto-pause

`SDL_DOSAudioSetIdlePauseEnabled(bool)` (`SDL_dos_audio_synth.c:1971`)
is a real, already-built API -- when enabled, the IRQ handler
auto-pauses the DSP after `IDLE_PAUSE_THRESHOLD=4` consecutive
IRQs (~92ms at the design's 43Hz rate) find the software ring
underrun (nothing new queued since the last IRQ). **`grep`ing all of
`vendor/ags/` and `patches/ags/` for `SDL_DOSAudioSetIdlePauseEnabled`
returns nothing -- this port never calls it.** `g_dos_audio_idle_pause_
enabled` defaults `false` and stays that way for this port's entire
life. This explains why the SB16 DMA channel, once genuinely
autoinit-started, never voluntarily quiets down on its own even though
this specific workload's PCM ring content is always silence (Tier-2
SFX never fires in this scene -- only OPL3 MIDI plays, and MIDI doesn't
route through this ring at all): autoinit DMA is self-sustaining once
started (the ISR fills silence on underrun and keeps firing forever,
independent of any thread or explicit pump activity -- confirmed
directly by `NOBGT1`'s own ~1948 real IRQ fires with no thread ever
touching the device again after open). Enabling idle-pause would let a
silent scene like this one settle the DMA down after ~92ms -- **but
this needs its own correctness/regression review before turning on**
(it changes real playback behavior, not just a diagnostic), and doesn't
by itself explain the ~5x floor established above (that floor exists
even in `OSA1NT`-`OSA4NT`, where DMA never started in the first place).

## `SDL_HINT_DOS_MIDI_ISR_TICK=0` tested and refuted as relevant here

Ran the existing killswitch (`OSAMID0`, normal full open, thread
present, real DMA active, MIDI tick reverted to the engine's own
main-loop path instead of piggybacking on the SB16 IRQ) to test whether
the ISR's own per-fire MIDI-tick callback work contributes measurably.
**Result: `tick_rate=2.49`, identical to the unmodified baseline
(`AUDIOFX3`/`4`: 2.96-2.97, close enough given normal cell-to-cell
variance) -- no effect.** Consistent with idle-pause being dormant
regardless of this setting (there was nothing this killswitch could
unlock), and confirms the MIDI-ISR-tick callback's own per-IRQ cost is
not a meaningful contributor either.

## Where this leaves the investigation

**Twelve hypotheses/mechanisms now checked** (poll cost, poll
multiplier, register-write cost, yield-switch volume, DMA-cycle-
stealing as originally stated, audio-thread existence as a sole cause,
IRQ7/LPT1 sharing, `SDL_UpdateAudio()`/RWLock cost, MIDI-ISR-tick
cost) -- all refuted as the FULL explanation, though thread-presence
and DMA-activity are now understood as two independent, ceiling-
saturating boosters over a real, still-unexplained ~5x floor.

**Not yet found**: what causes the ~5x floor itself, present in the
single most minimal state (`OSA1NT`) this port's own code can reach --
this is now the single most important open question, since it is the
*only* thing present in literally every sound-on configuration tested,
including ones with no thread and no hardware activity whatsoever. The
next genuinely new, unexplored territory is SDL3's *generic* audio core
beyond `SDL_UpdateAudio()` (e.g. `SDL_CreateAudioStream`'s own
resampler/format-conversion setup, or whatever `SDL_OpenAudioDevice`
itself does at the generic-core level before ever calling into
`DOSSOUNDBLASTER_OpenDevice`), or possibly `SDL_InitSubSystem(SDL_
INIT_AUDIO)` itself as a once-per-process cost distinct from any
specific device -- neither audited yet.

Acceptance gate items 4 and 5 remain FAIL. Patches 0059-0064, 0141,
0143-0144 all stay landed, all still temporary.
