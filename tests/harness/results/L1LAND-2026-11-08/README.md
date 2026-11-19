# L1LAND-2026-11-08 -- landing records for ags 0371 (lever L1, DOSAGS_ROUTE_PREWARM, default off)

DOSBox-X only (cycles=fixed 40000, tests/harness/confs/dosbox-x-fixed40k-opl3.conf); no rig, no vcctrl. Text records
only: frame digests (FHASH.TXT), RUNMANI.LOGs, the game-output lines each equivalence read (GAMELINES.TXT),
parse-results JSON, the cell command lines (CELL.txt, stage dir masked), the overlay and its apply scripts, the lane and
build scripts, the compare tools, the compare output (tables/), the ratchet reports. No images, no game data. Lever
design and lab numbers: docs/lab/LAB-L1R.md (its cells in docs/lab/l1r-lab/cells), docs/lab/LAB-RB.md sections 3.2, 5
and 7. Cells ran 2026-11-08 15:07 to 16:58 PST.

## 0. Answer first

- **0371 = LAB-L1R's lever, unchanged in code.** lab-l1r.diff applied as is to 0370. Two kinds of change:
  - its "lab L1R" comments now read "patch 0371" (13 places), and the mode comment says what other values do;
  - `#ifdef __DJGPP__` guards around the lever's counters in route_finder_impl_legacy.cpp. The lab note said all of
    the lever was under `__DJGPP__`; those lines were not (section 2).
  - With the renames and guard lines removed, the added lines equal lab-l1r.diff's line for line.
- **DOSAGS_ROUTE_PREWARM:** unset or "0" = off (the default); exactly "1" = on; **any other value = off** ("on", "2",
  "yes"). It is opt-in, so a mistyped value fails toward the default. Witnessed: I-Xon and I-X2 print mode=0, run no
  warm, and are frame-EQUAL to the off arm.
- **Gate 1, off vs on, R2 at its 0370 default in both arms: frame-EQUAL on all six fixtures:** G 3164, V 3964, GCL
  7004, H 7004, intro 1299 and AQ 3558 loop counters. PRESENT_VERIFY stale 0 everywhere. Whether the warm was exercised,
  per fixture:

  | fixture | warms | first request after a warm |
  |---|---|---|
  | H | 2 | 2 serial hits (restore and room 2) |
  | G, GCL | 2 | 1 serial hit (room 2); the restore warm was superseded before any request |
  | V, intro | 2 | none: no request reaches the cache |
  | AQ | 0 | 9 FadeIns skipped: JPS pathfinder |

- **Every gate cell is also frame-EQUAL to LAB-L1R's own cell for the same fixture and arm** (16 cells: the 12
  gate-1 cells plus C1, F1-0, F1-1 and F1-N). The lab set DOSAGS_CHAR_REUSE=2; here R2 runs by default. The off
  arms are also frame-EQUAL to 0370's default (R2DEF's D arms) on G, V, GCL, intro and AQ.
- **LAB-L1R's controls, overlay re-applied:**
  - C1, a stale warm: **DIFF 6285/7004** from lc 6155;
  - F1, the mask changed after the warm: on vs off **EQUAL 7004/7004** (the first request rebuilt: first_miss 1);
  - F1-N, the guard defeated: **DIFF 5124/7004** from lc 7316;
  - the forcing is real: F1-0 vs H-0 DIFF 5078 from lc 7362.
  - Every count equals LAB-L1R's.
- **Release game lines, on vs off: EQUAL** on 5 Days room 3 (30), Trilby room 35 (1121) and AGS Quest (356);
  parse-results PASS both.
- **P9:** 0371 unset vs 0370's release (9db4170acd89) unset: **EQUAL (78)**.
- **Builds:** both flavours clean (build_dirty=0) and byte-identical across two full clean builds. +3,073 bytes
  instrumented and +2,561 release over 0370, as the lab measured.
- **Ratchet:** only exe-bytes (+3,073) and code-lock-bytes (+1,440) fail, as expected; proposed exact limits
  8,698,670 / 5,222,512 (section 8). Every screen-alias check passes.

## 1. Binaries (worktree ~/git/dosags-l1land, branch l1land off main 4ee5b017 = 0370 landed; patches/ags/0371)

