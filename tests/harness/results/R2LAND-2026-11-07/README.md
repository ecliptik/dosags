# R2LAND-2026-11-07 -- landing records for ags 0369 (lever R2, DOSAGS_CHAR_REUSE, default OFF)

DOSBox-X only (cycles=fixed 40000, tests/harness/confs/dosbox-x-fixed40k-opl3.conf); no rig, no vcctrl. Text records
only: frame digests (FHASH.TXT), RUNMANI.LOGs, the game-output lines each equivalence read (GAMELINES.TXT),
parse-results JSON, the cell command lines (CELL.txt, stage dir masked), the overlay and its apply scripts, the lane and
build scripts, the compare tools, the compare output (tables/), the ratchet reports. No images. Lever design and lab
numbers: docs/lab/LAB-R2.md section 6, docs/lab/LAB-R2B.md. Cells ran 2026-11-07 22:49 to 2026-11-08 02:05 PST.

## 0. Answer first

- **0369 = LAB-R2B's lever plus two fixes found by reading the code, default off.** Modes 1 and 2 against 0 are
  EQUAL on every loop counter of G, V, GCL, the intro and AGS Quest. The R2a verify made 59,318 checks with 0
  mismatches and keyfail 0 everywhere. Every counter matches LAB-R2B's on those five fixtures.
- **Fix 1, the walk-behind mask generation (dos_cr_wb_gen).** It joins R2's key; it is bumped by
  walkbehinds_recalc() and by every DrawingSurface access to the walk-behind mask.
  - Why: a DrawingSurface on the walk-behind mask changes what walkbehinds_cropout() reads without touching
    walk_behind_baselines_changed.
  - Effect on the lab lever: a still character kept its old crop-out. Measured with the overlay's forcing: **DIFF
    1847/3164** with the generation ignored (= the lab lever), **EQUAL** with it.
- **Fix 2, the viewport count.** R2b's one-viewport guard counts the room viewports before the first one is drawn.
  The lab counted them while drawing, so with two viewports the first one's put still skipped. Multi-viewport is
  guarded, not gated (no fixture has one).
- **Dynamic sprite edited in place (coordinator's added gate).** The engine path does clear R2's hit:
  - the path: DrawingSurface.Release -> on_dynsprite_surface_release -> game_sprite_updated ->
    notify_sprite_changed sets the texture's notify mark -> IsChangeNotified() fails construct_object_gfx's cache
    test, and R2a's branch sits behind that test;
  - forced: 825 edits, 820 R2a candidates refused by the notification; **EQUAL**;
  - control (R2a blind to the notification): **DIFF 2989/3164**.
- **The two combos LAB-R2B did not gate:**
  - CHAR_REUSE=2 under DOSAGS_GUI_CLIP=2 and under =0: EQUAL on G and GCL;
  - under =1 (extra): EQUAL on G.
  - Every guiclip mode has a path that redraws an R2b entry, so no mode refuses R2b (section 3).
- **Controls DIFF; forced guards EQUAL on, DIFF off; release EQUAL; default-off inert** (frame-EQUAL to main's R3LAND
  records on G, V, intro, AQ and on GUI_CLIP=2/0).
- **Builds and ratchet.** Both flavours are clean (build_dirty=0) and reproduced byte for byte by a full clean rebuild.
  Ratchet: exe-bytes +7094 and code-lock-bytes +4432 fail as expected; the proposed exact limits are in section 9.

## 1. Binaries (worktree ~/git/dosags-r2land, branch r2land off main 6bd05070; patches/ags/0369)

| exe | what | sha256 | binary_sha12 | build_dirty | bytes |
|---|---|---|---|---|---|
| R2INS | 0001-0369, instrumented | 0e59c82b877719726cff6a5b45ee0495a498993756fd05e829a6c69e76ba5a88 | f9f8dd6614c8 | 0 | 8,695,597 |
| R2REL | 0001-0369, release | ffe49dab2c137748d91bbbace337590556cc1086b0420f6183e342deaee0282a | 84c1a74fdcf6 | 0 | 8,657,967 |
| MAINREL | main's release (= R3LAND's R3REL), P9 reference | 7deb7ca9778676e53f920cf654813697b6ce7f8081ab3f5e5656ca5b12df8898 | 4c9f83b62c5c | 0 | 8,651,385 |
| R2GATE | 0001-0369 + gate-overlay.diff, instrumented (lab only) | 0a94117eecaebd05c67eff8d8f3a6dc951fb05cb8ed77b633de387c2e58f5647 | c7911d373400 | 1 | 8,720,399 |

