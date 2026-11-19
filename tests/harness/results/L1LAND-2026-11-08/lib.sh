# L1LAND lane helpers (sourced; LAB-L1R's lib.sh on R2DEF's paths). Gate cells: every tick rendered (no fixed timestep),
# fine timing off, no TICKLOG, FRAMEHASH + PRESENT_VERIFY, RANDSEED=1. DOSAGS_CHAR_REUSE is NOT set: R2 runs at its 0370
# default (mode 2) in every arm (LAB-L1R set =2 explicitly). Arms: 0 = DOSAGS_ROUTE_PREWARM unset, 1 = =1.
L=/home/claude/git/dosags-l1land/build/l1
GATE=$L/exe/L1GATE.EXE
C=(--env DOSAGS_RANDSEED=1 --env DOSAGS_LAB_FRAMEHASH=1 --env DOSAGS_PRESENT_VERIFY=1)
arm() { case $1 in 0) X=();; 1) X=(--env DOSAGS_ROUTE_PREWARM=1);; esac; }
G()   { $L/cell.sh $1 $GATE 8600 "${C[@]}" --env DOSAGS_LABCLICKS=G "${@:2}"; }
V()   { $L/cell.sh $1 $GATE 9400 "${C[@]}" --env DOSAGS_LABCLICKS=V "${@:2}"; }
GCL() { $L/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=GCL "${@:2}"; }
H()   { $L/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=H "${@:2}"; }
I()   { NOSAVE=1 $L/cell.sh $1 $GATE 1300 --ags-arg --startr --ags-arg 40 "${C[@]}" "${@:2}"; }
Q()   { $L/pcell.sh $1 $GATE agsquest --no-fine-timing --timeout 2400 "${C[@]}" "${@:2}"; }
