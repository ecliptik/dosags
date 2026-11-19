#!/usr/bin/env bash
# R2DEF: every comparison the README's tables read, from the cell dirs (build/r2d/results) and R2LAND's committed records.
set -u
L=/home/claude/git/dosags-r2def/build/r2d; R=$L/results; T=$L/tables; mkdir -p $T
R2=/home/claude/git/dosags-r2def/tests/harness/results/R2LAND-2026-11-07
fh() { python3 $L/tools/fhcmp.py "$@"; }
{
echo "== gate 1: the default (unset) vs explicit =2, and vs =0 (the lever is frame-equal to off)"
for f in G V GCL I Q; do fh $R/$f-D $R/$f-2 $R/$f-Z; done
echo "== gate 3a: the operation-level control (sdlports): =0 vs the default must DIFF in what R2 changes (witness, skips,"
echo "   restore / GUI composite / present px); the default vs =2 must not"
for f in G V GCL I Q; do python3 $L/tools/opcmp.py $R/$f-Z $R/$f-D; python3 $L/tools/opcmp.py $R/$f-2 $R/$f-D; done
echo "== gate 2: =0 on 0370 vs 0369 default off (R2LAND X-0), =1 on 0370 vs 0369 =1 (R2LAND X-1)"
for f in G V GCL I Q; do fh $R2/$f-0.FHASH.TXT $R/$f-Z; fh $R2/$f-1.FHASH.TXT $R/$f-1; done
echo "== gate 2 extra: the 0370 default vs 0369 =2 (R2LAND X-2)"
for f in G V GCL I Q; do fh $R2/$f-2.FHASH.TXT $R/$f-D; done
echo "== gate 3: controls under the default (each against its =0 arm)"
fh $R/G-Z $R/G-D-NODRAW; fh $R/GCL-Z $R/GCL-D-NODRAW
fh $R/G-B-Z $R/G-B-D $R/G-B-N
echo "== gate 4: forced guards under the default (each against its own forced =0 arm)"
fh $R/G-T-Z $R/G-T-D $R/G-T-N
fh $R/G-L-Z $R/G-L-D $R/G-L-N
fh $R/G-C-Z $R/G-C-D $R/G-C-N
fh $R/G-S-Z $R/G-S-D
echo "== gate 4: in-place edits under the default: dynamic sprite (DYN, cells G-Y-*) and walk-behind mask (WBM, G-W-*)"
fh $R/G-Y-Z $R/G-Y-D $R/G-Y-N
fh $R/G-W-Z $R/G-W-D $R/G-W-N
echo "== forced =0 arms against unforced G-Z (does the forcing change an off picture?)"
fh $R/G-Z $R/G-T-Z $R/G-L-Z $R/G-C-Z $R/G-S-Z $R/G-B-Z $R/G-Y-Z $R/G-W-Z
echo "== forced =0 arms on 0370 against R2LAND's forced mode-0 arms on 0369 (R2LAND's DYN arm was named G-D-0)"
fh $R2/G-T-0.FHASH.TXT $R/G-T-Z; fh $R2/G-L-0.FHASH.TXT $R/G-L-Z; fh $R2/G-C-0.FHASH.TXT $R/G-C-Z
fh $R2/G-S-0.FHASH.TXT $R/G-S-Z; fh $R2/G-B-0.FHASH.TXT $R/G-B-Z; fh $R2/G-D-0.FHASH.TXT $R/G-Y-Z; fh $R2/G-W-0.FHASH.TXT $R/G-W-Z
echo "== extras: the default under DOSAGS_GUI_CLIP=0 and =2 (G), against =0 under the same GUI_CLIP, and =0 vs R2LAND"
for g in 0 2; do fh $R/G-G$g-Z $R/G-G$g-Dn; fh $R2/G-G$g-0.FHASH.TXT $R/G-G$g-Z; done
echo "== 0370's unknown-value choice: DOSAGS_CHAR_REUSE=3 and =off read as the default (mode 2); against the intro default"
fh $R/I-D $R/I-X3 $R/I-Xoff; python3 $L/tools/opcmp.py $R/I-D $R/I-X3; python3 $L/tools/opcmp.py $R/I-D $R/I-Xoff
} > $T/fhcmp-all.txt 2>&1
{
echo "== P9: 0370 release default (unset) vs main's 0369 release (84c1a74fdcf6) with =2; 0370 =0 vs main's release unset"
python3 $L/tools/eqcmp.py $R/P9-MAIN-2 $R/P9-REL-D; python3 $L/tools/eqcmp.py $R/P9-MAIN-D $R/P9-REL-Z
echo "== P9 cross-check against R2LAND's committed game lines (same main binary)"
python3 $L/tools/eqcmp.py $R2/P9-REL-2.GAMELINES.TXT $R/P9-MAIN-2; python3 $L/tools/eqcmp.py $R2/P9-MAIN-D.GAMELINES.TXT $R/P9-MAIN-D
echo "== release regression, default (unset) vs =0"
for c in RG-5D3S RG-TN35 RG-AQ; do python3 $L/tools/eqcmp.py $R/$c-Z $R/$c-D; done
for a in D Z; do echo "RG-AQ-$a: $(tail -2 $R/RG-AQ-$a/parse.txt | tr '\n' ' ')"; done
} > $T/eqcmp-all.txt 2>&1
python3 $L/tools/cellcheck.py $(ls -d $R/*/ | sort) > $T/cellcheck-all.txt 2>&1
cat $T/fhcmp-all.txt $T/eqcmp-all.txt
