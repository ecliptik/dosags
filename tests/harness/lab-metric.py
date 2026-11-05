#!/usr/bin/env python3
"""lab-metric.py -- score the pre-registered work-vector cost model (LAB-METRIC.md section 1).

For each cell: the hardware RUNMANI.LOG gives the MEASURED busy ms per render; the lab (DOSBox-X)
RUNMANI.LOG gives the WORK vector (ags patch 0230 `DOS-PORT work scope=steady` line). The model
prices the vector with PLAN.md's measured constants and predicts busy ms per render.

    lab-metric.py              # the five pre-registered cells, table + verdict
    lab-metric.py --json OUT   # also write every number to OUT

Nothing here is fitted except c_ins, calibrated on S2F2 exactly as pre-registered.
"""
import json
import re
import sys
from pathlib import Path

HW = Path.home() / "git/dosags/tests/harness/results"
LAB = Path(__file__).resolve().parent / "results/LABMETRIC-2026-09-23"

# cell -> (hardware dir, lab dir, push target)
CELLS = {
    "F2B1": ("F2B1-2026-09-21", "LF2B", "mode13"),
    "S2F2": ("S2F2-2026-09-22", "LS2F", "lfb"),
    "AQF1": ("AQF1-2026-09-21", "LAQF", "lfb"),
    "S2M1": ("S2M1-2026-09-22", "LS2M", "lfb"),
    "SB5O": ("SB5O-2026-09-23", "LSB5", "lfb"),
}
MEASURED_ORDER = ["S2F2", "AQF1", "F2B1", "S2M1", "SB5O"]
CALIB = "S2F2"

# ---- constants, us per byte / ms, all from PLAN.md "The numbers to plan against" ----
MB = 1e6
C = {
    "push_lfb":    1.0 / (27.3 * MB) * 1e6,          # us/B
    "push_mode13": 1.0 / (9.3 * MB) * 1e6,
    "copy":        1.0 / (17.0 * MB) * 1e6,
    "write":       1.0 / (40.9 * MB) * 1e6,
}
C["cmp"] = 2 * 1.4 * C["write"]                      # two reads per byte, a read 1.4x a write
C["scaled"] = 0.5 * C["write"] + 0.5 * C["copy"]     # DERIVED (not measured)
CLK = 66e6
C["msk_per_byte"] = (19.4 / 2) / CLK * 1e6           # 19.4 cycles/px at 2 B/px
C["opq_per_byte"] = (7.8 / 2) / CLK * 1e6            # 7.8 cycles/px at 2 B/px
SCENE_FIXED_MS = 3.0
SCENE_PER_SPRITE_MS = 0.335
ENGINE_FIXED_TICK_MS = 2.10


def rd(p):
    return Path(p).read_text(errors="replace")


def hw_measured(d):
    t = rd(HW / d / "RUNMANI.LOG")
    m = re.search(r"tick_rate_steady=([\d.]+) ticks=(\d+) stall_ticks=(\d+) loop_ms=(\d+) stall_ms=(\d+)", t)
    wait = int(re.search(r"tickstats_wait_next_frame calls=\d+ total_ms=(\d+)", t).group(1))
    renders = int(re.search(r"render_passes=(\d+)", t).group(1))
    ticks, st, loop, stall = int(m[2]), int(m[3]), int(m[4]), int(m[5])
    ph = {k: int(v) / 1000.0 for k, v in re.findall(r"tickstats_(\w+) calls=\d+ total_ms=\d+ .*? total_us=(\d+)", t)}
    busy = loop - stall - wait
    return {"ticks": ticks, "stall_ticks": st, "steady_ticks": ticks - st, "renders": renders,
            "loop_ms": loop, "stall_ms": stall, "wait_ms": wait, "busy_ms": busy,
            "busy_per_render": busy / renders, "phase_ms": ph,
            "lines": [l for l in t.splitlines() if "tick_rate_steady=" in l or "render_passes=" in l
                      or "tickstats_wait_next_frame " in l or "tickstats_script_vm " in l]}


def lab_vector(d, scope="steady"):
    t = rd(LAB / d / "RUNMANI.LOG")
    line = [l for l in t.splitlines() if l.startswith(f"DOS-PORT work scope={scope} ")][0]
    v = {}
    for k, val in re.findall(r"(\w+)=(\S+)", line):
        if k == "win":
            v[k] = val
        elif k != "scope":
            v[k] = int(val)
    return v, line


