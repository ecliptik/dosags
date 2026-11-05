# P2.1-P2.3 presentation research (read-only), 2026-09-17

Paths: DK = ~/git/doskutsu, DA = ~/git/dosags, SDL = DA/vendor/SDL/src/video/dos,
AGS = DA/vendor/ags/Engine. Nothing was edited; nothing touched the target.

## 0. Two facts that change the bake-off before it starts

**F1. Trilby's Notes is NOT a 320x200 game to the engine. It is 320x240.**
Every one of 39 recorded real-hardware logs says `Game native resolution:
320 x 240 (8 bit) letterbox-by-design` (e.g. DA/tests/games/trilbysnotes/
results/HW-486-66-2026-09-17-TNP4B2-STDOUT.TXT). Mechanism: the compiled
game option OPT_LETTERBOX makes `ResolutionTypeToSize(kGameResolution_320x200,
letterbox=true)` return 320x240 (DA/vendor/ags/Common/ac/
gamesetupstructbase.cpp:196-206; flag at gamesetupstructbase.h:184; log line
at AGS/game/game_init.cpp:423). No config key overrides it -- engine.cpp:172
only reports it. That is also why today's 2x fast blit engages at all:
640x480 / 320x240 = uniform 2x (`Render frame set ... 640 x 480`, same log).
=> **Mode 13h (320x200) cannot hold this fixture.** Frame = 76,800 bytes,
exactly doskutsu's case.

**F2. No current fixture is a native 320x200 8-bit game.** Real-hardware
logs exist for three titles only: Trilby's Notes 320x240x8 letterbox, AGS
Quest 640x360x16, Shards 320x200x32. 5days/7days/mmd manifests say
320x200 **16-bit** (from the AGS database, not engine-verified on hardware);
iowna is 32-bit. Mode 13h is 8-bit only (SDL/SDL_dosmodes.c:797-816). So
the Mode 13h rung has nothing to run on until an 8-bit non-letterbox game
exists (the planned BENCH8, or a sourced title). Evidence it would WORK on
this card exists though: DK/docs/internal/MACH64-TRIAGE.md:618-621 -- the
v1.3.0 "g2k-validated S3/Cirrus/Mach64" claim covered SETUP.EXE's
**mode-13h video bench** on the Mach64.

## 1. doskutsu's Mach64 approach

**How the unscaled centred present is done** (DK/patches/nxengine-evo/
0296-centre-320x240-screen-in-oversized-surface.patch, header lines 27-66):
- logical presentation disabled, a render **viewport** installed at the
  offset (`SDL_SetRenderViewport`, patch :135) -- translation + clip;
- direct writers clip to the logical box then translate by the offset;
- dirty rects translated after the logical clip; flush =
  `SDL_UpdateWindowSurfaceRects(_window, &bbox, 1)` (patch :351) with the
  bbox **intersected with the box**, and the "75% changed -> full flush"
  threshold **suppressed** while oversized (header :55-66);
- margins painted **once per window surface**, straight on the surface
  (`SDL_FillSurfaceRect(win, &r, 0)`, patch :218), then one forced full
  refresh (header :44-47);
- **direct-VESA stands down** when centred: `SDL_DOSVesaDirectPresentFull`
  pushes `fb_size` and SDL/0034 "has no rect variant" (header :50-54);
- killswitch `SDL_HINT_DOS_CENTER_OVERSIZED=0`; every site guarded so cards
  with a real 320x240 mode keep byte-identical behaviour (header :72-82).
Steady state witnessed: `flush rect=320x240@160,120 bytes=76800 (surface
would be 640x480 bytes=307200)`, `dirty_path_taken=100 full_flush_taken=0`
(TRIAGE.md:23-26). It depends on the app having set
`SDL_HINT_DOS_ALLOW_DIRECT_FRAMEBUFFER=1` and `SDL_HINT_DOS_PREFER_LFB=1`
(DK/vendor/nxengine-evo/src/main.cpp:2345, :2405) -- see section 2 for why
that matters.

**Why 640x480 and not 512x384 -- recorded, and it is NOT a defect of
512x384:**
- 512x384 (`0x01F3`) exists only in UniVBE's OEM `0x01Fx` series; the card
  ROM's smallest 8bpp modes are 640x400/640x480 (TRIAGE.md:48-51, :465-472).
- Under UniVBE SDL's closest-match picks 512x384 by itself (aspect tie-break;
  DK/docs/internal/MACH64-30FPS-PLAN.md:161-170).