- Build A ran from the vendor tree that `make patches` produced from the committed series (tree e40c5d5d, the same
  tree as the authoring commit).
- Build B was a full clean rebuild (build/ags and build/ags-release removed). It reproduced R2INS and R2REL byte for
  byte.
- The 0369 commit message was finalised after the gates. That changes no tree, so the stamps are unchanged: `make
  build-dirty` reads build_dirty=0 sha12=f9f8dd6614c8 / 84c1a74fdcf6 after the final `make patches`.
- Against main's aa334361a087 / 4c9f83b62c5c: **+7,094 bytes instrumented, +6,582 release.**

## 2. The overlay (apply-overlay-r2land.py; gate-overlay.diff is the full vendor/ags diff over 0369)

The overlay is applied to vendor/ags, built and reverted. It is never landed, and 0369 itself carries no lab knob.

It runs LAB-R2B's apply-overlay-r2b.py first, with its anchors renamed from "lab lever R2" to "patch 0369 R2".
That script in turn runs R3LAND's apply-overlay-r3land.py unchanged. Together they provide:
- the FRAMEHASH digest, the LABCLICKS presets G / V / GCL and CKPT;
- FORCE_WHOLE / NOGUARD, SPANMAX / SPANPROBE / NOCOARSE;
- CR_VERIFY, CR_NODRAW, CR_NOBASEL, CR_TOGGLE, CR_CAM, CR_BASEL, CR_NOMARK, CR_NOLATCH and CR_NOCAM, as in LAB-R2B
  section 8.

R2LAND adds two in-place-edit forcings, each with a control. Both forcings are render-only and identical in every arm.

- **DOSAGS_LAB_CR_DYN=N.** Every Nth scene, each character standing still in the room (walking 0, animating 0) has
  its current frame sprite edited in place through the script path:
  - a static frame sprite is first replaced by a dynamic copy (DynamicSprite_CreateFromExistingSprite; the frame's
    pic set to it; the script object held by a reference);
  - then DynamicSprite_GetDrawingSurface, DrawingColor, DrawRectangle 2x2 (position and colour move with each edit),
    and DrawingSurface_Release.
- **DOSAGS_LAB_CR_NONOTIFY=1** (control for DYN): construct_object_gfx's cache test ignores the notification, but only
  for an R2a candidate (dos_cr_allow set). Mode 0 is unaffected.
- **DOSAGS_LAB_CR_WBM=N.** Every Nth scene, through Room_GetDrawingSurfaceForMask(walk-behind), StartDrawing,
  FinishedDrawing and DrawingSurface_Release:
  - on odd N-windows, the lower half of each still character's rect is saved and filled with area 15;
  - area 15's baseline is set to 1000 once per room with SetWalkBehindBase, so the area crops every character;
  - on even windows the saved pixels are put back.
- **DOSAGS_LAB_CR_NOWBGEN=1** (control for WBM): R2's key ignores dos_cr_wb_gen. This is the lab lever's behaviour.
- **"DOS-PORT charreuse_lab2 ..."** counters:
  - dyn_forced, dyn_created;
  - dyn_refused: an R2a candidate whose cache test failed only on the notification;
  - dyn_nonotify_hits;
  - wbm_forced, wbm_restored;
  - wbm_refused: an R2a candidate refused only by the mask generation;
  - wbm_ignored.

## 3. Behaviour, guards, witness (deliverable b)

- **Modes.** DOSAGS_CHAR_REUSE unset or 0 = off, the default (the 0368 head). 1 = R2a, 2 = R2a + R2b. Software renderer
  only.
