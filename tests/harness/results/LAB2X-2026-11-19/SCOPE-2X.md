# SCOPE-2X -- a narrowed 2x present for 320-wide games on the Mach64 (scoping only, 2026-11-19)

Read-only scoping. Source: /home/claude/data/worktrees/dosags-ring (detached 55d2b2fa, vendor/ags at the ags 0383
patch level, vendor/SDL as vendored). Records: PLAN.md, PLAN-GATES.md, STATUS.md, LAB-S32.md, the hub's
HARDWARE.md and docs/video.md, and cell logs under tests/harness/results/. Nothing was built or run.
Labels: [M] = read from a log or the source; [m] = modelled from [M] rates, with the assumption stated.

## 0. Short answer

Yes for steady 40 ticks/s, and plausibly yes for 99% displayed at 8 and 16 bit. It is not yet shown for the
whole-run bar or for 32 bit. The brief's premise holds:
the narrowed present rejects every scaled present (sec. 1). On top of that, at 2x the engine pays a full-frame
scale blit on every present, and at 8 bit a full-frame byte compare as well. So today's 2x costs about 55 ms per
present at 8 bit [M] (S8 at 2x: 27% of frames displayed, fps_p50 9.78 [M]). If both the blit and the push are
narrowed to the engine's dirty boxes, scaled by 2, the model adds +0.3 to +3.0 ms per present at 8 bit,
+0.8 to +2.5 ms at 16 bit and +0.4 to +4.2 ms at 32 bit [m]. The biggest risk is not the narrowed frames. It is
the 15-17 full-frame presents per gate run (room entry and fades) [M]. At 2x each of those costs 4x or more,
and the whole-run margin on the v0.1.1 exe is only 0.42-0.65 s [M].

## 1. Who scales today, and where the narrowed present rejects scaled output

Scaling is done by AGS, in the SDL software driver's Present(), at
vendor/ags/Engine/gfx/ali3dsw.cpp. It is not done by an AGS gfx filter or by SDL:
- The filter is nominal. After ags 0031 the driver has the one filter "StdScale" (Nearest-neighbour)
  (gfxfilter_sdl_renderer.cpp:23), and Present() always blits at SDL_SCALEMODE_NEAREST (ali3dsw.cpp:219-224).
  There are no hq/linear filters to choose from.
- ali3dsw.cpp:1746-1750 sets dst from _scaling / _dstRect (the render frame from graphics_mode.cpp:583-616.
  ags 0101's DOSAGS_MAX_SCALE caps the scale there and forces "round").
- ali3dsw.cpp:1931-1937: with the alias on, the engine already drew into the window surface, so nothing is
  copied. The alias is 1x only: DosPortAliasTryActivate returns false at ali3dsw.cpp:365-366
  ("1x only; a scaled rung needs the real blit"). ags 0196 relaxed the full-width check to bounds
  (ali3dsw.cpp:383-386). That is why S8/S16 centred in 512x384 get "alias ON x=96 y=72" [M, RV8A/RV16A].
- ali3dsw.cpp:1951: otherwise TryFastIntegerNearestBlit(blit_src, win_surface, dst) (defined at 1301-1501)
  copies the WHOLE frame. At 2x and 8 bit it builds a doubled row with Uint16 stores, then memcpy's it twice
  (1403-1443). At 16/32 bit it does a std::memcpy per output pixel (1468-1494), which is slow. A non-integer
  or mismatched-format case falls back to SDL_BlitSurfaceScaled (1962).
- ali3dsw.cpp:1811-1814 (ags 0102): the unchanged-frame check runs only when pitch*h <= 100,000 bytes. At 1x
  with the alias the surface pitch is the window's (512 or 1024 bytes), so the check is off. At 2x and 8 bit the
  320x240 vscreen is 76,800 bytes, so the check RUNS on every present attempt: 6.72 ms/call, plus a
  76,800-byte cache copy on each changed frame [M, C364044].

The rejection (ags 0124/0128/0129) is at ali3dsw.cpp:2007-2009, with the gate at 2015-2016:

    const bool _dp_one_to_one =
        blit_src && dst.w == blit_src->w && dst.h == blit_src->h;
    if (!_dp_one_to_one) dos_port_dirty.rej_scaled++;
    ...
    if (hint_on && _dp_one_to_one && dos_port_dirty.scene_path &&
        !dos_port_dirty.is_full && dos_port_dirty.valid && !palette_only_present)

At any scaled rung _dp_push stays dst, _dp_narrowed stays false, and the push at 2272-2276 is
SDL_UpdateWindowSurface (the whole window). Confirmed in the logs: G2R1 "narrow=0 full=1500 ... rej
scaled=1500" (bench8, dst 0,40 640x400); C364044 "narrow=0 full=1000 ... rej scaled=1000" (Trilby room 35,
640x480); SB5O / WBF1 likewise.

