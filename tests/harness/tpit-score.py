#!/usr/bin/env python3
"""tpit-score.py -- score TPIT's C/F/R cells (PLAN.md "PRE-REGISTRATION TPIT" + amendment 1).

    tests/harness/tpit-score.py [RESULTS_ROOT] [--date D]

Cells (DOSBox-X, room 35, s8-cell opl3, DRAIN_STI=0): TPITC (the CAP3 re-cut tree, PIT forced), TPITC2 (the
same, only if TPITC shows no outlier), TPITF (+ SDL 0198 + ags 0217 + the wrap flag, PIT forced), TPITR (TPITC's
binary on the RDTSC timer). Stamps: C/R f90938dd7e0d, F c3c81b632b85. Committed before any C/F/R result.

Registered: C shows >= 1 isr_max_us >= 15000 (its power; VOID if not in two runs); F none (< 12000); F's
isr_ns_per_write below C's and within 10% of R's; late_writes/underruns/overwrites and the tick figures the
same class in C and F.
"""
import argparse
import os
import re
import sys

STAMP = {"TPITC": "f90938dd7e0d", "TPITC2": "f90938dd7e0d", "TPITF": "c3c81b632b85", "TPITR": "f90938dd7e0d"}
TIMER = {"TPITC": "PIT", "TPITC2": "PIT", "TPITF": "PIT", "TPITR": "RDTSC"}


def read(p):
    try:
        return open(p, encoding="ascii", errors="replace").read()
    except OSError:
        return None


def cell(root, tag, date):
    d = os.path.join(root, "%s-%s" % (tag, date))
    cd = os.path.join(d, "cell")
    man = read(os.path.join(cd, "RUNMANI.LOG"))
    if man is None:
        return None
    dbg = read(os.path.join(cd, "SDLDBG.LOG")) or ""
    out = read(os.path.join(cd, "STDOUT.TXT")) or ""
    c = {"tag": tag, "void": []}
    g = lambda k: (re.findall(r"\b%s=([0-9.]+)" % k, man) or [None])[-1]
    c.update({k: g(k) for k in ("isr_max_us", "isr_ns_per_write", "isr_burst", "late_writes", "underruns",
                                "overwrites", "tick_rate_steady", "frames_skipped")})
    c["sha"] = (re.findall(r"binary_sha12=([0-9a-f]+)", man) or ["?"])[0]
    c["dirty"] = (re.findall(r"build_dirty=(-?\d+)", man) or ["?"])[0]
    uw = re.search(r"uclockwrap first=(\d+) wrapped=(\d+)", man)
    c["uclockwrap"] = "%s/%s" % uw.groups() if uw else "none"
    t = re.search(r"audio IRQ timer: ([A-Za-z0-9]+)", dbg)
    c["timer"] = t.group(1) if t else "?"
    if c["sha"] != STAMP[tag] or c["dirty"] != "0":
        c["void"].append("binary %s dirty %s (want %s, 0)" % (c["sha"], c["dirty"], STAMP[tag]))
    if TIMER[tag] == "PIT" and not c["timer"].startswith("8253"):
        c["void"].append("timer %s, want the PIT" % c["timer"])
    if TIMER[tag] == "RDTSC" and c["timer"] != "RDTSC":
        c["void"].append("timer %s, want RDTSC" % c["timer"])
    if "Now in room 35" not in out:
        c["void"].append("not room 35")
    if tag == "TPITF" and not (uw and int(uw.group(1)) == 1 and int(uw.group(2)) > 0):
        c["void"].append("the wrapper did not run (uclockwrap %s)" % c["uclockwrap"])
    return c


def main(argv):
    ap = argparse.ArgumentParser(prog="tpit-score.py")
    ap.add_argument("root", nargs="?", default="tests/harness/results")
    ap.add_argument("--date", default="2026-09-25")
    a = ap.parse_args(argv)
    cells = {t: cell(a.root, t, a.date) for t in ("TPITC", "TPITC2", "TPITF", "TPITR")}
    for t, c in cells.items():
        if c is None:
            print("%s: no result" % t)
            continue
        print("%s sha=%s timer=%s isr_max_us=%s isr_ns_per_write=%s isr_burst=%s late=%s underruns=%s overwrites=%s "
              "steady=%s skipped=%s uclockwrap=%s%s" % (
                  t, c["sha"], c["timer"], c["isr_max_us"], c["isr_ns_per_write"], c["isr_burst"], c["late_writes"],
                  c["underruns"], c["overwrites"], c["tick_rate_steady"], c["frames_skipped"], c["uclockwrap"],
                  (" VOID: " + "; ".join(c["void"])) if c["void"] else ""))
    need = ("TPITC", "TPITF", "TPITR")
    if any(cells[t] is None for t in need):
        print("VERDICT TPIT INCOMPLETE")
        return 2
    if any(cells[t]["void"] for t in need) or (cells["TPITC2"] and cells["TPITC2"]["void"]):
        print("VERDICT TPIT VOID (a cell is void; see above)")
        return 1
    cs = [c for c in (cells["TPITC"], cells["TPITC2"]) if c]
    power = any(int(c["isr_max_us"] or 0) >= 15000 for c in cs)
    if not power:
        if len(cs) < 2:
            print("VERDICT TPIT PENDING: TPITC shows no outlier >= 15000 us; run TPITC2 (registered)")
            return 2
        print("VERDICT TPIT VOID (no power: no isr_max_us >= 15000 in two C runs) -- reported, not re-tuned")
        return 1
    F, R = cells["TPITF"], cells["TPITR"]
    C = next(c for c in cs if int(c["isr_max_us"] or 0) >= 15000)
    f_ns, c_ns, r_ns = (float(x["isr_ns_per_write"]) for x in (F, C, R))
    res = [
        ("F: isr_max_us %s < 12000 (no outlier)" % F["isr_max_us"], int(F["isr_max_us"]) < 12000),
        ("F: isr_ns_per_write %.0f below C's %.0f" % (f_ns, c_ns), f_ns < c_ns),
        ("F: isr_ns_per_write %.0f within 10%% of R's %.0f" % (f_ns, r_ns), abs(f_ns - r_ns) <= 0.10 * r_ns),
    ]
    for text, ok in res:
        print("%s  %s" % ("PASS" if ok else "FAIL", text))
    print("REPORT: late %s/%s underruns %s/%s overwrites %s/%s steady %s/%s (C/F; same class registered)" % (
        C["late_writes"], F["late_writes"], C["underruns"], F["underruns"], C["overwrites"], F["overwrites"],
        C["tick_rate_steady"], F["tick_rate_steady"]))
    print("VERDICT TPIT %s" % ("PASS" if all(ok for _, ok in res) else "FAIL"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
