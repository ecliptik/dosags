#!/usr/bin/env python3
"""
build_fixture.py -- generates a minimal, throwaway synthetic AGS game
package (a .ags CLIB v6 single-file-library container) just large enough
to get engine_init_gamedata() to succeed and InitGameState() past every
hard gate between it and the graphics-mode-switch code, for the
TITLE_SCREEN milestone. NOT the real hand-authored first test game
PLAN.md describes -- this is a bring-up artifact only, thrown away once
a real test game exists.

Byte layout derived by reading the pinned AGS source (vendor/ags/) end
to end for the exact GameDataVersion chosen here (kGameVersion_250 == 18,
the floor OpenMainGameFileBase() accepts), not guessed and not trusted
from a first pass -- several intermediate conclusions in this file's own
history were wrong until checked against the real enum values in
Common/ac/game_version.h (e.g. kGameVersion_272 == 32, so 18 is NOT
">" it, which flips which branch several functions below take).

Every field below is annotated with the exact function/line that reads
it and the version-gate reasoning for why that branch executes at
DataVersion=18. Key source files:
  - Common/data/multifilelib.cpp (MFLUtil::ReadSingleFileLib, CLIB v6)
  - Common/game/main_game_file.cpp (ReadGameData, the real call order)
  - Common/ac/gamesetupstructbase.cpp / gamesetupstruct.cpp
  - Common/ac/characterinfo.cpp (CharacterInfo::ReadFromFile)
  - Common/gui/guimain.cpp (GUI::ReadGUI)
  - Common/game/interactions.cpp (Interaction::CreateFromStream)
  - Common/font/wfnfont.cpp (WFNFont::ReadFromFile)

License: MIT (this file, dosags's own). See LICENSE in repo root.
"""
import struct
import sys

CLIB_SIGNATURE = b"CLIB\x1a"
MFL_VERSION_SINGLELIB = 6
SINGLE_FILE_PSW_LEN = 13  # Common/data/multifilelib.cpp's SingleFilePswLen

MAIN_GAME_SIGNATURE = b"Adventure Creator Game File v2"  # main_game_file.cpp:46, GetLength()==30
assert len(MAIN_GAME_SIGNATURE) == 30
GAME_VERSION_250 = 18  # kGameVersion_250 -- the floor OpenMainGameFileBase() accepts (< 18 -> too old)

MAX_OPTIONS = 100
MAXGLOBALMES = 500
NUM_INTS_RESERVED = 16
MAX_INV = 301                    # characterinfo.h:28
LEGACY_MAX_CHAR_NAME_LEN = 40     # characterinfo.h:69
LEGACY_MAX_SCRIPT_NAME_LEN = 20   # common_defines.h:24
LEGACY_MAX_SPRITES_V25 = 6000     # common_defines.h:32
GUIMAGIC = 0xcafebeef             # guidefines.h:17
KGUIVERSION_214 = 100             # guidefines.h:58 -- GameGuiVersion below this reuses itself as gui_count
KINTERACTIONVERSION_INITIAL = 1   # interactions.h:134
SCOM_VERSION_SECTIONS = 83        # cc_internal.h:21
SCOM_VERSION_321 = 90             # cc_internal.h:22 (== SCOM_VERSION_CURRENT)
ENDFILESIG = 0xbeefcafe           # cc_internal.h:131


def pack_filename(name: bytes) -> bytes:
    """13-byte fixed filename buffer per SingleFilePswLen, NUL-padded."""
    assert len(name) < SINGLE_FILE_PSW_LEN, name
    return name + b"\x00" * (SINGLE_FILE_PSW_LEN - len(name))


def build_clib(assets):
    """assets: list of (filename: bytes, data: bytes). Returns full CLIB
    v6 container bytes. Multi-asset layout confirmed directly from
    MFLUtil::ReadSingleFileLib (multifilelib.cpp:211-244): filenames are
    all read first, then all sizes, then flags/ratio skipped, then
    assets are laid out back-to-back starting right after that."""
    n = len(assets)
    header = bytearray()
    header += CLIB_SIGNATURE
    header += struct.pack("<b", MFL_VERSION_SINGLELIB)  # lib_version (int8)
    header += struct.pack("<b", 0)  # passwmodifier
    header += struct.pack("<b", 0)  # unused byte
    header += struct.pack("<H", n)  # asset_count (uint16 LE)
    header += b"\x00" * SINGLE_FILE_PSW_LEN  # password dooberry (skipped, content irrelevant)
    for name, _ in assets:
        header += pack_filename(name)
    for _, data in assets:
        header += struct.pack("<I", len(data))  # Size (uint32 LE)
    header += b"\x00" * (2 * n)  # flags & ratio (skipped)
    payload = b"".join(data for _, data in assets)
    return bytes(header) + payload


