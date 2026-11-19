# L2DEF-2026-11-09 -- landing records for ags 0373 (lever L2, DOSAGS_GUI_CTRL_MARK, on by default)

DOSBox-X only (cycles=fixed 40000, tests/harness/confs/dosbox-x-fixed40k-opl3.conf); no rig, no vcctrl. Text records
only: frame digests (FHASH.TXT), RUNMANI.LOGs, the game-output lines each equivalence read (GAMELINES.TXT),
parse-results JSON, the cell command lines (CELL.txt, stage dir masked), the overlay and its apply scripts, the lane and
build scripts, the compare tools, the compare output (tables/), the ratchet reports. No images, no game data. Why the
default changed: tests/harness/results/ROUNDRG-2026-11-09/README.md (the 486 round RG: L2 with fewer skipped frames in
all 4 pairs, -10 / -12 / -8 / -2, mean -8, +0.11 points displayed; the operator decided to make it the default). The
lever's own landing records: tests/harness/results/L2LAND-2026-11-09. Cells ran in two stretches: G-D and V-D on
2026-11-09 (finished 11:29 and 11:36 PST), then a VM reboot paused the lane; the other 38 ran 2026-11-11 07:23 to
11:48 PST with RESUME=1 (G-D and V-D kept, not re-run).

## 0. Answer first

- **0373 makes L2 the default.** DOSAGS_GUI_CTRL_MARK unset (or any value other than exactly "0") gives mode 1, on.
  Exactly "0" is off (0372's default, the 0371 head for GUIs). The witness reads "DOS-PORT guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1" when unset. Two changed lines (the resolver and the allowlist comment), no new
  getenv, no lab knob; guictrlmark_final is unchanged.
- **The choice for unknown values (for sdlports' review): they read as mode 1.** A mistyped value ("2", "off", "00")
  fails toward the default; only an exact "0" turns L2 off. This is 0370's rule for DOSAGS_CHAR_REUSE and 0368's for
  DOSAGS_GUI_CLIP. Witnessed: =2 and =off print mode=1 and render frame-EQUAL to the default (section 5).
- **Gate 1, default vs explicit =1: frame-EQUAL on all six fixtures** (G 3164, V 3964, GCL 7004, H 7004, intro 1299,
  AQ 3558 loop counters). Every guictrlmark counter is equal too, and so are the restore, composite and present
  counters. The lab texture verify reads **0 px out in every default and =1 cell**.
- **Gate 2, =0 on 0373 vs 0372's default-off records (L2LAND X-0): EQUAL on all six.** =1 on 0373 vs L2LAND's =1
  records: EQUAL on all six. The 0373 default vs L2LAND's =1 records: EQUAL on all six.
- **Gate 3, controls that must DIFF, both kinds:**
  - operation level: =0 vs the default DIFFs on all six fixtures in the witness (mode 0 vs 1), the L2 count (0 vs
    10-43), the restored px, the GUI composite px and the presented px and boxes, while the default vs =1 is EQUAL on
    every one of them;
  - frame level, under the default: L2 marking nothing (C1) **DIFF 6049/7004**; rects 1 px short (C2) **DIFF
    2921/7004** (both from lc 5438, as in L2LAND).
- **Gate 4, forced checks under the default (unset): each EQUAL 7004/7004 against its forced =0 arm.** A control
  moved / resized (unsafe 140), GUI visibility / transparency toggled, a label's text grown and shrunk (194 L2 marks,
  verify 0 out), the slot cap forced to 2 (slots_overflow 4). Each =0 arm equals L2LAND's off arm and each default arm
  L2LAND's =1 arm, all eight.
- **Gate 5, release regression:** default vs =0, game lines EQUAL on 5 Days room 3 (30), Trilby room 35 (1121) and AGS
  Quest (356); parse-results PASS both.
- **Gate 6, P9:** the 0373 release default vs 0372's release 8c123c770d0b run with =1: EQUAL (78), and the guictrlmark
  counters are identical; 0373 =0 vs 0372's release unset: EQUAL (78).
- **Gate 7, ratchet: exe-bytes PASS at its limit (8,706,959), but code-lock-bytes moved +32 (5,228,176 > 5,228,144)**,
  against the expectation that 0373 moves neither. code-lock-bytes measures etext - start, the unpadded .text: the
  resolver's new expression moves etext +0x20 in the instrumented build (+0x10 in the release), inside the sections'
  512-byte padding, so the files stay 0372's size. **Proposed exact limit code-lock-bytes 5228176** (tests/ratchet.yaml
  on l2def, with a LIMIT comment); exe-bytes unchanged. One screen-alias check, screen-bench8-alias-anim12, came back
  FAIL with a VOID pair (FRZ01 froze at tick 300 vs 301), not a picture difference; on an idle re-run of the 13
  gate-alias checks it PASSes, 5 of 5 pairs equal (section 9).
