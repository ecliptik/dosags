# R2LAND lane helpers (sourced; LAB-R2B's lib.sh). Gate cells: every tick rendered (no fixed timestep), fine timing off,
# no TICKLOG, FRAMEHASH + PRESENT_VERIFY, seeded. Arm: 0 = DOSAGS_CHAR_REUSE unset (the default, off), 1, 2 (with the
# lab verify on), 2n = 2 without the verify (controls).
L=/home/claude/git/dosags-r2land/build/r2
GATE=$L/exe/R2GATE.EXE
C=(--env DOSAGS_RANDSEED=1 --env DOSAGS_LAB_FRAMEHASH=1 --env DOSAGS_PRESENT_VERIFY=1)
arm() { case $1 in 0) X=();; 1) X=(--env DOSAGS_CHAR_REUSE=1 --env DOSAGS_LAB_CR_VERIFY=1);;
                   2) X=(--env DOSAGS_CHAR_REUSE=2 --env DOSAGS_LAB_CR_VERIFY=1);; 2n) X=(--env DOSAGS_CHAR_REUSE=2);; esac; }
G()   { $L/cell.sh $1 $GATE 8600 "${C[@]}" --env DOSAGS_LABCLICKS=G "${@:2}"; }
V()   { $L/cell.sh $1 $GATE 9400 "${C[@]}" --env DOSAGS_LABCLICKS=V "${@:2}"; }
GCL() { $L/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=GCL "${@:2}"; }
I()   { NOSAVE=1 $L/cell.sh $1 $GATE 1300 --ags-arg --startr --ags-arg 40 "${C[@]}" "${@:2}"; }
Q()   { $L/pcell.sh $1 $GATE agsquest --no-fine-timing --timeout 2400 "${C[@]}" "${@:2}"; }
