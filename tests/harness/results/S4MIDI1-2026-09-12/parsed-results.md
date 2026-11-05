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

Hardware ID: (fill in the vcctrl machine/tag this ran against)

## Build
Commit: c05df3a
Upstream revision: (see tests/harness/packages/agsquest/PIN)
binary_sha12: 484f010f483e
env_block_sha: df7c1a82c0f4

## Scene
Game: AGS Quest (adventuregamestudio/ags-demo-game, local-testing-only, see LICENSE-NOTES.md)
Level/room: full phase sequence, boot..quit
Duration: 609s

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
| audio | ok | 3564 | 3 |
| shots | ok | 3564 | 3 |
| quit | begin | 3564 | 3 |
| dialog (optional) | ok | 2024 | 4 |

### Screenshots (hash regression, environment: realhw)

| file | status | sha256 |
|---|---|---|
| PH01.BMP | match | `9f9d9bd9eee2794336d02b91e661612d2c707401a26b260e0588e2574b3cc185` |
| PH02.BMP | match | `6051787344120f894baa6c919564bc90d9d592d843536a3de7b2089e3ceb1a34` |
| PH03.BMP | match | `5b98f4da5aba5c3f992315a2192c0dea92dddbbeefe3706690698d08e02330db` |

Overall: PASS

## Measurement method
Real hardware (vcctrl), environment=realhw -- this fps/timing datum IS a real performance number, unlike a dosbox-x/86box run. Pair any fps claim with an independently-derived wall-clock bracket per .sdl-dos-ports/shared/skills/dos-hardware-validation.

