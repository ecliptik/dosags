#!/usr/bin/env bash
# L2DEF: every comparison the README's tables read, from the cell dirs (build/l2d/results) and L2LAND's committed records.
set -u
W=/home/claude/data/worktrees/dosags-l2def; L=$W/build/l2d; R=$L/results; T=$L/tables; mkdir -p $T
L2L=$W/tests/harness/results/L2LAND-2026-11-09
fh() { python3 $L/tools/fhcmp.py "$@"; }
{
echo "== gate 1: the default (unset) vs explicit =1 (both with the lab verify), and vs =0"
for f in G V GCL H I Q; do fh $R/$f-D $R/$f-1 $R/$f-Z; done
echo "== gate 2: =0 on 0373 vs 0372's default off (L2LAND X-0); =1 on 0373 vs L2LAND X-1; the 0373 default vs L2LAND X-1"
for f in G V GCL H I Q; do fh $L2L/$f-0.FHASH.TXT $R/$f-Z; fh $L2L/$f-1.FHASH.TXT $R/$f-1; fh $L2L/$f-1.FHASH.TXT $R/$f-D; done
echo "== controls under the default (LAB-L2G's): C1 marks nothing, C2 rects 1 px short, each vs H-Z must DIFF"
fh $R/H-Z $R/C1-D; fh $R/H-Z $R/C2-D
echo "== forced checks under the default: F?-D vs F?-Z must be EQUAL; each forcing vs unforced H-Z (is it real?)"
for f in F1 F2 F3 F4; do fh $R/$f-Z $R/$f-D; fh $R/H-Z $R/$f-Z | tail -1; done
echo "== forced arms against L2LAND's (0372): F?-Z vs F?-0, F?-D vs F?-1"
for f in F1 F2 F3 F4; do fh $L2L/$f-0.FHASH.TXT $R/$f-Z; fh $L2L/$f-1.FHASH.TXT $R/$f-D; done
echo "== 0373's unknown-value choice: =2 and =off read as on (mode 1); against the intro default"
fh $R/I-D $R/I-X2 $R/I-Xoff
} > $T/fhcmp-all.txt 2>&1
{
echo "== operation-level control: =0 vs the default must DIFF in the witness, l2 and the restore / composite / present px;"
echo "   the default vs =1 must not"
for f in G V GCL H I Q; do python3 $L/tools/l2cmp.py $R/$f-Z $R/$f-D; python3 $L/tools/l2cmp.py $R/$f-1 $R/$f-D; done
echo "== the unknown-value cells against the intro default"
python3 $L/tools/l2cmp.py $R/I-D $R/I-X2; python3 $L/tools/l2cmp.py $R/I-D $R/I-Xoff
} > $T/opcmp-all.txt 2>&1
{
echo "== guictrlmark witness, guictrlmark_final and the lab verify (labgc2_final) per cell"
for c in $(cd $R && ls -d */ | tr -d /); do l=$(grep -a 'DOS-PORT guictrlmark_final' $R/$c/RUNMANI.LOG 2>/dev/null | sed 's/DOS-PORT guictrlmark_final //'); w=$(grep -a 'DOS-PORT guictrlmark DOSAGS' $R/$c/STDOUT.TXT 2>/dev/null | sed 's/DOS-PORT guictrlmark //'); v=$(grep -a 'DOS-PORT labgc2_final' $R/$c/RUNMANI.LOG 2>/dev/null | sed 's/DOS-PORT labgc2_final //'); echo "$c | $w | $l | $v"; done
echo "== labgc2 knob actions (first lines)"
for c in F1-D F2-D F3-D F4-D; do grep -a -h "DOS-PORT labgc2 " $R/$c/STDOUT.TXT | sed "s#^#$c: #" | head -3; done
} > $T/guictrlmark-all.txt 2>&1
{
echo "== P9: 0373 release default (unset) vs 0372's release (8c123c770d0b) with =1; 0373 =0 vs 0372's release unset"
python3 $L/tools/eqcmp.py $R/P9-PREV-1 $R/P9-REL-D; python3 $L/tools/eqcmp.py $R/P9-PREV-D $R/P9-REL-Z
echo "== P9 cross-check: 0372's release here vs L2LAND's committed P9-REL-0 / P9-REL-1 lines (the same binary)"
python3 $L/tools/eqcmp.py $L2L/P9-REL-0.GAMELINES.TXT $R/P9-PREV-D; python3 $L/tools/eqcmp.py $L2L/P9-REL-1.GAMELINES.TXT $R/P9-PREV-1
echo "== release regression, default (unset) vs =0"
for c in RG-5D3S RG-TN35 RG-AQ; do python3 $L/tools/eqcmp.py $R/$c-Z $R/$c-D; done
for a in D Z; do echo "RG-AQ-$a: $(tail -2 $R/RG-AQ-$a/parse.txt | tr '\n' ' ')"; done
echo "== game lines, gate cells: default vs =0, controls, forced"
for p in "H-Z H-D" "H-Z C1-D" "H-Z C2-D" "F1-Z F1-D" "F2-Z F2-D" "F3-Z F3-D" "F4-Z F4-D"; do python3 $L/tools/eqcmp.py $R/${p% *} $R/${p#* }; done
} > $T/eqcmp-all.txt 2>&1
python3 $L/tools/cellcheck.py $(ls -d $R/*/ | sort) > $T/cellcheck-all.txt 2>&1
python3 $L/tools/guardcheck.py $W/vendor/ags HEAD~1..HEAD > $T/guardcheck.txt 2>&1
cat $T/fhcmp-all.txt $T/opcmp-all.txt $T/eqcmp-all.txt $T/guardcheck.txt
