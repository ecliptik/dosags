# Pre-registration: DEVICE -- is the 220 ms event the media, or something above it?

Written 2026-09-20, before the operator has ruled on the boot-config change
this needs. Fixed now so it cannot be shaped around whatever they permit.

## What is established, and why no further variation on C: can settle it

Twenty-seven observations across five probe cells:

- The event costs **217,132 - 229,526 us**. Inside 5%, every time, never
  varying.
- **Not** a FAT cluster allocation: clusters are 32,768 bytes and the SDL
  logs never reached one.
- **Not** directory-size dependent: `sync` is 1.01x between a 316-entry
  directory and an empty one.
- **Not** a fixed byte count: 28,000 bytes between events at 800-byte
  records against 19,778 at 400-byte, a **29% swing on the one coordinate a
  byte counter cannot vary.**
- **Near** a fixed elapsed period -- 445 ms against 479 ms, 1.08 -- but that
  is outside the 5% the event's own magnitude holds to.
- Detection is **intermittent**: events are observed only while a write is in
  flight, so absence is never evidence of non-occurrence. Two conclusions
  have already been retracted for missing that.

Every remaining question is about **where the 220 ms is spent**, and every
lever on this volume has been pulled.

## Design

The same sweep, to a **RAM disk** -- a device that is not the CF card and not
reached through the BIOS disk path. `FSPROBE_ORDER=none`, cumulative time on,
**record size 800** so it compares directly against the 800-byte CF run
(35.0 records, 28,000 bytes, 445 ms, lattice residual 0.0571).

**The requirement is a DIFFERENT PHYSICAL MEDIUM, and it has to be asserted
rather than inferred.** A second partition on the same CF card would have
different cluster geometry, would pass the geometry witness, would read as
"different device" -- and would **share every erase block**, discriminating
nothing. The geometry check distinguishes a different *volume*; only knowing
what the volume is backed by distinguishes a different *medium*. A RAM disk
qualifies because it is memory; a second partition does not, whatever the
geometry says.

### The layer stack this test actually cuts

| layer | replaced by a RAM disk? |
|---|---|
| DOS filesystem -- FAT, `BUFFERS`, INT 21h | **no** |
| DOS block-device layer | the RAM disk driver plugs in here |
| INT 13h BIOS disk services | **yes, bypassed** |
| ATA/CF controller | **yes, bypassed** |
| CF media | **yes, bypassed** |

The cut is between the DOS filesystem layer and everything under it. It does
**not** separate driver from BIOS from controller from media.

**Sweep length may have to shrink** if the RAM disk cannot hold 384 KB. If it
does, the CF comparison run must be re-run at the same reduced length --
comparing a short RAM-disk sweep against a long CF one would reintroduce the
multi-variable comparison that produced the RECSIZE retraction.

## Outcomes, all four fixed now

**A -- NO SPIKES.** No event over 20 ms in the whole sweep. **The cost is at
or below the block-device layer.** That is **four candidates, not one** --
the disk driver, INT 13h, the ATA/CF controller, and the media -- and a RAM
disk separates none of them from each other. It is the branch most likely to
end the investigation, so its label has to be exact: **"no spikes" does NOT
mean "the CF media", and writing it that way would retire three candidates
by wording.**

The practical consequence is the same either way -- a storage characteristic
with a known mitigation, write nothing during a timed region -- and
`HARDWARE.md` should say "at or below the block-device layer" rather than
naming the media.

**B -- SPIKES AT ~220 ms, SIMILAR SPACING.** **The cost is in DOS's own
filesystem layer or higher.** Not "DOS or the BIOS": **the BIOS is below DOS,
not above it**, and a RAM disk bypasses INT 13h entirely, so a surviving
event cannot be BIOS. A RAM disk cannot physically take 220 ms to accept
800 bytes, so a preserved magnitude implicates FAT handling, `BUFFERS=`, the
INT 21h path, an SMI or a TSR.

**`BUFFERS=` is then the natural follow-up for B, not only for C** -- it is
the tunable that sits exactly in the implicated layer. Still a second ask.

**Largest consequences, smallest prior**, and it would make the
investigation's framing wrong rather than incomplete.

