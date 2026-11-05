#!/usr/bin/env python3
"""flatten-alpha.py -- bake sprite-source PNG alpha into AGS's mask colour
before the Wine AGS Editor compiles a package at a non-32-bit colour depth.

Why this step exists (2026-09-15, "black boxes around sprites" root cause,
see PLAN.md's "Known graphical glitch" section):

  * Upstream AGS Quest is authored at TrueColor with alpha-channel PNG
    sprites (Game.agf: ImportAlphaChannel=True, ImportMethod=LeaveAsIs).
    Its acsprset.spr is gitignored upstream, so when packages/agsquest/
    overlay/Game.agf.patch retargets <ColorDepth> to HighColor (16-bit) and
    build-package.sh runs `AGSEditor.exe /compile`, the editor recreates
    every sprite from its <Sprite><Source><FileName> PNG
    (Editor/AGS.Editor/Tasks.cs RecreateSpriteFileFromSources).
  * The editor only honours a PNG's alpha channel when the game is
    TrueColor: Editor/AGS.Editor/Utils/SpriteTools.cs AdjustImportParams,
    `ImportAlpha = options.ImportAlpha && ColorDepth == GameColorDepth.TrueColor
    && bmp.HasAlpha()`. At HighColor the alpha is simply dropped, and
    ImportMethod=LeaveAsIs applies no colour key -- only pixels that are
    literally RGB (255,0,255) become the mask colour.
  * The source PNGs carry RGB black under their fully transparent pixels
    (e.g. Objects/TreehouseBackDoorClosed.png: 3209/4620 pixels alpha=0,
    all RGB (0,0,0)), so those pixels landed in the package as OPAQUE
    black (0xFF000000) and every engine -- the DOS port and the official
    Linux engine, byte-identically -- drew a black box around the sprite.

What it does: for every PNG referenced by a <Sprite><Source><FileName>
entry in Game.agf (parsing Game.agf, not globbing, so a referenced file
cannot be missed), rewrite

  alpha <= 127  ->  (255, 0, 255, 0)   AGS's mask colour; same threshold as
                                        the engine's own
                                        ReplaceHalfAlphaWithRGBMask()
                                        (Common/gfx/bitmap.h, applied to a
                                        32-bit alpha sprite loaded into a
                                        16-bit game), so the 16-bit package
                                        matches what a TrueColor game
                                        produces at load time.
  alpha >= 128  ->  (r, g, b, 255)      opaque.

The mask pixels keep alpha 0 on purpose: at HighColor the editor discards
alpha and keys on the RGB (this is exactly how the character sheets'
existing magenta+alpha0 pixels already came through correctly), while at
TrueColor alpha 0 is still "transparent", so the same rewritten sources
build correctly at either depth.

Pillow is used when importable; otherwise ImageMagick's `convert` (-fx)
with an approximate changed-pixel count. Fails loudly if neither exists
or a referenced source file is missing.

Usage: flatten-alpha.py <path/to/Game.agf>
"""
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

MASK = (255, 0, 255, 0)
HALF_ALPHA = 127  # ReplaceHalfAlphaWithRGBMask threshold: alpha <= 127 -> mask


def referenced_sources(agf_path):
    """Every distinct <Sprite><Source><FileName> in Game.agf, in order."""
    root = ET.parse(agf_path).getroot()
    seen = []
    for spr in root.iter("Sprite"):
        fn = spr.findtext("Source/FileName")
        if not fn:
            continue  # no import source recorded (e.g. the slot-0 placeholder)
        fn = fn.replace("\\", os.sep)
        if fn not in seen:
            seen.append(fn)
    return seen


def flatten_pillow(path):
    from PIL import Image
    im = Image.open(path)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    if not has_alpha:
        return None  # nothing to bake, leave the file byte-identical
    im = im.convert("RGBA")
    src = list(im.getdata())
    out = []
    changed = 0
    for px in src:
        if px[3] <= HALF_ALPHA:
            new = MASK
        elif px[3] != 255:
            new = (px[0], px[1], px[2], 255)
        else:
            new = px
        if new != px:
            changed += 1
        out.append(new)
    if changed:
        im.putdata(out)
        im.save(path, format="PNG")
    return changed, len(src)


