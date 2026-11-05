# S7 -- DMA-cycle-stealing experiment design + DOSBox-X validation -- 2026-09-14

Continuation of `S7-yield-diag-realhw-2026-09-14.md`'s leading, untested
hypothesis: real ISA-bus DMA cycle-stealing from the actively-streaming
SB16 PCM channel, not software scheduling, causes the ~9.7x uniform
per-`UpdateGameOnce()` tax. This cannot be confirmed or refuted by more
source reading or by DOSBox-X (no bus-contention model) -- it needs a
real-hardware experiment. This entry designs that experiment and
validates the new config under DOSBox-X first, per this investigation's
own established discipline. No new patch, no real hardware used this
entry.

## A real correction to this investigation's own "IRQ-5" shorthand

Every write-up in this series (including this one's own source reading)
has used "IRQ-5" as a generic stand-in, copied from the SDL backend's own
comments (which describe a typical/default SB16 config, not this rig's
actual jumpers). **HW-486-66's actual audio device for this workload is
a PicoGUS physically jumpered to IRQ 7 / DMA 3**, run in its SB-emulation
firmware mode with `SDL_HINT_DOS_AUDIO_SB_FORCE_8BIT=1` (the `PGSB` boot
profile: `BLASTER=A220 I7 D3 P330 T3`, `PGUSINIT /mode sb` + `/sbenv` --
see `~/git/g2k/README.TXT`'s PGSB section). That means the real cell this
investigation has been running is the **8-bit DMA path** (`T3` = SB
2.0-class, matching the forced-8-bit hint), not the 16-bit path DOSBox-X's
own `[sblaster]` conf (`irq=5 dma=1 hdma=5`, SB16-class) emulates. The
pause command the real cell will issue is therefore `0xD0` (8-bit pause),
not `0xD5` -- confirmed by reading `MaybeServiceIdlePauseRequests()`'s own
`soundblaster_is_sb16 ? 0xD5 : 0xD0` branch. This doesn't change any
conclusion reached so far (the diagnostic code reads the actual configured
IRQ/DMA at runtime, not a hardcoded 5), but every real-hardware log line
this investigation reads from here on should say `irq=7`/8-bit DMA, and
"IRQ-5" in this doc and its predecessors should be read as shorthand for
"the SB IRQ," not literally interrupt 5. Also newly relevant to the
DMA-cycle-stealing hypothesis itself: a PicoGUS is an RP2040-firmware ISA
card, not fixed silicon -- a firmware/PIO-driven device responding to
real-time ISA bus cycles is a structurally more plausible source of
bus-cycle wait-states than a discrete ASIC SB16 would be, which makes the
hypothesis somewhat more physically plausible going into the experiment,
not less. Still unconfirmed; the experiment below is unchanged by this.

## The experiment

Same fixed-timestep/tickfx/audioprb/yield instrumentation already landed
(patches 0059-0064, unconditional, no new hint needed), same binary
(`binary_sha12=7d2309fcdef7`, unchanged from `AUDIOFX3`/`AUDIOFX4` --
this is a config-only experiment, not a new patch). Three arms:

- **Arm A** (existing baseline, `S7-abba-2026-09-13.md`): sound-off.
  `tick_rate~23.8-23.9`, ~42ms/`UpdateGameOnce()`.
- **Arm B** (new, this entry): `SDL_HINT_DOS_AUDIO_BACKEND=opl3` +
  `SDL_HINT_DOS_AUDIO_FORCE_DSP_PAUSE=1`. OPL3 MIDI stays live (a
  separate register-I/O path, unaffected by the SB PCM device's own
  DMA state); the SB PCM device opens but its DMA channel is
  force-paused immediately and never auto-resumed.
- **Arm C** (existing baseline, `S7-tickfix-diag-realhw-2026-09-14.md`/
  `S7-yield-diag-realhw-2026-09-14.md`): sound-on (OPL3), full DMA
  streaming. `tick_rate~2.96-2.97`, ~407-409ms/`UpdateGameOnce()`.

If Arm B tracks Arm A: confirms DMA-cycle-stealing (the tax needs active
DMA transfer, not just an open device or active MIDI). If Arm B tracks
Arm C: refutes it (something else -- device-open state, IRQ armed but
not firing, or an unconsidered mechanism).

## A real interaction found by reading the source, not assumed

Patch 0040's own comment claims force-pause makes "IRQ-5 stop firing" --
true, confirmed below -- but reading `DOSSOUNDBLASTER_WaitDevice()`
(`SDL_dosaudio_sb.c`) found a real, previously-uncombined interaction
with patch 0063 (landed later, for an unrelated DX2 quit-hang fix):
`WaitDevice`'s ring-full spin loop's wall-clock backstop
(`DOS_AUDIO_WAITDEVICE_TIMEOUT_NS = 1000ms`) is **not gated on
`g_dos_audio_force_dsp_pause`** -- only the auto-resume request (Part 1)
is. Once force-paused, the PCM ring fills permanently (nothing drains
it), so every ~1s of real time the timeout fires and `WaitDevice()`
returns `true` anyway, letting `Iterate()`/`PlayDevice()` run again even
though DMA is halted. This is a real, structural difference from
force-pause's pre-0063 behavior (which likely blocked in `WaitDevice()`
indefinitely) and a real risk of reintroducing scheduler churn as a
confound distinct from DMA-cycle-stealing -- exactly the kind of
"doesn't compose cleanly" case worth checking before trusting the result,
not assuming patch 0040's comment still holds verbatim.

## DOSBox-X validation

`dosbox-run.sh --fast`, scratch `oplmode=opl3` conf (reverted after this
run -- never committed), Trilby's Notes (`tests/harness/games/
trilbysnotes/NOTES.ags`), a scratch `ACSETUP.CFG` (`[sound]\nenabled=1`,
not game data), `.sdl-dos-ports/shared/audio/opl3bank.dat` included,
`--args "--test --log-stdout=+mgs:all --user-data-dir c:\\"`,
`DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`,
`SDL_HINT_DOS_AUDIO_BACKEND=opl3`, `SDL_HINT_DOS_AUDIO_FORCE_DSP_PAUSE=1`.
Binary unchanged (`build-sha12` confirmed `7d2309fcdef7` against the
committed tree before running -- same binary as `AUDIOFX3`/`AUDIOFX4`).

```
[RUNMANIFEST-BEGIN]
binary_sha12=7d2309fcdef7
duration_s=9
exit_code=0
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=54
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=32.26 frames_skipped=52
DOS-PORT audioprb total_calls=180 window_calls=180 slots_us(min=2 mean=35 max=4718) pump_us(min=35 mean=11264 max=15971) regwrite(calls=210 min_us=4 mean_us=21 max_us=23)
DOS-PORT tickfx total_calls=148 window_calls=148 catchup_n_sum=52 catchup_us(min=2 mean=14914 max=2180648) realtick_us(min=288 mean=34701 max=604823) catchup_yield(switches=4 min_us=16 mean_us=4244 max_us=14929) realtick_yield(switches=3558 min_us=9 mean_us=1503 max_us=218568)
```

SDL debug log (`LOGS/SDLDBG.LOG`) confirms the mechanism directly, not
just the aggregate numbers:

```
audio: DSP forcefully paused via SDL_HINT_DOS_AUDIO_FORCE_DSP_PAUSE=1; ...
audio: SDL/0073 rate-meas: irqs=0 elapsed_ms=3614 irq_hz=0 hw_frame_rate=0
audio: SDL/0106 CloseDevice: total IRQ-5 fires this run = 0 (0 == DMA-IRQ never armed; the pumps never ran)
```

## Verdict: composes cleanly, no fix needed before real hardware

1. **IRQ genuinely stops**: 0 fires for the entire run (both the live
   rate-meas line and the CloseDevice tally agree). DMA is not
   transferring, confirmed directly, not assumed from the hint's own
   comment.
2. **OPL3 MIDI dispatch is unaffected**: `events=54` (real dispatch, not
   idle), `regwrite(calls=210 mean_us=21 max_us=23)` -- essentially
   identical to the non-force-paused OPL3 DOSBox-X baseline
   (`S7-regwrite-diag-dosboxx-2026-09-14.md`'s second run:
   `regwrite(calls=210 mean_us=23 max_us=23)`). The two audio paths are
   confirmed independent, not just assumed so from the source read.
3. **The WaitDevice-timeout interaction found above does not visibly
   manifest as pathological churn here**: `catchup_yield`/`realtick_yield`
   switch counts (4 / 3558) are essentially the same shape as the
   non-force-paused OPL3 DOSBox-X yield baseline
   (`S7-yield-diag-dosboxx-2026-09-14.md`: 4 / 3766), and `tick_rate`
   (32.26) sits in the same range as that baseline (30.58) and the
   `--fast`-conf sound-on baseline from `S7-fix-dosbox-x-2026-09-14.md`
   (~37). No runaway busy-loop, no crash, no hang, clean shutdown.
   **Caveat, stated plainly**: this is DOSBox-X's `--fast` conf, which
   keeps up with the 40Hz target well enough that main yields often --
   the real risk from the timeout interaction (a thread that yields
   rarely, so the audio thread's own WaitDevice call sits mid-loop for a
   long real-wall-clock stretch before its 1s backstop fires) is specific
   to real hardware's chronic-backlog regime, which this conf does not
   reproduce. This DOSBox-X result establishes the config is wired
   correctly and doesn't misbehave in an environment that keeps up with
   target -- it does NOT clear the real-hardware cell of this risk by
   itself. The real cell's own yield diagnostic (already instrumented,
   no new patch needed) is what actually answers it: if Arm B's real
   `catchup_yield`/`realtick_yield` switch counts come back far higher
   than Arm C's near-zero/~2-switch catch-up result
   (`S7-yield-diag-realhw-2026-09-14.md`), that is itself informative
   (a confound from this interaction, not from DMA), and should be read
   and reported alongside `catchup_us`/`realtick_us`, not skipped.

**No source fix needed** -- this is a real config-only experiment on the
existing binary, per the handoff's own instruction.

## Not yet done

1. **The real-hardware cell** -- the actual DMA-cycle-stealing question
   can only be answered on HW-486-66. Needs a fresh, separately-asked
   operator go-ahead; not taken this entry. Recipe: `run-rig.sh
   trilbysnotes --tag <TAG> --env DOSAGS_FIXED_TIMESTEP=1 --env
   DOSAGS_TAS_AUTO_EXIT_TICK=200 --env SDL_HINT_DOS_AUDIO_BACKEND=opl3
   --env SDL_HINT_DOS_AUDIO_FORCE_DSP_PAUSE=1 --extra-file
   ACSETUP.CFG:ACSETUP.CFG` (same recipe as `AUDIOFX1`-`4`, PicoGUS/PGSB
   boot profile already the rig default -- no `--boot-profile` override
   needed).
2. When reading that cell's result: check `irq=7` (not 5) and the
   `0xD0` (not `0xD5`) pause command in the tag's own SDL debug log to
   confirm the 8-bit PGSB path paused correctly on the real device, and
   read `catchup_yield`/`realtick_yield` alongside `catchup_us`/
   `realtick_us` for the WaitDevice-timeout-interaction caveat above.

Acceptance gate items 4 and 5 remain FAIL.
