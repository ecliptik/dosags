# S7 -- OpenDevice bisection: design + patch + DOSBox-X validated -- 2026-09-14

Continuation of `S7-irq7-lpt1-hypothesis-refuted-2026-09-14.md`'s own
"Not yet done" item 1. Eight hypotheses are ruled out; what's left
unexplained is that the ~9.7x-11.8x uniform per-`UpdateGameOnce()` tax
appears in every "device open" condition (thread present/absent, DMA
active/halted, IRQ firing 0-2000 times) and is absent only when the
device is fully closed -- pointing at a one-time `OpenDevice` side
effect, not an ongoing cost. This entry designs and lands a real patch
that bisects `OpenDevice`'s own hardware bring-up sequence into four
stop points, then validates it under DOSBox-X. Real hardware not yet
used.

## The four phases

`SDL_HINT_DOS_AUDIO_OPEN_STOP_AT=1|2|3|4` makes `OpenDevice` return
successfully (a normal SDL "device open" from the engine's point of
view -- `audio_core_entry_poll()` runs every tick exactly as with real
audio) at one of four points along its own real sequence:

- **1**: before the 8237 DMA controller is touched at all -- before
  `DOS_HookInterrupt`, before any DSP command beyond the unconditional
  `ResetSoundBlasterDSP()` every open already does.
- **2**: after the DMA controller channel is programmed (mode set) and
  unmasked, still before `DOS_HookInterrupt` and before any DSP command.
- **3**: after `DOS_HookInterrupt` (IRQ vector installed, PIC line
  unmasked), still before any DSP command.
- **4**: after `WriteSoundBlasterDSP(0xD1)` (speaker enabled) and its
  completion wait, still before the DSP is ever told to actually start
  autoinit playback (`0x1C`/`0xB6`).

DMA never actually engages in any of the four phases (the autoinit-start
command never runs in any of them), so this isolates setup-time state
from transfer activity entirely -- a genuinely different axis from
everything tested so far (Arm B tested "DMA armed+started then halted";
these four phases test "how far into arming did we get before DMA was
ever asked to start at all").

## A real correctness risk found and fixed before it became a bug

`audio_core_entry_poll()`'s existing per-tick `SDL_DOSAudioPump()` call
keeps running regardless of where `OpenDevice` stopped -- the engine has
no idea it stopped early. Reading the ring/staging-buffer allocation
(`chunk_size`/`ring_size`/`ring_buffer`/`staging_buffer`, `isr_*`
mirrors) found it originally lived *after* the DMA-controller-setup
section -- meaning phases 1 and 2 would have left `GetDeviceBuf()`/
`PlayDevice()` operating on a NULL ring buffer and zero `chunk_size`, a
real crash risk on real hardware. Fixed by relocating that whole block
earlier, before phase 1's stop point -- verified first that it depends
only on `hidden->dma_channel`/`dma_buffer`/`dma_buflen`/`is_16bit` and
`device->spec.*` (all already set), and that nothing between its old and
new position depends on it either, so the move is behavior-neutral for
the normal (full-open) path. ISR memory-locking
(`DOS_LockCode`/`DOS_LockData`/`DOS_LockVariable`) deliberately stays at
its original later position: phases 1-2 stop before reaching it, which
is safe because the IRQ is never hooked in those phases either, so no
interrupt context ever touches that memory.

Also verified before relying on it: `DOS_UnhookInterrupt()`
(`SDL_dos.c`) already no-ops safely on a never-hooked, calloc-zeroed
hook structure (`if (!hook || !hook->fn) return;`) -- phases 1-2's
`CloseDevice` teardown calls it on a structure that was never populated
by `DOS_HookInterrupt`, and this is already handled, not assumed safe.

## DOSBox-X validation

Baseline (no hint, regression check the reorder didn't change normal
behavior) plus all four phases, same scenario as every prior diagnostic
in this series (`dosbox-run.sh --fast`, scratch `oplmode=opl3` conf
reverted after, Trilby's Notes, `DOSAGS_FIXED_TIMESTEP=1`,
`DOSAGS_TAS_AUTO_EXIT_TICK=200`, `SDL_HINT_DOS_AUDIO_BACKEND=opl3`):

| Run | tick_rate | events (OPL3) | IRQ fires | Banner fired |
|---|---:|---:|---:|---|
| baseline (no hint) | 30.08 | 54 | 0 | (none -- full open, "OpenDevice SUCCESS") |
| phase 1 | 30.35 | 54 | 0 | phase 1 |
| phase 2 | 30.63 | 54 | 0 | phase 2 |
| phase 3 | 30.35 | 54 | 0 | phase 3 |
| phase 4 | 30.63 | 54 | 0 | phase 4 |

All five runs: clean shutdown, no crash, no hang. `tick_rate` stays in
the same 30-31 range across every phase and the baseline -- expected;
DOSBox-X does not reproduce the real-hardware collapse regardless of
phase, same as every prior diagnostic in this investigation. OPL3
dispatch (`events=54`) and IRQ count (0, expected -- DMA never starts in
any phase, and this exact short/quiet scenario already showed 0 IRQ
fires even in the full-open baseline, per `S7-thread-existence-diag-
dosboxx-2026-09-14.md`'s own finding) are identical across all five
runs. Each phase's own banner confirms it stopped at the intended point,
not some other one. `binary_sha12` changed from `36ebdca8ee61` to
`6ca3ac927604`.

**This DOSBox-X pass establishes correctness (wiring, no crash, no
regression to the normal path) -- it says nothing about which phase, if
any, reproduces the real-hardware tax**, exactly like every prior
diagnostic in this series. Only real hardware can answer that.

## Not yet done

1. **The real-hardware cells** -- needs a fresh, separately-asked
   operator go-ahead (already given for this design direction). New
   binary (`6ca3ac927604`) needs staging. Recommended order: run phase 4
   first (the single most informative point -- furthest along the setup
   sequence while still confirming DMA never starts; if the tax appears
   there, it narrows to "something in phases 1-4," if not, the
   mechanism requires the actual autoinit-start command itself, a
   different and arguably more interesting finding). Bisect from there
   based on the result rather than running all four blindly.
2. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0064, 0141, 0143-0144 all stay landed, all still temporary.