**C -- SPIKES AT ~220 ms, CLEARLY DIFFERENT SPACING.** The cost lives above
the media but the **trigger** depends on the device's I/O pattern. Points at
DOS buffer policy or the BIOS disk path rather than a free-running timer.
**Scored as different if the spacing ratio falls outside 0.8-1.25** -- the
band the CF runs' own 1.08 sits inside, so C requires a bigger move than the
one already seen between two CF runs.

**D -- SPIKES OF A DIFFERENT MAGNITUDE.** A different phenomenon. **Unscored
for this question**, and the magnitude has to be explained before any
comparison means anything. Named in advance because the previous four cells
each turned up one member that refused to join the structure, and three times
in a row that member was informative rather than noise.

## Invalidity conditions

- No RAM-disk driver available without a further boot-config change: the cell
  does not run. **Do not substitute a second CF partition.**
- Fewer than 4 events in outcome B or C: the spacing is not measurable from
  three points and only the magnitude is scored.
- If the sweep length differs from the CF comparison run, **the spacing
  comparison is invalid** and only the magnitude and the presence/absence are
  scored.

## What this does not settle even in the best case

Outcome A names the media without naming the mechanism inside it -- wear
levelling, erase-block recycling, and internal ECC retry all produce a
periodic stall and none is distinguishable from outside the card. **That is
an acceptable stopping point**: a storage characteristic with a known
mitigation does not need its internal cause identified, and the port's
remedy is the same whichever it is.

Outcome B does not stop, and should not: a 220 ms stall from something above
the storage layer would affect every port on this hardware, not only one that
writes files.

## Authorization, and its exact boundary

**Approved by the operator**, chosen over three alternatives including
releasing Gate 2 now -- a deliberate decision to spend a boot-config change
on the mechanism rather than take the claim.

- **Approved:** one boot-config change to bring up a RAM disk or a second
  volume, and the same sweep run against it. **One-time, for this test only.**
  It does not open boot config generally.
- **Required:** restore the previous config afterwards, and **verify the
  restore the same way the change is verified** -- not by the transfer
  returning 0.
- **Not approved, needs a separate ask:** any other game, any card swap,
  anything outside the sweep itself.

## Verifying the config actually took -- the witness is inside the instrument

**"The machine came back up" is not proof it booted through the full new
sequence**, and a sweep that silently ran against the CF card again would
look like a clean outcome-B result and would **falsely convict DOS.** That is
the worst available failure here.

The witness is DOS-side and independent of the transfer, and `fsprobe` now
carries it:

- **`FSPROBE_PATH`** -- the sweep's path, printed, and **the drive letter in
  it is what the geometry call interrogates.** The witness sits on the
  callee. A witness that reads the *default* drive while the sweep opens an
  explicit path can have both halves individually correct and leave the cell
  void **in the flattering direction** -- a clean "different device, no
  spikes" from a sweep that ran on the CF card anyway.
- **`INT 21h AH=19h`** -- the default drive, printed alongside, so a
  divergence between it and the sweep's drive is visible rather than silent.
- **`INT 21h AH=36h`** -- called with the sweep's own drive number, not 0. The CF volume is **512 x 64 = 32,768-byte clusters, 61,478 of
  them**. The probe now compares against exactly that and prints either
  `GEOMETRY MATCHES THE CF VOLUME ... this is C:, NOT a different device` or
  `geometry differs ... this is a DIFFERENT device`.

**If the probe prints the CF geometry, the cell is void regardless of what
the sweep shows.** No result is read from a run whose device is unconfirmed.

The same two lines verify the **restore**: after the config is put back, the
next cell must report the CF geometry again.

## Operational constraints carried from standing instructions

- **Push `CONFIG.SYS` / `AUTOEXEC.BAT` via vcctrl's live `send_file` on the
  NET boot profile.** No physical CF handling -- that path is deprecated.
- **Expect the post-FTP keyboard hang at the return reboot.** Known signature
  on this target: it stops answering keys after a transfer's return reboot.
  Four-step check first, one power cycle only if genuinely stuck, and the
  script self-recovers rather than wedging.
- **Log any mains cycle.** Minimising them is a standing instruction and a
  boot-config round trip is exactly where one becomes tempting.
- **Read the existing config before overwriting it**, and keep a copy in this
  repo, so the restore is a known-good file rather than a reconstruction.

