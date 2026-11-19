# R2DEF-2026-11-08 -- landing records for ags 0370 (lever R2, DOSAGS_CHAR_REUSE, on by default)

DOSBox-X only (cycles=fixed 40000, tests/harness/confs/dosbox-x-fixed40k-opl3.conf); no rig, no vcctrl. Text records
only: frame digests (FHASH.TXT), RUNMANI.LOGs, the game-output lines each equivalence read (GAMELINES.TXT),
parse-results JSON, the cell command lines (CELL.txt, stage dir masked), the overlay and its apply scripts, the lane and
build scripts, the compare tools, the compare output (tables/), the ratchet reports. No images, no game data. Why the
default changed: tests/harness/results/ROUNDRD-2026-11-08/README.md (the 486 round RD: +1.34 points displayed in MMD in
play with R2). Lever design: docs/lab/LAB-R2.md section 6, docs/lab/LAB-R2B.md; the lever's own landing records:
tests/harness/results/R2LAND-2026-11-07. Cells ran 2026-11-08 09:46 to 12:41 PST.

## 0. Answer first

- **0370 makes R2 the default.** DOSAGS_CHAR_REUSE unset (or any value other than exactly "0" or "1") gives mode 2,
  R2a + R2b. Exactly "0" is off; exactly "1" is R2a. The witness reads "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default)
  mode=2" when unset. No new getenv, no lab knob, nothing else in the lever changes.
- **The choice for unknown values (for sdlports' review): they read as mode 2.** A mistyped value ("3", "off", "00",
  " 0") fails toward the default; only an exact "0" turns R2 off. Witnessed: =3 and =off print mode=2 and render
  frame-EQUAL to the default (section 2).
- **Gate 1, default vs explicit =2: frame-EQUAL on all five fixtures** (G 3164, V 3964, GCL 7004, intro 1299, AQ 3558
  loop counters). Every charreuse counter is equal too, and so are the restore, composite and present counters.
- **Gate 2, =0 on 0370 vs the 0369 default-off records (R2LAND X-0): EQUAL on all five.** =1 on 0370 vs R2LAND's =1
  records: EQUAL on all five. Extra: the 0370 default vs R2LAND's =2 records, EQUAL on all five.
- **Gate 3, controls that must DIFF, both kinds:**
  - operation level (sdlports' added control): =0 vs the default DIFFs on all five fixtures in the witness (mode 0 vs
    2), the skips (0 vs 1,937-11,197), the restored px, the GUI composite px and the presented px and boxes, while the
    default vs =2 is EQUAL on every one of them;
  - frame level: NODRAW (no per-box redraw) DIFFs 3023/3164 on G and 6487/7004 on GCL; the key without the baseline
    (NOBASEL) DIFFs 980/3164 under a forced baseline change.
- **Gate 4, forced fallbacks under the default (unset): each EQUAL against its forced =0 arm, each off-control DIFF.**
  Old-rect mark (DIFF 590 off), 0366's latch (1440), whole invalidation (14), 0368's coarse flag (no off knob, EQUAL),
  dynamic sprite edited in place (2989), walk-behind mask edited (1847). Every count equals R2LAND's.
- **Gate 5, release regression:** default vs =0, game lines EQUAL on 5 Days room 3 (30), Trilby room 35 (1121) and AGS
  Quest (356); parse-results PASS both.
- **Gate 6, P9:** the 0370 release default vs main's release 84c1a74fdcf6 run with =2: EQUAL (78); 0370 =0 vs main's
  release unset: EQUAL (78). The R2 counters of the first pair are identical.
- **Gate 7, ratchet:** exe-bytes and code-lock-bytes PASS at their current limits (8,695,597 / 5,221,072), so no new
  limits are proposed. The screen-alias checks pass on an idle re-run (section 9).
- **Gate 8, clean builds:** both flavours build_dirty=0; a second full clean rebuild is byte-identical (cmp 0) in both.
  The exes are the same size as 0369's to the byte: 0370 changes constants and comments only.

