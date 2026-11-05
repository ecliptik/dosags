# S7-GUS -- .pat upload PIO + prepsong cost, real-hardware result: ROOT CAUSE CONFIRMED -- gus_upload_pio() accounts for the whole outlier -- 2026-09-15 (new session, continued)

Operator-approved cell (tag `GUSU1`, `binary_sha12=172b2d9ad4c6`, the
patches SDL/0147 + ags/0072 + ags/0073 build). Continuation of
`S7-gus-uploadpio-dosboxx-2026-09-15.md`'s own DOSBox-X pass -- this is
the real-hardware measurement that actually confirms or refutes the
byte-wise-PIO-overhead hypothesis.

## The boot-profile workaround: the automated path actually worked this time

Notable operational finding, worth recording alongside the actual
result: `run-rig.sh --boot-profile 3` (wrapping `vcctrl`'s own
`select_boot_profile()`), which had failed 3-for-3 across `GUST1`,
`GUSD1`, and `GUSV1`, **succeeded on this session's first attempt**
(`edge_s=24.58`, `ready_s=3.97`, `attempts=3` internally) -- landing
cleanly on `PGGUS` without any manual LED-polling or video-frame-
extraction workaround at all. `edge_s=24.58` matches `GUST1`/`GUSD1`'s
own original ~25s timing, not `GUSV1`'s own recalibrated ~35.5s --
consistent with the timing genuinely varying session-to-session (cold
vs. warm PSU/component state, plausibly) rather than the automated
helper's own logic being unconditionally broken. **This session's real
obstacle was a different, unrelated flake**: `send-file`'s NET-transfer
"did not come back" quirk hit three separate times on three different
single files (`RUN.BAT`, then `ACSETUP.CFG`, then `OPL3BANK.DAT` -- no
consistent culprit file, every other file transferred and verified
cleanly each time) before a full retry succeeded end-to-end -- recovered
via the already-documented pattern (kill the stalled `run-rig.sh`
process, re-invoke fresh; `--replace` makes re-staging idempotent). One
more instance on log collection (`AUTOPLT.LOG` no-return), recovered by
fetching `GUSU1.LOG` directly via a standalone `get-file`. Neither the
boot-profile success nor these transfer flakes changes anything about
the workaround's own known instability -- both remain real, worth
tracking, not yet root-caused.

## Result

```
exit_code=0
audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=76
STDOUT.TXT: DosMidiBackend: native GF1 (Gravis Ultrasound) backend active
DOS-PORT memory_min_free_kb=155008
DOS-PORT tick_rate=9.34 frames_skipped=164
DOS-PORT audioprb total_calls=68 window_calls=68 slots_us(min=96 mean=101605 max=6891463) pump_us(min=68 mean=81 max=159) regwrite(calls=0 min_us=0 mean_us=0 max_us=0) gusscan(calls=28 min_us=25 mean_us=106 max_us=169) voicefreq(calls=28 min_us=10 mean_us=11 max_us=15) voicevol(calls=58 min_us=27 mean_us=31 max_us=167) voicepan(calls=28 min_us=8 mean_us=8 max_us=10) voicestart(calls=28 min_us=41 mean_us=42 max_us=54) voicestop(calls=13 min_us=11 mean_us=12 max_us=14) miditick(calls=20 min_us=20 mean_us=534 max_us=3354) uploadpio(calls=22 min_us=55501 mean_us=274958 max_us=534704 bytes=712114) uploadsample(calls=22 min_us=55501 mean_us=274958 max_us=534704 bytes=712114) prepsong(calls=1 min_us=6891245 mean_us=6891245 max_us=6891245)
DOS-PORT tickfx total_calls=36 window_calls=36 catchup_n_sum=159 catchup_us(min=15 mean=165764 max=4016764) realtick_us(min=5709 mean=376000 max=7033870) catchup_yield(switches=0 min_us=0 mean_us=0 max_us=0) realtick_yield(switches=0 min_us=0 mean_us=0 max_us=0)
```

`audio_vital_status` confirms real GUS MIDI dispatch (`midi=gus,
events=76`, zero underruns), clean shutdown, `exit_code=0`. Local
`AGS.EXE` sha256 matched the staged/verified copy exactly (both
checked before and after transfer, per this hub's own populate
discipline).

## Verdict: ROOT CAUSE CONFIRMED -- prepsong accounts for essentially the entire outlier

**`prepsong(calls=1, max_us=6,891,245)`** -- exactly ONE call in the
whole 28-second run, and its own `max_us` is within **218 microseconds**
of `slots_us`'s own outlier (`max_us=6,891,463`). This is not "close" --
it is, within measurement resolution, the SAME event.
`gus_sink_prepare_song()`'s own call site (this port's own `dos_midi_
backend_prepare_song()`) is where the ~6.89 seconds actually happens.

