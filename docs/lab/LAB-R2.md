# LAB-R2 -- MMD room 1 on the GC fixture: the drawn-tick split, the character work, the skip attribution, and an exact R2 design (lab worktree ~/git/dosags-lab-r2)

Copied into the main repo 2026-11-06 from the lab worktree ~/git/dosags-lab-r2 (base 6d1b479d + lab-r3-full.diff); diffs and
readers in docs/lab/r2-lab-patches/, split/character/skip tables in docs/lab/r2-results/. Exes stay local (build_dirty=1).

Lab only: measurement and diagnosis, no speed lever built. Nothing was committed anywhere. ~/git/dosags, ~/git/dosags-r1land,
~/git/dosags-lab-r3, ~/git/dosags-lab-l1 and ~/git/dosags-nightly were not touched (lab-r3 was read: its diff, scripts and
tools). No rig or vcctrl use. All times are DOSBox-X fixed-40000 emulated time unless a row says 486.
Scores docs/lab/R2-PREREG.md (main 6d1b479d, written before any R2 data; not edited).

## 0. Answer first

- **Q1 (shares of a room-1 drawn tick, lab, R1+R3).** Scored as shares, as registered:
  - logic 53.5% (prereg 58-64%): **FALSIFIED, low**;
  - scene 21.7% (prereg 19-23%): **MET**;
  - render 24.8% (prereg 14-17%): **FALSIFIED, high**;
  - character work 2.93 ms = 28.1% of the tick (prereg 3.5 ms of 26.5 = 13.2%, band 9.4-18.9%): **FALSIFIED, high**.
  The registered falsifier (character work < 2.0 ms / 13%, which would mean "R2 is not room 1's lever") is NOT tripped.
  It fails the other way: R2 is a bigger lever than predicted. Fixed 40k underprices the script VM against the 486 (ratio
  2.8x) more than it underprices rendering (2.1-2.5x), so the lab shares lean towards render. The 486's own room-1 split
  (GCMP, R1, measured) is logic 61.5 / scene 21.2 / render 17.3%. On that basis, character work on the 486 is
  **~5.9-6.4 ms per drawn tick (22-24%)**, also above the registered band.
- **The character work is almost all redundant.** All three kids are drawn at 100% zoom: no scaling, no tint, no light.
  The two idle kids (Syd, Bernhard) never change, and Dave is idle in 88.5% of the room-1 frames. Even so, every frame,
  for every kid, the engine:
  1. re-copies the cached image into the raw bitmap (construct_object_gfx's "cached" branch);
  2. re-runs the walk-behind crop-out;
  3. marks the old and new rects dirty, which restores the background under them;
  4. masked-blits the sprite back into the back buffer;
  5. presents the box.
  I hashed each character's final image every frame. A frame with the same input key always had the same image
  (6,953 checks, 0 violations).
- **Q3, measured on the 486 (GCMP TICKS.BIN, instrumented):** spikes alone (clicks, room entry, post-click GUI re-renders)
  cost 69-77 skips (0.99-1.10% of ticks); the budget-bound drawn ticks cost 1,645 (23.5%).
  - This is half the registered 122-151 instrumented. MAX_CATCHUP = 5 plus the resync caps any spike at 5 skips and
    forgives the rest of its debt.
  - Projected to release logic it is 68-72 (0.97-1.03%): right at the release falsifier's 1.0% edge. A release cell on
    the rig scores it.
    (Approximate: the replay agrees with the per-tick skip state on 67.8% of ticks; see the review caveat further down, after the release projection.)
  - In DOSBox-X there is no budget-bound skip at all. S4 (R1+R3, fine timing off) has 15 skips: 5 after the restore,
    5 after the room-2 entry, and 5 after the 253 ms click.
- **R2 (exact, design only):** reuse an unchanged character twice over. First its prepared image (skip the re-copy and
  the crop-out), then its composite (no restore, no re-blit, no present, with R3's per-box recomposite where a dirty box
  reaches it).
  - Saving in room 1: **2.6 ms per drawn tick at fixed 40k** (net of its own cost; +0.25-0.35 from the smaller present).
  - **486: central 5.5 ms, band 3.5-6.5.** That takes room 1's drawn tick from ~26.6 to ~21 ms, under the 25 ms budget.
- **Q2 cannot be scored in DOSBox-X**, and neither can any 486 figure here. Falsifier added on review before any R2 data
  (coordinator, after 6d1b479d): **Q2 is falsified if either release cell of the eventual 486 round lands outside
  97.0-98.6%.** The band must not be read loosely.

## 1. Setup

- Worktree: `git -C ~/git/dosags worktree add --detach ~/git/dosags-lab-r2 6d1b479d`.
  - vendor/ags and vendor/SDL were cloned from ~/git/dosags/vendor. Their tree hashes equal lab-r3's: ags 7dc1074a, the
    0365 head; SDL 580997cd. patches/ does not change between 579c0b5c and 6d1b479d. The series fingerprints were copied
    from lab-r3 (ags 3ecc4317438f).
  - `git apply ~/git/dosags-lab-r3/lab-r3-full.diff` applied cleanly. The working-tree diff is byte-equal to lab-r3's
    (sha256 16f561a9...).
- Check: `make all` on lab-r3-full.diff alone gives **R3REF.EXE, byte-identical to LAB-R3's AGSR3B.EXE** (sha256
  de5517fe...).