- "512x384 is retired by operator decision"; 640x480 "is the shipping
  configuration" (DK/docs/internal/MACH64-FPS-ROUND-R.md:22-24), because
  "UniVBE is a third-party TSR the user must obtain and install"
  (30FPS-PLAN.md:215-219) -- a **product** reason (no TSR needed), not a
  technical one. The patch author's own preference was the opposite:
  "prefer centring [in 512x384] unless the operator wants the larger image"
  (TRIAGE.md:584-587).
- The stride-caching bug (hub docs/video.md, shared 0125) is the only
  recorded 512x384 *defect*, it is fixed, and 0125 is in DA's SDL
  (SDL/SDL_dosframebuffer.c:1701-1712). 30FPS-PLAN.md:176-182 adds the trap:
  with the native-mode pin OFF a later mode-set moved the hardware to
  640x480 while the engine still composed 512 wide.

**Did doskutsu measure 512x384 vs 640x480? Yes, twice:**
- Pre-centring-fix, same route: fps_mean 3.2 @512x384 vs 2.2 @640x480;
  flip_inner 49.7 vs 90.9 ms; residual tracks the 1.5625 pixel ratio
  (TRIAGE.md:161-176). (Full-surface work then -- not comparable to a
  scoped flush.)
- Post-fix, clean cells: **28.3/28.4 fps UniVBE+LFB @512x384** vs
  **26.9/26.8 card-ROM banked no-LFB @640x480** -- "+1.4 fps ... an upper
  bound on the LFB's share", cross-session band 0.85 (30FPS-PLAN.md:205-
  211). Confounded (provider + LFB + mode change together); no same-provider
  512-vs-640 pair was found.
- Full-surface flush at 512x384 measured 7.4 ms for 196 KB, 50 fps when not
  stalled (TRIAGE.md:497-501) -- POD-83, not the DX2-66.
- NB the "4.77 ms / 76,800 B = 16.1 MB/s" figure was through the **banked
  window** on the POD-83, and its authors call the bandwidth-bound reading
  "an argument from a numerical coincidence, so it is not a call"
  (DK/qa-results/2026-08-21-mach64-tilemap/MACH64-PHASE0-RESULTS.md:90-107).

## 2. The backend's direct-framebuffer path

- `SDL_HINT_DOS_ALLOW_DIRECT_FRAMEBUFFER` (env `SDL_DOS_ALLOW_DIRECT_
  FRAMEBUFFER`, DA/vendor/SDL/include/SDL3/SDL_hints.h:742): checked in
  CreateWindowFramebuffer (SDL/SDL_dosframebuffer.c:981). The app still
  gets a **system-RAM** surface (:986-1008); what changes is the UPDATE
  path: system RAM is copied straight to VRAM, "No cursor compositing, no
  SDL_BlitSurface" (:1886-1897), palette on version change (:1899-1917).
- **That fast path is rect-aware** (full-surface shortcut only when the
  rect list is a full-screen flush, else per-rect copies: :1939-1960 and
  the LFB twins at ~:2002-2095). The banked normal path is also "dirty-rect
  aware" (:2629-2631, loop :2742).
- **The normal LFB path -- the one dosags is on today (`hint_direct_fb=0
  hint_prefer_lfb=0`, DA/tests/games/trilbysnotes/results/HW-486-66-2026-
  09-16-TNP81A-SDLDBG.LOG:40-44) -- IGNORES `rects` entirely.** Lines
  :2792-2960 contain no reference to `rects`/`numrects`; it copies the whole
  source surface every call (INDEX8 memcpy :2829-2843, else
  `SDL_BlitSurface(src, NULL, dst, &dstrect)` :2845), centred via `dstrect =
  {(dst->w-src->w)/2, ...}` (:2801), then cursor composite and optional
  page-flip/`WaitForVBlank` (:2862-2870). **So calling
  SDL_UpdateWindowSurfaceRects from AGS buys nothing on this path; dirty
  rects (P2.4) and flush scoping (P2.2) require the hint = 1.**
- `SDL_HINT_DOS_PREFER_LFB` (env `SDL_DOS_PREFER_LFB`, hints.h:777): the
  fast path otherwise "prefers banked dosmemput ... over nearptr writes to
  the DPMI-mapped LFB" (:1891-1896); PREFER_LFB flips that (:774-781).
  Which is faster on the Mach64/DX2-66 is unmeasured -> P2.0 should time
  both.
- Documented trade-offs (hub docs/video.md "Presentation path"): no vsync,
  tearing expected, "potentially slow readback". Cursor: not composited on
  the fast path -- fine for AGS only if it really hides the SDL cursor and
  draws its own sprite (DA PLAN.md glitch section says so; re-verify).
