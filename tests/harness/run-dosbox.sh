#!/usr/bin/env bash
# run-dosbox.sh -- stage + run a built test package under DOSBox-X with
# the autopilot armed (--test), collecting STDOUT.TXT/RUNMANI.LOG/
# AUTOPLT.LOG (and, once slice 5 wires real captures, screenshots).
#
# Headless by default -- sufficient through slice 3, since no
# screenshots are taken yet. --interactive opens a real DOSBox-X window
# on a private Xvfb (DOSBOX_DISPLAY, never the caller's real DISPLAY --
# see .sdl-dos-ports/shared/skills/dos-emulator-workflow/references/
# tooling.md) for slice 5's screenshot phase.
#
# A real, playing game never self-exits on its own in the general case,
# but this harness's own autopilot does (QuitGame(0) at the end of the
# phase sequence) -- still wrapped in an external timeout as a safety
# net against a stuck phase, per this project's own tooling findings
# (dosbox-run.sh's headless mode has no internal timeout).
#
# Prints the staged run directory's path as its last line of stdout, so
# `./parse-results.py $(./run-dosbox.sh agsquest)` chains directly.
#
# Usage:
#   ./run-dosbox.sh <package-name> [--interactive] [--timeout SECONDS] [--env KEY=VALUE]...
#
# --env KEY=VALUE (repeatable): passed straight through to dosbox-run.sh's
# own --env (a real DOS `SET` in RUN.BAT, reaching SDL_GetHint()'s own
# getenv() fallback) -- e.g. --env SDL_HINT_DOS_AUDIO_BACKEND=gus. Added for
# the S5 GUS architecture work; the S5 WaveBlaster validation before it had
# to stage RUN.BAT by hand for exactly this gap (see that session's own
# PLAN.md write-up).
#
# --include-extra PATH (repeatable): passed straight through to
# dosbox-run.sh's own --include (staged to C:\ with an uppercased
# basename, same as the .ags package already is). Added for the Game
# porting framework's own S7 need: a binary-only golden reference has no
# per-package acsetup.cfg baked in the way AGS Quest's Wine build produces
# one, so `tools/port-game/layout.py`'s two sound-on/sound-off ACSETUP.CFG
# variants need a way in that isn't a hardcoded second --include.
# PATH:NAME (2026-09-26) stages PATH as NAME instead (uppercased), e.g.
# `--include-extra games/5days/ACSETUP-ON.CFG:ACSETUP.CFG`. A staged name
# matching *ACSETUP*.CFG that is not exactly ACSETUP.CFG is REFUSED: the
# engine reads only ACSETUP.CFG, so a variant staged under its own name
# silently turns the cell into a different fixture (lab-s8 and lab-s32 both
# ran sound-off cfgs that the game never read). --allow-odd-cfg-name lets
# such a name through for the rare intentional case.

set -euo pipefail

