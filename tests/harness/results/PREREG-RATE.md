# Pre-registration: RATE -- does the event fire every N device bytes?

Written 2026-09-20, before the run. One probe cell, same volume, no boot
config, no archive, no clear.

## The untested family

POSITION and COUNT were both tested as **where**. Neither was tested as
**how many**. What survived RECSIZE:

- **Magnitude rigidly constant** -- nine events, 218,770-229,526 us, within 5%.
- **Position not reproducible** -- scattered; three spikes where two runs had two.
- **Rate apparently stable** -- ~4-5 events per ~200 KB written.
- **`sync` pays every time**, and `sync` forces every record to the device.

That is the signature of an event firing **every N bytes actually written to
the device, wherever the running total happens to have reached**. Constant
cost because it is one operation; scattered position because the trigger is a
total, not a location. And the arms sort exactly as it predicts: `raw`
buffers everything until `fclose` and pushes nothing inside the window, so it
never pays; `sync` forces every record and pays every time; `flush` and
`reopen` pay or not depending on when DOS chooses to push.

**It also dissolves the inversion I reported.** The game's SDL log writes a
deterministic byte stream, so a running-total trigger fires at a
deterministic point in it -- flush 1200, three runs, two binaries. The
probe's arms differ in *when* bytes reach the device, so the same trigger
scatters. The probe's scatter and the game's determinism stop being in
tension and become one mechanism seen through two write patterns.

## Design

`FSPROBE_ORDER=none FSPROBE_SWEEP_KB=384 FSPROBE_REC=800`, in `C:\FSTEST`.

**Arms skipped deliberately.** Every sweep record is `fsync`'d, so every
sweep byte is a byte forced to the device. With the arms out, the sweep's
393,216 bytes are the *only* device bytes in the run, and the measurement is
events-per-device-byte with nothing to model. That is cheaper and cleaner
than instrumenting the arms' device bytes, which is not directly observable
from DJGPP anyway -- only `fsync` guarantees a commit, so for `flush` and
`reopen` the true figure is unknown rather than merely unmeasured.

Record size 800, matching the first two runs. Under the rate hypothesis
record size is irrelevant, which is itself a small extra check.

## Predictions

**P-RATE.** **8 to 12 events in 393,216 bytes.** Derived from the observed
sweeps before the fact: 2 and 3 spikes in 98,304 forced bytes is one per
33-49 KB, and 393,216 at that rate is 8.0 to 11.9. The probe prints
`RATE = one event per N device bytes` so the figure is not reconstructed
afterwards.
- **<= 5 events** -> not a rate. It is something about the run rather than
  the bytes, and the different-device test becomes the right next move.
- **> 15 events** -> faster than any previous run implies; the sweep-alone
  configuration changed something and the comparison is not clean.

**P-MAG-2.** Every event again falls in **210,000-240,000 us**. Nine of nine
so far sit inside a 5% band; a rate hypothesis has no reason to change the
cost of the operation.
- Falsified by events whose size varies with position or with each other,
  which would mean the constant magnitude was a property of the small
  samples.

**P-EVEN.** Under a running-total trigger the gaps between events should be
**roughly equal** -- within about 2x across the run, not 10x.
- This is the part the rate hypothesis can fail while still producing about
  the right count. Bunched events with long empty stretches would mean the
  right number for the wrong reason.

## Invalidity conditions

- Zero spikes: unscored, not falsified -- re-run before drawing anything.
- `FSPROBE_ORDER=none` failing to skip the arms (visible in the output,
  which prints the order and an explicit "arms SKIPPED" line) invalidates the
  device-byte denominator and therefore P-RATE.
- If free clusters have moved materially since the last run, the volume state
  differs; the probe prints them before and after.

## What this does NOT settle even if it passes

The **mechanism** stays open. A confirmed rate identifies the family -- the
trigger is a running total of device bytes -- without saying whether the
counter lives in the card, in DOS, or in the BIOS. The different-device test
is still what separates those, and it still needs a boot-config change and
therefore an operator ask.