- **R2a.**
  - When the full input key equals last scene's, and the raw bitmap and texture are the ones last scene left,
    construct_object_gfx's cached branch returns "intact": no re-copy, no crop-out, no texture sync.
  - The key: sprite and mirror, view/loop/frame, the six tint/light fields, zoom, w/h, final x/y, baseline,
    transparency, the no-walk-behinds flag, walk_behind_baselines_changed, the walk-behind mask generation, room and
    bg frame.
- **R2b (mode 2).**
  - Eligibility: a character with an R2a hit and the same full key, composited last scene, and idempotent
    (transparency 0, no alpha channel).
  - Such a character skips its mark and is flagged to the driver; DosPortNextIsChar(2) tags the entry for the counters.
  - What the driver does with the flagged entry, per DOSAGS_GUI_CLIP mode (the code read before gating):

    | mode | flagged entry drawn | when nothing dirty reaches it |
    |---|---|---|
    | 4 | once per dirty box (0368) | skipped |
    | 2 | clipped to the dirty bbox | skipped |
    | 1 | clipped to the bbox | drawn in full |
    | 0 | not flagged; drawn in full, as 0169's unchanged GUIs are in mode 0 | drawn in full |

    The driver also draws the entry in full whenever 0368's same-space test fails (a scrolled room camera).
  - Every mode therefore redraws the entry wherever the restore repainted, so R2b needs no refusal. Gated: G-G2,
    GCL-G2, G-G0, GCL-G0 and G-G1, all EQUAL.
- **Guards.**
  - (1) A record left unmarked whose character is now off, in another room, or not key-same gets its OLD rect marked
    before the restore. A net at the end of the scene marks the rest.
  - (2) The entry is drawn in full, not skipped, when:
    - 0366's latch is armed;
    - the camera or viewport moved;
    - dos_port_dirty or its carry is full;
    - 0368's coarse flag is set;
    - the scene has more than one room viewport (counted before the first viewport is drawn).
  - (3) Records are dropped on clear_drawobj_cache, on a room change, or after a scene without exactly one composite.
- **Witness.**
  - STDOUT: "DOS-PORT charreuse DOSAGS_CHAR_REUSE=<v|(default)> mode=<n>", printed at driver construction.
  - RUNMANI.LOG, both flavours: "DOS-PORT charreuse_final mode= hits= keyfail= elig= skips= refused= forced_full=
    ff_latch= ff_cam= ff_full= ff_coarse= ff_multi= mark_old= mo_off= mo_key= mo_end= mo_reset= resets= reset_cache=
    reset_room= reset_gap= drv_flagged= drv_skipped= drv_boxed= drv_boxes= drv_clipped= drv_full= drv_latched=
    scenes=".
  - DOSAGS_CHAR_REUSE is in the RUNMANIFEST env allowlist, after DOSAGS_BREAK_0193.
- **docs/dist/README.TXT is unchanged.**
  - R2 is off by default, so no player runs it unless they set it.
  - The KNOWN LIMITS fallback line lists only the on-by-default speed-ups to turn off (VM, ENGLEV, GUI_CLIP), and R2 is
    not one of them.
  - Advertising an opt-in lever before its 486 round would invite players to enable an unmeasured option.

## 4. Fixtures and witnesses

- **Fixtures** (MMD = Maniac Mansion Deluxe):
  - G: save 007 in room 1 -> room 2, exit 8600; 3164 loop counters.
  - V: G's route plus the verb bar, exit 9400; 3964.
  - GCL: LAB-L1's 16 clicks, exit 12440; 7004.
  - intro: --startr 40, exit 1300; 1299.
  - AQ: AGS Quest AutoPilot; 3558.
- **Gate cells:** no --fixed-timestep (every tick rendered), fine timing off, no TICKLOG, DOSAGS_LAB_FRAMEHASH=1 +
  DOSAGS_PRESENT_VERIFY=1, DOSAGS_RANDSEED=1.
- **Arm names:** 0 = CHAR_REUSE unset; 1 and 2 add DOSAGS_LAB_CR_VERIFY=1; "2n" is 2 without the verify (controls and
  disabled guards).
