# dosags -- plan of record

**Dated 2026-09-21.** This file is the plan: gates, bars, rulings in force,
the current position per colour depth, and the work order. It is meant to
be read in one sitting. **The full chronological campaign log is
`PLAN-LOG.md`** (26k lines, 2026-09-10..21); any older document that cites
`PLAN.md "<section title>"` is pointing at a section that now lives there.
`STATUS.md` is the short machine-readable state; `README.md` the narrative.

## Goal and target

Over 40 fps at 40 Hz on **HW-486-66** (486DX2-66, 16 MB, ATI Mach64
215CT, UniVBE) for 8-bit and 16-bit AGS games, measured on real hardware
through vcctrl. 32-bit is a correctness path whose place in the 486
profile is undecided (work order step 5).

**Every figure in this file is Mach64-only, `DOSAGS_FIXED_TIMESTEP=1`,
sound OFF unless it says otherwise.** ViRGE and Cirrus are in scope after
the fps work (ruling 2 below); expect the mechanism to differ, not just
the numbers -- Cirrus lands on the banked path.

## Position by depth (2026-09-21)

| depth | best figure | fixture and rung | what is NOT covered |
|---|---|---|---|
| 8-bit 320x200 | **40.00 / steady 40.01 / whole-run 39.34, 2,481 presents (anim12); steady 39.99, whole-run 39.34/39.32, 982 presents (walk)** | BENCH8 anim12 + walk arm (synthetic) at Mode 13h 1:1, ags 0194 -- **Gate 2, RE-CLAIMED SCOPED 2026-09-21** (see Gates) | any real game; the default 640x480 2x rung scores 14.99 on the same fixture |
| 8-bit 320x240 | **40.00 / whole-run 39.54** | Trilby's Notes IDLE title, 640x480 2x -- Gate 1, CLAIMED | in-play, unmeasured on the current binary; no Mode 13h for 320x240 |
| 16-bit 640x360 | **38.0 stable** (40.61 with `gCredits` hidden) | AGS Quest demo, 1:1 letterboxed -- content-bound, closed on evidence | it is the demo's ceiling, not the port's. **2026-09-21 note:** measured with ags patch 0169 stage 1 ON, which shipped with a stale-pixel-on-hide defect and a skip precondition that read "unchanged" after the flags were cleared (step 1, slice C). The figure stands as measured, pending the slice C confirmation cell; the demo's own GUI hide/show events are what the confirmation cell reads |
| 16-bit 320x200 | **5 Days a Stranger IN PLAY: steady 39.97 / 39.95, whole-run 39.26 / 39.24, stable 39.47 / 39.46, `fps_p50` 40.00 x2** (S2F2 / S2F3, 2026-09-22) | 5 Days a Stranger, room 3 via `--startr 3`, drive-walk 2 s, 512x384 centred 1x, pillarbox alias ON, ags 0196 -- **Gate 3, CLAIMED 2026-09-22** (see Gates) | Maniac Mansion Deluxe (S2M1 6.84, event-dispatch bound); the 0197 binary's rate; whole-run margin only 0.04-0.06; n=2 |
| 32-bit | 0.05 (Shards, 2026-09-15); 2.88 (AGS Quest forced-32, 2026-09-16) | 640x480 2x / 1:1 | every present-path patch since (0100, 0103, 0120, multi-rect) |

`fps_p50` counts render passes, not displayed frames (one cell scored
40.00 while displaying under 8 frames a second). Quote a rate as
`tick_rate_steady x (1 - frames_skipped/ticks)`, with `presents_real` and
completeness beside it.

## Gates

- **Gate 1 -- CLAIMED 2026-09-18** (operator sign-off). Trilby's Notes
  (8-bit) idle: `fps_p50` 40.00, `tick_rate_steady` 40.04, whole-run
  `tick_rate` 39.54 vs 39.2, replicated 5/5. Idle = ~23 real presents per
  run; an engine-overhead result.
- **Gate 2 -- RE-CLAIMED, SCOPED, 2026-09-21 (operator decision, via the question tool).**
  Claimed for **8-bit 320x200 at Mode 13h on the two fixtures that closed the reopening: an
  in-place-animation cell (anim12) and a moving-position cell (walk arm), Mach64-only.**
  Evidence: anim12 x2 (F2B1, F2B2) on the fixed binary (ags 0194) -- `fps_p50` 40.00 x2,
  `tick_rate_steady` 40.01 x2, whole-run 39.34 x2, 2,481 real presents, physical-screen witness
  reviewed clean both cells; walk arm x2 (W1, W2), same binary -- `fps_p50` 40.00 x2, steady
  39.99 x2, whole-run 39.34/39.32, 982 real presents, witness reviewed clean both cells (camera
  only; the capture card is not a physical witness at Mode 13h -- it locks the mode then loses
  signal). Both arms passed the alias-row screen-equality gate (`gate-alias.sh`, 8 rows, screen
  == full-push reference pixel for pixel) with its `DOSAGS_BREAK_0193` control failing as
  required (the check has demonstrated power). The whole-run margin over the 39.2 floor is
  **0.12 - 0.14**, with the systematic **+215 - 224 ms** whole-run denominator residual still
  unexplained (a candidate, not a cause; see the residual finding below) -- the claim stands on
  the measured band, not on an explanation of the residual. The walk arm's present load is
  noted as lighter than anim12's (about 40% of the presents for the same tick count), so this
  scope is "a moving position at Mode 13h", not the harder anim12-only case alone.
  **This claim explicitly does NOT cover any real game** -- BENCH8/BENCH16 are synthetic
  fixtures; 8-bit 320x240 is Gate 1; 16-bit and 32-bit are unclaimed (Gate 3, Gate 4).
  *Prior state, unchanged below: Gate 2 -- OPEN, REOPENED 2026-09-21 by the operator (it had
  been CLAIMED earlier that day; the original text follows).* Reason: the narrowed-present
  under-push exists at the Mode 13h alias rung for moving content: BENCH8 walk stale from frame
  2 (247 px constant, 198/199 frames), anim12 clean except its final teleport frame; the
  40.00/39.41 figures stand as measured on an in-place-animation fixture. **Closing condition
  (operator's terms):** anim12 AND a walk-arm cell both in band (39.2 - 40.8 on both tick
  figures, completeness >= 95% where defined, `fps_p50` >= 40) at Mode 13h on the FIXED binary,
  clean build, with the physical-screen witness sheet reviewed clean and the verifier at
  `stale_frames=0` on DOSBox-X for both arms. -- **met, see the re-claim above.**
  *Was: **Gate 2 -- CLAIMED 2026-09-21** (operator decision: released as bounded*
  and mitigated). BENCH8 anim12 at Mode 13h, `--gate` 5000 ticks, patch
  0189 binary: whole-run 39.41/39.41/39.41/39.40, steady 40.01 x4,
  `fps_p50` 40.00 x4, completeness 99.92%, spread 0.01. The ~210 ms CF
  write stall that held it is closed, not named (section below).
- **Gate 3 -- RE-HOMED 2026-09-21** (operator decision). AGS Quest is
  closed on evidence at 38.0: its 460x260 masked GUI composited over
  moving content is the entire tail, removing it gives 40.61, clipping it
  cannot reach budget, and the "lower output resolution" concession is
  withdrawn as unpayable there (letterbox never pushed, no upscale to
  remove, downscale costs ~45 cycles/px). **New Gate 3: 5 Days a Stranger
  (16-bit 320x200) in play, at a centred 1x rung** (512x384x16 `0x01D4`
  under UniVBE or 640x480x16), both tick figures in band, completeness
  >= 95%, clean build. **BENCH16** (`tests/fixtures/bench`, merged) is the
  scriptable A/B instrument for the optimisation work; 5 Days is the
  witness the gate is judged on.
  **Gate 3 -- CLAIMED 2026-09-22 (operator decision via the question tool, claimed on the
  pre-agreed replication condition: "replicate once, then claim").** Claimed for **16-bit 320x200,
  5 Days a Stranger IN PLAY** (room 3 via `--startr 3`, `drive-walk.sh` at a 2 s cadence), at the
  **512x384 centred-1x rung with the pillarbox alias ON** (ags patch 0196,
  `binary_sha12=340fa8167624`, `build_dirty=0`), **Mach64-only**, sound off, fixed timestep, direct
  framebuffer. Evidence, S2F2 / S2F3: `tick_rate_steady` 39.97 / 39.95, whole-run `tick_rate` 39.26 /
  39.24, stable rate 39.47 / 39.46, `fps_p50` 40.00 x2, `presents_real / render_passes` ~100% x2
  (4950/4938, 4951/4939). Witness: camera only (the capture card cannot lock 512x384), reviewed
  clean in both cells apart from the room-3 two-figure beat, which DUPCHAR4 showed is a `--startr`
  debug-jump artifact (natural entry shows one figure). **Caveats that travel with the claim:** the
  whole-run margin over the 39.2 floor is only **0.04 - 0.06** (thinner than Gate 2's 0.12 - 0.14);
  **n=2**; measured on the **0196** binary, NOT 0197 (0197's Object flush is untested for rate on
  real hardware); does **NOT** cover Maniac Mansion Deluxe (S2M1 6.84, event-dispatch bound) or any
  32-bit title.
- **Gate 4 (provisional) -- 32-bit.** Not a bar yet: two zero-code cells
  first (step 5), then decide whether 32-bit is a 486 target at all.
- **PLAN-GATES S8 / S16 / S32 (S32P) -- MET AS REGISTERED, 2026-09-30** (PLAN-GATES.md bar and claim procedure; every cell
  pre-registered before data). Bar: "Bar per depth, sound ON, Mach64, fixed timestep, 512x384 centred 1x (S32: 640x480x32 1:1):
  both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera witness clean, x2; audio by the counters (pcm_irqs exact,
  overwrites 0, late_writes 0, silent_irqs 0 outside room loads); one 640x480 capture listen per depth. WB arm: LAB-WB 24 A/B/D."
  - **Bar cells x2, gatebar.py (72f394ca):** S8 GL8A/B 39.26/40.23, 39.35/40.29 (Trilby room 35, DOSAGS_MSGSKIP=1); S16 GL16A/B
    39.29/40.13, 39.29/40.10 (5 Days room 3, 512x384); S32P GL32A/B 39.28/40.12, 39.34/40.07 (forced 32, 640x480 1x). fps_p50 40.00,
    completeness >= 98.98% both ways, silent_irqs 0, overwrites / late_writes / underruns 0 in all six. All six ran on
    **8249193ed041 (main 553588d4)**, under ags 0347's counter (silent_irqs = dropouts only; start latency reported separately);
    silent_irqs figures before 0347 are not comparable.
  - **Capture listens, one per depth, harness-scored (lab-wb):** S8 CAPS8 PASS (capture-check.py, lab/wb 37bf008c) on
    **8249193ed041**; S16 CAPS16 PASS (capture-check3.py, lab/wb 4194baf5; M1 +1 cent, M2 0.809) on **64d449a5b895** (main 3aee50b4,
    WITH ags 0348); S32 CAPS32R PASS (capture-check3.py, lab/wb e042cbad; M1 +1 cent, M2 0.801) on **e3a83135dc9c** (main 8f439c0f,
    current main; CAPS32 before it was VOID as registered, no "Playing sound 3", re-run once under lab/wb 49aa373f).
  - **WB arm:** the per-depth WB bar passes at S8 (WBC8R D 0.843), S16 (WBC16R D 0.785) and S32P (WBC32R D 0.780), all on
    **ef123dba0adf** (main d533b56d), clean no-PCM fixtures.
  - **Camera witness CLEAN in every cell above** (reviewed before scoring).
  - **Caveats that travel with the claim:**
    - The bar cells and CAPS8 ran on a binary whose **OPL3 music was ~89 cents sharp** (the opl3_sink F-number table started at
      C#; the WB cells' WaveBlaster MIDI does not use it); hub 8e6a9c9 fixed it afterwards (main 3aee50b4). Pitch is not in the bar. The two capture cells on the fixed
      table (CAPS16, CAPS32R) read **+1 cent**; CAPS8's scorer has no pitch check.
    - **CAPS16's binary carried ags 0348's ~46 ms hole ~186 ms into every cold-started sound** (underruns 6 = primes 6); its K2
      (gaps >= 0.12 s) cannot see a 46 ms hole. 0348 is reverted on main (4fc91556); the ratchet now gates underruns eq 0.
    - **CAPS8** (Trilby room 35): the music's identity is not checkable there (the ambient masks it), nor PCM bit depth.
      **CAPS16 / CAPS32R** (5 Days room 3): the PCM check (K3) is spectral presence of sound 3 only; PCM waveform fidelity, gaps
      under ~0.12 s (the SB counters cover those) and OPL3 timbre are not checked.
    - The evidence spans four binaries: the bar on 8249193ed041, the captures on 8249193ed041 / 64d449a5b895 / e3a83135dc9c,
      WB on ef123dba0adf; placement moved at each landing. Current main is e3a83135dc9c.
    - n=2 per depth for the bar; the S8 whole-run margin over the 39.2 floor is 0.06 / 0.15, S16 0.09 x2, S32P 0.08 / 0.14.

## KPI definitions (unchanged, 2026-09-17/18 rulings)

- Whole-run `tick_rate` = `get_loop_counter() / runtime since
  start_game()`, judged on a **5000-tick** `--gate` window; band
  **39.2 - 40.8**.
- `tick_rate_steady`: same band. Both tick figures must pass.
- `fps_p50` >= 40 render passes/s AND completeness >= 95% of the distinct
  frames the content generates (`presents_real / content-dirty ticks`;
  for BENCH8/BENCH16 the content rate is 20/s by authorship).
- Whole-run run-to-run floor on the Gate 2 configuration: **0.01** with
  the SDL trace off; it was 0.24 with the trace on. Gate cells run on a
  clean build (`build_dirty=0`), never on a probed binary (hot-path probes
  move the result ~1 fps by cache footprint).

## Standing authorization and rulings in force

- **Authorised without asking:** power off (power ON needs the operator's OK, see below), staging builds, running
  benchmark and probe cells for this plan. **Needs an explicit ask:** boot
  config changes, raw sector writes, anything outside this plan.
- **Power, 2026-09-22 late (operator, relayed by the coordinator; replaces the 2026-09-18 "leave
  the target powered between rounds" policy and narrows the standing authorization above):** "power
  off system if it's not needed", and "don't power system on before asking me if it's okay".
  Power-ON is NOT covered by standing authorization: when a hardware cell is ready, the worker stops
  and reports to the coordinator what it will run, the tags, and how long it needs the machine; the
  coordinator asks the operator and sends the go. Power-OFF after a round is still fine.
- **8.3 round GO, 2026-09-22 (operator, via the question tool, relayed by the coordinator). Scope,
  exactly:** (1) the worker may power the target ON for the 8.3 round (SB3O/SB3W/SB3S, PGSB,
  640x480) once the slice-2 pre-registration is committed AND pushed, without stopping to report
  first; power OFF when the round ends; any later round needs a new ask through the coordinator.
  (2) Post-transfer keyboard hang: the harness may cycle mains power ONCE per run to recover; a
  second hang in the same run stops the round -- power off and report.
- **8.3 RE-RUN GO, 2026-09-23 (operator, via the question tool, relayed by the coordinator). Scope:**
  one hardware round, the 8.3 re-run (SB4O / SB4W / SB4S). Power ON once the re-run pre-registration
  is committed and pushed; power OFF when the round ends; one mains cycle per run for the
  post-transfer hang (a second hang in the same run stops the round). Any later round needs a new ask.
- Tearing is accepted; the direct-framebuffer no-vsync path is the
  default (2026-09-18).
- **Sound Blaster first, then Maniac Mansion Deluxe at full speed, then ViRGE/Cirrus** (operator
  direction 2026-09-22; see "Next campaign").
- ViRGE and Cirrus after the fps work; every figure keeps its Mach64
  qualifier (2026-09-20).
- Gate 2 released; the stall is a HARDWARE.md row, not a gate (2026-09-21). (Gate 2 itself was
  later reopened the same day for a different reason: the under-push, see Gates.)
- The 16-bit gate is 5 Days a Stranger at centred 1x; AGS Quest's 38.0 and
  40.61 stay on record as the demo's ceiling (2026-09-21).
- 32-bit: two zero-code cells before any decision (2026-09-21).
- External write-up: no longer blocked by Gate 2; blocked only by having
  a 16-bit figure on a real game. **Now unblocked by that ruling's own terms** (Gate 3 claimed
  2026-09-22 on 5 Days a Stranger in play). Not started; starting it is a separate decision.
- **Operator decision 2026-09-23 (~17:20 PDT, via the coordinator's question tool), scoped to two
  rounds only:** two hardware rounds tonight, **power OFF between them**, and **one hang-recovery
  mains cycle allowed per run**; a second hang in a run stops that round.
  - **Round A:** the lab cells (lab-wb WBH0/2/1/4/3, lab-metric BW32, lab-mmd HW-MMD-0/1/2), taken
    from their committed staging records.
  - **Round B:** after the coordinator verifies A. My 16-bit cells (the stall split, 0210 decode,
    0211/0212 pathfinding before/after at the S16 fixture), lab-metric's 0230 counter off/on pair,
    and C1 off/on x2 if its G1 passes.
  - Power-on for any other round still needs its own GO.
  - **Round F (operator ~20:15Z, question tool: "Wait up to 2 h for the fix").**
    - **D2 variant:** power on as soon as SDL 0213 v2 has my APPROVE, has landed on main, and the
      D2 F/N builds are staged and hashed.
    - **Fallback variant:** otherwise power on at 22:15Z with START, WARMUP, 0305 ABBA, CAP3 (if
      landed and reviewed), STALLH-A0P, S8H-O2, and D2 moves to round G.
    - Rules for both: the C:\DOSAGS fetch comes before any send; the WARMUP cell is unscored; every
      cell's timeout is sized to end before the 90 min cap; WBH6L pauses for the coordinator's go;
      power OFF at the end, confirmed by power_state.
    - Round G needs its own approval.
    - **Staging (2026-09-24, before power-on):** `build/ws/roundF/`.
      - Every base binary is sha256-checked (`expected-base.txt`): AGSL297, AGSL305 `f159e932...`,
        probe60 `a82fcb9b...`, lab-journeys' landed `6a234d23...`, clean4 `cf19f33f...`, and
        **CAP3's lab binary `d7039e45...` (`b561fae61cb3`)**. CAP3 is stageable before landing,
        like C1P/C2P (coordinator; LAB-JOURNEYS 8.11, lab/journeys 934b2030).
      - CAP3 cells, S8H-O1 protocol (room 35, ON cfg, drive-walk 25 2 80): `CAPH1` (no env),
        `CAPH1I` (`DRAIN_STI=0`), `CAPHC` (`DEDUPE=0 MAX_PER_IRQ=256`), `CAPHI`
        (`DRAIN_STI=0 DEDUPE=0 MAX_PER_IRQ=8192`, the input check). drive-walk only clicks, so
        `kbd_undrained` has no key taps to read.
      - Driver `driveF.sh`, both variants: the fetch before any send; the WARMUP tag; cap-aware
        timeouts; CAP3 after D2 or after the 0305 ABBA; the WBH6L pause.
      - The 22:15Z fallback timer is armed.
      - **HOLD (coordinator, 2026-09-24): CAP3 and STALLH are NOT stageable.** cap3 `b561fae61cb3`
        and probe60 `07c3ba0357e1` were built before lab-journeys' rebase and lack main's ags
        0297/0305. The replacements (cap3m `8038393d83de`, `cd6a3e88...`; a rebuilt probe60) wait for
        the coordinator's relayed CONFIRMED with both hashes. Until then the driver records both as
        not run, and they move to round G if F starts first.
      - **Correction (coordinator): STALLH-A0P runs on probe60 as is** (`07c3ba0357e1`, `a82fcb9b...`).
        S8H-A0 itself ran on `32cc99df4761`, which also predates 0297/0305, so probe60 is the closer
        match for placing A0's stall. Released (`STALLH.OK`). **CAP3 stays on HOLD** until cap3m's
        CONFIRMED is relayed.
      - **D2 variant STARTED 21:44Z** (0213 v2 landed at 1301a56e; the fallback timer stood down).
        - **F** = lab-metric's landing binary `build/land0213/ags.exe`, `b983bf9d146a`, sha256
          `02c9eaeb...`.
        - **N** = main's clean build without 0213, `0a40583867d7`, `e403144a...`.
        - **Build-stamp finding:** my own build of main at 1301a56e is `5fa609ba8318`. It differs
          from lab-metric's in exactly 13 bytes, all inside the stamp immediates, with every code byte
          identical. `AGS_BUILD_SHA12` hashes `sha256sum` OUTPUT, which includes the absolute path
          of `sdl3-dos.mk` / `midi_sched.*` / `opl3_sink.*`, so the same series gives a different
          stamp in a different worktree. For identity, compare code bytes or use one worktree's
          file. Candidate fix: hash the files' contents only (`sha256sum < file` or `cut -c1-64`),
          so the stamp is path-independent.
        - Quarantine count for the AQ row: **4 of 10**. The landing gate at 1301a56e ran it 10/10
          in the default mode with `frames_skipped` 0/0; the rule counts every clean run in this
          mode, whoever runs it.
  - **STANDING RULE from round F on (coordinator, 2026-09-24): the first cell after power-on is a
    discarded warm-up; nothing measured runs cold.** lab-mmd found the power-on cell ran ~0.21
    ms/tick slower than the same binary warm (M297A1 cold vs M297A2 warm), while warm same-binary
    runs repeat within 0.02-0.03 ms/tick, even across sessions.
    - The warm-up is a short cell (the Gate 2 BENCH8 cell, or ~3 min of the round's first real
      fixture), tagged WARMUP, not scored, and marked in the staging record.
    - **Earlier measured cells that were power-on (cold) cells, for readers to weigh; nothing
      re-scored:** WBH0 (round A's first), S16B1 (round B), C2PA1 (round C), S16U1 (round D),
      M297A1 (round E).
  - **Round B scope (operator, 2026-09-24, question tool):** "Round B + the MMD cells",
    ~105-110 min, same hang rule (one recovery per run; a second hang stops the round), power OFF
    at the end. Order:
    1. fetch HW-MMD-0's files from `C:\DOSAGS` first;
    2. S16 ABBA x4;
    3. RTHB/RTHN;
    4. C1P x4;
    5. CTR x4;
    6. HW-MMD-1/2 last.
    Deferred: RTHS, STWH, DECHO, DECHN.
  - **Round C (operator, 2026-09-24 ~06:25Z, question tool: "Yes, when core is ready").**
    Power-on is authorized without a further ask, even if the operator is away. Hard cap: 1.5 h
    of target power-on.
    - Order: START (g2k boot config deploy + `SET` check), C2P x4, HW-MMD-4, S16U1, the
      conditional slot (HW-MMD-5, WBH5/6, HW-SBP-0/1), power OFF.
    - START trigger: lab-metric's C2P precondition (the DOSBox-X reproduction of PH01
      `50e4283a24be` and `pushed_px` 34037190 on `a2485a373bd2`) landed and PASSED, verified from
      its raw files.
    - S16U1 only if all three of its preconditions are met at START; the round is not held more
      than ~60 min for it.
    - Slot preconditions are checked when the slot is reached: the lab's committed PASS plus a
      clean build with a hash.
    - Same hang rule. Message the coordinator at power-on and at power-off with raw results.

## The numbers to plan against

**Bus ceilings, measured (bandwidth probe 2026-09-17/19):** LFB near
pointer **27.3 MB/s**; banked A000h **25.0**; Mode 13h aperture **9.3**
(but a 64,000 B frame); system RAM copy **17.0**; RAM write-only **40.9**
(a read costs 1.4x a write). Per full frame at the LFB: 320x200x8 2.2 ms,
640x360x16 16.1 ms, 320x200x32 at 1x 9.4 ms, at 2x (640x400x32) 37.5 ms.
**Any 2x-replicated rung beyond 8-bit is bus-impossible at 40 fps.**
Mach64 has no 320x200/320x240 VESA mode at all; Mode 13h is 8-bit only.

**16-bit non-stall tick, AGS Quest, 24.9 ms (2026-09-19):**
`present_update_window` 11.73 (47%, at the bus ceiling),
`scene_construct` 6.05 (24%), `render_backbuffer` 5.04 (20%; masked blit
at 19.4 cycles/px against a 7.8 copy floor; the opaque-run blit bought
0.48 ms because the sprites are speckled), everything else 2.10 (8%).

**8-bit Mode 13h tick, BENCH8 anim12:** present 4.17 ms,
`render_to_screen` 13.79, `scene_construct` 7.01 at 12 objects
(~0.335 ms per animating sprite, ~3.0 ms fixed).

**What each big win was (8-bit, Trilby idle):** 5.02 -> 7.45 integer
fast blit (0087) -> 8.42 word store (0090) -> 21.05 skip the present when
unchanged (0091) -> 34.62 word-sized compare (0092) -> 40.00 `fps_p50`
from replacing `Clock::now()` (1,324 us per call, 272x `uclock()`, 724 us
of it `mktime`) and the pacer (0096) -> whole-run over 39.2 from not
rebuilding the light table (0117). **16-bit (AGS Quest):** 9.62 -> 13.3
from the 8-bit chain -> 22.95 virtual-screen alias (0120, removes a
26.7 ms RAM copy; engages only on a true 1:1 full-width mode, confirmed
on Mode 13h, NOT on 2x) -> 36.96 multi-rect present (15.5 -> 3.76 ms)
-> 38.0 with 0123/0124 and GUI clip stage 1 (stage 1's premise retracted 2026-09-21, see step 1). **BENCH8:** 14.99 -> 38.87
from Mode 13h; the last 1.1 was un-inlining one hot function (0119).
Two Gate 2 "wins" were removing our own instrumentation (fixture
`WriteLog` handle, SDL trace `fsync` in the present flush, 0189).

## Work order

Each step names its bar or stop condition. Nothing here re-opens the stall.

1. **Housekeeping (records done 2026-09-21, no rig time).** This file;
   `STATUS.md` table; `README.md` Status trimmed; hub `COMPATIBILITY.md`
   and `HARDWARE.md` rows; hub skill reference cut to a checklist.
   **EXPORT DONE 2026-09-21 (dated paragraph below); it was open, and had
   to come first before any cell: export the patch series.**
   `patches/ags/` ends at 0123 and `patches/SDL/` at 0148, but
   `vendor/ags` carries 2,134 uncommitted lines across 22 files (every
   instrument and optimisation cited as patches 0124-0189: narrowed
   present, stall attribution, tail sampling, GUI clip, pacer 0163, trace
   off by default 0189) and `vendor/SDL` 233 lines. This is why every
   gate cell says `build_dirty=1`. A `make patches` resets the vendor
   trees and would destroy it (see the patch-series stamp trap). Commit
   in `vendor/<x>`, `git format-patch`, land in `patches/`, refresh the
   stamp by `series_sha`; then extend `port_game.py`'s hard-coded
   35-phase list so `bg_restore`, `rb_sprite_time` and the `sc_*`
   brackets reach `results/*.json` (today they are logged and dropped).
   Also give BENCH16 a manifest (`tests/games/bench16/`, copy bench8's
   with the depth-16 hashes from `tests/harness/expected/bench16/`).

   **2026-09-21 -- export done; the DOSBox-X correctness gate is NOT clean
   (two findings, neither caused by the export).** Both dirty trees were
   snapshotted first (tree hash of the working state through a temporary
   index), committed in `vendor/<x>` as nine ags patches (0124, 0125, 0127,
   0139, 0140, 0150, 0163, 0167, 0186) and two SDL patches (0177, 0189), and
   `git format-patch`ed into `patches/` (`7e570cd`). The 0124-0189 counter
   was shared by both vendors and intermediate states were never committed,
   so the series is a hunk-level partition by the in-source `patch NNNN`
   comments, not a replay of the order the edits were made in; each commit
   message names its constituent numbers and says its intermediate state was
   not built. 0163 was carved out at line level (every fragment of it is
   labelled) and lands under its cited number; 0189 likewise. Acceptance:
   pin + series in a throwaway clone gives ags `58aae479...` and SDL
   `178b66aa...`, both equal to the pre-export snapshot; the real `make
   patches` reproduces both; `verify-patches-applied` exits 0; `make
   build-dirty` says `build_dirty=0 sha12=667514e4b97d`. `port_game.py` now
   parses the eleven phases it dropped (`ce38f88`: 289 -> 366 fields on
   G2L1.LOG, no existing field changed) and `tests/games/bench16/` exists
   (`342e24f`). Correctness gate on the clean binary, raw in
   `tests/harness/results/EXPORT1-2026-09-21/`: `idle walk anim4 anim12
   text` are pixel-identical to the 2026-09-17 baselines at 8 and 16 bit
   (so the Gate 2 fixture renders as recorded) and the AGS Quest harness
   passes all phases and all three hashes. Two arms fail at both depths.
   (1) `gui`: the capture differs, and `DOSAGS_GUI_NOINVAL=0` restores the
   baseline hash exactly, so the cause is ags patch 0169 stage 1, which is
   ON by default: the fixture hides the menu (`FixedPose`) and waits 40
   ticks, and the menu is still painted (7,559 px). The AGS Quest gate did
   not catch it. That is a defect in default-on behaviour that every gate
   cell since 0169 ran under; what to do about it is not decided here. (2)
   `full`: the run ends 2 s in, after `RestoreGameSlot`, because the
   fixture's `WriteLog` writes to a handle the restore closed. The cause is
   fixture commit `155ad57` (2026-09-20, hold the log handle open), not the
   engine, and no engine switch changes it. `anim12` never saves or
   restores, so the Gate 2 arm is unaffected by either.

   **2026-09-21 -- PRE-REGISTRATION, cell G2R1: reproduce Gate 2 on the
   exported clean binary. NOT YET RUN.** Fixture `bench8 anim12`, Mode 13h,
   `--gate` (5000 ticks), binary `build/ags/ags.exe` sha256
   `6a2639b6f5fa05e0...ec66`, `binary_sha12=667514e4b97d`. Launch:
   `run-hw.sh bench8 --tag G2R1 --gate --extra-file
   tests/harness/games/bench8/ACSETUP-OFF.CFG:ACSETUP.CFG --extra-file
   tests/fixtures/bench/cfg/anim12-gate.cfg:BENCH.CFG`, with no `--env`.
   The environment is not guessed: a search of the allowlist against
   G2L1's recorded `env_block_sha=5a1973c32030` has exactly one solution,
   `BLASTER=A220 I7 D3 P330 T3` + `DOSAGS_FIXED_TIMESTEP=1` and nothing else
   (no `DOSAGS_TAS_AUTO_EXIT_TICK`, no `DOSAGS_SCENE`; the port's "default"
   SDL lines are not in the process environment), so the same hash is the
   witness. Code under test executes on this fixture, from G2L1: `STDOUT.TXT:102`
   `vscreen alias ON y=0 320x200 pitch=320`; `G2L1.LOG:74` `blit_path fast=1
   generic=0 src_bytes_per_pixel=1 unscaled=1`; `:73` `presents_real=2481
   presents_skipped=2515`; `:202` `video_banked_mode=0`; no `<TAG>SDL.LOG`
   collected (trace off). Prediction, from the same source having produced
   G2L1-G2L4: whole-run `tick_rate` **39.41 +/- 0.05** (floor 0.01),
   `tick_rate_steady` **40.01 +/- 0.05**, `fps_p50` **40.00**,
   `frames_skipped` 4 (+/- 2, completeness >= 99%), `presents_real` ~2481,
   `stall_ticks` 0, `loop_ms` ~124,975. The tree is byte-identical to the one
   they ran, so a miss is a finding about the harness or the machine, not
   about a change. Bar: both tick figures inside 39.2 - 40.8 and the
   reproduction inside the tolerance above. A whole-run figure more than 0.2
   off means the exported tree is NOT the tree the record measured: STOP and
   report, do not explain. VOID if: `env_block_sha` is not
   `5a1973c32030`; `build_dirty` is not 0 or `binary_sha12` is not
   `667514e4b97d`; the sha256 of the staged file is not the one above; TZ is
   not set in the run; a non-empty `<TAG>SDL.LOG` is collected (trace must be
   off); the alias line or `blit_path fast=1 ... unscaled=1` is absent; sound
   is not off. Independent bracket: wall-clock start/end of the run on the
   host against `loop_ms + preloop_ms + init`.

   **2026-09-21 -- G2R1 RAN AND IS VOID; the pre-registration's launch recipe
   was wrong (mine).** It staged `tests/harness/games/bench8/ACSETUP-OFF.CFG`,
   which says `fullscreen = full_window`, so the engine asked for 640x480 and
   ran the 2x rung (`Attempt to find nearest supported resolution for screen
   size 640 x 480`, `render dest (0,40,639,439 : 640x400)`). The Gate 2 cells
   staged `tests/harness/presentation/bench8/ACSETUP-OFF-NATIVE.CFG` (one line
   differs: `fullscreen = native`; the record says so at PLAN-LOG "Gate 2 at
   Mode 13h", TNG2M13), which gives `Graphics mode set: 320 x 200 (8-bit)
   fullscreen`. I inferred the recipe from a log instead of reading the record.
   The void conditions written above caught it: no `vscreen alias ON` line and
   `blit_path fast=1713 generic=0 unscaled=0`. The alias did NOT engage on this
   2x rung, so step 2's stop condition did not fire. Second fault, also mine:
   the tag `G2R1` had been used on 2026-09-20, so the collected `G2R1.LOG`
   holds TWO run manifests (the old one, `binary_sha12=327be2b29809`, started
   2026-09-20, and this run's) and `G2R1SDL.LOG` is the OLD run's stale trace
   (it reads `mode-set #1 ... 320x200`); RUN.BAT deletes AUTOPLT.LOG and
   PH0?.BMP but not `<TAG>.LOG` or `LOGS\<TAG>SDL.LOG`. Rule from here: a tag is
   never reused. What the run does show, only as a by-product and NOT a Gate 2
   figure: this binary at the 2x rung, `env_block_sha=5a1973c32030` (the
   environment recovery holds), `binary_sha12=667514e4b97d`, `build_dirty=0`,
   `fps_p50=13.83`, `tick_rate` 39.46 / steady 39.97, 3,250 skipped frames,
   `presents_real=1713`, capture hash identical to the BENCH8 anim12 baseline.
   Raw data is kept in `tests/harness/results/G2R1-2026-09-21/`, marked VOID.

   **2026-09-21 -- PRE-REGISTRATION, cell G2R2: G2R1 done properly. NOT YET
   RUN.** Identical to G2R1 in binary (`build/ags/ags.exe` sha256
   `6a2639b6f5fa05e0...ec66`), fixture and environment, with two corrections:
   the staged config is `tests/harness/presentation/bench8/ACSETUP-OFF-NATIVE.CFG:ACSETUP.CFG`
   and the tag is the never-used `G2R2`. Launch: `run-hw.sh bench8 --tag G2R2
   --gate --extra-file tests/harness/presentation/bench8/ACSETUP-OFF-NATIVE.CFG:ACSETUP.CFG
   --extra-file tests/fixtures/bench/cfg/anim12-gate.cfg:BENCH.CFG`, no `--env`.
   The prediction is NOT revised: G2R1 was void and says nothing about Mode
   13h, so nothing in it can move a number. Whole-run `tick_rate` **39.41 +/-
   0.05**, `tick_rate_steady` **40.01 +/- 0.05**, `fps_p50` **40.00**,
   `frames_skipped` 4 (+/- 2), `presents_real` ~2481, `stall_ticks` 0,
   `loop_ms` ~124,975. Bar and stop rule as for G2R1 (both tick figures in
   39.2 - 40.8; whole-run more than 0.2 off means the exported tree is not the
   tree the record measured -- STOP, do not explain). VOID if any of: the
   collected `G2R2.LOG` holds more than one manifest block; a `G2R2SDL.LOG` is
   collected (trace must be off); `env_block_sha` is not `5a1973c32030`;
   `build_dirty` is not 0 or `binary_sha12` is not `667514e4b97d`; the mode line
   is not `Graphics mode set: 320 x 200 (8-bit) fullscreen`; `vscreen alias ON
   y=0 320x200 pitch=320` is absent; `blit_path` is not `fast=<n> generic=0
   ... unscaled=1`; sound is not off. New witness added because G2R1 needed it:
   the mode line is checked BEFORE any number is read.

   **2026-09-21 -- G2R2 RESULT: not void; 5 of 6 predicted quantities hit, the
   sixth (whole-run `tick_rate`) missed its tolerance by 0.07.** Raw in
   `tests/harness/results/G2R2-2026-09-21/`. No void condition tripped: mode
   line `Graphics mode set: 320 x 200 (8-bit) fullscreen`, `vscreen alias ON
   y=0 320x200 pitch=320`, one manifest block, no SDL trace collected,
   `env_block_sha=5a1973c32030`, `binary_sha12=667514e4b97d`, `build_dirty=0`,
   `blit_path fast=1 generic=0 unscaled=1`, staged file verified byte-for-byte,
   capture hash `9f065048...` equal to the BENCH8 anim12 baseline, exit 0, no
   criticals or warnings. Predicted vs measured (5000-tick window, Mach64,
   fixed timestep, sound off): `tick_rate_steady` 40.01 +/- 0.05 -> **40.01**;
   `fps_p50` 40.00 -> **40.00**; `frames_skipped` 4 +/- 2 -> **4**;
   `presents_real` ~2481 -> **2481**; `stall_ticks` 0 -> **0**; `loop_ms`
   ~124,975 -> **124,974**; whole-run `tick_rate` 39.41 +/- 0.05 -> **39.34**
   (G2L1-G2L4 were 39.41, 39.41, 39.41, 39.40). Both tick figures are inside
   the 39.2 - 40.8 band, so the gate figure passes; the reproduction tolerance
   I wrote does not, and it is 7x the 0.01 floor, so it is stated as a miss.
   It is under the 0.2 stop threshold. **Where the 0.07 is:** whole-run
   runtime is 127.10 s here against 126.87 s (G2L1) and 126.90 s (G2L4).
   `loop_ms` is 124,974 vs 124,975 and `preloop_ms` 686 vs 683-688, so the
   loop and the start of the run are identical; the whole difference is the
   residual of the whole-run denominator, 1,437 ms here against 1,213 and
   1,241 (+224 ms, +196 ms). The engine's own startup report says nothing was
   slower before the first frame (`total_to_first_frame_ms` 4,537 vs 4,678,
   `script_vm_init_ms` 1,621 vs 1,615, `gamedata_asset_load_ms` 294 vs 294),
   and the per-phase totals are essentially the same run (`scene_construct`
   32,079,376 us vs 32,079,473 us; `present_update_window` 4,821,683 vs
   4,820,948). So the exported tree behaves as the tree the record measured.
   What is NOT established is what the 224 ms is: the record already shows
   this residual (it calls it `init`) ranging 920 - 1,380 ms across the
   2026-09-17 BENCH8 cells and 1,218 - 1,298 on 2026-09-20, 1,437 is above
   both, and its size is within the 205 - 219 ms band of the single-sector
   write stall that HARDWARE.md holds as bounded -- consistent with that, not
   shown to be it, and not reopened here. Replication of whole-run comes from
   the anim12 ABBA below (two more cells per arm on the same fixture) rather
   than from an extra cell now. Independent bracket: host wall-clock launch to
   collected 475 s (two reboots, boot, run, one collect reboot), engine
   `duration_s=131`, `loop_ms + preloop_ms` = 125.7 s.

   **2026-09-21 -- STEP 1 CLOSES on this record (coordinator ruling), with
   the words fixed.** Same tree, different bytes: G2L1-G2L4 ran
   `binary_sha12=7eef28ede173` with `build_dirty=1`; G2R2 ran
   `667514e4b97d` with `build_dirty=0`. The oracle shows the two are the same
   source tree, and the timed loop is identical between them
   (`loop_ms` 124,974/124,975, `preloop_ms` 686 vs 683-688). Wording:
   whole-run `tick_rate` **missed** the pre-registered 39.41 +/- 0.05 by 0.07
   (39.34, inside the 39.2 - 40.8 band); the whole gap is +224 ms in the part
   of the denominator outside loop and preloop; the cause is not established
   and the stall is not reopened. Nothing here says "reproduced 39.41" -- the
   subject line of commit `467aa7a` does say "reproduced", and that overstated
   it: five quantities reproduced, whole-run did not. Replication of whole-run
   comes from the anim12 ABBA below (at least two more reads on this binary);
   STOP and report if any of them is under 39.2 or if the +224 ms shows again
   on 2 of the 4 -- a whole-run figure at risk on clean builds is the
   operator's to weigh.

   **2026-09-21 -- SLICE C: make ags 0169 stage 1 sound (ags 0190 measures,
   ags 0191 fixes). Findings, then PRE-REGISTRATION. Nothing on hardware yet.**
   *Source, read not guessed.* `GUIMain::SetVisible`, `SetPosition`/`SetX`/`SetY`,
   `SetTransparency` and `SetZOrder` never mark the GUI changed (`SetSize` and
   content do); `InterfaceOff` invalidates nothing. A frame's UI marks are made
   after that frame's background restore, so they are consumed by the NEXT
   frame's restore, and stage 1 suppresses exactly the mark that would have made
   a hide erase. Underneath that: stage 1's "unchanged" test reads
   `HasChanged()` in the second loop of `draw_gui_and_overlays`, after the first
   loop has re-rendered changed GUIs and called `ClearChanged()`, so it is true
   for every displayed GUI on every frame. **RETRACTED in place (PLAN-LOG,
   "ANSWER: it is gCredits"): the "100% of 421 observations" evidence for stage 1
   was a tautology.** ags 0190 (instrument only, behaviour-identical, committed
   `a8802c5ab`, exported, oracle `efadb459...` = vendor tree) reads the flags
   before the clear. *First move, DOSBox-X AGS Quest, binary `a32b8346c983`,
   raw in `tests/harness/results/S1C0-2026-09-21/`:* **gCredits (idx 7) was
   displayed on 421 frames and its real changed flag was set on 1 of them (its
   first render); gTitleMenu 1 of 1; big-GUI total `changed=2 unchanged=420
   pct=99`. Model M1 (gCredits is static) is what was observed.** `dirtysrc
   uisprite px` is identical to the export binary's (11,723,320), as an
   instrument-only patch requires. DOSBox-X predicts pixel accounting, not rate.
   *The fix (ags 0191), one mechanism: the skip is only valid when this frame's
   composite of the GUI is the one already on screen.* Skip only if the real
   pre-clear flags are clear AND the GUI's X/Y/W/H/transparency/z-order equal
   what its last composite was drawn from (visibility is implied by being drawn).
   Record, per GUI, whether the last composite left its rect unmarked. At the top
   of `construct_game_scene`, BEFORE the restore, invalidate that old rect if the
   GUI is now hidden, moved, resized, re-alpha'd, re-ordered or changed. An
   unchanged, still-visible GUI dirties nothing, which is stage 1's whole win.
   Untracked GUIs (index >= 64) never skip. Stage 1.5/2 and the clip are not
   touched.
   *PRE-REGISTERED correctness gate (DOSBox-X, before the build is run):* (a)
   BENCH8 `gui` capture equals `3cbb692a908b...` and BENCH16 `gui` equals
   `d9eb97884a73...`; (b) `idle walk anim4 anim12 text` unchanged at both depths
   (BENCH8 `e0352be7 b1283ceb 02fa4b2f 9f065048 e69a82cb`, BENCH16 `72b0ad4e
   40bbfddf 64f5f0f1 969a479f c71e4252`) and `full` fails exactly as before
   (F2, its own fix); (c) the AGS Quest harness passes all phases with `PH01-PH03`
   `7ac5213f 3b265167 623fc3a7`; (d) mechanistic, on the AGS Quest DOSBox run: on
   the new `guiskip`/`guitally` lines, gCredits `skipped` >= 415 of 421 (>= 98%)
   and `changed` <= 3, `guiskip flushed` <= 8 and `late` = 0, and `dirtysrc
   uisprite px` within 5% of 11,723,320. A run that keeps the rate while
   `skipped` collapses means the fix disabled stage 1 by accident. Stop and
   report if (a) or (b) fail, if any other arm's hash moves, if the fix needs a
   second mechanism, or if the demo breaks.
   *PRE-REGISTERED real-hardware A/B, both models stated before either is
   seen on hardware.* Fixture: AGS Quest AutoPilot demo (16-bit 640x360, 640x480
   letterboxed 1:1, sound off), `ACSETUP.CFG` staged EXPLICITLY from
   `tests/harness/games/trilbysnotes/ACSETUP-OFF.CFG` in every cell (the record's
   AGS Quest cells took whatever an earlier Trilby cell had left in `C:\DOSAGS`;
   the last file staged there is now the native-size Bench8 one, which would
   silently change the rung). A = the export binary (`build/abba/ags-G2R1-export.exe`,
   sha256 `6a2639b6f5fa05e0...ec66`); B = the ags 0191 binary (sha256 to be
   recorded here before the first cell). Order A B B A, tags `C1A1 C1B1 C1B2 C1A2`
   (never used before). Rule fixed in advance: if the first A cell takes more
   than 13 minutes wall clock (launch to collected; a demo cell ran 281 s of game
   time in 2026-09-17 plus two reboots), drop the last A and run A B B. Metric:
   `tick_rate_steady x (1 - frames_skipped/ticks)` with `presents_real` beside it
   (`fps_p50` is not used: it spread 2.40 over three matched cells while this
   spread 0.05). Noise floor: 0.05, from 38.03 / 37.97 / 38.00 (REPRO1, three
   matched cells, an older binary of this same source; the floor for THIS
   binary is measured by the two A cells). Reference: stage 1 is worth +0.91 (38.03 on,
   37.12 off; skipped 300 vs 382 in 3,577 ticks).
   **M1 (gCredits static; observed in DOSBox-X):** B - A within +/-0.15 (3x the
   floor), expected 0.00 +/- 0.05; the HW `guitally idx=7` reads `changed` <= 3
   and `skipped/n` >= 98%; B `frames_skipped` within +/-10% of A's. **M2
   (gCredits changes on a fraction f of frames on hardware):** each changed frame
   is re-marked, so it pays the restore plus present of a 460x260x2 = 239,200 B
   rect (8.8 ms at the 27.3 MB/s LFB ceiling for the present alone; the record's
   tail frames were 36 - 40 ms against 24.9) and overruns the 25 ms budget, which
   costs about one skipped frame: -0.0116 fps per changed frame (41.5 / 3,577).
   A drop of 0.3 needs about 26 changed frames of ~421, f >= 6%. The hardware
   `changed` count reads it directly, so the models are told apart by a count,
   not by the rate. **The stage-1-disabled signature is `frames_skipped` near 382
   and rate near 37.1.** Ruling (coordinator): the fix stays whatever the rate does
   -- the unsound skip paints wrong pixels for a changing GUI, so a benchmark on it is
   not a valid figure. So there is no rate stop rule; the delta is recorded with the
   tallies and reported. Stop and report only if: the gui arm does not return to
   baseline at both depths, any other arm's hash moves, the fix needs a second
   mechanism, or the demo breaks. VOID a cell if: `env_block_sha` differs between
   arms; `binary_sha12`/sha256 is not the arm's; `build_dirty` is not 0; the mode
   line is not `Graphics mode set: 640 x 480 (16-bit) fullscreen desktop` (and
   `Game native resolution: 640 x 360 (16 bit)`); any AutoPilot phase is not ok
   or `critical_count` is not 0; the tag was used before; more than one manifest
   block; an SDL trace is collected. The `vscreen alias` line is recorded per
   cell, not assumed.

   **2026-09-21 -- SLICE C DOSBOX-X GATE RESULT (ags 0191, before any hardware
   cell). Correctness passes; two of the mechanistic sub-criteria I wrote were
   MISSED, with the cause established.** Raw in `tests/harness/results/
   S1C1-2026-09-21/`. Binary for the hardware arm B: `binary_sha12=53df45d9ac94`,
   `build_dirty=0`, sha256 `e234a22733d6d60609f7c17d06083c19c159ffa324abbd689eaada3b2a6e02be`
   (`build/abba/ags-0191.exe`); ags tree `95bb2b92e048...` = oracle, `make patches`
   reproduces it, `verify-patches-applied` exits 0. (a) BENCH8 and BENCH16 `gui`
   capture == baseline: **PASS at both depths**. (b) `idle walk anim4 anim12 text`
   unchanged at both depths, `full` fails as before: PASS. (c) AGS Quest harness
   all phases ok, `PH01-PH03` match: PASS. (d) gCredits `skipped` **420 of 421**
   (>= 415) PASS; `changed` **1** (<= 3) PASS; `guiskip flushed` **51** against
   my <= 8: **MISSED**; `dirtysrc uisprite px` **12,670,908**, +8.08% against my
   +/-5%: **MISSED**. `late` = 0. The primary mechanism check holds (stage 1's
   win is intact for the GUI that is the entire tail). The misses are a wrong model
   of the OTHER GUIs, established by a reason split (`hidden=4 props=0 flag=47`,
   by GUI idx 2 x37, idx 3 x7, idx 4 x6, idx 0 x1): I priced only the demo's 6
   hides and gCredits, and several GUIs change while drawn. The old tautological
   skip suppressed the mark on those changing frames too, and the fix now marks
   them (about 18.6k px per flush, +947,588 px over the run). That is the defect
   being removed, not a regression in the fix. Nothing about props: no GUI moved,
   re-alpha'd or re-ordered in this run. *Hardware expectation, revised BEFORE any
   hardware cell, from this DOSBox-X count:* the same ~50 flushes are extra work
   on the frames they land on, about 18.6k px each, so the restore plus the present
   of that rect is about 5 ms on the frame (18.6k px x 2 B = 37 KB at 12.2 MB/s
   restore + 27.3 MB/s present), against about 8 ms of slack; expect few overruns.
   B - A therefore expected in **[-0.2, +0.05]**, not the +/-0.15 I wrote around
   zero; the band stated above still applies as the bar (|B - A| <= 0.3), and the
   check that it is this and not something else is the hardware `guiskip` line
   reading flushed within +/-20% of 51 with `flag` ~ 47.

   **2026-09-21 -- F2 (fixture) and the anim12 ABBA: PRE-REGISTRATION. NOT YET
   RUN.** *The change:* one statement, `logf = null;`, at the top of the
   `eEventRestoreGame` branch of `tests/fixtures/bench/AutoPilot.asc`. A restore
   puts the script's globals back as saved, so `logf` names a handle the restore
   closed and the next `WriteLog` fails (`FileWriteRawLine: invalid file handle`,
   the `full` scene ending 2 s in, cause fixture commit `155ad57`). Dropping the
   stale handle makes `WriteLog` reopen in append mode. `WriteLog` and `CloseLog`
   are untouched and no scene but `full` ever restores, so the anim12 path is
   byte for byte the source it was; the compiled package still differs, which is
   why the ABBA below exists. *DOSBox-X bar, predicted before it runs:* `full`
   PASSES at BENCH8 and BENCH16 with capture hashes equal to the baselines
   (`33d19e90...`, `c8463175...`), and every other arm is unchanged at both depths
   (same hashes as in the slice C gate above). If the `full` capture differs from
   its 2026-09-17 baseline that is a finding (something else moved since), not a
   pass. *Hardware ABBA on the Gate 2 arm:* fixture BENCH8 anim12, Mode 13h,
   `--gate` 5000 ticks, `presentation/bench8/ACSETUP-OFF-NATIVE.CFG` +
   `cfg/anim12-gate.cfg`, no `--env`. A = the export binary (sha256 `6a2639b6...ec66`)
   + the OLD fixture package (`BENCH8.ags` sha256 `7e0fbc47...`, saved as
   `tests/harness/games/bench8old/`, run as package `bench8old`); B = the ags 0191
   binary (sha256 `e234a227...02be`, `binary_sha12=53df45d9ac94`) + the FIXED
   package (`BENCH8.ags` sha256 `1371961d...`). Order A B B A, tags `F2A1 F2B1 F2B2
   F2A2` (never used). A is G2R2's configuration exactly, so both A cells are also
   whole-run replicates of G2R2. *Prediction:* B - A = 0.00 +/- 0.02 on steady and
   `fps_p50` (both had spread 0.00 across G2L1-4), and whole-run within +/-0.05.
   *Threshold, from the measured 0.01 floor:* |B - A| <= 0.05 on whole-run, steady
   and `fps_p50` (5x the floor); STOP and report if B is worse by more than that
   on any. What could move B legitimately: the ags 0190/0191 code runs per frame
   (a snapshot loop over `game.numgui` and a per-GUI check, none of it doing work
   with no GUI displayed) and changes code layout, and hot-path layout has moved
   results by up to ~1 fps before, so a miss here is a real finding, not a
   nuisance. *Replication stop conditions (coordinator ruling):* STOP and report
   if any of the four whole-run figures is under 39.2, or if the +224 ms shows
   again on 2 of the 4, where "shows" is defined now as the whole-run denominator's
   residual (`5000 / tick_rate` s minus `loop_ms` minus `preloop_ms`) above 1,400
   ms (G2L1-4 were 1,213 - 1,241 ms, G2R2 1,437 ms). *VOID a cell if:* the mode
   line is not `Graphics mode set: 320 x 200 (8-bit) fullscreen`; `vscreen alias ON
   y=0 320x200 pitch=320` is absent; `blit_path` is not `unscaled=1`;
   `env_block_sha` is not `5a1973c32030`; `binary_sha12` or the staged package is not
   the arm's; `build_dirty` is not 0; more than one manifest block; an SDL trace is
   collected; the tag was used before.

   **2026-09-21 -- THE PRESENT-NARROWING DEFECT (dated note, plain).** On DOSBox-X with the
   ags 0192 verifier: **anim12 is clean in the timed window at Mode 13h (frames 1-502 of 503) and its one
   stale frame is the last, the fixture's `FixedPose` teleport; the walk arm is stale at the same
   rung (from frame 2, 247 px constant); the mechanism exists at the alias rung.** On AGS Quest at
   640x480x16 1:1 letterboxed: 3,100 of 3,565 presents stale (87%); with the narrowing switched off
   (`DOSAGS_DIRTY_PRESENT=0`) the same run is clean on the screen-level series, so the engine's RAM
   frame is right and the defect is which rects get pushed. Raw and method: `tests/harness/results/PRESENTV-2026-09-21/`
   (the verifier matrix, both screen-level series, the Mode 13h runs), `C1A2-2026-09-21/witness/` (the physical
   screen on the export binary) and the operator's photograph of the demo.
   **Every recorded figure whose binary carried ags 0124/0129 on a rung where the narrowing was on
   the path is marked here as UNEXPLAINED, not void, and no new figure is derived from it:**
   AGS Quest 23.98 -> 36.96 (multi-rect, PLAN-LOG "DPX1 scored"), the +0.74 of 0124 itself (PLAN-LOG
   "Patch 0124"), the 38.0 stable rate and stage 1's +0.91 (PLAN-LOG "REPRO1"), the 40.61 hidden-GUI
   probe (PLAN-LOG "NOGUI replication"), and cells C1A1/C1B1/C1B2/C1A2 (all AGS Quest 640x480x16
   1:1, alias ON, `dirtypresent narrow=3258 full=242` in C1A1; trails seen by the operator on C1A1
   and C1B2 and by my capture on C1A2); and BENCH8 anim12 at Mode 13h from 2026-09-19 on (G2L1-G2L4,
   LGOF1/2, LGON1/2, FPT1, G2R2: `narrow=2000 full=0` in G2L1's own log, so every present was
   narrowed), whose timed content is in-place animation. **NOT on the path, and what shows it:**
   every cell at a 2x rung (G2R1's own log at 640x480: `narrow=0 full=1500 rej scaled=1500`, so the
   narrowing rejects every present there), including BENCH8 at 640x480 2x (14.99) and the 2026-09-16
   catalogue rows; and AGS Quest before ags 0124 (22.95, alias only). **Gate 1, in one line:** its
   2026-09-18 binary predates the narrowed present (the first measurement of ags 0124 is
   committed 2026-09-19 08:11, `d273dd6`, after Gate 1 was claimed) and its 640x480 2x rung is one
   where the narrowing rejects every present, so neither Gate 1 nor the re-homed Gate 3 wording is
   touched. Cells not listed were not looked at and are not claimed either way.

   **2026-09-21 -- THE FIX (ags 0193): PRE-REGISTRATION, before it is written or measured.** *One
   mechanism: the pushed set covers every pixel that changed in RAM this present.* Present N pushes the
   marks made since present N-1 UNION the marks the previous interval made AFTER its background restore
   (this frame's restore repaints exactly those regions), plus a full latch at `invalidate_all_rects()`
   and `invalidate_all_camera_rects()` (the whole-surface invalidations `invalidate_screen()` reaches,
   including `Display()` boxes, room changes, fades). "After the restore" is tracked, not assumed, so a
   pre-restore mark is not carried twice and a full latch before the restore does not cost a second full
   push. The verifier is the oracle: if it disagrees with this account, the account loses. Nothing else
   goes in the patch, and a cost above what is written here is reported, not optimised in it.
   *Cost, predicted from the pixel accounting on record and the cost model already in the plan (0.37 ms per
   rect + 15,245 px/ms):* AGS Quest today pushes 12,070 union px in 4.82 rects per present (C1A1
   `dirtypresent`), 6.9% of presents full, mean `present_update_window` 2.43 ms (about 1.3 ms of that is the
   narrowed presents). With the previous interval's marks added for moving content: **union px per present
   x1.6 (1.3 - 2.0), rects per present 4.8 -> 6.3, so `present_update_window` mean 2.43 -> 3.4 ms (2.9 -
   4.0), about +1.0 ms of a 24.9 ms tick, about -1.6 fps on a rate that is itself marked unexplained.**
   *anim12 (in-place spinners): UNCHANGED.* The previous interval's rects equal the current ones, so union
   px per present stay 12,696 +/- 3%, rects stay 8.0 (the box cap), `present_update_window` stays 1.94 ms +/-
   0.1, and its final stale frame (503, the `FixedPose` teleport) goes to 0; if it does not, the mechanism is
   incomplete. *The walk arm (one character moving 1-2 px per tick):* today 3 rects, about 1,050 px per
   present; with the fix about 1,150 px (x1.1, range 1.0 - 1.4), still 3 rects, so the present is about 1.2
   ms and cheaper per tick than anim12's spinners (8 rects); it presents nearly every tick (content changes
   every tick), so `presents_real` is about the tick count where anim12's is 2,481, which is +1.1 s of
   present time over 125 s. **Predicted walk arm at Mode 13h `--gate` (5000 ticks, clean build, this fix):
   `tick_rate_steady` 40.01 +/- 0.05, whole-run 39.34 - 39.41 (the same tail as anim12), `fps_p50` 40.00,
   `frames_skipped` <= 8, completeness 99% or better, `presents_real` ~4,990.** The walk arm's window is
   `tests/fixtures/bench/cfg/walk-gate.cfg` (`hold_ticks=4960`); the fixture keeps the character walking
   for the whole window because `RunWindow` calls `WalkLeg()` whenever the player is not moving and the
   four legs loop, so no fixture slice is needed. **DOSBox-X gate, all before any hardware cell:** the
   verifier reads `stale_frames=0` on the whole AGS Quest AutoPilot run at defaults; on bench8 walk AND
   anim12 at the alias rung (`ACSETUP-OFF-NATIVE.CFG`, Mode 13h) and at the 2x rung; on bench16 at the 2x
   rung and at the centred-1x rung (`ACSETUP-OFF-640X480.CFG` with `DOSAGS_MAX_SCALE=1`, the rung the
   16-bit gate uses, where the narrowing is on the path); on every other arm; a V0-style screen series is
   clean at walking and speech moments (sheet looked at by a person); and every existing hash is unchanged.
   Pixel accounting on DOSBox-X predicts the ratios above (post/pre union px: anim12 1.00, walk 1.1, AGS Quest
   1.6), not the rates. Stop and report if the verifier reads stale after the fix (a second mechanism), or
   if anim12's cost moves.

   **2026-09-21 -- 0193 GATE RESULT and TWO OF MY PRE-REGISTERED PREDICTIONS CORRECTED IN PLACE (the wrong
   versions above stay visible).** Raw in `tests/harness/results/G93-2026-09-21/`. AGS Quest whole AutoPilot
   run: verifier `stale_frames 0 / 3862`, all phases and hashes pass; bench8/bench16, all seven arms, at the
   alias, 2x and 16-bit centred-1x rungs: 0 stale and every hash equal, EXCEPT bench16 `gui` at centred 1x, 480 of
   1038 stale (see ags 0194 below). anim12 at Mode 13h 0 / 503: its final teleport frame went 1 -> 0 as
   predicted; the walk arm at Mode 13h 0 / 199 (was 198 / 199). *Cost, predicted vs measured (DOSBox-X pixel
   accounting; rates are not predicted by it):* anim12 **unchanged as predicted** (12,702 px and 8.0 rects per
   present before and after). AGS Quest union px per present **x1.11 measured against x1.6 predicted (1.3 -
   2.0): MISSED LOW**, rects per present 4.84 -> 4.84 against 4.8 -> 6.3 predicted: MISSED. **The model lesson, one
   line: at 1 - 2 px per tick a moving sprite's old and new rects overlap and merge in the box set, so the carry
   is nearly free (I assumed they were disjoint).** Revised `present_update_window` for AGS Quest: 2.43 -> about
   2.6 ms (+0.2), not 3.4. *The walk arm's pre-registered "presents nearly every tick, `presents_real` ~4,990" is
   WRONG:* AGS moves the character every few ticks, and DOSBox-X reads `presents_real=983` of 5,001 ticks (19.7%,
   verifier 0 / 983, `tick_rate_steady` 40.01) on the full 5000-tick `--gate` window (`walk-gate.cfg`, native
   rung, raw in `G93-2026-09-21/`'s companion run). **Corrected prediction for the walk arm at Mode 13h on
   hardware: `presents_real` 983 +/- 50, steady 40.01 +/- 0.05, whole-run 39.34 - 39.41, `fps_p50` 40.00,
   `frames_skipped` <= 8.** The window is defined and validated: `RunWindow` loops `WalkLeg()` for the whole
   4,960 ticks (real presents are spread through it, not front-loaded), so no fixture slice is needed. **The walk
   arm's present load is about 40% of anim12's (983 against 2,481 real presents), so it is an EASIER band than
   anim12; its passing must not be read as more than "a moving position at Mode 13h".** Step 2's predictions
   (the 512x384 rungs assumed full-frame pushes, which a correct narrowed present can only undercut) stand within
   their ranges; the carry adds about 0.2 ms per present on AGS-Quest-like content. S2Q1's basis (the AGS Quest
   38.0) is one of the figures marked unexplained above, so its 16 (8 - 25) is now unanchored, and is reported as such.

   **2026-09-21 -- ags 0194: PRE-REGISTRATION (one mechanism), and why the other rungs did not show the bug.**
   *The defect (0191, mine):* the skip's "same picture as last frame" test compares a GUI with its LAST RECORDED
   composite, and that record stays valid while the GUI is hidden. A re-shown GUI has no changed flag
   (`SetVisible` marks nothing, its texture is clean) and identical properties, so it qualifies as unchanged and its
   invalidation is skipped: the menu is composited into RAM and never pushed. Diagnosis by one switch, bench16 `gui`
   at 640x480x16 centred 1x: `DOSAGS_GUI_NOINVAL=1` (default) 480 / 1036 stale, `=0` 0 / 1035. *The fix:* a GUI that
   is not drawn this frame (hidden, fully transparent, or the UI layer not drawn at all) has its skip record
   invalidated at the end of `draw_gui_and_overlays`, so a re-show is treated as new and marked. Nothing else.
   *Why the other rungs hid it, from counters:* (1) **2x rungs**: the narrowing rejects every present, G2R1's own
   log reads `narrow=0 full=1500 rej scaled=1500`, so a full push masks any narrowing bug there; the verifier cannot
   fail at 2x. (2) **8-bit alias (Mode 13h)**: bench8 `gui` reads `presents_real=52` of 1041 ticks and those 52 are
   clean; with `DOSAGS_PRESENT_NO_SKIP=1` (a present every tick) the same rung reads **480 / 1041 stale**,
   `first_stale_frame=62`. So the 8-bit unchanged-frame path hid it by deciding which ticks present; I have NOT
   established whether it does that by a full push or by frame selection. (3) **16-bit rungs** present every tick
   (no unchanged-frame skip at 16 bpp), so the centred-1x rung is where it showed. **Which rungs the verifier can
   and cannot see a narrowing bug on:** it can at centred 1x at both depths, and at the 8-bit alias rung only with
   `PRESENT_NO_SKIP=1`; it cannot at any 2x rung, and at the default 8-bit alias rung it sees only the ticks the
   unchanged-frame path lets present. The same class may hide behind any other full-push path. *Predictions
   (falsifiable):* bench16 `gui` at centred 1x **480 / 1038 -> 0**; every other row of the matrix stays 0 stale with
   equal hashes (35 rows below plus the AGS Quest run); bench8 `gui` at the alias rung with `PRESENT_NO_SKIP=1`
   **480 / 1041 -> 0** (which would show the bug was there too); AGS Quest: gCredits `skipped` stays 420 +/- 3 of 421
   and `changed` 1 (a static still-visible GUI must still skip), `guiskip flushed` 51 +/- 2, and union px per present
   within +/-1% of the 0193 run (13,142). If the skip counters collapse while stale reads 0, the fix disabled stage 1
   by accident.
   **THE STANDING PRESENT-CORRECTNESS GATE (MANDATORY, `tests/harness/gate-present.sh`):** every fixture arm x
   {alias / Mode 13h (8-bit only), 2x, centred 1x} x {8, 16 bit} where the rung exists (35 rows) plus the AGS Quest
   AutoPilot demo at defaults, verifier `stale_frames=0` and capture hash equal to `tests/harness/expected/`, exit 1
   on any failing row. Required for any change that touches GUI invalidation, the dirty accumulator, or the pushed
   rects, alongside the BENCH8/BENCH16 `gui` arms. **In place: ags 0191 was gated only at the default rungs (2x,
   and 8-bit alias where the unchanged-frame path hid it), which is how its skip bug got through; ags 0193's gate
   found it.**

   **2026-09-21 -- ags 0194 RESULT (DOSBox-X, `tests/harness/results/G94-2026-09-21/`), binary `binary_sha12=e8d4b76c5cd9`,
   `build_dirty=0`, sha256 `7243c1884ba3...bdd42`, ags tree `6e73ba0db8a5...` = oracle, `make patches` reproduces it,
   `verify-patches-applied` exits 0.** The standing gate: **35 of 35 rows and the AGS Quest whole run read
   `stale_frames=0` with every capture hash equal.** Predictions vs results: bench16 `gui` centred 1x **480/1038 ->
   0/1038 (met)**; every other row 0 stale, hashes equal (met); bench8 `gui` at the alias rung with
   `PRESENT_NO_SKIP=1` **480/1041 -> 0/1041 (met, which shows the bug was there too and was only hidden)**; AGS
   Quest gCredits `skipped` **419 of 420** (predicted 420 +/- 3, met), `changed` 1 (met), `guiskip flushed` **51**
   (predicted 51 +/- 2, met); union px per present **13,160 against 13,142 (+0.13%, inside +/-1%, met)**, rects per
   present 4.84. Stage 1's win is intact. Not reachable under DOSBox-X: 512x384 (needs UniVBE's mode; the oversized
   conf falls back to 640x400 2x), so the 640x480 centred-1x rows stand in for it at both depths, where the alias
   does not engage (`alias=0`, not full width).

   **2026-09-21 -- HARDWARE, FINAL BINARY (ags 0194): PRE-REGISTRATION for cells F2A1/F2B1/F2B2/F2A2, W1/W2, AQF1/AQF2.
   NONE RUN YET. Supersedes the F2 ABBA arm B above (the ags 0191 binary is not the final one; that text stays
   visible), and the slice C export-vs-0191 AGS Quest A/B (the export binary is the trails binary, so that
   comparison is no longer meaningful; the sound-skip question is answered by the tallies and the AQF cells).**
   *Common to every cell:* B binary = `build/abba/ags-0194.exe`, sha256 `7243c1884ba3...`, `binary_sha12=e8d4b76c5cd9`,
   `build_dirty=0`; the physical-screen witness is ON (it is the first real-hardware test of the runner: **if a
   cell's witness is SHORT or the sheet is unusable, STOP and fix the runner before any further cell**); a
   `witness/REVIEWED.txt` written by `witness_review.py` after I have LOOKED at `sheet.png` and `sheet-camera.png` is
   required before any rate from that cell is recorded (port_game/parse-results refuse it otherwise); a sheet
   showing trails voids the rate and stops the campaign; the mode line and the alias line are read BEFORE any
   number; fresh tags; raw under `results/<TAG>-2026-09-21/`; power on with `--power-on` (the operator lifted the
   hour hold), then LEAVE IT POWERED between cells. Stop and report on: any trails, a verifier/hardware
   disagreement, anim12 outside 0.05 of G2R2, any whole-run under 39.2, the keyboard hang recurring after the one
   guarded recovery (`run-hw.sh` now does that itself after 3 refused collections with a DOS prompt on screen,
   mock-tested only, so its first real trigger is itself a result to report).
   *Group 1, anim12 ABBA, Mode 13h* (`ACSETUP-OFF-NATIVE.CFG` + `anim12-gate.cfg`, `--gate`, no `--env`; the mode line
   must read `Graphics mode set: 320 x 200 (8-bit) fullscreen` and `vscreen alias ON y=0 320x200 pitch=320` be
   present). A = export binary (sha256 `6a2639b6...ec66`, `binary_sha12=667514e4b97d`) + OLD package (`bench8old`,
   `BENCH8.ags` sha256 `7e0fbc47...`) = G2R2's configuration; B = 0194 + the FIXED package (`bench8`, sha256
   `1371961d...`). Order A B B A, tags `F2A1 F2B1 F2B2 F2A2`. *Prediction:* B - A = 0.00 +/- 0.02 on `tick_rate_steady` and
   `fps_p50`, whole-run within +/- 0.05 (mean of the two B against mean of the two A); each cell `presents_real` 2481
   +/- 10, `present_update_window` mean 1.94 +/- 0.1 ms (anim12's union is unchanged by 0193, so nothing here should
   move), `frames_skipped` 4 (+/- 2), `stall_ticks` 0, `loop_ms` ~124,975; A cells replicate G2R2 (39.34) within the
   run-to-run spread seen so far (39.34 - 39.41). The new per-tick code (0190-0194 with the verifier off) is one
   cached-getenv branch and a small loop over the carried boxes, expected well under 0.1 ms per tick. *Threshold:*
   |B - A| <= 0.05 on all three, STOP if B is worse by more; STOP if any whole-run is under 39.2 or the whole-run
   denominator residual (`5000/tick_rate` s minus `loop_ms` minus `preloop_ms`) exceeds 1,400 ms in 2 of the 4. Witness:
   clean (12 in-place spinners; the fixture's final teleport frame is after the timed window).
   *Group 2, walk arm, Mode 13h, 5000-tick `--gate`* (`walk-gate.cfg`; B binary + fixed package; tags `W1 W2`; same rung
   and void conditions). Prediction from the revised accounting: `presents_real` **983 +/- 50** (about 20% of ticks),
   `tick_rate_steady` 40.01 +/- 0.05, whole-run 39.34 - 39.41, `fps_p50` 40.00, `frames_skipped` <= 8, completeness
   >= 95% (`presents_real` over content-dirty ticks), `present_update_window` mean 0.6 - 1.6 ms. **The walk arm's present
   load is about 40% of anim12's, so this is an EASIER band; passing means "a moving position at Mode 13h" and no
   more.** Witness: one character walking a loop, clean.
   *Group 3, AGS Quest demo on the final binary, 2 replicates* (tags `AQF1 AQF2`, no `--gate`, ACSETUP staged
   explicitly from `games/trilbysnotes/ACSETUP-OFF.CFG`, same rung as C1A1: `Graphics mode set: 640 x 480 (16-bit)
   fullscreen desktop`, `Game native resolution: 640 x 360 (16 bit)`, `vscreen alias ON y=60 640x360 pitch=1280`).
   Reported against the 38.0 record (a figure marked unexplained, from a renderer with the under-push) with
   denominators: **`tick_rate_steady x (1 - frames_skipped/ticks)` with `presents_real` beside it.** *Prediction
   (the correct present costs a little, pixel accounting says +0.2 ms per present, about 0.8% of the 25 ms tick):*
   stable rate **37.6 (37.0 - 38.2)** against 37.81 / 37.82 on the trails renderer (C1A1 / C1B1), `tick_rate_steady`
   41.1 (40.8 - 41.4), `frames_skipped` about 8% of ticks (290 +/- 30 of ~3,575), `presents_real` about the tick count
   (about 3,590), `present_update_window` mean **2.6 ms (2.4 - 3.0)** against 2.43, `guitally` gCredits skipped
   >= 95% of n and changed <= 3, `guiskip flushed` 51 +/- 5, replicate agreement within 0.3 (stop if wider; the only
   measured floor for this fixture is 0.05, from an older binary). Witness: the demo's walking, speech and menus, clean.
   This group answers slice C's remaining question (did 0191's sound skip cost anything): its cost is the
   tallies plus the AQF rates, not an A/B against a binary that draws trails.
   *Step 4 of the hardware order (step 2's five catalogue cells) waits for these three groups' witness reviews and for
   step 2's predictions to be re-done for 0193/0194 and committed.*

   **2026-09-21/22 -- AQF1/AQF2 RESULTS, WITNESS REVIEWED CLEAN, BOTH REPLICATES.** Fixed binary
   (ags 0194, `e8d4b76c5cd9`), `env_block_sha 5a1973c32030`, `build_dirty 0`. Both replicates
   landed on IDENTICAL raw fields (the demo's AutoPilot script is deterministic): `tick_rate_steady`
   **41.18** (predicted 41.1, 40.8-41.4 -- met), whole-run 20.60 (structurally the same shape as
   every other whole-run figure in this campaign), `frames_skipped` **295 of 3,577** (predicted
   ~290 +/- 30 of ~3,575 -- met), `presents_real` **3,586** (predicted ~3,590 -- met),
   `present_update_window` mean **2.55 ms** (predicted 2.6, 2.4-3.0 -- met), `guiskip flushed`
   **51** (predicted 51 +/- 5 -- met), `guitally` gCredits **187 of 188 unchanged, 1 changed**
   (predicted >=95% skipped and <=3 changed -- met). **Stable rate `tick_rate_steady x
   (1 - frames_skipped/ticks)` = 37.78 both replicates** (predicted 37.6, 37.0-38.2 -- met),
   against the 38.0 record (a figure itself marked unexplained, from the trails renderer): 0.22
   below, inside the predicted band, not called a pass or a regression on rate alone per the
   standing rule -- both witnesses reviewed card+camera clean first. Replicate agreement: exact
   (both cells' every raw field identical), well inside the 0.3 stop-width.
   Witness: both AQF1 and AQF2 card+camera sheets reviewed (`witness_review.py`, verdict clean,
   REVIEWED.txt bound to both sheet hashes each); complete backgrounds throughout, no trails, no
   repeated sprites. **One item investigated before either verdict:** AQF2 frame 11 (both card
   and camera) shows the demo's topic-list GUI with every line's leading glyph cut flush to the
   left raster edge (x=0). Root-caused via DOSBox-X: the AGS dialog-options render loop
   (`Engine/ac/dialog.cpp`, its own `while (_dlgNum >= 0)` loop calling `UpdateGameOnce()`/
   `render_graphics()` directly) bypasses `dos_run_tick_fixed()`, so `DOSAGS_FREEZE_TICKS`
   (ags 0195) cannot reach it -- confirmed empirically, zero markers over ticks spanning
   AUTOPILOT's own logged window with wide margin. Caught instead with a 0.12s `--screen-series`
   on the identical binary+package+cfg: the GUI renders **complete under both** the alias present
   path and a full unnarrowed push (`DOSAGS_DIRTY_PRESENT=0`) -- not present-path-dependent (the
   coordinator's test comes back negative on both sides), not a trail, not missing background.
   Recorded as hardware capture-chain framing (overscan-like, at the literal left raster edge on
   HW-486-66's CRT/capture chain), not a port software defect; not patched. Full evidence:
   `tests/harness/results/AQF2-DLG-2026-09-21/README.md`. This closes Group 3 of the pre-
   registration above; step 4 (the five catalogue cells) is now unblocked.

   **2026-09-21 -- F2A1 IS VOID; THE CAMPAIGN STOPS AT THE PHYSICAL SCREEN. (Recorded in place; nothing above is deleted.)**
   F2A1 (A = export binary + old package, Mode 13h, the G2R2 configuration) ran and its numbers are valid as a read of the
   loop (mode line, alias line, `env_block_sha`, `binary_sha12 667514e4b97d`, `build_dirty 0`, steady 40.01, `presents_real`
   2481, `frames_skipped` 4, whole-run 39.27), but **the physical screen showed the anim12 room as BLACK with small lit
   patches only around the spinners** (the coordinator's camera, 3 frames, lit fraction 0.13; my own three camera frames
   say the same). **I first described those frames as clean and dark; that was wrong** (I read a missing background as
   low exposure), and the F2A1 README now says so. Under this plan's own rule a run whose screen shows an incomplete picture
   has no rate: **F2A1's rate is VOID.** F2B1 (B = ags 0194 + fixed package, same rung) shows the COMPLETE room (brick wall,
   window, pillar, sign, floor, spinners, player, key) on every one of its camera frames. **G2L1-G2L4 and G2R2 were the
   same A configuration and had NO physical-screen witness (no camera frames of them exist), so what their screens showed is
   UNKNOWN; nothing further is inferred, and Gate 2 stays REOPENED.** The card also froze at Mode 13h in both cells
   (`card-state.log` in F2B1: `locked` for the first ~9 s, then `nosignal` with the frame counter stuck for the rest of the
   run), so at the alias rung the CAMERA is the only physical witness and is treated as such (8 s cadence, camera-only review
   only on a recorded frozen card). *What I know and do not:* the emulator and the hardware disagree on the SAME A
   configuration (DOSBox-X's ags 0192 verifier read anim12 at Mode 13h as 1 stale frame in 503); the verifier zero-initialises
   its shadow, so a never-pushed first frame would have been flagged there. **The mechanism is a HYPOTHESIS, not a finding:**
   H1, ags 0193's second half (a whole-surface invalidation such as a room load never reaches the accumulator, so the first
   present after it is narrowed to the spinners' rects and the static background is never pushed) fits the picture, but
   the emulator did not show it, so something differs between the two: timing (the fast conf never falls behind, so the
   catch-up loop never runs there), the palette-only/fade path, or the hardware flush path. **DIAGNOSTIC ROUND, no more cells than
   these:** (b) ONE hardware cell, `F2D1` = A binary + OLD package at Mode 13h with `--env DOSAGS_DIRTY_PRESENT=0` (a full push
   every present), 1000-tick window (`anim12.cfg`, not `--gate`; NO rate is recorded from it), witness reviewed. *Prediction:*
   **a complete room** (H1: the narrowed push is the defect). If it is STILL mostly black the defect is the backend or the
   aperture, not the rect list, and H1 is refuted. (c) DOSBox-X, A binary + old package, Mode 13h, emulated-screen capture
   (`--screen-series`) at the fast conf AND the parity conf (slower CPU, so the game falls behind like hardware), compared
   against the hardware frames; the ags 0192 binary (the A code plus the verifier) for the verifier read. (a) F2A2 is NOT run;
   F2B2 only after F2B1's own sheet is reviewed clean across the whole run.

   **2026-09-21 -- DIAGNOSTIC ROUND RESULT (raw: `results/F2A1`, `F2B1`, `F2B2`, `F2D1`, `PRESENTV-2026-09-21/alias-rung-screen-bisect`).**
   *(b) F2D1, met:* A + old package at Mode 13h with `DOSAGS_DIRTY_PRESENT=0` shows the COMPLETE room on the physical screen (camera;
   two frames inside the ~25 s game window, so thin); the defect is the narrowed push, not the backend or the aperture.
   *(c) DOSBox-X reproduces F2A1's picture at screen level* on the A binary (fast conf; the parity conf was not needed): black room, lit
   patches only around the spinners, player, key and cursor. **So the emulator and the hardware did not disagree; the ags 0192 verifier was
   blind.** *Bisect, six binaries, emulated-screen game-phase median brightness (complete room ~30, patches ~8):* export 8.2, 0190 8.2,
   0191 8.2, 0192 8.2, **0193 30.0, 0194 30.0**: incomplete in every binary up to 0192, fixed by 0193. *Verifier blind spot, in place:* the
   0192 binary with the alias ON reads `stale_frames 0` while its screen is incomplete; with the alias OFF it reads 503/503 stale
   (`first_stale_frame=1`) and the screen is still incomplete; with narrowing off it reads 0 and the screen is complete. **This CORRECTS my
   plain dated note above ("anim12 is clean in the timed window on DOSBox-X ... the mechanism exists at the alias rung") and the ags 0194
   result's use of the verifier as an oracle at the alias rung: at the 8-bit Mode 13h alias rows of `gate-present.sh` the verifier proves
   nothing, and only the emulated-screen series does.** Why it is blind with the alias on is NOT established (candidate, unproven: the
   alias adoption drops the frame already drawn and 0193's forced full pushes paper over it; with the alias on the engine frame and the
   window surface are the same memory, so a region never drawn reads equal to a shadow that was never written). *Records:* the
   physical-screen defect existed on every binary from the 0124 present narrowing through ags 0192 at Mode 13h; **G2L1-G2L4 and G2R2 used
   that configuration (same tree by the oracle, same fixture, same rung) and have no physical-screen witness, so their screens are
   unknown; DOSBox-X shows the incomplete screen for that configuration, which is evidence, not proof, about them.** Gate 2 stays REOPENED.
   *F2B1 and F2B2 (B = 0194 + fixed package, Mode 13h, `--gate` 5000 ticks, `binary_sha12=e8d4b76c5cd9`, `build_dirty 0`, env
   `5a1973c32030`, mode line `320 x 200 (8-bit) fullscreen`, alias line `y=0 320x200 pitch=320`, no SDL trace), both witness-REVIEWED clean,
   camera-only on a recorded frozen card (10 game-phase camera frames each, complete room, no trails):* whole-run **39.34 / 39.34**, steady
   **40.01 / 40.01**, `fps_p50` 40.00 / 40.00, `frames_skipped` 4 / 4, `presents_real` 2,481 / 2,481, `present_update_window` mean 1.93 /
   1.93 ms, stable rate 39.978 (`40.01 x (1 - 4/5000)`) with 2,481 real presents over 5,000 ticks, `stall_ticks` 0, `loop_ms` 124,980.
   Predicted vs measured (B against G2R2's reading): unchanged within 0.05 on all three: **met** (39.34 = 39.34). What it does NOT show:
   an A-to-B difference, because A1 is void and A2 was not run, so the ABBA is not formed. Note the identical figures mean the COMPLETE
   picture costs nothing measurable on this fixture, whose background is static. **Stop condition tripped, reported:** the whole-run
   denominator residual is 1,432 ms and 1,427 ms in the two valid cells (my rule: above 1,400 ms in 2 of the 4); whole-run is 39.34 in
   band, not under 39.2; the residual's cause is not established and the bounded stall is not reopened. **Gate 2's closing condition
   is NOT closed by this:** it also requires a walk-arm cell in band, and its verifier clause is void at this rung (above).
   *Cadence note:* the capture card froze at Mode 13h in both B cells (`card-state.log`: `locked` for the first ~8 s, one `frozen`, then
   `nosignal` with the frame counter stuck), so at the alias rung the camera at 8-12 s is the only physical witness; the card does lock
   640x480 rungs (the AGS Quest cells' card frames were live). Not yet established whether it cannot lock Mode 13h at all or loses lock
   after the switch (the stream shows it loses lock within seconds of the game's mode set).

   **2026-09-21 -- ALIAS-ON ROWS, THE VERIFIER'S SCOPE (corrected wording, in place; the paragraphs above are not deleted), THE
   SCREEN == FULL-PUSH GATE, AND THE MECHANISM READ.** *Which standing-gate rows are alias-ON:* the seven 8-bit Mode 13h rows of
   `gate-present.sh` (`alias=1` in G93/G94's `summary.txt`) and the AGS Quest AutoPilot row (alias ON at 640x480x16, `y=60 640x360
   pitch=1280`); all 28 other rows have `alias=0`. *Wording, as the coordinator corrected it (and I had overstated it as "verifier-blind at
   the alias rung"):* the ags 0192 verifier answers "do the pushed rects cover what the engine drew", and it IS sensitive to under-pushed
   marks at an alias rung (AGS Quest at `y=60`: 3,100 of 3,565 stale before ags 0193, 0 of 3,862 after, which is real evidence about marks).
   It cannot answer whether what it models as pushed reached the SCREEN. **So G93's and G94's "clean" means: clean for the 28 non-alias rows,
   and for the 8 alias rows clean for the RAM-versus-push model only; it did not cover the screen.** *The gate that does:*
   `tests/harness/gate-alias.sh` (ags 0195 freezes the engine at chosen ticks, `run-dosbox.sh --freeze-capture` photographs the emulated screen once
   per marker, `screen-equal.py` compares run A, default present, against run B, `DOSAGS_DIRTY_PRESENT=0`, the full-push reference, pixel for pixel,
   voiding a pair whose two runs froze at different ticks) with run C, `DOSAGS_BREAK_0193=1`, as a known-bad control. **Result on ags 0195
   (the 0194 code plus the two diagnostics), raw in `results/GALIAS-2026-09-21/`: A == B at every moment in all eight alias rows, and the control
   FAILS in all eight.** Per row: bench8 Mode 13h `idle`, `walk`, `anim4`, `anim12`, `text`, `gui`: 5 of 5 moments (ticks 100, 300, 500, 700,
   900) equal; `full`: 2 of 2 (the arm ends before tick 80, so only ticks 10 and 40 exist; a weak row); AGS Quest: 10 of 10 (ticks 100, 420 speech and
   walking, 700, 1000, 1300, 1600 room change, 1900, 2200, 2700 GUI menu, 3300), every A-vs-B pair frozen at the same tick. The control differs from the
   reference in all 5 anim12 moments (205,192 px, the whole game area) and in the other rows; **in AGS Quest 8 of its 10 moments differ (25 to 22,642 px) and
   2 were VOID, not different (the control froze at tick 1001 and 1301 against the reference's 1000 and 1300)**, so it is the check's evidence of
   power on that row, not a clean sweep. Predicted before it ran: A == B everywhere on 0194's code (the bisect said the picture is complete) and
   the control to fail everywhere: both as predicted. *Gate 2's closing condition:* the coordinator replaced its "verifier `stale_frames=0`" clause for alias
   rows by "screen == full-push reference" and will tell the operator; that is this gate.
   *The mechanism read, one bounded read and two runs (candidates labelled as candidates):* (a) **REFUTED, my earlier candidate:** alias adoption
   drops the frame already drawn. `Present()` adopts the alias only AFTER a normal copy (`if (!_aliasActive && blitted) DosPortAliasTryActivate`,
   "after the fact, never predicted"), so the frame is on the window surface when the alias takes over. (b) **REFUTED, the reading that the engine never drew
   into the adopted surface:** at the known-bad configuration (ags 0195 + `DOSAGS_BREAK_0193=1`, Mode 13h anim12, `midshot`), the ENGINE's own frame at
   mid-run (`PH02.BMP`) is the complete room while the emulated screen at the same tick is missing the background (non-black fraction 1.000 against 0.152; the
   same run without the knob reads 0.599). The loss is between what the engine pushes and what reaches the screen. (c) **REFUTED, a mid-run display reset:**
   the SDL trace of that configuration shows one framebuffer creation at flush 0, mode sets #1 and #2 at start and #3 only at shutdown. (d) **NOT ESTABLISHED,
   and a CANDIDATE only:** why the verifier reads 0 there (its shadow models "pushed" as "asked to push", so a push that did not land reads as landed), and what
   exactly is lost; ags 0193's full pushes at whole-surface invalidations remove the symptom without my having shown which lost push it re-delivers.
   (e) **CANDIDATE, unshown to fire in any fixture here:** `DosPortAliasDeactivate()` (a shake, a flip, a scaled rung, any geometry deviation) switches
   `virtualScreen` back to the owned buffer WITHOUT copying the aliased frame back, so the owned buffer holds the pre-adoption content; nothing in ags 0193
   covers that with a full push. Not tested, not patched. *Whether anything other than a room load can re-trigger the original loss (a mode change, a fade
   or palette change, a GUI, a window size change):* not shown by any run so far; the gate's `gui` and AGS Quest GUI-menu moments are equal at the alias
   rows, no fixture exercises a mode change mid-run, and a patch for (d) or (e) would be a separate mechanism, reported first.
   *Instrumentation inventory, added:* ags 0195 (`DOSAGS_FREEZE_TICKS`/`_MS`, `DOSAGS_BREAK_0193`): a cached-getenv branch per tick and per merge, nothing
   measured on hardware; **removal condition: both knobs are REMOVED (not merely defaulted off) by the release-packaging series before any release
   artefact, because a switch that re-breaks a shipped fix must not ship**; until then they are allowlisted (a run that used one hashes differently) and
   `run-hw.sh` refuses them outside a `DIAG*`-tagged cell. OPEN.
   *Hardware binary:* the walk-arm and AGS Quest cells continue on the 0194 binary (`ags-0194.exe`, sha256 `7243c188...`), the one F2B1 and F2B2 ran and
   whose evidence they are; ags 0195 adds only the two diagnostics above and is what the alias gate ran, so the gate is evidence about 0194's code and
   not a different binary's.
   *Whole-run, one read and no cell:* **finding: clean-build whole-run is 39.34, in band with 0.14 margin, on three cells of two different clean binaries (G2R2 on the
   export binary, F2B1 and F2B2 on 0194), against 39.41 on the 09-20 cells that ran a dirty binary (`7eef28ede173`, the same tree by the oracle); the 39.41 is not
   the clean-build figure.** The denominator (runtime minus loop) is 2,123 / 2,117 / 2,117 ms on the clean cells against 1,896 ms on G2L1 (residual after the
   preloop 1,437 / 1,432 / 1,427 against 1,213); the +215 to +224 ms is systematic on clean binaries, not a one-off, and I have not rounded it. *What is in it:*
   whole-run is `loop counter / get_runtime_ms()` sampled at quit.cpp:546, anchored at `start_game()`; `preloop_ms` (about 686) is measured separately;
   `loop_ms` ends at the last tick's exit; after that the fixture's `SaveScreenShot(PH01.BMP)`, `CloseLog()` and `QuitGame(0)` run and `quit()` runs its
   shutdown (CD, video, audio, `engine_shutdown_gfxmode`, `allegro_exit`) all BEFORE line 546, so an end-of-run file write does fall inside the denominator.
   `save_config_file()` is not compiled into this build (`AGS_AUTO_WRITE_USER_CONFIG` has no match), so it is not the candidate. **CANDIDATE, not claimed:** one
   end-of-run write (the `PH01.BMP` screenshot or the log flush) landing on a sector that stalls 205 to 219 ms, the bounded CF-write stall the record already
   holds, which the 215 to 224 ms shift matches in size; an equally unshown alternative is the directory-size effect the record already tied to `init` (more entries
   on `C:\DOSAGS` today than on 09-20). The CF stall is NOT reopened.

   **2026-09-21 -- CAVEATS ON THE ALIAS GATE (coordinator's, recorded), AND THE 5000-TICK WINDOWS VALIDATED.** Caveats: the gate is DOSBox-X only; the `full` row has
   only 2 freeze points; the AGS Quest control has 8 usable pairs (2 voided for a tick mismatch); the NON-alias rungs (2x, centred 1x) are covered by the
   RAM-versus-push verifier of `gate-present.sh`, not by this gate. *The two `--gate` windows, run through `gate-alias.sh` with freeze points spread across the
   whole window (ticks 500, 1500, 2500, 3500, 4500) and the auto-exit raised to 6000 so the 5000-tick window is not cut:* **walk-gate** completes
   (`phase=walk status=ok tick=4960`), verifier `stale_frames 0 / 982`, `presents_real` 982 of 4,976 render passes (the pre-registered 983 +/- 50), screen ==
   full-push at 5 of 5 points, control fails (as required); **anim12-gate** `stale_frames 0 / 2,473`, `presents_real` 2,473, 5 of 5 equal, control fails.
   So the walk arm's window is defined (`walk-gate.cfg`, `hold_ticks=4960` + 40 settle = 5000 ticks; `RunWindow` re-issues `WalkLeg()` whenever the player stops, so the
   character walks for the whole window and real presents are spread through it) and DOSBox-X-validated with the verifier and screen-equality clean. Raw:
   `results/GALIAS-2026-09-21/gate-windows-5000/`.
   **W1, W2 (walk arm, Mode 13h, 0194 binary + fixed package, `--gate`): launch note. PROCESS CORRECTION, mine: I meant to write this BEFORE launching W1; the edit
   failed silently (a wrong anchor), commit 66f1639's message wrongly says PLAN.md was updated, and W1 was launched (23:39 UTC) first. This note was written while W1 was
   running and before any of W1's results had been read; the tightening below comes from the clean-build finding, not from W1.** Group 2's pre-registration above stands with
   one tightening: **whole-run 39.34 +/- 0.05 (not 39.34 - 39.41), the denominator residual about 1,430 ms**; `presents_real` 983 +/- 50, steady 40.01 +/- 0.05, `fps_p50` 40.00,
   `frames_skipped` <= 8, completeness >= 95%, `present_update_window` mean 0.6 - 1.6 ms. Witness: camera at 8 s cadence (the card is expected to freeze at Mode 13h,
   recorded), one character walking a loop, complete room, no trails; REVIEWED.txt written before any rate is. Tags `W1`, `W2` were never used. Stop and report on any trail or
   incomplete-screen frame, a witness SHORT without a recorded reason, or whole-run under 39.2.

   **2026-09-21 -- W1 AND W2 RESULT (walk arm, Mode 13h, `--gate` 5000 ticks; raw `results/W1-2026-09-21`, `W2-2026-09-21`).** Identity, both cells: `binary_sha12=e8d4b76c5cd9`,
   `build_dirty 0`, `env_block_sha=5a1973c32030`, mode line `Graphics mode set: 320 x 200 (8-bit) fullscreen`, alias line `vscreen alias ON y=0 320x200 pitch=320`, blit path
   `fast=1 generic=0 unscaled=1`, one manifest block, no SDL trace, `stall_ticks 0`. **Witness: REVIEWED clean, camera-only on a recorded frozen card** (locked 4 / frozen 1 /
   nosignal 39 samples, 2 unique card frames of 11), 10 game-phase camera frames each at 8 - 12 s spacing: complete room in every frame (brick wall, window, pillar, sign, floor,
   key), ONE character at a different position each time (a walk loop; W1 and W2 show the same positions, the script being deterministic), no duplicated copies, no missing
   background, brightness 19.5 - 19.7 throughout. *Predicted vs measured (W1 / W2):* whole-run **39.34 +/- 0.05 -> 39.34 / 39.32 (met)**; `tick_rate_steady` **40.01 +/- 0.05 ->
   39.99 / 39.99 (met, 0.02 under)**; `fps_p50` **40.00 -> 40.00 / 40.00 (met)** (`fps_p95` 40.16); `frames_skipped` **<= 8 -> 4 / 4 (met)**; `presents_real` **983 +/- 50 -> 982 / 982 (met)**;
   completeness >= 95%: 982 real presents against at most 4 skipped renders, >= 99.6% (met); stable rate `steady x (1 - skipped/ticks)` = **39.958 / 39.958**, 982 real presents
   over 5,000 ticks; `present_update_window` mean **0.6 - 1.6 ms -> 0.50 / 0.50 (MISSED LOW by 0.1 ms: a single walking character makes fewer and smaller rects than my model)**.
   Denominator residual (whole-run minus loop minus preloop) **1,375 / 1,438 ms** against my 1,400 ms rule: one below, one above; the cell-to-cell spread (63 ms) is larger than
   the clean-build pair anim12 gave (1,432 / 1,427), cause not established. **This is the easier band (983 real presents against anim12's 2,481); it says "a moving position at Mode 13h
   in band with a complete picture" and no more.** *Gate 2's closing condition, as the coordinator restated it, on the evidence in hand:* anim12 (F2B1, F2B2) and the walk arm (W1, W2) are
   in band (39.2 - 40.8 on both tick figures, `fps_p50` >= 40, completeness >= 95%) at Mode 13h on the fixed binary, clean build, witness reviewed clean, with screen == full-push clean on
   DOSBox-X for both arms at their 5000-tick windows; **I am not changing any gate's wording; that is the operator's.**

   **2026-09-21 -- F2 DOSBOX-X BAR RESULT: MET.** Raw in
   `tests/harness/results/F2D-2026-09-21/`, recorded into both manifests by
   `port_game.py record` (a second `validated:` entry each; the first, failing
   BENCH16 entry stays as history). On `binary_sha12=53df45d9ac94` with the fixed
   packages, **all seven arms pass at BENCH8 and at BENCH16 with capture hashes
   equal to the baselines**, including `full` (`33d19e90...`, `c8463175...`), which
   had ended 2 s in. Every other arm is unchanged. So both DOSBox-X failures of the
   export binary are closed: `gui` by ags 0191 and `full` by the fixture change.
   The hardware anim12 ABBA above is still to run.
2. **Re-baseline the catalogue on the current binary -- zero code, five
   cells.** Trilby's Notes in play (walk into room 2, ~5000 ticks driven by
   vcctrl input, hold-then-release clicks), 5 Days a Stranger, Maniac
   Mansion Deluxe, Shards of God, AGS Quest forced-32. Each at its best
   available rung with `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`. Read
   `present_update_window`, `presents_real`, and whether the alias
   engaged. *Stop and re-read the record if the alias ever engages on a
   2x rung.* Output: one row per game in `STATUS.md` with a date.

   **2026-09-21 -- STEP 2 PRE-REGISTRATION (five cells, none run yet).** *Binary:*
   the FINAL one, ags 0191 (`binary_sha12=53df45d9ac94`, sha256 `e234a227...02be`,
   `build_dirty=0`, oracle re-verified). It carries the stage-1 fix, so it matters
   most for the GUI-heavy titles (5 Days, Maniac Mansion), whose GUIs change while
   drawn -- the case the old skip got wrong. *Uniform:* `--env
   SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`, fixed timestep (run-hw default), sound-off
   config staged EXPLICITLY (the catalogue titles' `ACSETUP-OFF.CFG` are byte-identical
   to Trilby's, checked, so Trilby's `presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG`
   serves all four 320-wide titles), a never-used tag per cell (`S2T1 S2F1 S2M1
   S2S1 S2Q1`), and the expected `env_block_sha` is computed in advance from the
   recovered hash function (it reproduces G2L1's `5a1973c32030`), so the exact
   environment is a witness. Read and record per cell: `present_update_window`
   (calls, total, mean), `presents_real`, `presents_skipped`, `frames_skipped`,
   whole-run `tick_rate` AND `tick_rate_steady`, `fps_p50` (render passes only), the
   stable rate `steady x (1 - skipped/ticks)` with the window in ticks beside it,
   the mode line, and whether `vscreen alias ON` appeared, cited by line. Every
   figure is Mach64-qualified. *Rungs, "best available" from the ladder in step 3
   (BENCH8: 14.99 at 640x480 2x, 19.72 at 640x480 centred, 26.89 at 512x384 centred):*
   the four 320-wide titles at **512x384 centred 1x** (UniVBE modes `0x01F3` 8-bit,
   `0x01D4` 16-bit, `0x01B3` 32-bit are all in the target's own enumerated list);
   AGS Quest forced-32 at 640x480x32 (`0x01B0`) 1:1 letterboxed, its native rung.
   *The alias:* it engages only on a true 1:1 FULL-WIDTH mode (ags 0120), so at
   512x384 with a 320-wide game it should be ABSENT on the four, and present on
   AGS Quest (640 wide). It engaging on a 2x rung is the stop condition; none of
   these cells is a 2x rung, so a 2x line in any mode line means the rung was not
   obtained and the cell is VOID. *What each cell is:* Trilby's is IN PLAY; the other
   four are title-idle windows to an auto-exit tick, as their recorded rows were, and
   are labelled that way in STATUS.md -- the catalogue titles have no AutoPilot and
   5 Days in play is step 4's job. Note on the plan text: it says "room 2"; the
   record's own room table has room 2 as Trilby's main menu and room 3 (Forest with
   Treehouse) as the gameplay room, so the in-play cell uses room 3.
   **Cells and predictions (a model and a number each; a 4x miss either way is a
   finding about the model, and is reported as one).**
   *S2T1, Trilby's Notes in play, 8-bit 320x240.* `run-hw.sh trilbysnotes --tag S2T1
   --timeout 1800 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env
   DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 3 --extra-file
   <512x384 round cfg>:ACSETUP.CFG`, with `tests/harness/drive-walk.sh S2T1` running
   alongside (blind hold-then-release walk clicks every 8 s after a 25 s warm-up).
   The engine's `--startr 3` puts it in the forest room at tick 0 (a DOSBox-X trial
   of exactly this reached room 3 and ran 1,200 ticks unattended, but only 62 of
   1,195 render passes were real presents -- an idle room, hence the driver).
   Expected `env_block_sha=459dcb815359`. Mode line
   `Graphics mode set: 512 x 384 (8-bit) fullscreen`. Model: 320x240x8 is 76.8 KB, so
   the RAM copy (no alias at 512 wide) is 4.5 ms at 17 MB/s and a full-frame push 2.8
   ms at the 27.3 MB/s LFB ceiling, on top of about 6-8 ms of scene work: about
   15 ms per tick, inside the 25 ms budget. **Predicted stable rate 34 (25 - 40),
   `tick_rate_steady` >= 39.** In-play witness: `presents_real` >= 30% of render
   passes, else the driver did not keep it in play and the cell is reported as an
   idle-room cell, not as in play. Falsified by a stable rate under 8 or by alias ON.
   *S2F1 and S2M1, 5 Days a Stranger and Maniac Mansion Deluxe, 16-bit 320x200,
   title idle to tick 1000.* Extra: `--env DOSAGS_TAS_AUTO_EXIT_TICK=1000`. Expected
   `env_block_sha=d5be4eb3c26d`; mode line `512 x 384 (16-bit) fullscreen`. Model: the
   unchanged-frame skip does not fire at 16 bpp (`presents_skipped=0`, PLAN step 4),
   so each tick pays the generic RAM copy, 128 KB = 7.5 ms at 17 MB/s, plus a
   narrowed present and about 5 ms of engine: about 13 ms. **Predicted stable rate
   30 (25 - 40) each**, against the 2026-09-16 rows of 5.45 and 2.73 at the 2x rung
   (whose frame is 512 KB, 4x the pixels, replicated). Falsified by under 7.5.
   *S2S1, Shards of God, 32-bit 320x200, title idle to tick 300* (a short window:
   the last recorded rate was 0.32 ticks/s, so 300 ticks is about 15 minutes if
   nothing improved, and the run-hw timeout is 1800 s; whole-run `tick_rate` is
   therefore NOT comparable to the 5000-tick rows and steady is the figure).
   Expected `env_block_sha=508eb9c56b2d`; mode line `512 x 384 (32-bit)`. Model: the
   0.05 fps of 2026-09-15 was the 2x replicate of a 1 MB frame through the generic
   scaled path; at 1x the frame is 256 KB (15 ms RAM copy, 9.4 ms full push), so the
   floor is about 25 ms/tick before the game's own 32-bit work. **Predicted steady
   20 ticks/s (5 - 40).** Falsified by under 1.25 (a 4x miss low) -- which would say
   the slowness was never the replicate. Feeds step 5's rule (within ~2x of 9.4 ms
   per full frame).
   *S2Q1, AGS Quest forced-32, 16-bit content run at 32 bpp, 640x480x32 1:1
   letterboxed, the AutoPilot demo to tick 1500.* Extra: `--env
   DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_TAS_AUTO_EXIT_TICK=1500`, config staged
   from `games/trilbysnotes/ACSETUP-OFF.CFG` (the same rung as the 38.0 cells).
   Expected `env_block_sha=bec92cf273e7`; alias expected ON. Model, from the record's
   own ratio: at 2026-09-16 the 32-bit arm ran 2.88 against 6.67 for the 16-bit arm of
   the same build, 0.43x; today's 16-bit figure is 38.0, so **predicted stable rate
   16 (8 - 25)** (the 921,600 B frame is 33.8 ms at the LFB ceiling if pushed whole,
   which the narrowed present avoids). A 4x miss either way is under 4 or over 64
   (the latter cannot be). Steady is compared, not whole-run (window 1500 ticks, and
   the demo's blocking operations dominate the whole-run figure).
   *VOID a cell if:* `env_block_sha` differs from the value written above; the mode
   line is not the one written above; `binary_sha12` is not `53df45d9ac94` or
   `build_dirty` is not 0; the tag was used before; more than one manifest block; an
   SDL trace is collected; or, for S2T1 only, the run did not reach room 3. *Stop
   and report if* the alias engages on a 2x line, the target cannot be driven, or a
   cell changes the record's mode for a reason I cannot read from its own log.

   **2026-09-21 -- STEP 2 PREDICTIONS, REDONE FOR ags 0193/0194 (written before any catalogue cell; the earlier ones above stay visible).** *What changed:* (1) the binary
   is `ags-0194.exe` (`binary_sha12=e8d4b76c5cd9`, sha256 `7243c188...`), not the ags 0191 build named above (`53df45d9ac94`); (2) at the 512x384 centred rungs
   the alias does NOT engage (a 320-wide picture is not full-width; the source read is in step 3) and the narrowed present IS on the path, now correct: the
   pixel accounting on record gives about +0.2 ms per present on moving content (union x1.11 on AGS Quest, x1.00 on in-place animation) and nothing on a static
   screen, so no prediction below moves outside its stated range; (3) every cell now needs a physical-screen witness reviewed clean before any rate is written
   (camera at <= 8 s; the capture card where it has signal, and it may or may not see 512x384, recorded either way), and a sheet showing an incomplete
   picture voids the rate; (4) the alias-on-2x-rung stop rule is unchanged; the DIAG-only variables are refused outside `DIAG*` tags. *Cells and predictions, unchanged in
   number and model but restated so they are on the record for this binary:* **S2T1** Trilby's Notes in play, 512x384x8: stable rate 34 (25 - 40), `tick_rate_steady` >= 39,
   `presents_real` >= 30% of render passes, alias absent, mode line `512 x 384 (8-bit) fullscreen`, `env_block_sha=459dcb815359`; **S2F1** 5 Days a Stranger and **S2M1** Maniac
   Mansion Deluxe, 512x384x16, title idle to tick 1000: stable rate 30 (25 - 40) each, `env_block_sha=d5be4eb3c26d`, `presents_skipped` 0 at 16 bpp; **S2S1** Shards of
   God, 512x384x32, title idle to tick 300: steady 20 ticks/s (5 - 40), steady only, `env_block_sha=508eb9c56b2d`; **S2Q1** AGS Quest forced-32, 640x480x32 alias ON: 16
   (8 - 25), UNANCHORED (its basis, the 38.0, is one of the figures marked unexplained). Every figure Mach64-qualified, `tick_rate_steady x (1 - frames_skipped/ticks)` with
   `presents_real` beside it and the window in ticks. These run only AFTER W1/W2 and AQF1/AQF2 are witness-reviewed.

   **2026-09-22 -- S2T1 RESULT: MODE/TICK PREDICTION MET, IN-PLAY CRITERION FALSIFIED.** Room 3
   reached (`Now in room 3`), mode line `512 x 384 (8-bit) fullscreen`, no alias line (matches
   the prediction: absent at 512x384 with a 320-wide game), `env_block_sha=459dcb815359`,
   `binary_sha12=e8d4b76c5cd9`, `build_dirty=0`, no VOID condition. `tick_rate_steady` 39.99
   (predicted >= 39 -- met), whole-run 39.05, `frames_skipped` 10 of 4999, stable rate
   `39.99 x (1 - 10/4999)` = **39.91** (predicted 34, 25-40 -- inside the range, above the
   central estimate). **`presents_real` 180 of `renders` 4968 = 3.6%**, far under the
   pre-registration's own 30% in-play bar, despite `drive-walk.sh` running 23 clicks across the
   full window -- the camera's ~8s-cadence samples show the character visibly near-stationary
   across most of the run. Per the pre-registration's own falsification rule ("`presents_real`
   >= 30% of render passes, else the driver did not keep it in play and the cell is reported as
   an idle-room cell, not as in play"): **this is an idle-room cell, not a sustained in-play
   measurement** -- the tick figures are real but describe a room that was drawn 180 times, not
   one played continuously. Not a defect in the port; a finding about the driver/model: an 8 s
   click period is too sparse against this room's walk-cycle length to sustain >=30% real
   presents (the DOSBox-X trial's 5.2% -- 62/1,195 -- from the pre-registration said as much in
   advance). Witness: card is solid black from frame 2 on (raw pixel min=max=0; anticipated,
   the card may not see 512x384); camera shows real, complete content throughout at a 6-7x
   brightness boost -- a standing character, a doorway, no trails, no missing background, single
   character instance every frame; reviewed clean (`witness_review.py`). Results:
   `tests/harness/results/S2T1-2026-09-22/`.

   **2026-09-22 -- S2F1 RESULT: PREDICTION MET.** 5 Days a Stranger, title idle to tick 1000,
   512x384x16, `env_block_sha=d5be4eb3c26d` (matches), mode line `512 x 384 (16-bit) fullscreen`,
   no alias (matches), `presents_skipped=0` at 16bpp (matches), no VOID condition.
   `tick_rate_steady` 40.20, `frames_skipped` 5 of 999, stable rate **39.999** (predicted 30,
   25-40 -- inside range, at the ceiling, same pattern as S2T1: tick figures on an idle title
   screen read near the model's upper bound). `presents_real` 1007 (a static title still redraws
   every tick under this present path -- not a completeness concern for a title-idle cell, which
   has no in-play bar). Witness: card shows boot text then a uniform flat frame (min=max=7) for
   the game window -- does not see 512x384, same as S2T1; camera frames 3-4 show the title
   screen complete at a 6x brightness boost (car under trees at dusk), no trails, no missing
   background; reviewed clean. Results: `tests/harness/results/S2F1-2026-09-22/`.

   **2026-09-22 -- S2M1 RESULT: MODEL FALSIFIED, ROOT-CAUSED TO ONE TICK PHASE.** Maniac Mansion
   Deluxe, title idle to tick 1000, 512x384x16, `env_block_sha=d5be4eb3c26d` (matches), mode line
   `512 x 384 (16-bit) fullscreen`, no alias (matches), no VOID condition; `render dest (96, 92,
   415, 291 : 320 x 200)` -- "round" (integer) scaling puts this title at 1x within the 512x384
   window (320x200 does not fit a 2x rung there), same as the other three 320-wide titles, not a
   different scale path. **`tick_rate_steady` 28.34, `frames_skipped` 761 of 999, stable rate
   6.75** -- against the prediction of 30 (25 - 40), a clear miss below the stated range (a
   ~4.4x miss against the 30 central estimate). Falsifies the model's assumption (`presents_skipped=0`
   at 16bpp, ~13ms/tick) for THIS title specifically; `presents_real` 251, `present_update_window`
   mean 0.74ms -- the PRESENT side is cheap and matches the model, so this is not a present-path or
   alias-adjacent cost. **Root cause, from the tick's own phase breakdown:** `tickstats_process_events_dispatch`
   alone costs **26.47 ms mean per tick** (1000 calls, one outlier at 894ms), which by itself equals
   or exceeds the entire 25ms tick budget regardless of anything else -- explains the 76% tick-skip
   rate directly. Every other phase is cheap (`render_to_screen` 18.50ms is a nested subset of the
   same tick, not additive on top of dispatch). Read as this specific title's own character-select
   screen (a row of clickable portraits, "Please select two other kids") doing per-tick hover/hotspot
   event evaluation across many GUI controls, not a rendering or present-path defect -- no patch
   proposed. Still a real improvement over the 2026-09-16 pre-optimisation baseline (2.73 at the old
   2x rung) even though it misses the new model badly. Witness: card doesn't see 512x384 (as before);
   camera shows the title screen complete across every sampled frame (portraits, prompt text,
   cursor icon), no trails, no missing background; reviewed clean. Results:
   `tests/harness/results/S2M1-2026-09-22/`.

   **2026-09-22 -- S2S1 STOPPED: SECOND COLLECTION FAILURE IN ONE RUN, HELD FOR THE OPERATOR.**
   Shards of God, title idle to tick 300, launched normally (env staged, mode requested). During
   collection, `run-hw.sh` hit "get-file refused 3 times after the game exited; screen=ready-
   prompt" -- the post-FTP keyboard-hang signature -- and its one automatic recovery (power-
   cycle) ran and RECOVERED (`boot_s=40 screen=ready-prompt verify_input=True`, 01:38:59Z). About
   6.5 minutes later the SAME symptom recurred; `hw_guard` correctly refused a second automatic
   power-cycle in one run ("a second reboot failure in one run is a hardware fault, not something
   to power-cycle through") and stopped (`run-hw.sh` exit 3). No `S2S1.LOG`/manifest was
   collected -- **no rate, no VOID, this cell did not complete measurement.** Per the standing
   rule ("stop and report if... the target cannot be driven"), stopping here rather than retrying
   past the guard's refusal on my own judgement.
   **Current state, checked read-only immediately after:** `vcctrl_power_state` shows the target
   powered, drawing 24,190 mW (a normal idle/ready draw, matches the post-recovery figure from
   the HW-MAINS-CYCLE entry above); the camera shows a clean `C:\>` prompt with a complete normal
   boot log behind it; `vcctrl_verify_input`'s Caps Lock round-trip **succeeded** ("the target
   acknowledged a keystroke", restored). The target is responsive right now -- whatever caused
   the second refusal is not presently reproducing, but two failures in one run is exactly the
   pattern the guard's one-recovery-per-run policy exists to catch rather than paper over.
   Partial witness/recovery artifacts (no measurement) kept at
   `tests/harness/results/S2S1-2026-09-22-STOPPED/`. Holding S2S1 (and S2Q1 after it) for the
   coordinator/operator's call on whether to retry with a fresh tag now that input is confirmed,
   or investigate further first.

   **2026-09-22 -- CHEAP CORRELATION CHECK (coordinator's request, from logs already in hand, no
   hardware touched).** RUN.BAT launched 01:21:42.433Z; no PS/2 keystroke is sent by `run-hw.sh`
   again until it is ready to type at a DOS prompt post-collection -- the wait-for-launch and
   collection phases are pure screen-polling and FTP-pull attempts (a different channel), zero
   keyboard activity. **First hang trigger:** 01:38:59Z, i.e. **17m17s** with no keystroke sent
   (the wait-loop itself had already called the screen "static" by 01:23:20, 98s in, so the true
   idle-looking stretch may be longer still). Recovery (power-cycle, `boot_s=40`) completed and a
   new pull attempt is already running by 01:39:00Z. **Second hang trigger:** 01:45:36Z, i.e.
   about **6m** after the post-recovery ready point, again zero keystrokes sent in between.
   **Reading:** both occurrences DO follow an extended stretch of zero PS/2 activity, consistent
   with the coordinator's candidate (a PS/2-over-USB4VC link timeout under prolonged inactivity)
   rather than a developing hardware fault -- stated as a candidate, not claimed. One honest
   complication: the two idle stretches are different lengths (17m17s vs ~6m), so this is not a
   single fixed-idle-timeout signature; if a timeout is the mechanism, this data bounds it at or
   under about 6 minutes, it does not confirm one. Recorded as a candidate only, per instruction.
   **Per the coordinator's decision: retrying once now (fresh tag), same pre-registration; a
   third occurrence across two attempts stops for real, no second manual retry.**

   **2026-09-22 -- S2S2 (THE RETRY) HIT THE SAME SIGNATURE TWICE MORE. STOPPING FOR REAL, PER THE
   COORDINATOR'S BOUND. NO SECOND MANUAL RETRY.** Fresh tag, same pre-registration, same command.
   RUN.BAT launched ~01:50:15Z. **First hang/recovery: 02:07:22Z** (`boot_s=39`,
   `verify_input=True`) -- **17m7s** with zero PS/2 keystrokes sent, matching S2S1's 17m17s to
   within 10s. **Second failure (hard stop): 02:14:00Z**, about **5m59s** after the post-recovery
   ready point -- matching S2S1's ~6m to within a few seconds. `run-hw.sh` exit 3 again, no
   manifest collected, no rate, no VOID. This is the **third and fourth occurrence of the same
   "get-file refused 3x, screen=ready-prompt" signature across two independent run attempts** --
   past the coordinator's bound (a third occurrence stops for real). **Not attempting a second
   manual retry.** Current state, checked read-only: `vcctrl_power_state` 24,185 mW (normal),
   camera shows a clean `C:\>` prompt with the full boot log behind it -- the target is
   responsive again right now, same as after S2S1's stop.
   **Updated reading on the correlation check, now with a second data point:** the two runs'
   timings are strikingly close (17m7s vs 17m17s to the first hang; 5m59s vs ~6m to the second),
   far too close to be coincidental. That argues AGAINST pure USB4VC-link-timeout randomness and
   FOR something deterministic tied to this specific cell: most likely Shards' own tick-300
   execution time on real hardware is highly reproducible (matching its historic sub-1-fps 32-bit
   rate), so the collection loop starts polling a still-running game at the same relative offset
   both times, cycles through the same number of refused pulls, and lands on the same
   "screen=ready-prompt but FTP refused" dead-link state at the same elapsed times in both runs.
   That still does not identify WHAT makes the link go dead (link timeout vs. something in how
   this specific 32-bit/slow-exit sequence leaves the target) -- stated as a sharper, but still
   unconfirmed, candidate for the coordinator to take to the operator as asked.
   Artifacts: `tests/harness/results/S2S2-2026-09-22-STOPPED/`. **S2S1/S2S2 status: neither
   measured; holding S2Q1 for the coordinator's word per the bound.**

   **2026-09-22 -- OPERATOR DECISION: INVESTIGATE THE HANG NOW (via the coordinator).** Naming
   note, so it is not conflated with the known g2k fault: g2k's documented "post-FTP keyboard
   hang" shows the screen STATIC MID-FTP-OUTPUT with no prompt; this one shows a FULL `C:\>`
   prompt with `get-file` itself refused 3x. Same discipline (second failure stops, tell the
   user), different signature -- not assumed to be the same mechanism.

   **STEP 1 (no hardware, from logs already in hand): is `verify_input` ALSO failing at the
   failure point, before any power-cycle?** Read `hw_guard.py`'s `cmd_recover` precisely: on the
   FIRST failure in a run it calls `verify_input()` as its very first action, BEFORE any recovery
   action -- logged as the `verify_input_before` field on the RECOVERED line. (On a SECOND
   failure the function returns immediately once its per-run state file exists, before ever
   calling `verify_input()` again -- so there is no at-failure reading for the second occurrence
   in either run, only for the first.) Both runs already have this exact reading:
   `verify_input_before=false` on S2S1's first hang (01:38:59Z) AND on S2S2's first hang
   (02:07:22Z). **Answer: yes -- the independent PS/2 round-trip check fails at the same moment
   as the FTP refusal, in both occurrences measured. This is a genuine input-subsystem freeze,
   not an FTP/network-only issue that happens to look like one.**
   **Correction to the earlier correlation-check writeup, found while reading this code for step
   1:** `get-file --return`'s own return leg (`vcctrld.py` `_leave_net`) sends a REAL
   `ctrl+alt+delete` PS/2 combo on every attempt, successful or refused, as part of its normal
   reboot-back mechanism (confirmed by reading `daemon/vcctrld.py` in the vcctrl repo, `_enter_net`
   line ~8699 and `_leave_net` line ~8784). So the "17m17s / 17m7s with zero keystrokes" framing
   in the earlier correlation check was WRONG: `run-hw.sh`'s collection retry loop calls a fresh
   `get-file --return` roughly every ~190s while refused, and each call sends its own
   enter/leave-NET reboot chords. The target was not sitting in silence for 17 minutes; it was
   sent repeated Ctrl+Alt+Delete combos throughout that window (this is normal, successful
   behaviour on every OTHER cell run today -- S2T1/S2F1/S2M1 all collected cleanly through this
   same mechanism on the first attempt). The near-identical S2S1/S2S2 timings (17m7s vs 17m17s;
   ~6m both times) are therefore closer to "N repeated reboot-cycles in, the link goes dead" than
   "N minutes of silence, the link times out" -- a different candidate than originally framed,
   still unconfirmed, and this is corrected here rather than left standing.

   **STEP 2 PRE-REGISTRATION (both outcomes stated before running, per instruction).** Fixture:
   `bench8`, idle scene, `DOSAGS_TAS_AUTO_EXIT_TICK=200` (exits in ~5s, well inside its normal
   near-40fps rate) -- a fast, disposable, unrelated fixture, not S2Q1 (keeping the one remaining
   real step-4 measurement clean of a deliberately-abused timing). `ACSETUP-OFF-NATIVE.CFG`, Mode
   13h, same rung as the Gate 2 cells. **The genuine-idle version of the test, as asked:**
   `RUNHW_MIN_WAIT_S=1260` (21 minutes) forces `wait_for_stable_screen` -- confirmed by reading it
   just now to be pure passive screen/card-state polling, no `vcctrl` input command anywhere in
   it -- to hold for at least 21 minutes (longer than the 17m7s/17m17s observed trigger, and past
   the operator's 20-minute ask) with LITERALLY ZERO keystrokes sent, game already idle at its own
   DOS prompt for nearly all of it, BEFORE the first (real, keystroke-sending) collection attempt
   of the normal retry loop begins. Tag `HANGTEST1`.
   **(a) It reproduces** (any refusal requiring the guarded recovery, or `verify_input_before=false`
   on a fresh trigger): genuine idle silence alone is sufficient to kill the link on a fixture with
   no relation to Shards or 32-bit -- a general infrastructure risk for any long-idle-driver cell,
   worth a campaign-wide keepalive mitigation (step 3a).
   **(b) It does not reproduce** (collection succeeds cleanly, first or later attempt, no
   guarded recovery needed): pure idle silence for 21 minutes is NOT sufficient by itself --
   points at something in Shards' OWN execution/exit sequence (32-bit, or repeated-reboot-cycling
   during its unusually long refused-collection window) rather than idle time alone (step 3b).
   Falsified by: a crash, a VOID condition (env/build/mode mismatch), or a witness that cannot be
   reviewed -- rerun once before drawing either conclusion in that case, not a hang finding.

   **2026-09-22 -- STEP 2 RESULT: (a) -- IT REPRODUCED ON bench8. GENERAL, NOT SHARDS-SPECIFIC.**
   `RUN.BAT` launched ~02:21:54Z; the card witness confirms bench8 exited to a DOS prompt within
   the first ~15s and sat there, unchanged, for the rest of the run (frames 2 through 166 all read
   as a sparse-white-text-on-black DOS prompt, no VOID condition, no crash). The forced wait held
   for **1267s (21m7s)** of pure passive polling -- zero keystrokes, confirmed by the code read in
   the pre-registration above -- before the first real collection attempt. **First hang: 02:53:45Z**
   (31m51s after launch: 21m7s idle + 10m44s of active collection-retry cycling on top, matching
   the corrected step-1 picture, not pure silence). **Second failure (hard stop): 03:00:52Z**, 7m07s
   later. `run-hw.sh` exit 3, no manifest, no rate -- this cell is a hang-mechanism probe, not a
   measurement. **Answer to the operator's actual question: YES, this can recur on any fast,
   unrelated fixture given enough combined idle-plus-cycling time -- not tied to Shards or 32-bit.**
   Current state, checked read-only: power normal (24,180 mW), target responsive.
   **One mechanism nuance, not glossed over:** this first hang's `verify_input_before` was
   **`true`** (not false, unlike both S2S1/S2S2 occurrences), and the guard's own recovery action
   was the lighter `reboot-chord` (not a `power-cycle`) -- and it worked on the first try
   (`verify_input_after=True`). So here the PS/2 link itself was provably still alive at the
   failure point; what failed was specifically the return-reboot's own chord landing (`_leave_net`
   in `vcctrld.py`) for three attempts running, not the whole input path. That is a **different
   sub-symptom** from S2S1/S2S2's `verify_input_before=false` (there, the link itself was down,
   needing a full power-cycle). Both surface identically from `run-hw.sh`'s side ("get-file
   refused 3x, screen=ready-prompt"), so the outer detection is right to treat them the same way,
   but they are not proven to be the SAME failure one level down -- recorded as two observed
   variants of one visible signature, not merged into a single claimed mechanism. `run-hw.sh`'s
   own one-recovery-per-run policy caught this run's SECOND failure exactly as designed regardless
   of which variant it was.
   Artifacts: `tests/harness/results/HANGTEST1-2026-09-22-STOPPED/`. **Per the stop condition:
   recovered once (the harness did this automatically), not pushing further (no step-3 mitigation
   design/validation round, which needs its own 20+ minute hardware hold) without checking in
   first, as instructed.**

   **2026-09-22 -- STEP 3.1: KEEPALIVE MITIGATION, DESIGNED (no hardware).** GO'd by the
   coordinator, one bounded round. `RUNHW_KEEPALIVE_S` (opt-in; 0/unset leaves every existing
   cell unchanged), wired into `wait_for_stable_screen()` in `run-hw.sh` -- the phase that
   currently sends nothing at all during the stretch both hangs accumulated in. Interval **300s
   (5 min)**, comfortably under the shortest observed gap to a hang (bench8's ~10m44s of active
   retry-loop cycling; Shards' ~17m). **Action:** `hw_guard.verify_input()`'s own Caps Lock
   round-trip -- the one primitive already established safe in this codebase, not a new "hope
   this is harmless" keystroke. **Gate:** fires only when `hw_guard.screen_reading()` (the same
   OCR check `run-hw.sh` already gates `guard recover` on) reads `dos-prompt` or `ready-prompt` --
   the game positively confirmed NOT running -- never trusting the frame-diff tracker's own
   "static" alone, since that cannot distinguish "the game exited" from "the game's idle screen
   hasn't moved yet" (the whole reason this wait loop exists). Lock handling: `wait_for_stable_screen`'s
   caller already holds the input lock as `run-hw-$TAG` for this entire phase, so the keepalive
   releases it, acts, and reacquires it -- the same release/act/reacquire dance
   `power_cycle_and_verify()` already uses elsewhere in `hw_guard.py`, not a new pattern; a failed
   reacquire is logged, not swallowed.
   **Validated dry, no hardware, against `mock-vcctrl` (three scenarios, extracting the same
   heredoc `run-hw.sh` runs, not a paraphrase of it):** (1) screen held at an idle prompt the
   whole time -- keepalive fires on schedule, `verify-input` returns `verified=True`, lock
   release/reacquire both clean; (2) screen held at "a running program" (no prompt) the whole
   time -- **zero** `verify-input` calls and zero lock calls, confirming the safety gate holds;
   (3) `RUNHW_KEEPALIVE_S` unset (the default for every other cell) -- zero new calls, existing
   behavior unchanged. `bash -n` and an AST parse of the embedded heredoc both clean.
   **STEP 3.2 PRE-REGISTRATION (before the hardware round).** Same fixture, same idle duration as
   HANGTEST1: `bench8`, idle scene, `DOSAGS_TAS_AUTO_EXIT_TICK=200`, `RUNHW_MIN_WAIT_S=1260` (21+
   minutes), same rung, WITH `RUNHW_KEEPALIVE_S=300` now active. Tag `HANGTEST2`. **Success:** no
   hang across the same or longer window -- collection completes (or refuses/retries normally
   without tripping the guarded recovery) with the card witness showing the keepalive's own
   Caps-Lock toggles landing (log lines `keepalive: sent ... verified=True`) roughly every 5
   minutes through the idle stretch. **Failure:** the same "get-file refused 3x, screen=ready-
   prompt" signature recurs despite the keepalive running. Either result is recorded and the
   HARDWARE.md tier is updated accordingly (established only on success; bounded, with "keepalive
   did not resolve it" stated plainly, on failure) -- this is the one hardware round for today's
   investigation, no second mitigation attempt without checking in again.

   **2026-09-22 -- STEP 3.2 RESULT: NEITHER OUTCOME -- THE GATE NEVER FIRED, A THIRD OPTION THE
   PRE-REGISTRATION DIDN'T NAME. NOT REPORTING THIS AS "MITIGATION FAILED."** Same signature
   recurred (first hang 03:42:56Z, `verify_input_before=true`, `reboot-chord` recovered it; second,
   hard stop, 03:50:04Z, 7m08s later) -- on the surface this looks like the pre-registration's
   "failure" branch. **It is not, and the difference matters:** `HANGTEST2.out` shows exactly four
   `keepalive: skipped -- screen reads 'other', not confirmed idle` lines and **zero**
   `keepalive: sent` lines. The keepalive's own safety gate never once judged the screen
   confirmed-idle, so it never fired even once in this run -- the mitigation was not tested, only
   its refusal-to-act path was.
   **Root cause, found from the existing witness frames, no new hardware:** ran `tesseract`
   directly against the saved card frames at each skip moment (00016, 00050, 00083, matching the
   four skip timestamps). All read a bare `C:\DOSAGS>` prompt (confirmed by eye) as **`U
   =NDUSAGS>`** -- consistently garbled, and critically, not matching `hw_guard.screen_reading()`'s
   anchored `dos-prompt` regex (`^[a-z]:\\...`) at all, so it falls through to `other`. Checked
   WHY the later, real hang-detection (inside `run-hw.sh`'s own `guard screen` call) correctly read
   `ready-prompt` at the same kind of moment: by then the target had been through this run's first
   recovery reboot, so the screen carried the FULL boot banner (`[PGSB] ready.` among many other
   lines) -- `ready-prompt`'s match is a forgiving anywhere-in-text substring (`\]\s*ready`), which
   tesseract gets right on a text-rich screen; `dos-prompt`'s match is a single-anchored-line regex,
   which tesseract gets wrong on a SPARSE screen (just the bare prompt, nothing else) -- exactly
   what a fast-exiting synthetic fixture like bench8 leaves behind before any reboot has happened.
   This is a **pre-existing weakness in `hw_guard.screen_reading()`** (shared, used elsewhere too),
   not something introduced by the keepalive; the mock-vcctrl dry validation could not have caught
   it, since the mock's `shot` command hands back hand-written OCR-clean text, never modelling
   tesseract's real failure modes.
   **What this round DID show:** the safety gate is conservative in exactly the intended
   direction -- faced with an ambiguous read, it never sent anything, matching "never while a game
   may be reading keys" even under a real OCR failure it hadn't been designed around. That is
   good news about the gate's failure mode, not evidence for or against the keepalive strategy
   itself.
   **Per the stop condition and the coordinator's explicit "I'll fold the final HARDWARE.md
   wording in myself once you report": not touching HARDWARE.md's tier (stays `bounded`, as
   before this round -- neither confirmed nor refuted), not launching a third hardware round on my
   own, and not treating this as "a second mitigation attempt" since it is a bug report on the
   first one's gate, not a new strategy.** Artifacts:
   `tests/harness/results/HANGTEST2-2026-09-22-STOPPED/`. A concrete, small, narrowly-scoped fix
   is available for whenever the coordinator wants another round (broaden or supplement the
   `dos-prompt` OCR pattern, e.g. accept a last line ending in `>` with a fuzzier prefix check, or
   lean on the frame-diff tracker's own `static` signal as a second, corroborating input rather
   than trusting OCR alone) -- proposed here, not yet written or tested.

   **2026-09-22 -- STEP 3 CONTINUED (coordinator GO, own authority for design+dry-validation, this
   is the last round today regardless of outcome).** Coordinator's sketch was `^[a-z]:\\` at the
   start of the last line AND ends in `>`, loosening only the middle. **Tested that sketch
   directly against the real evidence first (no hardware) and it does not fix the bug:** the
   observed garble, `"u =ndusags>"`, does not contain a colon or backslash anywhere -- tesseract's
   psm-6 misread ate the ENTIRE "C:\" prefix, not just put noise in the middle of it, confirmed
   testing every other psm mode `hw_guard.py` could plausibly use (3/4 blank, 6/7 identically
   `"u =ndusags>"`, 11/12 a different but equally prefix-free garble, 13 useless) -- the anchor
   itself was the wrong end to keep, not just too strict. **Landed on:** anchor the *trailing*
   `>` (the one glyph tesseract got right all three times) and the line's *length* (a prompt is
   short; boot-log/game-text lines are not) instead of the drive-letter prefix at all -- any last
   line, trailing whitespace/underscore stripped, ending in `>` with 2-30 characters. Implemented
   in `hw_guard.py`'s `screen_reading()`, with the full reasoning (including why it doesn't loosen
   `ftp-log`/`ready-prompt` -- both already return before this branch runs at all -- and why a
   false positive is bounded by an EXISTING property, not a new risk: a reboot-chord against a
   still-running SDL3-DOS game already fails harmlessly, its keyboard IRQ handler replaced;
   the keepalive's Caps Lock is not bound to any AGS action) written in place as a code comment,
   not just here.
   **Re-validated, not just the keepalive path:** the exact three `mock-vcctrl` scenarios from
   step 3.1 (idle -> fires; game running -> zero calls; disabled -> unchanged) all still pass
   against the fixed function; added a fourth, the mock's own `dosprompt` state (the same
   game-exited/dead-link case `guard recover` gates on) -- classifies `dos-prompt` correctly.
   **The full existing `test-hw-guard.sh` suite -- 39 tests covering every `guard recover` branch,
   not just the keepalive's own path -- still passes 39/39, 0 failed**, confirming the shared-
   function change does not regress hang-recovery detection itself. `python3 -c
   "import ast; ast.parse(...)"` clean.
   **HANGTEST3 pre-registration.** Identical to HANGTEST1/HANGTEST2: `bench8`, idle scene,
   `DOSAGS_TAS_AUTO_EXIT_TICK=200`, `RUNHW_MIN_WAIT_S=1260` (21+ minutes), `ACSETUP-OFF-NATIVE.CFG`,
   with BOTH `RUNHW_KEEPALIVE_S=300` and the OCR fix active. **Success:** no hang across the same
   or longer window, with `keepalive: sent ... verified=True` log lines actually appearing this
   time (the thing that didn't happen last round) roughly every 5 minutes through the idle stretch
   -> mitigation confirmed, HARDWARE.md tier goes to `established`, naming the mitigation.
   **Failure:** the same "get-file refused 3x, screen=ready-prompt" signature recurs DESPITE
   `keepalive: sent` lines actually appearing (i.e. the OCR fix worked, the keepalive genuinely
   ran, and the hang still happened) -> the OCR fix was not the blocker, tier stays `bounded`,
   stated plainly. **A result where the keepalive STILL never fires** (same as last round, a
   different OCR failure mode) is not a clean instance of either branch and gets reported before
   drawing either conclusion, same as this round. This is the last round on this investigation
   today regardless of outcome (four hardware rounds already: S2S1, S2S2, HANGTEST1, HANGTEST2,
   all correctly recovered, no degradation) -- report only if HANGTEST3 hits a genuinely new
   failure signature; otherwise record the result and move straight to S2Q1.

   **2026-09-22 -- HANGTEST3 RESULT: FAILURE. THE OCR FIX WORKED; THE KEEPALIVE DID NOT PREVENT
   THE HANG. INVESTIGATION CLOSED FOR TODAY BY OPERATOR DIRECTIVE, REGARDLESS OF THIS RESULT.**
   The fix is confirmed working this time: `keepalive: sent (screen='dos-prompt') verified=True
   reacquired=True` appears four times through the 21-minute idle wait (vs. zero in HANGTEST2),
   and the eventual hang-detection itself now correctly reads `screen=dos-prompt` too (was
   misread as `other` before the fix). The hang still happened anyway: first hang/recovery
   04:31:56Z (31m37s after launch, `verify_input_before=true`, `reboot-chord` recovered it,
   matching HANGTEST1/2's milder sub-symptom), second (hard stop) 04:39:04Z, 7m08s later --
   timings closely matching every prior occurrence. **Tier stays `bounded`. The keepalive +
   OCR-fix mitigation does not resolve this fault; whatever the real mechanism is, a periodic
   input-lock round-trip during the idle wait is not sufficient to prevent it.** No further
   diagnosis today, by operator directive (five hardware rounds across three runs today: S2S1,
   S2S2, HANGTEST1, HANGTEST2, HANGTEST3, all correctly recovered by the harness, no degradation
   observed, but the actual campaign KPI has waited long enough). Artifacts:
   `tests/harness/results/HANGTEST3-2026-09-22-STOPPED/`. The `RUNHW_KEEPALIVE_S` mechanism and
   the `hw_guard.py` OCR fix both stay in the tree (the fix is a strict improvement to a shared,
   previously-buggy function regardless of the mitigation's own outcome; the keepalive stays
   opt-in, off by default, available for a future round if anyone wants to pick this back up).

   **2026-09-22 -- S2Q1 PRE-REGISTRATION (before running).** Last of step 4's five catalogue
   cells. AGS Quest forced-32: 16-bit content run at 32bpp, 640x480x32 1:1 letterboxed, the
   AutoPilot demo to tick 1500. Binary `ags-0194.exe` (`binary_sha12=e8d4b76c5cd9`,
   `build_dirty=0`, the same fixed binary as every other cell today). `run-hw.sh agsquest --tag
   S2Q1 --timeout 1800 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env
   DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_TAS_AUTO_EXIT_TICK=1500 --extra-file
   tests/harness/games/trilbysnotes/ACSETUP-OFF.CFG:ACSETUP.CFG`. Expected
   `env_block_sha=bec92cf273e7` (unchanged by which binary runs it); alias expected ON (this is
   the 640-wide 1:1 rung, unlike the four 512x384 titles). **Prediction, unrevised from the
   0193/0194 restatement:** stable rate **16 (8 - 25)**, UNANCHORED (its basis, the 38.0 AGS
   Quest figure, is itself marked unexplained). Steady is the figure compared, not whole-run (the
   1500-tick window and the demo's blocking operations dominate the whole-run figure). Falsified
   by a 4x miss either way: under 4, or over 64 (which cannot happen). *VOID if:* `env_block_sha`
   differs from `bec92cf273e7`; the mode line is not `640 x 480 (32-bit)` (or equivalent);
   `binary_sha12` is not `e8d4b76c5cd9` or `build_dirty` is not 0; the tag was reused; more than
   one manifest block; an SDL trace is collected. *Stop and report if:* the alias engages on a 2x
   rung (it should not at this 1:1 rung, but this is the standing stop condition regardless), the
   target cannot be driven, or the mode changes for a reason unreadable from the log. Witness
   (card + camera, per the operator's standing order) reviewed clean, no trails, no missing
   background, before any rate is written -- same discipline as every cell today.

   **2026-09-22 -- S2Q1 RESULT: NO VOID, WITNESS CLEAN, PREDICTION MISSED HIGH (not falsified --
   the 4x bound was never crossed).** `env_block_sha=bec92cf273e7` (matches), mode line `640 x
   480 (32-bit) fullscreen desktop` (matches), alias ON y=60 (expected at this 1:1 rung, not a
   stop condition), `binary_sha12=e8d4b76c5cd9`, `build_dirty=0`, one manifest block, no SDL
   trace -- no VOID. `tick_rate_steady` **40.52**, `frames_skipped` 189 of 1499, **stable rate
   35.41** -- against the predicted 16 (8 - 25): more than double the central estimate and above
   the stated range's own ceiling, but not a falsifying 4x miss (would need under 4 or over 64).
   `presents_real` 1415, `present_update_window` mean **11.5 ms** (vs. 2.55 ms for the same
   demo's 16-bit run today, AQF1/AQF2 -- the 4 bytes/pixel content costs more per present, as
   expected, just not as much more as the old ratio predicted). **Reading:** the prediction's own
   basis was the 2026-09-16 pre-optimisation ratio (32-bit ran 0.43x of 16-bit on that build).
   Today's actual ratio is 35.41 / 37.78 (this session's 16-bit AQF figure) = **0.937x** -- 32-bit
   content now costs almost the same as 16-bit at this rung, not 43% of it. Plausible candidate,
   not claimed as proven: the present-path work since 2026-09-16 (narrowed multi-rect present,
   the alias, dirty tracking) cuts the AMOUNT of data pushed per present, which matters more the
   larger each pixel is -- so it would disproportionately help the 32-bit path specifically. This
   is recorded as a genuine model miss, not written off, and not chased further today (S2Q1's own
   prediction was explicitly UNANCHORED from the start, its basis one of the figures already
   marked unexplained). Witness: card + camera both reviewed clean -- AGS Quest splash/title,
   forest scene with speech, single character instance every frame, complete backgrounds, no
   trails; fades before the demo's own end (tick-1500 exit as configured), then the DOS prompt.
   Results: `tests/harness/results/S2Q1-2026-09-22/`. **This closes step 4's five catalogue
   cells** (S2T1, S2F1, S2M1 measured; S2S1/S2S2 unmeasured, recorded as such; S2Q1 measured).

3. **8-bit 320x240: make the alias + direct path engage on a centred 1x
   rung** (512x384x8 under UniVBE / 640x480x8 on ROM), so Trilby's gets
   what BENCH8 got from Mode 13h. Ladder today: 19.72 (640x480 centred),
   26.89 (512x384 centred), pre-alias. *Bar: Gate-1-style 40/40 on Trilby
   in play, clean build, both tick figures.*

   **2026-09-21 -- STEP 3 DESIGN READ (source only, no cell; findings and open questions, not a plan).**
   *Finding 1, the premise as written cannot be met by tuning:* `DosPortAliasTryActivate` (ali3dsw.cpp) refuses
   unless `dst.x == 0 && dst.w == win->w` -- the picture must span the FULL window width -- and `dst.w == native
   width` (1x). A 320-wide game at 512x384 or 640x480 has `dst.w` 320 against a window of 512 or 640, so the alias
   can never engage at a centred 1x rung of either; Mach64 has no 320x240 mode (Mode 13h is 320x200 only), so the
   only full-width 1x rung a 320x240 game could ever have does not exist. "Make the alias engage" therefore means
   RELAXING that condition, which is a new mechanism, not a configuration. *Finding 2, the relaxation looks
   possible in principle:* the alias wraps the window surface with an explicit pitch (`create_bitmap_userdata(...,
   win->pitch, ...)`), so a base offset of `y*pitch + x*bpp` with the same pitch gives a correctly strided
   interior; the SDL flush path already has a per-rect branch with a row-contiguous optimisation for
   `pitches_match` (SDL_dosframebuffer.c, `_dos_port_is_full_fb_rect_list`), and pushed rects are already in window
   coordinates. *Open questions to close BEFORE any patch, each a read or a DOSBox-X run:* (a) why the contiguity
   condition was written ("nothing beside them"): whether anything else assumes an aliased picture owns whole rows
   (the ags 0100 margins-already-clean logic, `full_update`, the palette-only present, shake/flip fallbacks); (b)
   that a sub-screen rect list on a bordered aliased surface flushes correctly on the direct-framebuffer path, which
   the ags 0192 verifier can check at centred 1x at both depths (it models rects, not the backend, so a backend
   copy bug needs the screen-level series as well); (c) the payoff: it removes the RAM-to-RAM present copy, 76.8 KB
   at 320x240x8 = 4.5 ms at 17.0 MB/s of a 25 ms tick, so it is worth building only if Trilby's in-play cell (step
   2) is still short of 40 after ags 0193, which step 2 measures first. Order: step 2 decides whether step 3 is
   needed. The standing gate (`gate-present.sh`) is the acceptance test for any such change, at the centred-1x
   rows in particular.

4. **16-bit (new Gate 3).** BENCH16 anim12 at 512x384x16 / 640x480x16
   centred 1x for the A/B work; then 5 Days in play for the claim. Known
   before the first cell: at 16 bpp the integer fast blit does not engage
   and the unchanged-frame skip never fires (`blit_path fast=0`,
   `presents_skipped=0` on BENCH16 under DOSBox-X), so the 8-bit chain's
   first two wins are absent and the alias (0120) plus multi-rect are the
   whole present story. *Bar: the Gate 3 definition above.* If 5 Days is
   bound by its own content the way AGS Quest was, say so with the same
   accounting and stop. Bar 2 (blocking-operation budget) needs its
   number: on AGS Quest `SaveGame` at 16-bit took **7.76 s in one tick**
   and `gem`-class room events 4-6 s each; a player-facing budget is
   needed before FULL_GAME.
5. **32-bit decision** from step 2's two cells. If Shards at 1x centred
   lands within ~2x of the 9.4 ms bus figure per full frame, 32-bit joins
   the ladder as a 1x-only profile; if still two orders slow, one
   bisection round on the 32-bit sprite blend path, then decide. *Stop:
   one round.*
6. **Sound on, at 40.** One GUS on/off ABBA on the Gate 2 fixture. GUS
   cost ~0 fps at 5 fps but 12% of tick rate; unmeasured at 25 ms/tick.
7. **ViRGE and Cirrus**, per ruling 2, after steps 3-4.

Not on the work order: the CF stall's mechanism (see below); AGS Quest
past 38.0 (pacer patch 0163 is written, defaulted off, and predicted to
move `tick_rate_steady` 41.5 -> 40.1, not fps -- run it only if a tick
overshoot blocks a claim).

## Instrumentation inventory and hazards

- **RUNMANIFEST** (patches 0038, 0041-0044, 0054, 0115): `fps_p50/p95`,
  `tick_rate`, `tick_rate_steady`, `tick_rate_window`, `frames_skipped`,
  `presents_real/skipped`, `tick_stalls[]`, `build_dirty`, `binary_sha12`,
  `env_block_sha`, `memory_min_free_kb`, `audio_vital_status`.
- **Phase brackets**, exclusive self-time since patch 0093: present
  sub-phases (`present_update_window`, `present_blit`, `fastblit_*`,
  `present_dirty_check`), `scene_construct`, `render_backbuffer` +
  `rb_sprite_time`, `render_to_screen`, `process_events_dispatch`,
  `end_of_tick`, `rep_exec_wrapper`, `script_vm`, `wait_next_frame`,
  `input_*`, and the `preloop / loop / init` split (0105-0110).
- **Stall attribution** per tick with nested loops subtracted (0141/0142);
  span measurement (0153); tail sampling 1-in-4 episodes with pixels and
  largest sprite on the skip line (0164/0166); GUI tally with a changed
  flag (`biggui`, `guitally`).
- **Standalone probes** in `tests/harness/results/`: bandwidth
  (`bwprobe`), clock, instrumentation overhead, filesystem (`fsprobe`),
  `INT 13h` hook (`int13p`). `gate3-bars.py` computes bars from logs.
- **Standing correctness gate for anything that touches GUI invalidation
  (ags 0167/0169/0190/0191) or the present rect:** the BENCH8 AND BENCH16
  `gui` arms must equal their baseline capture hashes, alongside the AGS Quest
  harness. The AGS Quest gate alone is BLIND to this class: it passed all phases
  and all three hashes with ags 0169 stage 1 ON while the `gui` arm failed at
  both depths (2026-09-21, `EXPORT1-2026-09-21`), because none of its three
  capture moments follows a GUI being hidden.
- **What the campaign instrumentation costs while compiled in, and when it
  should go (proposed; none is scheduled).** Bare patch numbers are ambiguous:
  ags and SDL number independently and share values. Measured basis is only
  `uclock()` = 4.9 us per call and one bracket = 11.4 us on the target (overhead
  probe, 2026-09-16); the counts below multiply that, they are not separate
  measurements of this binary. ags 0139: one `debug_script_log` line per
  fade-in, and three `uclock()` per 8-bit palette step (about 15 us x 64 steps
  per fade); remove or gate once the ags 0185 8-bit fade counters have been read
  in step 2. ags 0140: on every tick a snapshot of five phase totals when a stall
  scope opens, a depth counter, a parts-sum check when it closes, and an
  unconditional 12-variable snapshot per `dos_run_tick_fixed` call -- loads and
  stores, no clock read beyond the existing scope's pair, so expected below one
  bracket per tick and unmeasured; the `stallwhat` and `skipframe` lines are
  stdout writes on stall ticks and every 4th skipped frame; gate behind an
  environment switch once the tail attribution is closed. ags 0150: two
  `uclock()` per `process_event` (about 11 us), two more per interaction run, and
  two per call of the script API entry points it wraps (`File.Open`,
  `WriteRawLine`, `Close`, `Object.SetView/Animate/SetVisible`, `SaveScreenShot`).
  These sit in entry points a game can call many times a frame, so they tax any
  real game by about 11 us per call; remove once the AfterFadein / room-transition
  attribution is closed (the record put that cost in the fixture's own script), or
  gate. SDL 0177: counters and one threshold compare per flush on the LFB path
  this port takes, but about eight `uclock()` (about 40 us) per BANKED flush,
  which Cirrus will run; its `dos_port_dbg_log` lines are silent while the trace
  is off (SDL 0189), the banked `flushtrace` `SDL_Log` fires only over 100 ms;
  remove or gate once HARDWARE.md row 59's one-variable test is answered and
  before any Cirrus/banked measurement is quoted.
- **Hazards:** the instrument contaminated gate figures twice (an `fsync`
  in the present flush, ~220 ms per hit, off by default since 0189; a
  ms/us unit bug that logged script time 1000x small, fixed by 0098).
  Inclusive brackets double-count nested ticks -- use the exclusive ones.
  DOSBox-X predicts pixel accounting to 0.3 points and rates not at all
  (18% there was 100x on hardware). `TZ` must be set or DJGPP's clock
  reads cost ~42 ms (patch 0097).
- **Gaps:** no per-frame timeline export (aggregates + `persec` rows +
  sampled tail only); no sampling profiler (gprof records zero samples on
  DJGPP, patch 0082 header); no live bytes-pushed counter (the 27.5 MB/s
  is an external probe); `fps_p50` is sampled once per wall-clock second
  over the whole run with no warm-up or transition exclusion; no 32-bit
  cell on the current binary and no BENCH32 (`build.sh --depth 32` exists,
  never run); no sound-on cell at 40; no real-game in-play fixture
  (catalogue titles have no AutoPilot -- drive them with vcctrl input).
  The recurring ~250 ms present stall on Mode 13h was isolated by
  `SDL_HINT_DOS_FLIP_INSTR=1` (FPT1) to the fast path's `post` sub-phase
  (241.7 ms against 22-37 normal); it went away with the SDL trace off
  (0189), which is the fsync, so treat it as closed unless it returns on
  a clean build.

## The storage stall: closed as bounded and mitigated

Established: every event is one single-sector `INT 13h` write blocking
205-219 ms inside a single call (a wait); the same seven CHS addresses
stall across independent runs; 14 and 11 events on CF against 0 and 0 on
a RAM disk. Not named: remap vs worn erase block vs controller retry, which
are indistinguishable from above `INT 13h`. Mitigation for every port:
buffer in memory, write outside the timed region; `DOS_PORT_LOG=0` is the
default. The hub's `HARDWARE.md` row carries the tiers; `PLAN-LOG.md`
2026-09-19..21 carries the full record including the withdrawn claims.
Half-built pieces left in `tests/harness/results/`: the read test never
ran (`INT13P_READ` did not reach the program, cause unknown), the
neighbourhood map is designed and NOT approved, the hook alters PF/AF.
None of it is scheduled.

## Pre-existing agsquest-alias-y60 flicker: confirmed alias-unrelated, decoupled from patch 0196

**2026-09-22.** While gating ags patch 0196 (the pillarboxed-alias fix, step 3), the standing
`agsquest-alias-y60` DOSBox-X row (x=0, y=60 -- unchanged by 0196) started failing intermittently:
clean across 20 independent freeze-tick samples on the pre-patch binary (ags-0195, two full runs),
but 4 of 20 samples differed on the patched binary (ags-0196, two full runs) -- small (32-1074px),
scattered pixel differences concentrated around the treehouse room's chandelier/candle-flame
sprites, a DIFFERENT tick failing each run (never repeating), and, cross-checked directly against
saved frames from both binaries at the same tick, the difference landed in either the default-
present capture or the full-push capture unpredictably -- not consistently one or the other.
Verified from source (both independently and by the coordinator) that patch 0196 is algebraically
inert for this row's own geometry (dst.x=0 takes an identical path through both the old and the new
bounds check), and that `DOSAGS_DIRTY_PRESENT=0` (the row's own "B" reference capture) does not
disable the alias -- it only gates a later, separate narrowing step -- so both captures already run
through the same alias code regardless of which binary is used.
**The one decisive check:** re-ran the row with `DOSAGS_DIRECT_VSCREEN=0` (the existing hint that
disables the alias mechanism ENTIRELY, unrelated to `DOSAGS_DIRTY_PRESENT`) on the patched binary.
**The exact same flicker still occurred** -- 3 of 10 pairs, the identical ticks and identical bboxes
as the patched binary's very first (alias-ON) run. **This conclusively decouples the flicker from
the alias mechanism, and therefore from patch 0196**: it reproduces with the alias fully off, in
code this patch never touches. Cause not confirmed -- candidate is a pre-existing, low-rate,
run-to-run rendering nondeterminism (an uninitialized-buffer read is the leading guess, given the
signature: sparse, scattered differences in a bright/detailed sprite region, never the same tick
twice) that the patch's own changed code layout/timing merely happened to perturb into a visible
rate on this particular day's testing, rather than something 0196 introduced. **Not chased further,
per the coordinator's bound** (one check, one report). Not a reason to hold patch 0196; the
pillarbox rows (0196's own actual target) passed cleanly and are unaffected by this question. If
this recurs on an unrelated cell in the future, this note is the prior art -- start from "alias-
unrelated, confirmed" rather than re-deriving it.

## Step 3: Trilby's Notes in play at the pillarboxed centred-1x rung (ags patch 0196)

**2026-09-22 -- PRE-REGISTRATION, cell S2T2. NOT YET RUN.** Same fixture, rung and config as S2T1
(Trilby's Notes in play, room 3, 512x384x8 centred), on the FIXED binary now carrying patch 0196
(`build/abba/ags-0196.exe`), witness-clean DOSBox-X gate already passed for this exact geometry
(`bench8-alias-512x384-idle`/`-anim12`, both `screen-equal: 5 pair(s), 0 problems`, x=96 y=92 --
one axis off from Trilby's own x=96 y=72, same mechanism, same code path). Fresh tag `S2T2`.

**Command (unchanged from S2T1 except the binary):** `AGS_EXE=build/abba/ags-0196.exe run-hw.sh
trilbysnotes --tag S2T2 --timeout 1800 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env
DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 3 --extra-file
tests/harness/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG`, with
`tests/harness/drive-walk.sh S2T2 25 2 80` running alongside -- **the driver fix**: S2T1 used the
default `PERIOD_S=8`, which produced `presents_real` 180 of 4968 renders (3.6%), far under the
30% in-play bar -- most of each 8s window was the character standing still between short walk
hops, not moving. `PERIOD_S=2` (a new click roughly every 2s, well under a typical short walk
hop's own duration) keeps a new destination queued before the previous one finishes, aiming to
keep the character in near-continuous motion for most of the run; `MAX_CLICKS=80` covers the
full ~115s driven span (WARMUP_S 25s + up to 160s of clicking, comfortably past the ~141s S2T1
itself took wall-clock for the same 5000-tick window).

**Predictions, two separate questions:**
1. *Tick figures, revised upward from S2T1's own prediction now that the alias engages here for
   the first time* (previously S2T1 met/exceeded its own no-alias prediction already, 39.91
   against a predicted 34/25-40; the alias should cut present cost further, the same shape as
   every other aliased cell today). **`tick_rate_steady` >= 39.9** (was >= 39), stable rate
   **38 (34 - 40.5)**. Mode line unchanged (`512 x 384 (8-bit) fullscreen`); **alias line now
   expected `vscreen alias ON x=96 y=72 320x240 pitch=512`** (S2T1 had none). Falsified by a
   stable rate under 9.5 or the alias failing to engage at all (which would itself be the more
   important finding, and stops the cell for a source-level look, not just a missed number).
2. *In-play witness, the actual question this cell exists to answer.* **`presents_real` >= 30%
   of render passes** (S2T1's own falsification rule, unchanged) -- no point prediction stated
   for the exact fraction beyond "clears 30%", since click-to-walk-duration on real hardware
   has not been measured directly; report the achieved fraction plainly either way. If still
   under 30% with the fixed driver, that is a finding about walk-cycle duration vs. a 2s period,
   not evidence against the patch (the tick figures answer that question independently) -- widen
   the gap further (a faster still period, or queuing two clicks per interval) before concluding
   the fixture itself cannot produce a real in-play number this way.
**VOID if:** `env_block_sha` differs from S2T1's own `459dcb815359`; mode line differs from
above; `binary_sha12` is not `340fa8167624` (`make build-dirty`, confirmed fresh just now) or
`build_dirty` is not 0; the tag was reused; more than one manifest block; an SDL trace collected;
the run did not reach room 3. **Stop and report if:** the alias engages on a 2x rung (should not happen here, standing
condition regardless), the target cannot be driven, or the picture is incomplete on either
witness. Witness (card + camera, operator's standing order) reviewed clean before any rate is
written, same discipline as every cell today.

**2026-09-22 -- S2T2 RESULT: BOTH PREDICTIONS MET, IN-PLAY DECISIVELY.** No VOID:
`env_block_sha=459dcb815359` (matches), mode line `512 x 384 (8-bit) fullscreen` (matches),
`binary_sha12=340fa8167624`, `build_dirty=0`, room 3 confirmed, one manifest block, no SDL trace.
**The alias engages** -- `DOS-PORT vscreen alias ON x=96 y=72 320x240 pitch=512`, exactly the
predicted line, confirming patch 0196 works on real hardware, not just in the DOSBox-X gate.
1. *Tick figures:* `tick_rate_steady` **39.99** (predicted >= 39.9 -- met), stable rate **39.91**
   (predicted 38, 34-40.5 -- met, essentially at the ceiling). `present_update_window` mean
   **0.95 ms** (S2T1, no alias, same fixture: 11.5ms-scale present costs were never reported for
   S2T1 specifically since it wasn't aliased, but this is in the same cheap range as every other
   aliased cell today).
2. *In-play witness, the actual question:* `render_passes` **4990**, `presents_real` **5003** --
   essentially every render pass was a real content change (the small excess over render_passes
   is a minor accounting overlap, not a defect). **This clears the 30% bar by more than 3x over,
   not marginally** -- S2T1's 3.6% is not comparable to a fixture that could not produce a real
   in-play number; this one produces an overwhelming one. The driver fix (`PERIOD_S=2` instead of
   8) is confirmed as the actual lever: same game, same room, same rung, only the click cadence
   changed.
Witness: card doesn't see 512x384 (as every prior cell at this rung); camera shows the character
changing position across samples (unlike S2T1's near-stationary appearance), complete background
every frame, no trails, single character instance every frame; reviewed clean. Results:
`tests/harness/results/S2T2-2026-09-22/`. **Step 3's bar (Gate-1-style 40/40 on Trilby in play,
clean build, both tick figures) is met**, and the underlying question S2T1 could not answer
(does this fixture produce a real in-play number once the alias engages) is now answered: yes.

**2026-09-22 -- STEP 3 CLOSED (coordinator's call).** Scope was exactly "make the 8-bit 320x240
alias + direct path engage on a centred 1x rung, so Trilby's gets what BENCH8 got from Mode 13h";
S2T2 met it cleanly, not marginally. Deliberately NOT extended today to the other 320-wide
catalogue titles the same patch also applies to (5 Days a Stranger, Maniac Mansion Deluxe, Shards
of God all land on the identical pillarboxed geometry at this rung) -- that is new scope beyond
what step 3 asked for, left for a future step rather than assumed. Patch 0196 stays landed
(vendor/ags commit, exported to `patches/ags/0196-*`, DOSBox-X-gated, hardware-validated) whether
or not that generalization is ever picked up. Not starting step 5 or the generalization without
the coordinator's dispatch.

## Generalizing patch 0196 to the remaining 320-wide catalogue titles (operator GO, 2026-09-22)

Scope: 5 Days a Stranger (16-bit, the re-homed Gate 3 target -- closes it if it hits 40/40),
Maniac Mansion Deluxe (16-bit), Shards of God (32-bit), in that order. Same discipline as step 3:
a DOSBox-X correctness gate first, checked (not assumed) against each title's own geometry/depth,
then real-hardware in-play validation with a per-title cadence check, not S2T1's blind 8s reused
blind. **Source-grounded coverage read, done before any new DOSBox-X cell:** confirmed native
geometry from today's own logs/manifests -- 5 Days 320x240/16bpp, render dest "(96, 72, 415, 311 :
320 x 240)" (x=96 y=72, same pairing as Trilby's own S2T2, different depth); Maniac Mansion
320x200/16bpp (x=96 y=92, same pairing as BENCH8); Shards 320x200/32bpp (x=96 y=92, `manifest.yaml`
`color_depth: 32`, its own native, not forced). 0196's existing gate proves the x,y PLACEMENT math
at 8bpp (bench8, twice, plus real hardware) and proves 16bpp only with `dst.x == 0`
(agsquest-alias-y60) -- the patch's one new arithmetic term, `dst.x * bytes_per_pixel`
(`ali3dsw.cpp:280`), has never been exercised with a NONZERO product, at any depth, and never at
32bpp at all (confirmed: no 32-bit AGS binary exists anywhere under `build/`). Not assumed
covered by extension -- treated as three separate open questions.

**Coverage plan, extended into `gate-alias.sh` (`--no-bench16`/`--no-catalogue`/`--catalogue`
flags added, `--out`/`--arms`/`--no-aq`/`--no-control`/`--no-pillarbox` unchanged):**
- Maniac Mansion Deluxe: `bench16-alias-512x384-{idle,anim12}` -- BENCH16 (same source as BENCH8,
  only `ColorDepth` differs) is an exact geometry match at 320x200/16bpp, reusing the pillarbox
  rows' own pattern verbatim.
- 5 Days a Stranger: `5days-alias-512x384` -- no synthetic fixture matches 320x240/16bpp, so this
  runs the real game itself through the same tick-freeze A/B the standing `agsquest-alias-y60`
  row already uses on real content, at its own title-idle state (5 ticks, 100-900,
  `DOSAGS_TAS_AUTO_EXIT_TICK=1000`, matching today's S2F1 hardware cell's own window).
- Shards of God: `shards-alias-512x384` -- same freeze-capture technique, real game, its own
  title-idle state, same tick window. **The first exercise of this patch at 32bpp anywhere** --
  treated with the same weight as a new correctness question, not a formality.

**2026-09-22 -- PRE-REGISTRATION, 5 Days a Stranger's gate cell (`5days-alias-512x384`). NOT YET
RUN.** Binary `build/abba/ags-0196.exe` (`binary_sha12=340fa8167624`, `build_dirty=0`).
`ACSETUP.CFG` staged from the same generic pillarbox cfg every title today has used
(`tests/harness/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG`). Freeze ticks
100,300,500,700,900 within the title-idle window (`DOSAGS_TAS_AUTO_EXIT_TICK=1000`), A (default
present) vs B (`DOSAGS_DIRTY_PRESENT=0`, full push -- note per the flicker investigation this is
NOT alias-free, just unnarrowed) vs C (`DOSAGS_BREAK_0193=1` control). **Prediction: A == B pixel
for pixel at all 5 freezes** (screen-equal.py, `--min 5`), mode line `512 x 384 (16-bit)
fullscreen`, alias line `DOS-PORT vscreen alias ON x=96 y=72 320x240 pitch=1024` (16bpp: pitch
doubles from 8bpp's 512 at the same 512-wide window). **Falsified by any A-vs-B mismatch** -- a
real defect at this specific new combination, not a modelling miss, so any failure here means
stop and report, not retune-and-rerun. Control (C) expected to fail against B, same as every
other row -- if it does not, the gate has no demonstrated power on this row specifically.

**2026-09-22 -- 5 DAYS A STRANGER GATE RESULT: PASS.** `screen-equal: 5 pair(s) compared, 0
problem(s)`, control fails against B as required (gate has demonstrated power on this row).
Alias line confirmed directly (a one-off verify run, same binary/cfg): `DOS-PORT vscreen alias ON
x=96 y=72 320x240 pitch=1024` -- the exact predicted line, pitch correctly doubled from 8bpp's
512 to 16bpp's 1024. This closes the {nonzero x-offset, 16bpp} coverage gap for 5 Days's own
geometry. Next: BENCH16 (Maniac Mansion Deluxe's stand-in), then Shards of God. Real-hardware
in-play validation for 5 Days follows once all three titles' DOSBox-X gates are through, per the
coordinator's stated order (source reads/gates first, hardware after).

**2026-09-22 -- BENCH16 GATE RESULT (Maniac Mansion Deluxe's stand-in): PASS, both arms.**
`bench16-alias-512x384-idle` and `-anim12`: `screen-equal: 5 pair(s) compared, 0 problem(s)`
each, controls fail as required (2 of 2). Alias line confirmed directly: `DOS-PORT vscreen alias
ON x=96 y=92 320x200 pitch=1024` -- the exact predicted line (same x,y as BENCH8's own pillarbox
rows, pitch doubled to 1024 for 16bpp). Closes the {nonzero x-offset, 16bpp} coverage gap at
Maniac Mansion Deluxe's own exact geometry (BENCH16 is byte-for-byte the same source at the same
native size, only `ColorDepth` differs). Next: Shards of God, 32bpp -- the first exercise of this
patch at that depth anywhere.

**2026-09-22 -- SHARDS OF GOD GATE RESULT (32bpp, the first exercise of this patch at that depth
anywhere): FAIL on screen-equal, then decoupled from patch 0196 by the same decisive check the
`agsquest-alias-y60` flicker note above already established as prior art -- read that note first,
not re-derived here.** `shards-alias-512x384`: `screen-equal: 5 pair(s) compared, 1 problem(s)`,
control fails against B as required (gate has demonstrated power on this row):
```
FRZ00  tick 100    DIFFERS: 120672 px, bbox (512, 513, 1152, 913)
FRZ01  tick 300    equal
FRZ02  tick 500    equal
FRZ03  tick 700    equal
FRZ04  tick 900    equal
```
Max per-channel delta across those 120,672px: 9 (of 255), mean ~6.6 -- a subtle whole-frame
difference (consistent with a title-screen fade-in/starfield-twinkle effect), not a structural or
positional one; distinct signature from the flicker note's sparse/scattered sprite-region diffs,
but the same underlying category (pre-existing rendering nondeterminism, not this patch).

**The one decisive check, same pattern as the flicker note:** re-ran the row with
`DOSAGS_DIRECT_VSCREEN=0` (alias fully disabled) on the same binary, same ticks. **The exact same
divergence reproduced** -- identical pixel count (120,672px) and identical bbox
`(512, 513, 1152, 913)` at tick 100, ticks 300-900 equal. This conclusively decouples the
divergence from the alias mechanism, and therefore from patch 0196: it reproduces with the alias
fully off, in code this patch never touches. Not a defect in the fix.

**Attempted a clean-tick rerun to close 32bpp coverage outright (tick 100 -> 200, ticks 300-900
unchanged) instead of just documenting decoupling.** Result: `screen-equal: 5 pair(s) compared, 0
problem(s)` -- clean. **But the control (`DOSAGS_BREAK_0193=1`) also stopped differing from B on
this tick set** (`gate-alias: NO control failed anywhere: the check has no demonstrated power`,
exit 3). Checked against the ORIGINAL run's own `C-vs-B.txt`: the control's one demonstrated
difference on this row was ALSO only at tick 100 (`DIFFERS: 255624 px`, same bbox, larger
magnitude than A-vs-B's own difference there) -- ticks 300-900 were already `equal` for the
control too. So this title screen's only tick where anything distinguishes A, B, and C from each
other is tick 100: after that, the picture has settled into a state where full-push, narrowed-
present, and the broken-0193 control all converge to the same bytes. **Swapping the tick set does
not close coverage "for free" -- it trades a real-but-decoupled FAIL for a clean-but-blind PASS
that no longer proves this row can catch a real regression.** Not adopted: `gate-alias.sh` reverted
to the original `CAT_TICKS[shards]=100,300,500,700,900`; the standing row's result stays the FAIL
recorded above, decoupled from 0196 by the alias-disabled check, same as the flicker note's own
resolution. Not chased further with additional candidate ticks -- one attempt, one report, per the
same bound the flicker note used; a control-blind gate is a worse outcome than a documented,
decoupled FAIL.

**32bpp coverage conclusion:** the {nonzero x-offset, 32bpp} placement math is exercised and
correct at every tick where the underlying content is itself stable (300, 500, 700, 900) --
4 of 5 freezes, unanimous. The one tick that differs (100) differs identically with the alias on,
the alias off, and (per the original run) even for the unrelated 0193 control, so it is a title-
screen content question, not a placement-math or an alias question, at any depth. This closes the
32bpp open question from the coverage read above on the same standard as 5 Days and Maniac Mansion
Deluxe, without asserting a clean PASS the row cannot actually support. Patch 0196's generalization
across all three catalogue titles (16bpp x2, 32bpp x1) is DOSBox-X-gated. Real-hardware in-play
validation is next, per the coordinator's stated order (source reads/gates first, hardware after),
starting with 5 Days a Stranger since it can close Gate 3.

**2026-09-22 -- room search for 5 Days a Stranger's in-play cell, done entirely in local
DOSBox-X before any real-hardware time (coordinator's call, citing the 5-hardware-round hang
investigation earlier today and dos-emulator-workflow's own local-first rule).** Unlike Trilby's
Notes, 5 Days a Stranger had no proven `--startr` room; natural boot was checked first and found
to auto-play a ~90s narrated intro (dynamic content, no input needed) landing on a Start/Load/Quit
button menu -- a real "wrong click" risk (Quit adjacent to Start) blind relative-mouse wandering
does not have on a simple walkable room. `run-dosbox.sh` turned out to already carry the
passthrough needed to test `--startr` locally, as an undocumented `AGS_EXTRA_ARGS` env var; surfaced
properly as a reusable `--ags-arg` flag matching `run-hw.sh`'s own interface (commit `a538474`,
verified with the new flag itself, not just the old var). Tested rooms 1-4 with the ags-0196 binary,
confirmed by BOTH a screenshot and the engine's own `STDOUT.TXT` line (not visual inspection alone):
rooms 1-2 are the same intro cutscene content as natural boot (`Loading room 1`/`2`, car scene /
manor exterior); **room 3 is a real interior room** (office/study, player alone, no dialogue
overlay, stable across ticks 20 and 60, `Loading room 3` / `Game : (room:3) Mouse bounds constrained
to (0,0)-(319,199)`, no errors beyond the same benign boilerplate every run already has); room 4 is
also real (a hallway with an NPC and a visible interaction cursor) but was not chosen, to avoid an
NPC potentially catching a wandering click into an unplanned dialogue during automated driving.
**Room 3 selected** (coordinator's call) -- `--ags-arg --startr --ags-arg 3` bypasses both the
menu-click risk and the ~90s intro entirely, same shape as Trilby's own `--startr 3`.

## Step 4: 5 Days a Stranger in play at the pillarboxed centred-1x rung (ags patch 0196, closes
Gate 3 if it hits band)

**2026-09-22 -- PRE-REGISTRATION, cell S2F2. NOT YET RUN.** Binary `build/abba/ags-0196.exe`
(`binary_sha12=340fa8167624`, `build_dirty=0`, unchanged since today's DOSBox-X gate -- same file,
same mtime, re-verified just now). Config: the same generic pillarbox cfg every catalogue title
today has used (`tests/harness/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG` ->
`ACSETUP.CFG`), the exact geometry the DOSBox-X gate (`5days-alias-512x384`, PASS) already proved
correct for this binary.

**Command, same shape as S2T2 (Trilby's own in-play cell) with the room search above substituted
for Trilby's already-known room 3:** `AGS_EXE=build/abba/ags-0196.exe run-hw.sh 5days --tag S2F2
--timeout 1800 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=5000
--ags-arg --startr --ags-arg 3 --extra-file
tests/harness/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG`, with
`tests/harness/drive-walk.sh S2F2 25 2 90` running alongside -- `PERIOD_S=2` from the start (not
S2T1's originally-too-sparse 8s default), applying the lesson S2T2 already paid for on Trilby's own
cell rather than re-discovering it here; `MAX_CLICKS=90` covers a generous margin over the
~115-140s a 5000-tick window is expected to take at a near-ceiling rate (S2T2's own comparable
window took ~141s wall-clock with `MAX_CLICKS=80`).

**Predictions, two separate questions, modelled on S2T2's own reasoning (5 Days's own S2F1 already
met its no-alias bar at 39.999, essentially the ceiling; the alias should only cut present cost
further, same shape as every other aliased cell today):**
1. *Tick figures.* **`tick_rate_steady` >= 39.9**, stable rate **38 (34 - 40.5)**. Mode line
   unchanged from S2F1 (`512 x 384 (16-bit) fullscreen`); **alias line now expected `DOS-PORT
   vscreen alias ON x=96 y=72 320x240 pitch=1024`** (S2F1 had none -- pre-0196 binary). Expected
   `env_block_sha=459dcb815359` -- computed from the allowlist's own actual inputs (patch 0077):
   only `DOSAGS_FIXED_TIMESTEP` (set, via run-hw.sh's default) and `DOSAGS_TAS_AUTO_EXIT_TICK`
   (set, =5000) are both allowlisted AND set here; `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER` and the
   `--ags-arg` room jump are NOT allowlisted, so neither changes the hash -- same two allowlisted
   vars, same values, as S2T1/S2T2, hence the same predicted hash. Falsified by a stable rate under
   9.5 or the alias failing to engage at all (which would itself be the more important finding).
2. *In-play witness, the actual question this cell exists to answer.* **`presents_real` >= 30% of
   render passes** (the standing bar, unchanged) -- no point prediction beyond "clears 30%" since
   room 3's own walk-cycle/click-response timing on real hardware has never been measured (a fresh
   room, unlike Trilby's already-characterised forest room); report the achieved fraction plainly
   either way.

**VOID if:** `env_block_sha` differs from `459dcb815359`; mode line differs from `512 x 384
(16-bit) fullscreen`; `binary_sha12` is not `340fa8167624` or `build_dirty` is not 0; the tag was
reused; more than one manifest block; an SDL trace collected; the run did not reach room 3 (checked
directly against the log's own `(room:3)` line, the same check S2T1 used for Trilby's room 3).
**Stop and report if:** the alias engages on a 2x rung (should not happen, standing condition
regardless), the target cannot be driven, or the picture is incomplete on either witness. Witness
(card + camera, operator's standing order) reviewed clean before any rate is written, same
discipline as every cell today. **This cell can close Gate 3** if both tick figures land in the
39.2-40.8 band and completeness clears 95% -- the Gate 3 definition's own bar, stated in full above
under "Gates."

**2026-09-22 -- S2F2 RAN, exit_code=0, no VOID condition -- RAW FIGURES ON FILE, HELD, NOT
CLAIMED.** First launch attempt (07:54) crashed on a bad `--extra-file` path (my own bug, cwd
mismatch -- fixed, see `a538474`/commit history); this is the corrected relaunch (07:58:29).
`env_block_sha=459dcb815359` (matches), mode line `512 x 384 (16-bit) fullscreen` (matches),
`binary_sha12=340fa8167624`, `build_dirty=0` (both match), alias confirmed: `DOS-PORT vscreen
alias ON x=96 y=72 320x240 pitch=1024` (matches predicted exactly), `Now in room 3` confirmed.
Raw figures (`tests/harness/results/S2F2-2026-09-22/RUNMANI.LOG`): `tick_rate_steady=39.97`
(ticks=4999, stall_ticks=2), whole-run `tick_rate=39.26` (`frames_skipped=62`), stable rate
`39.97 x (1 - 62/4999)` = **39.47**, `fps_p50=40.00`, `fps_p95=40.12`, `render_passes=4938`,
`presents_real=4950`, `presents_skipped=0` (the small excess over render_passes is the same minor
accounting overlap S2T2 noted, not a defect), `critical_count=0`, `warn_count=0`, `duration_s=141`.
drive-walk: 71 clicks, lock released naturally when the run finished (not from hitting the
90-click cap -- the whole run was actively driven). **These figures are NOT recorded as a valid
Gate-3 result and must not be quoted as one** -- held per the duplicate-character finding below
until that is understood, per the coordinator's stop-and-report instruction. Both tick figures, if
they were to be accepted, would meet the pre-registration's own band and bar, which is exactly why
this hold matters: a passing number is not evidence the cell is trustworthy.

**2026-09-22 -- PRE-REGISTRATION, cell S2F3 (exact real-hardware replication of S2F2, operator's
pick: same binary, config and command). NOT YET RUN.** S2F2's hold is resolved: the room-3 second
figure is the `--startr 3` artifact (DUPCHAR4), and the coordinator reviewed S2F2's camera sheet in
full (frames 5-16 one walking figure; the doubled look in 5 and 13 is translucent camera blur).
**Binary:** `build/abba/ags-0196.exe` (NOT 0197), expected `binary_sha12=340fa8167624`,
`build_dirty=0`. **Command** (run from `tests/harness/`, both paths absolute -- the corrected form
of S2F2's relaunch, not the 07:54 one that crashed on a cwd-relative `--extra-file`):
`AGS_EXE=$REPO/build/abba/ags-0196.exe ./run-hw.sh 5days --tag S2F3 --timeout 1800 --env
SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 3
--extra-file $REPO/tests/harness/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG`,
with `./drive-walk.sh S2F3 25 2 90` launched alongside, just before it, as S2F2 did. Default
`RUNHW_POLL_S` (8 s), as S2F2. **Expected identity:** `env_block_sha=459dcb815359`; mode line
`512 x 384 (16-bit) fullscreen`; `DOS-PORT vscreen alias ON x=96 y=72 320x240 pitch=1024`;
`Now in room 3`. **Predictions:** `tick_rate_steady` and whole-run `tick_rate` both in 39.2 - 40.8;
completeness (`presents_real / render_passes`) >= 95%; `fps_p50` >= 40. S2F2 reference: steady
39.97, whole-run 39.26, stable 39.47. **Witness:** the room-3 opening WILL show two figures ~7-9 s
after room entry (the known `--startr` artifact, DUPCHAR4) -- expected, NOT a witness failure. Any
OTHER anomaly (trails, stale sprites, torn or incomplete picture) is stop-and-report. **VOID if:**
`env_block_sha` differs; mode line differs; `binary_sha12` is not `340fa8167624` or `build_dirty` is
not 0; the tag was reused; more than one manifest block; an SDL trace collected; `Now in room 3` not
reached. **Stop if:** any VOID, the target cannot be driven, picture incomplete, or an anomaly beyond
the known two-figure beat -- report, no rerun without asking. One cell only. The result is written
as "RESULT, pending coordinator verification"; the Gate 3 claim decision is the coordinator's.

**2026-09-22 -- S2F3 RESULT, pending coordinator verification (NOT a claim).** Ran 11:54-12:04
PDT, exit_code=0, `***** ENGINE HAS SHUTDOWN`, no VOID condition: `binary_sha12=340fa8167624`,
`build_dirty=0`, `env_block_sha=459dcb815359` (all match), mode line `512 x 384 (16-bit)
fullscreen`, `DOS-PORT vscreen alias ON x=96 y=72 320x240 pitch=1024`, `Now in room 3`; one manifest
block, no SDL trace, tag unused before (checked results/ and PLAN-LOG.md). Collection reboots
witnessed (2/2), no post-collection hang. drive-walk: 71 clicks, stopped when run-hw released the
lock (same count as S2F2). Raw (`tests/harness/results/S2F3-2026-09-22/RUNMANI.LOG`):
`tick_rate_steady=39.95` (ticks=4999, stall_ticks=2), whole-run `tick_rate=39.24`,
`frames_skipped=61`, stable rate `39.95 x (1 - 61/4999)` = **39.46**, `fps_p50=40.00`,
`fps_p95=40.12`, `render_passes=4939`, `presents_real=4951` (100.2%, the same small accounting
overlap as S2F2), `presents_skipped=0`, `critical_count=0`, `warn_count=0`, `duration_s=142`.
Against S2F2 (steady 39.97 / whole-run 39.26 / stable 39.47): -0.02 / -0.02 / -0.01. Both tick
figures in 39.2 - 40.8; whole-run margin over the floor is **0.04** (S2F2: 0.06).
**Witness (reviewed frame by frame, camera 00001-00025 at ~9 s):** 00001 DOS prompt/RUN.BAT;
00002 blank mode switch; **00003_115725.378 the known two-figure beat** (Object 0 at the window/
bookshelf + cTrb at the desk, the `--startr` artifact, DUPCHAR4), with the hourglass wait cursor;
00004 one figure at the bookshelf; 00005-00016 one figure throughout, walking (00005, 00007, 00013)
or standing, complete picture, no trails, no stale sprites, no tearing visible; 00017 blank exit
mode switch; 00018-00025 DOS prompt. Capture card black from frame 2 on (does not see 512x384 --
same as S2F2, whose card frames read mean 0 at the same indices); the camera is the physical
witness. No anomaly beyond the pre-stated two-figure beat.

## CLOSED 2026-09-22 -- `--startr` artifact, not a port defect: duplicate player-character sprite during room 3's opening animation (S2F2)

**Closed by DUPCHAR4 (below):** the second figure is the player left at his authored default
position (160,160) by the `--startr 3` debug jump; natural entry parks him at (15,194), where he is
not visible, and shows one figure. Patch 0197 stands as a separate, real fix (its Object flush fires
on Object 0's turn-off); it was never the cause of this sighting. The original text follows,
unchanged.

**2026-09-22.** During the S2F2 real-hardware cell (5 Days a Stranger, room 3 via `--startr 3`,
512x384 pillarboxed, alias engaged), the operator watched the physical screen directly and
reported two identical player-character sprites on screen simultaneously during room 3's opening
animation (a "Day One" title card followed by a window-entry sequence) -- one in profile near the
bookshelf/cabinet, one facing forward near the desk -- and confirmed against a reference
playthrough that only one character should ever be visible at that moment. This is a real
gameplay-visible defect, independent of the fps/Gate-3 question, and is recorded here on its own
regardless of what happens to that hold.

**Confirmed (not hypothesis):**
- The physical-screen witness camera caught it directly: `tests/harness/results/S2F2-2026-09-22/
  witness/camera/00003_080144.057.jpg` shows both sprites; frame 00002 (9s earlier) is a blank
  mode-transition; frame 00004 (9s later) shows only one character. So the duplicate is real and
  transient, resolved within roughly 9-18s of room entry -- both the coordinator and I read the
  raw frame directly, independently, same conclusion.
- The engine's own log (`STDOUT.TXT`) shows the mechanism this coincides with: `Game : (room:3)
  Object 0 set to view 14` then `Obj 0 start anim view 14 loop 0, speed 3, repeat 0, frame 0` --
  a room OBJECT (not the player Character) is given an animated view around engine tick 1-7, which
  is the room's own window-entry animation. A large stall is logged at the same point (`DOS-PORT
  stallwhat tick=1 self_ms=574 ... events_us=561630`).
- A dense local DOSBox-X reproduction attempt, done with the EXACT same binary/config as the
  real-hardware run (verified: same mode line, same `vscreen alias ON x=96 y=72 320x240
  pitch=1024` line -- my first two local attempts at this had used the wrong rung entirely, no
  alias, a real config bug on my part caught before drawing any conclusion from it), freeze-capturing
  every tick from 1 through 9 plus 12/16/20/30/50 -- spanning well before and after the object's
  animation start -- **found no duplicate at any sampled tick.** This is a genuine negative result
  on a correctly-matched config, not an inconclusive one from a bad config.

**Hypothesis, not confirmed:** the duplicate is a real-hardware-specific present/framebuffer-write
timing race (the class this campaign has already found before -- see "Pre-existing agsquest-alias-y60
flicker" and the present-narrowing defect history elsewhere in this file), not a general engine
logic bug -- reasoning: the real-hardware witness is an async ~9s-cadence camera, not
tick-synchronised, so for it to have caught this the artifact plausibly persisted for a non-trivial
span of real time, which dense tick-boundary sampling in DOSBox-X should have caught if it were a
defect reproducible at the engine-logic level. Not catching it after that thorough a sweep points
away from a logic bug and toward something specific to real hardware's own present/framebuffer
timing, the physical capture chain, or both -- not yet distinguished.

**Unknown, not yet tested:** whether `--startr 3`'s direct room jump is a factor at all (does the
same duplicate occur reaching room 3 via the game's own normal intro -> menu -> Start path, or only
via the direct jump this cell used). No natural-entry cell has been run, locally or on real
hardware, to check this.

**Next (coordinator's call, in progress):** one bounded real-hardware round, within today's
standing authorization -- repeat the S2F2 launch (same `--startr 3`, same config) with denser,
near-continuous camera sampling bracketing the first 20-30s after room 3 loads, to (a) replicate at
least once more (one sighting could be a fluke) and (b) narrow the actual onset/duration relative
to the `Object 0 set to view 14` log line already found.

**2026-09-22 -- PRE-REGISTRATION, diagnostic cell `DUPCHAR1`. NOT YET RUN.** Same binary/config as
S2F2 (`build/abba/ags-0196.exe`, `binary_sha12=340fa8167624`, `build_dirty=0`, the 512x384
pillarbox cfg, `--ags-arg --startr --ags-arg 3`), but a short auto-exit
(`DOSAGS_TAS_AUTO_EXIT_TICK=800`, well past the room-entry window, not a 5000-tick gate run) and
**no drive-walk.sh** -- the opening animation plays on its own with no player input needed, same as
it did in S2F2 before anyone clicked. The one change: `RUNHW_POLL_S=2` (down from the 8s default),
which sets both the card-frame and camera-shot cadence in `run-hw.sh`'s own wait loop
(`witness_keep.py`) -- the tightest interval this capture setup exposes without bypassing the
witness mechanism entirely (camera shot latency itself is the practical floor beneath that, not
measured in advance). **Counts as a replication:** any camera frame in the first 30s after `Now in
room 3` shows more than one player-character sprite. **Counts as narrowing the window:** the
frame-to-frame gap between the last single-character frame and the first multi-character frame,
and between the last multi-character frame and the first single-character frame again, at ~2s
resolution instead of ~9s. **Not a fluke if replicated; if NOT replicated this once, that alone
does not clear it** (a real-hardware timing race is not guaranteed to reproduce every run) --
report either outcome plainly, do not read a single clean repro as resolving the finding above.

**2026-09-22 -- DUPCHAR1 RESULT: NOT REPLICATED this round.** exit_code clean (`***** ENGINE HAS
SHUTDOWN`), `Now in room 3` confirmed, no VOID condition, no stderr. `RUNHW_POLL_S=2` achieved
~2.7-2.9s actual camera cadence (`tests/harness/results/DUPCHAR1-2026-09-22/witness/camera/`,
frames 00001-00038), more than 3x denser than S2F2's ~9s. The engine's own log this run shows
Object 0's full lifecycle: `set to view 14` / `start anim view 14 loop 0` (tick ~1-7, the part
S2F2's log also showed) followed this time by a second call, `start anim view 14 loop 1` (a
second phase of the same animation, not caught in S2F2's own log excerpt), then cleanly
`Object 0 turned off` / `stop moving`. **Every camera frame from before the animation starts
through `Object 0 turned off` and into steady interactive play (frames 00007-00013, covering the
"And the gentleman thief makes his entrance" narration line and the character visibly walking
from the desk to the bookshelf) shows exactly one player-character sprite** -- reviewed frame by
frame, not just the contact sheet. No duplicate anywhere in the reviewed window.

**Reading this against the pre-registration's own terms: this does not clear the finding.** One
non-replication was explicitly pre-registered as inconclusive on its own, and this cell also
differs from S2F2 in one respect the pre-registration didn't fully control for: no `drive-walk.sh`
was running (none needed for this diagnostic -- the animation is not player-driven), so real
hardware CPU/IO load during the critical window was somewhat different between the two runs
(S2F2 had `drive-walk.sh`'s own vcctrl-side mouse-move traffic active from its 25s warmup
onward, overlapping the room-3 entry; DUPCHAR1 had none). If the defect is a genuine timing race,
a difference in concurrent load is exactly the kind of thing that could change whether it fires --
noted as a real variable, not dismissed. **Next, if pursued further:** repeat once more WITH
drive-walk.sh running (matching S2F2's own conditions exactly, not just its config), before
concluding anything about replication rate one way or the other; two data points (one hit, one
miss under a slightly different condition) is not yet enough to characterize this as rare,
load-dependent, or anything else. Not run without the coordinator's direction, per today's
hardware-round discipline.

**2026-09-22 -- PRE-REGISTRATION, diagnostic cell `DUPCHAR2`. NOT YET RUN. Last round today on
this investigation regardless of outcome (coordinator's bound, same discipline as today's earlier
hang investigation).** Combines both prior cells' own conditions instead of DUPCHAR1's isolated
change: S2F2's exact `drive-walk.sh` timing/params (launched alongside `run-hw.sh`, 25s warmup,
`PERIOD_S=2`, `MAX_CLICKS=90`) -- the coordinator independently confirmed S2F2's driver was live
from 07:58:24, 5s before `run-hw.sh` itself, so it really did overlap the critical window -- PLUS
DUPCHAR1's short `DOSAGS_TAS_AUTO_EXIT_TICK=800` (no 5000-tick gate run needed) and
`RUNHW_POLL_S=2` dense camera cadence. Same binary/config/`--startr 3` as both prior cells
(`binary_sha12=340fa8167624`, `build_dirty=0`, 512x384 pillarbox, alias engaged). This is the one
cell that matches S2F2's own load conditions (drive-walk active through the critical window) while
also getting DUPCHAR1's ~2.7-2.9s camera resolution -- the combination neither prior cell had.
**Counts as a replication:** same as DUPCHAR1 -- any camera frame in the room-entry window shows
more than one player-character sprite. **Reading the three cells together afterward:** S2F2 (driver
ON, ~9s cadence) = HIT; DUPCHAR1 (driver OFF, ~2.7s cadence) = MISS; this cell (driver ON, ~2.7s
cadence) breaks the tie on whether the driver's concurrent load is the operative variable -- a HIT
here points at load-dependence, a MISS here points at S2F2's own hit being the rarer/harder-to-pin
event rather than reliably load-gated. **This is the last hardware round on this investigation
today regardless of outcome** -- report replicated / not replicated / ambiguous plainly and stop;
next steps (if any) are the coordinator's call from there, not decided in advance here.

**2026-09-22 -- DUPCHAR2 RESULT: REPLICATED.** exit_code clean (`***** ENGINE HAS SHUTDOWN`),
`Now in room 3` confirmed, no VOID condition, no stderr. drive-walk.sh ran the full S2F2-matching
timing (lock taken at 15:28:02, 25s warmup, `PERIOD_S=2`, stopped naturally at 31 clicks when the
run ended -- not from hitting `MAX_CLICKS=90`). `tests/harness/results/DUPCHAR2-2026-09-22/
witness/camera/`: frame `00009_082828.525` shows one character (at the desk); frame
`00010_082831.064` shows **two identical character sprites simultaneously** -- one in profile near
the bookshelf, one forward-facing near the desk, the same signature as S2F2's own frame 00003, down
to the two positions; frame `00011_082833.661` is back to one character (with the in-play verb-bar
UI now visible). At `RUNHW_POLL_S=2`'s actual ~2.6-2.7s cadence this brackets the defect far tighter
than S2F2's ~9s cadence could: onset falls somewhere in the ~2.5s between frames 00009 and 00010,
resolution somewhere in the ~2.6s between frames 00010 and 00011 -- roughly a 2.5-5s window total,
down from S2F2's own 9-18s bound. The engine's log shows the same Object 0 lifecycle as DUPCHAR1
(`set to view 14` -> `start anim view 14 loop 0` -> `loop 1` -> `turned off` / `stop moving`,
cleanly) -- the duplicate is not visible in the log itself, only on the physical screen, consistent
with the present/framebuffer-timing hypothesis rather than an engine-side state error the log would
also show.

**Reading all three cells together, per the pre-registration's own terms:** S2F2 (driver ON, ~9s
cadence) = HIT; DUPCHAR1 (driver OFF, ~2.7s cadence) = MISS; DUPCHAR2 (driver ON, ~2.7s cadence) =
HIT. Both driver-ON cells hit; the one driver-OFF cell missed. **This is consistent with the
drive-walk.sh load hypothesis, not proof of it** -- three cells is not enough to separate
"load-dependent" from "common enough that both driver-ON attempts happened to hit it while one
driver-OFF attempt happened to miss it" (a fair coin can land the same way twice). What IS now
established, not merely suggested: the defect is real (two independent real-hardware sightings,
both cross-verified against the raw frames, not one), it is not rare in the sense of "hard to hit"
(2 for 2 under matching conditions), and its onset/duration is now bracketed to within a few
seconds of `Object 0`'s own logged animation-start tick rather than a loose 9-18s window. **Per the
coordinator's bound, this is the last hardware round on this investigation today.** Not pursuing
further rounds, a `--startr`-vs-natural-entry test, or a root-cause fix without the coordinator's
direction.

## Root cause: Object visibility has no invalidation path (same defect class as the pre-0191 GUI bug)

**2026-09-22 -- source read, per the operator's direction (root-cause now, no guessing, read gating
code not commit titles).** Read `patches/ags/0190`/`0191` (the GUI stage-1 fix) and
`vendor/ags/Engine/ac/{global_object.cpp,object.cpp,draw.cpp}` directly, not from memory.

**Item 1 -- does an Object's visibility change get the same before/after-restore treatment GUIs got
in 0190/0191? No -- it has no invalidation path at all, stock AGS or DOS-PORT-patched.**
- `ObjectOff()` (`global_object.cpp`): sets `objs[obn].on = OBJ_STATE_DISABLED`, logs "Object %d
  turned off", calls `StopObjectMoving()` -- and calls no invalidation function of any kind. Compare
  `SetObjectBaseline()` three functions above it, which DOES call `mark_object_changed()` when the
  baseline changes -- `ObjectOff()` has no equivalent call. This is exactly patch 0191's own
  description of the original GUI defect: "`GUIMain::SetVisible` marks nothing... nothing else does."
- `prepare_objects_for_drawing()` (`draw.cpp:2252`), the per-frame loop that decides which objects
  get added to the sprite list: `if (obj.on != OBJ_STATE_ENABLED) continue; // disabled` -- and the
  identical pattern for off-screen (`if ((obj.x >= thisroom.Width) || (obj.y < 1)) continue;`). Just
  `continue`, no comparison against what was drawn last frame, no flush of an old rect. This is the
  exact structural hole patch 0191's `dos_port_gui_flush_unmarked()` was built to close for GUIs --
  Objects never got the equivalent.
- **Confirmed this is not Object-specific -- Characters have the identical gap.**
  `prepare_characters_for_drawing()` (`draw.cpp:2359`) has the same `if (chin.on == 0) continue;`
  with no before/after comparison, and `character.cpp` has zero invalidate-family calls anywhere
  (checked directly, not inferred). So this is a general "drawable room entity stops being drawn"
  gap in the engine, present since before any DOS-PORT patch touched it -- not something any patch
  introduced. It has simply never been exercised: every cell in this whole campaign that moves a
  Character keeps it `on` throughout (ordinary walking changes position, not visibility, and
  position changes ARE correctly invalidated via `put_sprite_list_on_screen()`'s own
  `invalidate_sprite()` call on every drawn sprite, every frame -- confirmed at `draw.cpp:3021`,
  `in_room=true` for room sprites). 5 Days a Stranger's room-3 cutscene is the first content
  anywhere in this campaign that actually flips a visibility flag (`Object.Visible=false` /
  `ObjectOff()`) mid-scene while the narrowed present is active and something is watching the
  physical screen closely enough to catch it.
- **Mechanism, following 0193's own account of the same class of bug:** with the narrowed present
  (0124/0129/0193) only pushing what was explicitly marked dirty, an object that stops being drawn
  leaves its last-rendered pixels on the physical screen -- correct in RAM (the restore + skip
  redraws it away internally, confirmed: the engine's own log shows `Object 0 turned off` /
  `stop moving` cleanly on every cell, including both cells where the duplicate did NOT appear on
  screen) but never told to the screen. This is consistent with everything observed: the duplicate
  never appears in the engine's own log (RAM state is always correct), only on the physical screen;
  the ghost eventually disappears on its own (frame 4 in S2F2, frame 11 in DUPCHAR2) because *some
  other* unrelated invalidation eventually happens to overlap that same screen region, not because
  anything deliberately erases it.

**Item 2 -- the tick/event-dispatch ordering, read directly in `vendor/ags/Engine/main/game_run.cpp`
(`UpdateGameOnce()`), not guessed.** Per-tick order: `input_poll` (SDL_PollEvent) ->
`room_check` -> early rep-exec -> `ground_interactions` (hotspot/region lookups, **schedules**
events via `setevent()`, does not run them inline for 3.6.3+ games) -> `input_handling`
(`ags_domouse()`, GUI-under-mouse, **`GameUpdateCheckControlsAndEdges()`** -- where a mouse click's
own dispatch happens) -> game-state update -> late rep-exec -> audio sync ->
`UpdateDrawableObjectStates()` -> `render_graphics()` (scene_construct + present, where
`prepare_objects_for_drawing()` and the restore both live, in that order within
`construct_room_view()`) -> **`GameUpdateProcessEvents()`** (`processallevents()` -- where a
`setevent()`-scheduled handler, e.g. a room's `on_call`/interaction script that could call
`ObjectOff()`, actually *runs*) -> end-of-tick bookkeeping -> `WaitForNextFrame()`. **The scheduled-
event dispatch that would run an object-disabling script handler happens AFTER this tick's own
render**, so a state change decided this tick is invisible to the engine's own drawing code until
next tick -- an unconditional one-tick latency, present on every tick regardless of concurrent
input.
**Honest limit:** the exact script that calls `ObjectOff()` for Object 0 (whatever room interaction
or timed script drives the "gentleman thief" sequence) is compiled into `5DAYS.AGS`'s own room data,
not present anywhere in this open engine source -- it cannot be read the way the GUI bug's engine-
side mechanism could. **Reframing the drive-walk correlation against what IS confirmed:** since the
missing invalidation is unconditional (it fires -- or rather, fails to fire -- identically whether
or not a driver is running), the correlation is most plausibly not a race in *whether/when the
disable itself is recorded*, but in *whether something else's invalidation happens to overlap the
ghost's screen rect before a given camera sample*. Concurrent mouse-driven work every tick while
the driver runs (`ags_domouse()`, `update_cursor_over_gui()`/`gui_poll`, cursor-hotspot redraws) is
a plausible source of exactly that kind of incidental, unrelated overlap -- but this is a hypothesis
about *why sampling happened to correlate with driver state*, not a mechanism the underlying bug
requires. 2-for-2 vs 0-for-1 is real but small; it does not by itself prove load-dependence, per the
DUPCHAR2 write-up above.

**Item 3 -- hypothesis, pre-registered before writing any fix:**
- **Mechanism:** a room `Object` (or `Character`, same gap, not touched by this fix) that
  transitions from drawn-this-frame to not-drawn (disabled or moved off-screen) leaves its last
  on-screen rectangle unmarked for the present's dirty-rect union, because neither `ObjectOff()`
  nor `prepare_objects_for_drawing()`'s per-frame skip has any before/after comparison -- the exact
  gap `dos_port_gui_flush_unmarked()` (patch 0191) closed for GUIs, never built for Objects.
- **Candidate fix:** mirror 0191's technique, scoped to Objects only (Characters noted as the same
  gap, not fixed here -- smallest change that tests the hypothesis). Add a per-object "last drawn
  rect" record; in `prepare_objects_for_drawing()`, when an object that WAS recorded as drawn last
  frame is about to be skipped this frame (disabled or off-screen), invalidate its recorded rect
  (`invalidate_rect(rx, ry, rx+rw, ry+rh, true)` -- `in_room=true`, confirmed at `draw.cpp:3021` as
  the room-sprite convention, not the GUI path's `false`) before the `continue`. Placed inside
  `prepare_objects_for_drawing()` itself, which already runs before `draw_room_background()`'s
  restore within `construct_room_view()` (confirmed by reading the call order directly:
  `construct_room_view()` calls `prepare_room_sprites()` -> `prepare_objects_for_drawing()` at
  line 3075, THEN the per-viewport loop's `draw_room_background()` at line 3132) -- so the mark
  lands as a pre-restore mark for THIS frame, no "late flush" fallback needed the way GUIs needed
  one (Objects have no later-in-the-frame state-change window between this decision point and the
  restore the way GUI script code did). Re-enabling an object needs no symmetric handling: once
  drawn again, it goes through the normal `put_sprite_list_on_screen()` -> `invalidate_sprite()`
  path like any other frame, which already works (confirmed: this is the same path that already
  correctly invalidates a moving object's old position every frame).
- **What confirms:** a debug counter on the new flush path (mirroring `guiflush`) fires for Object 0
  at the tick where `Object 0 turned off` is logged, on every run where that log line appears --
  checkable in DOSBox-X even though DOSBox-X does not naturally show the visible glitch (its own
  present timing evidently lets something else cover the gap before any DOSBox-X capture catches
  it -- a real, unexplained difference from real hardware, not assumed away). This is a mechanism
  check, not a visual repro -- DOSBox-X not reproducing the glitch was already established before
  this investigation started and is not expected to change.
- **What falsifies:** if the counter does NOT fire for Object 0's disable (meaning some other code
  path already covers this case and the read above missed it), or if a real-hardware cell with this
  fix applied still shows the duplicate at a comparable rate, the missing-invalidation theory is
  wrong or incomplete.
- **Gate before anywhere near real hardware, same as every other patch today:** the standing
  DOSBox-X screen-equality gate (`gate-present.sh`/`gate-alias.sh`) must still pass on every existing
  row (this touches present/draw code every arm exercises) before this is a candidate for anything
  beyond a source-level and DOSBox-X check. **No further real-hardware rounds without checking in
  first**, per the operator's explicit bound today (8 rounds already spent).

**2026-09-22 -- gate result and next steps, per the coordinator's own follow-up (queued ahead of
time, standing authorization for both pieces below -- no further check-in needed for either).**
Full standing gate (`gate-alias.sh`, no scope flags -- every row) run twice against
`build/abba/ags-0197.exe`: a first attempt cut short by my own `timeout 500` wrapper at the `text`
arm (not a gate failure -- `idle`/`walk`/`anim4`/`anim12` all clean before the cutoff), a second,
longer-timeout run reproducing the same four rows clean and continuing through the rest of the
suite.

**FULL GATE RESULT: 13 of 14 rows clean, zero regressions.** Every BENCH8 arm (idle, walk, anim4,
anim12, text, gui, full), AGS Quest, both BENCH8 and BENCH16 pillarbox rows, and the 5 Days a
Stranger catalogue row all pass (`A==B: ok`, 0 problems, control fails as required). **The one
failing row, `shards-alias-512x384`, is the pre-existing, already-documented, decoupled tick-100
title-screen content defect** (same bbox `(512, 513, 1152, 913)` as the original finding, ticks
300-900 clean) -- unrelated to this patch (Object-visibility invalidation has nothing to do with
Shards' own title-screen content nondeterminism), unchanged by it, not caused by it. One incidental
difference from the original finding worth recording plainly rather than glossing over: this run's
own control (`DOSAGS_BREAK_0193=1`) did NOT differ from B at tick 100 this time (`"control did NOT
fail (no power on this row)"`), where the original finding's control DID differ (255,624px) -- both
readings are consistent with the same underlying tick-100 nondeterminism (sometimes the random
content state coincides across arms, sometimes it doesn't); the gate's own overall verdict is
unaffected since 13 other rows demonstrated the control's power.

**Patch 0197 committed and exported.** `vendor/ags` commit `e622baaa8` (checkpoint branch
`export-0197`, matching the `export-0190`-`export-0195` convention already in place for this
detached-HEAD-per-patch workflow), `git format-patch` exported to
`patches/ags/0197-DOS-PORT-patch-0197-an-Object-that-stops-being-drawn.patch`.

## Real-hardware validation of patch 0197 (DUPCHAR3), pre-registered ahead of time

**Goal:** confirm whether the duplicate-character defect is gone on the fixed binary, under the
exact same conditions DUPCHAR2 reliably hit it. **Command: identical to DUPCHAR2**, only the binary
changes -- `AGS_EXE=build/abba/ags-0197.exe RUNHW_POLL_S=2 run-hw.sh 5days --tag DUPCHAR3 --timeout
300 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=800 --ags-arg --startr
--ags-arg 3 --extra-file presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG`, with
`drive-walk.sh DUPCHAR3 25 2 90` launched alongside `run-hw.sh` the same way (matching S2F2/DUPCHAR2's
own timing, not DUPCHAR1's isolated no-driver variant -- driver-ON is the condition that hit 2/2).
**Counts as fix confirmed:** every camera frame from before `Object 0 set to view 14` through
`Object 0 turned off` and into steady interactive play shows exactly one character, reviewed frame
by frame the same way DUPCHAR1/DUPCHAR2 were, not just the contact sheet. **Counts as fix NOT
confirmed:** a duplicate appears anywhere in that window. **One clean run does not, by itself, prove
the race is gone** (DUPCHAR1's own natural miss under different conditions already showed this isn't
100% reliable even unfixed) -- report the raw outcome plainly either way; a single miss here is
still informative (especially combined with the `objflush` mechanism confirmation already on
record) but is not being overclaimed as certainty. VOID conditions: same as DUPCHAR1/DUPCHAR2 --
`Now in room 3` not reached, `binary_sha12` mismatch, `build_dirty` != 0, tag reused, more than one
manifest block, an SDL trace collected.

**CORRECTION (2026-09-22, found during step 8.0): DUPCHAR3 did hit a VOID condition.** Its own
`RUNMANI.LOG` reads `build_dirty=1` (`binary_sha12=4a6da6186078`), and the result below says "No VOID
hit". `build/abba/ags-0197.exe` differs from a clean build of the same tree (`4b621d0350d4`) in 11 bytes,
all in the stamp and the dirty flag, so the code that ran was the export-0197 code and DUPCHAR3's
finding (duplicate still seen) is unaffected; DUPCHAR4 has since explained it anyway. Recorded so the
text below is not read as a clean-build cell.

**2026-09-22 -- RESULT: ran clean, VOID conditions all clear, fix NOT confirmed by the pre-registered
bar -- the duplicate still appeared. Reinterpreted below: source-grounded evidence now says this was
probably never patch 0197's bug to fix.**

Identity: `RUNMANI.LOG`/`DUPCHAR3.LOG` `binary_sha12=4a6da6186078`, `duration_s=36`, `exit_code=0`,
`fps_p50=40.00`. Differs from S2F2/DUPCHAR2's `binary_sha12=340fa8167624` as expected (a different
binary ran) -- independently corroborated two ways: `sha256sum build/abba/ags-0197.exe` is
`48917f1a5115...` (a different identity space entirely; `binary_sha12` is `PORT_BUILD_SHA12`, a
build-time fingerprint of the vendor source trees + build flags, not a hash of the linked binary --
confirmed from `Makefile`'s own `AGS_BUILD_SHA12` recipe, not assumed), and `vendor/ags` `HEAD` sits
at `e622baaa8` == `export-0197` right now, the exact tree `ags-0197.exe` was built from. No VOID hit.
Coordinator independently confirmed the same binary via `/proc/611694/environ`.

`DUPCHAR3.LOG` itself carries no per-event lines (only the `tickstats_*` block) -- the
`objflush`/"Object N turned off" lines live in `STDOUT.TXT`, not the tagged log; noted here because
it's an easy place to look in the wrong file. `STDOUT.TXT`: `Object 0 turned off` fires once, and
`DOS-PORT objflush n=1` / `objflush idx=0 n=1` confirm patch 0197's flush executed for it, on real
hardware, exactly as designed.

Camera witness: frame 00009 (09:35:02.722) one character; **frame 00010 (09:35:05.430) two identical
gray-suited figures, one at the bookshelf, one at the desk**; frame 00011 (09:35:08.158) one
character, with "And the gentleman thief makes his entrance." visible on screen; frame 00012
(09:35:10.907) stable single-character interactive state. Same signature as S2F2 and DUPCHAR2. By the
pre-registered bar above, this is **fix NOT confirmed** -- reported plainly, not softened.

**Investigation, per the coordinator's direction (source first, no further hardware without a
source-grounded reason):**

1. Went looking for the Character-side equivalent of the Object gap patch 0197 closed.
   `prepare_characters_for_drawing()` (`vendor/ags/Engine/ac/draw.cpp:2411-2446`) has the identical
   structural gap: `if (chin.on == 0) continue;` and `if (chin.room != displayed_room) continue;`,
   neither wrapped in any `#ifdef __DJGPP__` invalidation block, unlike the now-fixed Object loop.
   Structurally confirmed, unfixed -- this part of the coordinator's hypothesis (b) is real.

2. But triggering it needs some event that actually flips a Character's `on` flag or room membership
   near this window, and the full `STDOUT.TXT` script trace for room 3 (every `Game :` line, start to
   finish) shows no such event for any character -- no "moved to room", no on/off toggle, nothing
   beyond `cTrb`'s own `Face location` calls (facing, not visibility) and two later `MoveCharacter`
   requests. Ruled out one concrete candidate directly rather than leaving it as a guess: added a
   one-line `debug_script_log` at `room.cpp:1027`'s `PlayerCharOff` branch (the one place in the
   engine that silently sets `forchar->on=0` with no log of its own -- see
   `play.temporarily_turned_off_character`, `room.cpp:401-403,1028-1037`), rebuilt `build/ags/ags.exe`
   locally (DJGPP toolchain at `~/emulators/tools/djgpp`, not in `PATH` by default -- `export
   PATH="/home/claude/emulators/tools/djgpp/bin:$PATH"`), and ran room 3 in local DOSBox-X
   (`run-dosbox.sh 5days --env DOSAGS_TAS_AUTO_EXIT_TICK=400 --ags-arg --startr --ags-arg 3`). Result:
   `DOS-PORT-DIAG room 3 PlayerCharOff=0 char=0(cTrb) x=160 y=160` -- **`cTrb` is never hidden in this
   room.** Diagnostic line reverted immediately after (`git -C vendor/ags checkout --
   Engine/ac/room.cpp`); `vendor/ags` is back to a clean `export-0197` tree, nothing committed from
   this. Hypothesis (b), as "some Character silently toggles near this window," is refuted for this
   specific case, even though the underlying structural gap in `prepare_characters_for_drawing()` is
   real and still unfixed in general.

3. With (b)'s specific trigger ruled out, went back to the visual signature itself rather than
   guessing at (c). Built and ran a **local, non-hardware** freeze-capture
   (`run-dosbox.sh 5days --fixed-timestep --env DOSAGS_TAS_AUTO_EXIT_TICK=500 --ags-arg --startr
   --ags-arg 3 --freeze-capture <dir> --env DOSAGS_FREEZE_TICKS=300,340,360,420` -- `--fixed-timestep`
   is required for freeze ticks to land exactly, confirmed from `gate-alias.sh`'s own invocation after
   a first attempt without it produced zero frames) at ticks bracketing "Object 0 turned off".
   Screenshots (`tests/harness/results/DUPCHAR3-2026-09-22/local-diag-freeze-r3/`, `FRZ00`-`FRZ03`):
   tick 300 and tick 343 both show **two identical gray-suited figures on screen simultaneously**, one
   at the bookshelf, one at the desk -- the same signature as every real-hardware sighting, reproduced
   locally, on demand, deterministically. Tick 361 (right after "Object 0 turned off"/"Object 0 stop
   moving" in `STDOUT.TXT`) shows **one figure** (bookshelf); the desk area is cleanly restored, no
   ghost. Tick 421 shows the same single figure with "And the gentleman thief makes his entrance." now
   on screen. This whole run's own present-verifier read `stale_frames=0 stale_px=0` across 286 frames
   -- the DOS port's own correctness instrument sees no invalidation failure anywhere in this run.

**Reading:** this is consistent with the two-figure moment being the room's own scripted intro, not a
stale/unflushed sprite -- Object 0 plays a distinct "walking in" animation (`view 14`, 2 loops) ending
near the desk, while Character `cTrb` (never hidden, `PlayerCharOff=0`) is already waiting at the
bookshelf; both draw as the same costume because 5 Days a Stranger's Trilby *is* "the gentleman thief"
(the narration's own words) -- Object 0 is presumably standing in for his own entrance sprite before
handoff. Object 0 turning off is clean (zero stale pixels, patch 0197's flush working exactly as
designed on an event that was apparently never what produced the visible "duplicate" in the first
place). Under this reading, S2F2/DUPCHAR1/DUPCHAR2/DUPCHAR3 may all be the same intended cutscene beat,
not a bug at all, and there may be nothing here for the DOS port to fix.

**What this does not settle:** whether the original (non-DOS) game is actually meant to show two
figures at once during this beat, versus this being some other quirk. That is a question about this
game's own script/asset design, answerable from a reference video or the operator's own knowledge of
the game -- not from engine traces or a stale-pixel verifier, which can only say the DOS port drew
what it was told to draw, cleanly. Not declaring this closed unilaterally; handing the raw evidence
back rather than a verdict. No second patch written. No further real-hardware round run on this
specific question, per instruction, pending that call.

**2026-09-22 -- PRE-REGISTRATION, local diagnostic `DUPCHAR4` (DOSBox-X only, no real hardware).
NOT YET RUN.** Question: is the room-3 two-figure frame an artifact of the `--startr 3` debug jump?
Coordinator's reading of FRZ00 / DUPCHAR3 camera 00010: the BOOKSHELF figure is in profile, reaching,
beside the left-wall window (dark/open in FRZ00, glazed in FRZ02) -- Object 0 (view 14) doing the
window climb-in; the DESK figure faces the camera at about screen-centre x with its feet below the
floor edge, where the DUPCHAR3 diagnostic put `cTrb x=160 y=160` at room load. Stock `--startr`
(`vendor/ags Engine/main/game_start.cpp:210-211`) sets only `playerchar->room`; x/y stay at the
character's authored defaults. The game's own flow starts in room 1 (S2F1: `Now in room 1`) and
reaches room 3 through earlier rooms that can place, hide or recolour the player in ways `--startr`
skips. **Prediction:** on NATURAL entry to room 3, the climb-in frames show ONE figure (the player
off-screen, hidden, or placed where the object ends); on `--startr` entry, TWO (reproduces FRZ00).
**Falsified if** natural entry also shows two figures during the climb -- then it is the game's own
staging or an engine-side (not present-side) difference; report and stop. **Method:** local build
`build/ags/ags.exe` = the `export-0197` tree plus a THROWAWAY, uncommitted diagnostic (reverted after):
(a) at room load, log the player's x, y, on, transparency, view, loop, frame, flags, prevroom and
the load tick; (b) every rendered tick in room 3, log the same fields plus Object 0's on/view/x/y
whenever any of them changes; (c) `DOSAGS_DIAG4_REL3=1` makes `DOSAGS_FREEZE_TICKS` count from the
room-3 load tick instead of game start, so both entry paths freeze at the same room-relative ticks
even though natural entry depends on input timing. Both paths: `--fixed-timestep`, the same 512x384
pillarbox cfg (`presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG` -> `ACSETUP.CFG`), freeze at
room-relative ticks 20,100,200,300,343,361,421 (the last four match FRZ00-FRZ03). Natural entry is
driven by xdotool on a private Xvfb. Stop if natural entry is unreachable after ~45 min of driving.

**2026-09-22 -- DUPCHAR4 RESULT: prediction MET. The room-3 "duplicate" is the `--startr 3` jump
leaving the player at his authored default position, not a port defect and not the game's own
staging.** Raw: `tests/harness/results/DUPCHAR4-2026-09-22/` (README, both arms' STDOUT.TXT and
freeze frames, `sheet.png` per arm, `diag4-throwaway.diff`). Both arms: 512x384 16-bit, `vscreen
alias ON x=96 y=72 320x240 pitch=1024`, present verifier `stale_frames=0` (668 frames `--startr`,
10,319 natural). Natural entry reached with one START click: room 1 -> room 2 (intro + title
menu) -> room 99 (title card) -> room 3.
*Facts.* Player at room-3 load -- `--startr`: `x=160 y=160 on=1 tr=0 view=8 prevroom=3`; natural:
`x=15 y=194 on=1 tr=0 view=8 prevroom=99`. In both arms the room script moves him to `x=71 y=126` at
the tick Object 0 turns off (rel 352 / 353). Frames at the same room-relative ticks: `--startr`
FRZ00-02 one figure (cTrb at the desk), FRZ03-04 (rel 300/343) TWO (Object 0 climbing in at the
window + cTrb at the desk -- reproduces local-diag-freeze-r3 FRZ00 and every real-hardware
sighting), FRZ05-06 one at the bookshelf; natural FRZ00-02 empty room, **FRZ03-04 ONE figure
(Object 0 only)**, FRZ05-06 one at the bookshelf, identical to `--startr`'s. The earlier real-
hardware sequence (camera: one at the desk, then two, then one at the bookshelf) is exactly the
`--startr` arm's sequence.
*Hypothesis, not checked:* why the player is not visible at (15,194) with `on=1 tr=0` -- most
likely a walk-behind or an out-of-room parking spot in the game's own data; no room-data hunt done.
*Consequences (the coordinator's call, recorded not decided here):* the DUPCHAR sighting is a
test-fixture artifact of every `--startr 3` cell (S2F2, DUPCHAR1-3), so it is no longer a reason on
its own to hold S2F2's figures; patch 0197 stays a real but separate fix (its flush demonstrably
fires on Object 0's turn-off); the Character-side gap in `prepare_characters_for_drawing()` is still
real and unfixed in general, with no trigger found in this game. Throwaway diagnostic reverted,
`vendor/ags` clean at `export-0197`, `build/ags/ags.exe` rebuilt without it. No real hardware used.

## Step 6: GUS on/off ABBA on the Gate 2 fixture, pre-registered ahead of time

**Lever:** `[sound] enabled` (0 vs 1) plus, for the sound-on arm, `SDL_HINT_DOS_AUDIO_BACKEND=gus`
(confirmed exact hint name and success line -- `vendor/ags/Engine/platform/dos/
dos_midi_backend.cpp` -- `"DosMidiBackend: native GF1 (Gravis Ultrasound) backend active"` on
success, `"...no GF1 detected -- MIDI disabled this session"` if the card is not actually in GUS
mode; `SDL_HINT_DOS_GUS_PIO_AUTOINC` defaults to `"1"` already, no need to set it explicitly).
**Fixture: identical to Gate 2's own claim** -- BENCH8 anim12, Mode 13h, `ACSETUP-OFF-NATIVE.CFG` +
`anim12-gate.cfg`, `--gate` 5000 ticks (the same rung F2B1/F2B2 used) -- the walk arm is not
included in this one ABBA, per the step's own singular framing; a second block on walk is a
separate future step if this one's result calls for it. **New config file needed and added:**
`tests/harness/presentation/bench8/ACSETUP-ON-NATIVE.CFG`, a copy of the existing
`ACSETUP-OFF-NATIVE.CFG` with only `enabled = 1` changed -- every other field (critically
`fullscreen = native`, the Mode 13h rung itself) stays byte-identical, so sound is the only variable
that moves. (The pre-existing `tests/harness/games/bench8/ACSETUP-ON.CFG` was checked and NOT
reused -- it sets `fullscreen = full_window`, a different rung than Gate 2's own.)
**Boot profile:** `--boot-profile 3` (PGGUS on this rig, confirmed against `run-hw.sh`'s own
documented profile table) on every cell in the block, both A and B arms -- idempotent
(`select_boot_profile()` only reboots if the current profile differs), and per the prior S7-GUS
precedent (`PLAN-LOG.md`, tags `SGA1-SGA2`, a different milestone/fixture, not reused here) sound-off
cells do not need the card in a different mode since AGS's own audio init never runs when
`enabled=0` -- one PGGUS boot for the whole block, not a reboot per arm. **Tags (fresh, not
`SGA1`-family):** `GUSA1 GUSB1 GUSB2 GUSA2`, order A-B-B-A per the standing ABBA methodology.
**Prediction:** genuinely uncertain, which is why this is being measured, not assumed -- the prior
S7-GUS finding ("-0.05 fps, noise") was at the OLD ~5 fps/200ms-tick regime; "12% of tick rate" at
that regime is a much smaller ABSOLUTE cost than 12% of today's 25ms tick budget would be. Two
questions, not one: (1) does `fps_p50`/`tick_rate_steady` stay inside Gate 2's own band (39.2-40.8,
`fps_p50` >= 40) with sound on; (2) what is `tick_rate` (not just fps) doing, since the prior
finding's own "12%" figure was a tick-rate effect that did not show up in fps at the old tier --
report both numbers, do not fold tick_rate into a single fps verdict. **Threshold:** reusing this
work order step's own bar structure -- a fps cost <= 1.5 (matching the original Sound-milestone
acceptance bar, the only precedented number available) is not disqualifying by itself; a fall
outside the Gate 2 band (regardless of the 1.5 figure) IS disqualifying for the "sound on, at 40"
claim specifically. **Invalidity:** A-to-A and B-to-B spread checked before trusting any delta,
per the standing ABBA methodology; A cells expected to reproduce today's own Gate 2 baseline
(anim12: `fps_p50` 40.00, steady ~40.01, whole-run ~39.34) within the same run-to-run floor (0.01)
already established for this exact fixture. **VOID if:** the GUS success log line does not appear
on a B cell (falls back silently instead of reporting "MIDI disabled" honestly); mode line is not
`320 x 200 (8-bit) fullscreen`; `vscreen alias ON y=0 320x200 pitch=320` absent; binary/build_dirty
mismatch; a tag reused. Witness: card + camera, same standing order as every cell today.

**2026-09-22 -- A1 cell result, after a real, informative harness detour (both retained as raw
data, `tests/harness/results/SNDA1-2026-09-22-VOID/`, `tests/harness/results/SNDA3-2026-09-22/`).**

Tag rename first: this block's original tags (`GUSA1 GUSB1 GUSB2 GUSA2`) turned out to collide --
`GUSA1` was already used 2026-09-15 (`S7-gus-autoinc-ab-realhw-2026-09-15.md`, PLAN-LOG.md:6636) and
every other `GUS*` tag ever used in this repo was checked and is also taken
(`GUSA1 GUSAB0 GUSAB1 GUSD1 GUSDMAWE(DGE) GUSN1 GUSQ1 GUSQ2 GUST1 GUSU1 GUSV1`). Renamed the whole
block off the `GUS` prefix to `SNDA1 SNDB1 SNDB2 SNDA2` (confirmed unused) to close the question for
good rather than dodge one collision into another (`GUSA2`, the coordinator's first suggested
replacement, wasn't actually free either -- it's this same block's own 4th-cell tag).

`--boot-profile 3` (PGGUS) itself then failed 0/4 via a single `run-hw.sh` attempt each (clean,
prompt `select_boot_profile -> None`, no crash, machine left idle and safe every time) -- a
documented, pre-existing rig gap (PLAN-LOG.md: `GUST1`/`GUSD1`/`GUSV1`/`GUSU1`/`GUSN1`, 2026-09-13..
15, rates from "3-for-3 failed" to "first attempt" session to session, never fixed, only ever hand-
retried). Re-ran the identical primitive standalone with verbose per-stage logging: 1/1, landed
cleanly (capslock edge_s=18.42, scrolllock ready_s=2.70, prompt_s=0.79). Rather than hand-splice
run-hw.sh's own witness/launch/collect machinery around that one proven step (real risk of a subtler
bug than the flake being routed around), added a small, narrow retry loop to `run-hw.sh`'s existing
boot-profile call instead (`RUNHW_BOOT_PROFILE_RETRY_N`, default 3 -- commit `df6e052`). Validated
same session: both `SNDA1` and `SNDA3` needed exactly one retry (attempt 1 missed, attempt 2 landed,
edge_s 18.38-18.49 both times) and then completed their full pipelines unattended.

Separately, and caught before anything was recorded: `run-hw.sh` was never given an explicit
`AGS_EXE`, so the first corrected attempt ran its own default (`build/ags/ags.exe`) instead of Gate
2's own established baseline (`build/abba/ags-0194.exe`) -- a stale local rebuild left over from the
DUPCHAR3 source investigation earlier this session, `binary_sha12=a36f76536d71`, **`build_dirty=1`**.
Not recorded; redone with `AGS_EXE` pinned explicitly. That redo then hit a THIRD, self-inflicted
issue -- reusing the tag `SNDA1` against a target whose `DEST` still held the wrong-binary run's own
files produced exactly the `G2R1` failure mode: two `RUNMANIFEST` blocks in one collected `.LOG`
(`tests/harness/results/SNDA1-2026-09-22-VOID/VOID.txt` has the full account). Per the same rule that
made `G2R1` VOID, not "take the last block": discarded, redone under a genuinely fresh tag, `SNDA3`.

**`SNDA3` (A1 arm, sound off, `PGGUS` boot profile, `build/abba/ags-0194.exe`, `binary_sha12=
e8d4b76c5cd9`, `build_dirty=0`) -- clean.** One `RUNMANIFEST` block. Mode line `320 x 200 (8-bit)
fullscreen`, `vscreen alias ON y=0 320x200 pitch=320` present. Witness sheets (card + camera, 11
frames each) reviewed: consistent, complete anim12 background every frame, no trails (frame 1's dark
card / green-tinted camera shot is the same benign stream-settling artifact noted on other cells
today, not content). `fps_p50=40.00`, `fps_p95=40.24`, `tick_rate_steady=40.01`, `ticks=5000`,
`stall_ticks=0`, `loop_ms=124981`, `duration_s=131` -- inside Gate 2's own band (39.2-40.8,
`fps_p50` >= 40) and matches the VOID `SNDA1` run's own second (correct-binary) manifest block
closely (40.01/5000/40.00/40.24), which is reassuring cross-run agreement even though that run isn't
being counted. A-to-A check (`SNDA3` vs. Gate 2's `G2R1`/anim12 baseline `fps_p50` 40.00, steady
~40.01) reproduces within the established run-to-run floor.

Next: `SNDB1` (sound on, GUS), same fixture, same `PGGUS` boot (no reboot needed between arms now
that the profile is already selected and no file changes -- **wait, ACSETUP.CFG does change between
A and B arms**, so `SNDB1` still needs its own stage+send, which will itself revert to `PGSB` and
need another boot-profile selection; the "one PGGUS boot for the whole block" framing in this step's
own pre-registration undersold that -- every arm whose `ACSETUP.CFG` differs from the previous one
needs its own transfer, and `vcctrl_send_file`'s own tool description confirms every transfer reboots
the target twice regardless of file count. Noting this now rather than re-discovering it mid-block.

**2026-09-22 -- FULL ABBA RESULT (`SNDA3 SNDB1 SNDB2 SNDA2`, in that order -- the A-B-B-A block
itself, not counting the discarded `SNDA1`). All four raw under `tests/harness/results/<TAG>-2026-09-22/`.**

Identity, all four cells: `build/abba/ags-0194.exe`, `binary_sha12=e8d4b76c5cd9`, `build_dirty=0`,
mode line `320 x 200 (8-bit) fullscreen`, `vscreen alias ON y=0 320x200 pitch=320` present, one clean
`RUNMANIFEST` block each, witness sheets reviewed (card + camera, 10-11 frames each cell, every
single frame across all four cells shows the same complete anim12 background -- window, pillar, board
panel, pinwheel border -- no trails; frame 1's dark-card/green-camera tint on every cell is the same
benign stream-settling artifact, not content). B arms (`SNDB1`/`SNDB2`) additionally confirm
`DOSAudioMixer: GUS PCM path active (8-bit unsigned @ 11025 Hz mono, up to 8 voices...)` in
`STDOUT.TXT` and `audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0` in the manifest -- GUS
audio genuinely engaged, zero underruns, both B cells.

**Raw numbers (fps_p50 / fps_p95 / tick_rate_steady / tick_rate / frames_skipped / ticks /
stall_ticks / duration_s):**
- `SNDA3` (A1): 40.00 / 40.24 / 40.01 / 39.33 / 4 / 5000 / 0 / 131
- `SNDB1` (B1): 40.00 / 40.24 / 40.01 / 39.33 / 4 / 5000 / 0 / 131
- `SNDB2` (B2): 40.00 / 40.24 / 40.01 / 39.34 / 4 / 5000 / 0 / 131
- `SNDA2` (A2): 40.00 / 40.24 / 40.01 / 39.34 / 4 / 5000 / 0 / 131

**Invalidity checks, both pass with the widest possible margin:** A-to-A (`SNDA3` vs `SNDA2`) --
every field identical except `tick_rate` 39.33 vs 39.34 (0.01, at the field's own reporting
resolution). B-to-B (`SNDB1` vs `SNDB2`) -- same, 39.33 vs 39.34. Both reproduce Gate 2's own anim12
baseline (`fps_p50` 40.00, steady ~40.01) exactly.

**Verdict, against the pre-registered two-question bar:** (1) `fps_p50`/`tick_rate_steady` stay
inside Gate 2's band on every B cell (40.00/40.01, both `fps_p50` >= 40) -- yes, with zero margin
consumed. (2) `tick_rate` (the field the original S7-GUS "12% of tick rate" finding was actually
about) shows **no A-vs-B direction at all** -- B cells are not systematically lower than A cells;
the whole four-cell spread is 39.33-39.34, tighter than the pre-registered 0.05 threshold by 5x, and
the sign flips (A2 > A1, B2 > B1, both by the same 0.01) rather than tracking the sound lever. **No
measurable fps or tick-rate cost from GUS PCM audio at 40fps, sound off vs on, on this fixture.**

**Scope note, not a threat to the result but worth being explicit about:** this fixture's own
`STDOUT.TXT` shows `Playing music 0` at scene start but zero MIDI activity in the manifest
(`midi=none,events=0`) and no `DosMidiBackend` init line at all in either B cell -- BENCH8's anim12
scene never actually drives the MIDI subsystem (no warning, no crash, the call just does not reach
it). What this ABBA measured is the **GUS PCM/SFX path's cost specifically**, not MIDI -- the much
larger, already-characterized MIDI tax from the S7-GUS investigation (PLAN-LOG.md, `~10-12x`
systemic cost at the old fps regime, later narrowed to `gus_sink.c`'s `reap_finished_voices()`
GF1 voice-mask scan) is a separate, still-open question this specific cell does not speak to.

Harness gap found and fixed along the way, independent of this result: `tests/harness/run-hw.sh`'s
`--boot-profile` selection needed a retry loop (`RUNHW_BOOT_PROFILE_RETRY_N`, commit `df6e052`) --
0/4 via a single attempt this session, 100% (5/5 across the corrected `SNDA3`/`SNDB1`/`SNDB2`/`SNDA2`
runs) with one retry allowed. Also found and discarded: `SNDA1`'s own two collection attempts, VOID
per `tests/harness/results/SNDA1-2026-09-22-VOID/VOID.txt` (wrong un-pinned binary, then a self
tag-collision) -- neither reused past this point.

**Step 6 closed.** GUS PCM audio is free at 40fps on this fixture; no fps-cost tradeoff exists for
the "sound on" question this step was scoped to answer.

## Next campaign (operator direction 2026-09-22): Sound Blaster first, then Maniac Mansion Deluxe at full speed

**Operator direction, 2026-09-22.** Sound Blaster support is what most players will use, so it is tested
next, music and SFX both. After that, Maniac Mansion Deluxe runs at full speed and fps. Work order
step 7 (ViRGE and Cirrus) moves behind both. Every earlier figure in this file was taken with sound
off; the GUS work (S7-GUS, step 6) does not speak for Sound Blaster.

**What we already know, and why it is not enough (coordinator read, 2026-09-22):**
- All four in-profile titles (Trilby's Notes, 5 Days a Stranger, 7 Days a Skeptic, Maniac Mansion
  Deluxe) play **MIDI music plus WAV SFX** (their `inspect-report.json`). On a Sound Blaster the music
  goes out as **OPL3 FM** or, with a wavetable daughterboard, **MPU-401 / WaveBlaster**.
- Those are exactly the two paths that were **waived** on 2026-09-15 (PLAN-LOG "S7 -- acceptance gate
  decision"). Two things were measured: opening the SB device cost ~5x, and touching any MIDI backend
  cost ~10-12x (NOBK1, SILNT1, SUBSY1/2, TNWB1). Both were blamed on "a hardware/electrical constant of
  the PicoGUS running SB emulation".
- **That attribution was never tested, only inferred.** Every one of those cells ran (a) on the
  **PicoGUS** (PGSB), never on a real Creative card; (b) at the **old ~3-5 fps regime**, on a binary
  from before patch 0096 replaced `Clock::now()` (1,324 us per call, `mktime` inside) and the pacer,
  and before every present-path change since. A software cause that interacts with timer/IRQ activity
  was not ruled out by any cell on a current binary.
- The target has a **real Creative Vibra16S** (SB16 class, IRQ 5, 16-bit DMA 5, onboard OPL3 via
  UNISOUND), boot profile 4 `VIBRA`, which no dosags cell has ever used. A DreamBlaster S2 at 330h is
  reachable from both `PGSB` and `VIBRA` (`~/git/g2k/README.TXT`, SOUND CARD ENVIRONMENT).
- Maniac Mansion Deluxe's only real-hardware figure (S2M1, 6.84 fps, steady 28.34) is its
  **character-select screen**, not gameplay. It ran on the **pre-0196 binary with no alias**, and its
  attribution (`tickstats_process_events_dispatch` 26.47 ms/tick, with `render_to_screen` 18.50 ms
  nested inside it) is a reading, not a measurement of what runs inside dispatch.

**Binary for this whole campaign:** a clean build of the current head (0197), `build_dirty=0`, pinned
by `binary_sha12` in step 8.0. Its sound-off arm doubles as the missing rate check for 0197 (Gate 3 was
claimed on 0196).

### Step 8: Sound Blaster, music and SFX

**Lanes, in priority order:**
1. **`VIBRA` (real SB16)**: this is what "Sound Blaster support" means for most players. SFX = SB16
   PCM; music = **OPL3 FM** (the default for SB owners; most have no wavetable board), then
   WaveBlaster.
2. **`PGSB` (PicoGUS, SB 2.0 class, 8-bit DMA)**: emulation, secondary. Also the lane where the old tax
   was seen.
3. `PGADLIB` (OPL2 only, no SFX by design): one correctness cell, no rate work.

Coverage limit, stated up front: this machine has one real SB16 and one SB 2.0-class emulation. SB Pro
and clone chipsets (ESS, Aztech, OPTi) are not testable here, and nothing below claims them.

**8.0 -- Prerequisites (no rate claims).**
- Build and pin the binary.
- Confirm from source (not from this plan) which `SDL_HINT_DOS_AUDIO_BACKEND` values select OPL3 and
  WaveBlaster, and that `[sound] enabled=1` plus the backend hint is the whole lever.
- Confirm the **audio capture device hears the Vibra's line-out**, not only the PicoGUS's
  (`vcctrl_audio_state` during a known sound). If it doesn't, stop and ask: moving a cable is a
  physical action for the operator.
- `VIBRA` puts the PicoGUS in USB mode and adds a CD drive, so check `run-hw.sh`'s staging and drive
  letters under profile 4 before the first cell.
- If the DreamBlaster is silent on `VIBRA`, the card mixer may need `MIXERSET` once. That is a
  persistent card-state change: ask first.

**8.0 record (2026-09-22, worker).**
- *Binary pinned:* clean build of head (vendor/ags `e622baaa8` = `export-0197`), `make build-dirty` ->
  `build_dirty=0 sha12=4b621d0350d4`, staged as `build/abba/ags-0197-clean.exe` (sha256 `92314931...`).
  Differs from `build/abba/ags-0197.exe` in 11 bytes only: the stamp and the dirty flag (that file is
  `4a6da6186078`, `build_dirty=1`; see the DUPCHAR3 correction below).
- *Source, the whole lever:* `[sound] enabled` -> `setup.AudioEnabled` (`Engine/main/config.cpp:416`);
  audio init only under it (`Engine/main/engine.cpp:401`). PCM: `SDL_HINT_DOS_AUDIO_BACKEND=gus` selects
  GUS PCM, anything else opens SDL's default playback device = the SB driver
  (`Engine/platform/dos/dos_audio_mixer.cpp:129,166`; `sys_main.cpp:366`), which finds the card only via
  the `BLASTER` string (`vendor/SDL/src/audio/dos/SDL_dosaudio_sb.c:4606`). MIDI: no hint = `"auto"`
  (`dos_midi_backend.cpp:58`), and `auto` or `opl3` -> OPL3 probe + `OPL3BANK.DAT` (`:122`); `wb` ->
  MPU-401 via cold init before the PCM device opens (`:71`, `:101`, called at `sys_main.cpp:325`);
  `none` -> no probe (`:97`); `gus` -> GF1 (`:145`); anything else (incl. `adlib`) -> MIDI disabled.
  **Default under a BLASTER string with no hint: SB PCM + OPL3 music.** `DOSAGS_MIDI_NO_BACKEND=1`
  (`Engine/media/audio/audioplayer.cpp:75`) skips only `dos_midi_backend_open()`; `midi_sched` and the
  MIDI-clip machinery still run -- so 8.2's arm B is "PCM + generic MIDI machinery, no backend", not
  "SB PCM alone".

**2026-09-22 -- PRE-REGISTRATION, capture probes `SBCAP1` (VIBRA, profile 4) and `SBCAP2` (PGSB,
profile 1, control). Probe cells, no rate claims.** Pinned binary, 5 Days a Stranger NATURAL flow (its
intro rooms 1-2 play MIDI music with no input), `games/5days/ACSETUP-ON.CFG` (`[sound] enabled=1`), no
backend hint (= SB PCM + OPL3, per the source read above), `DOSAGS_TAS_AUTO_EXIT_TICK=1600`,
`--boot-profile 4` / `1`. A background sampler logs `vcctrl level 2000` + `spectrum 2000` every ~3 s
for the whole cell. **Heard** = during the game, mean level >= 10 dB above the idle floor (idle
2026-09-22: mean -67.6, peak -50.9 dBFS, 0/8 bands) with >= 2 active bands in several consecutive
samples. **Also checked:** STDOUT/RUNMANI show the lane's BLASTER string (VIBRA `A220 I5 D1 H5 T6
P330`), `audio_vital_status` device open with OPL3 active, staging to `C:\DOSAGS` and collection work
under profile 4. **If SBCAP1 is not heard: stop and report** (cable is the operator's call; no MIXERSET,
no config change). SBCAP2 not heard either would point at the capture chain, not the Vibra.

**2026-09-22 -- SBCAP1 / SBCAP2 RESULT: step 8 STOPPED at 8.0 -- the Vibra16S is not detected at
all, so the capture question for it cannot be asked yet.** Both cells: pinned binary
(`binary_sha12=4b621d0350d4`, `build_dirty=0`), exit_code=0, `ENGINE HAS SHUTDOWN`, natural flow to
room 2; profile select landed on attempt 2/3 in both (attempt 1 missed; its late digit bursts show up
as harmless `C:\>4 / Bad command or file name` lines at the prompt).
- **SBCAP1 (VIBRA, profile 4):** the profile landed (`[VIBRA] ready`, PicoGUS rebooted to its USB
  firmware; camera `results/SBCAP1-2026-09-22/VIBRA-boot-camera.jpg`). **UNISOUND printed "No PnP card
  detected."** The engine then failed audio init: `Failed to init SDL audio subsystem: Not a
  SoundBlaster at port 0x220 (last DSP read 0xFF, expected 0xAA)`; `audio_vital_status=NA`. Capture
  silent throughout (`LEVEL.log`: 309 samples, 0 active bands in all, mean/peak at the idle floor).
  Staging to `C:\DOSAGS` and collection both worked under profile 4; CD drives come up on **D: and
  E:** (MSCD000 and OPTICAL), C: unchanged.
- **SBCAP2 (PGSB, profile 1, control): HEARD.** `DOS audio device opened: pcm=sb@11025m16,...`,
  `DosMidiBackend: OPL3/OPL2 chip detected and initialized`,
  `audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=2534`. `LEVEL.log`: 44
  samples at 6-7 active bands, mean -43 to -34 dBFS, peak -30 to -21 (floor -68 / -51), continuous
  12:47:08-12:48:15 during the intro music. The capture chain works; the problem is upstream of it,
  on the Vibra.
- **Reading (hypothesis, not tested):** the Vibra16S is a PnP card that UNISOUND could not find --
  not seated, disabled, or needing a different init than `UNISOUND.COM /V80` -- and with no PnP
  configuration it answers nothing at 220h. Whether its line-out reaches the capture device is still
  unknown. **Operator's call (physical/config):** no MIXERSET, no UNISOUND/CONFIG change, no cable
  move made. 8.1 (local DOSBox-X) and the 8.2 draft are not started.

**8.1 -- Correctness on DOSBox-X (local, no hardware).** On the pinned binary, for SB16 + OPL3 and SB16
+ MPU-401: run the AGS Quest harness (its deterministic MIDI tune and CC0 chime) and 5 Days in play.
Bar: `audio_vital_status` shows the device open, MIDI events dispatched, zero underruns, exit 0. This
only proves the paths run; DOSBox-X audio timing is not evidence about hardware.

**Operator decision, 2026-09-22 (question tool): "PGSB now, Vibra later".** The `VIBRA` lane is
PENDING the operator sorting out the card (SBCAP1: UNISOUND "No PnP card detected", DSP 0xFF at 220h).
It is **not waived**; the real-SB16 gap stays open. 8.2 runs on `PGSB` (profile 1) first, once 8.1
passes.

**2026-09-22 -- 8.1 RESULT (DOSBox-X, local): FAILS its bar on 5 Days (underruns); AGS Quest passes.
Stopped here per the dispatch -- 8.2 not pre-registered, not run.** Pinned binary (`binary_sha12=
4b621d0350d4`, `build_dirty=0`; run as a byte-identical copy named `AGS.EXE`, because
`run-dosbox.sh` stages the exe under its own basename and `ags-0197-clean.exe` is not 8.3 with LFN
off -- the first attempt failed `Bad command or filename`, no engine ran). Confs:
`confs/dosbox-x-fast-opl3.conf` (SB16 + OPL3, no hint) and the new `confs/dosbox-x-fast-mpu401.conf`
(same + intelligent MPU-401 at 330h, `mididevice=none`; hint `wb`). Raw:
`tests/harness/results/SB81-2026-09-22/`.

| run | `audio_vital_status` | exit | bar |
|---|---|---|---|
| AGS Quest, OPL3 | `pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=25` | 0 | PASS (autopilot `audio` phase ok, tick 3144-3564) |
| AGS Quest, MPU-401 | `pcm=sb@11025m16,voices=8,underruns=0;midi=wb,events=27` | 0 | PASS (same) |
| 5 Days in play, OPL3 | `pcm=sb@11025m16,voices=8,underruns=8;midi=opl3,events=1617` | 0 | **FAIL: underruns=8** |
| 5 Days in play, MPU-401 | `pcm=sb@11025m16,voices=8,underruns=12;midi=wb,events=1622` | 0 | **FAIL: underruns=12** |

5 Days cells: `--fixed-timestep`, `--startr 3`, 2000 ticks, the new
`presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG` (the Gate 3 pillarbox cfg with `[sound]
enabled=1`; the only diff), mode `512 x 384 (16-bit)`, alias ON x=96 y=72, `Now in room 3`,
presentverify `stale_frames=0` (1992 / 1999 frames). Both backends opened as designed (`OPL3/OPL2
chip detected and initialized`; `WaveBlaster/MPU-401 cold-init succeeded (ran before the PCM device
opened, as required)` then `backend active`).
*Fact:* the counter (`Engine/platform/dos/dos_audio_mixer.cpp:349`) increments once per mix chunk in
which some active voice's ring was empty -- a streamed voice ran dry. No per-event log exists, so
when and which clip is not known from these files.
*Not known (not tested, no rerun per the stop rule):* whether this is a DOSBox-X `cycles=max` timing
artifact or a real stream-feed shortfall, and whether `--fixed-timestep` matters (AGS Quest ran
without it; the 5 Days cells with it). DOSBox-X audio timing is not hardware evidence either way.

**2026-09-22 -- PRE-REGISTRATION, local underrun investigation `UR1` (DOSBox-X only, bounded ~1 h,
no fix).** *Source read first (gating code, not names):* the mixer's `underruns` counter
(`Engine/platform/dos/dos_audio_mixer.cpp:316-351`) increments once per 512-sample mix chunk (~46 ms)
in which an **active voice's own software ring is empty** -- it is NOT the SB device running dry.
Everything that feeds or mixes voices runs in the main loop: `audio_core_entry_poll()` polls each
slot, `AudioPlayer::Poll()` hands the voice **at most one decoder buffer per call**
(`Engine/media/audio/audioplayer.cpp:180-189`), then `dos_audio_mixer_pump()` (`audio_core.cpp:863`)
mixes **up to 8 chunks** until the SDL stream holds 186 ms (`dos_audio_mixer.cpp:74-77,383-392`) and
calls `SDL_DOSAudioPump()`, which moves stream data into the SB ISR ring. The SB IRQ
(`vendor/SDL/src/audio/dos/SDL_dosaudio_sb.c:1737-1790`) copies from that ring into the DMA half-buffer
and, if the ring is short, plays **silence** and counts `dos_port_audio_silent_irq_count` -- a separate
counter from `underruns`. So during a stall the device can go silent once the ISR ring and DMA
buffers run out, and that gap is invisible to `audio_vital_status`.
**Hypotheses:** *H-stall (coordinator's):* underruns coincide with stall ticks (within the stall
tick or the next one); falsified by underruns spread across steady ticks. *H-refill (refinement from
the source, tested by the same probe):* the mechanism is the first pump after a stall, which mixes
several chunks to refill 186 ms while each voice received only one decoder buffer that poll, so the
voice ring empties mid-refill; predicts underrun lines carry a multi-chunk `iter` index (>= 1) at the
tick after a stall. *Other readings the probe can see:* clip start (voice active with an empty ring
before its first write) or clip end (voice still active after its data is consumed) -- both would put
underruns at clip boundaries in steady ticks.
**Probe (throwaway, reverted after, diff kept):** logs every underrun (loop tick, uclock ms, voice,
ring bytes, the pump iteration and stream bytes queued at pump entry); every multi-chunk pump; every
voice write (bytes) and activation/stop; once, the ISR ring capacity in ms and the DMA physical
capacity. Rerun 5 Days OPL3 exactly as SB81. **Zero-code controls, pinned binary:** 5 Days OPL3
without the fixed timestep, and AGS Quest OPL3 with it.

**2026-09-22 -- UR1 RESULT, pending coordinator verification: the 5 Days underruns are clip-end
accounting, not stalls and not audible gaps. H-stall and H-refill both FALSIFIED.** Raw:
`tests/harness/results/UR1-2026-09-22/` (probe run, controls, `ur1-probe-throwaway.diff`,
`probe-5days-opl3-fixed/UR1-events.txt`).
- *Probe run* (probe build `9d35a069420f`, `build_dirty=1`, never a gate binary; 5 Days OPL3 exactly as
  SB81): `underruns=16;midi=opl3,events=1617`, exit 0. All 16 logged. Only one stall in this run
  (`stallwhat tick=1 self_ms=488`).

  | underrun ticks | voice | clip written (voice 0) | what precedes it |
  |---|---|---|---|
  | 76 (x4) | 0 | ticks 75-76: 4096 + 3690 B (~353 ms) | whole clip written, then drained |
  | 280 (x4) | 0 | ticks 279-280: same ~353 ms clip | same |
  | 1025 (x4) | 0 | tick 1023: 8 x 4096 + 3514 B (~1.13 s) | same |
  | 1525 (x4) | 0 | tick 1523: same ~1.13 s clip | same |

  Every underrun is `iter=0` on a one-chunk pump (`queued_in=3072`), four consecutive pumps within
  ~4 ms of each other, **after the clip's last byte was written and consumed and before the voice was
  released** (no stop/deactivate line; the voice is freed when the player finishes). None is at a stall
  tick, none mid-clip, none on a multi-chunk refill.
- *Mechanism (source + log):* the mixer drains a voice as fast as the device side accepts data, so a
  clip's ring empties well before its sound finishes playing out of the device ring; from then until
  `AudioPlayer::Poll()` sees `EOS && IsEmpty` and the slot releases the voice
  (`Engine/media/audio/audioplayer.cpp:192`), each pump mixes a chunk from an active, empty voice and
  `mix_one_chunk()` counts it (`dos_audio_mixer.cpp:316-351`). The counter therefore includes every
  clip's normal tail. It is not a measure of audible dropouts.
- *Buffer cover:* SB ISR ring capacity **743 ms** (`SDL_DOSAudioRingCapacityMs`); physical capacity
  **9216 frames** (~836 ms at 11025 Hz); mixer stream target 4096 B = **186 ms** (4 chunks of 1024 B /
  46 ms). A main-loop stall longer than roughly ring fill + DMA half-buffers would starve the device;
  that shows up in `dos_port_audio_silent_irq_count` (silent IRQs), not in `underruns`.
- *Feed path, answered from source:* all voice feeding and mixing is **main-loop only**:
  `audio_core_entry_poll()` -> `AudioPlayer::Poll()` (one decoder buffer per call,
  `audioplayer.cpp:180-189`) -> `dos_audio_mixer_pump()` (`audio_core.cpp:863`; mix to 186 ms, then
  `SDL_DOSAudioPump()` into the ISR ring, `dos_audio_mixer.cpp:383-395`). The SB IRQ handler only
  copies ISR ring -> DMA half-buffer and plays **silence** when the ring is short
  (`vendor/SDL/src/audio/dos/SDL_dosaudio_sb.c:1737-1790`). So yes: during a stall the IRQ keeps
  pulling from a ring that nothing refills, and it can run dry -- but that is a different event from
  the one counted here.
- *Zero-code controls, pinned binary `4b621d0350d4`:* 5 Days OPL3 **without** fixed timestep:
  `underruns=15;midi=opl3,events=1625`. AGS Quest OPL3 **with** fixed timestep:
  `underruns=0;midi=opl3,events=25`. Fixed timestep is not the confound.
- *Open, not explained:* why AGS Quest's chime ends with 0 (possibly its clip ends on a chunk boundary
  or its slot is stopped differently -- not checked); run-to-run count varies (8, 15, 16) with how many
  pumps land between drain and release. `SDL_DOSAudioRingFillMs` rose past its own 743 ms capacity
  during the run (232 -> 4086), suggesting the ISR read cursor does not advance as expected under
  DOSBox-X -- noted, not chased (DOSBox-X audio timing is not hardware evidence).
- *Consequence for the 8.1 bar (coordinator's call):* `underruns=0` cannot pass for any title whose
  SFX end during the run. An audibility bar would read silent IRQs during active playback instead.
  Probe reverted; `vendor/ags` clean at `export-0197`; the clean rebuild is **byte-identical** to
  `build/abba/ags-0197-clean.exe`. No fix written.

**2026-09-22 -- 8.1 BAR CORRECTION (coordinator decision, after verifying UR1).** 8.1 is
**re-scored PASS for 5 Days.** Reason: `underruns` counts clip-end drain (an active voice with no
bytes left, `dos_audio_mixer.cpp:316-349`, UR1), so "underruns=0" was the wrong bar for any game whose
SFX end during the run. The measured values stand as recorded (SB81: 8 OPL3 / 12 MPU-401; UR1: 15
no-fixed-timestep, 16 probe). AGS Quest's 0 is unexplained; noted, not chased. The audible-gap
judgement moves to real hardware: the capture (LEVEL / active bands, then 8.3's analysis) is the
judge. `dos_port_audio_silent_irq_count` is NOT reported by the pinned binary (nothing in
`vendor/ags` reads it), so a silent-IRQ bar needs code -- see the work item below.

**Work item, BEFORE 8.3 (not now; the 8.2 binary stays pinned at `4b621d0350d4`): a small audio
reporting patch series, one concern per patch.** (a) count an underrun only when the voice's source
has not reached end of data (mid-clip starvation); (b) report `silent_irq_count` -- the delta while
any voice is active -- in `audio_vital_status`; (c) explain the DOSBox-X ISR ring fill exceeding its
743 ms capacity (UR1: 232 -> 4086 ms) by reading the ring math -- a counter bug, or real overwrite
of unplayed audio.

**Arm B' (MIDI clips not played at all) -- no zero-code lever exists.** `[sound]` reads only
`enabled`, `driver`, `usespeech` (`Engine/main/config.cpp:416-418`); music master volume is set to 100
at init (`Engine/main/engine.cpp:859`) and changed only by game script. The two env levers do not
qualify: `DOSAGS_MIDI_NO_BACKEND=1` still plays clips through `midi_sched` (`audioplayer.cpp:75`), and
`DOSAGS_MIDI_SILENT_CHIP` programs the chip with no notes (`audioplayer.cpp:160`). A B' arm would need
code; not invented here.

**8.2 -- Re-baseline the old tax on the current binary (the question everything else depends on).**
Fixture: **the Gate 3 cell exactly** (5 Days in play, `--startr 3`, drive-walk 2 s, 512x384 centred
1x, alias on), with sound switched by config only. Screening, one cell per arm, per lane:

| arm | what it isolates |
|---|---|
| A: sound off | baseline (0197 rate check) |
| B: SFX only, `DOSAGS_MIDI_NO_BACKEND=1` | SB PCM device cost alone (old "~5x" factor) |
| C: SFX + OPL3 music | the real SB-owner configuration |
| D: SFX + WaveBlaster music | the wavetable owner |

That makes 8 screening cells (4 arms x `VIBRA` + `PGSB`), each with its own new tag and every usual
VOID condition. Pre-register, **before any cell**: the band each arm is expected to land in, plus both
hypotheses. H1 says the tax is PicoGUS-specific (`VIBRA` C/D near A, `PGSB` C/D far below). H2 says a
software cause, since fixed (both lanes near A). A third reading is also possible: both lanes show the
tax, so it is software, it still exists, and it is not PicoGUS.

**2026-09-22 -- PRE-REGISTRATION, 8.2 screening, PGSB lane (profile 1). NOT YET RUN.** The `VIBRA`
lane is **pending operator: card not detected (SBCAP1)**. Binary: pinned
`build/abba/ags-0197-clean.exe`, expected `binary_sha12=4b621d0350d4`, `build_dirty=0`. Fixture: the
Gate 3 cell exactly -- `AGS_EXE=$REPO/build/abba/ags-0197-clean.exe ./run-hw.sh 5days --tag <TAG>
--timeout 1800 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg
--startr --ags-arg 3 --extra-file $REPO/tests/harness/presentation/trilbysnotes/<CFG>:ACSETUP.CFG`, with
`./drive-walk.sh <TAG> 25 2 90` alongside. No `--boot-profile`: the machine lands on its menu default,
PGSB, after the transfer, exactly as S2F2/S2F3 did (and it avoids the blind digit burst that left
stray `4`s at the prompt in SBCAP1/2). Sound switched by config and env only:

| tag | arm | cfg | extra env |
|---|---|---|---|
| SB2A1 | A: sound off (also the 0197 rate check) | `ACSETUP-OFF-512X384-ROUND.CFG` | -- |
| SB2B1 | B: SB PCM + MIDI machinery, no backend | `ACSETUP-ON-512X384-ROUND.CFG` | `DOSAGS_MIDI_NO_BACKEND=1` |
| SB2C1 | C: SFX + OPL3 music (no hint) | `ACSETUP-ON-512X384-ROUND.CFG` | -- |
| SB2D1 | D: SFX + WaveBlaster music | `ACSETUP-ON-512X384-ROUND.CFG` | `SDL_HINT_DOS_AUDIO_BACKEND=wb` |

Run in that order, one cell each. No B' (it needs code).
**Profile landing confirmed by:** camera frame 1 showing `[PGSB] ready`; `env_block_sha` -- `BLASTER`
is in the hashed allowlist (`Engine/main/quit.cpp:379`), so A must reproduce S2F2/S2F3's
**`459dcb815359`** (same BLASTER, same two DOSAGS vars); B and C will hash alike (neither
`DOSAGS_MIDI_NO_BACKEND` nor `ACSETUP.CFG` is hashed), D differs (hint hashed). B/C/D also need
`DOS audio device opened: pcm=sb@...`.
**Expected bands.** A: both tick figures 39.2 - 40.8, `fps_p50` >= 40, completeness >= 95%, stable rate
~39.46 (S2F3). For B, C, D, against A's stable rate: **"near A"** = both tick figures in 39.2 - 40.8
and stable rate within 1.0 of A; **"far below"** = stable rate <= A/2 (a >= 2x slowdown; the old tax
was 5x for the SB device and 10-12x with any MIDI backend); **"partial"** = anything between.
**Readings:** *H1* (PicoGUS-specific): C/D far below A on PGSB. *H2* (a software cause, fixed since):
C/D near A. *H3* (software, still present, not PicoGUS-specific) also predicts C/D far below on
PGSB, so **PGSB alone cannot separate H1 from H3**; that needs the Vibra lane. "Near A" refutes H1 and
H3 as far as PGSB is concerned. "Partial" is recorded as its own reading (a smaller tax than the
old one), not a contradiction. B against A isolates the PCM + MIDI-machinery cost; C/D against B
the backend's.
**Per cell:** new tag; `audio_vital_status` (underruns recorded as-is, **includes clip-end drain,
UR1**); `vcctrl` LEVEL/spectrum sampler running alongside every sound-on arm (B/C/D) and A (as the
silent reference); camera frames reviewed frame by frame (the `--startr` two-figure beat is expected,
DUPCHAR4). D: if WaveBlaster cold-init declines (no MPU at 330h), the cell is recorded as "wb
unavailable", not VOID.
**VOID if:** `binary_sha12` is not `4b621d0350d4` or `build_dirty` != 0; the mode line is not `512 x
384 (16-bit) fullscreen`; the alias line is missing; `Now in room 3` not reached; more than one
manifest block; an SDL trace collected; the tag was reused; A's `env_block_sha` differs from
`459dcb815359`; the profile did not land on PGSB. **Stop if:** any VOID; the profile won't land; the
post-collection hang recurs twice in one cell; any arm crashes or hangs the target; a result
contradicts all pre-registered readings. Results written as "RESULT, pending coordinator
verification"; no gate claims.

**2026-09-22 -- 8.2 PGSB SCREENING RESULT, pending coordinator verification. No VOID, no stop
condition hit. All three sound-on arms land in the pre-registered "partial" zone: steady rate
unchanged, whole-run below band from extra stalls -- nowhere near the old 5-12x tax.** Raw:
`tests/harness/results/SB2{A,B,C,D}1-2026-09-22/` (RUNMANI, STDOUT, LEVEL.log, witness sheets). All
four: `binary_sha12=4b621d0350d4`, `build_dirty=0`, exit_code=0, one manifest block, no SDL trace,
`512 x 384 (16-bit) fullscreen`, alias ON x=96 y=72, `Now in room 3`, profile landed on PGSB (camera
frame 1 `[PGSB] ready` in every cell; A reproduced `env_block_sha=459dcb815359`, B and C hash alike
as predicted, D differs as predicted: `8275d60e29c9`); collection reboots witnessed, no hang.
Order A, B, C, D, 13:15-13:51 PDT.

| cell | arm | steady | whole-run | stable | `fps_p50` | presents/passes | frames_skipped | stalls | `audio_vital_status` |
|---|---|---|---|---|---|---|---|---|---|
| SB2A1 | A sound off | 40.03 | **39.18** | 39.57 | 40.00 | 4955/4943 | 57 | 3 | `NA` |
| SB2B1 | B PCM + MIDI machinery | 40.18 | 38.66 | 39.15 | 40.00 | 4884/4872 | 128 | 10 | `pcm=sb@11025m16,voices=8,underruns=77;midi=none,events=0` |
| SB2C1 | C OPL3 | 39.89 | 38.61 | 38.96 | 40.00 | 4895/4883 | 117 | 7 | `pcm=sb@11025m16,voices=8,underruns=76;midi=opl3,events=4542` |
| SB2D1 | D WaveBlaster | 39.98 | 38.64 | 38.98 | 40.00 | 4887/4875 | 125 | 7 | `pcm=sb@11025m16,voices=8,underruns=74;midi=wb,events=4534` |

`underruns` **includes clip-end drain (UR1)**. Stable = steady x (1 - frames_skipped/4999).
*Against the pre-registration:*
- **A** (0197 rate check) **misses its own band on whole-run by 0.02** (39.18 vs 39.2): it has one
  stall more than S2F2/S2F3 (tick 1187, 251 ms) besides the same tick-1 (765 ms) and ~319 ms ones.
  Steady, `fps_p50`, completeness all in. Gate 3's 0.04-0.06 margin does not absorb one extra
  quarter-second stall.
- **B, C, D: "partial"** by the pre-registered definitions -- stable within 1.0 of A (-0.42, -0.61,
  -0.59) but whole-run out of band; nothing near "far below" (<= 19.8). The old tax (5x SB device,
  10-12x any MIDI backend) is **not present on PGSB on this binary**, so on this lane H1 is refuted as
  stated (PicoGUS SB emulation does not collapse the rate) and H3 is not supported here -- but H3
  remains untestable without the Vibra, as pre-registered. H2 is closest, with a residual.
- **Where the residual sits (fact):** steady-state is unchanged (39.89-40.18 vs 40.03); the loss is
  in stalls -- `frames_skipped` roughly doubles (57 -> 117-128), stall count 3 -> 7-10, the room-load
  stall grows (765 -> 924-1007 ms), and B shows a ~300 ms stall every 500 ticks (2457/2957/3457)
  that A does not. *Hypothesis, untested:* sound-on stalls are clip loads / audio init work in the
  main loop. B vs C/D: the MIDI backend adds ~0.2 stable on top of PCM + machinery; OPL3 and WB cost
  the same within one cell each.
- **Capture: SILENT in every sound-on cell** -- 0 active bands in all samples (B 329, C 328, D 329),
  max mean -67.65 dBFS / max peak -49.56, the idle floor; the capture chain was alive (checked after
  C, and SBCAP2's music is in its own log). So on the Gate 3 fixture, neither the SB PCM SFX (clips did
  play: 74-77 clip-end drains) nor OPL3 (4542 events) nor WaveBlaster (4534 events) music reached the
  capture, while SBCAP2 (natural intro flow, rooms 1-2, default 640x480 cfg, no drive-walk) heard OPL3
  clearly on the same profile. *Not known:* whether room 3 under `--startr 3` actually sounds (the
  DUPCHAR4 lesson: the jump skips rooms 1-2 state), whether its music is simply quiet, or whether SB
  PCM is audible on PGSB at all (never yet seen in a capture). This does not change the rate readings
  (the dispatch work was done either way) but it **blocks 8.3** until explained.
- *Witness:* camera frames 1-25 reviewed per cell; frame 3 is the known `--startr` beat in each
  (caught at different points of the climb), frames 4-16 one complete figure each, walking blur only
  (A 7/13, C 5, D 13); 17-25 after exit. No trails, stale sprites or tearing.

**2026-09-22 -- PRE-REGISTRATION, probe cell `SBCAP3` (PGSB, pinned binary). NOT YET RUN.**
Coordinator's diagnosis of the silent 8.2 capture: vcctrl's audio device (`hw:CARD=U0x010xff02`) is
the same MacroSilicon ff02 USB dongle as the VGA capture, which cannot lock 512x384 (black card frames
in every 512x384 cell); SBCAP2 was heard at the default rung (`games/5days/ACSETUP-ON.CFG`, no
`[graphics]`), and the post-C "capture alive" check was at the DOS prompt. The two sound-on cfgs
differ only in `[graphics]`. **Hypothesis:** the dongle drops or mutes audio when it has no video
lock. **Cell:** SB2C1's command (`--startr 3`, OPL3, no hint, `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`,
landing on the PGSB default) with `games/5days/ACSETUP-ON.CFG` instead of the 512x384 cfg,
`DOSAGS_TAS_AUTO_EXIT_TICK=1600`, **no drive-walk**, LEVEL sampler on; card lock read from
run-hw.sh's own card witness frames and `card-state.log` during room 3. **Heard** = active bands >= 2
in several consecutive samples during room 3 -> confirms capture lock as the cause, and that room 3's
music/SFX do play. **Silent** -> the capture-lock hypothesis is refuted; the `--startr`/room-3 music
question is live again; report and stop. One cell, no fix, no config change.

**2026-09-22 -- SBCAP3 RESULT, pending coordinator verification: HEARD. The capture-lock hypothesis
is confirmed -- the 8.2 silence was the ff02 dongle having no video lock at 512x384, not room 3.**
Pinned binary (`4b621d0350d4`, `build_dirty=0`), exit_code=0, `ENGINE HAS SHUTDOWN`, PGSB default,
`Graphics mode set: 640 x 480 (16-bit) fullscreen desktop`, `Now in room 3` (via `--startr 3`),
`env_block_sha=28d00ba91ee7`, `audio_vital_status=pcm=sb@11025m16,voices=8,underruns=2;midi=opl3,
events=2407` (underruns include clip-end drain, UR1). Raw: `tests/harness/results/SBCAP3-2026-09-22/`.
- *Level (LEVEL.log):* 42 samples at 6-7 active bands, **consecutive** 13:57:17 -> 13:58:21 (every
  ~1.5 s sample in that span), mean -46.6 to -32.8 dBFS (floor -68), 267 samples silent outside it
  (transfer, boot, exit).
- *Card lock:* `card-state.log` 70 `locked` / 2 `frozen` / **0 `nosignal`** (SB2C1 at 512x384: 57
  `nosignal`); card frames 00003-00009 (13:57:22-13:58:17) carry picture (mean 0.056-0.064) -- the same
  span as the heard audio -- and `witness/frames/00006_135750.093.jpg` shows room 3 in play at 640x480
  (verb bar "Desk"); 00010 on is the exit mode switch.
- *Reading:* room 3's music plays under `--startr 3`, and the capture hears it when the dongle has
  lock. Every 512x384 cell's audio capture (8.2 B/C/D) is therefore blind, not evidence of silence.
  Whether this is the dongle muting without lock or dropping the stream is not distinguished. SB PCM
  SFX audibility is still not separately shown (music dominates the bands). Consequences (a separate
  audio input, or audio cells at a lockable rung) are the operator's decision. No fix, no config
  change.

**Operator decision, 2026-09-22 (question tool): "640x480 now, USB audio later".** Rate cells stay
at 512x384; audio-correctness cells (8.3) run at 640x480, which the ff02 dongle locks. Separately, the
operator will add a standalone USB audio input for the card's line-out and vcctrl will be pointed at
it; after that, rate and audio can be judged in the same cell.
**Capture blind, no video lock:** the `LEVEL.log` of every 512x384 cell -- SB2A1, SB2B1, SB2C1, SB2D1
(and any earlier 512x384 cell with a level log) -- is **not evidence of silence**; the dongle has no
video lock at 512x384 and its audio went with it (SBCAP3). Only SBCAP2 and SBCAP3 (default 640x480
rung) are valid audio captures on this lane so far.

**2026-09-22 -- Pre-8.3 audio reporting, slice 1 (worker). Patches 0198 and 0199 written; (c) read
from source and STOPPED before any fix, per the dispatch.**
- **ags 0198** (`vendor/ags` `export-0198`): `underruns` now counts only **mid-clip starvation** -- an
  active voice whose ring is empty while its source is NOT done (`source_done` = decoder EOS and no
  buffer pending, set each `AudioPlayer::Poll()` via `OpenAlSource::SetSourceDone`, cleared by
  `voice_stop`). An empty voice whose clip ended counts as **`drains=`**, a new field; per chunk a
  starving voice wins, so `underruns + drains` equals the pre-0198 count. GUS path unchanged (drains
  stays 0). *Field check (what it prints if starvation happens, and the path that lets it):* the
  decoder hands out 2048-sample slices (`sdldecoder.cpp:34`), one per `Poll()`; a pump that mixes
  more than 4 chunks of 512 for one voice empties its ring while `EOS()` is false -> `underruns++`
  in `mix_one_chunk()`. Probe `UR2` (below) forces exactly that.
- **ags 0199** (`export-0199`): `audio_vital_status` gains **`play_irqs=`** and **`silent_irqs=`**:
  the SB driver's `dos_port_audio_irq_count` / `dos_port_audio_silent_irq_count` deltas, charged only
  over pump intervals that began with a voice still playing (active, and not `source_done` with an
  empty ring). *What increments silent_irq (read, `SDL_dosaudio_sb.c:1759-1789`):* every SB IRQ that
  finds `isr_ring_write - isr_ring_read < isr_chunk_size` -- it memsets the DMA half to silence; it
  does not distinguish idle from starved, hence the play window. `play_irqs` exists so that
  `silent_irqs=0` can be told apart from an IRQ that never fired. **GUS:** no SDL device and no
  silent-IRQ equivalent (its missed-swap count is what `underruns` already sums), so both print `NA`.
- *Build and gate:* both build clean. `gate-alias.sh` on the 0198 binary: **13/14 rows clean, 0
  regressions, every control fails as required**; the one failing row is `shards-alias-512x384`,
  tick 100 only, bbox `(512, 513, 1152, 913)` -- the pre-existing title-screen defect, same bbox as
  recorded for 0197. Raw: `tests/harness/results/AR1-5days-opl3-2026-09-22/gate-alias-0198-summary.txt`. 0199 gate: 13/14, same single pre-existing row (see AR1 result below).
- *Review (`/sdldos:review`):* real `git format-patch` output (bodies byte-equal to `export-0198/9`
  after `make patches`), next free slots 0198/0199, ASCII-only, no `fopen`, no SIMD, no size_t
  assumptions beyond 32-bit, port-owned names; permanent reporting, not a temporary diagnostic.
- **(c) the ring fill past capacity (UR1: 232 -> 4086 ms, capacity 743): REAL OVERWRITE of unplayed
  ring data, not a counter bug. Read from source; NOT fixed; stopped per the dispatch.**
  1. The fill is `isr_ring_write - isr_ring_read`, both monotonic (`SDL_dosaudio_sb.c:1103`). Above
     `ring_size` it means the writer has lapped the reader: the bytes at `read & mask` are newer data.
     There is no reporting path that could inflate it (no reset asymmetry; the only cursor collapse,
     `SDL_DOSAudioFlushRingSilence`, sets read = write).
  2. `DOSSOUNDBLASTER_PlayDevice` writes a chunk **with no room check** (`:4228-4242`); room is
     checked only in `DOSSOUNDBLASTER_WaitDevice` (`:2007-2011`), which runs only in SDL's background
     thread loop `while (Iterate()) WaitDevice()`.
  3. `SDL_DOSAudioPump()` calls `SDL_PlaybackAudioThreadIterate()` directly and never calls
     `WaitDevice` (`:3674`; the hub's own comment at `:807-813` says so). It checks room only AFTER
     the iterate, for its return value. A caller that invokes it while the ring is full therefore
     overwrites the chunk the ISR plays next.
  4. dosags calls it **unconditionally, once per pump** (`dos_audio_mixer.cpp` end of
     `dos_audio_mixer_pump()`), and each iterate that finds stream data writes one 1024 B chunk
     (46 ms). With a voice playing, the main loop alone offers 40 x 46 ms = 1.84 s of audio per second
     against an ISR drain of 1.0 s/s, and the background thread also fills to full. So on real
     hardware, **any PCM clip longer than the ring (~743 ms) plus DMA cover will have chunks
     overwritten once the ring is full** -- audible as a skip -- whenever the game runs near 40 fps.
     (At the old 3-5 fps regime this could not show.) *Not measured on hardware; a source reading.*
  5. The **DOSBox-X** side is additionally odd: UR1's fill never went DOWN between clips (371 ms at
     tick 76 and still 371 at tick 279, 5 s later), so the ISR was not draining there at all. 0199's
     `play_irqs` in the AR1 cells below answers whether the SB IRQ fires under DOSBox-X.
  **Where a fix would land is the coordinator's call:** the code is the hub's reference SDL series
  (`shared/patches/sdl3-dos/0067`, `0068`, `0088`), vendored here. Candidate shapes, not chosen: (i)
  engine side, call `SDL_DOSAudioPump()` only while `SDL_DOSAudioRingFillFrames()` + one chunk <=
  capacity (doskutsu's depth-setpoint pump already does this); (ii) SDL side, `SDL_DOSAudioPump()`
  returns without iterating when the ring has no room for a chunk. A cheap field first, if wanted:
  an overwrite-event count in PlayDevice (writes where `used + buffer_size > ring_size`).

**2026-09-22 -- PRE-REGISTRATION, AR1 validation cells + UR2 field check (DOSBox-X, local, no hardware).**
Binary: the 0199 build, `build_dirty=0 sha12=fdbd2bf77f4d` (staged as `AGS.EXE`). **AR1-5days-opl3,
AR1-5days-mpu401, AR1-agsquest-opl3**: exactly SB81's commands (confs `dosbox-x-fast-opl3.conf` /
`dosbox-x-fast-mpu401.conf` + hint `wb`; 5 Days `--fixed-timestep --startr 3`, 2000 ticks,
`ACSETUP-ON-512X384-ROUND.CFG`). **Expect:** `underruns=0` in all three; `drains` > 0 on 5 Days
(UR1 range 8-16) with `underruns + drains` in that range; `play_irqs` and `silent_irqs` present.
**Readings:** `play_irqs=0` = the SB IRQ does not fire under DOSBox-X (consistent with UR1's
non-draining ring; `silent_irqs` then means nothing there); `play_irqs>0, silent_irqs>0` on a
2000-tick run with no stall = the device ran dry while a voice played -- a finding, reported as is.
Any `underruns>0` is a finding. **UR2** (probe build `816a4687c4c6`, `build_dirty=1`, throwaway diff
`tests/harness/results/UR2-5days-opl3-forcestarve-2026-09-22/ur2-force-starve-throwaway.diff`, never lands): 5 Days OPL3 as AR1 with
`DOSAGS_UR2_FORCE_STARVE=1`, which removes the pump's 186 ms top-up stop so every pump mixes 8
chunks. **Predict `underruns > 0`** (both 5 Days clips exceed one 2048-sample slice). `underruns=0`
there = 0198 cannot say "starved" -> 0198 is wrong and slice 1 stops.

**2026-09-22 -- AR1 / UR2 RESULT (DOSBox-X), pending coordinator verification. 0198 behaves as
pre-registered; 0199 shows zero SB IRQs in these dosags DOSBox-X cells.** *(Headline corrected in place
2026-09-22 by the coordinator: it read "the SB IRQ NEVER FIRES under DOSBox-X", framed as an emulator
limit. See the RETRACTION in the 0199 bullet.)* Raw:
`tests/harness/results/{AR1-5days-opl3,AR1-5days-mpu401,AR1-agsquest-opl3,UR2-5days-opl3-forcestarve,
AR1T-5days-opl3-sdltrace}-2026-09-22/` (RUN.BAT, RUNMANI.LOG, STDOUT.TXT, run-dosbox.log; AR1T adds
SDLDBG.LOG). All exit through the auto-exit; each RUNMANI has one `audio_vital_status` line:

| cell | binary | `audio_vital_status` |
|---|---|---|
| AR1-5days-opl3 | `fdbd2bf77f4d`, dirty 0 | `underruns=0,drains=12,play_irqs=0,silent_irqs=0;midi=opl3,events=1617` |
| AR1-5days-mpu401 | `fdbd2bf77f4d`, dirty 0 | `underruns=0,drains=7,play_irqs=0,silent_irqs=0;midi=wb,events=1617` |
| AR1-agsquest-opl3 | `fdbd2bf77f4d`, dirty 0 | `underruns=0,drains=0,play_irqs=0,silent_irqs=0;midi=opl3,events=25` |
| UR2-5days-opl3-forcestarve | probe `816a4687c4c6`, dirty 1 | `underruns=8,drains=56,play_irqs=0,silent_irqs=0;midi=opl3,events=1617` |
| AR1T-5days-opl3-sdltrace (`DOS_PORT_LOG=1`) | `fdbd2bf77f4d`, dirty 0 | `underruns=0,drains=12,play_irqs=0,silent_irqs=0;...` |

- **0198, as predicted:** `underruns=0` in all three AR1 cells; the clip tails moved to `drains`
  (OPL3 12, in UR1's 8-16 range). *Deviation:* MPU-401's `underruns + drains` = 7, one below the
  pre-stated 8-16 range (SB81 MPU was 12); the count varies with how many pumps land between drain
  and release (UR1), recorded as is. **UR2 field check passed: forcing 8-chunk pumps gives
  `underruns=8`** -- the field can say "starved".
- **0199: `play_irqs=0` everywhere.** Independent witness, AR1T's `SDLDBG.LOG`: 20 lines `SDL/0073
  rate-meas: irqs=0 ... irq_hz=0` and `SDL/0106 CloseDevice: total IRQ-5 fires this run = 0`; the
  open itself reports `dsp_ver=255 ... 16-bit-high-DMA dma_ch=5 irq=5 ... OpenDevice SUCCESS`
  (`SDL_DOS_AUDIO_SB_SKIP_DETECTION=1` is set by the DOSBox-X runner).
  **RETRACTED 2026-09-22 (coordinator correction): the rest of this bullet framed the zero IRQs as a
  DOSBox-X limit ("under DOSBox-X the SB PCM ring is never drained"). That is not shown.** doskutsu's
  logs on the same driver read `dsp_ver=4` (16-bit path) and `dsp_ver=2` (8-bit path) (all on real
  hardware, see DSPV); 255 is what the DSP read returns when the DSP does not answer (compare SBCAP1's 0xFF). So in dosags
  the version query failed and the driver then took the 16-bit path because 255 >= 4, with 0 IRQs.
  **Treat it as a dosags-side defect until shown otherwise** (investigation "DSPV", below). The data
  stands; the original wording follows, struck in meaning: ~~So **under DOSBox-X the SB
  PCM ring is never drained and no SFX ever reaches the DSP**; 8.1's DOSBox-X "all paths open and
  play" holds for OPL3/MPU music (register writes) but NOT for SB PCM. This also fully explains UR1's
  ring fill: with zero drain, every non-silent `SDL_DOSAudioPump()` iterate adds one 46 ms chunk
  (232 -> 4086 ms), overwriting as it laps. The overwrite *path* found in (c) is source-proven and
  hardware-independent; whether it fires on hardware is unmeasured. *Not chased:* why DOSBox-X's SB16
  IRQ does not fire (dsp_ver 255 hints the DSP never answered a version query); DOSBox-X audio is not
  hardware evidence, and 0199's `play_irqs` will say directly whether the IRQ fires on the target.~~
  **Also corrected (coordinator):** 8.2's "clips did play: 74-77 clip-end drains" is not shown
  either -- drains are mixer-side; nothing yet shows the device consumed PCM on hardware. 8.3 must
  show `play_irqs > 0` on PGSB.
- `silent_irqs` cannot be validated as nonzero-capable in DOSBox-X (no IRQs). Its increment path is
  read from source only (`SDL_dosaudio_sb.c:1778-1789`); the first real reading is on hardware.
- **Re-pin (slice 1 binary, for 8.3 unless a (c) fix lands first):** clean build of `vendor/ags`
  `export-0199`, `make build-dirty` -> `build_dirty=0 sha12=fdbd2bf77f4d`, staged as
  **`build/abba/ags-0199-clean.exe`** (sha256 `bce64b30...e3e8a7`), byte-identical to the binary
  the gate and AR1 ran. `gate-alias.sh` on it: **13/14 clean, 0 regressions**, controls fail as
  required; `shards-alias-512x384` tick 100 only, bbox `(512, 513, 1152, 913)`, the pre-existing
  defect (`tests/harness/results/AR1-5days-opl3-2026-09-22/gate-alias-0199-summary.txt`). UR2 probe reverted (`vendor/ags` clean), diff kept at
  `tests/harness/results/UR2-5days-opl3-forcestarve-2026-09-22/ur2-force-starve-throwaway.diff`.
- **Slice 2 not started:** the coordinator holds the (c) fix-placement decision, and power-on now
  needs the operator (see Standing authorization).

**2026-09-22 -- PRE-REGISTRATION, DSPV (why `dsp_ver=255` in dosags' DOSBox-X cells; local, read
first, bounded ~1 h).** *Source read (`vendor/SDL/src/audio/dos/SDL_dosaudio_sb.c`):*
`CheckForSoundBlaster()` (:4528) returns true at once when `SDL_DOS_AUDIO_SB_SKIP_DETECTION` is set
and not "0" -- **no DSP reset at all** -- and `IsSoundBlasterPresent()` (:4665) then writes `0xE1`
and reads the version with `ReadSoundBlasterDSP()` (:676), which spins 100000 polls on base+0xE bit 7
and reads base+0xA regardless (0xFF when nothing is staged). The hub's `dosbox-run.sh:185` puts
`SET SDL_DOS_AUDIO_SB_SKIP_DETECTION=1` into every DOSBox-X RUN.BAT; real-hardware runs never set it
(SBCAP1's error came from the full reset-and-0xAA path). Note: the doskutsu `dsp_ver=4` / `dsp_ver=2`
logs on disk (`qa-results/2026-08-1x-*`) are all **real-hardware** runs (POD83, DX266, Am5x86, DX250);
none on disk is a DOSBox-X run, so there is no doskutsu DOSBox-X control on file.
**Cell DSPV1** (DOSBox-X, 0199 binary, AR1T exactly, `DOS_PORT_LOG=1`) plus
`SDL_DOS_AUDIO_SB_SKIP_DETECTION=0` (a later SET overrides the runner's; the code treats "0" as off):
the full reset-and-detect runs before `0xE1`. **H-reset** (the skip path's missing reset is the
cause): detection passes (0xAA), `dsp_ver=4`, IRQ-5 fires > 0, `play_irqs > 0`. **H-emu** (this
DOSBox-X's DSP does not answer reads at all, as the runner's comment claims): detection fails with
`last DSP read 0xFF`. Anything else is reported as is.

**2026-09-22 -- DSPV RESULT, pending coordinator verification: named cause -- the hub DOSBox-X
runner's `-silent` flag turns off SB emulation. Not a dosags code defect, and not a real-hardware
path.** Raw: `tests/harness/results/DSPV{1,2,3}-*-2026-09-22/` (each with RUN.BAT, RUNMANI.LOG,
STDOUT.TXT; INVOCATION.txt where the runner was bypassed; DSPV2 SDLDBG.LOG).

| cell | invocation | detection (`SKIP_DETECTION=0`) | `dsp_ver` | IRQ-5 fires | `audio_vital_status` |
|---|---|---|---|---|---|
| DSPV1 | hub `dosbox-run.sh` (`-silent -exit -nogui -nomenu`) | **FAIL, `last DSP read 0xFF`** | -- | -- | `NA` |
| DSPV2 | same conf, **no `-silent`** (Xvfb, `SDL_AUDIODRIVER=dummy`) | pass | **4** | **1105** (21 Hz all run) | `...drains=8,play_irqs=0,...` |
| DSPV3 | DSPV2 **plus `-silent`** | **FAIL, 0xFF** | -- | -- | `NA` |

- *Mechanism:* with `-silent`, the SB DSP at 220h does not answer (reset or no reset, 0xFF). The
  runner's `SET SDL_DOS_AUDIO_SB_SKIP_DETECTION=1` (`dosbox-run.sh:185`, comment "DOSBox-X's emulated
  SB16 returns 0xFF on the DSP detection read regardless of timing tuning") hid that: detection is
  skipped, `0xE1` reads 0xFF = 255, and 255 >= 4 selects the 16-bit path on a card that is not
  there -> 0 IRQs. That runner comment's premise is this same `-silent` artifact. doskutsu's
  `tools/dosbox-run.sh:159` has the same `-silent`.
- *Real hardware:* not affected. `run-hw.sh` never sets `SKIP_DETECTION`; on hardware the full
  reset-and-0xAA detection runs before `0xE1` (SBCAP1's failure was that path), and PGSB forces the
  8-bit path (`SDL_HINT_DOS_AUDIO_SB_FORCE_8BIT=1`) whatever the version reads. 8.2's sound-on arms
  opened `pcm=sb@...` after passing detection, so this does not invalidate them. It does NOT show the
  device consumed PCM there either (correction 2 stands).
- *Every earlier dosags DOSBox-X SB PCM result* (SB81, UR1, AR1) ran with SB emulation off: their
  mixer-side numbers stand, nothing device-side in them means anything.
- *Hub, coordinator's call (not touched here):* `-silent` in `shared/tools/dosbox-run.sh`, the
  SKIP_DETECTION default and its comment; and whether the driver should treat a 0xFF version under
  SKIP_DETECTION as "no answer" rather than SB16. For its own audio cells this slice bypasses the
  runner (`build/ws/ovw/run-nosilent.sh`, recorded in each cell's INVOCATION.txt).
- *Also found by DSPV2:* 0199's `play_irqs=0` with 1105 IRQs firing all run -> **0199's window was
  wrong** (next paragraph).

**2026-09-22 -- ags 0200, ags 0201, SDL 0190, SDL 0191 (worker): the (c) fix per the coordinator's
decision, plus the 0199 correction.**
- **ags 0200** (`export-0200`) corrects 0199. The mixer runs many times per tick and, before 0191,
  handed the driver every chunk at once, so a clip was "mixed out" within milliseconds while its
  sound played from the ring for up to ~743 ms; 0199's "voice still playing" window was nearly empty
  by construction. Now: **`pcm_irqs`** = IRQs that played ring data since open
  (`dos_port_audio_sfx_active_count`, the ISR's `ring_had_audio` branch) -- the "device consumed
  PCM" witness; **`silent_irqs`** = silent IRQs over pump intervals that began with audio still owed
  (SDL stream non-empty, or a voice not fully mixed out), evaluated after `SDL_DOSAudioPump()`.
  `play_irqs` is gone; **the slice-2 bar "play_irqs > 0" becomes "pcm_irqs > 0".**
- **SDL 0190** (`patches/SDL/0190-sb-ring-overwrite-counter.patch`): `dos_port_audio_ring_overwrite_count`,
  +1 per PlayDevice write where `(ring_write - isr_ring_read) + buffer_size > ring_size`. Counting only.
- **ags 0201** (`export-0201`): `audio_vital_status` gains `overwrites=<n>,ring_max_ms=<peak>/<cap>`
  (peak `SDL_DOSAudioRingFillMs()` after any pump). Status now:
  `pcm=...,underruns=,drains=,pcm_irqs=,silent_irqs=,overwrites=,ring_max_ms=a/b;midi=...`.
- **SDL 0191** (`patches/SDL/0191-sb-pump-no-iterate-into-full-ring.patch`): `SDL_DOSAudioPump()`
  applies WaitDevice's predicate under the lock before iterating and returns false without iterating
  when the ring lacks room for one chunk.
- *Mechanistic signature (pre-registered by the coordinator), DOSBox-X WITHOUT `-silent`, 5 Days OPL3
  in play as AR1, 2000 ticks, `SKIP_DETECTION=0`:* raw `tests/harness/results/OVW{1,2,3,4}-*-2026-09-22/`.

  | cell | binary | `overwrites` | `ring_max_ms` | `pcm_irqs` | `silent_irqs` | sounds played (STDOUT) |
  |---|---|---|---|---|---|---|
  | OVW1 before | `a9ff35b752c5` (0190+0201, no guard) | **38** | **1625/743** | 88 | 0 | sound 3 x2 |
  | OVW3 before, rep | same | **19** | **1578/743** | 88 | 2 | sounds 3, 9 |
  | OVW2 after | `4bbae85c9953` (+0191) | **0** | **510/743** | 52 | 2 | sound 9 |
  | OVW4 after, rep | same | **0** | **743/743** | 227 | 0 | sound 10 |

  **Met as pre-registered:** before, overwrites > 0 and fill > capacity (x2); after, overwrites = 0
  and fill <= capacity (x2; OVW4 reached exactly full and stopped there). All four `dsp_ver=4`,
  1099-1105 IRQ-5 fires. *Not a comparator:* `pcm_irqs` and `silent_irqs` vary because **5 Days
  plays a different random sound set per run** (STDOUT `Playing sound N on channel 3`: 3/3, 3/9, 9,
  10), so neither says anything before-vs-after. `silent_irqs=2` in OVW2 and OVW3 shows the field
  can come out nonzero (DOSBox-X at `cycles=max`; not hardware evidence of dropouts).
- *Gates* (`gate-alias.sh`): counter build `a9ff35b752c5` -- 13/14; **`agsquest-alias-y60` failed at
  ticks 1600 (32 px) and 1900 (1074 px), bbox around (550-653, 409-581)** -- the signature recorded
  in "Pre-existing agsquest-alias-y60 flicker" (32-1074 px, chandelier region, alias-unrelated,
  different ticks per run); `shards-alias-512x384` passed this time (its tick-100 defect is also
  intermittent). Raw: `tests/harness/results/OVW1-5days-opl3-before-2026-09-22/gate-alias-counter-build-*`.
  Guarded build: see the next paragraph.

**2026-09-22 -- GUARD GATE RESULT: STOP CONDITION HIT ("the guard changes a screen-equality row").
Slice C (re-pin, slice-2 pre-registration) NOT done; the pinned binary stays `ags-0199-clean.exe`
(`fdbd2bf77f4d`).** Raw: `tests/harness/results/OVW2-5days-opl3-after-2026-09-22/` (`gate-alias-guard-build-*`,
`aq-row-replicates-log.txt`, `aq-row-audio-and-keyphase.txt`, `aq-FRZ06-A-left-B-right-crop.png`).
- *Guarded build `4bbae85c9953`, full gate:* 12/14. `agsquest-alias-y60` FAIL (ticks 1600 32 px, 1900
  1074 px, 2200 32 px, 2700 731 px); `shards-alias-512x384` FAIL (tick 100, the known 120672 px bbox,
  plus one VOID pair frozen at A=501/B=500; a solo rerun of the shards row passed 5/5).
- *AQ row replicates* (row alone, `--arms "" --no-pillarbox --no-bench16 --no-catalogue`):
  **guarded 3/3 FAIL** at the same ticks 1600/1900/2200 (full gate + r1 + r2); **counter-only build
  `a9ff35b752c5` 1/3 FAIL** (full gate FAIL at 1600/1900; r1 and r2 clean). Earlier: 0198 and 0199
  full gates passed this row.
- **What the row difference IS (new, from the raw files): not rendering -- a one-tick game-state
  divergence between the A and B runs.** The FRZ06 crop shows the wizard at different stair
  positions in A and B at the same tick. `AUTOPLT.LOG` `phase=key status=ok` lands at tick **1194 in
  one run and 1195 in the other in every failing pair** and at the same tick in every passing pair
  (both builds; 12 runs listed in `aq-row-audio-and-keyphase.txt`). So the "Pre-existing
  agsquest-alias-y60 flicker" (scattered 32-1074 px in the chandelier region) is most likely this
  same one-tick autopilot divergence, not a present/uninitialized-buffer defect -- *inferred from
  these runs; the pre-0196 cases were not re-examined.*
- *Why the guard raises the rate (mechanism, from the manifests + source; inferred, not proven):*
  AGS Quest's music goes through SB PCM (`midi=none`). **Before the guard the gate runs overwrote the
  ring massively: `overwrites=1237-3350`, `ring_max_ms` 50480-148189 against 743** *(label added
  2026-09-23, coordinator via the hub port: these AQ gate figures, the pump-guard build's residual
  789/743, and UR1's 232 -> 4086 ms, come from DOSBox-X runs whose SB was not a normal live device --
  UR1 ran the `-silent` runner (SB off; see DSPV); the gate's freeze-capture runs are interactive, so
  not `-silent`, but with `SKIP_DETECTION=1` -- and their own manifests show `pcm_irqs=193-249`, so
  some IRQs did fire there; worker's note: I cannot confirm "SB switched off" for the gate runs from
  their data. SDL 0191's landed message cites these figures; not rewritten)* (the pump fed the
  ring at mix speed, so every clip "finished" in engine ticks, deterministically). With the guard,
  playback is paced by the device (`overwrites=1`, `ring_max_ms=789/743`), so when a clip finishes is
  wall-clock time, and any autopilot/script step that waits on a sound can land a tick either side
  under DOSBox-X `cycles=max`. Correct behaviour for a real device; it breaks the gate row's
  tick-for-tick A/B assumption.
- **The guard is also incomplete: `overwrites=1`, `ring_max_ms=789/743` (= capacity + one 46 ms
  chunk) in every guarded AQ run.** A second path, from source: `DOSSOUNDBLASTER_WaitDevice` checks
  room WITHOUT the device lock and, on the room-available path, calls `DOS_Yield()` before returning
  (patch 0086, `g_dos_audio_coop_yield_enabled` default ON, `SDL_dosaudio_sb.c:1924`); the main
  thread can pump into that last free chunk during the yield; the background thread then runs
  Iterate -> PlayDevice into a now-full ring. *Inferred; not instrumented.* A complete fix needs the
  room check in the path both callers share, under the lock (e.g. `GetDeviceBuf` or the top of
  `PlayDevice`'s caller), which is a design choice for the coordinator.
- **Also surfaced (for 8.3 and every PCM-music title):** before the guard, PCM music was fed at mix
  speed with thousands of overwrites per run (AGS Quest above); on hardware that would be garbled or
  fast audio for any title whose music is PCM, and every "wait for sound" in script lasted about half
  its real length. 5 Days / Trilby use MIDI music, so their exposure is SFX only.
- *Local tooling added for audio work (build/ws, not committed):* a DOSBox-X runner without
  `-silent`, and a DOSBox-X WAV capture via the F12+W host key into `-set "dosbox captures=DIR"`
  (48 kHz stereo; tested, 25 s capture with music and SFX levels at -22 dB RMS) -- the OPL3
  golden reference for 8.3 is feasible. The 5 Days title needs a mouse click on START (keys do not
  start it); at 640x480 START is at screen (60, 448) (game 30, 224).

**2026-09-22 -- Coordinator decisions after the guard stop, and PRE-REGISTRATION of the rework cells.**
Decisions (coordinator): (1) rework 0191 so the room check sits in `DOSSOUNDBLASTER_GetDeviceBuf`
(`*buffer_size = 0` when the ring lacks room for one chunk), replacing the pump-side version in
place; (2) the AQ gate row runs with SOUND OFF from now on; (3) leave the runner's `-silent` alone in
dosags (the hub fixes it: hub `1667198` adds `--sb-live`; bump the subtree at the end of this slice);
(4) then re-pin and pre-register slice 2. *Lock check done first:* `SDL_PlaybackAudioThreadIterate`
takes `device->lock` before calling `device->GetDeviceBuf` and holds it through PlayDevice
(`vendor/SDL/src/audio/SDL_audio.c:1179-1291`); `buffer_size == 0` skips both the stream pull and
PlayDevice (`:1189-1190`).
**AQ gate row, why it changed:** AGS Quest's music is SB PCM. Once the driver ring paces playback to
the device, when a clip ends is wall-clock time, and a script/autopilot step that waits on a sound
can land a tick either side between the A and B runs: every failing AQ pair had `phase=key status=ok`
at 1194 in one run and 1195 in the other (both builds). That is game state, not the present path
this gate judges; audio is covered by the AR/OVW/SBL cells and 8.3. **"The pre-existing
agsquest-alias-y60 flicker is probably the same one-tick autopilot divergence" is INFERRED, not
shown** (the pre-0196 failures were not re-examined). `gate-alias.sh` now stages
`[sound] enabled=0` for that row only; a solo run on the rework build: 10/10 pairs equal, control
fails as required, both runs `audio_vital_status=NA`, mode `640 x 480 (16-bit)`, key phase at 1194 in
both.
**Cells (DOSBox-X, SB live: no `-silent`, detection on; `build/ws/sbl/run-sblive.sh`; rework build):**
SBL1-SBL3 = 5 Days OPL3 in play (`--startr 3`, diagnostic entry, 2000 ticks, the AR1 cfg) x3, because
the sound set is random per run; SBL4 = AGS Quest harness, SB PCM music (sound on, its own default
cfg). **Bar (coordinator's):** `overwrites=0` and `ring_max_ms <= 743` in EVERY run, including SBL4
(AGS Quest showed `overwrites=1` with the pump-side version); SFX not silenced by the gate: 5 Days
`Playing sound` lines in STDOUT and `pcm_irqs > 0`, in the range OVW2/OVW4 showed for the same sound
(sound 9: 52; sound 10: 227; sounds are compared like for like). `pcm_irqs=0` in any sound-on cell =
the gate silenced audio -> stop. Full gate on the rework build: 13/14 with only the known Shards
tick-100 row = pass.

**2026-09-22 -- REWORK RESULTS (DOSBox-X, local), pending coordinator verification: every
pre-registered bar met.** Raw: `tests/harness/results/SBL{1..5}-*-2026-09-22/`,
`UR3-5days-opl3-stallprobe-r{1,2}-2026-09-22/`; gate summaries below.

| cell | binary | sounds (STDOUT) | `pcm_irqs` | `silent_irqs` | `overwrites` | `ring_max_ms` | IRQ-5 fires |
|---|---|---|---|---|---|---|---|
| SBL1 5 Days OPL3 | `2f64a30b5560` (0191 rework) | sound 10 | 227 | 0 | **0** | 743/743 | 1091 |
| SBL2 5 Days OPL3 | same | none logged | 16 | 0 | **0** | 325/743 | 1098 |
| SBL3 5 Days OPL3 | same | sound 10 | 227 | 0 | **0** | 743/743 | 1096 |
| SBL4 AGS Quest (SB PCM music) | same | music | 182 | 0 | **0** | 743/743 | 2197 |
| SBL5 5 Days NATURAL flow, 640x480 | `b238a51214ca` (+0202) | 18 (room 99), 3, 10 (room 3) | 251 | 0 | **0** | 743/743 | 5159 |

- **`overwrites=0` and `ring_max_ms <= 743` in every run**, including AGS Quest (SBL4), where the
  pump-side version left 1. All `dsp_ver=4`, detection on, no `-silent`.
- **SFX are not silenced by the GetDeviceBuf gate:** sound 10 gives `pcm_irqs=227` in SBL1 and SBL3,
  identical to OVW4 (same sound, pump-side version); SBL5's scripted sound 18 and room-3 sounds all
  played through. The ring filled to exactly capacity and waited there (743/743), the designed
  behaviour.
- **SBL5 (natural flow, the SB3O fixture):** room 1 -> 2 -> START (xdotool click at 640x480 screen
  (60, 448)) -> 99 -> 3, `silent_irqs=0` across the 99 -> 3 transition in DOSBox-X. (The earlier
  local title probe's 13 was on the pump-side build.)
- **ags 0202** (`export-0202`): one line per pump interval charged with silent IRQs,
  `DOS-PORT silentirq tick=<t> room=<r> irqs=<n>`. *Field check, UR3* (throwaway
  `DOSAGS_UR3_STALL_EVERY`: `SDL_Delay(1500)` in the pump every N ticks, probe `f800dafec8eb`, diff in
  the results folder, never lands): r1 `silent_irqs=56` = lines 27 + 29; r2 `silent_irqs=54` = lines
  25 + 1 + 1 + 26 + 1. The lines sum to the counter exactly; a 1.5 s main-loop stall during a clip
  gives ~25-29 silent IRQs (~1.2-1.3 s of silence), i.e. the ring (then holding a few hundred ms)
  plus DMA ran out.
- **Gates:** rework build `2f64a30b5560`, full `gate-alias.sh` with the AQ row sound-off: **13/14,
  pass** -- only `shards-alias-512x384` tick 100, bbox `(512, 513, 1152, 913)` (230192 px this run;
  the known defect's px count varies run to run); AQ row 10/10 equal. Raw:
  `tests/harness/results/SBL1-5days-opl3-2026-09-22/gate-alias-rework-summary.txt`. Final build
  `b238a51214ca` (+0202): see the re-pin paragraph.
- *Review (`/sdldos:review`) of SDL 0191 (reworked, From `b20db8f3`), ags 0202, and the
  `gate-alias.sh` change:* real `git format-patch` output, 0191 replaces its own slot (the earlier
  0191 file is removed, it was never ported), 0202 next free, ASCII-only, no `fopen`, no SIMD;
  permanent code, not a diagnostic. The two throwaways (UR2, UR3) never entered the series.

**2026-09-22 -- RE-PIN for 8.3 onward.** Clean build of `vendor/ags` `export-0202` over `vendor/SDL`
with 0190 + 0191 (rework), `make build-dirty` -> **`build_dirty=0 sha12=b238a51214ca`**, staged as
**`build/abba/ags-0202-clean.exe`** (sha256 `bdceff39...65f523`), byte-identical to SBL5's binary.
`gate-alias.sh` (AQ row sound-off) on it: **14/14 rows clean**, every control fails as required
(Shards' intermittent tick-100 defect did not show this run). Raw:
`tests/harness/results/SBL5-5days-natural-opl3-2026-09-22/gate-alias-pin-0202-summary.txt`.
Status line of this binary: `pcm=sb@11025m16,voices=8,underruns=<mid-clip>,drains=<clip-end>,
pcm_irqs=<n>,silent_irqs=<n>,overwrites=<n>,ring_max_ms=<peak>/<cap>;midi=<backend>,events=<n>`,
plus `DOS-PORT silentirq tick= room= irqs=` lines in STDOUT.

**2026-09-22 -- ags 0203 and the FINAL RE-PIN for 8.3 (supersedes the 0202 pin above).** 0202's line
could not say which silent intervals are room transitions: "Now in room N" carries no tick and the
load stall is not always a `stallwhat` line. **ags 0203** (`export-0203`) adds `since_room=<ticks
since the pump first saw this room>`; the pump after a room load is the first to see the new room,
so a load-spanning interval prints `since_room=0` by construction (that case was not exercised
locally: UR4's throwaway room-entry stall hit no owed audio; the field's other values were,
`since_room=280..1422`). **Pinned: `build/abba/ags-0203-clean.exe`, `binary_sha12=951a6a2d5d1e`,
`build_dirty=0`, sha256 `2b01b401...a554c28`.** `gate-alias.sh` on it: **14/14 clean**. Raw:
`tests/harness/results/UR4-5days-natural-roomstall-2026-09-22/` (gate summary, UR4 run, throwaway diff).
Hub subtree bumped to `1667198` (commit `affdc20`; the pinned binary is byte-identical before and
after the bump); `run-dosbox.sh --sb-live` passes through to it (cell SBL6: `dsp_ver`-4 path,
`pcm_irqs=263`, `overwrites=0`).
**Observation to carry into 8.3 (DOSBox-X, not hardware evidence):** in every SB-live 5 Days run in
which **sound 9** played in steady play (SBL6, REF-5D-NAT-OPL3-a/-b, UR4), single silent IRQs recur
in pairs about every 15 ticks (~375 ms, about two 2048-sample decoder slices) for the length of the
clip, far from any room change (`since_room` 280-1422): 13-41 per run. Runs where sound 9 did not play
show none (SBL1-5). Mechanism unknown, not chased.

**2026-09-22 -- PRE-REGISTRATION, 8.3 round (real hardware, PGSB profile 1, 640x480): SB3O, SB3W,
SB3S. Run under the operator's GO (Standing authorization, "8.3 round GO"): power ON after this is
pushed, power OFF when the round ends; mains-cycle hang recovery at most once per run.**
*Binary:* `build/abba/ags-0203-clean.exe`, expected `binary_sha12=951a6a2d5d1e`, `build_dirty=0`;
sha256 checked before staging and on the target copy after sending (run-hw.sh's own hash check).
*Order:* power on -> DOS prompt -> **idle floor** (3 x `vcctrl level 3000` + `spectrum 3000` at the
DOS prompt, capture locked; recorded as the floor for every cell) -> SB3O -> SB3W -> SB3S -> power off.
No `--boot-profile` (the menu default after the transfer is PGSB, as in 8.2/SBCAP3).
*Every cell runs, alongside run-hw.sh:* `tests/harness/audio-sampler.sh <results>/LEVEL.log`
(level + active bands every ~1.5 s) and `tests/harness/audio-rec.py <results>/<TAG>.ogg <secs>`
(vcctrl's Ogg Opus side-stream for the whole cell -- the files for the operator's golden listen).

| tag | fixture | cfg / env | driver | reference |
|---|---|---|---|---|
| SB3O | 5 Days a Stranger, **the game's own flow**: room 1 -> 2 -> title -> START -> 99 -> 3 | `games/5days/ACSETUP-ON.CFG` (640x480 default rung), `DOSAGS_TAS_AUTO_EXIT_TICK=16000`, no hint (SB PCM + OPL3) | `tests/harness/drive-start.sh SB3O` | `REF-5D-NAT-OPL3-a` (DOSBox-X, same binary, same flow, F12+W WAV; `build/ws/sb3/ref/`, Opus copy in `tests/harness/results/REF83-2026-09-22/`) |
| SB3W | same | same + `SDL_HINT_DOS_AUDIO_BACKEND=wb` (DreamBlaster S2 at 330h) | same | **none exists** (DOSBox-X's MPU-401 has no synth here); judged against SB3O's own capture |
| SB3S | AGS Quest harness (AutoPilot: its MIDI tune and the CC0 chime in the `audio` phase) | package default cfg (sound on), no hint | AutoPilot | `REF-AQ-OPL3` (DOSBox-X, same binary) |

*START click (SB3O/SB3W), `drive-start.sh`:* waits for the run's input lock; polls capture frames
until the START plank's pixel at (60, 448) is brown on two consecutive polls; **calibrates the
relative PS/2 mouse** (home to the corner, frame, move +100/+100 counts, frame; the changed bbox is
the cursor -> px per count); homes, moves to (60, 448) with that scale, clicks press-0.5 s-release;
checks the plank is gone. It clicks once only. Every frame it judged by and the calibration numbers
go into the cell's results. If it cannot calibrate or the title never shows, it does not click: the
cell then records the intro rooms only and is not an in-play cell (VOID for the in-play bars).

**VOID if** (as 8.2): `binary_sha12` not `951a6a2d5d1e` or `build_dirty` != 0; camera frame 1 does
not show `[PGSB] ready`; more than one manifest block; an SDL trace collected; the tag was reused;
STDOUT's game identity is not the fixture's; SB3O/SB3W STDOUT lacks `Now in room 99` then `Now in
room 3` (own flow not reached). **Audio VOID** (numbers still recorded) if `card-state.log` shows
`nosignal` during the run: the dongle is blind without video lock.
**STOP the round if:** the post-transfer hang recurs after the one allowed mains cycle in a run; the
profile does not land after the retry; a cell crashes or hangs the target; **the capture is silent
at 640x480 with lock present** (no heard window, below) -- report, no further cells.

**Bars, every sound-on cell** (all from RUNMANI `audio_vital_status` and STDOUT; the one-word vcctrl
verdict is not used):
1. `pcm_irqs > 0` -- the device consumed SB PCM (correction 2: nothing had shown it on hardware).
2. `overwrites = 0` and `ring_max_ms <= <cap>/<cap>`.
3. `underruns = 0` (mid-clip starvation; `drains` recorded as is).
4. **`silent_irqs = 0` outside room transitions**: every `DOS-PORT silentirq` line with
   `since_room <= 2` is a room-transition gap -- reported as measured values (irqs x 46.4 ms each),
   and handed to the stall-residual item, not judged here; any line with `since_room > 2` fails the
   bar. **Prediction, stated in advance:** if the DOSBox-X "sound 9" pattern (above) is real, SB3O
   and SB3W FAIL this bar with pairs of single-IRQ gaps ~15 ticks apart during sound 9; a pass means
   it is a DOSBox-X artefact.
5. **Heard:** at least 5 consecutive LEVEL samples during the run with mean >= floor + 10 dB and
   `active_bands >= 2` (SBCAP convention).
6. **SFX while music (SB3O, SB3W):** STDOUT shows `Playing sound 18` (room 99, scripted) and at least
   one room-3 sound while the MIDI `events` count grows, with bars 1-4 holding. The capture is NOT
   separately shown to contain the SFX (the music dominates the bands); the operator's listen covers
   that, and it is said so in the result.
**Correctness against the reference (`tests/harness/audio-compare.py`, Opus capture decoded):**
- *Melody, SB3O vs REF-5D-NAT-OPL3-a and SB3S vs REF-AQ-OPL3:* `chroma_score >= 0.85` AND at least
  0.10 above both `control_reversed` and `control_transposed5`. Calibration (DOSBox-X): two renders of
  the same flow score 0.987 (controls 0.53 / 0.80; 0.987 again with one side through Opus 128k);
  5 Days against AGS Quest scores 0.465 (controls 0.49 / 0.48). The score is also tempo-sensitive:
  the same pair with the reference sped up 1% scores 0.96, 3% 0.87-0.89 (pitch kept or not), so
  **>= 0.92 additionally shows tempo within about 2%**; between 0.85 and 0.92 the melody passes but
  tempo is judged by the next check only. (The onset-autocorrelation tempo field is recorded but NOT
  used: it picked an octave on the Opus copy of the reference, 2.07.)
- *Tempo, engine side, every music cell:* MIDI `events` per second of run time
  (`events / (ticks / tick_rate)`, RUNMANI) within 3% of the reference run's (REF-5D-NAT-OPL3-a:
  2494 events over 9600 ticks at `tick_rate=39.82` = 10.35 events/s; SB3S against REF-AQ-OPL3 the
  same way). Song-level constant: music 0 loops at one tempo across rooms.
- *WaveBlaster (SB3W), no reference:* heard (bar 5); the engine-side tempo check against SB3O's
  events/s (same song through a different synth: the event stream is identical, so within 3%);
  `chroma_score` against SB3O's capture recorded, not a bar (GM wavetable timbre differs from OPL3).
**After the round:** the three captures (and the DOSBox-X OPL3 reference) are sent to the operator
for one golden-reference listen, only if the bars above hold (standing feedback: listen only with
strong evidence, captures attached). **Machine time:** ~5 min power-on/boot/idle floor + SB3O and
SB3W ~15 min each (transfer ~2, boot, intro to the title ~3-4, room 3 to tick 16000, collect) +
SB3S ~10 min + a mains-cycle recovery margin: **about 50-60 minutes**, then power off.

**2026-09-22 -- SB3O RESULT: VOID for the in-play bars (own flow not reached) -- harness bug in
`drive-start.sh`, fixed; rerun as SB3O2.** Raw: `tests/harness/results/SB3O-2026-09-22/`. Binary
`951a6a2d5d1e`, `build_dirty=0`, exit 0, `ENGINE HAS SHUTDOWN`, mode `640 x 480 (16-bit)`, camera frame
1 `[PGSB] ready` (not yet reviewed frame by frame -- with SB3O2), card-state 143 `locked` / 1
`frozen` / 0 `nosignal`. STDOUT reached room 1 and room 2 only: the game sat at the title until the
auto-exit tick. **Cause:** the capture card frames the 640x480 mode shifted on the target -- the
START plank is at about (42, 402) in the capture, not DOSBox-X's (60, 448) -- so the fixed-pixel
title test never fired and nothing was clicked (`drive-start/poll.jpg`, `DRIVE-START.LOG`: "lock gone
before the title -- stopping, no click"). **Fix (harness only, before any rerun):** the title test
now LOCATES the plank as the brown blob in the lower-left and aims at its centroid, and the mouse
calibration uses three +100/+100 moves and picks the cursor as the blob two frame-diffs share, so an
off-frame homed corner does not matter (tested on the SB3O title frame with synthetic cursors).
Also: `audio-rec.py` lost the stream after 40 s (websocket keepalive ping timeout; the daemon does
not answer pings) -- now pings are off and a drop reconnects into a new segment file, logged; tested
60 s clean. *Numbers recorded, not judged (title screen, not in play):* `audio_vital_status=pcm=
sb@11025m16,voices=8,underruns=0,drains=1,pcm_irqs=10,silent_irqs=0,overwrites=0,ring_max_ms=278/743;
midi=opl3,events=23685`; whole-run `tick_rate=24.59`, `frames_skipped=13333` (the title at 640x480
16-bit); LEVEL 1402 of 2170 samples >= floor+10 dB with >= 2 bands (floor -67.9 dB, 3 samples at the
DOS prompt, `SB3-FLOOR-2026-09-22/FLOOR.log`). **Deviation from the pre-registration:** the driver
changed between SB3O and SB3O2 (fixture, binary and bars unchanged).

**2026-09-22 -- 8.3 ROUND RESULT, pending coordinator verification. Device-side SB audio works on
PGSB (PCM consumed, no overwrites, no mid-clip starvation), but two pre-registered bars FAIL: SB3O2
and SB3W play long silent gaps during SOUND 9 in steady play (as predicted from DOSBox-X), and the
melody bar is not met (SB3O2) / not decidable by its controls (SB3S). Target powered OFF 21:35:32
(plug 0 mW); no hang, no mains-cycle recovery used.** Raw: `tests/harness/results/SB3{O,O2,W,S}-2026-09-22/`
(RUNMANI, STDOUT, LEVEL.log, `<TAG>-seg01.ogg` = the whole cell's audio from vcctrl's Opus stream,
`DRIVE-START*.LOG` + frames, witness sheets); floor `SB3-FLOOR-2026-09-22/FLOOR.log` (-67.9 dB).
All cells: `binary_sha12=951a6a2d5d1e`, `build_dirty=0`, one manifest block, exit 0, `ENGINE HAS
SHUTDOWN`, `640 x 480 (16-bit)`, no SDL trace, card-state 0 `nosignal` (SB3O2 175 locked / 1 frozen;
SB3W 158 / 2; SB3S 103 / 9).

| cell | flow | `pcm_irqs` | `overwrites` | `ring_max_ms` | `underruns` | `silent_irqs` (lines) | transition lines (`since_room<=2`) | heard (longest run of samples) | `midi` | whole-run `tick_rate` |
|---|---|---|---|---|---|---|---|---|---|---|
| SB3O2 OPL3 | own flow: 1 -> 2 -> title -> START -> 99 -> 3 | **1513** | **0** | 743/743 | 0 (drains 19) | **279** (160) | **0** | 236 | opl3, 5630 ev | 25.52 |
| SB3W WaveBlaster | own flow, same | **1199** | **0** | 743/743 | 0 (drains 18) | **376** (218) | **0** | 238 | wb (cold-init ok), 4557 ev | 25.11 |
| SB3S AGS Quest | AutoPilot, `audio` phase ok 3163-3587 | **180** | **0** | 743/743 | 0 | **0** | -- | 26 | opl3, 27 ev | 19.74 |

**Bars:** 1 `pcm_irqs > 0` **PASS x3** (the first hardware evidence that the SB device consumed PCM:
correction 2 closed). 2 `overwrites = 0`, `ring_max <= cap` **PASS x3**. 3 `underruns = 0` **PASS x3**.
5 heard **PASS x3**. 6 SFX while music (SB3O2, SB3W): `Playing sound 18` in room 99 and room-3 sounds
(3, 9, 10) with MIDI running -- **PASS as pre-registered** (bars 1-3 hold; SFX not separately shown in
the capture). **4 `silent_irqs = 0` outside room transitions: FAIL on SB3O2 and SB3W, PASS on SB3S.**
No silent interval fell at a room transition (no `since_room <= 2` line in either cell) -- all of it is
steady play in room 3. **Every large cluster is a sound-9 play:** per 500-tick bins, SB3O2 has five
bins of ~50 silent IRQs (ticks 7000, 8500, 12500, 13500, 14500) and STDOUT has 5 `Playing sound 9`;
SB3W has seven (4500, 8000, 9000, 10500, 12500, 13000, 15500) and 7 plays. Everything else is 1-4 per
bin. ~50 silent IRQs per play of a clip that DOSBox-X measured at ~1.13 s: most of each sound-9 play
is silence on the device. Sound 10 (a ~10 s clip in DOSBox-X, `pcm_irqs=227`) does not do it.
**The DOSBox-X prediction held; this is a real dropout on hardware, not an emulator artefact.**
Mechanism NOT known and not chased (bounded round): the pump moves one device chunk per call and the
background thread only runs when the main loop yields, but that would hit sound 10 too; something
specific to sound 9 (its format/conversion at load, or how it is fed) is the lead. First probes, if
wanted: log each clip's source format and decoded length at load, and the ring fill at every pump
while sound 9 plays.
**Melody (`audio-compare.py`):** *SB3O2 vs REF-5D-NAT-OPL3-a*, intro/title music segments (capture
201-362 s vs reference 1-68 s): `chroma_score=0.668` (controls reversed 0.601, transposed 0.522) --
**FAIL** (bar 0.85 and +0.10 over both controls). Supplementary, not bars: best score at no time
stretch (0.67 at x1.0, 0.58 at x0.9 and x1.1, falling further out) and at no pitch shift (0.67 at 0,
0.28/0.22 at +-1 semitone); the hardware music's two halves match each other at 0.96. So neither a
tempo nor a pitch error explains it; the likely difference is timbre (PicoGUS `dbopl3` firmware vs
DOSBox-X's OPL3 emulator, plus the analog path) or that the two segments do not cover the same
music (the intro ran ~160 s on hardware at ~25 fps against ~68 s in DOSBox-X). Room 3 is mostly
silent in both apart from SFX; its recurring SFX envelope matches by eye (reference -50 -45 -46 -46
-50 -48 -57 dB vs hardware -47 -49 -46 -50 -49 -53 -63 dB, 1.5 s windows). *SB3S vs REF-AQ-OPL3*
(audio phase, 14 s): `chroma_score=0.973`, but `control_reversed=0.980` -- the phase is harmonically
static, so the reversed control has no power on it: **bar not met as written; undecidable by this
test**. Transposed control 0.457 (pitch right); the device played the same 180 PCM chunks as the
DOSBox-X reference.
*WaveBlaster (SB3W), no reference:* heard (238 consecutive samples); `chroma_score` against SB3O2's
capture 0.26 (recorded, not a bar; GM wavetable vs OPL3).
**Pre-registration errors, stated plainly:** (a) the engine-side tempo check (MIDI events per second
of run time vs the reference) is INVALID as designed: the music differs by room -- SB3O (title only)
ran 36 events/s, SB3O2 (title then room 3) 9.0, REF-a 10.35 -- so whole-run rates compare time spent
per room, not tempo. Not scored. (b) The onset-autocorrelation tempo field is unreliable, as already
noted; not scored.
**Deviations:** SB3O VOID (above). SB3O2's first `drive-start.sh` fired on a brown intro picture and
could not calibrate (no click); it was tightened to require the START and LOAD planks level with each
other and relaunched against the SAME running cell twice -- the second relaunch overshot on 3 x 100
counts (the cursor moves ~2.9 px per count in x), the third (3 x 40 counts) clicked START at 03:57:19
UTC and the title was gone 6 s later; the game therefore sat on the title ~2.5 min longer than it
would have. SB3W ran the final driver from the start and clicked on its first title detection.
SB3S's camera frame 1 is dark (the camera sheet starts after the launch); the profile landing is
witnessed instead by the capture card at the send reboot (`WITNESS-send.jpg`: `[PGSB] ready`). Every
camera frame of SB3O2, SB3W and SB3S was looked at: boot text, the intro narration, the title, DAY ONE,
room 3 (Trilby standing, no input after the click), then the DOS prompt; SB3S the forest, treehouse,
dialogue and credits screens and the prompt. No visual defect seen.
**Golden listen:** NOT sent -- the pre-registration sends captures only if the bars hold, and bar 4
fails. The files are ready: `SB3O2-seg01.ogg` (966 s), `SB3W-seg01.ogg`, `SB3S-seg01.ogg`, and the
DOSBox-X reference `REF83-2026-09-22/REF-5D-NAT-OPL3-a/*.opus`. Coordinator's call.

**2026-09-22 -- SOUND-9 / "DROPOUT" INVESTIGATION (local, DOSBox-X `--sb-live`, target off), pending
coordinator verification. MECHANISM NAMED: the SB driver's post-mix silence gate (SDL/0054 "Shape A",
`DOSSOUNDBLASTER_PlayDevice`) drops every chunk that is silent IN THE DEVICE FORMAT. On every path that
is the clip's own digital-zero stretches; on the 8-bit path (PGSB's `SDL_HINT_DOS_AUDIO_SB_FORCE_8BIT=1`)
it is ALSO every chunk whose peak is below 128 (-48 dBFS) -- real, quiet audio, lost. The fix changes
SB driver behaviour with a latency trade: STOPPED with options, no fix written.** Raw:
`tests/harness/results/UR5-*, UR5b-*, UR6-*, UR7a-*, UR7b-*, UR8-5days-opl3-{8,16}bit-2026-09-22/`
(each with its throwaway diff where one was used; all reverted, `vendor/ags` clean, `build/ags/ags.exe`
rebuilt byte-identical to the pinned `ags-0203-clean.exe`).
- *Read first (8.2 STDOUT, no cells):* every `stallwhat` in SB2B1/C1/D1 room 3 is printed right after a
  `Playing sound N` line: sound 10 -> 595-656 ms, sound 3 / sound 9 -> 250-280 ms, all `script_us`
  ~= `events_us` (script time). ~~**SB2A1 (sound OFF) has the same lattice stalls, 251-319 ms**
  (ticks 858, 1187): the ~500-tick lattice is the game's own ambient-sound script timer, and a
  ~250-320 ms script stall exists with sound off~~ **(CORRECTED 2026-09-23, STW: SB2A1's two stalls,
  and 4 of SB2C1's 6, come right after `MoveCharacter: request move` -- a walk click's pathfinding --
  not after a play; they are sound-independent walk stalls. The plays DO fall on a 500-tick lattice
  (DOSBox-X: ticks 1022, 1522, ...), but the sound-off stalls are not the plays' "script part".)**;
  sound 10 adds ~300 ms more with sound on (its play
  loads and decodes a 215 KB WAV synchronously -- UR5 `open_ms=10-12` on DOSBox-X, unmeasured on the
  486). So the lattice links the stall and the sound-9 silence by WHEN the game fires sounds, not by
  mechanism: the silence runs across the whole clip, after the stall.
- *The clips (UR5 probe, logged at decode):* sound 3 = WAV 8000 Hz mono 8-bit, 18141 samples at 11025
  (1.65 s); **sound 9 = WAV 11025 Hz mono 16-bit, 45160 samples (4.10 s), 52 of its 88 512-sample
  windows are exact digital zero** (UR5b); sound 10 = WAV 11025 Hz mono 16-bit, 107581 samples (9.76 s),
  0 zero windows; room-3 intro sound = WAV 44100 Hz mono 8-bit (0.35 s). All decode fully at load
  (resample-at-load, no streaming).
- *Per-pump trace during sound 9 (UR5):* the SDL stream sits full (`q=4096`) and the voice ring full
  (~30 KB) the whole time, yet the driver ring hovers at 0-185 ms and `pcm` (IRQs that played data)
  rises by 34 over ~90 pumps while the pump moved ~88 chunks: most chunks never reached the ring.
- **H-feed FALSIFIED** (supply is never short: stream and voice are full throughout). **H-load
  FALSIFIED for the silence** (decode is 5 ms and before the gaps; the gaps span the clip).
- **Control UR6** (`SDL_HINT_DOS_SILENCE_DETECT=0`, the gate off): `silent_irqs=0` across 2 sound-9 plays
  (UR5, gate on: 27). **UR8** (throwaway: classify every mixed chunk): 16-bit path `mixed=639 zero=57
  quiet<128=29`, **`pcm_irqs=582` = 639-57 exactly**; 8-bit path `mixed=605 zero=59 quiet<128=29`,
  **`pcm_irqs=516` = 605-59-29 (+-1)**. Source for the 8-bit threshold: SDL's `F32 -> S8/U8` rounds
  (`SDL_audiotypecvt.c:100-140`), so an S16 chunk with |s| <= 127 everywhere converts to all 0x80,
  which PlayDevice's bytewise scan calls silence (`silence=0x80` on the 8-bit path, SDLDBG).
- **What it does to the sound:** a skipped chunk either becomes a silent IRQ (ring empty -> timing
  kept; that is every `silentirq` line of the sound-9 clusters on hardware: ~50 per play = ~2.3 s,
  vs 52 zero windows = 2.4 s -- **the "dropout" is sound 9's own digital silence, mis-counted**), or,
  with data queued, the timeline collapses (the pause is shortened). On the 8-bit path quiet audio is
  removed outright. **Hardware accounting agrees:** expected chunks from STDOUT's plays and the clip
  sizes vs `pcm_irqs`: SB3O2 1617 vs 1513 (-104), SB3W 1304 vs 1199 (-105); DOSBox-X 16-bit REF-a
  774 vs 774; DOSBox-X 8-bit UR7a 807 vs 779 (-28). ~~The coordinator's burst measurement (hardware
  sound 10 ~9.0 s vs 10.0 s in the reference, with internal dips) is this~~ **(CORRECTED 2026-09-23 by
  the coordinator: the 10.0 s / "0 dips" reference figure used a different threshold; at the same
  -60 dBFS scan the reference's long effect is 9.3-9.6 s WITH 12-16 dips -- the dips are the sound's
  own quiet passages, not dropouts, and "gappy vs clean" is not evidence. The 9.0 s hardware figure
  vs 9.3-9.4 s at equal threshold still shows lost time.)** The lost time is sound 10's quiet chunks
  dropped on PGSB's 8-bit path (~17 chunks, ~0.8 s per play, from the chunk accounting).
- **So:** 8.3's bar 4 as written counted content silence as dropouts; the real defect is the gate --
  it loses quiet PCM on 8-bit Sound Blasters (PGSB here; SB 2.0/Pro-class cards) and shortens
  digital-silence pauses inside clips on every path. Not a feed, stall or ring problem.
- **Options (coordinator/operator decision; none implemented):**
  (1) *dosags sets `SDL_HINT_DOS_SILENCE_DETECT=0` at audio init* (zero-code in SDL; UR6/UR7b show it
  removes the loss). Trade: while idle, SDL's silence then fills the driver ring up to capacity (the
  0191 gate holds it at 743 ms), so a new SFX queues behind up to ~0.74 s of silence -- SFX latency.
  Could be paired with a smaller ring (`SDL_HINT_DOS_AUDIO_RING_CHUNKS=4` -> ~186 ms), at the cost of
  stall cover (room loads are 250-1000 ms on the 486). (2) *SDL-side, in the port's series and the
  hub's reference:* write a silent buffer when the ring already holds audio (timing then stays
  exact), skip it only when the ring is empty (idle stays idle; the idle-pause and `SDL_Delay(10)`
  throttle keep working); on the 8-bit path quiet chunks are then kept whenever sound is playing.
  (3) *SDL-side:* judge silence on the pre-conversion S16 data (or on "the bound streams returned no
  data"), not the device bytes -- closest to the gate's intent, but it is the 0050 history (a
  stream-emptiness gate once silenced SFX that SDL_mixer produces on pull), so it needs care for
  callback-driven ports. My recommendation: (2) -- narrow, keeps idle behaviour, fixes both effects.
- *Also noticed, for the stall item, not measured:* PlayDevice's all-silence branch calls
  `SDL_Delay(10)` while holding the device lock, and `SDL_DOSAudioPump()` reaches it on the MAIN thread
  whenever the pump iterates on an empty stream (nothing playing).
- **Melody re-score (re-analysis, not a new bar; the original FAIL stays):** aligning both captures
  from the music's start (game start; the music runs on wall-clock time, not frame rate, and room 3
  has none): capture 201-268 s vs reference 1-68 s `chroma_score=0.674` at lag 1 frame (controls
  0.626 / 0.523); first 30 s 0.633; 30-67 s 0.714. **Aligned segments still fail -- the finding
  stands; alignment was not the cause.** Diagnostic only: restricting chroma to >= 200 Hz gives 0.657
  (not hum). Cause not determined.
- **SB3S (AGS Quest):** chroma stays **undecidable** (reversed control 0.980 vs 0.973). The chime
  cross-correlation: my 8.3 pre-registration did NOT include it (only step 8.3's list does, "the chime
  cross-correlates"); computed now as that step names it -- waveform normalized cross-correlation of
  the audio phase, capture vs reference: peak |r| **0.031**, controls reversed -0.030 and a shifted
  window -0.037. **No power either** (analog chain, Opus, and the SB 2.0 time-constant rate of ~10989
  Hz vs 11025 all decorrelate raw waveforms). Undecidable; no third metric invented.

**2026-09-22 -- Coordinator decision after the sound-9 investigation, and PRE-REGISTRATION of the
content-active slice (local, DOSBox-X `--sb-live`).** *Decision (coordinator):* not option 2 --
SDL3's playback iterate fills an empty stream with silence and still calls PlayDevice
(`vendor/SDL/src/audio/SDL_audio.c:1210-1211`, `br < buffer_size -> SDL_memset(... silence ...)`,
confirmed), so "keep silence while the ring holds audio" would never let the ring empty again. And
on the 8-bit path a chunk that rounds to all 0x80 is also silent when played: both effects are the
same defect, lost TIME while content plays. The criterion is "is content playing". Built:
**SDL 0192** `SDL_DOSAudioSetContentActive(bool)` (default false = unchanged for every non-calling
port) + counters `skipped_silent` / `idle_pause`; **ags 0204** drives it from 0200's "audio owed"
predicate (before and after `SDL_DOSAudioPump()`), reports `skipped_silent=` and `idle_pauses=`;
**ags 0205** reports which FM chip answered (`chip=opl3|opl2,voices=18`); **ags 0206** MIDI timing
(`late_max_ms`, `late_hist` <=25/50/100/250/500/>500 ms events-weighted, `late50`, `burst=N@tick`,
`clk=<song ms>/<RTC s>s`, and a `DOS-PORT midilate` line per poll with gap > 100 ms that dispatched
events) -- after the operator's listen ("the real hardware sounds way better than dosbox, although I
think the tempo might be slower and it sounds like music speeds up randomly").
*Source answers first:* (a) OPL: `SDL_DOSOpl3Detect` is the AdLib timer-1 test (passes for OPL2 and
OPL3 alike); `SDL_DOSOpl3InitChip` always writes `0x105=1` (OPL3 mode) and `0x104=0` and the sink
drives 18 two-op voices, 9-17 via the 0x1xx bank at 38Ah/38Bh -- on an OPL2 (or an emulation without
the second bank) those voices are silent. Nothing checked which. (b) MIDI: `midi_sched_tick` advances
song time by the wall gap since the last call (clamped at 10 s) and dispatches everything due, from
the main loop -- a stall of N ms delays every note due in it by up to N ms and releases them in one
tick. Song time = uclock time, so "slower overall" needs uclock slow against real time. (c)
`idle_pauses`: dosags never calls `SDL_DOSAudioSetIdlePauseEnabled`, so the driver's idle-pause is off
and the field reads 0 before and after by construction; the idle behaviour that must survive here is
the gate's skip (`skipped_silent > 0`).
**Cells (binary `aa78f0416c81`, build_dirty=0; 5 Days `--startr 3` = diagnostic entry, 8000 ticks,
the AR1 cfg, OPL3):** CA16 (16-bit path), CA8 (`SDL_HINT_DOS_AUDIO_SB_FORCE_8BIT=1`), CA16P (the
pinned 0203 binary, same as CA16, for the rate ranking), MT1 (throwaway forced stall -- the UR3 diff,
`DOSAGS_UR3_STALL_EVERY=150`, 1.5 s -- MIDI field check).
**Predictions:** (1) no `silentirq` line during any sound-9 play (CA16, CA8); (2) `pcm_irqs` =
the content chunks expected from the plays (sound 10: 211, sound 9: 89 -- now INCLUDING its zero
windows --, sound 3: 36, room-3 intro sound: 8, per play) + `drains`, give or take 2 per play, less
where two sounds overlap, on BOTH paths (before: 16-bit dropped zero windows, 8-bit also quiet ones);
(3) `skipped_silent > 0` (idle still skipped; not attributed per interval -- aggregate only);
(4) `idle_pauses = 0` (by construction, above -- NOT a drop); (5) `overwrites = 0`, `ring_max <= cap`;
(6) `chip=opl3` under DOSBox-X `oplmode=opl3`; (7) MT1: `late_max_ms >= 1400` and `midilate` lines
at the forced-stall ticks (the field can say "late"); CA16's own `midilate` lines, if any, fall on
`stallwhat` ticks; `clk` within 2% of 1000 ms per RTC second over the run (RTC 1 s resolution).
Then the screen-equality gate, `/sdldos:review`, a clean re-pin, and a DOSBox-X whole-run rate
ranking of CA16 vs CA16P (ranking only). Stop if: a non-calling port could change behaviour; a
screen-equality row changes.

**2026-09-22 -- CONTENT-ACTIVE SLICE RESULT (DOSBox-X `--sb-live`), pending coordinator verification:
every pre-registered prediction holds.** Raw: `tests/harness/results/{CA16,CA16B,CA8,CA16P,MT1}-2026-09-22/`
(MT1 with its throwaway diff; reverted, `vendor/ags` clean). Binary `aa78f0416c81`, `build_dirty=0`
(CA16P: the pinned `951a6a2d5d1e`; MT1: probe `2e907229c4f4`).

| cell | path | plays (STDOUT) | expected chunks + drains | `pcm_irqs` | `silent_irqs` | `skipped_silent` | `overwrites` | whole-run `tick_rate` |
|---|---|---|---|---|---|---|---|---|
| CA16 | 16-bit | 3x sound 3 (+2 intro) | 124 + 3 = **127** | **127** | 1 | 7638 | 0 | 39.87 |
| CA16B | 16-bit | 4x10, 7x3, **2x9** (+2 intro) | 1290 + 8 = **1298** | **1298** | 2 | 5784 | 0 | 39.86 |
| CA8 | 8-bit | 5x10, 3x3, **2x9** (+2 intro) | 1357 + 4 = **1361** | **1361** | 1 | 5608 | 0 | 39.82 |
| CA16P (pinned, no 0192/0204) | 16-bit | 2x10, 3x9 | (drops zero windows) | 546 | **37** | -- | 0 | 39.88 |

Expected chunks per play = ceil(samples / 512): sound 10 211, sound 9 **89 (zero windows included)**,
sound 3 36, room-3 intro sound 8 (it plays twice at room entry without a "Playing sound" line; UR5).
- **(1) no silent IRQ during any sound-9 play** (CA16B, CA8: 4 plays); every remaining `silentirq` line
  is ONE IRQ about 24 ticks after a sound-3 play starts (4024, 6524, 7024: lattice tick + 24) -- not
  in this slice's scope, not chased. The pinned binary shows 37 over 3 sound-9 plays.
- **(2) `pcm_irqs` = expected + drains EXACTLY, on both the 16-bit and the 8-bit path** (the pinned
  binary: 16-bit short by the zero windows, 8-bit also by the quiet ones -- UR7/UR8/SB3O2/SB3W).
- **(3) `skipped_silent` 5608-7638**: idle silence is still dropped. (Aggregate; not attributed per
  interval, as pre-registered.)
- **(4) `idle_pauses=0`**, by construction (dosags never enables the driver's idle-pause) -- not a drop.
- **(5) `overwrites=0`, `ring_max_ms=743/743`** everywhere.
- **(6) `chip=opl3,voices=18`** under DOSBox-X `oplmode=opl3` (status bits 1-2 = 0). The hardware
  answer waits for the next round.
- **(7) MIDI timing field check, MT1** (forced 1.5 s stall every 150 ticks): `late_max_ms=1571`, 53
  `midilate` lines at the tick after each stall (151, 301, 451, ... gap 1522-1554 ms, 37-61 events
  each), `burst=130@5701`, `late_hist=1929/4907/95/0/0/2800`. The field can say "late". Unforced runs:
  `late_max_ms` 64-105, `late50` 94-814 events, `burst` 20-30 at tick 0 (the song start), CA16B's 4
  `midilate` lines at ticks 264-465 are 101-105 ms gaps with no `stallwhat` (that line's threshold is
  higher). **`clk`: 200429/201 s, 200512/200 s, 200609/201 s, 277365/278 s** -- 0.998-1.003 of real time
  against the RTC (1 s resolution): no tempo drift on DOSBox-X.
- **Rate ranking (DOSBox-X, ranking only, no claim):** whole-run `tick_rate` 39.86-39.87 (CA16, CA16B)
  vs 39.88 (CA16P, pinned): no difference visible.
- **Gate** (`gate-alias.sh`, AQ row sound-off): **13/14** -- only `shards-alias-512x384` tick 100, bbox
  `(512, 513, 1152, 913)` (180340 px; the known intermittent defect). No other row changed. Raw:
  `CA16-2026-09-22/gate-alias-0206-summary.txt`.
- **Review (`/sdldos:review`):** SDL 0192 (From `00a6f143`), ags 0204-0206: real `git format-patch`
  output, next free slots, ASCII-only, no `fopen`; SDL 0192's API is neutral (`SDL_DOSAudio*`, like
  0067/0088's exports) and a no-op for a non-calling port (default false, and the only other change
  is two counter increments). Note: 0206 reads the CMOS RTC (ports 70h/71h, register < 80h so NMI stays
  enabled) on every MIDI poll -- about 10 port reads, ~10-20 us per tick on the 486, and up to ~244 us
  once a second while the RTC updates; negligible, but it is per tick.
- **Re-pin:** `build/abba/ags-0206-clean.exe`, **`binary_sha12=aa78f0416c81`**, `build_dirty=0`,
  byte-identical to the CA cells' binary.
- **Recorded, per the coordinator:** the 5 Days chroma metric barely discriminates on hardware either
  (SB3O2 aligned 0.674 against a reversed control of 0.626). No metrics added.

**2026-09-23 -- PRE-REGISTRATION, 8.3 RE-RUN (real hardware, PGSB profile 1, 640x480): SB4O, SB4W,
SB4S.** Everything as the 8.3 pre-registration above (idle floor first; `audio-sampler.sh` +
`audio-rec.py` alongside every cell; `drive-start.sh` for the 5 Days cells; VOID / stop rules;
witness review; power off at the end) except:
*Binary:* **`build/abba/ags-0206-clean.exe`, expected `binary_sha12=aa78f0416c81`, `build_dirty=0`**
(SDL 0190/0191/0192, ags 0198-0206). Fixtures: SB4O = 5 Days own flow, OPL3; SB4W = the same with
`SDL_HINT_DOS_AUDIO_BACKEND=wb`; SB4S = AGS Quest harness. `DOSAGS_TAS_AUTO_EXIT_TICK=16000` for 5 Days.
**Bars (every sound-on cell):** `pcm_irqs > 0`; `overwrites = 0` and `ring_max_ms <= cap`;
`underruns = 0`; **`silent_irqs = 0` outside room transitions, with NO sound-9 exemption** (a
`silentirq` line with `since_room <= 2` is a transition gap, reported as measured); **`pcm_irqs` =
expected chunks + `drains`** -- per clip open, ceil(samples/512): sound 10 = 211, sound 9 = 89,
sound 3 = 36, sound 18 = 7, and in the own flow a room-2 clip at START (5080 samples, 10) plus the
room-3 entry clip twice (8 each), every one of which opens once per play (UR5c clip list, DOSBox-X
natural flow: `REF84-2026-09-23/UR5c-natural-cliplist`). Calibration, DOSBox-X, this binary, same
flow (REF84): 3x211 + 3x89 + 3x36 + 7 + 10 + 2x8 + drains 6 = **1047 = `pcm_irqs` 1047**. Tolerance:
equal, or lower by the chunks where two sounds overlapped (the mix shares chunks) -- an overlap has to
be visible in STDOUT order to excuse a shortfall. For SB4S, AGS Quest's chunks from its DOSBox-X
reference (`REF-AQ-OPL3`: 180) -- equal expected.
**Readings, predicted, not bars:**
- `chip=` / `voices=` on the PicoGUS (`picogus-sb-dbopl3` firmware; "AdLib port 388" on its boot
  screen). Prediction: `chip=opl3`. `chip=opl2` would mean voices 9-17 are silent on the target and
  would explain part of the melody gap (0.674).
- MIDI: `late_max_ms`, `late50`, `burst=N@tick`, `midilate` lines, `clk`. **"Rushes after stalls"
  (the operator's impression) is supported if** the `midilate` lines and the biggest bursts fall on
  stall ticks -- the room loads (`since_room`-0 ticks; room 1 -> 2 -> 99 -> 3) and the ~250-320 ms
  lattice stalls (`stallwhat` ticks) -- with `late_max_ms` in the stall range (250-1000 ms); it is not
  supported if `late_max_ms` stays under ~100 ms. **"Slower overall" is supported if** `clk` comes out
  below 1.0 (song ms per RTC second) beyond the RTC's 1 s resolution. *Second witness (0206 reads the
  CMOS RTC every poll):* the music's duration in the capture (host wall clock, from the music's onset
  to its end in `audio-compare.py`'s 1.5 s level windows) against `clk`'s song ms. Trusted: the RTC
  for the ratio (its own crystal, independent of the PIT behind uclock); the capture duration as the
  cross-check (+-1.5 s). If the two disagree by more than their resolutions, neither is quoted as a
  tempo result. (A BIOS tick count would NOT be independent: it runs off the same PIT as uclock.)
- Melody chroma, SB4O vs REF84 (music start aligned): recorded; the metric is weak (0.674 against a
  0.626 reversed control last round) and gets no verdict.
**Captures:** `<TAG>-seg01.ogg` per cell, for the coordinator's listening page.
**Machine time:** ~50-60 minutes including the idle floor, then power off.

**2026-09-23 -- 8.3 RE-RUN RESULT (SB4O / SB4W / SB4S), pending coordinator verification. Target
powered OFF 00:57:06 (plug 0 mW); no hang, no mains cycle.** Raw: `tests/harness/results/
SB4{O,W,S}-2026-09-23/` (RUNMANI, STDOUT, LEVEL.log, `<TAG>-seg01.ogg` whole-cell captures,
DRIVE-START.LOG + frames, witness sheets), floor `SB4-FLOOR-2026-09-23/FLOOR.log` (-67.9 dB after one
restart of vcctrl's audio reader: its first three samples read a constant -91.0 dB -- a wedged reader,
`audio state` last_error "non monotonically increasing dts" -- fixed by `vcctrl audio release` +
`acquire` before any cell; host side only). All cells: `binary_sha12=aa78f0416c81`, `build_dirty=0`,
one manifest block, exit 0, `640 x 480 (16-bit)`, card-state 0 `nosignal` (159/1, 159/1, 108/8
locked/frozen). START clicked on the first detection in SB4O and SB4W (same calibration as SB3W).
Profile: the send witness (capture) shows `[PGSB] ready` for all three (`WITNESS-send.jpg`); camera
frame 1 shows the boot text for SB4O/SB4W and is dark for SB4S (as SB3S). All camera frames
reviewed: intro, title, DAY ONE, room 3 (SB4O/SB4W); forest, treehouse, dialogue, credits, prompt
(SB4S). No visual defect.

| cell | `pcm_irqs` / expected+drains | `overwrites` | `underruns` | `silent_irqs` (lines, all `since_room > 2`) | `skipped_silent` | `chip` | `late_max_ms` / `late50` / `burst` | `clk` (RTC) | tick_rate |
|---|---|---|---|---|---|---|---|---|---|
| SB4O OPL3 | **1432 / 1432** | 0 | 0 | **10 (6)** | 13748 | **opl3**, voices 18 | 426 / 3176 of 4438 / 50@0 | 124374 ms / 124 s | 25.63 |
| SB4W WB | **1554 / 1554** | 0 | 0 | **23 (16)** | 13561 | -- (wb) | 427 / 3052 of 4530 / 50@0 | 127586 ms / 128 s | 25.56 |
| SB4S AQ | **181 / 180** | 0 | 0 | 0 | 3556 | opl3 | 64 / 13 of 27 / 2@3467 | 3043 ms / 3 s | 19.55 |

Expected per the pre-registration: SB4O 3x211 + 6x89 + 6x36 + 7 + 10 + 16 + drains 16 = 1432; SB4W
4x211 + 5x89 + 6x36 + 7 + 10 + 16 + 16 = 1554; SB4S: REF84-AQ-OPL3 (this binary, DOSBox-X, rendered
after the round) 180.
**Bars:** `pcm_irqs > 0` PASS x3. `overwrites = 0`, ring <= cap PASS x3. `underruns = 0` PASS x3.
**`pcm_irqs` = expected + drains: EXACT on SB4O and SB4W (hardware, 8-bit path); SB4S one chunk
over (181 vs 180) -- not equal as pre-registered; cause not known (a guess: one extra silent chunk
written at a content-active edge; untested).** **`silent_irqs = 0` outside room transitions: FAIL
on SB4O (10 IRQs = ~0.46 s over the run) and SB4W (23 = ~1.07 s); PASS on SB4S.** No sound-9
clusters any more (old SB3O2/SB3W: ~50 per play). Every remaining line falls on the ~500-tick
lattice (ticks ending 59-62, and SB4W's 2055/3160/3364), 1-3 IRQs each, 9 of 22 within 4 ticks of a
`stallwhat` line (255-639 ms, the sound-start script stalls): the ring runs short while the play call
stalls the main loop -- the stall-residual item, unchanged by this slice. (Attribution by tick; the
ring state at those moments was not probed.)
**Capture signature (the coordinator's level scan, NOT the harness; -60 dBFS, 50 ms, merge < 1 s):**
long effect 9.0 s (old SB3O2/SB3W) -> 9.3 s (SB4O/SB4W) vs 9.3-9.4 s (REF84); short effect 3.1 s ->
3.5-3.6 s vs 3.6 s. The fixed build restores on hardware the time the old one lost.
**Readings (predicted, not bars):**
- **`chip=opl3`, voices 18 on the PicoGUS** (status bits 1-2 read 0) -- as predicted. The OPL2 explanation
  of the melody gap is ruled out.
- **MIDI, "rushes after stalls": NOT supported as stated; a different mechanism instead.** Of SB4O's 483
  `midilate` lines, 465 have gaps of 150-200 ms and they run REGULARLY through the whole intro and
  title (ticks 7-2995, about every 6 ticks), not on stall ticks (33 of 483 within 3 ticks of a
  `stallwhat` tick). The room loads do not starve MIDI: during the 2.6 s room-2 load MidiPoll kept
  running at ~197 ms intervals (tick 1051, `update_polled_stuff`). The largest gaps are 403-427 ms
  (room-2 and room-99 loads); the biggest bursts are at song start (50@0) and 40 events once at tick
  2753. 72% of all MIDI events (late50 3176 of 4438) were dispatched more than 50 ms late, most by
  100-250 ms (`late_hist` 1254/8/1/3148/27/0). *Mechanism (source + these numbers):* at 640x480 16-bit
  the target renders the intro at ~6 fps, the fixed-timestep loop runs its catch-up ticks back to back
  (MAX_CATCHUP = 5, `game_run.cpp`), and every MIDI event due in the ~157 ms between renders goes out
  in one batch at the next render -- note timing quantised to ~157 ms. That fits "speeds up randomly"
  better than stalls do. SB4W the same (470 lines, 446 in 150-200 ms). SB4S (AGS Quest, ~20 fps)
  `late_max_ms=64`.
- **"Slower overall": NOT supported.** `clk` 124374 ms per 124 RTC s (1.003) and 127586 / 128 (0.997);
  second witness, the music's length in the capture (host clock, 1.5 s windows): SB4O 124.5 s vs song
  124.4 s, SB4W 127.5 s vs 127.6 s (0.999-1.001). Both witnesses agree; tempo is right to within about
  1%. The RTC is the trusted ratio; the capture agrees within its resolution.
- **Candidate fix shapes for the MIDI timing (not in scope; for the operator's decision):** (a) tick
  midi_sched from the SB IRQ (the SDL/0072 ISR-tick hook doskutsu uses, `SDL_DOSMidiTick...`,
  `g_dos_midi_isr_tick_active`) -- 21.5 Hz on this device, ~46 ms granularity, and it runs during
  stalls; (b) a PIT/timer callback (`SDL_dosopltimer.h` exists) at e.g. 100-200 Hz; (c) poll MIDI
  inside the catch-up loop with its own clock (does nothing for real stalls, and the ticks in a
  catch-up burst are microseconds apart, so it would not help here). (a) and (b) move sink calls
  (OPL register writes / MPU bytes) into interrupt context, which the WaveBlaster path's DRR-poll
  hazard (SDL/0093) makes non-trivial.
- **Melody chroma** (SB4O vs REF84, from music start): 0.654 at lag 1 frame (reversed control 0.604,
  transposed 0.556). Weak metric, no verdict, as written.
**Captures for the listening page:** `SB4O-seg01.ogg` (1026 s), `SB4W-seg01.ogg` (1029 s),
`SB4S-seg01.ogg` (587 s); DOSBox-X reference `REF84-2026-09-23/REF84-5D-NAT-OPL3/REF84-5D-NAT-OPL3.opus`.

**2026-09-23 -- MIDI TIMING FIX: read-first, choice, PRE-REGISTRATION (local only; operator decision:
MIDI timing next, ahead of the sound-load stalls; target off).**
*Read first (source):*
- **doskutsu's SDL/0072 ISR tick** (vendored here; SDL/0075 made it default-ON, so
  `g_dos_midi_isr_tick_active` is already true in dosags, with no callback registered = no-op): the
  SB IRQ calls a registered engine callback with `now_ms` built from inter-IRQ timer deltas. The
  contract (`SDL_dosmidi_tick.h`): no malloc, **no FPU**, no SDL calls, everything touched
  DPMI-locked, cli/sti around main-thread scheduler edits. doskutsu met it with its own fixed-point
  `tick_isr` scheduler. **dosags cannot run its scheduler in the ISR as is:** the hub's shared
  `midi_sched_tick` computes `event_us = (double)ev->abs_tick * m->us_per_tick` (FPU), and the shared
  `opl3_sink` / `waveblaster_sink` / `gus_sink` hold C state with allocation at open; none of that
  code or data is locked, and none of it is dosags' to rewrite.
- **The ISR clock:** the SB ISR timestamps with RDTSC or, on the 486, PIT counter 0 read by latch
  (`SDL_dos_audio_synth.h`, read-only: it never reprograms ch0, so uclock is untouched). A per-IRQ
  PIT delta aliases if one IRQ is >55 ms late. The IRQ COUNT itself (`dos_port_audio_irq_count`) is
  an exact device clock: one IRQ = one 512-frame half-buffer = 46.44 ms at 11025 Hz.
- **SDL/0093 (WaveBlaster):** the hazard is READING the MPU status port while the WaveBlaster is absent
  or wedged -- the ISA IOCHRDY wait stalls the CPU mid-`inportb`, no software cap can break it. The
  default (0093) is a blind write: `outportb(base, byte)`, no status read. A blind write is safe in
  an ISR; the DRR-poll opt-in, the `WB_TX_DELAY` PIT busy-wait and the DSP-mediated path are not.
- **Sinks' port writes:** every OPL3 write goes through `SDL_DOSOpl3WriteRegister` (two `outportb` +
  12 dummy `inportb` of 388h; it also calls `uclock()` for a diagnostic); every MPU byte through
  `SDL_DOSMpu401WriteByte`.
- **No SB IRQ:** GUS (PGGUS), PGADLIB (MIDI disabled there anyway), the SB device not open, or an SB
  that never raises IRQs (DSPV) -- these need the existing main-loop poll.
- **PIT option:** hooking IRQ0 without reprogramming gives 18.2 Hz (55 ms); reprogramming ch0 breaks
  uclock (hub docs/audio.md), which is the MIDI clock and the pacer's. Same ISR constraints as the SB
  route, coarser, and no exact device clock. Not chosen.
**Choice: DEFERRED PORT WRITES replayed by the SB ISR ("plan on the main thread, play in the ISR").**
The main thread keeps running the unchanged shared scheduler and sinks, but AHEAD of time: each
MidiPoll plans the song up to a lookahead horizon (default 2 s = 43 IRQs), one 46.44 ms slot at a
time, and every OPL register write / MPU byte the sinks produce is captured into a locked queue
stamped with the IRQ index its slot is due at. The SB ISR, on every IRQ, writes out the entries whose
stamp has come (raw `outportb`/`inportb` only, bounded per IRQ). No FPU, malloc or unlocked code in the
ISR; nothing shared is rewritten; timing becomes the device's own IRQ clock (46 ms granularity)
whatever the render rate, and music keeps playing through any main-loop stall shorter than the
lookahead. Opt-in only (default off), so doskutsu and every port that doesn't call it see no change.
Scope: OPL3 and WaveBlaster-blind (the default WB write path); WB with DRR-poll / TX-delay / DSP
transport, GUS, and no-IRQ cases fall back to the poll, logged as `midi_tick=poll`. Known costs, stated
now: a stop/pause flushes the planned-ahead writes and sends note-offs at once; song changes drain
the queue first; stalls LONGER than the lookahead still starve (then the plan falls behind and plays
late -- measured by `plan_behind`). MIDI volume is not applied by the port (`AudioPlayer::SetVolume`
ignores MIDI), so control-change latency is not an issue today.
**Patches:** SDL 0193 (the queue, its locked ISR replay, capture in the two write primitives when
enabled, stats; OFF by default) and ags 0207 (the planner in `AudioPlayer::MidiPoll`, mode choice +
fallback, stop/pause/song-change handling, status fields `midi_tick=isr|poll`, ISR lateness
`late_max_ms` / `late_writes` / `isr_burst`, `plan_behind`). `DOSAGS_MIDI_TICK=poll` forces the fallback
(the A/B control inside one binary).
**Cells (DOSBox-X `--sb-live`, 5 Days `--startr 3` = diagnostic entry, 8000 ticks, music plays
throughout; new binary unless noted):** MI0P (poll, OPL3), MI0I (isr, OPL3); MISP / MISI (throwaway
stall probe: `SDL_Delay(1500)` in the pump every 150 ticks, as MT1; poll / isr); MITP / MITI (throwaway
render throttle: ~150 ms delay per rendered frame, ~6 fps like the 640x480 intro on the 486; poll /
isr); MIWI (isr, WaveBlaster: mpu401 conf + `wb`), MIWT (isr, WB, throttle); MIF (the default
`-silent` runner: the SB never raises an IRQ -> must fall back).
**Bars (the mechanistic signature):**
1. **MISI:** ISR `late_max_ms < 60` and `late_writes = 0`; the probe logs ISR writes made DURING each
   forced stall > 0 (music keeps playing through the stall); `plan_behind = 0`. Control MISP:
   `late_max_ms >= 1400` with bursts at the stall ticks (MT1: 1571, 130).
2. **MITI:** `late_writes` <= 1% of ISR writes (`late50` near 0); control MITP: most events > 50 ms late.
3. **clk** within 1% of the RTC in every isr cell.
4. **MIF:** `midi_tick=poll`, the pre-0207 fields unchanged in kind; MI0P likewise `midi_tick=poll`.
5. **MIWI / MIWT:** `midi_tick=isr` on WaveBlaster with bars 2-3 holding.
6. No hang or crash in any run; `overwrites=0` and the audio fields otherwise as CA16.
Then the screen-equality gate, `/sdldos:review` (DJGPP ISR rules explicitly: locked code + data, no
malloc/printf/FPU in the ISR, cli around shared-state edits), a clean re-pin, and a DOSBox-X rate
ranking against `aa78f0416c81` (ISR work steals CPU; ranking only). **Stop if:** the SDL side would
change behaviour for a port that does not opt in; a screen-equality row changes; any run hangs or
crashes in the ISR.

**2026-09-23 -- MIDI TIMING FIX RESULT (DOSBox-X `--sb-live`), pending coordinator verification. The
mechanistic signature holds for OPL3; WaveBlaster stays on the poll (by design, below).** Final
binary **`build/abba/ags-0207-clean.exe`, `binary_sha12=7d43b8e155ed`, `build_dirty=0`** (SDL
0190-0193 + ags 0198-0207); probe build `71dc73445bdd` (throwaway stall + render-throttle probes, diff
in `MISI4`/`MITI4`, reverted). Raw: `tests/harness/results/MI*4-2026-09-23/` (generation 4 = the
final build; generations 1-3 are earlier builds of the same two patches, kept, superseded -- see the
build history below).

| cell | mode | condition | `late_max_ms` | late (events / writes) | burst | `clk` (RTC) | tick_rate |
|---|---|---|---|---|---|---|---|
| MI0P4 | poll | plain | 88 | late50 118 of 7649 | 30@0 | 200565/200 s | 39.83 |
| MI0I4 | **isr** | plain | **0** | late_writes **0** of 16349 | isr_burst 79 | 198582/201 s | 39.85 |
| MISP4 | poll | 1.5 s stall every 150 ticks | **1560** | late50 3053 | **130@5701** | 276155/276 s | 28.94 |
| MISI4 | **isr** | same stalls | **0** | **0** of 22468; ISR writes during each stall: min 2, median 96, max 224 (n 53) | 79 | 275868/277 s | 28.78 |
| MITP4 | poll | 150 ms per render (~6 fps) | 231 | late50 **9583 of 11686** | 50@0 | 312042/312 s | 25.61 |
| MITI4 | **isr** | same throttle | **0** | **0** of 27112 | 79 | 321794/323 s | 24.72 |
| MIWI4 | poll (WB) | plain | 101 | late50 387 | 20@0 | 200440/201 s | 39.85 |
| MIF4 | poll (no IRQ: `-silent` runner) | plain | 80 | late50 91 | 20@0 | 200390/200 s | -- |

- **Bar 1 (stalls), MISI4: MET.** `late_max_ms=0`, no late write, the ISR kept writing through every
  forced stall (median 96 writes per 1.5 s stall; the minimum 2 falls in a rest), `plan_behind=0`, no
  `midilate` line. Control MISP4: 1560 ms, a 130-event burst at a stall tick.
- **Bar 2 (render throttle, the operator's symptom), MITI4: MET.** 0 of 27112 writes late; control
  MITP4: 9583 of 11686 events (82%) > 50 ms late.
- **Bar 3 (clk within 1%): 2 of 3 isr cells** (MISI4 0.996, MITI4 0.996); **MI0I4 0.988** by point
  estimate (RTC resolution +-1 s over 201 s = +-0.5%). In isr mode the song clock IS the device's IRQ
  clock (512 frames at the rate the SB plays), and every isr cell across four builds read 0.988-0.996
  against 0.997-1.003 for the poll cells: DOSBox-X's SB plays ~0.5% slower than its PIT/RTC here. On
  the PicoGUS the SB 2.0 time constant gives ~10989 Hz (-0.33%). Not fixed; see follow-ups.
- **Bar 4 (fallback), MIF4 and MI0P4: MET** -- `midi_tick=poll` with the 0206 fields.
- **Bar 5 (WaveBlaster via the ISR): NOT MET, by design.** MIWI (all four builds) fell back to the
  poll: dosags opens WB through the cold-init path, whose default per-byte transport is SDL/0098's
  320 us TX-delay PIT busy-wait (the fix for the DreamBlaster's input overrun, H20). Doing that in the
  ISR means busy-waiting up to tens of ms per IRQ (a 60-byte burst ~19 ms) with other IRQs held off;
  0193 therefore refuses kind 2 unless the transport is blind (no status read, no delay), which is
  the "iter-7 garbled" baseline for this hardware. Recommendation, as the dispatch allowed: OPL3 via
  the ISR, WaveBlaster on the poll.
- **Bar 6: MET** -- no hang or crash in any of 32 MI runs; `overwrites=0` everywhere.
- **Gate** (`gate-alias.sh`, alone on `7d43b8e155ed`): 12/14 -- `shards-alias-512x384` tick 100 (the known
  defect, bbox `(512, 513, 1152, 913)`) and **`agsquest-alias-y60`** at ticks 1600/1900/2200 with the
  familiar one-tick autopilot divergence (`phase=key status=ok` 1194 vs 1195) -- **with sound OFF**
  (`audio_vital_status=NA`, `[sound] enabled=0` staged in both runs). The row alone, re-run: 0207
  build 2/2 clean, 0206 build 2/2 clean (key_ok 1194/1194 each). With sound off, 0193/0207 never run.
  **Correction:** the earlier reading that device-paced audio makes this row diverge ("Why the guard
  raises the rate", 2026-09-22) is refuted as the cause -- the divergence occurs with sound off too; it
  is an intermittent, sound-independent one-tick autopilot divergence. The sound-off change of the
  row stands but did not remove it.
- *An earlier gate on build `d33bfc203373` failed bench8 anim4/anim12 rows with 16 px differences:
  their freeze frames were the DOS prompt, not the game -- that gate ran while `--sb-live` MI cells
  (under `xvfb-run -a`) ran alongside, and the captures came from the wrong screen. Invalid; not a
  code effect. Tooling note: do not run `--sb-live` cells concurrently with the freeze-capture gate.*
- **Rate ranking (DOSBox-X, ranking only):** MI0I4 39.85 / MI0P4 39.83 against `aa78f0416c81`'s CA16
  39.87 and CA16B 39.86 -- no difference visible.
- **Review (`/sdldos:review`):** SDL 0193 (From `097def7c`) and ags 0207 (From `fb01d963`): real
  `git format-patch` output, next free slots, ASCII-only, no `fopen`. DJGPP ISR rules checked on the
  ISR path (`MidiDeferDrain`, `MidiDeferWriteOne`): integer ops and `inportb`/`outportb` only -- no
  malloc/free, printf/log, FPU, uclock or SDL call; code range and queue locked at the first enable;
  `g_mdq_kind`/`g_mdq_hold` locked at OpenDevice with the ISR's variables; compiler barriers on both
  sides of the queue publish. The code-range lock relies on source-order function layout, the same
  convention the existing `SoundBlasterIRQHandler`/`_End` lock uses.
- **Build history (why four):** `aa105e72563b` first build (MI gen 1); `d33bfc203373` + compiler barriers
  around the queue publish/read (my review; MI gen 2); `33f03b691c5c` the coordinator's hub review of
  0193 -- Detect/InitChip/Shutdown now HOLD the replay instead of relying on cli (Detect's
  SDL_DelayPrecise yields and the thread switch's iret re-enables interrupts: the hub probe saw 28 of
  300 Detect calls with an IRQ mid-call), Enable(0) drains at most 1024 entries in batches of 32 under
  short cli and discards the rest (counted), CloseDevice turns deferral off and discards (counted),
  `g_mdq_kind`/`g_mdq_hold` locked at OpenDevice; ags 0207 plans from now+2 (MITI2's 19 late writes:
  an entry stamped for the very next IRQ could miss it when that IRQ fired while the plan was being
  written; 0 in gen 3/4) and reports qsync/qdropped (MI gen 3); `7d43b8e155ed` the MIDI status fragment
  buffer 192 -> 320 and status buffers 384 -> 512 (gen 3's isr lines were truncated at `clk=`) (MI gen 4).
**Follow-ups (not done in this slice):** (1) song clock in isr mode follows the device rate (-0.3% on
the PicoGUS, ~-0.5% on DOSBox-X); a rate-corrected slot length from uclock would remove it if wanted;
(2) WaveBlaster timing stays render-bound until a transport exists that is both ISR-safe and
overrun-safe (e.g. an ISR-side byte budget per IRQ with inter-byte spacing, or a PIT tick); (3) the
AQ gate row's intermittent one-tick divergence needs its own look (it is not audio); (4) pause keeps
playing up to the lookahead (2 s) of already-queued writes, then holds; (5) hardware confirmation
(needs an operator ask).

**2026-09-23 -- PRE-REGISTRATION, CLOCK FIX + CODE LOCK (local; operator decision "Clock fix first,
then HW").** **ags 0208:** in isr mode each planned slot advances SONG time by the MEASURED IRQ period
(IRQ count against uclock since song start, used after 43 IRQs, clamped +-5%; uclock read only, the
PIT is never reprogrammed) instead of the nominal 46439 us; stamps (and the ISR replay) unchanged;
`clk` now reports the song clock itself; status gains `real_period_us`. **SDL 0194** = the hub's
`shared/patches/sdl3-dos/0145` (From `029ebcaa451e`, hub `208923a`), applied unchanged with `git am`
(no conflicts): lock `[start, etext)` once at hook install, log every `DOS_LockCode` range of length
<= 0 instead of passing it to the host. Binary `513a187edcbb` (probe build for stall/throttle as in MI).
**Cells (DOSBox-X `--sb-live`, 5 Days `--startr 3`, OPL3):** MC0I (isr, 8000 ticks), MCSI (isr + the MI
stall probe), MCTI (isr + the MI render throttle), MCL (isr, 16000 ticks, the long witness), MC0P
(poll control), plus one `DOS_PORT_LOG=1` run (MCLK) for the 0194 log lines.
**Bars:** `clk` within 1% of the RTC in every isr cell (RTC resolution +-1 s: the long cells MCSI/MCTI/
MCL carry the weight); `real_period_us` recorded; `late_writes=0` and `plan_behind=0` still;
MCSI/MCTI late as in MISI4/MITI4 (0); the poll control unchanged in kind. 0194: one "program code
lock ... locked" line and the `<= 0` witness lines for the known sites in MCLK's SDL log; image size
recorded; free memory after the lock read from the log if SDL reports it (dosags logs no free-memory
figure of its own -- stated, not invented). Then the gate (only the two known rows may differ), review,
re-pin. **Stop if** clk cannot reach 1% without late writes; any other gate row changes.

**2026-09-23 -- CLOCK FIX + CODE LOCK RESULT (DOSBox-X `--sb-live`), pending coordinator verification.**
Binary **`build/abba/ags-0208-clean.exe`, `binary_sha12=513a187edcbb`, `build_dirty=0`** (SDL 0190-0194,
ags 0198-0208); probe `58c52c0d709b`. Raw: `tests/harness/results/MC*-2026-09-23/`.

| cell | mode | clk (song ms / RTC s) | ratio | real_period_us | late_writes / late_max | plan_behind | tick_rate |
|---|---|---|---|---|---|---|---|
| MC0I | isr | 200351 / 201 | 0.997 | 46440 | 0 / 0 | 0 | 39.88 |
| MCSI (stalls) | isr | 277633 / 278 | 0.999 | 46438 | 0 / 0 | 0 | 28.78 |
| MCTI (6 fps) | isr | 325554 / 325 | 1.002 | 46440 | 0 / 0 | 0 | 24.54 |
| MCL (16000 ticks) | isr | 400283 / 401 | 0.998 | 46436 | 0 / 0 | 0 | 39.94 |
| MCLK (SDL log) | isr | 200426 / 200 | 1.002 | 46447 | 0 / 0 | 0 | 39.86 |
| MC0P | poll | 200521 / 200 | 1.003 | -- | late50 125 | -- | 39.84 |

- **Bars MET:** clk within 1% of the RTC in every isr cell (0.997-1.002; the longest, MCL, 0.998 over
  401 s); `late_writes=0`, `plan_behind=0` everywhere, stalls and throttle included.
- **CORRECTION to the MI result (in place of its "clock" bullet):** on DOSBox-X the measured IRQ period is
  46436-46447 us = nominal 46439, so the device clock was NOT slow there. 0207's `clk` of 0.988-0.996 was
  a witness artifact: 0207 accumulated `clk` per poll as `(IRQ delta x 46439) / 1000` in integer ms,
  dropping ~0.44 ms per IRQ (0.95%). 0208 reports the song clock from cumulative microseconds. The
  device-rate offset 0208 corrects is real on the PicoGUS (SB 2.0 time constant: ~10989 Hz, -0.33%),
  which only the hardware round can show (`real_period_us` there).
- **SDL 0194 (hub 0145) engaged**, raw from `MCLK-2026-09-23/SDLDBG.LOG`:
  `DOS: patch 0145 program code lock [start=0x19f0, etext=0x4db8a0) = 5086896 bytes: locked`;
  `DOS: patch 0145 DOS_LockCode(SoundBlasterIRQHandler) range length -64 <= 0 (end marker laid out
  before the function); not locked by range, covered by the program code lock (held)`;
  `DOS: patch 0145 DOS_LockCode(RingCopyOut) range length -3504 <= 0 (...) (held)`. The code image is
  **5,086,896 bytes (4.85 MB) now locked** (the exe is 8,448,534 bytes). The engine's memory KPI
  (`memory_min_free_kb`, the largest free DPMI block -- virtual memory, not physical) reads
  166512-167536 KB with 0194 vs 166576-168240 before (CA16/CA16B): no change visible; physical free
  pages are not logged by anything in dosags (not measured).
- **Gate:** 13/14 -- only `shards-alias-512x384` tick 100, the known bbox. **Review:** 0194's code hunks
  are byte-identical to hub 0145 (diff empty), message states the adoption; 0208: ASCII-only, no
  `fopen`, main-thread only (no ISR change). **Rate ranking:** 39.88 (MC0I) vs 39.85-39.87 (MI0I4, CA16).

**2026-09-23 -- PRE-REGISTRATION, HARDWARE ROUND (PGSB, 640x480): SB5O, SB5W, SB5L.** Operator GO
(question tool, 2026-09-23, relayed): ONE power-on for this round, power off at the end; **mains-cycle
hang recovery NOT approved -- a post-transfer hang means power off and report.** Binary
`build/abba/ags-0208-clean.exe`, expected `binary_sha12=513a187edcbb`, `build_dirty=0`, hash before and
after staging. Discipline as 8.3 (idle floor first; `[PGSB] ready` on the send witness / camera frame
1; card-state lock before any audio verdict; every witness frame reviewed; vcctrl's verdict ignored;
captures saved).
| tag | fixture | env |
|---|---|---|
| SB5O | 5 Days own flow (drive-start), `games/5days/ACSETUP-ON.CFG`, OPL3 | `DOSAGS_TAS_AUTO_EXIT_TICK=16000` |
| SB5W | same, WaveBlaster | + `SDL_HINT_DOS_AUDIO_BACKEND=wb` |
| SB5L | 5 Days `--startr 3` (diagnostic entry), 1000 ticks, OPL3 -- the SDL-log cell | + `DOS_PORT_LOG=1` |
SB5L carries the SDL debug trace (fsync per line) and so is NOT a timing cell: it exists to show 0194's
lock lines and the isr banner on the 486. SB5O/SB5W run without the trace.
**Predictions:** SB5O `midi_tick=isr`, `late_writes` about 0 (<= 1%) and `late_max_ms` <= 46 at the
~6 fps 640x480 intro (hardware SB4O on poll: 72% of events > 50 ms late); `plan_behind` = 0 unless a
stall exceeds the 2 s lookahead (the room-2 load was 2.6 s on SB4O -- if it recurs, `plan_behind` >= 1
there, which skips song time instead of rushing, recorded as such); `clk` within 1% of the RTC and of
the capture's music duration (host clock); `real_period_us` ~46590 (the PicoGUS's ~10989 Hz), i.e.
0208 correcting the device offset. SB5W `midi_tick=poll` (WB transport), lateness like SB4W (late50
~67%). Both: `pcm_irqs` = expected chunks + drains (SB4 accounting), `overwrites=0`, `silent_irqs`
recorded (bar 4 expected to fail as in SB4 on the lattice stalls -- that item is unchanged here).
SB5L: one `program code lock ... locked` line and the `<= 0` witnesses, `MIDI tick isr`. Memory:
`memory_min_free_kb` compared with SB4O/SB4W (152576/152320) -- the locked 4.85 MB is physical; the
KPI is the largest free virtual block, so it may not move; physical headroom not measured.
**Stop:** VOID not fixable in the round; a post-transfer hang (power off, report); a result that
contradicts every pre-registered reading.

**2026-09-23 -- HARDWARE ROUND RESULT (SB5O / SB5W / SB5L, PGSB 640x480), pending coordinator
verification. OPL3 on the ISR replay: 0 late writes on the real 486 at the ~6 fps intro; song clock
within 1%; 0194's lock engaged on the target. Target powered OFF 13:08:36 (0 mW); no hang.** Raw:
`tests/harness/results/SB5{O,W,L}-2026-09-23/`, floor `SB5-FLOOR-2026-09-23/FLOOR.log` (-68.4 dB; the
capture's audio reader was wedged again at power-on -- constant -91.0 -- and needed `vcctrl audio
release`/`acquire` plus a few seconds, host side). All cells: `binary_sha12=513a187edcbb`,
`build_dirty=0` (pre-stage sha256 recorded, run-hw's own staging hash check passed), one manifest
block, exit 0, card-state 0 `nosignal` (171/1, 159/1 locked/frozen; SB5L short). `[PGSB] ready` on
the boot capture (`SB5-FLOOR-2026-09-23/boot-pgsb-ready.jpg`) and camera frame 1 of every cell. Every
camera frame reviewed: SB5O/SB5W intro, title, room 3 through to the prompt; SB5L room 3 (frame 3 the
known `--startr` two-figure beat) and the prompt. No visual defect.

| cell | midi_tick | lateness | clk (song / RTC) | music in capture (host clock) | real_period_us | pcm / expected | silent_irqs | overwrites |
|---|---|---|---|---|---|---|---|---|
| SB5O OPL3 | **isr** | **late_writes 0 of 12233, late_max 0**, plan_behind 0 | 155734 / 156 s (0.998) | 202.5-357.0 = 154.5 s (song 155.7: 0.992, +-1.5 s) | **46127** | **1828 / 1828** | 20 (11 lines) | 0 |
| SB5W WB | poll | late50 3119 of 4502 (69%), late_max 432 | 126809 / 126 s (1.006) | 202-327.5 = ~126 s (0.994) | -- | **1624 / 1624** | 16 (11 lines) | 0 |
| SB5L OPL3 (SDL trace) | isr | late_writes 0 of 2546 | -- (short) | -- | -- | -- | 0 | 0 |

- **The prediction held for OPL3:** hardware SB4O (poll) had 72% of events > 50 ms late at this intro;
  SB5O (isr) has 0 late writes and `late_max_ms=0` -- every register write went out at its IRQ, at the
  ~6 fps intro, and `plan_behind=0` (no stall outran the 2 s lookahead, the 2.6 s room-2 load included).
- **Device rate (0208), measured on the target:** `real_period_us=46127` against nominal 46439 -- the
  PicoGUS plays ~0.68% FAST (~11100 Hz, the SB 2.0 time constant rounding to 166), not the -0.33% I
  predicted (TC 165). Without 0208 the music would have run ~0.7% fast; with it the song clock is
  0.998 of the RTC and 0.992 of the capture's host-clock duration (both within 1% and their
  resolutions). **WaveBlaster** stayed on the poll as predicted, lateness like SB4W (69% vs 67%).
- **Chunk accounting exact on both 5 Days cells.** `silent_irqs` again on the lattice stalls (the
  stall item, unchanged); `overwrites=0`.
- **SDL 0194 on the 486, raw from `SB5L-2026-09-23/SB5LSDL.LOG`:**
  `DOS: patch 0145 program code lock [start=0x19f0, etext=0x4db8a0) = 5086896 bytes: locked`;
  `DOS: patch 0145 DOS_LockCode(SoundBlasterIRQHandler) range length -64 <= 0 (end marker laid out
  before the function); not locked by range, covered by the program code lock (held)`;
  `DOS: patch 0145 DOS_LockCode(RingCopyOut) range length -3504 <= 0 (end marker laid out before the
  function); not locked by range, covered by the program code lock (held)`; plus
  `DosMidiBackend: MIDI tick isr (writes planned ahead, replayed by the SB IRQ)` and the 8-bit path
  (`force_8bit=1 dsp_ver=2`, 1268 IRQ-5 fires). **Memory:** 4.85 MB of the 16 MB now locked; the engine's
  `memory_min_free_kb` (largest free DPMI block, virtual) 152512 / 152512 / 154048 vs SB4O/SB4W 152576 /
  152320 -- unchanged; physical free pages are not measured by anything in dosags. No hang, no
  allocation failure, runs completed.
- **Deviation:** SB5O's first START driver found only one cursor blob per diff and stopped (no click);
  `drive-start.sh` gained a logged fallback (`DRIVE_FALLBACK_COUNTS="19 274"`, the value every earlier
  calibration on this machine produced) and was relaunched against the same running cell (clicked
  19:30:35 UTC; the title waited ~40 s longer). SB5W ran with the fallback armed; its calibration
  succeeded on its own.
**Captures for the listening page:** `SB5O-seg01.ogg`, `SB5W-seg01.ogg` (and `SB5L-seg01.ogg`, short).

**2026-09-23 -- PRE-REGISTRATION, isr pause/stop (follow-up 4).** SDL 0195 (`SDL_DOSMidiDeferPause`:
hold + keep the queue + key off what the replay left sounding; resume shifts the queued stamps;
`SDL_DOSMidiDeferKeysOn`) and ags 0209 (pause/resume use it; stop/song change already silence via
0207). Binary `db4960959cf2`; throwaway probe `943561433abf` (`DOSAGS_MP_PAUSE="1000,1400,2400"`: pause
at loop tick 1000, resume at 1400, stop at 2400; after pause and stop it waits two IRQs and logs
`keys_on_after_1irq`). Cells (DOSBox-X `--sb-live`, 5 Days `--startr 3`, 3000 ticks, F12+W WAV):
**MP1** (isr), **MP1P** (poll control, `DOSAGS_MIDI_TICK=poll`). **Bars (MP1):** `keys_on_after_1irq=0`
at the pause and at the stop; the WAV at the idle floor through the pause (~400 ticks) and music back
after the resume; `late_writes=0`, `plan_behind=0`; `events` after resume continue (no skipped song).
Control MP1P: the WAV shows whatever the poll's pause did (held notes expected). Then gate, review,
re-pin.

**2026-09-23 -- MP1/MP1P result: the isr pause is silent at once; bars met.** Raw:
`tests/harness/results/MP1-2026-09-23/`, `MP1P-2026-09-23/` (STDOUT, RUNMANI, the WAV as `.opus`, the
probe diff). **MP1 (isr):** `MPPAUSE tick=1000 keys_on_after_1irq=0`, `MPRESUME tick=1400`,
`MPSTOP tick=2400 keys_on_after_1irq=0`; final `midi_tick=isr, isr_writes=3091, late_writes=0,
late_max_ms=0, qfull=0, qdropped=0, plan_behind=0, events=1656`. The WAV: the 24-27 s windows hold
the release tail of the notes keyed off at the pause, 28-31 s at the idle floor, music back at ~33 s
and continuing the song (events keep counting after the resume; no jump back to the start). `clk=49858/60s`
is expected here, not a clock fault: the RTC also counts the ~10 s pause, which song time does not.
**MP1P (poll control):** no silence through the pause -- held notes at about -19 dB, the old
behaviour (the poll path has no key-off on pause). Its `keys_on_after_1irq=0` means nothing: key
tracking lives in the replay, which the poll never runs, so it reads 0 by construction. Late figures
on the poll are the emulator's (`late_max_ms=34`, `late50=0`), not a hardware claim. **Open before
re-pin:** the full gate on `db4960959cf2` (gate-0209's first run is void -- see below), then
`/sdldos:review` on SDL 0195 + ags 0209, then pin `build/abba/ags-0209-clean.exe`.

**2026-09-23 -- gate-0209 first run VOID (harness, not the binary).** Only 6 of 14 rows ran (the
outer `timeout 3000` I wrapped it in expired). Row 1 (`bench8-alias-idle`) checked by hand: its own
stages, 5 frames each, A == B. `bench8-alias-gui` FAILED 5/5 with a 720x417 bbox, and its B frames are
a **DOS prompt**, not the game: another DOSBox-X window was on display :211 while B ran, and
`--freeze-capture` photographs the root window. Separately, both watchers took the FIRST
`dosbox-x ... MOUNT C` in `ps` host-wide, so with parallel workers they could watch, photograph and
kill another run. **Fix, `tests/harness/run-dosbox.sh`:** the runner starts in the background first
and both watchers find THIS run's stage by walking `ps` ancestry down from its PID (`own_stage`); the
kill matches that stage exactly; and a display that already has a DOSBox-X window is refused (checked
on the display's window tree, because other workers' `/proc/<pid>/environ` is not readable from here).
**Test WATCH1** (`tests/harness/results/WATCH1-2026-09-23/`): two `--arms gui` gates at the same
time on :211 and :212 -- six distinct stages, 5 frames each, A == B 5/5 on both, control fails as
required on both, frames are the game (witness PNG); a third run aimed at the busy :211 was refused
with exit 1. The gate re-runs in full once no `--sb-live` run is on the host.

**2026-09-23 -- gate-0209 full run: 12/14, both failures the known intermittent rows; re-pinned
`build/abba/ags-0209-clean.exe` (`db4960959cf2`, byte-identical to a clean rebuild).** Raw:
`build/ws/gate-0209b/` (out/, rerun1/, rerun2/). Host quiet for the whole run (I was the only
DOSBox-X user; watcher fix in). 12 rows A == B, all 14 controls fail as required.
- `agsquest-alias-y60` FAIL: the one-tick autopilot divergence, **now starting at the splash**
  (`phase=splash status=ok` tick 81 in A vs 82 in B), so every later freeze lands a tick apart
  (100/101 ...) and the frames differ from tick 1600. Sound is off in this row. Solo re-runs: 2/2
  clean (10/10 pairs each). A sound-independent one-tick nondeterminism at startup; the coordinator
  is queueing it as its own lab thread.
- `shards-alias-512x384` FAIL: tick 100 only, in all three runs (full gate: froze 100 vs 101;
  rerun1: 101 vs 100; rerun2: the known 120672 px bbox `(512, 513, 1152, 913)`); ticks 300-900
  equal every time. The pre-existing Shards tick-100 defect.
- Both rows go into `tests/ratchet.yaml` as QUARANTINED when that file lands (flake rule).
Accepted by the coordinator pending the solo re-runs, which are above.

**2026-09-23 -- hub lock wired in; subtree at hub `a8379a3`.** `.sdl-dos-ports` bumped (86ea2b3:
the host-wide DOSBox-X lock, `.who` cleared on release, ratchet.sh). New
`tests/harness/dosbox-lock.sh`: EXCLUSIVE once around a series, `DOSBOX_LOCK_HELD=1` exported, `.who`
removed on release. Taken by `gate-alias.sh`, `gate-present.sh`, and `run-dosbox.sh` for
`--freeze-capture` / `--screen-series` / `--sb-live` (a no-op inside a gate); plain functional runs
take SHARED inside the hub's `dosbox-run.sh`. **Test LOCK1** (`tests/harness/results/LOCK1-2026-09-23/`):
a one-row gate (22:24:41) and an `--sb-live` cell (22:24:44) started together. The cell printed
"waiting ... holder: gate-alias.sh (alive)", and its DOSBox-X started at 22:26:01, after the gate
released at 22:26:00. The gate's two runs held the lock throughout (A == B ok), and afterwards `.who`
was removed and the lock was free. My first LOCK1 attempt was void: I passed `ags-0209-clean.exe` as
`AGS_EXE`, which is not an 8.3 name, so DOS said "Bad command"; it was stopped by PID and re-run with
the same bytes as `ags.exe`. The rules are in `tests/harness/RUNNER-DEFAULTS.md`.

**2026-09-23 -- PRE-REGISTRATION MP2/MP2C: SDL 0196 (a nested hold release keeps a paused replay
held).** Patch `patches/SDL/0196-midi-hold-release-keeps-pause.patch`: `SDL_DOSMidiDeferHold(false)`
releases to `g_mdq_paused ? 1 : 0` instead of 0. Probe: the MP probe (throwaway) plus a fourth
value, `DOSAGS_MP_PAUSE="1000,1400,2400,1010"`: at loop tick 1010, while paused, it reads
`SDL_DOSMidiDeferStats` `written`, calls `SDL_DOSOpl3Detect()` (whose wrapper holds, then releases),
waits 5 IRQs and logs `MPNEST written_during=<delta> keys_on=<n>`. Cells (DOSBox-X `--sb-live`,
5 Days `--startr 3`, 3000 ticks, the MP1 recipe, under the exclusive lock): **MP2** = the probe on the
0196 build; **MP2C** = the same probe on the 0209 build (the control: the defect present).
**Bars:** MP2 `written_during=0` and `keys_on=0`; MP2C `written_during>0` (the replay ran during the
pause -- if MP2C also shows 0 the test has no power and MP2 proves nothing); both resume at 1400 and
reach the stop at 2400 with `late_writes=0` and `plan_behind=0`. Then the full gate on the 0196 build
and a re-pin.

**2026-09-23 -- MP2/MP2C RESULT: SDL 0196 holds a paused replay through a nested hold; the control
reproduces the defect. Bars met.** Raw: `tests/harness/results/MP2-, MP2C-2026-09-23/` (probe diff
included; exclusive lock, display :211).

| cell | build | MPNEST (tick 1010, paused) | pause / stop keys_on | late_writes | plan_behind |
|---|---|---|---|---|---|
| MP2 | 0196 probe `c6b351e1c7de` | `written_during=0 keys_on=0` | 0 / 0 | **0** | 0 |
| MP2C | 0195 probe `2713a11fd0be` | **`written_during=30 keys_on=1`** | 0 / 0 | **16** (max 185 ms) | 0 |

On 0195 the Detect wrapper's release let the ISR replay 30 queued writes in the middle of the pause
(a note left sounding), and resume then replayed the rest late. On 0196 nothing plays until the
resume. Both cells resume at 1400 and reach the stop at 2400 (events 1660 / 1658).
**Deviation (voids the first MP2C):** the first control exe differed from the MP2 exe only in its
9 sha-stamp bytes. Taking 0196 out of `patches/SDL/` and running `make patches` moved vendor/SDL to
0195, but `make sdl3` rebuilt nothing, because libSDL3.a's prerequisites are the patch files and
none was newer. So that "control" carried 0196 (it showed 0/0: no power, as the pre-registration's
own rule caught). Fix: `touch` a patch in the series after each roll-back/roll-forward, then check
that the lib really recompiled and that the exes differ by more than the stamp (the real control: 75
bytes). vendor/SDL is back at 0196; the clean build `634d0364412e` has a recompiled lib and differs
from 0209 in 78 bytes. Its gate is next.

**2026-09-23 -- STW0/STW1 RESULT: a play's cost is decode (~65%) and first-play file I/O (~32%),
all inside the script's play call; the other stalls are walk pathfinding, not sound. Removing the
play cost is estimated to lift SB2C1's whole-run from 38.61 to ~38.9-39.0, short of the 39.2
floor on its own.** Raw: `tests/harness/results/STW0a-, STW1a-, STW1b-2026-09-23/` (probe diff
included). The lock held each cell exclusively (STW0a waited for the hub ratchet's control); display
:211; probe `e61660b27a4c`. Code executed: 9 plays in each sound-on cell, each with its `stwplay` and
`stwtick` line; `pcm_irqs` 582/644, `overwrites=0`, `late_writes=0`; STW0a (sound off) 0 plays. The
DOSBox-X rate is the same in all three (steady 40.08, one stall at tick 1).

| DOSBox-X, room-3 plays | plays | load ms | io | decode | convert | copy | voice (slot) | script besides the load |
|---|---|---|---|---|---|---|---|---|
| STW1a | 6 | 128.8 | 43.3 (33.6%) | 82.1 (63.7%) | 1.42 (1.1%) | 0.93 (0.7%) | 0.04 | 1.8 ms over 6 ticks |
| STW1b | 6 | 137.7 | 43.3 (31.5%) | 90.9 (66.0%) | 1.49 (1.1%) | 0.89 (0.6%) | 0.04 | 1.9 ms over 6 ticks |

Per clip on DOSBox-X: sound 10 on first play 61-67 ms (io 28.5-28.7, decode 31-37), on a repeat
24.5 ms (io 0, decode 23.8); sound 9 first 21-25 ms (io 12.3), repeats 8-16; sound 3 7-12 ms.
- **H1 MET:** decode + convert = 64.8% / 67.1% of the sound-attributable time.
- **H2 MET:** `io_us` is non-zero only on the first play of each clip, and 0 on every repeat.
- **H3 MET:** the copy is 0.6-0.7% and the voice build 0.03%. The mixer poll (`apoll`, ~10-12 ms
  per tick on DOSBox-X) is steady per-tick cost, not play cost.
- **H4 REFUTED as framed.** On a play tick, script work besides the load is 0.2-0.4 ms on DOSBox-X,
  and the 486's sound-off stalls are not play ticks. In every 486 cell of 8.2, and in S2F2/S2F3,
  each stall that does not follow a play follows a `MoveCharacter: request move` (walk pathfinding):
  - SB2A1: 858 / 319 ms and 1187 / 251 ms;
  - SB2C1: 800 / 347, 1131 / 281, 1578 / 272 and 3835 / 252;
  - S2F2 939 / 319 and S2F3 911 / 319.
  The earlier "ambient-timer script stall" reading is corrected in place above.
- **486 cross-check of the io share:** sound 10's first play costs 595-656 ms and its repeats
  299 ms (SB2B1, cache hit), so first-play io is ~50% on the 486. That agrees with DOSBox-X's 43-47%
  for this clip.

**Estimate (method as pre-registered; different runs and binaries, DOSBox-X shares applied to 486
times):**
- SB2C1 vs its own round's sound-off arm SB2A1: 4999/38.61 - 4999/39.18 = 1.88 s more wall time.
- SB2C1's play ticks cost ~1.1 s of that: sound 10 656 ms, sound 9 253 ms, and sound 3's
  sub-threshold ticks ~125-190 ms each, less a normal 25 ms frame per tick.
- The rest: walk stalls crossing the threshold more often with sound on (1152 vs 570 ms), and the
  steady-rate mixing cost (steady 39.89 vs 40.03).

| change | recovered on SB2C1 | whole-run |
|---|---|---|
| play io only (first plays) | ~0.35 s | ~38.71 |
| decode only | ~0.72 s | ~38.83 |
| decode + io, i.e. the whole play off the play tick | ~1.1 s | ~38.94 |

The floor is 39.2 = 127.53 s. **Fixing the plays alone does not reach it.** The sound-off arm itself
scored 39.18 in that round, so walk pathfinding (~250-370 ms per click that crosses, 1-4 per run,
sound-independent) is the other lever Gate S16 needs. The steady mixing cost is the third.

**What this implies for S16 (not acted on):**
- Take the play off the main-thread tick: decode at room load, or decode ahead from the cache.
- Separately, measure and reduce the pathfinding cost, since that stall happens with sound off too.
- Only a hardware probe cell measures the 486's own split, and that needs a GO.

**2026-09-23 -- S16 A, PRE-REGISTRATION RT1a/RT1b: where a walk request's 250-370 ms goes (MEASUREMENT
ONLY, DOSBox-X).** *Read first:* 5 Days is data version 22, so it runs the **legacy** pathfinder
(`route_finder_impl_legacy.cpp`, "PathFinder v2.00", 1998-99). Every `MoveCharacter` request that
cannot see its destination directly does, on the main thread:
1. `prepare_walkable_areas(chac)` (the mask with blocking areas);
2. `is_route_possible`: a copy of the whole mask, two full passes over it (the second column-major,
   per-pixel `GetScanLineForWriting`), an Allegro `FloodFill`, and, if the destination is not
   walkable, a nearest-walkable sweep with a `sqrt` per candidate;
3. a 2-byte-per-pixel `beenhere` malloc;
4. `find_route_dijkstra`: a memset of `beenhere`, a mask-sized `parent` malloc, and a main loop
   that re-scans EVERY visited cell (up to 5000) on every pass, with a `%` and a `/` by the mask
   width per cell;
5. if that fails, the recursive `try_this_square`, and the whole thing again with `leftorright=1`;
6. path smoothing: `can_see_from` (Allegro `do_line` with a `getpixel` callback per pixel) from each
   stage to every remaining waypoint.

*Probe* (throwaway `80439d6f00ec`, diff saved with the results): per-phase uclock buckets for each
of those, pass/visited/`can_see` counts, and one `routewhat` line per request with src, dst,
stages and an FNV hash of the waypoints. `DOSAGS_RT_BENCH` replays the **13 exact requests SB2C1
made on the 486** (`71,126,34,128;51,141,0,128;50,145,285,69;188,125,0,0;75,115,84,173;79,144,319,173;260,145,319,186;260,145,34,186;48,145,0,156;48,145,0,157;48,146,319,186;188,146,34,186;48,145,0,156`) for the player character, 3 times each, into a scratch MoveList (no
character moves), at loop tick 1100 in room 3 (`--startr 3`, sound off, Gate 3 cfg). **RT1a, RT1b**
are the same cell twice.
**Predictions:**
- H1: the Dijkstra main loop is the largest phase on the requests that cost the most, and it scales
  with passes x visited (`iter_sum`).
- H2: `is_route_possible` (copy + scans + flood) is a near-constant per-request cost, largest in
  share on the short requests.
- H3: `prepare_walkable_areas` < 10% of a request.
- H4: smoothing is under 20% except on multi-stage routes.
**Mapping to the 486:** the requests that crossed the stall threshold on the 486 (SB2C1 ticks 800,
1131, 1578, 3835) should be the ones with the highest DOSBox-X `total_us`. If the ranking disagrees,
the emulator's relative costs mislead (divides, memory bandwidth), and the 486 split probe decides.
**Void if:** fewer than 13x3 bench lines, or the room at tick 1100 is not room 3. The hashes must
agree between RT1a and RT1b (a deterministic finder); any later fix must reproduce every hash.
**Amendment after RT1a, before RT1b (same day):** the probe that ran is `3da89ed18aca` (the
pre-registered one plus reading the bench list from `RTBENCH.TXT`, since a 13-pair SET line exceeds
DOS's ~127-character command line). RT1a's per-call `rp_scans` fell from ~17 to ~2 ms across one
tick for identical work: DOSBox-X's cycles=max auto-adjust, so shares within a tick are not
comparable at cycles=max. Added **RT2a**: the same bench at FIXED cycles
(`tools/dosbox-x.conf`: core=normal, cycles=fixed 40000), taking the lock SHARED (hub bb5482c).
RT2a's split is the one reported; RT1a/RT1b stay as the route-hash determinism check.

**2026-09-23 -- RT RESULT: a walk request's time is the walkable-mask analysis, run twice, plus the
Dijkstra loop on long routes.** Raw: `tests/harness/results/RT1a-, RT2a-2026-09-23/`.
- RT2a (fixed 40000, all 39 bench lines, room 3): each `is_route_possible` call spends **44.1 ms in
  the two mask passes** (`rp_scans`), and each successful request calls it **twice** (the
  nearest-walkable retry), so that is **88.3 ms per request**.
  - Request totals: 98-231 ms (the 3 immediate failures: 49 ms).
  - Dijkstra main loop: 0-122 ms, scaling with `iter_sum` (up to 50960 visits).
  - Smoothing: <= 11.7 ms. Flood fill: 5.0 ms. Mask copy: 1.7 ms. `beenhere` memset: 1.1 ms.
    `prepare_walkable_areas`: 0.74 ms.
- **H1 REFUTED:** the Dijkstra loop is the largest phase only on the longest request (122 vs 88 ms);
  everywhere else the scans are.
- **H2 MET, with a twist:** near-constant (44.1 ms at fixed cycles), and doubled by the retry.
- **H3 MET:** prep 0.3-1.5%. **H4 MET:** smoothing <= 6.5%.
- Route hashes are identical between RT1a (cycles=max) and RT2a (fixed) on all 39 lines, so the
  finder is deterministic. RT1b was dropped: it queued for the exclusive lock behind a stream of
  shared holders for over an hour, and RT1a == RT2a already makes its point.
- At cycles=max the per-call scan time drifted from ~17 to ~2 ms within one tick (the
  auto-adjust), the reason for the fixed-cycles rule.
- DOSBox-X's normal core charges a divide or a cache miss like any other instruction, so it
  understates the Dijkstra loop's `%`/`/` per visit and the column-major pass's misses on the 486.
  Only the 486 split probe settles the 486's own shares (hardware list).

**Fixes, bit-exact by construction (S16 A):**
- **ags 0211:** keep the mask analysis (granularity table + normalised mask) with a copy of the mask
  it came from, and reuse it on a byte-identical mask. The retry call always hits; so does every
  later request while nothing on the mask has moved. Cost: 2 x 64 KB and a row compare per call.
- **ags 0212:** Dijkstra keeps each visited cell's x/y beside its index instead of dividing by the
  mask width per visit per pass.

**PRE-REGISTRATION RT3B/RT3N (witness for 0211/0212).**
- One probe (per-request `routewhat`: total, prep, route hash; no finder instrumentation), built
  on 0210 (**RT3B**, `24dc534cc896`) and on 0212 (**RT3N**, `49de5ac09378`).
- Bench: the 13 recorded requests x3, then **300 random requests** (`DOSAGS_RT_RAND=300,7`: an LCG
  seed, walkable source, any target), at tick 1100 in room 3.
- Fixed 40000 cycles, lock shared.
- **Bars:**
  1. Every request's ok / stages / hash identical between RT3B and RT3N, in order (339 lines).
  2. RT3N's bench total falls: each 13-list request by >= 44 ms (one pass pair saved), and the
     second and third repeats by ~88 ms (the mask unchanged).
  3. The game's own walk results in the full gate stay A == B (next).
- **Void if:** fewer than 339 lines in either, or the room is not 3.

**2026-09-23 -- RT3 RESULT: routes identical, walk requests 56-57% faster at fixed cycles. Bars 1-2
met.** Raw: `tests/harness/results/RT3B-, RT3N-, RT3N2-2026-09-23/`.
- **All 339 requests** (13 x3 recorded + 300 random) have the same ok / stages / route hash, in order,
  in RT3B (0210) vs RT3N and vs RT3N2. 330 routes found, 9 refusals.
- **RT3N** (first 0211) cut 42-43%. A repeat saved ~62 ms, not ~88, because the cache's hit test was
  DJGPP's `memcmp`, a byte loop (8 instructions a byte, verified by disassembly): ~13 ms per 64 KB
  compare at fixed 40000. 0211 now compares 32-bit words (re-exported; still only the equality
  test).
- **RT3N2** (final 0211 + 0212):

  | requests | before (mean) | after (mean) | change |
  |---|---|---|---|
  | 13-list x3 | 124.0 ms | 52.9 ms | -57.3% |
  | 300 random | 131.6 ms | 57.7 ms | -56.2% |

  - A repeat of a short request: 98-101 -> 15-19 ms.
  - The first request (cache miss): 103 -> 64 ms.
  - The worst request: 256 -> 176 ms. That is the long-route Dijkstra loop, whose per-visit divides
    (0212) the emulator does not charge for, so the 486 gains more than this shows.
- Gate on the final build (`4612b69a0887`: SDL 0196 + ags 0210-0212) next. The 486 split probe
  (before/after) goes on the hardware list.

**2026-09-23 -- gate-0196 (SDL 0196 on the 0209 ags): 14/14 A == B, every control fails as
required** (both intermittent rows passed this time). **Re-pinned
`build/abba/ags-0209-sdl0196-clean.exe`, `binary_sha12=634d0364412e`.** Raw: `build/ws/gate-0196/`.

**2026-09-23 -- SDL 0197 + ags 0213 (content-active underflow padding; lab-journeys' mi-stall-isr
finding, pcm_unaccounted -156).** Built, not yet witnessed.
- *Design (b), SDL side:* the core records per iteration what the bound streams supplied
  (`dos_pull_got`/`dos_pull_wanted`, `SDL_PLATFORM_DOS` only). PlayDevice sends a buffer the
  streams supplied NOTHING to through the silence gate even while content is active (it is the
  core's underflow padding), and writes a partly filled buffer as before.
  - Counters: `underflow_pads`, `partial_pulls` (ags 0213 status line).
- *Why not (a), on the ags side:* the ring is refilled after a stall by the background thread's
  iterations between engine pumps, and the engine cannot see those per chunk.
- *Witness, to pre-register:* the mi-stall-isr cell's `pcm_unaccounted=0` with forced stalls, and
  CA16B/CA8-style accounting still exact without them. After round A.
- The hub's copy of 0192 (0143) needs the same caveat.

**2026-09-24 -- HARDWARE ROUND A, staging record (operator GO relayed 2026-09-23; one power-on, one
guarded recovery per run, power OFF at the end).** The cells, bars and predictions are the lab
workers' own committed pre-registrations, not re-derived here:
- lab-wb `LAB-WB.md` 6.5 / 6.7 (`lab/wb` `75f93f76`, worktree head `0ebe60ea`);
- lab-metric `LAB-S32.md` 5 (`lab/metric` `f3b49835`);
- lab-mmd `LAB-MMD.md` 8 / 10 (`lab/mmd` `a738cc11`).

Binaries were copied into `build/ws/roundA/` and every sha256 matched its record before staging:
- `wb-clean.exe` `4c9e8275...` = lab-wb `build/lab/clean/ags.exe`, `40c554604d6a`;
- `wb-probe.exe` `0949f0e6...` = lab-wb `build/lab/probe/ags.exe`, `d17c761c6adc`;
- `mmd-base.exe` `b395af34...` = lab-mmd `AGSBASE.EXE`;
- `mmd-probe.exe` `d0c05016...` = lab-mmd `AGSPROBE.EXE`;
- `BWPRB32.EXE` `37fc4225...`;
- `CWSDPMI.EXE` `2de899fe...` (the same bytes as this repo's `vendor/cwsdpmi`).

**Order**, with the only hang risk last:
1. WBH0, WBH2, WBH1, WBH4, via `build/ws/roundA/cellA.sh`: SB5W's shape, PGSB 640x480,
   `games/5days/ACSETUP-ON.CFG`, drive-start for the own-flow cells.
2. BW32, via `run-probe-hw.sh`.
3. HW-MMD-0, HW-MMD-1, HW-MMD-2 (S2M1's shape).
4. WBH3, last; WBH3K is ready and not run unless WBH3 hangs.

**Deviation, BW32:** `run-probe-hw.sh` runs the probe from the target dir (`C:\DOSAGS`) into
`PRBOUT.TXT`, not from `C:\` into `PRBOUT32.TXT`, and runs MODE12 itself. The collected file is
renamed to the lab's name `HW-486-66-2026-09-24-bwprb32-PRBOUT32.TXT`.

**Each cell records** the pre-stage, staged and post-run hashes; `[PGSB] ready` on the send
witness; the card-state lock before any audio verdict; every witness frame reviewed.

**2026-09-24 -- PRE-REGISTRATION, HARDWARE ROUND B (my 16-bit cells; runs only after the
coordinator verifies round A).** The fixture is 8.2's SB2C1 exactly, i.e. the S16 fixture:
- `run-hw.sh 5days --timeout 1800 --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env
  DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 3 --extra-file
  presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG`;
- `drive-walk.sh <TAG> 25 2 90` alongside;
- PGSB, OPL3, sound on.

Audio is judged by counters (the capture is blind at 512x384).
- **Base:** `build/abba/ags-0209-sdl0196-clean.exe`, `634d0364412e`.
- **New:** `build/ws/gate-0212/ags.exe`, `4612b69a0887` (SDL 0196 + ags 0210-0212); pinned only if
  its gate passes. SDL 0197 / ags 0213 are NOT in this round (their DOSBox-X witness comes first).

| order | tag | binary | what it answers |
|---|---|---|---|
| 1-4 | **S16B1, S16N1, S16N2, S16B2** (ABBA) | base / new / new / base | whole-run effect of 0210-0212 at the S16 fixture |
| 5 | **STWH** | STW probe `e61660b27a4c` | the 486's own play split (io / copy / decode / convert / slot) and the stall ticks |
| 6-7 | **DECHO, DECHN** | DEC probes `0165bac69ff5` / `87898543c1ae` | per-clip Open time before/after 0210 on the 486, and the clip hashes |
| 8 | **RTHS** | RT phase probe `3da89ed18aca`, `DOSAGS_RT_BENCH=@RTBENCH.TXT` (the 13 SB2C1 requests x3) | the 486's own pathfinder phase split |
| 9-10 | **RTHB, RTHN** | RT3 probes `24dc534cc896` / `484527264cb9`, bench + `DOSAGS_RT_RAND=300,7` | before/after route cost on the 486; route hashes |

- RT/DEC/STW cells use the same fixture, with sound on for STWH/DECH* and sound off for RTH*
  (`ACSETUP-OFF-512X384-ROUND.CFG`), and the probes' own tick exits (1300 / 1150).
- The `RTBENCH.TXT` spec goes on as an extra file.

**Predictions / bars:**
- **(1) ABBA:** new whole-run `tick_rate` above base in BOTH pairs by >= 0.2 ticks/s.
  - Estimate: +0.3 to +0.7, from STW's decode share, RT3's 56% on walk requests, and SB2C1's four
    walk stalls (~1.15 s) and plays (~1.1 s).
  - Reaching 39.2 is not a bar of this round.
  - pcm accounting exact in all four, `overwrites=0`, `late_writes=0`.
  - Walk-stall count and length recorded per cell (`stallwhat` after `MoveCharacter`).
- **(2) STWH:** decode + io >= 80% of each play's cost, as on DOSBox-X (io ~50% on first plays per
  SB2B1's 595-656 vs 299 ms).
- **(3) DECH:** each clip's `pcm`/`dev` hash equals DOSBox-X's (sound2 `1732254d`, sound3
  `1471e9e1`, sound9 `62be796a`, sound10 `92545aef`). sound10's Open falls >= 70%; the hash loop
  is the same probe overhead in both.
- **(4) RTHS:** the mask passes (`rp_scans`) are the largest phase on the short requests. On the long
  ones the Dijkstra loop's share is larger than DOSBox-X's (the divides).
- **(5) RTHB/RTHN:**
  - All 339 route hashes identical to each other and to DOSBox-X's RT3.
  - Mean request time down >= 50%; the long-route cut exceeds DOSBox-X's 32% (0212's divides).
- **Void if:** the room is not 3; `[PGSB] ready` is missing; a probe line is missing; a binary hash
  does not match before or after staging.
- **Stop:** a second hang in a run (the one guarded recovery per run is authorised); power OFF at
  the end.
- lab-metric's 0230 counter off/on pair and C1 off/on x2 (if its G1 passes) are added from
  lab-metric's own staging record when it is committed.

**2026-09-24 -- ROUND A, cell WBH0 (raw; lab-wb scores it against WBH2).**
`tests/harness/results/WBH0-2026-09-24/`.
- Target power-on at 01:24Z; `[PGSB] ready` on the send witness (MPU-401 330, sysex delay off).
- sha256 `4c9e8275...` pre-stage = staged = post-run; `binary_sha12=40c554604d6a`.
- run-hw exit 0, no recovery.
- `midi=wb, midi_tick=isr` (blind kind 2), `isr_writes=13294, late_writes=0, late_max_ms=0,
  plan_behind=0, qdropped=0`, `clk=124570/124s`, `real_period_us=46127`.
- `pcm_irqs=1396, silent_irqs=9, overwrites=0, drains=17`; `tick_rate=25.51`.
- Capture: above -60 dB 18:28:53-18:39:06 (local); card-state locked 158 of 160 samples.
- All 40 camera and 40 capture frames reviewed: intro, title, START, room 3 through the exit;
  no visual defect.
- The garble check (chroma, onsets) is lab-wb's, against WBH2's capture.

**2026-09-24 -- ROUND A RESULT (raw, pending coordinator verification): STOPPED at HW-MMD-0 by the
operator's rule (second hang in one run). Target powered OFF 02:5xZ (0 mW confirmed).**
Every cell's sha256 was identical pre-stage, staged and post-run. All ran on PGSB.

| cell | exit | recovery | key raw fields |
|---|---|---|---|
| WBH0 | 0 | none | above |
| WBH2 (poll) | 0 | none | `midi_tick=poll, late_max_ms=444, late50=3132 of 4558`, clk 128519/128s; `pcm_irqs=1605, overwrites=0`; tick_rate 25.44 |
| WBH1 (rtc pump) | 0 | none | `midi_tick=rtc, events=2718, isr_writes=461, late_writes=0, plan_behind=554, clk=69325/123s`, `rtc_hz=2048, rtc_ticks=1382, bios_waits=212, lat_max_us=28792, rs_skipped=30`; tick_rate 25.56 |
| WBH4 (rtc, SDL log) | 0 | none | `rtc_ticks=2202` over ~42 s, `bios_waits=342`, clk 42173/42s, `plan_behind=0`. SDLDBG: `0230 RTC pump installed -- IRQ 8 at 2048 Hz (register A 0x26 -> rate bits 5) ... PIE was off, IRQ 8 was unmasked`; `uninstalled -- rate bits restored to 6 ... ticks=2202`; 0145 lock held |
| BW32 | 0 | n/a | file ends `done`. **Anchor 0x111 LFB memcpy 614400 B = 27.30 MB/s (valid)**. 32 bpp is mode **0x1B0** (0x112 is 24 bpp here): LFB memcpy 7.67-7.70 MB/s, stosl 10.22, banked 7.3, rects 5.7-7.6 MB/s. 24 bpp 0x112: 27.2 MB/s |
| HW-MMD-0 | **3** | the first post-collection hang was RECOVERED by the reboot chord (02:46Z); the second was **STOPPED-second-failure** 02:53:35Z (screen: dos-prompt) | the game ran; **RUNMANI/STDOUT on the target (`C:\DOSAGS`), uncollected**. Fetch them at round B's power-on, BEFORE any staging overwrites them |

- **Not run:** HW-MMD-1, HW-MMD-2, WBH3 (and WBH3K).
- **WBH1 anomaly:** the RTC pump ticked ~11/s (1382 in 123 s), and in WBH4 ~52/s (2202 in 42 s),
  against a programmed 2048 Hz. Song time ran at 0.56x real in WBH1 (`plan_behind=554`). DOSBox-X
  never showed this. `bios_waits` is nonzero in both. Whether the BIOS's INT 15h/86h waits clear PIE
  or reprogram register A under the pump is a hypothesis for lab-wb, not a finding.
- **Witness:** WBH2/WBH1 intro, title and room 3; WBH4 room 3. Capture above -60 dB in the music
  windows; card-state 1 unlocked sample each. HW-MMD-0's frames are saved (43 camera), no sheet
  (the run stopped before it was built). The capture is blind at 512x384, as expected.
- The BW32 file is copied to lab-metric's results path for scoring there.

**2026-09-24 -- WITHDRAWN: every past "control FAILS as required" claim for the gate row
`shards-alias-512x384`.** That row's control never had power. The control (`DOSAGS_BREAK_0193=1`,
0193's dirty-mark carry off) equals B at ticks 300-900 in every recent gate (gate-0209b, gate-0196,
gate-0212), because Shards' title is static after tick 100. Its only "failures" were the
intermittent tick-100 frame, the same flake A==B fails on. The fix (freeze ticks where Shards has
motion) comes after round B; until then the row judges nothing.

**2026-09-24 -- CORRECTION to round A's stop: HW-MMD-0 did NOT hang. It was a harness naming bug.**
- The engine names the manifest from `DOSAGS_LOG_TAG`: uppercased, `[A-Z0-9_]` only, 8 characters
  (`quit.cpp`, patch 0044). So tag `HW-MMD-0` wrote **`HWMMD0.LOG`**.
- run-hw asked for `HW-MMD-0.LOG`. Every collection came back not-ok, the loop read that as the
  post-transfer dead link, spent the one recovery (the reboot chord, 02:46Z) and then stopped as a
  "second failure".
- At round B's power-on, `C:\DOSAGS` held `HWMMD0.LOG` and `STDOUT.TXT` (both 7:36p) with a
  complete run:
  - `exit_code=0, build_dirty=0, binary_sha12=234a4db92f12`;
  - `tick_rate=26.75, tick_rate_steady=29.09`;
  - `Now in room 50`, and the end-of-run dumps present.
  Fetched with verified get-files into `results/HW-MMD-0-2026-09-24/fetched-2026-09-24/` (copied to
  RUNMANI.LOG / STDOUT.TXT beside it). HW-MMD-0 is a complete cell.
- **Fixed in `run-hw.sh`:** `MANIFEST_LOG` is derived from `$TAG` with the engine's own rule and
  used for get-file, the ok check, `pulled save` and the RUNMANI copy.
- **My own slip in the fetch:** its first version took the input lock itself, so get-file's reboot
  chord was refused (the machine was never reset) and `pulled save` handed back copies from an
  earlier pull. Those are kept as `fetched-2026-09-24-STALE-refused/` and not used. The fetch now
  saves only files the job itself reports ok.
- **Earlier "post-collection hangs" re-read (coordinator's question):** HANGTEST1, HANGTEST2 and
  HANGTEST3 (2026-09-22) are explained by the same bug. Their 9-character tags truncate to
  `HANGTEST.LOG`, which is on the target (40,433 bytes, 09-21 9:02p). Every one of their
  "get-file refused" collections asked for `HANGTEST1..3.LOG`.
  - S2S1 and S2S2 have 4-character tags, so this bug does not explain them, and no `S2S*.LOG` is
    on the target: a different cause, still open.
  - C1A2, RBB1 and RH090233 (recovered, not stopped) are name-safe too.
  - Annotated in `results/hw-recoveries.log`; HARDWARE.md is the coordinator's.

**2026-09-24 -- OPERATOR DECISION, boot config: "Boot config now, auto-detect later".** Basis:
lab-wb's WBH0 verdict, CLEAN (chroma 0.958 vs bar 0.646, onsets +2.8%, none in rests).
- The g2k PGSB profile gets `SET SDL_HINT_DOS_AUDIO_WB_TX_DELAY=0` and
  `SET SDL_HINT_DOS_AUDIO_WB_DRR_POLL=0`, with the reason in comments, and README.TXT's PGSB
  section to match: g2k `64814fd`. Scoped to those two lines on PGSB only.
- **Deploy** with vcctrl send-file at the START of the next hardware round, never mid-round, then
  one boot into PGSB with `SET` to verify both.
- dosags README gains a line for other PicoGUS + WaveBlaster owners.
- Auto-detection (lab-wb researching a rule) is meant to replace it.

**2026-09-24 -- ROUND B, S16 ABBA and RTHB/RTHN (raw; the rest of the round is still running).**
Every cell: run-hw exit 0, no recovery, sha256 identical pre-stage/staged/post-run, room 3,
`build_dirty=0` for the ABBA binaries.

| cell | binary | whole-run `tick_rate` | steady | pcm_irqs / drains | silent_irqs | overwrites |
|---|---|---|---|---|---|---|
| S16B1 | base `634d0364412e` | 38.84 | 39.96 | 710 / 42 | 1 | 0 |
| S16N1 | new `4612b69a0887` | 39.14 | 40.01 | 1074 / 37 | 1 | 0 |
| S16N2 | new | 39.13 | 40.01 | 1179 / 41 | 1 | 0 |
| S16B2 | base | 38.69 | 40.15 | 1358 / 53 | 1 | 0 |

- **Bar 1 MET:** new above base in both pairs by >= 0.2 (+0.30 and +0.44; the means are 39.135 vs
  38.765, +0.37). MIDI `late_writes=0` on isr in all four.
- 39.2 was not a bar of this round and is not reached (39.14 best).
- pcm counts differ per cell because the ambient plays are random and drive-walk's clicks differ.
  The per-cell chunk accounting is the lab's check against expected-from-plays, not yet done here.

**RTHB/RTHN (pathfinding before/after on the 486; verified from raw STDOUT by the coordinator):**
- **Bar 1 MET:** all 339 ok / stages / hash values identical, in order, between RTHB and RTHN and
  against DOSBox-X's RT3B.
- **Bar 2, first half, MISSED by 1.8 points:** mean request time 170.3 -> 88.2 ms, -48.2% (bench
  -48.3%, rand -48.2%). The bar was >= 50%.
- **Bar 2, second half, NOT MET:** the worst request (50,145 -> 285,69) went 308.8 -> 211.7 ms,
  -31.4%, equal to DOSBox-X's -31.25%. The bar was "exceeds DOSBox-X's 32%". The premise that 0212's
  divides win more on the 486 is falsified.
- **What stands:** a real **1.93x** speedup of walk requests on hardware (whole-run of the bench
  cell 12.69 -> 18.37; steady 40.53 in both), routes unchanged.

**2026-09-24 -- lab-mmd merged (`cc5b66f5`):** ags 0293 + 0295, script VM levers A+B, MMD script
event 1.159x at fixed 40000; determinism, op-count and screen gates passed. See
[LAB-MMD.md](LAB-MMD.md). My next clean build and gate include them; the pin record will say so.

**2026-09-24 -- ROUND B COMPLETE (raw; the lab cells are scored by their lab workers). All 14 cells
plus the HW-MMD-0 fetch ran, every run-hw exit 0, no recovery used, sha256 identical pre-stage/staged/
post-run in every cell. Target powered OFF (0 mW confirmed).**
- **C1P** (lab-metric 8.1). All four VOID checks pass:
  - `binary_sha12=f429957f47dc`, `build_dirty=0`;
  - `640 x 480 (32-bit)`, alias ON y=60;
  - one manifest each, no SDL trace;
  - `alphafast calls=0` in A1/A2, and 9123 / 9131 with `mid_px=0` in B1/B2.

  | cell | whole-run | steady |
  |---|---|---|
  | C1PA1 | 16.15 | 40.54 |
  | C1PB1 | 16.25 | 40.64 |
  | C1PB2 | 16.26 | 40.62 |
  | C1PA2 | 16.16 | 40.53 |
- **CTR** (lab-metric 8.2). VOID checks pass (A2 label `a0a0a0a0a0a0`, B2 `640060d25f24`,
  `640 x 480 (16-bit)`, alias ON y=60, one manifest, no SDL trace).

  | cell | whole-run | steady |
  |---|---|---|
  | CTRA1 | 20.51 | 41.16 |
  | CTRB1 | 20.44 | 41.22 |
  | CTRB2 | 20.42 | 41.22 |
  | CTRA2 | 20.47 | 41.16 |
- **HW-MMD-1 / HW-MMD-2** (`AGSPROBE.EXE`, `23e131293cef`, `build_dirty=1` by construction):
  - room 50;
  - `mmdprobe cost ... apitime=1` / `apitime=0` (the witness that the env took effect);
  - `insns_total=5685500` in both; `pair_ns` 4272 / 4263;
  - whole-run 19.22 / 21.79, steady 20.42 / 23.30.
- **HW-MMD-0** (round A, fetched at this power-on): complete, as recorded above.
- **Witness:** camera sheets show the expected sequences (AGS Quest logo, rooms, end text; MMD
  character select); card-state unlocked samples 1-9 per cell. Card sheets are saved for the labs'
  own witness review.
- **Deferred as agreed:** RTHS, STWH, DECHO, DECHN (DOSBox-X ranking stands in).

**2026-09-24 -- PRE-REGISTRATION: the SDL 0197 / ags 0213 witness (underflow padding), and hardware
cell S16U1.** Clean main build **`4339326550df`** (`build_dirty=0`): SDL 0196+0197, ags 0210-0213 +
lab-mmd's 0293/0295. Saved as `build/ws/main-4339/ags.exe`.
- **(a) Gate:** the full `gate-alias.sh` on `4339326550df`. Bars as usual: every row A == B except
  the quarantined rows, and every control that has power fails.
- **(b) DOSBox-X witness, by lab-journeys:** its `mi-stall-isr` ratchet unit (5 Days `--startr 3`,
  fixed 40000, `--sb-live`, 19 forced 1.5 s stalls) run on its branch rebased onto main at or after
  this build. Its `pcm_unaccounted` and `mixed`/`inflight` counters are ags 0252, unmerged.
  - **Bar:** `pcm_unaccounted` within +-1 (it was -156 before 0197);
  - `underflow_pads` > 0 (the fix fired);
  - MIDI `late_writes=0`.
  - Control: the same cell on its pre-0197 base, reproducing about -156.
  - Plus the no-stall cells (CA16B/CA8 style) still exact, with `underflow_pads=0` and
    `partial_pulls` recorded.
- **(c) S16U1 (486, next batch):** the S16 fixture exactly (SB2C1's recipe with drive-walk), OPL3,
  PGSB, on `4339326550df`.
  - **Predictions:** `underflow_pads=0` (the 486's stalls, 250-650 ms, are inside the 743 ms ring),
    `overwrites=0`, `late_writes=0`, `silent_irqs` <= 2, whole-run `tick_rate` >= 39.13 (S16N's).
  - **Void if** (a) or (b) has not passed before staging, or the room is not 3.

**2026-09-24 -- (a) RESULT: gate on `4339326550df`: 13/14 A == B; the one fail is
`shards-alias-512x384`, tick 100 only.** The bbox is `(512, 513, 1152, 913)`, 243252 px, as in every
earlier gate. Every other row's control fails as required.
- **Rule applied:** the pre-registration's own wording, "every row A == B except the quarantined
  rows". `shards-alias-512x384` is quarantined (coordinator, 2026-09-24).
- **The Shards "control FAILS as required" does not give the row power.** C-vs-B also differs only
  at tick 100 (229012 px, same bbox), and ticks 300-900 are equal in both comparisons. That is the
  same tick-100 flake: the control still has no power at the frames that could show a 0193 defect,
  as withdrawn above.
- Under that rule (a) passes. The Shards pair gets a look after round C, with the moving-frame freeze
  ticks from the sweep.
- (b) needs lab-journeys' W0 control (~-156) before it counts. W1 met its bar (`pcm_unaccounted
  0, underflow_pads 279, late 0`).
- **(b) W0 control (lab-journeys, 07:31Z, `3e52fca583e4`, pre-0197, clean):** `pcm_unaccounted=-44`
  (98 data IRQs vs 54 mixed chunks), late 0, 19 stalls, no `underflow_pads` field (pre-0213). The
  coordinator accepts it as a control with power, **with a deviation from my "reproducing about
  -156"**, recorded here rather than hidden:
  - the -156 was at cycles=max, and the fixed-40k full run gave -90;
  - 5 Days' ambient clips are random, so W0 mixed only 54 chunks against W1's 441;
  - the defect's signature (silence played that was never mixed) is present.
  (b) still needs the no-stall cells W2/W3 before it counts.
- **(b) PASSED (lab-journeys `359cbcb4`)**, after round C's S16U1 decision, so the drop stands. (b) is
  met for the next batch.
  - Record: lab-journeys `LAB-JOURNEYS.md` section 5 (`lab/journeys` `359cbcb4`). Raw:
    `~/git/dosags-lab-journeys/tests/harness/results/W0197-{W1-stall,W0-stall-pre0197,W2-ca16,W3-ca8}-2026-09-24/`.
  - W2 (16-bit, no stalls, 8000 ticks): mixed 679 = pcm_irqs 679, `underflow_pads 0,
    partial_pulls 0`, late 0.
  - W3 (8-bit, FORCE_8BIT): 997 = 997, `underflow_pads 0, partial_pulls 0`, late 0.
  - **For S16U1's scoring:**
    - the status string's `m16` is the MIXER format, not the device's bit depth;
    - W2/W3 show 29 `silent_irqs` with no forced stalls. They count against "silent IRQs outside
      room loads" only if they fall outside room loads (read from the `silentirq ... since_room=`
      lines).

**2026-09-24 -- ROUND C COMPLETE (raw; lab cells scored by their labs). Target on 06:55:07Z, OFF
07:57:36Z (0 mW confirmed), ~62 min of the 1.5 h cap.** Every cell: run-hw exit 0, no recovery,
sha256 identical pre-stage/staged/post-run, and each staged binary checked against its full recorded
sha256 before the round.
- **START:** g2k `64814fd` AUTOEXEC.BAT sent to `C:\` (staged sha256 `898b4bd6f02b`, the same
  file). `SET` at the PGSB prompt shows `CONFIG=PGSB`, `BLASTER=A220 I7 D3 P330 T3`,
  `SDL_HINT_DOS_AUDIO_SB_FORCE_8BIT=1`, `SDL_HINT_DOS_AUDIO_WB_TX_DELAY=0`,
  `SDL_HINT_DOS_AUDIO_WB_DRR_POLL=0` (`results/RC-START-2026-09-24/SET-shot.jpg`). **The boot config
  is deployed.**
- **C2P** (lab-metric 9.8; `a2485a373bd2`, `build_dirty=0`, `640 x 480 (32-bit)`, one manifest each,
  no SDL trace):
  - arm A (C2PA1/C2PA2) has no `pack24` line, `alphafast calls` 9131 / 9130;
  - arm B (C2PB1/C2PB2) has both `pack24 engaged mode=0x0112 640x480 vram_pitch=1920 src_pitch=2560
    path=lfb` and `pack24 active=1 mode=0x0112 pushed_px=31138950`, `alphafast calls` 9388;
  - `mid_px=0` everywhere.

  | cell | whole-run | steady |
  |---|---|---|
  | C2PA1 | 16.19 | 40.63 |
  | C2PB1 | 16.99 | 40.67 |
  | C2PB2 | 16.94 | 40.67 |
  | C2PA2 | 16.24 | 40.66 |
  - Camera sheet: B's sequence matches A's (logo, parchment title, rooms), with no stripes, skew or
    colour swap visible at sheet scale. The full-size frames are for lab-metric's camera-judged VOID
    rule.
- **HW-MMD-4:** `AGSM1.EXE`, `4a5cca2fa1fd`, `build_dirty=0`, room 50; whole-run 30.41, steady
  33.22 (HW-MMD-0: 26.75 / 29.09).
- **HW-SBP-0 / HW-SBP-1** (`AGSAPI.EXE` `c7767d08684e...`, `f7b0d940965c`, `build_dirty=1`): whole-run
  29.81 / 30.45, steady 32.61 / 33.38; both carry the `apiprobe` line (scored by lab-mmd on the
  script event).
- **Dropped:**
  - S16U1: (b)'s W3 came in after the decision point; (b) has since passed.
  - HW-MMD-5: 0297 has no committed lab PASS and is not on main.
  - WBH5/WBH6: no lab-wb DOSBox-X PASS for pump fix B.

**2026-09-24 -- VOID: the Shards moving-frame sweep (both attempts, `build/ws/shardsctl/`).** The
sweep ran at fixed 40000 without `--fixed-timestep`. Both arms ran all 1000 ticks (presentverify
frames=1012) and wrote no FRZ markers and no captures.
- **Real cause:** patch 0195's freeze check is called only from `dos_run_tick_fixed()`. Without
  the fixed timestep, `GameTick()` runs a bare `UpdateGameOnce(true)`, so the instrument never fires.
- My first explanation (the 25-value `DOSAGS_FREEZE_TICKS` overflowing DOSBox-X's environment) was
  WRONG: a 9-value re-run was also empty. Retracted.
- This also blocked the coordinator's AQ retry design (no fixed timestep at fixed 40000).

**ags 0214 (coordinator GO): the freeze check also runs after `UpdateGameOnce(true)` in the
non-fixed branch**, under `__DJGPP__`, inert when `DOSAGS_FREEZE_TICKS` is unset. Clean build
**`ea3cf035f78f`**.
- `/sdldos:review` passes: real format-patch; next slot in my range; ASCII; no fopen/SIMD;
  port-owned naming; one concern; no double call (the fixed path returns before it).
- **Witness, in order:**
  1. the full gate on `ea3cf035f78f` (every existing row A == B, since they all run with
     `--fixed-timestep` and must be unchanged);
  2. the AQ row x3 with `GATE_FIXED_TIMESTEP=0 GATE_ASSERT_NO_SKIP=1` at fixed 40000
     (`GATE_CONF=tools/dosbox-x.conf`);
  3. the Shards sweep, re-run.
- **0214 witness RESULT** (raw: `tests/harness/results/AQFIX-2026-09-24/`):
  - **(1) Full gate on `ea3cf035f78f`: 13/14 A == B.** The only fail is the quarantined Shards row,
    tick 100 (froze at 101 vs 100); every control with power fails.
  - **(2) AQ row x3 at fixed 40000, no fixed timestep, `GATE_ASSERT_NO_SKIP=1`: 3/3 clean.** 10/10
    pairs equal in each run, `frames_skipped` 0/0 in each, controls fail as required.
  - At cycles=max the same row diverged by one tick intermittently (splash onset 81 vs 82). So that
    divergence reads as host-timing nondeterminism, not a defect in the present path: with the
    emulated time fixed and every tick rendered, it did not appear in 3 runs (n=3, stated as that).
    The row is a candidate to leave quarantine and run shared under this mode; the coordinator
    decides.
  - `ea3cf035f78f` predates lab-metric's landing `aa0c6e17`. The next pinned build carries both.
- **Coordinator decision (2026-09-24): the AQ row switches mode now; its quarantine stays.**
  - `gate-alias.sh` runs `agsquest-alias-y60` by default at fixed 40000 (`tools/dosbox-x.conf`),
    without the fixed timestep, with `GATE_ASSERT_NO_SKIP=1`, and a gate of that row alone takes
    the lock shared. `GATE_AQ_LEGACY=1` restores the old mode.
  - **Rule:** the row leaves quarantine after **10 consecutive clean runs in this mode**, counting
    the 3 AQFIX runs, later gates and the nightly ratchet (lab-journeys mirrors the mode in
    `tests/ratchet.yaml`). Any divergence in this mode resets the count and reopens the question,
    because it would then not be host noise.
  - **Count: 3** (AQFIX r1-r3, 2026-09-24).
- **2026-09-24 -- the first default-mode AQ gate (`build/ws/aqmode1`) is VOID: a display collision,
  mine.** Its arm A photographed **Shards of God**: my Shards sweep (`run-dosbox.sh`, fixed cycles)
  ran at the same time on the same display :211. Both hold the host-wide lock SHARED at fixed
  cycles, so both ran, and `run-dosbox.sh`'s occupied-display refusal is racy when two runs start
  together (lab-journeys hit the same trap).
  - It does not count toward the 10, and it does not reset the count: it was not a divergence of
    the row, the frames were of another game. **Count stays 3.**
  - Fix, applied once the sweep's last chunk ends: an exclusive per-display lock in `run-dosbox.sh`
    (`/tmp/dos-port-display-<N>.lock`, fd 4, held for the run), so runs on one display queue while
    different displays still share.
  - The Shards sweep itself was not contaminated: all 36 of its frames so far are Shards.

**2026-09-24 -- ROUND D (operator approval ~14:25Z, question tool: "Yes, start when ready"; 1.5 h
cap; power-on without a further ask). Staging record.**
- Binaries, sha256-checked against their records before the round (`build/ws/roundD/expected.txt`):
  - `s16u.exe` = `4339326550df` (S16U1);
  - `s32.exe` = lab-metric's landing build `d37c10b9f891` (`a24c3de4...`, LAB-S32 11);
  - `wb.exe` = lab-wb clean3 `35c950e41d59` (`859e3e90...`).
- Order: S16U1, S32S1, WBH5, WBH2' (tag `WBH2P`, since an apostrophe is not tag-safe).
  - WBH5 and WBH2P override the PGSB AUTOEXEC with `WB_TX_DELAY=320 WB_DRR_POLL=1`; RUN.BAT's SETs
    run after AUTOEXEC.
  - WBH5 is VOID unless `midi_tick=rtc`; WBH2P unless `midi_tick=poll`.
- Then S8H and C221 (lab-journeys `ae9125d9`) only if the landed main build with SDL 0220-0222 and
  ags 0250-0253 exists and is hashed when reached; HW-MMD-5 only if 0297 has landed with its arms
  built.
- **Tail, as run** (coordinator 2026-09-24, after power-on): S8H-A0, S8H-O1, HW-MMD-5A, HW-MMD-5B,
  each only if it fits before 17:10Z. **S8H-O2 dropped by coordinator decision**, traded for the
  HW-MMD-5 pair: a deviation from LAB-JOURNEYS 7.1's O1/O2 pair, so the S8 baseline is n=1. C221 is
  dropped for time.
  - Tail binaries sha256-checked: lab-journeys' landed `32cc99df4761` (`6a234d23...`); lab-mmd's
    AGSM3 (`dfb2aea8...`, `0aa50f02be56`) and AGSL297 (`6bd42553...`, `9a3b05ce7e20`).

**2026-09-24 -- ROUND D COMPLETE (raw; lab cells scored by their labs). Target on ~15:43Z, OFF
~17:06Z (power_state `on=false, power_mw=0`), ~83 min of the 1.5 h cap.** Every cell: run-hw exit 0,
no recovery, sha256 identical pre-stage/staged/post-run.
- **S16U1** (`4339326550df`; pre-registration 3342b5c9): whole-run **39.05**, steady 40.00, room 3.
  `pcm_irqs=991 drains=33`, `silent_irqs=0`, `overwrites=0`, **`underflow_pads=0`**,
  `partial_pulls=0`, MIDI isr `late_writes=0`, `plan_behind=0`, clk 126288/126s.
  - Against the predictions: `underflow_pads=0` MET; `overwrites=0`, `late_writes=0`, `silent_irqs`
    <= 2 MET.
  - Whole-run >= 39.13 NOT MET: 39.05. It is still above both base runs (38.84 / 38.69), but below
    S16N1/N2 (39.14 / 39.13) at n=1, and below the 39.2 floor.
  - The pump's per-tick `SDL_Delay(10)` on silent iterations (lab-metric's finding) is in this build.
- **S32S1** (lab-metric; `d37c10b9f891`): `pcm_irqs=0`, `midi=none`, `midi_tick=poll`, `events=0`,
  `skipped_silent=1557`. By lab-metric's own VOID rule ("pcm=sb and midi=opl3") it is **VOID**: no
  sound played, although the SB opened. Whole-run 16.04, steady 40.11. Cause for lab-metric to find
  (the ON cfg on AGS Quest?).
- **WBH5** (clean3 `35c950e41d59`, TX_DELAY=320/DRR_POLL=1 overrides):
  - `midi_tick=rtc` (not VOID);
  - `late_writes=259`, `late_max_ms=92`, `plan_behind=0`, clk 128547/128s, **`rearm=0/0/0/37`**;
  - whole-run 25.37.
- **WBH2P** (the poll control): `midi_tick=poll`, `late_max_ms=475`, late50 3067/4467. Captures for
  lab-wb's garble check: `results/WBH5-2026-09-24/WBH5-seg01.ogg`,
  `results/WBH2P-2026-09-24/WBH2P-seg01.ogg`.
- **S8H-A0** (`32cc99df4761`, room 35, sound off): whole-run 39.10, steady 40.21.
- **S8H-O1** (room 35, OPL3):
  - whole-run 38.04, steady 40.24;
  - `late_writes=504`, `late_max_ms=46`, **`isr_burst=256`**, as the 256-cap baseline predicted;
  - pcm_irqs 2179 vs mixed 2198, inflight 19;
  - `overwrites=0`, `underflow_pads=0`.
  - n=1 (O2 traded).
- **HW-MMD-5A** (AGSM3 `0aa50f02be56`): room 50, whole-run 30.16, steady 33.02.
- **Dropped:**
  - HW-MMD-5B: it would have passed the cap at 17:05:21, so there is no 0297 A/B pair this round.
    5A alone stands beside HW-MMD-4 (30.41 / 33.22).
  - C221: time.

**2026-09-24 -- ROUND E (operator ~18:20Z, question tool: "Yes, start now with fill runs"; 1.5 h
cap; power-on without a further ask). Staging record.**
- Binaries sha256-checked against their records (`build/ws/roundE/expected.txt`):
  - AGSM3 `dfb2aea8...`, AGSL297 `6bd42553...` (LAB-MMD 18.4);
  - clean4 `cf19f33f...` (LAB-WB 13);
  - STALLH probe60 `a82fcb9b...` = `07c3ba0357e1` (LAB-JOURNEYS 9b.3);
  - lab-journeys' landed `32cc99df4761` (`6a234d23...`) for S8H-O2.
- Order:
  1. 0297 ABBA `M297A1/B1/B2/A2`;
  2. WB pair `WBH2PP` (= WBH2'') then `WBH6`, both with TX_DELAY=320/DRR_POLL=1 overrides; VOID
     unless `midi_tick` poll / rtc;
  3. fill, each only if it fits: `STALLHA0P` (= STALLH-A0P; S8H-A0 protocol, sound off), then
     `S8HO2` (= S8H-O2).
- Tags are chosen so the engine's 8-character manifest names stay distinct.
- D2 and the 0305 ABBA go to round F (coordinator).

**2026-09-24 -- ROUND E RESULT (raw; lab cells scored by their labs). Target on 18:22Z, OFF 19:58Z
(power_state `on=false, power_mw=0`): ~6 min PAST the 19:52 cap.** The cap overrun: the driver's
launch guard checked the cap before WBH6 and placed the WB pair inside it, but WBH6 did not end; it
spent its whole 2516 s collection budget. Every other cell: run-hw exit 0, no recovery, sha256
identical pre/staged/post.
- **0297 ABBA** (M297A1 was the power-on cell, i.e. cold):

  | cell | binary | whole-run | steady |
  |---|---|---|---|
  | M297A1 | AGSM3 `0aa50f02be56` | 29.80 | 32.64 |
  | M297B1 | AGSL297 `9a3b05ce7e20` | 30.31 | 33.28 |
  | M297B2 | AGSL297 | 30.34 | 33.28 |
  | M297A2 | AGSM3 | 30.16 | 33.07 |
- **WBH2PP (= WBH2'', clean4 `3e220e53230a`):** `midi_tick=poll` (valid), `late_max_ms=449`, late50
  3084/4590, clk 129744/130s, `pcm_irqs=1777`, `overwrites=0`; whole-run 25.29.
- **WBH6 (clean4, RTC pump + reworked 0233): run-hw exit 1, NO manifest collected.**
  - drive-start clicked START (19:18:34Z) and the camera shows intro, title and room 3. Music was
    in the capture from 12:16:29 to 12:26:26 local (448 LEVEL samples above -60 dB).
  - The screen went BLACK at ~12:29 local, about when the 16000-tick exit was due (~25 ticks/s from
    ~12:17), and never returned to the DOS prompt. run-hw's collect loop read "other", not a prompt,
    so it did not recover (correctly), and refused after 2516 s.
  - Reading: a wedge at or after the game's exit (the pump's uninstall on quit is one candidate),
    not during play. lab-wb's to diagnose.
  - Its RUNMANI/STDOUT/SDL log may be on `C:\DOSAGS`; fetch only at the next power-on and only with
    the operator's approval (coordinator).
  - Captures: `results/WBH6-2026-09-24/WBH6-seg01.ogg`, plus WBH2PP's.
- **Fill dropped:** STALLH-A0P and S8H-O2 did not run; the driver stopped after WBH6's failure.
- M297A1 is a cold cell (warm-up rule from round F).

**2026-09-24 -- ROUND F RESULT (D2 variant; raw; lab cells scored by their labs). Target on 21:44:29Z,
OFF 23:03Z (power_state `on=false, power_mw=0`), inside the 23:14:29Z cap.** Every cell: run-hw exit
0, no recovery, sha256 identical pre/staged/post.
- **START fetch (before any send):** WBH6's manifest `WBH6.LOG` (complete, exit_code 0),
  `AUDIOPRB.LOG`, `AGSSAVE.001`; `STDOUT.TXT` 0 bytes. See `results/WBH6-2026-09-24/fetch/`.
  lab-wb's reading: the wedge is after quit(), so WBH6L is NO-GO (recorded as not run).
- **WARMUP** (AGSL297, unscored): 30.45 / 33.28.
- **D2** (F = `b983bf9d146a` with SDL 0213; N = `0a40583867d7` without it; S16 fixture):

  | cell | whole-run | steady |
  |---|---|---|
  | D2N1 | 39.01 | 39.88 |
  | D2F1 | 39.14 | 39.98 |
  | D2F2 | 39.13 | 39.95 |
  | D2N2 | 38.99 | 39.87 |
  - All four: `overwrites=0`, `underflow_pads=0`, MIDI isr `late_writes=0`.
  - **lab-metric's score (fd267c43): FALSIFIED as registered** (the F cells' skips 63/68 exceed 59).
  - The fix does what it should: pump 8.1 -> 0.4 ms, +0.135 whole-run.
  - The S16 floor 39.2 is still not reached.
- **S32F1** (F, 32-bit, sound on, no 1500 exit):
  - whole-run 13.63, steady 41.09;
  - `pcm_irqs=181` (sound played this time), MIDI `events=40`, `late_writes=0`, `overwrites=0`.
  - lab-metric scores it.
- **STALLH-A0P** (probe60): whole-run 38.85, steady 40.22, room 35. lab-journeys reads its stall lines.
- **S8H-O2** (`32cc99df4761`, room 35, OPL3):
  - whole-run 38.24, steady 40.24;
  - ~~`late_writes=50`~~ **`late_writes=507`, `late_max_ms=46`** (CORRECTED 2026-09-24: my summary line
    was cut at 360 characters and truncated 507 to 50; the same as O1's 504, so no improvement, as
    lab-journeys scored in 83bb8ceb). `pcm_irqs=2185` vs mixed 2204 with 19 inflight;
  - `overwrites=0`, `underflow_pads=0`.
- **Not run:** CAP3 (held for 0226 v2; the round-G candidate is now cap3v2) and WBH6L (no-go).

**2026-09-24 -- ROUND G (operator approval ~23:03Z, their own message). Staging record.**
- **Binaries** (`build/ws/roundG/expected.txt`, all sha256-checked):
  - cap3v2 `18d292f5...` (`e8c3c2a8dcd5`, lab binary; 0226 v2 APPROVED);
  - AGSL297 `6bd42553...` (stamp `9a3b05ce7e20`) and AGSL305 `f159e932...` (stamp `75ae0819b212`),
    per LAB-MMD 25.3 @ 0e1b497a;
  - clean4 `cf19f33f...`, xm `f55ca804...` (`2abba7a4d9f4`), clean6 `39c7c2ec...` (`8c54bd669100`),
    per LAB-WB 20.3 @ 6871176d.
- **Order, cut from the bottom by the cap** (cap-aware timeouts; anything cut -> round H):
  1. WARMUP (AGSL297, unscored);
  2. `CAPH1`, `CAPH1I`, `CAPHC`, `CAPHI` on cap3v2 (S8H-O1 protocol; LAB-JOURNEYS 8.9-8.11, judged
     under amendments 3 and 4);
  3. the 0305 ABBA `P305A1/B1/B2/A2`, run only as a whole block;
  4. `WBH6R`, then `WBH6X` if the exit wedge reproduces, else `WBH6W` (LAB-WB 20 / 20.2).
- **Wedge handling (WB block only):** a wedged WB cell does not stop the round. The driver uses that
  run's one recovery (a mains cycle) and does a read-only get-file of the manifest, STDOUT.TXT, and
  for WBH6X the marker files, into `results/<TAG>-2026-09-24/fetch/`.
- Expected by arithmetic: items 1-3 are ~76 min, so the WB block will most likely go to round H.

**2026-09-24/25 -- ROUND G RESULT (raw, every figure grepped from the raw manifests; lab cells scored
by their labs). Target on 23:06:12Z (relay), OFF ~00:30Z (power_state `on=false, power_mw=0` at
00:30:50Z), inside the 00:36:12Z cap.** Every cell: run-hw exit 0, no recovery, sha256 identical
pre/staged/post.
- **WARMUP** (AGSL297, unscored): 30.45 / 33.28.
- **CAPH** (cap3v2 `e8c3c2a8dcd5`, room 35, OPL3; judged by lab-journeys under amendments 3 and 4):

  | cell | env | late_writes | isr_burst | cap_hits | plan_behind | clk | pcm_irqs | whole-run / steady |
  |---|---|---|---|---|---|---|---|---|
  | CAPH1 | defaults | 6 (max 46) | 384 | 1 | 0 | 124872/130s | 2191 | 38.11 / 40.19 |
  | CAPH1I | DRAIN_STI=0 | 6 (max 46) | 384 | 1 | 1 | 122925/129s | 2167 | 38.44 / 40.28 |
  | CAPHC | DEDUPE=0, cap 256 | 480 (max 46) | 256 | 3 | 0 | 122799/129s | 2172 | 38.54 / 40.26 |
  | CAPHI | STI=0, DEDUPE=0, cap 8192 | 0 | 416 | 0 | 0 | 122792/129s | 2185 | 38.51 / 40.26 |

  - All four: `overwrites=0`, `underflow_pads=0`, `silent_irqs` 3-4.
  - The control CAPHC reproduces O1's lateness (480 at budget 256), so it has power.
- **0305 ABBA** (manifest stamps match the literal arms: A `9a3b05ce7e20`, B `75ae0819b212`):

  | cell | arm | whole-run | steady |
  |---|---|---|---|
  | P305A1 | A | 30.43 | 33.29 |
  | P305B1 | B | 30.24 | 33.16 |
  | P305B2 | B | 30.31 | 33.15 |
  | P305A2 | A | 30.35 | 33.28 |

  Scored by lab-mmd with `abba.py` (027dff00) on the script event.
- **WB block: NOT RUN.** The operator asked (~00:19Z) to stop after the 0305 ABBA, with no WB cells.
  My attempt to stop the driver was refused by the tool's permission classifier. The driver itself
  dropped WBH6R at 00:27:36Z (352 s left < 1200 s), so no WB cell ran. WBH6r/x/w carry to round H.
  I powered off ~2.5 min after the driver ended, not at once.
- **The operator's standing stop:** no power-on until the operator says go.

**Operator MMD decisions (relayed; lab-mmd records them in LAB-MMD):** the target is now FULL SPEED
with fps secondary, and G gets one time-boxed register-friendly variant.

**2026-09-25 -- ROUND H (operator approval ~02:20Z, via the coordinator's question tool: "Yes, as
proposed"). Staging record, before power-on.** Driver `build/ws/roundH/driveH.sh`, cell wrapper `cellH.sh`.
- **Binaries** (`build/ws/roundH/expected.txt`, all sha256-checked against the orders; read-only copies):
  - `l308.exe` = AGSL308 `425c1609...` (stamp `bc9c3704a839`); `pre308.exe` = AGSPRE308 `c23527e6...`
    (`f05b69e9454b`); `prof4.exe` = AGSPROF4 `5d045678...` (lab-mmd `build/lab/`, LAB-MMD 29);
  - `cap3c.exe` `f242d324...` (`78683aa4c501`; LAB-JOURNEYS 8.24 addendum).
  - The stamps are not greppable from any exe (checked on my own DEC35 builds too), so each cell's manifest
    `binary_sha12` is checked after the run; the file sha256 is checked before staging and after sending.
- **Cap:** 90 min from relay-on, recorded by the driver at `power on`; every `--timeout` ends by cap - 240 s;
  a watchdog powers off at cap - 45 s. Cut from the bottom; cuts go to round I.
- **Order:** 1. `WARMUPH` (l308, MMD cell, unscored). 2. `INT33H` (prof4, MMD cell with
  `DOSAGS_TAS_AUTO_EXIT_TICK=100`, `DOSAGS_INT33BENCH=1`; `lab-mmd/int33.py`). 3. CAP3c on cap3c, room 35,
  `DOSAGS_TAS_AUTO_EXIT_TICK=5000`, direct framebuffer, drive-walk: `C3512` (ON-512x384 cfg,
  `SDL_HINT_DOS_MIDI_DEFER_DRAIN_STI=0`), then the 640x480 ABA with `ACSETUP-ON-640X480.CFG` (lab/journeys
  40906b5d, sha256 `24d874f2...`): `C364066A` (`SDL_HINT_DOS_OPL_DELAY_READS=6`), `C364044` (default),
  `C364066B` (`DELAY_READS=6`); judged by `cap3c-score.py` at 0189a4f7 (8.23 + amendments 1 and 2).
  4. H' ABBA `HPA1` (pre308) `HPB1` `HPB2` (l308) `HPA2` (pre308), MMD cell, only as a whole block
  (>= 2080 s left); `abba.py A1 B1 B2 A2 -0.30 -0.20`.
- **MMD cell (LAB-MMD 29):** mmd, `ACSETUP-OFF-512X384-ROUND.CFG`, run-hw's default fixed timestep, sound
  off, no input, `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=1000`.
- **Input (lab-journeys' hardware click rule, ca8e6d98):** drive-walk waits 60 s after run-hw takes the
  lock (boot ended <= ~40 s after the lock in rounds D-G), then clicks every 2 s; judged in-window only via
  `drive-align.py`. The 486 click check for SDL 0227 rides on the C3 cells: in-window host clicks vs
  `mouse_presses_hw`, and `lost_clicks` = 0.
- **Audio:** captured in every cell, kept LOCAL (gitignored, deb93b8b); result files carry each capture's
  sha256 and the numbers derived from it.
- **Arithmetic:** ~5085 s usable after boot and margin; items 1-3 are ~3200 s, so the H' ABBA (needs 2080 s)
  will most likely be cut to round I.
- **Not in this round** (not in the coordinator's order): LAB-MMD 29's P2 and `-mtune=i486` pairs, the
  CTMOUSE.EXE fetch LAB-MMD 29 recommends, and round G's WBH6r/x/w.

**2026-09-25 -- ROUND H RESULT (raw; every figure grepped from the raw manifests and scorer output).**
Relay-on 02:49:59Z, cap 04:19:59Z; driver `build/ws/roundH/driveH.sh`; power OFF 03:45:09Z, confirmed
`on=False power_mw=0`. Every cell run-hw exit 0, recover 0, file sha256 pre = post = staged.
- `WARMUPH` (l308): `binary_sha12=bc9c3704a839 build_dirty=0`. Unscored.
- `INT33H` (prof4): `binary_sha12=a5d4c1dea5fb build_dirty=1` (lab build, as LAB-MMD 29 states).
  `DOS-PORT int33bench n=200 present=1 ucps=1193180 uclock_self=1038 int21_30=26263 int33_3=19871
  int33_5=20082`. int33.py (73f32fd7): fn3 83.3 us, fn5 84.2 us, INT21h/30h 110.1 us per call; 0.75 ms
  a tick. **The ~0.2 ms/call prediction is FALSIFIED** (both < 0.1 ms).
- CAP3c on cap3c (`binary_sha12=78683aa4c501 build_dirty=0`, room 35 in all four): `C3512`, `C364066A`,
  `C364044`, `C364066B`. `cap3c-score.py` + `audio-compare.py` at 0189a4f7 (`C3512-2026-09-25/CAP3C-SCORE.txt`):
  choice `pgdetect=1 opl_reads=4 budget=448` PASS; **cost_window FAIL, 25.5 us per write (20.1-22.3)**;
  mechanism PASS (101 arrivals per 2.57 ms window); bound PASS (isr_burst 390 x 25467 ns = 9.93 ms);
  late_writes 0; underruns 0; overwrites 0; SB alive clock 0.963, pcm 2188; silent 3 at tick 1006;
  isr_max_us 52788 reported only. Audio: 44 vs 66a chroma 0.9596, 44 vs 66b 0.8238, **66b vs 66a 0.8246
  < 0.905: audio VOID on hardware** (amendment 2); loud windows 106/106/107. **VERDICT CAP3c FAIL; audio
  VOID.** The coordinator notes (LAB-JOURNEYS 8.28) that ~3.9 us of the 25.5 may be PIT-read inflation.
  C3512's stall100 at t_ms=80188 is 1536 ms, the 9b.2 end-of-dialogue stall.
- **Clicks (SDL 0227 on the 486):** `lost_clicks=0` in all four C3 cells (seen = hw: 32/32, 31/31, 31/31,
  30/30); no phantom. drive-align, in-window host clicks vs `mouse_presses_hw`: C364066A 31/31, C364044
  31/31, C364066B 30/30, no gaps; engine start at lock + 5.4 / 5.9 / 4.6 s. **C3512:** its
  `DRIVE-ALIGN.txt` offset (+82 s) is a period ALIAS of the regular walker cadence (LAB-JOURNEYS 8.29,
  9443e65f: +4.5 s by interval matching), so that file's classes are wrong; lab-journeys counts 43-45
  in-window host clicks against 32 driver presses, all missing ones at engine t >= 125 s. In the 640 cells
  run-hw released the input lock ~40 s before quit (engine ~143 s), so they cover the tail only to ~143 s.
  Daemon side: from C364044 on, a passive poller kept every vcctrl command
  (`C364044-2026-09-25/DAEMON-EVENTS-roundH.jsonl`); C364044's 31 clicks were 31 `mouse_down` + 31
  `mouse_up`, all ok. C3512's own window is not recoverable (ring ~20 s; no journal entries).
- **Not run:** the H' ABBA, dropped as a block at 03:45:03Z (1856 s left < 2080 s) -> round I.
- **Audio:** every capture kept local (gitignored); each dir's `AUDIO-SHA256.txt` records it.

**2026-09-25 -- ROUND I (operator approval ~04:35Z, via the coordinator's question tool: "Yes, MMD block").
Staging record, before power-on.** Driver `build/ws/roundI/driveI.sh` (round H's cap logic, watchdog at cap - 45 s,
power-off at the end); cell wrapper `cellH.sh` (no drive: MMD cells take no input). LAB-MMD 34.5/34.6 at
lab/mmd 32930a1.
- **Binaries** (`build/ws/roundI/expected.txt`, full sha256 checked against the orders): `l308.exe` AGSL308
  `425c1609...` (stamp `bc9c3704a839`); `pre308.exe` AGSPRE308 `c23527e6...` (`f05b69e9454b`); `prof5.exe` AGSPROF5
  `77f27a4a...`; `p2a.exe` AGSP2A `0b3cf9ff...` (`c04f697cb7c9`); `p2bd.exe` AGSP2BD `23247bc1...` (`e77f078d5bed`;
  NOT the old AGSP2B 058e660e).
- **MMD cell (LAB-MMD 29):** mmd, `ACSETUP-OFF-512X384-ROUND.CFG`, sound off, no input,
  `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=1000`.
- **Order, cut from the bottom:** 1. `WARMUPI` (l308, unscored). 2. `PROF5BE` (prof5, MMD cell at auto-exit 100,
  `DOSAGS_INT33BENCH=2`). 3. `PROF5PO` (the same + `SDL_HINT_DOS_MOUSE_POLL=1`). 4. H' ABBA `HIA1` (pre308)
  `HIB1` `HIB2` (l308) `HIA2` (pre308), whole block only (>= 2080 s left). 5. P2b ABBA `P2BA1` (p2a) `P2BB1`
  `P2BB2` (p2bd) `P2BA2` (p2a), whole block only, cut before H'. Readings: 27 / 33.1 (int33.py), 29 (abba.py),
  28.12 (abba.py --metric inputs; band [-1.09, -0.82] ms/tick).
- **Forced exit / mouse vector:** the `mousechk` check is a lab gate on the probe builds (28.11, CLEAN); arm B
  has no probe, so on the target the check is that every P2b cell exits and is collected cleanly (a wedge shows
  as a failed collection: one recovery, then the round stops).
- **Tags:** new; round H's HPA1-HPA2 were staged but never run and are not reused.
- **Arithmetic:** boot 75 + warm-up ~480 + PROF5 x2 ~920 + H' ~2080 = ~3555 s of ~5160 usable, so the P2b block
  (~2080) will most likely be cut to round J.
- **Audio:** captured by the cell wrapper, kept local (gitignored); `AUDIO-SHA256.txt` per dir.
- **2026-09-25 ~04:56Z -- REORDER (coordinator request, before any ABBA cell ran):** the P2b ABBA now runs BEFORE
  the H' ABBA (P2b is the open decision; H' is landed and only confirmed). Done without touching a running cell:
  driveI.sh's main process was stopped (SIGTERM) while PROF5BE ran; PROF5BE's own cell and the cap watchdog kept
  running; `build/ws/roundI/driveI2.sh` waits for PROF5BE to finish, then runs PROF5PO, the P2b block, the H'
  block, with the cap still from the ORIGINAL relay-on (04:44:54Z, cap 06:14:54Z). No power action.

**2026-09-25 -- ROUND I RESULT (raw; figures grepped from the raw manifests and the scorers' output).** Relay-on
04:44:54Z, cap 06:14:54Z; reordered at ~04:56Z (P2b before H', coordinator request); power OFF 05:40:53Z, confirmed
`on=False power_mw=0`. Every cell run-hw exit 0, recover 0, file sha256 pre = post = staged.
- `WARMUPI` (l308): `binary_sha12=bc9c3704a839 build_dirty=0`. Unscored.
- `PROF5BE` / `PROF5PO` (prof5, `binary_sha12=cb3c2a304d39 build_dirty=1`), int33.py at cf629335
  (`PROF5BE-2026-09-25/INT33-SCORE.txt`): warm fn3 82.6 / fn5 81.6 (BE), 82.6 / 81.1 (PO), INT21h 104.3 / 105.1 us;
  cold fn3 166.3 / fn5 166.8 (BE), 166.9 / 166.9 (PO), ratios 2.01-2.06x: **"486 reading: SUPPORTS"** in both;
  pump warm -> cold: BE 36.7 -> 127.1 us (3.46x), PO 523.9 -> 588.5 us (1.12x).
- **P2b ABBA** `P2BA1` `P2BB1` `P2BB2` `P2BA2` (A p2a `c04f697cb7c9`, B p2bd `e77f078d5bed`, both `build_dirty=1`),
  abba.py at f12799e (`P2BA1-2026-09-25/ABBA-SCORE.txt`): **inputs A 2.249 / 2.249, B 0.698 / 0.699 ms/tick,
  N 0.001, D -1.550: PRIMARY GAIN.** The registered 28.12 band [-1.09, -0.82] is MISSED on the high side (the
  saving is ~0.5 ms/tick larger than the model). Secondary `--metric ugo`: A 30.809 / 30.808, B 29.109 / 29.365,
  N 0.256, D -1.571: GAIN. Every P2b cell exited and was collected cleanly (no wedge, no recovery).
- **Not run:** the H' ABBA, dropped as a block at 05:40:47Z (1807 s left < 2080 s) -> round J.
- **Audio:** local only; `AUDIO-SHA256.txt` per dir.

**2026-09-25 -- ROUND J (operator approval ~06:35Z, via the coordinator's question tool; to run only AFTER
the coordinator confirms the vcctrld redeploy). Staging record, before power-on.** Driver
`build/ws/roundJ/driveJ.sh` (round I's cap logic and watchdog), cell wrapper `cellJ.sh` (cellH + the new
`vcctrl input-log` window saved as `INPUT-LOG.jsonl` in each cell, once the command is live).
- **Binaries** (`build/ws/roundJ/expected.txt`, full sha256 checked): `l308.exe` AGSL308 `425c1609...`
  (`bc9c3704a839`); `pad.exe` AGSPAD `04432308...` (`67116a7312ac`, `build_dirty=1`); `pre308.exe` AGSPRE308
  `c23527e6...` (`f05b69e9454b`); `c3pn.exe` N `1f664bc3...` (`476abb1c5a32`, no `overskip` string);
  `c3pf.exe` F `8ce2aa9c...` (`dc883a267eb8`, has it); `wb4.exe` clean4 `cf19f33f...` (`3e220e53230a`);
  `wbxm.exe` xm `f55ca804...` (`2abba7a4d9f4`); `wb6.exe` clean6 `39c7c2ec...` (`8c54bd669100`).
- **Order, cut from the bottom:** 1. `WARMUPJ` (l308, MMD cell, unscored). 2. layout-control ABBA `LCJA1`
  (l308) `LCJB1` `LCJB2` (pad) `LCJA2` (l308), MMD cell, whole block (>= 2080 s); abba.py script metric +
  `--metric ugo`, read per LAB-MMD 31.2. 3. C3P ABBA `C3PN1` `C3PF1` `C3PF2` `C3PN2`, LAB-S32 20.2's fixture
  (agsquest, direct framebuffer, `DOSAGS_FORCE_COLOR_DEPTH=32`, `DOSAGS_TAS_AUTO_EXIT_TICK=1500`,
  `SDL_DOS_PACK24=1`, `games/trilbysnotes/ACSETUP-OFF.CFG` as ACSETUP.CFG, sound off), whole block (>= 2040 s);
  `lab-c3p.py --n-sha 476abb1c5a32 --f-sha dc883a267eb8 --witness-clean <tags>` after the camera sheets are
  reviewed. Optional sound-on pair dropped. 4. WB block (LAB-WB 27): `WBH6R` (clean4), then `WBH6X` (xm) if it
  wedges at exit, else `WBH6W` (clean6); 5 Days drive-start, `games/5days/ACSETUP-ON.CFG`,
  `DOSAGS_TAS_AUTO_EXIT_TICK=16000 SDL_HINT_DOS_AUDIO_BACKEND=wb SDL_HINT_DOS_AUDIO_WB_TX_DELAY=320
  SDL_HINT_DOS_AUDIO_WB_DRR_POLL=1`, --timeout <= 1200; each cell needs >= 1200 s; a wedge uses that cell's one
  mains cycle (covered by the operator's approval), then a read-only fetch into `<TAG>-2026-09-25/fetch/`;
  never stops the round. 5. H' ABBA `HJA1` (pre308) `HJB1` `HJB2` (l308) `HJA2` (pre308), >= 2080 s.
- **Arithmetic** (round G-I cell times: MMD ~480-500 s, C3P ~490 s, WB 440-1100 s): boot 75 + warm-up 480 +
  layout ~2000 + C3P ~1960 = ~4515 of ~5160 usable; the WB block and the H' ABBA will most likely go to round K.
- **Not in J** (coordinator): TAIL, P3, SCRIPTH, the DEC35 486 pair.
- **2026-09-25 -- REORDER (coordinator, before any round J cell; only two of the three blocks fit):** WARMUPJ,
  then the C3P ABBA (the operator's 32-bpp fps goal), then the WB block (the operator chose to keep pursuing the
  pump; cut three rounds running), then the layout-control ABBA, then H'. Layout and H' are the likely cuts, to
  round K (P3's round K arms are same-binary, so they do not need the layout noise first). driveJ.sh updated.

**2026-09-25 -- ROUND J RESULT (raw; SUMMARY lines copied verbatim).** Relay-on 06:47:03Z, cap 08:17:03Z; power
OFF 08:05:09Z, confirmed `on=False power_mw=0` at 08:05:36Z.
```
WARMUPJ: run-hw exit=0 pre=425c1609f50a post=425c1609f50a staged_has_pre=1 binary_sha12=bc9c3704a839 build_dirty=0 tick_rate=30.16 tick_rate_steady=33.11  recover=0 rooms=Now in room 50, 06:56:22
C3PN1: run-hw exit=0 pre=1f664bc3b927 post=1f664bc3b927 staged_has_pre=1 binary_sha12=476abb1c5a32 build_dirty=0 tick_rate=16.82 tick_rate_steady=40.65  recover=0 rooms=Now in room 1,Now in room 2,Now in room 3, 07:04:52
C3PF1: run-hw exit=0 pre=8ce2aa9cf9d8 post=8ce2aa9cf9d8 staged_has_pre=1 binary_sha12=dc883a267eb8 build_dirty=0 tick_rate=16.87 tick_rate_steady=40.67  recover=0 rooms=Now in room 1,Now in room 2,Now in room 3, 07:13:03
C3PF2: run-hw exit=0 pre=8ce2aa9cf9d8 post=8ce2aa9cf9d8 staged_has_pre=1 binary_sha12=dc883a267eb8 build_dirty=0 tick_rate=16.88 tick_rate_steady=40.67  recover=0 rooms=Now in room 1,Now in room 2,Now in room 3, 07:21:14
C3PN2: run-hw exit=0 pre=1f664bc3b927 post=1f664bc3b927 staged_has_pre=1 binary_sha12=476abb1c5a32 build_dirty=0 tick_rate=16.85 tick_rate_steady=40.64  recover=0 rooms=Now in room 1,Now in room 2,Now in room 3, 07:29:28
WBH6R: run-hw exit=0 pre=cf19f33f13a5 post=cf19f33f13a5 staged_has_pre=1 binary_sha12=3e220e53230a build_dirty=0 tick_rate=25.28 tick_rate_steady=25.84  recover=0 rooms=Now in room 1,Now in room 2,Now in room 3,Now in room 99, 07:46:49
WBH6W: run-hw exit=0 pre=39c7c2ec0171 post=39c7c2ec0171 staged_has_pre=1 binary_sha12=8c54bd669100 build_dirty=0 tick_rate=25.79 tick_rate_steady=26.36  recover=0 rooms=Now in room 1,Now in room 2,Now in room 3,Now in room 99, 08:05:04
```
- **C3P ABBA** (lab-c3p.py at lab/metric 7f6b106, `C3PN1-2026-09-25/C3P-SCORE.txt`; the four camera sheets
  reviewed clean first): N 37.26 / 37.25 stable (skips 125 / 125), F 38.93 / 38.93 (skips 64 / 64, `overskip
  mode=1 skipped=284`); net +1.67, N-N spread 0.01. **VERDICT C3P: NOT FALSIFIED, predictions partly missed**
  (F skips 64 vs 20-55, stable 38.93 vs 39.2-40.2). Coordinator: ags 0233 goes to landing review.
- **WB block:** WBH6R (clean4) **exited clean** -- the exit wedge did not reproduce -- so WBH6W (clean6) ran,
  also clean; no recovery used. Scoring (gate A per cell, B/D on WBH6R) is lab-wb's (LAB-WB 27).
- **Not run:** the layout-control and H' ABBAs, dropped as blocks at 08:05:04Z (479 s left) -> round K.
- **Input log (vcctrld 662e94d):** each cell's window was saved AFTER the round: the cell wrapper's existence
  probe (`input-log --help`) exits 3, so the in-cell capture never ran; recovered from the persistent log
  per cell (`INPUT-LOG.json`, START.UTC to the cell's SUMMARY end; none truncated). The probe now queries.
- **Audio:** local only; `AUDIO-SHA256.txt` per dir.

**2026-09-25 -- ROUND K (MMD only; LAB-MMD 38 at lab/mmd 97c7425). Staging record, before any power-on; NOT
approved yet -- the driver is not started until the operator's approval comes through the coordinator.**
Driver `build/ws/roundK/driveK.sh` (round J's cap logic, watchdog at cap - 45 s, power-off at the end), cell
wrapper `cellK.sh`.
- **Binaries** (`build/ws/roundK/expected.txt`, full sha256 checked against 38, each byte-identical to lab-mmd's
  own `build/ags-k-*/ags.exe`): `l308.exe` AGSL308 `425c1609...` (warm-up); `kmain.exe` AGSKMAIN `f5e1e92d...`
  (main 98fa396); `kj.exe` AGSKJ `0d602bfd...` (+ ags 0312); `kp3.exe` AGSKP3 `d6bbee8d...` (+ SDL 0241 + ags
  0311); `kstk.exe` AGSKSTK `c8930724...` (+ 0241 + 0311 + 0312; the stack arm, the P3 classifier read CLEAN,
  36.6). Strings: 0240 in all four, 0241's hint only in kp3/kstk. AGSKMW/AGSKSW are lab-only, not staged.
- **MMD cell** (as rounds I/J): mmd, `ACSETUP-OFF-512X384-ROUND.CFG`, sound off, no input, direct framebuffer,
  `DOSAGS_TAS_AUTO_EXIT_TICK=1000`.
- **Order, cut from the bottom; each ABBA only as a whole block (>= 2080 s):** 1. `WARMUPK` (l308). 2.
  main-vs-stack `KSA1` `KSB1` `KSB2` `KSA2` (kmain / kstk). 3. P3 `KPA1` `KPB1` `KPB2` `KPA2` (kp3; A =
  `SDL_HINT_DOS_INPUT_PENDING_ALWAYS=1`, B = default). 4. J `KJA1` `KJB1` `KJB2` `KJA2` (kmain / kj) -- the
  cut-line. Readings per 38 (abba.py; logic metric for main-vs-stack, inputs/update_game_once for P3, script for J).
- **Input log (round L rule, applied from round K):** every cell saves `INPUT-LOG.json` (the raw window) and
  `INPUT-LOG.jsonl` (run-hw-<TAG>'s lock.acquired .. lock.released); a fetch failure or a missing pair writes
  `INPUT-LOG-VOID.txt` and the cell is VOID. The extraction was tested on round J's C3PN1 log (6 events, seq
  7894..9566) and on an empty log (VOID).
- **Arithmetic** (round I's MMD cells 472-484 s; an ABBA ~1935 s): boot + warm-up ~547 s, main-vs-stack to
  ~2480 s, P3 to ~4415 s; J needs 2080 s with ~745 left, so it is expected to be cut to round L. Power-off
  expected ~74 min after relay-on.

**2026-09-25 -- ROUND K RESULT (raw; SUMMARY lines copied verbatim).** Relay-on 13:42:15Z, cap 15:12:15Z; power
OFF 14:58:21Z, confirmed `on=False power_mw=0` at 14:58:37Z. The J ABBA was dropped as a block (600 s left) ->
round L. Every cell: run-hw exit 0, recover 0, sha256 pre = post = staged, the 38.1 stamp OK, and
`INPUT-LOG.jsonl` from run-hw-<TAG>'s lock pair (6 events each).
```
WARMUPK: run-hw exit=0 pre=425c1609f50a post=425c1609f50a staged_has_pre=1 binary_sha12=bc9c3704a839 build_dirty=0 tick_rate=30.31 tick_rate_steady=33.10  recover=0 inputlog=ok:6 rooms=Now in room 50, 13:52:27
WARMUPK: stamp OK bc9c3704a839
KSA1: run-hw exit=0 pre=f5e1e92dd3a8 post=f5e1e92dd3a8 staged_has_pre=1 binary_sha12=8d5df1ebe705 build_dirty=0 tick_rate=32.72 tick_rate_steady=36.09  recover=0 inputlog=ok:6 rooms=Now in room 50, 14:01:27
KSA1: stamp OK 8d5df1ebe705
KSB1: run-hw exit=0 pre=c8930724d19d post=c8930724d19d staged_has_pre=1 binary_sha12=8117f8d6e6e0 build_dirty=1 tick_rate=32.60 tick_rate_steady=36.06  recover=0 inputlog=ok:6 rooms=Now in room 50, 14:09:24
KSB1: stamp OK 8117f8d6e6e0
KSB2: run-hw exit=0 pre=c8930724d19d post=c8930724d19d staged_has_pre=1 binary_sha12=8117f8d6e6e0 build_dirty=1 tick_rate=32.42 tick_rate_steady=35.69  recover=0 inputlog=ok:6 rooms=Now in room 50, 14:17:29
KSB2: stamp OK 8117f8d6e6e0
KSA2: run-hw exit=0 pre=f5e1e92dd3a8 post=f5e1e92dd3a8 staged_has_pre=1 binary_sha12=8d5df1ebe705 build_dirty=0 tick_rate=32.60 tick_rate_steady=36.08  recover=0 inputlog=ok:6 rooms=Now in room 50, 14:25:24
KSA2: stamp OK 8d5df1ebe705
KPA1: run-hw exit=0 pre=d6bbee8dab95 post=d6bbee8dab95 staged_has_pre=1 binary_sha12=3798de6a8793 build_dirty=1 tick_rate=31.65 tick_rate_steady=34.75  recover=0 inputlog=ok:6 rooms=Now in room 50, 14:34:27
KPA1: stamp OK 3798de6a8793
KPB1: run-hw exit=0 pre=d6bbee8dab95 post=d6bbee8dab95 staged_has_pre=1 binary_sha12=3798de6a8793 build_dirty=1 tick_rate=32.46 tick_rate_steady=35.69  recover=0 inputlog=ok:6 rooms=Now in room 50, 14:42:18
KPB1: stamp OK 3798de6a8793
KPB2: run-hw exit=0 pre=d6bbee8dab95 post=d6bbee8dab95 staged_has_pre=1 binary_sha12=3798de6a8793 build_dirty=1 tick_rate=31.70 tick_rate_steady=34.81  recover=0 inputlog=ok:6 rooms=Now in room 50, 14:50:20
KPB2: stamp OK 3798de6a8793
KPA2: run-hw exit=0 pre=d6bbee8dab95 post=d6bbee8dab95 staged_has_pre=1 binary_sha12=3798de6a8793 build_dirty=1 tick_rate=31.41 tick_rate_steady=34.65  recover=0 inputlog=ok:6 rooms=Now in room 50, 14:58:15
KPA2: stamp OK 3798de6a8793
```
- **Camera witness (all 9 sheets reviewed, 15 frames each, none short): CLEAN.** Every cell: the PGSB boot text,
  the Maniac Mansion Deluxe title ("Please select two other kids.", START, the kid row) for 2-3 frames, then the
  post-exit `C:\DOSAGS>` prompt; no trails or corruption. KPB1 was filmed under room lighting. KPA2: room
  lights on from frame 9 (14:55:25Z) and the camera turned away from the screen at frames 14-15 (14:56:12Z),
  all after the game had exited (the prompt from frame 7), so the run itself is witnessed.
- Scoring is lab-mmd's (LAB-MMD 38: the logic metric for main-vs-stack, abba.py inputs/ugo for P3).
- **Audio:** local only; `AUDIO-SHA256.txt` per dir.

**2026-09-25 -- POST-FLASH FUNCTION CHECK (operator approval "Yes, check now"; not a scored cell).** USB4VC
0.5.107 (counters build) on vcctrld 3d26789 (daemon_start_t 1790349883.53 before and after: no restart);
`vcctrl board` fw_ver [0, 5, 107] before and after. Relay-on 15:28:41Z, PGSB ready 15:29:36Z (camera frame:
CuteMouse v2.1 beta4 "Installed at PS/2 port", normal PGSB boot), power OFF 15:39:47Z (0 mW at 15:39:52Z).
- **Keyboard:** `ver` + Enter at the prompt -> "MS-DOS Version 6.22" on screen.
- **Mouse:** a brief MMD cell (kmain.exe `8d5df1ebe705`, auto-exit 2000, run-hw exit 0) with a jittered
  drive-walk of 20 clicks (20 s warm-up). Input log: 20 mouse_down + 20 mouse_up, all rc 0. Engine:
  mouse_presses_hw 17 = seen 17, lost_clicks 0. drive-align (unique offset, residuals <= 33 ms): 15 in-window
  host clicks, all registered; 5 in MMD's 27.6 s boot (undecidable by rule; 2 of them still reached the
  driver). **No in-window loss.**
- **Counters, post-CuteMouse baseline -> release (>= 2 s after the last click, age_s 0.3):** ev_in 64,
  pkt_built 64, pkt_ok 64 (40 button edges + 24 moves); pkt_inhibit 0, pkt_timeout 0, pkt_partial 0,
  ev_discarded 0, edge_merged 0, ev_buf_full 0, host_fe 0 (**L_board 0**); host_cmd 34, host_ff 8, host_f5 2
  (the engine and run-hw's collection reboot resetting the mouse); kb_inhibit_retry 4. No mouse.dropped rows.
  Pre-power -> baseline: ev_discarded 2 (vcctrl's two queued test moves, the expected artefact), host_cmd 7,
  host_ff 2 (BIOS + CuteMouse).
- Raw: `tests/harness/results/POSTFLASH-2026-09-25/`.

**2026-09-25 -- ROUND L. Staging record, before any power-on.** Operator approval "when checks pass"; the power-on
waits for the coordinator's "ROUND L GO" (after lab-mmd's MMD determinism guard on the fb83830 arms reads
EQUAL). Driver `build/ws/roundL/driveL.sh`, cell wrapper `cellL.sh`, helper `snapshots.py`.
- **Firmware:** USB4VC 0.5.107, the mouse-delivery-counters build (vcctrl's flash report, hex sha256 98a8b9aa...;
  PB INFO board 1, hw_rev 0); `vcctrl board` fw_ver [0, 5, 107] (post-flash check). vcctrld 3d26789, up since
  15:24:43Z (daemon_start_t 1790349883.53). Any restart inside the round is listed in the result record.
- **Binaries** (`build/ws/roundL/expected.txt`, full sha256 checked; manifest stamps checked per cell):
  `l308.exe` AGSL308 `425c1609...` (`bc9c3704a839`, warm-up); `lmain.exe` AGSLMAIN `9679de80...` (`55cca7e85a28`,
  main fb83830, byte-identical to my build of it); `lpin.exe` AGSLPIN `bcd151b1...` (`e3f9b2f79d0e`, build_dirty 1,
  + ags 0313); `wbfix1.exe` fix1 `56ee6c56...` (`978d8feb1ced`); `scripthk.exe` `9abdbc66...` (`dbc7f4329478`).
  Stamps for lmain/lpin from LAB-MMD 41.2 (lab/mmd d2e876a).
- **Order, cut from the bottom, whole blocks only:** 1. `WARMUPL` (unscored). 2. MMD main-vs-pin ABBA `LMA1`
  `LMB1` `LMB2` `LMA2` (lmain / lpin; LAB-MMD 41/41.1; round K's MMD recipe; >= 2080 s). 3. WB block `WBF1` then
  `WBF2` (wbfix1; LAB-WB 32; WBH6W's fixture and env per 27; >= 1200 s each; a wedge uses that cell's one mains
  cycle, then a read-only fetch, and never stops the round). 4. `SCRIPTH-A0P` (scripthk; LAB-JOURNEYS 9b.5 A1;
  S8H-A0's protocol -- room 35, sound off, auto-exit 5000 -- with the round-H+ click rule: jittered drive-walk,
  60 s warm-up) -- the first cut.
- **Every cell (the round L rule; LAB-JOURNEYS 8.30 A2-A4):** stamp check; `INPUT-LOG.json` (raw) +
  `INPUT-LOG.jsonl` (run-hw-<TAG>'s lock.acquired .. lock.released, plus `mouse.dropped` rows to release + 1.5 s;
  a fetch failure or a missing pair VOIDs); `vcctrl board` + `vcctrl mouse-stats` at lock-take and release with
  the freshness rule (CROSSCHECK-NA, not VOID, when unmet); fw_ver must read 0.5.107 at both points (VOID
  otherwise; A4's fallback coded but not expected, since fw_ver is now exposed). `vcctrl activity`
  daemon_start_t at round start and end. The helper was tested against a fake vcctrl on every firmware path
  and the stale case.
- **Arithmetic** (rounds I-K: MMD cells 472-484 s; WB cells ~18 min clean): boot + warm-up ~555 s, MMD ABBA
  ~1935 s, WBF1 + WBF2 ~2160 s -> ~4650 of ~5160 usable; SCRIPTH-A0P (~600 s) is expected to go to round M.
  Power-off expected ~78 min after relay-on. D35HW, TAIL, the layout control and J are round M's.
- **2026-09-25 ~17:00Z -- NOTE (during the round): `fw=VOID` on WARMUPL (and LMA1, whose helper had already
  started) is a COMPARATOR BUG in `snapshots.py`, not a firmware mismatch.** `vcctrl board` reports `fw_ver` as a
  list, `[0, 5, 107]`, and the helper compared its string form with "0.5.107"; my fake-vcctrl test had used a
  string. The raw reads show the right firmware at both points (`WARMUPL-2026-09-25/BOARD-TAKE.json` and
  `BOARD-RELEASE.json`: fw_ver [0, 5, 107]). Fixed in place at ~17:00Z (both sides normalised to "0.5.107";
  a list, a string, a missing key and 0.5.7 re-tested); the helper is started fresh per cell, so the fix applies
  from **LMB1** on. The SUMMARY lines of WARMUPL and LMA1 stay as written. The firmware check is TAIL's registered
  rule (LAB-JOURNEYS 8.30 A2); MMD and WB scoring do not use it, so no MMD or WB cell is void because of it.

**2026-09-24 -- ROUND B staging.** Driver `build/ws/roundB/driveB.sh`, in the operator's order. It
stops if the HW-MMD-0 fetch fails (nothing is staged over those files) or on any run-hw failure.
- `base.exe` = the gate-0196 exe (`634d0364412e`); `new.exe` = the gate-0212 exe
  (`4612b69a0887`); RT3 probes as run on DOSBox-X (`24dc534cc896` / `484527264cb9`). Each is
  byte-identical to the file whose run manifests show that sha12.
- Lab binaries sha256-verified against LAB-S32.md 8 @ `1f5080f9`: `round-b/timed` `7ba8d49f...`,
  `lab/A2` `08e5ff91...`, `lab/B2` `d46ee5fa...`. `AGSPROBE.EXE` `d0c05016...` per LAB-MMD.md 10.
- Fixtures and envs exactly as pre-registered (S16: SB2C1's; C1P: S2Q1's; CTR: AQF1's;
  HW-MMD: S2M1's).

**2026-09-23 -- DEC1O/DEC1N RESULT (ags 0210): every decoded clip byte-identical; a play's decode
69-88% faster at fixed cycles; accounting exact. VOID by its own pre-registered play-count rule.**
Raw: `tests/harness/results/DEC1O-, DEC1N-2026-09-23/`.
- **Why void:** DEC1N has 7 plays against DEC1O's 9 (and STW's 9). The game picks its ambient
  sounds at random, and the sequence differed between the two runs even at fixed cycles, so "same
  order" and the play count were the wrong bars for this game. The rule was mine.
- **What the evidence still shows:** each of the 4 distinct clips has the same `pcm` and `dev` hash
  every time it played in either cell (sound2 `1732254d`, sound3 `1471e9e1`, sound9 `62be796a`,
  sound10 `92545aef`). pcm accounting is exact in both: DEC1O 566 chunks + 11 drains = 577 =
  `pcm_irqs`; DEC1N 563 + 8 = 571; `overwrites=0`.

| clip | format | Open before | Open after | play tick before | play tick after |
|---|---|---|---|---|---|
| sound10, first play | 11025 Hz 16-bit mono, 107581 samples | 154.3 ms | 20.6 ms (-87%) | 363 ms, a stall | 232 ms, under the threshold |
| sound9, first play | same format, 45160 samples | 65.0 ms | 7.8 ms (-88%) | 168.9 ms | 111.6 ms |
| sound3, first play | 8000 Hz 8-bit, resampled | 45.3 ms | 28.4 ms (-37%) | 99.3 ms | 85.1 ms |
| sound2 | 44100 Hz 8-bit, resampled | 28.9 ms | 9.0 ms (-69%) | 56.4 / 42.9 ms | 38.5 / 25.0 ms |

- Bar 3 met (sound10 > 50%; the resampled sound3 less). Bar 4 met: each tick fell by about the
  Open time saved (sound10 -131 vs -134 ms; sound9 -57.3 vs -57.2 ms).
- Tick times include the probe's own hash loop, which is the same in both builds for the same clip.
- Remaining per play: first-play file I/O (48 ms for sound10 at fixed cycles) and the resampler on
  non-11025 clips. Those are the next S16 B items (the decoded-PCM cache, the room-load preload),
  with numbers first.
- I propose re-running as DEC2O/DEC2N with the bar judged per clip rather than in order, if the
  coordinator wants a non-void witness; the per-clip evidence above is what that would check.

**2026-09-23 -- S16 B, first slice (approved by the coordinator): ags 0210, bit-exact decoder fast
paths. PRE-REGISTRATION DEC1O/DEC1N.**
- *The patch* (`patches/ags/0210-*.patch`): `decode_pcm_block` gets mono and stereo loops with no
  runtime divide and no per-sample `push_back`. A clip already at the mixer rate is moved into the
  output instead of copied. `SDLDecoder::Open` decodes the cached bytes in place instead of copying
  them first. The resampler is unchanged.
- *Bit-exactness, host:* old vs new over 1/2/3 channels, 8/16 bits, 7 rates, odd tails, extremes and
  VOC multi-block appends: 1730 cases, 0 mismatches (integer-only paths; the FP resampler is
  untouched).
- *Cells:* the STW recipe (5 Days `--startr 3`, sound on, OPL3, 5000 ticks, exclusive lock) at
  **fixed cycles** (`tests/harness/confs/dosbox-x-fixed40k-opl3.conf`: core=normal, cycles=fixed
  40000), so that before/after times compare instruction counts, not host load. **DEC1O** = the
  probe on the pre-0210 tree (`0165bac69ff5`); **DEC1N** = the same probe on 0210 (`87898543c1ae`).
  The probe is the STW play/tick probe plus a `decodehash` line per Open (FNV of `_pcm` and
  `_pcmDevice`, and the Open's own time). Diffs are saved with the results.
- **Bars:**
  1. Every `decodehash` line identical between DEC1O and DEC1N (samples, pcm, dev), same order.
  2. pcm accounting exact in both (`pcm_irqs` = expected, `overwrites=0`).
  3. Prediction: `open_us` for sound 10 (same-rate 16-bit mono) falls by > 50%. For sound 3
     (8 kHz 8-bit, resampled) it falls less, since the resampler dominates there.
  4. Each play tick's `self_us` falls by about the `open_us` saved.
- **Void if:** fewer plays than STW (9), or `decodehash` missing.

**2026-09-23 -- `/sdldos:review` of SDL 0195 + ags 0209.** Provenance: both real `git format-patch`
output from the vendor trees (0195 = vendor/SDL `7dcea5ed3`, 0209 = vendor/ags `e95834c3c`), next free
slots in each series (SDL 0194 -> 0195, ags 0208 -> 0209). ASCII only; no `fopen`, no SIMD; port-owned
series, so the neutral-naming rule does not apply; not diagnostics (the MP probe stays out of the
series, saved as a throwaway diff). Built and smoked on DOSBox-X (MP1/MP1P). Code read:
- The ags side is consistent: resume moves `_midiPlanUs` and `_midiLastIrq` by the same IRQ count SDL
  moved the queued stamps, and song time does not move, so the song continues from where it
  stopped; the planner does not run while paused (`MidiPoll` returns unless playing); MIDI `Seek` is a
  no-op; stop and destroy while paused both reach `SDL_DOSMidiDeferEnable(0)`, which now clears the
  pause and the hold.
- Interrupts-off span in the pause: at most 18 OPL key-offs (12 port reads each) or 48 MPU bytes --
  bounded. MPU bytes go out blind, the same as the existing kind-2 replay (`BlindDirectBase`); no
  current lane uses kind 2 (WaveBlaster stays on the poll).
- **Finding (not hit by any fixture yet):** `SDL_DOSMidiDeferHold(false)` clears `g_mdq_hold`
  unconditionally. If `SDL_DOSOpl3Detect`/`InitChip`/`Shutdown` run while the replay is paused (their
  wrappers hold, then release), the release lifts the pause's hold and the ISR plays the paused song's
  queued ~2 s while the game thinks it is paused. That needs a second OPL sink opened while the ISR
  owner is paused (another MIDI clip started during a music pause). Fix, one line: release to
  `g_mdq_paused ? 1 : 0`. Proposed as SDL 0196 in the next slice, gated with that slice's binary,
  so the 0209 pin stays the binary the gate passed.


**2026-09-23 -- PRE-REGISTRATION STW0/STW1: what each sound-on stall tick is spent on (MEASUREMENT
ONLY, DOSBox-X, no fix).** Question: in each sound-on stall tick of the Gate 3 fixture, which call
holds the main thread, and how much of the sound-on whole-run loss (8.2 on the 486: SB2C1 whole-run
38.61 vs S2F2 39.26 sound off; over 5000 ticks that is 5000/38.61 - 5000/39.26 = ~2.1 s more wall time)
would removing it buy? **What the code does per play (read first):** `load_sound_clip` (sound.cpp)
reads the asset only on a cache miss (SndCache, 32 MB, so the first play of each clip only), then
`audio_core_slot_init` -> `SDLDecoder::Open` makes a full copy of the cached bytes (`raw =
*_sampleData`, 215 KB for sound 10), decodes it whole (`dos_audio_decode_pcm`: parse + resample to
the mixer rate), converts it whole to the device format (`convert_to_device_format`), then builds the
AudioPlayer -- all synchronously inside the script's play call. **Probe** (throwaway, never a gate
binary; diff saved with the results): uclock() buckets per tick, printed on every `stallwhat` tick and
on every tick with a play: `io_us` (OpenAsset + Read, cache miss), `copy_us` (the `raw` copy),
`decode_us` (`dos_audio_decode_pcm`), `convert_us` (`convert_to_device_format`), `voice_us`
(`audio_core_slot_init`'s AudioPlayer build + the channel start in `play_audio_clip_on_channel`),
each with the clip's name and sample count; the remainder of `script_us` is script work.
**Cells** (Gate 3 fixture: 5 Days `--startr 3`, drive-walk 2 s, 512x384 centred 1x, alias on, 5000
ticks, taken under the exclusive DOSBox-X lock): **STW1a/STW1b** sound on (`--sb-live`, OPL3 conf),
**STW0a** sound off (the script-only base). **Predictions:**
- H1: decode + convert are the largest sound-attributable share of every sound-10 stall tick (> 50%
  of the sound-on minus sound-off stall time), because both walk the whole clip on the main thread.
- H2: `io_us` is non-zero only on the first play of each clip (the cache holds every repeat).
- H3: `copy_us` and `voice_us` are each < 10% of the sound-attributable time.
- H4: the ~250-320 ms (486) lattice stall is script work with sound off, and the same script work
  appears with sound on: the sound-on stall = the script stall + the play's own cost, not a
  different stall.
**Gain estimate method:** the sound-attributable ms on DOSBox-X do not transfer to the 486 (the
emulator runs at host speed), so I report the SHARES per bucket from DOSBox-X and apply them to the
486's ~2.1 s. Result: an estimated whole-run with each bucket removed, against the 39.2 floor. This
is an estimate from two different runs and binaries (SB2C1, S2F2); only a hardware probe cell,
which needs a GO, measures it. **Void if:** the probe lines are missing on the sound ticks (code not
executing), `pcm_irqs=0` in STW1 (the device was not opened), another DOSBox-X overlapped a cell (the
lock's `.who`), or the fixture did not reach room 3.
**Amendment before any cell ran (same day), two deviations:** (1) no walking on DOSBox-X --
`drive-walk.sh` drives the target machine through vcctrl only; the plays come from the game's own
ambient-sound timer, which fires without input (UR5/SBL cells, no walking, show the same plays).
(2) DOSBox-X has no stall ticks on the plays: at host speed a play stays far under the 250 ms
threshold (UR5 and SBL1 each logged one stall, tick 1). So the probe also prints `stwtick` on every
tick with a play, and the shares are computed over those ticks, not over `stallwhat` ticks. Caveat
for the estimate: the emulator's relative costs (a memcpy, integer decode loops, emulated file I/O)
need not match the 486's, so the shares are a ranking plus a first estimate, not the 486's split.
Probe binary `e61660b27a4c` (build_dirty=1), runner `build/ws/stw/run-stw.sh` (exclusive lock,
display :211, Gate 3 cfg for STW0, the same cfg with `[sound] enabled=1` for STW1, 5000 ticks).

**Decision after 8.2 (reported, not acted on, until the coordinator verifies):**
- `VIBRA` C within Gate 3's band: ABBA it (the step 6 design, sound off vs on) and go to 8.3.
- `VIBRA` C slowed: root-cause in software on the Vibra (it is a real card, so the "PicoGUS
  hardware" explanation is already gone). Narrow patches, a DOSBox-X gate, then a hardware ABBA.
- `PGSB`-only slowdown: record it as a `HARDWARE.md` row (PicoGUS SB emulation), with the Vibra
  numbers beside it. It does not block the gate.

**8.3 -- Audio correctness on real hardware (per lane, per music backend).** The capture harness is
the judge (standing feedback: the operator listens only when the evidence is already strong, with the
captures attached).
- Music: melody and tempo match the reference tune.
- SFX: the chime cross-correlates.
- No dropouts or underruns over a full 5000-tick window.
- SFX audible while music plays (mixing).
- 5 Days' own opening music and one scripted SFX present in the capture.

After that, one golden-reference listen by the operator: VIBRA+OPL3, VIBRA+WB and PGSB+OPL3 captures
sent as files.

**8.4 -- Proposed gate (operator to confirm when 8.2 is in): "Gate 3S".** 5 Days in play on `VIBRA`
with **OPL3 music + SFX on** meets the Gate 3 bar: both tick figures 39.2-40.8, completeness >= 95%,
`fps_p50` >= 40, camera witness clean, the 8.3 audio verdict passes, x2 replication. WaveBlaster and
`PGSB` get recorded figures, and a claim only if the operator asks for one. If 8.2 shows sound-on
cannot reach 40 on a real SB16, what to trade (for example, a lower MIDI tick rate or fewer PCM
voices) is an operator decision, brought with numbers.

**Stop conditions for step 8:**
- The capture can't hear the card.
- A lane can't be booted reliably (the profile-select retry is 3).
- The post-collection hang recurs twice in one cell (`HARDWARE.md`).
- Any arm crashes or hangs the target.
- Screening results contradict all three readings above.

### Step 9: Maniac Mansion Deluxe at full speed (after step 8)

**2026-09-23 operator decision:** step 9 runs in parallel on dosags-lab-mmd (`~/git/dosags-lab-mmd`,
branch `lab/mmd`, display 261, ags 0290-0309 / SDL 0240-0249), starting with 9.1. Hardware rounds for
it still go through the coordinator and me.

**2026-09-24 operator decisions (relayed):** the MMD target is **full speed, 40 logic ticks/s, at
~20 fps** (the stretch target), and lab-mmd builds **lever G** (interpreter pre-decode) with full
gates. Next hardware batch: nothing powers on without an operator ask through the coordinator. I
draft the batch plan once lab-wb's pump fix B and lab-metric's G2b have results.

**Goal:** MMD **in play** meets the Gate 3 bar at 512x384 centred 1x 16-bit, then again with Sound
Blaster sound on (the step 8 winner). The fix must be in the engine or port; game data is user-supplied
and never modified.

**9.0 -- Re-baseline on the current binary** (alias on, which S2M1 never had): character-select (the
S2M1 screen) and **the first in-play room reached through the game's own flow**. After DUPCHAR, a
debug jump is a diagnostic only, never the measured entry. Driving the character-select needs held
clicks at this frame rate: hold, then release (STATUS.md, `input_stack`).

**9.1 -- Find out what dispatch actually is, before any fix.** Probe build (never a gate binary). Split
`process_events_dispatch` into: script VM time per script function (name and instruction count), engine
API calls made from script, GUI polling, and **nested game loops**. A blocking `Wait()` inside a
handler runs whole ticks inside dispatch, which would explain `render_to_screen` appearing nested. That
would also make 26.47 ms partly an accounting artefact. Pre-registered hypotheses:
- H0: nested-loop accounting; the real cost is the nested render.
- H1: bytecode interpreter cost on a 486 (a script-heavy SCUMM-style verb UI).
- H2: one DOS-expensive engine call per tick, the same class as the old `Clock::now()`.
- H3: GUI control polling across many controls.

DOSBox-X can rank candidates; real hardware settles them. The 894 ms single outlier gets its own
line.

**9.2 -- Fix in order of breadth.** Engine-wide fixes (interpreter hot path, an expensive API) come
before anything that only helps this title. Each fix follows the usual pattern: a DOSBox-X
screen-equality gate across all rows, then a real-hardware cell. Report the figure each fix buys; don't
bundle.

**9.3 -- Gate:** MMD in play meets the Gate 3 bar x2, witness clean, then the same with SB sound on.
If 9.1 shows the budget cannot be met without something the player would notice, bring the trade to
the operator with numbers before deciding.

**Deferred behind steps 8-9:** step 7 (ViRGE and Cirrus); Gate 4 (32-bit); tracker music (libxmp-lite
is not wired, but none of the four in-profile titles need it); the external write-up.

## Next campaign (operator direction 2026-09-23): working music + high fps at 8/16/32 bpp

**Goal:** at each colour depth, a fixture **in play with sound ON** meets the Gate 3 bar, with music
that works on **both OPL3 and WaveBlaster**.

**Gates S8 / S16 / S32** (one per depth, same bar):
- Both tick figures 39.2-40.8, `fps_p50` >= 40, completeness >= 95%, camera witness clean, x2
  replication -- the Gate 3 bar, with sound on.
- **Audio judged by the counters** in the same cells (valid at 512x384, where the capture dongle is
  blind): `pcm_irqs` = expected from chunk accounting, `overwrites=0`, MIDI `late_writes=0`,
  `silent_irqs=0` outside room loads.
- Plus **one 640x480 capture listen per depth** (the dongle locks 640x480), judged by the capture
  harness first.
- **WaveBlaster must pass as well as OPL3 at every depth.** Today WB is on the poll (the SDL/0098
  320 us TX-delay busy-wait keeps it out of the ISR replay), and hardware SB5W had 69% of events
  > 50 ms late at the 6 fps intro; the on-time WB transport is dosags-lab-wb's slice.

**2026-09-24 -- WaveBlaster gate amendment (coordinator, from LAB-WB 24 / 24.1 / 24.2 at lab/wb
`d5d3e202`, `abece12e`, `cead2326`; the lab data stays in LAB-WB, none is copied here).** A WB cell
passes on the counters and the capture as follows; the old onset-ratio-against-poll criterion is
dropped.
- **A, on time (all required):** A1 `late_writes=0`; A2 `plan_behind=0`; A3 `qfull=0`; A4 rearm
  stuck 0 (pump cells only); A5 clock ratio 0.95-1.02; A6 `isr_writes` >= 95% of the song model.
- **B, content (required):** chroma against a same-binary poll control, and no onsets in rests.
- **C, optional:** onset count within +/-10% of a same-binary blind capture.
- **Provisional:** song-match F1 >= 0.70.
- **Operator decisions, 2026-09-24 (relayed by the coordinator):** keep pursuing the WB pump; test
  the WB on the Vibra16S after perf on the current configuration settles.

**Fixtures:**

| gate | depth | fixture | sound-off baseline |
|---|---|---|---|
| S8 | 8-bit | Trilby's Notes in play, 512x384x8 (S2T2) | stable 39.91 |
| S16 | 16-bit | 5 Days a Stranger in play, 512x384 centred 1x (Gate 3) | Gate 3 met; 8.2 sound-on whole-run ~38.6 vs the 39.2 floor |
| S32 | 32-bit | AGS Quest forced-32, 640x480x32 1:1 (S2Q1) | stable 35.41 -- already below the bar with sound off |

**Split:**
- dosags-worker (me): S16 and **every hardware round**; the only one who touches hardware and this
  file.
- dosags-lab-journeys: S8, after its current slice.
- dosags-lab-metric: S32, after its validation.
- dosags-lab-wb (`~/git/dosags-lab-wb`, display 241, ags 0270-0289 / SDL 0230-0239): the WaveBlaster
  on-time transport.
- dosags-lab-mmd (`~/git/dosags-lab-mmd`, branch `lab/mmd`, display 261, ags 0290-0309 / SDL
  0240-0249): step 9, Maniac Mansion Deluxe at full speed, in parallel (operator decision
  2026-09-23), starting with 9.1 (the dispatch breakdown); on the DOSBox-X hold until the hub lock lands.

Lab workers' hardware needs go through the coordinator; lab results come back as a one-line link here
to their `LAB-*.md` when the branch merges.

**Open items:**
- A second OPL sink opened during a music pause lifts the pause's hold (`SDL_DOSMidiDeferHold(false)`
  clears it unconditionally), so the paused song's queued ~2 s plays. Fix: SDL 0196, my next slice,
  gated with its own binary.
- `agsquest-alias-y60` one-tick startup nondeterminism (splash 81 vs 82, sound off): a lab thread,
  queued by the coordinator.

**2026-09-24 -- drive-walk alignment (harness; lab-journeys' flag, via the coordinator).** drive-walk
clicks while run-hw holds the input lock, and that hold is not the game's input window, so "host clicks
= driver presses" could not be judged across rounds. The host cannot see the window live: at 512x384
the capture dongle cannot lock (every in-game witness frame is black), and the game leaves no LED trace
(`vcctrl led-changes` over round G shows only reset/boot pairs). So the window is placed after the run:
`tests/harness/drive-align.py RESULTS_DIR` pairs the host clicks with the engine's click journeys
(ags 0250, `t_ms` from engine start), which have the same irregular cadence. This fixes the clock
offset, then puts engine start, boot end and quit (`duration_s` +/-1 s) on the host clock. Each host
click is classed before/boot/in/edge/after, in `DRIVE-ALIGN.txt` beside the raw logs; no raw file is
edited. `drive-walk.sh` now logs millisecond stamps, `down_at=` and `rc_down`/`rc_up` per click.
Retro, on the 12 cells whose binaries have journeys (round B's S16 cells predate 0250 and are refused):
- S8HO2: in-window 46 vs `mouse_presses_hw` 46; 3 boot clicks and 28 after quit made up its 77.
- S8H-O1: in-window 28 vs hw 26. The lock was released at 16:53:49, about 45 s before quit, so the
  window was cut short; host clicks 26 and 27 are unpaired mid-run. The old log cannot tell a refused
  send from a transport loss; the new `rc` fields will.
- CAPH1I 44 (+1 edge) vs 43, click 45 unpaired; CAPHC 43 vs 42, clicks 42-43 unpaired.
- The other eight agree within their boot/edge clicks.
Whole-second stamps leave residuals up to 1376 ms against a 1500 ms tolerance: a pairing, not a proof.
From round H the stamps are ms and the tolerance 600 ms. Boot clicks are not decidable: the driver's
counters reset at SDL's mouse init, somewhere inside boot, and nothing logs when.

**2026-09-25 -- PRE-REGISTRATION DEC35 (9b.2 decode fix; DOSBox-X only, before any DEC35 cell ran).**
The fix for LAB-JOURNEYS 9b.2's two decode costs in room 35 (baseline, probe exe `0dc72c3dc075`,
`STALL35-opl3`): (a) ambient 18's first play, `PlayAmbientSound` 299 ms of which `decode_pcm` 248 ms,
inside the 515 ms end-of-dialogue stall; (b) a repeating clip re-decoded on every play, 107 x ~14 ms =
1517 ms of `decode_pcm` from t=38.9 s to the end.
- **ags 0215** (wip/9b2 `ab0c9154`): the resampler in integers; bit-exact (fuzz PASS on host SSE, host
  x87 and DJGPP under DOSBox-X; its control FAILs on all three). Almost every Trilby clip is 24000,
  22050 or 44100 Hz against the 11025 Hz mixer, so it runs on almost every play.
- **ags 0216** (wip/9b2 `9fb29dfd`): a decoded-PCM cache. Keyed by the identity of the sound cache's byte buffer (a weak
  reference, so an entry dies with its bytes); holds the device-format samples, shared and immutable;
  LRU under `DOSAGS_PCM_CACHE_KB` (default 2048); `DOSAGS_PCM_CACHE_VERIFY=1` also decodes each hit
  afresh and counts mismatches. Reports `DOS-PORT pcmcache hits= misses= evictions= uncacheable=
  bytes= peak_bytes= cap_kb= verify= verify_mismatches=` in RUNMANI.LOG.
**Binaries (one clean tree, only the named patches differ; all build_dirty=0):** CTRL-P = main at this
commit + lab-journeys' throwaway stall probe (`stall-probe-throwaway.patch` at lab/journeys, never
landed); FIX-P = CTRL-P + 0215 + 0216; R-P = CTRL-P + 0215 only (splits the two).
**Cells (DOSBox-X fixed 40k, EXCLUSIVE, one at a time on :211; `S8_ROOM=35 s8-cell.sh OUT opl3 --env
SDL_HINT_DOS_MIDI_DEFER_DEDUPE=0`, STALL35-opl3's recipe):** DEC35-C (CTRL-P), DEC35-R (R-P), DEC35-F
(FIX-P), DEC35-V (FIX-P with `DOSAGS_PCM_CACHE_VERIFY=1`).
**Measures, from the LABPROBE lines and RUNMANI.LOG:** M1 the `decode_pcm` bracket inside ambient 18's
`PlayAmbientSound` at the end of the opening dialogue, and that bracket's ms; M2 the count and total ms
of `decode_pcm` brackets (the probe prints those >= 2 ms) after t=38.9 s; M3 the end-of-dialogue
`stall100` gap in ms; M4 the pcmcache line.
**Predictions:**
- DEC35-C reproduces 9b.2: M1 within +/-10% of 248 ms; M2 >= 90 brackets. If not, the baseline moved
  and R/F are judged against DEC35-C alone (recorded, not void).
- DEC35-R: M1 <= 45% of DEC35-C's (instruction estimate ~40%); M2 still >= 90 brackets, each smaller.
- DEC35-F: M1 as DEC35-R's (+/-10%: the first play is a cache miss); M2 = 0 brackets after the
  repeating clip's first play; M4 hits >= 90, evictions 0, bytes <= cap.
- M3 (F vs C): shorter by at least 80% of (C's M1 - F's M1).
- DEC35-V: verify_mismatches = 0 with verify >= 90.
**Void if** a cell is not exclusive, the stall does not occur at the end of the dialogue in DEC35-C,
or any binary is dirty.
**Then:** the gate (gate-alias.sh) and the ratchet on main + 0215 + 0216 (no probe), review, land;
room 35's 486 stall (S8H-O1's 1543 ms) becomes a round H candidate cell, on the operator's go.
**DEC35 builds (2026-09-25, before any DEC35 cell ran; `build/ws/dec35/build.sh`, each arm = main
`2c52eeb0` + its extra ags patch files copied in untracked for the build only; all `build_dirty=0`):**
CTRL-P `29f89b6ed84f` (+ probe), R-P `39e868922fb2` (+ 0215 + probe), FIX-P `2fa6ab52f25f` (+ 0215 +
0216 + probe); strings check: all three carry LABPROBE, only FIX-P the pcmcache line. Tree restored to
main after (`476abb1c5a32`). Results dirs `tests/harness/results/DEC35{C,R,F,V}-2026-09-25/` (the
8-character forms of DEC35-C/R/F/V); driver `build/ws/dec35/cells.sh`, one cell at a time on :211.
**2026-09-25 -- DEC35 RESULT (scored by dec35-score.py 326a54bb; `DEC35C-2026-09-25/DEC35-SCORE.txt`).
VERDICT DEC35 FAIL, on 0215's registered size alone.** First attempt: DEC35C lock-blocked 3600 s (not
run), R/F/V "the game never ran" (my relative OUT path; click-cell cds into tests/harness), all void and
discarded; re-run whole 03:49-04:06Z, every cell rc 0 with its registered binary, `build_dirty=0`.
- C: M1 248 ms (decode_pcm inside PlayAmbientSound 298 ms), M2 106 / 1499 ms, M3 492 ms: reproduces 9b.2.
- R (0215): M1 211 ms, **FAIL against <= 112** (45% of C): the integer resampler takes 15%, not ~60% --
  my cost model was wrong; most of ambient 18's decode is not the resampler. Repeats 12.1 vs 14.1 ms: PASS.
- F (0215 + 0216): M1 211 (= R) PASS; 0 repeat decodes after the clip's first play PASS; `pcmcache hits=106
  misses=4 evictions=0 bytes=312374 cap_kb=2048` PASS; M3 456 vs 492, 36 ms shorter (>= 30) PASS.
- V: `verify=106 verify_mismatches=0` PASS.
**Decision (coordinator, 2026-09-25):** accepted as scored, not re-tuned. 0215 + 0216 land lab-gated
(gate-alias + ratchet + sdldos:review; both exact); a 486 room-35 pair then MEASURES the gain, with
`memory_min_free_kb` against the pre-landing figure, and a worse end-of-dialogue stall on the 486 makes
them a revert candidate. A new pre-registration will bracket decode_pcm_block vs the resampler vs the
allocation for ambient 18.

**2026-09-25 -- DESIGN + PRE-REGISTRATION TPIT (an IRQ-safe PIT read; coordinator order; nothing built).**
**The race (from the code):** in PIT mode the SB ISR times itself with `SDL_DOSAudioReadTimer()`
(SDL_dos_audio_synth.h: latch counter 0 at port 43h, read two bytes from 40h). The main thread reads the same
counter through DJGPP's `uclock()` (SDL's systimer, 4 other SDL DOS files, 27 ags files), which latches and
reads with interrupts ON. An SB IRQ between the main thread's latch and its byte reads finds the 8254's latch
and read flip-flop mid-sequence: the ISR's own latch is ignored (a pending latch holds), and its two reads
return the main thread's leftover byte plus a live byte. The ISR's delta is then garbage -- the 22-54 ms
`isr_max_us` outliers (hub docs/timing.md, 0024d52) -- and it biases `isr_ns_per_write`, now a judged figure
(CAP3c cost window; LAB-JOURNEYS 8.28 bounds the inflation at ~3.9 us of C3-512's 25.5).
**Fix, at the source, for every caller:** make each main-thread counter read atomic against IRQs.
- **SDL 0198** adds `__wrap_uclock()` to src/timer/dos/SDL_systimer.c: save EFLAGS, `cli`, `__real_uclock()`,
  restore EFLAGS (so a caller already at IF=0 stays at IF=0, and the first call's PIT reprogramming, which
  DJGPP's uclock does once, also runs atomically).
- **The ags link** gets `-Wl,--wrap=uclock` (Makefile, next to the ags linker flags), so every undefined
  reference to `uclock` in the final link -- ags objects, libSDL3.a, libc -- goes through the wrapper. No
  call site changes.
- No ISR code changes. Behaviour: each uclock() holds IF=0 for its 3 port I/Os plus the arithmetic
  (single-digit us on the 486), added IRQ latency the SB/MIDI paths already tolerate far more of.
- Rejected: discarding a corrupted delta in the ISR (a second latch/read cannot be trusted while the
  flip-flop is mid-sequence, and a period bound only hides the large outliers); cli at each uclock call
  site (27+ sites, and libc's own).
**Cells (DOSBox-X, the cap3c base -- main's series + LAB-JOURNEYS' CAP3 series as in cap3c -- room 35,
DRAIN_STI=0, `SDL_HINT_DOS_AUDIO_TIMER_RDTSC=0` to force the PIT, one at a time, EXCLUSIVE):** TPIT-C (the
base), TPIT-F (base + SDL 0198 + the wrap flag), TPIT-R (the base on the RDTSC timer, the reference).
**Predictions:** C shows at least one `isr_max_us` >= 15000 (the outlier; its power); F shows none
(`isr_max_us` < 12000); F's `isr_ns_per_write` is below C's and within 10% of R's. `late_writes`,
`underruns`, `overwrites` and the tick figures are unchanged between C and F (same class).
**Void if** C shows no outlier in two runs (no power: reported as such, not re-tuned), a binary is dirty, or
a cell is not exclusive. **Then:** gate + ratchet, review, land; the 486 reading rides on the next CAP3c
follow-up cell, which this must precede (coordinator).
**TPIT AMENDMENT 1 (2026-09-25, coordinator's correction, before anything is built): the first uclock()
must run with interrupts ON.** DJGPP's uclock() reprograms PIT channel 0 on its first call and then WAITS for
the BIOS tick at 0040:006C to change (hub docs/timing.md). At IF=0, IRQ 0 never fires, the tick never moves,
and the machine hangs. The design above cli-wrapped every call, the first included: wrong.
- **`__wrap_uclock` now:** while its own `initialised` flag is clear, it calls `__real_uclock()` exactly as
  the caller left the interrupt flag (no cli), then sets the flag. Only later calls are cli-wrapped, and the
  IF=0 window is `__real_uclock()` alone (save EFLAGS, cli, call, restore EFLAGS -- nothing else inside).
- **Stated assumption:** DJGPP re-runs its reprogramming only when its own init condition fires again
  (`__bss_count` changed, i.e. a program restart via unexec), which these programs never do. A caller that
  itself makes the FIRST call at IF=0 would hang with or without the wrapper (unchanged behaviour).
- **Added lab check (TPIT-1, before C/F/R):** a cell of the F binary in which the first uclock() in the
  program goes through the wrapper (SDL's timer init makes it; confirmed by a breakpoint-free check: the
  wrapper counts first-path calls and the status line reports `uclock_first=1`). Its guard is run-dosbox's
  timeout: **no STDOUT.TXT/RUNMANI.LOG by the timeout = FAIL** (a hang), not VOID.
- **Added control of that guard (TPIT-H, lab-only hook, never landed):** the same binary plus a hook that
  cli-wraps the first call too (`DOSAGS_TEST_UCLOCK_CLI_FIRST=1`). It must hang to the timeout; if it
  returns, the guard has no power (DOSBox-X would then not model the wait) and TPIT-1 proves nothing about
  the 486 -- recorded as such.
**TPIT BUILD + TPIT-1 / TPIT-H RESULT (2026-09-25).** SDL 0198 (`src/timer/dos/SDL_dosuclockwrap.c`, its own
object: `__real_uclock` must be a STRONG reference -- a weak one, tested with the DJGPP toolchain, does not
pull libc's uclock.o out of the archive and resolves to 0), ags 0217 (`DOS-PORT uclockwrap first= wrapped=`),
and `-Wl,--wrap=uclock` on the ags link (Makefile). In the built exe, 349 call sites call `___wrap_uclock`;
the only two direct calls to `_uclock` are the wrapper's own. F (main + 0198 + 0217) `98ceb0e9d2e4`,
`build_dirty=0`, sha256 `9d6389ad31cce2fa427b543ed35fbe8c1885e75de75defe722e885f1c8884bd5` (a rebuild was
byte-identical); H (F + the lab hook `DOSAGS_TEST_UCLOCK_CLI_FIRST=1`, never landed) `7b37c994e6c7`,
`build_dirty=1`. Both cells DOSBox-X, 5 Days room 3, `--sb-live`, fixed 40k, auto-exit 1500, one at a time.
TPIT-1 and TPIT-H ran on main + 0198 (the landing candidate), not on the cap3c base: their question is
whether the first call returns, which does not depend on the CAP3 series (and that series no longer applies
on main after 0275). C/F/R stay on the cap3c base as registered.
- **TPIT-1 PASS:** exit 0, `uclockwrap first=1 wrapped=302064`.
- **TPIT-H: did NOT hang** (exit 0, `uclockwrap first=1 wrapped=302139`, the hook armed: `SET
  DOSAGS_TEST_UCLOCK_CLI_FIRST=1` in RUN.BAT, the cli-wrapped first path in the exe). **Explained by DJGPP's
  own code, not by the emulator:** `__uclock`'s first-call wait loops `do { errno = 0; __dpmi_yield(); }
  while (errno == 0 && tick unchanged)` (disassembled: `0x625140` is `_errno`), and `__dpmi_yield` (real-mode
  INT 2Fh AX=1680h) sets errno when AL comes back 80h -- no multitasker releases time slices. On plain MS-DOS
  under CWSDPMI (the 486) and in DOSBox-X nothing answers 1680h, so the loop exits on its first pass and the
  first call never waits on the tick, at IF=0 or not. The hang is real only under a host that honours 1680h
  (a Windows 9x DOS box, some multitaskers). So TPIT-H cannot have power on this platform, and TPIT-1's
  result carries to the 486 for the same reason. The amendment's first-call rule stays (it costs nothing and
  covers yield-capable hosts). **Correction for hub docs/timing.md:** "the first call waits for the BIOS tick"
  holds only when `__dpmi_yield` succeeds.
- **Verdicts as registered (coordinator ruling, 2026-09-25): TPIT-1 PASS. TPIT-H MISSED as registered -- the
  hang control did not hang, so it has NO POWER on this platform.** Dated reason: DJGPP's first-call wait
  exits on `__dpmi_yield`'s errno when nothing answers INT 2Fh/1680h, as on MS-DOS + CWSDPMI and DOSBox-X.
  The first-call rule is kept (free; covers 1680h hosts). The hub docs/timing.md correction is the
  coordinator's.
- **C/F/R base (coordinator, option b):** lab-journeys has re-cut the CAP3 ags patches onto main (after 0275),
  renumbered ags 0330-0332, with SDL 0223-0228 unchanged. C/F/R run on that tree + 0198 once it is committed,
  so TPIT is measured on the tree that will land. Not before.
- **2026-09-25 -- NOTE on TPIT-H's REASON (coordinator; the entries above are left as written): the reason is
  PROVISIONAL.** hub-sb-port's probe under DOSBox-X (`dosbox-x.conf`) reads `int2f 1680 -> AL=00 (answered)` and
  `__dpmi_yield errno=0`, so in DOSBox-X the first-call loop does NOT exit on errno, and something else let
  TPIT-H return (a candidate: the real-mode reflection of INT 2Fh services IRQ0, so the tick advances despite
  the protected-mode cli). Pending hub-sb-port's direct test. **"Plain DOS + CWSDPMI: nothing answers 1680h" is
  UNMEASURED on the 486.** The verdict stands as a fact: TPIT-H did not hang, so the control has no power.
- **2026-09-25 -- TPIT-H's reason, MEASURED (replaces "provisional" above; hub docs/timing.md 0e3f35d, YLD2
  probe):** in DOSBox-X at the default `dos` idle API, INT 2Fh/1680h IS answered and the BIOS tick advances
  inside the first `__dpmi_yield` even with IF=0, so uclock's first-call loop ends on the tick -- that is why
  TPIT-H exited 0. With the idle API off, errno ends it instead. My errno explanation above was wrong for
  DOSBox-X. The 486 remains unverified. The verdict is unchanged: no power.
- **2026-09-25 -- TPIT C/F/R RESULT: VERDICT TPIT PASS** (tpit-score.py 606da1d; `TPITC-2026-09-25/TPIT-SCORE.txt`).
  DOSBox-X, room 35, s8-cell opl3, DRAIN_STI=0, DOS_PORT_LOG=1, one at a time on :211; built in a scratch
  worktree at lab/journeys 61f80ab (the CAP3 re-cut), each arm in its own build dir. First attempt VOID (my
  setup: the scratch worktree had no game data, so no game ran -- kept as `VOID-TPIT{C,F,R}-nogamedata-*`);
  re-run with the same binaries and tags.
  - C (the re-cut, `f90938dd7e0d`, PIT): `isr_max_us` **29398** (the outlier: C has power), `isr_ns_per_write`
    25114, isr_burst 328.
  - F (+ SDL 0198 + ags 0217 + the wrap flag, `c3c81b632b85`, PIT, `uclockwrap first=1 wrapped=468901`):
    `isr_max_us` **7200** (< 12000: PASS), `isr_ns_per_write` **22200** (below C: PASS; within 1.9% of R's
    22619: PASS).
  - R (C's binary, `confs/dosbox-x-fixed40k-opl3-pentium.conf`, RDTSC): `isr_max_us` 7386, 22619.
  - late 0/0, underruns 0/0, overwrites 0/0, steady 40.33 / 40.35 (C/F): the same class.
  The PIT-read race inflated the per-write figure by ~2.9 us (11.6%) here; the fix brings the PIT reading to
  the RDTSC reference. The 486 reading rides on the next CAP3c follow-up cell, which TPIT precedes.
- **Build trap found on the way (for the landing):** dropping `-Wl,--wrap=uclock` from the Makefile does not
  clear `CMAKE_EXE_LINKER_FLAGS` from build/ags's CMake cache, so a later build without 0198 fails to link
  (`undefined reference to __wrap_uclock`). Any build that removes the flag needs `make ags-clean` first.



**2026-09-25 -- PRE-REGISTRATION D35HW (the 486 measurement of ags 0215 + 0216; round L; ABBA agreed with the
coordinator, 2 cells the registered fallback, read as a direction only).**
- **Arms (clean builds, one change apart):** C = main at 40f319f, 0215/0216's parent (stamp `476abb1c5a32`,
  byte-identical to round J's C3P N binary, sha256 `1f664bc3...`); F = main at 9ac4ced, the 0215 + 0216 landing
  (stamp `5f052e7319af`). Both built at staging; each stamp is checked in the cell manifest. 0240 is in
  neither arm (lab-journeys' point), so it cannot confound the stall.
- **Cells:** `D35C1 D35F1 D35F2 D35C2`, the S8 room-35 fixture as C3512 minus its DRAIN_STI env: trilbysnotes,
  `--startr 35`, `DOSAGS_TAS_AUTO_EXIT_TICK=5000`, direct framebuffer, `ACSETUP-ON-512X384-ROUND.CFG`, sound on
  (PGSB, OPL3), drive-walk with its jittered gap after a 60 s warm-up; ~10 min a cell.
- **Primary M1:** the end-of-dialogue stall, defined as the largest `DOS-PORT stall100` with `journey=0` in the
  run (S8H-O1 1543 ms at t=48 s, C3512 1536 ms at t=80 s: the only journey-free stall over 1 s in each).
  D = mean(F) - mean(C), N = the larger same-arm spread (|C1-C2|, |F1-F2|).
- **Prediction:** D in [-250, -30] ms (the lab removed 36 ms of a 492 ms stall; the 486 runs this code ~3x
  slower). **GAIN** if D < -N and D <= -30. **Revert candidate** (coordinator rule) if D > +N: the stall got
  worse on F. Anything else: no measurable effect on the 486, reported as such.
- **Secondary:** F's `pcmcache` line: hits >= 50, evictions 0, bytes <= cap; `memory_min_free_kb` F >= C - 512
  (the cache's 312 KB plus allocator slack; pre-landing figures 145536 / 145600 KB); `stallshare
  share_nojourney` and `tick_rate_steady` reported per arm; `late_writes`, `underruns`, `overwrites`,
  `silent_irqs` the same class in both arms.
- **VOID per cell:** wrong binary or `build_dirty != 0`; not room 35; no journey-free stall >= 1000 ms in a C
  cell (the fixture changed); the witness not clean; the round L input-log rule (INPUT-LOG.jsonl from
  run-hw-<TAG>'s lock.acquired to lock.released, plus the raw INPUT-LOG.json; a fetch failure or a missing
  pair VOIDs the cell).
- **Scorer** `tests/harness/d35hw-score.py`, committed before staging.

**2026-09-25 -- ROUND L RESULT (raw; SUMMARY lines copied verbatim).** Relay-on 16:44:51Z, cap 18:14:51Z; power
OFF 18:07:32Z (`on=False mW=0`), re-read `on False mW 0` at 18:07:54Z. SCRIPTH-A0P was dropped by the cap rule
(204 s left, typical 600 s) -> round M. Every cell: run-hw exit 0, recover 0, sha256 pre = post = staged, stamp OK,
`INPUT-LOG.jsonl` from run-hw-<TAG>'s lock pair (6 events per MMD cell, 27 per WBF cell), lock-take and lock-release
snapshots valid (age_s 0.2-0.7), `BOARD-TAKE/RELEASE.json` fw_ver [0, 5, 107] in all 7 cells, vcctrld
daemon_start_t 1790349883.5326602 at round start and end (no restart).
```
vcctrld daemon_start_t at round start: 1790349883.5326602
WARMUPL: run-hw exit=0 pre=425c1609f50a post=425c1609f50a staged_has_pre=1 binary_sha12=bc9c3704a839 build_dirty=0 tick_rate=30.29 tick_rate_steady=33.10  recover=0 inputlog=ok:6 fw=VOID:firmware [0, 5, 107], staging record says '0.5.107' xcheck=ok rooms=Now in room 50, 16:55:49
WARMUPL: stamp OK bc9c3704a839
LMA1: run-hw exit=0 pre=9679de80e742 post=9679de80e742 staged_has_pre=1 binary_sha12=55cca7e85a28 build_dirty=0 tick_rate=31.93 tick_rate_steady=35.25  recover=0 inputlog=ok:6 fw=VOID:firmware [0, 5, 107], staging record says '0.5.107' xcheck=ok rooms=Now in room 50, 17:05:42
LMA1: stamp OK 55cca7e85a28
LMB1: run-hw exit=0 pre=bcd151b1fa1d post=bcd151b1fa1d staged_has_pre=1 binary_sha12=e3f9b2f79d0e build_dirty=1 tick_rate=31.51 tick_rate_steady=34.81  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 17:14:32
LMB1: stamp OK e3f9b2f79d0e
LMB2: run-hw exit=0 pre=bcd151b1fa1d post=bcd151b1fa1d staged_has_pre=1 binary_sha12=e3f9b2f79d0e build_dirty=1 tick_rate=31.55 tick_rate_steady=34.82  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 17:23:28
LMB2: stamp OK e3f9b2f79d0e
LMA2: run-hw exit=0 pre=9679de80e742 post=9679de80e742 staged_has_pre=1 binary_sha12=55cca7e85a28 build_dirty=0 tick_rate=31.87 tick_rate_steady=35.26  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 17:31:40
LMA2: stamp OK 55cca7e85a28
WBF1: run-hw exit=0 pre=56ee6c563be4 post=56ee6c563be4 staged_has_pre=1 binary_sha12=978d8feb1ced build_dirty=0 tick_rate=25.19 tick_rate_steady=25.75  recover=0 inputlog=ok:27 fw=OK xcheck=ok rooms=Now in room 1,Now in room 2,Now in room 3,Now in room 99, 17:49:05
WBF1: stamp OK 978d8feb1ced
WBF2: run-hw exit=0 pre=56ee6c563be4 post=56ee6c563be4 staged_has_pre=1 binary_sha12=978d8feb1ced build_dirty=0 tick_rate=25.21 tick_rate_steady=25.77  recover=0 inputlog=ok:27 fw=OK xcheck=ok rooms=Now in room 1,Now in room 2,Now in room 3,Now in room 99, 18:07:27
WBF2: stamp OK 978d8feb1ced
SCRIPTH-A0P dropped: 204s left, typical 600s (18:07:27) -> round M
vcctrld daemon_start_t at round end: 1790349883.5326602
power OFF 18:07:32: on=False mW=0
```
- **fw=VOID on WARMUPL/LMA1** is the helper's comparator bug (NOTE ~17:00Z above); the raw reads are [0, 5, 107].
- **End-of-round ENOSPC check (every cell):** no `No space left`/ENOSPC/errno 28 text in any cell dir; one
  continuous audio segment with a clean `end` in WARMUPL, LMA1, LMB2, LMA2, WBF1 and WBF2. **LMB1 only:** seg02
  short (368640 bytes), seg03 zero bytes (`drop ... pages=14 OSError`), seg04 reconnected 17:08:49Z -> the known
  17:07:54-17:08:49Z audio gap. MMD is sound-off and not audio-scored, so there is no re-run. The only zero-byte
  files elsewhere are the empty `snapshots.out`/`INPUT-LOG.err` (nothing was written to stderr).
- **Camera witness (all 7 camera sheets and 7 card sheets reviewed; none short, none frozen): CLEAN.**
  - WARMUPL, LMA1, LMB1, LMB2, LMA2 (15 frames each): the PGSB boot text and RUN.BAT, a blank mode switch, the Maniac
    Mansion Deluxe character select ("Please select two other kids.", START, the kid row) for frames 4-6
    (~30 s, matching `loop_ms=31089` for 999 ticks on WARMUPL), then the post-exit `C:\DOSAGS>` prompt, dim on
    camera, from frame 7. No trails or corruption. The card sheet goes black at the mode switch and never
    re-locks after exit (the known post-exit capture trap); the camera is the witness here.
  - WBF1, WBF2 (41 frames each, 41 unique card frames): the 5 Days intro (car, the mansion narration), the title
    with its buttons, (WBF1) the DAY ONE card, then the office room ("And the gentleman thief makes his entrance"),
    held static to the end of the sheet. The engine ran to `ticks=16050` with 2662 renders/presents (WBF1), so
    the static room is the fixture idling, not a wedge. **No WB wedge and no recovery in either cell** (recover=0,
    run-hw exit 0). Both cells have two ~133 s sampler gaps at the same offsets, identical on card and camera
    (WBF1 after 17:39:02Z and 17:42:14Z; WBF2 after 17:57:27Z and 18:00:39Z): harness-side and systematic, not
    screen faults.
- Scoring: MMD is lab-mmd's (the pin REFUTED, LAB-MMD 41.4); WBF is lab-wb's.
- **Audio:** local only; `AUDIO-SHA256.txt` per dir.

**2026-09-25 -- ROUND M. Staging record, before any power-on; order CONFIRMED by the coordinator after round L.**
The power-on waits for the operator's approval, relayed by the coordinator as "ROUND M GO". Driver
`build/ws/roundM/driveM.sh` (refuses to start without `ORDER-CONFIRMED`), round L's `cellL.sh` + `snapshots.py`
reused as-is (the fw comparator fixed).
- **Binaries** (`build/ws/roundM/expected.txt`, full sha256 checked at staging and by the driver; manifest stamps
  checked per cell): `l308.exe` `425c1609...` (`bc9c3704a839`, warm-up); `fine.exe` = lab-mmd `AGSFINE.EXE`
  `0d63234e9a6e35faf426877d034bd53777e298cf87d335dd6642bf805c84ee7a` (`867f4cb6d9be`, build_dirty 1, both arms;
  LAB-MMD 45/45.1/45.2, lab/mmd 85da6b1; hashed at lab-mmd's path and after the copy); `wbfix1.exe` fix1
  `56ee6c563be4a7ea723d861ade0fe3d8e21a149f843f1fb758c9c7fd8e7cc739` (`978d8feb1ced`); `cap3d.exe` TPIT F
  `f0ec94a1...` (`c3c81b632b85`); `d35c.exe` `1f664bc3...` (`476abb1c5a32`); `d35f.exe` `3dee45f4...`
  (`5f052e7319af`); `cap3c.exe` `f242d324...` (`78683aa4c501`); `scripthk.exe` `9abdbc66...` (`dbc7f4329478`).
- **Order, cut strictly from the bottom** (once a block is dropped for time, every block after it is dropped;
  a block starts only if cap - 240 s leaves its need):
  1. `WARMUPM` (l308, unscored).
  2. MMD FINE ABBA `FINEA1` `FINEB1` `FINEB2` `FINEA2` (one binary; A = default, B = `DOSAGS_TICKSTATS_FINE=0`;
     round K/L's MMD recipe: auto-exit 1000, ACSETUP-OFF-512X384-ROUND; need 2160 s).
  3. `WBFP` (LAB-WB 34, lab/wb 32f53e5): wbfix1 on WBF1's exact fixture (SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1,
     5days ACSETUP-ON.CFG, auto-exit 16000, backend wb, WB_TX_DELAY=320, WB_DRR_POLL=1) plus
     `DOSAGS_MIDI_TICK=poll`, the only difference; `--timeout 1200` (need 1200 s); NO wedge budget: a failed WBFP
     powers off and ends the round (no mains cycle, no fetch).
  4. `CAP3d-D1`, `CAP3d-D2` (LAB-JOURNEYS 8.33; need 1160 s), then `cap3d-score.py` decides `CAP3d-V1` (only on
     V1-NEEDED, at its MAX_PER_IRQ; need 560 s, otherwise round N).
  5. The tail, all expected to be cut: D35HW ABBA `D35C1 D35F1 D35F2 D35C2` or its registered 2-cell fallback;
     `TAIL-0`/`TAIL-1` (cap3c, RUNHW_MIN_WAIT_S=300); `SCRIPTH-A0P` (round L's definition).
- **Tags:** all 16 are distinct under run-hw's 8-char [A-Z0-9_] manifest rule (e.g. CAP3DD1, SCRIPTHA) and
  unused in main's and every lab worktree's results.
- **Every cell:** round L's rule unchanged (stamp; INPUT-LOG pair; board + mouse-stats snapshots with the freshness
  rule; fw_ver 0.5.107; daemon_start_t at round start and end; the end-of-round ENOSPC check).
- **Arithmetic** (round L's actuals, with the new wrapper: MMD 492-593 s, warm-up 582 s, WBF 1045/1102 s;
  trilbysnotes 5000-tick ~540-560 s): boot 75 s; WARMUPM ends ~0:11; FINE ABBA ~0:47; WBFP (has ~2350 s) ~1:05;
  CAP3d D1+D2 (has ~1250 s, margin ~90 s) ~1:24; V1 then has ~130 s -> round N, and the tail with it. Power-off
  expected ~1:24 after relay-on.
- **Driver checks:** `bash -n`; a hardware-free simulation (fake vcctrl, fake cell) of the full-time path, a short
  cap (FINE dropped, then every later block), and a failed WBFP (power off, exit 1, nothing after); the FINE arms'
  env read back from the simulated cell lines. Fixed on the way: the draft stored the CAP3d verdict in `V` (the
  vcctrl path), which would have broken the power-off after CAP3d; it is `CV` now.

**2026-09-25 -- AUDIOPRB GATE: SDL 0199 + ags 0218 (coordinator queue item; criteria written before the lab
cells' data).** ags 0059's per-poll timing (and the SDL 0141/0146/0147 and ags 0071/0072 brackets it collects)
goes behind `SDL_HINT_DOS_AUDIO_DIAG_TIMING`, default OFF. No current gate reads it (lab-wb: none; lab-journeys:
none, run-hw.sh only fetches the file; lab-metric: only the closed D2-era scorers lab-d2/lab-d2hw/lab-s32f1).
Clean build `c7a073cdd72e` (sha256 063eac5d...), build_dirty 0.
- **Found on the way:** every `AUDIOPRB.LOG` the 486 harness ever fetched (142 dirs) is byte-identical
  (`64659cba...`, two DOSBox-X-sized windows): a stale file on the target's disk, left over from 0059's
  original sink, which 0061 stopped writing on 2026-09-14. The fetch has returned no new data since. The
  run-hw.sh fetch-list edit waits until round M is off (run-hw.sh is executing during the round).
- **Lab check** (DOSBox-X :211, one at a time; `s8-cell.sh ... opl3`, `S8_ROOM=16`: MIDI on the OPL3, fixed
  40k, auto-exit 5000): APMAIN = main d635277 (`b56839568382`), APOFF = `c7a073cdd72e` default, APON = the same
  with the hint set. PASS needs all of:
  1. APOFF's RUNMANI.LOG has exactly one audioprb line, `timing=off total_calls=N` with N > 0, and no window or
     `pump_hist` line.
  2. APON's has the `pump_hist` line with lt1ms + 1to5ms + 5to9ms + ge9ms == calls == the header's
     total_calls, the windows as before, and regwrite and miditick calls > 0 in its windows (the gated SDL and
     ags brackets still time when asked).
  3. rc 0 in all three.
  Reported, not gated: `uclockwrap wrapped` per tick in each arm (APOFF should be lower than APMAIN by about
  3 x polls/tick plus 2 x the bracketed calls; APON about APMAIN).
- Then the full ratchet `--no-record` on `c7a073cdd72e`. exe-bytes is 8598510 against the 8596893 limit
  (+1617) and needs the coordinator's exact-value approval before landing.
- **2026-09-25 ~20:05Z -- AUDIOPRB lab check, first reading and a supplementary pair (registered before its data).**
  APMAIN / APOFF / APON all rc 0 (the first APMAIN/APOFF attempt is VOID: a relative results path, kept as
  `VOID-AP*-relpath`). Criterion 1 MET (APOFF: one line, `timing=off total_calls=5248`). Criterion 2: the
  pump_hist line MET (buckets 5181+65+1+1 = 5248 = calls = the header's total_calls; 27 windows, 0 dropped), but
  **its last clause is NOT MET: regwrite and miditick calls are 0 -- and 0 on APMAIN (ungated main) too.** This
  fixture runs `midi_tick=isr`: OPL writes take the deferred path, which returns before 0141's timer
  (SDL_dos_audio_synth.c:1066 vs :1071), and the ISR branch of MidiPoll skips the miditick bracket. The clause
  could not be met by this fixture on any build; my specification error. Criterion 3 MET.
  Supplementary pair, same fixture plus `DOSAGS_MIDI_TICK=poll` (MIDI dispatched on the main thread, so
  0141's timer and the miditick bracket run): APMAINP (main `b56839568382`) and APONP (`c7a073cdd72e` + the
  hint). PASS if APONP's windows show regwrite > 0 and miditick > 0, and APMAINP's show both > 0 as well (the
  fixture really exercises them). An APOFFP cell is not needed: 0218 skips those snapshots entirely when off.
  **Supplementary pair RESULT: PASS.** APMAINP (main `b56839568382`, `midi_tick=poll`): regwrite 17444, miditick
  1039 over 27 windows. APONP (`c7a073cdd72e` + the hint): regwrite 17460, miditick 1041, 27 windows, and the
  pump_hist line (5181+64+1+2 = 5248 = calls). Both build_dirty 0, rc 0. The gated SDL 0141 timer and the miditick
  bracket time when asked, with the same counts as ungated main.

**2026-09-25 -- ROUND M RESULT (raw; SUMMARY lines copied verbatim).** Relay-on 18:33:45Z, cap 20:03:45Z; power OFF
19:53:03Z (`on=False mW=0`), re-read `on False mW 0` at 19:53:15Z. Every cell: run-hw exit 0, recover 0, sha256 pre =
post = staged, stamp OK, fw=OK (fw_ver [0, 5, 107]), xcheck ok, INPUT-LOG pair present; vcctrld daemon_start_t
1790349883.53 at start and end (no restart). CAP3d-V1 was not needed by time: D35HW (2-cell fallback, 408 s left),
TAIL and SCRIPTH-A0P were cut -> round N, as expected.
```
relay-on 18:33:45, cap 20:03:45
vcctrld daemon_start_t at round start: 1790349883.5326602
WARMUPM: run-hw exit=0 pre=425c1609f50a post=425c1609f50a staged_has_pre=1 binary_sha12=bc9c3704a839 build_dirty=0 tick_rate=30.29 tick_rate_steady=33.28  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 18:43:05
WARMUPM: stamp OK bc9c3704a839
FINEA1: run-hw exit=0 pre=0d63234e9a6e post=0d63234e9a6e staged_has_pre=1 binary_sha12=867f4cb6d9be build_dirty=1 tick_rate=31.96 tick_rate_steady=35.20  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 18:52:44
FINEA1: stamp OK 867f4cb6d9be
FINEB1: run-hw exit=0 pre=0d63234e9a6e post=0d63234e9a6e staged_has_pre=1 binary_sha12=867f4cb6d9be build_dirty=1 tick_rate=32.81 tick_rate_steady=36.33  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 19:00:51
FINEB1: stamp OK 867f4cb6d9be
FINEB2: run-hw exit=0 pre=0d63234e9a6e post=0d63234e9a6e staged_has_pre=1 binary_sha12=867f4cb6d9be build_dirty=1 tick_rate=33.20 tick_rate_steady=36.45  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 19:08:59
FINEB2: stamp OK 867f4cb6d9be
FINEA2: run-hw exit=0 pre=0d63234e9a6e post=0d63234e9a6e staged_has_pre=1 binary_sha12=867f4cb6d9be build_dirty=1 tick_rate=31.92 tick_rate_steady=35.23  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 19:17:05
FINEA2: stamp OK 867f4cb6d9be
WBFP: run-hw exit=0 pre=56ee6c563be4 post=56ee6c563be4 staged_has_pre=1 binary_sha12=978d8feb1ced build_dirty=0 tick_rate=24.98 tick_rate_steady=25.53  recover=0 inputlog=ok:27 fw=OK xcheck=ok rooms=Now in room 1,Now in room 2,Now in room 3,Now in room 99, 19:34:40
WBFP: stamp OK 978d8feb1ced
CAP3d-D1: run-hw exit=0 pre=f0ec94a14bb7 post=f0ec94a14bb7 staged_has_pre=1 binary_sha12=c3c81b632b85 build_dirty=0 tick_rate=31.37 tick_rate_steady=40.29  recover=0 inputlog=ok:234 fw=OK xcheck=ok rooms=Now in room 35, 19:44:21
CAP3d-D1: stamp OK c3c81b632b85
CAP3d-D2: run-hw exit=0 pre=f0ec94a14bb7 post=f0ec94a14bb7 staged_has_pre=1 binary_sha12=c3c81b632b85 build_dirty=0 tick_rate=31.29 tick_rate_steady=40.30  recover=0 inputlog=ok:55 fw=OK xcheck=ok rooms=Now in room 35, 19:52:57
CAP3d-D2: stamp OK c3c81b632b85
CAP3d after D2: VERDICT CAP3d FAIL, 1 FLAG(s)
D35HW (2-cell fallback) dropped as a block: 408s left < 1160s (19:52:57) -> round N
TAIL dropped: an earlier block was cut (19:52:57) -> round N
SCRIPTH-A0P dropped: an earlier block was cut (19:52:57) -> round N
vcctrld daemon_start_t at round end: 1790349883.5326602
power OFF 19:53:03: on=False mW=0
```
- **CAP3d scorer after D2** (`CAP3d-D2-2026-09-25/CAP3D-SCORE-AFTER-D2.txt`): `VERDICT CAP3d FAIL, 1 FLAG(s)`. The FAIL is
  `mechanism: 156 arrivals per 2.57 ms window (<= 128)`, identical in D1 and D2. The FLAG is D2 `silent_elsewhere [1138]`.
  Everything else PASS: late_writes 0, cap_hits 0, underruns 0, overwrites 0, sb_alive, isr_max 6124 us (<= 10000),
  tpit_witness. The scorer derives B = 606 but did not ask for V1. Interpretation is lab-journeys'.
- **CAP3d-D2 early collect (harness-side, reported, not a VOID by any registered rule):** run-hw's camera
  stability wait read the dark room-35 scene as `static` for 60 s past its 90 s floor and proceeded to collect at
  t+102 s. It released the input lock at 19:49:15Z, about 65 s before the game's own auto-exit (ENGINE HAS
  SHUTDOWN, ticks=5002; the files came back complete). Consequences: the drive-walk stopped after 15 clicks (D1:
  74; engine seen 15 vs 42), and the camera witness ends at 19:49:14Z, mid-game. In D1 the camera read `blind`, so
  run-hw waited for the real exit. The CAP3d cells had no RUNHW_MIN_WAIT_S (only TAIL did). Fix for round N:
  RUNHW_MIN_WAIT_S covering the auto-exit on every trilbysnotes cell.
- **End-of-round ENOSPC check (every cell):** no ENOSPC text in any dir; one continuous audio segment with a clean
  `end` and no `drop` in all 8. The only zero-byte files are the empty `snapshots.out`/`INPUT-LOG.err`.
- **Camera witness (all 8 camera and card sheets reviewed; none short):**
  - WARMUPM, FINEA1, FINEB1, FINEB2, FINEA2 (15 frames each): CLEAN. The PGSB boot, the MMD character select, then
    the post-exit `C:\DOSAGS>` prompt from frame 7 (FINEA1: the select for frames 4-5, then the mode switch).
  - WBFP (41 frames, 41 unique on the card): CLEAN, the same sequence as WBF1/WBF2 (intro, title, DAY ONE, then the
    office room static to the end: the fixture idling at 16000 ticks). **No WB wedge and no recovery.** The same two
    ~134 s sampler gaps as WBF1/2, identical on card and camera (after 19:24:28Z and 19:27:41Z).
  - CAP3d-D1 (29 frames): CLEAN. Boot, room 35's intro caption and dialogue, play, then the prompt from frame 21.
    The card sheet is `frozen` (512x384, which the capture card cannot lock -- the known trap); the camera is the
    witness.
  - CAP3d-D2 (11 frames): PARTIAL. Boot, the same intro and dialogue, then play up to 19:49:14Z; the last ~65 s of
    play and the exit are not on the sheet (see the early collect above).
- Scoring: FINE is lab-mmd's (LAB-MMD 45.3, 299534e: GAIN -0.691 ms/tick); WBFP is lab-wb's; CAP3d is lab-journeys'.
- **Audio:** local only; `AUDIO-SHA256.txt` per dir.

**2026-09-25 -- ROUND N. Staging record, before any power-on.** Operator approval 22:27Z ("when checks pass", 90-min cap,
relayed by the coordinator); the power-on waits for the coordinator's GO. Driver `build/ws/roundN/driveN.sh` (refuses
to start without `ORDER-CONFIRMED`); round L's `cellL.sh` + `snapshots.py`; run-hw.sh at 7efa08b (saves each cell's
RUN.BAT; --pre-line/--post-line/--stdout-to/--collect). 0315's run-hw.sh hunk is set aside
(`build/ws/0315-run-hw.diff`) and lands only after this round powers off, so the round runs the committed harness.
- **Binaries** (`build/ws/roundN/expected.txt`, full sha256 checked at staging and by the driver; stamps per cell):
  | file | sha256 | stamp | source |
  |---|---|---|---|
  | `l308.exe` | `425c1609f50ac62cb712109f383e1fff99955d77830f93943dc3d491d849607f` | `bc9c3704a839` | warm-up (round M copy) |
  | `land1.exe` | `07b604f8cc6a4d22433dd19b578273e87b3f97fa0379191bc5e87dbd78c61eed` | `e93cb957c3be` | lab-wb `build/lab/land1/ags.exe` (LAB-WB 36) |
  | `pace.exe` | `50175c3bf8da7aee90d06a37c348a98bbaab1b58d0f075fd280aec6bf7c761f7` | `0fe3bf4be411` | lab-journeys `build/ws/recut250/ags.exe` (8.35 note) |
  | `d35c.exe` | `1f664bc3b9272365a893775dae8f0dbc43b75f29d9c57d2716882967f2871c3b` | `476abb1c5a32` | round M copy (PLAN D35HW) |
  | `d35f.exe` | `3dee45f4145cf7d3c77f783a4a88cead08a7d6fdec5d0c184f7b34035ae833d1` | `5f052e7319af` | round M copy |
  | `cap3c.exe` | `f242d32469ac01c20947be79cb3e4b1b7b4fc00cfac7c619e7212220c2c53f3e` | `78683aa4c501` | round M copy (TAIL) |
  | `scripthk.exe` | `9abdbc660312ea82095acfeb555de52e64d611d64107eb8e00b35c77c9638e94` | `dbc7f4329478` | round L/M copy |
  Lab binaries hashed at their source paths and after the copy; the round M copies match round M's record.
- **Order, cut strictly from the bottom** (a block starts only if cap - 240 s leaves its need):
  1. `WARMUPN` (l308, MMD recipe, unscored). **MAINABS is not in this round:** 0315 has not landed (its ratchet
     is running), so its binary cannot be staged before the start -> the next round.
  2. `WBLC` (LAB-WB 36): WBF1's exact fixture and env (5days, ACSETUP-ON.CFG, auto-exit 16000, backend wb,
     WB_TX_DELAY=320, WB_DRR_POLL=1, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1) plus `SDL_HINT_DOS_AUDIO_WB_RTC_PUMP=1`;
     `--timeout 1200` (need 1200); RUNHW_MIN_WAIT_S at WBF1's default (90); one wedge recovery (round L's
     wedge_fetch), and the round continues.
  3. `PACE-H-ON`, `PACE-H-OFF` (8.35/8.36; need 1170): C3-512 (room 35, 512x384 ACSETUP-ON-ROUND, auto-exit 5000,
     walker), `SDL_HINT_DOS_MIDI_DEFER_DRAIN_STI=0`; OFF adds `SDL_HINT_DOS_OPL_PACE_K=0`.
  4. LOGRAM (8.40 + A1; need 1350): first `XMSCHK`, a read-only `get-file` of `C:\MTCP\XMSDSK.EXE`, which must be
     20016 B with sha256 `d3a79e8aeffbccd18ecc03de49f56aaa5475f18e2ca3155d205e9f436aab232c` (the host copy, checked).
     Missing or different -> LOGRAM is dropped (no mid-round send) -> round O with a send-file. Then `LOG-CF`,
     `LOG-RAM` on pace.exe, C3-512 with the DEFAULT drain (no DRAIN_STI), walker. RUN.BAT in both arms:
     `CHKDSK C: > CHKDSK.TXT`, `C:\MTCP\XMSDSK.EXE 512 L: /y /t > XMSDSK.TXT`, `MEM /C > MEMC.TXT`, the game,
     `C:\MTCP\XMSDSK.EXE /u /y > NUL`; LOG-RAM redirects to `L:\STDOUT.TXT`, deletes a stale STDOUT.TXT first,
     and copies it back. XMSDSK.TXT, CHKDSK.TXT and MEMC.TXT are collected. **Deviation from A1's staging text,
     stated for the coordinator's check:** CHKDSK (the cluster size) and MEM /C (the resident size) are recorded
     from RUN.BAT in BOTH arms instead of typed at the prompt, so the arms stay identical except the redirect.
     DOS_PORT_LOG is not set.
  5. The tail, all expected to be cut: D35HW ABBA or its 2-cell fallback; TAIL-0/1 (RUNHW_MIN_WAIT_S=300, as
     registered); SCRIPTH-A0P.
- **RUNHW_MIN_WAIT_S=270 on every trilbysnotes cell except TAIL** (coordinator's round N rule): CAP3d-D1, which
  waited for the real exit, proceeded at 267 s (exit ~207 s after launch, plus the 60 s still-screen rule).
- **Tags:** WARMUPN, WBLC, PACEHON, PACEHOFF, LOGCF, LOGRAM, D35C1/F1/F2/C2, TAIL0/1, SCRIPTHA under the 8-char
  rule; all unused in main's and every lab worktree's results.
- **Every cell:** round L's rule (stamp; INPUT-LOG pair; board + mouse-stats snapshots; fw_ver 0.5.107;
  daemon_start_t at start and end; the end-of-round ENOSPC check), plus the saved RUN.BAT.
- **Arithmetic** (round L/M actuals; from relay-on; usable 5160 s): boot 75 s; WARMUPN ~580 -> ~0:11; WBLC ~1100
  -> ~0:29; PACE-H 2 x ~585 -> ~0:49; LOGRAM XMSCHK ~150 + 2 x ~600 -> ~1:11. D35HW then has ~885 s < 1170 ->
  cut, with TAIL and SCRIPTH. Power-off expected ~1:12 after relay-on.
- **Driver checks:** `bash -n`; a hardware-free simulation (fake vcctrl and cell) of the full-time path, a cap
  that drops WBLC and then every later block, an XMSDSK mismatch (LOGRAM and everything after dropped), and a
  WBLC failure (one recovery and fetch, the round continues). Each cell's arguments and RUNHW_MIN_WAIT_S were
  read back from the simulated calls.

**2026-09-25 -- ROUND N RESULT (raw; SUMMARY lines copied verbatim).** Relay-on 22:33:03Z, cap 00:03:03Z; power OFF
23:56:04Z (`on=False mW=0`), re-read `on False mW 0` at 23:56:30Z (the coordinator verified 0 mW independently). Every
cell: run-hw exit 0, recover 0, sha256 pre = post = staged, stamp OK, fw=OK, xcheck ok, INPUT-LOG pair present, and
the cell's RUN.BAT saved; vcctrld daemon_start_t 1790349883.53 at start and end. The round ran ~6 min ahead of
plan, so D35HW's 2-cell fallback fit (1359 s left < 2340 for the ABBA); TAIL (185 s left) and SCRIPTH-A0P were cut
-> round O, below WBLC2 (coordinator).
```
relay-on 22:33:03, cap 00:03:03
vcctrld daemon_start_t at round start: 1790349883.5326602
WARMUPN: run-hw exit=0 pre=425c1609f50a post=425c1609f50a staged_has_pre=1 binary_sha12=bc9c3704a839 build_dirty=0 tick_rate=30.13 tick_rate_steady=33.27  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 22:42:12
WARMUPN: stamp OK bc9c3704a839
WBLC: run-hw exit=0 pre=07b604f8cc6a post=07b604f8cc6a staged_has_pre=1 binary_sha12=e93cb957c3be build_dirty=0 tick_rate=32.98 tick_rate_steady=33.89  recover=0 inputlog=ok:27 fw=OK xcheck=ok rooms=Now in room 1,Now in room 2,Now in room 3,Now in room 99, 22:55:38
WBLC: stamp OK e93cb957c3be
PACE-H-ON: run-hw exit=0 pre=50175c3bf8da post=50175c3bf8da staged_has_pre=1 binary_sha12=0fe3bf4be411 build_dirty=0 tick_rate=31.21 tick_rate_steady=40.30  recover=0 inputlog=ok:234 fw=OK xcheck=ok rooms=Now in room 35, 23:05:20
PACE-H-ON: stamp OK 0fe3bf4be411
PACE-H-OFF: run-hw exit=0 pre=50175c3bf8da post=50175c3bf8da staged_has_pre=1 binary_sha12=0fe3bf4be411 build_dirty=0 tick_rate=31.27 tick_rate_steady=40.29  recover=0 inputlog=ok:241 fw=OK xcheck=ok rooms=Now in room 35, 23:14:58
PACE-H-OFF: stamp OK 0fe3bf4be411
XMSCHK: size=20016 sha256=d3a79e8aeffbccd18ecc03de49f56aaa5475f18e2ca3155d205e9f436aab232c (23:16:20)
LOG-CF: run-hw exit=0 pre=50175c3bf8da post=50175c3bf8da staged_has_pre=1 binary_sha12=0fe3bf4be411 build_dirty=0 tick_rate=32.31 tick_rate_steady=40.26  recover=0 inputlog=ok:242 fw=OK xcheck=ok rooms=Now in room 35, 23:26:23
LOG-CF: stamp OK 0fe3bf4be411
LOG-RAM: run-hw exit=0 pre=50175c3bf8da post=50175c3bf8da staged_has_pre=1 binary_sha12=0fe3bf4be411 build_dirty=0 tick_rate=32.24 tick_rate_steady=40.32  recover=0 inputlog=ok:234 fw=OK xcheck=ok rooms=Now in room 35, 23:36:24
LOG-RAM: stamp OK 0fe3bf4be411
D35HW: 1359s left < 2340s -> the registered 2-cell fallback (23:36:24)
D35C1: run-hw exit=0 pre=1f664bc3b927 post=1f664bc3b927 staged_has_pre=1 binary_sha12=476abb1c5a32 build_dirty=0 tick_rate=31.17 tick_rate_steady=40.23  recover=0 inputlog=ok:232 fw=OK xcheck=ok rooms=Now in room 35, 23:46:21
D35C1: stamp OK 476abb1c5a32
D35F1: run-hw exit=0 pre=3dee45f4145c post=3dee45f4145c staged_has_pre=1 binary_sha12=5f052e7319af build_dirty=0 tick_rate=31.63 tick_rate_steady=40.22  recover=0 inputlog=ok:245 fw=OK xcheck=ok rooms=Now in room 35, 23:55:58
D35F1: stamp OK 5f052e7319af
TAIL dropped as a block: 185s left < 1320s (23:55:58) -> round O
SCRIPTH-A0P dropped: an earlier block was cut (23:55:58) -> round O
vcctrld daemon_start_t at round end: 1790349883.5326602
power OFF 23:56:04: on=False mW=0
```
- **WBLC** (lab-wb scores it): `midi=wb`, `midi_tick=rtc`, `c_redrain=74`, late_writes 0, stuck_at/late_at empty,
  ENGINE HAS SHUTDOWN at ticks 16058. The cell took 13.5 min (WBF1/2: ~18): steady 33.89 vs ~25.5. lab-wb's
  scoring of D is theirs (the coordinator relays WBLC failed D; LAB-WB 38 re-registers the window).
- **PACE-H-ON/OFF** (lab-journeys scores them): ON `pace=128/2570 pwait=80/32972/445 peak=144/0 isr_max_us=7823`,
  pgdetect 1, budget 448, late 0, cap_hits 0; run-hw collected at 278 s (after the real exit).
- **LOGRAM** (lab-journeys scores it): XMSCHK read the card's `C:\MTCP\XMSDSK.EXE` as 20016 B,
  sha256 d3a79e8a...232c (= the host copy; the exe itself is not committed, only its hash). Both arms: XMSDSK.TXT
  "Installed as drive L:", CHKDSK.TXT and MEMC.TXT collected, RUN.BAT saved. LOG-RAM's STDOUT.TXT came back
  complete (231825 B, ENGINE HAS SHUTDOWN).
  - **CHKDSK C: (read-only, LOG-CF): 32,768 bytes in each allocation unit** (so the predicted period is ~24 s);
    2,014,511,104 bytes total, 61,478 units, 13,319 available; **683 lost allocation units found in 19 chains**.
    Nothing changed. Operator decision (~23:28Z): fix in round O as the FIXC pre-step (CHKDSK /F, chains kept as
    .CHK files for review). XMSDSK resident: 688 B conventional (MEMC.TXT).
- **D35HW, the registered 2-cell fallback** (d35hw-score.py 8af473c, unchanged; `D35F1-2026-09-25/D35HW-SCORE.txt`):
```
D35C1 C sha=476abb1c5a32 M1=1741 ms at t=85183 pcmcache=None memfree=145600 steady=40.23 share_nj=0.0701 late=495 underruns=0 overwrites=0 silent=7 input_log=232 events
D35F1 F sha=5f052e7319af M1=1102 ms at t=81279 pcmcache={'hits': 110, 'misses': 4, 'evictions': 0, 'uncacheable': 0, 'lapsed': 0, 'entries': 4, 'bytes': 312374, 'peak_bytes': 312374, 'cap_kb': 2048, 'verify': 0, 'verify_mismatches': 0} memfree=145856 steady=40.22 share_nj=0.0581 late=480 underruns=0 overwrites=0 silent=4 input_log=245 events
D35F2: no result
D35C2: no result
M1 (end-of-dialogue stall): D = F - C = -639.0 ms, N = NA (2-CELL FALLBACK (direction only)); predicted D in [-250, -30]
secondary: pcmcache hits>=50/evictions 0/bytes<=cap PASS; memory_min_free_kb F >= C - 512 PASS
VERDICT D35HW DIRECTION shorter on F (fallback: no noise figure)
```
  D = -639 ms is larger than the predicted [-250, -30]; the fallback carries no noise figure, so it is a
  direction only, as registered.
  **2026-09-25 coordinator decision: D35HW is closed.** Reported as DIRECTION shorter on F (D = -639 ms, outside
  the predicted [-250, -30]; no N, so GAIN is not claimed). No full ABBA scheduled: nothing gates on it (ags
  0215 + 0216 landed in 9ac4ced), and 486 time goes to MMD/PACE/WB. D35HW is removed from round O.
- **End-of-round ENOSPC check (every cell):** no ENOSPC text; one continuous audio segment, no drop, in all 8.
- **Camera witness (all 8 camera and card sheets reviewed; none short): CLEAN.**
  - WARMUPN: boot, the MMD character select, the post-exit prompt.
  - WBLC (30 frames, 30 unique on the card): the 5 Days intro, title, DAY ONE, the office room to the end (the
    fixture idling), room lights on. One ~134 s sampler gap after 22:48:52Z, identical on card and camera (the
    known sampler gap). No wedge, no recovery.
  - PACE-H-ON, PACE-H-OFF, LOG-CF, LOG-RAM, D35C1, D35F1 (29-30 frames each): boot, room 35's intro caption and
    dialogue, play, then the prompt after the real exit (RUNHW_MIN_WAIT_S=270 held each collect past the
    auto-exit). The card is `frozen` at 512x384 (the known lock trap); the camera is the witness. PACE-H-OFF: a
    hand passes the frame edge at frame 4 and the room light changes at frame 18; the screen is unaffected.
- **Audio:** local only; `AUDIO-SHA256.txt` per dir.

**2026-09-25 -- ROUND O. Staging record, before any power-on.** Round O needs its own operator approval (the coordinator asks
once this is committed); the power-on waits for GO. Driver `build/ws/roundO/driveO.sh` (refuses without `ORDER-CONFIRMED`);
round L's `cellL.sh` + `snapshots.py`; run-hw.sh at 221fb28 (fine timing ON by default; `--no-fine-timing` for MAINABS).
- **Binaries** (`build/ws/roundO/expected.txt`; stamps checked per cell):
  | file | sha256 | stamp | source |
  |---|---|---|---|
  | `l308.exe` | `425c1609f50ac62cb712109f383e1fff99955d77830f93943dc3d491d849607f` | `bc9c3704a839` | warm-up |
  | `mainabs.exe` | `952c914b9ce77b0e0e9c6ead50c50c4de443dbeb79271486010516ddfc0607d0` | `3cf8c4a48fe6` | landed main 221fb28 (main + 0315), saved before the CAP3/PACE build |
  | `land1.exe` | `07b604f8cc6a4d22433dd19b578273e87b3f97fa0379191bc5e87dbd78c61eed` | `e93cb957c3be` | lab-wb land1 (WBLCP, WBLC2) |
  | `cap3c.exe` | `f242d32469ac01c20947be79cb3e4b1b7b4fc00cfac7c619e7212220c2c53f3e` | `78683aa4c501` | TAIL |
  | `scripthk.exe` | `9abdbc660312ea82095acfeb555de52e64d611d64107eb8e00b35c77c9638e94` | `dbc7f4329478` | SCRIPTH-A0P |
- **MAINABS measures 221fb28 (main + 0315), NOT main + CAP3/PACE.** The CAP3/PACE set lands later (its ratchet is
  running) and moves placement again; MAINABS's reading is of this binary's placement (`Run` set 11).
- **Order, cut strictly from the bottom:**
  1. `WARMUPO` (l308, MMD recipe), which also carries `FIXC.BAT` and `Y.TXT` to C:\DOSAGS (`--extra-file`).
  2. **FIXC** (operator decision ~23:28Z; coordinator additions a-d): after WARMUPO's collect, with the input lock
     held, `C:\DOSAGS\FIXC.BAT` is typed at the prompt. FIXC.BAT (CRLF, sha256
     `d9930d6c866e6b4fef47786d9540d7d78d33bf768d2e0d09c780c7742b4949d8`): `SMARTDRV /C` (the target's README rule
     before CHKDSK /F), load XMSDSK at L:, copy Y.TXT to L:, `CHKDSK C: /F < L:\Y.TXT > L:\CHKDSKF.TXT`, `SMARTDRV /C`,
     copy the report to C:\DOSAGS, `CHKDSK C: > C:\DOSAGS\CHKDSK2.TXT` (read-only), `DIR C:\FILE*.CHK >
     C:\DOSAGS\CHKLIST.TXT`, unload XMSDSK. Nothing writes to C: while /F repairs the FAT (a pipe would: DOS pipes
     are temp files). **Y.TXT is exactly "Y" CR LF, 3 bytes, sha256
     `b259bcb434250e59221023c52831a95998cc89345587a711578627e51ade37ec`.** The .CHK files are NOT deleted.
     - **At +60 s:** a camera shot and a capture frame, classified by `fixc_screen.py` (OCR; hw_guard's DOS-prompt
       rule plus CHKDSK's question). A DOS prompt -> no keystroke (FIXC is done). CHKDSK's question on screen, or
       any other screen -> one buffered "y"+Enter (the elapsed-time rule: FIXC.BAT redirects CHKDSK's output, its
       question included, to L:, so the screen cannot show it; a stray "y" is harmless to an answered CHKDSK and
       at the prompt). An unreadable screen -> no keystroke.
     - Then the screen is polled every 15 s for the DOS prompt, up to +900 s. **No prompt by then -> FIXC STALL:
       the driver stops with the target LEFT ON and the watchdog stopped (no power cut mid-repair); the operator
       decides.**
     - Then a read-only get-file of CHKDSKF.TXT, CHKDSK2.TXT, CHKLIST.TXT (saved in `FIXC-2026-09-25/`).
     - **If CHKDSK2.TXT is missing or still reports lost units or an error:** bulk C:-writing cells are skipped
       (none in round O), it is reported, and the rest continues.
     - **C:'s free-space layout changes at FIXC.** CF-write comparisons across rounds N and O (LOGRAM-style) are not
       like-for-like: round N ran on a FAT with 683 lost units in 19 chains, round O's scored cells on the repaired one.
  3. `MAINABS1`, `MAINABS2` (LAB-MMD 47): the MMD cell as rounds I-M with `--no-fine-timing` (need 1080).
  4. `WBLCP` then `WBLC2` (LAB-WB 38; need 1200 each; one wedge recovery each; RUNHW_MIN_WAIT_S 90): WBLC's exact
     fixture and env; WBLCP adds `DOSAGS_MIDI_TICK=poll`.
  5. `TAIL-0`, `TAIL-1` (cap3c, RUNHW_MIN_WAIT_S=300; need 1320).
  6. `SCRIPTH-A0P` (RUNHW_MIN_WAIT_S=270; need 600).
  PACEL -> round P (it needs the landed CAP3/PACE binary). D35HW closed (coordinator).
- **Tags:** WARMUPO, FIXC, MAINABS1/2, WBLCP, WBLC2, TAIL0/1, SCRIPTHA under the 8-char rule; all unused.
- **Arithmetic** (rounds L-N actuals; from relay-on; usable 5160 s): boot 75; WARMUPO ~580 -> ~0:11; FIXC ~120 +
  get-file ~80 -> ~0:14; MAINABS 2 x ~540 -> ~0:32; WBLCP (poll, WBF-like ~1100) -> ~0:51; WBLC2 (rtc, WBLC-like
  ~810) -> ~1:04; TAIL then has ~1315 s against its 1320: a coin-flip; SCRIPTH cut. Power-off ~1:05-1:26.
- **Driver checks:** `bash -n`; `fixc_screen.py` tested offline on synthetic DOS screens (waiting -> chkdsk-prompt,
  answered -> dos-prompt, bare prompt -> dos-prompt) and on real round N frames (never chkdsk-prompt); a
  hardware-free simulation (fake vcctrl, fake cell) of FIXC answered from the file (no key), still at the question
  at +60 s (one y+Enter), the read-only pass still reporting lost units (flagged, round continues), a stall (driver
  stops, target left on, no power-off), and a time cut; each cell's arguments and RUNHW_MIN_WAIT_S read back.

**2026-09-25 -- ROUND O RESULT (raw; SUMMARY lines copied verbatim).** Relay-on 00:13:30Z (2026-09-26 UTC), cap 01:43:30Z.
**Ended early by OPERATOR ORDER** ("power the system off once the Maniac Mansion runs are done and CHKDSK is complete",
relayed ~00:34Z): the driver (PID 3115487) got SIGTERM after it had launched MAINABS2 (the coordinator approved the PIDs
first; the watchdog subshell was checked to have no parent/trap logic and was left running); MAINABS2 finished and
collected normally; `build/ws/roundO/finishO.sh` (tested without hardware on four fetch paths) then wrote MAINABS2's
lines, fetched FIXC's reports read-only, powered off and stopped the watchdog. Power OFF 00:46:10Z (`on=False mW=0`),
re-read `on False mW 0` at 00:46:20Z. WBLCP, WBLC2, TAIL, SCRIPTH-A0P -> round P. daemon_start_t unchanged.
```
relay-on 00:13:30, cap 01:43:30
vcctrld daemon_start_t at round start: 1790349883.5326602
WARMUPO: run-hw exit=0 pre=425c1609f50a post=425c1609f50a staged_has_pre=1 binary_sha12=bc9c3704a839 build_dirty=0 tick_rate=30.20 tick_rate_steady=33.02  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 00:22:58
WARMUPO: stamp OK bc9c3704a839
FIXC +60s: screen=chkdsk-prompt -> fallback y+Enter sent (elapsed-time rule)
FIXC done 00:24:23: DOS prompt back
FIXC report: 
FIXC after (read-only): 
FIXC .CHK files: 0
FIXC: the read-only pass is missing or still reports lost units / an error -> bulk C:-writing cells skipped (none in round O); the rest continues
MAINABS1: run-hw exit=0 pre=952c914b9ce7 post=952c914b9ce7 staged_has_pre=1 binary_sha12=3cf8c4a48fe6 build_dirty=0 tick_rate=33.12 tick_rate_steady=36.49  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 00:36:29
MAINABS1: stamp OK 3cf8c4a48fe6
MAINABS2: run-hw exit=0 pre=952c914b9ce7 post=952c914b9ce7 staged_has_pre=1 binary_sha12=3cf8c4a48fe6 build_dirty=0 tick_rate=32.97 tick_rate_steady=36.29  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 00:44:32
MAINABS2: stamp OK 3cf8c4a48fe6
round O stopped after MAINABS2 by operator order (driver SIGTERM after it launched MAINABS2): WBLCP, WBLC2, TAIL, SCRIPTH-A0P -> round P
FIXC fetch done 00:46:05: collected [CHKDSKF.TXT CHKDSK2.TXT CHKLIST.TXT] (job status saved: fetch2/file-status.json)
FIXC CHKDSKF.TXT:    683 lost allocation units found in 19 chains.        61,478 total allocation units on disk        13,308 available allocation units on disk 
FIXC CHKDSK2.TXT:        61,478 total allocation units on disk        13,306 available allocation units on disk 
FIXC CHKLIST.TXT: FILE0000 CHK        32,768 09-25-94   5:22p FILE0001 CHK        32,768 09-25-94   5:22p FILE0002 CHK        32,768 09-25-94   5:22p FILE0003 CHK        32,768 09-25-94   5:22p FILE0004 CHK        32,768 09-25-94   5:22p FILE0005 CHK        
vcctrld daemon_start_t at round end: 1790349883.5326602
power OFF 00:46:10: on=False mW=0
watchdog 3115734 stopped 00:46:10
```
- **The FIXC lines above written by the driver at 00:24-00:28Z are ARTEFACTS:** its pull delivered none of the three files
  (the job ran +19..+220 s and returned with nothing; its status record was overwritten by MAINABS1's send, so the reason
  is unknown), and the driver read the missing files as "still reports lost units" and ".CHK files: 0". **At that point
  the outcome was unknown (async get-file).** The later fetch (finishO.sh, 00:44:32-00:46:05Z; the pull seen running,
  then finished, job ok, all 3 files ok, status JSON in `FIXC-2026-09-25/fetch2/file-status.json`) collected them:
  - **CHKDSKF.TXT** (the /F run; sha256 d808e4f9...): "683 lost allocation units found in 19 chains", "22,380,544 bytes
    in 19 recovered files", 13,308 available allocation units.
  - **CHKDSK2.TXT** (read-only, after; sha256 df9c7cbc...): **no lost units, no errors**; 6,510 user files (6,489 + 19).
  - **CHKLIST.TXT** (sha256 eb464c3a...): FILE0000-FILE0018.CHK in C:\, 19 files, 22,380,544 bytes, **kept for the
    operator's review** (dated 09-25-94: the target's clock reads 1994).
  - **The repair worked.** Free space did not grow (the chains became files, as "Y" does). **C:'s free-space layout
    changed at FIXC (00:23-00:24Z):** CF-write comparisons across rounds N and O are not like-for-like.
- **Rule MISS (FIXC's keystroke rule, coordinator addition b): one "y"+Enter was sent at a DOS prompt.** CHKDSK 6.22
  prints its question to the console even with its output redirected, and took "Y" from L:\Y.TXT itself; by +60 s
  FIXC.BAT had finished ("FIXC DONE", then `C:\>`). `fixc_screen.py` checked the last 3 lines for the question BEFORE
  checking the last line for a prompt, so it returned chkdsk-prompt. Effect: `C:\>y` / "Bad command or file name" /
  `C:\>`, after everything had finished; nothing reached CHKDSK or the disk (`FIXC-2026-09-25/shot-060.jpg`,
  `shot-poll.jpg`). Fixed after the round: the prompt on the last line wins; the question counts only as the last line.
- **MAINABS1/2** (lab-mmd scores them, mainabs.py): 3cf8c4a48fe6 (landed 221fb28 = main + 0315, `Run` set 11; NOT main +
  CAP3/PACE); the saved RUN.BATs carry no DOSAGS_TICKSTATS_FINE line (`--no-fine-timing`), WARMUPO's carries
  `SET DOSAGS_TICKSTATS_FINE=1` (the harness default).
- **End-of-round ENOSPC check (WARMUPO, MAINABS1, MAINABS2):** no ENOSPC text; one continuous audio segment, no drop.
- **Camera witness (3 camera + 3 card sheets; none short): CLEAN.** Boot, the MMD character select, the post-exit prompt;
  MAINABS1 filmed under room lighting.
- **Audio:** local only; `AUDIO-SHA256.txt` per dir.

**2026-09-26 -- ROUND P. Staging record, before any power-on.** Round P needs its own operator approval (the coordinator asks
once this is committed); the power-on waits for GO. Driver `build/ws/roundP/driveP.sh` (refuses without `ORDER-CONFIRMED`);
round L's `cellL.sh` + `snapshots.py`; run-hw.sh at b009a3d (fine timing ON by default; `--no-fine-timing` for MAINABS-P).
Staged on main 389a37a (b009a3d touched only gate-alias.sh, which no round cell uses).
- **Binaries** (`build/ws/roundP/expected.txt`; stamps checked per cell):
  | file | sha256 | stamp | cells |
  |---|---|---|---|
  | `l308.exe` | `425c1609f50ac62cb712109f383e1fff99955d77830f93943dc3d491d849607f` | `bc9c3704a839` | WARMUPP |
  | `mainp.exe` | `9221e3e87ffcb3f74a99d8dbfe22ac198b9544d39eefcf39e87193df5429f3ae` | `a30ee9702c2a` | MABSP1/2, PACEL (landed main 389a37a) |
  | `land1.exe` | `07b604f8cc6a4d22433dd19b578273e87b3f97fa0379191bc5e87dbd78c61eed` | `e93cb957c3be` | WBLCP, WBLC2 |
  | `cap3c.exe` | `f242d32469ac01c20947be79cb3e4b1b7b4fc00cfac7c619e7212220c2c53f3e` | `78683aa4c501` | TAIL-0/1 |
  | `scripthk.exe` | `9abdbc660312ea82095acfeb555de52e64d611d64107eb8e00b35c77c9638e94` | `dbc7f4329478` | SCRIPTH-A0P |
  **If 0316 lands before the power-on:** mainp.exe is restaged from the new main, MAINABS-P and PACEL re-verified, and
  this record amended with the new stamp; otherwise it runs as staged.
- **Order, cut strictly from the bottom:**
  1. `WARMUPP` (l308, MMD recipe).
  2. MAINABS-P (LAB-MMD 49.1): **tags `MABSP1`, `MABSP2`** -- 49.1's MAINABSP1/2 both truncate to MAINABSP under the
     engine's 8-char manifest rule; `mainabs.py` takes cell dirs, so it runs unchanged:
     `lab-mmd/mainabs.py a30ee9702c2a MABSP1-<date> MABSP2-<date>`. The MMD cell with `--no-fine-timing` (need 1080).
  3. `PACEL` (LAB-JOURNEYS 8.43 + A1 + note 223728e; `pace-score.py hw --binary a30ee9702c2a --on PACEL-<date>`):
     **PACE-H-ON's exact fixture and env** as saved in its RUN.BAT: C3-512 (room 35, ACSETUP-ON-512X384-ROUND,
     auto-exit 5000, walker), `SDL_HINT_DOS_MIDI_DEFER_DRAIN_STI=0`, no pacing/budget hints, RUNHW_MIN_WAIT_S=270
     (need 585). **Flagged:** 8.43's text says both "PACE-H-ON's exact fixture and env" and "the default drain";
     PACE-H-ON ran DRAIN_STI=0, so the exact env is staged. The harness default `DOSAGS_TICKSTATS_FINE=1` matches
     PACE-H-ON's pre-0315 binary, whose fine timers were always on.
  4. P3 ABBA (LAB-MMD 49.2): **not staged** -- its rebased binary and lab re-gates were not done by staging.
  5. `WBLCP` then `WBLC2` (LAB-WB 38; need 1200 each; one wedge recovery each; RUNHW_MIN_WAIT_S 90), as round O staged.
  6. `TAIL-0`, `TAIL-1` (RUNHW_MIN_WAIT_S=300; need 1320). 7. `SCRIPTH-A0P` (RUNHW_MIN_WAIT_S=270; need 600).
- **Get-file:** the only one is WB's wedge_fetch. It now waits until its pull is SEEN running, then finished (600 s
  cap), saves the job's status JSON, and logs missing files as "not collected" (the round O fix). No FIXC this round.
- **Tags:** WARMUPP, MABSP1, MABSP2, PACEL, WBLCP, WBLC2, TAIL0/1, SCRIPTHA; all unused.
- **Arithmetic** (rounds L-O actuals; from relay-on; usable 5160 s): boot 75; WARMUPP ~580 -> ~0:11; MAINABS-P
  2 x ~500 -> ~0:28; PACEL ~585 -> ~0:38; WBLCP (poll, WBF-like ~1100) -> ~0:56; WBLC2 (rtc, ~810) -> ~1:10; TAIL
  then has ~930 s < 1320 -> cut, with SCRIPTH. Power-off ~1:10.
- **Driver checks:** `bash -n`; a hardware-free simulation (fake vcctrl and cell) of the full path, a WBLCP wedge
  (one recovery; the pull seen running then finished; files saved; the round continues), and a cut below
  MAINABS-P's need (it and every later block dropped); each cell's arguments and RUNHW_MIN_WAIT_S read back.

**2026-09-26 -- ROUND P RESULT (raw; SUMMARY lines copied verbatim).** Relay-on 02:49:01Z, cap 04:19:01Z; power OFF
03:54:46Z (`on=False mW=0`), re-read `on False mW 0` at 03:54:53Z, and powerguard.sh confirmed OFF at 03:54:55Z (the
coordinator verified 0 mW independently). Every cell: run-hw exit 0, recover 0, sha256 pre = post = staged, stamp OK,
fw=OK, xcheck ok, INPUT-LOG pair, RUN.BAT saved. TAIL (1221 s left < 1320) and SCRIPTH-A0P cut -> round Q.
```
relay-on 02:49:01, cap 04:19:01
vcctrld daemon_start_t at round start: 1790349883.5326602
WARMUPP: run-hw exit=0 pre=425c1609f50a post=425c1609f50a staged_has_pre=1 binary_sha12=bc9c3704a839 build_dirty=0 tick_rate=30.17 tick_rate_steady=32.99  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 02:59:58
WARMUPP: stamp OK bc9c3704a839
MABSP1: run-hw exit=0 pre=9221e3e87ffc post=9221e3e87ffc staged_has_pre=1 binary_sha12=a30ee9702c2a build_dirty=0 tick_rate=33.07 tick_rate_steady=36.48  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 03:08:56
MABSP1: stamp OK a30ee9702c2a
MABSP2: run-hw exit=0 pre=9221e3e87ffc post=9221e3e87ffc staged_has_pre=1 binary_sha12=a30ee9702c2a build_dirty=0 tick_rate=33.06 tick_rate_steady=36.47  recover=0 inputlog=ok:6 fw=OK xcheck=ok rooms=Now in room 50, 03:16:52
MABSP2: stamp OK a30ee9702c2a
PACEL: run-hw exit=0 pre=9221e3e87ffc post=9221e3e87ffc staged_has_pre=1 binary_sha12=a30ee9702c2a build_dirty=0 tick_rate=31.59 tick_rate_steady=40.26  recover=0 inputlog=ok:241 fw=OK xcheck=ok rooms=Now in room 35, 03:26:33
PACEL: stamp OK a30ee9702c2a
WBLCP: run-hw exit=0 pre=07b604f8cc6a post=07b604f8cc6a staged_has_pre=1 binary_sha12=e93cb957c3be build_dirty=0 tick_rate=32.79 tick_rate_steady=33.67  recover=0 inputlog=ok:27 fw=OK xcheck=ok rooms=Now in room 1,Now in room 2,Now in room 3,Now in room 99, 03:41:01
WBLCP: stamp OK e93cb957c3be
WBLC2: run-hw exit=0 pre=07b604f8cc6a post=07b604f8cc6a staged_has_pre=1 binary_sha12=e93cb957c3be build_dirty=0 tick_rate=33.00 tick_rate_steady=33.91  recover=0 inputlog=ok:27 fw=OK xcheck=ok rooms=Now in room 1,Now in room 2,Now in room 3,Now in room 99, 03:54:40
WBLC2: stamp OK e93cb957c3be
TAIL dropped as a block: 1221s left < 1320s (03:54:40) -> round Q
SCRIPTH-A0P dropped: an earlier block was cut (03:54:40) -> round Q
vcctrld daemon_start_t at round end: 1790390964.157187
power OFF 03:54:46: on=False mW=0
```
- **vcctrld restarted once, before any cell** (the d5aeb64 deploy; operator-approved in the vcctrl session; Pi journal
  via the coordinator): down 02:49:23.72-02:49:25.80Z (~2.1 s), 22 s after relay-on, while the driver was in its 75 s
  boot sleep (no lock, job or capture of the round's in flight); the Pi-hosted MCP down 02:49:28.5-02:50:59.8Z (the
  round uses the CLI only). **daemon_start_t therefore changed from 1790349883.53 (round start) to 1790390964.157
  (02:49:24.157Z) at round end: EXPECTED, this restart, not an anomaly.** No daemon-side watchdog or timer was set by
  the round (power-on is a plain `vcctrl power on`; the cap watchdog is host-side; the daemon's power config has no
  watchdog). Lost frames: only boot frames before 02:49:25.8Z; WARMUPP's witness starts at 02:55:06Z, complete. The
  safeguards armed on the coordinator's alert: `daemongap.sh` (no further gaps) and `powerguard.sh` (confirmed OFF),
  both host-side, both exited on their own after the power-off. Full log: `WARMUPP-2026-09-25/DAEMON-GAPS.txt`,
  `POWERGUARD.txt`.
- **MABSP1/2** (LAB-MMD 49.1 MAINABS-P; tags shortened from MAINABSP1/2, which collide under the 8-char rule): landed
  main 389a37a = a30ee9702c2a, `--no-fine-timing` (no FINE line in their RUN.BATs). Scoring is lab-mmd's:
  `lab-mmd/mainabs.py a30ee9702c2a MABSP1-2026-09-25 MABSP2-2026-09-25`.
- **PACEL** (8.43 + A1 + 223728e, with 8.43's clarification 0668ebf: DRAIN_STI=0): `pace=128/2570 pwait=80/32853/436
  peak=144/0 isr_max_us=7820`, pgdetect 1, budget 448, midi_tick isr, late 0, cap_hits 0, underruns 0, overwrites 0,
  `uclockwrap first=1 wrapped=5269379`; collected at 277 s (after the real exit). Scoring is lab-journeys': the
  coordinator relays a HEALTH-row FAIL (8.49), whose registered consequence is SDL 0256 (pace default off).
- **WBLCP** (`midi_tick=poll`, valid) and **WBLC2** (lab-wb scores both, LAB-WB 38).
- **Result dirs** carry `2026-09-25` (the drivers' fixed CELL_DATE since round L), although round P ran on 2026-09-26 UTC.
- **End-of-round ENOSPC check (all 6 cells):** no ENOSPC text; one continuous audio segment, no drop.
- **Camera witness (6 camera + 6 card sheets; none short): CLEAN.** WARMUPP, MABSP1, MABSP2: boot, the MMD select, the
  prompt (MABSP2 room light from frame 8). PACEL (30 frames): boot, room 35's intro and play, the prompt after the real
  exit; card `frozen` at 512x384 (the known trap), camera the witness. WBLCP, WBLC2 (31 frames each): the 5 Days intro,
  title, office room to the end; one ~133 s sampler gap each, identical on card and camera (after 20:34:16 and
  20:47:54 local); WBLCP's room light changes mid-sheet. No wedge, no recovery.
- **vcctrl job history (d5aeb64, saved to `build/ws/roundP/jobs/`: `--history` + each `--job ID`; 14 jobs, 6 sends
  all ok, 8 pulls):**
  1. **Every pull `partial`, all missing files `not-listed`: expected, optional outputs.** run-hw.sh asks for them
     speculatively (its fetch list, run-hw.sh:950-968): `<TAG[0:5]>SDL.LOG` exists only with DOS_PORT_LOG=1 (never set);
     `AUTOPLT.LOG` and `PH01-03.BMP` only for AutoPilot fixtures (none this round); `WARNINGS.LOG` only when a script
     warning is emitted ("its absence is the good case"). The required files arrived for all 6 cells: STDOUT.TXT (each
     ending ENGINE HAS SHUTDOWN), `<TAG>.LOG` (the manifest; RUNMANI.LOG in each dir) and AGSSAVE.001.
  2. **The two `no-reset` pulls (03:34:17Z, 03:47:56Z) were WBLCP's and WBLC2's FIRST collect attempts, made while the
     game was still running:** run-hw's still-screen rule read 5 Days' static office room as finished (MIN_WAIT 90 +
     60 s still) and proceeded at t+233/234 s; the reboot chord cannot land on a running SDL3-DOS game (its keyboard
     handler), so the job stopped at `no-reset`; run-hw's own retry ("not ready yet ... retrying collection in 60s")
     collected after the game's real exit (03:37:30Z, 03:51:09Z). Both games ran to their auto-exit (ticks 16052 /
     16064, ENGINE HAS SHUTDOWN), so no data was lost -- but it is the same early-collect pattern as round M's CAP3d-D2,
     now on the WB fixture. For round Q: RUNHW_MIN_WAIT_S covering the WB cells' 16000-tick auto-exit (~470 s + boot).
  3. **Caps Lock LED on while typing (pull-20260926T035109.176Z, 03:53:54Z), not acted on by vcctrl.** WBLC2's three
     collected files are complete and uncorrupted: STDOUT.TXT, WBLC2.LOG and AGSSAVE.001 match the job's sha256 and
     byte counts exactly (2f0c2070fc30 / 126651 B, 1fd37dc9bd36 / 138451 B, e49d7349568d / 8130 B). DOS file names and
     commands are case-insensitive, so inverted case changes nothing on the target side; nothing else was typed after
     that pull (the driver went straight to the power-off).
- **Audio:** local only; `AUDIO-SHA256.txt` per dir.

**2026-09-26 -- ROUND Q RESULT (PLAN-GATES procedure; rows in STATUS.md "Gate cells, sound ON").** Relay-on 06:59:04Z,
power OFF 08:00:07Z (guard-confirmed 0 mW 08:00:14Z); 6 cells, run-hw exit 0, stamps OK, camera CLEAN, no daemon gap.
- **S16 (x2, main 75543c93, fine off): NOT MET as registered.** Whole-run 39.18 / 39.13 (floor 39.2), steady 40.08 /
  40.09, fps_p50 40.00, audio clean; the same 3 stall ticks (1546 ms) in both. Prediction falsified on whole-run.
  Next: lab-s8 names the stalls with 0316 on DOSBox-X before any re-run (no re-run until a lab fix + 486 prediction).
- **WBLR** (land3): midi_tick rtc, c_redrain 84, late 0; lab-wb scores D 0.697 against 0.70 -- not a landing run.
- **PLAYQ1/Q2: VOID** as registered (both walked into room 2, loops 6937 / 6859); TICKS.BIN complete for lab-mmd.
- Raw: `tests/harness/results/{WARMUPQ,S16Q1,S16Q2,WBLR,PLAYQ1,PLAYQ2}-2026-09-26/`. Audio local only.

**2026-09-26 -- ROUND R RESULT (PLAN-GATES procedure; rows in STATUS.md).** Relay-on 14:36:22Z, power OFF 15:51:26Z by
the driver's own poweroff (0 mW; coordinator-verified 15:51:36Z); 7 cells, run-hw exit 0, stamps OK, camera CLEAN, no
daemon restart. powerguard/daemongap did NOT run: the auto-mode classifier denied the post-launch command (Auto-Mode Bypass).
- **S8 (x2, main 5ca997b3, fine off): NOT MET as registered.** Whole-run 38.76 / 38.76, steady 40.24 / 40.27, fps_p50
  40.00; prediction held. silent_irqs 6 / 4 outside room loads (the one >743 ms gap per cell, t~51-52 s): audio not met.
- **S32 (x2): baseline only** (operator ruling): 16.62 / 16.58 whole-run, 40.74 steady; no audio played (pcm_irqs 0).
- **WBLRP / WBLR2** (land4): lab-wb VALID (D 0.667) / PASS (D 0.702, B PASS); **no WB landing** -- LAB-WB 38 governs.
- Raw: `tests/harness/results/{WARMUPR,S8R1,S8R2,S32R1,S32R2,WBLRP,WBLR2}-2026-09-26/`. Audio and AGSSAVE.001 local only.

**2026-09-26 -- ROUND S RESULT (PLAN-GATES procedure; rows in STATUS.md).** Relay-on 21:06:38Z, power OFF 22:04:27Z by the
driver's own poweroff (powerguard confirmed 0 mW 22:04:30Z; coordinator-verified); 6 cells, run-hw exit 0, stamps OK, camera
CLEAN, no daemon restart. First round whose driver starts its own guards (one permission rule, no follow-up command).
- **PACEI (LAB-JOURNEYS 8.50), main 0cb807ee: VERDICT PACEI CLEARED** (pacei-score.py 179af48c): A [2, 3] = B [2, 3], all
  silent IRQs FP_AMB, health OK; per 8.50/8.51 lab-journeys' restore-default patch follows, then lab/journeys retires.
- **PROF16** (lab-s8, AGSPRF16 9ae27591b0c8): **P1: FALSIFIED as registered**, **P2: HELD** (PATH 20.7%); lab-s8's reading:
  S16Q's 505 ms stall ~ 200 ms pathfinder + ~300 ms that needs sound (first play of sound 9, a 0216 cache miss).
- Camera: all 6 CLEAN; PACEIA2 frames #3, #9-19 carry a whole-image green cast incl. the bezel (camera white balance).
- Raw: `tests/harness/results/{WARMUPS,PACEIA1,PACEIB1,PACEIB2,PACEIA2,PROF16}-2026-09-26/`. Audio and AGSSAVE.001 local only.

**2026-09-27 -- ROUND T RESULT (rows in STATUS.md).** Relay-on 04:36:17Z, target OFF 05:32:10Z (powerguard 0 mW 05:32:19Z); 6 cells,
exit 0, stamps OK. **Witness PARTIAL:** camera framing cut the top of the screen in all 6 cells; the VGA capture froze at the DOS
boot text (stick absent, device_present=false, last frame ~22:15Z); what's visible is clean -- no gate PASS can rest on round T.
- **S32P-HW (0239 ABBA):** "VERDICT: VOID [] spreads 0.06/0.10". Note 2026-09-27: the rule says "exceeds 0.10"; the decimal B-B
  spread is exactly 0.10 (the VOID is float 0.10000000000000142). Both readings NO FLIP (B1 39.11 < 39.2): 0239 stays OFF.
- **Gate S32P NOT MET:** whole-run 39.21/39.11/39.21/39.15, steady 39.95-40.05, fps_p50 40; silent IRQs in play on B1/B2/A2.
- **AUDH16:** P1 FALSIFIED, P2 FALSIFIED (read clause), P3 HELD; asset_open is a fixed ~55 ms per 486 first play (lab-s8).
- Raw: `tests/harness/results/{WARMUPT,S32PA1,S32PB1,S32PB2,S32PA2,AUDH16}-2026-09-27/`. Audio and AGSSAVE.001 local only.

**2026-09-28 -- ROUND U RESULT (rows in STATUS.md).** Relay-on 17:33:28Z, target OFF 18:40:48Z (powerguard 0 mW 18:40:50Z); 7 cells,
exit 0, stamps OK. Re-dated before any data (285d9272). Camera CLEAN in all cells, whole screen in frame; capture stick unreliable
by operator decision camera-only: capture=STALE on IOA0/IOES, intermittent (capture=ok) from IO41 on. Target CONFIG.SYS (read by
WARMUPU): FILES=30, BUFFERS=20, DOS=HIGH,UMB, LASTDRIVE=M.
- **S16-IOARMS-HW** (lab-io-hw.py, --sha 80463ed30b91): "ES gate: PASS (compared=25 mismatches=0)"; "drift OFF-OFF 0.2 ms";
  "0241 saving 33.9 ms (pred 25-45): HOLDS"; "0242 further saving 8.2 ms (pred 15-25): HOLDS" (clears the < 5 ms falsifier, below
  the predicted range); IO22 mean 13.0 ms, reported only. asset_open: OFF 55.2/55.0 -> 0241 21.2 -> 0241+0242 13.0 ms per first play.
- Raw: `tests/harness/results/{WARMUPU,IOA0,IOES,IO41,IO42,IO22,IOA1}-2026-09-28/`. Audio and AGSSAVE.001 local only.

**2026-09-28 -- ROUND V RESULT (rows in STATUS.md).** Relay-on 20:38:16Z (coordinator launch), target OFF 21:45:16Z (powerguard 0 mW
21:45:19Z); 7 cells exit 0, stamp d18d63368af6 (main 5bec55aa: 0241/0242 ON). Camera CLEAN in all cells. Capture: stick absent at the
pre-flight, USB-cycled by vcctrl 20:38:47-53Z, present since (device #94); INC cells capture=STALE = 512x384 lock loss; FF cells ok.
- **0320 ABBA** (abba320.py d3dc8239): deltas -274 / -283 ms, drift 9 ms, prediction HELD, B counters 0; "VERDICT: NOT SEPARABLE"
  -- B silent IRQs 1 (INCB1, in play, tick 972) vs A 0. Only FLIP ON flips 0320, so its default stays OFF.
- **0240 pair** (lab-s32p-ff-hw.py; 02a57e4d and 5786b508 identical): fade 2274 -> 981 ms (0.43x), whole-run +0.40; "VERDICT: VOID
  (fast fade over 0.9 s but under 0.6x -- stated, not a pass)". 0240's default is unchanged (ON as landed); any ruling is the coordinator's.
- Raw: `tests/harness/results/{WARMUPV,INCA1,INCB1,INCB2,INCA2,S32FF0,S32FF1}-2026-09-28/`. Audio and AGSSAVE.001 local only.

**2026-09-28 -- ROUND W RESULT (rows in STATUS.md).** Relay-on 22:54:42Z (coordinator launch), target OFF 23:43:33Z (powerguard 0 mW
23:43:35Z, coordinator-verified); 5 cells exit 0, ADP cells stamp ef123dba0adf (main d533b56d); no daemon gap. Camera CLEAN in all
cells. Capture: SUMMARY capture=ok everywhere, but that is a false negative -- in play the card read "frozen" (flat grey frames, stddev 0)
in every ADP cell; card.frozen stayed false because locked samples (boot + post-exit) outnumbered frozen ones. The camera is the witness.
- **0322 safety ABBA** (lab/mmd 017050ef; abba322.py c19cb451): silent IRQs B 5 (ADPB1 2, ADPB2 3) vs A 2 (1 + 1), none of B's in a room
  load, B counters 0, drift 0.08; "VERDICT: KEEP OFF". 0322 (DOSAGS_PCM_ADOPT) stays default OFF. Reported: stall100 B-A -71 / -81 ms,
  sound10-tick B-A -70.3 / -7.6 ms; gate bar DOES NOT MEET in all four (in-play silent IRQs, A cells included).
- RP486 "not run: not staged" (as intended; W2 carries it). Raw: `tests/harness/results/{WARMUPW,ADPA1,ADPB1,ADPB2,ADPA2}-2026-09-28/`.
  Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND W2 RESULT (rows in STATUS.md).** Relay-on 00:44:21Z (coordinator launch), target OFF 01:25:00Z (powerguard 0 mW
01:25:04Z, coordinator-verified); 5 cells exit 0, RPF cells stamp 55959f2577ca (lab-s8's AGSRPW = main d533b56d + ags 0319 + RT3
route-hash probe, build_dirty 1 as registered); no daemon gap. Camera CLEAN in all cells. Capture: SUMMARY capture=ok, but the same
false negative as round W -- 512x384, in-play frames flat grey; longest non-locked runs 16-26 (STALE(nolock) under the approved rule).
- **RP486, ags 0319 killswitch ABBA** (lab/mmd 0b5aaeea; rp486.py bdd54dc8): routes IDENTICAL (339 rows x 4); mean request F1 40.32 /
  40.25 ms vs F0 57.65 / 57.67 ms = saving 30.1% / 30.2%; "VERDICT: LANDING GATES". **Disclosed:** the registered prediction's "the
  worst request falls too" did NOT hold -- worst request F1 244.5 / 244.6 ms vs F0 173.0 / 172.9 ms (+41%, both pairs). The kill rule
  gates on identity + mean only; the coordinator sent the worst-request rise to lab-s8 -- no 0319 landing work until it reports.
- Raw: `tests/harness/results/{WARMUPW2,RPF1A,RPF0A,RPF0B,RPF1B}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND X DATA (no verdict; the 0320 confirmation verdict is pooled after round X2).** Relay-on 01:25:17Z (coordinator
launch), target OFF 02:13:13Z (powerguard 0 mW 02:13:19Z, coordinator-verified); 5 cells exit 0, INC cells stamp d18d63368af6 (round V's
binary, main 5bec55aa); no daemon gap. Camera CLEAN in all cells (Trilby room 35 night scene, as round V). Capture: WARMUPX ok, INC
cells capture=STALE (512x384 nolock: locked/frozen samples only). Block 2 of 3 (INCA3 INCB3 INCB4 INCA4); abba320c.py (7f0c43c9) runs
only once X2's block 3 is in -- no per-block numbers are printed before then. Raw: `tests/harness/results/{WARMUPX,INCA3,INCB3,INCB4,
INCA4}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND X2 RESULT + 0320 POOLED CONFIRMATION (rows in STATUS.md, X and X2).** Relay-on 02:13:40Z (coordinator launch),
target OFF 03:01:31Z (powerguard 0 mW 03:01:33Z, coordinator-verified); 5 cells exit 0, INC cells stamp d18d63368af6; no daemon gap.
Camera CLEAN in all cells; WARMUPX2 capture ok, INC cells capture=STALE (512x384 nolock).
- **0320 pooled** (lab/mmd cee07b0f + f227b8b6 + 7f0c43c9; abba320c.py 7f0c43c9 over V + X + X2, 6 A vs 6 B): pair deltas -274/-283,
  -280/-281, -279/-282 ms, drifts 9/1/2 ms; in-play silent-IRQ cells B 2/6 vs A 0/6, Fisher p = 0.227; B counters 0, none in a room
  load; **SLICE-ONLY B silent IRQ INCB3 tick 903** -> amendment (iii) -> "VERDICT: KEEP OFF". 0320 (DOSAGS_PCM_INCR) stays
  default OFF. A reading, not a rule: tick 903 falls after "sound 11", the same spot as round V's INCB1 tick 972 (which stays
  AMBIGUOUS as classified at f227b8b6); the verdict rests on amendment (iii) alone, not on this observation.
- Raw: `tests/harness/results/{WARMUPX2,INCA5,INCB5,INCB6,INCA6}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND Y RESULT (rows in STATUS.md).** Relay-on 03:01:50Z (coordinator launch), target OFF 04:08:59Z (powerguard 0 mW
04:09:02Z, coordinator-verified); 7 cells exit 0; no daemon gap. Camera CLEAN in all cells. Capture: SUMMARY capture=ok, the round W
false negative again (512x384; longest non-locked runs 55-57, STALE(nolock) under the approved rule).
- **Driver regex error (disclosed):** SUMMARY prints "STAMP-VOID manifest , want labUSY0" for all six IO cells. driveY.sh's two
  extraction greps ('binary_sha12=[0-9a-f]*') were left hex-only when its stamp check was relaxed for the label, so they read the
  label as empty. Identity held: every RUNMANI reads binary_sha12=labUSY0; PRE-STAGE = POST-RUN = 3d4f1c1d54fe...; STAGED-SHA256 has
  it; roundY/usy.exe sha256 -c OK after collection; the scorer's registered --sha labUSY0 check passed all six. SUMMARY.txt not edited.
- **IO arms** (lab/metric 167e2a91; lab-io2-hw.py ee0de7b0): IODS gate PASS (21 compared, 0 mismatches), drift 0.16 ms.
  **0245** asset_open saving 12.42 ms (pred 9-13): HOLDS, but "audio not clean" (IODC 2 silent IRQs vs OFF max 1) -> no default flip
  proposed from it. **0246** summed read saving 9.95 ms vs midpoint 20.13 ms: HOLDS (above the 25% bar), audio clean; per clip below
  the predicted bands. IOBB (reported): open 1.66 vs 14.07 ms, audio not clean (3).
- Readings, not rules: "room3 fade t_ms" is ~+245-265 ms in every DIRCACHE=1 cell (886/865/866 vs 626/623/623), which camera frame #3
  shows too; clip sets differ across cells (IOB1 n=3, no sound9/10). IOB1's timeout was capped to 1715 s by the cap; it exited 0.
- Raw: `tests/harness/results/{WARMUPY,IOB0,IODS,IODC,IORD,IOBB,IOB1}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND Z RESULT (rows in STATUS.md); the operator's five-round sequence W2 X X2 Y Z is complete.** Relay-on 04:09:16Z
(coordinator launch), target OFF 05:02:02Z (powerguard 0 mW 05:02:09Z, coordinator-verified); 5 cells exit 0, WBD cells stamp
ef123dba0adf (main d533b56d = round W's mainw.exe); no daemon gap. Camera CLEAN in all cells (WBD8R's camera framing wider than WBD8P's;
whole screen in frame). Capture at 640x480 LOCKED in play (longest non-locked runs 3-4; WBD8R's capture sheet shows the room 35 content).
- **WB depth** (lab/wb 4a4585d0 + c080538f; depth-score.py at c080538f): **WBD8R VERDICT: FAIL** -- A PASS, B PASS (chroma 0.957), D
  0.288 (bar 0.70; poll control 0.280); **WBD32R VERDICT: FAIL** -- A PASS, B PASS (0.905), D 0.630 (control 0.727). Registered rule for
  D < 0.70 with the rest passing: one re-run (operator rule), the operator's call.
- Readings, not rules: S8's D fails for both arms alike (0.288 / 0.280, phase corr 0.08 / 0.12) while B's chroma is 0.957 -- more like
  the D alignment failing on this capture than the pump; WBD8R's clk ratio 0.9672 is near A5's 0.95 floor; S32P pump D 0.630 is below
  its predicted 0.68-0.76 while the poll control's 0.727 is above its own.
- Raw: `tests/harness/results/{WARMUPZ,WBD8P,WBD8R,WBD32P,WBD32R}-2026-09-29/`. Captures (game music) and AGSSAVE.001 local only.

**2026-09-29 -- ROUND Z2 RESULT (rows in STATUS.md).** Relay-on 05:12:23Z (coordinator launch, operator: "Run Z2 now, Z3 after"),
target OFF 05:53:41Z (powerguard 0 mW 05:53:45Z, coordinator-verified); 5 cells exit 0, RRF cells stamp 514d0a6cb094 (lab-s8's AGSRPW2 =
main d533b56d + 0319 re-cut 2 + RT3 probe, dirty 1); no daemon gap. Camera CLEAN in all cells. Capture: first round on the new rule
(05e7b4c2, landed 05:05:32Z, before relay-on) -- all five STALE(nolock), runs 19-25 at 512x384; the camera is the witness.
- **0319 re-cut 2** (lab/mmd 54f4ff73; rp486b.py 240dd83f): routes IDENTICAL; mean request F1 40.43 / 40.46 vs F0 57.27 / 57.27 ms =
  saving 29.4% / 29.3%; worst request F1 173.0 / 172.8 vs F0 171.8 / 171.9 ms (-0.7% / -0.5%); "VERDICT: LANDING GATES". Reported:
  P-row0 MISSED (F1 row 0 ~1 ms above F0's), P-label MISSED (label_us 10,482 / 10,345 vs 10,000), P-mean HELD.
- Reading, not a rule: re-cut 2 removed W2's worst-request rise (F1 244.5 -> 173.0 ms); F1's worst is now its row 0, within ~1 ms of F0.
- Raw: `tests/harness/results/{WARMUPZ2,RRF1A,RRF0A,RRF0B,RRF1B}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND Z3 RESULT, MEASUREMENT ONLY (rows in STATUS.md).** Relay-on 05:53:59Z (coordinator launch, operator: "Run Z2
now, Z3 after"), target OFF 07:01:30Z (powerguard 0 mW 07:01:32Z, coordinator-verified); 7 cells exit 0, Z3 cells stamp 2f73bacd1f95
(lab-s8's AGSLAC4, dirty 1); no daemon gap. Camera CLEAN in all cells; capture STALE(nolock) at 512x384 (the camera is the witness).
Z3A2's timeout was capped to 1692 s by the cap; it exited 0. No hardware is left in the plan; the target stays OFF.
- **Z3** (lab/mmd 15fca729 + b77e6948; z3.py 912453a5; all six cells "ok"): per-arm medians A (INCR=0) M1 901 ms, sound11 margin 170.1 /
  max gap 76.8, sound18 margin 176.0 / 745.8, silent IRQs 1 (EOD SLICE); B (INCR=1) M1 575, 160.9 / 71.9, 122.2 / 369.3, 0; C (INCR=1 +
  LOOKAHEAD=2) M1 562, 160.2 / 66.6, 146.4 / 369.4, 0; instrument cost 10.55-11.15 us per record. "MEASUREMENT ONLY -- no verdict, no
  flip (the cap stays FAILED as registered; 0320 stays OFF)". Any later cap candidacy needs a new registration citing these numbers.
- Raw: `tests/harness/results/{WARMUPZ3,Z3A1,Z3B1,Z3C1,Z3C2,Z3B2,Z3A2}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND GATE RESULT: gate re-reading x2 per depth on main b7ac6c46 (rows in STATUS.md).** Operator released the hardware
("System may be used now"; "All five in sequence"). Relay-on 13:46:00Z, target OFF 14:52:43Z (powerguard 0 mW 14:52:44Z,
coordinator-verified); 7 cells exit 0, stamp 3074cd9ce099 (0241/0242/0246/0319 ON as landed; player default, no pins); no daemon gap.
Camera CLEAN in all cells; capture STALE(nolock) at 512x384 (S8/S16), ok at 640x480 (S32). Scored per the claim procedure (sumline +
RUNMANI, no script); completeness >= 99% every cell (no content-dirty counter: presents_real / render_passes and 1 - skipped/ticks).
- **S8 NOT MET:** whole-run 39.19 / 38.51 (GS8A 0.01 under, GS8B 0.69 under; stall_ms 1942 / 4315), steady 40.24 / 40.28; audio clean.
- **S16 NOT MET, audio only:** both tick figures IN BAND x2 (39.28/40.10, 39.31/40.10 -- first S16 x2 over the floor; round Q
  39.18/39.13); GS16A 2 silent IRQs in play (ticks 1864, 4494), GS16B 0.
- **S32 (S32P) NOT MET, audio only:** both tick figures IN BAND x2 (39.32/40.12, 39.28/40.08); GS32A 2 silent IRQs in play (921, 1421),
  GS32B 1 (4912).
- "pcm_irqs exact": no expected pcm_irqs count is logged, so it is read as recorded (overwrites / underruns / late_writes 0 in
  every cell) and nothing beyond that is claimed.
- Cross-binary against earlier gate readings (placement moved at fe4b1a81 and b7ac6c46).
- Raw: `tests/harness/results/{WARMUPGATE,GS8A,GS8B,GS16A,GS16B,GS32A,GS32B}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND ID1 DATA (no verdict; the 0320 candidacy-2 decisive test is pooled after ID3).** Relay-on 14:52:58Z (coordinator
launch), target OFF 15:41:10Z (powerguard 0 mW 15:41:11Z, coordinator-verified); 5 cells exit 0, ID cells stamp f17997f06baa (main
b7ac6c46 + lab 0323); no daemon gap. Camera CLEAN in all cells (Trilby room 35); capture STALE(nolock) at 512x384. Block 1 of 3 (IDA1
IDD1 IDD2 IDA2); abba320d.py b2f83e52 (silentwhere 75f296a2, clock fix) runs only once ID3 is in -- no per-cell counters or deltas before
then. Raw: `tests/harness/results/{WARMUPID1,IDA1,IDD1,IDD2,IDA2}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND ID2 DATA (no verdict; pooled after ID3).** Relay-on 15:41:25Z (coordinator launch), target OFF 16:29:34Z
(powerguard 0 mW 16:29:37Z, coordinator-verified); 5 cells exit 0, ID cells stamp f17997f06baa; no daemon gap. Camera CLEAN in all
cells (Trilby room 35); capture STALE(nolock) at 512x384. Block 2 of 3 (IDA3 IDD3 IDD4 IDA4); no per-cell counters or deltas before the
pooled score. Raw: `tests/harness/results/{WARMUPID2,IDA3,IDD3,IDD4,IDA4}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND ID3 RESULT + 0320 CANDIDACY-2 POOLED VERDICT (rows in STATUS.md, ID1-ID3).** Relay-on 16:29:50Z (coordinator
launch), target OFF 17:17:34Z (powerguard 0 mW 17:17:43Z, coordinator-verified); 5 cells exit 0, ID cells stamp f17997f06baa; no daemon
gap. Camera CLEAN in all cells; capture STALE(nolock) at 512x384.
- **0320 candidacy 2** (lab/mmd 3804a35d + dba9d4bd; abba320d.py b2f83e52, silentwhere 75f296a2 clock fix; 6 A vs 6 D on main b7ac6c46 +
  lab 0323): pair deltas -347/-292, -294/-294, -297/-294 ms, drifts 56/1/1 ms; in-play silent-IRQ cells D 2/6 vs A 1/6, Fisher p 0.500;
  D counters 0, none in a room load; **SLICE-ONLY D silent IRQs IDD2 tick 876 and IDD5 tick 788 (both after "sound 11")** -> "VERDICT:
  KEEP OFF". 0320 (and lab 0323) stays OFF. Prediction MISSED (D events after a short clip). Pre-fix clock labels equal the fixed ones.
- Readings, not rules: arm A also shows a SLICE-classed silent IRQ after "sound 11" (IDA2 tick 1037) -- the class is by clip identity, so
  part of what the rule counts may be the fixture's base rate; the three warm-ups share the 8.3 log WARMUPID.LOG on the target (1/2/3
  tick_rate values across ID1-ID3), unscored.
- Raw: `tests/harness/results/{WARMUPID3,IDA5,IDD5,IDD6,IDA6}-2026-09-29/` (+ ID1 363f32a9, ID2 a7aec2f0). Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND WBC RESULT: clean-fixture WB cells PASS at both depths (rows in STATUS.md); the operator's five-round sequence
(GATE, ID1-ID3, WBC) is complete.** Relay-on 17:17:52Z (coordinator launch), target OFF 18:17:43Z (powerguard 0 mW 18:17:46Z,
coordinator-verified); 5 cells exit 0, WBC cells stamp ef123dba0adf (round Z's mainz.exe); no daemon gap. Camera CLEAN in all cells
(Trilby room 40; 5 Days room 13). 640x480 LOCKED in play (longest non-locked runs 3-4); no PCM play logged in any cell.
- **WB depth** (lab/wb d4b2db0c; depth-score.py at d4b2db0c with --no-pcm): **WBC8R VERDICT: PASS** (A PASS, B chroma 0.990, D 0.843;
  poll control 0.864); **WBC32R VERDICT: PASS** (A PASS, B 0.940, D 0.780; control 0.802). The WB pump passes its per-depth bar at 8 and
  32 bpp on clean fixtures.
- Readings, not rules: round Z's S8/S32 D failures were the fixtures' PCM, as lab-wb read; the poll controls also clear 0.70 on these idle
  fixtures; WBC8P/R's sumline tick_rate_steady reads 58.03 / 57.66 (> 40.8) in Trilby's text room 40 -- flagged, not part of the WB gate.
- Raw: `tests/harness/results/{WARMUPWBC,WBC8P,WBC8R,WBC32P,WBC32R}-2026-09-29/`. Captures (game music) and AGSSAVE.001 local only.

**2026-09-29 -- ROUND CS1 DATA (probe v3 486 round, no readout yet; coldstart3.py runs over all 9 CS cells after CS2).** Operator
approved "All three" (CS1 -> CS2 -> S8M). Relay-on 18:23:07Z (coordinator launch), target OFF 19:29:56Z (powerguard 0 mW 19:30:01Z,
coordinator-verified); 7 cells exit 0, CSV cells stamp 95519022159e (AGSCS3 = main b7ac6c46 + probe v3); no daemon gap. Camera CLEAN in
all cells (5 Days room 3 at 512x384 / 640x480); capture STALE(nolock) at 512x384 (S16), ok at 640x480 (S32). CSV32H3's timeout was capped
to 1736 s; it exited 0. Raw: `tests/harness/results/{WARMUPCS1,CSV16H1,CSV32H1,CSV16H2,CSV32H2,CSV16H3,CSV32H3}-2026-09-29/`. Audio and
AGSSAVE.001 local only.

**2026-09-29 -- ROUND CS2 DATA + PROBE v3 486 READOUT (coldstart3.py, lab/mmd 3a55115d, over all 9 CS cells).** Relay-on 19:30:16Z
(coordinator launch), target OFF 20:08:39Z (powerguard 0 mW, coordinator-verified); 4 cells exit 0 (WARMUPCS2 + CSV8H1-3, Trilby room 35
at 512x384), CSV cells stamp 95519022159e; no daemon gap. Camera CLEAN in all cells; capture STALE(nolock) at 512x384.
- Readout: all 9 cells CONSISTENT (scorer charges = engine charges). Charged silent IRQs: IN-PUMP 4 (CSV32H1 t913, t4913; CSV16H3 t784;
  CSV8H1 t1037), FEED 1 (CSV16H2 t2297, fill=0), GAP 0, IN-PUMP-OWED 0. P1 HELD (51 cold starts, expected 0.101/cold start, 95% [1, 10],
  observed 4); P2 FALSIFIED as written; P3 not reproduced. S8: CSV8H1 t1037 IN-PUMP at the lc 1036 cold start (the sound11 spot);
  CSV8H2/H3 no charges. The coordinator re-ran the scorer independently (git archive 3a55115d); output identical.
- Reading, not a rule: each P2 falsifier's Q seq equals its cold start's priming-pump seq (913/911 seq 8870, 4913/4911 seq 26508,
  784/782 seq 8241). Only P2's tick window abs(charge - lc) <= 1 fails, by 2; CSV8H1 1037/1036 passes, off by 1. No scorer amendment.
- The warm-ups share the 8.3 log WARMUPCS.LOG on the target, so WARMUPCS2's copy holds CS1's 212 lines plus its own; not scored.
- Raw: `tests/harness/results/{WARMUPCS2,CSV8H1,CSV8H2,CSV8H3}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-29 -- ROUND S8M RESULT: Gate S8 re-reading x2 with DOSAGS_MSGSKIP=1 (GM8A GM8B) -- the bar MET x2.** Main a504b469 (ags
0324), stamp d8c3aa2eafdf; round GATE's GS8 line plus DOSAGS_MSGSKIP=1, no other pins. Relay-on 20:08:59Z (coordinator launch), target
OFF 20:37:43Z (powerguard 0 mW 20:37:50Z, coordinator-verified); 3 cells exit 0, stamps OK, room 35, no daemon gap. Camera CLEAN in all
cells (warm-up: MMD title; GM8A/B: Trilby room 35, message box then the walker; black after exit); capture STALE(nolock) at 512x384.
- GM8A: whole-run 39.21 / steady 40.16, fps_p50 40.00, frames_skipped 48, stall_ms 1607; GM8B: 39.21 / 40.24, 40.00, 43, 1641. Whole-run
  is 0.01 over the 39.2 floor in both, as recorded (2 dp).
- Completeness: presents_real / render_passes 4966/4952 and 4971/4957 (100.28% both); 1 - frames_skipped/ticks (5002) 99.04% / 99.14%.
- Audio: pcm_irqs 2124 / 2079, silent_irqs 0, late_writes 0, overwrites 0, underruns 0 in both. "pcm_irqs exact" is read as recorded,
  as in round GATE.
- VOID check: exactly one "DOS-PORT msgskip n=1 lc=101" per cell (in STDOUT.TXT). Not void.
- Comparability: whole-run and stall_ms are NOT comparable with pre-MSGSKIP S8 readings (rounds R, GATE, the V/X/X2/ID A arms): the
  fixture changed. Steady is cross-binary against GATE's GS8 (b7ac6c46 -> a504b469); placement moved.
- Not covered: PLAN-GATES' "one 640x480 capture listen per depth" (not in the pre-registered bar; S8 runs at 512x384). No "Gates"
  claim paragraph until the coordinator decides.
- Raw: `tests/harness/results/{WARMUPS8M,GM8A,GM8B}-2026-09-29/`. Audio and AGSSAVE.001 local only.

**2026-09-30 -- ROUND BATCH: gate re-read under the ags 0347 counter -- S16, S32 (S32P) and S8 each MET x2 against the bar; CAPS8 +
WBC16 data only (lab-wb scores).** Operator "Batch after 0347 lands" / "Full set, 115 min"; relay-on 00:00:35Z (coordinator launch),
target OFF 01:42:14Z (powerguard 0 mW 01:42:20Z); 10 cells exit 0, stamps OK (8249193ed041 = main 553588d4 for CAPS8/GL, ef123dba0adf
for WBC16), no daemon gap. Camera CLEAN in all 10 (GL8B: the camera's exposure rose after exit, monitor black); capture STALE(nolock) at
512x384 (warm-up, GL16, GL8), ok at 640x480 (CAPS8, GL32, WBC16).
- gatebar.py (e341a3bd + ee0196b3), as registered: GL16A 39.29/40.13, GL16B 39.29/40.10; GL32A 39.28/40.12, GL32B 39.34/40.07; GL8A
  39.26/40.23, GL8B 39.35/40.29 (msgskip n=1 once each); fps_p50 40.00, completeness >= 98.98% both ways, silent_irqs 0, overwrites /
  late_writes / underruns 0, accounting diff 0 in all six. start_latency_irqs (reported): GL16B 1 (t1914), GL32B 3 (t2413, 3914,
  4913), others 0 -- where the pre-0347 counter charged in-play silent IRQs in round GATE.
- Not a claim yet: PLAN-GATES' "one 640x480 capture listen per depth" (CAPS8 covers S8, lab-wb scores it); no "Gates" paragraph here.
- Comparability: silent_irqs is not comparable with pre-0347 readings (rounds GATE, S8M); tick figures are cross-binary against GATE
  (b7ac6c46) and S8M (a504b469), placement moved at each landing.
- Raw: `tests/harness/results/{WARMUPBT,CAPS8,GL16A,GL16B,GL32A,GL32B,GL8A,GL8B,WBC16P,WBC16R}-2026-09-30/`. Audio and AGSSAVE.001 local.
- 2026-09-30 SCORED (lab/wb 37bf008c; the registered invocations at caff563d, coordinator re-ran both, identical): CAPS8 CAPTURE CHECK
  PASS (K1 0 zero frames; K2 worst 24.7 dB < 25, one 11.6 ms frame at 299.25 s, information; K3 NCC 0.41 vs null 0.14; K4 >= 52.8 /
  47.8 dB; K5 clean under 0347) -- the S8 640x480 capture listen, closed by score. WBC16R VERDICT PASS (A pass; B chroma 0.973; D
  0.785, control WBC16P 0.794 information): the WB bar passes at S8 / S16 / S32P on ef123dba0adf, clean fixtures. S8 is complete
  against PLAN-GATES (GL8 bar MET x2 + CAPS8). S16 / S32 wait for CAPS16 / CAPS32 (operator "Harness capture cells"; lab-wb).

**2026-09-30 -- ROUND CAPS DATA (CAPS16 + CAPS32, the S16 / S32 640x480 harness capture cells; lab-wb scores).** Operator "Power on at
9:30 pt" then "Power on is okay now": relay-on 04:25:45Z (coordinator launch, early; ORDER-CONFIRMED records it), target OFF 04:54:35Z
(powerguard 0 mW 04:54:37Z); 3 cells exit 0, stamps OK (64d449a5b895 = main 3aee50b4), no daemon gap. Camera CLEAN in all 3 (warm-up MMD
title; CAPS16 / CAPS32 5 Days room 3 with the walker; black after exit); capture ok on CAPS16 / CAPS32 (640x480), STALE on the warm-up.
- CAPS16: valid on the game-side log (music 0; "Playing sound 3" x3); scored by lab-wb (capture-check3.py 33cde13b).
- CAPS32: VOID as registered -- its STDOUT has no "Playing sound 3" (only "Playing music 0", "Playing sound 10" x3, "Playing sound 9" x1);
  the first walked 486 room-3 run without it (GL16A/B, GL32A/B logged it 2-3x). silent_irqs 0 in both cells.
- Raw: `tests/harness/results/{WARMUPCP,CAPS16,CAPS32}-2026-09-30/`. Audio and AGSSAVE.001 local only.
- 2026-09-30 SCORED (lab/wb 4194baf5): CAPS16 CAPTURE CHECK PASS (M1 +1 cent, M2 0.809) -- the S16 640x480 capture listen closed by
  score; both CAPS cells read underruns 6 = primes 6 on the 0348 binary, which was reverted (4fc91556; lab/mmd 569df3b1).
- ROUND C32R DATA (CAPS32R, the one re-run lab/wb 49aa373f allows; binary per 32378c49 = main 8f439c0f, e3a83135dc9c, 0348 out):
  relay-on 08:13:45Z (operator "Run now, 30 min cap"), target OFF 08:32:39Z (powerguard 0 mW 08:32:46Z); both cells exit 0, stamps OK,
  no daemon gap; camera CLEAN (warm-up MMD title; 5 Days room 3 with the walker; black after exit); capture ok. Valid on the game-side
  log ("Playing sound 3" x2, music 0); underruns 0, silent_irqs 0, pcm_irqs 483 = mixed. Scored by lab-wb (capture-check3.py 33cde13b).
  Raw: `tests/harness/results/{WARMUPC2,CAPS32R}-2026-09-30/`. Audio and AGSSAVE.001 local only.
- 2026-09-30 LANDED ags 0348 + 0349 + 0350 (cd217660): main = af3f0824499e, sha256 27a2f5e6a1a9e26d..., 8,670,630 B; lab-s8's independent
  build from a fresh clone at 8f439c0f is byte-identical (lab/mmd df5885b2, T6.md "Independent build of the landing binary").

**Parallel-worker rules (operator decision 2026-09-23):**
- DOSBox-X displays: me 211 (default), lab 221/231/241/261. `run-dosbox.sh` now refuses a display that
  already has a DOSBox-X window on it.
- No `--sb-live` cells at the same time as a freeze-capture gate.
- Patch ranges: me ags 0210-0229 / SDL 0196-0209; lab-metric ags 0230-0249 / SDL 0210-0219;
  lab-journeys ags 0250-0269 / SDL 0220-0229; lab-wb ags 0270-0289 / SDL 0230-0239; lab-mmd ags
  0290-0309 and 0310-0319 (added 2026-09-24 by the coordinator; its levers filled 0290-0309) / SDL
  0240-0249.
- `git pull --rebase` before every push to main; never force.
- When the hub's host-wide DOSBox-X lock lands (`/tmp/dos-port-dosbox.lock`: shared for functional
  runs, exclusive for timing/rate/screen runs), the gate, the probe series and `run-dosbox.sh`'s
  freeze/screen/`--sb-live` paths take it exclusive, once around the whole series.

## How to re-enter

1. Read this file, then `STATUS.md`'s table. Do not open `PLAN-LOG.md`
   unless a step needs a specific past cell; grep it by tag.
2. Before any cell: pre-register the prediction, the bar, and what would
   void the cell; confirm the code under test executes on that fixture
   (`grep` the existing cell log first); use a clean build for gate cells.
3. Record each cell's raw results under `tests/harness/results/<TAG>-<date>/`
   and one dated paragraph here under the step it serves -- not a new
   chronological section.
4. **Next, in order (2026-09-23; see "Next campaign: working music + high fps at 8/16/32 bpp"):**
   1. ~~Gate, review, pin of 0209~~ done 2026-09-23 (`ags-0209-clean.exe`, `db4960959cf2`).
      SDL 0196 (the Hold-vs-Pause fix) opens my next slice.
   2. The hub's DOSBox-X lock: bump `.sdl-dos-ports` when it lands and take it exclusive around
      the gate, the probe series and the freeze/screen/`--sb-live` paths.
   3. The sound-on stall measurement, **measurement only**, on DOSBox-X (Gate 3 fixture): name the
      call in each sound-on stall tick -- WAV parse/resample, file I/O, voice start, script work --
      in ms, and estimate the whole-run gain against the 39.2 floor. Pre-register first.
   4. S16 fixes toward Gate S16 (5 Days, sound on), then the hardware rounds for S8/S16/S32 as the
      lab slices land.
   5. The Vibra lane, pending the operator (card not detected, SBCAP1). Step 9 (Maniac Mansion
      Deluxe) runs IN PARALLEL on dosags-lab-mmd (operator decision 2026-09-23), starting at 9.1.
   Step 7 (ViRGE and Cirrus) stays deferred behind all of these. Rate cells at 512x384 have a blind
   audio capture until the standalone USB audio input exists.