def build_main_game_file_header(data_version=GAME_VERSION_250):
    """OpenMainGameFileBase() (main_game_file.cpp:162-191): 30-byte
    signature, int32 DataVersion, then a length-prefixed CompiledWith
    string (StrUtil::ReadString), read unconditionally once
    DataVersion >= kGameVersion_230(12) -- true here."""
    buf = bytearray()
    buf += MAIN_GAME_SIGNATURE
    buf += struct.pack("<i", data_version)
    buf += struct.pack("<i", 0)  # CompiledWith: empty string, 0-length prefix
    return bytes(buf)


KGAMERESOLUTION_320X200 = 1  # gamestructdefines.h:175
KGAMERESOLUTION_320X240 = 2  # gamestructdefines.h:176

def build_gamesetupstructbase(numfonts=1, color_depth_bytes=1, numcharacters=1, playercharacter=0,
                               resolution_type=KGAMERESOLUTION_320X240):
    """GameSetupStructBase::ReadFromFile() (gamesetupstructbase.cpp:89-147).
    color_depth_bytes is BYTES per pixel (GetColorDepth() = color_depth*8),
    so 1 == 8bpp, 2 == 16bpp.

    resolution_type defaults to kGameResolution_320x240(2), a named enum
    value with no version gate, deliberately NOT kGameResolution_Default(0)
    (which resolves to 320x200 for an 8-bit game per an earlier empirical
    run) and NOT kGameResolution_Custom(8) (its explicit width/height
    fields are only read for data_ver >= kGameVersion_330(43), far above
    our chosen DataVersion(18) -- they would silently not be read at all).
    PLAN.md's Measured constants record 320x200 as having NO VESA mode
    under this DOSBox-X setup (falls back to a default XRGB8888 surface
    regardless of the bpp hint), while 320x240 is a clean, already-
    validated VESA mode (BOOTSTRAP-0 probe 3). Choosing 320x240 first
    isolates the window-surface/palette code paths from that separate,
    already-understood fallback behavior; 320x200 is worth a follow-up
    run once 320x240 is confirmed working, to observe the fallback path
    deliberately rather than by surprise."""
    buf = bytearray()
    buf += b"\x00" * 50            # gamename (String::ReadCount, 50 bytes)
    buf += struct.pack("<h", 0)    # alignment padding to int32
    buf += struct.pack(f"<{MAX_OPTIONS}i", *([0] * MAX_OPTIONS))  # options[100]
    buf += b"\x00" * 256           # paluses[256] (uint8_t)
    buf += b"\x00" * (256 * 4)     # defpal[256] (RGB = 4 bytes each)
    buf += struct.pack("<i", 0)    # numviews
    buf += struct.pack("<i", numcharacters)  # numcharacters -- MUST be >=1: engine.cpp:676
                                              # null-derefs playerchar->view otherwise (setup_player_character())
    buf += struct.pack("<i", playercharacter)  # playercharacter
    buf += struct.pack("<i", 0)    # totalscore
    buf += struct.pack("<h", 0)    # numinvitems (int16)
    buf += struct.pack("<h", 0)    # alignment padding
    buf += struct.pack("<i", 0)    # numdialog
    buf += struct.pack("<i", 0)    # numdlgmessage
    buf += struct.pack("<i", numfonts)         # numfonts -- game_init.cpp:464-465 hard-fails at 0
    buf += struct.pack("<i", color_depth_bytes)  # color_depth (bytes/pixel)
    buf += struct.pack("<i", 0)    # target_win
    buf += struct.pack("<i", 0)    # dialog_bullet
    buf += struct.pack("<H", 0)    # inv_hot_color (uint16)
    buf += struct.pack("<H", 0)    # inv_hot_cross_color (uint16)
    buf += struct.pack("<i", 1)    # uniqueid (arbitrary nonzero)
    buf += struct.pack("<i", 0)    # numgui (overwritten later by GUI::ReadGUI's own count anyway)
    buf += struct.pack("<i", 0)    # numcursors
    buf += struct.pack("<i", resolution_type)  # resolution_type
    # (no width/height fields: only present if resolution_type == kGameResolution_Custom(8))
    buf += struct.pack("<i", 0)    # default_lipsync_frame
    buf += struct.pack("<i", 0)    # inv_hot_sprite
    buf += struct.pack(f"<{NUM_INTS_RESERVED}i", *([0] * NUM_INTS_RESERVED))  # reserved[16]
    buf += struct.pack("<I", 0)    # ExtensionOffset (uint32) = 0 -> no extension blocks
    buf += struct.pack(f"<{MAXGLOBALMES}i", *([0] * MAXGLOBALMES))  # HasMessages[500] (all false -> read_messages is 0 bytes)
    buf += struct.pack("<i", 0)    # HasWordsDict = false -> skips word dictionary read
    buf += struct.pack("<i", 0)    # globalscript dummy pointer
    buf += struct.pack("<i", 0)    # chars dummy pointer
    buf += struct.pack("<i", 1)    # HasCCScript = true -- InitGameState() hard-fails at game_init.cpp:555-556
                                    # if ents.GlobalScript is null; a global script is not optional
    return bytes(buf)


