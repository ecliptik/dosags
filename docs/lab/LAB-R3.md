# LAB-R3 -- MMD in play, room 2 late stretch: what the verb bar costs, and lever R3 (lab worktree ~/git/dosags-lab-r3)

Copied into the main repo 2026-11-06 from the lab worktree (base 579c0b5c) as the lab record and the source of the R3
pre-registration; the diffs are in docs/lab/r3-lab-patches/. Exes are lab-only (build_dirty=1) and are not committed.

Lab only. Nothing committed anywhere; ~/git/dosags, ~/git/dosags-lab-play, ~/git/dosags-r1land and ~/git/dosags-nightly
untouched; no rig binary built or staged. All times are DOSBox-X fixed-40000 emulated time unless a row says 486.

## 0. Answer first

- **The late stretch costs the R1 bbox clip, not a GUI redraw.** With the pointer still on the verb bar no GUI is
  re-rendered and no UI entry loses its skip flag. Both 320x57 bottom GUIs (gMaingui idx 1 @y143: verbs + portraits;
  gAction idx 0 @y144: the sentence line) are composited every frame, clipped to the dirty BBOX. That bbox runs
  x = -640..318, the whole screen width, because it unions three things: the pointer's 16x16 box, Dave's box at the
  right fence (292..318), and three invisible room-object entries that are invalidated every frame at off-camera screen
  x -640..-216. So R1's clip is "every row from y=143 down to the bottom of the pointer, full width": 20,100-32,200 px
  of masked composite per frame.
- Cost (R1 on, pointer still, fine timing, rb_sprite_time per pass): pointer in the room 0.69 ms; on a verb 2.74;
  between the verbs and the portraits 3.02; on the lower portrait 4.20; moving over the verbs 2.84. On the 486 the same
  step is 2.30 -> 6.75 ms render per drawn tick (GCMP).
- Trigger: the cursor's dirty box (this frame's plus its carry from last frame), widened to full width by the bbox.
  Hover highlighting and the sentence line re-render only when they CHANGE (a pointer move or a click): gMaingui marks
  all 14 controls changed and re-renders in 2.4-7.5 ms, gAction in 2.8-10.8 ms, once per event. That is not the
  steady cost.
- **R3 (DOSAGS_GUI_CLIP=4):** composite a flagged UI entry once per dirty BOX that reaches it (box set U carry boxes,
  each intersected with the entry; a box inside one already listed is dropped) instead of once to their bbox. It uses
  R1's exactness argument with the union of the boxes in place of their bbox. It falls back to R1's bbox clip if AGS's
  own span set coarsened, and to a full composite if AGS's restore went whole-surface without telling the dirty set.
- Prototype built and gated. Digest gates: R3 vs off EQUAL on every fixture (section 6). Timing: rb_sprite_time on the
  verb bar drops from 2.74-4.20 to 0.87-1.05 ms per pass, a saving of 1.8-3.3 ms (section 5).
- 486, per the review addendum (section 7): render per drawn tick in the late stretch (instrumented) 6.75 -> central
  2.7 ms (band 2.4-3.6). Displayed (release, R1 on, R3 off -> on): late stretch 78-82% -> central 97% (band 93-100%);
  whole fixture 88.7/89.3% -> central 96.5% (band 94-98.5%). 99% is not claimed.

## 1. Setup

- Worktree `git -C ~/git/dosags worktree add --detach ~/git/dosags-lab-r3 579c0b5c`. vendor/ags and vendor/SDL were
  cloned from ~/git/dosags/vendor at the manifest pins, then `make patches` (series fingerprint 3ecc4317438f, same as
  LAB-PLAY), then `git apply ~/git/dosags-lab-play/lab-play.diff`. Copied in, untracked: tools/ symlinks
  (setup-symlinks.sh), vendor/cwsdpmi, tests/harness/games/{mmd,agsquest}.
- Check: `make all` with lab-play.diff alone gives an exe byte-identical to LAB-PLAY's R1INS.EXE (sha256 f5089493...),
  kept as build/lab3/exe/R1INS.EXE.
