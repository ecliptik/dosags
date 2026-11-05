# PATCH-SEQUENCE.md -- minimum patch sequence to a compiling, linking DJGPP build

Milestone-0 deliverable per `PLAN.md` (the last unchecked Research item).
Scope matches the `COMPILES` milestone's own definition: "engine compiles
and links under DJGPP with editor, networking, hardware renderers, Theora
(`AGS_NO_VIDEO_PLAYER`), and plugins disabled (SDL/audio may still be
stubbed)." This is a **sequence proposal** -- ordered, one concern per
patch per `docs/patch-conventions.md` -- not the patches themselves.
Nothing has been written to `patches/ags/` yet.

Every patch here is local to this repository, permanently. Nothing in
this sequence is ever sent to AGS upstream (see `CLAUDE.md`'s "Never
contribute upstream"), so "diverges from upstream" is never a cost that
weighs against a change -- only "harder to re-apply on the next AGS
version bump" is, and that is a deliberate, rare event.

## Scope and methodology

Source: `vendor/ags/` at the pinned revision (`v3.6.3.13`,
`94e271df9c14484d89f4861100f643d39555dae7`), read directly for this
document -- `Common/platform/platform.h` (the whole feature-macro block,
lines 20-194), `Engine/util/library.h` + `library_dummy.h`,
`Engine/platform/base/agsplatformdriver.h`, `Engine/platform/linux/acpllnx.cpp`
(reference driver), `Engine/gfx/ali3dsw.cpp`/`.h`, `Engine/media/audio/audio_core.cpp`,
`Engine/ac/gamesetup.h`, `Common/libsrc/alfont-2.0.9/alfont.c`, the
top-level `CMakeLists.txt`, `Engine/CMakeLists.txt`, `Common/CMakeLists.txt`,
`CMake/FindLocalOpenAL.cmake`, and `libsrc/allegro/CMakeLists.txt` -- rather
than taken from `SDL-SURFACE.md`/`DEPENDENCIES.md`/`PLATFORM-SURFACE.md`'s
prose alone. Every patch below cites a real file and, where checked
directly, a line number.

Plus one set of real measurements: `tests/probes/djgpp-runtime/run.sh`
(compile-and-link probes against the actual DJGPP 12.2.0 toolchain;
results in that directory's `README.md`). Several items that were "open
questions" in the three research documents are facts now -- see "Probe
results" below.

## tl;dr

Three real configure/link-time blockers exist that **none of the three
Milestone-0 documents found**, because each of them read AGS's own
`Common/platform/platform.h` / `AGS_HAS_OPENGL` chain or its per-file
`target_link_libraries` calls, but not the two *other*, independent
places AGS gates on the host platform:

1. **The top-level `CMakeLists.txt` has its own `CMAKE_SYSTEM_NAME`
   `#elif` chain with a `FATAL_ERROR "Unsupported system"` fallback**
   (lines 76-89) -- entirely separate from `platform.h`'s
   `AGS_PLATFORM_OS_*` macros, and hit at **configure** time, before any
   compiler invocation. `vendor/SDL/build-scripts/i586-pc-msdosdjgpp.cmake`
   sets `CMAKE_SYSTEM_NAME DOS` (confirmed by reading it directly in the
   sibling doskutsu checkout's SDL clone, same pin), which matches none
   of this chain's `Windows`/`Linux`/`Darwin`/`Android`/`Emscripten`/
   `FreeBSD` branches -- an unpatched configure run dies here, before it
   ever reaches `platform.h`'s own gap.
2. **`libsrc/allegro/CMakeLists.txt` (the vendored Allegro 4.4.3 subset)
   has its own, second, independent `CMAKE_SYSTEM_NAME` chain with the
   identical `FATAL_ERROR "Unsupported system"` fallback** (lines
   148-166), reached when the top-level `add_subdirectory(libsrc/allegro
   EXCLUDE_FROM_ALL)` processes that subdirectory's own `CMakeLists.txt`
   -- `EXCLUDE_FROM_ALL` only excludes a target from the default build,
   it does not defer configure-time errors, so this dies just as hard as
   #1 does, independently.
3. **Nothing gets AGS's build pointed at this port's own DJGPP SDL3
   instead of AGS's own SDL2.** The top-level `CMakeLists.txt` either
   `FetchContent`s SDL2 from the internet or (`AGS_USE_LOCAL_SDL2=ON`)
   calls `find_package(SDL2 REQUIRED)` -- a package literally named
   `SDL2`, which will never resolve against a sysroot that only has SDL3
   installed, regardless of `CMAKE_PREFIX_PATH`. Three consuming link
   sites need to change, not just the acquisition block: `Engine/CMakeLists.txt`'s
   `target_link_libraries(engine PUBLIC ... ${SDL2_LIBRARY} ...)` (line
   ~548) and `target_link_libraries(ags PRIVATE engine ${SDL2MAIN_LIBRARY})`
   (line ~617), plus `Common/CMakeLists.txt`'s
   `target_link_libraries(common PUBLIC ${SDL2_LIBRARY} ...)` (line
   ~199). This is the hub's first CMake-based upstream engine port --
   `shared/build/sdl3-dos.mk`'s own header comment already anticipates a
   port wrapping `cmake -S $(ENGINE_SRC) -B ...` for its "game" stage, but
   nothing in this hub has actually pointed a real upstream
   `CMakeLists.txt` at the DJGPP SDL3 sysroot's own CMake package output
   before -- the exact target name to link against (`SDL3::SDL3` is the
   likely name, not independently confirmed against this hub's actual
   SDL3 CMake install rules) should be confirmed before writing this
   patch for real, not assumed.

**One correction to `DEPENDENCIES.md`/`PLATFORM-SURFACE.md`, found while
reading `library.h` directly for this document**: both said DOS falling
into `library_dummy.h`'s no-op fallback is "already exercised today by
PSP." That is not accurate at this pinned revision. `AGS_PLATFORM_OS_PSP`
is defined (always `(0)`) in `platform.h`'s macro set but referenced
**nowhere else in the entire tree**. PSP's real historical AGS port used
its own separate `Engine/Makefile.psp` + `Engine/util/library_psp.h`, a
parallel, non-CMake build system that was never wired through `library.h`'s
modern `#if`/`#elif` chain. The conclusion survives ("DOS falls to
`library_dummy.h` with zero new code, once not added to the POSIX list")
-- but it is **not** a currently-exercised path in this build. Corrected
in both documents. Low risk either way: `DummyLibrary::Load()`
unconditionally returns `false`.

**Decisions taken in the 2026-09-10 plan review** (recorded in `PLAN.md`,
applied throughout this sequence):

- **Renderer: present via the window surface from the start, not
  `SDL_Renderer`.** AGS's "Software" driver hard-requires a 32-bit display
  (`ali3dsw.cpp:73` rejects any other depth; `GetDisplayDepthForNativeDepth()`
  at lines 80-83 returns a constant 32; line 221 creates an ARGB8888
  streaming texture). For an 8-bit game that is three full-frame passes at
  4 bytes/pixel (8-bit virtual screen -> 32-bit texture -> SDL's software
  renderer -> 32-bit window surface -> VESA), and 320x200x32 is not a
  universally available VESA mode on 486-era cards. The program doc's
  section 17, `.sdl-dos-ports/docs/video.md`'s "Reduced color depth"
  section, and doskutsu's own measured history (its 8bpp+palette wave was
  its single largest gain, +12.7 fps, and that INDEX8 window-surface path
  is real-hardware-proven on the rig today) all point the same way. So
  patch 0017 replaces the present step -- the *only* place `ali3dsw.cpp`
  uses `SDL_Renderer` -- with `SDL_GetWindowSurface` + one blit at the
  game's own depth, rather than rename-porting the renderer path. This
  makes the "does `SDL_Renderer` work on the DOS backend" probe moot.
- **v0.1 color depth: 8-bit and 16-bit games.** 8-bit games present on
  an INDEX8 window surface (`SDL_HINT_DOS_MAX_BPP=8`) with the palette
  synced from Allegro's; 16-bit games on a 16bpp surface with one
  format-aware conversion if the card's mode is RGB555 rather than 565
  (`docs/video.md`'s "write in the queried format" rule). 32-bit games
  are out of scope for v0.1.
- **Build system: patch AGS's own CMake and drive it from this port's
  Makefile via the SDL DJGPP toolchain file**, as `shared/build/sdl3-dos.mk`
  was designed for -- not a from-scratch source-list Makefile. (The hub's
  `ports.yaml` note that said "DJGPP needs its own hand-written Makefile
  regardless" was written before `sdl3-dos.mk` existed and is corrected.)
- **Audio is stubbed for `COMPILES`**, exactly as the milestone wording
  allows: AGS's own OpenAL call sites (`audio_core.cpp`/`openalsource.cpp`)
  and its SDL2_sound decode call sites (`sdldecoder.cpp`) each get a
  temporary, explicitly-flagged stub patch, and mojoAL and SDL2_sound are
  gated out of the link entirely, so the mojoAL-vs-custom-mixer decision
  and the SDL2_sound port both stay deferred to the Sound milestone
  without blocking anything before it.
- **First test game: authored by us** (one room, one character, one
  hotspot, MIDI + WAV, 320x200, 8-bit) in the Windows AGS editor, so
  license, format version, and palette usage are all under our control.

## Probe results (2026-09-10)

From `tests/probes/djgpp-runtime/run.sh` against DJGPP GCC 12.2.0. Full
table in that directory's `README.md`; what matters for this sequence:

- **`std::mutex`, `std::condition_variable`, `std::thread` do not exist**
  -- libstdc++ is built without `_GLIBCXX_HAS_GTHREADS`. `<mutex>` defines
  no `std::mutex` at all. `AGS_DISABLE_THREADS` only guards the thread
  *creation* sites; `audio_core.cpp` keeps a `std::mutex` and a
  `std::condition_variable` as unguarded struct members (lines 48-49) and
  locks them unguarded (158, 182, 191), and `Common/debug/debugmanager.cpp`/`.h`
  does the same. That is a certain patch now (0010), not an open question.
  `video.cpp` also uses them but is excluded by `AGS_NO_VIDEO_PLAYER`.
- `std::this_thread::sleep_for`, `std::chrono::steady_clock`, `std::atomic`
  all build -- `Engine/ac/timer.cpp` needs no patch to *compile*.
- **`<iconv.h>` is absent.** `alfont.c:20` shows `#ifdef ALFONT_DOS` is
  the *iconv* path (README.txt: "The Libiconv project for DOS version");
  the default path uses `<locale.h>`/`<wchar.h>` + `setlocale`/`mbstowcs`,
  which DJGPP has (probe PASS). So **do not define `ALFONT_DOS`** --
  `DEPENDENCIES.md`'s "encouraging head start" framing was inverted and
  is corrected there.
- `statfs()` from `<sys/vfs.h>` builds -- the mechanism for
  `GetDiskFreeSpaceMB()` is identified (0030).
- `mmap`/`mprotect` symbols and `<sys/io.h>` are absent; Allegro's
  `if(UNIX)` feature probes for them will simply report false. The
  remaining Unix-branch headers Allegro checks all exist.

From `tests/probes/allegro-isolated/` (2026-09-10), building
`libsrc/allegro` alone under DJGPP:

- Two real fixes needed, not one: a quoted-`STREQUAL` DOS branch in
  `libsrc/allegro/CMakeLists.txt`'s own `CMAKE_SYSTEM_NAME` chain (the
  file's existing unquoted `MATCHES` pattern silently never matches "DOS"
  specifically -- CMake predefines a colliding variable named `DOS`; see
  patch 0002's row), *and* a new `__DJGPP__` branch in `alconfig.h`'s
  separate C-preprocessor platform-autodetect chain (the actually
  load-bearing one -- without it the first file compiled hits
  `#error platform not supported` regardless of the CMake-level fix).
- With both applied, `liballeg.a` builds and links with zero errors.
  Allegro's own `if(UNIX)` CMake feature-probe block never runs for DOS
  (gated on CMake's builtin `UNIX`, which this cross-compile leaves
  unset) -- confirmed not to matter, since the platform header DOS
  actually resolves to (`alucfg.h`) hardcodes every `ALLEGRO_HAVE_*` value
  it needs rather than reading those probed results.

## Sequence

Patch numbers are provisional slot proposals (`patches/ags/NNNN-*`), not
reservations -- confirm numbering against whatever's landed by the time
patch 0001 is written for real.

### Phase A -- get CMake to configure at all

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0001 | `CMakeLists.txt:76-89`, and the Emscripten block at 156-166 as precedent | Add `elseif ("${CMAKE_SYSTEM_NAME}" STREQUAL "DOS")` branch (**quoted `STREQUAL`, not the file's own unquoted `MATCHES` pattern** -- see `tests/probes/allegro-isolated/README.md`'s Finding 2: CMake ships a bundled `Platform/DOS-Initialize.cmake` that defines a variable literally named `DOS`, value `1`, purely because `CMAKE_SYSTEM_NAME` is the string "DOS"; an unquoted `elseif (${CMAKE_SYSTEM_NAME} MATCHES "DOS")` silently never matches because `if()` auto-dereferences the resulting bare `DOS` token against that colliding variable, testing `1 MATCHES "DOS"` instead of `"DOS" MATCHES "DOS"`): `set(DOS TRUE)`; do **not** set `AGS_DESKTOP` (line 92's `if(LINUX OR MACOS OR WIN32 OR FREEBSD)` stays false -- no `install(TARGETS ags RUNTIME DESTINATION bin)` for DOS); and, mirroring lines 164-166, `set(AGS_DISABLE_THREADS TRUE)` + `add_compile_definitions("AGS_DISABLE_THREADS=1")` -- only the Emscripten block does that today, so passing the option on the command line alone does **not** add the compile definition | Necessarily first -- every other patch is unreachable until configure gets past this. **Verified 2026-09-10** as part of BOOTSTRAP-0 probe 2's investigation (which bisected the STREQUAL-vs-MATCHES landmine using Allegro's own, independent copy of this same chain) -- this top-level gate itself was not independently probe-built, only read; the quoting fix is inferred from the identical pattern, not separately reproduced against the top-level file |
| 0002 | `libsrc/allegro/CMakeLists.txt:148-166` **and, newly found, `include/allegro/internal/alconfig.h`'s own separate C-preprocessor platform-autodetect chain (~line 52-61)** | **Two hunks, one concern.** (a) Same shape of `elseif` addition as 0001, independent CMake-level chain -- also needs the quoted `STREQUAL` form, not unquoted `MATCHES` (identical landmine, confirmed by building, not just by analogy: the naive unquoted copy silently fell through to `FATAL_ERROR` here). `set(ALLEGRO_UNIX TRUE)` in this branch is CMake-level cosmetic only (verified: never reaches a `-D` flag or gates `PLATFORM_SOURCES`, which branches on `ALLEGRO_WINDOWS` instead) but kept for shape-consistency with the sibling branches. (b) **The actually load-bearing fix**: `alconfig.h`'s own `#if defined(__linux__) #elif defined(__EMSCRIPTEN__) #elif defined(__FreeBSD__) #elif defined(__MINGW32__) #endif` chain (a *separate* mechanism from CMake's, evaluated by the C preprocessor using compiler-predefined macros, not `CMAKE_SYSTEM_NAME`) has no DJGPP branch at all -- without it, `ALLEGRO_UNIX` the **C macro** (distinct from, and unrelated to, the CMake variable of the same name in (a)) is never defined, and the very first file compiled hits `alconfig.h`'s `#error platform not supported` before anything else. Add `#elif defined(__DJGPP__) #define ALLEGRO_UNIX` alongside the `__FreeBSD__` branch | **Resolved 2026-09-10** by BOOTSTRAP-0 probe 2, a real isolated build, not analysis alone -- see `tests/probes/allegro-isolated/README.md` for both findings' full evidence, the tested diff, and why the CMake-level `if(UNIX)` feature-probe block (lines 37-115) not running for DOS turned out not to matter (`alucfg.h`, the header this resolves to, hardcodes every `ALLEGRO_HAVE_*` value it needs rather than reading those probed cache variables). Clean build confirmed: `liballeg.a` links with zero errors |
| 0003 | `CMakeLists.txt` (SDL2 acquisition block, ~288-293), `Engine/CMakeLists.txt` (~548, ~617), `Common/CMakeLists.txt` (~199) | Point the engine/common/ags targets at this port's own DJGPP-built SDL3 (sysroot from `shared/build/sdl3-dos.mk`) instead of AGS's `FetchSDL2`/`find_package(SDL2)` path | **Confirm the real SDL3 CMake target name from this hub's own SDL3 build output before writing this patch.** First CMake-consuming port in the hub; no precedent to copy |
| 0004 | `CMakeLists.txt:301-317` | Wrap the three `find_package(Ogg\|Vorbis\|Theora REQUIRED)`/Fetch blocks in `if (NOT AGS_NO_VIDEO_PLAYER)` (this port always configures with `AGS_NO_VIDEO_PLAYER=ON`) | Confirmed unconditional today |
| 0005 | `CMakeLists.txt:322` (`include(FindLocalOpenAL)`), `Engine/CMakeLists.txt:548` (`External::OpenAL`) | Gate both out for DOS | **Newly found**: `FindLocalOpenAL.cmake` sets `AGS_USE_MOJO_AL` only for `WIN32 OR LINUX OR MACOS OR FREEBSD`, else runs `find_package(OpenAL)` -- which fails under a cross-compile -- and then *falls back to mojoAL anyway* (`if(AGS_USE_MOJO_AL OR NOT OPENAL_FOUND)`), adding `libsrc/mojoAL` and linking `External::OpenAL`. `mojoal.c` is SDL2 code; compiled against SDL3 headers it fails. Stubbing AGS's `al*` call sites (0023) is not enough on its own |
| 0006 | `CMakeLists.txt:295-299` (`include(FetchSDL_Sound)`/`find_package(SDL2_sound)`), `Engine/CMakeLists.txt:550` (`SDL2_sound::SDL2_sound`) | Gate both out for DOS | Pairs with 0016's decoder stub. Vendoring SDL_sound (`icculus/SDL_sound` @ `3a41c3de5b90355745333041b96e142ba8f5fbdf`, pinned in `vendor/sources.manifest` like every other upstream) and porting its own SDL2 surface belong at the Sound milestone, not before `COMPILES` |
| 0007 | `Engine/CMakeLists.txt:547` | Wrap `Cda::Cda` in the same `if (WIN32 OR LINUX)` predicate that already gates `AGS_HAS_CD_AUDIO` at line ~568; don't add DOS to either | Mechanical |
| 0008 | `Engine/CMakeLists.txt:558-561` | Gate `Glad::Glad`/`Glad::GladGLES2` behind `AGS_HAS_OPENGL` | Whether `add_subdirectory(Engine/libsrc/glad EXCLUDE_FROM_ALL)` (line 360, still processed at configure time) does anything that fails under DJGPP even when unreferenced was not checked |

### Phase B -- get the compiler to accept `__DJGPP__` as a known platform

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0009 | `Common/platform/platform.h` | Add `#elif defined(__DJGPP__)` ahead of the final `#else #error` defining `AGS_PLATFORM_OS_DOS (1)` and the **eight** existing `AGS_PLATFORM_OS_*` macros `(0)`; add a new `AGS_PLATFORM_OS_DOS (0)` line to each of the eight existing branches (flat macro set redefined wholesale per branch, not an enum). Add `AGS_PLATFORM_OS_DOS` to the `AGS_SEARCH_FOR_GAME_ON_LAUNCH` list (line 187 -- DOS launches from the game directory with no wrapper passing a path, same as desktop) | **Landed 2026-09-10.** Everything else falls out on its own, confirmed by reading lines 162-194: `AGS_PLATFORM_DESKTOP` (162), `AGS_SUPPORT_MULTIDISPLAY` (168, derived from DESKTOP), `AGS_HAS_DIRECT3D` (169), `AGS_HAS_OPENGL` (170), `AGS_OPENGL_ES2` (177), `AGS_PLATFORM_IS_XDG_UNIX` (194) are all explicit OS lists DOS is simply not in |
| -- | `Engine/util/library.h:70-81` | No patch | Verification: with 0009 and DOS absent from the `LINUX \|\| MACOS \|\| ANDROID \|\| FREEBSD` condition, DOS falls to `#else -> library_dummy.h` with zero new code. Confirmed compiling as-is |

### Phase B2 -- source-compile gaps found by real build-testing, not anticipated by this document's original Phase B/C scope

**None of these four patches were in this document before 2026-09-10.** Phase A/B were scoped entirely from reading CMake/`platform.h` directly; they correctly predicted every *configure*-time blocker but none of these *source-compile*-time ones, which only a real build against the actual toolchain surfaces. Found and landed in this order, each confirmed against the real toolchain before being written (a standalone reproduction outside the full build, not just theory) -- see each patch's own commit message for the full diagnosis:

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0010 | `Common/libsrc/freetype-2.1.3/CMakeLists.txt` | Add a `DOS` branch selecting `src/base/ftsystem.c` (FreeType's own portable "ANSI" stdio implementation) + `src/base/ftdebug.c`, instead of the `else()` branch's "assume unix-y" `builds/unix/ftsystem.c` (uses `mmap`/`PROT_READ`/`MAP_PRIVATE`, confirmed absent under DJGPP) | **Landed 2026-09-10.** First real source-compile failure once Phase A+0009 get configure to fully succeed |
| 0011 | Top-level `CMakeLists.txt` | `add_compile_options(-U__STRICT_ANSI__)` for DOS, applied once globally before any `add_subdirectory()` | **Landed 2026-09-10.** Twelve targets set `C_EXTENSIONS`/`CXX_EXTENSIONS NO` (`-std=c11`/`-std=c++11`), and DJGPP's own libc headers (e.g. `sys/stat.h`) hide real declarations behind `#ifndef __STRICT_ANSI__` -- found via `libsrc/miniz/miniz.c`'s `struct stat` disappearing, reproduced standalone before fixing |
| 0012 | New `Common/platform/dos_compat.h`, wired via a global `-include` compile option (top-level `CMakeLists.txt`) | DJGPP's libstdc++ does not export C99 `<cmath>` additions into `std::` at all. Declares the `f`/`l`-suffixed C99 variants (present as GCC builtins under DJGPP, no header declaration) and defines three real, disambiguated `std::` overloads per function (`log2`/`exp2`/`round`/`trunc`/`fma`/`asinh`/`acosh`/`atanh`) | **Landed 2026-09-10, two real iterations.** GLM (used throughout Engine/Common) calls these directly. A first `using ::round;`-style attempt looked reasonable but failed for real against GLM's function-pointer-typed dispatch ("unresolved overloaded function type") -- DJGPP's global math functions are each a single double-only overload, not three, so binding the bare name to a `float(*)(float)` target is ambiguous without real per-width overloads. Corrected before landing, not after -- see the patch's own commit message |
| 0013 | `Engine/ac/characterextras.cpp` (x2), `Engine/game/game_init.cpp`, `Common/ac/gamesetupstructbase.cpp` | `reinterpret_cast<int32_t*>`/`const int32_t*` at 4 confirmed call sites where a `std::vector<int>`/`std::array<int, N>` feeds `Stream::ReadArrayOfInt32`/`WriteArrayOfInt32` (which take `int32_t*`) | **Landed 2026-09-10.** DJGPP is ILP32 with `int32_t` typedef'd to `long int`, distinct from `int` in C++'s type system even though both are 4 bytes here -- a real divergence from a 64-bit Linux dev host, where the two are the same type. Checked breadth first (grepped every `ReadArrayOfInt32`/`WriteArrayOfInt32(....data())` call site, 8 total) rather than assuming: 4 already pass an `int32_t`-typed container and need no change |

This category is not closed -- expect more of this shape (a real, narrow DJGPP-vs-modern-Linux-host divergence, confirmed by a standalone reproduction, fixed with a small targeted patch) as Phase C/D proceeds into real Engine/Common source, which Phase A/B's CMake-only research could not see.

### Phase C -- DJGPP runtime gaps the probes turned into known patches

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0014 | `Common/platform/dos_compat.h` | One concern: define `std::mutex`, `std::condition_variable`, and `std::cv_status` as DOS no-op shims, extending `dos_compat.h` (patch 0012) rather than a second DOS-compat file -- no source-file changes needed in `debugmanager.h`/`.cpp` or `audio_core.h`/`.cpp` themselves | **Landed 2026-09-10.** Corrected from this row's original plan: `std::lock_guard<T>`/`std::unique_lock<T>` do **not** need shimming -- confirmed by a standalone probe that both already exist as generic templates under DJGPP even without `_GLIBCXX_HAS_GTHREADS` (they only require `T` to provide `lock()`/`unlock()`), so redefining them would be a duplicate-definition error. Only the concrete `std::mutex`/`std::condition_variable`/`std::cv_status` types DJGPP's headers never declare at all needed adding. `audio_core.h:39-66`'s `AudioPlayerLock` (`std::unique_lock<std::mutex>&&`) and `audio_core.cpp`'s unconditional `notify_all()` call sites (outside any `AGS_DISABLE_THREADS` guard) were both probed against the candidate shim before landing, not just reasoned about. Verified: `debugmanager.cpp.obj` builds clean; `audio_core.cpp.obj` gets past every mutex/cv site and fails later, at the unrelated (already-known, deferred to 0022) `sdldecoder.h:22` `SDL_sound.h` missing-header error |
| -- | `Common/libsrc/alfont-2.0.9/` | No patch expected | Do **not** define `ALFONT_DOS` (iconv path). The default path's `setlocale`/`mbstowcs`/`wchar.h` all build under DJGPP. Whether that path renders a real game's non-ASCII text correctly is a test-game question, not a build one |

### Phase D -- get `engine`'s own SDL2 call sites to compile

One patch per file/concern per `SDL-SURFACE.md`'s inventory. 0016, 0022
and 0023 are **temporary stubs**, not real ports -- see tl;dr.
**Renumbered from 0011-0019 2026-09-10** to make room for Phase B2's
four real findings; **renumbered again 2026-09-10** (0018-0026 ->
0019-0027) to make room for a real finding surfaced by landing 0017 --
see that row's note; **renumbered a third time 2026-09-10** (0019-0027
-> 0020-0028) to make room for a real finding surfaced by landing 0018
-- see 0019's row. Confirmed as the real next blocker 2026-09-10: with
patches 0001-0013 applied, `make build-ags` gets past every
vendored-library gap (Allegro, FreeType, miniz, GLM) and fails on AGS's
own `Engine/ac/sys_events.h:21`, `fatal error: SDL_keyboard.h: No such
file or directory` -- the bare (SDL2-style) header name patch 0017 (the
input-pump patch, this table's new number) needs to fix, confirming
Phase D is next, exactly as this document predicted, just later than
originally numbered.

**Renumbered a fourth time 2026-09-10** (0020-0028 -> 0020-0029, i.e. one
new slot inserted, nothing shifted below 0023): landing patches 0020-0022
in file order (not phase order) meant the two audio stubs (this table's
former 0022/0024) landed back-to-back, so the OpenAL stub took the real
next-free slot **0023** rather than the "0024" this table had named it --
harmless, the same zero-cost reordering every prior renumbering here was.
What did cost a new slot: confirming patch 0023's own build result
surfaced a genuinely new, previously undocumented gap in
`Engine/media/video/videoplayer.h` (not part of any phase's original
scope) -- see the new 0024 row. Everything at or after the old 0023
(window-surface) shifts down by one to make room for it.

**Renumbered a fifth time 2026-09-10** (0020-0029 -> 0020-0032): continuing
`make build-ags`/`cmake --build ... -- -k` past 0023 turned out to be a
real four-patch chain, not a one-off -- each landed patch's own build
result surfaced exactly one more new, previously undocumented gap, in
strict sequence (0024 found the gap 0025 fixed; 0025's fix surfaced the
gap 0026 fixed; 0026's fix surfaced the gap 0027 fixed), until a full
`cmake --build ... -- -k` keep-going pass after 0027 showed no error
anywhere in the build except the two already-known, deliberately-deferred
items (the window-surface rewrite and the remaining rename-only sites).
Nothing below the old 0025 (window-surface) was written yet, so this
shift -- three new slots -- costs nothing beyond a table edit, same as
every renumbering before it.

**Renumbered a sixth time 2026-09-10, a swap rather than a shift**: this
document called the remaining-rename-only-sites patch "0029" and the
still-unwritten window-surface patch "0028," in that order. The
rename-only patch turned out ready to land first (it's the simpler,
lower-risk one), and the real next-free-slot check at that moment --
done before committing, not assumed from this document's own plan --
showed **0028** free, not 0029, since the window-surface patch had
never actually been written. The file was briefly named "0029" locally
before this was caught and it was renamed to 0028 prior to any commit.
Net effect: the two rows below swap numbers (rename-only sites is now
0028, landed; window-surface is now 0029, still open) with no other
shift -- everything from Phase E onward keeps its existing number.

| # | File(s) | Concern | Notes |
|---|---|---|---|
| 0015 | `Engine/platform/base/sys_main.cpp` | Window/display management: rename-only items plus the real signature changes (display index -> `SDL_DisplayID` resolution, `SDL_CreateWindow` position handling, fullscreen bool collapse and the `SDL_WINDOW_FULLSCREEN_DESKTOP` removal, `SDL_SetWindowGrab` mouse/keyboard split, `SDL_ShowCursor`/`HideCursor` split, `SDL_FreeSurface`->`SDL_DestroySurface`) | **Landed 2026-09-10.** Excludes the audio half of this file (0016) and the `AGS_SUPPORT_MULTIDISPLAY`-/`AGS_PLATFORM_OS_WINDOWS`-gated bodies (both macros are 0 for DOS -- dead code here, not a gap). **Correction to this row's original plan**: it is not where `SDL_HINT_DOS_MAX_BPP` gets set. Read directly for this patch (not assumed): `sys_main_init()` is called from `engine_init_backend()` (`Engine/main/engine.cpp:112`), very early ("Initializing backend libs"), well before any game package is loaded -- the game's own color depth (from the loaded game's data) is not known yet at that point in AGS's real call order, so there is nothing to set the hint *from* here despite BOOTSTRAP-0 probe 3's real timing requirement (before `SDL_InitSubSystem(SDL_INIT_VIDEO)`, not merely `SDL_CreateWindow`). This is a real, unresolved tension for 0022 (or an earlier decision point) to resolve, not solved by this patch -- see that row's updated note |
| 0016 | `sys_main.cpp` (`try_init_audio_driver()` and friends) | **Stub**: minimum to link and report "no audio device" cleanly, not the real `SDL_OpenAudioDevice` 5-param->2-param+stream rewrite. Also defines `g_dos_sfx_synth_active_count` | **Landed 2026-09-10.** `try_init_audio_driver()` deleted outright (nothing in its SDL2 shape is reusable once the Sound milestone picks a real API/architecture); `sys_audio_init()` logs and returns `false` -- confirmed against `Engine/main/engine.cpp`'s `engine_init_audio()` directly: this is an already-handled path (`usetup.AudioEnabled = res`), not a new failure mode. `g_dos_sfx_synth_active_count` (found 2026-09-10 by BOOTSTRAP-0 probe 3, `tests/probes/window-surface-smoke/README.md`: `vendor/SDL/src/audio/dos/SDL_dosaudio_sb.c:292` declares this as an `extern` the consuming engine is expected to define -- pulled into **every** DJGPP link against this sysroot's `libSDL3.a` by `SDL_audio.c`'s always-linked driver bootstrap table, not just a real audio integration) is now defined permanently in `sys_main.cpp`, `extern "C"`, always zero |
| 0017 | `Engine/ac/sys_events.cpp`/`.h` | Input event pump: `SDL_WINDOWEVENT` flattening, `SDL_Keysym` removal, event-type renames, and the bare `#include <SDL_keyboard.h>`-style SDL2 header names (confirmed the actual next build blocker 2026-09-10: `Engine/ac/sys_events.h:21`) | **Landed 2026-09-10.** Real signature changes beyond rename found by reading the vendored SDL3 headers directly: `SDL_GetKeyboardState()`/`SDL_GetKeyFromScancode()`/`SDL_GetScancodeFromKey()` all gained or changed params; `SDL_MouseButtonEvent`/`MouseMotionEvent`/`MouseWheelEvent`'s x/y/xrel/yrel are `float` now, not `int`; `SDL_TouchFingerEvent::fingerId` renamed `fingerID`; `SDL_TextInputEvent::text` is a heap-owned `const char *` now, not a fixed array. Also touched two files outside this row's original scope, both real necessary companions to `sys_events.h`'s own type changes (the header change would otherwise break them): `Engine/main/game_run.cpp` and `Engine/ac/global_game.cpp` -- see the patch's own commit message. **Found a real, previously unknown gap while confirming this patch's own build result**: with 0001-0017 applied, `make build-ags` gets past every file this patch or its two companions touch, but fails on a new, unrelated blocker -- `Engine/ac/dynobj/cc_serializer.h:22`, `'void AGSDeSerializer::Unserialize(...)' marked 'override', but does not override`. A fresh instance of patch 0013's `int32_t`-vs-`int` DJGPP divergence (`ICCObjectCollectionReader::Unserialize`'s first param is `int32_t handle`; the override declared `int index`), in a virtual-override shape 0013's own narrower grep (`ReadArrayOfInt32`/`WriteArrayOfInt32` call sites only) didn't cover. Given the next free slot as **0018**, cascading every later Phase D/E/F patch down by one (0018-0026 -> 0019-0027) -- nothing past 0017 had been written yet, so this costs nothing beyond a table edit, same as Phase B2's insertion |
| 0018 | `Engine/ac/dynobj/cc_serializer.h`/`.cpp` | Fix `AGSDeSerializer::Unserialize`'s parameter type: `int index` -> `int32_t index`, matching `ICCObjectCollectionReader::Unserialize`'s real declared signature (`Engine/ac/dynobj/cc_scriptobject.h`) | **Landed 2026-09-10.** Found while confirming patch 0017's build result, not previously known -- see that row's note. Same DJGPP-divergence category as patch 0013 (ILP32's `int32_t` is `long int`, a distinct type from `int` in C++, even though both are 4 bytes here), a different call-site shape (virtual override, not a `Stream::ReadArrayOfInt32`/`WriteArrayOfInt32` call). Parameter kept named `index` (not renamed `handle`) -- override resolution only needs the type to match, and every one of this function's ~20 internal `.Unserialize(index, ...)` call sites already compiled fine either way. Verified: `cc_serializer.cpp.obj` compiles clean; full `make build-ags` gets past this file and reaches a *third* real gap in the same category -- see 0019 |
| 0019 | `Engine/ac/roomstatus.cpp`, `Common/ac/view.cpp`, `Common/ac/gamesetupstruct.cpp`, `Common/ac/gamesetupstructbase.cpp`, `Common/game/interactions.cpp`, `Common/game/room_file_deprecated.cpp`, `Common/ac/inventoryiteminfo.cpp`, `Engine/ac/gamestate.cpp` | Same one concern as patch 0013 (`reinterpret_cast<int32_t*>`/`const int32_t*` at every remaining `Stream::ReadArrayOfInt32`/`WriteArrayOfInt32` call site whose buffer is a plain `int`/`int[]`, not already `int32_t`-typed) | **Landed 2026-09-10.** Found while confirming patch 0018's build result: `make build-ags` got past `cc_serializer.h` and failed on 5 more identical-shaped errors in `Engine/ac/gamestate.cpp` alone. Patch 0013's own commit claimed "grepped every `ReadArrayOfInt32`/`WriteArrayOfInt32` call site in the tree, 8 total" -- **that grep was incomplete**, confirmed by redoing it fresh: a real tree-wide `grep -rn "ReadArrayOfInt32\|WriteArrayOfInt32"` across `Engine/` and `Common/` finds 18 real call sites needing a cast (5 in `gamestate.cpp`, 2 each in `roomstatus.cpp`/`gamesetupstruct.cpp`/`interactions.cpp`/`room_file_deprecated.cpp`/`inventoryiteminfo.cpp`, 4 in `gamesetupstructbase.cpp`, 1 in `view.cpp`), not 4. The pattern in what 0013 missed: every site it *did* catch passes a `.data()`-returning container (`std::vector`/`std::array`); every site it missed passes a bare C-style `int[]` array name (which decays to a pointer without an explicit call needing inspection) -- 0013's own grep likely matched on `.data()` call shapes specifically. `Common/script/cc_script.cpp`'s 4 `.data()` sites needed no cast at all -- `code`/`fixups` are already `std::vector<int32_t>`. Verified: `make build-ags` gets past every one of these files cleanly; the only two remaining errors anywhere in the build are `Engine/media/audio/openal.h:18` (patch 0023's scope) and `Engine/media/audio/sdldecoder.h:22` (patch 0021's scope) -- both already documented, neither a new surprise |
| 0020 | `Engine/ac/system.cpp`, `Engine/device/mousew32.cpp` | Small rename-only sites | Low risk. **Renumbered from 0018, then 0019** |
| 0021 | `Engine/util/sdl2_util.cpp`/`.h` | `SDL_RWops`->`SDL_IOStream` rewrite of `OpenRWops()` | Bridges AGS's own `Stream`, needed regardless of the decoder stub. **Renumbered from 0019, then 0020** |
| 0022 | `Engine/media/audio/sdldecoder.cpp`/`.h` | **Stub**: keep the interface `sound.cpp`/`global_audio.cpp` call against; replace SDL2_sound decode + `SDL_AudioCVT` resampling with silent-failure no-ops | Pairs with 0006. **Renumbered from 0020, then 0021.** Confirmed as a real, currently-reached build blocker (`Engine/media/audio/sdldecoder.h:22`, `fatal error: SDL_sound.h: No such file or directory`) by patch 0019's own build verification. **Landed 2026-09-10.** Verified: `sdldecoder.cpp.obj` compiles clean; `audioplayer.cpp.obj`/`audio_core.cpp.obj` (untouched consumers) both get past every `sdldecoder.h` site and reach the same pre-existing `openal.h` blocker. Full `make build-ags`: exactly one error remains anywhere in the build (`openal.h`'s `AL/al.h`), down from two. Flagged a real follow-on for 0023, not fixed here: dropping `#include <SDL_sound.h>` also removes `Sound_AudioInfo`, which `openalsource.h` independently depends on (two members, one `SDLResampler::Setup()` overload) -- masked by `openal.h`'s own error firing first in the same include chain, so `make build-ags` didn't surface it yet |
| 0023 | `Engine/media/audio/audio_core.cpp`, `openalsource.cpp`/`.h`, `openal.h` | **Stub**: replace AGS's own OpenAL (`al*`/`alc*`) call sites with safe no-ops | Pairs with 0005. Where the mojoAL-vs-custom-mixer decision would otherwise have to be made; deliberately deferred. **Renumbered from 0022, then 0024** (landed straight after 0022 rather than after an intervening window-surface patch -- see this row's own former 0024 slot, now 0025, below). Confirmed as a real, currently-reached build blocker (`Engine/media/audio/openal.h:18`, `fatal error: AL/al.h: No such file or directory`) by patch 0019's own build verification. **Landed 2026-09-10.** Also resolved 0022's flagged `Sound_AudioInfo` follow-on: `openalsource.h` no longer declares `_inputFmt`/`_recvFmt` at all (the whole class lost every member that only existed to talk to a real OpenAL source). Also found and fixed, in the same patch, a second direct-SDL2_sound-API gap in `audio_core.cpp` itself (`Sound_Init()`/`Sound_Quit()`/`Sound_AvailableDecoders()` -- independent of `SDLDecoder`, not caught by 0022's narrower scope, previously masked by this same file's own `openal.h` failure). Verified: `openalsource.cpp.obj`/`audio_core.cpp.obj` compile clean. Full `make build-ags`: the `openal.h` blocker is fully gone; a new, previously-unreached, previously-undocumented error surfaces at `Engine/media/video/videoplayer.h:171` (`SDL_AudioFormat _audioFormat = 0;`, invalid int->enum conversion) -- not part of this patch's scope, see 0024 below |
| 0024 | `Engine/media/video/videoplayer.h`, `Engine/ac/global_game.cpp`, `Engine/ac/room.cpp` | Three independently-diagnosed residual gaps found in one continued-build slice, bundled because each is a single line, not because they're the same concern: (a) `videoplayer.h`'s `SDL_AudioFormat _audioFormat = 0;` -- a real C++ enum in SDL3 unlike SDL2's plain `Uint16` typedef, so implicit `int` init is a hard error; this header is **not** excluded by `AGS_NO_VIDEO_PLAYER` the way `theora_player.cpp`'s own decode source is (`Engine/ac/game.cpp` pulls it in unconditionally via `media/video/video.h`); (b) `global_game.cpp` extends patch 0017's own coverage -- `GetPressedKeys()` needs a complete `SDL_KeyboardEvent` type to call `std::vector<SDL_KeyboardEvent>::size()`/`operator[]`, but `sys_events.h` only forward-declares it by design; (c) `room.cpp`'s two `Math::Clamp(to_step, 0u, ...)` calls, a new instance of the established `int32_t`/`uint32_t`-vs-`int`/`unsigned int` DJGPP divergence category (0013/0018/0019), fixed with an explicit `Math::Clamp<uint32_t>` template argument matching the existing `listbox.cpp:323` precedent | Found while confirming patch 0023's build result -- masked until then by `openalsource.h`'s own (transitively included) `openal.h` failure firing first in the same file. See this document's own tl;dr / "expect more of this shape" framing: real, narrow SDL2->SDL3/DJGPP gaps in files no phase table anticipated, caught only by an actual build attempt. **Landed 2026-09-10** |
| 0025 | `Engine/gfx/ali3dogl.cpp`, `Engine/media/video/theora_player.h`, `Engine/media/video/video.cpp` | One real concern, three files: a disabled subsystem's own header/using-directive was placed *before* the `#if`/`#ifndef` check meant to gate it out, so its real dependencies still had to resolve even though none of its actual code compiled. `ali3dogl.cpp` included `ogl_headers.h` (which has no `AGS_HAS_OPENGL` check of its own -- always picks a platform header set, `#error`s on anything unrecognized) before checking `AGS_HAS_OPENGL`, unlike its sibling `gfxfilter_ogl.cpp`; `theora_player.h` declared its whole `APEG_STREAM*`-typed class body with no `AGS_NO_VIDEO_PLAYER` guard at all; `video.cpp`'s `using namespace AGS::Common;` sat inside its own `#ifndef AGS_NO_VIDEO_PLAYER` block, invisible to the `#else` branch's own `HError`-returning stub functions (a branch that has almost certainly never been compiled on any upstream AGS platform before this port) | Found while confirming patch 0024's build result. **Landed 2026-09-10** |
| 0026 | `Engine/ac/sys_events.cpp`, `Common/platform/dos_compat.h` | Three more gaps in patch 0017's own file, found only by a continued full build (not the earlier scratch-stub isolation check, which didn't need to reach these later functions): `SDLK_a`/`SDLK_z` -> `SDLK_A`/`SDLK_Z` (SDL3's `SDL_oldnames.h` deliberately breaks the lowercase spelling at compile time unless `SDL_ENABLE_OLD_NAMES` is defined -- a real rename, not a compat-layer opt-in, matches this whole series' practice); a `Utf8::Rune*`/`int*` cast at `Utf8::GetChar(..., &ki.UChar)`, a new instance of the 0013/0018/0019 `int32_t`-vs-`int` category; `dos_compat.h` extended with `std::truncf`/`std::roundf` (AGS calls the f-suffixed name directly, a libstdc++ extension DJGPP doesn't provide -- one-line addition reusing patch 0012's existing `std::trunc`/`std::round` overloads) | Found while confirming patch 0025's build result. **Landed 2026-09-10** |
| 0027 | `Engine/script/cc_instance.cpp` | Another new `int32_t`-vs-`int` divergence site (0013/0018/0019/0024's category), a brand new file for it: `CallScriptFunction()`'s local `int start_at, export_args;` couldn't bind to `FindExportedFunction(..., int32_t&, int32_t&)`'s reference parameters at all (no cast escape hatch for a reference the way there is for a pointer) -- fixed by declaring the locals as `int32_t` directly, matching the callee's already-correct signature. Also fixes a second error one line later for free: `std::min(numargs, export_args)` needed the same real type on both sides, and `numargs` (the function's own parameter) was already `int32_t` | Found while confirming patch 0026's build result. **Landed 2026-09-10.** Full `cmake --build ... -- -k` (keep-going) re-run after this patch: no error anywhere in the build except the two already-documented, deliberately-deferred items below (this table's own then-current 0028/0029, since renumbered again -- see 0028's row) |
| 0028 | `Engine/debug/debug.cpp`, `Engine/platform/base/agsplatformdriver.cpp` (+`sys_main.h`/`.cpp`), `Engine/main/graphics_mode.cpp`, `Engine/main/main_sdl2.cpp` | Remaining small rename-only sites: each file's own direct, first-party bare `#include <SDL.h>` (not a downstream consequence of another file's own gap). Real changes beyond rename found only by compiling: `debug.cpp`'s `SDL_priority[]`/`SDL_to_MT[]`/config-string `CstrArr` were all sized/ordered for SDL2's 7-priority layout -- SDL3 inserts a new `SDL_LOG_PRIORITY_TRACE` between `INVALID` and `VERBOSE`, so a "trace" slot was added to all three (mapped to the same `kDbgMsg_All` bucket `VERBOSE` already used); `SDL_LOG_CATEGORY_RESERVED1` no longer exists (renumbered from `RESERVED2`) -- `SDL_category[]`'s size sentinel becomes `SDL_LOG_CATEGORY_CUSTOM`; `SDL_LogSetOutputFunction`/`SDL_LogSetAllPriority` -> `SDL_SetLogOutputFunction`/`SDL_SetLogPriorities` (plain renames); `SDL_GetKeyboardState()`'s `const bool*` return (same fix as 0020/0023). `agsplatformdriver.cpp`'s `SDL_GetDisplayUsableBounds()` needs a real `SDL_DisplayID`, not a plain index -- reused (rather than duplicated) patch 0015's own `sys_get_display_id()` helper by exposing it through `sys_main.h` (was file-local to `sys_main.cpp`). `graphics_mode.cpp`'s SDL fix unmasked a second, unrelated pre-existing bug: DJGPP's `<inttypes.h>` gates `PRIu64` behind `__STDC_FORMAT_MACROS` in C++ mode, never defined here -- swapped for `<cinttypes>`, matching the already-working pattern in `managedobjectpool.cpp`. `main_sdl2.cpp` needed only the rename (no other `SDL_` symbol used) | **Real slot 0028, corrected from an initial mis-labeling as "0029"** before landing (caught and fixed prior to any commit -- see this document's own repeated "always confirm the real next-free slot" lesson; the window-surface patch below was never actually written, so labeling it "0028" and reserving "0029" for this already-ready patch was wrong the moment this one was ready first). **Landed 2026-09-10.** Verified: all four files compile clean individually; full `make build-ags`/`cmake --build ... -- -k` re-run shows these four files no longer appear anywhere in the build's error output -- exactly one blocker family remains anywhere in the entire tree, the window-surface rewrite below |
| 0029 | `Engine/gfx/ali3dsw.cpp`/`.h` | **Window-surface presentation, the present step only** (the review decision): replace the `SDL_CreateRenderer`/`SDL_CreateTexture`/`SDL_LockTexture`/`SDL_RenderCopy`/`SDL_RenderPresent` present step with `SDL_GetWindowSurface` + `SDL_BlitSurfaceScaled` + `SDL_UpdateWindowSurface`; `GetDisplayDepthForNativeDepth()` returns the native depth (8 or 16) instead of 32, `IsModeSupported()` accepts 8/16 instead of requiring 32; the virtual screen's own pixel buffer is wrapped directly as an `SDL_Surface` (`_vscreenSurface`) with no intermediate texture at all, since native-depth presentation needs no conversion step. Also resolves the `SDL_HINT_DOS_MAX_BPP` sequencing gap (see this row's own prior text below, now solved): re-initializes `SDL_INIT_VIDEO` once, right before creating the one window this backend ever creates, now that the real depth is finally known | **Landed 2026-09-10 (third session), split from this row's own prior single-patch plan into three concerns (present step, palette sync, filter collapse) -- see 0030/0031 below.** Traced `GetDisplayDepthForNativeDepth()`'s callers (`graphics_mode.cpp`) per this row's own prior open item: no 32-bit assumptions found needing a fix; `engine_setup.cpp`'s `engine_setup_color_conversions()` already sets Allegro's 16-bit RGB565 shifts unconditionally on every platform, not a DOS-specific gap. Also fixed a real gap this rewrite would otherwise have introduced: the old `SDL_RenderClear()` every frame kept any letterbox border clean; a plain blit doesn't, so an explicit conditional black-fill was added. Screen-shake/mirror-display (`play.shake_screen_yoff`/`play.screen_flipped`) honored via a lazily-allocated scratch surface, not dropped. Verified via isolated compile against the real DJGPP build flags (with `gfxfilter_sdl_renderer.h`/`gfxfilter_aa_sdl_renderer.h` temporarily scratch-stubbed, not landed, to isolate this file's own correctness from that still-open blocker) |
| 0030 | `Engine/gfx/ali3dsw.cpp`/`.h` | **8-bit palette sync**: every AGS call site that sets the palette (18 total -- `Engine/ac/screen.cpp` x8, `ac/global_palette.cpp` x3, `main/engine.cpp` x1, `media/video/flic_player.cpp` x2, `plugin/agsplugin.cpp` x1, `ac/draw.cpp` x1, plus one in the never-compiled-for-DOS `apeg` video-decode library -- located by a tree-wide grep, this row's own prior open item) calls Allegro's `set_palette()`/`set_palette_range()` directly; none need to change. `_vscreenSurface` instead shares the exact same `SDL_Palette` object as the window surface (confirmed via reading `SDL_pixels.c`'s `SDL_MapSurface()`/`Map1to1()` directly: two INDEX8 surfaces with merely equal-content-but-distinct palette objects are not guaranteed SDL's fast identity blit path), synced from Allegro's global palette (`get_palette()`) once per present, only when it's actually changed (a 256-entry `memcmp` against a cached copy) | **Landed 2026-09-10 (third session).** A grep-completeness caveat worth recording here since this row's own earlier text asked for the call sites to be "located": the first count (17) came from the shell's default `grep`, which is `ugrep` here -- re-verifying every "grepped the whole tree" claim from this same session with `/usr/bin/grep` explicitly found the 18th (the `apeg` one), unaffected by RGB::a (color.h: "alpha if available, otherwise a filler"), forced fully opaque on sync since this engine's palette never carries meaningful per-color alpha |
| 0031 | `Engine/gfx/gfxfilter_sdl_renderer.h`/`.cpp`, `Engine/gfx/ali3dsw.h`/`.cpp`, `Engine/CMakeLists.txt` | **Filter collapse**: the two `gfxfilter_*_sdl_renderer` filters (nearest, linear) become the one this driver's now-fixed-scale blit actually offers -- `GetScaleMode()`/`InitSDLHint()` were already dead after 0029 (nothing calls them; `SDL_HINT_RENDER_SCALE_QUALITY` doesn't even exist in SDL3, confirmed by a scratch-stub compile attempt), not merely simplified. `gfxfilter_aa_sdl_renderer.h`/`.cpp` deleted outright (a tree-wide grep found their basename referenced only in other-platform IDE project files this build never touches -- `Solutions/`/`iOS/`/`OSX/` -- not in any code this port compiles) and removed from `Engine/CMakeLists.txt`'s file list | **Landed 2026-09-10 (third session).** This is the row this document originally scoped as part of a single "0029" -- kept as a separate patch per the "one concern per patch" convention, matching this whole series' own precedent (0015/0016 both touch `sys_main.cpp` as separate concerns). **A full `cmake --build build/ags -j$(nproc) -- -k` pass compiled `ali3dsw.cpp.obj`/`gfxfilter_sdl_renderer.cpp.obj` clean against the real (unstubbed) headers together for the first time** -- the Engine side of `COMPILES` was done, but the same pass then failed inside `Common/` on five files that had never actually been compiled by any prior session at all (a stale, partially-populated `.obj` cache this `CMakeLists.txt` edit's forced reconfigure finally invalidated) -- see 0032-0036 below, a genuinely new discovery, not a regression from this patch |
| 0032 | `Common/ac/gamesetupstruct.cpp`, `Common/data/tra_file.cpp`, `Common/gfx/allegrobitmap.h`, `Common/gfx/image_png.cpp`, `Engine/ac/display.h` | One concern, five files, same category as 0013/0018/0019/0024/0027: `std::max(0, in->ReadInt32())` ambiguous-template-deduction sites (`gamesetupstruct.cpp` x2, `tra_file.cpp` x1) cast to `int`, matching `FontInfo::LineSpacing`'s own type; `Bitmap::RotateBlt`'s two declarations (`allegrobitmap.h`) said `int angle` where both real definitions already used `fixed_t` (`int32_t`) -- fixed the declarations to match, matching patch 0018's own precedent of fixing the declaration side; `image_png.cpp`'s `palette_colors` was `uint32_t[PAL_SIZE]` but passed to vendored `stb_image.h`'s own `unsigned int *palette_buffer` parameter -- a pointer-type mismatch, not just value-level, fixed by changing the local array's element type; `display.h`'s `wouttext_aligned` declaration said `int outline_color` where its real definition and its sibling `wouttext_outline`'s declaration one line above both already use `color_t` (`int32_t`) | **Landed 2026-09-10 (third session).** Found by comparing `Common/`'s own `.obj` count (68) against its `.cpp` count (91) in `build/ags/Common/CMakeFiles/common.dir/` before investigating -- 23 files had never actually been compiled by any prior session; of those, exactly 5 had real errors, fixed here |
| 0033 | `Common/platform/dos_compat.h`, new `Common/platform/dos_compat.cpp`, `Common/CMakeLists.txt` | `wcslen` is absent under DJGPP, not merely undeclared -- DJGPP's own `<wchar.h>` is documented in its own text as a "Bare bones header to satisfy SGI STL's `basic_string<>`" and declares no wide-string functions at all. Real callers: `Common/util/string_utils.cpp` (1, C++) and `Common/libsrc/alfont-2.0.9/alfont.c` (13, C) -- the C file never sees `dos_compat.h`'s force-include (CXX-only), and even where the shim is visible, a header-only `inline` function has no obligation to produce a real externally-linkable symbol at all. Fixed with a real, non-inline, `extern "C"` definition in a new companion `.cpp`, not another header-only `inline` | **Landed 2026-09-10 (third session).** Worth recording plainly: the first grep for `alfont.c`'s own call sites came back empty -- the shell's default `grep` here is `ugrep`, which gave a false negative on this specific file; `/usr/bin/grep` found all 13 sites immediately. See `feedback_grep_is_ugrep` (hub memory) / this doc's own "always confirm" lessons -- same category of tooling trap, different tool |
| 0034 | `Engine/media/video/video.cpp` | The `AGS_NO_VIDEO_PLAYER`-disabled stub branch defined `video_pause()`/`video_resume()` -- names `video.h` never declares outside that branch (only `video_single_pause()`/`video_single_resume()`/`video_single_stop()` are ever declared there), so those two stubs matched nothing callable through the header at all, and `video_single_stop()` was simply missing outright. Renamed to match and added the missing stub | **Landed 2026-09-10 (third session).** Same disabled branch patch 0025 already found guard-ordering bugs in -- "almost certainly never compiled on any upstream AGS platform before this port" continues to hold |
| 0035 | `Engine/ac/sys_events.cpp` | `is_sdl_mod_key()`/`make_sdl_mod_flag()` were declared in `sys_events.h` (patch 0017) with a comment stating they're "defined in sys_events.cpp", but the actual out-of-line bodies were never written -- undefined at link time the moment `Engine/main/game_run.cpp` (their only caller) finally got linked against a completing build. Ported directly from the pre-0017 original (`git show 94e271df9:Engine/ac/sys_events.h`), not guessed: `SDL_Keysym::scancode` is exactly the same field, now flattened onto `SDL_KeyboardEvent` per 0017's own finding, and the `KMOD_*` constants were already renamed `SDL_KMOD_*` by this same file's sibling function and by patch 0020 | **Landed 2026-09-10 (third session).** Never reached before either, for the same "never actually compiled" reason as 0032-0034's files |

### Phase E -- DOS platform driver

**Renumbered from 0020-0021 2026-09-10, then from 0024-0025, then from 0025-0026, then from 0026-0027, then from 0027-0028, then from 0028-0029, then from 0030-0031 2026-09-10** (see Phase D's intro for why). Landed as a single patch, not two -- the CMake wiring for one new file is a one-line addition, not a distinct concern from adding the file itself.

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0036 | New `Engine/platform/dos/acpldos.cpp`, `Engine/CMakeLists.txt` | Extend `AGSPlatformDriver` directly (not `AGSPlatformXDGUnix`), per `acpllnx.cpp`'s pattern: `GetDiskFreeSpaceMB()` via `statfs()` (`f_bsize * f_bfree`, probe-confirmed to build); `GetSystemOSID()` returns `eOS_DOS` (already defined, `Engine/ac/runtime_defines.h:258`); `InitializeCDPlayer()`/`CDPlayerCommand()`/`ShutdownCDPlayer()` stubbed "no CD, always fail" (matches 0007); `AGSPlatformDriver::CreateDriver()` under `#if AGS_PLATFORM_OS_DOS` like `acpllnx.cpp`'s own `#if AGS_PLATFORM_OS_LINUX` guard. The five directory methods inherit their `"."` defaults -- not overridden | **Landed 2026-09-10 (third session).** `AGSPlatformDriver::CreateDriver()` was the very last undefined symbol a full build found. **This is the patch that reaches `COMPILES`**: `rm -rf build/ags && make configure-ags` (clean reconfigure) + `cmake --build build/ags -j$(nproc) -- -k` completes with exit 0 and a real, linked `ags.exe`. Runtime correctness of `GetDiskFreeSpaceMB()`'s `statfs()` call under DOSBox-X is not yet verified -- only that it compiles and links |

### Phase F -- RUNMANIFEST wiring (2026-09-10, sixth session)

CLAUDE.md rule 5's own instrumentation, deferred from the fifth session
(TITLE_SCREEN) and overdue by that rule's own urgency. Landed as patch
0038, claiming the slot the cache-defaults patch below expected (see
that phase's own renumbering note).

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0038 | `Engine/main/main.cpp`, `Engine/main/quit.cpp` | Wire `.sdl-dos-ports/shared/include/runmanifest.h`'s `runmanifest_emit()` at `quit()`'s clean-shutdown path, right after its own `"***** ENGINE HAS SHUTDOWN"` print; capture engine start time in `main_init()` for `started_utc`/`duration_s`. Adds this port's own env-var allowlist (`BLASTER`, `DOS_PORT_ENVIRONMENT`, `SDL_DOS_AUDIO_SB_SKIP_DETECTION`, `SDL_INVALID_PARAM_CHECKS`) for `env_block_sha`. Also reorders `quit.cpp`'s own includes (`runmanifest.h` now before `<allegro.h>`) to avoid a real macro collision this patch found: vendored Allegro's `alconfig.h` unconditionally `#define`s `_farsetsel`/`_farnspokeb`/etc as generic plain-pointer macros, which mangle DJGPP's own real `<sys/farptr.h>` declarations (pulled in by `runmanifest.h`'s 86Box-detection code) if already active when that header is parsed -- a real compile break, confirmed by a real build failure before the reorder | **Landed 2026-09-10 (sixth session).** `binary_sha12` deliberately left at its documented-empty default -- no build-fingerprint pipeline wired for this CMake-driven engine stage yet (a real follow-up, not a silent gap; see the commit message). Confirmed by a clean-slate full build and a real DOSBox-X run against `tests/fixtures/minimal-game-package`'s fixture producing a genuine `RUNMANIFEST-BEGIN`/`END` block in `RUNMANI.LOG` -- `environment=dosbox-x`, a real non-zero `env_block_sha`, real `started_utc`/`duration_s`, `exit_code=0` |

### Phase G -- DOS defaults (originally "needed at `STARTS`"; `STARTS` landed without it 2026-09-10 -- now a game-load/`TITLE_SCREEN` item, cheap, listed so it isn't forgotten)

**Renumbered from 0022 2026-09-10, then from 0026, then from 0027, then from 0028, then from 0029, then from 0032 2026-09-10, then from 0037 2026-09-10, then from 0038 2026-09-10** (see Phase D's intro for why -- 0037 was claimed mid-session by an unplanned, higher-priority real bug fix, Phase E2 below; 0038 was claimed by the RUNMANIFEST wiring above, Phase F, per the sixth session's own explicit priority order).

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0039 | `Engine/ac/gamesetup.h:86-92`, `Common/ac/spritecache.h:49-53` | DOS branch for the cache defaults: today sprite cache = 128 MB (32 MB on Android/iOS), texture cache = 128 MB, sound cache = 32 MB. Program doc section 20 says start at sprite 4-8 MB, sound 2-4 MB, then profile; texture cache is meaningless for the software driver | Not a `COMPILES` blocker, **not a `STARTS` blocker (confirmed 2026-09-10, fourth session)**, and confirmed **low urgency, not a `TITLE_SCREEN` blocker either (2026-09-10, fifth session)**: read `Common/util/resourcecache.h`'s `SetMaxCacheSize()` directly -- it only sets a limit (`_maxSize = size; FreeMem(0u);`), it does not pre-allocate, so a 128 MB default is a wrong number, not a crash risk on a 16 MB DOS box. **Landed 2026-09-10 (sixth session)**: sprite cache and sound cache both set to the low end of their documented ranges (4 MB, 2 MB); texture cache and `DefSoundLoadAtOnce` left untouched (texture cache is meaningless for the software driver, per this row's own note). Confirmed build-clean and DOSBox-X-smoke-tested against the TITLE_SCREEN fixture (no observable behavior change, as expected -- this only lowers an upper limit that milestone's synthetic package never approaches) |

### Phase H -- binary_sha12 build fingerprint (2026-09-10, seventh session)

Closes the follow-up patch 0038 (Phase F) deliberately left open: no
build-fingerprint pipeline existed yet for this CMake-driven engine
stage, so `binary_sha12` was left at its documented-empty default.

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0040 | `Engine/main/quit.cpp` (vendor patch); `Makefile` (this port's own, not a vendor patch) | Makefile gains `AGS_BUILD_SHA12` (content hash of both vendor trees post-patch, this stage's own CMake flags, the hub build fragment, and the compiler version -- dossage's own `BUILD_SHA12`/`GAME_CXXFLAGS` non-circular-ordering pattern, read directly and adapted for CMake), threaded through `CMAKE_CXX_FLAGS` as `-DPORT_BUILD_SHA12="<hash>"`. `quit.cpp`'s existing RUNMANIFEST block (patch 0038) now `strncpy`s `PORT_BUILD_SHA12` into `manifest.binary_sha12` when the macro is defined | **Landed 2026-09-10 (seventh session).** Real quoting gap found and fixed while landing this (see Measured Constants): a single `\"` survives only one of the two shell layers between this Makefile and the actual compiler invocation (this Makefile's own recipe invoking `cmake`, then cmake's generated `build.make` invoking the compiler from its own separate recipe) -- `\\\"` (double backslash) is needed for the literal quote to reach the compiler's argv intact. Confirmed by a full clean build (zero errors) and a real DOSBox-X run against the TITLE_SCREEN fixture producing `binary_sha12=20a84a45bd83` in `RUNMANI.LOG`, matching `make build-sha12`'s own output. Also empirically confirms a `CMAKE_CXX_FLAGS` change forces a real recompile+relink for this stage (each object's own `build.make` depends on `flags.make`) -- no stale-object hazard here, unlike dossage's plain-Makefile-pattern-rule case |

### Phase I -- test harness engine instrumentation (2026-09-10/11, ninth session)

PLAN.md's "Test harness (AGS Quest)" section, slice 3: fill the
RUNMANIFEST fields that stayed at their documented NA defaults because
no real game loop had ever run before this session's test harness
(slices 1-2) gave the engine a real game to drive.

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0041 | `Engine/main/game_run.cpp`, `Engine/main/game_run.h`, `Engine/main/quit.cpp` | `dos_fps_sample_tick()` (called from the existing `game_loop_update_fps()`, self-gated to once per real second) samples `get_real_fps()` into a fixed 4096-entry ring buffer; `dos_fps_percentiles()` sorts a copy and fills RUNMANIFEST's `fps_p50`/`fps_p95` at `quit()` | **Landed 2026-09-11 (ninth session).** Confirmed by a real DOSBox-X run against the `tests/harness` AGS Quest package (`--test`, full autopilot run): `RUNMANI.LOG` shows `fps_p50=40.00`, `fps_p95=40.38` -- this port's game-speed cap under DOSBox-X's `--fast` cycles=max, not a real-hardware number (see PLAN.md's Performance KPIs section). `/sdldos:review`ed before landing: real `git format-patch` provenance, correct next-free slot, no `fopen`/non-ASCII/SIMD issues, not applicable to neutral-naming (port-owned patch), not a temporary diagnostic |
| 0042 | `Engine/main/main.cpp`, `Engine/ac/room.cpp`, `Engine/ac/event.cpp` | `dos_port_engine_start_uclock` (main.cpp, captured alongside the existing `dos_port_engine_start_time` at the same `main_init()` point) is a second, millisecond-precision anchor using DJGPP's `uclock()`. Paired `DOS-PORT room_transition t_ms=<ms> event=<start\|ready> room=<n>` log lines: `event=start` in `room.cpp`'s `new_room()` (the actual start of loading, not `global_room.cpp`'s earlier request-accepted log), `event=ready` in `event.cpp`'s `kRoomEvent_AfterFadein` handler (the same event the test harness's own autopilot keys its phase transitions on -- not `current_fade_in_effect()`'s fade-in-BEGINS point, which would measure the wrong span). For room 1 this pair doubles as the boot-to-first-frame load-time metric | **Landed 2026-09-11 (ninth session).** Confirmed by a real DOSBox-X run against the AGS Quest package: real `t_ms` pairs for every transition the autopilot's phase sequence drives, e.g. `t_ms=1908 event=ready room=1` (boot-to-first-frame), a ~9.3s `room=2`->`room=3` span (menu click through the room's own intro cutscene, which runs before `AfterFadein` fires -- a real, correctly-measured span, not a bug), and ~1-1.5s room3<->room4 transitions during the gem phase's balcony round trip. `/sdldos:review`ed before landing: same clean checks as 0041. Landing this also surfaced the patch-series stamp trap (see `~/.claude` memory `reference_patch_series_stamp_trap.md`) -- `make build-ags` refused with `verify-patches-applied` SERIES CHANGED after 0041 landed without a `make patches` refresh; fixed by committing 0042 first (capturing the dirty vendor-tree edits in the series itself) then running `make patches`, never by force-resetting a dirty tree |
| 0043 | `Engine/main/game_run.cpp`, `Engine/main/game_run.h`, `Engine/main/quit.cpp` | `dos_memory_sample_tick()` (same call site and once-per-real-second self-gating convention as `dos_fps_sample_tick()`, its own independent timer) reads `__dpmi_get_free_memory_information()`'s `largest_available_free_block_in_bytes` -- the field DPMI hosts including CWSDPMI most reliably support -- and tracks the smallest value seen across the run. Written as its own `DOS-PORT memory_min_free_kb=<n>` line in `RUNMANI.LOG`, right after the standard block (not a RUNMANIFEST struct field -- the shared schema has no memory slot and `runmanifest_emit()` has no mid-block extension hook) | **Landed 2026-09-11 (ninth session).** Confirmed by a real DOSBox-X run against the AGS Quest package: `RUNMANI.LOG` shows `memory_min_free_kb=158000` -- a real, sane, non-`0xFFFFFFFF` reading (DOSBox-X's generous default memory config, not this port's 16 MB real-hardware target, so the absolute number isn't a KPI datum yet, but the mechanism is confirmed working). `/sdldos:review`ed before landing: same clean checks as 0041/0042 |
| 0044 | `Engine/main/quit.cpp`, `Engine/main/game_run.cpp`, `Engine/main/game_run.h` | Last of the four slice-3 instrumentation items: `DOSAGS_LOG_TAG`/`DOSAGS_SCENE` fill RUNMANIFEST's `wave_tag`/`scene` (falling back to the previous `DEV0`/`boot`) and `DOSAGS_LOG_TAG` now also picks the `RUNMANI.LOG` filename itself (`<TAG>.LOG`, DOS 8.3-sanitized) instead of always the same fixed name -- a real collision between any two runs sharing a stage directory. `dos_auto_exit_check()` honors `DOSAGS_TAS_AUTO_EXIT_TICK`, calling `quit()` through the normal-exit path once the loop counter reaches it, independent of any script/AutoPilot module. `profiles/dosags.yaml` gains the `scene` env-block entry (was missing) and marks all three as implemented | **Landed 2026-09-11 (ninth session).** Confirmed by a real DOSBox-X run with a hand-edited `RUN.BAT` (`SET DOSAGS_LOG_TAG=tagtest`, `SET DOSAGS_SCENE=forestx`, `SET DOSAGS_TAS_AUTO_EXIT_TICK=30` -- `dosbox-run.sh` has no generic env-passthrough flag yet, noted as a real gap, not this patch's scope): produced `TAGTEST.LOG` with `wave_tag=tagtest`/`scene=forestx`, engine quit cleanly (`exit_code=0`, `duration_s=3`) well before the AutoPilot module's own splash-phase wait would have completed on its own, confirming the auto-exit fired independent of it. A normal run with no env vars set still produces `RUNMANI.LOG`/`DEV0`/`boot`, confirmed against the full 16-phase autopilot run (still all green). `/sdldos:review`ed before landing: same clean checks as 0041-0043 (the `fopen(run_manifest_filename, "a")` text-mode call is the same pre-existing convention as the original `fopen("RUNMANI.LOG", "a")`, not a new binary-mode violation) |

### Phase J -- test harness input-latency instrumentation (2026-09-11, eleventh session)

PLAN.md's "Test harness (AGS Quest)" section, slice 7 (optional,
non-gating): the `dialog` phase itself is pure AGS script
(`AutoPilot.asc`, not a vendor patch); this is its one engine-side
companion patch.

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0045 | `Engine/ac/sys_events.cpp` | Paired `DOS-PORT input_latency t_ms=<ms> event=<inject\|processed>` log lines around a simulated click: `event=inject` in `ags_simulate_mouseclick()` (reuses the existing `dos_port_engine_start_uclock` anchor patch 0042 introduced), `event=processed` in `on_sdl_mouse_down()`, gated on `event.button.which == SDL_TOUCH_MOUSEID` (the same pseudo-device `ags_simulate_mouseclick()` injects through, so a real physical click never gets double-logged) | **Landed 2026-09-11 (eleventh session).** Confirmed by several real DOSBox-X runs against the AGS Quest package's new `dialog` phase: real `inject`/`processed` pairs, deltas 11-24ms across runs. Also confirmed on real hardware (HW-486-66, tag `HW8`): `t_ms=287785`->`t_ms=288008`, a real 223ms delta -- roughly 10x DOSBox-X's own reading, the real hardware/emulator gap this instrumentation exists to surface. `/sdldos:review`ed before landing: real `git format-patch` provenance (`vendor/ags` commit `355eaae9f`), correct next-free slot (`0045`, confirmed via `ls patches/ags/ \| sort \| tail` before assuming), no `fopen`/non-ASCII/SIMD issues, not applicable to neutral-naming (port-owned patch), not a temporary diagnostic (kept permanently, like 0041-0044) |

### Phase E2 -- real, unplanned bug found during `TITLE_SCREEN` bring-up (2026-09-10, fifth session)

| # | File(s) | Change | Notes |
|---|---|---|---|
| 0037 | `libsrc/allegro/include/allegro/internal/alconfig.h`, `libsrc/allegro/src/unix/ufile.c` | Restore `DEVICE_SEPARATOR ':'` for the `__DJGPP__`/`ALLEGRO_UNIX` branch (patch 0002) instead of the driveless-Unix default `'\0'`, so vendored Allegro's `canonicalize_filename()` (`libsrc/allegro/src/file.c`) can recognize an already drive-qualified absolute path (what DJGPP hands back as `argv[0]`) instead of double-prepending the current drive+cwd; also adds a DJGPP `_al_getdrive()` to `unix/ufile.c` (derived from `getcwd()`, matching that file's own `_al_getdcwd()`), since the fix makes a previously-unlinked call to it reachable | **Landed 2026-09-10 (fifth session).** Root-caused a "cosmetic" doubled-drive-prefix bug STARTS had noticed in its own no-game-data error text (`c:/c:/...`) -- turned out to also corrupt a *successfully resolved* game-data path (`define_gamedata_location_checkall()`, engine.cpp:969, calls `MakeAbsolutePath()` on the success path too), which would have silently broken the very first real game package this port ever tried to load. Found via `tests/probes/getcwd-probe/` (ruled out DJGPP/the DOS mount -- raw `getcwd()` is clean) then a standalone `canonicalize_filename()` harness linked against this tree's own `liballeg.a`. See that probe's README and this patch's own commit message for the full mechanism |

## BOOTSTRAP-0: three probes before patch 0001 is written

1. **DJGPP runtime probe** -- done, `tests/probes/djgpp-runtime/`.
2. **Isolated Allegro subset compile** -- **done 2026-09-10**,
   `tests/probes/allegro-isolated/`. Configured and built `libsrc/allegro`
   alone under the DJGPP toolchain; found two real fixes needed (a
   quoted-`STREQUAL` CMake gate, matching Finding 2 below, and a missing
   `__DJGPP__` branch in `alconfig.h`'s own separate C-preprocessor
   platform chain -- the load-bearing one patch 0002 as originally scoped
   here did not anticipate). `liballeg.a` links clean with both applied.
3. **Window-surface presentation smoke test** -- **done 2026-09-10**,
   `tests/probes/window-surface-smoke/`. `SDL_HINT_DOS_MAX_BPP=8` ->
   `SDL_PIXELFORMAT_INDEX8`, palette set via `SDL_CreateSurfacePalette` +
   `SDL_SetPaletteColors`, fill via palette index, confirmed correct by
   screenshot; `SDL_HINT_DOS_MAX_BPP=16` -> `SDL_PIXELFORMAT_RGB565`
   (`Rmask=0xf800 Gmask=0x07e0 Bmask=0x001f`), fill computed via
   `SDL_GetPixelFormatDetails`+`SDL_MapRGB` from the queried format,
   also confirmed by screenshot. Two real mechanism findings along the
   way (both documented in that probe's README, not just this line):
   the hint must be set before `SDL_Init(SDL_INIT_VIDEO)`, not merely
   before `SDL_CreateWindow` (mode enumeration/filtering happens once at
   `VideoInit`); and 320x200 has no VESA mode entry at all under this
   emulated card (320x240 does) -- a game targeting exactly 320x200 needs
   this checked against whatever card profile it actually ships against.
   This is a DOSBox-X result, not a real-hardware confirmation of the
   16-bit format choice -- see "16-bit surface format on real cards"
   below, still open.

## Deferred / explicitly not resolved by this sequence

- ~~**mojoAL vs. a custom SDL3-audio-stream mixer** -- 0005/0023 gate and
  stub around it; the real choice belongs before the Sound milestone.~~
  **Resolved 2026-09-11**: custom mixer; mojoAL stays gated out. See
  `PLAN.md`'s "Sound milestone plan" (Architecture + work order S1).
- ~~**SDL2_sound: vendoring and its own SDL2->SDL3 port** -- 0006/0022
  defer it to the Sound milestone.~~ **Resolved 2026-09-11**: not ported
  at all -- a tiny RIFF WAV/VOC loader replaces it for PCM, MIDI clips go
  to the shared hardware-MIDI scheduler, OGG/MP3 are pre-converted on
  the host, and a tracker decoder (if any) is chosen only after
  profiling. See `PLAN.md`'s "Sound milestone plan".
- ~~**Allegro's `ALLEGRO_UNIX` branch choice** -- BOOTSTRAP-0 probe 2.~~
  **Resolved 2026-09-10**, see patch 0002's row above and
  `tests/probes/allegro-isolated/README.md`.
- ~~**The real SDL3 CMake target name this hub's DJGPP SDL3 build exports**
  -- confirm before writing 0003.~~ **Resolved 2026-09-10**: `SDL3::SDL3`
  -- `SDL3Config.cmake` always creates it as a compat alias to whichever of
  `SDL3::SDL3-shared`/`SDL3::SDL3-static` the sysroot actually has; this
  port's sysroot is static-only (`sdl3-dos.mk`'s `-DSDL_SHARED=OFF
  -DSDL_STATIC=ON`), so it resolves to `SDL3::SDL3-static` / `libSDL3.a`.
  See PLAN.md's Measured constants.
- **16-bit surface format on real cards** (RGB565 vs 555) -- BOOTSTRAP-0
  probe 3 (`tests/probes/window-surface-smoke/`) measured RGB565 under
  DOSBox-X's VESA emulation and confirmed the *mechanism* patch 0017
  needs (query `SDL_GetPixelFormatDetails`, compute fill values from it,
  never hardcode 565 or 555) works end-to-end -- but a real card's VESA
  BIOS could still report RGB555, and that still needs a real-hardware
  pass before this is fully closed, not just this emulator result.
  **The AGS palette-update hook site** for 8-bit is still open -- the
  probe confirmed the SDL-side API shape (`SDL_CreateSurfacePalette` +
  `SDL_SetPaletteColors`) but not where in AGS's own code (`set_palette`/
  `set_palette_range` call sites, not yet located) patch 0017 should call
  it from.
- **Whether alfont's default charset path renders non-ASCII text
  correctly** -- a test-game question.
- **Two open license gaps, not blocking, not to be forgotten**: Allegro
  4.4.3's vendored subset (no license file anywhere in the pinned tree)
  and AGSBlend -- tracked as open `RELEASE_READY` blockers in
  `LICENSE-REVIEW.md`.

Resolved since the first draft of this document, no longer open: the
`SDL_Renderer`-on-DOS-backend probe (moot, by decision), `std::mutex`
under DJGPP (absent, now patch 0014), `GetDiskFreeSpaceMB()`'s mechanism
(`statfs`, now in 0030).
