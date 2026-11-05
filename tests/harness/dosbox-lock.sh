# dosbox-lock.sh -- sourced, not run. dosags' wrapper over the hub's host-wide DOSBox-X lock library
# (.sdl-dos-ports/shared/tools/dosbox-lock-lib.sh, hub b9b7364): take the lock ONCE around a whole
# series (a gate, an ABBA or probe series, one run-dosbox.sh run), so no other worker's DOSBox-X can
# start between two runs of it or during one of its screen captures.
#
# One protocol, one implementation: the lock file, the intent lock (writer priority -- a queued
# exclusive waiter blocks NEW shared takers, so a stream of overlapping readers cannot starve it) and
# the .who lines are all the library's. What stays here is dosags-specific:
#   - the series mode: `dosbox_lock_series NAME [shared|exclusive]` (default exclusive). Shared is for
#     a series whose every run is at FIXED cycles -- deterministic whatever the host load (hub
#     bb5482c). cycles=max timing/rate, cycles=max gates and --sb-live at cycles=max stay exclusive.
#   - nesting: once held, DOSBOX_LOCK_HELD=1 (and DOSBOX_LOCK_HELD_MODE) are exported, so the
#     dosbox-run.sh calls inside do not take it again (that would deadlock) and a nested series
#     (run-dosbox.sh inside gate-alias.sh) does nothing. A nested series that needs exclusive under a
#     SHARED parent is refused (exit 75): a shared holder cannot upgrade in place.
#   - dosbox_conf_fixed_cycles CONF: whether a conf sets `cycles = fixed N`.
#
# The lock lives on fd 8 of this shell and of every child that inherits it (DOSBox-X included), so it
# is released when the series and all its children have exited; run-dosbox.sh's EXIT trap makes sure
# no watcher outlives it holding the fd.
#
#   source "$HARNESS/dosbox-lock.sh"; dosbox_lock_series gate-alias.sh || exit $?
#   trap dosbox_lock_release EXIT      # or call it from an existing EXIT trap
#
# Waits up to DOSBOX_LOCK_WAIT seconds (default 3600, as dosbox-run.sh), then returns 75.
_DBL_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_DBL_LIB="$_DBL_HERE/../../.sdl-dos-ports/shared/tools/dosbox-lock-lib.sh"
if [[ ! -f "$_DBL_LIB" ]]; then
    echo "dosbox-lock.sh: $_DBL_LIB not found -- pull the .sdl-dos-ports subtree (hub b9b7364 or later)" >&2
    return 75 2>/dev/null || exit 75
fi
# shellcheck source=../../.sdl-dos-ports/shared/tools/dosbox-lock-lib.sh
source "$_DBL_LIB"

DOSBOX_LOCK_OWNED=0
dosbox_lock_who() { dbxlock_describe; }   # kept for callers of the old name
dosbox_conf_fixed_cycles() {   # 0 if CONF sets `cycles = fixed N` (or a bare number)
    [[ -n "${1:-}" && -f "$1" ]] || return 1
    /usr/bin/grep -Eiq '^[[:space:]]*cycles[[:space:]]*=[[:space:]]*(fixed[[:space:]]+)?[0-9]+[[:space:]]*$' "$1"
}
dosbox_lock_series() {
    local tool="$1" mode="${2:-exclusive}"
    case "$mode" in shared|exclusive) ;; *) echo "dosbox_lock_series: mode must be shared or exclusive" >&2; return 2 ;; esac
    if [[ "${DOSBOX_LOCK_HELD:-0}" == "1" ]]; then
        if [[ "$mode" == exclusive && "${DOSBOX_LOCK_HELD_MODE:-exclusive}" == shared ]]; then
            echo "$tool: needs the exclusive DOSBox-X lock but its parent holds it shared; not running" >&2
            return 75
        fi
        return 0
    fi
    local w="${DOSBOX_LOCK_WAIT:-3600}"
    if ! dbxlock_acquire "$mode" "$w" "tool=$tool series=1"; then
        echo "$tool: DOSBox-X lock ($mode) still busy after ${w}s; not running" >&2
        return 75
    fi
    export DOSBOX_LOCK_HELD=1 DOSBOX_LOCK_HELD_MODE="$mode" DOSBOX_LOCK_FILE="$DBXLOCK_FILE"
    DOSBOX_LOCK_OWNED=1
    return 0
}
dosbox_lock_release() {   # our .who lines out, fd 8 closed (the library's release)
    [[ "$DOSBOX_LOCK_OWNED" == "1" ]] || return 0
    dbxlock_release
    DOSBOX_LOCK_OWNED=0
    return 0
}