usage() { echo "Usage: $0 <package-name> [--interactive] [--fixed-timestep] [--timeout SECONDS] [--env KEY=VALUE]... [--include-extra PATH[:NAME]]... [--allow-odd-cfg-name] [--conf PATH] [--ags-arg ARG]... [--screen-series DIR [--series-every SEC]] [--freeze-capture DIR] [--no-verify-present] [--no-fine-timing] [--sb-live]" >&2; exit 1; }
[[ $# -ge 1 ]] || usage
PKG="$1"; shift

# --fixed-timestep: SET DOSAGS_FIXED_TIMESTEP=1, which run-hw.sh sets BY
# DEFAULT and this script never has. That asymmetry silently invalidated an
# instrument verification on 2026-09-19: dos_run_tick_fixed()'s catch-up
# loop had never executed under the emulator, so an instrument living in it
# ran zero times here while appearing to have been checked, and the
# resulting frames_skipped=0 read as "the emulator keeps up" rather than
# "the code is switched off".
#
# NOT made the default, deliberately: the committed DOSBox-X expectations
# (expected/agsquest/dosbox-x.json, the PH0N.BMP hashes) were all recorded
# without it, and flipping the default would change what every existing
# baseline compares against. Opt in for instrument verification; leave it
# off for regression runs.
FIXED_TIMESTEP=0
FINE_TIMING=1   # ags 0315: see the FINE_TIMING block below
INTERACTIVE=0
# 300, not the original 120: a full 18-phase AGS Quest autopilot run
# reaches `quit` around tick 3560 and the old default cut it off in the
# `audio` phase (tick ~3144), which also silently blanks the baseline
# comparison (no RUNMANIFEST -> environment=unknown -> "no committed
# baseline" instead of a real mismatch). Found 2026-09-16 while
# re-baselining after the sprite-alpha fix; pre-existing, not caused by
# it. --timeout still overrides per run.
TIMEOUT_S=300
TIMEOUT_EXPLICIT=0
ENVS=()
EXTRA_INCLUDES=()
ALLOW_ODD_CFG=0
# --conf PATH: passed straight through to dosbox-run.sh's own --conf (hub,
# 2026-09-16) in place of its --fast default. This port's own confs live
# in tests/harness/confs/ -- dosbox-x-fast-opl3.conf is the fast conf
# with oplmode=opl3, the one the Sound gate's sound-on arm needs for
# OPL3 chip detection under emulation (the hub's shipped confs set
# oplmode=none by design). A manifest names it via validate: dosbox_conf.
CONF_OVERRIDE=""
# --ags-arg ARG (repeatable, 2026-09-22): one more command-line argument for AGS.EXE, same
# interface as run-hw.sh's own flag of the same name (e.g. --ags-arg --startr --ags-arg 3 --
# see run-hw.sh's own comment for what --startr does). This was previously reachable only
# through the undocumented AGS_EXTRA_ARGS env var below (kept working, for anything already
# using it); added as a flag once the 0196-generalization work needed to find 5 Days a
# Stranger's own in-play room locally before spending real-hardware time on it, the same way
# S2T2 already used --startr 3 for Trilby's Notes on real hardware -- every future 320-wide
# catalogue title hits this same need to find and verify its own room number, so it belongs
# in the wrapper, not rediscovered per session. Appended after AGS_EXTRA_ARGS if both are set.
AGS_ARGS=()
# --screen-series DIR (2026-09-21): capture the EMULATED SCREEN every --series-every seconds
# (default 0.5) into DIR/frames/ for the whole run and build DIR/sheet.png plus a manifest.
# Implies --interactive, because the picture only exists on a display (a private Xvfb).
# Why: every other check in this harness reads the engine's own RAM frame
# (SaveScreenShot -> GetCopyOfScreenIntoBitmap -> virtualScreen), so a region that changed in
# RAM and was never pushed to the screen ("trails") passes every hash. Only a frame of the
# screen sees it, at a WALKING or speaking moment, not the still PH0N moments.
SERIES_DIR=""
SERIES_EVERY="0.5"
# --freeze-capture DIR (2026-09-21): pairs with DOSAGS_FREEZE_TICKS (ags patch 0195). The engine stalls at each chosen tick
# and writes FRZnn.TXT into its directory (the staging dir on the host); this watches for it and photographs the emulated
# screen ONCE per marker, into DIR/frames/FRZnn.png with the marker copied beside it, and records the staging dir in DIR/stage.
# Tick-synchronised captures are what make a pixel-for-pixel comparison of two runs meaningful. Implies --interactive.
FREEZE_DIR=""
# The present verifier (ags patch 0192) is ON by default here and off on hardware: it reads
# the window surface twice per present, which is nothing to an emulator and a lot to a 486.
# parse-results.py and port_game.py FAIL a run whose presentverify line reports stale frames.
VERIFY_PRESENT=1
# --sb-live (2026-09-22): passed through to the hub dosbox-run.sh's own --sb-live -- DOSBox-X's
# Sound Blaster really plays (no -silent, SB detection on). Without it the SB is switched off and
# every SB PCM device-side figure is meaningless (PLAN.md step 8, DSPV1-3).
# 2026-11-04: it also decides the MIDI mode. Without it pcm_irqs=0, so MIDI falls back to
# midi_tick=poll, and the audio status has no late_writes= at all -- gatebar.py then VOIDs the
# cell on "missing late_writes". Any cell scored like a gate cell (gatebar.py, the capture
# checks' K5) needs --sb-live, as the 486 runs with a live SB and the ISR MIDI replay.
SB_LIVE=0
# --no-host-input (2026-09-24, hub ee910e5): the caller asserts that nothing on the host drives this
# run's input (an AutoPilot, a freeze gate). Only then may a run with a display share the host lock
# at fixed cycles: host-driven input (xdotool clicks) lands at wall-clock times, which breaks
# fixed-cycles determinism under load, so such a run takes the lock EXCLUSIVE.
HOST_INPUT="${DOSBOX_HOST_INPUT:-}"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --fixed-timestep) FIXED_TIMESTEP=1; shift ;;
        --no-fine-timing) FINE_TIMING=0; shift ;;
        --interactive) INTERACTIVE=1; shift ;;
        --timeout) TIMEOUT_S="$2"; TIMEOUT_EXPLICIT=1; shift 2 ;;
        --env) ENVS+=(--env "$2"); shift 2 ;;
        --include-extra) EXTRA_INCLUDES+=("$2"); shift 2 ;;
        --conf) CONF_OVERRIDE="$2"; shift 2 ;;
        --ags-arg) AGS_ARGS+=("$2"); shift 2 ;;
        --screen-series) SERIES_DIR="$2"; INTERACTIVE=1; shift 2 ;;
        --series-every) SERIES_EVERY="$2"; shift 2 ;;
        --freeze-capture) FREEZE_DIR="$2"; INTERACTIVE=1; shift 2 ;;
        --no-verify-present) VERIFY_PRESENT=0; shift ;;
        --allow-odd-cfg-name) ALLOW_ODD_CFG=1; shift ;;
        --no-host-input) HOST_INPUT=none; shift ;;
        --sb-live) SB_LIVE=1; shift ;;
        *) usage ;;
    esac
