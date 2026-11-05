# Pre-registration: CLEARDIR -- is the 220 ms event physical or logical?

Written 2026-09-20, before the archive-and-clear. The four-cell Gate 2
treatment runs first and finishes on the current 316-entry directory, so
these figures stay comparable to FPT1 and LOGAB.

## The question

A ~220 ms event fires during writes on this volume. FSPROBE showed it is:

- **not** a FAT cluster allocation -- clusters are 32,768 bytes, the sweep
  passed straight through 32,768 and 65,536, and the three SDL logs never
  reached 32,768 at all;
- **not** directory-size dependent -- rec 8 at byte 6,400 and rec 73 at
  58,400 in *both* `C:\DOSAGS` (316 entries) and `C:\FSTEST` (empty), within
  1.5%;
- present standalone on an idle machine.

The best available account is **the CF card's own erase-block cycle, firing
at a PHYSICAL address**. It is the only proposal that explains both the
arbitrary-looking logical offsets in a scratch file and the perfectly
repeatable logical offset in the SDL log across three runs -- a file written
identically each run into similar volume state lands in the same physical
clusters, so a fixed physical boundary shows up at a fixed logical one.

**It is a hypothesis. This tests it.**

## Correction: the cross-directory result does NOT weaken the physical account

I wrote that two files in two directories hitting the same *logical* offsets
made the physical-address guess do no work. **That was wrong, and it is the
same coincidence read carelessly a second time.**

`C:\FSTEST` was created immediately after the `C:\DOSAGS` run, on a 76%-full
volume. DOS's free-cluster search resumes from where it left off, so the two
scratch files were plausibly allocated **from the same region of free space**.
If both start at similar alignment relative to an erase-block boundary, both
hit it at similar logical offsets -- which is **a prediction of the physical
account, not a refutation of it.**

So the cross-directory result is **consistent with both accounts** and
discriminates neither. It should not have been written up as evidence
against one.

**Which makes CLEARDIR sharper than either framing above.** Clearing 316
files does not just free space, it moves the free-space pointer somewhere
materially different, so the next file allocated lands at a different
alignment. The two outcomes are unchanged but the inference from them is
stronger: a same-offset result after clearing is no longer explicable by
"the files happened to be allocated next to each other", because they were
not.

## Design

1. **Archive first.** `C:\DOSAGS` holds 316 files including every `<TAG>.LOG`
   back to `HW1.LOG`; the repo's `results/` tree holds 55 cells. **For part
   of this campaign the target is the only copy.** Fetch everything, verify,
   commit, and only then delete.
2. Clear the `<TAG>.LOG` archive. The volume is **76% full** -- 14,604 free
   clusters of 61,478, 478 MB of 1.88 GB -- so clearing a few hundred log
   files frees a materially different amount of space and changes which
   clusters a new file is allocated.
3. Re-run **one ON cell** (`DOS_PORT_LOG=1`), same fixture, same gate window,
   same binary as the gate treatment. Fetch its SDL log.
4. Compare the stall's **byte offset** against FPT1's 16,103->16,861,
   LGON1's 16,141->16,899 and LGON2's 16,142->16,900.

## The two outcomes, fixed now

**PHYSICAL (hypothesis stands).** The stall lands at a **materially different
byte offset**, or disappears from the run's range entirely. A physical
boundary that used to sit under logical offset ~16.4 KB now sits somewhere
else, because the file was allocated into different clusters.

**LOGICAL (hypothesis falsified).** The stall lands at **the same ~16.4 KB
offset** on a substantially emptier volume. Then the address is logical,
something about the 16,384th byte of a written file is special on this
system, and the erase-block account is wrong. I have no candidate mechanism
for that outcome, which is worth saying in advance rather than inventing one
afterwards.

## Invalidity conditions

- If the ON cell produces no stall at all, the test is **unscored** -- an
  absent event has no offset. Re-run before concluding anything; three of
  three ON cells stalled before clearing, so an absence is itself
  informative but is not the PHYSICAL outcome.
- If the archive fetch cannot be verified file-by-file, **nothing is
  deleted.** The experiment waits. Evidence outranks the experiment that
  would consume it.
- Clearing must change **where** the allocator hands out clusters. See the
  amendment below: the original form of this condition was about the wrong
  quantity.

## Not being claimed

