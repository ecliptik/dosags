# S7-GUS -- autoinc on/off same-session A/B, real-hardware result: anomaly does NOT track autoinc -- 2026-09-15 (new session, continued)

Operator-approved cell pair (tags `GUSAB0` control / `GUSAB1` test,
`binary_sha12=54d51604e8d8` per both RUNMANIFESTs -- the locally rebuilt
`build/ags/ags.exe` hashes differently (`11fe46e59f7a...`) despite an
identical, clean working tree at the same HEAD as the GUSA1 build; sizes
match exactly (8,197,381 bytes) and both RUNMANIFESTs self-report
`54d51604e8d8`, so this is read as non-reproducible DJGPP link metadata
(e.g. an embedded timestamp), not a source difference -- the staged
binary was not re-staged). Both runs launched back-to-back from the SAME
`PGGUS` boot, no reboot between them, per the operator's own explicit
design for this cell: only `SDL_HINT_DOS_GUS_PIO_AUTOINC` (and the
`DOSAGS_LOG_TAG`/`DOS_PORT_LOG_TAG` pair) changed between the two runs.
`SDL_HINT_DOS_GUS_DIAG=1` set throughout; both runs actively monitored
for a hang (periodic `vcctrl_burst` content checks, not a blind wait).
**No freeze, no hang, in either run.**

## Boot-profile workaround: three attempts this session

`--boot-profile` automation was not used this session (the tool-access
blocker in the handoff meant this session replicated `select_boot_
profile()`'s own LED-edge logic directly via MCP calls rather than
shelling out to the CLI). First two attempts (reactive: poll for the
capslock/scrolllock POST-edge, then fire) both landed on the menu
DEFAULT (`PGSB`), not `PGGUS` -- confirmed via `SET`'s `CONFIG=PGSB` and
literal `3` / `Bad command or file name` echoes at the prompt, meaning
the keystrokes arrived AFTER the ~5s interactive window had already
closed. Root cause: this session's own MCP round-trip latency (~9-12s
per individual `vcctrl_key` call) is too slow for a reactive
detect-then-fire approach -- by the time a poll result was received and
acted on, real time had already advanced past the window. Third attempt
switched to PROACTIVE, packed multi-key calls (15x `3`+`enter` in one
`vcctrl_key` call, letting the daemon's own internal pacing fire them
quickly) sent at two fixed offsets (~t+14s and ~t+23s post-`ctrl+alt+
delete`) without waiting for LED confirmation first -- landed on `PGGUS`
cleanly (`CONFIG=PGGUS`, `SDL_HINT_DOS_AUDIO_BACKEND=gus`,
`ULTRASND=240,3,3,7,7` confirmed via `SET`). Added evidence for `vcctrl`'s
own already-flagged `select_boot_profile()` timing hazard: the fix here
is procedural (proactive packed bursts beat reactive polling when
per-call latency is high), not a vcctrl code change.

## Result

```
GUSAB0 (control, autoinc=0):
[RUNMANIFEST] binary_sha12=54d51604e8d8 duration_s=80 exit_code=0 fps_p50=0.79 fps_p95=0.83 audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=580
DOS-PORT tick_rate=2.93 frames_skipped=168
DOS-PORT audioprb slots_us(min=93 mean=288189 max=11271680) gusscan(calls=283 min_us=4431 mean_us=26008 max_us=236168) voicefreq(calls=283 mean_us=18) voicevol(calls=373 mean_us=33) voicepan(calls=283 mean_us=9) voicestart(calls=283 mean_us=56) voicestop(calls=268 mean_us=19) miditick(calls=19 mean_us=392309 max_us=1138942) uploadpio(calls=22 min_us=81968 mean_us=467151 max_us=1010760 bytes=712114) uploadsample(calls=22 mean_us=473557 max_us=1019489 bytes=712114) prepsong(calls=1 max_us=11271459)

GUSAB1 (test, autoinc=1):
[RUNMANIFEST] binary_sha12=54d51604e8d8 duration_s=71 exit_code=0 fps_p50=0.79 fps_p95=0.86 audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=572
DOS-PORT tick_rate=3.32 frames_skipped=168
DOS-PORT audioprb slots_us(min=93 mean=167476 max=5511241) gusscan(calls=283 min_us=5216 mean_us=18640 max_us=98901) voicefreq(calls=283 mean_us=18) voicevol(calls=337 mean_us=34) voicepan(calls=283 mean_us=9) voicestart(calls=283 mean_us=56) voicestop(calls=268 mean_us=19) miditick(calls=19 mean_us=282525 max_us=829114) uploadpio(calls=22 min_us=36204 mean_us=205284 max_us=405659 bytes=712114) uploadsample(calls=22 mean_us=211185 max_us=410297 bytes=712114) prepsong(calls=1 max_us=5511020)
```

Both `STDOUT.TXT`s confirm `DosMidiBackend: native GF1 (Gravis Ultrasound)
backend active`, the identical scene/script path (room -10 -> room 1,
`room_transition t_ms=18419` control / `t_ms=17937` test -- close to each
other), clean `***** ENGINE HAS SHUTDOWN`, `exit_code=0` both. All four
fetched files (`GUSAB0.LOG`, `GUSAB1.LOG`, `GUSAB0-S.TXT`, `GUSAB1-S.TXT`)
verified byte-size-clean on transfer.

## The comparison this cell was designed to make

