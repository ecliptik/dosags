# LAB-RB -- what MMD's remaining skips are (lab worktree ~/git/dosags-lab-rb, base main 478b8f21; lab only)

Lab only: no landing patch, no rig or vcctrl, nothing pushed. ~/git/dosags (main) and the RD/RC round files were only read.
All lab times are DOSBox-X fixed-40000 emulated time: read ratios and counts, not absolute ms. 486 figures are quoted from
round RD (tests/harness/results/RDMP-2026-11-08, TICKS.BIN, RUNMANI.LOG, STDOUT.TXT) and are labelled "486".

## 0. Answer first

- **Q1 (whole-scene ticks): in room 1 there are none outside the room transitions. The 486's post-click "whole-scene"
  ticks are GUI 0 redraws, not full latches.** In both lab fixtures every latch of dos_port_dirty_set_full() comes from:
  - a room transition: ScreenTransition crossfade, screen.cpp:873 construct_game_scene(true), 15 scenes per transition;
  - the first drawn tick after a transition: crossfade End(), screen.cpp:864 invalidate_screen();
  - the room-2 camera pan (GCL only): on_roomcamera_changed, draw.cpp:1360, reached from construct_game_scene ->
    UpdateViewports. That gives 41 ticks per pan; the camera does move, so these redraws are needed.
  Each click is followed by two genuine GUI 0 changes. on_mouse_click (script line 1498/1526) changes a property of
  GUI 0's only control, a 320x10 label (the action line), and repeatedly_execute (line 737) changes it back on the next
  tick. The text is unchanged (the text setter logged no new text); every label setter compares before it marks.
  R3 then re-marks the whole 320x56 GUI. The room is restored under it and GUI 0 + GUI 1 (overlapping) are re-composited.
  The present pushes 44,800 px instead of about 2,000. Lab: scene 1.0 -> 9.5 ms, render 0.6 -> 5.3 ms. 486: about 50 ms
  ugo vs 25. Of the excess, about 2.8 ms (lab) is the GUI texture redraw, which is needed; the rest scales with the
  marked area. Only 18% of that area changed (the label rect): this part is avoidable.
- **Q2 (click logic spikes): route finding, and mostly the cold cache.** The breakdown is on_mouse_click ->
  RoomProcessClick -> Pathfinding::FindRoute. The legacy finder always returned a 2-node (straight) path here. On the two
  biggest spikes, 90-95% of the tick is is_route_possible's mask analysis (0211's cache plus 0319's labels), rebuilt by
  the first request after a room load or restore:
  - 6154 (first click after the restore): FindRoute 62.3 of 101 ms, is_route_possible 57.4. 486: 237 ms, 5 skips.
  - 7895 (first click in room 2): FindRoute 182.2 of 200 ms, is_route_possible 172.8. 486: 374 ms, 5 skips.
  Warm-cache clicks are find_route_dijkstra plus the can_see_from path simplification:
  - 7315: dijkstra 52.1 ms over 91 passes (106,608 cell scans) + can_see_from 21.2 ms (96 calls), of 94 ms. 486: 131 ms,
    4 skips.
  The GUI redraw is not on the click tick: it is the next 1-2 ticks (Q1).
