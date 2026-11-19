#!/usr/bin/env bash
# waitfor.sh -- the one way to wait on background work in this repo (agents and humans).
#
# Every wait MUST end: on success, when the process doing the work dies, or at a hard timeout.
#
#   tools/waitfor.sh --timeout SECS [--pid PID | --pidfile F] [--file F --grep PATTERN] [--interval N]
#
#   --timeout SECS   required, 1..3600. Exit 124 when it passes.
#   --pid PID        the process doing the work. Exit 3 as soon as it is gone (checked with kill -0,
#   --pidfile F        never with `pgrep -f`, which matches the waiting shell's own command line and
#                      so never reports the work as finished).
#   --file F --grep PATTERN   success (exit 0) once F contains PATTERN (grep -E).
#   With only --pid/--pidfile: success (exit 0) when that process exits.
#
# Start the work so it records its own PID, then wait on it, e.g.
#   build/land/series2.sh > results/series2.log 2>&1 & echo $! > results/series2.pid
#   tools/waitfor.sh --timeout 1800 --pidfile results/series2.pid --file results/series2.log --grep 'rc='
#
# Run ONE waiter per job. If a waiter times out, check the job (is its PID alive? what does its log say?)
# before starting another: never stack a new copy of the same wait on a job that may be dead.
set -u
timeout= pid= pidfile= file= pat= interval=5
while [ $# -gt 0 ]; do
  case "$1" in
    --timeout) timeout=$2; shift 2;;
    --pid) pid=$2; shift 2;;
    --pidfile) pidfile=$2; shift 2;;
    --file) file=$2; shift 2;;
    --grep) pat=$2; shift 2;;
    --interval) interval=$2; shift 2;;
    *) echo "waitfor: unknown argument $1" >&2; exit 2;;
  esac
done
case "$timeout" in ''|*[!0-9]*) echo "waitfor: --timeout SECS is required" >&2; exit 2;; esac
[ "$timeout" -ge 1 ] && [ "$timeout" -le 3600 ] || { echo "waitfor: --timeout must be 1..3600" >&2; exit 2; }
if [ -n "$file" ] && [ -z "$pat" ] || [ -z "$file" ] && [ -n "$pat" ]; then
  echo "waitfor: --file and --grep go together" >&2; exit 2
fi
if [ -n "$pidfile" ]; then
  [ -s "$pidfile" ] || { echo "waitfor: pidfile $pidfile missing or empty" >&2; exit 2; }
  pid=$(tr -dc '0-9' < "$pidfile")
fi
[ -n "$pid" ] || [ -n "$file" ] || { echo "waitfor: give --pid/--pidfile and/or --file --grep" >&2; exit 2; }

found() { [ -n "$file" ] && [ -f "$file" ] && grep -qE -- "$pat" "$file"; }
alive() { kill -0 "$pid" 2>/dev/null; }

end=$(( $(date +%s) + timeout ))
while :; do
  if [ -n "$file" ]; then
    found && { echo "waitfor: found /$pat/ in $file"; exit 0; }
    if [ -n "$pid" ] && ! alive; then
      sleep 1; found && { echo "waitfor: found /$pat/ in $file"; exit 0; }
      echo "waitfor: process $pid exited without writing /$pat/ to $file" >&2
      [ -f "$file" ] && tail -n 5 "$file" >&2
      exit 3
    fi
  elif ! alive; then
    echo "waitfor: process $pid exited"; exit 0
  fi
  [ "$(date +%s)" -ge "$end" ] && { echo "waitfor: timed out after ${timeout}s" >&2; exit 124; }
  sleep "$interval"
done
