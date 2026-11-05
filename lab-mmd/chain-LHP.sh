#!/usr/bin/env bash
# lab-mmd: L's gates, then H''s, then the profiler cells -- sequentially (no pgrep waiters: those
# matched their own command lines and never fired, 2026-09-24).
cd "$(dirname "$0")/.."
export DOSBOX_LOCK_WAIT=21600 MMD_DATE=2026-09-24
FAST=$PWD/tools/dosbox-x-fast.conf
lab-mmd/run-cells.sh lab-mmd/gL.spec > lab-mmd/gL.log 2>&1
MMD_CONF=$FAST MMD_LOCK=exclusive DOSBOX_DISPLAY_NUM=261 lab-mmd/run-cells.sh lab-mmd/gLscreen.spec >> lab-mmd/gL.log 2>&1
echo done >> lab-mmd/gL.log
lab-mmd/run-cells.sh lab-mmd/gH.spec > lab-mmd/gH.log 2>&1
MMD_CONF=$FAST MMD_LOCK=exclusive DOSBOX_DISPLAY_NUM=261 lab-mmd/run-cells.sh lab-mmd/gHscreen.spec >> lab-mmd/gH.log 2>&1
echo done >> lab-mmd/gH.log
lab-mmd/run-cells.sh lab-mmd/prof.spec > lab-mmd/prof.log 2>&1
echo done >> lab-mmd/prof.log
