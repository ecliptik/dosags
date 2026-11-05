# P2.4/P2.5 + P1 item 3 research: dirty rects, scene skip, idle overhead, fades

Read-only research, 2026-09-17, from the PATCHED tree `~/git/dosags/vendor/ags`
(state incl. patch 0096) and `vendor/SDL`. Paths below are relative to
`vendor/ags/Engine/` unless prefixed. Nothing was edited, built, or run; every
"expected saving" is arithmetic on TNP4B2's recorded tickstats and the clock
probe, NOT a measurement. Numbers are per 1000 logic ticks unless stated.

## 0. Two findings that change the premise of P1 item 3 (read these first)

### 0a. `script_vm` and `rep_exec_vm` are recorded 1000x too small since patch 0083

`dos_port_tick_record()` takes MICROSECONDS (`main/dos_port_tick_timing.h:405`,
`sample_us`; the RAII scope passes `* 1000000LL / UCLOCKS_PER_SEC`, :443-444).
The two manual call sites in `script/script.cpp` still pass MILLISECONDS:

- `script/script.cpp:401-402` (`rep_exec_vm`): `(uclock()-t0) * 1000 / UCLOCKS_PER_SEC`
- `script/script.cpp:484-485` (`script_vm`): same expression

They are the only two such sites (`grep dos_port_tick_record(`: the others, in
`gfx/ali3dsw.cpp:785,912,913`, pass microseconds). Proof in the data itself:
TNP4B2 has `process_events_dispatch max_ms=2605` but `script_vm max_ms=2` -- the
2605 ms fade call IS a `RunScriptFunction()` call, so its sample was stored as
"2605 us" and printed as 2 ms. Before 0083 (TNP82E) the two maxima agreed
(3672 vs 3694 ms).

Corrected reading of TNP4B2 (each value is a sum of ms-TRUNCATED samples, so a
lower bound; true value up to +1 ms per call higher):

| bracket | logged | really | compare with |
|---|---|---|---|
| `script_vm` (917 calls) | total_us=3807 | >= 3807 ms (incl. the 2605 ms fade call) | `process_events_dispatch` 6033 ms |
| `rep_exec_vm` (1003 calls) | total_us=2951 | >= 2951 ms | `rep_exec_wrapper` 3268 ms |

So there is NO "1.63 ms/call of zero-work wrapper overhead": `rep_exec_wrapper`
is ~90%+ real VM calls, and `process_events_dispatch`'s ~3.4 ms/tick is mostly
real `repeatedly_execute`/room-repexec script runs. The plan's P1 item 3 premise
("zero script work") came from this unit bug. Fix = change both expressions to
`* 1000000LL / UCLOCKS_PER_SEC` (and drop the `(long)` cast). No behaviour change.

### 0b. Every script function run reads the SLOW clock -- patch 0096 does not cover it

