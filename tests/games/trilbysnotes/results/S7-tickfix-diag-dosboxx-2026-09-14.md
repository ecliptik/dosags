# S7 -- dos_run_tick_fixed() catch-up-vs-real-tick diagnostic, DOSBox-X validated -- 2026-09-14

Continuation of `S7-tick-starvation-source-investigation-2026-09-14.md`'s
recommended next step. Patch `patches/ags/0063` (temporary) brackets
`dos_run_tick_fixed()` itself, splitting each call into the catch-up
burst's summed cost vs. the one real (rendering) tick's cost -- see that
patch's own commit message and `game_run.cpp`'s block comment (right
before `dos_run_tick_fixed()`) for the full rationale.

## DOSBox-X validation

Same recipe as every other diagnostic in this series (`dosbox-run.sh`,
scratch `oplmode=opl3` fast conf, Trilby's Notes,
`DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`,
`SDL_HINT_DOS_AUDIO_BACKEND=opl3`). Provenance: `binary_sha12=ec9459908706`,
confirmed matching `make build-sha12` against the committed tree
(patch 0063 applied as a real commit, not just an uncommitted edit --
the first run of this diagnostic was built against an uncommitted
`vendor/ags` working-tree edit and its own `build-sha12` output was
silently stale, since that fingerprint hashes `git rev-parse HEAD^{tree}`;
caught before trusting it, re-run after landing the patch properly).

```
DOS-PORT tickfx total_calls=154 windows_recorded=1 windows_dropped=0
DOS-PORT tickfx total_calls=154 window_calls=154 catchup_n_sum=46 catchup_us(min=2 mean=14631 max=2224899) realtick_us(min=361 mean=33311 max=579392)
```

(A prior run against the uncommitted build showed the same shape:
`total_calls=157 catchup_n_sum=43 catchup_us(mean=14335) realtick_us(mean=32628)`
-- reproducible.)

**Wired correctly, sane means**: `catchup_us` mean (14.6ms, the summed
cost of up to 5 logic-only `UpdateGameOnce()` calls) and `realtick_us`
mean (33.3ms, the one real tick, which includes the already-known audio
sub-cost -- `pump_us` mean 11.0ms + `slots_us` mean 33us from the same
run's `audioprb` line) are both plausible against everything already
measured in this investigation.

**A real, unresolved max outlier**: both fields show one huge single-call
spike (`catchup_us max=2.22s`, `realtick_us max=579ms`) in a 9-second
total run. Most likely a one-time room-transition/asset-load stall
folding into whichever tick it happened to land on (this investigation's
own real-hardware STDOUT.TXT elsewhere logs a genuine ~20s room-transition
cost for this same game) -- not chased further at this DOSBox-X-sanity-
check stage, since the means are what the tick-starvation question turns
on. Worth remembering when reading the eventual real-hardware result: a
single-window run (this diagnostic's own `windows_recorded=1` at this
tick cap) can have its max dominated by a one-time non-recurring event,
not the steady-state per-tick cost.

**A note on `total_calls` divergence**: `tickfx total_calls` (154,
`dos_run_tick_fixed()`/`GameTick()` invocations) is lower than `audioprb
total_calls` (186, `audio_core_entry_poll()` invocations) in the same
run. Expected, not a bug: `audio_core_entry_poll()` has a second call
site outside `dos_run_tick_fixed()`'s catch-up loop entirely (the
`play.fast_forward` cutscene-skip path, `game_run.cpp`'s own comment on
that branch) -- this diagnostic does not (and is not meant to) capture
that path.

## Not yet done

1. **Real-hardware cell** -- the actual question (does the missing
   ~250ms/tick concentrate in `catchup_us` or `realtick_us`) can only be
   answered on real hardware; DOSBox-X does not reproduce the collapse at
   all here (`tick_rate=30.58`, nowhere near the target-starved regime).
   Needs a fresh, separately-asked operator go-ahead -- not taken this
   entry.
2. The max-outlier mechanism (room-transition/asset-load stall) is
   plausible but not confirmed -- would need `--log-stdout=+mgs:all`
   (not used by this ad-hoc smoke recipe) to see the room-transition log
   line directly correlated against which tick it landed in.

No real-hardware time used this commit. Acceptance gate items 4 and 5
remain FAIL.
