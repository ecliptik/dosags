# tools/port-game -- Game porting framework

Turns a third-party AGS game binary into a runnable DOS package plus a
validation record. See `PLAN.md`'s "Game porting framework" section for
the full six-stage design (`inspect -> convert -> repack -> layout ->
validate -> record`). `inspect`/`convert`/`repack`/`layout` were built
2026-09-13 for the Sound milestone's S7 acceptance-gate item 4 (in-profile
fps ABBA) -- see `tests/games/trilbysnotes/` for the first real golden
reference this produced, entirely by hand through what `validate`/
`record` (added 2026-09-15) now generalize: those two stages used to be
hand-typed flags to `tests/harness/run-dosbox.sh` (its `--include-extra`/
`--env` flags) plus a hand-edited `manifest.yaml` -- now driven by that
same manifest's own `validate:` block instead. `all` chains every stage
from one manifest.

Game data itself is never committed (see each game's own `PIN` file for
its licensing/source pin) -- only this tool, `manifest.yaml`, and
`*-report.json`/`results/*.json` outputs.

## Usage

```
python3 port_game.py inspect  <game-file> [--json OUT.json]
python3 port_game.py convert  <game-file> --workdir DIR
python3 port_game.py repack   <game-file> --workdir DIR --out OUT.ags
python3 port_game.py layout   OUT.ags --dest DIR --name NAME8 --sound on|off
python3 port_game.py validate --manifest tests/games/<id>/manifest.yaml --layout-dir DIR [--arm <arm-name>|all]
python3 port_game.py check    --manifest tests/games/<id>/manifest.yaml --arm <arm-name> --run-dir DIR [--log PATH] [--json OUT.json]
python3 port_game.py record   --manifest tests/games/<id>/manifest.yaml --validate-json REPORT.json --tag TAG [--environment HW-486-66]
python3 port_game.py all      <game-file> --workdir DIR --dest DIR --name NAME8 --manifest tests/games/<id>/manifest.yaml
```

`<game-file>` is either a standalone `.ags`, or a Windows `.exe` with a
CLIB appended (AGS's "single EXE" distribution shape) -- `clib.py`'s
`read_header()` finds the signature either way, the same as the real
engine's own `MFLUtil::ReadSigsAndVersion`.

`convert` extracts every asset to `<workdir>/assets/`, host-transcoding
(via `ffmpeg`) only clips `inspect`'s own classifier flags as needing it
(OGG/MP3; tracker formats per decision 5, once vendored). WAV/VOC/MIDI
pass through byte-for-byte unchanged -- this port's own DOS-side loaders
(`dos_audio_decode.cpp`, `dos_midi_backend`) already sniff format and
resample/downmix to the mixer's Tier-2 rate once, at load time, so there
is no host-side resampling step to perform. This is a real,
source-verified correction to this framework's original design (which
assumed WAV/VOC above the tier rate needed a host-side resample) --
confirmed against `patches/ags/0050`'s own header comment, not guessed.

`repack` always writes a fresh V30-format CLIB (`clib.py`'s
`write_v30()`) regardless of the source game's own original version --
`multifilelib.cpp` itself only ever writes V30 (`WriteHeader` calls
`WriteV30` unconditionally for the base datafile), and the pinned
engine's `ReadHeader()` reads any supported version on load, so
re-emitting V30 is not a compatibility concern for this port's own build.

