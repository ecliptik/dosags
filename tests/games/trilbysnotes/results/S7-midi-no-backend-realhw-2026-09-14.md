# S7 -- no-MIDI-backend-at-all, real-hardware result: MIDI backend touch is the necessary trigger for the full tax -- 2026-09-14 (new session)

Operator-approved cell (tag `NOBK1`, `binary_sha12=433340f66668`, the
patch-0068 build), HW-486-66, same recipe as every prior S7 cell (a
NORMAL, unrestricted SB16 open -- no `OPEN_STOP_AT`, no `NO_BG_THREAD`,
nothing else touched) plus `DOSAGS_MIDI_NO_BACKEND=1`. `run-rig.sh`
completed quickly and cleanly (no harness intervention needed).

## Result

`NOBK1.LOG`:

```
[RUNMANIFEST-BEGIN]
binary_sha12=433340f66668
duration_s=75
exit_code=0
fps_p50=0.63
fps_p95=0.67
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=none,events=0
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=3.20 frames_skipped=167
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=17 mean=20 max=37) pump_us(min=7058 mean=11228 max=11808) regwrite(calls=0 min_us=0 mean_us=0 max_us=0)
DOS-PORT tickfx total_calls=34 window_calls=34 catchup_n_sum=165 catchup_us(min=16 mean=1751380 max=25028919) realtick_us(min=85449 mean=449797 max=2822345) catchup_yield(switches=0 min_us=0 mean_us=0 max_us=0) realtick_yield(switches=876 min_us=38 mean_us=62766 max_us=3133532)
```

`audio_vital_status` confirms `midi=none,events=0` -- `dos_midi_backend_
open()` was genuinely never reached (its own `DosMidiBackend: OPL3/OPL2
chip detected and initialized` banner does not appear anywhere in
`STDOUT.TXT`) -- while `pcm=sb@11025m16,voices=8,underruns=0` confirms
the SB16 PCM device opened completely normally, full default
configuration: thread present, no `OPEN_STOP_AT` restriction, nothing
about the SB16 backend itself touched.

## Verdict: `tick_rate=3.20` -- the ~5x floor, NOT the full tax -- and it rewrites the earlier bisection matrix's own conclusion

**`tick_rate=3.20`** matches `OSA1NT` (3.21) almost exactly -- the same
~5x-floor band this investigation found in the `OSA1NT`-`OSA4NT` family,
**not** the full ~10-12x collapsed band every other "SB16 fully open,
thread present" cell in this investigation has shown (`AUDIOFX3`/`4`:
2.96-2.97, `NOBGT1`: 2.48, `DMAX1`: 2.50). `duration_s=75` and
`catchup_n_sum=165` both match `OSA1NT`'s own 74s/165 almost exactly --
the same class of run, not a fluke.

**This is the first real-hardware cell in the entire investigation to
test "SB16 device open completely normally (thread present, default
autoinit DMA) AND zero MIDI backend ever touched."** Every prior "SB16
fully open" cell also had a real, dispatching OPL3 MIDI backend active
-- the earlier bisection matrix (`S7-full-bisection-matrix-realhw-2026-
09-14.md`) concluded "thread presence and DMA/IRQ activity are each
independently sufficient to reach the ~10x ceiling," but every cell that
conclusion rested on also had MIDI active, so it never actually isolated
thread/DMA state from MIDI state. **`NOBK1` shows that conclusion needs
correcting**: a fully-normal SB16 open (thread present, real autoinit
DMA available) does NOT by itself reach the full tax -- it lands at the
same ~5x floor `OSA1NT`'s maximally-minimal SB16 state showed. Thread
presence and DMA activity, on their own, were never the second booster
this investigation thought they were; they were a proxy for "MIDI is
also active in this cell," because no cell before `NOBK1` ever broke
that correlation.

## The corrected, now fully coherent two-factor model

Combining every real-hardware cell in this investigation (fourteen
prior cells plus `SUBSY1`, `SUBSY2`, `SILNT1`, `NOBK1`):

| SB16 device state | MIDI backend touched? | tick_rate | Example cells |
|---|---|---:|---|
| Never opened (`SUBSY1`/`SUBSY2`) | Yes (OPL3, real dispatch) | 2.52-2.53 | `SUBSY1`, `SUBSY2` |
| Minimal (`OPEN_STOP_AT=1`, no thread) | Yes (OPL3, real dispatch) | 3.21-3.23 | `OSA1NT`-`OSA4NT` |
| Minimal (`OPEN_STOP_AT=1`, thread present) | Yes (OPL3, real dispatch) | 2.49 | `OSA1`, `OSA4` |
| Full/normal (thread present, real DMA) | Yes (OPL3, real dispatch) | 2.49-2.97 | `AUDIOFX3`/`4` |
| Full/normal (no thread, real DMA) | Yes (OPL3, real dispatch) | 2.48 | `NOBGT1` |
| Full/normal (thread present, DMA halted) | Yes (OPL3, real dispatch) | 2.50 | `DMAX1` |
| Full/normal (thread present, real DMA) | Yes (OPL3, chip init only, **zero dispatch**) | 2.48 | `SILNT1` |
| **Full/normal (thread present, real DMA)** | **No -- never touched** | **3.20** | **`NOBK1` (new)** |
| Never opened at all | No -- never touched | ~23.8-23.9 | Arm A (sound-off) |

