# Pre-registration: TIMER -- integer multiples, not even gaps

Written 2026-09-20 while the timed sweep is still on the machine, **before
its output has been opened.** The fit criterion and its calibration are
fixed here so neither can be chosen after seeing the gaps.

## Why "even gaps" is the wrong test

A timer fires on its own schedule. These are **write** stalls, so a tick
arriving while nothing is in flight produces nothing observable, and the next
observed event is one, two or three periods later. **Observed gaps under a
real timer are integer multiples of a common period, not all equal to it.**
A strict evenness test would report "not a timer" on a textbook timer.

**That shape is already in this campaign's data.** The SDL-log analysis found
gaps of **20,544 / 40,215 / 60,224 ms** -- 1.02x, 2.00x, 3.00x of ~20,100.
A periodic source sampled by an intermittent observer, which is exactly what
a write stall observed only during writes would be.

## The criterion, fixed now

Let the six measured inter-event intervals be `g_1..g_6`, in **milliseconds
of cumulative elapsed time**, from the probe's own `cum_ms` fields -- not
reconstructed from an assumed per-record cost, which is the error that made
the previous conversion a property of its own assumption.

1. Search `T` over **[max(g)/4, max(g)]**. That range is the anti-
   unfalsifiability clause: it forces every multiplier `n_i = round(g_i/T)`
   into **{1,2,3,4}**, so `T` cannot shrink until it divides anything. It is
   the same hole as P-RATE's undefined middle, closed in advance.
2. **PASS** if some `T` in that range gives
   `max_i |g_i/T - round(g_i/T)| <= 0.10`.
3. Report the fitted `T`, the six multipliers, and the worst residual,
   whatever the verdict.

### Calibrated against a null before the data was seen

20,000 draws of six gaps uniform on [200, 1500] ms, same search, same range:

| tolerance | null pass rate |
|---|---|
| 0.15 | 2.50% |
| **0.10** | **0.38%** |
| 0.05 | 0.00% |

**0.10 is the right tolerance**: a 0.38% false-positive rate is a real test,
and tightening to 0.05 would risk rejecting a true timer over jitter in a
220 ms event measured on a 486. Fixed at 0.10.

## Outcomes

- **PASS** -- the timer family is live, and the different-device test becomes
  the question of *whose* timer rather than whether there is one.
- **FAIL** -- the coordinate the original observation pointed at is
  eliminated properly, three families plus this one are dead, and the
  different-device ask is the right next move.

## Secondary, and reported either way

- **`c`, the mean cost of the quiet records.** Every byte-to-time conversion
  so far has had to guess it. Its measured value retires that.
- Whether `uclock` sweep elapsed agrees with the summed per-record total. A
  disagreement means time is going somewhere the per-record timing does not
  see, which would be its own finding.