**A sibling `audio.vox`/`speech.vox` (2026-09-15).** Modern AGS ships
audio as its own SEPARATE CLIB file sitting next to the main `.ags`, not
only as assets embedded in the main file's own CLIB -- confirmed against
two real 2021/2023-compiled 32-bit games (Shards of God: 21 clips in a
99 MB `audio.vox`; IOAWN4T: 235 clips in a 97 MB `audio.vox`, ALL of them
OGG). `trilbysnotes`, this framework's original golden reference, embeds
its 30 clips directly and has no separate vox file at all, so this shape
went completely unexercised until these two games surfaced it -- every
stage was silently blind to a sibling vox's existence: `inspect` never
looked for one, `convert`/`repack` never touched it, and `layout` never
staged it, so a package built for a game shaped this way silently shipped
with no audio.vox content whatsoever (not even the mechanically-copied,
un-transcoded original -- it was never referenced at all). Fixed:
`find_sibling_vox()` looks for a case-insensitive `audio.vox`/`speech.vox`
next to `<game-file>` on disk; if found, `inspect` reports its own asset
list under `sibling_vox` (so this is visible up front, not a silent
surprise), `convert` transcodes/passes through its clips into
`<workdir>/assets_vox/` exactly like the main file's own assets, `repack`
rebuilds it as a second fresh V30 CLIB written next to `--out` under its
original name (uppercased, e.g. `AUDIO.VOX`), and `layout` copies that
file into `--dest` alongside `<NAME8>.ags` -- found by convention (a file
named `AUDIO.VOX`/`SPEECH.VOX` next to `repacked_ags`), no new CLI flag on
any stage. An EMBEDDED audio.vox/speech.vox asset (the older AGS shape --
still what `has_audio_vox`/`has_speech_vox` in `inspect`'s report means)
remains out of scope: no real example of that shape has been ported here
yet, so it stays a known, named gap rather than a guessed fix.

`layout` emits `<NAME8>.ags` (and a sibling `AUDIO.VOX`/`SPEECH.VOX` if
`repack` wrote one, see above) plus one `ACSETUP-ON.CFG`/`ACSETUP-OFF.CFG`
variant per call (`--sound on`/`--sound off`) -- toggling `[sound]
enabled=` (`Engine/main/config.cpp:416`), a real, already-shipping,
zero-patch engine feature, not a new lever. A caller stages whichever
variant an ABBA arm needs as the target's actual `ACSETUP.CFG` via
`run-dosbox.sh --include-extra`/`run-hw.sh --extra-file` (both added
alongside this tool) -- `layout` itself does not know which arm is
"current", only how to produce both.

`validate` drives `tests/harness/run-dosbox.sh` (DOSBox-X boot +
`DOSAGS_TAS_AUTO_EXIT_TICK`, patch 0044) per the manifest's own
`validate:` block -- `pkg` (the `tests/harness/games/<pkg>/` convention),
`auto_exit_tick`, `timeout_s`, and one `arms.<sound_on|sound_off>` entry
per ABBA arm (its ACSETUP variant + any extra env like
`SDL_HINT_DOS_AUDIO_BACKEND`). It renames the chosen `ACSETUP-*.CFG` to
the engine's expected `ACSETUP.CFG` before staging (run-dosbox.sh's own
`--include-extra` only uppercases a filename, it never renames one), then
checks the resulting RUNMANIFEST's `exit_code`/`critical_count`/
`warn_count`/`audio_vital_status` against the manifest's own
`expected_runmanifest_dosbox_x.<arm>`. A `validate:` block must already
exist in the manifest -- see `tests/games/trilbysnotes/manifest.yaml`'s
own for the pattern; this tool never invents a driving recipe.

Binary-only games (every current golden reference except AGS Quest) have
no AutoPilot module, so there is no in-script screenshot call to hash yet
-- `capture_hash` is `null`/"unavailable" for them rather than invented,
and pass/fail is RUNMANIFEST-only, not phase-based.

