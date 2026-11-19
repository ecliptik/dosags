# R2DEF lane helpers (sourced; R2LAND's lib.sh). Gate cells: every tick rendered (no fixed timestep), fine timing off,
# no TICKLOG, FRAMEHASH + PRESENT_VERIFY, seeded. Arms (0370 makes unset = mode 2):
#   D  = DOSAGS_CHAR_REUSE unset (the new default) + the lab verify;  Dn = unset, no verify (controls, forcings)
#   2  = DOSAGS_CHAR_REUSE=2 + the lab verify;  1 = =1 + the lab verify;  Z = DOSAGS_CHAR_REUSE=0 (off), no verify
L=/home/claude/git/dosags-r2def/build/r2d
GATE=$L/exe/R2DGATE.EXE
C=(--env DOSAGS_RANDSEED=1 --env DOSAGS_LAB_FRAMEHASH=1 --env DOSAGS_PRESENT_VERIFY=1)
arm() { case $1 in D) X=(--env DOSAGS_LAB_CR_VERIFY=1);; Dn) X=();; Z) X=(--env DOSAGS_CHAR_REUSE=0);;
                   1) X=(--env DOSAGS_CHAR_REUSE=1 --env DOSAGS_LAB_CR_VERIFY=1);;
                   2) X=(--env DOSAGS_CHAR_REUSE=2 --env DOSAGS_LAB_CR_VERIFY=1);; esac; }
G()   { $L/cell.sh $1 $GATE 8600 "${C[@]}" --env DOSAGS_LABCLICKS=G "${@:2}"; }
V()   { $L/cell.sh $1 $GATE 9400 "${C[@]}" --env DOSAGS_LABCLICKS=V "${@:2}"; }
GCL() { $L/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=GCL "${@:2}"; }
I()   { NOSAVE=1 $L/cell.sh $1 $GATE 1300 --ags-arg --startr --ags-arg 40 "${C[@]}" "${@:2}"; }
Q()   { $L/pcell.sh $1 $GATE agsquest --no-fine-timing --timeout 2400 "${C[@]}" "${@:2}"; }
