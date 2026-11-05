#!/usr/bin/env bash
# run-hw.sh -- run a built test package on the real vcctrl rig, the way
# ~/git/dosags's first real-hardware run (2026-09-11, HW-486-66, tag HW1)
# was actually done by hand. Automates that sequence so it doesn't have to
# be improvised again.
#
# Unlike run-dosbox.sh, this does NOT drive vcctrl-cell -- vcctrl-cell is
# shaped around doskutsu's own env-var+CFG-file-configured, no-CLI-args
# engine (see the hub's docs/hardware-testing.md "The orchestration layer"
# section). AGS.EXE takes real CLI args (--test --log-stdout=+mgs:all
# --user-data-dir) and needs shell stdout redirection, which is a
# different shape entirely -- this script stages a purpose-built RUN.BAT
# instead, via vcctrl's generic stage-file/send-file/get-file primitives
# (docs/hardware-testing.md's "Manual workflow").
#
# Usage:
#   ./run-hw.sh <package-name> [--tag TAG] [--dest DOS-DIR] [--power-on]
#                [--timeout SECONDS] [--env KEY=VALUE]... [--boot-profile N]
#                [--no-fixed-timestep]
#
#   --no-fine-timing     opt OUT of the SET DOSAGS_TICKSTATS_FINE=1 line (ags 0315; see FINE_TIMING below)
#   --no-fixed-timestep  opt OUT of the SET DOSAGS_FIXED_TIMESTEP=1 line this
#                     script emits into RUN.BAT by default (since 2026-09-16;
#                     see the FIXED_TIMESTEP comment below). Only for a
#                     correctness-only cell that deliberately wants the
#                     engine's own 1:1 logic/render default.
#
#   --tag TAG        DOS 8.3-safe run identity (default: an auto-generated
#                     one from the current time). Sets both DOSAGS_LOG_TAG
#                     (names RUNMANI.LOG -> <TAG>.LOG, patches/ags/0044)
#                     and DOS_PORT_LOG_TAG (names the shared SDL debug log
#                     LOGS\<TAG>SDL.LOG, shared/ SDL3-DOS backend) to the
#                     SAME value -- these are two independent env vars
#                     that happen to serve the same "tag this run" intent;
#                     see this run's own results/ writeup for why they are
#                     not (yet) bridged to one name.
#   --dest DOS-DIR    where the package lives on the target
#                     (default: profiles/dosags.yaml's target.dir)
#   --power-on        power on the rig if it's currently off, instead of
#                     refusing (mirrors vcctrl_common.ensure_powered)
#   --timeout SECONDS how long to wait for the run to finish before giving
#                     up and collecting whatever exists (default: 1200,
#                     since the first real run took ~433s of actual engine
#                     time but the console-mode-restore gap this script
#                     fixes below means a bare run used to look "stuck"
#                     for another ~10 min on a naive poll loop -- see
#                     KNOWN GAP below, now fixed at the RUN.BAT level)
#   --env KEY=VALUE   extra env var to SET in RUN.BAT before AGS.EXE runs
#                     (repeatable). A real, previously-missing gap: this
#                     script could only ever set DOSAGS_LOG_TAG/
#                     DOS_PORT_LOG_TAG, so testing any OTHER engine env
#                     var (DOSAGS_FIXED_TIMESTEP, patches/ags/0047, is the
#                     first real need) meant hand-editing a staged RUN.BAT
#                     by hand each time -- the same workaround patch
#                     0044's own real-hardware confirmation used for
#                     DOSAGS_TAS_AUTO_EXIT_TICK. No validation of KEY
#                     beyond "looks like an env var name" -- this writes
#                     whatever is given straight into RUN.BAT, same trust
#                     level as --tag/--dest already have.
#   --pre-line LINE   a DOS command emitted into RUN.BAT just before AGS.EXE (repeatable, in order;
#                     after the SET lines). Same trust level as --env: written as given.
#   --stdout-to PATH  AGS.EXE's stdout goes to PATH (e.g. a RAM disk) instead of STDOUT.TXT, and
#                     RUN.BAT copies it to STDOUT.TXT in the package dir right after the game exits,
#                     so collection is unchanged. Without either option RUN.BAT is byte-identical
#                     to before (2026-09-25, LAB-JOURNEYS 8.40 LOGRAM).
#   --post-line LINE  a DOS command emitted after the game exits and after the --stdout-to copy
#                     (repeatable, in order), before the SDL log copy and MODE12.
#   --collect NAME    an extra file (8.3 name, in the package dir) fetched with the usual set.
#   --boot-profile N  select CONFIG.SYS menu entry N (this rig: 1=PGSB
#                     default, 2=PGADLIB, 3=PGGUS, 4=VIBRA, 5=NET, 6=CLEAN
#                     -- g2k/README.TXT is the authority, not this comment)
#                     via vcctrl's select_boot_profile(), AFTER the file
#                     transfer and BEFORE RUN.BAT launches. Omit for the
#                     existing behavior (whatever send-file --return's own
#                     menu default is, PGSB on this rig). Added for S5 GUS
#                     real-hardware validation (2026-09-13) -- GUS audio
#                     needs PGGUS, which send-file's own reboot never
#                     selects on its own.
#
# KNOWN GAP THIS SCRIPT FIXES: the first real-hardware run's hand-written
# RUN.BAT never restored the console to a capture-friendly video mode
# after AGS.EXE exited, so the engine finished cleanly (confirmed after
# the fact from RUNMANI.LOG/AUTOPLT.LOG) while vcctrl's video capture read
# a perfectly healthy DOS prompt as "no picture" for ~10 more minutes --
# same class of gap vcctrl-cell's own finally-block mode-restore exists to
# prevent. This script's generated RUN.BAT ends with a MODE-restore step
# for exactly that reason -- see the RUN.BAT heredoc below.
#
# Requires: the vcctrl repo checked out as a sibling of this hub's clone,
# or VCCTRL_BIN pointing at its bin/vcctrl wrapper directly.
#
# --extra-file LOCAL:REMOTENAME (repeatable): stages one more file onto
# the rig alongside AGS.EXE/CWSDPMI.EXE/the package/RUN.BAT, via the same
# `vc stage-file ... --replace` call those already use. Added for the Game
# porting framework's own S7 need: a binary-only golden reference (no Wine
# rebuild script, no baked-in acsetup.cfg) needs `tools/port-game/
# layout.py`'s sound-on/sound-off ACSETUP.CFG variants staged explicitly,
# one per ABBA arm -- this script has no other way to get a second file
# onto the rig next to the package.
# A REMOTENAME matching *ACSETUP*.CFG that is not exactly ACSETUP.CFG, or an
# ACSETUP-named LOCAL staged under any other name, is REFUSED before anything
# touches the target (2026-09-26): the engine reads ACSETUP.CFG only, so such
# a cell silently runs a different fixture. --allow-odd-cfg-name lets it
# through for the rare intentional case.

set -euo pipefail

