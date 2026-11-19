# L2DEF lane helpers (sourced; L2LAND's lib.sh with the 0373 arms). Gate cells: every tick rendered (no fixed timestep),
# fine timing off, no TICKLOG, FRAMEHASH + PRESENT_VERIFY, RANDSEED=1. DOSAGS_CHAR_REUSE and DOSAGS_ROUTE_PREWARM are not
# set (their defaults: R2 mode 2, L1 off). Arms (0373 makes unset = 1):
#   D = DOSAGS_GUI_CTRL_MARK unset (the new default) + the lab verify (DOSAGS_LAB_GC2_VERIFY, reads only);
#   Dn = unset, no verify; 1 = =1 + verify; Z = =0 (off), no verify.
L=/home/claude/data/worktrees/dosags-l2def/build/l2d
GATE=$L/exe/L2DGATE.EXE
export DOSBOX_DISPLAY_NUM=398
export TMPDIR=/home/claude/data/tmp
C=(--env DOSAGS_RANDSEED=1 --env DOSAGS_LAB_FRAMEHASH=1 --env DOSAGS_PRESENT_VERIFY=1)
arm() { case $1 in D) X=(--env DOSAGS_LAB_GC2_VERIFY=1);; Dn) X=();; Z) X=(--env DOSAGS_GUI_CTRL_MARK=0);;
                   1) X=(--env DOSAGS_GUI_CTRL_MARK=1 --env DOSAGS_LAB_GC2_VERIFY=1);; esac; }
G()   { $L/cell.sh $1 $GATE 8600 "${C[@]}" --env DOSAGS_LABCLICKS=G "${@:2}"; }
V()   { $L/cell.sh $1 $GATE 9400 "${C[@]}" --env DOSAGS_LABCLICKS=V "${@:2}"; }
GCL() { $L/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=GCL "${@:2}"; }
H()   { $L/cell.sh $1 $GATE 12440 "${C[@]}" --env DOSAGS_LABCLICKS=H "${@:2}"; }
I()   { NOSAVE=1 $L/cell.sh $1 $GATE 1300 --ags-arg --startr --ags-arg 40 "${C[@]}" "${@:2}"; }
Q()   { $L/pcell.sh $1 $GATE agsquest --no-fine-timing --timeout 2400 "${C[@]}" "${@:2}"; }
