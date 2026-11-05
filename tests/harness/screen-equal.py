#!/usr/bin/env python3
"""screen-equal.py A_DIR B_DIR [--min N]

Compares tick-synchronised emulated-screen captures (run-dosbox.sh --freeze-capture, ags patch 0195) of two runs:
frames/FRZnn.png of A against B, pixel for pixel, whole capture. A is the run under test (default present); B is the
FULL-PUSH REFERENCE (DOSAGS_DIRTY_PRESENT=0), which puts the engine's whole frame on the screen every present.
A pair passes only if (1) both runs froze at the SAME actual tick (the marker files say so; otherwise the pair is void,
not equal) and (2) the two PNGs are identical. Exit 0 iff every pair passes and at least --min pairs exist.

This answers the question the ags 0192 verifier cannot: not "do the pushed rects cover what the engine drew" but "is the
picture on the screen the one a full push would have shown". With the alias on the engine's frame IS the window surface,
so a frame never drawn into it reads equal to the verifier's shadow while the screen is incomplete.
"""
import argparse, os, re, sys
from PIL import Image, ImageChops


def markers(d):
    out = {}
    for f in sorted(os.listdir(os.path.join(d, "frames"))):
        m = re.match(r"(FRZ\d+)\.png$", f)
        if m:
            t = os.path.join(d, "frames", m.group(1) + ".txt")
            tick = None
            if os.path.exists(t):
                mm = re.search(r"tick=(\d+)", open(t).read())
                tick = int(mm.group(1)) if mm else None
            out[m.group(1)] = (os.path.join(d, "frames", f), tick)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--min", type=int, default=1)
    a = ap.parse_args()
    A, B = markers(a.a), markers(a.b)
    keys = sorted(set(A) | set(B))
    bad = 0; pairs = 0
    for k in keys:
        if k not in A or k not in B:
            print("%s  MISSING in %s" % (k, "A" if k not in A else "B")); bad += 1; continue
        (pa, ta), (pb, tb) = A[k], B[k]
        if ta is None or tb is None or ta != tb:
            print("%s  VOID: froze at different ticks (A=%s B=%s), not comparable" % (k, ta, tb)); bad += 1; continue
        ia, ib = Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")
        if ia.size != ib.size:
            print("%s  tick %d  DIFFERENT SIZE %s vs %s" % (k, ta, ia.size, ib.size)); bad += 1; continue
        pairs += 1
        diff = ImageChops.difference(ia, ib)
        bb = diff.getbbox()
        if bb is None:
            print("%s  tick %-5d  equal" % (k, ta))
        else:
            n = sum(1 for p in diff.getdata() if p != (0, 0, 0))
            print("%s  tick %-5d  DIFFERS: %d px, bbox %s" % (k, ta, n, bb)); bad += 1
    if pairs < a.min:
        print("only %d comparable pair(s), need >= %d" % (pairs, a.min)); bad += 1
    print("screen-equal: %d pair(s) compared, %d problem(s)" % (pairs, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
