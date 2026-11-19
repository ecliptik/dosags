# L2LAND-2026-11-09 -- landing records for ags 0372 (lever L2, DOSAGS_GUI_CTRL_MARK, default off)

DOSBox-X only (cycles=fixed 40000, tests/harness/confs/dosbox-x-fixed40k-opl3.conf); no rig, no vcctrl. Text records
only: frame digests (FHASH.TXT), RUNMANI.LOGs, the game-output lines each equivalence read (GAMELINES.TXT),
parse-results JSON, the cell command lines (CELL.txt, stage dir masked), the overlay and its apply scripts, the lane and
build scripts, the compare tools, the compare output (tables/), the ratchet reports. No images, no game data. Lever
design and lab numbers: docs/lab/LAB-L2G.md section 8 (its cells in docs/lab/l2g-lab/cells-s8, on branch lab-rb),
docs/lab/LAB-RB.md section 3.1. Cells ran 2026-11-08 23:22 to 2026-11-09 03:44 PST.

## 0. Answer first

- **0372 = LAB-L2G section 8's slim lever, unchanged in code.** lab-l2g2.diff (lever-l2g-slim.py) was applied as is to
  0371. Three kinds of change:
  - its "lab L2G" comments now read "patch 0372" (22 places);
  - the mode comment says what other values do, and draw.cpp's lever comment describes the lever instead of pointing
    at the lab script;
  - **`#ifdef __DJGPP__` around draw.cpp's three new #includes** (gui/guilabel.h, <string.h>, ac/global_translation.h).
    They were the only added lines outside a `__DJGPP__` branch (build/l2's guardcheck.py, every hunk). quit.cpp's
    allowlist line already sits inside an existing `__DJGPP__` block.
  - With these removed, the added lines equal lab-l2g2.diff's line for line.
- **DOSAGS_GUI_CTRL_MARK:** unset or "0" = off (the default); exactly "1" = on; **any other value = off**. The witness is
  read at every flush and printed once, at the first scene, in every cell (tables/cellcheck-all.txt; the 0371 reference
  P9-PREV-D has none, as expected).
- **Gate 1, off vs on, R2 at its 0370 default in both arms: frame-EQUAL on all six fixtures** (G 3164, V 3964, GCL
  7004, H 7004, intro 1299, AQ 3558 loop counters; PRESENT_VERIFY stale 0). The lab verify (old vs new GUI texture
  outside the marked rects) reads **0 px in every on cell**; L2 engaged 18 / 19 / 34 / 16 / 10 / 43 times.
- **Cross-checks:**
  - every gate, control and forced cell is frame-EQUAL to LAB-L2G section 8's cell for the same tag (22 cells; the lab
    ran 0369 with DOSAGS_CHAR_REUSE=2 explicit);
  - every off arm is frame-EQUAL to L1LAND's off arm (0371's default) on all six fixtures: the lever is inert when off.
- **Controls:** L2 marking nothing **DIFF 6049/7004**; rects 1 px short **DIFF 2921/7004** (both from lc 5438).
- **Forced checks, each on vs off EQUAL 7004/7004:** a control moved / resized (unsafe 140: those frames take the 0371
  path); GUI visibility / transparency toggled; the label's text grown and shrunk (194 L2 marks, verify 0 out); the slot
  cap forced to 2 (**slots_overflow 4**: GUI 1's 14 controls take the 0371 path). Each forcing but the cap (a lab-side
  limit with no picture of its own) changes the picture vs unforced H.
