# LAB-L1R -- lever L1 built in the lab (DOSAGS_ROUTE_PREWARM): exact on every gate; the first room click after the restore drops from 63 to 4 ms of route search, the first room-2 click from 187 to 17 ms (lab worktree ~/git/dosags-lab-rb, branch lab-rb)

Lab only: base main 478b8f21 (ags 0001-0369) + lever + overlay, nothing landed, no rig, nothing pushed. DOSBox-X fixed-40000
emulated time throughout. Pre-registration committed before any lever data: docs/lab/l1r-lab/PREREG.md (lab-rb d35412b5).
Design: docs/lab/LAB-RB.md sections 3.2, 5 (L1) and 7.

## 0. Answer first

- **Built.** DOSAGS_ROUTE_PREWARM: unset/0 = off, 1 = on. One edit script (l1r-lab/lever-l1r.py) over 0001-0369, 6 files,
  +113 / -0, all under `__DJGPP__`; diff l1r-lab/lab-l1r.diff. Cost: +3,073 bytes instrumented, +2,561 release.
- **What it does.** When the FadeIn event is processed (after a new room's BeforeFadein event, and after a save restore;
  inside the stall tick, screen still faded out) it prepares the walkable mask for the player (prepare_walkable_areas,
  as move_character_impl does) and calls the legacy finder's **unchanged** is_route_possible() once on it, source =
  destination = the first walkable pixel. That runs exactly the 0211 analysis + 0319 labels the first request would run
  and records the same mask serial. The request path is untouched: every request still matches the cache by serial or
  byte compare, or rebuilds it.
- **Exact.**
  - G1 frames: FHASH + PRESENT_VERIFY on vs off EQUAL on every loop counter of G (3164), V (3964), GCL (7004), H (7004),
    intro (1299) and AQ (3558); stale px 0 everywhere.
  - G2 release game lines: on vs off **EQUAL** on 5 Days room 3 (30), Trilby room 35 (1121) and AGS Quest (356; parse-results
    PASS both).
- **The gate sees a wrong cache.** C1, a stale warm (built from a mask with a block cut out around the player, stamped
  with the live serial): **DIFF 6285/7004** from lc 6155. Every route then fails (nodes 0) and Dave never leaves room 1.
- **Mask change after the warm still invalidates.** F1 draws a 10x9 unwalkable block on the walkable mask and bumps the
  mask generation right after the warm, in both arms. On vs off is **EQUAL 7004/7004**, and the first request after the
  warm rebuilt (first_miss 1). The forcing changes the game (F1-0 vs H-0 DIFF 5078 from lc 7362), so this is a real
  test. F1-N, the same with the cache re-stamped (guard defeated): **DIFF 5124/7004** from lc 7316. So the
  validation is what makes F1 EQUAL.
- **Timing (information; H, --fixed-timestep, fine on).**
  - First room click after the restore (6154): FindRoute 63.4 -> **4.2 ms**, tick 116.5 -> 56.5.
  - First room-2 click (7895): FindRoute 187.2 -> **16.8 ms**, tick 205.0 -> 34.0.
  - Both first requests are serial hits (first_serial 2, first_miss 0).
  - The faded-out gap (load_end -> fadein_begin) grows by +66 ms on the restore and +184 ms on the room-2 load (the warm's
    own time: 63.6 and 181.6 ms).
  - Skips: entry window 5 -> **0**; whole run 22 -> 13.
- **Against the pre-registration.** Every gate met. Timing met except one bar: 7895 <= 15 ms predicted, 15.5 ms measured
  (rbroute bracket) or 16.8 (rbslow path bracket). That misses the prediction, inside the 30 ms falsifier: reported as
  missed, not falsified. The remaining 7 ms of that search is the labels' nearest-walkable sweep for the unwalkable target
  (925,69) on the 960-wide mask: endpoint work, not the cache.
- **Coverage notes.**
  - AGS Quest is a >= 3.5.0 game, so its pathfinder is JPS and the warm is a no-op (skipped 9, one per FadeIn).
  - The intro warms twice but never asks for a route (first_none 1, pending 1). V's walks are all direct (can_see_from),
    so V never reaches is_route_possible after a warm.
  - G and GCL ask once after a warm (room 2), H twice (restore and room 2).

## 1. Setup

