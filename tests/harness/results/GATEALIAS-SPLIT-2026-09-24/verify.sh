#!/usr/bin/env bash
# Verify gate-alias.sh's per-run lock split (2026-09-24): one row (bench8-alias-idle) + its control.
#   (a) default conf       -> each run takes its own EXCLUSIVE lock (freeze capture at cycles=max)
#   (b) GATE_CONF fixed40k -> each run takes SHARED (fixed cycles + --no-host-input)
#   (c) ratchet-style      -> an outer EXCLUSIVE hold (DOSBOX_LOCK_HELD=1): the runs take nothing
# A watcher samples the lock's .who file every second; verdicts must match G3a's bench8-alias-idle row.
set -u
H=/home/claude/git/dosags-lab-metric/tests/harness; R=$H/results/GATEALIAS-SPLIT-2026-09-24
export AGS_EXE=/home/claude/git/dosags-lab-metric/build/lab/C3v1/ags.exe DOSBOX_DISPLAY_NUM=221
SUB=(--arms idle --no-aq --no-pillarbox --no-bench16 --no-catalogue)
watch() { while :; do date -u +%T | tr '\n' ' '; /usr/bin/grep -E 'gate-alias|run-dosbox|lab-gatesplit' /tmp/dos-port-dosbox.lock.who | /usr/bin/grep -v 'waiting' | tr '\n' '|'; echo; sleep 1; done > "$1"; }
cd $H
watch $R/a.who & w=$!; ./gate-alias.sh --out $R/a "${SUB[@]}" > $R/a.log 2>&1; echo "a rc=$?" >> $R/rc.txt; kill $w
watch $R/b.who & w=$!; GATE_CONF=$H/../../tools/dosbox-x.conf ./gate-alias.sh --out $R/b "${SUB[@]}" > $R/b.log 2>&1; echo "b rc=$?" >> $R/rc.txt; kill $w
source /home/claude/git/sdl-dos-ports/shared/tools/dosbox-lock-lib.sh
watch $R/c.who & w=$!
( dbxlock_acquire exclusive 21600 "tool=lab-gatesplit-outer" || exit 75; export DOSBOX_LOCK_HELD=1 DOSBOX_LOCK_HELD_MODE=exclusive
  trap dbxlock_release EXIT; ./gate-alias.sh --out $R/c "${SUB[@]}" > $R/c.log 2>&1; echo "c rc=$?" >> $R/rc.txt )
kill $w
