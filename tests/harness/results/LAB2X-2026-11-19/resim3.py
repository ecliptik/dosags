#!/usr/bin/env python3
"""resim3.py GATE2 COPY [--negative] -- FIX-UP 3 re-sim of gate-2x-read.py on a COPY of gate run 2's cells (never on gate2).
Positive set: C2 and V2 relabelled to the FIX-UP 3 control (the scale2 line says break=3 instead of break=2). The one row
where gate2's break=2 had no power, B16-2x-walk, gets the outcome FIX-UP 3 predicts for break=3: one C2 freeze frame gets a
6x6 patch (so C2 differs from B), and V2 reads vfy_bad=197 (the diag count of presents whose boxes hold a changed px).
Every other row keeps gate2's frames and counters, which already had power at break=2.
Negative set (--negative): the same, then four defects the FIX-UP 3 reader must catch:
  1. B16-2x-walk/V2 vfy_bad back to 0 -> "V2 verifier power" NOPOWER;
  2. B16-2x-walk/C2 frames restored to gate2's (equal to B) -> "C2 differs" NOPOWER, now registered on a bench row;
  3. S16-2x/C2 scale2 line left at break=2 -> witness C2 VOID (break must be 3);
  4. S8-2x/C2i scale2 line set to break=3 -> witness C2i VOID (break must be 1).
Expected: positive exit 0; negative exit 1 (a VOID outranks NOPOWER), with all four lines present."""
import os, re, shutil, sys
from PIL import Image
G, C = sys.argv[1], sys.argv[2]
neg = "--negative" in sys.argv
shutil.rmtree(C, ignore_errors=True)
shutil.copytree(G, C, ignore=shutil.ignore_patterns("*-vs-*.txt", "VERDICT.txt", "GATE-READ.txt", "_cfg"))
for _r, _ds, _fs in os.walk(C):   # the copy must be writable
    for _n in _ds + _fs:
        os.chmod(os.path.join(_r, _n), 0o755 if _n in _ds else 0o644)
def sub_log(p, f):
    s = open(p).read(); open(p, "w").write(f(s))
def brk(n):
    return lambda s: re.sub(r"(DOS-PORT scale2 on=1 )break=\d", r"\g<1>break=%d" % n, s)
for row in sorted(os.listdir(C)):
    rd = os.path.join(C, row)
    if not os.path.isfile(os.path.join(rd, "ROW.txt")):
        continue
    for arm in ("C2", "V2"):
        p = os.path.join(rd, arm, "RUNMANI.LOG")
        if os.path.isfile(p):
            sub_log(p, brk(3))
w = os.path.join(C, "B16-2x-walk")
fr = sorted(f for f in os.listdir(os.path.join(w, "C2", "frames")) if f.endswith(".png"))
p = os.path.join(w, "C2", "frames", fr[len(fr) // 2])
im = Image.open(p).convert("RGB")
for x in range(300, 306):
    for y in range(200, 206):
        im.putpixel((x, y), (255, 0, 255))
im.save(p)
sub_log(os.path.join(w, "V2", "RUNMANI.LOG"),
        lambda s: s.replace("vfy_bad=0 vfy_bad_px=0 vfy_first=-1", "vfy_bad=197 vfy_bad_px=44678 vfy_first=5"))
if neg:
    sub_log(os.path.join(w, "V2", "RUNMANI.LOG"), lambda s: re.sub(r"vfy_bad=\d+ ", "vfy_bad=0 ", s))
    shutil.rmtree(os.path.join(w, "C2", "frames"))
    shutil.copytree(os.path.join(G, "B16-2x-walk", "C2", "frames"), os.path.join(w, "C2", "frames"))
    sub_log(os.path.join(C, "S16-2x", "C2", "RUNMANI.LOG"), brk(2))
    sub_log(os.path.join(C, "S8-2x", "C2i", "RUNMANI.LOG"), brk(3))
print("resim copy ready:", C, "negative" if neg else "positive")
