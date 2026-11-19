#!/usr/bin/env bash
# L1LAND: every comparison the README's tables read, from the cell dirs (build/l1/results) and committed records
# (LAB-L1R's cells, R2DEF's records).
set -u
W=/home/claude/git/dosags-l1land; L=$W/build/l1; R=$L/results; T=$L/tables; mkdir -p $T
LAB=$W/docs/lab/l1r-lab/cells; R2D=$W/tests/harness/results/R2DEF-2026-11-08
fh() { python3 $L/tools/fhcmp.py "$@"; }
{
echo "== gate 1: DOSAGS_ROUTE_PREWARM off (unset) vs on (=1), R2 at its 0370 default in both arms"
for f in G V GCL H I Q; do fh $R/$f-0 $R/$f-1; done
echo "== cross-check: 0371 vs LAB-L1R's lever cells (0369 + lever, DOSAGS_CHAR_REUSE=2 explicit), same arm"
for f in G V GCL H I Q; do for a in 0 1; do fh $LAB/$f-$a/FHASH.TXT $R/$f-$a; done; done
for c in C1-1 F1-0 F1-1 F1-N; do fh $LAB/$c/FHASH.TXT $R/$c; done
echo "== lever inert when off: 0371 off vs 0370's default (R2DEF's D arms, same overlay family, verify on)"
for f in G V GCL I Q; do fh $R2D/$f-D.FHASH.TXT $R/$f-0; done
echo "== controls (LAB-L1R): C1 stale warm vs H-0 must DIFF; F1 on vs off EQUAL; F1-N vs F1-0 must DIFF; F1-0 vs H-0 (the forcing is real)"
fh $R/H-0 $R/C1-1; fh $R/F1-0 $R/F1-1; fh $R/F1-0 $R/F1-N; fh $R/H-0 $R/F1-0
echo "== 0371's unknown-value choice: =on and =2 read as off (mode 0); against the intro off arm"
fh $R/I-0 $R/I-Xon $R/I-X2
} > $T/fhcmp-all.txt 2>&1
{
echo "== routeprewarm_final per cell (was the warm exercised?)"
for c in $(cd $R && ls -d */ | tr -d /); do l=$(grep -a 'DOS-PORT routeprewarm_final' $R/$c/RUNMANI.LOG 2>/dev/null | sed 's/DOS-PORT routeprewarm_final //'); w=$(grep -a 'DOS-PORT routeprewarm DOSAGS' $R/$c/STDOUT.TXT 2>/dev/null | sed 's/DOS-PORT routeprewarm //'); echo "$c | $w | $l"; done
echo "== labrpw knob actions"
for c in C1-1 F1-0 F1-1 F1-N; do grep -a -h "DOS-PORT labrpw" $R/$c/STDOUT.TXT | sed "s#^#$c: #" | head -6; done
} > $T/prewarm-all.txt 2>&1
{
echo "== P9: 0371 release unset vs 0370's release (r2def R2DREL, 9db4170acd89) unset -- must MATCH"
python3 $L/tools/eqcmp.py $R/P9-PREV-D $R/P9-REL-0
echo "== P9 extra: 0371 =1 vs 0371 unset (information)"
python3 $L/tools/eqcmp.py $R/P9-REL-0 $R/P9-REL-1
echo "== P9 cross-check: 0370's release unset here vs R2DEF's committed P9-REL-D lines"
python3 $L/tools/eqcmp.py $R2D/P9-REL-D.GAMELINES.TXT $R/P9-PREV-D
echo "== release regression, off (unset) vs on (=1)"
for c in RG-5D3S RG-TN35 RG-AQ; do python3 $L/tools/eqcmp.py $R/$c-0 $R/$c-1; done
for a in 0 1; do echo "RG-AQ-$a: $(tail -2 $R/RG-AQ-$a/parse.txt | tr '\n' ' ')"; done
} > $T/eqcmp-all.txt 2>&1
python3 $L/tools/cellcheck.py $(ls -d $R/*/ | sort) > $T/cellcheck-all.txt 2>&1
cat $T/fhcmp-all.txt $T/eqcmp-all.txt
