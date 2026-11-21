#!/usr/bin/env python3
"""resim2.py GATE COPY [--negative] -- FIX-UP 2 re-sim of gate-2x-read.py on a COPY of gate run 1's cells.
Positive set: C2i = gate1's C2 as it ran (break=1); C2 = synthetic break=2 (the scale2 line says break=2 and one freeze
frame gets a 6x6 patch, so it differs from B); V2 = synthetic break=2 with vfy_bad>0. frames_skipped left as it ran.
Negative set (--negative): on top of that, three defects the new rules must catch -- S16-2x/F frames_skipped -1 (row
reads 0: mismatch -> VOID), S8-2x/A frames_skipped 0 (row reads -1: mismatch -> VOID), CLK-2x/C2 frames restored to
gate1's (no difference -> NOPOWER), B8-2x-walk/V2 vfy_bad=0 (-> NOPOWER)."""
import os, re, shutil, sys
from PIL import Image
G, C = sys.argv[1], sys.argv[2]
neg = "--negative" in sys.argv
shutil.rmtree(C, ignore_errors=True)
shutil.copytree(G, C, ignore=shutil.ignore_patterns("*-vs-*.txt", "VERDICT.txt"))
for _r, _ds, _fs in os.walk(C):   # the source is kept read-only; the copy must be writable
    for _n in _ds + _fs:
        os.chmod(os.path.join(_r, _n), 0o755 if _n in _ds else 0o644)
def sub_log(p, f):
    s = open(p).read(); open(p, "w").write(f(s))
for row in sorted(os.listdir(C)):
    rd = os.path.join(C, row)
    rt = os.path.join(rd, "ROW.txt")
    if not os.path.isfile(rt) or not os.path.isdir(os.path.join(rd, "C2")):
        continue
    if "R" in os.listdir(rd):   # game rows: add C2i (gate1's C2, break=1)
        shutil.copytree(os.path.join(rd, "C2"), os.path.join(rd, "C2i"))
        sub_log(rt, lambda s: s.replace(" C2 V V2 R", " C2 C2i V V2 R"))
    sub_log(os.path.join(rd, "C2", "RUNMANI.LOG"), lambda s: s.replace("break=1", "break=2"))
    fr = sorted(f for f in os.listdir(os.path.join(rd, "C2", "frames")) if f.endswith(".png"))
    p = os.path.join(rd, "C2", "frames", fr[len(fr) // 2])
    im = Image.open(p).convert("RGB")
    for x in range(600, 606):
        for y in range(500, 506):
            im.putpixel((x, y), (255, 0, 255))
    im.save(p)
    sub_log(os.path.join(rd, "V2", "RUNMANI.LOG"),
            lambda s: re.sub(r"vfy_bad=0 vfy_bad_px=0 vfy_first=-1", "vfy_bad=37 vfy_bad_px=2911 vfy_first=5",
                             s.replace("break=1", "break=2")))
if neg:
    sub_log(os.path.join(C, "S16-2x", "F", "RUNMANI.LOG"), lambda s: s.replace("frames_skipped=0", "frames_skipped=-1"))
    sub_log(os.path.join(C, "S8-2x", "A", "RUNMANI.LOG"), lambda s: s.replace("frames_skipped=-1", "frames_skipped=0"))
    shutil.rmtree(os.path.join(C, "CLK-2x", "C2", "frames"))
    shutil.copytree(os.path.join(G, "CLK-2x", "C2", "frames"), os.path.join(C, "CLK-2x", "C2", "frames"))
    sub_log(os.path.join(C, "B8-2x-walk", "V2", "RUNMANI.LOG"), lambda s: re.sub(r"vfy_bad=\d+ ", "vfy_bad=0 ", s))
print("resim copy ready:", C, "negative" if neg else "positive")