- Conf tests/harness/confs/dosbox-x-fixed40k-opl3.conf; ACSETUP-ON-512X384-ROUND.CFG.
- Restore: save 007 from ~/git/dosags/build/ws/roundQ/AGSSAVE.007, `--loadsavedgame 7`.
- Fixture **GCL** (LAB-L1's GC fixture with clicks):
  - DOSAGS_RANDSEED=1, DOSAGS_TAS_AUTO_EXIT_TICK=12440.
  - 16 DOSAGS_LABCLICKS at GCMP's own click ticks (6178 ... 12136). Room 1 alternates (250,135)/(60,135); 7890 is (1,135).
    Room 2 is entered at lc 7972.
- Arms: DOSAGS_GUI_CLIP=4 (R1+R3, scored) and =2 (R1, reference).
- Displays 388/389 only, at most two DOSBox-X instances. Every wait went through tools/waitfor.sh with a pid file and a
  timeout. One cell queued behind another session's exclusive dosbox lock (the harness's own lock) and then ran normally.
- Witnesses checked in every scored cell:
  - `DOS-PORT fixed-timestep: ENABLED` (NOFT gate cells: DISABLED, as intended);
  - `DOS-PORT guiclip DOSAGS_GUI_CLIP=n mode=n`;
  - fine-timing cells record script_vm (the last SET survived); fine-off cells say script_vm "never-entered";
  - RUN.BAT SET lines 301-475 bytes, all under ~500.
- **DOS environment.** LAB-R2's exe takes `DOSAGS_LABCLICKS=GCL`, a preset that expands inside the exe to the same
  16-click string. It saves ~230 bytes. Gate G shows the preset and the spelled-out string give the same frames.

## 2. Instrumentation (lab-r2.diff over lab-r3-full.diff; lab-r2-full.diff = whole vendor/ags diff over the 0365 head; ASCII)

DOSAGS_R2P (read once). Unset = off: one test per hook.

- **=1, timing.**
  - Per character per frame: uclock around construct_char_gfx and around prepare_and_add_object_gfx.
  - The cache path taken. construct_object_gfx records: 2 = cached, raw bitmap kept; 3 = cached image re-copied;
    4 = drawn from the sprite (transform / tint / plain blit) and re-cached. Also whether the sprite was transformed or
    tinted, and walkbehinds_cropout's return value.
  - An input key compared with the last frame's: sppic (sign = mirror), view/loop/frame, the 6 tint/light fields, zoom,
    width/height, the final atx/aty, usebasel, transparency, walk_behind_baselines_changed, and the dynamic-sprite
    change flag.
  - uclock around each character's composite in RenderSpriteBatch, matched by the bitmap the character registered that
    frame.
  - Lab TICKS.BIN kinds: 7 wait_next_frame, 8 sc_prep_chars, 9 character blit us/pass, 10 bg_restore,
    13 rb_sprite_time us/pass, 14 character blit px/pass.
  - Checkpoint lines `labck c=r2char` and an exit summary in RUNMANI.LOG.