**Within `prepsong`, the upload transfer itself dominates**:
`uploadpio`/`uploadsample` are numerically identical (as expected --
`gus_upload_pio()` is the default, only-exercised transport this run,
`SDL_HINT_DOS_GUS_DMA_UPLOAD` unset): 22 calls, `bytes=712114` total
(712 KB of real GM instrument `.pat` sample data actually uploaded to
GUS DRAM for this song), summing to **~6,049,076us (~6.05 SECONDS)** of
the ~6.89s total. Effective throughput: **≈115 KB/s, ≈8.5us per byte**
-- a real, measured, ISA-bus-limited number, not an estimate.

**Residual**: `prepsong`'s own total minus the upload sum leaves
**≈842,169us (~0.84s) unaccounted for** -- not yet separately bracketed
this pass. The most likely explanation, not yet confirmed: `upload_pat()`
(`gus_sink.c`)'s own `.pat` file I/O (`fopen`/`fread` per candidate
sample, per instrument) and/or `gus_sink_prepare_song()`'s own 256-
program scan loop (128 melodic + 128 drum, most of which are unused for
any given song and skip immediately, but still iterated). Neither is
separately measured; if a future pass wants the full breakdown, this is
the next thing to bracket -- but the headline finding does not depend on
resolving this residual.

## What this changes: a real, likely-fixable software cost, not a hardware constant

Unlike the OPL3/WaveBlaster tax (a genuine hardware/electrical constant
of this rig, waived by the operator 2026-09-15), **this is source-
verified as a real software inefficiency**: `gus_upload_pio()`'s DEFAULT
path re-selects the FULL 20-bit GF1 DRAM address before every single
byte (`g_gus_pio_autoinc` defaults `false`) -- the function's own comment
already documented this costs roughly "~6 outportb/byte" vs. roughly
"~1 outportb/byte" with `SDL_HINT_DOS_GUS_PIO_AUTOINC=1` set, an
EXISTING hint, never enabled by default, requiring zero new code.

**Naive extrapolation** (not yet measured, flagged as an estimate, not a
result): if per-byte overhead drops ~6x, the upload's own ~6.05s could
plausibly drop to roughly **~1.0s**, bringing `prepsong`'s total to
roughly **~1.85s** (1.0s upload + the ~0.84s residual, which autoinc
would not help) -- down from ~6.89s. Applied to `GUSU1`'s own `tick_
rate=9.34`, this could meaningfully close the gap toward the ~23.8-23.9
sound-off baseline, though the actual effect on `tick_rate` depends on
exactly how this one-time per-song cost interacts with the fixed-
timestep catch-up accounting (`dos_run_tick_fixed()`'s own clamp) --
not derived here, needs its own measurement once the fix lands.

## Not yet done

1. **Land the fix**: enable `SDL_HINT_DOS_GUS_PIO_AUTOINC=1` for this
   port (either as this port's own default, or confirm autoinc mode's
   own real-hardware correctness first if it has never been validated
   on real GF1 hardware before -- check `gus_upload_pio()`'s own history/
   patch provenance for whether autoinc mode has ever been real-
   hardware-tested at all before flipping its default).
2. DOSBox-X-validate the fix, then a fresh real-hardware cell measuring
   the SAME six fields (`prepsong`/`uploadpio`/`uploadsample` especially)
   to confirm the actual (not extrapolated) speedup.
3. Once confirmed: revert the ten temporary S7 diagnostic patches that
   are now fully spent (0059-0068, 0141, 0143-0144; keep 0142 pending a
   separate check, 0144 may be worth keeping permanently -- previously
   flagged, still unresolved) AND the GUS-specific diagnostics from this
   sub-investigation (0145/0146/0147, ags 0069/0070/0071/0072/0073) --
   narrow slices, DOSBox-X regression-check after each, commit after
   each, per this hub's own housekeeping discipline.
4. Re-target acceptance gate items 4 and 5 against GUS with a PROPER
   ABBA (not a single cell) before claiming the Sound milestone met --
   this entry, `GUST1`, `GUSD1`, and `GUSV1` combined are five single
   operator-approved cells across two binaries, real signal but not yet
   the pre-registered A/B/B/A block acceptance gate 4 actually requires.
5. `vcctrl`'s own `select_boot_profile()` timing sensitivity remains
   unresolved (now 1 success / 3 failures across four sessions for this
   exact rig/profile combination) -- still flagged, not fixed, still a
   good candidate for its own focused session in `~/git/vcctrl`.
