# PLATFORM-SURFACE.md -- filesystem, platform-driver, and dynamic-loading assumptions

Milestone-0 deliverable per `PLAN.md`. Audited against
`.sdl-dos-ports/docs/filesystem.md`'s checklist (drive letters,
backslash/forward-slash, cwd assumptions, 8.3/long filenames,
case-sensitivity, per-user config dirs, Unicode filenames, temp
directories, file locking, symlinks) plus the platform-driver interface
AGS expects every target to implement, and the dynamic-loading question
`DEPENDENCIES.md`'s plugin research already answered in outline.

## Scope and methodology

Source: `vendor/ags/` at the pinned revision (`v3.6.3.13`,
`94e271df9c14484d89f4861100f643d39555dae7`). As with `SDL-SURFACE.md` and
`DEPENDENCIES.md`, every claim below is sourced from reading the actual
pinned code, not assumed from AGS's typical desktop-platform behavior.

## tl;dr

This is the most reassuring Milestone-0 document so far. AGS's own
platform-driver base class already defaults every save/config/output
directory to `"."` (current directory) -- which is almost exactly
`.sdl-dos-ports/docs/filesystem.md`'s recommended DOS policy (keep
everything local to the game directory) -- and AGS's own script-visible
`eScriptSystemOSID` enum already has an `eOS_DOS` value, unused by any
current platform driver. Directory/file I/O (`Common/util/directory.cpp`)
uses plain POSIX `opendir`/`readdir`/`mkdir`/`stat`, all of which DJGPP's
libc implements. No symlink or file-locking usage exists anywhere in the
engine. Path handling already normalizes backslashes to forward slashes
internally. A DOS-appropriate platform driver looks like it should be one
of the *smaller* per-platform driver files in this codebase, not a new
subsystem -- though none of this has been build-tested yet, and "looks
small by inspection" is not "confirmed," consistent with this document's
sibling documents' caution.

## Platform driver: directory/config/save locations

`Engine/platform/base/agsplatformdriver.h` is the interface every
platform (`AGSLinux`, `AGSWin32`, `AGSMacOS`, ...) subclasses. Its
**base-class defaults**, inherited by any subclass that doesn't override
them:

| Method | Base default | Notes |
|---|---|---|
| `GetAllUsersDataDirectory()` | `FSLocation(".")` | |
| `GetUserSavedgamesDirectory()` | `FSLocation(".")` | |
| `GetUserConfigDirectory()` | `FSLocation(".")` | |
| `GetUserGlobalConfigDirectory()` | `FSLocation(".")` | |
| `GetAppOutputDirectory()` | `FSLocation(".")` | |
| `IsLocalDirRestricted()` | `true` | |
| `GetIllegalFileChars()` | `"\\/"` | Already disallows both slash styles by default -- matches the filesystem.md audit item without any port-side work |