- LAB-R3 changes (lab-r3.diff = over lab-play.diff; lab-r3-full.diff = the whole vendor/ags working-tree diff over the
  0365 head; ASCII, all behind env or counters):
  - DOSAGS_GUI_CLIP=4 = R3 (section 4); DOSAGS_GUI_CLIP=4 + DOSAGS_LAB_GUISKIP_BREAK=2 = mode 5, the R3 control (per-box
    clip WITHOUT the carry boxes).
  - draw_software.cpp: invalidate_rect_on_surf flags a coarsened restore (bit 1: a row past MAX_SPANS_PER_ROW=4 had its
    nearest span stretched across a gap; bit 2: the 26th rect of an interval turned the surface WHOLESCREENDIRTY). The
    flag is latched per restore interval at update_room_invreg_and_reset.
  - DOSAGS_LAB_R3LOG=lo:hi: per render pass in the window, one line per UI-batch dirty set (bbox, boxes, carry, coarse,
    latch); one per composited sprite (mode n/F/C/S/M, clip rects, px, us); which GUI/controls say they changed before
    the update loop clears the flags; every GUI re-render with its us; the skip decision per GUI.
  - Counters: GUI re-renders (n, us), UI entries not skip-flagged (n, px), per-mode composite px, R3 rects, fallbacks,
    span/overflow events. These go to RUNMANI.LOG (`DOS-PORT r3_final ...`) and to every DOSAGS_LAB_CKPT checkpoint
    (`labck c=r3 ...`).
- Fixture V (build/lab3/fixv.sh; fixture G's route; save 007 sha256 f486d0e9... = build/ws/roundGC/AGSSAVE.007; seeded;
  exit 9400). Room 1 walk clicks 6000/6400/6800 -> room 2 at lc ~6882 (Dave idle at the right fence, as in the GCB1
  camera frames 13-21). Then pointer moves only (DOSAGS_LABCLICKS ...:0) except one click:
  E 7100-7400 pointer in the room (160,80) | H1 7500-7800 still on "Look at" (65,166) | H2 7900-8200 the same point
  after clicking it (sentence "Look at") | H3 8300-8600 still between the verbs and the portraits (200,170) |
  H4 8700-9000 still on the lower portrait (300,185) | H5 9000-9300 moving between three verbs every 50 ticks.
- Conf tests/harness/confs/dosbox-x-fixed40k-opl3.conf (fixed 40000), sound-ON 512x384 round cfg, as LAB-PLAY.
- **Trap hit and fixed:** the first timing pair (TV*, kept in build/lab3/results-envlost/) passed a 339-char
  DOSAGS_LABCLICKS. The DOS environment overflowed and silently dropped every later SET, including
  DOSAGS_FIXED_TIMESTEP and DOSAGS_TICKSTATS_FINE (STDOUT said "fixed-timestep: DISABLED"). I shortened H5 to 6 moves
  and dropped DOSAGS_TICKLOG for the timing cells (NOTL=1), which keeps RUN.BAT's SETs under ~520 bytes, and re-ran as
  TF*. Every scored cell was checked for "fixed-timestep: ENABLED". The env-lost pair agrees in direction (render per
  pass on the bar 3.16-4.66 R1 -> 1.29-1.33 R3, all ticks rendered).

## 2. Where the late-stretch frame goes (log runs VLOG = R1, VLOG4 = R3; NOFT, every tick rendered; us per frame)

| window | UI batch (3 GUIs), R1 | UI px, R1 | R1 modes 0x16@0 / 57@143 / 57@144 | UI batch, R3 | UI px, R3 | room batch | cursor |
|---|---|---|---|---|---|---|---|
| E pointer in room | 0 | 0 | S / S / S | 0 | 0 | 459 | 71 |
| H1 still on a verb | 2,103 | 20,097 | S / C / C | 379 (pre-dedupe) | 1,024 | 459 | 71 |
| H3 still, bar middle | 2,566 | 22,649 | S / C / C | 326 | 1,024 | 459 | 71 |
| H4 still, lower portrait | 3,557 | 32,219 | S / C / C | 394 | 1,024 | 459 | 71 |
| H5 moving over verbs | 2,307 | 21,972 | S / C(285) n(15) / C | 770 | 4,752 | 459 | 71 |
(S skipped, C bbox-clipped, M per-box, n not skip-flagged. VLOG4 ran AGSR3A, before the duplicate-box drop: the still
pointer's box and its carry are the same rect, so each GUI was drawn twice; AGSR3B draws it once. Raw:
build/lab3/results/VLOG{,4}/STDOUT.TXT, VLOG-win.txt, VLOG4-win.txt via tools/r3win.py.)

