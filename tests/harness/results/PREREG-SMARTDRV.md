# Pre-registration: SMARTDRV -- is the 220 ms event a disk cache?

Written 2026-09-20, before the toggle cell runs and while the status cell
(`SMARTDRV /S`, `SMARTDRV /?`) is still on the machine.

## Standing on a confirmed line, at last

The card's own `AUTOEXEC.BAT` -- fetched, not reconstructed, and
byte-identical to the `g2k` repo copy -- loads:

    LH C:\WINDOWS\SMARTDRV.EXE 4096 1024 C A-

**What that line does is NOT settled and will not be settled by argument.**
The drive is `C`, not `C+`, and the recollection on the table is that a bare
letter enables read caching and **disables** write-behind -- which would
remove the deferred-flush row the mechanism rests on. The sizes also appear
*before* the drive letters, which is not the documented order, so the command
line is a poor guide to the running state either way.

**`SMARTDRV /S` prints the per-drive read/write cache state as the resident
instance actually configured it.** That replaces two recollections of a
manual with a measurement, and it is running now. **No claim about write
caching is made in this document.**

## Design: within-boot **A-B-B-A**, one cell

`FSPROBE_SYS_PRE` / `FSPROBE_SYS_MID` run DOS commands via `system()` before
the sweep and between two sweeps, so **both arms come from one boot** --
which removes everything except the lever by construction, the same reason a
within-build A/B beats two binaries. No reboot, no `CONFIG.SYS` edit, no
restore to verify, no post-FTP keyboard hang, no mains cycle.

    FSPROBE_SEQ = A-setup | B-toggle | (B again) | A-restore
      stage 1  SMARTDRV /S                  -> sweep A1
      stage 2  <off-toggle> ; SMARTDRV /S   -> sweep B1
      stage 3  SMARTDRV /S                  -> sweep B2
      stage 4  <on-toggle>  ; SMARTDRV /S   -> sweep A2
    384 KB, 800-byte records, arms off, all four identical.

**A-then-B was not enough and I had written it anyway.** Two of
`abba-methodology.md`'s reasons are unusually live for this phenomenon:

- **The first write activity after boot is confounded with whichever arm
  runs first**, on a stall whose trigger is unknown and whose detection is
  intermittent. In an A-then-B layout that confound is indistinguishable
  from the lever.
- **The device accumulates state in one direction only.** Arm B would write
  onto a card that has just taken 384 KB it would not otherwise have taken,
  and wear levelling, cache occupancy and free-cluster position have each
  been candidates in this investigation at some point.

**A-to-A agreement across the two A arms is the stability check.** If A1 and
A2 disagree with each other by more than the A arms disagree with the B
arms, **the cell is void** -- and that is read off the data rather than
argued.

**Every stage's `/S` is the `expect_log`.** A toggle that silently did nothing
would otherwise read as "not the cause", which is the flattering-direction
failure again. **If the two `/S` tables are identical, the cell is void
regardless of what the sweeps show.**

The toggle's exact syntax comes from `SMARTDRV /?` **on the machine**, not
from recollection.

## Predictions

Baseline, from five prior cells: **35.0 records / 28,000 bytes / 445 ms**
between events at 800-byte records, event magnitude **217-230 ms**, rigid to
5% across 27 observations.

**P-GONE (the hit).** Both B arms have **zero events over 20 ms** in 384 KB,
both A arms have events, **and `c` moves between arms** (see below).
SMARTDRV is the mechanism, Gate 2's hold lifts on an explanation rather than
an elimination, and the RAM-disk approval goes unspent.

**The `c` clause is part of P-GONE, not a footnote to it.** P-GONE is the
outcome that would end the investigation, so it is the one to distrust:
**zero events with an unchanged `c` is not a hit.**

**P-SAME (the miss).** Arm B's events match arm A in magnitude **and**
spacing -- magnitude within the 5% band, spacing ratio inside 0.8-1.25.
SMARTDRV is eliminated, and **branch A of the RAM-disk test narrows from four
candidates to three** before that cell runs.

