#!/usr/bin/env bash
# LAB-R2B lane C (display 394): controls (i) NODRAW and (ii) NOBASEL, then the forced guards on fixture G. Serialized.
set -u; export DOSBOX_DISPLAY_NUM=394; source /home/claude/git/dosags-lab-r2b/build/r2b/lib.sh
arm 2n
G   G-2-NODRAW   "${X[@]}" --env DOSAGS_LAB_CR_NODRAW=1
GCL GCL-2-NODRAW "${X[@]}" --env DOSAGS_LAB_CR_NODRAW=1
G   G-2-NOBASEL  "${X[@]}" --env DOSAGS_LAB_CR_NOBASEL=1
GCL GCL-2-NOBASEL "${X[@]}" --env DOSAGS_LAB_CR_NOBASEL=1
I   I-2-NOBASEL  "${X[@]}" --env DOSAGS_LAB_CR_NOBASEL=1
Q   Q-2-NOBASEL  "${X[@]}" --env DOSAGS_LAB_CR_NOBASEL=1
# guard (1), the old-rect mark: character 1 (Syd) not drawn on every 7th scene; N = marks counted, not made
FT_=(--env DOSAGS_LAB_CR_TOGGLE=7)
G G-T-0 "${FT_[@]}"; G G-T-2 "${FT_[@]}" "${X[@]}"; G G-T-N "${FT_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOMARK=1
# guard (2a), 0366's latch: a whole-surface restore every 7th room restore (R3LAND's forcing); N = R2b ignores the latch
FL_=(--env DOSAGS_LAB_FORCE_WHOLE=7)
G G-L-0 "${FL_[@]}"; G G-L-2 "${FL_[@]}" "${X[@]}"; G G-L-N "${FL_[@]}" "${X[@]}" --env DOSAGS_LAB_CR_NOLATCH=1
echo LANEC-DONE