`ccInstance::Run()` executes `_lastAliveTs = FastClock::now();` once per run
(`script/cc_instance.cpp:614`), again every 1024 backward jumps (:1063-1070), and
in `NotifyAlive()` (:1679-1682, reached from `main/game_run.cpp:1660` only when a
script instance is current, i.e. inside nested/blocking ticks).
`FastClock` is still `std::chrono::system_clock` (`util/time_util.h:105` in the
patched file, just below patch 0096's `DosUclockClock`), i.e. `gettimeofday()`:
**1324.6 us per read** on HW-486-66 (clock probe). Patch 0096 replaced `Clock`
only; its own comment says calendar users stay on FastClock, but the only
FastClock users in the tree are durations: `script/cc_instance.cpp:614,1065,1070,
1682` and load-time stopwatches in `ac/game.cpp:1210-1214,1913-1924`. Nothing
converts a FastClock time_point to calendar time (ScriptDateTime has its own
`SystemClock` typedef, `ac/dynobj/scriptdatetime.h:27`).

Cost: (1003 rep-exec-always runs + ~917 event-dispatched runs) x 1.32 ms
= **~2.5 s per 1000 ticks (~2.5 ms/tick)**, i.e. roughly a third to a half of
what 0a shows as "script VM time" is this one clock read. Fix: under
`__DJGPP__`, `using FastClock = Clock;` (the uclock clock). One line.

## 1. AGS's own dirty-region tracking (software renderer)

- **It exists and is ACTIVE under this port's driver.**
  `gfx/ali3dsw.h:178` `RequiresFullRedrawEachFrame()` returns false ->
  `ac/draw.cpp:733-734` sets `drawstate.SoftwareRender=true`,
  `FullFrameRedraw=false` -> `construct_room_view()` takes the dirty-rect branch
  (`ac/draw.cpp:2845-2848`) and `draw_preroom_background()` runs
  (`:2443-2448`). No DOS-PORT patch disables it (grep of `invalidate_`/
  `FullFrameRedraw` shows only upstream code).
- **PLAN.md's "RenderToBackBuffer() has no dirty-rectangle tracking at all" is
  half right.** `RenderToBackBuffer()` (`gfx/ali3dsw.cpp:474-582`) indeed redraws
  every sprite in the list every frame and knows nothing about regions. But the
  ENGINE tracks regions one level up, in `ac/draw_software.cpp`.
- **What it tracks: where sprites were DRAWN, not what CHANGED.**
  `put_sprite_list_on_screen()` calls `invalidate_sprite()` for every drawn
  thing, every frame, unconditionally (`ac/draw.cpp:2758-2761`): room objects,
  characters, room overlays (in_room=true), GUIs and UI overlays
  (in_room=false, via `draw_gui_and_overlays()` `:2739-2742`), the cursor
  (`:3021-3022`), the FPS overlay (`:2556`), extraBitmap (`:3183`). Its purpose
  is to restore the room BACKGROUND under last frame's sprites:
  `draw_room_background()` -> `update_room_invreg_and_reset()`
  (`ac/draw.cpp:2478-2484`, `ac/draw_software.cpp:505-512`) memcpy's bg spans
  (`:428-439`) then `Reset()`s. Black areas outside the room viewport use
  `BlackRects` (`:173`, `:497-503`).
- **Coordinate space:** camera-surface coords, 0,0..camera size
  (`ac/draw_software.cpp:53-55`); screen->surface via `Screen2DirtySurf`
  (`:359-363`), room->surface by subtracting the camera offset (`:366-371`);
  `GlobalOffs` for non-room items (`:376-384`). Per-row span lists, max 4 spans
  per row (`MAX_SPANS_PER_ROW`, `:51`), plus a region COUNT.
- **Whole-screen is forced when:** more than 25 invalidations in one frame
  (`MAXDIRTYREGIONS 25`, `:49`, `:263-266` -- a TODO says pick by resolution;
  a busy AGS Quest room may hit this every frame -- unmeasured); camera moved,
  i.e. any scrolling room (`:232-239`); `invalidate_screen()` callers: full
  redraw / screen tint / shake (`ac/draw.cpp:2953-2954`), raw DrawingSurface
  release (`ac/global_drawingsurface.cpp:59..300`), GUI transparency
  (`ac/gui.cpp:717`), dialog options (`ac/dialog.cpp:1615`), hi-colour fade end
  (`ac/screen.cpp:275`), crossfade/dissolve (`:469,:546,:601`), viewport
  changes (`ac/draw.cpp:1047,1095`), engine init (`main/engine.cpp:1565`).
- **Consequence for Present():** pixels that can differ between presented
  frame N-1 and N lie inside D(N-1) U D(N): D(N-1) is restored to background at
  the start of frame N (then Reset), D(N) is where sprites were drawn in N.
  That union is a correct SUPERSET of the change, and on a screen with a
  full-screen GUI it is simply "everything". It is not a "did anything change"
  test -- a static screen with sprites on it is dirty every frame.

## 2. Design: changed rects out to Present()

**Capture (engine side, `ac/draw_software.cpp`):** keep a per-game-row extent
accumulator `PresentDirty[y] = {minx,maxx}` in GAME-SCREEN coords plus a
`whole` flag. (a) In `update_room_invreg_and_reset()` / `update_black_invreg_
and_reset()`, BEFORE `Reset()`, fold the outgoing spans in (room rects need
`Viewport.Left/Top` added, and `Room2Screen.ScaleRange` if a room viewport is
scaled; `WHOLESCREENDIRTY` -> `whole`). (b) At present time, fold in the spans
currently held (D(N), not reset). (c) Clear the accumulator after a real
present. Expose `get_present_dirty(rows, &whole)`.

**Only the per-tick path may use it.** `render_to_screen()` has other call
sites (fades, video, `global_screen.cpp`, `main/engine.cpp` -- already noted at
`ac/draw.cpp:3189-3199`). Those write the back buffer outside the sprite list
(e.g. hi-colour fade `Fill`+`TransBlendBlt`, `ac/screen.cpp:287-290`; the
no-room `Fill(0)`, `ac/draw.cpp:2975`). Pass a flag from `render_graphics()`;
every other caller presents the full frame.

**Present side (`gfx/ali3dsw.cpp:961`):** group consecutive dirty rows into
bands (cap ~16 rects, else full), then per presentation shape:
- 1:1 / Mode 13h: rect = band as is.
- centered-unscaled: rect = band + (offx, offy); margins cleared ONCE at
  mode-set / on geometry change, not by the per-present
  `SDL_FillSurfaceRect` at `:1097-1098` (that fill is the ~15 ms AGS Quest
  letterbox cost).
- 2x scaled: run the existing row loop of `TryFastIntegerNearestBlit` only for
  source rows in the band; window rect = {0, 2*y0, win_w, 2*(y1-y0+1)}.
  Prefer full-width bands over exact x extents at first (one memcpy per band).
- **PRECONDITION -- the backend path must honour the rect list, and dosags's
  current one does NOT.** In `vendor/SDL/src/video/dos/SDL_dosframebuffer.c`
  the per-rect copy exists only inside the direct-framebuffer block
  (`if (fb_state.direct_fb ...)`, `:1898`; LFB per-rect `:2075-2124`, bulk row
  copy `:2109-2115`, full-window test `:510-516`) and on the banked path
  (`:2030-2070`, and the normal banked path from `:2628`). The NORMAL LFB path
  -- what TNP81A's log shows dosags on (`use_lfb=1 banked=0 hint_direct_fb=0`)
  -- never reads `rects`/`numrects`: it memcpy's or blits the WHOLE surface
  (`:2827-2846`) and may page-flip (`:2861-2903`), which a partial update would
  break anyway. The hub's `docs/video.md` records the same finding. So dirty
  bands need `SDL_HINT_DOS_ALLOW_DIRECT_FRAMEBUFFER=1` (+ `SDL_HINT_DOS_PREFER_LFB=1`,
  doskutsu's configuration; this is P2.3) FIRST; otherwise they save only the
  blit half of a present, never the push.
- Call `SDL_UpdateWindowSurfaceRects(window, rects, n)` instead of
  `SDL_UpdateWindowSurface()` (`vendor/SDL/src/video/SDL_video.c:3760-3788`
  wraps one full rect).

**What invalidates it:**
- 8-bit palette change: no pixel write, whole screen changes colour. It needs
  NO pixel push at all in principle: the backend programs the DAC whenever
  the palette version differs (`SDL_dosframebuffer.c:2623-2625`, `:2710-2716`;
  direct-fb path `:1903-1904`). With the direct-fb path: palette changed + no
  dirty rows -> update with one 1x1 rect = DAC only. On the NORMAL LFB path a
  1x1 rect still pushes the whole surface (see precondition above), so there
  the palette-only case saves the ~34 ms scale blit but not the ~42 ms push.
  Today `palette_changed` defeats patch 0091's skip (`gfx/ali3dsw.cpp:1064`)
  and forces the full blit + push (see section 5).
- Flip (`play.screen_flipped`) and shake (`yoff`): `invalidate_screen()` already
  fires for shake (`ac/draw.cpp:2953`); treat flip != none or a changed
  xoff/yoff as `whole`.
- Hardware cursor: AGS hides SDL's and draws its own sprite (invalidated at
  `ac/draw.cpp:3022`) -- covered.
- Regions > 25 -> whole. Consider raising `MAXDIRTYREGIONS` (trivial).
- **Patch 0091's full-frame compare:** retire it from the hot path once this
  lands (it costs 6.27 ms per render pass), but KEEP it as a verification mode:
  after a partial present, compare the full back buffer with a shadow of what
  was pushed; any difference OUTSIDE the dirty bands is a missed invalidation
  -> count it, log it, fall back to full. Run that mode in the DOSBox-X gate.

## 3. `scene_construct` (~3.26 ms per rendered frame)

The bracket (`ac/draw.cpp:3172-3188`) covers `construct_game_scene()` +
`construct_game_screen_overlay()`. Per frame, even when nothing moved:
`play.UpdateViewports()` (`:2946`); `construct_overlays()` loop (`:2869-2939`);
`draw_preroom_background()`; `prepare_room_sprites()` -> objects, characters,
room overlays, sprite-list sort (`:2373-2427`); **`draw_room_background()` ->
the background-restore memcpy over every span dirtied last frame
(`:2484`; upstream's own comment: "takes up to 50% of the game CPU time at
high resolutions", `:2480-2483`)** -- this pixel work is INSIDE scene_construct,
not inside `render_backbuffer`; `put_sprite_list_on_screen()` (`:2747-2769`);
GUI pass: for each GUI `IsDisplayed/HasChanged` checks, redraw only if changed
(`:2660-2709`), then add to list (`:2713-2737`); cursor (`:3001-3025`).
Which of these owns the 3.26 ms is NOT known -- sub-bracket first
(bg-restore / room sprites / GUI pass / overlays+cursor).

**Cheapest correct "nothing changed" test -- a scene signature.** The scene is
fully determined by what is pushed to the driver. Hash, while pushing:
each `SpriteListEntry` (`ac/draw.cpp:445-460`: DDB pointer, X, Y) plus the
DDB's alpha/stretch/flip, the batch viewports/transforms, `play.bg_frame`,
cursor pos, plus a driver-level **DDB content counter** bumped in
`CreateDDBFromBitmap`/`UpdateDDBFromBitmap`/`DestroyDDB`
(`gfx/ali3dsw.cpp:327-349`) -- needed because a software DDB only WRAPS a Bitmap
pointer (`:327-332`, `ac/draw.cpp:2377`) and GUIs/objects are redrawn in place
into a recycled bitmap, then re-synced via `sync_object_texture` (`:2693`), which
goes through UpdateDDBFromBitmap. If signature(N)==signature(N-1), no
`whole`/invalidate_screen happened, and the palette is unchanged, frame N is
pixel-identical: skip the bg restore, `RenderToBackBuffer()`, the compare AND
the present. This removes patch 0091's 6.27 ms compare from static screens
without any pixel work. The list still has to be built (most of 3.26 ms stays
until sub-brackets say where it goes). Risk: an in-place bitmap mutation that
bypasses UpdateDDBFromBitmap -> stale screen; guard with the same verification
mode as section 2.

## 4. Idle per-tick overhead (after correcting 0a)

- **`rep_exec_wrapper` (3268 ms, 2001 calls):** `GameUpdateEarlyRepExec()` /
  `LateRepExec()` (`main/game_run.cpp:272-308`) -> `run_function_on_non_blocking_
  thread()` (`script/script.cpp:97-119`): `update_script_mouse_coords()` (two
  divisions, `ac/mouse.cpp:447-459`), then per module + global + room
  `DoRunScriptFuncCantBlock()` (`:382-422`), which is SKIPPED once a module is
  known not to have the function (`ModuleHasFunction`, `:384-385,405-409`) -- the
  "cache function-absent" idea is ALREADY upstream here. The 1003 real VM
  calls are `repeatedly_execute_always` bodies; each pays 0b's 1.32 ms clock
  read. Late rep-exec also runs `SyncDrawablesState()` (`game_run.cpp:303`,
  separately bracketed as `drawable_object_states`, 145 ms).
- **`process_events_dispatch` (6033 ms; 3428 without the fade call):**
  `processallevents()` copies the event vector (`ac/event.cpp:349`, 2 small
  PODs per tick) and dispatches: `kTS_Repeat` -> `QueueScriptFunction` ->
  `RunScriptFunctionAuto` -> `RunUnclaimableEvent(REP_EXEC_NAME)` ->
  `RunEventInModules` -> `RunScriptFunction` per module + global
  (`script/script.cpp:534-555`, `:450-513`); and the room Repexec event ->
  `run_room_event`-style dispatch (`ac/event.cpp:212-219,301-308`). Here the
  absent case is NOT cached: `PrepareTextScript()` -> `DoesScriptFunctionExist()`
  -> `GetSymbolAddress()` -> `ScriptSymbolsMap::GetIndexOfAny()`
  (`script/systemimports.cpp:46-116`): a `std::map<String,...>::find`, and on a
  miss of the exact name (exports are stored as `name$argc`) two heap-allocating
  `String` ops (`Left`, `Mid`, `:81-82`) plus a `lower_bound` scan; a successful
  call repeats the lookup in `FindExportedFunction()` (`cc_instance.cpp:356-378`).
  Also per tick: `String` temporaries built from `REP_EXEC_NAME` and the
  `ScriptEventCb[].FnName` C strings (`ac/event.cpp:173`, `script.cpp:334-345`).
  All real but small next to 0b: each successful run pays 1.32 ms of clock.
  Smallest fixes, in order: 0b; then cache per-instance
  `(name -> start_at,argc | absent)` for the ~6 fixed engine callback names;
  measure before doing the second.
- **`input_handling` (1053 ms):** `ags_domouse()` -> `Mouse::Poll()` ->
  `sys_evt_process_pending()` (one of the three event pumps per tick, 81.9 us
  of INT 33h each per the probe = ~0.25 ms/tick for all three),
  `update_gui_disabled_status()`, `update_cursor_over_gui()` (own bracket,
  14 ms), `GameUpdateCheckControlsAndEdges()` (`main/game_run.cpp:1707-1727,
  890-906`). ~0.8 ms/tick is unattributed -> sub-bracket before proposing
  anything. Not found: any allocation or lookup by name on this path.
- **How to confirm before writing fixes:** fix 0a, re-run one Trilby cell:
  `script_vm`/`rep_exec_vm` should come up to ~`process_events_dispatch` /
  `rep_exec_wrapper`. Then 0b alone in one build: per-call `rep_exec_vm` mean
  should fall by ~1.3 ms, `end_of_tick` unaffected.

## 5. Fades: the stall ticks and the ~3.1 s pre-loop

- **AGS already has a palette-only fade for 8-bit.** `ScreenFadeSoftware`
  with `game.color_depth == 1` (`ac/screen.cpp:207-345`): `Begin()` renders the
  scene to the back buffer ONCE (`:247-251`); each step only interpolates the
  palette, `_alpha` 0->64 by `_speed` (`:309-314`), then `Draw()` ->
  `render_to_screen()` (`:292-295`), then `WaitForNextFrame()` (`:115-126`).
  Default speed 5 (`:777-781`, `:812-816`) -> **13 steps**, designed duration
  13 x 25 ms = 325 ms at 40 fps.
- **Why it stalls here:** every step changes the palette, so
  `SyncPaletteIfNeeded()` returns true (`gfx/ali3dsw.cpp:680-701`), which
  defeats patch 0091's skip (`:1064`) and forces a FULL scale-blit + full
  window push (~34 + ~42 ms) plus the backend's `WaitForVBlank()`
  (`SDL_dosframebuffer.c:2710-2712`) for a frame whose PIXELS did not change.
  13 x ~80-90 ms ~= 1.0-1.2 s -- consistent with stall tick 1 (1132 ms).
  Fix = the palette-only present of section 2: skip the blit when only the
  palette changed (~34 ms/step on any path), and with the direct-fb path also
  skip the push (1x1 rect) -> back to ~the designed 325 ms floor. The 734 ms tick is not identified from source -- likely a
  script-driven fade or a second transition; check the stall list after the fix.
- **Pre-loop after `set_runtime_start()`** (`main/game_start.cpp:67-98`):
  `game_start` script; `SetRestartPoint()` for pre-3.6.1 games (`:83-84` ->
  `SaveGameSlot2`, `ac/global_game.cpp:534-537` -- a save written to disk;
  cost NOT measured, bracket it); `current_fade_out_effect()` on the
  PLACEHOLDER room (`:88-90`) -- another 13 full presents (~1 s) to fade out a
  screen that shows nothing; then `load_new_room()`. Cheap wins: palette-only
  present (automatic), or skip the fade-out when `displayed_room < 0` and
  nothing has been shown (upstream behaviour change -- guard `__DJGPP__`,
  operator decision).
- **Hi-colour fade (AGS Quest, 16-bit):** `_speed *= 4` (`:233`) -> alpha
  0->255 by 20 = 13 steps, each a full-screen `Fill` + software
  `TransBlendBlt` + full present (`:285-291`), both in and out of every room.
  No palette trick exists at 16-bit. Options (operator decision, it changes how
  the game looks): cap the step count on the 486 tier, or map Fade to
  Instant via a config/hint. Per-step cost is not measured yet.

## 6. Ranked list (savings are estimates from recorded data, not measurements)

| # | Item | Expected recovery | Confidence | Risk |
|---|---|---|---|---|
| 1 | `FastClock` -> uclock clock under DJGPP (0b) | ~2.5 ms/tick (Trilby idle); scales with script calls per tick, so larger for AGS Quest | high (source + probe; call counts from log) | very low, one line |
| 2 | Fix the ms/us unit bug in script.cpp (0a) | none directly -- makes `script_vm`/`rep_exec_vm` true so #1 can be verified and P1 item 3 re-scoped | certain | none |
| 3 | Palette-only present on 8-bit palette change | skip-blit alone: ~0.45 s per fade on the current LFB path; with the direct-fb path also skip the push: ~0.7-0.8 s per fade (stall 1132 -> ~330 ms) and ~0.7 s of the 3.1 s pre-loop | medium-high (step count from source; per-step cost inferred) | low-moderate: DAC-only update must be verified on the direct-fb and banked paths |
| 4 | Scene-signature skip (section 3) | ~6.5-8 ms per render pass on a static screen (compare 6.27 + render 0.35 + bg restore); ~5.5-6.5 s/1000 ticks | medium | moderate: missed invalidation = stale screen; needs verify mode |
| 5 | Dirty-band present (section 2) -- REQUIRES the direct-fb backend path (P2.3) first | moving content: ~76 ms full present -> roughly proportional to changed rows (a walking character ~10-25% of rows); on the current normal LFB path only the blit half shrinks | medium; zero gain where a full-screen GUI or >25 regions force `whole` | moderate; per-tick path only; direct-fb path has no vsync (tearing accepted per `docs/video.md`) |
| 6 | Skip placeholder-room fade-out / bracket `SetRestartPoint()` | up to ~1 s + unknown save cost of the pre-loop | medium | low; behaviour change, operator call |
| 7 | Hi-colour fade step cap / instant (AGS Quest) | most of the 58% of loop time in its 16 stall ticks | medium (per-step cost unmeasured) | changes the game's look -- operator call |
| 8 | Raise `MAXDIRTYREGIONS`; clear letterbox margins once | avoids whole-screen fallbacks; ~15 ms/present on AGS Quest | medium | low |
| 9 | Sub-bracket `scene_construct` and `input_handling` | none directly; 3.26 ms/frame and ~0.8 ms/tick are unattributed | -- | none |
| 10 | Cache engine-callback symbol lookups per instance | small (tens of us per lookup, a few per tick) -- measure after #1 | low-medium | low |

Out of scope, noticed in passing: patch 0096's comment in `util/time_util.h`
says calendar-time users are on FastClock; no such user exists in the tree.