**P-REDUCED, and this is the one that must not be scored as P-GONE.** Events
survive but the **magnitude** moves outside 217-230 ms. A *reduced* stall is
a different finding from an *absent* one: it would mean the cache contributes
part of the cost and something else contributes the rest, which is a
two-mechanism result and closes nothing on its own. **Scored separately, and
it does not lift Gate 2's hold.**

**P-PERIOD.** Events survive at the same magnitude but the **spacing ratio
falls outside 0.8-1.25** -- the same band used for the RAM-disk test, chosen
because the two CF runs' own 1.08 sits inside it. Then the cache is not the
**cost** but is part of the **trigger**: it shapes when writes reach the
layer below without producing the stall itself. That would keep SMARTDRV
alive as an intermediary while eliminating it as the source, and the
follow-up would be the RAM-disk cell anyway -- so **P-PERIOD does not lift
the hold either**, but it does change what the RAM-disk cell is asking.

## Invalidity conditions

- The two `/S` tables identical: the toggle did not take, cell void.
- `SMARTDRV /S` not available, or SMARTDRV not resident in the boot profile
  the probe runs under: **the whole hypothesis is untestable this way and
  must be re-examined** -- the probe cells run under whichever profile
  `run-probe-hw.sh` boots, and SMARTDRV being in `[COMMON]` needs confirming
  from the `/S` output rather than from the file.
- Fewer than 4 events in arm A: the baseline for the comparison is not there
  and only presence/absence in arm B is scored.

## What no outcome here settles

Even P-GONE names the resident without naming what inside it costs 220 ms.
That is an acceptable stopping point for the port -- the mitigation is the
same, and the finding for `HARDWARE.md` is "a resident disk cache on this
target stalls sustained writes by ~220 ms periodically" -- but it is not a
mechanism in the sense of knowing why.


## A second witness on the toggle: the quiet-record cost

`/S` attests what SMARTDRV **reports**. `c` -- the mean cost of a quiet
sweep record, printed per sweep -- attests what the **device path actually
did**. Its stability is already known from two independent measurements:
**6,419 us at 800-byte records, 5,244.9 us at 400-byte**.

**Pre-registered direction: taking a cache out of the write path should
change `c`.** Which way is not obvious enough to call -- removing a cache
could make each `fsync` dearer by forcing real media writes, or cheaper by
removing bookkeeping -- so the prediction is **a change, of either sign,
larger than the A1-to-A2 difference.**

**If `c` is unchanged between arms, the toggle is suspect even with two
different `/S` tables**, because a cache that reports itself off while the
path behaves identically is a distinction without a difference for this
hypothesis. That applies to every outcome, and it is written into P-GONE
explicitly because that is the branch where an unchanged `c` would be
easiest to overlook.

## Restoring: re-fetch and re-diff, not the geometry witness

The probe's two lines confirm which **device** the sweep ran on. They say
nothing about whether `CONFIG.SYS` came back correct, and this cell does not
change `CONFIG.SYS` at all -- but the RAM-disk cell will, and the rule
belongs here where it was established.

**And the clean diff was clean only after normalising.** The card's bytes
arrived through a DOS text path that doubled every newline; the host copy
and the card's bytes are known to be **equivalent modulo that transform**,
not identical. So the restore procedure is: **push back the bytes the card
gave us, re-fetch through the same path, and re-diff through the same
normalisation.** A restore verified by "the machine booted" is the hazard
the hub already has an entry for.

## MEASURED, before the toggle cell: write-behind is OFF, and my mechanism claim is falsified

`SMARTDRV /S` on the machine:

    Room for    512 elements of   8,192 bytes each
    There have been    357 cache hits and 72 cache misses
    Cache size:  4,194,304 bytes

                Disk Caching Status
    drive   read cache   write cache   buffering
      B:       yes           no           no
      C:       yes           no           no

And `SMARTDRV /?`, from the same machine:

    drive   Sets caching options on specific drive(s). The specified
            drive(s) will have write-caching disabled unless you add +.

**`write cache: no` for C:.** The coordinator's recollection of the argument
grammar was right and mine was wrong: a bare drive letter enables read
caching and disables write-behind. **The deferred-flush mechanism I proposed
has no basis** -- the row it rested on is gone, and the table in PLAN.md that
matched five observations against "a write-behind cache flush" was matching
them against something this machine does not do.

