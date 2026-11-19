# LAB-R2B -- lever R2 built in the lab (DOSAGS_CHAR_REUSE): exact on every digest gate, and room 1's drawn tick at fixed 40k drops from 10.29 to 7.42 ms busy (lab worktree ~/git/dosags-lab-r2b)

Copied into the main repo 2026-11-07 from the lab worktree ~/git/dosags-lab-r2b (base main 9e54b6d9; lab only). Diffs, lever and
overlay scripts, cell text records and tables in docs/lab/r2b-lab/. Exes stay local (lab builds are build_dirty=1, not for the rig).

Lab only: nothing committed, no rig or vcctrl, no pushes. ~/git/dosags (main), the other worktrees and ~/git/dosags-nightly
were only read (R3LAND's committed FHASH records, scripts and the RCMP/RC round files). All times are DOSBox-X fixed-40000
emulated time. Design: docs/lab/LAB-R2.md sections 1, 3 and 6 (main 35e983d2); docs/lab/R2-FORECAST.md was read, not edited.

## 0. Answer first

- **Built.** DOSAGS_CHAR_REUSE: unset or 0 = off (the 0368 head), 1 = R2a, 2 = R2a + R2b. One edit script
  (build/r2b/lever-r2b.py) over 0001-0368, 6 files, +285 / -2 lines, all under `__DJGPP__`; diff build/r2b/lab-r2b.diff.
- **Exact.** Mode 1 and mode 2 against 0, every tick rendered, FRAMEHASH + PRESENT_VERIFY, seeded: **EQUAL on every loop
  counter** of G (3164), V (3964), GCL (7004), the intro (1299) and AGS Quest AutoPilot (3558); stale px 0 in every cell.
  The lab verify rebuilt every reused image the old way: **0 mismatches in 59,318 checks** (G 5780, V 6717, GCL 11261,
  intro 2033, AQ 3868, each in mode 1 and again in mode 2), keyfail 0 everywhere.
- **Controls.** (i) no per-box redraw: **DIFF** 3023/3164 (G), 6487/7004 (GCL). (ii) the key without the baseline:
  **EQUAL** on all five natural fixtures (no fixture changes a baseline without moving the character), **DIFF 980/3164**
  under a forced draw-baseline change, where the full key is EQUAL. Reported as found; the natural (ii) is not a DIFF.
- **Guards, forced in the overlay.** Old-rect mark: EQUAL / disabled DIFF 590. Latch (whole-surface restore every 7th):
  EQUAL / disabled DIFF 1440. Camera / whole-surface invalidation every 7th scene: EQUAL / disabled DIFF 14. A real 1-px
  camera move every 7th scene in the 960-wide room 2: EQUAL (no disabled arm can DIFF there, section 4).
- **Release.** Mode 2 vs 0 game lines EQUAL on 5 Days room 3 (30), Trilby room 35 (1121), AGS Quest (356; parse-results
  PASS both); P9 fixture EQUAL (78) for the lever's release with R2 off and with R2 on, against main's release.
- **Lab timing (information).** Room 1, GCL, drawn ticks, same binary: busy 10.29 -> 7.42 ms mean (-2.87; median 10.05 ->
  7.23), scene + render 4.68 -> 1.83 ms. LAB-R2 predicted ~2.6 net (+0.25-0.35 present upside); LAB-R2 6.3's lab bar
  (>= 1.8 ms) is met. Skips per window are identical (15 = 5 restore + 10 entry; DOSBox-X has no budget-bound skips).
- **One bug found and fixed in the lab, before any scored cell:** v1 recorded composites only in mode 2, so R2a never
  hit in mode 1 (hits=0; its "EQUAL" cells were really mode 0). Fixed (records in modes 1 and 2), all three flavours
  rebuilt, every cell re-run on v2. v1 cells are kept in build/r2b/results/v1/ and not scored.
- **Where R2b does not engage on the composite:** room 2 of MMD (960 wide, camera at 640) and 5 Days / Trilby. 0368's
  same-space test (batch offset 0, full-size surface) fails there, so a skipped character is drawn in full: drv_full
  1579 of 5716 skips on G, all 854 on 5 Days, all 2299 on Trilby. R2a and the restore/present savings still apply.

## 1. Setup

- `git -C ~/git/dosags worktree add --detach ~/git/dosags-lab-r2b main` (35e983d2); vendor/ags and vendor/SDL cloned from
  ~/git/dosags/vendor, vendor/cwsdpmi and the 5days/agsquest/mmd/trilbysnotes packages copied from main; `make patches`,
  `make sdl3`, `make game`, `DOSAGS_RELEASE=1 make game`.
- **Check: main's two flavours rebuilt here are byte-identical to R3LAND's R3INS / R3REL** (sha256 1cb00ce1... / 7deb7ca9...,
  stamps aa334361a087 / 4c9f83b62c5c, build_dirty 0).
- Conf tests/harness/confs/dosbox-x-fixed40k-opl3.conf; ACSETUP-ON-512X384-ROUND.CFG; save 007 from
  ~/git/dosags/build/ws/roundQ/AGSSAVE.007 (`--loadsavedgame 7`). DOSAGS_RANDSEED=1 in every cell.
- Displays 394/395 only, at most two DOSBox-X at once (two serial chains). Every wait went through tools/waitfor.sh
  with a pid file and a timeout; nothing was left running; stage dirs deleted per cell (the two cells of the stopped v1
  lanes were deleted by hand).
- Witnesses, every cell (tables/cellcheck-all.txt, 48 cells, all rc 0 and exit_code=0): `fixed-timestep: DISABLED` in the
  35 gate cells, `ENABLED` in the 13 release/timing cells; `DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4`;
  `DOS-PORT charreuse DOSAGS_CHAR_REUSE=<(default)|1|2> mode=<0|1|2>` (MAINREL has none, as expected); `labclicks n=14`
  (G, V) / `16` (GCL); fine-timing cells record script_vm (14028 calls), fine-off cells say "never-entered".
- RUN.BAT SET totals 119-343 bytes. The overlay expands DOSAGS_LABCLICKS=G / V / GCL in the exe (R3LAND's G and V strings,
  LAB-R2's GCL preset). Proof the preset is the same fixture: mode-0 G, V, intro and AQ FHASH equal R3LAND's committed
  GG-0 / GV-0 / GI-0 / GQ-0 (spelled-out clicks, main + overlay v1) on every loop counter (3164 / 3964 / 1299 / 3558).

## 2. The lever (build/r2b/lever-r2b.py; diff build/r2b/lab-r2b.diff)

- **R2a (ac/draw.cpp).** Before construct_char_gfx, prepare_characters_for_drawing matches the part of the key outside the
  cache test against last scene's record: view/loop/frame, width/height, final atx/aty and baseline, transparency, the
  no-walk-behinds flag, walk_behind_baselines_changed == 0, room, bg frame, and the raw bitmap / texture being the ones
  last scene left (pointer equality), composited in the previous scene. construct_object_gfx's cached branch already
  matched sprite+mirror, the six tint/light fields, zoom and no change notification; with permission it returns "intact"
  (no re-copy), so the caller skips the crop-out and the texture sync. After prepare, the full key (sppic, view/loop/
  frame, 6 tint/light, zoom, mirror, w/h, x/y, baseline, transparency, nowb, room, bg frame) is compared with last
  scene's; an R2a hit with a differing key is counted (keyfail; 0 in every cell).
- **R2b (mode 2).** A character with an R2a hit, the same full key, composited last scene, and idempotent (transparency 0,
  no alpha channel) skips its mark in put_sprite_list_on_screen and is flagged to the driver like 0169's entries
  (DosPortClipNextToDirty), so 0368 draws it once per dirty box that reaches it, or not at all. A new one-shot
  DosPortNextIsChar(2) tags the driver entry for the counters (gfxdriverbase.h, graphicsdriver.h, ali3dsw.h).
  - Rule 1 (0197's convention, before the restore): a record left unmarked whose character is now off, in another room,
    not eligible (any key change, baseline included) gets its old rect marked in prepare_characters_for_drawing; a net at
    the end of construct_game_scene marks any unmarked record not composited this scene.
  - Rule 2, decided at the mark (after this scene's restore, before the composite): not skipped -- marked and drawn in
    full -- when 0366's latch is armed for this composite (dos_gc_latch >= 2, which latch_fullrestore sets during the
    restore), when the room camera or viewport rect changed since last scene, when dos_port_dirty is full or its carry is,
    when 0368's coarse guard is set, or with more than one room viewport. In the driver a flagged entry under the latch,
    or failing same-space / valid / not-full, is drawn in full exactly as 0366 draws GUIs.
  - Rule 3: records dropped (unmarked old rects marked) on clear_drawobj_cache, a room change, or a scene gap / a scene
    without exactly one composite (dos_cr_composites, counted in RenderToBackBuffer).
- Witness: `DOS-PORT charreuse DOSAGS_CHAR_REUSE=<v|(default)> mode=<n>` at driver construction; in RUNMANI.LOG (both
  flavours) `DOS-PORT charreuse_final mode= hits= keyfail= elig= skips= refused= forced_full= ff_latch= ff_cam= ff_full=
  ff_coarse= ff_multi= mark_old= mo_off= mo_key= mo_end= mo_reset= resets= reset_cache= reset_room= reset_gap=
  drv_flagged= drv_skipped= drv_boxed= drv_boxes= drv_clipped= drv_full= drv_latched= scenes=`. DOSAGS_CHAR_REUSE joins
  the RUNMANIFEST env allowlist (alphabetical, after DOSAGS_BREAK_0193). Requested counters: reuse hits = `hits`, R2b
  skips = `skips` (driver outcome: drv_skipped / drv_boxed / drv_full), forced full draws = `forced_full` (+ drv_full),
  mark-old-rect events = `mark_old`.
- Reuses 0366's latch and 0368's coarse flag through two read-only accessors (dos_guiclip_latched_next,
  dos_guiclip_coarse) and the existing flagged-entry path; nothing of R1/R3 is duplicated. guiclip_final's counts now
  include R2b character entries in mode 2.

## 3. Exes (build/r2b/exe/)

| exe | what | sha256 | binary_sha12 | build_dirty | bytes |
|---|---|---|---|---|---|
| MAININS | main 35e983d2 instrumented (= R3INS) | 1cb00ce1307d1f7bccbf3d65c3d9cbe61fb9228c847a4f0ece6e398bb2c2c91e | aa334361a087 | 0 | 8,688,503 |
| MAINREL | main 35e983d2 release (= R3REL), P9 reference | 7deb7ca9778676e53f920cf654813697b6ce7f8081ab3f5e5656ca5b12df8898 | 4c9f83b62c5c | 0 | 8,651,385 |
| R2BINS | 0001-0368 + lever, instrumented (not run in a cell) | c37f61ca139e822363ab301f602f6599a96f528330507eab9fc194c77912382d | 2cb65b120866 | 1 | 8,696,035 |
| R2BREL | 0001-0368 + lever, release | e60355e36b12f0606093e4eb66fd3f3b1ca1744110b4ffbb88345edd15f02dc5 | cb8459377533 | 1 | 8,657,893 |
| R2BGATE | lever + overlay, instrumented (all gate, control, guard and timing cells) | 1eb1b372ae67a25a62eb10f42a74fd5c59a387a8c41c4749f4e18b09a7691ff2 | b6c2075d8e9c | 1 | 8,711,678 |
Lever cost vs main: +7,532 bytes instrumented, +6,508 release. v1 exes (the mode-1 bug) in exe/v1/, not scored. None is for the rig.

## 4. Gates (R2BGATE; every tick rendered, fine timing off, no TICKLOG, FRAMEHASH + PRESENT_VERIFY)

Arms: 0 = DOSAGS_CHAR_REUSE unset; 1 and 2 with DOSAGS_LAB_CR_VERIFY=1 (verify only reads). fhcmp.py by loop counter.

| fixture | 1 vs 0 | 2 vs 0 | verify checks / mismatches (1; 2) | mode 2: hits / skips / drv skipped / boxed (boxes) / full | forced_full | mark_old (key/reset) | PV stale |
|---|---|---|---|---|---|---|---|
| G | EQUAL 3164/3164 | EQUAL 3164/3164 | 5780/0; 5780/0 | 5780 / 5716 / 3023 / 1114 (1134) / 1579 | 64 (full) | 8 (5/3) | 0 |
| V | EQUAL 3964/3964 | EQUAL 3964/3964 | 6717/0; 6717/0 | 6717 / 6653 / 3023 / 1114 (1134) / 2516 | 64 (full) | 6 (3/3) | 0 |
| GCL | EQUAL 7004/7004 | EQUAL 7004/7004 | 11261/0; 11261/0 | 11261 / 11197 / 4839 / 2405 (2462) / 3953 | 64 (full) | 19 (16/3) | 0 |
| intro | EQUAL 1299/1299 | EQUAL 1299/1299 | 2033/0; 2033/0 | 2033 / 1937 / 1404 / 2 (2) / 531 | 96 (cam 80, full 16) | 4 (2/2) | 0 |
| AQ | EQUAL 3558/3558 | EQUAL 3558/3558 | 3868/0; 3868/0 | 3868 / 3862 / 2789 / 1073 (1126) / 0 | 6 (full) | 530 (525/5) | 0 |
Natural guard fires: ff_full (dos_port_dirty full: room entries, the restore, fades) in every fixture, ff_cam 80 in the
intro (its camera pans); ff_latch, ff_coarse, ff_multi, keyfail, refused and mo_end 0 everywhere; latch_fullrestore and
span_stretch 0 in every unforced cell. drv_full on G/V/GCL is room 2 (scrolled camera, section 0).

**Controls (mode 2, no verify):**

| control | fixture | vs 0 | note |
|---|---|---|---|
| (i) NODRAW: an R2b character not drawn at all | G | **DIFF 3023/3164** (first lc 5438) | nodraw_n 5716 |
| (i) | GCL | **DIFF 6487/7004** (first lc 5438) | nodraw_n 11197 |
| (ii) NOBASEL: key without baseline / walk_behind_baselines_changed | G, GCL, intro, AQ | EQUAL 3164, 7004, 1299, 3558 | no natural baseline-only change |
| (ii) NOBASEL + forced baseline (BASEL=7: Dave's draw baseline +1000 on alternate 7-scene windows) | G | **DIFF 980/3164** vs G-B-0 (first lc 6050) | the full key: G-B-2 EQUAL 3164/3164, mo_key 407 |

**Forced guards (fixture G; knobs only in the overlay; "0" = mode 0 + the same forcing, which equals unforced G-0 except
where the forcing changes the picture):**

| guard | forcing | guard on (2 + forcing) vs 0 + forcing | guard disabled vs 0 + forcing | fires (guard-on arm) |
|---|---|---|---|---|
| rule 1, old-rect mark | TOGGLE=7: Syd (ch 1) not drawn on every 7th scene (208 toggles) | **EQUAL 3164/3164** | NOMARK: **DIFF 590/3164** (first lc 5441) | mo_off 206, mark_old 214 |
| rule 2, 0366's latch | FORCE_WHOLE=7: a whole-surface restore every 7th room restore (456 forced, latch_fullrestore 439) | **EQUAL 3164/3164** | NOLATCH (mark and driver): **DIFF 1440/3164**, PV stale 2,569,638 px | ff_latch 815 |
| rule 2, camera move / whole invalidation | CAM=7: invalidate_screen() every 7th scene (456; room 1 is 320 wide) | **EQUAL 3164/3164** | NOCAM (mark and driver): **DIFF 14/3164** (lc 5700-6007) | ff_full 880 |
| rule 2, a real camera move | CAM=7:1: room camera moved 1 px every 7th scene in room 2 (248 moves; room 1 falls back to invalidate) | **EQUAL 3164/3164** | -- (in room 2 R2b characters are drawn in full: same-space fails) | ff_cam 454, ff_full 651 |
G-L-0 and G-C-0 equal G-0 on every tick (the forcings do not change a mode-0 picture); G-T-0, G-B-0, G-C1-0 differ from
G-0 by construction (206, 1049, 246 ticks), which is why each pair is compared against its own forced mode-0 arm. The
camera control's DIFF is small because the forcing only bites in room 1 (in room 2 a skipped character is drawn in full).

## 5. Release equivalence (R2BREL / MAINREL; game output lines, eqcmp.py; --fixed-timestep)

| pair | result |
|---|---|
| P9-REL-0 (lever, R2 off) vs P9-MAIN-D (main release) | EQUAL (78) |
| P9-REL-2 (lever, R2 on) vs P9-MAIN-D | EQUAL (78); hits 6027, skips 5979 (drv skipped 5945, boxed 34) |
| RG-5D3S-2 vs -0 (5 Days room 3, exit 3000) | EQUAL (30); skips 854, all drawn in full (drv_full 854) |
| RG-TN35-2 vs -0 (Trilby room 35, MSGSKIP=1) | EQUAL (1121); skips 2299, all drawn in full; mark_old 762 |
| RG-AQ-2 vs -0 (AGS Quest AutoPilot) | EQUAL (356); parse-results PASS both; skips 3794 (2749 skipped, 1045 boxed) |
Every release cell: fixed-timestep ENABLED, guiclip (default) mode=4, charreuse witness, exit 0.

## 6. Lab timing (information; R2BGATE, GCL, same binary, mode 0 vs 2)

T cells: --fixed-timestep, fine timing on, DOSAGS_TICKLOG=30000, lab kinds (DOSAGS_LAB_TK=1: 7 wait, 8 sc_prep_chars,
10 bg_restore, 9 character composite us/pass, 14 its px/pass, 13 rb_sprite_time us/pass), checkpoints 5480/7890/8100/12430.
Reader tools/r2bsplit.py (busy = ugo - wait; logic = busy - scene - render). Room 1, loop ticks 5480-7889, 2410 drawn ticks
each (0 skipped):

| ms per drawn tick | T-0 mean | median | share | T-2 mean | median | share | change (mean) |
|---|---|---|---|---|---|---|---|
| busy | 10.291 | 10.046 | 100% | 7.422 | 7.230 | 100% | **-2.869** |
| logic | 5.616 | 5.654 | 54.6% | 5.592 | 5.662 | 75.3% | -0.02 |
| scene | 2.201 | 2.156 | 21.4% | 1.156 | 1.009 | 15.6% | -1.045 |
| render | 2.474 | 2.468 | 24.0% | 0.674 | 0.550 | 9.1% | -1.800 |
| sc_prep_chars | 0.714 | 0.562 | 6.9% | 0.341 | 0.297 | 4.6% | -0.373 |
| character composites | 1.558 | 1.545 | 15.1% | 0.119 | 0.044 | 1.6% | -1.439 |
| bg_restore (all of it) | 0.578 | 0.618 | 5.6% | 0.157 | 0.139 | 2.1% | -0.421 |
| rb_sprite_time | 1.773 | 1.739 | 17.2% | 0.339 | 0.243 | 4.6% | -1.434 |
| character composite px/pass | 5,220 | 5,294 | | 370 | 112 | | -93% |

- Character work (sc_prep_chars + composites + 0.957 of the restore, LAB-R2 L4's share): 2.83 ms -> at most 0.62 (restore
  counted whole). From the checkpoints over the same window: character entries drawn per scene 3.00 -> 1.10; R2b skips
  2.89 per scene, of which 1.90 not drawn at all and 0.99 drawn per box (1.01 boxes).
- render's drop beyond rb_sprite_time (0.37 ms) is the present: the kids' boxes are no longer marked or pushed.
- Against LAB-R2 6.2's 40k prediction: R2a 0.6 predicted / 0.37 measured (sc_prep_chars still runs get_local_tint and
  the key tests); R2b 2.0 / ~1.86 (composites 1.44 + restore 0.42); present +0.25-0.35 / ~0.37. Net 2.6 / 2.87.
- Information, not a 486 claim: LAB-R2's per-phase 486/40k ratios applied to the measured cuts give R2a 0.94 +
  composites 2.46-3.08 + restore 1.01 = 4.4-5.0 ms, +0.85 present = 5.3-5.9 ms per room-1 drawn tick (LAB-R2 band
  3.5-6.5, central 5.5).
- Whole run (scenes 7019): T-2 hits 11241, skips 11177. One uclock rollover sample in T-2 (clamped 1; the medians stand).

S cells (--fixed-timestep, fine timing off, TICKLOG, no lab kinds; tools/winskips.py), and the T cells:

| window | S-0 | S-2 | T-0 | T-2 |
|---|---|---|---|---|
| restore 5437-5441 | 5/5 | 5/5 | 5/5 | 5/5 |
| room 1 5480-7889 | 0/2410 | 0/2410 | 0/2410 | 0/2410 |
| entry 7890-8399 | 10/510 (7973-7977, 8119-8123) | 10/510 (same) | 10/510 | 10/510 |
| room 2 8400-9499 | 0/1100 | 0/1100 | 0/1100 | 0/1100 |
| late 9500-end | 0/2939 | 0/2939 | 0/2939 | 0/2939 |
| all | 15/7003 | 15/7003 | 15/7003 | 15/7003 |
As LAB-R2 found: no budget-bound skip at 40k, so the skip count cannot move here; the 486 decides it (section 7).

## 7. 486 pre-registration draft (one rig round; consistent with docs/lab/R2-FORECAST.md, whose bands are quoted verbatim)

Not to be staged from this worktree: a rig round needs clean builds (build_dirty=0) of a commit carrying the lever as a
port patch (ags 0369, DOSAGS_CHAR_REUSE off by default). Stamps below are placeholders until that commit exists.

- **Round RD (R2 = DOSAGS_CHAR_REUSE=2 on the R3 default), one power-on:** WARMUPRD, RDA1 RDB1 RDB2 RDA2, RDMP, RDS16
  (first to drop); cap ~100 min.
- **WARMUPRD**: as WARMUPRC (l308.exe, MMD title, TAS 1000; BLASTER.TXT "A220 I7 D3 P330 T3", else STOP). Not scored.
- **RDA1 / RDA2 (arm A, R3-only) and RDB1 / RDB2 (arm B, R2), same-binary ABBA x1.**
  - Binary: RDREL.EXE = the lever commit's clean release, stamp <tbd>, build_dirty=0; VOID if the staged stamp differs.
  - Arm A: no DOSAGS_CHAR_REUSE; STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=0" and "guiclip
    DOSAGS_GUI_CLIP=(default) mode=4", else VOID. Arm B: SET DOSAGS_CHAR_REUSE=2; "charreuse DOSAGS_CHAR_REUSE=2 mode=2",
    charreuse_final skips > 0 and drv_boxed > 0, else VOID.
  - Fixture: P9M1's line verbatim, as RCA1/RCB1 (AGSSAVE.007 f486d0e9..., DRIVE 5 host clicks, TAS 12440, sound ON cfg);
    the camera sheet shows play (room 1 -> 2), else VOID.
  - Score as RC: displayed = 1 - frames_skipped/ticks; per-window skips from the persec lines (room 1 5480-7890, entry
    7890-8400, room 2 8400-9500, late 9500-end); raw guiclip_final and charreuse_final lines.
  - F1 (room 1), verbatim: "R2 cells' room-1 skips 20-40 (central 30), i.e. room 1 98.3-99.2% (central 98.8). Falsifier:
    either R2 cell's room-1 skips > 50, or less than 25 fewer than its same-binary R3-only arm (DOSAGS env toggle, ABBA)
    in that window."
  - F2 (whole fixture), verbatim: "R2 cells 98.9-99.5% displayed (central 99.1; 35-77 skips). Falsifier: either R2 cell
    < 98.6%, or mean(R2) - mean(R3-only) < +0.5 points. 99% x2 is ON THE EDGE of this band, not claimed."
  - F3 (mechanism, per room), verbatim: "entry, room 2 and late windows each within +-10 skips of the R3-only arm ...; a >
    10-skip gain there is a finding, a loss falsifies."
  - R3-only arms expected at RCB1/RCB2's 98.43 / 98.24% (room 1 79 / 75 skips).
  - Lab context (not a band): DOSBox-X shows R2b's composite saving only in room 1; in room 2 (scrolled camera) a skipped
    character is drawn in full, so F3's room-2 window should read near 0 change.
- **RDMP (one instrumented cell, mechanism).**
  - Binary: RDINS.EXE = the same commit's clean instrumented build, stamp <tbd>, build_dirty=0. SET DOSAGS_CHAR_REUSE=2;
    witnesses as arm B. Fixture: RCMP's line verbatim (fine timing on, DOSAGS_TICKLOG=12500, TICKS.BIN).
  - Reader: tests/harness/f1/f1prof.py, room 1 window 5480..7890, drawn ticks. Reference RCMP (R3, aa334361a087, same
    fixture and reader; a different binary and day, stated as such): median scene 5.60 + render 4.09 = 9.69 ms.
  - Prediction (LAB-R2 6.2's 486 band, unchanged): scene + render per room-1 drawn tick cut by central 5.5 ms, band
    3.5-6.5, i.e. 3.2-6.2 ms. FALSIFIED if the cut is < 3.0 ms (LAB-R2 6.3's line). The lab cut scaled by LAB-R2's
    ratios is 4.4-5.9 (section 6), inside the band.
  - Information: script_vm per tick, sc_prep_chars, bg_restore, rb_sprite_time per drawn frame, displayed.
- **RDS16 (the S16 guard).** RDREL with SET DOSAGS_CHAR_REUSE=2; GR16's line verbatim (as RCS16); scorer gatebar.py
  --label S16 --stamp <tbd> --room 3. Prediction: MET (RCS16 / CFS16 levels). R2 engages there (lab: 854 skips on room 3,
  all drawn in full, R3 never boxes there); charreuse_final recorded; boxed > 0 is a finding. First to drop.

## 8. Files

- Lever and overlay: build/r2b/lever-r2b.py (applies the lever to vendor/ags), build/r2b/lab-r2b.diff (vendor/ags, lever
  only, over 0001-0368), build/r2b/apply-overlay-r2b.py (runs R3LAND's apply-overlay.py, copied as apply-overlay-r3land.py,
  then the R2B knobs: GCL/G/V presets, CR_VERIFY, CR_NODRAW, CR_NOBASEL, CR_TOGGLE, CR_CAM, CR_BASEL, CR_NOMARK, CR_NOLATCH,
  CR_NOCAM, LAB_TK, labck c=cr, labroom, charreuse_lab), build/r2b/lab-r2b-gate-full.diff (lever + overlay).
- Scripts: build/r2b/{build-all2.sh, cell.sh, pcell.sh, lib.sh, laneA-E.sh, chain1.sh, chain2.sh, collect.sh}.
  Tools: build/r2b/tools/{cellcheck.py, fhcmp.py, eqcmp.py, ticks.py, r2bsplit.py, winskips.py}.
- Raw results: build/r2b/results/<TAG>/ (STDOUT.TXT, RUNMANI.LOG, RUN.BAT, FHASH.TXT, TICKS.BIN, CELL.txt).
- Text records collected (no images, no TICKS.BIN): docs/lab/r2b-lab/ (scripts, tools, diffs), docs/lab/r2b-lab/cells/
  (FHASH, RUNMANI, CELL, RUN.BAT, GAMELINES, LABCK, parse JSON), docs/lab/r2b-lab/tables/ (fhcmp-all.txt, eqcmp-all.txt,
  cellcheck-all.txt, T-room1-split.txt, S-T-winskips.txt).
- The vendor/ags working tree holds the lever only (no overlay), byte-equal to lab-r2b.diff.

## 9. For the reviewer

- R2b relies on 0368's argument that everything written before an entry lies inside box[] U carry_box[]. The pre-restore
  old-rect marks and the post-restore marks of characters that are not skipped are added to box[] before the composite,
  so entries above a skipped character redraw over anything that changed under it. The forced guards and control (i)
  are the evidence for that, not this paragraph.
- Not gated: DOSAGS_GUI_CLIP=2 or 0 with R2b on (exact by the same argument: under mode 2 the bbox, under mode 0 every
  entry in full); a multi-viewport game (guarded: no skip).
- Landing questions: whether to default it on; whether to widen 0368's same-space test for a scrolled room camera (room 2
  would then get the composite saving too -- a separate, gated change).