- **Witnesses** (tables/cellcheck-all.txt, all 56 cells): rc 0 and exit_code=0 in each.
  - fixed-timestep: DISABLED in the 47 gate cells, ENABLED in the 9 release cells.
  - The guiclip witness (=(default) mode=4, or =0/1/2 in the G?/GCL-G? cells) is present in every cell.
  - The charreuse witness is present in every cell except P9-MAIN-D, main's binary, which has none, as expected.
  - labclicks n=14 (G, V) / 16 (GCL).
  - RUN.BAT SET totals are 119-336 bytes, longest line 38.
- **Stage dirs** were deleted per cell. Displays 396/397 only, at most two DOSBox-X at once.

Compare, in this directory: `python3 fhcmp.py G-0.FHASH.TXT G-2.FHASH.TXT` (by loop counter); `python3 eqcmp.py
P9-MAIN-D.GAMELINES.TXT P9-REL-0.GAMELINES.TXT`. tables/ holds the full compare output (tables.sh regenerates it).

## 5. Gate 1 -- mode equivalence (R2GATE)

| fixture | 1 vs 0 | 2 vs 0 | verify checks / mismatches (1; 2) | mode 2: hits / skips / drv skipped / boxed (boxes) / full | forced_full | mark_old (key/reset) | PV stale |
|---|---|---|---|---|---|---|---|
| G | EQUAL 3164/3164 | EQUAL 3164/3164 | 5780/0; 5780/0 | 5780 / 5716 / 3023 / 1114 (1134) / 1579 | 64 (full) | 8 (5/3) | 0 |
| V | EQUAL 3964/3964 | EQUAL 3964/3964 | 6717/0; 6717/0 | 6717 / 6653 / 3023 / 1114 (1134) / 2516 | 64 (full) | 6 (3/3) | 0 |
| GCL | EQUAL 7004/7004 | EQUAL 7004/7004 | 11261/0; 11261/0 | 11261 / 11197 / 4839 / 2405 (2462) / 3953 | 64 (full) | 19 (16/3) | 0 |
| intro | EQUAL 1299/1299 | EQUAL 1299/1299 | 2033/0; 2033/0 | 2033 / 1937 / 1404 / 2 (2) / 531 | 96 (cam 80, full 16) | 4 (2/2) | 0 |
| AQ | EQUAL 3558/3558 | EQUAL 3558/3558 | 3868/0; 3868/0 | 3868 / 3862 / 2789 / 1073 (1126) / 0 | 6 (full) | 530 (525/5) | 0 |

- **Totals.** 59,318 verify checks, 0 mismatches; keyfail 0, refused 0 and mo_end 0 everywhere.
- **Natural guard fires:**
  - ff_full in every fixture;
  - ff_cam 80 in the intro;
  - ff_latch, ff_coarse and ff_multi are 0 in every unforced cell;
  - latch_fullrestore and span_stretch are 0 in every unforced cell.
- **Against LAB-R2B.** Every number in this table equals LAB-R2B section 4's.

## 6. Gate 2 -- R2b under the other guiclip modes, and default-off inert

| pair | result | mode-2 driver outcome for R2b entries |
|---|---|---|
| G-G2-2 vs G-G2-0 (GUI_CLIP=2, R1) | EQUAL 3164/3164 | skipped 3011, clipped to bbox 1126, full 1579; verify 5780/0 |
| GCL-G2-2 vs GCL-G2-0 | EQUAL 7004/7004 | skipped 4835, clipped 2409, full 3953; verify 11261/0 |
| G-G0-2 vs G-G0-0 (GUI_CLIP=0, off) | EQUAL 3164/3164 | not flagged: 5716 skips drawn in full (drv_* 0, they count flagged entries only); verify 5780/0 |
| GCL-G0-2 vs GCL-G0-0 | EQUAL 7004/7004 | 11197 skips drawn in full; verify 11261/0 |
| G-G1-2 vs G-G1-0 (GUI_CLIP=1, extra) | EQUAL 3164/3164 | clipped 4137, full 1579 |

Lever inert (default off) against main's committed R3LAND records (0001-0368 + R3LAND overlay):