## Outcome C, expanded as asked -- the branch most likely to be live

Elapsed period was the least-bad coordinate at **1.08** while record spacing
swung **1.41**, so "same period" is not a foregone conclusion even if the
cost source is identical.

**C is scored if the spacing ratio falls outside 0.8-1.25.** That band
contains the 1.08 the two CF runs already differ by, so C requires a bigger
move than one already seen between two runs of the same device.

**What I would conclude from C, written now:** the ~220 ms cost lives above
the media -- a RAM disk cannot produce it -- but the **trigger** is not a
free-running timer, because a free-running timer would keep its period across
a change of device. The trigger would then be something that scales with the
I/O pattern: DOS's own buffer-flush policy (`BUFFERS=`), the number of INT 21h
write calls, or the BIOS disk path's per-operation work. **The follow-up
would be `BUFFERS=` varied on the CF card**, which is a config change of the
same class and would be a second ask -- not something to fold into this one.

**C would also retire the timer family**, which is currently the leading
candidate, so it is not a soft landing: it would mean the best-supported
reading at the time of writing is wrong.

## ECHO's own failure mode, named before its result is read

**The DOS environment is a fixed block -- `SHELL=... /E:1024` -- and when it
fills, the variables that fail to set are the LAST ones, not the ones
containing special characters.** Twelve probe variables plus the harness's
own is not obviously safe, and the failure mode **looks exactly like a
finding**: E1-E6 arrive intact, E7-E11 come back missing, and the conclusion
is that `>`, `%`, `^`, `&` and `,` are all eaten. **A five-character
alphabet, entirely fabricated by running out of room.**

The first ECHO cell, already on the machine, **does not carry the guards
against this** and its result is therefore provisional whatever it says:

- **E13, a repeat of E4's plain control, at the END of the list.** If E4
  survives and E13 does not, it is space or ordering and not characters. A
  known-good control on **each side** of the suspects is the general form.
- **A bare `SET`, dumped through `FSPROBE_SYS_PRE`.** Per-variable echo says
  what each variable holds; `SET` says **which variables exist at all, in
  what order, and how much room is left.** A variable that never got set is
  invisible to an echo that only prints what it finds -- the same distinction
  as a counter reading zero versus never having run, and the direct read
  rather than the inferred one.

**Scoring rule, fixed now:** if the first cell shows **any** variable missing
or altered, it is **not scored** -- the exhaustion and alphabet explanations
are not separable without E13 and the `SET` dump, and the second cell decides
it. If it shows **all twelve intact**, the alphabet hypothesis is dead for
those characters and the SEQ truncation needs a different explanation
entirely, which is itself a clean result.

**And a discipline note aimed at my own reasoning:** `%` is my bet because it
has a story -- COMMAND.COM expands `%VAR%` in a BAT file. `#` has no story
and was eaten anyway. **The plausible member of an alphabet must not set the
prior for the others**, which is exactly how the `|` diagnosis survived a
night longer than it should have.

### E14/E15: send the value that actually failed

**Nothing in E1-E13 reproduces it.** E6 has the failing *shape* at 23
characters; E12 has a long *plain* value at 100. The value that broke twice
was **72 characters with delimiters in it**, and no probe combines those
properties. So "all twelve intact" would mean only that a short delimited
value and a long plain value both survive, while the thing that actually
failed goes untested.

**We have been testing properties of the value without once sending the
value.** It costs one variable.

- **E14** = the `#` value verbatim, all 72 bytes:
  `SMARTDRV /S#SMARTDRV C- ;SMARTDRV /S#SMARTDRV /S#SMARTDRV C ;SMARTDRV /S`
- **E15** = the same with `|`, also 72 bytes.

**`FSPROBE_E14` is 11 characters, exactly the length of `FSPROBE_SEQ`** --
so the variable-name length is controlled for without a separate probe.

Three readings, fixed now:

| E14/E15 | reading |
|---|---|
| **truncated** | it is the value, and E1-E13 says which property of it |
| **intact** | it is **not** the value -- points at the variable *name*, the position in the argument list, or that cell's total environment pressure, none of which any probe currently touches, and all still live for the RAM-disk cell |
| **intact, and E1-E13 all intact too** | the failure is **not reproducible by echo**. The mangling happens somewhere the echo path does not traverse, and the RAM-disk cell's environment is safe **only if it goes through the same path the echo did** |