Directory-scan cost and this event are **different findings** and clearing
affects both. `reopen` was 21,075 us at 316 entries against 6,769 us empty
-- ~14.3 ms per `fopen` -- so after clearing, every file open on the volume
gets faster too. **That will move `init` and therefore whole-run
`tick_rate`, and it means no cell run after the clear is directly comparable
to one run before it.** The Gate 2 treatment is deliberately being run first
for that reason.


## Amendment, from sizing the archive before running it

The cached listing gives the numbers this experiment actually rests on:

| | count | bytes |
|---|---|---|
| all files in `C:\DOSAGS` | 316 | 97.5 MB |
| **`.LOG` files** | **281** | **6.1 MB** |
| largest single file | `SHARDS.AGS` | 72.8 MB |

**Only the `.LOG` files get archived and cleared.** The `.AGS` and `.EXE`
files are staged from this repo every cell and are reproducible; the logs are
not. That is 281 files and 6.1 MB to fetch, not 316 and 97.5 MB.

**And it exposes a flaw in the invalidity condition I wrote above.** At
32 KB clusters those 281 files occupy at least 9.2 MB and realistically
~18 MB of slack-inflated allocation, against **478 MB free**. That is under
4% -- **right at the "less than a few percent" threshold I set as grounds
for calling the test unscored.** Had I run it as written I would have had a
result and no way to know whether to believe it.

**The condition was measuring the wrong thing.** What matters for allocation
alignment is not how much free space exists but **where the allocator hands
out the next clusters.** Deleting 281 files written over ten days punches
holes throughout the FAT, and DOS fills the earliest hole it finds -- so the
next file created lands somewhere structurally different even though total
free space barely moves.

**Replacement condition, and it is empirical rather than arithmetic:**
**re-run FSPROBE immediately after the clear.** Its sweep spikes were at
byte 6,400 and 58,400 in both pre-clear runs.

- **FSPROBE's spikes move** -> allocation location changed, and the SDL-log
  offset comparison is meaningful. Score CLEARDIR.
- **FSPROBE's spikes stay at 6,400 and 58,400** -> the clear did not change
  what the allocator does, and CLEARDIR is **unscored**, whatever the SDL log
  says. Free more space or accept the test is not available.

That also makes FSPROBE the control for the experiment rather than just its
predecessor, which it should have been from the start.

## The control needs a stability baseline, and it does not have one yet

The pre-clear evidence for "6,400 and 58,400 are where the spikes live" is
two FSPROBE runs -- but they were **two different directories in one
session**, back to back. That establishes the offsets agree *across
directories*, which is what falsified P-DIR. It does **not** establish they
are stable *run to run*, and those are different claims.

The consequence is an asymmetry in CLEARDIR's two branches:

| post-clear FSPROBE | inference | strength |
|---|---|---|
| spikes **move** | the allocator hands out different clusters; the SDL-log comparison is meaningful | **sound** -- a move from a position held twice is a move |
| spikes **stay** | either the clear changed nothing the allocator noticed, **or** the offsets were never stable enough for a move to mean anything | **ambiguous, and not currently separable** |

**Fixing it: one more FSPROBE before the clear, in `C:\FSTEST` again.** Same
directory, same volume state, nothing else changed. If it returns 6,400 and
58,400 a third time, the offsets are stable run to run and the stay-branch
becomes interpretable. One probe cell, and it slots between the gate
treatment and the archive without competing with either.

**Recorded here in case that run does not happen or does not agree**, so the
weaker branch is labelled as weaker now rather than discovered at scoring
time. If the third run disagrees with the first two, CLEARDIR is off --
there is no baseline to compare against and the whole experiment needs
rethinking before it is worth a cell.

## Revised order

1. G2L1-G2L4, the four-cell Gate 2 treatment, on the current 316-entry
   directory so they stay comparable to FPT1 and LOGAB. **Running.**
2. FSPROBE #3 in `C:\FSTEST` -- the stability baseline.
3. Archive the 281 `.LOG` files, 6.1 MB. Verify **file by file**. The
   `.AGS`/`.EXE` files are staged from this repo every cell and are
   excluded; fetching them would be 90 MB of transfer to re-acquire what is
   already in git.
4. Clear the logs **only if every one of the 281 verified.**
5. FSPROBE #4 -- the control. Spikes move or they do not.
6. One ON cell (`DOS_PORT_LOG=1`), fetch its SDL log, compare the stall's
   byte offset against 16,103->16,861 / 16,141->16,899 / 16,142->16,900.