| pair | result |
|---|---|
| G-0 vs R3LAND GG-D | EQUAL 3164/3164 (guiclip_final identical: flagged 9558, skipped 6742, boxed 2475 (2510), full 341) |
| V-0 vs GV-D | EQUAL 3964/3964 |
| I-0 vs GI-D | EQUAL 1299/1299 |
| Q-0 vs GQ-D | EQUAL 3558/3558 |
| G-G2-0 vs GG-2, G-G0-0 vs GG-0 | EQUAL 3164/3164 each |

## 7. Gates 3 and 4 -- controls, forced guards, in-place edits (fixture G unless named; "0" = mode 0 + the same forcing)

| item | forcing | guard on (2 + forcing) vs 0 + forcing | disabled / control vs 0 + forcing | fires |
|---|---|---|---|---|
| control (i) no per-box redraw | -- | -- | NODRAW: **DIFF 3023/3164** (G), **6487/7004** (GCL) | nodraw_n 5716 / 11197 |
| control (ii) key without the baseline | BASEL=7 (Dave's draw baseline +1000, alternate 7-scene windows) | G-B-2 **EQUAL 3164/3164** | NOBASEL: **DIFF 980/3164** | basel_forced 1596; G-B-2 mo_key 407, mark_old 410 |
| guard (1) old-rect mark | TOGGLE=7 (Syd not drawn every 7th scene) | **EQUAL 3164/3164** | NOMARK: **DIFF 590/3164** | toggles 208; mo_off 206, mark_old 214; nomark_n 214 |
| guard (2) 0366's latch | FORCE_WHOLE=7 (whole-surface restore every 7th) | **EQUAL 3164/3164** | NOLATCH: **DIFF 1440/3164**, PV stale 1429 frames / 2,569,638 px | forced 456, latch_fullrestore 439; ff_latch 815; NOLATCH drv_latched 225 |
| guard (2) whole invalidation | CAM=7 (invalidate_screen() every 7th scene) | **EQUAL 3164/3164** | NOCAM: **DIFF 14/3164** (lc 5700-6007) | cam_forced 456; ff_full 880 |
| guard (2) 0368's coarse flag (extra) | SPANMAX=1, SPANPROBE=7:166 (R3LAND's) | G-S-2 **EQUAL 3164/3164** | -- (no R2-only disable knob) | probes 456, span_stretch 213,348, fb_coarse 3047; ff_coarse 5451 |
| dynamic sprite edited in place | DYN=7 (825 edits, 5 dynamic copies) | G-D-2 **EQUAL 3164/3164** | NONOTIFY: **DIFF 2989/3164** | dyn_refused 820 (R2a candidates refused by the notification); mo_key 819; NONOTIFY hits 5716 in spite of the mark |
| walk-behind mask edited | WBM=7 (412 fills, 412 restores) | G-W-2 **EQUAL 3164/3164** | NOWBGEN (= the lab lever): **DIFF 1847/3164** | wbm_refused 1206 (refused only by the generation); mo_key 818; NOWBGEN wbm_ignored 1206 |

- **Reference arms.** Each pair is compared against its own forced mode-0 arm. Against unforced G-0:
  - G-L-0, G-C-0 and G-S-0 are EQUAL (those forcings change what is restored, never the picture);
  - G-T-0 (206), G-B-0 (1049), G-D-0 (3029) and G-W-0 (1716) DIFF by construction.
- **Verify in the forced cells.** The verify was on in G-D-2 (4955/0) and G-W-2 (4570/0). It was off in the other
  forced and control arms (arm 2n).
- **The NONOTIFY hit count.** It counts every hit taken over a notified mark. The mark stays notified because the
  texture is never resynced, so after the first edit every scene's hit counts.

## 8. Gates 5 and 6 -- release regression and P9 (R2REL / MAINREL; game output lines, eqcmp.py; --fixed-timestep)

