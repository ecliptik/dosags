#!/usr/bin/env python3
"""lab-metric-posthoc.py -- POST HOC model, written AFTER the pre-registered verdict (FAIL).

NOT the pre-registered model and NOT its verdict (that is lab-metric.py, LAB-METRIC.md 1.4).
Everything here was designed after the five cells' counts and hardware figures were seen, so its
only honest error figure is the leave-one-out (LOO) one: every constant is refitted on four cells
and the fifth is predicted with them.

Changes from the pre-registered model, each prompted by the per-phase table:
  push     measured bus constant per byte (kept) + a per-rect overhead k_rect (fitted);
           the full-frame single-rect push (SB5O) matched the bus constant (1.01x), the
           multi-rect pushes did not (0.28-0.71x).
  blit     1x copy kept (S2M1 0.97x); the 2x scaled copy gets a fitted us/byte k_sc -- only
           SB5O has one, so when SB5O is held out the derived constant is all there is.
  rb       sprite composite bytes x a fitted scale k_rb on the 19.4 cycles/px figure.
  scene    (3.0 ms + 0.335 ms/sprite + bg bytes at copy speed) x a fitted scale k_sc_scene.
  dirty    8-bit compare + cache, pre-registered constants (F2B1 only; 0.93x).
  per tick a + b x script_ext/tick, fitted by least squares on each training cell's residual
           ((measured busy/render - predicted per-render) / ticks-per-render). Replaces c_ins,
           whose S2F2 calibration folded an 11.7 s blocking call into a per-instruction price.

    lab-metric-posthoc.py [--json OUT]
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("lm", HERE / "lab-metric.py")
lm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lm)
C, CELLS, HW = lm.C, lm.CELLS, lm.HW


def hw_phase(d):
    t = lm.rd(HW / d / "RUNMANI.LOG")
    out = {}
    for k, n, us in re.findall(r"tickstats_(\w+) calls=(\d+) total_ms=\d+ .*? total_us=(\d+)", t):
        out[k] = (int(n), int(us) / 1000.0)
    return out


def cell_data(cell):
    hwd, labd, tgt = CELLS[cell]
    hw = lm.hw_measured(hwd)
    v, _ = lm.lab_vector(labd)
    ph = hw_phase(hwd)
    pres = max(v["presents"], 1)
    r = max(v["renders"], 1)
    t = max(v["ticks"], 1)
    bpp = v["vs_bpp"]
    cbus = C["push_mode13" if tgt == "mode13" else "push_lfb"]
    mean = lambda k: ph[k][1] / ph[k][0] if k in ph and ph[k][0] else 0.0
    return {
        "cell": cell,
        "meas": hw["busy_per_render"],
        "mix": hw["steady_ticks"] / hw["renders"],
        # lab-side quantities, per present / per render / per tick
        "push_bus_ms": v["push_bytes"] / pres * cbus / 1000.0,
        "rects_pp": v["push_rects"] / pres,
        "pres_per_render": v["presents"] / r,
        "blit1x_ms": v["blit1x_bytes"] / r * C["copy"] / 1000.0,
        "blitsc_bytes_pr": v["blitsc_bytes"] / r,
        "rb_ms0": (v["spr_msk_px"] + v["spr_bld_px"]) * bpp / r * C["msk_per_byte"] / 1000.0
                  + v["spr_opq_px"] * bpp / r * C["opq_per_byte"] / 1000.0,
        "scene_ms0": lm.SCENE_FIXED_MS + lm.SCENE_PER_SPRITE_MS * v["spr_n"] / r
                     + v["bg_px"] * bpp / r * C["copy"] / 1000.0 + v["fill_px"] * bpp / r * C["write"] / 1000.0,
        "dirty_ms": (v["cmp_bytes"] * C["cmp"] + v["cache_bytes"] * C["copy"]) / r / 1000.0,
        "ext_pt": v["script_ext"] / t,
        "ins_pt": v["script_ins"] / t,
        # hardware phase means per call
        "hw_puw": mean("present_update_window"),
        "hw_blit": mean("present_blit"),
        "hw_rb": mean("render_backbuffer"),
        "hw_scene": mean("scene_construct"),
    }


def lsq(xs, ys):
    """y = a + b x, least squares; falls back to a mean if x has no spread."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return my, 0.0
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return my - b * mx, b