The SDL side already supports a narrowed push and needs no change for the basic design. In
vendor/SDL/src/video/dos/SDL_dosframebuffer.c, DOSVESA_UpdateWindowFramebuffer (1874) copies only the rects
it is given on every direct-FB branch: pack24 (2142-2143 -> dos_pack24_push 1824-1872), banked single/multi
(2150-2288) and LFB nearptr (2289-2343). A whole-window memcpy happens only when the list is one full-mode rect
(_dos_port_is_full_fb_rect_list, 603). The palette goes to the DAC by palette version, independent of the rects
(2113-2132). The window surface is system RAM, and SDL never scales.

The present-path patches involved (patches/ags/): 0029/0031 (window-surface present, one filter), 0087/0090
(integer fast blit), 0091/0099/0102 (unchanged-frame skip and its 100 KB rule), 0100 (bordered present,
margins cleared once), 0101 (DOSAGS_MAX_SCALE), 0103 (direct-FB opt-in), 0104 (palette-only present), 0120
(alias), 0124 (narrowed multi-rect present; consolidates 0124/0128-0132/0134), 0167 (GUI clip), 0192
(DOSAGS_PRESENT_VERIFY), 0193 (pushed set covers the restore carry), 0195 (freeze ticks, DOSAGS_BREAK_0193
control), 0196 (pillarbox alias). SDL: 0210 (pack24, SDL_dosmodes.c:684-773, SDL_dosframebuffer.c:519-560).

## 2. Modes available (target's own UniVBE list, e.g. RLTB-2026-11-12/RLTBSDL.LOG:9-27)

    640x400:  8 bpp 0x0100 (pitch 640)                 -- no 15/16/24/32-bit 640x400
    640x480:  8 bpp 0x0101 (640)   15 bpp 0x0110 (1280)  16 bpp 0x0111 (1280)
              24 bpp 0x0112 (1920; with SDL_DOS_PACK24=1 offered as XRGB8888, the 32-bit gate's mode)
              32 bpp 0x01B0 (2560; hidden under PACK24; writes at 7.70 MB/s vs 27.2 at 24 bpp, HARDWARE.md)
    512x384:  0x01F3 / 0x01E4 / 0x01D4 / 0x01C4 / 0x01B3 (the 1x rungs today). No 320-wide VESA mode.

All three gate games are 320x240 to the engine ("letterbox-by-design"; RV8A/RV16A/RV32A). At 2x in 640x480
the picture is dst (0,0,640,480), with no border at any depth. The game's own letterbox bars sit inside the
vscreen, are static and are never dirtied.
A 320x200 game at 2x has two options:
- 640x480 at dst (0,40,640,400): letterboxed 40 rows top and bottom [M, G2R1 "render dest (0, 40, 639,
  439)"]. Square pixels: the picture looks squashed next to a 4:3-stretched 13h or CRT 320x200.
- 8 bit only: 640x400 0x0100, which fills the mode with no border. Mode 13h already serves 8-bit 320x200 at
  full speed (Gate 2).
There is no 16/32-bit 640x400, so 16/32-bit 320x200 games can only use the letterboxed 640x480.

## 3. Design: a narrowed 2x present

Principle. The engine-side dirty set (draw_software.cpp: dos_port_dirty, boxes in GAME coordinates, cap
DOSAGS_DIRTY_BOXES default 8 (:422-423), array max 32 (draw_software.h:54), 0193 restore carry) does not
depend on the present scale. At 1x with the alias, pushing the set is enough, because the window surface IS the
vscreen. At 2x the window surface is a scaled copy that persists between presents. So:
(a) scale-blit only each dirty box from the vscreen into the window surface, at (dst.x + 2*x1, dst.y + 2*y1,
2*w, 2*h); then (b) push exactly those scaled rects.
The window surface stays equal to scale2(vscreen) everywhere under the same invariant 0193 already proves for
1x: the pushed set covers every pixel changed since the last present. The screen-equality gate checks this
(sec. 5).

Where. All the work is in ali3dsw.cpp Present(). No SDL change is needed for the basic design.
1. Widen the 0124 gate with a second accepted geometry: exact uniform 2x (dst.w == 2*src->w &&
   dst.h == 2*src->h), blit_src == _vscreenSurface (no flip scratch), margins_clean, dst_inside, same window
   surface and dst as the last full present, and formats equal. Every other case keeps today's full path.
2. Clamp the boxes to the GAME size (src->w-1, src->h-1), not dst.w-1/dst.h-1. Today's clamps (2029-2030,
   2140-2141, 2113-2114) are only right because dst == src at 1x. At 2x they would let a box run to x=639 in
   game space. Then scale: r = {dst.x + 2*x1, dst.y + 2*y1, 2*w, 2*h}. With integer 2x there is no rounding:
   every output pixel belongs to exactly one source pixel. The "smaller than the screen" tests (2041, 2153)
   compare scaled area to dst area.
