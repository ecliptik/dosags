# Round F1b -- 2026-11-06: the VM fast loop on the 486 -- GAIN: MMD 26.7% -> 86.9% displayed, steady 36.5 -> 40.0

One power-on 01:27:09Z-02:35:53Z (driver; powerguard confirmed), cap 02:47:09Z. Operator's standing order. Pre-registrations
f775be21 (committed as 1b23e1b4, re-hashed with identical content by the F1a image amend; ORDER-CONFIRMED names 1b23e1b4).
Lab binaries from ~/git/dosags-lab-vm vm-slice2b.diff (VM slice 1 + 2 + handler table): VMREL.EXE release c044ae62df3f,
VMINS.EXE instrumented b58ad934471b, build_dirty=1 by design (gatebar VOIDs on dirty, so the figures below are read from
each manifest directly, as the pre-registration states). Every cell exit 0, stamp matched, BLASTER "A220 I7 D3 P330 T3".

## VM ABBA, MMD character select (room 50, idle), release, same binary

| Cell | DOSAGS_VM | whole / steady | fps_p50 | displayed (1 - fs/ticks) | audio | env_block_sha |
|---|---|---|---|---|---|---|
| VMA1 | legacy | 35.69 / 36.53 | 9.87 | 26.77% | clean | 33f0861465fe |
| VMB1 | fast | 38.99 / 39.99 | 34.97 | **86.94%** | clean | b2a6255591e3 |
| VMB2 | fast | 38.99 / 39.99 | 34.97 | **86.94%** | clean | b2a6255591e3 |
| VMA2 | legacy | 35.71 / 36.54 | 9.87 | 26.71% | clean | 33f0861465fe |

- **GAIN as registered:** min(B) - max(A) = 86.94 - 26.77 = **+60.2 points** (bar >= 35); both B steady 39.99 (bar >= 39.2).
  FALSIFIER not met: min(B) 86.94% >> 50%, B - A >> 10. Predictions: A 20-35% (met); B 70-100%, central ~93% (met).
- VMB1/VMB2 are separate runs (started_utc 18:52:58 vs 19:04:18 local, loop_ms 125,940 vs 125,942, preloop 1,458 vs
  1,473) with the same skip count (653): the fixed-timestep idle screen is deterministic at this rate.
- The legacy arm on the lab binary matches the release main (F1MMDK 27.77%, steady 35.76): the binary's own weight is not
  a factor.

## VMPROF (instrumented, fine timing on, sound off, fast) vs round F1a's probe on main (F1MMDP, legacy)

| ms per game tick | F1MMDP (legacy) | VMPROF (fast) |
|---|---|---|
| update_game_once | 28.16 | 24.88 |
| process_events_dispatch | 21.88 | 14.00 |
| **script_vm** | **20.47** | **12.70** (1.61x on the 486; 1.82x at fixed 40k) |
| logic excl. render/scene/wait | 25.5 | 17.44 |
| render_to_screen per pass | 6.71 | 6.39 |
| scene_construct per pass | 2.84 | 2.65 |
| displayed | -- | 81.5% (927 of 4,999 skipped; fine timing costs ~0.7 ms/tick) |

Prediction script_vm 9.8-13.3 (met); falsifier > 14.5 (not met). **What is left for 99%:** logic ~17.4 + one frame ~9.0
= ~26.4 ms against 25: ~1.5-2 ms. Slice 3 (superinstructions on the remaining 12.7 ms of VM) needs ~15%; the timer
reads (~0.5 ms) and character update are further margin.

Rig: the capture stick stayed on USB (vcctrl) but logged 3 corrupt frames (01:33:34Z warm-up, 01:55:06Z VMB1, 02:06:25Z VMB2),
none affecting a figure (all from the manifests; the card cannot lock these modes). WARMUPF1B's 9-character tag was
truncated by DOS to WARMUPF1.LOG, which appended to round F1a's warm-up manifest (two runs in one file; the warm-up is not
scored). Rule from here: tags <= 8 characters and never reused.
