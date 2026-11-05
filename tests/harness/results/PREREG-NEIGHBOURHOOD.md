# Design + risk: the neighbourhood map

**Written 2026-09-21. NOT RUN. This needs an operator decision because it is
categorically different from every cell of this campaign.**

## What it would settle -- the name the ruling asks for

Write every sector in a range around a known stalling address and record
which stall:

| result | mechanism |
|---|---|
| **stalls come in RUNS at aligned boundaries** | **a worn erase block**, and **its size falls out of the run length** |
| **exactly one sector stalls, neighbours clean** | **a remapped bad block** |

That distinction is the name. Everything else in this investigation
narrows; this one names.

## Why it is categorically different from every cell so far

**Every write this campaign has made went through the filesystem to a file
we created.** This writes **raw `AH=03h` to a chosen CHS**, bypassing DOS
entirely, landing on whatever occupies that sector **now**, on the boot
drive of a machine that **cannot be physically re-imaged** -- CF handling is
deprecated and the only copy of its configuration is the one fetched
tonight.

**That is the risk, stated without softening: a wrong CHS calculation
overwrites live filesystem data and the machine may not boot.**

## The mitigation: write only to sectors the FAT says are FREE

Delete the probe's scratch file, re-read the FAT, and **restrict every raw
write to clusters marked free.** A free cluster belongs to nobody; writing
it corrupts nothing, and DOS overwrites it whenever it next allocates.
**That converts "raw writes to the boot drive" into "raw writes to
unallocated space".**

Three conditions on top, each from a failure this campaign has already paid
for:

1. **Verify freshly, per sector, immediately before each write.** Not once
   for the range at the start. A range checked and then written over many
   seconds is a range whose status is being **assumed** -- the retained-
   reading error that `vcctrl_file_list` has a rule about.
2. **Refuse and abort on the first sector that is not free.** Not skip it.
   **A skip means the CHS arithmetic and the FAT disagree**, and continuing
   past that is typing blind -- the same judgement vcctrl made when it
   aborted rather than type into an untrusted prompt.
3. **Write a recognisable pattern**, so that if something does land where it
   should not, the damage is **identifiable rather than anonymous**.

## THE CHECK THAT MAY SINK IT, done first

**The stalling sectors are inside the probe file's own extent, so their
neighbourhood is probably allocated.** Deleting the file frees it -- **but
whether the freed clusters actually cover the addresses to be mapped is an
open question, not an assumption.**

**So the first step is read-only and decides whether the test exists:**
delete the scratch file, read the FAT, and report **for each address to be
mapped whether its cluster is now free**.

- **All free** -> the test is possible as designed.
- **Some allocated to other files** -> **say so and stop.** Narrowing the
  range until it fits would be choosing the sectors that make the test
  possible rather than the ones that answer the question -- and a
  neighbourhood map of a neighbourhood chosen for convenience does not
  distinguish a run from a remap.

## Blocking dependency

**The geometry is still not in hand.** `AH=08h` returns CF=1 AH=07 under
DOSBox-X; the hardware value arrives with the read-test cell now running.
**Without it, CHS-to-LBA and LBA-to-cluster cannot be computed, and every
FAT check above depends on that arithmetic being right.**

**This design cannot be executed before the geometry is measured**, and the
FAT arithmetic must then be validated against a known address -- the probe
file's own first sector, whose cluster is known from its directory entry --
before any write is issued.

## THE ASK IS HELD -- the read cell may make all of this unnecessary

**If reads stall at the same addresses, the neighbourhood can be mapped with
READS.** No raw writes, no free-cluster mitigation, no
CHS-arithmetic-must-be-perfect-or-the-machine-dies, **no operator decision at
all** -- and an `AH=02h` against an address that turns out to be wrong costs
a wasted read.

| read result | consequence for the map |
|---|---|
| **reads stall too** | map it **read-only**. **Ask withdrawn.** And it says the cost is in *reaching* the media, not in programming |
| **reads fast, writes stall** | cost is in **programming**; the map needs writes, and this design and its ask go to the operator |

**So the ask does not go out until the read cell returns.** Half the time it
is moot, and **asking for a dangerous capability that turns out to be
unnecessary spends the operator's attention for nothing.**

## Arithmetic validation: a marker round-trip, not a derived cluster number

My first plan was to validate against the scratch file's starting cluster
from its directory entry -- **which I had already established is not in the
documented FindFirst fields on DOS 6.22.** Building the safety validation on
an undocumented field is the same error as building the extent check on
`AH=440Dh` minor 60h.

**Better, and it needs no undocumented field:**

1. Write a **recognisable pattern** to a known offset of the scratch file,
   **through DOS**.
2. Compute where that offset should live: geometry -> CHS -> absolute
   sector.
3. Read that absolute sector back with **`INT 25h`** -- an absolute **read**,
   harmless.
4. **Check the pattern is there.**

**That tests every step at once** -- geometry, CHS-to-logical,
logical-to-cluster, and the file's actual placement -- and **it fails loudly
on an error anywhere in the chain**, including an error in the geometry
about to arrive. A derived cluster number tests one link and assumes the
rest.

**If the marker is not where it was computed to be, abort before any write,
with a concrete mismatch rather than a suspicion.**

## What I am asking for -- once the read cell says it is still needed

**Not approval to run it.** A decision on whether the mitigated form is
acceptable at all, after the free-cluster check reports whether the
neighbourhood is even reachable.