- **Q3 (no-event spikes 8533 / 9445 / 11775): not reproduced in the lab, and not work.** Each 486 value equals an
  ordinary busy tick (~21.4 ms) plus an over-long wait of 77 / 94 / 59 ms. RDMP's run maximum for wait_next_frame is
  94 ms, against 22 ms in the lab. Over the run the measured waits total 28.1 s against 17.4 s requested, so waits do
  overshoot. The 2 skips after each spike are the fixed-step loop repaying the wait. Scene and render are ordinary, and no click, route, GUI, sound load or asset open
  happens near them in the lab replica (fixture H matches RDMP's game actions to lc 8231).
  - 11775's excess is 55.5 ms, one BIOS tick (54.9).
  - RDMP's persistent_anims also shows max_ms=55 with clamped_neg=1, a uclock step; audio_sync has clamped_neg=1 too.
  - Cause of the long wait: undetermined. See 3.3 for the instrument that would settle it.
- **Q4 (catch-up after an excluded stall): the variant already exists and is default off.** It is DOSAGS_STALL_RESYNC=1
  (patch 0163), and its stall flag is compiled into the release flavour too. It changes no game logic: the game lines
  are EQUAL in both fixtures. It removes the 5-tick burst after every tick whose self time is > 250 ms. Lab: GCL 15 -> 2
  skips, H 20 -> 13. In wall-clock terms, every later tick runs 125 ms later per such stall (details in 4).
- **Q5 / most promising exact lever: pre-warm the route-possible cache in the room-load stall** (draft in 7). It is exact
  by construction, because the cache is validated against the request's mask on every request. 486 estimate: -4 to -8
  skips per run (central -6), on the first click after the restore and the first click in room 2.
  - Next, at medium risk: GUI marks limited to the changed control's rect (-5 to -9).
  - Then the dijkstra bucket queue LAB-R2 named (-2 to -4).
  - 0163 (-10 to -20) is a pacing decision for the operator, not a lever.

## 1. Setup

- `git -C ~/git/dosags worktree add --detach ~/git/dosags-lab-rb main` (478b8f21). vendor/ags and vendor/SDL were cloned
  from ~/git/dosags/vendor, cwsdpmi and the mmd/5days/agsquest/trilbysnotes packages copied from main, and
  `.sdl-dos-ports/shared/scripts/setup-symlinks.sh` run (tools/djgpp). Then `make patches` (ags 0001-0369, series
  060a7888eb99), `make sdl3`, `make game`, `DOSAGS_RELEASE=1 make game` (rb-lab/build-main.sh).
- **Check: main's two flavours rebuilt here are byte-identical to RDINS / RDREL.**
  - MAININS: sha256 0e59c82b877719726cff6a5b45ee0495a498993756fd05e829a6c69e76ba5a88, PORT_BUILD_SHA12 f9f8dd6614c8,
    PORT_BUILD_DIRTY=0.
  - MAINREL: ffe49dab2c137748d91bbbace337590556cc1086b0420f6183e342deaee0282a, 84c1a74fdcf6, PORT_BUILD_DIRTY=0.
- Lab exe RBGATE*.EXE = main + the overlay (instrumented flavour, build_dirty=1, never for the rig). The overlay grew by
  additions only, v1 -> v7. Each cell's CELL.txt records its exe sha256:
  - v1: A1;
  - v2: A2;
  - v3: H1;
  - v4: H2;
  - v5: H3;
  - v6 (dc62c384...): A3, H4, HSR, GSR;
  - v7 (51845f3d...): H7, HS2, HS3.
- Conf tests/harness/confs/dosbox-x-fixed40k-opl3.conf, ACSETUP-ON-512X384-ROUND.CFG, save 007
  (~/git/dosags/build/ws/roundQ/AGSSAVE.007, `--loadsavedgame 7`). --fixed-timestep with fine timing on,
  DOSAGS_TICKLOG=30000, exit tick 12440. Env: DOSAGS_RANDSEED=1, DOSAGS_CHAR_REUSE=2, DOSAGS_LAB_SLOWMS=30.
- DOSBox-X display 398 only (399 unused), one DOSBox-X at a time in serial chains. Every wait used tools/waitfor.sh with
  a pid file and a timeout. cell.sh deletes its stage dir; none is left. Nothing is left running.
- Overlay neutrality: A1 (GCL, v1) reproduces LAB-R2B's T-2 exactly: charreuse_final hits 11241, skips 11177, ff_full 64,
  15 skips (5 restore + 10 entry). The game lines are EQUAL across every overlay version and seed (tables/eqcmp.txt).

## 2. Method

- **Overlay** (rb-lab/apply-overlay-rb.py; diff rb-lab/lab-rb-overlay.diff, v7). It first runs R3LAND's overlay unchanged
  (DOSAGS_LABCLICKS etc.), then adds:
  - GCL and H click presets.
  - `rbfull`: every dos_port_dirty_set_full() call with its reason, a caller-tag stack and the running script function
    and position. The tags are file:line of every invalidate_screen / invalidate_all_rects /
    invalidate_all_camera_rects / construct_game_scene / invalidate_rect call, via macros in draw.h and draw_software.h;
    the definitions are parenthesized.
  - `rbpfull`: a present pushed with the latch set. `rbff`: once per scene in which R2b's mark fell back on ff_full.
  - `rbslow`: every UpdateGameOnce that is >= 30 ms inclusive, has a GUI redraw, a latch or a FindRoute. It carries
    per-phase deltas (tick-timing scopes, sc_*, bg_restore, rb_sprite_time, present), lab brackets (FindRoute, GUI
    redraw, sprite/sound load, asset open, RoomProcessClick), the GUIs redrawn (bit mask), present px and the script
    functions run (name:us).
  - `rbroute`: each FindRoute >= 5 ms, split into is_route_possible / find_route_dijkstra (passes, cell scans, cells) /
    try_this_square / can_see_from.
  - `rbguimark`: every GUI change-mark, with GUI, control and script position. `rblabel`: label text changes, lengths
    only.
  - `rbgui` / `rbctl` / `rbclip`: GUI and control geometry and OPT_CLIPGUICONTROLS.
  - `rbbig` / `rbmark`: sprite entries and marks >= 20,000 px.
- **Fixtures.**
  - GCL: LAB-R2's 16 clicks; room-1 floor walks, then room-2 walks that pan the camera.
  - H (new): RDMP's 14 post-restore click ticks, with positions chosen so that the game log repeats RDMP's actions. The
    room-1 sequence is identical to RDMP line for line: walks to 204,98 / 319,98, GUI 10 twice, 34,128, exit at 0,128,
    room change at 7711. Room 2 matches through its first walk (945,132 -> 925,69 at 7895) and the GUI 10 click. After
    that H's GUI 1 clicks (30,165) choose verb mode 2 where RDMP chose mode 1, so H never returns to room 1 (RDMP does at
    10017).
