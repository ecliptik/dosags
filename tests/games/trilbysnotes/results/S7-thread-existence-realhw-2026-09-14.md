# S7 -- audio-thread-existence hypothesis, real-hardware result: REFUTED -- 2026-09-14

Continuation of `S7-thread-existence-diag-dosboxx-2026-09-14.md`.
Operator-approved real-hardware cell (tag `NOBGT1`, `binary_sha12=
36ebdca8ee61` -- the SDL/0143 build, new relative to `AUDIOFX3`/`4`/
`DMAX1`), HW-486-66, same recipe: `run-rig.sh trilbysnotes --tag NOBGT1
--power-on --env DOSAGS_FIXED_TIMESTEP=1 --env DOSAGS_TAS_AUTO_EXIT_
TICK=200 --env SDL_HINT_DOS_AUDIO_BACKEND=opl3 --env SDL_HINT_DOS_AUDIO_
NO_BG_THREAD=1 --extra-file ACSETUP.CFG:ACSETUP.CFG`. `run-rig.sh`
completed cleanly end to end.

## Result

`NOBGT1.LOG`:

```
[RUNMANIFEST-BEGIN]
binary_sha12=36ebdca8ee61
duration_s=93
exit_code=0
fps_p50=0.48
fps_p95=0.49
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=911
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=2.48 frames_skipped=168
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=17 mean=3245 max=25319) pump_us(min=6055 mean=10821 max=12443) regwrite(calls=6338 min_us=20 mean_us=21 max_us=230)
DOS-PORT tickfx total_calls=34 window_calls=34 catchup_n_sum=167 catchup_us(min=970181 mean=2446052 max=34748830) realtick_us(min=115611 mean=472638 max=535205) catchup_yield(switches=0 min_us=0 mean_us=0 max_us=0) realtick_yield(switches=0 min_us=0 mean_us=0 max_us=0)
```

`LOGS\NOBGTSDL.LOG` (see "A real 8.3-truncation gap" below for why the
filename differs from the tag):

```
audio: SDL/0106 SB DMA-path decision: is_sb16=0 force_8bit=1 dsp_ver=2 highdma=-1 -> 8-bit-low-DMA path
audio: SDL/0106 OpenDevice DMA programmed: path=8-bit-low-DMA dma_ch=3 (low/byte ports 0x00-0x0F) dma_buflen=1024 fmt=0x8 ch=1 freq=11025 Hz irq=7 ack_port=0x22E silence=0x80
audio: SDL_HINT_DOS_AUDIO_NO_BG_THREAD=1 -- ProvidesOwnCallbackThread set at Init(); no PlaybackAudioThread will be created for this device. ...
audio: SDL/0106 OpenDevice SUCCESS path=8-bit-low-DMA dma_ch=3 irq=7 irq_count_at_open=0
audio: SDL/0106 CloseDevice: total IRQ-5 fires this run = 1948 (0 == DMA-IRQ never armed; the pumps never ran)
```

## Verdict: REFUTED, and cleanly -- both prior caveats now closed

**`tick_rate=2.48`** -- the same collapsed order of magnitude as every
other sound-on arm (Arm B `DMAX1`=2.50, Arm C `AUDIOFX3`/`4`=2.96-2.97),
nowhere near Arm A's sound-off ~23.8-23.9. Per-tick cost: `catchup_us`
mean (2,446,052us / (167/34=4.91 ticks/burst) = **498.0ms/tick**) and
`realtick_us` mean (**472.6ms**) both land in the same 469-498ms band
as Arm B (495.8ms/469.3ms), both still above Arm C's 407.2ms/409.5ms.

**`catchup_yield(switches=0)` / `realtick_yield(switches=0)` -- exactly
zero, confirmed on real hardware, not just DOSBox-X.** This is the
mechanistic proof the patch does what it claims on the actual target:
with no second thread ever created, there is nothing for `DOS_Yield()`
to switch to, so the count is provably zero, not just small.

**`total IRQ-5 fires this run = 1948` -- closes this entry's own
pre-registered caveat.** The DOSBox-X writeup flagged that a zero-IRQ
Arm-D result would need a same-scenario threaded baseline to rule out
"the patch broke DMA arming" as an alternative explanation. On real
hardware, DMA is unambiguously alive and well: 1948 real IRQ fires over
93s (~20.9 Hz), matching the theoretical ~21.55 Hz chunk-completion rate
for 8-bit/11025Hz/511-byte half-buffer chunks almost exactly. Pulling
the AUDIOFX-tag collision file (see below) for direct comparison: the
last AUDIOFX-tagged cell (thread present, DMA active, most likely
`AUDIOFX4` -- see the naming-gap note) shows **1638 IRQ-5 fires over
79s (~20.7 Hz)** -- the same rate, confirming DMA behaves identically
with or without the background thread. **With both DMA activity and
thread existence now independently confirmed-present/confirmed-absent
across four real-hardware cells and the tax staying in the same
collapsed band regardless, the audio-thread-existence hypothesis is
refuted just as cleanly as the DMA-cycle-stealing hypothesis was.**

