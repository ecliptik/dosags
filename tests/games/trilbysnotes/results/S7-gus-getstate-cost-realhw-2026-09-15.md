# S7-GUS -- SDL_DOSGusGetState() per-call cost, real-hardware result: exonerated, and a course correction -- 2026-09-15 (new session)

Operator-approved cell (tag `GUSD1`, `binary_sha12=c6d6f6626df8`, the
patches SDL/0145 + ags/0069 build), HW-486-66, `PGGUS` boot profile
(manually driven -- see below), same recipe as `GUST1`.

## A second real harness gap, worked around the same proven way

`run-rig.sh --boot-profile 3` failed again in the same way as `GUST1`'s
own session (the underlying `select_boot_profile()` timing gap is still
unfixed, flagged not fixed per the prior entry's own plan). Also hit,
mid-session: the local `run-rig.sh` process was killed by the
environment itself ("system is running low on memory") right after the
`send-file --return` job started server-side -- confirmed via direct
`vc file-status` that the underlying transfer continued and completed
successfully despite the local process dying, matching this
investigation's own repeated finding that these jobs run independently
of the calling script. Recovered by polling `vc file-status` directly
(lightweight, no long-lived background process) instead of re-invoking
the full script. The same manual LED-polling boot-profile protocol from
`GUST1` (reboot, poll `vc leds` for the real capslock edge, fire
`3`+`enter` immediately, poll for RDYPULSE) worked cleanly again,
first attempt.

## Result

```
[RUNMANIFEST-BEGIN]
binary_sha12=c6d6f6626df8
duration_s=28
exit_code=0
audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=76
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=9.36 frames_skipped=164
DOS-PORT audioprb total_calls=68 window_calls=68 slots_us(min=24 mean=101489 max=6890385) pump_us(min=24 mean=26 max=42) regwrite(calls=0 min_us=0 mean_us=0 max_us=0) gusscan(calls=28 min_us=27 mean_us=109 max_us=170)
DOS-PORT tickfx total_calls=37 window_calls=37 catchup_n_sum=164 catchup_us(min=16 mean=162603 max=4025078) realtick_us(min=5567 mean=367026 max=7031353) catchup_yield(switches=0 min_us=0 mean_us=0 max_us=0) realtick_yield(switches=0 min_us=0 mean_us=0 max_us=0)
```

`tick_rate=9.36` matches `GUST1`'s own 9.39 closely (a second, near-
identical confirmation of that number). `STDOUT.TXT` confirms
`room_transition t_ms=12808` (close to but not identical to `GUST1`'s
own 13028 -- consistent with genuine environmental jitter in real disk
I/O timing for room/asset loading).

## Verdict: `SDL_DOSGusGetState()` is completely exonerated -- and the prior handoff's own fix idea was based on an unverified assumption