- **Cells:** A1-A3 GCL; H1-H4, H7 H; HS2 / HS3 H with seeds 2 / 3; HSR / GSR H / GCL with DOSAGS_STALL_RESYNC=1.
- **486 attribution:** rb-lab/rdmp-attrib.py over RDMP's TICKS.BIN. It finds each run of skipped ticks and takes the
  costlier of the two ticks before it as the cause.

## 3. Results

### 3.0 RDMP's 93 skipped ticks from the restore (486; tables/rdmp-attrib.txt)

| cause of the run (tick before it) | skips | ticks |
|---|---|---|
| a tick > 250 ms (stall detector), then MAX_CATCHUP | 20 | 5436 restore, 7711 room 1->2 (burst after 7712), 7895 click 374 ms, 10017 room 2->1 |
| click tick < 250 ms | 10 | 6154 (237 ms, 5), 7315 (131, 4), 6409 (58, 1) |
| GUI 0 redraw tick after a click (Q1) | 11 | 6160, 6412, 7320, 7702, 7704, 7901, 10004 |
| no-event spike (Q3) | 7 | 8533 (2), 9445 (2), 11775 (2), 5442 post-transition full redraw (1) |
| ordinary tick (ugo <= 60 ms) | 45 | mostly 1-2 skips while a character walks after a click (scene 4.5-10 ms vs 2.8 idle; idle ticks have ~0.3 ms slack) |

### 3.1 Q1 -- every full latch, by caller (tables/rbtab-A3.txt, rbtab-H4.txt; main's line numbers)

