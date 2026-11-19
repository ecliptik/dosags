#!/usr/bin/env bash
# RB cell A: GCL, R2 on (=2), --fixed-timestep, fine timing on, TICKLOG, lab lines
set -u
C=/home/claude/git/dosags-lab-rb/docs/lab/rb-lab/cell.sh; E=/home/claude/git/dosags-lab-rb/build/rb/exe/${EXE:-RBGATE.EXE}
ENV=(--env DOSAGS_RANDSEED=${SEED:-1} --env DOSAGS_CHAR_REUSE=2 --env DOSAGS_LABCLICKS=${FIX:-GCL} --env DOSAGS_LAB_SLOWMS=30)
FT=1 TL=30000 $C ${TAG:-A1} $E 12440 "${ENV[@]}" "$@"
echo CELL-DONE
