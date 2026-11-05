#!/usr/bin/env bash
# run-probe-hw.sh -- run ONE bare DJGPP probe executable on the real
# vcctrl rig and bring its stdout back. The standalone-probe counterpart
# of run-hw.sh, which is shaped around AGS.EXE (game package, CLI args,
# RUNMANIFEST collection) and cannot run an arbitrary exe.
#
# Exists because the first synthetic probe this project ran on the rig
# (overhead-probe/ovhtest.cpp, 2026-09-16) was staged and driven by hand,
# and that hand-driving hit a real trap: vcctrl's get-file/send-file each
# REBOOT the target, which resets the DOS current directory to C:\, so
# commands typed afterwards ran in the wrong directory and the first
# "result" fetched was 19 bytes of batch-file echo. Everything here goes
# through a staged RUN.BAT that does its own CD, the same way run-hw.sh
# does, so there is no typed-command state to lose.
#
# Same vcctrl primitives and the same verified-send / verified-get
# discipline as run-hw.sh (stage-file --replace, send-file --return,
# poll file-status until running=false, check ok, get-file --return).
#
# Usage:
#   ./run-probe-hw.sh <probe.exe> [--dest DOS-DIR] [--wait SECONDS]
#
#   --wait SECONDS   how long the probe is expected to run before its
#                    output is collected (default 120). A probe is text
#                    mode and short; there is no screen-settle heuristic
#                    here on purpose -- say how long it takes.
#
# Prints the collected STDOUT.TXT's path as its last line of stdout.

set -euo pipefail

usage() { echo "Usage: $0 <probe.exe> [--dest DIR] [--wait SECONDS] [--env KEY=VALUE]..." >&2; exit 1; }
[[ $# -ge 1 ]] || usage
PROBE="$1"; shift
DEST=""
WAIT_S=120
EXTRA_ENV=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dest) DEST="$2"; shift 2 ;;
        --wait) WAIT_S="$2"; shift 2 ;;
        --env) EXTRA_ENV+=("$2"); shift 2 ;;
        *) usage ;;
    esac
done
[[ -f "$PROBE" ]] || { echo "run-probe-hw.sh: $PROBE not found" >&2; exit 1; }

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HARNESS_DIR/../.." && pwd)"
CWSDPMI_EXE="$REPO_ROOT/vendor/cwsdpmi/cwsdpmi.exe"
PROFILE="$REPO_ROOT/profiles/dosags.yaml"
VCCTRL_BIN="${VCCTRL_BIN:-$REPO_ROOT/../vcctrl/bin/vcctrl}"
[[ -x "$VCCTRL_BIN" ]] || { echo "run-probe-hw.sh: $VCCTRL_BIN not found -- set VCCTRL_BIN" >&2; exit 1; }
[[ -f "$CWSDPMI_EXE" ]] || { echo "run-probe-hw.sh: $CWSDPMI_EXE not found" >&2; exit 1; }

if [[ -z "$DEST" ]]; then
    DEST="$(python3 -c "
import yaml
with open('$PROFILE') as f:
    print(yaml.safe_load(f)['target']['dir'])
")"
fi

vc() { "$VCCTRL_BIN" "$@"; }

wait_for_job_done() {
    local max_wait_s="${1:-1800}" elapsed=0 running raw
    while (( elapsed < max_wait_s )); do
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
    echo "wait_for_job_done: gave up after ${max_wait_s}s" >&2
    return 1
}

# Aggregate job.ok -- right for SEND, where every staged file is needed.
job_ok() {
    vc file-status 100 2>/dev/null | python3 -c 'import json,sys
try:
    print(json.load(sys.stdin)["job"]["ok"])
except Exception:
    print("UNKNOWN")' 2>/dev/null || echo "UNKNOWN"
}

# Per-file ok, by name -- right for COLLECT. Same shape as vcctrl's own
# harness/vcctrl-collect (f["ok"] per name) and as run-hw.sh since
# 8999f5f, which was burned by the aggregate: job.ok is false whenever ANY
# name in the job failed, including ones the caller never needed. This
# script asks for one file today, so the two agree -- but the check should
# say what it means rather than be right by coincidence.
file_ok() {
    vc file-status 100 2>/dev/null | NAME="$1" python3 -c 'import json,os,sys
try:
    files = json.load(sys.stdin)["job"]["files"]
    print({f["name"]: f.get("ok") for f in files}.get(os.environ["NAME"]) is True)
except Exception:
    print("UNKNOWN")' 2>/dev/null || echo "UNKNOWN"
}

# Operator maintenance window (hw_guard.py hold-set): checked BEFORE the
# first command that could touch the target -- including the power-state
# read just below, whose --power-on branch is a power action. A machine
# somebody switched off on purpose stays off.
VCCTRL_BIN="$VCCTRL_BIN" python3 "$HARNESS_DIR/hw_guard.py" hold-check >/dev/null \
    || { echo "run-probe-hw.sh: REFUSED -- maintenance window in force (see above); nothing was sent to the target." >&2; exit 4; }

if [[ "$(vc power state | python3 -c 'import json,sys; print(json.load(sys.stdin)["power"]["on"])')" == "False" ]]; then
    echo "run-probe-hw.sh: REFUSED -- rig is off." >&2
    exit 2
fi

EXE_NAME="$(basename "$PROBE" | tr '[:lower:]' '[:upper:]')"
LOCK_AS="run-probe-$$"
WORK="$(mktemp -d)"
OUT_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK"; vc lock release --as "$LOCK_AS" >/dev/null 2>&1 || true' EXIT