- **=lo:hi, detail.** Everything in =1, plus, inside the window:
  - an FNV hash of each character's final image (after the crop-out), compared with its last frame;
  - one `r2f` log line per character per frame;
  - the restore's px split, from the character rects marked since the last restore (camera 0's surface coordinates)
    against the restored spans: kinds 11 (restore px) and 12 (restore px inside character rects).
- Reader tools (build/lab2/tools/):
  - ticks.py groups TICKS.BIN by TICK: the update_game_once close is stamped lc+1, so a tick is every record up to and
    including the next kind-1 record. f1prof.py groups by lc instead and pairs tick N-1's ugo with tick N's render/scene.
  - r2split.py gives the Q1 split; r2char.py and r2frames.py the per-character tables; q3sim.py the skip attribution.
  - ckwin.py, fhcmp.py and eqcmp.py are copied from lab-r3.
- **Trap: DJGPP uclock steps by one BIOS tick.** A handful of samples per run jump by +-54.9 ms at the BIOS tick rollover.
  Seen: one Bernhard prep interval in T4 and L4, one Syd construct interval in L4, one character-blit pass in T2, one
  wait in T4, one render in T2.
  - Medians and the per-frame tables are unaffected.
  - The per-character totals for Syd's construct (L4) and Bernhard's prep (T4/L4) are off by that one sample. Read
    those two from T2 or from the per-frame medians.
  - A negative kind value is counted as 0 and listed by the reader.

## 3. Cells (exit 12440, GCL; results in build/lab2/results/<TAG>/)

| cell | exe | GUI_CLIP | timing | R2P | use |
|---|---|---|---|---|---|
| T4 | R2P | 4 | fixed ts, fine on, TICKLOG, ckpt 5480/7890/8100/12430 | 1 | **Q1 scored** |
| T2 | R2P | 2 | same | 1 | Q1 reference arm |
| L4 | R2P | 4 | same | 5480:7890 | restore px split, image hashes, per-frame log |
| S4 | R3REF | 4 | fixed ts, **fine off**, TICKLOG | - | **Q3 scored** (unprobed) |
| S2 | R3REF | 2 | same | - | Q3 reference arm |
| F4 | R3REF | 4 | fixed ts, fine on, no TICKLOG | - | probe-overhead reference |
| G0 / G1 | R3REF / R2P | 4 | NOFT (every tick drawn), DOSAGS_LAB_FRAMEHASH=1 | - / 5480:7890 | inertness gate |
| SMOKE | R2P | 4 | short (exit 5700) | 5500:5560 | probe check only |

Every cell: exit 0; renders/ticks 100% in room 1 (fixed ts).

**Inertness.** G1 (the probe in detail mode, the GCL preset) against G0 (the unprobed exe, the spelled-out clicks):
FHASH.TXT byte-identical, **EQUAL 7004 of 7004** loop counters. Game lines are EQUAL across T4, L4 and F4 (46 of 46).
The probe's timing cost: whole-run sc_prep_chars 0.611 against 0.533 ms/pass (F4), about +45 us per character-frame;
render_to_screen +0.03 ms/pass; bg_restore, script_vm and present unchanged. In room 1 (3 kids) that is ~+0.13 ms per
drawn tick, all in sc_prep_chars.

## 4. Q1 -- the room-1 drawn tick (loop ticks 5480-7889, steady = drawn and ugo < 40 ms)

busy = ugo - wait (fixed 40k leaves ~14.5 ms of frame wait per tick); logic = busy - scene - render. bg_restore and
sc_prep_chars sit inside scene; the character blits and rb_sprite_time inside render. Character restore = bg_restore x
(restore px inside character rects / restore px), from L4 tick by tick (the fixture is deterministic): 95.7% of the
restored px are the kids' rects; the rest is the pointer.