usage() { echo "Usage: $0 <package-name> [--tag TAG] [--dest DIR] [--power-on] [--timeout SECONDS] [--env KEY=VALUE]... [--boot-profile N] [--extra-file LOCAL:REMOTENAME]... [--allow-odd-cfg-name] [--no-fixed-timestep] [--gate] [--ags-arg ARG]... [--no-witness REASON]" >&2; exit 1; }
[[ $# -ge 1 ]] || usage
PKG="$1"; shift

TAG="RH$(date +%H%M%S)"
DEST=""
POWER_ON=0
TIMEOUT_S=1200
EXTRA_ENV=()
BOOT_PROFILE=""
EXTRA_FILES=()
# --ags-arg ARG (repeatable): one more command-line argument for AGS.EXE, appended after the
# fixed ones on the RUN.BAT line (e.g. --ags-arg --startr --ags-arg 3 starts Trilby's Notes in
# room 3). Nothing changes when it is not given. Added 2026-09-21 for the catalogue
# re-baseline's in-play cell, which has no AutoPilot and must not click through a menu.
AGS_ARGS=()
PRE_LINES=()     # --pre-line: DOS commands run just before AGS.EXE (2026-09-25, LOGRAM)
STDOUT_TO=""     # --stdout-to: where AGS.EXE's stdout goes before it is copied to STDOUT.TXT
POST_LINES=()    # --post-line: DOS commands run after the game (and the --stdout-to copy)
COLLECT_EXTRA=() # --collect: extra files fetched from the package dir with the usual set
# The PHYSICAL-SCREEN WITNESS (2026-09-21, operator's standing order): every cell saves frames of
# the actual screen during the timed run and builds one contact sheet to LOOK at, ON by default.
# Why: every other check (BENCH capture hashes, the AGS Quest PH0N hashes) reads the engine's own
# RAM frame, so a region the engine changed and never pushed to the screen -- "trails" -- passes
# all of them. The operator found the first one with a camera, twice, while a cell ran. A rate
# taken from a run whose sheet shows trails is void. --no-witness REASON turns it off and the
# reason is written to the run record; there is no silent way off.
WITNESS=1
WITNESS_WHY=""
# Fixed timestep (patches/ags/0047) is ON for every rig run by default
# since 2026-09-16 -- operator decision: the engine keeps its opt-in
# default, the benchmarking tooling enforces it. Every KPI cell since S0
# already passed --env DOSAGS_FIXED_TIMESTEP=1 by hand; a cell that
# forgot would have measured slow GAMEPLAY, not low fps (PLAN.md "Fixed
# timestep and the fps KPI"). --no-fixed-timestep is the explicit opt-out
# for a correctness-only cell; an explicit --env DOSAGS_FIXED_TIMESTEP=...
# always wins over this default (it is emitted after it in RUN.BAT, and
# DOS SET is last-writer-wins). tools/port-game/port_game.py check reads
# the engine's own "DOS-PORT fixed-timestep:" log line back from
# STDOUT.TXT, so the record shows what actually ran, not what was asked.
FIXED_TIMESTEP=1
# Fine timing (ags patch 0315): the engine leaves its per-phase/event/render timers OFF by default -- on the
# target they cost 0.69 ms/tick of logic (LAB-MMD 45.3) -- and DOSAGS_TICKSTATS_FINE=1 turns them on. Every
# benchmark cell here reads the per-phase figures, so this tooling sets it by default, exactly as it does fixed
# timestep. --no-fine-timing is the explicit opt-out (a cell measuring what a player runs); an explicit
# --env DOSAGS_TICKSTATS_FINE=... always wins (emitted after this line; DOS SET is last-writer-wins).
FINE_TIMING=1
# --gate: this cell is a GATE measurement, so enforce the gate window.
#
# The 40/40 plan judges whole-run tick_rate over 5000 ticks, but BENCH8
# scenes run for however many ticks BENCH.CFG's hold_ticks asks for. On one
# binary, one scene, the default 1040-tick run reported whole-run 36.39
# where the same binary reported 39.24 at 5000 -- a 2.8-point artefact of
# window length, large enough to pass or fail a gate on its own.
#
# Refusing here rather than recording it afterwards, for the same reason
# the build-stamp check moved to a pre-build `make build-dirty`: a check
# that prevents beats a check that diagnoses.
GATE=0
ALLOW_ODD_CFG=0
GATE_HOLD_TICKS=4960   # + SETTLE_TICKS(40) = the 5000-tick gate window
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag) TAG="$2"; shift 2 ;;
        --dest) DEST="$2"; shift 2 ;;
        --power-on) POWER_ON=1; shift ;;
        --timeout) TIMEOUT_S="$2"; shift 2 ;;
        --env) EXTRA_ENV+=("$2"); shift 2 ;;
        --boot-profile) BOOT_PROFILE="$2"; shift 2 ;;
        --extra-file) EXTRA_FILES+=("$2"); shift 2 ;;
        --no-fixed-timestep) FIXED_TIMESTEP=0; shift ;;
        --no-fine-timing) FINE_TIMING=0; shift ;;
        --gate) GATE=1; shift ;;
        --allow-odd-cfg-name) ALLOW_ODD_CFG=1; shift ;;
        --ags-arg) AGS_ARGS+=("$2"); shift 2 ;;
        --pre-line) PRE_LINES+=("$2"); shift 2 ;;
        --stdout-to) STDOUT_TO="$2"; shift 2 ;;
        --post-line) POST_LINES+=("$2"); shift 2 ;;
        --collect) COLLECT_EXTRA+=("$2"); shift 2 ;;
        --no-witness) WITNESS=0; WITNESS_WHY="$2"; shift 2 ;;
        *) usage ;;
    esac
done

# Diagnostic-only variables (ags patch 0195 and 0192): DOSAGS_BREAK_0193 re-breaks the present fix, DOSAGS_FREEZE_* stalls the engine,
# DOSAGS_PRESENT_VERIFY reads the surface twice per present. None may sit under a figure by accident: a cell that sets any of them
# must carry a tag beginning DIAG, which the record then reads as "diagnostic, no rate".
for _kv in "${EXTRA_ENV[@]:-}"; do
    case "${_kv%%=*}" in
        DOSAGS_BREAK_0193|DOSAGS_FREEZE_TICKS|DOSAGS_FREEZE_MS|DOSAGS_PRESENT_VERIFY)
            if [[ "$TAG" != DIAG* ]]; then
                echo "run-hw.sh: REFUSED -- ${_kv%%=*} is a diagnostic-only variable; a cell that sets it must be tagged DIAG* (got '$TAG')." >&2
                exit 2
            fi ;;
    esac
done
# An ACSETUP variant staged under any name but ACSETUP.CFG is never read by the engine: refuse it here,
# before anything touches the target (see --extra-file above).
for _kv in "${EXTRA_FILES[@]:-}"; do
    [[ -n "$_kv" ]] || continue
    _lb="$(basename "${_kv%%:*}")"; _rn="${_kv#*:}"; _rn="${_rn^^}"
    if [[ $ALLOW_ODD_CFG -eq 0 && "$_rn" != ACSETUP.CFG && ( "$_rn" == *ACSETUP*.CFG || "${_lb^^}" == *ACSETUP*.CFG ) ]]; then
        echo "run-hw.sh: REFUSED -- --extra-file $_kv stages as $_rn, which the engine never reads (it reads ACSETUP.CFG only). Use ${_kv%%:*}:ACSETUP.CFG, or --allow-odd-cfg-name if this is intended." >&2
        exit 2
    fi
done
# --gate enforcement: a BENCH.CFG staged by this cell must ask for the gate
# window. Checked before anything touches the target, so a mis-windowed gate
# cell costs nothing rather than producing a number that looks like a result.
if [[ $GATE -eq 1 ]]; then
    _gate_saw_cfg=0
    for _kv in "${EXTRA_FILES[@]:-}"; do
        [[ -n "$_kv" ]] || continue
        _local="${_kv%%:*}"
        _remote="${_kv##*:}"
        [[ "${_remote^^}" == "BENCH.CFG" ]] || continue
        _gate_saw_cfg=1
        _ht="$(sed -n 's/^hold_ticks=\([0-9]*\).*/\1/p' "$_local" | head -1)"
        if [[ "$_ht" != "$GATE_HOLD_TICKS" ]]; then
            echo "run-hw.sh: --gate REFUSED: $_local has hold_ticks=${_ht:-<unset>}, gate requires $GATE_HOLD_TICKS" >&2
            echo "run-hw.sh:   the gate judges whole-run tick_rate over 5000 ticks; a shorter run" >&2
            echo "run-hw.sh:   inflates or deflates it purely by window length (measured: 36.39 at" >&2
            echo "run-hw.sh:   1040 ticks vs 39.24 at 5000 on the same binary and scene)." >&2
            exit 2
        fi
    done
    if [[ $_gate_saw_cfg -eq 0 ]]; then
        echo "run-hw.sh: --gate REFUSED: no BENCH.CFG staged, so the run length is unverifiable" >&2
        exit 2
    fi
fi

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HARNESS_DIR/../.." && pwd)"
GAMES_DIR="$HARNESS_DIR/games/$PKG"
AGS_EXE="${AGS_EXE:-$REPO_ROOT/build/ags/ags.exe}"  # overridable: an A/B chain can name a saved binary instead of swapping this file
CWSDPMI_EXE="$REPO_ROOT/vendor/cwsdpmi/cwsdpmi.exe"
# S4 (Sound milestone): the full 128-program DMXOPL GM bank, hoisted into
# the hub by S3 and pulled in via this repo's own .sdl-dos-ports subtree.
# opl3_sink_load_bank()'s own contract makes this optional (a missing file
# just keeps the built-in 8-patch fallback) -- staged unconditionally here
# anyway, since a real-hardware MIDI validation cell wants the actual
# shipped bank exercised, not the fallback silently substituting for it.
OPL3BANK_DAT="$REPO_ROOT/.sdl-dos-ports/shared/audio/opl3bank.dat"
PROFILE="$REPO_ROOT/profiles/dosags.yaml"

VCCTRL_BIN="${VCCTRL_BIN:-$REPO_ROOT/../vcctrl/bin/vcctrl}"
[[ -x "$VCCTRL_BIN" ]] || { echo "run-hw.sh: $VCCTRL_BIN not found -- set VCCTRL_BIN" >&2; exit 1; }

