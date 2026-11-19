# REFAQ0379-2026-11-13 -- DOSBox-X reference renders for round RP (the lockable-mode audio check), made before any rig data

LAB ONLY (DOSBox-X). The reference sdlports' terms ask for: "a DOSBox-X render of that same binary and flow, made BEFORE the
round". Round RP's bar B1 accepts exactly the pcm_irqs values seen in the five REGISTERED renders (REFAQB1-5).

- Binary: the 0379 release, main be0d1d37 (build/ags-release/ags.exe built in worktree dosags-ring at b1821bb3, the same
  tree), DOSAGS_RELEASE=1, sha256 2191042b343cfd66b9e01d09da100362af15b693fcf7019911a22eee9e87f728, 8,669,559 B,
  binary_sha12 d5c8fe52808a (see RMDIAG-2026-11-13's stamp correction, 5419f62d). Staged as build/abba/r0379/ags.exe
  and as build/ws/roundRP/r0379.exe (expected.txt).
- Flow: AGS Quest AutoPilot (`--test`), the rig line's cfg (tests/harness/games/5days/ACSETUP-ON.CFG as ACSETUP.CFG:
  sound on, 640x480) and SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_FIXED_TIMESTEP=1, live SB (detection on), OPL3.
- Command (REFAQB, registered): `AGS_EXE=build/abba/r0379/ags.exe tests/harness/lab-cell.sh <out> agsquest
  --fixed-timestep --sb-live --no-fine-timing --no-verify-present --conf tests/harness/confs/dosbox-x-fast-opl3.conf
  --include-extra <repo>/tests/harness/games/5days/ACSETUP-ON.CFG:ACSETUP.CFG --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1
  --timeout 1200`. RUN.BAT then sets what the rig's N7AQ line sets (DOSAGS_FIXED_TIMESTEP, the framebuffer hint), and no
  lab diagnostic (no DOSAGS_PRESENT_VERIFY, which the release reads; DOSAGS_TICKSTATS_FINE is not read by the release).
  Differences from the rig that remain: DOSBox-X's SB (BLASTER A220 I5 D1 H5 T6, emulated OPL3) vs the PicoGUS
  (A220 I7 D3 P330 T3), and DOSBox-X's timing.

## The registered renders (REFAQB1-5): the set for bar B1 is {180,181}

| render | binary_sha12 | exit | voicering compactions / moved / cap_max | pcm_irqs | mixed | underruns | overwrites | silent_irqs | drains | mode | AutoPilot ok | shutdown |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REFAQB1 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 180 | 180 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| REFAQB2 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 181 | 181 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| REFAQB3 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 180 | 180 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| REFAQB4 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 181 | 181 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| REFAQB5 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 180 | 180 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |

## Information (not the reference): the same binary, other env

- REFAQ1-5 (info-lab-env/): the same flow and cfg with the lab's default env (DOSAGS_PRESENT_VERIFY=1, TICKSTATS_FINE=1).
- AQV1-5 (info-default-cfg/): the package's own cfg (no ACSETUP.CFG; it also selects 640x480 and sound), lab env. These were
  the validity pre-check (compactions >= 1 on AGS Quest), before the rig line's cfg was matched.

REFAQ (lab env, rig cfg):

| render | binary_sha12 | exit | voicering compactions / moved / cap_max | pcm_irqs | mixed | underruns | overwrites | silent_irqs | drains | mode | AutoPilot ok | shutdown |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REFAQ1 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 181 | 181 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| REFAQ2 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 181 | 181 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| REFAQ3 | d5c8fe52808a | 0 | 2 / 55876 / 169344 | 180 | 180 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| REFAQ4 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 181 | 181 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| REFAQ5 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 180 | 180 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |

AQV (package cfg, lab env):

| render | binary_sha12 | exit | voicering compactions / moved / cap_max | pcm_irqs | mixed | underruns | overwrites | silent_irqs | drains | mode | AutoPilot ok | shutdown |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AQV1 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 180 | 180 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| AQV2 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 180 | 180 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| AQV3 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 181 | 181 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| AQV4 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 180 | 180 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |
| AQV5 | d5c8fe52808a | 0 | 2 / 55532 / 169344 | 181 | 181 | 0 | 0 | 0 | 0 | 640 x 480 | 18 | 1 |

## Reading

- The bound is exercised on this flow: compactions = 2 in all 15 renders, cap_max 169,344 (<= 196,608, the bound's ceiling
  of 192 KB). So AGS Quest is a VALID fixture for the check (sdlports' validity condition), and the rig cell must show its
  own compactions >= 1 (bar V2 in tests/harness/aq-audio-bars.py).
- pcm_irqs varies by one chunk between renders of the same binary: 180 or 181 over all 15. mixed equals pcm_irqs in every
  render (no silent chunk is written), so the extra chunk carries content. In AQV1 (180) vs AQV3 (181) the MIDI event count
  also differs (40 vs 42) and clk differs (2970 vs 3004 ms per 3 s): the run's timing differs between renders.
  Hypothesis, untested: the PCM clips' start phase against the 512-sample chunk grid decides whether a clip spans
  ceil(n/512) or ceil(n/512) + 1 chunks.
- The jitter is OLDER than 0377. SB4S on the 486 (2026-09-23, ags-0206 binary aa78f0416c81) read 181 against REF84-AQ's 180,
  recorded then as "cause not known". So accepting the set seen in the registered renders, rather than one value, is not a
  loosening for 0377's sake (sdlports' condition 2, 2026-11-13).
- Owed lab information (not a blocker; sdlports' condition 3): why one render writes an extra chunk.

## Addendum (2026-11-13, after round RP): the cause of the one-chunk jitter -- answered in the lab (move, lab-rb df52b851)

move-lab/rj/aq/AQ-PCMIRQS.txt (a lab overlay counting chunks per voice, no slot; six renders with the REFAQB command):
- AGS Quest's flow has ONE PCM voice: a streamed clip acquired at tick 3149 (AutoPilot phase=audio begin) and STOPPED at
  the phase's end (tick 3569) with 29-33 KB still unplayed; every mixed chunk is its data (nodata=0, so mixed = pcm_irqs).
- So pcm_irqs = the 512-sample chunks the SB consumed at its own real-time rate (46.4 ms each) between the voice's start
  and a stop fixed in GAME time: the run's timing moves that span across a chunk boundary. Six lab renders read 180 / 179 /
  180 / 180 / 180 / 181 (179 on the overlay build, a little extra main-thread work).
- The hypothesis above (a clip's start phase against the chunk grid) is REFUTED: the voice starts at chunk 0 in every
  render and ends by Stop, not by running out.
- Consequence for bar B1: the registered set {180,181} is not a bound. A rig value of 179 or 182 would be the same timing
  mechanism, not a defect. Round RP's verdict is unaffected (both cells read 180). For any later round on this flow, a bar
  on the mechanism is the robust form (pcm_irqs == mixed; underruns / overwrites / silent_irqs 0; pcm_irqs within a
  registered tolerance of the reference), or a count taken from the voice's own data rather than the device clock.
