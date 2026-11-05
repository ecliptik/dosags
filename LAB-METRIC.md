# LAB-METRIC -- a deterministic work metric that predicts 486 time

Branch `lab/metric` (worktree `~/git/dosags-lab-metric`), worker `dosags-lab-metric`.
Plan input: hub `plans/LESSONS-CLAUDE-AI-PERF-2026-09-23.md` section 2 and "Execution design".
Operator decision 2026-09-23: engine counters first, validated against hardware rates already on
disk before they screen anything. LAB ONLY: no real-hardware run is part of this work.

Target machine for every "measured" figure below: HW-486-66 (486DX2-66, 16 MB, ATI Mach64 215CT,
UniVBE), `DOSAGS_FIXED_TIMESTEP=1`, direct framebuffer. DOSBox-X figures are COUNTS only; no
DOSBox-X time is used as evidence of 486 time anywhere in this file.

---

## 1. PRE-REGISTRATION (written and committed before any DOSBox-X counter run)

### 1.1 The validation cells and what is measured on them

The measured quantity is **busy ms per render pass on the 486**, over the steady part of the run:

    busy_ms          = loop_ms - stall_ms - wait_next_frame.total_ms
    busy_per_render  = busy_ms / render_passes

All three inputs are the hardware run's own `RUNMANI.LOG` lines (`tick_rate_steady=... loop_ms=...
stall_ms=...`, `tickstats_wait_next_frame ... total_ms=...`, `fps_basis ... render_passes=...`).
Stall ticks (self time > 250 ms: loads, fades, blocking script) are excluded from time; the new
counters exclude the same ticks' work (section 1.2), so both sides cover the same ticks.

| cell (raw dir under `~/git/dosags/tests/harness/results/`) | fixture | binary | busy ms | renders | **busy / render** | stable rate |
|---|---|---|---|---|---|---|
| F2B1-2026-09-21 (F2B2 replicate) | BENCH8 anim12-gate, Mode 13h 320x200x8, alias ON | 0194 `e8d4b76c5cd9` | 105583 (105580) | 4996 | **21.13** (21.13) | 39.98 |
| S2F2-2026-09-22 (S2F3 replicate) | 5 Days in play, `--startr 3`, drive-walk 2 s, 512x384x16 pillarbox alias ON | 0196 `340fa8167624` | 52021 (52143) | 4938 | **10.53** (10.56) | 39.47 |
| AQF1-2026-09-21 (AQF2 replicate) | AGS Quest AutoPilot, 640x480x16 1:1 letterbox (640x360), alias ON y=60 | 0194 `e8d4b76c5cd9` | 58473 (58462) | 3282 | **17.82** (17.81) | 37.78 |
| S2M1-2026-09-22 | Maniac Mansion Deluxe character select, title idle to tick 1000, 512x384x16, no alias | 0194 `e8d4b76c5cd9` | 35134 | 239 | **147.00** | 6.75 |
| SB5O-2026-09-23 | 5 Days own flow (intro, title, room 3), 640x480x16 2x, **sound ON (OPL3, PGSB)**, 16000 ticks | 0208 `513a187edcbb` | 579109 | 2666 | **217.22** | 4.47 |

Measured order, fastest to slowest per render: **S2F2 < AQF1 < F2B1 < S2M1 < SB5O.**

Not validated, and why: the AGS Quest NOGUI 40.61 cells (PLAN-LOG "NOGUI replication") and REPRO1
have no raw directory on disk (searched `tests/harness/results/` and the tree); their fixture is a
modified package with `gui[7].Visible = false`. Recorded as a gap, not a cell.

### 1.2 The work vector (per run, split steady / excluded)

Counted by ONE new ags patch (range 0230-0249). Every counter is a plain integer increment or an
add of a size already in hand, never a clock read. The vector is snapshotted when each tick scope
(the existing `DosTickStallScope`) opens and closes; a tick whose self time is a stall moves its
own (children-excluded) delta into an `excluded` bucket, and so does everything before the first
tick (`preloop`) and after the last one. The summary line reports the steady vector.

| counter | what it counts | where | new or existing |
|---|---|---|---|
| `ticks`, `renders`, `presents` | loop ticks, render passes, real presents | GameTimer / tick timing | existing, re-reported per scope |
| `script_ins` | script VM instructions dispatched | `ccInstance::Run` loop head, local counter flushed on exit | **new** |
| `script_ext` | script -> engine API calls (`SCMD_CALLEXT`) | same | **new** |
| `push_bytes`, `push_rects` | bytes handed to `SDL_UpdateWindowSurface(Rects)` (clipped rect area x window Bpp) | `Present()` | **new** (existing `dirtypresent` px are periodic and px-only) |
| `blit1x_bytes` | present-time RAM->RAM copy, 1:1, dst bytes | `Present()` non-aliased branch | **new** |
| `blitsc_bytes` | present-time scaled copy (2x rung), dst bytes | same | **new** |
| `cmp_bytes` | bytes compared by the 8-bit unchanged-frame check | `FramesEqualFast` exit paths | **new** |
| `cache_bytes` | bytes copied into the last-presented cache | `Present()` | **new** |
| `bg_px` | background-restore pixels | `bg_px` (patch 0126) | existing |
| `fill_px` | black-fill + batch clear pixels | `black_fill_px` + `rb_clear_px` | existing |
| `spr_n` | sprite composites | `rb_sprites` (0125) | existing |
| `spr_opq_px`, `spr_msk_px`, `spr_bld_px` | composited px by blit class (opaque `Blit`; masked `DrawSpriteWithTransparency`; alpha `TransBlendBlt` or alpha < 255), clipped to the surface clip | `RenderSpriteBatch` | **new** (0125 counts nominal area, one class) |
| `file_bytes`, `file_calls` | bytes returned by `FileStream::Read`/`ReadByte` | `Common/util/filestream.cpp` | **new** |
| context | `vs_bpp`, `win_bpp`, `win=WxH` | last real present | new |

Not added: **allocations** (needs `-Wl,--wrap=malloc` or an allocator hook across every library;
a build-level change, not a counter; revisit only if the validation says something unmodelled
scales with churn). **Text/font rendering** (inside the sprite composites once rendered).

Optional per-second rows: `DOS-PORT workpersec t=N ...` with the cumulative counters, sampled at
the existing once-per-second `persec` point (no extra clock read).

### 1.3 The cost model (constants from PLAN.md "The numbers to plan against"; nothing fitted except where marked)

Clock 66e6 Hz (the figure PLAN-LOG used to derive 19.4 and 7.8 cycles/px). Bus figures are the
bandwidth probe (2026-09-17/19), measured on the target.

| term | constant | source |
|---|---|---|
| push, VESA LFB | 1 / 27.3 MB/s = 0.03663 us/B | PLAN.md bus ceilings |
| push, Mode 13h aperture | 1 / 9.3 MB/s = 0.10753 us/B | same |
| RAM->RAM copy (`blit1x_bytes`, `cache_bytes`, `bg_px` x vs_bpp) | 1 / 17.0 MB/s = 0.05882 us/B | same |
| write-only fill (`fill_px` x vs_bpp) | 1 / 40.9 MB/s = 0.02445 us/B | same |
| compare (`cmp_bytes`), two reads per byte, a read 1.4x a write | 2 x 1.4 / 40.9 MB/s = 0.06846 us/B | same ("a read costs 1.4x a write") |
| scaled 2x copy (`blitsc_bytes`, dst) | half the dst written by the replicate at write-only, half copied row-to-row: 0.5 x 0.02445 + 0.5 x 0.05882 = 0.04164 us/B | DERIVED from the two figures above; not itself measured |
| masked / alpha sprite px | 19.4 cycles/px at 2 B/px = 9.7 cycles per byte of pixel = 0.14697 us/B x vs_bpp | PLAN.md (AGS Quest `render_backbuffer`, 16-bit). **8-bit masked and alpha-blend costs are NOT measured**; per-byte scaling from the 16-bit figure is an assumption |
| opaque sprite px | 7.8 cycles/px at 2 B/px = 3.9 cycles/B = 0.05909 us/B x vs_bpp | PLAN.md copy floor |
| scene construct, per render | 3.0 ms fixed + 0.335 ms x (`spr_n` / render) | PLAN.md BENCH8 8-bit 4 vs 12 objects. Known overlap: the 3.0 ms includes BENCH8's own background restore, which `bg_px` also costs (about 0.6 ms on that fixture): accepted as a stated bias, not tuned out |
| engine fixed, per tick | 2.10 ms | PLAN.md AGS Quest 16-bit tick "everything else" |
| script VM, per instruction | **NOT MEASURED anywhere in the record.** Calibrated on ONE cell, S2F2, before looking at any other cell's count: c_ins = S2F2 hardware `tickstats_script_vm total_us` / S2F2 DOSBox-X `script_ins` over the whole run. S2F2 is therefore in-sample for this term; F2B1, AQF1, S2M1, SB5O are held out for it | calibration, stated |
| file bytes read | **NOT MEASURED** (the CF read test never ran, PLAN.md "storage stall") | costed at 0 and reported as a count |
| audio (mixing, OPL/MIDI ISR) | **NOT MODELLED** | SB5O carries sound; predicted to be under-predicted by whatever sound costs |

Prediction for a cell:

    per_render_ms = R_present + R_rb + R_scene + R_fill + R_bg          (DOSBox-X steady vector / steady renders)
    per_tick_ms   = 2.10 + c_ins x script_ins/tick                       (DOSBox-X steady vector / steady ticks)
    predicted busy / render = per_render_ms + per_tick_ms x (hw_steady_ticks / hw_renders)

The last factor is the workload mix the 486 actually ran (ticks per render under the fixed
timestep), taken from the hardware manifest; it is an input stating what was asked of the machine,
not a fitted constant. A closed-form rate prediction that does not use it (fixed point of
`40 x per_tick + R x per_render = 1000 ms`) is reported beside it as a secondary figure.

DOSBox-X reproduction of each cell: same package, config, rung, `--startr`, auto-exit tick and
`DOSAGS_FIXED_TIMESTEP=1` as the hardware command; the input drivers (`drive-walk.sh`,
`drive-start.sh`) use vcctrl and are replaced by xdotool clicks on a private display at the same
cadence; S2M1 adds `DOSAGS_DIRECT_VSCREEN=0` because its 0194 binary had no pillarbox alias (0196
engages one at that rung); SB5O runs with `--sb-live` and the OPL3 conf. Where the lab run cannot
match the hardware run's content, that is written down next to the cell.

### 1.4 Pass criterion (fixed now)

**PASS if and only if both hold across the five cells F2B1, S2F2, AQF1, S2M1, SB5O:**
1. **Rank:** the predicted busy/render orders the five cells exactly as measured
   (S2F2 < AQF1 < F2B1 < S2M1 < SB5O).
2. **Scale:** every cell's predicted / measured busy/render lies within **[0.67, 1.5]** (a factor
   of 1.5 either way).

Reported beside it, not part of the verdict: the factor-2 band; per-phase predicted vs hardware
phase (`present_update_window`, `render_backbuffer`, `scene_construct`, `script_vm`); the held-out
error of the calibrated `c_ins` term on the four held-out cells (hardware `script_vm` ms vs
predicted).

A failure is a finding. The pre-registered model is not re-tuned after the counts come in; any
revised model is reported separately, labelled post hoc, with its own held-out error.

### 1.5 Counter cost

Measured as a DOSBox-X RATE RANKING only (not 486 time): BENCH8 anim12 at Mode 13h and MMD title
(script-heavy), fixed timestep OFF so the rate floats, A B B A of the baseline build (ags 0208) and
the patched build, same conf and cycles. Reported as the rate delta and its sign against the A-A
spread. Real 486 cost is a hardware question and is written as a request, not measured here.

---

## 2. Step 1: what dosags already counted (inventory, 2026-09-23)

Read from a hardware manifest (`F2B1-2026-09-21/RUNMANI.LOG`, `STDOUT.TXT`) and the source
(`vendor/ags` at ags 0208). Not re-added; patch 0230 re-reads them into the vector.

| existing line / field | where | what it gives | gap for a work metric |
|---|---|---|---|
| `tickstats_*` (40+ phases) | `quit.cpp` `dos_port_tick_emit` | per-phase time on the machine it ran on | time, not work; DOSBox-X time is not 486 time |
| `fps_basis` render_passes / presents_real / skipped | `game_run.cpp` | render and present counts | none |
| `blit_path fast/generic/unscaled` | same | which present copy path | no bytes |
| `persec` rows | same | cumulative ticks/renders/presents per second | no work columns |
| `bgstruct`, `bgstruct_final` px, `bgspans` | `draw_software.cpp` 0126/0162 | background-restore px | none (px x bpp = bytes) |
| `rbstruct` sprites, sprite_px (nominal), clears | `ali3dsw.cpp` 0125 | composites and nominal area | one class; masked vs opaque vs alpha cost differ 2.5x |
| `dirtypresent` px_narrow/px_full/px_multi | `ali3dsw.cpp` 0124/0129 | pushed px, printed every 500 presents | periodic, px only |
| `blackfill` px | `draw_software.cpp` 0137 | fill px | none |
| `skipframe` (every 4th skip) | `game_run.cpp` 0140/0164/0166 | per-skip sample: present/rb/scene/script/events us, sprite_px, present_px, sprites, maxspr | sampled tail only |
| `stallwhat`, `tick_stall` | same 0141/0153 | stall attribution | none |
| `evtype`, `evobj`, `objsetup`, `scfile`, `afterfadein` | 0150/0155 | event dispatch time by kind | time only |
| **missing** | | script VM instructions, API calls, bytes to the screen, present copy bytes, 8-bit compare bytes, px by blit class, file bytes | added by ags 0230 |

## 3. Step 2: the patch (ags 0230)

`patches/ags/0230-DOS-PORT-patch-0230-work-vector-deterministic-counts.patch`
(format-patch `From 9f9b14dc1...`, vendor tree `vendor/ags` on top of 0208; reviewed with
`/sdldos:review`). Output, in `RUNMANI.LOG` after `persec`:

    DOS-PORT work scope=steady ticks= renders= presents= script_ins= script_ext= push_bytes= push_rects=
        blit1x_bytes= blitsc_bytes= cmp_bytes= cache_bytes= bg_px= fill_px= spr_n= spr_opq_px= spr_msk_px=
        spr_bld_px= file_bytes= file_calls= vs_bpp= win_bpp= win=WxH script_ins_counted=0|1
    DOS-PORT work scope=excluded ...        (preloop + stall ticks' self work + after the last tick)
    DOS-PORT workpersec t=N ins= push= blit= spr_px= bg_px= file=   (cumulative, once per second)

`steady` covers exactly the ticks `tick_rate_steady` covers (first tick entry to last tick exit
at any depth, stall ticks' self work removed with nested ticks subtracted as for time).
`steady + excluded` = the whole run.

**Two builds.** `script_ins` (a per-instruction increment in `ccInstance::Run`) is compiled only
into the LAB binary: `make build-ags AGS_WORK_SCRIPT_INS=1` (the define sits in the flags the
build fingerprint hashes, so a lab binary never shares a `binary_sha12` with a timed one). Every
other counter is in every build. `script_ext` (API calls) is in every build.

One defect found and fixed before any result was recorded: the first build updated the "last
exit" snapshot only at outermost tick exits while `dos_tick_last_exit` updates at every exit;
AGS Quest's AutoPilot ends inside nested ticks, so 434 ticks landed in `excluded`. Those runs were
discarded (not committed); every run below is on the fixed code.

### Determinism
- MMD title, same binary, two runs: every field of both `work` lines identical
  (`script_ins=5636730`, `push_bytes=3036544`, ...). BENCH8 anim12-gate, two runs: identical.
- 5 Days in play (xdotool-driven) two runs: within 0.1% (`bg_px` 8020939 vs 8011965).
- Lab vs the hardware run's OWN existing counters, same fixture: BENCH8 presents 2483 vs 2481,
  `bg_px` 54587832+10907 vs `bgstruct_final px=54544194` (0.1%); 5 Days in play `bg_px` 8.08M vs
  6.24M (+29%) and blackfill+clear 1.06M vs 0.71M: xdotool clicks do not walk the vcctrl
  driver's path, so the in-play content differs by that much. AGS Quest steady ticks 3555 vs
  3560 on the 486.

## 4. Step 3: the lab runs (counts only)

Raw: `tests/harness/results/LABMETRIC-2026-09-23/L*/` (RUN.BAT, ACSETUP.CFG, RUNMANI.LOG, STDOUT.TXT).
Scored by `tests/harness/lab-metric.py` (the pre-registered model, unchanged) into
`lab-metric-results.json` beside them.

| cell | lab dir | lab binary | how the lab run matched the hardware run |
|---|---|---|---|
| F2B1 | `LF2B` | 0230 pre-gate lab (`a6f3c285ba73` line) | same BENCH8 anim12-gate cfg; deterministic |
| S2F2 | `LS2F` | same | `--startr 3`, xdotool walk (`lab-drive-xdotool.sh walk`) for drive-walk: bg_px +29% vs the 486's own counter (different path walked) |
| AQF1 | `LAQF` | same | AutoPilot, same cfg; steady ticks 3555 vs 3560 |
| S2M1 | `LS2M` | same | title idle to tick 1000, `DOSAGS_DIRECT_VSCREEN=0` (0194 had no pillarbox alias) |
| SB5O | `LSB5` | `6bc92c4015ff` (rebased lab build: + ags 0209, SDL 0195/0196 MIDI pause fixes, no engine-work change) | own flow with OPL3 + SB live (`--interactive --sb-live`, `confs/dosbox-x-fast-opl3.conf`, `games/5days/ACSETUP-ON.CFG`, 16000 ticks); `midi=opl3 midi_tick=isr late_writes=0` in the lab manifest |

**SB5O, first attempt void.** The first LSB5 run (binary `a6f3c285ba73`) was killed partway by the
coordinator and is not used; its files are kept out of the tree. It had also sat on the title
screen about twice as long as the hardware run (room 99 at about tick 5370 against 3781) and ran
without the OPL3 conf (`midi=none`).
**The re-run is aligned by tick:** rooms 1 -> 2 are tick-deterministic (room 2's fade-in stall is
tick 1053 on both). Hardware left the title at tick 3781, so `LSB5/lsb5.sh` clicks START (window
56,424) 68 s (2728 ticks at 40/s) after `event=ready room=2` appears in the stage's STDOUT: room 99
began at lab t_ms 96765, i.e. tick ~3781. One click, answered (`LSB5/DRIVER.LOG`, `CLICK.TXT`).
Lab renders 14710 against the 486's 2666 in steady scope. That is expected: the emulator renders
almost every tick, the 486 one tick in six. The model uses per-render and per-tick work and takes
the ticks-per-render mix from the hardware.

Note on interactive runs: `dosbox-run.sh --interactive` never auto-exits (it is the "user drives"
mode), so an interactive lab run holds the EXCLUSIVE lock until its runner is stopped. LSB5's runner
was stopped (TERM to its own runner pid, whose trap takes down only its own DOSBox-X and Xvfb and
releases the lock) after `RUNMANI.LOG` was complete (`exit_code=0`). About 4.5 min of lock were
held idle. Future interactive lab runs watch for the manifest and stop their own runner.

## 5. VERDICT (section 1.4, as written): **FAIL** -- rank fails and scale fails

| cell | measured busy/render (ms) | predicted | predicted / measured | measured rank | predicted rank | per_render / per_tick (ms) | ticks per render (hw) | closed-form rate |
|---|---|---|---|---|---|---|---|---|
| S2F2 | 10.53 | 11.33 | **1.08** | 1 | 1 | 5.84 / 5.42 | 1.012 | 40.0 |
| AQF1 | 17.82 | 20.25 | **1.14** | 2 | 2 | 17.01 / 2.99 | 1.085 | 40.0 |
| F2B1 | 21.13 | 24.28 | **1.15** | 3 | 3 | 14.90 / 9.37 | 1.001 | 40.0 |
| S2M1 | 147.00 | 1473.45 | **10.02** | 4 | **5** | 24.66 / 346.95 | 4.176 | 0.0 |
| SB5O | 217.22 | 84.21 | **0.39** | 5 | **4** | 54.10 / 5.01 | 6.011 | 14.8 |

- **Rank:** predicted S2F2 < AQF1 < F2B1 < **SB5O < S2M1**; measured ... < S2M1 < SB5O. FAIL.
- **Scale [0.67, 1.5]:** S2M1 10.02 and SB5O 0.39 are outside. FAIL. (Factor 2, informational: also fails.)
- Three of five cells (the render-bound ones) are within 1.08-1.15, all over-predicted.
- Raw: hardware `~/git/dosags/tests/harness/results/{F2B1-2026-09-21,S2F2-2026-09-22,AQF1-2026-09-21,S2M1-2026-09-22,SB5O-2026-09-23}/RUNMANI.LOG`;
  lab `tests/harness/results/LABMETRIC-2026-09-23/{LF2B,LS2F,LAQF,LS2M,LSB5}/RUNMANI.LOG`;
  every number in `lab-metric-results.json`.

**Held-out error of the calibrated script term** (`c_ins` = 61.06 us/instruction = S2F2 hardware
`script_vm` 16608 ms / 272009 lab instructions), predicted script ms over the run vs hardware
`script_vm`:

| cell | predicted | hardware | ratio |
|---|---|---|---|
| F2B1 | 36505 | 5717 | 6.39 |
| AQF1 | 3777 | 102102 | 0.037 |
| S2M1 | 347143 | 24629 | 14.1 |
| SB5O | 46680 | 131986 | 0.35 |
| (S2F2, in-sample) | 16608 | 16608 | 1.00 |

Off by a factor of 3 to 27 on every held-out cell, in both directions. **Why:** the hardware
`script_vm` phase is not instruction time. It wraps blocking script calls, and their nested game
loops run inside it: S2F2's total includes one 11,667 ms call, AQF1's 16,987, SB5O's 56,937. So
the one-cell calibration folded a blocking call into a per-instruction price. The per-instruction
cost is not constant even without the largest call: 4.3 us/ins on S2M1 (script-bound, 5691
ins/tick), 9-18 on F2B1/S2F2, 98-1376 where speech and waits nest ticks.

**Per phase** (informational, predicted ms per call / hardware tickstats mean per call):

| phase | F2B1 | S2F2 | AQF1 | S2M1 | SB5O |
|---|---|---|---|---|---|
| `present_update_window` | 1.37 / 1.93 | 0.14 / 0.49 | 0.98 / 2.55 | 0.11 / 0.74 | **22.51 / 22.34** |
| `present_blit` | -- | -- | -- | **7.53 / 7.74** | 25.58 / **117.30** |
| `present_dirty_check` (8-bit) | 4.41 / 4.73 | -- | -- | -- | -- |
| `render_backbuffer` | 1.14 / 2.73 | 1.51 / 1.94 | 9.21 / 6.91 | 11.50 / 9.43 | 1.66 / 2.29 |
| `scene_construct` (+bg) | 8.67 / 6.79 | 4.19 / 3.17 | 6.82 / 5.04 | 5.52 / 2.59 | 4.35 / 3.15 |

What the per-phase table says:
- **Bus terms priced from the probe are right where the copy is one big block:** SB5O's full-frame
  single-rect push is 1.01x; S2M1's 1x present copy 0.97x; F2B1's 8-bit compare + cache 0.93x.
- **Multi-rect pushes cost 1.4-6.6x their bytes at the bus ceiling.** The byte count misses a
  per-rect or per-row cost (the backend's `SDL_memcpy` per row per rect).
- **The 2x scaled 16-bit copy costs 4.6x the DERIVED constant** (117 ms per 614,400 B, 5.2 MB/s).
  That constant was never measured, and it is the largest single miss after script.
- **Masked 8-bit sprites cost 2.4x the per-byte scaling of the 16-bit figure** (F2B1). The
  assumption was flagged as unmeasured in 1.3, and it is wrong.
- Scene is over-predicted 1.3-2.1x (the 3.0 ms fixed figure is BENCH8's own).
- **SB5O's audio (OPL3 ISR replay + SB PCM) is not modelled.** Its busy time has about 70 ms per
  render (11.6 ms per tick) that no phase above accounts for.

## 6. POST HOC model (labelled: designed after the verdict; its only error figure is leave-one-out)

`tests/harness/lab-metric-posthoc.py` -> `lab-metric-posthoc.json`. Changes, each prompted by the
per-phase table: push = bus bytes (kept) + fitted `k_rect` per rect; 2x scaled copy = fitted us/B
(only SB5O has one, so held-out SB5O falls back to the derived constant); `render_backbuffer` and
`scene` get fitted scales; per tick = a + b x `script_ext`/tick (API calls) fitted on residuals,
replacing `c_ins`. Every constant is refitted on four cells and predicts the fifth.

| cell | measured | LOO predicted | LOO ratio | in-sample ratio (not an error figure) |
|---|---|---|---|---|
| F2B1 | 21.13 | 19.55 | 0.93 | 0.94 |
| S2F2 | 10.53 | 12.78 | 1.21 | 1.16 |
| AQF1 | 17.82 | 24.95 | 1.40 | 1.27 |
| S2M1 | 147.00 | 1181.39 | **8.04** | 1.00 |
| SB5O | 217.22 | 87.49 | **0.40** | 0.87 |

**LOO: rank fails, scale fails** (S2M1 8.0x, SB5O 0.40x). Five cells cannot validate the post hoc
model either, because each of the two slow cells is dominated by a term that no other cell exercises
(S2M1: script at 177 API calls/tick, 50x the next cell; SB5O: the 2x scaled copy plus audio).
**The render-bound cells hold at 0.93-1.40 held out.** Fitted constants (all five, in-sample):
`k_rect` 0.166 ms/rect (LOO range 0.111-0.238), `render_backbuffer` x0.93 (0.86-1.04), `scene`
x0.70 (0.67-0.76), scaled copy 0.191 us/B (SB5O only).

**How far this can be trusted for screening (and no further):** for a render-bound fixture (AGS
Quest, BENCH8, 5 Days in play), the counters predict busy/render within about 0.9-1.4x held out,
and a change that moves one render-side term by more than about 40% moves the prediction
meaningfully. The counters cannot price: script/API work, blocking calls, audio, the 2x scaled
copy, and any present path the five cells do not contain. **A 32-bit present is one of those**
(LAB-S32.md).

## 7. Counter cost (section 1.5), re-measured under the EXCLUSIVE lock

**The earlier figures are NOT COMPARABLE.** These are the ones in the 0230 v2 commit message and
in patch 0230's own message: "script_vm 4.6% slower", "render rate 18% lower (9.52 -> 7.76)",
"+0.9% busy per render on BENCH8". Their runs (13:57-14:17 local, 2026-09-23) interleaved with
other workers' DOSBox-X runs before the host lock existed. The figures of record are below.

Series: `tests/harness/results/LABMETRIC-2026-09-23/COST/cost-series.sh`, one EXCLUSIVE
`dosbox_lock_series` around all 14 runs (22:56-23:04 UTC), `confs/dosbox-x-fixed25k.conf`
(section 8), `--fixed-timestep`, `--no-verify-present`, order A B L L B A per fixture. Arms:
**A** = rebased tree without ags 0230 (`binary_sha12` label `a0a0a0a0a0a0`, built from a separate
checkout of `vendor/ags` at 0209), **B** = 0230 timed build (`640060d25f24`), **L** = 0230 lab
build with `script_ins` (`6bc92c4015ff`). Fixtures: BENCH8 anim12 at Mode 13h (F2B1's cfg,
`hold_ticks=1000`), MMD title to tick 1000 (S2M1's cfg, `DOSAGS_DIRECT_VSCREEN=0`). Raw:
`COST/<fixture>-<arm>-<n>/RUNMANI.LOG`; `COST/INDEX.TXT`.

| fixture | arm | busy/render (ms, emulated) | renders | `fps_p50` | `script_vm` us | `render_backbuffer` us |
|---|---|---|---|---|---|---|
| BENCH8 | A x2 | 15.280 / 15.280 | 1040 | 40.00 | 709567 / 709458 | 3493466 / 3493378 |
| BENCH8 | B x2 | 15.406 / 15.406 | 1040 | 40.00 | 709817 / 709967 | 3569624 / 3569607 |
| BENCH8 | L x2 | 15.423 / 15.423 | 1040 | 40.00 | 728452 / 728435 | 3569650 / 3569655 |
| MMD | A x2 | 104.650 / 104.650 | 239 | 9.88 | 17802847 x2 | 3641615 x2 |
| MMD | B x2 | 105.986 / 105.977 | 236 | 9.68 / 9.67 | 17815214 / 17816885 | 3603916 / 3603914 |
| MMD | L x2 | 127.821 x2 | 196 | 7.94 | 18615277 x2 | 2993059 x2 |

- **Always-on counters (B vs A; they are in every timed build):** busy per render **+0.82%**
  (BENCH8; `render_backbuffer` +2.2%, the per-sprite class counters) and **+1.28%** (MMD; renders
  239 -> 236). The A-A spread is 0.000 ms on busy per render for both fixtures. That is the DOSBox-X
  ranking. The 486 cost is a hardware question: **REQUEST (for the coordinator's batching):** one
  timed-build pair on a render-bound cell, 0230 off vs on, e.g. AQF-style AutoPilot x2 each.
- **`script_ins` (L vs B; lab builds only):** MMD `script_vm` +4.5%, busy per render **+20.6%**,
  renders 236 -> 196 (the tick is saturated, so the extra cost comes out of renders). BENCH8 +0.1%.
  The gate to lab builds (0230 v2) stays justified.

## 8. METHOD: fixed-cycles DOSBox-X (`tests/harness/confs/dosbox-x-fixed25k.conf`)

What it is: the fast conf with `cycles = fixed 25000` (and `oplmode = none`). DOSBox-X then
executes a fixed number of emulated cycles per emulated millisecond, and the PIT (every clock the
engine reads) advances with emulated cycles. Host speed and host load change only how long the run
takes in wall time, not what the engine measures.

Evidence it is host-load independent (this is what makes it usable while other workers run):
the predecessor's arm-A binary (`705912d9b22b`) was run four times on MMD while other workers'
DOSBox-X runs overlapped (14:03-14:15 local, no lock) and once by me under the EXCLUSIVE lock (`COST/mmd-M-1`):
`script_vm` total_us **17801540 in all five**, `wait_next_frame` 44817-44818 us, 240 render passes
in all five. BENCH8 (`fw0ggi`, `2UBOUm` overlapped vs `COST/anim-M-1` exclusive): 1040 renders
each, `script_vm` 709373-709590 us (0.03%), `wait_next_frame` within 0.01%. Within one arm, busy
per render repeats to 0.000 ms. **Rule kept anyway:** timing figures from fixed-cycles runs are
still taken EXCLUSIVE. The evidence is n=2 fixtures and does not cover `--sb-live`.

What it is not: 486 time. DOSBox-X's dynamic core charges about one cycle per instruction and
nothing for bus traffic (a VRAM write costs what a register move costs). Fixed-cycles emulated
time is an **instruction-count proxy**, not a clock.

## 9. Recommendation on phase B (the emulator instruction count)

**Do phase B, but first as "B-lite": fixed-cycles DOSBox-X per-phase emulated time as the CPU-work
term, no DOSBox-X patch. Keep the counters' bus bytes for the bus terms.** Patch DOSBox-X only if
B-lite fails its own pre-registered validation.

Why:
- The counters failed exactly where the work is CPU, not bus: script/API work (S2M1), the 2x
  scaled copy (a CPU-bound generic path at 5.2 MB/s), audio (SB5O), per-rect/per-row present
  overhead. An instruction count sees all of that, and sees audio ISR work in whatever phase it
  interrupts. The counters were right where the work is one big block of bus traffic, which an
  instruction count cannot see. The two are complements.
- B-lite costs nothing to maintain, is deterministic (section 8), and the engine already
  brackets every phase with the clock it reads.
- **POST HOC hint, n=2, NOT a validation:** at 25000 fixed cycles, emulated busy per render is
  15.28 ms on BENCH8 anim12 against F2B1's 21.13 on the 486 (ratio **1.38**) and 104.65 ms on the MMD
  title against S2M1's 147.00 (ratio **1.40**). One is a render-bound cell and the other the
  script-bound cell the counter model missed by 10x, and the ratio is the same. Hardware
  binaries were 0194; the lab arm is the rebased tree without 0230.
- Proposed validation (to pre-register before any run): the same five cells at fixed 25000 cycles
  (SB5O with `--sb-live`, S2F2 with the xdotool walk), predicted 486 busy/render =
  k x emulated busy/render, **k calibrated on one cell named in advance**, the other four held
  out, same rank + [0.67, 1.5] criterion. Expected weak spots, stated now: bus-heavy phases
  (SB5O's 22 ms full-frame push costs about nothing in emulation) and 8-bit Mode 13h's 9.3 MB/s
  aperture, so the pre-registered form should be k x emulated + counter bus terms.
- **B-lite blind spot, stated before any run:** under DOSBox-X a `rep movsl`/`rep stosl` is
  charged about one cycle whatever its count (bwprobe.c's own note), so emulated time does not see
  bulk copies and fills at all: libc `memcpy`, the present push, the background restore's row copies.
  Those must stay priced by the counters' bytes. B-lite = k x emulated time (the CPU loops) + counter
  bus/copy bytes, never emulated time alone.

## 10. PRE-REGISTRATION: B-lite validation (approved by the coordinator 2026-09-23; written before any B-lite run)

### 10.1 Reconciliation with dosags-lab-mmd, denominators stated

| source | conf | quantity (denominator) | 486 / emulated |
|---|---|---|---|
| lab-mmd 5.1 (MMD character select, 1000 ticks) | fixed 40000, `core=normal` (`tools/dosbox-x.conf`) | `render_backbuffer`, ms per call | **1.00** (9.43 / 9.42) |
| same | same | script event, ms per tick | **2.21** (24.26 / 10.98) |
| mine, section 9 (BENCH8 anim12; MMD title to tick 1000) | fixed 25000, `core=dynamic` | whole busy, ms per render | 1.38; 1.40 |
| mine scaled x 40/25 (assumes both cores charge ~1 cycle per instruction; not verified) | ~fixed 40000 | whole busy, ms per render | 2.21; 2.24 |

These agree once the denominators are separated. MMD's busy is mostly interpreter, so its whole-busy
ratio (~2.2) is the script ratio. BENCH8's whole busy mixes tight blit work (ratio ~1.0) with engine
work (~2.2) and with bulk copies that emulation charges almost nothing for: the Mode 13h push, the
8-bit cache copy, the background row copies. **One global k cannot hold: the model has two per-kind
factors plus the counters' bus terms.** To keep lab-mmd's figures comparable, B-lite uses their conf
(fixed 40000, `core=normal`), not my 25000 dynamic conf.

### 10.2 Model (coded in `tests/harness/lab-metric-blite.py`, committed with this section)

- **R** (render-side CPU) = `render_backbuffer + scene_construct + present_update_window +
  present_blit + present_dirty_check`, tickstats totals / render passes, the same set on both sides.
- **B** = bulk-copy/bus ms per render that emulation does not charge, from the lab run's own
  steady work vector, at the probe's measured constants:
  `push_bytes x bus (LFB 27.3 / Mode 13h 9.3 MB/s) + blit1x x copy + 0.5 x blitsc x copy +
  cache x copy + bg_px x bpp x copy + fill_px x bpp x write`. The 0.5 on the scaled copy is an
  assumption (half its dst is row copies), stated now.
- **O** (everything else in busy, per steady tick) = (busy - R totals) / steady ticks.
  busy = `loop_ms - stall_ms - wait_next_frame` on both sides. A nested tick is counted once, so
  **blocking-call time is never double counted**. The `script_vm` phase, which wraps nested ticks,
  is **not used**.
- **Calibration, one cell named in advance: S2M1.** `k_R = (hw R - B) / lab R`, `k_O = hw O / lab O`.
  Expected from lab-mmd: k_R ~ 1.0, k_O ~ 2.2. If either differs by more than 25%, that is reported
  as a reconciliation miss (not a void).
- **Prediction:** `busy/render = k_R x lab R + B + k_O x lab O x (hw steady ticks / hw renders)`.
- **Held out:** F2B1, S2F2, AQF1, SB5O.

### 10.3 Pass criterion (fixed now)

**PASS iff** the five predicted busy/render rank exactly as measured (S2F2 < AQF1 < F2B1 < S2M1 <
SB5O) **and** all four held-out predicted/measured ratios lie in **[0.67, 1.5]**. Reported beside
it, not part of the verdict: per-kind held-out error (predicted R per render and O per tick against
the 486's), and the factor-2 band.

### 10.4 Runs

`tests/harness/results/BLITE-2026-09-24/blite.sh`. One EXCLUSIVE lock per cell (others interleave
between cells). Binary `build/lab/B2` (0230 timed build `640060d25f24`: the work vector without the
script-instruction increment, which would inflate emulated interpreter time by about 20%).
`--fixed-timestep --no-verify-present`. Configs are those of the section-4 lab runs (`cfg/`).
SB5O runs with `confs/dosbox-x-fixed40k-opl3.conf` and `--sb-live`, with START clicked 68.2 s after
`event=ready room=2`. Interactive runs are stopped by their own driver once their manifest is complete.
**VOID a cell if:** `exit_code != 0`; no `work scope=steady` line; S2F2 gets fewer than 40 walk clicks;
SB5O does not reach room 99, or reaches it more than 10% away from the 486's tick 3781 (then it is
re-run once, with the click delay rescaled by the observed ticks per wall second).
Hardware binaries were 0194/0196/0208; the lab binary is the rebased tree (0209 + 0230). The
difference is audio/MIDI and counters, not render or script code. Stated, not corrected for.

## 11. B-lite RESULT: **PASS** (section 10.3, scored exactly as written)

Scorer `tests/harness/lab-metric-blite.py` (committed with the pre-registration, unchanged) ->
`results/BLITE-2026-09-24/blite-results.json`. Lab runs `results/BLITE-2026-09-24/<cell>/`
(binary `build/lab/B2`, fixed 40000 `core=normal`, one EXCLUSIVE lock per cell).

**Calibration (S2M1):** k_R = **1.132**, k_O = **2.311**. lab-mmd's figures were 1.00 and 2.21; both
are within the pre-registered 25%, so the reconciliation holds.

| cell | measured busy/render | predicted | ratio | R per render, pred / 486 | O per tick, pred / 486 |
|---|---|---|---|---|---|
| S2F2 | 10.53 | 7.71 | **0.73** | 3.86 / 5.61 | 3.80 / 4.87 |
| AQF1 | 17.82 | 13.78 | **0.77** | 13.67 / 15.53 | 0.09 / 2.10 |
| F2B1 | 21.13 | 16.82 | **0.80** | 11.85 / 15.21 | 4.97 / 5.92 |
| S2M1 | 147.00 | 147.00 | 1.00 (calibration) | -- | -- |
| SB5O | 217.22 | 291.81 | **1.34** | 181.79 / 147.11 | 18.30 / 11.66 |

- **Rank:** predicted S2F2 < AQF1 < F2B1 < S2M1 < SB5O = measured. **Scale:** all four held out in
  [0.67, 1.5]. **VERDICT: PASS.** (Factor 2, informational: also within.)
- **Bias, stated:** the three render-bound cells are all under-predicted, by 20-27%. On the render
  side (R) the held-out ratios are 0.69-0.88 there, so k_R from S2M1 (1.13) is low for them.
  SB5O is over-predicted by 34%, on both sides (R 1.24, O 1.57). SB5O carries sound (OPL3 ISR +
  SB PCM) and the 2x scaled copy, whose B term uses the pre-registered 0.5 x copy assumption.
- **O on AQF1 is not predicted** (0.09 vs 2.10 ms per tick): its emulated non-render time per tick
  is almost nothing. It matters little to AQF1's total (R dominates), but it means the O term is
  unvalidated for render-bound cells.
- **Void attempt recorded:** SB5O's first B-lite run reached room 99 at tick ~3158 (-16.5% against
  3781; the emulated game ran 29.8 ticks per wall second at fixed 40k, not 40). It was voided under
  10.4 and re-run once with the click delay rescaled (68.2 -> 88.4 s): room 99 at tick ~3747
  (-0.9%). The void run is kept in `SB5O-VOID1-room99-tick3158/`.

**What B-lite may be trusted for (and no further):**
- ranking candidate changes;
- busy per render within about -30% / +35% absolute on fixtures like these five;
- per-kind terms taken from fixed-cycles emulated time (render CPU at k_R ~1.1, everything
  else at k_O ~2.3) plus counter bytes for bulk copies.

A render-bound fixture is predicted about 25% low. It is n=5 with one calibration cell and is not
validated at 32 bpp or for 24-bpp packing. Every S32 use of it is labelled a screen.
