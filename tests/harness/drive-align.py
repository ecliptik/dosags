#!/usr/bin/env python3
"""drive-align.py -- place the game's input window on drive-walk.sh's host clock.

    tests/harness/drive-align.py RESULTS_DIR [--tol-ms N] [--quiet]

WHY. drive-walk.sh clicks for as long as run-hw.sh holds the input lock, and that
hold is not the game's input window: it starts before the engine is up and ends when
the screen has settled, which can be well after the game quit (S8HO2: 77 host clicks
against 46 driver presses) or before it (S8H-O1 stopped 80 s in). So "host clicks =
driver presses" cannot be judged from the raw counts, and not across rounds. The
host cannot see the window live either: at 512x384 the capture dongle cannot lock,
so every in-game frame is black, and the game leaves no LED trace.

HOW. The engine records every click it dequeued (RUNMANI.LOG `journey kind=click
t_ms=`, engine-start relative, ags 0250) and the run length (`duration_s`, whole
seconds, engine start to quit). The host records every click it sent
(DRIVE-WALK.LOG). The two series have the same irregular cadence, so the offset
between the two clocks is the one that pairs the most host clicks with engine clicks
within --tol-ms; its median residual refines it. Engine start, the boot journey's
end and quit then map onto host time, and each host click is classed:

  before  -- ahead of engine start (the driver was not counting for the game)
  boot    -- engine start to the end of the boot journey (first playable
             present). The driver's counters are reset at SDL's mouse init,
             somewhere inside boot, at a time nothing logs, so a boot click
             may or may not be in mouse_presses_hw; S8HO2's three were not.
  in      -- boot end to quit
  edge    -- inside quit's +/-1 s uncertainty
  after   -- after quit (at a DOS prompt; no game counted it)

The check that means something is then: in (+ edge) vs mouse_presses_hw, with
boot clicks as the only allowed excess on the hw side. Output
goes to DRIVE-ALIGN.txt in RESULTS_DIR; the raw DRIVE-WALK.LOG is never edited.
Works on logs from before drive-walk.sh logged milliseconds (whole-second stamps;
use a wider --tol-ms, default picks 1500 for those and 600 otherwise).
"""
import argparse
import os
import re
import statistics
import sys


# The engine starts after run-hw takes the input lock (RUN.BAT is typed under it): 2-13 s after in
# rounds D-I. The window is generous on purpose; it only has to exclude whole-period aliases.
START_BEFORE_LOCK_S = 2
START_AFTER_LOCK_S = 30


def die(msg):
    print("drive-align: " + msg, file=sys.stderr)
    sys.exit(2)


def hms_to_s(s):
    h, m, rest = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def s_to_hms(t):
    t = t % 86400
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    return "%02d:%02d:%06.3f" % (h, m, t % 60)


def read_host(path):
    """Host click times in seconds of the UTC day (monotonic across midnight)."""
    clicks, ms_res, prev, day = [], False, None, 0.0
    lock_t = lock_end_t = None
    failed = []  # clicks whose press or release send exited non-zero
    for line in open(path, encoding="ascii", errors="replace"):
        m = re.match(r"(\d\d:\d\d:\d\d(?:\.\d+)?) (.*)", line)
        if not m:
            continue
        t = hms_to_s(m.group(1))
        if prev is not None and t + day < prev - 43200:
            day += 86400
        t += day
        prev = t
        body = m.group(2)
        c = re.match(r"click (\d+)\b", body)
        if c:
            rc = re.findall(r"rc_(?:down|up)=(\d+)", body)
            if any(int(x) != 0 for x in rc):
                failed.append(int(c.group(1)))
            d = re.search(r"down_at=(\d\d:\d\d:\d\d\.\d+)", body)
            if d:
                td = hms_to_s(d.group(1)) + day
                if td > t + 43200:
                    td -= 86400
                clicks.append((int(c.group(1)), td))
                ms_res = True
            else:
                clicks.append((int(c.group(1)), t))
        elif body.startswith("lock is "):
            lock_t = t
        elif body.startswith("lock no longer") or body.startswith("done:"):
            lock_end_t = lock_end_t or t
    return clicks, ms_res, lock_t, lock_end_t, failed