**Fixed timestep is on by default for every arm (2026-09-16).**
`validate` sets `DOSAGS_FIXED_TIMESTEP=1` (patch 0047) unless the
manifest's `validate:` block says `fixed_timestep: false`, and then
checks the engine's OWN one-time log line in `STDOUT.TXT`
(`DOS-PORT fixed-timestep: ENABLED` / `DISABLED`) rather than trusting
that the `SET` reached `AGS.EXE` -- the `checks.fixed_timestep` entry.
Before this, the generalized path never set it while every hand-run KPI
cell did, so a manifest-driven run would have measured slow gameplay,
not low fps (PLAN.md "Fixed timestep and the fps KPI", and the
2026-09-16 "Fixed timestep in benchmarking -- review"). The same run
also parses patch 0048's `DOS-PORT tick_rate=<r> frames_skipped=<n>`
and patch 0043's `memory_min_free_kb` lines into the `runmanifest`
dict, and `record` writes `tick_rate`/`frames_skipped`/`fps_p95`/
`binary_sha12` into the `validated:` entry -- previously typed by hand.
A non-gating `game_speed_40hz` check (tick_rate within 40 +/- 2%, the
KPI's hard game-speed bar) is reported on every run so the number is
never silently absent; it is informational on DOSBox-X and becomes a
campaign's own acceptance criterion on real hardware.

**Arm names are the manifest's own.** `--arm` accepts any key of
`validate.arms` (`sound_on`/`sound_off` for a Sound-gate manifest,
`depth_32_native`/`depth_16_forced` for the color-depth ones in
`tests/games/shards/` and `tests/games/iowna/`), or `all`. An arm's
expected block may carry `stdout_contains: [..]` -- substrings that
must appear in `STDOUT.TXT`, used to witness a `DOSAGS_FORCE_COLOR_DEPTH`
arm from the engine's own `Graphics mode set: ... (N-bit)` line instead
of the requested env var (the 32-bit KPI campaign's own rule, now
mechanical).

**`check` -- a real-hardware run enters the record through the tool.**
`check --manifest M --arm A --run-dir DIR [--log PATH] --json OUT`
applies exactly `validate`'s checks to a run that already happened (a
`run-hw.sh` collected dir, or a `tests/games/<id>/results/` record
holding `<TAG>.LOG` + `*STDOUT*.TXT`) and emits the JSON `record
--environment HW-486-66` consumes. First proven against the S32B7
Shards of God real-hardware logs from 2026-09-15. This is the
framework gate's "real-hardware `results/` record" path -- no second,
hand-typed route.

**Former known gap, closed 2026-09-16.** The hub's `dosbox-run.sh` used
to offer only its `--fast`/parity confs (both `oplmode=none` by design),
so a sound-on arm needing real OPL3 chip detection could not be
reproduced from a manifest. The hub now takes `--conf PATH` (pulled into
`.sdl-dos-ports/`), `run-dosbox.sh` passes it through, and a manifest
names its conf with `validate: dosbox_conf: <repo-relative path>` --
Trilby's Notes uses `tests/harness/confs/dosbox-x-fast-opl3.conf`, this
port's own copy of the fast conf with `oplmode=opl3`. A manifest without
`dosbox_conf` runs on the stock `--fast` conf exactly as before, and an
`audio_vital_status` mismatch is still reported honestly, never forced.

`record` appends one validate run to the manifest's `validated:` list, in
the exact hand-written style already established there, plus a raw
`results/<tag>.json`. It appends via plain text rather than a YAML
load+dump round trip -- these manifests are hand-annotated with extensive
`#` comments a `safe_load()`/`safe_dump()` round trip would silently
discard, and `validated:` is always the file's last top-level section in
every manifest this framework has produced so far.

`all` chains every stage from one manifest: inspect, convert, repack,
layout (twice, sound on/off), stages the package where
`run-dosbox.sh`/`run-hw.sh` expect it
(`tests/harness/games/<pkg>/*.ags`), then validate, then record.

## `clib.py`

Read/write support for AGS's MFL ("CLIB") asset library format,
transcribed directly from `vendor/ags/Common/data/multifilelib.cpp`
(read: SingleLib/V10/V11/V15/V20/V30; V21's RNG-keyed encryption is the
one real gap -- no golden reference has needed it yet). Verified against
a real shipped game (Trilby's Notes, lib_version 15) by round-tripping
the whole CLIB and diffing every one of its 78 assets byte-for-byte
against the original before trusting the tool -- not just "it ran
without error."