- **L1 + L2 together** (the 486 round's pair): H with ROUTE_PREWARM=1 + GUI_CTRL_MARK=1 vs ROUTE_PREWARM=1: **EQUAL
  7004/7004**, game lines EQUAL. Both warms serial hits, L2 16 marks, verify 0. ROUTE_PREWARM=1 alone equals L1LAND's
  H-1.
- **Release game lines, on vs off: EQUAL** on 5 Days room 3 (30), Trilby room 35 (1121), AGS Quest (356; parse-results
  PASS both). **P9:** 0372 unset vs 0371's release (a6aaab93c3d2) unset: **EQUAL (78)**.
- **Builds:** both flavours clean (build_dirty=0) and byte-identical across two clean builds; **+8,289 bytes over 0371 in
  both flavours** (section 1 says why the two match).
- **Ratchet:** only exe-bytes (+8,289) and code-lock-bytes (+5,632) fail, as expected. Proposed exact limits 8,706,959 /
  5,228,144 (section 8). Every screen-alias check passes.
- **Line-by-line guard check** (build/l2's guardcheck.py over the vendor commit, tables/guardcheck.txt): every one of the
  243 added lines lies inside a positive `__DJGPP__` branch, file by file (section 2).

## 1. Binaries (worktree ~/git/dosags-l2land, branch l2land off local main 2fd95231 = 0371 landed; patches/ags/0372)

| exe | what | sha256 | binary_sha12 | build_dirty | bytes |
|---|---|---|---|---|---|
| L2INS | 0001-0372, instrumented | 234b56266f83a2ebbb6e76606ab6908e352d6403a21a5e074e014891e28e8d95 | 01658435489c | 0 | 8,706,959 |
| L2REL | 0001-0372, release | 5af21f2ad45877c92efe015f121c3beb3e28ed7389cc55ec34e472c8be335c00 | 8c123c770d0b | 0 | 8,668,817 |
| PREVREL | 0371's release (L1LAND's L1REL-A, = main's), P9 reference | aee2aff6022e1001c8b34b1def86a8ef8ccaf31788f9312c255f14e976b61708 | a6aaab93c3d2 | 0 | 8,660,528 |
| L2GATE | 0001-0372 + gate-overlay.diff, instrumented (lab only) | 26b6d25f8dcc83b097d89360aad819a6237faac33e05489b50a1cd6016c9fdb2 | 6d6993a4cdfe | 1 | 8,738,828 |

- **Vendor tree.** `make patches` from the committed series gave vendor/ags tree b58aa151, the same tree as the
  authoring commit.
- **Build A / build B.** Build A was the first build in the fresh worktree. Build B removed build/ags and
  build/ags-release and rebuilt both flavours. `cmp` L2INS-A L2INS-B and L2REL-A L2REL-B: both 0.
- **Stamps.** From `make build-dirty` / `DOSAGS_RELEASE=1 make build-dirty`, and from every release cell's RUNMANI.LOG
  (binary_sha12=8c123c770d0b build_dirty=0). After the gate build, build/ags/ags.exe was rebuilt from the clean tree
  and `cmp` equal to L2INS-A before the ratchet ran.
- **Against 0371** (6198d2e06b8d / a6aaab93c3d2, 8,698,670 / 8,660,528): **+8,289 bytes in both flavours.** Section
  sizes (objdump -h; DJGPP pads each section to 512 bytes, and the exe carries .bss):

  | flavour | .text | .data | .bss | sections | file | file - sections |
  |---|---|---|---|---|---|---|
  | instrumented 0371 -> 0372 | 5,222,936 -> 5,228,568 (+5,632) | 735,232 -> 735,232 (0) | 570,368 -> 571,904 (+1,536) | +7,168 | +8,289 | +1,121 |
  | release 0371 -> 0372 | 5,191,704 -> 5,196,824 (+5,120) | 732,160 -> 732,672 (+512) | 569,344 -> 570,880 (+1,536) | +7,168 | +8,289 | +1,121 |
  | lab, instrumented 0369 -> lever (LAB-L2G s8) | +5,632 | +512 | +1,536 | +7,680 | +8,801 | +1,121 |
  | lab, release 0369 -> lever | +5,120 | 0 | +1,536 | +6,656 | +7,777 | +1,121 |

  - The release build's code is 512 B smaller than the instrumented one's (one rounding step of .text), and here its
    .data crossed a 512-byte boundary that the instrumented one did not. So both total +7,168 in sections.
  - The +1,121 bytes outside the sections (symbol / string table) are the same in every build.
  - In the lab, on 0369, .data crossed the boundary in the instrumented build and not in the release. Same code,
    different rounding.
  - The release exe contains the lever: its witness and final-line strings are present, and its cells print them
    (P9-REL-1: l2 29).

## 2. The lever (deliverable b)

| file | change |
|---|---|
| Common/gui/guimain.cpp | per-GUI counters (global, under `__DJGPP__`): MarkControlChanged count; unsafe on NotifyControlPosition and on NotifyControlState(mark_changed); the pending control bitmask (16 controls), an overflow flag |
| Engine/gui/gui_engine.cpp | GUIObject::MarkChanged records the control in its GUI's pending bitmask (or the overflow flag past 16) and counts a matched mark |
| Engine/ac/gui.cpp | a font generation, bumped by MarkForFontUpdate (the label-rect cache key) |
| Engine/ac/draw.cpp | mode + witness (read at every flush); dos_gc2_try in dos_port_gui_flush_unmarked (marks the rects); dos_gc2_before_redraw (a flag set between the flush and the redraw drops L2, and R3's late mark of the whole rect follows); dos_gc2_after_redraw (records the rects in a per-GUI block allocated on first use, resets the counters; on only); the draw loop's `_unch` also accepts an L2 GUI; the label-rect cache (8 entries, strcmp, fixed buffers); dos_gc2_report |
| Engine/main/quit.cpp | DOSAGS_GUI_CTRL_MARK joins the RUNMANIFEST env allowlist; guictrlmark_final in the run manifest (both flavours) |

- **Modes.**

  | DOSAGS_GUI_CTRL_MARK | mode | witness |
  |---|---|---|
  | unset | 0, off (the 0371 head) | `DOS-PORT guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=0` |
  | exactly "1" | 1, on | `...=1 mode=1` |
  | anything else | 0, off | `...=<v> mode=0` |

- **RUNMANI line, both flavours:** `DOS-PORT guictrlmark_final mode= l2= ctrls= px= px_gui= no_safe= unsafe= mixed=
  props= norec= slots_overflow= late= mismatch= calc= cache_hits=`.
- **Lab knobs:** none in 0372. DOS_GC2_CAP is a macro equal to the 16 slots. Only the gate overlay redefines it
  (DOSAGS_LAB_GC2_CAP). The verify, NOMARK, SHORT, MOVE, VIS and TEXT knobs live only in the overlay (section 3).
- **docs/dist/README.TXT is unchanged:** L2 is off by default.
- **Constraints.** ASCII only (checked on the patch and every record). One getenv. No file I/O. No SIMD.
- **Result:** 5 files, +243 / -1, against the lab's +235 / -1 (+2 guard lines and +6 comment lines in draw.cpp).
- **Line-by-line guard check** (guardcheck.py; full output in tables/guardcheck.txt). Every added line, mapped to its
  line in the patched file, with the `#if` nesting that encloses it. Each block lies inside the positive `__DJGPP__`
  branch opened at the line shown:

  | file | added lines | blocks (patched-file lines -> enclosing `#ifdef __DJGPP__`) | unguarded |
  |---|---|---|---|
  | Common/gui/guimain.cpp | 17 | 1-8 (its own guard, the counters) / 259-261 (MarkControlChanged) / 267-269 (NotifyControlPosition) / 278-280 (NotifyControlState), each its own `#ifdef __DJGPP__` | 0 |
  | Engine/ac/draw.cpp | 205 | 62-66 (the three #includes, own guard) / 3239-3426, 3429-3430, 3442-3443 (inside the 0191 flush's guard @3223) / 3527-3529, 3542-3544 (own guards: before / after redraw) / 3690, 3695 (inside 0169's guard @3659) | 0 |
  | Engine/ac/gui.cpp | 6 | 1-3 (the font generation, own guard) / 129-131 (MarkForFontUpdate, own guard) | 0 |
  | Engine/gui/gui_engine.cpp | 12 | 1-5 (externs, own guard) / 129-135 (MarkChanged, own guard) | 0 |
  | Engine/main/quit.cpp | 3 | 37 (dos_gc2_report declaration, inside the guard @32) / **420 (the allowlist line)** and 956 (the report call), both inside the existing `#ifdef __DJGPP__` @382, which closes at 970; the report call is outside the DOSAGS_RELEASE / #else block (597-862), so present in both flavours | 0 |

## 3. The overlay (LAB-L2G section 8's, anchors renamed; gate-overlay.diff is the full vendor/ags diff over 0372)

- apply-overlay-l2land.py is LAB-L2G's apply-overlay-l2g-slim.py with three edits, and nothing else changed:
  - its two lever anchors renamed from "lab L2G" to "patch 0372";
  - the DOS_GC2_CAP define's comment, as in the patch;
  - LAB-RB's apply-overlay-rb.py looked up in the same directory.
- apply-overlay-rb.py and apply-overlay-r3land.py are byte-identical to L1LAND's committed copies.
- It is applied, built and reverted (build-gate.sh), never landed.
- Knobs used here:
  - FRAMEHASH; LABCLICKS G / V / GCL / H;
  - DOSAGS_LAB_GC2_VERIFY=1, on arm 1 (reads only);
  - DOSAGS_LAB_GC2_NOMARK=1 (C1) and DOSAGS_LAB_GC2_SHORT=1 (C2);
  - DOSAGS_LAB_GC2_MOVE=50, VIS=60, TEXT=40 (F1-F3, both arms);
  - DOSAGS_LAB_GC2_CAP=2 (F4, both arms).

## 4. Fixtures, arms, witnesses

- **Fixtures** as L1LAND: G (exit 8600; 3164), V (9400; 3964), GCL (12440; 7004), H (12440; 7004), intro (--startr 40,
  no save, 1300; 1299), AQ (AutoPilot; 3558).
- **Gate cells:** no --fixed-timestep, fine timing off, no TICKLOG, FRAMEHASH + PRESENT_VERIFY, RANDSEED=1,
  **DOSAGS_CHAR_REUSE unset** (R2 at its 0370 default, mode 2). DOSAGS_ROUTE_PREWARM unset except HP-0 / HP-1.
- **Arms:** 0 = DOSAGS_GUI_CTRL_MARK unset; 1 = =1 with the lab verify; 1n = =1 without it (C1, C2).
- **Witnesses** (tables/cellcheck-all.txt, all 33 cells): rc 0 and exit_code=0 in each.
  - fixed-timestep: DISABLED in the 24 gate cells, ENABLED in the 9 release cells.
  - guiclip (default) mode=4 and charreuse (default) mode=2 in every cell.
  - guictrlmark (default)/m0 or 1/m1 as set.
  - labclicks n=14 (G, V, H, C1, C2, F*, HP*) / 16 (GCL). RUN.BAT SET totals 119-313 bytes, longest line 38.
  - PRESENT_VERIFY stale frames 0 in every gate cell.
- **Display and stage dirs.** Display 398 only, one DOSBox-X at a time (one serial lane); stage dirs deleted per cell.

Compare, in this directory: `python3 fhcmp.py H-0.FHASH.TXT H-1.FHASH.TXT`; `python3 eqcmp.py P9-PREV-D.GAMELINES.TXT
P9-REL-0.GAMELINES.TXT`. tables/ holds the full compare output (tables.sh regenerates it from build/l2/results).

## 5. Gate 1 -- off vs on, and L2 per fixture (L2GATE)

| fixture | off vs on | = LAB-L2G s8 (off; on) | off = 0371 off (L1LAND) | PV stale (off; on) | guictrlmark_final (on): l2 (ctrls) / px / px_gui | verify px out (in) |
|---|---|---|---|---|---|---|
| G | **EQUAL 3164/3164** | EQUAL; EQUAL | EQUAL | 0; 0 | 18 (18) / 54,400 / 328,320 | **0** (2,619) |
| V | **EQUAL 3964/3964** | EQUAL; EQUAL | EQUAL | 0; 0 | 19 (24) / 48,592 / 346,560 | **0** (4,122) |
| GCL | **EQUAL 7004/7004** | EQUAL; EQUAL | EQUAL | 0; 0 | 34 (34) / 127,616 / 620,160 | **0** (2,843) |
| H | **EQUAL 7004/7004** | EQUAL; EQUAL | EQUAL | 0; 0 | 16 (16) / 48,656 / 291,840 | **0** (1,732) |
| intro | **EQUAL 1299/1299** | EQUAL; EQUAL | EQUAL | 0; 0 | 10 (17) / 67,520 / 96,000 | **0** (7,746) |
| AQ (32-bit) | **EQUAL 3558/3558** | EQUAL; EQUAL | EQUAL | 0; 0 | 43 (43) / 86,698 / 180,440 | **0** (1,365) |

In every on cell no_safe, unsafe, mixed, props, norec, slots_overflow, late and mismatch are 0. Every count equals
LAB-L2G section 8's.

## 6. Gate 2 -- controls, forced checks, L1 + L2 (fixture H; L2GATE)

| control / forcing | pair | result | counters (on) | = LAB-L2G s8 |
|---|---|---|---|---|
| C1 L2 marks nothing | H-0 vs C1-1 | **DIFF 6049/7004**, first lc 5438 | px 0 | EQUAL |
| C2 rects 1 px short on every side | H-0 vs C2-1 | **DIFF 2921/7004**, first lc 5438 | px 40,272 | EQUAL |
| F1 a control moved +1 px / shrunk 1 px every 50 ticks | F1-0 vs F1-1 | **EQUAL 7004/7004** | unsafe 140; l2 16, verify 0 out | EQUAL; EQUAL |
| F2 GUI 0 hidden / transparency 10, every 60 ticks | F2-0 vs F2-1 | **EQUAL 7004/7004** | l2 12, verify 0 out | EQUAL; EQUAL |
| F3 label text +13 characters / restored, every 40 ticks | F3-0 vs F3-1 | **EQUAL 7004/7004** | l2 194, 732,176 px; verify 0 out, 53,164 in | EQUAL; EQUAL |
| F4 slot cap forced to 2 | F4-0 vs F4-1 | **EQUAL 7004/7004** | **slots_overflow 4**; GUI 0 still l2 12, verify 0 out | EQUAL; EQUAL |
| the forcings are real | H-0 vs F1-0 / F2-0 / F3-0 / F4-0 | DIFF 3500 / 3500 / 89 / EQUAL | F4's cap changes nothing with the lever off | -- |
| **L1 + L2: ROUTE_PREWARM=1 + GUI_CTRL_MARK=1 vs ROUTE_PREWARM=1** | HP-0 vs HP-1 | **EQUAL 7004/7004** | both: prewarms 2, built 2, first_serial 2; HP-1: l2 16, verify 0 out | HP-0 = L1LAND H-1: EQUAL |

Game lines EQUAL (48) for every pair above, controls included: they change only the picture.

## 7. Gates 3 and 4 -- release regression and P9 (L2REL / PREVREL; game output lines, eqcmp.py; --fixed-timestep)

| pair | result | guictrlmark_final (on arm) |
|---|---|---|
| P9-REL-0 (0372, unset) vs P9-PREV-D (0371, a6aaab93c3d2, unset) | **EQUAL (78)** | off: mode 0 |
| P9-REL-1 (0372, =1) vs P9-REL-0 (information) | EQUAL (78) | l2 29, 63,840 px of 528,960 |
| P9-PREV-D vs L1LAND's committed P9-REL-0 lines (same 0371 binary, re-run) | EQUAL (78) | -- |
| RG-5D3S-1 vs -0 (5 Days room 3, exit 3000) | exit 0/0, **EQUAL (30)** | mode 1, l2 0 |
| RG-TN35-1 vs -0 (Trilby room 35, MSGSKIP=1) | exit 0/0, **EQUAL (1121)** | mode 1 (witness at the first scene), l2 0 |
| RG-AQ-1 vs -0 (AGS Quest AutoPilot) | exit 0/0, **EQUAL (356)**; parse-results PASS both | l2 41 |

Every release cell shows fixed-timestep ENABLED, guiclip (default) mode=4, charreuse (default) mode=2, and its binary's
stamp with build_dirty=0 (8c123c770d0b for 0372, a6aaab93c3d2 for 0371).

## 8. Gate 5 -- ratchet (instrumented L2INS 01658435489c = build/ags/ags.exe)

`.sdl-dos-ports/shared/tools/ratchet.sh --root <l2land> --no-build --no-host-wait --capture-display 398 --no-record`,
with all nine game packages present (5days, 7days, agsquest, bench16, bench8, bench8old, mmd, shards, trilbysnotes).
build/ags/ags.exe was rebuilt from the clean tree after the gate build and is `cmp` equal to L2INS-A.

| run | result |
|---|---|
| 20261109T114537Z (RATCHET-20261109T114537Z-*) | 39 pass (10 improved), **2 fail, both the expected size checks**, 4 quarantined. exe-bytes 8706959 > 8698670; code-lock-bytes 5228144 > 5222512. Every screen-alias check PASS (bench8 x9, bench16 x2, 5 Days); screen-shards-alias-512x384 FAIL(q) 1 (FRZ00 only, 188,832 px; FRZ01-04 equal), its fixed-40k twin PASS(q) |
| 0372's delta vs 0371 (0001-0371) | exe +8289 (both flavours), code-lock +5632 (= the .text growth of the instrumented flavour) |
| proposed limits (exact, no headroom; tests/ratchet.yaml on l2land, with a LIMIT comment) | **exe-bytes 8706959, code-lock-bytes 5228144** |

- **No second run was needed.** No load-sensitive unit came back VOID or failed. The shards FAIL(q) is the quarantined
  check's known freeze-tick drift at FRZ00 (L1LAND, R2DEF, R2LAND show the same). It never gates.
- **The 10 IMPROVED values are the run's, not this lever's:** AQ journey p95s, sb-live clock and PCM counters, the MIDI
  stall count. The same checks improved in L1LAND's run. Limits are not lowered here.

## 9. Caveats -- what was not exercised, what was not tested

- **Not exercised naturally:**
  - late (a flag set between the flush and the redraw) and mismatch: 0 everywhere;
  - mixed and no_safe (an unmatched MarkControlChanged): 0 everywhere;
  - a 32-bit alpha GUI (props): AQ's GUIs have no alpha channel;
  - a macro label on an L2 GUI.
- **Not tested:**
  - GUIs drawn as textures (draw_controls_as_textures, a hardware renderer): the DOS software renderer never takes that
    path;
  - a translation or font change while L2 is on (the cache key covers both; no fixture changes them);
  - the slim build's verify at more than 16 controls (overflow is forced, F4, not natural).
- **No timing here.** The speed claim is LAB-L2G sections 5 and 8's: MMD's action-label flip ticks -5.2 ms at 40k,
  about -3 skips per MMD run on the 486 (band 2-5). The 486 round is still to come.
