#!/usr/bin/env bash
# L2LAND: every comparison the README's tables read, from the cell dirs (build/l2/results) and committed records
# (LAB-L2G section 8's cells, L1LAND's records).
set -u
W=/home/claude/git/dosags-l2land; L=$W/build/l2; R=$L/results; T=$L/tables; mkdir -p $T
LAB=/home/claude/git/dosags-lab-rb/docs/lab/l2g-lab/cells-s8; L1L=$W/tests/harness/results/L1LAND-2026-11-08
fh() { python3 $L/tools/fhcmp.py "$@"; }
{
echo "== gate 1: DOSAGS_GUI_CTRL_MARK off (unset) vs on (=1, lab verify), R2 at its 0370 default in both arms"
for f in G V GCL H I Q; do fh $R/$f-0 $R/$f-1; done
echo "== cross-check: 0372 vs LAB-L2G section 8's slim-lever cells (0369 + lever, DOSAGS_CHAR_REUSE=2 explicit), same arm"
for f in G V GCL H I Q; do for a in 0 1; do fh $LAB/$f-$a/FHASH.TXT $R/$f-$a; done; done
for c in C1-1 C2-1 F1-0 F1-1 F2-0 F2-1 F3-0 F3-1 F4-0 F4-1; do fh $LAB/$c/FHASH.TXT $R/$c; done
echo "== lever inert when off: 0372 off vs 0371 off (L1LAND's 0 arms: 0371 default, its own overlay)"
for f in G V GCL H I Q; do fh $L1L/$f-0.FHASH.TXT $R/$f-0; done
echo "== controls: C1 (marks nothing) and C2 (1 px short) vs H-0 must DIFF"
fh $R/H-0 $R/C1-1; fh $R/H-0 $R/C2-1
echo "== forced checks, off vs on EQUAL; each forcing vs unforced H-0 (is it real?)"
for f in F1 F2 F3 F4; do fh $R/$f-0 $R/$f-1; fh $R/H-0 $R/$f-0 | tail -1; done
echo "== L1 + L2 together: H with ROUTE_PREWARM=1 + GUI_CTRL_MARK=1 (HP-1) vs ROUTE_PREWARM=1 (HP-0); HP-0 vs L1LAND H-1"
fh $R/HP-0 $R/HP-1; fh $L1L/H-1.FHASH.TXT $R/HP-0 | tail -1
} > $T/fhcmp-all.txt 2>&1
{
echo "== guictrlmark witness and final per cell"
for c in $(cd $R && ls -d */ | tr -d /); do l=$(grep -a 'DOS-PORT guictrlmark_final' $R/$c/RUNMANI.LOG 2>/dev/null | sed 's/DOS-PORT guictrlmark_final //'); w=$(grep -a 'DOS-PORT guictrlmark DOSAGS' $R/$c/STDOUT.TXT 2>/dev/null | sed 's/DOS-PORT guictrlmark //'); v=$(grep -a 'DOS-PORT labgc2_final' $R/$c/RUNMANI.LOG 2>/dev/null | sed 's/DOS-PORT labgc2_final //'); p=$(grep -a 'DOS-PORT routeprewarm_final' $R/$c/RUNMANI.LOG 2>/dev/null | sed 's/DOS-PORT routeprewarm_final //' | cut -c1-60); echo "$c | $w | $l | $v | rp: $p"; done
echo "== labgc2 knob actions (first lines)"
for c in F1-1 F2-1 F3-1 F4-1; do grep -a -h "DOS-PORT labgc2 " $R/$c/STDOUT.TXT | sed "s#^#$c: #" | head -3; done
} > $T/guictrlmark-all.txt 2>&1
{
echo "== P9: 0372 release unset vs 0371's release (l1land L1REL, a6aaab93c3d2) unset -- must MATCH"
python3 $L/tools/eqcmp.py $R/P9-PREV-D $R/P9-REL-0
echo "== P9 extra: 0372 =1 vs 0372 unset (information)"
python3 $L/tools/eqcmp.py $R/P9-REL-0 $R/P9-REL-1
echo "== P9 cross-check: 0371's release unset here vs L1LAND's committed P9-REL-0 lines"
python3 $L/tools/eqcmp.py $L1L/P9-REL-0.GAMELINES.TXT $R/P9-PREV-D
echo "== release regression, off (unset) vs on (=1)"
for c in RG-5D3S RG-TN35 RG-AQ; do python3 $L/tools/eqcmp.py $R/$c-0 $R/$c-1; done
for a in 0 1; do echo "RG-AQ-$a: $(tail -2 $R/RG-AQ-$a/parse.txt | tr '\n' ' ')"; done
echo "== game lines, gate cells: off vs on, controls, forced, L1+L2"
for p in "H-0 H-1" "H-0 C1-1" "H-0 C2-1" "F1-0 F1-1" "F2-0 F2-1" "F3-0 F3-1" "F4-0 F4-1" "HP-0 HP-1"; do python3 $L/tools/eqcmp.py $R/${p% *} $R/${p#* }; done
} > $T/eqcmp-all.txt 2>&1
python3 $L/tools/cellcheck.py $(ls -d $R/*/ | sort) > $T/cellcheck-all.txt 2>&1
cat $T/fhcmp-all.txt $T/eqcmp-all.txt
