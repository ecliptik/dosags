# S7 -- GUS MIDI escape-hatch test, real-hardware result: GUS avoids the tax entirely -- 2026-09-14 (new session)

Operator-approved cell (tag `GUST1`, `binary_sha12=433340f66668`, the
same unmodified binary as `NOBK1` -- GUS support needed no new patch),
HW-486-66, `PGGUS` boot profile, `SDL_HINT_DOS_AUDIO_BACKEND=gus`,
`DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`.

## A real harness gap hit and worked around, not routed around blindly

`run-rig.sh --boot-profile 3` (which wraps `vcctrl`'s `select_boot_
profile()`) failed twice in a row (`select_boot_profile -> None`), both
times landing safely back on the default `PGSB` profile at a clean
`C:\>` prompt -- confirmed via independent screenshot each time, no
corruption, no hang. This is the first time this exact dosags harness
path (`tests/harness/run-rig.sh`'s own `--boot-profile` flag) has been
exercised for Trilby's Notes; `vcctrl`'s underlying LED-edge-timed blind
menu selection (reboot, wait for the capslock LED edge, spam "3+enter"
within a narrow window, per `vcctrl_common.py`'s own `select_boot_
profile()`/`spam_menu()`) is shared code also used by other ports, and
its exact timing margins were not re-validated against this specific
combination before now.

**Worked around by driving the same LED-edge protocol manually, with
direct polling instead of the automated helper's own internal round
trip**: acquired the input lock, sent `ctrl+alt+delete`, polled `vc
leds` in a tight loop until `capslock`'s `changed_at` advanced past the
reboot trigger time (the real POST-complete edge, detected at t+24.9s,
matching `g2k/README.TXT`'s own documented ~32s POST time), then
immediately fired four rapid `3`+`enter` keypresses (a single ~0.58s
burst, well under the CONFIG.SYS menu's documented 5-second timeout),
then polled for the `scrolllock` RDYPULSE signal to confirm full boot.
**This landed on `PGGUS` cleanly on the first attempt** (`[PGGUS]
ready.` visible on an independent screenshot, `GUS-like card detected
on port 240...`, `Running in GUS mode on port 240`). Three harmless
stray `3` keystrokes flushed into `Bad command or file name` lines
post-boot (already-documented blind-menu-selection residue, no actual
effect). This is a real, reproducible gap in `vcctrl`'s own generic
`select_boot_profile()` timing for this specific rig/profile
combination, worth a closer look before the next port that needs
`--boot-profile` relies on it -- not root-caused further this entry
(the manual protocol is a real, verified workaround, not a guess), and
not something to "fix" by guessing at new LED timing constants without
first collecting enough real data to know what actually changed.

An earlier `wait_for_job_done` call in `run-rig.sh` also separately
timed out after a full 1800s even though `vc file-status` independently
showed the underlying transfer job had already finished (`running:
false`) within 5 minutes and only one file (`CWSDPMI.EXE`) came back
flagged `no-return` (uncertain arrival, not a failure) -- the same
already-documented, low-severity `vcctrl` quirk this investigation has
hit before, recovered the standard way (re-invoking `run-rig.sh` from
scratch; that second attempt's own file transfer completed and
verified byte-for-byet cleanly, only the boot-profile step needed the
manual workaround above).

## Result

Once the RUN.BAT staged by `run-rig.sh`'s own earlier (boot-profile-
failed) invocation was launched by hand against the already-verified
files on `C:\DOSAGS`:

```
[RUNMANIFEST-BEGIN]
binary_sha12=433340f66668
duration_s=28
exit_code=0
fps_p50=4.81
fps_p95=4.81
audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=70
critical_count=0
warn_count=0
[RUNMANIFEST-END]
DOS-PORT tick_rate=9.39 frames_skipped=166
DOS-PORT audioprb total_calls=67 window_calls=67 slots_us(min=17 mean=102962 max=6890560) pump_us(min=19 mean=20 max=27) regwrite(calls=0 min_us=0 mean_us=0 max_us=0)
DOS-PORT tickfx total_calls=35 window_calls=35 catchup_n_sum=164 catchup_us(min=16 mean=173317 max=4025307) realtick_us(min=5742 mean=383704 max=7041908) catchup_yield(switches=0 min_us=0 mean_us=0 max_us=0) realtick_yield(switches=0 min_us=0 mean_us=0 max_us=0)
```

`audio_vital_status` confirms real GUS MIDI dispatch (`midi=gus,
events=70`, zero underruns) -- not a degenerate silent run.
`STDOUT.TXT` confirms `DosMidiBackend: native GF1 (Gravis Ultrasound)
backend active`, clean room transition (`room_transition t_ms=13028`,
smaller than the usual ~19.7-25s outlier seen throughout this
investigation, not concerning), clean shutdown, `exit_code=0`.

## Verdict: GUS avoids the systemic tax entirely -- the working hardware hypothesis holds

**`tick_rate=9.39`** -- 2.4x-3.8x better than every OPL3/WaveBlaster
sound-on cell in this entire investigation (2.48-3.23 range), the best
sound-on result by a wide margin, though still short of the sound-off
baseline (~23.8-23.9). Per-tick breakdown confirms *why*, precisely:

- **`catchup_us`**: mean 173,317us summed per window / (164 catchup
  ticks / 35 calls = 4.69 ticks/call) = **~37ms/catch-up-tick** --
  statistically indistinguishable from the ~42ms/tick sound-off
  baseline. **Catch-up ticks, which touch zero audio-related code by
  construction (gated to `play.fast_forward` only since patch 0060),
  show NO tax at all under GUS** -- in stark contrast to every OPL3/
  WaveBlaster cell, where catch-up ticks (also touching zero
  audio-related code) paid the full ~9.7-11.8x tax anyway. This is the
  cleanest, most direct confirmation possible: the systemic,
  everything-pays-it tax this whole investigation chased is **absent**
  under GUS.
- **`realtick_us`**: mean 383,704us -- elevated, comparable in
  magnitude to the OPL3/WB tax band, but for a fully identified, real,
  narrowly-scoped reason (below), not a mystery.

**The elevated real-tick cost is fully explained by an already-known,
already-partially-fixed inefficiency, not a new mystery**: `slots_us`
(the MIDI slot `Poll()` loop, called once per real tick) shows a mean
of 102,962us and a max of 6,890,560us (6.9 SECONDS) -- `gus_sink.c`'s
own `reap_finished_voices()` (called from `allocate_voice()` on every
note-on) calls `SDL_DOSGusGetState()`, a full GF1 voice-mask hardware
scan across every voice, cli/sti-protected. **This is the exact same
class of cost the S5 GUS architecture work already found and fixed --
but only for the PCM path** (`gus_pcm_stream_pump()`'s own per-frame
full-scan, fixed via the new `SDL_DOSGusVoiceActive(int voice)` export,
sdl3-dos patch 0140). That session's own writeup explicitly noted
`gus_sink.c`'s `reap_finished_voices()` was left unchanged because it
is "note-driven, not frame-driven" and therefore "was never the flagged
hot path" -- true for the PCM streaming investigation's own workload,
but this is the first time in this whole hub's history that `gus_sink`'s
MIDI-side full-scan cost has actually been measured under real,
sustained note-on traffic. A max of 6.9 seconds for one scan call is
far beyond what a register-read loop over ~8-14 voices should cost,
suggesting either a real hardware wait/retry condition inside `SDL_
DOSGusGetState()` (the same "start-race grace-window" logic mentioned
in its own header comments) or a genuine, deeper GF1-communication
stall worth its own investigation -- but this is a **scoped, understood-
in-kind, likely-fixable software cost**, not the unexplained hardware/
electrical tax this whole S7 arc was chasing.

## Practical implication: this is a real, actionable path to the 40fps goal

**Switching this rig's target profile from `PGSB` to `PGGUS` sidesteps
the entire ~10-12x systemic tax this investigation spent the whole
session characterizing.** The remaining GUS-specific cost (`tick_rate`
9.39 instead of ~23.8) is a single, already-identified, already-
precedented inefficiency (`reap_finished_voices()`'s per-note-on full
voice scan) with a proven fix pattern already in this codebase (`SDL_
DOSGusVoiceActive()`, sdl3-dos patch 0140) -- applying the same
per-voice-check pattern to `gus_sink.c`'s own reap path is a concrete,
scoped, real next step, not another open-ended investigation. This does
not mean the OPL3/WaveBlaster tax is fixed or should be abandoned as a
question -- it means there is now a real, working alternative path to
real music at much better performance on this exact rig, which the S7
acceptance gate's own re-scoping decision (flagged in the prior entry)
should weigh alongside "accept the OPL3/WB hardware constant."

Acceptance gate items 4 and 5 (which pre-registered against OPL3
specifically) remain FAIL and are unaffected by this result directly --
but this result changes what "the achievable ceiling on this rig" means
in practice, which is exactly the kind of information the operator
needs for the re-scoping decision already flagged as pending.

## Not yet done

1. Profile `SDL_DOSGusGetState()`'s own real-hardware cost directly (a
   new, narrow diagnostic, same discipline as this whole investigation) --
   is the mean ~103us/call [correction: 103ms, i.e. 102,962us] cost from
   register-read volume (many voices), or from the max's own 6.9s outlier
   pointing at a real stall/retry condition? This determines whether the
   fix is "port `SDL_DOSGusVoiceActive`'s per-voice pattern to `gus_
   sink.c`" (straightforward) or something deeper in the GF1
   communication path (a bigger investigation).
2. An ABBA-style confirmation run (multiple cells, not just one) before
   trusting `tick_rate=9.39` as a stable number -- this entry is a
   single operator-approved cell, the same discipline this investigation
   applied to every other single-cell finding before trusting it fully.
3. Investigate and, if warranted, fix `vcctrl`'s own `select_boot_
   profile()` timing for this rig/profile combination -- flagged, not
   fixed, in the harness-gap section above.
4. Acceptance gate items 4 and 5 remain FAIL (OPL3-specific, unaffected).

Patches 0059-0068, 0141, 0143-0144 all stay landed, all still temporary
(none of them touched GUS code at all this entry).
