# S7 -- DMA-cycle-stealing hypothesis, real-hardware result: REFUTED -- 2026-09-14

Continuation of `S7-dma-cyclesteal-diag-dosboxx-2026-09-14.md`. Operator-
approved single real-hardware cell (tag `DMAX1`, `binary_sha12=
7d2309fcdef7` -- same binary as `AUDIOFX3`/`AUDIOFX4`, config-only
experiment, no rebuild), HW-486-66, same recipe as `AUDIOFX1`-`4`:
`run-rig.sh trilbysnotes --tag DMAX1 --env DOSAGS_FIXED_TIMESTEP=1 --env
DOSAGS_TAS_AUTO_EXIT_TICK=200 --env SDL_HINT_DOS_AUDIO_BACKEND=opl3 --env
SDL_HINT_DOS_AUDIO_FORCE_DSP_PAUSE=1 --extra-file ACSETUP.CFG:ACSETUP.CFG`.
`run-rig.sh` completed cleanly end to end (no collect-phase stall).

## Result

`DMAX1.LOG` (RUNMANIFEST + diagnostics):

```
[RUNMANIFEST-BEGIN]
binary_sha12=7d2309fcdef7
duration_s=93
exit_code=0
fps_p50=0.48
fps_p95=0.51
audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=891
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=2.50 frames_skipped=168
DOS-PORT audioprb total_calls=65 window_calls=65 slots_us(min=16 mean=3022 max=23848) pump_us(min=6391 mean=11178 max=13398) regwrite(calls=6079 min_us=19 mean_us=21 max_us=25)
DOS-PORT tickfx total_calls=34 window_calls=34 catchup_n_sum=167 catchup_us(min=947795 mean=2434253 max=34641911) realtick_us(min=114951 mean=469332 max=524869) catchup_yield(switches=2 min_us=241 mean_us=950138 max_us=1900035) realtick_yield(switches=596 min_us=37 mean_us=109771 max_us=4142502)
```

Fetched separately (`LOGS\DMAX1SDL.LOG`, not in `run-rig.sh`'s own
hardcoded pull list -- retrieved directly via `vc get-file DMAX1SDL.LOG
--return --from "C:\DOSAGS\LOGS"`, since the file lives in a subdirectory
and the flat `--from "C:\DOSAGS"` form fails with "not in the target's
own DIR" -- a real, minor `vc get-file` usage gap worth remembering for
next time, not a bug in the file itself):

```
audio: SDL/0106 SB DMA-path decision: is_sb16=0 force_8bit=1 dsp_ver=2 highdma=-1 -> 8-bit-low-DMA path
audio: SDL/0106 OpenDevice DMA programmed: path=8-bit-low-DMA dma_ch=3 (low/byte ports 0x00-0x0F) dma_buflen=1024 fmt=0x8 ch=1 freq=11025 Hz irq=7 ack_port=0x22E silence=0x80
audio: SDL/0106 DSP start seq (8-bit): 0xD1(spkr-on) 0x40 tc=166 (rate=11025 effective=11025) 0x48 block_size=511 (bytes-1) 0x1C(8-bit autoinit)
audio: DSP forcefully paused via SDL_HINT_DOS_AUDIO_FORCE_DSP_PAUSE=1; ...
audio: SDL/0106 OpenDevice SUCCESS path=8-bit-low-DMA dma_ch=3 irq=7 irq_count_at_open=0
audio: SDL/0106 CloseDevice: total IRQ-5 fires this run = 0 (0 == DMA-IRQ never armed; the pumps never ran)
audio close: force-pause active, issuing DSP hard reset (skips 0xDA/0xD3 graceful exit)
```

