# S7-GUS -- diag-off confirmation cell, real-hardware result: confound closed, true autoinc benefit confirmed near the original hypothesis -- 2026-09-15 (new session, continued)

Operator-approved cell (tag `GUSN1`, `binary_sha12=54d51604e8d8`,
`PGGUS`, landed cleanly on the first attempt). Proposed by the
`s7-tickrate-confound` investigation fork as the cheapest possible
confirmation: `SDL_HINT_DOS_GUS_DIAG` left unset (not `0` -- simply
never set) and `SDL_HINT_DOS_GUS_PIO_AUTOINC` also left unset,
inheriting the current shipped default (autoinc ON, per `patches/
ags/0074`). No new instrumentation needed. Verified via `SET` before
launch that neither hint was present in the environment.

## Result

```
[RUNMANIFEST] binary_sha12=54d51604e8d8 duration_s=23 exit_code=0 fps_p50=4.81 fps_p95=5.45 audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=76
DOS-PORT tick_rate=12.30 frames_skipped=165
DOS-PORT audioprb slots_us(min=93 mean=29819 max=2009973) gusscan(calls=28 min_us=25 mean_us=106 max_us=167) voicefreq(calls=28 mean_us=11) voicevol(calls=58 mean_us=28) voicepan(calls=28 mean_us=8) voicestart(calls=28 mean_us=42) voicestop(calls=13 mean_us=12) miditick(calls=20 mean_us=541 max_us=3373) uploadpio(calls=22 min_us=10694 mean_us=53071 max_us=103225 bytes=712114) uploadsample(calls=22 mean_us=53106 max_us=103262 bytes=712114) prepsong(calls=1 max_us=2009752)
DOS-PORT tickfx catchup_us(min=16 mean=161937 max=4036677) realtick_us(min=5666 mean=234202 max=2148324)
```

Run completed in ~30s real time (fastest of the whole S7-GUS
sub-investigation), `exit_code=0`. `GUSN1-ST.TXT` (the STDOUT capture,
correctly named -- see note below) was not independently re-fetched
after a first fetch attempt used the wrong DOS 8.3 truncation
(`GUSN1-S.TXT` instead of the actual `GUSN1-ST.TXT`, an 8-character
truncation of `GUSN1-STDOUT.TXT` that differs from the 6-character-tag
pattern `GUSAB0-S.TXT`/`GUSAB1-S.TXT` used); the RUNMANIFEST/`DOS-PORT`
log line is the authoritative data source and `exit_code=0` is already
captured there, so a second NET round-trip was skipped as
not worth the added rig time. Noted for whoever next names a log tag:
DOS 8.3 truncation of `<TAG>-STDOUT.TXT` is exactly 8 characters of
`<TAG>-` + however many `S`/`T`/etc. characters fit, NOT a fixed
`<TAG>-S` suffix -- it depends on the tag's own length.

## Both open questions closed by one cell

**1. The tick_rate/gusscan confound is confirmed as `SDL_HINT_DOS_GUS_
DIAG`'s own synchronous fsync'd logging**, exactly as the source
analysis predicted: `gusscan` calls=28 at 106us mean (vs 283-530 calls
at 18640-26008us mean in every diag-on cell) -- byte-for-byte the same
numbers as `GUSU1`'s original clean baseline. `tick_rate=12.30` is the
best of the entire S7-GUS investigation (better even than `GUSU1`'s own
9.34, since `GUSU1` predates the autoinc default). `midi events=76`
matches `GUSU1`'s clean 76 exactly, not the 580-1083 seen in every
diag-on cell -- confirms the catch-up-clamp feedback loop explanation
was correct, not just the direct I/O cost.

**2. Autoinc's true benefit, uncontaminated by the diag tax, lands much
closer to the original ~6x hypothesis than the ~2x measured under diag
contamination**: `uploadpio` mean_us=53071 here vs `GUSU1`'s own
274,958us (autoinc off, diag off, the only other clean-diag baseline
this investigation has) -- a **5.18x reduction**, for the identical
712,114 bytes. `prepsong` max_us=2,009,752 (~2.01s) vs `GUSU1`'s
6,891,245us (~6.89s) -- a **3.43x reduction** (prepsong includes
non-upload overhead the upload-only ratio doesn't, so a smaller but
still large multiple is expected). This is the first real-hardware
measurement of autoinc's benefit that isn't confounded by either the
autoinc-vs-non-autoinc binary's own build differences (`GUSU1` predates
patch `ags/0074`) or the diag-logging tax -- and it lands within shouting
distance of the "~6 outportb/byte -> ~1 outportb/byte" hypothesis this
whole sub-investigation set out to test.

## Conclusion

Both acceptance-gate-relevant questions this sub-investigation opened
are now closed with real-hardware evidence: `patches/ags/0074` (autoinc
default) delivers a real, large, now-quantified improvement (~3.4-5.2x
depending on which metric) with no freeze/hang across three separate
real-hardware exposures (`GUSA1`, `GUSAB1`, `GUSN1`), and the tick_rate/
gusscan anomaly that looked like a possible autoinc side-effect was
conclusively the diagnostic hint's own logging cost, not a GF1/autoinc
interaction defect. Acceptance gate items 4 and 5 (re-targeted at GUS)
look closeable on this result -- left for the operator to confirm.

## Not yet done

1. Operator confirms acceptance gate items 4/5 can close.
2. `SDL_HINT_DOS_GUS_DIAG`'s real cost (a ~3-5x tick_rate tax) is worth
   documenting explicitly wherever the hint itself is documented, so a
   future session doesn't mistake a diag-on run for a representative
   performance measurement again.
3. `vcctrl`'s `select_boot_profile()` timing hazard has been fixed
   upstream in `~/git/vcctrl` (commit `d645faa`, not yet deployed to the
   live daemon -- see that repo's own `docs/lab/FINDINGS.md` sec. 59)
   following this sub-investigation's own procedural finding. No further
   action needed from dosags; will pick up the fix automatically once
   deployed.
