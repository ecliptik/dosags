#!/usr/bin/env python3
"""d35hw-score.py -- score the D35HW 486 ABBA (PLAN.md "PRE-REGISTRATION D35HW", 36b0a61).

    tests/harness/d35hw-score.py [RESULTS_ROOT] [--date D] [--witness-clean TAG,TAG,...]

Cells D35C1 D35F1 D35F2 D35C2 (C = main 40f319f, stamp 476abb1c5a32; F = main 9ac4ced, 0215 + 0216, stamp
5f052e7319af). With only D35C1 and D35F1 present it scores the 2-cell fallback, as a direction only.
Written and committed before any D35HW cell ran.
"""
import argparse
import json
import os
import re
import sys

STAMP = {"C": "476abb1c5a32", "F": "5f052e7319af"}


def read(p):
    try:
        return open(p, encoding="ascii", errors="replace").read()
    except OSError:
        return None


def input_log_ok(d, tag):
    """Round L rule: INPUT-LOG.jsonl holds run-hw-<TAG>'s lock.acquired .. lock.released, INPUT-LOG.json the raw."""
    raw, jl = read(os.path.join(d, "INPUT-LOG.json")), read(os.path.join(d, "INPUT-LOG.jsonl"))
    if raw is None or jl is None:
        return False, "missing INPUT-LOG.json/.jsonl"
    try:
        ev = [json.loads(l) for l in jl.splitlines() if l.strip()]
    except ValueError:
        return False, "INPUT-LOG.jsonl unparsable"
    owner = "run-hw-" + tag
    kinds = [(e.get("kind"), e.get("owner")) for e in ev]
    if ("lock.acquired", owner) not in kinds or ("lock.released", owner) not in kinds:
        return False, "no lock.acquired/lock.released pair for " + owner
    return True, "%d events" % len(ev)


def cell(root, tag, date, arm, clean):
    d = os.path.join(root, "%s-%s" % (tag, date))
    man = read(os.path.join(d, "RUNMANI.LOG"))
    out = read(os.path.join(d, "STDOUT.TXT")) or ""
    if man is None:
        return None
    c = {"tag": tag, "arm": arm, "void": []}
    c["sha"] = (re.findall(r"binary_sha12=([0-9a-f]+)", man) or ["?"])[0]
    c["dirty"] = (re.findall(r"build_dirty=(-?\d+)", man) or ["?"])[0]
    stalls = [(int(t), int(ms)) for t, ms, j in re.findall(r"DOS-PORT stall100 t_ms=(\d+) ms=(\d+) journey=(\d)", man)
              if j == "0"]
    c["m1"] = max(stalls, key=lambda s: s[1]) if stalls else (None, 0)
    pc = re.search(r"DOS-PORT pcmcache (.*)", man)
    c["pcm"] = dict((k, int(v)) for k, v in re.findall(r"(\w+)=(\d+)", pc.group(1))) if pc else None
    c["memfree"] = int((re.findall(r"memory_min_free_kb=(\d+)", man) or ["-1"])[0])
    for k in ("tick_rate_steady", "share_nojourney", "late_writes", "underruns", "overwrites", "silent_irqs"):
        m = re.findall(r"\b%s=([0-9.]+)" % k, man)
        c[k] = m[0] if m else "NA"
    rooms = set(re.findall(r"Now in room (\d+)", out))
    if c["sha"] != STAMP[arm] or c["dirty"] != "0":
        c["void"].append("binary %s dirty %s (want %s, 0)" % (c["sha"], c["dirty"], STAMP[arm]))
    if "35" not in rooms:
        c["void"].append("not room 35 (%s)" % ",".join(sorted(rooms)))
    if arm == "C" and c["m1"][1] < 1000:
        c["void"].append("C cell without a journey-free stall >= 1000 ms (fixture changed)")
    if tag not in clean:
        c["void"].append("witness not reviewed clean")
    ok, why = input_log_ok(d, tag)
    c["inputlog"] = why
    if not ok:
        c["void"].append("input log: " + why)
    return c