def predict(v, push_target, c_ins, mix):
    """per-render ms, per-tick ms, and the terms, from a steady work vector."""
    r = max(v["renders"], 1)
    t = max(v["ticks"], 1)
    bpp = v["vs_bpp"]
    us = lambda n, c: n * c / 1000.0 / r   # total units x us/unit -> ms per render
    terms = {
        "push":    us(v["push_bytes"], C["push_mode13" if push_target == "mode13" else "push_lfb"]),
        "blit1x":  us(v["blit1x_bytes"], C["copy"]),
        "blitsc":  us(v["blitsc_bytes"], C["scaled"]),
        "cmp":     us(v["cmp_bytes"], C["cmp"]),
        "cache":   us(v["cache_bytes"], C["copy"]),
        "spr_msk": us((v["spr_msk_px"] + v["spr_bld_px"]) * bpp, C["msk_per_byte"]),
        "spr_opq": us(v["spr_opq_px"] * bpp, C["opq_per_byte"]),
        "fill":    us(v["fill_px"] * bpp, C["write"]),
        "bg":      us(v["bg_px"] * bpp, C["copy"]),
        "scene":   SCENE_FIXED_MS + SCENE_PER_SPRITE_MS * v["spr_n"] / r,
    }
    per_render = sum(terms.values())
    per_tick = ENGINE_FIXED_TICK_MS + (c_ins * v["script_ins"] / t / 1000.0 if c_ins is not None else 0.0)
    busy_per_render = per_render + per_tick * mix
    # closed form, no hardware input: 40 ticks/s of logic, the rest renders
    avail = 1000.0 - 40.0 * per_tick
    rate = min(40.0, avail / per_render) if avail > 0 else 0.0
    return {"terms_ms_per_render": terms, "per_render_ms": per_render, "per_tick_ms": per_tick,
            "busy_per_render": busy_per_render, "closed_form_rate": rate}


