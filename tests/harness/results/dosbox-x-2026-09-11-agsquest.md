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

Hardware ID: DOSBox-X (correctness gate, not a performance number)

## Build
Commit: 466ba21
Upstream revision: (see tests/harness/packages/agsquest/PIN)
binary_sha12: 813f9591575c
env_block_sha: 46c9aaec20ba

## Scene
Game: AGS Quest (adventuregamestudio/ags-demo-game, local-testing-only, see LICENSE-NOTES.md)
Level/room: full phase sequence, boot..quit
Duration: 84s

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
| save | ok | 2015 | 4 |
| restore | ok | 2015 | 4 |
| exit | ok | 2042 | 3 |
| gem | ok | 2448 | 3 |
| audio | ok | 2632 | 3 |
| shots | ok | 2632 | 3 |
| quit | begin | 2632 | 3 |

### Screenshots (hash regression, environment: dosbox-x)

| file | status | sha256 |
|---|---|---|
| PH01.BMP | match | `9f9d9bd9eee2794336d02b91e661612d2c707401a26b260e0588e2574b3cc185` |
| PH02.BMP | match | `6051787344120f894baa6c919564bc90d9d592d843536a3de7b2089e3ceb1a34` |
| PH03.BMP | match | `5b98f4da5aba5c3f992315a2192c0dea92dddbbeefe3706690698d08e02330db` |

Overall: PASS

## Measurement method
DOSBox-X automation gate (correctness only) -- not real hardware, not a performance datum. See PLAN.md's "Test harness (AGS Quest)" Milestone mapping for what each rung needs beyond this.