**The third branch is why this is written down in advance**, because it is
the one where "the probe found nothing" would otherwise be read as "the
problem is gone."

### ECHO cell 2, designed so an intact E14 is still informative

`#` is cleared, so **E14 arriving intact is now the expected outcome, not the
surprising one** -- and the three readings collapse to one: not the value, so
the variable *name*, the *argument position*, or that cell's *environment
pressure*. `FSPROBE_E14` matching `FSPROBE_SEQ`'s 11 characters rules out the
name for free, leaving two, **and neither had a probe.** An intact E14 alone
would leave me where I am with a cell spent.

So cell 2 tests position and length-with-spaces in the same pass:

| var | payload | what it isolates |
|---|---|---|
| **E1** | the 72-char `#` value, **first** `--env` | content at full length, early |
| **E2** | 72 chars, same spaces, `#`/`;` replaced by letters | **length + spaces, no specials** |
| E3 | plain 17-char control, early | ordering control, head |
| **E14** | **the same 72-char `#` value, late** | **position, against E1** |
| **E15** | the 72-char `\|` value | the control that makes E14 readable |
| E13 | plain 17-char control, **last** | ordering control, tail |
| `FSPROBE_SYS_PRE=SET` | -- | which variables exist at all, and room left |

**E1 versus E14 is the position test**: identical content, different `SET`
order. **E2 is the length-with-spaces test**: if E14 truncates and E2 also
truncates, it is length and whitespace rather than content; if E14 truncates
and E2 survives, it is content at that length.

**E15 is what makes any of it readable.** If E15 truncates at 11 and E14 does
not, the harness path is confirmed identical to the one that broke, and an
intact E14 genuinely exonerates the value rather than meaning the probe
missed the path.

### The residue, which is not closed

Even with `#` cleared, **the `#` run's truncation stands unexplained**: a `#`
split gives four stages, a `|` split gives one stage of three `;` commands,
and **what ran was one command and one sweep -- neither.** That is the same
environment path the RAM-disk cell will use. **It needs an answer before the
approval is spent**, and cell 2 is the attempt.

### Confound in the position test, caught before the result is read

**`FSPROBE_E1` is 10 characters and `FSPROBE_E14` is 11.** The E1-versus-E14
comparison -- the position test, which now carries the whole question since
content is expected to survive -- **varies name length as well as position.**
And name length is live precisely because I invoked it one message earlier to
rule the name out for E14.

**Cell 2 is already on the machine, so this is handled by reading rather than
re-running.** The confound only bites **if E1 and E14 disagree**:

- **E1 and E14 agree** -- position and name length are both cleared together,
  and the confound is moot. Everything else in the cell (E2's
  length-and-whitespace separation, E15's path control, E13's tail control,
  the `SET` dump) is unaffected either way.
- **E1 and E14 disagree** -- **the position result is NOT scored**, because
  two variables moved. A re-run uses **E10 against E14**, both 11 characters,
  matching `FSPROBE_SEQ` exactly, with position the only difference. No code
  change needed: the echo loop already covers E1..E16 and `FSPROBE_E10` is
  the same length as `FSPROBE_E14`.

**And the payload budget went up.** Four 72-byte values is ~288 bytes plus
names against a 1024-byte block -- materially more pressure than cell 1
carried. **E13-last is the control for exactly that**, and it matters more
now than when it was first added: if E13 is missing while E3 (identical
content, head position) survives, the cell hit the block and nothing about
characters or positions can be read from it.

## SIZING CORRECTION: the cell as designed would have returned branch A whatever is true

**A byte-matched RAM-disk arm cannot fail.** The C: arm writes 480 records at
a measured `c` of ~6,400 us = **3.07 s**, and events arrive at ~436 ms, which
is the ~7 seen. A RAM disk accepts a record in tens of microseconds:

| RAM-disk per-record cost | 480 records takes | expected periods at 436 ms |
|---|---|---|
| 50 us | 24 ms | **0.06** |
| 100 us | 48 ms | **0.11** |
| 200 us | 96 ms | 0.22 |