- **Gate 8, clean builds:** both flavours build_dirty=0; a second full clean rebuild is byte-identical (cmp 0) in both.
  The exes are the same size as 0372's to the byte, section by section: 0373 changes a constant and comments only.
- **Guard check** (guardcheck.py over the vendor commit, tables/guardcheck.txt): both added lines lie inside existing
  `__DJGPP__` branches (draw.cpp @3223, quit.cpp @382); 0 unguarded.

## 1. Binaries (worktree /home/claude/data/worktrees/dosags-l2def, branch l2def off main 7e6b4ec3; patches/ags/0373)

| exe | what | sha256 | binary_sha12 | build_dirty | bytes |
|---|---|---|---|---|---|
| L2DINS | 0001-0373, instrumented | 5fc339413b605f4f974fe1b14e180496f7dfb68d72916f1b763d2cca3a8986ed | 39abbc4b5c34 | 0 | 8,706,959 |
| L2DREL | 0001-0373, release | 36473d6154f4a130dd0a0075f1b0431d1fdcfb1a7b42c81c994330abf1d91c4f | 942ad0260d36 | 0 | 8,668,817 |
| PREVREL | 0372's release (main's series, = L2LAND's L2REL), P9 reference | 5af21f2ad45877c92efe015f121c3beb3e28ed7389cc55ec34e472c8be335c00 | 8c123c770d0b | 0 | 8,668,817 |
| L2DGATE | 0001-0373 + gate-overlay.diff, instrumented (lab only) | fd00fd81376108814f42e7fff69c9446c307bc68b0acd4b0fd51c325c450d851 | f01b0b0670a8 | 1 | 8,738,828 |

- **Vendor tree.** `make patches` from the committed series gives vendor/ags tree c38ae4e5, the same tree as the
  authoring commit. Re-checked after the reboot, before the lane resumed: tree c38ae4e5, vendor/ags clean.
- **The final patch text.** After the gates, 0373's commit message got its Gates paragraph (it said "in progress"); the
  diff is unchanged. `make patches` from that text gives tree c38ae4e5 again (series fingerprint 1cac3e4c9d9c),
  vendor/ags clean, stamps 39abbc4b5c34 / 942ad0260d36 build_dirty=0. Both flavours were then rebuilt from the
  replayed tree (every object recompiled) and are `cmp` equal to L2DINS-A / L2DREL-A.
- **PREVREL** was rebuilt here from main's series (build-prev.sh) and is byte-identical to L2LAND's L2REL (same
  sha256).
- **Build A / build B.** build-clean.sh A, then build-gate.sh, then build-clean.sh B; each clean build removes
  build/ags and build/ags-release first. `cmp` L2DINS-A L2DINS-B and L2DREL-A L2DREL-B: both 0.
- **Stamps.** From `make build-dirty` / `DOSAGS_RELEASE=1 make build-dirty` after each build and again after the
  reboot (39abbc4b5c34 / 942ad0260d36, build_dirty=0), and from every cell's RUNMANI.LOG: f01b0b0670a8 build_dirty=1
  in the 30 gate cells, 942ad0260d36 build_dirty=0 in the 8 0373 release cells, 8c123c770d0b build_dirty=0 in the 2
  PREVREL cells. build/ags/ags.exe is `cmp` equal to L2DINS-A (checked after the reboot and again before the ratchet).
- **Against 0372** (L2LAND: 01658435489c / 8c123c770d0b, 8,706,959 / 8,668,817): **+0 bytes in both flavours**, and
  every section is the same size (objdump -h): instrumented .text 5,228,568, .data 735,232, .bss 571,904; release
  .text 5,196,824, .data 732,672, .bss 570,880 -- L2LAND section 1's 0372 figures.

## 2. The change (deliverable b)