**The candidate survives in a weaker form, exactly as the coordinator
framed it.** SMARTDRV is still an INT 13h hook that sees every write and
must invalidate or update cached elements on each one -- write-*through*
work, not deferred work. That is a smaller, less periodic-looking cost, so
**the prior drops substantially** and the cell is now more likely to
eliminate than to confirm. Worth running anyway: it is minutes, the
elimination narrows the RAM-disk branch for free, and the lever is
reversible.

**Element size is 8,192 bytes.** Recorded because it is the only internal
quantum SMARTDRV exposes, and the spacings measured are 28,000 bytes at
800-byte records and 19,778 at 400-byte -- **neither a multiple of 8,192**.
That is a further argument against, stated before the cell rather than after.

### The lever changes accordingly

Write caching is already off, so toggling it is not available. The arm that
takes the cache out of the write path is **`SMARTDRV C-`**, which `/?`
documents as disabling **all** caching for that drive, restored by
**`SMARTDRV C`** -- the invocation the card's own `AUTOEXEC.BAT` uses.

    stage 1  SMARTDRV /S         -> sweep A1   (read cache on)
    stage 2  SMARTDRV C- ; /S    -> sweep B1   (all caching off for C:)
    stage 3  SMARTDRV /S         -> sweep B2
    stage 4  SMARTDRV C  ; /S    -> sweep A2   (restored)

**The `/S` tables must show `read cache: no` for C: in stages 2 and 3 and
`yes` again in stage 4**, or the toggle did not take and the cell is void.

## Scoring bars, fixed before the re-run is opened

### Gate 0: stage count, checked before any sweep number is read

The re-run predates `FSPROBE_STAGES`, so the check is host-side: **count the
`/S` tables in the output. There must be four.** With `#` the truncation
would not announce itself and the run would look right. **Fewer than four:
void again, nothing scored.**

### A-to-A stability: judged on `c`, NOT on event count

**Event counts are explicitly excluded from the stability test.** Three runs
of one configuration produced **7, 10 and 14** events. A1-versus-A2 differing
2x in event count is therefore expected and means nothing, and without saying
so now it would look alarming at scoring time with no pre-registered answer.

**The A-to-A bar is `c`:** the two A arms must agree within **3%**. That is
calibrated from data, not chosen -- `c` measured 6,419 us and 6,593 us across
two runs of the same configuration, **2.7% apart**. Beyond 3%, something
drifted that is not the lever and **the cell is void.**

Same bar for B1-versus-B2.

**Secondary A-to-A check: mean event magnitude within 5%**, the band the
magnitude has held across 27 observations.

### Spacing, for P-SAME and P-PERIOD: the base spacing, not the mean gap

**P-PERIOD's 0.8-1.25 band cannot be judged on mean gap or on
bytes-per-event**, because those are exactly the quantities that swing 2x
with nothing varied. Judging a 1.25 band against a 2x-noisy statistic would
be scoring noise.

**Base spacing is estimated by folding multiples down:** take every observed
gap, divide by `round(gap / g_min)` where `g_min` is the smallest gap in that
arm, and take the median. A missed detection makes one gap 2x or 3x the base
and this divides it back, which is precisely the property the mean gap lacks.
Applied per arm, then compared A-to-B.

This is the same statistic as the lattice `S` and is used here only as a
robust estimator of base spacing between arms -- **no significance is
claimed for it, per the no-p-value finding.**

### Correction to the spacing estimator, before the re-run is opened

**`g_min` was the wrong anchor and the error is systematic, not noisy.**
Dividing every gap by a multiple derived from `g_min` anchors the whole
estimate on the single most extreme order statistic in the sample -- the one
an anomaly lands on by definition. Two off-lattice members are already on
record: **rec 246**, off the 35.0 lattice and present in one run only, and
the **33 ms** magnitude outlier. One short anomalous gap becomes `g_min`,
every `round()` above it inflates, and **the base estimate biases downward in
a way the median cannot rescue, because the median is taken after the bad
division.**