Desktop platforms **override** these to real per-user paths: Linux/FreeBSD
route through `AGSPlatformXDGUnix` (`Engine/platform/base/agsplatform_xdg_unix.cpp`,
real `$XDG_CONFIG_HOME`/`$HOME`-based logic), Windows/macOS have their own
equivalents (not inspected this pass -- irrelevant to a DOS driver, which
should extend the **base** `AGSPlatformDriver` directly, not
`AGSPlatformXDGUnix`). **Recommendation: a DOS platform driver should not
override any of the five directory methods above at all** -- the base
defaults already implement `.sdl-dos-ports/docs/filesystem.md`'s
recommended policy (`GAME\SAVE\`, config local to the game directory,
no `$HOME`/`%APPDATA%`/XDG dependency) with zero new code. This is a
genuine "AGS already agrees with the hub's own DOS policy" finding, not
a coincidence to double-check away.

## Platform driver: pure-virtual methods a DOS driver must implement

Looking at `Engine/platform/linux/acpllnx.cpp` as the smallest real
reference implementation (54 lines total, extends `AGSPlatformXDGUnix`
and adds exactly four methods) -- a DOS driver extending the *base*
class directly would need at minimum:

| Method | Purpose | DOS implementation note |
|---|---|---|
| `GetDiskFreeSpaceMB(path)` | Pure virtual, no default | Needs a real DJGPP-side implementation. **Mechanism identified 2026-09-10**: `statfs()` from `<sys/vfs.h>` compiles and links under DJGPP (`tests/probes/djgpp-runtime/`); `f_bsize * f_bfree` is the free-space figure. Runtime correctness under DOSBox-X still to verify when the driver is written (`PATCH-SEQUENCE.md` 0020) |
| `GetSystemOSID()` | Pure virtual, no default | `Engine/ac/runtime_defines.h:258` already defines `eOS_DOS` in the `eScriptSystemOSID` enum -- **no new enum work needed**, `return eOS_DOS;` is the whole implementation. This enum is script-visible (`System.OperatingSystem` in AGS script), so a game's script logic that branches on OS will see a real, intentional value, not a misleading fallback. |
| `InitializeCDPlayer()` / `CDPlayerCommand()` / `ShutdownCDPlayer()` | Pure virtual, no default | Physical CD-DA audio playback (AGS's legacy `cdaudio.cpp` scripting API, uses the vendored `libcda-0.5` on Linux). **Recommendation: stub to "no CD, always fail," matching `DEPENDENCIES.md`'s finding that `Cda::Cda` should be excluded from the DOS link entirely** -- do not attempt real CD-DA support for v0.1. |

## Case sensitivity, path separators, 8.3 filenames

- **Case sensitivity**: `AGS_CASE_SENSITIVE_FILESYSTEM` is a real,
  existing compile-time macro (`Common/util/path.cpp`'s
  `Path::ComparePaths()`), defined only for `LINUX OR ANDROID`
  (`Common/CMakeLists.txt`). DOS is case-insensitive, matching the
  Windows/macOS default (undefined) -- **no new code needed, just don't
  add DOS to that `if (LINUX OR ANDROID)` condition.**
- **Path separators**: `Common/util/path.cpp`'s path-normalization logic
  (`FixupPath()` and friends) already does `path.Replace('\\', '/')` to
  bring Windows-style separators to a uniform internal style -- AGS
  already treats this defensively, consistent with games/assets
  potentially carrying Windows-authored paths. No DOS-specific gap found.
- **8.3 filenames**: `Common/util/path.h`'s doc comment on
  `Path::ComparePaths()` explicitly mentions "DOS-compatible 8.3
  filenames" as something the function accounts for -- **but the actual
  implementation only does a case-insensitive (or case-sensitive under
  `AGS_CASE_SENSITIVE_FILESYSTEM`) UTF-8 string compare, with no real 8.3
  truncation/comparison logic at all.** The doc comment is aspirational
  or a holdover from AGS's own real DOS-era history (Adventure Game
  Studio's lineage traces back to actually running on MS-DOS in the
  1990s, via Allegro), not a currently-implemented feature. Do not treat
  this comment as evidence that 8.3 handling already works -- it doesn't,
  the underlying compare is DOS-*compatible* (case-insensitive) but not
  DOS-*aware* (8.3-truncation-aware). Per `.sdl-dos-ports/docs/filesystem.md`'s
  own guidance ("prefer 8.3-safe filenames throughout... detect support
  explicitly and fail with a clear message rather than silently
  truncating"), this port's own asset/config naming should just stay
  8.3-safe by construction rather than relying on AGS to handle
  non-8.3-safe names gracefully -- it doesn't currently try to.

## Directory/file I/O

`Common/util/directory.cpp` uses plain POSIX calls throughout:
`mkdir(path, 0755)`, `opendir`/`readdir`/closedir (the Android-only
branch additionally tries `AAssetDir`, irrelevant here), `stat()`. All of
these are present in DJGPP's libc (DJGPP provides a substantially
POSIX-compatible C library on top of DOS) -- **expected to work without
porting, not yet build-verified.** No Windows-specific
(`_findfirst`/`GetFileAttributes`) or other non-portable directory API
usage found.

## Symlinks, file locking, temp directories -- all absent or irrelevant

- **Symlinks**: zero uses of `readlink`/`symlink()` anywhere in
  `Engine`/`Common`. Not a concern for this port.
- **File locking**: zero uses of `flock()`/`LockFile`/`fcntl(F_SETLK)`
  anywhere in `Engine`/`Common`. Not a concern.
- **Temp directories**: the only hit for temp-directory-style APIs
  (`tmpnam`/`mkstemp`/`GetTempPath`) is inside
  `Engine/platform/base/agsplatform_xdg_unix.cpp` -- the Linux/FreeBSD-only
  driver this port's own driver should **not** extend (see above). No
  temp-directory usage exists in any code path a DOS driver would
  actually compile.
- **Unicode filenames**: not specifically audited this pass -- AGS's
  `path.cpp` does reference UTF-8-aware comparison (`CompareUtf8NoCase`),
  suggesting Unicode-aware path handling exists at the string level; DOS
  itself has no meaningful native Unicode filename support (8.3 codepage-based
  names), so this is more a "what does AGS assume vs. what DOS can
  actually store" mismatch than a portability bug -- worth a real look
  once a first test game's actual asset filenames are known, not
  resolved here.

## Dynamic loading / plugins

Fully covered in `DEPENDENCIES.md`'s "Plugin loading" section -- summary
for this document's filesystem/platform-loading lens: AGS's plugin
loader already has a working `library_dummy.h` no-op fallback for
platforms without real dynamic linking, which a DOS platform naturally
falls into once `AGS_PLATFORM_OS_DOS` is added to
`Common/platform/platform.h` and **not** added to the POSIX
(`dlopen`-based) platform list. This directly satisfies this hub's "no
shared libraries" DJGPP constraint with zero new loader code. **Correction
(2026-09-10, see `DEPENDENCIES.md`'s own correction and `PATCH-SEQUENCE.md`)**:
this document previously said the fallback is "used today by PSP" -- not
accurate at this pinned revision. `AGS_PLATFORM_OS_PSP` is never
referenced outside `platform.h`; PSP's real historical build used a
separate, non-CMake `Makefile.psp` + `library_psp.h` never wired through
this chain. The dummy fallback for DOS is structurally identical to what
PSP's own separate build once used, not a currently-exercised path -- the
technical conclusion (zero new loader code, six common plugins ship
statically linked by default) is unaffected. See `DEPENDENCIES.md` for
the full three-tier breakdown (dynamic attempt -> builtin static plugins
-> stub placeholders) and which six plugins are statically linked.

## Threading (filesystem/platform-loading-adjacent, cross-referenced)

Not re-derived here -- see `SDL-SURFACE.md`'s Thread section (the
`std::thread` in `audio_core.cpp`, and the `AGS_DISABLE_THREADS`
precedent already set by AGS's own Emscripten target) and
`DEPENDENCIES.md`'s Threading section (the newly-found unconditional
`std::mutex` usage in `Common/debug/debugmanager.cpp`, not covered by
`AGS_DISABLE_THREADS`). Both need a real DJGPP viability check before
BOOTSTRAP, not assumed from either direction.

## Recommendation

A DOS `AGSPlatformDriver` subclass looks like it should be one of the
smallest platform driver files in this codebase -- smaller than
`acpllnx.cpp`'s 54 lines is plausible, since even the CD-player methods
that file implements for real should be pure stubs here. Concretely, it
needs:

1. Extend `AGSPlatformDriver` directly (not `AGSPlatformXDGUnix`) so all
   five directory methods inherit their already-DOS-appropriate `"."`
   defaults.
2. Implement `GetDiskFreeSpaceMB()` for real via `statfs()`
   (`<sys/vfs.h>`; builds under DJGPP per the 2026-09-10 probe).
3. Implement `GetSystemOSID()` as `return eOS_DOS;` (zero new enum work).
4. Stub `InitializeCDPlayer()`/`CDPlayerCommand()`/`ShutdownCDPlayer()`
   to "no CD, always fail."
5. Add `AGS_PLATFORM_OS_DOS` to `Common/platform/platform.h`'s platform
   `#if` chain (the gap already flagged in `SDL-SURFACE.md`) with
   `AGS_HAS_OPENGL`/`AGS_HAS_DIRECT3D` both false, `AGS_SUPPORT_MULTIDISPLAY`
   false, and **not** added to `AGS_PLATFORM_IS_XDG_UNIX` or
   `library.h`'s POSIX dynamic-loading platform list.

None of this has been build-tested -- this document describes what the
source says should work, not a confirmed result. The BOOTSTRAP milestone
is where these five items get written as real patches and checked
against an actual DJGPP compile, not assumed correct because the
inspection reads clean.