## 1. Binaries (worktree ~/git/dosags-r2def, branch r2def off main 478b8f21; patches/ags/0370)

| exe | what | sha256 | binary_sha12 | build_dirty | bytes |
|---|---|---|---|---|---|
| R2DINS | 0001-0370, instrumented | 8179d8e9c5a687fb90a8700eff5731ae1f1f2fc376710fbfda49519431f22a2e | 27a296a5b589 | 0 | 8,695,597 |
| R2DREL | 0001-0370, release | f9202de6ffc795000b32b55138424a97038fe49f8010b1d238ccd0697fd240e1 | 9db4170acd89 | 0 | 8,657,967 |
| MAINREL | main's release (0001-0369, = R2LAND's R2REL), P9 reference | ffe49dab2c137748d91bbbace337590556cc1086b0420f6183e342deaee0282a | 84c1a74fdcf6 | 0 | 8,657,967 |
| R2DGATE | 0001-0370 + gate-overlay.diff, instrumented (lab only) | 97e77079311c6f25e95419b92341d63763d2535325200e49833f84bf247820da | fb4de6f93f76 | 1 | 8,720,399 |

- `make patches` from the committed series gave vendor/ags tree 94006bb9, the same tree as the authoring commit.
- Build A was the first build in the fresh worktree. Build B removed build/ags and build/ags-release and rebuilt both
  flavours: `cmp` R2DINS-A R2DINS-B and R2DREL-A R2DREL-B both 0.
- The stamps come from `make build-dirty` and `DOSAGS_RELEASE=1 make build-dirty` after each build, and from every
  release cell's RUNMANI.LOG (binary_sha12=9db4170acd89 build_dirty=0).
- Against main's f9f8dd6614c8 / 84c1a74fdcf6: +0 bytes in both flavours (R2INS 8,695,597, R2REL 8,657,967).

## 2. The change (deliverable b)

- **Behaviour.** One expression in dos_char_reuse_mode() (Engine/ac/draw.cpp):

  | DOSAGS_CHAR_REUSE | 0369 | 0370 |
  |---|---|---|
  | unset (or empty: DOS `SET X=` removes it) | 0, off | **2** |
  | exactly "0" | 0 | 0, off |
  | exactly "1" | 1, R2a | 1, R2a |
  | exactly "2" | 2 | 2 |
  | anything else ("3", "off", "yes", "00") | 0 | **2** |

- **Why an unknown value means 2.** DOSAGS_GUI_CLIP (0368) and DOSAGS_VM (0359) both map an unknown value to their
  default, and DOSAGS_ENGLEV turns off only on a leading "0". 0370 follows the same rule, so a mistyped value fails
  toward the default and only an exact "0" turns R2 off. A player has to type the documented "=0":
  "SET DOSAGS_CHAR_REUSE=off" leaves R2 on, as "SET DOSAGS_GUI_CLIP=off" leaves R3 on.
  Witnessed: I-X3 (=3) and I-Xoff (=off) print mode=2 and are frame-EQUAL to the intro default (1299/1299), with equal
  charreuse and present counters.
- **Comments and doc strings touched in the series** (0370 edits lines 0369 added):
  - Engine/ac/draw.cpp, the lever's header: "unset or 0 = off (the 0368 head)" becomes "0 = off (the 0368 head); ... 2 =
    R2a + R2b, the default since patch 0370 (unset or any other value)";
  - Engine/ac/draw.cpp, the resolver: a new one-line comment over the changed expression;
  - Engine/main/quit.cpp, the RUNMANIFEST env allowlist entry: "(0 off by default; 1 = R2a; 2 = R2a + R2b)" becomes "(2
    = R2a + R2b, on by default since 0370; 0 = off; 1 = R2a)".
  - No other comment in 0369 says off by default. The witness format string is unchanged.
