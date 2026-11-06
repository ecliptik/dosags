#!/usr/bin/env bash
# 8.3 cell wrapper: sampler + recorder + optional drive-start + run-hw.sh; collect into results/.
# round V1 copy of roundN7/cellN7.sh; round N7 copy of roundL5/cellL5.sh; round L copy of roundK/cellK.sh (+ snapshots.py at lock-take/release; input-log window to release + 1.5 s with mouse.dropped rows); round K copy of roundJ/cellJ.sh (input-log -> INPUT-LOG.jsonl by lock pair, VOID on failure); round J copy of roundH/cellH.sh; round H copy of roundD/cellD.sh (results dir dated by CELL_DATE, default 2026-09-25; DRIVE 4 added).
# usage: cellH.sh TAG PKG DRIVE(0/1) EXE [run-hw args...]  (round B, 2026-09-24; DRIVE 2 = drive-walk.sh TAG 25 2 90)
set -u
TAG=$1 PKG=$2 DRIVE=$3 EXE=$4; shift 4
REPO=~/git/dosags; H=$REPO/tests/harness; R=$H/results/$TAG-${CELL_DATE:?CELL_DATE unset}
mkdir -p "$R"; cd "$R"
sha256sum "$EXE" | tee PRE-STAGE-SHA256.txt
$H/audio-sampler.sh "$R/LEVEL.log" & SAMP=$!
python3 $H/audio-rec.py "$R/$TAG" 3600 > "$R/audio-rec.out" 2>&1 & REC=$!
# round H (lab-journeys' hardware click rule): no clicks during boot -- drive-walk waits 60 s after the lock
# (boot ended <= ~40 s after the lock in rounds D-G), then clicks every 2 s until the lock is released.
# round Q copy of roundL/cellL.sh: + DRIVE 5 = LAB-MMD 50.4 PLAY486 clicks (held clicks 8 s apart after a 40 s warm-up)
if [[ "$DRIVE" == 5 ]]; then DRIVE_LOG="$R/DRIVE-WALK.LOG" $H/drive-walk.sh "$TAG" 40 8 30 > /dev/null 2>&1 & DRV=$!; fi
if [[ "$DRIVE" == 4 ]]; then DRIVE_LOG="$R/DRIVE-WALK.LOG" $H/drive-walk.sh "$TAG" 60 2 80 > /dev/null 2>&1 & DRV=$!; fi
if [[ "$DRIVE" == 3 ]]; then DRIVE_LOG="$R/DRIVE-WALK.LOG" $H/drive-walk.sh "$TAG" 25 2 80 > /dev/null 2>&1 & DRV=$!; fi
if [[ "$DRIVE" == 2 ]]; then DRIVE_LOG="$R/DRIVE-WALK.LOG" $H/drive-walk.sh "$TAG" 25 2 90 > /dev/null 2>&1 & DRV=$!; fi
if [[ "$DRIVE" == 1 ]]; then DRIVE_LOG="$R/DRIVE-START.LOG" DRIVE_DIR="$R/drive-start" DRIVE_FALLBACK_COUNTS="19 274" $H/drive-start.sh "$TAG" 1500 > /dev/null 2>&1 & DRV=$!; fi
date +%T > START.txt; date -u +%Y-%m-%dT%H:%M:%SZ > START.UTC
# round L (LAB-JOURNEYS 8.30 A2/A3/A4): board + mouse-stats at lock-take/release, freshness rule, firmware check
FLASH_REPORT="${FLASH_REPORT:-}" python3 ~/git/dosags/build/ws/roundL/snapshots.py "$R" "$TAG" "${FW_EXPECT:-0.5.107}" > "$R/snapshots.out" 2>&1 & SNAP=$!
( cd $H && AGS_EXE="$EXE" ./run-hw.sh "$PKG" --tag "$TAG" "$@" ) > "$R/run-hw.out" 2>&1
echo "run-hw exit=$?" >> "$R/run-hw.out"; date +%T > END.txt
kill $SAMP 2>/dev/null; kill -TERM $REC 2>/dev/null; sleep 3
[[ -n "${DRV:-}" ]] && kill $DRV 2>/dev/null
OUT=$(tail -2 "$R/run-hw.out" | head -1)
[[ -d "$OUT" ]] && cp -r "$OUT"/. "$R/"
# round K (round L rule, coordinator 2026-09-25): the daemon's sent-record. INPUT-LOG.json = the raw window
# (cell start .. now); INPUT-LOG.jsonl = its events from run-hw-<TAG>'s lock.acquired to the matching
# lock.released, one per line. A fetch failure or a missing pair writes INPUT-LOG-VOID.txt: the cell is VOID.
~/git/vcctrl/bin/vcctrl input-log --from "$(cat START.UTC)" --to "$(date -u -d '+5 sec' +%Y-%m-%dT%H:%M:%SZ)" --limit 5000 \
    > "$R/INPUT-LOG.json" 2> "$R/INPUT-LOG.err"
python3 - "$R" "$TAG" <<'PYEOF'
import json, sys, os
r, tag = sys.argv[1], sys.argv[2]
owner = "run-hw-" + tag
def void(why):
    open(os.path.join(r, "INPUT-LOG-VOID.txt"), "w").write(why + "\n"); sys.exit(0)
try:
    d = json.load(open(os.path.join(r, "INPUT-LOG.json")))
except Exception as e:
    void("fetch failed or unparsable: %s" % e)
if not d.get("ok") or d.get("truncated"):
    void("fetch not ok or truncated: ok=%s truncated=%s" % (d.get("ok"), d.get("truncated")))
ev = sorted(d.get("events", []), key=lambda e: e.get("seq", 0))
a = [i for i, e in enumerate(ev) if e.get("kind") == "lock.acquired" and e.get("owner") == owner]
if not a:
    void("no lock.acquired for " + owner)
b = [i for i, e in enumerate(ev) if i > a[0] and e.get("kind") == "lock.released" and e.get("owner") == owner]
if not b:
    void("no lock.released for " + owner + " after its acquire")
# round L: the window runs to lock-release + 1.5 s, so the mouse.dropped rows of the last poll are kept (A3 2)
t_rel = ev[b[0]].get("t")
keep = ev[a[0]:b[0] + 1] + [e for e in ev[b[0] + 1:]
                            if e.get("kind") == "mouse.dropped" and t_rel is not None and e.get("t", 1e18) <= t_rel + 1.5]
with open(os.path.join(r, "INPUT-LOG.jsonl"), "w") as f:
    for e in keep:
        f.write(json.dumps(e, sort_keys=True) + "\n")
PYEOF
for i in $(seq 1 90); do kill -0 $SNAP 2>/dev/null || break; sleep 1; done
kill -0 $SNAP 2>/dev/null && { echo "snapshot helper still running after 90 s -- killed" >> "$R/SNAPSHOTS.txt"; kill $SNAP; echo "snapshot helper did not finish" >> "$R/CROSSCHECK-NA.txt"; }
echo CELLDONE >> "$R/run-hw.out"
sha256sum "$EXE" > POST-RUN-SHA256.txt
/usr/bin/grep -o '"sha256": "[0-9a-f]*"' "$R/run-hw.out" | sort -u > STAGED-SHA256.txt
