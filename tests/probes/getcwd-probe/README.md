# getcwd-probe

Isolated probe for the doubled drive-prefix finding from `STARTS`
(`c:/c:/` in `PLAN.md`'s Measured constants table). Calls raw DJGPP
`getcwd()` directly, no AGS code, no `Path::FixupPath`, to answer: is
the doubling in DJGPP's own `getcwd()`, in DOSBox-X's mount, or in AGS's
own code?

## Result

Raw `getcwd()` is clean in both cases:

| Invoked from | `getcwd()` result |
|---|---|
| `C:\` (repo root, staged by `dosbox-run.sh`) | `"c:/"` |
| `C:\BUILD\AGS` | `"c:/build/ags"` |

No doubling, no drive-letter oddity, either place. **The bug is not in
DJGPP or the DOS mount.**

## Root cause (found by following up this probe's result)

Traced to `libsrc/allegro/src/file.c`'s `canonicalize_filename()`
(Allegro's own generic path-canonicalization function, used by
`Common/util/path.cpp`'s `MakeAbsolutePath()`, which in turn is used on
`Engine/main/main.cpp`'s `appPath` -- built from `argv[0]`, which DJGPP
hands back as an already drive-qualified absolute path like
`"c:/build/ags/ags.exe"`).

`libsrc/allegro/include/allegro/internal/alconfig.h` left
`DEVICE_SEPARATOR` as `'\0'` for the `__DJGPP__`/`ALLEGRO_UNIX` branch
patch 0002 introduced (DJGPP takes the same generic non-Windows platform
config as real Unix targets, since Allegro's own `ALLEGRO_DOS` platform
files use raw DOS/INT21 calls this port doesn't want). With
`DEVICE_SEPARATOR == '\0'`, `canonicalize_filename()`'s drive-letter
detection/stripping code (`file.c:142-162`) never runs, so an
already-absolute `"c:/..."` input falls through to the "make relative
path absolute" branch, which prepends the current drive+cwd in front of
it -- doubling the prefix.

Confirmed directly with a standalone `canonicalize_filename()` harness
linked against this tree's own `liballeg.a`, run under DOSBox-X from two
different real cwds, before and after the fix (`patches/ags/0037`):

| Input | Before 0037 | After 0037 |
|---|---|---|
| `argv[0]` = `"c:/canon.exe"` (at root) | `"c:/c:/canon.exe"` | `"c:/canon.exe"` |
| `argv[0]` = `"c:/build/ags/canon.exe"` | `"c:/build/ags/c:/build/ags/canon.exe"` | `"c:/build/ags/canon.exe"` |
| `"relative_no_drive.exe"` (no drive prefix at all) | (untested pre-fix; branch was unreachable for this input too since `_al_getdrive()` was unlinked) | `"c:/relative_no_drive.exe"` (root) / `"c:/build/ags/relative_no_drive.exe"` (subdir) |

This is not merely cosmetic: `Engine/main/engine.cpp`'s
`define_gamedata_location_checkall()` calls
`Path::MakeAbsolutePath(data_path)` on the **success** path too (line
969, after a game package is actually found) -- so an unpatched build
would have corrupted the resolved game-data path the first time a real
game package was staged, not just the no-game-data error message a
prior session noticed this in.

See `patches/ags/0037-AGS-Fix-canonicalize_filename-doubling-the-DOS-drive.patch`
for the fix itself (restores `DEVICE_SEPARATOR ':'` for DJGPP, plus a
DJGPP `_al_getdrive()` implementation in `unix/ufile.c` since fixing
`DEVICE_SEPARATOR` makes that previously-unlinked call reachable).

## Running it again

```
export PATH="$(readlink -f tools/djgpp)/bin:$(readlink -f tools/djgpp)/i586-pc-msdosdjgpp/bin:$PATH"
i586-pc-msdosdjgpp-gcc -march=i486 -mtune=pentium -O2 -Wall \
    -o build/getcwd-probe/GETCWD.EXE tests/probes/getcwd-probe/getcwd_probe.c
stubedit build/getcwd-probe/GETCWD.EXE minstack=256k
CWSDPMI=vendor/cwsdpmi/cwsdpmi.exe tools/dosbox-run.sh --exe build/getcwd-probe/GETCWD.EXE --fast --stdout /tmp/getcwd.log
```

The subdirectory case (`BUILD\AGS`) needs a manual stage since
`dosbox-run.sh` always stages flat at `C:\` -- see this session's own
history for the exact `MOUNT`/`RUN.BAT` invocation, not reproduced here
as a script since it was a one-off cross-check, not a repeatable probe.
