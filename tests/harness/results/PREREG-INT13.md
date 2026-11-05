# Design + pre-registration: the INT 13h timing hook

Written 2026-09-21, before any code. **The first instrument in this
investigation that can NAME the mechanism rather than eliminate another
candidate.**

## What it decides

Branch A left four candidates at or below the block-device layer: the DOS
block driver, `INT 13h`, the ATA/CF controller, the media. **Timing every
`INT 13h` call splits them in two, and one of the halves comes with a
physical address.**

| where the stall sits | conclusion | what it hands over |
|---|---|---|
| **INSIDE a call** | the controller or the media | **the sector number** -- a PHYSICAL address, which is the thing five cells could never reach and which tests the erase-block hypothesis directly |
| **BETWEEN calls** | the block driver **above** `INT 13h` | SMARTDRV becomes the prime suspect rather than a queued one |

No boot-config change. It is a program, inside standing authorization.

## Mechanism: a real-mode TSR, not DPMI interception

**Decided early and deliberately, because this is the hard part.**

The probe is a DJGPP protected-mode program. Hooking a *real-mode* vector
from protected mode is possible (`__dpmi_get_real_mode_interrupt_vector` and
its setter, with a real-mode callback) but the callback path is an expensive
mode transition **on every call**, which violates the third requirement
below -- the instrument would become the cost.

**So: a small real-mode TSR, assembled or written in real-mode C, loaded
before the probe runs.** It hooks `INT 13h`, times each call with a cheap
real-mode clock, keeps a fixed ring of records in its own resident data, and
exposes them through a private `INT 2Fh` multiplex function that the DJGPP
probe calls once at the end to read them out.

That keeps the per-call cost to a counter read and a compare, and keeps all
the mode-switching out of the interrupt path entirely.

## Three requirements, each from a lesson already paid for tonight

### 1. Verify the hook FIRES before trusting a zero

**A hook that never installed reports no long calls, which is
indistinguishable from a stall that lives elsewhere** -- the zero-counter
rule, on the branch that would end the investigation.

- The TSR keeps a **total call counter**, not only a slow-call ring.
- The probe reads it and **refuses to score if it is zero**, exactly as
  `FSPROBE_STAGES` refuses a truncated stage list.
- The installer reports whether the vector it replaced was the one it
  expected, and the probe prints both the pre- and post-hook vector.
- **Positive control:** the sweep does thousands of `fsync`'d writes. A total
  call count in the low thousands is consistent; **a count of zero means the
  hook is not in the path and the cell is VOID, not "no long calls".**

### 2. Assert the parts sum to the whole

Time inside `INT 13h` plus time outside it must reconcile against the
per-record `c` already measured to **2.7%** across three runs.

- Per sweep record, the probe records total elapsed (it already does) and the
  TSR's accumulated in-`INT 13h` time for that record.
- **Printed as a reconciliation line with a residual**, the same shape as the
  `uclock` vs summed-per-record cross-check that already agrees to 0.7%.
- **A residual outside 5% means the instrument is wrong and nothing is read
  off it.** Not adjusted after the fact -- 5% is fixed here, chosen against
  the 2.7% the quantity is already known to vary by.

### 3. The clock must be safe in an interrupt path and cheap

`uclock()` is a DJGPP libc call and is **not** callable from a real-mode
interrupt handler.

**Use the PIT directly**: latch counter 0 with a `MOV AL,0` / `OUT 43h` and
two `IN 40h` reads. That is a handful of I/O port accesses, microsecond
resolution, no libc, no DOS, no mode switch, reentrant enough for this use.

**CORRECTED BEFORE ANY CODE -- the original design here would have discarded
100% of the phenomenon.** PIT counter 0 wraps every **54.9 ms** and the stall
is **~220 ms**, so **every single event spans four wraps.** "Discard a
wrapped record rather than report a 55 ms event" is the right instinct for a
60 ms event and catastrophic for this one: it would throw away every stall
and return a clean, guarded, honest-looking **H-BETWEEN**. Sixth instance
tonight of an arm that cannot fail in the informative direction, and the
first one I wrote into a design document as a feature.

**COMPOSE, DO NOT DISCARD.** Read the BIOS tick count at `0040:006C` as the
high-order part and the latched PIT residual as the low-order part -- an
unbounded monotonic timestamp at ~0.84 us resolution. Resolve the race by
reading the tick, latching, reading the tick again, and re-reading if it
moved. **Wrapping then carries information instead of destroying it.**

**The hazard that remains:** if `INT 13h` runs with interrupts disabled for
part of a call, the BIOS tick does not advance and the composed timestamp
undercounts. **The parts-sum-to-whole reconciliation is what catches that,
so it is a HARD GATE and not a printed residual.**

## RE-REGISTERED: the hook sits FIRST in the chain, which changes what its
## branches mean

`__dpmi_set_real_mode_interrupt_vector` puts this hook **ahead of everything
else on the vector**, including SMARTDRV:

    DOS FAT layer -> [this hook] -> SMARTDRV -> BIOS INT 13h -> controller -> media

