#!/usr/bin/env python3
"""generate_assets.py -- every asset of the BENCH fixture, drawn or
synthesized from scratch by this script. No third-party art, samples or
templates. Original work, CC0 1.0 (no rights reserved).

Usage: generate_assets.py <out-dir> [--depth 8|16|32]

  --depth 8   (default) sprites and background are 8-bit paletted PNGs
              against the fixed palette below; index 0 is transparent in
              sprites (AGS's 8-bit rule).
  --depth 16/32  the same drawings as RGBA PNGs (index 0 -> alpha 0), plus
              the two glitch-regression sprites (a real-alpha one and a
              magenta-keyed one), which only make sense above 8-bit.

Output layout (consumed by ../build.sh):
  <out>/sprites/spr%06d.png   sprite slots (see SLOTS below)
  <out>/room1/bg.png, mask-hotspot.png, mask-walkarea.png,
              mask-walkbehind.png, mask-region.png
  <out>/audio/tune.mid, chime.wav
  <out>/palette.json          the 256-entry game palette, for gen_agf.py

Deterministic: same inputs, byte-identical outputs (no timestamps, no
randomness without a fixed seed).
"""
import json
import math
import os
import struct
import sys
import wave

from PIL import Image

W, H = 320, 200

# ------------------------------------------------------------ palette ----
EGA = [(0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170), (170, 0, 0),
       (170, 0, 170), (170, 85, 0), (170, 170, 170), (85, 85, 85),
       (85, 85, 255), (85, 255, 85), (85, 255, 255), (255, 85, 85),
       (255, 85, 255), (255, 255, 85), (255, 255, 255)]


def build_palette():
    pal = list(EGA)                                    # 0..15
    pal += [(v, v, v) for v in range(8, 256, 16)]      # 16..31 grey ramp
    steps = [0, 51, 102, 153, 204, 255]
    for r in steps:                                    # 32..247 colour cube
        for g in steps:
            for b in steps:
                pal.append((r, g, b))
    pal += [(255, 204, 170), (224, 160, 120), (120, 72, 40), (90, 54, 30),
            (60, 100, 60), (40, 60, 110), (200, 200, 230), (250, 240, 200)]
    assert len(pal) == 256
    return pal


PAL = build_palette()
SKIN, SKIN_D, WOOD, WOOD_D, MOSS, NAVY, PALE, CREAM = range(248, 256)


def cube(r, g, b):
    """Nearest colour-cube index for 0..5 component levels."""
    return 32 + r * 36 + g * 6 + b


def new_p(w, h, fill=0):
    im = Image.new("P", (w, h), fill)
    flat = []
    for c in PAL:
        flat += list(c)
    im.putpalette(flat)
    return im


MASK_RGBA = (255, 0, 255, 0)


def to_rgba(im):
    """Paletted drawing -> RGBA for a sprite WITHOUT an alpha channel:
    index 0 becomes AGS's 32-bit mask colour, magenta with alpha 0
    (0x00FF00FF, Allegro's MASK_COLOR_32). That exact value is what the
    engine keys on when it converts a non-alpha sprite to the game's depth
    (Engine/ac/draw.cpp PrepareSpriteForUseImpl -> ConvertBitmap keep_mask).
    The first version of this function wrote (0,0,0,0) -- "transparent" to
    an image editor, opaque BLACK to the engine, since a sprite flagged
    AlphaChannel=False has its alpha ignored: every sprite got a black box
    (seen by LOOKING at the first BENCH16 capture; the same data defect as
    the AGS Quest black-box report, PLAN.md 2026-09-16)."""
    out = Image.new("RGBA", im.size)
    src = im.load()
    dst = out.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            i = src[x, y]
            r, g, b = PAL[i]
            dst[x, y] = MASK_RGBA if i == 0 else (r, g, b, 255)
    return out


