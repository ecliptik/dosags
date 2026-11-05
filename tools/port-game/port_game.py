#!/usr/bin/env python3
"""port_game.py -- the Game porting framework's full pipeline (PLAN.md,
"Game porting framework" section): inspect -> convert -> repack -> layout
-> validate -> record, turning a third-party AGS game binary into a
runnable DOS package plus a validation record. The first four stages
extract/rebuild/lay out the package; `validate`/`record` generalize what
was previously hand-typed flags to tests/harness/run-dosbox.sh (see that
script's own --include-extra/--env flags, added alongside this tool) into
subcommands driven by a per-game manifest (tests/games/<id>/manifest.yaml)
instead -- see that manifest's own `validate:` block for the schema, and
tests/games/trilbysnotes/ for the first golden reference this generalizes
from (built by hand through the ad-hoc process this tool now automates).

Subcommands (each also runnable standalone; `all` chains them):
  inspect  <game-file>                    -- survey, prints a JSON report
  convert  <game-file> --workdir DIR       -- extract + host-transcode assets
  repack   <game-file> --workdir DIR --out OUT.AGS
                                           -- rebuild a single V30 CLIB
  layout   <repacked.ags> --dest DIR --name NAME8 --sound on|off
                                           -- DOS-directory-ready package
  validate --manifest M --layout-dir DIR  -- DOSBox-X boot + auto-exit-tick
                                              + RUNMANIFEST check, per the
                                              manifest's own `validate:` block
  record   --manifest M --validate-json J --tag T
                                           -- append a validated: entry +
                                              a results/<tag>.json record
  all      <game-file> --workdir DIR --dest DIR --name NAME8 --manifest M
                                           -- inspect, then convert+repack,
                                              then layout twice (sound
                                              on/off), then validate, then
                                              record -- one manifest in,
                                              a package + validation
                                              record out

License: MIT (this file, dosags's own tooling). See LICENSE in repo root.
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

import clib

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# main_game_file.cpp's own version gates -- see inspect_report()'s own
# docstring-length citation in the "inspect" subcommand below.
GAME_VERSION_250 = 18
GAME_VERSION_320 = 41

AUDIO_EXTENSIONS = {
    ".mid": ("midi", "native passthrough (SMF, dos_midi_backend)"),
    ".rmi": ("midi", "native passthrough (RIFF-wrapped SMF)"),
    ".wav": ("pcm", "native passthrough (RIFF WAV, dos_audio_decode sniffs+resamples at load)"),
    ".voc": ("pcm", "native passthrough (Creative VOC, dos_audio_decode sniffs+resamples at load)"),
    ".ogg": ("compressed", "needs host transcode (ffmpeg) -- OGG has no DOS decoder"),
    ".mp3": ("compressed", "needs host transcode (ffmpeg) -- MP3 has no DOS decoder"),
    ".xm": ("tracker", "decision 5: native decode via libxmp-lite (not yet vendored)"),
    ".it": ("tracker", "decision 5: native decode via libxmp-lite (not yet vendored)"),
    ".s3m": ("tracker", "decision 5: native decode via libxmp-lite (not yet vendored)"),
    ".mod": ("tracker", "decision 5: native decode via libxmp-lite (not yet vendored)"),
}
FONT_EXTENSIONS = {".wfn": "native bitmap font (WFNFont)", ".ttf": "TrueType (alfont/FreeType path)"}


def classify_audio(name: str):
    lower = name.lower()
    for ext, (kind, note) in AUDIO_EXTENSIONS.items():
        if lower.endswith(ext):
            return kind, note
    return None, None


def find_main_asset(lib):
    for cand in ("ac2game.dta", "game28.dta"):
        matches = [a for a in lib.assets if a.file_name.lower() == cand]
        if matches:
            return matches[0]
    return None


def find_sibling_vox(game_file):
    """Looks for a sibling audio.vox/speech.vox file sitting next to
    game_file on disk (case-insensitive) -- distinct from an EMBEDDED
    audio.vox/speech.vox asset inside game_file's own CLIB (the
    has_audio_vox/has_speech_vox fields below, an older AGS packaging
    shape trilbysnotes -- this framework's original golden reference --
    happens not to use either way). Modern AGS ships audio.vox as its
    OWN separate CLIB file next to the main .ags: confirmed by reading
    two real 2021/2023-compiled 32-bit games this session (Shards of
    God, IOAWN4T), both of which have a real, load-bearing audio.vox
    (99/97 MB) the engine actively opens ("audio.vox found and
    initialized") and that itself contains further OGG-compressed clips
    needing the exact same host-transcode treatment as any clip embedded
    in the main file. convert/repack/layout used to be completely blind
    to this file's existence -- inspect never looked for it, so a game
    shaped this way silently shipped a package missing all of its
    audio.vox content until someone noticed by hand. Returns the sibling
    path, or None if game_file has no such neighbor."""
    game_dir = os.path.dirname(os.path.abspath(game_file))
    try:
        entries = os.listdir(game_dir)
    except OSError:
        return None
    for name in entries:
        if name.lower() in ("audio.vox", "speech.vox"):
            return os.path.join(game_dir, name)
    return None


def find_lib_volumes(game_file, lib):
    """Locates the sibling data-volume files a multi-part CLIB's non-zero
    LibUid assets actually live in (multifilelib.cpp's ReadHeader only
    adds the base file's own abs_offset to LibUid==0 assets -- ANY other
    LibUid's Offset is a plain offset into ITS OWN separate physical file,
    named by lib.lib_file_names[uid], never into game_file's own bytes).
    This is the old floppy-disk-splitting shape (multiple Maniac.NNN
    volumes next to Maniac.exe) -- unexercised by every golden reference
    before Maniac Mansion Deluxe, so convert/repack were silently blind
    to it exactly like find_sibling_vox() once was for audio.vox: they
    read `data[a.offset:a.offset+a.size]` from the base file's own bytes
    unconditionally, which is only correct for LibUid==0.

    Same case-insensitive sibling-file lookup style as find_sibling_vox().
    Returns {lib_uid: bytes} for every non-zero LibUid actually used by
    `lib`'s assets; raises FileNotFoundError (not silently) if a required
    volume is missing next to game_file."""
    needed_uids = sorted({a.lib_uid for a in lib.assets if a.lib_uid != 0})
    if not needed_uids:
        return {}
    game_dir = os.path.dirname(os.path.abspath(game_file))
    entries_by_lower = {name.lower(): name for name in os.listdir(game_dir)}
    volumes = {}
    for uid in needed_uids:
        want_name = lib.lib_file_names[uid]
        actual_name = entries_by_lower.get(want_name.lower())
        if actual_name is None:
            raise FileNotFoundError(
                f"find_lib_volumes: CLIB references volume {uid} "
                f"({want_name!r}) but no such file sits next to {game_file}")
        with open(os.path.join(game_dir, actual_name), "rb") as f:
            volumes[uid] = f.read()
    return volumes


def _convert_lib_assets(data, lib, assets_dir, tier_rate, volumes=None):
    """Shared per-asset convert loop -- extracted so cmd_convert can run
    it once for the main game file and, if find_sibling_vox() finds one,
    a second time for that sibling CLIB, with no logic duplicated between
    the two calls. `volumes` (see find_lib_volumes()) supplies the bytes
    for any asset whose LibUid != 0 -- `data` alone only ever covers
    LibUid==0 assets."""
    os.makedirs(assets_dir, exist_ok=True)
    volumes = volumes or {}
    report = {"transcoded": [], "passthrough": [], "skipped": []}
    for a in lib.assets:
        lower = a.file_name.lower()
        if lower in ("audio.vox", "speech.vox"):
            # Only reachable for a MAIN game file that embeds one
            # (older AGS packaging) -- a vox file's own assets never
            # nest another vox inside it.
            report["skipped"].append(a.file_name)
            continue
        buf = data if a.lib_uid == 0 else volumes[a.lib_uid]
        raw = buf[a.offset:a.offset + a.size]
        out_path = os.path.join(assets_dir, a.file_name)
        kind, _note = classify_audio(a.file_name)
        if kind in ("compressed",):
            wav_path = os.path.splitext(out_path)[0] + ".wav"
            src_path = out_path + ".src"
            with open(src_path, "wb") as f:
                f.write(raw)
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", src_path,
                 "-ar", str(tier_rate), "-ac", "1", "-c:a", "pcm_s16le", wav_path],
                check=True)
            os.remove(src_path)
            new_name = os.path.basename(wav_path)
            report["transcoded"].append({"from": a.file_name, "to": new_name})
        else:
            with open(out_path, "wb") as f:
                f.write(raw)
            report["passthrough"].append(a.file_name)
    return report


def _repack_lib(data, lib, assets_dir, rename_map, out_path):
    """Shared repack loop -- extracted so cmd_repack can run it once for
    the main game file and, if convert recorded a sibling_vox, a second
    time for that sibling's own repacked output."""
    assets_with_data = []
    for a in lib.assets:
        if a.file_name.lower() in ("audio.vox", "speech.vox"):
            continue
        name = rename_map.get(a.file_name, a.file_name)
        path = os.path.join(assets_dir, name)
        with open(path, "rb") as f:
            assets_with_data.append((name, f.read()))
    clib.write_v30(lib.lib_file_names, assets_with_data, out_path)
    return assets_with_data


def build_report(data: bytes, tier_rate: int, source_file: str):
    lib = clib.read_header(data)
    main_asset = find_main_asset(lib)
    if main_asset is None:
        raise SystemExit("port_game.py: FATAL -- no ac2game.dta/game28.dta asset found in this CLIB")
    header = clib.read_main_game_file_header(data, main_asset.offset)
    data_version = header["data_version"]

    report = {
        "source_file": source_file,
        "clib": {"lib_version": lib.lib_version, "base_file_offset": lib.base_file_offset,
                 "asset_count": len(lib.assets), "lib_file_names": lib.lib_file_names},
        "game": {"name": header["gamename"], "data_version": data_version,
                 "compiled_with_editor": header["compiled_with"]},
        "loadable": data_version >= GAME_VERSION_250,
        "legacy_audio_system": data_version < GAME_VERSION_320,
        "audio_clips": [],
        "fonts": [],
        "has_audio_vox": any(a.file_name.lower() == "audio.vox" for a in lib.assets),
        "has_speech_vox": any(a.file_name.lower() == "speech.vox" for a in lib.assets),
        "other_assets": [],
    }
    for a in lib.assets:
        kind, note = classify_audio(a.file_name)
        if kind:
            report["audio_clips"].append({"file_name": a.file_name, "size": a.size, "kind": kind, "note": note})
            continue
        lower = a.file_name.lower()
        if lower in ("audio.vox", "speech.vox"):
            continue
        matched = False
        for ext, fnote in FONT_EXTENSIONS.items():
            if lower.endswith(ext):
                report["fonts"].append({"file_name": a.file_name, "size": a.size, "note": fnote})
                matched = True
                break
        if not matched:
            report["other_assets"].append({"file_name": a.file_name, "size": a.size})

    sibling_vox_path = find_sibling_vox(source_file)
    if sibling_vox_path:
        vox_data = open(sibling_vox_path, "rb").read()
        vox_lib = clib.read_header(vox_data)
        vox_clips = []
        for a in vox_lib.assets:
            kind, note = classify_audio(a.file_name)
            if kind:
                vox_clips.append({"file_name": a.file_name, "size": a.size, "kind": kind, "note": note})
        report["sibling_vox"] = {
            "file_name": os.path.basename(sibling_vox_path),
            "asset_count": len(vox_lib.assets),
            "audio_clips": vox_clips,
        }
    else:
        report["sibling_vox"] = None
    return lib, report


def cmd_inspect(args):
    data = open(args.game_file, "rb").read()
    _lib, report = build_report(data, args.tier_rate, args.game_file)
    text = json.dumps(report, indent=2)
    if args.json:
        with open(args.json, "w") as f:
            f.write(text)
    print(text)
    return report


def cmd_convert(args):
    """Extracts every real asset (skipping an audio.vox/speech.vox
    EMBEDDED inside game_file's own CLIB -- the older AGS packaging shape
    this framework's original golden reference, trilbysnotes, doesn't
    even use, so that case stays unhandled/out of scope here) to
    <workdir>/assets/<name>, host-transcoding only the ones inspect's own
    classify_audio() flags as "compressed"/"tracker" (ffmpeg for OGG/MP3;
    tracker files are passed through unconverted for now -- decision 5's
    native-decode path has no host-side conversion step at all, see S6).
    Everything else (midi/pcm/fonts/rooms/sprites/the main .dta) is
    copied byte-for-byte unchanged: this port's own DOS-side loaders
    (dos_audio_decode.cpp, dos_midi_backend) already sniff format and
    resample/downmix WAV/VOC to the mixer's Tier-2 rate ONCE, at load
    time -- there is no host-side resampling step to perform, a real
    correction against this port-game framework's own original PLAN.md
    design (written before S1 existed), not a guess.

    If find_sibling_vox() finds a SEPARATE audio.vox/speech.vox file next
    to game_file (the modern-AGS shape both Shards of God and IOAWN4T
    actually use, and this framework's own real gap until 2026-09-15),
    that file's assets are converted too, into <workdir>/assets_vox/,
    recorded under convert_report["sibling_vox"] so cmd_repack knows to
    rebuild it as its own sibling CLIB rather than silently dropping it."""
    data = open(args.game_file, "rb").read()
    lib = clib.read_header(data)
    assets_dir = os.path.join(args.workdir, "assets")
    volumes = find_lib_volumes(args.game_file, lib)
    convert_report = _convert_lib_assets(data, lib, assets_dir, args.tier_rate, volumes)
    if volumes:
        convert_report["lib_volumes"] = {uid: lib.lib_file_names[uid] for uid in sorted(volumes)}

    sibling_vox_path = find_sibling_vox(args.game_file)
    if sibling_vox_path:
        vox_data = open(sibling_vox_path, "rb").read()
        vox_lib = clib.read_header(vox_data)
        vox_assets_dir = os.path.join(args.workdir, "assets_vox")
        vox_report = _convert_lib_assets(vox_data, vox_lib, vox_assets_dir, args.tier_rate)
        convert_report["sibling_vox"] = {
            "source_file": sibling_vox_path,
            "output_name": os.path.basename(sibling_vox_path).upper(),
            **vox_report,
        }

    report_path = os.path.join(args.workdir, "convert-report.json")
    with open(report_path, "w") as f:
        json.dump(convert_report, f, indent=2)
    print(json.dumps(convert_report, indent=2))
    return convert_report


def cmd_repack(args):
    """Rebuilds a single standalone V30 CLIB from <workdir>/assets/ in the
    ORIGINAL game's own directory order (asset names/order come from
    re-reading game_file's own CLIB header -- convert.py's transcode step
    may have renamed an asset's extension, e.g. music.ogg -> music.wav;
    repack follows that rename via convert-report.json rather than
    assuming the name never changes).

    If convert-report.json carries a "sibling_vox" entry (see cmd_convert),
    that sibling is rebuilt too, as its own fresh V30 CLIB written next to
    --out under its original filename (uppercased, e.g. AUDIO.VOX) --
    cmd_layout picks it up from there by convention, no extra flag needed."""
    data = open(args.game_file, "rb").read()
    lib = clib.read_header(data)
    assets_dir = os.path.join(args.workdir, "assets")
    convert_report_path = os.path.join(args.workdir, "convert-report.json")
    convert_report = {}
    if os.path.exists(convert_report_path):
        with open(convert_report_path) as f:
            convert_report = json.load(f)
    rename_map = {e["from"]: e["to"] for e in convert_report.get("transcoded", [])}

    assets_with_data = _repack_lib(data, lib, assets_dir, rename_map, args.out)
    print(f"port_game.py repack: wrote {args.out} "
          f"({len(assets_with_data)} assets, {os.path.getsize(args.out)} bytes)")

    sibling = convert_report.get("sibling_vox")
    if sibling:
        vox_data = open(sibling["source_file"], "rb").read()
        vox_lib = clib.read_header(vox_data)
        vox_assets_dir = os.path.join(args.workdir, "assets_vox")
        vox_rename_map = {e["from"]: e["to"] for e in sibling.get("transcoded", [])}
        vox_out = os.path.join(os.path.dirname(os.path.abspath(args.out)), sibling["output_name"])
        vox_assets = _repack_lib(vox_data, vox_lib, vox_assets_dir, vox_rename_map, vox_out)
        print(f"port_game.py repack: wrote {vox_out} "
              f"({len(vox_assets)} assets, {os.path.getsize(vox_out)} bytes) [sibling vox]")


ACSETUP_TEMPLATE = """[sound]
digiid=-1
midiid=-1
digiwin=1096302880
midiwin=-1
digiindx=0
midiindx=0
digiwinindx=0
midiwinindx=0
enabled={enabled}

[misc]
gamecolordepth=8
defaultres=1
screenres=0
letterbox=0
windowed=0
refresh=0
"""


def _name8(name):
    """Normalizes a base name to the <NAME8>.ags this framework's own
    tooling + tests/harness/run-dosbox.sh/run-hw.sh (their case-sensitive
    AGS_PKG=("$GAMES_DIR"/*.ags) glob) expect -- strips a redundant .AGS
    the caller might have included, then appends lowercase .ags (DOS 8.3
    itself is case-insensitive either way; every existing package,
    AGSQuest.ags, already matches this convention). Shared by cmd_layout
    and cmd_all so the two never compute this differently."""
    base = name.upper()
    if base.endswith(".AGS"):
        base = base[:-4]
    name8 = base + ".ags"
    if len(name8) > 12:
        raise SystemExit(f"port_game.py: {name8!r} is not 8.3-safe")
    return name8


def cmd_layout(args):
    """Produces: <dest>/<NAME8>.AGS (the repacked package, copied),
    <dest>/AUDIO.VOX or SPEECH.VOX if cmd_repack wrote one alongside
    repacked_ags (a sibling vox travels with the package it belongs to --
    found next to repacked_ags by convention, not a new CLI flag), and
    <dest>/ACSETUP-<SOUND>.CFG (this port-game framework's own naming --
    tests/harness/run-dosbox.sh's --include-extra / run-hw.sh's
    --extra-file, both added alongside this tool, stage whichever variant
    an ABBA arm needs as plain ACSETUP.CFG on the target). Config.cpp's
    own `setup.AudioEnabled = CfgReadBoolInt(cfg, "sound", "enabled", ...)`
    (Engine/main/config.cpp:416) is a real, already-shipping, zero-patch
    audio on/off lever -- confirmed by reading the engine source, not
    assumed -- which is why this tool needs no engine patch at all for
    the acceptance gate's sound-on/sound-off arms."""
    os.makedirs(args.dest, exist_ok=True)
    name8 = _name8(args.name)
    out_ags = os.path.join(args.dest, name8)
    shutil.copyfile(args.repacked_ags, out_ags)

    repacked_dir = os.path.dirname(os.path.abspath(args.repacked_ags))
    vox_out = None
    for cand in ("AUDIO.VOX", "SPEECH.VOX"):
        cand_path = os.path.join(repacked_dir, cand)
        if os.path.exists(cand_path):
            vox_out = os.path.join(args.dest, cand)
            shutil.copyfile(cand_path, vox_out)
            break

    enabled = "1" if args.sound == "on" else "0"
    cfg_name = f"ACSETUP-{args.sound.upper()}.CFG"
    cfg_path = os.path.join(args.dest, cfg_name)
    with open(cfg_path, "w", newline="\r\n") as f:
        f.write(ACSETUP_TEMPLATE.format(enabled=enabled))

    vox_msg = f", {vox_out}" if vox_out else ""
    print(f"port_game.py layout: wrote {out_ags}{vox_msg} and {cfg_path} (sound={args.sound})")
    return out_ags, cfg_path


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def _dos_tag(raw):
    """DOS 8.3-safe run tag: [A-Z0-9_], truncated to 8 chars -- the same
    restriction patches/ags/0044's own DOSAGS_LOG_TAG handling applies
    (it picks the RUNMANI.LOG replacement filename directly from this
    value), so an out-of-range tag here would silently get truncated
    again downstream. Enforced here instead so a --tag-prefix collision
    (two arms truncating to the same 8 chars) is visible immediately."""
    tag = re.sub(r"[^A-Z0-9_]", "", raw.upper())
    return tag[:8] or "PGVAL"


RUNMANIFEST_LINE_RE = re.compile(r"^(?P<key>[a-zA-Z_][a-zA-Z0-9_]*)=(?P<value>.*)$")


def fps_measures_label(fields):
    """What this run's fps_p50/fps_p95 actually counted, in words.

    Never a bare number: the 40/40 plan's fps gate requires every record
    to state how many presents were real vs skipped, and a static-screen
    figure must be labelled as one rather than quoted as gameplay fps.
    """
    real, skipped = fields.get("presents_real"), fields.get("presents_skipped")
    if real is None or skipped is None:
        return ("render passes/s (RenderCounter); real-vs-skipped presents "
                "NOT recorded (binary predates patch 0093) -- unknown whether "
                "frames reached the display")
    real, skipped = int(real), int(skipped)
    total = real + skipped
    pct = (100.0 * real / total) if total else 0.0
    kind = ("STATIC-SCREEN figure, not a gameplay fps" if pct < 50.0
            else "most render passes reached the display")
    return (f"render passes/s (RenderCounter), NOT displayed frames/s; "
            f"{real} of {total} presents real ({pct:.1f}%), {skipped} skipped "
            f"as unchanged -- {kind}")


def parse_runmanifest(text):
    """Extracts the [RUNMANIFEST-BEGIN]..[RUNMANIFEST-END] key=value block.
    A small, deliberately re-typed copy of tests/harness/parse-results.py's
    own parse_runmanifest() -- that script's filename has a hyphen, so it
    is not importable as a module; run-hw.sh's own wait_for_stable_screen()
    comment establishes the "small cited copy beats a sibling-script
    loader hack" precedent this follows."""
    m = re.search(r"\[RUNMANIFEST-BEGIN\](.*?)\[RUNMANIFEST-END\]", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        fm = RUNMANIFEST_LINE_RE.match(line)
        if fm:
            fields[fm.group("key")] = fm.group("value")
    # The RUNMANIFEST-adjacent "DOS-PORT" lines this port's own patches
    # emit AFTER the block (patch 0048: `DOS-PORT tick_rate=<r>
    # frames_skipped=<n>`, the game-speed KPI PLAN.md's "Fixed timestep
    # and the fps KPI" makes the hard PASS/FAIL number on real hardware;
    # patch 0043: `DOS-PORT memory_min_free_kb=<kb>`). Folded into the
    # same dict so record's validated: entry and results/<tag>.json carry
    # them next to fps_p50 -- before 2026-09-16 the tool silently dropped
    # both, and every manifest's tick_rate had been typed in by hand.
    dm = re.search(r"^DOS-PORT tick_rate=(?P<tr>\S+) frames_skipped=(?P<fs>\S+)", text, re.M)
    if dm:
        fields["tick_rate"] = dm.group("tr")
        fields["frames_skipped"] = dm.group("fs")
    mm = re.search(r"^DOS-PORT memory_min_free_kb=(?P<kb>\S+)", text, re.M)
    if mm:
        fields["memory_min_free_kb"] = mm.group("kb")
    # patch 0079 (script_vm, render_backbuffer) + patch 0080 (input_poll,
    # audio_sync) + patch 0081 (scene_construct, wait_next_frame) +
    # patch 0082 (the exhaustive closes-by-construction partition):
    # full-run per-tick timing aggregates, same "fold the DOS-PORT line
    # into this same dict" rationale as tick_rate/memory_min_free_kb
    # above -- one regex per phase, all lines share the same
    # calls/total_ms/min_ms/max_ms/mean_ms shape.
    for phase in ("script_vm", "render_backbuffer", "input_poll", "audio_sync",
                  "scene_construct", "wait_next_frame",
                  "game_tick_outer", "update_game_once_total",
                  "game_objects_update", "objects_scale", "gui_poll",
                  "ground_interactions", "input_handling", "room_check",
                  "gui_context_cursor", "persistent_anims", "end_of_tick",
                  "rep_exec_vm", "rep_exec_wrapper", "drawable_object_states",
                  "process_events_dispatch", "catchup_audio_poll", "render_to_screen",
                  "render_to_screen_pertick", "screen_overlay_vsync", "present_get_win_surface",
                  "present_sync_palette", "present_flip_handling", "present_blit",
                  "present_update_window", "fastblit_lock", "fastblit_hreplicate",
                  "fastblit_vmemcpy", "present_dirty_check", "present_skip_unchanged",
                  # patches 0125/0126/0133/0135 (ags 0125): logged by
                  # quit.cpp through the same dos_port_tick_emit() and, until
                  # 2026-09-21, dropped here -- so the render_backbuffer
                  # blitting half, the background restore and the nine
                  # scene_construct sub-brackets never reached results/*.json.
                  "rb_sprite_time", "bg_restore",
                  "sc_overlays", "sc_room_view", "sc_ui_view", "sc_screen_ovl",
                  "sc_preroom", "sc_prep_objects", "sc_prep_chars",
                  "sc_draw_list", "sc_viewports"):
        pm = re.search(
            r"^DOS-PORT tickstats_" + phase +
            r" calls=(?P<calls>\S+) total_ms=(?P<total>\S+) "
            r"min_ms=(?P<min>\S+) max_ms=(?P<max>\S+) mean_ms=(?P<mean>\S+)"
            r"(?: clamped_neg=(?P<clamped>\S+))?"
            # patch 0082 (catch-up-loop audit): total_us is the new,
            # un-truncated microsecond aggregate -- see
            # dos_port_tick_timing.h's own total_us comment for why
            # total_ms/mean_ms alone can silently read 0 for a phase
            # with real but sub-millisecond-per-call cost.
            r"(?: total_us=(?P<totalus>\S+))?",
            text, re.M)
        if pm:
            fields[f"{phase}_calls"] = pm.group("calls")
            fields[f"{phase}_total_ms"] = pm.group("total")
            fields[f"{phase}_min_ms"] = pm.group("min")
            fields[f"{phase}_max_ms"] = pm.group("max")
            fields[f"{phase}_mean_ms"] = pm.group("mean")
            if pm.group("clamped") is not None:
                fields[f"{phase}_clamped_neg"] = pm.group("clamped")
            if pm.group("totalus") is not None:
                fields[f"{phase}_total_us"] = pm.group("totalus")
    # patch 0081: what WaitForNextFrame() itself intended to sleep for,
    # separate from its own measured cost above -- comparing the two is
    # the calibration check (see dos_port_tick_timing.h's own comment).
    wr = re.search(
        r"^DOS-PORT tickstats_wait_next_frame_requested "
        r"sleep_calls=(?P<calls>\S+) requested_ms=(?P<ms>\S+)",
        text, re.M)
    if wr:
        fields["wait_next_frame_sleep_calls"] = wr.group("calls")
        fields["wait_next_frame_requested_ms"] = wr.group("ms")
    # patch 0085: real-mode-callback visibility (operator-directed DPMI/
    # interrupt audit) -- the resolved banked-vs-LFB flush decision and
    # the cumulative count of real BIOS-issued VESA bank switches.
    bm = re.search(
        r"^DOS-PORT video_banked_mode=(?P<banked>\S+) bank_switches=(?P<switches>\S+)",
        text, re.M)
    if bm:
        fields["video_banked_mode"] = bm.group("banked")
        fields["bank_switches"] = bm.group("switches")
    # patch 0093 (40/40 plan, P0 items 2-4): the yardstick lines.
    # fps_p50/fps_p95 count RENDER PASSES (GameTimer.RenderCounter), not
    # frames that reached the display -- since patch 0091 Present() can
    # skip an unchanged frame entirely, so a static screen reports a high
    # fps while almost nothing is pushed. Every fps figure this tool
    # records therefore carries what it measured (fps_measures below).
    fb = re.search(
        r"^DOS-PORT fps_basis counts=(?P<counts>\S+) render_passes=(?P<rp>\S+) "
        r"presents_real=(?P<real>\S+) presents_skipped=(?P<skipped>\S+)",
        text, re.M)
    if fb:
        fields["fps_counts"] = fb.group("counts")
        fields["render_passes"] = fb.group("rp")
        fields["presents_real"] = fb.group("real")
        fields["presents_skipped"] = fb.group("skipped")
    bp = re.search(
        r"^DOS-PORT blit_path fast=(?P<fast>\S+) generic=(?P<gen>\S+) "
        r"src_bytes_per_pixel=(?P<bpp>\S+)", text, re.M)
    if bp:
        fields["blits_fast"] = bp.group("fast")
        fields["blits_generic"] = bp.group("gen")
        fields["blit_src_bytes_per_pixel"] = bp.group("bpp")
    ts = re.search(
        r"^DOS-PORT tick_rate_steady=(?P<rate>\S+) ticks=(?P<ticks>\S+) "
        r"stall_ticks=(?P<st>\S+) loop_ms=(?P<loop>\S+) stall_ms=(?P<sms>\S+) "
        r"preloop_ms=(?P<pre>\S+) threshold_ms=(?P<thr>\S+)", text, re.M)
    if ts:
        fields["tick_rate_steady"] = ts.group("rate")
        fields["tick_stall_ticks"] = ts.group("st")
        fields["tick_loop_ms"] = ts.group("loop")
        fields["tick_stall_ms"] = ts.group("sms")
        fields["tick_preloop_ms"] = ts.group("pre")
        fields["tick_stall_threshold_ms"] = ts.group("thr")
    stalls = re.findall(r"^DOS-PORT tick_stall index=(\S+) ms=(\S+)", text, re.M)
    if stalls:
        fields["tick_stalls"] = [{"index": int(i), "ms": int(ms)} for i, ms in stalls]
    # ms= (patch 0094) is optional: a patch-0093-only log has rows without
    # it, and rows alone are NOT a time base (none is sampled during a
    # blocking stall) -- a consumer must use ms when present.
    persec = re.findall(
        r"^DOS-PORT persec t=(\S+) tick=(\S+) renders=(\S+) real=(\S+) skipped=(\S+)(?: ms=(\S+))?",
        text, re.M)
    if persec:
        fields["persec"] = [
            {"t": int(t), "tick": int(tk), "renders": int(r), "real": int(re_), "skipped": int(sk),
             "ms": (int(ms) if ms else None)}
            for t, tk, r, re_, sk, ms in persec]
    # tick_rate_steady removes stall ticks AND their time, but the fixed-
    # timestep loop then repays up to MAX_CATCHUP=5 ticks after each stall,
    # and those repaid ticks land in the steady numerator with no time to
    # match -- so it reads ~+0.2 per stall high over a 25 s cell (40.4-40.5
    # on a run whose pacing is exactly 40). That makes it the wrong figure
    # for "is the pacer letting the game run FAST?". This one is: ticks
    # over real elapsed time between the first per-second row at least 200
    # ticks (5 s of game time) past the last stall and the last row -- no
    # stall, no repay, and no post-stall fade (a run of slow-but-under-
    # threshold ticks: 24 ticks/s for a second on Trilby's Notes) inside
    # it. Derived here, from rows every patch-0094+ log already has.
    rows = [r for r in (fields.get("persec") or []) if r.get("ms") is not None]
    if len(rows) >= 2:
        last_stall = max([st["index"] for st in fields.get("tick_stalls", [])] or [0])
        window = [r for r in rows if r["tick"] >= last_stall + 200]
        if len(window) >= 2 and window[-1]["ms"] > window[0]["ms"]:
            d_tick = window[-1]["tick"] - window[0]["tick"]
            d_ms = window[-1]["ms"] - window[0]["ms"]
            fields["tick_rate_window"] = f"{1000.0 * d_tick / d_ms:.2f}"
            fields["tick_rate_window_ticks"] = d_tick
            fields["tick_rate_window_ms"] = d_ms
    # patch 0095: the clock every rate above was measured with, checked
    # against the CMOS RTC (an oscillator that shares nothing with the PIT
    # or IRQ0). Present only when the cell ran DOSAGS_CLOCK_CROSSCHECK=1.
    cc = re.search(
        r"^DOS-PORT clock_crosscheck status=(?P<status>\S+)"
        r"(?: rtc_s=(?P<rtc>\S+) uclock_ms=(?P<ums>\S+) ratio=(?P<ratio>\S+) ticks=(?P<ticks>\S+))?",
        text, re.M)
    if cc:
        fields["clock_crosscheck_status"] = cc.group("status")
        if cc.group("ratio"):
            fields["clock_crosscheck_rtc_s"] = cc.group("rtc")
            fields["clock_crosscheck_uclock_ms"] = cc.group("ums")
            fields["clock_crosscheck_ratio"] = cc.group("ratio")
            fields["clock_crosscheck_ticks"] = cc.group("ticks")
    fields["fps_measures"] = fps_measures_label(fields)
    return fields


# Patch 0047's own one-time log line (Engine/main/game_run.cpp,
# dos_fixed_timestep_active()) -- the engine's word on whether the fixed
# timestep was actually active for a run, checked from STDOUT.TXT rather
# than trusting that the SET line reached AGS.EXE. The RUNMANIFEST
# env_block_sha does NOT cover DOSAGS_FIXED_TIMESTEP (patch 0038's
# allowlist predates 0047), so without this witness two runs with
# different game-speed semantics would be indistinguishable in the record.
FIXED_TIMESTEP_WITNESS = {
    True: "DOS-PORT fixed-timestep: ENABLED",
    False: "DOS-PORT fixed-timestep: DISABLED",
}


def read_stdout_txt(stage_dir):
    """The engine's --log-stdout=+mgs:all output, as run-dosbox.sh /
    dosbox-run.sh redirect it (RUN.BAT's `> STDOUT.TXT`). Returns "" when
    absent so a witness check fails honestly rather than crashing."""
    # A DOSBox-X stage dir has STDOUT.TXT; a run-hw.sh collected dir (or
    # a tests/games/<id>/results/ record) may carry it renamed with the
    # run's own prefix, e.g. HW-486-66-2026-09-15-S32B7-STDOUT.TXT.
    cands = [os.path.join(stage_dir, n) for n in ("STDOUT.TXT", "stdout.txt")]
    cands += sorted(glob.glob(os.path.join(stage_dir, "*STDOUT*.TXT")))
    cands += sorted(glob.glob(os.path.join(stage_dir, "*stdout*.txt")))
    for p in cands:
        if os.path.isfile(p):
            try:
                return open(p, errors="replace").read()
            except OSError:
                return ""
    return ""


# PLAN.md "Fixed timestep and the fps KPI": game speed = logic ticks per
# wall-second = 40 within +/- 2% on the in-profile package on HW-486-66 is
# the HARD KPI; rendered fps is the tracked smoothness number. Reported
# (non-gating) on every record so the number is never silently absent,
# gated only where a real-hardware campaign's own acceptance says so --
# on DOSBox-X it is meaningless as a pass/fail (emulation speed is not
# the target's), and on the 486 tier today every run fails it (best so
# far 23.8 at 4.99 fps idle), which is the 40fps push's actual target.
GAME_SPEED_TARGET = 40.0
GAME_SPEED_TOLERANCE = 0.02


def _check_game_speed(runmanifest):
    tr = (runmanifest or {}).get("tick_rate")
    try:
        val = float(tr)
    except (TypeError, ValueError):
        return {"ok": False, "gating": False, "detail": "no DOS-PORT tick_rate line (patch 0048) in the run"}
    lo = GAME_SPEED_TARGET * (1 - GAME_SPEED_TOLERANCE)
    hi = GAME_SPEED_TARGET * (1 + GAME_SPEED_TOLERANCE)
    return {"ok": lo <= val <= hi, "gating": False, "tick_rate": val,
            "band": f"{GAME_SPEED_TARGET} +/- {int(GAME_SPEED_TOLERANCE * 100)}%"}


def _check_witness(run_dir):
    """Gating: a hardware run that has a physical-screen witness directory has its figure REFUSED
    unless a person recorded a clean review of that witness (tests/harness/witness_review.py).
    None for runs with no witness directory (DOSBox-X, or cells from before the standing order)."""
    hd = os.path.join(REPO_ROOT, "tests", "harness")
    if hd not in sys.path:
        sys.path.insert(0, hd)
    import witness_check
    return witness_check.check(str(run_dir))


def _check_present_verify(stdout_text):
    """The ags 0192 present verifier's answer, as a GATING check, or None if the run did not
    carry it (real hardware never does: it reads the surface twice per present).

    Every other check here reads the engine's own RAM frame -- a capture hash comes from
    SaveScreenShot, which blits virtualScreen -- so none of them can see a region that
    changed in RAM and was never pushed to the screen. That is a trail, it passed every hash
    for as long as it existed, and the operator found it with a camera. The verifier shadows
    what was pushed and counts the pixels that differ; any stale frame fails the arm.
    """
    import re as _re
    last = None
    for line in (stdout_text or "").replace("\r", "").splitlines():
        m = _re.search(r"DOS-PORT presentverify frames=(\d+) stale_frames=(\d+) stale_px=(\d+) stale_px_max=(\d+)", line)
        if m:
            last = tuple(int(g) for g in m.groups())
    if last is None:
        return None
    frames, stale_frames, stale_px, stale_max = last
    return {"ok": stale_frames == 0, "frames": frames, "stale_frames": stale_frames,
            "stale_px": stale_px, "stale_px_max": stale_max,
            "detail": ("no pushed-rect deficit" if stale_frames == 0 else
                       f"{stale_frames}/{frames} presents left the screen different from the engine's frame")}


# A self-reported rate is only as good as the clock it was measured with.
# uclock() runs SLOW whenever IRQ0 is starved (a wait with interrupts off,
# or one that never lets the BIOS timer ISR run), and a slow clock makes
# tick_rate/fps read HIGH -- this hub has shipped that failure once. 0.5%
# is ~25x the cross-check's own resolution over a 30 s cell and a quarter
# of the 40 +/- 2% game-speed band, so a clock error big enough to move a
# gate verdict cannot hide under it.
CLOCK_CROSSCHECK_TOLERANCE = 0.005


def _check_clock_crosscheck(runmanifest):
    """Gating on real hardware when the cell asked for it; informational
    under DOSBox-X, whose RTC is host wall time while its PIT is emulated
    time -- a loaded host legitimately pulls the two apart there."""
    rm = runmanifest or {}
    status = rm.get("clock_crosscheck_status")
    if status is None:
        return None
    gating = rm.get("environment") != "dosbox-x"
    if status != "ok":
        return {"ok": False, "gating": gating, "detail": f"clock_crosscheck status={status}"}
    try:
        ratio = float(rm.get("clock_crosscheck_ratio"))
    except (TypeError, ValueError):
        return {"ok": False, "gating": gating, "detail": "unparseable ratio"}
    return {"ok": abs(ratio - 1.0) <= CLOCK_CROSSCHECK_TOLERANCE, "gating": gating,
            "ratio": ratio, "rtc_s": rm.get("clock_crosscheck_rtc_s"),
            "band": f"1 +/- {CLOCK_CROSSCHECK_TOLERANCE * 100:g}%"}


def _check_hw_recovery(run_dir):
    """A cell whose run needed the harness's automatic recovery (a return
    reboot that never took -- tests/harness/hw_guard.py) must not look like
    a clean one. Informational, never gating: the recovery happens between
    steps, outside the measured run, and the collected files were already
    verified -- but anyone reading the record should know the machine was
    power-cycled (or re-rebooted) around this cell. Absent file = no
    recovery = no entry."""
    rec = Path(run_dir) / "RECOVERY.TXT"
    try:
        lines = [ln.strip() for ln in rec.read_text(errors="replace").splitlines() if ln.startswith("HW-RECOVERY")]
    except OSError:
        return None
    if not lines:
        return None
    return {"ok": True, "gating": False, "recovered": True, "count": len(lines), "records": lines,
            "detail": "this cell's run needed an automatic hardware recovery -- see records"}


def _passes(checks):
    """Only gating checks decide pass/fail; informational ones (game_speed
    today) are reported alongside so they are never silently missing."""
    return all(c["ok"] for c in checks.values() if c.get("gating", True))


def find_runmanifest_log(stage_dir):
    """Scans *.LOG under stage_dir for a RUNMANIFEST block instead of
    assuming the untagged default name RUNMANI.LOG -- DOSAGS_LOG_TAG
    (patches/ags/0044) makes the engine write <TAG>.LOG instead. Same
    fallback parse-results.py's own runmani_log lookup already uses."""
    stage = Path(stage_dir)
    for candidate in sorted(stage.glob("*.LOG")):
        if candidate.name == "AUTOPLT.LOG":
            continue
        try:
            text = candidate.read_text(errors="replace")
        except OSError:
            continue
        if "[RUNMANIFEST-BEGIN]" in text:
            return candidate, text
    return None, None


def _hash_any_bmp(stage_dir):
    """Hashes any *.BMP the run produced (a title-screen capture, per
    PLAN.md's validate stage design) -- content-agnostic, works for any
    future golden reference's own screenshot naming, not just AGS Quest's
    AutoPilot-driven PH0N.BMP. Returns None (not a failure) when the game
    has no in-script capture call at all -- every current golden reference
    except AGS Quest is binary-only with no AutoPilot module, so this is
    the normal, honest case today, not a bug to work around."""
    hits = sorted(glob.glob(os.path.join(stage_dir, "*.BMP"))) + \
        sorted(glob.glob(os.path.join(stage_dir, "*.bmp")))
    if not hits:
        return None
    return {os.path.basename(p): hashlib.sha256(open(p, "rb").read()).hexdigest() for p in hits}


def _check_captures(run_dir, expected):
    """Optional, additive: an arm whose expected block carries
    `capture_sha256: {NAME.BMP: <sha256>}` gets one gating check per named
    capture. Arms without the key (every closed-binary game) get none, so
    their behaviour is unchanged. A capture that is absent fails -- a
    scripted fixture that did not write its screenshot did not finish."""
    checks = {}
    for name, want in (expected.get("capture_sha256") or {}).items():
        path = os.path.join(run_dir, name)
        got = hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.isfile(path) else None
        checks[f"capture:{name}"] = {"ok": got == want, "expected": want, "actual": got}
    return checks


def _check_runmanifest(runmanifest, expected):
    """Compares one arm's actual RUNMANIFEST fields against the manifest's
    own expected_runmanifest_dosbox_x.<arm> block. exit_code/critical_
    count/warn_count are hard checks (a binary-only golden reference's
    only correctness signal, since it has no AutoPilot phase sequence to
    check instead); audio_vital_status is checked as either an exact
    match or a startswith() prefix match, whichever the manifest gives --
    fps/tick_rate are recorded elsewhere but never gated here, same as
    parse-results.py never gates AGS Quest's own fps numbers."""
    checks = {}
    if runmanifest is None:
        checks["runmanifest_present"] = {"ok": False, "detail": "no RUNMANIFEST block found in any staged *.LOG"}
        return checks
    checks["runmanifest_present"] = {"ok": True}

    expected_exit = expected.get("exit_code", 0)
    actual_exit = runmanifest.get("exit_code")
    checks["exit_code"] = {"ok": str(actual_exit) == str(expected_exit),
                            "expected": expected_exit, "actual": actual_exit}

    actual_crit = runmanifest.get("critical_count")
    checks["critical_count"] = {"ok": actual_crit == "0", "expected": "0", "actual": actual_crit}

    actual_warn = runmanifest.get("warn_count")
    checks["warn_count"] = {"ok": actual_warn == "0", "expected": "0", "actual": actual_warn}

    actual_audio = runmanifest.get("audio_vital_status", "")
    if "audio_vital_status_prefix" in expected:
        prefix = expected["audio_vital_status_prefix"]
        checks["audio_vital_status"] = {"ok": actual_audio.startswith(prefix),
                                         "expected_prefix": prefix, "actual": actual_audio}
    elif "audio_vital_status" in expected:
        want = expected["audio_vital_status"]
        checks["audio_vital_status"] = {"ok": actual_audio == want,
                                         "expected": want, "actual": actual_audio}
    return checks


def _check_stdout_witnesses(stdout_text, expected, fixed_timestep):
    """Engine-log witnesses, checked against STDOUT.TXT rather than the
    RUNMANIFEST block: (1) patch 0047's fixed-timestep line, always
    checked, so a benchmark record can never silently come from a
    1:1-logic/render run (or vice versa); (2) any `stdout_contains:` list
    the manifest's expected_runmanifest_dosbox_x.<arm> gives -- the
    32-bit KPI campaign's own rule was "confirmed via each run's own
    'Graphics mode set: ... (N-bit)' log line, never trusted from the
    requested env var alone" (tests/games/shards/manifest.yaml), and this
    is that rule made mechanical for DOSAGS_FORCE_COLOR_DEPTH arms."""
    checks = {}
    if not stdout_text:
        checks["stdout_present"] = {"ok": False, "detail": "no STDOUT.TXT in the staged run dir"}
        return checks
    checks["stdout_present"] = {"ok": True}
    want = FIXED_TIMESTEP_WITNESS[bool(fixed_timestep)]
    checks["fixed_timestep"] = {"ok": want in stdout_text, "expected_line": want}
    for needle in expected.get("stdout_contains", []) or []:
        checks[f"stdout_contains:{needle}"] = {"ok": needle in stdout_text, "expected_substring": needle}
    return checks


def cmd_validate(args):
    """DOSBox-X boot-to-title + DOSAGS_TAS_AUTO_EXIT_TICK (patch 0044) +
    RUNMANIFEST check + a title-screen capture hash (PLAN.md's `validate`
    stage) -- drives tests/harness/run-dosbox.sh, the SAME underlying
    mechanism the hand-run S7 sessions used (that script's own
    --include-extra for the sound-on/off ACSETUP.CFG variant, --env for
    DOSAGS_TAS_AUTO_EXIT_TICK/DOSAGS_LOG_TAG/the audio backend hint), just
    reading those parameters from the manifest's own `validate:` block
    instead of a human retyping them per game.

    FORMER KNOWN GAP, closed 2026-09-16: the hub's dosbox-run.sh used to
    have no conf override (only --fast/parity, both oplmode=none by
    design), so the S7 sound-on arm's OPL3 chip detection needed a
    hand-staged scratch conf this path could not reproduce. The hub now
    takes --conf PATH (pulled into .sdl-dos-ports/ the same day),
    run-dosbox.sh passes it through, and a manifest names its conf via
    `validate: dosbox_conf:` (tests/games/trilbysnotes/manifest.yaml ->
    tests/harness/confs/dosbox-x-fast-opl3.conf). A manifest without
    one still runs on the stock --fast conf, and a mismatch between the
    expected and actual audio_vital_status is still reported honestly
    rather than forced.

    Binary-only games (every current golden reference except AGS Quest)
    have no AutoPilot phase sequence -- pass/fail here is RUNMANIFEST-
    only (exit_code/critical_count/warn_count/audio_vital_status), not
    phase-based like tests/harness/parse-results.py's AGS Quest checks.
    """
    manifest = load_yaml(args.manifest)
    vconf = manifest.get("validate")
    if not vconf:
        raise SystemExit(
            f"port_game.py validate: {args.manifest} has no 'validate:' block -- "
            f"hand-author one first (pkg/auto_exit_tick/timeout_s/arms), see "
            f"tests/games/trilbysnotes/manifest.yaml for the pattern")
    expected_all = manifest.get("expected_runmanifest_dosbox_x", {})
    pkg = vconf.get("pkg", manifest["id"])
    tick = vconf.get("auto_exit_tick", 200)
    timeout_s = vconf.get("timeout_s", 180)
    arms = vconf.get("arms", {})
    # Fixed timestep (patches/ags/0047, DOSAGS_FIXED_TIMESTEP=1) is opt-in
    # at the engine level by operator decision (2026-09-16: keep the
    # player-facing default unchanged until a per-game real-hardware
    # sign-off) but MANDATORY for every benchmark cell this framework
    # produces -- PLAN.md's "Fixed timestep and the fps KPI" makes
    # tick_rate the hard game-speed KPI and rendered fps a pure smoothness
    # number, which only holds when the catch-up loop is on. Every
    # hand-run KPI cell so far (S7 ABBAs, the 8/16/32-bit comparison) set
    # it by hand; before 2026-09-16 this generalized path did not, so a
    # manifest-driven run would have measured slow GAMEPLAY, not low fps.
    # A manifest may opt out explicitly (validate: fixed_timestep: false,
    # e.g. a pure correctness cell) -- never silently.
    fixed_timestep = bool(vconf.get("fixed_timestep", True))
    # validate: dosbox_conf: <path relative to the repo root> -- an
    # arbitrary DOSBox-X conf handed to run-dosbox.sh --conf (hub
    # dosbox-run.sh --conf, 2026-09-16) instead of the stock --fast
    # conf. Closes the "known gap" this function's docstring describes:
    # the Sound gate's sound-on arm needs oplmode=opl3 for OPL3 chip
    # detection under emulation, which the hub's shipped confs
    # deliberately never provide. Optional; absent means --fast as before.
    dosbox_conf = vconf.get("dosbox_conf")
    if dosbox_conf:
        dosbox_conf = dosbox_conf if os.path.isabs(dosbox_conf) else os.path.join(REPO_ROOT, dosbox_conf)
        if not os.path.isfile(dosbox_conf):
            raise SystemExit(f"port_game.py validate: validate.dosbox_conf {dosbox_conf} not found")

    requested = list(arms.keys()) if args.arm == "all" else [args.arm]
    for arm in requested:
        if arm not in arms:
            raise SystemExit(f"port_game.py validate: manifest has no validate.arms.{arm}")

    run_dosbox = os.path.join(REPO_ROOT, "tests", "harness", "run-dosbox.sh")
    if not os.path.isfile(run_dosbox):
        raise SystemExit(f"port_game.py validate: {run_dosbox} not found")

    results = {}
    used_tags = set()
    tmp_root = tempfile.mkdtemp(prefix="port-game-validate.")
    try:
        for arm in requested:
            arm_conf = arms[arm]
            cfg_src = os.path.join(args.layout_dir, arm_conf["cfg"])
            if not os.path.isfile(cfg_src):
                raise SystemExit(f"port_game.py validate: {cfg_src} not found -- run layout first")

            # DOS 8.3: the engine looks for the literal name ACSETUP.CFG
            # on C:\ -- run-dosbox.sh's own --include-extra stages a file
            # under ITS OWN basename (dosbox-run.sh only uppercases it,
            # never renames it), so the rename to the engine's expected
            # name has to happen here, on the host, before staging.
            arm_stage_dir = os.path.join(tmp_root, arm)
            os.makedirs(arm_stage_dir, exist_ok=True)
            staged_cfg = os.path.join(arm_stage_dir, "ACSETUP.CFG")
            shutil.copyfile(cfg_src, staged_cfg)

            # Suffix from the END of the arm name, not the start: arm
            # names sharing a common prefix (sound_on/sound_off both
            # start "sou") would otherwise truncate to the SAME 8-char
            # tag -- a real collision this exact pair hit during this
            # tool's own regression check (both arms logged RUNMANIFEST
            # as tag=PGVALSOU). Guaranteed-unique fallback below in case
            # even the suffix collides for some other arm-name pair.
            tag = _dos_tag((args.tag_prefix or "PGVAL") + arm[-3:])
            n = 1
            while tag in used_tags:
                disambig = str(n)
                tag = _dos_tag(tag[:8 - len(disambig)] + disambig)
                n += 1
            used_tags.add(tag)
            env = {"DOSAGS_TAS_AUTO_EXIT_TICK": str(tick), "DOSAGS_LOG_TAG": tag}
            if fixed_timestep:
                env["DOSAGS_FIXED_TIMESTEP"] = "1"
            env.update(arm_conf.get("env", {}))

            cmd = [run_dosbox, pkg, "--timeout", str(timeout_s), "--include-extra", staged_cfg]
            # Optional, additive: validate.arms.<arm>.extra_files maps a DOS
            # name to a repo-relative source file, staged next to the package
            # under that name (same host-side rename as ACSETUP.CFG above).
            # On real hardware the same source goes through run-hw.sh's
            # --extra-file SRC:NAME.
            for dos_name, src in (arm_conf.get("extra_files") or {}).items():
                src_path = src if os.path.isabs(src) else os.path.join(REPO_ROOT, src)
                if not os.path.isfile(src_path):
                    raise SystemExit(f"port_game.py validate: extra_files source {src_path} not found")
                staged_extra = os.path.join(arm_stage_dir, dos_name)
                shutil.copyfile(src_path, staged_extra)
                cmd += ["--include-extra", staged_extra]
            if dosbox_conf:
                cmd += ["--conf", dosbox_conf]
            for k, v in env.items():
                cmd += ["--env", f"{k}={v}"]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            stdout_lines = [l for l in proc.stdout.splitlines() if l.strip()]
            if not stdout_lines:
                results[arm] = {"tag": tag, "pass": False, "error": "run-dosbox.sh produced no stage dir",
                                 "stderr": proc.stderr.strip()}
                continue
            stage_dir = stdout_lines[-1].strip()

            log_path, log_text = find_runmanifest_log(stage_dir)
            runmanifest = parse_runmanifest(log_text) if log_text else None
            arm_expected = expected_all.get(arm, {})
            checks = _check_runmanifest(runmanifest, arm_expected)
            checks.update(_check_stdout_witnesses(read_stdout_txt(stage_dir), arm_expected, fixed_timestep))
            checks.update(_check_captures(stage_dir, arm_expected))
            checks["game_speed_40hz"] = _check_game_speed(runmanifest)
            cc_check = _check_clock_crosscheck(runmanifest)
            if cc_check is not None:
                checks["clock_crosscheck"] = cc_check
            pv_check = _check_present_verify(read_stdout_txt(stage_dir))
            if pv_check is not None:
                checks["present_verify"] = pv_check
            capture = _hash_any_bmp(stage_dir)

            results[arm] = {
                "tag": tag,
                "env": env,
                "stage_dir": stage_dir,
                "runmanifest_log": str(log_path) if log_path else None,
                "runmanifest": runmanifest,
                "expected": arm_expected,
                "checks": checks,
                "pass": bool(runmanifest) and _passes(checks),
                "capture_hash": capture,
            }
    finally:
        if not args.keep_stage:
            shutil.rmtree(tmp_root, ignore_errors=True)

    text = json.dumps(results, indent=2)
    if args.json:
        with open(args.json, "w") as f:
            f.write(text)
    print(text)
    overall_pass = bool(results) and all(r.get("pass") for r in results.values())
    print(f"port_game.py validate: {'PASS' if overall_pass else 'FAIL'}", file=sys.stderr)
    return results, overall_pass


def cmd_check(args):
    """The `validate` checks applied to a run that ALREADY happened --
    a run-hw.sh collected dir (real hardware) or any dir holding a
    <TAG>.LOG with a RUNMANIFEST block plus the run's STDOUT.TXT -- and
    emits the same per-arm JSON `record` consumes. This is how a real-
    hardware run enters a manifest's validated: list through the tool
    rather than by hand: run-hw.sh runs the cell, `check` judges the
    collected dir against the manifest's expected_runmanifest_dosbox_x
    .<arm> block (the RUNMANIFEST/witness expectations are environment-
    independent; only fps/tick_rate MEAN something different on real
    hardware, and those are never gated here), then `record --environment
    HW-486-66` appends it. Closes the framework gate's "the three
    in-profile references have a real-hardware results/ record" half
    without a second, hand-typed path -- added 2026-09-16, first proven
    against tests/games/shards/results/'s own 2026-09-15 S32B7 logs."""
    manifest = load_yaml(args.manifest)
    vconf = manifest.get("validate") or {}
    arms = vconf.get("arms", {})
    if args.arm not in arms:
        raise SystemExit(f"port_game.py check: manifest has no validate.arms.{args.arm} "
                         f"(have: {', '.join(arms) or 'none'})")
    fixed_timestep = bool(vconf.get("fixed_timestep", True))
    expected = (manifest.get("expected_runmanifest_dosbox_x") or {}).get(args.arm, {})

    run_dir = args.run_dir
    if args.log:
        log_path = Path(args.log)
        log_text = log_path.read_text(errors="replace")
        if "[RUNMANIFEST-BEGIN]" not in log_text:
            log_text = None
    else:
        log_path, log_text = find_runmanifest_log(run_dir)
    runmanifest = parse_runmanifest(log_text) if log_text else None
    checks = _check_runmanifest(runmanifest, expected)
    checks.update(_check_stdout_witnesses(read_stdout_txt(run_dir), expected, fixed_timestep))
    checks.update(_check_captures(run_dir, expected))
    checks["game_speed_40hz"] = _check_game_speed(runmanifest)
    cc_check = _check_clock_crosscheck(runmanifest)
    if cc_check is not None:
        checks["clock_crosscheck"] = cc_check
    pv_check = _check_present_verify(read_stdout_txt(run_dir))
    if pv_check is not None:
        checks["present_verify"] = pv_check
    wit_check = _check_witness(run_dir)
    if wit_check is not None:
        checks["witness_reviewed"] = wit_check
    hw_rec = _check_hw_recovery(run_dir)
    if hw_rec is not None:
        checks["hw_recovery"] = hw_rec
    tag = args.tag or (runmanifest or {}).get("wave_tag") or _dos_tag(os.path.basename(run_dir.rstrip("/")))
    results = {args.arm: {
        "tag": tag,
        "run_dir": run_dir,
        "runmanifest_log": str(log_path) if log_path else None,
        "runmanifest": runmanifest,
        "expected": expected,
        "checks": checks,
        "pass": bool(runmanifest) and _passes(checks),
        "capture_hash": _hash_any_bmp(run_dir),
    }}
    text = json.dumps(results, indent=2)
    if args.json:
        with open(args.json, "w") as f:
            f.write(text)
    print(text)
    ok = results[args.arm]["pass"]
    print(f"port_game.py check: {'PASS' if ok else 'FAIL'}", file=sys.stderr)
    return results, ok


def cmd_record(args):
    """Appends one validate run's results to tests/games/<id>/manifest.yaml's
    `validated:` list, in the exact hand-written style already established
    there (see tests/games/trilbysnotes/manifest.yaml's own dosbox-x
    entry) -- plus a raw results/<tag>.json record, per PLAN.md's `record`
    stage.

    Deliberately appends via plain text rather than a YAML-library
    load+dump round trip: this repo's manifest.yaml files are hand-
    annotated with extensive '#' comments explaining each field's
    provenance (data_version's own gate citation, the resolution cross-
    check, the clib repack-verification note, all in trilbysnotes'
    manifest.yaml today) -- a yaml.safe_load()+safe_dump() round trip
    would silently discard every one of them.

    `validated:` is NOT always the file's last top-level section --
    trilbysnotes' and shards' manifests both have a `compat_sweep:`
    mapping after it. A blind EOF append landed a new list item after
    that mapping once already (shards/manifest.yaml, 2026-09-16,
    S16FRC5 -- a dangling `- environment:` entry with no owning key,
    which broke this same tool's own YAML parsing until fixed by hand;
    see git history). Instead, find where the `validated:` list's last
    existing entry actually ends (the next top-level, column-0 `key:`
    line, skipping back over any blank lines) and insert there.
    """
    manifest_path = args.manifest
    manifest = load_yaml(manifest_path)  # read-only: validates the file parses, never rewritten wholesale
    with open(args.validate_json) as f:
        validate_report = json.load(f)

    results_dir = os.path.join(os.path.dirname(manifest_path), "results")
    os.makedirs(results_dir, exist_ok=True)
    results_json_path = os.path.join(results_dir, f"{args.tag}.json")
    with open(results_json_path, "w") as f:
        json.dump(validate_report, f, indent=2)

    # json.dumps()'s string escaping (backslash/quote/control chars) is a
    # valid subset of YAML double-quoted-scalar escaping -- used here
    # instead of a bare f-string interpolation so an engine-produced
    # audio_vital_status or a --note containing a literal '"' can never
    # produce broken YAML the way this manifest's own hand-written
    # wav_note field already did once (see this tool's own regression-
    # check commit for that unrelated, pre-existing bug and its fix).
    date = args.date or datetime.date.today().isoformat()
    lines = [f"  - environment: {args.environment}", f"    date: {date}"]
    for arm, r in validate_report.items():
        rm = r.get("runmanifest") or {}
        fields = [
            f"tag: {r.get('tag', 'NA')}",
            f"exit_code: {rm.get('exit_code', 'NA')}",
            f"audio_vital_status: {json.dumps(rm.get('audio_vital_status', 'NA'))}",
            f"fps_p50: {rm.get('fps_p50', 'NA')}",
            f"fps_p95: {rm.get('fps_p95', 'NA')}",
            f"tick_rate: {rm.get('tick_rate', 'NA')}",
            f"frames_skipped: {rm.get('frames_skipped', 'NA')}",
            f"presents_real: {rm.get('presents_real', 'NA')}",
            f"presents_skipped: {rm.get('presents_skipped', 'NA')}",
            f"tick_rate_steady: {rm.get('tick_rate_steady', 'NA')}",
            f"tick_rate_window: {rm.get('tick_rate_window', 'NA')}",
            f"clock_crosscheck_ratio: {rm.get('clock_crosscheck_ratio', 'NA')}",
            f"hw_recovered: {str(bool((r.get('checks') or {}).get('hw_recovery'))).lower()}",
            f"tick_stalls: {json.dumps(rm.get('tick_stalls', []))}",
            f"fps_measures: {json.dumps(rm.get('fps_measures', 'NA'))}",
            f"critical_count: {rm.get('critical_count', 'NA')}",
            f"warn_count: {rm.get('warn_count', 'NA')}",
            f"binary_sha12: {rm.get('binary_sha12', 'NA')}",
        ]
        lines.append(f"    {arm}: {{{', '.join(fields)}}}")
    overall_pass = bool(validate_report) and all(r.get("pass") for r in validate_report.values())
    note = args.note or (
        f"tools/port-game/port_game.py record -- generalized validate, "
        f"see results/{args.tag}.json for the full RUNMANIFEST + checks. "
        f"{'PASS' if overall_pass else 'FAIL'} -- see that file for which check(s) failed."
        if not overall_pass else
        f"tools/port-game/port_game.py record -- generalized validate, "
        f"see results/{args.tag}.json for the full RUNMANIFEST + checks."
    )
    lines.append(f"    note: {json.dumps(note)}")
    block = "\n".join(lines) + "\n"

    with open(manifest_path) as f:
        content = f.read()
    if "validated:" not in content:
        if not content.endswith("\n"):
            content += "\n"
        content += "\nvalidated:\n"

    lines = content.splitlines(keepends=True)
    validated_idx = next(i for i, l in enumerate(lines) if l.rstrip("\n") == "validated:")
    top_level_key_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*:")
    next_section_idx = next(
        (i for i in range(validated_idx + 1, len(lines)) if top_level_key_re.match(lines[i])),
        len(lines),
    )
    insert_idx = next_section_idx
    while insert_idx > validated_idx + 1 and lines[insert_idx - 1].strip() == "":
        insert_idx -= 1

    new_lines = lines[:insert_idx] + [block] + lines[insert_idx:]
    with open(manifest_path, "w") as f:
        f.write("".join(new_lines))

    print(f"port_game.py record: appended {args.environment}/{args.tag} to {manifest_path}")
    print(f"port_game.py record: wrote {results_json_path}")
    print(f"port_game.py record: overall {'PASS' if overall_pass else 'FAIL'}")
    return overall_pass


def cmd_all(args):
    """Chains inspect -> convert -> repack -> layout (x2, sound on/off) ->
    validate -> record from one per-game manifest, per PLAN.md's "Game
    porting framework" section. The manifest's own `validate:` block
    (pkg/auto_exit_tick/timeout_s/arms) must already exist -- a human
    decision (which env var flips which backend, how many ticks to boot
    to title) this tool does not invent, same as `inspect` does not
    invent a driving recipe on its own. See tests/games/trilbysnotes/
    manifest.yaml for the pattern this reads.
    """
    manifest = load_yaml(args.manifest)
    vconf = manifest.get("validate")
    if not vconf:
        raise SystemExit(f"port_game.py all: {args.manifest} has no 'validate:' block yet")
    pkg = vconf.get("pkg", manifest["id"])

    print("== port_game.py all: inspect ==")
    inspect_json = os.path.join(args.workdir, "inspect-report.json")
    os.makedirs(args.workdir, exist_ok=True)
    cmd_inspect(argparse.Namespace(game_file=args.game_file, tier_rate=args.tier_rate, json=inspect_json))

    print("== port_game.py all: convert ==")
    cmd_convert(argparse.Namespace(game_file=args.game_file, workdir=args.workdir, tier_rate=args.tier_rate))

    print("== port_game.py all: repack ==")
    name8 = _name8(args.name)  # same normalization layout itself uses -- see that helper's own docstring
    repacked = os.path.join(args.workdir, name8)
    cmd_repack(argparse.Namespace(game_file=args.game_file, workdir=args.workdir, out=repacked))

    print("== port_game.py all: layout (sound on/off) ==")
    for sound in ("on", "off"):
        cmd_layout(argparse.Namespace(repacked_ags=repacked, dest=args.dest, name=args.name, sound=sound))

    # Stage the freshly-built package where run-dosbox.sh/run-hw.sh
    # expect it (tests/harness/games/<pkg>/*.ags, gitignored, rebuilt on
    # demand -- same rule as tests/harness/games/agsquest/).
    harness_games_dir = os.path.join(REPO_ROOT, "tests", "harness", "games", pkg)
    os.makedirs(harness_games_dir, exist_ok=True)
    shutil.copyfile(os.path.join(args.dest, name8), os.path.join(harness_games_dir, name8))
    for cand in ("AUDIO.VOX", "SPEECH.VOX"):
        cand_path = os.path.join(args.dest, cand)
        if os.path.exists(cand_path):
            shutil.copyfile(cand_path, os.path.join(harness_games_dir, cand))

    print("== port_game.py all: validate ==")
    val_json = os.path.join(args.workdir, "validate-report.json")
    _results, _ok = cmd_validate(argparse.Namespace(
        manifest=args.manifest, layout_dir=args.dest, arm="all",
        tag_prefix=args.tag_prefix, json=val_json, keep_stage=False))

    print("== port_game.py all: record ==")
    overall_pass = cmd_record(argparse.Namespace(
        manifest=args.manifest, validate_json=val_json, environment=args.environment,
        tag=_dos_tag(args.tag_prefix + "ALL"), date=None, note=args.note))

    return overall_pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_inspect = sub.add_parser("inspect", help="survey a game file, print a JSON report")
    p_inspect.add_argument("game_file")
    p_inspect.add_argument("--tier-rate", type=int, default=11025)
    p_inspect.add_argument("--json", help="also save the report to this path")
    p_inspect.set_defaults(func=cmd_inspect)

    p_convert = sub.add_parser("convert", help="extract + host-transcode assets")
    p_convert.add_argument("game_file")
    p_convert.add_argument("--workdir", required=True)
    p_convert.add_argument("--tier-rate", type=int, default=11025)
    p_convert.set_defaults(func=cmd_convert)

    p_repack = sub.add_parser("repack", help="rebuild a single V30 CLIB from converted assets")
    p_repack.add_argument("game_file")
    p_repack.add_argument("--workdir", required=True)
    p_repack.add_argument("--out", required=True)
    p_repack.set_defaults(func=cmd_repack)

    p_layout = sub.add_parser("layout", help="produce a DOS-directory-ready package + acsetup variant")
    p_layout.add_argument("repacked_ags")
    p_layout.add_argument("--dest", required=True)
    p_layout.add_argument("--name", required=True, help="8.3-safe base name, e.g. NOTES")
    p_layout.add_argument("--sound", choices=["on", "off"], required=True)
    p_layout.set_defaults(func=cmd_layout)

    p_validate = sub.add_parser(
        "validate", help="DOSBox-X boot + auto-exit-tick + RUNMANIFEST check, driven by the manifest")
    p_validate.add_argument("--manifest", required=True, help="tests/games/<id>/manifest.yaml")
    p_validate.add_argument("--layout-dir", required=True, help="layout's --dest (has NAME8.ags + ACSETUP-*.CFG)")
    # Arm names are whatever the manifest's validate.arms declares (checked
    # against it at run time) -- sound_on/sound_off for a Sound-gate
    # manifest, depth_32_native/depth_16_forced for a color-depth one.
    p_validate.add_argument("--arm", default="all",
                            help="one of the manifest's validate.arms names, or 'all' (default)")
    p_validate.add_argument("--tag-prefix", default="PGVAL", help="DOS 8.3-safe run-tag prefix (truncated to 8)")
    p_validate.add_argument("--json", help="also save the combined report to this path")
    p_validate.add_argument("--keep-stage", action="store_true", help="keep the temp ACSETUP.CFG staging dir")
    p_validate.set_defaults(func=cmd_validate)

    p_check = sub.add_parser(
        "check", help="apply validate's checks to an already-collected run dir (e.g. run-hw.sh output)")
    p_check.add_argument("--manifest", required=True, help="tests/games/<id>/manifest.yaml")
    p_check.add_argument("--arm", required=True, help="which validate.arms entry this run was")
    p_check.add_argument("--run-dir", required=True, help="dir holding <TAG>.LOG (RUNMANIFEST) + STDOUT.TXT")
    p_check.add_argument("--log", default=None, help="explicit RUNMANIFEST log path (default: first *.LOG with a block)")
    p_check.add_argument("--tag", default=None, help="run tag (default: the RUNMANIFEST wave_tag)")
    p_check.add_argument("--json", help="also save the report to this path (feed it to record)")
    p_check.set_defaults(func=cmd_check)

    p_record = sub.add_parser(
        "record", help="append a validate run to manifest.yaml's validated: list + write results/<tag>.json")
    p_record.add_argument("--manifest", required=True)
    p_record.add_argument("--validate-json", required=True, help="a report validate's own --json wrote")
    p_record.add_argument("--environment", default="dosbox-x")
    p_record.add_argument("--tag", required=True, help="results/<tag>.json filename + the validated: entry's identity")
    p_record.add_argument("--date", default=None, help="default: today (UTC-agnostic, matches existing entries)")
    p_record.add_argument("--note", default=None)
    p_record.set_defaults(func=cmd_record)

    p_all = sub.add_parser(
        "all", help="inspect -> convert -> repack -> layout(x2) -> validate -> record, from one manifest")
    p_all.add_argument("game_file")
    p_all.add_argument("--workdir", required=True)
    p_all.add_argument("--dest", required=True)
    p_all.add_argument("--name", required=True, help="8.3-safe base name, e.g. NOTES")
    p_all.add_argument("--manifest", required=True, help="tests/games/<id>/manifest.yaml (must have a validate: block)")
    p_all.add_argument("--tier-rate", type=int, default=11025)
    p_all.add_argument("--tag-prefix", default="PGVAL")
    p_all.add_argument("--environment", default="dosbox-x")
    p_all.add_argument("--note", default=None)
    p_all.set_defaults(func=cmd_all)

    args = ap.parse_args()
    result = args.func(args)
    if args.cmd in ("validate", "check", "record", "all") and result is not None:
        ok = result[1] if isinstance(result, tuple) else result
        if ok is False:
            sys.exit(1)


if __name__ == "__main__":
    main()
