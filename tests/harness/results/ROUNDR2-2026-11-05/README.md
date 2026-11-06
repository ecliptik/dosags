# Round R2 (PLAN-NEXT step 4) -- 2026-11-05 result: GR32P MET, GR16WB PASS, GR16 figures MET but UNWITNESSED

One power-on: relay-on 19:49:57Z, power OFF 20:57:15Z (driver; powerguard confirmed 20:57:22Z), cap 21:04:57Z
not reached; vcctrld daemon_start_t unchanged (1793905813.82). Binary: rel.exe a1dba5d61624 (sha256 1fc012c1...),
pre-stage = staged = post-run in every cell. Pre-registrations de57a55e (before any data).

Power-on: operator, directly (question tool, 2026-11-05 ~19:49Z), "Power on now, waive the bar" -- after
being told the bar they set that morning was NOT met (vcctrl 11:48 PST: no cable or stick swap; 37.5 min clean
since vcctrl's 11:11 PST auto-recovery test). The round ran on the R1 cable/stick (vcctrld a14fce5
auto-recovery live). See ORDER-CONFIRMED.

Witness deviation: the operator pointed the room camera away and switched the Gateway's LCD off during the
round (vcctrl, during GR16WBR). Asked directly (question tool), the operator chose "Accept the capture sheet":
the VGA-capture frame sheet stands in for the camera in GR16 / GR32P (and the WB pair's "screen CLEAN"). The
camera and LCD were back by 20:56:55Z, after GR32P's run.

| Cell | whole-run / steady | fps_p50 | completeness | audio counters | screen witness | verdict |
|---|---|---|---|---|---|---|
| WARMUPR2 (l308) | 30.14 / 33.03 | -- | -- | -- | capture nolock (as R1) | not scored; close-watch passed (capture present, locked) |
| GR16WBP (poll) | 39.53 / 40.02 | -- | -- | midi_tick=poll | capture sheet clean | valid control |
| GR16WBR (pump) | 39.49 / 40.02 | -- | -- | midi_tick=rtc | capture sheet clean (idle room 13) | **PASS** (depth-score) |
| GR16 (S16) | 39.27 / 40.11 | 40.00 | 99.54% | clean | **none** (see below) | figures MET; **not a gate reading** |
| GR32P (S32P) | 39.29 / 40.12 | 40.00 | 99.52% | clean | capture sheet clean | **MET x1** |

BLASTER.TXT read "A220 I7 D3 P330 T3" in all five cells. "Clean" = silent_irqs 0, start_latency_irqs 0,
overwrites 0, underruns 0, late_writes 0, pcm_irqs + inflight = mixed (GATEBAR.txt per cell; gatebar was given
the one cell twice, so its "x2" line means nothing here -- the cell line is the reading).

## WB pair (GR16WBR-2026-11-05/DEPTH-SCORE.txt)

depth-score.py --sha a1dba5d61624 --no-pcm (the registered line): gate A PASS (late 0, plan_behind 0, qfull 0,
stuck 0/0/0/0, clk 0.9998, isr_writes 99.9% of model); B chroma 0.963 vs bar 0.627 (transposed 0.369, reversed
0.731, 0 pump onsets in the control's rests); D 0.744 (bar 0.70); control D 0.779 (information) -> **VERDICT:
PASS**. Comparison WBC16R (ef123dba0adf): B 0.973 / 0.634, D 0.785 -- the same scorer reproduces it exactly.
Validity: midi_tick rtc / poll, room 13, no PCM logged, one audio segment each, card locked through the scored
window (GR16WBR 12:22:01-12:23:41 PST; its 7 non-locked "frozen" samples are 12:21:47-54 and 12:24:34-39, static
idle screen, outside it).

## GR16: no screen witness

The capture card never locks the 512x384 mode (stale_kind "nolock"; GL16A/B on 09-30 were capture STALE too and
stood on the camera), so the capture sheet shows only the boot text then blank frames; the camera sheet shows
the dark room it was pointed at. The bar needs a clean screen witness, so GR16 is recorded as figures MET
(39.27 / 40.11 vs GL16A/B 39.29 / 40.13 and 39.29 / 40.10), witness absent -- **not a gate reading**. It
needs a re-run with the camera and LCD on (PLAN-NEXT).

## GR32P

MET on every figure (vs GL32A/B 39.28 / 40.12 and 39.34 / 40.07: whole-run inside their range, steady equal to
GL32A's). Capture sheet: 5 Days room 3 at 640x480 32-bit, the character moves between frames, no stuck or
garbage regions -> CLEAN. 7 of 112 card samples non-locked, all in the exit and fetch.

## Rig

vcctrl's usb3 watch: no USB event all round (dev 41 throughout; no disconnect, -71 or "Cannot enable"; no
auto-recovery). One corrupt capture frame (seq 127525, ~20:21:47Z, read 3 times), inside GR16WBR before its
scored window; 3 decode errors of 224,641 attempts. vcctrld 10 jobs (jobs/): every send ok/complete, every pull
delivered STDOUT.TXT, the manifest, BLASTER.TXT and AGSSAVE.001 (the optional names absent as in R1); no
`settle` line anywhere. USB4VC fw 0.5.107 at every lock take/release.

Files: SUMMARY.txt, driveR2.sh / cellR2.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED
(copied from build/ws/roundR2), POWERGUARD.txt, jobs/*.json. Game-music captures stay local (AUDIO-SHA256.txt).
