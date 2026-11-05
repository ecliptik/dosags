# Pre-registration: FPT1 -- locating the ~250 ms present stall

Written 2026-09-20, BEFORE the cell runs. Scored honestly afterwards.

## What is already known

- BENCH8 gate-window runs show ~2 present stalls of ~250 ms each, clocked in
  REAL time (3 ms of spread across independent runs, ~20.1 s apart). The
  present's ordinary CPU share on BENCH8/Mode 13h is 4.9%, so the stall is
  18.7x over-represented -- it is not the present getting slower, it is a
  discrete event living inside the present's call.
- The fast path in `DOSVESA_UpdateWindowFramebuffer` is the one taken
  (commit cd2e95a).

## What changed for this cell (no behaviour change; two instruments)

1. **Nothing in SDL's timing.** The four-phase brackets
   (`fastpath-timing`, t0 entry / t1 after lazy-reinit+DPMI / t2 after the
   VRAM copy / t3 exit, avg+min+**max** per 100 flushes) have existed in
   `SDL_dosframebuffer.c` since doskutsu patch 0015 and are **unconditional**
   -- `dos_port_dbg_log` has no hint gate. They write to
   `LOGS\<TAG>SDL.LOG`, which `run-hw.sh`'s single `get-file` call has never
   fetched. So this instrument has been recording on every run of this
   campaign and been read on none of them. That is also the correct reading
   of "SDL_HINT_DOS_FLIP_INSTR=1 produced no output": that hint gates a
   different bracket entirely; the four-phase block was producing output
   into a file nobody collected. run-hw.sh now copies it to $DEST's root
   after the game exits and fetches it with everything else. Note SDL caps
   the tag at 5 chars for that basename, so the file is `<TAG[0:5]>SDL.LOG`.
2. **Patch 0186**: `dos_port_fb_created`, incremented on the FIRST line of
   `DOSVESA_CreateWindowFramebuffer`, reported on the `DOS-PORT flushpath`
   line. Surface rebuilds happen in a different function from the flush, so
   no bracket inside the flush could ever see one.

## Predictions, in order of how much they would settle

**P-A (primary).** `fb_created == 3` (one at startup, two at the stalls),
or `fb_created == 2` with the startup one accounted for. A surface rebuild
at each stall time is the whole answer and nothing else needs to be true.
- Falsified by `fb_created == 1`: the surface is built once and never
  rebuilt, and the lazy-reinit hypothesis is dead for good.

**P-B.** At least one `fastpath-timing` block reports
`total_ms_max >= 200`. Then the stall is inside t0..t3, and whichever of
`dpmi_ms_max` / `copy_ms_max` / `post_ms_max` carries it names the phase.
- `dpmi_max` large -> the lazy re-init block (consistent with P-A).
- `copy_max` large -> the VRAM copy itself; a bus/refresh event, not code.
- `post_max` large -> the VRAM-readback diag / return path.

**P-C.** Every block reports `total_ms_max < 50`. Then the stall is
**outside** t0..t3 -- t3 is taken before the summary line is written, so the
un-bracketed tail is `dos_port_dbg_log` itself (`fprintf` + `fflush` +
`fsync` to a FAT volume on a CF card), plus SDL_video.c's prologue.
- This is the weakest of the three a priori, and here is why I am saying so
  in advance rather than after: the logging fires on a **100-flush** cadence
  (~2.5 s at 40 fps), so it would produce ~8 stalls per 20 s, not one every
  20.1 s. For P-C to be the answer, something with an ~800-flush period, or
  DOS's own deferred FAT/directory commit, has to be doing the work -- an
  extra mechanism P-A and P-B do not need.
- If P-C does hold, the follow-up is a cell with the SDL log suppressed,
  because then the stall is an artifact of the instrumentation.

## Addendum, written while the cell was running and before any result

Reading the t2..t3 span to understand what `post` contains turned up
something that is worth stating on its own, and I am stating it here so it
is on the record as a prediction rather than a rationalisation:

**`dos_port_dbg_log` is running inside the measured present path on every
cell this campaign has produced.** Three of its call sites are on a
100-flush cadence and every one of them does `fprintf` + `fflush` +
`fsync` to a FAT volume on a CF card:

- `[lifecycle] UpdateWindowFramebuffer #N` (line ~1809) -- *before* t0.
- the post-write VRAM readback at line 2226, which also does a
  `dosmemget`/`SDL_memcpy` of 16 bytes out of VRAM -- *inside* t2..t3.
- the bank-switch audit summary at line ~2390 -- *inside* t2..t3.
- and now the `fastpath-timing` block itself -- *after* t3.

A gate-window run does roughly 8,000 flushes, so that is roughly 240
disk-syncing writes inside the present. Gate 2's whole-run `tick_rate`
misses its bar by 0.05-0.14 out of 39.2 -- about 0.3% of the run. If an
fsync on this target costs even 10 ms, 240 of them is ~2.4 s out of ~127 s,
which is 1.9% -- **several times the size of the gap Gate 2 is failing
by.** I have not measured an fsync on this target and that number is
arithmetic on an assumed cost, not a result.

This does not replace P-A/P-B/P-C; it sharpens P-C and adds a reading of
P-B. If `post_ms_max` is the large one, the readback-plus-log at 2226 is
the first thing to look at, not the VRAM copy. Either way the follow-up is
the same and it is cheap: gate `dos_port_dbg_log` behind an env var, run
the gate cells with it off, and see what whole-run `tick_rate` does.

## Correction, written while FPT1 was still collecting and before its files
## were opened

**A gate-window run does 23 real presents, not 8,000.** From TNFA1's own
`fps_basis` line: `render_passes=4985 presents_real=23 presents_skipped=4995
presents_palette_only=20`. The dirty check short-circuits before SDL is
called on all but 23 of them.

Two things follow, and both of them cut against what I wrote above.

1. **P-B and P-C cannot be scored by this cell.** `fastpath-timing` emits
   once per 100 flushes; at 23 flushes per run it will never emit at all.
   The invalidity condition below covers this, but I listed it as an edge
   case when it was in fact a certainty I could have checked in one grep
   before spending the cell. The bracket is the right instrument and the
   wrong reporting cadence: with 23 flushes in a run, the thing to print is
   every flush, not a 100-flush aggregate.

2. **The 240-fsync arithmetic in the addendum is wrong by two orders of
   magnitude.** 23 flushes means roughly one or two of those log calls
   inside the present per run, not 240. The addendum's conclusion --
   that logging could account for several times Gate 2's gap -- does not
   survive its own denominator. The fsync probe is still worth running,
   because the per-call cost is unmeasured and other code logs too, but it
   is no longer a candidate explanation for Gate 2.

What this does NOT change: **P-A is untouched and is still the primary.**
`fb_created` counts surface rebuilds wherever they happen and does not care
how many flushes there were.

And it sharpens the target considerably. 23 presents in a run, two of them
costing 242 ms: that is not a tax spread over thousands of calls, it is
**two events out of twenty-three.** Whatever it is, roughly one present in
ten does it.

## Invalidity conditions

- `fastpath-timing` absent from the fetched log: the fast-path branch was
  not entered, and P-B/P-C are unscored (not "small"). Check the
  `[lifecycle] UpdateWindowFramebuffer #N` lines in the same file first --
  if those are absent too, the flush was never called at all and the cell
  says nothing about the present.
- `<TAG[0:5]>SDL.LOG` absent from the pulled set: the harness change did not
  work; nothing is scored. The collection loop's own gate only requires
  STDOUT.TXT and `<TAG>.LOG`, so this failure mode cannot wedge the cell,
  only leave it uninformative.
- Fewer than 2 stalls in this run's tick trace: there is nothing to locate
  and the cell is unscored regardless of what the brackets say.

## Not being claimed

Neither instrument changes rendering, so this cell is not a Gate 2 or
Gate 3 datapoint and its tick_rate is not comparable to the gate cells --
it carries one extra file copy in RUN.BAT after the game has already
exited, which is outside the measured window, but the build differs from
the gate build by patch 0186 and that is enough to keep it separate.