| exe | what | sha256 | binary_sha12 | build_dirty | bytes |
|---|---|---|---|---|---|
| L1INS | 0001-0371, instrumented | e88b5f3209ba36d46995202f724710dbaee272a1427e2ce3c07b12378421f053 | 6198d2e06b8d | 0 | 8,698,670 |
| L1REL | 0001-0371, release | aee2aff6022e1001c8b34b1def86a8ef8ccaf31788f9312c255f14e976b61708 | a6aaab93c3d2 | 0 | 8,660,528 |
| R2DREL | 0370's release (R2DEF's R2DREL, = main's), P9 reference | f9202de6ffc795000b32b55138424a97038fe49f8010b1d238ccd0697fd240e1 | 9db4170acd89 | 0 | 8,657,967 |
| L1GATE | 0001-0371 + gate-overlay.diff, instrumented (lab only) | c2e43af77d68eb93d4d55bd3d8e24bdb8709eece6c9c4b1c48c16ee84c73541a | 0569be349c76 | 1 | 8,725,245 |

- **Base.** The lead named r2def's 2378b86b. By the time this started, main held the same 0370 as 2583aea0 /
  4ee5b017; the only difference was the LAB-RB and LAB-L1R lab docs (patches, README.TXT, ratchet.yaml and the R2DEF
  records are identical). l1land was moved onto main before its first commit, so it carries the lab records this
  README compares against.
- **Vendor tree.** `make patches` from the committed series gave vendor/ags tree b85e9e56, the same tree as the
  authoring commit.
- **Build A / build B.** Build A was the first build in the fresh worktree. Build B removed build/ags and
  build/ags-release and rebuilt both flavours: `cmp` L1INS-A L1INS-B and L1REL-A L1REL-B both 0.
- **Stamps.** From `make build-dirty` / `DOSAGS_RELEASE=1 make build-dirty`, and from every release cell's RUNMANI.LOG
  (binary_sha12=a6aaab93c3d2 build_dirty=0).
- **Against 0370** (27a296a5b589 / 9db4170acd89, 8,695,597 / 8,657,967): **+3,073 bytes instrumented, +2,561 release.**
  LAB-L1R measured the same sizes over 0369; 0370 added no bytes.

## 2. The lever (deliverable b)

| file | change |
|---|---|
| Engine/ac/route_finder.h | `virtual bool MaskRouteFinder::DosPrewarm(const Bitmap *mask)`, default `false` (JPS keeps no such cache) |
| Engine/ac/route_finder_impl_legacy.h | the override's declaration |
| Engine/ac/route_finder_impl_legacy.cpp | `LegacyRouteFinder::DosPrewarm`: first walkable pixel, `rp_req_mask = nullptr`, `is_route_possible(mask, x, y, x, y, _pfc)`, `rp_req_mask = nullptr`, counters. Observation-only counters in is_route_possible. `routeprewarm_final` after `rpcache` in dos_rp_report |
| Engine/ac/room.cpp | `dos_route_prewarm_mode()` (the one getenv + the witness, first called from init_room_pathfinder); `dos_route_prewarm()`: off -> return; no room / pathfinder -> skipped; else `room_pathfinder->DosPrewarm(prepare_walkable_areas(game.playercharacter))` |
| Engine/ac/event.cpp | `dos_route_prewarm()` in the kAGSEvent_FadeIn branch, before current_fade_in_effect() |
| Engine/main/quit.cpp | DOSAGS_ROUTE_PREWARM joins the RUNMANIFEST env allowlist (after DOSAGS_PRESENT_VERIFY) |

- **Modes.**

  | DOSAGS_ROUTE_PREWARM | mode | witness |
  |---|---|---|
  | unset | 0, off (the 0370 head) | `DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=(default) mode=0` |
  | exactly "1" | 1, on | `...=1 mode=1` |
  | anything else ("0", "on", "2", "yes", "01") | 0, off | `...=<v> mode=0` |

  The witness prints the value as set. LAB-L1R's `e ? e : "(default)"` is kept, so an empty value (which DOS's `SET X=`
  never produces; it removes the variable) would print as empty.
- **RUNMANI line, both flavours** (present in every 0371 cell, both flavours): `DOS-PORT routeprewarm_final mode=
  prewarms= built= matched= nowalk= skipped= us= max_us= first_serial= first_compare= first_miss= first_none=
  pending=`.
