#!/usr/bin/env python3
"""parse-results.py -- turn a staged run-dosbox.sh directory into one JSON
record and one templates/BENCHMARK.md-format record.

Usage:
    ./parse-results.py <staged-run-dir> [--out-dir DIR] [--tag TAG]
                        [--pkg PACKAGE] [--update-baseline]

Exits non-zero if any AUTOPILOT phase line reports status=fail, if the
expected phase sequence (boot..quit) never completed, or if a
screenshot's hash mismatches its committed expected/ baseline -- so
this script doubles as the harness's own pass/fail gate, not just a
report generator. See PLAN.md's "Test harness (AGS Quest)" section.

Screenshot regression: PH01/PH02/PH03.BMP (settle/room3,
interior/room4, gem-balcony/room3 -- see AutoPilot.asc's own inline
SaveScreenShot() calls) are hashed and compared against
expected/<pkg>/<environment>.json (environment read from RUNMANIFEST,
e.g. "dosbox-x"). A screenshot with no committed baseline yet is
reported as NEW, not a failure -- establishing a baseline is a
deliberate act (--update-baseline), done only after a human/agent has
actually looked at the image and confirmed it's correct. Images
themselves are NEVER committed (AGS Quest's own CC BY-NC-ND art) --
only the hash.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

EXPECTED_PHASES = [
    "boot", "splash", "menu", "intro", "settle", "key", "unlock",
    "enter", "interior", "anim", "save", "restore", "exit", "gem",
    "guimenu", "audio", "shots", "quit",
]

# Optional/fragile phases (PLAN.md's "Test harness (AGS Quest)" section) --
# shown in the rendered record when present, but never required and never
# gate pass/fail: a run predating slice 7, or one where this phase's own
# best-effort coordinate-based click missed, is still a normal PASS.
OPTIONAL_PHASES = ["dialog"]

SCREENSHOT_NAMES = ["PH01.BMP", "PH02.BMP", "PH03.BMP"]
HARNESS_DIR = Path(__file__).resolve().parent

AUTOPILOT_RE = re.compile(
    r"AUTOPILOT phase=(?P<phase>\S+) status=(?P<status>\S+) "
    r"tick=(?P<tick>\d+) room=(?P<room>\d+)"
)
RUNMANIFEST_RE = re.compile(r"^(?P<key>[a-zA-Z_][a-zA-Z0-9_]*)=(?P<value>.*)$")



def _clock_bracket_line(rm):
    """RTC-vs-engine-clock residual for this run, as a standing per-cell output.

    Reports the residual, not a ratio: the engine clock is anchored after
    init and stops before shutdown, so a few seconds of fixed overhead is
    EXPECTED and is not evidence of anything. What would be evidence is the
    residual growing with run length -- measured across 46 archived runs
    (37s to 281s) the rate error is -0.245%, 95% CI [-0.91%, +0.42%], and a
    direct RTC-vs-uclock probe on HW-486-66 read +0.059%. So flag only a
    residual far outside the established per-fixture range.
    """
    try:
        rtc = float(rm.get("duration_s"))
        eng = (float(rm.get("loop_ms")) + float(rm.get("preloop_ms"))) / 1000.0
    except (TypeError, ValueError):
        return "Clock bracket: NA (duration_s or loop_ms/preloop_ms missing)"
    resid = rtc - eng
    note = ""
    if rtc > 0 and (resid < 0 or resid > 0.25 * rtc + 12.0):
        note = "  <-- OUTSIDE the expected fixed-overhead range, investigate"
    return (f"Clock bracket: RTC {rtc:.0f}s vs engine {eng:.2f}s, "
            f"residual {resid:.2f}s (fixed init+shutdown, should NOT scale "
            f"with run length){note}")

def parse_phase_log(text):
    events = []
    for m in AUTOPILOT_RE.finditer(text):
        events.append({
            "phase": m.group("phase"),
            "status": m.group("status"),
            "tick": int(m.group("tick")),
            "room": int(m.group("room")),
        })
    return events


def parse_runmanifest(text):
    m = re.search(r"\[RUNMANIFEST-BEGIN\](.*?)\[RUNMANIFEST-END\]", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        fm = RUNMANIFEST_RE.match(line)
        if fm:
            fields[fm.group("key")] = fm.group("value")
    # The engine-clock side of the wall-clock bracket is emitted OUTSIDE the
    # RUNMANIFEST block, on the tick_rate_steady line, so it is not a
    # key=value field and was invisible to this parser. Lifted in here so
    # _clock_bracket_line has both halves -- the RTC half (duration_s) was
    # already a field, which is exactly why the two never got compared.
    tr = re.search(r"tick_rate_steady=.*?loop_ms=(\d+).*?preloop_ms=(\d+)", text)
    if tr:
        fields.setdefault("loop_ms", tr.group(1))
        fields.setdefault("preloop_ms", tr.group(2))
    return fields


def summarize_phases(events):
    # Last event per phase wins (a phase can log begin then ok/fail).
    by_phase = {}
    for e in events:
        by_phase[e["phase"]] = e
    return by_phase


def hash_screenshots(stage_dir):
    hashes = {}
    for name in SCREENSHOT_NAMES:
        p = stage_dir / name
        if p.is_file():
            hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()
        else:
            hashes[name] = None
    return hashes


def git_head_short():
    try:
        out = subprocess.run(
            ["git", "-C", str(HARNESS_DIR), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return None


def expected_path(pkg, environment):
    return HARNESS_DIR / "expected" / pkg / f"{environment}.json"


def load_expected(pkg, environment):
    p = expected_path(pkg, environment)
    if not p.is_file():
        return {}
    return json.loads(p.read_text())


def compare_screenshots(actual_hashes, expected_hashes):
    """Returns {name: {"actual": hash_or_None, "expected": hash_or_None, "status": ...}}.
    status is one of: missing (capture failed), new (no baseline yet),
    match, mismatch."""
    results = {}
    for name in SCREENSHOT_NAMES:
        actual = actual_hashes.get(name)
        expected = expected_hashes.get(name)
        if actual is None:
            status = "missing"
        elif expected is None:
            status = "new"
        elif actual == expected:
            status = "match"
        else:
            status = "mismatch"
        results[name] = {"actual": actual, "expected": expected, "status": status}
    return results


# Scripted fixtures that run ONE scene per run (tests/fixtures/bench/): the
# phase list depends on the scene, there is one capture (PH01.BMP), and the
# expected/<pkg>/<environment>.json baseline is keyed by arm first. Only
# used with --scene; without it everything above is AGS Quest's, unchanged.
SCENE_SUBPHASES = {"full": ["look", "pickup", "useinv", "gui", "save", "restore"]}


def scene_phases(arm):
    scene = re.sub(r"\d+$", "", arm)          # anim12 -> anim
    return ["boot"] + SCENE_SUBPHASES.get(scene, []) + [scene, "shot", "quit"]


sys.path.insert(0, str(Path(__file__).resolve().parent))


def read_present_verify(stage_dir):
    """The ags 0192 verifier's answer, from STDOUT.TXT, or None if the run did not carry it.

    Every other check in this file reads the engine's own RAM frame (a screenshot is
    virtualScreen), so none of them can see a region that changed in RAM and was never
    pushed to the screen -- a trail. This is the one that can: it shadows what was pushed and
    counts the pixels that differ. A run whose line says stale_frames > 0 FAILS, whatever its
    hashes say. Hardware cells do not carry it (it reads the surface twice per present); they
    carry the screen witness from run-hw.sh instead.
    """
    out = stage_dir / "STDOUT.TXT"
    if not out.exists():
        return None
    import re as _re
    last = None
    for line in out.read_text(errors="replace").replace("\r", "").splitlines():
        m = _re.search(r"DOS-PORT presentverify frames=(\d+) stale_frames=(\d+) stale_px=(\d+) stale_px_max=(\d+)", line)
        if m:
            last = {"frames": int(m.group(1)), "stale_frames": int(m.group(2)),
                    "stale_px": int(m.group(3)), "stale_px_max": int(m.group(4))}
    return last


def main():
    global EXPECTED_PHASES, OPTIONAL_PHASES, SCREENSHOT_NAMES
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scene", default=None,
                     help="Arm name of a one-scene-per-run fixture (e.g. walk, anim12 with --pkg bench8): "
                          "expects that scene's phases and PH01.BMP, baseline keyed by arm")
    ap.add_argument("stage_dir", type=Path)
    ap.add_argument("--out-dir", type=Path, default=None,
                     help="Where to write the JSON + .md records (default: the stage dir itself)")
    ap.add_argument("--tag", default=None,
                     help="Run identity tag for the output filenames (default: the stage dir's basename)")
    ap.add_argument("--pkg", default="agsquest",
                     help="Package name, for expected/<pkg>/<environment>.json (default: agsquest)")
    ap.add_argument("--update-baseline", action="store_true",
                     help="Write the current screenshot hashes as the new expected/ baseline. "
                          "Only after actually looking at the images and confirming they're correct.")
    args = ap.parse_args()
    if args.scene:
        EXPECTED_PHASES = scene_phases(args.scene)
        OPTIONAL_PHASES = []
        SCREENSHOT_NAMES = ["PH01.BMP"]

    stage_dir = args.stage_dir
    if not stage_dir.is_dir():
        print(f"parse-results.py: {stage_dir} is not a directory", file=sys.stderr)
        return 2

    autoplt_log = stage_dir / "AUTOPLT.LOG"
    stdout_txt = stage_dir / "STDOUT.TXT"
    runmani_log = stage_dir / "RUNMANI.LOG"
    if not runmani_log.is_file():
        # DOSAGS_LOG_TAG (patches/ags/0044) makes the engine write <TAG>.LOG
        # instead of the fixed RUNMANI.LOG name -- scan for whichever *.LOG
        # actually holds a RUNMANIFEST block rather than assuming the
        # untagged default name. First real-hardware run (2026-09-11) used
        # this path (HW1.LOG), which is what exposed the gap.
        for candidate in sorted(stage_dir.glob("*.LOG")):
            if candidate.name == "AUTOPLT.LOG":
                continue
            try:
                if "[RUNMANIFEST-BEGIN]" in candidate.read_text(errors="replace"):
                    runmani_log = candidate
                    break
            except OSError:
                continue

    # AUTOPLT.LOG is the authoritative source (written by the game itself
    # to $SAVEGAMEDIR$, independent of stdout capture); STDOUT.TXT is a
    # fallback if it's missing.
    if autoplt_log.is_file():
        phase_text = autoplt_log.read_text(errors="replace")
    elif stdout_txt.is_file():
        phase_text = stdout_txt.read_text(errors="replace")
    else:
        print(f"parse-results.py: neither AUTOPLT.LOG nor STDOUT.TXT found under {stage_dir}", file=sys.stderr)
        return 2

    events = parse_phase_log(phase_text)
    by_phase = summarize_phases(events)

    runmanifest = None
    if runmani_log.is_file():
        runmanifest = parse_runmanifest(runmani_log.read_text(errors="replace"))

    tag = args.tag or stage_dir.name
    out_dir = args.out_dir or stage_dir
    environment = (runmanifest or {}).get("environment", "unknown")

    failures = []
    missing = []
    for name in EXPECTED_PHASES:
        e = by_phase.get(name)
        if e is None:
            missing.append(name)
        elif e["status"] == "fail":
            failures.append(name)

    actual_hashes = hash_screenshots(stage_dir)
    expected_hashes = load_expected(args.pkg, environment)
    if args.scene:
        expected_hashes = expected_hashes.get(args.scene, {})
    shot_results = compare_screenshots(actual_hashes, expected_hashes)
    shot_mismatches = [n for n, r in shot_results.items() if r["status"] == "mismatch"]
    shot_capture_missing = [n for n, r in shot_results.items() if r["status"] == "missing"]
    shot_new = [n for n, r in shot_results.items() if r["status"] == "new"]

    if args.update_baseline:
        ep = expected_path(args.pkg, environment)
        ep.parent.mkdir(parents=True, exist_ok=True)
        baseline = {n: h for n, h in actual_hashes.items() if h is not None}
        if args.scene:
            merged = load_expected(args.pkg, environment)
            merged[args.scene] = baseline
            baseline = dict(sorted(merged.items()))
        ep.write_text(json.dumps(baseline, indent=2) + "\n")
        print(f"parse-results.py: wrote baseline {ep} ({len(baseline)} screenshot(s))")

    present_verify = read_present_verify(stage_dir)
    import witness_check as _wc
    witness = _wc.check(str(stage_dir))   # None for DOSBox-X runs and pre-standing-order cells
    record = {
        "tag": tag,
        "stage_dir": str(stage_dir),
        "commit": git_head_short(),
        "phases": by_phase,
        "expected_phases": EXPECTED_PHASES,
        "optional_phases": OPTIONAL_PHASES,
        "missing_phases": missing,
        "failed_phases": failures,
        "environment": environment,
        "screenshots": shot_results,
        "screenshot_mismatches": shot_mismatches,
        "screenshot_capture_missing": shot_capture_missing,
        "screenshot_new": shot_new,
        "present_verify": present_verify,
        "witness": witness,
        "pass": (not missing and not failures and not shot_mismatches and not shot_capture_missing
                 and not (present_verify and present_verify["stale_frames"] > 0)
                 and not (witness is not None and not witness["ok"])),
        "runmanifest": runmanifest,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{tag}.json"
    json_path.write_text(json.dumps(record, indent=2) + "\n")

    md_path = out_dir / f"{tag}.md"
    md_path.write_text(render_benchmark_md(record))

    print(f"parse-results.py: wrote {json_path}")
    print(f"parse-results.py: wrote {md_path}")

    if shot_new:
        print(f"parse-results.py: NOTE -- no committed baseline yet for {shot_new} "
              f"(look at the image, then rerun with --update-baseline once confirmed correct)", file=sys.stderr)

    if not record["pass"]:
        print(f"parse-results.py: FAIL -- missing={missing} failed={failures} "
              f"screenshot_mismatches={shot_mismatches} screenshot_capture_missing={shot_capture_missing}"
              + (f" WITNESS: {witness['detail']}" if witness is not None and not witness["ok"] else "")
              + (f" present_verify_stale_frames={present_verify['stale_frames']}/{present_verify['frames']}"
                 f" stale_px={present_verify['stale_px']}"
                 if present_verify and present_verify["stale_frames"] > 0 else ""),
              file=sys.stderr)
        return 1

    print("parse-results.py: PASS -- all phases ok")
    return 0


def render_benchmark_md(record):
    rm = record["runmanifest"] or {}
    environment = record.get("environment", "unknown")
    is_real_hw = environment not in ("dosbox-x", "86box", "unknown")
    hardware_id_line = (
        "Hardware ID: (fill in the vcctrl machine/tag this ran against)"
        if is_real_hw else
        f"Hardware ID: {environment} (correctness gate, not a performance number)")
    lines = [
        "# Benchmark",
        "",
        "## Hardware",
        "CPU:",
        "Clock:",
        "L1:",
        "L2:",
        "RAM:",
        "Video:",
        "Sound:",
        "MIDI:",
        "DOS:",
        "VESA:",
        "",
        hardware_id_line,
        "",
        "## Build",
        f"Commit: {record.get('commit') or 'NA'}",
        f"Upstream revision: (see tests/harness/packages/agsquest/PIN)",
        f"binary_sha12: {rm.get('binary_sha12', 'NA')}",
        f"env_block_sha: {rm.get('env_block_sha', 'NA')}",
        "",
        "## Scene",
        "Game: AGS Quest (adventuregamestudio/ags-demo-game, local-testing-only, see LICENSE-NOTES.md)",
        "Level/room: full phase sequence, boot..quit",
        f"Duration: {rm.get('duration_s', 'NA')}s",
        # The independent wall-clock bracket the hub's dos-hardware-validation
        # standard asks for, printed on EVERY cell rather than when someone
        # thinks to look. duration_s comes from time(), which on DJGPP reads
        # the CMOS RTC -- a separate crystal from the PIT that backs uclock()
        # and therefore every tick_rate figure. It was present in all 46
        # archived manifests and unread until the clock came under suspicion
        # at hour twenty-four; a self-reported clock fails in the flattering
        # direction, so this has to be automatic, not remembered.
        _clock_bracket_line(rm),
        "",
        "## Results",
        "",
        "| phase | status | tick | room |",
        "|---|---|---|---|",
    ]
    for name in record["expected_phases"]:
        e = record["phases"].get(name)
        if e is None:
            lines.append(f"| {name} | MISSING | - | - |")
        else:
            lines.append(f"| {name} | {e['status']} | {e['tick']} | {e['room']} |")
    for name in record.get("optional_phases", []):
        e = record["phases"].get(name)
        if e is not None:
            lines.append(f"| {name} (optional) | {e['status']} | {e['tick']} | {e['room']} |")
    lines += [
        "",
        "### Screenshots (hash regression, environment: " + record.get("environment", "unknown") + ")",
        "",
        "| file | status | sha256 |",
        "|---|---|---|",
    ]
    for name in SCREENSHOT_NAMES:
        r = record["screenshots"].get(name, {})
        h = r.get("actual") or "NA"
        lines.append(f"| {name} | {r.get('status', 'NA')} | `{h}` |")
    lines += [
        "",
        f"Overall: {'PASS' if record['pass'] else 'FAIL'}",
        "",
        "## Measurement method",
        (f"Real hardware (vcctrl), environment={environment} -- this fps/timing datum "
         "IS a real performance number, unlike a dosbox-x/86box run. Pair any fps claim "
         "with an independently-derived wall-clock bracket per "
         ".sdl-dos-ports/shared/skills/dos-hardware-validation."
         if is_real_hw else
         f"{environment} automation gate (correctness only) -- not real hardware, not a "
         "performance datum. See PLAN.md's \"Test harness (AGS Quest)\" Milestone mapping "
         "for what each rung needs beyond this."),
        "",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
