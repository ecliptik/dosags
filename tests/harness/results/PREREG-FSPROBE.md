# Pre-registration: FSPROBE -- is the stall a FAT cluster allocation?

Written 2026-09-20, before the probe runs. LOGAB has the machine.

## What is being tested

FPT1 and LGON1 both stalled on the write that crossed **16,384 bytes** --
FPT1's batch spanning 16,103 to 16,861 and LGON1's 16,141 to 16,899, on
different binaries, at the same flush index and the same tick. The account
is a FAT new-cluster allocation on a 16 KB-cluster volume.

**The cluster size is inferred from that coincidence and has never been read
off the volume.** Nothing in this repo records it, which makes it an unknown
constant sitting underneath every disk timing this project has taken.

## Design

`fsprobe.exe`, run twice by the BAT from two directories: `C:\DOSAGS`
(316 entries) and a fresh empty one. The exe takes no arguments.

- `INT 21h AH=36h` before and after the sweep: bytes/sector,
  sectors/cluster, total clusters, free clusters.
- Arms 1-4: `fprintf`, `+fflush`, `+fsync`, and open-write-close, 200
  iterations each, min/mean/max.
- Arm 5, the sweep: 800-byte records -- close to the ~900 the SDL log writes
  per batch -- appended out to 96 KB with an `fsync` each, every record
  timed individually, every record over 20 ms printed with its end offset.
  96 KB covers the 16K, 32K and 64K crossings in one pass. Record 1 is
  always printed whether it spikes or not.

## Predictions

**P-POS (position).** Spikes land on records whose write crosses an exact
multiple of the cluster size `AH=36h` reports, and on no others.
- Falsified by spikes at non-multiples, or by no spikes at all in 96 KB.
- **If the reported cluster size is not 16,384**, the byte coincidence in
  FPT1/LGON1 needs a different explanation and the mechanism in PLAN.md is
  not established. That is the outcome I most want to know about, and it is
  why this probe exists.

**P-MAG (magnitude, and this is the part position alone cannot test).**
Each boundary crossing costs **the same**: across **all crossings the sweep
produces**, the last costs **no more than 1.3x the first**, and there is **no
monotonic rise** across them. An allocation is a fixed operation: find a free
cluster, write the FAT sector, write the chain link.

*Stated as a trend across all crossings, not as a band on each, because a
band cannot discriminate what this test exists to discriminate: 230 / 300 /
400 ms is within a factor of two at every step and is unmistakably
increasing. A per-crossing envelope would pass and leave the question
unanswered.*

*Stated as "all crossings the sweep produces" rather than a fixed count,
because the count depends on the number being measured: 96 KB gives six
crossings at 16 KB clusters (16/32/48/64/80/96), twenty-four at 4 KB, three
at 32 KB. Six is comfortably enough to separate flat from rising; three is
weak, and if `AH=36h` reports 32 KB the sweep should be re-run longer before
P-MAG is scored at all rather than scored on three points.*

- **If the cost rises monotonically, the FAT free-cluster scan is
  lengthening**, and that is a different finding with a different lifetime:
  the cost gets worse as the volume fills, every measurement this project
  takes drifts with disk usage, and the 316 accumulated log files matter
  after all -- **not through directory scanning, which the `init` analysis
  ruled out, but through free-space fragmentation.** The `init` null was
  about the wrong mechanism; this tests the right one.
- Committing to **constant** as the prediction. Increasing would be the more
  interesting result -- it is the one that reframes the null and implicates
  the 316 files -- and I am not hedging toward it.

**P-FIRST.** Record 1 costs **more** than a mid-file boundary crossing.
`fopen("wb")` creates a zero-length file with no clusters, so record 1
allocates the first cluster *and* writes the starting-cluster field into the
directory entry; later crossings only extend the chain.
- Falsified if record 1 is comparable to the later spikes, which would mean
  the directory-entry write is free relative to the FAT work.

**P-DIR.** Arms 1-4 and the sweep cost the same in `C:\DOSAGS` as in the
empty directory, within the noise of the arms themselves.
- This is the precise version of the `init` null, at a 316-vs-0 contrast
  instead of 2x. A difference here reopens the directory question.
- A difference in the **sweep** but not in arms 1-4 would point at free-space
  state rather than directory size, since both runs share one volume.

## Invalidity conditions

- `AH=36h` returning `AX=0xFFFF` -- invalid drive -- leaves every prediction
  unscored, because all of them are stated against the reported cluster size.
- Fewer than two spikes in 96 KB: P-MAG is unscored, since a shape needs at
  least two points. P-POS may still score.
- The two directories must be on the **same volume** for P-DIR to mean
  anything about directory size rather than about two different filesystems.

## What this does not retire

**The 32,768-byte game-run prediction stands as written.** It was stated
before the fact against the real writer and the real volume state, and a
probe confirming the mechanism is not the same evidence as a gate cell
exercising it. Both get scored.
