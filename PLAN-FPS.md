# PLAN-FPS -- frames displayed on the Gateway 2000, then other cards and CPUs (2026-11-05)

Operator, 2026-11-05: "let's see how far we can push the FPS, trying to get +99% of frames displayed.
When we hit a wall where it seems infeasible, we will begin testing the S3 Virge and Cirrus Card with
the 486, then move to the cpu hardware matrix." Asked which target, the operator answered: all of them --
(a) real games in play, (b) room loads (whole-run), (c) Maniac Mansion Deluxe, (d) AGS Quest.

This file is the campaign's plan of record and measured-constants table. PLAN-NEXT.md keeps the release
work (R1-R4, v0.1); STATUS.md keeps the figures.

## KPI (per target; real hardware only; release flavour; named build_sha12; x2 to claim)

- **Frames displayed >= 99.0%**, both ways gatebar.py gives it: `1 - frames_skipped/ticks` AND
  `presents_real/render_passes` (the PLAN-GATES bar uses 95%; this campaign's line is 99%).
- At the game's own rate: `tick_rate_steady` 39.2-40.8 (40 ticks/s games), `fps_p50` >= 40.
- Camera (or a locked capture) witness clean; audio counters clean (sound ON, as the gates).
- Whole-run is reported beside steady; target (b) is the whole-run figure itself (39.2 -> 40).
- **Falsifiable:** a target FAILS on a cell under 99.0% on either completeness reading, or steady out of
  band. Every lever is pre-registered with a predicted band before its first run, and stops when it
  misses that band (LAB-MMD's rule).

## Measured constants (486DX2-66, Mach64, PicoGUS; append, never rewrite)

| what | figure | build | source |
|---|---|---|---|
| S8 Trilby room 35, frames displayed | 99.48 / 99.44% (26 / 28 skipped of 5,002) | release a1dba5d61624 | R1R1 / R1R2 |
| S16 5 Days room 3 | 99.54% (23 of 4,999) | release | GR16 (R2, unwitnessed); GR16R3 pending |
| S32P 5 Days room 3, 32-bit 640x480 | 99.52% (24 of 4,999) | release | GR32P (R2) |
| room-load stall on those scenes | stall_ms 1,136-1,569; whole-run 39.23-39.29 vs steady 40.11-40.27 | release | R1, R2 |
| room-35 load bracket (load_begin -> load_end) | 405-425 ms; load_begin 419-438 ms after start | release + instr | R1 |
| MMD character select (room 50, idle) | steady 36.5 ticks/s (does not hold 40), **fps_p50 8.9-9.8, displayed 25%** (750 skipped of 999; 250 renders) | instr a30ee9702c2a (09-26) | MABSP1/2 |
| MMD logic | 24.6 ms/tick (budget 25.0); without the entry tick 23.8-24.2 | instr a30ee9702c2a | LAB-MMD 49.10 (archive/lab-mmd) |
| MMD in play (room 1, information only) | plain logic 24.0-24.1 ms/tick; a click costs ~124 ms (one tick) | instr b1cd5ccee175 | LAB-MMD 50.5 |
| AGS Quest AutoPilot (16-bit 640x360) | 38.0 stable, 40.61 with its GUI hidden | old build (09-20) | STATUS.md |
| MMD character select, release (F1a) | steady 35.76, fps_p50 9.94, **displayed 27.77%** | release a1dba5d61624 | F1MMDK |
| MMD character select, profile (F1a) | ugo 28.16 ms/tick: script_vm **20.47**, other logic ~5; render **6.71 ms/pass** + scene 2.84; samples script 71.8% (Run:head 31.5% of it), non-script 17.9%, render 9.2% (_linear_draw_sprite16 51%) | probe 770a7ba9e60f, sound off | F1MMDP |
| 7 Days room 2 in play, release (F1a) | steady 39.99, fps_p50 40.00, **displayed 99.48%** -- MET | release | F17DK |
| 7 Days room 2, profile (F1a) | busy 11.50 ms/tick (logic 6.08, scene 3.36, render 2.06; script_vm 1.27), idle wait 13.44 | probe | F17DP |
| MMD character select, VM fast (F1b, lab c044ae62df3f) | steady 39.99, fps_p50 34.97, **displayed 86.94%** x2 (legacy 26.7%); script_vm 12.70 ms/tick (fine on) | lab release, DOSAGS_VM=fast | VMB1/VMB2, VMPROF |
| AGS Quest AutoPilot, release (F1a) | steady 41.09, fps_p50 39.49, displayed 93.04%, stall_ms 89,926 (whole-run 19.79) | release | F1AQK |
| MMD character select, VM slice 3 fast (round E, lab 1781fe2bf36c) | steady 39.99, fps_p50 36.89, **displayed 91.52 / 91.56%** (legacy 27.97% x2); band 95-100% missed low | lab release, DOSAGS_VM=fast | VM3B1/VM3B2 |
| 5 Days S16 room 3, VM slice 3 fast | 39.30 / 40.08, fps_p50 40.00, **displayed 99.38%**, audio clean -- MET (no regression) | lab release | VM3S16 |
| MMD CS, slice 3 fast, fuse masks (round C4) | 0x3F 90.16%, 0x03 88.72%, 0x00 87.52% displayed; script_vm 0x3F 12.689 / 0x03 12.859 ms/tick (fine on, sound on) | lab 1781fe2bf36c / 4bbb3f1224a5 | R4*/P4* |
| **MMD CS, VM fast + engine levers (round L5, lab 23fd25201ec9)** | steady 40.00, fps_p50 40.00, **displayed 99.90% x2** (presents 100.24%); levers off 91.28 / 91.24% | lab release | L5B1/L5B2 |
| 5 Days S16, VM fast + levers | 39.29 / 40.17, 99.52%, audio clean -- MET | lab release | L5S16 |
| **MMD CS, shipped build (round N7, main c284ddfd)** | steady 40.00, fps_p50 40.00, **displayed 99.90% x2**; whole-run 39.08 (boot load 966 ms) | release c754df64babd | N7M1/N7M2 |
| gate scenes, shipped build | S16 99.44% (39.24 / 40.13), S32P 99.52% (39.26 / 40.10), S8 99.32% (39.23 / 40.23); all MET, audio clean | release c754df64babd | N7S16/N7S32/N7S8 |
| AGS Quest AutoPilot, shipped build | steady 41.09, fps_p50 39.96, displayed 93.04% (249 skipped, = F1AQK), stall_ms 91,966 | release c754df64babd | N7AQ |
| v0.1 zip as shipped (DIST2, README.TXT settings) | 39.22 / 40.17, 99.42%, music + 7 effects, audio clean -- PASS | zip c0c6fe00 = c754df64babd | DIST2 |
| gate second readings, shipped exe (V1) | S16 99.40% 39.21 / 40.13 MET; S32P 99.64% **39.18** / 40.12, S8 99.44% **39.13** / 40.25 NOT MET (whole-run); preloop 926-1,004 ms vs N7 722-864 | release c754df64babd | V1S16/V1S32/V1S8 |
| Iowna, Shards in play | **not measured**: packages lack audio.vox (script null pointer) | -- | F1 prep |

So the walls today: MMD is logic-bound -- its logic takes 24.6 ms/tick, it steps at 36.5 ticks/s (it does not
hold 40), and only one frame in four is displayed; a render costs at most ~15 ms (upper bound, derived from totals:
(loop_ms 28,285 - 24.6 x 999) / 250 renders; the remainder also holds any other non-logic per-tick work). F1's
profile cell measures render per pass directly. 99% displayed at 40 needs logic + one render <= 25 ms. (An earlier
line here said render was the wall: wrong, corrected 2026-11-05.)
AGS Quest is GUI-bound; the gate scenes lose their last ~0.5% to one room-load stall.

## Work order

1. **Close the release work first** (PLAN-NEXT): R3 (GR16R3), R4 (DIST1, GUS, OPL2). v0.1 timing is the
   operator's call.
2. **F1 -- catalogue baseline on the release exe (one round, <= 6 cells, pre-registered):** one in-play
   cell per game not yet measured (7 Days, Iowna, Shards) plus MMD and AGS Quest on the release build,
   each with the KPI's figures and a witness. Output: the per-game table above, filled.
3. **F2 -- per-target lab slices (DOSBox-X first, the 486 decides):** for each target under 99%, profile
   the per-tick cost split (logic / render / present) with the existing instruments (ags 0316 per-tick
   coarse log, fine timing), name the dominant cost, pre-register a lever with a predicted band, then an
   ABBA on the 486.
   - (b) room loads: what the ~1.1-1.6 s stall is made of (load bracket, first-decode, sprite cache).
   - (c) MMD: logic first (24.6 ms/tick; LAB-MMD's remaining exact levers I, L, H', J/D/E total ~1.75 ms
     central -- far short of the ~12 ms needed, so a wall is likely on this CPU), then the ~15 ms render; then
     click handling (~124 ms).
   - (d) AGS Quest: GUI redraw cost.
   - **Lever V (script VM, 2026-11-05 design study, docs/lab/VM-DESIGN.md):** pre-decoded parallel stream +
     computed-goto dispatch + 8 MMD-derived superinstructions, same-binary switch DOSAGS_VM=legacy|fast. Predicted on
     the 486: script event ~20 -> 9.5-12.5 ms/tick (central ~10.5), MMD logic 24.6 -> ~14-17 ms/tick, displayed
     25% -> ~53-72%. Not enough alone for 99% (needs logic <= ~10 ms + a cheap render). Slices 0-5 as in the study;
     slice 0 (compiler output of a 6-handler sketch, hard stop if ip/this spill) first. Benefits every game.
     Slice 0 PASSED 2026-11-05 (docs/lab/VM-SLICE0.md): ip in %ebx, this in a register, 2-instruction dispatch per
     handler under DJGPP GCC 12.2 with the project flags; model now ~18-20 x86 instr/op (~2.8-3.1x); bands unchanged.
     Open: engine-call superop +54% (two constant divisions), full hot loop ~5-6 KB vs the 4 KB target.
     Slice 1 PASSED 2026-11-05 (docs/lab/VM-SLICE1.md; lab worktree ~/git/dosags-lab-vm): decoded stream = bytecode,
     0 mismatches / 0 ineligible on MMD, AGS Quest and 5 Days (98,997 instructions); decoder off = behaviour identical,
     Run() byte-identical. Open: decode ~2.0 us/word at fixed 40k (2-3x the design), AQ memory_min_free -1,536 KB
     with decode on (fragmentation or leak, unproven), exe-bytes ratchet +7,722 B (exact limit by design).
     Slice 2 PASSED 2026-11-06 (docs/lab/VM-SLICE2.md): fast loop = legacy instruction for instruction on MMD CS,
     AQ (incl. restore), seeded 5 Days and the MMD intro (26.7M instructions traced); screen and journey gates equal;
     MMD CS script event 9.311 -> 5.130 ms/tick at fixed 40k (1.82x, inside the pre-registered 4.6-6.4 band).
     AQ memory: not a leak (16 allocs / 16 frees, 0 B live at quit). Next: 486 same-binary ABBA (legacy vs fast),
     then slice 3 (superinstructions).
     **486 ABBA (round F1b, 2026-11-06) GAIN:** MMD character select, same lab release binary: legacy 26.77 / 26.71%
     displayed (steady 36.5), fast **86.94 / 86.94%** (steady 39.99), +60.2 points. VMPROF: script_vm 20.47 -> 12.70
     ms/tick (1.61x on the 486). Left for 99%: ~1.5-2 ms/tick (logic 17.4 + frame 9.0 vs 25). Next: slice 3.
     Slice 3 PASSED in the lab 2026-11-06 (docs/lab/VM-SLICE3.md): six superinstructions, shadow check 0 mismatches over
     ~4.66M executions, digests EQUAL on four fixtures, aq-journeys 10/10; MMD CS script event 9.256 -> 4.308 ms/tick at
     fixed 40k (2.15x; -16% vs slice 2); hot loop 6.7 KB. Round E (486 ABBA + 5 Days S16 fast) predicts 95-100% displayed.
     **Round E (2026-11-06) GAIN, band missed low:** MMD 91.52 / 91.56% displayed (slice 2 86.94%), legacy 27.97% x2;
     5 Days S16 fast 99.38% MET. First lever to miss its band (wall rule: one of two). Suspect: 6.7 KB hot loop vs 8 KB cache.
     **Round C4 (2026-11-06): the cache suspect is FALSIFIED** (release R4B-R4F -1.44 points; profile P4B-P4F +0.170 ms/tick):
     the superops stay; the 486 realizes less per fixed-cycle ms. Next MMD levers are engine-side (docs/lab/MMD-REMAINDER.md).
     Engine levers 1+2+3 PASSED in the lab 2026-11-06 (docs/lab/LEVERS-REPORT.md): lever 1 skips provably no-op off-room
     character updates (0 shadow mismatches over ~751k checks), lever 2 memoises 3 of 4 in-VM GetCharIDAtRoom calls a tick
     (10-call audited whitelist, 0 mismatches), lever 3 inlines cc_has_error. Round L5 predicts MMD 96-100% (central 99%).
     **Round L5 (2026-11-06) MET on the lab binary: MMD 99.90% displayed x2 at 40.00 ticks/s** (levers off 91.28 / 91.24%);
     5 Days S16 99.52% MET. **Landed 2026-11-06 as patches/ags 0359-0365, default on** (docs/lab/VM-LANDING.md; release
     c754df64babd, instrumented f3a8774e03c8; fallback DOSAGS_VM=legacy DOSAGS_ENGLEV=0). **Round N7 (2026-11-06): MET on the shipped build -- MMD 99.90% x2; S16/S32P/S8 MET; AGS Quest unchanged at 93.04%.** Queued for the next
     binary-changing patch: move 0363's dos_englev_shadow() definition under #ifdef DOSAGS_VMTRACE (dead code today).
   - **Lever R (render on mostly static screens):** after F1 measures render per pass directly.
4. **The wall rule:** a target is called a wall (operator decides) when its profiled dominant cost has no
   remaining pre-registered lever whose central estimate closes the gap, or when two levers in a row miss
   their bands. The record says which.
5. **Then other hardware (operator's physical swaps):** the S3 ViRGE and the Cirrus card in the 486
   (check the hub's HARDWARE.md known-issues table for each chip first; re-run the gate scenes + F1's
   table per card), then the CPU hardware matrix.

## Rig

Every round: pre-registration commit before data, its own power-on ask to the operator, power OFF between
rounds, vcctrl's USB watch. The capture stick (usb3-port2) is still flaky (R1 dropout; rising corrupt
frames in R3): cells scored from captured audio VOID on a drop; 512x384 cells need the camera.