done


# after parsing, so an explicit --env DOSAGS_FIXED_TIMESTEP=... still wins
if [[ $FIXED_TIMESTEP -eq 1 ]]; then
    ENVS+=(--env DOSAGS_FIXED_TIMESTEP=1)
fi
# Fine timing (ags 0315) is off in the engine by default and on for every benchmark cell by default here, as in
# run-hw.sh; --no-fine-timing opts out, and an explicit --env DOSAGS_TICKSTATS_FINE=... wins.
if [[ $FINE_TIMING -eq 1 ]]; then
    _have_ft=0
    for _e in "${ENVS[@]:-}"; do [[ "$_e" == DOSAGS_TICKSTATS_FINE=* ]] && _have_ft=1; done
    [[ $_have_ft -eq 1 ]] || ENVS+=(--env DOSAGS_TICKSTATS_FINE=1)
fi
# the verifier is a default, not a mandate: an explicit --env DOSAGS_PRESENT_VERIFY=... wins
if [[ $VERIFY_PRESENT -eq 1 ]]; then
    _have_pv=0
    for _e in "${ENVS[@]:-}"; do [[ "$_e" == DOSAGS_PRESENT_VERIFY=* ]] && _have_pv=1; done
    [[ $_have_pv -eq 1 ]] || ENVS+=(--env DOSAGS_PRESENT_VERIFY=1)
fi
# --include-extra PATH[:NAME]: resolve each staged name and refuse a misnamed ACSETUP variant before
# anything runs (a refused cell costs nothing; a misnamed one produces a result for the wrong fixture).
EXTRA_SRC=(); EXTRA_NAME=()
for _x in "${EXTRA_INCLUDES[@]:-}"; do
    [[ -n "$_x" ]] || continue
    if [[ "$_x" == *:* ]]; then _src="${_x%:*}"; _name="${_x##*:}"; else _src="$_x"; _name="$(basename "$_x")"; fi
    [[ -f "$_src" ]] || { echo "run-dosbox.sh: --include-extra $_src not found" >&2; exit 1; }
    _name="${_name^^}"
    if [[ "$_name" == *ACSETUP*.CFG && "$_name" != ACSETUP.CFG && $ALLOW_ODD_CFG -eq 0 ]]; then
        echo "run-dosbox.sh: REFUSED: --include-extra $_x would stage as $_name, which the engine never reads (it reads ACSETUP.CFG only). Use $_src:ACSETUP.CFG, or --allow-odd-cfg-name if this is intended." >&2
        exit 2
    fi
    EXTRA_SRC+=("$_src"); EXTRA_NAME+=("$_name")