def ratio_fit(xs, ys):
    """y = k x through the origin (ratio of sums); None if no x."""
    sx = sum(xs)
    return sum(ys) / sx if sx else None


def fit(train):
    k = {}
    # per-rect overhead: hw push minus bus term, per rect
    k["rect"] = ratio_fit([d["rects_pp"] for d in train], [max(d["hw_puw"] - d["push_bus_ms"], 0.0) for d in train]) or 0.0
    sc = [d for d in train if d["blitsc_bytes_pr"] > 0]
    k["sc_us_per_B"] = (sum(d["hw_blit"] * d["pres_per_render"] * 1000.0 for d in sc) /
                        sum(d["blitsc_bytes_pr"] for d in sc)) if sc else C["scaled"]
    k["rb"] = ratio_fit([d["rb_ms0"] for d in train], [d["hw_rb"] for d in train]) or 1.0
    k["scene"] = ratio_fit([d["scene_ms0"] for d in train], [d["hw_scene"] for d in train]) or 1.0
    res = []
    for d in train:
        pr = per_render(d, k)
        res.append((d["meas"] - pr) / d["mix"])
    k["tick_a"], k["tick_b"] = lsq([d["ext_pt"] for d in train], res)
    return k


def per_render(d, k):
    push = (d["push_bus_ms"] + k["rect"] * d["rects_pp"]) * d["pres_per_render"]
    blit = d["blit1x_ms"] + d["blitsc_bytes_pr"] * k["sc_us_per_B"] / 1000.0
    return push + blit + k["rb"] * d["rb_ms0"] + k["scene"] * d["scene_ms0"] + d["dirty_ms"]


def predict(d, k):
    return per_render(d, k) + (k["tick_a"] + k["tick_b"] * d["ext_pt"]) * d["mix"]


def main():
    data = {c: cell_data(c) for c in CELLS}
    out = {"label": "POST HOC -- not the pre-registered model; LOO is its only error figure", "loo": {}, "in_sample": {}}
    print("POST HOC model (see header). Leave-one-out: constants fitted on the other four cells.\n")
    print(f"{'cell':5} {'measured':>9} {'LOO pred':>9} {'ratio':>6}   {'in-sample':>9} {'ratio':>6}   LOO constants")
    kall = fit(list(data.values()))
    rows = []
    for c, d in data.items():
        k = fit([x for n, x in data.items() if n != c])
        p = predict(d, k)
        pin = predict(d, kall)
        rows.append((c, d["meas"], p))
        out["loo"][c] = {"measured": d["meas"], "pred": p, "ratio": p / d["meas"], "constants": k}
        out["in_sample"][c] = {"pred": pin, "ratio": pin / d["meas"]}
        print(f"{c:5} {d['meas']:9.2f} {p:9.2f} {p / d['meas']:6.2f}   {pin:9.2f} {pin / d['meas']:6.2f}   "
              + " ".join(f"{n}={v:.4g}" for n, v in k.items()))
    order = [c for c, *_ in sorted(rows, key=lambda r: r[2])]
    ok15 = all(0.67 <= p / m <= 1.5 for _, m, p in rows)
    print("\nLOO predicted order:", " < ".join(order), "| measured:", " < ".join(lm.MEASURED_ORDER))
    print(f"LOO rank match: {order == lm.MEASURED_ORDER}; LOO all within 1.5x: {ok15}")
    print("\nall-five constants (in-sample, for screening only as far as the LOO error allows):")
    print("  " + " ".join(f"{n}={v:.4g}" for n, v in kall.items()))
    out["loo_order"] = order
    out["loo_rank_ok"] = order == lm.MEASURED_ORDER
    out["loo_within_1p5"] = ok15
    out["constants_all_five"] = kall
    out["cell_inputs"] = data
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
