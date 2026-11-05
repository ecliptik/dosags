#!/usr/bin/env python3
"""lab-metric-blite.py -- score the PRE-REGISTERED B-lite model (LAB-METRIC.md section 10).

Written and committed before any B-lite run. Fixed-cycles DOSBox-X (fixed 40000, core=normal) times
the CPU work the 486 does; the work-vector counters price the bulk copies the emulator charges
~nothing for (rep movs). Two per-kind factors, both calibrated on ONE cell named in advance (S2M1);
F2B1, S2F2, AQF1, SB5O are held out.

Per cell, all per render (R) or per steady tick (T):
  R phases  = render_backbuffer + scene_construct + present_update_window + present_blit
              + present_dirty_check  (tickstats totals / render_passes, same set on both sides)
  B         = invisible bus/copy ms per render from the lab work vector (steady scope):
              push_bytes x bus(lfb|mode13) + blit1x x copy + 0.5 x blitsc x copy + cache x copy
              + bg_px x bpp x copy + fill_px x bpp x write
  E_R       = lab R phases per lab render;   E_O = (lab busy - lab R phase totals) / lab steady ticks
  hw_R      = hw R phases per hw render;     hw_O = (hw busy - hw R phase totals) / hw steady ticks
  busy      = loop_ms - stall_ms - wait_next_frame (both sides; nested ticks counted once, so
              blocking-call time is never double counted and the script_vm phase is not used)
Calibration (S2M1 only):  k_R = (hw_R - B) / E_R ;  k_O = hw_O / E_O
Prediction:  busy/render = k_R x E_R + B + k_O x E_O x (hw steady ticks / hw renders)
PASS iff the five predicted busy/render rank exactly as measured AND all four held-out ratios lie
in [0.67, 1.5].

    lab-metric-blite.py [--json OUT]
"""
import json
import re
import sys
from pathlib import Path

HW = Path.home() / "git/dosags/tests/harness/results"
LAB = Path(__file__).resolve().parent / "results/BLITE-2026-09-24"
CELLS = {  # cell -> (hardware dir, lab dir, push target)
    "F2B1": ("F2B1-2026-09-21", "F2B1", "mode13"),
    "S2F2": ("S2F2-2026-09-22", "S2F2", "lfb"),
    "AQF1": ("AQF1-2026-09-21", "AQF1", "lfb"),
    "S2M1": ("S2M1-2026-09-22", "S2M1", "lfb"),
    "SB5O": ("SB5O-2026-09-23", "SB5O", "lfb"),
}
CALIB = "S2M1"
MEASURED_ORDER = ["S2F2", "AQF1", "F2B1", "S2M1", "SB5O"]
R_PHASES = ("render_backbuffer", "scene_construct", "present_update_window", "present_blit",
            "present_dirty_check")
MB = 1e6
US_PER_B = {"lfb": 1e6 / (27.3 * MB), "mode13": 1e6 / (9.3 * MB), "copy": 1e6 / (17.0 * MB),
            "write": 1e6 / (40.9 * MB)}
LAB_MMD_REF = {"k_R": 1.00, "k_O": 2.21}   # dosags-lab-mmd 5.1 (rb per call, script per tick, fixed 40000)


def figures(runmani):
    t = Path(runmani).read_text(errors="replace")
    m = re.search(r"tick_rate_steady=[\d.]+ ticks=(\d+) stall_ticks=(\d+) loop_ms=(\d+) stall_ms=(\d+)", t)
    ph = {k: int(us) / 1000.0 for k, us in re.findall(r"tickstats_(\w+) calls=\d+ total_ms=\d+ .*? total_us=(\d+)", t)}
    renders = int(re.search(r"render_passes=(\d+)", t).group(1))
    busy = int(m[3]) - int(m[4]) - ph["wait_next_frame"]
    rsum = sum(ph.get(p, 0.0) for p in R_PHASES)
    steady = int(m[1]) - int(m[2])
    out = {"renders": renders, "steady_ticks": steady, "busy_ms": busy, "R_total_ms": rsum,
           "R_per_render": rsum / renders, "O_per_tick": (busy - rsum) / steady,
           "busy_per_render": busy / renders}
    wl = [l for l in t.splitlines() if l.startswith("DOS-PORT work scope=steady ")]
    if wl:
        out["work"] = {k: (v if k == "win" else int(v)) for k, v in re.findall(r"(\w+)=(\S+)", wl[0]) if k != "scope"}
    return out