| caller (outermost > innermost) | reason | ticks (GCL A3) | ticks (H4) | avoidable? |
|---|---|---|---|---|
| screen.cpp:873 crossfade Draw -> construct_game_scene(true) (draw.cpp:3790) and its invalidate_screen (draw.cpp:3804) | full_redraw requested | 5436, 7972 (15 scenes each) | 5436, 7711 | no: the transition composes every pixel |
| screen.cpp:864 crossfade End() -> invalidate_screen | invalidate_all_rects | 5436, 7972; presented at the next drawn tick 5442 / 7978 | 7711 -> 7717 | maybe: the last crossfade step was already a whole clean scene. 1 skip per transition on the 486 (5443); not proven safe |
| room.cpp:1080 (load_new_room end), room.cpp:1271 (on_background_frame_change), draw.cpp:2709 R2 old-rect mark with no camera | invalidate_all_rects / in_room rect with no camera | room-change tick only | same | no (inside the stall tick) |
| render_graphics construct_game_scene(false) (draw.cpp:4051) -> UpdateViewports -> on_roomcamera_changed invalidate_screen (draw.cpp:1360), plus draw_software.cpp:241 camera moved | invalidate_all_rects / invalidate_all_camera_rects | 410 ticks: 8168-8208, 8521-8561, ... (41 per room-2 pan) | none (no pan) | only by a scroll-blit (AGS: "TODO: only invalidate what this particular camera sees"); costs ~0-4 skips in RD's room-2 window |
| main/engine_setup.cpp:175 | invalidate_all_rects | lc 0 | lc 0 | no |

- Room 1 after the restore: **zero** latches in both fixtures. R2b's ff_full is 64 in every lab cell, i.e. 32 scenes =
  2 transitions x 16 scenes x 2 eligible characters.
  - RDMP's 112 includes a third transition (10017, room 2 -> 1) that the lab fixtures never reach. Its per-scene count is
    not verified here.
- **The post-click heavy ticks are GUI 0 changes, not latches** (tables/rbtab-H4.txt section 4; cells/H7 rbctl):