def build_read_savegame_info():
    """gamesetupstruct.cpp:56-64: `if (data_ver > kGameVersion_272)`.
    kGameVersion_272 == 32 (game_version.h); our DataVersion(18) is NOT
    greater than 32, so this ENTIRE block (guid/saveGameFileExtension/
    saveGameFolderName) is skipped. 0 bytes."""
    return b""


def build_font_infos_legacy(numfonts=1):
    """gamesetupstruct.cpp's read_font_infos (66-104): DataVersion(18) <
    kGameVersion_350(50), so the LEGACY branch runs: 1 byte per font
    (SetFontInfoFromLegacyFlags), then 1 more byte per font (Outline),
    then `if (data_ver < kGameVersion_341(48)) return;` -- 18 < 48 is
    true, so it returns immediately without reading YOffset/LineSpacing.
    2 bytes per font."""
    buf = bytearray()
    buf += bytes(numfonts)  # legacy flags byte per font: 0 -> Flags=0, Size=0 (FFLG_LEGACY_SIZEMASK & 0)
    buf += bytes(numfonts)  # Outline byte per font: 0
    return bytes(buf)


def build_sprite_flags_padding():
    """main_game_file.cpp's ReadSpriteFlags (817-831): DataVersion(18) <
    kGameVersion_256(24), so `sprcount = LEGACY_MAX_SPRITES_V25` (a fixed
    constant, NOT read from the stream) and then it unconditionally
    reads that many raw bytes. Content is irrelevant (sprite flags,
    consulted only much later by engine_init_sprites(), which runs
    after window creation) but the STREAM POSITION must actually advance
    by this many real bytes so everything after it lands correctly."""
    return b"\x00" * LEGACY_MAX_SPRITES_V25


def build_interaction_record(evt_count=0):
    """Interaction::CreateFromStream (interactions.cpp:335-371): a hard
    version check (must equal kInteractionVersion_Initial or the whole
    game load fails), then an event count. 0 events -> no further bytes."""
    return struct.pack("<i", KINTERACTIONVERSION_INITIAL) + struct.pack("<i", evt_count)


def build_interaction_scripts_legacy(numcharacters=1, numinvitems=0):
    """gamesetupstruct.cpp's read_interaction_scripts (130-178):
    `if (data_ver > kGameVersion_272)` -- false at 18, so the 2.x (else)
    branch runs: one Interaction record per character, then one per
    inventory item (numinvitems=0 here -> none), and then -- easy to
    miss reading the function only partway, as an earlier pass of this
    investigation did at real cost -- an UNCONDITIONAL trailing
    `numIntrVars = in->ReadInt32()` (line 173) followed by
    `intrVars[i].Read(in)` for i in 0..numIntrVars (line 174-175),
    regardless of numcharacters/numinvitems. Omitting this field left
    the stream one int32 short, so this read consumed the next real
    bytes in the stream (this fixture's own ccscript "SCOM" signature)
    as a garbage numIntrVars value (~1.3 billion), driving
    intrVars[i].Read() far out of bounds -- a real, reproducible crash
    that had nothing to do with DJGPP, the toolchain, or AssetManager
    despite extensive isolated probing before this line was found.
    numIntrVars=0 makes the trailing loop 0 bytes."""
    buf = bytearray()
    for _ in range(numcharacters):
        buf += build_interaction_record(0)
    for _ in range(numinvitems):
        buf += build_interaction_record(0)
    buf += struct.pack("<i", 0)  # numIntrVars = 0
    return bytes(buf)


