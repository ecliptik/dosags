# S7-GUS -- acceptance gate item 4 ABBA, real-hardware result: PASS -- 2026-09-15 (new session, continued)

Operator-approved ABBA campaign, re-targeting acceptance gate item 4 at
GUS per the 2026-09-15 "S7 -- acceptance gate decision" entry. Design
pre-registered before touching the rig (see the session's own design
notes, reproduced below), then verified against source
(`Engine/main/config.cpp:416`'s `AudioEnabled` lever, `tools/port-game/
port_game.py`'s existing `ACSETUP-ON.CFG`/`ACSETUP-OFF.CFG` generator)
before the first cell ran.

## Pre-registered design

- **Lever**: `ACSETUP.CFG`'s `[sound] enabled=` (0/1) -- an existing,
  zero-patch AGS engine feature, the same lever the original OPL3 ABBA
  used.
- **Held constant across all four arms**: same `PGGUS` boot (one boot,
  no reboot between arms -- `ACSETUP.CFG` swapped locally via `COPY`
  instead, a deliberate adaptation from the original OPL3 ABBA's
  separate-boot-per-cell design that removes boot-profile-selection
  variance as a confound rather than adding one), same binary
  (`binary_sha12=54d51604e8d8`), `DOSAGS_FIXED_TIMESTEP=1` +
  `DOSAGS_TAS_AUTO_EXIT_TICK=200` every arm, no `SDL_HINT_DOS_GUS_DIAG`,
  no `SDL_HINT_DOS_GUS_PIO_AUTOINC` override (inherits the shipped
  default, `patches/ags/0074`), same game (Trilby's Notes, same
  `NOTES.AGS`).
- **Block**: A1(off) -> B1(on/GUS) -> B2(on/GUS) -> A2(off), tags
  `SGA1`/`SGB1`/`SGB2`/`SGA2`.
- **Pre-registered PASS/FAIL bar** (reused from acceptance gate item 4
  as originally written, not invented fresh): sound-on fps_p50 cost
  <= 1.5 against sound-off.
- **Pre-registered invalidity conditions**: A-to-A and B-to-B spread
  < 15% relative; A1/A2 should land near the existing sound-off
  reference (4.81/5.17 fps_p50, avg ~4.99, from the original OPL3 ABBA's
  own A1/A2 cells, `S7-abba-2026-09-13.md`, same exact workload/config)
  within roughly +/-20%.

CPU tier confirmed via `vcctrl_sysinfo` before the campaign: Intel
486DX2, ~66MHz -- the pass/fail-bearing HW-486-66 tier.

## Result

| Cell | Arm | fps_p50 | fps_p95 | tick_rate | duration_s | audio_vital_status |
|---|---|---|---|---|---|---|
| SGA1 | sound-off | 4.76 | 5.50 | 13.96 | 21 | NA |
| SGB1 | sound-on (GUS) | 4.81 | 5.71 | 12.22 | 24 | pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=76 |
| SGB2 | sound-on (GUS) | 4.81 | 5.45 | 12.25 | 24 | pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=76 |
| SGA2 | sound-off | 4.76 | 5.45 | 13.79 | 21 | NA |

All four: `exit_code=0`, identical scene path (`room_transition` into
room 1 at 12.5-13.3s), clean `***** ENGINE HAS SHUTDOWN`. Sound-on arms
confirm `DosMidiBackend: native GF1 (Gravis Ultrasound) backend active`
in STDOUT; sound-off arms correctly show no `DosMidiBackend` line at
all (audio subsystem skipped) and `audio_vital_status=NA`, matching the
lever's intended effect exactly.

## Invalidity checks (all pass)

- **A-to-A spread**: 4.76 vs 4.76 -- 0.00, byte-for-byte identical.
- **B-to-B spread**: 4.81 vs 4.81 -- 0.00; `events=76` both times,
  fully deterministic.
- **Baseline reproduction**: today's A1/A2 (4.76) vs. the original OPL3
  ABBA's own sound-off baseline (avg 4.99, 2026-09-13, same exact
  workload/config) -- within ~4.6%, well inside the +/-20% band.

Block is valid on every pre-registered check.

## Verdict

Baseline (sound-off) avg fps_p50 = 4.76. Sound-on (GUS) avg fps_p50 =
4.81. **Cost = -0.05 fps** (sound-on is marginally faster, not slower --
noise, not a real effect) **against the <= 1.5 fps pre-registered bar:
PASS, decisively.** GUS mode's fps cost against sound-off is
indistinguishable from zero.

`tick_rate` shows a real, small, secondary GUS cost (13.9 sound-off vs.
12.2 sound-on avg, ~12% relative) -- the residual scoped cost of GUS's
own per-tick bookkeeping (`gusscan` etc.), consistent with everything
this sub-investigation has already found, but it does not translate
into a measurable fps_p50 hit at this tier/workload, and fps_p50 (not
tick_rate directly) is what acceptance gate item 4 is written against.

## Conclusion

**Acceptance gate item 4, re-targeted at GUS: PASS.** This closes the
GUS voice-scan-cost concern the milestone's work order originally
opened (that concern turned out to be a red herring -- the real cost
was the upload-path issue already fixed via `patches/ags/0074`, and the
diag-logging confound already root-caused and closed this session), and
supersedes the informal, non-ABBA data points (`GUST1`, `GUSN1`, etc.)
that motivated pursuing GUS in the first place.

**Acceptance gate item 5** (the milestone claimed with operator
sign-off): this result is the evidence; the sign-off itself is left to
the operator, per this hub's own standing practice of never claiming a
milestone unilaterally.

## Not yet done

1. Operator sign-off on acceptance gate items 4 and 5 for the Sound
   milestone.
2. Once signed off: mark the `S7-GUS` work-order item and the top-level
   `Sound` milestone checkbox in `PLAN.md` accordingly.
3. Housekeeping still pending from earlier this session: the remaining
   entangled S7 diagnostic patches (`ags/0059,0061,0062,0067,0068`,
   `SDL/0141`) stay landed until/unless a future session decides the
   GUS diagnostics they support are no longer needed.