- **docs/dist/README.TXT** (KNOWN LIMITS, script speed-ups): the example of skipped work now names "interface panels
  and characters nothing has touched", and the fallback list ends "SET DOSAGS_GUI_CLIP=0 and SET DOSAGS_CHAR_REUSE=0
  (AGS's own interpreter and drawing, no skipping)". Rewrapped at 72 columns.
- **The optional cleanup: in, partly.** 0369's `dos_cr_wb_gen++` in Engine/ac/dynobj/scriptdrawingsurface.cpp now sits
  under `#ifdef __DJGPP__`, like its definition in Engine/ac/walkbehind.cpp. On DOS nothing changes (the gate, P9 and
  regression results above are on this tree).
  - **0319's dos_walkmask_gen line next to it is left unguarded, on purpose.** dos_walkmask_gen is defined without a
    guard in Engine/ac/walkablearea.cpp, the legacy pathfinder's cache that reads it (route_finder_impl_legacy.cpp,
    dos_walktemp_serial) is built on every platform, and 0319's other bumps (ac/room.cpp, plugin/agsplugin.cpp,
    game/savegame.cpp) are unguarded too. Guarding this one bump would leave a non-DOS build's path cache stale after a
    script draws on the walkable mask, a behaviour change off DOS.
  - The new comment says so.
- **Constraints.** ASCII only (checked on every touched file and record). No new getenv. No lab knob. No fopen and no
  size_t change.

## 3. The overlay (R2LAND's, unchanged; gate-overlay.diff is the full vendor/ags diff over 0370)

- apply-overlay-r2land.py (which runs apply-overlay-r2b.py, which runs apply-overlay-r3land.py) applied to 0370
  without an edit.
- Its added and removed lines are identical to R2LAND's gate-overlay.diff; only the hunk offsets moved (0370 adds a
  line above them in draw.cpp).
- It is applied, built and reverted (build-gate.sh), never landed. Knobs as in R2LAND section 2: FRAMEHASH, LABCLICKS
  G / V / GCL, CR_VERIFY, CR_NODRAW, CR_NOBASEL, CR_TOGGLE, CR_CAM, CR_BASEL, CR_NOMARK, CR_NOLATCH, CR_NOCAM,
  FORCE_WHOLE, SPANMAX / SPANPROBE, CR_DYN / CR_NONOTIFY, CR_WBM / CR_NOWBGEN.

## 4. Fixtures, arms, witnesses