def build_minimal_ccscript():
    """ccScript::Read (cc_script.cpp:118-198): "SCOM" signature, a file
    version <= SCOM_VERSION_CURRENT(90), then globaldata/code/strings
    sizes (all 0 here -- no data blocks follow when a size is 0),
    fixups/imports/exports counts (all 0), a sections list (present
    since our chosen fileVer(90) >= SCOM_VERSION_SECTIONS(83), count 0),
    and a mandatory ENDFILESIG trailer. This is main_game_file.cpp's
    ReadGameData() block gated on `sinfo.HasCCScript` (1134-1146): once
    the global script itself parses, ReadDialogScript() is a 0-byte
    no-op (data_ver(18) <= kGameVersion_310) and so is
    ReadScriptModules() (data_ver(18) < kGameVersion_270)."""
    buf = bytearray()
    buf += b"SCOM"
    buf += struct.pack("<i", SCOM_VERSION_321)  # fileVer
    buf += struct.pack("<I", 0)  # globaldatasize
    buf += struct.pack("<I", 0)  # codesize
    buf += struct.pack("<I", 0)  # stringssize
    buf += struct.pack("<I", 0)  # numfixups
    buf += struct.pack("<I", 0)  # numimports
    buf += struct.pack("<I", 0)  # numexports
    buf += struct.pack("<I", 0)  # numsections (fileVer >= SCOM_VERSION_SECTIONS)
    buf += struct.pack("<I", ENDFILESIG)
    return bytes(buf)


def build_views_none():
    """main_game_file.cpp's ReadViews (271-290): resizes to numviews(0)
    then loops 0 times regardless of which version branch is taken.
    0 bytes."""
    return b""


def build_legacy_251_skip_field():
    """main_game_file.cpp:1150-1155: `if (data_ver <= kGameVersion_251(19))
    { count = ReadInt32(); Seek(count*0x204); }` -- DataVersion(18) <= 19
    is true, so this DOES execute. Write count=0 explicitly (not relying
    on EOF fill, since real bytes for read_characters follow right after
    this in the stream and must not be misaligned)."""
    return struct.pack("<i", 0)


def build_character_info(view=-1, defview=-1, talkview=-1, thinkview=-1,
                          idleview=-1, blinkview=-1):
    """CharacterInfo::ReadFromFile (characterinfo.cpp:22-89), the
    non-savegame (game data) variant. view/defview/talkview/thinkview/
    idleview/blinkview default to -1 (no view assigned) so
    engine_init_game_settings() (engine.cpp:676's `if (playerchar->view
    >= 0)`) takes its "no view" branch instead of indexing an empty
    Views vector (numviews=0)."""
    buf = bytearray()
    buf += struct.pack("<i", defview)
    buf += struct.pack("<i", talkview)
    buf += struct.pack("<i", view)
    buf += struct.pack("<i", 0)    # room
    buf += struct.pack("<i", 0)    # [UNUSED] prevroom
    buf += struct.pack("<i", 0)    # x
    buf += struct.pack("<i", 0)    # y
    buf += struct.pack("<i", 0)    # [UNUSED] wait
    buf += struct.pack("<i", 0)    # flags
    buf += struct.pack("<h", 0)    # [UNUSED] following
    buf += struct.pack("<h", 0)    # [UNUSED] follow_info
    buf += struct.pack("<i", idleview)
    buf += struct.pack("<h", 0)    # idledelay
    buf += struct.pack("<h", 0)    # [UNUSED] idleleft
    buf += struct.pack("<h", 0)    # transparency
    buf += struct.pack("<h", 0)    # baseline
    buf += struct.pack("<i", 0)    # [UNUSED] activeinv
    buf += struct.pack("<i", 0)    # talkcolor
    buf += struct.pack("<i", thinkview)
    buf += struct.pack("<h", blinkview)
    buf += struct.pack("<h", 0)    # [UNUSED] blinkinterval
    buf += struct.pack("<h", 0)    # [UNUSED] blinktimer
    buf += struct.pack("<h", 0)    # [UNUSED] blinkframe
    buf += struct.pack("<h", 0)    # walkspeed_y
    buf += struct.pack("<h", 0)    # [UNUSED] pic_yoffs
    buf += struct.pack("<i", 0)    # [RESERVED] z
    buf += struct.pack("<i", 0)    # [UNUSED] walkwait
    buf += struct.pack("<h", 0)    # speech_anim_speed
    buf += struct.pack("<h", 0)    # idle_anim_speed
    buf += struct.pack("<h", 0)    # blocking_width
    buf += struct.pack("<h", 0)    # blocking_height
    buf += struct.pack("<i", 0)    # index_id
    buf += struct.pack("<h", 0)    # blocking_x
    buf += struct.pack("<h", 0)    # blocking_y
    buf += struct.pack("<h", 0)    # [UNUSED] loop
    buf += struct.pack("<h", 0)    # [UNUSED] frame
    buf += struct.pack("<h", 0)    # [UNUSED] walking
    buf += struct.pack("<h", 0)    # [UNUSED] animating
    buf += struct.pack("<h", 0)    # walkspeed
    buf += struct.pack("<h", 0)    # animspeed
    buf += struct.pack(f"<{MAX_INV}h", *([0] * MAX_INV))  # inv[MAX_INV]
    buf += struct.pack("<h", 0)    # [UNUSED] actx
    buf += struct.pack("<h", 0)    # [UNUSED] acty
    buf += b"\x00" * LEGACY_MAX_CHAR_NAME_LEN    # name
    buf += b"\x00" * LEGACY_MAX_SCRIPT_NAME_LEN  # scrname
    buf += struct.pack("<b", 1)    # on
    buf += struct.pack("<b", 0)    # alignment padding
    return bytes(buf)


