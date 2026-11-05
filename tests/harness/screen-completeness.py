#!/usr/bin/env python3
"""screen-completeness.py SERIES_DIR...   (each holds frames/*.png from run-dosbox.sh --screen-series)

Prints, per series, the median brightness of the emulator-window crop over the middle third of its game-phase frames
(frames brighter than 0.8). A complete Mode 13h anim12 room reads about 30; the room with its background never pushed
(lit patches around the spinners, player, key and cursor only) reads about 8. A screen-level look, cheap and numeric; it is a
bisect aid, not the gate (that is gate-alias.sh / screen-equal.py, which compares against a full-push reference).
"""
import glob, os, statistics, sys
from PIL import Image
CROP = (300, 290, 1060, 760)
for d in sys.argv[1:]:
    fs = sorted(glob.glob(os.path.join(d, "frames", "*.png")))
    vals = [statistics.mean(Image.open(f).convert("L").crop(CROP).resize((76, 47)).getdata()) for f in fs]
    g = [v for v in vals if v > 0.8]
    mid = g[len(g) // 3: 2 * len(g) // 3]
    print("%-28s frames=%-4d game-phase median brightness=%s" % (os.path.basename(d.rstrip("/")), len(fs), round(statistics.median(mid), 1) if mid else None))