| GUI 0 change | caller | lc in H4 (RDMP's click ticks) |
|---|---|---|
| control 0 (label, x 0 y 0 320x10 in GUI 0 at screen 0,144 320x56; ClipControls=0) marked changed | on_mouse_click, script line 1498 (1526 for the first click) | 6154, 6409, 7315, 7701, 7895 |
| the same control marked changed back | repeatedly_execute, script line 737 | 6155, 6410, 7316, 7702, 7896, 8667 |
| label text actually changed (Label_SetText with new text) | repeatedly_execute line 736 | 5437, 8667 only |

| lab H4, ms | click tick 6409 (render part) | GUI 0 tick 6410 | 6411 | change |
|---|---|---|---|---|
| scene | 1.02 | 9.46 | 9.09 | +8.4 |
| of which room view / ui view | 0.76 / 0.09 | 4.29 / 4.88 | 4.04 / 4.88 | +3.5 / +4.8 |
| GUI texture redraw (in ui view) | 0 | 2.81 (1 GUI) | 2.81 | +2.8 (needed) |
| bg_restore / prep_chars / viewports | 0.14 / 0.30 / 0.30 | 0.72 / 0.68 / 0.96 | 0.72 / 0.43 / 0.96 | |
| render (rb_sprite_time / present) | 0.59 (0.22 / 0.12) | 5.33 (4.47 / 0.57) | 5.37 | +4.7 |
| present px | 1,968 | 44,800 | 44,800 | GUI 0 rect + walking character bbox |
For comparison, a whole-surface tick (5442): scene 19.9, render 8.6, present 64,000 px. On the 486 the GUI ticks read
scene ~25 / render ~8.6 against 37.8 / 14.0 at 5442, the same ordering.

### 3.2 Q2 -- click ticks by phase (lab H4 v6, A3; tables/rbtab-*.txt)

| tick | 486 ugo | lab tick ms | script (on_mouse_click) | FindRoute | is_route_possible | dijkstra (passes / scans / cells) | can_see_from (calls) | other |
|---|---|---|---|---|---|---|---|---|
| 6154 first click after restore, 203,136 -> 204,98 | 236.8 | 101.0 | 72.7 (68.4) | 62.3 | **57.4** (cold) | 2.4 (1 / 1 / 1) | 0.1 (4) | input poll 22.5 (lab click injection; 2-4 on other clicks) |
| 6409, 196,135 -> 319,98 | 58.1 | 37.1 | 28.8 | 20.3 | 0.4 | 14.2 (38 / 17,201 / 1,036) | 4.2 (42) | |
| 7315, 311,135 -> 34,128 | 131.0 | 94.2 | 84.6 | 76.3 | 0.7 | **52.1** (91 / 106,608 / 2,863) | **21.2** (96) | |
| 7701, 33,135 -> 0,128 (exit) | 37.9 | 25.0 | 11.8 | 3.2 | - | - | - | |
| 7895 first click in room 2, 945,132 -> 925,69 | 374.3 | 200.0 | 192.1 | 182.2 | **172.8** (cold, 960-wide mask) | 7.9 (9 / 263 / 63) | 0.4 (12) | |
| GCL 8118 first click in room 2, 945,132 -> 680,130 | (380 in LAB-R2) | 252.7 | 244.6 | 242.6 | **167.1** (cold) | 55.4 (88 / 99,400 / 2,758) | 19.6 (93) | |
| GCL 8519..12136, warm, room-2 floor | - | 25-28 | 33 | 25-28 | 1.2 | 18.9-21.0 (45 / ~25,000) | 5.4-5.7 (49) | |

- Every one of these requests returns a 2-node path (nodes=2), so the route search's output is the straight line. The
  cost is the search and the simplification, not the walk.
- No GUI work on a click tick (gui 0/0); no sprite or sound loads; scene and render ordinary. The GUI cost follows on
  the next ticks (3.1).
- No FindRoute outside on_mouse_click in any lab cell: no follower or script-driven re-pathing in these fixtures.

### 3.3 Q3 -- the three no-event spikes (486 RDMP; tables/rdmp-windows.txt)

| tick | ugo | scene + render | logic (incl. wait) | ugo - 21.4 (an ordinary busy tick) | skips after |
|---|---|---|---|---|---|
| 8533 | 98.4 | 5.0 | 93.5 | 77.0 | 2 |
| 9445 | 115.4 | 5.2 | 110.2 | 94.0 = the run's wait_next_frame max (94 ms) | 2 |
| 11775 | 80.3 | 4.2 | 76.0 | 58.9 = ordinary wait ~3.4 + 55.5 (one BIOS tick, 54.9) | 2 |

- The ticks around each spike are ordinary (24.8 ms; skipped neighbours 16-19 ms).
- RDMP's fine phase maxima carry no matching work: script_vm max 350 is the 7895 click; sc_* <= 21; persistent_anims
  max 55 with clamped_neg=1, a uclock step. There is a 94 ms wait. Requested sleep is kept only as a run total:
  17,355 ms requested over 6,550 sleeps against 28,120 ms measured over 6,957 waits. So whether 94 ms was asked for or
  overshot is not recorded.
- In the lab, H replicates RDMP's state through lc 8231, yet no tick near 8533 exceeds 30 ms, and the lab wait max is
  22 ms. Seeds 2 and 3 give game lines identical to seed 1 (the restore fixes the sequence), so randomness is not it.
- Lab-only artefact, for the record: rbslow saw a 79.888 ms tick at one fixed lc per exe (9295, 9623, 12277, 12362)
  while TICKS' own ugo for the same tick was 24.9. That is a uclock read one BIOS tick off inside the lab scope; it is
  the overlay's, not the game's.
- **Not determined:** why the wait runs 59-94 ms. Candidates:
  - (a) AGS's own frame schedule (WaitForNextFrame's next_frame_timestamp, advanced only on rendered ticks) running ahead
    of dos_run_tick_fixed's epoch;
  - (b) a uclock read one BIOS tick off feeding the deadline (11775's excess is one BIOS tick);
  - (c) work booked as wait: 0096's busy-wait calls audio_core_entry_poll() about once a millisecond, so a long poll
    (a buffer refill or decode) lands in wait_next_frame.
  To settle it: one instrumented 486 cell with a per-slow-tick line holding wait_next_frame us, this call's requested us,
  the audio-poll us inside the wait, next_frame_timestamp - now, owed and the epoch (the rbslow line plus those fields),
  landed as an instrumentation patch.

### 3.4 Q4 -- DOSAGS_STALL_RESYNC=1 in the lab (tables/winskips.txt, eqcmp.txt)

| fixture | off (0163 default) | on | catchup ticks / resyncs (on) | game lines |
|---|---|---|---|---|
| GCL (A3 / GSR) | 15 (restore 5, entry 5 + 5 after the 8118 click, 253 ms incl.) | **2** (7974-7975) | 2 / 3 | EQUAL (46) |
| H (H4 / HSR) | 20 (restore 5, room change 5 after 7711, 6155, 7316-7318, 7703, 7896-7900) | **13** | 13 / 2 | EQUAL (48) |
H's 7895 click is 200 ms at 40k (< 250, not a stall, so its 5 skips stay). On the 486 it is 374 ms and would be resynced.

## 4. Q4 -- what "no catch-up after an excluded stall" changes (pacing semantics; for the operator)

No lever was built for this. Code: dos_run_tick_fixed() (game_run.cpp, ags patches 0144 / 0163 / 0239), MAX_CATCHUP = 5, DOS_TICK_STALL_THRESHOLD_US =
250000 (self time of one UpdateGameOnce, children excluded).

- **Today (0163 off).** After a stall of S ms, the next call computes owed = (now - epoch) / 25 ms - ticks run, about S/25
  (80-155 after a room load). It runs min(owed, 5) logic ticks back to back with render and wait suppressed, the 5
  skips. Owed is still > 0, so it rebases the epoch to now and renders one tick.
  - Game time = the loop counter; no tick is dropped.
  - 5 ticks (125 ms of game time) are executed in a burst: about 5 x 17-20 ms on the 486, never shown.
  - The remaining S - 125 ms of wall time is simply not repaid: from then on the game runs S - 125 ms behind the wall
    clock.
- **Variant (DOSAGS_STALL_RESYNC=1, already in both flavours, default off).** The call after a stall tick rebases first,
  so owed is about 0 and there is no burst.
  - The same 5 logic ticks still run, each rendered, 25 ms apart. Per-tick game logic is identical (lab game lines
    EQUAL).
  - The game now runs S behind the wall clock instead of S - 125: **every later tick happens 125 ms later in wall time,
    per stall.**
  - RDMP's 4 qualifying stalls: the run takes ~0.5 s longer wall time; frames_skipped -20; ticks unchanged.
- What that moves:
  - (1) displayed%: up.
  - (2) whole-run tick_rate: slightly down (same ticks, more wall time). tick_rate_steady excludes the stall ticks but
    not the 5 extra rendered ticks.
  - (3) anything paced in wall time against loop-counter events. Music and ambient loops play in wall time, so game
    events shift 125 ms more per stall against them. Today each room load already shifts them by S - 125 (1.9-3.7 s on
    the 486); +125 ms is a 3-6% change of an existing offset.
  - (4) rig fixtures with host-timed clicks (DRIVE): after each stall a wall-clock click lands 5 loop ticks later, so a
    paired comparison sees slightly different click ticks. Lab lc-keyed clicks are unaffected.
- **Which ticks qualify** (self > 250 ms): the restore, each room load and any click whose route search passes 250 ms. On
  the 486 that is 7895 (374) but not 6154 (237).
  - A 240 ms spike keeps its 5 skips; a 260 ms one loses them. If the operator adopts 0163, the threshold edge deserves
    its own line in the registration.
- **Ordering detail seen on the 486.** The room load at 7711 ran as a catch-up tick and the rendered 7712 (118 ms, the
  room's after-fade-in script and ambient sound load) followed in the same call. The resync on the next call forgives
  7712's overrun too. In the lab ordering (stall = rendered tick) 7712's 60 ms is repaid, 2 skips (HSR 7713-7714).
- DOSAGS_FADE_RESYNC (0239) adds nothing here: both lab transitions run inside the stall ticks (faderesync
  transitions=2).
- **486 skip change per run:** RDMP-like -20 (4 stalls x 5, minus any repaid follower overrun: band -14 to -20).
  Release-cell-like (restore, one room change, the 7895-type click): -10 to -15.

## 5. Q5 -- per-finding exactness, risk and 486 saving

| # | finding | lever | exactness / risk | 486 skips per run (RDMP-like) |
|---|---|---|---|---|
| L1 | cold route-possible cache on the first click after a restore or room entry (6154, 7895) | build the cache at the end of the room-load / restore stall (prepare_walkable_areas(player) + the existing analysis) | **exact by construction**: is_route_possible reuses the cache only on a serial hit or a byte-identical mask (0211/0319), else rebuilds; outputs (granularity, labels, routes) are the same function of the same pixels. Risk low; ~170-340 ms more inside an already-excluded stall | **-4 to -8** (6154 5 -> 1-2; 7895 5 -> 1-2; less 7895's share if 0163 is also adopted) |
| L2 | GUI 0 label flash re-marks the whole 320x56 GUI twice per click | mark only the changed control's graphic rect (GUILabel::CalcGraphicRect; old union new) when the GUI itself did not change | exact if nothing outside that rect changes in the GUI texture (only the control changed; ClipControls=0 here, so the unclipped text rect is needed). Medium: render path, the class R3/R2 gate with FRAMEHASH + PRESENT_VERIFY | **-5 to -9** (11 skips after GUI ticks; GUI texture redraw ~7 ms stays) |
| L3 | warm-cache route search (7315, 6409): dijkstra rescans every visited cell each pass; can_see_from 96 calls | bucket queue reproducing the rescan's tie order (LAB-R2 section 7); fewer can_see_from calls in the simplification | exact only if tie order is reproduced; gate = identical routes (RT/RRF rounds). Medium | -2 to -4 |
| L4 | MAX_CATCHUP burst after a > 250 ms tick | DOSAGS_STALL_RESYNC=1 (exists) | game logic identical; pacing changes (section 4); operator decision | -14 to -20 (release-like -10 to -15) |
| L5 | crossfade End()'s invalidate_screen: a whole-surface redraw on the first drawn tick after each transition (5442) | drop it when the last step was a clean full scene | not proven: the backbuffer after the last step must equal a normal frame's; needs the screen gate. Medium | -1 per transition (-1 to -3) |
| L6 | room-2 camera pans: 41 whole-surface ticks per pan (GCL) | scroll-blit instead of invalidate | large change; low value at today's speed | 0 to -4 |
| -- | no-event over-long waits (Q3) | undetermined (instrument first) | -- | up to -6 |
| -- | walking-period single skips (45): idle room-1 ticks have ~0.3 ms slack on the 486 | general speed (logic ~20 ms/tick) | -- | -- |
RD's release cells (RDB1 72, RDB2 65 skips) share the click fixture, so L1-L3 apply to them. L4's share is smaller there
(no return to room 1).

## 6. Files

- docs/lab/rb-lab/apply-overlay-rb.py: the overlay, v7 (runs apply-overlay-r3land.py, copied from r2b-lab).
  docs/lab/rb-lab/lab-rb-overlay.diff: the vendor/ags working tree over 0001-0369 with v7 applied (tracked diff plus the
  new Common/util/dos_lab_rb.h).
- Scripts: rb-lab/{build-main.sh, build-gate.sh (OUTEXE= names the copy), cell.sh (LAB-R2B's, display 398/399),
  runA.sh (FIX= GCL|H, SEED=, EXE=), chain1.sh, chain2.sh}.
- Tools: rb-lab/{rbtab.py (the tables above), rdmp-attrib.py (3.0), tickwin.py, ticks.py, winskips.py, eqcmp.py,
  fhcmp.py, cellcheck.py}. ticks.py and the last four are copied from r2b-lab.
- Records: rb-lab/cells/<TAG>/{CELL.txt, RUN.BAT, RUNMANI.LOG}, plus RBLINES.TXT (only the lab lines, no game text) for
  A3, H4, H7, HSR and GSR.
- Tables: rb-lab/tables/{rbtab-A3, rbtab-H4, rbtab-H7, rbtab-HSR, rbtab-GSR, winskips, eqcmp, rdmp-attrib,
  rdmp-windows}.txt.
- Not committed: exes, TICKS.BIN, STDOUT.TXT (game log text), saves, captures. They stay in
  ~/git/dosags-lab-rb/build/rb/.

## 7. Pre-registration DRAFT -- L1, route-possible cache pre-warm (not registered; for review before any data)

- **Lever.** A port patch, default off for the round. With DOSAGS_RP_PREWARM=1 the engine calls the legacy finder's
  existing cache build once, on walkable_areas_temp as prepared for the player character. It does so at the end of
  load_new_room (after the room's before-fade-in scripts, which can change walkable areas: room 2 removes area 2 at
  load) and after a save restore. Nothing else changes: a later mask change still rebuilds lazily. Witness:
  "DOS-PORT rpprewarm DOSAGS_RP_PREWARM=<v> mode=<n>" plus prewarm count / us in rpcache.
- **Lab gates before any rig time.**
  - Identical routes: an overlay hashes every FindRoute's input and output path; EQUAL on G, V, GCL, H, intro and AQ.
  - Game lines EQUAL; FHASH EQUAL; release game lines EQUAL on 5 Days room 3, Trilby room 35, AQ, P9.
  - Lab bar (H fixture, v6 overlay's rbroute): 6154 FindRoute <= 8 ms (62.3), 7895 <= 15 ms (182.2). The room-load
    stall ticks grow by about the moved build (57 / 173 ms at 40k).
- **486 round, same-binary ABBA x1, R2 on (DOSAGS_CHAR_REUSE=2) in both arms.** Arm A: DOSAGS_RP_PREWARM unset. Arm B: =1.
  Fixture: RD's P9M1 line verbatim. Plus one instrumented B cell with TICKS (RDMP's line).
- **Window.** Room 1 + entry scored as one window (5480-8400) on the persec rows. In the MP cell, also from the
  TICKS-recorded restore (5436) to the TICKS-recorded room-2 entry + 400 ticks.
- **Predictions.**
  - P1 (per pair, room 1 + entry): B has 6 fewer skips than A (band 3-9). **Falsifier: either pair < 2 fewer.**
  - P2 (whole run): mean(B) - mean(A) = +0.09 points (band +0.04 to +0.13). **Falsifier: < +0.02, or a B cell worse than
    its A in the late window by > 5 skips.**
  - P3 (mechanism, MP cell): logic of the first room click after the restore <= 80 ms (RDMP 233) and of the first room-2
    click <= 100 ms (RDMP 370). **Falsifier: either > 120 ms.**
- **Drift note.** Expect the off arms (A) to drift by about 0.5-0.8 points against round RD's R2 cells (98.97 / 99.07),
  as RD's R3-only arms ran 97.93 / 97.44 against RC's 98.43 / 98.24. That is why P1-P2 are paired within the round, not
  against RD. 99% x2 is not claimed by this lever alone: at RD's level +0.09 lands at ~99.06 / 99.16, on the edge.
- Not in this round: L2 (needs its own lab gate first) and 0163 (operator decision, section 4). If the operator adopts
  0163 for the same round, P1's band drops to 2-5 (7895 is then already resynced).
