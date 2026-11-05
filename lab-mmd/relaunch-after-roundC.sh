#!/usr/bin/env bash
# Relaunch lab-mmd's stopped cells after round C's lab-metric trigger (coordinator, 2026-09-24):
#  - shared cells (VM control, G timing, 0297 self-test v3) once the trigger cell has COMPLETED -- its
#    RUNMANI.LOG carries RUNMANIFEST-END (a directory can appear at the start of a run);
#  - the two EXCLUSIVE screen-gate series only after the main worker's gate-alias run (pid 3167215) has
#    exited as well, so no flock race can put a whole exclusive series ahead of that gate.
set -u
cd "$(dirname "$0")/.."
G2=$HOME/git/dosags-lab-metric/tests/harness/results/LABS32-2026-09-23/G2
trigger_done() {
    local c
    for c in hw0210-B-1 g2b-B-1; do
        /usr/bin/grep -qa 'RUNMANIFEST-END' "$G2/$c/RUNMANI.LOG" 2>/dev/null && { echo "$c"; return 0; }
    done
    return 1
}
gate_alias_running() { ps -p 3167215 -o args= 2>/dev/null | /usr/bin/grep -q 'gate-alias'; }
until c=$(trigger_done); do sleep 30; done
echo "trigger $c complete $(date -u +%H:%M:%S); shared cells"
lab-mmd/run-cells.sh lab-mmd/gvc.spec
lab-mmd/run-cells.sh lab-mmd/ggate-rest.spec
lab-mmd/run-cells.sh lab-mmd/fgst3.spec
while gate_alias_running; do sleep 30; done
echo "gate-alias 3167215 gone $(date -u +%H:%M:%S); exclusive screen gates"
MMD_CONF=$PWD/tools/dosbox-x-fast.conf MMD_LOCK=exclusive DOSBOX_DISPLAY_NUM=261 lab-mmd/run-cells.sh lab-mmd/fgscreen.spec
MMD_CONF=$PWD/tools/dosbox-x-fast.conf MMD_LOCK=exclusive DOSBOX_DISPLAY_NUM=261 lab-mmd/run-cells.sh lab-mmd/gscreen.spec
echo "all done $(date -u +%H:%M:%S)"