| ms per drawn tick | T4 (R1+R3) mean | median | share (mean) | share (median) | T2 (R1) mean | share | 486 GCMP (R1) mean | share |
|---|---|---|---|---|---|---|---|---|
| busy | 10.41 | 10.21 | 100% | 100% | 10.68 | 100% | 26.65 | 100% |
| logic | 5.57 | 5.66 | **53.5%** | 55.4% | 5.57 | 52.1% | 16.38 | 61.5% |
| scene | 2.26 | 2.21 | **21.7%** | 21.6% | 2.26 | 21.2% | 5.66 | 21.2% |
| render | 2.58 | 2.58 | **24.8%** | 25.2% | 2.85 | 26.7% | 4.61 | 17.3% |
| sc_prep_chars | 0.81 | 0.66 | 7.8% | 6.5% | 0.81 | 7.6% | -- | -- |
| character blits | 1.56 | 1.54 | 15.0% | 15.1% | 1.56 | 14.6% | -- | -- |
| character restore (of bg_restore 0.58) | 0.56 | 0.61 | 5.4% | 6.0% | 0.56 | 5.2% | -- | -- |
| **character work** | **2.93** | 2.85 | **28.1%** | 27.9% | 2.93 | 27.4% | est. 5.9-6.4 | 22-24% |
| rb_sprite_time (all sprites) | 1.88 | 1.85 | 18.1% | 18.1% | 2.13 | 19.9% | -- | -- |
T4 n = 2409, T2 n = 2409, GCMP n = 1919 (1925 drawn, 485 skipped). Probe-corrected (section 3): character work 2.80 ms of
a 10.27 ms busy tick = 27.2%. GCMP's medians: logic 60.9 / scene 21.0 / render 16.5%.

- Other room-1 facts (T4 checkpoint window 5480:7890, per pass):
  - masked composite 5,728 px, of which the characters are 5,220 (91%);
  - character blits are 1.56 of 1.88 ms rb_sprite_time (83%);
  - present_update_window 0.40 ms for 11,117 bytes in 3 rects, nearly all of it the kids' boxes;
  - no whole-screen restore.
- R3 vs R1 in room 1: rb_sprite_time 1.88 vs 2.13 ms mean (p95 1.89 vs 2.78). At (250,135) and (60,135) the 16x16
  pointer reaches y >= 143, and R1 then composites the bottom GUIs full width.
- 486 character work, two ways:
  - (a) the lab's room-1 component shares applied to GCMP's room-1 render and scene. Render side 1.556/2.581 x 4.608 =
    2.78 ms; scene side (0.813 + 0.560)/2.261 x 5.660 = 3.44 ms; total 6.2 ms.
  - (b) per-phase 486/DOSBox-X ratios, GCMP over T2 whole run (both R1): sc_prep_chars 2.51, rb_sprite_time 2.14,
    bg_restore 2.40. That gives 2.04 + 3.33 + 1.34 = 6.7 ms.
  - Less the probe's ~0.13 x 2.5: **5.9-6.4 ms**. It is an estimate: GCMP has no per-character timer.

### 4.1 Per-character work, room 1 (T2/T4 window 5480:7890; L4 per-frame log; us per frame; 2410 frames)

| | cDave (ch 0, player) | cSyd (ch 1) | cBernhard (ch 4) |
|---|---|---|---|
| size (all frames unscaled: zoom 100, final = sprite size) | 22x77 standing, 26x75 walking | 22x77 | 22x75 |
| flip / tint / light / transparency | mirrored on some walk frames (46 re-transforms) / none / none / 0 | none | none |
| path per frame | cached + re-copy 2311, re-drawn from sprite 99 (new walk frame or flip) | cached + re-copy 2410 | cached + re-copy 2410 |
| construct (get_local_tint, key test, re-copy of the cached image) median | 149 | 146 | 143 |
| prep (walk-behind crop-out + texture sync) median | 23 (468 when the crop-out cuts: 754 frames, standing or walking behind a walk-behind) | 21 | 21 |
| composite (masked blit, R1+R3) mean, px | 506 us, 1876 px | 532 us, 1694 px | 518 us, 1650 px |
| restore of its rect (0.109 us/px) | ~200 | ~185 | ~180 |
| input key same as last frame | 2134 | 2411 | 2411 |
| image hash same as last frame | 2263 (key same: 2133 of 2133 hashed) | 2410 of 2410 | 2410 of 2410 |
| key same but image changed | **0** | **0** | **0** |
All three kids are key-same in 2134 of 2411 frames (88.5%). Dave moves in five runs of 17-65 frames after the clicks
(6179-6195, 6511-6575, 6975-7039, 7206-7270, 7544-7608). A moving kid's box reaches a static kid in 57 frames (Syd), at
48 px a frame on average.

