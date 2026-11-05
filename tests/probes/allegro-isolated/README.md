# allegro-isolated probe

BOOTSTRAP-0 probe 2 (`PATCH-SEQUENCE.md`): configure and build
`vendor/ags/libsrc/allegro` (Allegro 4.4.3's headless subset -- the only
part AGS's own `cmake/FileList.cmake` compiles: blit/dither/palette/
quantize, FLI/FLC decode, polygon/rotate/floodfill, fixed-point math, BMP
loading, Unicode string helpers, a legacy packfile reader) ALONE under the
DJGPP cross toolchain, before it's mixed into the full AGS build.

Two real, independent findings came out of this, not one. Both are needed
together for a clean build; neither alone is sufficient.

## Finding 1: the load-bearing gate is in `alconfig.h`, not `CMakeLists.txt`

`PATCH-SEQUENCE.md`'s patch 0002 as originally sketched only anticipated
`libsrc/allegro/CMakeLists.txt`'s own `CMAKE_SYSTEM_NAME` `elseif` chain
(lines 148-166) -- the same shape as the top-level gate patch 0001 fixes.
That CMake-level gate is real and does need a DOS branch (see Finding 2),
but even with it fixed, the very first file compiled
(`src/allegro.c`) still failed immediately:

```
alconfig.h:79:8: error: #error platform not supported
astdint.h:32:5: error: #error I dunno how to get the definitions of
    fixed-width integer types on your platform...
alconfig.h:392:5: error: #error endianess not defined
alconfig.h:412:32: error: unknown type name 'uintptr_t'
```

`include/allegro/internal/alconfig.h` has its own, completely separate
platform-autodetection chain, evaluated by the **C preprocessor** at
compile time (not CMake at configure time):

```c
#if defined(__ANDROID__) || defined(ANDROID)
   #define ALLEGRO_ANDROID
#elif defined(_MSC_VER)
   #define ALLEGRO_MSVC
#elif defined(__APPLE__)
   ...
#elif defined(__linux__)
   #define ALLEGRO_UNIX
#elif defined(__EMSCRIPTEN__)
   #define ALLEGRO_UNIX
#elif defined(__FreeBSD__)
    #define ALLEGRO_UNIX
#elif defined(__MINGW32__)
    #define ALLEGRO_MINGW
    #define ALLEGRO_WINDOWS
#endif
```

