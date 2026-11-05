#!/usr/bin/env python3
"""witness_sheet.py -- turn a directory of screen frames into ONE reviewable contact sheet
plus a manifest, for the physical-screen witness (run-hw.sh) and the emulated-screen
series (run-dosbox.sh).

Why this exists: every check the harness had reads the engine's own RAM frame, so a
present-side defect (regions changed in RAM and never pushed to the screen: "trails")
passes every hash. A frame taken OF THE SCREEN during the timed run, looked at by someone,
is the only thing that sees it. The operator found the first one with a camera. This makes
looking at the screen part of every cell instead of a thing he has to report.

Frame files are named  <seq>_<HHMMSS.mmm>[_t<tick>].<ext>  (monotonic in wall clock; the
tick is present only where the engine tick is known) and sorted by name. Nothing here
judges a frame: the sheet is for a person, and the manifest records what was captured so a
short capture is visible instead of silently fine.

  witness_sheet.py FRAMES_DIR [--out SHEET.png] [--manifest MANIFEST.json]
                   [--cols 6] [--tile 320x240] [--max-tiles 48]
                   [--crop auto|X0,Y0,X1,Y1|none] [--expect-min N]
"""
import argparse
import hashlib
import json
import os
import re
import sys

from PIL import Image, ImageDraw

EXTS = (".png", ".jpg", ".jpeg", ".bmp")
NAME_RE = re.compile(r"^(?P<seq>\d+)_(?P<ts>\d{6}(?:\.\d+)?)(?:_t(?P<tick>\d+))?\.")
FROZEN_RUN = 10   # consecutive non-locked card-state samples that make a capture STALE (see card{} below)


def frame_files(d):
    return sorted(f for f in os.listdir(d) if f.lower().endswith(EXTS))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def auto_crop_box(paths):
    """Union bounding box of the non-black content over a few of the frames: the emulator
    window on a big Xvfb root is mostly black margin."""
    box = None
    step = max(1, len(paths) // 12)
    for p in paths[::step]:
        try:
            bb = Image.open(p).convert("L").point(lambda v: 255 if v > 24 else 0).getbbox()
        except Exception:
            continue
        if bb is None:
            continue
        box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]),
                                      max(box[2], bb[2]), max(box[3], bb[3]))
    return box


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("frames_dir")
    ap.add_argument("--out", default=None)
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--tile", default="320x240")
    ap.add_argument("--max-tiles", type=int, default=48)
    ap.add_argument("--crop", default="none")
    ap.add_argument("--card-log", default=None,
                    help="witness/card-state.log: summarised into the manifest so a frozen capture card is a RECORDED fact")
    ap.add_argument("--expect-min", type=int, default=0,
                    help="fewer frames than this is recorded as short in the manifest (and exit 2)")
    a = ap.parse_args()

    d = a.frames_dir
    names = frame_files(d)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(d)), "sheet.png")
    man = a.manifest or os.path.splitext(out)[0] + ".MANIFEST.json"
    tw, th = (int(x) for x in a.tile.lower().split("x"))

    entries = []
    for n in names:
        m = NAME_RE.match(n)
        entries.append({
            "file": n,
            "sha256": sha256(os.path.join(d, n)),
            "time": m.group("ts") if m else None,
            "tick": int(m.group("tick")) if (m and m.group("tick")) else None,
        })

    short = len(names) < a.expect_min
    card = None
    if True:   # computed with or without a state log: the frames themselves say whether the card froze
        states = {}
        run = longest = 0   # the longest stretch of consecutive non-"locked" samples (~2 s apart)
        for ln in (open(a.card_log, errors="replace") if (a.card_log and os.path.exists(a.card_log)) else []):
            m = re.search(r"state=(\S+)", ln)
            if m:
                states[m.group(1)] = states.get(m.group(1), 0) + 1
                run = run + 1 if m.group(1) != "locked" else 0
                longest = max(longest, run)
        uniq = len(set(e["sha256"] for e in entries))
        total = sum(states.values())
        nos = sum(v for k, v in states.items() if k != "locked")
        # round W (2026-09-28): a 512x384 cell read "frozen" for its whole play window, yet locked boot and post-exit
        # samples outnumbered those, so the majority rule said live. A stretch of >= 10 non-locked samples (~20 s) now
        # counts too: healthy cells never showed more than 4 in a row, lock-loss cells 15 or more (survey of every
        # card-state.log to date).
        why = []
        if len(entries) >= 3 and uniq <= 1:
            why.append("one picture")
        if total >= 6 and nos * 2 >= total:
            why.append("most samples not locked")
        if longest >= FROZEN_RUN:
            why.append("%d non-locked samples in a row" % longest)
        absent = sum(v for k, v in states.items() if k in ("unavailable", "starting"))
        card = {"state_samples": states, "unique_frames": uniq, "frames": len(entries),
                "longest_nonlocked_run": longest,
                # frozen = the card kept handing back ONE picture while the cell ran, lost signal for most samples, or
                # lost it for a sustained stretch (the play window of a mode it cannot lock)
                "frozen": bool(why), "frozen_why": why,
                # absent = the capture device itself was missing (round T); nolock = present but no live picture
                "stale_kind": (None if not why else ("absent" if absent * 2 >= max(1, nos) else "nolock"))}
    manifest = {
        "frames_dir": os.path.basename(os.path.abspath(d)),
        "frame_count": len(names),
        "first_time": entries[0]["time"] if entries else None,
        "last_time": entries[-1]["time"] if entries else None,
        "expected_min": a.expect_min,
        "short": short,
        "card": card,
        "witness_reviewed": False,   # flipped by witness_review.py; port_game/parse-results refuse a figure until then
        "frames": entries,
    }

    if names:
        paths = [os.path.join(d, n) for n in names]
        crop = None
        if a.crop == "auto":
            crop = auto_crop_box(paths)
        elif a.crop != "none":
            crop = tuple(int(v) for v in a.crop.split(","))
        step = max(1, -(-len(names) // a.max_tiles))
        pick = list(range(0, len(names), step))
        cols = max(1, a.cols)
        rows = -(-len(pick) // cols)
        sheet = Image.new("RGB", (cols * tw, rows * th), (24, 24, 24))
        dr = ImageDraw.Draw(sheet)
        for k, i in enumerate(pick):
            try:
                im = Image.open(paths[i]).convert("RGB")
                if crop:
                    im = im.crop(crop)
                im = im.resize((tw, th))
            except Exception:
                im = Image.new("RGB", (tw, th), (90, 0, 0))
            x, y = (k % cols) * tw, (k // cols) * th
            sheet.paste(im, (x, y))
            e = entries[i]
            label = "#%d %s%s" % (i + 1, e["time"] or "", (" t%d" % e["tick"]) if e["tick"] is not None else "")
            dr.rectangle([x, y, x + 8 * len(label) + 4, y + 12], fill=(0, 0, 0))
            dr.text((x + 2, y + 1), label, fill=(255, 255, 0))
        sheet.save(out)
        manifest["sheet"] = os.path.basename(out)
        manifest["sheet_tiles"] = len(pick)
        manifest["sheet_every_nth_frame"] = step
        manifest["crop"] = list(crop) if crop else None

    with open(man, "w") as f:
        json.dump(manifest, f, indent=1)
    print("witness_sheet: %d frame(s), first %s last %s%s -> %s, %s" % (
        len(names), manifest["first_time"], manifest["last_time"],
        "  ** SHORT (expected >= %d) **" % a.expect_min if short else "", out if names else "(no sheet)", man))
    return 2 if short else 0


if __name__ == "__main__":
    sys.exit(main())
