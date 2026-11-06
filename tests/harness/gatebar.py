#!/usr/bin/env python3
"""gatebar.py -- score one gate depth's x2 cells against PLAN-GATES' bar, mechanically.

PLAN-GATES' claim procedure scores a gate cell from its sumline tick figures and
RUNMANI counters. Rounds GATE and S8M did that by hand; this does the same reads
in one place, because ags 0347 changed what silent_irqs counts (dropouts only;
a cold start's first late half is start_latency_irqs) and a re-read under the
new counter should not depend on which fields someone remembered to grep.

  gatebar.py --label S16 --stamp 8249193ed041 --room 3 [--msgskip] DIR_A DIR_B

Bar (PLAN-GATES.md): both tick figures 39.2-40.8, fps_p50 >= 40, completeness
>= 95%, camera witness clean, x2; audio by the counters (pcm_irqs exact,
overwrites 0, late_writes 0, silent_irqs 0 outside room loads).
- Tick figures are compared as recorded (2 dp), never rounded.
- Completeness has no content-dirty counter, so it is given two ways,
  presents_real / render_passes and 1 - frames_skipped / ticks; MET needs both.
- "Outside room loads": a silentirq line with since_room > 0 (patch 0203: the
  interval spanning a load prints since_room=0). The lines must sum to the
  silent_irqs counter, else the cell is flagged.
- pcm_irqs has no logged expected count: printed as recorded, not scored.
- start_latency_irqs and startlat lines are reported, not scored (not in the bar).
- Amendment 2026-09-29, before any data: "pcm_irqs exact" gets a REPORTED accounting line, pcm_irqs + inflight
  vs mixed from audio_vital_status (0 = every mixed chunk was played or is in flight); not scored.
- The camera witness is not scriptable: every MET is "subject to camera CLEAN".
- Amendment 2026-11-05 (F1): late_writes absent is not a missing field when midi=none or midi_tick=poll.
VOID: binary_sha12 != --stamp, exit_code != 0, build_dirty != 0, last room !=
--room, a missing field, or (--msgskip) not exactly one "DOS-PORT msgskip n=1".
"""

import argparse
import re
import sys
from decimal import Decimal
from pathlib import Path

LO, HI = Decimal("39.2"), Decimal("40.8")


def one(pattern, text, what, errs):
    m = re.findall(pattern, text, re.M)
    if not m:
        errs.append("missing " + what)
        return None
    return m[-1]