None of these match DJGPP (`__DJGPP__`/`__MSDOS__` are what DJGPP's GCC
actually predefines; DJGPP deliberately does not define `__unix__` since
it isn't Unix). With no branch taken, `ALLEGRO_UNIX`/`ALLEGRO_MACOSX`/etc.
are never defined, and a few lines later:

```c
#ifndef SCAN_EXPORT
   #if defined ALLEGRO_MSVC
      ...
   #elif defined ALLEGRO_UNIX
      #include "allegro/platform/alucfg.h"
   ...
   #else
      #error platform not supported
   #endif
```

hits the `#error` immediately, before `astdint.h`'s `uint32_t`/`uintptr_t`
definitions or the endianness check are even reachable -- those two later
`#error`s in the same failing translation unit are downstream consequences
of the same root cause, not independent bugs (GCC keeps parsing in
error-recovery mode after the first `#error`, so it surfaces more).

**This is the load-bearing fix.** Tested candidate (kept as a diff here,
not landed as `patches/ags/0002` yet -- that's authored fresh later, during
the real patch sequence, informed by this finding):

```diff
--- a/libsrc/allegro/include/allegro/internal/alconfig.h
+++ b/libsrc/allegro/include/allegro/internal/alconfig.h
@@ -55,6 +55,8 @@
    #define ALLEGRO_UNIX
 #elif defined(__FreeBSD__)
     #define ALLEGRO_UNIX
+#elif defined(__DJGPP__)
+    #define ALLEGRO_UNIX
 #elif defined(__MINGW32__)
     #define ALLEGRO_MINGW
     #define ALLEGRO_WINDOWS
```

`ALLEGRO_UNIX` (not a new `ALLEGRO_DOS`) is the right choice: it routes to
`alucfg.h`, the platform header that matches what `FileList.cmake`'s own
`PLATFORM_SOURCES` selection already assumes for any non-Windows target
(see Finding 2) -- POSIX-style `dirent`-based directory listing, no GDI,
C-convention bank switching (`ALLEGRO_NO_ASM`), and (important) `alucfg.h`
**hardcodes** every `ALLEGRO_HAVE_*` macro it needs
(`ALLEGRO_HAVE_DIRENT_H`/`INTTYPES_H`/`STDINT_H`/`SYS_STAT_H`/
`SYS_TIME_H`/`MEMCMP`, all `#define`d unconditionally) rather than
generating them from CMake's feature-probe results -- so it does not
depend on the `if(UNIX)` block in `CMakeLists.txt` (Finding 2) having run
at all. Every one of those hardcoded facilities is confirmed present under
DJGPP by `tests/probes/djgpp-runtime/`.

## Finding 2: the CMake-level `CMAKE_SYSTEM_NAME` gate needs a QUOTED comparison, not the pattern the existing branches use -- a landmine specific to the string "DOS"

Patch 0002's other half -- `libsrc/allegro/CMakeLists.txt`'s own
`CMAKE_SYSTEM_NAME` `elseif` chain (lines 148-166), independent of the
top-level one patch 0001 fixes -- does need a DOS branch (its
`FATAL_ERROR "Unsupported system: DOS"` blocks configure before any
compiler is even invoked). The obvious fix is to copy the existing
branches' shape:

```cmake
elseif (${CMAKE_SYSTEM_NAME} MATCHES "DOS")
    set(ALLEGRO_UNIX TRUE)
```

**This does not work, and fails silently in a way that is easy to miss**:
configure still falls through to the `else()` / `FATAL_ERROR` branch, even
though a `message()` printed immediately beforehand confirms
`CMAKE_SYSTEM_NAME` is exactly the 3-byte string `DOS` (verified with
`string(LENGTH ...)`, ruling out hidden whitespace).

Root cause, isolated by bisection (see "How this was found" below): CMake
itself ships a bundled `Modules/Platform/DOS-Initialize.cmake` (for
OpenWatcom DOS cross-compiling support -- the SDL DJGPP toolchain file's
own header comment already notes CMake has *a* `Platform/DOS.cmake`, for a
different reason: OpenWatcom library-naming conventions). That module is
auto-loaded by CMake's own platform-detection machinery during
`project(ALLEGRO C CXX)` (which enables languages, triggering full
platform-module loading) purely because `CMAKE_SYSTEM_NAME` is the string
`"DOS"` -- regardless of which actual compiler/toolchain is in use. Its
entire content:

```cmake
set(DOS 1)
```

CMake defines a **variable literally named `DOS`**, value `1`. Every
existing branch in this chain is written **unquoted**:
`if (${CMAKE_SYSTEM_NAME} MATCHES "Windows")`. `${CMAKE_SYSTEM_NAME}` is
textually substituted to the bare token `DOS` *before* `if()` ever sees
its arguments (this happens at the language level, unconditionally, for
every `${...}` reference). `if()`'s own argument evaluator then sees the
bare, unquoted word `DOS` and -- because a variable of that exact name now
exists (CMake's own `DOS=1`, set moments earlier by the platform module)
-- dereferences it too, turning `if(DOS MATCHES "DOS")` into the
effective test `if(1 MATCHES "DOS")`, which is false. `CMP0054` (confirmed
`NEW` in this project via `cmake_policy(GET CMP0054 ...)`) does not
protect against this -- CMP0054 stops `if()` from re-interpreting an
*already-quoted* string as a variable/keyword; it says nothing about a
bare *unquoted* argument that happens to collide with a variable CMake
itself just defined, which is exactly this case.

**None of the other branches in this chain (`"Windows"`, `"Linux"`,
`"Android"`, `"Emscripten"`, `"Darwin"`, `"FreeBSD"`) hit this** --
checked: none of those exact strings collides with a CMake-predefined
variable name the way `"DOS"` does. This is a landmine specific to this
one platform string, not a general problem with the pattern AGS's
CMakeLists.txt uses throughout.

**Fix: quote the comparison (or use `STREQUAL`, which forces literal
string comparison and sidesteps this whole class of bug)**:

```diff
--- a/libsrc/allegro/CMakeLists.txt
+++ b/libsrc/allegro/CMakeLists.txt
@@ -160,6 +160,8 @@ elseif (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
     set(ALLEGRO_MACOSX TRUE)
 elseif (${CMAKE_SYSTEM_NAME} MATCHES "FreeBSD")
     set(ALLEGRO_UNIX TRUE)
+elseif ("${CMAKE_SYSTEM_NAME}" STREQUAL "DOS")
+    set(ALLEGRO_UNIX TRUE)
 else ()
     message(FATAL_ERROR "Unsupported system: ${CMAKE_SYSTEM_NAME}")
 endif ()
```

**This finding also applies to patch 0001** (the top-level
`CMakeLists.txt:76-89` gate PATCH-SEQUENCE.md already scoped), which uses
the identical unquoted-`MATCHES` shape for the identical reason -- a naive
copy-paste `elseif (${CMAKE_SYSTEM_NAME} MATCHES "DOS")` there hits the
exact same landmine. Confirmed directly: the parent session's own
`make configure-ags` run against the current *unpatched* top-level file
fails at line 89 (the fallback `FATAL_ERROR`, no DOS branch exists yet);
patch 0001 must write its new branch with a quoted comparison
(`STREQUAL`, matching this fix) from the start, not the unquoted pattern
the file's own existing branches use.

## Does the CMake variable `ALLEGRO_UNIX` (set in `CMakeLists.txt`) actually do anything?

No. Checked directly (`grep -rn "ALLEGRO_UNIX" .` across
`libsrc/allegro/`): the CMake-level `ALLEGRO_UNIX` variable this file's
`elseif` chain sets is read in exactly one place in the whole directory --
the `message( "ALLEGRO_UNIX:" ${ALLEGRO_UNIX} )` diagnostic print a few
lines below it. It is never passed to `target_compile_definitions`,
`add_definitions`, or any `-D` flag (confirmed against the real compile
command line CMake generates -- no `-DALLEGRO_UNIX` anywhere), and
`PLATFORM_SOURCES`'s own file-list selection (`if(ALLEGRO_WINDOWS) ...
else() ... ALLEGRO_SRC_UNIX_FILES ...`, lines 224-231) branches on the
*different* variable `ALLEGRO_WINDOWS`, not this one. The **C-level**
macro of the same name (`ALLEGRO_UNIX`, no `CMAKE_` involved, defined by
`alconfig.h`'s own chain -- Finding 1) is what actually matters; the two
are unrelated despite sharing a name. `set(ALLEGRO_UNIX TRUE)` in the new
DOS branch is kept anyway, purely to match every sibling branch's shape
for readability -- not because anything downstream depends on it.

## Does DOS need to run the `if(UNIX)` CMake feature-probe block (lines 37-115)?

No, and it can't as written regardless of the fix above: that block is
gated on CMake's own **builtin** `UNIX` variable (a completely different
thing from AGS's custom `ALLEGRO_UNIX`), which this cross-compile leaves
unset (confirmed: `message("UNIX=${UNIX}")` printed empty under
`CMAKE_SYSTEM_NAME=DOS`). That block runs *before* the `CMAKE_SYSTEM_NAME`
`elseif` chain (lines 37 vs. 148 -- compiler/platform setup comes later in
this file), so even setting CMake's builtin `UNIX` TRUE inside the new DOS
branch would be too late to affect it in the same configure pass. This
turns out not to matter: as Finding 1 notes, `alucfg.h` (the header DOS
actually uses once `ALLEGRO_UNIX` is `#define`d) hardcodes every
`ALLEGRO_HAVE_*` value it needs and never reads the CMake-probed
`ALLEGRO_HAVE_MMAP`/`ALLEGRO_HAVE_SYS_IO_H`/etc. cache variables this
block would have produced. Those probed values are dead code for the
`alucfg.h` path (checked: not referenced by `alucfg.h`, and `mmap`/
`mprotect`/`sys/io.h` are confirmed absent under DJGPP by
`tests/probes/djgpp-runtime/` regardless).

## Build result with both fixes applied

Clean: `liballeg.a` links with **zero errors**, one harmless warning
(`ufile.c:54`: `U_CURRENT` macro redefinition, pre-existing upstream
duplicate between `unicode.h` and `ufile.c`'s own `#define`, unrelated to
this port). All of Allegro's own Unix-branch feature-probe absences
(`mmap`, `mprotect`, `sys/io.h` -- confirmed absent under DJGPP) turned out
irrelevant to what actually gets compiled, consistent with the "does not
matter" analysis above.

## How this was found

Bisected with `message()`/`cmake_policy(GET CMP0054 ...)`/
`string(LENGTH ...)` diagnostics temporarily inserted at each `elseif`
branch and right after `project()`, comparing a minimal standalone
reproduction (`project(t NONE)`, manual `set(CMAKE_SYSTEM_NAME "DOS")`,
same `elseif` chain shape -- worked fine) against the real file under the
real DJGPP toolchain file (failed) to isolate that `project(ALLEGRO C
CXX)`'s full language-enablement path (which the minimal repro's
`NONE`-language `project()` never triggers) is what loads CMake's bundled
`Platform/DOS-Initialize.cmake` and defines the colliding `DOS` variable.
All diagnostic-only edits were removed before finishing; the two fixes
above are the only ones tested to be necessary.

## Recommended content for `patches/ags/0002`

Both hunks together (`CMakeLists.txt`'s quoted DOS branch, and
`alconfig.h`'s `__DJGPP__` branch) are one concern -- "make the vendored
Allegro subset buildable under DJGPP" -- and belong in one patch. Patch
0001 (top-level `CMakeLists.txt`) needs the same STREQUAL-not-MATCHES
correction applied to its own new DOS branch; note this when 0001 is
authored, don't rediscover it there.

## Reproducing

```
cd ~/git/dosags
export PATH="$PWD/tools/djgpp/bin:$PWD/tools/djgpp/i586-pc-msdosdjgpp/bin:$PATH"
# apply the two diffs above to a fresh vendor/ags checkout, then:
cmake -S vendor/ags/libsrc/allegro -B build/probe-allegro \
    -DCMAKE_TOOLCHAIN_FILE="$PWD/vendor/SDL/build-scripts/i586-pc-msdosdjgpp.cmake" \
    -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF
cmake --build build/probe-allegro -j"$(nproc)"
# expect: lib/liballeg.a, zero errors
```