3. Replace the full-frame TryFastIntegerNearestBlit call with a per-rect 2x blit over the same rects that will
   be pushed. Write both output rows directly with dword stores and no row_buf:
   - 8 bpp: two source px -> one Uint32 (a,a,b,b).
   - 16 bpp: one px -> one Uint32 (p | p<<16).
   - 32 bpp: two Uint32 stores.
   Drop the per-row uclock calls (two per row today). Use the same code for the full-frame fallback, so the full
   2x present also gets faster (sec. 4).
   AGS's own filters are not an alternative: the driver has no other filter, and nearest-neighbour integer
   replication is exactly what TryFast already produces, so the full-push reference (DOSAGS_DIRTY_PRESENT=0)
   is pixel-comparable.
4. Bypass the unchanged-frame check (1811-1879) on frames that will narrow. It costs 6.72 ms per attempt at 8
   bit [M], and the engine's dirty set makes it redundant. KEEP it on frames that cannot narrow (no scene,
   latched full). Otherwise an 8-bit fade loses ags 0104's palette-only present and every fade step becomes a
   full 2x present (~49 ms today [M], 20-28 ms rewritten [m]).
5. Counters: rej_scaled stays as is for non-2x scales. Add frames_narrow2x, px_narrow2x and blit2x_rect_px,
   and keep the kDW_BlitScBytes / kDW_PushBytes accounting (it already handles rect lists, 2223-2253).

Depth notes.
- 8 bpp INDEX8: the blit copies indices. SyncPaletteIfNeeded (1699) plus SDL's version-gated
  ProgramVGADAC set the colours for the whole screen. Palette-only presents stay as in (4).
- 16 bpp RGB565: same format both sides (TryFast already requires src->format == dst->format). A 555 card
  falls back to the generic path, which is not narrowed.
- 32 bpp with SDL_DOS_PACK24=1: AGS writes XRGB8888 into the 2560-pitch window surface, and dos_pack24_push
  packs each pushed rect 4->3 bytes straight into the 1920-pitch LFB (rect-honouring already, 1830-1871). No
  change is needed for correctness. Cost note: at 2x the RAM intermediate is 16 bytes per source pixel.
  Alternative B (below) removes it.

Interactions.
- Pillarbox alias (0120/0196): it never engages at 2x (365-366). The engine renders into _origVirtualScreen
  (already allocated). Nothing to change, but note that the 2x rung loses the alias's free "blit".
