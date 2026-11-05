#!/usr/bin/env python3
"""gate3-bars.py -- compute Gate 3's two bars from a run directory.

Exists because bar 1 has been computed by hand three times today against
three different segmentations, and each time the number moved by more than
the bar's own tolerance. A gate figure that depends on which exclusions
someone remembered to apply is not a gate figure.

The operator's definitions, third revision (2026-09-19):

  bar 1 -- sustained tick rate during play, excluding transitions AND
           every blocking tick. Target 40 +/- 2% (39.2 .. 40.8).
  bar 2 -- no single blocking operation exceeds a budget. Budget unset;
           this prints the distribution so one can be argued from data.

A transition is `fadeout_begin` to `fadein_end` (patch 0139's fifth
milestone stamp). Measuring only to `fadein_begin`, as every earlier
calculation did, left 37% of transition time in bar 1's denominator.

A blocking tick is one whose EXCLUSIVE time exceeds the stall threshold --
`self_us`, with nested game loops already subtracted, so it really is one
loop iteration spending that long in its own code.

Deliberately reports bar 1 under several segmentations rather than one
number, because the difference between them was worth 21 ticks/s and
hiding that behind a single figure is how the question got confused in the
first place.
"""

import re
import sys
from pathlib import Path


def read(run_dir):
    text = ""
    for name in ("RUNMANI.LOG", "STDOUT.TXT"):
        p = Path(run_dir) / name
        if p.is_file():
            text += p.read_text(errors="ignore")
    if not text:
        sys.exit(f"gate3-bars.py: no RUNMANI.LOG or STDOUT.TXT in {run_dir}")
    return text


def transitions(text):
    """(fadeout_begin, fadein_end) pairs, in ms on the engine clock."""
    stamps = [
        (int(m.group(1)), m.group(2))
        for m in re.finditer(r"DOSAGS_XT t_ms=(\d+) phase=(fade\w+)", text)
    ]
    segs, open_at = [], None
    for t, phase in stamps:
        if phase == "fadeout_begin" and open_at is None:
            open_at = t
        elif phase == "fadein_end" and open_at is not None:
            segs.append((open_at, t))
            open_at = None
    # Whether the fifth stamp was present at all decides if bar 1 is a
    # figure or an upper bound, so the caller is told, not left to infer.
    have_fifth = any(p == "fadein_end" for _, p in stamps)
    return segs, have_fifth


def stalls(text):
    """(tick_index, ms, t_ms) per blocking tick. t_ms may be None on a run
    predating patch 0149, in which case the union cannot be taken."""
    out = []
    for m in re.finditer(r"tick_stall index=(\d+) ms=(\d+)(?: t_ms=(\d+))?"
                         r"(?: begin_ms=(\d+) end_ms=(\d+))?", text):
        out.append((int(m.group(1)), int(m.group(2)),
                    int(m.group(3)) if m.group(3) is not None else None,
                    int(m.group(4)) if m.group(4) is not None else None,
                    int(m.group(5)) if m.group(5) is not None else None))
    return out


def union_ms(intervals):
    """Total wall time covered by [start, end) intervals, counting overlap once.

    The whole reason this function exists: bar 1 was computed by SUMMING
    transition time and blocking-tick time, which overlap heavily because a
    transition is largely made of blocking ticks. That removed 137,708 ms of
    a 170,930 ms run -- 80% of the wall clock -- and produced 107 ticks/s on
    a 40 Hz pacer.
    """
    if not intervals:
        return 0, []
    xs = sorted(intervals)
    merged = [list(xs[0])]
    for a, b in xs[1:]:
        if a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return sum(b - a for a, b in merged), merged


def assert_exclusion_sane(excluded_ms, loop_ms, label):
    """Physical bounds on a figure computed by exclusion.

    Generalises the instrument plausibility floor to analysis: a derived
    quantity asserts its own bounds where it is computed, rather than
    relying on a reader noticing the result is ridiculous. Three separate
    tools produced plausible-shaped wrong numbers in one day and two were
    caught only because the values happened to be absurd.
    """
    # The >70% check is INFORMATIONAL, not a refusal. It was written as a
    # proxy for the overlap bug (summing two overlapping sets), and taking
    # the union of MEASURED spans removes that bug at the source. A game
    # that genuinely spends most of its run inside blocking operations --
    # which AGS Quest's autopilot does -- is a fact about the fixture, not
    # an arithmetic error, and refusing on it would suppress a correct
    # answer. Excluding MORE than the run is still impossible and still a
    # hard failure.
    problems = []
    if excluded_ms > loop_ms:
        problems.append(f"excluded {excluded_ms} ms of a {loop_ms} ms run "
                        f"-- more than elapsed, impossible")
    elif excluded_ms > 0.70 * loop_ms:
        print(f"  note: {label} excludes {100.0*excluded_ms/loop_ms:.0f}% of the "
              f"run ({excluded_ms} of {loop_ms} ms) -- large, but the union is "
              f"of measured spans, so this is the fixture blocking a lot, not "
              f"double-counting")
    for p in problems:
        print(f"  !! {label}: {p}")
    return not problems


