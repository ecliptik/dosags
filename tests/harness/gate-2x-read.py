#!/usr/bin/env python3
"""gate-2x-read.py OUT [--rows "LABEL ..."] -- the verdicts of tests/harness/gate-2x.sh (LAB 2x screen-equality gate;
registered in tests/harness/results/LAB2X-2026-11-19/PREREG-2X.md, sec. 4 + FIX-UP 1 + FIX-UP 2 + FIX-UP 3). Post-hoc: reads OUT/<row>/<arm>/
(frames/, RUNMANI.LOG, STDOUT.TXT, EXE-SHA256.txt, rc) and runs screen-equal.py on the registered pairs. Prints one line per
row and check, PASS / FAIL / VOID / MISSING / INFO, then a summary. Exit 0 = every registered check PASS; 1 = any FAIL,
VOID or MISSING in a registered check; 3 = otherwise, but a control without power (no C1 differing anywhere, a C2 not
differing in a row -- verdict NOPOWER -- or a V2 with vfy_bad = 0).

Registered checks (per row that ran):
  witness (every arm; VOID): rc 0; render dest as the row expects; frames_skipped 0 or -1 AND equal to the row's
      reference arm's (R; B where a row has no R; I0 on S16-1x) -- FIX-UP 2 (-1 is the engine's un-timestepped reading,
      game_run.cpp:1528-1546, the plain exe's too); the scale2 line present with on=1 in A F C1 C2 C2i V V2 I1 and absent
      in B R I0; the scale2 line's break= is 3 in C2 and V2, 1 in C2i, 0 in every other switch-on arm (FIX-UP 3);
      exe sha256 = the plain release for R, the same S2NR for every other arm;
      S32P rows: "DOS-PORT pack24 engaged" in every arm (in NO arm: the row is EXCEPTED, FIX-UP 1 F1.5; in some: VOID);
      CLK row: "tickclicks first=200 period=50 count=12" and 12 tickclick lines with the same (lc, x, y) in every arm.
  A==B, F==B, R==B (game rows), I1==I0 (S16-1x): screen-equal.py exit 0 (equal at every freeze, equal ticks, >= min pairs).
  A counters: narrow > 0 and latch_sets > 0 (else VOID: the path did not run). (rej fmt: information since FIX-UP 2.)
  V: vfy > 0 and vfy_bad = 0.     V2 (DOSAGS_SCALE2_BREAK=3 since FIX-UP 3): vfy_bad > 0 (power).
  C2 (DOSAGS_SCALE2_BREAK=3 since FIX-UP 3) vs B: DIFFERS at >= 1 comparable freeze in every row it runs, bench rows
      included, except B8-2x-full where it is information (FIX-UP 3 F3.3; power).   C1 vs B: DIFFERS in >= 1 row overall (power).
  I1 (S16-1x): narrow = full = fullfast = pal = rects = 0, latch_sets = 0, every rej but geom = 0, and
      rej geom = presents_real + presents_skipped (fps_basis).
Information (printed, not scored): narrow share of A's 2x presents, px_src/narrow, rects/narrow, skipcheck vs narrow,
V==B, C1==B, C2i==B (DOSAGS_SCALE2_BREAK=1, FIX-UP 2) and V2==B detail, F's counters, A's rej fmt.
"""
import argparse, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAIN_SHA256 = "c68241073cb0dbcc6f0870c22ba31a0d904dd2261e72a44fbb7ba75f6cfb7f43"
GAME_ROWS = ("S16-2x", "S32P-2x", "S8-2x", "CLK-2x")
DEST_2X = "render dest (0, 0, 639, 479 : 640 x 480)"
DEST_B2X = "render dest (0, 40, 639, 439 : 640 x 400)"
DEST_1X = "render dest (160, 120, 479, 359 : 320 x 240)"
SWITCH_ON = ("A", "F", "C1", "C2", "C2i", "V", "V2", "I1")
BREAK = {"C2": 3, "V2": 3, "C2i": 1}   # FIX-UP 3: the break= each switch-on arm must report (others 0)
MIN_PAIRS = {"CLK-2x": 10}
C2_INFO_ROWS = ("B8-2x-full",)   # FIX-UP 3 F3.3: 2 comparable freezes, 4 changing presents -- C2 power not predictable


