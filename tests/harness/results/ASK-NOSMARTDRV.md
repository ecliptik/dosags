# Queued ask: boot without SMARTDRV

**Drafted 2026-09-20, NOT folded into the live RAM-disk approval.**

**Gated on the RAM-disk cell's NO-SPIKES branch only. Do not put this ask if
spikes appear.** A RAM disk is a DOS block-device driver and does not go
through `INT 13h`, so **SMARTDRV is already out of the path on the RAM-disk
arm** -- which means the cell already running disposes of it on one branch:

| RAM-disk cell | SMARTDRV |
|---|---|
| **spikes present** -- cause at the filesystem layer or above | **eliminated entirely, for free.** It sits below. This ask buys nothing. |
| **no spikes** -- cause at or below the block-device layer | still live, and this ask is the lever |

Checked before proposing rather than after, which is the same discipline as
the withdrawn save-game reframing.

## The material fact about this ask, stated first

**It is a BETWEEN-BOOT comparison.** The resident cannot be toggled at
runtime, so within-boot A-B-B-A -- the thing every cell tonight was rebuilt
to achieve -- **is not available here.** After an evening spent removing
between-boot confounds by construction, asking the operator to accept one is
the fact about this ask; everything below is mitigation, and mitigations are
weaker than construction.

## What is being asked for

**One boot-config change: comment out the single `LH C:\WINDOWS\SMARTDRV.EXE
4096 1024 C A-` line in `AUTOEXEC.BAT`, run the sweep, restore.** Same class,
same scope and same restore discipline as the RAM-disk change. One line, one
file, reversible.

## Why it is the next lever and not a variation

The A-B-B-A cell eliminated **SMARTDRV's caching of C:** and explicitly not
SMARTDRV. `SMARTDRV C-` disables caching for the drive; **the TSR stays
resident and keeps hooking INT 13h**, so a cost in its pass-through path
survived that test untouched. That is the half-candidate branch A was left
holding:

| candidate | status after the A-B-B-A cell |
|---|---|
| SMARTDRV's **caching** of C: | **eliminated** -- events survive unchanged with caching provably off and `c` moved 6.6% |
| SMARTDRV **resident in the INT 13h path** | **untested** |
| BIOS INT 13h itself | untested |
| ATA/CF controller | untested |
| CF media | untested |

**Unloading it is the only way to separate the first two**, and SMARTDRV
cannot be unloaded at runtime -- hence a boot-config change rather than
another `system()` call.

## Design

Mitigations for the between-boot weakness above, all cheap and none of them
equal to construction:

- **Four sweeps in the no-SMARTDRV boot and four in a restored boot**, same
  `FSPROBE_S1..S4` shape, so within-boot position is matched between the two
  conditions rather than confounded with them.
- **`c` is the cross-boot stability check**, calibrated at 2.7% from three
  identical-configuration runs. A cross-boot `c` difference larger than the
  within-boot spread is the signal; `c` unchanged with events unchanged means
  the lever did nothing observable.
- **`MEM` and a `SET` dump in stage 1 of each boot** as the witness that
  SMARTDRV is actually absent -- **not** the absence of a `/S` table, which
  a missing executable also produces.

## Branches, fixed now

**A -- events gone.** SMARTDRV's presence in the INT 13h path is the
mechanism. Gate 2's hold closes on a name. This is the outcome the ask is
for.

**B -- events unchanged in magnitude and base spacing.** SMARTDRV is
eliminated entirely, and branch A of the RAM-disk result narrows from four
candidates to three: BIOS INT 13h, controller, media. **No name, and the
front needs its next lever before this cell is worth running again.**

**C -- events survive, magnitude or spacing moved.** Two mechanisms, or one
mechanism whose trigger SMARTDRV shapes. Does not close the hold.

**D -- `c` unchanged between boots.** The lever is suspect: removing a
resident from the write path with no measurable effect on quiet write cost
means either it was never in the path for these writes, or the witness is
wrong. **Unscored until the witness is explained.**

## What it costs, stated honestly

Two boots, two config pushes, two restores, each verified by re-fetch and
re-diff through the same normalisation. **It is a bigger ask than the
RAM-disk cell** -- that one is one change; this is a change, a measurement, a
restore and a matched control boot.

**And it may return branch B**, which names nothing. The operator chose
"named mechanism, however long", so that is within the rules -- but it should
be said plainly when the ask is made rather than discovered afterwards.