What is redone each frame, for each kid:
- get_local_tint (region tint lookup), then the cache-key test, which hits (same sprite, tint, zoom, mirror).
- recycle_bitmap (same size, no allocation), then a Blit of the cached 22x77 image into actsp.Bmp.
- walkbehinds_cropout over the sprite's columns: a no-op for Syd and Bernhard, a real cut for Dave in 754 frames.
- sync_object_texture: a pointer update in the software driver.
- invalidate_sprite: the rect is restored next frame, recomposited with a masked blit, and pushed by the present.
- Nothing is scaled, flipped (except Dave's walk frames), tinted or lit, and the image is unchanged in every key-same
  frame. AGS has a "same position" short cut for this (optimize_by_position) but disables it for characters ("z coord
  and view offsets"); keying on the final atx/aty/usebasel covers both.

## 5. Q3 -- skip attribution (spike = a tick of ugo >= 40 ms; the >250 ms room entry is counted with the spikes)

Method (build/lab2/tools/q3sim.py):
1. Observed skips: ticks with no render record. A skip is spike-local when its burst starts right behind a spike tick.
2. A replay of dos_run_tick_fixed on per-tick costs:
   - owed = elapsed/25 - ticks;
   - up to MAX_CATCHUP = 5 render-skipped ticks, then a resync when still owed;
   - the normal tick waits to its slot;
   - logic = ugo - scene - render - wait, plus the time outside update_game_once (0.31 ms/tick on GCMP:
     (loop_ms - ugo)/ticks).
3. Counterfactual replays:
   - NOBUDGET: every non-spike drawn tick capped at 24.9 ms, so only spike skips are left;
   - NOSPIKE: spike ticks take the local median costs;
   - NEITHER: both.
4. FIFO labels: each tick's excess is a debt packet; a skip takes the tag of the packets it repays.

| cell | ticks | skipped | spike (standalone NOBUDGET / marginal) | budget (marginal) | other | replay check |
|---|---|---|---|---|---|---|
| **S4** DOSBox-X R1+R3, fine off | 7002 | 15 (0.21%) | **10** (0.14%) | **0** | 5 after the restore (5437-5441) | replay 15 of 15, state agreement 99.9% |
| S2 DOSBox-X R1, fine off | 7002 | 15 | 10 | 0 | 5 (same ticks) | identical skip ticks to S4 |
| T4 DOSBox-X R1+R3, fine on + checkpoints | 7002 | 18 | 10, +3 behind the checkpoint dumps (8101, 8102, 12431: lab artefact) | 0 | 5 (5437-5441) | 18 of 18 |
| **GCMP 486 R1, instrumented** | 7002 | 1732 (24.7%) | **77 (1.10%) / 69 (0.99%)** | **1645 (23.5%)** | 5 after the restore | replay 1722 vs 1732 observed |
| GCMP, logic -0.4 / -1.0 ms (release estimate) | 7002 | -- | 72 (1.03%) / 68 (0.97%) | 1404 / 1052 | | |
| GCMP, spike threshold 30 ms | 7002 | -- | 112 (1.60%) / 99 (1.41%) | 1609 | | sensitivity |

- S4 tick lists:
  - spike skips 7973-7977 (room-2 entry: 2200 ms at 7972, 58 ms at 7973) and 8119-8123 (the 253 ms click at 8118);
  - other: 5437-5441 (the first ticks after the restore).
  - The other click ticks in S4 run 40-43 ms. Cheap logic ticks (5.4 ms) repay them before a skip is needed.
- GCMP spike ticks:
  - clicks at 6178 (241), 6510 (63), 7543 (137), 7890 (45) and 8118 (380);
  - room entry at 7900 (4142) and 7901 (120);
  - the drawn tick that follows each click's catch-up burst: 6184, 6513, 7549, 7892, 8124 (~53 ms: scene 25 ms,
    render 9-10 ms);
  - plus 5442, 8718, 8766, 8795, 9250, 9395, 9627, 10457, 10715, 10748, 11057, 11441.
- GCMP spike-only skip ticks (NOBUDGET replay): 5443 5445 5447 6179-6183 6185 6511 6513 6518 6520 7544-7547 7549-7551
  7553 7554 7556 7557 7559 7561 7893 7894 7896 7898 7901-7905 8119-8123 8125 8719-8721 8723 8724 8726 8728 8730 8767 8796
  8798 8800 8802 9396 9397 9399 9401 9403 9628-9632 10458 10459 10461 10463 10465 10749 10751 10753 11442-11446.
- Observed with the local rule: 49 spike-local, 1683 others. The full lists are in build/lab2/results/*-q3.txt.
- The same post-burst tick in DOSBox-X (T4/S4 8124: scene 10.2, render 5.6 ms, with a normal restore of 0.71 ms) is the
  GUI re-render after the click: the sentence line and verb highlight change (LAB-R3: gAction 2.8-10.8 ms, gMaingui all
  14 controls). It is not a whole-screen restore.
- **Prereg Q3 scoring.**
  - "Recovering them costs 122-151 skips (1.8-2.2%) instrumented": measured **69-77 (0.99-1.10%) on GCMP, so the
    instrumented figure is FALSIFIED, low.** The model missed that dos_run_tick_fixed takes at most 5 catch-up ticks and
    then resyncs, forgiving the rest: the 241, 137, 185, 197 and 380 ms spikes cost 5 skips each, not 10-45.
  - Release (1.0-2.0%, central 1.4; falsifier < 1.0%): **not scorable here** (no release TICKS.BIN). The projection with
    release-level logic is 0.97-1.03%, right at the falsifier's edge.
  - Caveat (review, 2026-11-06): the GCMP replay matches the skip TOTAL (1722 of 1732) but agrees with the observed
    per-tick skip state on only 67.8% of ticks, so the spike-vs-budget split (77 / 1645) and the 0.97-1.03% projection
    are approximate, not tick-exact; read them as ~1%, with more uncertainty than the total carries.
  - The registered cap ("every per-tick lever together caps this fixture at ~98.0-99.0%, central 98.4") becomes, on
    this basis, ~98.9-99.0% (1 - spike skips - the 5 restore skips). So 99% sits at the edge of the cap rather than
    beyond it, and a release cell decides.

## 6. R2 -- what an exact character cache can skip (design only; nothing built)

### 6.1 Two levels, both keyed on the per-character input key of section 2 (all of it equal to last frame's, in the same room)

- **R2a, prep reuse (draw.cpp, software mode only).**
  - What it does: when the key is equal and actsp.Bmp still holds last frame's final image, construct_object_gfx returns
    "intact" and prepare_and_add_object_gfx skips the crop-out (actsp_modified = false). That skips the re-copy of the
    cached image and the walk-behind crop-out.
  - Only construct_object_gfx and walkbehinds_cropout write actsp.Bmp. GetCharacterImage (pixel hit tests) only reads it.
  - This is AGS's own optimize_by_position short cut, made safe for characters by keying on the final atx/aty/usebasel
    and the walk-behind-baseline flag.
  - Exact because the final bitmap is a pure function of the key (the walk-behind mask is fixed per room). The lab
    shows it: key same => hash same, 6,953 of 6,953.
- **R2b, composite reuse (R1/R3 for room sprites).**
  - What it does: a character that is key-same and was drawn last frame is put on the sprite list with SkipInvalidate,
    so its rect is not marked, not restored and not presented. It is flagged to the driver like 0170's GUI entries, and
    R3's per-box clip recomposites it only inside the dirty boxes that reach it (a moving kid, the pointer). A box set
    that never reaches it means it is not drawn at all.
  - Exact by R3's argument: everything written into its rect this frame lies inside the dirty boxes; outside them the
    buffer still holds last frame's composite of the same entry at the same place.
  - Extra rules R2b needs:
    1. A character that turns off, leaves the room, changes z-order (usebasel) or stops being key-same must mark its OLD
       rect, as patch 0197 does for objects. It is no longer re-marked every frame.
    2. It falls back to a full mark whenever R1's latch is set (back-buffer change, alias switch, tint/plugin entry),
       on any invalidate_all / camera move, and on a coarse restore (R3's coarse bits).
    3. Entries above it in z-order need nothing extra: they are drawn after it. Entries below it that change are in the
       dirty set, and it is recomposited there.
- **Not worth caching:** scaling, flipping and tinting (never in room 1), and the DDB sync (a pointer in the software
  driver).

### 6.2 Saving per drawn tick, room 1

At fixed 40k, from key-same kid-frames only (2.89 of 3 per frame):

| part | R2a | R2b | per drawn tick |
|---|---|---|---|
| re-copy of the cached image | yes | | 0.42 |
| walk-behind crop-out + sync | yes | | 0.19 |
| masked composite | | yes | 1.50 |
| restore of the rect | | yes | 0.55 |
| gross | | | 2.65 |
| R2's own cost (key build/compare ~10 us a kid, R3 box loop for 3 entries, Syd's 57 partial recomposites), probe | | | -0.05..-0.10 |
| **net** | 0.6 | 2.0 | **~2.6 ms (25% of the 10.3 ms busy tick)** |
| present (11,117 bytes/pass, almost all the kids' boxes: 0.40 ms) | | upside | +0.25-0.35 |

486, scaled per phase with the 486/DOSBox-X ratios from GCMP over T2 (both R1, whole run, the same phases):
- R2a: 0.59 x 2.51 = 1.48 ms;
- composite: 1.50 x 1.71-2.14 = 2.57-3.21 ms (1.71 = the room-1 render ratio GCMP/T2, 4.40/2.56; 2.14 = rb_sprite_time);
- restore: 0.55 x 2.40 = 1.31 ms;
- own cost: -0.15 ms.
- Total: **central 5.5 ms per drawn tick (R2a ~1.5, R2b ~4.0), band 3.5-6.5.** The band is widened downward for the R1
  lesson (an unmodelled per-call cost of clipped masked blits on the 486). The present (+0.6-0.8 at x2.33) is upside
  only, not counted.
- Effect: room 1's drawn tick on the 486, ~26.6 ms (GCMP, R1) -> ~21 ms (band 20-23) with R1+R3+R2. That is under the
  budget, so room 1's budget-bound skips go to ~0, and only its click spikes are left (section 5).
- These are emulator-derived predictions, not 486 measurements.

### 6.3 Gate (for when it is built)

1. **Lab self-check DOSAGS_R2_VERIFY=1.** On every reused frame, also build the image the old way into a scratch bitmap
   and compare. 0 mismatches on G, V, GCL, the intro (rooms 40-49) and AGS Quest.
2. **Digest gates.** NOFT + DOSAGS_LAB_FRAMEHASH=1 + DOSAGS_PRESENT_VERIFY=1 against R2 off, by loop counter: EQUAL on G,
   V, GCL, the intro and AGS Quest AutoPilot (PH BMPs byte-equal), with stale px 0.
   - Two controls must DIFF: (i) reuse without R3's per-box recomposite; (ii) reuse that ignores usebasel or the
     walk-behind-baseline flag.
   - GCL covers kids walking past each other (Dave's box over Syd in 57 frames), standing behind walk-behinds, and
     clicks.
3. **Release equivalence.** Game lines EQUAL against BASEREL on the P9 fixture, R2 off and on.
4. **Timing.**
   - Lab: room-1 pass time per drawn tick down by >= 1.8 ms at 40k against the same binary with R2 off.
   - 486: GC fixture ABBA, instrumented room-1 render+scene per drawn tick down by >= 3.0 ms, and room-1 renders/ticks
     >= 99% in release.

## 7. Q4 -- the spike sources (pointers only)

- **Click: Room::ProcessClick -> the legacy pathfinder** (route_finder_impl_legacy.cpp; MMD is an old data version).
  - Already exact and landed: 0211, 0212, 0317 and 0319 (mask analysis cache, no divides, verified mask reuse, no
    copy-and-flood).
  - What is left is find_route_dijkstra's main loop, which rescans every visited cell on every pass (O(visited x
    passes)). An exact lever is a bucket queue by cost that reproduces the rescan's tie order (lowest visit index first).
    Its gate is identical route hashes, as in the RT/RRF rounds (PLAN.md, STATUS.md RPF1B/RRF1B).
  - Worst case here: 244 ms at 40k, 380 ms on the 486 (8118).
- **The drawn tick right after a click's catch-up burst** (GCMP ~53 ms, scene 25 ms) is the GUI re-render on the
  sentence/verb change: gMaingui re-renders all 14 controls on a change; gAction re-renders the label. An exact lever is
  to re-render only the controls whose state changed (LAB-R3 section 8). It costs 1-2 skips per click on the 486.
- **Room entry** (7900: 4.1 s on the 486, 2.2 s at 40k). It is a >250 ms stall, worth 5 catch-up skips and then a
  resync. DOSAGS_STALL_RESYNC=1 (patch-era hint, off by default) resyncs right after a stall instead. The game's
  per-tick logic is unchanged and only the wall-clock alignment moves, which drops those 5 skips. It needs an equivalence
  gate on game lines, and the pacing change has to be accepted as such.
- **The catch-up cap itself** is why spike skips are small: at most 5 per spike. Raising MAX_CATCHUP would raise them.

## 8. Files

| exe (build/lab2/exe/) | what | sha256 | bytes |
|---|---|---|---|
| R2P.EXE | instrumented, lab-r3-full + LAB-R2 probe + GCL preset | 44a43220f209d72474b4094d267941181aabeac51e9b19aef14773f219ad9cb8 | 8,728,940 |
| R3REF.EXE | instrumented, lab-r3-full only (= LAB-R3 AGSR3B, byte-identical) | de5517feec25df9bf1fd23e43516062ae876b302886e2d18ee6843fe8d9a6d1a | 8,703,734 |
Both are build_dirty=1 lab builds (binary_sha12 of R3REF: 0ca26019bb5c); neither is for the rig.

- Diffs:
  - ~/git/dosags-lab-r2/lab-r2.diff: the probe over lab-r3-full.diff, 6 files including ac/timer.cpp;
  - ~/git/dosags-lab-r2/lab-r2-full.diff: the whole vendor/ags working tree over the 0365 head.
- Scripts: build/lab2/{cell.sh, fix.sh, pair.sh}. Tools: build/lab2/tools/{ticks.py, r2split.py, r2char.py,
  r2frames.py, q3sim.py, ckwin.py, fhcmp.py, eqcmp.py}.
- Results: build/lab2/results/{T4,T2,L4,S4,S2,F4,G0,G1,SMOKE}/ (STDOUT.TXT, RUNMANI.LOG, RUN.BAT, TICKS.BIN, FHASH.TXT,
  CELL.txt). The tables:
  - T4-split.txt, T2-split.txt, GCMP-room1-split.txt;
  - T4-chars.txt, T2-chars.txt, L4-chars.txt, L4-frames.txt;
  - T4-win.txt, T2-win.txt;
  - S4-q3.txt, S2-q3.txt, T4-q3.txt, GCMP-q3.txt;
  - G-fhcmp.txt.
- 486 source (read only): ~/git/dosags/tests/harness/results/GCMP-2026-11-06/{TICKS.BIN, RUNMANI.LOG}.