- **Fixtures** (R2LAND's; MMD = Maniac Mansion Deluxe): G (save 007, room 1 -> 2, exit 8600; 3164 loop counters), V
  (G + the verb bar, exit 9400; 3964), GCL (LAB-L1's 16 clicks, exit 12440; 7004), intro (--startr 40, exit 1300;
  1299), AQ (AGS Quest AutoPilot; 3558).
- **Gate cells:** no --fixed-timestep (every tick rendered), fine timing off, no TICKLOG, DOSAGS_LAB_FRAMEHASH=1 +
  DOSAGS_PRESENT_VERIFY=1, DOSAGS_RANDSEED=1.
- **Arm names** (0370 turned unset into 2, so the off arm sets =0 explicitly):
  - D = DOSAGS_CHAR_REUSE unset + DOSAGS_LAB_CR_VERIFY=1; Dn = unset, no verify (controls, forcings, guiclip extras);
  - 2 = =2 + verify; 1 = =1 + verify; Z = =0, no verify;
  - N = the default + the forcing + the guard's off knob.
  - R2LAND's dynamic-sprite cells were G-D-*; here they are G-Y-* (D is the default arm).
- **Witnesses** (tables/cellcheck-all.txt, all 58 cells): rc 0 and exit_code=0 in each.
  - fixed-timestep: DISABLED in the 48 gate cells, ENABLED in the 10 release cells.
  - The guiclip witness is in every cell (=(default) mode=4, or =0 / =2 in G-G0-* / G-G2-*).
  - The charreuse witness is in every cell: (default)/m2 in every default arm, 0/m0, 1/m1, 2/m2, 3/m2, off/m2 as set.
    P9-MAIN-D (main's 0369, unset) reads (default)/m0, as expected.
  - labclicks n=14 (G, V) / 16 (GCL). RUN.BAT SET totals 119-310 bytes, longest line 38.
  - PRESENT_VERIFY stale frames are 0 in every gate cell but G-L-N (the latch control: 1429 frames, 2,569,638 px, as in
    R2LAND).
- **Stage dirs** were deleted per cell. Displays 396/397 only, at most two DOSBox-X of this worktree at once.

Compare, in this directory: `python3 fhcmp.py G-Z.FHASH.TXT G-D.FHASH.TXT` (by loop counter); `python3 eqcmp.py
P9-MAIN-2.GAMELINES.TXT P9-REL-D.GAMELINES.TXT`. opcmp.py (new here) and cellcheck.py read cell dirs (build/r2d/results,
not committed); tables/ holds their full output (tables.sh regenerates it).

## 5. Gates 1 and 2 -- the default vs =2, and =0 / =1 against 0369's records (R2DGATE)

| fixture | D vs 2 | D vs Z | Z vs R2LAND X-0 (0369 off) | 1 vs R2LAND X-1 | D vs R2LAND X-2 | verify checks / mismatches (D) | D: hits / skips / drv skipped / boxed (boxes) / full | forced_full | mark_old (key/reset) |
|---|---|---|---|---|---|---|---|---|---|
| G | EQUAL 3164/3164 | EQUAL 3164/3164 | EQUAL 3164/3164 | EQUAL 3164/3164 | EQUAL 3164/3164 | 5780 / 0 | 5780 / 5716 / 3023 / 1114 (1134) / 1579 | 64 (full) | 8 (5/3) |
| V | EQUAL 3964/3964 | EQUAL 3964/3964 | EQUAL 3964/3964 | EQUAL 3964/3964 | EQUAL 3964/3964 | 6717 / 0 | 6717 / 6653 / 3023 / 1114 (1134) / 2516 | 64 (full) | 6 (3/3) |
| GCL | EQUAL 7004/7004 | EQUAL 7004/7004 | EQUAL 7004/7004 | EQUAL 7004/7004 | EQUAL 7004/7004 | 11261 / 0 | 11261 / 11197 / 4839 / 2405 (2462) / 3953 | 64 (full) | 19 (16/3) |
| intro | EQUAL 1299/1299 | EQUAL 1299/1299 | EQUAL 1299/1299 | EQUAL 1299/1299 | EQUAL 1299/1299 | 2033 / 0 | 2033 / 1937 / 1404 / 2 (2) / 531 | 96 (cam 80, full 16) | 4 (2/2) |
| AQ | EQUAL 3558/3558 | EQUAL 3558/3558 | EQUAL 3558/3558 | EQUAL 3558/3558 | EQUAL 3558/3558 | 3868 / 0 | 3868 / 3862 / 2789 / 1073 (1126) / 0 | 6 (full) | 530 (525/5) |

- **Totals.** 25 comparisons, all EQUAL. The verify ran in 17 cells (D, 2, 1 on five fixtures, plus
  G-Y-D and G-W-D): 98,502 checks, 0 mismatches.
- keyfail 0, refused 0 and mo_end 0 in all 58 cells.
- Every count in this table equals R2LAND section 5's mode-2 row for the same fixture. The =1 arms take the same hits
  with 0 skips, as in R2LAND.
- ff_latch, ff_coarse and ff_multi are 0 in every unforced cell, as in R2LAND.

## 6. Gate 3 -- controls that must DIFF under the default

### 6a. Operation level (sdlports): =0 vs the default, scored on what R2 changes (opcmp.py)

R2 is exact, so =0 and the default are frame-EQUAL (section 5); this control reads what R2 does instead. The figures
are the startup witness, charreuse_final, and the running counters the engine prints on STDOUT every 500 scenes, taken
at the last checkpoint both arms reached:
- restore_px: bgstruct px, the background restored;
- gui_hitpx: rbstruct hitpx, the clipped GUI composite;
- present_px: dirtypresent px_narrow + px_full, the pixels presented;
- boxes: dirtypresent boxes, the present boxes.

Gate cells run fine timing off, so there are no per-tick tickstats; these running counters are the per-run present and
blit counts.

| fixture | witness Z / D | skips Z / D | checkpoint (scenes) | restore_px Z / D | gui_hitpx Z / D | present_px Z / D | present boxes Z / D | Z vs D | 2 vs D |
|---|---|---|---|---|---|---|---|---|---|
| G | 0 m0 / (default) m2 | 0 / 5716 | 3000 | 18,875,609 / 9,098,755 | 9,969,906 / 3,863,232 | 67,215,313 / 21,602,169 | 7542 / 3131 | **DIFF** | EQUAL |
| V | 0 m0 / (default) m2 | 0 / 6653 | 3500 | 14,784,011 / 3,695,929 | 37,894,093 / 19,640,975 | 110,814,495 / 29,373,309 | 8696 / 3646 | **DIFF** | EQUAL |
| GCL | 0 m0 / (default) m2 | 0 / 11197 | 7000 | 51,567,333 / 31,640,409 | 4,320,847 / 1,155,294 | 157,106,011 / 59,557,919 | 15764 / 7010 | **DIFF** | EQUAL |
| intro | 0 m0 / (default) m2 | 0 / 1937 | 1000 | 9,459,649 / 9,301,706 | 3,459,460 / 79,960 | 37,407,830 / 18,427,364 | 3371 / 2545 | **DIFF** | EQUAL |
| AQ | 0 m0 / (default) m2 | 0 / 3862 | 3500 | 32,116,027 / 28,077,196 | 7,497,768 / 7,600,356 | 298,054,071 / 252,518,297 | 15628 / 13291 | **DIFF** | EQUAL |

"EQUAL" in the last column means every one of those figures is equal between explicit =2 and the default.

### 6b. Frame level (the gate overlay's controls; fixture G unless named)

| control | arms | result |
|---|---|---|
| (i) no per-box redraw | G-D-NODRAW vs G-Z; GCL-D-NODRAW vs GCL-Z | **DIFF 3023/3164** (G), **DIFF 6487/7004** (GCL) |
| (ii) the key without the baseline | BASEL=7 (1596 forced): G-B-D vs G-B-Z EQUAL 3164/3164; G-B-N (NOBASEL) vs G-B-Z | **DIFF 980/3164** |

## 7. Gate 4 -- forced fallbacks and in-place edits under the default (fixture G; each against its own forced =0 arm)

| guard | forcing | default + forcing vs =0 + forcing | off-control vs =0 + forcing | fires (default arm) |
|---|---|---|---|---|
| (1) old-rect mark | TOGGLE=7 | G-T-D **EQUAL 3164/3164** | G-T-N (NOMARK) **DIFF 590/3164** | toggles 208; mo_off 206, mark_old 214 |
| (2) 0366's latch | FORCE_WHOLE=7 | G-L-D **EQUAL 3164/3164** | G-L-N (NOLATCH) **DIFF 1440/3164**, PV stale 1429 frames / 2,569,638 px | forced 456, latch_fullrestore 439; ff_latch 815; NOLATCH drv_latched 225 |
| (2) whole invalidation | CAM=7 | G-C-D **EQUAL 3164/3164** | G-C-N (NOCAM) **DIFF 14/3164** (lc 5700-6007) | cam_forced 456; ff_full 880 |
| (2) 0368's coarse flag | SPANMAX=1, SPANPROBE=7:166 | G-S-D **EQUAL 3164/3164** | -- (no R2-only off knob) | probes 456, span_stretch 213,348, fb_coarse 3047; ff_coarse 5451 |
| dynamic sprite edited in place | DYN=7 (825 edits, 5 dynamic copies) | G-Y-D **EQUAL 3164/3164** (verify 4955/0) | G-Y-N (NONOTIFY) **DIFF 2989/3164** | dyn_refused 820; mo_key 819; NONOTIFY hits 5716 |
| walk-behind mask edited | WBM=7 (412 fills, 412 restores) | G-W-D **EQUAL 3164/3164** (verify 4570/0) | G-W-N (NOWBGEN) **DIFF 1847/3164** | wbm_refused 1206; mo_key 818; NOWBGEN wbm_ignored 1206 |

- **The =0 + forcing arms on 0370 equal R2LAND's mode-0 + forcing arms on 0369**, all seven (G-T, G-L, G-C, G-S, G-B,
  G-Y = R2LAND G-D, G-W), EQUAL 3164/3164 each.
- **Against unforced G-Z:** G-L-Z, G-C-Z and G-S-Z are EQUAL (they change what is restored, never the picture). G-T-Z
  (206), G-B-Z (1049), G-Y-Z (3029) and G-W-Z (1716) DIFF by construction, as in R2LAND.
- **Extras, the default under the other guiclip modes.** G-G0-Dn vs G-G0-Z (DOSAGS_GUI_CLIP=0, README.TXT's fallback
  with R2 left on): EQUAL 3164/3164; 5716 skips, not flagged, drawn in full. G-G2-Dn vs G-G2-Z (=2): EQUAL 3164/3164;
  skipped 3011, clipped 1126, full 1579. The =0 arms of both equal R2LAND's G-G0-0 / G-G2-0.

## 8. Gates 5 and 6 -- release regression and P9 (R2DREL / MAINREL; game output lines, eqcmp.py; --fixed-timestep)

| pair | result | R2 counters (default arm) |
|---|---|---|
| P9-REL-D (0370, unset) vs P9-MAIN-2 (main 84c1a74fdcf6, =2) | **EQUAL (78)** | both: hits 6027, skips 5979, mark_old 3, drv skipped 5945, boxed 34 -- identical |
| P9-REL-Z (0370, =0) vs P9-MAIN-D (main, unset) | **EQUAL (78)** | both mode 0, 0 hits |
| P9-MAIN-2 / P9-MAIN-D vs R2LAND's P9-REL-2 / P9-MAIN-D lines | EQUAL (78) / EQUAL (78) | same main binary, re-run |
| RG-5D3S-D vs -Z (5 Days room 3, exit 3000) | exit 0/0, **EQUAL (30)** | skips 857, all drawn in full; mark_old 11 |
| RG-TN35-D vs -Z (Trilby room 35, MSGSKIP=1) | exit 0/0, **EQUAL (1121)** | skips 2299, all drawn in full; mark_old 767 |
| RG-AQ-D vs -Z (AGS Quest AutoPilot) | exit 0/0, **EQUAL (356)**; parse-results PASS both | skips 3794 (2749 skipped, 1045 boxed) |

Every release cell shows fixed-timestep ENABLED, guiclip (default) mode=4 and its binary's stamp with build_dirty=0
(9db4170acd89 for 0370, 84c1a74fdcf6 for main), and the charreuse witness ((default) mode=2 or =0 mode=0 on 0370;
(default) mode=0 or =2 mode=2 on main).

## 9. Gate 7 -- ratchet (instrumented R2DINS 27a296a5b589 = build/ags/ags.exe)

`.sdl-dos-ports/shared/tools/ratchet.sh --root <r2def> --no-build --no-host-wait --capture-display 397 --no-record`;
the second run adds `--only` with the 14 alias checks named below.

| run | machine | result |
|---|---|---|
| 20261108T204548Z (RATCHET-20261108T204548Z-*) | shared: the lead chose to run it while another session's serial DOSBox-X chain (~/git/dosags-lab-rb, docs/lab/l1r-lab/chainG.sh) was running | 30 pass (10 improved), 11 ERROR, 4 quarantined. **exe-bytes 8695597 PASS (limit 8695597); code-lock-bytes 5221072 PASS (limit 5221072).** The 11 ERRORs are all screen-bench8/bench16-alias checks; screen-shards-alias-512x384 and its -fixed40k twin were ERROR(q). screen-5days-alias-512x384 PASS |
| 20261108T222850Z (RATCHET-20261108T222850Z-*; `--only` the 11 errored checks, both shards checks and the 5 Days alias check) | idle, after that chain had exited (load 0.6, no other DOSBox-X) | **PASS: 12 pass, 0 fail, 2 quarantined.** All 11 bench alias checks PASS (screen-equal on every compared pair); screen-5days-alias-512x384 PASS, 5 of 5 pairs equal; screen-shards-alias-512x384-fixed40k PASS(q); screen-shards-alias-512x384 FAIL(q) 1 (FRZ00 only, the rest equal) |
| 0370's delta vs main (0001-0369) | -- | exe +0 (instrumented), +0 (release); code-lock +0 |
| proposed limits | -- | **none: exe-bytes 8695597 and code-lock-bytes 5221072 stay as they are; tests/ratchet.yaml is unchanged on r2def** |

- **Why the second run, and which units.** Run 1's errors were not load and not the binary. They came from this
  worktree's setup: only the 5days, agsquest, mmd and trilbysnotes packages had been copied into
  tests/harness/games/. gate-alias's cells for bench8, bench16 and shards stopped at "run-dosbox.sh: no .ags package
  under .../games/bench8 -- run build-package.sh first" (18 bench8 cells, 4 bench16, 2 shards; gate-alias 77 s instead
  of R2LAND's 944 s). gate-shards-fixed stopped the same way after 2 s.
- **What was re-run.** The missing packages (7days, bench16, bench8, bench8old, shards) were copied from main's
  tests/harness/games. Then the gate-alias and gate-shards-fixed units were re-run, with exactly the checks that read
  them, once the machine was idle, as the lead asked (load-sensitive at cycles=max).
- **Not re-run.** Every other unit of run 1 is kept as it ran on the shared machine: the fixed-40k units, the sb-live
  units, the clicks and both size checks. They all passed or improved.
- **The shards FAIL(q).** FRZ00 at tick 100 differs (243,252 px); FRZ01-FRZ04 are equal. This is the quarantined
  check's known freeze-tick drift, the same one R2LAND recorded (FAIL(q) 2 there, FRZ00 A=100 B=101). It never gates.
  Its fixed-40k twin, which removes the host-timing dependence, PASSes.
- **Every other check** is PASS or IMPROVED, as in R2LAND's run.

## 10. Caveats -- what did not fire naturally, what was not tested

- **Never fired naturally** in any unforced cell, as in R2LAND:
  - ff_latch, ff_coarse, ff_multi;
  - keyfail, refused, mo_end (0 in all 58 cells, forced ones included);
  - latch_fullrestore, span_stretch;
  - a dynamic-sprite edit, a walk-behind mask edit.
- **How those were exercised instead.** The latch, the whole invalidation, the coarse flag, the old-rect mark and both
  in-place edits only by forcing (section 7). The coarse flag has no R2-only off knob, so it has no DIFF arm.
- **Not tested:**
  - the one-viewport guard (ff_multi): no fixture has two room viewports;
  - a real camera move (LAB-R2B's CAM=7:1), not re-run here or in R2LAND; the whole-invalidation forcing was;
  - mode 1 under the forcings;
  - DOSAGS_GUI_CLIP=1 with the default (R2LAND gated =2 under it, EQUAL on G);
  - the empty value: DOS's `SET X=` removes the variable, so it is the unset case; the resolver maps "" to 2 as well;
  - timing: nothing here is timed; the speed claim is round RD's, on the 486.