def read_engine(path):
    clicks, duration_s, hw, seen, boot_ms = [], [], None, None, None
    for line in open(path, encoding="ascii", errors="replace"):
        m = re.search(r"journey kind=boot\b.*?\bt_ms=(\d+) ms=(\d+)", line)
        if m:
            boot_ms = int(m.group(1)) + int(m.group(2))
            continue
        m = re.search(r"journey kind=click\b.*?\bt_ms=(\d+)", line)
        if m:
            clicks.append(int(m.group(1)))
            continue
        m = re.match(r"duration_s=(\d+)", line.strip())
        if m:
            duration_s.append(int(m.group(1)))
            continue
        m = re.search(r"journey_input mouse_presses_hw=(\d+) mouse_presses_seen=(\d+)", line)
        if m:
            hw, seen = int(m.group(1)), int(m.group(2))
    if len(duration_s) != 1:
        die("%s: expected one duration_s line, found %d" % (path, len(duration_s)))
    if boot_ms is None:
        die("%s: no journey kind=boot line (ags 0250)" % path)
    return sorted(clicks), duration_s[0], hw, seen, boot_ms


def pair(host, eng, off, tol):
    """Greedy one-to-one pairing of host times (s) with engine times (s) + off."""
    used, pairs = set(), []
    for i, h in enumerate(host):
        best, bj = None, None
        for j, e in enumerate(eng):
            if j in used:
                continue
            r = h - (e + off)
            if abs(r) <= tol and (best is None or abs(r) < abs(best)):
                best, bj = r, j
        if bj is not None:
            used.add(bj)
            pairs.append((i, bj, best))
    return pairs