- Multi-rect cap: at 2x every merged-away waste pixel costs 4x in both blit and push, and SDL's per-rect cost
  is a per-row loop (2333-2340 LFB, 1853-1869 pack24), which doubles with height. The knee measured at 1x
  (8 boxes) may sit higher at 2x. Sweep DOSAGS_DIRTY_BOXES=8/12/16 on DOSBox-X counters (px pushed, rects)
  before the 486. The 0134 merge-pricing accounting already prices it.
- Full-frame fallbacks (today's path, unchanged in kind): first present at a geometry (margins fill, 1903-1918),
  screen shake (dst moves), flip (scratch), no scene (rej_no_scene), latched full (0193 whole-surface
  invalidations), and a box set not smaller than the screen. Gate runs show 15-17 of them [M, GL8A/GL16A/GL32A:
  noscene 12, latched 3-5].

Correctness risks, and what covers each:
- Under-blit: a box that was pushed but not blitted, or a change not in the set. Here the 0192 verifier is
  VACUOUS: the window surface is written only where it is pushed, the same blind spot gate-alias.sh's header
  describes for the alias. Covered only by screen-equality (sec. 5).
- Clamp bug (step 2): covered by the screen-equality rows at the screen edges (walk arm).
- Letterbox borders at 320x200 2x: narrowed rects lie inside dst by construction, and the margins are cleared
  once and pushed by the full present that cleared them (0100).
- Cursor: drawn into the vscreen and marked as kDirtySrc_Cursor (draw.cpp:4101). SDL composites no cursor on
  the direct-FB path (SDL_dosframebuffer.c:2101-2102). A cursor drawn outside the scene path would show as a
  screen-equality failure.
- Palette: version-gated DAC, as above. A palette change with no pixel change at 8 bit needs (4).
- A first frame after a mode set or a vscreen recreation must be full: the margins_clean/geometry latch
  handles it, plus a new "last full 2x present" latch.

Alternative B (not recommended first): scale inside the SDL push. AGS would hand SDL the 1x surface, and
the DOS backend would write each rect doubled straight into VRAM. This removes the RAM intermediate (about
10/20/40 ms per full frame at 8/16/32 bit) [m], but it changes SDL's window/surface size contract. It is
shared platform work (a hub shared/ change by PR and a subtree bump), and it buys little on narrowed frames.
Consider it only if the full-frame fallbacks decide the result.

## 4. Cost estimate

Measured per-unit rates on the 486 (Mach64, UniVBE, LFB):
- 8-bit 2x horizontal replicate: 0.325 us per source px [M, C364044: 24.93 ms / 76,800].
- RAM row write (vmemcpy): 0.0336 us/B (~29.7 MB/s) [M, C364044: 10.34 ms / 307,200 B]; 0.0301 at 16 bit
  [M, WBF1].
- 16-bit 2x replicate (memcpy-per-pixel loop): 1.30 us per source px [M, WBF1: 100.04 ms / 76,800].
- Full-frame LFB push: 0.0366 us/B = 27.3 MB/s [M, C364044 11.25 ms / 307,200 B; WBF1 22.42 / 614,400].
  SB5O's 4.92 ms for 614,400 B is unexplained and not used.
- Small-rect push at 1x: S8 0.86 ms for 3,759 B in 3.84 rects [M, C3512]; S16 0.21 ms for 3,705 B [M,
  BLITE/S2F2]. Per-rect and per-row overhead, not bandwidth, sets these.
- pack24 push: 0.11 us/px bandwidth (HARDWARE.md 24-bpp row) up to 0.32 us/px all-in [M, LAB-S32 9.9 C2P:
  6.72 ms per present at ~20,745 px].

Same scene, same binary, 1x vs today's 2x (Trilby room 35, 8 bit, cap3c 78683aa4c501, 2026-09-25) [M]:

    cell      rung             steady  displayed  fps_p50  present_blit  update_window  dirty_check  rts mean
    C3512     512x384 1x alias  40.19   98.48%     40.00    --            0.86 ms        --           3.31 ms
    C364044   640x480 2x full   39.54   26.99%      9.78    37.62 ms      11.25 ms       6.72 ms      28.27 ms
    C364066A  640x480 2x full   39.62   26.93%      9.81    37.71         11.30          6.71         --

Pixels per present at 1x on the gate scenes (narrowed presents; multi-rect area / narrow count) [M]:
- S8: 2,210 px, 3.75 boxes (GL8A 2026-09-30); 2,205 px (R1I1 2026-11-05).
- S16: 1,299 px, 2.08 boxes (GL16A).
- S32P: 1,388 px, 2.08 boxes (GL32A). The v0.1.1 exe pushes less: RV32A pack24 pushed_px 3,195,838 / 4,990
  presents = 640 px all-in, about 410 px on narrowed frames after removing 15 full frames [m].
- The release flavour prints no dirtypresent, so the current S8/S16 areas are unmeasured. They may be lower
  than the Sept/Nov figures (the redraw levers landed since).

Narrowed 2x, per narrowed present [m] (2x = 4x the dst px, 2x the rows of the 1x set):

    scene  src px       scale-blit (today's loop / rewritten)   push 2x          2x total   1x today   added
    S8     ~2,205       1.0 / 0.5-0.8 ms                        0.32-2.0 ms      0.8-3.5    ~0.5       +0.3..+3.0
    S16    ~1,300       2.0 / 0.5-0.8 ms                        0.38-0.6 ms      0.9-2.6    ~0.15      +0.8..+2.5
    S32P   410-1,388    0.7-2.9 / 0.25-1.25 ms                  0.18-1.8 ms      0.4-4.6    0.05-0.45  +0.4..+4.2

How the ranges are built:
- Push low end: bandwidth only.
- Push high end: the 1x small-rect push cost scaled by 2-4x (rows double, bytes x4).
- 32-bit scale with today's loop is not measured. It is taken as the 16-bit rate plus 16 B of RAM write.
For comparison, today's full 2x present: 48.9 ms at 8 bit plus the 6.7 ms check [M]; 143.4 ms at 16 bit [M,
WBF1]; about 150-250 ms at 32-bit pack24 [m].

Full-frame fallbacks per 5,000-tick run: 15-17 [M].

    depth  1x full       2x today        2x rewritten       2x fused (alt B)   added per run (today .. rewritten)
    8      ~2.8 ms [m]   48.9 ms [M]     20-28 ms [m]       ~13 ms [m]         0.3-0.8 s
    16     ~5.6 ms [m]   143.4 ms [M]    40-55 ms [m]       ~25 ms [m]         0.5-2.1 s
    32p24  8.5-25 ms     150-250 ms [m]  75-140 ms [m]      35-100 ms [m]      0.4-3.4 s

Whole-run margin over 39.2 on the v0.1.1 exe [M, from tick_rate]: RV8A 39.33 -> 0.42 s; RV16A 39.40 -> 0.65 s;
RV32A 39.38 -> 0.58 s. The full-frame cost lands in one of two places:
- If those presents fall in room-entry or stall time (likely: noscene = not via construct_game_scene), they
  count against whole-run directly.
- If they fall in ordinary ticks, the pacer catches up by skipping renders: about 1 skipped frame per 25 ms,
  i.e. 0.25-0.65 pp displayed at 8 bit, 0.4-1.7 pp at 16, 0.3-2.7 pp at 32.
Either way, at 16/32 bit a faster full 2x path is a requirement, not polish.

Displayed% cannot be predicted tightly from the records. The gate cells do not time wait_next_frame, so the
per-tick slack distribution is unknown. At 1x the gate scenes skip 0.4-0.7% of frames (RV: 33/4999, 22/4999,
32/5002) [M]. Every added millisecond pushes some near-budget ticks over. Step 0 in sec. 5 measures that slope
without writing any code.

## 5. Falsifiable lab plan

Step 0 (486, no code, optional but decision-grade). Measure the price of "+N ms per rendered frame" at 1x using
the existing ags 0251 knob DOSAGS_MI_RENDER_DELAY_MS=N (draw.cpp:1610-1625; SDL_Delay with ~1 ms naps,
SDL_systimer.c:67-104; present in both flavours). Run the RV fixture lines with N=2 and N=4 on S16 and S32P
(and S8 if the cap allows), 4-6 cells.
- Reads: displayed and whole-run vs N.
- Decision rule: if N=2 already takes displayed under 99.0% at a depth, the narrowed 2x cannot meet the 99%
  line there without offsetting savings. Stop or re-scope before building.
- Caveat: the delay is flat, while the real 2x cost grows with the dirty area, which tends to be largest on the
  heaviest ticks. So step 0 UNDER-states the real cost.

Step 1 (DOSBox-X: build, then the screen-equality gate). Tools that exist: tests/harness/run-dosbox.sh
--freeze-capture (ags 0195, DOSAGS_FREEZE_TICKS), tests/harness/screen-equal.py (tick-synchronised PNGs, pixel
for pixel, void on a tick mismatch), and tests/harness/gate-alias.sh, whose A/B/C structure is reused.
.sdl-dos-ports/shared/tools/dosbox-run.sh / dosbox-launch.sh / dosbox-teardown.sh sit underneath, and
tests/ratchet.yaml takes the rows with --break-a controls.
- Arms, per row:
  - A = narrowed 2x (default).
  - B = DOSAGS_DIRTY_PRESENT=0 at the same 2x rung. This is the full scale plus the full push, and it is the
    reference as long as the new path sits under the same hint.
  - C = DOSAGS_BREAK_0193=1, which MUST differ from B.
- Rows: bench8 x7 arms at 640x480 2x (320x200 -> y=40); bench16 2x; 5days room 3 at 16-bit 2x; 5days room 3
  forced 32 + SDL_DOS_PACK24=1 at 2x; trilbysnotes room 35 at 8-bit 2x; an 8-bit fade row; a screen-shake row
  if any fixture has one; an edge-walk row for the clamp.
- Pass: every A==B pair identical at every freeze tick, both runs frozen at the same tick, and at least one
  control differing per row (exit codes as gate-alias.sh).
- Also on DOSBox-X counters (not timing):
  - dirtypresent rej scaled=0;
  - narrowed share >= 99% of presents outside the 15-17 full ones;
  - unchanged-check calls = 0 on narrowed frames;
  - push_bytes / presents about 4x the 1x row's.
- gate-present.sh's 2x rows (DOSAGS_PRESENT_VERIFY) stay, but they are vacuous for this path, as the alias rows
  are. The screen-equal rows are the gate.

Step 2 (486 A/B, one power-on, operator approval; instrumented flavour in BOTH arms so dirtypresent and the
work vector print).
- Scenes:
  - S16: 5 Days room 3, 16 bit.
  - S8: Trilby room 35, 8 bit, DOSAGS_MSGSKIP=1.
  - S32P: 5 Days room 3, forced 32, SDL_DOS_PACK24=1.
- Arms:
  - A = today's gate line (MAX_SCALE=1; 512x384 cfg for S8/S16, the S32P cfg at 640x480).
  - B = same fixture, 640x480 cfg (CAPS8/CAPS16 used one), DOSAGS_MAX_SCALE=2.
- Order: warm-up, then A B B A per scene, 12 cells (~45-55 min of a 120-min cap). Optionally one extra B cell
  per depth with DOSAGS_TICKSTATS_FINE=1 for per-call costs (diagnostic, unscored).
- Witness: B runs at 640x480, so the capture stick locks (A at 512x384 is camera only); camera both.
- Predictions for B against A (same flavour, same exe):
  - S8: steady 40.0-40.3, fps_p50 40.00, displayed A minus 0.3 to 1.5 pp, whole-run A minus 0.05 to 0.2.
  - S16: steady 40.0-40.3, fps_p50 40.00, displayed A minus 0.3 to 1.5 pp, whole-run A minus 0.05 to 0.35.
  - S32P: steady 40.0-40.3, fps_p50 40.00, displayed A minus 0.3 to 2.5 pp, whole-run A minus 0.05 to 0.5.
  - B's push_bytes per present 3-5x A's at 8/16 bit.
  - Against today's 2x anchor (C364044: 26.99%, 9.78): B at least 97% displayed and fps_p50 40.
- What falsifies the model (any one):
  - B fps_p50 < 40 or steady < 40.0 at any depth;
  - B displayed < 95% (the bar's completeness floor);
  - a fine-timing B cell whose per-call present cost is outside the [m] range by more than 2x either way;
  - B dirtypresent showing rej scaled > 0 or narrowed < 95% of presents (the path did not engage, so the cell
    is VOID as a test of the design);
  - any witness defect (a trail, a stale cursor, border garbage).
- Which bar applies: the PLAN-GATES bar numbers (both tick figures 39.2-40.8, fps_p50 >= 40, completeness >=
  95%, witness clean, audio counters, x2), plus the campaign's 99% line (RV's REGRESSION line: displayed <
  99.0%). The bar's rung clause names 1x ("512x384 centred 1x (S32: 640x480x32 1:1)"). A 2x claim is
  therefore a new registration with that clause changed, and that is the operator's call. Proof is the
  registered pair (the operator's standing rule): if step 2 passes, a release-flavour pair per depth follows.

## 6. Open questions, risks, and what the operator decides

Risks, largest first:
1. Whole-run bar at 16/32 bit, from full-frame 2x presents (fades, room entry, latched full). These add
   0.5-3.4 s per run [m] against a 0.42-0.65 s margin [M]. Mitigation: the rewritten scaler (required). If that
   is not enough, alternative B (a hub change) or a cheaper 2x fade path. First, measure where those presents
   fall (tick indices from the tick_stall lines plus a new per-full-present tick log).
2. 99% displayed with unknown per-tick slack: step 0 prices it. If the redraw levers made the current dirty
   areas smaller (as RV32A suggests at S32P), the cost moves toward the low end.
3. Correctness of the narrowed blit: only screen-equality can see it (the verifier is vacuous). Same class as
   the 2026-09-21 alias defect.
4. 8-bit fades lose the palette-only present if the check bypass is too broad (design step 4).
5. The box cap tuned at 1x may be wrong at 2x (sweep on DOSBox-X).
6. The hub's docs/video.md says "present unscaled, never scale to fill". If this works it needs a dated hub
   amendment (narrowed integer 2x as a measured rung), by PR to the hub, not edited here.

Open questions:
- The current exe's S8/S16 dirty area (the release prints nothing). Read it in step 2's instrumented A arms.
- Aspect for 320x200 games: square-pixel letterbox in 640x480 vs 8-bit 640x400 / Mode 13h. For 16/32 bit,
  only the letterbox exists.
- Not investigated: Mode X (320x240 on the VGA core, 8 bit only, planar writes) for S8-class games; any Mach64
  CRTC pixel doubling or overlay scaler.
- Maniac Mansion Deluxe / MS3 (16-bit 320x200, parked at ~95% at 1x): 2x adds cost there. It needs its own
  reading before any per-game default.

Operator decisions:
- Whether to build at all: after step 0, given its slope.
- Default, per game, or a switch. Recommendation: a switch first (DOSAGS_MAX_SCALE=2 plus a 640x480 config,
  surfaced as a setup option "2x picture"), with the shipped default staying the gated 1x. A per-depth or
  per-game default only after a registered pair at that depth passes the bar and the 99% line. 32 bit may stay
  1x.
- Whether the 2x rung gets its own registered gate (the bar's rung clause changed), or stays an unscored
  option.
- Whether alternative B (a hub shared/ change) is in scope if the full-frame fallbacks decide it.

Cells cited: tests/harness/results/{G2R1-2026-09-21, C3512-2026-09-25, C364044-2026-09-25,
C364066A-2026-09-25, WBF1-2026-09-25, BLITE-2026-09-24/{SB5O,S2F2}, GL8A/GL16A/GL32A-2026-09-30, R1I1-2026-11-05,
RV8A/RV16A/RV32A-2026-11-19, RLTB-2026-11-12}; LAB-S32.md 9.9 (C2P); .sdl-dos-ports/HARDWARE.md:51,71.