| pair | result |
|---|---|
| P9-REL-0 (0369, default off) vs P9-MAIN-D (main 4c9f83b62c5c) | EQUAL (78) |
| P9-REL-2 (0369, =2) vs P9-MAIN-D | EQUAL (78); hits 6027, skips 5979 (drv skipped 5945, boxed 34) |
| RG-5D3S-2 vs -0 (5 Days room 3, exit 3000) | exit 0/0, EQUAL (30); skips 857, all drawn in full (same-space fails) |
| RG-TN35-2 vs -0 (Trilby room 35, MSGSKIP=1) | exit 0/0, EQUAL (1121); skips 2299, all drawn in full; mark_old 766 |
| RG-AQ-2 vs -0 (AGS Quest AutoPilot) | exit 0/0, EQUAL (356); parse-results PASS both; skips 3795 (2750 skipped, 1045 boxed) |

- **Witnesses.** Every release cell shows fixed-timestep ENABLED, guiclip (default) mode=4 and binary_sha12
  84c1a74fdcf6 build_dirty=0, plus the charreuse witness (=(default) mode=0, or =2 mode=2).
- **Small differences from LAB-R2B's release counts.** 5 Days 857 skips here against 854 in the lab, and Trilby
  mark_old 766 against 762. These are fixed-timestep cells, where the set of ticks drawn follows emulated time per
  frame, which 0369's code changes shift. The game lines are EQUAL either way.
- **Lever inert, the frame half.** That default off renders frame-EQUAL to main is shown in section 6.

## 9. Ratchet (deliverable c; instrumented R2INS f9f8dd6614c8 = build/ags/ags.exe; `ratchet.sh --root <r2land> --no-build --no-host-wait --capture-display 397 --no-record`)

| run | result |
|---|---|
| 20261108T090448Z (RATCHET-20261108T090448Z-*) | 38 pass (10 improved), 3 fail, 4 quarantined. exe-bytes 8695597 > 8688503; code-lock-bytes 5221072 > 5216640; screen-5days-alias-512x384 FAIL 2: VOID, not a picture difference (see the note below). Quarantined: screen-shards-alias-512x384 FAIL(q) 3, its known freeze-tick drift |
| 20261108T101009Z (`--only screen-5days-alias-512x384,screen-shards-alias-512x384`, machine idle) | PASS: screen-5days-alias-512x384 5 of 5 pairs equal; shards FAIL(q) 2 (FRZ00 A=100 B=101, its known drift) |
| 0369's delta vs main (0001-0368) | exe +7094 (instrumented), +6582 (release); code-lock +4432 |
| proposed limits (exact, no headroom; tests/ratchet.yaml on r2land) | **exe-bytes 8695597, code-lock-bytes 5221072** |

- **Why the first 5 Days row was VOID.** Its FRZ03 froze at different ticks (A=701 B=700), so only 4 pairs were
  comparable against the 5 the check needs. All 4 comparable pairs were equal.
- **The likely cause, inferred and not proven.** gate-alias runs at cycles=max, so the freeze tick is sensitive to
  host load, and this run shared the host with lane 1/3 gate cells; it waited 126 s for its exclusive lock. The
  binary runs with CHAR_REUSE unset there, and the lever is inert (section 6).
- **Every other check** is PASS or IMPROVED, as in R3LAND's run.

## 10. Caveats

- **Never fired naturally** in any unforced cell:
  - ff_latch, ff_coarse, ff_multi;
  - keyfail, refused, mo_end;
  - latch_fullrestore, span_stretch;
  - a dynamic-sprite edit, a walk-behind mask edit.
- **How the guards were exercised instead.**
  - The latch, the whole invalidation, the coarse flag and the old-rect mark were exercised only by forcing.
  - The coarse flag has no R2-only disable knob, so there is no DIFF arm for it.
  - The one-viewport guard (ff_multi) is untested: no fixture has two room viewports.
- **A real camera move (LAB-R2B's CAM=7:1)** was not re-run here; LAB-R2B gated it EQUAL. The whole-invalidation
  forcing (CAM=7) was re-run.
- **Mode 1 under the forcings.** The DYN and WBM forcings ran in mode 2, which includes R2a. Mode 1 was not run under
  them.
- **No timing here.** LAB-R2B's lab timing (room 1 busy 10.29 -> 7.42 ms) is unchanged information. Nothing was timed
  on 0369 itself, and the 486 round (LAB-R2B section 7, round RD) is still to be staged from this commit's clean
  builds.
