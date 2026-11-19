#!/usr/bin/env bash
# drive6-gate.sh -- the round driver's decision after a DRIVE 6 cell, from its game log (DRIVE6-RIG-CHECKS.md).
#
#   tests/harness/drive6-gate.sh <cell-results-dir> [--no-recentre]   after the calibration cell (DRIVE6_MODE=cal)
#   tests/harness/drive6-gate.sh --play <cell-results-dir>             after an MS3 play cell (DRIVE6_MODE=ms)
#
# Reads <dir>/STDOUT.TXT and <dir>/DRIVE-WALK.LOG with drive6-cal.py and prints EXACTLY ONE decision line on stdout.
# FIRST, before any other check: a short run -- DRIVE-WALK.LOG's "done: N presses" below the planned count in its
# header line (or no done line) -- is "GATE STOP presses sent N < planned M" (cal) / "GATE PLAY-VOID ..." (play);
# then a failed press (a one-call press's non-zero exit or step not ok; a split press's non-zero rc) is the same.
#   calibration:
#     GATE PASS DRIVE6_DY=.. DRIVE6_DXL=.. DRIVE6_DXA=.. DRIVE6_DXB=..       exit 0: RESULT PASS; use these values
#     GATE RECENTRE DRIVE6_DY=.. DRIVE6_DXL=.. DRIVE6_DXA=.. DRIVE6_DXB=..   exit 3: re-run the cal cell ONCE with
#         these as centres. Given only when every failure is C4-C7 for a value that the fitted line says hits its band
#         but that lies outside the swept range (an extrapolation), and C1 (presses walk, rooms), C2 / C3 (corners),
#         C8 (repeats and linearity within 2 px) and C9 (slope as the model) all pass. The values are the fitted ones.
#         With --no-recentre (the re-run) this case is a STOP instead.
#     GATE STOP <reason>                                                       exit 1: anything else, UNREADABLE
#         included; no MS3 cell in this power-on
#   recheck (--recheck REF_CAL_DIR, after a DRIVE6_MODE=calq cell; REF_CAL_DIR is the last full calibration that PASSes
#   under the current rules, e.g. round RI's RICAL):
#     GATE PASS DRIVE6_DY=.. DRIVE6_DXL=.. DRIVE6_DXA=.. DRIVE6_DXB=..       exit 0: every press inside MS3's landing bands
#         at the reference's values (the same meaning for MS3 as a full-cal PASS); then ' drift: DXL 57 (ref 60, -3 px)
#         / DXA .. / DXB .. / y ..', each quantity's worst point against the reference's own measurement (information)
#     GATE PASS <env> NEXT-FULL-CAL drift: ..                                  exit 0: as PASS, with a point more than 6 px
#         from the reference: the values serve this power-on, the NEXT power-on runs the full calibration (no calq)
#     GATE STOP recheck: <first miss> (run the full calibration)             exit 1
#   play:
#     GATE PLAY-OK                                                             exit 0
#     GATE PLAY-VOID <reason>                                                  exit 1: drive6-cal.py --play failed
#         (pointing bands, walks == presses, rooms exactly [1, 2]) or the files are unreadable
# Also written to the cell dir: CAL-RESULT.txt (cal) or PLAY-RESULT.txt (play), the parser's full output; GATE.txt, the
# decision line. Nothing here touches the rig.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAY=0; NORE=0; DIR=""; RECHECK=""
while (( $# )); do
    case $1 in
        --play) PLAY=1;;
        --no-recentre) NORE=1;;
        --recheck) RECHECK=${2:-}; shift;;
        -*) echo "GATE STOP usage: unknown option $1"; exit 1;;
        *) DIR=$1;;
    esac
    shift
