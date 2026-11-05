# BENCH -- the self-authored, TAS-driven benchmark fixture

Spec and rationale: PLAN.md, "First test game -- authoring plan
(TAS-driven benchmark fixture), 2026-09-16". This file is the as-built
record: what exists, how it is built, what was verified, and every
deviation from that plan with its reason. Built on branch `bench8` in an
isolated worktree, in parallel with the main 40/40 work.

Why it exists: every other fixture is a closed binary (no scripted
motion) or a 16-bit 640x360 game. BENCH8 is a TRUE 320x200 8-bit game to
the engine (letterbox off -- the only fixture that can exercise the DOS
backend's Mode 13h path) whose `walk` and `anim` scenes change real
pixels every frame for a fixed tick window.

## Licenses

- `assets/generate_assets.py` and everything it generates (background,
  masks, sprites, WAV, MIDI): original work, **CC0 1.0**.
- Scripts (`*.asc`, `*.ash`), `gen_agf.py`, `build*.sh`, `tools/mkroom.cpp`:
  **MIT** (this repo's LICENSE).
- Font: Press Start 2P, **SIL OFL 1.1**, the copy already verified under
  `tests/harness/packages/agsquest/overlay/assets/` (with its OFL text).
- Nothing from `ags-template-source`, the AGS demo game, or any other
  game is in here -- no default GUI art, no cursors, no template script.
  Game.agf's element and setting NAMES are the Editor's schema; every
  value is ours. AGS's own script API header (`agsdefns.sh`) is read
  from the AGS source tree at build time and never copied here.

## T0 -- host tools (done)

`build-host-tools.sh [AGS_SRC] [OUT_DIR]` builds AGS 3.6.3.13's own
headless toolchain natively, then `mkroom`:

    cmake -S <AGS_SRC> -B build/host-tools -DCMAKE_BUILD_TYPE=Release \
      -DAGS_BUILD_ENGINE=OFF -DAGS_BUILD_TOOLS=ON -DAGS_BUILD_COMPILER=ON \
      -DAGS_TESTS=OFF -DCMAKE_C_FLAGS=-D_GNU_SOURCE
    make -C build/host-tools

`-D_GNU_SOURCE` is the one gap (Common/util/stdio_compat.c needs it under
-std=c11 for truncate()); a flag, not a source change. Products used:
`Compiler/agscc`, `Tools/agf2dta`, `Tools/agfexport`, `Tools/spritepak`,
`Tools/crmpak`, `Tools/agspak`, and `mkroom`.

Built and verified 2026-09-17 from a PRISTINE clone of the pin
(94e271df9c14, tag v3.6.3.13), not from `vendor/ags` -- that tree carries
the DOS patch series and is reset/re-patched by other work. Use a
pristine clone as AGS_SRC (`git clone vendor/ags X && git -C X checkout
94e271df9c14484d89f4861100f643d39555dae7`).

Tool facts learned by running them (not assumed):

- `agf2dta` does NOT embed compiled scripts in game28.dta (its own header
  comment, Tools/data/data_file_writer.cpp:23-25). The engine picks them
  up as separate assets instead: `GlobalScript.o`, `__DialogScripts.o`,
  and the modules named in `ScriptModules.lst` (Engine/main/
  game_file.cpp:49-51, TryLoadGameScripts()).
- `agfexport` (not named in the plan) generates what the Editor would:
  `autoash` (the auto script header), `game-cfg` (acsetup.cfg),
  `script-list`/`header-list`, `font-list`, `audioclip-list` (the
  `au%06d.ext` asset names), `room-list`.
- PNG input keeps 8-bit indices: Common/gfx/image_png.cpp detects an
  indexed PNG and loads it with its palette, so paletted sprites and
  backgrounds go in as PNG.

### mkroom

`tools/mkroom.cpp`: reads a room crmpak created, sets the room DATA the
AGS tools do not cover (hotspot names/handlers, objects, walkable-area
scaling, walk-behind baselines, edges, room events, GameID) from an XML
description, and writes it back through AGS's own `WriteRoomData()`.
No format code of our own; each field cites the writer line it lands on.

Deviation: the plan said a JSON room description. It is XML, because
TinyXML2 is already part of AGS's libtools and JSON would have meant
carrying a parser for ~60 lines of input.

## T1 -- skeleton that boots (done, 2026-09-17)

`build.sh [--depth 8|16|32]` runs the whole pipeline with no Editor and
no Wine: `assets/generate_assets.py` -> `gen_agf.py` -> `spritepak -c`
-> `agf2dta` -> `agfexport autoash|game-cfg` -> `agscc` per module and
for the room -> `crmpak -c` (background + four masks) -> `mkroom`
(room data) -> `crmpak -e ash` (the room's own header) -> `crmpak -i
script` -> `agspak -c`. Output: `tests/harness/games/bench<depth>/
BENCH<depth>.ags` + `acsetup.cfg` (gitignored, where run-dosbox.sh looks).
The package holds 10 assets: `acsprset.spr`, `sprindex.dat`,
`game28.dta`, `GlobalScript.o`, `AutoPilot.o`, `ScriptModules.lst`,
`room1.crm`, `agsfnt0.ttf`, `au000000.mid`, `au000001.wav`.

Deviation: `Game.agf` is GENERATED (`gen_agf.py`), not hand-authored as
the plan said. The three depth builds must differ in exactly one setting,
and ~2,000 lines of hand-kept XML would not stay that way. The depth-8
output is committed as `Game.agf` so a drift shows up in git.

Gate met under DOSBox-X (snapshot engine binary, see below), first run:

    Game data version: 3060310 / Compiled with: 3.6.3.13
    Script module asset 'GlobalScript.o' is found and loaded
    Script module asset 'AutoPilot.o' is found and loaded
    Loaded font 0: agsfnt0.ttf, req size: 8
    Game native resolution: 320 x 200 (8 bit)      <- no "letterbox-by-design"
    Initialize path finder
    Now in room 1
    RUNMANIFEST: exit_code=0 critical_count=0 warn_count=0

and a SaveScreenShot at tick 60 (320x200, 8-bit paletted BMP) shows the
brick wall, window, sign, pillar, floor, the character and the cursor in
the fixture's own palette -- looked at, not just hashed. `agf2dta`'s
"v0.1.0" risk named in the plan did not bite: the pinned engine read its
game28.dta without complaint.

A TRUE 320x200 game: `LetterboxMode` is False in Game.agf and must stay
so. With it on the engine reports 320x240 (Common/ac/
gamesetupstructbase.cpp, ResolutionTypeToSize) and the fixture could not
exercise the DOS backend's Mode 13h path. A letterboxed 320x240 variant
would be one changed setting in `gen_agf.py` (plus a taller room) -- not
built.

Engine binary used for every DOSBox-X run on this branch: a SNAPSHOT of
the main tree's `build/ags/ags.exe` taken 2026-09-17 14:16 PDT at main
commit 7b7772c (patches through 0097), sha256
54c6f6e36f83bc4b913e36b86451c8f0f7ba6b0086f954c4ebf291467ace6d54
(RUNMANIFEST binary_sha12=a4c5c8b91c53), copied into this worktree's own
gitignored `build/ags/`. Nothing was built in the main tree.

## T2 -- content to spec (done, 2026-09-17)

One room (320x200, 8-bit), all of it drawn by `assets/generate_assets.py`
against one fixed 256-entry palette (16 EGA, 16 greys, a 6x6x6 colour
cube, 8 extras; index 0 transparent in sprites):

- background: a LIGHT brick wall (deliberate -- the glitch-regression
  sprites are judged against it), a window, a wooden floor;
- one hotspot, `hSign` (look / interact / use-inventory handlers);
- one walkable area (the floor) and one WALK-BEHIND, the pillar (baseline
  151: feet above it are drawn behind it);
- one character, `cEgo`, a 4-direction walk view (standing frame + two
  steps per direction, 16x32);
- one inventory item, `iKey`, and the `oKey` room object that gives it;
- twelve `oSpinN` objects (view `VSPINNER`, four frames), all OFF until
  the `anim` scene turns N of them on;
- one GUI, `gMenu` (SAVE / LOAD / CLOSE, slot 1; F5 toggles it), text-only
  buttons -- no GUI art at all;
- one font slot, the OFL TTF, used for everything (GUI, Display, overlays);
- one MIDI clip (`aTune`, the harness's known C D E F G F E C phrase, so
  the Sound gate's pitch-track check applies) and one WAV (`aChime`,
  11025 Hz mono 16-bit -- the DOS mixer's own rate, nothing to resample).

Package size: ~200 KB, of which 118 KB is the TTF.

`RoomTransition` is `Instant`: a fade is N full presents and would land
as stall ticks in every record. `GameFPS` is 40.

## T3 -- AutoPilot + BENCH.CFG scenes (done, 2026-09-17)

`AutoPilot.asc` runs ONE scene per run, armed only under `--test`
(`game.debug_mode`), driven purely by AGS script. AGS script cannot read
the environment, so the harness stages `BENCH.CFG` next to the package
and the module reads it from `$INSTALLDIR$` at `game_start`:

    scene=<idle|walk|anim|text|gui|audio|full>   default full
    hold_ticks=<n>                               default 1000
    objects=<n>      anim: spinners on, 0..12    default 4
    midshot=<0|1>    PH02.BMP at the midpoint    default 0

Log grammar is the AGS Quest harness's, unchanged:
`AUTOPILOT phase=<name> status=<begin|ok|fail> tick=<n> room=<n>`, to
stdout and `$SAVEGAMEDIR$/AUTOPLT.LOG`, plus one `AUTOPILOT config ...`
line echoing what was actually parsed.

| Scene | Pose x | What runs for `hold_ticks` |
|---|---|---|
| `idle` | 40 | nothing: the present-path floor |
| `walk` | 64 | the character loops a rectangle, BEHIND the pillar on the way out and in front of it on the way back |
| `anim` | 88 | N spinners animating at delay 1 (a new frame every 2 ticks) |
| `text` | 112 | a new TTF text overlay every 20 ticks, `SayBackground` every 80 |
| `gui` | 136 | `gMenu` shown/hidden every 20 ticks |
| `audio` | 160 | `aTune` looping, `aChime` every 40 ticks |
| `full` | 184 | look at the sign (WAV + Display), pick up the key, use it on the sign, open the GUI, SAVE via its button, LOAD via its button, close, quit -- phases `look`, `pickup`, `useinv`, `gui`, `save`, `restore` |

Every scene ends the same way: everything forced into a FIXED pose,
40 still ticks, `SaveScreenShot("PH01.BMP")`, `QuitGame` (RUNMANIFEST).
The capture is a CORRECTNESS hash of the final state, identical whatever
the frame rate was. (Changed in T5, see below: the capture is always
`PH01.BMP` and the pose is scene-specific -- the character stands at
x = 40 + 24 * scene -- so every arm has its own hash.) 40 ticks, not a handful: under `DOSAGS_FIXED_TIMESTEP` a slow
machine may render one tick in six and the screenshot copies the last
RENDERED frame. Those 40 ticks are inside the RUNMANIFEST window (4% of a
1000-tick scene): a constant dilution, equal in every arm.

`midshot=1` adds `PH02.BMP` at the window's midpoint -- a motion witness
for a human, never hash-gated (which frame it catches depends on frame
rate) and off by default (a file write inside the window perturbs a
benchmark cell). Looked at on 2026-09-17: the character mid-stride in
profile, twelve spinners with one partly hidden by the pillar, a dark-blue
TTF line on the wall, the grey menu with its three buttons.

Runners: `run-scene.sh <scene> [--hold-ticks N] [--objects N] [--midshot]`
(one scene through `tests/harness/run-dosbox.sh`, fixed timestep on) and
`run-all.sh [--update]` (all seven, gated on each scene's own `ok`, its
shot, `exit_code=0`/`critical_count=0`/`warn_count=0`, and the hash in
`tests/harness/expected/bench8/dosbox-x.json`).

DOSBox-X result, three consecutive full passes (the baseline run and two
re-runs), every scene PASS and hash-identical each time:

    idle/walk/anim/text/gui/audio  tick_rate_steady 39.95-39.98
    full                           tick_rate_steady 40.6-40.9, 3 stall
                                   ticks (two Display() boxes + save/
                                   restore) -- a functional gate, not a
                                   benchmark window

(DOSBox-X numbers are correctness evidence only, never performance.)

### Findings for the 40/40 plan (from these runs; not acted on here)

1. **None of patches 0087-0092 engages on a true 320x200 game in the
   default 640x480 mode.** Every scene, including `idle`, reports
   `presents_real=N presents_skipped=0` and `blit_path fast=0
   generic=N`. 320x200 at 2x is 640x400 -- letterboxed inside 640x480,
   not a full-window destination -- the same precondition failure the
   AGS Quest baseline showed. Trilby's Notes only qualified because the
   engine sees it as 320x240. So on real hardware BENCH8 will pay the
   generic scaled blit plus a full push on every frame until the
   presentation work (unscaled / Mode 13h) lands; that is exactly the
   case it exists to measure.
2. The engine calls `newmusic(0)` unconditionally at start
   (Engine/main/game_start.cpp:73). It finds no old-style `music0` here
   and is a no-op; noted so nobody mistakes the log line for the fixture
   starting audio in a non-audio scene.
3. `Display()` with timer-only skip advances almost no `TickCounter`
   ticks but seconds of wall clock: the new yardstick's stall list
   reports it correctly (3 stall ticks in `full`).

### Not done in this run

- BENCH16 / BENCH32: not built in that run (BENCH16 since done, below).
- T4 (official Linux engine + Wine Editor cross-check), T5 (harness PIN,
  `tests/games/bench/manifest.yaml`, `port_game.py validate` wiring --
  `parse-results.py` still expects AGS Quest's phase list), T6/T7 (real
  hardware) are untouched.
- `make host-tools` was not added to the top-level Makefile (shared with
  the main worker); `build-host-tools.sh` is the entry point.

## Rebase onto main d3c7a4a + newer engine snapshot (2026-09-17)

Branch rebased onto `origin/main` d3c7a4a (run-rig.sh -> run-hw.sh,
hw_guard.py, patches 0096-0098). No conflicts: nothing here touches a
file main changed. Engine snapshot refreshed from main's
`build/ags/ags.exe` (mtime 14:33 PDT, stable across two hashes 5 s
apart, no build running, vendor tree clean at patch 0098): sha256
b47f7e321060140b989f78e9828745d1804dadbc1e6f267fa2f51237f4ceecf7
(binary_sha12=7e00e95d8c41
). `run-all.sh` re-run against it: all seven scenes
PASS, **every hash unchanged** from the 0097-era baseline -- the uclock
clock/pacer (0096) and the TZ fix (0097) change timing, not pixels.

## T5 -- harness + framework wiring (done, 2026-09-17)

Goal: the main worker can run BENCH8 on real hardware through the normal
path without writing anything.

- `tests/games/bench8/manifest.yaml`: arms are SCENES -- `idle`, `walk`,
  `anim4`, `anim12`, `text`, `gui`, `full` -- all on `ACSETUP-OFF.CFG`
  (sound off, as every 40/40 cell is), each staging its committed
  `cfg/<arm>.cfg` as `BENCH.CFG`. Expectations per arm: the `320 x 200
  (8 bit)` line, the echoed `AUTOPILOT config` line (proves the staged
  file was the one read), the scene's own `status=ok` (and `full`'s six
  sub-phases), `shot status=ok`, `audio_vital_status=NA`, exit/critical/
  warn 0, and the PH01.BMP sha256. `auto_exit_tick: 1500` is a safety
  net only; a run that needed it fails the witnesses. The manifest's
  header carries the exact `run-hw.sh` + `check` command lines.
- `tests/harness/packages/bench/PIN`: the source is this repo.
- `build.sh` now also emits `ACSETUP-ON.CFG` / `ACSETUP-OFF.CFG`.

Three small ADDITIVE changes to shared files (nothing existing changes
behaviour; each is inert unless a manifest/caller opts in):

1. `tools/port-game/port_game.py` `validate`: optional
   `validate.arms.<arm>.extra_files: {DOS_NAME: repo-relative source}`,
   staged next to the package under that name (+13 lines).
2. `port_game.py` `validate` and `check`: optional
   `capture_sha256: {NAME.BMP: sha}` in an arm's expected block becomes
   one gating check per named capture; absent file = fail (+15 lines).
3. `tests/harness/parse-results.py`: optional `--scene ARM` -- expected
   phases become `boot, [full's sub-phases], <scene>, shot, quit`, the
   capture list `PH01.BMP`, and the baseline is read from
   `expected/<pkg>/<env>.json[ARM]` (+26 lines). Without `--scene` the
   code path is AGS Quest's, untouched.

`run-hw.sh` is NOT modified. That is why the capture is always
`PH01.BMP` (midshot `PH02.BMP`): names its fixed get-file list already
collects. The cost of one name for all scenes -- a stale capture from
another scene passing by accident -- is what the scene-specific pose
removes. It does not remove a stale capture from the SAME scene, and
`AUTOPLT.LOG` is append-mode: clear `PH*.BMP` and `AUTOPLT.LOG` on the
target before each cell (the manifest header says so too).

Gate, met: `port_game.py validate --arm all` from the manifest alone --
**PASS, 7/7 arms**, recorded via `record` as `results/B8V-DOSBOX.json`
and the manifest's first `validated:` entry.

Checks that the checks work: (a) the first validate run FAILED `anim4`
on exactly `capture:PH01.BMP` while it still carried `anim12`'s hash --
the capture check discriminates 4 spinners from 12; the anim4 capture
was then looked at (4 spinners, character at x=88) before its hash went
in. (b) `parse-results.py --scene idle` against a `walk` run dir FAILS
(`missing=['idle']`, hash mismatch). (c) AGS Quest regression: its
package run through the unchanged default path on the same 0098 engine
-- `PASS -- all phases ok`, 18 phases, its three captures matching its
own committed baseline.

`run-all.sh` remains as the developer gate over all eight cfg files
(the seven arms plus `audio` with sound on, which the manifest leaves
out: under DOSBox-X its `underruns=` count varies run to run, 0-10, an
emulator-timing artefact that would make a gated expectation flaky).

Two observations for the main worker, not acted on:

- `full` reports `tick_rate_steady` 43.4-43.8 -- above 40 + 2%. It is a
  ~45-tick run with 3 stall ticks (two Display() boxes and the
  save/restore); the steady figure divides the few non-stall ticks by a
  window whose edges the stall exclusion rounds. Probably a small-sample
  artefact of the steady-rate arithmetic rather than a fast pacer (the
  six 1000-tick arms sit at 40.01-40.09), but it is the pacer slice's
  own correctness rule that the rate must not exceed 40, so it is worth
  one look by whoever owns patch 0093/0096. `full` is a functional
  gate; do not read a rate from it.
- Whole-run `tick_rate` for the 1000-tick arms is 38.7-39.2 under
  DOSBox-X: below the 40 +/- 2% band that "both figures must pass"
  demands, from ~0.65 s of pre-loop startup inside the runtime window
  plus 40 settle ticks. On real hardware the pre-loop share will be
  larger. A longer `hold_ticks` dilutes it; whether the gate should be
  judged on a longer window is the operator's call, not this fixture's.

## T4 step 1 -- the official Linux engine (done, 2026-09-17)

Reference: AGS's own prebuilt Linux engine from the pinned release's own
page, https://github.com/adventuregamestudio/ags/releases/tag/v3.6.3.13 --
asset `ags_3.6.3.13_linux.tar.gz`, 11,216,514 bytes, sha256
`5270d78cc5b56db379e6e242ccce86512163a8460769b4f6e8832e19a69f7c9a`. The
URL and digest were read from GitHub's release API for that tag, not
recalled; the copy already on this host (`/tmp/ags-linux.tar.gz`, from
the seventh session) hashes to exactly that digest, so it was reused
rather than re-fetched. `data/ags64` reports "Engine version 3.6.3.13,
64-bit LE" (sha256 41f3f9e034c4...). Not vendored.

`run-linux-ref.sh <arm>` runs the SAME `BENCH8.ags` the DOS engine runs
(`--gfxdriver software --windowed --test`, private Xvfb :233, SDL dummy
audio) and compares PH01.BMP with the DOS baseline.

Result: `full` quits cleanly (exit 0) with every phase ok at the SAME
ticks as the DOS run (look 1, pickup 2, useinv 3, gui/save/restore 3,
shot 43), and its capture is **sha256-identical to the DOS port's**. So
are `idle`, `walk`, `anim4`, `anim12`, `text` and `gui` -- seven of
seven arms, byte-for-byte, between an independent desktop engine and
dosags under DOSBox-X. The headless pipeline's package is a valid AGS
game, and the DOS port renders it exactly as upstream does (TTF text,
walk-behind, GUI, save/restore included).

Behavioural differences seen, none affecting the game:
- the reference picks `960 x 600 (32-bit) windowed` (3x desktop scaling
  of the 320x200 virtual screen); dosags picks `640 x 480 (8-bit)`. The
  capture is the 8-bit virtual screen either way, hence identical.
- the reference logs one `OpenAL Error: AL_INVALID_OPERATION` at the
  restore, an artefact of its mojoAL layer on SDL's dummy audio driver;
  dosags has no OpenAL layer at all.
- the reference writes `warnings.log` into its working directory.

Not done: step 2 (the same source compiled by the Wine Editor and
compared via `inspect`), by instruction.

## BENCH16 -- HighColor build (done, 2026-09-17)

`build.sh --depth 16`: same content, `<ColorDepth>HighColor</ColorDepth>`,
sprites exported as 32-bit RGBA, the background as 24-bit RGB, plus the
two glitch-regression objects appended after the spinners (`oGlitchA`
slot 40, a real alpha channel; `oGlitchM` slot 41, magenta-keyed with
checkerboard edges), both on the light wall between pillar and sign.
Boots: `Game native resolution: 320 x 200 (16 bit)`, `640 x 480
(16-bit)`, all eight arms ok, exit/critical/warn 0.

**The first BENCH16 capture was WRONG, and only looking at it showed
it**: black boxes around the character, cursor and key, and the magenta
sprite drawn as a solid magenta square. Cause: OUR asset generator, not
the engine. It exported transparent pixels as RGBA (0,0,0,0) and the
keyed sprite's background as opaque (255,0,255,255). A sprite flagged
`AlphaChannel="False"` has its alpha ignored, so (0,0,0,0) is opaque
black; and the engine keys a non-alpha 32-bit sprite on exactly
0x00FF00FF -- magenta WITH alpha byte 0 (Engine/ac/draw.cpp
PrepareSpriteForUseImpl -> ConvertBitmap(keep_mask); Allegro's
MASK_COLOR_32) -- so opaque magenta is just magenta. Fixed in
`generate_assets.py` (`MASK_RGBA = (255, 0, 255, 0)`); the 8-bit path
never used that function, and BENCH8's hashes are unchanged (re-checked).
This is the same DATA defect class as the AGS Quest black-box report
(PLAN.md 2026-09-16), now reproduced and fixed in a pipeline we own --
and the reason a headless sprite pipeline must write the mask colour
itself: the Editor does it at import, `spritepak` stores what it is given.

After the fix, looked at again: no boxes; the alpha sprite is a
hard-edged blue disc with wall visible all round it (alpha thresholded
at 50% by ReplaceHalfAlphaWithRGBMask -- correct for a 16-bit game, no
soft edge is possible); the keyed sprite is red with the brick wall and
a mortar line showing through its checkerboard edges, no magenta fringe.
That capture is the standing regression for the engine's load-time
alpha-to-mask path.

Baseline: `tests/harness/expected/bench16/dosbox-x.json` (eight arms).
Reference engine, `run-linux-ref.sh <arm> --depth 16`: `idle`, `anim12`
and `full` are sha256-IDENTICAL to the DOS port's captures -- so the
16-bit sprite preparation (32 -> 16 conversion, mask keying, alpha
threshold) is bit-exact with upstream on DJGPP.

Same finding as BENCH8: `blit_path fast=0`, `presents_skipped=0` at
16-bit too. No manifest for bench16 yet (copy bench8's with the depth-16
hashes when it is wanted); BENCH32 not built.