def cell(d, args):
    d = Path(d)
    tag = d.name.split("-")[0]
    log = (d / (tag + ".LOG")).read_text(errors="ignore") if (d / (tag + ".LOG")).is_file() else ""
    out = (d / "STDOUT.TXT").read_text(errors="ignore") if (d / "STDOUT.TXT").is_file() else ""
    errs, void = [], []
    stamp = one(r"^binary_sha12=([0-9A-Za-z]+)", log, "binary_sha12", errs)
    exitc = one(r"^exit_code=(-?\d+)", log, "exit_code", errs)
    dirty = one(r"^DOS-PORT build_dirty=(\d+)", log + out, "build_dirty", errs)
    room = one(r"Now in room (\d+)", out, "room", errs)
    whole = one(r"^DOS-PORT tick_rate=([\d.]+)", log, "tick_rate", errs)
    fskip = one(r"^DOS-PORT tick_rate=[\d.]+ frames_skipped=(\d+)", log, "frames_skipped", errs)
    steady = one(r"^DOS-PORT tick_rate_steady=([\d.]+)", log, "tick_rate_steady", errs)
    ticks = one(r"^DOS-PORT tick_rate_steady=[\d.]+ ticks=(\d+)", log, "ticks", errs)
    stall = one(r"^DOS-PORT tick_rate_steady=.* stall_ms=(\d+)", log, "stall_ms", errs)
    p50 = one(r"^fps_p50=([\d.]+)", log, "fps_p50", errs)
    rp = one(r"fps_basis .*render_passes=(\d+)", log, "render_passes", errs)
    pr = one(r"fps_basis .*presents_real=(\d+)", log, "presents_real", errs)
    avs = one(r"^audio_vital_status=(.*)$", log, "audio_vital_status", errs) or ""
    c = {}
    for k in ("pcm_irqs", "silent_irqs", "start_latency_irqs", "overwrites", "underruns", "late_writes"):
        m = re.search(r"\b" + k + r"=(\d+)", avs)
        c[k] = int(m.group(1)) if m else None
        # Amendment 2026-11-05 (PLAN-FPS F1, before any F1 data): late_writes is a MIDI ISR-mode field; with midi=none
        # (no MIDI device opened: digital-only games, silent rooms) or midi_tick=poll it is absent by design, not missing.
        if c[k] is None and k == "late_writes" and re.search(r"\bmidi=none\b|\bmidi_tick=poll\b", avs):
            continue
        if c[k] is None and k != "start_latency_irqs":  # absent before ags 0347; the stamp check catches that
            errs.append("missing " + k)
    acc = {k: (int(m.group(1)) if m else None) for k in ("mixed", "inflight")
           for m in [re.search(r"\b" + k + r"=(\d+)", avs)]}
    sil = [(int(t), int(n), int(s)) for t, n, s in
           re.findall(r"^DOS-PORT silentirq tick=(\d+) room=-?\d+ irqs=(\d+) since_room=(\d+)", out, re.M)]
    lat = [(int(t), int(n), int(s)) for t, n, s in
           re.findall(r"^DOS-PORT startlat tick=(\d+) room=-?\d+ irqs=(\d+) since_room=(\d+)", out, re.M)]
    msk = re.findall(r"^DOS-PORT msgskip n=1\b.*$", out, re.M)

    if stamp is not None and stamp != args.stamp:
        void.append("stamp %s != %s" % (stamp, args.stamp))
    if exitc is not None and exitc != "0":
        void.append("exit_code " + exitc)
    if dirty is not None and dirty != "0":
        void.append("build_dirty " + dirty)
    if room is not None and room != str(args.room):
        void.append("room %s != %d" % (room, args.room))
    if args.msgskip and len(msk) != 1:
        void.append("msgskip lines %d != 1" % len(msk))
    void += errs

    print("== %s" % d.name)
    print("   stamp %s exit %s build_dirty %s room %s%s" % (stamp, exitc, dirty, room,
          (" msgskip %d: %s" % (len(msk), " | ".join(msk))) if args.msgskip else ""))
    if void:
        print("   VOID: " + "; ".join(void))
        return None
    whole_d, steady_d = Decimal(whole), Decimal(steady)
    comp_p = Decimal(pr) / Decimal(rp) * 100
    comp_t = (1 - Decimal(fskip) / Decimal(ticks)) * 100
    outside = sum(n for t, n, s in sil if s > 0)
    fails = []
    if not (LO <= whole_d <= HI):
        fails.append("whole-run %s outside 39.2-40.8" % whole)
    if not (LO <= steady_d <= HI):
        fails.append("steady %s outside 39.2-40.8" % steady)
    if Decimal(p50) < 40:
        fails.append("fps_p50 %s < 40" % p50)
    if comp_p < 95 or comp_t < 95:
        fails.append("completeness < 95%")
    if c["overwrites"]:
        fails.append("overwrites %d" % c["overwrites"])
    if c["late_writes"]:
        fails.append("late_writes %d" % c["late_writes"])
    if outside:
        fails.append("silent_irqs %d outside room loads" % outside)
    print("   whole-run %s / steady %s (as recorded)  fps_p50 %s  frames_skipped %s  ticks %s  stall_ms %s" % (
        whole, steady, p50, fskip, ticks, stall))
    print("   completeness: presents_real/render_passes %s/%s = %.2f%%; 1 - frames_skipped/ticks = %.2f%%" % (
        pr, rp, comp_p, comp_t))
    print("   audio: pcm_irqs %s (as recorded) silent_irqs %s start_latency_irqs %s overwrites %s underruns %s"
          " late_writes %s" % tuple("absent" if c[k] is None else c[k] for k in (
              "pcm_irqs", "silent_irqs", "start_latency_irqs", "overwrites", "underruns", "late_writes")))
    if None not in (c["pcm_irqs"], acc["mixed"], acc["inflight"]):
        print("   accounting (reported, not scored): pcm_irqs %d + inflight %d = %d vs mixed %d (diff %d)" % (
            c["pcm_irqs"], acc["inflight"], c["pcm_irqs"] + acc["inflight"], acc["mixed"],
            c["pcm_irqs"] + acc["inflight"] - acc["mixed"]))
    else:
        print("   accounting (reported, not scored): mixed= or inflight= absent")
    for t, n, s in sil:
        print("   silentirq tick=%d irqs=%d since_room=%d -> %s" % (t, n, s, "in play" if s > 0 else "room load"))
    for t, n, s in lat:
        print("   startlat tick=%d irqs=%d since_room=%d (reported, not scored)" % (t, n, s))
    if sum(n for t, n, s in sil) != c["silent_irqs"]:
        fails.append("silentirq lines sum %d != silent_irqs %d" % (sum(n for t, n, s in sil), c["silent_irqs"]))
    if sum(n for t, n, s in lat) != (c["start_latency_irqs"] or 0):
        fails.append("startlat lines sum %d != start_latency_irqs %d" % (sum(n for t, n, s in lat),
                                                                        c["start_latency_irqs"] or 0))
    print("   cell: %s" % ("MET (subject to camera CLEAN)" if not fails else "NOT MET: " + "; ".join(fails)))
    return not fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--stamp", required=True)
    ap.add_argument("--room", type=int, required=True)
    ap.add_argument("--msgskip", action="store_true")
    ap.add_argument("dirs", nargs=2)
    args = ap.parse_args()
    res = [cell(d, args) for d in args.dirs]
    if None in res:
        verdict = "VOID (a cell is void)"
    elif all(res):
        verdict = "MET x2 (subject to camera CLEAN in both)"
    else:
        verdict = "NOT MET"
    print("%s: %s" % (args.label, verdict))
    return 0


if __name__ == "__main__":
    sys.exit(main())
