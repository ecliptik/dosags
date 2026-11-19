# L2LAND lane helpers (sourced; L1LAND's lib.sh with the 0372 arms). Gate cells: every tick rendered (no fixed timestep),
# fine timing off, no TICKLOG, FRAMEHASH + PRESENT_VERIFY, RANDSEED=1. DOSAGS_CHAR_REUSE is NOT set: R2 runs at its 0370
# default (mode 2) in every arm (LAB-L2G set =2 explicitly). Arms: 0 = DOSAGS_GUI_CTRL_MARK unset; 1 = =1 with the lab
# verify (DOSAGS_LAB_GC2_VERIFY, reads only); 1n = =1 without it.
L=/home/claude/git/dosags-l2land/build/l2
GATE=$L/exe/L2GATE.EXE
export DOSBOX_DISPLAY_NUM=398
C=(--env DOSAGS_RANDSEED=1 --env DOSAGS_LAB_FRAMEHASH=1 --env DOSAGS_PRESENT_VERIFY=1)
arm() { case $1 in 0) X=();; 1) X=(--env DOSAGS_GUI_CTRL_MARK=1 --env DOSAGS_LAB_GC2_VERIFY=1);; 1n) X=(--env DOSAGS_GUI_CTRL_MARK=1);; esac; }
G()   { $L/cell.sh $1 $GATE 8600 "${C[@]}" --env DOSAGS_LABCLICKS=G "${@:2}"; }
V()   { $L/cell.sh $1 $GATE 9400 "${C[@]}" --env DOSAGS_LABCLICKS=V "${@:2}"; }
GCL() { $L/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=GCL "${@:2}"; }
H()   { $L/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=H "${@:2}"; }
I()   { NOSAVE=1 $L/cell.sh $1 $GATE 1300 --ags-arg --startr --ags-arg 40 "${C[@]}" "${@:2}"; }
Q()   { $L/pcell.sh $1 $GATE agsquest --no-fine-timing --timeout 2400 "${C[@]}" "${@:2}"; }