def rect(px, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px[x, y] = c


# ---------------------------------------------------------- background ----
PILLAR = (150, 52, 171, 150)       # x0, y0, x1, y1 -- the walk-behind
SIGN = (236, 62, 292, 96)          # the hotspot
FLOOR_TOP = 118


def draw_background():
    im = new_p(W, H, PALE)
    px = im.load()
    # back wall: light bricks (a light background is deliberate -- the
    # glitch-regression sprites are judged against it)
    for y in range(0, FLOOR_TOP):
        for x in range(W):
            row = y // 12
            off = 14 if row % 2 else 0
            mortar = (y % 12 == 0) or ((x + off) % 28 == 0)
            px[x, y] = 23 if mortar else CREAM
    # window
    rect(px, 40, 30, 110, 84, NAVY)
    rect(px, 44, 34, 106, 80, cube(2, 4, 5))
    rect(px, 74, 34, 76, 80, NAVY)
    rect(px, 44, 56, 106, 58, NAVY)
    # floor: wooden boards with perspective-free seams
    for y in range(FLOOR_TOP, H):
        for x in range(W):
            seam = (x % 40 == 0) or (y % 27 == 0)
            px[x, y] = WOOD_D if seam else WOOD
    rect(px, 0, FLOOR_TOP, W - 1, FLOOR_TOP + 1, WOOD_D)
    # sign (hotspot)
    rect(px, SIGN[0], SIGN[1], SIGN[2], SIGN[3], WOOD_D)
    rect(px, SIGN[0] + 3, SIGN[1] + 3, SIGN[2] - 3, SIGN[3] - 3, 14)
    for i in range(3):
        rect(px, SIGN[0] + 10, SIGN[1] + 9 + i * 8, SIGN[2] - 10, SIGN[1] + 11 + i * 8, 0 + 8)
    # pillar (drawn on the background; the walk-behind mask re-draws it
    # over the character)
    rect(px, PILLAR[0], PILLAR[1], PILLAR[2], PILLAR[3], 26)
    rect(px, PILLAR[0], PILLAR[1], PILLAR[0] + 3, PILLAR[3], 29)
    rect(px, PILLAR[2] - 3, PILLAR[1], PILLAR[2], PILLAR[3], 21)
    rect(px, PILLAR[0] - 4, PILLAR[3] - 6, PILLAR[2] + 4, PILLAR[3], 24)
    rect(px, PILLAR[0] - 4, PILLAR[1], PILLAR[2] + 4, PILLAR[1] + 6, 24)
    return im


def draw_mask(kind):
    im = new_p(W, H, 0)
    px = im.load()
    if kind == "hotspot":
        rect(px, SIGN[0], SIGN[1], SIGN[2], SIGN[3], 1)
    elif kind == "walkarea":
        rect(px, 8, FLOOR_TOP + 6, W - 9, H - 4, 1)
    elif kind == "walkbehind":
        rect(px, PILLAR[0] - 4, PILLAR[1], PILLAR[2] + 4, PILLAR[3], 1)
    return im


# -------------------------------------------------------------- sprites ----
def draw_placeholder():
    im = new_p(8, 8, 0)
    px = im.load()
    for i in range(8):
        px[i, i] = 12
        px[7 - i, i] = 12
    return im


def draw_cursor():
    im = new_p(12, 16, 0)
    px = im.load()
    for y in range(12):
        for x in range(0, y // 2 + 1 if y < 9 else 12 - y):
            px[x, y] = 15
        px[0, y] = 8
    for y in range(12):
        px[min(y // 2 + 1, 11) if y < 9 else max(12 - y, 0), y] = 8
    return im


def draw_key(w, h):
    im = new_p(w, h, 0)
    px = im.load()
    cy = h // 2
    rect(px, 1, cy - 3, 6, cy + 3, 14)
    rect(px, 3, cy - 1, 4, cy + 1, 0)
    rect(px, 6, cy - 1, w - 2, cy, 14)
    rect(px, w - 4, cy, w - 4, cy + 3, 14)
    rect(px, w - 2, cy, w - 2, cy + 2, 14)
    return im


def draw_ego(direction, pose):
    """16x32 figure. direction: down/left/right/up; pose 0 stand, 1/2 step."""
    im = new_p(16, 32, 0)
    px = im.load()
    shirt, trousers, hair, shoe = cube(1, 3, 5), cube(1, 1, 3), WOOD_D, 8
    rect(px, 5, 1, 10, 3, hair)                     # hair
    rect(px, 5, 4, 10, 9, SKIN)                     # head
    if direction == "up":
        rect(px, 5, 1, 10, 7, hair)
    elif direction == "down":
        px[6, 6] = 0 + 8
        px[9, 6] = 0 + 8
        rect(px, 7, 8, 8, 8, SKIN_D)
    else:
        rect(px, 5, 1, 7, 6, hair)
        px[9, 6] = 8
        px[10, 7] = SKIN_D
    rect(px, 4, 10, 11, 19, shirt)                  # torso
    swing = {0: 0, 1: 2, 2: -2}[pose]
    if direction in ("down", "up"):
        rect(px, 2, 11, 3, 17 + swing // 2, shirt)  # arms
        rect(px, 12, 11, 13, 17 - swing // 2, shirt)
        rect(px, 4, 20, 7, 28 + (1 if pose == 1 else 0), trousers)
        rect(px, 8, 20, 11, 28 + (1 if pose == 2 else 0), trousers)
        rect(px, 4, 29 + (1 if pose == 1 else 0), 7, 30 + (1 if pose == 1 else 0), shoe)
        rect(px, 8, 29 + (1 if pose == 2 else 0), 11, 30 + (1 if pose == 2 else 0), shoe)
    else:
        rect(px, 7, 11, 8, 18, cube(1, 2, 4))       # near arm
        rect(px, 5 - swing, 20, 8 - swing, 28, trousers)
        rect(px, 7 + swing, 20, 10 + swing, 28, cube(1, 1, 2))
        rect(px, 4 - swing, 29, 9 - swing, 30, shoe)
        rect(px, 7 + swing, 29, 12 + swing, 30, shoe)
    if direction == "left":
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im


def draw_spinner(frame):
    """24x24 four-frame rotating pinwheel -- the `anim` scene's object."""
    im = new_p(24, 24, 0)
    px = im.load()
    cx = cy = 11.5
    for y in range(24):
        for x in range(24):
            dx, dy = x - cx, y - cy
            d = math.hypot(dx, dy)
            if d > 11.4:
                continue
            a = (math.atan2(dy, dx) + frame * math.pi / 8) % (math.pi / 2)
            px[x, y] = 12 if a < math.pi / 4 else 14
            if d < 2.5:
                px[x, y] = 15
    return im


def draw_glitch_alpha():
    """32-bit sprite with a REAL alpha channel (soft round blob)."""
    im = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    px = im.load()
    for y in range(24):
        for x in range(24):
            d = math.hypot(x - 11.5, y - 11.5)
            a = max(0, min(255, int((11.5 - d) * 40)))
            px[x, y] = (30, 120, 220, a)
    return im


def draw_glitch_magenta():
    """32-bit sprite with NO alpha channel, keyed with the mask colour
    (magenta, alpha byte 0 -- see to_rgba). Checkerboard edges, so a
    wrong key shows up as a fringe rather than hiding in a solid shape."""
    im = Image.new("RGBA", (24, 24), MASK_RGBA)
    px = im.load()
    for y in range(4, 20):
        for x in range(4, 20):
            if (x + y) % 2 == 0 or 8 <= x < 16:
                px[x, y] = (220, 60, 40, 255)
    return im


# Sprite slot map -- gen_agf.py and the scripts use the same numbers.
SLOT_PLACEHOLDER, SLOT_CURSOR, SLOT_KEY_INV, SLOT_KEY_OBJ = 0, 1, 2, 3
SLOT_EGO = 10          # +0..2 down, +3..5 left, +6..8 right, +9..11 up
SLOT_SPINNER = 30      # +0..3
SLOT_GLITCH_ALPHA, SLOT_GLITCH_MAGENTA = 40, 41


def sprite_set(depth):
    s = {SLOT_PLACEHOLDER: draw_placeholder(), SLOT_CURSOR: draw_cursor(),
         SLOT_KEY_INV: draw_key(16, 16), SLOT_KEY_OBJ: draw_key(14, 10)}
    for di, d in enumerate(("down", "left", "right", "up")):
        for pose in range(3):
            s[SLOT_EGO + di * 3 + pose] = draw_ego(d, pose)
    for f in range(4):
        s[SLOT_SPINNER + f] = draw_spinner(f)
    if depth != 8:
        s = {k: to_rgba(v) for k, v in s.items()}
        s[SLOT_GLITCH_ALPHA] = draw_glitch_alpha()
        s[SLOT_GLITCH_MAGENTA] = draw_glitch_magenta()
    return s


# ---------------------------------------------------------------- audio ----
RATE = 11025   # the DOS mixer's own Tier-2 rate: nothing to resample at load


def tone(freq, dur, amp=0.5, fade=0.01):
    n, fn = int(RATE * dur), max(1, int(RATE * fade))
    out = []
    for i in range(n):
        env = min(1.0, i / fn, (n - i) / fn)
        out.append(int(amp * env * math.sin(2 * math.pi * freq * i / RATE) * 32767))
    return out


def write_wav(path):
    data = tone(523.25, 0.10) + tone(783.99, 0.14)     # C5 then G5
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(struct.pack("<%dh" % len(data), *data))


def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def write_midi(path):
    """The harness's known C D E F G F E C phrase (the Sound gate's
    pitch-track check knows it), four times, SMF format 0."""
    tpq = 96
    ev = bytearray(vlq(0) + bytes([0xC0, 80]))
    for _ in range(4):
        for note in (60, 62, 64, 65, 67, 65, 64, 60):
            ev += vlq(0) + bytes([0x90, note, 100])
            ev += vlq(tpq // 2) + bytes([0x80, note, 0])
    ev += vlq(0) + bytes([0xFF, 0x2F, 0x00])
    with open(path, "wb") as f:
        f.write(b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpq))
        f.write(b"MTrk" + struct.pack(">I", len(ev)) + bytes(ev))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    depth = 8
    if "--depth" in sys.argv:
        depth = int(sys.argv[sys.argv.index("--depth") + 1])
        args = [a for a in args if a != str(depth)]
    out = args[0]
    for d in ("sprites", "room1", "audio"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    for slot, im in sorted(sprite_set(depth).items()):
        im.save(os.path.join(out, "sprites", "spr%06d.png" % slot))
    bg = draw_background()
    (bg if depth == 8 else bg.convert("RGB")).save(os.path.join(out, "room1", "bg.png"))
    for kind in ("hotspot", "walkarea", "walkbehind", "region"):
        draw_mask(kind).save(os.path.join(out, "room1", "mask-%s.png" % kind))
    write_midi(os.path.join(out, "audio", "tune.mid"))
    write_wav(os.path.join(out, "audio", "chime.wav"))
    with open(os.path.join(out, "palette.json"), "w") as f:
        json.dump(PAL, f)
    print("generate_assets.py: depth %d -> %s" % (depth, out))


if __name__ == "__main__":
    main()