def main():
    out = {"constants_us_per_unit": C, "cells": {}}
    have = {k: (LAB / v[1] / "RUNMANI.LOG").exists() for k, v in CELLS.items()}
    # calibration: c_ins = S2F2 hardware script_vm us / S2F2 lab script_ins, whole run (both scopes)
    hwc = hw_measured(CELLS[CALIB][0])
    vs, _ = lab_vector(CELLS[CALIB][1], "steady")
    vx, _ = lab_vector(CELLS[CALIB][1], "excluded")
    ins_all = vs["script_ins"] + vx["script_ins"]
    c_ins = hwc["phase_ms"]["script_vm"] * 1000.0 / ins_all
    out["c_ins_us"] = c_ins
    out["c_ins_basis"] = {"hw_script_vm_ms": hwc["phase_ms"]["script_vm"], "lab_script_ins": ins_all}
    print(f"c_ins = {c_ins:.3f} us/instruction  (S2F2 hw script_vm {hwc['phase_ms']['script_vm']:.0f} ms / lab {ins_all} instructions)")
    print()
    rows = []
    for cell, (hwd, labd, tgt) in CELLS.items():
        if not have[cell]:
            print(f"{cell}: lab run missing ({LAB / labd})")
            continue
        hw = hw_measured(hwd)
        v, line = lab_vector(labd)
        mix = hw["steady_ticks"] / hw["renders"]
        p = predict(v, tgt, c_ins, mix)
        ratio = p["busy_per_render"] / hw["busy_per_render"]
        # held-out check of the calibrated term: predicted script ms over the run vs hardware script_vm
        vx, _ = lab_vector(labd, "excluded")
        lab_ins_per_tick = (v["script_ins"] + vx["script_ins"]) / max(v["ticks"] + vx["ticks"], 1)
        pred_script_ms = c_ins * lab_ins_per_tick * hw["ticks"] / 1000.0
        rec = {"hw_dir": str(HW / hwd), "lab_dir": str(LAB / labd), "push_target": tgt,
               "measured": {k: hw[k] for k in hw if k not in ("phase_ms", "lines")},
               "hw_lines": hw["lines"], "lab_line": line, "mix_ticks_per_render": mix,
               "prediction": p, "ratio": ratio,
               "script_heldout": {"pred_ms": pred_script_ms, "hw_ms": hw["phase_ms"].get("script_vm")},
               "hw_phase_ms_per_render": {k: hw["phase_ms"].get(k, 0) / hw["renders"] for k in
                   ("present_update_window", "present_blit", "present_dirty_check", "render_backbuffer",
                    "scene_construct", "bg_restore", "script_vm", "process_events_dispatch")}}
        out["cells"][cell] = rec
        rows.append((cell, hw["busy_per_render"], p["busy_per_render"], ratio, p, mix, hw))
    print(f"{'cell':5} {'measured':>9} {'predicted':>9} {'ratio':>6}  per_render per_tick mix   closed-form rate")
    for cell, meas, pred, ratio, p, mix, hw in rows:
        print(f"{cell:5} {meas:9.2f} {pred:9.2f} {ratio:6.2f}  {p['per_render_ms']:9.2f} {p['per_tick_ms']:8.2f} {mix:4.2f}  {p['closed_form_rate']:.2f}")
    print()
    for cell, meas, pred, ratio, p, mix, hw in rows:
        t = p["terms_ms_per_render"]
        print(cell, " ".join(f"{k}={t[k]:.2f}" for k in t))
    if len(rows) == len(CELLS):
        pred_order = [c for c, *_ in sorted(rows, key=lambda r: r[2])]
        rank_ok = pred_order == MEASURED_ORDER
        scale_ok = all(0.67 <= r[3] <= 1.5 for r in rows)
        f2 = all(0.5 <= r[3] <= 2.0 for r in rows)
        out["verdict"] = {"predicted_order": pred_order, "measured_order": MEASURED_ORDER,
                          "rank_ok": rank_ok, "scale_1p5_ok": scale_ok, "factor2_ok": f2,
                          "pass": rank_ok and scale_ok}
        print()
        print("predicted order:", " < ".join(pred_order))
        print("measured  order:", " < ".join(MEASURED_ORDER))
        print(f"rank match: {rank_ok}; all within 1.5x: {scale_ok}; all within 2x (informational): {f2}")
        print("VERDICT:", "PASS" if rank_ok and scale_ok else "FAIL")
    # ---- per-phase: each bus/blit term against the hardware phase that contains it ----
    print()
    print("PER-PHASE (informational): predicted ms per call vs hardware tickstats mean per call")
    phase_rows = {}
    for cell, meas, pred, ratio, p, mix, hw in rows:
        v, _ = lab_vector(CELLS[cell][1])
        tgt = CELLS[cell][2]
        ph = hw["phase_ms"]
        t = rd(HW / CELLS[cell][0] / "RUNMANI.LOG")
        calls = {k: int(n) for k, n in re.findall(r"tickstats_(\w+) calls=(\d+)", t)}
        pres = max(v["presents"], 1); r = max(v["renders"], 1); tk = max(v["ticks"], 1)
        cpush = C["push_mode13" if tgt == "mode13" else "push_lfb"]
        rowp = {
            "present_update_window": (v["push_bytes"] / pres * cpush / 1000, ph.get("present_update_window", 0) / max(calls.get("present_update_window", 0), 1)),
            "present_blit": ((v["blit1x_bytes"] * C["copy"] + v["blitsc_bytes"] * C["scaled"]) / 1000 / pres,
                             ph.get("present_blit", 0) / max(calls.get("present_blit", 0), 1)),
            "present_dirty_check": ((v["cmp_bytes"] * C["cmp"] + v["cache_bytes"] * C["copy"]) / 1000 / r,
                                    ph.get("present_dirty_check", 0) / max(calls.get("present_dirty_check", 0), 1)),
            "render_backbuffer": (p["terms_ms_per_render"]["spr_msk"] + p["terms_ms_per_render"]["spr_opq"],
                                  ph.get("render_backbuffer", 0) / max(calls.get("render_backbuffer", 0), 1)),
            "scene_construct(+bg)": (p["terms_ms_per_render"]["scene"] + p["terms_ms_per_render"]["bg"],
                                     ph.get("scene_construct", 0) / max(calls.get("scene_construct", 0), 1)),
            "bg_restore": (p["terms_ms_per_render"]["bg"], ph.get("bg_restore", 0) / max(calls.get("bg_restore", 0), 1)),
        }
        phase_rows[cell] = rowp
        print(cell, "  ".join(f"{k}={a:.2f}/{b:.2f}" for k, (a, b) in rowp.items()))
    out["per_phase_pred_vs_hw_ms_per_call"] = phase_rows

    # ---- POST HOC (not the verdict): script cost per instruction ----
    print()
    print("POST HOC, labelled, not the pre-registered verdict: script ms per tick, hardware vs lab counts")
    ph_rows = {}
    for cell, meas, pred, ratio, p, mix, hw in rows:
        v, _ = lab_vector(CELLS[cell][1]); vx, _ = lab_vector(CELLS[cell][1], "excluded")
        t = rd(HW / CELLS[cell][0] / "RUNMANI.LOG")
        m = re.search(r"tickstats_script_vm calls=(\d+) total_ms=\d+ min_ms=\d+ max_ms=(\d+)", t)
        sc_ms = hw["phase_ms"]["script_vm"]; mx = int(m[2])
        ins_t = (v["script_ins"] + vx["script_ins"]) / (v["ticks"] + vx["ticks"])
        ext_t = (v["script_ext"] + vx["script_ext"]) / (v["ticks"] + vx["ticks"])
        per_tick = sc_ms / hw["ticks"]
        per_tick_nomax = (sc_ms - mx) / hw["ticks"]
        ph_rows[cell] = {"hw_script_ms_per_tick": per_tick, "hw_script_ms_per_tick_without_max_call": per_tick_nomax,
                         "max_call_ms": mx, "lab_ins_per_tick": ins_t, "lab_ext_per_tick": ext_t,
                         "us_per_ins_without_max": per_tick_nomax * 1000 / ins_t if ins_t else None}
        print(f"{cell}: hw script {per_tick:.2f} ms/tick ({per_tick_nomax:.2f} without its {mx} ms max call); "
              f"lab {ins_t:.0f} ins/tick, {ext_t:.2f} ext/tick -> {per_tick_nomax*1000/ins_t:.2f} us/ins")
    out["posthoc_script"] = ph_rows
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