**A tenth of one period. Zero spikes is guaranteed by construction and
indistinguishable from the finding** -- it would read as "no spikes on a
different medium", clear four candidates at a stroke, close branch A, and be
worth nothing. **The most expensive false negative available, bought with the
one approved boot-config change.**

### Fix: terminate the sweep on TIME, not bytes

`FSPROBE_SWEEP_MS` runs the sweep for a wall-clock duration and lets the
record count fall out of whatever the device costs -- **measured in the same
run, never assumed**, because the conversion constant changes by two orders of
magnitude across the very change under test. That is the `c400` lesson applied
before the cell instead of after it.

`FSPROBE_WRAP_KB` rewinds to offset 0 at a set size, because time-matching a
RAM disk to a 3-second CF arm needs **25-50 MB** of writes and no RAM disk
here will hold that. **Both arms use the same wrap**, so the write pattern is
matched between them rather than differing with the device.

`FSPROBE_P1..P8` gives each stage its own path, so **C: and the RAM disk
alternate within one boot.** Without it the comparison is between-boot, which
is the confound every cell tonight was rebuilt to remove.

### Three things fixed before the cell

**Minimum arm duration.** An arm shorter than **8 expected periods (~3.5 s)**
makes the no-spikes branch **NOT SCORABLE**. "No events in an arm too short to
contain one" is not evidence of absence, and it must not be allowed to land as
branch A. Same shape as P-PERIOD's 5-event floor.

**Expected-events figure, computed before the run from the C: arm's own
rate.** At 436 ms a 6-second arm expects **~13 events**. Zero observed against
13 expected is a result; zero against 0.1 is nothing. **The expected figure is
reported alongside the observed one in the scoring, always.**

**Branch C is retired for this cell.** A period comparison between arms whose
per-record costs differ by two orders of magnitude cannot use the 0.8-1.25
band on records, and the time-based period is the only coordinate that could
transfer -- which is not enough to rest a branch on. **This cell scores
presence versus absence only.** The period questions go rather than be made
unsound.

## The wrapped C: arm is a positive control that MUST fire

`FSPROBE_WRAP_KB` solves the RAM disk's capacity problem and **changes the
write pattern while doing it.** Every observation of this phenomenon has come
from a **monotonically growing file**; a wrapped file rewrites one region
repeatedly -- different logical positions, different allocation behaviour,
possibly different physical mapping. **We do not know the events survive
that**, and the one relevant fact cuts both ways: position *does* reproduce
across identical runs (six of seven records matched), so position is not
irrelevant, so resetting it is not obviously harmless.

**Two silent arms cannot distinguish "the wrap killed the phenomenon" from
"the device does not matter."** Only the C: arm separates a null result from
a broken instrument.

**Bar, from the unwrapped runs' own rates.** Five arms at 384 KB / ~3.15 s
gave 6, 7, 10, 11 and 14 events -- **1.90 to 4.44 events/s**. A 6-second
wrapped C: arm therefore expects **11 to 27 events**.

- **Wrapped C: arm produces >= 5 events** -- generous against an 11-27
  expectation, and far from zero. The instrument works under wrapping and
  the RAM-disk arm is readable.
- **Wrapped C: arm produces < 5 events** -- **THE CELL IS VOID.** Nothing
  about the RAM disk can be read from it, whatever that arm shows.
- **Rate outside 1.0 to 5.5 events/s** -- the phenomenon survives but the
  wrap changed it. **A finding about the wrap in its own right**, recorded
  even though it complicates the cell, and the RAM-disk comparison is then
  read with that caveat attached rather than silently.

## RETRACTED -- the blocker below was a one-directory search, not a card search

**`DIR C:\DOS\*.SYS` is not a search of the card**, and concluding "no
RAM-disk driver on the machine" from it is the same conflation this campaign
has been catching all night: *absent from the directory I looked in* and
*absent from the machine* are different statements.

**Windows 3.x ships its own `RAMDRIVE.SYS` in the Windows directory, and this
machine demonstrably has a Windows install** -- `AUTOEXEC.BAT` loads
`C:\WINDOWS\SMARTDRV.EXE`. A whole-volume search is running:
`DIR C:\RAMDRIVE.SYS /S`, `DIR C:\WINDOWS\*.SYS /W`, `DIR C:\*.SYS /S /B`.

