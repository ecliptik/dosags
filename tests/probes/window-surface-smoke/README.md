# window-surface-smoke -- BOOTSTRAP-0 probe 3

Standalone SDL3 program (`wsprobe.c`), no AGS code at all, against this
port's own DJGPP SDL3-DOS sysroot (`build/sysroot/`). Exercises exactly
the presentation path `PATCH-SEQUENCE.md`'s patch 0017 commits AGS's own
graphics driver (`Engine/gfx/ali3dsw.cpp`) to: `SDL_GetWindowSurface` +
one fill + `SDL_UpdateWindowSurface`, at the game's own depth, instead of
`SDL_Renderer`/`SDL_Texture`. Run at 8bpp (`SDL_HINT_DOS_MAX_BPP=8`,
paletted), 16bpp (`SDL_HINT_DOS_MAX_BPP=16`), and 32bpp
(`SDL_HINT_DOS_MAX_BPP=32`), all under DOSBox-X.

## Result

| Depth | Queried format | indexed | Rmask/Gmask/Bmask |
|---|---|---|---|
| 8bpp (`SDL_DOS_MAX_BPP=8`) | `SDL_PIXELFORMAT_INDEX8` | yes | n/a (paletted) |
| 16bpp (`SDL_DOS_MAX_BPP=16`) | `SDL_PIXELFORMAT_RGB565` | no | `0xf800`/`0x07e0`/`0x001f` |
| 32bpp (`SDL_DOS_MAX_BPP=32`) | `SDL_PIXELFORMAT_XRGB8888` | no | `0x00ff0000`/`0x0000ff00`/`0x000000ff` |

Full captured stdout: `wsprobe-headless.log`. Screenshots: `8bpp.png`,
`16bpp.png` -- both show four correctly filled quadrants (red / green /
blue / white, top-left / top-right / bottom-left / bottom-right). They
look visually identical to each other; that is the *correct* outcome, not
a bug -- RGB565 can represent all four full-intensity primaries/white
losslessly (5/6/5 bits all-on or all-off round-trips exactly), so a
16bpp `SDL_MapRGB`-computed fill of these specific test colors is
pixel-identical to the 8bpp palette fill. The headless log is what
actually distinguishes the two runs (`format=SDL_PIXELFORMAT_INDEX8` vs
`format=SDL_PIXELFORMAT_RGB565`), not the screenshots alone.

**32bpp added 2026-09-15, validating PLAN.md's "32-bit display path --
design comparison" section (operator decision, Option 1) at the shared
SDL3-DOS backend level, independent of AGS's own gate (`patches/ags/0075`).**
`32bpp.png` shows the same four-quadrant pattern -- also visually
identical to the 8/16bpp shots for the same round-tripping reason -- but
this is the first time this backend's VESA/LFB present path has ever
actually run at 32bpp end to end, on DOSBox-X or real hardware, rather
than just reading as bpp-generic in `SDL_dosmodes.c`/
`SDL_dosframebuffer.c`. The headless log confirms the real signal: a
genuine `320x240` VESA mode-set at `bits_per_pixel=32`
`bytes_per_pixel=4`, `format=SDL_PIXELFORMAT_XRGB8888`, correct
`pitch=1280` (`320 * 4`), and a successful fill + present. `32bpp.png`
was captured from a separate scratch single-depth build (`ws32.exe`, not
committed -- see "Running it again" below) rather than the normal
all-three-depths `wsprobe.exe`, specifically to remove any ambiguity
about which of the three 8-second display windows a screenshot landed in
(this repo does not yet have a robust way to correlate a screenshot's
capture time against a specific phase inside one multi-phase headless
run).