done
decide() {  # LINE CODE: print, record, exit
    echo "$1"
    [[ -n "$DIR" && -d "$DIR" ]] && echo "$1" > "$DIR/GATE.txt"
    exit "$2"
}
if [[ -z "$DIR" || ! -d "$DIR" ]]; then
    (( PLAY )) && decide "GATE PLAY-VOID UNREADABLE: no cell dir [$DIR]" 1
    decide "GATE STOP UNREADABLE: no cell dir [$DIR]" 1
fi
for f in STDOUT.TXT DRIVE-WALK.LOG; do
    if [[ ! -s "$DIR/$f" ]]; then
        (( PLAY )) && decide "GATE PLAY-VOID UNREADABLE: $f missing or empty" 1
        decide "GATE STOP UNREADABLE: $f missing or empty" 1
    fi
done

# A short run first, ahead of any other check (sdlports, after round RH's 1-of-40 cal cell): DRIVE-WALK.LOG's first
# line names the planned count ("..., N presses ..."), its last "done: M presses" the count sent.
short="$(python3 - "$DIR/DRIVE-WALK.LOG" <<'PY'
import re, sys
t = open(sys.argv[1], errors='replace').read()
m = re.search(r'(\d+) presses', t.splitlines()[0]) if t.strip() else None
d = re.findall(r'done: (\d+) presses', t)
if not m:
    print('no planned press count in the log header')
elif not d:
    print('no "done: N presses" line: the driver did not finish (planned %s)' % m.group(1))
elif int(d[-1]) < int(m.group(1)):
    print('presses sent %s < planned %s' % (d[-1], m.group(1)))
else:
    # a failed press: a one-call press with a non-zero exit or a step not ok (failed_at=...), or a split press with
    # any non-zero rc_ (D4)
    bad = [l for l in t.splitlines() if ' click ' in l and (re.search(r'rc_press=[1-9]|ok=0', l) or
                                                         re.search(r'rc_(?:home|x|y|down|up)=[1-9]', l))]
    if bad:
        f = re.search(r'click (\d+)\s+(\S+)', bad[0]); fa = re.search(r'failed_at=(\S+)', bad[0])
        rc = re.findall(r'rc_\w+=[1-9]\d*', bad[0])
        print('%d failed press(es), first: click %s %s (%s)' % (len(bad), f.group(1), f.group(2),
              ('failed_at=' + fa.group(1)) if fa and fa.group(1) != '-' else ' '.join(rc)))
PY
)"
if [[ -n "$short" ]]; then
    (( PLAY )) && decide "GATE PLAY-VOID $short" 1
    decide "GATE STOP $short" 1
fi

if [[ -n $RECHECK ]]; then
    [[ -s $RECHECK/STDOUT.TXT && -s $RECHECK/DRIVE-WALK.LOG ]] || decide "GATE STOP UNREADABLE: no reference cal at [$RECHECK]" 1
    python3 "$HERE/drive6-cal.py" --recheck "$DIR/STDOUT.TXT" "$DIR/DRIVE-WALK.LOG" "$RECHECK" --json > "$DIR/RECHECK-RESULT.txt" 2>&1
    rc=$?
    line="$(python3 - "$DIR/RECHECK-RESULT.txt" "$rc" <<'PY'
import json, sys
lines = open(sys.argv[1], errors='replace').read().splitlines()
try:
    d = json.loads(lines[-1])
except Exception:
    print('GATE STOP UNREADABLE: %s' % ((lines[-1] if lines else 'no recheck output')[:120])); sys.exit()
e = d.get('env', {})
if d.get('pass') and sys.argv[2] == '0':
    print('GATE PASS ' + ' '.join('%s=%s' % (k, e.get(k)) for k in ('DRIVE6_DY', 'DRIVE6_DXL', 'DRIVE6_DXA', 'DRIVE6_DXB'))
          + (' NEXT-FULL-CAL' if d.get('next_full_cal') else '') + ' drift: %s' % (d.get('drift') or 'none'))
else:
    print('GATE STOP recheck: %s (run the full calibration)' % ((d.get('fails') or ['?'])[0][:160]))