def build_gui_minimal():
    """GUI::ReadGUI (guimain.cpp:1158-1182): a hard-checked magic number
    (GUIMAGIC) or the whole load fails, then a GameGuiVersion int32.
    With GameGuiVersion(0) < kGuiVersion_214(100), gui_count is reused
    AS that version value itself (0), giving zero GUI entries, and
    GameGuiVersion is reset to kGuiVersion_Initial internally."""
    return struct.pack("<I", GUIMAGIC) + struct.pack("<i", 0)


# After GUI::ReadGUI, main_game_file.cpp's ReadGameData continues:
#   - ReadPlugins: skipped, DataVersion(18) < kGameVersion_255(22)
#   - read_customprops: skipped, DataVersion(18) < kGameVersion_256(24)
#   - read_audio: skipped, DataVersion(18) < kGameVersion_320(41)
#   - read_room_names: skipped, options[OPT_DEBUGMODE] == 0
#   - `if (data_ver <= kGameVersion_350(50)) return HGameFileError::None();`
#     18 <= 50 -> returns success right here. No more bytes needed at all.


WFN_MINIMAL = (
    b"WGT Font File  "      # 15-byte signature, wfnfont.cpp:23-24
    + struct.pack("<H", 17)  # table_addr = 17 (WFN_FILE_SIG_LENGTH + sizeof(uint16_t)), the minimum allowed
    + b"\x00"                # 1 padding byte so table_addr(17) < file length(18) per wfnfont.cpp:66-72
)


def build_game28_dta(color_depth_bytes=1, resolution_type=KGAMERESOLUTION_320X240):
    return (
        build_main_game_file_header()
        + build_gamesetupstructbase(numfonts=1, color_depth_bytes=color_depth_bytes,
                                     numcharacters=1, playercharacter=0,
                                     resolution_type=resolution_type)
        + build_read_savegame_info()
        + build_font_infos_legacy(numfonts=1)
        + build_sprite_flags_padding()
        + build_interaction_scripts_legacy(numcharacters=1, numinvitems=0)
        + build_minimal_ccscript()  # HasWordsDict=false already skips that block (0 bytes) before this
        + build_views_none()
        + build_legacy_251_skip_field()
        + build_character_info()
        + build_gui_minimal()
    )


def main():
    color_depth_bytes = 1  # 1 == 8bpp (INDEX8), 2 == 16bpp (RGB565)
    if len(sys.argv) > 2 and sys.argv[2] == "16":
        color_depth_bytes = 2
    # Third arg selects the resolution_type -- default stays 320x240 (the
    # already-validated VESA mode this fixture originally isolated the
    # window-surface/palette code paths with, per this function's own
    # docstring above). "320x200" selects kGameResolution_320x200(1) to
    # deliberately exercise the VESA-mode-absent fallback path PLAN.md's
    # Measured Constants documents (falls back to a default XRGB8888
    # surface regardless of the bpp hint) instead of hitting it by
    # surprise with a real game later.
    resolution_type = KGAMERESOLUTION_320X240
    if len(sys.argv) > 3 and sys.argv[3] == "320x200":
        resolution_type = KGAMERESOLUTION_320X200
    game_payload = build_game28_dta(color_depth_bytes, resolution_type)
    clib = build_clib([
        (b"game28.dta", game_payload),
        (b"agsfnt0.wfn", WFN_MINIMAL),
    ])
    out_path = sys.argv[1] if len(sys.argv) > 1 else "game.ags"
    with open(out_path, "wb") as f:
        f.write(clib)
    res_label = "320x200" if resolution_type == KGAMERESOLUTION_320X200 else "320x240"
    print(f"wrote {out_path}: {len(clib)} bytes (game28.dta payload: {len(game_payload)} bytes, "
          f"color_depth={color_depth_bytes * 8}bpp, resolution={res_label})")


if __name__ == "__main__":
    main()