done
HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HARNESS_DIR/../.." && pwd)"
GAMES_DIR="$HARNESS_DIR/games/$PKG"
AGS_EXE="${AGS_EXE:-$REPO_ROOT/build/ags/ags.exe}"
CWSDPMI_EXE="$REPO_ROOT/vendor/cwsdpmi/cwsdpmi.exe"
DOSBOX_RUN="$REPO_ROOT/tools/dosbox-run.sh"

[[ -f "$AGS_EXE" ]] || { echo "run-dosbox.sh: $AGS_EXE not found -- run 'make build-ags' first" >&2; exit 1; }
# The exe is staged under its own basename and RUN.BAT calls it by that name; DOS only runs an 8.3
# name, so `AGS_EXE=.../ags-0209-clean.exe` ends in "Bad command or filename" at a DOS prompt (an
# interactive run then idles until its timeout). Copy a pinned binary to .../ags.exe instead.
if ! [[ "$(basename "$AGS_EXE")" =~ ^[A-Za-z0-9_-]{1,8}\.[Ee][Xx][Ee]$ ]]; then
    echo "run-dosbox.sh: AGS_EXE basename '$(basename "$AGS_EXE")' is not a DOS 8.3 name (<=8 chars before .exe) -- DOS cannot run it; copy it to e.g. .../ags.exe" >&2
    exit 2
fi
[[ -f "$CWSDPMI_EXE" ]] || { echo "run-dosbox.sh: $CWSDPMI_EXE not found" >&2; exit 1; }
[[ -x "$DOSBOX_RUN" ]] || { echo "run-dosbox.sh: $DOSBOX_RUN not found" >&2; exit 1; }