- A typical frame on a verb (lc 7600, R1): `labdirty ... bbox=-640,57-318,174 boxes=-304,97--216,103;292,57-318,132;
  -640,93--600,112;58,159-73,174; carry=<the same four>` and `labspr ... y=143 ... px=10208 us=1360 mode=C
  rects=0,57-318,174;`. The four boxes are three off-camera room objects (0 px drawn, invalidated every frame), Dave,
  and the pointer.
- GUI re-renders in the whole V run (R1): gMaingui 17 times (2.37-7.54 ms, mean 3.18), each with ctrls=0..13 (every
  control flagged) on a hover change; gAction 3 times (2.75-10.82 ms, mean 7.83) on a sentence change. None happened in
  a still window. In H5 they average 0.10 ms per pass (fine timing).
- Answer to "what triggers the full composite": none of the four candidates sets off a full composite in the steady
  state. The CURSOR BOX sets off the clipped composite, and the BBOX makes it full width. Hover and the sentence label
  trigger only per-event re-renders. The 0x16 top GUI is skipped throughout.

## 3. Why R1 could not skip it

R1 skips an entry only when (entry rect) n (bbox of box set U carry boxes) is empty. A pointer anywhere on rows 143-199
makes that intersection non-empty, and with Dave and the off-camera objects in the set, it is every column. R1 then
clips to it. On the 486 that is the whole step from 3.54 (early room 2) to 6.75 ms render. It also explains most of
why GCMP's rb_sprite_time per drawn frame came out at 4.12 against the predicted 1.5-3.7: that prediction assumed the
pointer in the room, but GCMP's pointer sat on GUI 1 (the verb bar) from the click at tick ~8519 to the end.

## 4. R3 design (ali3dsw.cpp RenderSpriteBatch, inside 0170/0236's flagged-entry block)

For an entry flagged by 0169/0191/0234 (unchanged since its last composite, same geometry, idempotent), in mode 4, with
no latch, the same space, and a valid, non-full dirty set without a full carry:
1. If this frame's restore went WHOLESCREENDIRTY behind the dirty set's back (coarse bit 2): composite in full
   (fb_whole).
2. Else if a row's spans were stretched (coarse bit 1): take R1's bbox path (fb_bbox). A stretched span stays inside
   the x-range of that row's marks, so it stays inside the bbox, but not necessarily inside any one box.
3. Else build the list {entry n clip n b : b in box[0..nbox) U carry_box[0..carry_nbox)}, dropping empty rects and any
   rect contained in one already listed. Empty list: skip (R1's case). Otherwise draw the entry once per rect with the
   surface clip set to it (the unchanged draw dispatch, called through a lambda), then restore the clip.

Why it is exact: everything written to the back buffer before this entry in this frame lies inside box[] U carry_box[].
That covers the restore (pre-restore marks plus last interval's post-restore marks = carry, both added through
dos_port_dirty_add_screen), the room sprites (always invalidated), and lower UI entries (invalidated, or flagged and
themselves drawn only inside the boxes). Boxes only grow when the box set merges. Outside the union the pixels are last
frame's, and they already hold this same composite (by induction from its last full draw, as in R1). Inside each rect
the entry is drawn completely. Overlapping rects draw some pixels twice. An idempotent entry over its own pixels is a
no-op, and in any case all of this entry's rects are drawn before the next entry starts. Over-coverage is always
safe; only under-coverage could break the image. The one case where the restore writes outside the marks is AGS's
span coarsening, and it is guarded by (1)/(2).

Hazard found on the way (R1 too): AGS's invalidate_rect_on_surf turns the whole camera surface dirty at the 26th rect
of an interval and tells no one, so dos_port_dirty can stay narrow while the restore repaints everything. R1 has no
guard for it. Observed: overflow events 3 (V), 6 (intro), 18 (AQ) per run, in 1, 1 and 12 restore intervals. In every
one of them the frame's dirty set was already full (R3's fb_whole stayed 0 in all runs), so it did not bite. If R1
lands, it should take the same latch: a coarse bit 2 frame composites in full.

