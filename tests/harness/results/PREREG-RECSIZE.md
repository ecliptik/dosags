# Pre-registration: RECSIZE -- position or operation count?

Written 2026-09-20, before the run. One probe cell. No archive touched, no
clear, no risk to the only copy of the campaign's logs.

## The two families

The ~220 ms event fired at **record 8 / byte 6,400** and **record 73 / byte
58,400** with 800-byte records, in both FSPROBE runs, within 1.5%. Record
index and byte offset are perfectly confounded at a single record size.

Re-run the same sweep at **400 bytes**, same binary, same volume, same
directory, record size from `FSPROBE_REC`. The two families now predict
different things and cannot both be right:

| observed spikes | family | consequence |
|---|---|---|
| bytes **6,400 and 58,400** (records 16 and 146) | **POSITION** -- in the file, the allocation, or on the media | the physical account is alive and CLEARDIR is the right follow-up, unchanged |
| records **8 and 73** (bytes 3,200 and 29,200) | **OPERATION COUNT** -- something above the media counting writes | the physical account is dead outright, and a family nobody has considered opens |

**Predicting POSITION.** The event's size (~220 ms) is characteristic of
media, not of bookkeeping, and nothing in DOS is known to do expensive work
on the 8th write. Committing to it so a count result is a real surprise
rather than a shrug.

## Third possibility, named in advance

**Neither.** Spikes at some other offset, or none at all in 96 KB. That
would mean the positions were never as stable as two agreeing runs
suggested -- which is the stability worry already recorded against CLEARDIR,
arriving from a different direction. In that case **CLEARDIR is off**: there
is no baseline, and no experiment built on these offsets is worth a cell
until stability is established.

## What the 400-byte run also does

It is the **stability baseline** CLEARDIR was missing, for the position
branch. If the spikes land at 6,400 and 58,400 a third time, at a different
record size, those byte positions are established far more strongly than a
same-size repeat would have established them.

## If it comes back count-driven

The next discriminator is whether the count is per-write, per-`fsync` or
per-`fopen`, and **the existing four arms already vary those independently**
-- `raw` writes without flushing, `flush` flushes without syncing, `sync`
syncs, `reopen` opens per iteration. It may fall out of data already in
hand.

## Held in reserve, not to be run yet

If both families die: write the same sweep **to a different device**. No
spikes on a RAM disk or another volume means the CF media; spikes means DOS
or the BIOS above it. **That needs a boot-config change, which the standing
authorization explicitly excludes**, so it is an operator ask and not a next
step. Recorded so that "no candidate mechanism" is known not to be the end
of the road before the branch where it would be reported as one.

## Queued behind this: ARMORDER, and the asymmetry stays its own open item

`flush` spiked at **212,867 us** in `C:\DOSAGS` and peaked at **3,611 us** in
`C:\FSTEST` -- same arm, same byte range, same crossing of 6,400 at iteration
50 -- while `sync` spiked in both. **Position as stated does not predict
that.**

**It stays on the open list with its own line whatever RECSIZE returns.** A
clean POSITION result would make it very easy to file as noise, or as
"position, plus something", and one confirmed mechanism quietly absorbing a
neighbouring phenomenon it does not explain is the shape this campaign has
been caught by more than once tonight alone.

**ARMORDER tests it, and it needs no new instrument.** `FSPROBE_ORDER` now
selects the arm order at runtime, default `raw,flush,sync,reopen` -- what
every run so far used. Arms 1-3 each truncate and rewrite bytes 0..25,600, so
all three cross 6,400 at iteration 50, and the first-write-to-a-region
refinement says whichever gets there **first** pays.

Run with `FSPROBE_ORDER=flush,raw,sync,reopen`:

| result | inference |
|---|---|
| `flush` spikes when first and not when third | **first-write-to-region confirmed**, and `C:\FSTEST`'s silence is `raw`'s `fclose` burst having touched the region outside any timed window |
| `flush` spikes in both positions, or neither | the refinement is **wrong** and the asymmetry is something else |

Queued **behind** RECSIZE, not ahead of it: RECSIZE decides which family we
are in, and this only means anything inside the position family.