PY
)"
    case $line in "GATE PASS "*) decide "$line" 0;; *) decide "$line" 1;; esac
fi

if (( PLAY )); then
    python3 "$HERE/drive6-cal.py" --play "$DIR/STDOUT.TXT" "$DIR/DRIVE-WALK.LOG" --json > "$DIR/PLAY-RESULT.txt" 2>&1
    rc=$?
    if (( rc == 0 )); then decide "GATE PLAY-OK" 0; fi
    why="$(python3 - "$DIR/PLAY-RESULT.txt" <<'PY'
import json, sys
lines = open(sys.argv[1], errors='replace').read().splitlines()
try:
    d = json.loads(lines[-1])
    f = d.get('fails') or ['RESULT FAIL']
    print('%s%s' % (f[0], ' (+%d more)' % (len(f) - 1) if len(f) > 1 else ''))
except Exception:
    print('UNREADABLE: ' + (lines[-1] if lines else 'no parser output'))
PY
)"
    decide "GATE PLAY-VOID $why" 1
fi

python3 "$HERE/drive6-cal.py" "$DIR/STDOUT.TXT" "$DIR/DRIVE-WALK.LOG" --json > "$DIR/CAL-RESULT.txt" 2>&1
rc=$?
line="$(python3 - "$DIR/CAL-RESULT.txt" "$rc" "$NORE" <<'PY'
import json, sys
path, rc, nore = sys.argv[1], int(sys.argv[2]), sys.argv[3] == '1'
lines = open(path, errors='replace').read().splitlines()
ORDER = ('DRIVE6_DY', 'DRIVE6_DXL', 'DRIVE6_DXA', 'DRIVE6_DXB')
try:
    d = json.loads(lines[-1])
except Exception:
    print('GATE STOP UNREADABLE: %s' % ((lines[-1] if lines else 'no parser output')[:120])); sys.exit()
if rc not in (0, 1):
    print('GATE STOP UNREADABLE: parser exit %d' % rc); sys.exit()
env = d.get('env', {})
if d.get('pass') and rc == 0 and all(k in env for k in ORDER):
    print('GATE PASS ' + ' '.join('%s=%s' % (k, env[k]) for k in ORDER)); sys.exit()
ch = d.get('checks', {})
hard = [c for c in ('C1', 'C2', 'C3', 'C10', 'C9', 'C8') if ch.get(c)]
if hard:
    print('GATE STOP %s: %s' % (hard[0], ch[hard[0]][0][:160])); sys.exit()
q = d.get('quantities', {})
if len(q) < 4 or not all(k in env for k in ORDER):
    print('GATE STOP a quantity has no reading: %s' % sorted(set(ORDER) - set(env))); sys.exit()
soft = [k for k in q if not (q[k]['in_band'] and q[k]['in_range'])]
for k in soft:
    if not q[k]['in_band']:
        print('GATE STOP %s=%s lands at %s, outside its band' % (q[k]['env'], q[k]['chosen'], q[k]['predicted'])); sys.exit()
if not soft:
    print('GATE STOP RESULT FAIL with no check filed: %s' % (d.get('fails') or ['?'])[0][:120]); sys.exit()
if nore:
    print('GATE STOP still extrapolated after the re-run: %s' % ', '.join(
        '%s=%s (swept %s..%s)' % (q[k]['env'], q[k]['chosen'], q[k]['swept'][0], q[k]['swept'][1]) for k in soft)); sys.exit()
print('GATE RECENTRE ' + ' '.join('%s=%s' % (k, env[k]) for k in ORDER))
PY
)"
[[ -n "$line" ]] || line="GATE STOP UNREADABLE: no decision"
case $line in
    "GATE PASS "*) decide "$line" 0;;
    "GATE RECENTRE "*) decide "$line" 3;;
    *) decide "$line" 1;;
esac
