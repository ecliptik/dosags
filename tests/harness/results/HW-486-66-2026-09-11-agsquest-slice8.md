# Benchmark

## Hardware
CPU: Intel 486DX2
Clock: ~66 MHz
L1: UNKNOWN (not reported by dinspect on this rig)
L2: UNKNOWN (not reported by dinspect on this rig)
RAM: 640 KB base + extended (unchanged hardware, see slice 6's own record)
Video: ATI Mach64, 2 MB VRAM
Sound: PicoGUS 2 in SB mode (not exercised, dosags audio is stubbed pre-Sound-milestone)
MIDI: not applicable yet (stubbed)
DOS: MS-DOS 6.22

Hardware ID: HW-486-66 (sdl-dos-ports HARDWARE.md matrix) -- same physical
machine (gateway2000/g2k-lab) as slice 6's HW1 and slice 7's HW8 runs, per
vcctrl profile/rig continuity. This run did not independently re-inspect
a live boot-banner screenshot to re-confirm the PicoGUS/Mach64 identity
strings the way slice 7 did -- the fps (10.00/10.09 vs slice 7's
9.62/10.09) and memory (143936 vs slice 7's 144704 kb) readings are
consistent with the same hardware, but that consistency is corroborating
evidence, not an independent re-confirmation.

## Build
Commit: 6bfd3fc
Upstream revision: (see tests/harness/packages/agsquest/PIN)
binary_sha12: 138b85d583ae
env_block_sha: df7c1a82c0f4

## Scene
Game: AGS Quest (adventuregamestudio/ags-demo-game, local-testing-only, see LICENSE-NOTES.md)
Level/room: full phase sequence, boot..quit
Duration: 486s

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
| anim | ok | 2020 | 4 |
| save | ok | 2024 | 4 |
| restore | ok | 2024 | 4 |
| exit | ok | 2051 | 3 |
| gem | ok | 2457 | 3 |
| guimenu | ok | 3144 | 3 |
| audio | ok | 3144 | 3 |
| shots | ok | 3144 | 3 |
| quit | begin | 3144 | 3 |
| dialog (optional) | ok | 2024 | 4 |

### Screenshots (hash regression, environment: realhw)

| file | status | sha256 |
|---|---|---|
| PH01.BMP | match | `9f9d9bd9eee2794336d02b91e661612d2c707401a26b260e0588e2574b3cc185` |
| PH02.BMP | match | `6051787344120f894baa6c919564bc90d9d592d843536a3de7b2089e3ceb1a34` |
| PH03.BMP | match | `5b98f4da5aba5c3f992315a2192c0dea92dddbbeefe3706690698d08e02330db` |

Overall: PASS

## Slice 8 confirmation: `guimenu` and `anim` on real hardware

**Both new phases pass, first attempt, tag HW10** -- clean single run, no
retry needed, after the vcctrl-side fix described below.

**`anim` real values**: `frame0=0 frame1=1 animating=1`, tick 2015->2020
(5 ticks) -- byte-for-byte identical to the DOSBox-X confirmation earlier
this session (also `frame0=0 frame1=1`, also 5 ticks). **`guimenu` real
values**: tick 2641->3144 (503 ticks) -- also identical to the DOSBox-X
run's own 503-tick resolution time for `Button.Click()`'s deferred
handler. Tick-counted durations for both new phases match DOSBox-X
exactly, unlike this port's own wall-clock (`uclock()`-based) metrics --
e.g. this same run's `input_latency` datum (`t_ms=288099` inject ->
`t_ms=288323` processed = 224ms) is close to slice 7's own 223ms HW8
reading but nothing like DOSBox-X's 11-24ms. Consistent with `Game.
TickCounter` being a logical per-loop counter tied to `GetGameSpeed()`,
not wall-clock time (already established, e.g. PLAN.md's ninth-session
"frozen during a blocking Display()" finding) -- the NUMBER of ticks a
deferred script action takes to resolve is apparently CPU-speed-
independent even though the real wall-clock duration of each tick is not.
Worth knowing for any future real-hardware-vs-DOSBox-X comparison: expect
tick-counted phase durations to match, expect ms-based instrumentation to
diverge by roughly an order of magnitude.

All 16 pre-existing required phases plus optional `dialog` are
unaffected -- identical tick/room values to slice 7's own HW8 run above
(same physical machine, same package, same walkthrough up to the point
`anim`/`guimenu` were inserted). `fps_p50=10.00`/`fps_p95=10.09` and
`memory_min_free_kb=143936`, both consistent with HW1's/HW8's own
readings on this machine.

**Rig-side context this run needed to succeed**: this is the first clean
single-attempt run since a real vcctrl-daemon bug (found during this same
session's first two attempts, both tagged HW9, both failing at ~221s with
a misleading "no-net" reason) was root-caused and fixed by the vcctrl
peer session -- `_enter_net()`'s boot-menu retry early-stop was watching
the wrong signal (full net-boot completion, not "the menu accepted the
digit"), so it fell through to blindly sending all 7 retry keystrokes
regardless of whether the boot menu had already resolved, corrupting the
next real command. Fixed by capping the retry loop at 3 attempts
(matching the cap `vcctrl_common.spam_menu()` already had elsewhere but
`_enter_net()` never inherited). Not a dosags/AGS defect; full account in
vcctrl's own `docs/lab/FINDINGS.md` sec. 58 and `docs/lab/OPEN-FAULTS.md`
sec. 20 (commit `a867254`). Also confirms `run-rig.sh` itself needed no
changes this time -- the same script that needed three real fixes during
slice 7 ran clean end to end on the first real attempt after the daemon
fix landed.

## Measurement method
Real hardware (vcctrl), environment=realhw -- this fps/timing datum IS a real performance number, unlike a dosbox-x/86box run. Pair any fps claim with an independently-derived wall-clock bracket per .sdl-dos-ports/shared/skills/dos-hardware-validation.