- **Behaviour.** One expression in dos_gc2_mode() (Engine/ac/draw.cpp):

  | DOSAGS_GUI_CTRL_MARK | 0372 | 0373 |
  |---|---|---|
  | unset (or empty: DOS `SET X=` removes it) | 0, off | **1, on** |
  | exactly "0" | 0, off | 0, off |
  | exactly "1" | 1, on | 1, on |
  | anything else ("2", "off", "yes", "00") | 0, off | **1, on** |

  - 0372: `dos_gc2_mode_v = (e && e[0] == '1' && e[1] == 0) ? 1 : 0;`
  - 0373: `dos_gc2_mode_v = (e && e[0] == '0' && e[1] == 0) ? 0 : 1;`
- **Why an unknown value means on.** DOSAGS_CHAR_REUSE (0370), DOSAGS_GUI_CLIP (0368) and DOSAGS_VM (0359) all map an
  unknown value to their default. 0373 follows the same rule, so a mistyped value fails toward the default and only an
  exact "0" turns L2 off: "SET DOSAGS_GUI_CTRL_MARK=off" leaves L2 on, as "SET DOSAGS_CHAR_REUSE=off" leaves R2 on.
  Witnessed: I-X2 (=2) and I-Xoff (=off) print mode=1 and are frame-EQUAL to the intro default (1299/1299), with equal
  guictrlmark, restore, composite and present counters.
- **Witness** (unchanged format string): `DOS-PORT guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=1` when unset;
  `=0 mode=0`, `=1 mode=1`, `=2 mode=1`, `=off mode=1` as set. The RUNMANI line `DOS-PORT guictrlmark_final mode= l2=
  ...` is unchanged.
- **Comments touched** (0373 edits lines 0372 added):
  - Engine/ac/draw.cpp, the resolver: the trailing comment "unset / "0" = off (the default); exactly "1" = on; anything
    else = off" becomes a line above it, "patch 0373: unset or any other value = 1 (on, the default); exactly "0" = off
    (the 0371 head)";
  - Engine/main/quit.cpp, the RUNMANIFEST env allowlist entry: "(off by default)" becomes "(on by default since 0373; 0
    = off)".