def flatten_imagemagick(path):
    thr = "a<0.5"  # 127/255 = 0.498 -> mask, 128/255 = 0.502 -> opaque
    # Approximate count first (alpha < 128 pixels), before rewriting.
    total = subprocess.run(
        ["convert", path, "-format", "%[fx:w*h]", "info:"],
        check=True, capture_output=True, text=True).stdout.strip()
    trans = subprocess.run(
        ["convert", path, "-alpha", "extract", "-threshold", "49.9%",
         "-format", "%[fx:round(w*h*(1-mean))]", "info:"],
        check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(
        ["convert", path, "-alpha", "on",
         "-channel", "R", "-fx", f"{thr}?1:u.r",
         "-channel", "G", "-fx", f"{thr}?0:u.g",
         "-channel", "B", "-fx", f"{thr}?1:u.b",
         "-channel", "A", "-fx", f"{thr}?0:1",
         "+channel", "PNG32:" + path],
        check=True)
    return int(float(trans)), int(float(total))


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: flatten-alpha.py <Game.agf>")
    agf = sys.argv[1]
    project_dir = os.path.dirname(os.path.abspath(agf))

    try:
        import PIL  # noqa: F401
        backend = "pillow"
    except ImportError:
        if subprocess.run(["which", "convert"], capture_output=True).returncode == 0:
            backend = "imagemagick"
        else:
            sys.exit("flatten-alpha.py: FATAL -- neither Pillow (python3 PIL) nor "
                     "ImageMagick `convert` is available; cannot flatten sprite alpha")
    if os.environ.get("FLATTEN_ALPHA_FORCE_IM") == "1":
        backend = "imagemagick"

    sources = referenced_sources(agf)
    if not sources:
        sys.exit(f"flatten-alpha.py: FATAL -- no <Sprite><Source><FileName> entries found in {agf}")

    files_changed = 0
    pixels_changed = 0
    skipped = 0
    missing = 0
    for rel in sources:
        path = os.path.join(project_dir, rel)
        if not os.path.isfile(path):
            # Wine's filesystem lookup is case-insensitive, so the editor
            # would still find a case-mismatched file -- mirror that.
            d, b = os.path.split(path)
            cands = [f for f in os.listdir(d) if f.lower() == b.lower()] if os.path.isdir(d) else []
            if cands:
                path = os.path.join(d, cands[0])
            else:
                # Upstream AGS Quest @064a14d really does reference one
                # nonexistent source (slot 6, GUIs/TitleScreenMageHat.png);
                # the editor tolerates it (emits an empty placeholder
                # sprite), so warn rather than fail the build here.
                print(f"flatten-alpha.py: WARNING -- Game.agf references missing sprite source {rel} "
                      f"(the editor will emit a placeholder sprite for it)")
                missing += 1
                continue
        if not path.lower().endswith(".png"):
            print(f"flatten-alpha.py: skip (not PNG, no alpha channel possible) {rel}")
            skipped += 1
            continue
        if backend == "pillow":
            res = flatten_pillow(path)
        else:
            res = flatten_imagemagick(path)
        if res is None:
            print(f"flatten-alpha.py: skip (no alpha channel) {rel}")
            skipped += 1
            continue
        changed, total = res
        if changed:
            files_changed += 1
            pixels_changed += changed
        print(f"flatten-alpha.py: {rel}: {changed}/{total} pixels rewritten")

    print(f"flatten-alpha.py: done ({backend}) -- {len(sources)} referenced sources, "
          f"{files_changed} files changed, {pixels_changed} pixels rewritten, "
          f"{skipped} skipped, {missing} missing")


if __name__ == "__main__":
    main()
