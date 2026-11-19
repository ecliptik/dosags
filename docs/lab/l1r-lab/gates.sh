#!/usr/bin/env bash
# LAB-L1R gate tables from build/l1r/results (writes docs/lab/l1r-lab/tables/)
set -u
D=/home/claude/git/dosags-lab-rb/docs/lab/l1r-lab; R=/home/claude/git/dosags-lab-rb/build/l1r/results; T=$D/tables; mkdir -p $T
cd $R
{ echo "== G1 frames (FHASH by loop counter; off vs on)"
  for f in G V GCL H I Q; do python3 $D/fhcmp.py $f-0 $f-1; done
  echo "== C1 / F1 (vs the matching off arm)"
  python3 $D/fhcmp.py H-0 C1-1; python3 $D/fhcmp.py F1-0 F1-1; python3 $D/fhcmp.py F1-0 F1-N; python3 $D/fhcmp.py H-0 F1-0
} > $T/fhcmp.txt 2>&1
{ for p in "RG-5D3S-0 RG-5D3S-1" "RG-TN35-0 RG-TN35-1" "RG-AQ-0 RG-AQ-1" "T-H-0 T-H-1" "H-0 H-1" "F1-0 F1-1" "H-0 C1-1" "F1-0 F1-N"; do
    python3 $D/eqcmp.py ${p% *} ${p#* }; done
  for a in 0 1; do echo "RG-AQ-$a: $(grep -h 'PASS\|FAIL\|parse rc' RG-AQ-$a/parse.txt | tr '\n' ' ' | cut -c1-200)"; done
} > $T/eqcmp.txt 2>&1
python3 $D/cellcheck.py $(ls -d */ | sed 's#/##') > $T/cellcheck.txt 2>&1
for c in */; do c=${c%/}; grep -h "DOS-PORT labrpw\|presentverify" $c/STDOUT.TXT $c/RUNMANI.LOG 2>/dev/null | sed "s#^#$c: #" | head -6; done > $T/knobs-pv.txt
for c in T-H-0 T-H-1; do echo "== $c"; grep -h "rbroute\|rbslow lc=5436 \|rbslow lc=7711 \|rbslow lc=6154 \|rbslow lc=7895 " $c/STDOUT.TXT | cut -c1-240; python3 $D/../rb-lab/winskips.py $c; done > $T/timing.txt
echo GATES-DONE