- **Lab knobs:** none in 0371. The STALE / MASKCHG / NOGUARD knobs live only in the gate overlay (section 3).
- **docs/dist/README.TXT is unchanged:** L1 is off by default.
- **What changed against lab-l1r.diff:**
  - The 13 "DOS-PORT lab L1R" / "lab L1R" comments read "patch 0371".
  - The mode comment in room.cpp now says: unset/0 = off, exactly "1" = on, any other value = off, the default.
  - **`#ifdef __DJGPP__` around the lever's lines in route_finder_impl_legacy.cpp**, in six places: the extern
    declarations and counter statics, the routeprewarm_final fprintf, `pw_by_serial`'s declaration and assignment, the
    first-request block, and `rp_pw_builds++`.
    - Why: LAB-L1R section 0 says the lever is all under `__DJGPP__`; in that file it was not. The file's older DOS-PORT
      cache code (0211 / 0317 / 0319) is built on every platform. On a non-DOS build the lever's lines would reference
      dos_route_prewarm_mode() and dos_route_prewarm_skipped, which exist only under `__DJGPP__` in room.cpp: a link
      error.
    - It is the same class of fix as 0370's dos_cr_wb_gen guard. On DOS it changes nothing: the cells here are
      frame-EQUAL to LAB-L1R's.
  - Result: 6 files, +126 / -0, against the lab's +113.
- **Constraints.** ASCII only (checked on the patch and every record). One getenv. binary fopen and size_t are
  untouched (the lever opens no file).

## 3. The overlay (LAB-L1R's, anchors renamed; gate-overlay.diff is the full vendor/ags diff over 0371)

- apply-overlay-l1land.py is LAB-L1R's apply-overlay-l1r.py with two edits, and nothing else changed:
  - its four anchors renamed from "DOS-PORT lab L1R" to "DOS-PORT patch 0371";
  - LAB-RB's apply-overlay-rb.py looked up in the same directory.
- The chain it runs is the same as the lab's: apply-overlay-rb.py and apply-overlay-r3land.py, both byte-identical to
  the committed copies.