**If it is there the provenance question evaporates.** It is the machine's own
file, already licensed by whoever licensed that install, and pointing a
`CONFIG.SYS` line at a driver already on the card is squarely inside standing
authorization -- no ask, no sourcing decision, and the cell runs tonight.

**A floppy was considered as the different medium and is rejected on
instrument grounds, not availability.** Seeks and motor spin-up land at
roughly 100-200 ms, **overlapping the ~220 ms phenomenon directly.** An
instrument whose own native latencies sit inside the signal's band cannot
measure it.

The section below is kept as written, wrong conclusion included.

## (RETRACTED) BLOCKER: there is no RAM-disk driver on the card

`DIR C:\DOS\*.SYS` returns **one file: `HIMEM.SYS`, 29,136 bytes.** No
`RAMDRIVE.SYS`. And no copy exists anywhere in the local working trees --
`~/git` and `~/emulators` contain no `ramdrive*`, `xmsdsk*`, `tdsk*` or
`srdisk*`.

Capacity is not the problem: `MEM` reports **43,296 KB of XMS free**.

**This is a pre-registered invalidity condition and I am not routing around
it:** *"No RAM-disk driver available without a further boot-config change:
the cell does not run. Do not substitute a second CF partition."*

**And the second CF partition remains barred for the reason already
recorded** -- it would pass the geometry witness, read as a different device,
and share every erase block, discriminating nothing.

### What is actually available, checked rather than assumed

| candidate | writable? | different medium? | verdict |
|---|---|---|---|
| `RAMDRIVE.SYS` | yes | yes | **not on the card, no local copy** |
| second CF partition | yes | **no** | barred, discriminates nothing |
| ATAPI optical (E:) | no | yes | read-only, useless for a write sweep |
| PicoGUS USB CD (D:, VIBRA only) | no | yes | read-only |

**There is currently no writable non-CF volume on this machine and no driver
to make one.**

### What that changes

Obtaining `RAMDRIVE.SYS` means sourcing an MS-DOS 6.22 system file, and
**provenance is not something to guess at** -- the same rule that stopped the
`CONFIG.SYS` being reconstructed from the sibling repo. Staging a file is
inside standing authorization; **choosing where that file comes from is not a
decision to make quietly.**

So the RAM-disk cell is **blocked, not failed**, and the operator's approval
is **unspent**. Under ruling 1 the front does not close on this; under the
agreed sequencing, this is the point where **Gate 3's lower-resolution work
opens** rather than a sixth variation being manufactured. The RAM-disk cell
resumes the moment a driver with clean provenance is available.

## Fourth guard against a false branch A: the arm must prove it wrote

The RAM disk is **2 MB** and the time-matched arm pushes **25-50 MB** through
it, relying on the wrap to stay inside capacity. **If the wrap is
misconfigured or a write fails, the arm goes quiet -- and a quiet arm is
exactly what branch A looks like.**

`fwrite` to a full DOS volume does not crash; it returns short. A probe that
does not check loops happily, writes nothing, completes in good time, and
reports zero events -- **branch A's exact signature from an arm that never
wrote a byte.** And an `fsync` that fails costs nothing, which would flatten
the very distribution being sampled.

Both are now asserted per arm and printed:

    fsprobe: INTEGRITY attempted=N written=M short_writes=X sync_fails=Y -> OK | ARM VOID
    fsprobe: free bytes on the sweep drive: start=... end=...

**Any mismatch voids the arm -- not branch A, void.** Same contract as
`FSPROBE_STAGES`: the instrument refuses rather than reporting a plausible
number. And the free-space pair distinguishes **"the wrap is working"** from
**"the wrap never triggered because the arm was shorter than I thought."**

### Four guards for one shape, which is the right amount

This cell has now needed four separate protections against a single failure
mode -- **the failure and the finding produce identical output**:

| guard | the false branch A it blocks |
|---|---|
| time-matched arms | an arm too fast to contain one period |
| wrapped C: positive control | the wrap having killed the phenomenon |
| not-scorable duration floor | an arm too short to contain an event |
| **integrity assertion** | **an arm that never wrote** |

That is not over-engineering. **It is what an absence costs when it is the
interesting answer** -- every one of these would read as a clean result, and
none of them would be one.
