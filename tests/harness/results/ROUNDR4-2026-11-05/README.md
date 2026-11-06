# Round R4 ("as shipped") -- 2026-11-05 result: DIST1 FAIL as registered (one proxy condition), GUSC16 FAIL, ADLC16 VOID -- two real bugs found

One power-on: relay-on 21:25:52Z, power OFF 22:16:14Z (driver; powerguard confirmed), cap 22:35:52Z not reached. Operator's
standing order (ORDER-CONFIRMED). Pre-registrations f0c084a0 (+ the 4274abd2 zip). Release a1dba5d61624 in every scored cell
(DIST1's from the dist zip, byte-identical), pre-stage = staged = post-run. vcctrl: no USB event, no corrupt frame, the audio
stream never restarted (audio_spawns steady) -- the capture was clean all round.

| Cell | Boot | whole / steady | displayed | audio | verdict |
|---|---|---|---|---|---|
| WARMUPR4 | PGSB | 30.15 / 33.02 | -- | -- | not scored; camera shows the LCD (MMD title); close-watch passed |
| DIST1 | PGSB | 39.27 / 40.13, fps_p50 40.00 | 99.56% | SB PCM + OPL3 music 0, counters clean; sounds 10 x4, 9 x2 | **FAIL as registered**: no "Playing sound 3" |
| GUSC16 | PGGUS (attempt 2) | 39.23 / 40.12 | -- | midi=gus (GF1 found), GUS PCM, underruns=39631 | **FAIL** (capture-check3) |
| ADLC16 | PGADLIB | 39.53 / 40.08 | -- | **Audio is disabled** | **VOID** (no OPL2 line, no midi field) |

## DIST1 -- the zip plays at the gate rate, as shipped; FAIL on one registered condition

Every other registered condition is met: exit 0, room 3, `DOS-PORT fixed-timestep: ENABLED` (the release default; RUN.BAT
has no harness SETs but the log tags and the TAS exit), midi=opl3, music 0, gatebar S16 MET (39.27 / 40.13, fps_p50 40.00,
99.56% / 100.24%), counters clean, camera CLEAN (room 3 on the LCD, the character moves). The failing condition, "Playing
sound 3", depends on where the blind walk clicks land (R2's GR16 and 09-30's CAPS32 also lacked it); effects 9 and 10 played
six times. The condition was a poor proxy copied from CAPS16 (where sound 3 is the scorer's reference clip). Recorded as FAIL
as registered; the question asked (does the zip play at the gate rate with music and effects) is answered yes.

## GUSC16 -- the GUS backend runs but is not right (CAPTURE-CHECK3.txt)

K1 PASS (0 zero frames); **K2 FAIL** (a 1.02 s run at the floor while the render plays); **K3 FAIL** (sound 3 logged once but
not found: 0.42 vs null 0.43); **M1 -23 cents** (limit +-15); **M2 FAIL** (chroma 0.470 vs transposed 0.602); K4 PASS; D 0.40.
Counters: **underruns=39631** (the S7 GUS cells on 2026-09-15 read underruns=0). ULTRASND "240,3,3,7,7"; "native GF1 (Gravis
Ultrasound) backend active", 4,470 MIDI events, MIDI tick poll; the card stayed locked through the span (6 "frozen" samples,
at the start and the exit). Pre-registered: an M1/M2 FAIL with K1-K4 PASS would be reported as patch-set difference; here K2
and K3 fail too, and the underrun count points at the GUS PCM stream -- a **regression since 09-15**, not yet located.
DOSBox-X cannot reproduce it (its GF1 fails the probe; its GUS PCM path mixed 0 in a release-exe run today).

## ADLC16 -- no sound at all without a Sound Blaster (finding)

STDOUT: "Failed to init SDL audio subsystem: No BLASTER environment variable to find Sound Blaster" -> "Audio is disabled";
audio_vital_status=NA; no DosMidiBackend line. PGADLIB has no DSP and no BLASTER by design (g2k README.TXT), so the engine
turns off ALL audio, including the OPL2 music the FM chip at 388h could play without any SB. README.TXT's "If a backend's
hardware is not found, that part of the sound is off ... and the game still runs" is wrong for this case: an AdLib-only (or
MPU-only) player hears nothing. VOID as registered (its validity lines need the OPL2 line); the OPL2 question is unanswered.

## Follow-ups (PLAN-NEXT)

1. Audio init without a Sound Blaster: open the MIDI backend (OPL at 388h, MPU-401) when SB PCM fails, then re-run ADLC16.
2. GUS PCM regression since 09-15 (underruns 39,631): locate in the lab, then re-run GUSC16.
3. README.TXT: correct the sound section until 1 and 2 land; DIST1's proxy condition is not reused.

Files: SUMMARY.txt, driver and helpers, ORDER-CONFIRMED, POWERGUARD.txt, jobs/*.json. Captures stay local (AUDIO-SHA256.txt).