def persec(text):
    """(t_ms, cumulative_tick) samples, for counting ticks inside an interval.

    Excluding wall time WITHOUT excluding the ticks that happened during it
    inflates the rate -- on BAR1A that produced 49.53 ticks/s, because 99 s
    of wall clock was removed while only the 19 blocking ticks came out of
    the numerator, leaving every ordinary tick that ran inside a transition
    still counted against a much shorter denominator.
    """
    return [(int(m.group(2)), int(m.group(1)))
            for m in re.finditer(r"persec t=\d+ tick=(\d+) renders=\d+ real=\d+ "
                                 r"skipped=\d+ ms=(\d+)", text)]


def partition_by_intervals(samples, intervals):
    """Split the per-second series into (excluded, included) (ticks, ms).

    Partitions whole SAMPLES by where each sample's timestamp falls -- it
    does not interpolate inside one. Interpolating was the first attempt and
    it is wrong here for a specific reason: the series is emitted per tick,
    so a six-second blocking tick produces NO samples across its span, and
    linear interpolation across that gap invents ticks that never ran.

    Each sample carries its own wall delta, so the excluded and included
    wall times come out of the same partition as the tick counts and cannot
    disagree with them. That is the property the earlier version lacked:
    it took wall time from the interval arithmetic and ticks from an
    interpolation, and the two described different things.
    """
    samples = sorted(samples)
    ex_t = ex_ms = in_t = in_ms = 0
    prev = None
    for ms, tick in samples:
        if prev is not None:
            d_ms, d_tick = ms - prev[0], tick - prev[1]
            if d_ms > 0 and d_tick >= 0:
                mid = (ms + prev[0]) // 2
                if any(a <= mid < b for a, b in intervals):
                    ex_t += d_tick; ex_ms += d_ms
                else:
                    in_t += d_tick; in_ms += d_ms
        prev = (ms, tick)
    return (ex_t, ex_ms), (in_t, in_ms)


