#!/usr/bin/env python3
"""score-arms.py -- score a multi-stage fsprobe run against PREREG-SMARTDRV.

Gate 0 first: count the /S tables. Then c-stability, then the outcomes.
Base spacing is anchored on a fitted S, never on g_min -- g_min is the most
outlier-sensitive anchor available and two off-lattice members are already on
record. The fold must be able to fail: residuals and the multiplicity
histogram are printed, and P-PERIOD is scored only if max residual <= 0.20
and the arm has at least 5 events.
"""
import re, sys, statistics

MIN_EVENTS_FOR_PERIOD = 5
MAX_FOLD_RESIDUAL = 0.20
C_STABILITY_PCT = 3.0


def fit_S(gaps):
    """Closed-form-p0 phase fit over a gap set; returns (S, worst_residual)."""
    if len(gaps) < 2:
        return None, None
    # S is searched only down to max(gaps)/MAX_N. Without that floor the fit
    # walks off to a subharmonic: on sweep 4 it returned S=4.47 with almost
    # every multiplicity at 8 and a residual of 0.166, which PASSED a
    # residual-only gate. A small enough S divides anything, so a residual
    # threshold alone is an estimator that cannot fail its own assumption --
    # the exact failure the gate was added to prevent, reappearing one level
    # down.
    MAX_N = 4
    lo, hi = max(gaps) / MAX_N, max(gaps) * 1.05
    best = None
    steps = 4000
    for i in range(steps + 1):
        S = lo + (hi - lo) * i / steps
        if S <= 0:
            continue
        r = max(abs(g / S - round(g / S)) for g in gaps)
        if all(round(g / S) >= 1 for g in gaps) and (best is None or r < best[1]):
            best = (S, r)
    return best if best else (None, None)


def main(path):
    txt = open(path, errors="replace").read()

    # Gate 0. The original host-side proxy was "exactly 4 /S tables"; that was
    # MIS-SPECIFIED, not merely strict. `SMARTDRV C-` and `SMARTDRV C` each
    # print a status table of their own, so a correct four-stage run emits
    # six. Counting tables was a fallback written when the binary had no
    # in-instrument assert. It now has one, FSPROBE_STAGES, which is the
    # stronger and also pre-registered check -- so that is Gate 0, and the
    # table count is only required to be at least the number of stages.
    m = re.search(r"FSPROBE_STAGES=(\d+), found (\d+) of", txt)
    stages = re.findall(r"===== SWEEP (\d+) \(STAGE\d+\) =====", txt)
    stables = re.findall(r"drive\s+read cache\s+write cache", txt)
    print("Gate 0:")
    print("   FSPROBE_STAGES assertion: %s"
          % (("declared %s, found %s" % m.groups()) if m else "ABSENT"))
    print("   SWEEP blocks: %d   /S-style tables: %d" % (len(stages), len(stables)))
    if not m or m.group(1) != m.group(2):
        print("VOID -- the in-instrument stage assertion did not pass.")
        return 1
    if len(stages) != int(m.group(1)):
        print("VOID -- %s stages declared but %d sweeps ran."
              % (m.group(1), len(stages)))
        return 1

    # The toggle witness. `SMARTDRV C-` does not print "read cache: no" for
    # C: -- it removes C: from the table entirely. The pre-registration asked
    # for the right condition in the wrong display form; absence is the
    # stronger witness.
    blocks = re.split(r"===== SWEEP \d+ \(STAGE\d+\) =====", txt)
    cached = []
    for b in blocks[:-1]:
        tail = b[-2000:]
        cached.append(bool(re.search(r"^\s+C:\s+\w+", tail, re.M)))
    print("   C: present in the cache table, per stage: %s" % cached)
    if cached != [True, False, False, True]:
        print("VOID -- toggle witness is not A-B-B-A (expected [T,F,F,T]).")
        return 1
    print("   toggle witness OK: A-B-B-A")

    arms = []
    for m in re.finditer(r"===== SWEEP (\d+) \(STAGE\d+\) =====(.*?)(?====== SWEEP |\Z)",
                         txt, re.S):
        body = m.group(2)
        sp = [(int(a), int(b)) for a, b in
              re.findall(r"SPIKE rec=(\d+)\s+end_off=\d+\s+us=(\d+)", body)]
        cm = re.search(r"quiet records n=\d+ mean_us=([\d.]+)", body)
        arms.append({"n": int(m.group(1)), "spikes": sp,
                     "c": float(cm.group(1)) if cm else None})
    print("\nsweeps parsed: %d" % len(arms))
    for a in arms:
        recs = [r for r, _ in a["spikes"]]
        mags = [u for _, u in a["spikes"]]
        gaps = [recs[i + 1] - recs[i] for i in range(len(recs) - 1)]
        a["gaps"], a["mags"] = gaps, mags
        print("\n  sweep %d: events=%d  c=%s us  mean_mag=%s us"
              % (a["n"], len(recs),
                 ("%.1f" % a["c"]) if a["c"] else "?",
                 ("%.0f" % statistics.mean(mags)) if mags else "-"))
        print("    gaps: %s" % gaps)
        if len(gaps) >= MIN_EVENTS_FOR_PERIOD - 1:
            S, r = fit_S(gaps)
            if S:
                ns = [round(g / S) for g in gaps]
                res = [abs(g / S - round(g / S)) for g in gaps]
                hist = {k: ns.count(k) for k in sorted(set(ns))}
                a["S"], a["fold_ok"] = S, (max(res) <= MAX_FOLD_RESIDUAL)
                print("    fitted S = %.2f rec   worst folded residual %.3f  -> fold %s"
                      % (S, max(res), "HELD" if a["fold_ok"] else "FAILED"))
                print("    multiplicities %s   residuals %s"
                      % (hist, [round(x, 3) for x in res]))
        else:
            a["S"], a["fold_ok"] = None, False
            print("    fewer than %d events -- P-PERIOD NOT SCORABLE for this arm"
                  % MIN_EVENTS_FOR_PERIOD)

    if len(arms) == 4:
        A = [arms[0], arms[3]]
        B = [arms[1], arms[2]]
        for lbl, pair in (("A1/A2", A), ("B1/B2", B)):
            cs = [x["c"] for x in pair if x["c"]]
            if len(cs) == 2 and min(cs) > 0:
                d = abs(cs[0] - cs[1]) / statistics.mean(cs) * 100
                print("\n%s c-stability: %.1f%% (bar %.1f%%) -> %s"
                      % (lbl, d, C_STABILITY_PCT,
                         "OK" if d <= C_STABILITY_PCT else "VOID"))
        ca = statistics.mean([x["c"] for x in A if x["c"]])
        cb = statistics.mean([x["c"] for x in B if x["c"]])
        print("\nc  A=%.1f  B=%.1f  -> %.1f%% apart (toggle witness; <3%% = toggle suspect)"
              % (ca, cb, abs(ca - cb) / statistics.mean([ca, cb]) * 100))
        print("events  A=%s  B=%s   (NOT a stability test -- 7/10/14 across identical runs)"
              % ([len(x["spikes"]) for x in A], [len(x["spikes"]) for x in B]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