- doskutsu's engine goes further with the 0034 helper API
  (`SDL_DOSVesaDirectGetState` / `SDL_DOSVesaDirectPresentFull`, SDL/
  SDL_dosframebuffer.c:2962, :3184; engine DK/vendor/nxengine-evo/src/
  graphics/Renderer.cpp:5950, :6071) -- full-surface only, and it stood
  down on the Mach64 (section 1). **Not the lever for dosags.** The lever
  is the plain hint + `SDL_UpdateWindowSurfaceRects`.
- Could ali3dsw.cpp use it? Yes with no API change: Present() already does
  GetWindowSurface + blit + UpdateWindowSurface (AGS/gfx/ali3dsw.cpp:971,
  :1117, :1126). Set the two hints by env first (zero code) and measure;
  then change :1126 to `SDL_UpdateWindowSurfaceRects(window, &dst, 1)`.
  What could break: tearing; loss of page-flip; any reliance on SDL cursor
  compositing; `pitches_match` handling if the window surface pitch differs
  from VRAM pitch (0125 covers the shear).

## 3. How AGS picks window size/scale here, and the config surface

- Defaults: `FsSetup = kWnd_FullDesktop`, `FsGameFrame = kFrame_
  Proportional`, windowed frame = Round (AGS/main/config.cpp:265-268).
  Full-desktop = the backend's desktop size 640x480 (graphics_mode.cpp:247).
- Existing keys (config.cpp:386-400): `[graphics] windowed`, `fullscreen=`,
  `window=`, `game_scale_fs=`, `game_scale_win=`, `filter=`. Accepted
  `fullscreen=` values: `full_window`, `desktop`, `native`, `xN`, `WxH`
  (parse_window_mode, config.cpp:49-79). `round|stretch|proportional`
  (config.cpp:99-105).
- Render frame: `graphics_mode_update_render_frame()` calls
  `get_game_frame_from_screen_size(native, screen, CurFrameSetup)` with
  **scale = 0**, so Round = the LARGEST integer that fits (graphics_mode.cpp:
  571-580, :203-221), centred by `CenterInRect`.