- **docs/dist/README.TXT** (KNOWN LIMITS, script speed-ups): the fallback list now ends "SET DOSAGS_GUI_CLIP=0, SET
  DOSAGS_CHAR_REUSE=0 and SET DOSAGS_GUI_CTRL_MARK=0 (AGS's own interpreter and drawing, no skipping)". Rewrapped at
  72 columns.
- **Guard check** (tables/guardcheck.txt):

  | file | added lines | patched-file lines -> enclosing `#ifdef __DJGPP__` | unguarded |
  |---|---|---|---|
  | Engine/ac/draw.cpp | 2 | 3279-3280 (comment + resolver) -> the 0191 flush's guard @3223 | 0 |
  | Engine/main/quit.cpp | 1 | 420 (the allowlist line) -> the existing guard @382 | 0 |

- **Constraints.** ASCII only (checked on the patch, README.TXT and every record). No new getenv. No lab knob. No file
  I/O, no size_t change.

## 3. The overlay (L2LAND's, unchanged; gate-overlay.diff is the full vendor/ags diff over 0373)

- apply-overlay-l2land.py, apply-overlay-rb.py and apply-overlay-r3land.py are byte-identical to L2LAND's committed
  copies, and applied to 0373 without an edit.
- Their added and removed lines are identical to L2LAND's gate-overlay.diff (0373's resolver line is not one of the
  overlay's anchors).
- It is applied, built and reverted (build-gate.sh), never landed. Knobs used here: FRAMEHASH; LABCLICKS G / V / GCL /
  H; DOSAGS_LAB_GC2_VERIFY=1 (arms D and 1, reads only); DOSAGS_LAB_GC2_NOMARK=1 (C1), DOSAGS_LAB_GC2_SHORT=1 (C2);
  DOSAGS_LAB_GC2_MOVE=50, VIS=60, TEXT=40 (F1-F3), DOSAGS_LAB_GC2_CAP=2 (F4).

## 4. Fixtures, arms, witnesses

- **Fixtures** as L2LAND (MMD = Maniac Mansion Deluxe): G (save 007, exit 8600; 3164 loop counters), V (9400; 3964),
  GCL (12440; 7004), H (12440; 7004), intro (--startr 40, no save, exit 1300; 1299), AQ (AGS Quest AutoPilot; 3558).
- **Gate cells:** no --fixed-timestep (every tick rendered), fine timing off, no TICKLOG, DOSAGS_LAB_FRAMEHASH=1 +
  DOSAGS_PRESENT_VERIFY=1, DOSAGS_RANDSEED=1. DOSAGS_CHAR_REUSE and DOSAGS_ROUTE_PREWARM unset (R2 at its 0370
  default, L1 off).
- **Arm names** (0373 turned unset into 1, so the off arm sets =0 explicitly; L2LAND's "0" arm was unset):
  - D = DOSAGS_GUI_CTRL_MARK unset + DOSAGS_LAB_GC2_VERIFY=1; Dn = unset, no verify (C1, C2);
  - 1 = =1 + verify; Z = =0, no verify;
  - X2 = =2, Xoff = =off (no verify).
- **Witnesses** (tables/cellcheck-all.txt, all 40 cells): rc 0 and exit_code=0 in each.
  - fixed-timestep: DISABLED in the 30 gate cells, ENABLED in the 10 release cells.
  - guiclip (default) mode=4 and charreuse (default) mode=2 in every cell.
  - guictrlmark (default)/m1 in every default arm; 0/m0, 1/m1, 2/m1, off/m1 as set. P9-PREV-D (0372's release, unset)
    reads (default)/m0, as expected.
  - labclicks n=14 (G, V, H, C1, C2, F*) / 16 (GCL). RUN.BAT SET totals 119-289 bytes, longest line 38.
  - PRESENT_VERIFY stale frames 0 in every cell that runs it.
  - no_safe, mixed, props, norec, late and mismatch are 0 in all 40 cells; unsafe is non-zero only in F1-D (140, the
    forcing) and slots_overflow only in F4-D (4, the forcing).
- **Display and stage dirs.** Display 398 only, one DOSBox-X at a time (one serial lane; the host DOSBox-X lock
  serialized it with other sessions' cells); stage dirs and their .meta sidecars deleted per cell.

Compare, in this directory: `python3 fhcmp.py H-Z.FHASH.TXT H-D.FHASH.TXT` (by loop counter); `python3 eqcmp.py
P9-PREV-1.GAMELINES.TXT P9-REL-D.GAMELINES.TXT`. l2cmp.py and cellcheck.py read cell dirs (build/l2d/results, not
committed); tables/ holds their full output (tables.sh regenerates it).

## 5. Gates 1 and 2 -- the default vs =1, and =0 / =1 against 0372's records (L2DGATE)

| fixture | D vs 1 | D vs Z | Z vs L2LAND X-0 (0372 off) | 1 vs L2LAND X-1 | D vs L2LAND X-1 | PV stale (D; 1; Z) | guictrlmark_final (D): l2 (ctrls) / px / px_gui | verify px out (in), D and 1 |
|---|---|---|---|---|---|---|---|---|
| G | EQUAL 3164/3164 | EQUAL 3164/3164 | EQUAL 3164/3164 | EQUAL 3164/3164 | EQUAL 3164/3164 | 0; 0; 0 | 18 (18) / 54,400 / 328,320 | **0** (2,619) |
| V | EQUAL 3964/3964 | EQUAL 3964/3964 | EQUAL 3964/3964 | EQUAL 3964/3964 | EQUAL 3964/3964 | 0; 0; 0 | 19 (24) / 48,592 / 346,560 | **0** (4,122) |
| GCL | EQUAL 7004/7004 | EQUAL 7004/7004 | EQUAL 7004/7004 | EQUAL 7004/7004 | EQUAL 7004/7004 | 0; 0; 0 | 34 (34) / 127,616 / 620,160 | **0** (2,843) |
| H | EQUAL 7004/7004 | EQUAL 7004/7004 | EQUAL 7004/7004 | EQUAL 7004/7004 | EQUAL 7004/7004 | 0; 0; 0 | 16 (16) / 48,656 / 291,840 | **0** (1,732) |
| intro | EQUAL 1299/1299 | EQUAL 1299/1299 | EQUAL 1299/1299 | EQUAL 1299/1299 | EQUAL 1299/1299 | 0; 0; 0 | 10 (17) / 67,520 / 96,000 | **0** (7,746) |
| AQ (32-bit) | EQUAL 3558/3558 | EQUAL 3558/3558 | EQUAL 3558/3558 | EQUAL 3558/3558 | EQUAL 3558/3558 | 0; 0; 0 | 43 (43) / 86,698 / 180,440 | **0** (1,365) |

- **Totals.** 30 comparisons, all EQUAL. The verify ran in 12 cells (D and 1 on six fixtures): 280 checks, 0 px out.
- **Every count in this table equals L2LAND section 5's on-arm row** for the same fixture, and the D and 1 arms'
  guictrlmark_final lines are identical, field for field, on every fixture.
- **Unknown values** (intro): I-X2 vs I-D EQUAL 1299/1299, I-Xoff vs I-D EQUAL 1299/1299; both mode=1, l2 10 (17), and
  the same restore / composite / present counters as I-D (tables/opcmp-all.txt).

## 6. Gate 3 -- controls that must DIFF under the default

### 6a. Operation level: =0 vs the default, scored on what L2 changes (l2cmp.py)

L2 is exact, so =0 and the default are frame-EQUAL (section 5); this control reads what L2 does instead. The figures
are the startup witness, guictrlmark_final, and the running counters the engine prints on STDOUT every 500 scenes,
taken at the last checkpoint both arms reached:
- restore_px: bgstruct px, the background restored;
- gui_hitpx: rbstruct hitpx, the clipped GUI composite;
- present_px: dirtypresent px_narrow + px_full, the pixels presented;
- boxes: dirtypresent boxes, the present boxes.

| fixture | witness Z / D | l2 Z / D | checkpoint (scenes) | restore_px Z / D | gui_hitpx Z / D | present_px Z / D | present boxes Z / D | Z vs D | 1 vs D |
|---|---|---|---|---|---|---|---|---|---|
| G | 0 m0 / (default) m1 | 0 / 18 | 3000 | 9,098,755 / 8,686,105 | 3,863,232 / 3,777,073 | 21,602,169 / 21,119,657 | 3131 / 3140 | **DIFF** | EQUAL |
| V | 0 m0 / (default) m1 | 0 / 19 | 3500 | 3,695,929 / 3,395,542 | 19,640,975 / 19,620,572 | 29,373,309 / 29,020,364 | 3646 / 3655 | **DIFF** | EQUAL |
| GCL | 0 m0 / (default) m1 | 0 / 34 | 7000 | 31,640,409 / 31,040,424 | 1,155,294 / 932,254 | 59,557,919 / 58,811,053 | 7010 / 7017 | **DIFF** | EQUAL |
| H | 0 m0 / (default) m1 | 0 / 16 | 7000 | 4,483,489 / 4,086,789 | 9,262,562 / 9,170,086 | 32,361,229 / 31,817,089 | 7121 / 7116 | **DIFF** | EQUAL |
| intro | 0 m0 / (default) m1 | 0 / 10 | 1000 | 9,301,706 / 9,187,786 | 79,960 / 156,760 | 18,427,364 / 18,253,240 | 2545 / 2538 | **DIFF** | EQUAL |
| AQ | 0 m0 / (default) m1 | 0 / 43 | 3500 | 28,077,196 / 27,828,907 | 7,600,356 / 7,729,891 | 252,518,297 / 251,338,580 | 13291 / 13258 | **DIFF** | EQUAL |

- "EQUAL" in the last column means every one of those figures is equal between explicit =1 and the default.
- l2cmp.py also lists gui_fullpx among the DIFFing figures in every Z vs D row (tables/opcmp-all.txt).
- Not every figure goes down under the default: gui_hitpx goes up on the intro and AQ, and present boxes on G, V and
  GCL (by 7-9). Restored and presented px go down on all six. This control asks only that the figures DIFF; it is not
  a speed claim (that is round RG's). The pictures stay EQUAL (section 5).

### 6b. Frame level (the gate overlay's controls, fixture H, under the default)

| control | pair | result | counters (C arm) |
|---|---|---|---|
| C1 L2 marks nothing (NOMARK) | H-Z vs C1-D | **DIFF 6049/7004**, first lc 5438, last 12439 | l2 16, px 0 |
| C2 rects 1 px short on every side (SHORT) | H-Z vs C2-D | **DIFF 2921/7004**, first lc 5438, last 10647 | l2 16, px 40,272 |

Both equal L2LAND's C1-1 / C2-1 counts (6049 / 2921, from lc 5438). Game lines EQUAL (48) in both: the controls change
only the picture.

## 7. Gate 4 -- forced checks under the default (fixture H; each against its own forced =0 arm)

| forcing | default + forcing vs =0 + forcing | counters (default arm) | =0 arm vs L2LAND F?-0; default arm vs L2LAND F?-1 | forcing vs unforced H-Z |
|---|---|---|---|---|
| F1 a control moved +1 px / shrunk 1 px every 50 ticks (MOVE=50) | **EQUAL 7004/7004** | unsafe 140 (forced 140); l2 16; verify 16 / 0 out | EQUAL; EQUAL | DIFF 3500 |
| F2 GUI 0 hidden / transparency 10, every 60 ticks (VIS=60) | **EQUAL 7004/7004** | l2 12 (forced 117); verify 12 / 0 out | EQUAL; EQUAL | DIFF 3500 |
| F3 label text +13 characters / restored, every 40 ticks (TEXT=40) | **EQUAL 7004/7004** | l2 194, 732,176 px (forced 175); verify 194 / 0 out, 53,164 in | EQUAL; EQUAL | DIFF 89 |
| F4 slot cap forced to 2 (CAP=2) | **EQUAL 7004/7004** | **slots_overflow 4**; l2 12, verify 12 / 0 out | EQUAL; EQUAL | EQUAL (the cap changes nothing with L2 off) |

- Every =0 + forcing arm on 0373 equals L2LAND's off + forcing arm on 0372, and every default + forcing arm equals
  L2LAND's =1 + forcing arm: 8 comparisons, all EQUAL 7004/7004.
- Game lines EQUAL (48) for every F?-D vs F?-Z pair, and H-D vs H-Z.

## 8. Gates 5 and 6 -- release regression and P9 (L2DREL / PREVREL; game output lines, eqcmp.py; --fixed-timestep)

| pair | result | guictrlmark_final (default arm) |
|---|---|---|
| P9-REL-D (0373, unset) vs P9-PREV-1 (0372 8c123c770d0b, =1) | **EQUAL (78)** | both: l2 29 (29), px 63,840, px_gui 528,960, calc 41, cache_hits 3 -- the lines are identical |
| P9-REL-Z (0373, =0) vs P9-PREV-D (0372, unset) | **EQUAL (78)** | both mode 0, l2 0 |
| P9-PREV-D / P9-PREV-1 vs L2LAND's committed P9-REL-0 / P9-REL-1 lines | EQUAL (78) / EQUAL (78) | same 0372 binary, re-run |
| RG-5D3S-D vs -Z (5 Days room 3, exit 3000) | exit 0/0, **EQUAL (30)** | mode 1, l2 0 |
| RG-TN35-D vs -Z (Trilby room 35, MSGSKIP=1) | exit 0/0, **EQUAL (1121)** | mode 1, l2 0 |
| RG-AQ-D vs -Z (AGS Quest AutoPilot) | exit 0/0, **EQUAL (356)**; parse-results PASS both | l2 41 (41), px 83,134 |

Every release cell shows fixed-timestep ENABLED, guiclip (default) mode=4, charreuse (default) mode=2 and its binary's
stamp with build_dirty=0 (942ad0260d36 for 0373, 8c123c770d0b for 0372), and the guictrlmark witness ((default) mode=1
or =0 mode=0 on 0373; (default) mode=0 or =1 mode=1 on 0372). The release counts equal L2LAND's =1 release cells (P9
l2 29, AQ l2 41, 5 Days and Trilby l2 0).

## 9. Gate 7 -- ratchet (instrumented L2DINS 39abbc4b5c34 = build/ags/ags.exe)

`.sdl-dos-ports/shared/tools/ratchet.sh --root <l2def> --no-build --no-host-wait --capture-display 398 --no-record
--lock-wait 7200`, with all nine game packages present (5days, 7days, agsquest, bench16, bench8, bench8old, mmd, shards,
trilbysnotes). build/ags/ags.exe is `cmp` equal to L2DINS-A. The second run adds `--only` with the 13 gate-alias checks.

| run | machine | result |
|---|---|---|
| 20261111T202520Z (RATCHET-20261111T202520Z-*) | it first waited on the ratchet lock for another worktree's ratchet (dosags-cap3) to finish, then ran alone under the host DOSBox-X lock | 39 pass (10 improved), **2 fail**, 4 quarantined. **exe-bytes 8706959 PASS (limit 8706959). code-lock-bytes 5228176 FAIL (limit 5228144).** screen-bench8-alias-anim12 FAIL 1: FRZ01 VOID, froze at tick 300 (A) vs 301 (B), not comparable; FRZ00, FRZ02-04 equal. Every other screen-alias check PASS. screen-shards-alias-512x384 FAIL(q) 1 (FRZ00 DIFFERS 254,984 px; FRZ01-04 equal); its fixed-40k twin PASS(q) |
| 20261111T212649Z (RATCHET-20261111T212649Z-*; `--only` the 13 gate-alias checks) | idle (load ~1, no other DOSBox-X) | **PASS: 12 pass, 0 fail, 1 quarantined.** screen-bench8-alias-anim12 PASS, 5 of 5 pairs equal; every other bench8 / bench16 / 5 Days alias check PASS; screen-shards-alias-512x384 FAIL(q) 2 (FRZ00 VOID, A=100 B=101; only 4 comparable pairs) |
| 0373's delta vs 0372 (0001-0372) | -- | exe +0 (both flavours); code-lock **+32** (instrumented etext 0x4fe080 here; L2LAND's 5228144 at the same start 0x19f0 is 0x4fe060; release etext 0x4f64b0 -> 0x4f64c0, measured here on PREVREL / L2DREL-A) |
| proposed limits (exact, no headroom; tests/ratchet.yaml on l2def, with a LIMIT comment) | -- | **code-lock-bytes 5228144 -> 5228176; exe-bytes stays 8706959** |

- **Why code-lock moved and the exe did not.** SDL 0194 locks [start=0x19f0, etext), and ratchet-facts.py reads that
  length from SDLDBG.LOG. etext is the end of the code itself; objdump's .text size is rounded up to 512 bytes, and
  the exe's size follows the rounded sections. 0373's resolver compiles 16 bytes longer (one alignment step) in the
  release build and 32 in the instrumented one, which stays inside the last 512-byte block: .text, .data and .bss are
  the same size as 0372's in both flavours (section 1).
- **Why the anim12 FAIL is not 0373's.** The pair that failed is VOID (the two captures froze one tick apart), not a
  pixel difference; the four pairs that could be compared were equal. gate-alias runs at cycles=max and is
  load-sensitive. On the idle re-run the same check compares 5 of 5 pairs equal. R2DEF re-ran its alias checks the
  same way.
- **The shards FAIL(q)** is the quarantined check's known freeze-tick drift at FRZ00 (L2LAND, L1LAND, R2DEF and R2LAND
  show the same). It never gates. Its fixed-40k twin, which removes the host-timing dependence, PASSes.
- **Not re-run.** Every unit of run 1 but gate-alias is kept as it ran: the fixed-40k units, the sb-live units, the
  clicks and both size checks. They all passed or improved, except code-lock-bytes (above).
- **The 10 IMPROVED values are the run's, not this change's** (AQ journey p95s, sb-live clock and PCM counters, the
  MIDI stall count; the same checks improved in L2LAND's run). Limits are not lowered here.

## 10. Caveats -- what was not exercised, what was not tested

- **Not exercised naturally** (as in L2LAND):
  - late (a flag set between the flush and the redraw) and mismatch: 0 in all 40 cells;
  - mixed and no_safe (an unmatched MarkControlChanged): 0 everywhere;
  - a 32-bit alpha GUI (props): AQ's GUIs have no alpha channel;
  - a macro label on an L2 GUI;
  - unsafe and slots_overflow fired only under their forcings (F1, F4).
- **L2 never engaged in two of the three release games:** 5 Days room 3 and Trilby room 35 read l2 0 under the default
  (as under =1 in L2LAND); their EQUAL lines say L2 is inert there, not that it is exact there.
- **Not tested:**
  - GUIs drawn as textures (draw_controls_as_textures, a hardware renderer): the DOS software renderer never takes that
    path;
  - a translation or font change while L2 is on (the cache key covers both; no fixture changes them);
  - the verify at more than 16 controls (overflow is forced, F4, not natural);
  - L1 + L2 together under the new default (L2LAND's HP pair ran it with =1 explicit; not re-run here);
  - the empty value: DOS's `SET X=` removes the variable, so it is the unset case; the resolver maps "" to 1 as well;
  - timing: nothing here is timed; the speed claim is round RG's, on the 486.
