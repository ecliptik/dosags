#!/usr/bin/env bash
# test-hw-guard.sh -- drive the reboot guard's branches WITHOUT the rig.
#
# VCCTRL_BIN is pointed at mock-vcctrl/vcctrl, so by construction not one
# real vcctrl command -- power, input or otherwise -- can be issued from
# here; the mock records what it WOULD have been asked, and the assertions
# read that record. What this does and does not prove is stated at the end
# of the run and in the commit that added it.
#
#   ./test-hw-guard.sh            all scenarios against run-probe-hw.sh
#   ./test-hw-guard.sh --with-run-hw   also one run-hw.sh scenario (its
#        wait_for_stable_screen has a 150 s floor, so it is opt-in)
set -uo pipefail
HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOCK="$HARNESS_DIR/mock-vcctrl/vcctrl"
WITH_RUN_HW=0
[[ "${1:-}" == "--with-run-hw" ]] && WITH_RUN_HW=1

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT
PROBE="$ROOT/DUMMY.EXE"; echo "not a real probe" > "$PROBE"
PASS=0; FAIL=0

count() { /usr/bin/grep -c -- "$1" "$2" 2>/dev/null || true; }

# run NAME SCENARIO EXPECT_EXIT -- then assertions via `expect`
run() {
    NAME="$1"; local scen="$2" want="$3"; shift 3
    ST="$ROOT/$NAME"; mkdir -p "$ST"
    OUT="$ST/out.txt"
    env MOCK_VC_STATE="$ST" MOCK_VC_SCENARIO="$scen" VCCTRL_BIN="$MOCK" \
        HW_HOLD_FILE="${HOLD_FILE_OVERRIDE:-$ST/no-hold.json}" HW_GUARD_WITNESS_S=4 \
        HW_GUARD_PERSISTENT_LOG="$ST/recoveries.log" "$@" \
        "$HARNESS_DIR/run-probe-hw.sh" "$PROBE" --wait 1 --dest 'C:\DOSAGS' > "$OUT" 2>&1
    GOT=$?
    CALLS="$ST/calls.log"; [[ -f "$CALLS" ]] || : > "$CALLS"
    if [[ "$GOT" == "$want" ]]; then ok "exit code $GOT"; else bad "exit code $GOT, wanted $want"; fi
}
ok()  { PASS=$((PASS+1)); echo "  ok   [$NAME] $1"; }
bad() { FAIL=$((FAIL+1)); echo "  FAIL [$NAME] $1"; sed 's/^/        | /' "$OUT" | tail -25; }
expect() {  # expect DESCRIPTION ACTUAL WANTED
    if [[ "$2" == "$3" ]]; then ok "$1 = $2"; else bad "$1 = $2, wanted $3"; fi
}
rec_field() { /usr/bin/grep -o "$1=[^ ]*" "$OUT" | tail -1 | cut -d= -f2; }

echo "== A. healthy rig: both witnesses pass, the recovery is never reached =="
run A "" 0
expect "power cycles"      "$(count '^power cycle' "$CALLS")" 0
expect "verify-input calls" "$(count '^verify-input' "$CALLS")" 0
expect "HW-RECOVERY lines" "$(count 'HW-RECOVERY' "$OUT")" 0

echo "== B. the 2026-09-17 fault: collect's return reboot never takes, link dead =="
run B "hang_return:collect" 0
expect "power cycles"       "$(count '^power cycle' "$CALLS")" 1
expect "verify-input calls" "$(count '^verify-input' "$CALLS")" 2
expect "outcome"            "$(rec_field outcome)" RECOVERED
expect "step"               "$(rec_field step)" collect
expect "screen seen"        "$(/usr/bin/grep -c 'ftp-log' "$OUT" | sed 's/^[1-9].*/seen/')" seen
expect "probe output kept"  "$(/usr/bin/grep -c 'PRBOUT.TXT$' "$OUT" | sed 's/^[1-9].*/yes/')" yes

echo "== C. same fault at SEND (before the probe is typed) =="
run C "hang_return:send" 0
expect "power cycles" "$(count '^power cycle' "$CALLS")" 1
expect "step"         "$(rec_field step)" send
expect "PRUN.BAT still typed after the recovery" "$(count '^type PRUN.BAT' "$CALLS")" 1

