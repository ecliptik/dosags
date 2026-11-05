#!/usr/bin/env python3
"""gen_agf.py -- write this fixture's Game.agf (AGS Editor 3.6.3 project
XML) from the small spec below. License: MIT (dosags's own tooling).

PLAN.md called for a hand-authored Game.agf. It is generated instead,
because the three depth builds (BENCH8/16/32) must differ in exactly one
setting and ~2,000 lines of hand-kept XML would not stay that way. The
element and setting NAMES are the Editor's schema (what Tools/data/
agfreader.cpp reads); every VALUE is ours -- nothing here comes from an
AGS template project.

Usage: gen_agf.py <palette.json> <out/Game.agf> [--depth 8|16|32]
"""
import json
import sys
import xml.etree.ElementTree as ET

DEPTH_NAME = {8: "Palette", 16: "HighColor", 32: "TrueColor"}

# Sprite slots -- must match assets/generate_assets.py.
SLOT_PLACEHOLDER, SLOT_CURSOR, SLOT_KEY_INV, SLOT_KEY_OBJ = 0, 1, 2, 3
SLOT_EGO, SLOT_SPINNER = 10, 30
SLOT_GLITCH_ALPHA, SLOT_GLITCH_MAGENTA = 40, 41
SPRITE_SIZES = {0: (8, 8), 1: (12, 16), 2: (16, 16), 3: (14, 10)}
SPRITE_SIZES.update({SLOT_EGO + i: (16, 32) for i in range(12)})
SPRITE_SIZES.update({SLOT_SPINNER + i: (24, 24) for i in range(4)})

GAME_ID = 1486066          # arbitrary, ours; room files carry the same
GUID = "{b3e0c8d2-4866-4f40-9a8b-be9c48000001}"


def sub(parent, tag, text=None, **attrs):
    e = ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})
    if text is not None:
        e.text = str(text)
    return e