**Both runs this session are degraded relative to `GUSU1`'s historical
clean baseline** (`tick_rate=9.34`, `duration_s=28`, `gusscan` calls~28 at
~106-170us mean) -- including the CONTROL run, `autoinc=0`, which should
reproduce that baseline if autoinc were the sole cause of `GUSA1`'s
anomaly. It does not: `GUSAB0` shows `tick_rate=2.93`, `duration_s=80`,
`gusscan` calls=283 at 26008us mean, and a `prepsong` cost
(11,271,459us, ~11.3s) that is WORSE than `GUSU1`'s own non-autoinc
baseline (6,891,245us) and worse than `GUSA1`'s autoinc-on prepsong
(6,274,811us). **A run with autoinc explicitly OFF, in this session,
reproduces the GUSA1-shaped anomaly (low tick_rate, inflated gusscan,
inflated prepsong) just as strongly as GUSA1's own autoinc-ON cell did.**
This is the single most important fact this A/B produces: whatever drove
`GUSA1`'s degradation, it is present here with autoinc OFF, so **autoinc
is not the cause of the anomaly.**

**Within this session, holding the confound constant, `autoinc=1`
(`GUSAB1`, run second) outperformed `autoinc=0` (`GUSAB0`, run first) on
every metric**: `gusscan` mean_us 18640 vs 26008 (~28% lower), `prepsong`
max_us 5,511,020 vs 11,271,459 (~2.05x faster, the closest this whole
investigation has come to the ~6x hypothesis, though still well short of
it), `uploadpio` mean_us 205284 vs 467151 (~2.28x faster for the
identical 712,114 bytes), `duration_s` 71 vs 80, `tick_rate` 3.32 vs 2.93,
midi events 572 vs 580 (comparable, not a repeat of `GUSA1`'s 580-vs-1083
blowout since BOTH arms this session dispatch a similar, elevated count).
**This is the direction the original "~6 outportb/byte -> ~1 outportb/byte"
hypothesis predicted, just smaller in magnitude than hoped.**

**One caveat this single A/B pair cannot rule out**: `GUSAB0` ran first
(right after the fresh boot) and `GUSAB1` ran second. A monotonic
run-order or hardware-warm-up effect independent of autoinc could also
produce "second run faster than first run" -- this pair alone cannot
fully separate "autoinc helps" from "later runs in a boot are faster for
an unrelated reason." The cross-session finding (both arms degraded vs.
`GUSU1`) does NOT have this confound, since it compares each run
independently against a different session's baseline -- that comparison
is the reliable one.

## Conclusion

**The GUSA1 anomaly was a session-level confound, not an autoinc
defect.** Evidence: this session's own autoinc-OFF control run reproduces
the anomaly-shaped degradation just as strongly as GUSA1's autoinc-ON
cell did, which is inconsistent with autoinc being the cause. Within the
same confounded session, autoinc never regressed anything and
consistently improved the upload-path metrics it was meant to improve
(prepsong, uploadpio, gusscan), in the hypothesized direction if not the
hypothesized magnitude. **This does not support reverting `patches/
ags/0074`.**

**A separate, still-open, and now better-evidenced question**: something
about session/rig state (unrelated to the `SDL_HINT_DOS_GUS_PIO_AUTOINC`
hint) can depress `tick_rate` from ~9.3 to ~2.3-3.3 and inflate `gusscan`
cost by ~150-250x -- present in THREE of the last four real-hardware GUS
cells now (`GUSA1`, `GUSAB0`, `GUSAB1`), absent only in `GUSU1`/`GUST1`/
`GUSD1`/`GUSV1`. This is a real, sizeable, gameplay-relevant regression
from the best-known-clean baseline and deserves its own investigation,
separate from the autoinc question this cell resolves. No hypothesis for
it is confirmed yet.

## Recommendation

**Keep `patches/ags/0074`** (autoinc default ON) -- the freeze hazard it
was written to fix has now been tested twice on real hardware with no
freeze, and this same-session A/B found no case where autoinc regressed
anything relative to its own control. Left for the operator to confirm,
per this investigation's standing practice of not deciding this
unilaterally.

**Separately track** the session-level `tick_rate`/`gusscan` confound as
its own open investigation -- not blocking, not evidence against
autoinc, but a real unexplained regression worth its own root-cause pass
(candidates not yet ruled out: PicoGUS firmware/thermal state, rig
scheduling/timing variance, something in this specific `AGS.EXE` build's
non-source-visible state). Acceptance gate items 4 and 5 remain open
pending that separate investigation, since the underlying tick_rate cost
is still present regardless of the autoinc decision.

## Not yet done

1. Root-cause the session-level tick_rate/gusscan confound (candidate
   for its own dedicated investigation).
2. If the operator confirms keeping `patches/ags/0074`: revert the
   now-fully-spent S7 non-GUS diagnostic patches
   (`patches/ags/0059-0068`, `patches/SDL/0141,0143-0144`) and decide on
   the GUS-specific diagnostics (`patches/SDL/0145-0147`,
   `patches/ags/0069-0073`) -- keep while the confound above is still
   being chased, since `SDL_HINT_DOS_GUS_DIAG` and the `gusscan`
   instrumentation are exactly what a follow-up investigation would
   reach for first.
3. `vcctrl`'s own `select_boot_profile()` timing hazard: this session
   adds a concrete data point (reactive polling fails when per-call MCP
   latency is ~9-12s; proactive packed multi-key bursts at fixed offsets
   worked first-try) -- still a good candidate for its own focused
   `~/git/vcctrl` session, now with a specific procedural workaround to
   fold in.