shopt -s nullglob
AGS_PKG=("$GAMES_DIR"/*.ags)
shopt -u nullglob
[[ -f "${AGS_PKG[0]:-}" ]] || { echo "run-dosbox.sh: no .ags package under $GAMES_DIR -- run build-package.sh first" >&2; exit 1; }

# dosbox-run.sh's own CWSDPMI auto-include resolves relative to ITS OWN
# location (a hub script under .sdl-dos-ports/shared/tools/), so it
# never finds a per-port vendor/cwsdpmi/ automatically -- override
# explicitly. See ~/.claude memory reference_sibling_repos_and_rig_config.md's
# doskutsu equivalent; the same gap applies to every port.
export CWSDPMI="$CWSDPMI_EXE"

# AGS_EXTRA_ARGS: extra engine CLI args, appended to the fixed set below.
# Added for patch 0108's restore-path proof (--loadsavedgame 999), which
# needs to exercise try_restore_save() rather than just check a file
# appeared; generally useful for any one-off that needs a real engine flag.
# --ags-arg (above) folds in here too, after AGS_EXTRA_ARGS if both are set.
EXTRA_ARGS_STR="${AGS_EXTRA_ARGS:-}"
if [[ ${#AGS_ARGS[@]} -gt 0 ]]; then
    EXTRA_ARGS_STR="${EXTRA_ARGS_STR:+$EXTRA_ARGS_STR }${AGS_ARGS[*]}"
fi
ARGS=(--exe "$AGS_EXE" --include "${AGS_PKG[0]}" --args "--test --log-stdout=+mgs:all --user-data-dir c:\\ ${EXTRA_ARGS_STR}" --keep-stage)
if [[ -n "$CONF_OVERRIDE" ]]; then
    [[ -f "$CONF_OVERRIDE" ]] || { echo "run-dosbox.sh: --conf $CONF_OVERRIDE not found" >&2; exit 1; }
    ARGS+=(--conf "$CONF_OVERRIDE")
else
    ARGS+=(--fast)
fi
# NOT "${ENVS[@]:-}" spliced into the array literal above -- for an array,
# the ":-" default triggers even when the array is merely EMPTY (not
# unset), inserting one bogus empty-string element that dosbox-run.sh's own
# arg parser then rejects as "unknown arg". Appending separately with a
# bare "${ENVS[@]}" (guarded by the length check) avoids that.
if [[ ${#ENVS[@]} -gt 0 ]]; then
    ARGS+=("${ENVS[@]}")
fi
[[ $SB_LIVE -eq 1 ]] && ARGS+=(--sb-live)
# Extra includes are added after the cleanup trap below: a renamed one is copied into a private
# directory first (dosbox-run.sh stages a file under its own uppercased basename).

# Cleanup on any exit (2026-09-23), including a TERM from the caller's own timeout (gate-alias.sh
# wraps every run in `timeout 900`): take down this run's watchers, its own DOSBox-X and its Xvfb.
# Before this, a killed runner left its freeze watcher polling forever as an orphan (found after
# gate-0209's first run: pid 90911, still running 20 minutes later).
XVFB_PID=""; RUN_PID=""; FRZ_PID=""; CAP_PID=""; WATCH_PID=""
cleanup() {   # every step `|| true`: under set -e a failed kill (already gone) would end the trap early
    local _s="" _w
    if [[ -n "$RUN_PID" ]]; then _s="$(own_stage 2>/dev/null || true)"; fi
    for _w in "$FRZ_PID" "$CAP_PID" "$WATCH_PID"; do
        if [[ -n "$_w" ]]; then kill "$_w" 2>/dev/null || true; fi
    done
    if [[ -n "$_s" ]]; then pkill -TERM -f "dosbox-x .*-c MOUNT C $_s( |\$)" 2>/dev/null || true; fi
    if [[ -n "$RUN_PID" ]]; then kill "$RUN_PID" 2>/dev/null || true; fi
    if [[ -n "$XVFB_PID" ]]; then
        kill "$XVFB_PID" 2>/dev/null || true
        # wait until our Xvfb has EXITED before the display (fd 5) goes: the next owner would otherwise
        # start its Xvfb into this one's dying socket and capture nothing (the hub's test, b79e724)
        for _i in $(seq 1 100); do kill -0 "$XVFB_PID" 2>/dev/null || break; sleep 0.1; done
        wait "$XVFB_PID" 2>/dev/null || true
    fi
    if declare -F dosbox_lock_release >/dev/null; then dosbox_lock_release; fi
    if [[ -n "${EXTRA_DIR:-}" ]]; then rm -rf "$EXTRA_DIR" || true; fi
    return 0
}
trap cleanup EXIT
trap 'exit 143' TERM INT HUP

EXTRA_DIR=""
for _i in "${!EXTRA_SRC[@]}"; do
    _src="${EXTRA_SRC[$_i]}"; _name="${EXTRA_NAME[$_i]}"
    _base="$(basename "$_src")"
    if [[ "${_base^^}" == "$_name" ]]; then
        ARGS+=(--include "$_src")
    else
        [[ -n "$EXTRA_DIR" ]] || EXTRA_DIR="$(mktemp -d)"
        [[ ! -e "$EXTRA_DIR/$_name" ]] || { echo "run-dosbox.sh: two --include-extra files would both stage as $_name" >&2; exit 2; }
        cp "$_src" "$EXTRA_DIR/$_name"
        ARGS+=(--include "$EXTRA_DIR/$_name")
    fi
done

# An interactive DOSBox-X does not exit when the game does, and the hub's dosbox-run.sh holds the
# host-wide lock EXCLUSIVE for any --interactive run -- so a run that never ends idles the whole
# host until its timeout (a lab run held it ~4.5 min after its measurement, 2026-09-23). Every
# interactive run is stopped once the engine's manifest is complete (the watcher below), and one
# with no way to end on its own -- no DOSAGS_TAS_AUTO_EXIT_TICK and no explicit --timeout -- is
# refused. (AGS Quest's autopilot quits on its own; pass --timeout with it anyway.)
if [[ $INTERACTIVE -eq 1 && $TIMEOUT_EXPLICIT -eq 0 ]]; then
    _have_ae=0
    for _e in "${ENVS[@]:-}"; do [[ "$_e" == DOSAGS_TAS_AUTO_EXIT_TICK=* ]] && _have_ae=1; done
    if [[ $_have_ae -eq 0 ]]; then
        echo "run-dosbox.sh: an --interactive/--freeze-capture/--screen-series run needs --env DOSAGS_TAS_AUTO_EXIT_TICK=N or an explicit --timeout: it holds the host-wide DOSBox-X lock exclusively until it ends" >&2
        exit 2
    fi
fi
# Host-wide DOSBox-X lock (hub library dosbox-lock-lib.sh via ./dosbox-lock.sh, 2026-09-24): taken
# HERE, for every run, before the display check and -- the point of taking it here rather than inside
# dosbox-run.sh -- BEFORE `timeout $TIMEOUT_S` starts, so --timeout measures the run, not the queue
# (a run queued behind other workers used to be killed before it ever started). The mode is the one
# dosbox-run.sh would pick: EXCLUSIVE for a screen capture, --interactive or --sb-live at cycles=max;
# SHARED for a plain functional run, and for ANY run at FIXED cycles (`cycles = fixed N` in --conf:
# deterministic whatever the host load, hub bb5482c). A no-op inside a gate or series that already
# holds it. DOSBOX_LOCK_HELD=1 then tells dosbox-run.sh not to take it again. Released by cleanup().
source "$HARNESS_DIR/dosbox-lock.sh"
_has_display=0; [[ -n "$FREEZE_DIR" || -n "$SERIES_DIR" || $SB_LIVE -eq 1 || $INTERACTIVE -eq 1 ]] && _has_display=1
if dosbox_conf_fixed_cycles "$CONF_OVERRIDE" && { [[ $_has_display -eq 0 || "$HOST_INPUT" == "none" ]]; }; then
    dosbox_lock_series run-dosbox.sh shared || exit $?
elif [[ -n "$FREEZE_DIR" || -n "$SERIES_DIR" || $SB_LIVE -eq 1 || $INTERACTIVE -eq 1 ]]; then
    dosbox_lock_series run-dosbox.sh || exit $?
else
    dosbox_lock_series run-dosbox.sh shared || exit $?
fi
if [[ $INTERACTIVE -eq 1 ]]; then
    DISPLAY_NUM="${DOSBOX_DISPLAY_NUM:-211}"
    export DOSBOX_DISPLAY=":$DISPLAY_NUM"
    # The display, per the hub's pattern (tooling.md, b79e724), taken AFTER the host lock:
    # 1. hold display N's flock (fd 5) in this shell, so a second cell pinned to N waits here;
    # 2. start our own Xvfb (lock fds closed) only while holding it, and wait until THAT pid answers;
    # 3. run dosbox-run.sh with DOSBOX_DISPLAY_HELD=1 (it must not take the flock again);
    # 4. cleanup kills our Xvfb and WAITS for it to exit;  5. our exit releases fd 5.
    if ! dbxlock_display_acquire "$DISPLAY_NUM" >/dev/null; then
        echo "run-dosbox.sh: display $DOSBOX_DISPLAY still held by another cell after ${DOSBOX_LOCK_WAIT:-3600}s; not running" >&2
        exit 75
    fi
    export DOSBOX_DISPLAY_HELD=1
    # We hold the display, so any DOSBox-X window already on it is an orphan of a killed run, and it
    # would land in our root-window captures (gate-0209's gui B frames were a DOS prompt).
    if xdpyinfo -display "$DOSBOX_DISPLAY" >/dev/null 2>&1 \
       && xwininfo -display "$DOSBOX_DISPLAY" -root -children 2>/dev/null | /usr/bin/grep -q '("dosbox-x"'; then
        echo "run-dosbox.sh: an orphaned DOSBox-X window is on $DOSBOX_DISPLAY -- refusing (it would land in our captures); stop it" >&2
        exit 1
    fi
    if ! xdpyinfo -display "$DOSBOX_DISPLAY" >/dev/null 2>&1; then
        # lock fds closed: an Xvfb that inherits fd 8 (host lock) or fd 5 (display) holds them for its
        # whole life (a kept-alive Xvfb held the host lock shared and stalled every writer, 2026-09-24)
        Xvfb "$DOSBOX_DISPLAY" -screen 0 1280x1024x24 4>&- 5>&- 6>&- 7>&- 8>&- 9>&- >/dev/null 2>&1 &
        XVFB_PID=$!
        for _i in $(seq 1 100); do
            kill -0 "$XVFB_PID" 2>/dev/null || { echo "run-dosbox.sh: Xvfb on $DOSBOX_DISPLAY exited at start" >&2; exit 1; }
            xdpyinfo -display "$DOSBOX_DISPLAY" >/dev/null 2>&1 && break
            sleep 0.1
        done
    fi
    ARGS+=(--interactive)
fi

RUN_LOG="$(mktemp)"
# own_stage (2026-09-23): the stage directory of THIS run's own DOSBox-X -- the dosbox-x process
# that descends from the runner launched below (RUN_PID), never the first match in `ps`. Several
# workers now run DOSBox-X in parallel; the old first-match lookup could watch, photograph and
# kill another run's emulator (a foreign -silent run overlapped a freeze-capture gate, 2026-09-23).
own_stage() {
    [[ -n "$RUN_PID" ]] || return 0
    ps -eo pid=,ppid=,args= | awk -v root="$RUN_PID" '
        { pid = $1; ppid = $2; $1 = ""; $2 = ""; sub(/^ +/, ""); par[pid] = ppid; cmd[pid] = $0 }
        END {
            for (p in cmd) {
                if (cmd[p] !~ /^dosbox-x .*-c MOUNT C \/tmp\/dos-port-dosbox\./) continue
                q = p
                for (n = 0; n < 64 && q != "" && q != "0" && q != "1"; n++) {
                    if (q == root) {
                        match(cmd[p], /\/tmp\/dos-port-dosbox\.[A-Za-z0-9]*/)
                        print substr(cmd[p], RSTART, RLENGTH); exit
                    }
                    q = par[q]
                }
            }
        }'
}
if [[ -n "$SERIES_DIR" || -n "$FREEZE_DIR" ]]; then
    command -v import >/dev/null 2>&1 || { echo "run-dosbox.sh: --screen-series/--freeze-capture need ImageMagick's import" >&2; exit 1; }
