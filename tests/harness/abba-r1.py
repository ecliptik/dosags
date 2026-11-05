#!/usr/bin/env python3
"""abba-r1.py -- score PLAN-NEXT round R1's RELEASE ABBA (S8 fixture), mechanically.

  abba-r1.py --stamp-a SHA12 --stamp-b SHA12 A1 B1 B2 A2

A = instrumented flavour (build/ags), B = release flavour (build/ags-release,
DOSAGS_RELEASE=1), same commit. Each cell is first scored by gatebar.py's own
cell() (the 09-30 S8 bar, --room 35 --msgskip), so VOID and MET mean exactly
what they meant for GL8A/B. Rule (operator 2026-11-05, before any data):

- VOID: any cell VOID by gatebar, or BLASTER.TXT (RUN.BAT: ECHO %BLASTER%)
  stripped != "A220 I7 D3 P330 T3" (profiles/dosags.yaml profile_witness).
- NOT SEPARABLE: |A1 - A2| >= 0.30 on whole-run or steady tick_rate.
- EQUIVALENT: mean(B) >= mean(A) - 0.10 on BOTH tick figures; LOSS otherwise.
- Release S8 x2: both B cells MET by gatebar (subject to camera CLEAN). Operator
  2026-11-05: this counts as the release flavour's S8 x2 gate reading.
- Gate cells MOVE to the release flavour iff EQUIVALENT and release S8 MET x2.
  EQUIVALENT with release S8 not MET x2: reported, the operator decides.
Reported, not scored: per-cell room-35 load (DOSAGS_XT load_begin -> load_end,
which spans ags 0354's commit) and the deltas against GL8A/B (8249193ed041;
whole-run there does not include 0354's commit, see PLAN-NEXT step 4).
Tick figures are compared as recorded (2 dp Decimals), never rounded.
"""
import argparse
import contextlib
import importlib.util
import io
import re
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gatebar", HERE / "gatebar.py")
gatebar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gatebar)

BLASTER = "A220 I7 D3 P330 T3"
TOL, DRIFT = Decimal("0.10"), Decimal("0.30")
GL8 = {"GL8A": (Decimal("39.26"), Decimal("40.23")), "GL8B": (Decimal("39.35"), Decimal("40.29"))}


def figures(d):
    tag = d.name.split("-")[0]
    log = (d / (tag + ".LOG")).read_text(errors="ignore") if (d / (tag + ".LOG")).is_file() else ""
    out = (d / "STDOUT.TXT").read_text(errors="ignore") if (d / "STDOUT.TXT").is_file() else ""
    w = re.findall(r"^DOS-PORT tick_rate=([\d.]+)", log, re.M)
    s = re.findall(r"^DOS-PORT tick_rate_steady=([\d.]+)", log, re.M)
    lb = re.findall(r"DOSAGS_XT t_ms=(\d+) phase=load_begin room=35", out)
    le = re.findall(r"DOSAGS_XT t_ms=(\d+) phase=load_end room=35", out)
    load = "%s -> %s ms" % (lb[-1], le[-1]) if lb and le else "absent"
    return (Decimal(w[-1]) if w else None, Decimal(s[-1]) if s else None, load)


def blaster(d):
    p = d / "BLASTER.TXT"
    return p.read_text(errors="ignore").strip() if p.is_file() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp-a", required=True)
    ap.add_argument("--stamp-b", required=True)
    ap.add_argument("dirs", nargs=4, metavar="A1 B1 B2 A2")
    args = ap.parse_args()
    a1, b1, b2, a2 = [Path(x) for x in args.dirs]
    arms = [("A1", a1, args.stamp_a), ("B1", b1, args.stamp_b), ("B2", b2, args.stamp_b), ("A2", a2, args.stamp_a)]
    met, fig, void = {}, {}, []
    for name, d, stamp in arms:
        ns = argparse.Namespace(stamp=stamp, room=35, msgskip=True)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = gatebar.cell(d, ns)
        print("[%s] %s" % (name, buf.getvalue().rstrip().replace("\n", "\n     ")))
        bl = blaster(d)
        print("     BLASTER.TXT: %r" % bl)
        if r is None:
            void.append("%s VOID by gatebar" % name)
        if bl != BLASTER:
            void.append("%s BLASTER %r != %r" % (name, bl, BLASTER))
        met[name] = r
        fig[name] = figures(d)
        print("     room-35 load (reported): %s" % fig[name][2])
    if void:
        print("R1 ABBA: VOID -- " + "; ".join(void))
        return 2
    labels = ("whole-run", "steady")
    for i, lab in enumerate(labels):
        drift = abs(fig["A1"][i] - fig["A2"][i])
        print("drift %s |A1-A2| = %s" % (lab, drift))
        if drift >= DRIFT:
            print("R1 ABBA: NOT SEPARABLE (%s drift %s >= %s)" % (lab, drift, DRIFT))
            return 3
    equiv = True
    for i, lab in enumerate(labels):
        ma = (fig["A1"][i] + fig["A2"][i]) / 2
        mb = (fig["B1"][i] + fig["B2"][i]) / 2
        ok = mb >= ma - TOL
        equiv &= ok
        print("%s: mean A %s, mean B %s, B - A %+.3f -> %s" % (lab, ma, mb, mb - ma, "ok" if ok else "LOSS"))
        for g, gv in GL8.items():
            print("   (reported) mean B - %s = %+.3f" % (g, mb - gv[i]))
    rel_x2 = bool(met["B1"]) and bool(met["B2"])
    print("instrumented S8 this round: A1 %s, A2 %s (reported)" % (
        "MET" if met["A1"] else "NOT MET", "MET" if met["A2"] else "NOT MET"))
    print("release S8 x2: %s (subject to camera CLEAN in B1 and B2)" % ("MET" if rel_x2 else "NOT MET"))
    print("R1 ABBA: %s" % ("EQUIVALENT" if equiv else "LOSS"))
    if equiv and rel_x2:
        print("decision: gate cells MOVE to the release flavour (subject to camera CLEAN)")
    elif equiv:
        print("decision: EQUIVALENT but release S8 not MET x2 -- the operator decides")
    else:
        print("decision: gate cells STAY on the instrumented flavour; R2 does not run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
