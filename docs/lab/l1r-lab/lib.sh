# LAB-L1R lane helpers (sourced). Gate cells: every tick rendered (no fixed timestep), fine timing off, no TICKLOG,
# FRAMEHASH + PRESENT_VERIFY, RANDSEED=1, DOSAGS_CHAR_REUSE=2 in every arm (the round's configuration).
# Arm: 0 = DOSAGS_ROUTE_PREWARM unset, 1 = DOSAGS_ROUTE_PREWARM=1.
D=/home/claude/git/dosags-lab-rb/docs/lab/l1r-lab
L=/home/claude/git/dosags-lab-rb/build/l1r
GATE=$L/exe/L1RGATE.EXE; REL=$L/exe/L1RREL.EXE
export DOSBOX_DISPLAY_NUM=398
C=(--env DOSAGS_RANDSEED=1 --env DOSAGS_LAB_FRAMEHASH=1 --env DOSAGS_PRESENT_VERIFY=1 --env DOSAGS_CHAR_REUSE=2)
arm() { case $1 in 0) X=();; 1) X=(--env DOSAGS_ROUTE_PREWARM=1);; esac; }
G()   { $D/cell.sh $1 $GATE 8600 "${C[@]}" --env DOSAGS_LABCLICKS=G "${@:2}"; }
V()   { $D/cell.sh $1 $GATE 9400 "${C[@]}" --env DOSAGS_LABCLICKS=V "${@:2}"; }
GCL() { $D/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=GCL "${@:2}"; }
H()   { $D/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=H "${@:2}"; }
I()   { NOSAVE=1 $D/cell.sh $1 $GATE 1300 --ags-arg --startr --ags-arg 40 "${C[@]}" "${@:2}"; }
Q()   { $D/pcell.sh $1 $GATE agsquest --no-fine-timing --timeout 2400 "${C[@]}" "${@:2}"; }
# timing (information): --fixed-timestep, fine timing on, TICKLOG, no FRAMEHASH
T()   { FT=1 TL=30000 $D/cell.sh $1 $GATE 12440 --env DOSAGS_RANDSEED=1 --env DOSAGS_CHAR_REUSE=2 --env DOSAGS_LAB_SLOWMS=30 --env DOSAGS_LABCLICKS=H "${@:2}"; }