fi
timeout "$TIMEOUT_S" "$DOSBOX_RUN" "${ARGS[@]}" > "$RUN_LOG" 2>&1 &
RUN_PID=$!
if [[ -n "$FREEZE_DIR" ]]; then
    mkdir -p "$FREEZE_DIR/frames"; rm -f "$FREEZE_DIR"/frames/* "$FREEZE_DIR/.stop" "$FREEZE_DIR/stage"
    (   declare -A seen
        while [[ ! -f "$FREEZE_DIR/.stop" ]]; do
            _fs="$(own_stage)"
            if [[ -n "$_fs" ]]; then
                echo "$_fs" > "$FREEZE_DIR/stage"
                for f in "$_fs"/FRZ*.TXT; do
                    [[ -e "$f" ]] || continue
                    b="$(basename "$f" .TXT)"
                    [[ -n "${seen[$b]:-}" ]] && continue
                    seen[$b]=1
                    sleep 0.4     # inside the engine's spin, screen static
                    import -display "$DOSBOX_DISPLAY" -window root "$FREEZE_DIR/frames/$b.png" >/dev/null 2>&1 || true
                    cp "$f" "$FREEZE_DIR/frames/$b.txt"
                done
            fi
            sleep 0.1
        done ) &
    FRZ_PID=$!
fi
if [[ -n "$SERIES_DIR" || -n "$FREEZE_DIR" ]]; then
    if [[ -n "$SERIES_DIR" ]]; then
    mkdir -p "$SERIES_DIR/frames"; rm -f "$SERIES_DIR"/frames/* "$SERIES_DIR/.stop"
    (   i=0
        while [[ ! -f "$SERIES_DIR/.stop" ]]; do
            i=$((i + 1))
            import -display "$DOSBOX_DISPLAY" -window root \
                "$SERIES_DIR/frames/$(printf %05d "$i")_$(date +%H%M%S.%3N).png" >/dev/null 2>&1 || true
            sleep "$SERIES_EVERY"
        done ) &
    CAP_PID=$!
    fi
fi
if [[ $INTERACTIVE -eq 1 ]]; then
    # Interactive DOSBox-X does not exit when the program does. Find it by its own MOUNT
    # argument, wait for the engine's manifest to be complete, let the last frames land, then
    # stop it -- otherwise every series run costs the full timeout at a DOS prompt.
    (   for _ in $(seq 1 "$TIMEOUT_S"); do
            sleep 1
            _stage="$(own_stage)"
            [[ -n "$_stage" && -f "$_stage/RUNMANI.LOG" ]] || continue
            /usr/bin/grep -q 'RUNMANIFEST-END' "$_stage/RUNMANI.LOG" 2>/dev/null || continue
            sleep 3
            pkill -TERM -f "dosbox-x .*-c MOUNT C $_stage( |\$)" 2>/dev/null || true
            break
        done ) &
    WATCH_PID=$!
fi
RUN_RC=0; wait "$RUN_PID" 2>/dev/null || RUN_RC=$?
if [[ -n "$FREEZE_DIR" ]]; then
    touch "$FREEZE_DIR/.stop"; wait "$FRZ_PID" 2>/dev/null || true
    [[ -n "$SERIES_DIR" ]] || kill "$WATCH_PID" 2>/dev/null || true
fi
if [[ -n "$SERIES_DIR" ]]; then
    touch "$SERIES_DIR/.stop"; wait "$CAP_PID" 2>/dev/null || true
    kill "$WATCH_PID" 2>/dev/null || true
    python3 "$HARNESS_DIR/witness_sheet.py" "$SERIES_DIR/frames" --out "$SERIES_DIR/sheet.png" \
        --manifest "$SERIES_DIR/MANIFEST.json" --crop auto >&2 || true
fi

STAGE_DIR="$(grep -o '/tmp/dos-port-dosbox\.[A-Za-z0-9]*' "$RUN_LOG" | tail -1 || true)"
if [[ -z "$STAGE_DIR" ]]; then
    echo "run-dosbox.sh: could not determine the staged run directory" >&2
    cat "$RUN_LOG" >&2
    rm -f "$RUN_LOG"
    exit 1
fi
# The game must have run: a runner killed by --timeout while still queued for the DOSBox-X lock
# (the timeout counts the wait) leaves a stage with no STDOUT.TXT, and this used to exit 0 with it
# (seen 2026-09-23 behind an exclusive cell). Fail and say why.
if [[ ! -f "$STAGE_DIR/STDOUT.TXT" ]]; then
    echo "run-dosbox.sh: no STDOUT.TXT in $STAGE_DIR -- the game never ran (runner exit $RUN_RC; 124 = --timeout $TIMEOUT_S s expired; the lock is taken before the timeout starts)" >&2
    /usr/bin/grep -a 'waiting\|lock' "$RUN_LOG" >&2 || true
    rm -f "$RUN_LOG"
    exit 1
fi
rm -f "$RUN_LOG"

# one line, on stderr, so the verifier's answer is in front of whoever ran this
if [[ -f "$STAGE_DIR/STDOUT.TXT" ]]; then
    # `|| true`: with the verifier off (--no-verify-present) there is no such line, grep fails, and
    # under pipefail + set -e the script used to exit 1 here, before printing the stage dir
    # (found by dosags-lab-mmd, 2026-09-23).
    _pv="$(/usr/bin/grep -a 'DOS-PORT presentverify frames=' "$STAGE_DIR/STDOUT.TXT" | tail -1 | tr -d '\r' || true)"
    if [[ -n "$_pv" ]]; then echo "run-dosbox.sh: $_pv" >&2; fi
fi

echo "$STAGE_DIR"
