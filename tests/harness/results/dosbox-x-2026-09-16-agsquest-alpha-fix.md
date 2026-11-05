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
Commit: 5b4e9ac
Upstream revision: (see tests/harness/packages/agsquest/PIN)
binary_sha12: c9ee2b121d04
env_block_sha: 46c9aaec20ba

## Scene
Game: AGS Quest (adventuregamestudio/ags-demo-game, local-testing-only, see LICENSE-NOTES.md)
Level/room: full phase sequence, boot..quit
Duration: 124s

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

### Screenshots (hash regression, environment: dosbox-x)

| file | status | sha256 |
|---|---|---|
| PH01.BMP | mismatch | `7ac5213ff8b4b8b3b99bf46b2aa89da605979f51869753b97a651cac4fd14350` |
| PH02.BMP | mismatch | `3b2651677ea1cef96265ba33d6ef361d61f54211c4a70a4b4e9266acaaf63dce` |
| PH03.BMP | mismatch | `623fc3a701e2afcddac99804434537e9c47b84e19a9a83455b359c0bf529d2ce` |

Overall: FAIL

## Measurement method
dosbox-x automation gate (correctness only) -- not real hardware, not a performance datum. See PLAN.md's "Test harness (AGS Quest)" Milestone mapping for what each rung needs beyond this.


## Why this run re-baselined `expected/agsquest/dosbox-x.json`

This is the first DOSBox-X run of the AGS Quest package after
`build-package.sh` gained the sprite-source alpha flatten
(`flatten-alpha.py`, see that file's header and PLAN.md "Black-box
sprite glitch -- root cause, fix plan, test plan"). The three
screenshot hashes changed exactly as expected, and the images were
inspected before `--update-baseline`: no black boxes around the player,
NPC, chest, frog, doors, chandelier, or balcony objects; zero magenta
pixels; no new fringing (every source PNG has no semi-alpha pixels).
The pixel diff against the previous baseline's frames covers only the
former box areas (3445 / 6124 / 2689 pixels for PH01/02/03).

Reference-engine byte-identity check (the proof this changed data, not
engine behaviour): AGS's official Linux 3.6.3.13 engine
(`ags64 --gfxdriver software --test`, same rebuilt package, same
autopilot) produced PH01/PH02/PH03 with sha256 values IDENTICAL to this
DOS run's -- `7ac5213f...`, `3b265167...`, `623fc3a7...` -- as it had
for the defective package before the fix.

Two runs of the rebuilt package (this one with `--timeout 300`, an
earlier one cut short at 120 s in the `audio` phase) gave byte-identical
PH01-03, so the new baseline is deterministic the same way the original
one was confirmed to be.

Still stale, by design: `expected/agsquest/realhw.json` keeps the old
three hashes until a real-hardware run re-establishes them (the harness
never writes a real-hardware baseline from a DOSBox-X run). The
2026-09-11 real-hardware records cite the old hashes and remain correct
descriptions of what those runs rendered. The AGS Quest fps numbers'
meaning is unaffected (same sprites, same sizes).
