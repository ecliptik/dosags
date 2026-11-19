#!/usr/bin/env bash
# L2LAND: collect the text records (no images, no TICKS.BIN, no game data) into tests/harness/results/L2LAND-2026-11-09/.
set -u
W=/home/claude/git/dosags-l2land; L=$W/build/l2; R=$L/results; D=$W/tests/harness/results/L2LAND-2026-11-09
mkdir -p $D $D/tables
mask() { sed 's#/tmp/dos-port-dosbox\.[A-Za-z0-9]*#<stage>#' "$1"; }
for c in $(cd $R && ls -d */ | tr -d /); do
  [ -f $R/$c/FHASH.TXT ] && cp $R/$c/FHASH.TXT $D/$c.FHASH.TXT
  [ -f $R/$c/RUNMANI.LOG ] && cp $R/$c/RUNMANI.LOG $D/$c.RUNMANI.LOG
  [ -f $R/$c/CELL.txt ] && mask $R/$c/CELL.txt > $D/$c.CELL.txt
  case $c in P9-*|RG-*) python3 - $R/$c/STDOUT.TXT > $D/$c.GAMELINES.TXT <<'PY'
import re, sys
for l in open(sys.argv[1], 'rb').read().decode('latin1').splitlines():
    if not (l.startswith('Game :') or l.startswith('DOS-PORT tickclick')): continue
    if re.search(r'(^|[ _])(t_)?ms=|_ms=|_us=', l): continue
    print(l.rstrip())
PY
  ;; esac
done
for a in 0 1; do [ -f $R/RG-AQ-$a/pr/RGAQ$a.json ] && cp $R/RG-AQ-$a/pr/RGAQ$a.json $D/RG-AQ-$a.parse.json; done
cp $L/cell.sh $L/pcell.sh $L/lib.sh $L/lane.sh $L/release.sh $L/build-clean.sh $L/buildAB.sh $L/guardcheck.py \
   $L/tables.sh $L/collect.sh $D/
# (apply-overlay-l2land.py, apply-overlay-rb.py, apply-overlay-r3land.py, build-gate.sh and gate-overlay.diff are written in $D directly)
cp $L/tools/*.py $D/
cp $L/tables/*.txt $D/tables/
LC_ALL=C grep -l -P '[^\x00-\x7F]' $D/* $D/tables/* 2>/dev/null || echo "ascii ok"
du -sh $D
