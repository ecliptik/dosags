# S7-GUS -- default GUS PIO autoinc, real-hardware result: NO FREEZE, but an unexplained regression elsewhere -- 2026-09-15 (new session, continued)

Operator-approved cell (tag `GUSA1`, `binary_sha12=54d51604e8d8`, the
patch `ags/0074` build -- `SDL_HINT_DOS_GUS_PIO_AUTOINC=1` now this
port's own default). Treated as a safety-critical FIRST real-hardware
exposure of autoinc mode, not a routine re-measure, per the operator's
own explicit choice ("land it, test as its own careful single cell
first") after autoinc was found to have never been exercised on real
GF1 hardware since SDL patch SDL/0112 introduced it in June 2026 as the
fix for a documented CPU-freeze hazard in the path it replaces.

## Safety measures taken

`SDL_HINT_DOS_GUS_DIAG=1` set for this run specifically (the existing
byte-offset progress diagnostic `gus_upload_pio()` already implements,
built for exactly this purpose -- "last line before a freeze pins where
the ISA bus wedged"), and the run was actively monitored throughout
(periodic live checks, not a blind wait-then-collect), per this
session's own explicit safety plan. No hang or freeze was observed at
any point.

## Boot-profile workaround: a more precise characterization this session

`--boot-profile 3` automation failed again (back to its usual failure
mode after `GUSU1`'s own single success). The manual LED-edge
workaround needed 5 attempts. Video/timeline analysis found the real
interactive boot-menu window is only ~1.2s wide, and the capture channel
goes fully dark/desynced during exactly that window, making blind or
reactive timing unreliable in either direction. Success came from a
DENSE keystroke burst (~every 0.15s) fired across a WIDE t+18-34s
window, rather than a single well-timed burst. This is a more precise
characterization of the same already-flagged timing hazard, not a new
one, and still not fixed -- see the note below on cumulative evidence.

## Result

```
[RUNMANIFEST] binary_sha12=54d51604e8d8 duration_s=100 exit_code=0 fps_p50=0.51 fps_p95=0.59 audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=1083
DOS-PORT tick_rate=2.31 frames_skipped=168
DOS-PORT audioprb slots_us(min=93 mean=283735 max=6275028) gusscan(calls=530 min_us=5176 mean_us=22623 max_us=235817) voicefreq(calls=530 mean_us=18) voicevol(calls=587 mean_us=34) voicepan(calls=530 mean_us=9) voicestart(calls=530 mean_us=55) voicestop(calls=515 mean_us=19) miditick(calls=19 mean_us=640049 max_us=1448099) uploadpio(calls=22 min_us=36668 mean_us=240545 max_us=581420 bytes=712114) uploadsample(calls=22 mean_us=246367 max_us=589587 bytes=712114) prepsong(calls=1 max_us=6274811)
DOS-PORT tickfx catchup_us(min=746319 mean=2064168 max=29619292) realtick_us(mean=944369 max=6692123)
```

`STDOUT.TXT` confirms `DosMidiBackend: native GF1 (Gravis Ultrasound)
backend active`, the identical scene/script path as `GUSU1` (room -10
-> room 1, same `PlayMusic` calls, `room_transition t_ms=20670`, close
to `GUSU1`'s own). `exit_code=0`, clean shutdown, no crash, no hang.
Both local and staged sha256 matched throughout.

## The safety question: answered, cleanly

**No freeze, no hang, no instability observed at any point** during
active monitoring, including through the ~6.3-second `prepsong` upload
window itself. The specific documented hazard this cell was designed to
test for did not materialize on this rig's current PicoGUS firmware
with this song's data.

## The performance question: NOT what was hypothesized, and a new, unexplained anomaly

**The targeted fix barely moved.** `prepsong` (6,274,811us) is only
~9% faster than `GUSU1`'s non-autoinc baseline (6,891,245us) --
nowhere near the ~6x hypothesized from the "~6 outportb/byte -> ~1
outportb/byte" comment. `uploadpio`'s own mean per-call cost
(240,545us) is only ~13% better than `GUSU1`'s (274,958us) for the
IDENTICAL 712,114 bytes transferred. Whatever autoinc mode is actually
doing on this real hardware, it is not delivering anything close to the
expected per-byte port-op reduction.

**Something else got dramatically worse, unrelated to the upload path
on its face**: `tick_rate` collapsed from `GUSU1`'s 9.34 to **2.31**
(a >4x regression); `duration_s` grew from 28 to **100** for the
identical `DOSAGS_TAS_AUTO_EXIT_TICK=200` target; total MIDI events
dispatched grew from 76 to **1083** (a ~14x increase); and
`SDL_DOSGusGetState()` -- a function this patch does not touch at all,
already measured and exonerated as cheap (~106-170us/call) in THREE
prior real-hardware cells this sub-investigation -- ballooned to a
**22,623us mean per call** (a ~213x increase) across 530 calls (a ~19x
increase in volume). Cumulatively, `gusscan` alone now costs
**~11.99 SECONDS** of real time across this one run, versus ~3
milliseconds in `GUSU1`. `tickfx`'s own `catchup_us` max also spiked to
**29,619,292us (~29.6s)** -- a single catch-up tick nearly 5x longer
than `GUSU1`'s own worst catch-up tick (4,013,841us).

**Two competing, NOT yet distinguished explanations, both plausible**:

1. **A real correctness/interaction defect in autoinc mode itself.**
   If the auto-increment DRAM pointer state is corrupted or left in an
   unexpected condition by *something* (a register-select collision
   between the upload's own bounded bursts and any other GF1 register
   traffic during the ~6s upload window, or a subtler timing
   sensitivity the per-byte address-reselect path happened to mask),
   this could plausibly leave the GF1's voice-tracking state confused
   for the REST of the session -- explaining why `gusscan` (a function
   that reads `voice_active_mask`, directly sensitive to real voice
   state) got dramatically more expensive and more frequent long after
   the upload itself finished, not just during it.
2. **A downstream confound with no defect in autoinc at all.** If
   something else (independent of autoinc) made this specific run's
   real wall-clock pacing slower for any reason, more real time would
   let `midi_sched_tick()`'s own catch-up window (`delta_ms>10000`
   clamp) advance further through the song per call, dispatching more
   events (explaining the 76->1083 jump largely on its own) and
   allocating/reaping more voices (explaining `gusscan`'s call-COUNT
   increase, though not obviously its dramatic PER-CALL cost increase).

**Neither is confirmed.** This single cell cannot distinguish them --
exactly the situation this whole sub-investigation has repeatedly
warned against trusting without a proper comparison (`GUST1`/`GUSD1`
already established a single cell needs corroboration before treating
a finding as settled). The `gusscan` per-call cost increase in
particular has no obvious confound-only explanation and is the
strongest reason to suspect a real interaction issue, not pure noise.

## Recommendation

**Given the net real-hardware effect of `patches/ags/0074` on the one
cell measured is a large REGRESSION (tick_rate 9.34 -> 2.31), not an
improvement, it should not remain this port's shipped default while
this anomaly is unexplained** -- even though the specific freeze hazard
it was tested for did not occur. A future session should either revert
`patches/ags/0074` back to the well-proven (if slow) default, or run a
tightly-controlled follow-up (a second autoinc-on cell under matched
conditions, ideally alongside a non-autoinc control in the SAME
session) before drawing any conclusion either way. Not decided in this
entry -- left for the operator/parent session.

## Not yet done

1. Decide whether to revert `patches/ags/0074` or investigate the
   `gusscan` anomaly further with a controlled comparison first.
2. If investigating further: a same-session A/B (autoinc on, then off,
   back to back, same song, same boot) would directly distinguish the
   two competing explanations above -- a single autoinc-on cell cannot.
3. `vcctrl`'s own boot-profile timing hazard has now been characterized
   more precisely (a ~1.2s real interactive window, capture-blind
   during it) across FIVE sessions with mixed automated-path outcomes
   (1 success / 4 failures) -- still unresolved, still a strong
   candidate for its own focused `~/git/vcctrl` session.
4. Acceptance gate items 4 and 5 (re-targeted at GUS) remain open --
   further from being closeable than before this cell, given the net
   regression.