**This is a DOSBox-X (emulator) result, not real-hardware confirmation.**
Pixel *format* correctness (what `SDL_GetPixelFormatName` reports, RGB565
vs RGB555 at 16bpp; XRGB8888 at 32bpp) is something DOSBox-X's VESA BIOS
emulation can meaningfully answer -- it is not a timing/fps claim, so the
"never quote a DOSBox-X number as a performance result" rule does not
apply here. But `PATCH-SEQUENCE.md`'s own open item ("16-bit surface
format on real cards") still wants a real-hardware pass before treating
RGB565 as the only format patch 0017's fill-value code needs to handle --
a real VESA BIOS could report RGB555 for some cards, exactly the scenario
`docs/video.md`'s "write in the queried format" rule exists for. This
probe confirms the *mechanism* (query the format, don't hardcode it;
mode-set/fill/present all succeed at a depth nothing has ever asked for
before) works end-to-end at all three depths; it does not close the
cross-card question at 16bpp, and does not answer the real-hardware
per-frame-cost question PLAN.md's "32-bit display path" section raised
for 32bpp (2x bytes/frame at 320x200 vs. today's 16-bit ceiling) at all --
that needs a real 486DX2-66 measurement, not an emulator timing number.

## API shape confirmed (precedent for patch 0017)

Real SDL3 names, read directly from the pinned `vendor/SDL/include/SDL3/`
headers rather than assumed from SDL2:

- `SDL_HINT_DOS_MAX_BPP` (`"SDL_DOS_MAX_BPP"`, `SDL_hints.h`) -- string
  value `"8"`, `"16"`, or `"32"`.
- `SDL_CreateSurfacePalette(surface)` -- creates and attaches a palette
  to an indexed surface in one call (SDL3 collapses SDL2's separate
  `SDL_AllocPalette` + `SDL_SetSurfacePalette` into this for the common
  case of "give this surface its own new palette").
- `SDL_SetPaletteColors(palette, colors, first, n)` -- unchanged shape
  from SDL2.
- `SDL_FillSurfaceRect(surface, rect, color)` -- renamed from SDL2's
  `SDL_FillRect`. For an indexed surface the `color` argument *is* the
  palette index directly (no `SDL_MapRGB` needed for that case).
- `SDL_GetPixelFormatDetails(format)` -> `SDL_MapRGB(details, palette, r,
  g, b)` -- for a direct-color surface, compute the fill pixel from the
  actually-queried format; never hardcode an RGB565/555 shift.
- `SDL_UpdateWindowSurface(window)` -- unchanged shape from SDL2.

## Three real findings outside this probe's original scope, all fixed here

**1. `SDL_HINT_DOS_MAX_BPP` only takes effect if set before
`SDL_Init(SDL_INIT_VIDEO)`, not merely before `SDL_CreateWindow`.**
`vendor/SDL/src/video/dos/SDL_dosvideo.c`'s `DOSVESA_VideoInit()`
(`device->VideoInit`, run once by `SDL_Init`) calls
`DOSVESA_GetDisplayModes()` directly -- that is where the hint's bpp cap
actually filters the enumerated VESA mode list, and the filtered list is
then cached for the display's lifetime. The hint's own doc comment
("must be set before... SDL_CreateWindow") is consistent with the common
case (an app that sets the hint once at startup, before any video call
at all) but is easy to misread as "just before the create call" when
testing two depths in one process, as this probe originally tried. Fixed
by giving each depth its own `SDL_InitSubSystem(SDL_INIT_VIDEO)` /
`SDL_QuitSubSystem(SDL_INIT_VIDEO)` cycle with the hint set first. A real
port picks its depth once at startup and never hits this -- worth a note
near wherever patch 0011 ends up setting the hint, so a future session
does not lose time re-deriving this.

**2. `libSDL3.a` has an unresolved `extern` that blocks every DJGPP link
against this sysroot, not just AGS's eventual real audio integration.**
`vendor/SDL/src/audio/dos/SDL_dosaudio_sb.c:292` declares `extern
volatile uint32_t g_dos_sfx_synth_active_count;` with the comment
"engine -> SDL extern" -- SDL's own DOS SoundBlaster backend expects the
*consuming engine* to define and maintain this counter (doskutsu/
NXEngine's PixTone active-voice count; see e.g.
`patches/SDL/0070-pixtone-v2-rewire.patch`, `patches/SDL/0071-lever3-pixtone-irq-mix.patch`).
`SDL_audio.c`'s static driver bootstrap table references
`DOSSOUNDBLASTER_bootstrap` unconditionally (confirmed via `nm` on
`build/sysroot/lib/libSDL3.a`: `SDL_audio.c.obj` has an undefined
reference to `_DOSSOUNDBLASTER_bootstrap`, defined in
`SDL_dosaudio_sb.c.obj`), so `SDL_dosaudio_sb.c.obj` -- and this
unresolved extern -- is pulled into **every** DJGPP link against this
sysroot's `libSDL3.a`, including a video-only, `SDL_INIT_AUDIO`-free
probe like this one. AGS has no PixTone-equivalent counter anywhere in
its own source. `wsprobe.c` defines a local link-satisfying stub
(`volatile uint32_t g_dos_sfx_synth_active_count = 0;`, clearly commented
as such) to unblock this one probe's build -- **this is not a real fix**,
just what let this probe link. The port needs one real, permanent
decision here (most likely a small stub translation unit compiled into
every dosags binary, landing naturally alongside patch 0012/0018's audio
stubs, since that is where "AGS has no real audio backend yet" already
gets handled) rather than every future probe/binary improvising its own
copy of this same stub. Flagged in `PATCH-SEQUENCE.md`'s patch 0012 row
and `PLAN.md`'s open questions.

**3. A second engine -> SDL extern, `dos_port_engine_start_uclock`, joined
the first one some time between this probe's original build and its
2026-09-15 rebuild for the 32bpp addition.**
`vendor/SDL/src/timer/dos/SDL_dos_scheduler.c` declares `extern uclock_t
dos_port_engine_start_uclock;` -- same "consuming engine provides this"
shape as finding 2 above, just for the scheduler rather than audio. AGS
defines and sets the real one at `Engine/main/main.cpp:77`
(`dos_port_engine_start_uclock = uclock();` at startup, feeding every
ms-since-start timestamp the engine logs). `wsprobe.c` adds a second
local link-satisfying stub (`uclock_t dos_port_engine_start_uclock = 0;`)
next to the first -- same non-fix status, same reasoning: this probe has
no engine startup to hook, and never reads the value itself. Worth
folding into whatever permanent stub translation unit resolves finding 2,
rather than becoming a third improvised copy the next time this probe (or
any other non-AGS DJGPP binary against this sysroot) gets rebuilt after
more scheduler/timing work lands.

## Two scaffolding gaps fixed along the way (not a probe finding, real repo state)

- `tools/dosbox-launch.sh` (and `dosbox-run.sh`/`dosbox-teardown.sh`/the
  three `.conf` files) did not exist at this port's own `tools/` --
  `scripts/new-port.sh` only wires `scripts/*.sh` symlinks into
  `.sdl-dos-ports/shared/scripts/`, not an equivalent `tools/` set for
  `.sdl-dos-ports/shared/tools/`. `dosbox-launch.sh` itself assumes it
  lives exactly one directory below the port's repo root
  (`REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"`), which only holds from a
  `tools/` symlink at the repo root, not from invoking the hub's copy
  under `.sdl-dos-ports/shared/tools/` directly (that resolves
  `REPO_ROOT` to `.sdl-dos-ports/shared`, silently mounting the wrong
  directory as `C:`). Fixed by adding
  `tools/dosbox-launch.sh`/`dosbox-run.sh`/`dosbox-teardown.sh`/
  `dosbox-x*.conf` as symlinks into `.sdl-dos-ports/shared/tools/`,
  matching the existing `scripts/` convention exactly. This is a real,
  general dosags scaffolding gap, not specific to this probe -- every
  future DOSBox-X interactive session needs it.
- `dosbox-launch.sh` (unlike `dosbox-run.sh`) has no `CWSDPMI` env-var
  override -- it always mounts `D:` from a hardcoded
  `$REPO_ROOT/vendor/cwsdpmi`. dosags does not vendor its own CWSDPMI yet
  (per this session's own instructions, the sibling `~/git/doskutsu`
  checkout's copy is the one to use, via `dosbox-run.sh`'s `CWSDPMI=`
  override). For this probe's interactive/screenshot run specifically
  (`dosbox-launch.sh`, not `dosbox-run.sh`), that meant copying
  `~/git/doskutsu/vendor/cwsdpmi/cwsdpmi.{exe,doc}` into this repo's own
  `vendor/cwsdpmi/` locally so the hardcoded mount resolves --
  **deliberately not committed** (`*.exe` is already gitignored repo-wide;
  `cwsdpmi.doc` was left untracked too). Vendoring CWSDPMI for real
  (a `vendor/binaries.manifest` + fetch script, matching dossage's
  `fetch-vendor-binaries.sh` convention) is a real, separate decision
  outside this probe's scope -- flagged here, not made here.

## Running it again

```
tools/djgpp/bin/i586-pc-msdosdjgpp-gcc -march=i486 -mtune=pentium -O2 -Wall \
    -I build/sysroot/include -o build/ws/wsprobe.exe \
    tests/probes/window-surface-smoke/wsprobe.c -L build/sysroot/lib -lSDL3 -lm
tools/djgpp/i586-pc-msdosdjgpp/bin/stubedit build/ws/wsprobe.exe minstack=512k

# Headless capture (proves the API sequence + logs the queried formats,
# all three depths in one run):
CWSDPMI=~/git/doskutsu/vendor/cwsdpmi/cwsdpmi.exe \
    tools/dosbox-run.sh --exe build/ws/wsprobe.exe --fast --stdout /tmp/wsprobe.log

# Visual confirmation (needs vendor/cwsdpmi/cwsdpmi.exe staged locally --
# see the gap noted above):
DOSBOX_DISPLAY=:88 tools/dosbox-launch.sh --kill-first --fast --exe build/ws/wsprobe.exe
# then DISPLAY=:88 xdotool search --name DOSBox / import -window <id> out.png
```

Note the build output path (`build/ws/`, not something longer): the exe
must resolve to a valid 8.3 DOS path once mounted, and `dosbox-launch.sh`
does not translate long names for its auto-run command line -- an
earlier `build/probe-windowsurface/wsprobe.exe` path produced "Bad
command or filename" under DOSBox-X even though the file existed. Always
pass `--kill-first` (or confirm no dosbox-x is already running) before an
interactive launch -- `dosbox-launch.sh` silently refuses to start a
second instance and does not error loudly enough to be obvious via its
own backgrounded log, which cost real time this session (an xdotool
window search kept finding a *stale* prior run's window instead of the
new one, and a screenshot landed on that stale run's finished DOS prompt
rather than the intended frame).

`32bpp.png` specifically was captured from a scratch single-depth variant
(`ws32.exe`, 8.3-safe name, `DISPLAY_DELAY_MS` raised to 15000, only the
32bpp `run_depth()` call) rather than `wsprobe.exe`'s normal all-three-run
-- not committed, since it exists purely to make "which of three 8-second
windows did this screenshot land in" unambiguous for a single capture. To
reproduce it, copy `wsprobe.c`, keep only the `run_depth("32", ...)` call
in `main()`, raise the delay, rename the output to an 8.3 name (e.g.
`ws32.exe`), and run it through the same `dosbox-launch.sh` + `import
-window` sequence above.
