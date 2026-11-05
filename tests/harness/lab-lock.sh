# lab-lock.sh -- sourced by lab-cell.sh and click-cell.sh (lab/journeys): one cell takes the host-wide
# DOSBox-X lock through dosags' own wrapper, dosbox-lock.sh (itself the hub's dosbox-lock-lib.sh: intent
# lock, writer priority), SHARED when the cell's --conf runs at fixed cycles (hub rule bb5482c),
# EXCLUSIVE otherwise. A no-op inside a series or ratchet unit that already holds it (DOSBOX_LOCK_HELD=1).
#   source "$HARNESS/lab-lock.sh"; lab_lock_cell NAME [--exclusive] "$@" || exit $?; trap lab_lock_release EXIT
# --exclusive: always EXCLUSIVE, whatever the conf. RULE (2026-09-24, coordinator): a cell driven by
# wall-clock input (xdotool) is NOT deterministic under the shared lock even at fixed cycles -- fixed
# cycles fix EMULATED time, but a click lands at a WALL-clock time, so under host load it falls on a
# different emulated tick and the game can take a different path (lab/journeys CAP2 G35-on: +439 MIDI
# events). Only cells whose input comes from inside the game (AutoPilot, TAS keyed to ticks) may share.
# "$@" are the cell's run-dosbox.sh arguments; the conf is found after --conf (relative to the harness).
source "$(dirname "${BASH_SOURCE[0]}")/dosbox-lock.sh"
lab_lock_cell() {
    local tool="$1"; shift
    local conf="" a mode=exclusive force=0
    [[ "${1:-}" == --exclusive ]] && { force=1; shift; }
    while [[ $# -gt 0 ]]; do a="$1"; shift; [[ "$a" == --conf ]] && { conf="${1:-}"; shift; }; done
    if [[ $force -eq 0 && -n "$conf" ]]; then
        [[ "$conf" = /* ]] || conf="$(dirname "${BASH_SOURCE[0]}")/$conf"
        dosbox_conf_fixed_cycles "$conf" && mode=shared
    fi
    dosbox_lock_series "$tool" "$mode"
}
lab_lock_release() { dosbox_lock_release; }