def settings(g, depth):
    s = sub(g, "Settings")
    vals = [
        ("AllowRelativeAssetResolutions", "False"), ("AlwaysDisplayTextAsSpeech", "False"),
        ("AndroidAppVersionCode", 1), ("AndroidAppVersionName", "1.0.0.0"),
        ("AndroidApplicationId", "org.dosags.bench"), ("AndroidBuildFormat", "ApkEmbedded"),
        ("AntiAliasFonts", "False"), ("AntiGlideMode", "True"), ("AttachDataToExe", "False"),
        ("AudioIndexer", 2), ("AutoMoveInWalkMode", "True"), ("BackwardsText", "False"),
        ("BuildTargets", "DataFile"), ("ClipGUIControls", "True"),
        ("ColorDepth", DEPTH_NAME[depth]), ("CompressSpritesType", "None"),
        ("CustomDataDir", ""), ("CustomResolution", "320,200"), ("DebugMode", "True"),
        ("DefaultRoomMaskResolution", 1), ("Description", "dosags benchmark fixture"),
        ("DeveloperName", "dosags"), ("DeveloperURL", ""), ("DialogOptionsBackwards", "False"),
        ("DialogOptionsBullet", 0), ("DialogOptionsGUI", 0), ("DialogOptionsGap", 0),
        ("DialogScriptNarrateFunction", ""), ("DialogScriptSayFunction", ""),
        ("DisplayMultipleInventory", "False"), ("DisplaySingleDialogOption", "False"),
        ("EnforceNewAudio", "True"), ("EnforceNewStrings", "True"),
        ("EnforceObjectBasedScript", "True"), ("GUIAlphaStyle", "MultiplyTranslucenceSrcBlend"),
        ("GUIDAsString", GUID), ("GUIHandleOnlyLeftMouseButton", "False"), ("GameFPS", 40),
        ("GameFileName", "BENCH%d" % depth), ("GameName", "Bench %d-bit" % depth),
        ("GameTextEncoding", "utf-8"), ("GameTextLanguage", ""), ("Genre", "Benchmark"),
        ("GlobalSpeechAnimationDelay", 5), ("HandleInvClicksInScript", "True"),
        ("InventoryCursors", "True"), ("InventoryHotspotMarkerCrosshairColor", 0),
        ("InventoryHotspotMarkerDotColor", 0), ("InventoryHotspotMarkerSprite", 0),
        ("InventoryHotspotMarkerStyle", "None"), ("LeftToRightPrecedence", "True"),
        # LetterboxMode MUST stay False: with it on, the engine treats a
        # 320x200 game as 320x240 (Common/ac/gamesetupstructbase.cpp,
        # ResolutionTypeToSize) and the fixture could no longer exercise
        # the DOS backend's Mode 13h path, which is 320x200 exactly.
        ("LetterboxMode", "False"),
        ("MaximumScore", 0), ("MouseWheelEnabled", "False"), ("NumberDialogOptions", "None"),
        ("OptimizeSpriteStorage", "True"), ("PixelPerfect", "True"), ("PlaySoundOnScore", 0),
        ("ReleaseDate", "2026-09-17"), ("RenderAtScreenResolution", "UserDefined"),
        # Instant: a fade is N full presents and lands as stall ticks in
        # every record; scenes that want one ask for it from script.
        ("RoomTransition", "Instant"),
        ("RunGameLoopsWhileDialogOptionsDisplayed", "True"), ("SaveGameFileExtension", ""),
        ("SaveGameFolderName", "BENCH%d" % depth), ("SaveScreenshots", "False"),
        ("ScaleCharacterSpriteOffsets", "True"), ("ScaleMovementSpeedWithMaskResolution", "False"),
        ("ScriptAPIVersion", "Highest"), ("ScriptCompatLevel", "Highest"),
        ("SkipSpeech", "MouseOrKeyboardOrTimer"), ("SpeechPortraitSide", "Left"),
        ("SpeechStyle", "Lucasarts"), ("SplitResources", 0), ("SpriteAlphaStyle", "Improved"),
        ("TextBoxKeyClaimStyle", "All"), ("TextWindowGUI", 0), ("ThoughtGUI", 0),
        ("TranslateTextParser", "False"), ("TranslationExcludeFunctionCall", ""),
        ("TranslationExcludeScriptPrefix", ""), ("TranslationIncludeScriptPrefix", ""),
        ("TurnBeforeFacing", "False"), ("TurnBeforeWalking", "False"),
        ("TurnOrderPriority", "Clockwise"), ("UniqueID", GAME_ID),
        ("UseGlobalSpeechAnimationDelay", "False"), ("UseLowResCoordinatesInScript", "False"),
        ("UseOldCustomDialogOptionsAPI", "False"), ("UseOldKeyboardHandling", "False"),
        ("UseOldVoiceClipNaming", "False"), ("Version", "1.0.0.0"),
        ("WalkInLookMode", "False"), ("WhenInterfaceDisabled", "DisplayNormally"),
    ]
    for k, v in vals:
        sub(s, k, v)


def runtime_setup(g):
    r = sub(g, "RuntimeSetup")
    for k, v in [("AAScaledSprites", "False"), ("AutoLockMouse", "False"), ("CompressSaves", "True"),
                 ("CustomSavePath", ""), ("DigitalSound", "Default"), ("FullscreenDesktop", "True"),
                 ("FullscreenGameScaling", "ProportionalStretch"), ("GameScaling", "MaxInteger"),
                 ("GameScalingMultiplier", 1), ("GraphicsDriver", "Software"),
                 ("GraphicsFilter", "stdscale"), ("MouseSpeed", 1),
                 ("RenderAtScreenResolution", "False"), ("Rotation", "Unlocked"), ("ShowFPS", "False"),
                 ("SoundCacheSize", 8), ("SpriteCacheSize", 16), ("TextureCacheSize", 16),
                 ("TitleText", "Bench Setup"), ("TouchToMouseEmulation", "OneFinger"),
                 ("TouchToMouseMotionMode", "Direct"), ("Translation", ""),
                 ("UseCustomAppDataPath", "False"), ("UseCustomSavePath", "False"),
                 ("UseVoicePack", "False"), ("VSync", "False"), ("Windowed", "False")]:
        sub(r, k, v)
    sub(r, "CustomAppDataPath", IsNull="True")


def interactions(parent, count, handlers=None, module=None):
    i = sub(parent, "Interactions")
    if module:
        sub(i, "ScriptModule", module)
    for n in range(count):
        e = sub(i, "Event", Index=n)
        if handlers and n in handlers:
            e.text = handlers[n]


