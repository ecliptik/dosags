# Pre-registration: LOGAB -- does the present stall go away with the log?

Written 2026-09-20, before any cell runs.

## The claim being tested

FPT1 located the ~250 ms present stall in the `post` phase (t2..t3) of the
direct-framebuffer fast path: 227.106 ms of a 241.698 ms total, against a
steady-state `post` of 0.221 ms. That span contains the per-100-flush VRAM
readback diagnostic and the bank audit, both of which call
`dos_port_dbg_log` -- `fprintf` + `fflush` + `fsync`, per line, to a CF
card, from inside the present.

FPT1 shows the routine cost too: the five-line batch costs ~10 ms in all 24
blocks. The stall is one batch out of twenty-four costing 227 ms instead.

**If that is the cause, removing the log removes the stall.** If it is not,
the stall survives and the 227 ms belongs to something else in t2..t3 that
happens to coincide with the diagnostic's cadence.

## Design

Within-build A/B, one binary, arms selected by env -- so layout, code size
and patch level cannot differ between arms.

- **ON**: as FPT1 (no extra env). Logging on, ~5 log lines per 100 flushes
  inside the present.
- **OFF**: `DOS_PORT_LOG=0` (patch 0188). `dos_port_dbg_open` returns
  early, `g_dbg_log` stays NULL, every `dos_port_dbg_log` call becomes a
  function call and an int compare. No file is created at all -- verified
  under DOSBox-X: no `LOGS` directory exists after an OFF run.

Four cells, alternating OFF, ON, OFF, ON, so a drift in the machine cannot
line up with the arm. `bench8 anim12`, Mode 13h, `--gate` enforced
(5000 ticks), same binary throughout.

## Predictions

**P1 (the test).** Across the two OFF cells, **no `tick_stall` line with
`ms >= 200`**. The ON cells reproduce FPT1 and show at least one.
- Falsified if an OFF cell stalls at ~250 ms. Then the log is not the
  cause, FPT1's coincidence was a coincidence, and `post` still needs
  splitting.

**P2 (the size).** OFF's whole-run `tick_rate` exceeds ON's by **0.10 to
0.25**. Derivation, fixed now: the routine batches are 24 x ~10 ms = ~240 ms
and a stall is ~270 ms, so ~510 ms of a ~125,000 ms loop = 0.41%, and
0.41% of 39.2 is 0.16. The range allows for runs that take one stall rather
than two.
- A move larger than 0.4 means something other than the log changed and the
  cell is not clean.
- A move under 0.05 with P1 holding would mean the stall was real but
  costless in the whole-run figure, which would be strange and worth
  stopping over.

**P2 refined, before any cell finished.** The per-block analysis committed
after this file was written shows the batch costs 21-36 ms, not ~10 ms --
the ~10 ms was only the `post` share, and `dpmi` and `copy` carry an fsync
each as well. Excess over a 2.0 ms baseline flush is therefore ~19-34 ms per
batch: 23 batches x ~24 ms plus the 240 ms stall batch is ~790 ms of
125,000 ms, **0.63%**, which is 0.25 in `tick_rate`. That sits at the top of
the range P2 already states rather than outside it, so **P2's range stands
as written** -- but the expected value inside it moves from the bottom to
the top, and a result near 0.25 should be read as the prediction landing,
not as overshooting it.

**P2 refined again, still before any cell finished, and this time the range
breaks.** Both revisions above priced only the flush path. `FPT1SDL.LOG` is
197 lines and only 123 are per-flush; the other **74** are the VESA control
block, a 19-mode enumeration with its table rows, three mode-sets, nine
`GetWindowSurface (cached)` and three `CheckWindowPixelSizeChanged`. Each is
an fsync too, and most land in `preloop_ms`, which whole-run `tick_rate`
counts (TNFB1: 4999/39.06 = 128.0 s against `loop_ms` + `preloop_ms` =
127.8 s). 197 fsyncs at 4-7 ms plus the ~220 ms excess on the bad one is
**~1.2 s of ~127 s = 0.95%, or 0.37 in `tick_rate`.**

**The three figures, kept together so the score is legible:**

| | derivation | expected move |
|---|---|---|
| **P2 as pre-registered** | 24 batches x ~10 ms + one 270 ms stall | **0.10 - 0.25** |
| first revision | batch is 21-36 ms, not 10; flush path only | 0.25 |
| **second revision** | + 74 startup/other fsyncs, in the denominator | **0.37** |

**Scoring rule, fixed now.** P2 is the range in the first row and nothing
else. **A result of 0.25-0.40 scores as a MISS on P2** even though it is
what I now expect and even though it would confirm the mechanism. The range
was wrong because I priced the instrument only where I had been looking for
it, twice, and a prediction that gets widened to fit its own revisions is
not a prediction. What the mechanism earns is P1 and P3; P2 is a miss and
should be written as one.

**And the invalidity threshold below has to move, which is the part worth
being suspicious of.** "A move larger than 0.4 means the cell is not clean"
was written when 0.16 was expected; it now sits 0.03 above what I expect,
so it would fire on a clean result. Raising it to **0.60** -- but raising an
invalidity condition to accommodate a revised expectation is exactly the
manoeuvre that makes pre-registration worthless, so: the 0.60 is justified
only by the same 197-fsync count that produced the 0.37, it is recorded
before any cell landed, and **if the measured move exceeds 0.60 the cell is
still dirty and no further widening is available.**

**P3 (Gate 2).** OFF's whole-run `tick_rate` clears **39.2** in both cells.
FPT1 measured 39.36 with the log still on and one stall instead of two, so
this is not a stretch -- but 39.36 is n=1 on an instrumented build and is
not itself a claim.

## What a pass would and would not mean

It would mean the present stall is an artifact of our own instrumentation
and not a property of the port, and that Gate 2's whole-run `tick_rate`
was being held under its bar partly by the diagnostic that was installed to
find out why. It would **not** license reporting the OFF number as the
port's figure without saying which instruments were off, and it would not
retire the trace -- the default stays ON, because that trace is how this
port's video bring-up was diagnosed and a port that hard-resets wants it.

The honest framing if it passes: *this is what the port does when the
measurement is not in the way,* and every cell measured before today
carried it.

## Invalidity conditions

- **An ON cell with no stall makes its paired OFF cell uninformative.** The
  phenomenon has to be present before its removal means anything. Two ON
  cells are run for this reason; if neither stalls, P1 is unscored, not
  passed.
- `build_dirty` or the binary sha differing between arms invalidates the
  A/B outright -- it is supposed to be one binary.
- An OFF cell that still produces `LOGS\<TAG>SDL.LOG` means the gate did not
  take and the arm is not an arm.
- `exit_code != 0`, or a recovery firing mid-cell, drops that cell.

## Not being claimed

Patch 0187's per-flush `flushslow` trace and patch 0186's `fbcreate` line
are in this binary and print only on the ON arm. They are diagnostics for
the ON cells and are not part of the A/B.