- Real fullscreen consults the driver's mode list (`find_nearest_supported_
  mode`, graphics_mode.cpp:271-289); **windowed does not** (:272-277) while
  the DOS backend silently resizes the window to whatever mode it picked
  (`window->w = mode->w`, SDL/SDL_dosvideo.c:39-47, closest-match :76-83).
  AGS then keeps its own requested size (`OnModeSet(set_mode)`, ali3dsw.cpp:
  ~176-180). On a card with no 320x240 mode that is the recipe for
  doskutsu's original top-left-corner bug. `--windowed --gfxfilter stdscale
  1` = legacy windowed + scale 1 (config.cpp:282-297): proven only on
  DOSBox-X where a 320x240 mode exists. **Prefer explicit real fullscreen.**
- Mode selection: list built once at video init (SDL/SDL_dosmodes.c); VESA
  320x200x8 always skipped in favour of the synthetic Mode 13h entry
  (`VGA_MODE_13H_SENTINEL 0xFFEE`, :87, :692-696, :797-816; set via INT 10h
  AX=0013h, `banked_mode = true`, :938-946). Explicit pin:
  **`SDL_HINT_DOS_FORCE_MODE_ID`** (shared 0126; SDL_dosmodes.c:621-660;
  env name is literally `SDL_HINT_DOS_FORCE_MODE_ID`, hints.h:845) filters
  the list to one VBE id and falls back loudly if absent.

Minimal routes, per candidate, for a 320x240x8 (or 320x200x16) game:
- (b) **512x384 centred 1x -- config only:** `fullscreen=512x384` +
  `game_scale_fs=round` (Round gives 1x: 512/320=1). Optional belt:
  `SET SDL_HINT_DOS_FORCE_MODE_ID=0x01F3` (0x01D4 for 16-bit). Needs
  UniVBE resident (it is: TNP81A-SDLDBG.LOG:1-3).
- (c) **640x480 centred 1x -- needs ~5 lines of new code:** Round at
  640x480 yields **2x** for 320-wide games, and no key caps the scale in
  fullscreen. Smallest change: a DOS-only max-scale cap (env, e.g.
  DOSAGS_MAX_SCALE=1) where `get_game_frame_from_screen_size` is called
  with scale 0 (graphics_mode.cpp:579) -- the function already takes a
  `scale` argument (:197-198).
- (a) **Mode 13h:** `fullscreen=native` (or `x1`) for a true 320x200x8
  game -> nearest supported mode = the 13h entry. No fixture today (F1/F2).
- AGS Quest is already 1x: Round/Proportional at 640x480 -> 640x360 centred
  (dst.y = 60).

## 4. The per-present letterbox fill, and scoping

- The fill: `if (dst.x != 0 || dst.y != 0 || dst.w != win_surface->w ||
  dst.h != win_surface->h) SDL_FillSurfaceRect(win_surface, nullptr, black)`
  -- **whole window, every present** (ali3dsw.cpp:1097-1098). For AGS Quest
  that is 614,400 bytes of fill per present.
- Then a generic `SDL_BlitSurfaceScaled(..., NEAREST)` even at 1:1
  (:1117; fast blit refuses any border or scale 1, :750-760), then
  `SDL_UpdateWindowSurface` = full window (:1126).
- To fix: (1) clear margins once per (window surface, dst rect) -- track
  the last cleared geometry, re-clear only when dst/surface changes or after
  a full-screen effect (doskutsu: once per window surface + one forced full
  refresh); (2) at scale 1 with equal formats replace the scaled blit with
  row `memcpy` into `win_surface` at dst (SDL has no generated INDEX8->
  INDEX8 blitter -- TRIAGE.md:183-185); (3) `SDL_UpdateWindowSurfaceRects(
  window, &dst, 1)`; (4) **set ALLOW_DIRECT_FRAMEBUFFER=1 or (3) is a no-op
  on LFB** (section 2). Shake-screen (dst.x/y from xoff/yoff, :1031-1035)
  and flip must fall back to clear + full update.

## 5. Which preconditions survive in each candidate

Skip-unchanged (0091/0092) `clean_case` (:1051-1053): no flip; src format ==
window format; **dst == the whole window surface**. Compares `blit_src`
only -- the dst test is a conservative guard, not a necessity.
Fast blit (0087/0090) (:744-760): formats equal; dst origin 0,0; dst ==
whole window; exact uniform integer scale **> 1**; the word-store branch
only for `bpp == 1 && scale_x == 2` (:820).

| candidate | skip-unchanged | fast blit | copy per real present |
|---|---|---|---|
| today 640x480 2x (Trilby) | yes | yes | 307,200 + 2x scale |
| 512x384 centred 1x | **no** (dst != window) until relaxed | moot (scale 1) -> generic blit until (2) | 76,800 if scoped; 196,608 if not |
| 640x480 centred 1x | **no** until relaxed | moot | 76,800 scoped; 307,200 not |
| Mode 13h (true 320x200x8 game) | yes (dst == window) | moot; still the generic 1:1 blit | 64,000 |
| AGS Quest 640x360 in 640x480x16 | no | no (border; 1x) | 460,800 scoped; 614,400 + fill today |

So both centred candidates run SLOWER than today until section 4's four
changes land: they lose the skip and the fast path and gain a full-window
fill. Relaxing `clean_case` to "dst lies inside the window and margins are
known clean" restores the skip everywhere, AGS Quest included.

## Recommended order, with risks tied to evidence

1. **Zero-code probe first:** current binary, `SET SDL_DOS_ALLOW_DIRECT_
   FRAMEBUFFER=1` (then also `SDL_DOS_PREFER_LFB=1`) on Trilby 2x and AGS
   Quest, real presents forced. Tells us what the extra normal-path copy +
   cursor/page-flip work costs. Risk: tearing; cursor assumption (sec. 2).
2. **Present() 1x path** (section 4 items 1-3 + relaxed `clean_case`),
   validated under DOSBox-X with the hub's ready-made
   `shared/tools/dosbox-x-oversized.conf` (`allow low resolution vesa modes
   = false`, :69) via `dosbox-run.sh --conf` -- doskutsu's own stand-in for
   this card. This is P2.2 and the enabler for (b)/(c) at once.
3. **Bake-off on Trilby (320x240x8):** (d) today's 2x, (b) 512x384 centred
   by config, (c) 640x480 centred with the scale cap. Expect equal flush
   bytes for (b)/(c); doskutsu's only comparison favours 512x384 by <= 1.4
   fps and is confounded. (b) needs UniVBE; (c) does not -- the same
   product question doskutsu's operator settled for 640x480. Risk: mode
   pick differs per provider (pin with FORCE_MODE_ID); never use the
   windowed route on this card (section 3).
4. **Mode 13h** only once an 8-bit non-letterbox fixture exists; prior
   evidence says the card runs it (TRIAGE.md:618-621).
5. Dirty rects from AGS's own tracking (`invalidate_rect_*`,
   `update_room_invreg_and_reset`, AGS/ac/draw_software.cpp:259-505) last;
   pointless before step 1 proves the hint path.

Not found: a same-provider, same-build doskutsu 512x384-vs-640x480 present
cost pair; any DX2-66 Mach64 bandwidth figure; a recorded technical defect
of 512x384 beyond the fixed stride bug.
