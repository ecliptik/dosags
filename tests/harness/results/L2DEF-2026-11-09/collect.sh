#!/usr/bin/env bash
# L2DEF: collect the text records (no images, no TICKS.BIN, no game data) into tests/harness/results/L2DEF-2026-11-09/.
set -u
W=/home/claude/data/worktrees/dosags-l2def; L=$W/build/l2d; R=$L/results; D=$W/tests/harness/results/L2DEF-2026-11-09
mkdir -p $D $D/tables
mask() { sed 's#/[^ ]*/dos-port-dosbox\.[A-Za-z0-9]*#<stage>#' "$1"; }
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
for a in D Z; do [ -f $R/RG-AQ-$a/pr/RGAQ$a.json ] && cp $R/RG-AQ-$a/pr/RGAQ$a.json $D/RG-AQ-$a.parse.json; done
cp $L/apply-overlay-l2land.py $L/apply-overlay-rb.py $L/apply-overlay-r3land.py $L/gate-overlay.diff \
   $L/cell.sh $L/pcell.sh $L/lib.sh $L/lane.sh $L/release.sh $L/build-prev.sh $L/build-clean.sh $L/build-gate.sh \
   $L/tables.sh $L/collect.sh $D/
cp $L/tools/*.py $D/
cp $L/tables/*.txt $D/tables/
LC_ALL=C grep -l -P '[^\x00-\x7F]' $D/* $D/tables/* 2>/dev/null || echo "ascii ok"
du -sh $D