**Anchor on the fitted `S` instead**, per arm, by the same closed-form phase
fit used earlier: a global fit rather than a single extreme value, and a
missed detection raises one `n` rather than corrupting the divisor for every
gap. Used **purely as a robust estimator between arms** -- a robust estimator
and a significance test are different uses of the same arithmetic, and only
the second is barred by the no-p-value finding.

**And the fold has to be able to fail.** After dividing, report:

- the **folded residuals** `|gap/S - round(gap/S)|` for every gap, and
- the **multiplicity histogram**, the counts of each `n`.

**P-PERIOD is scored only if the fold held: max folded residual <= 0.20.**
An estimator that cannot fail its own assumption will return a number on
noise -- the same rule as a decomposition instrument asserting its parts sum
to its whole.

### Minimum event count, and why it has to be written down now

**P-PERIOD is scorable only for an arm with at least 5 events (4 gaps).**
Below that a folded median is not an estimate. **An arm below the threshold
is NOT SCORABLE for P-PERIOD** -- not P-SAME, not P-GONE, not any of the
four.

**This matters most for the arm expected to be quiet.** If the toggle works,
arm B has few or no events by construction, so **P-GONE and "P-PERIOD
unscorable" will arrive together** -- and "spacing unchanged" versus "spacing
could not be measured" are different statements, only one of which is about
the cache. That distinction is written down here, before both arrive at once
wearing each other's clothes.

### P-SAME's boundary, written into the outcome and not into a footnote

Excluding event counts from every test is correct -- they swing 2x with
nothing varied -- but it has a consequence that has to travel with the
verdict:

> **P-SAME eliminates SMARTDRV as the source of the event's cost and as the
> setter of its period. It does NOT eliminate it as an influence on the
> event's frequency, which this cell is not powered to measure.**

If disabling the cache halved or doubled how often the stall occurs while
leaving each event's magnitude and the base period intact, **this design
cannot see it, and it would return P-SAME.** A reader three weeks from now
will take P-SAME as "SMARTDRV eliminated" unless the outcome itself says
otherwise, so it says otherwise.

**The limitation is bounded, not open-ended.** Treating the counts as
Poisson -- 7, 10, 14 give mean 10.3 and sample variance 12.3, consistent
with Poisson, though on three points that is weak evidence and not a
distributional claim:

| rate change to detect | events needed per arm | runs per arm |
|---|---|---|
| 2x | 12 | **~1.2, so 2** |
| 1.5x | 41 | **~4** |
| 1.25x | 145 | **~14** |

*(2-sigma on the log ratio of two Poisson totals, `SE = sqrt(1/N_A + 1/N_B)`.
The first version of this table said 21 / 81 / 289 events and 2 / 8 / 28
runs; those were written from a rougher derivation before the arithmetic was
run and are wrong by roughly 2x. Corrected here rather than quietly
replaced.)*

**The three banked counts are NOT A-arm data, and "we already have the A
arm" is the shortcut this table invites.** 7, 10 and 14 came from
*standalone* runs: first write activity after boot, fresh device state, no
toggled arms sharing the boot. The new A arms sit at stage 1 and stage 4 of a
four-stage within-boot sequence, and stage 4 follows up to **1.1 MB** of
prior sweep writes. **Different population, same-looking number** -- and boot
position and accumulated device state being live confounds for this exact
phenomenon is why the cell was rebuilt as A-B-B-A in the first place. The
follow-up needs ~2 runs **per arm, both arms, in the same sequence shape.**
The three banked counts stay what they have been all night: evidence that
detection is intermittent, and nothing else.

**One point in the Poisson treatment's favour, not claimed above:
intermittent detection is a thinning, and a thinned Poisson is still
Poisson.** So the model is more defensible for the *detected* count -- which
is what the power calculation is about -- than for the underlying process.
Still three points and still not a distributional claim, but the structure is
on its side rather than against it.

**A 2x frequency change needs two runs per arm. Not running them now** --
the point is that the follow-up exists and has a size, so if branch A later
narrows to "SMARTDRV or the controller", nobody has to rediscover that this
cell left frequency open.

**The same boundary applies to the RAM-disk cell**, and for the same reason:
its branches are about **presence**, and presence and rate are different
questions on an instrument this noisy. Recorded there too when it runs.
