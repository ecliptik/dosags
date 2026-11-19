#!/usr/bin/env bash
# R2LAND: every comparison the README's tables read, from the cell dirs (build/r2/results) or the committed records.
set -u
L=/home/claude/git/dosags-r2land/build/r2; R=$L/results; T=$L/tables; mkdir -p $T
R3=/home/claude/git/dosags-r2land/tests/harness/results/R3LAND-2026-11-06
fh() { python3 $L/tools/fhcmp.py "$@"; }
{
echo "== gate 1: mode 1 and mode 2 vs 0 (default)"
for f in G V GCL I Q; do fh $R/$f-0 $R/$f-1 $R/$f-2; done
echo "== gate 2: CHAR_REUSE=2 vs 0 under DOSAGS_GUI_CLIP=2 (R1) and =0 (off)"
for f in G GCL; do for g in 2 0; do fh $R/$f-G$g-0 $R/$f-G$g-2; done; done
echo "== gate 3: controls"
fh $R/G-0 $R/G-2-NODRAW; fh $R/GCL-0 $R/GCL-2-NODRAW
fh $R/G-B-0 $R/G-B-2 $R/G-B-N
echo "== gate 4: forced guards (each against its own forced mode-0 arm)"
fh $R/G-T-0 $R/G-T-2 $R/G-T-N
fh $R/G-L-0 $R/G-L-2 $R/G-L-N
fh $R/G-C-0 $R/G-C-2 $R/G-C-N
echo "== in-place edits: dynamic sprite (DYN) and walk-behind mask (WBM)"
fh $R/G-D-0 $R/G-D-2 $R/G-D-N
fh $R/G-W-0 $R/G-W-2 $R/G-W-N
echo "== forced mode-0 arms against unforced G-0 (does the forcing change a mode-0 picture?)"
fh $R/G-0 $R/G-T-0 $R/G-L-0 $R/G-C-0 $R/G-B-0 $R/G-D-0 $R/G-W-0
echo "== lever inert: default (=0) gate arms against main's R3LAND records (0001-0368 + R3LAND overlay)"
fh $R3/GG-D.FHASH.TXT $R/G-0; fh $R3/GV-D.FHASH.TXT $R/V-0; fh $R3/GI-D.FHASH.TXT $R/I-0; fh $R3/GQ-D.FHASH.TXT $R/Q-0
fh $R3/GG-2.FHASH.TXT $R/G-G2-0; fh $R3/GG-0.FHASH.TXT $R/G-G0-0
} > $T/fhcmp-all.txt 2>&1
{
echo "== P9: the 0369 release vs main's release (4c9f83b62c5c)"
python3 $L/tools/eqcmp.py $R/P9-MAIN-D $R/P9-REL-0; python3 $L/tools/eqcmp.py $R/P9-MAIN-D $R/P9-REL-2
echo "== release regression, default (=0) vs =2"
for c in RG-5D3S RG-TN35 RG-AQ; do python3 $L/tools/eqcmp.py $R/$c-0 $R/$c-2; done
for a in 0 2; do echo "RG-AQ-$a: $(tail -2 $R/RG-AQ-$a/parse.txt | tr '\n' ' ')"; done
} > $T/eqcmp-all.txt 2>&1
python3 $L/tools/cellcheck.py $(ls -d $R/*/ | sort) > $T/cellcheck-all.txt 2>&1
cat $T/fhcmp-all.txt $T/eqcmp-all.txt
{
echo "== extras: 0368's coarse guard forced (SPANMAX=1, SPANPROBE=7:166), and DOSAGS_GUI_CLIP=1"
fh $R/G-S-0 $R/G-S-2; fh $R/G-G1-0 $R/G-G1-2; fh $R/G-0 $R/G-S-0 $R/G-G1-0
} > $T/fhcmp-extras.txt 2>&1
cat $T/fhcmp-extras.txt