echo "== D. link already dead when the run starts (today's SECOND symptom: the next cell's send hung) =="
run D "dead_before_send" 0
expect "power cycles"   "$(count '^power cycle' "$CALLS")" 1
expect "send-file jobs" "$(count '^send-file' "$CALLS")" 2
expect "outcome"        "$(rec_field outcome)" RECOVERED

echo "== E. a SECOND failure in one run stops it -- never a second power action =="
run E "hang_return:send,hang_return:collect" 3
expect "power cycles" "$(count '^power cycle' "$CALLS")" 1
expect "outcome"      "$(rec_field outcome)" STOPPED-second-failure

echo "== F. the power cycle does not bring the link back: stop, do not loop =="
run F "hang_return:collect,power_cycle_fails" 3
expect "power cycles" "$(count '^power cycle' "$CALLS")" 1
expect "outcome"      "$(rec_field outcome)" FAILED

echo "== G. link alive but the machine never rebooted: a chord, not a power cycle =="
run G "alive_no_reboot:collect" 0
expect "power cycles"  "$(count '^power cycle' "$CALLS")" 0
expect "reboot chords" "$(count '^combo ctrl alt delete' "$CALLS")" 1
expect "action"        "$(rec_field action)" reboot-chord

echo "== H. maintenance window: the script refuses before ANY command reaches the target =="
HOLD_FILE_OVERRIDE="$ROOT/hold.json"
python3 - "$HOLD_FILE_OVERRIDE" <<'PY'
import json, sys, datetime
until = (datetime.datetime.now().astimezone() + datetime.timedelta(hours=1)).isoformat()
json.dump({"until": until, "reason": "test window"}, open(sys.argv[1], "w"))
PY
run H "hang_return:collect" 4
# (led-changes is the one thing allowed through: a passive read the mock's
# vcctrl_common shim makes at import. Nothing else may appear.)
expect "power/input/transfer commands sent to the (mock) target" "$(/usr/bin/grep -vc '^led-changes' "$CALLS")" 0
echo "== I. ...and a recovery that finds a hold in force refuses to touch power or input =="
NAME=I; ST="$ROOT/I"; mkdir -p "$ST"; OUT="$ST/out.txt"; CALLS="$ST/calls.log"; : > "$CALLS"
env MOCK_VC_STATE="$ST" VCCTRL_BIN="$MOCK" HW_HOLD_FILE="$HOLD_FILE_OVERRIDE" HW_GUARD_PERSISTENT_LOG="$ST/recoveries.log" \
    python3 "$HARNESS_DIR/hw_guard.py" recover --tag TESTI --step collect --seen "test" --record "$ST/RECOVERY.TXT" --state "$ST/state" > "$OUT" 2>&1
expect "exit code" "$?" 4
expect "power cycles"       "$(count '^power cycle' "$CALLS")" 0
expect "verify-input calls" "$(count '^verify-input' "$CALLS")" 0
expect "outcome"            "$(rec_field outcome)" STOPPED-maintenance-window
unset HOLD_FILE_OVERRIDE

echo "== K. a REFUSED collection (a game may still be running): nothing is sent in response =="
run K "game_running:9" 1
expect "power cycles"       "$(count '^power cycle' "$CALLS")" 0
expect "verify-input calls" "$(count '^verify-input' "$CALLS")" 0
expect "reboot chords"      "$(count '^combo' "$CALLS")" 0

