# Benchmark

## Hardware
CPU:
Clock:
L1:
L2:
RAM:
Video:
Sound:
MIDI:
DOS:
VESA:

Hardware ID: dosbox-x (correctness gate, not a performance number)

## Build
Commit: ce38f88
Upstream revision: (see tests/harness/packages/agsquest/PIN)
binary_sha12: 667514e4b97d
env_block_sha: 7dc81bac1456

## Scene
Game: AGS Quest (adventuregamestudio/ags-demo-game, local-testing-only, see LICENSE-NOTES.md)
Level/room: full phase sequence, boot..quit
Duration: 103s
Clock bracket: RTC 103s vs engine 100.54s, residual 2.46s (fixed init+shutdown, should NOT scale with run length)

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
| gem | ok | 2462 | 3 |
| guimenu | ok | 3149 | 3 |
| audio | ok | 3569 | 3 |
| shots | ok | 3569 | 3 |
| quit | begin | 3569 | 3 |
| dialog (optional) | ok | 2024 | 4 |

### Screenshots (hash regression, environment: dosbox-x)

| file | status | sha256 |
|---|---|---|
| PH01.BMP | match | `7ac5213ff8b4b8b3b99bf46b2aa89da605979f51869753b97a651cac4fd14350` |
| PH02.BMP | match | `3b2651677ea1cef96265ba33d6ef361d61f54211c4a70a4b4e9266acaaf63dce` |
| PH03.BMP | match | `623fc3a701e2afcddac99804434537e9c47b84e19a9a83455b359c0bf529d2ce` |

Overall: PASS

## Measurement method
dosbox-x automation gate (correctness only) -- not real hardware, not a performance datum. See PLAN.md's "Test harness (AGS Quest)" Milestone mapping for what each rung needs beyond this.