**Confirms the prior entry's "IRQ-5" correction directly on real
hardware**: `is_sb16=0 force_8bit=1`, `dma_ch=3`, `irq=7` -- the real
PGSB/PicoGUS 8-bit path (IRQ7/DMA3), exactly as `~/git/g2k/README.TXT`
documents and exactly as predicted, not IRQ5/DMA1. The log line's own
"IRQ-5" text is confirmed cosmetic (generic string in the SDL backend's
source, unrelated to the actual `irq=7` it's reporting alongside).

## Verdict: the hypothesis is REFUTED, not confirmed

The pre-registered test: if Arm B (`DMAX1`, DMA halted) tracks Arm A
(sound-off, `tick_rate~23.8-23.9`), the tax needs active DMA transfer
(hypothesis confirmed). If it tracks Arm C (sound-on/full-DMA,
`tick_rate~2.96-2.97`, `S7-tickfix-diag-realhw-2026-09-14.md`/
`S7-yield-diag-realhw-2026-09-14.md`), the tax survives DMA halted
(hypothesis refuted).

**`DMAX1` measured `tick_rate=2.50` -- the same collapsed order of
magnitude as Arm C, not Arm A, and if anything slightly *worse* than
Arm C's own 2.96-2.97.** This is a clean result, not an ambiguous one:
2.50 sits nowhere near the ~23.8-23.9 Arm A ceiling and squarely inside
the Arm C collapsed regime. Per-tick cost confirms the same picture:
`catchup_us` mean (2,434,253us / 4.91 catch-up ticks per burst =
~495.8ms/tick) and `realtick_us` mean (469.3ms) are both *higher* than
Arm C's own 407.2ms/409.5ms (`S7-tickfix-diag-realhw-2026-09-14.md`) --
against Arm A's ~42ms/tick baseline, that is roughly an **11.2x-11.8x**
tax, slightly larger than Arm C's already-established 9.7x, not smaller.

**With zero DMA-IRQ fires confirmed for the entire 93-second run (both
the `irq_count_at_open=0` -> `CloseDevice` tally of 0, a hard, direct
real-hardware measurement, not an inference from the hint's own
comment), the DMA-cycle-stealing hypothesis is refuted: the tax does
not require active DMA transfer.** It survives -- fully, undiminished --
with the SB16/PicoGUS DMA channel completely halted for the whole run.
Whatever the mechanism is, it tracks **the audio device being open**
(and, per everything ruled out so far, specifically NOT explicit
`DOS_Yield()` call volume, not `audio_core_entry_poll()`'s own cost, not
OPL3 register-write cost, and now not active DMA transfer either), not
any activity the device performs once opened.

## The WaitDevice-timeout interaction flagged in the prior entry is real, but is a second-order effect, not the answer

`catchup_yield` shows only 2 real yield-switches during the entire
catch-up burst (same tiny count as Arm C's own 2), so yield-switch
*volume* is not the story here either, consistent with the yield
hypothesis's own prior ruling-out. But **their cost is enormous**:
`catchup_yield mean_us=950138` (0.95s/switch!) and `max_us=1900035`
(1.9s) -- both suspiciously close to the un-gated `DOS_AUDIO_
WAITDEVICE_TIMEOUT_NS` (1000ms) constant flagged in the prior entry.
This is exactly the predicted signature: once force-paused, the ring
fills permanently, and any yield that happens to reach the audio thread
while it's spinning in `WaitDevice()`'s ring-full loop pays close to the
full 1-second backstop before bouncing back. **This plausibly explains
why `DMAX1` (2.50) came in slightly worse than Arm C (2.96-2.97)** -- a
real, source-confirmed artifact of this specific force-pause
configuration, not a mechanism present in Arm C at all (Arm C's ring
drains normally via real IRQ activity, so it never takes the ring-full/
timeout branch this reasoning depends on). **It does not change the
core verdict**: even crediting the entire Arm-B-vs-Arm-C gap to this
artifact, Arm B is still an order of magnitude away from Arm A, and the
zero-IRQ confirmation is a hard fact this artifact cannot explain away.

## Where this leaves the investigation

**Ruled out so far, all with real-hardware data**: `audio_core_entry_
poll()`'s own call cost, the poll-count multiplier, OPL3 register-write
volume/cost, cooperative-scheduler yield-switch volume, and now active
DMA transfer. **What remains standing, unrefuted**: the tax tracks the
audio device being *open* (the autonomous `PlaybackAudioThread` existing
and being `READY` in the scheduler's thread table), independent of what
it actually does. This is exactly the hypothesis `S7-tickfix-diag-
realhw-2026-09-14.md`'s own "Not yet done" item 2 already named and did
not attempt: **A/B whether the mere existence of the background audio
thread (not its call frequency, not its DMA activity) is the lever** --
e.g. a build variant that services the SB16 ring fully synchronously
(no `SDL_CreateThread`/cooperative second thread at all) against this
one. That is a real architecture change, not a diagnostic, and per that
entry's own note needs its own design review before touching real
hardware again -- not attempted this entry.

## Not yet done

1. The audio-thread-existence hypothesis above -- needs its own design
   pass (how to build a synchronous-only SB16 backend variant safely,
   whether that's even feasible without breaking real playback) before
   any further real-hardware time.
2. A `vc get-file` usage note: pulling a file that lives in a
   subdirectory on the target needs `--from` pointed AT that
   subdirectory (`"C:\DOSAGS\LOGS"`), not the package root plus a
   backslash-qualified name (`"C:\DOSAGS"` + `"LOGS\DMAX1SDL.LOG"`
   fails with "not in the target's own DIR" -- the DIR listing vcctrl
   walks is not recursive). Worth folding into `run-rig.sh`'s own
   collect step if the SDL debug log becomes a routinely-needed pull,
   not done this entry (one-off manual pull was enough here).
3. Acceptance gate items 4 and 5 remain FAIL.

Patches 0059-0064 all stay landed, all still temporary.