**So H-INSIDE narrows the four candidates by ZERO.** "Inside the call" means
anywhere from SMARTDRV downward -- which is exactly the four that survive
branch A. **H-INSIDE must not be read as progress on the candidate list**, and
the queued no-SMARTDRV ask is still the only thing that separates the top
one.

**And H-BETWEEN would contradict the RAM-disk cell rather than answer it.**
Above this hook are DOS's FAT layer and the application -- **the layers that
were identical on both arms** when one produced fourteen events and the
other zero. A stall there cannot be device-dependent. **So H-BETWEEN is not
a branch pointing at the driver; it is two cells disagreeing, and it
registers now as "resolve the contradiction before concluding anything".**

## The actual payload: four things the RAM-disk cell could not give

INSIDE-versus-BETWEEN is a **consistency check on the previous cell**, and it
is close to determined already. The hook is worth a cell for these:

1. **The sector number.** `CX`/`DX` carry cylinder, head and sector, so a
   stalling call has a **physical address** -- the first time in this
   investigation anything has. It tests the erase-block hypothesis directly:
   **do stalling sectors cluster on a boundary?**
2. **The function code.** `AH` says read, write, verify, or extended. **Which
   operation stalls** has never been observable.
3. **One call at 220 ms, or many summing to it.** *This* is the
   wait-versus-work discriminator, and it needs no phase and no tick
   arithmetic.
4. **The duration distribution at 0.84 us resolution**, against the 5%-rigid
   figure every previous result has rested on. 118 events measured through
   the file layer said 215,712-241,541 us; this measures the call itself.

## Reconciliation: what "inside INT 13h" includes

Because the hook is first in the chain, **in-call time legitimately includes
SMARTDRV's own work.** That is correct for parts-summing-to-whole against
`c`, and it is **stated in the probe's own output** so a later reader cannot
take "time inside INT 13h" to mean "time in the BIOS".

## One free stage: the SMARTDRV toggle, within a boot

`INT13P_SYS_MID` runs a command between two identical passes, so the sweep
runs once with the cache on and once with `SMARTDRV C-`, **in one boot** --
the same discipline as the A-B-B-A cell, and the toggle is already proven to
work.

**It cannot eliminate SMARTDRV-as-resident** (`C-` disables caching; the TSR
stays in the chain). **What it gives is whether the stalling call's duration
changes when the cache is bypassed** -- a real datum about a candidate that
is otherwise untouchable without the operator ask.

## What this does NOT settle

Even H-INSIDE names the layer and the address, **not the mechanism inside the
card.** Wear levelling, erase-block recycling and internal ECC retry all
produce a slow sector and none is distinguishable from outside. **That is an
acceptable stopping point for a port** -- the mitigation is the same -- but
ruling 1 asks for a named mechanism, and "the media stalls on these sectors"
is a named mechanism at the resolution this hardware permits.


## The tick-quantization observation: tested against existing data, and the test is CIRCULAR

The claim: event magnitudes are whole multiples of one BIOS tick
(54,925.4 us), which would make the cost **a wait rather than work** -- a
timeout-and-retry loop, fitting the rigid magnitude, the device dependence
and the indifference to position and bytes.

**Tested on 121 individual events rather than on four arm means**, because
means of ~10 events cluster at the centre by construction:

| group | n | ticks | mean | sd |
|---|---|---|---|---|
| rounds to **4** | **118** | 3.9274 - 4.3976 | **4.0142** | 0.063 |
| rounds to **8** | 3 | 7.8527 - 7.9732 | 7.9016 | 0.063 |

118 of 121 at four ticks and 3 at eight looks decisive. **It is not.**

**The 4-group spans 0.470 ticks -- less than one tick wide.** A distribution
narrower than one tick **cannot straddle two integers**, so "they all round
to 4" is **guaranteed by the narrowness** and is not independent evidence of
anything. The magnitude was already known rigid to ~5%, and 5% of four ticks
is 0.2 ticks. **The fit is circular.**

**What survives is one number**: the 4-group's mean sits at **4.0142 ticks,
0.36% off exactly four.** Under a null where the true mean is uniform over
[3.5, 4.5] ticks, landing that close to an integer has probability ~3%.
Suggestive, single, and the tick was chosen as the unit **after** seeing the
data -- which is the shape the lattice p-value already died of tonight.

### So it is neither confirmed nor dropped, and the hook gets a NON-circular test

**Duration clustering cannot settle it** -- any sufficiently rigid magnitude
clusters at whichever integer it happens to sit near.

**Alignment can.** A tick-driven wait begins and ends on **tick edges**; work
that merely happens to take ~4 ticks does not. With composed absolute
timestamps the hook records, for every slow call, **the phase of its start
and end within the tick** -- i.e. `(timestamp mod 54,925.4) / 54,925.4`.

- **Phases cluster near 0** -> the cost is tick-driven. **A wait, not work.**
  The quantization observation is confirmed by a test that could have
  refuted it.
- **Phases are uniform** -> the 4.0142 was a coincidence across a narrow
  distribution, and it is dropped.

