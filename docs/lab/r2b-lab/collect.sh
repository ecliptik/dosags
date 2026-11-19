#!/usr/bin/env bash
# LAB-R2B: collect the text records (no images, no TICKS.BIN) into docs/lab/r2b-lab/ of this worktree (not committed).
set -u
L=/home/claude/git/dosags-lab-r2b/build/r2b; R=$L/results; D=/home/claude/git/dosags-lab-r2b/docs/lab/r2b-lab
mkdir -p $D/cells $D/tables
mask() { sed 's#/tmp/dos-port-dosbox\.[A-Za-z0-9]*#<stage>#' "$1"; }
for c in $(cd $R && ls -d */ | tr -d /); do
  [ "$c" = v1 ] && continue
  [ -f $R/$c/FHASH.TXT ] && cp $R/$c/FHASH.TXT $D/cells/$c.FHASH.TXT
  [ -f $R/$c/RUNMANI.LOG ] && cp $R/$c/RUNMANI.LOG $D/cells/$c.RUNMANI.LOG
  [ -f $R/$c/CELL.txt ] && mask $R/$c/CELL.txt > $D/cells/$c.CELL.txt
  [ -f $R/$c/RUN.BAT ] && cp $R/$c/RUN.BAT $D/cells/$c.RUN.BAT
  case $c in P9-*|RG-*) python3 - $R/$c/STDOUT.TXT > $D/cells/$c.GAMELINES.TXT <<'PY'
import re, sys
for l in open(sys.argv[1], 'rb').read().decode('latin1').splitlines():
    if not (l.startswith('Game :') or l.startswith('DOS-PORT tickclick')): continue
    if re.search(r'(^|[ _])(t_)?ms=|_ms=|_us=', l): continue
    print(l.rstrip())
PY
  ;; esac
  case $c in T-*) grep -a '^DOS-PORT labck ' $R/$c/STDOUT.TXT > $D/cells/$c.LABCK.TXT;; esac
done
for a in 0 2; do [ -f $R/RG-AQ-$a/pr/RGAQ$a.json ] && cp $R/RG-AQ-$a/pr/RGAQ$a.json $D/cells/RG-AQ-$a.parse.json; done
cp $L/lever-r2b.py $L/apply-overlay-r2b.py $L/apply-overlay-r3land.py $L/lab-r2b.diff $L/lab-r2b-gate-full.diff \
   $L/cell.sh $L/pcell.sh $L/lib.sh $L/lane?.sh $L/chain?.sh $L/build-all2.sh $L/collect.sh $D/
cp $L/tools/*.py $D/
LC_ALL=C grep -l -P '[^\x00-\x7F]' $D/* $D/cells/* 2>/dev/null || echo "ascii ok"
du -sh $D