**`gusscan(calls=28 min_us=27 mean_us=109 max_us=170)`** -- only 28
calls for the entire 28-second run, each individually cheap (27-170us,
exactly matching the source-reading prediction that a bounded O(busy
voices) register-read loop should cost microseconds). Total cost across
all 28 calls: ~3ms. **This cannot explain any part of `slots_us`'s own
101ms mean or 6.9s max** -- `reap_finished_voices()`'s hardware scan is
not the bottleneck. The prior session's handoff speculation (port `SDL_
DOSGusVoiceActive()`'s single-voice pattern to `reap_finished_voices()`)
would have been the wrong fix even if attempted -- not just
architecturally mismatched (already caught before writing any fix, see
`S7-gus-getstate-cost-dosboxx-2026-09-14.md`), but aimed at a function
that turns out not to be slow at all.

## The real finding: one single call dominates `slots_us` almost entirely, in both independent runs, at nearly the same value

Checked the arithmetic precisely rather than trusting the aggregate
mean at face value (per this hub's own "aggregate numbers from a short
run need cross-checking" discipline):

| Run | total_calls | slots_us mean | slots_us max | sum minus the one max | avg of the other calls |
|---|---:|---:|---:|---:|---:|
| `GUST1` (2026-09-14) | 67 | 102,962 | 6,890,560 | 7,894 | **119.6us** |
| `GUSD1` (2026-09-15) | 68 | 101,489 | 6,890,385 | 10,867 | **162.2us** |

**One single call accounts for ~99.8% of the total `slots_us` sum in
both runs** -- the other 66-67 calls average 120-162us each, genuinely
cheap and consistent with every other register-write-dominated cost
measured throughout this whole investigation. **The `slots_us` max
itself is nearly identical across two independent real-hardware runs
on two different binaries -- 6,890,560us vs 6,890,385us, a difference
of only 175 microseconds out of 6.89 SECONDS (a 1-in-~40,000 relative
match).** This is far too precise to be environmental/disk-I/O jitter
(the room-transition timestamps themselves, by contrast, differ by
~220ms between the same two runs -- genuine real-world variance). This
points at a **deterministic mechanism tied to the song/scene content
itself** (identical MIDI data, identical room, similar real-time
trigger point), not a random stall.

**Not yet identified**: what specifically causes this one near-
deterministic ~6.89-second call. Candidates, not yet checked: (a)
`midi_sched_tick()`'s own `delta_ms > 10000 -> clamp to 10000`
catch-up-window logic (confirmed by source read this entry) combined
with the exact density/timing of events in that specific 10-second
window of this specific song, landing on a genuinely expensive
per-event operation not yet individually measured (`SDL_DOSGusSetVoice
Freq/Vol/Pan`/`SDL_DOSGusStartVoice` were read and look like plain
register writes with no blocking loop, but were not INSTRUMENTED
directly the way `SDL_DOSGusGetState()` was this entry); (b) something
in the song-loop-restart path (`midi_sched_tick()`'s own `next_idx >=
nevents` wraparound, hit multiple times if a 10-second clamped
catch-up needs to loop a short song several times); (c) an
unidentified hardware/protocol-level cost not yet isolated to a
specific function.

## Where this leaves the S7-GUS work

**The originally-planned fix (port `SDL_DOSGusVoiceActive`'s pattern to
`gus_sink.c`) is not warranted** -- the function it targeted is already
cheap. This sub-investigation needs a fresh diagnostic pass (bracket
`SDL_DOSGusSetVoiceFreq/Vol/Pan`/`SDL_DOSGusStartVoice` individually,
the same way `SDL_DOSGusGetState()` was bracketed this entry) before
proposing any code change, per this hub's own instrument-before-guessing
discipline -- applied a second time in this same sub-investigation,
which is exactly why the first course-correction (catching the
architecture mismatch before writing code) mattered.

**A genuinely encouraging framing, though**: GUS's own *typical*
per-call MIDI dispatch cost (~120-160us) is cheap and unremarkable --
nothing like the systemic OPL3/WaveBlaster tax this whole investigation
spent so long on. The gap between GUS's own `tick_rate` (~9.36-9.39)
and the sound-off baseline (~23.8-23.9) may be dominated by this one
narrow, reproducible, not-yet-explained ~6.9s event rather than a
general inefficiency -- if so, a fix (once the actual mechanism is
found) could recover GUS performance much closer to baseline than the
raw tick_rate number currently suggests. This needs the further
diagnostic pass above to confirm before claiming it, not assumed here.

Acceptance gate items 4 and 5 (re-targeted at GUS) remain open. Patches
SDL/0145 and ags/0069 stay landed (the diagnostic itself is sound and
should stay in place for the next pass); no `gus_sink.c` fix landed
this entry -- correctly not landed, since the originally-planned one
would have been wrong.

## Not yet done

1. Instrument `SDL_DOSGusSetVoiceFreq`/`SDL_DOSGusSetVoiceVol`/
   `SDL_DOSGusSetVoicePan`/`SDL_DOSGusStartVoice` individually (same
   uclock()-bracket idiom) to find which specific call (or the
   `midi_sched_tick()` dispatch loop itself, timed as a whole) is
   responsible for the ~6.89s outlier.
2. Once found, determine whether it is fixable in software or, like
   the OPL3/WaveBlaster tax, another real hardware/protocol constant.
3. Acceptance gate items 4 and 5 remain FAIL/open.