def main(argv):
    ap = argparse.ArgumentParser(prog="drive-align.py")
    ap.add_argument("rdir", metavar="RESULTS_DIR")
    ap.add_argument("--tol-ms", type=int, default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    rdir, tol_ms, quiet = a.rdir, a.tol_ms, a.quiet

    dlog = os.path.join(rdir, "DRIVE-WALK.LOG")
    rlog = os.path.join(rdir, "RUNMANI.LOG")
    for p in (dlog, rlog):
        if not os.path.exists(p):
            die("missing " + p)
    hclicks, ms_res, lock_t, lock_end_t, failed = read_host(dlog)
    ems, duration_s, hw, seen, boot_ms = read_engine(rlog)
    if not hclicks or not ems:
        die("no clicks: host %d, engine %d" % (len(hclicks), len(ems)))
    if tol_ms is None:
        tol_ms = 600 if ms_res else 1500
    tol = tol_ms / 1000.0
    host = [t for _, t in hclicks]
    eng = [e / 1000.0 for e in ems]

    # Every host/engine pairing proposes an offset; keep the one pairing the most. A walker that clicks
    # at a fixed cadence makes this ambiguous: shifting by one period loses only an edge pair (C3512:
    # +76/+79/+82/+85 s all paired 32/32, the true offset +4.5 s; LAB-JOURNEYS 8.29). So the engine
    # start is bounded by the lock -- the game cannot start before run-hw takes it, and in rounds D-I
    # it started 2-13 s after -- and any other offset that pairs within one click of the best is
    # reported as an alias.
    lo = hi = None
    if lock_t is not None:
        lo, hi = lock_t - START_BEFORE_LOCK_S, lock_t + START_AFTER_LOCK_S
    cands = []
    for h in host:
        for e in eng:
            off = h - e
            if lo is not None and not (lo <= off <= hi):
                continue
            p = pair(host, eng, off, tol)
            cands.append(((len(p), -sum(abs(r) for _, _, r in p)), off, p))
    if not cands:
        die("no offset puts the engine start within [lock %+d s, lock %+d s]" % (-START_BEFORE_LOCK_S, START_AFTER_LOCK_S))
    cands.sort(key=lambda c: c[0], reverse=True)
    best = cands[0]
    near = sorted(c[1] for c in cands if c[0][0] >= best[0][0] - 1 and abs(c[1] - best[1]) > 2 * tol)
    aliases = []  # centres of clusters of near-best offsets (a regular walker aliases by whole periods)
    for o in near:
        if aliases and o - aliases[-1][-1] <= 1.0:
            aliases[-1].append(o)
        else:
            aliases.append([o])
    aliases = [statistics.median(c) - best[1] for c in aliases]
    _, off, p = best
    off += statistics.median([r for _, _, r in p])
    p = pair(host, eng, off, tol)
    resid = [r * 1000 for _, _, r in p]

    start = off
    boot_end = off + boot_ms / 1000.0
    end_lo = off + max(duration_s - 1, eng[-1])
    end_hi = off + duration_s + 1
    classes = {"before": [], "boot": [], "in": [], "edge": [], "after": []}
    per_click = []
    matched = {i for i, _, _ in p}
    for i, (n, h) in enumerate(hclicks):
        if h < start:
            c = "before"
        elif h < boot_end:
            c = "boot"
        elif end_lo < h <= end_hi:
            c = "edge"
        elif h <= end_lo:
            c = "in"
        else:
            c = "after"
        classes[c].append(n)
        per_click.append((n, h, c, i in matched))

    unmatched_in = [n for n, h, c, mt in per_click if c == "in" and not mt]
    out = []
    out.append("drive-align %s" % os.path.basename(os.path.normpath(rdir)))
    out.append("host clicks %d (stamps %s), engine clicks %d, mouse_presses_hw=%s mouse_presses_seen=%s duration_s=%d"
               % (len(host), "ms" if ms_res else "whole-second", len(eng), hw, seen, duration_s))
    out.append("offset: host = engine + %.3f s (%s); paired %d of %d engine clicks at tol %d ms; residual median %.0f ms, max |r| %.0f ms"
               % (off, s_to_hms(off), len(p), len(eng), tol_ms,
                  statistics.median(resid) if resid else 0, max(abs(r) for r in resid) if resid else 0))
    out.append("engine start %s; boot journey ends %s (%d ms)" % (s_to_hms(start), s_to_hms(boot_end), boot_ms))
    out.append("WINDOW-START %s (boot end: the first playable present)" % s_to_hms(boot_end))
    out.append("WINDOW-END   %s .. %s (quit: duration_s +/-1 s, not before the last engine click)" % (s_to_hms(end_lo), s_to_hms(end_hi)))
    if lock_t is not None:
        out.append("lock held    %s .. %s" % (s_to_hms(lock_t), s_to_hms(lock_end_t) if lock_end_t else "?"))
    out.append("host clicks: before %d, boot %d, in %d, edge %d, after %d"
               % tuple(len(classes[k]) for k in ("before", "boot", "in", "edge", "after")))
    out.append("in-window host clicks %d (+%d edge, %d boot) vs mouse_presses_hw %s; in-window host clicks with no engine click: %s"
               % (len(classes["in"]), len(classes["edge"]), len(classes["boot"]), hw, ",".join(map(str, unmatched_in)) or "none"))
    out.append("clicks whose press/release send failed (rc != 0): %s"
               % (",".join(map(str, failed)) if failed else ("none" if ms_res else "not logged (log predates rc_down/rc_up)")))
    if lo is not None:
        out.append("offset search: engine start bounded to lock %+d..%+d s" % (-START_BEFORE_LOCK_S, START_AFTER_LOCK_S))
    else:
        out.append("offset search: UNBOUNDED (no lock line in the log)")
    if aliases:
        out.append("WARNING: ALIAS -- %d other offset(s) in the window pair within one click of the best, at %s s "
                   "from it: a regular click cadence cannot pin the offset to less than a period, so clicks near "
                   "the window's edges may be classed one off. drive-walk logs with gap= (jittered) do not alias this way."
                   % (len(aliases), ", ".join("%+.1f" % a for a in aliases)))
    if len(p) < max(5, len(eng) // 2):
        out.append("WARNING: fewer than half the engine clicks paired -- the offset is not trustworthy")
    out.append("")
    for n, h, c, mt in per_click:
        out.append("click %3d %s %-6s %s" % (n, s_to_hms(h), c, "paired" if mt else "-"))
    text = "\n".join(out) + "\n"
    with open(os.path.join(rdir, "DRIVE-ALIGN.txt"), "w") as f:
        f.write(text)
    print(text if not quiet else "\n".join(l for l in out[:13] if l))


if __name__ == "__main__":
    main(sys.argv[1:])