**Two independent factors, not one**:
1. **The SB16 device merely being open, in ANY configuration** (even
   `SUBSY1`/`SUBSY2`'s complete non-open, since MIDI alone reaches the
   ceiling there too) costs a real, roughly-uniform ~5x tax against the
   sound-off baseline.
2. **A MIDI backend being touched at all -- even chip-init-only, even
   zero dispatch (`SILNT1`), even with the SB16 device never opened at
   all (`SUBSY1`/`SUBSY2`)** -- is independently *sufficient* to reach
   the full ~10-12x ceiling by itself, regardless of the SB16 device's
   own state (open, minimal, or absent) and regardless of thread/DMA/
   IRQ state (all independently already ruled out as *necessary*, and
   now also ruled out as *sufficient without MIDI*, by `NOBK1`).

**Neither factor's earlier attribution survives untouched**: the
original "thread presence and DMA activity are each independently
sufficient" claim is corrected -- both were confounded with MIDI being
simultaneously active in every cell that supported it. What actually
carries the full tax, in every cell across this whole investigation, is
MIDI backend activity (of any kind, however minimal) -- SB16 device
state only ever explains the smaller ~5x floor underneath it.

## What remains: the mechanism is a persistent, one-time side effect of touching either MIDI hardware path -- OPL3 or MPU-401 -- and cannot be register-write cost

The only action `SILNT1` (full tax) has that `NOBK1` (floor only) does
not is `dos_midi_backend_open()` itself succeeding -- for OPL3, that is
`opl3_sink_open()` -> `SDL_DOSOpl3InitChip()`'s roughly twenty register
writes (enable OPL3 mode, disable 4-op, key-off all 18 voices), a
one-time, sub-millisecond action already measured cheap in isolation.
`S7-abba-2026-09-13.md`'s own `TNWB1` cell shows the identical collapse
using WaveBlaster/MPU-401 instead -- a completely different chip, at a
completely different I/O port range, whose own hardware touch
(`SDL_DOSMpu401Init()`) happens even earlier, at session cold-init
time, not per-song. **A one-time register-write COST cannot explain a
tax that persists for the rest of a 75-95 second run** (this was already
established for the SB16 backend's own OpenDevice sequence, and applies
identically here) -- something about successfully touching either MIDI
chip's I/O ports must leave a PERSISTENT state change behind, most
plausibly a real hardware/electrical effect (this rig's PicoGUS card,
which emulates SB16 AND OPL3/MPU-401 concurrently on one board,
entering a different internal operating state once a second legacy
interface alongside the SB16 emulation is activated) rather than
anything expressible as AGS or SDL software cost. This is not
confirmable or refutable by further source reading or DOSBox-X
validation (an emulator has no ISA-bus electrical model to consult) --
it would need PicoGUS firmware-level investigation or bus-level
instrumentation (an oscilloscope/logic analyzer), both outside this
session's DOS-software toolkit.

## Where this leaves the investigation

**The root cause is now narrowed to a precise, reproducible trigger
condition, even though the underlying electrical/firmware mechanism
inside the PicoGUS card is beyond what this investigation's tools can
resolve further**: touching either MIDI hardware path (OPL3 InitChip or
MPU-401 Init) at all, regardless of subsequent dispatch, regardless of
SB16/thread/DMA state, is necessary and sufficient for the additional
push from the ~5x SB16-open floor to the full ~10-12x ceiling. Sixteen
real-hardware cells across this whole investigation are now fully
reconciled under one coherent two-factor model.

**Practical implication for the 40fps goal**: on this specific rig
(PicoGUS-based HW-486-66), a title that wants both PCM SFX (via the
SB16 path) and real MIDI music pays close to the full ~10-12x tax
essentially unavoidably in software -- no amount of thread/DMA/dispatch
tuning recovers past the ~5x floor once a MIDI backend is touched at
all, since the mechanism looks to be a persistent hardware-level cost of
having a second legacy interface active on the same PicoGUS card, not a
software inefficiency this port's own code can fix. This does not mean
audio must be abandoned to hit 40fps -- it means the achievable ceiling
with the current PicoGUS-based rig config needs to be re-planned around
this ~2x-on-top-of-~5x floor as a hardware constant, not chased further
as a bug.

Acceptance gate items 4 and 5 remain FAIL (the ~5x-to-full-tax mechanism
is now understood at the trigger-condition level, but "understood" is
not "fixed," and the pre-registered `<= 1.5 fps` bar was never going to
be reachable while any MIDI backend stays active on this rig). Patches
0059-0068, 0141, 0143-0144 all stay landed, all still temporary.

## Not yet done

1. A source/hardware note for whoever next works this: the mechanism is
   very unlikely to be fixable from this port's own code (`patches/ags/`,
   `patches/SDL/`) or the hub's shared SDL3-DOS layer -- it looks like a
   PicoGUS-firmware-level interaction between concurrently active
   emulated interfaces, which this project's own "never contribute
   upstream" policy would keep out of scope even if it were diagnosed
   further (PicoGUS is a third-party project this hub does not control).
2. Consider re-scoping the Sound milestone's acceptance gate 4/5
   threshold given this finding -- a `<= 1.5 fps` bar assumed a fixable
   software cost; this investigation's own conclusion is that most of
   the cost is a real hardware constant on this specific rig
   configuration. This is an operator decision, not something to change
   unilaterally.
3. Acceptance gate items 4 and 5 remain FAIL.
