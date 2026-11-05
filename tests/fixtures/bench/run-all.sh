#!/usr/bin/env bash
# run-all.sh -- run every BENCH arm (cfg/<arm>.cfg) once under DOSBox-X and
# check each against tests/harness/expected/bench<depth>/dosbox-x.json
# (keyed by arm, then capture name). Covers the arms the manifest gates
# plus `audio` (sound on), which the manifest leaves out. License: MIT.
#
# Usage: run-all.sh [--depth 8|16|32] [--update]
#   --update  write the hashes this run produced as the new baseline.
#             Only after LOOKING at the captures (this repo's own rule: a
#             baseline once enshrined boxed sprites because nobody did).
# Exit 0 only if every scene logged its own ok, its shot ok, quit with
# exit_code=0 / critical_count=0 / warn_count=0, and matched its hash.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
DEPTH=8; HOLD=1000; UPDATE=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --depth) DEPTH="$2"; shift 2 ;;
        --hold-ticks) HOLD="$2"; shift 2 ;;
        --update) UPDATE=1; shift ;;
        *) echo "run-all.sh: unknown arg $1" >&2; exit 1 ;;
    esac
done
EXP="$REPO/tests/harness/expected/bench$DEPTH/dosbox-x.json"
OUTDIR="$REPO/build/bench-work/run-all-$DEPTH"
rm -rf "$OUTDIR"; mkdir -p "$OUTDIR"
FAIL=0
for scene in idle walk anim4 anim12 text gui audio full; do
    SND=(); [[ "$scene" == audio ]] && SND=(--sound)
    "$HERE/run-scene.sh" "$scene" --depth "$DEPTH" --cfg "$HERE/cfg/$scene.cfg" "${SND[@]}" > "$OUTDIR/$scene.log" 2>&1 || true
    D="$(tail -1 "$OUTDIR/$scene.log")"
    python3 - "$scene" "$D" "$EXP" "$OUTDIR" <<'PY' || FAIL=1
import glob, hashlib, json, os, re, sys
scene, d, exp_path, outdir = sys.argv[1:5]
def rd(p):
    try: return open(p, errors="replace").read()
    except OSError: return ""
auto, mani = rd(os.path.join(d, "AUTOPLT.LOG")), rd(os.path.join(d, "RUNMANI.LOG"))
problems = []
if not re.search(r"phase=%s status=ok" % re.sub(r"\d+$", "", scene), auto): problems.append("scene not ok")
if "phase=shot status=ok" not in auto: problems.append("no shot")
if re.search(r"status=fail", auto): problems.append("a phase failed")
for k in ("exit_code=0", "critical_count=0", "warn_count=0"):
    if k not in mani: problems.append("RUNMANIFEST lacks " + k)
shots = sorted(glob.glob(os.path.join(d, "PH*.BMP")))
got = {os.path.basename(s): hashlib.sha256(open(s, "rb").read()).hexdigest() for s in shots}
if list(got) != ["PH01.BMP"]: problems.append("expected exactly PH01.BMP, got %s" % sorted(got))
json.dump({scene: got}, open(os.path.join(outdir, scene + ".hash.json"), "w"))
# baseline file is keyed by scene, then by capture name
exp = (json.load(open(exp_path)) if os.path.exists(exp_path) else {}).get(scene, {})
for name, h in got.items():
    if name not in exp: problems.append("%s: no baseline" % name)
    elif exp[name] != h: problems.append("%s: hash differs from baseline" % name)
m = re.search(r"tick_rate_steady=([\d.]+)", mani)
p = re.search(r"presents_real=(\d+) presents_skipped=(\d+)", mani)
print("%-6s %s  tick_rate_steady=%s presents real/skipped=%s  %s" % (
    scene, "PASS" if not problems else "FAIL", m.group(1) if m else "?",
    "/".join(p.groups()) if p else "?", "; ".join(problems)))
sys.exit(1 if problems else 0)
PY
done
if [[ $UPDATE -eq 1 ]]; then
    mkdir -p "$(dirname "$EXP")"
    python3 - "$OUTDIR" "$EXP" <<'PY'
import glob, json, sys
out = {}
for f in sorted(glob.glob(sys.argv[1] + "/*.hash.json")):
    out.update(json.load(open(f)))
json.dump(dict(sorted(out.items())), open(sys.argv[2], "w"), indent=2)
open(sys.argv[2], "a").write("\n")
print("run-all.sh: baseline written:", sys.argv[2])
PY
    exit 0
fi
exit $FAIL
