# Round R1 (PLAN-NEXT step 4) -- 2026-11-05 result: RELEASE ABBA EQUIVALENT, release S8 MET x2, CAPR8 PASS

Operator approved the power-on directly (question tool, 2026-11-05, "Power on, run R1 now"); pre-registrations
cb108322 (before any data). One power-on: relay-on 16:05:10Z, power OFF 17:20:16Z (driver; powerguard confirmed
17:20:25Z), cap 17:25:10Z not reached. vcctrld daemon_start_t unchanged through the round (1793830502.59); no
daemon gap. Binaries: A instr.exe 7e5dfe26f272 (sha256 d72fe181...), B rel.exe a1dba5d61624 (1fc012c1...), both
main f2228d5e; every cell's pre-stage, staged and post-run sha256 agree and every stamp matched (SUMMARY.txt).

| Cell | Exe | whole-run / steady | fps_p50 | completeness | audio counters | room-35 load | gatebar |
|---|---|---|---|---|---|---|---|
| WARMUPR1 | l308 bc9c3704a839 | 30.14 / 33.02 (WARMUPBT 30.13 / 33.02) | -- | -- | -- | -- | not scored |
| R1I1 (A1) | instr | 39.23 / 40.24 | 40.00 | 99.34% | clean | 419 -> 825 ms | MET |
| R1R1 (B1) | rel | 39.27 / 40.27 | 40.00 | 99.48% | clean | 438 -> 862 ms | MET |
| R1R2 (B2) | rel | 39.23 / 40.24 | 40.00 | 99.44% | clean | 426 -> 851 ms | MET |
| R1I2 (A2) | instr | 39.25 / 40.28 | 40.00 | 99.44% | clean | 426 -> 831 ms | MET |
| CAPR8 | rel, 640x480 | 39.34 / 40.25 | 40.00 | 99.34% | clean | -- | (MET; not its question) |

"Clean" = silent_irqs 0, start_latency_irqs 0, overwrites 0, underruns 0, late_writes 0; pcm_irqs + inflight =
mixed in every cell (diff 0). BLASTER.TXT read "A220 I7 D3 P330 T3" in all six cells (the profile_witness).

## RELEASE ABBA (abba-r1.py, ABBA-R1.txt)

- Drift |A1-A2|: whole-run 0.02, steady 0.04 (limit 0.30): separable.
- whole-run: mean A 39.24, mean B 39.25, B - A +0.010. steady: mean A 40.26, mean B 40.255, B - A -0.005.
  Both within the operator's 0.10: **EQUIVALENT**. Prediction (B >= A on both) held on whole-run, missed on
  steady by 0.005 -- inside the noise (A drift 0.04).
- Release S8 x2: R1R1 and R1R2 both MET -> **the release flavour's S8 x2** (operator 2026-11-05).
- Decision (as registered): **gate cells move to the release flavour**. R2 drops GR8 and runs GR16, GR32P, GR16WB.
- Against GL8A/B (reported, not scored): mean B - GL8A = -0.010 / +0.025, - GL8B = -0.100 / -0.035. Whole-run
  margins over 39.2 are 0.03-0.07 this round (GL8A/B: 0.06-0.15). The room-35 load itself is 405-425 ms (GL8A
  418 ms), so ags 0354's commit is not visible in it; load_begin comes 207-226 ms later than GL8A's 212 ms in
  all four cells, both flavours, which is where the whole-run difference sits. Not chased in this round.

## CAPR8 (capture-check.py, CAPR8-2026-11-05/CAPTURE-CHECK.txt)

K1 0 digital-zero frames; K2 worst 16.6 dB (< 25); K3 effect NCC 0.41 vs reversed-clip null 0.13; K4 >= 51.0 /
44.0 dB over the floor; K5 pcm_irqs 2053, silent 0, overwrites 0, underruns 0, late 0 -> **CAPTURE CHECK PASS**.
Validity: stamp, build_dirty 0, room 35, one msgskip line, sound 11, ambient sound 18, music 9 and 4 logged,
exit 0, capture=ok (card locked through the span), one audio segment (no reconnect). Comparison CAPS8: K2 24.7,
K3 0.41 / 0.14, K4 52.8 / 47.8 -- the same scorer re-run on CAPS8's capture reproduces those figures exactly
(control in CAPTURE-CHECK.txt).

## Witnesses and rig

- Camera: reviewed for R1R1 and R1R2 (and the warm-up) against GL8A's 09-30 sheet. Room 35 is a dark night
  scene and the room was unlit; the sheets match GL8A's in brightness and content (figures move, no stuck or
  garbage regions), so CLEAN at the 09-30 standard -- which, at this exposure, can only catch gross faults.
- Capture stick (vcctrl's usb3 watch): 4 dropouts 16:58:33-16:58:55Z (R1I2), then off USB from 16:59:23Z
  ("Cannot enable. Maybe the USB cable is bad?"). It came back by itself, or by a physical replug, at
  17:02:07Z (device 40, after two more failed enumerations and a kernel port power-cycle at 17:02:03-06Z).
  The operator approved a sysfs port reset, but it was NOT run: vcctrl saw the request after the stick was
  back, and the Pi's journal has no sudo command 16:59:30-17:06Z. (Commit 68e2d303's message says the
  reset was done; that is wrong.) Capture absent 16:59:23-17:02:07Z, flaky from 16:58:33Z. Decode errors
  ("broken data stream", stick on USB): 2 at 16:20:26, 3 at 16:34:42-50, 3 at 17:12:16-24Z. The last
  three fall in CAPR8 before its scored span (17:12:49.5-17:14:25Z, the scorer's held run from the 17:07:13Z
  audio connect); every card-state sample in that span reads locked. CAPR8's non-locked samples are two
  short "frozen" windows (frames arriving, picture static) at 17:12:18-22Z and 17:14:28-33Z, the same shape
  as CAPS8's (17:13:48-52Z and 17:15:57-16:05Z on 09-30). The capture is a witness only; no ABBA figure
  reads it. The audio side-stream rides the stick: R1I2's recording ends at 16:59:23Z (not scored in R1I2).
- vcctrld 8e291c4's first hardware use with sends: 12 jobs (jobs/), every send ok/complete, every pull delivered
  STDOUT.TXT, the manifest, BLASTER.TXT and AGSSAVE.001; the missing names are the optional AUTOPLT.LOG,
  <TAG>SDL.LOG, WARNINGS.LOG and PH0n.BMP, absent on the card (as on 09-30). No `settle` warning in any job log
  or run-hw.out; no truncated command (every RUN.BAT effect is in its logs).
- USB4VC fw 0.5.107 at every lock take/release (snapshots, fw=OK); input logs ok in every cell.

Files: SUMMARY.txt (driver record), driveR1.sh / cellR1.sh / powerguard.sh / daemongap.sh / expected.txt /
ORDER-CONFIRMED (copied from build/ws/roundR1), POWERGUARD.txt, ABBA-R1.txt, jobs/*.json.
Game-music captures stay local; each cell's AUDIO-SHA256.txt records its sha256.
