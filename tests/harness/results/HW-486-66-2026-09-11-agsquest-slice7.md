# Benchmark

## Hardware
CPU: Intel 486DX2
Clock: ~66 MHz
L1: UNKNOWN (not reported by dinspect on this rig)
L2: UNKNOWN (not reported by dinspect on this rig)
RAM: 640 KB base + extended (see slice 6's own record for the exact figure; unchanged hardware)
Video: ATI Mach64, 2 MB VRAM
Sound: PicoGUS 2 in SB mode (Sound Blaster 2.0 emulation) -- confirmed via this run's own live boot banner ("picogus-sb-dbopl3" firmware); not exercised, dosags audio is stubbed pre-Sound-milestone
MIDI: not applicable yet (stubbed)
DOS: MS-DOS 6.22

Hardware ID: HW-486-66 (sdl-dos-ports HARDWARE.md matrix) -- same physical machine (gateway2000/g2k-lab) as slice 6's own HW-486-66-2026-09-11-agsquest.md run, confirmed via this run's own live boot banner (identical PicoGUS/Mach64 identity strings)

## Build
Commit: d1c70f9
Upstream revision: (see tests/harness/packages/agsquest/PIN)
binary_sha12: 138b85d583ae
env_block_sha: df7c1a82c0f4

## Scene
Game: AGS Quest (adventuregamestudio/ags-demo-game, local-testing-only, see LICENSE-NOTES.md)
Level/room: full phase sequence, boot..quit
Duration: 434s

## Results

| phase | status | tick | room |
|---|---|---|---|
| boot | ok | 0 | 1 |
| splash | ok | 81 | 2 |
| menu | ok | 380 | 3 |
| intro | ok | 380 | 3 |
| settle | ok | 501 | 3 |
| key | ok | 1194 | 3 |
| unlock | ok | 1558 | 3 |
| enter | ok | 1581 | 4 |
| interior | ok | 2015 | 4 |
| save | ok | 2019 | 4 |
| restore | ok | 2019 | 4 |
| exit | ok | 2046 | 3 |
| gem | ok | 2452 | 3 |
| audio | ok | 2636 | 3 |
| shots | ok | 2636 | 3 |
| quit | begin | 2636 | 3 |
| dialog (optional) | ok | 2019 | 4 |

### Screenshots (hash regression, environment: realhw)

| file | status | sha256 |
|---|---|---|
| PH01.BMP | match | `9f9d9bd9eee2794336d02b91e661612d2c707401a26b260e0588e2574b3cc185` |
| PH02.BMP | match | `6051787344120f894baa6c919564bc90d9d592d843536a3de7b2089e3ceb1a34` |
| PH03.BMP | match | `5b98f4da5aba5c3f992315a2192c0dea92dddbbeefe3706690698d08e02330db` |

Overall: PASS

## Slice 7 confirmation: the `dialog` phase on real hardware

This is the first real-hardware run of the `dialog` phase (`AUTOPILOT
dialog_detail chosen=14` in `AUTOPLT.LOG`, twice -- once per screenshot
poll, both confirming "Leave" was selected correctly). The
coordinate-based `Mouse.SetPosition`+`Mouse.Click` mechanism
(`Dialog.DisplayOptions()`, see PLAN.md's eleventh-session "Current
state" for why not `Dialog.Start()`) works identically on real hardware
to DOSBox-X -- same option selected, same clean completion into `save`.

**First real-hardware input-latency datum for this port**
(`patches/ags/0045`): `t_ms=287785` (inject) -> `t_ms=288008`
(processed) = **223ms**. Compare against DOSBox-X's own reading under
`--fast` (11-24ms across several runs) -- real 486DX2-66 hardware is
roughly an order of magnitude slower to process a simulated click than
DOSBox-X's uncapped emulation, which is exactly the kind of gap this
approximation exists to surface. Not validated against a real physical
click's own latency (no such comparison is possible from script or
DOSBox-X), so treat as the engine's own dispatch overhead under real
timing, not a full input-to-response measurement.

Also confirms `run-rig.sh` end to end for the first time (previous
slice-6 runs used its steps by hand, since the script didn't exist yet
at the time; this is its first genuinely automated real invocation).
Getting to a clean run surfaced a real, multi-part infrastructure
investigation on the shared vcctrl rig this same evening -- stale FTP
credentials on the card, a boot-menu keystroke-retry bug, a hard hang
requiring a real power cycle, and a `run-rig.sh` cleanup-trap bug that
deleted this very results directory before it could be read the first
time a full run succeeded -- all found and fixed live, none of it a
dosags/AGS defect. Full account: PLAN.md's eleventh-session "Current
state" section.

## Measurement method
Real hardware (vcctrl), environment=realhw -- this fps/timing datum IS a real performance number, unlike a dosbox-x/86box run. Pair any fps claim with an independently-derived wall-clock bracket per .sdl-dos-ports/shared/skills/dos-hardware-validation.

**fps context**: `fps_p50=9.62`/`fps_p95=10.09` -- identical to slice 6's own HW1 reading on this same machine (expected: AGS Quest's own stress workload, sampled the same way, same hardware). Not the in-profile KPI floor (decision 4, PLAN.md). `memory_min_free_kb=144704`, consistent with HW1's own 143936 reading, both far from the 16MB real-hardware target.

