# S7 -- DOS_Yield() diagnostic, DOSBox-X validated -- 2026-09-14

Continuation of `S7-scheduler-mechanism-investigation-2026-09-14.md`.
Patches `SDL/0142` (instruments `DOS_Yield()` itself) + `ags/0064`
(folds it into the `tickfx` catch-up/real-tick split) are temporary.

## DOSBox-X validation

Same recipe as every other diagnostic in this series.
`binary_sha12=7d2309fcdef7`, confirmed matching `make build-sha12`.

```
DOS-PORT tickfx total_calls=156 window_calls=156 catchup_n_sum=44
  catchup_us(min=2 mean=14332 max=2207803)
  realtick_us(min=321 mean=33108 max=580804)
  catchup_yield(switches=4 min_us=16 mean_us=3721 max_us=12847)
  realtick_yield(switches=3766 min_us=9 mean_us=1429 max_us=204275)
```

Wired correctly, producing data. Two things worth recording:

**A genuine, pre-existing data-quality bug, not introduced by this
patch**: the same run's `audioprb` line shows
`regwrite(calls=214 min_us=6 mean_us=2841845630 max_us=2564571650)` --
a mean in the *billions* of microseconds, i.e. garbage. `min_us=6` is
sane; `mean_us`/`max_us` are not. Almost certainly a single corrupted
per-write sample poisoning the running sum -- most likely explanation:
a rare `uclock()` non-monotonicity dip (this hub's own history already
documents "~1 corrupt sample per 1800 frames" for this exact primitive,
`docs/timing.md` / patch `SDL/0136`'s findings) landing during one of
`SDL_DOSOpl3WriteRegister()`'s own diagnostic brackets (`SDL/0141`),
where an unsigned-wraparound subtraction (`uclock() - t0` when the
second reading is spuriously smaller) would produce a huge `call_us`
that then poisons `sum_us`/`max_us` for the rest of the window. Not
something this session's own new instrumentation touches -- `SDL/0141`
predates this patch and was clean in every prior run -- but genuinely
new exposure: this run does far more `uclock()` calls overall (every
`DOS_Yield()` now reads it too), which plausibly raised the odds of
hitting the same rare pre-existing hazard within one run. **A cheap,
safe follow-up** (not applied this entry, out of scope for the yield
question): clamp `SDL_DOSOpl3WriteRegister()`'s own diagnostic to reject
an implausibly large single-call duration (e.g. >1s) rather than folding
it into the running sum/max. Doesn't affect this diagnostic's own
`tickfx`/`catchup_yield`/`realtick_yield` numbers, which show no such
corruption.

**A real, unexpected DOSBox-X result on the yield question itself**:
switches are heavily concentrated in the real tick (24.1 switches/call)
versus almost none in the catch-up burst (0.09 switches/catch-up-tick,
4 total across 44 catch-up ticks). If this held on real hardware too,
it would refute rather than confirm the cooperative-scheduler
hypothesis for the catch-up-tick tax specifically (since catch-up ticks
would barely touch the scheduler's yield path at all here). **But this
cannot be trusted as the answer**: DOSBox-X does not reproduce the
underlying phenomenon under test at all in this cell (`tick_rate=30.58`,
nowhere near the real-hardware collapse) -- branch counts inside
`WaitDevice()`'s own ring-full spin loop are directly driven by real
wall-clock IRQ-drain timing, which legitimately differs between
environments (a ring that never goes dry in DOSBox-X's fast emulation
could run chronically dry on real, slow hardware, changing how many
times that loop -- and thus `DOS_Yield()` -- actually executes). This is
exactly the class of result this investigation has repeatedly found
DOSBox-X unable to predict. Only a real-hardware run of this exact
diagnostic can answer the actual question.

## Not yet done

1. Real-hardware cell -- needs a fresh, separately-asked operator
   go-ahead, not taken this entry.
2. The regwrite corruption's defensive clamp -- flagged, not fixed.

No real hardware used this entry. Acceptance gate items 4 and 5 remain
FAIL.
