# S5 GUS, GUSQ2 -- real-hardware confirmation, HW-486-66, 2026-09-13

Raw evidence for the `GUSQ2` cell already narrated in `PLAN.md` ("Current
state (2026-09-13, same day -- S5 GUS, real-hardware confirmed, S5 fully
done)"), collected here as its own commit per that section's own
follow-up note. AGS Quest under `PGGUS` (native GF1 MIDI + `gus_pcm_stream`
PCM together), same package/binary as the failed `GUSQ1` attempt, with the
`SDL_DOSGusVoiceActive` fix (patch 0140) applied.

Pulled via `vcctrl get-file ... --from C:\DOSAGS` in a later session than
the one that produced the run -- independently re-verified against the
numbers PLAN.md already recorded, not just trusted from the prior
write-up.

## Result

`GUSQ2.LOG` (RUNMANIFEST): `duration_s=554`, `exit_code=0`,
`fps_p50=9.62`/`fps_p95=10.09`, `tick_rate=6.48`,
`audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=gus,
events=146`, `critical_count=0`, `warn_count=0`.

Matches or beats every prior real-hardware baseline (S2 PCM-only
577s/8.65/6.02, S4MIDI1 OPL3 609s/8.57/5.90, S5WB WaveBlaster
608s/8.57/5.91) -- zero underruns, zero regression.

`STDOUT.TXT` ends cleanly: `DosMidiBackend: native GF1 (Gravis Ultrasound)
backend active` at the audio phase, then a normal `Quitting the game...`
/ `***** ENGINE HAS SHUTDOWN`.

Screenshots (`PH01/02/03.BMP`) are byte-for-byte identical
(`9f9d9bd9...`/`6051787...`/`5b98f4da...`) to the pre-existing S2/S4/S5WB
baseline -- zero visual regression from the GUS backend or its fix.

`AUTOPLT.LOG` is the harness's cumulative append-mode log (every run since
this rig's first ever cell is in there, `mode: ab`); the `GUSQ2` cell is
the final block, ending `phase=quit status=begin tick=3564 room=3`.

## Open item, not chased further here

The directory listing captured during this pull also shows a `GUSQ1.LOG`
(546 bytes) now present on the card -- PLAN.md's own GUSQ1 write-up says
"no GUSQ1.LOG (RUNMANIFEST) was ever written." Neither `GUSQ1.LOG` nor a
GUSQ1-specific `STDOUT.TXT` (overwritten by GUSQ2's own run, since both
share the same on-target filename) was pulled in this session -- worth a
follow-up look, but doesn't change S5's already-confirmed conclusion.