def scalar(text, key, cast=int):
    m = re.search(rf"{key}=([0-9.]+)", text)
    return cast(m.group(1)) if m else None


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: gate3-bars.py <run-dir>")
    text = read(sys.argv[1])

    ticks = scalar(text, "tick_rate_steady=[0-9.]+ ticks")
    if ticks is None:
        m = re.search(r"tick_rate_steady=[0-9.]+ ticks=(\d+)", text)
        ticks = int(m.group(1)) if m else None
    loop_ms = scalar(text, "loop_ms")
    stall_ms_total = scalar(text, "stall_ms")
    stall_ticks = scalar(text, "stall_ticks")
    if None in (ticks, loop_ms, stall_ms_total, stall_ticks):
        sys.exit("gate3-bars.py: run is missing tick_rate_steady/loop_ms/stall_ms")

    segs, have_fifth = transitions(text)
    tr_ms = sum(b - a for a, b in segs)
    st = stalls(text)

    print(f"run: {sys.argv[1]}")
    print(f"ticks={ticks} loop_ms={loop_ms} stall_ticks={stall_ticks} "
          f"stall_ms={stall_ms_total}")
    print(f"transitions: {len(segs)} segments, {tr_ms} ms"
          + ("" if have_fifth else "   <-- NO fadein_end STAMP: transitions"
                                   " under-measured, bar 1 is an UPPER BOUND"))
    print()

    def rate(dt, dm, label):
        n, d = ticks - dt, loop_ms - dm
        if d <= 0:
            print(f"  {label:<46} n/a")
            return None
        r = 1000.0 * n / d
        print(f"  {label:<46} {n:6d} ticks / {d:7d} ms = {r:6.2f}")
        return r

    print("bar 1 -- sustained tick rate during play")
    rate(0, 0, "whole run (no exclusions)")
    rate(0, tr_ms, "transitions excluded only")
    # Excluding a blocking tick removes that tick AND its exclusive time.
    # Take the UNION of transitions and blocking ticks, never the sum --
    # they overlap, because a transition is largely made of blocking ticks.
    # patch 0153's MEASURED spans, never 0149's derived t_ms -- see
    # game_run.cpp for why a window derived from self_ms cannot work.
    have_t_ms = bool(st) and all(b is not None and e is not None
                                 for _, _, _, b, e in st)
    if not have_t_ms:
        print("  BAR 1: not computable -- this run's tick_stall records carry no")
        print("         begin_ms/end_ms (patch 0153). A window derived from")
        print("         self_ms is too short and misplaced, because self_ms")
        print("         excludes nested loops and the wall span does not; three")
        print("         methods built on it gave 107.10, 26.24 and 21.98 on one")
        print("         run. Re-run on a current binary.")
        bar1 = None
    else:
        intervals = [(a, b) for a, b in segs] + [(b, e) for _, _, _, b, e in st]
        excl_ms, merged = union_ms(intervals)
        sum_ms = sum(b - a for a, b in intervals)
        print(f"  exclusion: union {excl_ms} ms, naive sum {sum_ms} ms "
              f"(overlap {sum_ms - excl_ms} ms)")
        # Take out the TICKS inside that wall time too, not just the 19
        # blocking ones. A transition runs ordinary ticks as well, and
        # leaving them in the numerator against a shortened denominator is
        # what produced 49.53 on a 40 Hz pacer.
        (ex_t, ex_ms), (in_t, in_ms) = partition_by_intervals(persec(text), merged)
        ok = assert_exclusion_sane(excl_ms, loop_ms, "bar 1")
        print(f"  partitioned by the persec series:")
        print(f"    excluded  {ex_t:5d} ticks / {ex_ms:7d} ms")
        print(f"    remaining {in_t:5d} ticks / {in_ms:7d} ms  <= BAR 1")
        bar1 = (1000.0 * in_t / in_ms) if in_ms > 0 else None
        if bar1 is not None:
            print(f"  {'transitions AND blocking ticks excluded':<46}"
                  f" {in_t:6d} ticks / {in_ms:7d} ms = {bar1:6.2f}")
        # STOP. This figure is not trustworthy and the tool says so rather
        # than printing it as bar 1.
        #
        # Three methods on the SAME run gave 107.10, 26.24 and 21.98. That is
        # not three refinements converging, it is three reconstructions of a
        # quantity the data does not actually contain, and the spread is five
        # times the bar's whole tolerance. The tool was written because bar 1
        # kept moving when computed by hand; it now moves when computed by
        # tool, which is the same failure wearing a better coat.
        #
        # The specific defect: a blocking tick's window is built as
        # [t_ms, t_ms + self_ms), and self_ms EXCLUDES nested game loops
        # while the wall span does not. So the window is both too short and
        # misplaced, and every sample-to-window assignment inherits that.
        # Against 40 Hz, 21.98 is also simply implausible for ordinary play.
        #
        # What would make it computable: the wall-clock START and END of each
        # excluded region, recorded directly, instead of reconstructed from a
        # self-time and a per-second series. Until then this is an open
        # instrument gap, not a measurement.
        if bar1 is not None and bar1 > 45.0:
            print("      REFUSED: above 45, which a 40 Hz pacer cannot produce.")
            print("      DO NOT QUOTE.")
            bar1 = None
    if bar1 is not None:
        lo, hi = 40 * 0.98, 40 * 1.02
        verdict = "IN BAND" if lo <= bar1 <= hi else (
            "FAILS HIGH" if bar1 > hi else "FAILS LOW")
        print(f"      target 40 +/- 2% ({lo:.1f} .. {hi:.1f}): {verdict}")
        if not have_fifth:
            print("      (upper bound only -- see the stamp warning above)")

    print()
    print("bar 2 -- blocking-operation budget (no budget set yet)")
    # Same overlap caveat as bar 1: a transition CONTAINS blocking ticks, so
    # listing both is double-counting. Blocking ticks alone are the honest
    # list -- each is one loop iteration's own exclusive time, so they cannot
    # overlap each other. Transitions are reported separately above.
    ops = sorted([ms for _, ms, _, _, _ in st], reverse=True)
    if not ops:
        print("  no blocking operations recorded")
        return
    print(f"  {len(ops)} blocking operations, worst {ops[0]} ms, "
          f"median {ops[len(ops)//2]} ms, total {sum(ops)} ms")
    print("  worst 8:", ", ".join(f"{v}" for v in ops[:8]))
    for budget in (500, 1000, 2000, 4000):
        over = [v for v in ops if v > budget]
        print(f"  at a {budget:5d} ms budget: {len(over):3d} of {len(ops)} "
              f"operations fail")


if __name__ == "__main__":
    main()