- Same worktree as LAB-RB (main 478b8f21; main's flavours byte-identical to RDINS / RDREL, LAB-RB section 1).
- Builds (l1r-lab/build-l1r.sh, build-gate.sh):

| exe | what | sha256 | bytes |
|---|---|---|---|
| L1RINS | 0001-0369 + lever, instrumented | fce4861d6ad790951f45e3157078e2d9fda5536c78f08c99bf4b003ee5098fa5 | 8,698,670 |
| L1RREL | 0001-0369 + lever, release (G2 cells) | 91e63265d0ff3d4d47300592963034a71707f58db79d045cb52b4a80b37c5c85 | 8,660,528 |
| L1RGATE | lever + gate overlay, instrumented (G1, C1, F1 cells) | 9a9c7b1643639fe5040e36907caec495dd13b6f13b3d5c098dbbd7fc44c51152 | 8,724,733 |
| L1RGATE v0 | the same without the G/V presets (T1 timing pair only) | fd715c13b407c202d735ad0308614bae14d20cdac9363c56525b47a66dbb04b1 | -- |

All are build_dirty=1 lab builds, none for the rig.
- Gate overlay (l1r-lab/apply-overlay-l1r.py; full diff l1r-lab/lab-l1r-gate-full.diff) is LAB-RB's overlay plus:
  - the G / V click presets (LAB-R2B's spelling of R3LAND's fixtures);
  - the knobs DOSAGS_LAB_RPW_STALE (C1), DOSAGS_LAB_RPW_MASKCHG (F1, both arms) and DOSAGS_LAB_RPW_NOGUARD (F1-N).
- **One mistake, caught before scoring.** The first gate chain ran G-0 / V-0 on L1RGATE v0, whose overlay had no G / V
  presets, so those two cells had no clicks (labclicks "-", no route requests). The chain was stopped, the presets
  added, the exe rebuilt, and every G1 / C1 / F1 / G2 cell re-run on 9a9c7b16. The v0 cells are deleted and not scored.
  The T1 pair (both arms on v0, H fixture, whose preset v0 had) stands.
- Cells (l1r-lab/lib.sh, chainT.sh, chainG.sh): conf dosbox-x-fixed40k-opl3, ACSETUP-ON-512X384-ROUND, save 007,
  DOSAGS_RANDSEED=1, **DOSAGS_CHAR_REUSE=2 in every arm** (the next round's configuration). G1 / C1 / F1: every tick
  rendered (no --fixed-timestep), fine timing off, FRAMEHASH + PRESENT_VERIFY. G2: LAB-R2B lane D's release lines.
  Display 398 only, one DOSBox-X at a time, waits via tools/waitfor.sh with pid files; stage dirs deleted (the one
  interrupted cell's stage dir and DOSBox-X were stopped and removed by hand).
- Witnesses (tables/cellcheck.txt): `DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=(default) mode=0` / `=1 mode=1`, the
  guiclip `(default) mode=4` and charreuse `2 mode=2` lines, and labclicks n=14/14/16/14 (G/V/GCL/H) in every cell. All
  cells rc 0, exit_code=0.

## 2. The lever (l1r-lab/lever-l1r.py)

| file | change |
|---|---|
| Engine/ac/route_finder.h | `virtual bool MaskRouteFinder::DosPrewarm(const Bitmap *mask)`, default `false` (JPS keeps no such cache) |
| Engine/ac/route_finder_impl_legacy.h | the override's declaration |
| Engine/ac/route_finder_impl_legacy.cpp | `LegacyRouteFinder::DosPrewarm`: first walkable pixel, `rp_req_mask = nullptr`, `is_route_possible(mask, x, y, x, y, _pfc)`, `rp_req_mask = nullptr`, counters. Observation-only counters in is_route_possible (`rp_pw_builds++` before the cache copy; how the first call after a warm found the cache). `routeprewarm_final` after `rpcache` in dos_rp_report |
| Engine/ac/room.cpp | `dos_route_prewarm_mode()` (env read + witness, first called from init_room_pathfinder); `dos_route_prewarm()`: off -> return; no room / pathfinder -> skipped; else `room_pathfinder->DosPrewarm(prepare_walkable_areas(game.playercharacter))` |
| Engine/ac/event.cpp | `dos_route_prewarm()` in the kAGSEvent_FadeIn branch, before current_fade_in_effect() |
| Engine/main/quit.cpp | DOSAGS_ROUTE_PREWARM joins the RUNMANIFEST env allowlist (after DOSAGS_PRESENT_VERIFY) |

- **Exactness argument (the gates are the evidence).**
  - The warm calls the same function the first request calls, on the same bitmap (walkable_areas_temp, prepared for the
    same character from the same inputs, so the same pixels and the same 0319 serial).
  - Its outputs are a function of the mask's pixels and MaxGranularity only: walk_area_granularity[], the normalised
    copy, the labels and the serial.
  - Its side effects on request state: rp_req_mask, which FindRouteImpl clears at every request start and the warm
    clears too; suggestx/suggesty and walk_area_granularity[], which every request rewrites before reading.
  - When the request's mask differs (a character moved, a script changed walkable areas, a DrawingSurface), the
    unchanged validation compares and rebuilds: F1.
- RUNMANI line, both flavours: `DOS-PORT routeprewarm_final mode= prewarms= built= matched= nowalk= skipped= us= max_us=
  first_serial= first_compare= first_miss= first_none= pending=`. Its fields:
  - first_*: how the first is_route_possible after each warm found the cache;
  - first_none: a warm superseded before any request;
  - pending: the last warm never asked;
  - skipped: FadeIns with no legacy pathfinder or no room.

## 3. Gates (L1RGATE; tables/fhcmp.txt, cellcheck.txt, knobs-pv.txt)

| fixture | off vs on (FHASH by loop counter) | PV stale (off; on) | routeprewarm_final (on) |
|---|---|---|---|
| G | **EQUAL 3164/3164** | 0; 0 | prewarms 2, built 2; first_serial 1, first_none 1 |
| V | **EQUAL 3964/3964** | 0; 0 | prewarms 2, built 2; first_none 1, pending 1 (no request reaches the cache) |
| GCL | **EQUAL 7004/7004** | 0; 0 | prewarms 2, built 2; first_serial 1, first_none 1 |
| H | **EQUAL 7004/7004** | 0; 0 | prewarms 2, built 2; **first_serial 2** |
| intro (startr 40) | **EQUAL 1299/1299** | 0; 0 | prewarms 2, built 2; first_none 1, pending 1 |
| AQ (AutoPilot) | **EQUAL 3558/3558** | 0; 0 | prewarms 0, **skipped 9** (JPS pathfinder) |

| control / guard | pair | result | counters |
|---|---|---|---|
| C1 stale warm (STALE=1, on) | H-0 vs C1-1 | **DIFF 6285/7004**, first lc 6155 | first_serial 1: the stale cache served the 6154 request; routes fail (nodes 0, 0.41 s / 1.23 s requests), Dave never moves, no room change |
| F1 mask change after the warm (MASKCHG=1) | F1-0 vs F1-1 | **EQUAL 7004/7004** | on: first_miss 1 (rebuilt); the forcing itself changes the game: H-0 vs F1-0 DIFF 5078 from lc 7362 (Dave stopped by the block; no room change, so one warm) |
| F1-N guard defeated (MASKCHG + NOGUARD, on) | F1-0 vs F1-N | **DIFF 5124/7004**, first lc 7316 | first_serial 1: the pre-change cache, re-stamped, served the first request; game lines DIFF (Dave's walk to the exit starts from 311,135 instead of 175,135) |

## 4. Release game lines (L1RREL; tables/eqcmp.txt)

| pair | game lines | routeprewarm_final (on) | note |
|---|---|---|---|
| RG-5D3S-0 vs -1 (5 Days, startr 3, exit 3000) | **EQUAL (30)** | prewarms 1, built 1, pending 1 | the warm ran (62.8 ms at 40k); no walk request followed |
| RG-TN35-0 vs -1 (Trilby, startr 35, MSGSKIP) | **EQUAL (1121)** | nowalk 1, skipped 1 | room 35's mask has no walkable pixel: the warm returns, as a request would |
| RG-AQ-0 vs -1 (AGS Quest AutoPilot) | **EQUAL (356)**; parse-results PASS both | skipped 9 | JPS pathfinder (>= 3.5.0 game): DosPrewarm is the no-op default |

Present counts (fixed timestep, wall-clock paced): 5 Days 902 / 902, Trilby 1665 / 1665, AQ 3874 / 3873. That is a 1-frame
render-count difference in AQ, with identical game lines; it is pacing noise between two runs of a skipping loop, not
the lever (AQ never calls it).

## 5. Timing (information; L1RGATE v0, H, --fixed-timestep, fine timing on, TICKLOG; tables/timing.txt)

| | off (T-H-0) | on (T-H-1) |
|---|---|---|
| 6154 first room click after restore: FindRoute (is_route_possible) | 63.4 ms (58.9) | **4.2** (below the 5 ms rbroute line) |
| 6154 tick | 116.5 | 56.5 (rest: script + the lab click injection's 22 ms input poll, LAB-RB 3.2) |
| 7895 first room-2 click: FindRoute (is_route_possible) | 187.2 (177.1) | **16.8** (7.0: the labels' nearest-walkable sweep) |
| 7895 tick | 205.0 | 34.0 |
| warm time (routeprewarm_final us) | -- | 63.6 restore + 181.6 room 2 = 245.1 |
| restore tick 5436 ugo / faded-out gap load_end -> fadein_begin | 1559.3 / 382 ms | 1624.2 (+64.9) / 448 (+66) |
| room-2 load tick 7711 ugo / gap | 2405.9 / 174 ms | 2540.2 (+134.3) / 358 (+184) |
| skips: restore / room 1 / entry / room 2 / late / all | 5 / 12 / 5 / 0 / 0 / 22 | 5 / 8 / **0** / 0 / 0 / 13 |
| game lines | -- | EQUAL (48) |

- Warm-cache clicks are unchanged (6409 18.9 / 18.9 ms, 7315 74.5 / 74.5): the lever only removes the cold build.
- The warm adds its own time to the faded-out part of each room entry. Lab: +66 / +184 ms. 486 estimate from RDMP's first
  clicks (logic 233 / 370 ms, most of it this build): about +150 to +340 ms of black screen per room entry or restore.
  That is player-visible as a slightly longer black frame. It runs even in rooms where the player never walks (intro:
  two warms, no request).

## 6. Landing note (not landed; 0370 lands first, so the slot is likely 0371)

- **Patch:** `patches/ags/0371-DOS-PORT-patch-0371-route-cache-pre-warm-in-the-room-load-restore-stall-DOSAGS_ROUTE_PREWARM-default-off.patch`,
  the six files of section 2 exactly (l1r-lab/lab-l1r.diff, ASCII, all under `__DJGPP__`), with "lab L1R" comments
  renamed to "patch 0371".
- **Touches:** the route-finder interface (one virtual with a no-op default), the legacy finder (one method + counters;
  is_route_possible gains three observation-only counter lines and no logic change), room.cpp (mode/witness + the call
  helper), event.cpp (one call in the FadeIn branch), quit.cpp (allowlist).
- **Does not touch:** the request path, walkablearea.cpp, the JPS finder, any script API, the render path.
- **Default:** off (env toggle for the ABBA round); flip only after the 486 round.
- **Interactions:** DOSAGS_RP_FAST=0 still works (the warm then builds only 0211's analysis); with RP_VERIFY=1 the warm's
  own call is also verified.
- **Gates to re-run on the port-patch commit (clean builds):** this G1 set, C1 / F1 / F1-N with the overlay re-applied,
  G2, the ratchet (+2.5 KB release), P9 equivalence.
- **Round:** LAB-RB section 7's draft stands (per pair -6 skips, band 3-9, in room 1 + entry; +0.09 points; mechanism
  bars 80 / 100 ms). Its MP bar for the first room-2 click (<= 100 ms logic on the 486) is consistent with the lab's
  34 ms tick.

## 7. Warm cost on the 5 Days gate scenes, and the predicted 486 whole-run change (added after review)

Cells (l1r-lab/chainW.sh; L1RREL, fixed 40k, exit 5000), off vs DOSAGS_ROUTE_PREWARM=1:
- S16 = GR16 / RDS16's line: --startr 3, ACSETUP-ON-512X384-ROUND, DOSAGS_CHAR_REUSE=2.
- S32P = round WB's line: S32P-ACSETUP-ON.CFG, DOSAGS_FORCE_COLOR_DEPTH=32, DOSAGS_MAX_SCALE=1, SDL_DOS_PACK24=1.

| scene | warm (routeprewarm_final us) | faded-out gap load_end -> fadein_begin (off -> on) | lab whole-run tick_rate (off -> on) |
|---|---|---|---|
| S16 | **62.8 ms** (one warm, room 3; labels 8.5 of it) | 9 -> 72 ms | 39.24 -> 39.23 (stall_ms 1629 -> 1692) |
| S32P | **63.1 ms** (labels 8.5) | 9 -> 74 ms | 23.03 -> 23.02 (not meaningful: 40k cannot pace 32-bit 640x480) |

- The warm works on the room's 8-bit walkable mask, so colour depth and resolution do not change it (62.8 vs 63.1).
- In the lab, 5 Days makes no route request in 5000 ticks: rpcache fast=-1 off, the warm pending on. The rig cells' host
  clicks do: RDS16 and WBA1/WBA2 show one cold build (compares=1) and 7-14 serial hits.
- These lines set no DOSAGS_RANDSEED (as on the rig), so their game lines differ between any two runs in the random
  sound picked ("Playing sound 3/9/10"). That is not the lever: the seeded G2 cells are EQUAL.

**Lab-to-486 factor (same work, different scale):**

| work | 486 | lab | factor |
|---|---|---|---|
| label build alone, 5 Days room 3 | 10.41-10.42 ms (RDS16, WBA1, WBA2 label_us) | 8.48-8.51 (W-*-1) | **1.22-1.23** |
| label build alone, MMD room 2 | 29.62-30.06 ms (RDA1, RDB1, RDB2, RDMP) | 24.53 (T-H-0, H-0) | **1.21-1.23** |
| whole cold-click tick 7895 (build + click) | 374.3 (RDMP) | 205.0 (T-H-0) | 1.83 |
| whole cold-click tick 6154 | 236.8 (RDMP) | 116.5 (T-H-0); 94.0 without the lab's 22.5 ms click-injection input poll | 2.03 (2.52) |
| build alone, from 7895: 486 tick minus the on-arm residual 34.0 ms x 2.2 | 299.5 | 171.0 (off - on) | **1.75** |
| build alone, from 6154: same, the residual without the injection artefact | 162.0 | 60.0 (off - on) | 2.70 |

- The labels scale tightly (1.22). The whole build scales 1.75-2.7, central **1.8**, taken from 7895 because 6154 is
  confounded by the lab injection artefact.
- The 2.2 residual ratio is an ordinary room-2 tick's busy time, 486 vs lab (~22 vs ~10 ms), an assumption.
- Factor band used below: **1.22 (all work scales like the labels) to 2.7**.
- **Predicted 486 warm on 5 Days room 3: 62.9 ms x 1.22-2.7 = 77-170 ms, central 113 ms.**

**Predicted 486 whole-run tick_rate change.** Whole-run = ticks / run time, with the first room load inside the run.
- On: the warm adds W to the room-3 load, before the first tick, and nothing repays it.
- Off: the same build lands in the first host click's tick. The fixed-step loop then repays up to MAX_CATCHUP = 5 ticks
  (125 ms) of it, so it costs wall time only beyond 125 ms.
- So the on - off run-time difference is min(W, 125 ms) = 77-125 ms. This assumes the rig's first click pays the cold
  build in the off arm, as RDS16 / WBA1-2's compares=1 show.

| scene | baseline (486) | run time | predicted change | predicted whole-run | floor margin |
|---|---|---|---|---|---|
| S16 | 39.34 (RDS16, 4,999 ticks) | 127.1 s | **-0.024 to -0.039 (central -0.035)** | **39.30-39.32** | +0.10-0.12 |
| S32P | 39.38-39.39 (WBA1 / WBA2); 39.30 (round V S32FF1) | ~127 s | -0.024 to -0.039 | 39.34-39.37 (from 39.38); 39.26-39.28 (from 39.30) | +0.06 at the low baseline |

- Steady tick_rate: on, the warm sits inside the excluded stall tick. Off, the 77-170 ms click tick (< 250 ms) is counted
  in steady, so on reads about +0.03 higher steady: information only.
- The S32P whole-run figure has ~0.1-0.2 of day-to-day start-up noise around 39.2 (round CF's note). A -0.04 shift is
  inside that noise, but it is not nothing at the low baseline. If the gate registration wants margin, run S16 / S32P in
  the round's off arm too, or exempt the warm from the whole-run figure (it is a start-up cost, like preloop).
- Files: l1r-lab/chainW.sh; cells/W-S16-{0,1}, W-S32P-{0,1}.

## 8. Files

- l1r-lab/PREREG.md (pre-registration), lever-l1r.py, lab-l1r.diff (vendor/ags, lever only, over 0001-0369),
  apply-overlay-l1r.py, lab-l1r-gate-full.diff (lever + overlay).
- Scripts: build-l1r.sh, build-gate.sh, lib.sh, cell.sh, pcell.sh, chainT.sh, chainG.sh, gates.sh.
- Tools: cellcheck.py (+ routeprewarm fields), fhcmp.py, eqcmp.py.
- Records: l1r-lab/cells/<TAG>/{CELL.txt, RUN.BAT, RUNMANI.LOG, FHASH.TXT, LABLINES.TXT}.
- Tables: l1r-lab/tables/{fhcmp, eqcmp, cellcheck, knobs-pv, timing}.txt.
- Not committed: exes, TICKS.BIN, STDOUT.TXT (game text), saves. The vendor/ags working tree holds the lever only
  (byte-equal to lab-l1r.diff).