- It is applied, built and reverted (build-gate.sh), never landed.
- Knobs used here:
  - FRAMEHASH;
  - LABCLICKS G / V / GCL / H;
  - DOSAGS_LAB_RPW_STALE=1 (C1: the warm builds from a copy of the mask with a 41x13 block around the player cut out,
    stamped with the live serial);
  - DOSAGS_LAB_RPW_MASKCHG=1 (F1, both arms: a 10x9 unwalkable block left of the player right after the warm point,
    and dos_walkmask_gen bumped);
  - DOSAGS_LAB_RPW_NOGUARD=1 (F1-N: the cache re-stamped with the new mask's serial).

## 4. Fixtures, arms, witnesses

- **Fixtures** (MMD = Maniac Mansion Deluxe; save 007 restored unless noted):
  - G (exit 8600; 3164 loop counters), V (exit 9400; 3964), GCL (exit 12440; 7004), H (LAB-RB's H clicks, exit 12440;
    7004);
  - intro (--startr 40, no save, exit 1300; 1299);
  - AQ (AGS Quest AutoPilot; 3558).
- **Gate cells:** no --fixed-timestep (every tick rendered), fine timing off, no TICKLOG, DOSAGS_LAB_FRAMEHASH=1 +
  DOSAGS_PRESENT_VERIFY=1, DOSAGS_RANDSEED=1, **DOSAGS_CHAR_REUSE unset** (R2 at its 0370 default, mode 2).
- **Arms:** 0 = DOSAGS_ROUTE_PREWARM unset; 1 = =1.
- **Witnesses** (tables/cellcheck-all.txt, all 27 cells): rc 0 and exit_code=0 in each.
  - fixed-timestep: DISABLED in the 18 gate cells, ENABLED in the 9 release cells.
  - guiclip (default) mode=4 and charreuse (default) mode=2 in every cell.
  - routeprewarm: (default)/m0, 1/m1, on/m0, 2/m0 as set. P9-PREV-D (0370's binary) has none, as expected.
  - labclicks n=14 (G, V, H, C1, F1-*) / 16 (GCL). RUN.BAT SET totals 119-316 bytes, longest line 38.
  - PRESENT_VERIFY stale frames 0 in every gate cell.
- **Stage dirs and displays.** Stage dirs were deleted per cell. Displays 396/397 only (the lab agent used 398), at most
  two DOSBox-X of this worktree at once.

Compare, in this directory: `python3 fhcmp.py H-0.FHASH.TXT H-1.FHASH.TXT`; `python3 eqcmp.py P9-PREV-D.GAMELINES.TXT
P9-REL-0.GAMELINES.TXT`. tables/ holds the full compare output (tables.sh regenerates it from build/l1/results).

## 5. Gate 1 -- off vs on, and the warm per fixture (L1GATE)

| fixture | off vs on | = LAB-L1R's cells (off; on) | off = 0370 default (R2DEF D) | PV stale (off; on) | routeprewarm_final (on) | warm exercised? |
|---|---|---|---|---|---|---|
| G | **EQUAL 3164/3164** | EQUAL; EQUAL | EQUAL | 0; 0 | prewarms 2, built 2; first_serial 1, first_none 1 | yes: room 2's first request a serial hit; the restore warm superseded unasked |
| V | **EQUAL 3964/3964** | EQUAL; EQUAL | EQUAL | 0; 0 | prewarms 2, built 2; first_none 1, pending 1 | built, never asked: V's walks are all direct (can_see_from) |
| GCL | **EQUAL 7004/7004** | EQUAL; EQUAL | EQUAL | 0; 0 | prewarms 2, built 2; first_serial 1, first_none 1 | yes: as G |
| H | **EQUAL 7004/7004** | EQUAL; EQUAL | -- (no H in R2DEF) | 0; 0 | prewarms 2, built 2; **first_serial 2** | yes: both first requests (restore, room 2) serial hits |
| intro | **EQUAL 1299/1299** | EQUAL; EQUAL | EQUAL | 0; 0 | prewarms 2, built 2; first_none 1, pending 1 | built, never asked: no walk request |
| AQ | **EQUAL 3558/3558** | EQUAL; EQUAL | EQUAL | 0; 0 | prewarms 0, **skipped 9** | no: AGS Quest (>= 3.5.0) uses JPS; DosPrewarm is the no-op default |

- **Warm time (instrumented, 40k).** G / V / GCL / H 245.1 ms in all (max 181.6, room 2); intro 317.2 ms (max 199.8).
  The G-to-H figure equals LAB-L1R section 5's 63.6 + 181.6 = 245.1 ms.
- **The cross-checks.** "= LAB-L1R's cells" compares each cell with docs/lab/l1r-lab/cells/<same tag>/FHASH.TXT: 0369
  + lever + LAB-L1R's overlay, DOSAGS_CHAR_REUSE=2 explicit. All 12 EQUAL. "off = 0370 default" compares the off arm
  with tests/harness/results/R2DEF-2026-11-08/<fixture>-D.FHASH.TXT: 0370 + R2DEF's overlay, the default, verify on.
  All 5 EQUAL. The lever is inert when off.

## 6. Gate 2 -- LAB-L1R's controls (fixture H; L1GATE)

| control / guard | pair | result | counters (this cell) | = LAB-L1R's cell |
|---|---|---|---|---|
| C1 stale warm (STALE=1, on) | H-0 vs C1-1 | **DIFF 6285/7004**, first lc 6155 | prewarms 1, matched 1, first_serial 1: the stale cache served the first request | EQUAL 7004/7004 |
| F1 mask change after the warm (MASKCHG=1, both arms) | F1-0 vs F1-1 | **EQUAL 7004/7004** | on: prewarms 1, built 1, **first_miss 1** (the request rebuilt) | EQUAL; EQUAL |
| F1-N guard defeated (MASKCHG + NOGUARD, on) | F1-0 vs F1-N | **DIFF 5124/7004**, first lc 7316 | first_serial 1: the pre-change cache, re-stamped, served the first request | EQUAL |
| the forcing is real | H-0 vs F1-0 | DIFF 5078/7004, first lc 7362 | -- (off arm) | -- |

- **Knob actions.** "DOS-PORT labrpw lc=5436 room=1 what=maskchg px=203 py=136" in F1-0 / F1-1 / F1-N, plus
  "what=noguard" in F1-N. C1 prints "what=stale px=203 py=136 serial=1".
- **Room-2 warms in these cells.** None of the C1 / F1 cells reach room 2: the block stops Dave, and C1's routes fail.
  So each has one warm, as in LAB-L1R.

## 7. Gates 3 and 4 -- release regression and P9 (L1REL / R2DREL; game output lines, eqcmp.py; --fixed-timestep)

| pair | result | routeprewarm_final (on arm) |
|---|---|---|
| P9-REL-0 (0371, unset) vs P9-PREV-D (0370, 9db4170acd89, unset) | **EQUAL (78)** | off: 0 warms |
| P9-REL-1 (0371, =1) vs P9-REL-0 (information) | EQUAL (78) | prewarms 1, built 1, pending 1 (63.5 ms; the P9 clicks make no walk) |
| P9-PREV-D vs R2DEF's committed P9-REL-D lines (same 0370 binary, re-run) | EQUAL (78) | -- |
| RG-5D3S-1 vs -0 (5 Days room 3, exit 3000) | exit 0/0, **EQUAL (30)** | prewarms 1, built 1, pending 1 (62.8 ms) |
| RG-TN35-1 vs -0 (Trilby room 35, MSGSKIP=1) | exit 0/0, **EQUAL (1121)** | nowalk 1, skipped 1: room 35's mask has no walkable pixel |
| RG-AQ-1 vs -0 (AGS Quest AutoPilot) | exit 0/0, **EQUAL (356)**; parse-results PASS both | skipped 9 (JPS) |

Every release cell shows fixed-timestep ENABLED, guiclip (default) mode=4, charreuse (default) mode=2, and its binary's
stamp with build_dirty=0 (a6aaab93c3d2 for 0371, 9db4170acd89 for 0370). The routeprewarm counters equal LAB-L1R's
release cells.

## 8. Gate 5 -- ratchet (instrumented L1INS 6198d2e06b8d = build/ags/ags.exe)

`.sdl-dos-ports/shared/tools/ratchet.sh --root <l1land> --no-build --no-host-wait --capture-display 397 --no-record`,
with all nine game packages present (5days, 7days, agsquest, bench16, bench8, bench8old, mmd, shards, trilbysnotes).

| run | machine | result |
|---|---|---|
| 20261109T005855Z (RATCHET-20261109T005855Z-*) | shared: the lab agent's L2 cells ran on display 398 throughout; the ratchet's exclusive units waited up to 723 s for their lock | 39 pass (10 improved), **2 fail, both the expected size checks**, 4 quarantined. exe-bytes 8698670 > 8695597; code-lock-bytes 5222512 > 5221072. Every screen-alias check PASS (bench8 x9, bench16 x2, 5 Days); screen-shards-alias-512x384 FAIL(q) 1 (FRZ00 only), its fixed-40k twin PASS(q) |
| 0371's delta vs 0370 (0001-0370) | -- | exe +3073 (instrumented), +2561 (release); code-lock +1440 |
| proposed limits (exact, no headroom; tests/ratchet.yaml on l1land) | -- | **exe-bytes 8698670, code-lock-bytes 5222512** |

- **No second run was needed.** No load-sensitive unit came back VOID or failed. The one FAIL(q) is the quarantined
  shards check's known freeze-tick drift (FRZ00 at tick 100, 236,840 px; FRZ01-04 equal), as in R2LAND and R2DEF. It
  never gates.
- **Every other check** is PASS or IMPROVED, as in R2DEF's runs.

## 9. Caveats -- what was not exercised, what was not tested

- **Not exercised naturally:**
  - a request finding the warm cache by byte compare (first_compare 0 everywhere): every warm-then-request pair here is
    a serial hit;
  - a natural mask change between the warm and the first request. F1 forces one;
  - DosPrewarm on a game other than MMD with a walk after the warm: 5 Days warms and never walks; Trilby room 35 has no
    walkable pixel; AQ is JPS.
- **Not tested:**
  - DOSAGS_RP_FAST=0 and DOSAGS_RP_VERIFY=1 with the warm on (LAB-L1R section 6 reasons about them; no cell here);
  - a game whose player character is not in the displayed room at FadeIn.
- **No timing here.** The speed claim (first room-2 click 187 -> 17 ms at 40k; +66 / +184 ms of faded-out time per
  room entry) is LAB-L1R section 5's, and the 486 round is still to come. The warm adds its own time to the faded-out
  part of every room entry and restore while on, even where the player never walks (V, the intro).