if [[ -z "$DEST" ]]; then
    DEST="$(python3 -c "
import yaml
with open('$PROFILE') as f:
    d = yaml.safe_load(f)
print(d['target']['dir'])
")"
fi

[[ -f "$AGS_EXE" ]] || { echo "run-hw.sh: $AGS_EXE not found -- run 'make build-ags' first" >&2; exit 1; }
[[ -f "$CWSDPMI_EXE" ]] || { echo "run-hw.sh: $CWSDPMI_EXE not found" >&2; exit 1; }
[[ -f "$OPL3BANK_DAT" ]] || { echo "run-hw.sh: $OPL3BANK_DAT not found -- pull the .sdl-dos-ports subtree" >&2; exit 1; }
shopt -s nullglob
AGS_PKG=("$GAMES_DIR"/*.ags)
shopt -u nullglob
[[ -f "${AGS_PKG[0]:-}" ]] || { echo "run-hw.sh: no .ags package under $GAMES_DIR -- run build-package.sh first" >&2; exit 1; }
AGS_PKG_NAME="$(basename "${AGS_PKG[0]}" | tr '[:lower:]' '[:upper:]')"

echo "== run-hw.sh: $PKG tag=$TAG dest=$DEST =="

vc() { "$VCCTRL_BIN" "$@"; }

# Polls `vc file-status 1` until the current job's own "running" flag goes
# false, tolerating a transient failure in the STATUS CHECK ITSELF (a
# flaky ssh round-trip, a momentarily-null job during a daemon restart,
# etc.) rather than letting `set -e` kill the whole script over it --
# confirmed a real, repeated failure mode on 2026-09-11: the underlying
# vcctrl job was still genuinely progressing (later confirmed via a
# direct `vc file-status` check) both times this script's own bare
# `RUNNING="$(vc file-status 1 | python3 -c ...)"` one-liner aborted the
# script outright on some transient hiccup in that pipeline. A status
# check that fails to even PARSE is not evidence the job failed -- only
# a real "running": false is.
wait_for_job_done() {
    local max_wait_s="${1:-1800}" elapsed=0 running raw
    while (( elapsed < max_wait_s )); do
        # `vc file-status` exits non-zero for TWO different reasons: a
        # real CLI/parse failure (transient -- tolerate and keep polling,
        # which is this function's whole reason to exist, see the comment
        # above) and a successfully-parsed job whose own "ok" is false
        # (e.g. a file that "did not come back") -- a REAL, already-
        # finished failure, not a reason to keep polling. The original
        # `vc ... | python3 ... || echo UNKNOWN` form conflated the two:
        # with `set -o pipefail` active, the whole pipeline reads as
        # failed whenever vc's own exit code is nonzero, which discards
        # python's already-correct "False" parse and substitutes UNKNOWN
        # instead. Confirmed the hard way, 2026-09-15: a 72.8MB file that
        # failed to verify (a real send-file failure, exit code 1) left
        # this loop polling for the full max_wait_s (30 minutes) on a job
        # that had already stopped running minutes earlier. Capturing
        # vc's stdout via `|| true` neutralizes `set -e`/pipefail without
        # discarding the JSON vc already printed before its nonzero exit,
        # so a real, parseable "running": false is never masked by vc's
        # own exit code -- only a truly unparseable response still falls
        # through to UNKNOWN below, exactly as before.
        raw="$(vc file-status 1 2>/dev/null || true)"
        running="$(printf '%s' "$raw" | python3 -c 'import json,sys
try:
    print(json.load(sys.stdin)["job"]["running"])
except Exception:
    print("UNKNOWN")' 2>/dev/null || echo "UNKNOWN")"
        [[ "$running" == "False" ]] && return 0
        sleep 10
        elapsed=$(( elapsed + 10 ))
    done
    echo "wait_for_job_done: gave up after ${max_wait_s}s, still not settled" >&2
    return 1
}

# Polls the rig's own video capture for the run actually finishing, instead
# of blindly sleeping for the full budget every time regardless of when the
# game actually exits. Uses vcctrl_common.grab() (the shared capture
# primitive -- imported, not reimplemented) plus a small port of
# vcctrl-sweep's own StallTracker/sig_differs classification (changing/
# static/no-picture), read directly from harness/vcctrl-sweep rather than
# guessed -- that logic is NOT importable from there (vcctrl-sweep is a
# script, not a module; only grab() and its capture-infrastructure
# siblings were promoted to the shared bin/vcctrl_common.py, per that
# file's own comment). Ported rather than imported because reaching into
# a sibling repo's own CLI script via a loader hack is more fragile than
# a small, cited copy of an already-small, already-tested algorithm --
# vcctrl-sweep's own test suite (tests/test_core.py) is what caught the
# real regression this exists to avoid repeating: a no-picture stream
# scoring as "changing" for six minutes straight.
#
# Content-blind, unlike vcctrl-sweep's own at_prompt(): it does not try to
# read WHAT the static screen shows, only that it has stopped changing,
# because teaching this check AGS Quest's own screen content is not worth
# it for one harness. That means STILL_SECONDS has to clear the real
# walkthrough's own longest ordinary static stretch, not just be "safely
# non-zero" -- AutoPilot.asc's settle phase is "~3s of ticks" at NORMAL
# game speed, but this session's own HW10 run confirmed tick-counted
# durations match DOSBox-X exactly while real WALL-CLOCK time per tick on
# real 486 hardware runs roughly an order of magnitude slower (e.g. the
# input-latency phase: 11-24ms on DOSBox-X vs 223-224ms on HW-486-66,
# both HW8 and HW10) -- so a tick-scaled "~3s" pause can plausibly cost
# several times that in real seconds here. STILL_SECONDS=60 and
# MIN_WAIT_S=90 are a conservative first cut, not a measured threshold --
# exactly the "pick a real STILL_SECONDS threshold for THIS package" this
# script's own prior version left as a follow-up once it had run enough
# times to have real data; both are safe to tighten later against actual
# HW9/HW10-style timing once more real runs exist. Falls back to
# max_wait_s unchanged (same behavior as the old unconditional sleep) if
# the screen never settles -- this makes completion detection faster, it
# does not remove the ceiling.
wait_for_stable_screen() {
    local max_wait_s="$1"
    VCCTRL_DIR="$(dirname "$VCCTRL_BIN")" VCCTRL_BIN="$VCCTRL_BIN" HARNESS_DIR="$HARNESS_DIR" WITNESS_DIR="${WITNESS_DIR:-}" MAX_WAIT_S="$max_wait_s" WAIT_LOCK_OWNER="run-hw-$TAG" python3 <<'PYEOF'
import os, sys, time, shutil, subprocess, datetime

sys.path.insert(0, os.environ["VCCTRL_DIR"])
import vcctrl_common as vcc

POLL_SECONDS = float(os.environ.get("RUNHW_POLL_S", 8))   # was 15; the witness wants a frame (and a camera shot) at least every 8 s
STILL_SECONDS = float(os.environ.get("RUNHW_STILL_S", 60))
MIN_WAIT_S = float(os.environ.get("RUNHW_MIN_WAIT_S", 90))
max_wait_s = float(os.environ["MAX_WAIT_S"])

sys.path.insert(0, os.environ["HARNESS_DIR"])
import witness_keep
WIT = os.environ.get("WITNESS_DIR", "")
_poll_no = 0

# RUNHW_KEEPALIVE_S (2026-09-22, hang investigation, opt-in -- 0/unset disables this
# entirely, unchanged behavior for every cell that does not ask for it): a periodic
# no-op keystroke meant to prevent the "get-file refused 3x, screen=ready-prompt" dead-
# link hang (PLAN.md, HARDWARE.md "vcctrl rig ... post-collection dead-link hang"),
# reproduced both on a slow game genuinely still executing for ~17 minutes and on a fast
# fixture held at an idle DOS prompt for 21 minutes with zero keystrokes -- the common
# ingredient in both is an extended stretch with no INPUT activity (the periodic
# ctrl+alt+delete the collection retry loop already sends did not, by itself, prevent
# it, but this wait loop currently sends literally nothing at all). Interval chosen
# comfortably under the shortest observed gap to a hang (bench8's ~11 min of active
# retry-loop cycling; Shards' ~17 min): 300s (5 min).
#
# SAFETY: a keystroke sent to a running SDL3-DOS game is REAL INPUT, not a no-op --
# this is the same rule hw_guard.py's verify_input() already lives by ("NEVER sent
# while one may be alive"). This loop cannot tell from its own frame-signature diff
# alone whether "static" means "the game exited" or "the game's idle title screen
# hasn't moved yet" (that ambiguity is the entire reason MIN_WAIT_S/STILL_SECONDS
# exist). So the keepalive does NOT trust "static" -- it reuses hw_guard.screen_reading(),
# the same OCR-classified, already-trusted check run-hw.sh itself gates guard recover on,
# and fires ONLY when that reads 'dos-prompt' or 'ready-prompt' (the game positively
# confirmed NOT running). The action itself is verify_input()'s own Caps Lock round-trip
# -- not a new "hope this is harmless" keystroke, but the one primitive this codebase has
# already established is safe when this same gate holds, and it doubles as a witness:
# every keepalive attempt is logged with what it saw and whether it fired.
KEEPALIVE_S = float(os.environ.get("RUNHW_KEEPALIVE_S", 0))
_keepalive_next = time.time() + KEEPALIVE_S if KEEPALIVE_S > 0 else None
if KEEPALIVE_S > 0:
    import hw_guard
    WAIT_LOCK_OWNER = os.environ["WAIT_LOCK_OWNER"]

    def _maybe_keepalive():
        # This function's caller (run-hw.sh, "$WAIT_LOCK_OWNER") holds the input lock
        # for the whole wait phase -- verify_input() acquires it under its OWN identity
        # (vcctrl's lock is exclusive by owner name, the same reason hw_guard.cmd_recover
        # refuses outright when someone else holds it), so it would be refused here
        # unheld first. Release, act, reacquire -- the same release/acquire dance
        # power_cycle_and_verify() already does elsewhere in hw_guard.py, not a new
        # pattern. A failed reacquire is reported, not swallowed: the caller's next
        # locked action (typing at the prompt) would surface it anyway, but silently
        # limping on here would blur which step actually lost the lock.
        global _keepalive_next
        now = time.time()
        if _keepalive_next is None or now < _keepalive_next:
            return
        _keepalive_next = now + KEEPALIVE_S
        screen = hw_guard.screen_reading()
        if screen not in ("dos-prompt", "ready-prompt"):
            print("  keepalive: skipped -- screen reads '%s', not confirmed idle" % screen)
            return
        subprocess.run([os.environ["VCCTRL_BIN"], "lock", "release", "--as", WAIT_LOCK_OWNER],
                        capture_output=True, text=True)
        verified, raw = hw_guard.verify_input()
        r = subprocess.run([os.environ["VCCTRL_BIN"], "lock", "acquire", "--as", WAIT_LOCK_OWNER],
                            capture_output=True, text=True)
        reacquired = r.returncode == 0
        print("  keepalive: sent (screen='%s') verified=%s reacquired=%s" %
              (screen, verified, reacquired))
        if not reacquired:
            print("  keepalive: WARNING -- could not reacquire the input lock as %s: %s" %
                  (WAIT_LOCK_OWNER, (r.stdout or r.stderr).strip()[:200]))
else:
    def _maybe_keepalive():
        pass


def frame_signature(path):
    # Ported from vcctrl's harness/vcctrl-sweep (frame_signature) --
    # not importable from there, see this function's own caller-side
    # comment above.
    from PIL import Image
    im = Image.open(path).convert("L").resize((32, 24))
    return list(im.getdata())


def sig_differs(a, b, threshold=8):
    # Ported from vcctrl's harness/vcctrl-sweep (sig_differs). b must not
    # be None -- no-picture is a third state, handled by the caller
    # (StallTracker below), never treated as "different".
    if b is None:
        raise ValueError("sig_differs received a null signature")
    if a is None:
        return True
    diff = sum(1 for x, y in zip(a, b) if abs(x - y) > threshold)
    return diff > len(a) * 0.02


class StallTracker(object):
    # Ported from vcctrl's harness/vcctrl-sweep (StallTracker) -- three-
    # state classification of a poll: changing, static, or blind (no
    # picture). See that class's own docstring for the real regression
    # (a no-picture stream scoring as "changing" for six minutes) this
    # exists to not repeat.
    def __init__(self):
        self.last_sig = None
        self.still_since = None

    def update(self, sig, now=None):
        now = time.time() if now is None else now
        if sig is None:
            return {"state": "blind", "still": 0.0}
        changed = sig_differs(self.last_sig, sig)
        self.last_sig = sig
        if changed:
            self.still_since = None
        elif self.still_since is None:
            self.still_since = now
        still = 0.0 if self.still_since is None else now - self.still_since
        return {"state": "changing" if changed else "static", "still": still}


tracker = StallTracker()
t0 = time.time()
while True:
    elapsed = time.time() - t0
    if elapsed > max_wait_s:
        print("wait_for_stable_screen: gave up after %.0fs, never settled" % elapsed,
              file=sys.stderr)
        break
    # sleep in 2 s slices, sampling the capture card's state each time (witness/card-state.log)
    for _ in range(max(1, int(POLL_SECONDS // 2))):
        time.sleep(min(2.0, POLL_SECONDS))
        witness_keep.card_state(WIT, os.environ["VCCTRL_BIN"])
    elapsed = time.time() - t0
    try:
        shot, _mean = vcc.grab("run-hw-wait")
        _poll_no += 1
        witness_keep.keep(shot, _poll_no, WIT, os.environ["VCCTRL_BIN"])
        sig = frame_signature(shot) if shot else None
    except Exception as exc:
        print("  t+%5.1fs  grab failed (%s), treating as no-picture" % (elapsed, exc))
        sig = None
    st = tracker.update(sig)
    print("  t+%5.1fs  %s  still %.0fs" % (elapsed, st["state"], st["still"]))
    _maybe_keepalive()
    if elapsed >= MIN_WAIT_S and st["state"] == "static" and st["still"] >= STILL_SECONDS:
        print("  screen static for %ds past the %ds floor -- proceeding" %
              (STILL_SECONDS, MIN_WAIT_S))
        break
PYEOF
}

# witness_hold SECONDS -- what `sleep` was in the collection retry loop, but taking frames. That
# loop runs exactly while a game that outlived the stability heuristic is still going, which is
# when moving content is on screen.
witness_hold() {
    local secs="$1"
    if [[ -z "${WITNESS_DIR:-}" ]]; then sleep "$secs"; return; fi
    VCCTRL_DIR="$(dirname "$VCCTRL_BIN")" VCCTRL_BIN="$VCCTRL_BIN" HARNESS_DIR="$HARNESS_DIR" \
        WITNESS_DIR="$WITNESS_DIR" HOLD_S="$secs" python3 <<'PYEOF'
import os, sys, time
sys.path.insert(0, os.environ["VCCTRL_DIR"])
sys.path.insert(0, os.environ["HARNESS_DIR"])
import vcctrl_common as vcc
import witness_keep
end = time.time() + float(os.environ["HOLD_S"])
n = 0
while time.time() < end:
    try:
        shot, _m = vcc.grab("run-hw-wait")
    except Exception:
        shot = None
    n += 1
    witness_keep.keep(shot, n, os.environ["WITNESS_DIR"], os.environ["VCCTRL_BIN"])
    for _ in range(4):
        time.sleep(max(0.0, min(2.0, end - time.time())))
        witness_keep.card_state(os.environ["WITNESS_DIR"], os.environ["VCCTRL_BIN"])
PYEOF
}

# Operator maintenance window (hw_guard.py hold-set): checked BEFORE the
# first command that could touch the target -- including the power-state
# read just below, whose --power-on branch is a power action. A machine
# somebody switched off on purpose stays off.
VCCTRL_BIN="$VCCTRL_BIN" python3 "$HARNESS_DIR/hw_guard.py" hold-check >/dev/null \
    || { echo "run-hw.sh: REFUSED -- maintenance window in force (see above); nothing was sent to the target." >&2; exit 4; }

if [[ "$(vc power state | python3 -c 'import json,sys; print(json.load(sys.stdin)["power"]["on"])')" == "False" ]]; then
    if [[ $POWER_ON -eq 1 ]]; then
        echo "-- powering on --"
        vc power on
        sleep 60   # BIOS POST + boot-menu timeout + AUTOEXEC; not polled
                   # for below because there is no video signal at all
                   # until well into POST, and this margin was measured
                   # generous against the first real run's own boot.
    else
        echo "run-hw.sh: REFUSED -- rig is off. Pass --power-on to bring it up." >&2
        exit 2
    fi
fi

WORK="$(mktemp -d)"
# Also release this run's own input lock on ANY exit path, not just the
# happy path -- found 2026-09-16 (Shards depth_16_forced S16FRC1): the
# "input verification failed" REFUSED path below does `exit 1` before
# ever reaching the happy-path `vc lock release --as "run-hw-$TAG"`
# near the end of this script, leaving the lock held under this run's
# own tag indefinitely (until manually cleared with the matching --as).
# `|| true` matches that same call's own tolerance for "was never
# acquired" / "already released" -- this must never be what fails a
# cleanup trap.
trap 'rm -rf "$WORK"; vc lock release --as "run-hw-$TAG" >/dev/null 2>&1 || true' EXIT
# Deliberately NOT under $WORK, and NOT covered by the cleanup trap
# above: this script's own last line of stdout is this directory's
# path, matching run-dosbox.sh's "prints the staged dir so
# ./parse-results.py $(...) chains directly" convention -- a directory
# the EXIT trap had already deleted by the time that convention's own
# caller could read it defeats the whole point. Confirmed the hard way
# on a real HW7 run (2026-09-11): the script printed a path, exited 0,
# and the path was already gone.
OUT_DIR="$(mktemp -d)"
WITNESS_DIR=""
mkdir -p "$OUT_DIR/witness"
if [[ $WITNESS -eq 1 ]]; then
    WITNESS_DIR="$OUT_DIR/witness"
    mkdir -p "$WITNESS_DIR/frames" "$WITNESS_DIR/camera"
    echo "-- physical-screen witness ON: frames -> $WITNESS_DIR --"
else
    echo "WITNESS DISABLED for $TAG: ${WITNESS_WHY:-<no reason given>}" | tee "$OUT_DIR/witness/DISABLED.txt"
fi

# The MODE-restore line is the fix for the gap the first real run found:
# without it, AGS.EXE exiting leaves the console in a mode the capture
# stick cannot lock, and a perfectly finished run reads as "no picture"
# (looks exactly like a hang) for as long as nobody thinks to reboot and
# check the logs. C:\VGACAP is rig-wide capture tooling (present
# regardless of which port is under test), not dosags-specific.
#
# AGS.EXE is invoked with $AGS_PKG_NAME as an explicit positional argument,
# never bare -- a real, silent wrong-game-measured incident found the hard
# way, 2026-09-15: $DEST accumulates *.ags files across every game this
# script has ever staged there (nothing deletes an old one when a new
# package lands), and AGS's own game-file lookup (Common/game/
# main_game_file.cpp's FindGameData(), confirmed by reading it directly)
# picks the FIRST *.ags it finds enumerating the directory when no
# explicit path is given -- alphabetically, not by recency. A cell meant
# to measure a freshly-staged 32-bit game silently ran an old 8-bit game
# instead (NOTES.AGS sorts before SHARDS.AGS), producing a complete,
# clean, exit_code=0 RUNMANIFEST for the WRONG GAME -- confirmed only by
# checking STDOUT.TXT's own "Game title:" line against what was actually
# staged, which every future cell must keep doing regardless of this fix
# (this closes the specific silent-wrong-pick failure mode, it does not
# replace the identity check). datafile_argv accepts any non-"-"-prefixed
# argument in any position (main.cpp's own cmdline parser, confirmed by
# reading it), so this is a strict narrowing with no other behavior
# change.
EXTRA_ENV_LINES=""
if [[ $FIXED_TIMESTEP -eq 1 ]]; then
    EXTRA_ENV_LINES+="SET DOSAGS_FIXED_TIMESTEP=1"$'\n'
fi
if [[ $FINE_TIMING -eq 1 ]]; then
    EXTRA_ENV_LINES+="SET DOSAGS_TICKSTATS_FINE=1"$'\n'
fi
for kv in "${EXTRA_ENV[@]:-}"; do
    [[ -n "$kv" ]] && EXTRA_ENV_LINES+="SET ${kv}"$'\n'
done
for ln in "${PRE_LINES[@]:-}"; do
    [[ -n "$ln" ]] && EXTRA_ENV_LINES+="${ln}"$'\n'
done
STDOUT_DEST="STDOUT.TXT"; STDOUT_COPY=""
if [[ -n "$STDOUT_TO" ]]; then
    STDOUT_DEST="$STDOUT_TO"; STDOUT_COPY="COPY ${STDOUT_TO} STDOUT.TXT > NUL"$'\n'
    # the previous cell's STDOUT.TXT must not be collected as this one's before the copy lands
    EXTRA_ENV_LINES+="IF EXIST STDOUT.TXT DEL STDOUT.TXT"$'\n'
fi
for ln in "${POST_LINES[@]:-}"; do
    [[ -n "$ln" ]] && STDOUT_COPY+="${ln}"$'\n'
done
# The two DELs (2026-09-17): $DEST is shared by every package and vcctrl
# never deletes anything there. AUTOPLT.LOG is opened in APPEND mode, so a
# collected copy carried every earlier run's phases (readers had to find the
# last "phase=boot" block), and a PH0N.BMP left by an earlier cell of the
# SAME scene would pass this cell's capture hash without this run having
# drawn anything -- BENCH8's manifest calls that out. STDOUT.TXT is
# truncated by its redirect and <TAG>.LOG is fresh by construction.
# The SDL3-DOS backend's own trace (dos_port_dbg_log, unconditional) is
# written to LOGS\<TAG>SDL.LOG, NOT to $DEST's root -- and SDL caps the tag
# at 5 chars when composing that basename (SDL_dosdbg.c's shorttag[6]), so
# the name is the FIRST FIVE characters of $TAG, not $TAG. get-file fetches
# bare names out of $DEST, so for the whole life of this harness that trace
# has been written on every single run and fetched on none of them -- which
# is why "the flip instrumentation produces no output" was wrong: it
# produces output into a file nobody collects. Copy it up to $DEST's root
# here so the one existing get-file call brings it back with everything
# else (no extra reboot, no second --from). IF EXIST because a run that
# never reaches the video backend never creates it.
SDLLOG="${TAG:0:5}SDL.LOG"
# The RUNMANIFEST file's name on the target (2026-09-24). The engine (quit.cpp, patches/ags/0044)
# uppercases DOSAGS_LOG_TAG, keeps only [A-Z0-9_], and truncates to 8 characters. This script used
# $TAG.LOG verbatim, so a tag with a '-' (HW-MMD-0 -> HWMMD0.LOG) was never collected: every get-file
# came back not-ok, the loop took that for the post-transfer dead link, spent the run's one recovery
# on it, and stopped as a "second failure" -- round A's stop, which was not a hang.
MANIFEST_LOG="$(printf '%s' "$TAG" | tr 'a-z' 'A-Z' | tr -cd 'A-Z0-9_' | cut -c1-8).LOG"

cat > "$WORK/RUN.BAT" <<BATEOF
@ECHO OFF
CD $DEST
IF EXIST AUTOPLT.LOG DEL AUTOPLT.LOG
IF EXIST PH01.BMP DEL PH0?.BMP
SET DOSAGS_LOG_TAG=$TAG
SET DOS_PORT_LOG_TAG=$TAG
${EXTRA_ENV_LINES}AGS.EXE $AGS_PKG_NAME --test --log-stdout=+mgs:all --user-data-dir $DEST${AGS_ARGS[*]:+ ${AGS_ARGS[*]}} > ${STDOUT_DEST}
${STDOUT_COPY}IF EXIST LOGS\\${SDLLOG} COPY LOGS\\${SDLLOG} ${SDLLOG} > NUL
C:\VGACAP\MODE12
BATEOF
sed -i 's/$/\r/' "$WORK/RUN.BAT"
# Keep the exact RUN.BAT this cell staged (CRLF and all) in its results (coordinator 2026-09-25):
# the env, args and redirections a cell ran with are then read from the cell dir, not reconstructed.
cp "$WORK/RUN.BAT" "$OUT_DIR/RUN.BAT"

# ---- reboot guard (2026-09-17) -------------------------------------------
# Every step below that reboots the target is followed by a POSITIVE
# "the reboot took" witness, and a missing one triggers ONE automatic
# recovery -- see hw_guard.py's own header for the why (the post-FTP
# dead-PS/2-link hang of 2026-09-16 and 2026-09-17, which left the target
# at a finished mTCP log while this script reported success), the witness
# (LED POST/ready edges from the daemon's trace + an OCR read of the
# screen), and the recovery. The one rule that does not bend: the recovery
# runs verify-input, whose lock-key press reaches a running SDL3-DOS game
# as real input, so it is only ever reached from the two points where no
# game can be running -- after SEND (before RUN.BAT is typed) and after a
# collection that has ALREADY SUCCEEDED (the game has exited; files are in
# hand). A REFUSED collection attempt still just retries, as before.
GUARD="$HARNESS_DIR/hw_guard.py"
GUARD_STATE="$WORK/guard.state"
RECOVERY_REC="$OUT_DIR/RECOVERY.TXT"
guard() { VCCTRL_BIN="$VCCTRL_BIN" python3 "$GUARD" "$@"; }

# guard_return_reboot STEP SEQ0 -- call after a --return file job that
# completed OK. Two completed boots (into NET, and back) must have been
# seen since LED-trace sequence SEQ0.
guard_return_reboot() {
    local step="$1" seq0="$2" wjson
    echo "-- reboot witness ($step): 2 completed boots since LED seq $seq0 --"
    if wjson="$(guard witness --since-seq "$seq0" --need 2 --step "$step" --shot "$OUT_DIR/WITNESS-$step.jpg")"; then
        echo "   witnessed: $wjson"
        return 0
    fi
    echo "   NO WITNESS: $wjson" >&2
    guard recover --tag "$TAG" --step "$step" --seen "$wjson" --record "$RECOVERY_REC" --state "$GUARD_STATE" \
        || { echo "run-hw.sh: STOPPED at step '$step' -- the return reboot never took and the rig could not be recovered automatically (or this run had already used its one recovery). See $RECOVERY_REC." >&2; exit 3; }
    echo "   recovered -- resuming after '$step' (this cell is marked recovered in its run record)"
}

# NOTE: called from an `if !`, where bash suspends `set -e` for the whole
# function body -- so every stage-file carries its own `|| return`. A
# stage that failed silently would send the rest and leave the PREVIOUS
# cell's AGS.EXE on the target: a clean-looking run of the wrong binary.
stage_and_send() {
echo "-- staging --"
# --replace on every call: re-running this script (the normal case, not
# an edge case) always re-stages a previous run's own files under the
# same names, and vcctrl's own stage-file refuses that silently -- "two
# different files can mangle to one 8.3 name" -- unless told this is
# deliberate. It always is here: RUN.BAT in particular has a fresh tag
# baked in every single run.
vc stage-file "$AGS_EXE" AGS.EXE --replace || return 2
vc stage-file "$CWSDPMI_EXE" CWSDPMI.EXE --replace || return 2
vc stage-file "${AGS_PKG[0]}" "$AGS_PKG_NAME" --replace || return 2
vc stage-file "$OPL3BANK_DAT" OPL3BANK.DAT --replace || return 2
for kv in "${EXTRA_FILES[@]:-}"; do
    [[ -n "$kv" ]] || continue
    LOCAL="${kv%%:*}"
    REMOTE="${kv#*:}"
    [[ -f "$LOCAL" ]] || { echo "run-hw.sh: --extra-file $LOCAL not found" >&2; exit 1; }
    vc stage-file "$LOCAL" "$REMOTE" --replace || return 2
done
vc stage-file "$WORK/RUN.BAT" RUN.BAT --replace || return 2

echo "-- sending to $DEST (reboot x2) --"
SEND_SEQ0="$(guard seq)"
vc send-file --return --dest "$DEST"
# send-file returns immediately; poll file-status the same way
# populate-and-verify already does, rather than guessing a sleep.
wait_for_job_done
SEND_RAW="$(vc file-status 100 2>/dev/null || true)"
SEND_OK="$(printf '%s' "$SEND_RAW" | python3 -c 'import json,sys
try:
    print(json.load(sys.stdin)["job"]["ok"])
except Exception:
    print("UNKNOWN")' 2>/dev/null || echo "UNKNOWN")"
[[ "$SEND_OK" == "True" ]]
}

if ! stage_and_send; then
    # The send did not verify. Today's live case: the PREVIOUS cell's return
    # reboot had silently failed, the link was dead, and this send hung in
    # its own first reboot. No game is running at this point (RUN.BAT has
    # not been typed), so the recovery is safe; then the WHOLE step is
    # redone -- staged files and all -- rather than trusting a half-sent job.
    echo "run-hw.sh: send-file did not verify cleanly -- attempting the one automatic recovery, then re-sending" >&2
    echo "$SEND_RAW" >&2
    vc file-cancel >/dev/null 2>&1 || true
    guard recover --tag "$TAG" --step send --seen "send-file job did not verify (job.ok=$SEND_OK)" --record "$RECOVERY_REC" --state "$GUARD_STATE" \
        || { guard_rc=$?
             # A lock refusal and a transfer failure are DIFFERENT FACTS and
             # this line used to make a reader guess which one they held. On
             # 2026-09-19 it cost an hour: the daemon's own refusal already
             # said "input locked by '<owner>' since <t>", the guard repeated
             # it, and then this summary buried both under a transfer verdict
             # -- and the tail of the log is what anyone reads first.
             #
             # hw_guard returns 3 specifically for "lock held by someone
             # else". Lead with that when it is the cause, and keep the
             # transfer verdict as the second line rather than the headline.
             if [[ $guard_rc -eq 3 ]]; then
                 echo "run-hw.sh: REFUSED -- THE HARDWARE LOCK IS HELD BY ANOTHER OWNER." >&2
                 echo "           This is NOT a transfer fault. See the hw_guard line above for" >&2
                 echo "           the owner, hold duration and whether anything is inflight;" >&2
                 echo "           a hold with nothing inflight is stale. tests/harness/RUNNER-DEFAULTS.md" >&2
                 echo "           has the signature and the current workaround." >&2
                 echo "           (the send-file verification also failed, as a consequence)" >&2
             else
                 echo "run-hw.sh: REFUSED -- send-file did not verify cleanly and the rig could not be recovered." >&2
             fi
             echo "           See $RECOVERY_REC." >&2; exit 3; }
    stage_and_send || { echo "run-hw.sh: REFUSED -- send-file did not verify cleanly even after a recovery" >&2; echo "$SEND_RAW" >&2; exit 1; }
fi
echo "   all files verified byte-for-byte"
guard_return_reboot send "$SEND_SEQ0"

# send-file --return lands on the menu DEFAULT (PGSB on this rig), not
# necessarily the profile the test actually needs (e.g. PGGUS for GUS
# audio). --boot-profile N selects a different CONFIG.SYS menu entry here,
# AFTER the transfer (file transfer itself always needs NET, so this can't
# happen any earlier) and BEFORE RUN.BAT is typed. Uses vcctrl's own
# select_boot_profile() (bin/vcctrl_common.py) -- the same tested primitive
# reboot_into_net() uses for NET, just not previously wired into a CLI
# script. ready_timeout is widened past the 200s default: a profile whose
# own AUTOEXEC does an extra PicoGUS mode-change reboot round-trip (PGGUS
# does) measured slower than that on this rig (S5 GUS session, 2026-09-13).
if [[ -n "$BOOT_PROFILE" ]]; then
    echo "-- selecting boot profile $BOOT_PROFILE --"
    # select_boot_profile() is a BLIND, timed keyboard-menu selection (Ctrl-Alt-Del,
    # poll for the capslock POST-edge, burst digit+Enter within the CONFIG.SYS menu's
    # ~5s window, poll for the scrolllock RDYPULSE signal) -- a probabilistic action,
    # not a deterministic one, extensively documented as such across many past
    # sessions (PLAN-LOG.md: GUST1/GUSD1/GUSV1/GUSU1/GUSN1, 2026-09-13..15, historical
    # rate "1 success / 3 failures across four sessions" via a single blind attempt,
    # ranging up to "3-for-3 failed" in one session and "first attempt" in another --
    # genuine run-to-run variance in the real menu timing, not a bug in the primitive
    # itself). Confirmed again directly, 2026-09-22: 0/4 via a single attempt each,
    # 1/1 when the identical call was re-run standalone moments later (edge_s=18.42,
    # ready_s=2.70, prompt_s=0.79, landed cleanly) -- the primitive works, a single
    # shot at it does not reliably. RETRY_N=3 below trades a modest amount of time
    # (each attempt is a full reboot cycle, ~20-30s to the DOS prompt when it lands,
    # up to the 280s ready_timeout when it does not) for a much better aggregate
    # success rate than gambling on exactly one attempt, which is what every failure
    # above actually was. Not a fix for the underlying flakiness -- a harness-level
    # retry around a primitive that has never been made deterministic.
    BOOT_PROFILE_RETRY_N="${RUNHW_BOOT_PROFILE_RETRY_N:-3}"
    _bp_ok=0
    for _bp_attempt in $(seq 1 "$BOOT_PROFILE_RETRY_N"); do
        echo "   attempt $_bp_attempt/$BOOT_PROFILE_RETRY_N..."
        if VCCTRL_DIR="$(dirname "$VCCTRL_BIN")" BOOT_DIGIT="$BOOT_PROFILE" python3 <<'PYEOF'
import os, sys, json
sys.path.insert(0, os.environ["VCCTRL_DIR"])
import vcctrl_common as vcc
vcc.set_lock_owner("run-hw-bootprofile")
res = vcc.select_boot_profile(int(os.environ["BOOT_DIGIT"]), ready_timeout=280)
print("select_boot_profile ->", res)
sys.exit(0 if res else 1)
PYEOF
        then
            _bp_ok=1
            break
        fi
        echo "   attempt $_bp_attempt/$BOOT_PROFILE_RETRY_N missed (documented, expected occasionally -- retrying)"
    done
    if [[ $_bp_ok -ne 1 ]]; then
        echo "run-hw.sh: REFUSED -- boot profile $BOOT_PROFILE not selected after $BOOT_PROFILE_RETRY_N attempts" >&2
        exit 1
    fi
    echo "   boot profile selected -- caller is responsible for verifying it landed correctly (e.g. via SET), same as any other real-hardware step"
fi

echo "-- launching RUN.BAT --"
vc lock acquire --as "run-hw-$TAG"
vc type "CD $DEST" --as "run-hw-$TAG"
vc key enter --as "run-hw-$TAG"
sleep 1
vc type "RUN.BAT" --as "run-hw-$TAG"
vc key enter --as "run-hw-$TAG"

echo "-- waiting up to ${TIMEOUT_S}s for the console to return to text mode --"
# The MODE12 fix above means "picture, static, small/text-mode-shaped" is
# the completion signal. Used to be an unconditional `sleep $TIMEOUT_S`
# regardless of when the game actually exited -- a real, measured waste
# confirmed on this session's own HW10 run (finished in well under 500s
# real time, the script waited the full 1200s anyway). wait_for_stable_
# screen polls for that signal instead and returns as soon as it settles;
# see its own definition above for the completion criteria and why they
# are a conservative first cut, and it still falls back to the full
# TIMEOUT_S -- same "collect regardless" ceiling as before -- if the
# screen never settles.
T0=$(date +%s)
wait_for_stable_screen "$TIMEOUT_S"
WAIT_S=$(( $(date +%s) - T0 ))
echo "   waited ${WAIT_S}s -- proceeding to collect"

# REMOVED 2026-09-16 (40fps push step 2 follow-up, commit 5f86091): this
# used to run `vc verify-input --as "run-hw-$TAG"` here as a standalone
# BIOS-path liveness probe, immediately after wait_for_stable_screen
# returned, on the theory that a content-static screen might still be a
# S32B5-style wedge (PS/2 link died mid-run, screen never changed at
# all, a stale multi-day-old STDOUT.TXT silently "succeeded" as this
# run's own output) rather than a genuinely finished run. That check is
# GONE, not just moved, for two read-and-confirmed reasons:
#
# 1. It is structurally guaranteed to fail against ANY still-running
#    SDL3-DOS game, healthy or not -- confirmed by reading
#    vendor/SDL/src/video/dos/SDL_dosevents.c's DOSVESA_InitKeyboard():
#    it replaces the BIOS INT 9 (IRQ-1) handler outright (DOSKUTSU Phase
#    11, to stop CWSDPMI's real-mode reflection from double-servicing
#    IRQ-1 and overflowing the BIOS keyboard buffer), so the engine
#    "never reads BIOS keyboard state" by design. verify-input's own
#    Scroll-Lock LED round trip depends on exactly that BIOS path, so it
#    cannot succeed until the game has actually quit and
#    DOSVESA_QuitKeyboard() has restored it -- a wait_for_stable_screen
#    "settled" declaration (which only means the screen stopped visibly
#    changing, not that the game exited) says nothing about whether that
#    has happened yet. For any game slower than wait_for_stable_screen's
#    own ~150s earliest-possible settle point (confirmed real: 16-bit-
#    forced Shards of God settles there while still ~200s from finishing
#    its own title-screen fade), this check was GUARANTEED to
#    misdiagnose "still legitimately running" as "wedged" every time.
# 2. It is not even a safe no-op when it fails: the Scroll-Lock keypress
#    the LED round trip sends still physically reaches the target, and
#    since the engine reads every raw scancode unconditionally, it
#    lands as real input. Live evidence, same session: two REFUSED
#    reboot-chord attempts made against a still-running Shards cell
#    were immediately followed, in that cell's own STDOUT.TXT, by four
#    "Running on_key_press keycode 383" lines and then "Quitting the
#    game..." with NO RUNMANIFEST block -- i.e., the earlier version of
#    this exact check very likely ended a legitimately-still-running
#    cell early, not detected a wedge in one.
#
# The S32B5 failure mode this used to guard against is NOT reintroduced
# by removing it: `vc get-file --return` (below) needs its own reboot to
# fetch anything, and that reboot goes through the identical Scroll-Lock
# LED verification -- confirmed directly, same session, by two manual
# get-file calls against a still-running game both refusing cleanly
# ("the machine never reset -- Scroll Lock did not clear") rather than
# collecting anything. That was already true before this change; what
# was missing was this script actually CHECKING get-file's own result
# instead of assuming success (see the new check below) -- so the one
# unavoidable reboot this script already needs for collection is now
# the single, later, correctly-checked gate for "did this actually
# finish", instead of an earlier, redundant, unsafe standalone probe.
# See PLAN.md's "40fps push" section, "Step 2 follow-up, 2026-09-16" for
# the full investigation this is based on.

echo "-- collecting results --"
vc lock release --as "run-hw-$TAG" || true
# wait_for_stable_screen returning "settled" only means the screen
# stopped visibly changing -- for a game whose idle title screen goes
# static long before it actually finishes (the whole reason the
# verify-input probe above was removed), that can happen while the game
# still has most of its own tick budget left. A single get-file attempt
# right here would therefore often refuse (correctly -- see the check
# below) on the FIRST try for exactly that reason, even though this
# script was given a much larger --timeout precisely to cover it. Retry
# collection every GET_RETRY_INTERVAL_S until it succeeds or the same
# overall $TIMEOUT_S budget (tracked from $T0, set before
# wait_for_stable_screen above) is actually exhausted, instead of
# treating the first refusal as final. Each retry's own reboot attempt
# is the safe, non-destructive kind confirmed this session (S16FRC3): a
# refused reboot chord leaves the target exactly as it was, still
# running, not harmed -- so retrying costs nothing but time.
GET_RETRY_INTERVAL_S="${RUNHW_GET_RETRY_S:-60}"
# Auto-recovery of the post-transfer dead link (2026-09-21, C1A2: the game had exited, the screen was a DOS
# prompt, and this loop retried a refused get-file for 13 minutes). After AUTO_RECOVER_AFTER refusals, and ONLY
# if the screen positively reads as a DOS prompt, run the one guarded recovery. A still-running game shows a
# picture and legitimately refuses the reboot chord, so anything else sends nothing. The per-run state file
# (hw_guard recover --state) keeps this to ONE recovery per run, shared with the send-side witness.
AUTO_RECOVER_AFTER="${RUNHW_AUTO_RECOVER_AFTER:-3}"
GET_REFUSALS=0
# The daemon's pulled-file store keeps the LAST copy of every name ever
# fetched, and `pulled save` below hands one over whether or not THIS
# get-file fetched it -- a BENCH8 cell (which writes only PH01.BMP) came
# back with AGS Quest's PH02/PH03.BMP from the cell before it, and the
# check report listed their hashes as if they were this run's. Clear it
# first so an absent file stays absent.
vc pulled clear >/dev/null 2>&1 || true
while true; do
    GET_SEQ0="$(guard seq)"
    # The list below is audited against every file the program can write.
    # Anything absent from it is invisible no matter how good the instrument
    # is -- which is exactly how doskutsu's four-phase present bracket came
    # to record faithfully on every cell of the campaign and be read on
    # none of them. Sources, checked 2026-09-20:
    #   STDOUT.TXT     the redirect in RUN.BAT
    #   <TAG>.LOG      RUNMANIFEST (patches/ags/0044, CWD root)
    #   <TAG[0:5]>SDL.LOG  SDL3-DOS backend (SDL_dosdbg.c, LOGS/ subdir,
    #                  copied to root by RUN.BAT above)
    #   AUTOPLT.LOG    the fixture's AutoPilot module
    #   AGSSAVE.001    autopilot save
    #   PH0N.BMP       phase captures
    #   WARNINGS.LOG   Engine/debug/debug.cpp:364 -- script warnings, and
    #                  it is created ONLY when a warning is emitted, so its
    #                  absence is the good case and its presence is
    #                  something we have never once looked at
    # Not fetched since 2026-09-25: AUDIOPRB.LOG. ags 0061 (2026-09-14) moved the audioprb summary into the
    # manifest log, and every copy fetched after that (142 result dirs) was the same stale file left on the
    # target's disk (sha256 64659cba...), so it carried no data.
    # Deliberately not fetched: ags.log (needs file logging configured; we
    # pass --log-stdout) and script.log (debug-only script dump).
    vc get-file STDOUT.TXT AUTOPLT.LOG "$MANIFEST_LOG" "$SDLLOG" WARNINGS.LOG ${COLLECT_EXTRA[@]+"${COLLECT_EXTRA[@]}"} \
        AGSSAVE.001 PH01.BMP PH02.BMP PH03.BMP \
        --return --from "$DEST"
    wait_for_job_done
    # Same pattern as the send-file check above -- this call's own
    # success was never actually verified before (a real, separate gap
    # found while fixing the verify-input issue above): a refused/failed
    # get-file would previously fall through to `vc pulled save`
    # silently producing an empty or stale OUT_DIR and still exiting 0,
    # exactly the kind of silent-wrong-data failure S32B5 already burned
    # this script on once.
    GET_RAW="$(vc file-status 100 2>/dev/null || true)"
    # job.ok requires ALL 7 requested names to succeed, but AUTOPLT.LOG/
    # AGSSAVE.001/PH0N.BMP only exist for a game with an AutoPilot module
    # -- for any binary-only game (no AutoPilot at all) those 5 can NEVER
    # be fetched, so job.ok can never be true and this loop would run
    # until --timeout every single time, reporting a false REFUSED even
    # after STDOUT.TXT and the RUNMANIFEST log both verified cleanly
    # (live, this session: S32FI1 -- exit_code=0, real RUNMANIFEST, both
    # files fetched and size-verified at t+4245s, but job.ok=false kept
    # this loop going until the full 5400s --timeout). Check the two
    # files this script actually needs instead of the aggregate.
    GET_OK="$(printf '%s' "$GET_RAW" | TAG="$TAG" MANIFEST_LOG="$MANIFEST_LOG" python3 -c 'import json,os,sys
try:
    files = json.load(sys.stdin)["job"]["files"]
    by_name = {f["name"]: f.get("ok") for f in files}
    tag_log = os.environ["MANIFEST_LOG"]
    print(by_name.get("STDOUT.TXT") is True and by_name.get(tag_log) is True)
except Exception:
    print("UNKNOWN")' 2>/dev/null || echo "UNKNOWN")"
    [[ "$GET_OK" == "True" ]] && break

    GET_REFUSALS=$(( GET_REFUSALS + 1 ))
    if (( GET_REFUSALS >= AUTO_RECOVER_AFTER )); then
        SCREEN_NOW="$(guard screen 2>/dev/null | tail -1)"
        if [[ "$SCREEN_NOW" == "dos-prompt" || "$SCREEN_NOW" == "ready-prompt" ]]; then
            echo "-- $GET_REFUSALS refused collections and the screen reads '$SCREEN_NOW': the game has exited, so this is the dead link, not a running game -- one guarded recovery --" >&2
            guard recover --tag "$TAG" --step collect \
                --seen "get-file refused $GET_REFUSALS times after the game exited; screen=$SCREEN_NOW" \
                --record "$RECOVERY_REC" --state "$GUARD_STATE" \
                || { echo "run-hw.sh: STOPPED -- collection never took and the automatic recovery did not (or could not) run. See $RECOVERY_REC." >&2; exit 3; }
            GET_REFUSALS=0
            continue
        else
            echo "   screen reads '$SCREEN_NOW', not a DOS prompt: a game may still be running -- NOT recovering" >&2
        fi
    fi
    ELAPSED_TOTAL=$(( $(date +%s) - T0 ))
    if (( ELAPSED_TOTAL >= TIMEOUT_S )); then
        echo "run-hw.sh: REFUSED -- could not collect from $DEST after ${ELAPSED_TOTAL}s (--timeout=${TIMEOUT_S}s)." >&2
        echo "  get-file's own reboot never completed. Most likely explanation for a slow arm: the game is" >&2
        echo "  still running. Any running SDL3-DOS game replaces the BIOS keyboard IRQ handler (see the" >&2
        echo "  comment above this block), so a reboot chord genuinely cannot succeed while it is still" >&2
        echo "  alive, healthy or not -- this is NOT by itself evidence of a wedge. Re-run with a longer" >&2
        echo "  --timeout first; only suspect a genuine wedge (docs/lab/OPEN-FAULTS.md sec. 23) after" >&2
        echo "  ruling that out." >&2
        echo "$GET_RAW" >&2
        exit 1
    fi
    echo "   not ready yet (t+${ELAPSED_TOTAL}s of ${TIMEOUT_S}s budget) -- game likely still running, retrying collection in ${GET_RETRY_INTERVAL_S}s" >&2
    witness_hold "$GET_RETRY_INTERVAL_S"
done
for f in STDOUT.TXT AUTOPLT.LOG "$MANIFEST_LOG" "$SDLLOG" WARNINGS.LOG ${COLLECT_EXTRA[@]+"${COLLECT_EXTRA[@]}"} \
         AGSSAVE.001 PH01.BMP PH02.BMP PH03.BMP; do
    vc pulled save "$f" --out "$OUT_DIR/$f" 2>/dev/null || true
done
# The files are in hand and size-verified, so the game has exited and the
# recovery's verify-input is safe here. What is NOT yet known is whether the
# target came back from NET: on 2026-09-16 and 2026-09-17 it did not, this
# script said nothing, and the NEXT cell paid for it. Nothing collected can
# be stale at this point -- the per-file ok above is the proof of that --
# so a recovery here protects the next cell and marks this one as recovered.
guard_return_reboot collect "$GET_SEQ0"
# The RUNMANIFEST file is named <TAG>.LOG, not RUNMANI.LOG, when
# DOSAGS_LOG_TAG is set (patches/ags/0044) -- parse-results.py now
# scans for it (see that script's own comment), but stage it under
# its expected default name too so a plain `ls` of OUT_DIR isn't
# confusing about which file is which.
[[ -f "$OUT_DIR/$MANIFEST_LOG" ]] && cp "$OUT_DIR/$MANIFEST_LOG" "$OUT_DIR/RUNMANI.LOG"

# Build the reviewable sheet and say what was captured. A cell with fewer frames than the wait
# implies is marked SHORT in the manifest and here; it is never silently fine. The frames are
# for a person: nothing here judges them, and a rate from a run whose sheet shows trails is void.
if [[ -n "$WITNESS_DIR" ]]; then
    W_EXPECT=$(( WAIT_S / 12 ))   # from the WAIT LOOP (the collection reboots take no frames); 8 s cadence plus grab time
    (( W_EXPECT < 3 )) && W_EXPECT=3
    python3 "$HARNESS_DIR/witness_sheet.py" "$WITNESS_DIR/frames" --out "$WITNESS_DIR/sheet.png" \
        --manifest "$WITNESS_DIR/MANIFEST.json" --expect-min "$W_EXPECT" --card-log "$WITNESS_DIR/card-state.log" \
        || echo "run-hw.sh: WITNESS SHORT -- fewer physical-screen frames than the wait implies (expected >= $W_EXPECT); see $WITNESS_DIR/MANIFEST.json" >&2
    python3 "$HARNESS_DIR/witness_sheet.py" "$WITNESS_DIR/camera" --out "$WITNESS_DIR/sheet-camera.png" \
        --manifest "$WITNESS_DIR/MANIFEST-camera.json" --cols 4 --tile 400x300 --expect-min "$W_EXPECT" || true
    # A frozen or absent capture card is said HERE, in the cell's own output, not only in MANIFEST.json (round T,
    # 2026-09-27: the capture stick was gone for the whole round -- card state "unavailable", every sheet frame one stale
    # boot-text picture -- and nothing but the manifest said so). Reported, not a VOID: the camera sheet is then the only
    # witness, and the record must say that.
    python3 - "$WITNESS_DIR" <<'CAPPY' || true
import json, os, sys
w = sys.argv[1]
try:
    card = (json.load(open(os.path.join(w, "MANIFEST.json"))) or {}).get("card") or {}
except Exception:
    card = {}
if card.get("frozen"):
    with open(os.path.join(w, "WITNESS-CAPTURE-STALE.txt"), "w") as f:
        f.write(json.dumps(card) + "\n")
    kind = card.get("stale_kind") or "nolock"
    print("witness: capture=STALE(%s) -- %s (%s; state samples %s, %s unique of %s frames); the camera sheet is the only witness"
          % (kind, "the capture device was absent" if kind == "absent" else "the card gave no live picture",
             "; ".join(card.get("frozen_why") or []) or "frozen", json.dumps(card.get("state_samples")),
             card.get("unique_frames"), card.get("frames")))
CAPPY
    echo "witness: REVIEW $WITNESS_DIR/sheet.png (capture card) and sheet-camera.png (what the monitor showed) BEFORE quoting any rate from $TAG"
fi

echo "$OUT_DIR"
