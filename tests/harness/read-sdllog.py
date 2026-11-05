#!/usr/bin/env python3
"""read-sdllog.py -- read the SDL3-DOS backend's own flush trace.

    ./read-sdllog.py results/FPT1-2026-09-20/FPT1SDL.LOG

The backend writes LOGS\\<TAG[0:5]>SDL.LOG on every run (dos_port_dbg_log is
unconditional -- no hint gates it). Until 2026-09-20 run-hw.sh never fetched
it, so this trace exists for every cell of the campaign and has been read for
none of them.

What it carries that nothing else does is the four-phase bracket around the
present's fast path, reported every 100 flushes with a MAX as well as a mean:

    t0  entry
    t1  after the lazy-reinit / DPMI block   -> dpmi
    t2  after the system-RAM -> VRAM copy    -> copy
    t3  exit                                 -> post

The mean is not the interesting number. The phenomenon this was fetched for
is a ~250 ms outlier roughly every 20 s against a present whose ordinary
share of the frame is 4.9%, so it lives entirely in the max columns: one
block out of eighty carries it and the other seventy-nine dilute it away.
This prints the max columns first for that reason, and calls out any block
whose total_max clears a threshold.

It also reports what the brackets CANNOT see, which is the point that
decides the case if no block clears the threshold:

  * A surface rebuild happens in DOSVESA_CreateWindowFramebuffer, a
    different function -- count fb_created on the engine's flushpath line
    instead.
  * dos_port_dbg_log's own fprintf + fflush + fsync runs AFTER t3 is taken,
    so the cost of writing these very lines is outside every bracket they
    report.
"""
import re
import sys

BLOCK = re.compile(
    r"fastpath-timing block @flush=(\d+): "
    r"dpmi_ms_avg=(\d+)\.(\d+) \(min=(\d+)\.(\d+) max=(\d+)\.(\d+)\) "
    r"copy_ms_avg=(\d+)\.(\d+) \(min=(\d+)\.(\d+) max=(\d+)\.(\d+)\) "
    r"post_ms_avg=(\d+)\.(\d+) \(min=(\d+)\.(\d+) max=(\d+)\.(\d+)\) "
    r"total_ms_avg=(\d+)\.(\d+) \(min=(\d+)\.(\d+) max=(\d+)\.(\d+)\) "
    r"\[over (\d+) flushes\]"
)
LIFECYCLE = re.compile(r"\[lifecycle\] UpdateWindowFramebuffer #(\d+):")

# A block whose total_max clears this is reported individually. 200 ms is
# chosen against the phenomenon (~250 ms), not against the noise.
STALL_MS = 200.0


def ms(whole, frac):
    return float(whole) + float(frac) / 1000.0


def main(path):
    try:
        with open(path, "r", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as exc:
        print("read-sdllog.py: cannot read %s: %s" % (path, exc))
        return 2

    blocks = []
    for line in lines:
        m = BLOCK.search(line)
        if m:
            g = m.groups()
            blocks.append({
                "flush": int(g[0]),
                "dpmi_avg": ms(g[1], g[2]),
                "dpmi_max": ms(g[5], g[6]),
                "copy_avg": ms(g[7], g[8]),
                "copy_max": ms(g[11], g[12]),
                "post_avg": ms(g[13], g[14]),
                "post_max": ms(g[17], g[18]),
                "total_avg": ms(g[19], g[20]),
                "total_max": ms(g[23], g[24]),
                "n": int(g[25]),
            })

    lc = [int(m.group(1)) for m in (LIFECYCLE.search(l) for l in lines) if m]

    print("%s: %d lines" % (path, len(lines)))
    if lc:
        print("  [lifecycle] UpdateWindowFramebuffer seen at calls %s"
              % ", ".join("#%d" % n for n in lc[:6])
              + (" ..." if len(lc) > 6 else ""))
    else:
        print("  NO [lifecycle] UpdateWindowFramebuffer line at all -- the")
        print("  flush was never called, and nothing below says anything")
        print("  about the present. Stop here.")

    if not blocks:
        print("  NO fastpath-timing block. Either the fast-path branch was")
        print("  not entered, or fewer than 100 flushes happened. This is")
        print("  UNSCORED, not 'the brackets were small'.")
        return 1

    covered = sum(b["n"] for b in blocks)
    print("  %d blocks covering %d flushes" % (len(blocks), covered))
    print()

    worst = max(blocks, key=lambda b: b["total_max"])
    print("  worst block by total_max: @flush=%d" % worst["flush"])
    print("    dpmi_max=%.3f ms  copy_max=%.3f ms  post_max=%.3f ms"
          % (worst["dpmi_max"], worst["copy_max"], worst["post_max"]))
    print("    total_max=%.3f ms" % worst["total_max"])
    named = max(("dpmi", worst["dpmi_max"]),
                ("copy", worst["copy_max"]),
                ("post", worst["post_max"]), key=lambda kv: kv[1])
    unexplained = worst["total_max"] - (worst["dpmi_max"] + worst["copy_max"]
                                        + worst["post_max"])
    print("    largest phase: %s (%.3f ms)" % named)
    if abs(unexplained) > 1.0:
        print("    NOTE: the three phase maxima need not come from the same")
        print("    flush as total_max, so %+.3f ms of 'unexplained' here is"
              % unexplained)
        print("    an artifact of per-bracket maxima, not a missing term.")
    print()

    over = [b for b in blocks if b["total_max"] >= STALL_MS]
    if over:
        print("  %d block(s) with total_max >= %.0f ms:" % (len(over), STALL_MS))
        for b in over:
            print("    @flush=%-6d total_max=%8.3f  dpmi_max=%7.3f "
                  "copy_max=%7.3f post_max=%7.3f"
                  % (b["flush"], b["total_max"], b["dpmi_max"],
                     b["copy_max"], b["post_max"]))
        print()
        print("  -> P-B holds: the stall is INSIDE t0..t3.")
    else:
        hi = worst["total_max"]
        print("  No block reaches %.0f ms (highest total_max = %.3f ms)."
              % (STALL_MS, hi))
        print("  -> P-B falsified. If the tick trace still shows ~250 ms")
        print("     present stalls in this same run, the stall is OUTSIDE")
        print("     t0..t3 -- the un-bracketed tail, which is")
        print("     dos_port_dbg_log's own fprintf+fflush+fsync and")
        print("     SDL_video.c's prologue. Confirm against the run's")
        print("     'DOS-PORT tick_stall' lines before concluding anything:")
        print("     no stalls in this run means UNSCORED, not falsified.")
    print()

    mean_total = sum(b["total_avg"] for b in blocks) / len(blocks)
    mean_dpmi = sum(b["dpmi_avg"] for b in blocks) / len(blocks)
    mean_copy = sum(b["copy_avg"] for b in blocks) / len(blocks)
    mean_post = sum(b["post_avg"] for b in blocks) / len(blocks)
    print("  steady state (mean of block means, %d flushes):" % covered)
    print("    dpmi=%.3f ms  copy=%.3f ms  post=%.3f ms  total=%.3f ms"
          % (mean_dpmi, mean_copy, mean_post, mean_total))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