def main(argv):
    ap = argparse.ArgumentParser(prog="d35hw-score.py")
    ap.add_argument("root", nargs="?", default="tests/harness/results")
    ap.add_argument("--date", default=None)
    ap.add_argument("--witness-clean", default="")
    a = ap.parse_args(argv)
    clean = set(t for t in a.witness_clean.split(",") if t)
    date = a.date
    if date is None:
        ds = sorted(x.split("-", 1)[1] for x in os.listdir(a.root) if x.startswith("D35C1-"))
        date = ds[-1] if ds else "?"
    cells = {t: cell(a.root, t, date, t[3], clean) for t in ("D35C1", "D35F1", "D35F2", "D35C2")}
    for t, c in cells.items():
        if c is None:
            print("%s: no result" % t)
            continue
        print("%s %s sha=%s M1=%d ms at t=%s pcmcache=%s memfree=%d steady=%s share_nj=%s late=%s underruns=%s "
              "overwrites=%s silent=%s input_log=%s%s" % (
                  t, c["arm"], c["sha"], c["m1"][1], c["m1"][0], c["pcm"], c["memfree"], c["tick_rate_steady"],
                  c["share_nojourney"], c["late_writes"], c["underruns"], c["overwrites"], c["silent_irqs"],
                  c["inputlog"], (" VOID: " + "; ".join(c["void"])) if c["void"] else ""))
    have = [t for t, c in cells.items() if c is not None]
    if any(cells[t]["void"] for t in have):
        print("VERDICT D35HW VOID (a cell is void; see above)")
        return 1
    if set(have) == {"D35C1", "D35F1", "D35F2", "D35C2"}:
        C = [cells["D35C1"]["m1"][1], cells["D35C2"]["m1"][1]]
        F = [cells["D35F1"]["m1"][1], cells["D35F2"]["m1"][1]]
        N = max(abs(C[0] - C[1]), abs(F[0] - F[1]))
        D = sum(F) / 2.0 - sum(C) / 2.0
        mode = "ABBA"
    elif set(have) >= {"D35C1", "D35F1"}:
        D, N, mode = cells["D35F1"]["m1"][1] - cells["D35C1"]["m1"][1], None, "2-CELL FALLBACK (direction only)"
    else:
        print("VERDICT D35HW INCOMPLETE")
        return 2
    print("M1 (end-of-dialogue stall): D = F - C = %+.1f ms, N = %s (%s); predicted D in [-250, -30]" % (
        D, "NA" if N is None else "%d" % N, mode))
    fs = [cells[t] for t in have if t[3] == "F"]
    cs = [cells[t] for t in have if t[3] == "C"]
    pcm_ok = all(c["pcm"] and c["pcm"].get("hits", 0) >= 50 and c["pcm"].get("evictions", 1) == 0
                 and c["pcm"].get("bytes", 1 << 30) <= c["pcm"].get("cap_kb", 0) * 1024 for c in fs)
    mem_ok = min(c["memfree"] for c in fs) >= min(c["memfree"] for c in cs) - 512
    print("secondary: pcmcache hits>=50/evictions 0/bytes<=cap %s; memory_min_free_kb F >= C - 512 %s" % (
        "PASS" if pcm_ok else "FAIL", "PASS" if mem_ok else "FAIL"))
    if N is None:
        print("VERDICT D35HW DIRECTION %s (fallback: no noise figure)" % ("shorter on F" if D < 0 else "not shorter on F"))
        return 0
    if D > N:
        print("VERDICT D35HW REVERT CANDIDATE (the stall got worse on F by more than the noise)")
    elif D < -N and D <= -30:
        print("VERDICT D35HW GAIN")
    else:
        print("VERDICT D35HW NO MEASURABLE EFFECT on the 486")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