# PRBOUT.TXT, not STDOUT.TXT: $DEST is shared with every game cell ever
# staged there, and a stale STDOUT.TXT from one of those must never be
# mistaken for this probe's output. DEL first for the same reason --
# this project has been burned by an append/stale target file before.
# --env KEY=VALUE: SET lines ahead of the probe, same shape as run-hw.sh's
# RUN.BAT -- added 2026-09-17 to reproduce an engine cell's exact
# environment around a probe (the bogus-date / slow-gettimeofday hunt).
EXTRA_ENV_LINES=""
for kv in "${EXTRA_ENV[@]:-}"; do
    [[ -n "$kv" ]] && EXTRA_ENV_LINES+="SET ${kv}"$'\n'
done
cat > "$WORK/PRUN.BAT" <<BATEOF
@ECHO OFF
CD $DEST
IF EXIST PRBOUT.TXT DEL PRBOUT.TXT
${EXTRA_ENV_LINES}$EXE_NAME > PRBOUT.TXT
IF EXIST C:\\VGACAP\\MODE12.COM C:\\VGACAP\\MODE12.COM
BATEOF
sed -i 's/$/\r/' "$WORK/PRUN.BAT"

# ---- reboot guard (2026-09-17) -- same mechanism and same rule as
# run-hw.sh; hw_guard.py's header is the explanation. A probe is not an
# SDL3-DOS program, but the rule is kept identical anyway: the recovery
# (which runs verify-input) is only reached after SEND, before the probe is
# typed, and after a collection that has already succeeded.
GUARD="$HARNESS_DIR/hw_guard.py"
GUARD_STATE="$WORK/guard.state"
RECOVERY_REC="$OUT_DIR/RECOVERY.TXT"
GUARD_TAG="PROBE-$(basename "$PROBE" | tr '[:lower:]' '[:upper:]' | cut -d. -f1)"
guard() { VCCTRL_BIN="$VCCTRL_BIN" python3 "$GUARD" "$@"; }
guard_return_reboot() {
    local step="$1" seq0="$2" wjson
    echo "-- reboot witness ($step): 2 completed boots since LED seq $seq0 --"
    if wjson="$(guard witness --since-seq "$seq0" --need 2 --step "$step" --shot "$OUT_DIR/WITNESS-$step.jpg")"; then
        echo "   witnessed: $wjson"
        return 0
    fi
    echo "   NO WITNESS: $wjson" >&2
    guard recover --tag "$GUARD_TAG" --step "$step" --seen "$wjson" --record "$RECOVERY_REC" --state "$GUARD_STATE" \
        || { echo "run-probe-hw.sh: STOPPED at step '$step' -- the return reboot never took and the rig could not be recovered automatically (or this run had already used its one recovery). See $RECOVERY_REC." >&2; exit 3; }
    echo "   recovered -- resuming after '$step'"
}

echo "== run-probe-hw.sh: $EXE_NAME dest=$DEST wait=${WAIT_S}s =="
# Called from an `if !` (set -e suspended inside), hence the `|| return`s.
stage_and_send() {
    echo "-- staging --"
    vc stage-file "$PROBE" "$EXE_NAME" --replace || return 2
    vc stage-file "$CWSDPMI_EXE" CWSDPMI.EXE --replace || return 2
    vc stage-file "$WORK/PRUN.BAT" PRUN.BAT --replace || return 2
    echo "-- sending to $DEST (reboot x2) --"
    SEND_SEQ0="$(guard seq)"
    vc send-file --return --dest "$DEST"
    wait_for_job_done
    [[ "$(job_ok)" == "True" ]]
}
if ! stage_and_send; then
    echo "run-probe-hw.sh: send-file did not verify cleanly -- attempting the one automatic recovery, then re-sending" >&2
    vc file-status 100 >&2 || true
    vc file-cancel >/dev/null 2>&1 || true
    guard recover --tag "$GUARD_TAG" --step send --seen "send-file job did not verify" --record "$RECOVERY_REC" --state "$GUARD_STATE" \
        || { echo "run-probe-hw.sh: REFUSED -- send-file did not verify cleanly and the rig could not be recovered. See $RECOVERY_REC." >&2; exit 3; }
    stage_and_send || { echo "run-probe-hw.sh: REFUSED -- send-file did not verify cleanly even after a recovery" >&2; vc file-status 100 >&2 || true; exit 1; }
fi
echo "   all files verified byte-for-byte"
guard_return_reboot send "$SEND_SEQ0"

echo "-- launching PRUN.BAT --"
vc lock acquire --as "$LOCK_AS"
vc type "CD $DEST" --as "$LOCK_AS"
vc key enter --as "$LOCK_AS"
sleep 1
vc type "PRUN.BAT" --as "$LOCK_AS"
vc key enter --as "$LOCK_AS"
vc lock release --as "$LOCK_AS" || true

echo "-- waiting ${WAIT_S}s for the probe to finish --"
sleep "$WAIT_S"

echo "-- collecting PRBOUT.TXT --"
GET_SEQ0="$(guard seq)"
vc get-file PRBOUT.TXT --return --from "$DEST"
wait_for_job_done
[[ "$(file_ok PRBOUT.TXT)" == "True" ]] || { echo "run-probe-hw.sh: REFUSED -- get-file did not verify cleanly" >&2; vc file-status 100 >&2 || true; exit 1; }
vc pulled save PRBOUT.TXT --out "$OUT_DIR/PRBOUT.TXT"
# File in hand and verified; now make sure the target actually came back
# from NET, so the NEXT run does not inherit a hung rig.
guard_return_reboot collect "$GET_SEQ0"
[[ -f "$RECOVERY_REC" ]] && { echo "   NOTE: this probe run needed a rig recovery:"; cat "$RECOVERY_REC"; }
echo "$OUT_DIR/PRBOUT.TXT"
