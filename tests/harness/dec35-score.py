#!/usr/bin/env python3
"""dec35-score.py -- score the DEC35 cells against PLAN.md's pre-registration (2c52eeb0).

    tests/harness/dec35-score.py [RESULTS_ROOT] [--date 2026-09-25]

Reads RESULTS_ROOT/DEC35{C,R,F,V}-DATE/cell/{STDOUT.TXT,RUNMANI.LOG} (the throwaway stall probe's
LABPROBE lines, stall100 lines, the pcmcache line, binary stamps) and prints every measure and each
pre-registered prediction's verdict. Written and committed before any DEC35 cell had a result.

Measures (engine clock, t_ms from engine start; the probe prints brackets >= 2 ms):
  M1  the decode_pcm bracket nested inside ambient 18's PlayAmbientSound bracket (the one at the end
      of the opening dialogue: the first PlayAmbientSound after t=30 s), its ms; 0 if none is nested
  M2  decode_pcm brackets starting after t=38900 ms: count and total ms
  M2F (FIX-P) decode_pcm brackets after the FIRST one after t=38900 (the repeating clip's first play)
  M3  the stall100 gap containing M1's PlayAmbientSound start, its ms
  M4  the pcmcache line
"""
import os
import re
import sys

BIN = {"C": "29f89b6ed84f", "R": "39e868922fb2", "F": "2fa6ab52f25f", "V": "2fa6ab52f25f"}


def read(path):
    try:
        return open(path, encoding="ascii", errors="replace").read()
    except OSError:
        return None


def measures(cell_dir):
    out = read(os.path.join(cell_dir, "STDOUT.TXT")) or ""
    man = read(os.path.join(cell_dir, "RUNMANI.LOG")) or ""
    m = {"present": bool(out and man)}
    probes = [(n, int(t), int(ms)) for n, t, ms in
              re.findall(r"LABPROBE (\w+) t_ms=(\d+) ms=(\d+)", out)]
    m["sha"] = (re.findall(r"binary_sha12=([0-9a-f]+)", man) or ["?"])[0]
    m["dirty"] = (re.findall(r"build_dirty=(-?\d+)", man) or ["?"])[0]
    pas = [p for p in probes if p[0] == "PlayAmbientSound" and p[1] > 30000]
    m["pas"] = pas[0] if pas else None
    decs = [p for p in probes if p[0] == "decode_pcm"]
    m1 = 0
    if m["pas"]:
        _, t0, ms0 = m["pas"]
        inner = [d for d in decs if d[1] >= t0 and d[1] + d[2] <= t0 + ms0 + 1]
        m1 = sum(d[2] for d in inner)
    m["M1"] = m1
    late = [d for d in decs if d[1] > 38900]
    m["M2n"], m["M2ms"] = len(late), sum(d[2] for d in late)
    m["M2F"] = max(0, len(late) - 1)
    m["M3"] = None
    stalls = [(int(t), int(ms)) for t, ms in re.findall(r"DOS-PORT stall100 t_ms=(\d+) ms=(\d+)", man)]
    if m["pas"]:
        t0 = m["pas"][1]
        for t, ms in stalls:
            if t - ms <= t0 <= t:
                m["M3"] = ms
    pc = re.search(r"DOS-PORT pcmcache (.*)", man)
    m["M4"] = dict(re.findall(r"(\w+)=(\d+)", pc.group(1))) if pc else None
    return m


def verdict(ok):
    return "PASS" if ok else "FAIL"


def main(argv):
    root = next((a for a in argv if not a.startswith("--")), "tests/harness/results")
    date = argv[argv.index("--date") + 1] if "--date" in argv else "2026-09-25"
    cells = {}
    for k in "CRFV":
        d = os.path.join(root, "DEC35%s-%s" % (k, date), "cell")
        cells[k] = measures(d)
    for k, m in cells.items():
        if not m["present"]:
            print("DEC35%s: no result yet" % k)
            continue
        pas = m["pas"]
        print("DEC35%s sha=%s dirty=%s PlayAmbientSound=%s M1=%d M2=%d/%dms M2F=%d M3=%s M4=%s"
              % (k, m["sha"], m["dirty"], "%d@%d" % (pas[2], pas[1]) if pas else "none", m["M1"],
                 m["M2n"], m["M2ms"], m["M2F"], m["M3"], m["M4"]))
    if not all(cells[k]["present"] for k in "CRFV"):
        print("VERDICT DEC35 INCOMPLETE")
        return 2
    C, R, F, V = (cells[k] for k in "CRFV")
    void = []
    for k in "CRFV":
        if cells[k]["dirty"] != "0":
            void.append("DEC35%s build_dirty=%s" % (k, cells[k]["dirty"]))
        if cells[k]["sha"] != BIN[k]:
            void.append("DEC35%s ran %s, not %s" % (k, cells[k]["sha"], BIN[k]))
    if C["M3"] is None:
        void.append("DEC35C: no stall100 gap holds ambient 18's start (the stall did not reproduce)")
    if void:
        for v in void:
            print("VOID: " + v)
        print("VERDICT DEC35 VOID")
        return 1
    res = []
    base_ok = 223 <= C["M1"] <= 273 and C["M2n"] >= 90
    res.append(("C reproduces 9b.2: M1 %d in 223..273, M2 %d >= 90" % (C["M1"], C["M2n"]), base_ok, False))
    res.append(("R: M1 %d <= 45%% of C's %d (%.0f)" % (R["M1"], C["M1"], 0.45 * C["M1"]),
                R["M1"] <= 0.45 * C["M1"], True))
    res.append(("R: M2 %d >= 90 brackets, mean %.1f ms < C's %.1f ms" % (
        R["M2n"], R["M2ms"] / max(1, R["M2n"]), C["M2ms"] / max(1, C["M2n"])),
        R["M2n"] >= 90 and R["M2ms"] / max(1, R["M2n"]) < C["M2ms"] / max(1, C["M2n"]), True))
    res.append(("F: M1 %d within +/-10%% of R's %d" % (F["M1"], R["M1"]),
                abs(F["M1"] - R["M1"]) <= 0.10 * max(1, R["M1"]), True))
    res.append(("F: M2F %d == 0" % F["M2F"], F["M2F"] == 0, True))
    m4 = F["M4"] or {}
    res.append(("F: pcmcache hits %s >= 90, evictions %s == 0, bytes %s <= cap %s KB" % (
        m4.get("hits"), m4.get("evictions"), m4.get("bytes"), m4.get("cap_kb")),
        bool(m4) and int(m4["hits"]) >= 90 and int(m4["evictions"]) == 0
        and int(m4["bytes"]) <= int(m4["cap_kb"]) * 1024, True))
    need = 0.8 * (C["M1"] - F["M1"])
    res.append(("F vs C: M3 shorter by %s >= %.0f (80%% of M1's drop)" % (
        (C["M3"] - F["M3"]) if F["M3"] is not None else "n/a (F has no stall100 there)", need),
        (C["M3"] - (F["M3"] or 0)) >= need, True))
    v4 = V["M4"] or {}
    res.append(("V: verify_mismatches %s == 0 with verify %s >= 90" % (v4.get("verify_mismatches"), v4.get("verify")),
                bool(v4) and int(v4["verify_mismatches"]) == 0 and int(v4["verify"]) >= 90, True))
    for text, ok, _ in res:
        print("%s  %s" % (verdict(ok), text))
    gating = all(ok for _, ok, g in res if g)
    print("VERDICT DEC35 %s%s" % ("PASS" if gating else "FAIL",
                                "" if base_ok else " (baseline moved: judged against DEC35C, recorded)"))
    return 0 if gating else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
