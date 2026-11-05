# S7 -- IRQ7/spurious-interrupt hypothesis: REFUTED before real hardware -- 2026-09-14

Continuation of `S7-thread-existence-realhw-2026-09-14.md`'s own
proposed next hypothesis: does HW-486-66's PicoGUS being jumpered to
IRQ7 (the classic ISA LPT1 line) interact with 8259 PIC "spurious IRQ7"
handling to produce the ~9.7x-11.8x uniform per-`UpdateGameOnce()` tax,
independent of DMA activity or thread existence (both already ruled
out)? This entry is the design pass for that hypothesis. It concludes
the hypothesis is dead **before spending any real-hardware time on it**
-- both this rig's own documented BIOS facts and a quantitative
re-reading of data already in hand refute it directly. No patch, no
real hardware used this entry.

## The specific mechanism is refuted by this rig's own documentation

`~/git/g2k/README.TXT`'s own "VERIFIED BIOS FACTS FOR THIS HARDWARE (do
not relitigate)" section already addresses this exact conflict:

> IRQ 7 IS CLAIMED TWICE ON PAPER: the parallel port is set to 378/IRQ 7
> and the PicoGUS is jumpered to IRQ 7. In practice nothing has broken,
> **because LPT Mode is Output Only and DOS printing is polled rather
> than interrupt-driven, so the port never asserts the line.**

This directly refutes the mechanism as proposed: LPT1 physically cannot
generate any interrupt activity on IRQ7 on this rig under normal DOS
operation -- there is no interrupt-driven printing path to trigger it,
polled output never asserts the IRQ line at all. The "shared line causes
spurious pulses" premise requires the OTHER device on the shared line to
actually assert it; here it structurally cannot. This is a real,
previously-recorded fact this investigation should have checked before
proposing the hypothesis, not a new measurement -- caught by reading the
rig's own operator documentation before reaching for a real-hardware
cell, per this hub's own "verify before guessing" discipline.

## A second, independent refutation: the tax doesn't scale with IRQ activity at all

Re-reading data already collected (`S7-dma-cyclesteal-realhw-2026-09-14.md`,
`S7-thread-existence-realhw-2026-09-14.md`) rather than new measurement:

| Arm | Real IRQ-7 fires this run | catchup_us/tick | realtick_us |
|---|---:|---:|---:|
| B (`DMAX1`, DMA halted) | **0** | 495,800 | 469,300 |
| D (`NOBGT1`, no thread) | **1,948** | 498,000 | 472,600 |

Arm B (zero real interrupt-line activity for the entire 93s run) and
Arm D (1,948 real fires, ~20.9/s, confirmed via the `CloseDevice` IRQ
tally) show **essentially the same tax** (a 2.2ms/tick difference
across 1,948 fires -- ~1.1us attributable per fire even if the entire
gap were credited to IRQ-servicing cost, which is not itself
established). **Any hypothesis in the "per-interrupt-servicing-cost"
family -- whether the interrupts are real DMA completions or
hypothetical spurious pulses -- cannot explain a ~450-500ms/tick tax
that is IDENTICAL whether the interrupt line fires zero times or ~2,000
times in the same window.** This independently kills not just the
IRQ7/LPT1-specific mechanism but the entire class of hypothesis it
belongs to (any "cost accrues per interrupt, real or spurious"
explanation), without needing a new measurement -- the disproof is
already implied by data on hand.

## Where this leaves the investigation

**Eight hypotheses now ruled out**, all with source-verified reasoning
or real-hardware/DOSBox-X measurement: `audio_core_entry_poll()`'s own
cost, the pre-0060 poll-count multiplier, OPL3 register-write
volume/cost, cooperative-scheduler yield-switch volume, active DMA
transfer, autonomous-audio-thread existence, and (this entry, by
documentation + re-analysis, no new measurement) IRQ7/LPT1 sharing and
the broader per-interrupt-servicing-cost family.

**What remains true and unexplained**: the tax appears in every
"device open" condition tested (thread present or absent, DMA active
or halted, IRQ firing 0 or ~2,000 times) and is absent only when the
device is closed entirely. The mechanism must be something established
**once**, at `OpenDevice`, that persists as a constant per-tick cost
independent of any subsequent hardware or software activity on the
device -- not an ongoing servicing cost of any kind measured so far.
Checked and not pursued further this entry (small, unlikely to matter,
not chased quantitatively): `OpenDevice`'s own `DOS_LockVariable()`
calls lock only individual scalar statics (a handful of bytes each),
not a large memory region -- implausible as the source of a system-wide
10x slowdown via paging/TLB effects on a 486-class DPMI target, but not
formally measured either.

**No further real-hardware time spent chasing the IRQ7 angle** -- the
design pass itself, not a hardware cell, is what answers this one.
Acceptance gate items 4 and 5 remain FAIL.

## Not yet done

1. A genuinely new hypothesis for "a one-time OpenDevice side effect,
   independent of all subsequent activity" -- not yet identified.
   Candidates worth a future design pass: bisecting `OpenDevice`'s own
   command sequence itself (does merely issuing the DSP speaker-enable
   `0xD1` and rate/mode setup, WITHOUT ever hooking the IRQ vector or
   arming DMA, reproduce the tax? -- would need a new, more invasive
   diagnostic build, since real playback depends on both); or an
   engine-side (not SDL-backend) audit of whether AGS's own per-tick
   code branches on "is any audio player registered" in a way not yet
   measured (`audio_core_entry_poll()`'s own cost was measured, but not
   necessarily every other per-tick site that might check audio state).
2. Acceptance gate items 4 and 5 remain FAIL.