def read(p):
    try:
        with open(p, "rb") as f:
            return f.read().decode("ascii", "replace")
    except OSError:
        return None


def scale2(text):
    """The scale2 exit line as a dict, or None."""
    if not text:
        return None
    m = None
    for m in re.finditer(r"DOS-PORT scale2 on=1 [^\n]*", text):
        pass
    if not m:
        return None
    line = m.group(0).replace("rej geom=", "rej_geom=").replace(" hint=", " rej_hint=").replace(" fmt=", " rej_fmt=")
    for k in ("nolatch", "noscene", "latched", "norects", "whole"):
        line = line.replace(" %s=" % k, " rej_%s=" % k)
    return {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", line)}


def field(text, name):
    m = re.search(r"\b%s=(-?\d+)" % name, text or "")
    return int(m.group(1)) if m else None


def expected_dest(row):
    if row == "S16-1x":
        return DEST_1X
    if row.startswith("B8-") or row.startswith("B16-"):
        return DEST_B2X
    return DEST_2X


def screen_equal(a, b, mn):
    """(rc, pairs, differs, text) of screen-equal.py A B."""
    r = subprocess.run([sys.executable, os.path.join(HERE, "screen-equal.py"), a, b, "--min", str(mn)],
                       capture_output=True, text=True)
    t = r.stdout + r.stderr
    m = re.search(r"screen-equal: (\d+) pair", t)
    return r.returncode, int(m.group(1)) if m else 0, len(re.findall(r"DIFFERS", t)), t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--rows", default="")
    a = ap.parse_args()
    want = a.rows.split()
    rows = sorted(d for d in os.listdir(a.out)
                  if os.path.isfile(os.path.join(a.out, d, "ROW.txt")) and (not want or d in want))
    fails = voids = missing = 0
    c1_power = False
    c2_rows_without = []
    v2_ok = True
    exe_shas = set()
    out = []

    def say(row, check, verdict, detail=""):
        nonlocal fails, voids, missing
        if verdict == "FAIL": fails += 1
        if verdict == "VOID": voids += 1
        if verdict == "MISSING": missing += 1
        out.append("%-14s %-22s %-7s %s" % (row, check, verdict, detail))

    for row in rows:
        rd = os.path.join(a.out, row)
        rowtxt = read(os.path.join(rd, "ROW.txt")) or ""
        arms = re.search(r"arms=(.*)", rowtxt).group(1).split()
        mn = MIN_PAIRS.get(row, 3 if row.startswith("B") else 5)
        if row.startswith("B8-2x-full"):
            mn = 2
        info = {}
        ok_arm = {}
        if row.startswith("S32P"):
            # FIX-UP 1 F1.5: the registered exception -- no arm engaged pack24 (DOSBox-X has no 640x480x24): the row is
            # VOID-EXCEPTED (it moves to the 486) and the gate is read without it. Any arm that did engage it: read as usual.
            sos = [read(os.path.join(rd, x, "STDOUT.TXT")) for x in arms]
            if any(s is not None for s in sos) and not any(s and "DOS-PORT pack24 engaged" in s for s in sos):
                out.append("%-14s %-22s %-7s %s" % (row, "row", "EXCEPTED", "pack24 not engaged in any arm: VOID, moves to the 486 (F1.5)"))
                continue
        # FIX-UP 2: the frames_skipped reference -- R, else B, else I0 (S16-1x)
        ref = "R" if "R" in arms else ("B" if "B" in arms else "I0")
        ref_fs = field(read(os.path.join(rd, ref, "RUNMANI.LOG")), "frames_skipped")
        for arm in arms:
            d = os.path.join(rd, arm)
            if not os.path.isdir(d):
                say(row, "witness " + arm, "MISSING", "not run")
                ok_arm[arm] = False
                continue
            rm, so = read(os.path.join(d, "RUNMANI.LOG")), read(os.path.join(d, "STDOUT.TXT"))
            sha = (read(os.path.join(d, "EXE-SHA256.txt")) or "").split()[:1]
            sha = sha[0] if sha else ""
            why = []
            if (read(os.path.join(d, "rc")) or "").strip() != "0": why.append("rc=%s" % (read(os.path.join(d, "rc")) or "?").strip())
            if rm is None: why.append("no RUNMANI.LOG")
            if so is None or expected_dest(row) not in so: why.append("render dest not %s" % expected_dest(row))
            _fs = field(rm, "frames_skipped")
            if _fs not in (0, -1) or ref_fs not in (0, -1) or _fs != ref_fs:   # FIX-UP 2
                why.append("frames_skipped=%s (reference %s reads %s)" % (_fs, ref, ref_fs))
            s2 = scale2(rm)
            if arm in SWITCH_ON and s2 is None: why.append("no scale2 line")
            if arm in SWITCH_ON and s2 is not None and s2.get("break") != BREAK.get(arm, 0):   # FIX-UP 3
                why.append("break=%s (registered %d)" % (s2.get("break"), BREAK.get(arm, 0)))
            if arm not in SWITCH_ON and rm is not None and "DOS-PORT scale2" in rm: why.append("scale2 line in a switch-off arm")
            if arm == "R":
                if sha != PLAIN_SHA256: why.append("R exe is not the plain release")
            else:
                exe_shas.add(sha)
                if sha == PLAIN_SHA256: why.append("exe is the plain release")
            if row.startswith("S32P") and (so is None or "DOS-PORT pack24 engaged" not in so):
                why.append("pack24 not engaged")
            if row == "CLK-2x":
                clicks = re.findall(r"DOS-PORT tickclick lc=(\d+) n=(\d+) x=(\d+) y=(\d+)", so or "")
                if "tickclicks first=200 period=50 count=12" not in (so or "") or len(clicks) != 12:
                    why.append("tickclicks %d/12" % len(clicks))
                info.setdefault("clicks", {})[arm] = clicks
            ok_arm[arm] = not why
            say(row, "witness " + arm, "PASS" if not why else "VOID", "; ".join(why))
            info[arm] = (s2, rm)
        if row == "CLK-2x" and len({tuple(v) for v in info.get("clicks", {}).values()}) > 1:
            say(row, "clicks equal", "VOID", "the arms' tickclick (lc, x, y) lists differ")

        def pair(x, y, check, must_equal=True, registered=True):
            if x not in arms or y not in arms:
                return None
            if not (ok_arm.get(x) and ok_arm.get(y)):
                if registered: say(row, check, "VOID" if (x in ok_arm and y in ok_arm) else "MISSING", "a witness failed")
                return None
            rc, n, dif, t = screen_equal(os.path.join(rd, x), os.path.join(rd, y), mn)
            with open(os.path.join(rd, "%s-vs-%s.txt" % (x, y)), "w") as f:
                f.write(t)
            void = "VOID" in t or n < mn
            if must_equal:
                v = "PASS" if rc == 0 else ("VOID" if void and dif == 0 else "FAIL")
            else:
                v = "PASS" if (dif > 0 and n >= mn) else ("VOID" if void else "NOPOWER")   # FIX-UP 2: a control's miss
            say(row, check, v if registered else "INFO", "%d pair(s), %d differ" % (n, dif))
            return v

        pair("A", "B", "A==B")
        pair("F", "B", "F==B")
        pair("R", "B", "R==B (identity)")
        pair("I1", "I0", "I1==I0 (1x inert)")
        pair("V", "B", "V==B", registered=False)
        v = pair("C1", "B", "C1 differs", must_equal=False, registered=False)
        if v == "PASS": c1_power = True
        _c2_reg = row not in C2_INFO_ROWS   # FIX-UP 3: registered in every row but B8-2x-full (F3.3)
        v = pair("C2", "B", "C2 differs", must_equal=False, registered=_c2_reg)
        if _c2_reg and "C2" in arms and v != "PASS": c2_rows_without.append(row)
        pair("C2i", "B", "C2i differs (break=1)", must_equal=False, registered=False)   # FIX-UP 2: information
        pair("V2", "B", "V2 vs B", must_equal=False, registered=False)

        s = info.get("A", (None, None))[0]
        if s is not None and ok_arm.get("A"):
            if s.get("narrow", 0) <= 0 or s.get("latch_sets", 0) <= 0:
                say(row, "A path ran", "VOID", "narrow=%s latch_sets=%s" % (s.get("narrow"), s.get("latch_sets")))
            else:
                say(row, "A path ran", "PASS", "narrow=%d latch_sets=%d" % (s["narrow"], s["latch_sets"]))
            say(row, "A rej fmt", "INFO", "rej fmt=%s (FIX-UP 2: information)" % s.get("rej_fmt"))
            tot = s.get("narrow", 0) + s.get("full", 0)
            say(row, "A narrow share", "INFO", "%.1f%% (narrow %d full %d pal %d) px_src/narrow %.0f rects/narrow %.2f"
                " skipcheck %d rej noscene %d latched %d norects %d whole %d nolatch %d drops %d" % (
                    100.0 * s.get("narrow", 0) / tot if tot else 0, s.get("narrow", 0), s.get("full", 0), s.get("pal", 0),
                    s.get("px_src", 0) / max(1, s.get("narrow", 0)), s.get("rects", 0) / max(1, s.get("narrow", 0)),
                    s.get("skipcheck", 0), s.get("rej_noscene", 0), s.get("rej_latched", 0), s.get("rej_norects", 0),
                    s.get("rej_whole", 0), s.get("rej_nolatch", 0), s.get("latch_drops", 0)))
        s = info.get("V", (None, None))[0]
        if s is not None and ok_arm.get("V"):
            good = s.get("vfy", 0) > 0 and s.get("vfy_bad", 1) == 0
            say(row, "V verifier clean", "PASS" if good else "FAIL",
                "vfy=%s vfy_bad=%s vfy_bad_px=%s" % (s.get("vfy"), s.get("vfy_bad"), s.get("vfy_bad_px")))
        s = info.get("V2", (None, None))[0]
        if s is not None and ok_arm.get("V2"):
            if s.get("vfy_bad", 0) <= 0: v2_ok = False
            say(row, "V2 verifier power", "PASS" if s.get("vfy_bad", 0) > 0 else "NOPOWER",
                "vfy=%s vfy_bad=%s break=%s" % (s.get("vfy"), s.get("vfy_bad"), s.get("break")))
        s = info.get("F", (None, None))[0]
        if s is not None and ok_arm.get("F"):
            say(row, "F counters", "INFO", "narrow=%s full=%s fullfast=%s rej hint=%s" % (
                s.get("narrow"), s.get("full"), s.get("fullfast"), s.get("rej_hint")))
        s, rm = info.get("I1", (None, None))
        if s is not None and ok_arm.get("I1"):
            pr, ps = field(rm, "presents_real"), field(rm, "presents_skipped")
            zero = all(s.get(k, -1) == 0 for k in ("narrow", "full", "fullfast", "pal", "rects", "latch_sets", "rej_hint",
                                                  "rej_fmt", "rej_nolatch", "rej_noscene", "rej_latched", "rej_norects",
                                                  "rej_whole"))
            geom = pr is not None and ps is not None and s.get("rej_geom") == pr + ps
            say(row, "I1 scale2 inert", "PASS" if zero and geom else "FAIL",
                "rej geom=%s presents_real+skipped=%s+%s, other fields zero=%s" % (s.get("rej_geom"), pr, ps, zero))

    if len(exe_shas) > 1:
        out.append("%-14s %-22s %-7s %s" % ("all", "one S2NR", "VOID", "S2NR arms ran %d different exes" % len(exe_shas)))
        voids += 1
    print("\n".join(out))
    power = []
    if not c1_power: power.append("no C1 differed from B in any row")
    if c2_rows_without: power.append("C2 did not differ in " + ",".join(c2_rows_without))
    if not v2_ok: power.append("a V2 read vfy_bad=0")
    print("gate-2x: %d FAIL, %d VOID, %d MISSING; controls: %s" % (fails, voids, missing, "; ".join(power) or "all have power"))
    if fails or voids or missing:
        return 1
    return 3 if power else 0


if __name__ == "__main__":
    sys.exit(main())