Cost: the box loop is ~8 intersections per flagged entry. In the pointer-in-room window that is +0.04 ms per pass over
R1 (0.726 vs 0.685 rb_sprite_time). A bbox pre-test (R1's empty test first, then the box loop) would remove it. Not
built.

Not exercised: the span-coarsening fallback (span_ext 0 in every run: MMD, the intro and AGS Quest never put 5 spans on
a row) and the whole-surface fallback (0 with a narrow dirty set). Both are guarded and counted, not proven.

## 5. Timing (fixed 40000, fixed timestep, fine timing ON; same exe AGSR3B; fixture V + checkpoints; build/lab3/timing3.sh)

ms per render pass (window = difference of two checkpoints). TF2 = R1 (DOSAGS_GUI_CLIP=2), TF4 = R3 (=4).
| window | rb_sprite R1 | rb_sprite R3 | render_to_screen R1 | R3 | pass (scene+render) R1 | R3 | masked px R1 | R3 |
|---|---|---|---|---|---|---|---|---|
| E pointer in room 7100-7400 | 0.685 | 0.726 | 1.213 | 1.254 | 3.141 | 3.182 | 2,175 | 2,175 |
| H1 still on a verb 7500-7800 | 2.743 | **0.871** | 3.271 | 1.400 | 5.194 | 3.322 | 22,272 | 2,687 |
| H3 still, bar middle 8300-8600 | 3.023 | **1.024** | 3.569 | 1.387 | 5.501 | 3.320 | 24,824 | 2,687 |
| H4 still, lower portrait 8700-9000 | 4.198 | **0.875** | 4.767 | 1.443 | 6.698 | 3.373 | 34,394 | 2,687 |
| H5 moving over verbs 9000-9300 | 2.843 | **1.045** | 3.387 | 1.589 | 5.578 | 3.775 | 23,196 | 5,154 |
Logic, scene_construct and present_update_window are equal between arms to <= 0.013 ms in every window; renders/ticks
99.7-100% in both. Saving per pass on the bar: 1.87 (H1), 2.18 (H3), 3.32 (H4), 1.80 (H5) ms. The R3 bar state sits
0.15-0.32 ms above the pointer-in-room state (two 16x16 clipped composites plus re-renders while moving). Raw:
build/lab3/results/TF{2,4}/, TF2-win.txt, TF4-win.txt (tools/ckwin.py, extended with the r3 counters).
Off arm (TF0, GUI_CLIP unset, same exe), for scale: rb_sprite_time 5.53-5.72 ms per pass and pass 7.98-8.45 in every
window (all three GUIs composited in full regardless of the pointer). R1 removed 4.85 ms of it with the pointer in the
room but only 1.5-2.8 ms with it on the bar. R3 removes 4.6-4.8 ms in both states.

## 6. Digest gates (NOFT: every tick rendered; DOSAGS_LAB_FRAMEHASH=1 + DOSAGS_PRESENT_VERIFY=1; same exe AGSR3B)

Compared by loop counter on FHASH.TXT (tools/fhcmp.py; last record of a loop counter). Arms: 0 = unset, 4 = R3,
5 = R3 control (per-box clip without the carry boxes: the old pointer/sprite position is restored but not recomposited).
| fixture | R3 (4) vs off (0) | control (5) vs off | R3 guiclip_final / r3_final | stale px (PRESENT_VERIFY) |
|---|---|---|---|---|
| G (LAB-PLAY's: save 007, room 1 -> 2, clicks + hovers, exit 8600) G0/G4/G5 | **EQUAL 3164 of 3164** | **DIFF 2329 of 3164** (first lc 5439) | flagged 9558: skipped 6742, per-box 2475 (2510 rects), full 341 | 0 all arms |
| V (this lab's: room 2, pointer still/moving on the verb bar, exit 9400) W0/W4/W5 | **EQUAL 3964 of 3964** | **DIFF 3426 of 3964** (first lc 5439) | flagged 11957: skipped 6305, per-box 5556 (5605 rects), full 96 | 0 all arms |
| intro, rooms 40 -> 49, --startr 40, exit 1300 (I0/I4/I5) | **EQUAL 1299 of 1299** | **DIFF 771 of 1299** (first lc 62) | flagged 7874: skipped 6441 (R1: 5453), per-box 47, full 1386 | 0 all arms |
| AGS Quest AutoPilot (AQ0/AQ4/AQ5) | **EQUAL 3558 of 3558** | **DIFF 2078 of 3558** (first lc 261) | flagged 8637: skipped 7343 (R1 on the rig: 6144), per-box 1281 (2774 rects: several boxes per entry), full 13 | 0 all arms; PH01-03 BMP byte-equal 0 vs 4; AutoPilot ok |
- Repeatability: V0 (a second off arm, run separately) vs W0: EQUAL 3964 of 3964.
- R3 skips MORE entries than R1 where the bbox reached an entry but no box did (intro +988, AQ), and every such frame is
  in the EQUAL count.
- Release flavour (R3REL.EXE, P9-shape fixture: save 007, 0247 TICKCLICKS 5500,60,30, seeded, exit 7436, fixed 40k;
  tools/eqcmp.py on game output): GUI_CLIP unset vs BASEREL (the shipped release, c754df64babd) **EQUAL 78/78**, exit
  0/0, guiclip mode=0 flagged=0; GUI_CLIP=4 vs BASEREL **EQUAL 78/78**, exit 0, R3 engaged (skipped 2047, per-box 3905,
  full 46, latched 6).
- R1 (=2) on fixture V (W2): EQUAL 3964 of 3964, the same flagged/skipped counts as R3, all non-skipped entries
  bbox-clipped (5556). Repeats V4/V5 of the V gate were still running on display 384 when this was written (same
  fixture as W4/W5, TICKLOG on). V4 (R3) finished: EQUAL 3964 of 3964 vs W0. V5 was terminated mid-run (exit 144,
  'Terminated', no output); it is not needed for the rows above.

## 7. 486 prediction (review addendum: twice in displayed %, plus render ms on the instrumented exe)

Basis on the 486 (GCMP, instrumented, R1 on, TICKS.BIN, render per DRAWN tick; tools/tickwin.py): pointer in room 2
(8190-8440) 2.30 ms; 8440-8690 3.54; the bar from ~8690 on: 5.5-7.2, steady 6.75 (10940-12439). Scene 3.9-4.3 and logic
~17.3 are flat across the step, so the step is render only. The same run's render-only cost of the bar state over the
in-room state is 4.45 ms. DOSBox-X puts it at 2.06-3.51 ms per pass (H windows, rb_sprite R1 minus E), so the bar
composite runs 1.27-2.16x slower on the 486 than here, above LAB-PLAY's rb_sprite range (1.00-1.31x). I use 1.0-2.0x
for the residual below.

(c) **Render per drawn tick, late stretch (9500-end), instrumented exe, R1 on -> R1 + R3: 6.75 -> central 2.7 ms, band
2.4-3.6.** Construction: in-room 486 level 2.30, plus R3's bar residual 0.15-0.32 ms and its +0.04 box-loop cost, times
1.0-2.0 -> 2.5-3.0. Widened up to 3.6 for the R1 shortfall lesson (an unmodelled per-call cost of a clipped masked blit
on the 486: two per frame here). Falsifier: median render per drawn tick in 9500-end > 3.6 ms, or less than 2.5 ms below
the same-binary R1-only arm.

(a) **Displayed, late stretch (loop ticks 9500 to the end), release exe, R1 on, R3 off -> on: GCB1/GCB2 78-82% -> central
97%, band 93-100%.** Basis: in GCMP (instrumented, MORE logic than release) the windows with render 2.30-3.54 ms per
drawn tick drew 100% of their ticks (8190-8690). R3 puts the bar state at ~2.7 ms, inside that range. What stays: each
verb click is a logic spike plus a gAction re-render (2.8-10.8 ms here, x1.3-2 on the 486) and a gMaingui re-render per
hover change. At ~10 clicks in 2,940 ticks that costs ~10-30 ticks (0.3-1%). Logic spikes in general account for the
rest of the band. Falsifier: either R3-on release cell < 92% renders/ticks over 9500-end, or less than +10 points over
its same-binary R1-only arm in that stretch.

(b) **Displayed, whole fixture, release exe, R1 on, R3 off -> on: 88.72% / 89.30% -> central 96.5%, band 94.0-98.5%.**
Arithmetic on the skip counts: GCB1 skipped 790 and GCB2 749 of 7,003. The late stretch at 78-82% accounts for 529-647
of them (central ~588), which leaves ~160-200 outside it (room 1, the room-2 entry and first-route hitch, the earlier
hover). With R3 the late stretch skips 0-206 (central ~88), and the earlier hover windows recover 0-60. Total skips:
central ~240 (96.6%), best ~100 (98.6%), worst ~410 (94.2%). Falsifier: either R3-on cell < 93%, or mean(R3 on) -
mean(R1 only) < +4 points. The campaign line (>= 99% x2) is NOT predicted. The remainder is room 1 (three kids
recomposited and prep_chars every frame: R2), the room-2 entry and first-route hitch, and scroll frames.

Instrumented exe on the same fixture (GCMP shape), for the record: late stretch 65% -> 88-100% (central ~95%).

## 8. Caveats and next

- DOSBox-X numbers are not 486 numbers; the 486 rows are predictions until a rig round measures them.
- The R3 prototype carries the lab instrumentation (R3LOG checks, counters, two uclock reads around each GUI re-render
  in both flavours). A landing patch would be the box loop + the containment drop + the coarse latch (~50 lines in
  ali3dsw.cpp + ~10 in draw_software.cpp) and could take the bbox pre-test.
- Both the off-camera objects (3 entries at x < 0) and the per-hover full re-render of gMaingui (all 14 controls flagged)
  are smaller next levers: the first costs nothing under R3; the second is ~3 ms per hover change, per event.
- Exes: build/lab3/exe/ (section 9). R3REL.EXE (release flavour of the same tree) was built but not run. It is a lab
  build (build_dirty=1), not staged for the rig.

## 9. Files
| file (build/lab3/exe/) | flavour | sha256 | binary_sha12 | bytes | used for |
|---|---|---|---|---|---|
| AGSR3B.EXE | instrumented | de5517feec25df9bf1fd23e43516062ae876b302886e2d18ee6843fe8d9a6d1a | 0ca26019bb5c | 8,703,734 | every scored timing and gate row |
| R3REL.EXE | release | c948b508307ae5de9ee4e4734dafe6d9dcf54aa72aaf15ab45aaed6158b75c0a | ff0d752744b1 | 8,660,461 | release equivalence rows only |
| AGSR3A.EXE | instrumented, before the duplicate-box drop | f58d88cc410529683af526a51246349d50fabcb45b7ac199e8ccfa2b130cdaa6 | 8faf847c50e8 | 8,703,734 | log runs VLOG / VLOG4 |
| R1INS.EXE | = LAB-PLAY R1INS (rebuilt here byte-identical) | f5089493b1a828198cb0ebfaa3b7f8b9d944b203a55507b67884762483cea044 | 5dc54892ad56 | 8,696,018 | build check |
| BASEREL.EXE | copy of LAB-PLAY's (shipped release) | d680e3b6fcfc49b0ca8e1f84aa6bc147f7658b946f2a7539a47a95bae4b542c4 | c754df64babd | 8,646,251 | equivalence reference |
All lab exes carry build_dirty=1 (uncommitted lab edits in vendor/ags). Not for the rig.
- Diffs: ~/git/dosags-lab-r3/lab-r3.diff (R3 + LAB-R3 instrumentation over lab-play.diff; ASCII),
  ~/git/dosags-lab-r3/lab-r3-full.diff (the whole vendor/ags working tree over the 0365 head = lab-play.diff + lab-r3.diff).
- Scripts: build/lab3/{cell.sh, pcell.sh, fixv.sh, timing3.sh, gate3.sh}; tools: build/lab3/tools/{r3win.py,
  tickwin.py, ckwin.py (LAB-PLAY's + r3 counters), fhcmp.py, eqcmp.py}.
- Results: build/lab3/results/{VLOG,VLOG4,TF0,TF2,TF4,G0,G4,G5,W0,W4,W5,W2,V0,I0,I4,I5,AQ0,AQ4,AQ5,EQ-*}/ plus the
  *-win.txt tables; build/lab3/results-envlost/ (the env-overflow pair, not scored). AQ *.BMP shots stay local and
  untracked, like everything under build/.
