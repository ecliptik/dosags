# DEPENDENCIES.md -- external dependency inventory

Milestone-0 deliverable per `PLAN.md`. Covers codecs, archive/data
formats, fonts, networking, and threading (`SDL-SURFACE.md` already
covers AGS's own SDL2 API surface and mojoAL's; this document covers
everything else AGS's build links against).

## Scope and methodology

Source: `vendor/ags/` at the pinned revision (`v3.6.3.13`,
`94e271df9c14484d89f4861100f643d39555dae7`). Every claim below is sourced
from reading the actual pinned `CMakeLists.txt` files and grepping actual
call sites -- not assumed from a library's typical purpose or from AGS's
own class/file naming (which, per the Allegro correction below, misled a
prior research pass on this exact question). Flags reuse `SDL-SURFACE.md`'s
scheme: **R** rename-only/no-op, **S** needs real work, **X** removed/no
equivalent, plus two new ones specific to this document: **Load-bearing**
(compiled and exercised at runtime for a normal game) vs. **Excludable**
(linked today but not actually reachable for a DOS v0.1 profile -- a real
CMake-level exclusion is undone work, not a fact already true).

## tl;dr

AGS's own `Engine`/`Common` code is a much smaller dependency surface
than its `CMakeLists.txt` link list suggests. Several libraries that
appear unconditionally linked today are either not called by DOS-relevant
code paths at all (`tinyxml2`, `libcda`, `Glad`/OpenGL) or are called
only by an already-excluded subsystem (Ogg/Vorbis/Theora's *decode* path
is exclusively `apeg`'s Theora cutscene player, gated by
`AGS_NO_VIDEO_PLAYER` -- AGS's own audio code never touches these codecs
directly, only SDL2_sound does). The CMake build system itself has real,
previously-unknown gaps for a DOS target: three libraries
(`Glad::Glad`, `Cda::Cda`, and the Ogg/Vorbis/Theora `find_package`/Fetch
calls) are wired at **configure or link time unconditionally**,
independent of whether the DOS-relevant code path that would use them is
even compiled in -- each needs its own new CMake guard, not just the
`#if`-guarded source files that already exist.

**One standout, genuinely encouraging find**: `Common/libsrc/alfont-2.0.9/`
(AGS's FreeType wrapper, the load-bearing TTF font path) already has a
dormant `ALFONT_DOS` build path -- 47 `#ifdef ALFONT_DOS` sites gating
Unicode/charset conversion, clearly inherited from when Allegro itself
had a real DJGPP/DOS backend, decades ago. It is defined nowhere in AGS's
current build (dormant, unexercised, not free -- still needs verifying
the branches still compile/behave correctly and that DJGPP's `iconv`
actually works) but it is a real head start on font support that this
port did not have to write from scratch.

**Correction (2026-09-10 plan review) -- the paragraph above has it
backwards.** `alfont.c:20` is `#ifdef ALFONT_DOS` -> `#include <iconv.h>`,
`#else` -> `<locale.h>` + `<wchar.h>`; the `ALFONT_DOS` branches are the
*iconv* implementation of the charset conversion (`README.txt` line 28
credits "the Libiconv project for DOS version"), and DJGPP has no
`<iconv.h>` at all (`tests/probes/djgpp-runtime/`). The default path's
`setlocale`/`mbstowcs`/`wchar_t` facilities *are* present under DJGPP
(same probe). So the dormant DOS path is a dependency on a library we
don't have, not a head start: **do not define `ALFONT_DOS`**, build
alfont exactly as every current AGS platform does. Whether the default
path renders a real game's non-ASCII text correctly is a test-game
question.

**One correction to prior research, found while investigating a second
question** (matching the Allegro correction already recorded in
`PLAN.md`): `LICENSE-REVIEW.md` described the AGSBlend plugin as
"irrelevant unless/until whitelisted." With `AGS_BUILTIN_PLUGINS` default
`ON`, AGSBlend is one of six plugins statically linked into the Engine
binary today, not gated behind any whitelist -- already corrected in
`LICENSE-REVIEW.md` directly.

## Required libraries -- what AGS's own code actually calls

| Library | Vendored at | Called by (DOS-relevant code) | Load-bearing? | License file present? |
|---|---|---|---|---|
| SDL2 (-> SDL3, this port's real work) | fetched, not vendored in AGS's tree | `sys_main.cpp`, `sys_events.cpp`, etc. | Yes | N/A -- covered by this repo's own SDL3 pin |
| SDL2_sound | **not vendored** -- `FetchContent`-pulled from `icculus/SDL_sound` @ `3a41c3de5b90355745333041b96e142ba8f5fbdf` | `sdldecoder.cpp`/`.h` | Yes (all non-OpenAL/mojoAL audio *decode*) | Not checked this pass -- inventory at the pinned SDL_sound commit before vendoring |
| mojoAL (vendored OpenAL) | `vendor/ags/libsrc/mojoAL/mojoal.c` | `audio_core.cpp`, `openalsource.cpp` | Yes (real-time mixing) -- see `SDL-SURFACE.md`'s Audio section, not re-covered here | Present, `.icculus.mojoAL.txt` (seen during earlier `SDL-SURFACE.md` research; not independently re-verified this pass) |
| Ogg | `find_package`/`FetchOgg`, not vendored | `Engine/libsrc/apeg-1.2.1/ogg.c` only (real `ogg_*` calls); SDL2_sound also needs it internally for `.ogg` audio decode, but that's inside SDL2_sound's own build, not AGS's code | Excludable for video (see Audio codec chain below); load-bearing for audio if `.ogg` music/SFX support is wanted | Not checked this pass |
| Vorbis | same as Ogg | same as Ogg (`vorbis_*` calls only in `apeg`) | Same split as Ogg | Not checked this pass |
| Theora | `find_package`/`FetchTheora`, not vendored | `Engine/libsrc/apeg-1.2.1/ogg.c` only | **Excludable** -- `AGS_NO_VIDEO_PLAYER` drops the only real caller from the link (see below for the configure-time gap this doesn't close) | Not checked this pass |
| Allegro 4.4.3 (trimmed, headless subset) | `vendor/ags/libsrc/allegro/` | ~34 files across `Engine`/`Common` include `<allegro.h>`/`<allegro/file.h>`; real link target `Allegro::Allegro` in both `Engine/CMakeLists.txt:546` and `Common/CMakeLists.txt:201` | Yes -- software blit/dither/palette/quantize, FLI/FLC decode, polygon/rotate/flood-fill, fixed-point math, BMP load, Unicode helpers, legacy packfile reader. **No OS-integration subsystems compiled** (no display/audio/input/timer/thread source in `FileList.cmake`) | **Absent** -- see `PLAN.md`'s Open questions correction and `LICENSE-REVIEW.md`'s new Allegro section; unresolved |
| FreeType 2.1.3 | `Common/libsrc/freetype-2.1.3/` | Not called directly by AGS code -- only reached through `alfont` | Yes, transitively (TTF rendering depends on it) | Present -- `docs/FTL.txt`, `docs/license.txt`, plus a module-specific `CatharonLicense.txt` for autohint |
| alfont 2.0.9 | `Common/libsrc/alfont-2.0.9/` | `Common/font/ttffontrenderer.cpp` -- the real TTF rendering path (`alfont_init`, `alfont_load_font_from_mem`, `alfont_textout_aa`, etc., ~15 distinct calls) | **Yes** -- TTF is a common AGS game font format, not safely excludable for a general-purpose engine port | Files present (`ALFONT.txt`, `AUTHORS.txt`, `FTL.txt`, `README.txt`) but not individually read/classified this pass -- `ALFONT.txt` is the likely actual license by filename convention, needs an explicit read before `LICENSE-REVIEW.md` closes this entry |
| aastr 0.1.1 | `Common/libsrc/aastr-0.1.1/` | `Engine/ac/draw.cpp`, `Common/gfx/allegrobitmap.cpp` -- anti-aliased stretch/rotate under the Allegro-bitmap-compat drawing layer | Yes | Present, inline in `aastr.c`/`aastr.h`'s header comment: gift-ware, Copyright 1998-1999 Michael Bukin -- a real license statement, just not a separate file |
| glm | `libsrc/glm/` (header-only) | `Engine/gfx/graphicsdriver.h`'s `RenderMatrixes` struct references `glm::mat4` in the base interface every graphics driver (including the DOS-relevant Software one) compiles against | Headers required at compile time engine-wide; actual transform-math *calls* are GL/D3D-only (`ali3dogl.cpp`, `platform/windows/gfx/ali3dd3d.cpp`), both excluded for DOS -- **keep in the include path, expect zero runtime cost** | Present, `libsrc/glm/copying.txt` |
| tinyxml2 | `libsrc/tinyxml2/` | **Zero usage in `Engine`/`Common`** -- only real caller is `Tools/data/agfreader.cpp` (Editor/data-tool side, `AGS_BUILD_TOOLS`/`AGS_BUILD_COMPILER` both default OFF). Confirmed not in `Engine/CMakeLists.txt`'s `target_link_libraries(engine ...)` list at all | **Fully excludable** for an engine-only DOS build -- not load-bearing | Present, `libsrc/tinyxml2/LICENSE.txt` |
| miniz | `libsrc/miniz/` | `Common/gfx/image_png.cpp` (PNG read/write), `Common/util/deflatestream.cpp`, `Common/util/compress.cpp` -- core data/asset (de)compression, likely load-bearing for game-package/save-data handling (not independently traced further -- a `PLATFORM-SURFACE.md`/filesystem-format question) | Likely yes, not fully traced | Present, inline in `miniz.h`'s header comment: public domain / unlicense, Rich Geldreich |
| stb (image only) | `libsrc/stb/` | Only `stb_image.c`/`.h` vendored (no `stb_truetype`, no `stb_vorbis` -- AGS uses FreeType+alfont and SDL2_sound+Ogg/Vorbis instead). Sole caller `Common/gfx/image_png.cpp` | Yes, for PNG decode/encode | Present, `libsrc/stb/LICENSE` |
| CD audio (`libcda-0.5`) | `Engine/libsrc/libcda-0.5` | `Engine/ac/cdaudio.cpp`/`.h` -- AGS's legacy physical-CD-audio scripting API | **Excludable** -- no CD-ROM audio requirement anywhere in this port's compatibility profile; linked unconditionally into `engine` today alongside Allegro/OpenAL/SDL2_sound, needs its own new CMake guard | Not checked this pass |
| OpenGL loader (Glad) | n/a (build-only) | `Engine/CMakeLists.txt`'s `target_link_libraries(engine PUBLIC ...)` links `Glad::Glad` unconditionally in the non-GLES2 branch, **independent of `AGS_HAS_OPENGL`** -- even once DOS makes `ali3dogl.cpp` compile to an empty translation unit (per `SDL-SURFACE.md`), this CMake line still tries to link Glad | **Excludable, needs a new CMake guard** (`if(AGS_HAS_OPENGL) target_link_libraries(...)`), not just the existing source-level `#if` | N/A |

## Audio codec chain -- two independent layers, confirmed

Corrects/refines `PLAN.md`'s existing Ogg/Vorbis open question with
concrete evidence:

1. **Video-cutscene decode** (`Engine/libsrc/apeg-1.2.1/`, an MPEG-1 +
   Ogg-Theora vendored decoder) is the **only** code in the whole
   `Engine`/`Common` tree that calls real `ogg_*`/`vorbis_*`/`theora_*`
   symbols directly (confirmed via full-tree grep, excluding `apeg`
   itself). `AGS_NO_VIDEO_PLAYER` correctly drops `apeg`'s own linking
   from the `engine` target -- but does **not** touch the top-level
   `find_package(Ogg/Vorbis/Theora REQUIRED)`/`Fetch*` calls in
   `CMakeLists.txt`, which run unconditionally at **configure** time
   regardless of that flag. Practical effect: even with
   `AGS_NO_VIDEO_PLAYER=ON`, CMake configure still fails without working
   Ogg/Vorbis/Theora available, even though nothing ends up linking
   them. Making those three `find_package`/Fetch blocks themselves
   conditional on `AGS_NO_VIDEO_PLAYER` (or a new DOS-specific flag) is
   real, undone patch work -- not something upstream AGS already
   supports.
2. **Audio decode** (`.ogg` music/SFX) goes entirely through SDL2_sound's
   own `Sound_*` abstraction (`sdldecoder.cpp`) -- AGS's own audio code
   (`sound.cpp`, `global_audio.cpp`, `scriptaudioclip.cpp`) only tags and
   dispatches by format (`eAudioFileMP3`, `MUS_OGG`), never calls
   `ov_*`/`vorbis_*` directly. **This means porting SDL2_sound to DJGPP
   is what actually needs libogg/libvorbis for audio support, not AGS's
   own Engine code** -- a materially different scope than "AGS needs
   Ogg/Vorbis," worth carrying into whatever patch-sequence planning
   follows this document.
3. **MP3**: no real MP3 decode implementation exists anywhere in
   `Engine`/`Common` outside `apeg`'s own vendored (and explicitly
   disabled -- `DISABLE_MPEG_AUDIO` set in `apeg`'s `CMakeLists.txt`,
   its audio-decode `.c` files commented out of the source list) copy.
   Every "mp3" reference in `Engine`/`Common` proper is format-tag/
   dispatch/legacy-script-API surface (`PlayMP3File`) delegating actual
   decode to SDL2_sound -- so real MP3 support, if any, depends entirely
   on SDL2_sound's own build configuration, not inventoried here.
4. **MIDI**: AGS explicitly force-enables SDL2_sound's own *software*
   MIDI decoder (`SDLSOUND_DECODER_MIDI`, set via a CACHE variable in
   `CMake/FetchSDL_Sound.cmake`, with a comment citing an upstream
   SDL_sound issue about it not defaulting on). A DOS port almost
   certainly wants **hardware** MIDI passthrough (MPU-401/OPL3/GUS, per
   `.sdl-dos-ports/docs/audio.md`'s established architecture) instead of
   a software MIDI-to-PCM softsynth path -- porting/enabling that
   decoder for DJGPP would likely be wasted effort unless deliberately
   kept as a fallback for games with no other MIDI path. Whether AGS's
   own MIDI playback for in-game music actually routes through
   SDL2_sound's MIDI decoder at all, or through a separate path, was not
   traced this pass -- worth confirming before assuming this decoder can
   simply be turned off.

## Networking -- confirmed absent

Full-tree scan for socket/networking symbols and headers (`socket(`,
`connect(`, `curl`, `<sys/socket.h>`, `winsock`, `wininet`, download/
updater patterns) across `Engine`/`Common` found no real hits. The only
"download" string found is a Windows-only driver-troubleshooting error
message (`Engine/platform/windows/acplwin.cpp`), not an auto-updater.
**Confirms `STATUS.md`'s existing "networking: none" claim.** No further
action needed for this item.

## Threading -- one addition to `SDL-SURFACE.md`'s Thread section

`SDL-SURFACE.md` already covers `audio_core.cpp`'s `std::thread` usage
and recommends defaulting to `AGS_DISABLE_THREADS=1`. A full-engine scan
(not just `media/audio/`) for `std::thread`/`std::mutex`/
`std::condition_variable`/`std::atomic`/`pthread_*`/`SDL_CreateThread`/
`SDL_mutex`/`SDL_cond` found exactly one additional file:
**`Common/debug/debugmanager.cpp`/`.h`** -- the engine-wide logging
dispatcher, which wraps every public method in `std::lock_guard<std::mutex>`
unconditionally (13 lock sites), confirmed compiled with no build-option
gate (`Common/CMakeLists.txt`) and confirmed **not** covered by
`AGS_DISABLE_THREADS` (zero references to that macro in either file).
This is a real gap in "just disable threads and the threading question
goes away": `<mutex>`/`std::mutex` still needs to compile and link under
DJGPP's libstdc++ regardless of `AGS_DISABLE_THREADS`, even though no
`std::thread` is ever spawned by this file. Lower risk than the real
thread-spawning question (an uncontended mutex is functionally inert),
but it is a real, unconditional C++11 threading-primitive dependency,
worth its own explicit DJGPP viability check in whatever probe answers
`SDL-SURFACE.md`'s `std::thread`-under-DJGPP open question -- check
`std::mutex` at the same time, not as an afterthought. The plugin
dispatch mechanism itself (`Engine/plugin/agsplugin.cpp` and friends)
spawns no threads (confirmed via grep, zero hits).

**Answered (2026-09-10 plan review)**: `tests/probes/djgpp-runtime/run.sh`
shows DJGPP's libstdc++ (GCC 12.2.0) is built without
`_GLIBCXX_HAS_GTHREADS` -- `<mutex>` defines no `std::mutex`, and
`std::condition_variable`/`std::thread` are likewise unusable. So this
"lower risk" item is a hard compile error, and it is wider than this
document found: `Engine/media/audio/audio_core.cpp` also keeps a
`std::mutex` and a `std::condition_variable` as struct members outside
any `AGS_DISABLE_THREADS` guard (lines 48-49, lock sites 158/182/191).
A DOS-only no-op lock/cv shim covering `debugmanager` and `audio_core`
is `PATCH-SEQUENCE.md` 0010. `std::this_thread::sleep_for`,
`std::chrono` and `std::atomic` all build.

## Plugin loading -- no dynamic-linking conflict, AGS already has the needed precedent

This hub's `CLAUDE.md` states a hard DJGPP constraint: no shared
libraries. AGS's plugin system (`Engine/plugin/agsplugin.cpp`) turns out
to already have exactly the fallback shape this needs, in three tiers:

1. **Dynamic load attempt first** (`pl_load_plugin()`): tries a
   `BaseLibrary`-derived loader selected at compile time by
   `Engine/util/library.h`'s platform `#if` chain --
   `AGS_PLATFORM_OS_WINDOWS` -> `library_windows.h`;
   `LINUX || MACOS || ANDROID || FREEBSD` -> `library_posix.h` (real
   `dlopen`/`dlsym`/`dlclose`); **`#else` -> `library_dummy.h`**, whose
   `Load()` unconditionally returns `false` and every other method is a
   no-op. **Correction (2026-09-10, found while writing `PATCH-SEQUENCE.md`):
   this dummy branch is NOT currently exercised by PSP, contrary to what
   this document originally said.** `AGS_PLATFORM_OS_PSP` is defined
   (always `(0)`) in `platform.h`'s macro set but referenced nowhere else
   in the entire pinned tree (confirmed by a repo-wide grep) -- PSP's real
   historical AGS port used its own separate `Engine/Makefile.psp` +
   `Engine/util/library_psp.h`, a parallel non-CMake build never wired
   through this modern `library.h` `#if` chain via `AGS_PLATFORM_OS_PSP`
   at all. DOS falling into `#else` once `AGS_PLATFORM_OS_DOS` is added to
   `platform.h` and correctly **not** added to the POSIX list is still the
   existing fallback firing correctly, with zero new loader code needed --
   just not a currently-proven path, only a structurally identical one to
   what PSP's own separate build once used. Low risk either way, since
   `DummyLibrary::Load()` unconditionally returns `false`.
2. **Falls back to statically-linked "builtin" plugins**
   (`pl_use_builtin_plugin()`) whenever dynamic load fails, gated by
   `AGS_BUILTIN_PLUGINS` (default **ON**). Six plugins compile directly
   into the Engine binary by filename match: `agsflashlight` (942
   lines), `agsblend` (1082 lines -- see the `LICENSE-REVIEW.md`
   correction above), `ags_snowrain`/`SnowRain20` (954 lines),
   `ags_parallax` (341 lines), `agspalrender` (4095 lines),
   `agsspritefont` (1158 lines); `agstouch` is iOS-only. (`Plugins/agslua`
   exists on disk but is not in the builtin-match list -- not
   auto-registered, not investigated further.)
3. **Falls back to harmless stub placeholders**
   (`RegisterPluginStubs()`) for anything not in the builtin list -- logs
   a warning, never fatal to the engine itself, only a potential feature
   gap for a specific game leaning on an unsupported plugin.

**Conclusion**: no architectural conflict. The only real work is (a)
wiring `AGS_PLATFORM_OS_DOS` to fall into `library_dummy.h` rather than
accidentally matching the POSIX list (would fail loudly at compile time
if wired wrong -- `dlfcn.h` doesn't exist under DJGPP, no silent
footgun), and (b) `PLAN.md`'s "few plugins" first-test-game selection
criterion now has a precise mechanical reason: any plugin outside the 6
statically-linked builtins silently degrades to stubs on this port, by
design. This finding also belongs in `PLATFORM-SURFACE.md` (it's a
filesystem/dynamic-loading question as much as a build one) -- see that
document.

## CMake build-system gaps found (not yet patched anywhere)

Four items where AGS's build links or configures something unconditionally
that a DOS profile doesn't need, each requiring its own new CMake guard
(the existing C-preprocessor `#if` guards on source files are not
sufficient by themselves):

1. `Glad::Glad` (OpenGL loader) -- linked regardless of `AGS_HAS_OPENGL`.
2. `Cda::Cda` (physical CD audio) -- linked unconditionally; no
   CD-ROM-audio requirement in this port's compatibility profile.
3. `find_package(Ogg/Vorbis/Theora REQUIRED)`/Fetch calls -- run at
   configure time regardless of `AGS_NO_VIDEO_PLAYER`.
4. SDL2_sound -- currently `FetchContent`-pulled and built inline rather
   than vendored+pinned like every other upstream in this repo's own
   `vendor/sources.manifest` convention; needs vendoring for a
   reproducible DJGPP cross-build, not a functional exclusion.

Found later while writing `PATCH-SEQUENCE.md` (2026-09-10), not by this
document's pass:

5. SDL2 itself -- `FetchSDL2`/`find_package(SDL2 REQUIRED)` can never
   resolve this port's SDL3-only sysroot; three link sites reference
   `${SDL2_LIBRARY}`/`${SDL2MAIN_LIBRARY}` (`PATCH-SEQUENCE.md` 0003).
6. `CMake/FindLocalOpenAL.cmake` -- outside `WIN32 OR LINUX OR MACOS OR
   FREEBSD` it tries `find_package(OpenAL)` and, on failure, falls back
   to building and linking mojoAL anyway; `mojoal.c` is SDL2 code
   (0005).
7. Two independent `CMAKE_SYSTEM_NAME` chains ending in `FATAL_ERROR`
   -- the top-level `CMakeLists.txt`'s and `libsrc/allegro/CMakeLists.txt`'s
   own (0001, 0002).

## Open items carried forward (not resolved by this document)

- ~~Whether the `ALFONT_DOS` build path compiles and whether DJGPP's
  `iconv` works~~ -- resolved 2026-09-10: DJGPP has no iconv, so that
  path is not used (see the tl;dr correction). What remains is whether
  alfont's *default* charset path renders a real game's non-ASCII text
  correctly -- a test-game check.
- `alfont`'s (`ALFONT.txt`), `miniz`'s (inline), `aastr`'s (inline), and
  Allegro's (**absent**) and AGSBlend's license texts need individually
  reading and recording in `LICENSE-REVIEW.md` -- presence was confirmed
  here, content was not classified, per this hub's "never guess a
  license" rule.
- SDL2_sound's own build-time decoder selection (which formats besides
  the explicitly-forced MIDI decoder actually get compiled in by
  default) was not inventoried -- check its own `CMakeLists.txt` at the
  pinned commit before vendoring.
- `miniz`'s actual role in AGS's game-package/save-data format was not
  traced past confirming the include sites -- relevant to
  `PLATFORM-SURFACE.md`'s filesystem-format question, not resolved here.
- Whether AGS's in-game MIDI playback (not cutscene audio) routes through
  SDL2_sound's MIDI decoder at all was not confirmed -- needed before
  assuming that decoder is safely disableable.
