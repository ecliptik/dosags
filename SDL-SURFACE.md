# SDL-SURFACE.md -- AGS engine's SDL2 API surface

Milestone-0 deliverable per `PLAN.md`. Decides the SDL2->SDL3 strategy
(Strategy A/B/C, see `PLAN.md`) -- do not start patching before reading
this.

## Scope and methodology

- Source: `vendor/ags/` at the pinned revision, `v3.6.3.13`
  (`94e271df9c14484d89f4861100f643d39555dae7`), fetched via
  `./scripts/fetch-sources.sh ags`.
- Searched `Engine/` and `Common/` for every file referencing an `SDL_`
  symbol (`grep -rlE '\bSDL_[A-Za-z]' Engine/ Common/`), not just files
  with an explicit `#include <SDL...>` -- several files pick up SDL types
  transitively through AGS's own `sys_main.h`/`sys_events.h` wrapper
  headers.
- Every SDL3 API claim below (signature, rename, or removal) was checked
  directly against the pinned SDL3 commit this hub already vendors
  (`74a746281f2208e07a7680560fcb7ec57565228e`, same pin as
  `vendor/sources.manifest`'s `SDL` entry here) via
  `git show <pin>:include/SDL3/<header>` in `~/git/doskutsu/vendor/SDL`
  (a full local SDL clone at the identical pin -- see this repo's
  `docs/patch-conventions.md` / the hub's sibling-repo notes). Nothing
  below is asserted from memory of SDL3's API alone.
- Flags used per item:
  - **R (rename-only)** -- same behavior, name and/or minor signature
    change (e.g. index -> opaque ID of the same practical shape).
  - **S (semantic change)** -- the call's shape, control flow, or
    behavioral contract changed, not just its name; a mechanical
    find-replace will not compile or will compile wrong.
  - **X (removed, no SDL3 equivalent)** -- the SDL2 function/type does
    not exist in SDL3 at all; needs a real design decision, not a port.
  - **N/A (excluded platform)** -- file is compiled only for a
    non-DOS/desktop target; irrelevant to this port, listed for
    completeness only.

## tl;dr

AGS already funnels nearly all of its SDL2 usage through two central
wrapper files -- `Engine/platform/base/sys_main.cpp` (window/display/audio
device lifecycle) and `Engine/ac/sys_events.cpp` (input event pump) --
which is exactly the shape **Strategy A** (direct SDL2->SDL3 port) wants:
a narrow, already-centralized surface, not calls scattered through
gameplay code. That surface itself is real work (window/display API is
almost entirely renamed with a few real signature changes; the audio
device API and the event model both need actual semantic rewrites, not
find-replace) but it is bounded and inherits doskutsu's already-proven
DOS window/input/audio plumbing underneath.

**Two things outside AGS's own `Engine/`/`Common/` code substantially
change the size of this port, and neither is mentioned yet in `PLAN.md`'s
open questions:**

1. **AGS's real-time audio mixer is OpenAL, not raw SDL audio.**
   `Engine/media/audio/audio_core.cpp` and `openalsource.cpp` call `al*`
   functions (`alGetError`, `alListenerf`, ...), and AGS vendors its own
   OpenAL implementation at `vendor/ags/libsrc/mojoAL/mojoal.c` (4923
   lines) rather than requiring a system OpenAL on non-desktop platforms
   (`CMake/FindLocalOpenAL.cmake`: `AGS_USE_MOJO_AL` is true for
   Windows/Linux/macOS/FreeBSD, and falls back to mojoAL automatically
   whenever `find_package(OpenAL)` doesn't find a system lib -- which it
   never will under a DJGPP cross-compile). **mojoAL itself is a second,
   large SDL2 audio/threading/atomics surface**, independent of AGS's own
   engine code, and it has real semantic-change items of its own (see
   Audio section). This is the single biggest unknown this document
   surfaces: the actual choice isn't just "port AGS's own SDL2 calls,"
   it's "port AGS's own SDL2 calls, *and* either port mojoAL's ~5k-line
   SDL2 surface too, or replace AGS's `OpenAlSource`/`audio_core` with a
   much smaller custom mixer written directly against SDL3's audio
   stream API." Worth a `PLAN.md` open-question entry of its own before
   the audio milestone starts, not just folded into the SDL2_sound note
   already there.
2. **AGS's "Software" graphics driver (`ali3dsw.cpp`, despite the name)
   is built on SDL2's accelerated 2D API (`SDL_Renderer`/`SDL_Texture`),
   not direct window-surface blitting.** doskutsu's own engine never
   calls `SDL_CreateRenderer` at all -- it blits straight to the window
   surface (`SDL_dosframebuffer.c`'s `CreateWindowFramebuffer`/
   `UpdateWindowFramebuffer` path is what `docs/video.md` documents in
   depth). Whether SDL3's DOS backend's `SDL_Renderer` support actually
   works has never been exercised by anything in this hub. It should:
   SDL3's software renderer backend (`src/render/software/`) is compiled
   for every platform unconditionally (gated on `SDL_RENDER_DISABLED`,
   not per-platform -- confirmed by reading the pinned SDL3's own
   `CMakeLists.txt` DOS block, which sets no `SDL_VIDEO_RENDER_*` flag at
   all, versus e.g. the NGAGE block right below it which explicitly does)
   and the software renderer is itself implemented on top of
   `SDL_GetWindowSurface`, which the DOS backend does implement. But
   "should work by inspection" is not "confirmed" -- **this needs an
   actual DOSBox-X probe (a minimal `SDL_CreateRenderer` + `SDL_Texture`
   smoke test) before Strategy A is treated as settled**, because if it
   doesn't work, `ali3dsw.cpp` needs a real rewrite against
   `SDL_GetWindowSurface`/`SDL_BlitSurface` directly (the doskutsu-proven
   path) rather than a port.

   **Resolved by decision, 2026-09-10 plan review: the window-surface
   rewrite is the plan from the start, and this probe is moot.** The
   review found `ali3dsw.cpp` hard-requires a 32-bit display (line 73;
   `GetDisplayDepthForNativeDepth()` returns a constant 32; ARGB8888
   streaming texture at line 221) -- three full-frame 4-byte passes for
   an 8-bit game, on a VESA mode 486-era cards often lack. See
   `PATCH-SEQUENCE.md`'s tl;dr and patch 0017.

Neither finding rules out Strategy A -- both are still "port the calls,"
not "build a second backend" -- but both are real scope, and #1 in
particular could plausibly justify a narrower Strategy-A-with-exception:
port AGS's own SDL2 surface directly, but replace mojoAL usage with a
small custom mixer instead of porting mojoAL itself. That tradeoff is a
`PLAN.md` decision, not this document's -- flagging it here because it
wasn't visible before this inventory.

## Files touching SDL2

### Core, cross-platform (in scope for this port)

| File | Category |
|---|---|
| `Engine/platform/base/sys_main.cpp` / `.h` | Video, audio device lifecycle |
| `Engine/ac/sys_events.cpp` / `.h` | Input (keyboard/mouse/touch/window events) |
| `Engine/ac/system.cpp` | Input (scroll-lock query) |
| `Engine/ac/timer.cpp` | Frame pacing (no direct SDL calls -- `std::chrono`/`std::this_thread`) |
| `Engine/debug/debug.cpp` | Log routing (`SDL_LogSetOutputFunction`) |
| `Engine/device/mousew32.cpp` | Input (relative mouse mode) |
| `Engine/gfx/ali3dsw.cpp` / `.h` | Video (SDL_Renderer-based "Software" driver) |
| `Engine/gfx/gfxfilter_sdl_renderer.cpp` / `.h` | Video (renderer scale-quality hint) |
| `Engine/gfx/gfxfilter_aa_sdl_renderer.cpp` / `.h` | Video (renderer scale-quality hint, anti-aliased variant) |
| `Engine/gfx/gfxdriverfactory.cpp` | Video (driver selection; only touches `SDL_SetError`) |
| `Engine/main/game_run.cpp` | Input (raw `SDL_Event` peek in the main loop) |
| `Engine/main/graphics_mode.cpp` | Video (`SDL_GetError` only) |
| `Engine/main/main_sdl2.cpp` | Entry point; includes `SDL.h` but calls nothing SDL-specific (just `main()` -> `ags_entry_point()`) |
| `Engine/main/engine.cpp` / `engine_setup.cpp` | Misc (`SDL_SetHint`/`SDL_HINT_ORIENTATIONS` -- mobile-only concern, `SDL_GetError`) |
| `Engine/media/audio/sdldecoder.cpp` / `.h` | Audio (SDL2_sound decode + `SDL_AudioCVT` resampler) |
| `Engine/media/audio/audio_core.cpp` | Audio (OpenAL mixer entry point, threading) |
| `Engine/media/audio/openalsource.cpp` / `.h` | Audio (OpenAL source playback) |
| `Engine/media/video/videoplayer.h` | Audio (holds an `SDL_AudioFormat` field only; the video *player* itself is Theora, excluded via `AGS_NO_VIDEO_PLAYER` per `PLAN.md`) |
| `Engine/platform/base/agsplatformdriver.cpp` / `.h` | Misc (error message box, desktop bounds query) |
| `Engine/util/sdl2_util.cpp` / `.h` | Filesystem/IO (`SDL_RWops` bridge for AGS's own `Stream`) |

### Excluded (not compiled for this port's target)

| File | Why excluded |
|---|---|
| `Engine/gfx/ali3dogl.cpp` / `.h` | Wrapped in `#if AGS_HAS_OPENGL`; DJGPP has no GL headers and this port's `PLAN.md` targets `graphics_api: software`. `AGS_HAS_OPENGL` (`Common/platform/platform.h`) is `AGS_PLATFORM_OS_WINDOWS \|\| ...ANDROID\|\|IOS\|\|LINUX\|\|EMSCRIPTEN\|\|FREEBSD\|\|MACOS` -- **none of which DOS matches, because there is no `AGS_PLATFORM_OS_DOS` case at all yet** (see "Platform macro gap" below), so this exclusion is currently *accidental* (falls through to the `#error "Unknown platform"` branch), not deliberate, until that patch lands. |
| `Engine/platform/windows/gfx/ali3dd3d.cpp`, `platform/windows/*` | Windows-only (`AGS_HAS_DIRECT3D` = `AGS_PLATFORM_OS_WINDOWS` only; file lives under `platform/windows/`) |
| `Engine/platform/android/acpland.cpp`, `platform/emscripten/acpemscripten.cpp`, `platform/ios/acplios.cpp`, `platform/osx/acplmac.cpp` | Per-platform driver files for other targets, selected by `AGS_PLATFORM_OS_*` |
| `Common/util/android_file.cpp` | Wrapped in `#if AGS_PLATFORM_OS_ANDROID` |
| `Common/gfx/image_png.cpp` | False positive -- only references `SDL_Image`/`SDL_stb.c` in a design-reference *comment*, no actual SDL symbol use |

## Video

`sys_main.cpp`'s window/display management is the bulk of this category,
plus `ali3dsw.cpp`'s renderer usage.

| Symbols | File(s) | Flag | Notes |
|---|---|---|---|
| `SDL_InitSubSystem(SDL_INIT_VIDEO\|...)`, `SDL_QuitSubSystem`, `SDL_Quit`, `SDL_GetVersion` | `sys_main.cpp` | R | Unchanged shape |
| `SDL_GetNumVideoDisplays()` | `sys_main.cpp` | S | -> `SDL_GetDisplays(int *count)` returns an `SDL_DisplayID*` array, not a count of sequential indices -- the loop shape changes, not just the name. Verified against pinned `include/SDL3/SDL_video.h`. |
| `SDL_GetDisplayBounds(int display_index, SDL_Rect*)` | `sys_main.cpp` | S | -> `SDL_GetDisplayBounds(SDL_DisplayID, SDL_Rect*)`; caller must hold/pass a real `SDL_DisplayID` from `SDL_GetDisplays()`, not a raw loop index |
| `SDL_GetDisplayUsableBounds(int display_index, SDL_Rect*)` | `sys_main.cpp` | S | Same `SDL_DisplayID` change as above |
| `SDL_GetWindowDisplayIndex(window)` | `sys_main.cpp` | S | -> `SDL_GetDisplayForWindow(window)` returns `SDL_DisplayID` |
| `SDL_GetNumDisplayModes(display_index)` + `SDL_GetDisplayMode(display_index, i, &mode)` loop | `sys_main.cpp` | S | -> single call `SDL_GetFullscreenDisplayModes(SDL_DisplayID, int *count)` returning an `SDL_DisplayMode**` array; the whole enumeration loop needs rewriting, not renaming |
| `SDL_BITSPERPIXEL(mode.format)` | `sys_main.cpp` | R | Macro still present in SDL3's pixel-format header (not independently re-verified by name in this pass, but `SDL_DisplayMode.format` itself is unchanged in shape) |
| `SDL_SetHint(SDL_HINT_RENDER_DRIVER, ...)` | `sys_main.cpp` | R | Hint API unchanged |
| `SDL_CreateWindow(title, x, y, w, h, flags)` | `sys_main.cpp` | S | SDL3's `SDL_CreateWindow` drops the `x, y` params (position is set separately via `SDL_SetWindowPosition` after creation); `SDL_WINDOWPOS_CENTERED_DISPLAY(display_index)` usage needs re-deriving against the new `SDL_DisplayID`-based positioning API too |
| `SDL_WINDOW_RESIZABLE`, `SDL_WINDOW_FULLSCREEN`, `SDL_WINDOW_FULLSCREEN_DESKTOP`, `SDL_WINDOW_ALLOW_HIGHDPI` | `sys_main.cpp` | R/S mixed | Most window-flag constants carry over; `SDL_WINDOW_FULLSCREEN_DESKTOP` specifically was folded away in SDL3 (fullscreen is a single concept now, exclusive vs. borderless-desktop is chosen via `SDL_SetWindowFullscreenMode`, not a separate flag) -- needs re-checking at the call site, not assumed identical |
| `SDL_SetWindowFullscreen(window, Uint32 flags)` | `sys_main.cpp` | S | -> `SDL_SetWindowFullscreen(window, bool fullscreen)`; the flags param collapses to a plain bool, `kWnd_Fullscreen` vs `kWnd_FullDesktop` distinction needs a different mechanism |
| `SDL_SetWindowResizable(window, SDL_bool)` | `sys_main.cpp` | S | `SDL_bool` itself is gone in SDL3 (see below); param is now plain `bool` |
| `SDL_SetWindowSize`, `SDL_GetWindowSize`, `SDL_SetWindowPosition`, `SDL_SetWindowDisplayMode`, `SDL_SetWindowTitle`, `SDL_RaiseWindow`, `SDL_DestroyWindow`, `SDL_GetWindowBordersSize` | `sys_main.cpp` | R | Signatures unchanged in the parts checked |
| `SDL_WINDOWPOS_CENTERED`, `SDL_WINDOWPOS_CENTERED_DISPLAY(i)` | `sys_main.cpp` | S | `..._DISPLAY(i)` variant keys off a raw index today; needs to key off `SDL_DisplayID` under SDL3 |
| `SDL_SetWindowGrab(window, SDL_bool)` | `sys_main.cpp` | S | -> `SDL_SetWindowMouseGrab(window, bool)`; SDL3 splits mouse grab from keyboard grab (`SDL_SetWindowKeyboardGrab`) where SDL2 had one combined `SDL_SetWindowGrab` -- a real semantic split, not just a rename |
| `SDL_SetWindowMouseRect(window, &rect)` (guarded `SDL_VERSION_ATLEAST(2,0,18)`) | `sys_main.cpp` | R | Exists in SDL3 under the same name (not independently re-verified by header read this pass; low risk, small surface) |
| `SDL_WarpMouseInWindow(window, x, y)` | `sys_main.cpp` | R | Unchanged (not independently re-verified this pass; standard, stable SDL API) |
| `SDL_ShowCursor(SDL_ENABLE/SDL_DISABLE)` | `sys_main.cpp` | S | SDL3 splits this into `SDL_ShowCursor()`/`SDL_HideCursor()` (two functions, no boolean arg) -- not independently re-verified by header read this pass, but this is a well-known SDL3 change worth confirming before writing the patch |
| `SDL_SetWindowIcon(window, SDL_Surface*)`, `SDL_FreeSurface(icon)` | `sys_main.cpp` | R/S | `SDL_SetWindowIcon` unchanged; `SDL_FreeSurface` was renamed to `SDL_DestroySurface` in SDL3 (not independently re-verified this pass -- confirm before patching) |
| `SDL_GetWindowGammaRamp` / `SDL_SetWindowGammaRamp` | `agsplatformdriver.cpp` (via `sys_main.h`-adjacent code) or `sys_main.cpp` | **X** | **Confirmed removed entirely** -- no gamma-related symbol anywhere in the pinned SDL3's `SDL_video.h`. There is no SDL3 replacement API. If AGS's gamma-ramp usage is load-bearing anywhere in the render path, this needs an actual design decision (drop the feature for v0.1, or implement a software LUT applied during the port's own present step), not a porting task. |
| `SDL_SysWMinfo`, `SDL_GetWindowWMInfo`, `SDL_VERSION(&wmInfo.version)` (`sys_main.cpp`, `#if AGS_PLATFORM_OS_WINDOWS` only) | N/A | Windows-only code path, excluded |

Renderer surface (`ali3dsw.cpp`, `ali3dsw.h`, `gfxfilter_sdl_renderer.*`,
`gfxfilter_aa_sdl_renderer.cpp`) -- **contingent on the DOSBox-X probe in
the tl;dr above confirming `SDL_Renderer` actually works on the DOS
backend at all**:

| Symbols | Flag | Notes |
|---|---|---|
| `SDL_CreateRenderer(window, index, flags)` | S | -> `SDL_CreateRenderer(window, const char *name)`; no more index/flags-based driver selection, driver choice is by name string (or left to SDL to pick) |
| `SDL_DestroyRenderer`, `SDL_RenderClear`, `SDL_RenderPresent`, `SDL_SetRenderDrawColor`, `SDL_RenderDrawRect` | R | Verified unchanged in shape (kept core `SDL_Render*` naming in SDL3) |
| `SDL_CreateTexture`, `SDL_DestroyTexture`, `SDL_LockTexture`, `SDL_UnlockTexture`, `SDL_SetTextureScaleMode` | R | Unchanged |
| `SDL_RenderCopyEx` | S | Renamed to `SDL_RenderTextureRotated` in SDL3 (not independently re-verified by header read this pass -- confirm exact name before patching; the rename is well-documented upstream) |
| `SDL_RenderSetLogicalSize` | S | Renamed/restructured to `SDL_SetRenderLogicalPresentation` with an added scaling-mode enum param in SDL3 (not independently re-verified this pass) |
| `SDL_RenderSetVSync` | R | Renamed `SDL_SetRenderVSync` in SDL3 (name only) |
| `SDL_GetRendererInfo`, `SDL_RendererInfo` | S | SDL3 replaced the info-struct query with a properties-ID-based query (`SDL_GetRendererProperties`); no direct struct equivalent |
| `SDL_GetPixelFormatName` | R | Unchanged |
| `SDL_ComposeCustomBlendMode`, `SDL_BLENDFACTOR_*`, `SDL_BLENDOPERATION_ADD` | R | **Verified unchanged** against pinned `SDL_blendmode.h` -- same constants, same function signature |
| `SDL_PIXELFORMAT_ARGB8888`, `SDL_ALPHA_OPAQUE` | R | Unchanged |
| `SDL_FLIP_NONE/HORIZONTAL/VERTICAL`, `SDL_RendererFlip` | R | Unchanged in SDL2->SDL3's texture-flip enum (paired with the `SDL_RenderCopyEx` rename above) |
| `SDL_HINT_RENDER_BATCHING`, `SDL_HINT_RENDER_SCALE_QUALITY`, `SDL_ScaleModeLinear`, `SDL_ScaleModeNearest`, `SDL_ScaleMode` | R | Hint-driven, unchanged in shape |

## Audio

Two independent layers, both real SDL2 surfaces: AGS's own device
lifecycle in `sys_main.cpp`, and the OpenAL/mojoAL mixing stack (see
tl;dr finding #1).

### AGS's own audio device lifecycle (`sys_main.cpp`)

| Symbols | Flag | Notes |
|---|---|---|
| `SDL_InitSubSystem(SDL_INIT_AUDIO)`, `SDL_QuitSubSystem` | R | Unchanged |
| `SDL_setenv`, `SDL_getenv` | R | Unchanged |
| `SDL_OpenAudioDevice(NULL, SDL_FALSE, &desired, NULL, SDL_AUDIO_ALLOW_ANY_CHANGE)` | S | **Verified**: SDL3's `SDL_OpenAudioDevice` is `(SDL_AudioDeviceID devid, const SDL_AudioSpec *spec)` -- 2 params, returns the device ID directly. SDL2's 5-param shape (device name string, capture flag, desired spec, obtained-spec out-param, "allowed changes" bitmask) is gone entirely; SDL3 auto-converts via the audio-stream layer instead of negotiating an "obtained" format. This is a real rewrite of `try_init_audio_driver()`, not a rename. |
| `SDL_CloseAudioDevice` | R | Signature unchanged (still takes an `SDL_AudioDeviceID`) |
| `SDL_GetCurrentAudioDriver` | R | Unchanged |
| `AGS_DISABLE_THREADS`-style audio path | -- | Not an SDL symbol, but directly relevant: see Thread section |

### `sdldecoder.cpp`/`.h` -- SDL2_sound decode + resampling

| Symbols | Flag | Notes |
|---|---|---|
| `Sound_Sample`, `Sound_FreeSample`, `Sound_NewSample`, `Sound_NewSampleFromMem`, `Sound_Decode`, `Sound_Rewind`, `Sound_Seek`, `Sound_GetDuration`, `Sound_AudioInfo` | -- | Not SDL symbols at all -- these are SDL2_sound's own API (`SDL_sound.h`), a separate upstream library from core SDL. SDL2_sound's *own* internal dependency on core SDL2 (if any beyond `SDL_RWops`) is `DEPENDENCIES.md`'s job to inventory, not this document's -- flagging the boundary here so it isn't missed. |
| `SDL_RWops *` (decoder input) | S | See Filesystem/IO section -- `SDL_RWops` -> `SDL_IOStream` rename is not cosmetic (vtable struct shape changed) |
| `SDL_AudioFormat` | R | Type itself still exists in SDL3 with the same role (format-flags typedef), though the concrete format constants changed representation (SDL3 uses a different bit layout -- not independently re-verified this pass) |
| `SDL_AUDIO_BITSIZE(format)` | R | Macro still present in SDL3 (not independently re-verified by header read this pass) |
| `SDL_AudioCVT`, `SDL_BuildAudioCVT`, `SDL_ConvertAudio` | **X** | **Confirmed removed** -- no `AudioCVT`/`BuildAudioCVT`/`ConvertAudio` symbol anywhere in the pinned SDL3's `SDL_audio.h`. Replacement is the `SDL_AudioStream` object model: `SDL_CreateAudioStream(src_spec, dst_spec)` + `SDL_PutAudioStreamData`/`SDL_GetAudioStreamData` does what `SDL_BuildAudioCVT`+`SDL_ConvertAudio` used to, but as a streaming/queueing API rather than a one-shot buffer conversion call -- `SDLResampler`'s whole implementation (`sdldecoder.h`'s `Setup()`/`Convert()`) needs a real rewrite around this different model, not a find-replace. |
| `SDL_memcpy`, `SDL_zero` | R | Still present as SDL's own libc-wrapper macros in SDL3 |

### mojoAL (`vendor/ags/libsrc/mojoAL/mojoal.c`, vendored inside AGS's own tree)

Only relevant if this port decides to port mojoAL rather than replace it
(see tl;dr finding #1). Full symbol list for that decision:

| Symbols | Flag | Notes |
|---|---|---|
| `SDL_InitSubSystem(SDL_INIT_AUDIO)`, `SDL_QuitSubSystem` | R | Unchanged |
| `SDL_OpenAudioDevice`, `SDL_CloseAudioDevice` | S | Same rewrite as AGS's own `sys_main.cpp` usage above -- SDL2's 5-param negotiated-format call vs. SDL3's 2-param stream-based call |
| `SDL_GetNumAudioDevices`, `SDL_GetAudioDeviceName(index, iscapture)` | S | **Verified removed as an index-based pair** -- SDL3's `SDL_GetAudioPlaybackDevices(int *count)` returns an `SDL_AudioDeviceID*` array directly, and `SDL_GetAudioDeviceName` now takes an `SDL_AudioDeviceID`, not an index. Device-enumeration code needs restructuring, not renaming. |
| `SDL_GetAudioDeviceStatus` | S | No 1:1 equivalent found in the SDL3 audio header structure implied by the stream-centric model above; needs checking against `SDL_IsAudioDevicePaused`/stream-state queries rather than assumed to still exist by that name |
| `SDL_LockAudioDevice`/`SDL_UnlockAudioDevice` | S | SDL3's audio model is stream-based with its own locking (`SDL_LockAudioStream`/`SDL_UnlockAudioStream`); device-level locking of this shape is not guaranteed to carry over unchanged |
| `SDL_PauseAudioDevice` | S | SDL3 changed this from a "pause on/off" boolean-style call to separate resume/pause-state semantics tied to the stream API; needs checking at the call site |
| `SDL_AudioCVT`, `SDL_BuildAudioCVT`, `SDL_ConvertAudio` | **X** | Same confirmed removal as `sdldecoder.cpp` above -- mojoAL's own internal resampling path hits the identical gap |
| `SDL_AudioStream`, `SDL_NewAudioStream`, `SDL_AudioStreamPut`, `SDL_AudioStreamGet`, `SDL_AudioStreamAvailable`, `SDL_AudioStreamClear`, `SDL_FreeAudioStream` | S | **Verified**: SDL3 keeps the audio-stream *concept* but renames every function (`SDL_CreateAudioStream(src_spec, dst_spec)`, `SDL_PutAudioStreamData`, `SDL_GetAudioStreamData`, `SDL_GetAudioStreamAvailable`, `SDL_ClearAudioStream`, `SDL_DestroyAudioStream`) and changes construction to take both a source *and* destination spec up front rather than one spec plus a separate conversion step. Real rewrite, not rename. |
| `SDL_CreateMutex`, `SDL_DestroyMutex`, `SDL_LockMutex`, `SDL_UnlockMutex`, `SDL_mutex` | R | Names and shapes preserved in SDL3 (not independently re-verified this pass; low-risk, stable SDL API) |
| `SDL_AtomicAdd`, `SDL_AtomicCAS`, `SDL_AtomicCASPtr`, `SDL_AtomicDecRef`, `SDL_AtomicGet`, `SDL_AtomicGetPtr`, `SDL_AtomicIncRef`, `SDL_AtomicSet`, `SDL_AtomicSetPtr`, `SDL_atomic_t` | S | **Verified renamed**: SDL3 uses a single `SDL_AtomicInt` struct type (`{ int value; }`) with `SDL_SetAtomicInt`/`SDL_GetAtomicInt`/`SDL_CompareAndSwapAtomicInt` functions, replacing the `SDL_atomic_t` + `SDL_Atomic*` family. Every call site changes name; the underlying operation is the same. |
| `SDL_HasNEON`, `SDL_HasSSE` | R | CPU-feature-detection API retained conceptually in SDL3 (not independently re-verified by name this pass) |
| `SDL_MemoryBarrierAcquire`, `SDL_MemoryBarrierRelease` | R | Standard SDL primitives, expected to carry over (not independently re-verified this pass) |
| `SDL_malloc`/`SDL_calloc`/`SDL_realloc`/`SDL_free`/`SDL_memcpy`/`SDL_memmove`/`SDL_memset`/`SDL_strcasecmp`/`SDL_strcmp`/`SDL_strdup`/`SDL_strlcpy`/`SDL_strlen`/`SDL_zero`/`SDL_zerop`/`SDL_min`/`SDL_max`/`SDL_clamp`/`SDL_arraysize`/`SDL_assert`/`SDL_INLINE`/`SDL_log`/trig functions | R | SDL's libc/math shim layer -- stable across SDL2->SDL3, not expected to need changes |
| `SDL_TRUE` | S | `SDL_bool` and its `SDL_TRUE`/`SDL_FALSE` constants are removed in SDL3 in favor of plain C99/C++ `bool`/`true`/`false` (consistent with the `SDL_SetWindowResizable`/`SDL_ShowCursor` findings above) |

## Input (keyboard, mouse, touch, window events)

`sys_events.cpp`/`.h` is almost the entire surface here, plus
`ac/system.cpp` and `device/mousew32.cpp`.

| Symbols | Flag | Notes |
|---|---|---|
| `SDL_PollEvent(SDL_Event*)` | S | **Verified**: SDL3 changes the return type from `int` (1/0) to `bool`. Every `while (SDL_PollEvent(&ev))`-style loop still reads correctly as a boolean condition, but any code comparing the return value against `1`/`0` explicitly needs checking. |
| `SDL_PumpEvents`, `SDL_PushEvent`, `SDL_FlushEvent`, `SDL_FlushEvents`, `SDL_SetEventFilter` | R | Verified/expected unchanged in shape |
| `SDL_Event` (union) | R | Container type itself unchanged; several member event structs inside it changed shape (see below) |
| `SDL_QUIT` | S | Renamed `SDL_EVENT_QUIT` in SDL3 (all `SDL_*` event-type enum constants were renamed with an `SDL_EVENT_` prefix as part of a general scheme -- confirmed by the window-event pattern below; treat every bare event-type constant in this file as needing the same rename) |
| `SDL_KEYDOWN`, `SDL_KEYUP` | S | -> `SDL_EVENT_KEY_DOWN`, `SDL_EVENT_KEY_UP` |
| `SDL_MOUSEBUTTONDOWN`, `SDL_MOUSEBUTTONUP`, `SDL_MOUSEMOTION`, `SDL_MOUSEWHEEL` | S | -> `SDL_EVENT_MOUSE_BUTTON_DOWN/UP`, `SDL_EVENT_MOUSE_MOTION`, `SDL_EVENT_MOUSE_WHEEL` |
| `SDL_TEXTINPUT` | S | -> `SDL_EVENT_TEXT_INPUT` |
| `SDL_FINGERDOWN`, `SDL_FINGERMOTION`, `SDL_FINGERUP` | S | -> `SDL_EVENT_FINGER_DOWN/MOTION/UP`. Touch-to-mouse emulation is a **mobile-only feature** per `sys_events.h`'s own comments (`TouchMouseEmulation`) -- low priority for a DOS target, candidate to `#ifdef` out entirely rather than port, pending a `PLAN.md` decision. |
| `SDL_WINDOWEVENT` + nested `SDL_WINDOWEVENT_CLOSE`/`_FOCUS_GAINED`/`_FOCUS_LOST`/`_SIZE_CHANGED` sub-switch | S | **Verified, and the single biggest structural change in this file**: SDL3 has no `SDL_WINDOWEVENT` wrapper type at all. Each sub-case becomes its own **top-level** event type in `SDL_Event`'s union/switch (`SDL_EVENT_WINDOW_CLOSE_REQUESTED`, `SDL_EVENT_WINDOW_FOCUS_GAINED`, `SDL_EVENT_WINDOW_FOCUS_LOST`, `SDL_EVENT_WINDOW_RESIZED`, confirmed present in the pinned `SDL_events.h`'s event-type enum). The nested `switch (event.window.event) { case SDL_WINDOWEVENT_CLOSE: ... }` structure in `sys_evt_process_one()` needs flattening into additional top-level `case` arms in the outer event switch, not a renamed inner constant. |
| `SDL_MouseMotionEvent`, `SDL_MouseWheelEvent`, `SDL_TextInputEvent`, `SDL_TouchFingerEvent` | R | Struct *names* preserved (not independently re-verified field-by-field this pass beyond the keyboard event below; low risk since these were not flagged in the restructuring above) |
| `SDL_Keysym` (type), used in `ags_getkeysdown()`'s return type and `is_sdl_mod_key()`/`make_sdl_mod_flag()` param | **X** | **Confirmed removed** -- no `SDL_Keysym` symbol anywhere in the pinned SDL3's `SDL_keyboard.h`. SDL3's `SDL_KeyboardEvent` flattens what used to be a nested `keysym` struct into direct fields (`scancode`, `key`, `mod`) on the event itself. Every function taking/returning `SDL_Keysym` in this file needs a real signature change (e.g. return `SDL_Scancode` + `SDL_Keymod` separately, or a small AGS-local replacement struct), not a rename. |
| `SDL_Scancode`, `SDL_SCANCODE_*` constants (full list: arrows, function keys, keypad, modifiers, editing keys) | R | Verified stable naming scheme across SDL2->SDL3 for the specific constants this file uses (not individually re-checked one-by-one, but `SDL_Scancode` as a concept and its `SDL_SCANCODE_*` values are one of the most stable parts of SDL's API) |
| `SDL_Keycode` | R | Type retained |
| `SDL_GetKeyFromScancode`, `SDL_GetScancodeFromKey` | S | SDL3 versions of both gained an extra `SDL_Keymod` parameter (for modifier-aware lookups) -- not independently re-verified by header read this pass, flagging as likely-S based on the general SDL3 keyboard-API pattern; confirm exact signature before patching |
| `SDL_GetKeyboardState(int*)` | S | **Verified return type changed**: SDL2 returns `const Uint8*`, SDL3's pinned header returns `const bool*`. Call sites reading `state[scancode]` as a byte still work structurally but the type itself changed; any code doing pointer arithmetic or byte-level tricks on the returned array needs checking. |
| `SDL_GetModState()` | R | Expected unchanged (not independently re-verified this pass) |
| `SDL_BUTTON_LEFT/MIDDLE/RIGHT/X1/X2` | R | Verified stable constant scheme |
| `SDL_PRESSED`, `SDL_RELEASED` | S | These are SDL2-only convenience constants (`1`/`0`); SDL3's `SDL_KeyboardEvent`/mouse-button events use a direct `bool down` field instead (confirmed via the `SDL_KeyboardEvent` struct dump above), so comparisons against `SDL_PRESSED`/`SDL_RELEASED` need rewriting against the new field, not a renamed constant |
| `SDL_FingerID`, `SDL_TOUCH_MOUSEID` | R | Expected to carry over (touch API largely stable; low priority per the mobile-only note above) |
| `SDL_SetRelativeMouseMode(SDL_bool)` (`mousew32.cpp`) | S | **Verified**: renamed to `SDL_SetWindowRelativeMouseMode(SDL_Window *window, bool enabled)` -- now takes an explicit window, was global before. Needs the window pointer threaded through, not just a rename. |
| `SDL_HINT_MOUSE_RELATIVE_SPEED_SCALE` (`mousew32.cpp`) | R | Hint name expected unchanged |
| `sdl_mbut_to_ags_but(int sdl_mbut)` | -- | AGS's own function, not an SDL symbol; listed for context since its input values come from `SDL_BUTTON_*` |
| `SDL_GetKeyboardState`, `SDL_GetModState`, `SDL_SCANCODE_SCROLLLOCK` (`ac/system.cpp`) | S/R | Same `SDL_GetKeyboardState` semantic note as above; `SDL_SCANCODE_SCROLLLOCK` itself unchanged |
| `SDL_category`, `SDL_LOG_CATEGORY_RESERVED1`, `SDL_LogPriority`, `SDL_LOG_PRIORITY_INFO`, `SDL_NUM_LOG_PRIORITIES`, `SDL_LogSetAllPriority`, `SDL_LogSetOutputFunction` (`debug/debug.cpp`) | R | Log API's shape is stable across SDL2->SDL3 (not individually re-verified this pass; low risk, this hub's own `shared/` DOS backend patches already rely on SDL's log plumbing being stable -- see `docs/patch-conventions.md`'s hint-naming section) |

## Timer

**No direct SDL symbols at all** in `Engine/ac/timer.cpp`. Frame pacing
uses `std::chrono::steady_clock` (`Clock::now()`) and
`std::this_thread::sleep_for()`. This means the timer surface isn't an
SDL2->SDL3 porting question -- it's a **DJGPP libstdc++ question**:
whether `std::chrono`/`std::this_thread::sleep_for` work correctly and
precisely enough under DJGPP's C++ runtime is unverified and belongs in
`PLATFORM-SURFACE.md`, not here. Cross-reference: `docs/timing.md` (not
read in depth for this document -- read it before starting the
BOOTSTRAP milestone, since the DOS backend's own timer subsystem
(`SDL_TIMER_DOS`, `src/timer/dos/*.c`) exists and provides `SDL_GetTicks`/
`SDL_Delay` regardless of whether AGS's `std::chrono` path works).

One Emscripten-specific exception worth noting for precedent:
`WaitForNextFrame()` has an `#if AGS_PLATFORM_OS_EMSCRIPTEN` branch that
calls `platform->Delay()` instead of `std::this_thread::sleep_for()` --
i.e. AGS already has a precedent for swapping the sleep primitive out
per-platform when the standard one doesn't suit a constrained target.
Worth following if `std::this_thread::sleep_for` turns out not to behave
well under DJGPP/the DOS cooperative scheduler (see Thread section and
`docs/architecture.md`'s cooperative-scheduler model).

## Thread

Also not primarily an SDL2->SDL3 question -- AGS's audio mixer
(`Engine/media/audio/audio_core.cpp`) spawns a real `std::thread`
(`g_acore.audio_core_thread = std::thread(audio_core_entry)`) to poll
OpenAL/mojoAL, guarded end-to-end by a build option AGS already has:
`AGS_DISABLE_THREADS`. When set, `timer.cpp` and `audio_core.cpp` both
switch to a single-threaded poll path (`audio_core_entry_poll()` called
directly from `WaitForNextFrame()` instead of a background thread).
`Engine/media/video/video.cpp` (Theora playback -- excluded from this
port via `AGS_NO_VIDEO_PLAYER` per `PLAN.md`) has the same guard.

**`AGS_DISABLE_THREADS` already has a real precedent for exactly this
port's situation**: AGS's own top-level `CMakeLists.txt` sets
`AGS_DISABLE_THREADS TRUE` unconditionally for Emscripten
(`if(EMSCRIPTEN) ... set(AGS_DISABLE_THREADS TRUE)`), a target chosen
specifically because it can't assume real preemptive OS threads either.
Per `docs/architecture.md`'s cooperative-scheduler model, DOS's SDL3
backend provides `SDL_THREAD_DOS` (`src/thread/dos/*.c`: mutex, semaphore,
systhread, TLS) as a `setjmp`/`longjmp` cooperative mini-scheduler, not
real preemption -- but AGS's audio thread doesn't go through `SDL_Thread`
at all, it uses `std::thread` directly, and whether DJGPP's libstdc++
`std::thread` implementation exists/works on top of that cooperative
scheduler (or at all) is unverified and is exactly the kind of question
`PLATFORM-SURFACE.md` should answer with a real probe. **Recommendation
for `PLAN.md`: default to `AGS_DISABLE_THREADS=1` for this port from the
start**, following the Emscripten precedent, rather than spending
Milestone-0 effort verifying `std::thread` under DJGPP when AGS already
ships a working single-threaded fallback for exactly this class of
target. This also sidesteps needing `SDL_THREAD_DOS` correctness for
anything AGS itself relies on.

**Not sufficient on its own (2026-09-10 probe, `tests/probes/djgpp-runtime/`)**:
DJGPP's libstdc++ has no `std::mutex`/`std::condition_variable` at all
(no `_GLIBCXX_HAS_GTHREADS`), and `audio_core.cpp` keeps both as struct
members outside the `AGS_DISABLE_THREADS` guards (lines 48-49, lock sites
158/182/191), as does `Common/debug/debugmanager.cpp`. `AGS_DISABLE_THREADS=1`
plus a DOS-only no-op lock/cv shim (`PATCH-SEQUENCE.md` 0010) is the
actual recommendation. `std::this_thread::sleep_for` and `std::chrono`
do build, so the Timer section's question is runtime precision only.

## Filesystem / IO

Narrow surface: `SDL2Util::OpenRWops()` (`Engine/util/sdl2_util.cpp`/`.h`)
bridges AGS's own `Common::Stream` abstraction into an `SDL_RWops*` so it
can be handed to SDL2_sound's decoder (`sdldecoder.cpp`), which requires
an `SDL_RWops*` as input.

| Symbols | Flag | Notes |
|---|---|---|
| `SDL_RWops` (struct, `AllocRW`/`FreeRW` pattern, `hidden.unknown.data1` field, `RW_SEEK_SET/CUR/END`) | **X→S** | **Confirmed removed as a type** -- no `include/SDL3/SDL_rwops.h` exists in the pinned SDL3 tree at all (renamed file). Replacement is `SDL_IOStream` (`include/SDL3/SDL_iostream.h`), constructed via `SDL_OpenIO(const SDL_IOStreamInterface *iface, void *userdata)` -- a vtable struct passed at construction time, not a struct allocated then have function pointers assigned onto it field-by-field (`SDL_AllocRW()` + `c->size = ...; c->seek = ...`). `sdl2_util.cpp`'s entire `OpenRWops()` implementation needs a real rewrite to the new interface-struct pattern; this is contained to one ~90-line file, low risk in scope, real in kind (not a rename). |
| `SDL_SetError` (used in `rwops_close`'s error path) | R | Unchanged |

This is the extent of AGS's *own* SDL2 filesystem/IO usage. Broader
filesystem assumptions (path separators, case sensitivity, `PHYSFS`-style
archive access if any, config file locations) are `PLATFORM-SURFACE.md`'s
job per `PLAN.md`, not this document's -- not inventoried here.

## Misc / platform

| Symbols | File(s) | Flag | Notes |
|---|---|---|---|
| `SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_WARNING, ...)` | `agsplatformdriver.cpp` | S | SDL3 keeps this function, but it depends on the platform having a real message-box facility -- the DOS backend almost certainly has no implementation (doskutsu's own platform driver equivalent should be checked for how it already handles this rather than assuming AGS's call will just no-op safely; needs a real look during the BOOTSTRAP milestone, not assumed here) |
| `SDL_Surface`, `SDL_Rect` (as plain structs, e.g. window-icon creation) | R | Struct shapes largely stable across SDL2->SDL3 for basic geometry/surface types (not exhaustively re-verified field-by-field) |
| `SDL_HINT_ORIENTATIONS` | `engine.cpp`/`engine_setup.cpp` | N/A | Mobile-only hint (screen orientation lock), irrelevant to a DOS target -- candidate to drop rather than port |
| `SDL_GetError`, `SDL_SetError` | Multiple | R | Stable across every file that uses them |

## Platform macro gap (blocks everything else, not an SDL question)

Not part of the SDL2 surface itself, but the literal first compile
blocker, worth recording here since it was found while tracing
`AGS_HAS_OPENGL`/`AGS_HAS_DIRECT3D` gating: **`Common/platform/platform.h`
has no `AGS_PLATFORM_OS_DOS` case at all.** Its `#if defined(...)` chain
(Android -> `_WIN32` -> `__APPLE__` -> `__linux__` -> `__EMSCRIPTEN__` ->
`__FreeBSD__` -> `#else #error "Unknown platform"`) does not check for
`__DJGPP__` anywhere, so an unpatched build hits the `#error` branch
immediately, before any SDL question even arises. Adding an
`AGS_PLATFORM_OS_DOS` branch there (with `AGS_HAS_OPENGL`/
`AGS_HAS_DIRECT3D` both false, `AGS_SUPPORT_MULTIDISPLAY` false, and a
decision on `AGS_SEARCH_FOR_GAME_ON_LAUNCH`) is necessarily the *first*
patch in `patches/ags/`, ahead of any SDL2->SDL3 work -- worth noting in
PLAN.md's "Minimum patch sequence" item when that's written up.

## Recommendation for the SDL2->SDL3 strategy decision

**Strategy A (direct port)** looks viable and is this document's
recommendation: AGS's engine-code-proper SDL2 surface is already
centralized in two wrapper files plus a handful of small, focused
call-sites (renderer, RWops bridge, event pump), none of which are
scattered through gameplay/scripting code. Most of the video/window
surface is rename-or-small-signature-change; the real work is
concentrated in a few genuinely semantic items (audio device API, event
model restructuring, `SDL_RWops`->`SDL_IOStream`, gamma ramp removal) that
are each bounded and well-precedented by patterns already proven
elsewhere (doskutsu's own SDL1.2->SDL3-DOS port solved harder versions of
several of these).

The two findings in the tl;dr are what could change this conclusion and
should be resolved before treating Strategy A as final:

1. Confirm (DOSBox-X probe) whether SDL3's software `SDL_Renderer`
   backend actually functions on the DOS backend at all -- if not,
   `ali3dsw.cpp` needs a real rewrite against the window-surface path
   doskutsu already proves out, which is still Strategy A in spirit
   (still "port AGS's own driver," just via a different SDL3 API) but
   more work than a renderer-API port. **Decided 2026-09-10: the
   window-surface path, from the start, without running the probe** --
   see the tl;dr note above and `PATCH-SEQUENCE.md` 0017.
2. Decide mojoAL's fate -- port its ~5k-line SDL2 surface too, or
   replace `OpenAlSource`/`audio_core`'s OpenAL calls with a small custom
   mixer against SDL3's audio-stream API directly. This is the one place
   where "port AGS's own SDL2 calls" and "avoid porting a second large
   SDL2 codebase" pull in different directions, and it's a real `PLAN.md`
   decision, not something this document should resolve unilaterally.