def main():
    args = [a for a in sys.argv[1:]]
    depth = 8
    if "--depth" in args:
        k = args.index("--depth")
        depth = int(args[k + 1])
        del args[k:k + 2]
    pal = json.load(open(args[0]))
    out = args[1]

    root = ET.Element("AGSEditorDocument", Version="3.0.3.2", VersionIndex="3060312",
                      EditorVersion="3.6.3.13")
    g = sub(root, "Game")
    settings(g, depth)
    runtime_setup(g)

    lip = sub(g, "LipSync")
    sub(lip, "Type", "None")
    sub(lip, "DefaultFrame", 0)
    fr = sub(lip, "Frames")
    for _ in range(20):
        sub(fr, "CharsForFrame")
    sub(g, "PropertyDefinitions")
    gm = sub(g, "GlobalMessages")
    for n in range(500, 1000):
        sub(gm, "Message", ID=n)
    sub(g, "OldInteractionVariables")
    sub(g, "Plugins")

    rooms = sub(sub(g, "Rooms"), "UnloadedRoomFolder", Name="Main")
    sub(rooms, "SubFolders")
    ur = sub(sub(rooms, "UnloadedRooms"), "UnloadedRoom")
    sub(ur, "Description", "Bench room")
    sub(ur, "Number", 1)

    # One GUI: the save/load menu. Text-only buttons (Image 0) -- no GUI art.
    gf = sub(sub(g, "GUIs"), "GUIFolder", Name="Main")
    sub(gf, "SubFolders")
    gui = sub(sub(gf, "GUIs"), "GUIMain")
    n = sub(gui, "NormalGUI")
    for k, v in [("BackgroundColor", 8), ("BackgroundImage", 0), ("BorderColor", 15),
                 ("Clickable", "True"), ("Height", 72), ("ID", 0), ("Left", 100),
                 ("Name", "gMenu"), ("OnClick", ""), ("PopupStyle", "Normal"), ("PopupYPos", 0),
                 ("Top", 40), ("Transparency", 0), ("Visible", "False"), ("Width", 120),
                 ("ZOrder", 0)]:
        sub(n, k, v)
    ctrls = sub(gui, "Controls")
    for cid, (name, text, top) in enumerate([("btnSave", "SAVE", 6), ("btnLoad", "LOAD", 28),
                                             ("btnClose", "CLOSE", 50)]):
        b = sub(ctrls, "GUIButton")
        for k, v in [("ClickAction", "RunScript"), ("Clickable", "True"), ("ClipImage", "False"),
                     ("Enabled", "True"), ("Font", 0), ("Height", 16), ("ID", cid), ("Image", 0),
                     ("Left", 10), ("Locked", "False"), ("MouseoverImage", 0), ("Name", name),
                     ("NewModeNumber", 0), ("OnClick", name + "_OnClick"), ("PushedImage", 0),
                     ("Text", text), ("TextAlignment", "MiddleCenter"), ("TextColor", 15),
                     ("Top", top), ("Visible", "True"), ("Width", 100), ("ZOrder", cid)]:
            sub(b, k, v)

    inv = sub(sub(g, "InventoryItems"), "InventoryItemFolder", Name="Main")
    sub(inv, "SubFolders")
    it = sub(sub(inv, "InventoryItems"), "InventoryItem")
    for k, v in [("CursorImage", SLOT_KEY_INV), ("Description", "Key"), ("HotspotX", 8),
                 ("HotspotY", 8), ("ID", 1), ("Image", SLOT_KEY_INV), ("Name", "iKey"),
                 ("PlayerStartsWithItem", "False")]:
        sub(it, k, v)
    sub(it, "Properties")
    interactions(it, 5)

    sub(sub(g, "TextParser"), "Words")

    cf = sub(sub(g, "Characters"), "CharacterFolder", Name="Main")
    sub(cf, "SubFolders")
    ch = sub(sub(cf, "Characters"), "Character")
    for k, v in [("AdjustSpeedWithScaling", "False"), ("AdjustVolumeWithScaling", "False"),
                 ("AnimationDelay", 4), ("Baseline", 0), ("BlinkingView", 0),
                 ("BlockingRectangle", "0,0,0,0"), ("Clickable", "False"),
                 ("DiagonalLoops", "False"), ("ID", 0), ("IdleAnimationDelay", 9),
                 ("IdleDelay", 20), ("IdleView", 0), ("MovementLinkedToAnimation", "True"),
                 ("MovementSpeed", 3), ("MovementSpeedX", 3), ("MovementSpeedY", 0),
                 ("NormalView", 1)]:
        sub(ch, k, v)
    sub(ch, "Properties")
    for k, v in [("RealName", "Ego"), ("ScriptName", "cEgo"), ("Solid", "True"),
                 ("SpeechAnimationDelay", 5), ("SpeechColor", 15), ("SpeechView", 0),
                 ("StartX", 40), ("StartY", 170), ("StartingRoom", 1), ("ThinkingView", 0),
                 ("Transparency", 0), ("TurnBeforeWalking", "False"), ("TurnWhenFacing", "False"),
                 ("UniformMovementSpeed", "True"), ("UseRoomAreaLighting", "False"),
                 ("UseRoomAreaScaling", "False")]:
        sub(ch, k, v)
    interactions(ch, 8, module="GlobalScript.asc")
    sub(g, "PlayerCharacter", 0)

    df = sub(sub(g, "Dialogs"), "DialogFolder", Name="Main")
    sub(df, "SubFolders")
    sub(df, "Dialogs")

    cur = sub(g, "Cursors")
    for cid, (name, std) in enumerate([("Walk to", "True"), ("Look at", "True"),
                                       ("Interact", "True"), ("Talk to", "True"),
                                       ("Use inventory", "False"), ("Pick up", "False"),
                                       ("Pointer", "False"), ("Wait", "False"),
                                       ("Usermode 1", "False"), ("Usermode 2", "False")]):
        c = sub(cur, "MouseCursor")
        for k, v in [("Animate", "False"), ("AnimateOnlyOnHotspots", "False"),
                     ("AnimateOnlyWhenMoving", "False"), ("AnimationDelay", 5), ("HotspotX", 0),
                     ("HotspotY", 0), ("ID", cid), ("Image", SLOT_CURSOR), ("Name", name),
                     ("StandardMode", std), ("View", 0)]:
            sub(c, k, v)

    # One font slot, and it is the TTF (the spec's "one TTF slot actually
    # used"); Game.SpeechFont is pointed at it from game_start.
    f = sub(sub(g, "Fonts"), "Font")
    for k, v in [("AutoOutlineStyle", "Squared"), ("AutoOutlineThickness", 1),
                 ("CharacterSpacing", 0), ("CustomHeightValue", 0),
                 ("HeightDefinedBy", "NominalHeight"), ("ID", 0), ("LineSpacing", 0),
                 ("Name", "PressStart2P"), ("OutlineFont", 0), ("OutlineStyle", "None"),
                 ("PointSize", 8), ("SizeMultiplier", 1),
                 ("SourceFilename", "assets/PressStart2P-Regular.ttf"),
                 ("TTFMetricsFixup", "None"), ("VerticalOffset", 0)]:
        sub(f, k, v)

    p = sub(g, "Palette")
    for i, (r, gg, b) in enumerate(pal):
        sub(p, "PaletteEntry", Index=i, Type="Gamewide", Red=r, Green=gg, Blue=b)

    sub(sub(g, "GlobalVariables"), "Variables")

    sf = sub(sub(g, "Sprites"), "SpriteFolder", Name="Main")
    sub(sf, "SubFolders")
    spr = sub(sf, "Sprites")
    sizes = dict(SPRITE_SIZES)
    if depth != 8:
        sizes[SLOT_GLITCH_ALPHA] = (24, 24)
        sizes[SLOT_GLITCH_MAGENTA] = (24, 24)
    for slot in sorted(sizes):
        w, h = sizes[slot]
        alpha = depth != 8 and slot == SLOT_GLITCH_ALPHA
        s = sub(spr, "Sprite", Slot=slot, Width=w, Height=h,
                ColorDepth=8 if depth == 8 else 32, Resolution="Real",
                AlphaChannel="True" if alpha else "False")
        src = sub(s, "Source")
        for k, v in [("FileName", "sprites/spr%06d.png" % slot), ("OffsetX", 0), ("OffsetY", 0),
                     ("ImportHeight", h), ("ImportWidth", w), ("ImportAsTile", "False"),
                     ("Frame", 0), ("RemapToGamePalette", "False"), ("RemapToRoomPalette", "False"),
                     ("ImportMethod", "LeaveAsIs"), ("TransparentColorIndex", 0),
                     ("ImportAlphaChannel", "True" if alpha else "False")]:
            sub(src, k, v)

    vf = sub(sub(g, "Views"), "ViewFolder", Name="Main")
    sub(vf, "SubFolders")
    views = sub(vf, "Views")

    def view(vid, name, loops):
        v = sub(views, "View")
        sub(v, "ID", vid)
        sub(v, "Name", name)
        ls = sub(v, "Loops")
        for li, frames in enumerate(loops):
            lp = sub(ls, "Loop")
            sub(lp, "ID", li)
            sub(lp, "RunNextLoop", "False")
            fs = sub(lp, "Frames")
            for fi, image in enumerate(frames):
                vfm = sub(fs, "ViewFrame")
                for k, val in [("Delay", 0), ("Flipped", "False"), ("ID", fi), ("Image", image),
                               ("Sound", -1)]:
                    sub(vfm, k, val)

    # AGS loop order: 0 down, 1 left, 2 right, 3 up; frame 0 is standing.
    view(1, "VEGO", [[SLOT_EGO + d * 3 + f for f in range(3)] for d in range(4)])
    view(2, "VSPINNER", [[SLOT_SPINNER + f for f in range(4)]])
    sub(g, "DeletedViews")

    scf = sub(sub(g, "Scripts"), "ScriptFolder", Name="Main")
    sub(scf, "SubFolders")
    sah = sub(scf, "ScriptAndHeaders")
    for key, base in enumerate(("AutoPilot", "GlobalScript")):   # module order matters
        pair = sub(sah, "ScriptAndHeader")
        for wrap, ext, hdr in (("ScriptAndHeader_Header", ".ash", "True"),
                               ("ScriptAndHeader_Script", ".asc", "False")):
            sc = sub(sub(pair, wrap), "Script")
            for k, v in [("FileName", base + ext), ("Name", base), ("Description", ""),
                         ("Author", "dosags"), ("Version", "1"), ("Key", 1000 + key),
                         ("IsHeader", hdr)]:
                sub(sc, k, v)

    acf = sub(sub(g, "AudioClips"), "AudioClipFolder", Name="Main")
    sub(acf, "SubFolders")
    clips = sub(acf, "AudioClips")
    for cid, (name, ftype, fn, typ, rep) in enumerate(
            [("aTune", "MIDI", "audio/tune.mid", 2, "True"),
             ("aChime", "WAV", "audio/chime.wav", 3, "False")]):
        c = sub(clips, "AudioClip")
        for k, v in [("BundlingType", "InGameEXE"), ("DefaultPriority", "Normal"),
                     ("DefaultRepeat", rep), ("DefaultVolume", 100), ("FileType", ftype),
                     ("ID", cid), ("Index", cid), ("ScriptName", name), ("SourceFileName", fn),
                     ("Type", typ), ("FileLastModifiedDate", "2026-09-17 00:00:00Z")]:
            sub(c, k, v)
    dflt = sub(acf, "AudioClipFolder")
    for k, v in [("DefaultBundlingType", "InGameEXE"), ("DefaultPriority", "Normal"),
                 ("DefaultRepeat", "False"), ("DefaultType", 3), ("DefaultVolume", 100)]:
        sub(dflt, k, v)
    ats = sub(g, "AudioClipTypes")
    for tid, (name, compat, maxch, red) in enumerate([("Ambient Sound", "True", 1, 0),
                                                      ("Music", "True", 1, 0),
                                                      ("Sound", "False", 0, 0)], start=1):
        t = sub(ats, "AudioClipType")
        for k, v in [("BackwardsCompatibilityType", compat), ("CrossfadeClips", "No"),
                     ("MaxChannels", maxch), ("Name", name), ("TypeID", tid),
                     ("VolumeReductionWhileSpeechPlaying", red)]:
            sub(t, k, v)
    sub(g, "Translations")

    ET.indent(root, space="  ")
    ET.ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)
    print("gen_agf.py: depth %d -> %s" % (depth, out))


if __name__ == "__main__":
    main()