def bus_ms_per_render(w, tgt):
    r = max(w["renders"], 1)
    bpp = w["vs_bpp"]
    us = (w["push_bytes"] * US_PER_B[tgt] + w["blit1x_bytes"] * US_PER_B["copy"]
          + 0.5 * w["blitsc_bytes"] * US_PER_B["copy"] + w["cache_bytes"] * US_PER_B["copy"]
          + w["bg_px"] * bpp * US_PER_B["copy"] + w["fill_px"] * bpp * US_PER_B["write"])
    return us / 1000.0 / r


def main():
    d = {}
    for c, (hwd, labd, tgt) in CELLS.items():
        f = LAB / labd / "RUNMANI.LOG"
        if not f.exists():
            print(f"{c}: lab run missing ({f})")
            continue
        hw, lab = figures(HW / hwd / "RUNMANI.LOG"), figures(f)
        d[c] = {"hw": hw, "lab": lab, "B": bus_ms_per_render(lab["work"], tgt),
                "mix": hw["steady_ticks"] / hw["renders"]}
    if CALIB not in d:
        sys.exit("calibration cell missing")
    cal = d[CALIB]
    k_R = (cal["hw"]["R_per_render"] - cal["B"]) / cal["lab"]["R_per_render"]
    k_O = cal["hw"]["O_per_tick"] / cal["lab"]["O_per_tick"]
    print(f"calibration on {CALIB}: k_R={k_R:.3f} (lab-mmd ref {LAB_MMD_REF['k_R']})  "
          f"k_O={k_O:.3f} (lab-mmd ref {LAB_MMD_REF['k_O']})")
    out = {"k_R": k_R, "k_O": k_O, "calib": CALIB, "lab_mmd_ref": LAB_MMD_REF, "cells": {}}
    rows = []
    for c, x in d.items():
        predR = k_R * x["lab"]["R_per_render"] + x["B"]
        predO = k_O * x["lab"]["O_per_tick"]
        pred = predR + predO * x["mix"]
        meas = x["hw"]["busy_per_render"]
        rows.append((c, meas, pred))
        out["cells"][c] = {"measured": meas, "pred": pred, "ratio": pred / meas, "B": x["B"],
                           "E_R": x["lab"]["R_per_render"], "E_O": x["lab"]["O_per_tick"], "mix": x["mix"],
                           "pred_R_per_render": predR, "hw_R_per_render": x["hw"]["R_per_render"],
                           "pred_O_per_tick": predO, "hw_O_per_tick": x["hw"]["O_per_tick"],
                           "held_out": c != CALIB}
        print(f"{c:5} measured {meas:8.2f}  predicted {pred:8.2f}  ratio {pred / meas:5.2f}  |  "
              f"R {predR:7.2f} vs hw {x['hw']['R_per_render']:7.2f}   O/tick {predO:6.2f} vs hw {x['hw']['O_per_tick']:6.2f}"
              f"   (B {x['B']:.2f}, E_R {x['lab']['R_per_render']:.2f}, E_O {x['lab']['O_per_tick']:.2f})"
              + ("" if c != CALIB else "   [calibration]"))
    if len(rows) == len(CELLS):
        order = [c for c, *_ in sorted(rows, key=lambda r: r[2])]
        rank_ok = order == MEASURED_ORDER
        scale_ok = all(0.67 <= p / m <= 1.5 for c, m, p in rows if c != CALIB)
        out.update({"predicted_order": order, "rank_ok": rank_ok, "scale_ok": scale_ok,
                    "pass": rank_ok and scale_ok})
        print("predicted order:", " < ".join(order), "| measured:", " < ".join(MEASURED_ORDER))
        print(f"rank {rank_ok}; held-out within [0.67,1.5] {scale_ok}; VERDICT {'PASS' if rank_ok and scale_ok else 'FAIL'}")
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