if [[ $WITH_RUN_HW -eq 1 ]]; then
    echo "== J. run-hw.sh itself, one refused collection, then fault B (needs ~4 min: wait_for_stable_screen's floor + one 60 s retry) =="
    NAME=J; ST="$ROOT/J"; mkdir -p "$ST"; OUT="$ST/out.txt"; CALLS="$ST/calls.log"
    env MOCK_VC_STATE="$ST" MOCK_VC_SCENARIO="game_running:1,hang_return:collect" VCCTRL_BIN="$MOCK" \
        HW_HOLD_FILE="$ST/no-hold.json" HW_GUARD_WITNESS_S=4 HW_GUARD_PERSISTENT_LOG="$ST/recoveries.log" \
        "$HARNESS_DIR/run-hw.sh" trilbysnotes --tag MOCKJ1 --timeout 400 > "$OUT" 2>&1
    expect "exit code"    "$?" 0
    # The first collection attempt is refused (game "still running"): the
    # script must only retry. verify-input may appear ONLY after the second,
    # successful get-file.
    expect "get-file attempts" "$(count '^get-file' "$CALLS")" 2
    expect "first verify-input comes after the successful get-file" \
        "$(awk '/^get-file/{g++} /^verify-input/{print (g>=2)?"yes":"NO"; exit}' "$CALLS")" yes
    expect "power cycles" "$(count '^power cycle' "$CALLS")" 1
    expect "outcome"      "$(rec_field outcome)" RECOVERED
    D="$(tail -1 "$OUT")"
    expect "RECOVERY.TXT in the collected dir" "$([[ -f "$D/RECOVERY.TXT" ]] && echo yes || echo no)" yes

    # L and M: the 2026-09-21 C1A2 fault. Timing knobs shortened by env (defaults unchanged in run-hw.sh).
    FAST=(RUNHW_MIN_WAIT_S=3 RUNHW_STILL_S=3 RUNHW_POLL_S=2 RUNHW_GET_RETRY_S=1 RUNHW_AUTO_RECOVER_AFTER=3)
    echo "== L. game EXITED (screen = a DOS prompt), link dead, get-file refused: after 3 refusals ONE guarded recovery, then collected =="
    NAME=L; ST="$ROOT/L"; mkdir -p "$ST"; OUT="$ST/out.txt"; CALLS="$ST/calls.log"
    env MOCK_VC_STATE="$ST" MOCK_VC_SCENARIO="exited_dead_link" VCCTRL_BIN="$MOCK" "${FAST[@]}" \
        HW_HOLD_FILE="$ST/no-hold.json" HW_GUARD_WITNESS_S=4 HW_GUARD_PERSISTENT_LOG="$ST/recoveries.log" \
        "$HARNESS_DIR/run-hw.sh" trilbysnotes --tag MOCKL1 --timeout 300 > "$OUT" 2>&1
    expect "exit code"    "$?" 0
    expect "power cycles" "$(count '^power cycle' "$CALLS")" 1
    expect "get-file attempts (3 refused + 1 taken)" "$(count '^get-file' "$CALLS")" 4
    expect "outcome"      "$(rec_field outcome)" RECOVERED
    expect "it said why"  "$(/usr/bin/grep -c "screen reads 'dos-prompt'\|the screen reads 'dos-prompt'" "$OUT" | sed 's/^[1-9].*/yes/')" yes

    echo "== M. game STILL RUNNING (a picture on screen), get-file refused every time: NOTHING is sent in response =="
    NAME=M; ST="$ROOT/M"; mkdir -p "$ST"; OUT="$ST/out.txt"; CALLS="$ST/calls.log"
    env MOCK_VC_STATE="$ST" MOCK_VC_SCENARIO="game_running:99" VCCTRL_BIN="$MOCK" "${FAST[@]}" \
        HW_HOLD_FILE="$ST/no-hold.json" HW_GUARD_WITNESS_S=4 HW_GUARD_PERSISTENT_LOG="$ST/recoveries.log" \
        "$HARNESS_DIR/run-hw.sh" trilbysnotes --tag MOCKM1 --timeout 30 > "$OUT" 2>&1
    expect "exit code (REFUSED at the timeout)" "$?" 1
    expect "power cycles"       "$(count '^power cycle' "$CALLS")" 0
    expect "verify-input calls" "$(count '^verify-input' "$CALLS")" 0
    expect "reboot chords"      "$(count '^combo' "$CALLS")" 0
    expect "it declined, and said so" "$(/usr/bin/grep -c 'NOT recovering' "$OUT" | sed 's/^[1-9].*/yes/')" yes
fi

echo
echo "passed=$PASS failed=$FAIL"
[[ $FAIL -eq 0 ]]