**That test is free** -- it is the same timestamps the hook already needs --
and unlike duration clustering it can fail.

## The count-to-4 wait is already dead, and the phase test's uniform branch is narrower than I wrote

**Restore confirmed first:** the card's `CONFIG.SYS` is byte-identical to the
verbatim original -- 1,041 bytes, 38 lines, no `RAMDRIVE` line. The
`CAPS LOCK LED READ ON WHILE TYPING` flag the daemon raised on the restore
send corrupted nothing.

**And the obvious tick-driven model is refuted by data already in hand.**
For `t0 = tick; while (tick - t0 < 4);` with start phase uniform, the fourth
edge arrives at `(4 - phi)` ticks:

| | count-to-4 predicts | observed (118 events) |
|---|---|---|
| duration | **uniform on (3, 4] ticks** | 3.9274 - 4.3976 |
| mean | **3.50** ticks (192,239 us) | **4.0142** (220,484 us) |
| mass below 3.93 | ~93% | **none** |
| values above 4.00 | **impossible -- bounded above** | about a third of the span |

**A count-to-4 wait cannot exceed four ticks and cannot mean 4.01.** Dead.

### So the phase test's branches are rewritten

- **End-phase near zero** -> tick-*edge*-driven after all, which then has to
  explain a duration distribution **a tick-counting loop cannot produce.**
  Interesting and contradictory, **not a clean confirmation.**
- **Phase uniform** -> the 4.0142 was a coincidence across a narrow
  distribution and **the BIOS-tick unit is retired.** That is all it means.

**A uniform phase does NOT establish "work rather than wait", and
pre-registering that now is the point.** A fixed-duration wait clocked by
**anything other than the BIOS tick** -- an RTC delay, a controller timeout,
a microsecond-calibrated busy loop -- produces exactly what is observed: a
**narrow** duration and a **uniform** phase. That hypothesis is untouched by
the phase test and is **more plausible than the tick model ever was**: a
rigid ~220 ms that survives on one device and vanishes on another is the
shape of a timeout constant in the ATA path.

**What actually distinguishes wait from work is the hook's primary output,
and it needs no phase at all:**

> **~220 ms inside ONE `INT 13h` call, with the drive idle -> a wait.
> Spread across many transfers -> work.**

Keep the phase test: it is free and it retires the tick unit cleanly. **Do
not let its uniform branch be read as a result about work versus wait** --
that would be over-reading a null exactly as a quiet arm would have been.

## The repetition question, pre-registered before the second run is read

**The probe's workload appends 400 records without wrapping**, so within one
run each sector is written once -- **repetition across sectors is not
available from a single pass of this program.** (`FSPROBE_WRAP_KB` belongs
to `fsprobe`, not to `int13p`; the wrap argument applies to the sweep cells,
not to this one.) **Stated plainly so the question is not credited to data
that cannot carry it.**

**What IS available, and it is the stronger form: CROSS-RUN repetition.**
Run 1's fourteen stalling addresses are on disk. If run 2 stalls on **the
same** CHS addresses, that is a physical property of those locations
confirmed on independent evidence. If run 2 stalls somewhere else entirely,
on sectors run 1 wrote without incident, **the property is not of the
location.**

**THE SUPPORT CHECK COMES FIRST, AND IT GATES THE NO-OVERLAP ROW HARDEST.**
I originally attached support-checking only to the partial-overlap row. That
was backwards: **no-overlap is the row that would relocate the whole
investigation, so it is the one that most needs its confound excluded**, not
the least. And the confound is live -- DOS allocates on first fit against
whatever free-cluster state exists, and since run 1 this volume has had a
`CONFIG.SYS` written, a RAM-disk cell run, and a restore pushed.

Run 1 has no histogram, but its fourteen stalling addresses place its file in
**cylinders 730-737 plus cylinder 0**, which is enough to say whether the
extent moved.

| run 2 support | stalling sectors | reading |
|---|---|---|
| **same extent** | **same** | **"where"** -- a property of those physical locations, on independent evidence |
| **same extent** | **different** | **"when" is live** -- same physical ground, different outcomes. A cycle count, a wear-levelling trigger, a housekeeping pass |
| **extent MOVED** | different | **UNINTERPRETABLE.** Not evidence for "when" -- just a different file. **Scored as nothing.** |
| same extent | partial | both, or mixed allocation -- read neither without the per-cylinder support |

**One caveat on resolution, registered now.** Cylinder granularity here is
roughly 500 KB, **the same order as a CF erase block**, so a per-cylinder
rate is a **first cut, not the resolution the mechanism lives at**. The slow
ring carries sector-level detail for the numerator while the histogram is
per-cylinder for the denominator, and that asymmetry is fine -- but **a flat
per-cylinder rate must not be read as "no structure"**, because the
structure could sit entirely inside one cylinder.

**And the mechanism boundary stays attached to whatever this returns:** one
long ATA wait and a BIOS retry sequence are indistinguishable from above
`INT 13h`. The erase-block reading assumes the first. **The operator's
ruling asks for a name, and "a wait of unknown internal cause inside a
single-sector write" is not yet one.**