| Arm | Thread | DMA/IRQ | tick_rate | catchup/realtick us |
|---|---|---|---:|---|
| A (sound-off) | n/a | n/a | 23.8-23.9 | ~42/~42 |
| B (`DMAX1`) | present | halted, 0 IRQ | 2.50 | 495.8k/469.3k |
| C (`AUDIOFX3`/`4`) | present | active, 1638-ish IRQ | 2.96-2.97 | 407.2k/409.5k |
| D (`NOBGT1`) | **absent** | active, 1948 IRQ | 2.48 | 498.0k/472.6k |

Every condition where the audio device is *open* collapses, regardless
of which axis (DMA activity, thread existence) is varied. Only closing
the device (Arm A) recovers performance.

## A real 8.3-truncation gap, found pulling this cell's own evidence

`DOS_PORT_LOG_TAG=NOBGT1` (6 chars) + `SDL.LOG` names a 9-character
base (`NOBGT1SDL`), one over the 8.3 limit -- DOS silently truncated it
to `NOBGTSDL.LOG` (dropping the trailing `1`), not `NOBGT1~1.LOG`. Cost
real time this session (`vc get-file DMAX1SDL.LOG`/`NOBGT1SDL.LOG`
against the literal tag both returned "not in the target's own DIR"
before the actual 8.3 name was found via a directory listing). **Worse,
a real, already-realized data-loss bug**: `AUDIOFX1`-`4`'s tags (8
chars each) + `SDL` (3 chars) = 11 chars, ALL four truncate to the
*same* `AUDIOSDL.LOG` -- each subsequent `AUDIOFX`-tagged real-hardware
cell in this investigation silently overwrote the previous one's SDL
debug log. The file pulled this entry (`AUDIOFXsomeSDL.LOG` locally) is
whichever `AUDIOFX` cell ran last chronologically (most likely
`AUDIOFX4`, not confirmed with certainty since the file itself carries
no tag identity once truncated) -- `AUDIOFX1`/`2`/`3`'s own SDL debug
logs are unrecoverable. Doesn't invalidate anything already concluded
(every `AUDIOFX*` finding used the tag-named `.LOG`/`STDOUT.TXT`, which
stay unique since `DOSAGS_LOG_TAG` isn't suffixed the same way), but is
a real gap worth fixing before it costs a future investigation real
data: `DOS_PORT_LOG_TAG` values longer than 5 characters are unsafe for
this specific log file. Not fixed this entry (out of scope -- flagging
for whoever next needs this log routinely).

## Where this leaves the investigation

**Ruled out, all with real-hardware data**: `audio_core_entry_poll()`'s
own cost, the poll-count multiplier, OPL3 register-write cost,
cooperative-scheduler yield-switch volume, active DMA transfer, and now
audio-thread existence. **What's common to every collapsed arm and
absent only in the sound-off arm**: the SB16/PicoGUS device is *open* --
specifically, `DOS_HookInterrupt` has installed a handler on IRQ7 (this
rig's actual PicoGUS jumper, not the generic "IRQ-5" shorthand) and the
DSP has issued its speaker-enable (`0xD1`) command, regardless of
whether that IRQ ever fires or a thread ever touches it. **A concrete,
motivated new hypothesis, not yet tested**: IRQ7 is the classic ISA
parallel-port (LPT1) interrupt line, and 8259 PIC "spurious IRQ7"
handling is a well-documented, real x86/PC-architecture-era quirk
(noise or timing on the IRQ7 line can trigger spurious interrupts that
BIOS/OS conventions specifically special-case) -- if HW-486-66's
mainboard also has LPT1 wired to IRQ7 (common BIOS default, not yet
checked against this rig's own README/CONFIG.SYS), merely *hooking* a
handler on IRQ7 -- independent of DMA activity or thread existence --
could plausibly interact with that convention in a way that adds a
uniform system-wide tax. This is a genuinely different class of
hypothesis (ISA IRQ-line/PIC behavior, not DMA bus contention or
cooperative scheduling) and needs its own design pass -- not attempted
this entry, per this investigation's own checkpoint discipline.

## Not yet done

1. The IRQ7/spurious-interrupt hypothesis above -- needs source/hardware
   research (does this rig's LPT1 share IRQ7? does `DOS_HookInterrupt`
   chain to a prior handler or replace it outright? is there a
   real difference between "IRQ hooked, DMA halted" (Arm B, already
   run) and "IRQ never hooked at all" (would need a new, more invasive
   diagnostic -- opening the DSP without ever calling
   `DOS_HookInterrupt`, likely breaking real playback, since nothing
   would service completions -- a bigger change needing its own design
   review) before any further real-hardware time.
2. The `DOS_PORT_LOG_TAG` 8.3-truncation gap -- flagged, not fixed.
3. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0064, 0141-0143 all stay landed, all still temporary.
